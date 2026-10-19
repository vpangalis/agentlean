"""Element templates — ADR-0093 "Element templates and the Gate view" (founder, 2026-10-19).

Each Define element is shown as its acceptance criteria, one row each, with the value that goes into the Gate
and where it came from: the read-back card (before a Confirm, from the exact value a Confirm will store) and the
Gate's element card (after it, from the stored value) are drawn from the SAME rows, built here.

- The criteria are the script's own (`acceptance_criteria`, R7), in its order; a template adds no criterion and
  no wording to any prompt — only a short label and where the row's value is read from.
- Structured values are read in code (the ADR-0088 parsers). Free text is read from the judgment's quoted span
  per criterion (`SufficiencyJudgment.criterion_spans`, option (b)); a span counts only when it is a verbatim
  substring of the Belt's answer (`verbatim_spans`) — otherwise the row shows no value of its own and the whole
  answer is shown once, marked "in your answer".
- A row is met by its code check where the template has one (the same checks a Confirm is refused on: ADR-0088's
  parts, a number, a date, the SIPOC's columns, both scope halves); otherwise by the judgment's verdict.

Pure functions, no model call, nothing stored: the rows are a view of the stored value (ADR-0093 "Rejected").
Module-level functions only (CLAUDE.md §2).
"""
from __future__ import annotations

import re
from typing import Any, Callable, Optional

from backend.core.substate import is_empty_capture
from backend.phases.define import parse
from backend.phases.define.report import REPORT_SECTIONS
from backend.phases.define.schema import DEFINE_FIELD_ORDER, DEFINE_POSITIONS

#: The sources a row's value can come from (ADR-0093 decision 2).
YOUR_ANSWER, FROM_FILE, CALCULATED, IN_ANSWER = "your answer", "from your file", "calculated", "in your answer"

#: The Gate's section letters, R5's seven in order (gate_view_mockup.html).
SECTION_LETTERS: tuple[str, ...] = ("A", "B", "C", "D", "E", "F", "G")

#: A row's value: text, a list of items, or a table {"columns": [...], "rows": [[...]]}; None when there is none.
Value = Any
#: (value, met) — `met` is the code check's answer, or None when the criterion is the judgment's to meet.
Read = tuple[Value, Optional[bool]]


def _text(v: Any) -> str:
    if isinstance(v, dict):
        return " ".join(_text(x) for x in v.values())
    if isinstance(v, list):
        return " ".join(_text(x) for x in v)
    return str(v or "").strip()


def _team(values: dict[str, Any]) -> list[dict[str, Any]]:
    return [m for m in values.get("team") or [] if isinstance(m, dict)]


def _named(values: dict[str, Any], pattern: Any) -> Read:
    names = [str(m.get("name") or "").strip() for m in _team(values) if pattern.search(_text(m))]
    names = [n for n in names if n]
    return ("; ".join(names) or None), bool(names) if _team(values) else False


def _people(values: dict[str, Any]) -> Read:
    rows = [[str(m.get(k) or "—") for k in ("name", "role", "function")] for m in _team(values)]
    return ({"columns": ["Name", "Role", "Function"], "rows": rows} if rows else None), None


def _training(values: dict[str, Any]) -> Read:
    said = []
    for m in _team(values):
        hit = next((str(v) for k, v in m.items() if k not in ("name", "role", "function")
                    and parse._TRAINING.search(str(v or ""))), None)
        if hit is None:
            # Training stated inside the name, role or function: the clause that states it, not the whole entry.
            hit = next((c.strip() for c in re.split(r"[;,.]", _text(m)) if parse._TRAINING.search(c)), None)
        if hit:
            said.append(f"{m.get('name') or m.get('role') or '—'}: {hit}")
    return ("; ".join(said) or None), not parse.missing_parts("team", _team(values)) or bool(said)


def _ctqs(values: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for r in values.get("critical_to_quality") or [] if isinstance(r, dict)]


def _ctq_part(key: str, part: str) -> Callable[[dict[str, Any]], Read]:
    def read(values: dict[str, Any]) -> Read:
        rows = _ctqs(values)
        seen: list[str] = []
        for r in rows:
            v = str(r.get(key) or "").strip()
            if v and v not in seen:
                seen.append(v)
        return ("; ".join(seen) or None), (part not in " ".join(parse.missing_parts("critical_to_quality", rows))
                                           if rows else None)
    return read


