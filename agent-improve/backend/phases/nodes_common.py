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

import asyncio
import json
import logging
import re
from typing import Any, Awaitable, Callable, Literal, Optional, cast

from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelRetryMiddleware,
    SummarizationMiddleware,
    ToolRetryMiddleware,
)
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from backend.core.tracing import child_span
from langgraph.errors import GraphRecursionError
from langgraph.graph import END
from langgraph.types import Command

from backend.core.conversation import message_to_turn
from backend.core.llm import get_llm
from backend.core.prompts import (
    PHASE_COACH_PROMPT,
    PLANNER_JUDGMENT_PROMPT,
    PLANNER_JUDGMENT_READING_BACK,
)
from backend.core.state import ImproveGraphState
from backend.core.substate import (
    CoachingPlan,
    CoachingResponse,
    PhaseState,
    SufficiencyJudgment,
    field_log_key,
    presentational_gaps,
    split_captures,
)
from datetime import datetime, timezone

from backend.upload.asks import ensure_ask
from backend.knowledge.computation import (
    COMPUTATION_TOOLS,
    COMPUTATION_TOOLS_BY_PHASE,
)
from backend.phases.define.schema import DEFINE_FIELD_ORDER, define_progress
from backend.knowledge.tools import (
    RAG_LOOKUP_TOOLS,
    UNIVERSAL_TOOLS,
    first_numeric_column,
    load_evidence_series,
)
from backend.middleware.coherence import CoherenceMiddleware
from backend.middleware.contradiction import ContradictionDetectionMiddleware
from backend.middleware.grader import DMAICGraderMiddleware, MAX_ITERATIONS_WARNING
from backend.middleware.skills import (
    DMAICSkillsMiddleware,
    example_match,
    acceptance_criteria,
    field_needs,
    script_record,
)
from backend.phases import moves
from backend.middleware.state_injection import BeforeModelStateInjection
from backend.phases.gate_registry import review_rows, split_by_declared_type
from backend.phases.mappers_common import PHASE_ORDER

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



def _anchored(citations: list[dict], state: PhaseState) -> list[dict]:
    """Citations with `blob_path` and `content_digest` attached — step 6.12.

    **Enriched in CODE, never by the model** (clause 7). The coach is shown a
    `role` in the manifest and cites it; the anchor is looked up here, so a
    64-character digest never has to survive a round trip through a language
    model that was never shown it.

    **Matched on ROLE, not on filename.** Ruling AP2.2 forbids inferring a
    document's identity from what it is called, and matching on filename would
    reintroduce exactly that through the back door.

    **ONLY HALF OF CLAUSE 7 IS SATISFIABLE HERE, and the seam is deliberate.**
    A citation the coach made against an upload it saw in the manifest can be
    anchored now, because `PhaseState.uploads` carries both fields. **One
    sourced from `rag_lookup_evidence` cannot** — the structured record that
    would carry them is §24's, and that is step 6.13. Those citations pass
    through unanchored rather than being given a guessed anchor.
    """
    by_role = {u.get("role"): u for u in (state.get("uploads") or [])
               if u.get("role")}
    if not by_role:
        return [dict(c) for c in citations]

    out: list[dict] = []
    for citation in citations:
        entry = dict(citation)
        if entry.get("blob_path"):
            out.append(entry)
            continue
        source = str(entry.get("source") or "").strip().lower()
        match = next(
            (u for role, u in by_role.items()
             if role and (role.lower() in source or source in role.lower())),
            None,
        )
        if match is not None:
            entry["blob_path"] = match.get("blob_path")
            entry["content_digest"] = match.get("content_digest")
        out.append(entry)
    return out


def _mark_consumed(
    state: PhaseState, messages: list, citations: list[dict],
) -> tuple[list[dict], int]:
    """`(uploads, n_marked)` — stamp `consumed_at` on what this turn read.

    **S-F57 B4, placed at the node because a tool cannot write state.** An
    upload counts as consumed when `load_evidence_series` was called on its
    `blob_path`, or when a citation anchored to it.

    **`consumed_at = None` at a gate on an upload bound to an open ask means
    the Belt supplied evidence and the coaching proceeded without it.** That
    condition is undetectable without this write, which is why the field is
    part of 6.12 rather than of the Stage 7 validation that will read it.
    """
    uploads = [dict(u) for u in (state.get("uploads") or [])]
    if not uploads:
        return uploads, 0

    touched: set[str] = {
        str(c.get("blob_path")) for c in citations if c.get("blob_path")
    }
    for message in messages:
        for call in (getattr(message, "tool_calls", None) or []):
            if (call.get("name") if isinstance(call, dict) else None)                     == "load_evidence_series":
                args = call.get("args") or {}
                if args.get("blob_path"):
                    touched.add(str(args["blob_path"]))

    if not touched:
        return uploads, 0

    stamp = datetime.now(timezone.utc).isoformat()
    marked = 0
    for upload in uploads:
        if upload.get("blob_path") in touched and not upload.get("consumed_at"):
            upload["consumed_at"] = stamp
            marked += 1
    if marked:
        logger.info("executor: marked %d upload(s) consumed", marked)
    return uploads, marked


def _unconsumed_for_open_ask(
    state: PhaseState, asks: Optional[list[dict]] = None,
) -> dict | None:
    """An upload bound to an open ask that nothing has read yet — step 6.12.

    **This is what turns "the coach will use the file" from a hope into a
    fact.** §24 makes retrieval discretionary by design, so no prompt can
    carry the guarantee; per S-F13 DP1 the planner owns the routing decision
    and the planner is code.

    Matched on `role`, never on filename — ruling AP2.2 forbids inferring a
    document's identity from what it happens to be called.

    **`asks` IS EXPLICIT SINCE STEP 6.21, AND THAT IS A CORRECTNESS FIX.**
    Option C has the executor DISPATCH what this returns, so the planner and
    the executor must reach the same answer or the turn's prose and its action
    disagree. They read different states: the planner decides before its own
    `update["asks"]` is applied, the executor after. With Define carrying no
    ask shapes the two agreed by accident; in Measure, `ensure_ask` opening an
    ask for a role no upload carries would narrow `open_roles` between the two
    reads and the executor would dispatch nothing while the plan said to. The
    planner now passes the asks it just computed, so both sides decide on the
    same input by construction rather than by coincidence.
    """
    open_roles = {a.get("role") for a in
                  (asks if asks is not None else state.get("asks") or [])
                  if a.get("status") == "open"}
    for upload in state.get("uploads") or []:
        if upload.get("consumed_at"):
            continue
        if upload.get("role") in open_roles or not open_roles:
            return upload
    return None


