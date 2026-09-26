"""R2 and R4 — what the coach teaches for each Define element, and the thirteen.

Founder requirements (`docs/requirements/define.md`, 2026-09-26):

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
        assert criteria and all("(p. " in text for _, text in criteria), (field, criteria)
    # The 5W2H and the SIPOC show the COMPLETED diagram, as a table.
    fivew = " ".join(_sections(blocks["problem_statement"][1])["Show"])
    sipoc = " ".join(_sections(blocks["process_map_sipoc"][1])["Show"])
    for question in ("What", "Where", "When", "Who", "Why", "How", "How much"):
        assert f"| {question} |" in fivew, question
    assert "| Suppliers | Inputs | Process | Outputs | Customers |" in sipoc
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
    assert "EXPECTED SAVINGS" in block and "68040.00" in block and "cost_of_gap" in block
