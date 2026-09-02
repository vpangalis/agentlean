from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from langchain_core.messages import AIMessage

from backend.core import conversation
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
from backend.gateway.schemas import SummariseRequest, SummariseResponse
from backend.gateway.schemas import ContextRequest, ContextResponse
from backend.phases.mappers_common import PHASE_ORDER
from backend.storage import blob
from backend.storage.models import CaseDocument, UploadRecord
from backend.upload.agent import process_upload

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.post("/summarise", response_model=SummariseResponse)
async def summarise_session(request: SummariseRequest) -> SummariseResponse:
    """Generate a 2-3 sentence AI summary of a session's conversation turns."""
    from backend.core.llm import get_llm, block_text
    from langchain_core.messages import HumanMessage, SystemMessage

    dialogue = "\n\n".join(
        f"{'AI Guide' if t.role == 'ai' else (t.user or 'Team member')}: {t.text}"
        for t in request.turns
    )

    system = (
        "You are summarising a working session from a Lean Six Sigma improvement project. "
        "Write clear, factual summaries that capture what was discussed and decided."
    )

    prompt = (
        f"Summarise the following session from the {request.phase.upper()} phase "
        f"of project: \"{request.case_title}\".\n\n"
        f"SESSION DIALOGUE:\n{dialogue}\n\n"
        "Write exactly 2-3 sentences. Cover: what topics were discussed, what information "
        "the team provided, and what fields or decisions were captured. "
        "Be specific — mention actual numbers, names, or facts from the conversation. "
        "Do not use bullet points. Do not start with 'In this session'."
    )

    try:
        llm = get_llm(role="summarizer", temperature=0.3)
        response = await llm.ainvoke(
            [SystemMessage(content=system), HumanMessage(content=prompt)]
        )
        summary = block_text(response)
    except Exception as e:
        logger.error("summarise_session() error: %s", e)
        summary = "Summary could not be generated."

    return SummariseResponse(summary=summary)


@router.post("/context", response_model=ContextResponse)
async def get_session_context(request: ContextRequest) -> ContextResponse:
    """Generate a re-entry greeting based on current gate status.
    Called when user opens the AI guide tab after a break."""
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")
    case = await blob.load_case(request.case_id)
    if case is None:
        raise HTTPException(404, f"Case {request.case_id} not found")

    # Get structured inputs for the phase.
    # case.phases is dict[str, PhaseRecord]; structured lives on the record.
    phase_data = {}
    try:
        phases = getattr(case, 'phases', {}) or {}
        phase_record = (
            phases.get(request.phase) if isinstance(phases, dict)
            else getattr(phases, request.phase, None)
        )
        if phase_record is not None:
            structured = getattr(phase_record, 'structured', None)
            if structured is None and isinstance(phase_record, dict):
                structured = phase_record.get('structured')
            phase_data = structured or {}
    except Exception:
        phase_data = {}

    # Determine missing sections for define phase
    SECTION_FIELDS = {
        'Problem Statement':   ['what','where','when','who_affected',
                                'why_it_matters','how_much_baseline','how_goal'],
        'Goal & Scope':        ['goal_statement','scope_in','scope_out'],
        'SIPOC Diagram':       ['sipoc'],
        'Business Case':       ['business_case_rationale','current_cost',
                                'expected_saving','hard_benefits','soft_benefits'],
        'Project Charter':     ['process_owner','sponsor','team_members',
                                'belt_level','target_date','primary_metric',
                                'estimated_completion_date','project_milestones'],
        'Baseline & Metrics':  ['how_much_baseline','primary_metric',
                                'secondary_metric'],
    }

    def field_has_value(v):
        if v is None: return False
        if isinstance(v, (list, dict)): return bool(v)
        return bool(str(v).strip())

    missing_sections = [
        section for section, fields in SECTION_FIELDS.items()
        if not all(field_has_value(phase_data.get(f)) for f in fields)
    ]

    completed_count = len(SECTION_FIELDS) - len(missing_sections)
    total_count = len(SECTION_FIELDS)

    # Build greeting
    case_title = getattr(case, 'title', '') or ''
    user_name = request.user or 'team'

    if not missing_sections:
        greeting = (
            f"Welcome back{', '+user_name if user_name else ''}! "
            f"All sections of your Define gate are complete. "
            f"When your team is ready, you can submit for gate review."
        )
        next_action = "Submit the Define gate for review."
    else:
        missing_str = ', '.join(missing_sections[:2])
        if len(missing_sections) > 2:
            missing_str += f" and {len(missing_sections)-2} more"
        greeting = (
            f"Welcome back{', '+user_name if user_name else ''}! "
            f"You've completed {completed_count} of {total_count} sections "
            f"for the Define gate. "
            f"Still needed: {missing_str}. "
            f"Shall we continue?"
        )
        next_action = (
            f"Let's work on: {missing_sections[0]}."
        )

    return ContextResponse(
        greeting=greeting,
        missing_sections=missing_sections,
        next_action=next_action,
    )


