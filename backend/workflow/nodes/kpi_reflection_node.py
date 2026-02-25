from __future__ import annotations

from pydantic import BaseModel

from backend.infra.llm_logging_client import LoggedLanguageModelClient
from backend.workflow.models import (
    KPIInterpretation,
    KPIMetrics,
    KPIReflectionOutput,
    ReflectionVerdict,
)


class KPIAssessment(BaseModel):
    schema_valid: bool
    completeness_score: float
    hallucination_risk: str
    should_regenerate: bool
    issues: list[str]


class KPIInterpretationDraft(BaseModel):
    summary: str
    insights: list[str]


class KPIReflectionNode:
    def __init__(
        self,
        llm_client: LoggedLanguageModelClient,
        regeneration_llm_client: LoggedLanguageModelClient,
    ) -> None:
        self._llm_client = llm_client
        self._regeneration_llm_client = regeneration_llm_client

    def run(self, question: str, metrics: KPIMetrics) -> KPIReflectionOutput:
        interpretation = self._llm_client.complete_json(
            system_prompt=(
                "You are a KPI analysis assistant for operations leadership. "
                "Respond with ONLY this JSON structure — no other keys:\n"
                "{\n"
                '  "summary": "<concise KPI summary string>",\n'
                '  "insights": ["insight 1", "insight 2"]\n'
                "}\n"
                "Do not add any other keys."
            ),
            user_prompt=f"Question: {question}\nMetrics: {metrics.model_dump()}",
            response_model=KPIInterpretationDraft,
            temperature=0.1,
            user_question=question,
        )
        assessment = self._llm_client.complete_json(
            system_prompt=(
                "You are a strict quality validator. "
                "Respond with ONLY this JSON structure — no other keys:\n"
                "{\n"
                '  "schema_valid": true,\n'
                '  "completeness_score": 0.85,\n'
                '  "hallucination_risk": "LOW",\n'
                '  "should_regenerate": false,\n'
                '  "issues": []\n'
                "}\n"
                "Rules: schema_valid=true if summary and insights are present; "
                "completeness_score=0.0-1.0; "
                "hallucination_risk=LOW|MEDIUM|HIGH; "
                "should_regenerate=true only if score<0.5 or schema_valid=false; "
                "issues=list of strings."
            ),
            user_prompt=(
                f"Question: {question}\n"
                f"Metrics: {metrics.model_dump()}\n"
                f"Interpretation summary: {interpretation.summary}"
            ),
            response_model=KPIAssessment,
            temperature=0.0,
            user_question=question,
        )

        verdict = ReflectionVerdict.model_validate(
            {
                "schema_valid": assessment.schema_valid,
                "completeness_score": assessment.completeness_score,
                "hallucination_risk": str(assessment.hallucination_risk).upper(),
                "should_regenerate": assessment.should_regenerate,
                "issues": assessment.issues,
            }
        )

        final_interpretation = interpretation
        if verdict.should_regenerate:
            final_interpretation = self._regeneration_llm_client.complete_json(
                system_prompt=(
                    "You are a KPI analysis assistant. "
                    "Respond with ONLY this JSON structure — no other keys:\n"
                    "{\n"
                    '  "summary": "<concise KPI summary string>",\n'
                    '  "insights": ["insight 1", "insight 2"]\n'
                    "}\n"
                    "Do not add any other keys."
                ),
                user_prompt=(
                    f"Question: {question}\n"
                    f"Metrics: {metrics.model_dump()}\n"
                    f"Issues to address: {verdict.issues}"
                ),
                response_model=KPIInterpretationDraft,
                temperature=0.1,
                user_question=question,
            )

        return KPIReflectionOutput(
            kpi_interpretation=KPIInterpretation(
                summary=final_interpretation.summary,
                insights=final_interpretation.insights,
                metrics=metrics,
            ),
            kpi_reflection=verdict,
        )


__all__ = ["KPIReflectionNode"]
