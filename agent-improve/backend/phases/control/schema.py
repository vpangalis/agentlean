from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ControlPhaseInput(BaseModel):
    """Control phase structured data — sustain the improvement."""

    # Work product 1 — Control plan
    control_plan: Optional[str] = Field(
        None,
        description="What will be controlled and how. Gate-required."
    )
    control_measures: Optional[List[str]] = Field(
        None,
        description="Specific control measures put in place."
    )

    # Work product 2 — Monitoring
    monitoring_method: Optional[str] = Field(
        None,
        description="How the primary metric will be tracked. Gate-required."
    )
    monitoring_frequency: Optional[str] = Field(
        None,
        description="How often monitoring occurs (daily, weekly, etc.)"
    )
    control_chart_type: Optional[str] = Field(
        None,
        description="Type of control chart or tracking tool used, if any."
    )

    # Work product 3 — Response plan
    response_plan: Optional[str] = Field(
        None,
        description="What happens if the metric deteriorates."
    )
    trigger_threshold: Optional[str] = Field(
        None,
        description="The threshold that triggers the response plan."
    )

    # Work product 4 — Documentation
    documentation_updated: Optional[str] = Field(
        None,
        description="Which documents, SOPs, or systems were updated."
    )
    training_completed: Optional[str] = Field(
        None,
        description="Whether team training on the new process is done."
    )

    # Work product 5 — Sustainability
    sustainability_confirmed: Optional[str] = Field(
        None,
        description="'yes' or 'no'. Gate-required."
    )
    sponsor_final_sign_off: Optional[str] = Field(
        None,
        description="Name of sponsor who confirmed project closure."
    )

    # ── actual_close_date — Tier 2, added at the Control review (F-12) ──
    actual_close_date: Optional[str] = Field(
        None,
        description=(
            "The ACHIEVED completion date, ISO format — the paired value for "
            "Define's PLANNED `target_date` (§39.1.2). Tier 2: a slipped date "
            "does not invalidate the improvement, the same logic that makes "
            "Define's target_date a planning parameter. Closes F-12."
        ),
    )

    # ── phase_metrics — on all five schemas (§40, §63.9, S-C39) ───────
    # NOTE: this class is still the v1 `ControlPhaseInput`. `phase_metrics` is added
    # here so the uniform-on-all-five rule holds today; it carries through the
    # v2 `ControlOutput` rebuild at procedure step 3.4 unchanged.
    phase_metrics: List[dict] = Field(
        default_factory=list,
        description=(
            "What this phase produced for each registry metric it engaged. One "
            "entry per metric, `name` equal to a `metric_definitions` name from "
            "Define (§63.8) — the grader traces a metric across phases by key "
            "equality on `name`. Control records the achieved state and the comparison: {name, unit, post_improvement_metrics, improvement_delta, source: 'measured'}. "
            "A phase touching no metric writes 'none this phase', never a "
            "silent gap (§40)."
        ),
    )
