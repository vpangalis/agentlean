"""Tests for the v2 state schemas — procedure step 3.1.

Reference §5 · §6 · §7, and the canonical entries **S-C01** (`SupervisorState`)
and **S-C02** (`PhaseState`), both of which carry a *rebuild test*: each class
must be reconstructable from its spec entry alone.

The expected field names are transcribed from those entries as literals rather
than derived from the modules under test. A test that reads its expectation out
of the code it is testing asserts nothing.

Nothing here builds a graph — step 3.1 declares the schemas and wires nothing.
"""
from __future__ import annotations

import operator
import typing

import pytest

from backend.core import state as state_module
from backend.core import substate as substate_module
from backend.core.state import (
    SUPERVISOR_STATE_DERIVED_FIELDS,
    SUPERVISOR_STATE_FIELDS,
    SUPERVISOR_STATE_REMOVED_FIELDS,
    SupervisorState,
)
from backend.core.substate import (
    PHASE_STATE_CONTENT_FIELDS,
    PHASE_STATE_IDENTITY_FIELDS,
    PHASE_STATE_PLUMBING_FIELDS,
    PHASE_STATE_READ_ONLY_FIELDS,
    PhaseState,
)

# ── S-C01, transcribed ────────────────────────────────────────────────────
SUPERVISOR_EXPECTED = [
    "messages", "history", "case_id", "phase_index", "current_phase",
    "gate_passed", "final_output",
]

# ── S-C02, transcribed: 2 identity + 3 plumbing + 14 content ──────────────
PHASE_IDENTITY = ["case_id", "current_phase"]
PHASE_PLUMBING = ["messages", "history", "phase_context"]
PHASE_CONTENT = [
    "coaching_plan", "field_index", "draft", "artifacts", "step_log",
    "belt_edits", "turn_count", "final", "gate_attempts",
    "validator_feedback", "citations", "uploads", "hop_results",
    "synthesis_output",
]
PHASE_EXPECTED = PHASE_IDENTITY + PHASE_PLUMBING + PHASE_CONTENT


def _annotations(td: type) -> dict:
    """Resolved annotations, keeping `Annotated` metadata.

    `from __future__ import annotations` makes every annotation a string, so
    the reducers are only visible after resolution — which is also how
    LangGraph reads them.
    """
    return typing.get_type_hints(td, include_extras=True)


def _reducer(td: type, field: str):
    """The reducer attached to `field`, or None if it carries no `Annotated`."""
    hint = _annotations(td)[field]
    if typing.get_origin(hint) is not typing.Annotated:
        return None
    metadata = typing.get_args(hint)[1:]
    return metadata[0] if metadata else None


# ── SupervisorState — §5 / S-C01 ──────────────────────────────────────────

def test_supervisor_state_has_exactly_seven_fields() -> None:
    """§5: 'Seven fields. That is the entire schema.' An eighth needs §56."""
    assert len(SUPERVISOR_EXPECTED) == 7
    assert list(SupervisorState.__annotations__) == SUPERVISOR_EXPECTED
    assert list(SUPERVISOR_STATE_FIELDS) == SUPERVISOR_EXPECTED


def test_supervisor_state_is_total() -> None:
    """S-C01 declares a plain TypedDict — every field required."""
    assert SupervisorState.__total__ is True


@pytest.mark.parametrize("field", ["messages", "history"])
def test_supervisor_append_only_fields_use_operator_add(field: str) -> None:
    """S-C01: `messages` and `history` are appended, never replaced."""
    assert _reducer(SupervisorState, field) is operator.add


@pytest.mark.parametrize(
    "field", ["case_id", "phase_index", "current_phase", "gate_passed", "final_output"]
)
def test_supervisor_remaining_fields_carry_no_reducer(field: str) -> None:
    """S-C01's field table: the other five have no reducer.

    `gate_passed` in particular is a whole-dict replace by its single writer,
    not a merge — the re-approval cascade (§37) sets a phase back to False.
    """
    assert _reducer(SupervisorState, field) is None


def test_supervisor_derived_fields_are_the_documented_three() -> None:
    """§5 B2: the output mapper writes these three together, and nothing else
    writes any of them."""
    assert set(SUPERVISOR_STATE_DERIVED_FIELDS) == {
        "phase_index", "current_phase", "gate_passed",
    }


def test_removed_supervisor_fields_have_not_returned() -> None:
    """§5: four fields were removed as redundant and 'may not return'."""
    assert set(SUPERVISOR_STATE_REMOVED_FIELDS) == {
        "dmaic_plan", "key_decisions", "open_items", "project_context",
    }
    for field in SUPERVISOR_STATE_REMOVED_FIELDS:
        assert field not in SupervisorState.__annotations__


def test_artifacts_and_gate_documents_are_not_on_supervisor_state() -> None:
    """§5: 'Captured fields and gate documents are NOT on SupervisorState.'

    They live on PhaseState and in the Store. §5 calls putting them back
    structural rather than stylistic.
    """
    for field in ("artifacts", "draft", "final", "step_log", "belt_edits"):
        assert field not in SupervisorState.__annotations__


# ── PhaseState — §6 / S-C02 ───────────────────────────────────────────────

