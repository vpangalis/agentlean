from __future__ import annotations

import json
import logging
import os
import re
import threading
import time
from contextlib import contextmanager
from functools import lru_cache, wraps
from typing import Any, Callable, Iterator, NoReturn, TypeVar

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ServiceRequestError,
)
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
)
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv
from langsmith import trace, traceable
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


# ── step 8.0 slice: what each HTTP attempt did, per thread ──────────────
#
# A span's wall time cannot say whether it was ONE slow call or a fast call
# retried after a 429. So each embed/search span collects, for its own thread
# only, every attempt the clients report:
#   * httpx logs one INFO line per HTTP response ("HTTP Request: POST ... 429")
#     — the OpenAI embeddings client rides on httpx;
#   * the OpenAI client logs "Retrying request to ... in N seconds" — its
#     backoff wait;
#   * Azure AI Search (azure-core, not httpx) reports each attempt through the
#     per-call `raw_response_hook`, which azure-core runs inside its retry loop.
# Observation only: the filters return True, so no record is suppressed, and
# nothing is collected on a thread that has no watch open.
_WATCH = threading.local()
_STATUS = re.compile(r'"HTTP/[\d.]+ (\d{3})')
_RETRY_WAIT = re.compile(r"Retrying request to \S+ in ([\d.]+) seconds")


def _observe(record: logging.LogRecord) -> bool:
    events = getattr(_WATCH, "events", None)
    if events is not None:
        events.append((time.monotonic(), record.name, record.getMessage()))
    return True


logging.getLogger("httpx").addFilter(_observe)
logging.getLogger("openai._base_client").addFilter(_observe)


@contextmanager
def _http_watch() -> Iterator[list[tuple[float, str, str]]]:
    _WATCH.events = []
    try:
        yield _WATCH.events
    finally:
        _WATCH.events = None


def _azure_hook(events: list[tuple[float, str, str]]) -> Any:
    def hook(response: Any) -> None:
        events.append((time.monotonic(), "azure.search",
                       f'"HTTP/1.1 {response.http_response.status_code}'))
    return hook


def _http_summary(events: list[tuple[float, str, str]]) -> dict[str, Any]:
    """Attempts, statuses, retries and backoff seconds, from one watch."""
    statuses = [int(m.group(1)) for _, _, msg in events
                for m in [_STATUS.search(msg)] if m]
    waits = [float(m.group(1)) for _, _, msg in events
             for m in [_RETRY_WAIT.search(msg)] if m]
    return {"attempts": len(statuses), "statuses": statuses,
            "http_429": statuses.count(429), "retries": max(0, len(statuses) - 1),
            "backoff_s": round(sum(waits), 3),
            "thread": threading.current_thread().name}


# ── step 6.54 (G-93): each client is built ONCE, and before any turn ──────
#
# Measured at 6.54's step 0: one embeddings build costs ~2.5 s and one knowledge
# vectorstore build ~3.5 s — mostly loading the TLS certificate bundle, plus the
# vectorstore's index-definition read; no login token (API-key auth). Six lookup
# threads missing an empty `lru_cache` together each built their own: 7.2 s
# apiece, 38 s of certificate loading summed. `lru_cache` guarantees one CACHED
# value, not one BUILD. `_single_flight` serialises the miss so the first caller
# builds and the rest read what it built.
_T = TypeVar("_T")


def _single_flight(cached: Callable[..., _T]) -> Callable[..., _T]:
    lock = threading.Lock()

    @wraps(cached)
    def call(*args: Any, **kwargs: Any) -> _T:
        with lock:
            return cached(*args, **kwargs)

    call.cache_clear = getattr(cached, "cache_clear")  # type: ignore[attr-defined]
    return call


#: One `SearchClient` per index for the process. Case and evidence searches
#: built one PER CALL — 7–12 per lookup, each loading certificates afresh.
#: Azure SDK clients are documented as thread-safe for concurrent use.
_SEARCH_CLIENTS: dict[str, SearchClient] = {}
_SEARCH_LOCK = threading.Lock()


