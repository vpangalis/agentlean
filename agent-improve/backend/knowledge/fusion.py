"""Multi-query fusion — Reciprocal Rank Fusion and the variant schema.

Canonical: **§59.8 — S-F17** (`reciprocal_rank_fusion`, *rebuild test: met*) and
**§59.4 — S-C19** (`QueryVariants`). Architecture: **§25** (multi-query + RRF),
§21 (structured output), §24 (the three tools). Procedure step 5.2.

WHY THIS IS CUSTOM CODE AND NOT A LANGCHAIN CLASS
-------------------------------------------------
**`MultiQueryRetriever` and `EnsembleRetriever` are BANNED** (§25), for two
independent reasons either of which would settle it:

  1. Both moved to `langchain_classic` in the LangChain 1.0 namespace split and
     are not importable from `langchain` in the pinned version;
  2. **`EnsembleRetriever` would be the wrong class even if it were
     importable.** It fuses results from *different retriever sources* — BM25
     plus vector, say. Ours is **same-index multi-query**: N phrasings against
     one index. No standard LangChain 1.x class covers that pattern, which is
     why the LangChain rag-fusion template is itself a custom implementation.

So this is ~15 lines, no LangChain class, no third-party dependency, stable
across framework versions. **That is a deliberate property, not an accident**
(S-F17 invariants).

WHY MULTI-QUERY AT ALL, GIVEN AZURE ALREADY DOES HYBRID SEARCH
--------------------------------------------------------------
The gap is not "missing BM25" — Azure AI Search already runs BM25 keyword
matching alongside vector similarity. **The gap is sending one query
formulation to an already-good hybrid retriever**, which misses concepts the
Belt did not explicitly name.

RRF operationalises **cross-variant consistency**: a document ranked well by
several different phrasings is more likely relevant than one ranked well by a
single phrasing. Native single-query ranking cannot do this, **because it does
not know the other variants exist**. Agent Resolve production experience
settled it — with a single query, ranking was not reliably returning the right
matches for this corpus — and an earlier "diminishing returns, defer it"
position was overridden by that evidence (§25).

ENCAPSULATION
-------------
Variant generation and fusion happen **inside** the tool. The model sees a
clean `rag_lookup_*(query, ...)` interface and never manages either (§25).
Complexity belongs inside the tool, not exposed to the model.
"""
from __future__ import annotations

import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Hashable,
    Iterable,
    Sequence,
    TypeVar,
)

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

#: §25, S-F17 B1. Not a tuning knob: 60 is the constant from the original RRF
#: paper and the value comparable implementations use, so changing it would
#: make our fused rankings incomparable with anyone else's.
RRF_K = 60

#: §25 — "3–5 query variants". Enforced by the schema below rather than by a
#: prompt instruction alone, so a model that returns two or seven fails at
#: parse time instead of silently narrowing or widening the fan-out.
MIN_VARIANTS = 3
MAX_VARIANTS = 5

T = TypeVar("T")


class QueryVariants(BaseModel):
    """The structured output of the variant-generation call (S-C19).

    ═══════════════════════════════════════════════════════════════════════
    THIS SCHEMA RESOLVES SPEC-GAP G-14 — Group C, "named but never defined"
    ═══════════════════════════════════════════════════════════════════════
    §21's mapping table and §25 both name `QueryVariants`; neither defines it.
    G-14 lists exactly three undecided points, each ruled here with its
    reasoning so the next reader inherits a decision rather than the gap.

    **1. Field names — one field, `variants: list[str]`.**
    There is nothing else the call produces. A `rationale` or `strategy` field
    was considered and rejected: it would be generated on every retrieval, read
    by nothing, and paid for in tokens on the hot path.

    **2. Is the original query among the variants? NO — and it is always
    searched anyway.**
    This is the substantive ruling. The Belt's own phrasing is the
    highest-signal formulation in the set, and it must not be at the mercy of a
    generation call: a model that paraphrases badly, or returns variants that
    all drift the same way, would lose it entirely. So `run_multi_query` runs
    the original **as its own ranked list, unconditionally**, and the model's
    job is purely to add *alternative* phrasings. Putting the original in the
    schema would also let the model spend one of its three-to-five slots
    restating what it was given.

    **Consequence worth naming:** the fan-out is `1 + len(variants)`, so 4–6
    ranked lists reach RRF, not 3–5. The original's list is one vote among
    them — deliberately not weighted higher, because RRF's whole premise is
    that agreement across phrasings is the signal.

    **3. Fixed or model-chosen count? Model-chosen, bounded at 3–5, enforced
    by the schema.**
    §25 says "3–5", which is a range and not a number. Some queries have three
    natural rephrasings and some have five; forcing exactly five produces
    padding, and padding produces near-duplicate lists that inflate one
    document's fused score without adding evidence. The bounds are
    `min_length` / `max_length` on the field, so a violation is a parse failure
    at the boundary rather than a silent narrowing deeper in.

    **Not ratified.** G-14 is a **Group C** gap — a schema named but never
    defined — not a Group A founder ruling, so it is resolvable here under
    CONTINUITY's Standing Reasoning Protocol. If the founder rules differently,
    the schema is one edit and variant generation is its only consumer.
    """

    variants: list[str] = Field(
        min_length=MIN_VARIANTS,
        max_length=MAX_VARIANTS,
        description=(
            "Between 3 and 5 alternative phrasings of the user's question, "
            "each rewritten to surface documents the original wording might "
            "miss. Do NOT repeat the original question — it is searched "
            "separately. Vary the vocabulary: use the formal methodology term "
            "where the user used plain language, and plain language where the "
            "user used jargon."
        ),
    )


