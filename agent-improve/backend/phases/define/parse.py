"""Define values read in code, before any model.

`parse_limit` (G-120, DEF-032): a target written as a number or as a limit — "under / below /
less than / at most 5%", "unter / weniger als / höchstens / maximal 5 %" — as number, unit and
direction. `metric_value` (ADR-0071, DEF-076): the ONE parser of the baseline and the target —
their Belt's words as a MetricValue {value, unit, direction, is_estimate, raw}. `parse_sipoc` (G-121, DEF-158): the Belt's SIPOC, written with its six labels, as the
six columns `schema.SIPOC_KEYS`; a column without its label is left out, never guessed.
`calendar_date` is the one date reader (ADR-0088 decision 5); `missing_parts` is the parts check the
Confirm and the gate share (ADR-0088 decision 6); the process steps and their figures follow ADR-0078.
"""
from __future__ import annotations

import calendar
import datetime as dt
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
    """`{number, unit, direction}` of the first number in `text` that is not a year (else the first),
    with its direction "below", "above" or "equal"; None when there is no number."""
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


_MONTH = (r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|"
          r"sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)")
#: ADR-0086 — a date as a goal writes it: ISO, "31 March 2027", "March 31, 2027", "(end of) March 2027".
_GOAL_DATE = re.compile(r"(?i)\b(\d{4}-\d{2}-\d{2}|\d{1,2}[./]\d{1,2}[./]\d{4}|\d{1,2}(?:st|nd|rd|th)?\s+" + _MONTH
                        + r"\.?,?\s+\d{4}|" + _MONTH + r"\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}|(?:end of\s+)?"
                        + _MONTH + r"\.?\s+\d{4}|(?:end of\s+)?q([1-4])\s*(?:/\s*)?(\d{4}))\b")
#: ADR-0086 note: a quarter is read as its last day, shown with the quarter it came from.
_QUARTER_END = {"1": "31 March", "2": "30 June", "3": "30 September", "4": "31 December"}
#: ADR-0086 note: a figure counts as the target only when a target word introduces it —
#: "to", "down to", a limit ("under", "at most" …) or "target (of)"; "by 30%", "by 5 points", "halve" are
#: changes relative to the baseline, never the target value, and the target is taught.
_TARGET_CUE = re.compile(r"(?:\bto|\btarget(?:\s+of)?|\bunder|\bbelow|\bless than|\blower than|\bat most|"
                         r"\bno more than|\bnot more than|\bup to|\bat least|\bover|\babove|\bmore than|"
                         r"\bgreater than|\bno less than)\s*(?:around|about|roughly|approximately|~)?\s*$")


def goal_targets(goal: Any, artifacts: dict[str, Any]) -> dict[str, Any]:
    """ADR-0086 (A8): what a confirmed goal states for the target, parsed in code —
    `target_value` a MetricValue (the goal's last figure, read as a limit, after any baseline figure:
    "from 23% to under 5%" is under 5 %) or None, and `target_date` the goal's date as an ISO calendar
    date (`calendar_date`), or None. The value counts only as `nodes_common._judged_in_code` would accept a
    typed target (G-120, ADR-0071): in the baseline's unit, and different from the baseline."""
    text = str(goal or "")
    date = _GOAL_DATE.search(text)
    rest = _GOAL_DATE.sub(" ", text)
    figures = [m for m in re.finditer(_NUMBER + _UNIT, rest.lower()) if not _is_year(m)]
    value = None
    start = figures[-2].end() if len(figures) > 1 else 0
    if figures and _TARGET_CUE.search(rest.lower()[start:figures[-1].start()]):
        mv = metric_value(rest[start:], target=True)
        unit = primary_unit(artifacts)
        baseline = as_metric(artifacts["baseline_estimate"], unit=unit) if artifacts.get("baseline_estimate") else None
        base_unit = unit or (baseline or {}).get("unit", "")
        if mv["value"] is not None and mv["unit"] and (not base_unit or mv["unit"] == base_unit) \
                and not (baseline and baseline.get("value") == mv["value"]):
            value = {**mv, "raw": text.strip()}
    # ADR-0088 decision 5: the date is stored as an ISO calendar date.
    found = calendar_date(date.group(0)) if date else None
    return {"target_value": value, "target_date": found[0] if found else None}


# ── ADR-0088 decision 5: one date parser ─────────────────────────────────────────────────────────────────

_MONTHS = {m: i for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
                                       "nov", "dec"), start=1)}


def _month(word: str) -> int:
    return _MONTHS[word.lower()[:3]]


def _long(d: dt.date) -> str:
    return f"{d.day} {calendar.month_name[d.month]} {d.year}"


def calendar_date(text: Any) -> Optional[tuple[str, str]]:
    """ADR-0088 decision 5 — THE date reader, for A8, element 9, the rubric's DEF-R09 and the report: the first
    date in `text` as (ISO, shown). Reads 2027-03-31, 31.03.2027 and 31/03/2027 (day first), "31 March 2027",
    "March 31, 2027", "March 2027" (the month's last day) and "Q1 2027" (the quarter's last day). `shown` is the
    Belt's form beside the unambiguous one: "31.03.2027 = 31 March 2027", "31 March 2027 (end of Q1 2027)". A
    year alone is no date: None."""
    m = _GOAL_DATE.search(str(text or ""))
    if not m:
        return None
    phrase = m.group(0).strip()
    low = re.sub(r"(?i)^end of\s+", "", phrase).replace(",", " ")
    try:
        if m.group(2):                                                   # Q1 2027
            year, q = int(m.group(3)), int(m.group(2))
            d = dt.date(year, q * 3, calendar.monthrange(year, q * 3)[1])
            return d.isoformat(), f"{_long(d)} (end of Q{q} {year})"
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", low):
            d = dt.date.fromisoformat(low)
        elif re.fullmatch(r"\d{1,2}[./]\d{1,2}[./]\d{4}", low):
            day, month, year = (int(x) for x in re.split(r"[./]", low))
            d = dt.date(year, month, day)
        else:
            words = re.findall(r"[A-Za-z]+|\d+", low)
            nums = [int(w) for w in words if w.isdigit()]
            month = next(_month(w) for w in words if not w.isdigit() and w.lower()[:3] in _MONTHS)
            year = next(n for n in nums if n > 999)
            days = [n for n in nums if n <= 31]
            if not days:                                                 # March 2027
                d = dt.date(year, month, calendar.monthrange(year, month)[1])
                return d.isoformat(), f"{_long(d)} (end of {calendar.month_name[month]} {year})"
            d = dt.date(year, month, days[0])
    except (ValueError, StopIteration):
        return None
    return d.isoformat(), (_long(d) if phrase == _long(d) else f"{phrase} = {_long(d)}")


def date_shown(stored: Any, words: Any = "") -> str:
    """A stored target date as the read-back shows it: the Belt's form from `words` when it reads as the
    same day, else the stored date written out."""
    stored_date = calendar_date(stored)
    said = calendar_date(words)
    if said and stored_date and said[0] == stored_date[0]:
        return said[1]
    return _long(dt.date.fromisoformat(stored_date[0])) if stored_date else str(stored or "")


