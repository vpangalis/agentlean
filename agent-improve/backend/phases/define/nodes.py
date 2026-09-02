"""The five nodes of the Define phase subgraph.

Canonical definition: reference **§13** (the five nodes), **§14** (the node
contract), **§15** (routing). Procedure steps 4.1 (topology) and 4.2 (traffic).

WHAT CHANGED AT 4.2, AND WHY IT HAD TO
--------------------------------------
Step 4.1 built these five nodes structurally correct and behaviourally minimal
and **routed no traffic to them**. Step 4.2 is the step that routes traffic, and
routing traffic through a topology is what proves it runs. Three things were
latent at 4.1 and are fixed here, none of them optional:

  1. **The planner/executor cycle did not terminate.** The 4.1 planner routed
     ``"executor" if not artifacts else "validation_stack"``, and the executor
     writes ``draft``, never ``artifacts`` (deliberately — WATCH 7). So
     ``artifacts`` stayed ``{}``, the planner routed to the executor forever,
     and a real invoke would have died on ``GraphRecursionError`` at the §16
     backstop of 50. It was invisible at 4.1 because the only caller was a test
     that seeded ``artifacts`` by hand. The predicate is now ``turn_count``-
     based: **one invoke is one coaching turn**, which is the boundary the
     procedure's own ordering note says 4.2 exists to establish.
  2. **The v1 bridge dropped everything the route returns.** The 4.1 executor
     kept only the captured fields and discarded the coach's answer, the SIPOC
     payload, the visualisation and the section-completion marker. Routing
     ``/ask`` through the graph with that bridge would have returned an empty
     answer to the Belt.
  3. **`_to_v1_state` could not run.** It passed ``PhaseState.history`` — the
     ``list[str]`` breadcrumb trail — as v1's ``chat_history``, which is a list
     of turn dicts; ``orchestrate_define`` calls ``.get("role")`` on each
     element, so every turn would have raised ``AttributeError`` on a ``str``.
     It also omitted ``case_metadata`` and ``current_user``, which frame the
     coaching prompt.

THE WATCH 7 SEAM, RESTATED
--------------------------
DECISIONS.md Part X (Route A): ``orchestrate.py`` keeps writing the v1 field
names, unchanged, until the executor's own capture path lands at step 6.2, and
is deleted at 11.1. Two consequences are load-bearing here:

  * **``draft`` is the v1 accumulator** for the duration of the seam, and
    ``artifacts`` stays empty. ``draft`` is ``PhaseState``'s "this turn's
    extraction" field and the v1 running extraction is exactly that; putting v1
    names into ``artifacts`` would put them on the v2 gate path, which the
    ruling exists to prevent. Step 6.2 moves capture into ``artifacts`` through
    ``CoachingResponse.fields_captured`` and this seam is deleted with it.
  * **The Define gate stays inert.** ``validate_define`` requires the §39.1.2
    v2 names; the v1 writer emits the v1 ones. Wiring the real validator into
    ``validation_stack`` below does not make the gate pass — it preserves
    exactly the verdict ``/gate`` returns today, on the same inputs, through
    the graph instead of through a dispatch table in the route.

WHY `case_metadata` AND `current_user` ARRIVE ON `config`, NOT ON STATE
----------------------------------------------------------------------
``PhaseState`` is twenty-one declared fields and **a twenty-second requires a
§56 amendment** — so the case framing the v1 orchestrator needs cannot be added
as a field. It does not want to be one either: it is immutable per-run framing,
which is what ``config["configurable"]`` is for, and this codebase already
reads ``thread_id`` from exactly there (``core/checkpointer.py``). Nothing here
invents a mechanism; it uses the one already in service. At stage 6 the framing
reaches the coach as ``phase_context`` through ``before_agent`` injection
(§8.5) and these two ``configurable`` keys go away with the seam.

WHAT IS STILL NOT REAL, AND MUST NOT BE FAKED
---------------------------------------------
  * **``interrupt()`` at ``gate_review``** — §33, stage 7. Until it exists
    there is no turn boundary inside the subgraph, so ``gate_apply`` **applies
    nothing**: it writes no gate document and advances no phase. Reaching
    ``END`` at 4.2 does NOT mean the gate passed, which is why the parent node
    does not call ``define_output_mapper`` (see ``core/graph.py``).
  * **The four validation layers** — §34, stage 7. ``validation_stack``
    delegates to the v1 layer-2b validator and nothing else.
  * **DP1** — S-F13's real planner predicate reads §39.1.2's field ordering.
    The ``turn_count`` predicate below is a terminating placeholder and is NOT
    a behavioural approximation of it.

NODES MAY NOT WRITE `case_id` OR `current_phase`
------------------------------------------------
Both are copied down by the input mapper at phase entry and are READ-ONLY here
(S-C02 B9). ``SupervisorState.current_phase`` keeps its single writer, the
output mapper. No return dict below carries either key, and
``test_define_graph.py`` pins that.
"""
from __future__ import annotations

