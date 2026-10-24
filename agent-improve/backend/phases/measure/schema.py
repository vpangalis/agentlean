from pydantic import BaseModel, Field
from typing import Optional, List


class DataCollectionEntry(BaseModel):
    """One row in the data collection plan — one metric/source pair."""
    metric: str = Field(..., description="Which metric this covers")
    data_source: str = Field(..., description="System, file, or person")
    data_owner: str = Field(..., description="Who collects it")
    data_type: str = Field(
        ...,
        description="'continuous' (measured values) or 'discrete' (counts/categories)"
    )
    sample_size: Optional[str] = Field(
        None, description="Number of records or time period"
    )
    frequency: Optional[str] = Field(
        None, description="How often data is collected"
    )
    operational_definition: Optional[str] = Field(
        None,
        description="Precise definition of what counts as a defect/event"
    )


class MeasurePhaseInput(BaseModel):
    """All fields captured during the Measure phase."""

    # Work product 1 — Metrics confirmation
    primary_metric_confirmed: Optional[str] = Field(
        None,
        description="Confirmed primary metric name and unit"
    )
    secondary_metric_confirmed: Optional[str] = Field(
        None,
        description="Confirmed secondary metric name and unit"
    )

    # Work product 2 — Data collection plan
    data_collection_plan: Optional[List[DataCollectionEntry]] = Field(
        None,
        description="List of data sources, one entry per metric/source"
    )

    # Work product 3 — Measurement reliability (optional)
    msa_required: Optional[str] = Field(
        None,
        description="'yes' or 'no' — does this process need MSA?"
    )
    msa_result: Optional[str] = Field(
        None,
        description="Result of MSA if conducted (reliable/unreliable/acceptable)"
    )

    # Work product 4 — Baseline data (all optional)
    baseline_period: Optional[str] = Field(
        None,
        description="Time period covered by baseline data"
    )
    baseline_sample_size: Optional[str] = Field(
        None,
        description="Number of records collected"
    )
    baseline_mean: Optional[str] = Field(
        None,
        description="Average value with unit"
    )
    baseline_variation: Optional[str] = Field(
        None,
        description="Range or standard deviation"
    )
    baseline_summary: Optional[str] = Field(
        None,
        description="Plain language summary of baseline findings"
    )

    # Work product 5 — Process capability (all optional)
    capability_method: Optional[str] = Field(
        None,
        description="How capability was assessed"
    )
    current_sigma_level: Optional[str] = Field(
        None,
        description="Estimated sigma level or defect rate"
    )
    capability_summary: Optional[str] = Field(
        None,
        description="Plain language summary of capability findings"
    )

    # ── phase_metrics — on all five schemas ───────────────────────────
    # Declared on this v1 input class as well as on `MeasureOutput`, so the
    # on-all-five rule holds for both.
    phase_metrics: List[dict] = Field(
        default_factory=list,
        description=(
            "What this phase produced for each registry metric it engaged. One "
            "entry per metric, `name` equal to a `metric_definitions` name from "
            "Define (§63.8) — the grader traces a metric across phases by key "
            "equality on `name`. Measure records the measured state: {name, unit, baseline_mean, baseline_sigma, stability, source: 'measured'}. "
            "A phase touching no metric writes 'none this phase', never a "
            "silent gap (§40)."
        ),
    )


from backend.phases.gate_assembly import (  # noqa: E402
    build_gate_document,
    tier_1,
    tier_2,
)


# =======================================================================
# MEASURE'S GATE DOCUMENT -- 15 fields (7 Tier 1, 3 Tier 2,
# `phase_metrics`, 4 gate metadata). The assembly below references every
# one of them (G-28).
#
# Assembled ONCE, at `gate_apply`, by Pydantic construction over values
# already captured -- there is NO LLM CALL in this path.
#
# THE ACCESS PATTERN ENCODES THE TIER:
#   Tier 1  artifacts["field"]        a KeyError is CORRECT -- Layer 2b
#                                     should have blocked the gate
#   Tier 2  artifacts.get(field, "")  an empty value RECORDS that the Belt
#                                     proceeded without it
# =======================================================================

MEASURE_TIER_1_FIELDS: tuple[str, ...] = (
    "baseline_mean",
    "data_collection_plan",
    "driver_priority_summary",
    "vital_few_drivers",
    "detailed_process_map",
    "stability_assessment",
    "issues_and_barriers",
)

MEASURE_TIER_2_FIELDS: tuple[str, ...] = (
    "baseline_sigma",
    "measurement_system_validated",
    "secondary_metrics",
)


