"""The declared shape travels with the type contract — step A, §56 v1.70.

WHAT THIS FILE PINS, AND WHY IT IS NOT THE SAME AS ROW 18
---------------------------------------------------------
`test_declared_types.py` holds capability row 18: **captured values carry their
declared type**, read off the case the system actually wrote. That row is the
OUTCOME.

This file pins the MECHANISM that produces it — that every structured coached
field is named in the contract the model receives on every turn, and that the
contract is derived from the schemas rather than typed out beside them.

**Why the mechanism needs its own tests when the outcome is already checked.**
Row 18 needs a live case to read; these run anywhere. And a contract that
silently loses a field would leave row 18 green until a Belt happened to answer
that particular field in prose — which is the shape of the defect this whole
step exists to close, one level up.

WHY A DESCRIPTION AND NOT THE COACHING SCRIPT
---------------------------------------------
Measured, 2026-09-23. The same four shapes were written into
`skills/dmaic-define-phase/SKILL.md` first. SKILL.md loads at **level 2, on
demand**, through the `load_skill` tool the coach must choose to call (§19.2).
Across four live turns `load_skill` was called **zero** times and all four
fields came back as prose. With the shapes in the field description and
`load_skill` still uncalled, all four came back structured on the first
attempt, with zero refusals.
"""
from __future__ import annotations

import pytest

from backend.core.substate import CoachingResponse
from backend.phases.gate_registry import GATE_SPECS

CONTRACT = CoachingResponse.model_fields["fields_captured"].description or ""


def _structured_coached_fields() -> dict[str, str]:
    """Every coached field on any phase whose declared type is not `str`.

    **Derived from the five schemas, never typed here.** A hand-kept list is
    the second copy that drifts, and the drift would be silent: the contract
    would simply stop mentioning a field, and nothing would fail until a Belt
    answered it.
    """
    out: dict[str, str] = {}
    for phase, spec in GATE_SPECS.items():
        coached = set(spec.tier_1) | set(spec.tier_2)
        for name, field in spec.model.model_fields.items():
            if name in coached and field.annotation is not str:
                out[name] = phase
    return out


def test_the_contract_names_every_structured_coached_field() -> None:
    """**The one that must not rot.** Nine fields today, derived from the
    schemas — so a tenth added to any phase fails here rather than silently
    reaching a Belt as prose."""
    missing = {f: p for f, p in _structured_coached_fields().items()
               if f not in CONTRACT}
    assert not missing, (
        f"structured coached fields absent from the capture contract: {missing}"
        " — the model is told nothing about their shape"
    )


def test_the_count_is_twelve_and_is_derived() -> None:
    """Pinned so that a field LEAVING the structured set is noticed too.

    A drop is as much a drift as an addition: it would mean a schema was
    retyped and the contract still teaches the old shape.
    """
    assert len(_structured_coached_fields()) == 12   # nine + R4/R5's three (2026-09-26)


@pytest.mark.parametrize("field,keys", [
    ("team", ("name", "role", "function")),
    ("critical_to_quality", ("customer", "need", "requirement")),
    ("problem_5w2h", ("what", "where", "when", "who", "why", "how", "how_much")),
    ("benefits_analysis", ("cost_of_gap", "impact_type", "realisation_schedule",
                           "finance_contact")),
    ("metric_definitions", ("name", "unit", "meaning")),
    ("project_scope", ("in_scope", "out_scope")),
    ("process_map_sipoc", ("suppliers", "inputs", "process_steps",
                           "outputs", "customers", "process_metrics")),
    ("detailed_process_map", ("steps", "cycle_times", "resources",
                              "value_vs_waste", "measurement_points",
                              "baseline_metrics")),
    ("control_plan", ("documentation", "monitoring", "response",
                      "training", "aligning_systems")),
])
def test_each_structured_field_carries_its_keys(field: str,
                                                keys: tuple[str, ...]) -> None:
    """The model is told the KEYS, not merely that the value is an object.

    Without them it invents plausible ones, the value passes the declared-type
    check at capture (step 6.48 checks the TYPE), and the wrong keys reach the
    gate — a green row over a value nothing downstream can read.
    """
    assert field in CONTRACT
    for key in keys:
        assert key in CONTRACT, f"{field} is missing key {key}"


def test_the_cross_phase_dicts_carry_all_four_reference_keys() -> None:
    """**FOUR reference keys, not three** — S-C32, F-13 closed 2026-08-26.

    `references_metric_name` names WHICH registry metric a link is about. With
    one metric the other three are unambiguous; with two, a hypothesis
    referencing a bare scalar resolves to whichever metric happens to be
    primary. Teaching a three-key shape would produce links the grader cannot
    resolve — and the contract is exactly where that error would propagate.
    """
    for key in ("references_phase", "references_field",
                "references_metric_name", "references_value"):
        assert key in CONTRACT, key
    for field in ("causal_hypothesis", "solution_linked_to_root_cause",
                  "post_improvement_metrics"):
        assert field in CONTRACT, field


def test_the_contract_says_a_wrong_shape_is_not_stored() -> None:
    """The consequence is stated, not just the requirement.

    §4.8: the turn does not fail for the Belt. What the model must understand
    is that prose here costs the Belt the answer — which is what makes the
    instruction worth following rather than advisory.
    """
    assert "NOT STORED" in CONTRACT
    assert "uncaptured" in CONTRACT


def test_the_eight_ratified_fields_are_still_eight() -> None:
    """**A description, not a type change.** The §56 amendment moved what the
    model is TOLD; it did not add a field, and a per-phase response schema
    stays ruled out."""
    assert len(CoachingResponse.model_fields) == 8
    assert CoachingResponse.model_fields["fields_captured"].annotation == list[dict]