def test_phase_state_has_exactly_nineteen_fields() -> None:
    """§6: 'Nineteen fields — two identity, three plumbing, fourteen content.'

    Note for reviewers: the procedure's step 3.1 'Done when' line says 17.
    That figure contradicts the same step's own Change and Prompt lines (19)
    and reference §6/S-C02 (19). The reference is authoritative (§0.12), so
    this asserts 19.
    """
    assert len(PHASE_IDENTITY) == 2
    assert len(PHASE_PLUMBING) == 3
    assert len(PHASE_CONTENT) == 14
    assert len(PHASE_EXPECTED) == 19
    assert list(PhaseState.__annotations__) == PHASE_EXPECTED


def test_phase_state_census_matches_the_schema() -> None:
    """The module's own census constants must not drift from the class."""
    assert list(PHASE_STATE_IDENTITY_FIELDS) == PHASE_IDENTITY
    assert list(PHASE_STATE_PLUMBING_FIELDS) == PHASE_PLUMBING
    assert list(PHASE_STATE_CONTENT_FIELDS) == PHASE_CONTENT


def test_phase_state_is_total() -> None:
    """S-C02 B1: entering a subgraph populates every one of the nineteen
    fields; no field is left undeclared."""
    assert PhaseState.__total__ is True


@pytest.mark.parametrize("field", ["messages", "history", "step_log"])
def test_phase_append_only_fields_use_operator_add(field: str) -> None:
    """S-C02: exactly three fields accumulate via a reducer.

    `step_log` is the audit trail (HOW), separate from `artifacts` (WHAT).
    """
    assert _reducer(PhaseState, field) is operator.add


def test_phase_state_has_exactly_three_reduced_fields() -> None:
    reduced = {f for f in PHASE_EXPECTED if _reducer(PhaseState, f) is not None}
    assert reduced == {"messages", "history", "step_log"}


def test_artifacts_and_validator_feedback_carry_no_reducer() -> None:
    """S-C02's table: both are written by their writer, not merged by a
    reducer — `artifacts` merges in the writer, `validator_feedback` appends
    in the writer and is reset to [] by `gate_apply` (B4). A reducer would
    make the reset impossible."""
    assert _reducer(PhaseState, "artifacts") is None
    assert _reducer(PhaseState, "validator_feedback") is None


def test_gate_attempts_is_on_phase_state() -> None:
    """§6, the field whose absence recreated a production bug.

    v1 held the equivalent counter in route scope, so every request rebuilt
    it at 0, the cap never fired, and the loop reported attempt 1
    indefinitely. It must be on PhaseState and therefore in the checkpoint.
    """
    assert "gate_attempts" in PhaseState.__annotations__
    assert _annotations(PhaseState)["gate_attempts"] is int


def test_validator_feedback_and_belt_edits_stay_separate() -> None:
    """§6: two actors at two moments (§33), and they must not be merged.

    A single conflated `feedback` field would have the coach reading the
    Belt's own corrections as validation failures.
    """
    assert "validator_feedback" in PhaseState.__annotations__
    assert "belt_edits" in PhaseState.__annotations__
    assert "feedback" not in PhaseState.__annotations__


def test_artifacts_and_step_log_stay_separate() -> None:
    """S-C02 invariant: WHAT was captured and HOW are different fields."""
    assert "artifacts" in PhaseState.__annotations__
    assert "step_log" in PhaseState.__annotations__


def test_copy_down_fields_are_the_two_identity_fields() -> None:
    """S-C02 B8/B9: `case_id` and `current_phase` are copied down at entry
    and are read-only inside the subgraph."""
    assert set(PHASE_STATE_READ_ONLY_FIELDS) == {"case_id", "current_phase"}


def test_step_index_is_never_reintroduced() -> None:
    """§6 naming discipline: `phase_index` (which phase) and `field_index`
    (which field within a phase) are distinct. `step_index` is the ambiguity
    the rename removed and must not come back."""
    assert "step_index" not in PhaseState.__annotations__
    assert "step_index" not in SupervisorState.__annotations__
    assert "field_index" in PhaseState.__annotations__
    assert "phase_index" in SupervisorState.__annotations__


def test_no_typed_computation_fields_on_phase_state() -> None:
    """§7: computation output goes in `artifacts["computation_results"]`.

    'No new top-level PhaseState field, and no per-phase typed destinations.'
    """
    assert "computation_results" not in PhaseState.__annotations__
    for field in PHASE_EXPECTED:
        assert not field.startswith("computation_")


# ── the two schemas are distinct, and v1 is untouched ─────────────────────

def test_supervisor_and_phase_state_are_different_schemas() -> None:
    """The two-level split is the point (§5, §6). Overlap is limited to the
    two copied-down identity fields plus the two plumbing lists."""
    overlap = set(SupervisorState.__annotations__) & set(PhaseState.__annotations__)
    assert overlap == {"case_id", "current_phase", "messages", "history"}


def test_v1_schema_still_exists_until_step_11_1() -> None:
    """The procedure keeps `ImproveGraphState` alive until 11.1; both coexist
    until the last v1 consumer is gone. Step 3.1 must not have removed it."""
    assert hasattr(state_module, "ImproveGraphState")
    assert state_module.ImproveGraphState.__total__ is False


def test_step_3_1_wires_nothing_into_a_graph() -> None:
    """3.1 declares the schemas and no more; the v1 capture path is NOT
    repointed at them (WATCH 7 — the Define gate stays inert until 6.2).
    """
    for module in (state_module, substate_module):
        source_names = dir(module)
        assert "StateGraph" not in source_names
        assert "get_graph" not in source_names