import logging
from typing import Any, Literal, Optional, cast

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
from backend.phases.define.orchestrate import orchestrate_define
from backend.phases.define.validate import validate_define

logger = logging.getLogger(__name__)

PHASE = "define"


def step_key(turn_count: int, step_name: str) -> str:
    """The deterministic `step_log` identity of one step of one turn.

    **§47 requirement 2** — ``f"{phase}:{turn_count}:{step_name}"``, never a raw
    timestamp as identity. An abandoned-then-retried turn re-executes the same
    logical step; a timestamp key records it as two events, a deterministic key
    records it as one. **Every `step_log` write site in this module goes through
    here**, which is what makes the requirement checkable rather than a habit.
    """
    return f"{PHASE}:{turn_count}:{step_name}"


def _step(turn_count: int, step_name: str, **fields: Any) -> dict[str, Any]:
    """One `step_log` entry, keyed deterministically. Dicts only — §10.3."""
    return {
        "key": step_key(turn_count, step_name),
        "node": step_name,
        "phase": PHASE,
        **fields,
    }


def _entry_mode(config: Optional[RunnableConfig]) -> str:
    """``"ask"`` (a coaching turn) or ``"gate"`` (a gate submission).

    Per-run intent, so it rides on ``config`` rather than on state — the same
    channel ``thread_id`` uses. **This is 4.2's stand-in for the Belt saying "I
    am ready for the gate" in conversation**, which is what DP1 will read at
    6.1; it is a route-level signal only because the route-level distinction
    (``/ask`` vs ``/gate``) is what exists today.
    """
    return ((config or {}).get("configurable") or {}).get("entry", "ask")


# ── planner ───────────────────────────────────────────────────────────────

