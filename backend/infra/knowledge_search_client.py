from __future__ import annotations

import logging

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery


class KnowledgeSearchClient:
    def __init__(self, endpoint: str, index_name: str, admin_key: str) -> None:
        self._logger = logging.getLogger("knowledge_search_client")
        self._search_client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(admin_key),
        )

    def hybrid_search(
        self,
        search_text: str,
        embedding: list[float],
        top_k: int,
    ) -> list[dict]:
        self._logger.info(
            "Running knowledge hybrid search",
            extra={"search_text": search_text, "top_k": top_k},
        )
        vector_query = VectorizedQuery(
            vector=embedding,
            fields="embedding",
            k_nearest_neighbors=top_k,
        )
        results = self._search_client.search(
            search_text=search_text or "*",
            vector_queries=[vector_query],
            top=top_k,
        )
        return [dict(r) for r in results]


__all__ = ["KnowledgeSearchClient"]
