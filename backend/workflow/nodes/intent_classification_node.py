from __future__ import annotations

from backend.infra.llm_logging_client import LoggedLanguageModelClient
from backend.workflow.models import IntentClassificationResult, IntentNodeOutput


class IntentClassificationNode:
    def __init__(self, llm_client: LoggedLanguageModelClient) -> None:
        self._llm_client = llm_client

    def run(self, question: str, case_id: str | None) -> IntentNodeOutput:
        clean_question = (question or "").strip()
        if not clean_question:
            raise ValueError("question is required")

        case_context = case_id or ""
        system_prompt = (
            "You classify industrial decision-support user requests. "
            "Return strict JSON only."
        )
        user_prompt = (
            "Classify the request and return ONLY this JSON object shape:\n"
            "{\n"
            '  "intent": "OPERATIONAL_CASE|SIMILARITY_SEARCH|STRATEGY_ANALYSIS|KPI_ANALYSIS",\n'
            '  "scope": "LOCAL|COUNTRY|GLOBAL",\n'
            '  "confidence": 0.0\n'
            "}\n"
            "Rules:\n"
            "- OPERATIONAL_CASE: asks guidance for an open/current case, next actions, D-state advice.\n"
            "- SIMILARITY_SEARCH: asks for similar historical closed cases.\n"
            "- STRATEGY_ANALYSIS: asks for cross-case patterns, systemic causes, portfolio strategy,\n"
            "  organisational weaknesses, fleet-wide recurring issues, supplier problems, or a big-picture\n"
            "  view of the incident portfolio. Examples: 'What are our most common failure categories?',\n"
            "  'Are there recurring issues across the fleet?', 'What organisational weaknesses does our\n"
            "  case history reveal?', 'Which suppliers cause the most problems?',\n"
            "  'Give me a strategic overview of our incident portfolio'.\n"
            "- KPI_ANALYSIS: asks for counts, trends, closure timing, KPI metrics.\n"
            "- scope LOCAL when local/site-level language appears.\n"
            "- scope COUNTRY when country-level language appears.\n"
            "- scope GLOBAL for cross-country/global requests.\n"
            "- confidence must be between 0 and 1.\n\n"
            f"case_id: {case_context}\n"
            f"question: {clean_question}"
        )
        classification = self._llm_client.complete_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=IntentClassificationResult,
            temperature=0.0,
            user_question=clean_question,
        )
        return IntentNodeOutput(classification=classification)


__all__ = ["IntentClassificationNode"]
