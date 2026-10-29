"""The five node bodies, parameterised by phase.

WHY A SHARED MODULE RATHER THAN FIVE COPIES
    The five nodes are **identical across all five phases**. They differ in
    the phase name and nothing else. Written out five times that is five
    copies of the planner's routing table, of the validation stack, and of
    the deterministic `step_log` key.

    `phases/mappers_common.py` exists for the same reason. These bodies carry
    live rules — the `step_log` key format, "do not validate a coaching turn",
    "nothing is stored before the Belt confirms" — and a rule enforced in four
    of five places is not enforced.

WHAT EACH PHASE'S `nodes.py` STILL OWNS
    Every phase keeps five real `async def`s at module level, because the node
    contract requires module-level async functions and `test_phase_subgraphs.py`
    asserts `fn.__module__` is that phase's module. They are two lines each and
    they delegate here. **That is deliberate rather than lazy**: generating the
    functions in a factory and assigning them would make `__module__` point at
    this file, and satisfying that assertion would then mean rewriting the
    function's `__module__` to something it is not.

`ARTIFACTS` AND `DRAFT`
    `artifacts` is the phase's accumulation of confirmed values, under their v2
    names; the executor writes it. `draft` is seeded from the phase record when
    the subgraph is entered (`core/graph.py`) and, after a coaching turn, holds
    what that turn stored — the route writes it into the case record. On a gate
    submission it is what layer 2b checks (`gate_registry.check_gate`).
"""
from __future__ import annotations

import asyncio
import contextvars
import hashlib
import json
import logging
import re
import time

import openai
from typing import Any, Literal, Optional, cast

from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ModelFallbackMiddleware,
    ModelRetryMiddleware,
    SummarizationMiddleware,
    ToolRetryMiddleware,
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from backend.core.tracing import child_span
from langgraph.errors import GraphRecursionError
from langgraph.graph import END
from langgraph.types import Command, interrupt

from backend.core import content_safety, guard, guard_messages, pii
from backend.middleware import fallback as model_fallback
from backend.middleware import turn_tools
from backend.core.config import TURN_CLOSE_RESERVE_S, TURN_LIMIT_S
from backend.core.request_context import mark_answered, turn_step   # R-F, #63
from backend.core.conversation import CARD_KEY, COMPLETION_KEY, ELEMENT_KEY, STRIP_KEY  # ADR-0093
from backend.core.conversation import LINK_CHECK_KEY, TEACHING_CARD_KEY  # R-C (ADR-0114), R-H
from backend.core.llm import get_fallback_llm, get_llm
from backend.knowledge import fusion
from backend.core.prompts import (
    FALLBACK_RESEND,
    PHASE_COACH_PROMPT,
    PLANNER_JUDGMENT_PROMPT,
    PLANNER_JUDGMENT_READING_BACK,
    READ_BACK_CARRIED,
    READ_BACK_METRIC,
    STORE_NOTE_NOT_STORED,
    STORE_NOTE_STORED,
    cut_at,
)
from backend.core.substate import (
    FIELDS_CAPTURED_NORMALIZED,
    CoachingPlan,
    CoachingResponse,
    PhaseState,
    SufficiencyJudgment,
    coaching_response_model,
    field_log_key,
    presentational_gaps,
    split_captures,
)
from pydantic import BaseModel

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
from backend.middleware.contradiction import ContradictionDetectionMiddleware
from backend.middleware import grader as grader_mode
from backend.middleware.grader import DMAICGraderMiddleware, GRADER_WARNING
from backend.middleware.skills import (
    DMAICSkillsMiddleware,
    example_match,
    acceptance_criteria,
    field_needs,
    script_record,
)
from backend.phases import moves
from backend.middleware.state_injection import BeforeModelStateInjection
from backend.phases.gate_registry import check_gate, gate_escalates, GATE_SPECS, captured_count, review_rows, split_by_declared_type
from backend.validation import kept as kept_verdicts
from backend.validation.rubric import grade_define
from backend.phases.mappers_common import PHASE_ORDER
from backend.core.clock import utc_now

logger = logging.getLogger(__name__)

#: Exactly these five, in this order, for every phase. A sixth is an architecture
#: decision (an ADR), not an edit. `policy_advisory` and `revise` are BANNED names.
NODE_NAMES: tuple[str, ...] = (
    "planner",
    "executor",
    "validation_stack",
    "gate_review",
    "gate_apply",
)



def step_key(phase: str, turn_count: int, step_name: str) -> str:
    """The deterministic `step_log` identity of one step of one turn.

    ``f"{phase}:{turn_count}:{step_name}"``, never a raw timestamp as identity.
    An abandoned-then-retried turn re-executes the same logical step; a
    timestamp key records it as two events, a deterministic key records it as
    one. **Every `step_log` write site goes through here**, which makes the
    rule checkable rather than a habit, for all five phases.
    """
    return f"{phase}:{turn_count}:{step_name}"


def _step(phase: str, turn_count: int, step_name: str, *, rejections: int = 0,
          **fields: Any) -> dict[str, Any]:
    """One `step_log` entry, keyed deterministically. Dicts only, never tuples.

    ADR-0107: the pass after a gate rejection repeats steps of the same run under the same
    turn, so it carries `:r1`, `:r2` … in its key (`rejections` = `len(rejection_feedback)`, `_rejections`)."""
    return {
        "key": step_key(phase, turn_count, step_name) + (f":r{rejections}" if rejections else ""),
        "node": step_name,
        "phase": phase,
        **fields,
    }


def _rejections(state: Any) -> int:
    """How many gate rejections this run has had — the pass number in a `step_log` key (ADR-0107)."""
    return len((state or {}).get("rejection_feedback") or [])


def entry_mode(config: Optional[RunnableConfig]) -> str:
    """``"ask"`` (a coaching turn) or ``"gate"`` (a gate submission).

    Per-run intent, so it rides on `config` rather than on state — the same
    channel `thread_id` uses. **It stands in for the Belt saying "I am ready
    for the gate" in conversation** (the routing predicate, G-01); it is a
    route-level signal because the route distinguishes `/ask` from `/gate`.
    """
    return ((config or {}).get("configurable") or {}).get("entry", "ask")


# ── planner ───────────────────────────────────────────────────────────────



def _anchored(citations: list[dict], state: PhaseState) -> list[dict]:
    """Citations with `blob_path` and `content_digest` attached.

    **Enriched in CODE, never by the model.** The coach is shown a `role` in
    the manifest and cites it; the anchor is looked up here, so a 64-character
    digest never has to survive a round trip through a language model that was
    never shown it.

    **Matched on ROLE, not on filename.** A document's identity is never
    inferred from what it is called, and matching on filename would do exactly
    that.

    **Only citations of uploads are anchored.** A citation the coach made
    against an upload it saw in the manifest is anchored, because
    `PhaseState.uploads` carries both fields. One sourced from
    `rag_lookup_evidence` passes through unanchored rather than being given a
    guessed anchor.
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

    **Placed at the node because a tool cannot write state.** An upload counts
    as consumed when `load_evidence_series` was called on its `blob_path`, or
    when a citation anchored to it.

    **`consumed_at = None` at a gate on an upload bound to an open ask means
    the Belt supplied evidence and the coaching proceeded without it.** That
    condition is undetectable without this write.
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

    stamp = utc_now().isoformat()
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
    """An upload bound to an open ask that nothing has read yet — or, when no
    ask is open, the first unread upload.

    **This is what turns "the coach will use the file" from a hope into a
    fact.** Retrieval is discretionary by design, so no prompt can carry the
    guarantee; the planner owns the routing decision, and the planner is code.

    Matched on `role`, never on filename — a document's identity is never
    inferred from what it happens to be called.

    **`asks` is explicit so the planner and the executor reach the same
    answer.** The executor DISPATCHES what this returns, so the two must agree
    or the turn's prose and its action disagree. They read different states:
    the planner decides before its own `update["asks"]` is applied, the
    executor after. `ensure_ask` opening an ask for a role no upload carries
    would narrow `open_roles` between the two reads, and the executor would
    dispatch nothing while the plan said to. The planner passes the asks it
    just computed, so both sides decide on the same input by construction.
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


def _unread_upload(state: PhaseState, asks: Optional[list[dict]] = None) -> dict | None:
    """The upload this turn reads — W5 (DEF-108): every new upload makes the next turn an upload
    turn. One bound to an open ask comes first; otherwise the newest unread upload, read against
    the current element."""
    bound = _unconsumed_for_open_ask(state, asks)
    if bound is not None:
        return bound
    unread = [u for u in state.get("uploads") or [] if not u.get("consumed_at")]
    return unread[-1] if unread else None


