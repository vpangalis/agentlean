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
    assert "FAIL only when they are generic labels" in j3.texts["DEF-R13"]


# ── G-241 (founder ruling 2026-10-22 afternoon, item 1) — the gate judge reads at temperature 0, and a failing reason
# that cites a fact the case never mentions is discarded and the criterion judged once more ──────────────────────

def test_g241_the_gate_judge_reads_at_temperature_0(monkeypatch) -> None:
    """G-241 (1b): the gate judge's call is the grader role at temperature 0 — the coaching grader keeps its 0.1."""
    import asyncio

    from backend.validation import rubric

    asked: list = []

    class Grader:
        def with_structured_output(self, schema):
            return self

        async def ainvoke(self, prompt):
            return rubric.GraderVerdict(verdicts=[])
    def get_llm(role, **kw):
        asked.append((role, kw))
        return Grader()
    monkeypatch.setattr(rubric, "get_llm", get_llm)
    asyncio.run(rubric._llm_verdicts([("DEF-R13", "issues_and_barriers", "names the key issues")], "doc"))
    assert asked == [("grader", {"temperature": 0.0})], asked


def test_g241_a_reason_citing_a_fact_not_in_the_case_is_judged_again_once() -> None:
    """G-241 (1b): run 140813's failing reason asked for "year-end close context" — a fact the case never mentions.
    A failing reason that names a term (a quoted phrase, a hyphenated compound, an acronym) found neither in the
    case's answers nor in the criteria is discarded and the criterion judged once more; the second verdict stands.
    A failing reason grounded in the case's own answers is kept, with no second call."""
    import asyncio

    from backend.tests.test_define_report import COMPLETE
    from backend.validation import rubric
    from backend.validation.schemas import CriterionVerdict, GraderVerdict

    def judge_with(*reasons: str):
        calls: list = []

        async def judge(criteria, document):
            calls.append([c[0] for c in criteria])
            reason = reasons[min(len(calls), len(reasons)) - 1]
            return GraderVerdict(verdicts=[
                CriterionVerdict(criterion=cid, status="fail" if (cid == "DEF-R13" and reason) else "pass",
                                 feedback=reason if cid == "DEF-R13" else "") for cid, _, _ in criteria])
        return judge, calls

    case = dict(COMPLETE)
    to_judge = [("DEF-R13", "issues_and_barriers", "names the key issues and barriers")]
    document = rubric._document(case)
    judge, calls = judge_with("Specify the exact approval routes, ERP system details, and year-end close context.", "")
    r13 = asyncio.run(rubric._judged_once(to_judge, document, judge))["DEF-R13"]
    assert r13.status == "pass" and calls == [["DEF-R13"], ["DEF-R13"]], (r13, calls)

    judge, calls = judge_with("Still cites the year-end close.", "Still cites the year-end close.")
    r13 = asyncio.run(rubric._judged_once(to_judge, document, judge))["DEF-R13"]
    assert r13.status == "fail" and len(calls) == 2, (r13, calls)          # judged again once, never a third time

    word = next(w for w in str(case["issues_and_barriers"]).split() if len(w) > 4).strip(".,;:")
    judge, calls = judge_with(f"The barriers name '{word}' but say nothing of its effect on the project.")
    r13 = asyncio.run(rubric._judged_once(to_judge, document, judge))["DEF-R13"]
    assert r13.status == "fail" and len(calls) == 1, (r13, calls)
    assert rubric.foreign_terms("Specify the year-end close and the 'ERP freeze'.", "ERP freeze until January", "") \
        == ["year-end"]


def test_g241_each_gate_criterion_is_the_majority_of_three_verdicts() -> None:
    """G-241 (1c): at temperature 0 the judge still disagreed with itself on run 140813's document (3 fail, 2 pass
    over 5 repeats). Each model-judged criterion is judged three times and takes the majority verdict; a failing
    majority keeps a failing reason. Criteria code settles never reach the judge."""
    import asyncio

    from backend.tests.test_define_report import COMPLETE
    from backend.validation import rubric
    from backend.validation.schemas import CriterionVerdict, GraderVerdict

    def votes(*r13: str):
        calls: list = []

        async def judge(criteria, document):
            calls.append([c[0] for c in criteria])
            status = r13[len(calls) - 1]
            return GraderVerdict(verdicts=[
                CriterionVerdict(criterion=cid, status=status if cid == "DEF-R13" else "pass",
                                 feedback="The barriers are not specific to this project." if
                                 (cid == "DEF-R13" and status == "fail") else "") for cid, _, _ in criteria])
        return judge, calls

    for r13, expected in ((("fail", "pass", "pass"), "pass"), (("fail", "fail", "pass"), "fail"),
                          (("pass", "pass", "pass"), "pass")):
        judge, calls = votes(*r13)
        out = asyncio.run(rubric.grade_define(dict(COMPLETE), judge=judge))
        v = next(x for x in out.verdicts if x.criterion == "DEF-R13")
        assert v.status == expected and len(calls) == rubric.GATE_VOTES == 3, (r13, v, calls)
        assert (v.feedback == "The barriers are not specific to this project.") is (expected == "fail"), v
        assert not set(rubric.CODE_ONLY) & set(calls[0]), calls[0]


def test_g241_each_criterion_is_judged_on_the_values_it_reads() -> None:
    """G-241 (founder ruling 2026-10-22 evening, item 1): each gate criterion is judged on the fields it reads
    (rubric.READS and the element's own captured fields), never the whole document — a wording change in an element a
    criterion does not read cannot tip it. The judge gets one section per criterion holding only those values, and
    is told to judge each criterion on its own section."""
    import asyncio

    from backend.core.prompts import GATE_GRADER_PROMPT
    from backend.tests.test_define_report import COMPLETE
    from backend.validation import rubric
    from backend.validation.schemas import CriterionVerdict, GraderVerdict

    seen: list[str] = []

    async def judge(criteria, document):
        seen.append(document)
        return GraderVerdict(verdicts=[CriterionVerdict(criterion=c, status="pass", feedback="") for c, _, _ in criteria])
    asyncio.run(rubric.grade_define(dict(COMPLETE), judge=judge))
    doc = seen[0]
    sections = {s.split("]", 1)[0].lstrip("["): s for s in doc.split("\n\n") if s.startswith("[DEF-R")}
    r13 = sections["DEF-R13 — the values it reads"]
    for field in ("issues_and_barriers", "business_case", "project_scope", "process_map_sipoc"):
        assert f"{field}:" in r13, field
    for field in ("team", "voc_summary", "goal_statement", "secondary_metrics"):
        assert f"{field}:" not in r13, field
    r03 = sections["DEF-R03 — the values it reads"]
    assert "voc_summary:" in r03 and "critical_to_quality:" in r03 and "business_case:" not in r03, r03
    assert "on its own section" in GATE_GRADER_PROMPT