async def planner(
    phase: str,
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> Command[Literal["executor", "validation_stack"]]:
    """Produce the `CoachingPlan` and make the phase's ONE routing decision.

    §13: the planner fires many times per phase, not once. After each executor
    step control returns here to decide whether to keep coaching the current
    field, advance to the next, or trigger the gate.

    **STEP 6.61 — THE MOVE IS DECIDED IN CODE** (founder ruling 2026-09-25,
    §17 v1.75). `_plan_turn` derives the focus field, its status and THIS
    TURN'S MOVE with `phases/moves.decide`; the `planner`-role model makes ONE
    judgment — is the Belt's answer sufficient, with a reason — and only when
    the Belt has answered. Until 6.61 the model chose the field and wrote the
    move as free text (`next_action`), which reached no channel the coach read
    (G-49) and so decided nothing: the coach waited after a read-back, moved
    on, or re-asked, turn by turn.

    **THE MODEL IS CALLED ONLY ON THE EXECUTOR-BOUND PATH**, and on it only when
    a judgment is needed. On the way to `validation_stack` the previous plan
    stands — B3 governs what happens when a NEW plan is produced, not that one
    must be.

    **THE ROUTING PREDICATE IS STILL A PLACEHOLDER** (G-01, founder-owned):

    ==========  ==============  ==========================
    ``entry``   ``turn_count``  goto
    ==========  ==============  ==========================
    ``gate``    any             validation_stack — validate
    ``ask``     0               executor — one coaching turn
    ``ask``     >0              validation_stack — walk out
    ==========  ==============  ==========================

    `turn_count` is incremented by the executor and reset by the input mapper,
    so the `ask` path visits the executor **exactly once per invoke**. That is
    what makes one `ainvoke` one Belt turn.
    """
    entry = entry_mode(config)
    turn_count = state.get("turn_count") or 0
    coached = turn_count > 0

    if entry == "gate":
        route, goto = "gate", "validation_stack"
    elif not coached:
        route, goto = "coach", "executor"
    else:
        route, goto = "close", "validation_stack"

    update: dict[str, Any] = {}
    entry_fields: dict[str, Any] = {}

    if goto == "executor":
        plan = await _plan_turn(phase, state, config)
        update["coaching_plan"] = plan

        # ── Ask-binding, step 6.12 (ruling AR-R1) ─────────────────────
        #
        # **The PLANNER derives the ask; the model never declares one.** Keyed
        # on ROLE, not on field (`ensure_ask`): Measure's baseline and
        # stability shapes are usually one file, so per-field asks would open
        # three for one upload and leave two permanently unanswered.
        asks = list(state.get("asks") or [])
        if plan.focus_field:
            asks = ensure_ask(asks, phase, plan.focus_field)
        if asks != list(state.get("asks") or []):
            update["asks"] = asks

        # **Routing on an unread upload is the guarantee's third leg.** The
        # executor dispatches the read itself (§17, 6.21 option C); the plan
        # carries no instruction for it — since 6.61 no free-text move exists
        # to carry one, and none ever reached the coach (G-49).
        pending_upload = _unconsumed_for_open_ask(state, asks)
        if pending_upload is not None:
            update["asks"] = asks
            logger.info(
                "%s.planner: routing to an UNREAD upload — role=%r path=%s",
                phase, pending_upload.get("role"), pending_upload.get("blob_path"),
            )

        entry_fields = {
            "focus_field": plan.focus_field,
            "field_status": plan.status,
            "move": plan.move,
            "stored_field": plan.stored_field,
            "judgment": plan.judgment.model_dump() if plan.judgment else None,
            "pending": bool(plan.pending),
            "retrieval_strategy": plan.retrieval_strategy,
            "retrieval_hops": len(plan.retrieval_hops),
        }
        logger.info(
            "%s.planner: entry=%s turn_count=%d -> %s | field=%s status=%s move=%s%s",
            phase, entry, turn_count, goto, plan.focus_field, plan.status, plan.move,
            f" judgment={plan.judgment.verdict}" if plan.judgment else "",
        )
    else:
        logger.info(
            "%s.planner: entry=%s turn_count=%d -> %s (%s) — no plan produced, "
            "the executor is not next",
            phase, entry, turn_count, goto, route,
        )

    update["step_log"] = [_step(
        phase, turn_count, "planner",
        goto=goto, route=route,
        status="planned" if entry_fields else "routed",
        reason="G-01 — DP1 is founder-owned; the routing predicate is the "
               "terminating placeholder, not a behavioural approximation",
        **entry_fields,
    )]
    return Command(
        goto=cast(Literal["executor", "validation_stack"], goto),
        update=update,
    )


def _retrieval_strategy(phase: str) -> str:
    """§28's per-phase DEFAULT. **Analyse is the one phase that plans
    multi-hop** — root-cause validation is layered. Since 6.61 no model plans
    the turn, so the default is the strategy: `retrieval_strategy` is set here
    and `retrieval_hops` stays empty."""
    return "multi_hop" if phase == "analyse" else "single_hop"


def _judgment_prompt(phase: str, state: PhaseState, field: str, previous: str,
                     latest: str, reading_back: bool) -> str:
    """The planner model's input for its one judgment — the field, what the
    phase script says it needs, this project's framing, and the Belt's words."""
    context = " ".join(str(state.get("phase_context") or "").split()) or \
        "(no phase context was composed)"
    return PLANNER_JUDGMENT_PROMPT.format(
        phase=phase, field=field,
        needs=field_needs(phase, field) or f"(the phase script gives no block for {field})",
        context=context[:1500],
        reading_back=PLANNER_JUDGMENT_READING_BACK if reading_back else "",
        previous=previous or "(none — the latest message is the first answer)",
        latest=latest or "(empty)",
    )


async def _judge(phase: str, state: PhaseState, field: str, previous: str,
                 latest: str, reading_back: str) -> SufficiencyJudgment:
    """THE PLANNER MODEL'S ONE JUDGMENT — a plain invocation, never an agent.

    **`planner` role, temperature 0.1** (§17, §4.7) — the role default, not an
    override. **Structured output, never JSON parsed out of raw text** (S-C04
    B1): a plain model call takes the builder-style form (§4.6). It dispatches
    to no tools.
    """
    judge = get_llm("planner").with_structured_output(SufficiencyJudgment)
    verdict = await judge.ainvoke(_judgment_prompt(
        phase, state, field, previous, latest, reading_back == "yes"))
    return _checked_criterion(phase, field, SufficiencyJudgment.model_validate(verdict))


def _checked_criterion(phase: str, field: str, j: SufficiencyJudgment) -> SufficiencyJudgment:
    """R3 — an 'insufficient' names one of THIS element's criteria, checked in
    code: an id the element does not list is replaced by the first listed id
    the reason QUOTES (`id`, 'id' or "id" — a bare word would match ordinary
    prose, "what is missing"), else cleared (and logged) rather than trusted.
    Only 'insufficient' carries one."""
    ids = [cid for cid, _ in acceptance_criteria(phase, field)]
    if j.verdict != "insufficient":
        return j.model_copy(update={"failed_criterion": None})
    crit = (j.failed_criterion or "").strip().strip("`").lower()
    if ids and crit not in ids:
        quoted = {q.lower() for q in re.findall(r"[`'\"]([a-z0-9-]+)[`'\"]", j.reason or "", re.I)}
        named = next((cid for cid in ids if cid in quoted), None)
        logger.info("%s.planner: the judgment named %r, not one of %s's criteria %s -> %r",
                    phase, j.failed_criterion, field, ids, named)
        crit = named or ""
    return j.model_copy(update={"failed_criterion": crit or None})


async def _plan_turn(phase: str, state: PhaseState,
                     config: Optional[RunnableConfig] = None) -> CoachingPlan:
    """This turn's plan: the move, decided in code (`moves.decide`).

    The status of every position is read from `artifacts` (confirmed) and from
    the move record the previous reply carries (taught, answered, a read-back
    awaiting confirmation); the Belt's latest message is the only other input.
    The model is asked for its judgment through `_judge`, and `decide` asks
    only when the field is answered and the reply is not a plain yes.
    """
    messages = list(state.get("messages") or [])

    async def judge(field: str, previous: str, latest: str, reading_back: str) -> SufficiencyJudgment:
        return await _judge(phase, state, field, previous, latest, reading_back)

    # R4 — a Confirm or Change click arrives on the request, not in the text;
    # the route puts it on `config` beside the entry mode.
    action = ((config or {}).get("configurable") or {}).get("belt_action")
    d = await moves.decide(phase, dict(state.get("artifacts") or {}),
                           dict(state.get("field_status") or {}),
                           moves.belt_message(messages), judge, action=action)
    return CoachingPlan(
        focus_field=d["field"], status=d["status"], move=d["move"],
        judgment=d["judgment"], answer=d["answer"], messages=d["messages"],
        pending=d["pending"], store=d["store"], stored_field=d["stored_field"],
        statuses=d["statuses"], field_status=d["field_status"], reason=d["reason"],
        retrieval_strategy=_retrieval_strategy(phase),
    )


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

#: §16 — a backstop against a genuine infinite loop, NOT the hop cap. Equal to
#: `core.graph.RECURSION_LIMIT` and kept as its own name because this module
#: cannot import that one: `core.graph` imports the phase subgraphs, which
#: import this file. `test_the_coach_backstop_matches_the_graph_backstop`
#: imports both and asserts they agree, so the two cannot drift silently.
#:
#: **It was 11 from step 6.2 to 6.6, and that was the WATCH 26 defect.**
#: `2 * max_hops + 1 = 11` was §3.7's formula for capping hops, which §16
#: rejects and which is short by one besides: measured on LangGraph 1.1.10 and
#: 1.2.11 alike, five hops consume all eleven steps and raise BEFORE the model can
#: compose, so a well-behaved five-hop turn could only ever end in `_CAP_MESSAGE`.
COACH_RECURSION_BACKSTOP = 50

#: What one hop COSTS, measured rather than assumed — the number that decides
#: the cap below, and the provenance is kept because a constant justified by a
#: measurement nobody can find is a constant nobody can revise.
#:
#: **§25's multi-query fusion makes a hop far more than one search**: one MODEL
#: CALL to generate variants, then six searches, then RRF. Measured **~9.5s**
#: on G-63's trace (2026-09-14) and consistent with rid `ca6ba417`
#: (2026-09-15), where three hops plus the coach's own calls reached 52.2s.
MEASURED_HOP_SECONDS = 9.5

#: Reserved out of the node budget for everything that is NOT a hop: the
#: coach's own model calls, and composing the answer. What is left over after
#: the cap's hops must still fit here or the turn degrades instead of capping.
HOP_BUDGET_COMPOSE_RESERVE = 10.0

#: §3.7 — `rag_lookup_*` calls per Belt turn. **This is the hop cap**, and
#: it is enforced by `_budgeted_rag_tools` rather than by any step counter:
#: hops and steps are different units (see `REMAINING_STEPS_FLOOR`). Past the
#: budget the retrieval tools stay bound and stay callable, and answer with
#: `_HOP_BUDGET_SPENT` instead of searching — so the coach reads a plain result
#: and composes, exactly as it does for a search that found nothing.
#:
#: **FIVE → THREE, founder ruling 2026-09-18, closing G-83.** Five was never
#: reachable: at `MEASURED_HOP_SECONDS` a fifth hop lands at ~47.5s against a
#: 40s node budget, so the turn died on the wall before the cap could fire and
#: `_HOP_BUDGET_SPENT` was unreachable code. **It was dead the day it was
#: written** — fusion landed at step 5.2 and the cap at 6.7, so the cap was
#: built on top of a per-hop cost that already excluded it.
#:
#: **THIS COSTS NO CAPABILITY.** Hops four and five could never be taken; the
#: declared cap now matches the ceiling that was always in force. What changes
#: is that the limit is REACHABLE, so the coach gets `_HOP_BUDGET_SPENT` and
#: composes — instead of the engine cancelling it mid-search.
#:
#: **The arithmetic is a TEST, not a comment**
#: (`test_hop_cap.py::test_the_cap_can_actually_fire_inside_the_node_budget`).
#: An unreachable cap is unfalsifiable, which is exactly how five survived
#: eleven steps.
COACH_HOP_BUDGET = 3

#: §26 / S-F09 B1 — the graceful off-ramp, and a DIFFERENT guard from the hop
#: budget above. `remaining_steps` is `recursion_limit` minus graph-node
#: transitions; the coach's whole tool loop runs inside ONE node, so this
#: counter moves by 1 per executor turn no matter how many hops that turn made.
#: Measured. It therefore cannot enforce five hops — and the hop budget cannot
#: notice the GRAPH running out of room, which is what this catches. At or
#: below the floor the executor coaches with no retrieval tools at all: it
#: composes from what is in hand rather than starting a chain it cannot finish.
REMAINING_STEPS_FLOOR = 2

#: §44 — the node's OWN wall, deliberately BELOW `EXECUTOR_RUN_TIMEOUT`.
#:
#: **The engine's `TimeoutPolicy` cancels this node FROM ABOVE ITS OWN BODY**
#: (`subgraph_common.py`), so none of the graceful paths below run and the
#: `NodeTimeoutError` reaches the route's bare `except Exception` as a 500 —
#: G-84, observed on rid `ca6ba417` at 52.219s against a 45s wall.
#:
#: **The fix is to finish FIRST.** The node budgets its own model loop at this
#: value and composes a degraded answer in the headroom that remains, so the
#: engine's wall is never reached and stays what it should be: a backstop for
#: a node that has stopped cooperating, not the ordinary failure path.
#:
#: **The headroom is for composing, which makes no model call** — marking
#: uploads consumed, attaching a diagram, building the step_log entry. Five
#: seconds is generous for that and cheap to hold back.
EXECUTOR_SOFT_BUDGET = 40.0

#: What the Belt reads when the coach ran out of time. **§4.8: never a hard
#: failure.** Addressed to the BELT, unlike `_HOP_BUDGET_SPENT` — it is the
#: turn's answer, not a tool result, and it says plainly what happened rather
#: than pretending the turn succeeded or returning nothing.
_TIMEOUT_MESSAGE = (
    "I ran out of time on that one before I could finish composing an answer "
    "— I was still gathering material when the turn's limit was reached. "
    "Nothing you have entered is lost." + chr(10) + chr(10) +
    "Asking me something narrower usually gets there: name the single field or "
    "figure you want, or point me at one uploaded file, and I will work from "
    "that rather than searching broadly."
)

#: What the coach reads when it has spent its five hops. Addressed to the
#: model, not to the Belt — it is a tool RESULT, and the coach's job on reading
#: it is to answer from what it already retrieved.
_HOP_BUDGET_SPENT = (
    "Retrieval budget for this turn is spent — you have made the {budget} "
    "lookups this turn allows. Do not search again. Answer the Belt now from "
    "what you have already retrieved and from the conversation, and say which "
    "part you would look into next turn if something is still missing."
)

#: What the Belt reads when the backstop fires. §3.7: a partial answer, never a
#: stack trace. It says what happened in plain language (§13) and hands the
#: turn back rather than pretending the coach finished. **Since 6.7 this is
#: the last-ditch path, not the ordinary one** — the hop budget and the
#: `remaining_steps` floor both off-ramp into a composed answer, so reaching
#: here means a genuine runaway loop, which is what §16 says the backstop is for.
_CAP_MESSAGE = (
    "I went further than I should have chasing that one down, and I have run "
    "out of room this turn. Could you narrow it slightly — a single question, "
    "or the one field you most want to work on — and I will pick it straight "
    "back up? Nothing you have told me is lost."
)

#: §19.3, verified against the installed `SummarizationMiddleware` before use
#: (§16.3 — this is where `max_retries` vs `retries` was learned). The current
#: parameter names are `trigger` and `keep`; `max_tokens_before_summary` and
#: `messages_to_keep` are the DEPRECATED spellings the class still warns on, so
#: a document copied from an older revision would look plausible and warn at
#: runtime rather than fail.
#:
#: 100_000 is ~78% of gpt-4o's 128k window; 20 turns of raw conversation are
#: kept below the summary. **Safe because facts do not live in `messages`** —
#: they are in `artifacts`, `step_log`, `citations` and the Store (§19.3).
#: Summarising conversation into prose is correct; summarising FACTS into prose
#: is the failure this policy prevents.
#: The `Literal` in each annotation is the installed signature's, not
#: decoration: `tuple[str, int]` type-checks here and is REJECTED at the call
#: site, because the middleware discriminates the trigger kind on that literal.
#: §19.4 and §19.5 — both retry middlewares, both at 2. **"Attempts after the
#: initial call"**, verified in source (`range(self.max_retries + 1)`), so this
#: is THREE attempts, not two.
#:
#: **This is one of three retry caps and they are not merged** (§19): model 2
#: here, `CoherenceMiddleware` 2 on response quality at 6.5, and the validation
#: stack's shared 3 at the gate (§34). Three different failure modes, three
#: counters, no shared state — merging any two would have a network flake
#: consume a gate attempt.
RETRY_MAX = 2

#: §19.5. **`"continue"` is current; `"return_message"` and `"raise"` are
#: DEPRECATED values the class still accepts and warns on** (verified against
#: the installed middleware — accepted is not the same as current, which is the
#: §16.3 distinction 6.3 learned on `SummarizationMiddleware`). The current set
#: is `"continue"`, `"error"`, or a callable.
TOOL_RETRY_ON_FAILURE: Literal["continue"] = "continue"

SUMMARIZATION_TRIGGER: tuple[Literal["tokens"], int] = ("tokens", 100_000)
SUMMARIZATION_KEEP: tuple[Literal["messages"], int] = ("messages", 20)

#: Which `additional_kwargs` key each diagram type rides on. **These are the
#: UI's names, read off `gateway/routes.py` and `ui/index.html`** — the route
#: lifts `sipoc_diagram` and `visualisation` off the reply and puts them in the
#: `/ask` envelope. A third diagram type needs a renderer before it needs a row.
_DIAGRAM_TO_UI_KEY = {
    "sipoc": "sipoc_diagram",
    "mindmap_5w2h": "visualisation",
}


def _routed_column(state: PhaseState, upload: dict) -> str | None:
    """The column to read, from the ask that solicited this upload.

    **Returns `None` when no ask declares one, and that is the G-63 fix.**

    It used to return a `"(not specified)"` placeholder, on the reasoning that
    the tool answers a miss by naming the columns the file DOES have (its B2
    path) and that this is a useful coaching move. **The reasoning was sound
    and the consequence was not.** `SHAPES_BY_PHASE["define"]` is empty by
    ruling AR-R2, so in Define NO ask ever declares a column — the placeholder
    was not an edge case there, it was every routed read. The tool could only
    answer `no_such_column`, the coach held no data and searched anyway, and
    the executor hit its 45s wall (trace `01a09ff4`). A read that can only
    fail is worse than no read, because the span still reports success.

    `None` is the honest answer: the ask layer has nothing to say. The caller
    decides whether to find a column elsewhere or to decline the dispatch.
    """
    for ask in state.get("asks") or []:
        if ask.get("status") == "open" and ask.get("role") == upload.get("role"):
            columns = (ask.get("expected_shape") or {}).get("columns") or []
            if columns:
                return str(columns[0])
    return None


# §51 / step 8.0 slice — the executor's setup, between node entry and the
# agent, is spanned so a trace shows where the pre-agent seconds go.
@child_span(run_type="chain", name="executor.setup.dispatch_routed_read",
           process_inputs=lambda i: {})
async def _dispatch_routed_read(state: PhaseState) -> list:
    """The planner's named call, EXECUTED HERE — §17, step 6.21, option C.

    **FOUNDER RULING 2026-09-11, and it changes what §17 means.** The planner
    owns the routing decision (S-F13 DP1) and G-49 was that the decision never
    reached the model: `executor()` invoked the agent with `{"messages":
    prior}`, so the one point in the loop that was not the model's discretion
    was, in fact, entirely the model's discretion. Options A and B put the
    instruction in front of the model and leave it free to rank a retrieval
    tool above it — which is the behaviour 6.18 measured, 18 evidence searches
    against a file the plan named. **C removes the decision from the model.**

    **SCOPED TO ONE CASE, deliberately.** This dispatches `load_evidence_series`
    and only when `_unconsumed_for_open_ask` routes to an unread upload. Every
    other tool stays model-chosen: §24's "no unconditional retrieval pipeline"
    is untouched, and nothing here decides WHAT to coach.

    **The result arrives as a real tool exchange**, an `AIMessage` carrying the
    call plus its `ToolMessage`, prepended to the turn's messages. Three things
    follow from that shape rather than from extra code: the coach reads the
    values as a tool result it can quote; `_mark_consumed` stamps `consumed_at`
    from the same call it already scans for; and the next turn's history shows
    the file was read, so the coach does not read it again.

    **No hop is spent.** §3.7's budget counts `rag_lookup_*` calls and
    `load_evidence_series` is not one — the same accounting as when the model
    issues it. A node-issued read that cost a hop would make the guarantee
    compete with the retrieval the coach still needs.

    **Fails soft, and says so.** A blob that cannot be read is a coaching fact,
    not a dead turn: the tool's own message carries it. An exception here
    returns no messages at all, leaving the manifest to make the coach aware —
    the pre-6.21 behaviour, which is degraded rather than broken.
    """
    upload = _unconsumed_for_open_ask(state)
    if upload is None or not upload.get("blob_path"):
        return []
    blob_path = str(upload["blob_path"])

    # ── the column: two sources and a refusal — G-63 ───────────────────
    #
    # 1. THE ASK that solicited the upload (§17, S-F13). Authoritative when it
    #    exists, because it is what the coach asked the Belt for.
    # 2. THE FILE'S OWN HEADER, when no ask declares one. Define populates no
    #    ask shapes (ruling AR-R2), so this is Define's normal path, not its
    #    exception. `first_numeric_column` owns the read — a parse here would
    #    be a second answer to a question `knowledge/tools.py` already owns.
    # 3. NEITHER — and then DO NOT DISPATCH. This is the half of the fix that
    #    is easy to miss: a read naming a column the file lacks IS G-63. The
    #    tool answers `no_such_column`, the coach holds nothing, and the span
    #    reports success either way. Declining leaves the manifest to make the
    #    coach aware — the pre-6.21 behaviour, degraded rather than broken,
    #    and §4.8's "never a hard failure to the Belt".
    column = _routed_column(state, upload)
    column_source = "ask"
    if column is None:
        column = await first_numeric_column(blob_path)
        column_source = "header"
    if column is None:
        logger.info(
            "executor: NOT dispatching a routed read of %s — no open ask "
            "declares a column and the file carries no numeric column. The "
            "coach keeps the manifest and the turn continues (G-63).",
            blob_path,
        )
        return []

    # Typed separately: a heterogeneous dict literal infers a value type the
    # args cannot be read back out of, and mypy is right to refuse it.
    args: dict[str, str] = {"blob_path": blob_path, "column": column}
    call: dict[str, Any] = {
        "name": "load_evidence_series",
        "args": args,
        "id": f"routed-{abs(hash(args['blob_path'])) % 10**12:012d}",
        "type": "tool_call",
    }
    try:
        result = await load_evidence_series.ainvoke(call)
    except Exception as exc:  # noqa: BLE001 — the turn survives a bad read
        logger.warning(
            "executor: the routed read of %s failed (%s) — the coach keeps the "
            "manifest and the turn continues",
            upload.get("blob_path"), exc,
        )
        return []

    logger.info(
        "executor: DISPATCHED the planner's call — load_evidence_series on %s "
        "[column=%s, from the %s] (§17, option C). The model was not offered "
        "this decision.",
        args["blob_path"], args["column"], column_source,
    )
    return [AIMessage(content="", tool_calls=[call]), result]


def _executor_status(hit_cap: bool, off_ramp: bool,
                     timed_out: bool = False) -> str:
    """The `step_log` status for one coaching turn — §10.3, dicts not tuples.

    Four outcomes, deliberately distinguished. **`"coached_no_retrieval"` is
    not a failure**: the graph was low on steps, so the coach answered from
    what it held (§26, S-F09 B1). That is the design working, and lumping it
    in with `"partial_cap_reached"` would hide exactly the signal WATCH 26
    needed — a turn that off-ramped cleanly looks nothing like one that died.

    **`"partial_timeout"` is the G-84 outcome and is FIRST, because it is the
    one that must never be silent.** A degraded turn that leaves no trace is
    the same error class G-84 closes — the Belt got an answer, so nothing else
    in the system would notice the coach never finished. This entry is what
    notices: `step_log` reaches the parent as `history` keys
    (`core/graph.py`), so it is checkpointed with the turn rather than living
    only in a log line.
    """
    if timed_out:
        return "partial_timeout"
    if hit_cap:
        return "partial_cap_reached"
    return "coached_no_retrieval" if off_ramp else "coached"


def _budgeted_rag_tools(
    tools: list[Any], budget: int, spent: list[int],
) -> list[Any]:
    """§3.7's five-hop cap — per-turn copies of the three `rag_lookup_*` tools.

    **This is where the hop cap lives**, and it is a count of retrieval calls,
    not a step counter. §16 rejects `recursion_limit` for this, and §26's
    `remaining_steps` cannot do it either: the whole coach loop runs inside one
    graph node, so `remaining_steps` moves by 1 per turn however many hops the
    turn made (measured — see `REMAINING_STEPS_FLOOR`). Neither counter can
    see a hop, so the hops are counted here.

    **Copies, made fresh per turn**, so the count cannot leak between turns or
    between concurrent cases. `model_copy` keeps `name`, `description`,
    `args_schema` and `response_format` exactly — §5.4 makes those docstrings
    load-bearing, and a hand-built replacement tool would quietly reword them.
    Only the coroutine is swapped.

    **Past the budget the tool still answers**, with `_HOP_BUDGET_SPENT` rather
    than a search. That is the graceful part: the coach reads an ordinary tool
    result, sees it has no more lookups, and composes — where a raised
    exception or a vanished tool would end the turn with nothing to say.

    `spent` is a one-element list rather than an `int` because the closure
    mutates it; `nonlocal` cannot reach a caller's local.
    """
    budgeted: list[Any] = []
    for original in tools:
        if original not in RAG_LOOKUP_TOOLS:
            budgeted.append(original)
            continue
        inner = original.coroutine

        async def guarded(_inner: Any = inner, **kwargs: Any) -> Any:
            if spent[0] >= budget:
                return (_HOP_BUDGET_SPENT.format(budget=budget), [])
            spent[0] += 1
            return await _inner(**kwargs)

        budgeted.append(original.model_copy(update={"coroutine": guarded}))
    return budgeted


def _executor_tools(
    phase: str, hop_budget: int, hops_spent: Optional[list[int]],
) -> list[Any]:
    """What the coach gets to call this turn — the two guards, applied.

    **`hop_budget == 0` is the `remaining_steps` off-ramp** (§26, S-F09 B1):
    the three `rag_lookup_*` tools are not bound at all, so the coach cannot
    start a retrieval chain the graph has no room to finish. **The other four
    of the universal seven stay**, and so do the phase's computation tools —
    the off-ramp is about not STARTING new retrieval, not about coaching with
    one hand tied. `propose_template`, `propose_diagram`, `check_gate_status`
    and `request_human_approval` all read state the executor already holds.

    Any other budget binds all seven, with the retrieval three counted (§3.7).
    """
    tools = UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]
    if hop_budget <= 0:
        return [t for t in tools if t not in RAG_LOOKUP_TOOLS]
    return _budgeted_rag_tools(tools, hop_budget, hops_spent
                               if hops_spent is not None else [0])