async def planner(
    phase: str,
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> Command[Literal["executor", "validation_stack"]]:
    """Produce the `CoachingPlan` and make the phase's ONE routing decision.

    The planner fires many times per phase, not once. After each executor step
    control returns here to decide whether to keep coaching the current field,
    advance to the next, or trigger the gate.

    **THE MOVE IS DECIDED IN CODE.** `_plan_turn` derives the focus field, its
    status and THIS TURN'S MOVE with `phases/moves.decide`; the `planner`-role
    model makes ONE judgment — is the Belt's answer sufficient, with a reason —
    and only when the Belt has answered. A move the model wrote as free text
    would reach no channel the coach reads (G-49).

    **THE MODEL IS CALLED ONLY ON THE EXECUTOR-BOUND PATH**, and on it only when
    a judgment is needed. On the way to `validation_stack` the previous plan
    stands.

    **THE ROUTING PREDICATE IS A PLACEHOLDER** (G-01; DP1 is founder-owned):

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

        # ── Ask-binding ───────────────────────────────────────────────
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

        # **Routing on an unread upload.** The asks are written so the executor
        # decides on the same ones, and the executor dispatches the read itself
        # (`_dispatch_routed_read`); the plan carries no instruction for it (G-49).
        pending_upload = _unread_upload(state, asks)
        if pending_upload is not None:
            update["asks"] = asks
            logger.info(
                "%s.planner: routing to an UNREAD upload — role=%r path=%s",
                phase, pending_upload.get("role"), pending_upload.get("blob_path"),
            )

        events = moves.park_events(
            dict(state.get("field_status") or {}), dict(plan.field_status or {}),
            person=((config or {}).get("configurable") or {}).get("current_user"),
            at=utc_now().isoformat(timespec="seconds"))
        if events:
            logger.info("%s.planner: %s", phase, "; ".join(f"{e['event']} {e['field']}" for e in events))
        entry_fields = {
            "field_events": events,
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
        phase, turn_count, "planner", rejections=_rejections(state),
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
    """The per-phase retrieval strategy. **Analyse is the one phase that plans
    multi-hop** — root-cause validation is layered. No model plans the turn, so
    the default is the strategy: `retrieval_strategy` is set here and
    `retrieval_hops` stays empty."""
    return "multi_hop" if phase == "analyse" else "single_hop"


def _judgment_prompt(phase: str, state: PhaseState, field: str, previous: str,
                     latest: str, reading_back: bool) -> str:
    """The planner model's input for its one judgment — the field, what the
    phase script says it needs, this project's framing, and the Belt's words."""
    context = " ".join(str(state.get("phase_context") or "").split()) or \
        "(no phase context was composed)"
    prompt = PLANNER_JUDGMENT_PROMPT.format(
        phase=phase, field=field,
        needs=field_needs(phase, field) or f"(the phase script gives no block for {field})",
        context=cut_at(context, 1500),                # ADR-0111 D3: the cut says so
        reading_back=PLANNER_JUDGMENT_READING_BACK if reading_back else "",
        previous=previous or "(none — the latest message is the first answer)",
        latest=latest or "(empty)",
    )
    # ADR-0077 — the inputs of this element's calculation the case does not hold yet.
    from backend.core.prompts import PLANNER_CALCULATION_INPUTS
    from backend.phases import calculations
    missing = calculations.missing_inputs(phase, field, dict(state.get("artifacts") or {}))
    if missing:
        prompt += PLANNER_CALCULATION_INPUTS.format(
            inputs="\n".join(f"  {name}: {what}" for name, what in missing.items()))
    return prompt


async def _judge(phase: str, state: PhaseState, field: str, previous: str,
                 latest: str, reading_back: str) -> SufficiencyJudgment:
    """THE PLANNER MODEL'S ONE JUDGMENT — a plain invocation, never an agent.

    What code can decide (`_judged_in_code`) is decided first, with no model
    call. **`planner` role, temperature 0.1** — the role default, not an
    override. **Structured output, never JSON parsed out of raw text**: a plain
    model call takes the builder-style form (`with_structured_output`). It
    dispatches to no tools.
    """
    in_code = _judged_in_code(phase, state, field, previous, latest)
    if in_code is not None:
        return in_code
    judge = get_llm("planner").with_structured_output(SufficiencyJudgment)
    judged_at, answered = time.monotonic(), False
    try:
        verdict = await judge.ainvoke(_judgment_prompt(
            phase, state, field, previous, latest, reading_back == "yes"))
        answered = True
    finally:
        # #63: each judgment call timed for the turn's log — a timed-out attempt too (the node retries it).
        turn_step("planner judgment" if answered else "planner judgment (failed)", time.monotonic() - judged_at)
    if verdict is None:
        # G-235: a model that answers without the structured verdict returns None here; validating it raised,
        # and the whole turn became the degraded reply. Decided in code instead: not an answer — the coach
        # responds and asks again, and nothing is stored.
        logger.warning("%s.planner: the judgment of `%s` came back empty — taken as not an answer, in code "
                       "(G-235)", phase, field)
        return SufficiencyJudgment(verdict="not_an_answer", reason=(
            "decided in code (G-235): the judgment came back empty; the coach responds and asks again, "
            "and nothing is stored"))
    return _number_required(phase, field, previous, latest,
                            _checked_criterion(phase, field, SufficiencyJudgment.model_validate(verdict)))


def _judgment_version(phase: str) -> str:
    """DEF-224: what a kept planner verdict was judged against — the phase script (its hash, as logged per turn)
    and the judgment's prompt. Either changing re-judges every answer."""
    from backend.core.prompts import PLANNER_CALCULATION_INPUTS
    from backend.middleware.skills import script_record
    return kept_verdicts.fingerprint(script_record(phase)["sha256"], PLANNER_JUDGMENT_PROMPT,
                                     PLANNER_JUDGMENT_READING_BACK, PLANNER_CALCULATION_INPUTS)


def _number_required(phase: str, field: str, previous: str, latest: str,
                     j: SufficiencyJudgment) -> SufficiencyJudgment:
    """ADR-0071 (DEF-076): a baseline or a target with no number is never sufficient — whatever
    the model judged, an answer the one parser reads no figure from is asked again, in code."""
    from backend.phases.define import criteria as define_criteria, parse
    if phase != "define" or field not in parse.METRIC_FIELDS or j.verdict != "sufficient":
        return j
    words = chr(10).join(x for x in (previous, latest) if x)
    if parse.metric_value(words, target=field == "target_value")["value"] is not None:
        return j
    crit = define_criteria.QUANTIFIED if field == "baseline_estimate" else define_criteria.NUMBER_AND_UNIT
    return _checked_criterion(phase, field, SufficiencyJudgment(
        verdict="insufficient", failed_criterion=crit, reason=(
            "decided in code (ADR-0071): the answer holds no number — the "
            + ("baseline" if field == "baseline_estimate" else "target")
            + " is stored as a number with its unit; ask for the figure again")))


def _judged_in_code(phase: str, state: PhaseState, field: str, previous: str,
                    latest: str) -> Optional[SufficiencyJudgment]:
    """G-120 (DEF-032): a target written as a number or a limit ("under 5%", "höchstens 5 %")
    is parsed in code into number, unit and direction BEFORE any model judgment. In the
    baseline's unit and different from the baseline, it meets `number-and-unit` — sufficient,
    no model call — unless it lies on the wrong side of the baseline, which fails `direction`
    (G-245). ADR-0071 (DEF-076): in ANOTHER unit than the baseline's, it is insufficient,
    decided here, and the reason names both units so the coach asks for it again in the
    baseline's. Anything else goes to the model. The one parser reads both values
    (`parse.metric_value` / `as_metric`)."""
    if phase != "define" or field != "target_value":
        return None
    from backend.phases.define import criteria as define_criteria, parse
    artifacts = dict(state.get("artifacts") or {})
    unit = parse.primary_unit(artifacts)
    baseline = (parse.as_metric(artifacts["baseline_estimate"], unit=unit)
                if artifacts.get("baseline_estimate") else None)                    # G-132
    base_unit = unit or (baseline or {}).get("unit", "")
    target = parse.metric_value(latest, target=True)
    if target["value"] is None:
        target = parse.metric_value(previous, target=True)
    if target["value"] is None or not target["unit"]:
        return None
    if base_unit and target["unit"] != base_unit:
        logger.info("%s.planner: target in %s, the baseline in %s — asked again (ADR-0071)",
                    phase, target["unit"], base_unit)
        return _checked_criterion(phase, field, SufficiencyJudgment(
            verdict="insufficient", failed_criterion=define_criteria.NUMBER_AND_UNIT, reason=(
                f"decided in code (ADR-0071): the target is in {target['unit']} but the baseline is "
                f"in {base_unit} — ask for the target in {base_unit}, naming both units")))
    if baseline and baseline["value"] is not None and baseline["value"] == target["value"]:
        return None
    side = parse.wrong_side((baseline or {}).get("value"), target, artifacts.get("goal_statement"))
    if side:
        # G-245: the element's `direction` criterion, decided in code by the gate's own check.
        return _checked_criterion(phase, field, SufficiencyJudgment(
            verdict="insufficient", failed_criterion=define_criteria.DIRECTION,
            reason=f"decided in code (G-245): {side}"))
    logger.info("%s.planner: target judged in code (G-120): %s %s%s, the baseline's unit",
                phase, target["direction"], target["value"], target["unit"])
    return SufficiencyJudgment(verdict="sufficient", reason=(
        f"parsed in code: {parse.metric_text(target)} — a number in the baseline's unit "
        f"({base_unit or target['unit']}), different from the baseline"))


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
    prior_status = dict(state.get("field_status") or {})
    judged: dict[str, dict[str, Any]] = {}

    async def judge(field: str, previous: str, latest: str, reading_back: str) -> SufficiencyJudgment:
        # DEF-224 (G-225): what code decides runs first — it reads other elements'
        # values, not only this answer; then a verdict kept for the same answer is reused with no model call.
        if _judged_in_code(phase, state, field, previous, latest) is not None:
            return await _judge(phase, state, field, previous, latest, reading_back)    # decided there, in code
        fp = kept_verdicts.fingerprint(_judgment_version(phase), field, reading_back,
                                       kept_verdicts.answer(previous, latest))
        held = (prior_status.get(field) or {}).get("judged") or {}
        if held.get("fp") == fp and held.get("verdict"):
            logger.info("%s.planner: `%s` answered as before — its kept verdict reused, no model call (DEF-224)",
                        phase, field)
            return SufficiencyJudgment.model_validate(held["verdict"])
        j = await _judge(phase, state, field, previous, latest, reading_back)
        if not (j.reason or "").startswith("decided in code (G-235)"):     # an empty reply is not a verdict
            judged[field] = {"fp": fp, "verdict": j.model_dump()}
        return j

    # R4 — a Confirm or Change click arrives on the request, not in the text;
    # the route puts it on `config` beside the entry mode.
    action = ((config or {}).get("configurable") or {}).get("belt_action")
    element = ((config or {}).get("configurable") or {}).get("belt_element")     # W9 (DEF-079)
    d = await moves.decide(phase, dict(state.get("artifacts") or {}),
                           dict(state.get("field_status") or {}),
                           moves.belt_message(messages), judge, action=action, element=element,
                           # ADR-0085 (G-169) — a file that covers the element is read back on its upload turn.
                           upload=_unread_upload(state))
    # DEF-224: the kept verdicts ride in each element's entry, which `decide` rebuilds — carried forward, and
    # this turn's model verdict kept beside the element it judged.
    field_status = kept_verdicts.carry(prior_status, dict(d["field_status"] or {}))
    for field, verdict in judged.items():
        if field in field_status:
            field_status[field]["judged"] = verdict
    return CoachingPlan(
        focus_field=d["field"], status=d["status"], move=d["move"],
        judgment=d["judgment"], answer=d["answer"], messages=d["messages"],
        pending=d["pending"], store=d["store"], stored_field=d["stored_field"], confirmed=d["confirmed"],
        statuses=d["statuses"], field_status=field_status, reason=d["reason"],
        retrieval_strategy=_retrieval_strategy(phase),
    )


# ── executor ──────────────────────────────────────────────────────────────

#: A backstop against a genuine infinite loop, NOT the hop cap. Equal to
#: `core.graph.RECURSION_LIMIT` and kept as its own name because this module
#: cannot import that one: `core.graph` imports the phase subgraphs, which
#: import this file. `test_the_coach_backstop_matches_the_graph_backstop`
#: imports both and asserts they agree, so the two cannot drift silently.
#:
#: **Not derived from the hop cap.** A hop-based limit (`2 * max_hops + 1`) is
#: consumed by the hops themselves and raises BEFORE the model can compose, so
#: a well-behaved turn at the cap would only ever end in the backstop.
COACH_RECURSION_BACKSTOP = 50

#: What one hop COSTS, measured rather than assumed — the number that decides
#: the cap below. The provenance is kept because a constant justified by a
#: measurement nobody can find is a constant nobody can revise.
#:
#: **Multi-query fusion makes a hop far more than one search**: one MODEL
#: CALL to generate variants, then six searches, then RRF. Measured at
#: **~9.5s** on G-63's trace, consistent with run `ca6ba417`, where three
#: hops plus the coach's own calls reached 52.2s.
MEASURED_HOP_SECONDS = 9.5

#: Reserved out of the node budget for everything that is NOT a hop: the
#: coach's own model calls, and composing the answer. What is left over after
#: the cap's hops must still fit here or the turn degrades instead of capping.
HOP_BUDGET_COMPOSE_RESERVE = 10.0

#: `rag_lookup_*` calls per Belt turn (ADR-0032). **This is the hop cap**, and
#: it is enforced by `_budgeted_rag_tools` rather than by any step counter:
#: hops and steps are different units (see `REMAINING_STEPS_FLOOR`). Past the
#: budget the retrieval tools stay bound and stay callable, and answer with
#: `_HOP_BUDGET_SPENT` instead of searching — so the coach reads a plain result
#: and composes, exactly as it does for a search that found nothing.
#:
#: **Three, so the cap is REACHABLE (G-83).** At `MEASURED_HOP_SECONDS` one more
#: hop would not fit inside `EXECUTOR_RUN_TIMEOUT` with
#: `HOP_BUDGET_COMPOSE_RESERVE` kept for composing: the turn would die on the
#: wall before the cap could fire, and `_HOP_BUDGET_SPENT` would be
#: unreachable. At three the coach gets `_HOP_BUDGET_SPENT` and composes,
#: instead of the engine cancelling it mid-search.
#:
#: **The arithmetic is a TEST, not a comment**
#: (`test_hop_cap.py::test_the_cap_can_actually_fire_inside_the_node_budget`).
#: An unreachable cap is unfalsifiable.
COACH_HOP_BUDGET = 3
#: T69 / G-119 (ADR-0059) — an ordinary coaching turn makes at most this many model calls,
#: retries included: the planner's judgment (when the Belt answered), the coach, and the one
#: after-agent check (the grader; the coherence judge is retired, ADR-0083). The coach's share is
#: what is left, enforced by `ModelCallLimitMiddleware(run_limit=…)`. The tools stay bound; a coach
#: that calls one past its share is stopped and the move's reply is written in code.
TURN_MODEL_CALLS = 4
AFTER_AGENT_CALLS = 1

#: The graceful off-ramp, and a DIFFERENT guard from the hop budget above.
#: `remaining_steps` is `recursion_limit` minus graph-node transitions; the
#: coach's whole tool loop runs inside ONE node, so this counter moves by 1 per
#: executor turn no matter how many hops that turn made. It therefore cannot
#: count hops — and the hop budget cannot notice the GRAPH running out of room,
#: which is what this catches. At or below the floor the executor coaches with
#: no retrieval tools at all: it composes from what is in hand rather than
#: starting a chain it cannot finish.
REMAINING_STEPS_FLOOR = 2

#: T70 (DEF-078) — the executor's time limit, ENFORCED BY LANGGRAPH: the subgraph registers the
#: node with `timeout=TimeoutPolicy(run_timeout=EXECUTOR_RUN_TIMEOUT)` and
#: `error_handler=executor_timeout_handler(phase)` (`subgraph_common.py`). When the wall fires, the
#: engine cancels the node and runs the handler, which composes the move's own reply in code —
#: never a 500 (G-84), and no hand-written `asyncio.wait_for` budget.
#: 40 s, not 45: the planner's judgment and the composition sit inside the same turn, and R13
#: holds the whole turn to 45 s.
EXECUTOR_RUN_TIMEOUT = 40.0

#: The plain-language text for a turn the coach ran out of time on — never a hard
#: failure, and it says plainly what happened rather than pretending the turn
#: succeeded or returning nothing. Addressed to the BELT, unlike `_HOP_BUDGET_SPENT`.
#: **This module does not send it**: a timed-out turn answers with the move's own
#: reply, written in code (`_fallback_reply`, through `executor_timeout_handler`).
#: The tests recognise it as a degraded answer.
_TIMEOUT_MESSAGE = (
    "I ran out of time on that one before I could finish composing an answer "
    "— I was still gathering material when the turn's limit was reached. "
    "Nothing you have entered is lost." + chr(10) + chr(10) +
    "Asking me something narrower usually gets there: name the single field or "
    "figure you want, or point me at one uploaded file, and I will work from "
    "that rather than searching broadly."
)

#: What the coach reads when it has spent its three hops (ADR-0032). Addressed to the
#: model, not to the Belt — it is a tool RESULT, and the coach's job on reading
#: it is to answer from what it already retrieved.
_HOP_BUDGET_SPENT = (
    "Retrieval budget for this turn is spent — you have made the {budget} "
    "lookups this turn allows. Do not search again. Answer the Belt now from "
    "what you have already retrieved and from the conversation, and say which "
    "part you would look into next turn if something is still missing."
)

#: The plain-language text for a turn that hit the backstop: a partial answer,
#: never a stack trace, handing the turn back rather than pretending the coach
#: finished. **This module does not send it**: the backstop path answers with the
#: move's own reply, written in code (`_fallback_reply`). The hop budget and the
#: `remaining_steps` floor both off-ramp into a composed answer first, so the
#: backstop firing means a genuine runaway loop.
_CAP_MESSAGE = (
    "I went further than I should have chasing that one down, and I have run "
    "out of room this turn. Could you narrow it slightly — a single question, "
    "or the one field you most want to work on — and I will pick it straight "
    "back up? Nothing you have told me is lost."
)

#: The `SummarizationMiddleware` settings (`SUMMARIZATION_TRIGGER` and
#: `SUMMARIZATION_KEEP`, below), verified against the installed class. The
#: current parameter names are `trigger` and `keep`; `max_tokens_before_summary`
#: and `messages_to_keep` are the DEPRECATED spellings the class still warns on,
#: so code copied from an older revision would look plausible and warn at
#: runtime rather than fail.
#:
#: 100_000 is ~78% of gpt-4o's 128k window; 20 turns of raw conversation are
#: kept below the summary. **Safe because facts do not live in `messages`** —
#: they are in `artifacts`, `step_log`, `citations` and the Store.
#: Summarising conversation into prose is correct; summarising FACTS into prose
#: is the failure this policy prevents.
#: The `Literal` in each annotation is the installed signature's, not
#: decoration: `tuple[str, int]` type-checks here and is REJECTED at the call
#: site, because the middleware discriminates the trigger kind on that literal.
#:
#: `RETRY_MAX` — both retry middlewares, both at 2. **"Attempts after the
#: initial call"**, verified in source (`range(self.max_retries + 1)`), so this
#: is THREE attempts, not two.
#:
#: **This is one of two retry caps and they are not merged**: model 2 here and
#: the validation stack's shared 3 at the gate. Different failure modes,
#: different counters, no shared state — merging them would have a network
#: flake consume a gate attempt.
RETRY_MAX = 2

#: **`"continue"` is current; `"return_message"` and `"raise"` are DEPRECATED
#: values the class still accepts and warns on** (verified against the installed
#: middleware — accepted is not the same as current). The current set is
#: `"continue"`, `"error"`, or a callable.
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

    **Returns `None` when no ask declares one (G-63)**, never a placeholder
    column. `SHAPES_BY_PHASE["define"]` is empty, so in Define NO ask ever
    declares a column: a placeholder would make every routed read answer
    `no_such_column`, the coach would hold no data and search anyway, and the
    span would still report success. A read that can only fail is worse than
    no read.

    `None` is the honest answer: the ask layer has nothing to say. The caller
    decides whether to find a column elsewhere or to decline the dispatch.
    """
    for ask in state.get("asks") or []:
        if ask.get("status") == "open" and ask.get("role") == upload.get("role"):
            columns = (ask.get("expected_shape") or {}).get("columns") or []
            if columns:
                return str(columns[0])
    return None


#: DEF-108 — set for the turn when the routed read RAISED: the file was not read, so the upload
#: stays unread and the next turn reads it again (a file with no numeric column is still read).
ROUTED_READ_FAILED: contextvars.ContextVar[bool] = contextvars.ContextVar("routed_read_failed", default=False)


# The executor's setup, between node entry and the agent, is spanned so a
# trace shows where the pre-agent seconds go.
@child_span(run_type="chain", name="executor.setup.dispatch_routed_read",
           process_inputs=lambda i: {})
async def _dispatch_routed_read(state: PhaseState) -> list:
    """The planner's routed read, EXECUTED HERE — the model is not offered this decision.

    The planner owns the routing decision, and it has to reach the turn (G-49).
    An instruction put in front of the model leaves it free to rank a retrieval
    tool above it; dispatching the read in the node removes the decision from
    the model.

    **SCOPED TO ONE CASE, deliberately.** This dispatches `load_evidence_series`
    and only when `_unread_upload` routes to an unread upload. Every other tool
    stays model-chosen — there is no unconditional retrieval pipeline — and
    nothing here decides WHAT to coach.

    **The result arrives as a real tool exchange**, an `AIMessage` carrying the
    call plus its `ToolMessage`, prepended to the turn's messages. Three things
    follow from that shape rather than from extra code: the coach reads the
    values as a tool result it can quote; `_mark_consumed` stamps `consumed_at`
    from the same call it already scans for; and the next turn's history shows
    the file was read, so the coach does not read it again.

    **No hop is spent.** The hop budget counts `rag_lookup_*` calls and
    `load_evidence_series` is not one — the same accounting as when the model
    issues it. A node-issued read that cost a hop would make the guarantee
    compete with the retrieval the coach still needs.

    **Fails soft, and says so.** A blob that cannot be read is a coaching fact,
    not a dead turn: the tool's own message carries it. An exception here
    returns no messages at all and sets `ROUTED_READ_FAILED`, leaving the
    manifest to make the coach aware — degraded rather than broken.
    """
    upload = _unread_upload(state)
    if upload is None or not upload.get("blob_path"):
        return []
    blob_path = str(upload["blob_path"])

    # ── the column: two sources and a refusal (G-63) ───────────────────
    #
    # 1. THE ASK that solicited the upload. Authoritative when it exists,
    #    because it is what the coach asked the Belt for.
    # 2. THE FILE'S OWN HEADER, when no ask declares one. Define populates no
    #    ask shapes, so this is Define's normal path, not its exception.
    #    `first_numeric_column` owns the read — a parse here would be a second
    #    answer to a question `knowledge/tools.py` already owns.
    # 3. NEITHER — and then DO NOT DISPATCH. A read naming a column the file
    #    lacks can only answer `no_such_column`: the coach holds nothing, and
    #    the span reports success either way. Declining leaves the manifest to
    #    make the coach aware — degraded rather than broken, and never a hard
    #    failure to the Belt.
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
        ROUTED_READ_FAILED.set(True)
        return []

    logger.info(
        "executor: DISPATCHED the planner's call — load_evidence_series on %s "
        "[column=%s, from the %s] (§17, option C). The model was not offered "
        "this decision.",
        args["blob_path"], args["column"], column_source,
    )
    return [AIMessage(content="", tool_calls=[call]), result]


def _executor_status(hit_cap: bool, off_ramp: bool,
                     timed_out: bool = False, filtered: bool = False, degraded: Optional[str] = None) -> str:
    """The `step_log` status for one coaching turn — a dict entry, never a tuple.

    The outcomes are deliberately distinguished, and checked in this order: a
    content-filter refusal (T92), a model failure or a token limit (T34 level 4),
    a timeout, the backstop, then a coached turn. **`"coached_no_retrieval"` is
    not a failure**: the graph was low on steps, so the coach answered from
    what it held. That is the design working, and lumping it in with
    `"partial_cap_reached"` would hide the signal — a turn that off-ramped
    cleanly looks nothing like one that died.

    **`"partial_timeout"` must never be silent (G-84).** The Belt got an
    answer, so nothing else in the system would notice the coach never
    finished. This entry is what notices: `step_log` reaches the parent as
    `history` keys (`core/graph.py`), so it is checkpointed with the turn
    rather than living only in a log line.
    """
    if filtered:
        return "content_filter"                  # T92: refused by the Azure filter, not retried
    if degraded:
        return degraded                          # T34 level 4: "model_unavailable" or "token_limit"
    if timed_out:
        return "partial_timeout"
    if hit_cap:
        return "partial_cap_reached"
    return "coached_no_retrieval" if off_ramp else "coached"


def _budgeted_rag_tools(
    tools: list[Any], budget: int, spent: list[int], hops: Optional[list[str]] = None,
) -> list[Any]:
    """The hop cap of three (ADR-0032) — per-turn copies of the three `rag_lookup_*` tools.

    **This is where the hop cap lives**, and it is a count of retrieval calls,
    not a step counter. `recursion_limit` is not the hop cap, and
    `remaining_steps` cannot be either: the whole coach loop runs inside one
    graph node, so `remaining_steps` moves by 1 per turn however many hops the
    turn made (see `REMAINING_STEPS_FLOOR`). Neither counter can see a hop, so
    the hops are counted here.

    **Copies, made fresh per turn**, so the count cannot leak between turns or
    between concurrent cases. `model_copy` keeps `name`, `description`,
    `args_schema` and `response_format` exactly — the tool docstrings are what
    the model reads, and a hand-built replacement tool would quietly reword
    them. Only the coroutine is swapped.

    **Past the budget the tool still answers**, with `_HOP_BUDGET_SPENT` rather
    than a search. That is the graceful part: the coach reads an ordinary tool
    result, sees it has no more lookups, and composes — where a raised
    exception or a vanished tool would end the turn with nothing to say.

    `spent` is a one-element list rather than an `int` because the closure
    mutates it; `nonlocal` cannot reach a caller's local.

    **A round that returns nothing new ends the search** (T26 / G-85, DEF-237): the three copies share the
    turn's set of document ids already returned; a round that returns documents, none of them new, ends the
    search, and every later lookup this turn answers `SEARCH_NOTHING_NEW` without searching. A round that
    returns nothing at all does not end it — the hop cap bounds those. `hops`, when given, is the executor's
    record of each hop, one line each; the executor returns it as `PhaseState.hop_results` (hop results are
    state, never a node local).
    """
    from backend.core.prompts import SEARCH_NOTHING_NEW
    seen: set[str] = set()
    ended = [False]
    record: list[str] = hops if hops is not None else []
    budgeted: list[Any] = []
    for original in tools:
        if original not in RAG_LOOKUP_TOOLS:
            budgeted.append(original)
            continue
        inner = original.coroutine

        async def guarded(_inner: Any = inner, _name: str = original.name, **kwargs: Any) -> Any:
            if ended[0]:
                record.append(f"{_name}: not run — the last round found nothing new")
                return (SEARCH_NOTHING_NEW, [])
            if spent[0] >= budget:
                record.append(f"{_name}: not run — the {budget} lookups this turn allows are spent")
                return (_HOP_BUDGET_SPENT.format(budget=budget), [])
            spent[0] += 1
            named = fusion.CALLING_TOOL.set(_name)   # T69: its variant call is counted to it
            try:
                out = await _inner(**kwargs)
            finally:
                fusion.CALLING_TOOL.reset(named)
            docs = out[1] if isinstance(out, tuple) and len(out) == 2 and isinstance(out[1], list) else []
            ids = [_document_key(d) for d in docs]
            new = [i for i in dict.fromkeys(ids) if i not in seen]
            seen.update(ids)
            record.append(f"{_name}: {len(ids)} document{'s' if len(ids) != 1 else ''}, {len(new)} new")
            if ids and not new:
                ended[0] = True
            return out

        budgeted.append(original.model_copy(update={"coroutine": guarded}))
    return budgeted


def _document_key(doc: Any) -> str:
    """A retrieved document's identity within a turn (DEF-237): its index id, else its source and page, else its
    text."""
    meta = dict(getattr(doc, "metadata", None) or {}) if not isinstance(doc, dict) else doc
    if meta.get("id"):
        return str(meta["id"])
    if meta.get("source_file") or meta.get("page_number"):
        return f"{meta.get('source_file')}#{meta.get('page_number')}"
    return str(getattr(doc, "page_content", "") or meta.get("content") or "")[:200]


def _executor_tools(
    phase: str, hop_budget: int, hops_spent: Optional[list[int]], hops: Optional[list[str]] = None,
) -> list[Any]:
    """What the coach gets to call this turn — the two guards, applied.

    **`hop_budget == 0` is the `remaining_steps` off-ramp**: the three
    `rag_lookup_*` tools are not bound at all, so the coach cannot start a
    retrieval chain the graph has no room to finish. **The other four of the
    universal seven stay** (`propose_template`, `propose_diagram`,
    `load_evidence_series`, `read_upload`), and so do the phase's computation
    tools — the off-ramp is about not STARTING new retrieval, not about
    coaching with one hand tied.

    Any other budget binds all seven, with the retrieval three counted
    (`_budgeted_rag_tools`).
    """
    tools = UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]
    if hop_budget <= 0:
        return [t for t in tools if t not in RAG_LOOKUP_TOOLS]
    return _budgeted_rag_tools(tools, hop_budget, hops_spent
                               if hops_spent is not None else [0], hops)


@child_span(run_type="chain", name="executor.setup.build_executor",
           process_inputs=lambda i: {"phase": i.get("phase")},
           process_outputs=lambda o: {})
def _build_executor(
    phase: str, state: PhaseState, config: Optional[RunnableConfig] = None,
    *, hop_budget: int = COACH_HOP_BUDGET, hops_spent: Optional[list[int]] = None,
    hop_results: Optional[list[str]] = None,
    script_log: Optional[list[dict[str, Any]]] = None,
    coach_limit: int = TURN_MODEL_CALLS - AFTER_AGENT_CALLS,
    turn_type: str = turn_tools.TEACHING,
    attempts: Optional[list[dict[str, Any]]] = None,
) -> tuple[Any, list[dict[str, Any]]]:
    """The phase coach — `create_agent`.

    **Both parameter names were verified against the installed
    `langchain.agents.create_agent`**: the signature carries `system_prompt`
    and has **no** `prompt` parameter, so `prompt=` would raise `TypeError` at
    construction rather than being silently ignored.

    **Tools are passed to `create_agent(tools=...)`, never bound onto the
    model.** Binding onto a bare model bypasses the entire middleware stack —
    grading, skills, compression, state injection, retry and contradiction —
    and does it silently. `pattern-8-bind-tools-in-phase-executor` guards this
    file for that reason.

    **Declaration order is execution order for hooks of the same kind**, so the
    middleware order is binding. `BeforeModelStateInjection` MUST be first —
    project facts have to reach the top of the prompt before skills loading
    and summarisation shape it.

    **The system prompt is STATIC per phase.** This turn's project facts arrive
    through `BeforeModelStateInjection`, never composed into the prompt here:
    both would inject the same facts twice, and the copy not derived from the
    shared gate computation would drift.

    Still constructed per turn: several middlewares are built with this turn's
    state and plan, so the agent cannot outlive it. That is cheap next to the
    model call it wraps.
    """
    # The grader's sink: a list the node owns, so the grader writes its audit
    # record without reaching into state (internals never reach PhaseState),
    # and per turn, so it cannot outlive the turn.
    grader_log: list[dict[str, Any]] = []
    plan = state.get("coaching_plan")
    agent = create_agent(
        # ADR-0101 decision 1: the coach's inner agent is not checkpointed — None would inherit the parent's
        # saver and write its ~10 internal steps a turn to Blob, read by nothing; no interrupt lives inside it
        # (DEF-040 pauses in a node of its own), and a crashed turn is abandoned (ADR-0080).
        checkpointer=False,
        model=get_llm("coach", max_tokens=1500),
        tools=_executor_tools(phase, hop_budget, hops_spent, hop_results),
        response_format=coaching_response_model(phase),   # never a {Phase}Output; typed per phase (G-252)
        middleware=[
            # 1 — before_agent. FIRST, and that is a rule, not a preference.
            BeforeModelStateInjection(
                phase, state, config,
                prior_documents=_prior_gate_documents(phase, config),
                # DEF-108 (W5) — on an upload turn, the file section 5 names, routed in code.
                upload=_unread_upload(state) if turn_type == turn_tools.UPLOAD else None,
            ),
            # 2 — before_agent + a registered `load_skill` tool.
            DMAICSkillsMiddleware(
                phase,
                # Each delivery of the phase script, for step_log.
                on_delivery=script_log.append if script_log is not None else None,
                # The current field's block; the opening only while the
                # conversation holds no coach reply — never in Define, whose welcome the server builds (DEF-200) and
                # whose first element the welcome's card teaches (R-A, R-C; founder test 2026-10-27 #11).
                focus_field=plan.focus_field if plan else None,
                opening=phase != "define" and not any(isinstance(m, AIMessage) for m in (state.get("messages") or [])),
            ),
            # 3 — before_model. LangChain core, used as shipped.
            SummarizationMiddleware(
                model=get_llm("summarizer"),
                trigger=SUMMARIZATION_TRIGGER,
                keep=SUMMARIZATION_KEEP,
            ),
            # ADR-0069 — LangChain's dynamic tool selection: every tool stays registered; this
            # wrap_model_call offers the model only the turn type's tools (`request.override(tools=…)`)
            # — none on an answer turn.
            turn_tools.turn_tools_middleware(turn_type, coach_limit),
            # T69 / G-119 (ADR-0059) — the coach's share of the turn's model calls. Declared
            # before the retry, so it encloses it: a retried call is one call of the budget.
            # Its state schema (ModelCallLimitState) is its own; the list is typed on AgentState.
            cast(Any, ModelCallLimitMiddleware(run_limit=coach_limit, exit_behavior="end")),
            # T34 (ADR-0059 decision 2, ADR-0082) — level 2: when the premium call has failed through its
            # retries, the same request on the operational deployment, retried the same way. As shipped.
            ModelFallbackMiddleware(get_fallback_llm("coach")),
            # Level 1 — wrap_model_call, the INVISIBLE retry tier: the network flaked, so retry the same
            # call (the fallback above swaps the model). `max_retries` is "attempts after the initial
            # call", so 2 means three attempts. `on_failure="error"`, so a call that fails through its
            # retries reaches the fallback. T92 (ADR-0067): a content-filter refusal is never retried.
            ModelRetryMiddleware(max_retries=RETRY_MAX, retry_on=content_safety.retry_on, on_failure="error"),
            # ADR-0082 — innermost of the three: a content-filter refusal (T92) or a token-limit 400
            # becomes a marked reply, so neither the retry nor the fallback sees it; every attempt is logged.
            model_fallback.kept_from_fallback_middleware(attempts),
            # **The same nesting rule, one layer out.** Position 1 is declared
            # first, so it is the OUTERMOST layer, and it also wraps the model
            # call. Its wrap therefore encloses the retry: the project-state
            # block is composed and prepended ONCE, and a retry re-sends the
            # built request rather than rebuilding it per attempt (3 model
            # calls, 1 composition, 1 prepend). Declaration is nesting;
            # `test_position_1_wrap_encloses_position_4_retry` pins it, because
            # if the layering inverted, three attempts would mean three Store
            # reads and three missing-field computations.
            #
            # 5 — wrap_tool_call. A failed retrieval is not a failed model
            # call and `ModelRetryMiddleware` never sees it.
            # `on_failure="continue"` is what keeps the coaching loop alive:
            # the coach reads a failure result and works around it instead of
            # the graph dying mid-session.
            ToolRetryMiddleware(
                max_retries=RETRY_MAX, on_failure=TOOL_RETRY_ON_FAILURE,
                retry_on=content_safety.retry_on,                    # T92
            ),
            # T87 / ADR-0062 point 2 (DEF-144) — personal data in TOOL RESULTS is redacted before
            # the model reads it (`before_model`); never the Belt's own messages. One per type.
            *pii.executor_middleware(),
            # ══════════════════════════════════════════════════════════════
            # THIS LIST IS NESTING ORDER, NOT EXECUTION ORDER.
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
            #   else spends effort on it.
            #
            #   So the layering below IS the intent, not a workaround for it:
            #   on the way out, contradiction runs first and the grader last.
            #   `test_the_declared_middleware_list_is_the_ratified_layering`
            #   asserts what executes, not what is listed.
            #
            #   LangChain offers no other control: no priority, no ordering
            #   attribute, and `hook_config` governs `can_jump_to` rather than
            #   sequence. List position is the only lever there is.
            # ══════════════════════════════════════════════════════════════
            DMAICGraderMiddleware(
                phase, on_evaluation=grader_log.append,
                # Graded as the move it was asked to make.
                move=plan.move if plan else None,
                # The case's confirmed values, for the "already given" criterion.
                context=_grader_context(phase, state, plan.focus_field if plan else None),
                # The coach's own sources — the element's script block as the coach was given it, the
                # Belt's words for the element, the answer awaiting a Confirm.
                purpose=_grader_method(phase, plan.focus_field if plan else None),
                sources=_grader_sources(phase, plan),
                # G-254 (founder ruling 2026-10-27, item 3): given, never graded as the coach's own claim.
                given=_grader_given(phase, state, plan.focus_field if plan else None),
                # A1 (founder ruling 2026-10-27): this turn's planner judgment, given; G2's missing items.
                decision=_grader_decision(phase, plan)[0], missing=_grader_decision(phase, plan)[1],
                # F4: a rewrite (enforce mode) never runs past the executor node's own wall.
                deadline=time.monotonic() + EXECUTOR_RUN_TIMEOUT,
            ),
            ContradictionDetectionMiddleware(),
        ],
        system_prompt=PHASE_COACH_PROMPT[phase],   # NOT `prompt=`
    )
    return agent, grader_log


@child_span(run_type="chain", name="executor.setup.prior_gate_documents",
           process_outputs=lambda o: {"documents": len(o) if isinstance(o, dict) else None})
def _prior_gate_documents(
    phase: str, config: Optional[RunnableConfig] = None
) -> dict[str, dict]:
    """Earlier phases' approved values, for the coach's prompt (`BeforeModelStateInjection`).

    Read from `v1_phase_inputs` on `config`, which the route assembles from the
    case document for every phase; only the phases before this one are kept.
    **It matters that it reads something**: without prior committed values in
    the prompt the coach has nothing to compare against, and the contradiction
    check silently detects nothing.
    """
    configurable = (config or {}).get("configurable") or {}
    prior = configurable.get("v1_phase_inputs") or {}
    upto = PHASE_ORDER.index(phase)
    return {
        name: dict(values)
        for name, values in prior.items()
        if values and name in PHASE_ORDER[:upto]
    }


def captured_entries(reply: Optional[CoachingResponse]) -> list[dict[str, Any]]:
    """G-252: the reply's read-back entries as plain records — typed entries (the schema's) and records alike."""
    # dict(e), not model_dump(): the value stays the object the coach sent — nothing is coerced or copied.
    return [dict(e) for e in ((reply.fields_captured if reply else None) or []) if isinstance(e, (BaseModel, dict))]


def _captured_fields(phase: str, reply: CoachingResponse) -> dict[str, Any]:
    """`fields_captured` as a dict, field name -> value: the coach's captures, from which a
    read-back's pending value is taken. Nothing reaches `artifacts` from here before the Belt
    confirms.

    **Entries without a `field_name` are dropped, not guessed.** The coach is
    told the exact names; an entry that does not carry one is a malformed
    capture, and inferring which field was meant is how a value lands under the
    wrong key and reaches a gate document unnoticed.

    `value` stays whatever the model sent — `Any`, deliberately: it must carry
    both plain strings and the three cross-phase reference dicts, and coercing
    to `str` here would make `causal_hypothesis` uncapturable.
    """
    out: dict[str, Any] = {}
    for entry in captured_entries(reply):
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
    """Which Belt turn this is, counted in the conversation itself.

    **NOT `turn_count`, and the difference is load-bearing.** `turn_count` is
    seeded to `0` by the input mapper on every invoke and read by `core/graph.py`
    as the ENTRY MODE — `0` means "coach one turn", non-zero means "we are here
    for the gate" — so on a coaching turn it is `0` every time, and every
    `step_log` key of every turn of a phase reads `{phase}:0:{node}`. A change
    log keyed on it would have each turn overwrite the one before.

    **The conversation is the one thing that does accumulate**: the parent's
    `messages` carry it across turns and the input mapper copies it down, so the
    number of Belt messages IS the turn ordinal. It is also stable under a
    REPLAY — a resumed turn has the same conversation and so the same ordinal —
    which makes the `field_log` key idempotent rather than merely unique.
    """
    return sum(1 for m in (state.get("messages") or [])
               if isinstance(m, HumanMessage))


#: R16 (DEF-082) — where a stored value came from: typed by the Belt (their own words stored), read
#: from an upload, or proposed by the coach (a composed or structured read-back) and confirmed.
FIELD_LOG_SOURCES: tuple[str, ...] = ("typed", "upload", "coach_proposed")


def _value_source(field: str, value: Any, pending: Optional[dict[str, Any]]) -> str:
    """R16's source for one stored value, decided in code from the read-back the Belt confirmed: the
    coach's capture marked `upload` → upload; the stored text is found in the Belt's own words (a
    string, or a MetricValue's raw) → typed; anything else the coach composed → coach_proposed."""
    pending = pending or {}
    if (pending.get("sources") or {}).get(field) == "upload":
        return "upload"
    words = " ".join(str(pending.get("belt_words") or "").split())
    said = value.get("raw") if isinstance(value, dict) and "raw" in value else value
    if words and isinstance(said, str) and " ".join(said.split()) and " ".join(said.split()) in words:
        return "typed"
    return "coach_proposed"


def _field_log_entries(
    phase: str,
    turn: int,
    captured: dict[str, Any],
    prior: dict[str, Any],
    reply: CoachingResponse | None,
    at: str,
    *,
    pending: Optional[dict[str, Any]] = None,
    by: Optional[str] = None,
) -> list[dict[str, Any]]:
    """One entry per CHANGE this turn made to a captured field.

    **The first capture of a field is a change too**, and carries
    `prior_value: None`. A re-statement of the value already held is NOT: the
    Belt repeating themselves is not a revision, and logging it would bury the
    revisions that matter under turns where nothing moved.

    **`reason` is the Belt's stated reason for a revision, where given** (G-89):
    the capture entry's `reason` (`CapturedValue.reason`), or the one the
    confirmed read-back carried on the pending value (DEF-021). A first capture
    carries `reason: None`. **Kept as a column even when empty**: a column that
    exists and is empty says "no reason was given"; a column that does not
    exist says nothing at all, and the next reader has to rediscover why.

    `prior_value: None` also reads as "first capture" when the prior value was
    itself empty; `split_captures` keeps empty values out of `artifacts`, so an
    empty prior comes only from a record written some other way.
    """
    # DEF-021: a value is stored on the Confirm turn, from the read-back the Belt confirmed — so the
    # reason the coach captured then travels on the pending value.
    reasons: dict[str, str] = {str(k): str(v) for k, v in ((pending or {}).get("reasons") or {}).items() if v}
    for entry in captured_entries(reply):
        name = str(entry.get("field_name") or "").strip()
        reason = str(entry.get("reason") or "").strip()
        if name and reason:
            reasons[name] = reason

    # ADR-0112: an answer the Belt keeps despite the mismatch it was told — noted on its element's entry, dated.
    from backend.middleware.state_injection import mismatch_kept
    kept = mismatch_kept(phase, (pending or {}).get("mismatch"))
    kept_on = str((pending or {}).get("field") or "")

    entries: list[dict[str, Any]] = []
    for field, value in captured.items():
        seen = field in prior
        if seen and prior[field] == value:
            continue
        given = reasons.get(field) if seen else None
        entries.append({
            "key":         field_log_key(phase, turn, field),
            "field":       field,
            "phase":       phase,
            "turn":        turn,
            "value":       value,
            "prior_value": prior[field] if seen else None,
            "timestamp":   at,
            "reason":      "; ".join(r for r in (given, kept if field == kept_on else "") if r) or None,
            "by":          by,                                       # R16: the signed-in person
            "source":      _value_source(field, value, pending),
        })
    return entries


#: How the installed LangChain renders the structured response into the
#: conversation (`langchain/agents/factory.py`: f"Returning structured
#: response: {structured_response}"). Matched EXACTLY before a rewrite, so a
#: framework that renders it differently leaves the message untouched.
_STRUCTURED_PREFIX = "Returning structured response: "


def _with_progress(messages: list, reply: CoachingResponse, label: str) -> list:
    """Set `reply.progress` to the computed figure, and re-render the one
    structured-response message that carried the model's count.

    A new `ToolMessage` with the same id, name and `tool_call_id`, so the
    tool-call pairing the next model call depends on is unchanged. Plain
    string content: this code constructs the message.
    """
    reply.progress = label
    after = f"{_STRUCTURED_PREFIX}{reply}"
    # The last structured-response message, found by its prefix: code may have changed a block since the
    # model wrote it (G-170's sample, G-175's next element), and the re-render carries those changes too.
    last = max((i for i, m in enumerate(messages)
                if isinstance(m, ToolMessage) and str(m.content).startswith(_STRUCTURED_PREFIX)), default=None)
    return [
        ToolMessage(content=after, tool_call_id=m.tool_call_id, name=m.name, id=m.id) if i == last else m
        for i, m in enumerate(messages)
    ]


#: The render contract — the blocks besides `message`, in render order.
COACHING_BLOCKS: tuple[str, ...] = ("explanation", "example", "prompt", "progress")


def _strip_mark(example: str) -> str:
    """A sample without the C3 mark in front of it."""
    from backend.core.prompts import SAMPLE_MARK
    return example.replace(SAMPLE_MARK, "", 1).strip()


def _with_sample_mark(reply: CoachingResponse | None) -> CoachingResponse | None:
    """C3 (DEF-083): every sample the Belt is shown carries the mark, written in code."""
    from backend.core.prompts import SAMPLE_MARK
    example = str(getattr(reply, "example", "") or "").strip() if reply is not None else ""
    if reply is None or not example or example.startswith(SAMPLE_MARK):
        return reply
    return reply.model_copy(update={"example": f"{SAMPLE_MARK}\n{example}"})


def _previous_sample(state: Any) -> str:
    """The sample under the request the Belt is answering now — the previous reply's `example`
    block when that reply asked for information (teach, challenge, store and advance). A read-back's
    block is not a request's sample: it may carry the very value the Belt is confirming."""
    for m in reversed(list((state or {}).get("messages") or [])):
        if isinstance(m, AIMessage):
            kw = m.additional_kwargs or {}
            move = (kw.get(moves.MOVE_RECORD_KEY) or {}).get("move")
            if move not in (moves.TEACH, moves.CHALLENGE, moves.STORE_AND_ADVANCE):
                return ""
            card = (kw.get(TEACHING_CARD_KEY) or {}).get("example") or {}
            if card.get("rows"):
                # R-C (ADR-0114): a teaching turn's sample is its card's example — its cells, never its row labels.
                first = 1 if (card.get("columns") or [""])[0] in ("Part", "Question", "Dimension") else 0
                return " ".join(str(c) for row in card["rows"] for c in row[first:])
            return _strip_mark(str((kw.get("coaching_blocks") or {}).get("example") or ""))
    return ""


def _attach_blocks(messages: list, reply: CoachingResponse | None,
                   warning: str | None) -> None:
    """Put this turn's coaching blocks, and the grader's warning, on the reply.

    **Beside `message`, never instead of it:** the AI message's
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
    """What the next turn's planner reads to know where this field stands:
    the field this reply worked on, the move, the Belt's words so far, the
    read-back awaiting confirmation (PENDING), what was stored."""
    if plan is None:
        return None
    carries_answer = plan.move in (moves.CHALLENGE, moves.READ_BACK, moves.RESPOND)
    return {
        "field": plan.focus_field,
        # ADR-0086: a store turn that ends with the target read back from the goal shows a
        # read-back — its Confirm and Change buttons are the target's.
        "move": moves.READ_BACK if goal_read_back(plan) is not None else plan.move,
        "status": plan.status,
        "answer": plan.answer if carries_answer else "",
        "messages": plan.messages if carries_answer else 0,
        "pending": pending,
        "stored": sorted(stored),
        "stored_field": plan.stored_field,
        "judgment": plan.judgment.model_dump() if plan.judgment else None,
    }


def _element_purpose(phase: str, field: Optional[str]) -> str:
    """The element's purpose as the script gives it (its explanation block) and its acceptance criteria,
    for the grader — from the phase script, no retrieval."""
    if not field:
        return ""
    from backend.middleware.skills import acceptance_criteria, teaching_blocks
    purpose = teaching_blocks(phase, field).get("explanation", "")
    criteria = "\n".join(f"- {cid}: {text}" for cid, text in acceptance_criteria(phase, field))
    return purpose + (f"\nAcceptance criteria:\n{criteria}" if criteria else "")


def _grader_method(phase: str, field: Optional[str]) -> str:
    """The method for the element exactly as the coach was given it —
    its block of the phase script (what it is, why it matters, the worked example, the ask, the acceptance
    criteria); with no element, the closing block."""
    from backend.middleware.skills import script_section
    return script_section(phase, field, False)


def _grader_sources(phase: str, plan: Optional[CoachingPlan]) -> str:
    """What the Belt has given for the element this turn works on, as the coach had it — section 3's answer
    awaiting Confirm, else the Belt's words: the composer's own lines (ADR-0111 D5), never cut, values in tags."""
    from backend.middleware.state_injection import element_sources
    return element_sources(phase, plan)


def _grader_context(phase: str, state: PhaseState, field: Optional[str]) -> str:
    """The case's confirmed values, for the grader's "already given" criterion — section 3's, by the same function
    (ADR-0111 D5; G-252: never cut, the element's own values and those it builds on whole, every other in one line;
    display names, each value in its tag)."""
    from backend.middleware.state_injection import confirmed_values, turn_artifacts
    return "\n".join(confirmed_values(phase, turn_artifacts(state), field))


def _grader_decision(phase: str, plan: Optional[CoachingPlan]) -> tuple[str, tuple[str, ...]]:
    """A1 (founder ruling 2026-10-27): this turn's planner judgment, given to the grader — its verdict and what it
    found missing, in words — and, on a challenge, the missing item G2's code check looks for in the reply: the
    criterion not met, as the element's criteria say it, else the judgment's own words for what is missing."""
    judgment = getattr(plan, "judgment", None) if plan is not None else None
    if plan is None or judgment is None:
        return "", ()
    from backend.middleware.skills import acceptance_criteria
    named = dict(acceptance_criteria(phase, plan.focus_field)) if plan.focus_field else {}
    item = named.get(str(judgment.failed_criterion or "").strip(), "")
    decision = f"{judgment.verdict} — {judgment.reason}" + (f" (the criterion not met: {item})" if item else "")
    missing = item or (judgment.reason if judgment.verdict == "insufficient" else "")
    return decision, ((missing,) if missing and plan.move == moves.CHALLENGE else ())


def _grader_given(phase: str, state: PhaseState, field: Optional[str]) -> tuple[str, ...]:
    """G-254 (founder ruling 2026-10-27, item 3): what a reply may carry as given, never as the coach's own claim —
    the element's worked example as the phase script gives it, and the lines code writes for it (the calculation's
    two figures, the sample's mark). They reach the grader tagged as given, and a fail quoting one is not counted."""
    if not field:
        return ()
    from backend.core.prompts import SAMPLE_MARK
    from backend.middleware.skills import element_text
    from backend.middleware.state_injection import turn_artifacts
    from backend.phases import calculations
    arts = turn_artifacts(state)
    lines = calculations.how_it_was_calculated(calculations.current(arts, phase, field), arts)
    return tuple(t for t in (element_text(phase, field, "Show"), *lines.splitlines(), SAMPLE_MARK) if t.strip())


def _quality_feedback(grader_log: list[dict[str, Any]]) -> dict[str, Any] | None:
    """This turn's quality verdict, for the NEXT turn's section 4: the grader's
    failed criteria with their feedback. `None` when it did not run or runs
    log-only (the coherence judge is retired, ADR-0083)."""
    # A judge in `log_only` mode changes nothing — its verdict is recorded in step_log and does not
    # reach the coach's next turn.
    g = grader_log[-1] if grader_log and grader_mode.GRADER_MODE == "enforce" else None
    if g is None:
        return None
    return {
        "grader": ({"status": g.get("status"), "criteria_failed": list(g.get("criteria_failed") or []),
                    "feedback": list(g.get("feedback") or []),
                    "failed": list(g.get("failed") or []), "move": g.get("move")} if g else None),
    }



def _element_card(phase: str, record: dict | None, artifacts: dict[str, Any],
                  plan: Optional[CoachingPlan], case: Optional[dict] = None,
                  kept: Optional[dict[str, Any]] = None) -> tuple[dict | None, dict | None]:
    """ADR-0093 decisions 2 and 3: the read-back card, drawn in code from the exact value a Confirm will store
    (the record's pending store over the case's values) — Confirm opens only under a read-back with every
    required criterion met; a challenge made because a Confirm could not store shows the same card with Confirm
    closed. After a Confirm, the saved note naming every element it stored, in short, and its Gate section
    (DEF-290). (None, None) otherwise."""
    if phase != "define" or record is None:
        return None, None
    from backend.phases.define import templates
    pending = record.get("pending") or goal_read_back(plan)
    field = str((pending or {}).get("field") or "")
    strip = None
    if record.get("stored_field") in templates.TEMPLATES:
        stored = [f for f, keys in moves.positions(phase)
                  if f == record["stored_field"] or any(k in (kept or {}) for k in (f, *(keys or ())))]
        strip = templates.strip(stored, artifacts)
    if pending and field in templates.TEMPLATES and record.get("move") == moves.READ_BACK:
        card = templates.card(field, {**artifacts, **dict(pending.get("store") or {})}, spans=pending.get("spans"),
                              upload=pending.get("upload"), belt_words=str(pending.get("belt_words") or ""),
                              case=case)
        return card, strip
    return None, strip


def _short_card(phase: str, field: Optional[str], pending: dict | None, artifacts: dict[str, Any],
                case: Optional[dict] = None) -> dict | None:
    """ADR-0093: the card of a read-back a Confirm could not store (G-163) — its rows show what is open; Confirm
    stays closed."""
    if phase != "define" or not pending or not field:
        return None
    from backend.phases.define import templates
    if field not in templates.TEMPLATES:
        return None
    # A read-back made again after a refused Confirm carries the refused value under `earlier`.
    values = {**artifacts, **dict(pending.get("earlier") or {}), **dict(pending.get("store") or {})}
    card = templates.card(field, values, spans=pending.get("spans"), upload=pending.get("upload"),
                          belt_words=str(pending.get("belt_words") or ""), case=case)
    return {**card, "confirm": False}


def _reply_element(phase: str, record: dict | None) -> dict | None:
    """ADR-0093 (DEF-196): the element this reply works on — "Element n of 13 · name", one numbering for the
    chat, the progress view and the Gate (the coached order). None outside Define or with no element."""
    field = str((record or {}).get("field") or "")
    if phase != "define" or field not in DEFINE_FIELD_ORDER:
        return None
    from backend.phases.define import templates
    return {"field": field, "n": templates.number_of(field), "of": len(DEFINE_FIELD_ORDER),
            "name": templates.name_of(field)}


def _attach_card(messages: list, card: dict | None, strip: dict | None, element: dict | None = None) -> None:
    """Put the card, the strip and the reply's element on the reply — the last AI message. Mutates in place."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            for key, value in ((CARD_KEY, card), (STRIP_KEY, strip), (ELEMENT_KEY, element)):
                if value is not None:
                    msg.additional_kwargs[key] = value
            return


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
            ask = text.split(":**", 1)[-1].strip()
            # G-130 (DEF-161): a sentence carrying a script placeholder ({baseline_estimate}) is the
            # model's to fill; a reply written in code leaves it out rather than show it raw.
            kept_sentences = [x for x in re.split(r"(?<=[.?!])\s+", ask) if not re.search(r"\{[^{}]*\}", x)]
            return " ".join(kept_sentences).strip() or f"Could you tell me about your {(field or 'next step').replace('_', ' ')}?"
    return f"Could you tell me about your {(field or 'next step').replace('_', ' ')}?"


def _fallback_reply(phase: str, plan: Optional[CoachingPlan]) -> CoachingResponse:
    """The move's reply, written by CODE.

    Used when the coach model did not finish its move (the node's time limit,
    the runaway backstop, the call limit, a turn with no structured reply) or
    its reply could not be kept (a number no source gives). The move is already
    decided, so the Belt still gets that move — never a message about the
    system running out of room."""
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


def _refused_turn(phase: str, state: PhaseState, plan: Optional[CoachingPlan], prior: list[Any],
                  filtered: bool) -> tuple[CoachingResponse, dict[str, Any]]:
    """A turn the coach model did not answer, answered in code (ADR-0082): a content-filter refusal gets
    T92's guidance reply; a model failure through both levels, or a token-limit 400, gets the level-4
    reply naming the phase and the captured count. Either way the exchange is marked as the
    guard marks a block, so `guard.without_blocked` keeps it from every later model call and the
    reload: the Belt sends the message again and it is not doubled."""
    if filtered:
        text = guard_messages.reply(guard_messages.AZURE, phase, plan.focus_field if plan else None)
        mark = {"status": "blocked", "threat": "azure", "rule": "content_filter"}
    else:
        captured, total = captured_count(phase, dict(state.get("artifacts") or {}))
        text = guard_messages.LEVEL_4.format(phase=phase.capitalize(), captured=captured, total=total)
        mark = {"status": "blocked", "threat": "unavailable", "rule": "model_unavailable"}
    reply = CoachingResponse(message=text, prompt="")
    refused = AIMessage(content=text, additional_kwargs={guard.NODE: mark})
    return reply, {"messages": [*prior, refused], "structured_response": reply}


#: G-138 — the moves that teach a field: its first reply carries all three teaching blocks.
TEACHING_MOVES = (moves.TEACH, moves.STORE_AND_ADVANCE)


def _with_teaching_blocks(phase: str, plan: Optional[CoachingPlan], reply: CoachingResponse,
                          gaps: list[str]) -> CoachingResponse:
    """G-138 (DEF-005): on a teaching move, a block the coach returned empty is written in code
    from the field's script (`skills.teaching_blocks`) — what it is and why, the marked
    illustration, the question — the same source the coach is given. A block the coach wrote is
    never replaced. Returns a COPY with the blocks filled (the reply itself is not changed), or
    `reply` when nothing is filled."""
    if plan is None or plan.move not in TEACHING_MOVES or not plan.focus_field:
        return reply
    from backend.middleware.skills import teaching_blocks
    script = teaching_blocks(phase, plan.focus_field)
    filled: dict[str, Any] = {k: script[k] for k in ("explanation", "example", "prompt")
                              if k in gaps and script.get(k)}
    if not filled:
        return reply
    logger.info("%s.executor: G-138 — teaching block(s) %s of `%s` written from the script",
                phase, ", ".join(filled), plan.focus_field)
    return reply.model_copy(update=filled)


#: G-170 (C3) — the moves that ask for new information: their
#: example block is the element's worked example from the script. A read-back asks for none.
SAMPLE_MOVES = (moves.TEACH, moves.CHALLENGE, moves.STORE_AND_ADVANCE, moves.RESPOND)


def _with_script_sample(phase: str, plan: Optional[CoachingPlan], reply: CoachingResponse) -> CoachingResponse:
    """G-170: the example block is the phase script's worked example for the element being asked for,
    inserted by code — never the coach's, so never the Belt's or the case's values (C3). A
    move that asks for nothing new (a read-back) shows none. Returns a COPY, or `reply`."""
    example = ""
    if plan is not None and plan.move in SAMPLE_MOVES and plan.focus_field and goal_read_back(plan) is None:
        from backend.middleware.skills import teaching_blocks
        example = teaching_blocks(phase, plan.focus_field).get("example", "")
    return reply if str(reply.example or "") == example else reply.model_copy(update={"example": example})


def _teach_next(phase: str, plan: Optional[CoachingPlan], reply: CoachingResponse) -> CoachingResponse:
    """G-175: after a store, the reply teaches the NEXT
    element — its explanation and its question come from that element's script (its sample is G-170's);
    and the message's own questions go, so the one ask is the next element's. Returns a COPY, or `reply`."""
    if plan is None or plan.move != moves.STORE_AND_ADVANCE or not plan.focus_field:
        return reply
    from backend.middleware.skills import teaching_blocks
    nxt = teaching_blocks(phase, plan.focus_field)
    if not nxt:
        return reply
    update: dict[str, Any] = {k: nxt[k] for k in ("explanation", "prompt") if nxt.get(k)}
    lines = [" ".join(s for s in _SENTENCE_END.split(line) if not s.rstrip().endswith("?"))
             for line in str(reply.message or "").split(chr(10))]
    message = chr(10).join(lines).strip()
    if message and message != reply.message:
        update["message"] = message
    return reply.model_copy(update=update)


def _card_note(phase: str, plan: CoachingPlan) -> str:
    """R-C: why an element is taught again, in plain words from code — after a park, a try-again or the return to a
    parked element; "" for a first teaching."""
    reason = str(plan.reason or "")
    named = re.findall(r"`(\w+)`", reason)
    if reason.startswith(moves.PARKED_REASON.split("`")[0]) and named:
        return f"{guard_messages.element_name(phase, named[0])} is parked — we come back to it before the report."
    if reason.startswith(moves.TRY_AGAIN_REASON.split("`")[0]):
        return "Let's go through this one again."
    if reason.startswith(moves.RETURN_REASON.split("`")[0]):
        return "Every other element is confirmed. Back to this one, which was parked."
    return ""


def _teaching_card(phase: str, state: PhaseState, plan: Optional[CoachingPlan]) -> Optional[dict[str, Any]]:
    """R-C (ADR-0114 decisions 2 and 4): on a Define move that teaches an element — taught first, or taught next after
    a Confirm — the element card, assembled in code from the skill and the state (the values this Confirm stores
    included); the card is the whole of the teaching and the turn makes no coach model call. None otherwise."""
    if phase != "define" or plan is None or plan.move not in TEACHING_MOVES or not plan.focus_field:
        return None
    from backend.phases.define import templates
    if plan.focus_field not in templates.TEMPLATES:
        return None
    store = dict(plan.store or {}) if plan.move == moves.STORE_AND_ADVANCE else {}
    stored = [f for f, fields in moves.positions(phase) if any(k in store for k in (f, *(fields or ())))]
    return templates.teaching_card(plan.focus_field, {**dict(state.get("artifacts") or {}), **store},
                                   dict(plan.field_status or {}), stored=stored, note=_card_note(phase, plan))


def _written_reply(phase: str, state: PhaseState, plan: Optional[CoachingPlan], written: Optional[CoachingResponse],
                   *, engine_timeout: bool, turn_type: str) -> tuple[Optional[CoachingResponse], Optional[dict]]:
    """`executor`'s reply when code writes it, and the element card when it is one; (None, None) when the coach
    writes the turn. A Change click, a status question, the goal's target and a value offered from an earlier answer
    are answered in code; R-C (ADR-0114 decision 4): a teaching move's reply is the element card, assembled in code —
    no coach call. An upload turn stays the coach's (W5, DEF-108; locked 2026-10-28: an upload starts its own turn)."""
    written = written if written is not None else (_change_reply(plan) or _status_reply(phase, state, plan)
                                                    or _goal_target_reply(phase, plan) or _offer_reply(phase, plan)
                                                    or _link_added_reply(plan))
    if written is not None or engine_timeout or turn_type == turn_tools.UPLOAD:
        return written, None
    teaching = _teaching_card(phase, state, plan)
    if teaching is None:
        return None, None
    from backend.phases.define.templates import card_text
    return CoachingResponse(message=card_text(teaching)), teaching


