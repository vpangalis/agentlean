from __future__ import annotations

import logging

from backend.core.state import IncidentGraphState
from backend.core.llm import get_llm
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from backend.reasoning.nodes.node_parsing_utils import extract_suggestions
from backend.core.prompts import (
    OPERATIONAL_REFLECTION_SYSTEM_PROMPT,
    OPERATIONAL_REGENERATION_SYSTEM_PROMPT,
)
from backend.reasoning.models import OperationalReflectionAssessment

_logger = logging.getLogger(__name__)
_REGENERATION_THRESHOLD: float = 0.65


def operational_reflection_node(state: IncidentGraphState) -> dict:
    """Critically assess quality of the operational draft."""
    draft = state.get("operational_draft") or {}
    question = state.get("question", "")
    draft_text = draft.get("current_state_recommendations", "")
    current_state = draft.get("current_state", "")

    llm = get_llm("reasoning", 0.0)
    regen_llm = get_llm("reasoning", 0.2)

    try:
        assessment = llm.with_structured_output(OperationalReflectionAssessment).invoke([
            SystemMessage(content=OPERATIONAL_REFLECTION_SYSTEM_PROMPT),
            HumanMessage(content=f"question: {question}\n\ndraft_response:\n{draft_text}"),
        ])

        score = _score(assessment)
        final_draft = draft_text

        if score < _REGENERATION_THRESHOLD:
            _logger.info(
                "operational_reflection_node: score %.3f below threshold %.3f \u2014 triggering regeneration.",
                score, _REGENERATION_THRESHOLD,
            )
            final_draft = regen_llm.invoke([
                SystemMessage(content=OPERATIONAL_REGENERATION_SYSTEM_PROMPT),
                HumanMessage(content=f"Question: {question}"),
            ]).content

        needs_escalation = (
            assessment.case_grounding == "GENERIC"
            or assessment.gap_detection == "MISSING"
            or assessment.next_state_relevance in ("DISCONNECTED", "MISSING")
            or assessment.general_advice_flagged == "MISSING"
            or assessment.explore_next_quality in ("MISSING", "INCOMPLETE")
        )
        regenerated = final_draft != draft_text

        return {
            "operational_result": {
                "current_state": current_state,
                "current_state_recommendations": final_draft,
                "next_state_preview": "" if regenerated else draft.get("next_state_preview", ""),
                "supporting_cases": draft.get("supporting_cases", []),
                "referenced_evidence": draft.get("referenced_evidence", []),
                "suggestions": extract_suggestions(final_draft),
            },
            "operational_reflection": {
                "quality_score": score,
                "needs_escalation": needs_escalation,
                "reasoning_feedback": (
                    "; ".join(assessment.issues)
                    if assessment.issues
                    else "Operational draft accepted."
                ),
            },
            "_last_node": "operational_reflection_node",
        }

    except Exception as exc:
        _logger.exception("operational_reflection_node failed: %s", exc)
        return {
            "operational_result": draft,
            "_last_node": "operational_reflection_node",
        }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _score(assessment: OperationalReflectionAssessment) -> float:
    g = {"GROUNDED": 1.0, "MIXED": 0.6, "GENERIC": 0.0}.get(assessment.case_grounding, 0.5)
    d = {"SPECIFIC": 1.0, "VAGUE": 0.5, "MISSING": 0.0}.get(assessment.gap_detection, 0.5)
    n = {"CONNECTED": 1.0, "DISCONNECTED": 0.3, "MISSING": 0.0}.get(assessment.next_state_relevance, 0.5)
    a = {"PRESENT_FLAGGED": 1.0, "PRESENT_UNFLAGGED": 0.6, "MISSING": 0.0}.get(assessment.general_advice_flagged, 0.5)
    e = {"SPECIFIC_MULTI_DOMAIN": 1.0, "GENERIC": 0.5, "INCOMPLETE": 0.3, "MISSING": 0.0}.get(
        assessment.explore_next_quality, 0.5
    )
    return max(0.0, min(1.0, (g + d + n + a + e) / 5.0))


