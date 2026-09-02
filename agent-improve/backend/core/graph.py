"""Level 1 — the supervisor graph, and where persistence attaches.

Canonical: reference **§58.10 — S-F01** (*rebuild test: this file's supervisor
wiring must be reconstructable from that entry alone*) · **§12** (topology) ·
**§15** (routing) · **§16** (`thread_id`, checkpointer and store) · **§38**
(escalation). CLAUDE.md §1.1, §1.2, §1.7, §3.5. Procedure steps **4.2** and
**4.3**.

THE SUPERVISOR MAKES NO ROUTING DECISION
----------------------------------------
Seven `add_edge` calls are the complete Level 1 wiring. **There is no
conditional edge, no router function, and nothing for the supervisor to branch
on** (§15, S-F01 invariants). DMAIC order is fixed, so an LLM call to choose the
next phase would be cost and latency purchasing no decision, and a
deterministic router would be a second source of truth for what the edges
already state.

**`route_after_phase` was deleted on 2026-08-22 and MUST NOT be reinstated**
(§15, CLAUDE.md §0.14, DECISIONS §R2). It returned `"next"` / `"escalate"` /
`"retry"` — labels wired to nothing — and read `state["gate_attempts"]` off
`SupervisorState`, where that field does not exist, so it would have raised
`KeyError` on the gate-failure path specifically.

> **Step 4.3's prompt asks to "route to escalation on the conditional edge §3.5
> describes", and that conditional edge is NOT at this level.** §3.5 names the
> trigger — the validation stack exhausting its shared cap of 3 — without
> saying where the edge lives; §15 and §38 both say, and they agree: *"a
> conditional edge **from inside the phase** to the escalation subgraph, which
> defers to the Belt and never returns to the supervisor."* Reading §3.5 as a
> Level 1 conditional edge reconstructs `route_after_phase` exactly, down to
> reading a counter this state does not carry. So escalation is a **node** here
> and an **edge** one level down.

WHY THE STATIC CHAIN IS SAFE — AND THE PRECONDITION THAT IS NOT YET TRUE
------------------------------------------------------------------------
§15's justification for static edges is precise: **a phase subgraph reaches
`END` only through `gate_apply`, and `gate_apply` runs only after Belt
approval, so reaching `END` MEANS the gate passed.** A failing gate never
arrives at the supervisor — it loops back to the planner inside the subgraph or
exits sideways to escalation.

**That precondition is FALSE today.** `gate_review` does not yet raise
`interrupt()` (§33, stage 7), so the Define subgraph runs straight through to
`END` on every invoke and `END` means only "the graph ran" (DECISIONS Z2). Wire
live traffic to this chain now and one `/ask` turn would run Define, then
Measure, then Analyse — the entire DMAIC sequence in a single turn, which is
the exact defect the procedure's Part 3 ordering note records against the v1
graph.

**So this supervisor is built and tested and is NOT yet the runtime**, exactly
as step 4.1 built the Define subgraph and routed no traffic to it. `get_graph()`
— what `gateway/routes.py` calls — still returns the one-turn parent that step
4.2 shipped and verified against the live container. **The swap is a two-line
change and its trigger is precise: when `gate_review` raises `interrupt()`,
`END` starts meaning what §15 says it means, and `get_graph` returns
`build_supervisor()`.** Both live in this file so the swap cannot be missed.

ESCALATION IS REACHED BY `Command.PARENT`, AND THAT IS VERIFIED
---------------------------------------------------------------
§0.17 makes the escalation hop **the only use of `Command.PARENT` in this
architecture**. There was a real question whether it survives S-F10's execution
site: the mappers require each phase subgraph to be invoked **inside** the
parent's node function, not added as a node, and `Command.PARENT` is documented
against the added-as-a-node shape.

**Tested against the pinned langgraph 1.2.11 rather than assumed — it works.**
A `Command(graph=Command.PARENT, goto="escalate")` raised inside a subgraph
invoked via `await subgraph.ainvoke(...)` propagates as a `ParentCommand`
exception out of the call, through the parent's node function, and is caught by
the parent's task runner, which rewrites its namespace and dispatches to
`escalate`. Both shapes reached the node.

**One consequence is load-bearing and is why this is recorded here rather than
in a commit body: the parent node function's code after the invoke DOES NOT
RUN** on an escalation — the exception passes straight through it. So the
output mapper is skipped, which is correct (an escalated phase did not pass its
gate and must not write a gate document) and must stay correct when stage 7
fills `gate_apply` in.
"""
from __future__ import annotations

