from __future__ import annotations

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
from backend.storage.blob import blob_client
from backend.storage.models import CaseDocument

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


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
    """Upload a file â stub classification until Upload agent is implemented."""
    if blob_client is None:
        raise HTTPException(503, "Storage not configured")
    data = file.file.read()
    blob_path = blob_client.upload_file(
        case_id,
        file.filename,
        data,
        file.content_type or "application/octet-stream",
    )
    return {
        "blob_path": blob_path,
        "filename": file.filename,
        "classification": "pending â upload agent not yet implemented",
    }


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
