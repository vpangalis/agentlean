from __future__ import annotations

import asyncio
from collections import deque
import time
import json
import logging
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException, Request, Response, UploadFile, File, Form
from langchain_core.messages import AIMessage, HumanMessage

from backend.core import conversation, pii
from backend.core.prompts import PII_HIDDEN_UPLOAD, TURN_DEADLINE_REPLY
from backend.core.request_context import set_case_id, set_phase
from backend.core.errors import CaseBusyError, StateSchemaVersionError
from backend.core.graph import RECURSION_LIMIT
from backend.gateway.schemas import (
    CaseCreateRequest,
    CaseCreateResponse,
    AskRequest,
    AskResponse,
    CapturedField,
    CitationOut,
    GateStatus,
    GateSubmitRequest,
    GateSubmitResponse,
    RegistryEntryOut,
    HealthResponse,
    UploadMetaRequest,
)
from backend.gateway.schemas import GateReviewField, GateReviewResponse
from backend.gateway import access
from backend.gateway.schemas import (CodeIssued, LeadHandover, PeopleResponse, PersonChange, PersonOut, PersonRemoval,
                                     SessionOut, SignInIn, SignInInfo)
from backend.gateway.schemas import GateDecisionRequest, GateDecisionResponse
from backend.gateway.schemas import SummariseRequest, SummariseResponse
from backend.core.store import get_store
from backend.core.substate import merge_field_log, split_captures
from backend.phases.gate_registry import (
    GATE_SPECS,
    review_rows,
    split_by_declared_type,
)
from backend.phases.define.report import define_report, element_of
from backend.phases.define.schema import DEFINE_FIELD_ORDER
from backend.phases.mappers_common import PHASE_ORDER, asks_for_phase, read_case_record
from backend.storage import blob
from backend.storage.models import CaseDocument, UploadRecord
from backend.upload.agent import process_upload
from backend.upload.classifier import EVIDENCE as CLASSIFIER_EVIDENCE
from backend.upload.asks import (
    check_shape,
    content_digest,
    open_ask_for_role,
)

#: Purpose label → §23.2.1 role, for an upload nobody asked for. **Not a
#: filename heuristic** — the purpose is what the Belt declared, and AP2.2
#: forbids inferring identity from a filename. Anything unrecognised falls to
#: the vocabulary's own catch-all, which is what those two rows exist for.
_PURPOSE_TO_ROLE = {
    "Process map": "as-is process map",
    "Data file": "baseline defect data",
    "Survey data": "voice-of-customer data",
    "Capability report": "capability study data",
    "Analysis": "root cause analysis",
    "Improvement plan": "improvement proposal",
    "Project document": "other artefact",
}


#: T93 (ADR-0067) — upload limits, in MB.
UPLOAD_NOTICE_MB = 5
UPLOAD_MAX_MB = 25
#: T93 — at most this many turns a minute from one person.
TURNS_PER_MINUTE = 10
#: T93 — each person's turn times in the last minute (this process).
_TURNS: dict[str, deque] = {}


def _over_turn_rate(person: str) -> bool:
    """T93: the 11th turn inside a minute from one person is refused; the turn is not counted."""
    now = time.monotonic()
    turns = _TURNS.setdefault(person or "", deque())
    while turns and now - turns[0] > 60:
        turns.popleft()
    if len(turns) >= TURNS_PER_MINUTE:
        return True
    turns.append(now)
    return False


def _role_from_purpose(purpose: str) -> str:
    return _PURPOSE_TO_ROLE.get(purpose, "other evidence")

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """W16 (DEF-113): reachable (this answer) and ready — storage configured and every required credential set. No
    model call: the page asks it when a case opens, before the first message."""
    from backend.core import config
    gaps = [] if blob.storage_configured() else ["case storage is not configured"]
    missing = config.missing_credentials()
    if missing:
        gaps.append("missing settings: " + ", ".join(missing))
    return HealthResponse(ready=not gaps, reason="; ".join(gaps))


@router.post("/summarise", response_model=SummariseResponse)
async def summarise_session(request: SummariseRequest) -> SummariseResponse:
    """Generate a 2-3 sentence AI summary of a session's conversation turns. G-262 (audit A4): the dialogue comes from
    the browser, so it is screened by the input guard's own check before any model reads it; the prompt is
    core/prompts.py's."""
    from backend.core import guard, llm
    from backend.core.prompts import SESSION_SUMMARY_PROMPT, SESSION_SUMMARY_SYSTEM, SESSION_SUMMARY_UNAVAILABLE
    from langchain_core.messages import HumanMessage, SystemMessage

    dialogue = "\n\n".join(
        f"{'AI Guide' if t.role in ('ai', 'assistant') else (t.user or 'Team member')}: {t.text}"
        for t in request.turns
    )
    verdict = await guard.screen(dialogue)
    if verdict["status"] != "passed":
        logger.warning("summarise_session(): the dialogue was not screened clean (%s, %s) — no model call",
                       verdict.get("threat"), verdict.get("rule"))
        return SummariseResponse(summary=SESSION_SUMMARY_UNAVAILABLE)
    prompt = SESSION_SUMMARY_PROMPT.format(phase=request.phase.upper(), title=request.case_title, dialogue=dialogue)
    try:
        response = await llm.get_llm(role="summarizer").ainvoke(
            [SystemMessage(content=SESSION_SUMMARY_SYSTEM), HumanMessage(content=prompt)]
        )
        summary = llm.block_text(response)
    except Exception:  # noqa: BLE001 — a summary that fails is said so in the History tab, never an error page
        logger.exception("summarise_session() failed")
        summary = SESSION_SUMMARY_UNAVAILABLE

    return SummariseResponse(summary=summary)


#: ADR-0090: said when a person is given without a full name.
PERSON_NEEDS_NAME = "Please give {who}'s full name — the case needs it to show who is on the team."
#: ADR-0090 / R8b: only the project lead changes the team.
TEAM_LEAD_ONLY = "Only the project lead, {lead}, can change the team."

#: ADR-0092 decision 2: a clash draws a new number up to this many times; one more is a readable error (W10).
CASE_NUMBER_REDRAWS = 5
CASE_NUMBER_EXHAUSTED = ("The case could not be created: no free case number was found. Nothing was saved — "
                         "please try again.")


@router.post("/cases", response_model=CaseCreateResponse)
async def create_case(request: CaseCreateRequest, response: Response) -> CaseCreateResponse:
    """Create a new improvement case and register it.

    ADR-0092 "Unique case numbers and a safe case list": the number is reserved by a create-only-if-absent
    write and redrawn on a clash, up to five times; a sixth clash is a readable error (W10). The case list
    is then updated by a conditional write. Existing case numbers never change (ruling a)."""
    from datetime import datetime, timezone

    from backend.core.errors import CaseNumberTaken

    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")
    year = datetime.now(timezone.utc).year
    people = _people_from_request(request)
    case = None
    for _ in range(1 + CASE_NUMBER_REDRAWS):
        case = CaseDocument.new(
            case_id=blob.new_case_number(year),
            title=request.title,
            belt_level=request.belt_level,
            leader=people[0].full_name,                      # ADR-0090 decision 4: the lead's one name
            department=request.department,
            target_date=request.target_date,
            team=[],
            people=people,
        )
        try:
            await blob.create_case(case)
            break
        except CaseNumberTaken:
            logger.warning("create_case: number %s already taken — drawing another (ADR-0092)", case.case_id)
            case = None
    if case is None:
        raise HTTPException(503, CASE_NUMBER_EXHAUSTED)
    case_id = case.case_id
    await blob.register_case(case)
    head = case.people[0]
    if head.email:                    # ADR-0091 decision 1: the creator is not asked again on this browser
        access.set_session(response, case_id, head.email)
    # WATCH 19's writer, at the site the watch names (step 6.8). §9: the Store's
    # `case` namespace is a session-start COPY so that boundary mappers depend
    # on `BaseStore` alone; the blob above stays the system of record.
    _ensure_case_record(case)
    return CaseCreateResponse(case_id=case_id, title=request.title)


def _person(p: Any, *, role: str = "", status: str = "member", by: str = "") -> Any:
    """ADR-0090: a PersonRecord from the form's or the panel's PersonIn; the location defaults to "not set"."""
    from datetime import datetime, timezone

    from backend.storage.models import PersonLocation, PersonRecord
    loc = dict(p.location or {})
    return PersonRecord(full_name=p.full_name.strip(), email=p.email.strip(), role=(role or p.role).strip(),
                        function=p.function.strip(), department=p.department.strip(),
                        location=PersonLocation(country=str(loc.get("country") or ""), site=str(loc.get("site") or "")),
                        status=status, added_by=by,
                        added_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))


def _people_from_request(request: CaseCreateRequest) -> list:
    """ADR-0090 decision 1: the creator is the project lead (from `lead`, else the typed `leader`), then the
    members (from `people`, else `team`). Full name required for everyone, a role for every member; the e-mail
    is not required at creation (ruling a). Refused in plain words, nothing created."""
    from backend.gateway.schemas import PersonIn as _In
    from backend.storage import people as people_mod
    from backend.storage.models import PROJECT_LEAD
    lead_in = request.lead or _In(full_name=request.leader)
    if not lead_in.full_name.strip():
        raise HTTPException(422, PERSON_NEEDS_NAME.format(who="the project lead"))
    out = [_person(lead_in, role=PROJECT_LEAD, by=lead_in.full_name)]
    members = request.people or [_In(full_name=str(m.get("name") or ""), role=str(m.get("role") or ""))
                                 for m in request.team]
    for m in members:
        if not m.full_name.strip() and not m.role.strip():
            continue
        try:
            out = people_mod.add(out, _person(m, by=lead_in.full_name))
        except ValueError as e:
            raise HTTPException(422, f"{m.full_name or 'A team member'}: {e}.")
    return out


def _ensure_case_record(case: CaseDocument) -> None:
    """Copy the case's framing fields into the Store — WATCH 19, both halves.

    **Called at creation AND on every turn.** `write_case_record` is idempotent
    by key, so the second call is a cheap overwrite rather than a branch, and
    that is deliberate: a branch that checked "does it exist yet" would be one
    more place for the record to be silently absent. WATCH 19 named exactly
    these two sites — *"the write belongs at case creation (`POST /cases`) and,
    for cases that predate it, lazily on first read"* — and every case in the
    registry today predates it.

    **Failure here must not fail the turn.** The Store is a copy; the blob is
    the system of record. A Store write that fails leaves the mapper on its
    labelled fallbacks, which now says so loudly rather than silently.
    """
    from backend.core.store import get_store
    from backend.phases.mappers_common import (
        case_record_from_document, write_case_record,
    )

    record = case_record_from_document(case)
    try:
        write_case_record(get_store(), case.case_id, record)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "case record NOT written to the Store for %s (%s: %s) — the "
            "coach will be framed with placeholder prose this turn. The blob "
            "case document is unaffected; this is the §9 copy.",
            case.case_id, type(exc).__name__, exc,
        )


class ClientGone(Exception):
    """The Belt's client disconnected before the turn finished (§47 ABANDON)."""


async def _until_disconnect(http: Request) -> None:
    """Return as soon as the client is gone. Blocks forever otherwise.

    ⚠ **`Request.is_disconnected()` DOES NOT WORK FOR THIS, and polling it is
    the obvious wrong answer.** It was tried first and verified not to fire:
    the client went, the poll kept returning `False`, and the turn ran to
    completion exactly as it had with a plain inline `await`.

    The reason is in uvicorn's own `receive()` (read from the installed
    0.29.0, `protocols/http/httptools_impl.py`), which does two things in
    order — `self.flow.resume_reading()`, then `await self.message_event.wait()`
    — and only then reports `http.disconnect`. **Starlette's
    `is_disconnected()` wraps that call in an immediately-cancelled
    `CancelScope`**, so the resume happens and the wait is torn down in the
    same tick: the socket read is re-armed and nothing ever waits for the
    protocol to deliver the EOF. Polling it in a loop just re-arms the read
    forever.

    Awaiting the raw ASGI `receive()` does both halves. It parks until uvicorn
    has a message, and uvicorn sets `message_event` on `connection_lost` — so
    this returns on the disconnect itself rather than on a timer, and there is
    no poll interval to tune.

    The loop is not decoration: a client that keeps the connection open may
    send further `http.request` frames, and those must be consumed and ignored
    rather than mistaken for a disconnect.
    """
    while True:
        message = await http.receive()
        if message["type"] == "http.disconnect":
            return


# `state` is the graph input: a state dict for a turn, or `Command(resume=...)`
# when `decide_gate` resumes the Define pause — hence `Any`, not `dict`.
#: DEF-093 / G-157 (founder ruling 2026-10-12, option B; ADR-0080): the coaching turn's limit, counted from
#: `turn_started` (stamped by `_graph_config`), less the closing reserve — both owned by `core/config.py`.
#: LangGraph has no whole-run deadline (per node `TimeoutPolicy`, per superstep `step_timeout` only —
#: checked 2026-10-12), so the route bounds the run itself.
from backend.core.config import TURN_CLOSE_RESERVE_S, TURN_LIMIT_S  # noqa: E402


