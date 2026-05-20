from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient

from backend.core.config import settings
from backend.storage.models import (
    CaseDocument,
    CaseRegistry,
    RegistryEntry,
    PhaseRecord,
    PhaseSummaryRecord,
)

logger = logging.getLogger(__name__)

REGISTRY_BLOB_PATH = "registry.json"


class ImproveBlobClient:
    """Azure Blob client for Agent Improve case storage.
    Mirrors BlobStorageClient pattern from agent-resolve."""

    def __init__(self):
        if not settings.AZURE_BLOB_CONNECTION_STRING:
            raise RuntimeError("AZURE_BLOB_CONNECTION_STRING not configured")
        service = BlobServiceClient.from_connection_string(
            settings.AZURE_BLOB_CONNECTION_STRING
        )
        self.container = service.get_container_client(
            settings.AZURE_BLOB_CONTAINER_IMPROVE
        )

    # ── low-level helpers ──────────────────────────────────────────────────

    def _upload(self, path: str, data: str, overwrite: bool = True) -> None:
        self.container.upload_blob(path, data, overwrite=overwrite)

    def _download(self, path: str) -> str:
        blob = self.container.get_blob_client(path)
        return blob.download_blob().readall().decode("utf-8")

    def _exists(self, path: str) -> bool:
        try:
            self.container.get_blob_client(path).get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False

    # ── case CRUD ──────────────────────────────────────────────────────────

    def case_path(self, case_id: str) -> str:
        return f"cases/case_{case_id}.json"

    def load_case(self, case_id: str) -> Optional[CaseDocument]:
        """Load case from blob. Returns None if not found."""
        try:
            raw = self._download(self.case_path(case_id))
            return CaseDocument.model_validate_json(raw)
        except ResourceNotFoundError:
            return None
        except Exception as e:
            logger.error("load_case %s failed: %s", case_id, e)
            return None

    def save_case(self, case: CaseDocument) -> None:
        """Save full case document to blob."""
        self._upload(
            self.case_path(case.case_id),
            case.model_dump_json(indent=2),
        )

    def create_case(self, case: CaseDocument) -> None:
        """Create new case — raises if already exists."""
        path = self.case_path(case.case_id)
        if self._exists(path):
            raise ValueError(f"Case {case.case_id} already exists")
        self._upload(path, case.model_dump_json(indent=2), overwrite=False)

    # ── phase gate operations ──────────────────────────────────────────────

    def write_phase_gate(
        self,
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
        case = self.load_case(case_id)
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
        phase_order = ["define", "measure", "analyse_phase", "improve", "control"]
        current_idx = phase_order.index(phase)
        if current_idx < len(phase_order) - 1:
            case.current_phase = phase_order[current_idx + 1]
        else:
            case.current_phase = "complete"
            case.status = "complete"

        self.save_case(case)
        self._update_registry_entry(case, phase, summary, now)
        logger.info(
            "Phase gate written: %s / %s by %s", case_id, phase, submitted_by
        )

    # ── conversation history ───────────────────────────────────────────────

    def append_turn(self, case_id: str, turn: dict) -> None:
        """Append one conversation turn to case history."""
        case = self.load_case(case_id)
        if case is None:
            raise ValueError(f"Case {case_id} not found")
        case.conversation_history.append(turn)
        self.save_case(case)

    # ── registry operations ────────────────────────────────────────────────

    def load_registry(self) -> CaseRegistry:
        """Load registry. Returns empty registry if not found."""
        try:
            raw = self._download(REGISTRY_BLOB_PATH)
            return CaseRegistry.model_validate_json(raw)
        except ResourceNotFoundError:
            return CaseRegistry()

    def save_registry(self, registry: CaseRegistry) -> None:
        registry.last_updated = datetime.now(timezone.utc).isoformat()
        self._upload(REGISTRY_BLOB_PATH, registry.model_dump_json(indent=2))

    def register_case(self, case: CaseDocument) -> None:
        """Add new case to registry."""
        registry = self.load_registry()
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
        self.save_registry(registry)

    def _update_registry_entry(
        self, case: CaseDocument, phase: str, summary: str, now: str
    ) -> None:
        """Update registry entry after gate pass."""
        from datetime import date

        registry = self.load_registry()
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
        self.save_registry(registry)

    # ── upload files ───────────────────────────────────────────────────────

    def upload_file(
        self,
        case_id: str,
        filename: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file to blob and return its blob path."""
        from azure.storage.blob import ContentSettings

        blob_path = f"uploads/{case_id}/{filename}"
        blob_client = self.container.get_blob_client(blob_path)
        blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        return blob_path


# Module-level singleton — import and use directly in nodes.
# Wrapped so import succeeds when Azure credentials are absent.
try:
    blob_client = ImproveBlobClient()
except Exception:
    blob_client = None  # type: ignore
