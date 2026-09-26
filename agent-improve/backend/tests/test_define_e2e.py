"""Define's end-to-end feature tests — the real route and graph, fake models. Step 6.67.

One test per feature of `docs/define_features.json` whose test lives here. A test
not written yet is a STUB that fails with "not written yet", so the feature's node
id exists (founder ruling 2026-09-26, Part C) and the feature honestly reads
failing. The lane that takes the feature replaces the stub with the real test —
the route-level fake harness to copy is `test_wiring.py`'s `three_turns` fixture.

Feature tests record the measurement, never block a commit: non-strict xfail.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.xfail(strict=False, reason="a Define feature test — its outcome is the measurement")


def _not_written(fid: str) -> None:
    pytest.fail(f"{fid}: not written yet — the lane that takes this feature writes it")


def test_a_new_case_opens_in_define() -> None:
    """DEF-001 — A Belt creates a new case and it opens in Define: POST /cases returns an id, the case list shows it, and GET /cases/{id} opens it with current_phase '"""
    _not_written('DEF-001')


def test_every_node_of_a_turn_is_checkpointed() -> None:
    """DEF-003 — Every node of a Define turn leaves a checkpoint, so a crash loses at most one node's work."""
    _not_written('DEF-003')


def test_a_qualified_yes_is_treated_as_a_correction() -> None:
    """DEF-009 — A typed plain yes confirms like the button; a yes carrying 'but/actually/change…' is treated as a correction and judged again."""
    _not_written('DEF-009')


def test_coherence_judges_the_belts_words() -> None:
    """DEF-013 — The coherence judge rules on the Belt's words, not the coach's: a reply that quotes the script is not degraded, a real parrot still is."""
    _not_written('DEF-013')


def test_a_coherence_rejection_asks_the_coach_again() -> None:
    """DEF-014 — When coherence rejects a reply, the coach is asked again inside the turn (a new model call), within the latency the founder rules."""
    _not_written('DEF-014')


def test_every_turn_is_graded_on_all_four_blocks() -> None:
    """DEF-015 — Every coaching turn is graded by the coaching rubric, the grader sees all four blocks (not only 'message'), and its verdict lands in step_log."""
    _not_written('DEF-015')


def test_the_savings_calculation_is_taught_and_reads_percent_once() -> None:
    """DEF-016 — The savings calculation is TAUGHT before its number is given, and '23%', '23' and '0.23' give the same saving (one percent convention)."""
    _not_written('DEF-016')


def test_a_calculation_is_recorded_with_its_five_keys() -> None:
    """DEF-017 — A calculation the coach ran is recorded in computation_results with its five keys and appears in the gate document without the coach retyping the numb"""
    _not_written('DEF-017')


def test_the_belt_can_see_captured_and_missing_fields() -> None:
    """DEF-020 — At any point the Belt can ask what is done and what is missing, and the coach shows the captured and missing fields from check_gate_status — the same """
    _not_written('DEF-020')


def test_a_correction_keeps_the_belts_reason() -> None:
    """DEF-021 — When the Belt corrects a stored value, their stated reason is kept with the change in field_log.reason."""
    _not_written('DEF-021')


def test_a_confirmed_field_can_be_revised() -> None:
    """DEF-022 — A Belt can revise a field they already confirmed while a later field is current, and the revision is judged, read back and re-confirmed."""
    _not_written('DEF-022')


def test_the_script_is_not_fetched_again() -> None:
    """DEF-023 — The coach does not fetch the Define script it already has in its system message (no load_skill call on a Define turn)."""
    _not_written('DEF-023')


def test_structured_fields_arrive_structured_or_are_refused() -> None:
    """DEF-038 — Captured values keep their declared type end to end: team, scope, SIPOC and the registry are stored structured, and prose for a structured field is re"""
    _not_written('DEF-038')


def test_a_contradiction_stops_in_a_node_and_resumes() -> None:
    """DEF-040 — When the Belt contradicts a value an earlier gate approved, the turn stops in a node that writes nothing, the Belt chooses update or keep, and the res"""
    _not_written('DEF-040')


