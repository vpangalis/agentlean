from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Iterable

from backend.domain.case.models import CaseModel
from backend.infrastructure.embeddings.EmbeddingClient import EmbeddingClient
from backend.infrastructure.search.CaseSearchIndex import CaseSearchIndex
from backend.infrastructure.storage.CaseReadRepository import CaseReadRepository


CASE_INDEX_NAME = "case_index_v3"
DOC_ID_SUFFIX = f"__{CASE_INDEX_NAME}"


class CaseIngestionService:
    """Orchestrates ingestion of closed cases into search infrastructure."""

    def __init__(
        self,
        search_index: CaseSearchIndex,
        case_repository: CaseReadRepository,
        embedding_client: EmbeddingClient,
        logger: logging.Logger | None = None,
    ) -> None:
        self._search_index = search_index
        self._case_repository = case_repository
        self._embedding_client = embedding_client
        self._logger = logger or logging.getLogger("case_ingestion")

    def ingest_all_closed_cases(self) -> None:
        paths = self._case_repository.list_case_paths()
        for path in paths:
            case_id = self._extract_case_id(path)
            self.ingest_closed_case(case_id)

    def ingest_closed_case(self, case_id: str) -> None:
        path = f"cases/{case_id}/case.json"

        try:
            data = self._case_repository.load_case(path)
            case_model = CaseModel.model_validate(data)
        except Exception as exc:
            self._log_outcome("FAILED", case_id, f"schema_validation_error: {exc}")
            return

        if not self._validate_closed_case(case_model):
            self._log_outcome("SKIPPED", case_id, "status_not_closed")
            return

        doc_id = self._build_doc_id(case_id)
        self._validate_doc_id(doc_id)

        searchable_fields = self._build_searchable_fields(case_model.model_dump())
        new_hash = self._searchable_hash(searchable_fields)
        existing_hash = self._existing_doc_hash(doc_id)

        if existing_hash is not None:
            if existing_hash == new_hash:
                self._log_outcome("SKIPPED", case_id, "content_hash_unchanged")
                return
            # Closed cases are immutable in Sprint 3; do not regenerate embeddings.
            self._log_outcome(
                "FAILED",
                case_id,
                "content_hash_changed_for_closed_case",
            )
            return

        embedding_input = self._build_embedding_input(searchable_fields)
        if not embedding_input:
            self._log_outcome("FAILED", case_id, "empty_embedding_input")
            return

        try:
            embedding = self._embedding_client.generate_embedding(embedding_input)
        except Exception as exc:
            self._log_outcome("FAILED", case_id, f"embedding_failed: {exc}")
            return

        document = self._build_index_document(case_model.model_dump(), doc_id)
        document["content_vector"] = embedding

        try:
            self._search_index.upload_documents([document])
        except Exception as exc:
            self._log_outcome("FAILED", case_id, f"index_upsert_failed: {exc}")
            return

        self._log_outcome("SUCCESS", case_id)


    @staticmethod
    def _now_iso() -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _log_outcome(self, status: str, case_id: str, reason: str | None = None) -> None:
        payload = {
            "timestamp": self._now_iso(),
            "case_id": case_id,
            "status": status,
        }
        if reason:
            payload["reason"] = reason
        self._logger.info(json.dumps(payload))

    @staticmethod
    def _extract_case_id(path: str) -> str:
        parts = path.split("/")
        if len(parts) < 3 or parts[0] != "cases" or parts[-1] != "case.json":
            raise ValueError(f"Invalid case path: {path}")
        return parts[1]

    @staticmethod
    def _build_doc_id(case_id: str) -> str:
        """Build immutable, versioned document IDs for case_index_v3."""
        return f"{case_id}{DOC_ID_SUFFIX}"

    @staticmethod
    def _validate_doc_id(doc_id: str) -> None:
        """Fail fast if a doc_id does not match {case_id}__case_index_v3."""
        if not doc_id.endswith(DOC_ID_SUFFIX) or len(doc_id) == len(DOC_ID_SUFFIX):
            raise ValueError("Invalid doc_id format. Expected '{case_id}__case_index_v3'.")

    @staticmethod
    def _safe_get(data: dict, *keys: str, default: Any = "") -> Any:
        cur: Any = data
        for key in keys:
            if not isinstance(cur, dict) or key not in cur:
                return default
            cur = cur[key]
        return cur

    @staticmethod
    def _flatten(values: Iterable[Any]) -> list[str]:
        result: list[str] = []
        for value in values:
            if value is None:
                continue
            if isinstance(value, list):
                result.extend([str(v) for v in value if v not in (None, "")])
            elif value != "":
                result.append(str(value))
        return result

    def _join_text(self, values: Iterable[Any]) -> str:
        parts = [str(v).strip() for v in self._flatten(values) if str(v).strip()]
        return "\n".join(parts)

    def _join_dict_field(self, values: Iterable[Any], field: str) -> str:
        items: list[str] = []
        for value in values:
            if isinstance(value, dict) and field in value:
                items.append(str(value.get(field, "")).strip())
        return self._join_text(items)

    @staticmethod
    def _collect_discipline_completed(phases: dict[str, Any]) -> list[str]:
        completed: list[str] = []
        for phase_key, phase in phases.items():
            header = phase.get("header", {}) if isinstance(phase, dict) else {}
            if not header.get("completed"):
                continue
            discipline = header.get("discipline")
            if isinstance(discipline, list):
                completed.extend([str(d) for d in discipline])
            elif discipline:
                completed.append(str(discipline))
        return completed

    def _build_searchable_fields(self, case_doc: dict[str, Any]) -> dict[str, Any]:
        phases = case_doc.get("phases", {})
        evidence = case_doc.get("evidence", [])
        ai = case_doc.get("ai", {}) or {}

        fishbone = self._safe_get(phases, "D5", "data", "fishbone", default={})
        fishbone_text = self._join_text(
            self._flatten([fishbone.get(k, []) for k in fishbone.keys()])
        )

        five_whys = self._safe_get(phases, "D5", "data", "five_whys", default={})
        five_whys_text = self._join_text(
            [five_whys.get("A", []), five_whys.get("B", [])]
        )

        evidence_descriptions = self._join_text(
            [e.get("description", "") for e in evidence]
        )
        evidence_tags = self._flatten([e.get("tags", []) for e in evidence])

        return {
            "problem_description": self._safe_get(
                phases, "D1_D2", "data", "problem_description"
            ),
            "team_members": self._safe_get(
                phases, "D1_D2", "data", "team_members", default=[]
            ),
            "what_happened": self._safe_get(phases, "D3", "data", "what_happened"),
            "why_problem": self._safe_get(phases, "D3", "data", "why_problem"),
            "when": self._safe_get(phases, "D3", "data", "when"),
            "where": self._safe_get(phases, "D3", "data", "where"),
            "who": self._safe_get(phases, "D3", "data", "who"),
            "how_identified": self._safe_get(
                phases, "D3", "data", "how_identified"
            ),
            "impact": self._safe_get(phases, "D3", "data", "impact"),
            "immediate_actions_text": self._join_dict_field(
                self._safe_get(phases, "D4", "data", "actions", default=[]),
                "action",
            ),
            "permanent_actions_text": self._join_dict_field(
                self._safe_get(phases, "D6", "data", "actions", default=[]),
                "action",
            ),
            "investigation_tasks_text": self._join_dict_field(
                self._safe_get(
                    phases, "D5", "data", "investigation_tasks", default=[]
                ),
                "task",
            ),
            "factors_text": self._join_dict_field(
                self._safe_get(phases, "D5", "data", "factors", default=[]),
                "factor",
            ),
            "fishbone_text": fishbone_text,
            "five_whys_text": five_whys_text,
            "evidence_descriptions": evidence_descriptions,
            "evidence_tags": evidence_tags,
            "ai_summary": ai.get("summary", ""),
        }

    def _build_embedding_input(self, searchable_fields: dict[str, Any]) -> str:
        parts: list[str] = []
        for key, value in searchable_fields.items():
            if isinstance(value, list):
                parts.append(self._join_text(value))
            else:
                parts.append(str(value))
        return self._join_text(parts)

    @staticmethod
    def _searchable_hash(searchable_fields: dict[str, Any]) -> str:
        payload = json.dumps(searchable_fields, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _existing_doc_hash(self, doc_id: str) -> str | None:
        doc = self._search_index.try_get_document(doc_id)
        if doc is None:
            return None

        existing_searchable = {
            key: doc.get(key)
            for key in [
                "problem_description",
                "team_members",
                "what_happened",
                "why_problem",
                "when",
                "where",
                "who",
                "how_identified",
                "impact",
                "immediate_actions_text",
                "permanent_actions_text",
                "investigation_tasks_text",
                "factors_text",
                "fishbone_text",
                "five_whys_text",
                "evidence_descriptions",
                "evidence_tags",
                "ai_summary",
            ]
        }
        return self._searchable_hash(existing_searchable)

    def _build_index_document(
        self,
        case_doc: dict[str, Any],
        doc_id: str,
    ) -> dict[str, Any]:
        case = case_doc["case"]
        phases = case_doc.get("phases", {})
        searchable_fields = self._build_searchable_fields(case_doc)

        document: dict[str, Any] = {
            "doc_id": doc_id,
            "case_id": case.get("case_number"),
            "status": case.get("status"),
            "opening_date": case.get("opening_date"),
            "closure_date": case.get("closure_date")
            or self._safe_get(phases, "D8", "data", "closure_date", default=None),
            "created_at": self._safe_get(case_doc, "meta", "created_at", default=None),
            "updated_at": self._safe_get(case_doc, "meta", "updated_at", default=None),
            "version": self._safe_get(case_doc, "meta", "version", default=1),
            "organization_country": self._safe_get(
                phases, "D1_D2", "data", "organization", "country"
            ),
            "organization_site": self._safe_get(
                phases, "D1_D2", "data", "organization", "site"
            ),
            "organization_department": self._safe_get(
                phases, "D1_D2", "data", "organization", "department"
            ),
            "discipline_completed": self._collect_discipline_completed(phases),
        }

        document.update(searchable_fields)
        return document

    @staticmethod
    def _validate_closed_case(case_doc: CaseModel) -> bool:
        return case_doc.case.status == "closed"
