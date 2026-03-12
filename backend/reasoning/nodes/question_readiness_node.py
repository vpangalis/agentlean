from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from backend.core.state import IncidentGraphState
from backend.core.llm import get_llm
from backend.core.models import QuestionReadinessResult
from backend.core.prompts import QUESTION_READINESS_SYSTEM_PROMPT, QUESTION_READINESS_USER_PROMPT_TEMPLATE

_logger = logging.getLogger(__name__)

_ALWAYS_READY_INTENTS: frozenset[str] = frozenset(
    {"KPI_ANALYSIS", "STRATEGY_ANALYSIS"}
)


def question_readiness_node(state: IncidentGraphState) -> dict:
    """Check whether the user's question is specific enough to answer."""
    question = (state.get("question") or "").strip()
    classification = state.get("classification") or {}
    intent = classification.get("intent", "") if isinstance(classification, dict) else ""
    case_loaded = bool(state.get("case_id") and str(state.get("case_id")).strip())

    # Deterministic fast path
    if case_loaded or intent in _ALWAYS_READY_INTENTS:
        return {
            "question_ready": True,
            "clarifying_question": "",
            "_last_node": "question_readiness_node",
        }

    # LLM path
    llm = get_llm("intent", 0.0)
    user_prompt = QUESTION_READINESS_USER_PROMPT_TEMPLATE.format(
        case_loaded="false",
        intent=intent,
        question=question,
    )
    try:
        result = llm.with_structured_output(QuestionReadinessResult).invoke([
            SystemMessage(content=QUESTION_READINESS_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        return {
            "question_ready": result.ready,
            "clarifying_question": result.clarifying_question or "",
            "_last_node": "question_readiness_node",
        }
    except Exception:  # noqa: BLE001
        _logger.warning(
            "question_readiness_node: LLM call failed — defaulting to ready=True"
        )
        return {
            "question_ready": True,
            "clarifying_question": "",
            "_last_node": "question_readiness_node",
        }