class TurnDeadline(Exception):
    """The coaching turn reached its deadline; the run was cancelled (DEF-093)."""


async def _run_turn(graph, state: Any, config: dict, http: Request, deadline: bool = False):
    """Run one turn, ABANDONING it if the client goes first (§47 req 1).

    ═══════════════════════════════════════════════════════════════════════
    WHY A RACE, AND NOT THE INLINE `await` THIS ORIGINALLY SHIPPED WITH
    ═══════════════════════════════════════════════════════════════════════
    Step 4.2 first shipped a plain `await graph.ainvoke(...)`, commented as the
    deliberate ABANDON shape on the reasoning that the run is the handler's own
    task and therefore dies with the client. **That reasoning is wrong on this
    stack, and the step's own `azure-query` verification disproved it**:
    a client killed 3s into a 30s turn left the turn running, and it completed
    5s later, wrote 12 checkpoint blobs across the parent and the subgraph
    namespace, and appended two turns to the case blob. **The Belt saw nothing
    and the checkpoint says the turn happened** — §47's opening finding, word
    for word.

    **Starlette does not cancel an endpoint coroutine on disconnect.** Verified
    against the installed starlette 0.50.0 / uvicorn 0.29.0, not assumed: the
    server notes the disconnect on the receive channel, and a handler that
    never awaits `receive()` is never notified, so it runs to completion. Only
    a streaming response (whose generator is closed) or an explicit
    `is_disconnected()` poll observes it.

    So the shape §47 requires for a non-streaming handler is this one: run the
    graph as a task, watch the connection alongside it, and **`cancel()` the
    task the moment the client is gone**. It is `t.cancel()` — §47's own
    prescription — with an `is_disconnected()` poll standing in for the
    streaming generator's `finally`. **This is NOT `asyncio.create_task` with
    no disconnect handling**, which §47 bans; the disconnect handling is the
    entire point of the function.

    **It does not build streaming.** `/ask/stream` (§49) is still step 10.1's,
    and when it lands its `gen()` must make this same choice explicitly in its
    own `finally` rather than inherit this one.

    **What ABANDON actually guarantees, stated precisely.** Cancellation lands
    at the next `await` inside the graph, so an in-flight Azure OpenAI call is
    abandoned rather than un-sent, and LangGraph may already have checkpointed
    the nodes that completed BEFORE the disconnect. The guarantee is that **no
    node runs, and no checkpoint is written, after the client is gone** — not
    that the turn leaves no trace. A partially-executed turn is exactly what
    resuming from `latest.json` is for. What it prevents is the whole turn
    completing, and the case blob being written, behind a Belt who left.
    """
    # T11 (DEF-115, ADR-0018): one writer per thread_id at a time — the case's Blob lease is held for
    # the whole run; a second writer is told, in plain words, and nothing of its turn runs.
    thread_id = str(((config or {}).get("configurable") or {}).get("thread_id") or "")
    try:
        async with blob.case_lease(thread_id):
            return await _run_turn_held(graph, state, config, http, deadline)
    except CaseBusyError:
        raise HTTPException(409, CASE_BUSY)


#: T11 (DEF-115) — said to a second person whose turn arrives while the case's lease is held.
CASE_BUSY = ("Someone else on the team is working on this case right now. Wait a moment and send "
             "your message again — nothing of yours was lost.")


def _bind(case_id: Any, phase: Any) -> None:
    """T43 (DEF-129): the request's case and phase into the logging context — every log line of the
    request, the graph's nodes included (they run in tasks that inherit it), names them."""
    set_case_id(str(case_id) if case_id else None)
    set_phase(str(phase) if phase else None)


#: DEF-219 (founder ruling 2026-10-22 evening, item 2b; ADR-0043): LangGraph's own durability mode for every run of
#: the graph — a turn and a gate resume. The installed LangGraph's modes: "sync", "async" (its default), "exit".
GRAPH_DURABILITY: Literal["sync", "async", "exit"] = "async"


async def _run_turn_held(graph, state: Any, config: dict, http: Request, deadline: bool = False):
    """`_run_turn`'s body, inside the case's lease. With `deadline` (a coaching turn, DEF-093), the run is
    cancelled — exactly as a disconnect cancels it — when the turn's 45 s, less the closing reserve, are
    spent: `TurnDeadline`."""
    task = asyncio.create_task(graph.ainvoke(state, config=config, durability=GRAPH_DURABILITY))
    watch = asyncio.create_task(_until_disconnect(http))
    left = None
    if deadline:
        started = float(((config or {}).get("configurable") or {}).get("turn_started") or time.time())
        left = max(0.0, started + TURN_LIMIT_S - TURN_CLOSE_RESERVE_S - time.time())
    try:
        done, _ = await asyncio.wait(
            {task, watch}, timeout=left, return_when=asyncio.FIRST_COMPLETED
        )
        if task not in done:
            task.cancel()
            # Awaited so the cancellation is delivered and the task is truly
            # finished before the handler returns; without this the run can
            # survive the response and keep checkpointing, which is the whole
            # defect this function exists to fix.
            try:
                await task
            except asyncio.CancelledError:
                pass
            if watch not in done:
                raise TurnDeadline()
            raise ClientGone()
        return task.result()
    finally:
        watch.cancel()
        try:
            await watch
        except asyncio.CancelledError:
            pass


# ── the graph boundary ────────────────────────────────────────────────────
#
# §1.1 and §49: the compiled graph is the ONLY runtime path, and a route that
# does anything beyond `await graph.ainvoke(...)` plus envelope marshalling is
# a violation. Everything between here and `/gate` is that marshalling.



def _mirror_asks(case_id: str, phase: str, result: Any) -> None:
    """Copy this turn's `asks` into the Store, for the upload route to read.

    **The upload route cannot read `PhaseState`** — it has the case blob and
    the Store, not the checkpoint. An ask is created by the planner during a
    coaching turn and must be resolvable by a file arriving moments later, so
    something has to carry it across. This is that something, and it runs
    AFTER the turn rather than during it.

    **Same mechanism `uploads` already uses in the other direction** (step
    6.11): the Store's `case` record is the one thing both a mapper and a route
    can see. A second namespace would need a second writer that the existing
    backfill could not keep current.

    **Fails soft.** The Store is a copy; the checkpoint holds the real asks. A
    failed mirror costs the next upload its ask binding, which degrades to
    `shape_match="unsolicited"` — honest, and not a lost file.
    """
    asks = list((result or {}).get("asks") or [])
    if not asks:
        return
    from backend.phases.mappers_common import write_asks
    try:
        write_asks(get_store(), case_id, phase, asks)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "asks NOT mirrored to the Store for %s/%s (%s: %s) — an upload "
            "arriving before the next turn will not resolve to an ask and "
            "will be recorded as unsolicited. The checkpoint is unaffected.",
            case_id, phase, type(exc).__name__, exc,
        )


async def _with_unfinished_work(case: CaseDocument, at: Optional[str] = None,
                                lost: Optional[list[str]] = None) -> CaseDocument:
    """The case as the Belt sees it — ADR-0066. The blob holds what is decided (framing,
    uploads, approved records); the checkpoint holds the unfinished work. This returns a COPY
    of the blob's case with, read through the compiled graph, the conversation and every open
    phase's record (captured values, statuses, log) from the checkpoint. The copy is for reading:
    no route writes it back, so the blob never holds unfinished work.

    `at` (a checkpoint id) reads the case as it was reloaded at that checkpoint — every phase record the
    checkpoint holds, whatever the blob has since approved. No route passes it; the capability rows
    use it to read a case as it stood before its approval (DEF-064, founder 2026-10-15).

    G-261 (audit W3): when the checkpoint cannot be read the blob copy is shown, and `lost` (when given) receives the
    case id, so the route tells the Belt that the work since the last confirmed answer was not kept."""
    from backend.core.graph import get_graph
    from backend.phases import record as phase_record
    out = case.model_copy(deep=True)
    config: dict[str, Any] = {"configurable": {"thread_id": case.case_id}}
    if at:
        config["configurable"]["checkpoint_id"] = at
    try:
        snapshot = await get_graph().aget_state(config)  # type: ignore[arg-type]
    except Exception as exc:  # noqa: BLE001 — a reload must render; the blob copy is the floor, and it is told
        logger.warning("case %s: the checkpoint could not be read (%s); showing the blob", case.case_id, exc)
        if lost is not None:
            lost.append(case.case_id)
        return out
    messages = list((snapshot.values or {}).get("messages") or [])
    if not messages:
        return out
    # What the Belt saw: their messages and the coach's replies — not the agent's tool calls
    # and tool results, which the checkpoint also holds.
    # ...and not a blocked turn: the guard's verdict is in step_log (ADR-0067).
    from backend.core.guard import without_blocked
    shown = [m for m in without_blocked(messages) if isinstance(m, HumanMessage)
             or (isinstance(m, AIMessage) and not getattr(m, "tool_calls", None) and str(m.content).strip()
                 and not (m.additional_kwargs or {}).get("gate_submission"))]
    out.conversation_history = [conversation.strip_transport(conversation.message_to_turn(m, i))
                                for i, m in enumerate(shown)]
    for phase, rec in phase_record.latest_by_phase(messages).items():
        held = out.phases.get(phase)
        if held is None or (held.gate_passed and not at):
            continue
        held.structured = dict(rec.get("structured") or {})
        held.field_status = {f: dict(v) for f, v in (rec.get("field_status") or {}).items()}
        held.field_log = [dict(e) for e in (rec.get("field_log") or [])]
        # G-148 (DEF-061) — the coach's citations from every turn, as the record keeps them.
        if rec.get("citations"):
            from backend.core.citations import as_records
            held.citations = as_records(rec["citations"])                 # G-176
    return out


def apply_capture(case: CaseDocument, phase: str, payload: dict[str, Any]) -> None:
    """Fold one turn's product into the case record — **MERGE, never replace**.

    ═══════════════════════════════════════════════════════════════════════
    STEP 6.33 — THE HALF OF G-78 THAT LIVED HERE
    ═══════════════════════════════════════════════════════════════════════
    This was four lines in `ask()`: build `clean` from THIS turn's extraction,
    then `case.phases[phase].structured = clean`. **An assignment, so every
    coached capture destroyed the ones before it** — a Belt filling Define's
    thirteen fields across a dozen turns arrived at the gate with one. Five
    turns, five fields, one survivor; the reproduction is in
    `test_capture_accumulates.py`.

    **It was invisible because the other half hid it.** The input mapper
    blanked `artifacts` every turn, so `clean` was usually empty, so
    `if clean` skipped the write and the prior value survived by accident.
    Fixing either half alone turns a silent no-op into silent data loss —
    which is why both land in one commit.

    **Extracted from the route body deliberately.** `ask()` needs a FastAPI
    request, a case blob and Azure; this needs a case document and a dict, so
    a test can drive five turns through the code that ships rather than
    through a copy of it. §49's "the route marshals the envelope and nothing
    else" is unchanged — this IS the marshalling, named.

    Silent about a phase the case has no record for, as the assignment's own
    `and request.phase in case.phases` guard was.
    """
    record = case.phases.get(phase)
    if record is None:
        return
    from backend.phases import record as phase_record
    prior = {"structured": record.structured, "field_status": record.field_status, "field_log": record.field_log}
    # DEF-219: a reply carries the record as what its turn changed — folded onto the case's record; a payload with
    # no record (an older caller) merges as before.
    merged = (phase_record.apply_delta({**phase_record.empty(phase), **prior}, payload[phase_record.KEY], phase)
              if isinstance(payload.get(phase_record.KEY), dict) else phase_record.merge(prior, payload, phase))
    record.structured = merged["structured"]
    record.field_status = merged["field_status"]
    record.field_log = merged["field_log"]


def _requested_phase(case: CaseDocument, requested: str) -> str:
    """The phase this turn runs, with the client's view checked against the record.

    **The case record wins, and a disagreement is refused rather than resolved.**
    `case.current_phase` is the system of record for which phase a project is in
    (§10.4) and is what seeds `SupervisorState.current_phase`; `request.phase` is
    what the UI believes. They are normally equal — the UI sets its phase from
    the case document and locks every later one.

    When they are not equal, silently preferring either is wrong in a way that
    does not surface: taking the request runs a phase the record does not agree
    the project is in, and taking the record coaches a phase the Belt did not
    ask about while `_graph_config` reads the REQUESTED phase's artifacts. That
    second combination is the one this function exists to stop — it would hand
    the Define subgraph Measure's captured fields, and every individual value
    would look valid.

    A completed project is the ordinary way to reach here: `current_phase` is
    `"complete"`, which is not a phase and has no subgraph.
    """
    if requested != case.current_phase:
        raise HTTPException(409, (
            f"Phase mismatch for {case.case_id}: the request asks for "
            f"{requested!r}, the case record is in {case.current_phase!r}. "
            f"The record is authoritative (§10.4); it is not overridden by a "
            f"request parameter."
        ))
    return requested


