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
    """Search improve_case_index for similar past improvement cases.

    Uses a raw SearchClient with the case index's own field names
    (content_text / embedding) rather than the LangChain AzureSearch
    wrapper. The wrapper resolves its content/vector field names from
    process-global settings, which here default to content/content_vector
    to serve improve_knowledge_index and improve_evidence_index; the case
    index uses a different schema, so it is queried directly instead.
    Mirrors the search_evidence() raw-client pattern below."""
    try:
        from azure.search.documents.models import VectorizedQuery

        search_client = SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_SEARCH_IMPROVE_CASE_INDEX,
            credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
        )

        query_vector = get_embeddings().embed_query(query)
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=k,
            fields="embedding",
        )

        results = search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=["content_text", "case_id", "title",
                    "current_phase", "rag_status"],
            top=k,
        )

        return [
            {
                "content": r.get("content_text", ""),
                "case_id": r.get("case_id", ""),
                "title": r.get("title", ""),
                "phase": r.get("current_phase", ""),
                "rag_status": r.get("rag_status", ""),
            }
            for r in results
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


def active_work_product_label(state_summary: str | None) -> str | None:
    """Best-effort extraction of the active work product label from a
    phase state summary. Every phase summary ends with a 'Continue with
    <label> ...' next-action hint; return the label that follows, or
    None when it cannot be determined."""
    if not state_summary:
        return None
    marker = "Continue with "
    idx = state_summary.find(marker)
    if idx == -1:
        return None
    tail = state_summary[idx + len(marker):]
    for sep in (". ", " — ", "—", "\n"):
        cut = tail.find(sep)
        if cut != -1:
            tail = tail[:cut]
    label = tail.strip()
    return label or None


def build_knowledge_context(
    phase: str,
    user_message: str,
    work_product_label: str | None = None,
    top_k: int = 3,
) -> str | None:
    """Retrieve relevant Black Belt methodology chunks for the current
    conversation turn and format them as a SystemMessage content block.

    Returns the formatted reference block, or None when nothing relevant
    is found. The query is built from the user's latest message and, when
    known, the active work product label (high-signal). Queries
    improve_knowledge_index via search_knowledge() across all phases
    (the live index has no per-phase filter field)."""
    query_parts = []
    if work_product_label:
        query_parts.append(work_product_label)
    query_parts.append((user_message or "")[:200])
    query = " ".join(p for p in query_parts if p).strip()
    if not query:
        return None

    try:
        results = search_knowledge(query, k=top_k)
    except Exception as e:
        logger.warning("build_knowledge_context retrieval failed: %s", e)
        return None

    if not results:
        return None

    blocks = []
    for i, r in enumerate(results, 1):
        text = (
            r.get("content") if isinstance(r, dict)
            else getattr(r, "page_content", "")
        )
        if not text:
            continue
        blocks.append(f"[Reference {i}]\n{text.strip()[:1200]}")

    if not blocks:
        return None

    return (
        "═══════════════════════════════════════════\n"
        "BLACK BELT METHODOLOGY REFERENCES — USE THESE\n"
        "═══════════════════════════════════════════\n\n"
        + "\n\n".join(blocks)
        + "\n\n"
        "═══════════════════════════════════════════\n"
        "REQUIRED RESPONSE STRUCTURE\n"
        "═══════════════════════════════════════════\n\n"
        "You MUST structure your response in 3 parts:\n\n"
        "PART 1 — TEACH (2-4 sentences):\n"
        "Explain the methodology concept relevant to this turn. "
        "Reference the Black Belt material above. "
        "Tell the team WHY this step matters and "
        "WHAT GOOD LOOKS LIKE.\n\n"
        "PART 2 — SHOW THE TEMPLATE (2-4 lines):\n"
        "Provide a concrete fill-in template the team can "
        "complete. Use placeholders in [square brackets].\n\n"
        "PART 3 — ASK ONE FOCUSED QUESTION (1-2 sentences):\n"
        "Ask exactly one specific question to elicit the next "
        "input. Never list multiple questions.\n\n"
        "TOTAL LENGTH: 150-400 words. Short, generic responses "
        "are unacceptable — the team is learning the methodology "
        "by doing, and they need substantive coaching at each turn.\n\n"
        "DO NOT just acknowledge and ask a question. "
        "DO NOT skip the template. "
        "DO NOT exceed 400 words."
    )
