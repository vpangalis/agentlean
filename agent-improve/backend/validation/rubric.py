"""Layer 2d for Define — the R7 rubric, graded at the gate.

Founder requirement R7 (`docs/requirements/business.md`, 2026-09-26): the gate
rubric comes from the manual, ONE criterion per element, pass/fail with a
reason. The criteria are `core.prompts.DEFINE_RUBRIC` (their one home); this
module grades a Define gate document against them:

  1. the DETERMINISTIC half of each criterion first — presence of the parts a
     criterion needs, a number where it needs one, a date, a named champion
     and process owner. Four criteria are decided entirely here (DEF-R02,
     DEF-R08, DEF-R09, DEF-R10); a code failure of a mixed one (DEF-R03,
     DEF-R04, DEF-R05, DEF-R12) is final, with no model call;
  2. ONE `grader` call (temperature 0 — G-241; §4.7), builder-style structured
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
#: G-133 (2026-09-29): DEF-R02 is no longer code-only — code settles the champion and the process
#: owner, and the training when it is written in so many words; otherwise the grader judges it with
#: the element's own criteria (founder ruling 2: the element check and the gate cannot disagree).
CODE_ONLY: frozenset[str] = frozenset({"DEF-R08", "DEF-R09", "DEF-R10"})

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
    """ADR-0088 decision 5: the one date parser (`define/parse.calendar_date`) — the rubric has no reader of its own."""
    from backend.phases.define.parse import calendar_date
    found = calendar_date(_text(value))
    return dt.date.fromisoformat(found[0]) if found else None


def _code_half(cid: str, a: dict[str, Any], today: dt.date) -> Optional[CriterionVerdict]:
    """A verdict when code can settle the criterion (or fail its code half);
    None when the criterion still needs the model's judgment."""
    if cid == "DEF-R02":
        team = [e for e in (a.get("team") or []) if isinstance(e, dict)]
        roles = " ".join(_text(e.get("role")) + " " + _text(e.get("function")) for e in team).lower()
        missing = [name for name, pat in (("a champion", r"champion|sponsor"),
                                          ("a process owner", r"process owner|owner of the process"))
                   if not re.search(pat, roles)]
        if missing:
            return _fail(cid, "The team does not name " + "; ".join(missing) + ".")
        # Training written as "train…" settles it; said in other words ("needs a half-day on data
        # collection"), it is the grader's to judge against the element's criteria (G-133).
        return _pass(cid) if any("train" in _text(e).lower() for e in team) else None
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
        from backend.phases.define.parse import as_metric, primary_unit
        if as_metric(a.get("baseline_estimate"), unit=primary_unit(a))["value"] is None:
            return _fail(cid, "The baseline has no number — quantify the primary metric today.")
        return None
    if cid == "DEF-R08":
        # ADR-0071: both read as MetricValues — by the one parser when a value is still text.
        from backend.phases.define.parse import as_metric, primary_unit
        baseline = as_metric(a.get("baseline_estimate"), unit=primary_unit(a))
        target = as_metric(a.get("target_value"), target=True, unit=baseline["unit"] or primary_unit(a))
        if target["value"] is None:
            return _fail(cid, "The target has no number.")
        if baseline["unit"] and target["unit"] and target["unit"] != baseline["unit"]:
            return _fail(cid, f"The target is in {target['unit']}, the baseline in {baseline['unit']} — "
                              "state the target in the baseline's unit.")
        if target["value"] == baseline["value"]:
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
    if cid == "DEF-R13":
        # G-134 (founder ruling 4, 2026-09-29): code settles what can be read — the conscious
        # "none identified at this stage", or nothing named at all; the model judges only
        # whether what is named is specific (MODEL_ASKS).
        text = _text(a.get("issues_and_barriers")).strip()
        if _NONE_IDENTIFIED.search(text):
            return _pass(cid)
        if not _names_a_roadblock(text):
            return _fail(cid, "Name at least one specific issue or barrier that could stop the project, "
                              "or state 'none identified at this stage'.")
        return None
    if cid == "DEF-R12":
        blank = _blank_keys(a.get("process_map_sipoc"), ("suppliers", "inputs", "process_steps",
                                                          "outputs", "customers", "process_metrics"))
        return _fail(cid, "The SIPOC leaves out: " + ", ".join(blank) + ".") if blank else None
    return None


#: G-134 — the conscious answer DEF-R13 accepts, and the words that name no roadblock at all.
_NONE_IDENTIFIED = re.compile(r"(?<![a-z])none identified at this stage(?![a-z])", re.I)
_NO_ROADBLOCK = re.compile(r"^(none|no|nothing|n/?a|tbd|tbc|unknown|not sure|don'?t know|-+)(?![a-z])[\s.!]*$", re.I)


def _names_a_roadblock(text: str) -> bool:
    """At least one issue or barrier is named: words beyond a bare "none" / "n/a" / "tbd",
    three or more of them. Whether it is SPECIFIC is the grader's judgment."""
    t = text.strip()
    return bool(t) and not _NO_ROADBLOCK.match(t) and len(re.findall(r"[A-Za-zÄÖÜäöüß]+", t)) >= 3


