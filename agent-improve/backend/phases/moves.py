"""The coaching move, decided in code.

The rule this module carries out:
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
                       (the CTQs, the 5W2H and metric_definitions captured
                       inside positions 3, 4 and 5); the other four phases walk
                       their gate list in `review_rows` order
    field_statuses()   not taught / asked / answered / confirmed / parked for
                       every position
    decide()           THE MOVE, from the status — plus the one model
                       judgment, asked for only when the Belt has answered
    is_confirmation()  whether the Belt's reply confirms a read-back — a rule,
                       not a model: a reply that is anything more than a plain
                       yes is treated as a correction and judged again

WHERE THE STATUS COMES FROM — stored, never derived from a reply
    The statuses are stored in `PhaseState.field_status` (the input mapper
    seeds it from the case record each turn). Only code changes one, at turn
    end: `decide` returns the statuses after this turn, and the executor stores
    them. A position with every field in `artifacts` and no status recorded
    counts as confirmed — `artifacts` receives a value only on the Belt's
    confirmation.

    **The move record rides on the coach's reply** (`additional_kwargs`,
    `MOVE_RECORD_KEY`), owned by `core/conversation.py`, which round-trips it
    through the case blob's conversation.
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

#: The four statuses of ruling R5, in order. STORED in
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
#: ADR-0085 (G-169) — the read-back an upload turn makes of a file that covers the element (no judgment).
UPLOAD_READ_BACK_REASON = ("Decided in code (ADR-0085): the Belt's file {filename} covers every criterion of this "
                           "element. Read its values back — the answer so far is the file's — and ask the Belt "
                           "to confirm them.")
#: ADR-0094 decision 2 (DEF-208) — the read-back an upload turn makes of a file that covers the element only partly.
UPLOAD_DRAFT_REASON = ("Decided in code (ADR-0094): the Belt's file {filename} answers this element only partly — "
                       "still missing: {missing}. Read back what the file gives as a DRAFT, name what is missing, and "
                       "ask the Belt to add it or correct anything; nothing is stored until it is complete and "
                       "confirmed.")
REJECT_REASON = ("The team rejected the Define report and named this element to "
                 "change — their reason: {reason}. Show the Belt their current "
                 "words and ask what should change.")

#: The move record and last turn's quality feedback ride on the coach's reply
#: under `MOVE_RECORD_KEY` and `QUALITY_FEEDBACK_KEY` — owned by
#: `core/conversation.py`, which round-trips both through the case blob.

#: Plain-string fields whose read-back value is COMPOSED by the coach from the
#: Belt's answers rather than read back verbatim — the script composes the
#: problem statement from the 5W2H answers (position 4).
COMPOSED_FIELDS: frozenset[str] = frozenset({"problem_statement"})


# ══ the walk ═════════════════════════════════════════════════════════════════


def positions(phase: str) -> list[tuple[str, tuple[str, ...]]]:
    """`(field, fields captured at that position)`, in coached order.

    Define has its ordered walk and three fields captured inside a position
    (`schema._CAPTURED_INSIDE`: the CTQs at position 3, the 5W2H at 4,
    `metric_definitions` at 5). The other four phases expose tier SETS, not a
    walk, so they walk their gate list in `review_rows` order — Tier 1, then
    Tier 2 — the planner's ledger's order.
    """
    if phase == "define":
        return [(f, (f, *_CAPTURED_INSIDE.get(f, ()))) for f in DEFINE_FIELD_ORDER]
    return [(r["field"], (r["field"],)) for r in review_rows(phase, {})]


def _stored(artifacts: dict[str, Any], field: str) -> bool:
    if field == "process_map_sipoc":            # G-121: all six columns, or not stored
        from backend.phases.define.parse import missing_columns
        return not missing_columns(artifacts.get(field))
    return not is_empty_capture(artifacts.get(field))


def store_missing(fields: Any, artifacts: dict[str, Any], store: dict[str, Any]) -> list[str]:
    """G-163 — the ONE test of whether a read-back can complete its position: the fields a Confirm of
    `store` would still leave unstored, given what `artifacts` already holds. The Confirm refuses on it
    (below) and the executor never offers a Confirm on it (`nodes_common`), so the two cannot disagree."""
    merged = {**artifacts, **store}
    # ADR-0088 decision 6 (G-188): a value this read-back stores counts only with its required parts.
    from backend.phases.define.parse import missing_parts
    return [f for f in fields if not _stored(merged, f) or (f in store and missing_parts(f, store[f]))]


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
    """Last turn's quality feedback — the grader's verdict on
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
    """The Belt's latest message, as text (its content blocks joined)."""
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


