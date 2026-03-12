from __future__ import annotations

import logging
from typing import Any

from backend.ingestion.case_ingestion import CaseEntryService, CaseIngestionService

_logger = logging.getLogger(__name__)


def create_case(
    envelope, case_entry: CaseEntryService, case_ingestion: CaseIngestionService
) -> dict[str, Any]:
    payload = envelope.payload or {}
    _logger.debug(
        "[DEBUG AI] payload keys: %s, question: %r",
        list(payload.keys()),
        payload.get("question"),
    )

    case_id = payload.get("case_id") or envelope.case_id
    opened_at = payload.get("opened_at")
    if not case_id:
        raise ValueError("case_id is required")
    doc = case_entry.create_case(case_id, opened_at)
    _logger.info("[CREATE_CASE] blob save complete for %s, starting index", case_id)
    try:
        case_ingestion.index_open_case(str(case_id))
        _logger.info("[CREATE_CASE] index complete for %s", case_id)
    except Exception as exc:
        _logger.exception("[CREATE_CASE] index FAILED for %s: %s", case_id, exc)
    return {"status": "created", "case_id": doc.get("case_id")}


def update_case(
    envelope, case_entry: CaseEntryService, case_ingestion: CaseIngestionService
) -> dict[str, Any]:
    payload = envelope.payload or {}
    # Bulk-import mode: UI sends a 'cases' array with no top-level case_id.
    cases = payload.get("cases")
    if isinstance(cases, list) and cases:
        return import_bulk_cases(cases, case_entry, case_ingestion)

    case_id = envelope.case_id or payload.get("case_id")
    if not case_id:
        raise ValueError("case_id is required")
    result = case_entry.patch_case(case_id, payload)
    _logger.info("[UPDATE_CASE] patch complete for %s, starting re-index", case_id)
    try:
        case_ingestion.index_open_case(str(case_id))
        _logger.info("[UPDATE_CASE] re-index complete for %s", case_id)
    except Exception as exc:
        _logger.exception("[UPDATE_CASE] re-index FAILED for %s: %s", case_id, exc)
    return {"status": "updated", **result}


def import_bulk_cases(
    cases: list[dict[str, Any]],
    case_entry: CaseEntryService,
    case_ingestion: CaseIngestionService,
) -> dict[str, Any]:
    """Import a batch of closed case documents sent as a JSON array."""
    imported: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    for item in cases:
        case_id = str(item.get("case_id") or "").strip()
        case_doc = item.get("case_doc") or {}
        if not case_id:
            failed.append({"case_id": None, "error": "missing case_id in item"})
            continue
        try:
            if not isinstance(case_doc, dict):
                case_doc = {}
            case_doc.setdefault("case_id", case_id)
            case_entry.save_case_document(case_id, case_doc)
            case_ingestion.ingest_closed_case(case_id)
            imported.append({"case_id": case_id, "status": "imported"})
        except Exception as exc:
            _logger.exception("[BULK_IMPORT] failed for %s: %s", case_id, exc)
            failed.append({"case_id": case_id, "error": str(exc)})
    return {
        "status": "bulk_imported",
        "imported": len(imported),
        "failed": len(failed),
        "results": imported + failed,
    }


def close_case(
    envelope, case_entry: CaseEntryService, case_ingestion: CaseIngestionService
) -> dict[str, Any]:
    case_id = envelope.case_id or (envelope.payload or {}).get("case_id")
    if not case_id:
        raise ValueError("case_id is required")
    payload = envelope.payload or {}
    if isinstance(payload, dict) and "case_id" not in payload:
        payload = {**payload, "case_id": case_id}
    existing = case_entry.get_case(case_id)
    merged = case_entry.merge_case_document(existing, payload)
    case_entry.save_case_document(case_id, merged)
    case_ingestion.ingest_closed_case(case_id)
    return {"status": "closed", "case_id": case_id}


def reindex_case(
    case_id: str, case_ingestion: CaseIngestionService
) -> dict[str, str]:
    """Force-index (or re-index) a case regardless of its status."""
    try:
        case_ingestion.index_open_case(case_id)
        return {"status": "indexed", "case_id": case_id}
    except RuntimeError as exc:
        _logger.error(
            "[REINDEX] Azure Search rejected document for %s: %s", case_id, exc
        )
        return {
            "status": "rejected_by_azure",
            "case_id": case_id,
            "error": str(exc),
        }
    except Exception as exc:
        _logger.exception("[REINDEX] unexpected error for %s: %s", case_id, exc)
        return {
            "status": "error",
            "case_id": case_id,
            "error": str(exc),
            "type": type(exc).__name__,
        }
