"""The five phase subgraphs — what procedure steps 4.1 and 4.4 established.

**Step 4.4's *Done when* is one parameterised test: all five compile with
identical node-name sets.** That is `test_all_five_compile_with_identical_node_
name_sets`. Everything else here runs over all five phases too, because the
whole point of 4.4 is that there is one topology and one set of node bodies —
a test that checked Define and trusted the rest would be checking the thing
least likely to be wrong.

This file was `test_define_graph.py` until 4.4. Every assertion in it was
already generic; only the parameterisation is new.

WHAT IS REAL, AND MUST NOT REGRESS
----------------------------------
  * five nodes per phase, named exactly as §13 names them, with the two banned
    names absent;
  * every node an `async def` **module-level** function in its own phase's
    module (§14) returning a dict slice or a `Command` — never a Pydantic
    model, never full state;
  * the planner owns the ONLY field/gate routing decision and the executor
    returns plainly (§17) — fusing them while leaving the node names intact is
    the failure §17 exists to prevent, and the hard one to see;
  * `Command` routing, never a conditional edge, and never mixed with a static
    edge out of the same node — both paths would execute, silently (§15 C2);
  * the planner's predicate **terminates** — the 4.1 version routed on
    `artifacts`, which the executor never writes, so the cycle ran until
    `GraphRecursionError`;
  * deterministic `step_log` keys at every write site (§47 requirement 2).

Not real yet, and each is marked at its site: the `CoachingPlan` type (S-C04,
6.1), `create_agent` with the tool subset (§18, stage 6), the four validation
layers (§34), the `interrupt()` (§33) and gate-document assembly (§33, S-F28).
"""
from __future__ import annotations

import ast
import asyncio
import importlib
import inspect
import pathlib
from typing import Any

import pytest
from langgraph.graph import END
from langgraph.types import Command

from backend.core.substate import CoachingPlan, PhaseState
from backend.phases.mappers_common import PHASE_ORDER
from backend.phases.subgraph_common import NODE_NAMES, build_phase_subgraph

#: §13. A sixth requires a §56 amendment.
EXPECTED = {"planner", "executor", "validation_stack", "gate_review", "gate_apply"}

#: §13 — retired, and neither may return as a node name. `policy_advisory` is
#: logic inside `gate_apply`; `revise` is an edge.
BANNED = {"policy_advisory", "revise"}


@pytest.fixture(scope="module")
def compiled() -> dict[str, Any]:
    """Every phase's compiled subgraph, built once."""
    return {phase: build_phase_subgraph(phase, llm=None) for phase in PHASE_ORDER}


def nodes_module(phase: str):
    return importlib.import_module(f"backend.phases.{phase}.nodes")


def graph_module(phase: str):
    return importlib.import_module(f"backend.phases.{phase}.graph")


def source_of(mod) -> str:
    """A module's source text. `__file__` is `str | None` on the type stubs, and
    a module without one is not something these tests can check."""
    assert mod.__file__ is not None, f"{mod.__name__} has no source file"
    return pathlib.Path(mod.__file__).read_text(encoding="utf-8")


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


def _node_names(graph) -> set[str]:
    return {n for n in graph.get_graph().nodes if n not in ("__start__", "__end__")}


def _run(coro):
    return asyncio.run(coro)


# ── step 4.4's Done-when ──────────────────────────────────────────────────

def test_all_five_compile_with_identical_node_name_sets(compiled) -> None:
    """**Step 4.4's *Done when*, stated as written.**

    One assertion over all five, not five assertions — the claim is that the
    sets are identical to each other, which five separate checks against a
    constant would not quite establish.
    """
    per_phase = {phase: _node_names(g) for phase, g in compiled.items()}
    assert set(per_phase) == set(PHASE_ORDER), "a phase failed to compile"
    assert len(set(map(frozenset, per_phase.values()))) == 1, per_phase
    assert next(iter(per_phase.values())) == EXPECTED


def test_the_node_names_constant_matches_every_compiled_graph(compiled) -> None:
    """The constant is what callers read; it must not drift from the build."""
    assert set(NODE_NAMES) == EXPECTED and len(NODE_NAMES) == 5
    for phase, graph in compiled.items():
        assert _node_names(graph) == set(NODE_NAMES), phase


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_neither_banned_node_name_appears(compiled, phase: str) -> None:
    assert _node_names(compiled[phase]) & BANNED == set()


