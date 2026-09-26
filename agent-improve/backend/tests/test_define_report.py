"""R5 — the Define gate is a readable DEFINE REPORT, not a field checklist.

Founder requirement R5 (`docs/requirements/define.md`, 2026-09-26): seven
sections — 1 project and team, 2 business case and benefits, 3 problem,
objective, scope with a 5W2H diagram, 4 VOC and CTQs, 5 metrics (one primary,
baseline to target, secondaries), 6 high-level process with a SIPOC diagram
(as-is), 7 issues and barriers — assembled from CONFIRMED values only.

Proven three ways:
  the builder    `phases/define/report.define_report`, on a complete case
  the route      GET /gate/review through the REAL /ask route and graph: after
                 a read-back (a value PENDING) the report does not show it;
                 after the Belt's Confirm it does, in the Belt's words
  the screen     the gate screen's `defineReportHtml`, run in node on the
                 route's own report: seven sections, the 5W2H and the SIPOC
                 drawn, the Belt's text escaped
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from backend.middleware.coherence import CoherenceMiddleware
from backend.middleware.grader import DMAICGraderMiddleware
from backend.phases.define.report import REPORT_SECTIONS, define_report, element_of
from backend.phases.define.schema import DEFINE_REQUIRED_FOR_GATE_FIELDS
from backend.tests.test_wiring import BELT, CONFIRM, OPENING, _coach
from backend.validation.schemas import CoachingGraderVerdict, CoherenceResult

UI = Path(__file__).resolve().parents[2] / "ui" / "index.html"
CASE_ID = "IMPR-TEST-REPORT"

COMPLETE: dict[str, Any] = {
    "business_case": "During H1 2026, 23% of invoices were paid late; about £62k a year.",
    "team": [{"name": "Priya", "role": "Belt", "function": "lead"},
             {"name": "Tom", "role": "Champion", "function": "<b>sponsor</b>"}],
    "voc_summary": "Suppliers need paying on terms.",
    "critical_to_quality": [{"customer": "suppliers", "need": "on time",
                             "requirement": "paid within 30 days"}],
    "problem_5w2h": {k: f"{k} answer" for k in
                     ("what", "where", "when", "who", "why", "how", "how_much")},
    "problem_statement": "23% of invoices paid late, H1 2026.",
    "metric_definitions": [{"name": "late_payment_rate", "unit": "%", "meaning": "paid after 30 days"},
                           {"name": "cycle_days", "unit": "days", "meaning": "invoice to payment"}],
    "baseline_estimate": "23%", "target_value": "5%", "target_date": "2027-03-31",
    "project_scope": {"in_scope": "PO invoices", "out_scope": "payroll"},
    "goal_statement": "23% to 5% by March 2027",
    "benefits_analysis": {"cost_of_gap": "£68k", "impact_type": "sustainable",
                          "realisation_schedule": "Q2 2027", "finance_contact": "Sam"},
    "secondary_metrics": "supplier queries",
    "process_map_sipoc": {"suppliers": "s", "inputs": "i", "process_steps": "p",
                          "outputs": "o", "customers": "c", "process_metrics": "days"},
    "issues_and_barriers": "ERP freeze until January",
    "computation_results": [{"tool": "calculate_expected_savings",
                             "result": {"annual_savings": "68000", "calculation_note": "(23-5)x42000x9"}}],
}


# ── the builder ───────────────────────────────────────────────────────────


def test_the_report_has_r5s_seven_sections_in_order() -> None:
    rep = define_report(COMPLETE, {"title": "AP"}, [])
    assert [(s["n"], s["title"]) for s in rep["sections"]] == [
        (1, "Project and team"), (2, "Business case and benefits"),
        (3, "Problem, objective and scope"), (4, "Voice of the customer and CTQs"),
        (5, "Metrics"), (6, "High-level process (as-is)"), (7, "Issues and barriers")]
    assert rep["complete"] and rep["missing"] == []
    assert all(s["complete"] for s in rep["sections"])


def test_every_gate_field_is_in_exactly_one_section() -> None:
    placed = [f for _, _, fields in REPORT_SECTIONS for f in fields]
    assert sorted(placed) == sorted(DEFINE_REQUIRED_FOR_GATE_FIELDS)


def test_the_diagrams_and_the_metrics_are_data_from_the_confirmed_values() -> None:
    rep = define_report(COMPLETE, {"title": "AP"}, [])
    sec = {s["n"]: s for s in rep["sections"]}
    assert [r["key"] for r in sec[3]["five_w_two_h"]] == [
        "what", "where", "when", "who", "why", "how", "how_much"]
    assert sec[3]["five_w_two_h"][6]["answer"] == "how_much answer"
    assert sec[5]["primary"]["name"] == "late_payment_rate", "the primary is the first registry entry"
    assert [m["name"] for m in sec[5]["other_registered"]] == ["cycle_days"]
    assert (sec[5]["baseline"], sec[5]["target"]) == ("23%", "5%")
    assert sec[6]["sipoc"]["process_metrics"] == "days"
    assert sec[2]["savings"]["result"]["annual_savings"] == "68000", "the savings calculation feeds it"


def test_an_incomplete_case_names_what_is_missing_and_which_element() -> None:
    partial = {k: v for k, v in COMPLETE.items() if k not in ("problem_5w2h", "team")}
    rep = define_report(partial, {}, [])
    assert not rep["complete"]
    assert set(rep["missing"]) == {"problem_5w2h", "team"}
    unconfirmed = {e["field"] for e in rep["elements"] if not e["confirmed"]}
    assert unconfirmed == {"team", element_of("problem_5w2h")} == {"team", "problem_statement"}


def test_r6_history_rides_on_the_report_only_for_changed_values() -> None:
    log = [{"field": "goal_statement", "phase": "define", "turn": 7, "value": "to 8%",
            "timestamp": "2026-09-26T10:00:00+00:00"},
           {"field": "goal_statement", "phase": "define", "turn": 9, "value": "to 5%",
            "timestamp": "2026-09-27T10:00:00+00:00"},
           {"field": "team", "phase": "define", "turn": 2, "value": [],
            "timestamp": "2026-09-26T09:00:00+00:00"}]
    rep = define_report(COMPLETE, {}, log)
    assert set(rep["history"]) == {"goal_statement"}
    assert rep["history"]["goal_statement"]["first"]["value"] == "to 8%"


# ── the route: confirmed values only, through the real /ask ───────────────


@pytest.fixture
def reports(monkeypatch, stub_planner) -> list[dict]:
    """Opening, answer (a read-back: PENDING), Confirm — through the real route
    and graph; the Define report read after each turn by GET /gate/review."""
    from backend.app import app
    from backend.core import graph as graph_mod
    from backend.gateway import routes
    from backend.phases import nodes_common
    from backend.storage.models import CaseDocument

    saver, store = InMemorySaver(), InMemoryStore()
    monkeypatch.setattr(graph_mod, "_persistence", lambda: (saver, store))
    graph_mod.get_graph.cache_clear()
    case = CaseDocument.new(case_id=CASE_ID, title="report proof", belt_level="green",
                            leader="Priya Shah", department="Finance",
                            target_date="2027-03-31", team=[])

    async def load(_cid: str):
        return case

    async def save(_c):
        return None

    monkeypatch.setattr(routes.blob, "storage_configured", lambda: True)
    monkeypatch.setattr(routes.blob, "load_case", load)
    monkeypatch.setattr(routes.blob, "save_case", save)
    monkeypatch.setattr("backend.core.store.get_store", lambda: store)
    monkeypatch.setattr(graph_mod, "get_store", lambda: store)
    monkeypatch.setattr(routes, "_mirror_asks", lambda *a, **k: None)
    planner_llm = nodes_common.get_llm
    monkeypatch.setattr(nodes_common, "get_llm",
                        lambda role, **kw: _coach() if role == "coach" else planner_llm(role, **kw))

    async def coherent(self, belt: str, coach: str) -> CoherenceResult:
        return CoherenceResult(coherent=True, is_conclusive=True, is_parroting=False,
                               on_topic=True, reason="")

    async def passing(self, belt: str, coach: str) -> CoachingGraderVerdict:
        return CoachingGraderVerdict(criteria=[])

    monkeypatch.setattr(CoherenceMiddleware, "_check", coherent)
    monkeypatch.setattr(DMAICGraderMiddleware, "_grade", passing)
    client = TestClient(app)
    out = []
    try:
        for message in (OPENING, BELT, CONFIRM):
            r = client.post("/ask", json={"case_id": CASE_ID, "user": "wired",
                                          "message": message, "phase": "define"})
            assert r.status_code == 200, r.text
            review = client.get(f"/gate/review/{CASE_ID}/define")
            assert review.status_code == 200, review.text
            out.append(review.json())
    finally:
        graph_mod.get_graph.cache_clear()
    return out


def test_the_report_shows_a_value_only_after_the_belt_confirms_it(reports) -> None:
    def business_case(body: dict) -> Any:
        return next(s for s in body["report"]["sections"] if s["n"] == 2)["business_case"]
    assert business_case(reports[1]) is None, "a PENDING read-back value reached the report"
    assert business_case(reports[2]) == BELT, "the confirmed value, in the Belt's words"
    assert "business_case" not in reports[2]["report"]["missing"]


def test_the_other_phases_carry_no_define_report(monkeypatch) -> None:
    from backend.app import app
    from backend.gateway import routes
    from backend.storage.models import CaseDocument
    case = CaseDocument.new(case_id="IMPR-TEST-RM", title="t", belt_level="green", leader="L",
                            department="D", target_date="2027-03-31", team=[])

    async def load(_cid: str):
        return case
    monkeypatch.setattr(routes.blob, "storage_configured", lambda: True)
    monkeypatch.setattr(routes.blob, "load_case", load)
    body = TestClient(app).get("/gate/review/IMPR-TEST-RM/measure").json()
    assert body["report"] is None


# ── the screen: the gate screen's renderer, in node ───────────────────────


def _fn(src: str, name: str) -> str:
    m = re.search(r"^(?:async )?function " + name + r"\(.*?^\}", src, re.M | re.S)
    assert m, f"{name} not found in ui/index.html"
    return m.group(0)


def _render(report: dict, passed: bool = False) -> str:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed — the report cannot be rendered; this is NOT a pass")
    src = UI.read_text(encoding="utf-8")
    js = (_fn(src, "escapeHtml") + "\n" + _fn(src, "defineReportHtml")
          + f"\nprocess.stdout.write(defineReportHtml({json.dumps(report)}, {json.dumps(passed)}));")
    out = subprocess.run([node, "-e", js], capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0, out.stderr
    return out.stdout


def test_the_gate_screen_draws_the_seven_sections_and_both_diagrams() -> None:
    html = _render(define_report(COMPLETE, {"title": "AP"}, []))
    assert all(f">{n} · " in html for n in range(1, 8)), "a section is missing from the screen"
    assert "How does it show up?" in html and "how_much answer" in html, "the 5W2H diagram"
    assert 'id="report-sipoc"' in html, "the SIPOC diagram's host"
    assert "paid within 30 days" in html, "the CTQ table"
    assert "late_payment_rate (%)" in html and "23% → 5%" in html, "one primary, baseline to target"
    assert "&lt;b&gt;sponsor" in html and "<b>sponsor</b>" not in html, "the Belt's text is escaped"


def test_the_gate_screen_names_what_is_still_to_confirm() -> None:
    partial = {k: v for k, v in COMPLETE.items() if k != "team"}
    html = _render(define_report(partial, {}, []))
    assert "Still to confirm" in html and "team" in html


def test_the_v1_gate_document_is_gone_from_the_define_path() -> None:
    """Step 10.2's screen moves onto the Define path: renderGate's Define branch
    draws the report, and the 26 retired v1 keys no longer build a document."""
    src = _fn(UI.read_text(encoding="utf-8"), "renderGate")
    assert "renderDefineReport(" in src
    assert "business_case_rationale" not in src and "structured.sipoc" not in src
