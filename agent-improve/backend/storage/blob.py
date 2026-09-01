"""Case records on Azure Blob — §10's second concern, as module-level functions.

Canonical definition: reference **§58.8 — S-C08**. Architecture: §10 (Azure Blob
— two distinct concerns). Procedure step 3.5.

Owner of the **system of record**: the case document, the registry, and uploaded
files. Writes on case create, on gate pass and on file upload, and **never
mid-conversation** — conversation history lives in the checkpoint until a gate
passes (§10, S-C08 B1/B2).

Paths owned, and no others:

    cases/case_{case_id}.json
    registry.json
    uploads/{case_id}/{filename}

CONCERN SEPARATION (§10) — THIS IS NOT `core/store.py`
------------------------------------------------------
§10 ratifies three Blob concerns with three owners, and they are not merged:

  * **checkpoints** — in-flight graph state, `checkpoints/{case_id}/...`,
    owned by `core/checkpointer.py` (S-C07).
  * **cross-phase artifacts** — `store/...`, owned by `AzureBlobStore` in
    `core/store.py` (S-C06), which is a LangGraph `BaseStore`.
  * **case records** — the three prefixes above. This file.

This module does not import, wrap or subclass `AzureBlobStore`, and must not
start doing so: `cases/case_{id}.json` is authoritative, and the Store's `case`
namespace is a session-start COPY so mappers can depend on `BaseStore` alone
(§9). Two writers on one authority is the thing §10 spends a section preventing.

NO CLASS LIVES HERE
-------------------
§54 and CLAUDE.md §2 both name `storage/blob.py` among the files that hold
**module-level functions ONLY**, with no exception. The former
`ImproveBlobClient` was a class where none is permitted; procedure step 3.5
removed it. Do not reintroduce one — the state it would have held is exactly
the cached client below, which is module state and needs no object around it.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, timezone
from typing import Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import (
    BlobServiceClient as AsyncBlobServiceClient,
    ContainerClient as AsyncContainerClient,
)

from backend.core.config import settings
from backend.storage.models import (
    CaseDocument,
    CaseRegistry,
    PhaseRecord,
    RegistryEntry,
)

logger = logging.getLogger(__name__)

REGISTRY_BLOB_PATH = "registry.json"


# ── the aio session lifecycle ─────────────────────────────────────────────
#
# CACHED, and deliberately so — the opposite of `AzureBlobStore`'s choice, on
# a measurement rather than a preference.
#
# An `azure.storage.blob.aio` client owns an aiohttp session, and that session
# owns a TLS connection pool. `core/store.py` opens and closes one per
# operation because Store writes happen a handful of times per phase, so the
# reconnect cost is paid rarely and buys a lifecycle with nothing to clean up.
#
# That reasoning does not transfer here. `load_case` and `save_case` are on the
# `/ask` path — every request pays both. Measured against the real container
# (`agent-improve-cases`, case IMPR-2026-E9D, 74,693 bytes, n=25, 2026-09-01):
#
#     shape                    load (median)   save (median)
#     per-operation client         289.2 ms        360.3 ms
#     cached client                 96.6 ms         82.5 ms
#
# — a 470 ms penalty per `/ask` request, roughly 3-4x. Note where it comes
# from: constructing the client and tearing down its session, with no blob I/O
# at all, costs 0.5 ms. The 470 ms is the TLS handshake and connection setup
# that a fresh pool cannot reuse. The per-operation shape was never really
# paying for object construction, which is why the cost had to be measured
# rather than assumed.
#
# The lifecycle cost of caching is one `await aclose()` at shutdown, wired to
# `backend/app.py`'s EXISTING `@app.on_event("shutdown")`. That hook is already
# there and is not gated: procedure step 8.5 is about *draining in-flight
# coaching turns* via `RunControl.request_drain()`, which is a different
# concern from closing an HTTP session. Nothing here depends on 8.5.
#
# The client is cached against the loop it was built on. A session is bound to
# its event loop, and a client carried across loops would fail at the first
# await on a closed transport — which is what a test suite running several
# `asyncio.run()` calls in one process would do.
_client: Optional[AsyncBlobServiceClient] = None
_client_loop: Optional[asyncio.AbstractEventLoop] = None


def storage_configured() -> bool:
    """Whether Blob credentials are present.

    Replaces the former import-time singleton, which constructed a client under
    a bare `except` and left `blob_client = None` when it failed — so an
    unrelated construction error read to every caller as "not configured".
    """
    return bool(
        settings.AZURE_BLOB_CONNECTION_STRING
        and settings.AZURE_BLOB_CONTAINER_IMPROVE
    )


def _container() -> AsyncContainerClient:
    """The container client for this loop, building and caching one if needed."""
    global _client, _client_loop

    if not storage_configured():
        raise RuntimeError(
            "Blob storage requires AZURE_BLOB_CONNECTION_STRING and "
            "AZURE_BLOB_CONTAINER_IMPROVE in settings."
        )

    loop = asyncio.get_running_loop()
    if _client is None or _client_loop is not loop:
        _client = AsyncBlobServiceClient.from_connection_string(
            settings.AZURE_BLOB_CONNECTION_STRING
        )
        _client_loop = loop
        logger.info(
            "Blob case-record client opened on container=%s",
            settings.AZURE_BLOB_CONTAINER_IMPROVE,
        )
    return _client.get_container_client(settings.AZURE_BLOB_CONTAINER_IMPROVE)


async def aclose() -> None:
    """Close the cached client and its session. Idempotent.

    Called from `backend/app.py`'s shutdown hook. Without it the aiohttp
    session is garbage-collected rather than closed, which is the unclosed-
    session warning the per-operation shape exists to avoid.
    """
    global _client, _client_loop
    if _client is None:
        return
    client, _client, _client_loop = _client, None, None
    await client.close()
    logger.info("Blob case-record client closed")


# ── low-level helpers ─────────────────────────────────────────────────────

async def _upload(path: str, data: str | bytes, overwrite: bool = True) -> None:
    await _container().upload_blob(path, data, overwrite=overwrite)


async def _download(path: str) -> str:
    blob = _container().get_blob_client(path)
    downloader = await blob.download_blob()
    raw = await downloader.readall()
    return raw.decode("utf-8")


async def _exists(path: str) -> bool:
    try:
        await _container().get_blob_client(path).get_blob_properties()
        return True
    except ResourceNotFoundError:
        return False


# ── case CRUD ─────────────────────────────────────────────────────────────

def case_path(case_id: str) -> str:
    """Pure path construction — no I/O, so it stays synchronous."""
    return f"cases/case_{case_id}.json"


async def load_case(case_id: str) -> Optional[CaseDocument]:
    """Load case from blob. Returns None if not found."""
    try:
        raw = await _download(case_path(case_id))
        return CaseDocument.model_validate_json(raw)
    except ResourceNotFoundError:
        return None
    except Exception as e:
        logger.error("load_case %s failed: %s", case_id, e)
        return None


async def save_case(case: CaseDocument) -> None:
    """Save full case document to blob."""
    await _upload(
        case_path(case.case_id),
        case.model_dump_json(indent=2),
    )


async def create_case(case: CaseDocument) -> None:
    """Create new case — raises if already exists."""
    path = case_path(case.case_id)
    if await _exists(path):
        raise ValueError(f"Case {case.case_id} already exists")
    await _upload(path, case.model_dump_json(indent=2), overwrite=False)


# ── phase gate operations ─────────────────────────────────────────────────

async def write_phase_gate(
    case_id: str,
    phase: str,
    structured: dict,
    submitted_by: str,
    summary: str,
    citations: list[dict] = [],
    uploads: list[dict] = [],
    analyst_output: Optional[dict] = None,
) -> None:
    """Write a validated phase record to blob and update registry.
    Called only after Pydantic gate passes."""
    case = await load_case(case_id)
    if case is None:
        raise ValueError(f"Case {case_id} not found")

    now = datetime.now(timezone.utc).isoformat()

    # Update phase record
    case.phases[phase] = PhaseRecord(
        gate_passed=True,
        submitted_by=submitted_by,
        submitted_at=now,
        structured=structured,
        citations=[c for c in citations],
        uploads=[u for u in uploads],
    )

    # Advance current phase
    phase_order = ["define", "measure", "analyse", "improve", "control"]
    current_idx = phase_order.index(phase)
    if current_idx < len(phase_order) - 1:
        case.current_phase = phase_order[current_idx + 1]
    else:
        case.current_phase = "complete"
        case.status = "complete"

    # B2: two separate writes, the case then the registry.
    await save_case(case)
    await _update_registry_entry(case, phase, summary, now)
    logger.info(
        "Phase gate written: %s / %s by %s", case_id, phase, submitted_by
    )


# ── conversation history ──────────────────────────────────────────────────

async def append_turn(case_id: str, turn: dict) -> None:
    """Append one conversation turn to case history."""
    case = await load_case(case_id)
    if case is None:
        raise ValueError(f"Case {case_id} not found")
    case.conversation_history.append(turn)
    await save_case(case)


# ── registry operations ───────────────────────────────────────────────────

async def load_registry() -> CaseRegistry:
    """Load registry. Returns empty registry if not found."""
    try:
        raw = await _download(REGISTRY_BLOB_PATH)
        return CaseRegistry.model_validate_json(raw)
    except ResourceNotFoundError:
        return CaseRegistry()


async def save_registry(registry: CaseRegistry) -> None:
    registry.last_updated = datetime.now(timezone.utc).isoformat()
    await _upload(REGISTRY_BLOB_PATH, registry.model_dump_json(indent=2))


async def register_case(case: CaseDocument) -> None:
    """Add new case to registry."""
    registry = await load_registry()
    entry = RegistryEntry(
        case_id=case.case_id,
        title=case.title,
        belt_level=case.belt_level,
        leader=case.leader,
        department=case.department,
        created_at=case.created_at,
        target_date=case.target_date,
        current_phase=case.current_phase,
        phase_started_at=datetime.now(timezone.utc).isoformat(),
    )
    registry.cases.append(entry)
    await save_registry(registry)


async def _update_registry_entry(
    case: CaseDocument, phase: str, summary: str, now: str
) -> None:
    """Update registry entry after gate pass."""
    registry = await load_registry()
    for entry in registry.cases:
        if entry.case_id == case.case_id:
            entry.current_phase = case.current_phase
            entry.phase_started_at = now
            entry.status = case.status
            setattr(entry.phase_summary, phase, summary)
            # RAG status — simple days-based calculation
            try:
                target = date.fromisoformat(case.target_date)
                days_left = (target - date.today()).days
                total = (
                    target - date.fromisoformat(case.created_at[:10])
                ).days
                pct_left = days_left / total if total > 0 else 1
                entry.rag_status = (
                    "red" if pct_left < 0.2
                    else "amber" if pct_left < 0.4
                    else "green"
                )
            except Exception:
                entry.rag_status = "green"
            break
    await save_registry(registry)


# ── upload files ──────────────────────────────────────────────────────────

async def upload_file(
    case_id: str,
    filename: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    """Upload a file to blob and return its blob path."""
    blob_path = f"uploads/{case_id}/{filename}"
    blob = _container().get_blob_client(blob_path)
    await blob.upload_blob(
        data,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )
    return blob_path


__all__ = [
    "REGISTRY_BLOB_PATH",
    "aclose",
    "append_turn",
    "case_path",
    "create_case",
    "load_case",
    "load_registry",
    "register_case",
    "save_case",
    "save_registry",
    "storage_configured",
    "upload_file",
    "write_phase_gate",
]
