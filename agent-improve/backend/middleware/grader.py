"""`DMAICGraderMiddleware` — position 8 — procedure step 6.5.

Canonical: **§61.5 — S-C14**. Architecture **§19.8**, **§36** (the rubric and
the two-grader distinction), §21, §11.

THERE ARE TWO GRADERS AND CONFUSING THEM IS A VIOLATION
--------------------------------------------------------
|  | this one | validation Layer 2d |
|---|---|---|
| Where | middleware, inside the executor | the `validation_stack` node |
| When | **every coaching turn** | **once**, at the gate boundary |
| Rubric | `COACHING_QUALITY_RUBRIC` — one, shared | `PHASE_RUBRIC` — five |
| Grades | the coach's **process** | the **gate document** |
| Sees | one response | the complete field set |

**Never point this at a phase rubric** (B1). They are not redundant: this
catches a coach accepting "poor morale" as a root cause before the Belt sees it;
2d catches four fields that each look sound while referencing different metrics.

WHAT IT RETURNS, AND WHAT IT KEEPS TO ITSELF
---------------------------------------------
**B3: per criterion, never an overall score. B4: feedback specific, never "try
again"** — a coach handed an aggregate has nothing to act on.

**B7: iteration count, accumulated evaluations and attempt tracking stay
PRIVATE to this middleware and never reach `PhaseState` or `SupervisorState`.**
They are instance attributes here for exactly that reason; what leaves is the
`step_log` entry B6 requires and nothing else.

**B5: on `max_iterations_reached` the output passes through with a warning flag
the Belt sees.** The turn is not blocked — §34.2's hierarchy puts blocking at
the gate, not mid-conversation.

**B8: the Belt does not see the grader loop.** It runs at step 2 of the
nine-step gate, before the interrupt (§33).

> **SPEC-GAP (G-12) is OPEN.** `CoachingGraderVerdict`'s shape — whether it
> reuses `CriterionVerdict`, and whether `tier` means anything for coaching
> criteria — is undecided. See `validation/schemas.py`; `tier` is deliberately
> absent rather than invented.
> **SPEC-GAP (G-24):** constructor arguments unstated, *"including how
> `max_iterations` and `on_evaluation` are passed"*. Both are taken as
> constructor arguments below, which is the reading §19.8's own prose implies.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from langchain.agents.middleware import AgentMiddleware

from backend.core.llm import get_llm
from backend.core.prompts import COACHING_QUALITY_RUBRIC
from backend.middleware.coherence import CoherenceMiddleware
from backend.validation.schemas import CoachingGraderVerdict

logger = logging.getLogger(__name__)

#: §19.8 / S-C14 B5.
GRADER_MAX_ITERATIONS = 3

#: What the Belt is shown when grading could not settle (B5). Plain language
#: (§13) — it names no rubric, no iteration count and no internal machinery.
MAX_ITERATIONS_WARNING = (
    "I was not able to fully check this response against my own coaching "
    "standards. It may be less useful than usual — say so and I will try again."
)

_PROMPT = """\
You are grading ONE coaching turn against the standards below. You are judging
the COACH's process, not the Belt's project and not the coach's writing style.

Return one verdict per criterion. Never an overall score - a coach handed an
aggregate has nothing to act on. Where a criterion fails, say specifically what
to change: name the behaviour, not the rule. "Try again" is not feedback.

THE STANDARDS:
{rubric}

THE BELT SAID:
{belt}