@traceable(run_type="chain", name="retriever.build_search_client")
def _build_search_client(index_name: str) -> SearchClient:
    return SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=index_name,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
    )


def get_search_client(index_name: str) -> SearchClient:
    """The process's one client for `index_name`, built on first use."""
    with _SEARCH_LOCK:
        client = _SEARCH_CLIENTS.get(index_name)
        if client is None:
            client = _SEARCH_CLIENTS[index_name] = _build_search_client(index_name)
        return client


def warm_clients() -> None:
    """Build every retrieval client a Define turn uses (app startup, 6.54)."""
    get_embeddings()
    get_knowledge_vectorstore()
    get_search_client(settings.AZURE_SEARCH_IMPROVE_CASE_INDEX)
    get_search_client(settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX)


def close_clients() -> None:
    """Close the per-index search clients and forget every cached client
    (app shutdown). Idempotent."""
    with _SEARCH_LOCK:
        clients = list(_SEARCH_CLIENTS.values())
        _SEARCH_CLIENTS.clear()
    for client in clients:
        client.close()
    for getter in (get_embeddings, get_knowledge_vectorstore,
                   get_evidence_vectorstore):
        getattr(getter, "cache_clear")()


# §51 / step 8.0 slice — every direct Azure call gets a span. Inputs are cut
# to the query and its parameters: a 1,536-float vector in every span would
# cost more to ship than the call it measures.


@_single_flight
@lru_cache(maxsize=1)
@traceable(run_type="chain", name="retriever.get_embeddings")
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


# The full field list of improve_knowledge_index (ARCHITECTURE.md §7.1).
#
# This is NOT decoration, and it is not for index creation — the index
# already exists. LangChain's AzureSearch never introspects the live index;
# it defaults `self.fields` to [id, content, content_vector, metadata] and
# promotes a metadata key to a top-level field only when the key matches a
# name in THAT list:
#
#     additional_fields = {k: v for k, v in metadata.items()
#                          if k in [x.name for x in self.fields]}
#
# So without declaring source_file / phase_relevance / page_number here,
# writes silently bury them in the metadata JSON blob, where `$filter`
# cannot reach them — no error, just a permanently unfilterable index.
# Passing `fields` is safe for reads: LangChain only inspects it when the
# index is absent, so it cannot mutate an existing schema.
KNOWLEDGE_INDEX_FIELDS = [
    SimpleField(name="id", type=SearchFieldDataType.String,
                key=True, filterable=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=3072,          # text-embedding-3-large
        vector_search_profile_name="default",
    ),
    SearchableField(name="metadata", type=SearchFieldDataType.String),
    SimpleField(name="source_file", type=SearchFieldDataType.String,
                filterable=True),
    SimpleField(name="phase_relevance", type=SearchFieldDataType.String,
                filterable=True),
    SimpleField(name="page_number", type=SearchFieldDataType.Int32,
                filterable=True),
]


@_single_flight
@lru_cache(maxsize=1)
@traceable(run_type="chain", name="retriever.get_knowledge_vectorstore")
def get_knowledge_vectorstore() -> AzureSearch:
    """Cached vectorstore for improve_knowledge_index."""
    return AzureSearch(
        azure_search_endpoint=settings.AZURE_SEARCH_ENDPOINT,
        azure_search_key=settings.AZURE_SEARCH_API_KEY,
        index_name=settings.AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX,
        embedding_function=get_embeddings(),
        search_type="hybrid",
        fields=KNOWLEDGE_INDEX_FIELDS,
    )


