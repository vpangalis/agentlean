"""Reciprocal Rank Fusion — half of what procedure step 5.2 requires.

**Step 5.2's *Done when* has two clauses.** This file is the second:
*"fusion.py's RRF is unit-tested at k=60"*. The first — a live
`rag_lookup_methodology` query returning docs whose `phase_relevance` is the
requested phase or `general` — is **not met**: the three tools are not written,
because variant generation is blocked (see `fusion.py`'s `run_multi_query`).

WHAT THESE TESTS ARE FOR
------------------------
RRF is fifteen lines and looks obviously right, which is exactly the kind of
code that is quietly wrong. The property that matters is not "it sorts" — it is
**cross-variant consistency**: a document several phrasings agree on must beat
one a single phrasing loved. That is the whole reason §25 mandates fusion over
native single-query ranking, and it is what `test_agreement_across_variants_
beats_a_single_first_place` pins.

The rest guard the ways fusion degenerates silently:
  * a wrong `k` — small k collapses fusion into "whatever list one said";
  * a broken identity key — every document unique turns fusion into
    concatenation, with no error and a plausible-looking result;
  * an unstable sort — ties resolving arbitrarily makes retrieval
    irreproducible across runs, which breaks LangSmith trace comparison.
"""
from __future__ import annotations

import asyncio

import pytest
from pydantic import ValidationError

from backend.knowledge.fusion import (
    MAX_VARIANTS,
    MIN_VARIANTS,
    RRF_K,
    QueryVariants,
    reciprocal_rank_fusion,
    run_multi_query,
)


def doc(doc_id: str, content: str = "") -> dict:
    """A retriever-shaped dict — what `knowledge/retriever.py` returns (S-F18)."""
    return {"id": doc_id, "content": content or f"content of {doc_id}"}


def ids(fused: list[tuple[dict, float]]) -> list[str]:
    return [d["id"] for d, _ in fused]


# ── k=60, stated as the step requires ─────────────────────────────────────

def test_the_constant_is_60() -> None:
    """§25 and S-F17 B1. Not a tuning knob — it is the RRF paper's constant."""
    assert RRF_K == 60


def test_scores_are_one_over_k_plus_rank_at_k_60() -> None:
    """The formula itself, arithmetic-exact at the ratified k."""
    fused = reciprocal_rank_fusion([[doc("a"), doc("b"), doc("c")]])
    scores = {d["id"]: s for d, s in fused}
    assert scores["a"] == pytest.approx(1 / 60)
    assert scores["b"] == pytest.approx(1 / 61)
    assert scores["c"] == pytest.approx(1 / 62)


def test_k_defaults_to_60_when_not_passed() -> None:
    """Callers must not have to remember it; `run_multi_query` never passes it."""
    assert (reciprocal_rank_fusion([[doc("a")]])[0][1]
            == pytest.approx(reciprocal_rank_fusion([[doc("a")]], k=60)[0][1]))


# ── B2: the property fusion exists for ────────────────────────────────────

def test_a_document_in_several_lists_accumulates_its_score() -> None:
    """S-F17 B2 — the sum across lists is the mechanism, not a detail."""
    fused = reciprocal_rank_fusion([[doc("a")], [doc("a")], [doc("a")]])
    assert len(fused) == 1
    assert fused[0][1] == pytest.approx(3 * (1 / 60))


def test_agreement_across_variants_beats_a_single_first_place() -> None:
    """**The point of §25.** Three phrasings agreeing outrank one enthusiast.

    `b` is never first for anyone; `a` is first for exactly one variant. Native
    single-query ranking cannot express this, because it does not know the other
    variants exist — which is the sentence §25 turns into a requirement.
    """
    fused = reciprocal_rank_fusion([
        [doc("a"), doc("b")],
        [doc("c"), doc("b")],
        [doc("d"), doc("b")],
    ])
    assert ids(fused)[0] == "b", (
        "the document three variants agreed on lost to one variant's favourite "
        "— cross-variant consistency is not being captured"
    )


