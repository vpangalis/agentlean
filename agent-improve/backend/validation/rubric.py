"""Layer 2d for Define — the R7 rubric, graded at the gate.

Founder requirement R7 (`docs/requirements/define.md`, 2026-09-26): the gate
rubric comes from the manual, ONE criterion per element, pass/fail with a
reason. The criteria are `core.prompts.DEFINE_RUBRIC` (their one home); this
module grades a Define gate document against them:

  1. the DETERMINISTIC half of each criterion first — presence of the parts a
     criterion needs, a number where it needs one, a date, a named champion
     and process owner. Four criteria are decided entirely here (DEF-R02,
     DEF-R08, DEF-R09, DEF-R10); a code failure of a mixed one (DEF-R03,
     DEF-R04, DEF-R05, DEF-R12) is final, with no model call;
  2. ONE `grader` call (temperature 0.1, §4.7), builder-style structured
     output (§4.6: a plain model call inside a validator), for what needs
     judgment — "no cause or solution speculation", "as-is, not the ideal",
     "real data, not a best guess". No retrieval (§9: never during gate
     validation).

Define is Tier 1 throughout: a `warning` from the model is read as `fail`, and
a criterion the model left unjudged FAILS CLOSED with that reason — a gate
never opens on a verdict nobody gave. Module-level functions only (§2).
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import re
from typing import Any, Awaitable, Callable, Optional

from backend.core.llm import get_llm
from backend.core.prompts import DEFINE_RUBRIC, GATE_GRADER_PROMPT
from backend.validation.schemas import CriterionVerdict, GraderVerdict

logger = logging.getLogger(__name__)

_LINE = re.compile(r"^-\s*(?P<id>DEF-R\d{2})\s+(?P<field>\w+):\s*(?P<text>.+)$")

#: (id, element, criterion text) — parsed from DEFINE_RUBRIC, in its order.
DEFINE_CRITERIA: tuple[tuple[str, str, str], ...] = tuple(
    (m["id"], m["field"], m["text"].strip())
    for m in (_LINE.match(ln.strip()) for ln in DEFINE_RUBRIC.splitlines()) if m)

#: The criteria decided entirely in code; the rest reach the model when their
#: code half (if any) passes.
CODE_ONLY: frozenset[str] = frozenset({"DEF-R02", "DEF-R08", "DEF-R09", "DEF-R10"})

Judge = Callable[[list[tuple[str, str, str]], str], Awaitable[GraderVerdict]]


def _text(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value or "").strip()


def _has_number(value: Any) -> bool:
    return bool(re.search(r"\d", _text(value)))


def _pass(cid: str) -> CriterionVerdict:
    return CriterionVerdict(criterion=cid, status="pass")


def _fail(cid: str, feedback: str) -> CriterionVerdict:
    return CriterionVerdict(criterion=cid, status="fail", feedback=feedback)


def _blank_keys(value: Any, keys: tuple[str, ...]) -> list[str]:
    d = value if isinstance(value, dict) else {}
    return [k for k in keys if not _text(d.get(k))]


def _parse_date(value: Any) -> Optional[dt.date]:
    text = _text(value)
    m = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if m:
        try:
            return dt.date.fromisoformat(m.group(0))
        except ValueError:
            return None
    for fmt in ("%d %B %Y", "%B %d %Y", "%d %b %Y", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(text.replace(",", ""), fmt).date()
        except ValueError:
            continue
    return None


def _code_half(cid: str, a: dict[str, Any], today: dt.date) -> Optional[CriterionVerdict]:
    """A verdict when code can settle the criterion (or fail its code half);
    None when the criterion still needs the model's judgment."""
    if cid == "DEF-R02":
        team = [e for e in (a.get("team") or []) if isinstance(e, dict)]
        roles = " ".join(_text(e.get("role")) + " " + _text(e.get("function")) for e in team).lower()
        missing = [name for name, pat in (("a champion", r"champion|sponsor"),
                                          ("a process owner", r"process owner|owner of the process"))
                   if not re.search(pat, roles)]
        if not any("train" in _text(e).lower() for e in team):
            missing.append("the training members need (or that none is needed)")
        return _fail(cid, "The team does not name " + "; ".join(missing) + ".") if missing else _pass(cid)
    if cid == "DEF-R03":
        ctqs = [c for c in (a.get("critical_to_quality") or []) if isinstance(c, dict)]
        if not ctqs or any(not _text(c.get("requirement")) for c in ctqs):
            return _fail(cid, "State at least one CTQ as a measurable requirement.")
        return None
    if cid == "DEF-R04":
        blank = _blank_keys(a.get("problem_5w2h"), ("what", "where", "when", "who", "why", "how", "how_much"))
        return _fail(cid, "The 5W2H leaves unanswered: " + ", ".join(blank) + ".") if blank else None
    if cid == "DEF-R05":
        registry = [m for m in (a.get("metric_definitions") or []) if isinstance(m, dict)]
        if not registry:
            return _fail(cid, "No primary metric is registered.")
        if not _has_number(a.get("baseline_estimate")):
            return _fail(cid, "The baseline has no number — quantify the primary metric today.")
        return None
    if cid == "DEF-R08":
        target, baseline = _text(a.get("target_value")), _text(a.get("baseline_estimate"))
        if not _has_number(target):
            return _fail(cid, "The target has no number.")
        if target == baseline:
            return _fail(cid, "The target equals the baseline — it sets no improvement.")
        return _pass(cid)
    if cid == "DEF-R09":
        date = _parse_date(a.get("target_date"))
        if date is None:
            return _fail(cid, "The target date is not a calendar date (e.g. 2027-03-31).")
        return _pass(cid) if date > today else _fail(cid, "The target date is not in the future.")
    if cid == "DEF-R10":
        b = a.get("benefits_analysis")
        blank = _blank_keys(b, ("cost_of_gap", "impact_type", "realisation_schedule", "finance_contact"))
        if blank:
            return _fail(cid, "The benefits analysis leaves out: " + ", ".join(blank) + ".")
        if not _has_number(b.get("cost_of_gap") if isinstance(b, dict) else None):
            return _fail(cid, "The cost of the gap has no figure.")
        impact = _text(b.get("impact_type") if isinstance(b, dict) else "").lower()
        if not re.search(r"sustain|one[- ]?off|recurr|annual|every year", impact):
            return _fail(cid, "Say whether the impact is sustainable or one-off.")
        return _pass(cid)
    if cid == "DEF-R12":
        blank = _blank_keys(a.get("process_map_sipoc"), ("suppliers", "inputs", "process_steps",
                                                          "outputs", "customers", "process_metrics"))
        return _fail(cid, "The SIPOC leaves out: " + ", ".join(blank) + ".") if blank else None
    return None