def test_the_metric_entry_mirrors_the_confirmed_scalars() -> None:
    """DEF-042 — The gate document's phase_metrics entry mirrors the confirmed baseline and target, derived at assembly with no model call."""
    _not_written('DEF-042')


def test_a_submission_missing_a_field_is_refused_by_name() -> None:
    """DEF-043 — Layer 2b refuses a gate submission missing any of the thirteen gate-required fields and names what is missing; the prompt's missing list and the valid"""
    _not_written('DEF-043')


def test_the_rubric_grades_the_gate_document_and_can_fail_it() -> None:
    """DEF-044 — At the gate, constraints (2c) and the Define rubric (2d) grade the document and can send it back to coaching with feedback; the shared cap is 3."""
    _not_written('DEF-044')


def test_define_gate_has_no_warning_path() -> None:
    """DEF-045 — Define's gate has no Tier 2: it never issues a 'warning' verdict and acknowledged_gaps is always empty."""
    _not_written('DEF-045')


def test_three_failed_gate_attempts_escalate() -> None:
    """DEF-046 — After three failed gate attempts the case is escalated to a person instead of looping."""
    _not_written('DEF-046')


def test_a_belt_edit_at_the_gate_is_advised_not_blocked() -> None:
    """DEF-051 — At the paused gate the Belt may edit a field; a non-blocking policy advisory checks the edit, and the edited value is what is written."""
    _not_written('DEF-051')


def test_the_four_blocks_reach_the_screen() -> None:
    """DEF-052 — The workspace shows the coach's four blocks — explanation, example, prompt, and progress — plus the grader's warning when there is one."""
    _not_written('DEF-052')


def test_the_progress_bar_and_next_step_follow_the_coach() -> None:
    """DEF-053 — The progress bar reads 'n of 12' from define_progress and moves turn by turn; the suggested next step always names the field the coach is on."""
    _not_written('DEF-053')


def test_the_read_back_buttons_send_the_action() -> None:
    """DEF-054 — Under a read-back the screen shows Confirm and Change; a click sends action=confirm|change on /ask and the Belt's side shows the button pressed."""
    _not_written('DEF-054')


def test_a_failed_turn_is_readable_and_stays() -> None:
    """DEF-055 — A failed turn tells the Belt what happened in words, stays on screen, and never renders an error as an empty state."""
    _not_written('DEF-055')


def test_an_upload_lands_once_and_is_indexed() -> None:
    """DEF-056 — The Belt can upload evidence to a Define case; the file lands, is indexed once, and carries an interpretation — and files picked on the create screen """
    _not_written('DEF-056')


def test_the_coach_quotes_an_uploaded_document() -> None:
    """DEF-057 — The coach can read a document the Belt uploaded and quote a line from it (e.g. from an uploaded process map)."""
    _not_written('DEF-057')


def test_the_gate_screen_shows_the_document_and_acts_on_the_pause() -> None:
    """DEF-058 — The gate screen shows the live gate document (one progress bar for Define), and the approve/reject controls act on the paused gate."""
    _not_written('DEF-058')


def test_the_reply_streams_and_a_drop_abandons() -> None:
    """DEF-059 — The coach's reply appears as it is written (server-sent events), and a dropped client abandons the turn."""
    _not_written('DEF-059')


def test_an_approval_writes_the_record_once() -> None:
    """DEF-060 — On approval the Define record is written once: the store (projects/{case}/artifacts/define.json), PhaseState.final and the case record agree, and writ"""
    _not_written('DEF-060')


def test_the_gate_write_keeps_the_change_log_and_uploads() -> None:
    """DEF-061 — The gate write keeps the Belt's change log, citations and uploads."""
    _not_written('DEF-061')


def test_measure_starts_from_the_approved_define_record() -> None:
    """DEF-062 — After approval the case advances to Measure, and Measure starts from the approved Define record without PriorGateDocumentMissing."""
    _not_written('DEF-062')
