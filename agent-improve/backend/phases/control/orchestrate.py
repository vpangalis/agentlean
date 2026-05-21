from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage

from backend.core.state import ImproveGraphState
from backend.core.llm import get_llm
from backend.core.prompts import (
    ORCHESTRATOR_SYSTEM_BASE,
    ORCHESTRATOR_CONTEXT_MAP,
    EXTRACTION_MAP,
    REFLECTION_CHECK,
)

logger = logging.getLogger(__name__)


def orchestrate_control(state: ImproveGraphState) -> dict:
    """Orchestrator node for Control phase.
    1. Runs extraction to update phase_inputs from chat history
    2. Generates next Orchestrator response
    3. Reflects on response quality before returning
    Returns dict slice only."""

    case_meta = state.get("case_metadata") or {}
    department = case_meta.get("department", "your department")
    title = case_meta.get("title", "this project")
    current_user = state.get("current_user", "the team")
    chat_history = state.get("chat_history") or []
    phase_inputs = state.get("phase_inputs") or {}

    # ââ 1. Extract structured fields from conversation ââââââââââââââ
    extraction_prompt = EXTRACTION_MAP["control"]
    conversation_text = _format_conversation(chat_history)
    extracted = _run_extraction(extraction_prompt, conversation_text)

    # Merge extracted values into phase_inputs (null values do not overwrite)
    control_inputs = phase_inputs.get("control") or {}
    for key, value in extracted.items():
        if value is not None and value != [] and value != "":
            control_inputs[key] = value
    phase_inputs["control"] = control_inputs

    # ââ 2. Generate Orchestrator response âââââââââââââââââââââââââââ
    system_prompt = (
        ORCHESTRATOR_SYSTEM_BASE.format(department=department, title=title)
        + "\n\n"
        + ORCHESTRATOR_CONTEXT_MAP["control"]
    )
    response_text = _run_orchestrator(system_prompt, chat_history, current_user)

    # ââ 3. Reflect on response quality ââââââââââââââââââââââââââââââ
    response_text = _reflect(response_text)

    # ââ 4. Append AI turn to chat history âââââââââââââââââââââââââââ
    now = datetime.now(timezone.utc).isoformat()
    new_turn = {
        "turn": len(chat_history) + 1,
        "role": "ai",
        "user": None,
        "text": response_text,
        "timestamp": now,
        "citations": [],
    }
    updated_history = chat_history + [new_turn]

    return {
        "phase_inputs": phase_inputs,
        "chat_history": updated_history,
    }


# ââ private helpers ââââââââââââââââââââââââââââââââââââââââââââââââ


def _format_conversation(chat_history: list) -> str:
    """Format chat history as plain text for extraction prompt."""
    lines = []
    for turn in chat_history:
        role = "AI" if turn.get("role") == "ai" else turn.get("user", "Team")
        lines.append(f"{role}: {turn.get('text', '')}")
    return "\n".join(lines)


def _run_extraction(prompt_template: str, conversation: str) -> dict:
    """Run extraction LLM call. Returns partial dict, empty on failure."""
    llm = get_llm("extraction", temperature=0.0)
    prompt = prompt_template.format(conversation=conversation)
    try:
        result = llm.invoke([HumanMessage(content=prompt)])
        text = result.content.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        # Robustly find JSON object boundaries
        text = text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            text = text[start:end]
        return json.loads(text)
    except Exception as e:
        logger.warning("Extraction failed: %s", e)
        return {}


def _run_orchestrator(
    system_prompt: str,
    chat_history: list,
    current_user: str,
) -> str:
    """Run orchestrator LLM call. Returns response text."""
    llm = get_llm("reasoning", temperature=0.3)
    messages = [SystemMessage(content=system_prompt)]
    for turn in chat_history[-12:]:  # last 12 turns for context window
        role = "ai" if turn.get("role") == "ai" else "human"
        content = turn.get("text", "")
        if role == "ai":
            from langchain_core.messages import AIMessage
            messages.append(AIMessage(content=content))
        else:
            messages.append(
                HumanMessage(content=f"{turn.get('user', 'Team')}: {content}")
            )
    try:
        result = llm.invoke(messages)
        return result.content.strip()
    except Exception as e:
        logger.error("Orchestrator LLM failed: %s", e)
        return "I'm having trouble connecting. Please try again in a moment."


def _reflect(response: str) -> str:
    """Check response quality. Returns revised response if issues found.
    Private â called only from orchestrate_control."""
    llm = get_llm("reasoning", temperature=0.0)
    prompt = REFLECTION_CHECK.format(response=response)
    try:
        result = llm.invoke([HumanMessage(content=prompt)])
        text = result.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)
        if not data.get("passes") and data.get("revised_response"):
            logger.info("Reflection revised response: %s", data.get("issues"))
            return data["revised_response"]
        return response
    except Exception as e:
        logger.warning("Reflection failed, returning original: %s", e)
        return response
