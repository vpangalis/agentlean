"""The DEFINE REPORT — requirement R5 (`docs/requirements/business.md`, 2026-09-26).

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


def _metric(artifacts: dict[str, Any], field: str) -> str | None:
    """A baseline or target as the report shows it — "at most 5 %" — from its MetricValue."""
    from backend.phases.define.parse import metric_text
    v = _value(artifacts, field)
    return None if v is None else metric_text(v)


#: C1 (DEF-086) — each key field with a one-line explanation of what it is, in plain words.
FIELD_EXPLAIN: dict[str, str] = {
    "team": "Who works on the project, and in what role.",
    "project_lead": "The person who leads the project day to day.",
    "champion": "The manager who backs the project and decides when it needs a decision.",
    "business_case": "Why the project deserves time and people.",
    "cost_of_gap": "What the problem costs a year if nothing changes.",
    "impact_type": "Whether the saving lasts or happens once.",
    "realisation_schedule": "When the saving is expected to show.",
    "finance_contact": "Who in finance checks the figure.",
    "five_w_two_h": "The seven questions that pin the problem down.",
    "problem_statement": "The problem in one sentence, built from the seven answers.",
    "objective": "What success looks like, with a number and a date.",
    "scope": "What the project covers, and what it deliberately leaves out.",
    "voc_summary": "What the customers of the process say they need.",
    "ctqs": "Each customer need turned into a requirement that can be measured.",
    "primary": "The measure the project is judged on.",
    "baseline_target": "Where the measure stands today, and where it should be.",
    "target_date": "When the target should be reached.",
    "secondary_metrics": "What else is watched, so the fix does not cause a new problem.",
    "sipoc": "The process on one page: who supplies it, its steps, what it produces and for whom.",
    "process_metrics": "What is measured on the process's outputs.",
    "issues": "What could stop the project.",
}

#: C1 — the sentence that tells a reader how to read each visual.
VISUAL_READ: dict[str, str] = {
    "mindmap_5w2h": "Read from the centre out: each branch answers one of the seven questions about the problem.",
    "baseline_target": ("The first bar is where the measure stands today, the second where it should be by "
                        "the target date; the gap between them is the project's job."),
    "sipoc": ("Read left to right: suppliers provide the inputs, the process steps turn them into outputs, and "
              "the outputs go to the customers."),
    "benefit_timeline": ("What the gap costs each year, the saving the project expects, and when that saving "
                         "is expected to land — the same figures as the text beside it."),
}

_NOT_YET = "Not confirmed yet."


def _summaries(a: dict[str, Any], body: dict[int, dict[str, Any]]) -> dict[int, str]:
    """C1 (DEF-086) — each section's short plain-language summary: what it shows and what it means for
    the project, built in code from the confirmed values only (never a value the section lacks)."""
    from backend.phases.define.parse import date_shown
    s1, s2, s3, s4, s5, s6, s7 = (body[n] for n in range(1, 8))
    team = s1.get("team") or []
    champion = (s1.get("champion") or {}).get("name")
    one = (f"{s1.get('project_lead') or 'The project lead'} leads the project"
           + (f"; {champion} is the Champion, who decides" if champion else "")
           + f"; {len(team)} people are on the team." if team else _NOT_YET)
    b = s2.get("benefits") or {}
    two = (f"Closing the gap is worth {b.get('cost_of_gap')} ({b.get('impact_type')}); the saving is "
           f"expected {b.get('realisation_schedule')}, checked by {b.get('finance_contact')}."
           if b else _NOT_YET)
    def sentence(text: Any) -> str:
        t = str(text).strip()
        return t if t.endswith((".", "!", "?")) else f"{t}."
    three = (f"The problem: {sentence(s3['problem_statement'])}"
             + (f" Success: {sentence(s3['objective'])}" if s3.get("objective") else "")
             if s3.get("problem_statement") else _NOT_YET)
    ctqs = s4.get("ctqs") or []
    four = (f"{len(ctqs)} customer need{'s' if len(ctqs) != 1 else ''} turned into measurable "
            f"requirement{'s' if len(ctqs) != 1 else ''}." if ctqs else _NOT_YET)
    primary = s5.get("primary") or {}
    five = (f"Success is measured by {str(primary.get('name') or 'the primary metric').replace('_', ' ')}: from "
            f"{s5.get('baseline') or 'a baseline not confirmed yet'} today to {s5.get('target') or 'a target not confirmed yet'}"
            + (f" by {date_shown(s5['target_date'])}" if s5.get("target_date") else "") + "."
            if primary else _NOT_YET)
    names = parse_steps_names(s6)
    six = (f"The process runs in {len(names)} step{'s' if len(names) != 1 else ''}, from {names[0]} to {names[-1]}."
           if names else _NOT_YET)
    issues = s7.get("issues") or []
    seven = (f"{len(issues)} issue{'s' if len(issues) != 1 else ''} could stop the project." if issues else _NOT_YET)
    return {1: one, 2: two, 3: three, 4: four, 5: five, 6: six, 7: seven}


def parse_steps_names(section6: dict[str, Any]) -> list[str]:
    """The step names section 6 draws (the SIPOC's process column)."""
    return [str(n) for n in ((section6.get("sipoc") or {}).get("process_steps") or []) if str(n).strip()]


def _issues(value: Any) -> list[str]:
    """Section 7's issues as a list: one per line or per ';', else the whole answer as one."""
    import re
    text = str(value or "").strip()
    if not text:
        return []
    parts = [p.strip(" -•\t") for p in re.split(r"\n|;", text)]
    return [p for p in parts if p] or [text]

def _process_section(sipoc: Any) -> dict[str, Any]:
    """Section 6 (ADR-0078, DEF-084): the SIPOC's columns as the diagram draws them (step names),
    each step's performance and the whole process's, every figure as text from its MetricValue."""
    from backend.core.diagrams import sipoc_columns
    from backend.phases.define import parse
    if not isinstance(sipoc, dict):
        return {"sipoc": {}, "steps": [], "process_performance": {}}

    def text(v: Any) -> str | None:
        return parse.metric_text(v) if isinstance(v, dict) else None
    steps = [{"id": s["id"], "name": s["name"],
              "duration": {k: text(s["duration"].get(k)) for k in parse.DURATION_KEYS if s["duration"].get(k)},
              "runs_per_period": text(s.get("runs_per_period")), "problems": s["problems"]}
             for s in parse.process_steps(sipoc.get("process_steps"))]
    perf: dict[str, Any] = sipoc["process_performance"] if isinstance(sipoc.get("process_performance"), dict) else {}
    return {"sipoc": {**sipoc_columns(sipoc), "process_metrics": sipoc.get("process_metrics")},
            "steps": steps,
            "process_performance": {k: text(perf.get(k)) for k in parse.PROCESS_PERFORMANCE_KEYS if perf.get(k)}}


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

    team = _value(a, "team") or []
    # R6 amendment (DEF-100): the report names the project lead and the Champion — the team member
    # whose role says Champion or Sponsor (§39.1.4); None when the team names none.
    champion = next(({"name": m.get("name"), "role": m.get("role")} for m in team
                     if isinstance(m, dict) and any(w in str(m.get("role") or "").lower()
                                                    for w in ("champion", "sponsor"))), None)
    body: dict[int, dict[str, Any]] = {
        1: {"project": frame, "team": team, "project_lead": frame.get("leader"), "champion": champion},
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
            # ADR-0071 (DEF-076): shown as text built from the MetricValue, which is kept beside it.
            "baseline": _metric(a, "baseline_estimate"),
            "target": _metric(a, "target_value"),
            "baseline_value": _value(a, "baseline_estimate"),
            "target_value": _value(a, "target_value"),
            "target_date": _value(a, "target_date"),
            "secondary_metrics": _value(a, "secondary_metrics"),
            "other_registered": registry[1:]},
        # The drawn columns (step names as the diagram shows them), what is measured on the outputs, and
        # each step's performance with the whole process's (ADR-0078, DEF-084).
        6: _process_section(sipoc),
        7: {"issues_and_barriers": _value(a, "issues_and_barriers"),
            "issues": _issues(_value(a, "issues_and_barriers"))},
    }
    # C1 (DEF-086): each section's plain-language summary, and its key fields' one-line explanations.
    summaries = _summaries(a, body)
    sections = [{"n": n, "title": title, "fields": list(fields),
                 "complete": all(_value(a, f) is not None for f in fields), **body[n],
                 "summary": summaries[n]}
                for n, title, fields in REPORT_SECTIONS]
    missing = [f for f in DEFINE_REQUIRED_FOR_GATE_FIELDS if _value(a, f) is None]
    history = {f: h for f, h in value_history(field_log, "define").items() if h["changes"] > 1}
    elements = [{"field": f, "confirmed": not any(element_of(m) == f for m in missing)}
                for f in DEFINE_FIELD_ORDER]
    # ADR-0070: the report's visuals, drawn from the stored values by the reply's own function.
    from backend.phases.define.visuals import report_visuals
    visuals = report_visuals(a)                       # R5 section 2's timeline among them (DEF-088)
    return {"sections": sections, "complete": not missing, "missing": missing,
            "elements": elements, "history": history, "visuals": visuals, "explain": FIELD_EXPLAIN,
            "read": {k: VISUAL_READ[k] for k in visuals if k in VISUAL_READ}}


def _sipoc_columns(sipoc: dict[str, Any]) -> dict[str, list[str]]:
    from backend.core.diagrams import sipoc_columns
    return sipoc_columns(sipoc)


__all__ = ["FIVE_W_TWO_H_QUESTIONS", "REPORT_SECTIONS", "FIELD_EXPLAIN", "VISUAL_READ", "define_report",
           "element_of"]
