from __future__ import annotations

import logging

from backend.core.state import ImproveGraphState
from backend.core.config import settings
from backend.phases.improve.schema import ImprovePhaseInput

logger = logging.getLogger(__name__)


# Subset of Improve fields that MUST be populated for the gate to pass.
# The ImprovePhaseInput schema makes every field optional, so gate
# enforcement is completeness-based rather than a Pydantic required-field
# check — mirroring the Analyse phase.
IMPROVE_REQUIRED_FOR_GATE = [
    "selected_solution",
    "pilot_result",
    "improvement_confirmed",
]


def validate_improve(state: ImproveGraphState) -> dict:
    """Validator node for Improve phase.

    ImprovePhaseInput fields are all optional at the schema level, so gate
    enforcement is a completeness check against IMPROVE_REQUIRED_FOR_GATE
    rather than a Pydantic required-field check. Signature and return shape
    match the LangGraph node contract (state -> state slice) so both
    graph.py and the HTTP /gate route can call this unchanged.
    """

    phase_inputs = state.get("phase_inputs") or {}
    data = dict(phase_inputs.get("improve") or {})
    attempts = state.get("gate_attempts") or 0

    # ── Completeness check against required fields ────────────────────
    missing = []
    for field in IMPROVE_REQUIRED_FOR_GATE:
        val = data.get(field)
        if val is None or val == "" or val == []:
            missing.append(field)

    # Check 3 — improvement_confirmed value-domain: must be "yes" or
    # "partial" (a bare "no" does not pass the gate). If present but
    # outside the accepted set, treat as incomplete.
    ic = data.get("improvement_confirmed")
    if isinstance(ic, str) and ic.strip().lower() not in ("yes", "partial"):
        if "improvement_confirmed" not in missing:
            missing.append("improvement_confirmed")

    passed = len(missing) == 0

    if passed:
        # Schema is permissive (all optional). model_dump normalises the
        # shape for downstream storage (write_phase_gate).
        try:
            validated = ImprovePhaseInput(**data).model_dump()
        except Exception as e:
            logger.warning("Improve schema dump unexpectedly failed: %s", e)
            validated = data
        logger.info("Improve gate PASSED")
        return {
            "gate_attempts": 0,
            "escalated": False,
            "phase_inputs": {
                **phase_inputs,
                "improve": {
                    **data,
                    "_gate_passed": True,
                    "_validated": validated,
                },
            },
        }

    new_attempts = attempts + 1
    logger.info(
        "Improve gate FAILED attempt %d/%d — missing: %s",
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
            "improve": {
                **data,
                "_gate_passed": False,
                "_missing_fields": missing,
                "_gate_attempts": new_attempts,
            },
        },
    }