# The full field list of improve_evidence_index (§23.2), as of step 6.13.
#
# Same contract as KNOWLEDGE_INDEX_FIELDS above and the same reason: LangChain
# never introspects the live index, so a metadata key reaches a top-level
# filterable field only when it is named here. §23.4.
#
# > **This list guards a function nothing currently calls.** Both live paths
# > use a raw `SearchClient` — `_index_upload` writes with `upload_documents`
# > and `search_evidence` reads with `search` — so §23.4's trap is not armed on
# > either. `get_evidence_vectorstore` below is declared and called by nothing
# > (recorded at DECISIONS Part AT). It is declared correctly anyway, because a
# > dead function that is revived without this list fails silently, and the
# > silence is the whole failure mode §23.4 exists to describe.
EVIDENCE_INDEX_FIELDS = [
    SimpleField(name="id", type=SearchFieldDataType.String,
                key=True, filterable=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=3072,          # text-embedding-3-large
        vector_search_profile_name="default",
    ),
    SearchableField(name="metadata", type=SearchFieldDataType.String),
    SimpleField(name="case_id", type=SearchFieldDataType.String,
                filterable=True),
    # The seven applied at 6.13. Attributes are §23.2's, field for field.
    SimpleField(name="phase", type=SearchFieldDataType.String,
                filterable=True),
    SimpleField(name="uploaded_at", type=SearchFieldDataType.String,
                filterable=True, sortable=True),
    SearchableField(name="role", type=SearchFieldDataType.String,
                    filterable=True),
    SimpleField(name="kind", type=SearchFieldDataType.String,
                filterable=True),
    SearchableField(name="description", type=SearchFieldDataType.String),
    SimpleField(name="content_digest", type=SearchFieldDataType.String,
                filterable=True),
    SimpleField(name="shape_match", type=SearchFieldDataType.String,
                filterable=True),
]

# What `search_evidence` asks the index to return. `select` is not `fields`:
# this is the projection on a raw SearchClient read, and a field missing here
# comes back absent rather than empty — which is why the structured record
# (§24) reads every one of the seven from this list.
EVIDENCE_SELECT = [
    "id", "content", "metadata", "case_id",
    "phase", "uploaded_at", "role", "kind",
    "description", "content_digest", "shape_match",
]

# §23.2: retrieval filters to evidence by default. An artefact is what the team
# DESIGNED, and one bucket would let a proposed future be retrieved later as a
# fact about the present (ruling AP2.3).
EVIDENCE_KIND_DEFAULT = "evidence"