THE COACH REPLIED:
{coach}
"""


class DMAICGraderMiddleware(AgentMiddleware):
    """Position 8, `after_agent`. Grades the coach's process every turn."""

    name = "DMAICGraderMiddleware"

    def __init__(
        self,
        phase: str,
        max_iterations: int = GRADER_MAX_ITERATIONS,
        on_evaluation: Optional[Callable[[dict[str, Any]], None]] = None,
        coherence: Optional["CoherenceMiddleware"] = None,
    ) -> None:
        super().__init__()
        self.phase = phase
        #: **S-C13 B3's channel, and it is a reference rather than state.**
        #: A dict returned from one `after_agent` is not visible to the next
        #: hook in the same pass — measured, not assumed — so the skip signal
        #: cannot travel through state. Both middlewares are constructed per
        #: turn in `_build_executor`, so this reference cannot outlive the
        #: turn and nothing reaches `PhaseState` (B7).
        self._coherence = coherence
        self.max_iterations = max_iterations
        #: B6 — each iteration goes to `step_log` through this callback. The
        #: middleware does not write state itself; the node owns that.
        self.on_evaluation = on_evaluation
        # ── B7: PRIVATE. None of these may reach PhaseState. ──────────────
        self._iterations = 0
        self._evaluations: list[CoachingGraderVerdict] = []

    async def aafter_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        """B1-B6. Skipped entirely when position 7 degraded the turn."""
        if self._skipped(state):
            logger.info(
                "%s.grader: SKIPPED — coherence degraded this turn (S-C13 B3)",
                self.phase,
            )
            return None

        coach_text = self._coach_text(state)
        if not coach_text:
            return None
        belt_text = self._belt_text(state)

        self._iterations = 0
        self._evaluations = []

        for _ in range(self.max_iterations):
            self._iterations += 1
            verdict = await self._grade(belt_text, coach_text)
            self._evaluations.append(verdict)
            self._emit(verdict)
            if verdict.passed:
                return None
            logger.info(
                "%s.grader: iteration %d — %d criterion/criteria failed: %s",
                self.phase, self._iterations, len(verdict.failed),
                [c.criterion for c in verdict.failed],
            )

        # B5 — passes through, with a warning the Belt sees.
        logger.warning(
            "%s.grader: max_iterations=%d reached; passing the turn through "
            "with a Belt-visible warning", self.phase, self.max_iterations,
        )
        return {"grader_warning": MAX_ITERATIONS_WARNING}

    def after_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        """Sync entry point — grading is a model call; §1.4 puts it on async."""
        return None

    async def _grade(self, belt: str, coach: str) -> CoachingGraderVerdict:
        """One grading call — `grader` role, temperature 0.1 (B2).

        **The temperature is a hard requirement, not a tuning knob** (§21): a
        grader returning different verdicts across runs makes §52's regression
        thresholds meaningless, because a 10% drop cannot be detected against a
        baseline that moves on its own. It is the role default, so `get_llm`
        supplies it.
        """
        model = get_llm("grader").with_structured_output(CoachingGraderVerdict)
        prompt = _PROMPT.format(rubric=COACHING_QUALITY_RUBRIC,
                                belt=belt[:2000], coach=coach[:4000])
        return CoachingGraderVerdict.model_validate(await model.ainvoke(prompt))

    def _emit(self, verdict: CoachingGraderVerdict) -> None:
        """B6 — one `step_log` entry per iteration, via `on_evaluation`.

        **Dicts only** (§10.3): named keys are what make the audit trail
        queryable, and tuples are banned. The callback is what keeps B7 true —
        the middleware hands over a record and keeps its counters.
        """
        if self.on_evaluation is None:
            return
        self.on_evaluation({
            "layer": "coaching_grader",
            "iteration": self._iterations,
            "status": "pass" if verdict.passed else "failed",
            "criteria_failed": [c.criterion for c in verdict.failed],
            "feedback": [c.feedback for c in verdict.failed if c.feedback],
        })

    # ── reading the turn ─────────────────────────────────────────────────

    def _skipped(self, state: Any) -> bool:
        """S-C13 B3 — position 7 degraded this turn, so grading is pointless."""
        return bool(self._coherence is not None and self._coherence.degraded)

    @staticmethod
    def _coach_text(state: Any) -> str:
        response = (state or {}).get("structured_response") if isinstance(
            state, dict) else getattr(state, "structured_response", None)
        if response is not None and str(getattr(response, "message", None) or ""):
            return str(response.message)
        messages = (state or {}).get("messages") if isinstance(state, dict) else []
        for message in reversed(list(messages or [])):
            if str(getattr(message, "type", "")) == "ai" and str(message.content).strip():
                return str(message.content)
        return ""

    @staticmethod
    def _belt_text(state: Any) -> str:
        messages = (state or {}).get("messages") if isinstance(state, dict) else []
        for message in reversed(list(messages or [])):
            if str(getattr(message, "type", "")) == "human":
                return str(message.content)
        return ""


__all__ = [
    "DMAICGraderMiddleware",
    "GRADER_MAX_ITERATIONS",
    "MAX_ITERATIONS_WARNING",
]
