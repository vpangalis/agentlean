from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from typing import NoReturn

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ServiceRequestError,
)
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from openai import (
    APIConnectionError,
    APITimeoutError,
    BadRequestError,
    OpenAIError,
    RateLimitError,
)
from openai import AuthenticationError as OpenAIAuthenticationError

from backend.core.config import settings
from backend.core.errors import AgentImproveError, KnowledgeSearchError

logger = logging.getLogger(__name__)

# Every failure mode a retrieval call can raise. Two services are involved:
# Azure AI Search, and Azure OpenAI for the query embedding — the embedding
# call sits inside the same try, so omitting OpenAIError here would let a
# raw provider exception escape and take down the coaching turn.
RETRIEVAL_EXCEPTIONS = (
    HttpResponseError,
    ServiceRequestError,
    ClientAuthenticationError,
    OpenAIError,
)


def _search_error(exc: Exception, index: str) -> AgentImproveError:
    """Classify an Azure AI Search failure into the §12.3 envelope.

    `severity` drives circuit-breaker retry-vs-stop and
    `retry_recommendation` drives the fallback chain's backoff choice (§4.8),
    so a malformed query must not be reported as transient — retrying it just
    fails again at the same cost.
    """
    # -- Azure OpenAI (query embedding) --------------------------------
    # Checked first: these are a disjoint hierarchy from azure.core's, and
    # the EMBEDDING_ prefix keeps "which service broke" readable in the log.
    if isinstance(exc, OpenAIError):
        if isinstance(exc, OpenAIAuthenticationError):
            code, severity, retry = "EMBEDDING_AUTH_FAILURE", "permanent", "do_not_retry"
        elif isinstance(exc, RateLimitError):
            code, severity, retry = "EMBEDDING_RATE_LIMIT", "transient", "retry_after_backoff"
        elif isinstance(exc, BadRequestError):
            code, severity, retry = "EMBEDDING_INVALID_REQUEST", "permanent", "do_not_retry"
        elif isinstance(exc, (APIConnectionError, APITimeoutError)):
            code, severity, retry = "EMBEDDING_CONNECTION_FAILURE", "transient", "retry_after_backoff"
        else:
            code, severity, retry = "EMBEDDING_SERVICE_ERROR", "transient", "retry_after_backoff"

    # -- Azure AI Search ------------------------------------------------
    # ClientAuthenticationError subclasses HttpResponseError, so it must be
    # tested before it — otherwise a bad key classifies as a generic 4xx.
    elif isinstance(exc, ClientAuthenticationError):
        code, severity, retry = "AUTH_FAILURE", "permanent", "do_not_retry"
    elif isinstance(exc, ServiceRequestError):
        code, severity, retry = "CONNECTION_FAILURE", "transient", "retry_after_backoff"
    elif isinstance(exc, HttpResponseError):
        status = getattr(exc, "status_code", None)
        if status == 429:
            code, severity, retry = "RATE_LIMIT", "transient", "retry_after_backoff"
        elif status is not None and 400 <= status < 500:
            # Bad filter / bad field / bad syntax — our bug, not the service's.
            code, severity, retry = "INVALID_QUERY", "permanent", "do_not_retry"
        else:
            code, severity, retry = "SERVICE_ERROR", "transient", "retry_after_backoff"
    else:  # pragma: no cover — defensive
        code, severity, retry = "UNKNOWN", "transient", "retry_after_backoff"

    return AgentImproveError(
        error_code=code,
        severity=severity,
        retry_recommendation=retry,
        affected_identifier=index,
        message=str(exc).strip().replace("\n", " ")[:500],
    )


def _fail(exc: Exception, index: str, **extra: object) -> NoReturn:
    """Classify, log, and raise. Single exit path for every retrieval failure.

    Callers must never translate a failure into `[]` — an empty list means
    the search ran and matched nothing, and nothing else.
    """
    err = _search_error(exc, index=index)
    logger.error(
        "Retrieval failed | %s",
        err.to_step_log_entry(layer="retrieval", **extra),
    )
    raise KnowledgeSearchError(err) from exc


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


# Cross-phase bucket in improve_knowledge_index.phase_relevance. Confirmed
# against the live index: the values present are define / measure / analyse /
# improve / control / general — there is no 'all'. Content tagged 'general'
# must stay reachable from every phase, so a phase filter always ORs it in.
CROSS_PHASE_RELEVANCE = "general"


def _phase_filter(phase: str | None) -> str | None:
    """OData filter for improve_knowledge_index, or None for no filter.

    The field is `phase_relevance`, NOT `phase` — there is no `phase` field on
    this index, and asking for one makes Azure reject the whole query.
    """
    if not phase:
        return None
    safe = phase.replace("'", "''")          # OData escapes ' by doubling it
    return (f"phase_relevance eq '{safe}' "
            f"or phase_relevance eq '{CROSS_PHASE_RELEVANCE}'")


