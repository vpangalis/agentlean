from __future__ import annotations

from backend.workflow.models import FinalResponsePayload


class EndNode:
    def run(self, final_response: FinalResponsePayload) -> FinalResponsePayload:
        return final_response


__all__ = ["EndNode"]
