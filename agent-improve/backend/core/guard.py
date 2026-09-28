"""The input guard — a node at the front of the main graph. ADR-0057 (placement, fail closed),
refined by ADR-0067 (scope, replies, limits, modes); R20, T71, T93, T94.

    START → input_guard → route_to_phase → {phase}_phase → END

Every turn that carries the Belt's text passes here before any model reads it. The guard screens
for ADR-0067's threats and nothing else:

  A  rewriting the coach's rules — overriding instructions, fake system or assistant turns,
     persona role-play, encoded instructions: fixed rules, then Prompt Shields (user prompt)
  D  flooding — a message over 10,000 characters (T93; the route limits the turn rate)

Out of scope, because blocking them at the door blocks ordinary questions: other cases' data, the
system prompt, harmful content (the Azure filter, T92), personal data (T87), "write it for me".

Pass → nothing is added. Block → one reply assembled in CODE (`core/guard_messages.py`): the
threat's fixed text, the element the Belt is on and its sample. No model sees the blocked text.
`route_to_phase` ends the turn, so nothing is stored. The verdict — threat, rule, person, time,
service — goes to the Store's `("projects", case_id, "step_log")` namespace (the decision trail,
R19), passed or blocked, never with the text.

MODES (ADR-0067 point 5, T94): strict by default. Prompt Shields configured but unreachable blocks
in every mode (fail closed). Not configured blocks in strict mode; in explicit development mode
(`GUARD_MODE=development`) the fixed rules run alone and the verdict records `shield: skipped`.

A resume (`POST /gate/decision`) continues the paused node and never passes here; a gate
submission (`entry="gate"`) carries no Belt text and is not screened.
"""
from __future__ import annotations

import datetime as dt
import logging
import re
from typing import Any, Optional

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore

from backend.core import content_safety, guard_messages
from backend.core.state import SupervisorState

logger = logging.getLogger(__name__)

NODE = "input_guard"
#: T93 — the Prompt Shields input limit.
MAX_CHARS = 10_000
#: Threat A's fixed rules — each (name, pattern), matched case-insensitively. Deliberately narrow:
#: Lean language ("attack the root cause", "kill the waste", "ignore the outliers", "bypass the
#: approval step") must pass (T91; evals/define/guard_benign.jsonl).
FIXED_RULES: tuple[tuple[str, str], ...] = (
    ("override instructions", r"\b(ignore|disregard|forget)\b.{0,40}\b(previous|prior|above|earlier|all|your)\b.{0,20}\b(instructions?|prompts?)\b|\b(ignore|disregard|forget)\s+(all\s+)?your\s+(rules|guidelines|instructions)\b"),
    ("reveal the prompt", r"\b(reveal|print|show|repeat|output|leak)\b.{0,30}\b(system|hidden|initial)\s+(prompt|instructions?|message)\b"),
    ("fake system or assistant turn", r"(^|\n)\s*#{1,3}\s*(system|assistant|developer)\s*:|<\|?(im_start|im_end)\|?>|\[/?(INST|SYS)\]|<\s*/?\s*system\s*>"),
    ("persona role-play", r"\byou are now (an? )?(unrestricted|jailbroken|different|new|evil)\b|\bdeveloper mode\b|\bjailbreak|\bpretend (to be|you are)\b.{0,40}\b(ai|assistant|model|system|coach)\b"),
    ("encoded instructions", r"\b(decode|base64|rot13)\b.{0,40}\b(and|then)\b.{0,20}\b(follow|execute|run|obey)\b"),
)
#: Zero-width and bidirectional control characters — text hidden from a human reader.
_HIDDEN = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff]")
_ENCODED = re.compile(r"[A-Za-z0-9+/=]{200,}")


def fixed_rules(text: str) -> Optional[tuple[str, str]]:
    """(threat, rule) of the first fixed rule the text breaks, or None."""
    if len(text) > MAX_CHARS:
        return "D", "too long"
    if _HIDDEN.search(text):
        return "A", "hidden characters"
    if _ENCODED.search(text):
        return "A", "encoded blob"
    for name, pattern in FIXED_RULES:
        if re.search(pattern, text, re.I | re.S):
            return "A", name
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