# ── ADR-0088 "Element values parsed and checked in code" ─────────────────────────────────────────────────

#: Decision 1: an item marker the Belt writes — (1), 1., 1), a), "-", "•" — at a line start or after a space.
_ITEM = re.compile(r"(?:(?<=^)|(?<=\s))(?:\(\d{1,2}\)|\d{1,2}[.)](?=\s)|\(?[a-h]\)(?=\s)|[-•*](?=\s))\s*", re.M)
_NONE = re.compile(r"^\s*none(?: identified)?(?: at this stage)?\s*[.!]?\s*$", re.I)


def list_items(text: Any, label: str = "") -> list[str]:
    """ADR-0088 decision 1: the items of a list-shaped answer, as the Belt numbered them — split only at (1),
    1., 1), a), "-" or "•", never inside an item at a ';', a ',' or 'and'; with no marker, at line breaks; else
    one item. A leading `label` ("Issues and barriers:") is dropped; "none identified" is one item."""
    t = str(text or "").strip()
    if label:
        t = re.sub(r"^\s*" + re.escape(label) + r"\s*:\s*", "", t, flags=re.I)
    if not t:
        return []
    if _NONE.match(t):
        return [t.rstrip(".! ")]
    marks = list(_ITEM.finditer(t))
    if len(marks) >= 2:
        parts = [t[m.end():(marks[i + 1].start() if i + 1 < len(marks) else len(t))] for i, m in enumerate(marks)]
        head = t[:marks[0].start()].strip(" :")
        items = [p.strip(" ;,\n\t") for p in parts]
        return [x for x in items if x] if not head else [head, *[x for x in items if x]]
    lines = [x.strip(" -•\t") for x in t.split("\n") if x.strip()]
    return lines if len(lines) > 1 else [t]


def _same(a: Any, b: Any) -> bool:
    return " ".join(str(a or "").lower().split()).rstrip(".") == " ".join(str(b or "").lower().split()).rstrip(".")


def ctq_rows(rows: Any) -> list[dict[str, Any]]:
    """ADR-0088 decision 2: CTQ rows as the Belt stated them — rows with the same need and requirement become one
    row, their customers joined in the order given. A cross product of customers and needs collapses."""
    out: list[dict[str, Any]] = []
    for r in rows if isinstance(rows, list) else []:
        if not isinstance(r, dict):
            continue
        hit = next((o for o in out if _same(o.get("need"), r.get("need"))
                    and _same(o.get("requirement"), r.get("requirement"))), None)
        if hit is None:
            out.append(dict(r))
        elif r.get("customer") and not any(_same(c, r.get("customer")) for c in str(hit.get("customer") or "").split("; ")):
            hit["customer"] = "; ".join(x for x in (str(hit.get("customer") or ""), str(r["customer"])) if x)
    return out


def stated_ctqs(words: Any) -> list[str]:
    """The CTQs the Belt listed after a "CTQs:" label (or as a numbered list after it), by the list parser."""
    m = re.search(r"(?is)\bCTQs?\s*:\s*(.+)$", str(words or ""))
    if not m:
        return []
    body = m.group(1).strip()
    items = list_items(body)
    if len(items) == 1 and ";" in body:
        items = [x.strip() for x in body.split(";") if x.strip()]
    return items


def ctq_question(rows: Any, words: Any) -> str:
    """ADR-0088 decision 2: when the rows do not match the CTQs the Belt listed, the question the read-back asks
    before Confirm; empty when they match or the Belt listed none."""
    stated = stated_ctqs(words)
    rows = rows if isinstance(rows, list) else []
    if not stated or len(stated) == len(rows):
        return ""
    return (f"You listed {len(stated)} CTQ{'s' if len(stated) != 1 else ''}; the table has {len(rows)} "
            f"row{'s' if len(rows) != 1 else ''}. Which customer does each CTQ apply to?")


#: Decision 6: the 5W2H answers by the question the Belt is asked (the report's wording).
_FIVE_W_TWO_H = (("what", "what is going wrong"), ("where", "where"), ("when", "when, or since when"),
                 ("who", "who is affected"), ("why", "why it matters"), ("how", "how it shows up"),
                 ("how_much", "how much"))
_CHAMPION = re.compile(r"champion|sponsor", re.I)
_OWNER = re.compile(r"process owner|owner of the process|owns the process", re.I)
#: Training stated in any words — a need ("a half-day on data collection") or none; the grader judges the rest.
_TRAINING = re.compile(r"train|course|workshop|half[- ]day|full[- ]day|session|learn|coaching|"
                       r"none needed|nothing needed|no (?:\w+ )?needed|needs? no", re.I)


#: DEF-230 — the 5W2H labels a Belt writes, longest first so "how much" is never read as "how"; `steps` joins `where`.
_FIVE_W_LABELS: tuple[tuple[str, str], ...] = (
    ("how_much", r"how[\s_-]+much"),
    ("how", r"how\s+(?:it|the\s+problem|the\s+defect)\s+(?:shows|is\s+detected|is\s+noticed)(?:\s+up)?|how"),
    ("what", r"what(?:\s+is\s+going\s+wrong)?"), ("where", r"where"),
    ("when", r"when(?:,?\s+or\s+since\s+when)?|since\s+when"), ("who", r"who(?:\s+is\s+affected)?"),
    ("why", r"why(?:\s+it\s+matters)?"), ("steps", r"(?:the\s+)?(?:process\s+)?steps?(?:\s+where\s+it\s+shows)?"))
_FIVE_W_LABEL = re.compile(r"(?:^|(?<=[.;\n]))\s*(" + "|".join(f"(?P<{k}>{p})" for k, p in _FIVE_W_LABELS) + r")\s*:\s*",
                           re.I)
#: The keys a coach may give the 5W2H under (the report's wording), to the stored keys.
_FIVE_W_KEYS = {"how much": "how_much", "howmuch": "how_much", "how it shows up": "how", "how it shows": "how",
                "why it matters": "why", "what is going wrong": "what", "who is affected": "who"}


def five_w_two_h(words: Any) -> dict[str, str]:
    """DEF-230 (ADR-0093): the seven 5W2H answers from the Belt's labelled answer ("What: … Where: … How much: …"),
    read in code, each in the Belt's own words; the process steps the Belt names join `where` (R18). Empty unless at
    least four of the seven are labelled — an answer in prose is the coach's to structure."""
    text = str(words or "")
    hits = list(_FIVE_W_LABEL.finditer(text))
    out: dict[str, str] = {}
    for i, m in enumerate(hits):
        key = next(k for k, _ in _FIVE_W_LABELS if m.group(k))
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        line_end = text.find(chr(10), m.end())
        if line_end != -1:
            end = min(end, line_end)                  # one answer, one line: a later message is not part of it
        answer = text[m.end():end].strip().rstrip(".;").strip()
        if answer:
            out[key] = answer                         # a later message's answer corrects an earlier one
    steps = out.pop("steps", "")
    if steps and out.get("where"):
        out["where"] = f"{out['where']}; steps: {steps}"
    return out if len(out) >= 4 else {}


