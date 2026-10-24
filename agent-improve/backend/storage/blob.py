"""Case records on Azure Blob, as module-level functions.

Owner of the **system of record**: the case document, the registry, and uploaded
files. Writes on case create, on gate pass and on file upload, and **never
mid-conversation** — conversation history lives in the checkpoint until a gate
passes.

Paths owned, and no others:

    cases/case_{case_id}.json
    registry.json
    uploads/{case_id}/{filename}

CONCERN SEPARATION — THIS IS NOT `core/store.py`
------------------------------------------------
There are three Blob concerns with three owners, and they are not merged:

  * **checkpoints** — in-flight graph state, `checkpoints/{case_id}/...`,
    owned by `core/checkpointer.py`.
  * **cross-phase artifacts** — `store/...`, owned by `AzureBlobStore` in
    `core/store.py`, which is a LangGraph `BaseStore`.
  * **case records** — the three prefixes above. This file.

This module does not import, wrap or subclass `AzureBlobStore`, and must not
start doing so: `cases/case_{id}.json` is authoritative, and the Store's `case`
namespace is a session-start COPY so mappers can depend on `BaseStore` alone.
Two writers on one authority is what the separation prevents.

NO CLASS LIVES HERE
-------------------
`storage/blob.py` is one of the files that hold **module-level functions
ONLY** (CLAUDE.md), with no exception. Do not add one — the state a class
would hold is the cached client below, which is module state and needs no
object around it.
"""
from __future__ import annotations

import asyncio
import json
import secrets
from contextlib import asynccontextmanager
import logging
from datetime import date
from typing import AsyncIterator, Callable, Optional

from azure.core import MatchConditions
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError, ResourceNotFoundError
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import (
    BlobServiceClient as AsyncBlobServiceClient,
    ContainerClient as AsyncContainerClient,
)

from backend.core.config import settings
from backend.core.errors import CaseNumberTaken, RegistryChanged
from backend.core.citations import CitationRecord, as_records
from backend.core.substate import merge_field_log
from backend.storage import layout
from backend.storage.models import (
    AnalystOutputRecord,
    CaseDocument,
    CaseRegistry,
    PhaseRecord,
    RegistryEntry,
    UploadRecord,
)
from backend.core.clock import utc_now

logger = logging.getLogger(__name__)

REGISTRY_BLOB_PATH = layout.REGISTRY_BLOB


# ── the aio session lifecycle ─────────────────────────────────────────────
#
# CACHED, and deliberately so — the opposite of `AzureBlobStore`'s choice.
#
# An `azure.storage.blob.aio` client owns an aiohttp session, and that session
# owns a TLS connection pool. `core/store.py` opens and closes one per
# operation because Store writes happen a handful of times per phase, so the
# reconnect cost is paid rarely and buys a lifecycle with nothing to clean up.
#
# That reasoning does not transfer here. `load_case` and `save_case` are on the
# `/ask` path — every request pays both. A per-operation client pays the TLS
# handshake and connection setup that a fresh pool cannot reuse, several times
# the cost of the blob I/O itself; constructing the client and tearing down its
# session costs almost nothing.
#
# The lifecycle cost of caching is one `await aclose()` at shutdown, wired to
# `backend/app.py`'s `@app.on_event("shutdown")`. Closing an HTTP session is a
# different concern from draining in-flight coaching turns
# (`RunControl.request_drain()`).
#
# The client is cached against the loop it was built on. A session is bound to
# its event loop, and a client carried across loops would fail at the first
# await on a closed transport — which is what a test suite running several
# `asyncio.run()` calls in one process would do.
_client: Optional[AsyncBlobServiceClient] = None
_client_loop: Optional[asyncio.AbstractEventLoop] = None


def storage_configured() -> bool:
    """Whether Blob credentials are present.

    A check of settings only, with no client built at import time — so an
    unrelated construction error can never read to a caller as "not
    configured".
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


async def _download_tagged(path: str) -> tuple[str, str]:
    """ADR-0092: a blob's text and the ETag it was read at."""
    downloader = await _container().get_blob_client(path).download_blob()
    raw = await downloader.readall()
    return raw.decode("utf-8"), str(downloader.properties.etag)


