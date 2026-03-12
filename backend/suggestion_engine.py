from __future__ import annotations

import logging
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel


class SuggestionItem(BaseModel):
    label: str
    question: str


class SuggestionsLLMResponse(BaseModel):
    suggestions: list[SuggestionItem] = []

_logger = logging.getLogger(__name__)

_SUGGESTIONS_SYSTEM = (
    "You are generating suggested questions for a problem-solving "
    "assistant UI. Given a case summary, generate exactly 6 suggested "
    "questions a user might want to ask.\n\n"
    "Return ONLY this JSON:\n"
    "{\n"
    '  "suggestions": [\n'
    '    { "label": "short 2-4 word label", "question": "full question text" },\n'
    "    ...6 items...\n"
    "  ]\n"
    "}\n\n"
    "Rules:\n"
    "- 2 suggestions must be operational (current state / gaps / next steps)\n"
    "- 2 suggestions must be similarity-focused (find similar cases)\n"
    "- 1 suggestion must be strategic (systemic risks or patterns)\n"
    "- 1 suggestion must be KPI-focused (trends or metrics)\n"
    "- Every question must reference the actual problem, component, "
    "or system from the case — no generic questions\n"
    "- Labels must be short: 'Root cause gaps', 'Similar faults', "
    "'Fleet trends', etc.\n"
    "- Questions must be natural language, as a user would type them\n"
    "- NEVER use D-step codes (D1, D2, D3, D4, D5, D6, D7, D8) in labels "
    "or question text — use plain language only. "
    "Instead of 'Next steps for D8' use 'What should we do to close this case?'; "
    "instead of 'D4 root cause' use 'What is the root cause?'; "
    "instead of 'D3 containment' use 'What containment actions are in place?'"
)

_FALLBACK_SUGGESTIONS: list[dict[str, str]] = [
    {
        "label": "Current gaps",
        "question": "What are the current gaps in our investigation?",
    },
    {"label": "Next steps", "question": "What should the team focus on next?"},
    {
        "label": "Similar faults",
        "question": "Are there similar cases in the closed case knowledge base?",
    },
    {
        "label": "Past incidents",
        "question": "Have we seen this type of failure before?",
    },
    {
        "label": "Systemic risks",
        "question": "Are there systemic risks highlighted by recurring incidents?",
    },
    {
        "label": "KPI trends",
        "question": "How are we trending on key reliability metrics?",
    },
]

_D_STATE_FRIENDLY: dict[str, str] = {
    "D1_2": "Problem Definition",
    "D3": "Containment Actions",
    "D4": "Root Cause Analysis",
    "D5": "Permanent Corrective Actions",
    "D6": "Implementation & Validation",
    "D7": "Prevention",
    "D8": "Closure & Learnings",
}

_DSTEP_RE = re.compile(r"\bD[1-8]\b", re.IGNORECASE)


def generate_suggestions(
    case_id: str,
    case_context: dict[str, Any],
    llm_client: AzureChatOpenAI | None,
) -> list[dict[str, str]]:
    """Generate 6 AI-suggested questions for the given case context."""
    if llm_client is None:
        return list(_FALLBACK_SUGGESTIONS)

    try:
        problem_description = extract_problem_description(case_context)
        raw_d_state = extract_current_d_state(case_context) or "D1_2"
        current_step_label = _D_STATE_FRIENDLY.get(raw_d_state, "Problem Definition")
        status = str(case_context.get("case_status") or "open")

        user_prompt = (
            f"Case ID: {case_id}\n"
            f"Problem: {problem_description}\n"
            f"Current investigation step: {current_step_label}\n"
            f"Status: {status}"
        )

        result: SuggestionsLLMResponse = llm_client.with_structured_output(
            SuggestionsLLMResponse
        ).invoke([
            SystemMessage(content=_SUGGESTIONS_SYSTEM),
            HumanMessage(content=user_prompt),
        ])
        suggestions = [
            {
                "label": _DSTEP_RE.sub("", s.label).strip(" -:"),
                "question": _DSTEP_RE.sub("", s.question).strip(),
            }
            for s in result.suggestions
        ]
        if len(suggestions) == 0:
            return list(_FALLBACK_SUGGESTIONS)
        return suggestions
    except Exception as exc:
        _logger.warning(
            "[SUGGESTIONS] LLM call failed, returning fallback: %s", exc
        )
        return list(_FALLBACK_SUGGESTIONS)


def extract_problem_description(case_context: dict[str, Any]) -> str:
    """Extract problem description from case context (supports multiple formats)."""
    # Try d_states.D1_2 (native format)
    d_states = case_context.get("d_states")
    if isinstance(d_states, dict):
        block = d_states.get("D1_2")
        if isinstance(block, dict):
            data = block.get("data") or {}
            desc = (
                data.get("problem_description")
                or data.get("description")
                or block.get("problem_description")
            )
            if desc:
                return str(desc)[:500]
    # Try phases.D1_D2 (legacy format)
    phases = case_context.get("phases")
    if isinstance(phases, dict):
        block = phases.get("D1_D2") or phases.get("D1_2")
        if isinstance(block, dict):
            data = block.get("data") or {}
            desc = (
                data.get("problem_description")
                or data.get("description")
                or block.get("problem_description")
            )
            if desc:
                return str(desc)[:500]
    # Fallback: top-level field
    return str(case_context.get("problem_description") or "(no description)")[:500]


def extract_current_d_state(case_context: dict[str, Any]) -> str | None:
    """Determine the current D-state from case context."""
    reasoning_state = case_context.get("reasoning_state")
    if not isinstance(reasoning_state, dict):
        reasoning_state = case_context.get("d_states")
    if not isinstance(reasoning_state, dict):
        phases = case_context.get("phases")
        if isinstance(phases, dict) and phases:
            reasoning_state = {
                ("D1_2" if k == "D1_D2" else k): v for k, v in phases.items()
            }
    if not isinstance(reasoning_state, dict):
        return None
    progression = ["D8", "D7", "D6", "D5", "D4", "D3", "D1_2"]
    for key in progression:
        block = reasoning_state.get(key)
        if not isinstance(block, dict):
            continue
        header = block.get("header")
        if isinstance(header, dict) and header.get("completed"):
            return key
        status = str(block.get("status") or "").lower()
        has_data = isinstance(block.get("data"), dict) and bool(block.get("data"))
        if status in {"in_progress", "completed"} or has_data:
            return key
    return "D1_2"
