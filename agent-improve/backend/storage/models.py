from __future__ import annotations

from typing import Optional, Any

from pydantic import BaseModel, Field

from backend.core.citations import CitationRecord


class TeamMemberRecord(BaseModel):
    name: str
    role: str


class UploadInterpretation(BaseModel):
    """What one upload MEANS — the single model call the parse is allowed.

    **Ruling 4: parse is deterministic first, and only meaning costs a model
    call, once, at ingest.** Every field here is a judgment the file itself
    cannot state; the columns, types and ranges that this call is *given* were
    read off the file by `upload/parsers.py` and are never asked for back.
    One call per upload, not one per question about the upload.

    **`source_filename` and `source_blob_path` are ruling 6.** §50's
    traceability binds on computed figures, not only quotations: a baseline
    derived from an uploaded extract must be followable back to the file it
    came from, or the gate document shows a number whose provenance stops at
    the coach. They travel with the interpretation so that whatever consumes
    it downstream cannot separate the two. **Step 6.12 is where a computation
    tool consumes this and writes to `computation_results`** — the citation
    exists now so that the write has something true to carry.
    """

    summary: str = Field(
        description="2-3 plain sentences: what this file is and what it shows."
    )
    supports: list[str] = Field(
        default_factory=list,
        description="What this file could substantiate for the project.",
    )
    caveats: list[str] = Field(
        default_factory=list,
        description="Gaps, ambiguities or limits a coach should raise.",
    )
    source_filename: str = ""
    source_blob_path: str = ""


class UploadRecord(BaseModel):
    """One Belt-uploaded file, as held in `PhaseRecord.uploads` (S-C09).

    **This record is the case-blob half of the §6 uploads entry shape.** The
    §6 shape a gate document reads is `evidence_index_id`, `filename`, `phase`,
    `uploaded_at`, `summary` (plus the two reserved fields); `phase` is the key
    this record is stored under rather than a field on it, and the rest are
    here. `to_phase_state_entry` below is the one place the two shapes are
    reconciled, so they cannot drift apart in four mappers' worth of copies.

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

    #: Row count from the deterministic parse. **Declared since before the
    #: refactor and written by nothing until 6.11** (Part AP1) — the parse is
    #: what finally gives it a writer.
    rows: Optional[int] = None

    #: The document's function in the project, from §23.2.1's ratified
    #: twelve-row vocabulary. **With `case_id` this is the LOGICAL IDENTITY**
    #: (ruling AP2.2): supersession resolves on `(case_id, role)`, and files
    #: are versions of the ask, never identified by filename.
    #: From the ask when the upload was solicited; from the Belt's declared
    #: purpose when it was not.
    role: str = "other evidence"

    #: `full` | `partial` | `none` | `unsolicited` — whether the file matched
    #: the ask's expected shape. **A mismatch is a coaching question, not a
    #: rejection**, so this records the answer rather than blocking the upload.
    shape_match: str = "unsolicited"

    #: SHA-256 of the uploaded bytes. **VERSION IDENTITY** — the same bytes
    #: re-uploaded are not a new version, and a different digest under the
    #: same `(case_id, role)` supersedes.
    content_digest: str = ""

    #: evidence | artefact (ruling 3). **The destination, not the format.**
    #: Evidence describes the world and goes to `improve_evidence_index`; an
    #: artefact is what the team designed and belongs to the gate document as
    #: captured content. One bucket would let a proposed future be retrieved
    #: later as a fact about the present.
    kind: str = "evidence"

    #: The `improve_evidence_index` document id, when this upload was indexed.
    #: **`None` for every artefact, and for evidence whose indexing failed** —
    #: which is why it is Optional rather than defaulted to "". §6 names it as
    #: what makes the evidence trail traversable.
    evidence_index_id: Optional[str] = None

    #: The interpretation's summary, lifted to the top level because §6's entry
    #: shape names `summary` and a gate document reads that shape.
    summary: str = ""

    interpretation: Optional[UploadInterpretation] = None

    #: Set when the deterministic parse could not read the file. **An upload
    #: that reaches the case record with this set was reported, not silently
    #: accepted** (ruling 5) — the route refuses before persisting, so this is
    #: the belt-and-braces record for any path that later chooses to keep one.
    refusal_reason: Optional[str] = None

    #: Set when a `load_evidence_series` call or a citation references this
    #: document. **`None` at a gate on an upload bound to an open ask means
    #: the Belt supplied evidence and the coaching proceeded without it** —
    #: a condition undetectable without the field (S-C02, S-C09).
    consumed_at: Optional[str] = None

    # Filled at 6.12 by the ask-binding; declared at 6.11. See the docstring.
    ask_id: Optional[str] = None
    version: Optional[int] = None

    def to_phase_state_entry(self, phase: str) -> dict[str, Any]:
        """This record in §6's `PhaseState.uploads` entry shape (S-C02).

        **The single reconciliation point between the two shapes.** Gate
        assembly reads `PhaseState.uploads`; the case blob holds
        `UploadRecord`; before 6.11 nothing connected them and
        `PhaseState.uploads` had no writer at all, so every gate document
        asserted §6's "this phase reached its conclusions from typed
        statements alone" — including for phases where the Belt uploaded.
        """
        return {
            "evidence_index_id": self.evidence_index_id,
            "filename": self.filename,
            "phase": phase,
            "uploaded_at": self.uploaded_at,
            "summary": self.summary,
            "kind": self.kind,
            "role": self.role,
            "shape_match": self.shape_match,
            "content_digest": self.content_digest,
            "blob_path": self.blob_path,
            "consumed_at": self.consumed_at,
            # Reserved for 6.12 — carried so the shape is stable across the
            # two steps rather than growing under the gate document.
            "ask_id": self.ask_id,
            "version": self.version,
        }


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
