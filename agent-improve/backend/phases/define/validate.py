"""Define phase gate validator.

**One third of an atomic unit**: `schema.py` owns the field names and types,
this file owns **which of them block the gate**, and
`skills/dmaic-define-phase/SKILL.md` coaches those exact names in the same
order. `DEFINE_REQUIRED_FOR_GATE` is imported from `schema.py` rather than
retyped here — **two hand-maintained copies of one list is precisely how the
three drift apart.**

**Define is the one phase with no Tier 2.** **All 13 coached elements block
(R4), plus the three fields captured inside a position.** The "Tier 2 warns
only" path has no Define members, and `acknowledged_gaps` is therefore always
empty for this phase — nothing is skippable, so nothing can be acknowledged as
skipped. The other four phases keep both tiers.

This is validation Layer 2b — field presence, **deterministic, no LLM**.
Layers 2a, 2c and 2d are elsewhere and are not this function's business.

**Only the names `schema.py` declares count.** A value captured under any
other name — the v1 granular names `what` / `where` / `when` /
`who_affected` / `why_it_matters` / `how_much_baseline` / `how_goal`,
`scope_in` / `scope_out`, `estimated_completion_date` (F-11) — leaves the
required field missing and the gate closed. There is no v1-to-v2 name shim:
one would hide the divergence at exactly the point where the two vocabularies
meet, which is how a rename half-lands and stays half-landed.
"""
from __future__ import annotations

import logging

from backend.core.config import settings
from backend.core.state import ImproveGraphState
from backend.phases.define.schema import (
    DEFINE_REQUIRED_FOR_GATE_FIELDS,
    METRIC_DEFINITION_KEYS,
    PROJECT_SCOPE_KEYS,
    SIPOC_KEYS,
    TEAM_MEMBER_KEYS,
)

from backend.phases.gate_registry import missing_gate_fields

logger = logging.getLogger(__name__)

# All 13 coached Define elements BLOCK the gate (R4), PLUS the three fields
# captured inside a position — the CTQs, the 5W2H and the metric registry.
# The count is the schema's; `field_index` walks only the 13.
# Sourced from schema.py: the single declaration.
DEFINE_REQUIRED_FOR_GATE = list(DEFINE_REQUIRED_FOR_GATE_FIELDS)


async def validate_define(state: ImproveGraphState) -> dict:
    """Validator node for the Define phase.

    Gate enforcement is a **completeness check against
    `DEFINE_REQUIRED_FOR_GATE`** — every gate-required field — not a Pydantic
    required-field check, matching the other four phases. `DefineOutput` is the
    gate *document*, assembled once at `gate_apply` after Belt approval; it
    is not the mechanism that decides whether the gate opens.

    Signature and return shape match the LangGraph node contract
    (state -> state slice) so `graph.py` and the HTTP `/gate` route both call
    it unchanged.
    """
    phase_inputs = state.get("phase_inputs") or {}
    data = dict(phase_inputs.get("define") or {})
    attempts = state.get("gate_attempts") or 0

    # ── Layer 2b: presence of every required field ────────────────────
    # **ONE computation, shared with the prompt.** `gate_registry.
    # missing_gate_fields` is what `BeforeModelStateInjection` also calls, so
    # the coach cannot ask for a field this gate does not want, or stay silent
    # about one it does. The Tier-1 loop and the structured sub-field checks
    # live there.
    missing = missing_gate_fields("define", data)

    passed = len(missing) == 0

    if passed:
        logger.info("Define gate PASSED")
        return {
            "gate_attempts": 0,
            "escalated": False,
            "phase_inputs": {
                **phase_inputs,
                "define": {**data, "_gate_passed": True},
            },
        }

    new_attempts = attempts + 1
    logger.info(
        "Define gate FAILED attempt %d/%d — missing: %s",
        new_attempts,
        settings.GATE_MAX_ATTEMPTS,
        missing,
    )
    escalate = new_attempts >= settings.GATE_MAX_ATTEMPTS
    return {
        "gate_attempts": new_attempts,
        "escalated": escalate,
        "phase_inputs": {
            **phase_inputs,
            "define": {
                **data,
                "_gate_passed": False,
                "_missing_fields": missing,
                "_gate_attempts": new_attempts,
            },
        },
    }