# ── §16: both attach to the parent only ───────────────────────────────────

@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_compiles_with_no_checkpointer_and_no_store(compiled, phase: str) -> None:
    """S-F02 B1. Passing either here is the violation §16 exists to name."""
    assert compiled[phase].checkpointer is None
    assert compiled[phase].store is None


# ── §14: the node contract ────────────────────────────────────────────────

@pytest.mark.parametrize("phase", PHASE_ORDER)
@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_every_node_is_a_module_level_async_function(phase: str, name: str) -> None:
    """§14 — and each in ITS OWN phase's module, not the shared one.

    The bodies live in `phases/nodes_common.py`; these five are thin
    module-level `async def`s that delegate. If a future refactor generates them
    in a factory, `__module__` moves to the common file and this fails — which
    is the point: satisfying it by rewriting `__module__` would make the
    attribute say something untrue.
    """
    mod = nodes_module(phase)
    fn = getattr(mod, name)
    assert inspect.iscoroutinefunction(fn), f"{phase}.{name} must be async (§14)"
    assert fn.__module__ == mod.__name__, f"{phase}.{name} must be module-level"


@pytest.mark.parametrize("phase", PHASE_ORDER)
@pytest.mark.parametrize("kind", ["nodes", "graph"])
def test_node_and_graph_files_define_no_class(phase: str, kind: str) -> None:
    """§54: `phases/{phase}/nodes.py` and `graph.py` hold functions ONLY."""
    mod = nodes_module(phase) if kind == "nodes" else graph_module(phase)
    src = source_of(mod)
    classes = [n.name for n in ast.parse(src).body if isinstance(n, ast.ClassDef)]
    assert classes == [], f"{mod.__name__} defines {classes}"


def test_the_shared_modules_define_no_class() -> None:
    """The same rule for the two modules that hold the real bodies."""
    for name in ("backend.phases.nodes_common", "backend.phases.subgraph_common"):
        mod = importlib.import_module(name)
        src = source_of(mod)
        classes = [n.name for n in ast.parse(src).body
                   if isinstance(n, ast.ClassDef)]
        assert classes == [], f"{name} defines {classes}"


# ── §13 / §15: the topology, and who routes ───────────────────────────────

@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_topology_matches_section_13(compiled, phase: str) -> None:
    """The diagram in §13, edge for edge, for every phase."""
    edges = {(e.source, e.target) for e in compiled[phase].get_graph().edges}
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
    }, phase


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_executor_has_a_static_edge_out_and_no_conditional_one(
    compiled, phase: str
) -> None:
    """§15 C2 — a node may not mix a Command with a static edge; both would run.

    The executor returns plainly (§17): it decides no strategy, so its only exit
    is the static edge back to the planner.
    """
    out = [e for e in compiled[phase].get_graph().edges if e.source == "executor"]
    assert [(e.target, e.conditional) for e in out] == [("planner", False)], phase


@pytest.mark.parametrize("phase", PHASE_ORDER)
@pytest.mark.parametrize("name", ["planner", "validation_stack", "gate_apply"])
def test_routing_nodes_have_only_conditional_edges_out(
    compiled, phase: str, name: str
) -> None:
    """The converse of §15 C2: a Command-routing node has no static edge out."""
    out = [e for e in compiled[phase].get_graph().edges if e.source == name]
    assert out, f"{phase}.{name} has no outgoing edge"
    assert all(e.conditional for e in out), (
        f"{phase}.{name} mixes a static edge with its Command routing (§15 C2)"
    )


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_planner_owns_the_field_gate_decision(compiled, phase: str) -> None:
    """§17 — the split that fusing would erase while leaving the names intact."""
    targets = {
        e.target for e in compiled[phase].get_graph().edges if e.source == "planner"
    }
    assert targets == {"executor", "validation_stack"}, phase


# ── S-C02 B9: nodes may not write the two identity fields ─────────────────

IDENTITY = {"case_id", "current_phase"}