def search_knowledge(query: str, phase: str = None,
                     k: int = 4) -> list[dict]:
    """Search improve_knowledge_index. Filter by phase if provided.

    Returns [] only when the search ran and matched nothing. If the search
    itself fails, raises KnowledgeSearchError rather than returning [] — the
    caller must be able to tell "no methodology content matched" apart from
    "retrieval is broken".
    """
    vs = get_knowledge_vectorstore()
    filters = _phase_filter(phase)
    try:
        docs = vs.similarity_search(query, k=k, filters=filters)
    except RETRIEVAL_EXCEPTIONS as e:
        _fail(e, settings.AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX,
              search="knowledge", filter=filters, query=query[:120])

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


def search_cases(query: str, k: int = 3) -> list[dict]:
    """Search improve_case_index for similar past improvement cases.

    Uses a raw SearchClient with the case index's own field names
    (content_text / embedding) rather than the LangChain AzureSearch
    wrapper. The wrapper resolves its content/vector field names from
    process-global settings, which here default to content/content_vector
    to serve improve_knowledge_index and improve_evidence_index; the case
    index uses a different schema, so it is queried directly instead.
    Mirrors the search_evidence() raw-client pattern below.

    Returns [] only when the search ran and matched nothing. Raises
    KnowledgeSearchError if the search itself fails."""
    search_client = SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_SEARCH_IMPROVE_CASE_INDEX,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
    )

    try:
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

        # The HTTP call is lazy — it fires on iteration, so materialising the
        # list must stay inside the try or the failure escapes unclassified.
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
    except RETRIEVAL_EXCEPTIONS as e:
        _fail(e, settings.AZURE_SEARCH_IMPROVE_CASE_INDEX,
              search="case_history", query=query[:120])


def search_evidence(query: str, case_id: str, k: int = 4) -> list[dict]:
    """Search improve_evidence_index filtered by case_id.
    Returns uploaded document extracts for this specific case only.

    Returns [] only when the search ran and matched nothing. Raises
    KnowledgeSearchError if the search itself fails."""
    search_client = SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
    )
    safe_case_id = case_id.replace("'", "''")   # OData escapes ' by doubling

    try:
        query_vector = get_embeddings().embed_query(query)
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=k,
            fields="content_vector",
        )

        results = search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            filter=f"case_id eq '{safe_case_id}'",
            select=["content", "metadata", "case_id"],
            top=k,
        )

        # Iteration is what fires the HTTP call — keep it inside the try.
        output = []
        for r in results:
            output.append({
                "content": r.get("content", ""),
                **_evidence_metadata(r),
            })
        return output

    except RETRIEVAL_EXCEPTIONS as e:
        _fail(e, settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX,
              search="evidence", case_id=case_id, query=query[:120])


def _evidence_metadata(row: dict) -> dict:
    """Parse one evidence row's metadata blob into the fields callers read.

    A malformed blob on a single document degrades that document rather than
    failing the whole search — but it is logged, not silently dropped, so a
    systematically bad writer is visible.
    """
    try:
        meta = json.loads(row.get("metadata") or "{}")
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(
            "Unparseable evidence metadata on doc %s: %s", row.get("id", "?"), e
        )
        meta = {}
    return {
        "filename": meta.get("filename", ""),
        "upload_phase": meta.get("upload_phase", ""),
        "content_type": meta.get("content_type", ""),
    }


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
    improve_knowledge_index via search_knowledge() across all phases —
    deliberately unfiltered, so cross-phase methodology stays reachable.
    (The index does have a per-phase filter field, `phase_relevance`; this
    caller simply chooses not to narrow. See _phase_filter().)"""
    query_parts = []
    if work_product_label:
        query_parts.append(work_product_label)
    query_parts.append((user_message or "")[:200])
    query = " ".join(p for p in query_parts if p).strip()
    if not query:
        return None

    try:
        results = search_knowledge(query, k=top_k)
    except KnowledgeSearchError:
        # Already logged with full classification in search_knowledge.
        # Coaching continues without grounding — a quality degradation, not
        # an availability failure (§4.8, Search breaker).
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
        "Your response MUST contain three flowing sections, "
        "in this order, with NO visible labels or headers — "
        "write them as natural connected paragraphs:\n\n"
        "FIRST — Teach the concept (2-4 sentences). "
        "Explain WHY this step matters and WHAT GOOD LOOKS "
        "LIKE. Reference the Black Belt material above where "
        "relevant. Use a natural opening like 'A strong "
        "problem statement…' or 'In this phase…' — NOT a "
        "label like 'PART 1' or 'TEACH'.\n\n"
        "SECOND — Present the template (2-4 lines). "
        "Introduce it with a natural lead-in like 'Use this "
        "format:' or 'Try filling in this template:' — "
        "NEVER 'PART 2' or 'TEMPLATE'. Use [square brackets] "
        "for placeholders.\n\n"
        "THIRD — Ask one specific question (1-2 sentences). "
        "Lead naturally into it. NEVER 'PART 3' or 'ASK'.\n\n"
        "TOTAL LENGTH: 160-400 words. NEVER use labels like "
        "PART 1, PART 2, PART 3, TEACH, TEMPLATE, ASK in "
        "your output. Write as flowing connected paragraphs, "
        "not a structured form.\n\n"
        "DO NOT just acknowledge and ask a question. "
        "DO NOT skip the template. "
        "DO NOT exceed 400 words. "
        "DO NOT use scaffolding labels in the output."
    )
