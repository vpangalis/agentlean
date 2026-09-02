"""The supervisor graph — what procedure step 4.3 established.

Step 4.3's *Done when* is three assertions: the parent has the five phase
subgraph nodes plus escalation, it compiles **with** checkpointer and store, and
each subgraph compiles with **neither**. Those are
`test_exactly_the_five_phases_plus_escalation`,
`test_the_parent_carries_both_persistence_primitives` and
`test_every_subgraph_compiles_with_neither`.

The rest pin what a later step could quietly undo, and each has a specific
failure it is guarding against:

  * **No conditional edge anywhere at Level 1.** `route_after_phase` was deleted
    on 2026-08-22 as a defect — it read `gate_attempts` off `SupervisorState`,
    where that field does not exist, so it would have raised `KeyError` on the
    gate-failure path specifically. §15 and S-F01 both say it MUST NOT be
    reinstated, and step 4.3's own prompt asks for "the conditional edge §3.5
    describes", which is the shape that would reinstate it. That makes this the
    most likely thing to come back.
  * **The escalation edge exists even though the drawing omits it.**
    `CompiledStateGraph.get_graph()` drops edges out of nodes unreachable from
    `START`, and `escalate` is unreachable until stage 7 raises the `Command`
    that reaches it — so a test reading the drawing would report the edge as
    missing when it is present. These read the BUILDER.
  * **`get_graph()` is still the one-turn parent**, deliberately. The static
    DMAIC chain is safe only once reaching `END` means the gate passed, and that
    is false until `gate_review` raises `interrupt()`. Swapping early would run
    the whole DMAIC sequence in one `/ask` turn.
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
    build_supervisor,
    supervisor_builder,
)

#: §12 — five phases plus escalation. A seventh needs a §56 amendment.
EXPECTED_NODES = {"define", "measure", "analyse", "improve", "control", "escalate"}

#: S-F01's definition block, plus `escalate -> END` which that block omits
#: because it does not draw the escalation node (§38: escalation never returns
#: to the supervisor).
EXPECTED_EDGES = {
    (START, "define"),
    ("define", "measure"),
    ("measure", "analyse"),
    ("analyse", "improve"),
    ("improve", "control"),
    ("control", END),
    (ESCALATE_NODE, END),
}


def _nodes(builder) -> set[str]:
    return {n for n in builder.nodes if n not in (START, END)}


# ── the step's Done-when ──────────────────────────────────────────────────

def test_exactly_the_five_phases_plus_escalation() -> None:
    """Step 4.3's *Done when*, first clause."""
    assert _nodes(supervisor_builder()) == EXPECTED_NODES


def test_the_parent_carries_both_persistence_primitives() -> None:
    """§16 B3 — and §1.1: "passing only a checkpointer is the most common
    architecture mistake"."""
    sup = build_supervisor()
    assert sup.checkpointer is not None, "no checkpointer on the parent"
    assert sup.store is not None, "no store on the parent — §1.1's named mistake"


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


# ── §15: the supervisor advances, it does not route ───────────────────────

def test_the_seven_static_edges_and_nothing_else() -> None:
    """S-F01's complete Level 1 wiring, edge for edge."""
    assert set(supervisor_builder().edges) == EXPECTED_EDGES


def test_the_phases_are_chained_in_dmaic_order() -> None:
    """§39: "Phase order is fixed and enforced by static edges. There is no
    skipping and no reordering"."""
    edges = set(supervisor_builder().edges)
    assert (START, PHASE_ORDER[0]) in edges
    for current, following in zip(PHASE_ORDER, PHASE_ORDER[1:]):
        assert (current, following) in edges, f"{current} -> {following} missing"
    assert (PHASE_ORDER[-1], END) in edges


def test_level_1_has_no_conditional_edge() -> None:
    """§15 and S-F01's invariants — `route_after_phase` MUST NOT return.

    A conditional edge here is not a style choice: the deleted router read
    `gate_attempts` off `SupervisorState`, which has seven fields and not that
    one, so it raised `KeyError` on the gate-failure path — the one path where a
    supervisor-level branch would matter.
    """
    builder = supervisor_builder()
    branches = getattr(builder, "branches", {}) or {}
    assert not branches, (
        f"Level 1 has conditional branches {sorted(branches)} — §15: "
        f"'there is no conditional edge, no router function, and nothing for "
        f"the supervisor to branch on'"
    )


