from __future__ import annotations

import logging
import os
from functools import lru_cache

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings

from backend.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_embeddings() -> AzureOpenAIEmbeddings:
    """Return cached embeddings instance — text-embedding-3-large.
    Mirrors agent-resolve embeddings.py pattern: load_dotenv + os.environ."""
    load_dotenv(override=True)
    return AzureOpenAIEmbeddings(
        azure_deployment=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", ""),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", ""),
    )


@lru_cache(maxsize=1)
def get_case_vectorstore() -> AzureSearch:
    """Cached vectorstore for improve_case_index."""
    return AzureSearch(
        azure_search_endpoint=settings.AZURE_SEARCH_ENDPOINT,
        azure_search_key=settings.AZURE_SEARCH_API_KEY,
        index_name=settings.AZURE_SEARCH_IMPROVE_CASE_INDEX,
        embedding_function=get_embeddings(),
        search_type="hybrid",
    )


@lru_cache(maxsize=1)
def get_knowledge_vectorstore() -> AzureSearch:
    """Cached vectorstore for improve_knowledge_index."""
    return AzureSearch(
        azure_search_endpoint=settings.AZURE_SEARCH_ENDPOINT,
        azure_search_key=settings.AZURE_SEARCH_API_KEY,
        index_name=settings.AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX,
        embedding_function=get_embeddings(),
        search_type="hybrid",
    )


@lru_cache(maxsize=1)
def get_evidence_vectorstore() -> AzureSearch:
    """Cached vectorstore for improve_evidence_index."""
    return AzureSearch(
        azure_search_endpoint=settings.AZURE_SEARCH_ENDPOINT,
        azure_search_key=settings.AZURE_SEARCH_API_KEY,
        index_name=settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX,
        embedding_function=get_embeddings(),
        search_type="hybrid",
    )


def search_knowledge(query: str, phase: str = None,
                     k: int = 4) -> list[dict]:
    """Search improve_knowledge_index. Filter by phase if provided."""
    vs = get_knowledge_vectorstore()
    filters = f"phase eq '{phase}'" if phase else None
    try:
        docs = vs.similarity_search(query, k=k, filters=filters)
        return [
            {
                "content": d.page_content,
                "source": d.metadata.get("source", ""),
                "tool_name": d.metadata.get("tool_name", ""),
                "phase": d.metadata.get("phase", ""),
                "section_title": d.metadata.get("section_title", ""),
            }
            for d in docs
        ]
    except Exception as e:
        logger.warning("Knowledge search failed: %s", e)
        return []


def search_cases(query: str, k: int = 3) -> list[dict]:
    """Search improve_case_index for similar past improvement cases."""
    vs = get_case_vectorstore()
    try:
        docs = vs.similarity_search(query, k=k)
        return [
            {
                "content": d.page_content,
                "case_id": d.metadata.get("case_id", ""),
                "title": d.metadata.get("title", ""),
                "phase": d.metadata.get("current_phase", ""),
                "rag_status": d.metadata.get("rag_status", ""),
            }
            for d in docs
        ]
    except Exception as e:
        logger.warning("Case search failed: %s", e)
        return []


def search_evidence(query: str, case_id: str, k: int = 4) -> list[dict]:
    """Search improve_evidence_index filtered by case_id.
    Returns uploaded document extracts for this specific case only."""
    try:
        import json
        from azure.search.documents import SearchClient
        from azure.search.documents.models import VectorizedQuery

        search_client = SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX,
            credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
        )

        # Generate embedding for the query
        embeddings = get_embeddings()
        query_vector = embeddings.embed_query(query)

        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=k,
            fields="content_vector",
        )

        results = search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            filter=f"case_id eq '{case_id}'",
            select=["content", "metadata", "case_id"],
            top=k,
        )

        output = []
        for r in results:
            meta = {}
            try:
                meta = json.loads(r.get("metadata") or "{}")
            except Exception:
                pass
            output.append({
                "content": r.get("content", ""),
                "filename": meta.get("filename", ""),
                "upload_phase": meta.get("upload_phase", ""),
                "content_type": meta.get("content_type", ""),
            })
        return output

    except Exception as e:
        logger.warning("Evidence search failed: %s", e)
        return []
