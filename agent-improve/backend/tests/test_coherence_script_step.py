"""G-96 — layer 2a judges a reply against the script step it performs.

THE DEFECT, MEASURED
--------------------
2026-09-24 13:14, `IMPR-2026-0E5` (first turn in process: no; untraced, G-95):
the Belt gave their business case in their own words; the coach captured it,
read it back and asked them to confirm it — the script's ④ **Confirm**. Layer
2a answered *"The coach's response is parroting the Belt's own words back,
which is a failure"*, degraded the turn and stood the grader down (S-C13 B3).
The turn has no grade and no record of why, so capability row 13 went red.

**Two causes, both in `CoherenceMiddleware`:**

1. **The judge was never told which step the coach was on.** §19.7 asks "is it
   parroting?" and §43's Confirm asks for exactly a read-back; with no script
   step in its prompt the judge could only apply the first.
2. **The judge never saw the confirmation question.** `_coach_text` read
   `CoachingResponse.message` only — and the 13:14 reply put its question,
   *"Confirm whether this business case fully captures…"*, in `prompt`. What
   the judge saw was a restatement with the question cut off.

**And the rejection left no mark**: the reason went to a log line, so the turn
is indistinguishable in `step_log` from one the grader simply never reached.

FOUNDER RULING 2026-09-24, OPTION A — what these tests hold
-----------------------------------------------------------
Coherence gets the current script step; reading back to confirm is allowed;
"parroting" is a restatement with no confirmation question and nothing added;
every 2a rejection records its reason in `step_log`.

The live A/B at the bottom (opt-in, `COHERENCE_LIVE=1`) is the ruling's
mutation: the REAL judge on the 13:14 reply passes it with the step context
and rejects it again with the step context removed — and still rejects a true
parrot at the same step.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from backend.core.substate import CoachingResponse, PhaseState
from backend.middleware import coherence as _coh
from backend.middleware.coherence import CoherenceMiddleware
from backend.middleware.grader import DMAICGraderMiddleware
from backend.middleware.skills import script_step
from backend.phases import nodes_common as _nc
from backend.validation.schemas import CoherenceResult

# ── the 13:14 turn, verbatim from its checkpoint ─────────────────────────────

BELT_1314 = (
    "Here is my business case in my own words: pricing mistakes on supplier "
    "invoices cost our accounts payable team about ninety hours of rework every "
    "month, and two of our largest clients escalated complaints last quarter."
)
BUSINESS_CASE_1314 = (
    "Pricing mistakes on supplier invoices cost our accounts payable team about "
    "ninety hours of rework every month, and two of our largest clients "
    "escalated complaints last quarter."
)
REPLY_1314 = CoachingResponse(
    message=("Your business case has been recorded:\n\n**Business Case:** "
             + BUSINESS_CASE_1314 + "\n\nThis statement highlights the operational "
             "and reputational impact of the issue, providing a solid rationale "
             "for the project."),
    explanation=("A strong business case quantifies both operational costs and "
                 "external impacts, ensuring the project's importance is clear."),
    example=("Example:\n- Business Case: Delivery delays cost GBP 2M annually in "
             "lost revenue and expedited shipping fees."),
    prompt=("Confirm whether this business case fully captures the issue's impact "
            "on operations and client relationships."),
    progress="Define · 13 of 13",
    fields_captured=[{"field_name": "business_case", "value": BUSINESS_CASE_1314,
                      "source": "belt"}],
)


def _turn(reply: CoachingResponse = REPLY_1314, belt: str = BELT_1314) -> dict[str, Any]:
    return {"structured_response": reply, "messages": [HumanMessage(content=belt)]}


class _RecordingJudge:
    """Stands in for `get_llm("coherence")` and its structured wrapper, and
    keeps every prompt it was sent."""

    def __init__(self, verdict: CoherenceResult) -> None:
        self.verdict = verdict
        self.prompts: list[str] = []

    def __call__(self, role: str, **_: Any) -> "_RecordingJudge":
        assert role == "coherence"
        return self

    def with_structured_output(self, _schema: Any) -> "_RecordingJudge":
        return self

    async def ainvoke(self, prompt: str) -> CoherenceResult:
        self.prompts.append(prompt)
        return self.verdict


PASS = CoherenceResult(coherent=True, is_conclusive=True, is_parroting=False,
                       on_topic=True, reason="")
PARROT = CoherenceResult(coherent=False, is_conclusive=True, is_parroting=True,
                         on_topic=True, reason="parroting the Belt's words back")


# ── the step, computed from the script ───────────────────────────────────────


def test_a_turn_that_captures_a_field_is_at_that_fields_confirm_step() -> None:
    step = script_step("define", captured=["business_case"], focus_field="team")
    assert step is not None
    assert (step["position"], step["field"], step["step"]) == (1, "business_case", "confirm")
    assert "**Read back:**" in step["block"], (
        "the field's own script block, its read-back line included (6.61: "
        "the script's ④ is 'Read back', no longer 'Confirm, then move on')")
    assert "In a sentence or two" in step["block"], "the block is business_case's, not another's"


def test_metric_definitions_confirms_inside_position_5() -> None:
    """§39.1.9: the registry is captured inside position 5, not at its own."""
    step = script_step("define", captured=["metric_definitions"], focus_field=None)
    assert step is not None
    assert (step["position"], step["field"]) == (5, "metric_definitions")
    assert "What are we measuring" in step["block"], "position 5's block, baseline_estimate's"


def test_a_turn_that_captures_nothing_is_at_its_focus_fields_teaching_steps() -> None:
    step = script_step("define", captured=[], focus_field="project_scope")
    assert step is not None
    assert (step["position"], step["field"], step["step"]) == (6, "project_scope", "explain_show_ask")


def test_every_phase_gets_its_own_numbered_step() -> None:
    """All five scripts number their fields, so every phase's judge is told
    the position and the block — Measure's position 5 is `baseline_mean`."""
    step = script_step("measure", captured=["baseline_mean"], focus_field=None)
    assert step is not None
    assert (step["position"], step["step"]) == (5, "confirm") and step["block"]


