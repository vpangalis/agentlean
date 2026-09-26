"""The coaching move, decided in code — step 6.61.

Founder ruling 2026-09-25, ARCHITECTURE.md v1.75 (§17, §20, §43), CLAUDE.md §21:
*"The coaching move is decided in code, never by the model. For every field in
every phase and every agent, code determines this turn's move from the field's
status: not yet taught -> teach (explain, show, ask); answered, judged
insufficient -> challenge (say what is missing); answered, judged sufficient ->
read back (the Belt's own words, then ask 'is this right?'); confirmed by the
Belt -> store and advance. An LLM is used only to judge whether an answer is
sufficient, and to write the coach's words. A value is stored only after the
Belt confirms it, in the Belt's words."*

WHAT THIS MODULE OWNS
    positions()        the coached walk, per phase: Define's thirteen positions
                       (metric_definitions inside position 5); the other four
                       phases walk their gate list in `review_rows` order
    field_statuses()   untaught / answered / confirmed for every position
    decide()           THE MOVE, from the status — plus the one model
                       judgment, asked for only when the Belt has answered
    is_confirmation()  whether the Belt's reply confirms a read-back — a rule,
                       not a model: a reply that is anything more than a plain
                       yes is treated as a correction and judged again

WHERE THE STATUS COMES FROM — the tree, never a stored status
    confirmed   every field of the position is in `artifacts`, which since
                6.61 receives a value only on the Belt's confirmation
    answered    the previous coach reply asked for this field (its move record
                names it) and the Belt has replied — or a read-back of it is
                awaiting confirmation (the record carries it as PENDING)
    untaught    neither

    **The move record rides on the coach's reply** (`additional_kwargs`,
    `MOVE_RECORD_KEY`), the channel the §50.1 blocks already use. `PhaseState`
    is rebuilt by the input mapper every turn, so nothing in it survives a turn
    on its own; the reply does — in the parent checkpoint, and in the case
    blob's conversation (`core/conversation.py` round-trips the key). No state
    field is added.
"""
from __future__ import annotations

import re
from typing import Any, Awaitable, Callable, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from backend.core.conversation import MOVE_RECORD_KEY, QUALITY_FEEDBACK_KEY
from backend.core.substate import SufficiencyJudgment, is_empty_capture
from backend.phases.define.schema import DEFINE_FIELD_ORDER, _CAPTURED_INSIDE
from backend.phases.gate_registry import review_rows

#: The four moves of the ruling, plus `respond`: the Belt's latest message is
#: not an answer to the field (a question — "where do we stand?"), so the coach
#: answers it and asks again. The field's status does not change.
TEACH, CHALLENGE, READ_BACK, STORE_AND_ADVANCE, RESPOND = (
    "teach", "challenge", "read_back", "store_and_advance", "respond")
MOVES: tuple[str, ...] = (TEACH, CHALLENGE, READ_BACK, STORE_AND_ADVANCE, RESPOND)

#: The four statuses of founder ruling R5 (2026-09-25), in order. STORED in
#: `PhaseState.field_status`, never derived from a reply; only code changes
#: one, at turn end. "Awaiting confirmation" is ANSWERED with a read-back
#: pending, not a fifth status.
NOT_TAUGHT, ASKED, ANSWERED, CONFIRMED = "not taught", "asked", "answered", "confirmed"
STATUSES: tuple[str, ...] = (NOT_TAUGHT, ASKED, ANSWERED, CONFIRMED)

#: The Belt's two buttons under a read-back (R4). A click sets the status in
#: code; no model reads it.
CONFIRM_CLICK, CHANGE_CLICK = "confirm", "change"
CHANGE_REASON = ("The Belt clicked Change: ask what they want to change in the "
                 "read-back, and show their current words.")
#: R6 — the team REJECTED the Define report naming this element; the resumed
#: run carries this action. Like Change, but from the gate, with its reason.
REJECTED = "rejected"
REJECT_REASON = ("The team rejected the Define report and named this element to "
                 "change — their reason: {reason}. Show the Belt their current "
                 "words and ask what should change.")

