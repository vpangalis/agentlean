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
