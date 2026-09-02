"""The parent graph — where the checkpointer and the store attach.

Canonical: reference **§12** (topology) · **§16** (`thread_id`, and where
persistence attaches) · **§47** (the disconnect policy) · **§49** (one runtime).
CLAUDE.md §1.1, §1.2, §1.7. Procedure step **4.2**.

THIS IS THE STEP THAT MAKES THE CHECKPOINTER REAL
--------------------------------------------------
Before 4.2 the checkpointer was **wired but inert**. This file compiled a graph
with a checkpointer attached and `gateway/routes.py` threw the compiled object
away, dispatching one v1 node by hand out of a dict literal. `thread_id` and
`ainvoke` appeared nowhere in the codebase and **zero checkpoints had ever been
written** (§53.1, Appendix E). Both dispatch tables are gone and every route
now goes through `await graph.ainvoke(state, config={"configurable":
{"thread_id": case_id}, ...})`.

WHY THIS IS A ONE-PHASE PARENT AND NOT YET THE SUPERVISOR
---------------------------------------------------------
**Step 4.3 is "the supervisor graph"** — five phase subgraph nodes, static
DMAIC edges, the escalation branch, and a test asserting that topology. This
step needs *a* parent for one reason only: **§16 puts the checkpointer and the
store on the parent and forbids them on a subgraph**, so making checkpoints
real means there must be a parent to attach them to. So the parent built here
is the smallest one that satisfies §16 — `START -> define_phase -> END` — and
4.3 grows it into the real supervisor. Building the five-node version now would
be doing 4.3's work with four subgraphs that do not exist until 4.4.

**The consequence is stated rather than hidden: only Define runs through the
graph at 4.2.** That is not a live regression — `build_phase_subgraph` refuses
any other phase (step 4.1), the Define gate is ratified inert until 6.2
(WATCH 7), a case's `current_phase` advances only on a gate pass, and the UI
locks every later phase — so no case can reach Measure today. The four phases
are refused explicitly at the boundary rather than quietly falling back to a
v1 dispatch table, which is the thing §49 exists to remove. Tracked as a WATCH;
it closes at 4.4.

**The v1 chained graph is gone.** It wired ten `orchestrate_*` / `validate_*`
nodes over `ImproveGraphState` with conditional edges from Define through to
Control, so a single `ainvoke` would have run the entire DMAIC sequence — which
is exactly why the route dispatched one node by hand instead. That topology has
no turn boundary and cannot be invoked; the phase subgraph is the boundary
(procedure Part 3's ordering note). The escalation node goes with it and
returns as the parent's conditional branch at 4.3.

THE OUTPUT MAPPER IS DESIGNATED AND DELIBERATELY NOT CALLED
-----------------------------------------------------------
§15 says a phase subgraph reaches `END` only through `gate_apply`, so arriving
there means the gate passed. **That becomes true when stage 7 lands the
`interrupt()` at `gate_review`.** At 4.2 there is no interrupt, so the subgraph
runs to `END` on every invoke and `END` means only "the graph ran". Calling
`define_output_mapper` here would therefore write a gate document and advance
`current_phase` on every coaching turn — a gate approval the Belt never saw,
which is the precise failure §47's ABANDON policy exists to prevent.

So `current_phase`'s single writer (§5 B2, S-F11 B1) is the output mapper, it
is the only thing that may write it, and at 4.2 it does not fire. **The route
no longer writes it either** — that is what the single-writer rule buys at this
step, and it is a real change: the v1 routes rebuilt an eleven-field state
literal per request, `current_phase` included.
"""
from __future__ import annotations

import asyncio
import logging
from functools import lru_cache
from typing import Any, Optional

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from backend.core.checkpointer import get_checkpointer
from backend.core.state import SupervisorState
from backend.core.store import get_store
from backend.phases.define.graph import build_phase_subgraph
from backend.phases.define.mappers import define_input_mapper
from backend.phases.mappers_common import PHASE_ORDER

logger = logging.getLogger(__name__)

#: §16 — a backstop against genuine infinite loops, NOT the hop budget. The
#: per-turn hop cap is `RemainingSteps`, read inside the executor (§26).
RECURSION_LIMIT = 50

#: The phases whose subgraph exists. 4.4 makes this `PHASE_ORDER`.
WIRED_PHASES: tuple[str, ...] = ("define",)


