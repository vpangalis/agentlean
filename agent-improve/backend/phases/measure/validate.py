from __future__ import annotations

import logging

from backend.core.state import ImproveGraphState
from backend.core.config import settings
from backend.phases.measure.schema import MeasurePhaseInput

logger = logging.getLogger(__name__)


# Subset of MEASURE_GATE_FIELDS that MUST be populated for the Measure
# gate to pass. The MeasurePhaseInput schema makes every field optional,
# so gate enforcement is completeness-based rather than Pydantic-required.
MEASURE_REQUIRED_FOR_GATE = [
    "primary_metric_confirmed",
    "secondary_metric_confirmed",
    "data_collection_plan",
    "msa_required",
    "baseline_summary",
    "capability_summary",
]


def validate_measure(state: ImproveGraphState) -> dict:
    """Validator node for Measure phase.

    MeasurePhaseInput fields are all optional at the schema level, so gate
    enforcement is a completeness check against MEASURE_REQUIRED_FOR_GATE
    rather than a Pydantic required-field check. Signature and return shape
    match the LangGraph node contract (state -> state slice) so both
    graph.py and the HTTP /gate route can call this unchanged.

    Pre-populates primary_metric_confirmed and secondary_metric_confirmed
    from Define phase inputs when they have not been confirmed explicitly,
    so the gate does not block on values the team already approved upstream.
    """

    phase_inputs = state.get("phase_inputs") or {}
    inputs = dict(phase_inputs.get("measure") or {})
    attempts = state.get("gate_attempts") or 0

    # Seed metric confirmations from Define if not yet set
    define_inputs = phase_inputs.get("define") or {}
    if not inputs.get("primary_metric_confirmed"):
        pm = define_inputs.get("primary_metric")
        pm_unit = define_inputs.get("primary_metric_unit", "")
        if pm:
            inputs["primary_metric_confirmed"] = (
                f"{pm} ({pm_unit})" if pm_unit else pm
            )

    if not inputs.get("secondary_metric_confirmed"):
        sm = define_inputs.get("secondary_metric")
        if sm:
            inputs["secondary_metric_confirmed"] = sm

    # Completeness check against required fields
    missing = []
    for field in MEASURE_REQUIRED_FOR_GATE:
        val = inputs.get(field)
        if val is None or val == "" or val == []:
            missing.append(field)

    # data_collection_plan needs at least one entry with metric/source/owner
    dcp = inputs.get("data_collection_plan")
    if isinstance(dcp, list):
        valid_entries = [
            e for e in dcp
            if isinstance(e, dict)
            and e.get("metric")
            and e.get("data_source")
            and e.get("data_owner")
        ]
        if not valid_entries and "data_collection_plan" not in missing:
            missing.append("data_collection_plan")

    passed = len(missing) == 0

    if passed:
        # Schema is permissive (all optional). model_dump normalises the
        # shape for downstream storage (write_phase_gate).
        try:
            validated = MeasurePhaseInput(**inputs).model_dump()
        except Exception as e:
            logger.warning("Measure schema dump unexpectedly failed: %s", e)
            validated = inputs
        logger.info("Measure gate PASSED")
        return {
            "gate_attempts": 0,
            "escalated": False,
            "phase_inputs": {
                **phase_inputs,
                "measure": {
                    **inputs,
                    "_gate_passed": True,
                    "_validated": validated,
                },
            },
        }

    new_attempts = attempts + 1
    logger.info(
        "Measure gate FAILED attempt %d/%d — missing: %s",
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
            "measure": {
                **inputs,
                "_gate_passed": False,
                "_missing_fields": missing,
                "_gate_attempts": new_attempts,
            },
        },
    }
