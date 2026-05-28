from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TeamMember(BaseModel):
    name: str
    role: str


class DefinePhaseInput(BaseModel):
    """Gate model for Define phase — 5W2H + charter.
    All fields required. Validator instantiates this from phase_inputs['define']."""

    # 5W2H elements
    what: str = Field(..., description="Problem in plain observable terms")
    where: str = Field(..., description="Location, asset, line, depot")
    when: str = Field(..., description="Timing, trend, since when")
    who_affected: str = Field(..., description="Who is impacted")
    why_it_matters: str = Field(..., description="Business impact, cost, safety")
    how_much_baseline: str = Field(
        ..., description="Quantified baseline e.g. 1.8mm vs 1.3mm avg"
    )
    how_goal: str = Field(
        ..., description="Target state e.g. reduce by 35% in 5 months"
    )

    # Charter
    process_owner: str = Field(..., description="Named person who owns the process")
    sponsor: str = Field(..., description="Named sponsor who approved the project")
    primary_metric: str = Field(..., description="The one number that defines success")
    primary_metric_unit: str = Field(..., description="Unit of primary metric")
    secondary_metric: str = Field(
        ..., description="Safety metric — detect unintended consequences"
    )
    belt_level: str = Field(..., description="yellow | green | black")
    target_date: str = Field(..., description="Target completion date ISO format")
    team_members: list[TeamMember] = Field(..., min_length=1)

    # Financial impact
    current_cost: str = Field(
        ..., description="Current cost of the problem e.g. €35k/month revenue loss"
    )
    expected_saving: str = Field(
        ..., description="Projected saving after improvement e.g. €20k/month"
    )

    # Project plan
    project_milestones: str = Field(
        ..., description="Key milestones as free text e.g. Define done Week 2, Measure done Week 6"
    )

    # Goal & Scope
    goal_statement: str = Field(
        ...,
        description=(
            "Single precise goal sentence e.g. "
            "'Reduce complaints from 28 to under 20 per week within 6 months'"
        )
    )
    scope_in: str = Field(
        ...,
        description="What is explicitly in scope for this project"
    )
    scope_out: str = Field(
        ...,
        description="What is explicitly out of scope for this project"
    )

    # Business case & benefits
    business_case_rationale: str = Field(
        ...,
        description=(
            "Strategic rationale — why the organisation should invest "
            "in this project, linked to business objectives"
        )
    )
    hard_benefits: str = Field(
        ...,
        description=(
            "Quantifiable financial benefits e.g. "
            "'€20k/month cost reduction, 30% reduction in rework hours'"
        )
    )
    soft_benefits: str = Field(
        ...,
        description=(
            "Qualitative benefits e.g. "
            "'Improved customer satisfaction, higher team morale'"
        )
    )

    estimated_completion_date: str = Field(
        ..., description="Expected project end date or duration e.g. end of Q3 2026"
    )

    # SIPOC diagram
    sipoc: Optional[dict] = Field(
        default=None,
        description=(
            "SIPOC map with keys: suppliers (list[str]), inputs (list[str]), "
            "process_steps (list[str]), outputs (list[str]), customers (list[str])"
        )
    )
