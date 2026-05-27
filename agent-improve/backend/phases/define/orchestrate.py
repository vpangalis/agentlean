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
    SIPOC_DRAFT_PROMPT,
)
from backend.knowledge.retriever import search_evidence

logger = logging.getLogger(__name__)


def orchestrate_define(state: ImproveGraphState) -> dict:
    """Orchestrator node for Define phase.
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

    # Ã¢ÂÂÃ¢ÂÂ 1. Extract structured fields from conversation Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    extraction_prompt = EXTRACTION_MAP["define"]
    conversation_text = _format_conversation(chat_history)
    extracted = _run_extraction(extraction_prompt, conversation_text)

    # Merge extracted values into phase_inputs (null values do not overwrite)
    define_inputs = phase_inputs.get("define") or {}
    for key, value in extracted.items():
        if value is not None and value != [] and value != "":
            define_inputs[key] = value
    phase_inputs["define"] = define_inputs

    # Ã¢ÂÂÃ¢ÂÂ 2. Generate Orchestrator response Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    system_prompt = (
        ORCHESTRATOR_SYSTEM_BASE.format(department=department, title=title)
        + "\n\n"
        + ORCHESTRATOR_CONTEXT_MAP["define"]
    )
    response_text = _run_orchestrator(system_prompt, chat_history, current_user)

    # Ã¢ÂÂÃ¢ÂÂ 3. Reflect on response quality Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    response_text = _reflect(response_text)

    # Ã¢ÂÂÃ¢ÂÂ 4. Append AI turn to chat history Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
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

    # ── 5. Determine if sipoc_diagram should be included ──────────────
    sipoc_diagram = None
    current_define = phase_inputs.get("define") or {}
    sipoc_already_captured = bool(current_define.get("sipoc"))

    if (
        _problem_statement_complete(current_define)
        and not sipoc_already_captured
    ):
        case_id = state.get("case_id") or ""
        sipoc_diagram = _generate_sipoc_draft(
            current_define, case_meta, case_id=case_id
        )

    elif sipoc_already_captured:
        # Return confirmed SIPOC (draft=False) so UI can display it
        sipoc_diagram = {**current_define["sipoc"], "draft": False}

    return {
        "phase_inputs": phase_inputs,
        "chat_history": updated_history,
        "sipoc_diagram": sipoc_diagram,   # None when not applicable
    }


# Ã¢ÂÂÃ¢ÂÂ private helpers Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ


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
    prompt = prompt_template.replace("{conversation}", conversation)
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
    Private Ã¢ÂÂ called only from orchestrate_define."""
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


def _generate_sipoc_draft(
    define_inputs: dict,
    case_meta: dict,
    case_id: str = "",
) -> dict | None:
    """Generate a SIPOC draft.
    Priority:
      1. If uploaded evidence contains SIPOC columns -> use those
         (draft=True, source='upload')
      2. Otherwise -> generate from problem fields via LLM
         (draft=True, source='generated')
    Returns dict with five SIPOC keys + draft:True + source, or None.
    """
    required = ["what", "where", "who_affected"]
    if not all(define_inputs.get(k) for k in required):
        return None

    # -- Priority 1: search uploaded evidence for SIPOC content -----------
    if case_id:
        try:
            evidence_results = search_evidence(
                "SIPOC suppliers inputs process steps outputs customers",
                case_id=case_id,
                k=3,
            )
            for result in evidence_results:
                content = result.get("content", "")
                sipoc_from_upload = _extract_sipoc_from_text(content)
                if sipoc_from_upload:
                    sipoc_from_upload["draft"] = True
                    sipoc_from_upload["source"] = "upload"
                    logger.info(
                        "SIPOC draft built from uploaded evidence for %s",
                        case_id,
                    )
                    return sipoc_from_upload
        except Exception as e:
            logger.warning("Evidence SIPOC search failed: %s", e)

    # -- Priority 2: generate from problem fields -------------------------
    prompt = SIPOC_DRAFT_PROMPT.format(
        what=define_inputs.get("what", ""),
        where=define_inputs.get("where", ""),
        who_affected=define_inputs.get("who_affected", ""),
        process_owner=define_inputs.get("process_owner", "the process owner"),
        department=case_meta.get("department", "the department"),
    )
    llm = get_llm("extraction", temperature=0.3)
    try:
        result = llm.invoke([HumanMessage(content=prompt)])
        text = result.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            required_keys = {
                "suppliers", "inputs", "process_steps",
                "outputs", "customers",
            }
            if required_keys.issubset(data.keys()):
                data["draft"] = True
                data["source"] = "generated"
                return data
    except Exception as e:
        logger.warning("SIPOC draft generation failed: %s", e)
    return None


def _extract_sipoc_from_text(text: str) -> dict | None:
    """Attempt to extract SIPOC columns from free text using LLM.
    Returns dict with five SIPOC keys or None if extraction fails."""
    if not text or len(text.strip()) < 20:
        return None
    llm = get_llm("extraction", temperature=0.0)
    prompt = f"""Extract SIPOC columns from the following text.
Return ONLY a JSON object with exactly these five keys:
{{
  "suppliers": [],
  "inputs": [],
  "process_steps": [],
  "outputs": [],
  "customers": []
}}
Each value is a list of short strings (5 words max per item).
If a column cannot be determined from the text, return an empty list for it.
If the text does not describe a process at all, return null.

Text:
{text[:2000]}

Return JSON only. No explanation.
"""
    try:
        result = llm.invoke([HumanMessage(content=prompt)])
        raw = result.content.strip()
        if raw.strip().lower() == "null":
            return None
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(raw[start:end])
            required = {"suppliers", "inputs", "process_steps",
                        "outputs", "customers"}
            if required.issubset(data.keys()):
                # Only return if at least one column has content
                if any(data[k] for k in required):
                    return data
    except Exception as e:
        logger.warning("_extract_sipoc_from_text failed: %s", e)
    return None


def _problem_statement_complete(define_inputs: dict) -> bool:
    """Returns True when all 7 problem statement fields are captured."""
    required = [
        "what", "where", "when", "who_affected",
        "why_it_matters", "how_much_baseline", "how_goal"
    ]
    return all(
        define_inputs.get(k) for k in required
    )
