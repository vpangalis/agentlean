"""Retrieval failure semantics — what procedure step 5.1 established.

**Step 5.1's *Done when* is two assertions**: a forced Azure failure raises
`KnowledgeSearchError` with `severity="permanent"` on a 4xx, and a genuine
no-match returns `[]`. Those are
`test_a_4xx_raises_with_severity_permanent` and
`test_a_genuine_no_match_returns_an_empty_list`.

WHY THIS FILE IS LARGER THAN THOSE TWO
--------------------------------------
§27 is a rule written from an incident. The `phase` filter bug **reported a
broken index as a silent empty corpus for an extended period**, and the coach
told Belts the methodology had nothing on their topic — false, and unfalsifiable
from the outside because an empty list is what "nothing matched" looks like too.

The rule that prevents it is not one assertion, it is a boundary: **`[]` means
the search ran and matched nothing, and nothing else.** So these tests hold the
boundary from both sides, and check the three rules §27 says have each already
bitten:

  1. `RETRIEVAL_EXCEPTIONS` spans **two services** — Azure AI Search and the
     Azure OpenAI query embedding, which runs inside the same `try`;
  2. **a 4xx is `permanent` / `do_not_retry`**, not transient — it is our
     malformed query and retrying fails identically;
  3. **results are materialised inside the `try`** — `SearchClient.search()` is
     lazy and the HTTP call fires on iteration, so a `try` that returns the
     iterator catches nothing.

And the fourth thing, which is where step 5.1 found live work:
**a failure must not reach the coach as an absence.**

No network. Every Azure and OpenAI boundary is replaced with a fake that raises
the real exception types, so the classification under test is the one that runs
in production.
"""
from __future__ import annotations

from typing import Any

import pytest
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ServiceRequestError,
)

from backend.core.errors import KnowledgeSearchError
from backend.knowledge import retriever


# ── fakes ─────────────────────────────────────────────────────────────────

class FakeVectorStore:
    """Stands in for `AzureSearch`. Raises, or returns materialised docs."""

    def __init__(self, raises: Exception | None = None, docs: list | None = None):
        self._raises = raises
        self._docs = docs or []
        self.calls: list[dict[str, Any]] = []

    def similarity_search(self, query: str, k: int = 4, filters=None):
        self.calls.append({"query": query, "k": k, "filters": filters})
        if self._raises is not None:
            raise self._raises
        return list(self._docs)


class FakeDoc:
    def __init__(self, content: str, **metadata: Any):
        self.page_content = content
        self.metadata = metadata


class LazyResults:
    """A results object that raises **on iteration**, like `SearchClient.search`.

    This is §27 rule 3 made testable: if a retrieval function returns the
    iterator instead of materialising it inside the `try`, the exception
    escapes unclassified and this fake is what proves it.
    """

    def __init__(self, raises: Exception):
        self._raises = raises

    def __iter__(self):
        raise self._raises


class FakeSearchClient:
    def __init__(self, results: Any):
        self._results = results

    def search(self, **kwargs: Any):
        return self._results


class FakeEmbeddings:
    def __init__(self, raises: Exception | None = None):
        self._raises = raises

    def embed_query(self, text: str) -> list[float]:
        if self._raises is not None:
            raise self._raises
        return [0.1, 0.2, 0.3]


