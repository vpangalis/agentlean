"""The Define phase subgraph — what procedure step 4.1 established.

The step's *Done when* is one assertion: the compiled graph has exactly the five
node names of §13. That is `test_exactly_the_five_nodes_of_13`. The rest pin the
structural facts around it that a later step could quietly break — the two
banned node names, the no-checkpointer/no-store compile, the planner-owns-the-
decision split, and the copy-down invariant.

These are structural. Behaviour is deliberately absent at 4.1 (the planner is a
stub, the executor delegates to v1, three nodes log and pass through), so there
is no behaviour to assert yet.
"""
from __future__ import annotations

import ast
import asyncio
import inspect
import pathlib
from typing import Any

import pytest

from langgraph.graph import END
from langgraph.types import Command

from backend.core.substate import PhaseState
from backend.phases.define import graph as graph_mod
from backend.phases.define import nodes as nodes_mod
from backend.phases.define.graph import NODE_NAMES, build_phase_subgraph

#: §13. A sixth requires a §56 amendment.
EXPECTED = {"planner", "executor", "validation_stack", "gate_review", "gate_apply"}

#: §13 — retired, and neither may return as a node name. `policy_advisory` is
#: logic inside `gate_apply`; `revise` is an edge.
BANNED = {"policy_advisory", "revise"}


@pytest.fixture(scope="module")
def compiled():
    return build_phase_subgraph("define", llm=None)


def _state(**overrides: object) -> PhaseState:
    """A complete `PhaseState`, so the nodes are called with what they declare.

    Partial dict literals type-check as `dict`, not as this TypedDict, and a
    node that reads a key the caller omitted would pass silently here and fail
    in the graph. Building the whole thing also means a §56 field addition
    breaks this helper first, which is where it should break.
    """
    base: PhaseState = {
        "case_id": "IMPR-TEST-001", "current_phase": "define",
        "messages": [], "history": [], "phase_context": "",
        "coaching_plan": None, "field_index": 0, "draft": {}, "artifacts": {},
        "step_log": [], "belt_edits": {}, "turn_count": 0, "final": {},
        "gate_attempts": 0, "validator_feedback": [], "rejection_feedback": [],
        "citations": [], "uploads": [], "hop_results": [],
        "synthesis_output": None,
    }
    base.update(overrides)  # type: ignore[typeddict-item]
    return base


def _node_names(compiled) -> set[str]:
    return {
        n for n in compiled.get_graph().nodes
        if n not in ("__start__", "__end__")
    }


# ── the step's Done-when ──────────────────────────────────────────────────

def test_exactly_the_five_nodes_of_13(compiled) -> None:
    """Procedure step 4.1's *Done when*, stated as written."""
    assert _node_names(compiled) == EXPECTED


def test_neither_banned_node_name_appears(compiled) -> None:
    assert _node_names(compiled) & BANNED == set()
    assert set(NODE_NAMES) & BANNED == set()


def test_node_names_constant_matches_the_compiled_graph(compiled) -> None:
    """The constant is what callers read; it must not drift from the build."""
    assert set(NODE_NAMES) == _node_names(compiled) == EXPECTED
    assert len(NODE_NAMES) == 5


# ── §16: both attach to the parent only ───────────────────────────────────

def test_compiles_with_no_checkpointer_and_no_store(compiled) -> None:
    """S-F02 B1. Passing either here is the violation §16 exists to name."""
    assert compiled.checkpointer is None
    assert compiled.store is None


# ── §14: the node contract ────────────────────────────────────────────────

@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_every_node_is_a_module_level_async_function(name: str) -> None:
    fn = getattr(nodes_mod, name)
    assert inspect.iscoroutinefunction(fn), f"{name} must be async (§14)"
    assert fn.__module__ == nodes_mod.__name__, f"{name} must be module-level"


@pytest.mark.parametrize("mod", [nodes_mod, graph_mod],
                         ids=["nodes", "graph"])
