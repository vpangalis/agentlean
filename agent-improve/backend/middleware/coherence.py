"""`CoherenceMiddleware` — position 7 — procedure step 6.5.

Canonical: **§61.4 — S-C13**. Architecture **§19.7**, **§34** (the four-layer
stack), §34.2 (the self-healing hierarchy), §21.

VALIDATION LAYER 2a, AND WHY IT IS MIDDLEWARE
----------------------------------------------
One LLM call at the `coherence` role, temperature 0.1 (B1), asking §19.7's three
questions: is this a real, conclusive statement? Is it parroting the Belt's own
words back? Is it on-topic for this phase?

**Layer 2a fires every coaching turn, which is why it is not in the
`validation_stack` node** — that node runs once, at the gate. Layers 2b-2d live
there; 2a lives here. One conceptual stack, two mechanisms (§34), and moving
either half into the other is a violation.

SILENT RETRY IS THE ONE SANCTIONED OPACITY
-------------------------------------------
**B2: retry silently, at most twice — the Belt never sees a failed coherence
response.** §34.2 calls this the narrowly-scoped exception to the transparency
principle, *"justified because showing a Belt that the AI produced gibberish
adds no value and erodes trust."* Everything else in the system is visible and
collaborative.

**B3: on exhaustion the turn degrades and `DMAICGraderMiddleware` is SKIPPED** —
grading a response already known to be incoherent spends a model call for a
meaningless score. The skip is signalled on state, because position 8 runs after
this one and has to be able to read it.

**B4: this cap is its own.** Two here, two on `ModelRetryMiddleware` (§19.4),
three on the validation stack (§34). Three failure modes, three counters, and
merging any two would let a coherence failure consume a gate attempt.

**B5: coherence is NOT a `COACHING_QUALITY_RUBRIC` criterion.** It moved out of
the rubric when this middleware was added; any rubric entry for it is stale.
`test_middleware.py` asserts the rubric carries none.

> **SPEC-GAP (G-09) is OPEN.** `CoherenceResult`'s shape — one verdict or three,
> and what drives the retry — is unstated. See `validation/schemas.py`.
> **SPEC-GAP (G-24):** constructor arguments unstated; `max_retries` below is
> B2's ratified two and nothing else is taken.

> **AI-ACT-REVIEW: uncertain** (S-C13). The silent retry is deliberate, reasoned
> opacity — but it *is* opacity, and whether Art. 13 requires it to be surfaced
> is a judgment the spec pass did not make. Carried, not resolved.
"""
from __future__ import annotations

import logging
from typing import Any, Callable

from langchain.agents.middleware import AgentMiddleware

from backend.core.llm import get_llm
from backend.middleware.skills import CONFIRM, script_step
from backend.validation.schemas import CoherenceResult

logger = logging.getLogger(__name__)

#: B2 — two silent retries, and this cap is not shared with any other (B4).
COHERENCE_MAX_RETRIES = 2

#: **How position 8 learns to stand down (B3), and why it is not state.**
#: Measured against the installed LangChain: a dict returned from one
#: `after_agent` is NOT visible to the next hook in the same pass — the grader
#: read `None` for a key coherence had just written. So the signal is the
#: `degraded` attribute on this instance, which the grader is handed at
#: construction. Both are built per turn in `_build_executor`, so the reference
#: cannot outlive the turn, and nothing reaches `PhaseState` (B7).
#:
#: Kept as a named constant because `test_middleware.py` asserts the state
#: route is NOT used — a future edit that "simplifies" it back to a state write
#: would restore a skip that silently never fires.
SKIP_GRADER_KEY = "coherence_degraded"

_PROMPT = """\
You are checking one coaching turn for basic coherence. This is not a quality
review - you are answering whether the response is a real statement at all.
{step}
Three questions:
  1. Is it conclusive? Does it actually say something, or is it gibberish or a
     vague non-answer that fills space without committing to anything?
  2. Is it parroting? Repeating the Belt's own words back as though they were
     coaching is a FAILURE - the Belt learns nothing from being quoted to
     themselves. Judge this against THE SCRIPT STEP above, when there is one.
  3. Is it on topic for the {phase} phase of a DMAIC project?

Set `coherent` false if any of the three fails, and say specifically which in
`reason` - the coach retries on that feedback, so "try again" is useless.

THE BELT SAID:
{belt}

THE COACH REPLIED:
{coach}
"""

