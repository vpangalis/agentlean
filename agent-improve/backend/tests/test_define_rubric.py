"""R7 — the Define gate rubric: one criterion per element, pass/fail with a reason.

Founder requirement R7 (`docs/requirements/define.md`, 2026-09-26) replaces
the G-40 draft. `core.prompts.DEFINE_RUBRIC` holds the thirteen criteria;
`validation/rubric.grade_define` grades the confirmed values against them —
the deterministic half first, one `grader` call for what needs judgment — and
the validation stack runs it as Layer 2d after 2b, so a report failing a
criterion never reaches the acceptance pause (R6).
"""
from __future__ import annotations

import asyncio
import datetime as dt
from pathlib import Path
from typing import Any

import pytest

from backend.core.prompts import DEFINE_RUBRIC
from backend.phases.define.schema import DEFINE_FIELD_ORDER
from backend.tests.test_define_report import COMPLETE
from backend.tests.test_gate_acceptance import CASE_ID, _review, _submit, env  # noqa: F401
from backend.validation.rubric import CODE_ONLY, DEFINE_CRITERIA, grade_define
from backend.validation.schemas import CriterionVerdict, GraderVerdict

TODAY = dt.date(2026, 9, 26)
_PROJECT = Path(__file__).resolve().parents[2]


class Judge:
    """The grader model, faked: a fixed status per criterion, and what it was asked."""

    def __init__(self, status: dict[str, str] | None = None, drop: tuple[str, ...] = ()) -> None:
        self.status, self.drop = status or {}, drop
        self.asked: list[str] = []

    async def __call__(self, criteria: list[tuple[str, str, str]], document: str) -> GraderVerdict:
        self.asked = [c for c, _, _ in criteria]
        return GraderVerdict(verdicts=[
            CriterionVerdict(criterion=c, status=self.status.get(c, "pass"),  # type: ignore[arg-type]
                             feedback="judged" if self.status.get(c, "pass") != "pass" else "")
            for c in self.asked if c not in self.drop])


def _grade(artifacts: dict[str, Any], judge: Judge) -> dict[str, CriterionVerdict]:
    v = asyncio.run(grade_define(artifacts, judge, today=TODAY))
    return {x.criterion: x for x in v.verdicts}


# ── the rubric ────────────────────────────────────────────────────────────


def test_one_criterion_per_element_each_citing_the_manual() -> None:
    assert [cid for cid, _, _ in DEFINE_CRITERIA] == [f"DEF-R{n:02d}" for n in range(1, 14)]
    assert [field for _, field, _ in DEFINE_CRITERIA] == list(DEFINE_FIELD_ORDER)
    assert all("(p. " in text for _, _, text in DEFINE_CRITERIA), "every criterion cites its page"


def test_r7s_criteria_are_the_ones_graded() -> None:
    text = DEFINE_RUBRIC.lower()
    for phrase in ("no cause and no solution", "exactly one primary metric", "linked to a kpi",
                   "side effect", "not too broad", "as-is", "champion and a process owner",
                   "training", "real data rather than a best guess"):
        assert phrase in text, phrase


def test_the_g40_draft_is_superseded_and_archived() -> None:
    assert not (_PROJECT / "docs" / "founder-inputs" / "G40_define_rubric_DRAFT.md").exists()
    assert (_PROJECT / "docs" / "_archive" / "G40_define_rubric_DRAFT_superseded_2026-09-26.md").exists()


# ── grading ───────────────────────────────────────────────────────────────


def test_a_complete_report_passes_and_only_judgment_reaches_the_model() -> None:
    judge = Judge()
    got = _grade(COMPLETE, judge)
    assert all(v.status == "pass" for v in got.values()), {c: v.feedback for c, v in got.items()}
    assert len(got) == 13
    assert not set(judge.asked) & CODE_ONLY, "a criterion code settles never reaches the model"
    assert set(judge.asked) == {c for c, _, _ in DEFINE_CRITERIA} - CODE_ONLY


@pytest.mark.parametrize("change,cid,words", [
    ({"team": [{"name": "Priya", "role": "Belt", "function": "lead"}]}, "DEF-R02", "champion"),
    ({"target_value": "23%"}, "DEF-R08", "equals the baseline"),
    ({"target_date": "2025-01-01"}, "DEF-R09", "not in the future"),
    ({"target_date": "soon"}, "DEF-R09", "not a calendar date"),
    ({"benefits_analysis": {**COMPLETE["benefits_analysis"], "impact_type": "big"}}, "DEF-R10", "one-off"),
    ({"problem_5w2h": {"what": "w"}}, "DEF-R04", "where"),
    ({"critical_to_quality": []}, "DEF-R03", "CTQ"),
    ({"baseline_estimate": "high"}, "DEF-R05", "no number"),
])
def test_code_fails_a_criterion_with_its_reason_and_the_model_is_not_asked(change, cid, words) -> None:
    judge = Judge()
    got = _grade({**COMPLETE, **change}, judge)
    assert got[cid].status == "fail" and words in got[cid].feedback, got[cid]
    assert cid not in judge.asked, "a code failure is final"


def test_the_models_judgment_fails_a_criterion_with_its_reason() -> None:
    got = _grade(COMPLETE, Judge({"DEF-R01": "fail"}))
    assert got["DEF-R01"].status == "fail" and got["DEF-R01"].feedback == "judged"


def test_define_never_warns_and_an_unjudged_criterion_fails_closed() -> None:
    got = _grade(COMPLETE, Judge({"DEF-R06": "warning"}, drop=("DEF-R13",)))
    assert got["DEF-R06"].status == "fail", "Tier 1: a warning is a fail in Define"
    assert got["DEF-R13"].status == "fail" and "no verdict" in got["DEF-R13"].feedback
    assert all(v.tier == 1 for v in got.values())


# ── in the gate: Layer 2d after 2b, before the pause ──────────────────────


def test_a_report_failing_a_criterion_is_not_paused_and_the_criterion_is_named(env) -> None:  # noqa: F811
    env.case.phases["define"].structured = {**COMPLETE, "target_value": "23%"}
    body = _submit(env)
    assert body["passed"] is False and body["awaiting_acceptance"] is False
    assert any(m.startswith("DEF-R08") for m in body["missing_fields"]), body["missing_fields"]
    assert _review(env)["awaiting_decision"] is False, "a failing report reached the pause"
    assert env.written == []


def test_a_report_meeting_every_criterion_pauses(env) -> None:  # noqa: F811
    assert _submit(env)["awaiting_acceptance"] is True


# ── the pre-write hook: an exclusion applies whatever the drive letter's case ──


def test_the_drift_hook_matches_paths_across_the_drive_letters_case() -> None:
    """The validator exclusion for §4.6's builder-style call did not apply to
    this module: CLAUDE_PROJECT_DIR said "c:/…", the tool said "C:/…", and the
    case-sensitive prefix test left the path absolute (6.68)."""
    import importlib.util
    import os
    hook = Path(__file__).resolve().parents[3] / ".claude" / "hooks" / "pre-tool-use-drift-check.py"
    spec = importlib.util.spec_from_file_location("pre_tool_use_drift_check", hook)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rel = mod.normalize_path("C:/X/agent-improve/backend/validation/rubric.py", r"c:\X")
    if os.name == "nt":
        assert rel == "agent-improve/backend/validation/rubric.py"
    assert mod.normalize_path("C:/X/a.py", "C:/X") == "a.py"
