"""R3 — every Belt answer passes a validation layer BEFORE the coach model.

Founder requirement R3 (`docs/requirements/define.md`, 2026-09-26): *"Every
Belt answer passes a validation layer BEFORE it reaches the coach model,
checking it is reasonable against the element's acceptance criteria;
insufficient -> challenge, naming the failed criterion."*

WHERE IT LIVES — the planner's one judgment, not a before-model middleware.
`moves.decide` (called by the planner node's `_plan_turn`) asks `_judge` for a
`SufficiencyJudgment` against the element's acceptance criteria, parsed from
its SKILL.md block (`skills.acceptance_criteria`). The planner node runs before
the executor node (`START -> planner -> executor`), and the coach model lives
only inside the executor's agent — so the judgment is made, and the move
decided, before the coach model is called. A middleware on the coach's agent
would run INSIDE the executor, after the move was already decided; the
planner is the earlier and the only place the move can still change.

WHAT IS AN ANSWER — proven exhaustively below: any Belt text on a field that
was asked, or a qualified reply to a read-back. NOT an answer, and so not
judged: the Belt's message on a field not yet taught (the field has not been
asked), a plain typed yes to a read-back (a confirmation), a Confirm or Change
click (no text at all).

The repeated-run half (the live model, five runs each) is
`test_define_runthrough.py::test_run_the_validation_layer_is_consistent_over_five_runs`,
reading the record `scripts/validation_repeat.py` writes — kept with the
run-through's tests because it goes stale the same way, on any product change.
"""
from __future__ import annotations

import asyncio
from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from backend.core.substate import CoachingResponse, PhaseState, SufficiencyJudgment
from backend.middleware.skills import acceptance_criteria, field_needs
from backend.phases import moves
from backend.phases import nodes_common as _nc
from backend.phases.define.schema import DEFINE_FIELD_ORDER
from backend.phases.subgraph_common import build_phase_subgraph

ANSWER = ("Late supplier payments cost us about £62,000 last year in interest and lost "
          "discounts, across our three sites, January to June 2026, 23% of invoices.")
PENDING = {"business_case": {
    "status": "answered", "answer": ANSWER, "messages": 1,
    "pending": {"field": "business_case", "fields": ["business_case"],
                "belt_words": ANSWER, "messages": 1, "store": {"business_case": ANSWER}}}}
ASKED = {"business_case": {"status": "asked"}}


class Judge:
    """The planner model's judgment, faked and counted."""

    def __init__(self, verdict: str = "sufficient", crit: str | None = None) -> None:
        self.verdict, self.crit = verdict, crit
        self.calls: list[str] = []

    async def __call__(self, field: str, previous: str, latest: str,
                       reading_back: str) -> SufficiencyJudgment:
        self.calls.append(latest)
        return SufficiencyJudgment(verdict=self.verdict, reason="r",  # type: ignore[arg-type]
                                   failed_criterion=self.crit)


def _decide(status: dict, belt: str, judge: Judge, action: str | None = None) -> dict[str, Any]:
    return asyncio.run(moves.decide("define", {}, dict(status), belt, judge, action=action))


# ── every answer is judged; nothing else is ─────────────────────────────────


@pytest.mark.parametrize("status,belt,action,judged", [
    (ASKED, ANSWER, None, True),                                   # an answer
    (ASKED, "Where do we stand?", None, True),                      # judged -> not_an_answer
    (ASKED, "yes", None, True),                                     # "yes" to a QUESTION is an answer
    (PENDING, "Yes, but add the cost of the supplier stops.", None, True),  # a qualified reply
    (PENDING, "What does baseline mean?", None, True),              # a question at a read-back
    ({}, "Hi — ready to start.", None, False),                      # not taught: nothing asked yet
    (PENDING, "Yes, that's right.", None, False),                   # a confirmation, not an answer
    (PENDING, "", "confirm", False),                                # a click carries no text
    (PENDING, "", "change", False),
])
def test_every_belt_answer_is_judged_and_nothing_else_is(status, belt, action, judged) -> None:
    judge = Judge()
    _decide(status, belt, judge, action)
    assert len(judge.calls) == (1 if judged else 0), (belt, action, judge.calls)


def test_insufficient_is_a_challenge_that_names_the_failed_criterion() -> None:
    d = _decide(ASKED, ANSWER, Judge("insufficient", "no-cause-no-fix"))
    assert d["move"] == moves.CHALLENGE
    assert "`no-cause-no-fix`" in d["reason"], d["reason"]
    assert d["judgment"].failed_criterion == "no-cause-no-fix"


def test_sufficient_is_a_read_back_and_stores_nothing() -> None:
    d = _decide(ASKED, ANSWER, Judge("sufficient"))
    assert d["move"] == moves.READ_BACK and d["store"] == {}


