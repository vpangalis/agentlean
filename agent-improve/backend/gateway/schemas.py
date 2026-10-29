from __future__ import annotations

from typing import Literal, Optional, Any, List

from pydantic import BaseModel


# ── inbound ───────────────────────────────────────────────────────────────


class PersonIn(BaseModel):
    """ADR-0090 "The people on a case": a person as the create form or the team panel gives them. Full name and
    role are required; the e-mail only before the person signs in (ruling a); location as ADR-0089 lists it."""

    full_name: str
    email: str = ""
    role: str = ""
    function: str = ""
    department: str = ""
    location: dict[str, str] = {}


class CaseCreateRequest(BaseModel):
    """Create a new improvement case."""

    title: str
    belt_level: str              # yellow | green | black
    leader: str = ""             # the lead's name — read when `lead` is not given (before ADR-0090)
    department: str
    target_date: str             # ISO date string
    team: list[dict[str, str]] = []   # [{name, role}] — read when `people` is not given (before ADR-0090)
    #: ADR-0090: the creator, who becomes the project lead, and the other members, with their details.
    lead: Optional[PersonIn] = None
    people: list[PersonIn] = []


class PersonChange(BaseModel):
    """ADR-0090 team panel: the lead (`actor`) adds a person, completes one's details, or confirms a proposed
    member — with an e-mail (ruling b)."""

    actor: str
    person: PersonIn


class PersonRemoval(BaseModel):
    """DEF-104 (R8b): the lead (`actor`) removes a member from the case."""

    actor: str


class LeadHandover(BaseModel):
    """DEF-105 (R8c): the lead (`actor`) hands the lead role `to` a registered member, saying why."""

    actor: str
    to: str
    reason: str = ""


class AskRequest(BaseModel):
    """One conversational turn from the team."""

    case_id: str
    user: str                    # name of team member sending this turn
    message: str                 # what they typed
    phase: str                   # current phase — UI sends this for routing
    # R4 — the Belt's Confirm or Change button under a read-back.
    # A click sets the field's status in code; no model reads it.
    action: Optional[Literal["confirm", "change", "park", "try_again", "revise", "link_add"]] = None   # R-H: link_add
    # W9 (DEF-079) — with action "revise": the element picked in the progress view.
    element: Optional[str] = None


class UploadMetaRequest(BaseModel):
    """Metadata sent alongside a file upload."""

    case_id: str
    uploaded_by: str
    phase: str


class GateSubmitRequest(BaseModel):
    """Team requests gate review for current phase."""

    case_id: str
    submitted_by: str
    phase: str


# ── outbound ──────────────────────────────────────────────────────────────


class CitationOut(BaseModel):
    agent_origin: str
    index_name: str
    document_id: str
    relevance_summary: str
    #: DEF-110 (W13): the file and the PDF page a reply drew on — read in code from the turn's tools.
    source_file: str = ""
    page: Optional[int] = None


class CapturedField(BaseModel):
    """One field shown in the right-panel capture view."""

    label: str                              # plain language label
    technical_label: Optional[str] = None   # methodology term shown as grey subtext
    value: Optional[str] = None             # None = not yet captured
    ai_suggested: bool = False              # True = purple styling in UI
    required_for_gate: bool = True


class GateStatus(BaseModel):
    phase: str
    passed: bool
    attempts: int
    missing_fields: list[str] = []          # plain language field names


