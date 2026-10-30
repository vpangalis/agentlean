"""The three `rag_lookup_*` tools, plus the four unbound cross-agent tools.

Also here: the two proposal tools (`propose_template`, `propose_diagram`), `load_evidence_series`, `read_upload`,
and `UNIVERSAL_TOOLS`, the list every phase's coach is given.

THE RETIRED TOOL NAMES
----------------------
The three `search_improve_{knowledge,cases,evidence}` tools are retired and
**no code may reference them**. `grep-absence` targets those three literal
strings, which is why they are written in brace form here — a docstring that
spelled them out would make the check pass only by explanation.

**Only the tool layer is retired.** `knowledge/retriever.py`'s
`search_knowledge` / `search_cases` / `search_evidence` are what these tools
call and **keep their names**, along with their failure semantics. Do not
grep-absence those.

WHAT EACH TOOL DOES, AND WHERE THE COMPLEXITY LIVES
---------------------------------------------------
Every `rag_lookup_*` tool: generate 3–5 query variants, search the original
**plus** each variant, fuse with RRF at k=60, return the top slice. All of
that is inside `knowledge/fusion.py` and none of it is visible to the model,
which sees a clean `rag_lookup_*(query, ...)` signature.

**`AzureSearch` with the filter at call time, never `AzureAISearchRetriever`.**
The latter takes `filters` at *construction*, which would force per-call
instantiation once the filter carries a dynamic `phase` — and would throw away
the cached module-level singleton. A rejected design, not an oversight.

`response_format="content_and_artifact"` on all three. The **content** is what
the model reads — formatted text carrying `source_file` and `page_number` so
citations are checkable — and the **artifact** is the `list[Document]`, which
`phases/nodes_common._attach_sources` turns into the reply's `citations`
without the model having to re-transcribe it. One return, both readings.

WRITTEN AGAINST THE LIVE INDEX SCHEMA, NOT THE TARGET ONE
---------------------------------------------------------
  * **`rag_lookup_evidence` takes no `order_by` — a design choice, not a
    schema constraint** (`uploaded_at` is a top-level, sortable field). The
    fusion is what keeps it out: retrieval is multi-query + RRF and this
    returns a fused rank, which an `$orderby` would discard in favour of
    recency — a different tool. Recency is answered by a FILTER on
    `uploaded_at`, never by sorting the fused set. It takes no `phase`
    either — a Control-phase Belt comparing against the Measure baseline is
    the normal case.
  * **`rag_lookup_case_history` searches `embedding`, not `content_vector`.**
    `improve_case_index` is the one index whose vector field is not
    `content_vector`; a rename is ratified and not yet applied in Azure. Each
    retriever function names its own vector field (`retriever.search_cases`),
    so no shared code hides the asymmetry and nothing can fail silently on it.

**Never write code against the target schema before the reindex lands.**

FAILURE IS NEVER AN ABSENCE
---------------------------
Each `rag_lookup_*` tool catches `KnowledgeSearchError` and returns a message
that says the search FAILED, distinct from its empty-result message. *"No cases found"*
when the search never ran is worse than an error, because the Belt acts on it.
"""
from __future__ import annotations

import logging
import re

from langchain_core.documents import Document
from langchain_core.tools import BaseTool, tool

from backend.core.config import settings
from backend.core.diagrams import BUILDERS, DIAGRAM_TYPES, DiagramError
from backend.core.errors import KnowledgeSearchError
from backend.knowledge.fusion import run_multi_query
from backend.knowledge.tool_args import (
    LoadEvidenceSeriesArgs,
    ProposeDiagramArgs,
    ProposeTemplateArgs,
    ReadSipocArgs,
    ReadUploadArgs,
)
from backend.knowledge.retriever import (
    get_knowledge_vectorstore,
    phase_filter,
    search_cases,
    search_evidence,
    search_knowledge,
)

logger = logging.getLogger(__name__)

#: The model asks for `top_k`; each variant fetches this many before
#: fusion. Fetching only `top_k` per variant would starve RRF of the
#: lower-ranked agreements that are the entire signal it reads.
PER_VARIANT_K = 10


def _as_documents(rows: list[dict], content_key: str = "content") -> list[Document]:
    """Retriever dicts -> `Document`s, for the tool's artifact half.

    The tools return `list[Document]` as their artifact; the retriever layer
    returns `list[dict]`, so the conversion happens here, at the tool
    boundary, rather than in the retriever.
    """
    docs = []
    for row in rows:
        metadata = {k: v for k, v in row.items() if k != content_key}
        docs.append(Document(page_content=row.get(content_key, ""),
                             metadata=metadata))
    return docs


