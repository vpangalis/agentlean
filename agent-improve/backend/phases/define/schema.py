from __future__ import annotations

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
