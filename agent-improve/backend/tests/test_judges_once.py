"""A judge judges each distinct reply once — procedure step 6.52, B2.

THE DEFECT, MEASURED
--------------------
Trace 01a0d215-a216-75e2-ba80-1c80597f891f: the grader called its model three
times on ONE reply — three inputs, 2,642 characters each, zero differing
lines — and the executor's wall ran out on the third. Coherence does the same:
`self._check(belt_text, coach_text)` inside a loop whose `coach_text` never
changes. Across the twelve turns on `IMPR-2026-0E5` that completed on
2026-09-23, the grader used all three calls on eight and coherence on four.

A retry that sends the same input to a temperature-0.1 judge is not a retry;
it is the same question asked again. Until step 6.53 regenerates the reply on
a FAIL (gated on G-83's latency ruling), the reply cannot change inside the
hook, so each judge makes ONE call. On FAIL the grader passes the turn through
with its Belt-visible warning — §19.8's end state — and coherence degrades the
turn and stands the grader down, as it did.

THE TEST THIS REPLACES
----------------------
`test_middleware.py::test_max_iterations_passes_through_with_a_belt_visible_
warning` asserted `len(logged) == GRADER_MAX_ITERATIONS == 3` — it ENCODED
re-judging identical text as correct.

AND THE VERDICT IS KEPT
-----------------------
§19.8: *"`on_evaluation` writes each grading iteration to `step_log`"*. The
executor collected them into `grader_log` and never read it (capability row
13). The last test here drives the real executor and reads its `step_log`.
"""
from __future__ import annotations

import asyncio
from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from backend.core.substate import CoachingResponse, PhaseState
from backend.middleware.coherence import CoherenceMiddleware
from backend.middleware.grader import DMAICGraderMiddleware, MAX_ITERATIONS_WARNING
from backend.phases import nodes_common as _nc
from backend.validation.schemas import (
    CoachingGraderVerdict,
    CoherenceResult,
    CriterionResult,
)

REPLY = "Here is what a good problem statement looks like."


def _turn(message: str = REPLY) -> dict[str, Any]:
    return {"structured_response": CoachingResponse(
                explanation="", example="", prompt="", progress="", message=message),
            "messages": [HumanMessage(content="what does good look like?")]}


def _failing_verdict() -> CoachingGraderVerdict:
    return CoachingGraderVerdict(criteria=[CriterionResult(
        criterion="Coach must challenge weak inputs with specific follow-up questions",
        status="fail", feedback="ask how the error rate was measured")])


def _incoherent() -> CoherenceResult:
    return CoherenceResult(coherent=False, is_conclusive=False, is_parroting=False,
                           on_topic=True, reason="vague non-answer")


def _recording(verdict: Any) -> tuple[list[tuple[str, str]], Any]:
    seen: list[tuple[str, str]] = []

    async def judge(belt: str, coach: str) -> Any:
        seen.append((belt, coach))
        return verdict
    return seen, judge


def test_the_grader_judges_a_reply_once() -> None:
    """A FAIL is graded once and passes through with the Belt-visible warning."""
    mw = DMAICGraderMiddleware("define")
    logged: list[dict[str, Any]] = []
    mw.on_evaluation = logged.append
    seen, mw._grade = _recording(_failing_verdict())  # type: ignore[method-assign]

    out = asyncio.run(mw.aafter_agent(_turn(), None))

    assert len(seen) == 1, f"the grader judged one reply {len(seen)} times"
    assert len(logged) == 1 and logged[0]["status"] == "failed"
    assert out == {"grader_warning": MAX_ITERATIONS_WARNING}


def test_coherence_checks_a_reply_once() -> None:
    """A reject is checked once; the turn degrades and the grader stands down."""
    mw = CoherenceMiddleware("define")
    seen, mw._check = _recording(_incoherent())  # type: ignore[method-assign]

    out = asyncio.run(mw.aafter_agent(_turn(), None))

    assert len(seen) == 1, f"coherence checked one reply {len(seen)} times"
    assert mw.degraded is True
    assert out is None, "the skip travels by reference, never through state"