#: G-134 — what the grader is asked when code has settled part of a criterion: the rest only.
MODEL_ASKS: dict[str, str] = {
    # G-134, second attempt (2026-09-29): the first narrowed question ("each one named is specific
    # ... a named system, team, rule, date or dependency") still failed an answer naming three sites'
    # approval routes and an ERP change freeze until January (record 20260929T103652). The question
    # now says what passes and what fails, in the project's terms.
    "DEF-R13": ("code has already checked that at least one issue or barrier is named. Judge ONLY "
                "whether they belong to THIS project: PASS when the roadblocks named mention something "
                "concrete from it — a site, process, system, team, rule, supplier, date or event; FAIL "
                "only when they are generic labels that would fit any project ('resources', 'time', "
                "'stakeholder buy-in', 'resistance to change') with nothing concrete from this project"),
}


def _document(a: dict[str, Any]) -> str:
    """The confirmed values, one line each — what the grader reads."""
    skip = {"computation_results", "citations", "uploads", "acknowledged_gaps", "phase_metrics"}
    return "\n".join(f"{k}: {_text(v)}" for k, v in a.items() if k not in skip and _text(v))


#: G-241 (founder ruling 2026-10-22 afternoon, 1b): the gate judge reads at temperature 0 — the same document gets the
#: same verdict. The coaching grader (the `grader` role's own 0.1, §4.7) is unchanged.
GATE_TEMPERATURE = 0.0

#: G-241: the terms a failing reason can name — a quoted phrase, a hyphenated compound, an acronym.
_TERM = re.compile(r"(?:(?<=\s)|^)['‘\"“]([^'’\"”]{3,80})['’\"”](?=[\s.,;:)]|$)"
                   r"|\b([A-Za-z]+(?:-[A-Za-z]+)+)\b|\b([A-Z]{2,})\b")


def foreign_terms(reason: str, document: str, criteria: str) -> list[str]:
    """G-241 (1b): the terms a failing reason names that appear neither in the case's answers nor in the criteria — a
    reason must name a gap in the case's own answers, never a fact the case does not hold (run 140813: "year-end
    close context", in a case that never mentions a year-end close)."""
    known = f"{document} {criteria}".lower()
    terms = [next(g for g in m.groups() if g) for m in _TERM.finditer(reason or "")]
    return [t for t in terms if t.lower() not in known]


async def _llm_verdicts(criteria: list[tuple[str, str, str]], document: str) -> GraderVerdict:
    """One `grader` call for the criteria that need judgment."""
    grader = get_llm("grader", temperature=GATE_TEMPERATURE).with_structured_output(GraderVerdict)
    # G-129 (founder ruling 2, 2026-09-28): each rubric line carries its element's own acceptance
    # criteria, so the element check and the gate cannot disagree on the same answer.
    from backend.middleware.skills import acceptance_criteria
    lines = "\n".join(
        f"- {cid} ({field}): {text}" + "".join(
            f"\n    element criterion `{aid}`: {atext}" for aid, atext in acceptance_criteria("define", field))
        for cid, field, text in criteria)
    out = await grader.ainvoke(GATE_GRADER_PROMPT.format(phase="Define", criteria=lines,
                                                         document=document))
    return GraderVerdict.model_validate(out)


#: DEF-224 — the elements a model-judged criterion reads beyond its own, so a change to any of them re-judges it:
#: the goal is judged against the baseline and the target (DEF-R07); "belongs to THIS project" against what the
#: project is (DEF-R13). Every other criterion judges its own element's value.
READS: dict[str, tuple[str, ...]] = {
    "DEF-R07": ("baseline_estimate", "target_value", "target_date"),
    "DEF-R13": ("business_case", "project_scope", "process_map_sipoc"),
}


def _version() -> str:
    """DEF-224: what a kept gate verdict was judged against — the Define script (the elements' acceptance criteria;
    its hash, as logged per turn), the rubric and the grader's prompt. Any of them changing re-judges everything."""
    from backend.middleware.skills import script_record
    from backend.validation import kept
    return kept.fingerprint(script_record("define")["sha256"], DEFINE_RUBRIC, GATE_GRADER_PROMPT, MODEL_ASKS)


def _fingerprint(version: str, cid: str, field: str, a: dict[str, Any]) -> str:
    from backend.validation import kept
    return kept.fingerprint(version, cid, [kept.answer(_text(a.get(f))) for f in (field, *READS.get(cid, ()))])


def kept_verdicts(artifacts: dict[str, Any], verdict: GraderVerdict) -> dict[str, dict[str, Any]]:
    """DEF-224: each model-judged criterion's verdict with its fingerprint, keyed by criterion — what the gate keeps
    in the graded element's `field_status` entry (`field_status[field]["gate"]`)."""
    a, version = dict(artifacts or {}), _version()
    fields = {cid: field for cid, field, _ in DEFINE_CRITERIA}
    return {v.criterion: {"fp": _fingerprint(version, v.criterion, fields[v.criterion], a), "field": fields[v.criterion],
                          "status": v.status, "feedback": v.feedback}
            for v in verdict.verdicts if v.criterion in fields and v.criterion not in CODE_ONLY}