class MeasureOutput(BaseModel):
    """Gate document for the Measure phase -- 15 fields.

    7 Tier 1, 3 Tier 2, `phase_metrics`, 4 gate metadata (S-C28, 40).
    Declaration order is the spec's: Tier 1, Tier 2, `phase_metrics`, metadata.

    The largest Tier 1 set of the five. `stability_assessment` is checked
    BEFORE capability (B1): a baseline Cpk computed across an unstable
    process averages two different processes and looks authoritative
    while being wrong.
    """

    # -- Tier 1 -- gate-required ---------------------------------------
    baseline_mean: str = Field(
        ...,
        description=(
            "Value with units, as the Belt stated it. Mirrored by the primary metric's `phase_metrics` entry -- the single-authority invariant (39.2.3) raises on drift."
        ),
    )
    data_collection_plan: str = Field(
        ...,
        description=(
            "Sample size, frequency, and the responsible person."
        ),
    )
    driver_priority_summary: str = Field(
        ...,
        description=(
            "Evidence that prioritisation actually happened. Tier 1 for all Belts -- Analyse cannot start without the ranked result it produces (B4)."
        ),
    )
    vital_few_drivers: str = Field(
        ...,
        description=(
            "The ranked result Analyse consumes."
        ),
    )
    detailed_process_map: dict = Field(
        ...,
        description=(
            "Expanded process map. SIX sub-fields (41, S-C33): steps, cycle_times, resources, value_vs_waste, measurement_points, baseline_metrics. `baseline_metrics` carries the BEFORE values of the measurement thread (B3)."
        ),
    )
    stability_assessment: str = Field(
        ...,
        description=(
            "Checked BEFORE capability (B1). An unstable process has special causes, so a Cpk across them is an average of two processes, not a capability figure."
        ),
    )
    issues_and_barriers: str = Field(
        ...,
        description=(
            "Belt-stated blockers. Gate-required in every phase -- every real project has some, and a Belt reporting none has not looked. 'None identified at this stage' is a conscious statement; silence is not."
        ),
    )

    # -- Tier 2 -- rubric-recommended; at worst a `warning` -------------
    baseline_sigma: str = Field(
        default_factory=str,
        description=(
            "Calculated sigma level. Mirrored by `phase_metrics` when present."
        ),
    )
    measurement_system_validated: str = Field(
        default_factory=str,
        description=(
            "GR&R or equivalent evidence."
        ),
    )
    secondary_metrics: str = Field(
        default_factory=str,
        description=(
            "What could get worse. On all five schemas (40)."
        ),
    )

    # -- On all five schemas -------------------------------------------
    phase_metrics: list[dict] = Field(
        default_factory=list,
        description=(
            "One entry per registry metric this phase engaged. `name` MUST "
            "equal a `metric_definitions` name verbatim, so key equality "
            "holds (S-C39 B1). A phase touching no metric writes 'none this "
            "phase' rather than leaving the list empty (B2) -- an empty list "
            "reads the same whether the phase engaged no metric or forgot to "
            "record one, and the second is the failure worth catching. "
            "Measure's entries carry the MEASURED state -- baseline_mean, baseline_sigma, stability, source 'measured'."
        ),
    )

    # -- Gate metadata -- the same four on all five schemas -------------
    computation_results: list[dict] = Field(default_factory=list)
    acknowledged_gaps: list[str] = Field(
        default_factory=list,
        description=(
            "Tier 2 fields the Belt consciously proceeded without (35). The "
            "next phase's input mapper carries these forward (G-27 ruling) "
            "so a deliberate decision stays distinguishable from an "
            "oversight."
        ),
    )
    citations: list[dict] = Field(default_factory=list)
    uploads: list[dict] = Field(default_factory=list)


def assemble_measure_gate_document(
    artifacts: dict,
    citations: list[dict],
    uploads: list[dict],
    acknowledged_gaps: list[str],
) -> MeasureOutput:
    """Construct Measure's gate document from captured values.

    Both assembly invariants run first, inside `build_gate_document`: metric
    single authority, then field coverage. Every one of the 15
    schema fields is referenced below -- that IS invariant 1, and G-28 is the
    risk it exists to close.
    """
    values = {
        # Tier 1 -- direct access; a KeyError is correct
        "baseline_mean": tier_1(artifacts, "baseline_mean"),
        "data_collection_plan": tier_1(artifacts, "data_collection_plan"),
        "driver_priority_summary": tier_1(artifacts, "driver_priority_summary"),
        "vital_few_drivers": tier_1(artifacts, "vital_few_drivers"),
        "detailed_process_map": tier_1(artifacts, "detailed_process_map"),
        "stability_assessment": tier_1(artifacts, "stability_assessment"),
        "issues_and_barriers": tier_1(artifacts, "issues_and_barriers"),
        # Tier 2 -- .get(); an empty value records a conscious gap
        "baseline_sigma": tier_2(artifacts, "baseline_sigma"),
        "measurement_system_validated": tier_2(artifacts, "measurement_system_validated"),
        "secondary_metrics": tier_2(artifacts, "secondary_metrics"),
        # On all five schemas
        "phase_metrics": artifacts.get("phase_metrics", []),
        # Gate metadata
        "computation_results": artifacts.get("computation_results", []),
        "acknowledged_gaps": acknowledged_gaps,
        "citations": citations,
        "uploads": uploads,
    }
    return build_gate_document(MeasureOutput, "measure", artifacts, values)


#: All six sub-fields required. **Declared here rather than in
#: `validate.py`**: `gate_registry.missing_structured` needs it, and the
#: registry imports schema only — that one-way direction is what keeps the
#: validators able to import the registry without a cycle.
DETAILED_PROCESS_MAP_KEYS: tuple[str, ...] = (
    "steps", "cycle_times", "resources", "value_vs_waste",
    "measurement_points", "baseline_metrics",
)
