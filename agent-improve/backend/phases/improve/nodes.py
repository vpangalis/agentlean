"""The five nodes of the Improve phase subgraph.

Canonical: reference **§13** (the five nodes), **§14** (the node contract),
**§15** (routing). Procedure step **4.4** — and 4.1/4.2 for Define, whose
corrected bodies these mirror.

**The bodies live in `phases/nodes_common.py`.** §13's five nodes are identical
across all five phases; they differ in the phase name, which
`orchestrate_improve` the executor delegates to, and which `validate_improve`
the validation stack calls. One copy of the logic means §47's key format, §34's
"do not validate a coaching turn" and the WATCH 7 seam hold in five places
rather than in the one they were written in.

**The five functions below are real module-level `async def`s and stay that
way.** §14 requires module-level async functions and `test_phase_subgraphs.py`
asserts `fn.__module__` is this module. Generating them in a factory would put
`__module__` on the common file, and satisfying the assertion would then mean
rewriting it to something untrue.

Improve's orchestrator builds a **cross-phase brief from Define,
Measure and Analyse** on every call, so it reads their `phase_inputs`
as well as its own.

WHAT IS NOT REAL YET, AND MUST NOT BE FAKED
-------------------------------------------
  * **`interrupt()` at `gate_review`** — §33, stage 7. Until it exists, reaching
    `END` does NOT mean the gate passed, so `gate_apply` applies nothing and the
    parent does not call the output mapper (DECISIONS Z2).
  * **The four validation layers** — §34, stage 7. `validation_stack` delegates
    to the v1 layer-2b validator and nothing else.
  * **DP1** — S-F13's real planner predicate. The `turn_count` predicate is a
    terminating placeholder and is NOT a behavioural approximation of it.

THE WATCH 7 SEAM
----------------
DECISIONS Part X (Route A): `orchestrate.py` keeps writing the v1 field names
until the v2 capture path lands, and is deleted at 11.1. So **`draft` is the v1
accumulator and `artifacts` stays empty** — putting v1 names into `artifacts`
would put them on the v2 gate path, which the ruling exists to prevent. **The
Improve gate is inert**: `validate_improve` requires the §39.x v2 names and the
orchestrator emits the v1 ones.

NODES MAY NOT WRITE `case_id` OR `current_phase`
------------------------------------------------
Both are copied down by the input mapper at phase entry and are READ-ONLY here
(S-C02 B9). No return dict below carries either key.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from backend.core.substate import PhaseState
from backend.phases import nodes_common as _c
from backend.phases.improve.validate import validate_improve

PHASE = "improve"


def step_key(turn_count: int, step_name: str) -> str:
    """This phase's deterministic `step_log` identity (§47 requirement 2)."""
    return _c.step_key(PHASE, turn_count, step_name)


async def planner(
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> Command[Literal["executor", "validation_stack"]]:
    """Produce the `CoachingPlan` and make the phase's ONE routing decision (§13)."""
    return await _c.planner(PHASE, state, config)


async def executor(
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> dict[str, Any]:
    """Run one coaching turn — `create_agent` + `CoachingResponse` (§18, §20).

    Step 6.2 removed the `orchestrate_improve` delegation. That module is now
    **dead code awaiting deletion at 11.1** (Route A) — unreferenced, and
    deliberately not migrated.
    """
    return await _c.executor(PHASE, state, config)


async def validation_stack(
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> Command[Literal["planner", "gate_review"]]:
    """The four layers, shared cap of 3 (§34) — layer 2b via `validate_improve`."""
    return await _c.validation_stack(PHASE, validate_improve, state, config)


async def gate_review(state: PhaseState) -> dict[str, Any]:
    """Present validated fields to the Belt and stop (§33)."""
    return await _c.gate_review(PHASE, state)


async def gate_apply(state: PhaseState) -> Command[Literal["planner", "__end__"]]:
    """Advisory, Belt edits, gate document, route on (§33)."""
    return await _c.gate_apply(PHASE, state)


__all__ = [
    "planner",
    "executor",
    "validation_stack",
    "gate_review",
    "gate_apply",
    "step_key",
    "PHASE",
]