def test_node_and_graph_files_define_no_class(mod) -> None:
    """§54: `phases/{phase}/nodes.py` and `graph.py` hold functions ONLY."""
    src = pathlib.Path(mod.__file__).read_text(encoding="utf-8")
    classes = [n.name for n in ast.parse(src).body if isinstance(n, ast.ClassDef)]
    assert classes == [], f"{mod.__name__} defines {classes}"


# ── §13 / §15: the topology, and who routes ───────────────────────────────

def test_topology_matches_section_13(compiled) -> None:
    """The diagram in §13, edge for edge."""
    edges = {(e.source, e.target) for e in compiled.get_graph().edges}
    assert edges == {
        ("__start__", "planner"),           # static — B1, never set_entry_point
        ("planner", "executor"),            # Command — S-F13 DP1
        ("planner", "validation_stack"),    # Command — S-F13 DP1
        ("executor", "planner"),            # static — the cycle
        ("validation_stack", "gate_review"),
        ("validation_stack", "planner"),    # fail -> planner with feedback
        ("gate_review", "gate_apply"),
        ("gate_apply", "__end__"),          # approve
        ("gate_apply", "planner"),          # reject -> planner with feedback
    }


def test_executor_has_a_static_edge_out_and_no_conditional_one(compiled) -> None:
    """§15 C2 — a node may not mix a Command with a static edge; both would run.

    The executor returns plainly (§17): it decides no strategy, so its only exit
    is the static edge back to the planner.
    """
    out = [e for e in compiled.get_graph().edges if e.source == "executor"]
    assert [(e.target, e.conditional) for e in out] == [("planner", False)]


@pytest.mark.parametrize("name", ["planner", "validation_stack", "gate_apply"])
def test_routing_nodes_have_only_conditional_edges_out(compiled, name: str) -> None:
    """The converse of §15 C2: a Command-routing node has no static edge out."""
    out = [e for e in compiled.get_graph().edges if e.source == name]
    assert out, f"{name} has no outgoing edge"
    assert all(e.conditional for e in out), (
        f"{name} mixes a static edge with its Command routing (§15 C2)"
    )


def test_planner_owns_the_field_gate_decision(compiled) -> None:
    """§17 — the split that fusing would erase while leaving the names intact."""
    targets = {
        e.target for e in compiled.get_graph().edges if e.source == "planner"
    }
    assert targets == {"executor", "validation_stack"}


# ── S-C02 B9: nodes may not write the two identity fields ─────────────────

IDENTITY = {"case_id", "current_phase"}


def _returned_update_keys(fn) -> set[str]:
    """Keys a node puts into state — from `return {...}` and `Command(update=…)`.

    AST rather than execution, so the executor (which would need a live LLM) is
    covered by the same check as the rest.
    """
    tree = ast.parse(inspect.getsource(fn))
    keys: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
            keys |= {k.value for k in node.value.keys
                     if isinstance(k, ast.Constant) and isinstance(k.value, str)}
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "Command":
            for kw in node.keywords:
                if kw.arg == "update" and isinstance(kw.value, ast.Dict):
                    keys |= {k.value for k in kw.value.keys
                             if isinstance(k, ast.Constant)
                             and isinstance(k.value, str)}
    return keys


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_no_node_writes_case_id_or_current_phase(name: str) -> None:
    """The copy-down invariant. Both are read-only inside the subgraph."""
    written = _returned_update_keys(getattr(nodes_mod, name))
    assert written & IDENTITY == set(), (
        f"{name} returns {written & IDENTITY} — read-only inside the subgraph "
        f"(S-C02 B9); the input mapper is the only writer"
    )


# ── the three pass-throughs actually route where §13 says ─────────────────

def _run(coro):
    return asyncio.run(coro)


def test_planner_returns_a_command_carrying_a_stub_plan() -> None:
    cmd = _run(nodes_mod.planner(_state()))
    assert isinstance(cmd, Command)
    assert cmd.goto == "executor"
    assert cmd.update is not None
    plan = cmd.update["coaching_plan"]
    assert plan["_stub"] is True, "4.1's plan is a stub; 6.1 types it as S-C04"
    assert plan["retrieval_strategy"] == "single_hop", "§28 — Define never multi-hops"


