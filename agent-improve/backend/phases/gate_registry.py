"""One place that knows all five gate documents — procedure step 3.4.

Architecture §40 · §35 (the two tiers) · S-C27–S-C31 · S-F28.

The five `{Phase}Output` schemas, their tier sets and their assembly functions,
keyed by phase. Without this, every caller that needs "the Define document"
re-derives the mapping by hand, and the fifth caller gets it wrong.

Import direction is one-way — registry -> schema -> gate_assembly — so there is
no cycle.
"""
from __future__ import annotations

from typing import Any, Callable, NamedTuple

from pydantic import BaseModel

from backend.phases.analyse.schema import (
    ANALYSE_TIER_1_FIELDS,
    ANALYSE_TIER_2_FIELDS,
    AnalyseOutput,
    assemble_analyse_gate_document,
)
from backend.phases.control.schema import (
    CONTROL_TIER_1_FIELDS,
    CONTROL_TIER_2_FIELDS,
    ControlOutput,
    assemble_control_gate_document,
)
from backend.phases.define.schema import (
    DEFINE_REQUIRED_FOR_GATE_FIELDS,
    DefineOutput,
    assemble_define_gate_document,
)
from backend.phases.improve.schema import (
    IMPROVE_TIER_1_FIELDS,
    IMPROVE_TIER_2_FIELDS,
    ImproveOutput,
    assemble_improve_gate_document,
)
from backend.phases.measure.schema import (
    MEASURE_TIER_1_FIELDS,
    MEASURE_TIER_2_FIELDS,
    MeasureOutput,
    assemble_measure_gate_document,
)


class GateSpec(NamedTuple):
    """What a caller needs to review or assemble one phase's gate document."""

    model: type[BaseModel]
    tier_1: tuple[str, ...]
    tier_2: tuple[str, ...]
    assemble: Callable[..., BaseModel]


#: **Define carries no Tier 2** — Option A (§39.1.2): every field blocks the
#: gate, so there is no `acknowledged_gaps` path out of Define. Its Tier-1 set
#: is therefore the whole 13-field gate-required list, and its Tier-2 set is
#: deliberately empty rather than omitted, so callers can treat all five
#: phases uniformly.
GATE_SPECS: dict[str, GateSpec] = {
    "define": GateSpec(
        DefineOutput, tuple(DEFINE_REQUIRED_FOR_GATE_FIELDS), (),
        assemble_define_gate_document,
    ),
    "measure": GateSpec(
        MeasureOutput, MEASURE_TIER_1_FIELDS, MEASURE_TIER_2_FIELDS,
        assemble_measure_gate_document,
    ),
    "analyse": GateSpec(
        AnalyseOutput, ANALYSE_TIER_1_FIELDS, ANALYSE_TIER_2_FIELDS,
        assemble_analyse_gate_document,
    ),
    "improve": GateSpec(
        ImproveOutput, IMPROVE_TIER_1_FIELDS, IMPROVE_TIER_2_FIELDS,
        assemble_improve_gate_document,
    ),
    "control": GateSpec(
        ControlOutput, CONTROL_TIER_1_FIELDS, CONTROL_TIER_2_FIELDS,
        assemble_control_gate_document,
    ),
}


def tier_of(phase: str, field: str) -> int | None:
    """1, 2, or None for a gate-metadata / `phase_metrics` field."""
    spec = GATE_SPECS[phase]
    if field in spec.tier_1:
        return 1
    if field in spec.tier_2:
        return 2
    return None


def review_rows(phase: str, artifacts: dict[str, Any]) -> list[dict[str, Any]]:
    """One row per content field, tier-labelled, for §50's gate-review screen.

    Ordered Tier 1 then Tier 2 — the order the Belt should read them in, since
    only the first group can block. Gate metadata and `phase_metrics` are not
    rows: they are assembled, not reviewed.
    """
    spec = GATE_SPECS[phase]
    rows: list[dict[str, Any]] = []
    for tier, fields in ((1, spec.tier_1), (2, spec.tier_2)):
        for field in fields:
            value = artifacts.get(field)
            rows.append({
                "field": field,
                "label": field.replace("_", " "),
                "tier": tier,
                "value": value,
                "present": not _is_empty(value),
                "structured": isinstance(value, (dict, list)),
            })
    return rows


def _is_empty(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    return False


__all__ = ["GateSpec", "GATE_SPECS", "tier_of", "review_rows"]
