"""ADR-0093 "Element templates and the Gate view", build step 1 — the templates and the row builder.

A test per element against the values of IMPR-2026-A99 (the founder test of 15 October 2026, as the approved
mockups readback_card_mockup.html and gate_view_mockup.html show them): each element's rows are its script
criteria in the script's order, with the value that goes into the Gate and its source; free text is read from
the judgment's quoted spans only where a span is verbatim in the Belt's answer (option (b), the safeguard); a
required criterion a code check finds open closes Confirm. Pure functions — no model call, nothing stored.
"""
from __future__ import annotations

import json

import pytest

from backend.phases.define import templates
from backend.phases.define.schema import DEFINE_FIELD_ORDER

BUSINESS_CASE = ("Since January 2026, 38% of complaints in the Austrian field service close later than 10 working "
                 "days, against a promise of 5. About 1,200 complaints a year; each late one costs about €45 extra "
                 "handling, about €20,000 a year, and two key accounts have escalated.")

#: IMPR-2026-A99's confirmed values, as the mockups show them.
A99: dict = {
    "business_case": BUSINESS_CASE,
    "team": [
        {"name": "Vassilis Pangalis", "role": "Project lead", "function": "Green Belt"},
        {"name": "Katharina Huber", "role": "Champion", "function": "Head of Field Service Austria",
         "training": "none"},
        {"name": "Markus Steiner", "role": "Process owner", "function": "Service Desk Lead Vienna",
         "training": "none"},
        {"name": "Elena Gruber", "role": "Team member", "function": "Field Technician Coordinator",
         "training": "half-day data collection"},
    ],
    "voc_summary": "Business customers want complaints closed quickly and to be told what happens next.",
    "critical_to_quality": [
        {"customer": "Business customers (external)", "need": "Complaint closed quickly and reliably",
         "requirement": "Closed within 5 working days of logging, for ≥ 95% of complaints"},
        {"customer": "Business customers; account managers (internal)", "need": "Told what happens next",
         "requirement": "Next step communicated within 1 working day, for 100% of complaints"},
    ],
    "problem_statement": ("Since January 2026, 38% of customer complaints in the Austrian field service take longer "
                          "than 10 working days to close, at the step between technician visit completed and "
                          "complaint closed in the ticket system."),
    "problem_5w2h": {
        "what": "Customer complaints in field service take too long to close",
        "where": "Austrian field service · step: technician visit completed → complaint closed in the ticket system",
        "when": "Since January 2026, all weekdays, worst at month end",
        "who": "Business customers, account managers, service desk team",
        "why": "Repeat calls, escalations, risk to two key accounts",
        "how": "Customers call back for status; account managers receive escalation e-mails",
        "how_much": "38% of complaints take longer than 10 working days",
    },
    "metric_definitions": [{"name": "Late-closure rate", "unit": "%",
                            "meaning": "share of complaints closed later than 10 working days after logging"}],
    "baseline_estimate": {"value": 38.0, "unit": "%", "direction": None, "is_estimate": False,
                          "raw": "38% · January–June 2026 · ticket system export; feeds the monthly service-level KPI"},
    "project_scope": {"in_scope": ("Complaints logged by business customers of the Austrian field service, from "
                                   "logging in the ticket system until the customer confirms closure"),
                      "out_scope": "Warranty claims · complaints from Germany and Switzerland · the repair work itself"},
    "goal_statement": ("Reduce the share of complaints closed later than 10 working days from 38% to under 10% by "
                       "31 March 2027."),
    "target_value": {"value": 10.0, "unit": "%", "direction": "<=", "is_estimate": False, "raw": "under 10%"},
    "target_date": "2027-03-31",
    "benefits_analysis": {"cost_of_gap": "About €20,500 a year today", "impact_type": "Sustainable, every year",
                          "realisation_schedule": "about €3,800 per quarter, from the first full quarter after the change",
                          "finance_contact": "Martina Koller, controller Field Service"},
    "secondary_metrics": "1. Customer satisfaction score 2. First-time fix rate",
    "process_map_sipoc": {
        "suppliers": "Business customers; Service desk; Field technicians",
        "inputs": "Complaint; Customer and contract data; Visit report",
        "process_steps": [
            {"id": "S1", "name": "Log complaint", "duration": {"avg": "15 min", "min": "5 min", "max": "40 min"},
             "runs_per_period": "100 per month", "problems": []},
            {"id": "S2", "name": "Schedule technician visit", "duration": {"avg": "2 days"},
             "runs_per_period": "100 per month", "problems": []},
            {"id": "S3", "name": "Close complaint in ticket system", "duration": {"avg": "4 days"},
             "runs_per_period": "100 per month", "problems": []},
            {"id": "S4", "name": "Inform customer", "duration": {"avg": "1 day"},
             "runs_per_period": "100 per month", "problems": []},
        ],
        "outputs": "Closed complaint; Closure confirmation",
        "customers": "Business customers; Account managers",
        "process_metrics": "Time from logging to closure",
        "process_performance": {"lead_time": "8 working days", "runs_per_period": "100 per month"},
    },
    "issues_and_barriers": "1. Month-end peak in the service desk 2. Ticket system change freeze until January",
}