def http_error(status: int) -> HttpResponseError:
    """An `HttpResponseError` carrying a real status code."""
    exc = HttpResponseError(message=f"simulated {status}")
    exc.status_code = status
    return exc


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Nothing in this module may reach Azure. Fails loudly if it tries."""
    monkeypatch.setattr(
        retriever, "get_embeddings", lambda: FakeEmbeddings()
    )


# ── step 5.1's Done-when ──────────────────────────────────────────────────

def test_a_4xx_raises_with_severity_permanent(monkeypatch) -> None:
    """**Done-when, first clause.** A 4xx is our malformed query, not a blip.

    Retrying it fails identically at the same cost, which is why
    `retry_recommendation` must say so — the fallback chain reads that field to
    choose its backoff (§4.8), and "transient" would put it in a retry loop
    against a query that can never succeed.
    """
    vs = FakeVectorStore(raises=http_error(400))
    monkeypatch.setattr(retriever, "get_knowledge_vectorstore", lambda: vs)

    with pytest.raises(KnowledgeSearchError) as caught:
        retriever.search_knowledge("anything", phase="define")

    err = caught.value.error
    assert err.severity == "permanent"
    assert err.retry_recommendation == "do_not_retry"
    assert err.error_code == "INVALID_QUERY"


def test_a_genuine_no_match_returns_an_empty_list(monkeypatch) -> None:
    """**Done-when, second clause.** The search ran; the corpus had nothing.

    This is the ONLY thing `[]` is allowed to mean.
    """
    vs = FakeVectorStore(docs=[])
    monkeypatch.setattr(retriever, "get_knowledge_vectorstore", lambda: vs)

    assert retriever.search_knowledge("nothing matches this", phase="define") == []
    assert vs.calls, "the search never ran — [] would be meaningless"


# ── §27 rule 2, across the status range ───────────────────────────────────

@pytest.mark.parametrize(
    "status, code, severity, retry",
    [
        (400, "INVALID_QUERY", "permanent", "do_not_retry"),
        (403, "INVALID_QUERY", "permanent", "do_not_retry"),
        (404, "INVALID_QUERY", "permanent", "do_not_retry"),
        (429, "RATE_LIMIT", "transient", "retry_after_backoff"),
        (500, "SERVICE_ERROR", "transient", "retry_after_backoff"),
        (503, "SERVICE_ERROR", "transient", "retry_after_backoff"),
    ],
)
def test_status_codes_classify_as_ratified(
    monkeypatch, status: int, code: str, severity: str, retry: str
) -> None:
    """429 is transient even though it is a 4xx — it is the service throttling,
    not our query being wrong, so it is the one 4xx worth retrying."""
    vs = FakeVectorStore(raises=http_error(status))
    monkeypatch.setattr(retriever, "get_knowledge_vectorstore", lambda: vs)

    with pytest.raises(KnowledgeSearchError) as caught:
        retriever.search_knowledge("q")

    err = caught.value.error
    assert (err.error_code, err.severity, err.retry_recommendation) == (
        code, severity, retry
    )


def test_auth_failure_is_permanent_and_not_a_generic_4xx(monkeypatch) -> None:
    """`ClientAuthenticationError` subclasses `HttpResponseError`.

    It must be tested before it in `_search_error`, or a bad key classifies as
    a generic 4xx and the operator reads "malformed query" for an expired
    credential.
    """
    vs = FakeVectorStore(raises=ClientAuthenticationError(message="bad key"))
    monkeypatch.setattr(retriever, "get_knowledge_vectorstore", lambda: vs)

    with pytest.raises(KnowledgeSearchError) as caught:
        retriever.search_knowledge("q")

    err = caught.value.error
    assert err.error_code == "AUTH_FAILURE"
    assert err.severity == "permanent"


def test_a_connection_failure_is_transient(monkeypatch) -> None:
    vs = FakeVectorStore(raises=ServiceRequestError(message="no route"))
    monkeypatch.setattr(retriever, "get_knowledge_vectorstore", lambda: vs)

    with pytest.raises(KnowledgeSearchError) as caught:
        retriever.search_knowledge("q")

    assert caught.value.error.error_code == "CONNECTION_FAILURE"
    assert caught.value.error.severity == "transient"


# ── §27 rule 1: two services inside one try ───────────────────────────────

def test_the_embedding_call_is_inside_the_same_try(monkeypatch) -> None:
    """The query embedding runs in the same `try` as the search (§27 rule 1).

    `RETRIEVAL_EXCEPTIONS` includes `OpenAIError` for exactly this reason:
    omitting it would let a raw provider exception escape and take down the
    coaching turn instead of degrading it.
    """
    from openai import APIConnectionError

    monkeypatch.setattr(
        retriever, "get_embeddings",
        lambda: FakeEmbeddings(raises=APIConnectionError(request=None)),  # type: ignore[arg-type]
    )
    monkeypatch.setattr(
        retriever, "SearchClient", lambda **kw: FakeSearchClient([])
    )

    with pytest.raises(KnowledgeSearchError) as caught:
        retriever.search_cases("q")

    err = caught.value.error
    assert err.error_code == "EMBEDDING_CONNECTION_FAILURE", (
        "an embedding failure must classify as one — the EMBEDDING_ prefix is "
        "what keeps 'which service broke' readable in the log"
    )
    assert err.severity == "transient"


def test_openai_error_is_in_the_retrieval_exception_tuple() -> None:
    """Pinned by name: dropping it lets a provider exception escape unclassified."""
    from openai import OpenAIError

    assert OpenAIError in retriever.RETRIEVAL_EXCEPTIONS
    assert HttpResponseError in retriever.RETRIEVAL_EXCEPTIONS
    assert ServiceRequestError in retriever.RETRIEVAL_EXCEPTIONS
    assert ClientAuthenticationError in retriever.RETRIEVAL_EXCEPTIONS


# ── §27 rule 3: lazy iteration must be materialised inside the try ────────

@pytest.mark.parametrize(
    "fn, kwargs, index_attr",
    [
        (lambda: retriever.search_cases("q"), {}, "AZURE_SEARCH_IMPROVE_CASE_INDEX"),
        (lambda: retriever.search_evidence("q", case_id="C1"), {},
         "AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX"),
    ],
)
def test_a_failure_on_iteration_is_still_classified(
    monkeypatch, fn, kwargs, index_attr: str
) -> None:
    """§27 rule 3 — `SearchClient.search()` is lazy; the HTTP call fires on
    iteration.

    `LazyResults` raises only when iterated. A function that returned the
    iterator, or built its list outside the `try`, would let this escape as a
    raw `HttpResponseError` — the failure would reach the coach unclassified
    and, worse, would not be a `KnowledgeSearchError`, so every caller's
    `except KnowledgeSearchError` would miss it.
    """
    monkeypatch.setattr(
        retriever, "SearchClient",
        lambda **kw: FakeSearchClient(LazyResults(http_error(400))),
    )

    with pytest.raises(KnowledgeSearchError) as caught:
        fn()

    assert caught.value.error.error_code == "INVALID_QUERY"
    assert caught.value.error.severity == "permanent"


@pytest.mark.parametrize(
    "fn", [
        lambda: retriever.search_cases("q"),
        lambda: retriever.search_evidence("q", case_id="C1"),
    ],
)
def test_the_raw_client_paths_return_empty_on_a_genuine_no_match(
    monkeypatch, fn
) -> None:
    """The other side of the same boundary, for the two raw-`SearchClient` paths."""
    monkeypatch.setattr(
        retriever, "SearchClient", lambda **kw: FakeSearchClient([])
    )
    assert fn() == []


# ── the failure must never reach the coach as an absence ──────────────────

def test_build_knowledge_context_returns_none_when_nothing_matched(
    monkeypatch
) -> None:
    """A genuine empty corpus injects nothing, and warns about nothing."""
    monkeypatch.setattr(retriever, "get_knowledge_vectorstore",
                        lambda: FakeVectorStore(docs=[]))
    assert retriever.build_knowledge_context("define", "how do I scope?") is None


def test_build_knowledge_context_says_so_when_retrieval_broke(monkeypatch) -> None:
    """**The gap step 5.1 found.** This used to return `None` — the same value
    as "nothing matched".

    §27: *"Never let a coach-facing failure message read as an absence of
    content."* `knowledge/tools.py` already drew this distinction for the three
    `@tool` entry points; this is the path all five orchestrators take on every
    turn, and it did not.
    """
    monkeypatch.setattr(
        retriever, "get_knowledge_vectorstore",
        lambda: FakeVectorStore(raises=http_error(400)),
    )

    out = retriever.build_knowledge_context("define", "how do I scope?")

    assert out is not None, (
        "a retrieval failure returned the same value as a no-match — the coach "
        "cannot tell a silent corpus from a broken one"
    )
    assert "not an absence" in out
    assert "INVALID_QUERY" in out, "the coach-facing text names the error code"
    assert "do not tell the team the methodology has nothing" in out


def test_the_failure_block_carries_no_response_scaffolding(monkeypatch) -> None:
    """The failure block must not tell the coach to cite references it lacks.

    The success block ends with a REQUIRED RESPONSE STRUCTURE section that
    instructs the coach to reference the retrieved material. Attaching that to
    a failure would ask it to cite sources it could not retrieve — which is the
    one thing §27's wording explicitly forbids.
    """
    monkeypatch.setattr(
        retriever, "get_knowledge_vectorstore",
        lambda: FakeVectorStore(raises=http_error(500)),
    )
    out = retriever.build_knowledge_context("define", "q")
    assert out is not None
    assert "REQUIRED RESPONSE STRUCTURE" not in out
    assert "BLACK BELT METHODOLOGY REFERENCES" not in out
    assert "avoid citing sources you could not retrieve" in out


def test_build_knowledge_context_returns_the_block_when_it_matched(
    monkeypatch
) -> None:
    """The success path still works — the boundary has three outcomes, not two."""
    monkeypatch.setattr(
        retriever, "get_knowledge_vectorstore",
        lambda: FakeVectorStore(docs=[FakeDoc("A SIPOC maps the process.")]),
    )
    out = retriever.build_knowledge_context("define", "what is a SIPOC?")
    assert out is not None
    assert "BLACK BELT METHODOLOGY REFERENCES" in out
    assert "A SIPOC maps the process." in out
    assert "not an absence" not in out


# ── the prohibition itself, checked as a property of the module ───────────

def test_no_bare_except_exception_in_the_retriever() -> None:
    """§27: *"Never wrap a retrieval call in a bare `except Exception`."*

    AST, not text — the module's own docstrings and comments quote the banned
    construct in order to forbid it, and a substring check trips on that prose.
    `json.JSONDecodeError` / `TypeError` on a single metadata blob is a
    different thing and is allowed: it degrades one document, is logged, and
    cannot mask a search failure because the search already returned.
    """
    import ast
    import pathlib

    src = pathlib.Path(retriever.__file__).read_text(encoding="utf-8")
    offenders: list[int] = []
    for node in ast.walk(ast.parse(src)):
        if not isinstance(node, ast.ExceptHandler):
            continue
        t = node.type
        if t is None:                                   # bare `except:`
            offenders.append(node.lineno)
        elif isinstance(t, ast.Name) and t.id == "Exception":
            offenders.append(node.lineno)
    assert not offenders, (
        f"bare `except Exception` at line(s) {offenders} — a broken index "
        f"reported as a silent corpus is the bug §27 exists to prevent"
    )


def test_every_retrieval_function_documents_the_empty_list_contract() -> None:
    """The contract lives in the docstring because callers read it there."""
    for fn in (retriever.search_knowledge, retriever.search_cases,
               retriever.search_evidence):
        doc = (fn.__doc__ or "").lower()
        assert "only when the search ran and matched nothing" in doc, fn.__name__
        assert "knowledgesearcherror" in doc, fn.__name__
