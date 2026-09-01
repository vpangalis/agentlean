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


from backend.phases.gate_assembly import (  # noqa: E402
    build_gate_document,
    tier_1,
    tier_2,
)


# =======================================================================
# CONTROL'S GATE DOCUMENT -- 17 fields (3 Tier 1, 9 Tier 2,
# `phase_metrics`, 4 gate metadata). Canonical: S-C31 (63.5) + 40.
# Procedure step 3.4, closing G-28 for this phase.
#
# Assembled ONCE, at `gate_apply`, by Pydantic construction over values
# already captured -- there is NO LLM CALL in this path (20, 33).
#
# THE ACCESS PATTERN ENCODES THE TIER (40.1):
#   Tier 1  artifacts["field"]        a KeyError is CORRECT -- Layer 2b
#                                     should have blocked the gate
#   Tier 2  artifacts.get(field, "")  an empty value RECORDS that the Belt
#                                     proceeded without it
# =======================================================================

CONTROL_TIER_1_FIELDS: tuple[str, ...] = (
    "control_plan",
    "post_improvement_metrics",
    "issues_and_barriers",
)

CONTROL_TIER_2_FIELDS: tuple[str, ...] = (
    "improvement_delta",
    "financial_impact_verified",
    "sustainability_check",
    "handover_documented",
    "lessons_learned",
    "transferability",
    "project_signoff",
    "secondary_metrics",
    "actual_close_date",
)


class ControlOutput(BaseModel):
    """Gate document for the Control phase -- 17 fields.

    3 Tier 1, 9 Tier 2, `phase_metrics`, 4 gate metadata (S-C31, 40).
    Declaration order is the spec's: Tier 1, Tier 2, `phase_metrics`, metadata.

    The smallest Tier 1 set and the largest Tier 2 set. The bright line
    is DELIVERY, not authorship -- a control plan written is not a
    control plan delivered, and the classic Control failure is a
    training plan authored and never run.
    """

    # -- Tier 1 -- gate-required (35) ----------------------------------
    control_plan: dict = Field(
        ...,
        description=(
            "FIVE sub-plans, all required (41, S-C33): documentation, monitoring, response, training, aligning_systems. A single string cannot show that four were done and one was skipped (B1)."
        ),
    )
    post_improvement_metrics: dict = Field(
        ...,
        description=(
            "Cross-phase reference dict -> Measure's `baseline_mean` (7, S-C32). THE ONLY CROSS-PHASE REFERENCE FIELD THAT IS TIER 1 (B2) -- a Control phase that cannot link its result back to the baseline has not demonstrated improvement at all. Its `metric` value equals the primary metric's `phase_metrics` `actual`: two names for one number, so a mismatch raises at assembly (39.2.3)."
        ),
    )
    issues_and_barriers: str = Field(
        ...,
        description=(
            "Belt-stated blockers."
        ),
    )

    # -- Tier 2 -- rubric-recommended; at worst a `warning` (35) --------
    improvement_delta: str = Field(
        default_factory=str,
        description=(
            "Change from baseline."
        ),
    )
    financial_impact_verified: str = Field(
        default_factory=str,
        description=(
            "Quantified saving."
        ),
    )
    sustainability_check: str = Field(
        default_factory=str,
        description=(
            "The process for maintaining the gains."
        ),
    )
    handover_documented: str = Field(
        default_factory=str,
        description=(
            "A named process owner accepting."
        ),
    )
    lessons_learned: str = Field(
        default_factory=str,
        description=(
            "Feeds the case index (23.3)."
        ),
    )
    transferability: str = Field(
        default_factory=str,
        description=(
            "Yokoten -- feeds `rag_lookup_case_history` (24)."
        ),
    )
    project_signoff: str = Field(
        default_factory=str,
        description=(
            "Champion + Belt + Finance."
        ),
    )
    secondary_metrics: str = Field(
        default_factory=str,
        description=(
            "What could get worse. On all five schemas (40)."
        ),
    )
    actual_close_date: str = Field(
        default_factory=str,
        description=(
            "ISO. The ACHIEVED completion date, paired with Define's PLANNED `target_date` (F-12). Tier 2 -- a slipped date does not invalidate the improvement (B4)."
        ),
    )

    # -- On all five schemas (63.9, S-C39) -----------------------------
    phase_metrics: list[dict] = Field(
        default_factory=list,
        description=(
            "One entry per registry metric this phase engaged. `name` MUST "
            "equal a `metric_definitions` name verbatim, so key equality "
            "holds (S-C39 B1). A phase touching no metric writes 'none this "
            "phase' rather than leaving the list empty (B2) -- an empty list "
            "reads the same whether the phase engaged no metric or forgot to "
            "record one, and the second is the failure worth catching. "
            "Control's entries carry the COMPARISON -- baseline, target, actual, delta, met -- and are THE AUTHORITATIVE STORE of all N comparisons. The grader grades every entry, not only the primary (B5)."
        ),
    )

    # -- Gate metadata -- the same four on all five schemas (40) --------
    computation_results: list[dict] = Field(default_factory=list)
    acknowledged_gaps: list[str] = Field(
        default_factory=list,
        description=(
            "Tier 2 fields the Belt consciously proceeded without (35). The "
            "next phase's input mapper carries these forward (G-27 ruling) "
            "so a deliberate decision stays distinguishable from an "
            "oversight."
        ),
    )
    citations: list[dict] = Field(default_factory=list)
    uploads: list[dict] = Field(default_factory=list)


def assemble_control_gate_document(
    artifacts: dict,
    citations: list[dict],
    uploads: list[dict],
    acknowledged_gaps: list[str],
) -> ControlOutput:
    """Construct Control's gate document from captured values (S-F28).

    Both S-F28 invariants run first, inside `build_gate_document`: metric
    single authority (39.2.3), then field coverage. Every one of the 17
    schema fields is referenced below -- that IS invariant 1, and G-28 is the
    risk it exists to close.
    """
    values = {
        # Tier 1 -- direct access; a KeyError is correct (40.1)
        "control_plan": tier_1(artifacts, "control_plan"),
        "post_improvement_metrics": tier_1(artifacts, "post_improvement_metrics"),
        "issues_and_barriers": tier_1(artifacts, "issues_and_barriers"),
        # Tier 2 -- .get(); an empty value records a conscious gap (35)
        "improvement_delta": tier_2(artifacts, "improvement_delta"),
        "financial_impact_verified": tier_2(artifacts, "financial_impact_verified"),
        "sustainability_check": tier_2(artifacts, "sustainability_check"),
        "handover_documented": tier_2(artifacts, "handover_documented"),
        "lessons_learned": tier_2(artifacts, "lessons_learned"),
        "transferability": tier_2(artifacts, "transferability"),
        "project_signoff": tier_2(artifacts, "project_signoff"),
        "secondary_metrics": tier_2(artifacts, "secondary_metrics"),
        "actual_close_date": tier_2(artifacts, "actual_close_date"),
        # On all five schemas (63.9)
        "phase_metrics": artifacts.get("phase_metrics", []),
        # Gate metadata (40)
        "computation_results": artifacts.get("computation_results", []),
        "acknowledged_gaps": acknowledged_gaps,
        "citations": citations,
        "uploads": uploads,
    }
    return build_gate_document(ControlOutput, "control", artifacts, values)