def five_w_two_h_store(words: Any, proposed: Any) -> dict[str, Any]:
    """DEF-230: the 5W2H a Confirm stores — the Belt's labelled answers (in code) where given, the coach's proposal
    (its keys read as the report labels them) for the rest; {} when neither gives one."""
    coach = {}
    for k, v in (proposed.items() if isinstance(proposed, dict) else []):
        key = re.sub(r"[\s-]+", " ", str(k).strip().lower())
        coach[_FIVE_W_KEYS.get(key, key.replace(" ", "_"))] = v
    return {**coach, **five_w_two_h(words)}


#: G-236 — the list elements whose uploaded table is read in code, one entry per row, every column kept.
TABLE_ELEMENTS: tuple[str, ...] = ("team",)
#: A team file's column for what the member does, when it has no `function` column.
_FUNCTION_COLUMNS = ("department", "job", "job_title", "title", "position")


def table_lines(text: Any) -> str:
    """G-236: a parsed table's rows as `upload.parsers._table_text` labels them ("name: … | role: …"), without
    its header line — the file's own words, every column, written in code."""
    lines = [x for x in str(text or "").splitlines() if x.strip()]
    return "\n".join(x for x in lines[1:] if ": " in x)


def readable_rows(text: Any) -> str:
    """G-296 (DEF-280): a file's labelled rows ("name: Katharina Huber | role: Project Sponsor | …") as the Belt reads
    them, one line each: the first column's value, a dash, the others in the file's order ("Katharina Huber — Project
    Sponsor, Head of Field Service Austria, 2 h per month"). Every other line stays as it is."""
    out = []
    for line in str(text or "").splitlines():
        parts = [_LABELLED.match(part) for part in line.split(" | ")]
        values = [v for v in ((m.group(1) or "").strip() for m in parts if m) if v]
        if len(parts) > 1 and values and all(parts):
            out.append(values[0] + (" — " + ", ".join(values[1:]) if values[1:] else ""))
        else:
            out.append(line)
    return "\n".join(out)


#: G-296: one labelled cell of a file's row, its value possibly empty ("department:").
_LABELLED = re.compile(r"^\s*[A-Za-z_][\w ]*:(?:\s(.*)|\s*)$")


def team_rows(text: Any) -> list[dict[str, str]]:
    """G-236: the team from an uploaded table's labelled lines ("name: … | role: … | training: …"), read in code —
    every column kept under its own key (lower case, spaces as underscores); a department or job title is the
    function when the file has no function column. Empty when the lines carry no names."""
    out = []
    for line in str(text or "").splitlines():
        row: dict[str, str] = {}
        for part in line.split(" | "):
            key, sep, val = part.partition(": ")
            if sep and key.strip() and val.strip():
                row[re.sub(r"\s+", "_", key.strip().lower())] = val.strip()
        if "function" not in row:
            row.update({"function": row[k] for k in _FUNCTION_COLUMNS if k in row and "function" not in row})
        if row.get("name"):
            out.append(row)
    return out


#: G-301 (DEF-264): a training line the Belt types to complete an uploaded team ("Training: Elena Gruber and Thomas
#: Wagner need a half-day on data collection; nobody else.").
_TRAINING_LINE = re.compile(r"(?im)^\s*training\s*:\s*(.+)$")
_NOBODY_ELSE = re.compile(r"(?i)\b(?:nobody|no one|no-one|none)\s+(?:else|for the others|for the rest)\b"
                          r"|\b(?:the )?others?\s*(?::|—|-)?\s*none\b")
_NEEDS = re.compile(r"(?i)^(?:(?:and|,|&)\s*)*(?:each\s+|both\s+)?(?:needs?|requires?|should get|get)\s+")
#: A typed line with no "Training:" label still states training when it names a member and says what they need
#: ("Elena Gruber and Thomas Wagner need half a day on data collection; the others none").
_TRAINING_CUE = re.compile(r"(?i)\bhalf an? (?:day|hour)\b|\b\d+\s*(?:days?|hours?)\s+(?:of|on)\b")


#: R-D (founder ruling 2026-10-27, R4's amendment): the scope's dimensions, in the order the card asks for them, and the
#: labels that name each in the Belt's or the read-back's words.
SCOPE_DIMENSIONS: tuple[tuple[str, str], ...] = (
    ("Process", r"process(?:es)?"),
    ("Places", r"places?|sites?|departments?|countr(?:y|ies)|locations?|regions?"),
    ("Products or services", r"products?(?:\s+or\s+services?)?|services?"),
    ("Customers", r"customers?|segments?|clients?"),
    ("Systems", r"systems?"),
)
_SCOPE_LABEL = re.compile(r"(?i)(?:^|(?<=[;\n.])\s*|(?<=,)\s+)(" + "|".join(p for _, p in SCOPE_DIMENSIONS)
                          + r")\s*:\s*")


def _scope_parts(text: Any) -> dict[str, str]:
    """{dimension: its words} for each labelled part of one half of the scope ("Process: …; Places: …")."""
    said = str(text or "")
    found = list(_SCOPE_LABEL.finditer(said))
    out: dict[str, str] = {}
    for i, m in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(said)
        dim = next(name for name, pattern in SCOPE_DIMENSIONS if re.fullmatch(pattern, m.group(1), re.I))
        piece = said[m.end():end].strip(" ;.\n")
        out[dim] = f"{out[dim]}; {piece}" if dim in out and piece else piece or out.get(dim, "")
    return out


def scope_rows(in_scope: Any, out_scope: Any) -> list[list[str]]:
    """R-D: the scope as one row per dimension, [dimension, in, out], in the card's order — from the labelled parts the
    read-back stores ("Process: from complaint logged to closed; Places: Vienna, Linz"); "—" for a half a line leaves
    empty; [] when neither half names a dimension (an answer from before R-D shows as one line)."""
    inside, outside = _scope_parts(in_scope), _scope_parts(out_scope)
    return [[name, inside.get(name) or "—", outside.get(name) or "—"] for name, _ in SCOPE_DIMENSIONS
            if name in inside or name in outside]


def uploaded_team(words: Any, proposed: Any) -> list[dict[str, str]]:
    """G-236 (DEF-229): an uploaded team as a Confirm stores it — the file's rows, read in code from its labelled lines
    (every column, training included), never the coach's re-typing of them; G-301 (DEF-264): a training line the Belt
    typed goes to each named member's own column. R-B (DEF-268): a person the Belt typed to complete the file — its
    draft lacked a champion or a process owner — is added from the read-back's own value (`proposed`), but only one
    whose name the Belt's words carry: the file's rows stay as the file states them."""
    rows = with_typed_training(team_rows(words), words)
    named = {str(r.get("name") or "").strip().lower() for r in rows}
    said = str(words or "")
    typed = [m for m in (proposed if isinstance(proposed, list) else []) if isinstance(m, dict)
             and (name := str(m.get("name") or "").strip()) and name.lower() not in named and name in said]
    return rows + typed


