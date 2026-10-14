"""Structured outputs for the coaching grader — procedure step 6.5.

Canonical: **§62.3 — S-C22** (`CoachingGraderVerdict`); §62.4's `CoherenceResult` is retired with the
coherence judge (ADR-0083). Architecture
§19.7, §19.8, §21, §34, §36.

NEITHER OF THESE CLOSES ITS SPEC-GAP
------------------------------------
**G-09 and G-12 are open and founder-owned.** Both schemas are *named* in §21's
mapping table and *defined nowhere*, and each gap asks a specific design
question this file does not answer:

  * **G-09** — *"whether it returns one verdict or three, and what drives the
    retry decision of S-C13 B2, is unstated"*
  * **G-12** — *"whether it reuses `CriterionVerdict` … or needs its own
    per-criterion type, is undecided, and the answer determines whether `tier`
    is meaningful for coaching criteria at all"*

What is below is the minimum the **ratified EARS behaviours** require, built
from what §19.7 and §36 already state, and no more. Same posture as G-29/G-30
at 6.2 and G-24 at 6.3: implement the behaviour, name the gap, leave it open.

**`tier` is deliberately absent from the coaching verdict.** §35's two tiers are
a property of *gate fields* — Tier 1 blocks the gate, Tier 2 warns — and
`COACHING_QUALITY_RUBRIC`'s criteria are not fields and have no tiers in §36.
Adding one would answer G-12 by invention, in the direction the gap explicitly
flags as undecided.

`CriterionVerdict` and `GraderVerdict` — Layer 2d's — landed with Define's
rubric (R7, 2026-09-26). `ConstraintVerdict` and `ConstraintCheckResult`
(Layer 2c) are still to come.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class CriterionResult(BaseModel):
    """One `COACHING_QUALITY_RUBRIC` criterion's verdict — §36, S-C14 B3.

    **Per criterion, never an overall score** (B3), and the feedback is
    specific (B4): *"you ran `calculate_cpk` without teaching what capability
    is"*, never *"try again"*. A coach handed an aggregate has nothing to act
    on, which is the whole reason B3 exists.

    **No `tier` field** — see the module docstring and G-12.
    """

    criterion: str = Field(description="The rubric line being judged.")
    status: Literal["pass", "fail"] = Field(
        description="Whether the coach met this criterion on this turn.",
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


class CriterionCheck(BaseModel):
    """Grader v2 (ADR-0084) — one criterion's judgement of one reply. **The order of the fields is the
    order the model writes them in**: the reasoning first, then the sentence quoted from the reply as
    evidence, then the verdict — a verdict written before its reasons is the v1 flaw this order removes."""

    criterion: Literal["C1", "C2", "C3", "C4"] = Field(description="Which criterion: C1, C2, C3 or C4.")
    reasoning: str = Field(description="Why, in one to three sentences, before any verdict.")
    evidence: str = Field(
        default="",
        description="One sentence copied word for word from the reply that the verdict rests on; empty only "
                    "when the verdict is not_applicable.")
    verdict: Literal["pass", "fail", "not_applicable"] = Field(
        description="pass, fail, or not_applicable when the criterion does not apply to this reply.")


class GraderV2Verdict(BaseModel):
    """Grader v2 (ADR-0084) — the reply's judgement, one entry per criterion asked about."""

    criteria: list[CriterionCheck] = Field(default_factory=list)


__all__ = ["CriterionResult", "CoachingGraderVerdict",
           "CriterionVerdict", "GraderVerdict", "CriterionCheck", "GraderV2Verdict"]
