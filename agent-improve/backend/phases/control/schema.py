from __future__ import annotations

from pydantic import BaseModel, Field


class ControlMeasure(BaseModel):
    metric: str = Field(..., description="What is being monitored")
    owner: str = Field(..., description="Named person responsible for monitoring")
    frequency: str = Field(..., description="e.g. weekly, per inspection cycle")
    upper_control_limit: str = Field(..., description="Value that triggers response")
    lower_control_limit: str = Field(..., description="Value that triggers response")
    response_action: str = Field(..., description="What to do if limit breached")


class ControlPhaseInput(BaseModel):
    """Gate model for Control phase — sustain and hand over."""

    control_measures: list[ControlMeasure] = Field(..., min_length=1)
    control_chart_configured: bool = Field(...)
    monitoring_system: str = Field(
        ..., description="Where monitoring data will be recorded"
    )
    training_complete: bool = Field(
        ..., description="Team trained on new process and response plan"
    )
    documentation_updated: bool = Field(
        ..., description="SOPs or work instructions updated"
    )
    sponsor_signoff: bool = Field(...)
    handover_complete: bool = Field(...)
    financial_impact_verified: str = Field(
        ..., description="Confirmed saving or cost reduction vs baseline"
    )
