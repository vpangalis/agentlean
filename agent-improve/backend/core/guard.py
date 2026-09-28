"""The input guard — a node at the front of the main graph. ADR-0057 (ACCEPTED, fail closed); T71.

    START → input_guard → route_to_phase → {phase}_phase → END

Every turn that carries the Belt's text passes here before any model reads it — before the
planner's judgment, which is the first model call of a turn. Two steps:

1. Fixed rules (no service call): length, hidden or control characters, long encoded blobs, and
   known attack phrasings.
2. Azure AI Content Safety Prompt Shields, user-prompt attack (`core/content_safety.py`).

Pass → nothing is added; the turn continues. Block → one plain reply that tells the Belt what to do,
flagged `input_guard` in its `additional_kwargs`, and `route_to_phase` ends the turn. Nothing is
written to `artifacts`, `field_status` or the phase records; the verdict — passed or blocked — goes
to the Store's `step_log` namespace, `("projects", case_id, "step_log")`, never with the text.

FAIL CLOSED: Prompt Shields configured but unreachable blocks the turn with a readable message;
not configured blocks in production and, elsewhere, leaves the fixed rules standing alone (the
verdict says so).

A resume (`POST /gate/decision`, `Command(resume=…)`) never passes here — it continues the paused
node. A gate submission (`entry="gate"`) carries no Belt text and is not screened.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Optional

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore

from backend.core import content_safety
from backend.core.state import SupervisorState

logger = logging.getLogger(__name__)

NODE = "input_guard"
MAX_CHARS = 8_000
#: Known attack phrasings — each a (name, pattern), matched case-insensitively.
FIXED_RULES: tuple[tuple[str, str], ...] = (
    ("override instructions", r"\b(ignore|disregard|forget)\b.{0,40}\b(previous|prior|above|all|your)\b.{0,20}\b(instructions?|rules?|prompts?)\b"),
    ("reveal the prompt", r"\b(reveal|print|show|repeat|output)\b.{0,30}\b(system|hidden|initial)\s+(prompt|instructions?|message)\b"),
    ("role hijack", r"\byou are now (an? )?(unrestricted|jailbroken|different|new)\b|\bdeveloper mode\b|\bjailbreak"),
)
_HIDDEN = re.compile("[​-‏‪-‮⁠-⁤﻿]")
_ENCODED = re.compile(r"[A-Za-z0-9+/=]{200,}")

BLOCKED_MESSAGE = ("I can't work with that message — it looks like it is trying to change how I work "
                   "rather than tell me about your project. Please rephrase it as an answer about your "
                   "process or a question about the method, and I'll pick up where we were.")
UNAVAILABLE_MESSAGE = ("The safety check that screens every message is unavailable right now, so I have "
                       "not read this one. Nothing was saved. Please send it again in a minute.")


def fixed_rules(text: str) -> Optional[str]:
    """The first fixed rule the text breaks, or None."""
    if len(text) > MAX_CHARS:
        return "too long"
    if _HIDDEN.search(text):
        return "hidden characters"
    if _ENCODED.search(text):
        return "encoded blob"
    for name, pattern in FIXED_RULES:
        if re.search(pattern, text, re.I | re.S):
            return name
    return None


def _text(message: Any) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict))


def blocked(state: SupervisorState) -> bool:
    """Did this turn's guard block it? (Read by `route_to_phase`.)"""
    msgs = state.get("messages") or []
    last = msgs[-1] if msgs else None
    return isinstance(last, AIMessage) and \
        (last.additional_kwargs or {}).get(NODE, {}).get("status") == "blocked"


def _record(store: Optional[BaseStore], state: SupervisorState, verdict: dict[str, Any]) -> None:
    if store is None:
        return
    key = f"{NODE}:{state.get('current_phase')}:{len(state.get('messages') or [])}"
    try:
        store.put(("projects", str(state.get("case_id")), "step_log"), key, {"layer": NODE, **verdict})
    except Exception as exc:  # noqa: BLE001 — the audit write must not decide the turn
        logger.error("input_guard: the verdict could not be recorded: %s", exc)


async def input_guard(state: SupervisorState, config: Optional[RunnableConfig] = None, *,
                      store: Optional[BaseStore] = None) -> dict[str, Any]:
    entry = ((config or {}).get("configurable") or {}).get("entry", "ask")
    msgs = state.get("messages") or []
    if entry != "ask" or not msgs or not isinstance(msgs[-1], HumanMessage):
        return {}
    text = _text(msgs[-1])
    rule = fixed_rules(text)
    if rule:
        verdict = {"status": "blocked", "reason": rule, "service": "fixed rules"}
    else:
        shield = await content_safety.shield(user_prompt=text)
        if not shield["configured"]:
            verdict = ({"status": "blocked", "reason": "unavailable", "service": "not configured"}
                       if content_safety.required() else
                       {"status": "passed", "reason": "fixed rules only", "service": "not configured"})
        elif not shield["reachable"]:
            verdict = {"status": "blocked", "reason": "unavailable", "service": "unreachable",
                       "error": shield["error"]}
        elif shield["user_attack"]:
            verdict = {"status": "blocked", "reason": "prompt attack", "service": "prompt_shields"}
        else:
            verdict = {"status": "passed", "reason": "", "service": "prompt_shields"}
    _record(store, state, verdict)
    if verdict["status"] == "passed":
        return {}
    logger.warning("input_guard BLOCKED a turn on case=%s: %s (%s)",
                   state.get("case_id"), verdict["reason"], verdict["service"])
    message = UNAVAILABLE_MESSAGE if verdict["reason"] == "unavailable" else BLOCKED_MESSAGE
    return {"messages": [AIMessage(content=message, additional_kwargs={NODE: verdict})]}


__all__ = ["input_guard", "blocked", "fixed_rules", "NODE", "BLOCKED_MESSAGE", "UNAVAILABLE_MESSAGE"]
