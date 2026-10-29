"""Define's visuals, drawn by the program — ADR-0070 (C1, C2, R2).

ONE drawing function per visual, `draw`, used by both the coach's reply (a read-back, marked "not
yet confirmed", from the coach's structured values; after Confirm, from the stored values) and the
gate document (`report.define_report`, from the stored values). So the confirmed picture and the
report picture can never differ. No model call draws.

    element 4  problem statement      5W2H mind map        (`problem_5w2h`)
    element 5  baseline               baseline → target    (target still open)
    element 7  goal statement         baseline → target    (target read from the goal's words)
    element 8  target value           baseline → target
    element 10 benefits analysis      benefit timeline     (cost of the gap, saving, when it lands)
    element 12 SIPOC                  SIPOC diagram
"""
from __future__ import annotations

import re
from typing import Any, Optional

from backend.core import diagrams
from backend.phases.define.parse import as_metric, metric_name, parse_limit, primary_unit

#: The visual of each read-back field.
VISUAL_OF: dict[str, str] = {
    "problem_statement": "mindmap_5w2h", "baseline_estimate": "baseline_target",
    "goal_statement": "baseline_target", "target_value": "baseline_target",
    "process_map_sipoc": "sipoc", "benefits_analysis": "benefit_timeline",
}
#: Where the reply carries each visual (the UI's keys, `gateway/schemas.py::AskResponse`).
UI_KEY: dict[str, str] = {"sipoc": "sipoc_diagram", "mindmap_5w2h": "visualisation",
                          "baseline_target": "visualisation", "benefit_timeline": "visualisation"}
#: The 5W2H mind map's slots, from the stored `problem_5w2h` keys.
_5W2H_SLOTS = {"what": "what", "where": "where", "when": "when", "who": "who_affected", "why": "why",
               "how_much": "how_much", "how": "how"}


#: A MetricValue's direction as the chart names it.
_CHART_DIRECTION = {"<=": "below", ">=": "above", "=": "equal", None: "equal"}


def _baseline_target(values: dict[str, Any], field: Optional[str]) -> dict[str, Any]:
    """ADR-0071 (DEF-076): drawn from the MetricValues, never from the raw text."""
    metrics = values.get("metric_definitions") or []
    primary = metrics[0] if metrics and isinstance(metrics[0], dict) else {}
    unit = primary_unit(values)
    b = as_metric(values["baseline_estimate"], unit=unit) if values.get("baseline_estimate") else None
    base = {"number": b["value"], "unit": b["unit"]} if b and b["value"] is not None else None   # G-132
    unit = unit or (base or {}).get("unit", "")
    t = as_metric(values["target_value"], target=True, unit=unit) if values.get("target_value") else None
    target = ({"number": t["value"], "unit": t["unit"], "direction": _CHART_DIRECTION[t["direction"]]}
              if t and t["value"] is not None else None)
    if target is None and field == "goal_statement":
        # The goal's words carry the target: the last figure in the baseline's unit, other than it.
        words = str(values.get("goal_statement") or "")
        import re
        figures = [parse_limit(m.group(0)) for m in re.finditer(r"(?:under|below|less than|at most|unter|höchstens)?\s*\d+(?:[.,]\d+)?\s*(?:%|percent|prozent|[a-z]+)?", words, re.I)]
        candidates = [f for f in figures if f and f["unit"] == unit and (not base or f["number"] != base["number"])]
        target = candidates[-1] if candidates else None
    return diagrams.build_baseline_target(
        metric=metric_name(primary.get("name")) or "primary metric", unit=unit,               # DEF-223: never the id
        baseline=(base or {}).get("number"), target=(target or {}).get("number"),
        direction=(target or {}).get("direction", "equal"), target_date=_date(values.get("target_date")))


def _benefit_timeline(values: dict[str, Any]) -> dict[str, Any]:
    """R5 section 2 (DEF-088): the cost of the gap, the expected saving and when it lands — only the
    figures the benefits analysis and the recorded calculation carry (C1: never a value the text lacks)."""
    b = values["benefits_analysis"]
    rows = [r for r in (values.get("computation_results") or [])
            if isinstance(r, dict) and r.get("tool") == "calculate_expected_savings"]
    from backend.phases.calculations import expected_saving_text
    saving = expected_saving_text(rows[-1]) if rows else None     # G-226: with its currency and separators
    # C2 amended (DEF-291): the two figures as numbers for the bars — each read from the text beside it (C1).
    return {"type": "benefit_timeline", "cost_of_gap": b.get("cost_of_gap"), "impact_type": b.get("impact_type"),
            "expected_saving": saving, "realisation_schedule": b.get("realisation_schedule"),
            "cost_number": _money(b.get("cost_of_gap")), "saving_number": _money(saving)}


#: A sum of money as the Belt or the calculation writes it — "€20,500", "EUR 62,000", "£68,000", "1.5 million" — never
#: a figure stuck to a letter ("Q2 2027"); its thousands separators are commas or spaces.
_MONEY = re.compile(r"(?<![\w.,])(\d{1,3}(?:[, ]\d{3})+|\d+(?:\.\d+)?)(?![\w,])(?:\s*(million|m|thousand|k)(?![a-z]))?",
                    re.I)
_SCALE = {"million": 1e6, "m": 1e6, "thousand": 1e3, "k": 1e3}


