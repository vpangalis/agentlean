"""The five nodes of the Define phase subgraph.

Canonical definition: reference **§13** (the five nodes), **§14** (the node
contract), **§15** (routing). Procedure step 4.1.

**Structurally correct, behaviourally minimal — deliberately.** Step 4.1 builds
the topology and nothing else: the planner returns a stub plan, the executor
delegates to the v1 `orchestrate_define`, and the last three log and pass
through. Stages 5–7 fill them. Routing no traffic here yet is part of the step.

WHAT IS REAL AT 4.1, AND WHAT IS NOT
------------------------------------
Real, and must not regress:

  * five nodes, named exactly as §13 names them;
  * every node an `async def` module-level function returning a dict slice or a
    `Command` — never a Pydantic model, never full state (§14);
  * the planner owns the ONLY field/gate routing decision, and the executor
    returns plainly (§17). Fusing them while leaving the node names intact is
    the failure §17 exists to prevent, and the hard one to see;
  * `Command` routing, never a conditional edge, and never mixed with a static
    edge out of the same node — both paths would execute, silently (§15 C2).

Not real yet, and each is marked at its site: the `CoachingPlan` type (S-C04,
step 6.1), `create_agent` with the tool subset (§18, stage 6), the four
validation layers (§34), the `interrupt()` (§33), and gate-document assembly
(§33, S-F28).

NODES MAY NOT WRITE `case_id` OR `current_phase`
-----------------------------------------------
Both are copied down by the input mapper at phase entry and are READ-ONLY here
(S-C02 B9). `SupervisorState.current_phase` keeps its single writer, the output
mapper. No return dict below carries either key, and `test_define_graph.py`
pins that.
"""
from __future__ import annotations

import logging
from typing import Any, Literal, cast

from langgraph.graph import END
from langgraph.types import Command

from backend.core.state import ImproveGraphState
from backend.core.substate import PhaseState
from backend.phases.define.orchestrate import orchestrate_define

logger = logging.getLogger(__name__)

PHASE = "define"


# ── planner ───────────────────────────────────────────────────────────────

async def planner(
    state: PhaseState,
) -> Command[Literal["executor", "validation_stack"]]:
    """Produce the `CoachingPlan` and make the phase's ONE routing decision.

    §13: the planner fires many times per phase, not once. After each executor
    step control returns here to decide whether to keep coaching the current
    field, advance to the next, or trigger the gate.

    **The plan is a stub at 4.1.** `PhaseState.coaching_plan` is annotated
    `Optional[dict[str, Any]]` because S-C04's `CoachingPlan` model does not
    land until step 6.1; §6 sanctions the dict as the interim annotation. The
    keys below are the shape S-C04 will type, so the swap is a type change
    rather than a rewrite.

    **The routing predicate is a PLACEHOLDER, not DP1.** S-F13's DP1 reads the
    per-phase field ordering (§39.1.2's twelve coached positions) to decide
    "field complete". That predicate lands with the real planner at 6.1. Until
    then this routes on "has anything been captured at all", which is enough to
    give the topology a terminating path and nothing more. It is NOT a
    behavioural approximation of DP1 and must not be treated as one.
    """
    artifacts = state.get("artifacts") or {}

    plan: dict[str, Any] = {
        "focus_field": None,          # S-F13 DP1 fills this from §39.1.2's order
        "next_action": "coach",
        "retrieval_strategy": "single_hop",   # §28: Define never multi-hops
        "tools_needed": [],
        "_stub": True,                # step 4.1 marker — 6.1 removes it
    }

    goto: Literal["executor", "validation_stack"] = (
        "executor" if not artifacts else "validation_stack"
    )
    logger.info(
        "define.planner: stub plan, routing to %s (artifacts=%d)",
        goto, len(artifacts),
    )
    return Command(
        goto=goto,
        update={
            "coaching_plan": plan,
            "step_log": [{
                "node": "planner", "phase": PHASE, "status": "stub",
                "goto": goto, "reason": "step 4.1 — DP1 lands at 6.1",
            }],
        },
    )


# ── executor ──────────────────────────────────────────────────────────────

def _to_v1_state(state: PhaseState) -> ImproveGraphState:
    """Bridge `PhaseState` to the v1 `ImproveGraphState` the orchestrator reads.

    **This is the WATCH 7 seam, and it is temporary by ruling.** DECISIONS.md
    Part X (Route A) keeps `orchestrate.py` writing the v1 field names until the
    executor's own capture path exists at step 6.2, after which it is deleted at
    11.1. So this function exists to be deleted, and the field-name mismatch it
    carries across is **known and accepted**, not an oversight:
    `artifacts` holds the v2 names of §39.1.2 while `orchestrate_define` reads
    and writes the v1 ones. That is precisely why the Define gate is accepted as
    inert until 6.2 — nothing here makes it less inert.
    """
    return {
        "case_id":        state.get("case_id"),
        "current_phase":  state.get("current_phase") or PHASE,
        "phase_inputs":   {PHASE: dict(state.get("artifacts") or {})},
        "chat_history":   list(state.get("history") or []),
        "gate_attempts":  state.get("gate_attempts", 0),
        "citations":      list(state.get("citations") or []),
    }


