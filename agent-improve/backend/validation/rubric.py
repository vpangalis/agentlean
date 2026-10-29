"""Layer 2d for Define — the R7 rubric, graded at the gate.

Requirement R7 (`docs/requirements/business.md`): the gate rubric comes from
the manual, ONE criterion per element, pass/fail with a reason. The criteria
are `core.prompts.DEFINE_RUBRIC` (their one home); this module grades a Define
gate document against them:

  1. the DETERMINISTIC half of each criterion first — presence of the parts a
     criterion needs, a number where it needs one, a date, a named champion
     and process owner. Two criteria are decided entirely here (`CODE_ONLY`:
     DEF-R08, DEF-R09); a mixed one (DEF-R02, DEF-R03, DEF-R04, DEF-R05,
     DEF-R10, DEF-R12, DEF-R13) that fails its code half fails, with no model
     call, and one that code settles (DEF-R02, DEF-R13) passes without one;
  2. the `grader` model at temperature 0 (G-241), with structured output (a
     plain model call inside a validator), for what needs judgment — "no cause
     or solution speculation", "as-is, not the ideal", "real data, not a best
     guess". Each criterion takes the majority of `GATE_VOTES` judgments, and
     a criterion verdict kept from an earlier submission whose answers are
     unchanged is reused with no call (DEF-224). No retrieval: none during
     gate validation.

Define is Tier 1 throughout: a `warning` from the model is read as `fail`, and
a criterion the model left unjudged FAILS CLOSED with that reason — a gate
never opens on a verdict nobody gave. Module-level functions only.
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import re
from typing import Any, Awaitable, Callable, Optional

from backend.core.llm import get_llm
from backend.core.prompts import DEFINE_RUBRIC, GATE_GRADER_PROMPT
from backend.phases.define.schema import BENEFITS_ANALYSIS_KEYS, PROJECT_SCOPE_KEYS, SIPOC_KEYS
from backend.validation.schemas import CriterionVerdict, GraderVerdict

logger = logging.getLogger(__name__)

_LINE = re.compile(r"^-\s*(?P<id>DEF-R\d{2})\s+(?P<field>\w+):\s*(?P<text>.+)$")

#: (id, element, criterion text) — parsed from DEFINE_RUBRIC, in its order.
DEFINE_CRITERIA: tuple[tuple[str, str, str], ...] = tuple(
    (m["id"], m["field"], m["text"].strip())
    for m in (_LINE.match(ln.strip()) for ln in DEFINE_RUBRIC.splitlines()) if m)

#: The criteria decided entirely in code; the rest reach the model when their
#: code half (if any) does not settle them.
#: DEF-R02 is code-only since R-B (founder ruling 2026-10-27): training needs are not a Define criterion, so the team's
#: criterion is the champion and the process owner, both read in code (parse.missing_parts) — the element check and
#: the gate cannot disagree.
#: DEF-R13 (G-263, founder ruling 2026-10-27, item 1's fallback): whether the barriers belong to THIS project is
#: read in code — the model's verdict flipped with the layout of its prompt on the same barriers.
#: DEF-R10 (founder ruling 2026-10-27, item 2, E19): no question about working — code computes the saving with the
#: ratified formula and the read-back shows the working line; the four parts are code's to check.
CODE_ONLY: frozenset[str] = frozenset({"DEF-R02", "DEF-R08", "DEF-R09", "DEF-R10", "DEF-R13"})

Judge = Callable[[list[tuple[str, str, str]], str], Awaitable[GraderVerdict]]


def _text(value: Any) -> str:
    """A value as the code checks read it (its figures and words): structure as JSON, text as it is. The gate judge
    never reads this form — it reads each value tagged under its display name (_document_by_criterion, G-263)."""
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
    # G-244 (G-129): the parts the element check and the gate both hold are checked by
    # ONE function, the element check's own (parse.missing_parts) — a confirmed element never fails here in code.
    from backend.phases.define.parse import missing_parts
    if cid == "DEF-R02":
        team = [e for e in (a.get("team") or []) if isinstance(e, dict)]
        missing = missing_parts("team", team)
        if not team or missing:
            return _fail(cid, "The team does not state " + ("; ".join(missing) or "its members") + ".")
        return _pass(cid)
    if cid == "DEF-R03":
        ctqs = [c for c in (a.get("critical_to_quality") or []) if isinstance(c, dict)]
        missing = missing_parts("critical_to_quality", ctqs)
        if not ctqs or missing:
            return _fail(cid, "The CTQs do not state " + ("; ".join(missing) or "any requirement") + ".")
        return None
    if cid == "DEF-R04":
        fivew = a.get("problem_5w2h")
        missing = missing_parts("problem_5w2h", fivew) if isinstance(fivew, dict) else ["the seven 5W2H answers"]
        return _fail(cid, "The 5W2H leaves unanswered " + "; ".join(missing) + ".") if missing else None
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
        from backend.phases.define.parse import wrong_side
        if side := wrong_side(baseline["value"], target, a.get("goal_statement")):        # G-245
            return _fail(cid, f"The target is on the wrong side of the baseline: {side}.")
        return _pass(cid)
    if cid == "DEF-R09":
        date = _parse_date(a.get("target_date"))
        if date is None:
            return _fail(cid, "The target date is not a calendar date (e.g. 2027-03-31).")
        return _pass(cid) if date > today else _fail(cid, "The target date is not in the future.")
    if cid == "DEF-R10":
        b = a.get("benefits_analysis")
        blank = _blank_keys(b, BENEFITS_ANALYSIS_KEYS)
        if blank:
            return _fail(cid, "The benefits analysis leaves out: " + ", ".join(blank) + ".")
        if not _has_number(b.get("cost_of_gap") if isinstance(b, dict) else None):
            return _fail(cid, "The cost of the gap has no figure.")
        impact = _text(b.get("impact_type") if isinstance(b, dict) else "").lower()
        if not re.search(r"sustain|one[- ]?off|recurr|annual|every year", impact):
            return _fail(cid, "Say whether the impact is sustainable or one-off.")
        if missing := missing_parts("benefits_analysis", b):                       # G-255: the element's own check
            return _fail(cid, "The benefits analysis does not say " + "; ".join(missing) + ".")
        return _pass(cid)                               # item 2 (E19): the working is code's, never asked
    if cid == "DEF-R13":
        # G-134: the conscious "none identified at this stage", or nothing named at all. G-263 (founder ruling
        # 2026-10-27, item 1's fallback; the founder's review, 11:25): what is named is specific when it names an
        # entity of this project's own — a date alone never is.
        text = _text(a.get("issues_and_barriers")).strip()
        if _NONE_IDENTIFIED.search(text):
            return _pass(cid)
        if not _names_a_roadblock(text):
            return _fail(cid, "Name at least one specific issue or barrier that could stop the project, "
                              "or state 'none identified at this stage'.")
        if barrier_names(text, a):
            return _pass(cid)
        from backend.phases.define.criteria import SPECIFIC_MISSING
        return _fail(cid, SPECIFIC_MISSING)
    if cid == "DEF-R12":
        blank = _blank_keys(a.get("process_map_sipoc"), SIPOC_KEYS)
        return _fail(cid, "The SIPOC leaves out: " + ", ".join(blank) + ".") if blank else None
    return None


#: G-134 — the conscious answer DEF-R13 accepts, and the words that name no roadblock at all.
_NONE_IDENTIFIED = re.compile(r"(?<![a-z])none identified at this stage(?![a-z])", re.I)
_NO_ROADBLOCK = re.compile(r"^(none|no|nothing|n/?a|tbd|tbc|unknown|not sure|don'?t know|-+)(?![a-z])[\s.!]*$", re.I)


#: G-263: words a scope, a SIPOC or a team uses that name no particular project — and the generic labels DEF-R13
#: fails ('resources', 'time', 'stakeholder buy-in', 'resistance to change').
_GENERIC = frozenset((
    "team teams process processes project projects member members owner other others their them they with from that "
    "this about hours days weeks months years minutes resource resources time timing budget money funding people "
    "staff staffing capacity stakeholder stakeholders support resistance change changes management leadership "
    "communication culture priority priorities workload data training skills lack pressure engagement commitment "
    "availability three four five seven eight nine").split())
#: G-263: a date — a month named in full, or a year. It adds to what the barriers name; it never suffices.
_DATE = re.compile(r"\b(?:january|february|march|april|june|july|august|september|october|november|december)\b"
                   r"|\b(?:19|20)\d{2}\b", re.I)


def _record_names(a: dict[str, Any]) -> str:
    """G-263: the words that name this project's own things — its scope (sites, systems), its SIPOC's suppliers,
    inputs, outputs, customers and steps, and its team's names and roles."""
    scope, sipoc = a.get("project_scope"), a.get("process_map_sipoc")
    parts = ([str(scope.get(k) or "") for k in PROJECT_SCOPE_KEYS] if isinstance(scope, dict)
             else [str(scope or "")])
    if isinstance(sipoc, dict):
        parts += [str(sipoc.get(k) or "") for k in ("suppliers", "inputs", "outputs", "customers")]
        parts += [str(s.get("name") or "") for s in sipoc.get("process_steps") or [] if isinstance(s, dict)]
    parts += [f"{e.get('name') or ''} {e.get('role') or ''}" for e in a.get("team") or [] if isinstance(e, dict)]
    return " ".join(parts)