#: Where the move record rides on the coach's reply, and where last turn's
#: quality feedback rides (step 6.61, §19.1's fifth section) — owned by
#: `core/conversation.py`, which round-trips both through the case blob.

#: Plain-string fields whose read-back value is COMPOSED by the coach from the
#: Belt's answers rather than read back verbatim — the script composes the
#: problem statement from the 5W2H answers (position 4).
COMPOSED_FIELDS: frozenset[str] = frozenset({"problem_statement"})


# ══ the walk ═════════════════════════════════════════════════════════════════


def positions(phase: str) -> list[tuple[str, tuple[str, ...]]]:
    """`(field, fields captured at that position)`, in coached order.

    Define has its ordered walk (§39.1.2) and one field captured inside a
    position (`metric_definitions` at position 5, §39.1.9). The other four
    phases expose tier SETS, not a walk, so they walk their gate list in
    `review_rows` order — Tier 1, then Tier 2 — the order the planner's ledger
    has always used.
    """
    if phase == "define":
        return [(f, (f, *_CAPTURED_INSIDE.get(f, ()))) for f in DEFINE_FIELD_ORDER]
    return [(r["field"], (r["field"],)) for r in review_rows(phase, {})]


def _stored(artifacts: dict[str, Any], field: str) -> bool:
    return not is_empty_capture(artifacts.get(field))


def focus(phase: str, artifacts: dict[str, Any]) -> Optional[tuple[str, tuple[str, ...]]]:
    """The first position not yet confirmed, or `None` when all are."""
    for field, fields in positions(phase):
        if not all(_stored(artifacts, f) for f in fields):
            return field, fields
    return None


# ══ the record the previous reply carries ════════════════════════════════════


def last_record(messages: list[BaseMessage]) -> Optional[dict[str, Any]]:
    """The move record of the coach's reply the Belt is answering now.

    Only the previous turn counts: walking back from the end, past this turn's
    Belt message, the AI messages up to the previous Belt message are that
    reply. A turn that ended without a record (a timeout) leaves `None`, and
    the field is taught again rather than a stale record being trusted.
    """
    seen_belt = False
    for message in reversed(messages or []):
        if isinstance(message, HumanMessage):
            if seen_belt:
                return None
            seen_belt = True
            continue
        if seen_belt and isinstance(message, AIMessage):
            record = (message.additional_kwargs or {}).get(MOVE_RECORD_KEY)
            if isinstance(record, dict):
                return dict(record)
    return None


def last_feedback(messages: list[BaseMessage]) -> Optional[dict[str, Any]]:
    """Last turn's quality feedback — the grader's and coherence's verdicts on
    the previous reply, which the executor put on that reply."""
    seen_belt = False
    for message in reversed(messages or []):
        if isinstance(message, HumanMessage):
            if seen_belt:
                return None
            seen_belt = True
            continue
        if seen_belt and isinstance(message, AIMessage):
            fb = (message.additional_kwargs or {}).get(QUALITY_FEEDBACK_KEY)
            if isinstance(fb, dict):
                return dict(fb)
    return None


def belt_message(messages: list[BaseMessage]) -> str:
    """The Belt's latest message, as text (content blocks, §4.5)."""
    for message in reversed(messages or []):
        if isinstance(message, HumanMessage):
            return message.text.strip()
    return ""


# ══ confirmation — a rule, not a model ══════════════════════════════════════

_AFFIRM = re.compile(
    r"^(yes|yep|yeah|yup|correct|right|exactly|confirmed?|agreed|perfect|spot on|"
    r"ok|okay|great|good|that'?s (right|correct|it|fine|good|perfect)|that is (right|correct)|"
    r"looks (good|right|fine)|sounds (good|right))\b")
#: Words that make a reply more than a plain yes — a correction, a condition or
#: an addition. Such a reply is judged as an answer again, never taken as a yes.
_QUALIFIER = re.compile(
    r"\b(but|except|however|although|though|actually|change|changed|instead|not|no|"
    r"wrong|missing|add|also|should|rather|correction|correct it|update|replace)\b")
_NOTHING_TO_CHANGE = re.compile(r"\b(no changes?|nothing to change|no corrections?|not a thing)\b")


