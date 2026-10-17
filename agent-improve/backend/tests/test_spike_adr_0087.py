"""SPIKE — ADR-0087 "The approval node writes both records" (founder 2026-10-17, item 4: spike on a branch, the
killed-process test included). Not for main: the ADR is ruled on what these show.

Q1 (the ADR's open question): when the approval node fails and T29's error handler answers, is the approval
still pending — GET /gate/review awaiting a decision, a second approval completing and writing once — or was
the resume used up?
"""
from __future__ import annotations

import pytest

from backend.tests.test_gate_acceptance import CASE_ID, _decide, _review, _submit, env  # noqa: F401


@pytest.fixture(autouse=True)
def _spike_on(request, monkeypatch):
    """The spike's path, switched on for its own tests (Q1 and Q2 measure main's behaviour and keep it off)."""
    from backend.core import graph as graph_mod
    if not request.node.name.startswith(("test_q1", "test_q2")):
        monkeypatch.setattr(graph_mod, "SPIKE_APPROVAL_WRITES_BOTH", True)
    graph_mod.get_graph.cache_clear()
    yield
    graph_mod.get_graph.cache_clear()


@pytest.fixture(autouse=True)
def _no_registry(monkeypatch):
    """The gate env never fakes the registry: a passed gate's _clear_escalation read the REAL registry.json
    through aiohttp, past pytest-socket (found by this spike). Kept off Azure here."""
    from backend.storage import blob

    async def nothing(*a, **k):
        return None
    monkeypatch.setattr(blob, "set_escalation", nothing)


def test_q1_after_a_failed_approval_is_the_decision_still_pending(env, monkeypatch) -> None:
    from backend.core import graph as graph_mod
    from backend.core.store import get_store
    from backend.phases.mappers_common import read_gate_document, write_gate_document

    real = graph_mod.OUTPUT_MAPPERS["define"]
    calls = {"n": 0}

    def failing_once(child, parent, store):
        calls["n"] += 1
        if calls["n"] == 1:
            write_gate_document(store, parent, "define", child)
            raise RuntimeError("the case record is unreachable")
        return real(child, parent, store)
    monkeypatch.setitem(graph_mod.OUTPUT_MAPPERS, "define", failing_once)
    _submit(env)
    first = _decide(env, decision="approve")
    review = _review(env)
    second = _decide(env, decision="approve")
    print("\nQ1 first:", first.status_code, first.json().get("detail"))
    print("Q1 review after the failure:", {k: review.get(k) for k in ("awaiting_decision", "passed", "phase")})
    print("Q1 second:", second.status_code, (second.json().get("detail") or second.json().get("message")))
    print("Q1 store after:", bool(read_gate_document(get_store(), CASE_ID, "define")), "written:", len(env.written),
          "phase:", env.case.current_phase)


def test_q2_if_the_handler_re_raises_is_the_decision_still_pending(env, monkeypatch) -> None:
    """Q2: the same failure, but the phase node's error handler re-raises instead of answering — the run ends
    with the exception, nothing of the node is committed."""
    from backend.core import graph as graph_mod
    from backend.core.store import get_store
    from backend.phases.mappers_common import read_gate_document, write_gate_document

    from backend.core.graph import NodeError

    def re_raising(node):
        async def handler(state, error: NodeError, config=None):
            cause = getattr(error, "error", error)
            assert isinstance(cause, BaseException)
            raise cause
        return handler
    monkeypatch.setattr(graph_mod, "degraded_handler", re_raising)
    graph_mod.get_graph.cache_clear()
    real = graph_mod.OUTPUT_MAPPERS["define"]
    calls = {"n": 0}

    def failing_once(child, parent, store):
        calls["n"] += 1
        if calls["n"] == 1:
            write_gate_document(store, parent, "define", child)
            raise RuntimeError("the case record is unreachable")
        return real(child, parent, store)
    monkeypatch.setitem(graph_mod.OUTPUT_MAPPERS, "define", failing_once)
    _submit(env)
    first = _decide(env, decision="approve")
    review = _review(env)
    second = _decide(env, decision="approve")
    print("\nQ2 first:", first.status_code, (first.json() or {}).get("detail"))
    print("Q2 review after the failure:", {k: review.get(k) for k in ("awaiting_decision", "passed", "phase")})
    print("Q2 second:", second.status_code, (second.json().get("detail") or second.json().get("message")))
    print("Q2 store after:", bool(read_gate_document(get_store(), CASE_ID, "define")), "written:", len(env.written),
          "phase:", env.case.current_phase, "mapper calls:", calls["n"])


