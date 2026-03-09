from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException

from backend.api.schemas import CoSolveRequest, CoSolveResponse, Source, SuggestedQuestions
from backend.graph import compiled_graph
from backend.state import IncidentGraphState

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ask", response_model=CoSolveResponse)
def ask(request: CoSolveRequest) -> CoSolveResponse:
    """Accept CoSolveRequest, run graph, return CoSolveResponse."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=422, detail="question must be non-empty")
    state: IncidentGraphState = {
        "question": request.question,
        "case_id": request.case_id,
        "session_id": request.session_id,
    }
    try:
        result = compiled_graph.invoke(state)
    except Exception as exc:
        logger.exception("[ASK] graph invocation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return _build_response(result)


def _build_response(state: IncidentGraphState) -> CoSolveResponse:
    """Translate graph result state → CoSolveResponse envelope."""
    final = state.get("final_response") or {}
    classification = final.get("classification") or {}
    result = final.get("result") or {}
    intent = str(classification.get("intent") or state.get("route") or "")

    if intent == "OPERATIONAL_CASE":
        answer = str(result.get("current_state_recommendations", ""))
    elif intent == "KPI_ANALYSIS":
        summary = str(result.get("summary", ""))
        insights = result.get("insights") or []
        if insights:
            bullets = "\n".join(f"• {i}" for i in insights)
            answer = f"{summary}\n\n{bullets}" if summary else bullets
        else:
            answer = summary
    else:
        answer = str(result.get("summary", ""))

    sources: list[Source] = []
    for s in result.get("supporting_cases", []):
        if isinstance(s, dict) and s.get("case_id"):
            sources.append(Source(
                case_id=s["case_id"],
                title=s.get("problem_description") or s.get("title") or "",
                relevance=s.get("@search.score"),
            ))

    raw_suggestions = result.get("suggestions") or []
    ask_team: list[str] = []
    ask_cosolve: list[str] = []

    if intent == "KPI_ANALYSIS":
        # KPI suggestions are plain strings — all go to ask_cosolve chips
        for sg in raw_suggestions:
            if isinstance(sg, str) and sg.strip():
                ask_cosolve.append(sg.strip())
    else:
        for sg in raw_suggestions:
            if isinstance(sg, dict):
                q = sg.get("question", "")
                if not q:
                    continue
                if sg.get("type") == "team":
                    ask_team.append(q)
                else:
                    ask_cosolve.append(q)

    suggested_questions = (
        SuggestedQuestions(ask_your_team=ask_team, ask_cosolve=ask_cosolve)
        if (ask_team or ask_cosolve) else None
    )

    return CoSolveResponse(
        answer=answer,
        intent=intent,
        sources=sources,
        suggested_questions=suggested_questions,
    )


__all__ = ["router"]
