from __future__ import annotations

import logging

from backend.core.state import ImproveGraphState
from backend.core.config import settings
from backend.phases.analyse_phase.schema import AnalysePhaseInput

logger = logging.getLogger(__name__)


# Subset of Analyse fields that MUST be populated for the gate to pass.
# The AnalysePhaseInput schema makes every field optional, so gate
# enforcement is completeness-based rather than a Pydantic required-field
# check — mirroring the Measure phase.
ANALYSE_REQUIRED_FOR_GATE = [
    "possible_causes",
    "vital_few_causes",
    "cause_verified",
    "root_cause_statement",
]


def validate_analyse_phase(state: ImproveGraphState) -> dict:
    """Validator node for Analyse phase.

    AnalysePhaseInput fields are all optional at the schema level, so gate
    enforcement is a completeness check against ANALYSE_REQUIRED_FOR_GATE
    rather than a Pydantic required-field check. Signature and return shape
    match the LangGraph node contract (state -> state slice) so both
    graph.py and the HTTP /gate route can call this unchanged.
    """

    phase_inputs = state.get("phase_inputs") or {}
    data = dict(phase_inputs.get("analyse_phase") or {})
    attempts = state.get("gate_attempts") or 0

    # ── Completeness check against required fields ────────────────────
    missing = []
    for field in ANALYSE_REQUIRED_FOR_GATE:
        val = data.get(field)
        if val is None or val == "" or val == []:
            missing.append(field)

    # Check 1 — possible_causes must have at least 3 items
    causes = data.get("possible_causes")
    if isinstance(causes, list):
        valid_causes = [c for c in causes if isinstance(c, str) and c.strip()]
        if len(valid_causes) < 3 and "possible_causes" not in missing:
            missing.append("possible_causes")
    elif "possible_causes" not in missing:
        # Present but not a list of strings → treat as incomplete
        missing.append("possible_causes")

    passed = len(missing) == 0

    if passed:
        # Schema is permissive (all optional). model_dump normalises the
        # shape for downstream storage (write_phase_gate).
        try:
            validated = AnalysePhaseInput(**data).model_dump()
        except Exception as e:
            logger.warning("Analyse schema dump unexpectedly failed: %s", e)
            validated = data
        logger.info("Analyse gate PASSED")
        return {
            "gate_attempts": 0,
            "escalated": False,
            "phase_inputs": {
                **phase_inputs,
                "analyse_phase": {
                    **data,
                    "_gate_passed": True,
                    "_validated": validated,
                },
            },
        }

    new_attempts = attempts + 1
    logger.info(
        "Analyse gate FAILED attempt %d/%d — missing: %s",
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
            "analyse_phase": {
                **data,
                "_gate_passed": False,
                "_missing_fields": missing,
                "_gate_attempts": new_attempts,
            },
        },
    }