def test_a_large_k_is_what_makes_that_possible() -> None:
    """Why 60 and not a small k — the guard on "simplifying" the constant.

    `a` is first for one variant; `b` is *third* for two. The verdict flips on
    k alone:

        k= 1   a = 1/1  = 1.000   b = 2/3  = 0.667   -> a
        k=60   a = 1/60 = 0.017   b = 2/62 = 0.032   -> b

    A small k makes the rank-0 slot dominate, so fusion collapses toward
    "whatever the first list ranked first" and stops measuring agreement. k=60
    flattens the rank curve enough that appearing in several lists is worth
    more than topping one.

    *(The first version of this test claimed the flip using `b` at rank 1 in
    three lists. That is false — 3 x 1/2 beats 1/1 at k=1 too. Kept as a
    reminder that the arithmetic here is not eyeballable.)*
    """
    lists = [
        [doc("a"), doc("x"), doc("b")],
        [doc("y"), doc("z"), doc("b")],
    ]
    assert ids(reciprocal_rank_fusion(lists, k=60))[0] == "b"
    assert ids(reciprocal_rank_fusion(lists, k=1))[0] == "a", (
        "this test documents the failure mode; if it changes, the reasoning "
        "for k=60 in fusion.py needs rewriting"
    )


def test_results_are_sorted_by_fused_score_descending() -> None:
    fused = reciprocal_rank_fusion([
        [doc("x"), doc("y"), doc("z")],
        [doc("y"), doc("z")],
    ])
    scores = [s for _, s in fused]
    assert scores == sorted(scores, reverse=True)
    assert ids(fused)[0] == "y"


# ── identity: the silent-degeneration guard ───────────────────────────────

def test_the_same_document_from_two_lists_is_one_entry() -> None:
    """Dedup by identity. Without it, fusion is concatenation with extra steps."""
    fused = reciprocal_rank_fusion([
        [doc("a", "same text")],
        [doc("a", "same text")],
    ])
    assert len(fused) == 1


def test_documents_are_keyed_on_id_not_content() -> None:
    """Two chunks of a corpus can legitimately share text; they are still two."""
    fused = reciprocal_rank_fusion([
        [doc("a", "identical text"), doc("b", "identical text")],
    ])
    assert sorted(ids(fused)) == ["a", "b"]


def test_content_is_the_fallback_when_a_select_forgot_id() -> None:
    """The raw-`SearchClient` paths must list `id` in `select=`.

    If one does not, every document arrives without an id. Keying on the object
    would then make each unique and fusion would silently stop deduplicating —
    a plausible-looking result and no error. The content fallback keeps dedup
    correct in that case.
    """
    fused = reciprocal_rank_fusion([
        [{"content": "no id here"}],
        [{"content": "no id here"}],
    ])
    assert len(fused) == 1
    assert fused[0][1] == pytest.approx(2 * (1 / 60))


def test_langchain_document_shape_is_supported() -> None:
    """S-F17 is written as `doc.metadata["id"]`; that shape must still work."""
    from langchain_core.documents import Document

    a = Document(page_content="x", metadata={"id": "a"})
    fused = reciprocal_rank_fusion([[a], [a]])
    assert len(fused) == 1 and fused[0][1] == pytest.approx(2 * (1 / 60))


def test_an_explicit_key_overrides_the_default() -> None:
    """Each tool answers identity for its own index."""
    fused = reciprocal_rank_fusion(
        [[{"case_id": "C1"}], [{"case_id": "C1"}]],
        key=lambda d: d["case_id"],
    )
    assert len(fused) == 1


# ── stability: retrieval must be reproducible ─────────────────────────────

def test_ties_resolve_toward_the_earliest_list() -> None:
    """Python's sort is stable and insertion order follows list one.

    `run_multi_query` makes list one the Belt's own query, so a tie resolves
    toward their phrasing. It also means the same inputs give the same order
    twice — without which a LangSmith trace cannot be read against a rerun.
    """
    fused = reciprocal_rank_fusion([[doc("first"), doc("second")]])
    assert ids(fused) == ["first", "second"]
    again = reciprocal_rank_fusion([[doc("first"), doc("second")]])
    assert ids(again) == ids(fused)