# ── the yardstick: the element's acceptance criteria ────────────────────────


def test_every_define_element_has_acceptance_criteria() -> None:
    for field in DEFINE_FIELD_ORDER:
        ids = [cid for cid, _ in acceptance_criteria("define", field)]
        assert ids, f"{field} has no acceptance criteria in its SKILL.md block"
        assert len(ids) == len(set(ids)), (field, ids)


def test_the_business_case_criteria_are_r7s_five_and_no_speculation() -> None:
    ids = [cid for cid, _ in acceptance_criteria("define", "business_case")]
    assert ids == ["what", "where-when", "baseline", "cost", "no-cause-no-fix"]


def test_the_judge_reads_the_criteria_and_never_a_demo() -> None:
    """The SIPOC's needs carry its criteria and not its demo table — until R3
    the table rows reached the judge."""
    needs = field_needs("define", "process_map_sipoc")
    assert "`as-is`" in needs and "`all-six`" in needs
    assert "| Suppliers |" not in needs and "Sales team" not in needs
    assert "`5w2h`" in field_needs("define", "problem_5w2h"), "an inside field reads its position's"


@pytest.mark.parametrize("named,reason,expected", [
    ("no-cause-no-fix", "proposes a fix", "no-cause-no-fix"),
    ("`COST`", "no money figure", "cost"),                   # normalised
    ("money", "the `cost` criterion is not met", "cost"),    # not listed -> the id the reason quotes
    ("money", "what is missing is the cost", None),          # a bare word is prose, never an id
    ("money", "vague", None),                                # not listed, not quoted -> cleared
])
def test_the_named_criterion_is_checked_against_the_elements_list(named, reason, expected) -> None:
    j = SufficiencyJudgment(verdict="insufficient", reason=reason, failed_criterion=named)
    assert _nc._checked_criterion("define", "business_case", j).failed_criterion == expected


def test_only_insufficient_carries_a_criterion() -> None:
    j = SufficiencyJudgment(verdict="sufficient", reason="ok", failed_criterion="cost")
    assert _nc._checked_criterion("define", "business_case", j).failed_criterion is None


# ── the order, in the real compiled graph: judged BEFORE the coach model ────


def _state(field_status: dict, belt: str) -> PhaseState:
    msgs: list = [HumanMessage(content="Hi"), AIMessage(content="What is your business case?")]
    if belt:
        msgs.append(HumanMessage(content=belt))
    return {  # type: ignore[typeddict-item]
        "case_id": "IMPR-TEST-R3", "current_phase": "define", "messages": msgs,
        "history": [], "phase_context": "framing", "coaching_plan": None, "field_index": 0,
        "draft": {}, "artifacts": {}, "step_log": [], "field_log": [],
        "field_status": field_status, "belt_edits": {}, "turn_count": 0, "final": {},
        "gate_attempts": 0, "validator_feedback": [], "rejection_feedback": [],
        "citations": [], "uploads": [], "asks": [], "hop_results": [],
        "synthesis_output": None,
    }


@pytest.fixture
def order(monkeypatch, stub_planner, stub_coach) -> list[str]:
    """The order of model calls in one turn: the planner's judgment, the coach."""
    calls: list[str] = []
    real_judge = _nc._judge

    async def judge(*a: Any, **k: Any) -> SufficiencyJudgment:
        calls.append("judgment")
        return await real_judge(*a, **k)

    make_agent = _nc.create_agent

    class _Ordered:
        def __init__(self, agent: Any) -> None:
            self._agent = agent

        async def ainvoke(self, *a: Any, **k: Any) -> Any:
            calls.append("coach")
            return await self._agent.ainvoke(*a, **k)

    monkeypatch.setattr(_nc, "_judge", judge)
    monkeypatch.setattr(_nc, "create_agent", lambda **kw: _Ordered(make_agent(**kw)))
    stub_coach.reply = CoachingResponse(explanation="e", example="x", prompt="p",
                                        progress="p", message="m")
    return calls


@pytest.mark.parametrize("status,belt,action,expected", [
    (ASKED, ANSWER, None, ["judgment", "coach"]),       # an answer: judged, then coached
    (PENDING, "Yes, that's right.", None, ["coach"]),   # a confirmation: no judgment
    ({}, "Hi — ready.", None, ["coach"]),               # a field not yet taught
])
def test_in_the_graph_the_answer_is_judged_before_the_coach_model(order, status, belt, action,
                                                                    expected) -> None:
    graph = build_phase_subgraph("define", llm=None)
    config = {"configurable": {"thread_id": "r3", "belt_action": action}}
    asyncio.run(graph.ainvoke(_state(status, belt), config=config))  # type: ignore[arg-type]
    assert order == expected, order
