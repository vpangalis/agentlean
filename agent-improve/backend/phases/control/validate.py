from __future__ import annotations

import logging

from pydantic import ValidationError

from backend.core.state import ImproveGraphState
from backend.core.config import settings
from backend.phases.control.schema import ControlPhaseInput

logger = logging.getLogger(__name__)


def validate_control(state: ImproveGraphState) -> dict:
    """Validator node for Control phase.
    Attempts to instantiate ControlPhaseInput from phase_inputs['control'].
    Returns gate result as dict slice for graph routing."""

    inputs = (state.get("phase_inputs") or {}).get("control") or {}
    attempts = state.get("gate_attempts") or 0

    try:
        validated = ControlPhaseInput(**inputs)
        logger.info("Control gate PASSED")
        return {
            "gate_attempts": 0,          # reset on pass
            "escalated": False,
            # Signal for graph: store validated dict in phase_inputs
            "phase_inputs": {
                **(state.get("phase_inputs") or {}),
                "control": {
                    **inputs,
                    "_gate_passed": True,
                    "_validated": validated.model_dump(),
                },
            },
        }
    except ValidationError as e:
        new_attempts = attempts + 1
        missing = _extract_missing_fields(e)
        logger.info(
            "Control gate FAILED attempt %d/%d — missing: %s",
            new_attempts,
            settings.GATE_MAX_ATTEMPTS,
            missing,
        )
        escalate = new_attempts >= settings.GATE_MAX_ATTEMPTS
        return {
            "gate_attempts": new_attempts,
            "escalated": escalate,
            "phase_inputs": {
                **(state.get("phase_inputs") or {}),
                "control": {
                    **inputs,
                    "_gate_passed": False,
                    "_missing_fields": missing,
                    "_gate_attempts": new_attempts,
                },
            },
        }


def _extract_missing_fields(error: ValidationError) -> list[str]:
    """Extract plain field names from ValidationError."""
    fields = []
    for err in error.errors():
        loc = err.get("loc", ())
        if loc:
            fields.append(" → ".join(str(l) for l in loc))
    return fields
