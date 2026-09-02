"""The five node bodies, parameterised by phase — procedure step 4.4.

Canonical: reference **§13** (the five nodes), **§14** (the node contract),
**§15** (routing), **§34** (the validation stack). Architecture §17.

WHY A SHARED MODULE RATHER THAN FIVE COPIES
    §13's five nodes are **identical across all five phases**. They differ in
    exactly three places — the phase name, which `orchestrate_{phase}` the
    executor delegates to, and which `validate_{phase}` the validation stack
    calls — and nothing else. Written out five times that is five copies of the
    planner's routing table, five copies of the v1 bridge, and five copies of
    the deterministic `step_log` key.

    **`phases/mappers_common.py` exists for the same reason and states it
    plainly:** *"the twenty-first field would land in four of them."* The same
    applies here with more force, because these bodies carry live rules — §47's
    key format, §34's "do not validate a coaching turn", the WATCH 7 seam — and
    a rule enforced in four of five places is not enforced.

    **Not in Appendix B's `New` file list**, which enumerates
    `phases/{phase}/{graph,nodes,mappers}.py` and no common module. Flagged
    rather than assumed, the same call `mappers_common.py` records.

WHAT EACH PHASE'S `nodes.py` STILL OWNS
    Every phase keeps five real `async def`s at module level, because §14
    requires module-level async functions and `test_phase_subgraphs.py` asserts
    `fn.__module__` is that phase's module. They are two lines each and they
    delegate here. **That is deliberate rather than lazy**: generating the
    functions in a factory and assigning them would make `__module__` point at
    this file, and satisfying the §14 assertion would then mean rewriting the
    function's `__module__` to something it is not.

THE WATCH 7 SEAM APPLIES TO ALL FIVE PHASES NOW
    DECISIONS Part X (Route A): every `orchestrate_{phase}.py` keeps writing the
    v1 field names until its v2 capture path lands, and all five are deleted at
    step 11.1. So `draft` is the v1 accumulator for every phase and `artifacts`
    stays empty for every phase — putting v1 names into `artifacts` would put
    them on the v2 gate path, which the ruling exists to prevent.

    **The four gates beyond Define are inert for the same reason Define's is**:
    each `validate_{phase}` requires its §39.x v2 names and its orchestrator
    emits the v1 ones.
"""
from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Literal, Optional, cast

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END
from langgraph.types import Command

from backend.core.conversation import (
    V1_PRESENTATION_KEYS,
    message_to_turn,
    turn_to_message,
)
from backend.core.state import ImproveGraphState
from backend.core.substate import PhaseState

logger = logging.getLogger(__name__)

#: §13 — exactly these five, in this order, for every phase. A sixth requires a
#: §56 amendment. `policy_advisory` and `revise` are BANNED names.
NODE_NAMES: tuple[str, ...] = (
    "planner",
    "executor",
    "validation_stack",
    "gate_review",
    "gate_apply",
)

#: A node body's delegate: `orchestrate_{phase}` or `validate_{phase}`.
V1Node = Callable[[ImproveGraphState], Awaitable[dict[str, Any]]]


def step_key(phase: str, turn_count: int, step_name: str) -> str:
    """The deterministic `step_log` identity of one step of one turn.

    **§47 requirement 2** — ``f"{phase}:{turn_count}:{step_name}"``, never a raw
    timestamp as identity. An abandoned-then-retried turn re-executes the same
    logical step; a timestamp key records it as two events, a deterministic key
    records it as one. **Every `step_log` write site goes through here**, which
    is what makes the requirement checkable rather than a habit — and what makes
    it true for all five phases rather than for the one it was written in.
    """
    return f"{phase}:{turn_count}:{step_name}"


def _step(phase: str, turn_count: int, step_name: str,
          **fields: Any) -> dict[str, Any]:
    """One `step_log` entry, keyed deterministically. Dicts only — §10.3."""
    return {
        "key": step_key(phase, turn_count, step_name),
        "node": step_name,
        "phase": phase,
        **fields,
    }


def entry_mode(config: Optional[RunnableConfig]) -> str:
    """``"ask"`` (a coaching turn) or ``"gate"`` (a gate submission).

    Per-run intent, so it rides on `config` rather than on state — the same
    channel `thread_id` uses. **This is the stand-in for the Belt saying "I am
    ready for the gate" in conversation**, which is what DP1 will read at 6.1;
    it is a route-level signal only because the route-level distinction
    (`/ask` vs `/gate`) is what exists today.
    """
    return ((config or {}).get("configurable") or {}).get("entry", "ask")


# ── planner ───────────────────────────────────────────────────────────────

