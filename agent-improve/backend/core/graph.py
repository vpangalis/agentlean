"""The main graph — ONE compiled graph, entered at the case's current phase. ADR-0063.

Canonical: ADR-0063 (one runtime graph with phase entry; supersedes ADR-0023's "no router at
the parent"), ADR-0021 (one compiled graph), ADR-0017 (checkpointer and store on the parent
only), ADR-0024 (`thread_id` is the case). Requirements T89 (one builder, production and tests),
T90 (deterministic entry; approval advances the phase inside the graph), T3.

THE SHAPE
---------
    START → input_guard → route_to_phase ─(current_phase)→ {phase}_phase → END
                                        └─(blocked)→ END
                                             escalate → END   (reached by Command.PARENT)

`graph_builder()` is the ONLY builder. `get_graph()` compiles it once per process with the
checkpointer and store; every route and every test that needs the runtime graph uses it.

`route_to_phase` is a pure function of `state["current_phase"]` — no model call. Every Belt turn
is a new invocation, so the entry is the case's CURRENT phase, never a fixed start; there are
no phase-to-phase edges, and a turn ends at `END` after its one phase node.

THE WRAPPER NODE (`phase_node`)
-------------------------------
input mapper → `await subgraph.ainvoke(child)` → on approval, the output mapper. The subgraph
is invoked INSIDE the node function (S-F10), so its checkpoint namespace is derived from the
node name — `{phase}_phase`, kept from the per-phase graphs so a paused run resumes where it
paused. The config reaches the subgraph through LangGraph's run context.

A phase subgraph returns `final` only from `gate_apply` after the Belt's approval. When it
does, the output mapper writes the approved record to the Store at
`("projects", case_id, "artifacts")` / phase, and sets `current_phase`, `phase_index` and
`gate_passed` together (`mappers_common.advance`, their single writer). The next turn enters
the next phase through `route_to_phase`.

ESCALATION IS REACHED BY `Command.PARENT`
-----------------------------------------
A `Command(graph=Command.PARENT, goto="escalate")` raised inside the subgraph propagates as a
`ParentCommand` out of `subgraph.ainvoke`, through the wrapper node, to the parent's task
runner, which dispatches to `escalate` (verified on langgraph 1.2.11). The wrapper's code after
the invoke does not run on an escalation, so the output mapper is skipped — correct: an
escalated phase did not pass its gate.
"""
from __future__ import annotations

import asyncio
import logging
from functools import lru_cache
from typing import Any, Callable, Optional

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from backend.core import guard
from backend.core.checkpointer import get_checkpointer
from backend.core.state import SupervisorState
from backend.core.store import get_store
from backend.phases.analyse.mappers import analyse_input_mapper, analyse_output_mapper
from backend.phases.control.mappers import control_input_mapper, control_output_mapper
from backend.phases.define.mappers import define_input_mapper, define_output_mapper
from backend.phases.improve.mappers import improve_input_mapper, improve_output_mapper
from backend.phases.mappers_common import PHASE_ORDER
from backend.phases.measure.mappers import measure_input_mapper, measure_output_mapper
from backend.phases import record as phase_record
from backend.phases.subgraph_common import build_phase_subgraph

logger = logging.getLogger(__name__)

#: §16 — a backstop against genuine infinite loops, NOT the hop budget. The
#: per-turn hop cap is `RemainingSteps`, read inside the executor (§26).
RECURSION_LIMIT = 50

#: §13 — the escalation node's name at Level 1. It is the `goto` target of the
#: `Command(graph=Command.PARENT, ...)` the validation stack raises at stage 7,
#: so it is part of the contract between the two levels, not a local label.
ESCALATE_NODE = "escalate"

#: Every phase has a compiled subgraph as of procedure step 4.4 — this closed
#: WATCH 17. Kept as a named constant rather than inlined to `PHASE_ORDER`
#: because it answers a different question: `PHASE_ORDER` is the DMAIC sequence,
#: this is what the graph can actually run. They are equal now and a future
#: phase added to one must be added to the other consciously.
WIRED_PHASES: tuple[str, ...] = PHASE_ORDER

#: S-F10 / S-F12 — one input mapper per phase, all ten landed at step 3.3.
INPUT_MAPPERS: dict[str, Callable[..., Any]] = {
    "define": define_input_mapper,
    "measure": measure_input_mapper,
    "analyse": analyse_input_mapper,
    "improve": improve_input_mapper,
    "control": control_input_mapper,
}


