"""The five gate documents, their tiers and their assembly — step 3.4.

Architecture §40 (the five schemas) · §40.1 + S-F28 (assembly) · §35 (the two
tiers) · §41 + S-C33 (structured dicts) · §63.1–63.5 (S-C27–S-C31).

Counts and field names are transcribed from §63 as literals. A test that reads
its expectation out of the code under test asserts nothing.
"""
from __future__ import annotations

import asyncio
import importlib

import pytest

from backend.phases.gate_assembly import GateAssemblyError, check_field_coverage
from backend.phases.gate_registry import GATE_SPECS, review_rows, tier_of

PHASES = ("define", "measure", "analyse", "improve", "control")

# §63.1–63.5, transcribed: (total fields, Tier 1, Tier 2)
SPEC_COUNTS = {
    "define":  (18, 13, 0),   # Option A — no Tier 2 (§39.1.2)
    "measure": (15, 7, 3),
    "analyse": (14, 4, 5),
    "improve": (14, 4, 5),
    "control": (17, 3, 9),
}

GATE_METADATA = ("computation_results", "acknowledged_gaps", "citations", "uploads")

# §41 / S-C33 — the three structured dicts and their required sub-fields.
STRUCTURED = {
    "process_map_sipoc": ("suppliers", "inputs", "process_steps", "outputs",
                          "customers", "process_metrics"),
    "detailed_process_map": ("steps", "cycle_times", "resources",
                             "value_vs_waste", "measurement_points",
                             "baseline_metrics"),
    "control_plan": ("documentation", "monitoring", "response", "training",
                     "aligning_systems"),
}


# ── §63: the counts ───────────────────────────────────────────────────────

@pytest.mark.parametrize("phase", PHASES)
def test_field_count_matches_spec(phase: str) -> None:
    total, t1, t2 = SPEC_COUNTS[phase]
    spec = GATE_SPECS[phase]
    assert len(spec.model.model_fields) == total
    assert len(spec.tier_1) == t1
    assert len(spec.tier_2) == t2


@pytest.mark.parametrize("phase", PHASES)
def test_tiers_plus_phase_metrics_plus_metadata_equals_total(phase: str) -> None:
    """The arithmetic §40 states: Tier 1 + Tier 2 + phase_metrics + 4."""
    total, t1, t2 = SPEC_COUNTS[phase]
    assert t1 + t2 + 1 + 4 == total


def test_define_has_no_tier_2() -> None:
    """Option A (§39.1.2): every Define field blocks, so there is no
    `acknowledged_gaps` path out of Define — nothing is skippable, so nothing
    can be acknowledged as skipped."""
    assert GATE_SPECS["define"].tier_2 == ()


# ── §40: the same fields on all five ──────────────────────────────────────

@pytest.mark.parametrize("phase", PHASES)
def test_four_gate_metadata_fields_on_every_schema(phase: str) -> None:
    fields = GATE_SPECS[phase].model.model_fields
    for name in GATE_METADATA:
        assert name in fields


@pytest.mark.parametrize("phase", PHASES)
def test_phase_metrics_on_every_schema(phase: str) -> None:
    """§63.9 S-C39 — the keyed measurement trail across all five documents."""
    assert "phase_metrics" in GATE_SPECS[phase].model.model_fields


@pytest.mark.parametrize("phase", PHASES)
def test_issues_and_barriers_is_tier_1_everywhere(phase: str) -> None:
    """§35: every real project has blockers; a Belt reporting none has not
    looked. 'None identified at this stage' is a conscious statement."""
    assert "issues_and_barriers" in GATE_SPECS[phase].tier_1


def test_secondary_metrics_on_every_schema() -> None:
    for phase in PHASES:
        assert "secondary_metrics" in GATE_SPECS[phase].model.model_fields


# ── §41 / S-C33: the structured dicts ─────────────────────────────────────

@pytest.mark.parametrize("field,phase", [
    ("process_map_sipoc", "define"),
    ("detailed_process_map", "measure"),
    ("control_plan", "control"),
])
def test_structured_fields_are_dict_and_tier_1(field: str, phase: str) -> None:
    """S-C33 B2: `dict`, never `str`. All three are gate-required."""
    model = GATE_SPECS[phase].model
    assert model.model_fields[field].annotation is dict
    assert field in GATE_SPECS[phase].tier_1


def test_no_fmea_field_anywhere() -> None:
    """§41 invariant: FMEA has no field in any schema and none may be added."""
    for phase in PHASES:
        for name in GATE_SPECS[phase].model.model_fields:
            assert "fmea" not in name.lower()


# ── §35: tier semantics ───────────────────────────────────────────────────

