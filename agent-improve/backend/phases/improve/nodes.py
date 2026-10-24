"""The five nodes of the Improve phase subgraph.

**The bodies live in `phases/nodes_common.py`.** The five nodes are identical
across all five phases; they differ in the phase name and in which
`validate_improve` the validation stack calls. One copy of the logic means the
`step_log` key format and "do not validate a coaching turn" hold in all five
phases at once.

**The five functions below are real module-level `async def`s and stay that
way.** The node contract requires module-level async functions, and
`test_phase_subgraphs.py` asserts `fn.__module__` is this module. Generating
them in a factory would put `__module__` on the common file, and satisfying
the assertion would then mean rewriting it to something untrue.

WHAT IS A PLACEHOLDER, AND MUST NOT BE FAKED
--------------------------------------------
  * **The planner's routing predicate** is a terminating placeholder and is
    NOT a behavioural approximation of the real one (G-01).
  * **The validation stack** runs layer 2b (field presence, via
    `validate_improve`) only.
  * **Only Define's gate pauses for acceptance** (R6). Here `gate_review`
    and `gate_apply` pass through, so reaching `END` does NOT mean the
    gate passed.

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
from backend.phases.improve.validate import validate_improve

PHASE = "improve"


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
    """The three layers (2b–2d), shared cap of 3 — layer 2b via `validate_improve`."""
    return await _c.validation_stack(PHASE, validate_improve, state, config)


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
