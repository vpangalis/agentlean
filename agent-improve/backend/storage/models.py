from __future__ import annotations

from typing import Literal, Optional, Any

from pydantic import BaseModel, Field, PrivateAttr

from backend.core.citations import CitationRecord
from backend.core.clock import utc_now


class TeamMemberRecord(BaseModel):
    """Version 11 and before: a create-form team entry. Read by the schema-12 migration only (ADR-0090)."""
    name: str
    role: str


#: ADR-0090 "The people on a case": the role the case's creator holds.
PROJECT_LEAD = "project lead"


class PersonLocation(BaseModel):
    """ADR-0090 decision 1 and ADR-0089 decision 1: country (an ISO 3166 code) and site, from the configured lists
    (`storage/sites.py`) — a person's and a case's; empty is "not set" (W20)."""
    country: str = ""
    site: str = ""


class PersonRecord(BaseModel):
    """ADR-0090 "The people on a case": one record per person, kept on the case and written on every team
    change. The e-mail is required only before the person signs in (ruling a). A person named in Define's
    element 2 who was not on the case is `proposed` until the lead confirms them with an e-mail (ruling b)."""
    full_name: str
    email: str = ""
    role: str = ""
    function: str = ""
    department: str = ""
    location: PersonLocation = Field(default_factory=PersonLocation)
    status: Literal["member", "proposed"] = "member"
    added_by: str = ""
    added_at: str = ""
    # ADR-0105 (DEF-103): the one-time code — only its HMAC-SHA256 under SESSION_SECRET, never the code; empty when
    # none is open (never issued, spent, voided).
    code_hash: str = ""
    code_issued_at: str = ""
    code_attempts: int = 0


class CriterionCheck(BaseModel):
    """ADR-0074: what an uploaded file shows for ONE acceptance criterion of the element."""

    criterion: str = Field(description="The criterion's id, as the phase script names it.")
    result: Literal["supported", "contradicted", "not_covered"]
    where: str = Field(default="", description="The page or section of the file, where it has one.")


class ElementCheck(BaseModel):
    """ADR-0074 (DEF-108, W5): the file judged against the current element's acceptance criteria
    at interpretation — the element the planner was working on when the file arrived."""

    element: str
    criteria: list[CriterionCheck] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list,
                               description="What the element still needs that the file does not give.")
    #: ADR-0085 (G-169) — what a read-back of the file shows: the element's answer as the file gives it.
    value: str = Field(default="", description="The element's answer as the file gives it, in the file's own "
                                               "words; empty when the file does not answer it.")


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
    #: ADR-0074 — None on the fallback, on a phase without acceptance criteria, and on every
    #: record written before schema version 4.
    element_check: Optional[ElementCheck] = None
    #: R10 (ADR-0095, DEF-295): a file at Define's element 12 is read by the SIPOC tool as its one reading —
    #: {read, is_process, draft, gaps, checks, reply} (`knowledge/sipoc.read_sipoc`). The draft is what the upload
    #: turn reads back and a Confirm stores. None on every other upload and on every record before schema 17.
    sipoc: Optional[dict[str, Any]] = None


class ImageSipoc(BaseModel):
    """The five SIPOC columns an image shows, each as a list."""

    suppliers: list[str] = Field(default_factory=list)
    inputs: list[str] = Field(default_factory=list)
    process_steps: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    customers: list[str] = Field(default_factory=list)


