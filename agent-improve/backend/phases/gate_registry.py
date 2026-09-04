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
    CONTROL_PLAN_KEYS,
    CONTROL_TIER_1_FIELDS,
    CONTROL_TIER_2_FIELDS,
    ControlOutput,
    assemble_control_gate_document,
)
from backend.phases.define.schema import (
    DEFINE_REQUIRED_FOR_GATE_FIELDS,
    METRIC_DEFINITION_KEYS,
    PROJECT_SCOPE_KEYS,
    SIPOC_KEYS,
    TEAM_MEMBER_KEYS,
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
    DETAILED_PROCESS_MAP_KEYS,
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


# ══════════════════════════════════════════════════════════════════════════
# Gate completeness — ONE implementation, two callers (procedure step 6.3)
#
# **§19.1's whole point: the prompt and the gate cannot disagree about what is
# missing.** `BeforeModelStateInjection` reports missing fields to the coach
# every turn (S-C11 B3), and `validate_{phase}` decides whether the gate opens.
# Before 6.3 those were two loops in six files; a divergence in either would
# have shown as a coach confidently asking for a field the gate did not want,
# or staying silent about one it did.
#
# So the loop lives HERE, in the file whose own header says *"without this,
# every caller that needs 'the Define document' re-derives the mapping by hand,
# and the fifth caller gets it wrong."* The five `validate.py` call it, and so
# does the middleware.
#
# **Import direction is unchanged and still one-way** — registry -> schema.
# This module imports no `validate.py`, which is what lets the validators
# import it without a cycle.
# ══════════════════════════════════════════════════════════════════════════

def _absent_keys(container: Any, keys: tuple[str, ...]) -> list[str]:
    """Which of `keys` are missing from one structured dict."""
    return [k for k in keys if _is_empty(container.get(k))]


def _missing_entries(rows: Any, keys: tuple[str, ...], label: str) -> list[str]:
    """Sub-field completeness across a list-of-dicts field (`team`, the registry)."""
    missing: list[str] = []
    if not isinstance(rows, list) or not rows:
        return missing
    for i, entry in enumerate(rows):
        if not isinstance(entry, dict):
            missing.append(f"{label}[{i}]")
            continue
        absent = _absent_keys(entry, keys)
        if absent:
            missing.append(f"{label}[{i}].{'/'.join(absent)}")
    return missing


def missing_structured(phase: str, data: dict[str, Any]) -> list[str]:
    """Sub-field checks for the fields that are not plain strings (§41, S-C33).

    **A dict that is present but half-filled passes a presence check and fails
    the Belt at the gate.** §41 calls this the partial-map failure, and it is
    the reason those fields are dicts rather than prose: a four-of-six SIPOC
    looks complete until someone tries to use it.

    Analyse and Improve have no structured field and return `[]` — stated
    rather than omitted, so all five phases can be called uniformly.
    """
    missing: list[str] = []

    if phase == "define":
        sipoc = data.get("process_map_sipoc")
        if isinstance(sipoc, dict):
            absent = _absent_keys(sipoc, SIPOC_KEYS)
            if absent:
                missing.append(f"process_map_sipoc.{'/'.join(absent)}")
        scope = data.get("project_scope")
        if isinstance(scope, dict):
            absent = _absent_keys(scope, PROJECT_SCOPE_KEYS)
            if absent:
                missing.append(f"project_scope.{'/'.join(absent)}")
        missing.extend(_missing_entries(
            data.get("metric_definitions"), METRIC_DEFINITION_KEYS,
            "metric_definitions"))
        missing.extend(_missing_entries(
            data.get("team"), TEAM_MEMBER_KEYS, "team"))

    elif phase == "measure":
        process_map = data.get("detailed_process_map")
        if isinstance(process_map, dict):
            absent = _absent_keys(process_map, DETAILED_PROCESS_MAP_KEYS)
            if absent:
                missing.append(f"detailed_process_map.{'/'.join(absent)}")

    elif phase == "control":
        plan = data.get("control_plan")
        if isinstance(plan, dict):
            absent = _absent_keys(plan, CONTROL_PLAN_KEYS)
            if absent:
                missing.append(f"control_plan.{'/'.join(absent)}")

    return missing


def missing_gate_fields(phase: str, data: dict[str, Any]) -> list[str]:
    """Which Tier-1 fields block this phase's gate, given what is captured.

    **The one computation.** `validate_{phase}` calls it to decide the gate;
    `BeforeModelStateInjection` calls it to tell the coach what is still owed
    (S-C11 B3). Derived from `data` every time — S-C11 B3 forbids reading a
    stored list, and §5 removed `open_items` for the same reason: a stored
    readiness list is a second source of truth that can disagree with the gate.

    **Tier 2 is deliberately not here.** Only Tier 1 blocks (§35); a Tier-2 gap
    the Belt proceeds past is recorded as `acknowledged_gaps`, not as missing.
    """
    spec = GATE_SPECS[phase]
    missing = [f for f in spec.tier_1 if _is_empty(data.get(f))]
    missing.extend(missing_structured(phase, data))
    return missing


__all__ = [
    "GateSpec",
    "GATE_SPECS",
    "tier_of",
    "review_rows",
    "missing_gate_fields",
    "missing_structured",
]