import asyncio
import logging
from functools import lru_cache
from typing import Any, Callable, Optional

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from backend.core.checkpointer import get_checkpointer
from backend.core.state import SupervisorState
from backend.core.store import get_store
from backend.phases.analyse.mappers import analyse_input_mapper
from backend.phases.control.mappers import control_input_mapper
from backend.phases.define.graph import build_phase_subgraph
from backend.phases.define.mappers import define_input_mapper
from backend.phases.improve.mappers import improve_input_mapper
from backend.phases.mappers_common import PHASE_ORDER
from backend.phases.measure.mappers import measure_input_mapper

logger = logging.getLogger(__name__)

#: §16 — a backstop against genuine infinite loops, NOT the hop budget. The
#: per-turn hop cap is `RemainingSteps`, read inside the executor (§26).
RECURSION_LIMIT = 50

#: §13 — the escalation node's name at Level 1. It is the `goto` target of the
#: `Command(graph=Command.PARENT, ...)` the validation stack raises at stage 7,
#: so it is part of the contract between the two levels, not a local label.
ESCALATE_NODE = "escalate"

#: The phases whose subgraph is built. 4.4 makes this `PHASE_ORDER`.
WIRED_PHASES: tuple[str, ...] = ("define",)

#: S-F10 / S-F12 — one input mapper per phase, all ten landed at step 3.3.
INPUT_MAPPERS: dict[str, Callable[..., Any]] = {
    "define": define_input_mapper,
    "measure": measure_input_mapper,
    "analyse": analyse_input_mapper,
    "improve": improve_input_mapper,
    "control": control_input_mapper,
}


class PhaseNotWired(ValueError):
    """A phase whose subgraph has not been built yet (procedure step 4.4)."""


@lru_cache(maxsize=len(PHASE_ORDER))
def _subgraph(phase: str):
    """The compiled subgraph for one phase — built once per process.

    **Compiled with neither checkpointer nor store** (§16, S-F02 B1); it reaches
    the parent's through the auto-managed `checkpoint_ns`.
    `test_supervisor_graph.py` asserts that for every wired phase.
    """
    if phase not in WIRED_PHASES:
        raise PhaseNotWired(
            f"No compiled subgraph for phase {phase!r}. Only "
            f"{', '.join(WIRED_PHASES)} is wired; the remaining four land at "
            f"procedure step 4.4."
        )
    return build_phase_subgraph(phase, llm=None)


# ── the phase node ────────────────────────────────────────────────────────

def phase_node(phase: str) -> Callable[..., Any]:
    """Build the parent's node function for one phase.

    **S-F10's execution site.** A boundary mapper runs inside the parent's
    *uniquely-named* node function for its phase, not inside the subgraph, and
    it does not add a sixth node — §13's five-node rule governs the subgraph and
    this runs one level up. The unique name is load-bearing: checkpoint
    namespaces for subgraphs invoked inside node functions are assigned by CALL
    ORDER, so a rename or reorder changes which subgraph loads which state.

    **The mapper is called on a worker thread.** `{phase}_input_mapper` takes a
    synchronous `BaseStore` (S-F10 fixes that signature) and `AzureBlobStore`'s
    sync path is a blocking Azure Blob call. Awaiting it inline would put
    blocking I/O on the event loop on every turn — the regression step 3.5 spent
    itself removing from `storage/blob.py`.

    **The output mapper is NOT called** — DECISIONS Z2. Reaching `END` does not
    yet mean the Belt approved, so writing a gate document and advancing
    `current_phase` here would commit an approval nobody saw. It stays
    `current_phase`'s designated single writer (§5 B2) and fires at stage 7.
    """

    async def node(
        state: SupervisorState,
        config: Optional[RunnableConfig] = None,
    ) -> dict[str, Any]:
        configurable = (config or {}).get("configurable") or {}

        # The parent's own view of where the project is. Checked against the
        # wired set BEFORE this node's own subgraph, because a case sitting in
        # an unbuilt phase is a "not yet, comes at 4.4" condition (501) rather
        # than an internal fault — and the route reports it as such. The
        # complementary check, that this node's phase IS the parent's, is the
        # input mapper's own assertion (S-C02 B8); it is left there rather than
        # duplicated here so there is one copy of the identity rule.
        current = state["current_phase"]
        if current not in WIRED_PHASES:
            raise PhaseNotWired(
                f"Case is in phase {current!r}, whose subgraph is not built. "
                f"Only {', '.join(WIRED_PHASES)} is wired; the remaining four "
                f"land at procedure step 4.4."
            )

        compiled = _subgraph(phase)          # raises PhaseNotWired until 4.4
        mapper = INPUT_MAPPERS[phase]

        store = get_store()
        child = await asyncio.to_thread(mapper, state, store)
        sent_messages = list(child["messages"])

        # ── the WATCH 7 seam, seeded at the boundary ──────────────────
        # `draft` is the v1 accumulator (see `phases/define/nodes.py`). The
        # mapper initialises it to `{}` because in the v2 design this turn's
        # extraction starts empty; until 6.2 it has to carry what the case
        # document already holds, or every turn re-extracts against nothing.
        seeded = configurable.get("v1_artifacts")
        if seeded:
            child["draft"] = dict(seeded)

        # `turn_count` carries the entry mode into the planner's predicate: 0
        # means "coach one turn", non-zero means "we are here for the gate".
        entry = configurable.get("entry", "ask")
        if entry == "gate":
            child["turn_count"] = 1

        # No explicit config: LangGraph propagates the running config through
        # contextvars and assigns the child its own `checkpoint_ns` (§16).
        # Passing the parent's config down by hand would hand the child the
        # PARENT's namespace and have the two write over each other.
        result = await compiled.ainvoke(child)

        new_messages = _new_messages(sent_messages, result)
        turn_count = result.get("turn_count") or 0

        # The turn's product, attached to the message that carries it out.
        # `SupervisorState` is seven fields (§5), so `messages` is the channel.
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
            "%s: entry=%s, %d new message(s), turn_count=%d",
            phase, entry, len(new_messages), turn_count,
        )
        # `history` reuses the subgraph's own deterministic `step_log` keys
        # (§47 requirement 2) rather than minting a second identity.
        return {
            "messages": new_messages,
            "history": [
                s.get("key", f"{phase}:{turn_count}:?")
                for s in (result.get("step_log") or [])
            ],
        }

    node.__name__ = phase
    return node


