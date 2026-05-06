from __future__ import annotations

import logging
from typing import Any, Optional, Literal

from pydantic import BaseModel
from langchain_openai import AzureChatOpenAI

from backend.storage.ingestion.case_ingestion import CaseEntryService, CaseIngestionService
from backend.storage.ingestion.evidence_ingestion import EvidenceIngestionService
from backend.storage.ingestion.knowledge_ingestion import KnowledgeIngestionService
from backend.utils.text import normalize_action

from backend.gateway.case_manager import (
    create_case,
    update_case,
    close_case,
    reindex_case as _reindex_case,
)
from backend.gateway.content_ingestion import (
    upload_evidence,
    upload_knowledge_from_envelope,
    upload_knowledge_file,
)
from backend.gateway.reasoning_handler import handle_ai_reasoning
from backend.gateway.suggestion_engine import generate_suggestions as _generate_suggestions

_logger = logging.getLogger(__name__)


class EntryEnvelope(BaseModel):
    intent: Literal["CASE_INGESTION", "AI_REASONING"]
    action: Optional[str] = None
    payload: dict[str, Any] = {}
    case_id: Optional[str] = None
    event: Optional[str] = None


class EntryResponseEnvelope(BaseModel):
    intent: str
    status: str
    data: dict[str, Any] = {}
    errors: list[str] = []


class EntryHandler:
    def __init__(
        self,
        case_entry: CaseEntryService,
        evidence_ingestion: EvidenceIngestionService,
        case_ingestion: CaseIngestionService,
        knowledge_ingestion: KnowledgeIngestionService,
        unified_graph: Any,
        llm_client: AzureChatOpenAI | None = None,
    ) -> None:
        self._case_entry = case_entry
        self._evidence_ingestion = evidence_ingestion
        self._case_ingestion = case_ingestion
        self._knowledge_ingestion = knowledge_ingestion
        self._unified_graph = unified_graph
        self._llm_client = llm_client

    def handle_entry(self, envelope: EntryEnvelope) -> EntryResponseEnvelope:
        intent = (envelope.intent or "").upper()
        if intent == "CASE_INGESTION":
            return self._handle_case_ingestion(envelope)
        if intent == "AI_REASONING":
            return handle_ai_reasoning(envelope, self._unified_graph)
        raise ValueError(f"Unsupported intent: {envelope.intent}")

    def _handle_case_ingestion(self, envelope: EntryEnvelope) -> EntryResponseEnvelope:
        _logger.debug("[DEBUG] Received action: %s", envelope.action)
        _logger.debug("[DEBUG] Received event: %s", envelope.event)
        action = normalize_action(envelope.action or envelope.event)
        _logger.debug("[DEBUG] Normalized action: %s", action)

        if action == "CREATE_CASE":
            data = create_case(envelope, self._case_entry, self._case_ingestion)
        elif action == "UPDATE_CASE":
            data = update_case(envelope, self._case_entry, self._case_ingestion)
        elif action == "CLOSE_CASE":
            data = close_case(envelope, self._case_entry, self._case_ingestion)
        elif action == "UPLOAD_EVIDENCE":
            data = upload_evidence(envelope, self._evidence_ingestion)
        elif action == "UPLOAD_KNOWLEDGE":
            data = upload_knowledge_from_envelope(envelope, self._knowledge_ingestion)
        else:
            raise ValueError(f"Unsupported case intent: {action}")
        return EntryResponseEnvelope(
            intent=envelope.intent,
            status="accepted",
            data=data,
        )

    def generate_suggestions(
        self, case_id: str, case_context: dict[str, Any]
    ) -> list[dict[str, str]]:
        return _generate_suggestions(case_id, case_context, self._llm_client)

    def upload_knowledge(self, filename: str, data: bytes, content_type: str) -> None:
        upload_knowledge_file(filename, data, content_type, self._knowledge_ingestion)

    def reindex_case(self, case_id: str) -> dict[str, str]:
        return _reindex_case(case_id, self._case_ingestion)

    def _compute_llm_stats(self) -> dict | str:
        # DEPRECATED: orphaned — llm_calls.jsonl no longer written
        raise NotImplementedError(
            "_compute_llm_stats is deprecated: llm_calls.jsonl is no longer written"
        )


__all__ = ["EntryEnvelope", "EntryHandler", "EntryResponseEnvelope"]
