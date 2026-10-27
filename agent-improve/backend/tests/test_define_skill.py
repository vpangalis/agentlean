"""R2 and R4 — what the coach teaches for each Define element, and the thirteen.

Founder requirements (`docs/requirements/business.md`, 2026-09-26):

  R2  for every Define element the coach explains what it is and why it
      matters, and shows a worked example of the finished result; for SIPOC
      and 5W2H it shows a demo of the completed diagram
  R4  thirteen elements: the twelve plus the BENEFITS ANALYSIS (cost of the
      gap / COPQ, sustainable vs one-off, realisation schedule, finance
      contact); the VOC includes the CTQs

Read from the script the coach receives (`skills/dmaic-define-phase/SKILL.md`,
through the skills middleware's own parser) and from the schema and the state
the coach is given — never from a copy of either.
"""
from __future__ import annotations

import re

from typing import Any, cast

from langchain_core.messages import HumanMessage

from backend.core.substate import CoachingPlan
from backend.middleware.skills import _field_blocks, _sections, acceptance_criteria, worked_examples
from backend.middleware.state_injection import BeforeModelStateInjection
from backend.phases import moves
from backend.phases.define.schema import (
    BENEFITS_ANALYSIS_KEYS,
    CTQ_KEYS,
    DEFINE_FIELD_ORDER,
    DEFINE_REQUIRED_FOR_GATE_FIELDS,
    DefineOutput,
)
from backend.phases.gate_registry import missing_gate_fields

#: What R2 asks of every element's block, as the script labels it.
R2_SECTIONS = ("What it is", "Why it matters", "Show", "Ask", "Acceptance criteria")


def test_r2_every_element_explains_shows_asks_and_lists_its_criteria() -> None:
    blocks = _field_blocks("define")
    assert list(blocks) == list(DEFINE_FIELD_ORDER), "one block per element, in order"
    for field in DEFINE_FIELD_ORDER:
        sections = _sections(blocks[field][1])
        missing = [s for s in R2_SECTIONS if s not in sections]
        assert not missing, (field, missing)
        show = " ".join(sections["Show"])
        assert "illustration" in show.lower(), f"{field}: the example is not marked as an illustration"
        criteria = acceptance_criteria("define", field)
        # A criterion cites the manual's page, or the requirement that added it when the manual has
        # none (R17, R18 — ADR-0078, founder 2026-10-12): never an uncited criterion.
        assert criteria and all("(p. " in text or re.search(r"\(R\d+[a-z]?\)", text)
                                for _, text in criteria), (field, criteria)
    # The 5W2H and the SIPOC show the COMPLETED diagram, as a table.
    fivew = " ".join(_sections(blocks["problem_statement"][1])["Show"])
    sipoc = " ".join(_sections(blocks["process_map_sipoc"][1])["Show"])
    for question in ("What", "Where", "When", "Who", "Why", "How", "How much"):
        assert f"| {question} |" in fivew, question
    # DEF-211 (founder note under ADR-0070, 2026-10-22): the SIPOC's example is the skill's structured file, drawn
    # by code — the script shows the model no table.
    assert "| Suppliers |" not in sipoc and "drawn below" in sipoc, sipoc
    assert "each process step starts with a verb" in sipoc, "how each part is formulated"
    # And every worked example is refused as the Belt's own data (§22).
    assert len(worked_examples("define")) >= len(DEFINE_FIELD_ORDER)


def test_r4_thirteen_elements_with_the_benefits_analysis_and_the_ctqs() -> None:
    assert len(DEFINE_FIELD_ORDER) == 13 and DEFINE_FIELD_ORDER[9] == "benefits_analysis"
    assert {"benefits_analysis", "critical_to_quality"} <= set(DEFINE_REQUIRED_FOR_GATE_FIELDS)
    assert dict(moves.positions("define"))["voc_summary"] == ("voc_summary", "critical_to_quality")
    assert BENEFITS_ANALYSIS_KEYS == ("cost_of_gap", "impact_type", "realisation_schedule",
                                      "finance_contact")
    assert CTQ_KEYS == ("customer", "need", "requirement")
    assert {"benefits_analysis", "critical_to_quality"} <= set(DefineOutput.model_fields)
    # A benefits analysis missing a part is refused at the gate, by name.
    half = {"benefits_analysis": {"cost_of_gap": "£68k", "impact_type": "sustainable"}}
    assert "benefits_analysis.realisation_schedule/finance_contact" in missing_gate_fields("define", half)
    # The savings calculation FEEDS the benefits analysis: while that element is
    # current, the coach is given the latest result to propose as cost_of_gap.
    plan = CoachingPlan(focus_field="benefits_analysis", status="asked", move="teach")
    state: Any = {"artifacts": {"computation_results": [
        {"tool": "calculate_expected_savings", "inputs": {"annual_volume": "42000"},
         "result": {"annual_savings": "68040.00"}}]},
        "phase_context": "", "coaching_plan": plan, "messages": [HumanMessage(content="ok")]}
    mw = BeforeModelStateInjection("define", cast(Any, state))
    mw.before_agent(None, None)
    block = mw._block
    assert "<savings_calculation>" in block and "68040.00" in block and "cost_of_gap" in block


def test_b7_the_define_readers_read_the_criteria_owner_never_the_skill(monkeypatch) -> None:
    """B7 (founder ruling 2026-10-27, item 4): Define's criteria, their ids, its element order and its welcome are
    read from their owner in code (`phases/define/criteria.py`), never parsed from SKILL.md. Proved by changing the
    OWNER only — the skill file still says the original — and seeing every reader follow the owner."""
    from backend.core import guard_messages
    from backend.middleware import skills
    from backend.phases.define import criteria as owner
    from backend.phases.define import templates, welcome

    patched = ((owner.A_DATE, "a patched calendar date criterion (p. 0)"),)
    monkeypatch.setitem(owner.CRITERIA, "target_date", patched)
    monkeypatch.setattr(owner, "PHASES", (("Define", "a patched purpose"),))
    skill = (skills.SKILLS_ROOT / "dmaic-define-phase" / "SKILL.md").read_text(encoding="utf-8")
    assert "a patched calendar date criterion" not in skill and "a patched purpose" not in skill
    assert acceptance_criteria("define", "target_date") == list(patched)
    assert templates.criteria("target_date") == list(patched)
    assert "> - `a-date` — a patched calendar date criterion (p. 0)" in skills.field_needs("define", "target_date")
    assert "a calendar date, in the future" not in skills.field_needs("define", "target_date")
    assert welcome.opening()[0] == (("Define", "a patched purpose"),)
    # The element order and the names: positions from the owner's order, names from the owner's table.
    order = list(owner.ELEMENT_ORDER)
    order[7], order[8] = order[8], order[7]                         # target_date before target_value
    try:
        with monkeypatch.context() as m:
            m.setattr(owner, "ELEMENT_ORDER", tuple(order))
            m.setitem(owner.ELEMENT_NAMES, "team", "The team, patched")
            for cached in (skills._field_blocks, skills._script_blocks, guard_messages._elements):
                cached.cache_clear()
            assert _field_blocks("define")["target_date"][0] == 8
            assert (skills.script_step("define", ["target_date"], None) or {})["position"] == 8
            assert guard_messages.element_name("define", "team") == "The team, patched"
    finally:
        for cached in (skills._field_blocks, skills._script_blocks, guard_messages._elements):
            cached.cache_clear()
    assert _field_blocks("define")["target_date"][0] == 9 and guard_messages.element_name("define", "team") == "Team"
