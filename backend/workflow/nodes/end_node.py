from __future__ import annotations

from backend.state import IncidentGraphState
from backend.workflow.models import FinalResponsePayload


def end_node(state: IncidentGraphState) -> dict:
    """Terminal node — no-op pass-through."""
    return {"_last_node": "end_node"}


# DEPRECATED: replaced by end_node() function above — remove in Phase 8
class EndNode:
    def run(self, final_response: FinalResponsePayload) -> FinalResponsePayload:
        return final_response


__all__ = ["EndNode"]
