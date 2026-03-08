from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.state import IncidentGraphState
from backend.workflow.models import (
    FinalResponsePayload,
    IntentClassificationResult,
    KPIInterpretation,
    OperationalPayload,
    ResponseFormatterOutput,
    SimilarityPayload,
    StrategyPayload,
)


def response_formatter_node(state: IncidentGraphState) -> dict:
    """Format the final response payload from the appropriate reasoning result."""
    classification = state.get("classification")
    result_payload: dict[str, Any] = {}

    if isinstance(classification, dict):
        intent = classification.get("intent")
        if intent == "OPERATIONAL_CASE":
            result_payload = state.get("operational_result") or {}
        elif intent == "SIMILARITY_SEARCH":
            result_payload = state.get("similarity_result") or {}
        elif intent == "STRATEGY_ANALYSIS":
            result_payload = state.get("strategy_result") or {}
        elif intent == "KPI_ANALYSIS":
            result_payload = state.get("kpi_interpretation") or {}

    return {
        "final_response": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "classification": classification,
            "result": result_payload,
        },
        "_last_node": "response_formatter_node",
    }


# DEPRECATED: replaced by response_formatter_node() function above — remove in Phase 8
class ResponseFormatterNode:
    def run(
        self,
        classification: IntentClassificationResult | None,
        operational_result: OperationalPayload | None,
        similarity_result: SimilarityPayload | None,
        strategy_result: StrategyPayload | None,
        kpi_interpretation: KPIInterpretation | None,
    ) -> ResponseFormatterOutput:
        result_payload: dict[str, Any] = {}
        if classification is not None:
            if (
                classification.intent == "OPERATIONAL_CASE"
                and operational_result is not None
            ):
                result_payload = operational_result.model_dump()
            elif (
                classification.intent == "SIMILARITY_SEARCH"
                and similarity_result is not None
            ):
                result_payload = similarity_result.model_dump()
            elif (
                classification.intent == "STRATEGY_ANALYSIS"
                and strategy_result is not None
            ):
                result_payload = strategy_result.model_dump()
            elif (
                classification.intent == "KPI_ANALYSIS"
                and kpi_interpretation is not None
            ):
                result_payload = kpi_interpretation.model_dump()

        return ResponseFormatterOutput(
            final_response=FinalResponsePayload(
                timestamp=datetime.now(timezone.utc).isoformat(),
                classification=classification,
                result=result_payload,
            )
        )


__all__ = ["ResponseFormatterNode"]
