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
