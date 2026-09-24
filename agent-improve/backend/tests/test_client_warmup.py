"""The clients are built once, at startup — procedure step 6.54 (gap G-93).

WHAT THE SPANS SHOWED (step 8.0's executor slice, trace 01a0d357…, the first
turn in a process): the cached embeddings client was built SIX times at once
(4.8–5.1 s each) and the knowledge search client SIX times at once
(10.5–10.7 s each), because six lookup threads missed an empty `lru_cache`
together and `lru_cache` does not stop them all building. Measured apart,
one build costs 2.5 s and 3.5 s — mostly loading the TLS certificate bundle —
and six racing builds cost 7.2 s each, 38 s of certificate loading summed.
Case and evidence searches built a new `SearchClient` per call, 7–12 per
lookup, each with its own certificates to load.

The fix, tested here: each client is built by exactly one caller however many
arrive at an empty cache; one search client per index; and the app builds
every client a turn uses before it accepts a request, so no turn pays for one.
"""
from __future__ import annotations

import threading
import time
from types import SimpleNamespace
from typing import Any

import pytest

from backend.core import llm as llm_mod
from backend.knowledge import retriever as r

RACERS = 6


def _race(fn: Any) -> None:
    """RACERS threads call `fn` at the same instant."""
    gate = threading.Barrier(RACERS)

    def run() -> None:
        gate.wait()
        fn()

    threads = [threading.Thread(target=run) for _ in range(RACERS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def _counting(builds: list[str], label: str) -> Any:
    """A client constructor that is slow enough for the race to happen."""
    def build(*_: Any, **__: Any) -> Any:
        builds.append(label)
        time.sleep(0.05)
        return SimpleNamespace(close=lambda: None)
    return build


def _reset() -> None:
    r.close_clients()
    llm_mod._build_llm.cache_clear()


@pytest.fixture
def empty_caches(monkeypatch):
    builds: list[str] = []
    monkeypatch.setattr(r, "AzureOpenAIEmbeddings", _counting(builds, "embeddings"))
    monkeypatch.setattr(r, "AzureSearch", _counting(builds, "vectorstore"))
    monkeypatch.setattr(r, "SearchClient", _counting(builds, "search_client"))
    monkeypatch.setattr(llm_mod, "AzureChatOpenAI", _counting(builds, "chat"))
    _reset()
    yield builds
    _reset()


@pytest.mark.parametrize("label, call", [
    ("embeddings", lambda: r.get_embeddings()),
    ("vectorstore", lambda: r.get_knowledge_vectorstore()),
    ("chat", lambda: llm_mod.get_llm("coach", max_tokens=1500)),
])
def test_six_threads_on_an_empty_cache_build_once(empty_caches, label, call) -> None:
    _race(call)
    made = [b for b in empty_caches if b == label]
    assert len(made) == 1, f"{RACERS} threads on an empty cache built {len(made)} {label} client(s)"


def test_one_search_client_per_index(empty_caches) -> None:
    """Case and evidence searches reuse one client per index — not one per call."""
    assert hasattr(r, "get_search_client"), "no per-index search client exists"
    _race(lambda: r.get_search_client("improve_case_index"))
    for _ in range(4):
        r.get_search_client("improve_case_index")
    r.get_search_client("improve_evidence_index")
    made = [b for b in empty_caches if b == "search_client"]
    assert len(made) == 2, f"{len(made)} search clients for two indexes"


def test_the_started_app_leaves_no_client_for_a_turn_to_build(empty_caches) -> None:
    """**The G-93 check.** Start the app; then every client a Define turn
    reaches for is already built — the turn's builds are zero."""
    from fastapi.testclient import TestClient
    from backend.app import app

    with TestClient(app):
        at_startup = len(empty_caches)
        # Every client a Define turn uses, with the arguments its call sites
        # pass — the cache keys the warm-up must have hit.
        for role, kw in llm_mod.TURN_LLM_CALLS:
            llm_mod.get_llm(role, **kw)
        r.get_embeddings()
        r.get_knowledge_vectorstore()
        r.get_search_client(r.settings.AZURE_SEARCH_IMPROVE_CASE_INDEX)
        r.get_search_client(r.settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX)
        during_turn = empty_caches[at_startup:]
    assert at_startup, "startup built nothing"
    assert not during_turn, f"a turn after startup still built: {during_turn}"


def test_every_get_llm_call_on_the_turn_path_is_warmed() -> None:
    """`TURN_LLM_CALLS` is the warm-up's list; this pins it to the call sites
    a Define turn actually runs, read from the source, so a new role on the
    turn path cannot be missed by the warm-up."""
    import ast
    import inspect
    from backend.knowledge import fusion
    from backend.middleware import coherence, grader
    from backend.phases import nodes_common

    seen = set()
    for mod in (nodes_common, coherence, grader, fusion):
        for node in ast.walk(ast.parse(inspect.getsource(mod))):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "get_llm"):
                role = ast.literal_eval(node.args[0]) if node.args else None
                kw = {k.arg: ast.literal_eval(k.value) for k in node.keywords}
                seen.add((role, tuple(sorted(kw.items()))))
    warmed = {(role, tuple(sorted(kw.items()))) for role, kw in llm_mod.TURN_LLM_CALLS}
    assert seen <= warmed, f"turn-path get_llm calls the warm-up misses: {sorted(seen - warmed)}"