def test_empty_input_is_empty_output_not_an_error() -> None:
    """A variant that matched nothing contributes nothing; it is not a failure."""
    assert reciprocal_rank_fusion([]) == []
    assert reciprocal_rank_fusion([[], []]) == []


def test_a_variant_that_matched_nothing_does_not_disturb_the_others() -> None:
    fused = reciprocal_rank_fusion([[doc("a")], [], [doc("a")]])
    assert len(fused) == 1
    assert fused[0][1] == pytest.approx(2 * (1 / 60))


# ── S-C19 / G-14: the schema this step ruled ──────────────────────────────

def test_the_variant_count_is_bounded_at_three_to_five() -> None:
    """§25 says "3–5". Enforced by the schema, so a violation fails at parse."""
    assert MIN_VARIANTS == 3 and MAX_VARIANTS == 5
    assert QueryVariants(variants=["a", "b", "c"]).variants == ["a", "b", "c"]
    assert len(QueryVariants(variants=list("abcde")).variants) == 5
    with pytest.raises(ValidationError):
        QueryVariants(variants=["a", "b"])
    with pytest.raises(ValidationError):
        QueryVariants(variants=list("abcdef"))


def test_the_schema_carries_exactly_one_field() -> None:
    """G-14 ruling 1 — a `rationale` field would be generated every retrieval,
    read by nothing, and paid for in tokens on the hot path."""
    assert list(QueryVariants.model_fields) == ["variants"]


# ── the mechanism end to end, without a model ─────────────────────────────

def test_the_original_query_is_always_searched_first() -> None:
    """G-14 ruling 2 — the Belt's phrasing must not depend on a generation call.

    It is list zero, so a total variant failure degrades multi-query to an
    ordinary single-query search rather than to nothing.
    """
    seen: list[str] = []

    def search(q: str) -> list[dict]:
        seen.append(q)
        return [doc(f"hit-for-{q}")]

    async def variants(_q: str) -> list[str]:
        return ["rephrased one", "rephrased two", "rephrased three"]

    asyncio.run(run_multi_query("the belt's words", search, 10, variants))
    assert seen[0] == "the belt's words"
    assert len(seen) == 4, "fan-out is 1 + len(variants), not len(variants)"


def test_a_failed_variant_call_degrades_to_single_query() -> None:
    """No variants is worse retrieval, not broken retrieval."""
    async def no_variants(_q: str) -> list[str]:
        return []

    out = asyncio.run(run_multi_query("q", lambda q: [doc("a")], 10, no_variants))
    assert [d["id"] for d in out] == ["a"]


def test_top_k_slices_after_fusion_not_before() -> None:
    """Slicing per-variant would discard documents fusion was about to promote."""
    def search(q: str) -> list[dict]:
        return ([doc("a"), doc("b"), doc("c")] if q == "q"
                else [doc("c"), doc("b"), doc("a")])

    async def variants(_q: str) -> list[str]:
        return ["v1", "v2", "v3"]

    out = asyncio.run(run_multi_query("q", search, 2, variants))
    assert len(out) == 2
    assert {d["id"] for d in out} == {"b", "c"}, (
        "b and c are ranked well by the three variants; a leads only the "
        "original, so fusion should demote it"
    )


def test_a_search_failure_propagates_rather_than_being_swallowed() -> None:
    """§27, one layer in. Catching here would rebuild the bug 5.1 just closed."""
    from backend.core.errors import AgentImproveError, KnowledgeSearchError

    def broken(_q: str):
        raise KnowledgeSearchError(AgentImproveError(
            error_code="INVALID_QUERY", severity="permanent",
            retry_recommendation="do_not_retry",
            affected_identifier="improve_knowledge_index", message="boom",
        ))

    async def variants(_q: str) -> list[str]:
        return ["a", "b", "c"]

    with pytest.raises(KnowledgeSearchError):
        asyncio.run(run_multi_query("q", broken, 10, variants))
