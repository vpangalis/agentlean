from __future__ import annotations

import re

from pydantic import BaseModel

from backend.infra.llm_logging_client import LoggedLanguageModelClient
from backend.workflow.models import (
    IntentClassificationResult,
    IntentReflectionOutput,
    ReflectionVerdict,
)


class IntentReflectionAssessment(BaseModel):
    schema_valid: bool
    completeness_score: float
    hallucination_risk: str
    should_regenerate: bool
    issues: list[str]


class _RawClassification(BaseModel):
    """Lenient parse model — accepts any string for intent/scope so enum
    validation never raises before our coercion step."""

    intent: str = "SIMILARITY_SEARCH"
    scope: str = "GLOBAL"
    confidence: float = 0.5

    model_config = {"extra": "ignore"}


_VALID_INTENTS: frozenset[str] = frozenset(
    {"OPERATIONAL_CASE", "SIMILARITY_SEARCH", "STRATEGY_ANALYSIS", "KPI_ANALYSIS"}
)
_VALID_SCOPES: frozenset[str] = frozenset({"LOCAL", "COUNTRY", "GLOBAL"})

# Ordered keyword → canonical-value mapping (first match wins).
_INTENT_KEYWORDS: list[tuple[str, str]] = [
    ("KPI", "KPI_ANALYSIS"),
    ("METRIC", "KPI_ANALYSIS"),
    ("COUNT", "KPI_ANALYSIS"),
    ("PERFORM", "KPI_ANALYSIS"),
    ("OPERATIONAL", "OPERATIONAL_CASE"),
    ("SIMILAR", "SIMILARITY_SEARCH"),
    ("SEARCH", "SIMILARITY_SEARCH"),
    ("STRATEGY", "STRATEGY_ANALYSIS"),
    ("STRATEGIC", "STRATEGY_ANALYSIS"),
    ("PORTFOLIO", "STRATEGY_ANALYSIS"),
    ("ANALYSIS", "STRATEGY_ANALYSIS"),
]
_SCOPE_KEYWORDS: list[tuple[str, str]] = [
    ("LOCAL", "LOCAL"),
    ("SITE", "LOCAL"),
    ("COUNTRY", "COUNTRY"),
    ("GLOBAL", "GLOBAL"),
]


class IntentReflectionNode:
    # ------------------------------------------------------------------
    # Coercion helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _coerce_intent(raw: str) -> str:
        """Map any LLM-returned intent string to a valid enum member."""
        normalised = re.sub(r"[^A-Z0-9]", "_", raw.strip().upper())
        if normalised in _VALID_INTENTS:
            return normalised
        for keyword, mapped in _INTENT_KEYWORDS:
            if keyword in normalised:
                return mapped
        return "SIMILARITY_SEARCH"

    @staticmethod
    def _coerce_scope(raw: str) -> str:
        """Map any LLM-returned scope string to a valid enum member."""
        normalised = re.sub(r"[^A-Z0-9]", "_", raw.strip().upper())
        if normalised in _VALID_SCOPES:
            return normalised
        for keyword, mapped in _SCOPE_KEYWORDS:
            if keyword in normalised:
                return mapped
        return "GLOBAL"

    @staticmethod
    def _coerce_raw(raw: _RawClassification) -> IntentClassificationResult:
        """Produce a fully-valid IntentClassificationResult from a lenient parse."""
        return IntentClassificationResult(
            intent=IntentReflectionNode._coerce_intent(raw.intent),  # type: ignore[arg-type]
            scope=IntentReflectionNode._coerce_scope(raw.scope),  # type: ignore[arg-type]
            confidence=max(0.0, min(1.0, float(raw.confidence))),
        )

    # ------------------------------------------------------------------

    def __init__(
        self,
        llm_client: LoggedLanguageModelClient,
        regeneration_llm_client: LoggedLanguageModelClient,
    ) -> None:
        self._llm_client = llm_client
        self._regeneration_llm_client = regeneration_llm_client

    def run(
        self,
        question: str,
        case_id: str | None,
        classification: IntentClassificationResult,
    ) -> IntentReflectionOutput:
        assessment = self._llm_client.complete_json(
            system_prompt=(
                "You are a strict reflection validator. Evaluate schema correctness, "
                "hallucination risk, and completeness. Return strict JSON only."
            ),
            user_prompt=(
                "Evaluate the classification and return ONLY this JSON shape:\n"
                "{\n"
                '  "schema_valid": true,\n'
                '  "completeness_score": 0.95,\n'
                '  "hallucination_risk": "LOW",\n'
                '  "should_regenerate": false,\n'
                '  "issues": []\n'
                "}\n\n"
                "Rules:\n"
                "- schema_valid: true if intent/scope/confidence fields are all present and valid\n"
                "- completeness_score: 0.0-1.0 float\n"
                "- hallucination_risk: exactly one of LOW, MEDIUM, HIGH\n"
                "- should_regenerate: true only if schema_valid is false or confidence < 0.5\n"
                "- issues: list of strings describing problems, empty list if none\n\n"
                f"question: {question}\n"
                f"case_id: {case_id}\n"
                f"classification: {classification.model_dump()}\n"
            ),
            response_model=IntentReflectionAssessment,
            temperature=0.0,
            user_question=question,
        )

        verdict = ReflectionVerdict.model_validate(
            {
                "schema_valid": bool(assessment.schema_valid),
                "completeness_score": float(assessment.completeness_score),
                "hallucination_risk": str(assessment.hallucination_risk).upper(),
                "should_regenerate": bool(assessment.should_regenerate),
                "issues": assessment.issues or [],
            }
        )

        validated_classification = classification
        if verdict.should_regenerate:
            try:
                raw = self._regeneration_llm_client.complete_json(
                    system_prompt=(
                        "You classify industrial decision-support user requests. "
                        "Return strict JSON only — no explanation, no markdown."
                    ),
                    user_prompt=(
                        "Classify the request below and return ONLY this JSON:\n"
                        "{\n"
                        '  "intent": "<value>",\n'
                        '  "scope": "<value>",\n'
                        '  "confidence": 0.0\n'
                        "}\n\n"
                        "intent MUST be exactly one of these four values (no variations):\n"
                        "  OPERATIONAL_CASE, SIMILARITY_SEARCH, STRATEGY_ANALYSIS, KPI_ANALYSIS\n\n"
                        "scope MUST be exactly one of these three values (no variations):\n"
                        "  LOCAL, COUNTRY, GLOBAL\n\n"
                        f"question: {question}\n"
                        f"case_id: {case_id}\n"
                        f"known_issues: {verdict.issues}"
                    ),
                    response_model=_RawClassification,
                    temperature=0.0,
                    user_question=question,
                )
                validated_classification = IntentReflectionNode._coerce_raw(raw)
            except Exception:  # noqa: BLE001
                pass  # keep the original first-pass classification

        return IntentReflectionOutput(
            classification=validated_classification,
            intent_reflection=verdict,
        )


__all__ = ["IntentReflectionNode"]
