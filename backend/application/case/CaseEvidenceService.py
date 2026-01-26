from backend.infrastructure.storage.CaseRepository import CaseRepository


class CaseEvidenceService:
    def __init__(self, repository: CaseRepository):
        self.repo = repository

    def upload_evidence(self, case_id: str, filename: str, data: bytes, content_type: str):
        self._ensure_case_exists(case_id)
        self.repo.add_evidence(case_id, filename, data, content_type)

    def list_evidence(self, case_id: str) -> list[dict]:
        self._ensure_case_exists(case_id)
        return self.repo.list_evidence(case_id)

    def get_evidence(self, case_id: str, filename: str) -> tuple[bytes, str]:
        return self.repo.get_evidence(case_id, filename)

    def _ensure_case_exists(self, case_id: str) -> None:
        self.repo.load(case_id)