#: ADR-0085 (G-169) — a Belt's message asking to use the uploaded file's values as read back.
_USE_FILE = re.compile(r"\b(use|take|go with|keep|accept)\b.{0,80}\b(file|upload|uploaded|csv|spreadsheet|"
                       r"list|as listed|attached|attachment)\b")
_FILE_CHANGE = re.compile(r"\b(but|except|however|change|changed|instead|without|apart from|remove|add|"
                          r"replace|update|wrong|missing|not)\b")
#: The parts of a message, split at clause breaks; each must ask to use the file or be a courtesy.
_CLAUSE = re.compile(r"[,;:!?]|\.(?=\s|$)|\s(?:and|then|also)\s")
_COURTESY = re.compile(r"^(please|thanks|thank you|thank you very much|cheers|yes|yes please|ok|okay|great|"
                       r"that's fine|that's right|that's correct|correct|perfect|as is|as it is)$")


def covering_upload(field: Optional[str], upload: Optional[dict[str, Any]]) -> Optional[dict[str, str]]:
    """ADR-0085 (G-169): {filename, value} when the upload this turn reads was checked against `field`
    and covers it — every criterion supported, nothing contradicted or missing — and gives its value.
    Otherwise None, and the upload turn stays as ADR-0074 made it (the file named, what it lacks)."""
    check = (upload or {}).get("element_check") or {}
    value = str(check.get("value") or "").strip()
    criteria = list(check.get("criteria") or [])
    if not field or check.get("element") != field or not value or not criteria:
        return None
    if any(c.get("result") != "supported" for c in criteria) or any(str(m).strip() for m in check.get("missing") or []):
        return None
    return {"filename": str((upload or {}).get("filename") or "the file"), "value": value}


