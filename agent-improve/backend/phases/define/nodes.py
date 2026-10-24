"""The five nodes of the Define phase subgraph.

**The bodies live in `phases/nodes_common.py`.** The five nodes are identical
across all five phases; they differ in the phase name and
nothing else. One copy of the logic means the
`step_log` key format and "do not validate a coaching turn" hold in all five
phases at once.

**The five functions below are real module-level `async def`s and stay that
way.** The node contract requires module-level async functions, and
`test_phase_subgraphs.py` asserts `fn.__module__` is this module. Generating
them in a factory would put `__module__` on the common file, and satisfying
the assertion would then mean rewriting it to something untrue.

Define is the only phase that emits `sipoc_diagram`, and the only one
whose gate pauses for the Belt to accept a report (R6): once validation
has passed, `gate_review` calls `interrupt()` and `gate_apply` applies the
decision.

WHAT IS A PLACEHOLDER, AND MUST NOT BE FAKED
--------------------------------------------
  * **The planner's routing predicate** is a terminating placeholder and is
    NOT a behavioural approximation of the real one (G-01).
  * **The validation stack** runs layer 2b (field presence,
    `gate_registry.check_gate`) and, on a 2b pass, layer 2d (the rubric). Layer 2c
    is not built.

NODES MAY NOT WRITE `case_id` OR `current_phase`
------------------------------------------------
Both are copied down by the input mapper at phase entry and are READ-ONLY here.
No return dict below carries either key.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from backend.core.substate import PhaseState
from backend.phases import nodes_common as _c

PHASE = "define"


def step_key(turn_count: int, step_name: str) -> str:
    """This phase's deterministic `step_log` identity."""
    return _c.step_key(PHASE, turn_count, step_name)


async def planner(
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> Command[Literal["executor", "validation_stack"]]:
    """Produce the `CoachingPlan` and make the phase's ONE routing decision."""
    return await _c.planner(PHASE, state, config)


async def executor(
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> dict[str, Any]:
    """Run one coaching turn — `create_agent` + `CoachingResponse`."""
    return await _c.executor(PHASE, state, config)


async def validation_stack(
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> Command[Literal["planner", "gate_review"]]:
    """The three layers (2b–2d), shared cap of 3 — layer 2b via `gate_registry.check_gate`."""
    return await _c.validation_stack(PHASE, state, config)


async def gate_review(state: PhaseState) -> dict[str, Any]:
    """Present validated fields to the Belt and stop."""
    return await _c.gate_review(PHASE, state)


async def gate_apply(state: PhaseState) -> Command[Literal["planner", "__end__"]]:
    """Advisory, Belt edits, gate document, route on."""
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
