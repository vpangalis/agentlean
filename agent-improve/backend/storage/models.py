from __future__ import annotations

from typing import Optional, Any

from pydantic import BaseModel, Field

from backend.core.citations import CitationRecord


class TeamMemberRecord(BaseModel):
    name: str
    role: str


class UploadRecord(BaseModel):
    """One Belt-uploaded file, as held in `PhaseRecord.uploads` (S-C09).

    **`ask_id` and `version` are RESERVED FOR STEP 6.12 and written `None`
    here.** 6.12's ask-binding is what fills them: an upload is bound to the
    coach's request that prompted it, never inferred from its filename
    (`DECISIONS.md` Part AP2 ruling 2), and the ask is the logical identity of
    which files are versions. They are declared one step early on §23.2's
    `phase` / `uploaded_at` precedent — RATIFIED, NOT YET APPLIED — so that no
    upload written between 6.11 and 6.12 lacks a place to record which ask it
    answered. Reconstructing that afterwards is exactly what ruling 2 forbids,
    which is why the alternative is a backfill with no source. Part AP5.
    """

    filename: str
    blob_path: str
    uploaded_by: str
    uploaded_at: str
    classification: str               # e.g. maintenance_log, operational_data
    rows: Optional[int] = None

    # RESERVED FOR 6.12 — declared, never written at 6.11. See the docstring.
    ask_id: Optional[str] = None
    version: Optional[int] = None


class ChartRecord(BaseModel):
    type: str                         # e.g. histogram, i_mr_chart, fishbone
    blob_path: str


class AnalystOutputRecord(BaseModel):
    summary: str
    charts: list[ChartRecord] = []
    generated_at: str


class PhaseRecord(BaseModel):
    """One DMAIC phase record — stored under phases.{phase_name} in blob."""

    gate_passed: bool = False
    submitted_by: Optional[str] = None
    submitted_at: Optional[str] = None
    structured: Optional[dict[str, Any]] = None   # validated PhaseInput.model_dump()
    analyst_output: Optional[AnalystOutputRecord] = None
    citations: list[CitationRecord] = []
    uploads: list[UploadRecord] = []


class PhaseSummaryRecord(BaseModel):
    """Lightweight summary written to registry on gate pass."""

    define: Optional[str] = None
    measure: Optional[str] = None
    analyse: Optional[str] = None
    improve: Optional[str] = None
    control: Optional[str] = None


class CaseDocument(BaseModel):
    """Full case record — serialised to case_{id}.json in blob."""

    case_id: str
    title: str
    belt_level: str                   # yellow | green | black
    leader: str
    department: str
    team: list[TeamMemberRecord] = []
    created_at: str
    target_date: str
    current_phase: str = "define"
    status: str = "active"            # active | complete | escalated | closed

    phases: dict[str, PhaseRecord] = Field(
        default_factory=lambda: {
            "define":        PhaseRecord(),
            "measure":       PhaseRecord(),
            "analyse":       PhaseRecord(),
            "improve":       PhaseRecord(),
            "control":       PhaseRecord(),
        }
    )

    conversation_history: list[dict[str, Any]] = []

    @classmethod
    def new(
        cls,
        case_id: str,
        title: str,
        belt_level: str,
        leader: str,
        department: str,
        target_date: str,
        team: list[dict],
    ) -> "CaseDocument":
        """Factory for creating a new case."""
        from datetime import datetime, timezone

        return cls(
            case_id=case_id,
            title=title,
            belt_level=belt_level,
            leader=leader,
            department=department,
            target_date=target_date,
            created_at=datetime.now(timezone.utc).isoformat(),
            team=[TeamMemberRecord(**m) for m in team],
        )


class RegistryEntry(BaseModel):
    """One row in registry.json — what the management dashboard reads."""

    case_id: str
    title: str
    belt_level: str
    leader: str
    department: str
    created_at: str
    target_date: str
    current_phase: str
    phase_started_at: Optional[str] = None
    days_in_phase: int = 0
    rag_status: str = "green"         # green | amber | red
    status: str = "active"
    phase_summary: PhaseSummaryRecord = Field(
        default_factory=PhaseSummaryRecord
    )


class CaseRegistry(BaseModel):
    """Full registry.json contents."""

    cases: list[RegistryEntry] = []
    last_updated: str = ""
