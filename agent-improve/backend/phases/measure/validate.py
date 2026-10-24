"""Measure phase gate validator — Layer 2b.

**One third of an atomic unit**: `schema.py` owns the field names and
types, this file owns WHICH OF THEM BLOCK THE GATE, and
`skills/dmaic-measure-phase/SKILL.md` coaches those names in the same order.
The tier tuples are IMPORTED from `schema.py` rather than retyped here —
two hand-maintained copies of one list is how the three drift apart.

**This is Layer 2b — field presence, DETERMINISTIC, no LLM.** Layer 2a
(coherence) is retired (ADR-0083); 2c (constraints) and 2d (the
rubric) run in the same `validation_stack` node but are not this function's
business.

**Two tiers, and the difference is the whole point:**

| Tier | This validator | The grader (2d) | The Belt |
|---|---|---|---|
| Tier 1 | **BLOCKS** | can `fail` | must supply it |
| Tier 2 | not checked | at worst `warning` | supplies it, or proceeds with an acknowledged gap |

A gate MAY pass with warnings. A gate may NEVER pass with failures. A Tier 2
field the Belt proceeds past is recorded in `acknowledged_gaps` — never
silently dropped — and the next phase's input mapper carries it forward
(G-27 ruling) so a deliberate decision stays distinguishable from an oversight.

**Why two tiers at all.** A gate that blocks on every criterion teaches Belts
to fill fields mechanically: complete gate documents, worse projects. Tier 1
catches genuinely incomplete phases; Tier 2 coaches toward best practice while
leaving the judgment with the Belt, who knows the project.
"""
from __future__ import annotations

import logging

from backend.core.substate import is_empty_capture
from backend.core.config import settings
from backend.core.state import ImproveGraphState
from backend.phases.measure.schema import (
    MEASURE_TIER_1_FIELDS,
    MEASURE_TIER_2_FIELDS,
)

from backend.phases.gate_registry import missing_gate_fields

logger = logging.getLogger(__name__)

#: Sourced from `schema.py` — the single declaration.
MEASURE_REQUIRED_FOR_GATE = list(MEASURE_TIER_1_FIELDS)


def acknowledged_gaps(data: dict) -> list[str]:
    """Tier 2 fields the Belt is proceeding without.

    Recorded rather than dropped: it is what turns a silent omission into a
    conscious decision the audit trail can show, and the next phase's planner
    reads it out of the gate document.
    """
    return [
        f"{field} — Belt accepted gap"
        for field in MEASURE_TIER_2_FIELDS
        if is_empty_capture(data.get(field))
    ]


async def validate_measure(state: ImproveGraphState) -> dict:
    """Validator node for the Measure phase.

    Gate enforcement is a **completeness check against the Tier 1 set** — not a
    Pydantic required-field check. `MeasureOutput` is the gate DOCUMENT, assembled
    once at `gate_apply` after Belt approval; it is not the mechanism that
    decides whether the gate opens.

    Signature and return shape match the LangGraph node contract
    (state -> state slice), so `graph.py` and the HTTP `/gate` route both call
    it unchanged.
    """
    phase_inputs = state.get("phase_inputs") or {}
    data = dict(phase_inputs.get("measure") or {})
    attempts = state.get("gate_attempts") or 0

    # -- Layer 2b: presence of every Tier 1 field ----------------------
    # **ONE computation, shared with the prompt.** `gate_registry.
    # missing_gate_fields` is what `BeforeModelStateInjection` also calls, so
    # the coach cannot ask for a field this gate does not want, or stay silent
    # about one it does. The Tier-1 loop and the structured sub-field checks
    # live there.
    missing = missing_gate_fields("measure", data)

    passed = len(missing) == 0
    gaps = acknowledged_gaps(data)

    if passed:
        logger.info(
            "Measure gate PASSED — %d acknowledged Tier 2 gap(s): %s",
            len(gaps), gaps,
        )
        return {
            "gate_attempts": 0,
            "escalated": False,
            "phase_inputs": {
                **phase_inputs,
                "measure": {
                    **data,
                    "_gate_passed": True,
                    "_acknowledged_gaps": gaps,
                },
            },
        }

    new_attempts = attempts + 1
    logger.info(
        "Measure gate FAILED attempt %d/%d — missing: %s",
        new_attempts, settings.GATE_MAX_ATTEMPTS, missing,
    )
    escalate = new_attempts >= settings.GATE_MAX_ATTEMPTS
    return {
        "gate_attempts": new_attempts,
        "escalated": escalate,
        "phase_inputs": {
            **phase_inputs,
            "measure": {
                **data,
                "_gate_passed": False,
                "_missing_fields": missing,
                "_gate_attempts": new_attempts,
                "_acknowledged_gaps": gaps,
            },
        },
    }
