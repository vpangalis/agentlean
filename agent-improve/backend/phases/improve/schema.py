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


from backend.phases.gate_assembly import (  # noqa: E402
    build_gate_document,
    tier_1,
    tier_2,
)


# =======================================================================
# IMPROVE'S GATE DOCUMENT -- 14 fields (4 Tier 1, 5 Tier 2,
# `phase_metrics`, 4 gate metadata). Canonical: S-C30 (63.4) + 40.
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

IMPROVE_TIER_1_FIELDS: tuple[str, ...] = (
    "selected_solution",
    "pilot_result",
    "experiment_justification",
    "issues_and_barriers",
)

IMPROVE_TIER_2_FIELDS: tuple[str, ...] = (
    "solution_linked_to_root_cause",
    "implementation_plan",
    "explanatory_power",
    "process_owner_buyin",
    "secondary_metrics",
)


class ImproveOutput(BaseModel):
    """Gate document for the Improve phase -- 14 fields.

    4 Tier 1, 5 Tier 2, `phase_metrics`, 4 gate metadata (S-C30, 40).
    Declaration order is the spec's: Tier 1, Tier 2, `phase_metrics`, metadata.

    Two movements: CHOOSE (generate candidates, then select on explicit
    criteria) then PROVE (pilot at limited scale, then confirm). The
    field order enforces it -- you decide how hard to test after you
    know what you are choosing between.
    """

    # -- Tier 1 -- gate-required (35) ----------------------------------
    selected_solution: str = Field(
        ...,
        description=(
            "Criteria-based selection, documented. A decision matrix rather than a preference."
        ),
    )
    pilot_result: str = Field(
        ...,
        description=(
            "Practical AND statistical significance -- the same two-gate test Analyse uses. A trivial-effect pilot is coached back."
        ),
    )
    experiment_justification: str = Field(
        ...,
        description=(
            "DOE conducted, a simplified one-factor experiment, or no experiment needed because the solution follows from root cause analysis. ALL THREE ARE VALID (B1) -- the failure this catches is drifting past the question, not skipping DOE. DOE is recommended for Black Belts and suppressed for Green Belts, but the question is asked of both (B2)."
        ),
    )
    issues_and_barriers: str = Field(
        ...,
        description=(
            "Belt-stated blockers."
        ),
    )

    # -- Tier 2 -- rubric-recommended; at worst a `warning` (35) --------
    solution_linked_to_root_cause: dict = Field(
        default_factory=dict,
        description=(
            "Cross-phase reference dict -> Analyse's root cause (7, S-C32). Names the metric via `references_metric_name`, so a multi-metric project links the solution to the specific Y its root cause explained; the grader resolves it by lookup (B3)."
        ),
    )
    implementation_plan: str = Field(
        default_factory=str,
        description=(
            "Timeline, owner, resources."
        ),
    )
    explanatory_power: str = Field(
        default_factory=str,
        description=(
            "R-squared / variance explained."
        ),
    )
    process_owner_buyin: str = Field(
        default_factory=str,
        description=(
            "The process owner accepts the solution."
        ),
    )
    secondary_metrics: str = Field(
        default_factory=str,
        description=(
            "What could get worse. On all five schemas (40)."
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
            "Improve's entries carry LINKAGE-PLUS-PILOT -- which metric the solution targets and what the pilot achieved on it. A metric the solution does not target writes 'not addressed this phase'."
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


def assemble_improve_gate_document(
    artifacts: dict,
    citations: list[dict],
    uploads: list[dict],
    acknowledged_gaps: list[str],
) -> ImproveOutput:
    """Construct Improve's gate document from captured values (S-F28).

    Both S-F28 invariants run first, inside `build_gate_document`: metric
    single authority (39.2.3), then field coverage. Every one of the 14
    schema fields is referenced below -- that IS invariant 1, and G-28 is the
    risk it exists to close.
    """
    values = {
        # Tier 1 -- direct access; a KeyError is correct (40.1)
        "selected_solution": tier_1(artifacts, "selected_solution"),
        "pilot_result": tier_1(artifacts, "pilot_result"),
        "experiment_justification": tier_1(artifacts, "experiment_justification"),
        "issues_and_barriers": tier_1(artifacts, "issues_and_barriers"),
        # Tier 2 -- .get(); an empty value records a conscious gap (35)
        "solution_linked_to_root_cause": tier_2(artifacts, "solution_linked_to_root_cause", {}),
        "implementation_plan": tier_2(artifacts, "implementation_plan"),
        "explanatory_power": tier_2(artifacts, "explanatory_power"),
        "process_owner_buyin": tier_2(artifacts, "process_owner_buyin"),
        "secondary_metrics": tier_2(artifacts, "secondary_metrics"),
        # On all five schemas (63.9)
        "phase_metrics": artifacts.get("phase_metrics", []),
        # Gate metadata (40)
        "computation_results": artifacts.get("computation_results", []),
        "acknowledged_gaps": acknowledged_gaps,
        "citations": citations,
        "uploads": uploads,
    }
    return build_gate_document(ImproveOutput, "improve", artifacts, values)