def _ctq_table(values: dict[str, Any]) -> Read:
    rows = _ctqs(values)
    table = [[str(r.get(k) or "—") for k in ("customer", "need", "requirement")] for r in rows]
    met = not any("measurable" in p for p in parse.missing_parts("critical_to_quality", rows)) if rows else None
    return ({"columns": ["Customer", "Need", "CTQ (measurable)"], "rows": table} if table else None), met


def _fivew(values: dict[str, Any]) -> dict[str, Any]:
    v = values.get("problem_5w2h")
    return v if isinstance(v, dict) else {}


def _fivew_key(key: str) -> Callable[[dict[str, Any]], Read]:
    def read(values: dict[str, Any]) -> Read:
        return (str(_fivew(values).get(key) or "").strip() or None), None
    return read


def _fivew_table(values: dict[str, Any]) -> Read:
    from backend.phases.define.report import FIVE_W_TWO_H_QUESTIONS
    fw = _fivew(values)
    if not fw:
        return None, None
    rows = [[question, str(fw.get(k) or "—")] for k, question in FIVE_W_TWO_H_QUESTIONS.items()]
    return {"columns": ["5W2H", "Answer"], "rows": rows}, not parse.missing_parts("problem_5w2h", fw)


def _primary(values: dict[str, Any]) -> dict[str, Any]:
    reg = [m for m in values.get("metric_definitions") or [] if isinstance(m, dict)]
    return reg[0] if reg else {}


def _primary_name(values: dict[str, Any]) -> Read:
    return (str(_primary(values).get("name") or "").strip() or None), None


def _defined(values: dict[str, Any]) -> Read:
    p = _primary(values)
    parts = [str(p.get(k) or "").strip() for k in ("name", "unit", "meaning")]
    return (" · ".join(x for x in parts if x) or None), None


def _metric(field: str) -> Callable[[dict[str, Any]], Read]:
    def read(values: dict[str, Any]) -> Read:
        v = values.get(field)
        if is_empty_capture(v):
            return None, False
        mv = parse.as_metric(v, target=field == "target_value")
        return parse.metric_text(mv), mv["value"] is not None
    return read


def _direction(values: dict[str, Any]) -> Read:
    base, target = values.get("baseline_estimate"), values.get("target_value")
    if is_empty_capture(base) or is_empty_capture(target):
        return None, None
    return f"from {parse.metric_text(base)} to {parse.metric_text(target)}", None


def _date(values: dict[str, Any]) -> Read:
    v = values.get("target_date")
    if is_empty_capture(v):
        return None, False
    return parse.date_shown(v), parse.calendar_date(v) is not None


def _scope(values: dict[str, Any]) -> Read:
    s = values.get("project_scope")
    if not isinstance(s, dict):
        return None, None
    inside, outside = _text(s.get("in_scope")), _text(s.get("out_scope"))
    rows = [[label, text or "—"] for label, text in (("In scope", inside), ("Out of scope", outside))]
    return {"columns": ["", ""], "rows": rows}, bool(inside and outside)


def _benefit(key: str) -> Callable[[dict[str, Any]], Read]:
    def read(values: dict[str, Any]) -> Read:
        b = values.get("benefits_analysis")
        return (_text(b.get(key)) or None) if isinstance(b, dict) else None, None
    return read


def _items(field: str, label: str) -> Callable[[dict[str, Any]], Read]:
    def read(values: dict[str, Any]) -> Read:
        items = parse.list_items(values.get(field), label)
        return (items or None), None
    return read


def _sipoc(values: dict[str, Any]) -> dict[str, Any]:
    v = values.get("process_map_sipoc")
    return v if isinstance(v, dict) else {}


def _start_to_end(values: dict[str, Any]) -> Read:
    names = parse.step_names(_sipoc(values))
    if not names:
        return None, None
    return (f"1 step: {names[0]}" if len(names) == 1
            else f"{len(names)} steps: {names[0]} → {names[-1]}"), None


