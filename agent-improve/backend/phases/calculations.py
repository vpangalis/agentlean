"""Calculations run in code, never by the coach — ADR-0077 (founder, 2026-10-11).

Each calculation belongs to one element. Its inputs come, in order, from the case's confirmed values
(read here, from state) and otherwise from the planner's one judgment call, which extracts from the
Belt's words only the inputs the case does not hold yet (`SufficiencyJudgment.calculation_inputs`).
When every input is present, code runs the tool and records it in `computation_results` with its five
keys (`tool`, `inputs`, `result`, `turn`, `phase`); the read-back carries the figure and one line on
how it was calculated (`how_it_was_calculated`). The coach explains the calculation; it never runs one.

Define has one: the expected savings of the benefits analysis. The other phases add theirs here.

Module-level functions only (CLAUDE.md §2).
"""
from __future__ import annotations

from typing import Any, Optional

#: The inputs the judgment may be asked to extract: name -> how the judgment prompt names it.
ASKED: dict[str, str] = {
    "unit_cost": "the cost of ONE defect or late unit, with its currency (for example '£9')",
    "annual_volume": "how many units go through the process in a year (for example '42,000 invoices')",
}


def _metric_number(artifacts: dict[str, Any], field: str) -> Optional[str]:
    """A confirmed baseline or target as the tool's string input — its number and, for a rate,
    its percent sign (ADR-0071 MetricValue)."""
    v = artifacts.get(field)
    if isinstance(v, dict) and v.get("value") is not None:
        return f"{v['value']}{'%' if v.get('unit') == '%' else ''}"
    return None


def _savings_from_state(artifacts: dict[str, Any]) -> dict[str, str]:
    out = {}
    for name, field in (("baseline_value", "baseline_estimate"), ("target_value", "target_value")):
        n = _metric_number(artifacts, field)
        if n is not None:
            out[name] = n
    return out


#: (phase, element) -> the tool, the inputs read from state, and the inputs asked of the judgment.
CALCULATIONS: dict[tuple[str, str], dict[str, Any]] = {
    ("define", "benefits_analysis"): {
        "tool": "calculate_expected_savings",
        "from_state": _savings_from_state,
        "asked": ("unit_cost", "annual_volume"),
    },
}


def calculation_for(phase: str, field: Optional[str]) -> Optional[dict[str, Any]]:
    return CALCULATIONS.get((phase, field or ""))


def missing_inputs(phase: str, field: Optional[str], artifacts: dict[str, Any]) -> dict[str, str]:
    """The inputs of this element's calculation the case does not hold — what the judgment is asked
    to extract. Empty when the element has no calculation."""
    calc = calculation_for(phase, field)
    if calc is None:
        return {}
    held = calc["from_state"](artifacts)
    return {n: ASKED[n] for n in calc["asked"] if n not in held}


def _tool(name: str) -> Any:
    from backend.knowledge import computation
    return getattr(computation, name)


def run(phase: str, field: Optional[str], artifacts: dict[str, Any],
        extracted: Optional[dict[str, Any]], turn: int) -> Optional[dict[str, Any]]:
    """The calculation's `computation_results` row when every input is present, else None. A row
    with the same tool and inputs as one already recorded is not run again."""
    calc = calculation_for(phase, field)
    if calc is None:
        return None
    inputs = dict(calc["from_state"](artifacts))
    for name in calc["asked"]:
        value = str((extracted or {}).get(name) or "").strip()
        if value and name not in inputs:
            inputs[name] = value
    needed = ("baseline_value", "target_value", *calc["asked"])
    if any(not inputs.get(n) for n in needed):
        return None
    for row in artifacts.get("computation_results") or []:
        if isinstance(row, dict) and row.get("tool") == calc["tool"] and row.get("inputs") == inputs:
            return None
    result = _tool(calc["tool"]).invoke(inputs)
    return {"tool": calc["tool"], "inputs": inputs, "result": result, "turn": turn, "phase": phase}


def latest(artifacts: dict[str, Any], phase: str, field: Optional[str]) -> Optional[dict[str, Any]]:
    """The newest recorded row of this element's calculation."""
    calc = calculation_for(phase, field)
    if calc is None:
        return None
    rows = [r for r in artifacts.get("computation_results") or []
            if isinstance(r, dict) and r.get("tool") == calc["tool"]]
    return rows[-1] if rows else None


def how_it_was_calculated(row: Optional[dict[str, Any]]) -> str:
    """The one line under a read-back (ADR-0077 point 4): the figure and the multiplication with
    the Belt's own numbers, written in code. Empty when nothing was calculated."""
    result = (row or {}).get("result") or {}
    if not isinstance(result, dict) or not result.get("annual_savings"):
        return ""
    from backend.core.prompts import CALCULATION_LINE
    return CALCULATION_LINE.format(figure=result["annual_savings"],
                                   how=str(result.get("calculation_note") or "").split(". Check")[0])


__all__ = ["ASKED", "CALCULATIONS", "calculation_for", "missing_inputs", "run", "latest",
           "how_it_was_calculated"]