def _document(a: dict[str, Any]) -> str:
    """The confirmed values, one line each — what the grader reads."""
    skip = {"computation_results", "citations", "uploads", "acknowledged_gaps", "phase_metrics"}
    return "\n".join(f"{k}: {_text(v)}" for k, v in a.items() if k not in skip and _text(v))


async def _llm_verdicts(criteria: list[tuple[str, str, str]], document: str) -> GraderVerdict:
    """One `grader` call for the criteria that need judgment."""
    grader = get_llm("grader").with_structured_output(GraderVerdict)
    lines = "\n".join(f"- {cid} ({field}): {text}" for cid, field, text in criteria)
    out = await grader.ainvoke(GATE_GRADER_PROMPT.format(phase="Define", criteria=lines,
                                                         document=document))
    return GraderVerdict.model_validate(out)


async def grade_define(artifacts: dict[str, Any], judge: Optional[Judge] = None,
                       today: Optional[dt.date] = None) -> GraderVerdict:
    """Grade a Define gate document against DEFINE_RUBRIC — one verdict per
    criterion, in the rubric's order, pass or fail with the reason."""
    a = dict(artifacts or {})
    today = today or dt.date.today()
    verdicts: dict[str, CriterionVerdict] = {}
    to_judge: list[tuple[str, str, str]] = []
    for cid, field, text in DEFINE_CRITERIA:
        v = _code_half(cid, a, today)
        if v is not None:
            verdicts[cid] = v
        elif cid in CODE_ONLY:                      # unreachable: code-only criteria always settle
            verdicts[cid] = _fail(cid, "the deterministic check did not settle")
        else:
            to_judge.append((cid, field, text))
    if to_judge:
        model = await (judge or _llm_verdicts)(to_judge, _document(a))
        given = {v.criterion.strip(): v for v in model.verdicts}
        for cid, _field, _criterion in to_judge:
            v = given.get(cid)
            if v is None:
                logger.warning("define rubric: the grader returned no verdict for %s", cid)
                verdicts[cid] = _fail(cid, "The grader gave no verdict on this criterion — grade again.")
            else:
                status = "pass" if v.status == "pass" else "fail"      # Tier 1: never a warning
                verdicts[cid] = CriterionVerdict(criterion=cid, status=status,
                                                 feedback="" if status == "pass" else v.feedback)
    return GraderVerdict(verdicts=[verdicts[cid] for cid, _, _ in DEFINE_CRITERIA])


__all__ = ["CODE_ONLY", "DEFINE_CRITERIA", "grade_define"]
