"""Define values read in code, before any model — founder ruling 3, 2026-09-28 (M1 loop package 4).

`parse_limit` (G-120, DEF-032): a target written as a number or as a limit — "under / below /
less than / at most 5%", "unter / weniger als / höchstens / maximal 5 %" — as number, unit and
direction. `metric_value` (ADR-0071, DEF-076): the ONE parser of the baseline and the target —
their Belt's words as a MetricValue {value, unit, direction, is_estimate, raw}. `parse_sipoc` (G-121, DEF-158): the Belt's SIPOC, written with its six labels, as the
six columns `schema.SIPOC_KEYS`; a column without its label is left out, never guessed.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from backend.phases.define.schema import SIPOC_KEYS

#: Words that bound a target from above or below, English and German, longest first.
_BELOW = ("less than", "lower than", "no more than", "not more than", "at most", "under", "below", "up to",
          "weniger als", "niedriger als", "nicht mehr als", "höchstens", "maximal", "unter", "bis zu", "<=", "≤", "<")
_ABOVE = ("more than", "greater than", "no less than", "at least", "over", "above",
          "mehr als", "mindestens", "über", ">=", "≥", ">")
_PERCENT = ("%", "percent", "per cent", "prozent")
_NUMBER = r"(\d+(?:[.,]\d+)?)"
_UNIT = r"\s*(%|per\s?cent|percent|prozent|[A-Za-zÄÖÜäöüß]+)?"


def unit_of(text: str) -> str:
    """A unit as one comparable word: every way of writing a percentage is "%"."""
    t = (text or "").strip().lower()
    if any(p in t for p in _PERCENT):
        return "%"
    return t.split()[0] if t.split() else ""


def parse_limit(text: str) -> Optional[dict[str, Any]]:
    """`{number, unit, direction}` of the first number in `text` ("below", "above" or "equal"),
    or None when there is no number."""
    t = (text or "").lower()
    found = list(re.finditer(_NUMBER + _UNIT, t))
    if not found:
        return None
    # G-135: a bare year ("January to June 2026") is not the figure when another one is there.
    m = next((f for f in found if not _is_year(f)), found[0])
    before = t[:m.start()]
    direction = "equal"
    for words, name in ((_BELOW, "below"), (_ABOVE, "above")):
        if any(re.search(r"(?<![a-zäöüß])" + re.escape(w) + r"\s*$", before.rstrip()) for w in words):
            direction = name
            break
    return {"number": float(m.group(1).replace(",", ".")), "unit": unit_of(m.group(2) or ""),
            "direction": direction}


def _is_year(m: "re.Match[str]") -> bool:
    """G-135 (2026-09-29): a four-digit 1900-2099 with no unit of its own is a year — "January
    to June 2026" — never a baseline or a target. The run-through read "2026" as the baseline
    when the read-back carried no metric unit (IMPR-2026-02C, turn 13)."""
    word = (m.group(2) or "").strip().lower()
    known = word in ("%", "percent", "per cent", "prozent") or word in _UNIT_OF_WORD
    return bool(re.fullmatch(r"(?:19|20)[0-9]{2}", m.group(1))) and not known


def number_in(text: str, unit: str) -> Optional[dict[str, Any]]:
    """The first figure in `text` written in `unit` (as `parse_limit` reads it), else the first
    figure at all. G-132: "paid more than 30 days after … about 23% today" is 23 %, not 30."""
    t = (text or "").lower()
    first = None
    for m in re.finditer(_NUMBER + _UNIT, t):
        if _is_year(m):
            continue                                          # G-135: a year is not the figure
        # The figure itself, with the words before it (digits removed) for its direction.
        prefix = re.sub(r"\d", "", t[max(0, m.start() - 24):m.start()])
        found = parse_limit(prefix + t[m.start():m.end()])
        if found is None:
            continue
        first = first or found
        if found["unit"] == unit:
            return found
    return first


#: The SIPOC labels a Belt writes, English and German, per column.
_SIPOC_LABELS: dict[str, tuple[str, ...]] = {
    "suppliers": ("suppliers", "supplier", "lieferanten", "lieferant"),
    "inputs": ("inputs", "input", "eingaben", "eingangsgrößen"),
    "process_steps": ("process steps", "process", "prozessschritte", "prozess"),
    "outputs": ("outputs", "output", "ergebnisse", "ausgaben"),
    "customers": ("customers", "customer", "kunden", "kunde"),
    "process_metrics": ("process metrics", "metrics", "prozesskennzahlen", "kennzahlen"),
}


def parse_sipoc(text: str) -> dict[str, str]:
    """The columns the Belt labelled ("Suppliers: …. Inputs: …"), keyed by `SIPOC_KEYS`."""
    labels = sorted(((w, k) for k, ws in _SIPOC_LABELS.items() for w in ws), key=lambda x: -len(x[0]))
    pattern = re.compile(r"(?<![A-Za-zÄÖÜäöüß])(" + "|".join(re.escape(w) for w, _ in labels) + r")\s*:", re.I)
    key_of = {w: k for w, k in labels}
    hits = list(pattern.finditer(text or ""))
    out: dict[str, str] = {}
    for i, h in enumerate(hits):
        key = key_of[h.group(1).lower()]
        value = (text[h.end():hits[i + 1].start() if i + 1 < len(hits) else len(text)]).strip().rstrip(".;").strip()
        if value and key not in out:
            out[key] = value
    return {k: out[k] for k in SIPOC_KEYS if k in out}


def missing_columns(value: Any) -> list[str]:
    """The SIPOC columns `value` lacks (all six when it is not a mapping)."""
    if not isinstance(value, dict):
        return list(SIPOC_KEYS)
    return [k for k in SIPOC_KEYS if not str(value.get(k) or "").strip()]


# ══ ADR-0071 (DEF-076): baseline and target as a MetricValue ═════════════════════════════
#
# THE ONE PARSER of `baseline_estimate` and `target_value` (ADR-0071 point 2): the Belt's words
# become `{value, unit, direction, is_estimate, raw}` here and nowhere else — the read-back, the
# chart, the rubric, the migration and the planner's in-code judgment all call it.

#: The fields ADR-0071 stores as a MetricValue.
METRIC_FIELDS: tuple[str, ...] = ("baseline_estimate", "target_value")

#: The normalised units (ADR-0071: "the list is owned by the parser"): every way of writing one
#: unit, English and German, maps to one comparable word. A unit not listed is kept as written.
_UNITS: dict[str, tuple[str, ...]] = {
    "%": ("%", "percent", "per cent", "prozent"),
    "days": ("day", "days", "tag", "tage", "tagen"),
    "hours": ("h", "hr", "hrs", "hour", "hours", "stunde", "stunden"),
    "minutes": ("min", "mins", "minute", "minutes", "minuten"),
    "weeks": ("week", "weeks", "woche", "wochen"),
    "EUR": ("eur", "euro", "euros", "€"),
    "count": ("count", "items", "invoices", "cases", "orders", "stück", "fälle"),
}
_UNIT_OF_WORD = {w: u for u, ws in _UNITS.items() for w in ws}
#: A limit's direction as ADR-0071 writes it.
_DIRECTION = {"below": "<=", "above": ">=", "equal": "="}
#: Words by which the Belt MARKS a Define value as an estimate (R17). Rounding words ("about 23%",
#: "around", "etwa") are not among them: "about 23% today, from the AP ledger" is real data, and
#: reading it as an estimate made the grader fail DEF-R05 on the 2026-09-29 run-through (IMPR-2026-730).
_ESTIMATE = re.compile(
    r"(?<![a-zäöüß])(rough(?:ly)?|estimate[ds]?|estimated|estimation|guess(?:ed|timate)?|"
    r"geschätzt|schätzung|schätzen|grob)(?![a-zäöüß])", re.I)


def normal_unit(unit: str) -> str:
    """One comparable word for a unit ("Prozent" -> "%", "Tage" -> "days"); unknown kept as written."""
    u = unit_of(unit)
    return _UNIT_OF_WORD.get(u, u)


def is_estimate(text: str) -> bool:
    """The Belt marked the figure as an estimate ("about", "roughly", "geschätzt" …)."""
    return bool(_ESTIMATE.search(text or ""))


def metric_value(text: Any, *, target: bool = False, unit: str = "") -> dict[str, Any]:
    """The Belt's words as a MetricValue dict. `unit` is the primary metric's (for a target: the
    baseline's) unit, when known: a baseline takes the first figure written in it (G-132); a
    figure written with no unit takes it. A target is read as a limit (G-120) with its direction.
    No figure: `value` None and `raw` kept — asked again, never guessed."""
    raw = str(text or "").strip()
    hint = normal_unit(unit)
    found = parse_limit(raw) if target else number_in(raw, hint)
    if found is None:
        return {"value": None, "unit": hint, "direction": None, "is_estimate": is_estimate(raw), "raw": raw}
    return {"value": float(found["number"]), "unit": normal_unit(found["unit"]) or hint,
            "direction": _DIRECTION[found["direction"]] if target else None,
            "is_estimate": is_estimate(raw), "raw": raw}


def as_metric(value: Any, *, target: bool = False, unit: str = "") -> dict[str, Any]:
    """A stored value as a MetricValue dict: a MetricValue as it is; text (a proposal, or a value
    from before ADR-0071) through `metric_value`."""
    if isinstance(value, dict) and "raw" in value and "value" in value:
        return dict(value)
    return metric_value(value, target=target, unit=unit)


_WORDS = {"<=": "at most", ">=": "at least", "=": ""}


def metric_text(value: Any) -> str:
    """A MetricValue as the Belt reads it: "at most 5 %", "23 % (an estimate)"; a value that is
    not a number yet says so and shows the Belt's words."""
    mv = as_metric(value)
    if mv["value"] is None:
        return f"not a number yet — {mv['raw']}" if mv["raw"] else "not given"
    figure = f"{mv['value']:g}{'' if mv['unit'] in ('', '%') else ' '}{mv['unit']}".strip()
    words = _WORDS.get(mv.get("direction") or "", "")
    return (f"{words} {figure}".strip() + (" (an estimate)" if mv.get("is_estimate") else ""))


def primary_unit(artifacts: Any) -> str:
    """The primary metric's unit, from the registry (its first entry)."""
    reg = (artifacts or {}).get("metric_definitions") or []
    return normal_unit(str(reg[0].get("unit") or "")) if reg and isinstance(reg[0], dict) else ""


__all__ = ["unit_of", "parse_limit", "number_in", "parse_sipoc", "missing_columns", "METRIC_FIELDS",
           "normal_unit", "is_estimate", "metric_value", "as_metric", "metric_text", "primary_unit"]