async def _upload_conditional(path: str, data: str, etag: str) -> None:
    """ADR-0092: overwrite `path` only if it still has `etag` (`If-Match`); ResourceModifiedError otherwise."""
    await _container().upload_blob(path, data, overwrite=True, etag=etag,
                                   match_condition=MatchConditions.IfNotModified)


async def _download(path: str) -> str:
    blob = _container().get_blob_client(path)
    downloader = await blob.download_blob()
    raw = await downloader.readall()
    return raw.decode("utf-8")


async def download_bytes(path: str) -> bytes:
    """The raw bytes at `path`, undecoded.

    **`_download` decodes UTF-8 and would corrupt every format this is for.**
    xlsx, pdf and docx are binary; running `.decode("utf-8")` over them either
    raises or silently mangles them, so `load_evidence_series` needs a reader
    that does not.
    """
    blob = _container().get_blob_client(path)
    downloader = await blob.download_blob()
    return await downloader.readall()


# ── case CRUD ─────────────────────────────────────────────────────────────

#: T11 (DEF-115) — the lease outlives a turn (R13: 45 s) and is released when the turn ends; Azure
#: allows 15–60 s or infinite, and a fixed 60 s frees a crashed writer's case within a minute.
LEASE_SECONDS = 60


@asynccontextmanager
async def case_lease(case_id: str) -> AsyncIterator[None]:
    """One writer per `thread_id` at a time — T11 (ADR-0018). Takes the Blob lease
    on the case's lock blob (`layout.CASE_LOCK_BLOB`, created empty on first use) for the length
    of one graph run and releases it after. Another holder → `CaseBusyError` (Azure's 409
    LeaseAlreadyPresent). Any other failure to take it (storage unreachable, no permission) is
    logged as a FINDING and the run goes on: ADR-0018's ETag check still detects a collision."""
    from azure.core.exceptions import HttpResponseError, ResourceExistsError

    from backend.core.errors import CaseBusyError
    lease = None
    try:
        client = _container().get_blob_client(layout.CASE_LOCK_BLOB.format(case_id=case_id))
        try:
            await client.upload_blob(b"", overwrite=False)
        except ResourceExistsError:
            pass
        lease = await client.acquire_lease(lease_duration=LEASE_SECONDS)
    except HttpResponseError as exc:
        if getattr(exc, "status_code", None) == 409 or "LeaseAlreadyPresent" in str(exc):
            raise CaseBusyError(f"case {case_id} is being written by another turn") from exc
        logger.warning("FINDING — T11: the lease on case %s could not be taken (%s); the turn runs "
                       "on the ETag check alone", case_id, exc)
    except Exception as exc:  # noqa: BLE001 — a lease that cannot be taken must not refuse the Belt
        logger.warning("FINDING — T11: the lease on case %s could not be taken (%s); the turn runs "
                       "on the ETag check alone", case_id, exc)
    try:
        yield
    finally:
        if lease is not None:
            try:
                await lease.release()
            except Exception as exc:  # noqa: BLE001 — it expires within LEASE_SECONDS anyway
                logger.warning("T11: the lease on case %s was not released (%s); it expires in %d s",
                               case_id, exc, LEASE_SECONDS)


def case_path(case_id: str) -> str:
    """Pure path construction — no I/O, so it stays synchronous."""
    return layout.CASE_BLOB.format(case_id=case_id)


async def load_case(case_id: str) -> Optional[CaseDocument]:
    """Load case from blob. Returns None if not found. ADR-0065 (T88): a case written by an
    older release is migrated in memory (the blob is rewritten at the next save); one written by
    a newer release raises `StateSchemaVersionError` — never "not found"."""
    from backend.core import migrations
    from backend.core.errors import StateSchemaVersionError
    try:
        raw = await _download(case_path(case_id))
        data = json.loads(raw)
        found = migrations.version_of(data)
        if found != migrations.current():
            data = migrations.migrate_case(data, found)
        return CaseDocument.model_validate(data)
    except ResourceNotFoundError:
        return None
    except StateSchemaVersionError:
        raise
    except Exception as e:
        # G-243: only a missing case is "not found"; any other failure raises — a failed read taken for
        # "no case" would let an approval write an empty upload list over the case's own.
        logger.error("load_case %s failed: %s", case_id, e)
        raise


