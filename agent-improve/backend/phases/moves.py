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
from backend.phases.gate_registry import declared_type, review_rows

#: The four moves of the ruling, plus `respond`: the Belt's latest message is
#: not an answer to the field (a question — "where do we stand?"), so the coach
#: answers it and asks again. The field's status does not change.
TEACH, CHALLENGE, READ_BACK, STORE_AND_ADVANCE, RESPOND = (
    "teach", "challenge", "read_back", "store_and_advance", "respond")
#: ADR-0072 (DEF-075, R14): after the THIRD failed attempt on one element — a challenge, or a
#: Confirm that could not be stored — code offers to park it; the Belt decides with a button.
OFFER_PARK = "offer_park"
MOVES: tuple[str, ...] = (TEACH, CHALLENGE, READ_BACK, STORE_AND_ADVANCE, RESPOND, OFFER_PARK)
#: Failed attempts on one element before the offer (ADR-0072 point 2).
PARK_AFTER = 3

#: The four statuses of founder ruling R5 (2026-09-25), in order. STORED in
#: `PhaseState.field_status`, never derived from a reply; only code changes
#: one, at turn end. "Awaiting confirmation" is ANSWERED with a read-back
#: pending, not a fifth status.
NOT_TAUGHT, ASKED, ANSWERED, CONFIRMED = "not taught", "asked", "answered", "confirmed"
#: ADR-0072: a parked element — open, nothing stored, skipped until every other available element
#: is confirmed, then returned to first; a Define element parked blocks the gate (all are Tier 1).
PARKED = "parked"
STATUSES: tuple[str, ...] = (NOT_TAUGHT, ASKED, ANSWERED, CONFIRMED, PARKED)

#: The Belt's two buttons under a read-back (R4). A click sets the status in
#: code; no model reads it.
CONFIRM_CLICK, CHANGE_CLICK = "confirm", "change"
#: ADR-0072 — the two buttons under an offer to park.
PARK_CLICK, TRY_AGAIN_CLICK = "park", "try_again"
#: W9 (DEF-079) — the Belt picked an element in the progress view: Change on a confirmed one,
#: Resume on a parked one. It rides with `element` and starts coaching on that element, in code.
REVISE_CLICK = "revise"
REVISE_REASON = ("The Belt chose to change `{field}`, confirmed earlier: show their current words "
                 "and ask what they want to change.")
OFFER_PARK_REASON = ("The Belt has tried `{field}` {n} times without it meeting its criteria. Explain "
                     "briefly why this element matters, and say they can park it and come back to it "
                     "later, or try again now — the screen shows the two buttons.")
PARKED_REASON = ("The Belt parked `{parked}` to come back to later. Teach `{field}` now.")
TRY_AGAIN_REASON = ("The Belt chose to try `{field}` again: explain it once more, simply, and ask for it.")
RETURN_REASON = ("Every other element is confirmed: back to the parked element `{field}`. Say it was "
                 "parked, explain it again and ask for it.")
CHANGE_REASON = ("The Belt clicked Change: ask what they want to change in the "
                 "read-back, and show their current words.")
#: DEF-029 / G-117 — the Belt confirmed a read-back that cannot complete the position: nothing
#: is stored, and the read-back is made again with what it lacked. Read by the executor
#: (`nodes_common._store_truth`) to tell the Belt, in code, that nothing was stored.
CONFIRM_INCOMPLETE = ("The Belt confirmed, but NOTHING WAS STORED: the read-back did not carry "
                      "{missing}. Read back again with every field of this position filled "
                      "from the Belt's words, each in its declared shape.")
#: G-121 (DEF-158) — the SIPOC is stored only with all six columns; a Confirm without them is
#: answered by asking for exactly the missing ones. Same opening as CONFIRM_INCOMPLETE, so the
#: executor tells the Belt, in code, that nothing was stored.
COLUMNS_MISSING = ("The Belt confirmed, but NOTHING WAS STORED: the SIPOC needs all six columns "
                   "and lacks {missing}. Ask for exactly those columns, naming each.")
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
    if field == "process_map_sipoc":            # G-121: all six columns, or not stored
        from backend.phases.define.parse import missing_columns
        return not missing_columns(artifacts.get(field))
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
    """The current field: an element the Belt picked in the progress view while it is not
    confirmed (W9, DEF-079); else the first position not confirmed (R5) — skipping a parked one
    while any other is open, and returning to the parked ones first once every other is
    confirmed (ADR-0072 point 4)."""
    for field, fields in positions(phase):
        entry = field_status.get(field) or {}
        if entry.get("picked") and status_of(phase, field, artifacts, field_status) not in (CONFIRMED, PARKED):
            return field, fields
    parked = None
    for field, fields in positions(phase):
        status = status_of(phase, field, artifacts, field_status)
        if status == CONFIRMED:
            continue
        if status == PARKED:
            parked = parked or (field, fields)
            continue
        return field, fields
    return parked