def without_blocked(messages: list) -> list:
    """The messages without each blocked turn: the Belt's message and the guard's reply to it.

    `SupervisorState.messages` appends (`operator.add`), so a blocked message stays in the
    checkpoint; this is how no model and no reload ever reads it (ADR-0067 point 2, T71). Read
    at the phase's input mapper, the one way into the coach, planner, grader and coherence."""
    out: list = []
    for m in messages or []:
        if isinstance(m, AIMessage) and (m.additional_kwargs or {}).get(NODE, {}).get("status") == "blocked":
            if out and isinstance(out[-1], HumanMessage):
                out.pop()
            continue
        out.append(m)
    return out


def current_field(state: SupervisorState, store: Optional[BaseStore]) -> Optional[str]:
    """The element the Belt is working on: the first position not confirmed, from the phase's
    record in the checkpoint (ADR-0066), else from the Store's case copy."""
    from backend.phases import moves, record
    phase = str(state.get("current_phase") or "")
    carried = record.latest(state.get("messages") or [], phase)
    artifacts: dict[str, Any] = dict((carried or {}).get("structured") or {})
    if carried is None and store is not None:
        try:
            from backend.phases.mappers_common import captured_for_phase, read_case_record
            artifacts = captured_for_phase(read_case_record(store, str(state.get("case_id"))), phase)
        except Exception:  # noqa: BLE001 — the reply still goes out without the element
            artifacts = {}
    try:
        found = moves.focus(phase, artifacts)
    except Exception:  # noqa: BLE001
        return None
    return found[0] if found else None


def record(store: Optional[BaseStore], case_id: str, phase: str, n: int, verdict: dict[str, Any]) -> None:
    """The verdict into the decision trail — never the text."""
    if store is None:
        return
    key = f"{NODE}:{phase}:{n}"
    try:
        store.put(("projects", case_id, "step_log"), key, {"layer": NODE, **verdict})
    except Exception as exc:  # noqa: BLE001 — the audit write must not decide the turn
        logger.error("input_guard: the verdict could not be recorded: %s", exc)


async def input_guard(state: SupervisorState, config: Optional[RunnableConfig] = None, *,
                      store: Optional[BaseStore] = None) -> dict[str, Any]:
    configurable = (config or {}).get("configurable") or {}
    msgs = state.get("messages") or []
    if configurable.get("entry", "ask") != "ask" or not msgs or not isinstance(msgs[-1], HumanMessage):
        return {}
    text = _text(msgs[-1])
    base: dict[str, Any] = {"person": configurable.get("current_user") or (msgs[-1].additional_kwargs or {}).get("user"),
            "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    hit = fixed_rules(text)
    if hit:
        verdict: dict[str, Any] = {"status": "blocked", "threat": hit[0], "rule": hit[1], "shield": "not asked"}
    else:
        shield = await content_safety.shield(user_prompt=text)
        if not shield["configured"]:
            verdict = ({"status": "passed", "threat": "", "rule": "", "shield": "skipped"}
                       if content_safety.development_mode() else
                       {"status": "blocked", "threat": "unavailable", "rule": "not configured", "shield": "not configured"})
        elif not shield["reachable"]:
            verdict = {"status": "blocked", "threat": "unavailable", "rule": "unreachable", "shield": "unreachable",
                       "error": shield["error"]}
        elif shield["user_attack"]:
            verdict = {"status": "blocked", "threat": "A", "rule": "prompt shields", "shield": "attack"}
        else:
            verdict = {"status": "passed", "threat": "", "rule": "", "shield": "clean"}
    verdict = {**base, **verdict}
    phase = str(state.get("current_phase") or "")
    record(store, str(state.get("case_id")), phase, len(msgs), verdict)
    if verdict["status"] == "passed":
        return {}
    logger.warning("input_guard BLOCKED a turn on case=%s: threat %s, %s", state.get("case_id"),
                   verdict["threat"], verdict["rule"])
    if verdict["threat"] == "unavailable":
        message = guard_messages.UNAVAILABLE
    else:
        field = current_field(state, store)
        text_of = guard_messages.D_LENGTH if verdict["threat"] == "D" else guard_messages.A
        message = guard_messages.reply(text_of, phase, field, limit=MAX_CHARS) if verdict["threat"] == "D" \
            else guard_messages.reply(text_of, phase, field)
    return {"messages": [AIMessage(content=message, additional_kwargs={NODE: verdict})]}


__all__ = ["input_guard", "blocked", "without_blocked", "fixed_rules", "current_field", "record", "NODE", "MAX_CHARS"]