@child_span(run_type="chain", name="executor.setup.build_executor",
           process_inputs=lambda i: {"phase": i.get("phase")},
           process_outputs=lambda o: {})
def _build_executor(
    phase: str, state: PhaseState, config: Optional[RunnableConfig] = None,
    *, hop_budget: int = COACH_HOP_BUDGET, hops_spent: Optional[list[int]] = None,
    script_log: Optional[list[dict[str, Any]]] = None,
    coherence_log: Optional[list[dict[str, Any]]] = None,
) -> tuple[Any, list[dict[str, Any]]]:
    """The phase coach — `create_agent`, per §18's ratified template.

    **Both parameter names were verified against the installed
    `langchain.agents.create_agent`** (§16.3, and CLAUDE.md §0.10 records what
    it cost last time): the signature carries `system_prompt` and has **no**
    `prompt` parameter, so `prompt=` would raise `TypeError` at construction
    rather than being silently ignored.

    **Tools are passed to `create_agent(tools=...)`, never bound onto the
    model.** Binding onto a bare model bypasses the entire middleware stack
    (§18) — grading, skills, compression, state injection, retry, coherence and
    contradiction — and does it silently.
    `pattern-8-bind-tools-in-phase-executor` guards this file for that reason.

    **MIDDLEWARE POSITIONS 1-3 MOUNT HERE (step 6.3).** Declaration order is
    execution order for hooks of the same kind, so this order is binding
    (§19). `BeforeModelStateInjection` MUST be first — project facts have to
    reach the top of the prompt before skills loading and summarisation shape
    it (§19, S-C11 B4). Positions 4-5 land at 6.4 and 6-8 at 6.5.

    **The system prompt is now STATIC per phase.** Step 6.2 composed this
    turn's project facts into it by hand, because there was no middleware to
    do it; §19.1 is the ratified home and that hand-composition came out at
    6.3. Leaving both would inject the same facts twice — once from the
    middleware and once from the prompt — and the second copy would be the one
    that drifted, because only one of them is derived from the shared gate
    computation.

    Still constructed per turn: the two custom middlewares are built with this
    turn's state, so the agent cannot outlive it. That is cheap next to the
    model call it wraps.
    """
    # B6's sink. A list the node owns, so the middleware writes an audit
    # record without reaching into state — which is what keeps B7's
    # "internals never reach PhaseState" true by construction.
    grader_log: list[dict[str, Any]] = []
    # Built here rather than inline because position 8 holds a reference to it:
    # a dict returned from one `after_agent` is NOT visible to the next hook in
    # the same pass, so S-C13 B3's skip cannot travel through state. Per turn,
    # so the reference cannot outlive the turn (B7).
    #
    # G-96 — told the planner's focus field, so a reply that captures nothing
    # is judged against the step that teaches it, and handed a sink so every
    # verdict reaches `step_log` the way the grader's does.
    plan = state.get("coaching_plan")
    coherence = CoherenceMiddleware(
        phase, focus_field=plan.focus_field if plan else None,
        on_verdict=coherence_log.append if coherence_log is not None else None,
    )
    agent = create_agent(
        model=get_llm("coach", max_tokens=1500),
        tools=_executor_tools(phase, hop_budget, hops_spent),
        response_format=CoachingResponse,   # §20 — never a {Phase}Output
        middleware=[
            # 1 — before_agent. FIRST, and that is a rule, not a preference.
            BeforeModelStateInjection(
                phase, state, config,
                prior_documents=_prior_gate_documents(phase, config),
            ),
            # 2 — before_agent + a registered `load_skill` tool.
            DMAICSkillsMiddleware(
                phase,
                # 6.46 — each delivery of the phase script, for step_log.
                on_delivery=script_log.append if script_log is not None else None,
                # 6.61 (item 4) — the current field's block; the opening only
                # while the conversation holds no coach reply.
                focus_field=plan.focus_field if plan else None,
                opening=not any(isinstance(m, AIMessage) for m in (state.get("messages") or [])),
            ),
            # 3 — before_model. LangChain core, used as shipped (§19.3).
            SummarizationMiddleware(
                model=get_llm("summarizer"),
                trigger=SUMMARIZATION_TRIGGER,
                keep=SUMMARIZATION_KEEP,
            ),
            # 4 — wrap_model_call. The INVISIBLE retry tier (§19.4): the
            # network flaked, so retry the same call. Distinct from §4.8's
            # fallback chain, which swaps the model. `max_retries` is
            # "attempts after the initial call", so 2 means three attempts.
            ModelRetryMiddleware(max_retries=RETRY_MAX),
            # **The same nesting rule, one layer out.** Position 1 is declared
            # first, so it is the OUTERMOST layer — and since 6.3 it also wraps
            # the model call. Its wrap therefore encloses this retry, which is
            # why the project-state block is composed and prepended ONCE and a
            # retry re-sends the built request rather than rebuilding it per
            # attempt. Measured: 3 model calls, 1 composition, 1 prepend.
            #
            # §19 calls positions 4 and 5 independent of everything else. That
            # was true before 6.3 and is not now — and it is the same conflation
            # as the trio below: declaration is nesting, positions are
            # execution. `test_position_1_wrap_encloses_position_4_retry` pins
            # it, because if the layering inverted, three attempts would mean
            # three Store reads and three missing-field computations.
            #
            # 5 — wrap_tool_call. A failed retrieval is not a failed model
            # call and `ModelRetryMiddleware` never sees it (§19.5).
            # `on_failure="continue"` is what keeps the coaching loop alive:
            # the coach reads a failure result and works around it instead of
            # the graph dying mid-session.
            ToolRetryMiddleware(
                max_retries=RETRY_MAX, on_failure=TOOL_RETRY_ON_FAILURE,
            ),
            # ══════════════════════════════════════════════════════════════
            # THIS LIST IS NESTING ORDER. POSITIONS 6/7/8 ARE EXECUTION ORDER.
            #
            #   **The list is outermost-first** — LangChain's documented model,
            #   "first in list as outermost layer". A `before_*` hook fires on
            #   the way in (outermost first) and an `after_*` hook on the way
            #   out (innermost first). Two different orderings, one list.
            #
            #   **Grader outermost**, because a final quality verdict should be
            #   the last thing to touch the answer on its way out.
            #   **Contradiction innermost**, because it should be first to see
            #   the coach's raw output and able to interrupt before anything
            #   else spends effort on it. Coherence sits between them so it can
            #   stand the grader down.
            #
            #   So the layering below IS the intent, not a workaround for it,
            #   and the execution order it produces is §19's 6, 7, 8.
            #   `test_the_declared_middleware_list_is_the_ratified_layering`
            #   asserts what executes, not what is listed.
            #
            #   LangChain offers no other control: no priority, no ordering
            #   attribute, and `hook_config` governs `can_jump_to` rather than
            #   sequence. List position is the only lever there is.
            # ══════════════════════════════════════════════════════════════
            DMAICGraderMiddleware(
                phase, on_evaluation=grader_log.append, coherence=coherence,
                # 6.61 (item 3) — graded as the move it was asked to make.
                move=plan.move if plan else None,
            ),
            coherence,
            ContradictionDetectionMiddleware(),
        ],
        system_prompt=PHASE_COACH_PROMPT[phase],   # NOT `prompt=` (§18)
    )
    return agent, grader_log


