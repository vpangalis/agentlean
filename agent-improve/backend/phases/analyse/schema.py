from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class AnalysePhaseInput(BaseModel):
    """Analyse phase structured data — root cause investigation."""

    # Work product 1 — Cause brainstorming (Fishbone)
    possible_causes: Optional[List[str]] = Field(
        None,
        description="All possible causes identified. Gate requires ≥3."
    )
    cause_categories: Optional[dict] = Field(
        None,
        description=(
            "Causes grouped by category. "
            "e.g. {'People': ['...'], 'Process': ['...']}. "
            "Optional — not gate-required."
        )
    )

    # Work product 2 — Root cause drilling (5 Whys)
    five_whys_analysis: Optional[List[dict]] = Field(
        None,
        description=(
            "Each entry: {'symptom': str, 'whys': [str, ...]}. "
            "Optional — enriches root cause confidence."
        )
    )

    # Work product 3 — Prioritisation (vital few)
    pareto_top_causes: Optional[List[str]] = Field(
        None,
        description="Causes ranked by frequency or impact, highest first."
    )
    vital_few_causes: Optional[str] = Field(
        None,
        description=(
            "Plain-English summary of the 1–3 causes that account "
            "for the majority of the problem. Gate-required."
        )
    )

    # Work product 4 — Verification
    cause_verified: Optional[str] = Field(
        None,
        description="'yes', 'partial', or 'no'. Gate-required."
    )
    verification_method: Optional[str] = Field(
        None,
        description="How the cause was verified (data, test, correlation…)"
    )
    evidence_summary: Optional[str] = Field(
        None,
        description="What the data or evidence actually showed."
    )

    # Work product 5 — Root cause statement
    root_cause_statement: Optional[str] = Field(
        None,
        description=(
            "Specific, measurable, solution-agnostic root cause. "
            "Gate-required. Format: 'The primary driver of X is Y because Z.'"
        )
    )
    root_cause_agreed_by: Optional[str] = Field(
        None,
        description="Process owner or sponsor who reviewed and agreed."
    )

    # ── phase_metrics — on all five schemas (§40, §63.9, S-C39) ───────
    # NOTE: this class is still the v1 `AnalysePhaseInput`. `phase_metrics` is added
    # here so the uniform-on-all-five rule holds today; it carries through the
    # v2 `AnalyseOutput` rebuild at procedure step 3.4 unchanged.
    phase_metrics: List[dict] = Field(
        default_factory=list,
        description=(
            "What this phase produced for each registry metric it engaged. One "
            "entry per metric, `name` equal to a `metric_definitions` name from "
            "Define (§63.8) — the grader traces a metric across phases by key "
            "equality on `name`. Analyse records LINKAGE, not values: which registry metric each validated root cause explains. "
            "A phase touching no metric writes 'none this phase', never a "
            "silent gap (§40)."
        ),
    )
