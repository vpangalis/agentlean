"""Define's visuals, drawn by the program — ADR-0070 (founder, 2026-09-28; C1, C2, R2).

ONE drawing function per visual, `draw`, used by both the coach's reply (a read-back, marked "not
yet confirmed", from the coach's structured values; after Confirm, from the stored values) and the
gate document (`report.define_report`, from the stored values). So the confirmed picture and the
report picture can never differ. No model call draws.

    element 4  problem statement      5W2H mind map        (`problem_5w2h`)
    element 5  baseline               baseline → target    (target still open)
    element 7  goal statement         baseline → target    (target read from the goal's words)
    element 8  target value           baseline → target
    element 12 SIPOC                  SIPOC diagram
"""
from __future__ import annotations

from typing import Any, Optional

from backend.core import diagrams
from backend.phases.define.parse import number_in, parse_limit, unit_of

#: The visual of each read-back field.
VISUAL_OF: dict[str, str] = {
    "problem_statement": "mindmap_5w2h", "baseline_estimate": "baseline_target",
    "goal_statement": "baseline_target", "target_value": "baseline_target",
    "process_map_sipoc": "sipoc",
}
#: Where the reply carries each visual (the UI's keys, `gateway/schemas.py::AskResponse`).
UI_KEY: dict[str, str] = {"sipoc": "sipoc_diagram", "mindmap_5w2h": "visualisation",
                          "baseline_target": "visualisation"}
#: The 5W2H mind map's slots, from the stored `problem_5w2h` keys.
_5W2H_SLOTS = {"what": "what", "where": "where", "when": "when", "who": "who_affected", "why": "why",
               "how_much": "how_much", "how": "how_often"}


def _baseline_target(values: dict[str, Any], field: Optional[str]) -> dict[str, Any]:
    metrics = values.get("metric_definitions") or []
    primary = metrics[0] if metrics and isinstance(metrics[0], dict) else {}
    unit = unit_of(str(primary.get("unit") or ""))
    base = number_in(str(values.get("baseline_estimate") or ""), unit)       # G-132: in the metric's unit
    unit = unit or (base or {}).get("unit", "")
    target = parse_limit(str(values.get("target_value") or "")) if values.get("target_value") else None
    if target is None and field == "goal_statement":
        # The goal's words carry the target: the last figure in the baseline's unit, other than it.
        words = str(values.get("goal_statement") or "")
        import re
        figures = [parse_limit(m.group(0)) for m in re.finditer(r"(?:under|below|less than|at most|unter|höchstens)?\s*\d+(?:[.,]\d+)?\s*(?:%|percent|prozent|[a-z]+)?", words, re.I)]
        candidates = [f for f in figures if f and f["unit"] == unit and (not base or f["number"] != base["number"])]
        target = candidates[-1] if candidates else None
    return diagrams.build_baseline_target(
        metric=str(primary.get("name") or "primary metric"), unit=unit,
        baseline=(base or {}).get("number"), target=(target or {}).get("number"),
        direction=(target or {}).get("direction", "equal"), target_date=_date(values.get("target_date")))


def _date(value: Any) -> Optional[str]:
    """The ISO date in the Belt's words when there is one (G-132), else the words."""
    import re
    text = str(value or "").strip()
    m = re.search(r"\d{4}-\d{2}-\d{2}", text)
    return m.group(0) if m else (text or None)


def draw(kind: str, values: dict[str, Any], *, confirmed: bool,
         field: Optional[str] = None) -> Optional[dict[str, Any]]:
    """THE drawing function for `kind` from `values`, or None when there is nothing to draw."""
    try:
        if kind == "sipoc" and isinstance(values.get("process_map_sipoc"), dict):
            payload = diagrams.build_sipoc(values["process_map_sipoc"], draft=not confirmed)
        elif kind == "mindmap_5w2h" and isinstance(values.get("problem_5w2h"), dict):
            payload = diagrams.build_mindmap_5w2h(
                {slot: values["problem_5w2h"].get(k) for k, slot in _5W2H_SLOTS.items()})
        elif kind == "baseline_target":
            payload = _baseline_target(values, field)
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
                        ("sipoc", "process_map_sipoc")):
        payload = draw(kind, artifacts, confirmed=True, field=field)
        if payload:
            out[kind] = payload
    return out


__all__ = ["VISUAL_OF", "UI_KEY", "draw", "for_field", "report_visuals"]
