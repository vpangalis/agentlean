"""`ContradictionDetectionMiddleware` — position 6 — procedure step 6.5.

Canonical: **§61.1 — S-C10**. Architecture **§19.6**, **§37**, §33; the redesign
record is `docs/DECISIONS.md` §R1.

IT READS A FLAG. IT DETECTS NOTHING.
------------------------------------
Its entire job is turning `CoachingResponse.contradiction_flag` into an
interrupt. **Detection is semantic and is performed by the coach**, in the
model call that already runs every turn (§20) — so there is no additional LLM
call anywhere in this path.

**None of these may be added, ever:** a Store read, a `current_phase` read,
field-name matching, an LLM call, or a tolerance threshold (§37).

WHY THE MECHANICAL VERSION WAS DELETED RATHER THAN FIXED — DECISIONS §R1
------------------------------------------------------------------------
Until 2026-08-22 this middleware did deterministic dict comparison against the
Store. Three verified defects:

1. **It read the wrong drawer.** `store.get(..., current_phase)` — but
   `gate_apply_node` is the only writer and writes at phase *end* (§33.2). Mid
   phase the key does not exist, so it read nothing, every turn, by
   construction.
2. **Of 41 content fields across the five `{Phase}Output` schemas, 38 are
   unique to exactly one phase** — `baseline_estimate` in Define,
   `baseline_mean` in Measure, the same quantity deliberately differently
   named. **93% cannot cross-phase name-match at all.**
3. **The 3 shared names are all prose**, where `!=` fires on any rewording.
   False positives, not detections.

**Repairing (1) leaves 3 prose fields out of 41.** Real contradictions arrive
as natural language referencing prior committed values under different names,
which needs semantic understanding — so this was a redesign, not a fix.

THE INTERRUPT MECHANISM — G-15, ANSWERED BY EXPERIMENT
------------------------------------------------------
§19.6 writes the body as ``raise HITLInterrupt(**flag)``. **`HITLInterrupt` is
not a LangGraph symbol and is defined nowhere**, and G-15 records the open
question: *"whether an exception raised from `after_agent` yields a resumable
graph-level interrupt — as opposed to propagating out of the node and hitting
`error_handler` — is unverified, and the answer determines whether the
contradiction path works at all."*

**Measured against the installed LangGraph, three ways:**

    raise a custom exception  -> propagates OUT. No interrupt. Hits
                                 error_handler (§45). The §19.6 form does not
                                 work.
    interrupt(payload)        -> __interrupt__ populated, Command(resume=...)
                                 continues cleanly. RESUMABLE.
    raise GraphInterrupt(...) -> __interrupt__ populated but resume FAILS —
                                 the payload carries no interrupt id.

So this uses **`interrupt()`**, which is what §33 mandates anyway (*"use
graph-level `interrupt()` + `Command(resume=...)`"*) and what §19.9's ban on
`HumanInTheLoopMiddleware` points at. **`HITLInterrupt` is deliberately NOT
defined**: creating a class whose documented use does not interrupt would be
building a trap. G-15 stays open for the founder to formalise; the evidence is
in `docs/DECISIONS.md` Part AJ.

IT SHIPS INERT, AND THAT IS EXPECTED — WATCH 29
------------------------------------------------
**Nothing sets `contradiction_flag` until step 6.6.** The flag is populated by
the coach following an instruction that lands in the SKILL.md files and the
coach prompt at 6.6 (§32, §37, DECISIONS §R1). Until then this middleware runs
every turn, reads `None`, and does nothing — **by construction, not by
accident.** Same shape as WATCH 7: silence here is the seam, not a bug.
"""
from __future__ import annotations

import logging
from typing import Any

from langchain.agents.middleware import AgentMiddleware
from langgraph.types import interrupt

from backend.core.substate import CONTRADICTION_FLAG_KEYS

logger = logging.getLogger(__name__)


class ContradictionDetectionMiddleware(AgentMiddleware):
    """Position 6, `after_agent`. Flag in, interrupt out.

    **G-24 leaves the constructor unstated**; this one takes nothing, because
    reading a flag off the response needs nothing.
    """

    name = "ContradictionDetectionMiddleware"

    def after_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        flag = self._flag(state)
        if not flag:
            return None
        logger.info(
            "contradiction: %s was approved in %s as %r, Belt now says %r — "
            "interrupting",
            flag.get("prior_field"), flag.get("approved_phase"),
            flag.get("approved_value"), flag.get("proposed_value"),
        )
        # §33's ratified mechanism, and the only one of the three that yields a
        # RESUMABLE interrupt — see the module docstring.
        interrupt(self._payload(flag))
        return None

    async def aafter_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        """Async twin — §1.4 makes the agent loop async, so this is the one
        that fires. `interrupt()` is not a coroutine; it raises."""
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
        if not isinstance(flag, dict):
            logger.warning(
                "contradiction_flag is %s, not a dict — ignoring: %r",
                type(flag).__name__, flag,
            )
            return None
        return flag

    @staticmethod
    def _payload(flag: dict[str, Any]) -> dict[str, Any]:
        """The Belt-facing interrupt payload — §37's five keys, plus the two
        options §37 requires the Belt be offered.

        **Missing keys are reported, not invented.** S-C05 B2 requires all five
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
            # §37: the Belt gets two options and the consequences differ.
            # Choosing to update is what triggers the re-approval cascade
            # (§37) — heavy on purpose, because a cheap reverse gate is a gate
            # the Belt learns to walk through twice.
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
