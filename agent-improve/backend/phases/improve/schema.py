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

    # ── phase_metrics — on all five schemas (§40, §63.9, S-C39) ───────
    # NOTE: this class is still the v1 `ImprovePhaseInput`. `phase_metrics` is added
    # here so the uniform-on-all-five rule holds today; it carries through the
    # v2 `ImproveOutput` rebuild at procedure step 3.4 unchanged.
    phase_metrics: List[dict] = Field(
        default_factory=list,
        description=(
            "What this phase produced for each registry metric it engaged. One "
            "entry per metric, `name` equal to a `metric_definitions` name from "
            "Define (§63.8) — the grader traces a metric across phases by key "
            "equality on `name`. Improve records LINKAGE, not values: which registry metric each selected solution targets. "
            "A phase touching no metric writes 'none this phase', never a "
            "silent gap (§40)."
        ),
    )
