"""Captured values carry their declared type — procedure step 6.48 (`CO-1`).

**CAPABILITY ROW 18's CHECK LIVES HERE**, and it is deliberately the one test
in this file that builds no input of its own.

WHY THE ROW CHECK READS REAL DATA
---------------------------------
The defect this step closes survived for months underneath a full test suite,
and the reason is one line: **every fixture handed the capture path a value of
the right type.** `test_gate_documents._full()` builds `team` as a `list[dict]`
because the schema says so; `test_executor` built `"Ana, Bo"` because the test
was about something else. Neither ever asked what the COACH produces.

So a row check that seeds its own artifacts would have been **green throughout
the entire life of the defect**. That is the escape cause, and a check that
would not have caught the thing it is written for is not a check.

`test_row_18_captured_values_carry_their_declared_type` therefore reads the
case record the system actually wrote and asserts against that. **It SKIPS
rather than passes when there is no case to read**: by Appendix H's rules a row
is green or red, and a check that did not run is not green.

WHAT THE OTHER TESTS ARE
------------------------
The step's own proofs — the producer, driven end to end with a coach that emits
prose. They ARE fixture-driven, which is correct for proving a mechanism, and
they are why the row check is not asked to do both jobs.
"""
from __future__ import annotations

import asyncio
import json
import os
from typing import Any

import pytest

from backend.tests.conftest import store_plan
from langchain_core.messages import HumanMessage

from backend.core.substate import CoachingResponse, PhaseState
from backend.phases import nodes_common as _nc
from backend.phases.gate_registry import (
    GATE_SPECS,
    declared_type,
    split_by_declared_type,
)

#: The four Define fields §7's law exempts from being strings, and the four
#: this step was raised for. Derived from the schema, never typed out, so a
#: fifth structured field joins this set without anyone remembering to add it.
STRUCTURED_DEFINE_FIELDS = tuple(sorted(
    name for name, f in GATE_SPECS["define"].model.model_fields.items()
    if f.annotation is not str
    and name in set(GATE_SPECS["define"].tier_1)
))


def _state(**overrides: Any) -> PhaseState:
    base: PhaseState = {
        "case_id": "IMPR-TEST-648", "current_phase": "define",
        "messages": [HumanMessage(content="hello")], "history": [],
        "phase_context": "", "coaching_plan": None, "field_index": 0,
        "draft": {}, "artifacts": {}, "step_log": [], "field_log": [], "field_status": {},
        "belt_edits": {}, "turn_count": 0, "final": {}, "gate_attempts": 0,
        "validator_feedback": [], "rejection_feedback": [], "citations": [],
        "uploads": [], "asks": [], "hop_results": [], "synthesis_output": None,
    }
    base.update(overrides)  # type: ignore[typeddict-item]
    return base


# ══════════════════════════════════════════════════════════════════════════
# CAPABILITY ROW 18 — the persistent check, on real data
# ══════════════════════════════════════════════════════════════════════════


def test_row_18_captured_values_carry_their_declared_type() -> None:
    """**Row 18 · container 4.** Team, scope, the SIPOC map and the registry
    arrive structured, not as prose.

    Reads the case the system actually wrote. **Nothing here constructs a
    captured value** — that is the whole design of this check, because a seeded
    version of it would have been green while `IMPR-2026-0E5` held four
    structured fields as prose.
    """
    case_id = os.environ.get("CAPABILITY_CASE_ID", "IMPR-2026-0E5")
    from backend.storage import blob

    if not blob.storage_configured():
        pytest.skip(
            "no storage configured, so row 18 CANNOT BE EVALUATED. A skipped "
            "row is not a green row (Appendix H) — run against a real case."
        )

    case = asyncio.run(blob.load_case(case_id))
    if case is None:
        pytest.skip(f"{case_id} not found — row 18 cannot be evaluated")

    record = case.phases.get("define")
    captured = dict((record.structured or {}) if record else {})
    if not captured:
        pytest.skip(f"{case_id} has captured nothing — row 18 has no subject")

    _, malformed = split_by_declared_type("define", captured)
    assert not malformed, (
        "captured values that do not carry their declared type: "
        + json.dumps(malformed)
        + f" — of {len(captured)} captured field(s). A gate document cannot "
          "be assembled from these."
    )


# ══════════════════════════════════════════════════════════════════════════
# The step's own proofs — the PRODUCER, driven with a coach that emits prose
# ══════════════════════════════════════════════════════════════════════════


def _prose_reply() -> CoachingResponse:
    """What the live coach produced on 2026-09-23: every field as a sentence."""
    return CoachingResponse(
        message="Noted.",
        fields_captured=[
            {"field_name": "team",
             "value": "Ana Ruiz as lead, Ben Okafor as process owner.",
             "source": "belt"},
            {"field_name": "project_scope",
             "value": "In scope: UK billing. Out: credit notes.",
             "source": "belt"},
            {"field_name": "process_map_sipoc",
             "value": "Suppliers: purchasing. Inputs: POs. Steps: receive…",
             "source": "belt"},
            {"field_name": "metric_definitions",
             "value": "invoice_error_rate, measured in percent.",
             "source": "belt"},
            {"field_name": "business_case",
             "value": "Rework costs GBP 245,000 a year.", "source": "belt"},
        ],
    )