class PhaseNotWired(ValueError):
    """A phase whose subgraph has not been built yet (procedure step 4.4)."""


@lru_cache(maxsize=1)
def _define_subgraph():
    """The compiled Define subgraph — built once per process.

    **Compiled with neither checkpointer nor store** (§16, S-F02 B1); it reaches
    the parent's through the auto-managed `checkpoint_ns`. `test_define_graph.py`
    asserts that, and `test_turn_graph.py` asserts the parent has both.
    """
    return build_phase_subgraph("define", llm=None)


async def define_phase(
    state: SupervisorState,
    config: Optional[RunnableConfig] = None,
) -> dict[str, Any]:
    """The parent's node for Define: input mapper -> subgraph -> parent slice.

    **S-F10's execution site.** A boundary mapper runs inside the parent's
    *uniquely-named* node function for its phase, not inside the subgraph, and
    it does not add a sixth node — §13's five-node rule governs the subgraph and
    this runs one level up. The unique name is load-bearing: checkpoint
    namespaces for subgraphs invoked inside node functions are assigned by CALL
    ORDER, so a rename or reorder would change which subgraph loads which state.

    **The mapper is called on a worker thread.** `define_input_mapper` takes a
    synchronous `BaseStore` (S-F10 fixes that signature) and `AzureBlobStore`'s
    sync path is a blocking Azure Blob call. Awaiting it inline would put
    blocking I/O on the event loop on every turn — the regression step 3.5 spent
    itself removing from `storage/blob.py`. `asyncio.to_thread` keeps the
    mapper's signature and keeps the loop free.

    **Two values are seeded onto the child after the mapper**, both marked at
    their site: `draft` carries the v1 accumulator across turns (the WATCH 7
    seam), and `turn_count` carries the entry mode. Seeding at the boundary is
    the parent node's job; neither is something a mapper may know about, and
    both are deleted with the seam at 6.2.

    **The subgraph is invoked with no explicit config**, deliberately.
    LangGraph propagates the running config — `thread_id` and the whole of
    `configurable` included — through contextvars and assigns the child its own
    `checkpoint_ns`. That auto-managed namespace is what §16 specifies; passing
    the parent's config down by hand would hand the child the PARENT's
    namespace and have the two write over each other.

    **Everything the route needs comes back on the messages** (§5). The parent
    state is orchestration only, so the coach's answer, the captured fields, the
    presentational payloads and the gate verdict all ride in the AI message's
    `additional_kwargs` — which is the channel `CoachingResponse` formalises at
    6.2, not a workaround invented here.
    """
    configurable = (config or {}).get("configurable") or {}
    phase = state["current_phase"]
    if phase not in WIRED_PHASES:
        raise PhaseNotWired(
            f"No compiled subgraph for phase {phase!r}. Only "
            f"{', '.join(WIRED_PHASES)} is wired at procedure step 4.2; the "
            f"remaining four land at 4.4."
        )

    store = get_store()
    child = await asyncio.to_thread(define_input_mapper, state, store)
    sent_messages = list(child["messages"])

    # ── the WATCH 7 seam, seeded at the boundary ──────────────────────
    # `draft` is the v1 accumulator (see `phases/define/nodes.py`). The mapper
    # initialises it to `{}` because in the v2 design this turn's extraction
    # starts empty; until 6.2 it has to carry what the case document already
    # holds, or every turn re-extracts against nothing.
    seeded = configurable.get("v1_artifacts")
    if seeded:
        child["draft"] = dict(seeded)

    # `turn_count` carries the entry mode into the planner's predicate: 0 means
    # "coach one turn", non-zero means "we are here for the gate". The mapper
    # resets it on every invoke, which is what keeps one invoke to one turn
    # (see the planner's docstring).
    entry = configurable.get("entry", "ask")
    if entry == "gate":
        child["turn_count"] = 1

    result = await _define_subgraph().ainvoke(child)

    # **`define_output_mapper` is NOT called** — see the module docstring. It
    # stays `current_phase`'s designated single writer and fires at stage 7,
    # when reaching END actually means the Belt approved.
    new_messages = _new_messages(sent_messages, result)
    turn_count = result.get("turn_count") or 0

    # The turn's product, attached to the message that carries it. Only the
    # coaching path produces one; the gate path gets a synthesised carrier
    # below, because there is no coach reply on a gate submission.
    verdict = _verdict(result)
    payload: dict[str, Any] = {
        "phase": phase,
        "v1_artifacts": dict(result.get("draft") or {}),
        "gate_verdict": verdict,
        "turn_count": turn_count,
    }
    if new_messages:
        _attach(new_messages[-1], payload)
    else:
        new_messages = [AIMessage(
            content=(
                f"Gate submitted for {phase}: "
                f"{'ready' if verdict.get('passed') else 'not ready'}."
            ),
            additional_kwargs={**payload, "gate_submission": True},
        )]

    logger.info(
        "define_phase: entry=%s, %d new message(s), turn_count=%d",
        entry, len(new_messages), turn_count,
    )

    # Only orchestration-relevant values go back to the parent (§5, S-F11 B3).
    # `history` is the breadcrumb trail and reuses the subgraph's own
    # deterministic `step_log` keys (§47 requirement 2) rather than minting a
    # second identity for the same step.
    return {
        "messages": new_messages,
        "history": [
            s.get("key", f"{phase}:{turn_count}:?")
            for s in (result.get("step_log") or [])
        ],
    }