async def planner(
    phase: str,
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> Command[Literal["executor", "validation_stack"]]:
    """Produce the `CoachingPlan` and make the phase's ONE routing decision.

    §13: the planner fires many times per phase, not once. After each executor
    step control returns here to decide whether to keep coaching the current
    field, advance to the next, or trigger the gate.

    **The plan is a stub.** `PhaseState.coaching_plan` is annotated
    `Optional[dict[str, Any]]` because S-C04's `CoachingPlan` model does not
    land until step 6.1; §6 sanctions the dict as the interim annotation.

    **THE ROUTING PREDICATE IS A PLACEHOLDER, NOT DP1.** S-F13's DP1 reads the
    per-phase field ordering (§39.x's coached positions) to decide "field
    complete". What is here is the smallest rule that **terminates**:

    ==========  ==============  ===============  ==========================
    ``entry``   ``turn_count``  ``next_action``  goto
    ==========  ==============  ===============  ==========================
    ``gate``    any             ``gate``         validation_stack — validate
    ``ask``     0               ``coach``        executor — one coaching turn
    ``ask``     >0              ``close``        validation_stack — walk out
    ==========  ==============  ===============  ==========================

    `turn_count` is incremented by the executor and reset by the input mapper,
    so the `ask` path visits the executor **exactly once per invoke**. That is
    what makes one `ainvoke` one Belt turn.

    **The 4.1 predicate routed on `artifacts`, which the executor never writes**
    (WATCH 7 — it writes `draft`), so the cycle ran until `GraphRecursionError`.
    Step 4.2 fixed it for Define; parameterising the body here is what stops the
    fixed version and the broken one coexisting across five phases.
    """
    entry = entry_mode(config)
    turn_count = state.get("turn_count") or 0
    coached = turn_count > 0

    if entry == "gate":
        next_action, goto = "gate", "validation_stack"
    elif not coached:
        next_action, goto = "coach", "executor"
    else:
        next_action, goto = "close", "validation_stack"

    plan: dict[str, Any] = {
        "focus_field": None,          # S-F13 DP1 fills this from §39.x's order
        "next_action": next_action,
        "retrieval_strategy": _retrieval_strategy(phase),
        "tools_needed": [],
        "_stub": True,                # step 4.1 marker — 6.1 removes it
    }

    logger.info(
        "%s.planner: entry=%s turn_count=%d -> %s (%s)",
        phase, entry, turn_count, goto, next_action,
    )
    return Command(
        goto=cast(Literal["executor", "validation_stack"], goto),
        update={
            "coaching_plan": plan,
            "step_log": [_step(
                phase, turn_count, "planner",
                status="stub", goto=goto, next_action=next_action,
                reason="step 4.4 — DP1 lands at 6.1",
            )],
        },
    )


def _retrieval_strategy(phase: str) -> str:
    """§28's per-phase default, carried on the plan.

    **Analyse is the one phase that plans multi-hop** — root-cause validation is
    layered, so it is *"multi-hop, planned (3 hops)"* while the other four are
    single-hop by default. Recorded on the stub plan now because it is a
    per-phase fact the parameterised builder would otherwise flatten, and
    because `CoachingPlan.retrieval_strategy` is what selects the executor's
    entire retrieval path at stage 6. **Nothing reads it yet.**
    """
    return "multi_hop" if phase == "analyse" else "single_hop"


# ── the v1 bridge ─────────────────────────────────────────────────────────
#
# Everything from here to `executor` exists to be deleted with the five
# `orchestrate.py` files at step 11.1 (DECISIONS Part X, Route A).

def to_v1_state(
    phase: str,
    state: PhaseState,
    config: Optional[RunnableConfig],
) -> ImproveGraphState:
    """Bridge `PhaseState` to the v1 `ImproveGraphState` the orchestrator reads.

    **This is the WATCH 7 seam, and it is temporary by ruling.** The field-name
    mismatch it carries across is known and accepted: `artifacts` holds the v2
    names of §39.x while `orchestrate_{phase}` reads and writes the v1 ones,
    which is why `draft` and not `artifacts` is what it is handed.

    **`phase_inputs` carries EVERY phase, not just this one, and that is the
    change step 4.4 had to make.** Define is the only phase that reads its own
    inputs alone; Measure seeds its metric confirmations from Define's
    `primary_metric` / `secondary_metric`, and Analyse, Improve and Control each
    build a cross-phase brief from the phases before them. Handing them
    `{phase: draft}` — which is all the Define-only seam needed — would leave
    every brief empty and every upstream fact missing from the prompt, with no
    error anywhere. The full map arrives on `config` as `v1_phase_inputs`; this
    phase's entry is overlaid with `draft`, which is the live accumulator and so
    is newer than the case document's copy.
    """
    configurable = (config or {}).get("configurable") or {}
    messages = list(state.get("messages") or [])

    phase_inputs = {
        name: dict(values or {})
        for name, values in (configurable.get("v1_phase_inputs") or {}).items()
    }
    phase_inputs[phase] = dict(state.get("draft") or {})

    return {
        "case_id": state.get("case_id"),
        "current_phase": state.get("current_phase") or phase,
        "current_user": configurable.get("current_user"),
        "case_metadata": configurable.get("case_metadata") or {},
        "phase_inputs": phase_inputs,
        "chat_history": [message_to_turn(m, i) for i, m in enumerate(messages)],
        "gate_attempts": state.get("gate_attempts", 0),
        "citations": list(state.get("citations") or []),
    }


# ── executor ──────────────────────────────────────────────────────────────

async def executor(
    phase: str,
    orchestrate: V1Node,
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> dict[str, Any]:
    """Run one coaching turn. **Returns plainly — emits no routing `Command`.**

    §17: the executor consumes the plan and decides no strategy. Control returns
    to the planner on the static edge, and the planner chooses what happens next.

    This delegates to the v1 `orchestrate_{phase}` (step 4.1's choice for
    Define, extended to all five at 4.4). Stage 6 replaces the body with
    `create_agent(...)` bound to the universal seven plus that phase's
    computation tools (§18, §29, §30) and `response_format=CoachingResponse`.

    The coach's answer goes into `messages` as an `AIMessage`, carrying whatever
    presentational payloads that phase produces in `additional_kwargs` —
    `sipoc_diagram` is Define's alone, `visualisation` Define's and Measure's,
    `section_completed` every phase's. Absent ones are simply not attached.
    """
    turn_count = state.get("turn_count") or 0
    prior = list(state.get("messages") or [])

    result = await orchestrate(to_v1_state(phase, state, config))

    captured = (result.get("phase_inputs") or {}).get(phase, {})
    updated_history = result.get("chat_history") or []

    # The v1 orchestrator returns the WHOLE history with its reply appended.
    # Only the tail is new; `messages` reduces with `operator.add`, so returning
    # more than the tail would duplicate the conversation on every turn.
    new_turns = [dict(t) for t in updated_history[len(prior):]]
    for turn in new_turns:
        if turn.get("role") == "ai":
            for key in V1_PRESENTATION_KEYS:
                if result.get(key) is not None:
                    turn[key] = result[key]
    new_messages = [turn_to_message(t) for t in new_turns]

    logger.info(
        "%s.executor: v1 orchestrate returned %d field(s) into draft, "
        "%d new message(s)",
        phase, len(captured), len(new_messages),
    )
    return {
        "messages": new_messages,
        "draft": dict(captured),
        "turn_count": turn_count + 1,
        "step_log": [_step(
            phase, turn_count, "executor",
            status="delegated_v1", impl=f"orchestrate_{phase}",
            fields_in_draft=len(captured), new_messages=len(new_messages),
        )],
    }


# ── validation_stack ──────────────────────────────────────────────────────

async def validation_stack(
    phase: str,
    validate: V1Node,
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> Command[Literal["planner", "gate_review"]]:
    """The four layers, shared cap of 3 (§34). **Layer 2b only.**

    Stage 7 fills it: layer 2b field presence (deterministic), 2c constraints,
    2d `PHASE_RUBRIC` — cheapest first, each firing only if the previous passed.
    **Layer 2a is NOT here** — it is `CoherenceMiddleware` on `after_agent`,
    because it fires every coaching turn and this node runs once, at the gate.

    **It runs the validator only when the planner asked for the gate.** A
    coaching turn walks through here on its way out (`next_action == "close"`)
    and must NOT be validated: `validate_{phase}` increments `gate_attempts` on
    failure, so validating every coaching turn would burn the shared cap of 3 in
    three turns and escalate a Belt who is simply still typing. That is the §34
    cap firing on the wrong event, and it is worth stating because the node is
    on the path either way.

    On the gate path this delegates to the v1 `validate_{phase}` — the same
    WATCH 7 seam the executor uses, and the same ruling: `validate.py` is
    carried unchanged and the verdict is the one `/gate` returns today, on the
    same inputs. **All five gates stay inert**; nothing here makes them less so.

    `gate_attempts` is owned by `validate_{phase}` for the duration of the seam
    and is carried back onto `PhaseState` — where §6 says it belongs, and the
    fix for the v1 defect of holding it in route scope.
    """
    turn_count = state.get("turn_count") or 0
    plan = state.get("coaching_plan") or {}

    if plan.get("next_action") != "gate":
        logger.info("%s.validation_stack: pass-through (coaching turn)", phase)
        return Command(
            goto="gate_review",
            update={"step_log": [_step(
                phase, turn_count, "validation_stack",
                status="passthrough", next_action=plan.get("next_action"),
                reason="not a gate submission — layers 2c/2d land at stage 7",
            )]},
        )

    result = await validate(to_v1_state(phase, state, config))
    data = (result.get("phase_inputs") or {}).get(phase, {})
    passed = bool(data.get("_gate_passed"))
    missing = list(data.get("_missing_fields") or [])
    attempts = int(result.get("gate_attempts") or 0)
    escalated = bool(result.get("escalated"))

    logger.info(
        "%s.validation_stack: layer 2b %s (missing=%d, attempts=%d)",
        phase, "PASSED" if passed else "FAILED", len(missing), attempts,
    )
    return Command(
        goto="gate_review",
        update={
            "gate_attempts": attempts,
            # Accumulation is the point (§6): the shared cap of 3 is defensible
            # only because each attempt is better informed than the last.
            "validator_feedback": [{
                "key": step_key(phase, turn_count, "validation_stack"),
                "layer": "2b",
                "impl": f"validate_{phase}",
                "passed": passed,
                "missing": missing,
                "attempts": attempts,
                "escalated": escalated,
            }],
            "step_log": [_step(
                phase, turn_count, "validation_stack",
                status="validated_v1", layer="2b",
                passed=passed, missing=len(missing), attempts=attempts,
            )],
        },
    )


# ── gate_review ───────────────────────────────────────────────────────────

async def gate_review(phase: str, state: PhaseState) -> dict[str, Any]:
    """Present validated fields to the Belt and stop. **Logs only.**

    §33: this is where the graph-level `interrupt()` fires — never
    `HumanInTheLoopMiddleware`, which has two confirmed bugs on exactly this use
    case (§19). **No `interrupt()` is raised here yet**: §47 requirement 4 is
    ruled OUT until stage 7, and an `interrupt()` with no `/gate/approve` and
    `/gate/reject` resume routes (§49) would halt every turn with nothing able
    to resume it. Both land together.

    Returns plainly. The static edge carries control to `gate_apply`: presenting
    and applying are two moments of one gate, and the branch belongs to
    `gate_apply` (approve -> END, reject -> planner).
    """
    logger.info(
        "%s.gate_review: pass-through (interrupt() lands at stage 7)", phase
    )
    return {"step_log": [_step(
        phase, state.get("turn_count") or 0, "gate_review",
        status="passthrough", reason="step 4.4 — interrupt() lands at stage 7",
    )]}


# ── gate_apply ────────────────────────────────────────────────────────────

async def gate_apply(
    phase: str, state: PhaseState
) -> Command[Literal["planner", "__end__"]]:
    """Apply Belt edits, run the policy advisory, write the gate document, route on.

    **`policy_advisory` is logic here, not a node** — it is a BANNED node name
    (§13), because it runs after the Belt edits, when the coach is no longer in
    the loop. Likewise `revise`: revision is an *edge*, the one the validation
    stack takes back to the planner.

    **IT APPLIES NOTHING YET, AND THAT IS THE POINT.** Without the `interrupt()`
    at `gate_review`, reaching this node does not mean the Belt approved — it
    means the graph ran. §15's rule that "arriving at END means the gate passed"
    is a statement about the FINISHED subgraph and becomes true when stage 7
    lands the interrupt. Writing the gate document here now would commit a gate
    approval the Belt never saw, which is precisely the failure §47's ABANDON
    policy and §33's nine-step gate exist to prevent — so the parent's phase
    node does not call the output mapper either, and the two omissions are one
    decision (DECISIONS Z2).

    Stage 7 adds the two writes §33 requires — `store.put(("projects", case_id,
    "artifacts"), phase, doc)` **and** `final = doc` — which must both happen,
    because a crash between them would leave state and store disagreeing about
    whether the gate applied.

    **`gate_attempts` and `validator_feedback` reset here and only here** — the
    retry budget is per gate passage (§33). Not yet: the reset belongs with the
    approval, and there is no approval here to reset against.
    """
    logger.info(
        "%s.gate_apply: pass-through -> END (assembly lands at stage 7)", phase
    )
    return Command(
        goto=cast(Literal["planner", "__end__"], END),   # END == "__end__"
        update={"step_log": [_step(
            phase, state.get("turn_count") or 0, "gate_apply",
            status="passthrough",
            reason="step 4.4 — advisory, assembly and store write land at stage 7",
        )]},
    )


__all__ = [
    "NODE_NAMES",
    "V1Node",
    "step_key",
    "entry_mode",
    "to_v1_state",
    "planner",
    "executor",
    "validation_stack",
    "gate_review",
    "gate_apply",
]