def test_no_router_function_is_defined_in_the_module() -> None:
    """The deleted function, pinned out by name (DECISIONS §R2)."""
    assert not hasattr(graph_mod, "route_after_phase"), (
        "route_after_phase was deleted on 2026-08-22 and MUST NOT be reinstated"
    )
    assert not hasattr(graph_mod, "_gate_router"), (
        "the v1 per-phase gate router belongs to the deleted v1 graph"
    )


def test_gate_attempts_is_not_read_at_level_1() -> None:
    """§15 — it is read only inside a phase and is not on `SupervisorState`.

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


# ── §38: escalation is a node here and an edge one level down ─────────────

def test_escalation_is_a_node_that_never_returns_to_the_supervisor() -> None:
    """§38 — it defers to the Belt; its only edge is to END."""
    edges = set(supervisor_builder().edges)
    out = {t for s, t in edges if s == ESCALATE_NODE}
    assert out == {END}, f"escalate routes to {out}, not just END"


def test_the_escalation_edge_is_absent_from_the_drawing_and_present_in_the_wiring() -> None:
    """Guards a plausible misreading, not a defect.

    `get_graph()` omits edges out of nodes unreachable from START, and nothing
    reaches `escalate` until stage 7. A future reader checking the drawing will
    find the edge "missing"; this records why, and fails if the drawing ever
    starts including it — which would mean something now reaches escalation and
    this test should be replaced by a behavioural one.
    """
    drawn = {(e.source, e.target) for e in build_supervisor().get_graph().edges}
    assert (ESCALATE_NODE, END) not in drawn, (
        "escalate is now reachable from START — replace this test with one "
        "that exercises the path"
    )
    assert (ESCALATE_NODE, END) in set(supervisor_builder().edges)


def test_nothing_reaches_escalation_yet() -> None:
    """`validation_stack` is a pass-through until stage 7 and raises no Command.

    Pinned so that when stage 7 wires the escalation hop, this test fails and
    forces a real behavioural test in its place.
    """
    from backend.phases.define import nodes as define_nodes

    src = inspect.getsource(define_nodes.validation_stack)
    assert "Command.PARENT" not in src, (
        "validation_stack now escalates — replace this with a test that "
        "asserts the Command reaches the parent's escalate node"
    )


def test_escalate_node_reads_no_counter_off_parent_state() -> None:
    """The `route_after_phase` mistake, guarded at its most likely return site.

    `escalate.py`'s v1 report wants `gate_attempts` and `_missing_fields`;
    neither is on `SupervisorState`, and reaching for them here is how a
    `KeyError` on the escalation path gets written.
    """
    src = inspect.getsource(graph_mod.escalate_node)
    for banned in ("gate_attempts", "_missing_fields", "phase_inputs"):
        assert banned not in src.split('"""')[-1], (
            f"escalate_node reads {banned!r} off parent state"
        )


# ── the runtime is deliberately not the supervisor yet ────────────────────

def test_get_graph_is_still_the_one_turn_parent() -> None:
    """One `ainvoke` must remain one Belt turn until the gate interrupt lands.

    §15's static chain advances on `END`, and until `gate_review` raises
    `interrupt()` reaching `END` means only "the graph ran" — so the supervisor
    would run Define, Measure and Analyse in a single `/ask` turn. This is the
    guard on that swap happening early.
    """
    runtime = {n for n in graph_mod.get_graph().nodes if n not in (START, END)}
    assert runtime == {"define_phase"}, (
        "get_graph() is no longer the one-turn parent. If gate_review now "
        "raises interrupt(), this test should be deleted along with the "
        "get_graph body — see its docstring."
    )
    assert runtime != EXPECTED_NODES


def test_the_supervisor_and_the_runtime_are_different_graphs() -> None:
    """Stated so the two cannot be confused while both exist."""
    assert build_supervisor() is not graph_mod.get_graph()


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