def _failure_message(kind: str, error_code: str, not_this: str) -> str:
    """The coach-facing wording of a failed search: a failure must not read as an absence.

    `not_this` names the wrong conclusion explicitly, because that is the one
    the coach will otherwise reach and state to the Belt as fact.
    """
    return (
        f"{kind} search is unavailable right now ({error_code}). This is a "
        f"retrieval failure, not {not_this} — do not tell the team so, and do "
        f"not cite sources you could not retrieve."
    )


def _citation_suffix(row: dict) -> str:
    """`source_file` and `page_number`, where the row carries them.

    "This came from page 47 of the BB eBook" is what makes a citation
    checkable rather than decorative. **The label says PDF page**:
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
    filters = phase_filter(phase)

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


def _evidence_record(row: dict) -> str:
    """One structured evidence record — attributes as VALUES, then the excerpt.

    The shape, line by line: role · kind · phase, then description, then
    uploaded_at · shape_match, then blob_path · content_digest, then filename,
    then the excerpt.

    **Two reasons it is not rendered prose**, each sufficient. The coach has
    to CHOOSE a file — *"which of these three is the current cycle-time
    data"* is a question about `role`, `uploaded_at` and `shape_match`, not
    about similarity, and prose forces the model to re-derive from sentences
    what the index already holds as values. And citations are built from
    source, page and summary: a coach can only cite accurately what it
    received as values, so returning prose and asking for the citation back
    is a transcription the model should never be asked to make.

    **`blob_path` and `content_digest` anchor a citation to the exact file**,
    so a check can tell that an approved gate rested on a file that has since
    been replaced. A record omitting them would leave nothing to compare.

    An empty value is rendered as `unknown` rather than omitted: a missing
    line reads as "this file has no role", and it means "this index document
    predates the field".
    """
    def v(key: str) -> str:
        return (row.get(key) or "").strip() or "unknown"

    return (
        f"role: {v('role')} · kind: {v('kind')} · phase: {v('phase')}\n"
        f"description: {v('description')}\n"
        f"uploaded_at: {v('uploaded_at')} · shape_match: {v('shape_match')}\n"
        f"blob_path: {v('blob_path')} · content_digest: {v('content_digest')}\n"
        f"filename: {v('filename')}\n"
        f"excerpt: {(row.get('content') or '').strip()}"
    )


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
    return ("\n\n".join(_evidence_record(r) for r in rows), docs)


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

    Source: improve_case_index, filtered to completed cases only (`status eq 'completed'`,
    DEF-165); no other filter.

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


#: The three retrieval tools; they lead `UNIVERSAL_TOOLS` below.
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


# ══════════════════════════════════════════════════════════════════════════
# The two universal proposal tools
#
# WHAT THEY ARE: Agent Improve does not export documents; the assembled
# {Phase}Output shown on the UI is the record. `propose_diagram` returns
# structured JSON the UI renders (renderSipocDiagram, render5W2HMindmap).
# `propose_template` returns a str the coach presents inside its coaching
# message for the Belt to complete — no UI renderer, by design. Neither emits a
# file; both are coaching aids, not document generators. A change that makes
# one emit a file, or routes the template through a renderer, is outside what
# they are for.
#
# G-29 (template types and `fill_data` schemas) and G-30 (the diagram
# catalogue) are open and founder-owned. What is built is the minimum the coach
# needs: the four template types below and the diagram types `ui/index.html`
# draws. Adding a type is a founder decision plus a renderer, not an entry
# added here.
# ══════════════════════════════════════════════════════════════════════════

#: The four scaffolds `propose_template` offers. The list is open under G-29,
#: so it is not extended here.
TEMPLATE_TYPES: tuple[str, ...] = (
    "problem_statement", "sipoc", "data_collection_plan", "fishbone",
)

#: G-258: Define's two scaffolds are built from the Define script and the schema's keys — the questions
#: and columns the element is graded on — never typed here.
_FROM_THE_SCRIPT = ("problem_statement", "sipoc")
#: A SIPOC column's label where it is not its key with the underscore dropped.
_SIPOC_LABELS = {"process_steps": "Process steps", "process_metrics": "Measures"}
_PAGE = re.compile(r"\s*\(p\.[^)]*\)|\s*\(R\d+\)")


def _scaffold(template_type: str) -> str:
    """G-258: the problem statement as the script's 5W2H table (each question with how it is formulated), the
    SIPOC as the schema's six columns with the script's step count and how each part is formulated."""
    from backend.middleware.skills import element_text, show_table
    from backend.phases.define import criteria as define_criteria
    from backend.phases.define.schema import FIVE_W_TWO_H_KEYS, SIPOC_KEYS
    if template_type == "problem_statement":
        crit = dict(define_criteria.criteria("problem_statement"))
        keys = {k.replace("_", " "): k for k in FIVE_W_TWO_H_KEYS}
        lines = [f"  {row[0]} — {row[1]}: {{{keys[row[0].lower()]}}}" for row in show_table("define", "problem_statement")
                 if len(row) > 1 and row[0].lower() in keys]
        return ("PROBLEM STATEMENT — the seven 5W2H answers, then one statement composed from them.\n\n"
                + "\n".join(lines) + "\n\nIt "
                + _PAGE.sub("", crit.get(define_criteria.NO_CAUSE_NO_FIX, "")).strip() + ".")
    crit = dict(define_criteria.criteria("process_map_sipoc"))
    columns = "\n".join(f"  {_SIPOC_LABELS.get(k, k.capitalize())}: {{{k}}}" for k in SIPOC_KEYS)
    how = next((ln.split(":", 1)[1].strip() for ln in element_text("define", "process_map_sipoc", "Show").splitlines()
                if ln.startswith("How each part is formulated")), "")
    return (f"SIPOC — {_PAGE.sub('', crit.get(define_criteria.START_TO_END, '')).strip()}; "
            f"{_PAGE.sub('', crit.get(define_criteria.ALL_SIX, '')).strip()}.\n\n{columns}\n\n"
            f"How each part is formulated: {how}")


_TEMPLATES: dict[str, str] = {
    "data_collection_plan": (
        "DATA COLLECTION PLAN\n\n"
        "  What we measure:          {metric}\n"
        "  Operational definition:   {definition}\n"
        "  Where the data comes from:{source}\n"
        "  Who collects it:          {owner}\n"
        "  How often:                {frequency}\n"
        "  Sample size:              {sample_size}\n"
        "  How it is recorded:       {recording}\n\n"
        "The operational definition is the line that matters: two people "
        "measuring the same thing must get the same number."
    ),
    "fishbone": (
        "FISHBONE — causes grouped by category, for: {effect}\n\n"
        "  People:       {people}\n"
        "  Process:      {process}\n"
        "  Equipment:    {equipment}\n"
        "  Materials:    {materials}\n"
        "  Environment:  {environment}\n"
        "  Measurement:  {measurement}\n\n"
        "These are candidate causes, not validated ones. Analyse is where "
        "they get tested."
    ),
}


class _Blank(dict):
    """`format_map` helper — an unfilled slot renders as a blank to complete."""

    def __missing__(self, key: str) -> str:  # noqa: D105
        return "________"


@tool(args_schema=ProposeTemplateArgs)
def propose_template(template_type: str, fill_data: dict) -> str:
    """Produce a fill-in scaffold the team completes — show before asking.

    Use it when the Belt needs to see the SHAPE of a good answer before
    producing theirs (§43.2): a completed example first, then an invitation to
    build their own. Anything already known goes in `fill_data` and appears
    pre-filled; everything else renders as a blank for the Belt to complete.

    Supported `template_type`: problem_statement, sipoc, data_collection_plan,
    fishbone. It returns text for the Belt, not a captured value — nothing here
    reaches `artifacts` unless the Belt states it back.

    **Present the returned text inside your own coaching message.** There is no
    UI renderer for a template and that is by design (founder ruling
    2026-09-03): unlike `propose_diagram`, this is prose the coach shows, not a
    payload the app draws. It is a coaching aid — it emits no file, and Agent
    Improve exports no documents.
    """
    if template_type not in _TEMPLATES and template_type not in _FROM_THE_SCRIPT:
        return (
            f"I do not have a {template_type!r} template. The ones I can offer "
            f"are: {', '.join(TEMPLATE_TYPES)}."
        )
    values = _Blank({k: str(v) for k, v in (fill_data or {}).items() if v})
    text = _scaffold(template_type) if template_type in _FROM_THE_SCRIPT else _TEMPLATES[template_type]
    return text.format_map(values)


@tool(args_schema=ProposeDiagramArgs, response_format="content_and_artifact")
def propose_diagram(diagram_type: str, data: dict) -> tuple[str, dict]:
    """Produce structured diagram data for the app to draw — never markup.

    **B1: this returns JSON, never SVG.** You describe what to draw; the
    frontend owns how it looks. Emitting markup here produces something that
    drifts from the design system and cannot be restyled.

    Use it at the "visualise" step of the seven-step computation pattern
    (§43.1), and whenever a picture carries the point better than prose.
    Supported `diagram_type`: 'sipoc' and 'mindmap_5w2h' — those are the two
    the app can currently render, and an unsupported type comes back as a plain
    message rather than a drawing nobody sees.
    """
    builder = BUILDERS.get(diagram_type)
    if builder is None:
        return (
            f"I cannot draw a {diagram_type!r}. I can draw: "
            f"{', '.join(DIAGRAM_TYPES)}.",
            {},
        )
    try:
        payload = builder(dict(data or {}))
    except DiagramError as e:
        return (str(e), {})
    # `content_and_artifact`: the model reads the confirmation, the executor
    # node lifts the ARTIFACT onto the reply's `additional_kwargs` for the UI.
    # Returning the dict as content would hand the model a payload to
    # re-transcribe and the executor a string to parse back.
    return (
        f"Diagram ready: a {diagram_type} the app will render for the Belt.",
        {"diagram_type": diagram_type, **payload},
    )


@tool(args_schema=LoadEvidenceSeriesArgs, response_format="content_and_artifact")
async def load_evidence_series(
    blob_path: str, column: str
) -> tuple[str, dict]:
    """Load one column of numbers from a file the Belt uploaded.

    USE THIS WHENEVER YOU NEED THE ACTUAL VALUES from an upload — before any
    calculation, and instead of reading numbers out of retrieved text. Search
    finds WHICH file; this loads THE VALUES.

    Returns the column's values with n, mean, sigma, min and max, ready to hand
    to a calculation tool. **Never retype a figure you have seen in a chunk or
    in your own earlier message** — load it.

    `blob_path` comes from the uploads manifest at the top of your context, or
    from a `rag_lookup_evidence` result. If the column name is wrong, the reply
    lists the columns the file actually has, so ask the Belt using those names.
    """
    from backend.storage import blob as blob_store
    from backend.upload.parsers import parse_upload

    filename = (blob_path or "").rsplit("/", 1)[-1]
    try:
        raw = await blob_store.download_bytes(blob_path)
    except Exception as exc:  # noqa: BLE001 — a missing file is a coaching fact
        logger.warning("load_evidence_series: cannot read %s: %s",
                       blob_path, exc)
        return (
            f"That file could not be opened ({filename}). Ask the Belt to "
            f"upload it again, or pick a different file from the list you "
            f"were shown.",
            {"ok": False, "reason": "unreadable"},
        )

    # RE-PARSE. No stored copy of the values is read or created:
    # `UploadRecord.rows` is a row count, and a second copy of the table could
    # drift from the file, which is the one authority.
    parsed = parse_upload(filename, raw, _content_type_for(filename))
    if not parsed.get("parsed"):
        return (
            f"That file could not be read: {parsed.get('refusal_reason')}",
            {"ok": False, "reason": "unparseable"},
        )

    columns = parsed.get("columns") or []
    match = _match_column(column, columns)
    if match is None:
        # A Belt-readable reformatting request naming what IS there,
        # never a bare failure.
        listed = ", ".join(columns) if columns else "none"
        return (
            f"'{column}' is not a column in {filename}. The columns it has "
            f"are: {listed}. Ask the Belt which of those holds the value you "
            f"need, using their own column names.",
            {"ok": False, "reason": "no_such_column", "columns": columns},
        )

    profile = (parsed.get("column_ranges") or {}).get(match) or {}
    kind = (parsed.get("column_types") or {}).get(match, "text")
    values = _column_values(parsed, match)

    if kind not in ("whole number", "decimal", "percentage"):
        return (
            f"'{match}' in {filename} holds {kind}, not numbers, so it cannot "
            f"be measured. The file's numeric columns are: "
            f"{', '.join(_numeric_columns(parsed)) or 'none'}.",
            {"ok": False, "reason": "not_numeric", "column_type": kind},
        )

    n = len(values)
    mean = sum(values) / n if n else 0.0
    sigma = (sum((v - mean) ** 2 for v in values) / (n - 1)) ** 0.5 if n > 1 else 0.0

    # A mixed column carries the parse's own report rather than being
    # silently coerced. A mixed column is a coaching question.
    mixed = profile.get("mixed")
    mixed_note = (
        f" NOTE: {sum(mixed.values())} of {n + sum(mixed.values())} rows in "
        f"this column are not numbers ({', '.join(mixed)}); they were left "
        f"out. Ask the Belt whether that is expected before relying on these "
        f"figures." if mixed else ""
    )

    # STRINGS, so the computation tools consume them unchanged.
    summary = {
        "column": match, "n": str(n), "mean": f"{mean:.4f}",
        "sigma": f"{sigma:.4f}",
        "min": str(profile.get("min", "")), "max": str(profile.get("max", "")),
        "unit_note": "unit is whatever the Belt declared in metric_definitions",
    }
    logger.info("load_evidence_series: %s[%s] n=%d", filename, match, n)
    return (
        f"{filename} · column '{match}': n={n}, mean={mean:.4f}, "
        f"sigma={sigma:.4f}, min={profile.get('min')}, "
        f"max={profile.get('max')}.{mixed_note}",
        {"ok": True, "blob_path": blob_path, **summary,
         "values": [str(v) for v in values]},
    )


#: ADR-0106 decision 3: how much of a file read_upload returns — enough to quote from, never a whole archive.
READ_UPLOAD_MAX_CHARS = 12000


@tool(args_schema=ReadUploadArgs, response_format="content_and_artifact")
async def read_upload(blob_path: str) -> tuple[str, dict]:
    """Read the text of ONE file the team uploaded to THIS project, to quote from it.

    USE THIS when you need what a specific upload actually says — a line of a process map, a passage of a plan or a
    report — and quote it. It reads uploads labelled EVIDENCE (what is) and ARTEFACT (what the team designed, e.g. a
    to-be process map); the label comes back with the text, so never present an artefact as a fact about today.
    Search (`rag_lookup_evidence`) finds evidence by meaning; this reads one named file.

    `blob_path` comes from the uploads manifest at the top of your context. Only this project's files are readable.
    Long files are cut to the first part; the reply says so.
    """
    from backend.core.request_context import get_case_id
    from backend.storage import blob as blob_store
    from backend.storage import layout
    from backend.upload import classifier
    from backend.upload.parsers import parse_upload

    case_id = get_case_id() or ""
    prefix = layout.UPLOAD_BLOB.format(case_id=case_id, filename="")
    if not case_id or not (blob_path or "").startswith(prefix):
        logger.warning("read_upload: refused %s — not a file of the current case %s", blob_path, case_id)
        return ("That file is not one of this project's uploads. Pick one from the uploads list you were shown.",
                {"ok": False, "reason": "not this case"})
    filename = blob_path.rsplit("/", 1)[-1]
    try:
        raw = await blob_store.download_bytes(blob_path)
    except Exception as exc:  # noqa: BLE001 — a missing file is a coaching fact
        logger.warning("read_upload: cannot read %s: %s", blob_path, exc)
        return (f"That file could not be opened ({filename}). Ask the Belt to upload it again.",
                {"ok": False, "reason": "unreadable"})
    parsed = parse_upload(filename, raw, _content_type_for(filename))
    if not parsed.get("parsed"):
        return (f"That file could not be read: {parsed.get('refusal_reason')}", {"ok": False, "reason": "unparseable"})
    case = await blob_store.load_case(case_id)
    record = next((u for ph in (case.phases.values() if case else []) for u in (ph.uploads or [])
                   if u.blob_path == blob_path), None)
    kind = str(getattr(record, "kind", "") or classifier.EVIDENCE)
    body = str(parsed.get("text") or "")
    truncated = len(body) > READ_UPLOAD_MAX_CHARS
    shown = body[:READ_UPLOAD_MAX_CHARS]
    head = (f"file: {filename} · kind: {kind}" + (" (what the team designed — not a fact about today)"
                                                  if kind == classifier.ARTEFACT else "")
            + (f" · the first {READ_UPLOAD_MAX_CHARS} characters of {len(body)}" if truncated else ""))
    return (head + chr(10) + shown, {"ok": True, "filename": filename, "blob_path": blob_path, "kind": kind,
                                   "truncated": truncated, "chars": len(body)})


@tool(args_schema=ReadSipocArgs, response_format="content_and_artifact")
async def read_sipoc(description: str) -> tuple[str, dict]:
    """Read the Belt's process into the SIPOC (suppliers, inputs, steps, outputs, customers, measures).

    USE THIS when the Belt describes their process, or answers a part of it that was missing: pass what they gave, in
    their own words. It returns the SIPOC as read so far and the parts still missing. Read back what it returns, as it
    is, and ask only the missing parts. Nothing is stored until the Belt confirms.
    """
    from backend.knowledge import sipoc
    return await sipoc.coach_reading(description)


#: R10 (ADR-0095 decision 4): Define's own tool — registered on Define's executor, offered at element 12 only.
DEFINE_TOOLS: list[BaseTool] = [read_sipoc]


def _content_type_for(filename: str) -> str:
    """The parser bucket for a filename, without a mime type to go on."""
    from backend.upload.classifier import classify_content_type
    return classify_content_type(filename, "")


def _match_column(wanted: str, columns: list[str]) -> str | None:
    """A column name, matched leniently — a Belt's header is not a label."""
    want = (wanted or "").strip().lower().replace("_", " ")
    for c in columns:
        if c.strip().lower().replace("_", " ") == want:
            return c
    for c in columns:
        norm = c.strip().lower().replace("_", " ")
        if want and (want in norm or norm in want):
            return c
    return None


