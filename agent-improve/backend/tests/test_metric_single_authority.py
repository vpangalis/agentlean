"""The metric single-authority invariant, across all five phases.

ARCHITECTURE.md §39.2.3 · §40.1 (S-F28) · §63.9 (S-C39).

`phase_metrics` is authoritative; the scalar fields mirror the PRIMARY metric's
entry. These tests pin that the mirror is checked rather than assumed, and that
the two legitimate no-mirror cases — Analyse/Improve linkage, and
`"none this phase"` — do not raise.
"""
import pytest

from backend.core.metrics import (
    NONE_THIS_PHASE,
    PRIMARY_MIRRORED_SCALARS,
    assert_single_authority,
    check_single_authority,
    primary_entry,
)

# One good artifacts dict per phase: primary entry and scalars agree.
GOOD = {
    "define": {
        "baseline_estimate": "12%",
        "target_value": "under 3%",
        "phase_metrics": [
            {"name": "invoice_error_rate", "unit": "%",
             "baseline_estimate": "12%", "target_value": "under 3%",
             "source": "stated"},
            {"name": "invoice_cycle_time", "unit": "days",
             "baseline_estimate": "2.6 days", "target_value": "under 2 days",
             "source": "stated"},
        ],
    },
    "measure": {
        "baseline_mean": "12.3%",
        "baseline_sigma": "2.6 sigma",
        "phase_metrics": [
            {"name": "invoice_error_rate", "unit": "%",
             "baseline_mean": "12.3%", "baseline_sigma": "2.6 sigma",
             "stability": "stable", "source": "measured"},
            {"name": "invoice_cycle_time", "unit": "days",
             "baseline_mean": "2.6 days", "baseline_sigma": "—",
             "stability": "not stable", "source": "measured"},
        ],
    },
    "analyse": {
        "phase_metrics": [
            {"name": "invoice_error_rate", "explains": "pricing-table staleness"},
        ],
    },
    "improve": {
        "phase_metrics": [
            {"name": "invoice_error_rate", "targeted_by": "nightly price sync"},
        ],
    },
    "control": {
        "post_improvement_metrics": "2.8%",
        "phase_metrics": [
            {"name": "invoice_error_rate", "unit": "%",
             "post_improvement_metrics": "2.8%", "improvement_delta": "-9.5pp",
             "source": "measured"},
        ],
    },
}
PHASES = list(PRIMARY_MIRRORED_SCALARS)


def test_all_five_phases_are_covered():
    """The invariant must know about every phase, or it silently skips one."""
    assert PHASES == ["define", "measure", "analyse", "improve", "control"]
    assert set(GOOD) == set(PHASES)


@pytest.mark.parametrize("phase", PHASES)
def test_matching_primary_entry_passes(phase):
    assert check_single_authority(phase, GOOD[phase]) == []
    assert_single_authority(phase, GOOD[phase])          # must not raise


@pytest.mark.parametrize(
    "phase", [p for p in PHASES if PRIMARY_MIRRORED_SCALARS[p]]
)
def test_mismatched_scalar_is_a_defect(phase):
    """The whole point: a top-level scalar disagreeing with the primary entry."""
    for scalar in PRIMARY_MIRRORED_SCALARS[phase]:
        bad = {k: (dict(v) if isinstance(v, dict) else v)
               for k, v in GOOD[phase].items()}
        bad["phase_metrics"] = [dict(e) for e in GOOD[phase]["phase_metrics"]]
        bad[scalar] = "SOMETHING ELSE"
        defects = check_single_authority(phase, bad)
        assert defects, "%s/%s drifted and was not caught" % (phase, scalar)
        assert scalar in defects[0]
        with pytest.raises(ValueError):
            assert_single_authority(phase, bad)


@pytest.mark.parametrize(
    "phase", [p for p in PHASES if PRIMARY_MIRRORED_SCALARS[p]]
)
def test_secondary_metric_drift_is_not_flagged(phase):
    """Only the PRIMARY entry mirrors. A second metric has no scalar to match."""
    art = {k: v for k, v in GOOD[phase].items()}
    entries = [dict(e) for e in GOOD[phase]["phase_metrics"]]
    if len(entries) < 2:
        pytest.skip("phase fixture has one metric")
    for scalar in PRIMARY_MIRRORED_SCALARS[phase]:
        entries[1][scalar] = "a completely different value"
    art["phase_metrics"] = entries
    assert check_single_authority(phase, art) == []


@pytest.mark.parametrize("phase", ["analyse", "improve"])
def test_linkage_phases_have_nothing_to_mirror(phase):
    """Analyse and Improve record which metric is targeted, not its value."""
    assert PRIMARY_MIRRORED_SCALARS[phase] == ()
    assert check_single_authority(phase, {"phase_metrics": []}) == []
    assert check_single_authority(phase, GOOD[phase]) == []


@pytest.mark.parametrize("phase", PHASES)
def test_none_this_phase_never_raises(phase):
    """§63.9 B2's conscious answer must not be read as a broken mirror."""
    for value in (NONE_THIS_PHASE, [NONE_THIS_PHASE]):
        assert check_single_authority(phase, {"phase_metrics": value}) == []


@pytest.mark.parametrize(
    "phase", [p for p in PHASES if PRIMARY_MIRRORED_SCALARS[p]]
)
def test_scalars_with_no_registry_entry_are_a_defect(phase):
    """A value that cannot be traced to a registry metric is the failure the
    registry exists to prevent — it must not pass silently."""
    art = {s: "12%" for s in PRIMARY_MIRRORED_SCALARS[phase]}
    art["phase_metrics"] = []
    defects = check_single_authority(phase, art)
    assert defects and "no primary entry" in defects[0]


def test_primary_entry_skips_malformed_entries():
    assert primary_entry([]) is None
    assert primary_entry(["none this phase"]) is None
    assert primary_entry([{"name": ""}, {"name": "real_one"}])["name"] == "real_one"