def _values(v):
    """Every text a row shows — a table's cells, a list's items."""
    if isinstance(v, dict):
        return [c for row in v.get("rows") or [] for c in row]
    if isinstance(v, list):
        return [str(x) for x in v]
    return [] if v is None else [str(v)]


def test_every_element_has_a_template_for_each_script_criterion_in_the_scripts_order() -> None:
    assert list(templates.TEMPLATES) == list(DEFINE_FIELD_ORDER)
    for field in DEFINE_FIELD_ORDER:
        ids = [cid for cid, _ in templates.criteria(field)]
        assert ids, f"{field}: the script lists no criterion"
        assert [r["id"] for r in templates.rows(field, A99)] == ids, field
        assert set(templates.TEMPLATES[field]) == set(ids), f"{field}: template and script disagree"


@pytest.mark.parametrize("field", DEFINE_FIELD_ORDER)
def test_each_a99_element_reads_back_complete_with_no_json(field: str) -> None:
    card = templates.card(field, A99)
    assert card["confirm"] and card["met"] == card["total"], (field, card["missing"])
    assert card["n"] == DEFINE_FIELD_ORDER.index(field) + 1 and card["of"] == 13
    for row in card["rows"]:
        for text in _values(row["value"]):
            assert not text.lstrip().startswith(("{", "[")), (field, row["id"], text)
    assert not str(card.get("answer") or "").lstrip().startswith("{"), card.get("answer")


def test_the_structured_elements_show_the_values_that_go_into_the_gate() -> None:
    team = {r["id"]: r for r in templates.rows("team", A99)}
    assert team["champion"]["value"] == "Katharina Huber" and team["process-owner"]["value"] == "Markus Steiner"
    assert team["people"]["value"]["rows"][2] == ["Markus Steiner", "Process owner", "Service Desk Lead Vienna"]
    assert "Elena Gruber: half-day data collection" in team["training"]["value"]
    voc = {r["id"]: r for r in templates.rows("voc_summary", A99)}
    assert voc["ctq"]["value"]["rows"][0][2].startswith("Closed within 5 working days")
    problem = {r["id"]: r for r in templates.rows("problem_statement", A99)}
    assert problem["5w2h"]["value"]["rows"][6] == ["How much?", "38% of complaints take longer than 10 working days"]
    assert problem["located"]["value"].startswith("Austrian field service · step")
    assert templates.card("problem_statement", A99)["statement"] == A99["problem_statement"]
    metric = {r["id"]: r for r in templates.rows("baseline_estimate", A99)}
    assert metric["one-primary"]["value"] == "Late-closure rate (%)" and metric["quantified"]["value"] == "38%"
    target = {r["id"]: r for r in templates.rows("target_value", A99)}
    assert target["number-and-unit"]["value"] == "at most 10%"
    assert target["direction"]["value"] == "38% → at most 10%"
    assert templates.rows("target_date", A99)[0]["value"] == "31 March 2027"
    sipoc = {r["id"]: r for r in templates.rows("process_map_sipoc", A99)}
    assert sipoc["start-to-end"]["value"] == "4 steps: Log complaint → Inform customer"
    assert sipoc["all-six"]["value"] == "all six filled"
    assert sipoc["performance"]["value"]["rows"][0][:2] == ["S1 · Log complaint", "15 minutes (5 minutes to 40 minutes)"]
    assert sipoc["performance"]["value"]["rows"][-1][0] == "Whole process"
    assert templates.rows("issues_and_barriers", A99)[0]["value"] == [
        "Month-end peak in the service desk", "Ticket system change freeze until January"]
    assert templates.rows("secondary_metrics", A99)[0]["value"] == ["Customer satisfaction score", "First-time fix rate"]