def _link_added_reply(plan: Optional[CoachingPlan]) -> Optional[CoachingResponse]:
    """R-H: the SIPOC read back again after "Add step n to the problem statement", written in code — the steps added,
    and that its one Confirm stores the changed problem statement with it. No coach call."""
    head = moves.LINK_ADDED_REASON.split("{")[0]
    if plan is None or plan.move != moves.READ_BACK or not str(plan.reason or "").startswith(head):
        return None
    from backend.core.prompts import LINK_ADDED
    return CoachingResponse(message=LINK_ADDED.format(steps=str(plan.reason)[len(head):].split(".")[0]))


def _link_check(phase: str, pending: Optional[dict], prior: dict[str, Any]) -> Optional[dict[str, Any]]:
    """R-H (founder ruling 2026-10-27): the SIPOC's link check as the page draws it under the challenge — each step with
    team-noted problems the problem statement does not mention, with the problem and who said it, and the two buttons'
    words. None when no such step."""
    pair = _r18_pair(phase, "process_map_sipoc", dict((pending or {}).get("store") or {}), prior)
    if pair is None:
        return None
    from backend.core.prompts import LINK_ADD_LABEL, LINK_KEEP_LABEL
    from backend.phases.define import parse
    sipoc, fivew = pair
    ignored = parse.link_mismatch(fivew.get("steps"), sipoc)["ignored"]
    steps = parse.process_steps(sipoc.get("process_steps"))
    flagged = [{"n": i + 1, "name": s["name"],
                "notes": [" — ".join(x for x in (str(p.get("note") or ""), str(p.get("said_by") or "")) if x)
                          for p in s["problems"] if isinstance(p, dict)]}
               for i, s in enumerate(steps) if s["name"] in ignored]
    if not flagged:
        return None
    numbers = [str(f["n"]) for f in flagged]
    which = numbers[0] if len(numbers) == 1 else ", ".join(numbers[:-1]) + " and " + numbers[-1]
    return {"flagged": flagged, "add": LINK_ADD_LABEL.format(s="" if len(numbers) == 1 else "s", n=which),
            "keep": LINK_KEEP_LABEL}


def _with_link_check(messages: list, phase: str, pending: Optional[dict], prior: dict[str, Any],
                     raised: bool) -> None:
    """R-H: on the turn the SIPOC's link check is raised, its flagged steps and two buttons on the reply. In place."""
    check = _link_check(phase, pending, prior) if raised else None
    last = next((m for m in reversed(messages) if isinstance(m, AIMessage)), None)
    if check is not None and last is not None:
        last.additional_kwargs[LINK_CHECK_KEY] = check


def _with_teaching_card(messages: list, teaching: Optional[dict], strip: Optional[dict]) -> Optional[dict]:
    """R-C (ADR-0114 decision 1, part 2): the card on the reply — the last AI message — and the strip the turn shows:
    none beside a card, whose saved note replaces it. Mutates `messages` in place."""
    if teaching is None:
        return strip
    next(m for m in reversed(messages) if isinstance(m, AIMessage)).additional_kwargs[TEACHING_CARD_KEY] = teaching
    return None


#: DEF-220 (G-221) — words that present a sample: the coach writes none of its own (G-170's is the script's,
#: inserted by code).
_SAMPLE_INTRO = re.compile(r"(?<![a-z])(for example|for instance|e\.g\.|an example|example:|illustration|"
                           r"let me show|a good (?:answer|goal|statement) (?:looks|might look|could look|would look))"
                           r"(?![a-z])", re.I)


def _lead_in_only(phase: str, plan: Optional[CoachingPlan], reply: CoachingResponse, opening: bool,
                  belt: str = "") -> CoachingResponse:
    """DEF-220 (G-221): on a teaching move whose explanation
    block is shown, the coach's own STATEMENTS are one lead-in sentence — the first that names the element in focus,
    else the first that presents no sample. The explanation lives once, in its block (WHY IT MATTERS); the sample is
    the script's, so a sentence presenting one of the coach's own goes. Kept whole: a question (G-171 owns repeats of
    the ask), a list item, and a sentence holding the Belt's own words (G-185). The phase's opening turn (the welcome)
    is left whole, and so is a message with no lead-in. Returns a COPY, or `reply`."""
    if (opening or plan is None or plan.move not in TEACHING_MOVES or not plan.focus_field
            or not str(reply.explanation or "").strip()):
        return reply
    from backend.core import guard_messages
    name = {w for w in re.findall(r"[a-z]+", guard_messages.element_name(phase, plan.focus_field).lower()) if len(w) > 3}
    own = _plain(belt)

    def kept_whole(sentence: str) -> bool:
        p = _plain(sentence)
        return sentence.rstrip().endswith("?") or (bool(own) and len(p) > 15 and p in own)

    def sample(sentence: str) -> bool:
        return bool(_SAMPLE_INTRO.search(sentence)) or sentence.lstrip().startswith(('"', "“", ">"))
    lines = str(reply.message or "").split(chr(10))
    statements = [s for line in lines if not _LIST_ITEM.match(line)
                  for s in _SENTENCE_END.split(line) if s.strip() and not kept_whole(s)]
    plain = [s for s in statements if not sample(s) and not s.rstrip().endswith(":")]
    lead = next((s for s in plain if name & set(re.findall(r"[a-z]+", s.lower()))), plain[0] if plain else "")
    if not lead:
        return reply
    out: list[str] = []
    for line in lines:
        if _LIST_ITEM.match(line):
            out.append(line)
            continue
        out.append(" ".join(s for s in _SENTENCE_END.split(line) if s == lead or kept_whole(s)).strip())
    message = re.sub(r"\n{3,}", chr(10) * 2, chr(10).join(out)).strip()
    if message == str(reply.message or "").strip():
        return reply
    logger.info("%s.executor: DEF-220 — the coach's own statements on `%s` cut to the lead-in", phase, plan.focus_field)
    return reply.model_copy(update={"message": message})