def _returned_update_keys(fn) -> set[str]:
    """Keys a node puts into state — from `return {...}` and `Command(update=…)`.

    AST rather than execution, so the executor (which would need a live LLM) is
    covered by the same check as the rest. Reads the SHARED body, since that is
    where the return dicts now live.
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
    """The copy-down invariant. Both are read-only inside the subgraph.

    Checked once on the shared body, which is where every phase's return dicts
    are built — the per-phase wrappers return the body's value unchanged.
    """
    from backend.phases import nodes_common

    written = _returned_update_keys(getattr(nodes_common, name))
    assert written & IDENTITY == set(), (
        f"{name} returns {written & IDENTITY} — read-only inside the subgraph "
        f"(S-C02 B9); the input mapper is the only writer"
    )


# ── the planner's predicate, per phase ────────────────────────────────────

@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_planner_returns_a_command_carrying_a_typed_plan(
    phase: str, stub_planner
) -> None:
    """Step 6.1 — a real `CoachingPlan`, not 4.4's stub dict.

    Read by ATTRIBUTE (S-C02 B7). The subscript form the stub required is what
    this replaces, so the assertion is deliberately `plan.focus_field` rather
    than `plan["focus_field"]` — the latter now raises, which is the point of
    typing it.
    """
    cmd = _run(nodes_module(phase).planner(_state(current_phase=phase)))
    assert isinstance(cmd, Command)
    assert cmd.goto == "executor"
    assert cmd.update is not None
    plan = cmd.update["coaching_plan"]
    assert isinstance(plan, CoachingPlan), "6.1 types the plan as S-C04"
    assert plan.focus_field and plan.next_action
    assert plan.retrieval_strategy in ("single_hop", "multi_hop")


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_planner_calls_the_planner_role_through_structured_output(
    phase: str, stub_planner
) -> None:
    """§17 — `planner` role at 0.1, and S-C04 B1 — structured output.

    **B1 is "never by parsing JSON from raw model text"**, which cannot be
    asserted by looking at a plan that came back well-formed: a parsed one
    would look identical. What makes it checkable is that the schema was handed
    to the model, so the fixture records it.
    """
    _run(nodes_module(phase).planner(_state(current_phase=phase)))
    assert stub_planner.roles == ["planner"]
    assert stub_planner.effective_temperature == 0.1
    assert stub_planner.schemas == [CoachingPlan]


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_planner_routes_to_the_gate_when_the_route_asked_for_it(
    phase: str, stub_planner
) -> None:
    """`entry="gate"` skips the executor. Placeholder, NOT DP1."""
    cmd = _run(nodes_module(phase).planner(
        _state(current_phase=phase), {"configurable": {"entry": "gate"}}
    ))
    assert cmd.goto == "validation_stack"
    assert cmd.update["step_log"][0]["route"] == "gate"


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_planner_leaves_the_cycle_after_one_coaching_turn(
    phase: str, stub_planner
) -> None:
    """The 4.1 predicate could not terminate; this is the fix, pinned.

    It routed on `artifacts`, which the executor never writes (WATCH 7 — it
    writes `draft`), so the planner/executor cycle ran until
    `GraphRecursionError`. `turn_count` is incremented by the executor, so the
    second pass leaves the cycle and one invoke is one Belt turn.
    """
    cmd = _run(nodes_module(phase).planner(_state(current_phase=phase, turn_count=1)))
    assert cmd.goto == "validation_stack"
    assert cmd.update["step_log"][0]["route"] == "close"


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_planner_spends_no_model_call_when_the_executor_is_not_next(
    phase: str, stub_planner
) -> None:
    """A plan is consumed by the executor and by nothing else.

    Producing one on the way to `validation_stack` would spend a premium call
    on a plan no node reads, and put a `focus_field` in the trace that never
    coached anything. The previous plan stands instead: B3 governs what a NEW
    plan does to the old one, not that one must be produced every visit.
    """
    for config in ({"configurable": {"entry": "gate"}}, None):
        state = _state(current_phase=phase,
                       turn_count=0 if config else 1)
        cmd = _run(nodes_module(phase).planner(state, config))
        assert cmd.goto == "validation_stack"
        assert "coaching_plan" not in (cmd.update or {})
    assert stub_planner.calls == 0, "the model was called with no consumer"


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_planner_does_not_route_on_artifacts(phase: str, stub_planner) -> None:
    """The 4.1 predicate, pinned as retired — `artifacts` stays empty until 6.2."""
    cmd = _run(nodes_module(phase).planner(
        _state(current_phase=phase, artifacts={"business_case": "x"})
    ))
    assert cmd.goto == "executor", (
        "routing on `artifacts` is the 4.1 predicate that could not terminate"
    )


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_planner_does_not_read_a_goto_out_of_next_action(
    phase: str, stub_planner
) -> None:
    """**G-01 stays open.** DP1 is founder-owned and 6.1 did not invent it.

    S-C04's `next_action` is the coaching move — "ask, challenge, show an
    example, run a computation" — not a routing verb. A planner that routed on
    it would close a founder-owned gap by implementation, and would do it by
    reading a field that does not mean that. So a plan whose `next_action` says
    "gate" must still route by the placeholder predicate.
    """
    stub_planner.plan = CoachingPlan(
        focus_field="business_case", next_action="gate",
        retrieval_strategy="single_hop", retrieval_hops=[],
    )
    cmd = _run(nodes_module(phase).planner(_state(current_phase=phase)))
    assert cmd.goto == "executor", (
        "the planner routed on the plan's next_action — that is DP1, and G-01 "
        "marks it 'to be designed with founder'"
    )


def test_analyse_is_the_one_phase_defaulting_to_multi_hop(stub_planner) -> None:
    """§28 — Analyse's root-cause validation is layered; the other four are not.

    **It is the DEFAULT offered to the planner, not an override applied to its
    answer.** S-C04 is explicit that the choice is the model's — "not restricted
    to Analyse — the planner may select multi_hop in any phase" — so this
    asserts the default reaches the prompt, and the next test asserts the
    model's answer is what actually lands on the plan.
    """
    prompts = {}
    for phase in PHASE_ORDER:
        stub_planner.prompts.clear()
        _run(nodes_module(phase).planner(_state(current_phase=phase)))
        prompts[phase] = stub_planner.prompts[0]

    assert 'is "multi_hop" by default' in prompts["analyse"]
    for phase in ("define", "measure", "improve", "control"):
        assert 'is "single_hop" by default' in prompts[phase], phase


def test_the_plans_strategy_is_the_models_answer_not_the_phase_default(
    stub_planner,
) -> None:
    """S-C04 — "the planner may select `multi_hop` in any phase".

    A per-phase constant that overrode the plan would make `retrieval_strategy`
    a lookup wearing a model's name, and §26's planned multi-hop would be
    unreachable in the four phases whose default is single-hop.
    """
    stub_planner.plan = CoachingPlan(
        focus_field="business_case", next_action="ask",
        retrieval_strategy="multi_hop",
        retrieval_hops=["what drives it?", "why does that happen?"],
    )
    cmd = _run(nodes_module("define").planner(_state(current_phase="define")))
    plan = cmd.update["coaching_plan"]
    assert plan.retrieval_strategy == "multi_hop", (
        "Define's single-hop DEFAULT overrode the planner's own choice"
    )
    assert len(plan.retrieval_hops) == 2


def test_single_hop_plans_carry_no_hops() -> None:
    """**S-C04 B2**, enforced on the model rather than at one call site.

    Normalises rather than raises: this runs on model output, and rejecting a
    plan for a stray hop list would fail the turn over something
    `retrieval_strategy` has already decided.
    """
    plan = CoachingPlan(
        focus_field="business_case", next_action="ask",
        retrieval_strategy="single_hop",
        retrieval_hops=["a hop the model should not have sent"],
    )
    assert plan.retrieval_hops == []


def test_the_planner_prompt_carries_the_phases_field_ledger(stub_planner) -> None:
    """The planner reads `artifacts` to derive what is next (§17).

    **`review_rows` is the ledger, not a second list built in the planner** —
    the same function §50's gate-review screen uses, so the planner and the
    screen cannot disagree about what the phase owes.
    """
    _run(nodes_module("define").planner(
        _state(current_phase="define", artifacts={"business_case": "stated"})
    ))
    prompt = stub_planner.prompts[0]
    assert "business_case  [captured]" in prompt
    assert "voc_summary  [missing]" in prompt
    assert "problem_statement  [missing]" in prompt


# ── the three pass-throughs ───────────────────────────────────────────────

@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_validation_stack_passes_through_on_a_coaching_turn(phase: str) -> None:
    """§34's cap of 3 must not be burned by a Belt who is still typing."""
    cmd = _run(nodes_module(phase).validation_stack(_state(current_phase=phase)))
    assert isinstance(cmd, Command) and cmd.goto == "gate_review"
    assert "gate_attempts" not in (cmd.update or {})


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_gate_apply_routes_to_end(phase: str) -> None:
    cmd = _run(nodes_module(phase).gate_apply(_state(current_phase=phase)))
    assert isinstance(cmd, Command) and cmd.goto == END


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_gate_review_returns_a_plain_dict_slice(phase: str) -> None:
    """It presents and stops; the approve/reject branch belongs to gate_apply."""
    out = _run(nodes_module(phase).gate_review(_state(current_phase=phase)))
    assert isinstance(out, dict) and not isinstance(out, Command)
    assert set(out) == {"step_log"}


