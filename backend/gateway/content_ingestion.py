from __future__ import annotations

import logging
from typing import Any

from backend.storage.ingestion.evidence_ingestion import EvidenceIngestionService
from backend.storage.ingestion.knowledge_ingestion import KnowledgeIngestionService
from backend.utils.text import decode_base64

_logger = logging.getLogger(__name__)


def upload_evidence(
    envelope, evidence_service: EvidenceIngestionService
) -> dict[str, Any]:
    case_id = envelope.case_id or (envelope.payload or {}).get("case_id")
    if not case_id:
        raise ValueError("case_id is required")
    files = (envelope.payload or {}).get("files", [])
    uploaded = []
    for item in files:
        filename = item.get("filename") or "unknown"
        content_type = item.get("content_type") or "application/octet-stream"
        data_base64 = item.get("data_base64") or ""
        raw = decode_base64(data_base64)
        evidence_service.upload_evidence(case_id, filename, raw, content_type)
        uploaded.append(
            {
                "filename": filename,
                "content_type": content_type,
                "size_bytes": len(raw),
            }
        )
    return {"case_id": case_id, "uploaded": uploaded}


def upload_knowledge_from_envelope(
    envelope, knowledge_service: KnowledgeIngestionService
) -> dict[str, Any]:
    documents = (envelope.payload or {}).get("documents", [])
    uploaded = []
    for item in documents:
        filename = item.get("filename") or "unknown"
        content_type = item.get("content_type") or "application/octet-stream"
        data_base64 = item.get("data_base64") or ""
        raw = decode_base64(data_base64)
        try:
            knowledge_service.upload_document(filename, raw, content_type)
        except Exception as e:
            _logger.error(
                "[KNOWLEDGE] upload failed for %r: %s: %s",
                filename,
                type(e).__name__,
                e,
            )
            raise
        uploaded.append(
            {
                "filename": filename,
                "content_type": content_type,
                "size_bytes": len(raw),
            }
        )
    return {"status": "uploaded", "documents": uploaded}


def upload_knowledge_file(
    filename: str,
    data: bytes,
    content_type: str,
    knowledge_service: KnowledgeIngestionService,
) -> None:
    try:
        knowledge_service.upload_document(filename, data, content_type)
    except Exception as e:
        _logger.error(
            "[KNOWLEDGE] upload failed for %r: %s: %s",
            filename,
            type(e).__name__,
            e,
        )
        raise
