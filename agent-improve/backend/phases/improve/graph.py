"""Improve's phase subgraph.

Canonical: reference **§58.11 — S-F02**. Architecture: §12 (topology), §13 (five
nodes), §15 (routing), §16 (where the checkpointer and store attach). Procedure
step **4.4** — 4.1 for Define.

**The wiring lives in `phases/subgraph_common.py`.** §12 specifies *one*
parameterised builder — *"the subgraph builder takes the phase as a
parameter"* — because all five phases have the same five nodes and the same
edges, and only the computation-tool subset differs (§30). Five copies of the
topology would be five things that must agree by hand, and §12's "identical
node-name sets" would become a convention instead of a fact.

This module exists because Appendix B's file list names it and because it is
where a reader looks for Improve's graph. It holds no second copy of the wiring.

**Compiled with neither checkpointer nor store** (§16, S-F02 B1) — both attach
to the parent graph only, and LangGraph routes this subgraph's writes through
the parent's saver under an auto-managed `checkpoint_ns`.
"""
from __future__ import annotations

from backend.phases.subgraph_common import (
    EXECUTOR_RUN_TIMEOUT,
    NODE_NAMES,
    build_phase_subgraph,
)

PHASE = "improve"

__all__ = [
    "build_phase_subgraph",
    "NODE_NAMES",
    "EXECUTOR_RUN_TIMEOUT",
    "PHASE",
]