def test_q3_no_handler_what_the_checkpoint_holds_and_whether_a_retry_completes(env, monkeypatch) -> None:
    """Q3: the phase node with no error handler: the failure escapes the run. What does the parent checkpoint
    hold — the pending task, its error, the interrupt — and does LangGraph's own retry (invoking with no input)
    run the approval again and complete it?"""
    import asyncio

    from backend.core import graph as graph_mod
    from backend.core.store import get_store
    from backend.gateway import routes
    from backend.phases.mappers_common import read_gate_document, write_gate_document

    monkeypatch.setattr(graph_mod, "degraded_handler", lambda node: None)
    graph_mod.get_graph.cache_clear()
    real = graph_mod.OUTPUT_MAPPERS["define"]
    calls = {"n": 0}

    def failing_once(child, parent, store):
        calls["n"] += 1
        if calls["n"] == 1:
            write_gate_document(store, parent, "define", child)
            raise RuntimeError("the case record is unreachable")
        return real(child, parent, store)
    monkeypatch.setitem(graph_mod.OUTPUT_MAPPERS, "define", failing_once)
    _submit(env)
    first = _decide(env, decision="approve")
    review = _review(env)
    print("\nQ3 first:", first.status_code, (first.json() or {}).get("detail"))
    print("Q3 review after the failure:", {k: review.get(k) for k in ("awaiting_decision", "passed")})

    async def inspect_and_retry():
        graph, config, pending = await routes._pending_interrupts(env.case, "define")
        snap = await graph.aget_state(config)
        print("Q3 next:", snap.next, "| tasks:", [(t.name, type(t.error).__name__ if t.error else None,
                                                   len(t.interrupts or ())) for t in snap.tasks])
        out = await graph.ainvoke(None, config)
        snap2 = await graph.aget_state(config)
        print("Q3 retry: next", snap2.next, "| current_phase", (snap2.values or {}).get("current_phase"),
              "| mapper calls", calls["n"], "| store has record", bool(read_gate_document(get_store(), routes.CASE_ID
              if hasattr(routes, "CASE_ID") else env.case.case_id, "define")))
        return out
    asyncio.run(inspect_and_retry())


# ── ADR-0087's own tests, on the spike's implementation ─────────────────────────────────────────────────────

class Killed(BaseException):
    """The process killed mid-approval: nothing that catches Exception runs, no undo, no handler."""


def _after(env):
    from backend.core.store import get_store
    from backend.phases.mappers_common import read_gate_document
    return {"store": bool(read_gate_document(get_store(), CASE_ID, "define")), "case_writes": len(env.written),
            "phase": env.case.current_phase, "awaiting": _review(env).get("awaiting_decision")}


def test_t1_failure_after_the_store_write(env, monkeypatch) -> None:
    from backend.core import graph as graph_mod
    from backend.phases.mappers_common import write_gate_document
    real, calls = graph_mod.OUTPUT_MAPPERS["define"], {"n": 0}

    def failing_once(child, parent, store):
        calls["n"] += 1
        if calls["n"] == 1:
            write_gate_document(store, parent, "define", child)
            raise RuntimeError("after the Store write")
        return real(child, parent, store)
    monkeypatch.setitem(graph_mod.OUTPUT_MAPPERS, "define", failing_once)
    _submit(env)
    first = _decide(env, decision="approve")
    mid = _after(env)
    second = _decide(env, decision="approve")
    end = _after(env)
    print("\nT1 first", first.status_code, "| after failure", mid, "| second", second.status_code, "| end", end)
    assert first.status_code == 503 and mid == {"store": False, "case_writes": 0, "phase": "define", "awaiting": True}
    assert second.status_code == 200 and end["store"] and end["case_writes"] == 1 and end["phase"] == "measure"


