"""Structured outputs for middleware positions 7 and 8 — procedure step 6.5.

Canonical: **§62.3 — S-C22** (`CoachingGraderVerdict`) and **§62.4 — S-C23**
(`CoherenceResult`), both of which assign this file and this step. Architecture
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

**The other four schemas §2 lists for this file are stage 7's** —
`CriterionVerdict`, `GraderVerdict`, `ConstraintVerdict` and
`ConstraintCheckResult` land with layers 2b-2d at steps 7.1 and 7.2.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class CoherenceResult(BaseModel):
    """Validation Layer 2a's verdict — S-C23, §19.7.

    **The three questions are §19.7's, verbatim**: is this a real, conclusive
    statement? Is it parroting the Belt's own words back? Is it on-topic for
    this phase? They are carried as three separate booleans rather than one
    score because the retry feedback has to say *which* failed — S-C14 B4's
    "never 'try again'" is the grader's rule, and the same reasoning applies to
    a retry the Belt never sees.

    `coherent` is what drives S-C13 B2's retry. **That it is a single field is
    the part G-09 leaves open** — the alternative, retrying on any one of the
    three, is not obviously wrong and is not chosen here.
    """

    coherent: bool = Field(
        description=(
            "True when the response is a real, conclusive, on-topic coaching "
            "turn. False triggers a silent retry the Belt never sees."
        ),
    )
    is_conclusive: bool = Field(
        description=(
            "Does it actually say something? False for gibberish, and for a "
            "vague non-answer that fills space without committing to anything."
        ),
    )
    is_parroting: bool = Field(
        description=(
            "Is it repeating the Belt's own words back as though they were "
            "coaching? True is a FAILURE — the Belt learns nothing from being "
            "quoted to themselves."
        ),
    )
    on_topic: bool = Field(
        description="Is it about the current DMAIC phase's work?",
    )
    reason: str = Field(
        default="",
        description=(
            "Why it failed, specifically, for the retry. Empty when coherent."
        ),
    )


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


__all__ = ["CoherenceResult", "CriterionResult", "CoachingGraderVerdict"]