#: ADR-0074 — a criterion's page reference in the method book ("(p. 49)") is the coach's, not the Belt's.
_BOOK_PAGE = re.compile(r"\s*\(p\.[^)]*\)")


def upload_check_text(phase: str, upload: Optional[dict], focus: Optional[str]) -> str:
    """ADR-0074 (DEF-108, W5): the file part of an upload turn's reply, written in code from the
    upload's `element_check` — the file named, what it shows for the element (with where in the
    file), what conflicts and what is still missing, and the ask for it. When the element has moved
    on since the file arrived, it says which element the file was checked against (point 4). With no
    check (a fallback interpretation, a phase without criteria, a record from before schema 4):
    the file named and its interpretation."""
    if not upload or not upload.get("filename"):
        return ""
    from backend.core import guard_messages
    from backend.core import prompts as P
    from backend.middleware.skills import acceptance_criteria
    name = str(upload["filename"])
    check = upload.get("element_check") or None
    if not check:
        return P.UPLOAD_READ_NOTE.format(filename=name,
                                         summary=" ".join(str(upload.get("summary") or "").split())[:400]).strip()
    field = str(check.get("element") or "")
    element = guard_messages.element_name(phase, field)
    texts = {cid: _BOOK_PAGE.sub("", text).strip() for cid, text in acceptance_criteria(phase, field)}

    def items(result: str) -> list[str]:
        return [texts.get(c["criterion"], c["criterion"]) + (f" ({c['where']})" if c.get("where") else "")
                for c in check.get("criteria") or [] if c.get("result") == result]
    parts = [P.UPLOAD_CHECK_HEAD.format(filename=name)]
    if focus and field != focus:
        parts.append(P.UPLOAD_CHECK_EARLIER.format(element=element))
    shows, conflicts = items("supported"), items("contradicted")
    missing = items("not_covered") + [str(m) for m in check.get("missing") or [] if str(m).strip()]
    if shows:
        parts.append(P.UPLOAD_CHECK_SHOWS.format(element=element, items="; ".join(shows)))
    if conflicts:
        parts.append(P.UPLOAD_CHECK_CONFLICTS.format(items="; ".join(conflicts)))
    parts.append(P.UPLOAD_CHECK_MISSING.format(items="; ".join(dict.fromkeys(missing))) if missing
                 else P.UPLOAD_CHECK_COMPLETE.format(element=element))
    return " ".join(parts)


def _with_upload_check(phase: str, reply: CoachingResponse, upload: Optional[dict],
                       focus: Optional[str]) -> CoachingResponse:
    """ADR-0074 point 2: on an upload turn the file part goes ahead of the coach's `message`,
    written in code — the coach is not responsible for it. Returns a COPY, or `reply`."""
    text = upload_check_text(phase, upload, focus)
    if not text:
        return reply
    return reply.model_copy(update={"message": f"{text}\n\n{reply.message or ''}".strip()})


#: G-117 — a sentence that says a value was stored. A negated or conditional one ("nothing is
#: stored until you confirm") is not a claim and stays.
_STORE_CLAIM = re.compile(r"(?<![A-Za-z])(recorded|stored|saved|logged)(?![A-Za-z])"
                          # G-136: "has been successfully captured" — the passive only;
                          # "here is what I've captured" opens every read-back and is no claim.
                          r"|(?<![A-Za-z])(has|have|is|are|was|were)\s+(now\s+)?(been\s+)?(successfully\s+)?captured(?![A-Za-z])",
                          re.I)
_NOT_A_CLAIM = re.compile(r"(?<![A-Za-z])(not|nothing|until|only if|unless|once you|when you|before)(?![A-Za-z])", re.I)
_SENTENCE_END = re.compile(r"(?<=[.!?])[ \t]+")


def _plain(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9£€%]+", text.lower()))


def _belts_own(sentence: str, belt: str) -> bool:
    """G-185: every store word in the sentence stands among the Belt's own words — the same word with up to
    three words either side, as the Belt wrote them ('…of being logged within…' read back is no claim)."""
    words = _plain(sentence).split()
    hits = [i for i, w in enumerate(words) if _STORE_CLAIM.fullmatch(w) or w == "captured"]
    return bool(belt) and bool(hits) and all(
        " ".join(words[max(0, i - 3):i + 4]) in belt for i in hits)


def _without_store_claims(text: str, belt: str = "") -> str:
    """The text with every sentence that claims a store removed, line by line — never a sentence that
    repeats the Belt's own words (G-185; `belt` is everything the Belt wrote)."""
    own = _plain(belt)
    lines = []
    for line in text.split(chr(10)):
        kept = [x for x in _SENTENCE_END.split(line)
                if not (_STORE_CLAIM.search(x) and not _NOT_A_CLAIM.search(x) and not _belts_own(x, own))]
        lines.append(" ".join(kept))
    return chr(10).join(lines).strip()


#: G-171 — a part of the message that repeats the example or the question
#: block: this share of its words or more come from the block.
REPEAT_SHARE = 0.6
_WORD = re.compile(r"[a-z0-9£€%]+")
_LIST_ITEM = re.compile(r"\s*(?:[-*•]|\d+[.)])\s")


def _block_words(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if len(w) > 2}


def _repeats(part: str, block: set[str]) -> bool:
    words = _block_words(part)
    return bool(words) and bool(block) and len(words & block) / len(words) >= REPEAT_SHARE


def _without_repeated_blocks(text: str, example: str, prompt: str, explanation: str = "",
                             whole: bool = True, belt: str = "") -> str:
    """G-171: the message with every paragraph that repeats the example or the explanation block, and every
    question that repeats the question block, removed — the screen shows the blocks under the message. A
    paragraph that loses half its sentences or more goes whole (it was mostly a repeat), and a lead-in line
    ending in ':' goes with what it introduced. When that leaves nothing, only the repeated sentences go;
    `text` comes back unchanged only when even that leaves nothing. G-185: a list item or a paragraph that
    holds the Belt's own words (`belt`) never goes whole — only its repeated question does."""
    ex, ask, why = _block_words(example), _block_words(prompt), _block_words(explanation)
    own, asked = _plain(belt), _plain(prompt)

    def repeats_ask(s: str) -> bool:
        # G-247: the question block's own sentence, written as a request ("Tell me …"), is a repeat too.
        p = _plain(s)
        return (s.rstrip().endswith("?") and _repeats(s, ask)) or (len(p) > 15 and p in asked)

    def belts(lines: list[str]) -> bool:
        return bool(own) and any(len(p) > 15 and p in own
                                 for p in (_plain(_LIST_ITEM.sub("", s, count=1)) for line in lines
                                           for s in _SENTENCE_END.split(line)))
    paragraphs = re.split(r"\n\s*\n", text.strip())
    kept: list[str] = []
    for para in paragraphs:
        before = [s for line in para.split(chr(10)) for s in _SENTENCE_END.split(line) if s.strip()]
        # A list item and the lines under it are one unit: a repeated question takes its item with it.
        items: list[list[str]] = []
        for line in para.split(chr(10)):
            if not items or _LIST_ITEM.match(line) or not _LIST_ITEM.match(items[-1][0]):
                items.append([line])
            else:
                items[-1].append(line)
        lines = []
        for item in items:
            if _LIST_ITEM.match(item[0]) and not belts(item) and any(
                    repeats_ask(s) for s in _SENTENCE_END.split(" ".join(item))):
                continue
            for line in item:
                sentences = [s for s in _SENTENCE_END.split(line) if not repeats_ask(s)]
                if sentences or not line.strip():
                    lines.append(" ".join(sentences))
                elif lines and lines[-1].rstrip().endswith(":"):
                    lines.pop()
        after = [s for line in lines for s in _SENTENCE_END.split(line) if s.strip()]
        if not belts(before) and (_repeats(para, ex) or _repeats(para, why)
                                  or (whole and before and len(after) * 2 <= len(before))):
            if kept and kept[-1].rstrip().endswith(":"):
                kept.pop()
            continue
        para = chr(10).join(lines).strip()
        if para:
            kept.append(para)
    if kept and kept[-1].rstrip().endswith(":"):
        kept.pop()
    out = (chr(10) * 2).join(kept).strip()
    if not out and whole:
        # Everything was a repeat: keep what the sentences alone leave, never an empty message.
        return _without_repeated_blocks(text, example, prompt, explanation, whole=False, belt=belt)
    return out or text


#: DEF-019 — a link in the coach's words: a markdown link keeps its words, a bare address goes.
_MD_LINK = re.compile(r"\[([^\]]+)\]\((?:https?://|www\.)[^)]*\)")
_BARE_LINK = re.compile(r"\(?(?:https?://|www\.)[^\s)>\]]+\)?")


def _without_links(text: str) -> str:
    """DEF-019: the coach teaches in its own voice and never hands the Belt a URL — decided in
    code, so no prompt has to be obeyed for it. A removal is logged as a FINDING."""
    out = _BARE_LINK.sub("", _MD_LINK.sub(r"\1", text))
    if out != text:
        logger.warning("executor: FINDING — DEF-019: a link in the coach's reply was removed")
        out = re.sub(r"[ \t]{2,}", " ", out).replace(" .", ".").strip()
    return out


def _missing_words(phase: str, missing: list[str], artifacts: dict[str, Any],
                   pending: dict[str, Any]) -> str:
    """G-163 — what a read-back still lacks, in the Belt's words: a number with its unit for a baseline
    or target, the SIPOC's missing columns, otherwise the part's own name."""
    from backend.phases.define.parse import METRIC_FIELDS, missing_columns, missing_parts
    store = {**artifacts, **(pending.get("store") or {})}        # read-back = Gate (founder 2026-10-28)
    parts = []
    for f in missing:
        if missing_parts(f, (pending.get("store") or {}).get(f)):
            parts.extend(missing_parts(f, (pending.get("store") or {}).get(f)))      # ADR-0088 decision 6
        elif f in METRIC_FIELDS:
            parts.append(f"a number with its unit for the {f.replace('_', ' ')}")
        elif f == "process_map_sipoc" and isinstance(sipoc := (pending.get("store") or {}).get(f, store.get(f)), dict) \
                and missing_columns(sipoc):
            # G-332 (DEF-259): the columns of what a Confirm would store — never of the coach's capture, which held
            # Outputs the Belt never gave ("still needs the  columns").
            cols = [c.replace("_", " ") for c in missing_columns(sipoc)]
            named = " and ".join([", ".join(cols[:-1]), cols[-1]] if len(cols) > 1 else cols)
            parts.append(f"the {named} column{'s' if len(cols) != 1 else ''} of the process map")
        elif phase == "define" and f == pending.get("field") and _open_rows(f, store, pending):
            parts.extend(_open_rows(f, store, pending))                                  # ADR-0093 decision 2
        else:
            parts.append(f"the {guard_messages.element_name(phase, f).lower() if f == pending.get('field') else f.replace('_', ' ')}")
    return " and ".join(parts)


def _open_rows(field: str, values: dict[str, Any], pending: dict[str, Any]) -> list[str]:
    """ADR-0093: the element's required criteria still open, by their labels — what a refused Confirm names. A
    read-back made again after a refused Confirm carries the refused value under `earlier`."""
    from backend.phases.define import templates
    if field not in templates.TEMPLATES:
        return []
    values = {**{k: v for k, v in (pending.get("earlier") or {}).items()}, **values}
    return [r["label"].lower() for r in templates.rows(field, values, spans=pending.get("spans"))
            if r["required"] and not r["met"]]


def _store_truth(messages: list, reply: CoachingResponse | None, phase: str,
                 plan: Optional[CoachingPlan], stored: dict[str, Any], belt: str = "") -> list:
    """G-117 (DEF-156): the only sentence telling the Belt what was stored is written HERE, from
    the storage result, like the read-back. The coach model's own store claims are removed from
    the reply (message and explanation); then, when this turn stored a value, one line names the
    element; when the Belt confirmed a read-back that could not be stored (`moves.CONFIRM_INCOMPLETE`),
    one line says nothing was stored and what was missing. The Belt's text reads `messages`'
    last AI message, so that message is rebuilt with plain-string content (a NEW message)."""
    if plan is None:
        return messages
    note = ""
    # DEF-290 (W3 amendment, founder 2026-10-29): a Define Confirm's stored values are named by the saved note on the
    # card or beside the reply (`_element_card`), never by a "Stored: X." line.
    if stored and plan.stored_field and not (phase == "define" and plan.stored_field in DEFINE_FIELD_ORDER):
        note = STORE_NOTE_STORED.format(elements=guard_messages.element_name(phase, plan.stored_field))
    elif plan.move in (moves.READ_BACK, moves.CHALLENGE) and (plan.reason or "").startswith(moves.CONFIRM_INCOMPLETE[:40]):
        missing = re.findall(r"`(\w+)`", plan.reason.split(".")[0] + ".")
        note = STORE_NOTE_NOT_STORED.format(
            element=guard_messages.element_name(phase, plan.focus_field or ""),
            missing=" and ".join("the " + f.replace("_", " ") for f in missing) or "every field")
    if reply is not None:
        reply.explanation = _without_links(_without_store_claims(str(reply.explanation or ""), belt))
        reply.example = _without_links(str(reply.example or ""))           # DEF-019
        reply.prompt = _without_links(str(reply.prompt or ""))
    for i in range(len(messages) - 1, -1, -1):
        msg = messages[i]
        if isinstance(msg, AIMessage) and guard.NODE in (msg.additional_kwargs or {}):
            # Written in code and marked (T92's refusal, T34's level 4 — ADR-0082): its "progress is
            # saved" is the system's statement, not a model's store claim.
            return messages
        if isinstance(msg, AIMessage) and msg.text.strip():
            body = _without_links(_without_store_claims(msg.text, belt))
            text = f"{note}{chr(10) * 2}{body}".strip() if note else body
            if text == msg.text:
                return messages
            if reply is not None:
                reply.message = text
            out = list(messages)
            out[i] = AIMessage(content=text, additional_kwargs=dict(msg.additional_kwargs or {}),
                               id=msg.id, name=msg.name)
            return out
    return messages


def _limit_diagnosis(turn: list, coach_limit: int) -> dict[str, Any]:
    """G-139 — the coach's output on a turn the call limit ended: each of its model responses (raw
    text, the tools it asked for with their arguments, invalid tool calls, the finish reason), each
    tool result sent back to it, and WHY the loop wanted another call. No model call."""
    responses: list[dict[str, Any]] = []
    tool_results: list[dict[str, Any]] = []
    for m in turn:
        if isinstance(m, AIMessage):
            if _LIMIT_NOTICE in str(m.content):
                continue
            responses.append({
                "text": m.text[:1500],
                "tool_calls": [{"name": c.get("name"), "args": json.dumps(c.get("args"), default=str)[:800]}
                               for c in (m.tool_calls or [])],
                "invalid_tool_calls": [{"name": c.get("name"), "error": str(c.get("error") or "")[:400],
                                        "args": str(c.get("args") or "")[:400]}
                                       for c in (getattr(m, "invalid_tool_calls", None) or [])],
                "finish_reason": (m.response_metadata or {}).get("finish_reason"),
            })
        elif isinstance(m, ToolMessage):
            tool_results.append({"name": m.name, "status": getattr(m, "status", None),
                                 "content": str(m.content)[:800]})
    last = responses[-1] if responses else {}
    if last.get("finish_reason") == "length":
        why = "the coach's response was cut off at its token limit before the structured reply (G-153)"
    elif last.get("tool_calls"):
        names = ", ".join(str(c["name"]) for c in last["tool_calls"])
        errs = [t for t in tool_results if t.get("status") == "error"]
        why = (f"the coach's last response asked for tool(s) {names}"
               + (f"; the tool result was an error ({errs[-1]['content'][:200]})" if errs else "")
               + " — the loop needed another call to write the reply")
    elif last.get("invalid_tool_calls"):
        why = "the coach's last response carried an invalid tool call — the loop asked again"
    elif responses:
        why = "the coach's last response was text with no structured reply — the loop asked again"
    else:
        why = "no coach response was recorded before the limit"
    return {"coach_limit": coach_limit, "responses": responses, "tool_results": tool_results, "why": why}


def _r18_link(phase: str, field: Optional[str], store: dict[str, Any],
              prior: dict[str, Any]) -> Optional[str]:
    """ADR-0078 point 5 (R18, DEF-085): the read-back of the SIPOC against the confirmed problem
    statement, or of the problem statement against the confirmed SIPOC — both directions, in code.
    The mismatch in words, or None when they agree or the other element is not confirmed yet."""
    pair = _r18_pair(phase, field, store, prior)
    if pair is None:
        return None
    from backend.core.prompts import (LINK_END_AMBIGUOUS, LINK_END_UNMATCHED, LINK_IGNORED, LINK_QUIET,
                                      LINK_UNMATCHED)
    from backend.phases.define import parse
    sipoc, fivew = pair
    gap = parse.link_mismatch(fivew.get("steps"), sipoc)
    # DEF-211 (ADR-0078): an end of a "from → to" location found nowhere, or at more than one
    # step, is asked about first.
    parts = [(LINK_END_AMBIGUOUS.format(verb=e["end"], name=e["name"], steps=" or ".join(f"“{n}”" for n in e["found"]))
              if e["found"] else LINK_END_UNMATCHED.format(verb=e["end"], name=e["name"])) for e in gap["ends"]]
    parts += [t.format(names=", ".join(f"“{n}”" for n in gap[k]))
              for k, t in (("unmatched", LINK_UNMATCHED), ("quiet", LINK_QUIET), ("ignored", LINK_IGNORED))
              if gap[k]]
    return " ".join(parts) or None


def _r18_pair(phase: str, field: Optional[str], store: dict[str, Any],
              prior: dict[str, Any]) -> Optional[tuple[dict[str, Any], dict[str, Any]]]:
    """(the SIPOC, the 5W2H) the R18 check compares on this read-back — the element read back against the other
    one confirmed — or None when there is no pair."""
    if phase != "define":
        return None
    if field == "process_map_sipoc" and isinstance(store.get("process_map_sipoc"), dict) \
            and isinstance(store.get("problem_5w2h") or prior.get("problem_5w2h"), dict):
        # R-H: a read-back carrying steps the Belt added to the problem statement is checked against them.
        return store["process_map_sipoc"], store.get("problem_5w2h") or prior["problem_5w2h"]
    if field == "problem_statement" and isinstance(store.get("problem_5w2h"), dict) \
            and isinstance(prior.get("process_map_sipoc"), dict):
        return prior["process_map_sipoc"], store["problem_5w2h"]
    return None


def _r18_located(phase: str, field: Optional[str], store: dict[str, Any],
                 prior: dict[str, Any]) -> Optional[str]:
    """DEF-211 (ADR-0078): a "from → to" location whose two ends are found — the
    steps between them read back in code ("The problem occurs in steps 3–4: is that right?"), for the read-back's
    one Confirm; None otherwise."""
    pair = _r18_pair(phase, field, store, prior)
    if pair is None:
        return None
    from backend.core.prompts import LINK_LOCATED, LINK_LOCATED_ONE
    from backend.phases.define import parse
    sipoc, fivew = pair
    where = parse.located_steps(fivew.get("steps"), sipoc)
    if not where["range"] or not where["located"]:
        return None
    ids = [s["id"] for s in parse.process_steps(sipoc.get("process_steps"))]
    numbers = [ids.index(i) + 1 for i in where["located"]]
    first, last = numbers[0], numbers[-1]
    return (LINK_LOCATED if last > first else LINK_LOCATED_ONE).format(first=first, last=last)


def _with_text(messages: list, text: str) -> list:
    """The messages with the last AI message's text replaced — a NEW message, its extras kept."""
    for i in range(len(messages) - 1, -1, -1):
        msg = messages[i]
        if isinstance(msg, AIMessage):
            out = list(messages)
            out[i] = AIMessage(content=text, additional_kwargs=dict(msg.additional_kwargs or {}),
                               id=msg.id, name=msg.name)
            return out
    return messages


def _with_carried(messages: list, reply: CoachingResponse | None, phase: str,
                  carried: dict[str, Any]) -> list:
    """G-118 (DEF-157): the parts of the element carried from an earlier read-back are shown to
    the Belt under this one, in code, so what a Confirm stores is what the Belt saw."""
    if not carried:
        return messages
    from backend.phases.define.templates import plain        # G-260
    lines = chr(10).join(READ_BACK_CARRIED.format(name=f.replace("_", " "), value=plain(v))
                         for f, v in carried.items())
    for i in range(len(messages) - 1, -1, -1):
        msg = messages[i]
        if isinstance(msg, AIMessage) and msg.text.strip():
            text = f"{msg.text.rstrip()}{chr(10) * 2}{lines}"
            if reply is not None:
                reply.message = text
            out = list(messages)
            out[i] = AIMessage(content=text, additional_kwargs=dict(msg.additional_kwargs or {}),
                               id=msg.id, name=msg.name)
            return out
    return messages


def _with_metric_reading(messages: list, reply: CoachingResponse | None, store: dict[str, Any]) -> list:
    """ADR-0071 (DEF-076): under a read-back of the baseline or the target, the number, unit and
    direction a Confirm will store — written HERE from the MetricValue, never by the model, so the
    Belt confirms what is stored."""
    from backend.phases.define.parse import METRIC_FIELDS, metric_text
    lines = chr(10).join(READ_BACK_METRIC.format(name=guard_messages.element_name("define", f),
                                                 value=metric_text(store[f]))
                         for f in METRIC_FIELDS if isinstance(store.get(f), dict))
    if not lines:
        return messages
    for i in range(len(messages) - 1, -1, -1):
        msg = messages[i]
        if isinstance(msg, AIMessage) and msg.text.strip():
            text = f"{msg.text.rstrip()}{chr(10) * 2}{lines}"
            if reply is not None:
                reply.message = text
            out = list(messages)
            out[i] = AIMessage(content=text, additional_kwargs=dict(msg.additional_kwargs or {}),
                               id=msg.id, name=msg.name)
            return out
    return messages


def _metric_meaning(store: dict[str, Any]) -> Optional[str]:
    """DEF-018 — the line under position 5's read-back, from the primary metric's registry entry the
    Belt gave (`metric_definitions[0]`), or None when it carries no meaning."""
    from backend.core.prompts import METRIC_MEANING_LINE, METRIC_READING
    reg = store.get("metric_definitions")
    first = reg[0] if isinstance(reg, list) and reg and isinstance(reg[0], dict) else {}
    meaning = str(first.get("meaning") or "").strip()
    if not meaning:
        return None
    unit = str(first.get("unit") or "").strip()
    reading = METRIC_READING["%" if "%" in unit or "percent" in unit.lower() else ""]
    return METRIC_MEANING_LINE.format(name=str(first.get("name") or "the primary metric").replace("_", " "),
                                      unit=unit or "no unit given",
                                      meaning=meaning.rstrip(".") + ".", reading=reading)


def _with_code_line(messages: list, reply: CoachingResponse | None, line: str) -> list:
    """The last AI message with one line written in code after it — a NEW message."""
    for i in range(len(messages) - 1, -1, -1):
        msg = messages[i]
        if isinstance(msg, AIMessage) and msg.text.strip():
            text = f"{msg.text.rstrip()}{chr(10) * 2}{line}"
            if reply is not None:
                reply.message = text
            out = list(messages)
            out[i] = AIMessage(content=text, additional_kwargs=dict(msg.additional_kwargs or {}),
                               id=msg.id, name=msg.name)
            return out
    return messages


def turn_type_of(plan: Optional[CoachingPlan], state: PhaseState) -> str:
    """ADR-0069's turn type, in code: an unread upload bound to an open ask makes an upload turn;
    teaching a field (teach, or store and advance to the next) a teaching turn; anything else — the
    Belt answered — an answer turn."""
    if _unread_upload(state) is not None:
        return turn_tools.UPLOAD
    if plan is None or plan.move in (moves.TEACH, moves.STORE_AND_ADVANCE):
        return turn_tools.TEACHING
    return turn_tools.ANSWER


#: The text `ModelCallLimitMiddleware` ends a run with (langchain 1.3.16), matched to replace it.
_LIMIT_NOTICE = "Model call limits exceeded"


#: The question a Change click is answered with (R4).
CHANGE_QUESTION = "What would you like to change?"


def goal_read_back(plan: Optional[CoachingPlan]) -> Optional[dict[str, Any]]:
    """The read-back a store turn ends with for the NEXT position — its pending record, or None:
    ADR-0086, the target the confirmed goal states (`moves.from_goal`); DEF-098 (R15), a value an earlier
    answer gave for it (`moves.from_offer`). Both decided in the planner."""
    if plan is None or plan.move != moves.STORE_AND_ADVANCE or not plan.focus_field:
        return None
    pending = ((plan.field_status or {}).get(plan.focus_field) or {}).get("pending") or {}
    return pending if pending.get("from_goal") or pending.get("from_offer") else None


def _offer_reply(phase: str, plan: Optional[CoachingPlan]) -> Optional[CoachingResponse]:
    """DEF-098 (R15): after a Confirm, the next element read back IN CODE from what an earlier answer gave for
    it — the element, the value as it was given, and the one question. No model call; nothing is stored until
    the Belt confirms (ADR-0002)."""
    pending = goal_read_back(plan)
    if pending is None or not pending.get("from_offer"):
        return None
    from backend.core import prompts as P
    field = str(pending.get("field") or "")
    value = (pending.get("proposed") or {}).get(field)
    from backend.phases.define.templates import plain        # G-260: never a MetricValue as JSON
    shown = str(pending.get("belt_words") or "") or plain(value)
    head = P.OFFER_HEAD.format(element=guard_messages.element_name(phase, field))
    return CoachingResponse(message=head + chr(10) + f"“{shown}”" + chr(10) * 2 + P.OFFER_ASK, prompt=P.OFFER_ASK)


