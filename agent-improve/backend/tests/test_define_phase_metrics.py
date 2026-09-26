"""Define's `phase_metrics` writer — procedure step 6.20, the scorecard half.

WHY A NEW FILE AND NOT MORE ROWS IN `test_gate_documents.py`
------------------------------------------------------------
**Because that file's fixture is the escape cause.** `_full()` hand-writes

    art["phase_metrics"] = [entry]

with a docstring explaining that a fixture omitting it *"would be testing an
artifact shape the gate would never accept"* — which is exactly right, and
exactly why the defect survived. The fixture supplied what the RUNTIME did not,
so every assembly test passed against a shape no live gate could produce, and
all 1078 tests still pass with this step's writer deleted.

**Every fixture here builds artifacts the way a Belt's turns build them** — the
captured fields and nothing else — so these tests go red without the writer.
That is the difference between testing the path you wrote and testing the path
that ships.

WHAT S-F28 B3 DOES TO A DEFINE GATE WITHOUT THIS
------------------------------------------------
`PRIMARY_MIRRORED_SCALARS["define"]` is `baseline_estimate` and `target_value`,
both gate-required (§39.1.2, Option A), so a Define gate that reaches assembly
ALWAYS carries them. With no `phase_metrics` entry to mirror, B3 raises: *"the
value cannot be traced to a registry metric."* A complete thirteen-field case
was therefore REFUSED, and `GET /gate/review` answered 500 for a Belt who had
done everything right.
"""
from __future__ import annotations

import pytest

from backend.core.metrics import NONE_THIS_PHASE, check_single_authority
from backend.phases.define.schema import (
    DEFINE_METRIC_SOURCE,
    NOT_ADDRESSED,
    assemble_define_gate_document,
    define_phase_metrics,
)
from backend.phases.gate_registry import GATE_SPECS

#: The registry as Define captures it inside position 5 (§63.8).
REGISTRY = [
    {"name": "invoice_error_rate", "unit": "%",
     "meaning": "share of invoices returned for correction"},
]


def _captured(**overrides: object) -> dict:
    """A COMPLETE Define case, built the way turns build one.

    Every gate-required field and **no `phase_metrics`** — because nothing
    a Belt does produces one. Asserted against the registry rather than typed,
    so a field added to the gate set breaks this helper first.
    """
    art: dict = {
        "business_case":       "Rework costs GBP 245,000 a year.",
        "team":                [{"name": "Ana", "role": "lead",
                                 "function": "finance"}],
        "voc_summary":         "Suppliers want invoices right first time.",
        "problem_statement":   "UK invoices are wrong 12% of the time.",
        "baseline_estimate":   "12%",
        "project_scope":       {"in_scope": "UK billing",
                                "out_scope": "credit notes"},
        "goal_statement":      "Cut invoice errors to 3% by December 2026.",
        "target_value":        "3%",
        "target_date":         "2026-12-01",
        "secondary_metrics":   "Invoice cycle time must not rise.",
        "process_map_sipoc":   {"suppliers": "s", "inputs": "i",
                                "process_steps": "p", "outputs": "o",
                                "customers": "c", "process_metrics": "m"},
        "issues_and_barriers": "none identified at this stage",
        "benefits_analysis":   {"cost_of_gap": "GBP 245,000 a year", "impact_type": "sustainable",
                                "realisation_schedule": "from Q1 2027", "finance_contact": "Sam"},
        "critical_to_quality": [{"customer": "suppliers", "need": "right first time",
                                 "requirement": "under 3% returned"}],
        "problem_5w2h":        {k: k for k in ("what", "where", "when", "who", "why",
                                                "how", "how_much")},
        "metric_definitions":  [dict(m) for m in REGISTRY],
    }
    assert set(GATE_SPECS["define"].tier_1) <= set(art), (
        "the gate-required set grew — this fixture is stale"
    )
    assert "phase_metrics" not in art, (
        "the whole point of this fixture is that nothing captures it"
    )
    art.update(overrides)
    return art


# ══════════════════════════════════════════════════════════════════════════
# The step's Done-when — a complete case assembles
# ══════════════════════════════════════════════════════════════════════════


def test_a_complete_define_case_assembles() -> None:
    """**The clause the whole step exists for.**

    Before this writer, a case with every field a Belt can supply was refused
    at the single-authority invariant. Nothing was missing; nothing could be
    added to fix it, because `phase_metrics` is on no tier set and no coach
    captures it.
    """
    doc = assemble_define_gate_document(_captured(), citations=[], uploads=[])
    assert doc.phase_metrics, "the document carries no metric entry"


def test_without_the_derivation_the_same_case_is_refused() -> None:
    """**The mutation, as a test rather than as a note** (§0.4).

    This is what the tree did before the writer: the same complete case, with
    the derivation not applied. It documents the failure the step closes, and
    it keeps failing if someone later makes the derivation a no-op.
    """
    defects = check_single_authority("define", _captured())
    assert defects, "a Define case with no phase_metrics must violate B3"
    assert "cannot be traced to a registry metric" in defects[0]


