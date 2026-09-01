"""Analyse phase gate validator — Layer 2b.

Architecture 34 (the four-layer validation stack) - 35 (two tiers) -
S-C29 (63.3). Procedure step 3.4.

**One third of an atomic unit** (56.1): `schema.py` owns the field names and
types, this file owns WHICH OF THEM BLOCK THE GATE, and
`skills/dmaic-analyse-phase/SKILL.md` coaches those names in the same order.
The tier tuples are IMPORTED from `schema.py` rather than retyped here —
two hand-maintained copies of one list is how the three drift apart.

**This is Layer 2b — field presence, DETERMINISTIC, no LLM** (9.2). Layer 2a
(coherence) fires every turn in middleware; 2c (constraints) and 2d (the
rubric) run in the same `validation_stack` node but are not this function's
business.

**Two tiers, and the difference is the whole point** (35):

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

from backend.core.config import settings
from backend.core.state import ImproveGraphState
from backend.phases.analyse.schema import (
    ANALYSE_TIER_1_FIELDS,
    ANALYSE_TIER_2_FIELDS,
)

logger = logging.getLogger(__name__)

#: Sourced from `schema.py` — the single declaration (56.1).
ANALYSE_REQUIRED_FOR_GATE = list(ANALYSE_TIER_1_FIELDS)



def _is_empty(value: object) -> bool:
    """Absent, or present-but-empty. A whitespace-only string is empty."""
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    return False


def _missing_structured(data: dict) -> list[str]:
    """Sub-field checks for the structured dicts (41, S-C33).

    **A dict that is present but half-filled passes a presence check and fails
    the Belt at the gate.** 41 calls this the partial-map failure, and it is
    why these fields are dicts rather than prose: a four-of-six map looks
    complete until someone tries to use it. B1 requires EVERY sub-field.
    """
    missing: list[str] = []
    return missing


def acknowledged_gaps(data: dict) -> list[str]:
    """Tier 2 fields the Belt is proceeding without (35, 9.7).

    Recorded rather than dropped: it is what turns a silent omission into a
    conscious decision the audit trail can show, and the next phase's planner
    reads it out of the gate document.
    """
    return [
        f"{field} — Belt accepted gap"
        for field in ANALYSE_TIER_2_FIELDS
        if _is_empty(data.get(field))
    ]


async def validate_analyse(state: ImproveGraphState) -> dict:
    """Validator node for the Analyse phase.

    Gate enforcement is a **completeness check against the Tier 1 set** — not a
    Pydantic required-field check. `AnalyseOutput` is the gate DOCUMENT, assembled
    once at `gate_apply` after Belt approval (33); it is not the mechanism that
    decides whether the gate opens.

    Signature and return shape match the LangGraph node contract
    (state -> state slice), so `graph.py` and the HTTP `/gate` route both call
    it unchanged.
    """
    phase_inputs = state.get("phase_inputs") or {}
    data = dict(phase_inputs.get("analyse") or {})
    attempts = state.get("gate_attempts") or 0

    # -- Layer 2b: presence of every Tier 1 field ----------------------
    missing: list[str] = [
        field for field in ANALYSE_REQUIRED_FOR_GATE if _is_empty(data.get(field))
    ]

    # -- Sub-field completeness for the structured dicts (41) ----------
    missing.extend(_missing_structured(data))

    passed = len(missing) == 0
    gaps = acknowledged_gaps(data)

    if passed:
        logger.info(
            "Analyse gate PASSED — %d acknowledged Tier 2 gap(s): %s",
            len(gaps), gaps,
        )
        return {
            "gate_attempts": 0,
            "escalated": False,
            "phase_inputs": {
                **phase_inputs,
                "analyse": {
                    **data,
                    "_gate_passed": True,
                    "_acknowledged_gaps": gaps,
                },
            },
        }

    new_attempts = attempts + 1
    logger.info(
        "Analyse gate FAILED attempt %d/%d — missing: %s",
        new_attempts, settings.GATE_MAX_ATTEMPTS, missing,
    )
    escalate = new_attempts >= settings.GATE_MAX_ATTEMPTS
    return {
        "gate_attempts": new_attempts,
        "escalated": escalate,
        "phase_inputs": {
            **phase_inputs,
            "analyse": {
                **data,
                "_gate_passed": False,
                "_missing_fields": missing,
                "_gate_attempts": new_attempts,
                "_acknowledged_gaps": gaps,
            },
        },
    }