def _money(text: Any) -> Optional[float]:
    """The first sum in `text` as a number; None when it has none (C1: a bar is drawn only from a figure the text
    carries). A year is no sum: a text whose only figure is a year, or a quarter's ("Q2 2027"), has none."""
    for m in _MONEY.finditer(str(text or "")):
        number = float(re.sub(r"[, ]", "", m.group(1)))
        if not m.group(2) and 1900 <= number <= 2100 and "," not in m.group(1):
            continue                                         # a year, not an amount
        return number * _SCALE.get((m.group(2) or "").lower(), 1)
    return None


def _date(value: Any) -> Optional[str]:
    """The ISO date in the Belt's words when there is one (G-132; ADR-0088 decision 5: the one parser), else the words."""
    from backend.phases.define.parse import calendar_date
    text = str(value or "").strip()
    found = calendar_date(text)
    return found[0] if found else (text or None)


def _marks(values: dict[str, Any]) -> dict[str, Any]:
    """DEF-211 (ADR-0078's note, point 4): the flow's marks when the problem statement places the
    problem — `located`, the numbers of the steps it is located in (a "from → to" location: every step between its
    ends); `flagged`, the numbers of steps with problem notes outside them. `parse.located_steps` is the matching."""
    from backend.phases.define.parse import located_steps, process_steps
    raw = values.get("problem_5w2h")
    fivew: dict[str, Any] = raw if isinstance(raw, dict) else {}
    where = fivew.get("steps")
    sipoc: dict[str, Any] = values.get("process_map_sipoc") or {}
    if not where:
        return {}
    steps = process_steps(sipoc.get("process_steps"))
    hit = set(located_steps(where, sipoc)["located"])
    flagged = [i + 1 for i, s in enumerate(steps) if s["problems"] and s["id"] not in hit]
    # R-H (founder ruling 2026-10-27): a flagged step shows its problem and who said it.
    notes = {str(n): [" — ".join(x for x in (str(p.get("note") or ""), str(p.get("said_by") or "")) if x)
                      for p in steps[n - 1]["problems"] if isinstance(p, dict)] for n in flagged}
    return {"located": [i + 1 for i, s in enumerate(steps) if s["id"] in hit], "flagged": flagged,
            **({"notes": notes} if notes else {})}


#: DEF-211 (ADR-0070's note): the SIPOC's worked example, a structured file in the skill.
SIPOC_EXAMPLE = "sipoc_example.json"


def teach_example(field: Optional[str]) -> Optional[tuple[str, dict[str, Any]]]:
    """(the reply's UI key, the drawing) of the element's worked example on its teaching turn — the SIPOC's,
    read from the skill's structured file and drawn by the read-back's own builder, marked as an example; None
    for an element without one."""
    if field != "process_map_sipoc":
        return None
    import json
    from backend.middleware.skills import SKILLS_ROOT
    try:
        example = json.loads((SKILLS_ROOT / "dmaic-define-phase" / SIPOC_EXAMPLE).read_text(encoding="utf-8"))
        payload = diagrams.build_sipoc(example, draft=True)
    except (OSError, ValueError, diagrams.DiagramError):
        return None
    return UI_KEY["sipoc"], {**payload, "example": True, "process_metrics": example.get("process_metrics"),
                             "confirmed": False, "label": "an example — not your data"}


def draw(kind: str, values: dict[str, Any], *, confirmed: bool,
         field: Optional[str] = None) -> Optional[dict[str, Any]]:
    """THE drawing function for `kind` from `values`, or None when there is nothing to draw."""
    try:
        if kind == "sipoc" and isinstance(values.get("process_map_sipoc"), dict):
            payload = {**diagrams.build_sipoc(values["process_map_sipoc"], draft=not confirmed),
                       **_marks(values)}
        elif kind == "mindmap_5w2h" and isinstance(values.get("problem_5w2h"), dict):
            payload = diagrams.build_mindmap_5w2h(
                {slot: values["problem_5w2h"].get(k) for k, slot in _5W2H_SLOTS.items()})
        elif kind == "baseline_target":
            payload = _baseline_target(values, field)
        elif kind == "benefit_timeline" and isinstance(values.get("benefits_analysis"), dict):
            payload = _benefit_timeline(values)
        else:
            return None
    except diagrams.DiagramError:
        return None
    return {**payload, "confirmed": confirmed, "label": "confirmed" if confirmed else "not yet confirmed"}


def for_field(field: Optional[str], values: dict[str, Any], *, confirmed: bool) -> Optional[tuple[str, dict[str, Any]]]:
    """(the reply's UI key, the visual) for a read-back or a Confirm of `field`, or None."""
    kind = VISUAL_OF.get(field or "")
    payload = draw(kind, values, confirmed=confirmed, field=field) if kind else None
    return (UI_KEY[kind], payload) if kind and payload else None


def report_visuals(artifacts: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The gate document's visuals, from the stored values — by the same `draw`."""
    out: dict[str, dict[str, Any]] = {}
    for kind, field in (("mindmap_5w2h", "problem_statement"), ("baseline_target", "target_value"),
                        ("sipoc", "process_map_sipoc"), ("benefit_timeline", "benefits_analysis")):
        payload = draw(kind, artifacts, confirmed=True, field=field)
        if payload:
            out[kind] = payload
    return out


__all__ = ["VISUAL_OF", "UI_KEY", "SIPOC_EXAMPLE", "draw", "for_field", "report_visuals", "teach_example"]