def test_tier_of_labels_correctly() -> None:
    assert tier_of("control", "control_plan") == 1
    assert tier_of("control", "lessons_learned") == 2
    assert tier_of("control", "citations") is None       # gate metadata
    assert tier_of("control", "phase_metrics") is None


@pytest.mark.parametrize("phase", PHASES)
def test_review_rows_are_tier_1_first(phase: str) -> None:
    """Tier 1 first: only that group can block, so it is what the Belt reads
    first on §50's review screen."""
    tiers = [r["tier"] for r in review_rows(phase, {})]
    assert tiers == sorted(tiers)


def test_post_improvement_metrics_is_the_only_tier_1_cross_phase_ref() -> None:
    """§63.5 B2 — a Control phase that cannot link back to the baseline has
    not demonstrated improvement at all."""
    assert "post_improvement_metrics" in GATE_SPECS["control"].tier_1
    assert "causal_hypothesis" in GATE_SPECS["analyse"].tier_2
    assert "solution_linked_to_root_cause" in GATE_SPECS["improve"].tier_2


# ── S-F28: the two assembly invariants ────────────────────────────────────

#: The mirrored scalars per phase (§39.2.3, `core/metrics.py`). Define and
#: Measure mirror plain strings; Control mirrors through a dict; Analyse and
#: Improve mirror nothing and satisfy the invariant vacuously.
MIRRORED = {
    "define":  {"baseline_estimate": "12.3%", "target_value": "<3%"},
    "measure": {"baseline_mean": "12.3%", "baseline_sigma": "2.6 sigma"},
    "analyse": {},
    "improve": {},
    "control": {},
}

METRIC = "invoice_error_rate"


def _full(phase: str) -> dict:
    """Artifacts with every Tier 1 and Tier 2 field populated, and a
    `phase_metrics` entry consistent with the mirrored scalars.

    The consistency matters: S-F28 B3 raises when a phase carries mirrored
    scalars but `phase_metrics` names no metric, because the value cannot then
    be traced to a registry metric. A fixture that omitted it would be testing
    an artifact shape the gate would never accept.
    """
    spec = GATE_SPECS[phase]
    art: dict = {}
    for field in tuple(spec.tier_1) + tuple(spec.tier_2):
        annotation = spec.model.model_fields[field].annotation
        if annotation is dict:
            keys = STRUCTURED.get(field)
            art[field] = ({k: "v" for k in keys} if keys
                          else {"references_phase": "measure",
                                "references_metric_name": METRIC,
                                "metric": "2.8%"})
        elif annotation is not str:
            # list[dict] — `team` (§39.1.4) and `metric_definitions` (§63.8).
            art[field] = [{"name": METRIC, "unit": "%", "meaning": "m"}]
        else:
            art[field] = f"{field} value"

    art.update(MIRRORED[phase])
    entry = {"name": METRIC, "source": "test"}
    entry.update(MIRRORED[phase])
    if phase == "control":
        entry["actual"] = art["post_improvement_metrics"]["metric"]
    art["phase_metrics"] = [entry]
    return art


@pytest.mark.parametrize("phase", PHASES)
def test_assembly_succeeds_with_every_field_present(phase: str) -> None:
    doc = GATE_SPECS[phase].assemble(_full(phase), [], [], [])
    assert doc.__class__ is GATE_SPECS[phase].model


@pytest.mark.parametrize("phase", PHASES)
def test_assembly_references_every_schema_field(phase: str) -> None:
    """S-F28 invariant 1 — G-28 in one assertion.

    A field assembly never sets reaches the Store as its default and is
    invisible until a later phase reads nothing. Pydantic will not catch it:
    all four gate-metadata fields have defaults and construct happily when
    omitted.
    """
    doc = GATE_SPECS[phase].assemble(_full(phase), [], [], [])
    assert set(doc.model_dump()) == set(GATE_SPECS[phase].model.model_fields)


def test_coverage_check_can_fail() -> None:
    """Prove the check can fail before trusting that it passed."""
    with pytest.raises(GateAssemblyError, match="never set by assembly"):
        check_field_coverage(GATE_SPECS["control"].model, {"control_plan": "x"})


def test_coverage_check_rejects_an_unknown_field() -> None:
    values = {f: "x" for f in GATE_SPECS["analyse"].model.model_fields}
    values["not_a_field"] = "x"
    with pytest.raises(GateAssemblyError, match="not on the schema"):
        check_field_coverage(GATE_SPECS["analyse"].model, values)


