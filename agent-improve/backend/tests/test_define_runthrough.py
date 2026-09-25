"""The Define run-through, read back — step 6.66 Part 7 (founder ruling 2026-09-25).

`scripts/define_runthrough.py` walks a scripted Belt through all twelve Define
fields on the real `POST /ask` route, once, with live models, tracing off, and
records every turn to `docs/runthrough/`. These tests READ that record — they
construct no input and call no model — and each proves one feature of
`docs/define_features.json` from what the product actually did.

**A record older than the source proves nothing**: every test here fails when
the record's product hash is not the current product source's
(`features.product_hash` — the board's source hash without `backend/tests/`, so
a new test never stales it). Re-run the script, commit the new record.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import pytest

_PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT / "tools" / "control_board"))

import features  # noqa: E402

#: A feature test's outcome is the MEASUREMENT, not a gate: failing, it is
#: recorded `skipped` (xfail) and the feature reads failing; passing, it is
#: recorded `passed` and the feature reads passing. Non-strict, so a pass is
#: never an error. Without this the landing commit's rule 4 would refuse the
#: harness for measuring what is not built yet (step 6.66, FOR FOUNDER).
pytestmark = pytest.mark.xfail(strict=False, reason="a Define feature test — its outcome is the measurement")

RECORDS = _PROJECT / "docs" / "runthrough"
ORDER = ("business_case", "team", "voc_summary", "problem_statement", "baseline_estimate",
         "project_scope", "goal_statement", "target_value", "target_date",
         "secondary_metrics", "process_map_sipoc", "issues_and_barriers")


def _load() -> dict[str, Any]:
    files = sorted(RECORDS.glob("define_runthrough_*.json"))
    if not files:
        pytest.fail("no run-through record in docs/runthrough/ — run scripts/define_runthrough.py")
    lines = json.loads(files[-1].read_text(encoding="utf-8"))
    by_kind: dict[str, Any] = {"turns": [l for l in lines if l.get("kind") == "turn"], "file": files[-1].name}
    for l in lines:
        if l.get("kind") != "turn":
            by_kind[l["kind"]] = l
    return by_kind


@pytest.fixture(scope="module")
def run() -> dict[str, Any]:
    r = _load()
    summary = r.get("summary") or {}
    now = features.product_hash()
    if summary.get("product_hash") != now:
        pytest.fail(f"{r['file']} ran on product source {summary.get('product_hash')}; it is now "
                    f"{now} — the record is stale, re-run the run-through")
    return r


def _structured(run: dict) -> dict[str, Any]:
    return (run.get("final_case") or {}).get("define_structured") or {}


# ── DEF-063 — the run-through itself ────────────────────────────────────────


def test_define_run_through(run) -> None:
    """All twelve fields confirmed through the real route, within the cap, untraced."""
    s = run["summary"]
    assert s["model_calls"] <= 150, s["model_calls"]
    assert s["langsmith_sends"] == 0
    assert s.get("stopped") == "done", f"the walk stopped: {s.get('stopped')} (stuck at {s.get('stuck_at')})"
    missing = [f for f in ORDER if not _structured(run).get(f)]
    assert not missing, f"not stored: {missing}"


# ── integrator ──────────────────────────────────────────────────────────────


def test_run_every_turn_answers_inside_its_time_limit(run) -> None:
    """DEF-002 — every turn a 200, inside the 45 s wall."""
    bad = [(t["n"], t["http"], t.get("seconds")) for t in run["turns"]
           if t["http"] != 200 or (t.get("seconds") or 0) > 45]
    assert not bad, bad


def test_run_sends_no_trace(run) -> None:
    """DEF-004 — tracing is a switch: zero LangSmith sends."""
    assert run["summary"]["langsmith_sends"] == 0


# ── lane A — coaching ───────────────────────────────────────────────────────


def _teaching_turns(run: dict) -> list[dict]:
    return [t for t in run["turns"] if t.get("move") in ("teach", "store_and_advance") and t.get("field")]


def test_run_an_untaught_field_is_taught_example_before_ask(run) -> None:
    """DEF-005 — a field's first reply carries an explanation, an example and one ask."""
    turns = _teaching_turns(run)
    assert turns, "no teaching turn recorded"
    bad = [(t["n"], t["field"]) for t in turns
           if not all((t["reply"] or {}).get(k) for k in ("explanation", "example", "prompt"))]
    assert not bad, f"teaching replies missing a block: {bad}"