async def save_case(case: CaseDocument) -> None:
    """Save full case document to blob, in this release's state schema version (ADR-0065)."""
    from backend.core import migrations
    case.state_schema_version = migrations.current()
    await _upload(
        case_path(case.case_id),
        case.model_dump_json(indent=2),
    )


#: ADR-0092 decision 1: a case number's suffix — 6 characters from letters and digits that cannot be misread
#: (no 0/O, no 1/I): 32**6, about 10**9 numbers a year.
CASE_NUMBER_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CASE_NUMBER_LENGTH = 6


def new_case_number(year: int) -> str:
    """ADR-0092: `IMPR-<year>-` and a random 6-character suffix. Existing numbers never change."""
    return f"IMPR-{year}-" + "".join(secrets.choice(CASE_NUMBER_ALPHABET) for _ in range(CASE_NUMBER_LENGTH))


async def create_case(case: CaseDocument) -> None:
    """ADR-0092 decision 2: the number is reserved by writing the case only if no blob has that name
    (Blob `If-None-Match: *`) — one write, no check-then-write window. `CaseNumberTaken` on a clash."""
    try:
        await _upload(case_path(case.case_id), case.model_dump_json(indent=2), overwrite=False)
    except ResourceExistsError as e:
        raise CaseNumberTaken(case.case_id) from e


async def update_people(case_id: str, change: Callable[[list], list]) -> Optional[CaseDocument]:
    """ADR-0090 decision 2 (T13): a change of the people on the case is written to the case record —
    the record as stored, re-read here, with only `people` changed, so unfinished work in the checkpoint never
    reaches the blob. None when the case does not exist."""
    case = await load_case(case_id)
    if case is None:
        return None
    people = change(list(case.people))
    if people == case.people:
        return case
    from backend.storage.people import lead
    case.people = people
    head = lead(people)
    if head is not None:
        case.leader = head.full_name                 # ADR-0090 decision 4: the lead's one display name
    await save_case(case)
    return case


# ── phase gate operations ─────────────────────────────────────────────────