class AskResponse(BaseModel):
    """What the backend returns for every conversational turn."""

    answer: str                                  # Orchestrator plain language response
    phase: str                                   # current phase
    captured_fields: list[CapturedField] = []    # right panel content
    phase_inputs: Optional[dict] = None          # full structured dict for live UI sync
    gate_status: GateStatus
    citations: list[CitationOut] = []
    suggestion_chips: list[str] = []             # 2-3 suggested follow-up questions
    sipoc_diagram: Optional[dict] = None         # SIPOC map; draft:True when AI-generated
    visualisation: Optional[dict] = None         # inline visual payload (e.g. 5W2H mindmap)
    section_completed: Optional[str] = None      # which Gate section just completed this turn
    escalated: bool = False
    # The reply's render contract, beside `answer` (which stays the `message`
    # block). Defaulted: a missing block is a finding, never a failed turn.
    explanation: str = ""
    example: str = ""                            # an illustration, never the Belt's data
    prompt: str = ""                             # the one ask of this turn
    progress: str = ""                           # "Define · n of 13 confirmed" (define_progress)
    grader_warning: Optional[str] = None         # the grader's Belt-visible warning (G-76)
    # R4 — the move this reply made and its field, so the screen
    # shows Confirm / Change under a read-back and nothing else decides that.
    move: Optional[str] = None
    move_field: Optional[str] = None
    # ADR-0067 (R20, T93): the threat when the guard or a limit refused the turn — the screen then
    # keeps the typed text in the box. None on an ordinary turn.
    blocked: Optional[str] = None
    # R-F (founder ruling 2026-10-27): the turn failed after its automatic retry ("degraded") or reached the hard
    # limit with no answer ("time") — the screen puts the Belt's message back in the box with Send again.
    failed: Optional[Literal["degraded", "time"]] = None
    # ADR-0093 "Element templates and the Gate view": the read-back's criteria card (Confirm opens only when
    # `confirm`), the strip after a Confirm, and the element the reply works on ("Element n of 13 · name").
    readback_card: Optional[dict] = None
    confirmed_strip: Optional[dict] = None
    reply_element: Optional[dict] = None
    #: DEF-212 — after Define's last Confirm: {title, steps} — read the report, submit, the team decides.
    completion_card: Optional[dict] = None
    #: R-C (ADR-0114) — a teaching turn's element card, assembled in code: the trail, the saved note, title and
    #: purpose, YOUR TURN, the example, the help links. The page draws it in place of the reply's text.
    teaching_card: Optional[dict] = None
    #: R-H — under the SIPOC's link check: {flagged: [{n, name, notes}], add, keep} — the page draws the two buttons.
    link_check: Optional[dict] = None


class CaseCreateResponse(BaseModel):
    case_id: str
    title: str
    current_phase: str = "define"
    message: str = "Case created. Define phase is now active."


class SignInInfo(BaseModel):
    """ADR-0091 / W17: what the sign-in window says, and whether this case asks for sign-in yet (ruling b)."""

    case_id: str
    title: str
    lead: str
    required: bool
    message: str
    not_on_team: str


class SignInIn(BaseModel):
    """ADR-0091 decision 2: the company e-mail the lead registered; ADR-0105: with the person's one-time code (an
    e-mail alone signs in only in development and demos)."""

    email: str
    code: str = ""


class CodeIssued(BaseModel):
    """ADR-0105 decision 2: the one-time code, shown once to the lead, and when it expires."""

    full_name: str
    code: str
    expires_at: str


class SessionOut(BaseModel):
    """ADR-0091: who the session is for."""

    case_id: str
    full_name: str
    email: str
    role: str = ""
    is_lead: bool = False


class PersonOut(BaseModel):
    """ADR-0090: a person on the case as the team panel shows them."""

    full_name: str
    email: str = ""
    role: str = ""
    function: str = ""
    department: str = ""
    location: dict[str, str] = {}
    status: str = "member"
    is_lead: bool = False


class PeopleResponse(BaseModel):
    """ADR-0090: everyone on the case, the lead first; `lead` is the one display name of the lead."""

    case_id: str
    lead: str
    people: list[PersonOut]


class GateSubmitResponse(BaseModel):
    passed: bool
    phase: str
    missing_fields: list[str] = []          # plain language — shown to team
    message: str                            # Orchestrator plain language feedback
    next_phase: Optional[str] = None        # set when gate passes
    #: R6 — the Define report passed validation and the graph is PAUSED for the
    #: team's decision (POST /gate/decision); nothing has been written yet.
    awaiting_acceptance: bool = False
    #: ADR-0076 (T65) — the third failed submission: the report is held for the project lead.
    escalated: bool = False
    #: G-193 — the server's failing checks, one per element: {criterion, element, element_name, reason}.
    #: The result screen draws these and nothing else; `element` is the position the "work on it" link opens.
    failed_checks: list[dict[str, str]] = []


