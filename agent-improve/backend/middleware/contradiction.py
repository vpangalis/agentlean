"""`ContradictionDetectionMiddleware` — middleware position 6.

IT READS A FLAG. IT DETECTS NOTHING.
------------------------------------
Its entire job is reading `CoachingResponse.contradiction_flag` off the
response. **Detection is semantic and is performed by the coach**, in the
model call that already runs every turn — so there is no additional LLM call
anywhere in this path. A turn with no flag reads `None` and does nothing.

**None of these may be added, ever:** a Store read, a `current_phase` read,
field-name matching, an LLM call, or a tolerance threshold.

WHY DETECTION IS SEMANTIC, NOT A DICT COMPARISON
------------------------------------------------
A mechanical comparison against the Store cannot work:

1. `gate_apply_node` is the only writer of a gate document and writes at phase
   *end*, so mid phase there is nothing stored for the current phase.
2. Nearly every content field across the five `{Phase}Output` schemas is
   unique to one phase — `baseline_estimate` in Define, `baseline_mean` in
   Measure, the same quantity deliberately differently named — so names
   cannot be matched across phases.
3. The few shared names are prose, where `!=` fires on any rewording: false
   positives, not detections.

Real contradictions arrive as natural language referencing prior committed
values under different names, which needs semantic understanding.

THE INTERRUPT MECHANISM — G-15
------------------------------
Against the installed LangGraph:

    raise a custom exception  -> propagates OUT. No interrupt. Hits
                                 error_handler.
    interrupt(payload)        -> __interrupt__ populated, Command(resume=...)
                                 continues cleanly. RESUMABLE.
    raise GraphInterrupt(...) -> __interrupt__ populated but resume FAILS —
                                 the payload carries no interrupt id.

So a pause uses graph-level **`interrupt()`** + `Command(resume=...)`, never
`HumanInTheLoopMiddleware`. **`HITLInterrupt` is deliberately NOT defined**: a
class whose documented use does not interrupt would be a trap.

IT DETECTS; IT NEVER PAUSES — ADR-0112
--------------------------------------
**Detection runs every turn and the flag reaches the response.** There is no
pause (founder ruling 2026-10-27, ADR-0112; DEF-040's pause node is dropped):
the executor tells the Belt in the reply, in code, what the answer conflicts
with and offers the choice to correct or keep it (`state_injection.
mismatch_line`); a kept answer is recorded, dated, and the conversation moves on.
"""
from __future__ import annotations

import logging
from typing import Any

from langchain.agents.middleware import AgentMiddleware

from backend.core.substate import CONTRADICTION_FLAG_KEYS

logger = logging.getLogger(__name__)


class ContradictionDetectionMiddleware(AgentMiddleware):
    """Position 6, `after_agent`. Flag in, logged; the Belt is told in the reply (ADR-0112).

    **G-24 leaves the constructor unstated**; this one takes nothing, because
    reading a flag off the response needs nothing.
    """

    name = "ContradictionDetectionMiddleware"

    def after_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        flag = self._flag(state)
        if not flag:
            return None
        logger.info(
            "contradiction: %s was approved in %s as %r, Belt now says %r",
            flag.get("prior_field"), flag.get("approved_phase"),
            flag.get("approved_value"), flag.get("proposed_value"),
        )
        # ADR-0112: no pause — the executor tells the Belt in the reply and offers correct or keep.
        logger.warning(
            "%s: mismatch DETECTED — told in the reply (ADR-0112). Field %r, "
            "confirmed %r in %s, Belt now says %r",
            self.name, flag.get("prior_field"), flag.get("approved_value"),
            flag.get("approved_phase"), flag.get("proposed_value"),
        )
        return None

    async def aafter_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        """Async twin — the agent loop is async, so this is the one that
        fires."""
        return self.after_agent(state, runtime)

    # ── reading the flag ─────────────────────────────────────────────────

    @staticmethod
    def _flag(state: Any) -> dict[str, Any] | None:
        """`structured_response.contradiction_flag`, or None.

        **Tolerant of the response being absent, not of it being malformed.**
        A turn that produced no structured response is a turn with nothing to
        check; a flag that is present but not a dict is a coach error worth
        seeing, so it is logged rather than silently dropped.
        """
        response = (state or {}).get("structured_response") if isinstance(
            state, dict) else getattr(state, "structured_response", None)
        if response is None:
            return None
        flag = getattr(response, "contradiction_flag", None)
        if flag is None:
            return None
        if hasattr(flag, "model_dump"):   # G-252: the typed flag
            flag = flag.model_dump()
        if not isinstance(flag, dict):
            logger.warning(
                "contradiction_flag is %s, not a dict — ignoring: %r",
                type(flag).__name__, flag,
            )
            return None
        return flag

    @staticmethod
    def _payload(flag: dict[str, Any]) -> dict[str, Any]:
        """The Belt-facing interrupt payload — the flag's five keys, plus the
        two options the Belt must be offered.

        **Missing keys are reported, not invented.** All five are required
        when the flag is set; a flag short of one is a coach error, and filling
        it in here would hide that behind a plausible-looking interrupt.
        """
        missing = [k for k in CONTRADICTION_FLAG_KEYS if not flag.get(k)]
        if missing:
            logger.warning(
                "contradiction_flag is missing %s — the interrupt will show "
                "them as unknown (S-C05 B2 requires all five)", missing,
            )
        return {
            "kind": "contradiction",
            **{k: flag.get(k) for k in CONTRADICTION_FLAG_KEYS},
            "missing_keys": missing,
            # The Belt gets two options and the consequences differ.
            # Choosing to update is what triggers the re-approval cascade —
            # heavy on purpose, because a cheap reverse gate is a gate the
            # Belt learns to walk through twice.
            "options": [
                {"id": "update_approved_value",
                 "consequence": "The approved value changes. That phase's gate "
                                "document and every phase after it become "
                                "provisional and need re-review."},
                {"id": "keep_approved_value",
                 "consequence": "The approved value stands. You are clarifying "
                                "that you misspoke; nothing changes."},
            ],
        }


__all__ = ["ContradictionDetectionMiddleware"]
