from __future__ import annotations

import json
import logging

from backend.state import IncidentGraphState
from backend.llm import get_llm
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from backend.workflow.models import (
    ReflectionResult,
    StrategyPayload,
    StrategyReflectionAssessment,
    StrategyReflectionOutput,
)
from backend.prompts import STRATEGY_REFLECTION_SYSTEM_PROMPT, STRATEGY_REGENERATION_SYSTEM_PROMPT

_logger = logging.getLogger(__name__)


def strategy_reflection_node(state: IncidentGraphState) -> dict:
    """Reflect on the strategy draft with structured quality assessment."""
    draft = state.get("strategy_draft") or {}
    question = state.get("question", "")
    draft_text = draft.get("summary", "")

    # Build context from supporting data
    supporting_cases = draft.get("supporting_cases", [])
    supporting_knowledge = draft.get("supporting_knowledge", [])
    cases_summary = json.dumps(supporting_cases, indent=2, default=str)
    knowledge_summary = json.dumps(supporting_knowledge, indent=2, default=str)

    llm = get_llm("gpt-4o", 0.0)

    try:
        assessment = llm.with_structured_output(StrategyReflectionAssessment).invoke([
            SystemMessage(content=STRATEGY_REFLECTION_SYSTEM_PROMPT),
            HumanMessage(content=(
                f"question: {question}\n\n"
                f"retrieved_cases: {cases_summary}\n\n"
                f"retrieved_knowledge: {knowledge_summary}\n\n"
                f"draft_response:\n{draft_text}"
            )),
        ])
        _logger.info("STRATEGY_REFLECTION: %s", assessment.model_dump())

        overall_pass = assessment.overall.upper() == "PASS"
        score = _score(assessment)

        fail_section = (
            "" if assessment.fail_section.upper() == "NONE" else assessment.fail_section
        )
        fail_reason = (
            "" if assessment.fail_reason.upper() == "NONE" else assessment.fail_reason
        )

        return {
            "strategy_result": {
                "summary": draft_text,
                "strategic_recommendations": [],
                "supporting_cases": supporting_cases,
                "supporting_knowledge": supporting_knowledge,
                "suggestions": list(draft.get("suggestions", [])),
            },
            "strategy_reflection": {
                "quality_score": score,
                "needs_escalation": not overall_pass,
                "reasoning_feedback": (
                    f"{fail_section}: {fail_reason}"
                    if fail_section
                    else "Strategy draft accepted."
                ),
            },
            "strategy_fail_section": fail_section,
            "strategy_fail_reason": fail_reason,
            "_last_node": "strategy_reflection_node",
        }

    except Exception as exc:
        _logger.exception("strategy_reflection_node failed: %s", exc)
        return {
            "strategy_result": draft,
            "_last_node": "strategy_reflection_node",
        }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _score(assessment: StrategyReflectionAssessment) -> float:
    overall_pass = assessment.overall.upper() == "PASS"
    if overall_pass:
        return 1.0
    return (
        sum(
            1.0
            for v in [
                assessment.portfolio_breadth,
                assessment.pattern_specificity,
                assessment.weakness_strength,
                assessment.knowledge_grounding,
                assessment.explore_next_quality,
            ]
            if v.upper() == "PASS"
        )
        / 5.0
    )


# DEPRECATED: replaced by strategy_reflection_node() function above — remove in Phase 8
class StrategyReflectionNode:
    _REFLECTION_SYSTEM_PROMPT = STRATEGY_REFLECTION_SYSTEM_PROMPT
    _REGENERATION_SYSTEM_PROMPT = STRATEGY_REGENERATION_SYSTEM_PROMPT

    def __init__(
        self,
        llm_client: AzureChatOpenAI,
        regeneration_llm_client: AzureChatOpenAI,
    ) -> None:
        self._llm_client = llm_client
        self._assessment_model = StrategyReflectionAssessment
        self._reflection_prompt = self._REFLECTION_SYSTEM_PROMPT
        self._current_draft: StrategyPayload | None = None

    def _score(self, assessment: StrategyReflectionAssessment) -> float:
        overall_pass = assessment.overall.upper() == "PASS"
        if overall_pass:
            return 1.0
        return (
            sum(
                1.0 for v in [
                    assessment.portfolio_breadth, assessment.pattern_specificity,
                    assessment.weakness_strength, assessment.knowledge_grounding,
                    assessment.explore_next_quality,
                ] if v.upper() == "PASS"
            ) / 5.0
        )

    def _build_output(self, draft_text: str, assessment: StrategyReflectionAssessment) -> dict:
        draft = self._current_draft
        overall_pass = assessment.overall.upper() == "PASS"
        fail_section = "" if assessment.fail_section.upper() == "NONE" else assessment.fail_section
        fail_reason = "" if assessment.fail_reason.upper() == "NONE" else assessment.fail_reason
        return StrategyReflectionOutput(
            strategy_result=StrategyPayload(
                summary=draft_text, strategic_recommendations=[],
                supporting_cases=draft.supporting_cases,
                supporting_knowledge=draft.supporting_knowledge,
                suggestions=list(draft.suggestions),
            ),
            strategy_reflection=ReflectionResult(
                quality_score=self._score(assessment),
                needs_escalation=not overall_pass,
                reasoning_feedback=(
                    f"{fail_section}: {fail_reason}" if fail_section else "Strategy draft accepted."
                ),
            ),
            strategy_fail_section=fail_section,
            strategy_fail_reason=fail_reason,
        ).model_dump()

    def run(self, question: str, draft: StrategyPayload) -> StrategyReflectionOutput:
        cases_summary = json.dumps(
            [c.model_dump(mode="json") for c in draft.supporting_cases], indent=2, default=str,
        )
        knowledge_summary = json.dumps(
            [k.model_dump(mode="json") for k in draft.supporting_knowledge], indent=2, default=str,
        )
        self._current_draft = draft
        try:
            assessment = self._llm_client.with_structured_output(self._assessment_model).invoke([
                SystemMessage(content=self._reflection_prompt),
                HumanMessage(content=(
                    f"question: {question}\n\nretrieved_cases: {cases_summary}\n\n"
                    f"retrieved_knowledge: {knowledge_summary}\n\ndraft_response:\n{draft.summary}"
                )),
            ])
            _logger.info("STRATEGY_REFLECTION: %s", assessment.model_dump())
            result_dict = self._build_output(draft.summary, assessment)
            return StrategyReflectionOutput.model_validate(result_dict)
        finally:
            self._current_draft = None


__all__ = ["StrategyReflectionNode"]