class ImageRead(BaseModel):
    """What the vision call reads off an image — ADR-0104 with its note: five typed fields, the
    image's only parse (no deterministic structure exists to read)."""

    extracted_text: str = Field(description="All visible text as a single string.")
    document_type: str = Field(default="other",
                               description="process_map | sipoc | fishbone | vsm | notes | other")
    process_steps: list[str] = Field(default_factory=list,
                                     description="A process map's or flow diagram's steps, in order.")
    sipoc_columns: Optional[ImageSipoc] = Field(default=None, description="A SIPOC's columns, if it is one.")
    metrics_found: list[str] = Field(default_factory=list,
                                     description="Numbers, metrics or KPIs visible in the image.")


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

    #: Row count from the deterministic parse.
    rows: Optional[int] = None

    #: The document's function in the project, from the ratified role
    #: vocabulary. **With `case_id` this is the LOGICAL IDENTITY**:
    #: supersession resolves on `(case_id, role)`, and files are versions of
    #: the ask, never identified by filename.
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

    #: evidence | artefact. **The destination, not the format.**
    #: Evidence describes the world and goes to `improve_evidence_index`; an
    #: artefact is what the team designed and belongs to the gate document as
    #: captured content. One bucket would let a proposed future be retrieved
    #: later as a fact about the present.
    kind: str = "evidence"

    #: The `improve_evidence_index` document id, when this upload was indexed.
    #: **`None` for every artefact, and for evidence whose indexing failed** —
    #: which is why it is Optional rather than defaulted to "". It is what
    #: makes the evidence trail traversable.
    evidence_index_id: Optional[str] = None

    #: The interpretation's summary, lifted to the top level because the
    #: uploads entry shape names `summary` and a gate document reads that shape.
    summary: str = ""

    interpretation: Optional[UploadInterpretation] = None
    #: T72 (ADR-0067): False when the document check flagged the file — it stays in the case,
    #: is never interpreted or indexed, and never reaches the coach. The reason says which and why.
    used_by_coach: bool = True
    not_used_reason: Optional[str] = None

    #: Set when the deterministic parse could not read the file. **An upload
    #: that reaches the case record with this set was reported, not silently
    #: accepted** — the route refuses before persisting, so this is
    #: the belt-and-braces record for any path that later chooses to keep one.
    refusal_reason: Optional[str] = None

    #: Set when a `load_evidence_series` call or a citation references this
    #: document. **`None` at a gate on an upload bound to an open ask means
    #: the Belt supplied evidence and the coaching proceeded without it** —
    #: a condition undetectable without the field.
    consumed_at: Optional[str] = None

    # The ask this upload answered, and its version under that ask. See the class docstring.
    ask_id: Optional[str] = None
    version: Optional[int] = None

    def to_phase_state_entry(self, phase: str) -> dict[str, Any]:
        """This record in the `PhaseState.uploads` entry shape.

        **The single reconciliation point between the two shapes.** Gate
        assembly reads `PhaseState.uploads`; the case blob holds
        `UploadRecord`. Without this, a gate document would assert "this
        phase reached its conclusions from typed statements alone" — even
        for phases where the Belt uploaded.
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
            # ADR-0074 — the upload turn writes the file part of its reply from this.
            "element_check": (self.interpretation.element_check.model_dump()
                              if self.interpretation and self.interpretation.element_check else None),
            # R10 (ADR-0095): the SIPOC tool's reading of a file at element 12, read back by the upload turn.
            "sipoc": self.interpretation.sipoc if self.interpretation else None,
            # Carried so the shape is stable rather than growing under the
            # gate document.
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
    #: Where each coached field stands — R5: `status` (not taught
    #: / asked / answered / confirmed), the Belt's words so far, and the
    #: read-back awaiting a yes. Written by the same statement as `structured`
    #: (`routes.apply_capture`), from the same turn's product.
    field_status: dict[str, dict[str, Any]] = {}

    #: The field change log — one entry per change to `structured`, keyed
    #: `{phase}:{turn}:{field}`. The entry shape and the merge rule are
    #: `core/substate.FIELD_LOG_ENTRY_KEYS` / `merge_field_log`.
    #:
    #: **HERE, and not in the Store's `case` record, which is where `asks`
    #: live.** The difference is WHO must read the thing BETWEEN turns: an ask
    #: is answered by an upload arriving moments later on a route that cannot
    #: see the checkpoint, and there is no sanctioned case-blob write between
    #: those two moments. A field change has no such reader. It is written
    #: with `structured`, on the same schedule — a history persisted on a
    #: different schedule from the value it is a history OF can disagree with
    #: it, which would read exactly like a change that never happened.
    field_log: list[dict[str, Any]] = []


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
    #: The project lead's display name — always the lead's `PersonRecord.full_name` (ADR-0090 decision 4).
    leader: str
    department: str
    #: ADR-0089 (W20, DEF-288): where the case is — country and site; empty on a case created before it ("not set",
    #: the lead is asked on the next open).
    location: PersonLocation = Field(default_factory=PersonLocation)
    #: ADR-0090: everyone on the case; the lead is the one whose role is PROJECT_LEAD.
    people: list[PersonRecord] = []
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

    #: ADR-0065 (T88): the state schema version this case blob was written in. Absent from a
    #: blob written before versioning, which is version 1; `storage/blob.py` stamps and migrates.
    state_schema_version: int = 1

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
        people: Optional[list["PersonRecord"]] = None,
        location: Optional[PersonLocation] = None,
    ) -> "CaseDocument":
        """Factory for creating a new case. ADR-0090: `people` (the lead first) when the form gives them;
        else the lead from `leader` and the members from `team` ({name, role})."""

        from backend.core.state import STATE_SCHEMA_VERSION
        return cls(
            state_schema_version=STATE_SCHEMA_VERSION,
            case_id=case_id,
            title=title,
            belt_level=belt_level,
            leader=leader,
            department=department,
            location=location or PersonLocation(),
            target_date=target_date,
            created_at=utc_now().isoformat(),
            people=list(people) if people is not None else [
                PersonRecord(full_name=leader, role=PROJECT_LEAD),
                *(PersonRecord(full_name=str(m.get("name") or ""), role=str(m.get("role") or ""))
                  for m in team if str(m.get("name") or "").strip())],
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
    #: ADR-0089 (DEF-288): the case's location, for the case list's filter.
    location: PersonLocation = Field(default_factory=PersonLocation)
    status: str = "active"
    #: ADR-0076 (T65): {at, criteria} while the report is held for the project lead; None otherwise.
    escalation: Optional[dict[str, Any]] = None
    phase_summary: PhaseSummaryRecord = Field(
        default_factory=PhaseSummaryRecord
    )


class CaseRegistry(BaseModel):
    """Full registry.json contents."""

    cases: list[RegistryEntry] = []
    last_updated: str = ""
    #: ADR-0092 decision 3: the ETag the registry was read at ("" when there was none yet), so the save is
    #: conditional — never serialised. None for a registry not read from storage.
    _etag: Optional[str] = PrivateAttr(default=None)