def _graph_config(case: CaseDocument, phase: str, user: str, entry: str,
                  started: float | None = None) -> dict:
    """The per-run config: `thread_id`, and the framing the v1 seam needs.

    **`thread_id` IS `case_id`** (§16) — never per phase, never concatenated.
    One `thread_id` per project is what lets two Belts on two projects share no
    state at any layer without a multi-tenancy mechanism being written.

    ⚠ **§47 REQUIREMENT 5 IS NOT MET, AND THIS IS THE LINE WHERE IT SHOWS.**
    `case_id` arrives from the request body. §47 requires it to be derived from
    the authenticated session, because `case_id` is the tenancy boundary and a
    client-supplied `thread_id` lets any caller resume any Belt's session. There
    is no auth layer to derive it from — §17 places that post-refactor — so it
    stays client-supplied for now and is carried as a WATCH rather than papered
    over with a check that cannot fail. **Do not read the presence of
    `thread_id` here as the requirement being satisfied.**

    `recursion_limit` is §16's backstop against a genuine infinite loop, NOT the
    per-turn hop budget — that is `RemainingSteps`, read inside the executor
    (§26). Fifty, per the step.

    The three seam keys — `current_user`, `case_metadata`, `v1_phase_inputs` —
    carry what `orchestrate_{phase}` needs and `PhaseState` may not declare
    (§56). They are deleted with the seam at 11.1; see
    `phases/nodes_common.py`.
    """
    return {
        "configurable": {
            "thread_id": case.case_id,
            "entry": entry,
            "current_user": user,
            # DEF-014 / ADR-0080: when the turn started — G-166 (founder ruling 2026-10-13): for a coaching
            # turn, the request's ARRIVAL (`started`), so the deadline covers the whole request as the Belt
            # experiences it, the case load and the unfinished-work read included.
            "turn_started": started if started is not None else time.time(),
            "case_metadata": {
                "title": case.title,
                "belt_level": case.belt_level,
                "leader": case.leader,
                "department": case.department,
            },
            # EVERY phase's captured fields, not just this turn's phase.
            # Measure seeds its metric confirmations from Define, and Analyse,
            # Improve and Control each build a cross-phase brief from the
            # phases before them (`nodes_common.to_v1_state`). Passing only the
            # current phase — which is all the Define-only seam needed before
            # step 4.4 — would leave every brief empty and every upstream fact
            # missing from the prompt, with no error anywhere.
            "v1_phase_inputs": {
                name: dict(record.structured or {})
                for name, record in case.phases.items()
            },
        },
        "recursion_limit": RECURSION_LIMIT,
    }


async def _graph_input(graph, config: dict, case: CaseDocument,
                       new_messages: list) -> dict:
    """What to hand `ainvoke`: the whole state on turn one, the delta after.

    **`SupervisorState.messages` reduces with `operator.add`** (§5), so a state
    update is APPENDED to what the checkpoint already holds. Passing the whole
    conversation every turn would duplicate it, and passing the whole state
    every turn would re-write `current_phase` from the route — exactly the
    second writer §5 B2 forbids, and exactly what the v1 eleven-field literal
    did on every request.

    So the seven fields are written **once**, when the thread has no checkpoint,
    and every later turn sends only the new message. The first-turn seed also
    carries the case document's existing conversation: a case created before 4.2
    has history in the case blob and nothing in the checkpoint, and dropping it
    would hand the coach a blank slate mid-project.

    **The two records of `current_phase` are checked against each other, and a
    disagreement is a 409 rather than a silent pick.** From the second turn on,
    `current_phase` comes from the checkpoint and the case document is not
    consulted for it — so if the two ever diverge, the graph would run one phase
    while the route reported another and read a third's artifacts. It can
    diverge: `write_phase_gate` advances `case.current_phase` on a gate pass,
    and the checkpoint's copy is written only by the output mapper, which 4.2
    does not call. Unreachable while the Define gate is inert (WATCH 7), and
    checked anyway, because the failure is silent and the check is two lines.
    """
    snapshot = await graph.aget_state(config)
    if snapshot.values:
        checkpointed = snapshot.values.get("current_phase")
        if checkpointed != case.current_phase:
            raise HTTPException(409, (
                f"Phase disagreement for {case.case_id}: the checkpoint says "
                f"{checkpointed!r}, the case record says "
                f"{case.current_phase!r}. `current_phase` has one writer (§5 "
                f"B2) and these are two records of it. Resolve before "
                f"continuing rather than letting the graph pick."
            ))
        return {"messages": new_messages}

    prior = [
        conversation.turn_to_message(t)
        for t in (case.conversation_history or [])
    ]
    return {
        "messages": prior + new_messages,
        "history": [],
        "case_id": case.case_id,
        "phase_index": (
            PHASE_ORDER.index(case.current_phase)
            if case.current_phase in PHASE_ORDER else 0
        ),
        "current_phase": case.current_phase,
        "gate_passed": {
            name: bool(record.gate_passed)
            for name, record in case.phases.items()
        },
        "final_output": None,
    }


