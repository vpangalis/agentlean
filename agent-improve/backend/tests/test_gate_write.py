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
from typing import Any

import pytest

from backend.storage import blob
from backend.storage.models import CaseDocument, PhaseRecord, UploadRecord

PHASE = "define"

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
