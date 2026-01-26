from __future__ import annotations

import json
from typing import Any

from backend.infrastructure.storage.blob_client import AzureBlobClient


class CaseReadRepository:
    """Infrastructure repository for reading case JSON documents."""

    CASES_PREFIX = "cases/"
    CASE_JSON_SUFFIX = "/case.json"

    def __init__(self, connection_string: str, container_name: str) -> None:
        self._blob_client = AzureBlobClient(connection_string, container_name)

    def list_case_paths(self) -> list[str]:
        files = self._blob_client.list_files(self.CASES_PREFIX)
        return [f["name"] for f in files if f["name"].endswith(self.CASE_JSON_SUFFIX)]

    def load_case(self, path: str) -> dict[str, Any]:
        raw = self._blob_client.download_json(path)
        return json.loads(raw)