def test_free_text_is_read_from_verbatim_spans_and_otherwise_shown_once_in_the_answer() -> None:
    """Option (b) and its safeguard: a span that is a verbatim substring of the Belt's answer is the row's value;
    a paraphrase, a span of another element's criterion and an unknown id are dropped, and their rows show no
    value of their own — the whole answer is shown once, marked "in your answer"."""
    spans = templates.verbatim_spans({
        "what": "38% of complaints in the Austrian field service close later than 10 working days",
        "where-when": "Since January 2026",
        "cost": "it costs us around twenty thousand euros",           # a paraphrase: not in the answer
        "champion": "Katharina Huber",                                # not a business-case criterion
        "invented": "38%",
    }, "business_case", BUSINESS_CASE)
    assert spans == {"what": "38% of complaints in the Austrian field service close later than 10 working days",
                     "where-when": "Since January 2026"}
    card = templates.card("business_case", A99, spans=spans, belt_words=BUSINESS_CASE)
    rows = {r["id"]: r for r in card["rows"]}
    assert rows["what"]["value"] == spans["what"] and rows["what"]["source"] == templates.YOUR_ANSWER
    assert rows["cost"]["value"] is None and rows["cost"]["source"] == templates.IN_ANSWER
    assert card["answer"] == BUSINESS_CASE, "the whole answer, shown once"
    # A span is checked against every text given: the Belt's words AND the text a Confirm stores.
    assert templates.verbatim_spans({"what": "38% of complaints"}, "business_case", BUSINESS_CASE, "38 % of complaints") == {}
    # Quotes around a span are not part of it.
    assert templates.verbatim_spans({"cost": "“about €45 extra handling”"}, "business_case", BUSINESS_CASE) == {
        "cost": "about €45 extra handling"}


def test_a_value_read_from_a_file_and_a_calculated_one_name_their_source() -> None:
    rows = templates.rows("team", A99, upload="team_list.xlsx")
    assert {r["source"] for r in rows} == {templates.FROM_FILE}
    from backend.phases import calculations
    row = calculations.run("define", "benefits_analysis", A99, {"unit_cost": "€45", "annual_volume": "1200"}, 30)
    assert row is not None
    calc = {**A99, "computation_results": [row]}
    cost = templates.rows("benefits_analysis", calc)[0]
    assert cost["source"] == templates.CALCULATED and cost["value"] == "€20,520 per year", cost
    assert "1,200" in cost["formula"] and "€45" in cost["formula"], cost["formula"]
    others = templates.rows("benefits_analysis", calc)[1:]
    assert [r["source"] for r in others] == [templates.YOUR_ANSWER] * 3


def test_a_required_criterion_a_code_check_finds_open_closes_confirm() -> None:
    """ADR-0093 decision 2: the code checks are the ones a Confirm is refused on (ADR-0088's parts, a number, a
    date, the SIPOC's columns) and both scope halves; anything else is the judgment's to meet."""
    no_training = [{k: v for k, v in m.items() if k != "training"} for m in A99["team"]]
    card = templates.card("team", {**A99, "team": no_training})
    assert not card["confirm"] and card["missing"] == ["Training needed"], card["missing"]
    assert card["ask"] == "Still needed before you can confirm: training needed."
    assert templates.open_required("team", {**A99, "team": no_training}) == ["training"]
    assert templates.open_required("project_scope", {**A99, "project_scope": {"in_scope": "Austria"}}) == ["in-and-out"]
    assert templates.open_required("target_date", {**A99, "target_date": "next spring"}) == ["a-date"]
    assert templates.open_required("process_map_sipoc", {**A99, "process_map_sipoc": {
        k: v for k, v in A99["process_map_sipoc"].items() if k != "outputs"}}) == ["all-six"]
    # A criterion with no code check follows the judgment.
    assert templates.open_required("business_case", A99, judged=False) == [
        cid for cid, _ in templates.criteria("business_case")]


def test_the_strip_names_the_element_and_its_gate_section() -> None:
    assert templates.strip("benefits_analysis")["text"] == (
        "✓ Element 10 · Benefits analysis confirmed — the Gate document is updated (section B).")
    assert [templates.section_of(f) for f in DEFINE_FIELD_ORDER] == [
        "B", "A", "D", "C", "E", "C", "C", "E", "E", "B", "E", "F", "G"]


def test_the_judgment_carries_the_spans_in_its_one_call() -> None:
    """T47: still one judgment call — the spans are a field of its structured output, as ADR-0077's calculation
    inputs are; the description is what the model reads (§31)."""
    from backend.core.substate import SufficiencyJudgment
    field = SufficiencyJudgment.model_fields["criterion_spans"]
    assert field.default is None and "character for character" in (field.description or "")
    assert json.loads(SufficiencyJudgment(verdict="sufficient", reason="r", criterion_spans={"what": "x"})
                      .model_dump_json())["criterion_spans"] == {"what": "x"}
