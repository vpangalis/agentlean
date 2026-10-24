"""Control's phase subgraph.

**The wiring lives in `phases/subgraph_common.py`**: one parameterised
builder, because all five phases have the same five nodes and the same edges,
and only the computation-tool subset differs. Five copies of the topology
would be five things that must agree by hand, and "identical node-name sets"
would become a convention instead of a fact.

This module is where a reader looks for Control's graph. It holds no second copy
of the wiring.

**Compiled with neither checkpointer nor store** — both attach to the parent
graph only, and LangGraph routes this subgraph's writes through the parent's
saver under an auto-managed `checkpoint_ns`.
"""
from __future__ import annotations

from backend.phases.subgraph_common import (
    EXECUTOR_RUN_TIMEOUT,
    NODE_NAMES,
    build_phase_subgraph,
)

PHASE = "control"

__all__ = [
    "build_phase_subgraph",
    "NODE_NAMES",
    "EXECUTOR_RUN_TIMEOUT",
    "PHASE",
]
