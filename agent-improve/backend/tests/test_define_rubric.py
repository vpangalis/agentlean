"""R7 — the Define gate rubric: one criterion per element, pass/fail with a reason.

Founder requirement R7 (`docs/requirements/business.md`, 2026-09-26) replaces
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
    # G-133: DEF-R02 is settled in code here (the team writes "no training needed").
    assert set(judge.asked) == {c for c, _, _ in DEFINE_CRITERIA} - CODE_ONLY - {"DEF-R02"}


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
    from backend.phases.define.parse import metric_value
    env.case.phases["define"].structured = {**COMPLETE, "target_value": metric_value("23%", target=True, unit="%")}
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


def test_g129_the_grader_sees_each_elements_acceptance_criteria(monkeypatch) -> None:
    """DEF-159 — G-129 (founder ruling 2, 2026-09-28): the gate grader receives each element's
    acceptance criteria next to its rubric line, and is told an answer that meets them meets the
    line in other words; DEF-R13 names "issues and barriers (roadblocks)"."""
    import asyncio

    from backend.core.prompts import DEFINE_RUBRIC
    from backend.middleware.skills import acceptance_criteria
    from backend.validation import rubric

    seen: list = []

    class Grader:
        def with_structured_output(self, schema):
            return self

        async def ainvoke(self, prompt):
            seen.append(prompt)
            return rubric.GraderVerdict(verdicts=[])
    monkeypatch.setattr(rubric, "get_llm", lambda role, **kw: Grader())
    asyncio.run(rubric._llm_verdicts([("DEF-R13", "issues_and_barriers", "names the key issues")], "doc"))
    assert seen, "no grader call"
    for aid, _ in acceptance_criteria("define", "issues_and_barriers"):
        assert f"element criterion `{aid}`" in seen[0]
    assert "never fail it for wording alone" in seen[0]
    assert "issues and barriers (roadblocks)" in DEFINE_RUBRIC


def test_g133_training_in_other_words_goes_to_the_grader_not_a_word_check() -> None:
    """G-133 (DEF-159): a team whose training is written in other words ("needs a half-day on data
    collection") is not failed by a word check; DEF-R02 then goes to the grader, which sees the
    element's own criteria (G-129). A missing champion still fails in code."""
    import asyncio

    from backend.validation import rubric

    team = [{"name": "Tom", "role": "Champion", "function": "Finance Director"},
            {"name": "Lena", "role": "Process Owner", "function": "AP Manager"},
            {"name": "Dev", "role": "Team Member", "function": "AP clerk; needs a half-day on data collection"}]
    assert rubric._code_half("DEF-R02", {"team": team}, __import__("datetime").date(2026, 9, 29)) is None
    asked: list = []

    async def judge(criteria, document):
        asked.extend(c for c, _, _ in criteria)
        return rubric.GraderVerdict(verdicts=[rubric.CriterionVerdict(criterion=c, status="pass")
                                              for c, _, _ in criteria])
    got = asyncio.run(rubric.grade_define({**COMPLETE, "team": team}, judge))
    assert "DEF-R02" in asked and {v.criterion: v.status for v in got.verdicts}["DEF-R02"] == "pass"
    no_champion = [e for e in team if e["role"] != "Champion"]
    verdict = rubric._code_half("DEF-R02", {"team": no_champion}, __import__("datetime").date(2026, 9, 29))
    assert verdict is not None and verdict.status == "fail"


def test_g134_def_r13_is_settled_in_code_first_and_the_model_judges_only_specificity() -> None:
    """G-134 (founder ruling 4, 2026-09-29): the gate grader failed DEF-R13 once in four runs on
    the SAME specific answer. Code now settles what it can read — the conscious 'none identified
    at this stage' passes, an answer that names nothing fails with the reason — and only the
    specificity of what is named reaches the model, asked that and nothing else."""
    from backend.validation.rubric import MODEL_ASKS

    class Recorder(Judge):
        async def __call__(self, criteria, document):
            self.texts = {c: t for c, _, t in criteria}
            return await super().__call__(criteria, document)

    none = _grade({**COMPLETE, "issues_and_barriers": "None identified at this stage."}, j1 := Recorder())
    assert none["DEF-R13"].status == "pass" and "DEF-R13" not in j1.asked, "settled in code, the model not asked"
    for blank in ("N/A", "tbd", "none"):
        got = _grade({**COMPLETE, "issues_and_barriers": blank}, j2 := Recorder())
        assert got["DEF-R13"].status == "fail" and "none identified at this stage" in got["DEF-R13"].feedback, blank
        assert "DEF-R13" not in j2.asked, blank
    live = ("Two barriers: the three sites use different approval routes, and an ERP change freeze until "
            "January limits system changes. One risk: AP staff turnover over the winter.")
    got = _grade({**COMPLETE, "issues_and_barriers": live}, j3 := Recorder())
    assert "DEF-R13" in j3.asked and got["DEF-R13"].status == "pass"
    assert j3.texts["DEF-R13"] == MODEL_ASKS["DEF-R13"], "the model is asked specificity only"
    assert "ONLY whether each one named is specific" in j3.texts["DEF-R13"]
