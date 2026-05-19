from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class YVariable(BaseModel):
    """One metric being measured — primary or secondary."""

    name: str = Field(..., description="Plain name e.g. brake pad thickness")
    unit: str = Field(..., description="Unit of measurement e.g. mm per inspection")
    source_system: str = Field(..., description="System where data lives")
    is_primary: bool = Field(..., description="True for the main Y, False for secondary")


class DataSource(BaseModel):
    """One source of data for the measure phase."""

    name: str = Field(..., description="Short name e.g. IBIS load data")
    system: str = Field(..., description="System name e.g. IBIS passenger system")
    owner: str = Field(..., description="Named person responsible for getting this data")
    status: str = Field(
        ...,
        description="e.g. ready to export / request submitted / received",
    )
    rows: Optional[int] = Field(None, description="Row count once received")


class MeasurePhaseInput(BaseModel):
    """Gate model for Measure phase. All fields required.
    Validator instantiates this from phase_inputs['measure'].
    ValidationError → specific missing fields → Orchestrator asks team."""

    y_variables: list[YVariable] = Field(
        ...,
        min_length=1,
        description="At least one Y variable. First is primary.",
    )
    confirmed_factors: list[str] = Field(
        ...,
        min_length=1,
        description="Factors team already records alongside Y",
    )
    ai_suggested_factors: list[str] = Field(
        default_factory=list,
        description="Additional factors AI suggested from past cases",
    )
    data_sources: list[DataSource] = Field(
        ...,
        min_length=1,
        description="One entry per data source needed",
    )
    sample_size_available: int = Field(..., gt=0)
    sample_size_minimum: int = Field(..., gt=0)
    sample_size_sufficient: bool = Field(...)
    msa_decision: str = Field(
        ...,
        description="'required' | 'not required' | 'completed'",
    )
    msa_justification: str = Field(
        ...,
        description="Plain language justification for MSA decision",
    )
    data_collection_complete: bool = Field(...)