def barrier_names(text: str, a: dict[str, Any]) -> list[str]:
    """G-263 (founder ruling 2026-10-27, item 1's fallback; tightened in the founder's review, 11:25): the entities of
    THIS project the barriers name — a site, system, team, person or rule its scope, SIPOC or team names: an acronym
    they use ('ERP'), or a word of theirs that is no generic label, no number and no date. A date adds to what is
    named and never suffices: with no entity, the list is empty."""
    names = _record_names(a)
    own = {w for w in re.findall(r"[a-zà-ÿ]{4,}", names.lower()) if w not in _GENERIC and not _DATE.fullmatch(w)}
    entities = [w for w in re.findall(r"\b[A-Z]{2,6}\b", text) if re.search(rf"\b{w}\b", names)]
    entities += [w for w in re.findall(r"[a-zà-ÿ]{4,}", text.lower()) if w in own]
    if not entities:
        return []
    return list(dict.fromkeys([*entities, *(m.group(0) for m in _DATE.finditer(text))]))


def _names_a_roadblock(text: str) -> bool:
    """At least one issue or barrier is named: words beyond a bare "none" / "n/a" / "tbd",
    three or more of them. Whether it is SPECIFIC is the grader's judgment."""
    t = text.strip()
    return bool(t) and not _NO_ROADBLOCK.match(t) and len(re.findall(r"[A-Za-zÄÖÜäöüß]+", t)) >= 3