async def escalate_node(
    state: SupervisorState,
    config: Optional[RunnableConfig] = None,
) -> dict[str, Any]:
    """Level 1's escalation node — the target of the Level 2 `Command.PARENT`.

    §38: reachable two ways, **both from inside a phase** — the validation stack
    exhausting its shared cap of 3 (§34), and the `request_human_approval` tool
    (§29.2). It defers to the Belt with the unresolved constraints named
    (§34.2 Level 4) and **never returns to the supervisor**, which is why its
    only edge is to `END`.

    **Nothing reaches it yet, and that is why it does not compose a report.**
    `validation_stack` is a pass-through until stage 7 and raises no `Command`,
    so this node is unreachable at 4.3 — a fact the topology test pins rather
    than hides. Composing an escalation report now would mean inventing the
    payload it is supposed to receive: `escalate.py`'s v1 `escalate()` reads
    `current_phase`, `gate_attempts` and `_missing_fields`, and **none of the
    three is on `SupervisorState`** (§5, seven fields — and §15 is explicit that
    `gate_attempts` must not be added to it). They arrive on the `Command`'s own
    `update` when stage 7 raises it, and wiring the report is that step's work.

    So this logs and hands back a plain message. **What it must NOT do** is read
    a counter off parent state — that is precisely the mistake that made
    `route_after_phase` a `KeyError` waiting on the gate-failure path.
    """
    logger.warning(
        "ESCALATION reached for case=%s phase=%s — deferring to the Belt",
        state.get("case_id"), state.get("current_phase"),
    )
    return {
        "messages": [AIMessage(
            content=(
                "This phase has been escalated for human review. Your Belt "
                "will pick it up with the outstanding items in front of them."
            ),
            additional_kwargs={"escalated": True},
        )],
        "history": [f"{state.get('current_phase')}:escalate"],
    }


# ── helpers shared by every phase node ────────────────────────────────────

