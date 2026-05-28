from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

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
from backend.gateway.schemas import SummariseRequest, SummariseResponse
from backend.storage.blob import blob_client
from backend.storage.models import CaseDocument, UploadRecord
from backend.upload.agent import process_upload

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@router.post("/summarise", response_model=SummariseResponse)
def summarise_session(request: SummariseRequest) -> SummariseResponse:
    """Generate a 2-3 sentence AI summary of a session's conversation turns."""
    from backend.core.llm import get_llm
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
        llm = get_llm(role="reasoning", temperature=0.3)
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=prompt)])
        summary = response.content.strip()
    except Exception as e:
        logger.error("summarise_session() error: %s", e)
        summary = "Summary could not be generated."

    return SummariseResponse(summary=summary)


@router.post("/cases", response_model=CaseCreateResponse)
def create_case(request: CaseCreateRequest) -> CaseCreateResponse:
    """Create a new improvement case and register it."""
    import uuid
    from datetime import datetime, timezone

    # Generate case ID: IMPR-YYYY-NNN
    year = datetime.now(timezone.utc).year
    short = str(uuid.uuid4())[:3].upper()
    case_id = f"IMPR-{year}-{short}"
    if blob_client is None:
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
    blob_client.create_case(case)
    blob_client.register_case(case)
    return CaseCreateResponse(case_id=case_id, title=request.title)


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    if blob_client is None:
        raise HTTPException(503, "Storage not configured")

    case = blob_client.load_case(request.case_id)
    if case is None:
        raise HTTPException(404, f"Case {request.case_id} not found")

    # Append user turn to history first
    from datetime import datetime, timezone
    from backend.core.state import ImproveGraphState
    from backend.core.graph import get_graph

    now = datetime.now(timezone.utc).isoformat()
    user_turn = {
        "turn": len(case.conversation_history) + 1,
        "role": "user",
        "user": request.user,
        "text": request.message,
        "timestamp": now,
        "citations": [],
    }
    case.conversation_history.append(user_turn)

    # Build state
    state: ImproveGraphState = {
        "case_id": request.case_id,
        "current_phase": request.phase,
        "current_user": request.user,
        "phase_inputs": {
            phase: (case.phases[phase].structured or {})
            for phase in case.phases
        },
        "chat_history": case.conversation_history,
        "gate_attempts": 0,
        "escalated": False,
        "citations": [],
        "analyst_output": None,
        "uploaded_files": [],
        "case_metadata": {
            "title": case.title,
            "belt_level": case.belt_level,
            "leader": case.leader,
            "department": case.department,
        },
    }

    # Run ONE orchestrate step (not full graph â conversational turn)
    graph = get_graph()
    orchestrate_node = f"orchestrate_{request.phase}"
    try:
        # Invoke just the orchestrate node for this turn
        from backend.phases.define.orchestrate import orchestrate_define
        from backend.phases.measure.orchestrate import orchestrate_measure
        from backend.phases.analyse_phase.orchestrate import orchestrate_analyse_phase
        from backend.phases.improve.orchestrate import orchestrate_improve
        from backend.phases.control.orchestrate import orchestrate_control

        node_map = {
            "define":        orchestrate_define,
            "measure":       orchestrate_measure,
            "analyse_phase": orchestrate_analyse_phase,
            "improve":       orchestrate_improve,
            "control":       orchestrate_control,
        }
        node_fn = node_map.get(request.phase)
        if node_fn is None:
            raise HTTPException(400, f"Unknown phase: {request.phase}")

        result = node_fn(state)

        # Update state with result
        state.update(result)

        # Sync updated chat history and phase_inputs back to case before saving
        updated_history = state.get("chat_history") or []
        case.conversation_history = updated_history
        updated_phase_inputs = state.get("phase_inputs") or {}
        for phase_key, phase_data in updated_phase_inputs.items():
            if phase_key in case.phases and phase_data:
                # Store extracted (non-internal) fields in structured
                clean = {k: v for k, v in phase_data.items() if not k.startswith("_") and v is not None and v != [] and v != {}}
                if clean:
                    case.phases[phase_key].structured = clean

        # Persist conversation to blob
        blob_client.save_case(case)

        # Build captured fields from phase_inputs
        phase_data = (state.get("phase_inputs") or {}).get(request.phase, {})
        captured = _build_captured_fields(phase_data, request.phase)

        # Get last AI turn
        history = state.get("chat_history") or []
        last_ai = next(
            (t["text"] for t in reversed(history) if t.get("role") == "ai"),
            "Processing...",
        )

        sipoc_diagram = result.get("sipoc_diagram")
        visualisation = result.get("visualisation")
        section_completed = result.get("section_completed")

        return AskResponse(
            answer=last_ai,
            phase=request.phase,
            captured_fields=captured,
            gate_status=GateStatus(
                phase=request.phase,
                passed=phase_data.get("_gate_passed", False),
                attempts=state.get("gate_attempts", 0),
                missing_fields=phase_data.get("_missing_fields", []),
            ),
            citations=[
                CitationOut(
                    agent_origin=c.get("agent_origin", ""),
                    index_name=c.get("index_name", ""),
                    document_id=c.get("document_id", ""),
                    relevance_summary=c.get("relevance_summary", ""),
                )
                for c in (state.get("citations") or [])
            ],
            suggestion_chips=_build_chips(request.phase, phase_data),
            sipoc_diagram=sipoc_diagram,
            visualisation=visualisation,
            section_completed=section_completed,
            escalated=state.get("escalated", False),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("ask() error: %s", e)
        raise HTTPException(500, f"Graph error: {str(e)}")


@router.post("/upload")
def upload_file(
    case_id: str = Form(...),
    uploaded_by: str = Form(...),
    phase: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload a file, extract content via Vision LLM if image,
    store in blob, index into improve_evidence_index."""
    if blob_client is None:
        raise HTTPException(503, "Storage not configured")

    file_bytes = file.file.read()
    mime_type = file.content_type or "application/octet-stream"

    case = blob_client.load_case(case_id)
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
    blob_path = blob_client.upload_file(
        case_id, file.filename, file_bytes, mime_type,
    )

    # Process: classify + extract via Upload Intelligence agent
    upload_record = process_upload(
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
        _index_upload(case_id, upload_record)
        indexed = True
        upload_record["indexed"] = True
    except Exception as e:
        logger.warning(
            "Evidence indexing failed for %s: %s", file.filename, e,
        )

    # Persist upload record into case blob (canonical phases[phase].uploads)
    phase_record = case.phases.get(phase)
    if phase_record is not None:
        classification = (
            f"{upload_record['content_type']}"
            f"{' · indexed' if indexed else ' · pending'}"
        )
        phase_record.uploads.append(UploadRecord(
            filename=file.filename,
            blob_path=blob_path,
            uploaded_by=uploaded_by,
            uploaded_at=upload_record["timestamp"],
            classification=classification,
        ))
        blob_client.save_case(case)

    return {
        "blob_path": blob_path,
        "filename": file.filename,
        "content_type": upload_record["content_type"],
        "summary": upload_record["summary"],
        "sipoc_columns": upload_record.get("sipoc_columns"),
        "indexed": indexed,
    }


def _index_upload(case_id: str, upload_record: dict) -> None:
    """Index extracted text into improve_evidence_index."""
    import hashlib
    from azure.search.documents import SearchClient
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

    search_client = SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
    )

    embeddings = get_embeddings()
    embedding = embeddings.embed_query(extracted_text)

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

    search_client.upload_documents([document])
    logger.info(
        "Indexed %s -> improve_evidence_index doc %s",
        upload_record["filename"], doc_id,
    )


@router.post("/gate", response_model=GateSubmitResponse)
def submit_gate(request: GateSubmitRequest) -> GateSubmitResponse:
    if blob_client is None:
        raise HTTPException(503, "Storage not configured")
    case = blob_client.load_case(request.case_id)
    if case is None:
        raise HTTPException(404, f"Case {request.case_id} not found")

    from backend.core.state import ImproveGraphState
    from backend.phases.define.validate import validate_define
    from backend.phases.measure.validate import validate_measure
    from backend.phases.analyse_phase.validate import validate_analyse_phase
    from backend.phases.improve.validate import validate_improve
    from backend.phases.control.validate import validate_control

    validate_map = {
        "define":        validate_define,
        "measure":       validate_measure,
        "analyse_phase": validate_analyse_phase,
        "improve":       validate_improve,
        "control":       validate_control,
    }
    validate_fn = validate_map.get(request.phase)
    if validate_fn is None:
        raise HTTPException(400, f"Unknown phase: {request.phase}")

    state: ImproveGraphState = {
        "case_id": request.case_id,
        "current_phase": request.phase,
        "current_user": request.submitted_by,
        "phase_inputs": {
            phase: (case.phases[phase].structured or {})
            for phase in case.phases
        },
        "chat_history": case.conversation_history,
        "gate_attempts": 0,
        "escalated": False,
        "citations": [],
        "analyst_output": None,
        "uploaded_files": [],
        "case_metadata": {
            "title": case.title,
            "belt_level": case.belt_level,
            "leader": case.leader,
            "department": case.department,
        },
    }

    result = validate_fn(state)
    phase_data = result.get("phase_inputs", {}).get(request.phase, {})
    passed = phase_data.get("_gate_passed", False)
    missing = phase_data.get("_missing_fields", [])

    if passed:
        validated = phase_data.get("_validated", {})
        blob_client.write_phase_gate(
            case_id=request.case_id,
            phase=request.phase,
            structured=validated,
            submitted_by=request.submitted_by,
            summary=f"Gate passed by {request.submitted_by}",
        )
        phase_order = ["define", "measure", "analyse_phase", "improve", "control"]
        idx = phase_order.index(request.phase)
        next_phase = phase_order[idx + 1] if idx < len(phase_order) - 1 else None
        return GateSubmitResponse(
            passed=True,
            phase=request.phase,
            message=(
                f"Phase complete. {'Moving to ' + next_phase if next_phase else 'Project complete!'}"
            ),
            next_phase=next_phase,
        )
    else:
        plain_missing = [f.replace("_", " ") for f in missing]
        return GateSubmitResponse(
            passed=False,
            phase=request.phase,
            missing_fields=plain_missing,
            message=f"Not quite ready yet. {len(missing)} item(s) still needed.",
        )


@router.get("/registry", response_model=list[RegistryEntryOut])
def get_registry() -> list[RegistryEntryOut]:
    """Management dashboard â returns all cases from registry."""
    if blob_client is None:
        raise HTTPException(503, "Storage not configured")
    registry = blob_client.load_registry()
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
def get_case(case_id: str):
    """Load full case document."""
    if blob_client is None:
        raise HTTPException(503, "Storage not configured")
    case = blob_client.load_case(case_id)
    if case is None:
        raise HTTPException(404, f"Case {case_id} not found")
    return case.model_dump()


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
        "analyse_phase": [
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