def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[T]],
    k: int = RRF_K,
    key: Callable[[T], Hashable] | None = None,
) -> list[tuple[T, float]]:
    """Fuse several ranked lists into one ordering. **S-F17, verbatim in shape.**

    Each document scores `1 / (k + rank)` in every list it appears in, and the
    scores sum across lists (B2). A document ranked 3rd by four different
    phrasings therefore beats one ranked 1st by a single phrasing — which is
    the cross-variant consistency the whole mechanism exists to capture.

    `k=60` (B1) damps the difference between adjacent ranks: with a small k,
    rank 0 would dominate rank 1 so heavily that fusion degenerates into
    "whatever the first list ranked first". It is the constant from the
    original RRF paper and is not a tuning knob.

    **`key` is the one departure from S-F17's literal definition, and it is a
    type accommodation rather than a design change.** The spec reads
    `doc.metadata["id"]`, written for `Document` objects; `knowledge/
    retriever.py` returns `list[dict]` (§27, S-F18), so identity is a per-index
    question the caller answers. The default handles both shapes.

    Returns `list[tuple[T, float]]`, highest fused score first. **Ties keep the
    order of first appearance** — Python's sort is stable and insertion order
    follows the first list's ranking, so a tie resolves toward the earliest
    variant, which `run_multi_query` makes the Belt's original query.
    """
    identity = key or _default_key
    scores: dict[Hashable, float] = {}
    docs: dict[Hashable, T] = {}

    for ranked in ranked_lists:
        for rank, doc in enumerate(ranked):
            doc_id = identity(doc)
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            docs[doc_id] = doc

    return sorted(
        ((docs[i], s) for i, s in scores.items()),
        key=lambda pair: pair[1],
        reverse=True,
    )


def _default_key(doc: Any) -> Hashable:
    """Identity for fusion: the index `id` where there is one, else the content.

    Every `improve_*` index has an `id` key field (§23), so the first branch is
    the normal path. The content fallback exists for the raw-`SearchClient`
    paths, whose `select=` lists must ask for `id` explicitly — a `select` that
    forgot it would otherwise make every document unique and turn fusion into
    concatenation, **silently**. Falling back on content keeps dedup correct in
    that case; `test_fusion.py` pins both branches.
    """
    if isinstance(doc, dict):
        return doc.get("id") or doc.get("content", "")
    metadata = getattr(doc, "metadata", None)
    if isinstance(metadata, dict) and metadata.get("id"):
        return metadata["id"]
    return getattr(doc, "page_content", repr(doc))