async def executor(state: PhaseState) -> dict[str, Any]:
    """Run one coaching turn. **Returns plainly — emits no routing `Command`.**

    §17: the executor consumes the plan and decides no strategy. Control returns
    to the planner on the static edge, and the planner chooses what happens next.

    At 4.1 this delegates to the v1 `orchestrate_define` (the step says so
    explicitly). Stage 6 replaces the body with `create_agent(...)` bound to the
    universal seven plus Define's one computation tool (§18, §29, §30) and
    `response_format=CoachingResponse`.

    **The v1 result lands in `draft`, not in `artifacts`.** `draft` is this
    turn's extraction; `artifacts` is what the gate reads. Writing v1 field
    names into `artifacts` would put them on the v2 gate path, which WATCH 7's
    ruling exists to prevent — the capture path into `artifacts` is step 6.2's,
    through `CoachingResponse.fields_captured`.
    """
    result = await orchestrate_define(_to_v1_state(state))

    captured = (result.get("phase_inputs") or {}).get(PHASE, {})
    logger.info(
        "define.executor: v1 orchestrate returned %d field(s) into draft",
        len(captured),
    )
    return {
        "draft": dict(captured),
        "turn_count": state.get("turn_count", 0) + 1,
        "step_log": [{
            "node": "executor", "phase": PHASE, "status": "delegated_v1",
            "impl": "orchestrate_define", "fields_in_draft": len(captured),
        }],
    }


# ── validation_stack ──────────────────────────────────────────────────────

async def validation_stack(
    state: PhaseState,
) -> Command[Literal["planner", "gate_review"]]:
    """The four layers, shared cap of 3 (§34). **Pass-through that logs at 4.1.**

    Stage 7 fills it: layer 2b field presence (`DMAICGateValidator`,
    deterministic), 2c constraints, 2d `PHASE_RUBRIC` — cheapest first, each
    firing only if the previous passed. **Layer 2a is NOT here** — it is
    `CoherenceMiddleware` on `after_agent`, because it fires every coaching turn
    and this node runs once, at the gate (§34).

    `gate_attempts` increments once at entry, not per layer, and the cap of 3 is
    shared across the layers — a partial stack still costs an attempt (§34).
    Neither is implemented here yet; the counter stays untouched so nothing
    reads a fabricated attempt count.
    """
    logger.info("define.validation_stack: pass-through (layers land at stage 7)")
    return Command(
        goto="gate_review",
        update={"step_log": [{
            "node": "validation_stack", "phase": PHASE, "status": "passthrough",
            "reason": "step 4.1 — layers 2b/2c/2d land at stage 7",
        }]},
    )


# ── gate_review ───────────────────────────────────────────────────────────

async def gate_review(state: PhaseState) -> dict[str, Any]:
    """Present validated fields to the Belt and stop. **Logs only at 4.1.**

    §33: this is where the graph-level `interrupt()` fires — never
    `HumanInTheLoopMiddleware`, which has two confirmed bugs on exactly this use
    case (§19). **No `interrupt()` is raised here yet**, deliberately: 4.1 routes
    no traffic, and a node that halts the graph is not something to add before
    there is a resume path (step 4.2 wires `thread_id` and `ainvoke`).

    Returns plainly. The static edge carries control to `gate_apply`, which is
    correct: presenting and applying are two moments of one gate, and the
    branch belongs to `gate_apply` (approve → END, reject → planner).
    """
    logger.info("define.gate_review: pass-through (interrupt() lands at stage 7)")
    return {"step_log": [{
        "node": "gate_review", "phase": PHASE, "status": "passthrough",
        "reason": "step 4.1 — interrupt() lands at stage 7",
    }]}


# ── gate_apply ────────────────────────────────────────────────────────────

async def gate_apply(state: PhaseState) -> Command[Literal["planner", "__end__"]]:
    """Apply Belt edits, run the policy advisory, write the gate document, route on.

    **`policy_advisory` is logic here, not a node** — it is a BANNED node name
    (§13), because it runs after the Belt edits, when the coach is no longer in
    the loop. Likewise `revise`: revision is an *edge*, the one the validation
    stack takes back to the planner.

    At 4.1 this is a pass-through that routes to `END`. Stage 7 adds the two
    writes §33 requires — `store.put(("projects", case_id, "artifacts"), phase,
    doc)` **and** `final = doc` — which must both happen, because a crash
    between them would otherwise leave state and store disagreeing about
    whether the gate applied.

    **`gate_attempts` and `validator_feedback` reset here and only here** — the
    retry budget is per gate passage (§33). Not yet: nothing has incremented
    them, so resetting would be theatre.
    """
    logger.info("define.gate_apply: pass-through -> END (assembly lands at stage 7)")
    return Command(
        goto=cast(Literal["planner", "__end__"], END),   # END == "__end__"
        update={"step_log": [{
            "node": "gate_apply", "phase": PHASE, "status": "passthrough",
            "reason": "step 4.1 — advisory, assembly and store write land at stage 7",
        }]},
    )


__all__ = [
    "planner",
    "executor",
    "validation_stack",
    "gate_review",
    "gate_apply",
]
