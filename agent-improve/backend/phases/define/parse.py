"""Define values read in code, before any model — founder ruling 3, 2026-09-28 (M1 loop package 4).

`parse_limit` (G-120, DEF-032): a target written as a number or as a limit — "under / below /
less than / at most 5%", "unter / weniger als / höchstens / maximal 5 %" — as number, unit and
direction. `parse_sipoc` (G-121, DEF-158): the Belt's SIPOC, written with its six labels, as the
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
    m = re.search(_NUMBER + _UNIT, t)
    if not m:
        return None
    before = t[:m.start()]
    direction = "equal"
    for words, name in ((_BELOW, "below"), (_ABOVE, "above")):
        if any(re.search(r"(?<![a-zäöüß])" + re.escape(w) + r"\s*$", before.rstrip()) for w in words):
            direction = name
            break
    return {"number": float(m.group(1).replace(",", ".")), "unit": unit_of(m.group(2) or ""),
            "direction": direction}


def number_in(text: str, unit: str) -> Optional[dict[str, Any]]:
    """The first figure in `text` written in `unit` (as `parse_limit` reads it), else the first
    figure at all. G-132: "paid more than 30 days after … about 23% today" is 23 %, not 30."""
    t = (text or "").lower()
    first = None
    for m in re.finditer(_NUMBER + _UNIT, t):
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


__all__ = ["unit_of", "parse_limit", "number_in", "parse_sipoc", "missing_columns"]