def _goal_target_reply(phase: str, plan: Optional[CoachingPlan]) -> Optional[CoachingResponse]:
    """ADR-0086: after the goal's Confirm, the target it states read back IN CODE for one Confirm —
    the value and the date, or the one the goal gives (the other is taught next). No model call."""
    pending = goal_read_back(plan)
    if pending is None or phase != "define" or not pending.get("from_goal"):
        return None
    from backend.core import prompts as P
    from backend.phases.define import parse
    store = dict(pending.get("store") or {})
    lines = [P.GOAL_TARGET_HEAD]
    if "target_value" in store:
        lines.append(f"- {guard_messages.element_name(phase, 'target_value')}: {parse.metric_text(store['target_value'])}")
    if "target_date" in store:
        shown = parse.date_shown(store["target_date"], pending.get("belt_words"))   # ADR-0088 decision 5
        lines.append(f"- {guard_messages.element_name(phase, 'target_date')}: {shown}")
    if "target_value" in store and "target_date" not in store:
        lines.append(P.GOAL_TARGET_NEXT)
    return CoachingResponse(message=chr(10).join(lines) + chr(10) * 2 + P.GOAL_TARGET_ASK,
                            prompt=P.GOAL_TARGET_ASK)


def _change_reply(plan: Optional[CoachingPlan]) -> Optional[CoachingResponse]:
    """R4's Change click, answered IN CODE: the Belt's exact current words, then
    the one question. No model call, so the Belt's words are always there.
    `None` for every other move."""
    if plan is None or plan.move != moves.CHALLENGE or plan.reason != moves.CHANGE_REASON:
        return None
    words = str((plan.pending or {}).get("belt_words") or plan.answer or "").strip()
    return CoachingResponse(message=words + chr(10) * 2 + CHANGE_QUESTION,
                            prompt=CHANGE_QUESTION)


#: G-173 (ADR-0077) — a number as it is written: digits with thousands
#: commas, a decimal part, and a k or m multiplier; a digit inside a word ("5W2H", "Q2") is not one.
_NUMBER = re.compile(r"(?<![A-Za-z0-9.,])(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?\s?([kKmM])?(?![A-Za-z0-9])")


def _number_values(text: str) -> list[tuple[str, set[float]]]:
    """Each number in `text`: its spelling and the values it may stand for (with its multiplier, without)."""
    out = []
    for m in _NUMBER.finditer(text or ""):
        base = float(m.group(1).replace(",", "") + ("." + m.group(2) if m.group(2) else ""))
        scale = {"k": 1e3, "m": 1e6}.get((m.group(3) or "").lower(), 1.0)
        out.append((m.group(0).strip(), {round(base, 6), round(base * scale, 6)}))
    return out


def _number_sources(phase: str, state: PhaseState, produced: list) -> set[float]:
    """G-173: every value a number in the coach's words may come from — the Belt's messages, the case's
    confirmed values and computation results, the phase script, this turn's tool results, and the step
    numbers. A percentage and its fraction are the same value (DEF-016's one convention)."""
    from backend.middleware.skills import instructions
    texts: list[str] = [str(m.text) for m in (state.get("messages") or []) if isinstance(m, HumanMessage)]
    texts.append(json.dumps(state.get("artifacts") or {}, default=str, ensure_ascii=False))
    texts.append(str(state.get("phase_context") or ""))
    texts.append(instructions(phase))
    # A lookup's result is a source; the structured reply's own echo (ToolStrategy's "Returning structured
    # response: …" tool message) is the coach's words, never their source.
    texts += [str(m.content) for m in produced if isinstance(m, ToolMessage)
              and not str(m.content).startswith("Returning structured response")]
    values: set[float] = {float(n) for n in range(0, len(moves.positions(phase)) + 1)}
    for text in texts:
        for _, vals in _number_values(text):
            for v in vals:
                values |= {v, round(v * 100, 6), round(v / 100, 6)}
                # A source rounded for reading ("about £68,000" for a computed 68,040) is still that source.
                if abs(v) >= 10:
                    values |= {float(f"{v:.{sig}g}") for sig in (1, 2, 3)}
    return values


def _unsourced_numbers(reply: CoachingResponse, sources: set[float]) -> list[str]:
    """G-173: the numbers in the coach's words (message and blocks) that no source holds — numbers the
    coach calculated or invented. ADR-0077: calculations run in code."""
    text = chr(10).join(str(getattr(reply, k, "") or "") for k in ("message", "explanation", "example", "prompt"))
    return [spelled for spelled, vals in _number_values(text) if not vals & sources]


#: G-173 — a list item's marker; the space between two sentences; a line
#: that introduces what follows it (a lead-in ending in a colon, a heading, a bold label).
_LIST_MARKER = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")
_SENTENCE_GAP = re.compile(r"(?<=[.!?])[\"”’)]*\s+(?=[\"“‘(]?[A-Z0-9£€$])")
_INTRODUCES = re.compile(r":\s*$|^\s*#{1,6}\s|^\s*\*\*[^*]+\*\*:?\s*$")


def _trim_block(text: str, sources: set[float]) -> tuple[str, list[str]]:
    """G-173 — `text` without its sentences holding a number no source gives. A list item left with no
    sentence goes whole, and so does a lead-in or heading whose lines underneath all went — never a
    dangling list or half a sentence. Returns the text kept and the sentences left out."""
    removed: list[str] = []
    lines: list[Optional[str]] = []                       # None: a line that went whole
    for line in (text or "").split("\n"):
        marker = _LIST_MARKER.match(line)
        prefix = marker.group(0) if marker else ""
        sentences = [s for s in _SENTENCE_GAP.split(line[len(prefix):]) if s.strip()]
        kept = [s for s in sentences if all(vals & sources for _, vals in _number_values(s))]
        if len(kept) == len(sentences):
            lines.append(line)
            continue
        removed += [s.strip() for s in sentences if s not in kept]
        lines.append(prefix + " ".join(s.strip() for s in kept) if kept else None)
    out: list[str] = []
    for i, left in enumerate(lines):
        if left is None:
            continue
        if left.strip() and _INTRODUCES.search(left):
            j = i + 1
            while j < len(lines) and lines[j] is not None and not str(lines[j]).strip():
                j += 1                                    # the blank lines after a lead-in
            block = []
            while j < len(lines) and (lines[j] is None or str(lines[j]).strip()):
                block.append(lines[j])
                j += 1
            if block and all(b is None for b in block):
                removed.append(left.strip())
                continue
        out.append(left)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip(), removed


def _without_unsourced(reply: CoachingResponse, sources: set[float]) -> tuple[Optional[CoachingResponse], list[str]]:
    """G-173: the coach's reply with only its sentences holding a number
    no source gives left out, every block, and one line in code saying so (before the closing question).
    None when too little remains — fewer than eight words or no whole sentence in the message, or the
    question block emptied — and the move's reply is written in code instead."""
    update: dict[str, str] = {}
    removed: list[str] = []
    for key in ("message", "explanation", "example", "prompt"):
        text = str(getattr(reply, key, "") or "")
        kept, went = _trim_block(text, sources)
        if went:
            update[key], removed = kept, removed + went
    from backend.core.prompts import NUMBERS_LEFT_OUT
    message = update.get("message", str(reply.message or ""))
    whole = re.search(r"[A-Za-z][^.!?]*[.!?]", message)
    if (not whole or len(re.findall(r"[A-Za-z']+", message)) < 8
            or (str(reply.prompt or "").strip() and "prompt" in update and not update["prompt"])):
        return None, removed
    paragraphs = message.split("\n\n")
    if len(paragraphs) > 1 and paragraphs[-1].rstrip().endswith("?"):
        message = "\n\n".join([*paragraphs[:-1], NUMBERS_LEFT_OUT, paragraphs[-1]])
    else:
        message = f"{message}\n\n{NUMBERS_LEFT_OUT}"
    return reply.model_copy(update={**update, "message": message}), removed


#: G-174 — a part of a value that is not filled in: a bracketed
#: placeholder, "TBD", "to be confirmed", or the coach's own note that a part still needs something.
_PLACEHOLDER = re.compile(r"\[[^\]\n]{3,80}\]|\b(TBD|TBC|to be (confirmed|defined|determined|decided|agreed))\b|"
                          r"\(\s*needs?\b[^)]{0,80}\)|\?\?+|\bX{2,}\b", re.I)


def _need_the_belt_stated(note: str, belt_words: str) -> bool:
    """G-272: a "(needs …)" note whose words are the Belt's own — at least two, three in four of them in the Belt's
    words for the element — is the Belt's content ("Dev needs a half-day of training"), not a part left unfilled."""
    words = [w for w in re.findall(r"[a-z]{4,}", note.lower()) if w not in ("need", "needs")]
    said = set(re.findall(r"[a-z]{4,}", belt_words.lower()))
    found = [w for w in words if w in said]
    return len(found) >= 2 and len(found) >= 0.75 * len(words)


def placeholders(store: dict[str, Any], belt_words: str = "") -> list[str]:
    """G-174: the placeholders in what a Confirm would store — an incomplete value is challenged, never
    read back for a Confirm. G-272: a bracketed "needs …" made of the Belt's own words is theirs, not a placeholder."""
    def leaves(value: Any) -> list[str]:
        if isinstance(value, dict):
            return [s for v in value.values() for s in leaves(v)]
        if isinstance(value, (list, tuple)):
            return [s for v in value for s in leaves(v)]
        return [value] if isinstance(value, str) else []
    found = [m.group(0) for text in leaves(list(store.values())) for m in _PLACEHOLDER.finditer(text)]
    return [p for p in found if not (p.startswith("(") and _need_the_belt_stated(p, belt_words))]


#: G-172 (DEF-020) — a question about where the project stands.
STATUS_QUESTION = re.compile(r"\b(where (do|are) we(\s+(stand|at|now))?|what('s| is| have we)?\s+(done|left|missing|"
                             r"still open|next)|how far (have we|are we)|(our|my) progress|progress so far|"
                             r"(project|our|my) status|status update)\b",
                             re.I)


def _status_reply(phase: str, state: PhaseState, plan: Optional[CoachingPlan]) -> Optional[CoachingResponse]:
    """G-172: "where do we stand?" answered IN CODE from the state, as the progress view reads it
    (`moves.element_rows`): the step, every element done, every element open (and parked), and the next
    one, then that element's question. Only on a respond move (the Belt asked rather than answered) whose
    message is a status question; `None` otherwise."""
    if plan is None or plan.move != moves.RESPOND:
        return None
    belt = next((m.text for m in reversed(list(state.get("messages") or [])) if isinstance(m, HumanMessage)), "")
    if not STATUS_QUESTION.search(belt):
        return None
    field_status = dict(plan.field_status or state.get("field_status") or {})
    rows = moves.element_rows(phase, dict(state.get("artifacts") or {}), field_status,
                              lambda f: guard_messages.element_name(phase, f))
    if not rows:
        return None
    done = [r["name"] for r in rows if r["status"] == "confirmed"]
    parked = [r["name"] for r in rows if r["status"] == "parked"]
    current = next((r for r in rows if r["status"] == "current"), None)
    still = [r["name"] for r in rows if r["status"] in ("current", "open")]
    lines = [f"You are in {phase.capitalize()}"
             + (f", step {current['n']} of {len(rows)}: {current['name']}." if current else ".")]
    lines.append(f"Done ({len(done)} of {len(rows)}): " + (", ".join(done) + "." if done else "none yet."))
    lines.append(f"Open ({len(still)}): " + (", ".join(still) + "." if still else "none — every element is confirmed."))
    if parked:
        lines.append(f"Parked ({len(parked)}): " + ", ".join(parked) + ".")
    if current:
        lines.append(f"Next: {current['name']}.")
    ask = _script_ask(phase, current["field"]) if current else ""
    return CoachingResponse(message=chr(10).join(lines) + (chr(10) * 2 + ask if ask else ""), prompt=ask)


def _conversation(messages: list) -> list:
    """The conversation as the coach is shown it (section 6 of its input): each
    Belt message, and each coach turn as ONE message carrying its reply text. A
    coach turn's tool-call stubs and the framework's "Returning structured
    response" message are dropped; a turn with no reply text (a timeout)
    contributes nothing. Built fresh — the stored messages are never edited
    (content is read through `.text`)."""
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

    *The structured response and the coaching text coexist* — the agent
    writes prose into `messages` AND returns the structured response. The two
    normally carry the same text. **When the terminal message has no text**, as
    happens when a provider puts everything in the structured payload, the
    Belt would otherwise get an empty turn, so `reply.message` is appended.
    """
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and str(msg.content).strip():
            return messages
    return [*messages, AIMessage(content=reply.message)]


#: The computation tools, by name. Derived from the registry rather than
#: typed, so a new tool is picked up here without a second list to remember.
_COMPUTATION_TOOL_NAMES: frozenset = frozenset(
    t.name for t in COMPUTATION_TOOLS
)


def _computation_results(
    messages: list, phase: str, turn: int,
) -> list[dict]:
    """The five-key rows for the computation tools THIS turn called.

    **The same inspection `_mark_consumed` does, over a different tool set.** A
    `@tool` receives only its arguments and cannot reach `PhaseState`, so the
    node inspects the turn's tool calls afterwards. Each tool returns the
    `result` sub-dict and the executor wraps it in the full
    `{"tool", "inputs", "result", "turn", "phase"}` shape — the turn and phase
    are not knowable inside the tool.

    **The record of what was computed is this list, never the coach's prose.**
    The gate document carries it, and the Define report and the coach's
    project-state block read the calculations from it. Against a list nothing
    wrote, a gate document would record that a project did no analysis
    whatever the Belt and the coach actually did.

    **The result is read as JSON, not parsed by hand.** LangChain serialises a
    `dict`-returning tool into the `ToolMessage`'s content as JSON — verified
    against the installed library rather than assumed:

        calculate_sigma_level -> '{"sigma_level": "3.76", "dpmo": "12000", …}'

    so `json.loads` recovers `Result` exactly (G-48: never hand-parse a
    structured payload). A tool whose content stops being JSON lands in the
    row as a `parse_error` rather than vanishing — **a computation that ran and
    could not be recorded is a finding, and dropping it silently would leave
    the record blind to it.**
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

    `field_index` walks the phase's ordered field list. **Define only**: only
    Define has an ordered `DEFINE_FIELD_ORDER`; Measure, Analyse, Improve and
    Control expose tier SETS, so no ordered sequence exists in code for them.
    Returning `None` for those four leaves `field_index` untouched rather than
    writing a number derived from an order nobody declared — **a number that
    looks walked and is not is worse than one that never moved**.

    The index is the first element NOT yet complete, so it names what to work
    on next; once every element is in, it rests on the LAST one rather than
    running off the end, because there is no next one to point at.

    **It is `define_position` minus one** — the position `define_progress`
    reports, so the index and the position cannot disagree. Position 5 waits
    for `metric_definitions` as well as `baseline_estimate`.
    """
    if phase != "define" or not DEFINE_FIELD_ORDER:
        return None
    return int(define_progress(artifacts)["position"]) - 1


def _attach_diagram(messages: list) -> None:
    """Lift this turn's `propose_diagram` payload onto the reply, for the UI.

    `gateway/routes.py` reads `sipoc_diagram` and `visualisation` off the
    reply's `additional_kwargs`, and this is what puts them there.
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


#: DEF-110 (W13): the tools whose results name a file a reply drew on — the retrieval tools' Documents
#: carry `source_file` and `page_number`; `read_upload` (ADR-0106) names the upload it read.
_SOURCE_TOOLS = frozenset({"rag_lookup_methodology", "rag_lookup_evidence", "rag_lookup_case_history"})


def _without_series_values(messages: list) -> list:
    """DEF-135 (T60): `load_evidence_series` results with the series values taken out of their artifact — a copy,
    so the tool's own result is untouched; the summary (n, mean, sigma, min, max) is kept."""
    out = []
    for m in messages:
        artifact = getattr(m, "artifact", None)
        if (isinstance(m, ToolMessage) and m.name == "load_evidence_series"
                and isinstance(artifact, dict) and "values" in artifact):
            m = m.model_copy(update={"artifact": {k: v for k, v in artifact.items() if k != "values"}})
        out.append(m)
    return out


def _attach_sources(messages: list) -> None:
    """DEF-110 (W13): put the files and pages this turn's tools returned on the reply, as `citations` —
    read in code from the ToolMessage artifacts, never from what the model says it cited. One per file
    and page, in the order the tools returned them; a failed read is left out. Mutates in place."""
    seen: dict[tuple[str, Any], dict] = {}
    for msg in messages:
        if not isinstance(msg, ToolMessage):
            continue
        artifact = getattr(msg, "artifact", None)
        if msg.name in _SOURCE_TOOLS and isinstance(artifact, list):
            for doc in artifact:
                meta = dict(getattr(doc, "metadata", None) or {})
                source = str(meta.get("source_file") or "")
                if source:
                    seen.setdefault((source, meta.get("page_number")), {
                        "agent_origin": "agent_improve", "index_name": str(msg.name),
                        "document_id": str(meta.get("id") or source), "relevance_summary": "",
                        "source_file": source, "page": meta.get("page_number")})
        elif msg.name == "read_upload" and isinstance(artifact, dict) and artifact.get("ok"):
            name = str(artifact.get("filename") or "")
            seen.setdefault((name, None), {
                "agent_origin": "agent_improve", "index_name": "read_upload",
                "document_id": str(artifact.get("blob_path") or name), "relevance_summary": "",
                "source_file": name, "page": None})
    if not seen:
        return
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            msg.additional_kwargs["citations"] = list(seen.values())
            return


def _off_ramp(phase: str, state: PhaseState) -> tuple[int, bool, int]:
    """Guard 1 of 2 of `executor`, the graceful off-ramp: the graph steps left, whether this turn coaches
    with no retrieval tools, and the turn's hop budget (0 on the off-ramp)."""
    # `remaining_steps` is a `RemainingSteps` managed value LangGraph fills in
    # on its own; declaring it on `PhaseState` is what activates it.
    # Low means the GRAPH is running out of room, so the coach is built with no
    # retrieval tools and answers from what is in hand rather than beginning a
    # hop chain it cannot finish. It coaches; it does not cap.
    #
    # `or 0` and not a `.get` default: an ABSENT field must fail this test, not
    # pass it — a default value would decide the guard instead of the graph.
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
    return remaining, off_ramp, hop_budget


def _turn_calculation(phase: str, state: PhaseState, plan: Optional[CoachingPlan]
                      ) -> tuple[Optional[dict[str, Any]], PhaseState]:
    """ADR-0077 for `executor`: the element's calculation row (None when it does not run) and the turn's
    state, which carries the row when it ran."""
    # ADR-0077 — the element's calculation, run in code (never by the coach) once every input is
    # present: confirmed values from state, the rest from the judgment's `calculation_inputs`. The
    # row joins this turn's state, so the coach is shown the figure (state injection), and the record.
    from backend.phases import calculations
    calc_row = calculations.run(
        phase, plan.focus_field if plan else None, dict(state.get("artifacts") or {}),
        (plan.judgment.calculation_inputs if plan is not None and plan.judgment is not None else None),
        _turn_ordinal(state))
    if calc_row is not None:
        logger.info("%s.executor: ADR-0077 — %s run in code: %s", phase, calc_row["tool"],
                    (calc_row["result"] or {}).get("annual_savings"))
        arts = dict(state.get("artifacts") or {})
        arts["computation_results"] = [*(arts.get("computation_results") or []), calc_row]
        state = {**state, "artifacts": arts}  # type: ignore[typeddict-item]
    return calc_row, state


def _backstop_result(phase: str, plan: Optional[CoachingPlan], prior: list,
                     hops_spent: list[int]) -> dict[str, Any]:
    """`executor`'s turn when the coach hit the recursion BACKSTOP (§16): the move's own reply, written in code."""
    logger.warning(
        "%s.executor: hit the %d-step BACKSTOP (§16) after %d hop(s) — "
        "returning a partial answer. This should not happen now that §3.7's "
        "hop budget and §26's off-ramp are live; it means a genuine runaway "
        "loop, not broad exploration.",
        phase, COACH_RECURSION_BACKSTOP, hops_spent[0],
    )
    # Never the backstop text as a coaching reply: the move was decided in
    # code, so code writes its reply. The step_log status still records
    # the degrade.
    fallback = _fallback_reply(phase, plan)
    return {"messages": [*prior, AIMessage(content=fallback.message)],
            "structured_response": fallback}


def _model_error_turn(phase: str, state: PhaseState, plan: Optional[CoachingPlan], prior: list,
                      exc: Exception) -> tuple[bool, Optional[str], dict[str, Any]]:
    """`executor`'s turn when a model service's error ended the call (ADR-0082): whether it was a content
    filter (T92), else T34 level 4's reason, and the turn answered in code (`_refused_turn`)."""
    filtered = False
    level_4: Optional[str] = None
    if content_safety.is_content_filter(exc):
        filtered = True
    else:
        level_4 = ("token_limit" if model_fallback.reason(exc) == model_fallback.TOKEN_LIMIT
                   else "model_unavailable")
    logger.warning("%s.executor: %s — %s, answered in code (ADR-0082)", phase, type(exc).__name__,
                   "content filter (T92)" if filtered else level_4)
    _, result = _refused_turn(phase, state, plan, prior, filtered)
    return filtered, level_4, result


def _contained_limit(phase: str, plan: Optional[CoachingPlan], result: dict[str, Any], history: list,
                     coach_limit: int, fell_back: bool
                     ) -> tuple[dict[str, Any], list, bool, bool, dict[str, Any] | None, bool]:
    """T69 / G-119 and G-153 for `executor`: a coach loop the call limit ended, or that ended with no
    structured reply, answered with the move's own reply written in code. Returns the result, its
    messages, `limited`, `unfinished`, the G-139 diagnosis and `fell_back`."""
    produced = list(result.get("messages") or [])
    # T69 / G-119 — the call limit ended the agent loop: its notice is never the Belt's reply;
    # the move's own reply is written in code, as on a timeout.
    limited = (result.get("structured_response") is None and bool(produced)
               and isinstance(produced[-1], AIMessage) and _LIMIT_NOTICE in str(produced[-1].content))
    limit_diagnosis: dict[str, Any] | None = None
    if limited:
        # G-139: what the coach returned before the limit ended it —
        # to step_log and the move record, so the run record carries it.
        limit_diagnosis = _limit_diagnosis(produced[len(history):], coach_limit)
        fallback = _fallback_reply(phase, plan)
        fell_back = True
        logger.warning("%s.executor: the coach reached its %d-call share of the turn's %d model calls "
                       "(T69, G-119) — the move's reply is written in code. G-139 diagnosis: %s",
                       phase, coach_limit, TURN_MODEL_CALLS, limit_diagnosis["why"])
        produced = [*produced[:-1], AIMessage(content=fallback.message)]
        result = {**result, "messages": produced, "structured_response": fallback}
    # G-153 — the loop ended with no structured reply and no limit notice: the coach's call was cut
    # off at its token limit or ended on text alone. Contained as the limit is:
    # the move's reply is written in code, never an empty turn, and the diagnosis rides on the record.
    unfinished = not limited and result.get("structured_response") is None
    if unfinished:
        limit_diagnosis = _limit_diagnosis(produced[len(history):], coach_limit)
        fallback = _fallback_reply(phase, plan)
        fell_back = True
        logger.warning("%s.executor: the coach's turn ended with no structured reply (G-153) — the "
                       "move's reply is written in code. Diagnosis: %s", phase, limit_diagnosis["why"])
        ended = produced[-1] if len(produced) > len(history) and isinstance(produced[-1], AIMessage) else None
        produced = [*(produced[:-1] if ended is not None else produced), AIMessage(content=fallback.message)]
        result = {**result, "messages": produced, "structured_response": fallback}
    return result, produced, limited, unfinished, limit_diagnosis, fell_back


def _sourced_numbers(phase: str, state: PhaseState, plan: Optional[CoachingPlan], result: dict[str, Any],
                     produced: list, history: list, written: Optional[CoachingResponse], fell_back: bool
                     ) -> tuple[dict[str, Any], list, list[str], Optional[dict[str, str]], list[str], bool, bool]:
    """G-173 (ADR-0077) for `executor`: the coach's reply with no number no source gives — trimmed, or
    replaced by the move's reply written in code. Returns the result, its messages, the unsourced
    numbers, the rejected reply's words, the sentences left out, `numbers_rejected` and `fell_back`."""
    # G-173 (ADR-0077) — every number in the coach's words comes from the Belt, the case, a computation
    # result, the script or this turn's tool results (`_number_sources`). A reply with any other number
    # keeps everything but the sentences holding one, and says so in a line written in code; only when
    # too little remains is the move's reply written in code.
    unsourced: list[str] = []
    rejected: Optional[dict[str, str]] = None     # G-173: the rejected reply's own words, for step_log
    left_out: list[str] = []                      # G-173: the sentences left out of a kept reply
    numbers_rejected = False                      # G-173: the reply was replaced, not trimmed
    sources: set[float] = set()
    if written is None and not fell_back and isinstance(result.get("structured_response"), CoachingResponse):
        sources = _number_sources(phase, state, produced[len(history):])
        unsourced = _unsourced_numbers(result["structured_response"], sources)
    trimmed: Optional[CoachingResponse] = None
    if unsourced:
        sent = result["structured_response"]
        rejected = {k: str(getattr(sent, k, "") or "")[:1500] for k in ("message", "explanation", "example", "prompt")}
        trimmed, left_out = _without_unsourced(sent, sources)
    if trimmed is not None:
        logger.warning("%s.executor: G-173 — the coach's reply held numbers no source gives (%s); the %d "
                       "sentence(s) holding them were left out and the rest kept", phase,
                       ", ".join(unsourced[:5]), len(left_out))
        ended = produced[-1] if len(produced) > len(history) and isinstance(produced[-1], AIMessage) else None
        produced = [*(produced[:-1] if ended is not None else produced), AIMessage(content=trimmed.message)]
        result = {**result, "messages": produced, "structured_response": trimmed}
    elif unsourced:
        fallback = _fallback_reply(phase, plan)
        if plan is not None and plan.move == moves.RESPOND:
            # The Belt's question asked for a figure no calculation in code gives — say so, in code,
            # before the ask, rather than answering with the ask alone.
            from backend.core.prompts import CALCULATION_FALLBACK, CALCULATION_NEEDS
            from backend.phases import calculations
            arts = dict(state.get("artifacts") or {})
            needs = calculations.missing_inputs(phase, plan.focus_field, arts)
            # In the catalogue (this element has a calculation in code): its own figures when it has run,
            # else what it still needs; outside it, `CALCULATION_FALLBACK`.
            said = (calculations.how_it_was_calculated(calculations.current(arts, phase, plan.focus_field), arts)
                    or (CALCULATION_NEEDS.format(needs=" and ".join(needs.values())) if needs else "")
                    or CALCULATION_FALLBACK)
            fallback = fallback.model_copy(update={"message": f"{said}\n\n{fallback.message}"})
        fell_back = numbers_rejected = True
        logger.warning("%s.executor: G-173 — the coach's reply holds numbers no source gives (%s) and too "
                       "little remains without them; the move's reply is written in code", phase,
                       ", ".join(unsourced[:5]))
        ended = produced[-1] if len(produced) > len(history) and isinstance(produced[-1], AIMessage) else None
        produced = [*(produced[:-1] if ended is not None else produced), AIMessage(content=fallback.message)]
        result = {**result, "messages": produced, "structured_response": fallback}
    return result, produced, unsourced, rejected, left_out, numbers_rejected, fell_back