def test_a_field_the_script_does_not_number_still_gets_the_pattern() -> None:
    """Every phase coaches Explain → Show → Ask → Confirm (§43); a field with
    no numbered block still has its step, with no position to name."""
    step = script_step("define", captured=["not_a_scripted_field"], focus_field=None)
    assert step is not None
    assert step["step"] == "confirm" and step["position"] is None and step["block"] == ""


# ── what the judge is sent ───────────────────────────────────────────────────


def _judge_prompt(monkeypatch, reply: CoachingResponse = REPLY_1314,
                  focus_field: str | None = None) -> str:
    judge = _RecordingJudge(PASS)
    monkeypatch.setattr(_coh, "get_llm", judge)
    mw = CoherenceMiddleware("define", focus_field=focus_field)
    asyncio.run(mw.aafter_agent(_turn(reply), None))
    assert len(judge.prompts) == 1
    return judge.prompts[0]


def test_the_judge_is_told_the_script_step_the_reply_performs(monkeypatch) -> None:
    prompt = _judge_prompt(monkeypatch)
    assert "SCRIPT STEP" in prompt
    assert "business_case" in prompt and "Confirm" in prompt
    assert "In a sentence or two" in prompt, "the field's script block is in the prompt"


def test_the_judge_sees_the_coachs_confirmation_question(monkeypatch) -> None:
    """Cause 2: the 13:14 question lived in `prompt`, which the judge never saw."""
    prompt = _judge_prompt(monkeypatch)
    assert REPLY_1314.prompt in prompt


def test_the_judge_is_given_the_rulings_definition_of_parroting(monkeypatch) -> None:
    prompt = " ".join(_judge_prompt(monkeypatch).lower().split())
    assert "no confirmation question and nothing added" in prompt
    assert "reading the belt's words back to confirm them is not parroting" in prompt


# ── every verdict reaches step_log ───────────────────────────────────────────


class _JudgedAgent:
    """The coach reduced to its after_agent pass: the REAL coherence and grader
    the executor mounted run on the 13:14 reply, the judge stubbed to REJECT."""

    def __init__(self, middleware: list[Any], verdict: CoherenceResult) -> None:
        self.coherence = next(m for m in middleware if isinstance(m, CoherenceMiddleware))
        self.grader = next(m for m in middleware if isinstance(m, DMAICGraderMiddleware))
        self.verdict = verdict

    async def ainvoke(self, payload: dict, *_: Any, **__: Any) -> dict:
        async def judge(belt: str, coach: str) -> CoherenceResult:
            return self.verdict
        self.coherence._check = judge  # type: ignore[method-assign]
        messages = [*payload["messages"], AIMessage(content=REPLY_1314.message)]
        state = {"structured_response": REPLY_1314, "messages": messages}
        await self.coherence.aafter_agent(state, None)
        await self.grader.aafter_agent(state, None)   # stands down on degrade
        return {"messages": messages, "structured_response": REPLY_1314}


