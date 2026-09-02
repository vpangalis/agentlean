"""`build_phase_subgraph(phase, llm)` — the one parameterised builder.

Canonical: reference **§58.11 — S-F02**. Architecture: §12 (topology), §13 (five
nodes), §15 (routing), §16 (where the checkpointer and store attach). Procedure
steps 4.1 (Define) and **4.4** (the other four).

**It takes `phase` as a parameter because it must select that phase's
computation-tool subset** (§30) — not because the topology varies. All five
phases have the same five nodes and the same edges; only the tool binding
differs, and that binding lands with `create_agent` in stage 6.

ONE BUILDER, NOT FIVE — AND WHY THIS FILE EXISTS
------------------------------------------------
Step 4.1 put `build_phase_subgraph` in `phases/define/graph.py`, where it
refused every phase but Define. Step 4.4's own words are *"same five-node
structure, **built from the parameterised builder**"*, and §12's is *"the
subgraph builder takes the phase as a parameter"* — singular. Copying it into
five files would give five topologies that must agree by hand, and §12's
"identical node-name sets" would become a convention rather than a fact.

**The alternative was for the four to import Define's builder**, and that is
worse than duplication: §12 says *"no subgraph imports another subgraph's
nodes"*, and while a builder is not a node, it would make Define structurally
special and put four phases' topology behind one phase's module. Hoisting it
here makes every phase a peer of every other.

**Each `phases/{phase}/graph.py` remains**, as Appendix B requires, and re-
exports this. That is the honest shape: the file exists, it is where a reader
looks for that phase's graph, and it contains no second copy of the wiring.

**Not in Appendix B's `New` file list** — flagged, the same call
`phases/mappers_common.py` and `phases/nodes_common.py` record.

THE COMPILE CARRIES NEITHER CHECKPOINTER NOR STORE
--------------------------------------------------
§16, and S-F02 B1. Both attach to the PARENT graph only; LangGraph routes a
subgraph's writes through the parent's saver under an auto-managed
`checkpoint_ns`. Passing either here is the violation §16 exists to name, and
`test_phase_subgraphs.py` asserts every one of the five carries neither.

THE ONLY STATIC EDGES ARE `START -> planner`, `executor -> planner` AND
`gate_review -> gate_apply`
-----------------------------------------------------------------------
Everything else is `Command` routing returned by the node itself (§15). The
distinction is load-bearing rather than terminological: **a node may not mix a
`Command` with a static edge out of the same node, because both paths would
execute, silently** (§15 C2). So `executor` has a static edge back to the
planner *and returns no Command*; `planner`, `validation_stack` and `gate_apply`
return Commands *and have no static edges out*.

`destinations=` declares each Command-routing node's possible targets. It is not
decoration: without it the compiled graph cannot report where those nodes can
go, and the topology stops being inspectable.
"""
from __future__ import annotations

import importlib
import logging
from types import ModuleType
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import TimeoutPolicy

from backend.core.substate import PhaseState
from backend.phases.mappers_common import PHASE_ORDER
from backend.phases.nodes_common import NODE_NAMES

logger = logging.getLogger(__name__)

#: §45 — the executor's wall-clock limit. `NodeTimeoutError` is what triggers
#: the fallback chain before the Belt notices the delay.
EXECUTOR_RUN_TIMEOUT = 45


def phase_nodes(phase: str) -> ModuleType:
    """Import one phase's `nodes.py`.

    **This is not a subgraph importing another subgraph's nodes** (§12). It is
    the builder importing the nodes of the phase it has been asked to build —
    one level up from the subgraphs, in the same position `core/graph.py` holds
    when it imports all five phases' mappers. The prohibition is on Measure's
    nodes reaching into Analyse's, and nothing here does that: each built
    subgraph sees only its own module.

    Imported by name rather than through a registry dict so that **no module
    imports all five nodes modules at once** — a registry would make every
    phase's nodes a load-time dependency of every other, which is the coupling
    §12 is guarding against even though it is not the letter of the rule.
    """
    if phase not in PHASE_ORDER:
        raise ValueError(
            f"Unknown phase {phase!r}; expected one of {', '.join(PHASE_ORDER)}."
        )
    return importlib.import_module(f"backend.phases.{phase}.nodes")


def build_phase_subgraph(phase: str, llm: Any = None):
    """Build and compile one phase subgraph. Returns a compiled `StateGraph`.

    `llm` is accepted and **unused**: the executor still delegates to the v1
    `orchestrate_{phase}`, which builds its own model through `core.llm.get_llm`
    (§4.1's factory rule). It is in the signature because S-F02 fixes the
    signature, and stage 6 passes it straight into `create_agent(model=llm, …)`.

    **Returns an already-compiled graph.** Procedure step 4.1's *Done when* read
    `build_phase_subgraph("define", llm).compile()`, which would compile twice;
    S-F02's own definition ends `return builder.compile()`, and that is what this
    follows.
    """
    nodes = phase_nodes(phase)
    builder = StateGraph(PhaseState)

    # ── the five nodes of §13 ─────────────────────────────────────────
    #
    # `destinations` mirrors each node's own `Command[Literal[...]]` return
    # annotation. Two statements of one fact, deliberately: the annotation is
    # what mypy checks, `destinations` is what the compiled graph reports.
    builder.add_node("planner", nodes.planner,
                     destinations=("executor", "validation_stack"))

    # B3 — the executor carries the §45 timeout. Its `error_handler` half is
    # NOT applied: `phase_error_recovery` does not exist in the codebase, and
    # the function it is specified to call,
    # `delete_or_flag_stale_in_case_index`, is itself an open spec gap (G-35).
    # Inventing either here would put a fabricated compensating action on the
    # one path that must be trustworthy. Owed at 8.2 — WATCH 16.
    builder.add_node("executor", nodes.executor,
                     timeout=TimeoutPolicy(run_timeout=EXECUTOR_RUN_TIMEOUT))

    builder.add_node("validation_stack", nodes.validation_stack,
                     destinations=("planner", "gate_review"))
    builder.add_node("gate_review", nodes.gate_review)
    builder.add_node("gate_apply", nodes.gate_apply,
                     destinations=("planner", END))

    # ── static edges — these three and no others (§15) ────────────────
    builder.add_edge(START, "planner")       # B1: never `set_entry_point`
    builder.add_edge("executor", "planner")  # the cycle §13 requires
    builder.add_edge("gate_review", "gate_apply")

    # B1 — NO checkpointer, NO store. Both attach to the parent only (§16).
    compiled = builder.compile()
    logger.info(
        "%s subgraph compiled: %d nodes, no checkpointer, no store",
        phase, len(NODE_NAMES),
    )
    return compiled


__all__ = ["build_phase_subgraph", "phase_nodes", "NODE_NAMES",
           "EXECUTOR_RUN_TIMEOUT"]
