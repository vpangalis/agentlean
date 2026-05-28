from __future__ import annotations

from typing import Optional, Any

from pydantic import BaseModel


# ── inbound ───────────────────────────────────────────────────────────────


class CaseCreateRequest(BaseModel):
    """Create a new improvement case."""

    title: str
    belt_level: str              # yellow | green | black
    leader: str                  # team leader name
    department: str
    target_date: str             # ISO date string
    team: list[dict[str, str]]   # [{name, role}]


class AskRequest(BaseModel):
    """One conversational turn from the team."""

    case_id: str
    user: str                    # name of team member sending this turn
    message: str                 # what they typed
    phase: str                   # current phase — UI sends this for routing


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
    gate_status: GateStatus
    citations: list[CitationOut] = []
    suggestion_chips: list[str] = []             # 2-3 suggested follow-up questions
    sipoc_diagram: Optional[dict] = None         # SIPOC map; draft:True when AI-generated
    visualisation: Optional[dict] = None         # inline visual payload (e.g. 5W2H mindmap)
    section_completed: Optional[str] = None      # which Gate section just completed this turn
    escalated: bool = False


class CaseCreateResponse(BaseModel):
    case_id: str
    title: str
    current_phase: str = "define"
    message: str = "Case created. Define phase is now active."


class GateSubmitResponse(BaseModel):
    passed: bool
    phase: str
    missing_fields: list[str] = []          # plain language — shown to team
    message: str                            # Orchestrator plain language feedback
    next_phase: Optional[str] = None        # set when gate passes


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
    phase_summary: dict[str, Any] = {}


# ── health ────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str = "ok"
    agent: str = "agent-improve"
    port: int = 8020
    version: str = "0.1.0"


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
