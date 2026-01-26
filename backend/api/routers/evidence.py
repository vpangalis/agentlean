from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from typing import List

from backend.main import build_backend_container
from backend.application.case.CaseEvidenceService import CaseEvidenceService


router = APIRouter(prefix="/cases", tags=["evidence"])


def _evidence_service() -> CaseEvidenceService:
    container = build_backend_container()
    return container.application.case_evidence_service


@router.post("/{case_id}/evidence", status_code=201)
def upload_evidence(case_id: str, files: List[UploadFile] = File(...)):
    service = _evidence_service()
    uploaded = []
    failed = []

    for file in files:
        filename = file.filename or "unknown"
        content_type = file.content_type or "application/octet-stream"
        try:
            data = file.file.read()
            service.upload_evidence(case_id, filename, data, content_type)
            uploaded.append(
                {
                    "filename": filename,
                    "content_type": content_type,
                    "size_bytes": len(data),
                }
            )
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Case not found")
        except FileExistsError as e:
            failed.append({"filename": filename, "reason": str(e)})
        except Exception:
            failed.append({"filename": filename, "reason": "Upload failed"})

    if failed and uploaded:
        return Response(
            content={
                "case_id": case_id,
                "uploaded": uploaded,
                "failed": failed,
            }.__str__(),
            status_code=207,
        )

    if failed and not uploaded:
        raise HTTPException(status_code=409, detail=failed)

    return {
        "case_id": case_id,
        "uploaded": uploaded,
        "failed": [],
    }


@router.get("/{case_id}/evidence")
def list_evidence(case_id: str):
    service = _evidence_service()
    try:
        return {
            "case_id": case_id,
            "evidence": service.list_evidence(case_id),
        }
    except Exception:
        raise HTTPException(status_code=404, detail="Case not found")


@router.get("/{case_id}/evidence/{filename}")
def download_evidence(case_id: str, filename: str):
    service = _evidence_service()
    try:
        data, content_type = service.get_evidence(case_id, filename)
        return Response(
            content=data,
            media_type=content_type,
            headers={
                "Content-Disposition": f'inline; filename="{filename}"'
            },
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
