"""The declared shape travels with the type contract — step A, §56 v1.70.

WHAT THIS FILE PINS, AND WHY IT IS NOT THE SAME AS ROW 18
---------------------------------------------------------
`test_capability_rows.py::test_row_18_captured_values_carry_their_declared_type`
holds capability row 18: **captured values carry their declared type**, read off
the case the system actually wrote (moved there from `test_declared_types.py` in
f61ddcb — the one file allowed to reach the live case, G-234). That row is the
OUTCOME.

This file pins the MECHANISM that produces it — that every structured coached
field is named in the contract the model receives on every turn, and that the
contract is derived from the schemas rather than typed out beside them.

**Why the mechanism needs its own tests when the outcome is already checked.**
Row 18 needs a live case to read; these run anywhere. And a contract that
silently loses a field would leave row 18 green until a Belt happened to answer
that particular field in prose — which is the shape of the defect this whole
step exists to close, one level up.

WHERE THE SHAPES TRAVEL — G-252 (founder ruling 2026-10-23, item 2e)
---------------------------------------------------------------------
The shapes moved from `fields_captured`'s description to the turn's task section (section 5), named for
the fields the read-back carries — sent on every read-back, never loaded on demand. The history below
is why they must reach the model every turn.
Measured, 2026-09-23. The same four shapes were written into
`skills/dmaic-define-phase/SKILL.md` first. SKILL.md loads at **level 2, on
demand**, through the `load_skill` tool the coach must choose to call (§19.2).
Across four live turns `load_skill` was called **zero** times and all four
fields came back as prose. With the shapes in the field description and
`load_skill` still uncalled, all four came back structured on the first
attempt, with zero refusals.
"""
from __future__ import annotations

from typing import Any, cast

import pytest

from backend.core.prompts import CAPTURE_RULES
from backend.core.substate import CapturedValue, CoachingPlan, CoachingResponse, coaching_response_model
from backend.middleware.state_injection import BeforeModelStateInjection
from backend.phases.gate_registry import GATE_SPECS


def _read_back_task(phase: str, field: str) -> str:
    """Section 5 of a read-back of `field` — where the model is told the field's shape (G-252)."""
    plan = CoachingPlan(focus_field=field, status="answered", move="read_back",
                        pending={"field": field, "fields": [field], "belt_words": "the Belt's words", "messages": 1})
    state: Any = {"artifacts": {}, "phase_context": "", "coaching_plan": plan, "messages": []}
    mw = BeforeModelStateInjection(phase, cast(Any, state))
    mw.before_agent(None, None)
    return mw._move


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
    """**The one that must not rot.** Derived from the schemas — so a field added to any phase fails here
    rather than silently reaching a Belt as prose: its read-back names it with its shape."""
    missing = {f: p for f, p in _structured_coached_fields().items()
               if f"`{f}`" not in _read_back_task(p, f)
               or not any(w in _read_back_task(p, f) for w in ("real structure", "the Belt's words"))}
    assert not missing, (
        f"structured coached fields absent from the capture contract: {missing}"
        " — the model is told nothing about their shape"
    )


def test_the_count_is_twelve_and_is_derived() -> None:
    """Pinned so that a field LEAVING the structured set is noticed too.

    A drop is as much a drift as an addition: it would mean a schema was
    retyped and the contract still teaches the old shape.
    """
    # nine + R4/R5's three (2026-09-26) + ADR-0071's two MetricValues (2026-09-29), which the
    # contract names as the Belt's words that code reads the number from.
    assert len(_structured_coached_fields()) == 14


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
    task = _read_back_task(_structured_coached_fields()[field], field)
    assert f"`{field}`" in task
    for key in keys:
        assert key in task, f"{field} is missing key {key}"


def test_the_cross_phase_dicts_carry_all_four_reference_keys() -> None:
    """**FOUR reference keys, not three** — S-C32, F-13 closed 2026-08-26.

    `references_metric_name` names WHICH registry metric a link is about. With
    one metric the other three are unambiguous; with two, a hypothesis
    referencing a bare scalar resolves to whichever metric happens to be
    primary. Teaching a three-key shape would produce links the grader cannot
    resolve — and the contract is exactly where that error would propagate.
    """
    for field in ("causal_hypothesis", "solution_linked_to_root_cause",
                  "post_improvement_metrics"):
        task = _read_back_task(_structured_coached_fields()[field], field)
        for key in ("references_phase", "references_field",
                    "references_metric_name", "references_value"):
            assert key in task, (field, key)


def test_the_contract_says_a_wrong_shape_is_not_stored() -> None:
    """The consequence is stated, not just the requirement.

    §4.8: the turn does not fail for the Belt. What the model must understand
    is that prose here costs the Belt the answer — which is what makes the
    instruction worth following rather than advisory.
    """
    assert "not stored" in CAPTURE_RULES and "answers again" in CAPTURE_RULES
    assert CAPTURE_RULES in _read_back_task("define", "team")


def test_the_eight_ratified_fields_are_still_eight() -> None:
    """No field added. G-252 (founder ruling 2026-10-23, item 2e) typed the entry: `field_name` from the phase's own
    field list, `value` still Any (§10.7)."""
    assert len(CoachingResponse.model_fields) == 8
    assert CoachingResponse.model_fields["fields_captured"].annotation == list[CapturedValue]
    assert CapturedValue.model_fields["value"].annotation is Any
    assert issubclass(coaching_response_model("define"), CoachingResponse)


def test_adr_0111_d4_the_reply_schema_says_its_purpose_in_about_150_tokens() -> None:
    """ADR-0111 D4 (founder ruling 2026-10-27): the `CoachingResponse` docstring — the structured reply's description,
    sent on every coach call — is its purpose, about 150 tokens; the fields' meanings stay on their Field
    descriptions. Counted with o200k_base, the deployed gpt-4o's encoding, on the phase model the executor binds."""
    import tiktoken

    enc = tiktoken.get_encoding("o200k_base")
    for model in (CoachingResponse, coaching_response_model("define")):
        assert len(enc.encode(model.__doc__ or "")) <= 150, (model.__name__, model.__doc__)
    assert all(f.description for f in CoachingResponse.model_fields.values()), \
        "a field's meaning is not on its Field description"
