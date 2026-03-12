from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from backend.state import IncidentGraphState

_logger = logging.getLogger(__name__)

_CLARIFYING_TEXT = (
    "I'm not sure what you're looking for with that question. "
    "Here are some things I can help you with \u2014 you could ask about a specific case "
    "you have loaded, look for similar past cases, explore recurring patterns across the "
    "organisation, or check performance metrics. "
    "Try rephrasing or pick one of the suggestions below."
)

_CLARIFYING_SUGGESTIONS = [
    {
        "label": "Overall performance",
        "question": "How is our overall performance this year?",
        "type": "cosolve",
    },
    {
        "label": "Recurring problems",
        "question": "Which areas have the most recurring problems?",
        "type": "cosolve",
    },
    {
        "label": "Organisational attention",
        "question": "Which areas need organisational attention?",
        "type": "cosolve",
    },
    {
        "label": "I\u2019ll load a case and ask again",
        "question": "I\u2019ll load a case and ask again",
        "type": "load_case",
    },
]


def handle_ai_reasoning(envelope, graph: Any):
    """Invoke the LangGraph graph for an AI_REASONING request."""
    from backend.entry_handler import EntryResponseEnvelope

    _logger.debug("[DEBUG AI ENTRY] raw envelope=%r", envelope.model_dump())
    payload = envelope.payload or {}
    question = str(payload.get("question") or "").strip()
    case_id = payload.get("case_id") or envelope.case_id

    if not question:
        response = {"status": "usage", "message": "Provide a non-empty question."}
        return EntryResponseEnvelope(
            intent=envelope.intent,
            status="accepted",
            data=response,
        )

    initial_state: IncidentGraphState = {
        "case_id": str(case_id) if case_id else None,
        "question": question,
    }

    try:
        graph_result = graph.invoke(initial_state)
    except Exception as e:
        _logger.error("[ENTRY_DEBUG] exception in graph: %s", str(e), exc_info=True)
        return build_clarifying_response(envelope)

    if graph_result.get("classification_low_confidence", False):
        _logger.info(
            "[ENTRY] low-confidence classification — returning clarifying response"
        )
        return build_clarifying_response(envelope)

    if not graph_result.get("question_ready", True):
        _logger.info("[ENTRY] question not ready — returning clarifying question")
        cq = str(graph_result.get("clarifying_question") or "")
        return build_clarifying_question_response(envelope, cq)

    response = graph_result.get("final_response") or {}
    return EntryResponseEnvelope(
        intent=envelope.intent,
        status="accepted",
        data=response,
    )


def build_clarifying_response(envelope):
    """Return a generic clarifying response when classification fails."""
    from backend.entry_handler import EntryResponseEnvelope

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "classification": {
            "intent": "SIMILARITY_SEARCH",
            "scope": "GLOBAL",
            "confidence": 0.3,
        },
        "result": {
            "summary": _CLARIFYING_TEXT,
            "supporting_cases": [],
            "suggestions": list(_CLARIFYING_SUGGESTIONS),
        },
    }
    return EntryResponseEnvelope(
        intent=envelope.intent,
        status="accepted",
        data=data,
    )


def build_clarifying_question_response(envelope, clarifying_question: str):
    """Return a clarifying question when the user's question needs refinement."""
    from backend.entry_handler import EntryResponseEnvelope

    summary = clarifying_question if clarifying_question else _CLARIFYING_TEXT
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "classification": {
            "intent": "SIMILARITY_SEARCH",
            "scope": "GLOBAL",
            "confidence": 0.3,
        },
        "result": {
            "summary": summary,
            "supporting_cases": [],
            "suggestions": list(_CLARIFYING_SUGGESTIONS),
        },
    }
    return EntryResponseEnvelope(
        intent=envelope.intent,
        status="ok",
        data=data,
    )