def partial_upload(field: Optional[str], upload: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """ADR-0094 decision 2 (DEF-208, G-209): {filename, value, missing} when the upload this turn reads was checked
    against `field`, gives its value, and covers it only PARTLY — a criterion not supported, or something missing.
    None when it covers the element fully (`covering_upload`), gives no value, or was checked against another."""
    check = (upload or {}).get("element_check") or {}
    value = str(check.get("value") or "").strip()
    if not field or check.get("element") != field or not value or covering_upload(field, upload) is not None:
        return None
    missing = [str(m).strip() for m in check.get("missing") or [] if str(m).strip()]
    return {"filename": str((upload or {}).get("filename") or "the file"), "value": value, "missing": missing}


def uses_upload(text: str, pending: Optional[dict[str, Any]]) -> bool:
    """ADR-0085 (G-169): on a read-back of an uploaded file, "use the file" is a Confirm — a message whose
    every part either asks to use the file (or names it) or is a courtesy, and that changes nothing. Any
    other content ("use the file, sponsor is Jane") is an answer, judged as one."""
    filename = str((pending or {}).get("upload") or "").lower()
    if not filename:
        return False
    stem = filename.rsplit(".", 1)[0]
    t = " ".join((text or "").lower().replace("’", "'").replace(filename, " the file ").replace(stem, " the file ")
                 .split())
    if not t or _FILE_CHANGE.search(t):
        return False
    parts = [" ".join(re.sub(r"[^\w'\s]", " ", p).split()) for p in _CLAUSE.split(t)]
    parts = [p for p in parts if p]
    return bool(parts) and any(_USE_FILE.search(p) for p in parts) and \
        all(_USE_FILE.search(p) or _COURTESY.match(p) for p in parts)


#: DEF-209 (G-210) — a part of a message that only points at an uploaded file ("the team is in the attached file",
#: "see the uploaded spreadsheet", the upload turn's own "📎 team.csv").
_POINTS_AT_FILE = re.compile(r"^📎|\b(in|see|from|on|within)\b.{0,40}\b(the|my|our|this)\b.{0,20}\b(file|upload|"
                             r"uploaded|attachment|attached|spreadsheet|csv|excel|sheet|list|document)\b")
#: The reason a message that only points at a file is answered without a judgment.
POINTS_AT_FILE_REASON = ("decided in code (DEF-209): the message points at the uploaded file and gives no answer "
                         "of its own — it is not judged as a typed answer; the coach responds about the file")


def points_at_file(text: str) -> bool:
    """DEF-209 (G-210): every part of the message either points at an uploaded file or is a courtesy — nothing
    in it is an answer of its own, so it is never judged as a typed answer."""
    t = " ".join((text or "").lower().replace("’", "'").split())
    if not t:
        return False
    if t.startswith("📎"):
        return True
    parts = [" ".join(re.sub(r"[^\w'\s]", " ", p).split()) for p in _CLAUSE.split(t)]
    parts = [p for p in parts if p]
    return bool(parts) and any(_POINTS_AT_FILE.search(p) for p in parts) and \
        all(_POINTS_AT_FILE.search(p) or _COURTESY.match(p) for p in parts)


#: ADR-0086 (A8) — the positions a confirmed goal can fill: its target value and its target date.
GOAL_FIELDS: tuple[str, ...] = ("target_value", "target_date")


def from_goal(phase: str, nxt: Optional[tuple[str, Any]], artifacts: dict[str, Any]) -> Optional[dict[str, Any]]:
    """ADR-0086 (A8): the read-back the next position starts with when the confirmed
    goal states it — for the target value, the value (and the date, when the goal gives one and none is
    stored), for the target date, the date; parsed in code (`parse.goal_targets`). None when the goal
    does not state it: the position is taught as usual."""
    if phase != "define" or not nxt or nxt[0] not in GOAL_FIELDS:
        return None
    goal = artifacts.get("goal_statement")
    if not isinstance(goal, str) or not goal.strip():
        return None
    from backend.phases.define import parse
    found = parse.goal_targets(goal, artifacts)
    store: dict[str, Any] = {}
    if nxt[0] == "target_value":
        if found["target_value"] is None:
            return None
        store["target_value"] = found["target_value"]
        if found["target_date"] and not artifacts.get("target_date"):
            store["target_date"] = found["target_date"]
    elif found["target_date"]:
        store["target_date"] = found["target_date"]
    else:
        return None
    return {"field": nxt[0], "fields": list(store), "belt_words": goal.strip(), "messages": 1,
            "from_goal": True, "store": store, "proposed": dict(store), "sources": {f: "typed" for f in store}}


def from_offer(phase: str, nxt: Optional[tuple[str, Any]], field_status: dict[str, dict[str, Any]],
               artifacts: dict[str, Any]) -> Optional[dict[str, Any]]:
    """DEF-098 (R15, G-196; ADR-0002): the read-back the next position starts with when an earlier answer gave a
    value for it — the coach captured it then (`field_status[field]["offered"]`), nothing was stored. It is read
    back for one Confirm, which stores it as any read-back does (`pending_store`); None when nothing was offered."""
    if not nxt:
        return None
    field = nxt[0]
    offered = ((field_status.get(field) or {}).get("offered") or {})
    value = offered.get("value")
    if value in (None, "", [], {}):
        return None
    words = value.strip() if isinstance(value, str) else str(offered.get("words") or "")
    proposed: dict[str, Any] = {field: value}
    pending: dict[str, Any] = {"field": field, "fields": list(nxt[1] or (field,)), "belt_words": words,
                               "messages": 1, "from_offer": True, "proposed": proposed, "sources": {field: "typed"}}
    pending["store"] = pending_store(phase, pending, dict(proposed), artifacts)
    return pending


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
    `artifacts` with no status recorded (an older case) counts as confirmed —
    nothing reaches `artifacts` any other way."""
    entry = field_status.get(field) or {}
    if entry.get("status") in STATUSES:
        return str(entry["status"])
    fields = dict(positions(phase)).get(field, (field,))
    return CONFIRMED if all(_stored(artifacts, f) for f in fields) else NOT_TAUGHT


def field_statuses(phase: str, artifacts: dict[str, Any],
                   field_status: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Every position's stored status (ruling R5)."""
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
        out.update(pending.get("store") or pending.get("proposed") or {})      # read-back = Gate: the store first
    return {f: v for f, v in out.items() if not is_empty_capture(v)}


def _earlier_kw(entry: dict[str, Any], pending: Optional[dict[str, Any]]) -> dict[str, Any]:
    """`{"earlier": …}` when there is anything to carry, else nothing."""
    e = _earlier(entry, pending)
    return {"earlier": e} if e else {}


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


def _spans_kw(phase: str, field: str, judgment: Any, answer: str) -> dict[str, Any]:
    """ADR-0093 decision 5 (option (b)): the judgment's quoted span per criterion, kept only where it is a
    verbatim substring of the Belt's answer (`templates.verbatim_spans`) — `{"spans": …}` whenever the judgment
    quoted at least one criterion, even if no quote held (DEF-263: the free-text rows are then met only with words of
    their own); nothing for a judgment that quoted nothing."""
    if phase != "define":
        return {}
    from backend.phases.define.templates import verbatim_spans
    quoted = getattr(judgment, "criterion_spans", None)
    return {"spans": verbatim_spans(quoted, field, answer)} if quoted else {}


def _confirmed(pending: dict[str, Any]) -> dict[str, Any]:
    """A confirmed element's status, with what its Gate rows read (ADR-0093 decision 7): the verified spans and
    the file its values came from."""
    return {"status": CONFIRMED, **({"spans": pending["spans"]} if isinstance(pending.get("spans"), dict) else {}),
            **({"upload": pending["upload"]} if pending.get("upload") else {})}


def criteria_open(phase: str, field: str, values: dict[str, Any], pending: dict[str, Any]) -> list[str]:
    """ADR-0093 decision 2: `[field]` when the read-back's rows, recomputed from what a Confirm would store, leave a
    required criterion open — the Confirm is refused and nothing stored; [] otherwise."""
    if phase != "define":
        return []
    from backend.phases.define.templates import open_required
    return [field] if open_required(field, values, spans=pending.get("spans")) else []


def _attempts(entry: dict[str, Any]) -> dict[str, Any]:
    """The failed-attempt count an element's entry carries forward (ADR-0072)."""
    n = int(entry.get("attempts") or 0)
    return {"attempts": n} if n else {}


def _join(*parts: str) -> str:
    return chr(10).join(p for p in (s.strip() for s in parts) if p)


#: R-G (founder ruling 2026-10-27): the SIPOC is collected in four short guided parts, in the BB manual's order — the
#: main steps; outputs and customers; inputs and suppliers; each step's time and problems, and how often the process
#: runs — each asked by its own card, in code; one read-back and one Confirm at the end.
SIPOC_FIELD, SIPOC_PARTS = "process_map_sipoc", 4
SIPOC_PART_REASON = "R-G: the SIPOC's part {part} of 4 is asked by its card, in code."


def sipoc_parts_covered(words: str, answered: list[int]) -> set[int]:
    """The SIPOC parts `words` gives: each part the Belt answered, and each part its labelled columns cover (a whole
    SIPOC pasted at once) — the steps; outputs and customers; inputs and suppliers; the step times."""
    from backend.phases.define.parse import has_step_times, parse_sipoc
    cols = set(parse_sipoc(words))
    covered = set(answered)
    for part, needs in ((1, {"process_steps"}), (2, {"outputs", "customers"}), (3, {"inputs", "suppliers"})):
        if needs <= cols:
            covered.add(part)
    if has_step_times(words):
        covered.add(4)
    return covered


def _sipoc_part(phase: str, field: str, entry: dict[str, Any], belt: str) -> Optional[dict[str, Any]]:
    """R-G: while the SIPOC is being collected (its entry names the part asked), the entry after the Belt's answer when
    a part is still to be asked — the answer joined, the part answered recorded, the next part named — else None: all
    four are given and the whole answer is judged as one."""
    if phase != "define" or field != SIPOC_FIELD or not entry.get("part") or belt.strip().endswith("?"):
        return None                     # a question is never a part's answer: the judgment decides it (a respond)
    answered = [*(entry.get("parts_answered") or []), int(entry["part"])]
    words = _join(str(entry.get("answer") or ""), belt)
    covered = sipoc_parts_covered(words, answered)
    nxt = next((p for p in range(1, SIPOC_PARTS + 1) if p not in covered), None)
    if nxt is None:
        return None
    texts = {**dict(entry.get("parts_text") or {}), str(entry["part"]): belt}
    return {**entry, "status": ASKED, "answer": words, "messages": int(entry.get("messages") or 0) + 1, "part": nxt,
            "parts_answered": answered, "parts_text": texts}


def _upload_kw(*sources: Optional[dict[str, Any]]) -> dict[str, Any]:
    """G-301 (DEF-264, founder test 2026-10-27 #28): the uploaded file an element's answer started from, carried
    through a Change and the Belt's typed additions — a Confirm then still stores the file's own rows, never the
    coach's re-typing of them. `{"upload": filename}` from the first source that names one, else nothing."""
    return next(({"upload": s["upload"]} for s in sources if s and s.get("upload")), {})


async def decide(phase: str, artifacts: dict[str, Any],
                 field_status: dict[str, dict[str, Any]], belt: str,
                 judge: Judge, action: Optional[str] = None,
                 element: Optional[str] = None, upload: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """THE MOVE, from the STORED status (rulings R4 and R5), and
    the statuses AFTER this turn — which the executor stores at turn end.

    `judge(field, answer_so_far, latest, reading_back)` is the planner's one
    model judgment, called only for an answer: never on a field not taught,
    never on a Confirm or Change click, never on a plain typed yes.
    """
    after = {f: dict(v) for f, v in field_status.items()}
    base: dict[str, Any] = {"judgment": None, "answer": "", "messages": 0, "pending": None,
            "store": {}, "stored_field": None, "reason": "", "confirmed": None}

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
            from backend.phases.define.templates import plain   # G-260: one way to flatten a value
            words = plain(artifacts.get(element))
            after[element] = {"status": ASKED, "answer": words, "messages": 1, "picked": True}
            return done(element, fields, status, CHALLENGE, answer=words, messages=1,
                        reason=REVISE_REASON.format(field=element))
        if status == PARKED:
            # G-167: a return teaches the element again from the start (ADR-0072 point 4) — the attempts
            # before the park are not part of the next answer.
            after[element] = {"status": ASKED, "returned": True, "picked": True}
            return done(element, fields, status, TEACH, reason=RETURN_REASON.format(field=element))
        after[element] = {**entry, "status": entry.get("status") if entry.get("status") in (ASKED, ANSWERED)
                          else ASKED, "picked": True,
                          # R-G: a SIPOC picked before any answer is collected from its part 1 card.
                          **({"part": 1} if phase == "define" and element == SIPOC_FIELD
                             and not entry.get("answer") and not entry.get("part") else {})}
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
            # Nothing else is open: the parked element is the one left, taught again (G-167: afresh).
            after[field] = {"status": ASKED}
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
        # ADR-0072 point 4 — back to a parked element (every other one is confirmed); G-167: afresh.
        after[field] = {"status": ASKED, "returned": True}
        return done(field, fields, status, TEACH, reason=RETURN_REASON.format(field=field))

    if action == REJECTED:
        # R6 — back from a rejected report: the coach guides the Belt to the
        # element the team named, showing their current words. No judgment:
        # the Belt has not answered anything yet.
        reason = str((entry.get("rejected") or {}).get("reason") or "none given")
        return done(field, fields, status, CHALLENGE, answer=str(entry.get("answer") or ""),
                    messages=int(entry.get("messages") or 1),
                    reason=REJECT_REASON.format(reason=reason))

    # ADR-0085 (G-169) — the upload turn of a file that covers this element reads the file's values back,
    # decided in code (no judgment call); a Confirm, or "use the file", stores them on the path below.
    covered = covering_upload(field, upload) if action is None else None
    if covered is not None:
        words = covered["value"]
        new_pending = {"field": field, "fields": list(fields), "belt_words": words, "messages": 1,
                       "upload": covered["filename"], **_earlier_kw(entry, None)}
        after[field] = {"status": ANSWERED, "answer": words, "messages": 1, "pending": new_pending,
                        **_attempts(entry)}
        return done(field, fields, status, READ_BACK, answer=words, messages=1, pending=new_pending,
                    reason=UPLOAD_READ_BACK_REASON.format(filename=covered["filename"]))
    # ADR-0094 decision 2 (DEF-208): a file that covers the element only partly is read back as a DRAFT — its value
    # with the gaps named; the card marks what is open and keeps Confirm closed until the Belt completes it.
    partial = partial_upload(field, upload) if action is None else None
    if partial is not None:
        words = partial["value"]
        new_pending = {"field": field, "fields": list(fields), "belt_words": words, "messages": 1,
                       "upload": partial["filename"], "draft": True, "missing": partial["missing"],
                       **_earlier_kw(entry, None)}
        after[field] = {"status": ANSWERED, "answer": words, "messages": 1, "pending": new_pending,
                        **_attempts(entry)}
        return done(field, fields, status, READ_BACK, answer=words, messages=1, pending=new_pending,
                    reason=UPLOAD_DRAFT_REASON.format(filename=partial["filename"],
                                                      missing="; ".join(partial["missing"]) or "the open parts"))

    if status == NOT_TAUGHT and element == field and action is None and str(belt or "").strip():
        # R-A (DEF-267, founder test 2026-10-27 #9): the welcome showed this element's card, so the Belt's first message
        # answers it — judged as an answer, never met with the same card again.
        status, entry = ASKED, {"status": ASKED}
        after[field] = entry
    if status == NOT_TAUGHT:
        # R-G: the SIPOC is taught by its part 1 card; its answers are collected part by part.
        after[field] = {"status": ASKED, **({"part": 1} if phase == "define" and field == SIPOC_FIELD else {})}
        return done(field, fields, status, TEACH)

    pending = entry.get("pending") if status == ANSWERED else None
    if pending and (action == CONFIRM_CLICK or (action is None and (is_confirmation(belt)
                                                                     or uses_upload(belt, pending)))):
        store = dict(pending.get("store") or {})
        merged = {**artifacts, **store}
        # ADR-0093 decision 2: a Confirm with a required criterion open is refused on the server too.
        missing = store_missing(fields, artifacts, store) or criteria_open(phase, field, merged, pending)
        if missing:
            # A yes to a read-back that cannot complete the position (a
            # structure refused): nothing is stored, the read-back is made again.
            # DEF-029 / G-117: the reason names what was missing, so the coach's next read-back
            # carries it and the executor tells the Belt, in code, that nothing was stored.
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
        after[field] = _confirmed(pending)
        nxt = current(phase, merged, after)
        # ADR-0086 (A8) — a confirmed goal that states the target: the next position is read back from
        # it, for one Confirm; otherwise it is taught.
        # DEF-098 (R15): else a value an earlier answer gave for it, offered now for one Confirm.
        derived = from_goal(phase, nxt, merged) or from_offer(phase, nxt, after, merged)
        if nxt is not None and derived is not None:
            after[nxt[0]] = {"status": ANSWERED, "answer": derived["belt_words"], "messages": 1, "pending": derived}
        elif nxt is not None:
            after[nxt[0]] = {"status": ASKED}
        # R16 (DEF-021, DEF-082): what the change log needs from the read-back just confirmed — with ADR-0112's
        # mismatch, when one was told: the Belt confirming it keeps the answer, noted on its element's entry.
        return done(nxt[0] if nxt else None, nxt[1] if nxt else (), status, STORE_AND_ADVANCE,
                    store=store, stored_field=field,
                    confirmed={k: pending.get(k) for k in ("belt_words", "reasons", "sources", "field", "mismatch")})

    if pending and action == CHANGE_CLICK and (pending.get("from_goal") or pending.get("from_offer")):
        # ADR-0086 — a Change of the target read from the goal teaches the element as usual; DEF-098, the same
        # for a value offered from an earlier answer.
        after[field] = {"status": ASKED}
        return done(field, fields, status, TEACH)
    if pending and action == CHANGE_CLICK:
        words = str(pending.get("belt_words") or "")
        after[field] = {"status": ASKED, "answer": words, "messages": int(pending.get("messages") or 1),
                        **_attempts(entry), **_earlier_kw(entry, pending), **_upload_kw(pending)}
        return done(field, fields, status, CHALLENGE, answer=words,
                    messages=int(pending.get("messages") or 1), reason=CHANGE_REASON)
    if action == CHANGE_CLICK and not pending and str(entry.get("answer") or "").strip():
        # Wave 1's final slice (founder's flawed SIPOC, 2026-10-28): Change pressed under a read-back a Confirm could
        # not store (the short card, G-163) shows the answer to edit, as under any read-back — never judged as the
        # answer "Change".
        words = str(entry.get("answer") or "")
        return done(field, fields, status, CHALLENGE, answer=words,
                    messages=int(entry.get("messages") or 1), reason=CHANGE_REASON)

    collecting = _sipoc_part(phase, field, entry, belt) if action is None and not pending else None
    if collecting is not None:
        # R-G: the next SIPOC part is asked by its card — no judgment until all four are given.
        after[field] = collecting
        return done(field, fields, status, TEACH, reason=SIPOC_PART_REASON.format(part=collecting["part"]))
    previous = str((pending or {}).get("belt_words") or entry.get("answer") or "")
    so_far = int((pending or entry).get("messages") or 0)
    answer = _join(previous, belt)
    # DEF-209 (G-210): a message that only points at the uploaded file is not an answer — decided here, no judgment.
    judgment = (SufficiencyJudgment(verdict="not_an_answer", reason=POINTS_AT_FILE_REASON) if points_at_file(belt)
                else await judge(field, previous, belt, "yes" if pending else "no"))
    if judgment.verdict == "not_an_answer":
        return done(field, fields, status, RESPOND, judgment=judgment, answer=previous,
                    messages=so_far, pending=pending, reason=judgment.reason)
    if judgment.verdict == "sufficient":
        new_pending = {"field": field, "fields": list(fields), "belt_words": answer,
                       "messages": so_far + 1, **_earlier_kw(entry, pending),
                       **_spans_kw(phase, field, judgment, answer), **_upload_kw(pending, entry)}
        after[field] = {"status": ANSWERED, "answer": answer, "messages": so_far + 1,
                        "pending": new_pending, **_attempts(entry)}
        return done(field, fields, status, READ_BACK, judgment=judgment, answer=answer,
                    messages=so_far + 1, pending=new_pending)
    # ADR-0072 — an insufficient answer is a failed attempt; the third brings the offer to park.
    tries = int(entry.get("attempts") or 0) + 1
    after[field] = {"status": ASKED, "answer": answer, "messages": so_far + 1, "attempts": tries,
                    **_earlier_kw(entry, pending), **_upload_kw(pending, entry)}
    if tries >= PARK_AFTER:
        after[field]["offer_park"] = True
        return done(field, fields, status, OFFER_PARK, judgment=judgment, answer=answer,
                    messages=so_far + 1, reason=OFFER_PARK_REASON.format(field=field, n=tries))
    # R3 — the challenge NAMES the failed acceptance criterion.
    crit = getattr(judgment, "failed_criterion", None)
    reason = f"criterion `{crit}` — {judgment.reason}" if crit else judgment.reason
    return done(field, fields, status, CHALLENGE, judgment=judgment, answer=answer,
                messages=so_far + 1, reason=reason)


def _structured_store(phase: str, field: str, value: dict[str, Any], words: str,
                      artifacts: Optional[dict[str, Any]]) -> Any:
    """A structured capture as a Confirm stores it: the SIPOC (`_sipoc_store`); the benefits analysis with the soft
    benefits the Belt stated (ADR-0096 decision 1, DEF-260, founder test 2026-10-27 #52), read in code from the
    Belt's words — the live coach captured the four hard keys only and the soft benefit was lost."""
    if field == "process_map_sipoc":
        return _sipoc_store(phase, value, words, artifacts)
    if phase == "define" and field == "benefits_analysis":
        from backend.phases.define import parse
        soft = parse.soft_benefits(words)
        return {**value, "soft_benefits": soft} if soft else value
    return value


def _sipoc_store(phase: str, value: dict[str, Any], words: str, artifacts: Optional[dict[str, Any]]) -> Any:
    """The SIPOC a Confirm stores, from the coach's capture: ADR-0078 (DEF-084) — steps as entries with stable ids,
    their figures read in code. G-332 (DEF-259, founder test 2026-10-27 #60): when the Belt labelled the columns, a
    column the Belt did not label is not taken from the capture — the live coach wrote Outputs the Belt never gave, and
    the all-six check passed on them."""
    from backend.phases.define import parse
    if phase == "define" and len(labelled := parse.parse_sipoc(words)) >= 2:
        value = {k: v for k, v in value.items() if k not in parse.SIPOC_KEYS or k in labelled}
    return parse.sipoc_with_performance(value, (artifacts or {}).get("process_map_sipoc"))


def pending_store(phase: str, pending: dict[str, Any], proposed: dict[str, Any],
                  artifacts: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """What a confirmation of this read-back will store.

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
        dated = parse.calendar_date(value) if phase == "define" and f == "target_date" and isinstance(value, str) else None
        if dated:
            value = dated[0]                               # ADR-0088 decision 5: stored as an ISO date
        if phase == "define" and f == "problem_5w2h":
            # DEF-230 (ADR-0093): the seven answers as the Belt labelled them, read in code — the card's rows and
            # the stored value — the coach's proposal only for what the Belt did not label.
            value = parse.five_w_two_h_store(words, value) or value
        if phase == "define" and f in parse.TABLE_ELEMENTS and pending.get("upload") and parse.team_rows(words):
            # G-236 (DEF-229): a read-back of an uploaded table stores the file's rows, read in code from its
            # labelled lines (every column, training included) — never the coach's re-typing of them. G-301
            # (DEF-264): a training line the Belt typed to complete the file goes to each named member's own column.
            value = parse.uploaded_team(words, value)
        if phase == "define" and f == "critical_to_quality" and isinstance(value, list):
            # ADR-0088 decision 2: the rows as the Belt stated them, never a cross product.
            value = parse.ctq_rows(value)
        if isinstance(value, dict):
            value = _structured_store(phase, f, value, words, artifacts)
        verbatim =(f == field and one_message and f not in COMPOSED_FIELDS and not structured
                    and (value is None or isinstance(value, str)))
        if verbatim:
            store[f] = words
        elif value is not None and not is_empty_capture(value) and not (structured and isinstance(value, str)):
            store[f] = value
    return store


__all__ = [
    "MOVES", "STATUSES", "OFFER_PARK", "PARKED", "PARK_CLICK", "TRY_AGAIN_CLICK", "PARK_AFTER",
    "parked", "park_events", "element_rows", "criteria_open", "REVISE_CLICK", "CONFIRM_INCOMPLETE", "COLUMNS_MISSING", "TEACH", "CHALLENGE", "READ_BACK", "STORE_AND_ADVANCE", "RESPOND",
    "NOT_TAUGHT", "ASKED", "ANSWERED", "CONFIRMED", "CONFIRM_CLICK", "CHANGE_CLICK", "REJECTED",
    "MOVE_RECORD_KEY", "QUALITY_FEEDBACK_KEY", "COMPOSED_FIELDS", "positions", "focus",
    "current", "status_of", "last_record", "last_feedback", "belt_message",
    "is_confirmation", "field_statuses", "decide", "pending_store",
]
