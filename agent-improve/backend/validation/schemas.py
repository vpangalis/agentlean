"""Structured outputs for the coaching grader and the gate document's grader.

`CoachingGraderVerdict` is the coaching grader's output; `CriterionVerdict` and
`GraderVerdict` are Layer 2d's (R7). There is no coherence judge (ADR-0083).

G-12 IS OPEN, AND THIS FILE DOES NOT CLOSE IT
---------------------------------------------
**G-12 is open and founder-owned:** whether the coaching verdict reuses
`CriterionVerdict` or needs its own per-criterion type is undecided, and the
answer determines whether `tier` is meaningful for coaching criteria at all.

What is below is the minimum the ratified behaviours require, and no more:
implement the behaviour, name the gap, leave it open.

**`tier` is deliberately absent from the coaching verdict.** The two tiers are
a property of *gate fields* — Tier 1 blocks the gate, Tier 2 warns — and
`COACHING_QUALITY_RUBRIC`'s criteria are not fields and have no tiers.
Adding one would answer G-12 by invention, in the direction the gap explicitly
flags as undecided.

Layer 2c's `ConstraintVerdict` and `ConstraintCheckResult` are not built.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class CriterionResult(BaseModel):
    """One `COACHING_QUALITY_RUBRIC` criterion's verdict — §36, S-C14 B3.

    **Per criterion, never an overall score** (B3), and the feedback is
    specific (B4): *"you ran `calculate_cpk` without teaching what capability
    is"*, never *"try again"*. A coach handed an aggregate has nothing to act
    on, which is the whole reason B3 exists.

    **No `tier` field** — see the module docstring and G-12.
    """

    criterion: str = Field(description="The criterion's id: G1 to G6.")
    evidence: str = Field(
        default="",
        description=(
            "On a fail: the sentence of the reply that breaks the criterion, copied word for word. "
            "Empty on a pass. A fail without it is not counted (founder ruling 2026-10-14)."
        ),
    )
    status: Literal["pass", "fail", "unknown"] = Field(
        description="Whether the coach met this criterion on this turn; 'unknown' when what you were given does "
                    "not let you decide (recorded, never counted as a fail).",
    )
    feedback: str = Field(
        default="",
        description=(
            "What specifically to change, when the status is 'fail'. Names the "
            "behaviour, not the rule. Empty on a pass."
        ),
    )


class CoachingGraderVerdict(BaseModel):
    """`DMAICGraderMiddleware`'s structured output — S-C22, §19.8, §36.

    **Grades the coach's PROCESS, every turn, against the one shared
    `COACHING_QUALITY_RUBRIC`.** It is not Layer 2d, which grades the gate
    *document* against a `PHASE_RUBRIC` once per phase — §19.8 calls confusing
    the two a violation, and they are two classes in two files for that reason.
    """

    criteria: list[CriterionResult] = Field(
        default_factory=list,
        description="One entry per rubric criterion. Never an overall score.",
    )
    warning: Optional[str] = Field(
        default=None,
        description=(
            "Set only when grading could not settle within its iteration "
            "budget. Belt-visible (S-C14 B5)."
        ),
    )

    @property
    def failed(self) -> list[CriterionResult]:
        """The criteria the coach did not meet — what feedback is built from."""
        return [c for c in self.criteria if c.status == "fail"]

    @property
    def passed(self) -> bool:
        """True when no criterion failed. **Derived, never a stored score.**"""
        return not self.failed


class CriterionVerdict(BaseModel):
    """One `{PHASE}_RUBRIC` criterion's verdict on the GATE DOCUMENT — Layer 2d
    (§9.7, S-C20). Per criterion, with specific feedback. Define is Tier 1
    throughout (R7, 2026-09-26): its criteria `pass` or `fail`, never `warning`."""

    criterion: str = Field(description="The rubric criterion id, e.g. 'DEF-R01'.")
    tier: int = Field(default=1, description="1 blocks the gate; 2 may only warn.")
    status: Literal["pass", "warning", "fail"] = Field(
        description="Whether the document meets the criterion.")
    feedback: str = Field(
        default="",
        description="The reason — what the document lacks and the one fix. Empty on a pass.")

    @model_validator(mode="after")
    def _tier_2_only_warns(self) -> "CriterionVerdict":
        """T66, ADR-0040 (DEF-138): a Tier 2 criterion can never fail a gate — its 'fail' is a 'warning'."""
        if self.tier == 2 and self.status == "fail":
            self.status = "warning"
        return self


class GraderVerdict(BaseModel):
    """Layer 2d's structured output: one verdict per rubric criterion (§9.7).
    Never an overall score; `passed` is derived."""

    verdicts: list[CriterionVerdict] = Field(
        default_factory=list,
        description="One entry per criterion judged. Never an overall score.")

    @property
    def failed(self) -> list[CriterionVerdict]:
        return [v for v in self.verdicts if v.status == "fail"]

    @property
    def passed(self) -> bool:
        return not self.failed


__all__ = ["CriterionResult", "CoachingGraderVerdict",
           "CriterionVerdict", "GraderVerdict"]