#: The reply's other §50.1 blocks, as the judge is shown them after `message`.
_REPLY_BLOCKS = (
    ("EXPLANATION", "explanation"),
    ("EXAMPLE - an illustration, not the Belt's data", "example"),
    ("QUESTION TO THE BELT", "prompt"),
)

_STEP_CONFIRM = """
THE SCRIPT STEP THIS REPLY PERFORMS: {where}{field} - step 4, CONFIRM.
The Belt has just given a value for this field, and the coaching script has the
coach read it back and check it before moving on:
{block}
Judging question 2 at this step: reading the Belt's words back to confirm them
is not parroting - it is what this step requires. Parroting is ONLY a
restatement of the Belt's words with no confirmation question and nothing added.
The coach's question to the Belt is in the block marked [QUESTION TO THE BELT]
at the end of the reply - read it before answering. If that question asks the
Belt to confirm, correct or complete the value, the reply is NOT parroting.
"""

_STEP_TEACH = """
THE SCRIPT STEP THIS REPLY PERFORMS: {where}{field} - steps 1-3, EXPLAIN, SHOW
and ASK. The coach teaches the field, shows a worked example and asks for the
Belt's version:
{block}
Judging question 2 at this step: parroting is ONLY a restatement of the Belt's
words with no confirmation question and nothing added.
"""


def _step_text(step: dict[str, Any] | None) -> str:
    """G-96 — the step section of the judge's prompt; "" when there is none."""
    if not step:
        return ""
    where = f"position {step['position']} of the script, " if step.get("position") else ""
    field = step.get("field") or "the current field"
    block = step.get("block") or "  (Explain -> Show -> Ask -> Confirm, on every field - §43)"
    template = _STEP_CONFIRM if step.get("step") == CONFIRM else _STEP_TEACH
    return template.format(where=where, field=field, block=block)