def _all_six(values: dict[str, Any]) -> Read:
    s = _sipoc(values)
    if not s:
        return None, False
    gone = parse.missing_columns(s)
    return ("all six filled" if not gone else "missing: " + ", ".join(c.replace("_", " ") for c in gone)), not gone


def _performance(values: dict[str, Any]) -> Read:
    s = _sipoc(values)
    steps = parse.process_steps(s.get("process_steps"))
    if not steps:
        return None, None

    def text(v: Any) -> str:
        return parse.metric_text(v) if isinstance(v, dict) else "—"
    rows = []
    for st in steps:
        d = st.get("duration") or {}
        rng = " – ".join(text(d[k]) for k in ("min", "max") if d.get(k))
        rows.append([str(st["name"]), (text(d["avg"]) if d.get("avg") else "—") + (f" ({rng})" if rng else ""),
                     text(st.get("runs_per_period")) if st.get("runs_per_period") else "—"])
    raw_perf = s.get("process_performance")
    perf: dict[str, Any] = raw_perf if isinstance(raw_perf, dict) else {}
    if perf.get("lead_time") or perf.get("runs_per_period"):
        rows.append(["Whole process", text(perf.get("lead_time")) if perf.get("lead_time") else "—",
                     text(perf.get("runs_per_period")) if perf.get("runs_per_period") else "—"])
    return {"columns": ["Step", "Time · average (range)", "How often"], "rows": rows}, None


def _stated(statement: str) -> Callable[[dict[str, Any]], Read]:
    """A criterion that is a check on the answer as a whole (no cause named, as-is): what it states, met by the
    judgment."""
    def read(values: dict[str, Any]) -> Read:
        return statement, None
    return read


def _span() -> Callable[[dict[str, Any]], Read]:
    """Free text: the row's value is the judgment's quoted span (option (b)), read by `rows`."""
    def read(values: dict[str, Any]) -> Read:
        return None, None
    return read


#: element -> criterion id -> (label, how its value is read). The ids are the script's; `rows` drops a template
#: entry the script no longer lists and shows a script criterion the template does not know as free text.
TEMPLATES: dict[str, dict[str, tuple[str, Callable[[dict[str, Any]], Read]]]] = {
    "business_case": {
        "what": ("What is wrong", _span()),
        "where-when": ("Where and since when", _span()),
        "baseline": ("How big it is today", _span()),
        "cost": ("What it costs", _span()),
        "no-cause-no-fix": ("No cause and no fix", _stated("No cause and no solution named")),
    },
    "team": {
        "champion": ("Champion (sponsor)", lambda v: _named(v, parse._CHAMPION)),
        "process-owner": ("Process owner", lambda v: _named(v, parse._OWNER)),
        "people": ("Each person: name, role, function", _people),
        "training": ("Training needed", _training),
    },
    "voc_summary": {
        "customers": ("Customers", _ctq_part("customer", "customer")),
        "needs": ("Their needs", _ctq_part("need", "need")),
        "ctq": ("CTQs (measurable)", _ctq_table),
    },
    "problem_statement": {
        "defect": ("The defect", _fivew_key("what")),
        "5w2h": ("The seven 5W2H answers", _fivew_table),
        "magnitude": ("How big", _fivew_key("how_much")),
        "no-cause-no-fix": ("No cause, no fix, no blame", _stated("No cause, no solution and no one to blame named")),
        "located": ("Where in the process", _fivew_key("where")),
    },
    "baseline_estimate": {
        "one-primary": ("Primary metric", _primary_name),
        "quantified": ("Baseline", _metric("baseline_estimate")),
        "kpi-link": ("Business measure it feeds", _span()),
        "real-data": ("Where the figure comes from", _span()),
        "defined": ("Name · unit · meaning", _defined),
    },
    "project_scope": {
        "in-and-out": ("In and out of scope", _scope),
        "start-end": ("Start and end point", _span()),
        "not-too-broad": ("One process or area", _stated("One process or area, not everything around it")),
    },
    "goal_statement": {
        "same-metric": ("Same metric as the problem", _span()),
        "how-much": ("How much improvement", _span()),
        "by-when": ("By when", _span()),
    },
    "target_value": {
        "number-and-unit": ("Target", _metric("target_value")),
        "direction": ("From the baseline to the target", _direction),
    },
    "target_date": {
        "a-date": ("Target date", _date),
    },
    "benefits_analysis": {
        "cost-of-gap": ("Cost of the gap", _benefit("cost_of_gap")),
        "impact-type": ("Sustainable or one-off", _benefit("impact_type")),
        "realisation": ("Realisation schedule", _benefit("realisation_schedule")),
        "finance-contact": ("Finance contact", _benefit("finance_contact")),
    },
    "secondary_metrics": {
        "side-effect": ("Side effects watched", _items("secondary_metrics", "Secondary metrics")),
        "not-the-primary": ("Not the primary metric", _stated("Not the primary metric")),
    },
    "process_map_sipoc": {
        "as-is": ("As it runs today", _stated("The process as it runs today")),
        "start-to-end": ("Steps from start to end", _start_to_end),
        "all-six": ("Suppliers, inputs, steps, outputs, customers, measures", _all_six),
        "customers-match": ("Customers agree with the VOC", _stated("The customers agree with the voice of the customer")),
        "performance": ("Step times and how often", _performance),
    },
    "issues_and_barriers": {
        "specific": ("Issues and barriers", _items("issues_and_barriers", "Issues and barriers")),
    },
}