@pytest.mark.parametrize("phase", PHASES)
def test_missing_tier_1_field_raises_keyerror(phase: str) -> None:
    """§40.1: a `KeyError` here is CORRECT — Layer 2b should have blocked the
    gate, so reaching assembly without the field is a bug that must surface."""
    art = _full(phase)
    del art[GATE_SPECS[phase].tier_1[0]]
    with pytest.raises(KeyError):
        GATE_SPECS[phase].assemble(art, [], [], [])


@pytest.mark.parametrize("phase", ["measure", "analyse", "improve", "control"])
def test_missing_tier_2_field_assembles_as_empty(phase: str) -> None:
    """§35: an empty value RECORDS that the Belt proceeded without it."""
    art = _full(phase)
    # Skip any Tier 2 field that is also a MIRRORED SCALAR: deleting it while
    # `phase_metrics` still carries the value is a genuine single-authority
    # violation, and S-F28 B2 is right to raise on it. Measure's
    # `baseline_sigma` is the one such field.
    mirrored = set(MIRRORED[phase])
    field = next(f for f in GATE_SPECS[phase].tier_2 if f not in mirrored)
    del art[field]
    doc = GATE_SPECS[phase].assemble(art, [], [], [f"{field} — Belt accepted gap"])
    assert getattr(doc, field) in ("", {}, [])
    # via model_dump: GateSpec.assemble is typed to the BaseModel base, so
    # attribute access on the concrete subclass is invisible to mypy.
    assert doc.model_dump()["acknowledged_gaps"] == [f"{field} — Belt accepted gap"]


def test_single_authority_runs_before_construction() -> None:
    """S-F28 B1/B2: the primary metric's `phase_metrics` entry and the mirrored
    scalar must agree. Two stores holding one number drift invisibly — both
    reads succeed and the disagreement surfaces a phase later."""
    art = _full("measure")
    art["baseline_mean"] = "12.3%"
    art["phase_metrics"] = [{"name": "invoice_error_rate",
                             "baseline_mean": "99.9%", "source": "measured"}]
    with pytest.raises(Exception) as exc:
        GATE_SPECS["measure"].assemble(art, [], [], [])
    assert "baseline_mean" in str(exc.value) or "authority" in str(exc.value).lower()


# ── the validators (Layer 2b) ─────────────────────────────────────────────

def _validate(phase: str, data: dict) -> dict:
    mod = importlib.import_module(f"backend.phases.{phase}.validate")
    fn = getattr(mod, f"validate_{phase}")
    state = {"phase_inputs": {phase: data}, "gate_attempts": 0}
    return asyncio.run(fn(state))["phase_inputs"][phase]


@pytest.mark.parametrize("phase", ["measure", "analyse", "improve", "control"])
def test_tier_1_complete_passes_even_with_tier_2_gaps(phase: str) -> None:
    """§35: a gate MAY pass with warnings. It may NEVER pass with failures."""
    art = _full(phase)
    for field in GATE_SPECS[phase].tier_2:
        art.pop(field, None)
    out = _validate(phase, art)
    assert out["_gate_passed"] is True
    assert len(out["_acknowledged_gaps"]) == len(GATE_SPECS[phase].tier_2)


@pytest.mark.parametrize("phase", ["measure", "analyse", "improve", "control"])
def test_missing_tier_1_blocks(phase: str) -> None:
    art = _full(phase)
    field = GATE_SPECS[phase].tier_1[0]
    del art[field]
    out = _validate(phase, art)
    assert out["_gate_passed"] is False
    assert field in out["_missing_fields"]


def test_partial_structured_dict_blocks() -> None:
    """§41's partial-map failure: four of six looks complete until someone
    tries to use it."""
    art = _full("control")
    art["control_plan"] = {"documentation": "d", "monitoring": "m"}
    out = _validate("control", art)
    assert out["_gate_passed"] is False
    assert any("control_plan." in m for m in out["_missing_fields"])


def test_whitespace_only_value_is_not_captured() -> None:
    art = _full("analyse")
    art["root_cause_statement"] = "   "
    out = _validate("analyse", art)
    assert "root_cause_statement" in out["_missing_fields"]


@pytest.mark.parametrize("phase", PHASES)
def test_validators_are_async_nodes(phase: str) -> None:
    """§14 / §3.2 — every node is `async def`."""
    import inspect
    mod = importlib.import_module(f"backend.phases.{phase}.validate")
    assert inspect.iscoroutinefunction(getattr(mod, f"validate_{phase}"))


def test_validator_tier_lists_come_from_schema() -> None:
    """§56.1's atomic unit: `validate.py` imports the tier tuples rather than
    retyping them — two hand-maintained copies of one list is how the three
    drift apart."""
    from backend.phases.measure.validate import MEASURE_REQUIRED_FOR_GATE
    assert list(GATE_SPECS["measure"].tier_1) == MEASURE_REQUIRED_FOR_GATE