def with_typed_training(rows: list[dict[str, str]], words: Any) -> list[dict[str, str]]:
    """G-301 (DEF-264, founder test 2026-10-27 #28): the team rows with a typed training line read into each named
    member's own `training` — the clause that names them, without their names ("a half-day on data collection");
    "nobody else" gives every member not named "none". The line is labelled "Training: …", or a typed line (never a
    file's labelled row) that names a member and states training. A member is named by their full name, or by a
    first name no other member shares. Rows the line does not touch keep what the file gave them."""
    out = [dict(r) for r in rows]
    firsts = [str(r.get("name") or "").split()[0].lower() for r in out if str(r.get("name") or "").split()]

    def names(r: dict[str, str]) -> list[str]:
        full = str(r.get("name") or "").strip()
        first = full.split()[0] if full.split() else ""
        return [full] + ([first] if first and firsts.count(first.lower()) == 1 else [])

    def names_someone(line: str) -> bool:
        return any(n and re.search(r"(?<!\w)" + re.escape(n) + r"(?!\w)", line, re.I) for r in out for n in names(r))
    text = str(words or "")
    typed = [x.strip() for x in text.splitlines() if x.strip() and " | " not in x and not _TRAINING_LINE.match(x)
             and not x.strip().lower().startswith("name:") and names_someone(x)
             and (_TRAINING.search(x) or _TRAINING_CUE.search(x))]
    for line in [*_TRAINING_LINE.findall(text), *typed]:
        named: set[int] = set()
        for clause in (c.strip() for c in re.split(r"[;.]\s*", line) if c.strip()):
            hits = [i for i, r in enumerate(out) if any(
                n and re.search(r"(?<!\w)" + re.escape(n) + r"(?!\w)", clause, re.I) for n in names(r))]
            if not hits:
                continue
            what = clause
            for i in hits:
                for n in names(out[i]):
                    what = re.sub(r"(?<!\w)" + re.escape(n) + r"(?!\w)", " ", what, flags=re.I)
            what = _NEEDS.sub("", " ".join(what.split()).strip(" ,&")).strip(" ,")
            for i in hits:
                out[i]["training"] = what
                named.add(i)
        if _NOBODY_ELSE.search(line):
            for i, r in enumerate(out):
                if i not in named and not str(r.get("training") or "").strip():
                    r["training"] = "none"
    return out


def missing_parts(field: str, value: Any) -> list[str]:
    """ADR-0088 decision 6: the required parts of an element R7 names that `value` lacks, in the Belt's words —
    the seven 5W2H answers (DEF-R04); a champion and a process owner (DEF-R02; R-B, 2026-10-27: training is not a Define
    criterion); customers, needs
    and at least one measurable CTQ (DEF-R03); a calendar target date (decision 5); when the saving shows (G-255).
    Empty when complete, or for an element with no parts to check."""
    def text(v: Any) -> str:
        return " ".join(str(x) for x in v.values()) if isinstance(v, dict) else str(v or "")
    if field == "problem_5w2h" and isinstance(value, dict):
        blank = [name for key, name in _FIVE_W_TWO_H if not text(value.get(key)).strip()]
        return [f"the 5W2H answer{'s' if len(blank) > 1 else ''} to {' and '.join(blank)}"] if blank else []
    if field == "team" and isinstance(value, list):
        everyone = " ".join(text(e) for e in value)
        return [part for part, pattern in (("a champion", _CHAMPION), ("a process owner", _OWNER))
                if not pattern.search(everyone)]
    if field == "critical_to_quality" and isinstance(value, list):
        rows = [r for r in value if isinstance(r, dict)]
        out = [part for part, key in (("the customer of each CTQ", "customer"), ("the need behind each CTQ", "need"))
               if not rows or any(not text(r.get(key)).strip() for r in rows)]
        if not any(re.search(r"\d", text(r.get("requirement"))) for r in rows):
            out.append("at least one CTQ as a measurable requirement (with a number)")
        return out
    if field == "target_date" and value and calendar_date(value) is None:
        return ["a calendar date for the target (for example 31 March 2027)"]           # decision 5
    if field == "benefits_analysis" and isinstance(value, dict) and not realisation_stated(value):
        return ["when the saving shows: by period, or from a start date, sustained"]    # G-255
    return []


#: G-255: when the saving shows — a schedule by period, or a start with the saving
#: sustained or ongoing.
_BY_PERIOD = re.compile(r"\b(?:a|per|each|every)\s+(?:week|month|quarter|year)\b"
                        r"|\b(?:weekly|monthly|quarterly|annually|yearly)\b", re.I)
_START = re.compile(r"\b(?:from|starting|beginning|as of|after)\b|\bQ[1-4]\b|\b20\d\d\b"
                    r"|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", re.I)
_SUSTAINED = re.compile(r"\bsustain|\bon-?going\b|\bevery year\b|\brecurr", re.I)


#: ADR-0096 decision 1 (DEF-260): the soft benefits the Belt labels ("Soft benefit: fewer escalations to account managers,
#: seen in the monthly escalation count"), each split from how it will be seen.
_SOFT_LABEL = re.compile(r"(?i)\bsoft benefits?\s*:\s*")
_NEXT_LABEL = re.compile(r"(?i)\n|\b(?:hard benefits?|cost of the gap|finance contact|impact|realisation)\s*:")
_SEEN = re.compile(r"(?i)\s*(?:\(|,|;|—|-)?\s*\b(?:seen|visible|shown|measured|tracked|counted)\s+(?:in|by|through|via|as)\s+")
_NONE_SOFT = re.compile(r"(?i)^\s*(?:none|none identified|no soft benefits?)\b")


#: ADR-0096 decision 1: the conscious answer that there are no soft benefits, kept as one entry.
SOFT_NONE = "None identified"


def soft_benefits_stated(benefits: Any) -> bool:
    """DEF-289 (R7's amendment ACCEPTED 2026-10-29, ADR-0096 decision 3): the soft benefits are stated, each with how
    it will be seen, or the Belt said consciously that there are none — that answer never blocks (founder,
    2026-10-29)."""
    b = benefits if isinstance(benefits, dict) else {}
    items = [s for s in b.get("soft_benefits") or [] if isinstance(s, dict) and str(s.get("benefit") or "").strip()]
    return bool(items) and all(s["benefit"] == SOFT_NONE or str(s.get("indicator") or "").strip() for s in items)


