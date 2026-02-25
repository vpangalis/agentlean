from __future__ import annotations

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


class IntentReflectionNode:
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
            validated_classification = self._regeneration_llm_client.complete_json(
                system_prompt=(
                    "You classify industrial decision-support user requests. "
                    "Return strict JSON only."
                ),
                user_prompt=(
                    "Classify and return JSON with intent/scope/confidence.\n"
                    f"question: {question}\n"
                    f"case_id: {case_id}\n"
                    f"known_issues: {verdict.issues}"
                ),
                response_model=IntentClassificationResult,
                temperature=0.0,
                user_question=question,
            )

        return IntentReflectionOutput(
            classification=validated_classification,
            intent_reflection=verdict,
        )


__all__ = ["IntentReflectionNode"]