def parked(phase: str, field_status: dict[str, dict[str, Any]]) -> list[str]:
    """The parked positions, in coached order."""
    return [f for f, _ in positions(phase) if (field_status.get(f) or {}).get("status") == PARKED]


def park_events(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]],
                person: Optional[str], at: str) -> list[dict[str, Any]]:
    """ADR-0072 point 6: every park and every return, with the person and the time — for
    `step_log`. A return is a parked element's status leaving PARKED."""
    out = []
    for field in sorted(set(before) | set(after)):
        was = (before.get(field) or {}).get("status")
        now = (after.get(field) or {}).get("status")
        if now == PARKED and was != PARKED:
            out.append({"event": "park", "field": field, "person": person, "at": at})
        elif was == PARKED and now != PARKED:
            out.append({"event": "return", "field": field, "person": person, "at": at})
    return out


Judge = Callable[[str, str, str, str], Awaitable[SufficiencyJudgment]]


def _earlier(entry: dict[str, Any], pending: Optional[dict[str, Any]]) -> dict[str, Any]:
    """G-118 (DEF-157) — what was proposed for this element before, kept so a later read-back of
    the same element is not left without a part the Belt already gave (the CTQs after a Change).
    Oldest first, so the latest proposal wins."""
    out = dict(entry.get("earlier") or {})
    if pending:
        out.update(pending.get("earlier") or {})
        out.update(pending.get("proposed") or pending.get("store") or {})
    return {f: v for f, v in out.items() if not is_empty_capture(v)}


def _earlier_kw(entry: dict[str, Any], pending: Optional[dict[str, Any]]) -> dict[str, Any]:
    """`{"earlier": …}` when there is anything to carry, else nothing."""
    e = _earlier(entry, pending)
    return {"earlier": e} if e else {}


def _words(value: Any) -> str:
    """A stored value as the Belt's words to show again: text as it is, a MetricValue's `raw`,
    structure as compact JSON."""
    import json
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and "raw" in value and "value" in value:
        return str(value["raw"])
    return json.dumps(value, ensure_ascii=False)


def element_rows(phase: str, artifacts: dict[str, Any],
                 field_status: dict[str, dict[str, Any]], name: Callable[[str], str]) -> list[dict[str, Any]]:
    """The progress view's elements (W9, DEF-079), from the same statuses the moves read: each
    position's number, field, name and status — confirmed, parked (ADR-0072's marker), current,
    or open. The screen draws a Change action on a confirmed one and Resume on a parked one."""
    at = current(phase, artifacts, field_status)
    rows = []
    for n, (field, _fields) in enumerate(positions(phase), start=1):
        status = status_of(phase, field, artifacts, field_status)
        shown = ("confirmed" if status == CONFIRMED else "parked" if status == PARKED
                 else "current" if at and at[0] == field else "open")
        rows.append({"n": n, "field": field, "name": name(field), "status": shown})
    return rows


def _attempts(entry: dict[str, Any]) -> dict[str, Any]:
    """The failed-attempt count an element's entry carries forward (ADR-0072)."""
    n = int(entry.get("attempts") or 0)
    return {"attempts": n} if n else {}


def _join(*parts: str) -> str:
    return chr(10).join(p for p in (s.strip() for s in parts) if p)