def soft_benefits(words: Any) -> list[dict[str, str]]:
    """ADR-0096 decision 1 (DEF-260, founder test 2026-10-27 #52): `[{benefit, indicator}]` from the Belt's labelled
    soft benefits, in the Belt's words — never converted into money. "None identified" is a conscious answer, kept as
    one entry. Empty when the Belt labelled none."""
    text = str(words or "")
    out: list[dict[str, str]] = []
    for label in _SOFT_LABEL.finditer(text):
        rest = text[label.end():]
        stop = _NEXT_LABEL.search(rest)
        part = rest[:stop.start()] if stop else rest
        if _NONE_SOFT.match(part):
            out.append({"benefit": SOFT_NONE, "indicator": ""})
            continue
        for item in list_items(part) or [part]:
            item = item.strip().rstrip(".").strip()
            if not item:
                continue
            split = _SEEN.search(item)
            benefit = (item[:split.start()] if split else item).strip(" ,;(—-")
            indicator = (item[split.end():] if split else "").strip(" .)")
            if benefit:
                out.append({"benefit": benefit, "indicator": indicator})
    return out


def realisation_stated(benefits: Any) -> bool:
    """G-255: the benefits' `realisation` criterion, read in code — in Define a schedule by
    period meets it, and so does a start date with the saving sustained or ongoing (said in the schedule or as the
    impact type)."""
    b = benefits if isinstance(benefits, dict) else {}
    when = str(b.get("realisation_schedule") or "")
    if _BY_PERIOD.search(when):
        return True
    return bool(_START.search(when)) and bool(_SUSTAINED.search(f"{when} {b.get('impact_type') or ''}"))


#: Decision 7: a goal named where the problem is described — a goal word, or a target cue before a figure.
_GOAL_WORDS = re.compile(r"\b(?:target|goal|objective|aim(?:ing)?\s+(?:for|to|at)|we want to (?:reach|get|bring|reduce|cut))\b"
                         r"|\b(?:reduce|cut|bring|get)\b[^.;]{0,40}?\b(?:to|under|below)\s*\d", re.I)


def goal_named(text: Any) -> str:
    """ADR-0088 decision 7: the goal phrase a 5W2H answer or a problem statement carries, or "". The problem
    states the pain as it shows up today; the goal is element 7 (R7, `no-cause-no-fix`)."""
    m = _GOAL_WORDS.search(str(text or ""))
    return m.group(0).strip() if m else ""


def goal_sentence(text: Any) -> str:
    """G-257 (DEF-098): the sentence of an answer that states a goal with a figure — a goal named (`goal_named`) and a
    number — or "". An answer for another element that carries one offers it to the goal statement."""
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", str(text or "")):
        if goal_named(sentence) and re.search(r"\d", sentence):
            return sentence.strip()
    return ""


def five_w_two_h_question(store: Any) -> str:
    """ADR-0088 decision 7: when the seventh answer (`how`) or the composed statement carries a goal, the
    question the read-back asks before Confirm; empty otherwise."""
    store = store if isinstance(store, dict) else {}
    how = (store.get("problem_5w2h") or {}).get("how") if isinstance(store.get("problem_5w2h"), dict) else None
    if goal_named(how) or goal_named(store.get("problem_statement")):
        return ("The problem statement describes the problem as it shows up today; the goal comes later, at "
                "the goal statement. How does the problem show up — how is it detected?")
    return ""


def _is_year(m: "re.Match[str]") -> bool:
    """G-135: a four-digit 1900-2099 with no unit of its own is a year — "January to June 2026" —
    never a baseline or a target."""
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


#: R-G: a step time as a Belt writes it — "10 min", "2 h", "4 working days", "1.5 hours".
_STEP_TIME = re.compile(r"(?i)\d+(?:[.,]\d+)?\s*(?:min(?:ute)?s?|h(?:ou)?rs?|h\b|(?:working |business )?days?|weeks?)\b")


def has_step_times(text: Any) -> bool:
    """R-G: whether an answer gives step times — at least two — so the SIPOC's fourth part need not be asked."""
    return len(_STEP_TIME.findall(str(text or ""))) >= 2


def sipoc_steps(text: Any) -> list[str]:
    """R-G: the main steps the Belt gave in the SIPOC's first part — one per line, numbered item, arrow or semicolon (a
    comma list when nothing else separates them) — for the fourth part's card to list."""
    said = str(text or "").strip()
    parts = re.split(r"\s*(?:→|->|=>|;|\n)\s*|\s*(?:^|\s)\d+[.)]\s+", said)
    steps = [p.strip(" .,") for p in parts if p and p.strip(" .,")]
    if len(steps) < 2:
        steps = [p.strip(" .") for p in said.split(",") if p.strip(" .")]
    return steps[:12]


def missing_columns(value: Any) -> list[str]:
    """The SIPOC columns `value` lacks (all six when it is not a mapping)."""
    if not isinstance(value, dict):
        return list(SIPOC_KEYS)
    # ADR-0078: `process_steps` is a list of step entries; an empty list is not a column.
    return [k for k in SIPOC_KEYS if not (value.get(k) if isinstance(value.get(k), (list, dict))
                                          else str(value.get(k) or "").strip())]


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
#: reading it as an estimate would fail DEF-R05 (real data, not a best guess).
_ESTIMATE = re.compile(
    r"(?<![a-zäöüß])(rough(?:ly)?|estimate[ds]?|estimated|estimation|guess(?:ed|timate)?|"
    r"geschätzt|schätzung|schätzen|grob)(?![a-zäöüß])", re.I)


def normal_unit(unit: str) -> str:
    """One comparable word for a unit ("Prozent" -> "%", "Tage" -> "days"); unknown kept as written."""
    u = unit_of(unit)
    return _UNIT_OF_WORD.get(u, u)


def is_estimate(text: str) -> bool:
    """The Belt marked the figure as an estimate ("roughly", "estimated", "geschätzt" …); a rounding word
    ("about", "around") does not."""
    return bool(_ESTIMATE.search(text or ""))


#: G-245: the goal's verb names the side of the baseline the target lies on.
_GOAL_DOWN = re.compile(r"(?<![a-zäöüß])(reduce|reducing|cut|cutting|lower|lowering|decrease|decreasing|shorten|"
                        r"halve|drop|bring down|fewer|less)(?![a-zäöüß])", re.I)
_GOAL_UP = re.compile(r"(?<![a-zäöüß])(increase|increasing|raise|raising|grow|growing|lift|boost|double|more|"
                      r"at least)(?![a-zäöüß])", re.I)


def wrong_side(baseline: Optional[float], target: dict[str, Any], goal: Any = "") -> Optional[str]:
    """G-245 (SKILL.md `direction`): why the target lies on the wrong side of the baseline, or None. The side
    is the target's own limit ("under" / "at least") or, with none, the goal's verb ("reduce" / "increase"); with
    neither, or with no number, nothing is refused. The ONE check, for the element and the gate."""
    value = target.get("value")
    if baseline is None or value is None:
        return None
    limit = target.get("direction")
    goal_text = str(goal or "")
    side = ("down" if limit == "<=" else "up" if limit == ">=" else
            "down" if _GOAL_DOWN.search(goal_text) and not _GOAL_UP.search(goal_text) else
            "up" if _GOAL_UP.search(goal_text) and not _GOAL_DOWN.search(goal_text) else None)
    if side == "down" and value >= baseline:
        return f"the target ({value:g}) is not below the baseline ({baseline:g}), although the goal brings it down"
    if side == "up" and value <= baseline:
        return f"the target ({value:g}) is not above the baseline ({baseline:g}), although the goal raises it"
    return None


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