def _numeric_columns(parsed: dict) -> list[str]:
    return [c for c, t in (parsed.get("column_types") or {}).items()
            if t in ("whole number", "decimal", "percentage")]


async def first_numeric_column(blob_path: str) -> str | None:
    """The file's first numeric column, read from its own header — G-63.

    **The second source for a routed read's column.** The first is the ask
    that solicited the upload; this one exists because
    `SHAPES_BY_PHASE["define"]` is empty, so in Define no ask declares
    columns and the node would otherwise have nothing to name.

    **It lives HERE rather than in the node.** The download, the parse, the
    column vocabulary and `_numeric_columns` are already this module's. A
    second parse site in `nodes_common` would be a second answer to *"what
    columns does this file have"* — the same reason `_match_column` is not
    reimplemented at the call site.

    **NUMERIC, not merely first.** `load_evidence_series` returns a SERIES
    with n, mean and sigma, so a date or a free-text `reason` column satisfies
    the letter of *"a column the file has"* and none of its purpose. In a file
    of `date, complaints, reason` the first column is a date and the only
    useful answer is `complaints`.

    Returns `None` when the file cannot be read, cannot be parsed, or carries
    no numeric column at all. **`None` is a caller's signal not to dispatch,
    never a failure**: a file with nothing to read is a coaching fact, never a
    hard failure for the Belt.
    """
    from backend.storage import blob as blob_store
    from backend.upload.parsers import parse_upload

    filename = (blob_path or "").rsplit("/", 1)[-1]
    try:
        raw = await blob_store.download_bytes(blob_path)
        parsed = parse_upload(filename, raw, _content_type_for(filename))
    except Exception as exc:  # noqa: BLE001 — a header read is best-effort
        logger.warning(
            "first_numeric_column: cannot read %s (%s) — the caller declines "
            "the routed read rather than naming a column blindly",
            blob_path, exc,
        )
        return None

    if not parsed.get("parsed"):
        logger.info("first_numeric_column: %s did not parse (%s)",
                    filename, parsed.get("refusal_reason"))
        return None

    numeric = _numeric_columns(parsed)
    if not numeric:
        logger.info(
            "first_numeric_column: %s has no numeric column (columns: %s)",
            filename, ", ".join(parsed.get("columns") or []) or "none",
        )
        return None
    return numeric[0]


def _column_values(parsed: dict, column: str) -> list[float]:
    """The column's numeric values, re-derived from the parsed text.

    The parser keeps `column: value` lines rather than a table, so the values
    are read back from there — still one parse, still no stored copy.
    """
    out: list[float] = []
    for line in (parsed.get("text") or "").splitlines()[1:]:
        for cell in line.split(" | "):
            name, _, value = cell.partition(": ")
            if name.strip() == column:
                try:
                    out.append(float(value.strip().rstrip("%")))
                except ValueError:
                    pass
    return out


#: Bound to every phase's coach, with the phase's computation tools, via `tools=` on `create_agent`
#: (`nodes_common`); `turn_tools` offers a subset per turn. The ratified total also counts `check_gate_status` and
#: `request_human_approval`, which are not built; `test_computation.py` asserts both counts.
UNIVERSAL_TOOLS: list[BaseTool] = [
    *RAG_LOOKUP_TOOLS,
    propose_template,
    propose_diagram,
    load_evidence_series,
    read_upload,                # ADR-0106: the ninth universal tool (offered on teaching and upload turns only)
]