#: G-134 — what the grader is asked when code has settled part of a criterion: the rest only.
MODEL_ASKS: dict[str, str] = {
    # DEF-R10's "how the cost of the gap was worked out" is gone (founder ruling 2026-10-27, item 2, E19); DEF-R13's
    # specificity is code's (G-263). A criterion code settles in part asks the model the rest here.
}


def _reads(field: str, cid: str) -> list[str]:
    """G-241: the fields a criterion is judged on — its element's captured fields
    (the CTQs with the voice of the customer, the 5W2H with the problem) and those of the elements in READS."""
    from backend.phases import moves
    captured = dict(moves.positions("define"))
    out: list[str] = []
    for element in (field, *READS.get(cid, ())):
        for f in captured.get(element, (element,)):
            if f not in out:
                out.append(f)
    return out


def _document_by_criterion(criteria: list[tuple[str, str, str]], a: dict[str, Any]) -> str:
    """G-241: one section per criterion, holding only the values it reads — a wording change in an element a
    criterion does not read cannot tip it. G-256: the benefits criterion reads the calculation shown with the cost.
    G-263 (founder ruling 2026-10-27): each value as the coach reads it — tagged, under its display name, in plain
    lines (state_injection.value_tag) — never JSON."""
    from backend.middleware.state_injection import value_tag
    return "\n\n".join(f"[{cid} — the values it reads]\n" + "\n".join(
        [value_tag("define", f, a.get(f), whole=True) for f in _reads(field, cid) if _text(a.get(f))]
        + _calculation(field, a))
        for cid, field, _ in criteria)


