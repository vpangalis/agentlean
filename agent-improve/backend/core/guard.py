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

import logging
import re
from typing import Any, Optional

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import get_runtime
from langgraph.store.base import BaseStore
from langgraph.types import RetryPolicy

from backend.core import content_safety, guard_messages
from backend.core.clock import utc_now
from backend.core.errors import ShieldTransientError
from backend.core.llm import block_text
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
    # Role takeover: a new persona WITHOUT the rules, or the
    # coach told to be the grader, validator or system. Narrow on purpose — "Dan will act as
    # champion" and "pretend to be the customer" must pass; Prompt Shields remains the main defence.
    ("role takeover", r"\byou are now\b.{0,60}\b(without|with no|free (of|from)|no longer bound by)\b.{0,20}"
                      r"\b(rules|limits|limitations|restrictions|guidelines|filters|instructions)\b"
                      r"|\bdo anything now\b"
                      r"|\b(pretend|role-?play)\b.{0,20}\b(to be|as|you are|you're)\s+(the |a |an )?(grader|validator|system|reviewer|approver)\b"
                      r"|\bas the (grader|validator)\b"
                      r"|\b(note|message|instructions?)\s+(to|for)\s+the\s+(grader|validator)\b"),
    ("encoded instructions", r"\b(decode|base64|rot13)\b.{0,40}\b(and|then)\b.{0,20}\b(follow|execute|run|obey)\b"),
)
#: Zero-width and bidirectional control characters — text hidden from a human reader.
_HIDDEN = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff]")
_ENCODED = re.compile(r"[A-Za-z0-9+/=]{200,}")
#: G-154 — a transient Prompt Shields failure is tried once more, then the guard fails closed. An
#: attack verdict is an answer, not an error, and is never retried (nor is a content block, T92).
ATTEMPTS = 2
RETRY = RetryPolicy(max_attempts=ATTEMPTS, initial_interval=0.5, jitter=False,
                    retry_on=lambda exc: isinstance(exc, ShieldTransientError))


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


async def screen(text: str) -> dict[str, Any]:
    """Threat A's check of one text, before any model reads it: the fixed rules, then Prompt Shields — the verdict,
    not yet recorded. Unreachable, it fails closed and says whether one more try is worth it (`transient`). The
    input guard and every model call outside the graph (G-262) screen through this one check."""
    hit = fixed_rules(text)
    if hit:
        return {"status": "blocked", "threat": hit[0], "rule": hit[1], "shield": "not asked"}
    shield = await content_safety.shield(user_prompt=text)
    if not shield["configured"]:
        return ({"status": "passed", "threat": "", "rule": "", "shield": "skipped"}
                if content_safety.development_mode() else
                {"status": "blocked", "threat": "unavailable", "rule": "not configured", "shield": "not configured"})
    if not shield["reachable"]:
        return {"status": "blocked", "threat": "unavailable", "rule": "unreachable", "shield": "unreachable",
                "error": shield["error"], "transient": bool(shield.get("transient"))}
    if shield["user_attack"]:
        return {"status": "blocked", "threat": "A", "rule": "prompt shields", "shield": "attack"}
    return {"status": "passed", "threat": "", "rule": "", "shield": "clean"}


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
    at the phase's input mapper, the one way into the coach, planner and grader."""
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
        except Exception as exc:  # noqa: BLE001 — the reply still goes out without the element
            logger.warning("input_guard: the case record could not be read for the element (%s); the reply goes "
                           "out without it", exc)
            artifacts = {}
    try:
        found = moves.focus(phase, artifacts)
    except Exception as exc:  # noqa: BLE001 — the reply still goes out without the element
        logger.warning("input_guard: the element could not be found for phase %s (%s)", phase, exc)
        return None
    return found[0] if found else None


def _attempt() -> int:
    """This run of the node: 1, then 2 on the retry (LangGraph's `ExecutionInfo.node_attempt`);
    1 outside a graph run."""
    try:
        info = getattr(get_runtime(), "execution_info", None)
    except RuntimeError:                     # called outside a graph run (a test calling the node)
        return 1
    return int(getattr(info, "node_attempt", 1) or 1)


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
    text = block_text(msgs[-1])        # G-262: the text the coach reads, through its content blocks
    base: dict[str, Any] = {"person": configurable.get("current_user") or (msgs[-1].additional_kwargs or {}).get("user"),
            "at": utc_now().isoformat(timespec="seconds")}
    verdict = await screen(text)
    if verdict["shield"] == "unreachable":
        attempt = _attempt()
        if verdict.pop("transient") and attempt < ATTEMPTS:
            # G-154 — the node's retry policy runs the guard once more; nothing is recorded yet.
            raise ShieldTransientError(verdict["error"])
        verdict["attempts"] = attempt
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


__all__ = ["input_guard", "screen", "blocked", "without_blocked", "fixed_rules", "current_field", "record", "NODE", "MAX_CHARS"]