def test_t2_failure_at_the_case_write(env, monkeypatch) -> None:
    from backend.storage import blob
    real, calls = blob.write_phase_gate, {"n": 0}

    async def failing_once(**kw):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("the case record is unreachable")
        return await real(**kw)
    monkeypatch.setattr(blob, "write_phase_gate", failing_once)
    _submit(env)
    first = _decide(env, decision="approve")
    mid = _after(env)
    second = _decide(env, decision="approve")
    end = _after(env)
    print("\nT2 first", first.status_code, "| after failure", mid, "| second", second.status_code, "| end", end)
    assert first.status_code == 503 and mid == {"store": False, "case_writes": 0, "phase": "define", "awaiting": True}
    assert second.status_code == 200 and end["store"] and end["case_writes"] == 1 and end["phase"] == "measure"


def test_t2b_failure_after_the_case_write(env, monkeypatch) -> None:
    """DEF-170's own case (G-178): the case write succeeded and a later step failed."""
    from backend.core import graph as graph_mod
    real, calls = graph_mod._write_case_record, {"n": 0}

    async def write_then_fail(*a, **k):
        calls["n"] += 1
        out = await real(*a, **k)
        if calls["n"] == 1:
            raise RuntimeError("after the case write")
        return out
    monkeypatch.setattr(graph_mod, "_write_case_record", write_then_fail)
    saved_before = len(env.saved)
    _submit(env)
    first = _decide(env, decision="approve")
    restored = env.saved[saved_before:]
    mid = _after(env)
    second = _decide(env, decision="approve")
    end = _after(env)
    print("\nT2b first", first.status_code, "| restored writes", len(restored),
          "| restored to define:", bool(restored) and restored[-1].current_phase == "define",
          "| after failure", mid, "| second", second.status_code, "| end", end)
    assert first.status_code == 503 and not mid["store"] and mid["awaiting"] is True
    assert restored and restored[-1].current_phase == "define" and not restored[-1].phases["define"].gate_passed
    assert second.status_code == 200 and end["store"] and end["phase"] == "measure"


def test_t3_the_success_path(env) -> None:
    _submit(env)
    ok = _decide(env, decision="approve")
    end = _after(env)
    again = _decide(env, decision="approve")
    print("\nT3 approve", ok.status_code, "| end", end, "| second", again.status_code, "| writes", len(env.written))
    assert ok.status_code == 200 and end["store"] and end["case_writes"] == 1 and end["phase"] == "measure"
    assert again.status_code == 409 and len(env.written) == 1


def test_t5_a_killed_process_between_the_two_writes(env, monkeypatch) -> None:
    import pytest

    from backend.core import graph as graph_mod
    from backend.core.store import get_store
    from backend.phases.mappers_common import read_gate_document
    real = graph_mod._write_case_record

    async def killed(*a, **k):
        raise Killed("the process was killed after the Store write")
    monkeypatch.setattr(graph_mod, "_write_case_record", killed)
    _submit(env)
    with pytest.raises(BaseException) as got:      # Starlette wraps it: the process "died" mid-request
        _decide(env, decision="approve")
    assert "Killed" in repr(got.value) or "No response returned" in str(got.value), repr(got.value)
    left = {"store": bool(read_gate_document(get_store(), CASE_ID, "define")), "case_writes": len(env.written)}
    monkeypatch.setattr(graph_mod, "_write_case_record", real)
    env.restart()                                    # a new process: the graph rebuilt, the saver over the same blobs
    awaiting = _review(env).get("awaiting_decision")
    resumed = _decide(env, decision="approve")
    end = _after(env)
    doc = read_gate_document(get_store(), CASE_ID, "define")
    print("\nT5 left by the kill", left, "| awaiting after restart", awaiting, "| resumed", resumed.status_code,
          resumed.json().get("detail"), "| end", end)
    assert left == {"store": True, "case_writes": 0}, "the kill is between the two writes"
    assert awaiting is True and resumed.status_code == 200, resumed.text
    assert end["store"] and end["case_writes"] == 1 and end["phase"] == "measure" and doc