@router.post("/cases", response_model=CaseCreateResponse)
async def create_case(request: CaseCreateRequest) -> CaseCreateResponse:
    """Create a new improvement case and register it."""
    import uuid
    from datetime import datetime, timezone

    # Generate case ID: IMPR-YYYY-NNN
    year = datetime.now(timezone.utc).year
    short = str(uuid.uuid4())[:3].upper()
    case_id = f"IMPR-{year}-{short}"
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")
    case = CaseDocument.new(
        case_id=case_id,
        title=request.title,
        belt_level=request.belt_level,
        leader=request.leader,
        department=request.department,
        target_date=request.target_date,
        team=request.team,
    )
    await blob.create_case(case)
    await blob.register_case(case)
    return CaseCreateResponse(case_id=case_id, title=request.title)


# ── the graph boundary ────────────────────────────────────────────────────
#
# §1.1 and §49: the compiled graph is the ONLY runtime path, and a route that
# does anything beyond `await graph.ainvoke(...)` plus envelope marshalling is
# a violation. Everything between here and `/gate` is that marshalling.


def _graph_config(case: CaseDocument, phase: str, user: str, entry: str) -> dict:
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

    The three seam keys — `current_user`, `case_metadata`, `v1_artifacts` —
    carry what `orchestrate_define` needs and `PhaseState` may not declare
    (§56). They are deleted with the seam at 6.2; see `phases/define/nodes.py`.
    """
    record = case.phases.get(phase)
    return {
        "configurable": {
            "thread_id": case.case_id,
            "entry": entry,
            "current_user": user,
            "case_metadata": {
                "title": case.title,
                "belt_level": case.belt_level,
                "leader": case.leader,
                "department": case.department,
            },
            "v1_artifacts": dict((record.structured or {}) if record else {}),
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
    """
    snapshot = await graph.aget_state(config)
    if snapshot.values:
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
async def ask(request: AskRequest) -> AskResponse:
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

    Inline `await` is chosen here because for a non-streaming handler it *is*
    the ABANDON policy: the graph run is the handler's own task, so when the
    client goes the task is cancelled with it and nothing keeps running to
    checkpoint behind the Belt's back. **The `t.cancel()`-in-`finally` variant
    belongs to `/ask/stream`** (§49), which does not exist yet — building the
    streaming half here would be building step 10.1's scope inside 4.2, and a
    cancellation handler with no generator to hang it on is a comment, not a
    policy. **When streaming lands, that handler must make this same choice
    explicitly**; inheriting this one silently is the accident §47 names.

    Ratified policy is ABANDON, not COMPLETE: a silently-completed gate approval
    the Belt never saw is unacceptable in a system whose premise is that the
    Belt approves what gets committed.
    """
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")

    case = await blob.load_case(request.case_id)
    if case is None:
        raise HTTPException(404, f"Case {request.case_id} not found")

    from datetime import datetime, timezone
    from backend.core.graph import PhaseNotWired, get_graph

    now = datetime.now(timezone.utc).isoformat()
    user_turn = {
        "turn": len(case.conversation_history) + 1,
        "role": "user",
        "user": request.user,
        "text": request.message,
        "timestamp": now,
        "citations": [],
    }

    graph = get_graph()
    config = _graph_config(case, request.phase, request.user, entry="ask")

    try:
        state = await _graph_input(
            graph, config, case, [conversation.turn_to_message(user_turn)]
        )
        # §47 requirement 1 — inline await. See the docstring above.
        result = await graph.ainvoke(state, config=config)
    except PhaseNotWired as e:
        raise HTTPException(501, str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("ask() error: %s", e)
        raise HTTPException(500, f"Graph error: {str(e)}")

    reply = _last_ai(result)
    payload = conversation.transport(reply) if reply is not None else {}
    phase_data = dict(payload.get("v1_artifacts") or {})
    verdict = dict(payload.get("gate_verdict") or {})
    extra = dict(getattr(reply, "additional_kwargs", None) or {}) if reply else {}

    # ── envelope marshalling from here down ───────────────────────────
    #
    # The case blob is still written per turn, which §10 says it should not be.
    # That is unchanged v1 behaviour and is NOT this step's to fix: the
    # conversation moves into the checkpoint only once the checkpoint is where
    # the UI reads it from, which is the UI rebuild (step 10.2). What 4.2
    # changes is that the checkpoint now exists alongside it.
    case.conversation_history.append(user_turn)
    if reply is not None:
        case.conversation_history.append(
            conversation.strip_transport(
                conversation.message_to_turn(reply, len(case.conversation_history))
            )
        )
    clean = {
        k: v for k, v in phase_data.items()
        if not k.startswith("_") and v is not None and v != [] and v != {}
    }
    if clean and request.phase in case.phases:
        case.phases[request.phase].structured = clean
    await blob.save_case(case)

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
            )
            for c in (extra.get("citations") or [])
        ],
        suggestion_chips=_build_chips(request.phase, phase_data),
        sipoc_diagram=extra.get("sipoc_diagram"),
        visualisation=extra.get("visualisation"),
        section_completed=extra.get("section_completed"),
        escalated=bool(verdict.get("escalated", False)),
    )


@router.get("/gate/review/{case_id}/{phase}", response_model=GateReviewResponse)
async def gate_review(case_id: str, phase: str) -> GateReviewResponse:
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
    from backend.phases.gate_registry import GATE_SPECS, review_rows

    if phase not in GATE_SPECS:
        raise HTTPException(400, f"Unknown phase: {phase}")
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")

    case = await blob.load_case(case_id)
    if case is None:
        raise HTTPException(404, f"Case {case_id} not found")

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
            logger.error("gate assembly failed for %s/%s: %s", case_id, phase, e)
            raise HTTPException(500, f"Gate assembly failed: {e}")

    return GateReviewResponse(
        phase=phase,
        passed=not missing,
        missing_fields=missing,
        fields=[GateReviewField(**r) for r in rows],
        acknowledged_gaps=gaps,
        document=document,
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
    case_id: str = Form(...),
    uploaded_by: str = Form(...),
    phase: str = Form(...),
    file: UploadFile = File(...),
    purpose: str = Form(""),
):
    """Upload a file, extract content via Vision LLM if image,
    store in blob, index into improve_evidence_index.

    Returns a flat ``file`` dict in the new CaseFile shape alongside
    the legacy response fields for backward compatibility."""
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")

    file_bytes = await file.read()
    mime_type = file.content_type or "application/octet-stream"

    case = await blob.load_case(case_id)
    if case is None:
        raise HTTPException(404, f"Case {case_id} not found")

    define_phase = case.phases.get("define")
    define_structured = (define_phase.structured or {}) if define_phase else {}
    case_meta = {
        "title": case.title,
        "department": case.department,
        "belt_level": case.belt_level,
        "what": define_structured.get("what", ""),
    }

    # Save raw file to blob
    blob_path = await blob.upload_file(
        case_id, file.filename, file_bytes, mime_type,
    )

    # Process: classify + extract via Upload Intelligence agent
    upload_record = await process_upload(
        case_id=case_id,
        filename=file.filename,
        file_bytes=file_bytes,
        mime_type=mime_type,
        uploaded_by=uploaded_by,
        phase=phase,
        case_meta=case_meta,
    )
    upload_record["blob_path"] = blob_path

    # Index into improve_evidence_index (best-effort)
    indexed = False
    try:
        await _index_upload(case_id, upload_record)
        indexed = True
        upload_record["indexed"] = True
    except Exception as e:
        logger.warning(
            "Evidence indexing failed for %s: %s", file.filename, e,
        )

    # Resolve purpose (form value wins; otherwise auto-detect)
    resolved_purpose = (purpose or "").strip() or auto_detect_purpose(
        file.filename
    )

    # Persist upload record into case blob (canonical phases[phase].uploads)
    phase_record = case.phases.get(phase)
    if phase_record is not None:
        phase_record.uploads.append(UploadRecord(
            filename=file.filename,
            blob_path=blob_path,
            uploaded_by=uploaded_by,
            uploaded_at=upload_record["timestamp"],
            classification=_classification_for(
                resolved_purpose, upload_record["content_type"], indexed
            ),
        ))
        await blob.save_case(case)

    # CaseFile-shaped dict for the UI (matches gateway.schemas.CaseFile)
    case_file = {
        "file_id": _case_file_id(case_id, file.filename, upload_record["timestamp"]),
        "filename": file.filename,
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
        "filename": file.filename,
        "content_type": upload_record["content_type"],
        "summary": upload_record["summary"],
        "sipoc_columns": upload_record.get("sipoc_columns"),
        "indexed": indexed,
    }


@router.delete("/files/{case_id}/{file_id}")
async def delete_case_file(case_id: str, file_id: str):
    """Remove a file record from the case.

    The upload record is removed from the case; **the blob itself is left
    orphaned.** `storage/blob.py` owns `uploads/{case_id}/{file}` and exposes
    no delete, so nothing here can remove it. This was already the behaviour:
    the previous code probed `getattr(blob_client, "delete_blob", None)` on a
    class that never defined one, so the branch never ran. Step 3.5 preserved
    the behaviour and dropped the probe rather than adding a deleter, which
    would be a new capability and not a structural refactor."""
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")

    case = await blob.load_case(case_id)
    if case is None:
        raise HTTPException(404, "Case not found")

    # Find and remove the upload from whichever phase contains it
    removed_blob_path = None
    for phase_data in case.phases.values():
        uploads = getattr(phase_data, "uploads", []) or []
        for i, u in enumerate(uploads):
            fid = _case_file_id(case_id, u.filename, u.uploaded_at)
            if fid == file_id:
                removed_blob_path = u.blob_path
                uploads.pop(i)
                break
        if removed_blob_path is not None:
            break

    if removed_blob_path is None:
        raise HTTPException(404, "File not found")

    # The blob at `removed_blob_path` is intentionally left in place — see
    # the docstring. Only the case record is updated.
    await blob.save_case(case)
    return {"deleted": True, "file_id": file_id}


async def _index_upload(case_id: str, upload_record: dict) -> None:
    """Index extracted text into improve_evidence_index."""
    import hashlib
    from azure.search.documents.aio import SearchClient
    from azure.core.credentials import AzureKeyCredential
    from backend.core.config import settings
    from backend.knowledge.retriever import get_embeddings

    extracted_text = (upload_record.get("extracted_text") or "").strip()
    if not extracted_text:
        logger.info(
            "Skipping evidence indexing - no extracted text for %s",
            upload_record.get("filename"),
        )
        return

    embeddings = get_embeddings()
    embedding = await embeddings.aembed_query(extracted_text)

    doc_id = hashlib.sha256(
        f"{case_id}_{upload_record['filename']}_{upload_record['timestamp']}"
        .encode()
    ).hexdigest()[:32]

    metadata = json.dumps({
        "case_id": case_id,
        "upload_phase": upload_record.get("phase"),
        "content_type": upload_record.get("content_type"),
        "filename": upload_record.get("filename"),
        "blob_path": upload_record.get("blob_path"),
        "uploaded_by": upload_record.get("uploaded_by"),
        "timestamp": upload_record.get("timestamp"),
    })

    document = {
        "id": doc_id,
        "content": extracted_text,
        "content_vector": embedding,
        "metadata": metadata,
        "case_id": case_id,
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


@router.post("/gate", response_model=GateSubmitResponse)
async def submit_gate(request: GateSubmitRequest) -> GateSubmitResponse:
    """Submit the phase for gate review — through the same compiled graph.

    **The same graph object as `/ask`** (§12, §49). The two differ only in the
    per-run `entry` on `config["configurable"]`, which the planner reads to
    decide whether this turn coaches or validates. There is no second dispatch
    table and no second runtime: `validate_map` and the five `validate_*`
    imports are gone, and the validator now runs where §34 puts it — inside
    `validation_stack`, in the subgraph.

    ═══════════════════════════════════════════════════════════════════════
    WHAT THIS ROUTE IS NOT, AT 4.2
    ═══════════════════════════════════════════════════════════════════════
    §49 splits this endpoint three ways — `/gate/submit` triggers the stack and
    the interrupt, `/gate/approve` and `/gate/reject` resume from it. **All
    three are stage 7**, because all three are the `interrupt()` this step
    deliberately does not build (§47 requirement 4, ruled OUT). So the gate
    still *applies* here rather than inside `gate_apply`: the graph returns the
    verdict, and this route writes the gate document and the registry entry as
    it did before.

    That is the honest shape and the safe one. Moving the write into
    `gate_apply` without the interrupt in front of it would commit a gate the
    Belt never approved on every coaching turn — the failure §47's ABANDON
    policy exists to prevent. **The write moves at stage 7, with the interrupt,
    in one change.**

    **The Define gate remains inert** (WATCH 7): `validate_define` requires the
    §39.1.2 v2 names and the v1 writer emits the v1 ones, so every required
    field reads as missing. The verdict below is the one this endpoint returned
    before, on the same inputs, computed in a different place.
    """
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")
    case = await blob.load_case(request.case_id)
    if case is None:
        raise HTTPException(404, f"Case {request.case_id} not found")

    from backend.core.graph import PhaseNotWired, get_graph

    graph = get_graph()
    config = _graph_config(
        case, request.phase, request.submitted_by, entry="gate"
    )

    try:
        state = await _graph_input(graph, config, case, [])
        # §47 requirement 1 — inline await, the same deliberate choice `/ask`
        # documents. A gate submission is the LAST turn that may complete
        # behind a departed Belt.
        result = await graph.ainvoke(state, config=config)
    except PhaseNotWired as e:
        raise HTTPException(501, str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("submit_gate() error: %s", e)
        raise HTTPException(500, f"Graph error: {str(e)}")

    reply = _last_ai(result)
    payload = conversation.transport(reply) if reply is not None else {}
    verdict = dict(payload.get("gate_verdict") or {})
    phase_data = dict(payload.get("v1_artifacts") or {})
    passed = bool(verdict.get("passed", False))
    missing = list(verdict.get("missing") or [])

    if passed:
        # `_validated` is unchanged v1 behaviour and unchanged v1 defect:
        # `validate_define` never writes that key, so this resolves to `{}` and
        # the gate document is written empty. It is unreachable today (the gate
        # cannot pass — WATCH 7) and fixing it here would be repairing v1 code
        # that step 11.1 deletes, so it is recorded as a WATCH rather than
        # patched inside a structural step.
        validated = phase_data.get("_validated", {})
        await blob.write_phase_gate(
            case_id=request.case_id,
            phase=request.phase,
            structured=validated,
            submitted_by=request.submitted_by,
            summary=f"Gate passed by {request.submitted_by}",
        )
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

    return GateSubmitResponse(
        passed=False,
        phase=request.phase,
        missing_fields=[f.replace("_", " ") for f in missing],
        message=f"Not quite ready yet. {len(missing)} item(s) still needed.",
    )


@router.get("/registry", response_model=list[RegistryEntryOut])
async def get_registry() -> list[RegistryEntryOut]:
    """Management dashboard â returns all cases from registry."""
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
            days_in_phase=e.days_in_phase,
            rag_status=e.rag_status,
            status=e.status,
            phase_summary=e.phase_summary.model_dump(),
        )
        for e in registry.cases
    ]


@router.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Load full case document. Also projects every per-phase upload
    into a flat ``files`` array in CaseFile shape so the UI can render
    a single grouped files panel without walking each phase record."""
    if not blob.storage_configured():
        raise HTTPException(503, "Storage not configured")
    case = await blob.load_case(case_id)
    if case is None:
        raise HTTPException(404, f"Case {case_id} not found")

    payload = case.model_dump()
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