async def decide(phase: str, artifacts: dict[str, Any],
                 field_status: dict[str, dict[str, Any]], belt: str,
                 judge: Judge, action: Optional[str] = None,
                 element: Optional[str] = None) -> dict[str, Any]:
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

    # W9 (DEF-079) — an element picked in the progress view: coaching starts on it, in code.
    known = dict(positions(phase))
    if action == REVISE_CLICK and element in known:
        fields = known[element]
        status = status_of(phase, element, artifacts, after)
        entry = dict(after.get(element) or {})
        if status == CONFIRMED:
            words = _words(artifacts.get(element))
            after[element] = {"status": ASKED, "answer": words, "messages": 1, "picked": True}
            return done(element, fields, status, CHALLENGE, answer=words, messages=1,
                        reason=REVISE_REASON.format(field=element))
        if status == PARKED:
            after[element] = {"status": ASKED, "answer": str(entry.get("answer") or ""), "returned": True,
                              "picked": True}
            return done(element, fields, status, TEACH, reason=RETURN_REASON.format(field=element))
        after[element] = {**entry, "status": entry.get("status") if entry.get("status") in (ASKED, ANSWERED)
                          else ASKED, "picked": True}
        return done(element, fields, status, TEACH)

    at = current(phase, artifacts, after)
    if at is None:
        return done(None, (), CONFIRMED, RESPOND)
    field, fields = at
    status = status_of(phase, field, artifacts, after)
    entry = dict(after.get(field) or {})

    # ADR-0072 — the Belt's answer to an offer to park, decided in code.
    if entry.get("offer_park") and action == PARK_CLICK:
        after[field] = {"status": PARKED, "answer": str(entry.get("answer") or ""), **_attempts(entry)}
        nxt = current(phase, artifacts, after)
        if nxt is None or nxt[0] == field:
            # Nothing else is open: the parked element is the one left, taught again.
            after[field] = {"status": ASKED, "answer": str(entry.get("answer") or "")}
            return done(field, fields, status, TEACH, reason=RETURN_REASON.format(field=field))
        nxt_status = status_of(phase, nxt[0], artifacts, after)
        if nxt_status in (NOT_TAUGHT, PARKED):
            after[nxt[0]] = {"status": ASKED}
        return done(nxt[0], nxt[1], nxt_status, TEACH, reason=PARKED_REASON.format(parked=field, field=nxt[0]))
    if entry.get("offer_park") and action == TRY_AGAIN_CLICK:
        after[field] = {"status": ASKED, "answer": str(entry.get("answer") or ""),
                        "messages": int(entry.get("messages") or 0), **_earlier_kw(entry, None)}
        return done(field, fields, status, TEACH, reason=TRY_AGAIN_REASON.format(field=field))
    if status == PARKED:
        # ADR-0072 point 4 — back to a parked element (every other one is confirmed).
        after[field] = {"status": ASKED, "answer": str(entry.get("answer") or ""), "returned": True}
        return done(field, fields, status, TEACH, reason=RETURN_REASON.format(field=field))

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
            # DEF-029 / G-117: the reason names what was missing, so the coach's next read-back
            # carries it and the executor tells the Belt, in code, that nothing was stored.
            missing = [f for f in fields if not _stored(merged, f)]
            # ADR-0072 — a refused Confirm is a failed attempt; the third brings the offer.
            tries = int(entry.get("attempts") or 0) + 1
            if tries >= PARK_AFTER:
                words = str(pending.get("belt_words") or "")
                after[field] = {"status": ASKED, "answer": words, "messages": int(pending.get("messages") or 1),
                                "attempts": tries, "offer_park": True, **_earlier_kw(entry, pending)}
                return done(field, fields, status, OFFER_PARK, answer=words,
                            reason=OFFER_PARK_REASON.format(field=field, n=tries))
            if missing == ["process_map_sipoc"] and isinstance(merged.get("process_map_sipoc"), dict):
                from backend.phases.define.parse import missing_columns
                words = str(pending.get("belt_words") or "")
                after[field] = {"status": ASKED, "answer": words, "messages": int(pending.get("messages") or 1),
                                "attempts": tries, **_earlier_kw(entry, pending)}
                return done(field, fields, status, CHALLENGE, answer=words,
                            messages=int(pending.get("messages") or 1),
                            reason=COLUMNS_MISSING.format(missing=", ".join(
                                f"`{c}`" for c in missing_columns(merged.get("process_map_sipoc")))))
            after[field] = {**entry, "attempts": tries}
            return done(field, fields, status, READ_BACK,
                        answer=str(pending.get("belt_words") or ""),
                        messages=int(pending.get("messages") or 1),
                        pending={**{k: v for k, v in pending.items() if k not in ("store", "proposed")},
                                 **_earlier_kw(entry, pending)},
                        reason=CONFIRM_INCOMPLETE.format(missing=", ".join(f"`{f}`" for f in missing)))
        after[field] = {"status": CONFIRMED}
        nxt = current(phase, merged, after)
        if nxt is not None:
            after[nxt[0]] = {"status": ASKED}
        return done(nxt[0] if nxt else None, nxt[1] if nxt else (), status, STORE_AND_ADVANCE,
                    store=store, stored_field=field)

    if pending and action == CHANGE_CLICK:
        words = str(pending.get("belt_words") or "")
        after[field] = {"status": ASKED, "answer": words, "messages": int(pending.get("messages") or 1),
                        **_attempts(entry), **_earlier_kw(entry, pending)}
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
                       "messages": so_far + 1, **_earlier_kw(entry, pending)}
        after[field] = {"status": ANSWERED, "answer": answer, "messages": so_far + 1,
                        "pending": new_pending, **_attempts(entry)}
        return done(field, fields, status, READ_BACK, judgment=judgment, answer=answer,
                    messages=so_far + 1, pending=new_pending)
    # ADR-0072 — an insufficient answer is a failed attempt; the third brings the offer to park.
    tries = int(entry.get("attempts") or 0) + 1
    after[field] = {"status": ASKED, "answer": answer, "messages": so_far + 1, "attempts": tries,
                    **_earlier_kw(entry, pending)}
    if tries >= PARK_AFTER:
        after[field]["offer_park"] = True
        return done(field, fields, status, OFFER_PARK, judgment=judgment, answer=answer,
                    messages=so_far + 1, reason=OFFER_PARK_REASON.format(field=field, n=tries))
    # R3 — the challenge NAMES the failed acceptance criterion.
    crit = getattr(judgment, "failed_criterion", None)
    reason = f"criterion `{crit}` — {judgment.reason}" if crit else judgment.reason
    return done(field, fields, status, CHALLENGE, judgment=judgment, answer=answer,
                messages=so_far + 1, reason=reason)