def test_all_four_structured_fields_are_refused_as_prose(stub_planner,
                                                         stub_coach) -> None:
    """The measured defect, as a test: four fields, all prose, none stored."""
    stub_coach.reply = _prose_reply()
    out = asyncio.run(_nc.executor("define", _state(coaching_plan=store_plan(stub_coach.reply))))

    assert set(out["artifacts"]) == {"business_case"}, (
        "a structured field was stored as prose"
    )
    for field in STRUCTURED_DEFINE_FIELDS:
        assert field not in out["artifacts"], field


def test_the_str_field_in_the_same_turn_is_untouched(stub_planner,
                                                     stub_coach) -> None:
    """**A refusal is per FIELD, not per turn** — §4.8. One malformed capture
    must not cost the Belt the four answers they gave correctly."""
    stub_coach.reply = _prose_reply()
    out = asyncio.run(_nc.executor("define", _state(coaching_plan=store_plan(stub_coach.reply))))
    assert out["artifacts"]["business_case"] == "Rework costs GBP 245,000 a year."


def test_the_turn_does_not_fail_for_the_belt(stub_planner, stub_coach) -> None:
    """§4.8 — never a hard failure to the Belt. The coaching text still
    reaches them, and the field simply stays uncaptured so the coach asks
    again in its own voice, in the same conversation."""
    stub_coach.reply = _prose_reply()
    out = asyncio.run(_nc.executor("define", _state(coaching_plan=store_plan(stub_coach.reply))))
    assert out["messages"], "the turn produced no reply"
    assert out["step_log"][0]["status"] != "error"


def test_the_refusal_is_reported_by_field_and_by_type(stub_planner,
                                                      stub_coach) -> None:
    """**Reported, never silently dropped** — 6.33's rule, applied to shape.

    The audit trail names the type each field needed, so *"why is this still
    blank on turn nine"* is answerable without re-running the turn.
    """
    stub_coach.reply = _prose_reply()
    out = asyncio.run(_nc.executor("define", _state(coaching_plan=store_plan(stub_coach.reply))))
    reported = out["step_log"][0]["fields_malformed"]
    assert reported == {
        "metric_definitions": "list[dict]",
        "process_map_sipoc": "dict",
        "project_scope": "dict",
        "team": "list[dict]",
    }


def test_a_well_typed_capture_is_stored_unchanged(stub_planner,
                                                  stub_coach) -> None:
    """**NOTHING IS COERCED.** The stored value is the object the coach sent,
    not a parsed copy of it — identity, not equality, is the assertion."""
    team = [{"name": "Ana", "role": "lead", "function": "finance"}]
    stub_coach.reply = CoachingResponse(
        message="Noted.",
        fields_captured=[{"field_name": "team", "value": team,
                          "source": "belt"}],
    )
    out = asyncio.run(_nc.executor("define", _state(coaching_plan=store_plan(stub_coach.reply))))
    assert out["artifacts"]["team"] is team


def test_prose_never_reaches_the_case_record_either(stub_planner) -> None:
    """**Both ends refuse, and this end is not belt-and-braces.**

    `structured` seeds the next turn's `artifacts`, so prose stored here is
    prose the accumulator inherits tomorrow — and the two records of one field
    would disagree, which is the condition step 6.33 closed one field over.
    """
    from backend.gateway.routes import apply_capture
    from backend.storage.models import CaseDocument

    case = CaseDocument.new(
        case_id="IMPR-TEST-648", title="T", belt_level="green", leader="L",
        department="D", target_date="2026-12-01", team=[],
    )
    apply_capture(case, "define", {"v1_draft": {
        "team": "Ana and Ben",
        "business_case": "Rework costs GBP 245,000 a year.",
    }})
    assert set(case.phases["define"].structured or {}) == {"business_case"}


# ══════════════════════════════════════════════════════════════════════════
# The split itself
# ══════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize("field", STRUCTURED_DEFINE_FIELDS)
def test_each_structured_field_rejects_prose(field: str) -> None:
    _, malformed = split_by_declared_type("define", {field: "a sentence"})
    assert field in malformed


def test_a_field_the_schema_does_not_declare_passes_through() -> None:
    """It has no declared type to carry, so there is nothing to enforce here.

    **That a name the schema does not know was captured at all is a different
    defect**, and reporting it under this one's name would send a reader
    looking for a shape problem in a field that has no shape.
    """
    kept, malformed = split_by_declared_type("define", {"not_a_field": "x"})
    assert kept == {"not_a_field": "x"} and malformed == {}
    assert declared_type("define", "not_a_field") is None


def test_the_declared_type_comes_from_the_schema_not_a_list() -> None:
    """The types are READ from `{Phase}Output`, so a schema change moves them.

    A hand-kept list of structured fields is the second copy that drifts —
    which is the failure mode `STRUCTURED_DEFINE_FIELDS` avoids by deriving.
    """
    assert declared_type("define", "team") == list[dict]
    assert declared_type("define", "business_case") is str
    assert set(STRUCTURED_DEFINE_FIELDS) == {
        "team", "project_scope", "process_map_sipoc", "metric_definitions",
        "critical_to_quality", "problem_5w2h", "benefits_analysis"}