def test_row_19_a_complete_case_assembles_a_gate_document() -> None:
    """**Capability row 19.** A complete case ASSEMBLES a gate document.

    Reads the case the system actually wrote and assembles from it — **no
    fixture, for row 18's reason.** Every seeded fixture in this suite hands
    assembly a `phase_metrics` that no runtime produced, so a seeded version of
    this row would have been green while `GET /gate/review` answered 500 on
    real data for months.

    **SKIPS rather than passes when there is no case to read**: a row that
    could not be evaluated is not a green row (Appendix H).
    """
    import asyncio
    import os

    from backend.storage import blob

    case_id = os.environ.get("CAPABILITY_CASE_ID", "IMPR-2026-0E5")
    if not blob.storage_configured():
        pytest.skip("no storage configured — row 19 cannot be evaluated")
    case = asyncio.run(blob.load_case(case_id))
    if case is None:
        pytest.skip(f"{case_id} not found — row 19 cannot be evaluated")

    record = case.phases.get("define")
    if record is None:
        pytest.skip(f"{case_id} has no define record — row 19 has no subject")
    artifacts = dict(record.structured or {})
    missing = [f for f in GATE_SPECS["define"].tier_1 if f not in artifacts]
    if missing:
        pytest.skip(
            f"{case_id} is not a complete case — missing {missing}. Row 19 "
            "asks whether a COMPLETE case assembles, and there is none to ask "
            "of"
        )

    doc = assemble_define_gate_document(
        artifacts,
        citations=[c.model_dump() if hasattr(c, "model_dump") else dict(c)
                   for c in (record.citations or [])],
        uploads=[u.model_dump() if hasattr(u, "model_dump") else dict(u)
                 for u in (record.uploads or [])],
    )
    assert doc.phase_metrics, "assembled without a metric entry"
    assert len(doc.model_dump()) == 18



# ══════════════════════════════════════════════════════════════════════════
# §39.1.9 — the five keys, and where each comes from
# ══════════════════════════════════════════════════════════════════════════


def test_the_entry_carries_exactly_the_five_specified_keys() -> None:
    entry = define_phase_metrics(_captured())[0]
    assert set(entry) == {"name", "unit", "baseline_estimate",
                          "target_value", "source"}


def test_name_and_unit_are_verbatim_from_the_registry() -> None:
    """§63.8 B2 — the registry `name` is a MATCHING KEY, not prose.

    The grader traces a metric across five gate documents by key equality, so
    a re-phrasing here is a metric that vanishes from the trail.
    """
    entry = define_phase_metrics(_captured())[0]
    assert entry["name"] == REGISTRY[0]["name"]
    assert entry["unit"] == REGISTRY[0]["unit"]


def test_the_scalars_are_the_captured_fields_of_the_same_names() -> None:
    art = _captured(baseline_estimate="14.2%", target_value="4%")
    entry = define_phase_metrics(art)[0]
    assert entry["baseline_estimate"] == "14.2%"
    assert entry["target_value"] == "4%"


def test_source_is_stated_because_define_states_rather_than_measures() -> None:
    """§63.9's Define row. Measure writes `"measured"`; the distinction is what
    tells a later reader which kind of number it is looking at."""
    assert define_phase_metrics(_captured())[0]["source"] == "stated"
    assert DEFINE_METRIC_SOURCE == "stated"


def test_every_scalar_inside_the_entry_is_a_string() -> None:
    """§63.9 B5 — the dict is §7's exception; its values are not."""
    for entry in define_phase_metrics(_captured()):
        for key, value in entry.items():
            assert isinstance(value, str), f"{key} is {type(value).__name__}"


# ══════════════════════════════════════════════════════════════════════════
# The invariant now holds BY CONSTRUCTION
# ══════════════════════════════════════════════════════════════════════════


def test_the_mirror_holds_by_construction_not_by_luck() -> None:
    """§39.1.9 — *"the entry's values ARE the captured scalars, so the two
    cannot drift."*

    Driven over several baselines rather than one, because a single value
    passes whether the entry mirrors the scalar or merely happens to equal it.
    """
    for baseline, target in [("12%", "3%"), ("0.4 defects/unit", "0.1"),
                             ("2.6 days", "1.5 days")]:
        art = _captured(baseline_estimate=baseline, target_value=target)
        art["phase_metrics"] = define_phase_metrics(art)
        assert check_single_authority("define", art) == []


def test_an_entry_that_arrived_another_way_is_overridden() -> None:
    """**§39.1.9 removes the second author rather than detecting it.**

    A `phase_metrics` reaching assembly from anywhere else — a model putting
    one in `fields_captured`, a stale record — is replaced, not merged. Two
    authors of one figure is the drift S-F28 B2 exists to catch, and the
    cheapest fix is that there is only ever one.
    """
    art = _captured()
    art["phase_metrics"] = [{"name": "invented", "baseline_estimate": "99%",
                             "source": "hallucinated"}]
    doc = assemble_define_gate_document(art, citations=[], uploads=[])
    assert [e["name"] for e in doc.phase_metrics] == ["invoice_error_rate"]
    assert doc.phase_metrics[0]["baseline_estimate"] == "12%"
    assert doc.phase_metrics[0]["source"] == "stated"