@child_span(run_type="chain", name="executor.setup.prior_gate_documents",
           process_outputs=lambda o: {"documents": len(o) if isinstance(o, dict) else None})
def _prior_gate_documents(
    phase: str, config: Optional[RunnableConfig] = None
) -> dict[str, dict]:
    """Earlier phases' approved values, for S-C11 B5.

    **Read from the seam that carries them today.** §9 makes the Store the
    home of cross-phase gate documents and `gate_apply` the writer — and
    `gate_apply` writes nothing until stage 7 (DECISIONS Z2), so there is
    nothing in the Store to read yet. What exists is `v1_phase_inputs` on
    `config`, which the route already assembles from the case document for
    every phase.

    **This is the seam, not the design.** When `gate_apply` starts writing at
    stage 7, this reads the Store instead — and B5 is why it matters that it
    reads something: without prior committed values in the prompt the coach has
    nothing to compare against, and §37's contradiction check silently detects
    nothing, which is the exact failure of the mechanism it replaced.
    """
    configurable = (config or {}).get("configurable") or {}
    prior = configurable.get("v1_phase_inputs") or {}
    upto = PHASE_ORDER.index(phase)
    return {
        name: dict(values)
        for name, values in prior.items()
        if values and name in PHASE_ORDER[:upto]
    }


def _captured_fields(phase: str, reply: CoachingResponse) -> dict[str, Any]:
    """`fields_captured` -> the dict written into `artifacts` (§20, S-F04 B4).

    **Entries without a `field_name` are dropped, not guessed.** The coach is
    told the exact names; an entry that does not carry one is a malformed
    capture, and inferring which field was meant is how a value lands under the
    wrong key and reaches a gate document unnoticed.

    `value` stays whatever the model sent — `Any`, deliberately (§20): it must
    carry both plain strings and the three cross-phase reference dicts, and
    coercing to `str` here would make `causal_hypothesis` uncapturable.
    """
    out: dict[str, Any] = {}
    for entry in reply.fields_captured or []:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("field_name") or "").strip()
        if not name:
            logger.warning(
                "%s.executor: dropped a capture with no field_name: %r",
                phase, entry,
            )
            continue
        out[name] = entry.get("value")
    return out