async def planner(
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> Command[Literal["executor", "validation_stack"]]:
    """Produce the `CoachingPlan` and make the phase's ONE routing decision.

    §13: the planner fires many times per phase, not once. After each executor
    step control returns here to decide whether to keep coaching the current
    field, advance to the next, or trigger the gate.

    **The plan is a stub at 4.2.** ``PhaseState.coaching_plan`` is annotated
    ``Optional[dict[str, Any]]`` because S-C04's ``CoachingPlan`` model does not
    land until step 6.1; §6 sanctions the dict as the interim annotation. The
    keys below are the shape S-C04 will type, so the swap is a type change
    rather than a rewrite.

    **THE ROUTING PREDICATE IS A PLACEHOLDER, NOT DP1.** S-F13's DP1 reads the
    per-phase field ordering (§39.1.2's twelve coached positions) to decide
    "field complete". That predicate lands with the real planner at 6.1. What is
    here is the smallest rule that **terminates**, which the 4.1 predicate did
    not:

    ==========  =============  ===============  ===========================
    ``entry``   ``turn_count``  ``next_action``  goto
    ==========  =============  ===============  ===========================
    ``gate``    any             ``gate``         validation_stack — validate
    ``ask``     0               ``coach``        executor — one coaching turn
    ``ask``     >0              ``close``        validation_stack — walk out
    ==========  =============  ===============  ===========================

    ``turn_count`` is incremented by the executor and reset by the input mapper,
    so the ``ask`` path visits the executor **exactly once per invoke**. That is
    what makes one ``ainvoke`` one Belt turn.
    """
    entry = _entry_mode(config)
    turn_count = state.get("turn_count") or 0
    coached = turn_count > 0

    if entry == "gate":
        next_action, goto = "gate", "validation_stack"
    elif not coached:
        next_action, goto = "coach", "executor"
    else:
        next_action, goto = "close", "validation_stack"

    plan: dict[str, Any] = {
        "focus_field": None,          # S-F13 DP1 fills this from §39.1.2's order
        "next_action": next_action,
        "retrieval_strategy": "single_hop",   # §28: Define never multi-hops
        "tools_needed": [],
        "_stub": True,                # step 4.1 marker — 6.1 removes it
    }

    logger.info(
        "define.planner: entry=%s turn_count=%d -> %s (%s)",
        entry, turn_count, goto, next_action,
    )
    return Command(
        goto=cast(Literal["executor", "validation_stack"], goto),
        update={
            "coaching_plan": plan,
            "step_log": [_step(
                turn_count, "planner",
                status="stub", goto=goto, next_action=next_action,
                reason="step 4.2 — DP1 lands at 6.1",
            )],
        },
    )


# ── the v1 bridge ─────────────────────────────────────────────────────────
#
# Everything from here to `executor` exists to be deleted with `orchestrate.py`
# at step 11.1 (DECISIONS.md Part X, Route A).

def _to_v1_state(
    state: PhaseState,
    config: Optional[RunnableConfig],
) -> ImproveGraphState:
    """Bridge ``PhaseState`` to the v1 ``ImproveGraphState`` the orchestrator reads.

    **This is the WATCH 7 seam, and it is temporary by ruling.** DECISIONS.md
    Part X (Route A) keeps ``orchestrate.py`` writing the v1 field names until
    the executor's own capture path exists at step 6.2, after which it is
    deleted at 11.1. So this function exists to be deleted, and the field-name
    mismatch it carries across is **known and accepted**, not an oversight:
    ``artifacts`` holds the v2 names of §39.1.2 while ``orchestrate_define``
    reads and writes the v1 ones, which is why ``draft`` and not ``artifacts``
    is what it is handed.

    Fixed at 4.2 (see the module docstring): the 4.1 version passed
    ``PhaseState.history`` — ``list[str]`` breadcrumbs — where v1 wants turn
    dicts, and omitted ``case_metadata`` and ``current_user`` entirely.
    """
    configurable = (config or {}).get("configurable") or {}
    messages = list(state.get("messages") or [])
    return {
        "case_id": state.get("case_id"),
        "current_phase": state.get("current_phase") or PHASE,
        "current_user": configurable.get("current_user"),
        "case_metadata": configurable.get("case_metadata") or {},
        # `draft` is the v1 accumulator for the duration of the seam.
        "phase_inputs": {PHASE: dict(state.get("draft") or {})},
        "chat_history": [message_to_turn(m, i) for i, m in enumerate(messages)],
        "gate_attempts": state.get("gate_attempts", 0),
        "citations": list(state.get("citations") or []),
    }


# ── executor ──────────────────────────────────────────────────────────────

async def executor(
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> dict[str, Any]:
    """Run one coaching turn. **Returns plainly — emits no routing ``Command``.**

    §17: the executor consumes the plan and decides no strategy. Control returns
    to the planner on the static edge, and the planner chooses what happens next.

    At 4.2 this still delegates to the v1 ``orchestrate_define`` (step 4.1's own
    choice, kept). Stage 6 replaces the body with ``create_agent(...)`` bound to
    the universal seven plus Define's one computation tool (§18, §29, §30) and
    ``response_format=CoachingResponse``.

    **What it returns changed at 4.2**, because the route now reads its output
    through the graph instead of calling ``orchestrate_define`` itself: the
    coach's answer goes into ``messages`` as an ``AIMessage`` carrying the SIPOC
    payload, the visualisation and the section-completion marker in
    ``additional_kwargs``.
    """
    turn_count = state.get("turn_count") or 0
    prior = list(state.get("messages") or [])

    result = await orchestrate_define(_to_v1_state(state, config))

    captured = (result.get("phase_inputs") or {}).get(PHASE, {})
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
        "define.executor: v1 orchestrate returned %d field(s) into draft, "
        "%d new message(s)",
        len(captured), len(new_messages),
    )
    return {
        "messages": new_messages,
        "draft": dict(captured),
        "turn_count": turn_count + 1,
        "step_log": [_step(
            turn_count, "executor",
            status="delegated_v1", impl="orchestrate_define",
            fields_in_draft=len(captured), new_messages=len(new_messages),
        )],
    }


# ── validation_stack ──────────────────────────────────────────────────────

async def validation_stack(
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> Command[Literal["planner", "gate_review"]]:
    """The four layers, shared cap of 3 (§34). **Layer 2b only at 4.2.**

    Stage 7 fills it: layer 2b field presence (``DMAICGateValidator``,
    deterministic), 2c constraints, 2d ``PHASE_RUBRIC`` — cheapest first, each
    firing only if the previous passed. **Layer 2a is NOT here** — it is
    ``CoherenceMiddleware`` on ``after_agent``, because it fires every coaching
    turn and this node runs once, at the gate (§34).

    **It runs the validator only when the planner asked for the gate.** A
    coaching turn walks through here on its way out (``next_action == "close"``)
    and must NOT be validated: ``validate_define`` increments ``gate_attempts``
    on failure, so validating every coaching turn would burn the shared cap of 3
    in three turns and escalate a Belt who is simply still typing. That is the
    §34 cap firing on the wrong event, and it is worth stating because the node
    is on the path either way.

    On the gate path this delegates to the v1 ``validate_define`` — the same
    WATCH 7 seam the executor uses, and the same ruling: ``validate.py`` is
    carried unchanged and the verdict is the one ``/gate`` returns today, on the
    same inputs. The Define gate stays inert (the v1 writer emits v1 names, this
    validator requires the v2 ones); nothing here makes it less inert.

    ``gate_attempts`` is owned by ``validate_define`` for the duration of the
    seam and is carried back onto ``PhaseState`` — which is where §6 says it
    belongs, and is the fix for the v1 defect of holding it in route scope where
    every request rebuilt it at 0.
    """
    turn_count = state.get("turn_count") or 0
    plan = state.get("coaching_plan") or {}

    if plan.get("next_action") != "gate":
        logger.info("define.validation_stack: pass-through (coaching turn)")
        return Command(
            goto="gate_review",
            update={"step_log": [_step(
                turn_count, "validation_stack",
                status="passthrough", next_action=plan.get("next_action"),
                reason="not a gate submission — layers 2c/2d land at stage 7",
            )]},
        )

    result = await validate_define(_to_v1_state(state, config))
    data = (result.get("phase_inputs") or {}).get(PHASE, {})
    passed = bool(data.get("_gate_passed"))
    missing = list(data.get("_missing_fields") or [])
    attempts = int(result.get("gate_attempts") or 0)
    escalated = bool(result.get("escalated"))

    logger.info(
        "define.validation_stack: layer 2b %s (missing=%d, attempts=%d)",
        "PASSED" if passed else "FAILED", len(missing), attempts,
    )
    return Command(
        goto="gate_review",
        update={
            "gate_attempts": attempts,
            # Accumulation is the point (§6): the shared cap of 3 is defensible
            # only because each attempt is better informed than the last.
            "validator_feedback": [{
                "key": step_key(turn_count, "validation_stack"),
                "layer": "2b",
                "impl": "validate_define",
                "passed": passed,
                "missing": missing,
                "attempts": attempts,
                "escalated": escalated,
            }],
            "step_log": [_step(
                turn_count, "validation_stack",
                status="validated_v1", layer="2b",
                passed=passed, missing=len(missing), attempts=attempts,
            )],
        },
    )


# ── gate_review ───────────────────────────────────────────────────────────

async def gate_review(state: PhaseState) -> dict[str, Any]:
    """Present validated fields to the Belt and stop. **Logs only at 4.2.**

    §33: this is where the graph-level ``interrupt()`` fires — never
    ``HumanInTheLoopMiddleware``, which has two confirmed bugs on exactly this
    use case (§19). **No ``interrupt()`` is raised here yet**, and 4.2
    deliberately does not add one: §47 requirement 4 is ruled OUT of this step,
    and an ``interrupt()`` with no ``/gate/approve`` and ``/gate/reject`` resume
    routes (§49) would halt every turn with nothing able to resume it. Both land
    together at stage 7.

    Returns plainly. The static edge carries control to ``gate_apply``, which is
    correct: presenting and applying are two moments of one gate, and the branch
    belongs to ``gate_apply`` (approve -> END, reject -> planner).
    """
    logger.info("define.gate_review: pass-through (interrupt() lands at stage 7)")
    return {"step_log": [_step(
        state.get("turn_count") or 0, "gate_review",
        status="passthrough", reason="step 4.2 — interrupt() lands at stage 7",
    )]}


# ── gate_apply ────────────────────────────────────────────────────────────

async def gate_apply(state: PhaseState) -> Command[Literal["planner", "__end__"]]:
    """Apply Belt edits, run the policy advisory, write the gate document, route on.

    **``policy_advisory`` is logic here, not a node** — it is a BANNED node name
    (§13), because it runs after the Belt edits, when the coach is no longer in
    the loop. Likewise ``revise``: revision is an *edge*, the one the validation
    stack takes back to the planner.

    **IT APPLIES NOTHING AT 4.2, AND THAT IS THE POINT.** Without the
    ``interrupt()`` at ``gate_review``, reaching this node does not mean the
    Belt approved — it means the graph ran. §15's rule that "arriving at END
    means the gate passed" is a statement about the FINISHED subgraph and
    becomes true when stage 7 lands the interrupt. Writing the gate document
    here now would commit a gate approval the Belt never saw, which is precisely
    the failure §47's ABANDON policy and §33's nine-step gate exist to prevent.
    So ``core/graph.py``'s phase node does not call ``define_output_mapper``
    either, and the two omissions are one decision.

    Stage 7 adds the two writes §33 requires — ``store.put(("projects",
    case_id, "artifacts"), phase, doc)`` **and** ``final = doc`` — which must
    both happen, because a crash between them would otherwise leave state and
    store disagreeing about whether the gate applied.

    **``gate_attempts`` and ``validator_feedback`` reset here and only here** —
    the retry budget is per gate passage (§33). Not yet: the reset belongs with
    the approval, and there is no approval here to reset against.
    """
    logger.info("define.gate_apply: pass-through -> END (assembly lands at stage 7)")
    return Command(
        goto=cast(Literal["planner", "__end__"], END),   # END == "__end__"
        update={"step_log": [_step(
            state.get("turn_count") or 0, "gate_apply",
            status="passthrough",
            reason="step 4.2 — advisory, assembly and store write land at stage 7",
        )]},
    )


__all__ = [
    "planner",
    "executor",
    "validation_stack",
    "gate_review",
    "gate_apply",
    "step_key",
    "V1_PRESENTATION_KEYS",
]