@_single_flight
@lru_cache(maxsize=1)
@traceable(run_type="chain", name="retriever.get_evidence_vectorstore")
def get_evidence_vectorstore() -> AzureSearch:
    """Cached vectorstore for improve_evidence_index."""
    return AzureSearch(
        azure_search_endpoint=settings.AZURE_SEARCH_ENDPOINT,
        azure_search_key=settings.AZURE_SEARCH_API_KEY,
        index_name=settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX,
        embedding_function=get_embeddings(),
        search_type="hybrid",
        fields=EVIDENCE_INDEX_FIELDS,
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


def search_knowledge(query: str, phase: str | None = None,
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
        with trace("azure.search.knowledge.similarity_search", run_type="retriever",
                   inputs={"query": query[:200], "k": k, "filter": filters}) as span, _http_watch() as ev:
            docs = vs.similarity_search(query, k=k, filters=filters)
            # One shared, cached vectorstore: its embeddings call rides on
            # httpx (collected); its search on azure-core, which this call
            # path does not expose to a hook — the span's remainder is it.
            span.end(outputs={"hits": len(docs), **_http_summary(ev),
                              "client_id": id(vs)})
    except RETRIEVAL_EXCEPTIONS as e:
        _fail(e, settings.AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX,
              search="knowledge", filter=filters, query=query[:120])

    # ═══════════════════════════════════════════════════════════════════
    # THE KEYS BELOW ARE THE INDEX'S OWN, AND THREE OF THEM WERE WRONG
    # ═══════════════════════════════════════════════════════════════════
    # Until procedure step 5.2 this projection read `source`, `tool_name`,
    # `phase` and `section_title`. **`improve_knowledge_index` has none of
    # them.** Its live metadata keys are exactly:
    #
    #     char_count · id · page_number · phase_relevance · source_file
    #
    # so every one of those four fields came back as `""` on every result, on
    # every call, with no error — the `.get(key, "")` default is what made it
    # silent. Found by step 5.2's live-run, not by review.
    #
    # The cost was not cosmetic. §50 requires retrieval citations to surface
    # `source_file` and `page_number` — "this came from page 47 of the BB
    # eBook" — and `page_number` was not projected at all, so a checkable
    # citation was unbuildable from this return shape.
    #
    # `phase_relevance` is the filter field (§7.2, §24), NEVER `phase`: there
    # is no `phase` field on this index, which is the same confusion that
    # produced the original filter bug §27 exists to prevent.
    return [
        {
            # The index key field (§23), here for RRF: fusion dedups on it
            # (S-F17), and without it every variant's copy of the same chunk
            # counts as a distinct document, turning fusion into concatenation
            # with no error. LangChain's AzureSearch puts it in
            # `Document.metadata` — see `_result_to_document`.
            "id": d.metadata.get("id", ""),
            "content": d.page_content,
            "source_file": d.metadata.get("source_file", ""),
            "page_number": d.metadata.get("page_number"),
            "phase_relevance": d.metadata.get("phase_relevance", ""),
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
    search_client = get_search_client(settings.AZURE_SEARCH_IMPROVE_CASE_INDEX)

    try:
        with trace("azure.openai.embed_query", run_type="embedding",
                   inputs={"query": query[:200]}) as espan, _http_watch() as ev:
            embedder = get_embeddings()
            query_vector = embedder.embed_query(query)
            espan.end(outputs={**_http_summary(ev), "client_id": id(embedder)})
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=k,
            fields="embedding",
        )

        # The HTTP call is lazy — it fires on iteration, so the span wraps the
        # materialised list, and both stay inside the try so a failure is
        # still classified.
        with trace("azure.search.case.query", run_type="retriever",
                   inputs={"query": query[:200], "k": k}) as span, _http_watch() as ev:
            results = list(search_client.search(
                raw_response_hook=_azure_hook(ev),
                search_text=query,
                vector_queries=[vector_query],
                # `id` is selected for RRF dedup (S-F17) — a `select` that
                # omits it makes every document unique to fusion, silently.
                select=["id", "content_text", "case_id", "title",
                        "current_phase", "rag_status"],
                top=k,
            ))
            span.end(outputs={"hits": len(results), **_http_summary(ev),
                              "client_id": id(search_client)})

        return [
            {
                "id": r.get("id", ""),
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


def search_evidence(query: str, case_id: str, k: int = 4,
                    kind: str | None = EVIDENCE_KIND_DEFAULT) -> list[dict]:
    """Search improve_evidence_index filtered by case_id.
    Returns uploaded document extracts for this specific case only.

    **`kind` defaults to `evidence` and filtering it OFF is explicit** (§23.2,
    step 6.13). An artefact is what the team designed; returning one to an
    unfiltered evidence query lets a proposed future be read back as a fact
    about the present, which is ruling AP2.3's whole subject. Pass
    `kind=None` to search both — a deliberate, visible act at the call site.

    **The filter is safe only because the backfill ran first.** Against
    documents where `kind` is null it would match nothing, which is why
    6.13's sub-steps are ordered schema → write path → backfill → filters and
    why that order is load-bearing rather than tidy.

    Returns [] only when the search ran and matched nothing. Raises
    KnowledgeSearchError if the search itself fails."""
    search_client = get_search_client(settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX)
    safe_case_id = case_id.replace("'", "''")   # OData escapes ' by doubling
    odata = f"case_id eq '{safe_case_id}'"
    if kind:
        odata += f" and kind eq '{kind.replace(chr(39), chr(39) * 2)}'"

    try:
        with trace("azure.openai.embed_query", run_type="embedding",
                   inputs={"query": query[:200]}) as espan, _http_watch() as ev:
            embedder = get_embeddings()
            query_vector = embedder.embed_query(query)
            espan.end(outputs={**_http_summary(ev), "client_id": id(embedder)})
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=k,
            fields="content_vector",
        )

        # Iteration is what fires the HTTP call — the span wraps it, inside
        # the try.
        with trace("azure.search.evidence.query", run_type="retriever",
                   inputs={"query": query[:200], "k": k, "filter": odata}) as span, _http_watch() as ev:
            results = list(search_client.search(
                raw_response_hook=_azure_hook(ev),
                search_text=query,
                vector_queries=[vector_query],
                filter=odata,
                # `id` is selected for RRF dedup (S-F17), as above.
                select=EVIDENCE_SELECT,
                top=k,
            ))
            span.end(outputs={"hits": len(results), **_http_summary(ev),
                              "client_id": id(search_client)})

        output = []
        for r in results:
            output.append({
                "id": r.get("id", ""),
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
        # §24's structured record. Six come off the row as top-level fields
        # applied at 6.13; `blob_path` stays in the metadata blob, because
        # §23.2 deliberately does not index it — the index carries the
        # pointer's identity (`role`, `content_digest`), the blob carries the
        # data. A citation anchors on the pair (§23.2, §6).
        "role": row.get("role") or "",
        "kind": row.get("kind") or "",
        "description": row.get("description") or "",
        "phase": row.get("phase") or meta.get("upload_phase", ""),
        "uploaded_at": row.get("uploaded_at") or meta.get("timestamp", ""),
        "shape_match": row.get("shape_match") or "",
        "content_digest": row.get("content_digest") or "",
        "blob_path": meta.get("blob_path", ""),
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

    **Three outcomes, and they are three (§27), not two:** the formatted
    reference block when the search matched; `None` when the search ran and
    matched nothing; and an explicit *"lookup failed, this is not an absence"*
    block when retrieval broke. Collapsing the last two into `None` is what
    this function used to do, and it is the precise shape of the bug §27
    exists to prevent — the coach cannot tell a silent corpus from a broken
    one, so it reports the silence to the Belt as fact.

    The query is built from the user's latest message and, when
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
    except KnowledgeSearchError as e:
        # ═══════════════════════════════════════════════════════════════
        # §27 — A FAILURE MUST NOT REACH THE COACH AS AN ABSENCE
        # ═══════════════════════════════════════════════════════════════
        # This used to `return None`, which is **the same value this function
        # returns when nothing matched**. Coaching then continued with no
        # grounding and no way for the coach to know grounding had been
        # attempted and had broken — so the coach would answer as though the
        # methodology simply had nothing on the topic. That is §27's named
        # failure: *"the coach then told Belts the methodology had nothing on
        # their topic, which was false and unfalsifiable from the outside."*
        #
        # `knowledge/tools.py` already drew this distinction for the three
        # `@tool` entry points. This is the path the five orchestrators take on
        # **every turn**, and it did not.
        #
        # The block below is §27's prescribed wording. Coaching still
        # continues — a retrieval failure is a quality degradation, not an
        # availability failure (§4.8, Search breaker) — but it continues
        # *knowing*.
        logger.error(
            "build_knowledge_context failed | %s",
            e.error.to_step_log_entry(layer="retrieval", phase=phase),
        )
        rule = "═" * 43
        return (
            f"{rule}\nMETHODOLOGY LOOKUP FAILED — NOT AN ABSENCE\n{rule}\n\n"
            f"Methodology search is unavailable right now "
            f"({e.error.error_code}). This is a retrieval failure, not an "
            "absence of guidance — do not tell the team the methodology has "
            "nothing on this. Answer from your own DMAIC knowledge, say the "
            "reference lookup failed, and avoid citing sources you could not "
            "retrieve."
        )

    if not results:
        # Genuine no-match: the search ran and the corpus had nothing
        # relevant. Nothing to inject, and nothing to warn about.
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