def test_planner_routes_to_the_gate_when_the_route_asked_for_it() -> None:
    """`entry="gate"` skips the executor. Placeholder, NOT DP1 (step 4.2)."""
    cmd = _run(nodes_mod.planner(
        _state(), {"configurable": {"entry": "gate"}}
    ))
    assert cmd.goto == "validation_stack"
    assert cmd.update["coaching_plan"]["next_action"] == "gate"


def test_planner_leaves_the_cycle_after_one_coaching_turn() -> None:
    """The 4.1 predicate could not terminate; this is the fix, pinned.

    The 4.1 planner routed on `artifacts`, which the executor never writes
    (WATCH 7 — it writes `draft`), so the planner/executor cycle ran until
    `GraphRecursionError`. `turn_count` is incremented by the executor, so the
    second pass leaves the cycle and one invoke is one Belt turn.
    """
    cmd = _run(nodes_mod.planner(_state(turn_count=1)))
    assert cmd.goto == "validation_stack"
    assert cmd.update["coaching_plan"]["next_action"] == "close"


def test_planner_does_not_route_on_artifacts() -> None:
    """The 4.1 predicate, pinned as retired — `artifacts` stays empty until 6.2."""
    cmd = _run(nodes_mod.planner(_state(artifacts={"business_case": "x"})))
    assert cmd.goto == "executor", (
        "routing on `artifacts` is the 4.1 predicate that could not terminate"
    )


def test_every_step_log_entry_is_deterministically_keyed() -> None:
    """§47 requirement 2 — `f\"{phase}:{turn_count}:{step_name}\"`, no timestamps."""
    calls: list[tuple[Any, str]] = [
        (nodes_mod.planner, "planner"),
        (nodes_mod.validation_stack, "validation_stack"),
        (nodes_mod.gate_review, "gate_review"),
        (nodes_mod.gate_apply, "gate_apply"),
    ]
    for fn, name in calls:
        out = _run(fn(_state(turn_count=2)))
        update = out.update if isinstance(out, Command) else out
        assert isinstance(update, dict)
        entry = update["step_log"][0]
        assert entry["key"] == f"define:2:{name}", entry
        assert entry["key"] == nodes_mod.step_key(2, name)


def test_step_key_carries_no_clock_reading() -> None:
    """The identity must be reproducible: same turn, same step, same key."""
    assert nodes_mod.step_key(3, "executor") == nodes_mod.step_key(3, "executor")
    assert nodes_mod.step_key(3, "executor") == "define:3:executor"


def test_validation_stack_passes_through_to_gate_review() -> None:
    cmd = _run(nodes_mod.validation_stack(_state()))
    assert isinstance(cmd, Command) and cmd.goto == "gate_review"


def test_gate_apply_routes_to_end() -> None:
    cmd = _run(nodes_mod.gate_apply(_state()))
    assert isinstance(cmd, Command) and cmd.goto == END


def test_gate_review_returns_a_plain_dict_slice() -> None:
    """It presents and stops; the approve/reject branch belongs to gate_apply."""
    out = _run(nodes_mod.gate_review(_state()))
    assert isinstance(out, dict) and not isinstance(out, Command)
    assert set(out) == {"step_log"}


def test_validation_stack_does_not_fabricate_a_gate_attempt() -> None:
    """The counter increments once at entry — when the layers exist (§34)."""
    cmd = _run(nodes_mod.validation_stack(_state(gate_attempts=0)))
    assert cmd.update is not None
    assert "gate_attempts" not in cmd.update


# ── the builder's own contract ────────────────────────────────────────────

def test_builder_refuses_a_phase_it_does_not_build() -> None:
    """Only Define exists at 4.1; the other four land at step 4.4."""
    with pytest.raises(ValueError, match="step 4.1"):
        build_phase_subgraph("measure", llm=None)


def test_llm_is_accepted_and_unused_at_this_step() -> None:
    """S-F02 fixes the signature now; stage 6 passes it into create_agent."""
    sig = inspect.signature(build_phase_subgraph)
    assert list(sig.parameters) == ["phase", "llm"]
    assert build_phase_subgraph("define", llm=object()) is not None