class GateDecisionRequest(BaseModel):
    """R6 — the Belt (with the team) approves or rejects the Define report.

    Until R8 (docs/requirements/platform.md) the Belt approves and is recorded
    as `actor`. A rejection names the element(s) to change and why."""

    case_id: str
    phase: str
    decision: Literal["approve", "reject"]
    actor: str
    elements: list[str] = []
    reason: str = ""


class GateDecisionResponse(BaseModel):
    decision: str
    phase: str
    message: str
    next_phase: Optional[str] = None        # set on approval
    reopened: list[str] = []                # set on rejection: the elements back in coaching
    #: On rejection, the coach's guidance back to the first re-opened element.
    answer: str = ""
    explanation: str = ""
    example: str = ""
    prompt: str = ""
    progress: str = ""


class RegistryEntryOut(BaseModel):
    """Management dashboard row."""

    case_id: str
    title: str
    belt_level: str
    leader: str
    department: str
    current_phase: str
    days_in_phase: int
    rag_status: str
    status: str
    escalation: Optional[dict[str, Any]] = None        # ADR-0076 (T65)
    phase_summary: dict[str, Any] = {}


# ── health ────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str = "ok"
    agent: str = "agent-improve"
    port: int = 8020
    version: str = "0.1.0"
    #: W16 (DEF-113): whether a turn can run — storage configured, no required credential missing; no model call.
    ready: bool = True
    #: Why not, in plain words; "" when ready.
    reason: str = ""


# ── case files ────────────────────────────────────────────────────────────


class CaseFile(BaseModel):
    """One uploaded file attached to a case. Shape returned by /upload
    and embedded as a flat list on the /cases/{case_id} response.
    Persistence is currently stored under phases[phase].uploads as
    UploadRecord; the gateway projects those into CaseFile shape on
    read so the UI sees a single flat list grouped by phase."""

    file_id: str                       # deterministic hash
    filename: str                      # original filename
    phase: str                         # which phase this belongs to
    purpose: str                       # auto-tagged or user-supplied
    blob_url: str                      # Azure blob URL / path
    uploaded_at: str                   # ISO timestamp
    uploaded_by: str                   # user name
    size_bytes: Optional[int] = None


# ── session summarisation ────────────────────────────────────────────────


class SummariseTurn(BaseModel):
    role: str          # "user" or "ai"
    user: str = ""     # team member name, blank for AI turns
    text: str
    timestamp: str = ""


class SummariseRequest(BaseModel):
    turns: list[SummariseTurn]
    phase: str
    case_title: str = ""


class SummariseResponse(BaseModel):
    summary: str


# ── session re-entry context ──────────────────────────────────────────────


class GateReviewField(BaseModel):
    """One reviewable field, carrying the tier that decides what it costs."""

    field: str
    label: str
    tier: int                    # 1 blocks the gate · 2 warns only
    value: object | None = None
    present: bool = False
    structured: bool = False     # dict/list — rendered, not free-typed


class GateReviewResponse(BaseModel):
    """The assembled gate document, shown BEFORE approval (§9.1 steps 3–4).

    `document` is populated only when every Tier 1 field is present — that is,
    only when assembly would succeed. A gate MAY pass with warnings; it may
    never pass with failures (§35).
    """

    phase: str
    passed: bool
    missing_fields: list[str] = []       # Tier 1 only — these block
    fields: list[GateReviewField] = []
    acknowledged_gaps: list[str] = []    # Tier 2 the Belt is proceeding past
    document: dict | None = None
    field_counts: dict = {}              # {total, tier_1, tier_2, captured}
    #: R5 — Define only: the seven-section Define report, from confirmed values
    #: (`phases/define/report.define_report`); None for the other phases.
    report: dict | None = None
    #: R6 — a Define report is paused for the team's decision (the graph holds
    #: an interrupt); the screen shows Approve / Reject rather than Submit.
    awaiting_decision: bool = False
    #: R11 (DEF-101) — when the phase was approved (the record's approval stamp, `submitted_at`), or None: the
    #: page prints a report only once this is set.
    approved_at: str | None = None
