from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ImprovePhaseInput(BaseModel):
    """Improve phase structured data — solution design and validation."""

    # Work product 1 — Solution generation
    solution_ideas: Optional[List[str]] = Field(
        None,
        description="All solution ideas brainstormed. One idea per string."
    )
    solution_evaluation: Optional[str] = Field(
        None,
        description="How ideas were compared (impact, effort, cost, etc.)"
    )

    # Work product 2 — Solution selection
    selected_solution: Optional[str] = Field(
        None,
        description="The chosen solution. Gate-required."
    )
    selection_rationale: Optional[str] = Field(
        None,
        description="Why this solution was chosen over alternatives."
    )

    # Work product 3 — Pilot plan
    pilot_plan: Optional[str] = Field(
        None,
        description="How the pilot or test will be run."
    )
    pilot_scope: Optional[str] = Field(
        None,
        description="Where, who, and when the pilot will run."
    )

    # Work product 4 — Results
    pilot_result: Optional[str] = Field(
        None,
        description="What happened in the pilot. Gate-required."
    )
    improvement_confirmed: Optional[str] = Field(
        None,
        description="'yes', 'partial', or 'no'. Gate-required."
    )
    projected_improvement: Optional[str] = Field(
        None,
        description="Expected gain once fully implemented, linked to metric."
    )

    # Work product 5 — Implementation
    implementation_plan: Optional[str] = Field(
        None,
        description="Rollout plan: steps, owners, timeline."
    )
    sponsor_sign_off: Optional[str] = Field(
        None,
        description="Name of sponsor or process owner who approved."
    )
