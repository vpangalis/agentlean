from __future__ import annotations

from backend.domain.case.events.CaseClosed import CaseClosed
from backend.application.CaseIngestionService import CaseIngestionService


class CaseClosedHandler:
    """Application handler that reacts to a CaseClosed domain event."""

    def __init__(self, ingestion_service: CaseIngestionService) -> None:
        self._ingestion_service = ingestion_service

    def handle(self, event: CaseClosed) -> None:
        self._ingestion_service.ingest_closed_case(event.case_id)
