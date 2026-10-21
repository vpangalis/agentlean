"""The main graph — ADR-0063 (one compiled graph, entered at the current phase), T89, T90.

Pinned:
  * one builder, `graph_builder()`: five `{phase}_phase` wrapper nodes and `escalate`;
    `START` → `route_to_phase` (conditional) → the phase node → `END`; no phase-to-phase edge;
  * the compiled graph carries the checkpointer and store, and every subgraph neither;
  * `route_to_phase` is a pure function of `current_phase` — no model call, no other key;
  * `get_graph()` is that one graph, compiled once per process;
  * escalation is a node reached by `Command.PARENT`, never by an edge from a phase.
"""
from __future__ import annotations

import asyncio
import inspect
from typing import Any

import pytest
from langgraph.graph import END, START

from backend.core import graph as graph_mod
from backend.core.graph import (
    ESCALATE_NODE,
    PHASE_ORDER,
    RECURSION_LIMIT,
    graph_builder,
    route_to_phase,
)

PHASE_NODES = {f"{p}_phase" for p in PHASE_ORDER}


def test_exactly_the_five_phase_nodes_plus_escalation() -> None:
    nodes = set(graph_builder().nodes)
    # T29 (DEF-122): LangGraph registers each node's error_handler as a node of its own.
    handlers = {n for n in nodes if n.startswith("__error_handler__")}
    # ADR-0087: Define's approval node, entered by the gate path, has no error handler (T29 amended).
    assert nodes - handlers == PHASE_NODES | {ESCALATE_NODE, "input_guard", "define_approval"}
    assert handlers == {f"__error_handler__{n}" for n in PHASE_NODES | {"input_guard"}}


def test_the_one_graph_carries_both_persistence_primitives(monkeypatch) -> None:
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.store.memory import InMemoryStore

    saver, store = InMemorySaver(), InMemoryStore()
    monkeypatch.setattr(graph_mod, "_persistence", lambda: (saver, store))
    graph_mod.get_graph.cache_clear()
    try:
        g = graph_mod.get_graph()
        assert g.checkpointer is saver and g.store is store
        assert graph_mod.get_graph() is g, "get_graph compiled a second graph"
    finally:
        graph_mod.get_graph.cache_clear()


@pytest.mark.parametrize("phase", graph_mod.WIRED_PHASES)
def test_every_subgraph_compiles_with_neither(phase: str) -> None:
    """S-F02 B1 — each subgraph reaches the parent's through `checkpoint_ns`."""
    sub = graph_mod._subgraph(phase)
    assert sub.checkpointer is None, f"{phase} subgraph carries a checkpointer"
    assert sub.store is None, f"{phase} subgraph carries a store"


def test_an_unwired_phase_has_no_subgraph_until_4_4() -> None:
    """The four remaining subgraphs land at step 4.4; the node exists now."""
    for phase in PHASE_ORDER:
        if phase in graph_mod.WIRED_PHASES:
            continue
        with pytest.raises(graph_mod.PhaseNotWired, match="4.4"):
            graph_mod._subgraph(phase)


# ── ADR-0063: the entry is the case's current phase ───────────────────────

def test_start_enters_every_phase_node_through_the_router_and_every_phase_ends() -> None:
    b = graph_builder()
    # ADR-0087: Define's approval node, entered from the router on the gate path, ends too.
    assert set(b.edges) == ({(p, END) for p in PHASE_NODES} | {("define_approval", END)}
                            | {(ESCALATE_NODE, END), (START, "input_guard")}), b.edges
    branches = b.branches["input_guard"]            # ADR-0057: the guard sits before the router
    assert list(branches) == ["route_to_phase"]
    assert not {(a, z) for a, z in b.edges if a in PHASE_NODES and z in PHASE_NODES}


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_the_router_reads_current_phase_alone(phase: str) -> None:
    assert route_to_phase({"current_phase": phase}) == f"{phase}_phase"  # type: ignore[typeddict-item]


def test_a_turn_the_guard_blocked_ends_at_the_router() -> None:
    from langchain_core.messages import AIMessage
    blocked = AIMessage(content="no", additional_kwargs={"input_guard": {"status": "blocked"}})
    assert route_to_phase({"current_phase": "define", "messages": [blocked]}) == END  # type: ignore[typeddict-item]


