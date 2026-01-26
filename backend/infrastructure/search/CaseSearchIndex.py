from __future__ import annotations

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex



class CaseSearchIndex:
    """Thin adapter over Azure AI Search for case indexing."""

    def __init__(self, endpoint: str, index_name: str, admin_key: str) -> None:
        self._endpoint = endpoint
        self._index_name = index_name
        self._admin_key = admin_key
        self._credential = AzureKeyCredential(admin_key)
        self._search_client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=self._credential,
        )
        self._index_client = SearchIndexClient(
            endpoint=endpoint,
            credential=self._credential,
        )

    def get_document(self, doc_id: str) -> dict[str, object]:
        return self._search_client.get_document(key=doc_id)

    def try_get_document(self, doc_id: str) -> dict[str, object] | None:
        try:
            return self.get_document(doc_id)
        except ResourceNotFoundError:
            return None

    def upload_documents(self, documents: list[dict[str, object]]) -> IndexDocumentsResult:
        return self._search_client.upload_documents(documents)

    def get_index(self, index_name: str) -> SearchIndex:
        return self._index_client.get_index(index_name)

    def ensure_index_exists(self, index_name: str, error_message: str) -> None:
        try:
            self.get_index(index_name)
        except ResourceNotFoundError as exc:
            raise ValueError(error_message) from exc
