"""Define phase gate validator.

ARCHITECTURE.md §35 · §39.1.2 · §39.1.6 · §56.1 · CLAUDE.md §9.2, §9.7.

**One third of an atomic unit** (§56.1): `schema.py` owns the field names and
types, this file owns **which of them block the gate**, and
`skills/dmaic-define-phase/SKILL.md` coaches those exact names in §39.1.2's
order. `DEFINE_REQUIRED_FOR_GATE` is imported from `schema.py` rather than
retyped here — **two hand-maintained copies of one list is precisely how the
three drift apart.**

**Define is the one phase with no Tier 2** (Option A, ratified 2026-08-26;
§39.1.2). **All 12 coached fields block, plus the metric registry — 13 in
total** (§63.8). The "Tier 2 warns only" path of §35 has no
Define members, and `acknowledged_gaps` is therefore always empty for this
phase — nothing is skippable, so nothing can be acknowledged as skipped. The
other four phases keep both tiers, each settled at its own phase review.

This is validation Layer 2b — field presence, **deterministic, no LLM** (§9.2).
Layers 2a, 2c and 2d are elsewhere and are not this function's business.

═══════════════════════════════════════════════════════════════════════
⚠ THE V1 WRITER IS NOT YET MIGRATED — THE V1 DEFINE GATE CANNOT PASS
═══════════════════════════════════════════════════════════════════════

**This validator now requires the §39.1.2 field names. `phases/define/
orchestrate.py` still writes the v1 granular names**, so on the v1 path every
required field reads as missing and the gate never opens.

**That is the ratified rename landing ahead of its writer, not a defect here.**
§39.1.2 retires `what` / `where` / `when` / `who_affected` / `why_it_matters` /
`how_much_baseline` / `how_goal`, `scope_in` / `scope_out`, and the duplicate
`estimated_completion_date` (F-11). Of the 12 required names, **exactly two
match v1** — `goal_statement` and `target_date`. The v2 writer is the executor
node, which captures through `CoachingResponse.fields_captured` into `artifacts`
(§56.1); `orchestrate.py` is v1 and is deleted at procedure step 11.1.

**A v1-to-v2 name shim was considered and rejected.** It would be *adding*
v1-style code, which CLAUDE.md §17 forbids, and it would hide the divergence
at exactly the point where the two vocabularies meet — which is how a rename
half-lands and stays half-landed.

**Owed:** migrate `phases/define/orchestrate.py` (and, with it, the Define
cross-phase briefs that `analyse` / `improve` / `control` orchestrators build
from the v1 names) as part of procedure step 4.1 (WATCH 7). Tracked in
`CONTINUITY.md`.
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

# All 12 coached Define fields BLOCK the gate (§35, §39.1.2 — Option A),
# PLUS `metric_definitions`, the metric registry (§63.8). Thirteen in total.
# The coached walk is still 12 positions — the registry is captured inside
# position 5 rather than at its own — so `field_index` is unaffected.
# Sourced from schema.py: the single declaration.
DEFINE_REQUIRED_FOR_GATE = list(DEFINE_REQUIRED_FOR_GATE_FIELDS)


async def validate_define(state: ImproveGraphState) -> dict:
    """Validator node for the Define phase.

    Gate enforcement is a **completeness check against
    `DEFINE_REQUIRED_FOR_GATE`** — all 13 fields — not a Pydantic
    required-field check, matching the other four phases. `DefineOutput` is the
    gate *document*, assembled once at `gate_apply` after Belt approval (§33);
    it is not the mechanism that decides whether the gate opens.

    Signature and return shape match the LangGraph node contract
    (state -> state slice) so `graph.py` and the HTTP `/gate` route both call
    it unchanged.
    """
    phase_inputs = state.get("phase_inputs") or {}
    data = dict(phase_inputs.get("define") or {})
    attempts = state.get("gate_attempts") or 0

    # ── Layer 2b: presence of all 13 required fields ──────────────────
    # **ONE computation, shared with the prompt** (step 6.3). `gate_registry.
    # missing_gate_fields` is what `BeforeModelStateInjection` also calls, so
    # the coach cannot ask for a field this gate does not want, or stay silent
    # about one it does (§19.1, S-C11 B3). The Tier-1 loop and the structured
    # sub-field checks that used to live in this file are there now.
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
