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


from backend.phases.gate_assembly import (  # noqa: E402
    build_gate_document,
    tier_1,
    tier_2,
)


# =======================================================================
# ANALYSE'S GATE DOCUMENT -- 14 fields (4 Tier 1, 5 Tier 2,
# `phase_metrics`, 4 gate metadata). Canonical: S-C29 (63.3) + 40.
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

ANALYSE_TIER_1_FIELDS: tuple[str, ...] = (
    "root_cause_statement",
    "root_cause_validation",
    "practical_significance",
    "issues_and_barriers",
)

ANALYSE_TIER_2_FIELDS: tuple[str, ...] = (
    "causal_hypothesis",
    "ruled_out_causes",
    "statistical_problem_statement",
    "process_owner_buyin",
    "secondary_metrics",
)


class AnalyseOutput(BaseModel):
    """Gate document for the Analyse phase -- 14 fields.

    4 Tier 1, 5 Tier 2, `phase_metrics`, 4 gate metadata (S-C29, 40).
    Declaration order is the spec's: Tier 1, Tier 2, `phase_metrics`, metadata.

    `practical_significance` is Tier 1 (B3) -- the eBook's second gate:
    how much of the problem does this actually explain. A validated cause
    explaining a trivial share is coached back, not passed.
    """

    # -- Tier 1 -- gate-required (35) ----------------------------------
    root_cause_statement: str = Field(
        ...,
        description=(
            "Specific and actionable. Coached at position 5, AFTER validation and ruling-out -- you state the cause once, once it is proven."
        ),
    )
    root_cause_validation: str = Field(
        ...,
        description=(
            "Statistical or observational evidence. Correlation is not causation: an association result needs a stated mechanism before it counts as a root cause."
        ),
    )
    practical_significance: str = Field(
        ...,
        description=(
            "How much of the problem the cause explains. Statistical significance is not practical significance."
        ),
    )
    issues_and_barriers: str = Field(
        ...,
        description=(
            "Belt-stated blockers."
        ),
    )

    # -- Tier 2 -- rubric-recommended; at worst a `warning` (35) --------
    causal_hypothesis: dict = Field(
        default_factory=dict,
        description=(
            "Cross-phase reference dict -> Measure's baseline (7, S-C32). Carries the Belt's content plus `references_phase`, `references_field`, `references_value` and `references_metric_name`, so the grader verifies the link by LOOKUP rather than judgment (B1)."
        ),
    )
    ruled_out_causes: str = Field(
        default_factory=str,
        description=(
            "Alternatives rejected, with rationale."
        ),
    )
    statistical_problem_statement: str = Field(
        default_factory=str,
        description=(
            "Required of ALL Belts, in Analyse and not Define -- no longer belt-gated (B2)."
        ),
    )
    process_owner_buyin: str = Field(
        default_factory=str,
        description=(
            "The process owner accepts the root causes."
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
            "Analyse's entries carry LINKAGE, not values -- which registry metric each validated root cause explains. A metric this phase does not touch writes 'not addressed this phase'."
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


def assemble_analyse_gate_document(
    artifacts: dict,
    citations: list[dict],
    uploads: list[dict],
    acknowledged_gaps: list[str],
) -> AnalyseOutput:
    """Construct Analyse's gate document from captured values (S-F28).

    Both S-F28 invariants run first, inside `build_gate_document`: metric
    single authority (39.2.3), then field coverage. Every one of the 14
    schema fields is referenced below -- that IS invariant 1, and G-28 is the
    risk it exists to close.
    """
    values = {
        # Tier 1 -- direct access; a KeyError is correct (40.1)
        "root_cause_statement": tier_1(artifacts, "root_cause_statement"),
        "root_cause_validation": tier_1(artifacts, "root_cause_validation"),
        "practical_significance": tier_1(artifacts, "practical_significance"),
        "issues_and_barriers": tier_1(artifacts, "issues_and_barriers"),
        # Tier 2 -- .get(); an empty value records a conscious gap (35)
        "causal_hypothesis": tier_2(artifacts, "causal_hypothesis", {}),
        "ruled_out_causes": tier_2(artifacts, "ruled_out_causes"),
        "statistical_problem_statement": tier_2(artifacts, "statistical_problem_statement"),
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
    return build_gate_document(AnalyseOutput, "analyse", artifacts, values)