def criteria(field: str) -> list[tuple[str, str]]:
    """The element's acceptance criteria as the script lists them: (id, text)."""
    from backend.middleware.skills import acceptance_criteria
    return acceptance_criteria("define", field)


def verbatim_spans(spans: Any, field: str, *answers: Any) -> dict[str, str]:
    """ADR-0093 decision 5, the safeguard: the judgment's spans that are verbatim substrings of every one of
    `answers` (the Belt's answer, and the text a Confirm stores when it is text), keyed by a criterion id of
    this element. Any other span is dropped — its row shows the whole answer once, marked "in your answer"."""
    ids = {cid for cid, _ in criteria(field)}
    texts = [str(a) for a in answers if isinstance(a, str) and a.strip()]
    out: dict[str, str] = {}
    for cid, span in (spans.items() if isinstance(spans, dict) else []):
        s = str(span or "").strip().strip("\"'“”‘’").strip()
        if str(cid) in ids and s and texts and all(s in t for t in texts):
            out[str(cid)] = s
    return out


def _calculated(field: str, values: dict[str, Any]) -> Optional[tuple[str, str]]:
    """ADR-0077: the benefits' cost of the gap as calculated in code, with how — None when nothing was."""
    if field != "benefits_analysis":
        return None
    from backend.phases import calculations
    row = calculations.latest(values, "define", field)
    lines = calculations.how_it_was_calculated(row)
    result = calculations._result(row)
    if not lines or not result.get("cost_of_gap"):
        return None
    figure = calculations.money_text(result["cost_of_gap"], str(result.get("currency") or ""))
    return f"{figure} per year", lines


def rows(field: str, values: dict[str, Any], *, spans: Optional[dict[str, str]] = None,
         judged: bool = True, upload: Optional[str] = None) -> list[dict[str, Any]]:
    """The element's rows: {id, label, required, met, value, source, formula}, in the script's order.

    `values` holds the element's value(s) as a Confirm stores them (with the case's confirmed values beside,
    for the calculation and the target's direction); `spans` the verified spans (`verbatim_spans`); `judged`
    whether the judgment found the answer sufficient (a read-back is made only then; a confirmed element was);
    `upload` the file the values came from (ADR-0085)."""
    template = TEMPLATES.get(field, {})
    spans = spans or {}
    calc = _calculated(field, values)
    out = []
    for cid, text in criteria(field):
        label, read = template.get(cid, (text.split(" — ")[0][:60], _span()))
        value, met = read(values)
        formula = None
        if cid == "cost-of-gap" and calc is not None:
            value, formula = calc
        if is_empty_capture(value) and cid in spans:
            value = spans[cid]
        source = (CALCULATED if formula else FROM_FILE if upload else IN_ANSWER if is_empty_capture(value)
                  else YOUR_ANSWER)
        out.append({"id": cid, "label": label, "required": True,
                    "met": bool(met) if met is not None else bool(judged),
                    "value": None if is_empty_capture(value) else value, "source": source,
                    **({"formula": formula} if formula else {})})
    return out


