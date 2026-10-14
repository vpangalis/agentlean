"""Grader v2 (ADR-0084, founder rulings 2026-10-14) — the grading call's rules, with a fake model (no live
call): the explicit move -> criteria table; the two code checks; a criterion not asked is not applicable; a
fail must quote a sentence that is in the reply, or it is not checked; the reply passes only when no code
check and no asked criterion fails."""
from __future__ import annotations

import asyncio
from typing import Any

from backend.validation import grader_v2 as G
from backend.validation.schemas import CriterionCheck, GraderV2Verdict


class _Fake:
    """Stands in for the grader model and its structured wrapper; records the prompt."""

    def __init__(self, verdict: GraderV2Verdict) -> None:
        self.verdict = verdict
        self.prompts: list[str] = []

    def with_structured_output(self, schema: Any, **_: Any) -> "_Fake":
        return self

    async def ainvoke(self, prompt: str) -> GraderV2Verdict:
        self.prompts.append(prompt)
        return self.verdict


def _grade(move: str, reply: str, *checks: CriterionCheck) -> tuple[dict[str, Any], _Fake]:
    fake = _Fake(GraderV2Verdict(criteria=list(checks)))
    out = asyncio.run(G.grade("define", move, "Project scope", ["names where the process starts and ends"],
                              reply, "Confirm", {"business_case": "late payments cost £62,000"},
                              ["Our late payment rate is 23%."], model=fake))
    return out, fake


def _verdict(out: dict[str, Any], c: str) -> str:
    return next(x["verdict"] for x in out["criteria"] if x["criterion"] == c)


def test_the_move_table_is_explicit_and_as_ruled() -> None:
    assert G.MOVE_CRITERIA["read_back"] == ("C2", "C3", "C4")          # C2 on read-backs (founder)
    assert G.MOVE_CRITERIA["store_and_advance"] == ("C1", "C4")        # C1 on stores (founder)
    assert G.MOVE_CRITERIA["challenge"] == ("C2", "C3", "C4")
    assert "C1" not in G.MOVE_CRITERIA["challenge"] and "C1" not in G.MOVE_CRITERIA["read_back"]


def test_the_two_old_rubric_lines_are_code_checks() -> None:
    checks = {c["check"]: c["passed"] for c in G.code_checks("define", "See www.example.com for the project scope.")}
    assert checks == {"no external address": False, "on the phase's topic": True}
    checks = {c["check"]: c["passed"] for c in G.code_checks("define", "Thanks, that is noted.")}
    assert checks["on the phase's topic"] is False


def test_only_the_moves_criteria_are_asked_and_the_rest_are_not_applicable() -> None:
    reply = "Stored: business case. Next, the project scope: where does your process start and end?"
    out, fake = _grade("store_and_advance", reply,
                       CriterionCheck(criterion="C1", reasoning="explains", evidence="", verdict="pass"),
                       CriterionCheck(criterion="C4", reasoning="one question",
                                      evidence="where does your process start and end?", verdict="pass"))
    assert out["asked"] == ["C1", "C4"] and _verdict(out, "C2") == _verdict(out, "C3") == "not_applicable"
    assert "C2 CHALLENGES" not in fake.prompts[0] and "C1 TEACHES" in fake.prompts[0]
    assert "late payments cost £62,000" in fake.prompts[0] and "Our late payment rate is 23%." in fake.prompts[0]
    assert out["passed"] is True


def test_a_fail_must_quote_a_sentence_of_the_reply() -> None:
    reply = "Here is what I captured for your project scope: In: invoice receipt to payment. Is this right?"
    out, _ = _grade("read_back", reply,
                    CriterionCheck(criterion="C3", reasoning="adds a word", evidence="a sentence not in the reply",
                                   verdict="fail"),
                    CriterionCheck(criterion="C2", reasoning="vague", evidence="", verdict="fail"),
                    CriterionCheck(criterion="C4", reasoning="asks", evidence="Is this right?", verdict="pass"))
    assert _verdict(out, "C3") == G.NOT_CHECKED and _verdict(out, "C2") == G.NOT_CHECKED
    assert out["passed"] is True
    out, _ = _grade("read_back", reply,
                    CriterionCheck(criterion="C3", reasoning="incomplete", evidence="In: invoice receipt to payment.",
                                   verdict="fail"))
    assert _verdict(out, "C3") == "fail" and out["passed"] is False


def test_a_failed_code_check_fails_the_reply() -> None:
    out, _ = _grade("store_and_advance", "Read www.example.com about the project scope. Where does it start?",
                    CriterionCheck(criterion="C4", reasoning="asks", evidence="Where does it start?", verdict="pass"))
    assert out["passed"] is False