def test_a_finished_case_has_no_phase_to_enter() -> None:
    with pytest.raises(graph_mod.PhaseNotWired):
        route_to_phase({"current_phase": "complete"})  # type: ignore[typeddict-item]


def test_there_is_one_builder() -> None:
    """T89 — `core/graph.py` constructs `StateGraph` once, in `graph_builder`; the routes call
    `get_graph()` and nothing else builds a parent graph."""
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path(graph_mod.__file__).read_text(encoding="utf-8"))
    sites = [f.name for f in tree.body if isinstance(f, ast.FunctionDef)
             for n in ast.walk(f) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "StateGraph"]
    assert sites == ["graph_builder"], sites
    assert not hasattr(graph_mod, "build_supervisor") and not hasattr(graph_mod, "supervisor_builder")


def test_gate_attempts_is_not_read_at_level_1() -> None:
    """It is read only inside a phase and is not on `SupervisorState` (the router reads
    `current_phase` alone).

    AST rather than text, because this module's own docstring QUOTES the banned
    expression in order to forbid it — a substring check fails on the very prose
    that documents the rule. (It did, on the first run.)
    """
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path(graph_mod.__file__).read_text(encoding="utf-8"))
    hits: list[str] = []
    for node in ast.walk(tree):
        # state["gate_attempts"]
        if (isinstance(node, ast.Subscript)
                and isinstance(node.value, ast.Name) and node.value.id == "state"
                and isinstance(node.slice, ast.Constant)
                and node.slice.value == "gate_attempts"):
            hits.append(f'state["gate_attempts"] line {node.lineno}')
        # state.get("gate_attempts", ...)
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "state"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == "gate_attempts"):
            hits.append(f'state.get("gate_attempts") line {node.lineno}')
    assert not hits, (
        f"Level 1 reads gate_attempts off parent state: {hits}. §15: it is read "
        f"only inside a phase and MUST NOT be added to SupervisorState — the "
        f"exact defect that made route_after_phase a KeyError."
    )


# ── escalation is a node, reached by Command.PARENT ───────────────────────

def test_escalation_ends_and_no_phase_edge_reaches_it() -> None:
    edges = set(graph_builder().edges)
    assert (ESCALATE_NODE, END) in edges
    assert not {a for a, z in edges if z == ESCALATE_NODE}


def test_recursion_limit_is_the_backstop_not_the_hop_cap() -> None:
    """§16 — 50 on the supervisor invocation; the hop budget is RemainingSteps."""
    assert RECURSION_LIMIT == 50


# ── the node contract ─────────────────────────────────────────────────────

@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_every_phase_node_is_async_and_uniquely_named(phase: str) -> None:
    """§14, and S-F10's execution site — the name drives `checkpoint_ns`."""
    node = graph_mod.phase_node(phase)
    assert inspect.iscoroutinefunction(node), f"{phase} node must be async"
    assert node.__name__ == phase


def test_every_phase_has_an_output_mapper() -> None:
    """ADR-0063 — the wrapper node runs it on approval."""
    assert set(graph_mod.OUTPUT_MAPPERS) == set(PHASE_ORDER)


def test_every_phase_has_an_input_mapper() -> None:
    """S-F10 / S-F12 — all ten mappers landed at step 3.3."""
    assert set(graph_mod.INPUT_MAPPERS) == set(PHASE_ORDER)


def test_the_escalation_node_is_async() -> None:
    assert inspect.iscoroutinefunction(graph_mod.escalate_node)


def test_module_defines_no_class() -> None:
    """§54 / CLAUDE.md §2 — `core/graph.py` holds module-level functions only.

    `PhaseNotWired` is the one permitted exception: an exception type is not
    state or behaviour, and the alternative is a bare `ValueError` the routes
    cannot distinguish from any other.
    """
    import ast
    import pathlib

    src = pathlib.Path(graph_mod.__file__).read_text(encoding="utf-8")
    classes = [n.name for n in ast.parse(src).body if isinstance(n, ast.ClassDef)]
    assert classes == ["PhaseNotWired"], f"core/graph.py defines {classes}"


# ── behaviour: the escalation hop is reachable in principle ───────────────

