"""B7 — Define's acceptance criteria, their ids, the element order and the welcome: one owner, in code.

Founder ruling 2026-10-27, item 4: "code owns the criteria, their ids and the element order (one owner); the skill
text and the welcome are generated from it, not parsed." (audit rows U1, U2, U4, U17.)

What this module owns, and who reads it:

  * the element order — the schema's own list (`schema.DEFINE_REQUIRED_FIELDS`), never re-typed — and each
    element's name;
  * each element's acceptance criteria, `(id, what it checks)`, the text with its page reference exactly as the
    founder's manual gives it — what an answer is judged against (R3), the card's rows (ADR-0093) and the gate judge's
    element criteria (G-129) all read `criteria()`;
  * a named constant for every criterion id: code that names a criterion reads the constant, never the string;
  * the welcome (the five phases and how Define is worked) and how Define ends — what `welcome.py` serves.

`skills/dmaic-define-phase/SKILL.md` (and `coaching_script.md`, its section 3) is GENERATED from this module where it
states any of these: the element table, the numbered heads' numbers, each element's acceptance criteria, the
`[OPENING]` block and section F (`tools/architecture/generate_define_script.py`; `test_generated_docs.py` fails when
either file differs from a fresh generation). The generator reads this module with `ast` and imports nothing, so every
value below is a literal, a name bound to a string literal above it, or the schema's own order.

DEF-R13 (G-263, founder ruling 2026-10-27, item 1's fallback): whether the barriers are this project's is decided in
code at the gate (`validation/rubric.py::barrier_names`); the `specific` criterion below is the coach's, unchanged in
wording — a later step aligns its wording with that check, here.

Module-level data and functions only.
"""
from __future__ import annotations

from backend.phases.define.schema import _CAPTURED_INSIDE, DEFINE_REQUIRED_FIELDS

#: The thirteen elements, in coached order — the schema's list itself (U1).
ELEMENT_ORDER: tuple[str, ...] = DEFINE_REQUIRED_FIELDS

#: Each element's name, as the skill's element table, the sidebar and the welcome show it.
ELEMENT_NAMES: dict[str, str] = {
    "business_case": "Business case",
    "team": "Team",
    "voc_summary": "Voice of the customer and CTQs",
    "problem_statement": "Problem statement",
    "baseline_estimate": "Primary metric and baseline",
    "project_scope": "Scope",
    "goal_statement": "Goal",
    "target_value": "Target",
    "target_date": "Target date",
    "benefits_analysis": "Benefits analysis",
    "secondary_metrics": "Secondary metrics",
    "process_map_sipoc": "High-level process (SIPOC, as-is)",
    "issues_and_barriers": "Issues and barriers",
}

# ── the criterion ids (U4) — code names a criterion by these, never by its string ──
# 1 business case
WHAT = "what"
WHERE_WHEN = "where-when"
BASELINE = "baseline"
COST = "cost"
NO_CAUSE_NO_FIX = "no-cause-no-fix"          # also the problem statement's
# 2 team
CHAMPION = "champion"
PROCESS_OWNER = "process-owner"
PEOPLE = "people"
TRAINING = "training"                          # R-B (2026-10-27): no longer a criterion; the Training column's key
# 3 voice of the customer and CTQs
CUSTOMERS = "customers"
NEEDS = "needs"
CTQ = "ctq"
# 4 problem statement
DEFECT = "defect"
FIVE_W_TWO_H = "5w2h"
MAGNITUDE = "magnitude"
LOCATED = "located"
# 5 primary metric and baseline
ONE_PRIMARY = "one-primary"
QUANTIFIED = "quantified"
KPI_LINK = "kpi-link"
REAL_DATA = "real-data"
DEFINED = "defined"
# 6 scope
IN_AND_OUT = "in-and-out"
START_END = "start-end"
NOT_TOO_BROAD = "not-too-broad"
# 7 goal
SAME_METRIC = "same-metric"
HOW_MUCH = "how-much"
BY_WHEN = "by-when"
# 8 target
NUMBER_AND_UNIT = "number-and-unit"
DIRECTION = "direction"
# 9 target date
A_DATE = "a-date"
# 10 benefits analysis
COST_OF_GAP = "cost-of-gap"
IMPACT_TYPE = "impact-type"
REALISATION = "realisation"
FINANCE_CONTACT = "finance-contact"
SOFT_BENEFITS = "soft-benefits"            # DEF-289 (R7's amendment, ADR-0096 decision 3)
# 11 secondary metrics
SIDE_EFFECT = "side-effect"
NOT_THE_PRIMARY = "not-the-primary"
# 12 high-level process (SIPOC, as-is)
AS_IS = "as-is"
START_TO_END = "start-to-end"
ALL_SIX = "all-six"
CUSTOMERS_MATCH = "customers-match"
PERFORMANCE = "performance"
# 13 issues and barriers
SPECIFIC = "specific"

