"""The three `rag_lookup_*` tools, plus the four unbound cross-agent tools.

Canonical: **§59.5 — S-F14** (`rag_lookup_methodology`), **§59.6 — S-F15**
(`rag_lookup_evidence`), **§59.7 — S-F16** (`rag_lookup_case_history`).
Architecture: **§24** (the three tools), **§25** (multi-query + RRF), **§23**
(index schemas), §27 (failure semantics), §29.4 (the cross-agent four).
Procedure step **5.2**.

THE THREE SUPERSEDED NAMES ARE GONE
-----------------------------------
The three `search_improve_{knowledge,cases,evidence}` tools are retired (§24)
and **no v2 code may reference them**. `grep-absence` targets those three
literal strings, which is why they are written in brace form here — a docstring
that spelled them out would make the check pass only by explanation.

**Only the tool layer is retired.** `knowledge/retriever.py`'s
`search_knowledge` / `search_cases` / `search_evidence` are what these tools
call and **keep their names**, along with §27's failure semantics. Do not
grep-absence those — §24 corrected itself on exactly this point on 2026-08-21,
after naming `search_evidence` as retired when §27 requires it to survive.

WHAT EACH TOOL DOES, AND WHERE THE COMPLEXITY LIVES
---------------------------------------------------
Every tool: generate 3–5 query variants, search the original **plus** each
variant, fuse with RRF at k=60, return the top slice. All of that is inside
`knowledge/fusion.py` and none of it is visible to the model, which sees a
clean `rag_lookup_*(query, ...)` signature (§25's encapsulation rule).

**`AzureSearch` with the filter at call time, never `AzureAISearchRetriever`**
(§24). The latter takes `filters` at *construction*, which would force
per-call instantiation once the filter carries a dynamic `phase` — and would
throw away the cached module-level singleton. This is a ratified rejection, not
an oversight: §24 records that the question was re-examined on 2026-08-21 and
no advantage was found.

`response_format="content_and_artifact"` on all three. The **content** is what
the model reads — formatted text carrying `source_file` and `page_number` so
citations are checkable (§50) — and the **artifact** is the `list[Document]`
S-F14/15/16 specify as the output, available programmatically for
`CoachingResponse.citations` at 6.2 without the model having to re-transcribe
it. One return, both readings satisfied.

WRITTEN AGAINST THE LIVE INDEX SCHEMA, NOT THE TARGET ONE
---------------------------------------------------------
Two ratified schema changes are **NOT YET APPLIED** in Azure (§23, blocked on
procedure step 9.1), and this file writes against what exists today:

  * **`rag_lookup_evidence` takes no `order_by` and applies no `phase`
    filter.** `improve_evidence_index` has neither `uploaded_at` nor `phase`
    as a top-level field yet — both live inside the non-sortable `metadata`
    JSON blob, which `$orderby` and `$filter` cannot reach. A tool cannot sort
    on a field the index does not have. §23 ratifies promoting both at reindex;
    the parameters arrive then, and **`phase` defaults OFF even after that** —
    a Control-phase Belt comparing against the Measure baseline is the normal
    case.
  * **`rag_lookup_case_history` uses `embedding`, not `content_vector`.**
    `improve_case_index` is the one index whose vector field is not
    `content_vector`; the rename is ratified and pending. Per-tool local
    knowledge of the field name is what makes that asymmetry safe (§23) — no
    shared code hides it, so nothing can fail silently on it.

**Never write code against the target schema before the reindex lands.**

FAILURE IS NEVER AN ABSENCE
---------------------------
Each tool catches `KnowledgeSearchError` and returns a message that says the
search FAILED, distinct from its empty-result message (§27). *"No cases found"*
when the search never ran is worse than an error, because the Belt acts on it.
"""
from __future__ import annotations

import logging

from langchain_core.documents import Document
from langchain_core.tools import tool

from backend.core.config import settings
from backend.core.errors import KnowledgeSearchError
from backend.knowledge.fusion import run_multi_query
from backend.knowledge.retriever import (
    get_knowledge_vectorstore,
    search_cases,
    search_evidence,
    search_knowledge,
)

logger = logging.getLogger(__name__)