class CoherenceMiddleware(AgentMiddleware):
    """Position 7, `after_agent`, immediately before the grader."""

    name = "CoherenceMiddleware"

    def __init__(
        self, phase: str, max_retries: int = COHERENCE_MAX_RETRIES, *,
        focus_field: str | None = None,
        on_verdict: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        super().__init__()
        self.phase = phase
        self.max_retries = max_retries
        #: G-96 — the planner's focus field, for a turn that captures nothing.
        self.focus_field = focus_field
        #: G-96 — each verdict, handed to the node that owns `step_log`; the
        #: grader's `on_evaluation` is the same shape (S-C14 B6).
        self.on_verdict = on_verdict
        #: Per-turn record for the audit trail. Private to the middleware.
        self.attempts = 0
        self.degraded = False
        self.last: CoherenceResult | None = None
        self.step: dict[str, Any] | None = None

    async def aafter_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        """B1-B3. Async, because §1.4 makes the agent loop async."""
        coach_text = self._coach_text(state)
        if not coach_text:
            return None

        belt_text = self._belt_text(state)
        self.attempts = 0
        self.degraded = False
        # G-96 — the script step this reply performs, derived from what it
        # captured; the judge is told it before it is asked "is it parroting?".
        self.step = script_step(self.phase, self._captured(state), self.focus_field)

        # 6.52 B2 — ONE CHECK PER DISTINCT REPLY. The loop that stood here
        # re-checked the SAME `coach_text` up to `max_retries + 1` times: a
        # "silent retry" (§19.7) that asked a temperature-0.1 judge the same
        # question and regenerated nothing — 10 of 10 rejecting turns on
        # IMPR-2026-0E5 show no model call after the rejection. A real retry
        # rewrites the reply first; that is step 6.53, and `max_retries` is
        # held for it. Until then one check decides.
        self.attempts = 1
        result = await self._check(belt_text, coach_text)
        self.last = result
        if result.coherent:
            self._record(result)
            return None
        logger.info(
            "%s.coherence: rejected — %s", self.phase,
            result.reason or "(no reason given)",
        )

        # B3 — degrade, and tell position 8 to stand down. The grader reads
        # `self.degraded` directly; see SKIP_GRADER_KEY.
        self.degraded = True
        self._record(result)
        logger.warning(
            "%s.coherence: reply rejected; degrading the turn and SKIPPING the "
            "grader — grading a response already known to be incoherent spends "
            "a model call for a meaningless score",
            self.phase,
        )
        return None

    def after_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        """Sync entry point. The check is a model call, so there is no
        meaningful synchronous implementation; §1.4 puts the loop on async."""
        return None

    async def _check(self, belt: str, coach: str) -> CoherenceResult:
        """One structured call at the ratified role and temperature (B1).

        Temperature is the role default (§21 puts `coherence` at 0.1) rather
        than passed, for the reason `get_llm` documents: an explicit value
        reads as a deliberate override.
        """
        model = get_llm("coherence").with_structured_output(CoherenceResult)
        prompt = _PROMPT.format(phase=self.phase, step=_step_text(self.step),
                                belt=belt[:2000], coach=coach[:4000])
        return CoherenceResult.model_validate(await model.ainvoke(prompt))

    def _record(self, result: CoherenceResult) -> None:
        """G-96 — every verdict to `step_log`, a rejection with its reason.

        Before this a rejection's reason reached a log line only, so a
        degraded turn was indistinguishable in the record from one the grader
        simply never reached (capability row 13, 2026-09-24 13:14).
        """
        if self.on_verdict is None:
            return
        step = self.step or {}
        self.on_verdict({
            "layer": "coherence",
            **result.model_dump(),
            "degraded": self.degraded,
            # B3 — the grader stands down on exactly this flag.
            "grader_skipped": self.degraded,
            "attempts": self.attempts,
            "script_step": {k: step.get(k) for k in ("position", "field", "step")},
        })

    # ── reading the turn ─────────────────────────────────────────────────

    @staticmethod
    def _response(state: Any) -> Any:
        return (state or {}).get("structured_response") if isinstance(
            state, dict) else getattr(state, "structured_response", None)

    @classmethod
    def _captured(cls, state: Any) -> list[str]:
        """The fields this reply captured — what decides its script step."""
        response = cls._response(state)
        return [str(c.get("field_name") or "") for c in
                (getattr(response, "fields_captured", None) or [])
                if isinstance(c, dict)]

    @classmethod
    def _coach_text(cls, state: Any) -> str:
        """The coaching turn this reply shows the Belt, or "" if there is none.

        **The whole reply, not `message` alone (G-96).** §50.1 splits a turn
        into blocks and the call to action lives in `prompt`: the 13:14 reply
        asked *"Confirm whether this business case fully captures…"* there,
        and a judge reading `message` only saw the read-back without the
        question — which is exactly what parroting looks like.
        """
        response = cls._response(state)
        if response is not None and str(getattr(response, "message", None) or ""):
            parts = [str(response.message)]
            for label, attr in _REPLY_BLOCKS:
                text = str(getattr(response, attr, None) or "").strip()
                if text:
                    parts.append(f"[{label}] {text}")
            return "\n\n".join(parts)
        messages = (state or {}).get("messages") if isinstance(state, dict) else []
        for message in reversed(list(messages or [])):
            if str(getattr(message, "type", "")) == "ai" and str(message.content).strip():
                return str(message.content)
        return ""

    @staticmethod
    def _belt_text(state: Any) -> str:
        """The Belt's most recent message — what "parroting" is judged against."""
        messages = (state or {}).get("messages") if isinstance(state, dict) else []
        for message in reversed(list(messages or [])):
            if str(getattr(message, "type", "")) == "human":
                return str(message.content)
        return ""


__all__ = ["CoherenceMiddleware", "COHERENCE_MAX_RETRIES", "SKIP_GRADER_KEY"]
