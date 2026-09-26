"""The DEFINE REPORT — requirement R5 (`docs/requirements/define.md`, 2026-09-26).

*"The gate is a readable DEFINE REPORT, not a field checklist: 1 project and
team, 2 business case and benefits, 3 problem, objective, scope with a 5W2H
diagram, 4 VOC and CTQs, 5 metrics (one primary, baseline to target,
secondaries), 6 high-level process with a SIPOC diagram (as-is), 7 issues and
barriers."*

**Assembled from CONFIRMED values only.** Since 6.61 a value reaches `artifacts`
only when the Belt confirms it (the executor stores the plan's `store`, never
what the coach returned), so this reads `artifacts` and nothing a turn merely
proposed. It never reads `CoachingResponse`'s presentational blocks — they are
how one turn was worded, gone by the next. Deterministic, no model call.

The diagrams are DATA here (rows and columns); the gate screen draws them. R6's
history rides along: every element whose confirmed value changed carries its
first and current value, each dated (`substate.value_history`).

Module-level functions only (CLAUDE.md §2).
"""
from __future__ import annotations

from typing import Any

from backend.core.substate import is_empty_capture, value_history
from backend.phases.define.schema import (
    DEFINE_FIELD_ORDER,
    DEFINE_REQUIRED_FOR_GATE_FIELDS,
    FIVE_W_TWO_H_KEYS,
    SIPOC_KEYS,
)

#: The 5W2H diagram's rows: the question each key answers.
FIVE_W_TWO_H_QUESTIONS: dict[str, str] = {
    "what": "What is going wrong?",
    "where": "Where?",
    "when": "When, or since when?",
    "who": "Who is affected?",
    "why": "Why does it matter?",
    "how": "How does it show up?",
    "how_much": "How much?",
}

#: R5's seven sections, in order, and the fields each is assembled from.
REPORT_SECTIONS: tuple[tuple[int, str, tuple[str, ...]], ...] = (
    (1, "Project and team", ("team",)),
    (2, "Business case and benefits", ("business_case", "benefits_analysis")),
    (3, "Problem, objective and scope", ("problem_5w2h", "problem_statement",
                                         "goal_statement", "project_scope")),
    (4, "Voice of the customer and CTQs", ("voc_summary", "critical_to_quality")),
    (5, "Metrics", ("metric_definitions", "baseline_estimate", "target_value",
                    "target_date", "secondary_metrics")),
    (6, "High-level process (as-is)", ("process_map_sipoc",)),
    (7, "Issues and barriers", ("issues_and_barriers",)),
)

#: Which of the thirteen elements each report field belongs to — so a
#: rejection can name the element to go back to (R6).
_ELEMENT_OF: dict[str, str] = {
    "critical_to_quality": "voc_summary",
    "problem_5w2h": "problem_statement",
    "metric_definitions": "baseline_estimate",
}


def element_of(field: str) -> str:
    """The coached element a report field is confirmed under."""
    return _ELEMENT_OF.get(field, field)


def _value(artifacts: dict[str, Any], field: str) -> Any:
    v = artifacts.get(field)
    return None if is_empty_capture(v) else v


def _savings(artifacts: dict[str, Any]) -> dict[str, Any] | None:
    rows = [r for r in (artifacts.get("computation_results") or [])
            if isinstance(r, dict) and r.get("tool") == "calculate_expected_savings"]
    return dict(rows[-1]) if rows else None


def define_report(artifacts: dict[str, Any], case: dict[str, Any] | None = None,
                  field_log: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """The seven-section Define report, from confirmed values.

    `case` is the case framing (title, leader, belt level, department, target
    date); `field_log` the phase's change log. Returns
    `{sections, complete, missing, elements, history}` — `missing` lists every
    gate-required field not yet confirmed, `elements` the thirteen with whether
    each is confirmed (the reject control's choices).
    """
    a = dict(artifacts or {})
    frame = {k: (case or {}).get(k) for k in
             ("case_id", "title", "leader", "belt_level", "department", "target_date")}
    registry = [m for m in (a.get("metric_definitions") or []) if isinstance(m, dict)]
    fivew = _value(a, "problem_5w2h") or {}
    sipoc = _value(a, "process_map_sipoc") or {}

    body: dict[int, dict[str, Any]] = {
        1: {"project": frame, "team": _value(a, "team") or []},
        2: {"business_case": _value(a, "business_case"),
            "benefits": _value(a, "benefits_analysis"),
            "savings": _savings(a)},
        3: {"five_w_two_h": [{"key": k, "question": FIVE_W_TWO_H_QUESTIONS[k],
                              "answer": fivew.get(k) if isinstance(fivew, dict) else None}
                             for k in FIVE_W_TWO_H_KEYS],
            "problem_statement": _value(a, "problem_statement"),
            "objective": _value(a, "goal_statement"),
            "scope": _value(a, "project_scope")},
        4: {"voc_summary": _value(a, "voc_summary"),
            "ctqs": _value(a, "critical_to_quality") or []},
        5: {"primary": registry[0] if registry else None,
            "baseline": _value(a, "baseline_estimate"),
            "target": _value(a, "target_value"),
            "target_date": _value(a, "target_date"),
            "secondary_metrics": _value(a, "secondary_metrics"),
            "other_registered": registry[1:]},
        6: {"sipoc": {k: sipoc.get(k) for k in SIPOC_KEYS} if isinstance(sipoc, dict) else {}},
        7: {"issues_and_barriers": _value(a, "issues_and_barriers")},
    }
    sections = [{"n": n, "title": title, "fields": list(fields),
                 "complete": all(_value(a, f) is not None for f in fields), **body[n]}
                for n, title, fields in REPORT_SECTIONS]
    missing = [f for f in DEFINE_REQUIRED_FOR_GATE_FIELDS if _value(a, f) is None]
    history = {f: h for f, h in value_history(field_log, "define").items() if h["changes"] > 1}
    elements = [{"field": f, "confirmed": not any(element_of(m) == f for m in missing)}
                for f in DEFINE_FIELD_ORDER]
    return {"sections": sections, "complete": not missing, "missing": missing,
            "elements": elements, "history": history}


__all__ = ["FIVE_W_TWO_H_QUESTIONS", "REPORT_SECTIONS", "define_report", "element_of"]
