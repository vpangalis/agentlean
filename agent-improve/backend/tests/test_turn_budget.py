"""A turn always answers inside its budget — procedure step 6.52, B1 (gap G-92).

THE TEST THIS REPLACES, AND WHY IT PASSED WHILE THE BELT GOT A 500
-----------------------------------------------------------------
`test_executor_timeout.py` proved the soft budget by RE-IMPLEMENTING it: it
copied the executor's `asyncio.wait_for` into the test and drove a polite
`_SlowAgent` that awaited a millisecond sleep. So it could not see the two
things that beat the budget on 2026-09-24 (traces 01a0d215…, 01a0d28e…):

  1. the clock started at `agent.ainvoke`, ~5 s after the node — and the
     engine's 45 s wall — had started;
  2. `rag_lookup_*` ran synchronous `embed_query` + `search` on the event loop,
     so no timer, the soft one or the engine's, could fire until it returned.

These tests run the REAL `executor` node under LangGraph's REAL
`TimeoutPolicy`, with budgets injected small: a setup delay before the agent,
and a tool that BLOCKS with `time.sleep`. Nothing is waited for at full size.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import TimeoutPolicy

from backend.core.substate import PhaseState
from backend.knowledge import tools as ktools
from backend.phases import nodes_common as _nc
from backend.phases.subgraph_common import phase_nodes

#: The injected budgets. The soft budget sits below the wall exactly as
#: 40 s sits below 45 s; the setup delay eats most of it before the agent
#: starts, as ~5 s did on the live turns.
WALL = 1.0
SOFT = 0.6
SETUP_DELAY = 0.5
#: One blocking round trip of a lookup's search — embed + search, simulated.
BLOCK = 0.3
#: A lookup searches the original query plus this many variants.
VARIANTS = 3


def _state() -> PhaseState:
    base: PhaseState = {
        "case_id": "IMPR-TEST-652", "current_phase": "define",
        "messages": [HumanMessage(content="what does good look like here?")],
        "history": [], "phase_context": "", "coaching_plan": None,
        "field_index": 0, "draft": {}, "artifacts": {}, "step_log": [],
        "field_log": [], "belt_edits": {}, "turn_count": 0, "final": {},
        "gate_attempts": 0, "validator_feedback": [], "rejection_feedback": [],
        "citations": [], "uploads": [], "asks": [], "hop_results": [],
        "synthesis_output": None,
    }
    return base


#: Arguments a lookup cannot be called without.
_REQUIRED_ARGS = {"rag_lookup_evidence": {"case_id": "IMPR-TEST-652"}}


class _Variants:
    """`generate_variants`' model, answering at once."""

    def with_structured_output(self, schema: Any, **_: Any) -> "_Variants":
        return self

    async def ainvoke(self, *_: Any, **__: Any) -> Any:
        class R:
            variants = [f"variant {i}" for i in range(VARIANTS)]
        return R()


def _blocking_search(*_: Any, **__: Any) -> list[dict]:
    """A search that does what the real one does to the loop: hold it."""
    time.sleep(BLOCK)
    return [{"id": "d1", "content": "passage", "source_file": "f", "page_number": 1}]


@pytest.fixture
def blocking_lookups(monkeypatch):
    """The three lookups' searches block; variant generation is instant."""
    monkeypatch.setattr("backend.core.llm.get_llm", lambda *a, **k: _Variants())
    for name in ("search_knowledge", "search_evidence", "search_cases"):
        monkeypatch.setattr(ktools, name, _blocking_search)


class _LookupThenStallAgent:
    """The coach, reduced to what beat the budget: it calls a REAL bound
    lookup, then outlives any budget."""

    def __init__(self, tools: list[Any]) -> None:
        self.tools = {t.name: t for t in tools}

    async def ainvoke(self, payload: dict, *_: Any, **__: Any) -> dict:
        await self.tools["rag_lookup_methodology"].ainvoke({"query": "good problem statement"})
        await asyncio.sleep(30)
        return {"messages": [*payload["messages"], AIMessage(content="never")],
                "structured_response": None}


@pytest.fixture
def slow_turn(monkeypatch, stub_planner, blocking_lookups):
    """The real executor, a setup delay before its agent, a blocking tool."""
    monkeypatch.setattr(_nc, "EXECUTOR_SOFT_BUDGET", SOFT)

    async def delayed_dispatch(state: Any) -> list:
        await asyncio.sleep(SETUP_DELAY)
        return []

    monkeypatch.setattr(_nc, "_dispatch_routed_read", delayed_dispatch)
    monkeypatch.setattr(_nc, "create_agent",
                        lambda **kw: _LookupThenStallAgent(kw["tools"]))


def _graph():
    """The executor node exactly as the subgraph registers it, under a real wall."""
    b = StateGraph(PhaseState)
    b.add_node("executor", phase_nodes("define").executor,
               timeout=TimeoutPolicy(run_timeout=WALL))
    b.add_edge(START, "executor")
    b.add_edge("executor", END)
    return b.compile()


def test_a_slow_turn_answers_before_the_wall(slow_turn) -> None:
    """**The G-92 check.** Setup eats most of the budget and the coach's
    lookup blocks; the node must still finish FIRST — a degraded answer and a
    `partial_timeout` entry, never the engine's `NodeTimeoutError` (a 500).
    """
    started = time.monotonic()
    out = asyncio.run(_graph().ainvoke(_state()))
    elapsed = time.monotonic() - started

    assert elapsed < WALL, f"the node ran {elapsed:.2f}s against a {WALL}s wall"
    assert out["messages"][-1].content == _nc._TIMEOUT_MESSAGE
    assert any(e.get("status") == "partial_timeout" for e in out["step_log"]), (
        f"no partial_timeout in step_log: {[e.get('status') for e in out['step_log']]}")


def test_no_knowledge_tool_blocks_the_loop(blocking_lookups) -> None:
    """**The watchdog.** While each lookup runs against a search that blocks,
    a heartbeat ticking every 10 ms must never stall for more than 100 ms. A
    blocked loop is what kept every timer from firing on trace 01a0d28e….
    """
    async def measure(tool: Any) -> float:
        worst = 0.0
        done = asyncio.Event()

        async def heartbeat() -> None:
            nonlocal worst
            last = time.monotonic()
            while not done.is_set():
                await asyncio.sleep(0.01)
                now = time.monotonic()
                worst = max(worst, now - last)
                last = now

        beat = asyncio.create_task(heartbeat())
        await asyncio.sleep(0.02)
        await tool.ainvoke({"query": "anything", **_REQUIRED_ARGS.get(tool.name, {})})
        done.set()
        await beat
        return worst

    stalls = {t.name: asyncio.run(measure(t)) for t in ktools.RAG_LOOKUP_TOOLS}
    blocked = {n: round(s, 3) for n, s in stalls.items() if s > 0.1}
    assert not blocked, f"these tools held the event loop (seconds): {blocked}"


def test_a_lookup_runs_its_queries_concurrently(blocking_lookups) -> None:
    """Original + variants run together, not one after another: four blocking
    round trips take about one round trip, not four."""
    started = time.monotonic()
    asyncio.run(ktools.rag_lookup_methodology.ainvoke({"query": "q"}))
    elapsed = time.monotonic() - started
    assert elapsed < BLOCK * 2, (
        f"{VARIANTS + 1} queries took {elapsed:.2f}s — sequential would be "
        f"{BLOCK * (VARIANTS + 1):.1f}s")