def _turn_ordinal(state: PhaseState) -> int:
    """Which Belt turn this is, counted in the conversation itself — step 6.33.

    **NOT `turn_count`, and the difference is load-bearing.** `turn_count` is
    seeded to `0` by the input mapper on every invoke and read by `core/graph.py`
    as the ENTRY MODE — `0` means "coach one turn", non-zero means "we are here
    for the gate" — so on a coaching turn it is `0` every time. That is why
    every `step_log` key of every turn of a phase reads `{phase}:0:{node}`. A
    change log keyed on it would have each turn overwrite the one before, which
    is the defect this step exists to end, reproduced in the fix.

    **The conversation is the one thing that does accumulate**: the parent's
    `messages` carry it across turns and the input mapper copies it down, so the
    number of Belt messages IS the turn ordinal. It is also stable under a
    REPLAY — a resumed turn has the same conversation and so the same ordinal —
    which is what makes §11's key idempotent rather than merely unique.
    """
    return sum(1 for m in (state.get("messages") or [])
               if isinstance(m, HumanMessage))


def _field_log_entries(
    phase: str,
    turn: int,
    captured: dict[str, Any],
    prior: dict[str, Any],
    reply: CoachingResponse | None,
    at: str,
) -> list[dict[str, Any]]:
    """One entry per CHANGE this turn made to a captured field — step 6.33.

    **The first capture of a field is a change too**, and carries
    `prior_value: None`. A re-statement of the value already held is NOT: the
    Belt repeating themselves is not a revision, and logging it would bury the
    revisions that matter under turns where nothing moved.

    **`reason` is the Belt's stated reason WHERE GIVEN, and today it is given
    nowhere — G-89.** It is read from a `reason` key on the capture entry, which
    `CoachingResponse.fields_captured` permits — the entries are free-form
    dicts — but which nothing asks the coach to supply. So it will be `None` on
    every turn until the schema's field description asks for one, and that is a
    §56 amendment to `CoachingResponse` rather than something to slip in here.
    **Recorded as a known-empty column rather than left out**: a column that
    exists and is empty says "nobody was asked"; a column that does not exist
    says nothing at all, and the next reader has to rediscover why.

    `prior_value: None` also reads as "first capture" when the prior value was
    itself empty. Unambiguous going forward — `split_captures` keeps empty
    values out of `artifacts` from this step on — and not reconstructable for
    anything captured before it.
    """
    reasons: dict[str, str] = {}
    for entry in ((reply.fields_captured if reply else None) or []):
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("field_name") or "").strip()
        reason = str(entry.get("reason") or "").strip()
        if name and reason:
            reasons[name] = reason

    entries: list[dict[str, Any]] = []
    for field, value in captured.items():
        seen = field in prior
        if seen and prior[field] == value:
            continue
        entries.append({
            "key":         field_log_key(phase, turn, field),
            "field":       field,
            "phase":       phase,
            "turn":        turn,
            "value":       value,
            "prior_value": prior[field] if seen else None,
            "timestamp":   at,
            "reason":      reasons.get(field),
        })
    return entries


#: How the installed LangChain renders the structured response into the
#: conversation (`langchain/agents/factory.py`: f"Returning structured
#: response: {structured_response}"). Matched EXACTLY before a rewrite, so a
#: framework that renders it differently leaves the message untouched.
_STRUCTURED_PREFIX = "Returning structured response: "


def _with_progress(messages: list, reply: CoachingResponse, label: str) -> list:
    """Set `reply.progress` to the computed step, and re-render the one
    structured-response message that carried the model's count (6.57).

    A new `ToolMessage` with the same id, name and `tool_call_id`, so the
    tool-call pairing the next model call depends on is unchanged. Plain
    string content, which §21 allows for a message this code constructs.
    """
    before = f"{_STRUCTURED_PREFIX}{reply}"
    reply.progress = label
    after = f"{_STRUCTURED_PREFIX}{reply}"
    return [
        ToolMessage(content=after, tool_call_id=m.tool_call_id, name=m.name, id=m.id)
        if isinstance(m, ToolMessage) and m.content == before else m
        for m in messages
    ]


#: §50.1's render contract — the blocks besides `message`, in render order.
COACHING_BLOCKS: tuple[str, ...] = ("explanation", "example", "prompt", "progress")


def _attach_blocks(messages: list, reply: CoachingResponse | None,
                   warning: str | None) -> None:
    """Put this turn's §50.1 blocks, and the grader's warning, on the reply.

    Step 10.0. **Beside `message`, never instead of it:** the AI message's
    content stays `message` — the transcript entry, what `messages` and
    summarisation carry — and the blocks ride on `additional_kwargs`, the
    channel `_attach_diagram` already uses for a turn's extras. Mutates in
    place — the last AI message is the reply.
    """
    if reply is None and warning is None:
        return
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            if reply is not None:
                msg.additional_kwargs["coaching_blocks"] = {
                    k: str(getattr(reply, k, "") or "") for k in COACHING_BLOCKS}
            if warning:
                msg.additional_kwargs["grader_warning"] = warning
            return


def _move_record(plan: CoachingPlan | None, pending: dict | None,
                 stored: dict[str, Any]) -> dict[str, Any] | None:
    """What the next turn's planner reads to know where this field stands —
    step 6.61. The field this reply worked on, the move, the Belt's words so
    far, the read-back awaiting confirmation (PENDING), what was stored."""
    if plan is None:
        return None
    carries_answer = plan.move in (moves.CHALLENGE, moves.READ_BACK, moves.RESPOND)
    return {
        "field": plan.focus_field,
        "move": plan.move,
        "status": plan.status,
        "answer": plan.answer if carries_answer else "",
        "messages": plan.messages if carries_answer else 0,
        "pending": pending,
        "stored": sorted(stored),
        "stored_field": plan.stored_field,
        "judgment": plan.judgment.model_dump() if plan.judgment else None,
    }


def _quality_feedback(grader_log: list[dict[str, Any]],
                      coherence_log: list[dict[str, Any]]) -> dict[str, Any] | None:
    """This turn's quality verdicts, for the NEXT turn's section 5 (§19.1
    v1.75): the grader's failed criteria with their feedback, and coherence's
    verdict. `None` when neither judge ran."""
    g = grader_log[-1] if grader_log else None
    c = coherence_log[-1] if coherence_log else None
    if g is None and c is None:
        return None
    return {
        "grader": ({"status": g.get("status"), "criteria_failed": list(g.get("criteria_failed") or []),
                    "feedback": list(g.get("feedback") or []),
                    "failed": list(g.get("failed") or []), "move": g.get("move")} if g else None),
        "coherence": ({"coherent": c.get("coherent"), "reason": c.get("reason") or ""}
                      if c else None),
    }


def _attach_move(messages: list, record: dict | None, feedback: dict | None) -> None:
    """Put the move record and the quality feedback on the reply — the last AI
    message, the channel `_attach_blocks` uses. Mutates in place."""
    if record is None and feedback is None:
        return
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            if record is not None:
                msg.additional_kwargs[moves.MOVE_RECORD_KEY] = record
            if feedback is not None:
                msg.additional_kwargs[moves.QUALITY_FEEDBACK_KEY] = feedback
            return


def _script_ask(phase: str, field: Optional[str]) -> str:
    """The script's own question for `field` (its `**Ask:**` line)."""
    for line in field_needs(phase, field or "").splitlines():
        text = line.lstrip("> ").strip()
        if text.startswith("**Ask"):
            return text.split(":**", 1)[-1].strip()
    return f"Could you tell me about your {(field or 'next step').replace('_', ' ')}?"


def _fallback_reply(phase: str, plan: Optional[CoachingPlan]) -> CoachingResponse:
    """The move's reply, written by CODE — step 6.61 (item 1).

    Used when the coach model did not finish (the node's time budget, or the
    runaway backstop). The move is already decided, so the Belt still gets
    that move — never a message about the system running out of room."""
    if plan is None:
        return CoachingResponse(message=_script_ask(phase, None), prompt=_script_ask(phase, None))
    label = (plan.focus_field or "").replace("_", " ")
    ask = _script_ask(phase, plan.focus_field)
    words = str((plan.pending or {}).get("belt_words") or plan.answer or "").strip()
    if plan.move == moves.READ_BACK:
        text, prompt = f'Here is your {label}, as you gave it: "{words}"', "Is this right?"
    elif plan.move == moves.CHALLENGE:
        need = plan.reason or (plan.judgment.reason if plan.judgment else "")
        text, prompt = f"Thanks — for your {label} there is one more thing I need. {need}", ask
    elif plan.move == moves.STORE_AND_ADVANCE:
        stored = (plan.stored_field or "").replace("_", " ")
        text = f"Recorded — your {stored} is stored." + (f" Next: your {label}." if label else "")
        prompt = ask if plan.focus_field else "Everything in this phase is confirmed."
    else:
        text, prompt = (f"Let's look at your {label}." if label else "Every field is confirmed."), ask
    return CoachingResponse(message=text + chr(10) * 2 + prompt, prompt=prompt)


#: The question a Change click is answered with (ruling on 6.61's review).
CHANGE_QUESTION = "What would you like to change?"


def _change_reply(plan: Optional[CoachingPlan]) -> Optional[CoachingResponse]:
    """R4's Change click, answered IN CODE — founder ruling on 6.61's review,
    2026-09-25: the Belt's exact current words, then the one question. No
    model call: live, the model asked the question but left the words out in
    3 of 3 runs, so nothing here is left to it. `None` for every other move."""
    if plan is None or plan.move != moves.CHALLENGE or plan.reason != moves.CHANGE_REASON:
        return None
    words = str((plan.pending or {}).get("belt_words") or plan.answer or "").strip()
    return CoachingResponse(message=words + chr(10) * 2 + CHANGE_QUESTION,
                            prompt=CHANGE_QUESTION)


def _conversation(messages: list) -> list:
    """The conversation as the coach is shown it — step 6.61 (item 4, section
    6): each Belt message, and each coach turn as ONE message carrying its
    reply text. A coach turn's tool-call stubs and the framework's
    "Returning structured response" message are dropped; a turn with no reply
    text (a timeout) contributes nothing. Built fresh — the stored messages
    are never edited (§21: content is read through `.text`)."""
    out: list = []
    for m in messages:
        if isinstance(m, HumanMessage):
            out.append(HumanMessage(content=m.text))
        elif isinstance(m, AIMessage) and m.text.strip():
            if out and isinstance(out[-1], AIMessage):
                out[-1] = AIMessage(content=m.text)      # one entry per coach turn: its last text
            else:
                out.append(AIMessage(content=m.text))
    return out


def _with_coaching_text(messages: list, reply: CoachingResponse) -> list:
    """Guarantee the Belt-facing prose is present in `messages`.

    §18: *"the structured response and the coaching text coexist"* — the agent
    writes prose into `messages` AND returns the structured response. The two
    normally carry the same text. **When the terminal message has no text**, as
    happens when a provider puts everything in the structured payload, the
    Belt would otherwise get an empty turn, so `reply.message` is appended.
    """
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and str(msg.content).strip():
            return messages
    return [*messages, AIMessage(content=reply.message)]


#: The twenty computation tools, by name. Derived from the registry rather
#: than typed, so a tool added at 5.3's successor is picked up here without a
#: second list to remember — the failure `MARKER_HOME` was deleted for.
_COMPUTATION_TOOL_NAMES: frozenset = frozenset(
    t.name for t in COMPUTATION_TOOLS
)