async def write_phase_gate(
    case_id: str,
    phase: str,
    structured: dict,
    submitted_by: str,
    summary: str,
    citations: list[dict] | None = None,
    uploads: list[dict] | None = None,
    analyst_output: Optional[dict] = None,
    field_log: list[dict] | None = None,
) -> None:
    """Write the approved gate document into the phase record — MERGING.

    Called only after assembly succeeded and the gate passed.

    ══════════════════════════════════════════════════════════════════════
    MERGE, NEVER REPLACE — THE GATE IS WHERE A REVIEWER LOOKS
    ══════════════════════════════════════════════════════════════════════
    Whatever the record holds that this call does not name survives the gate:
    `field_log` (the field change log), `analyst_output`, and the Belt's
    evidence trail in `citations` and `uploads`. **The gate is exactly where a
    reviewer goes looking for it.**

    **A replaced record would make a loss invisible.** A replaced record is a
    well-formed record; nothing reads as missing until somebody asks a question
    only the dropped fields can answer.

    SAFE TO PERFORM TWICE — AND THAT IS A FRAMEWORK REQUIREMENT, NOT CAUTION
    ─────────────────────────────────────────────────────────────────────
    `docs.langchain.com/oss/python/langgraph/interrupts`:
    *"the runtime restarts the entire node from the beginning — it does not
    resume from the exact line where `interrupt()` was called"*, and **"Do not
    create new records without checking if they exist."** Behind a pause,
    **every resume re-runs this write**. So:

      * the approval stamp (`submitted_by` / `submitted_at`) is written on the
        TRANSITION only — re-writing an already-passed gate leaves the original
        stamp, so two writes produce one record rather than one record with a
        moving timestamp;
      * `current_phase` is computed from the `phase` argument, never from the
        case's current value, so it lands on the same answer however many times
        it runs;
      * `_update_registry_entry` matches on `case_id` and updates in place — it
        appends nothing.

    **A re-approval after a reopen still re-stamps**, because reopening
    sets `gate_passed` back to `False` and the write is then a transition
    again. The stamp records when the gate LAST became passed, which is what it
    is for.
    """
    if not structured:
        # G-242: an approved record with no values is never written over the case record's own.
        raise ValueError(f"An empty {phase} record cannot be written as approved for {case_id}")
    case = await load_case(case_id)
    if case is None:
        raise ValueError(f"Case {case_id} not found")

    now = utc_now().isoformat()

    # ── MERGE, never replace ─────────────────────────────────────
    # Whatever this record holds that is not named below SURVIVES the gate.
    record = case.phases.get(phase) or PhaseRecord()
    already_passed = bool(record.gate_passed)

    record.structured = structured
    record.gate_passed = True
    if not already_passed:                  # the transition, stamped once
        record.submitted_by = submitted_by
        record.submitted_at = now

    # `None` means NOT SUPPLIED and keeps what the record holds; an explicit
    # empty list means supplied-and-empty, so a call site passing nothing
    # cannot erase the Belt's evidence trail.
    #
    # **Converted explicitly, because ASSIGNMENT DOES NOT VALIDATE.** Pydantic
    # coerces dicts into models at construction, not on attribute assignment:
    # the record would hold raw dicts, serialise back out looking correct, and
    # fail the next time anything read `.filename` off one.
    if citations is not None:
        record.citations = as_records(citations)                  # G-176: a coach citation never breaks the write
    if uploads is not None:
        record.uploads = [UploadRecord(**u) if isinstance(u, dict) else u
                          for u in uploads]
    if analyst_output is not None:
        record.analyst_output = AnalystOutputRecord(**analyst_output)
    # G-147 (DEF-061): the change log lives in the checkpoint until approval (ADR-0066); the
    # caller hands it over here, merged on the entries' keys, so nothing already logged is lost.
    if field_log is not None:
        record.field_log = merge_field_log(list(record.field_log or []), [dict(e) for e in field_log])

    case.phases[phase] = record

    # Advance current phase
    phase_order = ["define", "measure", "analyse", "improve", "control"]
    current_idx = phase_order.index(phase)
    if current_idx < len(phase_order) - 1:
        case.current_phase = phase_order[current_idx + 1]
    else:
        case.current_phase = "complete"
        case.status = "complete"

    # Two separate writes, the case then the registry.
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

#: ADR-0092 decision 3: how often a change to the case list is re-read and retried before it is an error, and
#: the most a retry waits — jittered (shared resources), so writers that collided do not collide again.
REGISTRY_RETRIES = 30
REGISTRY_RETRY_MAX_S = 0.2


async def load_registry() -> CaseRegistry:
    """Load registry. Returns empty registry if not found. The ETag it was read at rides on it (ADR-0092)."""
    try:
        raw, etag = await _download_tagged(REGISTRY_BLOB_PATH)
    except ResourceNotFoundError:
        registry = CaseRegistry()
        registry._etag = ""                       # read, and there was none: created only if still absent
        return registry
    registry = CaseRegistry.model_validate_json(raw)
    registry._etag = etag
    return registry


async def save_registry(registry: CaseRegistry) -> None:
    """ADR-0092 decision 3: a registry read from storage is written only if nobody changed it since
    (`If-Match: <ETag>`; a new one only if still absent) — `RegistryChanged` otherwise."""
    registry.last_updated = utc_now().isoformat()
    body = registry.model_dump_json(indent=2)
    etag = registry._etag
    try:
        if etag:
            await _upload_conditional(REGISTRY_BLOB_PATH, body, etag)
        else:
            await _upload(REGISTRY_BLOB_PATH, body, overwrite=etag is None)
    except (ResourceModifiedError, ResourceExistsError) as e:
        raise RegistryChanged(REGISTRY_BLOB_PATH) from e