#: Keys whose label is not their name with the underscores dropped.
_LABELS = {"in_scope": "In scope", "out_scope": "Out of scope"}


def plain(v: Any) -> str:
    """A stored value as words, never raw JSON (ADR-0093 decision 4): text as it is, a MetricValue's own words,
    a mapping as "Label: value" parts, a list as its items."""
    if isinstance(v, dict) and "raw" in v and "value" in v:
        return str(v["raw"])
    if isinstance(v, dict):
        return "; ".join(f"{_LABELS.get(str(k), str(k).replace('_', ' ').capitalize())}: {plain(x)}" for k, x in v.items()
                         if not is_empty_capture(x))
    if isinstance(v, list):
        return "; ".join(plain(x) for x in v if not is_empty_capture(x))
    return str(v or "").strip()


def answer_text(field: str, values: dict[str, Any], belt_words: str = "") -> str:
    """The whole answer, shown once under rows marked "in your answer": the Belt's words, else the stored
    value in words."""
    if str(belt_words or "").strip():
        return str(belt_words).strip()
    return plain(values.get(field))


def number_of(field: str) -> int:
    """The element's number, 1..13 (the coached order)."""
    return DEFINE_FIELD_ORDER.index(field) + 1


def section_of(field: str) -> str:
    """The Gate section (A–G, R5's seven) the element's value appears in."""
    from backend.phases.define.report import element_of
    for i, (_n, _title, fields) in enumerate(REPORT_SECTIONS):
        if field in fields or any(element_of(f) == field for f in fields):
            return SECTION_LETTERS[i]
    return ""


def name_of(field: str) -> str:
    from backend.core import guard_messages
    return guard_messages.element_name("define", field)


def card(field: str, values: dict[str, Any], *, spans: Optional[dict[str, str]] = None, judged: bool = True,
         upload: Optional[str] = None, belt_words: str = "") -> dict[str, Any]:
    """The read-back card (readback_card_mockup.html): "Element n of 13 · name", "k of m criteria met", the rows,
    the whole answer once when a row is marked "in your answer", what is missing in plain words with one ask,
    and whether Confirm opens (every required criterion met — the server refuses it otherwise)."""
    rs = rows(field, values, spans=spans, judged=judged, upload=upload)
    open_rows = [r for r in rs if r["required"] and not r["met"]]
    statement = values.get(field) if field in ("problem_statement", "goal_statement") else None
    return {
        "field": field, "n": number_of(field), "of": DEFINE_POSITIONS, "name": name_of(field),
        "section": section_of(field), "rows": rs,
        "met": sum(1 for r in rs if r["met"]), "total": len(rs),
        **({"statement": statement} if isinstance(statement, str) and statement.strip() else {}),
        **({"answer": answer_text(field, values, belt_words)} if any(r["source"] == IN_ANSWER for r in rs) else {}),
        **({"upload": upload} if upload else {}),
        "missing": [r["label"] for r in open_rows],
        "ask": (f"Still needed before you can confirm: {', '.join(r['label'].lower() for r in open_rows)}."
                if open_rows else ""),
        "confirm": not open_rows,
    }


def open_required(field: str, values: dict[str, Any], *, spans: Optional[dict[str, str]] = None,
                  judged: bool = True) -> list[str]:
    """The ids of the element's required criteria not met — a Confirm with any is refused, nothing stored."""
    return [r["id"] for r in rows(field, values, spans=spans, judged=judged) if r["required"] and not r["met"]]


def strip(field: str) -> dict[str, Any]:
    """After a Confirm (ADR-0093 decision 3): "✓ Element n · name confirmed — the Gate document is updated
    (section X)"."""
    n, name, section = number_of(field), name_of(field), section_of(field)
    return {"field": field, "n": n, "name": name, "section": section,
            "text": f"✓ Element {n} · {name} confirmed — the Gate document is updated (section {section})."}


__all__ = ["TEMPLATES", "SECTION_LETTERS", "YOUR_ANSWER", "FROM_FILE", "CALCULATED", "IN_ANSWER", "criteria",
           "verbatim_spans", "rows", "plain", "answer_text", "number_of", "section_of", "name_of", "card", "open_required",
           "strip"]