# ══════════════════════════════════════════════════════════════════════════
# More than one registry metric
# ══════════════════════════════════════════════════════════════════════════


def test_one_entry_per_registry_metric() -> None:
    """§39.1.9 — *"one entry per registry metric it engaged."*"""
    art = _captured(metric_definitions=[
        {"name": "invoice_error_rate", "unit": "%", "meaning": "m1"},
        {"name": "invoice_cycle_time", "unit": "days", "meaning": "m2"},
    ])
    assert [e["name"] for e in define_phase_metrics(art)] == [
        "invoice_error_rate", "invoice_cycle_time"]


def test_only_the_first_entry_carries_the_scalars() -> None:
    """**Define captures ONE baseline and ONE target** (§39.1.2), so only the
    primary can carry them — and `core.metrics.primary_entry` defines the
    primary as the FIRST entry carrying a name.

    The second metric's entry says **`"not addressed this phase"`**, which is
    the marker Analyse and Improve already write (§39.3.3, §39.4.3). Copying
    the primary's values across would assert that two different metrics share
    one baseline — false, and it would survive into Control's
    target-versus-actual comparison.
    """
    art = _captured(metric_definitions=[
        {"name": "invoice_error_rate", "unit": "%", "meaning": "m1"},
        {"name": "invoice_cycle_time", "unit": "days", "meaning": "m2"},
    ])
    first, second = define_phase_metrics(art)
    assert (first["baseline_estimate"], first["target_value"]) == ("12%", "3%")
    assert (second["baseline_estimate"], second["target_value"]) == (
        NOT_ADDRESSED, NOT_ADDRESSED)
    assert second["name"] and second["unit"], (
        "the metric is still on the trail — only its values are absent"
    )


def test_the_marker_is_the_one_analyse_and_improve_already_use() -> None:
    """**One convention, read by one grader.**

    §39.3.3 and §39.4.3 both write `"not addressed this phase"` into the
    content key of an entry the phase carries but did not act on. A third
    spelling here — an empty string, `"n/a"`, a missing key — would make the
    same fact look like three facts to whatever reads the trail.

    **Distinct from `"none this phase"`**, which §63.9 B2 puts in place of the
    WHOLE list when a phase engaged no metric. One marks an entry; the other
    replaces the list.
    """
    assert NOT_ADDRESSED == "not addressed this phase"
    assert NOT_ADDRESSED != NONE_THIS_PHASE


def test_a_multi_metric_case_still_satisfies_the_invariant() -> None:
    art = _captured(metric_definitions=[
        {"name": "invoice_error_rate", "unit": "%", "meaning": "m1"},
        {"name": "invoice_cycle_time", "unit": "days", "meaning": "m2"},
    ])
    art["phase_metrics"] = define_phase_metrics(art)
    assert check_single_authority("define", art) == []


# ══════════════════════════════════════════════════════════════════════════
# The edges, and the branch that is deliberately absent
# ══════════════════════════════════════════════════════════════════════════


def test_an_unnamed_registry_metric_is_skipped() -> None:
    """§63.8 B1 — an entry with no `name` is not a key, so it cannot join a
    trail that is matched on key equality."""
    art = _captured(metric_definitions=[
        {"unit": "%", "meaning": "nameless"},
        {"name": "invoice_error_rate", "unit": "%", "meaning": "real"},
    ])
    entries = define_phase_metrics(art)
    assert [e["name"] for e in entries] == ["invoice_error_rate"]
    assert entries[0]["baseline_estimate"] == "12%", (
        "the first EMITTED entry is the primary, not the first registry row"
    )


def test_an_empty_registry_yields_no_entries_and_the_gate_refuses() -> None:
    """**The deliberately absent branch.**

    `"none this phase"` (§63.9 B2) is for a phase that engaged no metric.
    Define's two scalars are gate-required, so a Define gate reaching assembly
    has always engaged one — writing it here would be a branch that cannot
    fire, which is the unfireable-check class this project keeps paying for.
    So an empty registry produces `[]` and S-F28 B3 raises with the message it
    already has. That is the correct outcome, not a gap.
    """
    art = _captured(metric_definitions=[])
    assert define_phase_metrics(art) == []
    with pytest.raises(ValueError, match="cannot be traced to a registry metric"):
        assemble_define_gate_document(art, citations=[], uploads=[])


def test_define_never_writes_none_this_phase() -> None:
    for art in (_captured(), _captured(metric_definitions=[])):
        assert NONE_THIS_PHASE not in str(define_phase_metrics(art))


def test_a_malformed_registry_does_not_raise_here() -> None:
    """A non-list registry is a captured-value defect, and the gate's own
    validators own it. This function returns `[]` and lets S-F28 B3 speak,
    rather than raising a second, less informative error from further away."""
    assert define_phase_metrics(_captured(metric_definitions="not a list")) == []
    assert define_phase_metrics(_captured(metric_definitions=[1, "x", None])) == []
