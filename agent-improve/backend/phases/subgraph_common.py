"""`build_phase_subgraph(phase, llm)` — the one parameterised builder.

**It takes `phase` as a parameter because it must select that phase's
computation-tool subset** — not because the topology varies. All five phases
have the same five nodes and the same edges; only the tool binding differs.

ONE BUILDER, NOT FIVE
---------------------
Five copies would give five topologies that must agree by hand, and
"identical node-name sets" would be a convention rather than a fact. Having
the other four import Define's builder would be worse: no subgraph imports
another subgraph's nodes, and while a builder is not a node, it would make
Define structurally special and put four phases' topology behind one phase's
module. Hoisted here, every phase is a peer of every other.

**Each `phases/{phase}/graph.py` remains** and re-exports this: it is where a
reader looks for that phase's graph, and it contains no second copy of the
wiring.

THE COMPILE CARRIES NEITHER CHECKPOINTER NOR STORE
--------------------------------------------------
Both attach to the PARENT graph only; LangGraph routes a subgraph's writes
through the parent's saver under an auto-managed `checkpoint_ns`.
`test_phase_subgraphs.py` asserts every one of the five carries neither.

THE ONLY STATIC EDGES ARE `START -> planner`, `executor -> planner` AND
`gate_review -> gate_apply`
-----------------------------------------------------------------------
Everything else is `Command` routing returned by the node itself. The
distinction is load-bearing rather than terminological: **a node may not mix a
`Command` with a static edge out of the same node, because both paths would
execute, silently.** So `executor` has a static edge back to the planner *and
returns no Command*; `planner`, `validation_stack` and `gate_apply` return
Commands *and have no static edges out*.

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
from langgraph.types import RetryPolicy, TimeoutPolicy

from backend.core.substate import PhaseState
from backend.phases.mappers_common import PHASE_ORDER
from backend.phases.nodes_common import (
    EXECUTOR_RUN_TIMEOUT,
    NODE_NAMES,
    executor_timeout_handler,
)

logger = logging.getLogger(__name__)

#: T70 (DEF-078) — the planner's retries are LangGraph's: its one model judgment is a plain
#: structured-output call (no `ModelRetryMiddleware` around it), so a transient API failure
#: (rate limit, connection) retries the NODE — which writes nothing outside the state — with
#: backoff. `default_retry_on` does not retry programming errors.
PLANNER_RETRY = RetryPolicy(max_attempts=3, initial_interval=0.5, backoff_factor=2.0)


def phase_nodes(phase: str) -> ModuleType:
    """Import one phase's `nodes.py`.

    **This is not a subgraph importing another subgraph's nodes.** It is the
    builder importing the nodes of the phase it has been asked to build — one
    level up from the subgraphs, in the same position `core/graph.py` holds
    when it imports all five phases' mappers. The prohibition is on Measure's
    nodes reaching into Analyse's, and nothing here does that: each built
    subgraph sees only its own module.

    Imported by name rather than through a registry dict so that **no module
    imports all five nodes modules at once** — a registry would make every
    phase's nodes a load-time dependency of every other, which is the coupling
    the rule guards against even though it is not the letter of it.
    """
    if phase not in PHASE_ORDER:
        raise ValueError(
            f"Unknown phase {phase!r}; expected one of {', '.join(PHASE_ORDER)}."
        )
    return importlib.import_module(f"backend.phases.{phase}.nodes")


def build_phase_subgraph(phase: str, llm: Any = None):
    """Build and compile one phase subgraph. Returns a compiled `StateGraph`.

    `llm` is accepted and **unused**: the coach builds its own model through
    `core.llm.get_llm` (the factory rule). It stays in the signature because
    the builder's signature is fixed.

    **Returns an already-compiled graph** — callers do not compile it again.
    """
    nodes = phase_nodes(phase)
    builder = StateGraph(PhaseState)

    # ── the five nodes ────────────────────────────────────────────────
    #
    # `destinations` mirrors each node's own `Command[Literal[...]]` return
    # annotation. Two statements of one fact, deliberately: the annotation is
    # what mypy checks, `destinations` is what the compiled graph reports.
    builder.add_node("planner", nodes.planner, retry_policy=PLANNER_RETRY,
                     destinations=("executor", "validation_stack"))

    # T70 (DEF-078) — the executor's limit and its recovery are LangGraph's: the engine's wall,
    # and the error handler that composes the move's own reply when it fires (G-84: never a 500).
    builder.add_node("executor", nodes.executor,
                     timeout=TimeoutPolicy(run_timeout=EXECUTOR_RUN_TIMEOUT),
                     error_handler=executor_timeout_handler(phase))

    builder.add_node("validation_stack", nodes.validation_stack,
                     destinations=("planner", "gate_review"))
    builder.add_node("gate_review", nodes.gate_review)
    builder.add_node("gate_apply", nodes.gate_apply,
                     destinations=("planner", END))

    # ── static edges — these three and no others ──────────────────────
    builder.add_edge(START, "planner")       # never `set_entry_point`
    builder.add_edge("executor", "planner")  # the planner-executor cycle
    builder.add_edge("gate_review", "gate_apply")

    # NO checkpointer, NO store. Both attach to the parent only.
    compiled = builder.compile()
    logger.info(
        "%s subgraph compiled: %d nodes, no checkpointer, no store",
        phase, len(NODE_NAMES),
    )
    return compiled


__all__ = ["build_phase_subgraph", "phase_nodes", "NODE_NAMES",
           "EXECUTOR_RUN_TIMEOUT", "PLANNER_RETRY"]
