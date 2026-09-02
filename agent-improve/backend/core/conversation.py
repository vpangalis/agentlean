"""Conversation <-> `messages` marshalling — procedure step 4.2.

The case document stores conversation as v1 turn dicts —
``{turn, role, user, text, timestamp, citations}`` — and `SupervisorState` and
`PhaseState` carry it as ``list[BaseMessage]`` (§5, §6). Step 4.2 is the first
step where both shapes are live at once, because it is the step that routes
`/ask` through the graph: the route reads and writes the case document, the
graph reads and writes `messages`.

WHY A MODULE OF ITS OWN
-----------------------
Two callers need the same conversion and neither may own it:

  * `gateway/routes.py` seeds `SupervisorState.messages` from the case document
    and writes the coach's reply back into it — envelope marshalling, which §49
    names as the route's own job;
  * `phases/define/nodes.py` converts in both directions across the WATCH 7
    seam, because `orchestrate_define` reads v1 turn dicts.

Putting it in either would make the other import it: routes importing from a
phase's `nodes.py` is what §1.1 exists to stop, and `phases/` importing from
`gateway/` inverts the layering. `core/` is below both and imports neither.

**Not in Appendix B's `New` file list**, which enumerates
``phases/{phase}/{graph,nodes,mappers}.py`` and no shared module. Flagged
rather than assumed — the same call `phases/mappers_common.py` records, and for
the same reason: the alternative is two copies of one conversion that must
agree byte for byte.

**It is transitional in one direction and permanent in the other.** The v1 turn
dict dies with `orchestrate.py` at step 11.1; the case document keeps storing
conversation, so the route side survives. What goes away then is
``V1_PRESENTATION_KEYS`` — those three payloads become
``CoachingResponse`` fields at 6.2 (§10.7, WATCH 9).
"""
from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

#: The presentational payloads the v1 orchestrator emits alongside its answer.
#: They have no `PhaseState` field and may not be given one without a §56
#: amendment, so they ride on the message's `additional_kwargs` — the channel
#: `CoachingResponse` formalises at 6.2.
V1_PRESENTATION_KEYS: tuple[str, ...] = (
    "sipoc_diagram", "visualisation", "section_completed",
)

#: Keys this module puts on `additional_kwargs` that are transport, not
#: conversation. They are stripped on the way back into the case document so a
#: turn dict never grows fields the UI does not know about.
_TRANSPORT_KEYS: tuple[str, ...] = (
    "phase", "v1_artifacts", "gate_verdict", "turn_count", "gate_submission",
)


def message_to_turn(msg: BaseMessage, index: int) -> dict[str, Any]:
    """One `BaseMessage` -> one v1 conversation turn dict.

    The whole turn shape round-trips through ``additional_kwargs``, so nothing
    the case document holds is lost crossing in either direction. The turn
    number falls back to position so a message built outside this module still
    produces a well-formed turn.
    """
    extra = dict(getattr(msg, "additional_kwargs", None) or {})
    content = msg.content
    turn: dict[str, Any] = {
        "turn": extra.get("turn") or index + 1,
        "role": "ai" if isinstance(msg, AIMessage) else "user",
        "user": extra.get("user"),
        "text": content if isinstance(content, str) else str(content),
        "timestamp": extra.get("timestamp"),
        "citations": extra.get("citations") or [],
    }
    for key in V1_PRESENTATION_KEYS:
        if extra.get(key) is not None:
            turn[key] = extra[key]
    return turn


def turn_to_message(turn: dict[str, Any]) -> BaseMessage:
    """One v1 conversation turn dict -> one `BaseMessage`.

    The inverse of `message_to_turn`. `SupervisorState` carries orchestration
    only (§5), so `messages` is the channel that reaches the route — which is
    why everything a turn holds beyond its text travels in
    ``additional_kwargs`` rather than in a state field of its own.
    """
    extra: dict[str, Any] = {
        "turn": turn.get("turn"),
        "user": turn.get("user"),
        "timestamp": turn.get("timestamp"),
        "citations": turn.get("citations") or [],
    }
    for key in V1_PRESENTATION_KEYS:
        if turn.get(key) is not None:
            extra[key] = turn[key]

    text = turn.get("text") or ""
    if turn.get("role") == "ai":
        return AIMessage(content=text, additional_kwargs=extra)
    return HumanMessage(content=text, additional_kwargs=extra)


def transport(msg: BaseMessage) -> dict[str, Any]:
    """The turn's product, read off the message that carried it out.

    The parent phase node attaches the captured fields, the gate verdict and
    the turn count here because `SupervisorState` has seven fields and may not
    grow an eighth (§5). Returns `{}` for a message that carries none, so a
    caller reads "nothing was produced" rather than a `KeyError`.
    """
    extra = dict(getattr(msg, "additional_kwargs", None) or {})
    return {k: extra[k] for k in _TRANSPORT_KEYS if k in extra}


def strip_transport(turn: dict[str, Any]) -> dict[str, Any]:
    """A turn dict with the transport keys removed, ready for the case blob."""
    return {k: v for k, v in turn.items() if k not in _TRANSPORT_KEYS}


__all__ = [
    "V1_PRESENTATION_KEYS",
    "message_to_turn",
    "turn_to_message",
    "transport",
    "strip_transport",
]
