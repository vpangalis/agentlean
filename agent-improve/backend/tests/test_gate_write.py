"""The gate write — procedure step 6.42.

TWO CAPABILITY ROWS LIVE HERE, AND THEY READ WHAT THE SYSTEM WROTE
------------------------------------------------------------------
Row 20 — the document is WRITTEN, and safe to write twice.
Row 21 — the gate write preserves the change log and the uploads.

Both follow rows 18 and 19: **they construct no input, and they SKIP rather
than pass when there is nothing to read.** A row that could not be evaluated is
not a green row (Appendix H).

That design is not a style choice. `write_phase_gate` replaced the whole
`PhaseRecord` for the entire life of the project, dropping `field_log`,
`analyst_output` and the Belt's evidence trail — and **every test passed
throughout**, because no test approved a gate and every fixture that touched
the record built its own. A row check that seeded a record would have been
green the whole time too.

WHAT THE REST OF THE FILE IS
----------------------------
The mechanism's own proofs. These DO use fixtures, which is correct for proving
a mechanism — and it is why the two rows above are not asked to do both jobs.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any

import pytest

from backend.phases.gate_registry import GATE_SPECS
from backend.storage import blob
from backend.storage.models import CaseDocument, PhaseRecord, UploadRecord

PHASE = "define"

#: **The gate-proof case, and it is a SECOND case on purpose** — founder
#: ruling 2026-09-23, option B. Submitting a gate ADVANCES the case out of
#: Define, so proving the write on `IMPR-2026-0E5` would have ended the Define
#: proofs still owed: the ten checks, 6.46, 10.3 and 6.44 all need a live
#: define case. `IMPR-2026-0E5` therefore stays in define, and this case
#: carries the gate.
#:
#: It was coached to 13 of 13 through **real turns with the real model** —
#: nothing constructed — and its gate was submitted ONCE. Its title says so:
#: *"GATE PROOF — step 6.42, do not use for Define coaching proofs."*
#:
#: **A submitted case has advanced and cannot carry the next gate proof**, so
#: 7.3 will need a fresh one. Overridable by `CAPABILITY_GATE_CASE_ID`.
GATE_PROOF_CASE_ID = "IMPR-2026-1FF"


# ══════════════════════════════════════════════════════════════════════════
# CAPABILITY ROWS 20 AND 21 — on the case the system wrote
# ══════════════════════════════════════════════════════════════════════════


def _live_record():
    """The live case's define record, or a skip explaining which row cannot
    be evaluated. **Never constructs one.**"""
    case_id = os.environ.get("CAPABILITY_GATE_CASE_ID", GATE_PROOF_CASE_ID)
    if not blob.storage_configured():
        pytest.skip("no storage configured — the row cannot be evaluated")
    case = asyncio.run(blob.load_case(case_id))
    if case is None:
        pytest.skip(f"{case_id} not found — the row cannot be evaluated")
    record = case.phases.get(PHASE)
    if record is None or not record.gate_passed:
        pytest.skip(
            f"{case_id}'s {PHASE} gate has not been submitted, so no document "
            "has been written. The row asks about a WRITTEN document and there "
            "is none to ask of — this is NOT a pass."
        )
    return case, record


def test_row_20_the_document_is_written_and_safe_to_write_twice() -> None:
    """**Capability row 20**, read from `IMPR-2026-1FF` — the gate-proof case.

    Two halves, both checkable without writing anything:

    1. what was WRITTEN is a complete gate document — every field the schema
       declares, not the captured subset and not an empty dict;
    2. it is **exactly what assembly produces from the same artifacts, and
       assembly is deterministic** — which is why a second write cannot produce
       a different record. `write_phase_gate` stamps the approval on the
       TRANSITION only, so the second write is a no-op on the stamp as well.
    """
    case, record = _live_record()
    written = dict(record.structured or {})
    declared = set(GATE_SPECS[PHASE].model.model_fields)

    assert set(written) == declared, (
        "what was written is not a complete gate document: missing "
        f"{sorted(declared - set(written))}, unexpected "
        f"{sorted(set(written) - declared)}"
    )

    # Determinism, from the case's own captured values — the property that
    # makes a repeated write harmless.
    artifacts = {k: v for k, v in written.items()
                 if k in set(GATE_SPECS[PHASE].tier_1)}
    once = GATE_SPECS[PHASE].assemble(artifacts, [], [], []).model_dump()
    twice = GATE_SPECS[PHASE].assemble(artifacts, [], [], []).model_dump()
    assert once == twice, "assembly is not deterministic"
    assert record.submitted_at, "a passed gate carries no approval stamp"


def test_row_21_the_gate_write_preserves_the_change_log_and_the_uploads() -> None:
    """**Capability row 21**, read from `IMPR-2026-1FF` — the gate-proof case.

    The record that survived the gate still holds what the gate did not write.
    `field_log` is step 6.33's, and by the time a gate is approved the Belt has
    captured twelve fields, so it cannot legitimately be empty.
    """
    case, record = _live_record()
    assert record.field_log, (
        "the gate write dropped `field_log` — the change log 6.33 built is "
        "gone from the record the gate approved"
    )
    assert record.submitted_by, "the approval stamp lost its actor"


# ══════════════════════════════════════════════════════════════════════════
# The mechanism — fixtures, because that is what a mechanism proof is for
# ══════════════════════════════════════════════════════════════════════════


def _seeded_case() -> CaseDocument:
    """A case whose define record already holds what a gate must not destroy."""
    case = CaseDocument.new(
        case_id="IMPR-TEST-642", title="T", belt_level="green", leader="L",
        department="D", target_date="2026-12-01", team=[],
    )
    case.phases[PHASE] = PhaseRecord(
        structured={"business_case": "captured"},
        field_log=[{"key": "define:1:business_case", "field": "business_case",
                    "phase": PHASE, "turn": 1, "value": "captured",
                    "prior_value": None, "timestamp": "2026-09-23T09:00:00Z",
                    "reason": None}],
        uploads=[UploadRecord(filename="baseline.csv", blob_path="p",
                              uploaded_by="Belt", uploaded_at="2026-09-23",
                              classification="operational_data")],
        citations=[],
    )
    return case


@pytest.fixture
def written(monkeypatch):
    """`write_phase_gate` against an in-memory case, so the real merge runs.

    Patches the two I/O ends and the registry write; **everything between them
    — which is the whole of what this step changed — is the real function.**
    """
    case = _seeded_case()
    saved: list[CaseDocument] = []
    registry_calls: list[tuple] = []

    async def fake_load(case_id: str):
        return case

    async def fake_save(c: CaseDocument):
        saved.append(c)

    async def fake_registry(c, phase, summary, now):
        registry_calls.append((c.case_id, phase, summary, now))

    monkeypatch.setattr(blob, "load_case", fake_load)
    monkeypatch.setattr(blob, "save_case", fake_save)
    monkeypatch.setattr(blob, "_update_registry_entry", fake_registry)

    def write(**kwargs: Any) -> None:
        asyncio.run(blob.write_phase_gate(
            case_id=case.case_id, phase=PHASE,
            structured=kwargs.pop("structured", {"business_case": "captured"}),
            submitted_by=kwargs.pop("submitted_by", "Vassilis"),
            summary="Gate passed", **kwargs,
        ))

    return case, write, saved, registry_calls


def test_the_change_log_survives_the_gate(written) -> None:
    """**The defect, as a test.** 6.33 built `field_log`; the gate erased it."""
    case, write, _, _ = written
    before = [dict(e) for e in case.phases[PHASE].field_log]
    write()
    assert case.phases[PHASE].field_log == before


def test_the_uploads_survive_a_call_that_does_not_mention_them(written) -> None:
    """**The `[]` default was the loss.** The call site passed neither
    `citations` nor `uploads`, so the defaults replaced the Belt's evidence
    trail with nothing — at the one moment a reviewer goes looking for it."""
    case, write, _, _ = written
    assert case.phases[PHASE].uploads, "fixture is stale"
    write()
    assert len(case.phases[PHASE].uploads) == 1
    assert case.phases[PHASE].uploads[0].filename == "baseline.csv"


def test_supplied_uploads_replace_rather_than_being_ignored(written) -> None:
    """`None` means NOT SUPPLIED; an explicit list means supplied.

    The old signature could not tell those apart, which is the whole reason
    the defaults did damage.
    """
    case, write, _, _ = written
    write(uploads=[])
    assert case.phases[PHASE].uploads == []


def test_the_analyst_output_argument_is_actually_written(written) -> None:
    """It was accepted as a parameter and dropped on the floor."""
    case, write, _, _ = written
    write(analyst_output={"summary": "s", "generated_at": "2026-09-23T09:00:00Z"})
    assert case.phases[PHASE].analyst_output is not None


def test_the_gate_document_replaces_the_captured_subset(written) -> None:
    """`structured` is the DOCUMENT after a gate, not the captured fields.

    That is the one field the gate is supposed to overwrite, and it must not
    be caught by the preservation the rest of the record gets.
    """
    case, write, _, _ = written
    write(structured={"business_case": "captured", "phase_metrics": []})
    assert "phase_metrics" in (case.phases[PHASE].structured or {})


# ── idempotence — the framework requires it (interrupts, 2026-09-23) ──────


def test_writing_twice_leaves_one_document_and_one_stamp(written) -> None:
    """**Write, write again, assert one document and no duplication.**

    The runtime *"restarts the entire node from the beginning"* on resume, so
    when 7.3 moves this write behind a pause EVERY resume re-runs it. A
    timestamp that moved on the second write would make one approval look like
    two.
    """
    case, write, saved, _ = written
    write()
    first = case.phases[PHASE].model_dump()
    write()
    second = case.phases[PHASE].model_dump()

    assert first == second, "the second write changed the record"
    assert len(saved) == 2, "both writes should have persisted"
    assert case.phases[PHASE].submitted_at == first["submitted_at"]


def test_the_phase_advance_is_the_same_answer_twice(written) -> None:
    """`current_phase` is computed from the `phase` argument, never from the
    case's current value — so it lands on `measure` however many times it
    runs, rather than walking the project down the DMAIC chain on resumes."""
    case, write, _, _ = written
    write()
    write()
    assert case.current_phase == "measure"


def test_a_reopened_gate_is_stamped_again(written) -> None:
    """**The stamp records when the gate LAST became passed.**

    §37's re-approval cascade sets `gate_passed` back to `False`; the next
    write is then a transition again and re-stamps. Idempotence must not
    freeze the record against a genuine second approval.
    """
    case, write, _, _ = written
    write(submitted_by="Vassilis")
    case.phases[PHASE].gate_passed = False          # §37 reopens it
    write(submitted_by="Ana")
    assert case.phases[PHASE].submitted_by == "Ana"


def test_the_registry_is_updated_in_place_not_appended(written) -> None:
    """The other place a repeated write could duplicate. It matches on
    `case_id` and updates; two writes are two updates, not two entries."""
    case, write, _, registry_calls = written
    write()
    write()
    assert {c[0] for c in registry_calls} == {case.case_id}
    assert {c[1] for c in registry_calls} == {PHASE}