def _computation_results(
    messages: list, phase: str, turn: int,
) -> list[dict]:
    """§7's five-key rows for the computation tools THIS turn called.

    **The same inspection `_mark_consumed` already does, over a different tool
    set.** Ruling AR-R4: *a `@tool` receives only its arguments and cannot
    reach `PhaseState`, so the node inspects the turn's tool calls afterwards.*
    No new pattern, and `computation.py` says the rest outright — each tool
    returns the `result` sub-dict and *"the executor wraps it in §7's full
    `{"tool", "inputs", "result", "turn", "phase"}` shape … the turn and phase
    are not knowable here."*

    **THE GRADER IS WHY THIS IS NOT A DICT KEY.** §35 and §41 have it answer
    *"was a hypothesis test actually run?"* by scanning this list for
    `"tool": "t_test"` rather than by reading the coach's prose — the whole
    anti-hallucination design. Against a list nothing wrote, its answer was
    always **no**, and a gate document recorded that a project did no analysis
    whatever the Belt and the coach actually did.

    **The result is read as JSON, not parsed by hand.** LangChain serialises a
    `dict`-returning tool into the `ToolMessage`'s content as JSON — verified
    against the installed library rather than assumed:

        calculate_sigma_level -> '{"sigma_level": "3.76", "dpmo": "12000", …}'

    so `json.loads` recovers `Result` exactly. G-48 records what hand-parsing a
    structured payload costs; this is the same shape and takes the standard
    format instead. A tool whose content stops being JSON lands in the row as
    a `parse_error` rather than vanishing — **a computation that ran and could
    not be recorded is a finding, and dropping it silently would leave the
    grader in exactly the state this step exists to end.**
    """
    by_id: dict[str, ToolMessage] = {
        str(m.tool_call_id): m
        for m in messages
        if isinstance(m, ToolMessage) and getattr(m, "tool_call_id", None)
    }
    rows: list[dict] = []
    for message in messages:
        for call in (getattr(message, "tool_calls", None) or []):
            if not isinstance(call, dict):
                continue
            name = call.get("name")
            if name not in _COMPUTATION_TOOL_NAMES:
                continue
            reply = by_id.get(str(call.get("id")))
            if reply is None:
                continue
            raw = reply.content if isinstance(reply.content, str) else ""
            try:
                result = json.loads(raw)
            except (ValueError, TypeError):
                result = {"parse_error": raw[:200]}
            if not isinstance(result, dict):
                result = {"parse_error": str(result)[:200]}
            rows.append({
                "tool": str(name),
                "inputs": dict(call.get("args") or {}),
                "result": result,
                "turn": turn,
                "phase": phase,
            })
    return rows


def _advance_field_index(phase: str, artifacts: dict) -> int | None:
    """Where the coach is in the phase's ordered field list, or `None`.

    §39.x.7 says `field_index` *"walks the §39.x.2 list"*. It was set to `0` by
    the input mapper and **advanced by nothing**, so it indexed the first field
    for the whole phase.

    **Define only, and that is the step's scope rather than an omission.** Only
    Define has an ordered `DEFINE_FIELD_ORDER`; Measure, Analyse, Improve and
    Control expose tier SETS, so the §39.x.2 sequence does not exist in code
    for four of the five phases whose §39.x.7 tells this to walk it. Returning
    `None` for those four leaves `field_index` untouched rather than writing a
    number derived from an order nobody declared — **a number that looks
    walked and is not is worse than one that never moved**, which is what the
    original `0` at least made obvious.

    The index is the first field NOT yet captured, so it names what to work on
    next; once every field is in, it rests on the LAST field rather than
    running off the end, because there is no next one to point at.

    **6.57 — it is `define_position` minus one**, the same computation the
    Belt's "Step n of 13" is delivered from, so the index the planner walks
    and the step the Belt is told cannot disagree. That moves one case:
    position 5 now waits for `metric_definitions` as well as
    `baseline_estimate` (§39.1.9).
    """
    if phase != "define" or not DEFINE_FIELD_ORDER:
        return None
    return int(define_progress(artifacts)["position"]) - 1


def _attach_diagram(messages: list) -> None:
    """Lift this turn's `propose_diagram` payload onto the reply, for the UI.

    `gateway/routes.py` reads `sipoc_diagram` and `visualisation` off the
    reply's `additional_kwargs`; the v1 orchestrator used to put them there.
    The tool returns its payload as a ToolMessage **artifact** rather than as
    content, so this reads a real dict instead of parsing one back out of a
    string. Mutates in place — the last AI message is the reply.
    """
    payload = None
    for msg in messages:
        if isinstance(msg, ToolMessage) and isinstance(
                getattr(msg, "artifact", None), dict):
            artifact = dict(msg.artifact)
            key = _DIAGRAM_TO_UI_KEY.get(str(artifact.pop("diagram_type", "")))
            if key:
                payload = (key, artifact)
    if payload is None:
        return
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            msg.additional_kwargs[payload[0]] = payload[1]
            return


