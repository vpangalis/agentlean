from __future__ import annotations

import logging
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage

from backend.core.state import ImproveGraphState
from backend.core.llm import get_llm
from backend.core.prompts import ESCALATION_REPORT
from backend.core.config import settings

logger = logging.getLogger(__name__)


def escalate(state: ImproveGraphState) -> dict:
    """Cross-phase escalation node.
    Generates a plain language escalation report and sets escalated=True.
    Returns dict slice only."""

    phase = state.get("current_phase", "unknown")
    attempts = state.get("gate_attempts", 0)
    phase_inputs = state.get("phase_inputs") or {}
    phase_data = phase_inputs.get(phase) or {}
    missing = phase_data.get("_missing_fields", [])

    # Build last submission summary from phase_inputs
    last_submission = {
        k: v
        for k, v in phase_data.items()
        if not k.startswith("_") and v is not None
    }

    # Generate plain language escalation message
    report = _generate_report(phase, attempts, missing, str(last_submission))

    # Append escalation turn to chat history
    now = datetime.now(timezone.utc).isoformat()
    chat_history = state.get("chat_history") or []
    escalation_turn = {
        "turn": len(chat_history) + 1,
        "role": "ai",
        "user": None,
        "text": report,
        "timestamp": now,
        "citations": [],
        "escalated": True,
    }

    logger.warning(
        "ESCALATION fired: case=%s phase=%s attempts=%d missing=%s",
        state.get("case_id"),
        phase,
        attempts,
        missing,
    )

    return {
        "escalated": True,
        "chat_history": chat_history + [escalation_turn],
    }


def _generate_report(
    phase: str, attempts: int, missing_fields: list, last_submission: str
) -> str:
    """Generate plain language escalation report via LLM."""
    llm = get_llm("reasoning", temperature=0.2)
    prompt = ESCALATION_REPORT.format(
        phase=phase,
        attempts=attempts,
        missing_fields=missing_fields,
        last_submission=last_submission[:500],  # truncate for context
    )
    try:
        result = llm.invoke([HumanMessage(content=prompt)])
        return result.content.strip()
    except Exception as e:
        logger.error("Escalation LLM failed: %s", e)
        return (
            f"This project is stuck in the {phase} phase after {attempts} attempts. "
            f"The following information is still missing: {', '.join(missing_fields)}. "
            "Please contact your team leader to review and provide the missing details."
        )