#: §23.1 — the cross-phase value on `improve_knowledge_index` is `general`.
#: NEVER `all` (no document carries it, so the corpus silently narrows) and
#: NEVER a `phase` field (it does not exist, so Azure rejects the whole query).
#: Both were wrong in earlier revisions; one fails loudly and one does not.
CROSS_PHASE_RELEVANCE = "general"

#: §25 — the model asks for `top_k`; each variant fetches this many before
#: fusion. Fetching only `top_k` per variant would starve RRF of the
#: lower-ranked agreements that are the entire signal it reads.
PER_VARIANT_K = 10


def _as_documents(rows: list[dict], content_key: str = "content") -> list[Document]:
    """Retriever dicts -> `Document`s, for the tool's artifact half.

    S-F14/15/16 all specify `list[Document]` as the output. The retriever layer
    returns `list[dict]` (S-F18), so the conversion happens here — at the
    boundary the specs describe — rather than by changing a function §27 owns.
    """
    docs = []
    for row in rows:
        metadata = {k: v for k, v in row.items() if k != content_key}
        docs.append(Document(page_content=row.get(content_key, ""),
                             metadata=metadata))
    return docs


def _failure_message(kind: str, error_code: str, not_this: str) -> str:
    """§27's coach-facing wording: a failure must not read as an absence.

    `not_this` names the wrong conclusion explicitly, because that is the one
    the coach will otherwise reach and state to the Belt as fact.
    """
    return (
        f"{kind} search is unavailable right now ({error_code}). This is a "
        f"retrieval failure, not {not_this} — do not tell the team so, and do "
        f"not cite sources you could not retrieve."
    )


def _phase_filter(phase: str) -> str | None:
    """The §24 filter, or None for an unfiltered search.

    **The field is `phase_relevance`, and the cross-phase value is `general`.**
    Not `phase` — that field does not exist on this index and asking for it
    makes Azure reject the entire query. Not `all` — no document carries it, so
    the corpus silently narrows to the named phase alone. One of those two
    mistakes fails loudly and the other does not, which is why both are named
    here and in `retriever._phase_filter`.
    """
    if not phase:
        return None
    safe = phase.replace("'", "''")          # OData escapes ' by doubling it
    return (f"phase_relevance eq '{safe}' "
            f"or phase_relevance eq '{CROSS_PHASE_RELEVANCE}'")


def _citation_suffix(row: dict) -> str:
    """`source_file` and `page_number`, where the row carries them (§50).

    "This came from page 47 of the BB eBook" is what makes a citation
    checkable rather than decorative. **The label says PDF page** — WATCH 5:
    `page_number` is the PDF index and the printed number is piecewise-offset,
    so calling it "page" invites the Belt to look in the wrong place.
    """
    source = row.get("source_file")
    page = row.get("page_number")
    if source and page:
        return f" · {source}, PDF page {page}"
    if source:
        return f" · {source}"
    return ""



# ── Agent Improve indexes — the three ratified tools ────────────────


@tool(response_format="content_and_artifact")
async def rag_lookup_methodology(
    query: str, phase: str = "", top_k: int = 10
) -> tuple[str, list[Document]]:
    """Search Lean Six Sigma Black Belt methodology.

    Use this when you need the methodology itself — what a tool IS, how a
    technique works, what good looks like for a phase deliverable, or a worked
    example. This is the AUTHORITATIVE source in the memory hierarchy: when it
    disagrees with case history or with something said earlier in conversation,
    it wins.

    Source: improve_knowledge_index (the Black Belt eBook), filtered to the
    named phase plus cross-phase content. Vector field: content_vector.

    Args:
        query: What you need to know, in your own words.
        phase: define | measure | analyse | improve | control. Optional —
            omit to search the whole corpus unfiltered.
        top_k: How many passages to return. Default 10.
    """
    filters = _phase_filter(phase)

    def search(q: str) -> list[dict]:
        return search_knowledge(q, phase=phase or None, k=PER_VARIANT_K)

    try:
        rows = await run_multi_query(query, search, top_k)
    except KnowledgeSearchError as e:
        logger.error(
            "rag_lookup_methodology failed | %s",
            e.error.to_step_log_entry(tool="rag_lookup_methodology",
                                      phase=phase, filter=filters),
        )
        return (
            _failure_message("Methodology", e.error.error_code,
                             "an absence of guidance"),
            [],
        )

    if not rows:
        return ("No relevant methodology content found.", [])

    docs = _as_documents(rows)
    content = "\n\n".join(
        f"[{r.get('tool_name') or r.get('section_title') or 'Methodology'}"
        f"{_citation_suffix(r)}] {r.get('content', '')}"
        for r in rows
    )
    return (content, docs)


