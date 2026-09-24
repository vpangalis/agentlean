"""No span ever starts a trace of its own — gap G-95.

On 2026-09-24 LangSmith refused every trace with 429 "Monthly unique traces
usage limit exceeded". Root traces: 19 on 09-23, 4,897 on 09-24 — 827 test
graph runs (tracing switched on for the whole pytest process by the first test
that started the app) and ~4,070 standalone spans (step 8.0's executor slice,
a2067db, whose spans became ROOT traces wherever no turn enclosed them: unit
tests and 6.54's startup warm-up).

These tests switch tracing ON inside the test, count what the LangSmith client
is asked to create — never sending it — and show that a span outside a traced
run creates nothing, that a span inside one still records, and that the app's
startup creates nothing. The session-wide half (tests never trace at all) is
`conftest.py`'s `_no_tracing` fixture and its `pytest_sessionfinish` guard.
"""
from __future__ import annotations

import time
from types import SimpleNamespace
from typing import Any

import pytest
from langsmith import Client, trace
from langsmith.run_trees import configure

from backend.core import llm as llm_mod
from backend.core.tracing import child_span, child_trace
from backend.knowledge import retriever as r


@pytest.fixture
def traced(monkeypatch):
    """Tracing ON for this test, with its own counter; nothing is sent."""
    calls: list[str] = []
    for method in ("create_run", "update_run", "batch_ingest_runs", "multipart_ingest"):
        if hasattr(Client, method):
            monkeypatch.setattr(Client, method,
                                lambda self, *a, _m=method, **k: calls.append(_m))
    monkeypatch.setenv("LANGSMITH_API_KEY", "not-a-real-key")
    configure(enabled=True, client=Client(api_key="not-a-real-key"))
    yield calls
    configure(enabled=False)


def _settle() -> None:
    time.sleep(0.3)          # the SDK hands runs to a background thread


@child_span(run_type="chain", name="test.child_span")
def _spanned() -> int:
    return 1


def test_a_span_outside_a_run_creates_no_trace(traced) -> None:
    _spanned()
    llm_mod._build_llm.cache_clear()
    with child_trace("test.child_trace") as span:
        span.end(outputs={"ok": True})
    _settle()
    assert not traced, f"a span with no enclosing run started a trace: {traced}"


def test_a_span_inside_a_run_still_records(traced) -> None:
    """The gate must not switch tracing off altogether: inside a traced run,
    the same span is a child and IS recorded."""
    with trace("test.parent"):
        _spanned()
    _settle()
    assert traced, "a span inside a traced run recorded nothing"


def test_the_server_start_creates_no_trace(traced, monkeypatch) -> None:
    """6.54's warm-up builds every client at startup, with no turn around it —
    exactly where a root span used to start a trace."""
    def fake(*_: Any, **__: Any) -> Any:
        return SimpleNamespace(close=lambda: None)
    for name in ("AzureOpenAIEmbeddings", "AzureSearch", "SearchClient"):
        monkeypatch.setattr(r, name, fake)
    monkeypatch.setattr(llm_mod, "AzureChatOpenAI", fake)
    r.close_clients()
    llm_mod._build_llm.cache_clear()

    from fastapi.testclient import TestClient
    from backend.app import app
    with TestClient(app):
        pass
    r.close_clients()
    llm_mod._build_llm.cache_clear()
    _settle()
    assert not traced, f"starting the server created {len(traced)} tracing call(s)"