def _last_ai(result: dict):
    """The coach's reply — the last AI message the run produced."""
    for msg in reversed(result.get("messages") or []):
        if isinstance(msg, AIMessage):
            return msg
    return None


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest, http: Request) -> AskResponse:
    """One coaching turn, through the compiled graph.

    ═══════════════════════════════════════════════════════════════════════
    §47 REQUIREMENT 1 — THE HANDLER SHAPE IS INLINE `await`, DELIBERATELY
    ═══════════════════════════════════════════════════════════════════════
    **This is a choice, not a default.** §47's finding is that once checkpoints
    write, the handler's control-flow shape — not the checkpointer — decides
    what survives a client disconnect, and that *a handler which has not chosen
    has chosen COMPLETE by accident*. The two permitted shapes are inline
    `await` and an explicit ABANDON policy calling `t.cancel()` in a streaming
    generator's `finally`; **a bare `asyncio.create_task` with no disconnect
    handling is banned.**

    The shape is the disconnect race in `_run_turn`, and **it replaced an
    inline `await` that this step originally shipped.** The reasoning for the
    inline version — that the run is the handler's own task and so dies with
    the client — is false on this stack, and the step's own `azure-query`
    verification disproved it rather than any review catching it: a client
    killed 3s into a 30s turn left the turn running to completion, writing 12
    checkpoint blobs and two case-blob turns the Belt never saw. Starlette does
    not cancel an endpoint coroutine on disconnect. Full account in `_run_turn`.

    **`/ask/stream` (§49) still does not exist**, and building it here would be
    building step 10.1's scope inside 4.2. When it lands, its `gen()` must make
    this choice explicitly in its own `finally` — inheriting this one silently
    is the accident §47 names.

    Ratified policy is ABANDON, not COMPLETE: a silently-completed gate approval
    the Belt never saw is unacceptable in a system whose premise is that the
    Belt approves what gets committed.
    """
    arrived = time.time()                   # G-166: the turn's clock starts when the request arrives
    _bind(request.case_id, request.phase)   # T43 (DEF-129): every log line of the request names them
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")

    case = await blob.load_case(request.case_id)
    if case is None:
        raise HTTPException(404, f"Case {request.case_id} not found")
    who = access.person(http, case, 'ask')          # ADR-0091 decision 3
    if who is not None:                              # the session names the person, never a typed name
        request = request.model_copy(update={"user": who.full_name})
    # WATCH 19's lazy half — every case in the registry predates the writer. From the blob
    # only: the Store's case copy never carries unfinished work (ADR-0066).
    _ensure_case_record(case)
    case = await _with_unfinished_work(case)

    from datetime import datetime, timezone
    from backend.core.graph import PhaseNotWired, get_graph
    if _over_turn_rate(request.user):
        # T93 (ADR-0067, threat D): refused before the graph runs, so nothing is stored; the
        # verdict joins the decision trail; the screen keeps the typed text.
        from backend.core import guard, guard_messages
        guard.record(get_store(), request.case_id, request.phase, int(time.time() * 1000),
                     {"status": "blocked", "threat": "D", "rule": "turn rate", "person": request.user,
                      "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        return AskResponse(answer=guard_messages.D_RATE.format(limit=TURNS_PER_MINUTE), phase=request.phase,
                           gate_status=GateStatus(phase=request.phase, passed=False, attempts=0, missing_fields=[]),
                           blocked="D")

    now = datetime.now(timezone.utc).isoformat()
    user_turn = {
        "turn": len(case.conversation_history) + 1,
        "role": "user",
        "user": request.user,
        "text": request.message,
        "timestamp": now,
        "citations": [],
    }

    phase = _requested_phase(case, request.phase)
    graph = get_graph()
    config = _graph_config(case, phase, request.user, entry="ask", started=arrived)
    # Step 6.61 (R4) — a Confirm / Change click rides beside the entry mode.
    config["configurable"]["belt_action"] = request.action
    config["configurable"]["belt_element"] = request.element      # W9 (DEF-079)

    try:
        state = await _graph_input(
            graph, config, case, [conversation.turn_to_message(user_turn)]
        )
        # §47 requirement 1 — ABANDON on disconnect. See `_run_turn`.
        result = await _run_turn(graph, state, config, http, deadline=True)
        _mirror_asks(request.case_id, phase, result)
    except TurnDeadline:
        # DEF-093 / G-157 (ADR-0080): the run was cancelled at the deadline; nothing after the last
        # completed step was checkpointed, so the turn changed nothing a Confirm or a store depends on.
        # The Belt is told, in code, to send the message again; step_log records the deadline.
        logger.warning("ask() reached the %.0f s turn deadline for %s — the run was cancelled",
                       TURN_LIMIT_S, request.case_id)
        try:
            from backend.core.store import get_store as _store   # read at call time
            _store().put(("projects", request.case_id, "step_log"), f"deadline:{phase}:{now}",
                         {"layer": "turn_deadline", "limit_s": TURN_LIMIT_S, "phase": phase, "at": now})
        except Exception as exc:  # noqa: BLE001 — the audit write must not change the reply
            logger.error("ask(): the turn deadline could not be recorded: %s", exc)
        return AskResponse(answer=TURN_DEADLINE_REPLY, phase=request.phase,
                           gate_status=GateStatus(phase=request.phase, passed=False, attempts=0))
    except ClientGone:
        logger.info(
            "ask() ABANDONED for %s — client disconnected mid-turn; "
            "no further node ran and the case blob was not written",
            request.case_id,
        )
        raise HTTPException(499, "Client disconnected; turn abandoned (§47).")
    except PhaseNotWired as e:
        raise HTTPException(501, str(e))
    except HTTPException:
        raise
    except StateSchemaVersionError as e:            # ADR-0065 (T88): readable, never "Graph error"
        raise HTTPException(409, str(e))
    except Exception as e:
        logger.exception("ask() error: %s", e)
        from backend.core.prompts import TURN_FAILED
        raise HTTPException(500, TURN_FAILED)          # G-261 (audit W8): the exception's text stays in the log

    reply = _last_ai(result)
    payload = conversation.transport(reply) if reply is not None else {}
    phase_data = dict(payload.get("v1_draft") or {})
    verdict = dict(payload.get("gate_verdict") or {})
    extra = dict(getattr(reply, "additional_kwargs", None) or {}) if reply else {}
    await _reconcile_team(request.case_id, phase, extra.get("phase_record"), request.user)

    # ── envelope marshalling from here down ───────────────────────────
    # ADR-0066 / T13: no case-blob write. The turn — the Belt's message, the reply and the
    # phase's merged record on it — is in the checkpoint, which is its only home.

    return AskResponse(
        answer=(reply.content if reply is not None else "Processing..."),
        phase=request.phase,
        captured_fields=_build_captured_fields(phase_data, request.phase),
        phase_inputs=({k: v for k, v in phase_data.items()
                       if not k.startswith("_")} or None),
        gate_status=GateStatus(
            phase=request.phase,
            passed=bool(verdict.get("passed", False)),
            # NOT a hardcoded 0. The counter lives on `PhaseState`, is written
            # by `validation_stack` and is reported from the graph result —
            # §1.7's rule that it may never sit in route scope. What it does not
            # yet do is SURVIVE across turns: the input mapper rebuilds the child
            # state on every invoke because there is no `interrupt()` holding the
            # subgraph open, so the cap of 3 still cannot accumulate. That lands
            # with the interrupt at stage 7 — carried as a WATCH.
            attempts=int(verdict.get("gate_attempts", 0)),
            missing_fields=list(verdict.get("missing") or []),
        ),
        citations=[
            CitationOut(
                agent_origin=c.get("agent_origin", ""),
                index_name=c.get("index_name", ""),
                document_id=c.get("document_id", ""),
                relevance_summary=c.get("relevance_summary", ""),
                source_file=str(c.get("source_file") or ""),
                page=c.get("page") if isinstance(c.get("page"), int) else None,
            )
            for c in (extra.get("citations") or [])
        ],
        # DEF-095 (C4): in Define, computed from what the reply's element still misses — never another element.
        suggestion_chips=(_define_next_steps(extra) if request.phase == "define"
                          else _build_chips(request.phase, phase_data)),
        sipoc_diagram=extra.get("sipoc_diagram"),
        visualisation=extra.get("visualisation"),
        section_completed=extra.get("section_completed"),
        escalated=bool(verdict.get("escalated", False)),
        # Step 10.0 — the four blocks and the warning, projected from the
        # reply message the executor put them on (`_attach_blocks`).
        **{k: str((extra.get("coaching_blocks") or {}).get(k) or "")
           for k in ("explanation", "example", "prompt", "progress")},
        grader_warning=extra.get("grader_warning") or None,
        move=(extra.get("coaching_move") or {}).get("move"),
        move_field=(extra.get("coaching_move") or {}).get("field"),
        blocked=((extra.get("input_guard") or {}).get("threat")
                 if (extra.get("input_guard") or {}).get("status") == "blocked" else None),
        readback_card=extra.get(conversation.CARD_KEY),
        confirmed_strip=extra.get(conversation.STRIP_KEY),
        reply_element=extra.get(conversation.ELEMENT_KEY),
        completion_card=extra.get(conversation.COMPLETION_KEY),
    )


async def _reconcile_team(case_id: str, phase: str, record: Any, by: str) -> None:
    """ADR-0090 decision 3, ruling b: once Define's element 2 (the team) is confirmed, every person its rows name
    who is not on the case is added as a proposed member — the team panel lists them for the lead to confirm.
    Element 2 stays confirmed. A failure here never fails the turn: it is logged, and the next turn retries."""
    from datetime import datetime, timezone

    from backend.phases import moves
    from backend.storage import people as people_mod
    if phase != "define" or not isinstance(record, dict):
        return
    if ((record.get("field_status") or {}).get("team") or {}).get("status") != moves.CONFIRMED:
        return
    rows = (record.get("structured") or {}).get("team")
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    added: list[str] = []

    def change(current: list) -> list:
        out, new = people_mod.reconcile_team(current, rows, by, at)
        added.extend(new)
        return out
    try:
        await blob.update_people(case_id, change)
    except Exception as exc:  # noqa: BLE001 — the turn has answered; the next confirmed turn retries
        logger.error("element 2's people were not reconciled for %s: %s", case_id, exc)
        return
    if added:
        logger.info("element 2 named %d person(s) not on the case — proposed members: %s",
                    len(added), ", ".join(added))


def _people_out(case: CaseDocument) -> PeopleResponse:
    from backend.storage import people as people_mod
    head = people_mod.lead(case.people)
    ordered = ([head] if head else []) + [p for p in case.people if p is not head]
    return PeopleResponse(case_id=case.case_id, lead=head.full_name if head else case.leader,
                          people=[PersonOut(full_name=p.full_name, email=p.email, role=p.role, function=p.function,
                                            department=p.department, location=p.location.model_dump(),
                                            status=p.status, is_lead=p is head) for p in ordered])


async def _as_lead(case_id: str, actor: str, http: Optional[Request] = None) -> CaseDocument:
    """R8b / ADR-0090: only the project lead changes the team. With ADR-0091's session the person is the
    session's; on a case that does not ask for sign-in yet, the lead is named by e-mail or full name."""
    from backend.storage import people as people_mod
    case = await blob.load_case(case_id)
    if case is None:
        raise HTTPException(404, f"Case {case_id} not found")
    who = access.person(http, case, "team change")
    if who is not None:
        actor = who.email
    head = people_mod.lead(case.people)
    if head is None or people_mod.find([head], actor) is None:
        raise HTTPException(403, TEAM_LEAD_ONLY.format(lead=head.full_name if head else case.leader))
    return case


@router.get("/cases/{case_id}/sign-in", response_model=SignInInfo)
async def sign_in_info(case_id: str) -> SignInInfo:
    """W17 — what the sign-in window says: the case, who may enter, the lead. Whether the case asks for sign-in
    (ruling b). Nothing else of the case."""
    _bind(case_id, None)
    case = await blob.load_case(case_id)
    if case is None:
        raise HTTPException(404, f"Case {case_id} not found")
    lead = access.lead_name(case)
    return SignInInfo(case_id=case.case_id, title=case.title, lead=lead, required=access.required(case),
                      message=access.SIGN_IN_NEEDED.format(lead=lead),
                      not_on_team=f"Not on the team? Ask {lead} to add you.")


@router.post("/cases/{case_id}/session", response_model=SessionOut)
async def sign_in(case_id: str, body: SignInIn, response: Response) -> SessionOut:
    """ADR-0091 decision 2: sign in with the company e-mail the lead registered; the session is this case's."""
    _bind(case_id, None)
    case = await blob.load_case(case_id)
    if case is None:
        raise HTTPException(404, f"Case {case_id} not found")
    who, outcome = access.sign_in(case, body.email, response, body.code)
    head = access.lead_name(case)
    if outcome in ("ok", "wrong", "expired") and body.code.strip():
        # ADR-0105 decisions 5 and 6: the code spent at the first sign-in, a wrong try counted (5 void it), an expired
        # code voided — written to the case record as every team change is (ADR-0090 decision 2).
        from backend.storage import people as people_mod
        await blob.update_people(case_id, lambda ps: people_mod.code_used(ps, who.email, outcome,
                                                                          access.CODE_ATTEMPTS))
    if outcome not in ("ok", ""):
        raise HTTPException(403, (access.CODE_NEEDED if outcome == "none" else access.CODE_REFUSED).format(lead=head))
    return SessionOut(case_id=case.case_id, full_name=who.full_name, email=who.email, role=who.role,
                      is_lead=who.full_name == head)


@router.post("/cases/{case_id}/people/{who}/code", response_model=CodeIssued)
async def issue_code(case_id: str, who: str, body: PersonRemoval, http: Request) -> CodeIssued:
    """ADR-0105 decisions 1-4 (DEF-103): the lead issues a one-time code for one confirmed member — shown once, here;
    only its HMAC-SHA256 is stored, in the person entry; a re-issue voids the earlier code; recorded in the access
    trail."""
    import datetime as _dt

    from backend.storage import people as people_mod
    _bind(case_id, None)
    case = await _as_lead(case_id, body.actor, http)
    person = people_mod.find(case.people, who)
    if person is None:
        raise HTTPException(404, f"{who} is not on this case.")
    code = access.new_code()
    now = _dt.datetime.now(_dt.timezone.utc)
    try:
        await blob.update_people(case_id, lambda ps: people_mod.set_code(
            ps, who, access.code_digest(case_id, person.email, code), now.isoformat(timespec="seconds")))
    except LookupError:
        raise HTTPException(404, f"{who} is not on this case.")
    except ValueError as e:
        raise HTTPException(422, f"{e}.")
    access._trail(case_id, "code_issued", person.email, "people", f"by {body.actor}")
    return CodeIssued(full_name=person.full_name, code=code,
                      expires_at=(now + _dt.timedelta(hours=access.CODE_HOURS)).isoformat(timespec="seconds"))


@router.get("/cases/{case_id}/people", response_model=PeopleResponse)
async def get_people(case_id: str, http: Request) -> PeopleResponse:
    """ADR-0090: the team panel — everyone on the case, the lead first, proposed members marked."""
    _bind(case_id, None)
    case = await blob.load_case(case_id)
    if case is None:
        raise HTTPException(404, f"Case {case_id} not found")
    who = access.person(http, case, 'team panel')          # ADR-0091 decision 3
    return _people_out(case)


@router.post("/cases/{case_id}/people", response_model=PeopleResponse)
async def add_person(case_id: str, change: PersonChange, http: Request) -> PeopleResponse:
    """ADR-0090 / R8b: the lead adds a member — full name and role; the e-mail before they sign in."""
    from backend.storage import people as people_mod
    _bind(case_id, None)
    await _as_lead(case_id, change.actor, http)
    try:
        case = await blob.update_people(case_id, lambda ps: people_mod.add(ps, _person(change.person, by=change.actor)))
    except ValueError as e:
        raise HTTPException(422, f"{e}.")
    assert case is not None
    return _people_out(case)


@router.post("/cases/{case_id}/people/{who}", response_model=PeopleResponse)
async def change_person(case_id: str, who: str, change: PersonChange, http: Request,
                        confirm: bool = False) -> PeopleResponse:
    """ADR-0090: the lead completes a person's details; with `confirm`, confirms a proposed member — only with
    an e-mail (ruling b). `who` is the person's e-mail or full name."""
    from backend.storage import people as people_mod
    _bind(case_id, None)
    await _as_lead(case_id, change.actor, http)
    details = change.person.model_dump()

    def apply(ps: list) -> list:
        ps = people_mod.complete(ps, who, details)
        return people_mod.confirm(ps, details.get("full_name") or who, change.person.email) if confirm else ps
    try:
        case = await blob.update_people(case_id, apply)
    except LookupError:
        raise HTTPException(404, f"{who} is not on this case.")
    except ValueError as e:
        raise HTTPException(422, f"{e}.")
    assert case is not None
    return _people_out(case)


@router.delete("/cases/{case_id}/people/{who}", response_model=PeopleResponse)
async def remove_person(case_id: str, who: str, body: PersonRemoval, http: Request) -> PeopleResponse:
    """DEF-104 (R8b, ADR-0090): the lead removes a member — never themselves (the case keeps one lead; handing the
    role over is R8c). Written to the case record as every change of the people is (ADR-0090 decision 2)."""
    from backend.storage import people as people_mod
    _bind(case_id, None)
    await _as_lead(case_id, body.actor, http)
    try:
        case = await blob.update_people(case_id, lambda ps: people_mod.remove(ps, who))
    except LookupError:
        raise HTTPException(404, f"{who} is not on this case.")
    except ValueError as e:
        raise HTTPException(422, f"{e}.")
    assert case is not None
    return _people_out(case)


@router.post("/cases/{case_id}/lead", response_model=PeopleResponse)
async def hand_over_lead(case_id: str, body: LeadHandover, http: Request) -> PeopleResponse:
    """DEF-105 (R8c, founder ruling 2026-10-21): the lead hands the role to another registered member. The case
    record's lead is updated (the people list, written as every team change is — ADR-0090 decision 2), and the
    handover is recorded in the Store's cross-phase audit (`step_log`): who, to whom, when, why."""
    import secrets
    import time
    from backend.core.store import get_store
    from backend.storage import people as people_mod
    _bind(case_id, None)
    before = await _as_lead(case_id, body.actor, http)
    head = people_mod.lead(before.people)
    try:
        case = await blob.update_people(case_id, lambda ps: people_mod.hand_over(ps, body.to))
    except LookupError:
        raise HTTPException(404, f"{body.to} is not on this case.")
    except ValueError as e:
        raise HTTPException(422, f"{e}.")
    assert case is not None
    new = people_mod.lead(case.people)
    get_store().put(("projects", case_id, "step_log"), f"lead:{int(time.time() * 1000)}:{secrets.token_hex(3)}",
                    {"layer": "people", "event": "lead_handover", "from": head.full_name if head else body.actor,
                     "to": new.full_name if new else body.to, "why": body.reason.strip(),
                     "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    logger.info("lead handed over on %s: %s -> %s", case_id, head.full_name if head else body.actor,
                new.full_name if new else body.to)
    return _people_out(case)


@router.get("/gate/review/{case_id}/{phase}", response_model=GateReviewResponse)
async def gate_review(case_id: str, phase: str, http: Request) -> GateReviewResponse:
    """The assembled gate document, shown to the Belt BEFORE approval.

    §9.1 steps 3-4 of the nine-step HITL gate: the Belt sees validated output
    and checks it. This is the READ half — the interrupt-based approve/reject
    flow is step 7.3, and the conflict panel and tier progress bars are step
    10.2. Building either here would be building 10.2's scope inside 3.4.

    Tier is carried per field because it is what the Belt needs to know:
    **a Tier 1 gap blocks, a Tier 2 gap is theirs to accept** (§35). The
    document is assembled only when assembly would succeed, so the screen never
    shows a half-built document as though it were the real one.
    """
    _bind(case_id, phase)   # T43 (DEF-129): every log line of the request names them
    if phase not in GATE_SPECS:
        raise HTTPException(400, f"Unknown phase: {phase}")
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")

    case = await blob.load_case(case_id)
    if case is None:
        raise HTTPException(404, f"Case {case_id} not found")
    who = access.person(http, case, 'gate review')          # ADR-0091 decision 3
    case = await _with_unfinished_work(case)   # ADR-0066: read through the graph

    record = case.phases.get(phase)
    artifacts = dict((record.structured or {}) if record else {})
    spec = GATE_SPECS[phase]

    rows = review_rows(phase, artifacts)
    missing = [r["field"] for r in rows if r["tier"] == 1 and not r["present"]]
    gaps = [f"{r['field']} — Belt accepted gap"
            for r in rows if r["tier"] == 2 and not r["present"]]

    document = None
    if not missing:
        try:
            document = spec.assemble(
                artifacts,
                citations=[c for c in (getattr(record, "citations", []) or [])],
                uploads=[u.model_dump() if hasattr(u, "model_dump") else u
                         for u in (getattr(record, "uploads", []) or [])],
                acknowledged_gaps=gaps,
            ).model_dump()
        except Exception as e:
            # Assembly raising with every Tier 1 field present is a CODE
            # DEFECT (S-F28), not an incomplete phase — surface it rather
            # than rendering an empty document as though the gate were open.
            logger.exception("gate assembly failed for %s/%s: %s", case_id, phase, e)
            from backend.core.prompts import REPORT_NOT_ASSEMBLED
            raise HTTPException(500, REPORT_NOT_ASSEMBLED)  # G-261 (audit W8)

    report = None
    if phase == "define":
        # R5 — the gate is a readable report, not a field checklist: the seven
        # sections, from confirmed values only, with R6's dated history.
        report = define_report(
            artifacts,
            case={"case_id": case.case_id, "title": case.title, "leader": case.leader,
                  "belt_level": case.belt_level, "department": case.department,
                  "target_date": case.target_date,
                  "people": [p.model_dump() for p in case.people]},           # ADR-0090
            field_log=list(getattr(record, "field_log", []) or []),
            field_status=dict(getattr(record, "field_status", {}) or {}))          # ADR-0093: the Gate's rows

    return GateReviewResponse(
        phase=phase,
        passed=not missing,
        missing_fields=missing,
        fields=[GateReviewField(**r) for r in rows],
        acknowledged_gaps=gaps,
        document=document,
        report=report,
        awaiting_decision=(phase == "define" and await _awaiting_decision(case, phase)),
        # R11 (DEF-101): the approval stamp, written once on the transition (`blob.write_phase_gate`).
        approved_at=(record.submitted_at if record is not None and record.gate_passed else None),
        field_counts={
            "total": len(rows),
            "tier_1": len(spec.tier_1),
            "tier_2": len(spec.tier_2),
            "captured": sum(1 for r in rows if r["present"]),
        },
    )


_PURPOSE_PREFIX = "purpose="


def auto_detect_purpose(filename: str) -> str:
    """Guess a purpose label from a filename. Used when the UI does
    not supply an explicit purpose."""
    name = (filename or "").lower()
    if any(x in name for x in ("sipoc", "process map", "map")):
        return "Process map"
    if any(x in name for x in ("data", "complaint", "measurement", "baseline")):
        return "Data file"
    if any(x in name for x in ("survey", "nps", "satisfaction")):
        return "Survey data"
    if any(x in name for x in ("capability", "sigma", "control")):
        return "Capability report"
    if any(x in name for x in ("charter", "project", "scope")):
        return "Project document"
    if any(x in name for x in ("fishbone", "pareto", "cause", "analyse", "analyze")):
        return "Analysis"
    if any(x in name for x in ("solution", "improve", "pilot")):
        return "Improvement plan"
    ext = filename.rsplit(".", 1)[-1].lower() if filename and "." in filename else ""
    if ext in ("xlsx", "xls", "csv"):
        return "Data file"
    if ext == "pdf":
        return "Document"
    return "File"


def _case_file_id(case_id: str, filename: str, uploaded_at: str) -> str:
    """Deterministic 16-char id for a case file. Computed from
    (case_id, filename, uploaded_at) so both /upload and /cases agree
    without persisting a separate id field."""
    import hashlib
    raw = f"{case_id}|{filename}|{uploaded_at}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def _classification_for(purpose: str, content_type: str, indexed: bool) -> str:
    """Encode purpose+content_type+indexed into the existing
    UploadRecord.classification field so the projection can recover
    the purpose later. New format: 'purpose=<p> · <type> · <status>'."""
    status = "indexed" if indexed else "pending"
    return f"{_PURPOSE_PREFIX}{purpose} · {content_type} · {status}"


def _purpose_from_classification(classification: str, fallback_filename: str) -> str:
    """Recover a purpose label from a UploadRecord.classification.
    Records persisted before the purpose tag was added fall back to
    auto-detect on the filename."""
    if not classification:
        return auto_detect_purpose(fallback_filename)
    if classification.startswith(_PURPOSE_PREFIX):
        head = classification[len(_PURPOSE_PREFIX):]
        return head.split(" · ", 1)[0] if " · " in head else head
    return auto_detect_purpose(fallback_filename)


@router.post("/upload")
async def upload_file(
    http: Request,
    case_id: str = Form(...),
    uploaded_by: str = Form(...),
    phase: str = Form(...),
    file: UploadFile = File(...),
    purpose: str = Form(""),
    kind: str = Form(""),
    role: str = Form(""),
):
    """§29.1's external-data channel — procedure step 6.11.

    Classify, parse DETERMINISTICALLY, refuse what cannot be read, interpret
    once, then route by kind: **evidence goes to `improve_evidence_index`; an
    artefact does not** (ruling 3). The upload record is persisted to the case
    blob, which is the system of record, and reaches `PhaseState.uploads`
    through the Store copy at the next phase entry.

    **A file that cannot be extracted is refused with a Belt-readable reason
    and is not stored** (ruling 5). Before 6.11 the opposite happened: csv and
    xlsx bucketed as `other`, pdf and docx reported as supported with no
    extractor, `_index_upload` returned early on empty text, and the file was
    saved to blob regardless — so a Belt could upload a spreadsheet, see it
    accepted, and have it be invisible to the coach and absent from the index.

    Returns a flat ``file`` dict in the CaseFile shape alongside the legacy
    response fields for backward compatibility.
    """
    _bind(case_id, phase)   # T43 (DEF-129): every log line of the request names them
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")

    file_bytes = await file.read()
    # T93 (ADR-0067): above 25 MB refused with advice; above 5 MB accepted with a notice.
    from backend.core import guard_messages
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > UPLOAD_MAX_MB:
        raise HTTPException(413, guard_messages.D_UPLOAD_MAX.format(limit_mb=UPLOAD_MAX_MB))
    notice = guard_messages.D_UPLOAD_NOTICE.format(size_mb=size_mb) if size_mb > UPLOAD_NOTICE_MB else None
    mime_type = file.content_type or "application/octet-stream"
    # `UploadFile.filename` is `str | None`. Resolved ONCE here rather than
    # at each of the four use sites — those four were carried as mypy DEBT
    # and are retired with this step, since a nameless upload is a real case
    # (some clients omit it) and every downstream consumer wants a `str`.
    filename = file.filename or "upload"

    case = await blob.load_case(case_id)
    if case is None:
        raise HTTPException(404, f"Case {case_id} not found")
    who = access.person(http, case, 'upload')          # ADR-0091 decision 3
    if who is not None:
        uploaded_by = who.full_name
    # T59 (DEF-134): the upload's phase is the case's, set here — the client's field is not trusted
    # (its `uploaded_at` is the server's clock too: `process_upload`'s timestamp).
    if phase != case.current_phase:
        logger.info("upload: the client sent phase %r; the case is in %r — filed under the case's",
                    phase, case.current_phase)
    phase = case.current_phase

    # ADR-0066: the upload is saved to the blob below, so the blob's case stays as loaded; the
    # current Define values are READ from the checkpoint through a copy.
    unfinished = await _with_unfinished_work(case)
    define_phase = unfinished.phases.get("define")
    define_structured = (define_phase.structured or {}) if define_phase else {}
    # ADR-0074 (DEF-108) — the element the planner is working on now: the file is judged against it.
    from backend.phases import moves as _moves
    here = unfinished.phases.get(phase)
    current = _moves.current(phase, dict((here.structured or {}) if here else {}),
                             dict((here.field_status or {}) if here else {})) if here else None
    element = current[0] if current else None
    case_meta = {
        "title": case.title,
        "department": case.department,
        "belt_level": case.belt_level,
        "what": define_structured.get("what", ""),
    }

    # Resolve purpose first — `classify_kind` reads it, and the parse below
    # is the expensive half, so a purpose that changes the destination should
    # be settled before anything is spent.
    resolved_purpose = (purpose or "").strip() or auto_detect_purpose(filename)

    # ── Ask-binding, step 6.12 ────────────────────────────────────────
    #
    # **The digest is the VERSION identity and is computed before anything
    # else** (§23.2). The same bytes re-uploaded are not a new version.
    digest = content_digest(file_bytes)

    # `role` is the LOGICAL identity, with `case_id` (ruling AP2.2). **From
    # the ask when the upload was solicited, from the Belt's declared purpose
    # when it was not** — never from the filename, which AP2.2 forbids.
    open_asks = asks_for_phase(read_case_record(get_store(), case_id), phase)
    declared_role = (role or "").strip()
    matched_ask = (open_ask_for_role(open_asks, declared_role)
                   if declared_role else
                   (open_asks[0] if len(open_asks) == 1 else None))
    resolved_role = (
        declared_role
        or (matched_ask or {}).get("role")
        or _role_from_purpose(resolved_purpose)
    )

    # ── Parse BEFORE storing (ruling 5) ───────────────────────────────
    #
    # **The refusal has to come before the blob write, or it is not a
    # refusal.** A file saved and then rejected leaves the Belt with an
    # upload they can see in the case and the coach cannot use — which is
    # the state this step exists to end, arrived at from the other side.
    upload_record = await process_upload(
        case_id=case_id,
        filename=filename,
        file_bytes=file_bytes,
        mime_type=mime_type,
        uploaded_by=uploaded_by,
        phase=phase,
        case_meta=case_meta,
        purpose=resolved_purpose,
        declared_kind=kind,
        element=element,
    )

    # Shape check against the ask — **a mismatch is a coaching question, not
    # a rejection**, so it classifies and never blocks (the step's own ruling;
    # AP2.5 governs unreadable files, not incomplete ones).
    shape_match, missing_columns = check_shape(
        matched_ask, upload_record.get("columns") or [])

    if not upload_record.get("parsed"):
        # 422, not 400: the request was well formed and the file is the
        # problem. The reason is written for the Belt, not for a log.
        raise HTTPException(422, upload_record.get("refusal_reason")
                            or "We could not read this file.")
    # T87 / ADR-0062 point 4 (DEF-144): every masking in step_log, by type and count, never the value.
    if upload_record.get("pii_masked"):
        try:
            from backend.core.store import get_store as _store   # read at call time
            _store().put(("projects", case_id, "step_log"),
                            f"pii:{phase}:{upload_record['timestamp']}",
                            {"layer": "pii", "where": "upload", "filename": filename,
                             "masked": dict(upload_record["pii_masked"]), "at": upload_record["timestamp"]})
        except Exception as exc:  # noqa: BLE001 — the audit write must not refuse the upload
            logger.error("upload: the personal-data masking could not be recorded: %s", exc)

    # ── Supersession, resolved on (case_id, role) by digest (§23.2) ────
    #
    # **Same digest is not a new version.** The Belt re-uploading the identical
    # file gets the existing record back, with no blob write, no re-index and
    # no version bump — which is what the digest is for.
    #
    # **A different digest under the same role SUPERSEDES.** Scoped to
    # `(case_id, role)` deliberately: a Control-phase measurement does not
    # supersede the Measure baseline, because they are different roles. Only a
    # correction of the same document supersedes.
    phase_record = case.phases.get(phase)
    prior = [u for u in (getattr(phase_record, "uploads", []) or [])
             if u.role == resolved_role]
    identical = next((u for u in prior if u.content_digest == digest), None)
    if identical is not None:
        logger.info(
            "Upload %s is byte-identical to the current %r — not a new "
            "version; returning the existing record.", filename, resolved_role,
        )
        return {
            "file": {
                "file_id": _case_file_id(case_id, identical.filename,
                                         identical.uploaded_at),
                "filename": identical.filename, "phase": phase,
                "purpose": resolved_purpose, "blob_url": identical.blob_path,
                "uploaded_at": identical.uploaded_at,
                "uploaded_by": identical.uploaded_by,
                "size_bytes": len(file_bytes) if file_bytes else None,
            },
            "blob_path": identical.blob_path, "filename": identical.filename,
            "content_type": upload_record["content_type"],
            "summary": identical.summary, "indexed": bool(identical.evidence_index_id),
            "kind": identical.kind, "role": identical.role,
            "shape_match": identical.shape_match,
            "content_digest": identical.content_digest,
            "version": identical.version, "superseded": False,
            "unchanged": True,
        }

    # A revision: this becomes the current version of the same ask.
    version = max([(u.version or 1) for u in prior], default=0) + 1
    if prior:
        logger.info(
            "Upload %s SUPERSEDES %d earlier version(s) of role %r — "
            "version %d. The earlier blobs are kept; the case blob is the "
            "system of record and retains every version (§10).",
            filename, len(prior), resolved_role, version,
        )

    # Save raw file to blob — only now that it is known to be readable
    blob_path = await blob.upload_file(
        case_id, filename, file_bytes, mime_type,
    )
    upload_record["blob_path"] = blob_path
    interpretation = dict(upload_record.get("interpretation") or {})
    if interpretation:
        # Ruling 6: the interpretation cites its source upload, and the blob
        # path is the half only this layer knows.
        interpretation["source_blob_path"] = blob_path
        upload_record["interpretation"] = interpretation

    # ── Route by kind (ruling 3) ──────────────────────────────────────
    #
    # **Evidence describes the world and goes to the index. An artefact is
    # what the team designed and does not.** One bucket would let a proposed
    # future — a to-be process map, a draft control plan — be retrieved later
    # as a fact about the present.
    upload_kind = upload_record.get("kind", CLASSIFIER_EVIDENCE)
    evidence_index_id = None
    not_indexed = None                       # G-261 (audit W4): what the Belt is told when indexing fails
    used_by_coach = upload_record.get("used_by_coach", True) is not False
    if not used_by_coach:
        logger.info("Upload %s kept, not used by the coach (T72) — not indexed.", filename)
    elif upload_kind == CLASSIFIER_EVIDENCE:
        try:
            evidence_index_id = await _index_upload(
                case_id, upload_record,
                role=resolved_role, shape_match=shape_match,
                content_digest=digest,
            )
            upload_record["indexed"] = True
        except Exception as e:  # noqa: BLE001 — the file is kept; the Belt is told it cannot be searched yet
            logger.warning(
                "Evidence indexing failed for %s: %s", filename, e,
            )
            from backend.core.prompts import UPLOAD_NOT_INDEXED
            not_indexed = UPLOAD_NOT_INDEXED.format(filename=filename)
    else:
        logger.info(
            "Upload %s classified as %s — captured content, not indexed "
            "(ruling 3).", filename, upload_kind,
        )
    indexed = evidence_index_id is not None

    # Persist upload record into case blob (canonical phases[phase].uploads)
    if phase_record is not None:
        phase_record.uploads.append(UploadRecord(
            filename=filename,
            blob_path=blob_path,
            uploaded_by=uploaded_by,
            uploaded_at=upload_record["timestamp"],
            classification=_classification_for(
                resolved_purpose, upload_record["content_type"], indexed
            ),
            rows=upload_record.get("row_count"),
            role=resolved_role,
            shape_match=shape_match,
            content_digest=digest,
            ask_id=(matched_ask or {}).get("ask_id"),
            version=version,
            kind=upload_kind,
            evidence_index_id=evidence_index_id,
            summary=upload_record.get("summary") or "",
            interpretation=upload_record.get("interpretation"),
            used_by_coach=used_by_coach,
            not_used_reason=upload_record.get("not_used_reason"),
        ))
        await blob.save_case(case)
        # The Store's `case` copy is what the input mappers read (§9), so it
        # has to move with the blob or `PhaseState.uploads` goes stale by one
        # upload — the same two-ends problem WATCH 19 was.
        _ensure_case_record(case)

    # CaseFile-shaped dict for the UI (matches gateway.schemas.CaseFile)
    case_file = {
        "file_id": _case_file_id(case_id, filename, upload_record["timestamp"]),
        "filename": filename,
        "phase": phase,
        "purpose": resolved_purpose,
        "blob_url": blob_path,
        "uploaded_at": upload_record["timestamp"],
        "uploaded_by": uploaded_by,
        "size_bytes": len(file_bytes) if file_bytes else None,
    }

    return {
        "file": case_file,
        # Legacy fields kept for callers that read them
        "blob_path": blob_path,
        "filename": filename,
        "content_type": upload_record["content_type"],
        "summary": upload_record["summary"],
        "sipoc_columns": upload_record.get("sipoc_columns"),
        "indexed": indexed,
        # ── step 6.11 ────────────────────────────────────────────────
        "kind": upload_kind,
        "role": resolved_role,
        "shape_match": shape_match,
        "missing_columns": missing_columns,
        "content_digest": digest,
        "version": version,
        "ask_id": (matched_ask or {}).get("ask_id"),
        "evidence_index_id": evidence_index_id,
        "structure": upload_record.get("structure"),
        "columns": upload_record.get("columns") or [],
        "row_count": upload_record.get("row_count"),
        "column_types": upload_record.get("column_types") or {},
        "column_ranges": upload_record.get("column_ranges") or {},
        "interpretation": upload_record.get("interpretation"),
        "used_by_coach": used_by_coach,
        # The PII line (founder ruling 2026-10-12): what was hidden from the coach, said at upload.
        "message": upload_record.get("not_used_reason") or " ".join(x for x in (notice, (
            PII_HIDDEN_UPLOAD.format(what=pii.described(upload_record["pii_masked"]))
            if upload_record.get("pii_masked") else None), not_indexed) if x) or None,
    }


@router.delete("/files/{case_id}/{file_id}")
async def delete_case_file(case_id: str, file_id: str, http: Request, by: str = ""):
    """W7 (DEF-109): remove an uploaded file — its blob, its `improve_evidence_index` document (by the id the
    upload kept; an artefact has none) and its record on the case — and keep in the case's audit trail (the
    Store's `step_log`) its name, digest, the date and who removed it: the signed-in person, else `by`, the
    name the page sends (as an upload's `uploaded_by`).

    Storage and the index first, the case record last: if either refuses, the file stays on the case and
    nothing is recorded as removed, so the removal can be tried again (a blob or index document already gone
    counts as removed)."""
    _bind(case_id, None)   # T43 (DEF-129): every log line of the request names them
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")

    case = await blob.load_case(case_id)
    if case is None:
        raise HTTPException(404, "Case not found")
    who = access.person(http, case, 'delete file')          # ADR-0091 decision 3
    removed_by = who.full_name if who is not None else (by.strip() or "unknown")

    found = None
    for phase_data in case.phases.values():
        uploads = getattr(phase_data, "uploads", []) or []
        for i, u in enumerate(uploads):
            if _case_file_id(case_id, u.filename, u.uploaded_at) == file_id:
                found = (uploads, i, u)
                break
        if found is not None:
            break
    if found is None:
        raise HTTPException(404, "File not found")
    uploads, i, upload = found

    try:
        await blob.delete_upload(upload.blob_path)
        if upload.evidence_index_id:
            await _unindex_upload(upload.evidence_index_id)
    except Exception as exc:  # noqa: BLE001 — the Belt is told; the file stays on the case
        logger.error("delete file: %s could not be removed: %s", upload.filename, exc)
        raise HTTPException(502, f"We could not remove {upload.filename} just now; it is still on the case. "
                                 "Please try again.")

    uploads.pop(i)
    await blob.save_case(case)
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        from backend.core.store import get_store as _store   # read at call time
        _store().put(("projects", case_id, "step_log"), f"file-removed:{file_id}:{at}",
                     {"layer": "files", "event": "removed", "filename": upload.filename,
                      "content_digest": upload.content_digest, "blob_path": upload.blob_path,
                      "evidence_index_id": upload.evidence_index_id, "removed_at": at, "removed_by": removed_by})
    except Exception as exc:  # noqa: BLE001 — the file is gone; the failed record is logged loudly
        logger.error("delete file: the removal of %s could not be recorded: %s", upload.filename, exc)
    return {"deleted": True, "file_id": file_id}


async def _unindex_upload(doc_id: str) -> None:
    """W7 (DEF-109): remove one upload's document from `improve_evidence_index` by its id — the one
    `_index_upload` returned and the upload record keeps."""
    from azure.search.documents.aio import SearchClient
    from azure.core.credentials import AzureKeyCredential
    from backend.core.config import settings

    async with SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
    ) as search_client:
        await search_client.delete_documents([{"id": doc_id}])
    logger.info("Removed improve_evidence_index doc %s", doc_id)


async def _index_upload(case_id: str, upload_record: dict, *,
                        role: str, shape_match: str,
                        content_digest: str) -> str:
    """Index one evidence upload into `improve_evidence_index`. Returns its id.

    **Returns the document id rather than None** — §6 names
    `evidence_index_id` as what makes the evidence trail traversable, and
    before 6.11 this function computed the id and dropped it, so a reviewer
    reading a gate document had no way back to the indexed chunk.

    **The empty-text early return is gone.** It used to swallow every
    unparsed file silently (Part AP1); a file with nothing to index now
    cannot reach this function at all, because `parse_upload` refuses it at
    the route. An empty text here is therefore a real fault and raises, which
    the caller logs and turns into `indexed=False`.

    **Only evidence reaches this function** (ruling 3). The caller does that
    routing; nothing here re-checks it, because a second opinion on the same
    question is how two answers to it come to exist.
    """
    import hashlib
    from azure.search.documents.aio import SearchClient
    from azure.core.credentials import AzureKeyCredential
    from backend.core.config import settings
    from backend.knowledge.retriever import get_embeddings

    extracted_text = (upload_record.get("extracted_text") or "").strip()
    if not extracted_text:
        raise ValueError(
            f"No extracted text for {upload_record.get('filename')!r}. A "
            "parsed upload always has text; reaching here means the parse "
            "contract was bypassed."
        )

    embeddings = get_embeddings()
    embedding = await embeddings.aembed_query(extracted_text)

    doc_id = hashlib.sha256(
        f"{case_id}_{upload_record['filename']}_{upload_record['timestamp']}"
        .encode()
    ).hexdigest()[:32]

    # **`upload_phase` and `timestamp` KEEP THEIR NAMES**, now for a different
    # reason than before 6.13. They were the keys the reindex was to backfill
    # `phase` and `uploaded_at` from; the backfill has run, both are top-level
    # fields below, and these two stay because `scripts/backfill_evidence_index.py`
    # reads them for any document it has to reconstruct from the index alone
    # (DECISIONS Part AT2 — one live document has no case-blob record).
    metadata = json.dumps({
        "case_id": case_id,
        "upload_phase": upload_record.get("phase"),
        "content_type": upload_record.get("content_type"),
        "filename": upload_record.get("filename"),
        "blob_path": upload_record.get("blob_path"),
        "uploaded_by": upload_record.get("uploaded_by"),
        "timestamp": upload_record.get("timestamp"),
        # The deterministic parse (ruling 4), carried so a retrieved chunk can
        # say what shape it came from without a second read of the file.
        "kind": upload_record.get("kind"),
        "structure": upload_record.get("structure"),
        "columns": upload_record.get("columns") or [],
        "row_count": upload_record.get("row_count"),
    })

    # §23.2's seven, applied at 6.13. **Each is TOP-LEVEL, not a metadata key**
    # — that distinction is the whole of §23.4: a value buried in the metadata
    # blob is unreachable by `$filter`, with no error raised, which is exactly
    # how `phase_relevance` went unpopulated. All seven are server-set; a
    # Belt-entered value for any of them makes it unreliable as a filter or a
    # sort key.
    document = {
        "id": doc_id,
        "content": extracted_text,
        "content_vector": embedding,
        "metadata": metadata,
        "case_id": case_id,
        "phase": upload_record.get("phase") or "",
        "uploaded_at": upload_record.get("timestamp") or "",
        "role": role,
        # Derived from `role` upstream and carried, never re-derived here —
        # §23.2.1 makes an inconsistent pair unrepresentable by having one
        # source, and a second opinion on the same question is how two
        # answers to it come to exist.
        "kind": upload_record.get("kind") or "",
        # A PROJECTION of `UploadRecord.summary` (§23.2). The case blob is the
        # system of record; this copy exists because it must be searchable,
        # which the blob cannot serve. Changing the summary means re-indexing
        # the document, never editing this in place.
        "description": upload_record.get("summary") or "",
        "content_digest": content_digest,
        "shape_match": shape_match,
    }

    # The aio client owns an aiohttp session, so it is closed on the way
    # out rather than left to the garbage collector.
    async with SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
    ) as search_client:
        await search_client.upload_documents([document])
    logger.info(
        "Indexed %s -> improve_evidence_index doc %s",
        upload_record["filename"], doc_id,
    )
    return doc_id


