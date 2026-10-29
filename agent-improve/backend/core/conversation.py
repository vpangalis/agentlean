"""Conversation <-> `messages` marshalling.

The case document stores conversation as v1 turn dicts —
``{turn, role, user, text, timestamp, citations}`` — and `SupervisorState` and
`PhaseState` carry it as ``list[BaseMessage]``. The route reads and writes the
case document, the graph reads and writes `messages`.

WHY A MODULE OF ITS OWN
-----------------------
Two callers need the same conversion and neither may own it:

  * `gateway/routes.py` seeds `SupervisorState.messages` from the case document
    and writes the coach's reply back into it — envelope marshalling, the
    route's own job;
  * the phase nodes (`phases/nodes_common.py`) convert across the v1 seam,
    because the v1 path reads turn dicts.

Putting it in either would make the other import it: routes importing from a
phase's nodes breaks the layering, and `phases/` importing from `gateway/`
inverts it. `core/` is below both and imports neither. The alternative is two
copies of one conversion that must agree byte for byte.

**It is transitional in one direction and permanent in the other.** The v1 turn
dict goes with the v1 path; the case document keeps storing conversation, so
the route side survives.
"""
from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

#: The presentational payloads the v1 orchestrator emits alongside its answer.
#: They have no `PhaseState` field and may not be given one without an
#: amendment, so they ride on the message's `additional_kwargs`.
V1_PRESENTATION_KEYS: tuple[str, ...] = (
    "sipoc_diagram", "visualisation", "section_completed",
)

#: Keys this module puts on `additional_kwargs` that are transport, not
#: conversation. They are stripped on the way back into the case document so a
#: turn dict never grows fields the UI does not know about.
_TRANSPORT_KEYS: tuple[str, ...] = (
    "phase", "v1_draft", "gate_verdict", "turn_count", "gate_submission",
    # This turn's field change entries. Rides out with the rest
    # of the turn's product for the same reason they do (`SupervisorState` is
    # seven fields and may not grow an eighth), and is STRIPPED before the
    # case blob's `conversation_history` like the rest: the log's home is
    # `PhaseRecord.field_log`, beside the values it is a log of, not a copy
    # inside every turn of the transcript.
    "field_log",
    # R5 — the turn's after-change field statuses; their home is
    # `PhaseRecord.field_status`, written by the same statement as the values.
    "field_status",
)


#: The four presentational blocks. On the MESSAGE they ride as one dict,
#: `coaching_blocks`; on the TURN (the case blob's `conversation_history`) as
#: flat keys the UI renders — so a turn the Belt saw is rebuilt from history
#: with its blocks, not only from the last send (G-79).
COACHING_BLOCK_KEYS: tuple[str, ...] = ("explanation", "example", "prompt", "progress")

#: The move record (`phases/moves.py`) and last turn's quality
#: feedback ride on the coach's reply, and are kept on the turn so a
#: conversation rebuilt from the case blob carries them too: the next turn's
#: move is derived from them.
MOVE_RECORD_KEY = "coaching_move"
QUALITY_FEEDBACK_KEY = "quality_feedback"
#: ADR-0093 — the read-back card and the confirmation strip, kept on the turn so a reload draws them again.
CARD_KEY, STRIP_KEY = "readback_card", "confirmed_strip"
#: ADR-0093 (DEF-196) — the element a reply works on, "Element n of 13 · name".
ELEMENT_KEY = "reply_element"
#: DEF-212 — the completion card after Define's last Confirm: what the team does next, in order.
COMPLETION_KEY = "completion_card"
#: R-C (ADR-0114) — the element card a teaching turn shows, kept on the turn so a reload draws it again.
TEACHING_CARD_KEY = "teaching_card"
#: R-H — the SIPOC's link check under its challenge: the flagged steps with their notes, and the two buttons' words.
LINK_CHECK_KEY = "link_check"
TURN_RECORD_KEYS: tuple[str, ...] = (MOVE_RECORD_KEY, QUALITY_FEEDBACK_KEY, CARD_KEY, STRIP_KEY, ELEMENT_KEY,
                                     COMPLETION_KEY, TEACHING_CARD_KEY, LINK_CHECK_KEY)


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
    blocks = extra.get("coaching_blocks") or {}
    for key in COACHING_BLOCK_KEYS:
        if blocks.get(key):
            turn[key] = blocks[key]
    if extra.get("grader_warning"):
        turn["grader_warning"] = extra["grader_warning"]
    for key in TURN_RECORD_KEYS:
        if extra.get(key) is not None:
            turn[key] = extra[key]
    return turn


def turn_to_message(turn: dict[str, Any]) -> BaseMessage:
    """One v1 conversation turn dict -> one `BaseMessage`.

    The inverse of `message_to_turn`. `SupervisorState` carries orchestration
    only, so `messages` is the channel that reaches the route — which is
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
    blocks = {k: turn[k] for k in COACHING_BLOCK_KEYS if turn.get(k)}
    if blocks:
        extra["coaching_blocks"] = blocks
    if turn.get("grader_warning"):
        extra["grader_warning"] = turn["grader_warning"]
    for key in TURN_RECORD_KEYS:
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
    grow an eighth. Returns `{}` for a message that carries none, so a
    caller reads "nothing was produced" rather than a `KeyError`.
    """
    extra = dict(getattr(msg, "additional_kwargs", None) or {})
    return {k: extra[k] for k in _TRANSPORT_KEYS if k in extra}


def strip_transport(turn: dict[str, Any]) -> dict[str, Any]:
    """A turn dict with the transport keys removed, ready for the case blob."""
    return {k: v for k, v in turn.items() if k not in _TRANSPORT_KEYS}


__all__ = [
    "V1_PRESENTATION_KEYS",
    "MOVE_RECORD_KEY",
    "QUALITY_FEEDBACK_KEY",
    "CARD_KEY",
    "STRIP_KEY",
    "ELEMENT_KEY",
    "COMPLETION_KEY",
    "TEACHING_CARD_KEY",
    "LINK_CHECK_KEY",
    "TURN_RECORD_KEYS",
    "message_to_turn",
    "turn_to_message",
    "transport",
    "strip_transport",
]