@tool(response_format="content_and_artifact")
async def rag_lookup_evidence(
    query: str, case_id: str, top_k: int = 10
) -> tuple[str, list[Document]]:
    """Search the documents THIS team uploaded for THIS project.

    Use this when the team has attached process maps, SIPOC diagrams,
    flipcharts, spreadsheets or reports and you need to reference what is
    actually in them — notably at step 3 of the seven-step computation pattern,
    when guiding data preparation.

    This is the only channel through which the team's own real-world data
    reaches you. Always scoped to one case; it never searches across cases.

    Source: improve_evidence_index, filtered by case_id.

    Args:
        query: What you are looking for in their uploads.
        case_id: The project identifier. Required.
        top_k: How many passages to return. Default 10.
    """
    if not case_id:
        return ("case_id is required for evidence search.", [])

    def search(q: str) -> list[dict]:
        return search_evidence(q, case_id=case_id, k=PER_VARIANT_K)

    try:
        rows = await run_multi_query(query, search, top_k)
    except KnowledgeSearchError as e:
        logger.error(
            "rag_lookup_evidence failed | %s",
            e.error.to_step_log_entry(tool="rag_lookup_evidence",
                                      case_id=case_id),
        )
        return (
            _failure_message("Evidence", e.error.error_code,
                             "an empty upload folder"),
            [],
        )

    if not rows:
        return ("No uploaded documents found for this case.", [])

    docs = _as_documents(rows)
    content = "\n\n".join(
        f"[Uploaded: {r.get('filename', 'document')}"
        f" · phase: {r.get('upload_phase', 'unknown')}] {r.get('content', '')}"
        for r in rows
    )
    return (content, docs)


@tool(response_format="content_and_artifact")
async def rag_lookup_case_history(
    query: str, top_k: int = 10, exclude_case_id: str = ""
) -> tuple[str, list[Document]]:
    """Search completed improvement projects from other teams — yokoten.

    Use this to show a team what worked elsewhere on a similar problem.

    CASE HISTORY IS PATTERNS, NOT PRESCRIPTIONS. Present it as "here is how
    another team approached this", never as methodology and never as what this
    team should do. A coach that presents precedent as instruction teaches the
    Belt to copy rather than to reason.

    Source: improve_case_index, completed cases.

    Args:
        query: The problem or approach you want precedent for.
        top_k: How many cases to return. Default 10.
        exclude_case_id: The current project's id, so a team is not shown its
            own case back. Optional.
    """
    def search(q: str) -> list[dict]:
        rows = search_cases(q, k=PER_VARIANT_K)
        if exclude_case_id:
            rows = [r for r in rows if r.get("case_id") != exclude_case_id]
        return rows

    try:
        rows = await run_multi_query(query, search, top_k)
    except KnowledgeSearchError as e:
        logger.error(
            "rag_lookup_case_history failed | %s",
            e.error.to_step_log_entry(tool="rag_lookup_case_history"),
        )
        return (
            _failure_message("Case history", e.error.error_code,
                             "an absence of precedent"),
            [],
        )

    if not rows:
        return ("No similar improvement cases found.", [])

    docs = _as_documents(rows)
    content = "\n\n".join(
        f"[Case {r.get('case_id', '?')}: {r.get('title', 'untitled')}"
        f" · {r.get('phase', 'unknown')} phase] {r.get('content', '')}"
        for r in rows
    )
    return (content, docs)


#: §29.2 — the retrieval third of the universal seven. The other four
#: (`propose_template`, `propose_diagram`, `check_gate_status`,
#: `request_human_approval`) land with the executor at stage 6.
RAG_LOOKUP_TOOLS = [
    rag_lookup_methodology,
    rag_lookup_evidence,
    rag_lookup_case_history,
]


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