async def generate_variants(query: str) -> list[str]:
    """Ask the model for 3–5 alternative phrasings. Structured output, never JSON.

    §25: *"Variant generation uses structured output (`QueryVariants`, §21),
    never manual JSON parsing."* §4.3 is the prohibition and §4.6 the mechanism:
    this is a **plain model call inside a tool**, not an agent, so it takes the
    builder-style structured-output call rather than `response_format=`. §4.6's
    mapping table names this exact site.

    **Role `extraction`, temperature 0.2.** No new role is introduced — §4.2
    requires a §56 amendment for that — and `extraction` is the right existing
    one: `operational-model` (gpt-4o-mini), roughly 15× cheaper than the premium
    tier for what is a mechanical rewriting task on the hot path (§4.2's
    tiering rule).

    **Low temperature is deliberate, and is not in tension with wanting diverse
    variants.** The diversity is carried by the prompt, which asks for
    alternative vocabulary explicitly; the sampler's job here is
    reproducibility — the same Belt question should retrieve the same documents
    twice, or a LangSmith trace cannot be read against a rerun. 0.2 sits inside
    §4.7's 0.0–0.2 band for extraction-class calls.

    **Failure returns `[]` rather than raising**, and that is safe here in a way
    it would never be in `retriever.py`: the caller searches the original query
    regardless, so a failed variant call degrades multi-query to single-query —
    measurably worse retrieval, but still retrieval, and still a real search.
    §27's rule is about a *search* failure masquerading as an empty corpus; this
    is a *generation* failure with a working fallback, and it is logged as one
    at `warning` because a persistent one is a quality regression.
    """
    from backend.core.llm import get_llm
    from backend.core.prompts import VARIANT_PROMPT

    try:
        llm = get_llm("extraction", temperature=0.2)
        structured = llm.with_structured_output(QueryVariants)
        result = await structured.ainvoke(VARIANT_PROMPT.format(
            query=query,
            min_variants=MIN_VARIANTS,
            max_variants=MAX_VARIANTS,
        ))
        variants = list(getattr(result, "variants", []) or [])
    except Exception as e:
        logger.warning(
            "Query variant generation failed, using the original only: %s", e
        )
        return []

    cleaned = [v.strip() for v in variants if v and v.strip()]
    logger.info("Generated %d query variant(s)", len(cleaned))
    return cleaned


async def run_multi_query(
    query: str,
    search: Callable[[str], Iterable[T]],
    top_k: int,
    make_variants: Callable[[str], Awaitable[list[str]]] = generate_variants,
    key: Callable[[T], Hashable] | None = None,
) -> list[T]:
    """The whole §25 mechanism: original + variants, searched, fused, sliced.

    `search` is a one-argument callable so each tool binds its own index, filter
    and vector field before handing it over — fusion never learns which index it
    is fusing.

    ═══════════════════════════════════════════════════════════════════════
    `make_variants` IS INJECTED BECAUSE ITS ONLY IMPLEMENTATION IS BLOCKED
    ═══════════════════════════════════════════════════════════════════════
    §25 requires variant generation to use **structured output**
    (`QueryVariants`), never manual JSON parsing, and §4.6's mapping table names
    the mechanism explicitly: *"Inside `rag_lookup_*` | Plain LLM call |
    `QueryVariants` | `with_structured_output`"*. **The drift registry blocks
    that call in this file** — `pattern-2-with-structured-output`'s
    `path_exclusions` cover `orchestrate.py` and `validate.py` but not
    `knowledge/`, because the list predates this file.

    Injecting the provider is **not** a workaround for that block — the
    implementation is still missing and the step is still incomplete. It is the
    shape the function would have anyway: it makes fusion unit-testable without
    a model, and it keeps the LLM dependency out of a module whose whole point
    is being dependency-free.

    **The original query is always list zero**, for the reason S-C19 gives: it
    is the highest-signal phrasing and must not depend on a generation call
    succeeding. It also means a total variant-generation failure degrades this
    to an ordinary single-query search rather than to nothing.

    **A search failure is NOT caught here.** `KnowledgeSearchError` propagates
    to the tool, which turns it into §27's coach-facing "this is a failure, not
    an absence" message. Catching it here would reintroduce the exact bug §27
    exists to prevent, one layer further in.
    """
    variants = await make_variants(query)
    queries = [query, *variants]

    ranked_lists: list[list[T]] = []
    for q in queries:
        ranked_lists.append(list(search(q)))

    fused = reciprocal_rank_fusion(ranked_lists, k=RRF_K, key=key)
    logger.info(
        "Multi-query fusion: %d quer(ies) -> %d unique doc(s), returning %d",
        len(queries), len(fused), min(top_k, len(fused)),
    )
    return [doc for doc, _score in fused[:top_k]]


__all__ = [
    "QueryVariants",
    "reciprocal_rank_fusion",
    "generate_variants",
    "run_multi_query",
    "RRF_K",
    "MIN_VARIANTS",
    "MAX_VARIANTS",
]
