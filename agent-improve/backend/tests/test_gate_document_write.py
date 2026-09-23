"""`POST /gate` builds its document by assembly — procedure step 6.42, half 1.

`assemble_gate_document` is driven directly rather than through the route,
because the route needs FastAPI, a blob client and a graph turn, and none of
those is what this step changed. **It is the function the route calls**, not a
copy of its logic — lifted out for exactly that reason, as `apply_capture` was
at 6.33.
"""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from backend.gateway.routes import assemble_gate_document
from backend.phases.gate_registry import GATE_SPECS
from backend.storage.models import CaseDocument, PhaseRecord

PHASE = "define"

COMPLETE = {
    "business_case": "Rework costs GBP 245,000 a year.",
    "team": [{"name": "Ana", "role": "lead", "function": "finance"}],
    "voc_summary": "Suppliers want invoices right first time.",
    "problem_statement": "UK invoices are wrong 12% of the time.",
    "baseline_estimate": "12%",
    "project_scope": {"in_scope": "UK billing", "out_scope": "credit notes"},
    "goal_statement": "Cut invoice errors to 3% by December 2026.",
    "target_value": "3%",
    "target_date": "2026-12-01",
    "secondary_metrics": "Invoice cycle time must not rise.",
    "process_map_sipoc": {"suppliers": "s", "inputs": "i", "process_steps": "p",
                          "outputs": "o", "customers": "c",
                          "process_metrics": "m"},
    "issues_and_barriers": "none identified at this stage",
    "metric_definitions": [{"name": "invoice_error_rate", "unit": "%",
                            "meaning": "returned for correction"}],
}


def _case(structured: dict | None) -> CaseDocument:
    case = CaseDocument.new(
        case_id="IMPR-TEST-642D", title="T", belt_level="green", leader="L",
        department="D", target_date="2026-12-01", team=[],
    )
    case.phases[PHASE] = PhaseRecord(structured=structured)
    return case


def test_the_document_is_the_assembly_not_a_key_nothing_sets() -> None:
    """**The defect, as a test.**

    `POST /gate` read `phase_data.get("_validated", {})` and **nothing in the
    tree has ever set `_validated`** — so the expression resolved to `{}`, the
    document was written EMPTY, and the phase advanced anyway.

    The document is now what `GATE_SPECS[phase].assemble` produces: every field
    the schema declares, from the captured set.
    """
    document, _ = assemble_gate_document(_case(dict(COMPLETE)), PHASE)
    assert set(document) == set(GATE_SPECS[PHASE].model.model_fields)
    assert document["business_case"] == COMPLETE["business_case"]
    assert document["phase_metrics"], "the metric entry is missing"


def test_it_is_the_same_function_the_review_route_uses() -> None:
    """*"Making the writing door use the reading door's function."*

    Asserted against the registry rather than by reading both call sites,
    because the point is that there is ONE assembly, not two that agree today.
    """
    document, _ = assemble_gate_document(_case(dict(COMPLETE)), PHASE)
    direct = GATE_SPECS[PHASE].assemble(dict(COMPLETE), [], [], []).model_dump()
    assert document == direct


def test_an_unassemblable_case_refuses_rather_than_writing() -> None:
    """**REFUSE, not write a partial document.**

    Writing anyway is what let a phase advance to Measure with nothing behind
    it. The caller never reaches its write, so the phase does not advance —
    the write is what advances it.
    """
    incomplete = {k: v for k, v in COMPLETE.items() if k != "team"}
    with pytest.raises(HTTPException) as exc:
        assemble_gate_document(_case(incomplete), PHASE)
    assert exc.value.status_code == 500
    detail = str(exc.value.detail)
    assert "nothing was written" in detail
    assert "did not advance" in detail


def test_the_refusal_leaks_no_internals_to_the_belt() -> None:
    """The Belt is told a condition, not a stack fragment.

    The exception itself goes to the log, where whoever is diagnosing it can
    read it. 10.4 owns the error contract in general; this is the one site
    this step touches, and it should not ship a new leak.
    """
    with pytest.raises(HTTPException) as exc:
        assemble_gate_document(_case({}), PHASE)
    detail = str(exc.value.detail)
    assert "KeyError" not in detail and "Traceback" not in detail


def test_the_evidence_travels_with_the_document() -> None:
    """The citations and uploads the write needs are read ONCE, here.

    Two reads could disagree about what the phase rested on — and the gate is
    where a reviewer goes looking for exactly that.
    """
    case = _case(dict(COMPLETE))
    _, evidence = assemble_gate_document(case, PHASE)
    assert set(evidence) == {"citations", "uploads"}
    assert isinstance(evidence["citations"], list)
    assert isinstance(evidence["uploads"], list)