def _new_messages(sent: list, result: dict[str, Any]) -> list:
    """The messages the subgraph added, and only those.

    `PhaseState.messages` reduces with `operator.add`, so the returned list is
    what was sent plus what the nodes appended. Returning more than the tail
    would duplicate the conversation into the parent on every turn — the same
    trap the executor guards against one level down.
    """
    returned = list(result.get("messages") or [])
    n = len(sent)
    if len(returned) >= n and returned[:n] == sent:
        return returned[n:]
    # A prefix mismatch means the subgraph did not start from what was sent.
    # Log it rather than silently returning the whole conversation as "new".
    logger.warning(
        "define_phase: subgraph message prefix did not match (sent=%d, "
        "returned=%d) — returning the tail only",
        n, len(returned),
    )
    return returned[n:] if len(returned) > n else []


def _verdict(result: dict[str, Any]) -> dict[str, Any]:
    """The gate verdict from the subgraph's accumulated `validator_feedback`.

    Empty on a coaching turn: `validation_stack` records nothing when the
    planner did not ask for the gate, so an empty dict here means "not
    validated", never "validated and passed".
    """
    feedback = list(result.get("validator_feedback") or [])
    if not feedback:
        return {}
    latest = dict(feedback[-1])
    latest["gate_attempts"] = result.get("gate_attempts", 0)
    return latest


def _attach(message: Any, payload: dict[str, Any]) -> None:
    """Attach the turn's product to the message that carries it out."""
    extra = dict(getattr(message, "additional_kwargs", None) or {})
    extra.update(payload)
    message.additional_kwargs = extra


@lru_cache(maxsize=1)
def get_graph():
    """Build and compile the parent graph. Cached — compiled once per process.

    **The checkpointer and the store attach HERE and only here** (§16). The
    phase subgraph compiles with neither and reaches these through the
    auto-managed `checkpoint_ns`.
    """
    builder = StateGraph(SupervisorState)
    builder.add_node("define_phase", define_phase)
    builder.add_edge(START, "define_phase")
    builder.add_edge("define_phase", END)

    try:
        checkpointer = get_checkpointer()
    except RuntimeError as e:
        logger.critical(
            "Checkpointer unavailable — graph will not persist state. "
            "This is acceptable for offline dev only. Error: %s", e
        )
        checkpointer = None

    try:
        store = get_store()
    except RuntimeError as e:
        # Same posture as the checkpointer above, and for the same reason: an
        # offline dev box with no connection string should still import.
        logger.critical(
            "Store unavailable — cross-phase artifacts will not persist. "
            "Offline dev only. Error: %s", e
        )
        store = None

    graph = builder.compile(checkpointer=checkpointer, store=store)
    logger.info(
        "Agent Improve parent graph compiled — checkpointer=%s store=%s, "
        "wired phases: %s (of %d)",
        type(checkpointer).__name__ if checkpointer else None,
        type(store).__name__ if store else None,
        ", ".join(WIRED_PHASES), len(PHASE_ORDER),
    )
    return graph


__all__ = [
    "get_graph",
    "define_phase",
    "PhaseNotWired",
    "PHASE_ORDER",
    "RECURSION_LIMIT",
    "WIRED_PHASES",
]