def _flag_of(reply: CoachingResponse | None) -> Optional[dict[str, Any]]:
    """The reply's `contradiction_flag` as a dict, or None."""
    flag = getattr(reply, "contradiction_flag", None) if reply is not None else None
    if isinstance(flag, BaseModel):
        return flag.model_dump()
    return dict(flag) if isinstance(flag, dict) and flag else None


def _mismatch_kept_note(phase: str, plan: Optional[CoachingPlan]) -> Optional[dict[str, Any]]:
    """ADR-0112: on a Confirm of a read-back that carried a mismatch, what was kept — the element, the note and the
    flag — for `step_log`; None otherwise."""
    from backend.middleware.state_injection import mismatch_kept
    confirmed = dict((plan.confirmed if plan is not None else None) or {})
    note = mismatch_kept(phase, confirmed.get("mismatch"))
    return {"field": confirmed.get("field"), "note": note, "flag": confirmed["mismatch"]} if note else None


def _with_mismatch(phase: str, plan: Optional[CoachingPlan], reply: CoachingResponse) -> CoachingResponse:
    """ADR-0112 (founder ruling 2026-10-27): a mismatch the coach flagged is told to the Belt in the reply, written in
    code — what the answer conflicts with, and the choice to correct it or keep it — before the reply's closing
    question. No pause, no interrupt: the conversation moves on."""
    from backend.middleware.state_injection import mismatch_line
    line = mismatch_line(phase, _flag_of(reply), read_back=plan is not None and plan.move == moves.READ_BACK)
    message = str(reply.message or "")
    if not line or line in message:
        return reply
    paragraphs = message.rstrip().split("\n\n")
    if len(paragraphs) > 1 and paragraphs[-1].rstrip().endswith("?"):
        message = "\n\n".join([*paragraphs[:-1], line, paragraphs[-1]])
    else:
        message = f"{message.rstrip()}\n\n{line}"
    return reply.model_copy(update={"message": message})


def _with_calculation_lines(phase: str, state: PhaseState, plan: Optional[CoachingPlan],
                            reply: CoachingResponse) -> CoachingResponse:
    """ADR-0077 point 4 — the figures and how they were calculated, in code, under a read-back; R-E (founder ruling
    2026-10-27) — and under any answer about an element with a calculation ("How do I calculate the cost of the gap?"),
    from its recorded row or, before the Belt answered, from the case's confirmed values. Returns a COPY, or `reply`."""
    from backend.phases import calculations
    if plan is None or not (plan.move == moves.READ_BACK or (
            plan.move == moves.RESPOND and calculations.calculation_for(phase, plan.focus_field))):
        return reply
    arts = dict(state.get("artifacts") or {})
    line = calculations.how_it_was_calculated(calculations.current(arts, phase, plan.focus_field), arts)
    if not line or line in (reply.message or ""):
        return reply
    return reply.model_copy(update={"message": f"{(reply.message or '').rstrip()}\n\n{line}"})


def _shaped_reply(phase: str, state: PhaseState, plan: Optional[CoachingPlan], reply: CoachingResponse | None,
                  new_messages: list, turn_type: str, written: Optional[CoachingResponse], *,
                  fell_back: bool, filtered: bool, level_4: Optional[str], card: bool = False
                  ) -> tuple[dict[str, Any], list[dict], CoachingResponse | None, list]:
    """`executor`'s captures and citations from the coach's reply, and the reply as the turn keeps it (the
    upload check, the read-back's calculation line, the teaching blocks, the next element, the script's
    sample). Returns `captured`, `citations`, the reply and the turn's new messages. With `card` (R-C), the reply is
    the element card's text and the card carries the teaching: no teaching block and no sample is added."""
    if card and reply is not None:
        return {}, list(state.get("citations") or []), reply, _with_coaching_text(new_messages, reply)
    from backend.phases import calculations
    captured: dict[str, Any] = {}
    citations: list[dict] = list(state.get("citations") or [])
    if reply is not None:
        captured = _captured_fields(phase, reply)
        citations.extend(_anchored([c.model_dump() if isinstance(c, BaseModel) else c for c in reply.citations or []],
                                   state))
        if turn_type == turn_tools.UPLOAD:
            reply = _with_upload_check(phase, reply, _unread_upload(state), plan.focus_field if plan else None)
        reply = _with_calculation_lines(phase, state, plan, reply)
        reply = _with_mismatch(phase, plan, reply)                 # ADR-0112: told in the reply, never a pause
        new_messages = _with_coaching_text(new_messages, reply)

        # The four presentational blocks are OPTIONAL, and an empty one is a
        # FINDING rather than a failure: a required `str` would make a model
        # omitting `progress` fail the whole turn's structured output — a hard
        # failure to the Belt.
        #
        # **Logged loudly BECAUSE it is not fatal.** Without the log, the UI
        # would draw four blocks, one of them blank, and nothing would notice.
        # Degraded, not broken — and visible. On a teaching move the gap is
        # then filled from the script (`_with_teaching_blocks`).
        gaps = presentational_gaps(reply)
        # Wave 0 (founder test 2026-10-27, #59): a reply whose move asks for no new information — a read-back —
        # has no explanation, example or prompt to write, and `progress` is written in code; those blocks empty
        # are its normal shape, not a finding. Only a move that teaches or asks is held to them.
        if plan is None or plan.move not in SAMPLE_MOVES:
            gaps = [g for g in gaps if g not in ("explanation", "example", "prompt", "progress")]
        if gaps:
            logger.warning(
                "%s.executor: FINDING — §50.1 presentational field(s) came "
                "back empty: %s. The turn completes and the block renders "
                "empty (§56 amendment v1.64, §4.8: never a hard failure to "
                "the Belt). A recurring gap here is a PROMPT defect, not a "
                "schema one.",
                phase, ", ".join(gaps),
            )
            reply = _with_teaching_blocks(phase, plan, reply, gaps)
        if written is None and not fell_back:
            # G-175 — after a store, the reply teaches the next element.
            # DEF-220: the welcome is the phase's first element taught with no coach reply before it.
            opening = (not any(isinstance(m, AIMessage) for m in (state.get("messages") or []))
                       and plan is not None and plan.focus_field == next(iter(moves.positions(phase)), ("",))[0])
            belt = chr(10).join([*(m.text for m in (state.get("messages") or []) if isinstance(m, HumanMessage)),
                                 str(plan.answer or "") if plan else ""])
            taught = _lead_in_only(phase, plan, _teach_next(phase, plan, reply), opening=opening, belt=belt)
            if taught.message != reply.message:
                new_messages = _with_text(new_messages, str(taught.message))
            reply = taught
        if not (filtered or level_4):
            # G-170 — the example is the script's worked example, inserted by code.
            reply = _with_script_sample(phase, plan, reply)
    return captured, citations, reply, new_messages


def _consumed_uploads(state: PhaseState, produced: list, citations: list[dict],
                      turn_type: str) -> tuple[list[dict], dict | None]:
    """`executor`'s uploads with `consumed_at` written on each file this turn read, and the routed upload
    an upload turn read (None when it read none)."""
    # `consumed_at` is written HERE, not inside the tool. A `@tool` receives
    # only its arguments and cannot reach `PhaseState`; the node inspects the
    # turn's tool calls afterwards.
    uploads, consumed = _mark_consumed(state, produced, citations)
    # DEF-108 (W5) — an upload turn READ its file: section 5 named it, whether or not a numeric
    # column was loaded, so the next turn is not an upload turn again for the same file.
    routed = (_unread_upload(state) if turn_type == turn_tools.UPLOAD and not ROUTED_READ_FAILED.get()
              else None)
    if routed is not None:
        stamp = utc_now().isoformat()
        for u in uploads:
            if u.get("blob_path") == routed.get("blob_path") and not u.get("consumed_at"):
                u["consumed_at"] = stamp
                consumed += 1
    return uploads, routed


def _store_candidate(phase: str, plan: Optional[CoachingPlan], captured: dict[str, Any]
                     ) -> tuple[Optional[str], Optional[dict], dict[str, Any], list[str]]:
    """`executor`'s store candidate, decided by the plan's move: the move, the read-back's pending entry,
    the candidate and the captures not stored (logged)."""
    move = plan.move if plan else None
    pending = dict(plan.pending) if plan and plan.pending else None
    if move == moves.STORE_AND_ADVANCE and plan is not None:
        candidate = dict(plan.store)
    elif move == moves.READ_BACK and pending:
        # ADR-0071 (DEF-076): the baseline and the target are parsed in code from the Belt's
        # words by `moves.pending_store`; the coach's own rendering of them is not a candidate.
        from backend.phases.define.parse import METRIC_FIELDS
        candidate = {f: v for f, v in captured.items() if f in (pending.get("fields") or [])
                     and not (phase == "define" and f in METRIC_FIELDS)}
    else:
        candidate = {}
    not_stored = sorted(f for f in captured if not (move == moves.READ_BACK and f in candidate))
    if not_stored:
        logger.info(
            "%s.executor: %d capture(s) NOT stored — the move is %s, and only a "
            "confirmed read-back is stored (§20 v1.75): %s",
            phase, len(not_stored), move, ", ".join(not_stored),
        )
    return move, pending, candidate, not_stored


def _refused_captures(phase: str, state: PhaseState, candidate: dict[str, Any], prior_artifacts: dict[str, Any]
                      ) -> tuple[dict[str, Any], list[str], dict[str, str], list[str], dict[str, Any]]:
    """`executor`'s guards on the candidate — empty, declared type, worked example — each refusal reported
    as a FINDING. Returns what is kept, the empty captures, the malformed ones, the worked-example
    refusals and the Belt's own confirmed values (G-159)."""
    kept, empty_captures = split_captures(candidate)

    # ── the declared type is enforced HERE, at the capture site ───────
    #
    # **Not at the model and not at assembly.** The per-phase response schema
    # narrows the shape (ADR-0110) but is not the enforcer: a value the model
    # sends in the wrong shape is still caught here. Coercing at assembly would INVENT the Belt's
    # data — a sentence about three people is not three `{name, role, function}`
    # entries, and anything turning one into the other is guessing which words
    # were the names.
    #
    # Ordered AFTER the empty split deliberately: a `""` for a `dict` field is
    # EMPTY, not malformed, and reporting it as the wrong type would send a
    # reader looking for a shape problem in a field the Belt never answered.
    kept, malformed = split_by_declared_type(phase, kept)

    # ── a worked example is NEVER captured as the Belt's data ─────────
    #
    # The script reaches the model every call, and with it every worked
    # example — each a plausible, well-formed value for the field it shows.
    # A capture that reproduces one (skills.example_match: containment either
    # way, or similarity >= 0.80 after normalising) is refused and reported,
    # exactly as a malformed one is: the field stays uncaptured, so the coach
    # asks again, and the turn does not fail for the Belt.
    # C3 (DEF-083): nor is a sample the coach showed — this turn's, or the one the Belt is answering.
    from backend.middleware.skills import matches_sample
    sample = _previous_sample(state)
    # G-159: the Belt's confirmed values — a sample built only from them quotes the Belt.
    belt_own = {k: v for k, v in prior_artifacts.items() if k != "computation_results"}
    example_refused = sorted(f for f, v in kept.items()
                             if example_match(v, phase) or (sample and matches_sample(v, sample, belt_own)))
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
    return kept, empty_captures, malformed, example_refused, belt_own


def _read_back_pending(phase: str, state: PhaseState, plan: Optional[CoachingPlan], move: Optional[str],
                       pending: Optional[dict], kept: dict[str, Any], prior_artifacts: dict[str, Any],
                       belt_own: dict[str, Any], reply: CoachingResponse | None
                       ) -> tuple[dict[str, Any], Optional[dict], dict[str, Any], Optional[str], Optional[str],
                                  list[str], list[str], list[str]]:
    """`executor`'s read-back, held as PENDING. Returns what reaches `artifacts` now (nothing, on a
    read-back), the pending entry, the carried parts, the R18 link and located steps, the copied sample's
    fields, the fields a Confirm could not store and the placeholders."""
    # A read-back's value is PENDING: it goes on the move record with
    # what a confirmation will store, and nothing reaches `artifacts` now.
    from backend.middleware.skills import matches_sample
    carried: dict[str, Any] = {}
    link: Optional[str] = None
    located_line: Optional[str] = None          # DEF-211: a "from → to" location's steps, read back in code
    copied: list[str] = []
    short: list[str] = []           # G-163: the position's fields a Confirm of this read-back could not store
    unfilled: list[str] = []        # G-174: placeholders in what a Confirm would store
    if move == moves.READ_BACK and pending is not None:
        # G-118 (DEF-157) — a part of the element this read-back lacks but an earlier read-back of
        # it carried (the CTQs, after a Change) is carried into it, shown to the Belt below, and
        # stored only if the Belt confirms.
        earlier = dict(pending.get("earlier") or {})
        carried = {f: earlier[f] for f in (pending.get("fields") or [])
                   if f != pending.get("field") and f not in kept and f in earlier}
        # R-H: a read-back made again in code (no coach capture) proposes the value its pending already holds.
        held = {f: v for f, v in (pending.get("store") or {}).items()
                if f in (pending.get("fields") or []) and f not in kept}
        kept = {**held, **kept, **carried}
        store = moves.pending_store(phase, pending, kept, prior_artifacts)
        # C3 (DEF-083): what a Confirm would store is never the sample the Belt was shown — even when it
        # is the Belt's own typed words (a plain-text answer stores those). G-160: no read-back is then
        # offered (a Confirm could not store it); the Belt is told why and asked for their own answer.
        shown = _previous_sample(state)
        copied = sorted(f for f, v in store.items() if shown and matches_sample(v, shown, belt_own))
        if copied:
            store = {f: v for f, v in store.items() if f not in copied}
            logger.warning("%s.executor: C3 — the answer to `%s` reproduces the sample the Belt was "
                           "shown; it will not be stored", phase, ", ".join(copied))
        # Read-back = Gate (founder 2026-10-28): the card, the drawing, the metric's meaning and what is missing
        # are all read from `store` — what a Confirm stores — never from the coach's capture beside it.
        # DEF-021 / DEF-082 (R16) — the reason the Belt gave for a change, and where each value came
        # from, as the coach captured them in this read-back; the Confirm writes them to the log.
        captures = captured_entries(reply)
        pending = {**pending, "store": store,
                   "reasons": {str(e.get("field_name")): str(e["reason"]).strip()
                               for e in captures if e.get("field_name") and str(e.get("reason") or "").strip()},
                   "sources": {str(e.get("field_name")): str(e.get("source") or "")
                               for e in captures if e.get("field_name")}}
        if _flag_of(reply):
            # ADR-0112: the mismatch told with this read-back rides on it; a Confirm keeps it, dated, in the log.
            pending["mismatch"] = _flag_of(reply)
        if pending.get("upload"):
            # ADR-0085 (G-169) — a read-back of an uploaded file: what a Confirm stores came from the file (R16).
            pending["sources"] = {**pending["sources"], **{f: "upload" for f in store}}
        if pending.get("spans") and isinstance(store.get(str(pending.get("field"))), str):
            # ADR-0093 decision 5: a span shown in a row is verbatim in the Belt's answer AND in the text a
            # Confirm stores (a composed answer stores the coach's version) — otherwise the whole answer, once.
            from backend.phases.define.templates import verbatim_spans
            pending["spans"] = verbatim_spans(pending["spans"], str(pending["field"]),
                                              str(pending.get("belt_words") or ""), store[str(pending["field"])])
        link = _r18_link(phase, plan.focus_field if plan else None, store, prior_artifacts)
        located_line = _r18_located(phase, plan.focus_field if plan else None, store, prior_artifacts)
        short = moves.store_missing(pending.get("fields") or [pending.get("field")], prior_artifacts, store)
        unfilled = placeholders(store, str(pending.get("belt_words") or ""))
        if unfilled:
            logger.warning("%s.executor: G-174 — the read-back of `%s` holds a placeholder (%s); it is challenged, "
                           "not offered for a Confirm", phase, pending.get("field"), "; ".join(unfilled[:3]))
        kept = {}
    return kept, pending, carried, link, located_line, copied, short, unfilled


def _turn_field_status(phase: str, state: PhaseState, plan: Optional[CoachingPlan], move: Optional[str],
                       pending: Optional[dict], captured: dict[str, Any], prior_artifacts: dict[str, Any],
                       filtered: bool, level_4: Optional[str]) -> tuple[dict[str, dict], bool]:
    """R5 for `executor`: the statuses stored at turn end, with the offers this answer made for other
    elements (DEF-098, G-257), and `refused` — the model did not answer this turn (ADR-0082)."""
    # R5 — THE STATUSES, STORED AT TURN END. The plan carries the
    # after-change map; a read-back's pending entry gains here what the Belt's
    # yes will store (it needs this turn's read-back to know).
    field_status = {f: dict(v) for f, v in ((plan.field_status if plan else None)
                                            or state.get("field_status") or {}).items()}
    # ADR-0082 — a turn the model did not answer (T92's refusal, T34's level 4) changes nothing: the
    # element keeps its status from before the turn, no read-back is offered, and the reply written in
    # code is the Belt's whole answer.
    refused = filtered or level_4 is not None
    # DEF-098 (R15, G-196; ADR-0002): a value the coach captured for ANOTHER element, one not confirmed, is kept
    # as an offer in that element's own entry — nothing is stored; when the element comes up it is read back
    # (`moves.from_offer`). The element in focus and the fields of this turn's read-back are this turn's own.
    if not refused and plan is not None:
        own = {plan.focus_field, *((pending or {}).get("fields") or [])}
        elements = {f for f, _ in moves.positions(phase)}
        for f, value in captured.items():
            if f in own or f not in elements or f in prior_artifacts or value in (None, "", [], {}):
                continue
            entry = dict(field_status.get(f) or {})
            if entry.get("status") in (moves.CONFIRMED, moves.ANSWERED):
                continue
            field_status[f] = {**entry, "offered": {"value": value}}
            logger.info("%s.executor: `%s` offered from this answer — read back when it comes up (DEF-098)",
                        phase, f)
        # G-257: the coach captures only the element it reads back, so a goal the Belt's own words state with a
        # figure is offered from those words, in code — unless the coach offered one itself.
        goal = "goal_statement"
        if phase == "define" and move == moves.READ_BACK and goal not in own and goal not in prior_artifacts:
            from backend.phases.define import parse as define_parse
            said = define_parse.goal_sentence(moves.belt_message(list(state.get("messages") or [])))
            entry = dict(field_status.get(goal) or {})
            if said and not entry.get("offered") and entry.get("status") not in (moves.CONFIRMED, moves.ANSWERED):
                field_status[goal] = {**entry, "offered": {"value": said}}
                logger.info("%s.executor: the goal offered from the Belt's words (G-257)", phase)
    return field_status, refused


def _read_back_outcome(phase: str, state: PhaseState, plan: Optional[CoachingPlan], move: Optional[str],
                       pending: Optional[dict], field_status: dict[str, dict], *, refused: bool,
                       fell_back: bool, short: list[str], unfilled: list[str], link: Optional[str]
                       ) -> tuple[dict[str, dict], bool, bool, bool]:
    """Whether `executor`'s read-back is offered for a Confirm — or is resent (G-140), challenged as a
    copied sample, a short store or a placeholder (G-163), or challenged as an R18 mismatch — with the
    focus element's status each leaves. Returns `field_status`, `resend`, `sample_challenge` and
    `link_challenge`."""
    # G-140: a read-back written in CODE whose pending store lacks a
    # field of the position is not offered — a Confirm under it could not store. The turn changes
    # nothing: the element keeps its status from before the turn, the reply asks the Belt to send
    # the answer again, and the move record carries no read-back (so no Confirm is drawn).
    resend = bool(not refused and fell_back and move == moves.READ_BACK and pending is not None and plan
                  and plan.focus_field and short)
    if refused and plan is not None and plan.focus_field:
        field_status[plan.focus_field] = dict((state.get("field_status") or {}).get(plan.focus_field)
                                              or {"status": moves.ASKED})
    if resend and plan is not None and plan.focus_field:
        before = dict((state.get("field_status") or {}).get(plan.focus_field) or {"status": moves.ASKED})
        field_status[plan.focus_field] = before
        logger.warning("%s.executor: G-140 — the code-written read-back of `%s` carries nothing a "
                       "Confirm could store; the Belt is asked to send the answer again",
                       phase, plan.focus_field)
    # ADR-0078 point 5 (R18, DEF-085) — a SIPOC and a problem statement that point at different steps
    # turn the read-back into a challenge naming the mismatch, once; the element stays asked, the
    # Belt's words kept. Answered again with the same mismatch, the read-back goes ahead and says so.
    focus_before = dict((state.get("field_status") or {}).get(plan.focus_field) or {}) \
        if plan is not None and plan.focus_field else {}
    # G-163 (one rule; G-160 is its copied-sample case): a read-back a Confirm could not store is never
    # offered for a Confirm — the element stays asked, the Belt's words kept, and the reply, written in
    # code, says why (below). A code-written read-back keeps G-140's own wording (`resend`).
    # ADR-0094 decision 2 (DEF-208): a file read back as a DRAFT keeps its read-back — its missing parts are marked on
    # the card, whose Confirm stays closed until they are given (ADR-0093 decision 2); a placeholder still challenges.
    draft = bool(pending and pending.get("draft"))
    sample_challenge = bool(((short and not draft) or unfilled) and not resend and not refused
                            and move == moves.READ_BACK and pending is not None and plan and plan.focus_field)
    if sample_challenge and plan is not None and plan.focus_field and pending is not None:
        field_status[plan.focus_field] = {
            "status": moves.ASKED, "answer": str(pending.get("belt_words") or ""),
            "messages": int(pending.get("messages") or 1),
            **({"attempts": focus_before["attempts"]} if focus_before.get("attempts") else {}),
            **({"earlier": pending["earlier"]} if pending.get("earlier") else {}),
            **({"upload": pending["upload"]} if pending.get("upload") else {})}          # G-301 (DEF-264)
    link_challenge = bool(link and not resend and not refused and not sample_challenge and not focus_before.get("link_raised")
                          and move == moves.READ_BACK and pending is not None and plan and plan.focus_field)
    if link_challenge and plan is not None and plan.focus_field and pending is not None:
        field_status[plan.focus_field] = {
            "status": moves.ASKED, "answer": str(pending.get("belt_words") or ""),
            "messages": int(pending.get("messages") or 1), "link_raised": True,
            "challenged": pending,         # R-H: what "Add step n to the problem statement" reads back again
            **({"attempts": focus_before["attempts"]} if focus_before.get("attempts") else {}),
            **({"earlier": pending["earlier"]} if pending.get("earlier") else {}),
            **({"upload": pending["upload"]} if pending.get("upload") else {})}          # G-301 (DEF-264)
        logger.info("%s.executor: R18 — the read-back of `%s` is raised as a challenge: %s",
                    phase, plan.focus_field, link)
    elif (not resend and not refused and not sample_challenge and move == moves.READ_BACK
          and pending is not None and plan and plan.focus_field):
        field_status[plan.focus_field] = {**field_status.get(plan.focus_field, {}),
                                          "status": moves.ANSWERED, "pending": pending}
    return field_status, resend, sample_challenge, link_challenge


def _with_define_read_back_lines(phase: str, move: Optional[str], pending: Optional[dict], new_messages: list,
                                 reply: CoachingResponse | None) -> list:
    """`executor`'s lines on a Define read-back, each written in code: the metric reading, its meaning, the
    CTQ and 5W2H questions, the date as read, the step-time questions and a list read as numbered items."""
    if move == moves.READ_BACK and phase == "define" and pending is not None:
        from backend.phases.define import templates as _templates
        if str(pending.get("field") or "") not in _templates.TEMPLATES:
            # DEF-223 (G-224): the read-back card (ADR-0093) shows the number a Confirm stores in its own row; the
            # code-written line is written only for a read-back that draws no card, never run into the coach's text.
            new_messages = _with_metric_reading(new_messages, reply, dict(pending.get("store") or {}))
        # DEF-018 — the metric's first appearance: its meaning from the Belt's registry entry, in code.
        meaning = _metric_meaning(dict(pending.get("store") or {})) \
            if "metric_definitions" in (pending.get("fields") or []) else None
        if meaning:
            new_messages = _with_code_line(new_messages, reply, meaning)
        # ADR-0088 decision 2: rows at odds with the CTQs the Belt listed are asked about before Confirm.
        from backend.phases.define.parse import ctq_question, five_w_two_h_question
        asked = ctq_question((pending.get("store") or {}).get("critical_to_quality"), pending.get("belt_words"))
        if asked:
            new_messages = _with_code_line(new_messages, reply, asked)
        # ADR-0088 decision 5: a target date is read back as the Belt wrote it and as the calendar date stored.
        if "target_date" in (pending.get("store") or {}):
            from backend.phases.define.parse import date_shown
            new_messages = _with_code_line(new_messages, reply, "Read as a date: " + date_shown(
                pending["store"]["target_date"], pending.get("belt_words")))
        # ADR-0088 decision 4 (G-186): the step times are asked about, never refused.
        from backend.phases.define.parse import duration_questions
        for question in duration_questions((pending.get("store") or {}).get("process_map_sipoc")):
            new_messages = _with_code_line(new_messages, reply, question)
        # ADR-0088 decision 1 (G-183): a list-shaped answer is read back as the items the Belt numbered.
        from backend.phases.define.parse import list_items
        for f, label in (("secondary_metrics", "Secondary metrics"), ("issues_and_barriers", "Issues and barriers")):
            items = list_items((pending.get("store") or {}).get(f), label)
            if len(items) > 1:
                new_messages = _with_code_line(new_messages, reply, f"Read as {len(items)} items:" + "".join(
                    f"{chr(10)}{n}. {item}" for n, item in enumerate(items, start=1)))
        # ADR-0088 decision 7: the seventh 5W2H answer is how the problem shows up, never a goal.
        asked = five_w_two_h_question(pending.get("store"))
        if asked:
            new_messages = _with_code_line(new_messages, reply, asked)
    return new_messages