#: The line that opens an element's criteria in the skill.
CRITERIA_HEAD = "**Acceptance criteria** *(BB manual, the founder's page numbers)*:"

#: Each element's acceptance criteria, in the order the coach teaches them and the card shows them: (id, what it
#: checks). The text paraphrases the founder's Black Belt manual (BB eBook v11.1, Define phase), its page numbers the
#: founder's; a criterion the manual does not carry cites the requirement that added it (R17, R18).
CRITERIA: dict[str, tuple[tuple[str, str], ...]] = {
    "business_case": (
        (WHAT, "names what is wrong: the product or service and the defect (p. 49)"),
        (WHERE_WHEN, "says where it happens and over which period (p. 49)"),
        (BASELINE, "gives how big it is today: a rate, a count or a cost — any one, as a number (p. 49)"),
        (COST, "says what it costs: money, time or volume (p. 49)"),
        (NO_CAUSE_NO_FIX, "carries no guess at the cause and no proposed solution; the method finds those (p. 49)"),
    ),
    "team": (
        (CHAMPION, "names a champion (sponsor) by name (p. 82)"),
        (PROCESS_OWNER, "names the process owner by name (p. 82)"),
        (PEOPLE, "each person has a name, a role and a function (p. 82)"),
    ),
    "voc_summary": (
        (CUSTOMERS, "names the customers, internal and/or external (p. 82)"),
        (NEEDS, "states what they need, in their terms (p. 29, p. 82)"),
        (CTQ, "turns at least one need into a measurable requirement (a CTQ) (p. 31, p. 82)"),
    ),
    "problem_statement": (
        (DEFECT, "describes the defect or pain itself (p. 51)"),
        (FIVE_W_TWO_H, "answers what, where, when, who, why, how and how much (p. 49, p. 52)"),
        (MAGNITUDE, "gives the size as a number against a requirement or reference (p. 49)"),
        (NO_CAUSE_NO_FIX, "names no cause, no solution and no one to blame (p. 49)"),
        (LOCATED, "names the process step(s) where the problem shows (R18); ask for them if the Belt has not said"),
    ),
    "baseline_estimate": (
        (ONE_PRIMARY, "exactly one primary metric (p. 58)"),
        (QUANTIFIED, "the baseline is a number with its unit and the period it covers (p. 58)"),
        (KPI_LINK, "the metric links to a business measure or KPI (p. 58)"),
        (REAL_DATA, "the figure names the data it comes from, not a best guess (p. 80)"),
        (DEFINED, "the metric has a name, a unit and an operational meaning two people would apply the same way "
                  "(p. 58)"),
    ),
    "project_scope": (
        (IN_AND_OUT, "states both what is in and what is out (p. 51)"),
        (START_END, "the in-scope part has a start point and an end point (p. 26)"),
        (NOT_TOO_BROAD, "covers one process or area where the problem sits, not everything around it (p. 80)"),
    ),
    "goal_statement": (
        (SAME_METRIC, "uses the primary metric of the problem (p. 52)"),
        (HOW_MUCH, "states how much improvement, from the baseline to a target (p. 52)"),
        (BY_WHEN, "carries a date (p. 52)"),
    ),
    "target_value": (
        (NUMBER_AND_UNIT, "a number in the baseline's unit (p. 58)"),
        (DIRECTION, "differs from the baseline in the direction the goal states (p. 52)"),
    ),
    "target_date": (
        (A_DATE, "a calendar date, in the future (p. 52)"),
    ),
    "benefits_analysis": (
        # Founder ruling 2026-10-27, item 2 (E19): no question about working — code computes the saving and the
        # read-back shows the working line for Confirm.
        (COST_OF_GAP, "quantifies what the gap costs, the cost of poor quality (p. 60)"),
        (IMPACT_TYPE, "says whether the impact is sustainable or one-off (p. 60)"),
        (REALISATION, "when the saving shows: by period, or a start date and sustained (p. 60)"),
        (FINANCE_CONTACT, "names the finance representative who validates the figure (p. 60, p. 62)"),
        (SOFT_BENEFITS, "states the soft benefits, each with how it will be seen, or says there are none (p. 60-63)"),
    ),
    "secondary_metrics": (
        (SIDE_EFFECT, "names at least one measure of a side effect of the change (p. 58)"),
        (NOT_THE_PRIMARY, "does not restate the primary metric (p. 58)"),
    ),
    "process_map_sipoc": (
        (AS_IS, "maps the process as it runs today, not the ideal (p. 80)"),
        (START_TO_END, "four to eight high-level steps from a start point to an end point (p. 26, p. 112)"),
        (ALL_SIX, "suppliers, inputs, steps, outputs, customers and the measures are all filled (p. 112)"),
        (CUSTOMERS_MATCH, "the customers agree with the Voice of the Customer (p. 112)"),
        (PERFORMANCE, "each step has a time (average, shortest, longest, with a unit) and how often it runs, and the "
                      "problems the team sees with who said them; the whole process has its lead time and how often "
                      "it runs; estimates are fine (R17)"),
    ),
    "issues_and_barriers": (
        # G-263 (the founder's review, 2026-10-27 11:25): the rule rubric.barrier_names checks, said as it is taught.
        (SPECIFIC, "names, for each roadblock, the site, system, team, person or rule of this project it concerns (a "
                   'date alone is not enough), or says "none identified at this stage" as a conscious answer '
                   "(p. 80, p. 82)"),
    ),
}