def test_a_coherent_reply_is_checked_once_and_left_alone() -> None:
    mw = CoherenceMiddleware("define")
    seen, mw._check = _recording(CoherenceResult(  # type: ignore[method-assign]
        coherent=True, is_conclusive=True, is_parroting=False, on_topic=True, reason=""))

    assert asyncio.run(mw.aafter_agent(_turn(), None)) is None
    assert len(seen) == 1 and mw.degraded is False


@pytest.mark.parametrize("make, attr, verdict", [
    (lambda: DMAICGraderMiddleware("define"), "_grade", _failing_verdict()),
    (lambda: CoherenceMiddleware("define"), "_check", _incoherent()),
])
def test_any_judge_retry_changes_its_input_or_makes_one_call(make, attr, verdict) -> None:
    """**The rule, stated once for every judge.** A second call is allowed only
    if its input differs from the first — otherwise it is the same question."""
    mw = make()
    seen, judge = _recording(verdict)
    setattr(mw, attr, judge)

    asyncio.run(mw.aafter_agent(_turn(), None))

    repeats = [i for i in range(1, len(seen)) if seen[i] == seen[i - 1]]
    assert not repeats, (
        f"{type(mw).__name__} sent the same input {len(seen)} times — a retry "
        "must change what it asks, or not happen")


# ── the verdict reaches step_log — the real executor ──────────────────────


class _GradedAgent:
    """The coach, reduced to its after_agent pass: the REAL grader the
    executor mounted runs on the reply, with its model call stubbed to FAIL."""

    def __init__(self, middleware: list[Any]) -> None:
        self.grader = next(m for m in middleware
                           if isinstance(m, DMAICGraderMiddleware))
        _, self.grader._grade = _recording(_failing_verdict())  # type: ignore[method-assign]

    async def ainvoke(self, payload: dict, *_: Any, **__: Any) -> dict:
        reply = CoachingResponse(explanation="", example="", prompt="",
                                 progress="", message=REPLY)
        messages = [*payload["messages"], AIMessage(content=REPLY)]
        await self.grader.aafter_agent(
            {"structured_response": reply, "messages": messages}, None)
        return {"messages": messages, "structured_response": reply}


def _state() -> PhaseState:
    base: PhaseState = {
        "case_id": "IMPR-TEST-652", "current_phase": "define",
        "messages": [HumanMessage(content="what does good look like?")],
        "history": [], "phase_context": "", "coaching_plan": None,
        "field_index": 0, "draft": {}, "artifacts": {}, "step_log": [],
        "field_log": [], "belt_edits": {}, "turn_count": 0, "final": {},
        "gate_attempts": 0, "validator_feedback": [], "rejection_feedback": [],
        "citations": [], "uploads": [], "asks": [], "hop_results": [],
        "synthesis_output": None,
    }
    return base


def test_the_graders_verdict_reaches_step_log(monkeypatch, stub_planner) -> None:
    """**Row 13's mechanism.** A FAIL verdict is in the turn's `step_log`,
    under `layer: "coaching_grader"`, with the criterion that failed."""
    monkeypatch.setattr(_nc, "create_agent",
                        lambda **kw: _GradedAgent(kw["middleware"]))

    out = asyncio.run(_nc.executor("define", _state()))

    graded = [e for e in out["step_log"] if e.get("layer") == "coaching_grader"]
    assert graded, (
        "the grader judged the reply and step_log holds no verdict: "
        f"{[e.get('node') for e in out['step_log']]}")
    assert graded[0]["status"] == "failed"
    assert graded[0]["criteria_failed"] == [
        "Coach must challenge weak inputs with specific follow-up questions"]
    assert graded[0]["key"] == "define:0:coaching_grader"