#: The units written singular after a 1 — time and count words; a unit like "%" or "EUR" is never touched.
_PLURAL_UNITS = frozenset({"seconds", "minutes", "hours", "days", "weeks", "months", "years", "invoices", "orders",
                           "items", "cases", "calls", "tickets", "errors", "defects", "units", "runs"})


def metric_text(value: Any) -> str:
    """A MetricValue as the Belt reads it: "at most 5%", "23% (an estimate)", "12 days"; a value that
    is not a number yet says so and shows the Belt's words."""
    mv = as_metric(value)
    if mv["value"] is None:
        return f"not a number yet — {mv['raw']}" if mv["raw"] else "not given"
    unit = str(mv["unit"] or "")
    if mv["value"] == 1 and unit.endswith("s") and unit.split()[-1] in _PLURAL_UNITS:
        unit = unit[:-1]                    # "1 day", never "1 days"
    figure = f"{mv['value']:g}{'' if unit in ('', '%') else ' '}{unit}".strip()
    words = _WORDS.get(mv.get("direction") or "", "")
    return (f"{words} {figure}".strip() + (" (an estimate)" if mv.get("is_estimate") else ""))


def limit_phrase(value: Any) -> str:
    """DEF-221 (ADR-0071): the Belt's own words for a target's limit — "under 10%" — found in the
    MetricValue's raw words around its figure, with the limit word before it. "" when the words carry no limit word
    or say it as the read-back does ("at most 10%")."""
    mv = as_metric(value, target=True)
    if mv["value"] is None or not mv.get("direction") or mv["direction"] == "=":
        return ""
    number = f"{mv['value']:g}".replace(".", "[.,]")
    words = "|".join(re.escape(w) for w in sorted((*_BELOW, *_ABOVE), key=len, reverse=True))
    m = re.search(rf"(?<![A-Za-zÄÖÜäöüß])({words})\s*{number}(?!\d)\s*(%|per\s?cent|percent|prozent|[A-Za-zÄÖÜäöüß]+)?",
                  str(mv.get("raw") or ""), re.I)
    if not m:
        return ""
    phrase = " ".join(m.group(0).split())
    return "" if phrase.lower().replace(" ", "") == metric_text(mv).lower().replace(" ", "") else phrase


def metric_name(name: Any) -> str:
    """DEF-223 (G-224, C1): a metric's name as the Belt reads it — a registry id ("late_payment_rate") becomes words
    ("Late payment rate"); a name already written as words is kept as written. The id stays the key in code."""
    text = str(name or "").strip()
    if "_" in text or (text and text == text.lower() and " " not in text):
        words = text.replace("_", " ").strip()
        return words[:1].upper() + words[1:]
    return text


def primary_unit(artifacts: Any) -> str:
    """The primary metric's unit, from the registry (its first entry)."""
    reg = (artifacts or {}).get("metric_definitions") or []
    return normal_unit(str(reg[0].get("unit") or "")) if reg and isinstance(reg[0], dict) else ""


# ══ ADR-0078 (DEF-084, DEF-085): the as-is process with its performance, per step ═══════════
#
# Each step of `process_map_sipoc["process_steps"]` is an entry {id, name, duration {avg, min, max},
# runs_per_period, problems [{note, said_by}]}; the whole process is `process_performance`
# {lead_time, runs_per_period}. Every figure is a MetricValue read here, by `metric_value` — the
# coach proposes the Belt's words, code reads the number (ADR-0071 point 2).

#: The step-entry keys and the whole-process keys (ADR-0078 points 1 and 2).
STEP_KEYS: tuple[str, ...] = ("id", "name", "duration", "runs_per_period", "problems")
DURATION_KEYS: tuple[str, ...] = ("avg", "min", "max")
PROCESS_PERFORMANCE_KEYS: tuple[str, ...] = ("lead_time", "runs_per_period")
#: A period a frequency is counted in, English and German.
_PERIODS: dict[str, tuple[str, ...]] = {
    "per hour": ("hour", "hourly", "stunde", "stündlich"),
    "per day": ("day", "daily", "tag", "täglich"),
    "per week": ("week", "weekly", "woche", "wöchentlich"),
    "per month": ("month", "monthly", "monat", "monatlich"),
    "per year": ("year", "yearly", "annually", "jahr", "jährlich"),
}
_STEP_SPLIT = re.compile(r"\s*(?:→|->|=>|;|,|\n)\s*")
_WORD = re.compile(r"[a-zäöüß0-9]+")


def period_value(text: Any) -> dict[str, Any]:
    """A frequency as a MetricValue whose unit is its period ("per week"): "about 40 a week",
    "200 invoices per day", "3x monthly". No period named: the unit is what the parser read."""
    if isinstance(text, dict) and "raw" in text and "value" in text:
        return dict(text)
    mv = metric_value(text)
    low = str(text or "").lower()
    for unit, words in _PERIODS.items():
        if any(re.search(r"(?<![a-zäöüß])" + re.escape(w) + r"(?![a-zäöüß])", low) for w in words):
            return {**mv, "unit": unit}
    return mv


#: ADR-0088 decision 4: the duration units, longest spelling first; "days" with no kind is asked in the read-back.
_DURATION_UNITS: tuple[tuple[str, str], ...] = (
    (r"working\s+days?|business\s+days?|work\s*days?|arbeitstage?n?|wd", "working days"),
    (r"calendar\s+days?|kalendertage?n?", "calendar days"),
    (r"minutes?|mins?|minuten", "minutes"), (r"hours?|hrs?|h|stunden?", "hours"),
    (r"days?|tage?n?", "days"), (r"weeks?|wks?|wochen?", "weeks"), (r"months?|monate?n?", "months"))
_DURATION = re.compile(r"(?i)" + _NUMBER + r"(?:\s*(?:–|-|to|bis)\s*" + _NUMBER + r")?\s*("
                       + "|".join(p for p, _ in _DURATION_UNITS) + r")\b")
_SAME_DAY = re.compile(r"(?i)\bsame[- ]day\b|\bam selben tag\b")


def _duration_unit(word: str) -> str:
    return next(u for p, u in _DURATION_UNITS if re.fullmatch(r"(?i)" + p, word.strip()))


def duration_range(text: Any) -> Optional[tuple[dict[str, Any], dict[str, Any]]]:
    """ADR-0088 decision 4: a range "1–6 days" as its (min, max) MetricValues; None when `text` is no range."""
    raw = str(text or "").strip()
    m = _DURATION.search(raw)
    if not m or m.group(2) is None:
        return None
    unit = _duration_unit(m.group(3))
    def mv(n: str) -> dict[str, Any]:
        return {"value": float(n.replace(",", ".")), "unit": unit, "direction": None,
                "is_estimate": is_estimate(raw), "raw": raw}
    return mv(m.group(1)), mv(m.group(2))