def test_command_parent_reaches_the_escalation_node() -> None:
    """The mechanism stage 7 will use, proven now rather than assumed.

    `Command.PARENT` is documented against a subgraph added AS A NODE, but
    S-F10 requires the subgraph to be invoked INSIDE the parent's node function.
    Whether the hop survives that was a real question; this answers it against
    the pinned LangGraph, and will fail loudly if a version bump changes it.

    Note what the assertion also proves: the phase node function's code AFTER
    the subgraph invoke does not run — the `ParentCommand` passes straight
    through it. That is why an escalated phase writes no gate document.
    """
    from typing import TypedDict

    from langgraph.graph import StateGraph as SG
    from langgraph.types import Command

    class Probe(TypedDict, total=False):
        """A minimal schema — the probe asserts routing, not state."""
        seen: list

    child_b = SG(Probe)
    child_b.add_node(
        "go",
        lambda s: Command(graph=Command.PARENT, goto="escalate"),
    )
    child_b.add_edge(START, "go")
    child = child_b.compile()

    ran: list[str] = []

    async def phase(state):
        await child.ainvoke({})
        ran.append("after_invoke")      # must NOT run
        return {}

    async def escalate(state):
        ran.append("escalate")
        return {}

    parent_b = SG(Probe)
    parent_b.add_node("define", phase)
    parent_b.add_node("escalate", escalate)
    parent_b.add_edge(START, "define")
    parent_b.add_edge("define", END)
    parent_b.add_edge("escalate", END)

    asyncio.run(parent_b.compile().ainvoke({}))
    assert ran == ["escalate"], (
        f"expected the Command to reach escalate and skip the rest of the "
        f"phase node; got {ran}"
    )


#: The calls by which a node function runs a compiled graph of its own: a phase subgraph, or the executor's agent.
_SUBGRAPH_CALLS = ("_subgraph(", "create_agent(", "agent.ainvoke(")


def _node_source(spec: Any) -> str:
    """A node function's source, with the shared `nodes_common` function it delegates to (`_c.<name>(`)."""
    import re

    from backend.phases import nodes_common
    fn = getattr(spec.runnable, "afunc", None) or getattr(spec.runnable, "func", None)
    try:
        source = inspect.getsource(fn) if fn is not None else ""
    except (OSError, TypeError):
        return ""
    for name in re.findall(r"(?<![\w.])_c\.(\w+)\(", source):
        if callable(shared := getattr(nodes_common, name, None)):
            source += inspect.getsource(shared)
    return source


def test_a_node_that_invokes_a_checkpointed_subgraph_carries_no_retry_policy(monkeypatch) -> None:
    """Graph rule §3.6 (founder ruling 2026-10-21, the D7 of the ADR-0087 retry escape): a node whose function invokes
    a checkpointed subgraph never carries a `retry_policy`. LangGraph issue #9253: a retry does not reset the task's
    subgraph call counter, so the retried call looks for its checkpoint under a new namespace and starts afresh —
    Define's approval re-ran as a coaching turn and the route answered "approved" with nothing saved. Review this
    rule when #9253 is fixed."""
    from langgraph.graph import StateGraph

    from backend.phases.subgraph_common import build_phase_subgraph
    builders: dict[str, Any] = {"parent": graph_builder()}
    real_compile = StateGraph.compile

    def capture(self, *a, **k):                                      # the subgraph builder compiles inside
        builders["define subgraph"] = self
        return real_compile(self, *a, **k)
    monkeypatch.setattr(StateGraph, "compile", capture)
    build_phase_subgraph("define")
    monkeypatch.setattr(StateGraph, "compile", real_compile)
    invoking = {(where, name): spec for where, b in builders.items() for name, spec in b.nodes.items()
                if any(call in _node_source(spec) for call in _SUBGRAPH_CALLS)}
    assert {("parent", "define_phase"), ("parent", "define_approval"), ("define subgraph", "executor")} <= set(invoking), \
        sorted(invoking)
    retried = sorted(f"{where}:{name}" for (where, name), spec in invoking.items() if spec.retry_policy)
    assert not retried, f"nodes that invoke a checkpointed subgraph carry a retry_policy (LangGraph #9253): {retried}"
