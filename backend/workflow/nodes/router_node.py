from __future__ import annotations

from backend.workflow.models import IntentClassificationResult, RouterNodeOutput


class RouterNode:
    def run(self, classification: IntentClassificationResult) -> RouterNodeOutput:
        return RouterNodeOutput(route=classification.intent)


__all__ = ["RouterNode"]