def _attach_visual(phase: str, plan: Optional[CoachingPlan], move: Optional[str], pending: Optional[dict],
                   prior_artifacts: dict[str, Any], kept: dict[str, Any], new_messages: list) -> None:
    """`executor`'s element visual and teaching drawing on the reply (Define only). Mutates in place."""
    # ADR-0070 — the element's visual, drawn by the program with the gate document's own function:
    # on a read-back from the coach's structured values ("not yet confirmed"), after Confirm from
    # the stored values. No model call draws.
    if phase == "define":
        from backend.phases.define import visuals
        drawn = (visuals.for_field(plan.focus_field, {**prior_artifacts, **dict((pending or {}).get("store") or {})},
                                   confirmed=False)
                 if move == moves.READ_BACK and plan is not None and pending is not None else
                 # ADR-0086: the target read back from the goal — its chart, not yet confirmed.
                 visuals.for_field(plan.focus_field, {**prior_artifacts, **kept,
                                                      **dict((goal_read_back(plan) or {}).get("store") or {})},
                                   confirmed=False)
                 if move == moves.STORE_AND_ADVANCE and plan is not None and goal_read_back(plan) is not None else
                 visuals.for_field(plan.stored_field, {**prior_artifacts, **kept}, confirmed=True)
                 if move == moves.STORE_AND_ADVANCE and plan is not None else None)
        # DEF-211 (ADR-0070): the element's worked example, drawn on its teaching
        # turn — taught on its own, or by the move that stores the element before it — from the skill's file.
        teach_drawing = (visuals.teach_example(plan.focus_field)
                         if plan is not None and move in (moves.TEACH, moves.STORE_AND_ADVANCE) else None)
        for visual in (drawn, teach_drawing if teach_drawing and not (drawn and drawn[0] == teach_drawing[0]) else None):
            if not visual:
                continue
            for msg in reversed(new_messages):
                if isinstance(msg, AIMessage):
                    msg.additional_kwargs[visual[0]] = visual[1]
                    break


def _code_written_reply(phase: str, state: PhaseState, plan: Optional[CoachingPlan], move: Optional[str],
                        pending: Optional[dict], reply: CoachingResponse | None, new_messages: list, *,
                        resend: bool, sample_challenge: bool, link_challenge: bool, link: Optional[str],
                        refused: bool, copied: list[str], short: list[str], unfilled: list[str],
                        prior_artifacts: dict[str, Any]) -> tuple[list, CoachingResponse | None]:
    """`executor`'s reply where code writes it: the resend (G-140), the challenge of a read-back a Confirm
    could not store (G-163 / G-160), the R18 challenge or kept-link line, a draft's ask, and the ask for a
    file the Belt pointed at (G-250). Returns the turn's new messages and the reply."""
    if resend:
        # G-140 — the reply is the resend sentence alone; the step line stays.
        new_messages = _with_text(new_messages, FALLBACK_RESEND)
        if reply is not None:
            reply = reply.model_copy(update={"message": FALLBACK_RESEND, "explanation": "",
                                             "example": "", "prompt": ""})
    elif sample_challenge and plan is not None:
        # G-163 / G-160 — the reason, written in code; no read-back is offered this turn.
        from backend.core.prompts import SAMPLE_COPIED, STORE_PLACEHOLDER, STORE_SHORT
        element = guard_messages.element_name(phase, plan.focus_field or "")
        said = (SAMPLE_COPIED.format(element=element) if set(copied) & set(short) else
                STORE_SHORT.format(element=element, missing=_missing_words(phase, short, prior_artifacts, pending or {}))
                if short else STORE_PLACEHOLDER.format(element=element, gap="; ".join(f"“{g}”" for g in unfilled[:3])))
        # G-332 (DEF-259, founder test 2026-10-27 #60): the step-time questions are asked with what is missing — the
        # read-back's own lines are not shown on this turn, and "the steps add up to 4, you said 8" was never asked.
        from backend.phases.define.parse import duration_questions
        said = " ".join([said, *duration_questions(((pending or {}).get("store") or {}).get("process_map_sipoc"))])
        new_messages = _with_text(new_messages, said)
        if reply is not None:
            reply = reply.model_copy(update={"message": said, "explanation": "", "example": "", "prompt": ""})
    elif link_challenge and link:
        # ADR-0078 point 5 — the challenge, written in code; no read-back is offered this turn.
        from backend.core.prompts import LINK_CHALLENGE
        challenge = LINK_CHALLENGE.format(details=link)
        new_messages = _with_text(new_messages, challenge)
        if reply is not None:
            reply = reply.model_copy(update={"message": challenge, "explanation": "", "example": "",
                                             "prompt": ""})
    elif link and move == moves.READ_BACK and not refused:
        from backend.core.prompts import LINK_KEPT
        new_messages = _with_code_line(new_messages, reply, LINK_KEPT.format(details=link))
    elif move == moves.READ_BACK and pending and pending.get("draft") and not refused:
        # ADR-0094 decision 2 (DEF-208): a file read back as a draft — the ask, written in code.
        from backend.core.prompts import UPLOAD_DRAFT_ASK
        new_messages = _with_code_line(new_messages, reply, UPLOAD_DRAFT_ASK)
    if (plan is not None and move == moves.RESPOND and plan.reason == moves.POINTS_AT_FILE_REASON and plan.focus_field
            and not (state.get("uploads") or []) and not resend and not refused):
        # G-250: it points at a file and none is attached — the reply is written in code: ask for the file
        # first, or typing. The coach is not told there is no file, so its words are not kept.
        from backend.core import guard_messages as _names   # an alias: a bare import would make the name local
        from backend.core.prompts import NO_FILE_ATTACHED
        name = _names.element_name(phase, plan.focus_field)
        no_file = NO_FILE_ATTACHED.format(element=name[:1].lower() + name[1:])
        new_messages = _with_text(new_messages, no_file)
        if reply is not None:
            reply = reply.model_copy(update={"message": no_file})
    return new_messages, reply


def _with_turn_lines(new_messages: list, reply: CoachingResponse | None, produced: list, history: list, *,
                     located_line: Optional[str], move: Optional[str], pending: Optional[dict], belt_words: str,
                     written: Optional[CoachingResponse], resend: bool, refused: bool, fell_back: bool,
                     sample_challenge: bool, link_challenge: bool
                     ) -> tuple[list, CoachingResponse | None, dict[str, int]]:
    """`executor`'s last lines on the reply: the located steps (DEF-211), the PII line (T87) and the
    coach's message without a repeated block (G-171). Returns the turn's new messages, the reply and
    the personal data masked in this turn's tool results, by type."""
    if (located_line and move == moves.READ_BACK and pending is not None and not resend and not refused
            and not sample_challenge and not link_challenge):
        # DEF-211 (ADR-0078): the located steps, read back in code, for the read-back's Confirm.
        new_messages = _with_code_line(new_messages, reply, located_line)
    # The PII line (T87, ADR-0062): when this turn's lookups read values masked
    # from an upload, the reply says so, in code — the Belt knows what the coach could not see.
    masked = pii.counted([str(m.content) for m in produced[len(history):] if isinstance(m, ToolMessage)])
    if masked and not resend and not refused:
        from backend.core.prompts import PII_HIDDEN_TURN
        new_messages = _with_code_line(new_messages, reply, PII_HIDDEN_TURN.format(what=pii.described(masked)))
    if reply is not None and not refused and not fell_back and written is None:
        # G-171 — the coach's message never repeats the example or the question block
        # (a reply written in code is composed once, its ask included).
        shown = next((m.text for m in reversed(new_messages) if isinstance(m, AIMessage)), "")
        single = _without_repeated_blocks(shown, str(reply.example or ""), str(reply.prompt or ""),
                                          str(reply.explanation or ""), belt=belt_words)
        if single != shown:
            new_messages = _with_text(new_messages, single)
            reply = reply.model_copy(update={"message": single})
    return new_messages, reply, masked


def _turn_move_record(plan: Optional[CoachingPlan], move: Optional[str], pending: Optional[dict],
                      kept: dict[str, Any], *, refused: bool, level_4: Optional[str], resend: bool,
                      sample_challenge: bool, link_challenge: bool, short: list[str], unfilled: list[str],
                      copied: list[str], link: Optional[str]) -> dict[str, Any] | None:
    """`executor`'s move record: a read-back's pending entry only where one is offered, and why none is
    on a refused turn (ADR-0082), a resend (G-140) or a challenge (G-163 / G-160, ADR-0078 point 5)."""
    record = _move_record(plan, pending if move in (moves.READ_BACK, moves.RESPOND)
                          and not resend and not refused and not link_challenge and not sample_challenge else None, kept)
    if refused and record is not None:
        # ADR-0082 — no read-back is offered, so the screen draws no Confirm; `refused` says why.
        record.update({"move": moves.RESPOND, "pending": None, "refused": level_4 or "content_filter"})
    if resend and record is not None:
        # G-140 — no read-back is offered, so the screen draws no Confirm (it draws one only under
        # a `read_back` move); `resend` says why.
        record.update({"move": moves.RESPOND, "pending": None, "resend": True})
    if sample_challenge and record is not None:
        # G-163 / G-160 — a challenge, not a read-back: no Confirm is drawn; `store_missing` says why.
        record.update({"move": moves.CHALLENGE, "status": moves.ASKED, "pending": None, "store_missing": short,
                       **({"placeholders": unfilled} if unfilled else {}),
                       **({"sample_copied": copied} if copied else {})})
    if link_challenge and record is not None:
        # ADR-0078 point 5 — a challenge, not a read-back: no Confirm is drawn; `link` says why.
        record.update({"move": moves.CHALLENGE, "status": moves.ASKED, "pending": None, "link": link})
    return record


def _record_fallback(phase: str, move: Optional[str], record: dict[str, Any] | None,
                     limit_diagnosis: dict[str, Any] | None, *, fell_back: bool, timed_out: bool, filtered: bool,
                     level_4: Optional[str], limited: bool, unfinished: bool, numbers_rejected: bool) -> None:
    """`executor`'s containment record: a reply written by code is logged as the DEFECT it is, with its
    cause, and marked on the move record with the G-139 diagnosis. Mutates `record` in place."""
    if fell_back:
        logger.error(
            "%s.executor: DEFECT — the coach did not finish its %s move (%s); the "
            "reply was written by code (containment, not a fix).",
            phase, move, "timeout" if timed_out else "content filter" if filtered else level_4 if level_4 else
            "call limit" if limited else "no structured reply" if unfinished else
            # G-173: a rejected reply names its own cause.
            "a number no source gives (G-173)" if numbers_rejected else "runaway loop backstop")
        if record is not None:
            record["fallback"] = True
            if limit_diagnosis is not None:
                record["limit"] = limit_diagnosis          # G-139: the run record reads it here


def _define_completion(phase: str, plan: Optional[CoachingPlan], record: dict[str, Any] | None,
                       new_messages: list, reply: CoachingResponse | None, fell_back: bool
                       ) -> tuple[list, CoachingResponse | None, dict[str, Any] | None]:
    """DEF-212 (G-213) for `executor`: the last Confirm of Define, its reply written in code. Returns the
    turn's new messages, the reply and the completion card (None on any other turn)."""
    completion = None
    if (phase == "define" and record is not None and record.get("move") == moves.STORE_AND_ADVANCE
            and record.get("stored_field") and plan is not None and not plan.focus_field and not fell_back):
        # DEF-212 (G-213): the last Confirm of Define — every element confirmed, none left in focus. The reply is
        # written in code: that all are confirmed, and the completion card's steps in order — never the coach's own
        # word on approving before anything was submitted. What was stored is the saved note's (DEF-290).
        from backend.core.prompts import DEFINE_COMPLETE_CARD, DEFINE_COMPLETE_LINE
        done = DEFINE_COMPLETE_LINE.format(n=len(DEFINE_FIELD_ORDER))
        new_messages = _with_text(new_messages, done)
        if reply is not None:
            reply = reply.model_copy(update={"message": done})
        completion = {"title": DEFINE_COMPLETE_CARD["title"], "steps": list(DEFINE_COMPLETE_CARD["steps"])}
    return new_messages, reply, completion


async def executor(
    phase: str,
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
    *,
    written: Optional[CoachingResponse] = None,
    engine_timeout: bool = False,
) -> dict[str, Any]:
    """Run one coaching turn. **Returns plainly — emits no routing `Command`.**

    The executor consumes the plan and decides no strategy: the coach does not
    pick the field, does not choose the retrieval mode, and does not route.
    Control returns to the planner on the static edge, and the planner chooses
    what happens next.

    **This is the v2 field writer.** The coach is `create_agent` with the
    phase's `CoachingResponse` model as `response_format`. What reaches
    `artifacts`, under the v2 names the gate checks (`gate_registry.check_gate`), is decided by the
    plan, never by what the coach returned: nothing is stored before the Belt
    confirms (the store block below).

    **How the plan reaches the coach**: the focus field and the move through
    the project-state block (`BeforeModelStateInjection`) and the focus
    field's block of the phase script (`DMAICSkillsMiddleware`); the grader
    judges the reply as that move. An unread upload's read is dispatched by this node
    (`_dispatch_routed_read`), so the model is not offered that decision at
    all; every other tool the coach calls is its own choice.

    The coach's answer goes into `messages` as an `AIMessage`. A `propose_diagram`
    payload from this turn rides on `additional_kwargs` under the key the UI
    already reads — `sipoc_diagram` for a SIPOC, `visualisation` for the 5W2H
    mind map (`gateway/routes.py` reads exactly those).

    `written`, when given, is the turn's reply composed in code, and no model is
    called; `engine_timeout` marks a turn the engine's wall ended
    (`executor_timeout_handler`).
    """
    turn_count = state.get("turn_count") or 0
    plan = state.get("coaching_plan")

    # ── guard 1 of 2 — the graceful off-ramp ──────────────────────────
    remaining, off_ramp, hop_budget = _off_ramp(phase, state)

    # ── guard 2 of 2 — the three hops (ADR-0032), counted in the tools ──
    # A different unit from the one above and not substitutable for it: this
    # counts `rag_lookup_*` CALLS, `remaining_steps` counts graph-node
    # transitions. The list is the sink `_budgeted_rag_tools` mutates, read
    # back below for `step_log`.
    hops_spent: list[int] = [0]
    # T26 / G-85 (DEF-237): one line per hop, filled by the lookups and returned as `hop_results` (state).
    hop_log: list[str] = []
    # T69 — model calls made inside tools, by tool: recorded, not counted
    # against the coach's limit, capped per lookup by T51.
    tool_model_calls: dict[str, int] = {}
    fusion.TURN_TOOL_MODEL_CALLS.set(tool_model_calls)
    # G-139 (ADR-0075) — each `fields_captured` the parse normalized this turn, by shape.
    normalized: list[str] = []
    FIELDS_CAPTURED_NORMALIZED.set(normalized)

    calc_row, state = _turn_calculation(phase, state, plan)

    # ADR-0068 / ADR-0069 — the turn type, decided in code from the move and the phase state,
    # recorded in step_log; the tools it offers are the turn_tools middleware's.
    turn_type = turn_type_of(plan, state)

    # T69 / G-119 — the turn's model-call budget, and the coach's share of it.
    calls_before = 1 if plan is not None and getattr(plan, "judgment", None) is not None else 0
    coach_limit = max(1, TURN_MODEL_CALLS - calls_before - AFTER_AGENT_CALLS)

    # The skills middleware reports every delivery of the phase script here;
    # the node, which owns step_log, writes the turn's record below.
    script_log: list[dict[str, Any]] = []
    # T34 / ADR-0082 — every model attempt the retry and the fallback made, for step_log.
    attempts: list[dict[str, Any]] = []
    agent, grader_log = _build_executor(
        phase, state, config, hop_budget=hop_budget, hops_spent=hops_spent, hop_results=hop_log,
        script_log=script_log, coach_limit=coach_limit, turn_type=turn_type, attempts=attempts,
    )
    # ── the planner's routed read, executed before the model runs ─────
    # `prior` is what the agent is invoked with;
    # `state["messages"]` is what the tail slice below measures against, so the
    # dispatched exchange is returned as new messages and checkpointed with the
    # turn — which is what stops the next turn re-reading the same file.
    # T70 — composing after the engine's wall (`engine_timeout`) makes no call: the read, if any,
    # was the timed-out node's to make.
    ROUTED_READ_FAILED.set(False)
    dispatched = [] if engine_timeout else await _dispatch_routed_read(state)
    # SECTION 6 OF THE COACH'S INPUT IS ONE ENTRY PER TURN: the Belt's words and
    # the coach's reply text — no tool-call stubs, no "Returning structured
    # response" dumps. The stored conversation keeps its full shape (the
    # audit trail); only what the model is shown is cleaned. This turn's
    # dispatched read stays whole: it is this turn's evidence, not history.
    history = _conversation(list(state.get("messages") or []))
    prior = [*history, *dispatched]
    hit_cap = False
    # T70 (DEF-078) — a turn the engine's wall ended arrives here from `executor_timeout_handler`
    # with the move's code-written reply; it composes like any other turn and is recorded as
    # `partial_timeout`, the fallback marked as the defect it is.
    timed_out = engine_timeout
    filtered = False
    level_4: Optional[str] = None            # T34 level 4 (ADR-0082): "model_unavailable" or "token_limit"
    # Containment: every use of the code-written fallback is a DEFECT (the
    # coach did not finish its move) and is logged as one; the target is zero.
    fell_back = engine_timeout
    # A Change click, a status question, the goal's target, a value offered from an earlier answer and (R-C) a
    # teaching move's element card are answered in code and the coach is not called (`_written_reply`); every other
    # move is the model's to write.
    written, teaching = _written_reply(phase, state, plan, written, engine_timeout=engine_timeout,
                                       turn_type=turn_type)
    agent_started = time.monotonic()             # #63: the coach's run, the grader inside it, timed for the log
    try:
        # No time limit here (T70): the node's limit is the engine's `TimeoutPolicy`, and its
        # handler composes the answer when it fires.
        result: dict[str, Any] = {"messages": [*prior, AIMessage(content=written.message)],
                  "structured_response": written} if written is not None else \
            await agent.ainvoke(
            {"messages": prior},
            # The infinite-loop backstop, NOT the hop cap. Passed explicitly so
            # it does not depend on what the caller happened to set: an agent
            # invoked inside a node inherits the parent's LIMIT with a FRESH
            # counter, which is right when the route sets 50 and silently wrong
            # when a test or a script invokes this node directly.
            config={"recursion_limit": COACH_RECURSION_BACKSTOP},
        )
    except GraphRecursionError:
        # MUST be caught here and turned into an answer: a Belt mid-session
        # never sees a stack trace because the coach explored too broadly.
        #
        # **Belt-and-braces, not the primary guard.** The two guards above
        # off-ramp into a composed answer, so arriving here means the coach
        # burned 50 graph steps without stopping — a genuine runaway loop,
        # which is what the backstop is for.
        hit_cap = True
        result = _backstop_result(phase, plan, prior, hops_spent)
        fell_back = True
    except Exception as exc:
        # T34 level 4 (ADR-0082): the premium model and the fallback both failed through their
        # retries (a refusal or a token limit never raises here: the marker turned it into a reply).
        # A content-filter refusal raised outside the marker still answers as T92. Anything that is not
        # a model service's error is not the model's failure: it goes to the node's degraded handler.
        if not (isinstance(exc, openai.APIError) or content_safety.is_content_filter(exc)):
            raise
        filtered, level_4, result = _model_error_turn(phase, state, plan, prior, exc)
        fell_back = True
    else:
        marked = model_fallback.kept_from_fallback(list(result.get("messages") or [])) if written is None else None
        if marked is not None:
            # ADR-0082 — the marker kept a refusal (T92) or a token-limit 400 from the retry and the
            # fallback; the reply is written in code here.
            filtered = marked == model_fallback.CONTENT_FILTER
            level_4 = None if filtered else "token_limit"
            logger.warning("%s.executor: %s — kept from the fallback, answered in code (ADR-0082)", phase, marked)
            _, result = _refused_turn(phase, state, plan, prior, filtered)
            fell_back = True
    if written is None:
        turn_step("coach and grader", time.monotonic() - agent_started)

    result, produced, limited, unfinished, limit_diagnosis, fell_back = _contained_limit(
        phase, plan, result, history, coach_limit, fell_back)
    result, produced, unsourced, rejected, left_out, numbers_rejected, fell_back = _sourced_numbers(
        phase, state, plan, result, produced, history, written, fell_back)
    # A reply written in code (a Change, a status question, R-C's card) made no coach call this run; the node's own
    # routed read (`dispatched`, an upload turn) is not the coach's either (G-345).
    coach_calls = 0 if written is not None else (
        sum(1 for m in produced[len(prior):] if isinstance(m, AIMessage)) - (1 if limited else 0))
    reply: CoachingResponse | None = result.get("structured_response")
    # The agent echoes the conversation it was given and appends its own turn.
    # `messages` reduces with `operator.add`, so returning more than the tail
    # would duplicate the exchange on every turn.
    new_messages = produced[len(history):]
    # DEF-014: the re-ask's quality feedback was for the coach this turn only — never kept in the
    # conversation, where a later turn would read it (it is in step_log).
    new_messages = [m for m in new_messages if not isinstance(m, SystemMessage)]
    # DEF-135 (T60): a series is re-read at use, never stored — its values leave the turn's messages
    # here; the summary stays, and computation arguments stay as the calculation's audit.
    new_messages = _without_series_values(new_messages)

    # What the model wrote in `progress`, kept before the executor writes the
    # computed figure over it (below, after the capture merge).
    model_progress = reply.progress if reply is not None else None

    captured, citations, reply, new_messages = _shaped_reply(
        phase, state, plan, reply, new_messages, turn_type, written,
        fell_back=fell_back, filtered=filtered, level_4=level_4, card=teaching is not None)

    uploads, routed = _consumed_uploads(state, produced, citations, turn_type)

    _attach_diagram(new_messages)
    _attach_sources(new_messages)

    # ── the accumulation ──────────────────────────────────────────────
    #
    # `state["artifacts"]` is the phase's whole capture history, seeded by the
    # input mapper from the case record rather than blanked (G-78). An EMPTY
    # capture never overwrites a real prior value (`split_captures`, below): a
    # `None` merged over a prior value would destroy what the gate document
    # reads while the case record kept it, and the two records of one field
    # would disagree, silently, in the direction that loses data.
    prior_artifacts = dict(state.get("artifacts") or {})

    # ── NOTHING IS STORED BEFORE THE BELT CONFIRMS ────────────────────
    #
    # *"A value is stored only after the Belt confirms it, in the Belt's
    # words; a tidied version may be proposed in the read-back and is stored
    # only if the Belt confirms it."* So what reaches
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
    move, pending, candidate, not_stored = _store_candidate(phase, plan, captured)
    kept, empty_captures, malformed, example_refused, belt_own = _refused_captures(
        phase, state, candidate, prior_artifacts)

    kept, pending, carried, link, located_line, copied, short, unfilled = _read_back_pending(
        phase, state, plan, move, pending, kept, prior_artifacts, belt_own, reply)
    artifacts = {**prior_artifacts, **kept}

    field_status, refused = _turn_field_status(
        phase, state, plan, move, pending, captured, prior_artifacts, filtered, level_4)
    field_status, resend, sample_challenge, link_challenge = _read_back_outcome(
        phase, state, plan, move, pending, field_status, refused=refused, fell_back=fell_back,
        short=short, unfilled=unfilled, link=link)

    # The field change log, built from the SAME `kept` the merge above uses,
    # so the log and the accumulator cannot disagree about what changed.
    turn_ordinal = _turn_ordinal(state)
    log_entries = _field_log_entries(
        phase, turn_ordinal, kept, prior_artifacts, reply,
        utc_now().isoformat(),
        pending=(plan.confirmed if plan is not None and move == moves.STORE_AND_ADVANCE else None),
        by=((config or {}).get("configurable") or {}).get("current_user"),
    )

    # ── the write paths for what the gate document and the planner read:
    #    this turn's computation results, and the field index.
    results = _computation_results(produced, phase, turn_count)
    if results:
        artifacts["computation_results"] = [
            *(artifacts.get("computation_results") or []), *results,
        ]
    next_field = _advance_field_index(phase, artifacts)

    # ── the Belt's progress is the COMPUTED one, in the reply the turn keeps
    # The model's own count is not trusted, even with the figure in its input:
    # the reply's `progress` is WRITTEN, on every turn, from the same function
    # the injection block delivers from (`define_progress`), and the
    # structured-response message the NEXT turn reads is re-rendered with it.
    # What the model wrote is kept in step_log below.
    #
    # **From the artifacts AFTER this turn's capture**, not the turn-start
    # ones the block was composed from: the reply is read after the turn, so a
    # figure computed before the capture would lag one element on every
    # capture turn.
    define_step = define_progress(artifacts) if phase == "define" else None
    delivered = (define_progress(prior_artifacts)["label"]
                 if define_step is not None else None)
    if define_step is not None and reply is not None:
        new_messages = _with_progress(new_messages, reply, define_step["label"])

    # G-117 (DEF-156) — what was stored is said by code, from `kept`, never by the model.
    # G-185: the Belt's own words are never taken for a store claim — everything the Belt wrote.
    belt_words = chr(10).join([*(m.text for m in (state.get("messages") or []) if isinstance(m, HumanMessage)),
                               str(plan.answer or "") if plan else ""])
    if teaching is None:
        # R-C: on a card turn the card's saved note says what the Confirm stored — never a second "Stored: …" line.
        new_messages = _store_truth(new_messages, reply, phase, plan,
                                    kept if move == moves.STORE_AND_ADVANCE else {}, belt_words)
    new_messages = _with_carried(new_messages, reply, phase, carried)
    new_messages = _with_define_read_back_lines(phase, move, pending, new_messages, reply)
    _attach_visual(phase, plan, move, pending, prior_artifacts, kept, new_messages)

    # ── the four blocks and the grader's warning ride on the reply ────
    # The route never holds the `CoachingResponse`, only the graph's
    # messages, so this is the one place the blocks can be put where it reads.
    # After the progress write above, so `progress` is the computed figure.
    # The warning is the grader's own text (`GRADER_WARNING`) whenever its
    # verdict this turn FAILED and the grader enforces — the dict its
    # `after_agent` returns reaches no reader (G-76, G-103).
    failed = any(e.get("status") == "failed" for e in grader_log)
    new_messages, reply = _code_written_reply(
        phase, state, plan, move, pending, reply, new_messages, resend=resend,
        sample_challenge=sample_challenge, link_challenge=link_challenge, link=link, refused=refused,
        copied=copied, short=short, unfilled=unfilled, prior_artifacts=prior_artifacts)
    new_messages, reply, masked = _with_turn_lines(
        new_messages, reply, produced, history, located_line=located_line, move=move, pending=pending,
        belt_words=belt_words, written=written, resend=resend, refused=refused, fell_back=fell_back,
        sample_challenge=sample_challenge, link_challenge=link_challenge)
    reply = _with_sample_mark(reply)            # C3 (DEF-083)
    # The grader's warning reaches the Belt only in `enforce` mode.
    _attach_blocks(new_messages, reply,
                   GRADER_WARNING if failed and grader_mode.GRADER_MODE == "enforce" else None)
    if (level_4 and level_4 != "token_limit" and not filtered) or resend:
        # R-F (founder ruling 2026-10-27): both models failed (T34 level 4) or the read-back could not be used
        # (G-140) — a failed turn, marked as T29's handler marks one, so the route retries it once and the page
        # shows Send again with the message back in the box; its words never ask the Belt to send it again. A
        # token limit is not retried: the same call would fail the same way (§4.8).
        last = next((m for m in reversed(new_messages) if isinstance(m, AIMessage)), None)
        if last is not None:
            last.additional_kwargs["degraded"] = {"node": "executor", "error": level_4 or "resend"}

    # ── the move record and the quality feedback ride on the reply ────
    # The next turn's planner reads the record (status, answer, PENDING); the
    # next turn's coach reads the feedback as section 4 of its input — never as
    # a message from the Belt. Attached even when the turn degraded, so a
    # confirmed value the plan stored is not taught again.
    record = _turn_move_record(
        plan, move, pending, kept, refused=refused, level_4=level_4, resend=resend,
        sample_challenge=sample_challenge, link_challenge=link_challenge, short=short, unfilled=unfilled,
        copied=copied, link=link)
    _record_fallback(phase, move, record, limit_diagnosis, fell_back=fell_back, timed_out=timed_out,
                     filtered=filtered, level_4=level_4, limited=limited, unfinished=unfinished,
                     numbers_rejected=numbers_rejected)
    feedback = _quality_feedback(grader_log)
    new_messages, reply, completion = _define_completion(phase, plan, record, new_messages, reply, fell_back)
    _attach_move(new_messages, record, feedback)
    # DEF-265: the case's lead and people, so the team read-back draws the Gate's table.
    case = ((config or {}).get("configurable") or {}).get("case_metadata")
    card, strip = _element_card(phase, record, artifacts, plan, case, kept if move == moves.STORE_AND_ADVANCE else {})
    if card is None and sample_challenge and short and plan is not None:
        card = _short_card(phase, plan.focus_field, pending, artifacts, case)
    _attach_card(new_messages, card, _with_teaching_card(new_messages, teaching, strip), _reply_element(phase, record))
    _with_link_check(new_messages, phase, pending, prior_artifacts, link_challenge)          # R-H
    if completion is not None:
        next(m for m in reversed(new_messages) if isinstance(m, AIMessage)).additional_kwargs[COMPLETION_KEY] = completion

    # **The counts reconcile with the write**: the KEYS the coach named
    # (`captured`) against what reached `artifacts`, what was not stored and
    # what changed — "captured" alone would not say whether anything reached
    # the gate document.
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
    mark_answered(time.time())     # R-F: the answer exists — the route never cancels this turn's save from here
    return {
        "messages": new_messages,
        # T26 / G-85 (DEF-237): what each hop returned, state rather than a node local.
        "hop_results": list(hop_log),
        # `draft` is what THIS turn stored, `artifacts` the accumulation.
        # Neither field carries a reducer, so the merge happens here or not at
        # all. **`kept`, never `captured`** — the route writes `draft` into the
        # case record, so a value the coach returned but the Belt has not
        # confirmed must not be in it.
        # ADR-0077: a calculation run this turn reaches the record now — it is not a Belt value
        # awaiting confirmation, and the record only keeps what `draft` carries.
        "draft": ({**kept, "computation_results": artifacts.get("computation_results") or []}
                  if calc_row is not None else dict(kept)),
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
            phase, turn_count, "executor", rejections=_rejections(state),
            status=_executor_status(hit_cap, off_ramp, timed_out, filtered, level_4),
            model_attempts=attempts or None,                     # T34 / ADR-0082
            unsourced_numbers=unsourced or None,                 # G-173 (ADR-0077)
            rejected_reply=rejected,                             # G-173: what the coach wrote
            numbers_left_out=left_out or None,                   # G-173: the sentences a kept reply lost
            fallback_used=fell_back,
            limit=limit_diagnosis,                                 # G-139
            resend=resend,                                         # G-140
            impl="create_agent",
            turn_type=turn_type,                                   # ADR-0068
            # G-139 (ADR-0075) — every normalization: the turn, the element, which shape.
            fields_captured_normalized=[{"turn": turn_ordinal, "element": plan.focus_field if plan else None,
                                         "shape": s} for s in normalized],
            # ADR-0074 point 5 — on an upload turn: the file, the element and each criterion's result.
            upload_check=({"file": routed.get("filename"), "element": (routed.get("element_check") or {}).get("element"),
                           "criteria": [{"criterion": c.get("criterion"), "result": c.get("result")}
                                        for c in (routed.get("element_check") or {}).get("criteria") or []]}
                          if routed is not None else None),
            # T87 — personal data redacted in this turn's tool results, by type and count.
            pii_masked=masked,
            # T69 / G-119 — the turn's model calls against its budget (after-agent calls: one grader pass).
            call_budget={"budget": TURN_MODEL_CALLS, "planner": calls_before, "coach": coach_calls,
                         "coach_limit": coach_limit, "after": min(len(grader_log), 1),
                         # F (founder ruling 2026-10-27, F6): a rewritten turn's coach and grader calls, outside the four
                         "rewrite": 2 if any(e.get("rewritten") for e in grader_log) else 0,
                         "turn": calls_before + coach_calls + min(len(grader_log), 1),
                         "limited": limited},
            tool_model_calls=dict(sorted(tool_model_calls.items())),   # T69: inside tools, by tool
            focus_field=plan.focus_field if plan else None,
            # The move code chose, the field's status, and what this turn
            # stored or holds as pending.
            move=plan.move if plan else None,
            field_status=plan.status if plan else None,
            stored_field=plan.stored_field if plan else None,
            fields_stored=sorted(kept),
            pending=((record or {}).get("pending") or {}).get("field"),
            pending_value=((record or {}).get("pending") or {}).get("store"),
            fields_not_stored=not_stored,
            fields_captured=sorted(captured),
            # What the coach named and what the record now holds, in the audit
            # trail rather than only in a log line. `fields_empty` is "reported
            # rather than silently dropped" made queryable: `len(fields_captured)`
            # and `len(fields_empty)` are what reconcile a turn's log against
            # its write.
            fields_empty=empty_captures,
            # Named with the type each needed, so the audit trail can
            # answer "why is this field still blank on turn nine" without a
            # re-run. `fields_captured` minus `fields_empty` minus this is what
            # actually reached `artifacts`.
            fields_malformed=dict(sorted(malformed.items())),
            # The worked-example refusals, by field.
            fields_example_refused=example_refused,
            fields_changed=sorted(e["field"] for e in log_entries),
            # Re-derived from the SAME function that built the bound list,
            # so the audit trail cannot disagree with what the coach actually
            # had. The throwaway counter is never spent — nothing invokes
            # these copies; only `len()` is read.
            tools_bound=len(_executor_tools(phase, hop_budget, None)),
            # The hop cap and the off-ramp, both readable in LangSmith. Hitting
            # the cap is a monitoring signal, and a signal nobody can read is
            # not one.
            hops_spent=hops_spent[0],
            hop_budget=hop_budget,
            # What the NODE called (`_dispatch_routed_read`), as against what
            # the model chose. Empty on every turn with no unread routed
            # upload, which is most of them.
            dispatched=[
                c["name"] for m in dispatched
                for c in (getattr(m, "tool_calls", None) or [])
            ],
            remaining_steps=remaining or None,
            # For the audit trail; `ContradictionDetectionMiddleware` reads the
            # reply's flag during the turn.
            contradiction_flag=_flag_of(reply),
            # ADR-0112: the Belt confirmed an answer it was told does not fit — kept, dated by this entry.
            mismatch_kept=(_mismatch_kept_note(phase, plan) if move == moves.STORE_AND_ADVANCE else None),
        ), *(
            # Each grading the grader's `on_evaluation` sink collected, written
            # to `step_log`, so a verdict outlives the turn (capability row 13).
            # One grading per reply; the iteration goes into the key should
            # there ever be more.
            _step(phase, turn_count,
                  "coaching_grader" if int(e.get("iteration") or 1) == 1
                  else f"coaching_grader:{e['iteration']}", rejections=_rejections(state), **e)
            for e in grader_log
        ),
            # The coach's input as it was sent: the six sections, in order, read
            # off the system message the model received (the skills middleware
            # sees it last), with the move and the field.
            _step(phase, turn_count, "coach_input", rejections=_rejections(state),
                  sections=list((script_log[0] if script_log else {}).get("sections") or []),
                  move=plan.move if plan else None,
                  field=plan.focus_field if plan else None),
            # Did this turn's model calls carry the phase script? One entry per
            # turn, `delivered` false when no call did: a turn coached without
            # its method is distinguishable in the record.
            _step(phase, turn_count, "coaching_script", rejections=_rejections(state),
                  **{k: v for k, v in (script_log[0] if script_log else script_record(phase)).items()
                     if k != "sections"},
                  delivered=bool(script_log), model_calls=len(script_log)),
            # The progress the reply carries (after the capture), the one the
            # coach was DELIVERED (turn start), and what the model wrote in
            # `progress`. A model that counted for itself is on the record, not
            # only on the screen.
            *([_step(phase, turn_count, "define_position", rejections=_rejections(state), **define_step,
                     delivered_label=delivered,
                     reply_progress=model_progress,
                     reply_matches=model_progress == define_step["label"],
                     progress_written=reply.progress if reply else None)]
              if define_step is not None else []),
        ],
    }