#: S-F11 / S-F12 — one output mapper per phase; run by the wrapper node on approval (ADR-0063).
OUTPUT_MAPPERS: dict[str, Callable[..., Any]] = {
    "define": define_output_mapper,
    "measure": measure_output_mapper,
    "analyse": analyse_output_mapper,
    "improve": improve_output_mapper,
    "control": control_output_mapper,
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
            f"No compiled subgraph for phase {phase!r}; expected one of "
            f"{', '.join(WIRED_PHASES)}."
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
                f"Case is in phase {current!r}, which has no subgraph. Since "
                f"step 4.4 all five DMAIC phases are wired, so this is a case "
                f"whose `current_phase` is not a phase — `\"complete\"` on a "
                f"finished project is the ordinary way to reach here."
            )

        compiled = _subgraph(phase)          # raises PhaseNotWired until 4.4
        mapper = INPUT_MAPPERS[phase]

        store = get_store()
        child = await asyncio.to_thread(mapper, state, store)
        sent_messages = list(child["messages"])
        # ADR-0066: the record this turn merges into — what the input mapper seeded from.
        prior = {"structured": dict(child.get("artifacts") or {}),
                 "field_status": {f: dict(v) for f, v in (child.get("field_status") or {}).items()},
                 "field_log": [dict(e) for e in (child.get("field_log") or [])]}
        carried = phase_record.latest(state.get("messages") or [], phase)

        # ── the WATCH 7 seam, seeded at the boundary ──────────────────
        # `draft` is the v1 accumulator (see `phases/nodes_common.py`). The
        # mapper initialises it to `{}` because in the v2 design this turn's
        # extraction starts empty; until the v2 capture path lands it has to
        # carry what the case document already holds, or every turn re-extracts
        # against nothing. The OTHER phases' inputs ride on `config` and are
        # read by `to_v1_state` — every phase but Define builds a cross-phase
        # brief from them.
        seeded = (dict(carried.get("structured") or {}) if carried is not None
                  else (configurable.get("v1_phase_inputs") or {}).get(phase))
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
            "v1_draft": dict(result.get("draft") or {}),
            "gate_verdict": verdict,
            "turn_count": turn_count,
            # Step 6.33 — the turn's field change entries, on the same channel
            # and for the same reason as the draft above. **The subgraph's
            # state does not otherwise reach the route**: the child gets a
            # fresh `checkpoint_ns` per parent turn and the parent returns
            # `messages` and `history` only, so a `PhaseState` field the route
            # must persist has to ride out here or not at all.
            "field_log": [dict(e) for e in (result.get("field_log") or [])],
            # Step 6.61 (R5) — where each field stands after this turn.
            "field_status": {f: dict(v) for f, v in (result.get("field_status") or {}).items()},
            # G-148 (DEF-061) — this turn's citations; the record keeps them.
            "citations": [dict(c) for c in (result.get("citations") or []) if isinstance(c, dict)],
            # DEF-108 (W5) — the uploads this turn read; the record keeps them read.
            "uploads_consumed": {str(u["blob_path"]): str(u["consumed_at"])
                                 for u in (result.get("uploads") or [])
                                 if u.get("blob_path") and u.get("consumed_at")},
        }
        # ADR-0066: the merged record travels on the reply, so the checkpoint is its home.
        payload[phase_record.KEY] = phase_record.merge(prior, payload, phase)
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
        update: dict[str, Any] = {
            "messages": new_messages,
            "history": [
                s.get("key", f"{phase}:{turn_count}:?")
                for s in (result.get("step_log") or [])
            ],
        }
        # ADR-0063 — the subgraph returns `final` only from gate_apply after approval: the
        # output mapper writes the approved record to the Store and advances the phase.
        if result.get("final"):
            advanced = await asyncio.to_thread(OUTPUT_MAPPERS[phase], result, state, store)
            update.update(advanced)
            logger.info("%s: approved — record in the Store, current_phase -> %s",
                        phase, advanced.get("current_phase"))
        return update

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


# ── the main graph (ADR-0063) ──────────────────────────────────────────────

def route_to_phase(state: SupervisorState) -> str:
    """The phase entry — the "traffic light". Deterministic, no model call: a turn the input
    guard blocked ends here; otherwise the entry is `current_phase`'s node. A case whose phase
    has no subgraph (`"complete"`) raises."""
    if guard.blocked(state):
        return END
    current = state.get("current_phase")
    if current not in WIRED_PHASES:
        raise PhaseNotWired(
            f"Case is in phase {current!r}, which has no subgraph — `\"complete\"` on a "
            f"finished project is the ordinary way to reach here."
        )
    return f"{current}_phase"


def graph_builder() -> StateGraph:
    """THE builder (T89): production and tests compile this one. Uncompiled, so the
    topology can be asserted on the builder itself."""
    builder = StateGraph(SupervisorState)
    for phase in PHASE_ORDER:
        builder.add_node(f"{phase}_phase", phase_node(phase))
        builder.add_edge(f"{phase}_phase", END)
    builder.add_node(ESCALATE_NODE, escalate_node)
    builder.add_edge(ESCALATE_NODE, END)
    builder.add_node(guard.NODE, guard.input_guard)
    builder.add_edge(START, guard.NODE)
    builder.add_conditional_edges(guard.NODE, route_to_phase, [*(f"{p}_phase" for p in PHASE_ORDER), END])
    return builder


@lru_cache(maxsize=1)
def get_graph():
    """The ONE compiled graph every route invokes — compiled once per process with the
    checkpointer and store (ADR-0063, T89). `get_graph.cache_clear()` rebuilds it."""
    checkpointer, store = _persistence()
    graph = graph_builder().compile(checkpointer=checkpointer, store=store)
    logger.info(
        "Agent Improve graph compiled — %d phase nodes + %s, entry by current_phase; "
        "checkpointer=%s store=%s",
        len(PHASE_ORDER), ESCALATE_NODE,
        type(checkpointer).__name__ if checkpointer else None,
        type(store).__name__ if store else None,
    )
    return graph


__all__ = [
    "graph_builder",
    "route_to_phase",
    "get_graph",
    "phase_node",
    "escalate_node",
    "PhaseNotWired",
    "PHASE_ORDER",
    "RECURSION_LIMIT",
    "ESCALATE_NODE",
    "WIRED_PHASES",
    "INPUT_MAPPERS",
    "OUTPUT_MAPPERS",
]