def _new_messages(sent: list, result: dict[str, Any]) -> list:
    """The messages the subgraph added, and only those.

    `PhaseState.messages` reduces with `operator.add`, so the returned list is
    what was sent plus what the nodes appended. Returning more than the tail
    would duplicate the conversation into the parent on every turn.
    """
    returned = list(result.get("messages") or [])
    n = len(sent)
    if len(returned) >= n and returned[:n] == sent:
        return returned[n:]
    logger.warning(
        "phase node: subgraph message prefix did not match (sent=%d, "
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


def _persistence():
    """The checkpointer and store, or `None` on an offline dev box.

    Both are required for a real run and neither may be silently absent in one
    that matters — hence `critical`. Raising instead would make the test suite
    unrunnable on a machine with no connection string.
    """
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
        logger.critical(
            "Store unavailable — cross-phase artifacts will not persist. "
            "Offline dev only. Error: %s", e
        )
        store = None
    return checkpointer, store


# ── Level 1 — the supervisor (S-F01) ──────────────────────────────────────

def supervisor_builder() -> StateGraph:
    """The uncompiled Level 1 wiring — the seven `add_edge` calls of S-F01.

    Separate from `build_supervisor()` so the topology can be asserted on the
    BUILDER rather than on the drawing. `CompiledStateGraph.get_graph()` omits
    edges out of nodes not reachable from `START`, and `escalate` is exactly
    that until stage 7 raises the `Command` that reaches it — so a test reading
    the drawing would report `escalate -> END` as missing when it is present.
    """
    builder = StateGraph(SupervisorState)

    for phase in PHASE_ORDER:
        builder.add_node(phase, phase_node(phase))
    builder.add_node(ESCALATE_NODE, escalate_node)

    # ── the complete Level 1 wiring (S-F01) ───────────────────────────
    builder.add_edge(START, PHASE_ORDER[0])                  # B1
    for current, following in zip(PHASE_ORDER, PHASE_ORDER[1:]):
        builder.add_edge(current, following)                 # B2 — no condition
    builder.add_edge(PHASE_ORDER[-1], END)
    # §38 — escalation defers to the Belt and never returns to the supervisor.
    builder.add_edge(ESCALATE_NODE, END)

    return builder


@lru_cache(maxsize=1)
def build_supervisor():
    """The ratified Level 1 graph. Cached — compiled once per process.

    **Seven `add_edge` calls and nothing else.** S-F01's own definition block,
    plus `escalate -> END`, which that block omits because it does not draw the
    escalation node. B1: entry is `add_edge(START, ...)`; `set_entry_point` is
    superseded and must not be used.

    **The checkpointer and store attach HERE and only here** (§16, B3). Every
    phase subgraph compiles with neither and reaches these through the
    auto-managed `checkpoint_ns`.

    ⚠ **NOT YET THE RUNTIME.** See the module docstring: the static chain is
    safe only once reaching `END` means the gate passed, and that becomes true
    when `gate_review` raises `interrupt()` at stage 7. Until then `get_graph()`
    returns the one-turn parent.
    """
    builder = supervisor_builder()
    checkpointer, store = _persistence()
    graph = builder.compile(checkpointer=checkpointer, store=store)
    logger.info(
        "Agent Improve SUPERVISOR compiled — %d phase nodes + %s, "
        "checkpointer=%s store=%s (not yet the runtime)",
        len(PHASE_ORDER), ESCALATE_NODE,
        type(checkpointer).__name__ if checkpointer else None,
        type(store).__name__ if store else None,
    )
    return graph


# ── the runtime, until the gate interrupt lands ───────────────────────────

@lru_cache(maxsize=1)
def get_graph():
    """The compiled graph every route invokes (§12, §49). Cached per process.

    **This is the one-turn parent step 4.2 shipped**, `START -> define_phase ->
    END`, and it stays the runtime until `gate_review` raises `interrupt()`.
    The reason is §15's own precondition, stated in the module docstring: the
    supervisor's static DMAIC chain advances on `END`, and until the interrupt
    exists `END` means "the graph ran", so one `/ask` turn would run every phase
    in sequence.

    **The swap, when stage 7 lands the interrupt:** `return build_supervisor()`,
    delete this function's body, and rename the node from `define_phase` to
    `define`. Nothing in `gateway/routes.py` changes — it calls `get_graph()`
    and marshals the envelope, which is all §49 permits it to do.

    **The node keeps the name `define_phase` deliberately.** Renaming it to the
    supervisor's `define` would change every subgraph's `checkpoint_ns` from
    `define_phase:{task}` to `define:{task}`, orphaning the checkpoints written
    since 4.2. That costs nothing today — the input mapper rebuilds child state
    on every invoke — but it is a rename to make once, with the swap, rather
    than twice.
    """
    builder = StateGraph(SupervisorState)
    builder.add_node("define_phase", phase_node("define"))
    builder.add_edge(START, "define_phase")
    builder.add_edge("define_phase", END)

    checkpointer, store = _persistence()
    graph = builder.compile(checkpointer=checkpointer, store=store)
    logger.info(
        "Agent Improve turn graph compiled (runtime) — checkpointer=%s "
        "store=%s, wired phases: %s of %d",
        type(checkpointer).__name__ if checkpointer else None,
        type(store).__name__ if store else None,
        ", ".join(WIRED_PHASES), len(PHASE_ORDER),
    )
    return graph


__all__ = [
    "build_supervisor",
    "supervisor_builder",
    "get_graph",
    "phase_node",
    "escalate_node",
    "PhaseNotWired",
    "PHASE_ORDER",
    "RECURSION_LIMIT",
    "ESCALATE_NODE",
    "WIRED_PHASES",
    "INPUT_MAPPERS",
]