def duration_value(text: Any) -> dict[str, Any]:
    """ADR-0088 decision 4 — THE duration reader: a duration as a MetricValue in minutes, hours, working days,
    calendar days, days (kind not said), weeks or months; "same day" is 0 days. A stored MetricValue whose
    unit is no duration unit ("working", G-186) is read again from its words."""
    if isinstance(text, dict) and "raw" in text and "value" in text:
        if text.get("unit") in {u for _, u in _DURATION_UNITS} or not text.get("raw"):
            return dict(text)
        text = text["raw"]
    raw = str(text or "").strip()
    m = _DURATION.search(raw)
    if m:
        return {"value": float(m.group(1).replace(",", ".")), "unit": _duration_unit(m.group(3)),
                "direction": None, "is_estimate": is_estimate(raw), "raw": raw}
    if _SAME_DAY.search(raw):
        return {"value": 0.0, "unit": "days", "direction": None, "is_estimate": is_estimate(raw), "raw": raw}
    return metric_value(raw)


#: Minutes per duration unit, to order a step's times written in different units (a working day as 8 hours).
_MINUTES = {"minutes": 1, "hours": 60, "working days": 480, "days": 1440, "calendar days": 1440,
            "weeks": 10080, "months": 43200}


def _in_minutes(mv: Any) -> Optional[float]:
    if not isinstance(mv, dict) or mv.get("value") is None or mv.get("unit") not in _MINUTES:
        return None
    return float(mv["value"]) * _MINUTES[mv["unit"]]


def duration_questions(sipoc: Any) -> list[str]:
    """ADR-0088 decision 4: what the read-back asks about the step times before Confirm — never an error:
    a step's shortest above its average or its average above its longest; days with no kind ("working or
    calendar days?"); working and calendar days mixed; the steps' averages against the stated end-to-end
    lead time, when they differ by more than 25 %."""
    if not isinstance(sipoc, dict):
        return []
    asks: list[str] = []
    steps = process_steps(sipoc.get("process_steps"))
    for s in steps:
        d = s["duration"]
        lo, avg, hi = (_in_minutes(d.get(k)) for k in ("min", "avg", "max"))
        if (lo is not None and avg is not None and lo > avg) or (avg is not None and hi is not None and avg > hi) \
                or (lo is not None and hi is not None and lo > hi):
            asks.append(f"For \"{s['name']}\" the shortest, average and longest times are not in order — which is right?")
    perf = process_performance(sipoc.get("process_performance"))
    # "Same day" (0 days) has no kind of day; every other figure names its unit.
    units = {v["unit"] for s in steps for v in s["duration"].values() if v.get("value")}
    units |= {perf["lead_time"]["unit"]} if perf.get("lead_time", {}).get("value") else set()
    if "days" in units:
        asks.append("Are the days working days or calendar days?")
    if {"working days", "calendar days"} <= units:
        asks.append("Some times are in working days and some in calendar days — which should they all be in?")
    averages = [s["duration"]["avg"] for s in steps if s["duration"].get("avg", {}).get("value") is not None]
    lead = perf.get("lead_time")
    if lead and lead.get("value") and averages:
        total = _steps_total(averages, lead)
        if total is not None and abs(total - lead["value"]) > 0.25 * lead["value"]:
            asks.append(f"The steps add up to {round(total, 1):g} {lead['unit']}, you said {lead['value']:g} "
                        f"{lead['unit']} from start to end — is there waiting time between the steps?")
    return asks


#: G-332 (DEF-259): the units a step sum converts across — one kind of day with the minutes and hours of a working
#: day, or calendar days with weeks and months. "Days" of no kind is never converted: its question is asked first.
_SUMMABLE = (frozenset({"minutes", "hours", "working days"}),
             frozenset({"minutes", "hours", "calendar days", "weeks", "months"}))


def _steps_total(averages: list[dict[str, Any]], lead: dict[str, Any]) -> Optional[float]:
    """The steps' averages added up in the lead time's unit: as they are when they share it; converted when they mix
    units that convert (G-332, founder test 2026-10-27 #60: "about 15 minutes" + 4 working days against 8 working
    days); None when they mix units that do not."""
    units = {a["unit"] for a in averages if a["value"]} | {lead["unit"]}
    if len(units) == 1:
        return float(sum(a["value"] for a in averages))
    if not any(units <= s for s in _SUMMABLE):
        return None
    minutes = [_in_minutes(a) for a in averages]
    return sum(m for m in minutes if m is not None) / _MINUTES[lead["unit"]]


def _step_name(entry: Any) -> str:
    if isinstance(entry, dict):
        return str(entry.get("name") or entry.get("step") or "").strip()
    return str(entry or "").strip()


def _key(name: str) -> str:
    return " ".join(_WORD.findall(name.lower()))


def _problems(value: Any) -> list[dict[str, str]]:
    """`[{note, said_by}]` from what the coach proposed: a list of entries or of notes, or one note."""
    items = value if isinstance(value, list) else ([value] if value else [])
    out = []
    for p in items:
        note = str((p.get("note") or p.get("problem") or "") if isinstance(p, dict) else p).strip()
        if note:
            said = str((p.get("said_by") or p.get("who") or "") if isinstance(p, dict) else "").strip()
            out.append({"note": note, "said_by": said})
    return out


def process_steps(value: Any, prior: Any = None) -> list[dict[str, Any]]:
    """The SIPOC's steps as entries (ADR-0078 point 1) — from entries, from a list of names, or from
    the Belt's text ("Receive → Approve → Pay"). Ids are stable: a step whose name matches a step of
    `prior` keeps its id; a new step takes the next free number."""
    if isinstance(value, str):
        raw: list[Any] = [p for p in _STEP_SPLIT.split(value) if p.strip()]
    elif isinstance(value, list):
        raw = list(value)
    else:
        raw = []
    before = {_key(_step_name(e)): str(e.get("id")) for e in (prior if isinstance(prior, list) else [])
              if isinstance(e, dict) and e.get("id")}
    taken = {i for i in before.values()}
    used: set[str] = set()

    def next_id() -> str:
        n = 1
        while f"S{n}" in taken or f"S{n}" in used:
            n += 1
        return f"S{n}"
    out = []
    for e in raw:
        name = _step_name(e)
        if not name:
            continue
        sid = str(e.get("id") or "") if isinstance(e, dict) else ""
        sid = before.get(_key(name)) or (sid if sid and sid not in used else "") or next_id()
        used.add(sid)
        d = e if isinstance(e, dict) else {}
        dur: dict[str, Any] = d["duration"] if isinstance(d.get("duration"), dict) else {}
        out.append({"id": sid, "name": name,
                    "duration": {k: duration_value(dur[k]) for k in DURATION_KEYS if dur.get(k) not in (None, "")},
                    **({"runs_per_period": period_value(d["runs_per_period"])}
                       if d.get("runs_per_period") not in (None, "") else {}),
                    "problems": _problems(d.get("problems"))})
    return out