def test_run_every_turn_states_step_n_of_12(run) -> None:
    """DEF-006 — 'Step n of 12', n the current field's position."""
    bad = []
    for t in run["turns"]:
        if t["http"] != 200 or not t.get("field"):
            continue
        n = ORDER.index(t["field"]) + 1 if t["field"] in ORDER else None
        progress_text = (t["reply"] or {}).get("progress") or ""
        if not re.search(rf"\b{n}\s+of\s+12\b", progress_text):
            bad.append((t["n"], t["field"], progress_text))
    assert not bad, bad


def test_run_a_sufficient_answer_is_read_back_and_not_stored(run) -> None:
    """DEF-007 — a read-back holds the value pending; nothing is stored until Confirm."""
    reads = [t for t in run["turns"] if t.get("move") == "read_back"]
    assert reads, "no read-back recorded"
    bad = [(t["n"], t["field"]) for t in reads if t["field"] in t.get("stored_keys", [])
           and not any(p.get("field") == t["field"] and p.get("move") == "store_and_advance"
                       for p in run["turns"] if p["n"] < t["n"])]
    assert not bad, f"stored at read-back: {bad}"


def test_run_a_confirm_click_stores_and_advances(run) -> None:
    """DEF-008 — Confirm stores the pending value and the next field becomes current."""
    turns = run["turns"]
    clicks = [i for i, t in enumerate(turns) if t.get("action") == "confirm"]
    assert clicks, "no Confirm click recorded"
    bad = []
    for i in clicks:
        t, before = turns[i], turns[i - 1]
        if t.get("move") != "store_and_advance" or before["field"] not in t.get("stored_keys", []):
            bad.append((t["n"], before["field"], t.get("move")))
    assert not bad, bad


def test_run_a_change_click_reopens_the_field_with_the_belts_words(run) -> None:
    """DEF-010 — Change reopens the field and shows the Belt's current words."""
    t = next((t for t in run["turns"] if t.get("action") == "change"), None)
    assert t, "no Change click recorded"
    assert t.get("move") == "challenge" and t.get("field") == "voc_summary", (t.get("move"), t.get("field"))
    words = (t["reply"] or {}).get("answer") or ""
    assert "suppliers" in words.lower(), "the reply does not show the Belt's words"


def test_run_a_weak_answer_is_challenged_not_completed(run) -> None:
    """DEF-011 — a weak answer is challenged and not read back as complete."""
    t = next((t for t in run["turns"] if t.get("why") == "probe: weak first answer"), None)
    assert t, "no weak-answer probe recorded"
    assert t.get("move") == "challenge", t.get("move")
    assert "problem_statement" not in t.get("stored_keys", [])


def test_run_a_question_is_answered_and_the_field_asked_again(run) -> None:
    """DEF-012 — 'where do we stand?' is answered; the field stays current."""
    t = next((t for t in run["turns"] if t.get("why") == "probe: where do we stand"), None)
    assert t, "no question probe recorded"
    assert t.get("move") == "respond" and t.get("field") == "project_scope", (t.get("move"), t.get("field"))


def _declared_ok(field: str, value: Any) -> str:
    """'' if `value` validates against DefineOutput's declared type for `field`."""
    from pydantic import TypeAdapter, ValidationError
    from backend.phases.define.schema import DefineOutput
    try:
        TypeAdapter(DefineOutput.model_fields[field].annotation).validate_python(value)
        return ""
    except ValidationError as exc:
        return str(exc).splitlines()[0]


@pytest.mark.parametrize("n,field", list(enumerate(ORDER, 1)))
def test_run_field_is_captured_after_confirm(run, n: int, field: str) -> None:
    """DEF-025..036 — field n of 12 is stored after Confirm, in its declared type."""
    value = _structured(run).get(field)
    assert value, f"field {n} ({field}) was not stored"
    problem = _declared_ok(field, value)
    assert not problem, f"field {n} ({field}) is stored but not in its declared type: {problem}"


def test_run_a_confirmed_value_survives_later_turns(run) -> None:
    """DEF-037 — the business case confirmed first is still there at the end."""
    assert _structured(run).get("business_case"), "the first confirmed field is gone"


# ── lane B — the gate ───────────────────────────────────────────────────────


def test_run_a_complete_case_assembles_a_gate_document(run) -> None:
    """DEF-041 — once all twelve are confirmed, the gate review returns a document."""
    review = run.get("gate_review") or {}
    assert review.get("http") == 200, review
    body = review.get("body") or {}
    assert body.get("passed") is True, body.get("missing_fields")
    assert body.get("document"), "the review returned no document"