def is_confirmation(text: str) -> bool:
    """A plain yes to the read-back: it opens with an affirmative and carries
    nothing that qualifies it. Anything else is a correction, and returns the
    field to ANSWERED (the ruling: *"The Belt correcting a read-back returns to
    'answered'"*)."""
    t = " ".join(re.sub(r"[^\w'\s]", " ", (text or "").lower().replace("’", "'")).split())
    if not t or not _AFFIRM.match(t):
        return False
    return not _QUALIFIER.search(_NOTHING_TO_CHANGE.sub(" ", t))


# ══ status and move ══════════════════════════════════════════════════════════


def status_of(phase: str, field: str, artifacts: dict[str, Any],
              field_status: dict[str, dict[str, Any]]) -> str:
    """A position's STORED status. A position whose values are already in
    `artifacts` with no status recorded (a case from before 6.61) counts as
    confirmed — nothing reaches `artifacts` any other way."""
    entry = field_status.get(field) or {}
    if entry.get("status") in STATUSES:
        return str(entry["status"])
    fields = dict(positions(phase)).get(field, (field,))
    return CONFIRMED if all(_stored(artifacts, f) for f in fields) else NOT_TAUGHT


def field_statuses(phase: str, artifacts: dict[str, Any],
                   field_status: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Every position's stored status — brief item 1, ruling R5."""
    return {f: status_of(phase, f, artifacts, field_status) for f, _ in positions(phase)}


def current(phase: str, artifacts: dict[str, Any],
            field_status: dict[str, dict[str, Any]]) -> Optional[tuple[str, tuple[str, ...]]]:
    """The current field: the first position not confirmed (R5)."""
    for field, fields in positions(phase):
        if status_of(phase, field, artifacts, field_status) != CONFIRMED:
            return field, fields
    return None


Judge = Callable[[str, str, str, str], Awaitable[SufficiencyJudgment]]


def _join(*parts: str) -> str:
    return chr(10).join(p for p in (s.strip() for s in parts) if p)


async def decide(phase: str, artifacts: dict[str, Any],
                 field_status: dict[str, dict[str, Any]], belt: str,
                 judge: Judge, action: Optional[str] = None) -> dict[str, Any]:
    """THE MOVE, from the STORED status (brief item 2, rulings R4 and R5), and
    the statuses AFTER this turn — which the executor stores at turn end.

    `judge(field, answer_so_far, latest, reading_back)` is the planner's one
    model judgment, called only for an answer: never on a field not taught,
    never on a Confirm or Change click, never on a plain typed yes.
    """
    after = {f: dict(v) for f, v in field_status.items()}
    base: dict[str, Any] = {"judgment": None, "answer": "", "messages": 0, "pending": None,
            "store": {}, "stored_field": None, "reason": ""}

    def done(field: Optional[str], fields: Any, status: str, move: str, **kw: Any) -> dict:
        out = {**base, "field": field, "fields": tuple(fields or ()), "status": status,
               "move": move, **kw}
        merged = {**artifacts, **out["store"]}
        out["field_status"] = after
        out["statuses"] = field_statuses(phase, merged, after)
        return out

    at = current(phase, artifacts, after)
    if at is None:
        return done(None, (), CONFIRMED, RESPOND)
    field, fields = at
    status = status_of(phase, field, artifacts, after)
    entry = dict(after.get(field) or {})

    if action == REJECTED:
        # R6 — back from a rejected report: the coach guides the Belt to the
        # element the team named, showing their current words. No judgment:
        # the Belt has not answered anything yet.
        reason = str((entry.get("rejected") or {}).get("reason") or "none given")
        return done(field, fields, status, CHALLENGE, answer=str(entry.get("answer") or ""),
                    messages=int(entry.get("messages") or 1),
                    reason=REJECT_REASON.format(reason=reason))

    if status == NOT_TAUGHT:
        after[field] = {"status": ASKED}
        return done(field, fields, status, TEACH)

    pending = entry.get("pending") if status == ANSWERED else None
    if pending and (action == CONFIRM_CLICK or (action is None and is_confirmation(belt))):
        store = dict(pending.get("store") or {})
        merged = {**artifacts, **store}
        if not all(_stored(merged, f) for f in fields):
            # A yes to a read-back that cannot complete the position (a
            # structure refused): nothing is stored, the read-back is made again.
            return done(field, fields, status, READ_BACK,
                        answer=str(pending.get("belt_words") or ""),
                        messages=int(pending.get("messages") or 1),
                        pending={k: v for k, v in pending.items() if k not in ("store", "proposed")})
        after[field] = {"status": CONFIRMED}
        nxt = current(phase, merged, after)
        if nxt is not None:
            after[nxt[0]] = {"status": ASKED}
        return done(nxt[0] if nxt else None, nxt[1] if nxt else (), status, STORE_AND_ADVANCE,
                    store=store, stored_field=field)

    if pending and action == CHANGE_CLICK:
        words = str(pending.get("belt_words") or "")
        after[field] = {"status": ASKED, "answer": words, "messages": int(pending.get("messages") or 1)}
        return done(field, fields, status, CHALLENGE, answer=words,
                    messages=int(pending.get("messages") or 1), reason=CHANGE_REASON)

    previous = str((pending or {}).get("belt_words") or entry.get("answer") or "")
    so_far = int((pending or entry).get("messages") or 0)
    answer = _join(previous, belt)
    judgment = await judge(field, previous, belt, "yes" if pending else "no")
    if judgment.verdict == "not_an_answer":
        return done(field, fields, status, RESPOND, judgment=judgment, answer=previous,
                    messages=so_far, pending=pending, reason=judgment.reason)
    if judgment.verdict == "sufficient":
        new_pending = {"field": field, "fields": list(fields), "belt_words": answer,
                       "messages": so_far + 1}
        after[field] = {"status": ANSWERED, "answer": answer, "messages": so_far + 1,
                        "pending": new_pending}
        return done(field, fields, status, READ_BACK, judgment=judgment, answer=answer,
                    messages=so_far + 1, pending=new_pending)
    after[field] = {"status": ASKED, "answer": answer, "messages": so_far + 1}
    # R3 — the challenge NAMES the failed acceptance criterion.
    crit = getattr(judgment, "failed_criterion", None)
    reason = f"criterion `{crit}` — {judgment.reason}" if crit else judgment.reason
    return done(field, fields, status, CHALLENGE, judgment=judgment, answer=answer,
                messages=so_far + 1, reason=reason)


def pending_store(phase: str, pending: dict[str, Any], proposed: dict[str, Any]) -> dict[str, Any]:
    """What a confirmation of this read-back will store — brief item 4.

    **The Belt's own words**, for a plain-string field answered in one message.
    **The version the coach read back** — which the Belt is then confirming —
    for a structured field (a team is a list, a SIPOC six keys: prose cannot
    be stored as either), a composed field (the problem statement is composed
    from the 5W2H answers) and an answer assembled from more than one message
    (a correction, or the piece a challenge asked for).
    """
    field = pending["field"]
    words = str(pending.get("belt_words") or "")
    one_message = int(pending.get("messages") or 1) <= 1
    store: dict[str, Any] = {}
    for f in pending.get("fields") or [field]:
        value = proposed.get(f)
        verbatim = (f == field and one_message and f not in COMPOSED_FIELDS
                    and (value is None or isinstance(value, str)))
        if verbatim:
            store[f] = words
        elif value is not None and not is_empty_capture(value):
            store[f] = value
    return store


__all__ = [
    "MOVES", "STATUSES", "TEACH", "CHALLENGE", "READ_BACK", "STORE_AND_ADVANCE", "RESPOND",
    "NOT_TAUGHT", "ASKED", "ANSWERED", "CONFIRMED", "CONFIRM_CLICK", "CHANGE_CLICK", "REJECTED",
    "MOVE_RECORD_KEY", "QUALITY_FEEDBACK_KEY", "COMPOSED_FIELDS", "positions", "focus",
    "current", "status_of", "last_record", "last_feedback", "belt_message",
    "is_confirmation", "field_statuses", "decide", "pending_store",
]