def process_performance(value: Any) -> dict[str, Any]:
    """`{lead_time, runs_per_period}` as MetricValues (ADR-0078 point 2); a key not given is left out."""
    v = value if isinstance(value, dict) else {}
    out: dict[str, Any] = {}
    if v.get("lead_time") not in (None, ""):
        out["lead_time"] = duration_value(v["lead_time"])
    if v.get("runs_per_period") not in (None, ""):
        out["runs_per_period"] = period_value(v["runs_per_period"])
    return out


def sipoc_with_performance(value: Any, prior: Any = None) -> Any:
    """The SIPOC a Confirm stores: its steps as entries with stable ids against `prior` (the SIPOC
    confirmed before), its whole-process figures read in code. Anything that is not a SIPOC
    mapping is returned as it is."""
    if not isinstance(value, dict):
        return value
    out = dict(value)
    before = prior.get("process_steps") if isinstance(prior, dict) else None
    if not isinstance(before, list) and isinstance(prior, dict):
        before = process_steps(before)
    out["process_steps"] = process_steps(value.get("process_steps"), before)
    for s in out["process_steps"]:
        # ADR-0088 decision 4: a range given as the step's time ("1–6 days") is its shortest and longest.
        found = duration_range((s["duration"].get("avg") or {}).get("raw"))
        if found and not s["duration"].get("min") and not s["duration"].get("max"):
            s["duration"] = {"min": found[0], "max": found[1]}
    perf = process_performance(value.get("process_performance"))
    if perf:
        out["process_performance"] = perf
    else:
        out.pop("process_performance", None)
    return out


def step_names(sipoc: Any) -> list[str]:
    """The step names of a stored SIPOC — entries or the old text form (ADR-0078 point 6)."""
    steps = sipoc.get("process_steps") if isinstance(sipoc, dict) else None
    return [s["name"] for s in process_steps(steps)]


def _matches(named: str, step: str) -> bool:
    """ADR-0078 point 5: case and punctuation ignored; one contains the other, or they share a word
    of five or more letters."""
    a, b = _key(named), _key(step)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    return bool({w for w in a.split() if len(w) >= 5} & {w for w in b.split() if len(w) >= 5})


#: A location written "from → to" (ADR-0078's note): an arrow between its two ends.
_RANGE_ARROW = re.compile(r"\s*(?:→|->|=>)\s*")


def _found(name: str, steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The steps one named step matches, by the rules in order: a step the name contains or that contains it;
    only when none does, a step that shares a word of five or more letters — "Approve invoice" is not also
    "Receive invoice"."""
    a = _key(name)
    return [s for s in steps if a and (a in _key(s["name"]) or _key(s["name"]) in a)] \
        or [s for s in steps if _matches(name, s["name"])]


def located_steps(problem_steps: Any, sipoc: Any) -> dict[str, Any]:
    """R18 (ADR-0078 point 5 and its note): where the problem statement places the
    problem in the process — THE matching; `link_mismatch` and the drawn flow's marks both read it.

    A "from → to" location (one arrow between two ends) is every step from its start step to its end step:
    each end is matched by the rules of `_found`, and an end that matches no step, or more than one, is
    returned in `ends` (never a guess). Otherwise each named step is matched on its own.

    Returns `{"located": [step ids, in process order], "range": True/False, "unmatched": [names],
    "ends": [{"end": "start" | "end", "name", "found": [step names]}], "found_by_name": [(name, [steps])]}`."""
    steps = process_steps(sipoc.get("process_steps") if isinstance(sipoc, dict) else None)
    parts = problem_steps if isinstance(problem_steps, list) else [problem_steps]
    texts = [str(p).strip() for p in parts if str(p or "").strip()]
    ranged = [t for t in texts if len([x for x in _RANGE_ARROW.split(t) if x.strip()]) == 2]
    if len(texts) == 1 and ranged:
        start, end = (x.strip() for x in _RANGE_ARROW.split(ranged[0]) if x.strip())
        ends, at = [], []
        for which, name in (("start", start), ("end", end)):
            found = _found(name, steps)
            if len(found) == 1:
                at.append(steps.index(found[0]))
            else:
                ends.append({"end": which, "name": name, "found": [s["name"] for s in found]})
        located = [s["id"] for s in steps[min(at):max(at) + 1]] if len(at) == 2 else []
        return {"located": located, "range": True, "unmatched": [], "ends": ends, "found_by_name": []}
    named = [n for t in texts for n in _STEP_SPLIT.split(t) if n.strip()] if not isinstance(problem_steps, list) \
        else texts
    by_name = [(n, _found(n, steps)) for n in named]
    hit = {s["id"] for _, found in by_name for s in found}
    return {"located": [s["id"] for s in steps if s["id"] in hit], "range": False,
            "unmatched": [n for n, found in by_name if not found], "ends": [], "found_by_name": by_name}


def link_mismatch(problem_steps: Any, sipoc: Any) -> dict[str, Any]:
    """R18, both directions (ADR-0078 point 5): `unmatched` — a step the problem names that matches
    no step; `ends` — an end of a "from → to" location that matches no step or more than one; `quiet` — a
    located step with no problem notes; `ignored` — a step with problem notes outside the located steps.
    Empty lists when the two agree. The matching is `located_steps`'. DEF-293 (R17 amended, founder 2026-10-29: the
    problems are optional): a SIPOC with no problem notes at all has no `quiet` step — none were given, so none is
    asked for."""
    steps = process_steps(sipoc.get("process_steps") if isinstance(sipoc, dict) else None)
    where = located_steps(problem_steps, sipoc)
    hit = set(where["located"])
    if not any(s["problems"] for s in steps):
        quiet: list[str] = []
    elif where["range"]:
        inside = [s for s in steps if s["id"] in hit]
        quiet = [s["name"] for s in inside] if inside and not any(s["problems"] for s in inside) else []
    else:
        quiet = [s["name"] for _, found in where["found_by_name"] if found and not any(s["problems"] for s in found)
                 for s in found]
    ignored = [s["name"] for s in steps if s["problems"] and s["id"] not in hit]
    return {"unmatched": where["unmatched"], "ends": where["ends"], "quiet": quiet, "ignored": ignored}


__all__ = ["has_step_times", "sipoc_steps", "SCOPE_DIMENSIONS", "scope_rows", "uploaded_team", "unit_of", "parse_limit", "number_in", "parse_sipoc", "missing_columns", "METRIC_FIELDS",
           "normal_unit", "is_estimate", "metric_value", "as_metric", "metric_text", "primary_unit",
           "STEP_KEYS", "DURATION_KEYS", "PROCESS_PERFORMANCE_KEYS", "period_value", "duration_value",
           "process_steps", "process_performance", "sipoc_with_performance", "step_names", "link_mismatch",
           "located_steps", "realisation_stated", "goal_sentence"]
