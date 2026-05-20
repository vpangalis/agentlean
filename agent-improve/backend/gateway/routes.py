from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from backend.gateway.schemas import (
    CaseCreateRequest,
    CaseCreateResponse,
    AskRequest,
    AskResponse,
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
    """Conversational turn — stub until graph is wired."""
    # Stub: graph not yet implemented
    return AskResponse(
        answer="[Graph not yet implemented — stub response]",
        phase=request.phase,
        gate_status=GateStatus(phase=request.phase, passed=False, attempts=0),
        escalated=False,
    )


@router.post("/upload")
def upload_file(
    case_id: str = Form(...),
    uploaded_by: str = Form(...),
    phase: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload a file — stub classification until Upload agent is implemented."""
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
        "classification": "pending — upload agent not yet implemented",
    }


@router.post("/gate", response_model=GateSubmitResponse)
def submit_gate(request: GateSubmitRequest) -> GateSubmitResponse:
    """Gate submission — stub until Validator node is implemented."""
    return GateSubmitResponse(
        passed=False,
        phase=request.phase,
        missing_fields=["Gate validator not yet implemented"],
        message="Gate validator is not yet implemented.",
    )


@router.get("/registry", response_model=list[RegistryEntryOut])
def get_registry() -> list[RegistryEntryOut]:
    """Management dashboard — returns all cases from registry."""
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


__all__ = ["router"]