def executor_timeout_handler(phase: str, goto: str = "planner") -> Any:
    """T70 (DEF-078): the executor node's `error_handler=`. LangGraph runs it when the node fails;
    on the engine's `TimeoutPolicy` (`NodeTimeoutError`) it composes the turn with the move's own
    reply, written in code (`_fallback_reply`), through the executor itself — so a timed-out turn
    stores, records and answers exactly as a finished one, marked `partial_timeout` — and routes on
    to the planner. Any other failure is raised. (A closure, not a class.)"""
    from langgraph.errors import NodeError, NodeTimeoutError

    async def executor_timed_out(state: PhaseState, error: NodeError,
                                 config: RunnableConfig) -> Command:
        if not isinstance(error.error, NodeTimeoutError):
            raise error.error
        logger.warning(
            "%s.executor: the engine's %.0fs wall ended the node (T70, G-84) — composing the "
            "move's own reply in code; recorded as partial_timeout", phase, EXECUTOR_RUN_TIMEOUT)
        update = await executor(phase, state, config,
                                written=_fallback_reply(phase, state.get("coaching_plan")),
                                engine_timeout=True)
        return Command(update=update, goto=goto)

    return executor_timed_out


# ── validation_stack ──────────────────────────────────────────────────────

def _criterion_element(criterion: str) -> str:
    """G-194 — the Define element a rubric criterion judges, by its name (the criterion id when unknown)."""
    from backend.core import guard_messages
    from backend.validation.rubric import DEFINE_CRITERIA
    field = next((f for cid, f, _ in DEFINE_CRITERIA if cid == criterion), "")
    position = {f: pos for pos, fields in moves.positions("define") for f in fields}.get(field, field)
    return guard_messages.element_name("define", position) if position else criterion


def submission_fingerprint(state: PhaseState) -> str:
    """G-192 (ADR-0076) — what a gate submission submitted: the phase's captured values and where
    each element stands. Two submissions with the same fingerprint changed nothing between them."""
    statuses = {f: (v or {}).get("status") for f, v in (state.get("field_status") or {}).items()}
    body = json.dumps({"artifacts": state.get("artifacts") or {}, "status": statuses},
                      sort_keys=True, default=str)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


async def validation_stack(
    phase: str,
    state: PhaseState,
    config: Optional[RunnableConfig] = None,
) -> Command[Literal["planner", "gate_review"]]:
    """The validation layers at the gate, sharing a cap of 3: layer 2b, field
    presence (deterministic, `validate_{phase}`), then for Define layer 2d, the
    rubric (`grade_define`) — cheapest first, each firing only if the previous
    passed. Layer 2c (constraints) does not run here. **Layer 2a is gone** — the
    coherence judge on `after_agent` is retired (ADR-0083); this node runs
    once, at the gate.

    **It runs the validators only on a gate submission.** A coaching turn walks
    through here on its way out and must NOT be validated: a failed validation
    counts a gate attempt, so validating every coaching turn would burn the
    shared cap of 3 in three turns and escalate a Belt who is simply still
    typing. It is worth stating because the node is on the path either way.

    Layer 2b is `gate_registry.check_gate` on the phase's own draft. `gate_attempts` lives on `PhaseState` and is
    carried
    across turns by the phase record: a pass resets it, a resubmission that
    changed nothing (`submission_fingerprint`) keeps it, and the third counted
    failure escalates.
    """
    turn_count = state.get("turn_count") or 0
    entry = entry_mode(config)

    # **Reads the per-run intent, not the plan.** The plan carries the coaching
    # move, never a routing verb, and the planner produces no plan on this
    # path. `entry_mode` is the same source the planner routes from, which is
    # what keeps the two nodes from disagreeing about what kind of turn this is.
    if entry != "gate":
        logger.info("%s.validation_stack: pass-through (coaching turn)", phase)
        return Command(
            goto="gate_review",
            update={"step_log": [_step(
                phase, turn_count, "validation_stack", rejections=_rejections(state),
                status="passthrough", entry=entry,
                reason="not a gate submission — layers 2c/2d land at stage 7",
            )]},
        )

    result = check_gate(phase, dict(state.get("draft") or {}), int(state.get("gate_attempts") or 0))
    passed, missing = bool(result["passed"]), list(result["missing"])
    attempts, escalated = int(result["attempts"]), bool(result["escalated"])

    logger.info(
        "%s.validation_stack: layer 2b %s (missing=%d, attempts=%d)",
        phase, "PASSED" if passed else "FAILED", len(missing), attempts,
    )
    feedback = [{
        "key": step_key(phase, turn_count, "validation_stack"),
        "layer": "2b",
        "impl": "gate_registry.check_gate",
        "passed": passed,
        "missing": missing,
        "attempts": attempts,
        "escalated": escalated,
    }]
    # ── Layer 2d — the R7 rubric, Define only, and only on a 2b pass ──────
    # (cheapest first). One verdict per element, pass/fail with the
    # reason; a failure never reaches `gate_review`'s pause — the report goes
    # back to coaching with the failed criteria named. Shares the cap of 3.
    kept_status: Optional[dict[str, dict[str, Any]]] = None
    if passed and phase == "define":
        # DEF-224 (G-225): the verdicts kept per element from earlier submissions; an unchanged answer keeps its
        # verdict with no model call, and this submission's model verdicts are kept beside the elements they judged.
        from backend.validation.rubric import kept_verdicts as gate_kept
        status_now = {f: dict(v) for f, v in (state.get("field_status") or {}).items()}
        held = {cid: v for entry in status_now.values() for cid, v in (entry.get("gate") or {}).items()}
        artifacts = dict(state.get("artifacts") or {})
        verdict = await grade_define(artifacts, kept=held)
        for cid, v in gate_kept(artifacts, verdict).items():
            status_now.setdefault(v["field"], {}).setdefault("gate", {})[cid] = v
        kept_status = status_now
        failed = [{"criterion": v.criterion, "feedback": v.feedback} for v in verdict.failed]
        if failed:
            attempts = int(state.get("gate_attempts") or 0) + 1
            escalated = gate_escalates(attempts)
        passed = not failed
        feedback.append({
            "key": step_key(phase, turn_count, "validation_stack") + ":2d",
            "layer": "2d", "impl": "DEFINE_RUBRIC", "passed": passed,
            "missing": [f"{f['criterion']} — {f['feedback']}" for f in failed],
            "verdicts": [v.model_dump() for v in verdict.verdicts],
            "attempts": attempts, "escalated": escalated,
        })
        logger.info("%s.validation_stack: layer 2d %s (%d of %d criteria failed)%s", phase,
                    "PASSED" if passed else "FAILED", len(failed), len(verdict.verdicts),
                    # G-194: which criterion, on which element, and why — never a count alone.
                    "".join(f"; {f['criterion']} on {_criterion_element(f['criterion'])}: {f['feedback']}"
                            for f in failed))
    # ADR-0076 (T65, G-150): the count is the phase record's, carried across turns; a pass resets it,
    # and the third failure escalates — the route tells the Belt and marks the case for the lead.
    # G-192: only a submission that changed something counts — the same one again keeps the count.
    fingerprint = submission_fingerprint(state)
    if passed:
        attempts, escalated, fingerprint = 0, False, ""
    elif fingerprint == (state.get("gate_fingerprint") or ""):
        attempts, escalated = int(state.get("gate_attempts") or 0), False
        logger.info("%s.validation_stack: unchanged since the last failed submission — not counted "
                    "(attempts=%d)", phase, attempts)
    else:
        escalated = gate_escalates(attempts)
    feedback[-1] = {**feedback[-1], "attempts": attempts, "escalated": escalated,
                    "gate_fingerprint": fingerprint}
    return Command(
        goto="gate_review",
        update={
            "gate_attempts": attempts,
            "gate_fingerprint": fingerprint,
            # This submission's layer verdicts. The field carries no reducer, so
            # they replace the previous submission's; `gate_apply` clears them.
            "validator_feedback": feedback,
            "step_log": [_step(
                phase, turn_count, "validation_stack", rejections=_rejections(state),
                status="validated_v1", layer="2b",
                passed=passed, missing=len(missing), attempts=attempts,
            )],
            **({"field_status": kept_status} if kept_status is not None else {}),     # DEF-224
        },
    )


# ── gate_review ───────────────────────────────────────────────────────────

#: R6 (docs/requirements/business.md) — the Belt's decision on the Define
#: report, delivered by `Command(resume=...)` to the pause below.
APPROVE, REJECT = "approve", "reject"


def _gate_passage(phase: str, state: PhaseState) -> Optional[dict[str, Any]]:
    """The gate submission this run is on — the validation stack's latest
    entry, when it PASSED — for the one phase with a report to accept (R6).
    `validator_feedback` carries no reducer, so `gate_apply` closes a passage by
    clearing it, and a later pass through `gate_review` in the same run (the
    coaching turn after a rejection) finds none and does not pause again."""
    if phase != "define":
        return None
    feedback = [f for f in (state.get("validator_feedback") or []) if isinstance(f, dict)]
    return feedback[-1] if feedback and feedback[-1].get("passed") else None


def _decision(value: Any) -> dict[str, Any]:
    """The resume value, normalised: approve or reject, the element(s) to
    change, the reason, the actor (until R8 the Belt), when."""
    v = dict(value or {}) if isinstance(value, dict) else {"decision": str(value or "")}
    decision = str(v.get("decision") or "").strip().lower()
    return {"decision": decision if decision in (APPROVE, REJECT) else REJECT,
            "elements": [str(e) for e in (v.get("elements") or [])],
            "reason": str(v.get("reason") or "").strip(),
            "actor": str(v.get("actor") or ""),
            "at": str(v.get("at") or utc_now().isoformat())}


async def gate_review(phase: str, state: PhaseState) -> dict[str, Any]:
    """Present the validated Define report and STOP — the graph-level pause.

    **R6: formal acceptance, human in the loop.** When the Define gate has
    passed validation this calls `interrupt()` — a graph-level pause, never
    `HumanInTheLoopMiddleware` (two confirmed bugs on this use case). The
    parent graph carries the checkpointer, so the pause is persisted (the
    interrupt and the resume are PENDING WRITES, `AzureBlobCheckpointSaver.
    put_writes`) and survives between the two requests: `POST /gate` pauses
    here; `POST /gate/decision` resumes with `Command(resume=...)`.

    **On resume this node re-runs from its start** (LangGraph: a resumed node
    restarts; verified against 1.2.11 for a subgraph invoked inside the parent
    node — the subgraph resumes HERE, its earlier nodes do not re-run), so
    nothing before the `interrupt()` has a side effect. The decision is written
    to `step_log`, where `gate_apply` reads it.

    Every other turn, and every other phase until its report exists, passes
    through.
    """
    turn = state.get("turn_count") or 0
    passage = _gate_passage(phase, state)
    if passage is None:
        return {"step_log": [_step(
            phase, turn, "gate_review", status="passthrough", rejections=_rejections(state),
            reason="no validated gate submission to review")]}
    value = interrupt({"kind": "accept_define_report", "phase": phase,
                       "passage": passage.get("key"),
                       "ask": "Approve the Define report, or reject it naming the "
                              "element(s) to change and why."})
    decision = _decision(value)
    logger.info("%s.gate_review: the Define report was %sd by %s",
                phase, decision["decision"], decision["actor"] or "the Belt")
    return {"step_log": [_step(phase, turn, "gate_review", status="decided", rejections=_rejections(state),
                               passage=passage.get("key"), **decision)]}


# ── gate_apply ────────────────────────────────────────────────────────────

def _decided(state: PhaseState) -> Optional[dict[str, Any]]:
    """The decision `gate_review` recorded on this run, if any."""
    for entry in reversed(state.get("step_log") or []):
        if isinstance(entry, dict) and entry.get("node") == "gate_review":
            return entry if entry.get("status") == "decided" else None
    return None


async def gate_apply(
    phase: str, state: PhaseState
) -> Command[Literal["planner", "__end__"]]:
    """Apply the Belt's decision on the Define report, and route on (R6).

    **`policy_advisory` is a BANNED node name**: any advisory belongs in this
    node's logic, never in a node of its own.

    APPROVE -> `final` = the gate document, assembled deterministically from
    the confirmed values (no model call); `gate_attempts` and
    `validator_feedback` reset; END. The case blob write and the phase advance
    stay the route's, after the resumed graph returns.

    REJECT -> the element(s) the team named are RE-OPENED: status back to
    `asked`, the Belt's current words kept as the answer so far, and the
    reason on the entry; the reason goes to `rejection_feedback`; the passage
    closes; and control goes to the PLANNER, whose move on the first re-opened
    element is a challenge naming the team's reason — the coach guides the Belt
    back in the same run. Every value keeps its dated history (`field_log`):
    the re-confirmation writes a new entry with the value it replaces.

    Anything else — a coaching turn, another phase — passes through to END.
    """
    turn = state.get("turn_count") or 0
    decision = _decided(state) if _gate_passage(phase, state) is not None else None
    if decision is None:
        return Command(
            goto=cast(Literal["planner", "__end__"], END),
            update={"step_log": [_step(phase, turn, "gate_apply", status="passthrough", rejections=_rejections(state),
                                       reason="no decision on a gate submission")]},
        )
    artifacts = dict(state.get("artifacts") or {})
    if decision["decision"] == APPROVE:
        # G-242: a gate document that cannot be assembled RAISES — never an empty `final`, which the approval
        # node would write over the case record's values and advance on.
        final: dict[str, Any] = GATE_SPECS[phase].assemble(
            artifacts, list(state.get("citations") or []),
            list(state.get("uploads") or []), []).model_dump()
        return Command(
            goto=cast(Literal["planner", "__end__"], END),
            update={"final": {**final, "_approved": {k: decision[k] for k in ("actor", "at")}},
                    "gate_attempts": 0, "validator_feedback": [],
                    "step_log": [_step(phase, turn, "gate_apply", status="approved", rejections=_rejections(state),
                                       actor=decision["actor"], at=decision["at"])]},
        )
    from backend.phases.define.templates import plain        # G-260
    elements = [e for e in decision["elements"] if e in DEFINE_FIELD_ORDER]
    field_status = {f: dict(v) for f, v in (state.get("field_status") or {}).items()}
    for element in elements:
        field_status[element] = {
            "status": moves.ASKED, "answer": plain(artifacts.get(element)), "messages": 1,
            "rejected": {k: decision[k] for k in ("reason", "actor", "at")}}
    return Command(
        goto="planner",
        update={"field_status": field_status, "validator_feedback": [], "turn_count": 0,
                "rejection_feedback": [*(state.get("rejection_feedback") or []),
                                       {**decision, "elements": elements}],
                "step_log": [_step(phase, turn, "gate_apply", status="rejected", rejections=_rejections(state),
                                   reopened=elements, reason=decision["reason"],
                                   actor=decision["actor"])]},
    )


__all__ = [
    "NODE_NAMES",
    "step_key",
    "entry_mode",
    "planner",
    "executor",
    "validation_stack",
    "gate_review",
    "gate_apply",
]