#: G-263: what the Belt is told when the barriers name nothing of this project's own — the `specific` criterion's
#: rule in plain words, given by the gate's check (rubric._code_half, DEF-R13).
SPECIFIC_MISSING = "Name the site, system or team that blocks you — as written, these barriers could belong to any project."

# ── the welcome (U17) — the founder's text, served by `welcome.py` and generated into the skill's [OPENING] ──

#: The welcome's first line.
WELCOME = ("Welcome — I'm here to coach you and your team through your improvement project step by step, so you "
           "don't need to be an expert. We'll work through five phases together:")
#: The five phases, each with its one-line purpose.
PHASES: tuple[tuple[str, str], ...] = (
    ("Define", "pin down the problem and who's solving it"),
    ("Measure", "get the real numbers"),
    ("Analyse", "find the true root cause"),
    ("Improve", "test and apply the fix"),
    ("Control", "make the gains stick"),
)
#: How Define is worked — the welcome's last line (the skill marks the phase's name bold).
HOW_DEFINE_IS_WORKED = (
    "Right now we're in **Define** — the most important phase, because a clear problem is half the solution. For "
    "each of the thirteen parts I'll explain what it is and why it matters, show you a finished example, then ask for "
    "yours. When all thirteen are agreed, you and your team review the Define report and approve it.")
#: How Define ends — the skill's section F, line by line as the skill wraps it; the overview serves it without the
#: skill's internal references ("(section 6)", "(requirement R6)").
HOW_DEFINE_ENDS: tuple[str, ...] = (
    "With all thirteen agreed, the Define report is assembled from the confirmed",
    "values only (section 6). It names the project lead and the Champion; the Belt and the team",
    "review it, and the project lead approves or rejects it on behalf of the team (requirement R6).",
    "**A rejection names the element(s) to change**, and coaching returns to those",
    "elements; every change is kept with its date (requirement R6).",
)


def element_of(field: str) -> str:
    """The element `field` is captured at: itself, or the position it is captured inside (the CTQs with the voice of
    the customer, the 5W2H with the problem statement, the metric registry with the baseline)."""
    return next((element for element, inside in _CAPTURED_INSIDE.items() if field in inside), field)


def criteria(field: str) -> tuple[tuple[str, str], ...]:
    """`(id, what it checks)` for the element `field` belongs to, in order; () for a field that is no element's."""
    return CRITERIA.get(element_of(field), ())


def criteria_lines(field: str) -> list[str]:
    """The element's criteria as the skill states them (and as the planner's judgment reads them): the opening line,
    then one `- `id` — text` line per criterion, each quoted. [] for a field that is no element's."""
    items = criteria(field)
    return [f"> {CRITERIA_HEAD}", *(f"> - `{cid}` — {text}" for cid, text in items)] if items else []


def element_names() -> dict[str, str]:
    """field -> its element's name, for every field the walk captures (a field captured inside a position carries
    that position's name)."""
    return {f: ELEMENT_NAMES[element] for element in ELEMENT_ORDER
            for f in (element, *_CAPTURED_INSIDE.get(element, ()))}


__all__ = ["CRITERIA", "CRITERIA_HEAD", "ELEMENT_NAMES", "ELEMENT_ORDER", "HOW_DEFINE_ENDS", "HOW_DEFINE_IS_WORKED",
           "PHASES", "WELCOME", "criteria", "criteria_lines", "element_names", "element_of"]
