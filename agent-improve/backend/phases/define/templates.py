"""Element templates — ADR-0093 "Element templates and the Gate view".

Each Define element is shown as its acceptance criteria, one row each, with the value that goes into the Gate
and where it came from: the read-back card (before a Confirm, from the exact value a Confirm will store) and the
Gate's element card (after it, from the stored value) are drawn from the SAME rows, built here.

- The criteria are the ones the script states (R7), in its order, read from their owner in code (`criteria.py`, B7);
  a template adds no criterion and no wording to any prompt — only a short label and where the row's value is read
  from.
- Structured values are read in code (the ADR-0088 parsers). Free text is read from the judgment's quoted span
  per criterion (`SufficiencyJudgment.criterion_spans`, option (b)); a span counts only when it is a verbatim
  substring of the Belt's answer (`verbatim_spans`) — otherwise the row shows no value of its own and the whole
  answer is shown once, marked "in your answer".
- A row is met by its code check where the template has one (the same checks a Confirm is refused on: ADR-0088's
  parts, a number, a date, the SIPOC's columns, both scope halves); otherwise by the judgment's verdict.

Pure functions, no model call, nothing stored: the rows are a view of the stored value (ADR-0093 "Rejected").
Module-level functions only.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Optional

from backend.core.substate import is_empty_capture
from backend.phases.define import criteria as define_criteria
from backend.phases.define import parse
from backend.phases.define.report import REPORT_SECTIONS
from backend.phases.define.schema import CTQ_KEYS, DEFINE_FIELD_ORDER, DEFINE_POSITIONS, TEAM_MEMBER_KEYS

#: The sources a row's value can come from (ADR-0093 decision 2).
YOUR_ANSWER, FROM_FILE, CALCULATED, IN_ANSWER = "your answer", "from your file", "calculated", "in your answer"

#: The Gate's section letters, R5's seven in order (gate_view_mockup.html).
SECTION_LETTERS: tuple[str, ...] = ("A", "B", "C", "D", "E", "F", "G")

#: A row's value: text, a list of items, or a table {"columns": [...], "rows": [[...]]}; None when there is none.
Value = Any
#: (value, met) — `met` is the code check's answer, or None when the criterion is the judgment's to meet.
Read = tuple[Value, Optional[bool]]


def _team(values: dict[str, Any]) -> list[dict[str, Any]]:
    return [m for m in values.get("team") or [] if isinstance(m, dict)]


def _named(values: dict[str, Any], pattern: Any) -> Read:
    names = [str(m.get("name") or "").strip() for m in _team(values) if pattern.search(plain(m))]
    names = [n for n in names if n]
    return ("; ".join(names) or None), bool(names) if _team(values) else False


def _people(values: dict[str, Any]) -> Read:
    # G-297 (DEF-264, founder test 2026-10-27 #24): the read-back's table has the Gate's Time and Training columns —
    # a file's time commitment was in the coach's bullet list but not in the table.
    rows = [[str(m.get(k) or "—") for k in TEAM_MEMBER_KEYS] + [_time_of(m), _member_training(m) or "—"]
            for m in _team(values)]
    return ({"columns": ["Name", "Role", "Function", "Time", "Training"], "rows": rows} if rows else None), None


def _member_training(m: dict[str, Any]) -> Optional[str]:
    """The training a team entry states, or None."""
    # G-236: the member's own training entry, in whatever words ("none" included); else a column that says it.
    hit = str(m.get("training") or "").strip() or next(
        (str(v) for k, v in m.items() if k not in TEAM_MEMBER_KEYS
         and parse._TRAINING.search(str(v or ""))), None)
    if hit is None:
        # Training stated inside the name, role or function: the clause that states it, not the whole entry.
        hit = next((c.strip() for c in re.split(r"[;,.]", plain(m)) if parse._TRAINING.search(c)), None)
    return hit or None


def _training(values: dict[str, Any]) -> Read:
    said = []
    for m in _team(values):
        hit = _member_training(m)
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
    table = [[str(r.get(k) or "—") for k in CTQ_KEYS] for r in rows]
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
    p = _primary(values)
    name, unit = parse.metric_name(p.get("name")), str(p.get("unit") or "").strip()     # DEF-223: never the id
    return (f"{name} ({unit})" if name and unit else name or None), None


def _defined(values: dict[str, Any]) -> Read:
    p = _primary(values)
    parts = [parse.metric_name(p.get("name")), *(str(p.get(k) or "").strip() for k in ("unit", "meaning"))]
    return (" · ".join(x for x in parts if x) or None), None


def _metric(field: str) -> Callable[[dict[str, Any]], Read]:
    def read(values: dict[str, Any]) -> Read:
        v = values.get(field)
        if is_empty_capture(v):
            return None, False
        mv = parse.as_metric(v, target=field == "target_value")
        text = parse.metric_text(mv)
        # DEF-221: the limit in words, with the Belt's own wording beside it when it differs.
        said = parse.limit_phrase(mv) if field == "target_value" else ""
        return (f"{text} (you wrote “{said}”)" if said else text), mv["value"] is not None
    return read


def _direction(values: dict[str, Any]) -> Read:
    base, target = values.get("baseline_estimate"), values.get("target_value")
    if is_empty_capture(base) or is_empty_capture(target):
        return None, None
    return f"{parse.metric_text(base)} → {parse.metric_text(target)}", None


def _date(values: dict[str, Any]) -> Read:
    v = values.get("target_date")
    if is_empty_capture(v):
        return None, False
    return parse.date_shown(v), parse.calendar_date(v) is not None


def _scope(values: dict[str, Any]) -> Read:
    s = values.get("project_scope")
    if not isinstance(s, dict):
        return None, None
    inside, outside = plain(s.get("in_scope")), plain(s.get("out_scope"))
    return {"boxes": [["In scope", inside or "—"], ["Out of scope", outside or "—"]]}, bool(inside and outside)


def _benefit(key: str) -> Callable[[dict[str, Any]], Read]:
    def read(values: dict[str, Any]) -> Read:
        b = values.get("benefits_analysis")
        return (plain(b.get(key)) or None) if isinstance(b, dict) else None, None
    return read


def soft_text(benefits: Any) -> Optional[str]:
    """ADR-0096 decisions 1 and 4 (DEF-260): the stored soft benefits as words, each with how it will be seen —
    "fewer escalations to account managers (seen in the monthly escalation count)"; None when none is stored."""
    b = benefits.get("soft_benefits") if isinstance(benefits, dict) else None
    items = [s for s in b or [] if isinstance(s, dict) and str(s.get("benefit") or "").strip()]
    return "; ".join(f"{s['benefit']} (seen in {s['indicator']})" if str(s.get("indicator") or "").strip()
                     else str(s["benefit"]) for s in items) or None


def _realisation(values: dict[str, Any]) -> Read:
    """G-255: when the saving shows, met by the code check the Confirm and the gate share (`parse.realisation_stated`,
    which `parse.missing_parts` applies)."""
    b = values.get("benefits_analysis")
    return _benefit("realisation_schedule")(values)[0], (parse.realisation_stated(b) if isinstance(b, dict) else None)


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


def _step_time(st: dict[str, Any]) -> str:
    """A step's time as words: the average, then its range (DEF-172, G-179: one end of the range reads in words —
    never "(? to 20 days)"); "—" when none is given."""
    def text(v: Any) -> str:
        return parse.metric_text(v) if isinstance(v, dict) else "—"
    d = st.get("duration") or {}
    rng = (f" ({text(d['min'])} to {text(d['max'])})" if d.get("min") and d.get("max") else
           f", at most {text(d['max'])}" if d.get("max") else
           f", at least {text(d['min'])}" if d.get("min") else "")
    return (text(d["avg"]) if d.get("avg") else "—") + rng


def _performance(values: dict[str, Any]) -> Read:
    s = _sipoc(values)
    steps = parse.process_steps(s.get("process_steps"))
    if not steps:
        return None, None

    def text(v: Any) -> str:
        return parse.metric_text(v) if isinstance(v, dict) else "—"
    rows = []
    for st in steps:
        seen = "; ".join(f"{p['note']} ({p['said_by']})" if p.get("said_by") else str(p.get("note") or "")
                         for p in st.get("problems") or [] if isinstance(p, dict)) or "—"
        rows.append([f"{'⚠ ' if st.get('problems') else ''}{st['id']} · {st['name']}", _step_time(st),
                     text(st.get("runs_per_period")) if st.get("runs_per_period") else "—", seen])
    raw_perf = s.get("process_performance")
    perf: dict[str, Any] = raw_perf if isinstance(raw_perf, dict) else {}
    if perf.get("lead_time") or perf.get("runs_per_period"):
        rows.append(["Whole process", text(perf.get("lead_time")) if perf.get("lead_time") else "—",
                     text(perf.get("runs_per_period")) if perf.get("runs_per_period") else "—", "—"])
    # G-332 (DEF-259): a code check, never the planner's verdict — every step has a time, and how often is given once
    # for the whole process (ruling R-G, founder 2026-10-27; applied 2026-10-28) or for every step.
    timed = all(any(st["duration"].get(k) for k in parse.DURATION_KEYS) for st in steps)
    often = bool(perf.get("runs_per_period")) or all(st.get("runs_per_period") for st in steps)
    return {"columns": ["Step", "Time (range)", "How often", "Problems seen"], "rows": rows}, timed and often


def _stated(statement: str) -> Callable[[dict[str, Any]], Read]:
    """A criterion that is a check on the answer as a whole (no cause named, as-is), met by the judgment. Its row
    shows the judgment's quoted span, else "in your answer" — never the criterion's own wording (G-314, founder
    2026-10-28); only an absence (`_ABSENCES`), which no quote can show, keeps its statement."""
    def stated_read(values: dict[str, Any]) -> Read:
        return statement, None
    return stated_read


def _span() -> Callable[[dict[str, Any]], Read]:
    """Free text: the row's value is the judgment's quoted span (option (b)), read by `rows` — a row with no span of
    its own is not met (DEF-263)."""
    def span_read(values: dict[str, Any]) -> Read:
        return None, None
    return span_read


#: G-314 (DEF-263): the whole-answer checks that are an absence ("no cause and no fix named") — no quote can show
#: one, so their row keeps its statement.
_ABSENCES = frozenset({define_criteria.NO_CAUSE_NO_FIX})
#: Founder ruling 2026-10-28 (locked parts, .claude/rules/planning.md): goal → target → target date was accepted
#: with real answers on 2026-10-27 and changes only for a blocker. DEF-263's rules — a free-text row met only with a
#: quote of its own, two rows never sharing one passage — do not reach the goal statement's rows: they are met on
#: the judgment's verdict, as accepted.
_LOCKED_ELEMENTS = frozenset({"goal_statement"})
#: G-288 (DEF-263): the rows that state a size — when their span repeats another row's, the size is the figure in it.
_SIZE_ROWS = frozenset({define_criteria.BASELINE})
#: A figure as the Belt wrote it: a share, else a number with the word or two after it ("1,200 complaints").
_SIZE = re.compile(r"\d[\d,.]*\s?(?:%|percent|per cent)|\d[\d,.]*(?:\s+[^\s\d,.;:]+){0,2}")


#: element -> criterion id -> (label, how its value is read). The ids are the owner's constants (B7,
#: `phases/define/criteria.py`), never re-typed; `rows` drops a template entry the owner no longer lists and shows a
#: criterion the template does not know as free text.
TEMPLATES: dict[str, dict[str, tuple[str, Callable[[dict[str, Any]], Read]]]] = {
    "business_case": {
        define_criteria.WHAT: ("What is wrong", _span()),
        define_criteria.WHERE_WHEN: ("Where and since when", _span()),
        define_criteria.BASELINE: ("How big it is today", _span()),
        define_criteria.COST: ("What it costs", _span()),
        define_criteria.NO_CAUSE_NO_FIX: ("No cause and no fix", _stated("No cause and no solution named")),
    },
    "team": {
        define_criteria.CHAMPION: ("Champion (sponsor)", lambda v: _named(v, parse._CHAMPION)),
        define_criteria.PROCESS_OWNER: ("Process owner", lambda v: _named(v, parse._OWNER)),
        define_criteria.PEOPLE: ("Each person: name, role, function", _people),
        define_criteria.TRAINING: ("Training needed", _training),
    },
    "voc_summary": {
        define_criteria.CUSTOMERS: ("Customers", _ctq_part("customer", "customer")),
        define_criteria.NEEDS: ("Their needs", _ctq_part("need", "need")),
        define_criteria.CTQ: ("CTQs (measurable)", _ctq_table),
    },
    "problem_statement": {
        define_criteria.DEFECT: ("The defect", _fivew_key("what")),
        define_criteria.FIVE_W_TWO_H: ("The seven 5W2H answers", _fivew_table),
        define_criteria.MAGNITUDE: ("How big", _fivew_key("how_much")),
        define_criteria.NO_CAUSE_NO_FIX: ("No cause, no fix, no blame",
                                          _stated("No cause, no solution and no one to blame named")),
        define_criteria.LOCATED: ("Where in the process", _fivew_key("where")),
    },
    "baseline_estimate": {
        define_criteria.ONE_PRIMARY: ("Primary metric", _primary_name),
        define_criteria.QUANTIFIED: ("Baseline", _metric("baseline_estimate")),
        define_criteria.KPI_LINK: ("Business measure it feeds", _span()),
        define_criteria.REAL_DATA: ("Where the figure comes from", _span()),
        define_criteria.DEFINED: ("Name · unit · meaning", _defined),
    },
    "project_scope": {
        define_criteria.IN_AND_OUT: ("In and out of scope", _scope),
        define_criteria.START_END: ("Start and end point", _span()),
        define_criteria.NOT_TOO_BROAD: ("One process or area",
                                        _stated("One process or area, not everything around it")),
    },
    "goal_statement": {
        define_criteria.SAME_METRIC: ("Same metric as the problem", _span()),
        define_criteria.HOW_MUCH: ("How much improvement", _span()),
        define_criteria.BY_WHEN: ("By when", _span()),
    },
    "target_value": {
        define_criteria.NUMBER_AND_UNIT: ("Target", _metric("target_value")),
        define_criteria.DIRECTION: ("From the baseline to the target", _direction),
    },
    "target_date": {
        define_criteria.A_DATE: ("Target date", _date),
    },
    "benefits_analysis": {
        define_criteria.COST_OF_GAP: ("Cost of the gap", _benefit("cost_of_gap")),
        define_criteria.IMPACT_TYPE: ("Sustainable or one-off", _benefit("impact_type")),
        define_criteria.REALISATION: ("Realisation schedule", _realisation),
        define_criteria.FINANCE_CONTACT: ("Finance contact", _benefit("finance_contact")),
    },
    "secondary_metrics": {
        define_criteria.SIDE_EFFECT: ("Side effects watched", _items("secondary_metrics", "Secondary metrics")),
        define_criteria.NOT_THE_PRIMARY: ("Not the primary metric", _stated("Not the primary metric")),
    },
    "process_map_sipoc": {
        define_criteria.AS_IS: ("As it runs today", _stated("The process as it runs today")),
        define_criteria.START_TO_END: ("Steps from start to end", _start_to_end),
        define_criteria.ALL_SIX: ("Suppliers, inputs, steps, outputs, customers, measures", _all_six),
        define_criteria.CUSTOMERS_MATCH: ("Customers agree with the VOC",
                                          _stated("The customers agree with the voice of the customer")),
        define_criteria.PERFORMANCE: ("Step times and how often", _performance),
    },
    "issues_and_barriers": {
        define_criteria.SPECIFIC: ("Issues and barriers", _items("issues_and_barriers", "Issues and barriers")),
    },
}


def criteria(field: str) -> list[tuple[str, str]]:
    """The element's acceptance criteria, (id, text), in order — the owner's (B7), as the script states them."""
    return list(define_criteria.criteria(field))


def verbatim_spans(spans: Any, field: str, *answers: Any) -> dict[str, str]:
    """ADR-0093 decision 5, the safeguard: the judgment's spans that are verbatim substrings of every one of
    `answers` (the Belt's answer, and the text a Confirm stores when it is text), keyed by a criterion id of
    this element. Any other span is dropped — its row shows the whole answer once, marked "in your answer".
    A span of two or more quotes joined by " … " (evidence in two places of the answer — wave 0, founder test
    2026-10-27 #19: "In Field Service Austria … from March to September 2026") is kept when EVERY quote is a
    verbatim substring."""
    ids = [cid for cid, _ in criteria(field)]
    texts = [str(a) for a in answers if isinstance(a, str) and a.strip()]
    given = dict(spans) if isinstance(spans, dict) else {}
    out: dict[str, str] = {}
    for cid in ids:
        s = str(given.get(cid) or "").strip().strip("\"'“”‘’").strip()
        pieces = [p.strip().strip("\"'“”‘’").strip() for p in re.split(r"\s*(?:…|\.\.\.)\s*", s)]
        runs = [_quotes(p, texts) for p in pieces if p]
        if not s or not texts or not runs or any(r is None for r in runs):
            continue
        span = " … ".join(q for r in runs for q in r or [])
        if field in _LOCKED_ELEMENTS:
            out[cid] = span                                      # locked (founder 2026-10-28): as accepted
            continue
        if span in out.values() and cid in _SIZE_ROWS:
            # G-288: "how big it is today" quoted the same passage as "what is wrong" — the size is its figure.
            span = next((m.group(0).strip() for m in _SIZE.finditer(span)), "")
        if span and span not in out.values():
            out[cid] = span                                      # G-292: two rows never share one passage
    return out


def _quotes(piece: str, texts: list[str]) -> Optional[list[str]]:
    """DEF-263 (G-292, founder test 2026-10-27 #19): `piece` as the verbatim quotes it is made of, in order — itself
    when it is a substring of every text; else at most three runs of at least two words each, joined by the planner
    from two places of the answer ("In Field Service Austria, from March to September 2026"). None otherwise."""
    if all(piece in t for t in texts):
        return [piece]
    words, first = piece.split(), texts[0]
    out: list[str] = []
    i, at = 0, 0
    while i < len(words) and len(out) < 3:
        j = next((j for j in range(len(words), i + 1, -1) if first.find(" ".join(words[i:j]), at) >= 0), None)
        if j is None:
            return None
        run = " ".join(words[i:j])
        at = first.find(run, at) + len(run)
        out.append(run.rstrip(",;:"))
        i = j
    if i < len(words) or not all(q in t for q in out for t in texts):
        return None
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
         judged: bool = True, upload: Optional[str] = None, case: Optional[dict[str, Any]] = None,
         before_confirm: bool = False) -> list[dict[str, Any]]:
    """The element's rows: {id, label, required, met, value, source, formula}, in the script's order.

    `values` holds the element's value(s) as a Confirm stores them (with the case's confirmed values beside,
    for the calculation and the target's direction); `spans` the verified spans (`verbatim_spans`); `judged`
    whether the judgment found the answer sufficient (a read-back is made only then; a confirmed element was);
    `upload` the file the values came from (ADR-0085). DEF-263: when the judgment quoted (`spans` given, even empty),
    a free-text row is met only with a span of its own; a judgment that quoted nothing (`spans` None) is met on its
    verdict. DEF-265 (founder test 2026-10-27 #22): with the `case` (its lead and people), the team's people row
    is the Gate's own table — the lead first, each person's status; `before_confirm` for a read-back."""
    template = TEMPLATES.get(field, {})
    quoted = spans is not None and field not in _LOCKED_ELEMENTS
    spans = spans or {}
    calc = _calculated(field, values)
    out = []
    for cid, text in criteria(field):
        label, read = template.get(cid, (text.split(" — ")[0][:60], _span()))
        value, met = read(values)
        if cid == define_criteria.PEOPLE and case and (case.get("leader") or case.get("people")):
            value = {k: v for k, v in _team_table(values, case, before_confirm=before_confirm).items() if k != "kind"}
        kind = getattr(read, "__name__", "")
        if kind == "stated_read" and (cid in spans or cid not in _ABSENCES):
            value = None                       # G-314: the quote, or "in your answer" — never the criterion's wording
        formula = None
        if cid == define_criteria.COST_OF_GAP and calc is not None:
            value, formula = calc
        if is_empty_capture(value) and cid in spans:
            value = spans[cid]
        source = (CALCULATED if formula else FROM_FILE if upload else IN_ANSWER if is_empty_capture(value)
                  else YOUR_ANSWER)
        if met is None:
            # DEF-263 (founder test 2026-10-27 #14, #19): a free-text row is met only with words of its own; a
            # whole-answer check and a file's row on the judgment's verdict.
            met = bool(judged) and (kind != "span_read" or not quoted or bool(upload) or not is_empty_capture(value))
        out.append({"id": cid, "label": label, "required": True, "met": bool(met),
                    "value": None if is_empty_capture(value) else value, "source": source,
                    **({"formula": formula} if formula else {})})
    soft = soft_text(values.get("benefits_analysis")) if field == "benefits_analysis" else None
    if soft:
        # DEF-260 (ADR-0096 decision 4): the soft benefits on the card and in the Gate, apart from the hard figures —
        # shown, not a criterion (decision 3's criterion waits on its requirement).
        out.append({"id": "soft-benefits", "label": "Soft benefits", "required": False, "met": True,
                    "value": soft, "source": FROM_FILE if upload else YOUR_ANSWER})
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


#: G-255 (eval E19): a figure in the Belt's words — "62,000", "23%", "2.8k".
_FIGURE = re.compile(r"\d[\d,.]*\d|\d")


def _dropped_figure(belt_words: str, shown: str) -> bool:
    """G-255 (DEF-185, eval E19): a figure the Belt gave that no row of the card shows — then the whole answer is shown
    once, so a read-back never loses the Belt's numbers."""
    have = shown.replace(",", "")
    return any(f.replace(",", "") not in have for f in _FIGURE.findall(str(belt_words or "")))


def card(field: str, values: dict[str, Any], *, spans: Optional[dict[str, str]] = None, judged: bool = True,
         upload: Optional[str] = None, belt_words: str = "", case: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """The read-back card (readback_card_mockup.html): "Element n of 13 · name", "k of m criteria met", the rows,
    the whole answer once when a row is marked "in your answer", what is missing in plain words with one ask,
    and whether Confirm opens (every required criterion met — the server refuses it otherwise)."""
    rs = rows(field, values, spans=spans, judged=judged, upload=upload, case=case, before_confirm=True)
    open_rows = [r for r in rs if r["required"] and not r["met"]]
    shown = " ".join(plain(r.get("value")) + " " + str(r.get("formula") or "") for r in rs)
    # G-253 (DEF-185): the voice of the customer in the Belt's words, as the Gate's card shows it — a need with no CTQ
    # row would otherwise not reach the card at all.
    statement = values.get(field) if field in ("problem_statement", "goal_statement", "voc_summary") else None
    return {
        "field": field, "n": number_of(field), "of": DEFINE_POSITIONS, "name": name_of(field),
        "section": section_of(field), "rows": rs,
        "met": sum(1 for r in rs if r["required"] and r["met"]), "total": sum(1 for r in rs if r["required"]),
        **({"statement": statement} if isinstance(statement, str) and statement.strip() else {}),
        **({"answer": answer_text(field, values, belt_words)}
           if any(r["source"] == IN_ANSWER for r in rs) or _dropped_figure(belt_words, f"{shown} {statement or ''}")
           else {}),
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


#: Each row's one-line explanation in the Gate (C1, DEF-086): criterion id -> the report's FIELD_EXPLAIN key.
_WHY: dict[str, dict[str, str]] = {
    "business_case": {define_criteria.WHAT: "business_case"},
    "team": {define_criteria.CHAMPION: "champion", define_criteria.PEOPLE: "team"},
    "voc_summary": {define_criteria.CUSTOMERS: "voc_summary", define_criteria.CTQ: "ctqs"},
    "problem_statement": {define_criteria.FIVE_W_TWO_H: "five_w_two_h"},
    "baseline_estimate": {define_criteria.ONE_PRIMARY: "primary", define_criteria.QUANTIFIED: "baseline_target"},
    "project_scope": {define_criteria.IN_AND_OUT: "scope"},
    "goal_statement": {define_criteria.HOW_MUCH: "objective"},
    "target_date": {define_criteria.A_DATE: "target_date"},
    "benefits_analysis": {define_criteria.COST_OF_GAP: "cost_of_gap", define_criteria.IMPACT_TYPE: "impact_type",
                          define_criteria.REALISATION: "realisation_schedule",
                          define_criteria.FINANCE_CONTACT: "finance_contact"},
    "secondary_metrics": {define_criteria.SIDE_EFFECT: "secondary_metrics"},
    "process_map_sipoc": {define_criteria.ALL_SIX: "sipoc"},
    "issues_and_barriers": {define_criteria.SPECIFIC: "issues"},
}

#: R16's sources, as the History link says them.
_SOURCE_WORDS = {"typed": "typed by the team", "upload": "read from a file",
                 "coach_proposed": "proposed by the coach and confirmed"}


def _element_fields(field: str) -> tuple[str, ...]:
    from backend.phases.define.schema import _CAPTURED_INSIDE
    return (field, *_CAPTURED_INSIDE.get(field, ()))


def _status(field: str, artifacts: dict[str, Any], field_status: dict[str, Any]) -> str:
    """The element's status in the Gate: confirmed (every value it holds is stored — only a Confirm stores), parked,
    awaiting your Confirm (a read-back is pending), or open."""
    if all(not is_empty_capture(artifacts.get(f)) for f in _element_fields(field)):
        return "confirmed"
    entry = field_status.get(field) or {}
    if entry.get("status") == "parked":
        return "parked"
    if entry.get("status") == "answered" and entry.get("pending"):
        return "awaiting your Confirm"
    return "open"


def history(field: str, field_log: list[dict[str, Any]] | None) -> list[str]:
    """DEF-199 (R16): the element's history as sentences, oldest first — when, who, where the value came from,
    and for a change what it was before and why. Never raw JSON."""
    fields = _element_fields(field)
    entries = sorted((e for e in field_log or [] if isinstance(e, dict) and e.get("field") in fields
                      and e.get("phase", "define") == "define"),
                     key=lambda e: (str(e.get("timestamp") or ""), int(e.get("turn") or 0)))
    out = []
    for e in entries:
        when = str(e.get("timestamp") or "")[:10] or "undated"
        who = f" by {e['by']}" if e.get("by") else ""
        part = "" if e.get("field") == field else f" ({str(e['field']).replace('_', ' ')})"
        source = _SOURCE_WORDS.get(str(e.get("source") or ""), "")
        value = plain(e.get("value"))
        if e.get("prior_value") in (None, "", [], {}):
            out.append(f"{when} — confirmed{who}{part}: “{value}”" + (f", {source}." if source else "."))
        else:
            why = f" Reason: {e['reason']}." if e.get("reason") else ""
            out.append(f"{when} — changed{who}{part} from “{plain(e.get('prior_value'))}” to “{value}”"
                       + (f", {source}." if source else ".") + why)
    return out


def gate_card(field: str, artifacts: dict[str, Any], field_status: dict[str, Any],
              field_log: list[dict[str, Any]] | None = None, case: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """ADR-0093 decision 4: the element's card in the Gate — "Element n · name", its status, its History, and for a
    confirmed element the SAME rows as its read-back card (`rows`, with the spans and the file its Confirm kept);
    for one not confirmed, what it still needs (its criteria by label), never a value."""
    from backend.phases.define.report import FIELD_EXPLAIN
    status = _status(field, artifacts, field_status)
    entry = field_status.get(field) or {}
    out: dict[str, Any] = {"field": field, "n": number_of(field), "name": name_of(field), "status": status,
                           "history": history(field, field_log)}
    if status != "confirmed":
        out["needs"] = [label for cid, (label, _read) in TEMPLATES[field].items()]
        return out
    rs = rows(field, artifacts, spans=entry.get("spans"), upload=entry.get("upload"), case=case)
    why = _WHY.get(field, {})
    out["rows"] = [{**r, **({"why": FIELD_EXPLAIN[why[r["id"]]]} if r["id"] in why else {})} for r in rs]
    if field in ("problem_statement", "goal_statement", "voc_summary") and isinstance(artifacts.get(field), str):
        out["statement"] = artifacts[field]
        if field != "voc_summary":
            out["statement_why"] = FIELD_EXPLAIN["problem_statement" if field == "problem_statement" else "objective"]
    if any(r["source"] == IN_ANSWER for r in rs):
        out["answer"] = answer_text(field, artifacts)
    return out


#: DEF-176: a team entry's column for the time on the project, whatever the file called it (DEF-229 keeps them all).
_TIME = re.compile(r"time|hours|commitment|availab|capacity", re.I)
_LEAD = re.compile(r"\blead(?:er)?\b", re.I)
_DASH = "—"
#: DEF-265 (founder test 2026-10-27 #21, #29; wording ruled by the founder 2026-10-28): the team table's statuses in
#: plain words — the lead's matches the role — and the one line under the table that explains them.
LEAD_STATUS = "Leads the project"
PERSON_STATUS = {"member": "On the case", "proposed": "Proposed — the lead confirms"}
TEAM_STATUS_NOTE = ("On the case: can open and work on the case. Proposed: named in the team, not yet confirmed by "
                    "the project lead in the team panel.")


def _time_of(m: dict[str, Any]) -> str:
    v = m.get("time_commitment") or next((m[k] for k in m if k not in ("name", "role", "function", "training")
                                          and _TIME.search(str(k)) and str(m[k] or "").strip()), "")
    return str(v or "").strip() or _DASH


def _team_table(artifacts: dict[str, Any], case: dict[str, Any], *, before_confirm: bool = False) -> dict[str, Any]:
    """DEF-176 (gate_view_mockup.html, section A): ONE table,
    Name | Role | Function | Time | Training | Status — the project lead first under the case's one name for the
    lead (ADR-0090 decision 4), then the champion (named as such), the process owner and the members, each as
    their confirmed entry states it, with member / proposed from their person record; then anyone on the case
    element 2 does not name. "—" where nothing states a value. The department is one case-level line above the
    table, not a column. DEF-265: the lead's status is "Leads the project"; a person's, in plain words; before the
    Confirm (`before_confirm`, the read-back) a named member not yet on the case is the proposed member the Confirm
    makes (ADR-0090); `note` explains the statuses."""
    def _norm(t: Any) -> str:
        return " ".join(str(t or "").lower().split())
    team = _team(artifacts)
    people = [p for p in case.get("people") or [] if isinstance(p, dict)]
    record = next((p for p in people if _norm(p.get("role")) == "project lead"), None)
    lead = str(case.get("leader") or (record or {}).get("full_name") or "").strip()

    def named(name: Any, full: Any) -> bool:
        """`name` is `full`, or a shorter form whose words begin it (ADR-0090: "Priya" for "Priya Shah")."""
        n, f = _norm(name).split(), _norm(full).split()
        return bool(n) and f[:len(n)] == n

    def record_of(name: Any) -> Optional[dict[str, Any]]:
        hits = [p for p in people if named(name, p.get("full_name"))]
        return hits[0] if len(hits) == 1 else None          # never a guess between two

    def status(p: Optional[dict[str, Any]]) -> str:
        if p is None:
            return PERSON_STATUS["proposed"] if before_confirm else _DASH
        return PERSON_STATUS.get(str(p.get("status") or "member"), _DASH)

    def is_lead(m: dict[str, Any]) -> bool:
        if lead and named(m.get("name"), lead):
            return True
        return bool(_LEAD.search(str(m.get("role") or ""))) and not lead
    entry = next((m for m in team if is_lead(m)), None)
    rows: list[list[str]] = []
    shown: list[Optional[dict[str, Any]]] = [record] if record else []
    if lead or entry:
        e = entry or {}
        belt = str(case.get("belt_level") or "").strip()
        rows.append([lead or str(e.get("name") or _DASH), "Project lead",
                     str(e.get("function") or (record or {}).get("function") or "").strip()
                     or (f"{belt.capitalize()} Belt" if belt else _DASH),
                     _time_of(e) if e else _DASH, (_member_training(e) if e else None) or _DASH, LEAD_STATUS])
    rest = [m for m in team if m is not entry]
    champions = [m for m in rest if parse._CHAMPION.search(str(m.get("role") or ""))]
    order = champions + [m for m in rest if parse._OWNER.search(str(m.get("role") or ""))
                         and not parse._CHAMPION.search(str(m.get("role") or ""))]
    order += [m for m in rest if all(m is not o for o in order)]
    for m in order:
        p = record_of(m.get("name"))
        shown.append(p)
        role = str(m.get("role") or "").strip()
        if champions and m is champions[0] and "champion" not in role.lower():
            role = f"{role} (Champion)" if role else "Champion"        # DEF-100: the report names the Champion
        rows.append([str(m.get("name") or "").strip() or _DASH, role or _DASH,
                     str(m.get("function") or "").strip() or _DASH, _time_of(m),
                     _member_training(m) or _DASH, status(p)])
    for p in people:                                   # on the case, not named in element 2
        if any(p is q for q in shown):
            continue
        rows.append([str(p.get("full_name") or "").strip() or _DASH, str(p.get("role") or "").strip() or _DASH,
                     str(p.get("function") or "").strip() or _DASH, _DASH, _DASH, status(p)])
    return {"kind": "table", "columns": ["Name", "Role", "Function", "Time", "Training", "Status"], "rows": rows,
            "note": TEAM_STATUS_NOTE}


#: DEF-178: the 5W2H table's row labels in the Gate (gate_view_mockup.html, section C).
_FIVE_W_LABELS = {"what": "What", "where": "Where", "when": "When", "who": "Who is affected",
                  "why": "Why it matters", "how": "How it shows up", "how_much": "How much"}


def _chart(artifacts: dict[str, Any]) -> Optional[dict[str, Any]]:
    """DEF-180 (gate_view_mockup.html, section E): the baseline-to-target chart in element 5's card — the report's
    own drawing (visuals.draw, confirmed values only: no target until the target is confirmed), on a 0–100 scale
    with its quarter ticks for a share, else on the larger of the two figures."""
    from backend.phases.define.visuals import draw
    v = draw("baseline_target", artifacts, confirmed=True, field="target_value")
    if not v:
        return None
    share = v.get("unit") == "%"
    top = 100 if share else max(float(v.get("baseline") or 0), float(v.get("target") or 0)) or 1
    return {"metric": v.get("metric"), "unit": v.get("unit") or "", "baseline": v.get("baseline"),
            "target": v.get("target"), "target_date": v.get("target_date"), "scale": top,
            "ticks": [0, 25, 50, 75, 100] if share else None}


def _sipoc_view(artifacts: dict[str, Any]) -> Optional[dict[str, Any]]:
    """DEF-181 (gate_view_mockup.html, section F): the confirmed SIPOC as the mockup draws it — suppliers, inputs,
    outputs and customers as columns; the steps as a numbered flow, each with its time and how often it runs, marked
    `located` (the steps the problem statement places the problem in: `parse.located_steps`, DEF-211) or `flagged`
    (problem notes outside them); what is measured on the outputs; the step count, lead time and frequency for the
    element's name; and the performance table. Every figure is the stored MetricValue's own words."""
    from backend.core.diagrams import sipoc_columns
    from backend.phases.define.report import FIELD_EXPLAIN
    s = _sipoc(artifacts)
    steps = parse.process_steps(s.get("process_steps"))
    if not steps:
        return None

    def text(v: Any) -> str:
        return parse.metric_text(v) if isinstance(v, dict) else ""
    fivew = _fivew(artifacts)
    hit = set(parse.located_steps(fivew.get("steps"), s)["located"]) if fivew.get("steps") else set()
    drawn, rows = [], []
    for i, st in enumerate(steps, 1):
        problems = [p for p in st.get("problems") or [] if isinstance(p, dict)]
        mark = "located" if st["id"] in hit else "flagged" if problems else ""
        often = text(st.get("runs_per_period")) or _DASH
        time = _step_time(st)
        drawn.append({"n": i, "name": st["name"], "time": time, "often": often, "mark": mark,
                      "problems": [{"note": str(p.get("note") or ""), "said_by": str(p.get("said_by") or "")}
                                   for p in problems]})
        said = list(dict.fromkeys(str(p.get("said_by") or "").strip() for p in problems if p.get("said_by")))
        rows.append([f"{i} {st['name']}", time, often,
                     "; ".join(str(p.get("note") or "") for p in problems) or _DASH, ", ".join(said) or _DASH])
    perf: dict[str, Any] = parse.process_performance(s.get("process_performance")) or {}
    note = " · ".join(x for x in (f"{len(steps)} step{'s' if len(steps) != 1 else ''}",
                                   f"lead time {text(perf.get('lead_time'))}" if text(perf.get("lead_time")) else "",
                                   text(perf.get("runs_per_period"))) if x)
    measured = s.get("process_metrics")
    if isinstance(measured, list):
        measured = "; ".join(str(m.get("name") or m) if isinstance(m, dict) else str(m) for m in measured)
    columns = sipoc_columns(s)
    return {"kind": "sipoc", "columns": {k: columns[k] for k in ("suppliers", "inputs", "outputs", "customers")},
            "steps": drawn, "note": note, "measured": str(measured or "").strip() or None,
            "located": [d["n"] for d in drawn if d["mark"] == "located"],
            "table": {"columns": ["Step", "Time · average (range)", "How often", "Problems the team sees", "Said by"],
                      "rows": rows, "marks": [d["mark"] for d in drawn]},
            "why": FIELD_EXPLAIN["sipoc"], "measured_why": FIELD_EXPLAIN["process_metrics"]}


def _baseline_line(artifacts: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> Optional[str]:
    """DEF-262 (G-311, founder test 2026-10-27 #38): Gate E's Baseline — the figure as parsed, then where it comes from
    and the period, in the Belt's words (the verified "real data" span): "38% · from the service desk system, March to
    September 2026". Never the whole answer, which the stored MetricValue keeps as its `raw` (ADR-0071). Without the
    span, the figure alone."""
    base = artifacts.get("baseline_estimate")
    if is_empty_capture(base):
        return None
    mv = parse.as_metric(base)
    figure = parse.metric_text(mv) if mv.get("value") is not None else plain(base)
    source = str((by_id.get(define_criteria.REAL_DATA) or {}).get("value") or "").strip().rstrip(".").strip()
    return " · ".join(x for x in (figure, source) if x) or None


def _view(field: str, artifacts: dict[str, Any], card: dict[str, Any], case: dict[str, Any]) -> Optional[dict[str, Any]]:
    """DEF-176..178: how a confirmed element's card is laid out in the Gate (gate_view_mockup.html, sections A–C),
    read from the card's own rows and the stored values — never a value they do not hold. None: the rows."""
    from backend.phases.define.report import FIELD_EXPLAIN, _savings
    by_id = {r["id"]: r for r in card.get("rows") or []}

    def item(label: str, cid: str) -> list[Any]:
        r = by_id.get(cid) or {}
        return [label, r.get("value"), *([r["why"]] if r.get("why") else [])]
    if field == "team":
        return {**_team_table(artifacts, case), "why": FIELD_EXPLAIN["team"]}
    if field == "business_case":
        return {"kind": "kv", "items": [item("What", define_criteria.WHAT),
                                        item("Where and since when", define_criteria.WHERE_WHEN),
                                        item("Size", define_criteria.BASELINE), item("Cost", define_criteria.COST)]}
    if field == "benefits_analysis":
        from backend.phases.calculations import expected_saving_text
        raw = artifacts.get("benefits_analysis")
        b: dict[str, Any] = raw if isinstance(raw, dict) else {}
        saving = expected_saving_text(_savings(artifacts))
        return {"kind": "kv",
                "figures": [["Cost of the gap today", plain(b.get("cost_of_gap")) or None, FIELD_EXPLAIN["cost_of_gap"]],
                            ["Expected saving at the target", f"{saving} a year" if saving else None]],
                "items": [item("Sustainable or one-off", define_criteria.IMPACT_TYPE),
                          item("When it lands", define_criteria.REALISATION),
                          item("Finance contact", define_criteria.FINANCE_CONTACT),
                          # DEF-260 (ADR-0096 decisions 4 and 6): soft benefits apart from the money; "not stated"
                          # when the Belt gave none, never added to the hard figure.
                          ["Soft benefits", soft_text(b) or "not stated"]]}
    if field == "problem_statement":
        fw = _fivew(artifacts)
        return {"kind": "statement", "why": FIELD_EXPLAIN["five_w_two_h"],
                **({"table": {"columns": ["5W2H", "Answer"],
                              "rows": [[label, str(fw.get(k) or "").strip() or _DASH]
                                       for k, label in _FIVE_W_LABELS.items()]}} if fw else {})}
    if field == "goal_statement":
        return {"kind": "statement"}
    if field == "process_map_sipoc":
        return _sipoc_view(artifacts)
    if field == "issues_and_barriers":
        # DEF-182: the issues in the Belt's order and words (ADR-0088's one list parser), numbered once; no owner.
        issues = parse.list_items(artifacts.get("issues_and_barriers"), "Issues and barriers")
        return {"kind": "list", "items": issues, "why": FIELD_EXPLAIN["issues"]} if issues else None
    if field == "voc_summary":
        table, _met = _ctq_table(artifacts)
        if not table:
            return None
        n = len(table["rows"])
        return {"kind": "table", **table, "note": f"{n} CTQ{'s' if n != 1 else ''}", "why": FIELD_EXPLAIN["ctqs"]}
    if field == "baseline_estimate":
        p = _primary(artifacts)
        name, _ok = _primary_name(artifacts)
        meaning = str(p.get("meaning") or "").strip()
        return {"kind": "kv", "items": [
            ["Metric", " — ".join(x for x in (name, meaning) if x) or None, FIELD_EXPLAIN["primary"]],
            item("Business measure it feeds", define_criteria.KPI_LINK),
            ["Baseline", _baseline_line(artifacts, by_id), FIELD_EXPLAIN["baseline_target"]]],
            **({"chart": chart} if (chart := _chart(artifacts)) else {})}
    if field == "project_scope":
        boxes, _met = _scope(artifacts)
        return {"kind": "boxes", "boxes": boxes["boxes"], "why": FIELD_EXPLAIN["scope"]} if boxes else None
    return None


def gate_view(artifacts: dict[str, Any], field_status: dict[str, Any] | None = None,
              field_log: list[dict[str, Any]] | None = None, case: dict[str, Any] | None = None) -> dict[str, Any]:
    """ADR-0093 decision 4 (gate_view_mockup.html): sections A–G (R5's seven, in order), each with its elements'
    cards in the report's order and a status ("confirmed", "k of m confirmed", "open"); "Still to confirm" at the
    end with the element numbers. One numbering with the chat and the progress view (the coached order).
    A confirmed card of sections A–C carries its `view`, the mockup's layout (DEF-176..178); `case` gives the
    project lead's one name (ADR-0090)."""
    from backend.phases.define.report import FIELD_EXPLAIN, element_of
    field_status = dict(field_status or {})
    sections = []
    for i, (_n, title, fields) in enumerate(REPORT_SECTIONS):
        elements: list[str] = []
        for f in fields:
            e = element_of(f)
            if e in TEMPLATES and e not in elements:
                elements.append(e)
        cards = [gate_card(e, artifacts, field_status, field_log, case) for e in elements]
        for c in cards:
            view = (_view(c["field"], artifacts, c, case or {}) if c["status"] == "confirmed" else
                    # DEF-176: the people on the case are case data — listed while element 2 is still open.
                    {**_team_table({}, case or {}), "why": FIELD_EXPLAIN["team"]}
                    if c["field"] == "team" and (case or {}).get("people") else None)
            if view:
                c["view"] = view
        done = sum(1 for c in cards if c["status"] == "confirmed")
        sections.append({"letter": SECTION_LETTERS[i], "title": title, "elements": cards,
                         # DEF-197 (gate_view_mockup.html): a section of several elements counts them, also when
                         # all are confirmed ("3 of 3 confirmed"); one element reads its own status.
                         "status": ("open" if not done else "confirmed" if len(cards) == 1
                                    else f"{done} of {len(cards)} confirmed")})
    still = [{"n": number_of(f), "name": name_of(f), "field": f} for f in DEFINE_FIELD_ORDER
             if _status(f, artifacts, field_status) != "confirmed"]
    return {"sections": sections, "still_to_confirm": still}


def strip(field: str) -> dict[str, Any]:
    """After a Confirm (ADR-0093 decision 3): "✓ Element n · name confirmed — the Gate document is updated
    (section X)"."""
    n, name, section = number_of(field), name_of(field), section_of(field)
    return {"field": field, "n": n, "name": name, "section": section,
            "text": f"✓ Element {n} · {name} confirmed — the Gate document is updated (section {section})."}


#: R-C (ADR-0114, the approved mockup "progress-led, business" v2): the card's fixed words.
EXAMPLE_LABEL = "What a good answer looks like · example, not your data"
WHY_LINK, STATUS_LINK = "Why this matters", "Where do we stand?"
_SUMMARY_CHARS = 90


def _summary(field: str, artifacts: dict[str, Any]) -> str:
    """A stored element in a few words, for the saved note: a list by its count, anything else as words, cut."""
    value = artifacts.get(field)
    if isinstance(value, list):
        return f"{len(value)} {'people' if field == 'team' else 'listed'}"
    if field == "process_map_sipoc" and isinstance(value, dict):
        return f"{len(value.get('process_steps') or [])} steps"
    text = " ".join(plain(value).split())
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        import datetime as _dt
        day = _dt.date.fromisoformat(text)
        text = f"{day.day} {day:%B %Y}"
    return text if len(text) <= _SUMMARY_CHARS else text[:_SUMMARY_CHARS].rsplit(" ", 1)[0] + "…"


def saved_note(stored: list[str], artifacts: dict[str, Any]) -> Optional[dict[str, Any]]:
    """R-C part 2: one line naming every element the last Confirm stored, with a short summary, and the Gate section
    to view it in ("Target and target date saved: under 10% · 31 March 2027"). None when nothing was stored."""
    elements = [f for f in DEFINE_FIELD_ORDER if f in stored]
    if not elements:
        return None
    names = [name_of(f) for f in elements]
    named = " and ".join([names[0], *(n[:1].lower() + n[1:] for n in names[1:])])
    return {"fields": elements, "section": section_of(elements[0]),
            "text": f"{named} saved: " + " · ".join(_summary(f, artifacts) for f in elements)}


def _sipoc_example() -> dict[str, Any]:
    """The SIPOC's card example, from its structured file (DEF-211), in the SIPOC's own columns."""
    import json

    from backend.middleware.skills import SKILLS_ROOT
    from backend.phases.define.schema import SIPOC_KEYS
    from backend.phases.define.visuals import SIPOC_EXAMPLE
    example = json.loads((SKILLS_ROOT / "dmaic-define-phase" / SIPOC_EXAMPLE).read_text(encoding="utf-8"))
    labels = {"process_steps": "Process steps", "process_metrics": "Measures"}

    def words(v: Any) -> str:
        if isinstance(v, list):
            return (" → " if v and isinstance(v[0], dict) else ", ").join(
                str(x.get("name") if isinstance(x, dict) else x) for x in v)
        return str(v or "")
    return {"columns": ["Part", "Example"],
            "rows": [[labels.get(k, k.capitalize()), words(example.get(k))] for k in SIPOC_KEYS]}


def teaching_card(field: str, artifacts: dict[str, Any], field_status: dict[str, Any] | None = None, *,
                  stored: Optional[list[str]] = None, note: str = "") -> dict[str, Any]:
    """R-C (ADR-0114 decision 1): the element card — one template for every element, assembled here from the skill's
    element block and the phase state, no model call. Its six parts, top to bottom: the step trail ("✓ n-1 · previous
    › [n] current › n+1 · next", "k of N confirmed"); the saved note for what the last Confirm stored; the title and
    one-line purpose; YOUR TURN (the question and a hint — never a confirm prompt); the example in the element's own
    columns, under one label; the quiet help links. `note` is a line from code about why the element is taught again
    (a return to a parked element)."""
    from backend.middleware.skills import card_parts, element_text
    field_status = dict(field_status or {})
    parts = card_parts("define", field)
    n = number_of(field)

    def step(i: int) -> Optional[dict[str, Any]]:
        if not 1 <= i <= len(DEFINE_FIELD_ORDER):
            return None
        f = DEFINE_FIELD_ORDER[i - 1]
        return {"n": i, "name": name_of(f), "field": f,
                "confirmed": _status(f, artifacts, field_status) == "confirmed"}
    confirmed = sum(1 for f in DEFINE_FIELD_ORDER if _status(f, artifacts, field_status) == "confirmed")
    example = parts.get("example") or (_sipoc_example() if field == "process_map_sipoc" else None)
    return {
        "field": field, "n": n, "of": DEFINE_POSITIONS, "name": name_of(field), "section": section_of(field),
        "trail": {"previous": step(n - 1), "current": step(n), "next": step(n + 1),
                  "confirmed": confirmed, "of": DEFINE_POSITIONS},
        "saved": saved_note(list(stored or []), artifacts),
        **({"note": note} if note else {}),
        "title": name_of(field), "purpose": parts.get("purpose", ""),
        "your_turn": {"question": parts.get("question", ""), "hint": parts.get("hint", "")},
        **({"example": {"label": EXAMPLE_LABEL, **example}} if example else {}),
        "help": [{"label": WHY_LINK, "text": element_text("define", field, "Why it matters")},
                 *([{"label": parts["help"], "ask": parts["help"]}] if parts.get("help") else []),
                 {"label": STATUS_LINK, "ask": STATUS_LINK}],
    }


def card_text(card: dict[str, Any]) -> str:
    """The card as the conversation keeps it for the coach's later turns and the transcript: the saved note, the
    element and its question — the page draws the card itself, never this text beside it."""
    saved = (card.get("saved") or {}).get("text")
    lines = [f"{saved}." if saved else "", str(card.get("note") or ""),
             f"Element {card['n']} of {card['of']} · {card['name']}: {card['your_turn']['question']}"]
    return "\n\n".join(x for x in lines if x)


__all__ = ["TEMPLATES", "SECTION_LETTERS", "YOUR_ANSWER", "FROM_FILE", "CALCULATED", "IN_ANSWER", "criteria",
           "verbatim_spans", "rows", "plain", "answer_text", "history", "gate_card", "gate_view", "number_of", "section_of", "name_of", "card", "open_required",
           "strip", "EXAMPLE_LABEL", "WHY_LINK", "STATUS_LINK", "saved_note", "teaching_card", "card_text"]
