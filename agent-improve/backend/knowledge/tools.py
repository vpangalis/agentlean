from __future__ import annotations

import logging

from langchain_core.tools import tool

from backend.knowledge.retriever import search_knowledge, search_cases, search_evidence

logger = logging.getLogger(__name__)


# ── Agent Improve indexes ──────────────────────────────────────────


@tool
def search_improve_knowledge(query: str, phase: str = "") -> str:
    """Search DMAIC methodology knowledge base.
    Use for tool explanations, phase guidance, worked examples.
    Optionally filter by phase: define/measure/analyse_phase/improve/control"""
    results = search_knowledge(query, phase=phase or None)
    if not results:
        return "No relevant methodology content found."
    return "\n\n".join(
        f"[{r['tool_name'] or r['section_title']}] {r['content']}"
        for r in results
    )


@tool
def search_improve_cases(query: str) -> str:
    """Search past improvement cases for similar projects and outcomes."""
    results = search_cases(query)
    if not results:
        return "No similar improvement cases found."
    return "\n\n".join(
        f"[Case {r['case_id']}: {r['title']}] {r['content']}"
        for r in results
    )


@tool
def search_improve_evidence(query: str, case_id: str) -> str:
    """Search uploaded project documents for this specific case.
    Use when the team has uploaded process maps, SIPOC diagrams,
    flipcharts, or other documents and you need to reference them.
    Always requires case_id — never searches across cases.
    Source: improve_evidence_index"""
    if not case_id:
        return "case_id is required for evidence search."
    results = search_evidence(query, case_id=case_id)
    if not results:
        return "No uploaded documents found for this case."
    return "\n\n".join(
        f"[Uploaded: {r['filename']} · phase: {r['upload_phase']}] "
        f"{r['content']}"
        for r in results
    )


# ── Agent Resolve indexes (read-only cross-agent queries) ──────────


@tool
def search_resolve_cases(query: str) -> str:
    """Search Agent Resolve past incident cases for relevant insights.
    Use in Analyse and Improve phases to surface past root causes and solutions.
    Source: Agent Resolve case_index_v3"""
    try:
        from functools import lru_cache
        from azure.core.credentials import AzureKeyCredential
        from langchain_community.vectorstores.azuresearch import AzureSearch
        from backend.knowledge.retriever import get_embeddings
        from backend.core.config import settings

        @lru_cache(maxsize=1)
        def _get_resolve_case_store():
            return AzureSearch(
                azure_search_endpoint=settings.AZURE_SEARCH_ENDPOINT,
                azure_search_key=settings.AZURE_SEARCH_API_KEY,
                index_name=settings.AZURE_SEARCH_RESOLVE_CASE_INDEX,
                embedding_function=get_embeddings(),
                search_type="hybrid",
            )

        docs = _get_resolve_case_store().similarity_search(query, k=3)
        if not docs:
            return "No relevant past incidents found in Agent Resolve."
        return "\n\n".join(
            f"[Agent Resolve · case_index_v3 · {d.metadata.get('case_id','')}] "
            f"{d.page_content}"
            for d in docs
        )
    except Exception as e:
        logger.warning("search_resolve_cases failed: %s", e)
        return "Agent Resolve case search unavailable."


@tool
def search_resolve_knowledge(query: str) -> str:
    """Search Agent Resolve domain knowledge base.
    Use for technical/domain context alongside DMAIC methodology guidance.
    Source: Agent Resolve knowledge_index_v2"""
    try:
        from functools import lru_cache
        from langchain_community.vectorstores.azuresearch import AzureSearch
        from backend.knowledge.retriever import get_embeddings
        from backend.core.config import settings

        @lru_cache(maxsize=1)
        def _get_resolve_knowledge_store():
            return AzureSearch(
                azure_search_endpoint=settings.AZURE_SEARCH_ENDPOINT,
                azure_search_key=settings.AZURE_SEARCH_API_KEY,
                index_name=settings.AZURE_SEARCH_RESOLVE_KNOWLEDGE_INDEX,
                embedding_function=get_embeddings(),
                search_type="hybrid",
            )

        docs = _get_resolve_knowledge_store().similarity_search(query, k=3)
        if not docs:
            return "No relevant knowledge found in Agent Resolve."
        return "\n\n".join(
            f"[Agent Resolve · knowledge_index_v2] {d.page_content}"
            for d in docs
        )
    except Exception as e:
        logger.warning("search_resolve_knowledge failed: %s", e)
        return "Agent Resolve knowledge search unavailable."


@tool
def search_resolve_evidence(query: str) -> str:
    """Search Agent Resolve evidence documents.
    Use in Measure phase for baseline data context.
    Source: Agent Resolve evidence_index_v1"""
    try:
        from functools import lru_cache
        from langchain_community.vectorstores.azuresearch import AzureSearch
        from backend.knowledge.retriever import get_embeddings
        from backend.core.config import settings

        @lru_cache(maxsize=1)
        def _get_resolve_evidence_store():
            return AzureSearch(
                azure_search_endpoint=settings.AZURE_SEARCH_ENDPOINT,
                azure_search_key=settings.AZURE_SEARCH_API_KEY,
                index_name=settings.AZURE_SEARCH_RESOLVE_EVIDENCE_INDEX,
                embedding_function=get_embeddings(),
                search_type="hybrid",
            )

        docs = _get_resolve_evidence_store().similarity_search(query, k=3)
        if not docs:
            return "No relevant evidence found in Agent Resolve."
        return "\n\n".join(
            f"[Agent Resolve · evidence_index_v1] {d.page_content}"
            for d in docs
        )
    except Exception as e:
        logger.warning("search_resolve_evidence failed: %s", e)
        return "Agent Resolve evidence search unavailable."


@tool
def search_flow_vsm(query: str) -> str:
    """Search Agent Flow VSM process data.
    STUB — activates when Agent Flow indexes are populated.
    Source: Agent Flow vsm_index (future)"""
    return "Agent Flow VSM index not yet available."