async def _change_registry(change: Callable[[CaseRegistry], bool]) -> None:
    """ADR-0092 decision 3: read the case list, apply `change` (False: nothing to write), write it
    conditionally; on a concurrent change read it again and retry — never a lost entry."""
    for attempt in range(REGISTRY_RETRIES):
        if attempt:
            await asyncio.sleep(secrets.SystemRandom().uniform(0, REGISTRY_RETRY_MAX_S * min(attempt, 5) / 5))
        registry = await load_registry()
        if change(registry) is False:
            return
        try:
            await save_registry(registry)
            return
        except RegistryChanged:
            logger.info("registry changed since it was read — read again and retried (ADR-0092)")
    raise RegistryChanged(f"{REGISTRY_BLOB_PATH}: still changing after {REGISTRY_RETRIES} reads")


async def register_case(case: CaseDocument) -> None:
    """Add new case to registry — by a conditional write, retried on a concurrent change (ADR-0092)."""
    entry = RegistryEntry(
        case_id=case.case_id,
        title=case.title,
        belt_level=case.belt_level,
        leader=case.leader,
        department=case.department,
        created_at=case.created_at,
        target_date=case.target_date,
        current_phase=case.current_phase,
        phase_started_at=utc_now().isoformat(),
    )

    def add(registry: CaseRegistry) -> bool:
        if any(e.case_id == entry.case_id for e in registry.cases):
            return False                          # already listed
        registry.cases.append(entry)
        return True
    await _change_registry(add)


async def set_escalation(case_id: str, escalation: Optional[dict]) -> None:
    """ADR-0076 (T65): mark the case's registry row escalated — `{at, criteria}`, status
    "escalated" — or clear it (None, status back to "active"). The registry, not the case blob:
    nothing about the case blob changes mid-conversation (ADR-0066)."""
    def mark(registry: CaseRegistry) -> bool:
        for entry in registry.cases:
            if entry.case_id == case_id:
                if escalation is None and entry.escalation is None:
                    return False
                entry.escalation = escalation
                entry.status = "escalated" if escalation else "active"
                return True
        return False
    await _change_registry(mark)


async def _update_registry_entry(
    case: CaseDocument, phase: str, summary: str, now: str
) -> None:
    """Update registry entry after gate pass — a conditional write, retried (ADR-0092)."""
    def update(registry: CaseRegistry) -> bool:
        _gate_passed_entry(registry, case, phase, summary, now)
        return True
    await _change_registry(update)


def _gate_passed_entry(registry: CaseRegistry, case: CaseDocument, phase: str, summary: str, now: str) -> None:
    """The registry row after a gate pass: phase, status, summary and the RAG status."""
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
            except (TypeError, ValueError) as exc:
                # W6: a date that cannot be read leaves the status as it was — never a green no date earned.
                logger.warning("registry: case %s's RAG status not recomputed — target %r, created %r (%s)",
                               case.case_id, case.target_date, case.created_at, exc)
            break


# ── upload files ──────────────────────────────────────────────────────────

async def upload_file(
    case_id: str,
    filename: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    """Upload a file to blob and return its blob path."""
    blob_path = layout.UPLOAD_BLOB.format(case_id=case_id, filename=filename)
    blob = _container().get_blob_client(blob_path)
    await blob.upload_blob(
        data,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )
    return blob_path


async def delete_upload(blob_path: str) -> None:
    """W7 (DEF-109): delete an uploaded file's blob. A blob already gone counts as deleted, so a removal that
    failed half-way can be tried again."""
    try:
        await _container().delete_blob(blob_path)
    except ResourceNotFoundError:
        logger.info("delete_upload: %s was already gone", blob_path)


__all__ = [
    "REGISTRY_BLOB_PATH",
    "aclose",
    "append_turn",
    "case_path",
    "create_case",
    "delete_upload",
    "download_bytes",
    "load_case",
    "load_registry",
    "register_case",
    "save_case",
    "save_registry",
    "storage_configured",
    "upload_file",
    "write_phase_gate",
]