def pending_store(phase: str, pending: dict[str, Any], proposed: dict[str, Any],
                  artifacts: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """What a confirmation of this read-back will store — brief item 4.

    **The Belt's own words**, for a plain-string field answered in one message.
    **The version the coach read back** — which the Belt is then confirming —
    for a structured field (a team is a list, a SIPOC six keys: prose cannot
    be stored as either), a composed field (the problem statement is composed
    from the 5W2H answers) and an answer assembled from more than one message
    (a correction, or the piece a challenge asked for).

    **ADR-0071 (DEF-076): the baseline and the target are MetricValues parsed IN CODE from the
    Belt's words** (`parse.metric_value`, the one parser) — never the model's proposal. A reading
    with no number stores nothing, so a Confirm is refused and the value is asked again. The unit
    hint: the primary metric's (proposed in the same read-back, or registered), for a target the
    baseline's.
    """
    field = pending["field"]
    from backend.phases.define import parse
    known = {**dict(artifacts or {}), **{k: v for k, v in proposed.items() if k == "metric_definitions"}}
    words = str(pending.get("belt_words") or "")
    one_message = int(pending.get("messages") or 1) <= 1
    store: dict[str, Any] = {}
    for f in pending.get("fields") or [field]:
        if phase == "define" and f in parse.METRIC_FIELDS:
            unit = parse.primary_unit(known)
            if f == "baseline_estimate" and not unit:
                # G-135: without the metric's unit there is nothing to read the baseline by — the
                # first figure could be "30 days" or a year. Nothing is stored; the Confirm names it.
                continue
            if f == "target_value" and known.get("baseline_estimate"):
                unit = parse.as_metric(known["baseline_estimate"], unit=unit)["unit"] or unit
            # The figure of the Belt's LATEST message that holds one (a correction wins over the
            # answer it corrects); `raw` keeps all of the Belt's words for this element.
            for line in reversed([x for x in words.split(chr(10)) if x.strip()]):
                mv = parse.metric_value(line, target=f == "target_value", unit=unit)
                if mv["value"] is not None:
                    store[f] = {**mv, "raw": words}
                    break
            continue
        value = proposed.get(f)
        structured = declared_type(phase, f) not in (None, str)
        if f == "process_map_sipoc" and not isinstance(value, dict):
            # G-121 (DEF-158): the SIPOC from its labels, parsed in code — never the prose itself.
            from backend.phases.define.parse import parse_sipoc
            value = parse_sipoc(str(value or words)) or None
        verbatim = (f == field and one_message and f not in COMPOSED_FIELDS and not structured
                    and (value is None or isinstance(value, str)))
        if verbatim:
            store[f] = words
        elif value is not None and not is_empty_capture(value) and not (structured and isinstance(value, str)):
            store[f] = value
    return store


__all__ = [
    "MOVES", "STATUSES", "OFFER_PARK", "PARKED", "PARK_CLICK", "TRY_AGAIN_CLICK", "PARK_AFTER",
    "parked", "park_events", "element_rows", "REVISE_CLICK", "CONFIRM_INCOMPLETE", "COLUMNS_MISSING", "TEACH", "CHALLENGE", "READ_BACK", "STORE_AND_ADVANCE", "RESPOND",
    "NOT_TAUGHT", "ASKED", "ANSWERED", "CONFIRMED", "CONFIRM_CLICK", "CHANGE_CLICK", "REJECTED",
    "MOVE_RECORD_KEY", "QUALITY_FEEDBACK_KEY", "COMPOSED_FIELDS", "positions", "focus",
    "current", "status_of", "last_record", "last_feedback", "belt_message",
    "is_confirmation", "field_statuses", "decide", "pending_store",
]