async def grade_define(artifacts: dict[str, Any], judge: Optional[Judge] = None,
                       today: Optional[dt.date] = None,
                       kept: Optional[dict[str, dict[str, Any]]] = None) -> GraderVerdict:
    """Grade a Define gate document against DEFINE_RUBRIC — one verdict per
    criterion, in the rubric's order, pass or fail with the reason.

    DEF-224 (G-225): `kept` is the verdicts kept from earlier submissions (`kept_verdicts`); a criterion whose
    fingerprint is unchanged keeps its verdict with no model call, and only the changed ones go to the model."""
    a = dict(artifacts or {})
    today = today or dt.date.today()
    verdicts: dict[str, CriterionVerdict] = {}
    to_judge: list[tuple[str, str, str]] = []
    version = _version() if kept else ""
    for cid, field, text in DEFINE_CRITERIA:
        v = _code_half(cid, a, today)
        held = (kept or {}).get(cid) or {}
        if v is not None:
            verdicts[cid] = v
        elif cid in CODE_ONLY:                      # unreachable: code-only criteria always settle
            verdicts[cid] = _fail(cid, "the deterministic check did not settle")
        elif held.get("fp") and held["fp"] == _fingerprint(version, cid, field, a):
            verdicts[cid] = CriterionVerdict(criterion=cid, status="pass" if held.get("status") == "pass" else "fail",
                                             feedback=str(held.get("feedback") or ""))
        else:
            to_judge.append((cid, field, MODEL_ASKS.get(cid, text)))
    if kept is not None:
        logger.info("define rubric: %d criterion verdict(s) kept for unchanged answers, %d to judge (DEF-224)",
                    sum(1 for cid, _, _ in DEFINE_CRITERIA if cid in verdicts and cid in kept), len(to_judge))
    if to_judge:
        document = _document(a)
        # G-241 (1c): three judgments, the majority per criterion — the same document must get the same verdict.
        rounds = [await _judged_once(to_judge, document, judge) for _ in range(GATE_VOTES)]
        for cid, _field, _criterion in to_judge:
            fails = [r[cid] for r in rounds if r[cid].status == "fail"]
            verdicts[cid] = fails[0] if len(fails) * 2 > GATE_VOTES else CriterionVerdict(criterion=cid, status="pass",
                                                                                          feedback="")
        logger.info("define rubric: G-241 — %d judgment(s) per criterion, majority kept: %s", GATE_VOTES,
                    ", ".join(f"{cid} {sum(r[cid].status == 'pass' for r in rounds)}/{GATE_VOTES} pass"
                              for cid, _, _ in to_judge))
    return GraderVerdict(verdicts=[verdicts[cid] for cid, _, _ in DEFINE_CRITERIA])


#: G-241 (founder ruling 2026-10-22 afternoon, 1c): each model-judged gate criterion takes the majority of this many
#: judgments — the judge disagreed with itself at temperature 0 on the same document (3 fail, 2 pass in 5).
GATE_VOTES = 3


async def _judged_once(to_judge: list[tuple[str, str, str]], document: str,
                       judge: Optional[Judge] = None) -> dict[str, CriterionVerdict]:
    """One judgment of `to_judge` — pass or fail per criterion (Tier 1: never a warning; no verdict fails closed).
    G-241 (1b): a failing reason naming a fact the case does not hold is discarded and that criterion judged once
    more; the second verdict stands."""
    model = await (judge or _llm_verdicts)(to_judge, document)
    given = {v.criterion.strip(): v for v in model.verdicts}
    from backend.middleware.skills import acceptance_criteria
    ungrounded = [c for c in to_judge
                  if (v := given.get(c[0])) is not None and v.status != "pass"
                  and foreign_terms(v.feedback, document, c[2] + " " + " ".join(
                      t for _, t in acceptance_criteria("define", c[1])))]
    if ungrounded:
        logger.warning("define rubric: G-241 — %s failed on a fact not in the case; judged once more",
                       ", ".join(c[0] for c in ungrounded))
        again = await (judge or _llm_verdicts)(ungrounded, document)
        given.update({v.criterion.strip(): v for v in again.verdicts})
    out: dict[str, CriterionVerdict] = {}
    for cid, _field, _criterion in to_judge:
        v = given.get(cid)
        if v is None:
            logger.warning("define rubric: the grader returned no verdict for %s", cid)
            out[cid] = _fail(cid, "The grader gave no verdict on this criterion — grade again.")
        else:
            status = "pass" if v.status == "pass" else "fail"      # Tier 1: never a warning
            out[cid] = CriterionVerdict(criterion=cid, status=status, feedback="" if status == "pass" else v.feedback)
    return out


__all__ = ["CODE_ONLY", "DEFINE_CRITERIA", "MODEL_ASKS", "READS", "grade_define", "kept_verdicts"]
