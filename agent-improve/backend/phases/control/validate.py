from __future__ import annotations

import logging

from backend.core.state import ImproveGraphState
from backend.core.config import settings
from backend.phases.control.schema import ControlPhaseInput

logger = logging.getLogger(__name__)


# Subset of Control fields that MUST be populated for the gate to pass.
# The ControlPhaseInput schema makes every field optional, so gate
# enforcement is completeness-based rather than a Pydantic required-field
# check — mirroring the Improve phase.
CONTROL_REQUIRED_FOR_GATE = [
    "control_plan",
    "monitoring_method",
    "sustainability_confirmed",
]


def validate_control(state: ImproveGraphState) -> dict:
    """Validator node for Control phase.

    ControlPhaseInput fields are all optional at the schema level, so gate
    enforcement is a completeness check against CONTROL_REQUIRED_FOR_GATE
    rather than a Pydantic required-field check. Signature and return shape
    match the LangGraph node contract (state -> state slice) so both
    graph.py and the HTTP /gate route can call this unchanged.
    """

    phase_inputs = state.get("phase_inputs") or {}
    data = dict(phase_inputs.get("control") or {})
    attempts = state.get("gate_attempts") or 0

    # ── Completeness check against required fields ────────────────────
    missing = []
    for field in CONTROL_REQUIRED_FOR_GATE:
        val = data.get(field)
        if val is None or val == "" or val == []:
            missing.append(field)

    # Value-domain check on sustainability_confirmed: the project can only
    # close when the team confirms the improvement will hold — it must be
    # "yes" (a bare "no" does not pass the gate). If present but not "yes",
    # treat as incomplete.
    sc = data.get("sustainability_confirmed")
    if isinstance(sc, str) and sc.strip().lower() != "yes":
        if "sustainability_confirmed" not in missing:
            missing.append("sustainability_confirmed")

    passed = len(missing) == 0

    if passed:
        # Schema is permissive (all optional). model_dump normalises the
        # shape for downstream storage (write_phase_gate).
        try:
            validated = ControlPhaseInput(**data).model_dump()
        except Exception as e:
            logger.warning("Control schema dump unexpectedly failed: %s", e)
            validated = data
        logger.info("Control gate PASSED")
        return {
            "gate_attempts": 0,
            "escalated": False,
            "phase_inputs": {
                **phase_inputs,
                "control": {
                    **data,
                    "_gate_passed": True,
                    "_validated": validated,
                },
            },
        }

    new_attempts = attempts + 1
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
            **phase_inputs,
            "control": {
                **data,
                "_gate_passed": False,
                "_missing_fields": missing,
                "_gate_attempts": new_attempts,
            },
        },
    }
