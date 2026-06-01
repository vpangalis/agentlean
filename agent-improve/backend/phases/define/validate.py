from __future__ import annotations

import logging

from pydantic import ValidationError

from backend.core.state import ImproveGraphState
from backend.core.config import settings
from backend.phases.define.schema import DefinePhaseInput

logger = logging.getLogger(__name__)


def validate_define(state: ImproveGraphState) -> dict:
    """Validator node for Define phase.
    Attempts to instantiate DefinePhaseInput from phase_inputs['define'].
    Returns gate result as dict slice for graph routing."""

    inputs = (state.get("phase_inputs") or {}).get("define") or {}

    # Apply case metadata fallbacks for fields set at case creation
    # but not extracted into structured from the conversation.
    case_meta = state.get("case_metadata") or {}
    if not inputs.get("belt_level"):
        case_belt = case_meta.get("belt_level") or ""
        if case_belt:
            inputs = {**inputs, "belt_level": case_belt}
    if not inputs.get("process_owner"):
        case_leader = case_meta.get("leader") or ""
        if case_leader:
            inputs = {**inputs, "process_owner": case_leader}

    attempts = state.get("gate_attempts") or 0

    try:
        validated = DefinePhaseInput(**inputs)
        logger.info("Define gate PASSED")
        return {
            "gate_attempts": 0,          # reset on pass
            "escalated": False,
            # Signal for graph: store validated dict in phase_inputs
            "phase_inputs": {
                **(state.get("phase_inputs") or {}),
                "define": {
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
                **(state.get("phase_inputs") or {}),
                "define": {
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