def assemble_gate_document(
    case: CaseDocument, phase: str,
) -> tuple[dict[str, Any], dict[str, list[dict]]]:
    """The approved gate document, and the evidence that must travel with it.

    ═══════════════════════════════════════════════════════════════════════
    STEP 6.42 — THE WRITING DOOR USES THE READING DOOR'S FUNCTION
    ═══════════════════════════════════════════════════════════════════════
    `POST /gate` built its document from `phase_data.get("_validated", {})`.
    **Nothing in the tree has ever set `_validated`** — `validate_define` does
    not write it — so the expression resolved to `{}`, the document was written
    EMPTY, and the phase advanced anyway. The code's own comment had said so
    since step 4.2; it was unreachable while the gate could not pass, and steps
    6.48 and 6.20 made it reachable.

    `GET /gate/review` one route away has assembled correctly since 3.4 and
    returns a complete document on a real case as of `01e8f8a`. **This is not
    new logic** — it is `GATE_SPECS[phase].assemble`, called by the path that
    WRITES rather than only by the path that READS.

    **Extracted rather than left inline** so the step's own proofs drive the
    function that ships, not a copy of its logic — the same reason
    `apply_capture` was lifted out at 6.33.

    **It REFUSES rather than returning a partial document.** Assembly raising
    with the validator already satisfied is a CODE DEFECT (S-F28), not an
    incomplete phase, and writing anyway is what let a phase advance to Measure
    with nothing behind it. The caller never reaches its write, so the phase
    does not advance — the write is what advances it.

    Returns `(document, evidence)`, where `evidence` is the `citations` and
    `uploads` kwargs for `write_phase_gate`, read from the record ONCE here so
    the write cannot disagree with the document about what the phase rested on.
    """
    record = case.phases.get(phase)
    artifacts = dict((record.structured or {}) if record else {})
    evidence = {
        "citations": [c.model_dump() if hasattr(c, "model_dump") else dict(c)
                      for c in (getattr(record, "citations", None) or [])],
        "uploads": [u.model_dump() if hasattr(u, "model_dump") else dict(u)
                    for u in (getattr(record, "uploads", None) or [])],
        # G-147 (DEF-061) — the change log, read with the rest so the write hands it over.
        "field_log": [dict(e) for e in (getattr(record, "field_log", None) or [])],
    }
    rows = review_rows(phase, artifacts)
    gaps = [f"{r['field']} — Belt accepted gap"
            for r in rows if r["tier"] == 2 and not r["present"]]
    try:
        document = GATE_SPECS[phase].assemble(
            artifacts,
            citations=evidence["citations"],
            uploads=evidence["uploads"],
            acknowledged_gaps=gaps,
        ).model_dump()
    except Exception as exc:                        # noqa: BLE001
        logger.error(
            "gate assembly REFUSED for %s/%s, so the gate was NOT written and "
            "the phase did NOT advance: %s", case.case_id, phase, exc,
        )
        raise HTTPException(500, (
            "The gate document could not be assembled, so nothing was written "
            "and the phase did not advance. This is a defect in the system, "
            "not something to answer differently."
        ))
    return document, evidence


