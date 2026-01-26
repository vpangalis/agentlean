from __future__ import annotations

import logging

from backend.application.case.CaseService import CaseService
from backend.domain.case.events.CaseClosed import CaseClosed

logger = logging.getLogger(__name__)


class CaseClosedObserver:
    """Read-only observer that extracts insight from closed cases."""

    def __init__(self, case_service: CaseService) -> None:
        self._case_service = case_service

    def handle(self, event: CaseClosed) -> None:
        case_doc = self._case_service.load_case(event.case_id)
        meta = case_doc.get("meta", {})
        insight = {
            "case_id": event.case_id,
            "closed_at": event.closed_at.isoformat(),
            "version": event.version,
            "status": case_doc.get("status"),
            "updated_at": meta.get("updated_at"),
        }
        logger.info("Case closed insight: %s", insight)