def _state() -> PhaseState:
    base: PhaseState = {
        "case_id": "IMPR-TEST-G96", "current_phase": "define",
        "messages": [HumanMessage(content=BELT_1314)],
        "history": [], "phase_context": "", "coaching_plan": None,
        "field_index": 0, "draft": {}, "artifacts": {}, "step_log": [],
        "field_log": [], "field_status": {}, "belt_edits": {}, "turn_count": 0, "final": {},
        "gate_attempts": 0, "validator_feedback": [], "rejection_feedback": [],
        "citations": [], "uploads": [], "asks": [], "hop_results": [],
        "synthesis_output": None,
    }
    return base


def _coherence_entries(monkeypatch, verdict: CoherenceResult) -> list[dict]:
    monkeypatch.setattr(_nc, "create_agent",
                        lambda **kw: _JudgedAgent(kw["middleware"], verdict))
    out = asyncio.run(_nc.executor("define", _state()))
    return [e for e in out["step_log"] if e.get("layer") == "coherence"]


def test_every_rejection_records_its_reason_in_step_log(monkeypatch, stub_planner) -> None:
    entries = _coherence_entries(monkeypatch, PARROT)
    assert len(entries) == 1, "one layer-2a record per turn"
    e = entries[0]
    assert e["coherent"] is False and e["is_parroting"] is True
    assert e["reason"] == PARROT.reason
    assert e["degraded"] is True and e["grader_skipped"] is True
    assert e["script_step"] == {"position": 1, "field": "business_case", "step": "confirm"}
    assert e["key"] == "define:0:coherence"


def test_a_pass_is_recorded_too(monkeypatch, stub_planner) -> None:
    """A turn whose reply 2a passed is distinguishable from one 2a never ran on."""
    entries = _coherence_entries(monkeypatch, PASS)
    assert len(entries) == 1 and entries[0]["coherent"] is True
    assert entries[0]["degraded"] is False


# ── the ruling's mutation, on the REAL judge — opt-in ────────────────────────

LIVE = os.environ.get("COHERENCE_LIVE") == "1"


#: The negative control: what parroting IS under the ruling — the Belt's words
#: back, no confirmation question, nothing added — at the very same step.
TRUE_PARROT = CoachingResponse(
    message="Business case: " + BUSINESS_CASE_1314, explanation="", example="",
    prompt="", progress="",
    fields_captured=[{"field_name": "business_case", "value": BUSINESS_CASE_1314,
                      "source": "belt"}],
)


@pytest.mark.skipif(not LIVE, reason="real coherence judge; set COHERENCE_LIVE=1")
@pytest.mark.parametrize("reply, with_step, coherent", [
    (REPLY_1314, True, True),
    (REPLY_1314, False, False),
    (TRUE_PARROT, True, False),
], ids=["1314-confirm-with-step", "MUTATION-1314-no-step", "control-true-parrot-with-step"])
def test_live_the_real_judge(monkeypatch, reply, with_step, coherent) -> None:
    """The ruling's mutation and its control, on the REAL judge (Azure only;
    the suite's G-95 guard keeps it untraced).

    With the step context the 13:14 read-back is coherent; REMOVE the step
    context and the same reply is rejected as parroting again; and a true
    parrot at the same step is still rejected — the step context allows a
    confirmation, it does not switch the question off. Measured 2026-09-24,
    ten runs each: 10/10, 0/10, and 10/10 rejected.
    """
    # Each case runs on its own event loop; a cached client from the last
    # case is bound to a loop that is closed ("Event loop is closed").
    from backend.core import llm as _llm
    _llm._build_llm.cache_clear()
    if not with_step:
        monkeypatch.setattr(_coh, "script_step", lambda *a, **k: None)
    mw = CoherenceMiddleware("define")
    asyncio.run(mw.aafter_agent(_turn(reply), None))
    assert mw.last is not None
    print(f"\ncoherent={mw.last.coherent} parroting={mw.last.is_parroting} "
          f"reason={mw.last.reason!r}")
    assert mw.last.coherent is coherent, mw.last.reason
    if not coherent:
        assert mw.last.is_parroting, mw.last.reason