# ── §47 requirement 2: deterministic step_log keys, every phase ───────────

@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_every_step_log_entry_is_deterministically_keyed(phase: str) -> None:
    """`f"{phase}:{turn_count}:{step_name}"`, no timestamps, all five phases."""
    mod = nodes_module(phase)
    for fn, name in (
        (mod.planner, "planner"),
        (mod.validation_stack, "validation_stack"),
        (mod.gate_review, "gate_review"),
        (mod.gate_apply, "gate_apply"),
    ):
        out = _run(fn(_state(current_phase=phase, turn_count=2)))
        update = out.update if isinstance(out, Command) else out
        assert isinstance(update, dict)
        entry = update["step_log"][0]
        assert entry["key"] == f"{phase}:2:{name}", entry
        assert entry["key"] == mod.step_key(2, name)
        assert entry["phase"] == phase


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_step_key_carries_no_clock_reading(phase: str) -> None:
    """The identity must be reproducible: same turn, same step, same key."""
    mod = nodes_module(phase)
    assert mod.step_key(3, "executor") == mod.step_key(3, "executor")
    assert mod.step_key(3, "executor") == f"{phase}:3:executor"


# ── the builder's own contract ────────────────────────────────────────────

def test_the_builder_is_one_function_shared_by_every_phase() -> None:
    """§12 — "the subgraph builder takes the phase as a parameter", singular.

    Each `phases/{phase}/graph.py` re-exports it; five copies would be five
    topologies that must agree by hand.
    """
    shared = build_phase_subgraph
    for phase in PHASE_ORDER:
        assert graph_module(phase).build_phase_subgraph is shared, phase


def test_the_builder_refuses_a_phase_that_is_not_a_dmaic_phase() -> None:
    with pytest.raises(ValueError, match="Unknown phase"):
        build_phase_subgraph("escalate", llm=None)


def test_llm_is_accepted_and_unused_at_this_step() -> None:
    """S-F02 fixes the signature now; stage 6 passes it into create_agent."""
    sig = inspect.signature(build_phase_subgraph)
    assert list(sig.parameters) == ["phase", "llm"]
    assert build_phase_subgraph("define", llm=object()) is not None


def test_no_subgraph_imports_another_subgraphs_nodes() -> None:
    """§12 — the prohibition, checked as a grep of every phase's own modules.

    Each phase's `nodes.py` may import its own `orchestrate`/`validate` and the
    shared bodies; reaching into a sibling phase is what this forbids.
    """
    for phase in PHASE_ORDER:
        others = [p for p in PHASE_ORDER if p != phase]
        for kind in ("nodes", "graph"):
            mod = nodes_module(phase) if kind == "nodes" else graph_module(phase)
            src = source_of(mod)
            for other in others:
                assert f"backend.phases.{other}" not in src, (
                    f"{phase}/{kind}.py imports from {other}"
                )