async def _pending_interrupts(case: CaseDocument, phase: str, user: str = "") -> tuple[Any, dict, list]:
    """(graph, config, the interrupts the case's graph holds) — R6's pause."""
    from backend.core.graph import get_graph
    graph = get_graph()
    config = _graph_config(case, phase, user, entry="decision")
    snapshot = await graph.aget_state(config)
    pending = [i for task in (snapshot.tasks or ()) for i in (getattr(task, "interrupts", ()) or ())]
    return graph, config, pending


async def _awaiting_decision(case: CaseDocument, phase: str) -> bool:
    """Is the Define report paused for the team's decision? Never raises — the
    review screen must render even when the checkpoint cannot be read."""
    try:
        _graph, _config, pending = await _pending_interrupts(case, phase)
    except Exception as exc:                        # noqa: BLE001
        logger.warning("gate review: could not read the pause for %s: %s", case.case_id, exc)
        return False
    return any((getattr(i, "value", None) or {}).get("kind") == "accept_define_report"
               for i in pending)


@router.post("/gate/decision", response_model=GateDecisionResponse)
async def decide_gate(request: GateDecisionRequest, http: Request) -> GateDecisionResponse:
    """R6 — approve or reject the Define report, RESUMING the paused graph.

    `POST /gate` validated the report and the graph paused in `gate_review`
    (`interrupt()`); this resumes it with `Command(resume=...)`. APPROVE: the
    graph assembles `final` and ends, and this route writes the gate document
    and advances the phase — the write that `POST /gate` made before R6, now
    only after the team's approval, with the actor recorded. REJECT: the graph
    re-opens the named element(s) and runs one coaching turn that guides the
    Belt back to the first of them; this route persists it as `/ask` does.
    Until R8 the Belt is the actor.
    """
    _bind(request.case_id, request.phase)   # T43 (DEF-129): every log line of the request names them
    from langgraph.types import Command

    if request.phase != "define":
        raise HTTPException(400, "Only Define has a report to accept (R6).")
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")
    case = await blob.load_case(request.case_id)
    if case is None:
        raise HTTPException(404, f"Case {request.case_id} not found")
    who = access.person(http, case, 'gate decision')          # ADR-0091 decision 3
    if who is not None:                              # decision 4: the session's person, never a typed name
        request = request.model_copy(update={"actor": who.full_name})
    _ensure_case_record(case)
    case = await _with_unfinished_work(case)   # ADR-0066
    graph, config, pending = await _pending_interrupts(case, request.phase, request.actor)
    if not any((getattr(i, "value", None) or {}).get("kind") == "accept_define_report"
               for i in pending):
        raise HTTPException(409, "The Define report is not awaiting a decision — "
                                 "submit it for acceptance first (POST /gate).")
    elements = sorted({element_of(e) for e in request.elements})
    # R6 amendment (DEF-100): the approval is recorded against the project lead, on behalf of the
    # team — until single sign-on (R8) the signed-in lead is the case's leader by name.
    if request.decision == "approve" and case.leader and request.actor.strip() != case.leader.strip():
        raise HTTPException(403, APPROVE_LEAD_ONLY.format(lead=case.leader))
    if request.decision == "reject":
        unknown = [e for e in elements if e not in DEFINE_FIELD_ORDER]
        if not elements or unknown or not request.reason.strip():
            raise HTTPException(422, "A rejection names at least one Define element "
                                     f"and a reason{'; unknown: ' + ', '.join(unknown) if unknown else ''}.")
        config["configurable"]["belt_action"] = "rejected"
    resume = {"decision": request.decision, "elements": elements, "reason": request.reason,
              "actor": request.actor,
              "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    try:
        result = await _run_turn(graph, Command(resume=resume), config, http)
    except ClientGone:
        raise HTTPException(499, "Client disconnected; decision abandoned (§47).")
    except HTTPException:
        raise                                       # T11 (DEF-115): a busy case is a 409, not a 500
    except StateSchemaVersionError as e:            # ADR-0065 (T88)
        raise HTTPException(409, str(e))
    except Exception as e:
        # ADR-0087 decision 3: the approval node undid both writes and re-raised, and its retries are spent —
        # nothing was committed and the report still awaits the decision; the lead approves again.
        from backend.core import graph as _graph
        logger.error("decide_gate() error: %s — the approval did not go through; nothing changed", e)
        raise HTTPException(503, _graph.APPROVAL_FAILED)

    if request.decision == "approve" and (getattr(_last_ai(result), "additional_kwargs", None) or {}).get("degraded"):
        # G-242: an approval whose run failed (its gate document could not be assembled) changed nothing — the
        # approval message, so the lead approves again.
        from backend.core import graph as _graph
        raise HTTPException(503, _graph.APPROVAL_FAILED)
    _refuse_degraded(result)                                   # T29 (DEF-122)
    if request.decision == "approve":
        # ADR-0087 decision 2: the approval node wrote both records — the Store's and the case's; the route
        # writes neither. Founder ruling 2026-10-21 (item 3): it answers "approved" only when it can see that
        # both exist and the phase advanced — never on a run that merely returned.
        from backend.core.store import get_store
        from backend.phases.mappers_common import read_gate_document
        stored = read_gate_document(get_store(), request.case_id, request.phase)
        after = await blob.load_case(request.case_id)
        if not (stored and after is not None and after.phases[request.phase].gate_passed
                and after.current_phase != request.phase):
            logger.error("decide_gate(): the approval ran but did not complete — Store record %s, case record %s, "
                         "phase %s", bool(stored), bool(after and after.phases[request.phase].gate_passed),
                         after.current_phase if after else None)
            raise HTTPException(500, APPROVAL_INCOMPLETE)
        idx = PHASE_ORDER.index(request.phase)
        next_phase = PHASE_ORDER[idx + 1] if idx < len(PHASE_ORDER) - 1 else None
        return GateDecisionResponse(
            decision="approve", phase=request.phase, next_phase=next_phase,
            message=f"The Define report is approved. {'Moving to ' + next_phase if next_phase else ''}".strip())

    reply = _last_ai(result)
    payload = conversation.transport(reply) if reply is not None else {}
    extra = dict(getattr(reply, "additional_kwargs", None) or {}) if reply else {}
    # ADR-0066: the rejection's coaching turn is in the checkpoint; the blob is not written.
    blocks = extra.get("coaching_blocks") or {}
    return GateDecisionResponse(
        decision="reject", phase=request.phase, reopened=elements,
        message=f"Back to coaching on {', '.join(e.replace('_', ' ') for e in elements)}.",
        answer=str(reply.content) if reply is not None else "",
        **{k: str(blocks.get(k) or "") for k in ("explanation", "example", "prompt", "progress")})


@router.post("/gate", response_model=GateSubmitResponse)
async def submit_gate(request: GateSubmitRequest,
                      http: Request) -> GateSubmitResponse:
    """Submit the phase for gate review — through the same compiled graph.

    **The same graph object as `/ask`** (§12, §49). The two differ only in the
    per-run `entry` on `config["configurable"]`, which the planner reads to
    decide whether this turn coaches or validates. There is no second dispatch
    table and no second runtime: `validate_map` and the five `validate_*`
    imports are gone, and the validator now runs where §34 puts it — inside
    `validation_stack`, in the subgraph.

    R6 (2026-09-26): FOR DEFINE THIS PAUSES. A validated Define report stops
    in `gate_review`'s `interrupt()` and this returns `awaiting_acceptance`
    with NOTHING written; `POST /gate/decision` resumes it, and only an
    approval writes the gate document and advances the phase. The other four
    phases, which have no report to accept yet, still write here when they pass.
    """
    _bind(request.case_id, request.phase)   # T43 (DEF-129): every log line of the request names them
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")
    case = await blob.load_case(request.case_id)
    if case is None:
        raise HTTPException(404, f"Case {request.case_id} not found")
    who = access.person(http, case, 'gate submission')          # ADR-0091 decision 3
    if who is not None:
        request = request.model_copy(update={"submitted_by": who.full_name})
    # WATCH 19's lazy half — /gate enters a phase subgraph too, so the input
    # mapper runs here as well and needs the same record.
    _ensure_case_record(case)
    case = await _with_unfinished_work(case)   # ADR-0066

    from backend.core.graph import PhaseNotWired, get_graph

    phase = _requested_phase(case, request.phase)
    graph = get_graph()
    config = _graph_config(case, phase, request.submitted_by, entry="gate")

    try:
        state = await _graph_input(graph, config, case, [])
        # §47 requirement 1 — ABANDON, the same shape `/ask` uses. A gate
        # submission is the LAST turn that may complete behind a departed
        # Belt: it is the one the whole nine-step gate exists to keep in
        # front of them.
        result = await _run_turn(graph, state, config, http)
    except ClientGone:
        logger.info(
            "submit_gate() ABANDONED for %s/%s — client disconnected mid-turn",
            request.case_id, request.phase,
        )
        raise HTTPException(499, "Client disconnected; turn abandoned (§47).")
    except PhaseNotWired as e:
        raise HTTPException(501, str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("submit_gate() error: %s", e)
        from backend.core.prompts import SUBMIT_FAILED
        raise HTTPException(500, SUBMIT_FAILED)        # G-261 (audit W8)

    if result.get("__interrupt__"):
        # R6 — the Define report passed validation and the graph PAUSED in
        # `gate_review` for the team's decision. Nothing is written until
        # POST /gate/decision resumes it with an approval.
        await _clear_escalation(request.case_id)                    # ADR-0076: a pass clears it
        return GateSubmitResponse(
            passed=True, phase=request.phase, awaiting_acceptance=True,
            message=("The Define report is ready for your team's review. Approve it, "
                     "or reject it naming what needs to change."))

    _refuse_degraded(result)                                   # T29 (DEF-122)
    reply = _last_ai(result)
    payload = conversation.transport(reply) if reply is not None else {}
    verdict = dict(payload.get("gate_verdict") or {})
    phase_data = dict(payload.get("v1_draft") or {})
    passed = bool(verdict.get("passed", False))
    missing = list(verdict.get("missing") or [])

    if passed:
        # ── 6.42 — THE WRITING DOOR NOW USES THE READING DOOR'S FUNCTION ──
        #
        # This read `phase_data.get("_validated", {})`. **Nothing in the tree
        # has ever set `_validated`** — `validate_define` does not write it —
        # so the expression resolved to `{}` and the gate document was written
        # EMPTY, while the phase advanced and the Belt was moved to Measure.
        # The code's own comment had said so since 4.2; it was unreachable
        # while the gate could not pass, and 6.48 and 6.20 made it reachable.
        #
        # `GET /gate/review` one route away already assembles correctly and
        # has returned a complete document on a real case since 01e8f8a. **This
        # is not new logic. It is the same assembly, called by the path that
        # WRITES rather than only by the path that READS.**
        document, evidence = assemble_gate_document(case, request.phase)

        await blob.write_phase_gate(
            case_id=request.case_id,
            phase=request.phase,
            structured=document,
            submitted_by=request.submitted_by,
            summary=f"Gate passed by {request.submitted_by}",
            # Passed EXPLICITLY, from what assembly already read. The old call
            # passed neither, and the `[]` defaults then replaced the Belt's
            # evidence trail with nothing at the one moment a reviewer goes
            # looking for it.
            citations=evidence["citations"],
            uploads=evidence["uploads"],
            field_log=evidence["field_log"],                    # G-147 (DEF-061)
        )
        await _clear_escalation(request.case_id)                    # ADR-0076: a pass clears it
        idx = PHASE_ORDER.index(request.phase)
        next_phase = (
            PHASE_ORDER[idx + 1] if idx < len(PHASE_ORDER) - 1 else None
        )
        return GateSubmitResponse(
            passed=True,
            phase=request.phase,
            message=(
                f"Phase complete. "
                f"{'Moving to ' + next_phase if next_phase else 'Project complete!'}"
            ),
            next_phase=next_phase,
        )

    # ADR-0072 point 5 — a parked element blocks submission (every Define element is Tier 1),
    # and the refusal names it.
    from backend.core import guard_messages
    from backend.phases import moves
    record = case.phases.get(request.phase)
    held = moves.parked(request.phase, dict(getattr(record, "field_status", None) or {}))
    names = ", ".join(guard_messages.element_name(request.phase, f) for f in held)
    escalated = bool(verdict.get("escalated"))
    told = _escalated_to(case, request.phase, request.submitted_by) if escalated else ""
    if escalated:
        # ADR-0076 (T65): the third failure — the report is held for the lead; the case stays open.
        # G-192: when the lead submits, the Champion is told.
        await blob.set_escalation(request.case_id, {
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "attempts": int(verdict.get("attempts") or verdict.get("gate_attempts") or 0),
            "criteria": [m.replace("_", " ") for m in missing], "to": told})
    return GateSubmitResponse(
        passed=False,
        phase=request.phase,
        missing_fields=[f.replace("_", " ") for f in missing],
        failed_checks=_failed_checks(request.phase, verdict),
        escalated=escalated,
        message=(GATE_ESCALATED.format(who=told, criteria="; ".join(m.replace("_", " ") for m in missing))
                 if escalated else
                 (f"Parked: {names}. Complete {'it' if len(held) == 1 else 'them'} to submit. " if held else "")
                 + f"Not quite ready yet. {len(missing)} item(s) still needed."),
    )


def _failed_checks(phase: str, verdict: dict[str, Any]) -> list[dict[str, str]]:
    """G-193 — what failed, by element, from the gate's own verdict: each failed rubric criterion (layer 2d)
    with its reason, else each element still missing (layer 2b). `element` is the position a revise opens."""
    from backend.core import guard_messages
    from backend.phases import moves
    position = {f: field for field, fields in moves.positions(phase) for f in fields}
    out: list[dict[str, str]] = []
    if phase == "define":
        from backend.validation.rubric import DEFINE_CRITERIA
        field_of = {cid: field for cid, field, _ in DEFINE_CRITERIA}
        for v in verdict.get("verdicts") or []:
            if isinstance(v, dict) and v.get("status") == "fail":
                element = position.get(field_of.get(str(v.get("criterion")), ""), field_of.get(str(v.get("criterion")), ""))
                out.append({"criterion": str(v.get("criterion")), "element": element,
                            "element_name": guard_messages.element_name(phase, element),
                            "reason": str(v.get("feedback") or "")})
    if not out:
        for f in verdict.get("missing") or []:
            if " — " in str(f):
                continue
            element = position.get(str(f), str(f))
            out.append({"criterion": "", "element": element,
                        "element_name": guard_messages.element_name(phase, element), "reason": "Not confirmed yet."})
    return out


def _refuse_degraded(result: Any) -> None:
    """T29 (DEF-122): a gate run whose node failed ended in the degraded reply (`graph.degraded_handler`)
    — nothing was changed. The gate routes answer 503 with it, never "not ready" or a 500."""
    reply = _last_ai(result)
    if reply is not None and (getattr(reply, "additional_kwargs", None) or {}).get("degraded"):
        from backend.core.graph import DEGRADED_REPLY
        raise HTTPException(503, DEGRADED_REPLY)


#: R6 amendment (DEF-100) — an approval sent by someone other than the project lead.
APPROVE_LEAD_ONLY = ("Only the project lead, {lead}, approves the Define report, on behalf of the team. "
                     "Ask {lead} to approve it — or reject it naming what to change, which anyone may do.")

#: Founder ruling 2026-10-21 (ADR-0087 amendment, item 3): the approval ran but the route cannot see both records
#: and the phase moved on, so it is not reported as approved.
APPROVAL_INCOMPLETE = ("The approval ran but was not saved completely, so the Define report is not shown as "
                       "approved. Please open the report again before approving.")


#: ADR-0076 (T65) — said in code on the third failed submission; the case stays open. G-192: it reads as
#: information, and names who was told — the Champion when the project lead submitted.
GATE_ESCALATED = ("For your information: the report has not passed three times, so {who} has been told, to "
                  "help decide the next step with you. What still fails: {criteria}. You can keep working on "
                  "these with the coach and submit again.")


def _escalated_to(case: Any, phase: str, submitted_by: Optional[str]) -> str:
    """G-192 — who an escalation goes to, in words: the project lead; the Champion when the lead submitted
    (ADR-0076 escalates to someone other than the person submitting)."""
    lead = str(getattr(case, "leader", "") or "").strip()
    if lead and " ".join(str(submitted_by or "").split()).lower() != " ".join(lead.split()).lower():
        return f"the project lead, {lead}"
    from backend.phases.define.report import champion_of
    record = (getattr(case, "phases", None) or {}).get(phase)
    champion = champion_of(((getattr(record, "structured", None) or {}).get("team")))
    return (f"the Champion, {champion['name']}" if champion and champion.get("name")
            else "the Champion (the team names none yet — add one under Project and team)")


async def _clear_escalation(case_id: str) -> None:
    """ADR-0076: a passing submission takes the case off the lead's list. A registry that cannot be
    written must not undo the pass — logged."""
    try:
        await blob.set_escalation(case_id, None)
    except Exception as exc:  # noqa: BLE001
        logger.warning("case %s: the escalation could not be cleared in the registry (%s)", case_id, exc)


@router.get("/registry", response_model=list[RegistryEntryOut])
async def get_registry() -> list[RegistryEntryOut]:
    """Management dashboard — returns all cases from registry."""
    from backend.phases.status import days_in_phase
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")
    registry = await blob.load_registry()
    return [
        RegistryEntryOut(
            case_id=e.case_id,
            title=e.title,
            belt_level=e.belt_level,
            leader=e.leader,
            department=e.department,
            current_phase=e.current_phase,
            days_in_phase=days_in_phase(e),                       # DEF-204: computed, as project_status does
            rag_status=e.rag_status,
            status=e.status,
            escalation=getattr(e, "escalation", None),           # ADR-0076
            phase_summary=e.phase_summary.model_dump(),
        )
        for e in registry.cases
    ]


@router.get("/cases/{case_id}")
async def get_case(case_id: str, http: Request):
    """Load full case document. Also projects every per-phase upload
    into a flat ``files`` array in CaseFile shape so the UI can render
    a single grouped files panel without walking each phase record."""
    _bind(case_id, None)   # T43 (DEF-129): every log line of the request names them
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")
    case = await blob.load_case(case_id)
    if case is None:
        raise HTTPException(404, f"Case {case_id} not found")
    who = access.person(http, case, 'open case')          # ADR-0091 decision 3
    lost: list[str] = []
    case = await _with_unfinished_work(case, lost=lost)   # ADR-0066: read through the graph

    payload = case.model_dump()
    if lost:                                       # G-261 (audit W3): never a silent fall-back
        from backend.core.prompts import RELOAD_UNFINISHED_LOST
        payload["notice"] = RELOAD_UNFINISHED_LOST
    # W9 (DEF-079) — the progress view's elements, computed here once from the statuses the
    # coaching moves read: confirmed (a Change action), parked (ADR-0072's marker), current, open.
    from backend.core import guard_messages
    from backend.phases import moves
    define = case.phases.get("define")
    payload["define_elements"] = moves.element_rows(
        "define", dict((define.structured if define else None) or {}),
        dict((define.field_status if define else None) or {}),
        lambda f: guard_messages.element_name("define", f))
    # DEF-053 — the screen's progress bar reads "n of 13" from the function the reply's step uses.
    from backend.phases.define.schema import define_progress
    payload["define_progress"] = define_progress(dict((define.structured if define else None) or {}))
    # DEF-204 (W2): the project's status, computed once — the bar, the chat, the overview and Submit all read it.
    from backend.phases.status import project_status
    payload["project_status"] = project_status(
        case, payload["define_elements"] if case.current_phase == "define" else [],
        "The Define report waits for your team's decision." if (
            case.current_phase == "define" and await _awaiting_decision(case, "define")) else None)
    # DEF-214 (W1): the Define overview, served from the skill (its opening and section F).
    from backend.phases.define.welcome import briefings, overview
    payload["define_overview"] = overview()
    payload["define_briefings"] = briefings()      # G-258 (audit D6): the tool briefings, from the skill
    # DEF-200 (W3): the welcome, assembled in code from the phase state and the skill — greeting the signed-in person.
    if case.current_phase == "define":
        from backend.phases.define.welcome import welcome
        payload["welcome"] = welcome(str(getattr(who, "full_name", "") or ""),
                                     dict((define.structured if define else None) or {}),
                                     dict((define.field_status if define else None) or {}))
    files: list[dict] = []
    for phase_name, phase_record in (payload.get("phases") or {}).items():
        for upload in (phase_record or {}).get("uploads") or []:
            filename = upload.get("filename", "")
            uploaded_at = upload.get("uploaded_at", "")
            files.append({
                "file_id": _case_file_id(case_id, filename, uploaded_at),
                "filename": filename,
                "phase": phase_name,
                "purpose": _purpose_from_classification(
                    upload.get("classification", ""), filename
                ),
                "blob_url": upload.get("blob_path", ""),
                "uploaded_at": uploaded_at,
                "uploaded_by": upload.get("uploaded_by", ""),
                "size_bytes": None,
            })
    payload["files"] = files
    return payload


def _build_captured_fields(phase_data: dict, phase: str) -> list:
    """Build captured fields list for right panel UI."""
    fields = []
    for key, value in phase_data.items():
        if key.startswith("_"):
            continue
        if value is None or value == [] or value == "":
            continue
        fields.append(
            CapturedField(
                label=key.replace("_", " ").title(),
                value=(
                    str(value)[:200]
                    if not isinstance(value, list)
                    else f"{len(value)} item(s)"
                ),
                ai_suggested=key in ("ai_suggested_factors",),
            )
        )
    return fields


def _define_next_steps(extra: dict) -> list[str]:
    """DEF-095: the next steps under a Define reply, from the element it works on and its card (phases/status.py)."""
    from backend.core import guard_messages
    from backend.phases.status import next_steps
    field = str((extra.get("coaching_move") or {}).get("field") or "")
    return next_steps(guard_messages.element_name("define", field) if field else "", extra.get(conversation.CARD_KEY))


def _build_chips(phase: str, phase_data: dict) -> list[str]:
    """Build 2-3 suggestion chips based on what is still missing."""
    missing = phase_data.get("_missing_fields", [])
    chips_map = {
        "define": [
            "How do I write a good problem statement?",
            "What should the project target look like?",
            "Who should be the process owner?",
        ],
        "measure": [
            "How many records do we need?",
            "Do we need to check our measurement tool?",
            "What format should the data export be in?",
        ],
        "analyse":       [
            "How do we verify a root cause?",
            "What analysis tools can we use here?",
            "How do we build a fishbone diagram?",
        ],
        "improve": [
            "How do we evaluate solution options?",
            "What should a pilot plan contain?",
            "How do we measure pilot success?",
        ],
        "control": [
            "What goes in a control plan?",
            "How do we set control limits?",
            "What should the handover document contain?",
        ],
    }
    return chips_map.get(phase, [])[:3]


__all__ = ["router"]
