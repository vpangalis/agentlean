from __future__ import annotations

from typing import Any

from backend.ingestion.case_ingestion import CaseEntryService
from backend.workflow.models import ContextNodeOutput


class ContextNode:
    def __init__(self, case_entry_service: CaseEntryService) -> None:
        self._case_entry_service = case_entry_service

    def run(self, case_id: str | None) -> ContextNodeOutput:
        if not case_id:
            return ContextNodeOutput(case_context=None, current_d_state=None)

        try:
            case_doc = self._case_entry_service.get_case(case_id)
        except FileNotFoundError:
            # Case does not exist in storage — continue graph without context
            return ContextNodeOutput(case_context=None, current_d_state=None)

        return ContextNodeOutput(
            case_context=case_doc,
            current_d_state=self._detect_current_state(case_doc),
        )

    def _detect_current_state(self, case_doc: dict[str, Any]) -> str | None:
        reasoning_state = case_doc.get("reasoning_state")
        if not isinstance(reasoning_state, dict):
            reasoning_state = case_doc.get("d_states")
        # Support legacy "phases" format (blob docs with D1_D2 key)
        if not isinstance(reasoning_state, dict):
            phases = case_doc.get("phases")
            if isinstance(phases, dict) and phases:
                reasoning_state = {
                    ("D1_2" if k == "D1_D2" else k): v for k, v in phases.items()
                }
        if not isinstance(reasoning_state, dict):
            return None

        progression = ["D8", "D7", "D6", "D5", "D4", "D3", "D1_2"]
        for key in progression:
            block = reasoning_state.get(key)
            if not isinstance(block, dict):
                continue
            # Phases format uses header.completed; native format uses status field
            header = block.get("header")
            if isinstance(header, dict) and header.get("completed"):
                return key
            status = str(block.get("status") or "").lower()
            has_data = isinstance(block.get("data"), dict) and bool(block.get("data"))
            if status in {"in_progress", "completed"} or has_data:
                return key
        return "D1_2"


__all__ = ["ContextNode"]
