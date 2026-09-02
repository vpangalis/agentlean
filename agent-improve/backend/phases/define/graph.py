"""`build_phase_subgraph(phase, llm)` — the Define phase subgraph.

Canonical definition: reference **§58.11 — S-F02**. Architecture: §12
(topology), §13 (five nodes), §15 (routing), §16 (where the checkpointer and
store attach). Procedure step 4.1.

**It takes `phase` as a parameter because it must select that phase's
computation-tool subset** (§30) — not because the topology varies. All five
phases have the same five nodes; only the tool binding differs, and that
binding lands with `create_agent` in stage 6.

THE COMPILE CARRIES NEITHER CHECKPOINTER NOR STORE
--------------------------------------------------
§16, and S-F02 B1. Both attach to the PARENT graph only; LangGraph routes a
subgraph's writes through the parent's saver under an auto-managed
`checkpoint_ns`. Passing either here is the violation §16 exists to name, and
`test_define_graph.py` asserts the compiled graph carries neither.

THE ONLY STATIC EDGES ARE `START -> planner` AND `executor -> planner`
---------------------------------------------------------------------
Everything else is `Command` routing returned by the node itself (§15). The
distinction is load-bearing rather than terminological: **a node may not mix a
`Command` with a static edge out of the same node, because both paths would
execute, silently** (§15 C2). So `executor` has a static edge back to the
planner *and returns no Command*; `planner`, `validation_stack` and
`gate_apply` return Commands *and have no static edges out*.

`destinations=` declares each Command-routing node's possible targets. It is
not decoration: without it the compiled graph cannot report where those nodes
can go, and the topology stops being inspectable — which is most of what step
4.1 exists to establish.
"""
from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import TimeoutPolicy

from backend.core.substate import PhaseState
from backend.phases.define.nodes import (
    executor,
    gate_apply,
    gate_review,
    planner,
    validation_stack,
)

logger = logging.getLogger(__name__)

#: §13 — exactly these five, in this order. A sixth requires a §56 amendment.
#: `policy_advisory` and `revise` are BANNED names: the first is logic inside
#: `gate_apply`, the second is an edge.
NODE_NAMES: tuple[str, ...] = (
    "planner",
    "executor",
    "validation_stack",
    "gate_review",
    "gate_apply",
)

#: §45 — the executor's wall-clock limit. `NodeTimeoutError` is what triggers
#: the fallback chain before the Belt notices the delay.
EXECUTOR_RUN_TIMEOUT = 45


def build_phase_subgraph(phase: str, llm: Any = None):
    """Build and compile one phase subgraph. Returns a compiled `StateGraph`.

    `llm` is accepted and **unused at step 4.1**: the executor still delegates
    to the v1 `orchestrate_define`, which builds its own model through
    `core.llm.get_llm` (§4.1's factory rule). It enters the signature now
    because S-F02 fixes the signature, and stage 6 passes it straight into
    `create_agent(model=llm, ...)`.

    **Returns an already-compiled graph.** Procedure step 4.1's *Done when*
    reads `build_phase_subgraph("define", llm).compile()`, which would compile
    twice; S-F02's own definition ends `return builder.compile()`, and that is
    what this follows. Flagged rather than reconciled silently — see the step
    report.
    """
    if phase != "define":
        raise ValueError(
            f"Only the Define subgraph is built at procedure step 4.1; "
            f"got phase={phase!r}. Measure/Analyse/Improve/Control land at 4.4."
        )

    builder = StateGraph(PhaseState)

    # ── the five nodes of §13 ─────────────────────────────────────────
    #
    # `destinations` mirrors each node's own `Command[Literal[...]]` return
    # annotation. Two statements of one fact, deliberately: the annotation is
    # what mypy checks, `destinations` is what the compiled graph reports.
    builder.add_node("planner", planner,
                     destinations=("executor", "validation_stack"))

    # B3 — the executor carries the §45 timeout. Its `error_handler` half is
    # NOT applied: `phase_error_recovery` does not exist in the codebase, and
    # the function it is specified to call, `delete_or_flag_stale_in_case_index`,
    # is itself an open spec gap (G-35). Inventing either here would put a
    # fabricated compensating action on the one path that must be trustworthy.
    # Owed before any traffic routes here — see the step report.
    builder.add_node("executor", executor,
                     timeout=TimeoutPolicy(run_timeout=EXECUTOR_RUN_TIMEOUT))

    builder.add_node("validation_stack", validation_stack,
                     destinations=("planner", "gate_review"))
    builder.add_node("gate_review", gate_review)
    builder.add_node("gate_apply", gate_apply,
                     destinations=("planner", END))

    # ── static edges — these two and no others (§15) ──────────────────
    builder.add_edge(START, "planner")      # B1: never `set_entry_point`
    builder.add_edge("executor", "planner")  # the cycle §13 requires
    builder.add_edge("gate_review", "gate_apply")

    # B1 — NO checkpointer, NO store. Both attach to the parent only (§16).
    compiled = builder.compile()
    logger.info(
        "define subgraph compiled: %d nodes, no checkpointer, no store",
        len(NODE_NAMES),
    )
    return compiled


__all__ = ["build_phase_subgraph", "NODE_NAMES", "EXECUTOR_RUN_TIMEOUT"]