async def executor(
    phase: str,
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> dict[str, Any]:
    """Run one coaching turn. **Returns plainly — emits no routing `Command`.**

    §17: the executor consumes the plan and decides no strategy. Control returns
    to the planner on the static edge, and the planner chooses what happens next.

    **THIS IS THE V2 FIELD WRITER, AND ITS EXISTENCE CLEARS WATCH 7.** Step 6.2
    replaces the v1 delegation with `create_agent` +
    `response_format=CoachingResponse` (§18, §20). `fields_captured` is written
    into `artifacts` under the §39.x names — which is what `validate_{phase}`
    has been reading since the rename, and why every phase's gate was inert
    until now (DECISIONS Part X, Route A). **`orchestrate.py` and
    `EXTRACTION_{PHASE}` are now dead code awaiting deletion at 11.1**; nothing
    calls them, and per the ruling they are not migrated.

    **§17's contract, and what step 6.21 changed about it.** The coach decides
    no strategy: it does not pick the field, does not choose the retrieval mode,
    and does not route.

    **That sentence was FALSE between steps 6.2 and 6.21 and this docstring
    asserted it anyway.** It said the contract was "now fully true" and that the
    coach "is told the plan's `focus_field`" — the coach was told neither. The
    plan reached no channel the model reads (G-49, diagnosed at 6.18 as layer
    2: system prompt 7,770 chars, injected block 797, messages 5, and the
    planner's imperative in none of them). A docstring claiming a contract holds
    is the last place a reader looks for the news that it does not.

    **It is true now, for the one case the planner routes**: an unread upload's
    read is dispatched by this node (`_dispatch_routed_read`), so the model is
    not offered that decision at all. Everything else the coach calls is still
    the coach's choice, and the plan's `focus_field` still reaches the model
    through nothing — which is transport A or B's job if it is ever wanted, and
    is NOT claimed here.

    **Middleware positions 1–3 are mounted as of step 6.3** (§19); 4–5 land at
    6.4 and 6–8 at 6.5. So the per-turn project facts now arrive through
    `BeforeModelStateInjection` rather than being composed into the prompt
    here — 6.2 did that by hand only because there was no middleware to do it,
    and leaving both would inject the same facts twice. One consequence is
    still live and is not a defect: there is no
    `ContradictionDetectionMiddleware` until 6.5, so a `contradiction_flag` the
    coach sets is carried into `step_log` and read by nobody until then.

    The coach's answer goes into `messages` as an `AIMessage`. A `propose_diagram`
    payload from this turn rides on `additional_kwargs` under the key the UI
    already reads — `sipoc_diagram` for a SIPOC, `visualisation` for the 5W2H
    mind map (`gateway/routes.py` reads exactly those).
    """
    # §44 / G-92 — THE BUDGET'S CLOCK STARTS HERE, at node entry, because the
    # engine's `TimeoutPolicy` wall starts here too. Anchored at
    # `agent.ainvoke` instead, the ~5 s this node spends building the agent and
    # dispatching the planner's read came off the WALL but not off the budget,
    # so the soft deadline fell after the wall and the engine cancelled the
    # node first (trace 01a0d215…: soft at 54.7 s, wall at 54.2 s).
    _node_entered = asyncio.get_running_loop().time()
    turn_count = state.get("turn_count") or 0
    plan = state.get("coaching_plan")

    # ── guard 1 of 2 — §26 / S-F09 B1, the graceful off-ramp ──────────
    # `remaining_steps` is a `RemainingSteps` managed value LangGraph fills in
    # on its own; declaring it on `PhaseState` is what activates it (§10.1).
    # Low means the GRAPH is running out of room, so the coach is built with no
    # retrieval tools and answers from what is in hand — B1's *"rather than
    # beginning a hop chain it cannot finish"*. It coaches; it does not cap.
    #
    # `or 0` and not a `.get` default: an ABSENT field must fail this test, not
    # pass it. `state.get("remaining_steps", 10)` was §0.16's bug in the other
    # direction — a default that made the guard unfireable — and a default here
    # would make it fire on every turn instead.
    remaining = state.get("remaining_steps") or 0
    off_ramp = 0 < remaining <= REMAINING_STEPS_FLOOR
    hop_budget = 0 if off_ramp else COACH_HOP_BUDGET
    if off_ramp:
        logger.warning(
            "%s.executor: %d graph step(s) left (floor %d) — coaching with no "
            "retrieval tools this turn (§26, S-F09 B1). MONITORING SIGNAL: the "
            "graph is close to its %d-step backstop.",
            phase, remaining, REMAINING_STEPS_FLOOR, COACH_RECURSION_BACKSTOP,
        )

    # ── guard 2 of 2 — §3.7's five hops, counted in the tools ─────────
    # A different unit from the one above and not substitutable for it: this
    # counts `rag_lookup_*` CALLS, `remaining_steps` counts graph-node
    # transitions. The list is the sink `_budgeted_rag_tools` mutates, read
    # back below for `step_log`.
    hops_spent: list[int] = [0]

    # 6.46 — the skills middleware reports every delivery of the phase script
    # here; the node, which owns step_log, writes the turn's record below.
    script_log: list[dict[str, Any]] = []
    # G-96 — layer 2a's verdicts, a rejection with its reason, for step_log.
    coherence_log: list[dict[str, Any]] = []
    agent, grader_log = _build_executor(
        phase, state, config, hop_budget=hop_budget, hops_spent=hops_spent,
        script_log=script_log, coherence_log=coherence_log,
    )
    # ── the planner's named call, executed before the model runs ──────
    # §17, step 6.21, option C. `prior` is what the agent is invoked with;
    # `state["messages"]` is what the tail slice below measures against, so the
    # dispatched exchange is returned as new messages and checkpointed with the
    # turn — which is what stops the next turn re-reading the same file.
    dispatched = await _dispatch_routed_read(state)
    # 6.61 (item 4) — SECTION 6 IS ONE ENTRY PER TURN: the Belt's words and the
    # coach's reply text — no tool-call stubs, no "Returning structured
    # response" dumps. The stored conversation keeps its full shape (the
    # audit trail); only what the model is shown is cleaned. This turn's
    # dispatched read stays whole: it is this turn's evidence, not history.
    history = _conversation(list(state.get("messages") or []))
    prior = [*history, *dispatched]
    hit_cap = False
    timed_out = False
    # 6.61 — containment, founder 2026-09-25: every use of the code-written
    # fallback is a DEFECT (the coach did not finish its move) and is logged
    # as one; the target is zero.
    fell_back = False
    # What is LEFT of the node's budget, not a fresh one: time already spent
    # above is time the wall has already counted. Floored at zero, so a setup
    # that overran the budget times the agent out at once and still composes.
    remaining_budget = max(
        0.0,
        EXECUTOR_SOFT_BUDGET - (asyncio.get_running_loop().time() - _node_entered),
    )
    # A Change click is answered in code and the coach is not called
    # (`_change_reply`); every other move is the model's to write.
    written = _change_reply(plan)
    try:
        # §44 / G-84, G-92 — the node's OWN budget, so the ENGINE's wall is
        # never the thing that ends this turn. `asyncio.wait_for` cancels the
        # agent loop and raises HERE, inside the node, where the composition
        # below can still run. `EXECUTOR_SOFT_BUDGET` is read from the module
        # global at call time so a test can inject a small budget.
        result: dict[str, Any] = {"messages": [*prior, AIMessage(content=written.message)],
                  "structured_response": written} if written is not None else \
            await asyncio.wait_for(agent.ainvoke(
            {"messages": prior},
            # §16 — the infinite-loop backstop, NOT the hop cap. Passed
            # explicitly so it does not depend on what the caller happened to
            # set: measured, an agent invoked inside a node inherits the
            # parent's LIMIT with a FRESH counter, which is right when the
            # route sets 50 and silently wrong when a test or a script invokes
            # this node directly.
            config={"recursion_limit": COACH_RECURSION_BACKSTOP},
        ), timeout=remaining_budget)
    except asyncio.TimeoutError:
        # §4.8 — NEVER A HARD FAILURE TO THE BELT, and this is the path that
        # was missing. Before G-84 the engine's `TimeoutPolicy` fired instead,
        # cancelling the node from above and delivering a 500 carrying a stack
        # trace. The turn now completes: 200, a partial and honest answer, and
        # a `step_log` entry that says it was partial.
        timed_out = True
        logger.warning(
            "%s.executor: TIMED OUT at %.1fs (from node entry) of a %.1fs budget after %d "
            "hop(s) — composing a degraded answer (§4.8, G-84). The engine's "
            "%.0fs wall was NOT reached, which is the point: it stays a "
            "backstop rather than the ordinary failure path.",
            phase, asyncio.get_running_loop().time() - _node_entered,
            EXECUTOR_SOFT_BUDGET, hops_spent[0], 45.0,
        )
        # 6.61 (item 1) — never the backstop text as a coaching reply: the
        # move was decided in code, so code writes its reply (_TIMEOUT_MESSAGE is kept
        # for the log). The step_log status still records the degrade.
        fallback = _fallback_reply(phase, plan)
        fell_back = True
        result = {"messages": [*prior, AIMessage(content=fallback.message)],
                  "structured_response": fallback}
    except GraphRecursionError:
        # §3.7 — MUST be caught here and turned into a partial answer. A Belt
        # mid-session never sees a stack trace because the coach explored too
        # broadly. Found by step 6.2's live-run, which looped a real turn.
        #
        # **Belt-and-braces since 6.7, not the primary guard** (§26). The two
        # guards above off-ramp into a composed answer, so arriving here means
        # the coach burned 50 graph steps without stopping — a genuine runaway
        # loop, which is what §16 says the backstop is for.
        hit_cap = True
        logger.warning(
            "%s.executor: hit the %d-step BACKSTOP (§16) after %d hop(s) — "
            "returning a partial answer. This should not happen now that §3.7's "
            "hop budget and §26's off-ramp are live; it means a genuine runaway "
            "loop, not broad exploration.",
            phase, COACH_RECURSION_BACKSTOP, hops_spent[0],
        )
        # 6.61 (item 1) — never the backstop text as a coaching reply: the
        # move was decided in code, so code writes its reply (_CAP_MESSAGE is kept
        # for the log). The step_log status still records the degrade.
        fallback = _fallback_reply(phase, plan)
        fell_back = True
        result = {"messages": [*prior, AIMessage(content=fallback.message)],
                  "structured_response": fallback}

    reply: CoachingResponse | None = result.get("structured_response")
    produced = list(result.get("messages") or [])
    # The agent echoes the conversation it was given and appends its own turn.
    # `messages` reduces with `operator.add`, so returning more than the tail
    # would duplicate the exchange on every turn.
    new_messages = produced[len(history):]

    # 6.57 — what the model wrote in `progress`, kept before the executor
    # writes the computed step over it (below, after the capture merge).
    model_progress = reply.progress if reply is not None else None

    captured: dict[str, Any] = {}
    citations: list[dict] = list(state.get("citations") or [])
    if reply is not None:
        captured = _captured_fields(phase, reply)
        citations.extend(_anchored(reply.citations or [], state))
        new_messages = _with_coaching_text(new_messages, reply)

        # §50.1's four blocks are OPTIONAL as of §56 amendment v1.64, and an
        # empty one is a FINDING rather than a failure. Required `str` meant a
        # model omitting `progress` failed the whole turn's structured output
        # — a hard failure to the Belt, which §4.8 forbids.
        #
        # **Logged loudly BECAUSE it is no longer fatal.** Making the fields
        # optional without this would trade a loud failure for a silent one:
        # the UI would draw four blocks, one of them blank, and nothing would
        # have noticed. Degraded, not broken — and visible.
        gaps = presentational_gaps(reply)
        if gaps:
            logger.warning(
                "%s.executor: FINDING — §50.1 presentational field(s) came "
                "back empty: %s. The turn completes and the block renders "
                "empty (§56 amendment v1.64, §4.8: never a hard failure to "
                "the Belt). A recurring gap here is a PROMPT defect, not a "
                "schema one.",
                phase, ", ".join(gaps),
            )

    # R4 — `consumed_at` is written HERE, not inside the tool. A `@tool`
    # receives only its arguments and cannot reach `PhaseState`; the node
    # inspects the turn's tool calls afterwards. S-F57 B4.
    uploads, consumed = _mark_consumed(state, produced, citations)

    _attach_diagram(new_messages)

    # ── 6.33 — the accumulation, and the two ways it used to be lost ──
    #
    # `state["artifacts"]` is now the phase's whole capture history, seeded by
    # the input mapper from the case record rather than blanked (G-78, half
    # one). And an EMPTY capture no longer overwrites a real prior value:
    # `{**prior, **captured}` with a `None` in `captured` destroyed the value
    # the gate document reads, while the case-blob write discarded the same
    # entry — so the two records of one field disagreed, silently, in the
    # direction that loses data.
    prior_artifacts = dict(state.get("artifacts") or {})

    # ── 6.61 — NOTHING IS STORED BEFORE THE BELT CONFIRMS (§20 v1.75) ──
    #
    # Founder ruling 2026-09-25: *"A value is stored only after the Belt
    # confirms it, in the Belt's words; a tidied version may be proposed in the
    # read-back and is stored only if the Belt confirms it."* So what reaches
    # `artifacts` is decided by the PLAN, never by what the coach returned:
    #   store_and_advance  the plan's `store` — the read-back the Belt just
    #                      confirmed (`moves.pending_store`)
    #   read_back          nothing; the coach's `fields_captured` is the value
    #                      it read back, held as PENDING on the move record
    #   anything else      nothing; a capture the coach returned is reported
    #                      as not stored (`fields_not_stored`)
    # The guards below — empty, declared type, worked example — run on the
    # candidate either way, so a pending value is checked when it is proposed
    # and a stored one when it is stored.
    move = plan.move if plan else None
    pending = dict(plan.pending) if plan and plan.pending else None
    if move == moves.STORE_AND_ADVANCE and plan is not None:
        candidate = dict(plan.store)
    elif move == moves.READ_BACK and pending:
        candidate = {f: v for f, v in captured.items() if f in (pending.get("fields") or [])}
    else:
        candidate = {}
    not_stored = sorted(f for f in captured if not (move == moves.READ_BACK and f in candidate))
    if not_stored:
        logger.info(
            "%s.executor: %d capture(s) NOT stored — the move is %s, and only a "
            "confirmed read-back is stored (§20 v1.75): %s",
            phase, len(not_stored), move, ", ".join(not_stored),
        )
    kept, empty_captures = split_captures(candidate)

    # ── 6.48 — the declared type is enforced HERE, at the capture site ──
    #
    # **Not at the model and not at assembly**, and both were ruled out rather
    # than passed over. A per-phase response schema would make the model the
    # enforcer, which is a §56 amendment and still leaves the value unchecked
    # when the model ignores it. Coercing at assembly would INVENT the Belt's
    # data — a sentence about three people is not three `{name, role, function}`
    # entries, and anything turning one into the other is guessing which words
    # were the names.
    #
    # Ordered AFTER the empty split deliberately: a `""` for a `dict` field is
    # EMPTY, not malformed, and reporting it as the wrong type would send a
    # reader looking for a shape problem in a field the Belt never answered.
    kept, malformed = split_by_declared_type(phase, kept)

    # ── 6.46 — §22: a worked example is NEVER captured as the Belt's data ──
    #
    # The script now reaches the model every call, and with it every worked
    # example — each a plausible, well-formed value for the field it shows.
    # A capture that reproduces one (skills.example_match: containment either
    # way, or similarity >= 0.80 after normalising) is refused and reported,
    # exactly as a malformed one is: the field stays uncaptured, so the coach
    # asks again, and the turn does not fail for the Belt.
    example_refused = sorted(f for f, v in kept.items() if example_match(v, phase))
    if example_refused:
        kept = {f: v for f, v in kept.items() if f not in example_refused}
        logger.warning(
            "%s.executor: FINDING — %d capture(s) reproduced a WORKED EXAMPLE "
            "from the coaching script and were NOT stored: %s (§22).",
            phase, len(example_refused), ", ".join(example_refused),
        )
    if malformed:
        logger.warning(
            "%s.executor: FINDING — %d capture(s) did not carry the type their "
            "schema declares and were NOT stored: %s. The field stays "
            "uncaptured, so the coach asks again — §4.8, the turn does not fail "
            "for the Belt. Storing the prose would put a value in `artifacts` "
            "that no gate document can be assembled from (step 6.48).",
            phase, len(malformed),
            ", ".join(f"{f} (needs {t})" for f, t in sorted(malformed.items())),
        )

    if empty_captures:
        logger.warning(
            "%s.executor: FINDING — %d capture(s) arrived with no value and "
            "did NOT reach `artifacts`: %s. The coach named the field, so it "
            "counts as captured in its own reply and does not exist anywhere "
            "the gate can read — which is the disagreement step 6.33 closes. "
            "Reported rather than dropped; the prior value (if any) is kept.",
            phase, len(empty_captures), ", ".join(empty_captures),
        )

    # 6.61 — a read-back's value is PENDING: it goes on the move record with
    # what a confirmation will store, and nothing reaches `artifacts` now.
    if move == moves.READ_BACK and pending is not None:
        pending = {**pending, "proposed": dict(kept),
                   "store": moves.pending_store(phase, pending, kept)}
        kept = {}
    artifacts = {**prior_artifacts, **kept}

    # 6.61 (R5) — THE STATUSES, STORED AT TURN END. The plan carries the
    # after-change map; a read-back's pending entry gains here what the Belt's
    # yes will store (it needs this turn's read-back to know).
    field_status = {f: dict(v) for f, v in ((plan.field_status if plan else None)
                                            or state.get("field_status") or {}).items()}
    if move == moves.READ_BACK and pending is not None and plan and plan.focus_field:
        field_status[plan.focus_field] = {**field_status.get(plan.focus_field, {}),
                                          "status": moves.ANSWERED, "pending": pending}

    # The field change log — §56 amendment, ratified 2026-09-21. Built from
    # the SAME `kept` the merge above uses, so the log and the accumulator
    # cannot disagree about what changed.
    turn_ordinal = _turn_ordinal(state)
    log_entries = _field_log_entries(
        phase, turn_ordinal, kept, prior_artifacts, reply,
        datetime.now(timezone.utc).isoformat(),
    )

    # ── 6.20 — the write paths. Three things §39.x.7 specifies were READ by
    #    the gate document and written by NOTHING; each was a one-directional
    #    break where the reader existed, was correct, and always found nothing.
    results = _computation_results(produced, phase, turn_count)
    if results:
        artifacts["computation_results"] = [
            *(artifacts.get("computation_results") or []), *results,
        ]
    next_field = _advance_field_index(phase, artifacts)

    # ── 6.57 — the Belt's step is the COMPUTED one, in the reply the turn keeps
    # Delivery alone did not hold: on 0E5 at 15:05 (trace 01a0d3f3…) the step
    # sat at the top of the model's input and the model still wrote "13 of
    # 13" — its own earlier replies put "of 13" in that input 55 times. So the
    # reply's `progress` is WRITTEN, on every turn, from the same function the
    # injection block delivered, and the structured-response message the NEXT
    # turn reads is re-rendered with it. What the model wrote is kept in
    # step_log below.
    #
    # **From the artifacts AFTER this turn's capture**, not the turn-start
    # ones the block was composed from: the reply is read after the turn, and
    # a Belt who just completed position 1 is on step 2. Computed before the
    # capture, the label lagged one step on every capture turn (dry run 2,
    # IMPR-2026-134, turn 2: the model wrote "Step 2", the executor "Step 1").
    define_step = define_progress(artifacts) if phase == "define" else None
    delivered = (define_progress(prior_artifacts)["label"]
                 if define_step is not None else None)
    if define_step is not None and reply is not None:
        new_messages = _with_progress(new_messages, reply, define_step["label"])

    # ── 10.0 — the four blocks and the grader's warning ride on the reply ──
    # The route never holds the `CoachingResponse`, only the graph's
    # messages, so this is the one place the blocks can be put where it reads.
    # After 6.57's write, so `progress` is the computed step. The warning is
    # the grader's own B5 text whenever its verdict this turn FAILED — the
    # dict its `after_agent` returns reaches no reader (G-76, G-103).
    failed = any(e.get("status") == "failed" for e in grader_log)
    _attach_blocks(new_messages, reply, MAX_ITERATIONS_WARNING if failed else None)

    # ── 6.61 — the move record and the quality feedback ride on the reply ──
    # The next turn's planner reads the record (status, answer, PENDING); the
    # next turn's coach reads the feedback as section 5 of its input — never as
    # a message from the Belt. Attached even when the turn degraded, so a
    # confirmed value the plan stored is not taught again.
    record = _move_record(plan, pending if move in (moves.READ_BACK, moves.RESPOND) else None, kept)
    if fell_back:
        logger.error(
            "%s.executor: DEFECT — the coach did not finish its %s move (%s); the "
            "reply was written by code (containment, not a fix).",
            phase, move, "timeout" if timed_out else "runaway loop backstop")
        if record is not None:
            record["fallback"] = True
    feedback = _quality_feedback(grader_log, coherence_log)
    _attach_move(new_messages, record, feedback)

    # **The count that used to disagree with the write, reconciled.** This
    # line logged `len(captured)` — the KEYS the coach named — while the write
    # filtered on VALUES, so "captured 1 field(s)" and "nothing reached the
    # gate document" were both true of the same turn (6.33's trap). It now
    # reports all three numbers, and they add up.
    logger.info(
        "%s.executor: focus=%s | turn %d | captured %d -> %d field(s) into "
        "artifacts (%d not stored, %d changed), %d new message(s), %d/%d "
        "hop(s), %s remaining step(s), contradiction=%s",
        phase, plan.focus_field if plan else "(none)", turn_ordinal,
        len(captured), len(kept), len(empty_captures) + len(malformed),
        len(log_entries),
        len(new_messages), hops_spent[0], hop_budget,
        remaining or "no", bool(reply and reply.contradiction_flag),
    )
    return {
        "messages": new_messages,
        # `draft` is what THIS turn stored, `artifacts` the accumulation
        # (S-F04's Output). Neither field carries a reducer, so the merge
        # happens here or not at all. **6.61: `kept`, never `captured`** —
        # the route writes `draft` into the case record, so a value the coach
        # returned but the Belt has not confirmed must not be in it (§20 v1.75).
        "draft": dict(kept),
        "artifacts": artifacts,
        # Returned as THIS TURN's entries only. The channel's reducer folds
        # them onto what the input mapper seeded — which is the whole reason
        # this field carries one: a node cannot destroy the history it does
        # not return.
        "field_log": log_entries,
        "field_status": field_status,
        "citations": citations,
        "uploads": uploads,
        "turn_count": turn_count + 1,
        # Only Define has an ordered list to walk, so the other four keep the
        # value they had rather than gaining a derived one (see the helper).
        **({"field_index": next_field} if next_field is not None else {}),
        "step_log": [_step(
            phase, turn_count, "executor",
            status=_executor_status(hit_cap, off_ramp, timed_out),
            fallback_used=fell_back,
            impl="create_agent",
            focus_field=plan.focus_field if plan else None,
            # 6.61 — the move code chose, the field's status, and what this
            # turn stored or holds as pending.
            move=plan.move if plan else None,
            field_status=plan.status if plan else None,
            stored_field=plan.stored_field if plan else None,
            fields_stored=sorted(kept),
            pending=((record or {}).get("pending") or {}).get("field"),
            pending_value=((record or {}).get("pending") or {}).get("store"),
            fields_not_stored=not_stored,
            fields_captured=sorted(captured),
            # 6.33 — what the coach named and what the record now holds, in
            # the audit trail rather than only in a log line. `fields_empty`
            # is the clause "reported rather than silently dropped" made
            # queryable: `len(fields_captured)` and `len(fields_empty)` are
            # what reconcile a turn's log against its write.
            fields_empty=empty_captures,
            # 6.48 — named with the type each needed, so the audit trail can
            # answer "why is this field still blank on turn nine" without a
            # re-run. `fields_captured` minus `fields_empty` minus this is what
            # actually reached `artifacts`.
            fields_malformed=dict(sorted(malformed.items())),
            # 6.46 — §22's refusals, by field.
            fields_example_refused=example_refused,
            fields_changed=sorted(e["field"] for e in log_entries),
            # Re-derived from the SAME function that built the bound list,
            # so the audit trail cannot disagree with what the coach actually
            # had. The throwaway counter is never spent — nothing invokes
            # these copies; only `len()` is read.
            tools_bound=len(_executor_tools(phase, hop_budget, None)),
            # §3.7's cap and §26's off-ramp, both readable in LangSmith.
            # "Hitting the cap is a monitoring signal" — a signal nobody can
            # read is not one, and WATCH 26 went four steps undiagnosed partly
            # because the hop count was never written down.
            hops_spent=hops_spent[0],
            hop_budget=hop_budget,
            # §17 option C — what the NODE called, as against what the model
            # chose. Empty on every turn with no unread routed upload, which
            # is most of them.
            dispatched=[
                c["name"] for m in dispatched
                for c in (getattr(m, "tool_calls", None) or [])
            ],
            remaining_steps=remaining or None,
            # Carried for the audit trail; §19.6's middleware reads it at 6.5.
            contradiction_flag=(reply.contradiction_flag if reply else None),
        ), *(
            # §19.8 / S-C14 B6 — each grading written to `step_log`, which the
            # grader's `on_evaluation` callback was always meant to reach.
            # `grader_log` was collected here and read by nothing until 6.52
            # B2, so a verdict existed only for the length of the turn
            # (capability row 13). One grading per reply until 6.53; the
            # iteration goes into the key should 6.53 ever make more.
            _step(phase, turn_count,
                  "coaching_grader" if int(e.get("iteration") or 1) == 1
                  else f"coaching_grader:{e['iteration']}", **e)
            for e in grader_log
        ), *(
            # G-96 — layer 2a's verdict, whichever way it went. A rejection
            # degrades the turn and stands the grader down (S-C13 B3); until
            # this entry, the reason reached a log line and nothing else, so a
            # turn with no grade could not say why it had none (row 13).
            _step(phase, turn_count, "coherence", **e) for e in coherence_log
        ),
            # 6.46 — did this turn's model calls carry the phase script? One
            # entry per turn, `delivered` false when no call did: a turn
            # coached without its method is now distinguishable in the record.
            # 6.61 — the coach's input as it was sent: the six sections, in
            # order, read off the system message the model received (the skills
            # middleware sees it last), and the move section's own text.
            _step(phase, turn_count, "coach_input",
                  sections=list((script_log[0] if script_log else {}).get("sections") or []),
                  move=plan.move if plan else None,
                  field=plan.focus_field if plan else None),
            _step(phase, turn_count, "coaching_script",
                  **{k: v for k, v in (script_log[0] if script_log else script_record(phase)).items()
                     if k != "sections"},
                  delivered=bool(script_log), model_calls=len(script_log)),
            # 6.57 — the step the reply carries (after the capture), the one
            # the coach was DELIVERED (turn start), and what the model wrote
            # in `progress`. A model that counted for itself is on the record,
            # not only on the screen.
            *([_step(phase, turn_count, "define_position", **define_step,
                     delivered_label=delivered,
                     reply_progress=model_progress,
                     reply_matches=model_progress == define_step["label"],
                     progress_written=reply.progress if reply else None)]
              if define_step is not None else []),
        ],
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
    entry = entry_mode(config)

    # **Reads the per-run intent, not the plan** — changed at step 6.1.
    # It used to test `coaching_plan["next_action"] != "gate"`, which worked
    # only because 4.4's stub put the ROUTING verb in that key. S-C04 makes
    # `next_action` the coaching move — "ask, challenge, show an example, run a
    # computation" — so a gate submission cannot be spelled there any more, and
    # the planner no longer produces a plan on this path at all. `entry_mode`
    # is the same source the planner routes from, which is what keeps the two
    # nodes from disagreeing about what kind of turn this is.
    if entry != "gate":
        logger.info("%s.validation_stack: pass-through (coaching turn)", phase)
        return Command(
            goto="gate_review",
            update={"step_log": [_step(
                phase, turn_count, "validation_stack",
                status="passthrough", entry=entry,
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
