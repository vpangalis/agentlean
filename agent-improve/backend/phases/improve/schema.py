from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SolutionCandidate(BaseModel):
    description: str = Field(..., description="Plain language solution description")
    impact_score: int = Field(..., ge=1, le=5, description="1=low 5=high impact")
    effort_score: int = Field(..., ge=1, le=5, description="1=low 5=high effort")
    selected: bool = Field(..., description="True for the chosen solution")


class PilotResult(BaseModel):
    metric: str = Field(..., description="What was measured in the pilot")
    before: str = Field(..., description="Value before pilot")
    after: str = Field(..., description="Value after pilot")
    improvement_confirmed: bool


class ImprovePhaseInput(BaseModel):
    """Gate model for Improve phase — solution selection and pilot."""

    solution_candidates: list[SolutionCandidate] = Field(
        ...,
        min_length=2,
        description="At least 2 options evaluated — shows selection was rigorous",
    )
    selected_solution_summary: str = Field(
        ..., description="Plain language description of chosen solution"
    )
    selection_justification: str = Field(
        ..., description="Why this solution was chosen over alternatives"
    )
    pilot_results: list[PilotResult] = Field(..., min_length=1)
    pilot_confirms_improvement: bool = Field(...)
    implementation_plan_approved: bool = Field(...)
    sponsor_approved: bool = Field(...)