def _calculation(field: str, a: dict[str, Any]) -> list[str]:
    """G-256: how the benefits' figures were calculated in code (ADR-0077), as the Belt saw them — nothing for another
    element, or when nothing was calculated."""
    if field != "benefits_analysis":
        return []
    from backend.phases import calculations
    lines = calculations.how_it_was_calculated(calculations.latest(a, "define", field))
    return [f"calculated: {lines}"] if lines else []


def _document(a: dict[str, Any]) -> str:
    """The confirmed values, one line each — what the grader reads."""
    skip = {"computation_results", "citations", "uploads", "acknowledged_gaps", "phase_metrics"}
    return "\n".join(f"{k}: {_text(v)}" for k, v in a.items() if k not in skip and _text(v))


#: G-241: the terms a failing reason can name — a quoted phrase, a hyphenated compound, an acronym.
_TERM = re.compile(r"(?:(?<=\s)|^)['‘\"“]([^'’\"”]{3,80})['’\"”](?=[\s.,;:)]|$)"
                   r"|\b([A-Za-z]+(?:-[A-Za-z]+)+)\b|\b([A-Z]{2,})\b")


def foreign_terms(reason: str, document: str, criteria: str) -> list[str]:
    """G-241: the terms a failing reason names that appear neither in the case's answers nor in the criteria — a
    reason must name a gap in the case's own answers, never a fact the case does not hold ("year-end close
    context", in a case that never mentions a year-end close)."""
    known = f"{document} {criteria}".lower()
    terms = [next(g for g in m.groups() if g) for m in _TERM.finditer(reason or "")]
    return [t for t in terms if t.lower() not in known]


async def _llm_verdicts(criteria: list[tuple[str, str, str]], document: str) -> GraderVerdict:
    """One `gate_judge` call for the criteria that need judgment — at its role's temperature, 0 (G-241: the same
    document gets the same verdict)."""
    grader = get_llm("gate_judge").with_structured_output(GraderVerdict)
    # G-129: each rubric line carries its element's own acceptance
    # criteria, so the element check and the gate cannot disagree on the same answer — read from their owner (B7).
    from backend.phases.define import criteria as define_criteria
    lines = "\n".join(
        f"- {cid} ({field}): {text}" + "".join(
            f"\n    element criterion `{aid}`: {atext}" for aid, atext in define_criteria.criteria(field))
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
        document = _document_by_criterion(to_judge, a)
        # G-241: GATE_VOTES judgments, the majority per criterion — the same document must get the same verdict.
        rounds = [await _judged_once(to_judge, document, judge) for _ in range(GATE_VOTES)]
        for cid, _field, _criterion in to_judge:
            fails = [r[cid] for r in rounds if r[cid].status == "fail"]
            verdicts[cid] = fails[0] if len(fails) * 2 > GATE_VOTES else CriterionVerdict(criterion=cid, status="pass",
                                                                                          feedback="")
        logger.info("define rubric: G-241 — %d judgment(s) per criterion, majority kept: %s", GATE_VOTES,
                    ", ".join(f"{cid} {sum(r[cid].status == 'pass' for r in rounds)}/{GATE_VOTES} pass"
                              for cid, _, _ in to_judge))
    return GraderVerdict(verdicts=[verdicts[cid] for cid, _, _ in DEFINE_CRITERIA])


#: G-241: each model-judged gate criterion takes the majority of this many judgments, because the judge can disagree
#: with itself on the same document even at temperature 0.
GATE_VOTES = 3


async def _judged_once(to_judge: list[tuple[str, str, str]], document: str,
                       judge: Optional[Judge] = None) -> dict[str, CriterionVerdict]:
    """One judgment of `to_judge` — pass or fail per criterion (Tier 1: never a warning; no verdict fails closed).
    G-241: a failing reason naming a fact the case does not hold is discarded and that criterion judged once
    more; the second verdict stands."""
    model = await (judge or _llm_verdicts)(to_judge, document)
    given = {v.criterion.strip(): v for v in model.verdicts}
    from backend.phases.define import criteria as define_criteria
    ungrounded = [c for c in to_judge
                  if (v := given.get(c[0])) is not None and v.status != "pass"
                  and foreign_terms(v.feedback, document, c[2] + " " + " ".join(
                      t for _, t in define_criteria.criteria(c[1])))]
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
