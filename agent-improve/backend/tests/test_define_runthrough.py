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
import os
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
from backend.phases.define.schema import DEFINE_FIELD_ORDER, DEFINE_POSITIONS  # noqa: E402

ORDER = DEFINE_FIELD_ORDER

def _not_written(fid: str) -> None:
    """A feature not built yet — named so the board reads it as not started (founder, 2026-10-12)."""
    pytest.fail(f"{fid}: not written yet — the lane that takes this feature writes it")



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
    # Founder ruling 1, 2026-09-29: the board asks what the latest record proves about the code it
    # ran on (`features.earlier_proof`). That run sets AWAIT_ENV, and the recorder never records it.
    if summary.get("product_hash") != now and os.environ.get(features.AWAIT_ENV) != "1":
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
    # G-153 (founder ruling 2026-10-12): a cut-off reply is answered in code; more than one a run fails.
    assert "cut_offs" in s, "the record does not count its cut-off calls (G-153)"
    assert s["cut_offs"]["count"] <= 1, f"{s['cut_offs']['count']} calls cut off at their token limit: {s['cut_offs']}"
    missing = [f for f in ORDER if not _structured(run).get(f)]
    assert not missing, f"not stored: {missing}"


# ── integrator ──────────────────────────────────────────────────────────────


def test_run_every_turn_answers_inside_its_time_limit(run) -> None:
    """DEF-002 — every turn a 200 and a COACHED reply, inside the 45 s wall: a
    fallback (the executor's backstop or timeout containment) is not coaching."""
    bad = [(t["n"], t["http"], t.get("seconds"), "fallback" if t.get("fallback") else "")
           for t in run["turns"]
           if t["http"] != 200 or (t.get("seconds") or 0) > 45 or t.get("fallback")]
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


def test_run_every_turn_states_its_step(run) -> None:
    """DEF-006 — 'Step n of 13', n the current element's position."""
    bad = []
    for t in run["turns"]:
        if t["http"] != 200 or not t.get("field"):
            continue
        n = ORDER.index(t["field"]) + 1 if t["field"] in ORDER else None
        progress_text = (t["reply"] or {}).get("progress") or ""
        if not re.search(rf"\b{n}\s+of\s+{DEFINE_POSITIONS}\b", progress_text):
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
    """DEF-037 — the business case confirmed first is still there once the
    SIPOC (field 11) has been captured, many turns later."""
    s = _structured(run)
    assert s.get("process_map_sipoc"), "the SIPOC was never captured, so survival to it is unproven"
    assert s.get("business_case"), "the first confirmed field is gone"


# ── lane B — the gate ───────────────────────────────────────────────────────


def test_run_no_answer_turn_ends_in_a_code_written_reply(run) -> None:
    """DEF-160 — G-128, ADR-0068's verification: in the live run-through no answer turn (the Belt
    answered: challenge, read back, respond) ends in a reply written in code because the call
    limit ended the coach. Found on IMPR-2026-C8A: turns 10, 26 and 31."""
    bad = [(t["n"], t.get("move")) for t in run["turns"]
           if t.get("fallback") and t.get("move") in ("challenge", "read_back", "respond")]
    assert not bad, f"answer turns ended in a code-written reply: {bad}"


def test_run_a_complete_define_passes_the_gate_rubric(run) -> None:
    """DEF-159 — G-129 (R7): once all thirteen elements are confirmed, the submission passes the
    Define rubric — an answer the element's own criteria accepted is not failed at the gate for
    its wording ("barriers" for "roadblocks", DEF-R13). Found on IMPR-2026-C8A."""
    review = (run.get("gate_review") or {}).get("body") or {}
    assert review.get("passed") is True, "the run did not complete Define; this proof needs a complete run"
    submit = (run.get("gate_submit") or {}).get("body") or {}
    assert submit.get("passed") is True, submit.get("missing_fields")


def test_run_a_complete_case_assembles_a_gate_document(run) -> None:
    """DEF-041 — once all twelve are confirmed, the gate review returns a document."""
    review = run.get("gate_review") or {}
    assert review.get("http") == 200, review
    body = review.get("body") or {}
    assert body.get("passed") is True, body.get("missing_fields")
    assert body.get("document"), "the review returned no document"


# ── stubs: named by a feature, not written yet (6.67) ──────────────────────

def test_runthrough_metric_meaning_comes_from_the_registry(run) -> None:
    """DEF-018 — R2, on the live run: when the Belt's metric first comes up (the read-back of position
    5), the reply explains what it means — the registry entry the Belt gave, word for word, never
    invented — why Define cares and how to read it, in a line written in code."""
    reg = (_structured(run).get("metric_definitions") or [{}])[0]
    meaning = str(reg.get("meaning") or "").rstrip(".")
    assert meaning, "the run registered no metric meaning"
    backs = [t for t in run["turns"] if (t.get("reply") or {}).get("move") == "read_back"
             and (t.get("reply") or {}).get("move_field") == "baseline_estimate"]
    assert backs, "no read-back of position 5 in the run"
    answer = str(backs[-1]["reply"].get("answer") or "")
    assert "About your metric" in answer and meaning in answer, answer[-500:]
    assert "Measure checks this baseline" in answer, answer[-500:]


def test_runthrough_no_reply_carries_a_link(run) -> None:
    """DEF-019 — the coach teaches in its own voice and never hands the Belt a URL. (a) In code: a
    link in any of the coach's words is removed (a markdown link keeps its words), so no prompt has
    to be obeyed for it. (b) Live, on the latest run-through: no reply on any turn — Define's and
    Measure's — carries a link, and none answers by deferring to a source ("according to the
    manual"); the method is taught, not referred to."""
    import re

    from backend.phases.nodes_common import _without_links

    assert _without_links("See [the method](https://example.com/sipoc) first.") == "See the method first."
    assert _without_links("Read www.example.com/guide before you start.") == "Read before you start."
    assert _without_links("No link here.") == "No link here."
    link = re.compile(r"https?://|www\.|\]\(")
    deferral = re.compile(r"according to (the|our) (manual|book|guide|source)|as the (manual|book|guide) says"
                          r"|see (the|our) (manual|book|guide)", re.I)
    turns = [*run["turns"], *([run["measure_turn"]] if run.get("measure_turn") else [])]
    assert turns, "the record holds no turns"
    for r in turns:
        said = json.dumps(r.get("reply") or r.get("body") or {}, ensure_ascii=False)
        assert not link.search(said), f"turn {r.get('n')} hands the Belt a link: {said[:300]}"
        assert not deferral.search(said), f"turn {r.get('n')} defers to a source: {said[:300]}"


def test_every_define_row_is_green_on_the_run_through_case() -> None:
    """DEF-064 — not written yet (a stub, step 6.67): Define end to end: on ONE fresh case carrying an upload, every Define capability row's own check is green after one run."""
    _not_written('DEF-064')


# ── R3 — the validation layer, repeated on the live model ───────────────────


def test_run_the_validation_layer_is_consistent_over_five_runs() -> None:
    """R3's repeated-run test, on the LIVE planner model, five runs each: a
    business case that proposes a solution is challenged naming
    `no-cause-no-fix` every time; one with all five elements is read back every
    time. Read from the newest `validation_repeat_*.json`
    (`scripts/validation_repeat.py`, which the run-through runs first), bound to
    the current product source like the run-through's own record."""
    files = sorted(RECORDS.glob("validation_repeat_*.json"))
    if not files:
        pytest.fail("no validation_repeat record — run scripts/validation_repeat.py")
    rec = json.loads(files[-1].read_text(encoding="utf-8"))
    if rec["product_hash"] != features.product_hash():
        pytest.fail(f"{files[-1].name} is older than the product source — re-run it")
    solution = [r for r in rec["runs"] if r["case"] == "proposes-a-solution"]
    complete = [r for r in rec["runs"] if r["case"] == "all-five-elements"]
    assert len(solution) == len(complete) == 5
    assert all(r["move"] == "challenge" and r["failed_criterion"] == "no-cause-no-fix"
               for r in solution), solution
    assert all(r["move"] == "read_back" for r in complete), complete

def test_the_record_prices_its_own_tokens(run) -> None:
    """DEF-164 — R12: the live run's cost, recorded in its summary, is the price file's cost of the
    tokens the run recorded per model — recomputed here from the record, never retyped — and it is
    within the ceiling."""
    from scripts.run_cost import load_prices, run_cost
    s = run["summary"]
    again = run_cost((s.get("tokens") or {}).get("by_model") or {}, load_prices())
    assert s["cost"]["usd"] == again["usd"] and s["cost"]["by_model"] == again["by_model"], (s["cost"], again)
    assert again["within_ceiling"] is True and again["usd"] > 0, again


def test_run_scenario_a_a_contradiction_pauses_and_resumes() -> None:
    """DEF-040's run criterion — scenario (a), founder rulings 2026-10-13: on the live run, a Belt who
    contradicts a value an earlier gate approved meets a pause in a node that writes nothing, picks a
    value, and the turn resumes: nothing stored twice, no model call charged twice, and the record says
    which steps reran. An OPEN PROOF: DEF-040 is built before Measure goes live (M3 / Stage C)."""
    _not_written('DEF-040')


def _scenario(run: dict, name: str) -> dict:
    entry = run.get(f"scenario_{name}")
    assert entry, f"the record has no scenario ({name}) — the run-through did not run it"
    failed = [k for k, v in (entry.get("checks") or {}).items() if not v]
    assert entry.get("passed") and not failed, (failed, entry.get("error"), entry.get("turns"))
    return entry


def test_run_scenario_b_a_crashed_turn_recovers(run) -> None:
    """Founder ruling 2026-10-13, scenario (b) — DEF-003's run criterion: a turn whose coach call fails
    after the planner checkpointed ends in an error; the next message is coached from the last
    checkpoint, nothing is stored, one reply is in the history."""
    _scenario(run, "b")


def test_run_scenario_c_a_turn_at_its_deadline_is_resent(run) -> None:
    """Scenario (c) — DEF-093's run criterion: a turn stopped at its deadline asks the Belt to send
    again (no Confirm, nothing stored, no reply left in the history); the resend is coached."""
    _scenario(run, "c")


def test_run_scenario_d_a_parked_element_is_resumed(run) -> None:
    """Scenario (d) — DEF-075's run criterion: the third failed attempt offers the park; parking moves on;
    the element is recorded parked; resume returns to it; it is read back, confirmed and stored."""
    _scenario(run, "d")


def test_run_scenario_e_an_upload_is_read_back_and_stored(run) -> None:
    """Scenario (e) — DEF-056's and DEF-082's run criterion: an upload lands, is read back naming the file,
    is confirmed and stored, and its source is recorded as the upload."""
    _scenario(run, "e")


def test_run_an_answer_is_judged_at_most_once(run) -> None:
    """DEF-066's run criterion — R3 amendment, on the live run: at most one judgment call per
    substantive answer, and none for any other turn (a Confirm or Change click, the opening)."""
    def judged(t: dict) -> int:
        return list(t.get("model_calls") or []).count("planner-judgment")
    over = [(t["n"], judged(t)) for t in run["turns"] if judged(t) > 1]
    clicks = [t["n"] for t in run["turns"] if (t.get("action") or t.get("why") == "opening") and judged(t)]
    assert not over and not clicks, (over, clicks)


def test_run_most_coaching_turns_are_graded(run) -> None:
    """DEF-015 on the live run: the grader runs on the coaching turns — a turn goes ungraded only
    when coherence rejected it (S-C13 B3) — at least 90% of them."""
    coached = [t for t in run["turns"] if "coach" in (t.get("model_calls") or [])]
    graded = [t for t in coached if "grader" in t["model_calls"]]
    assert coached and len(graded) >= 0.9 * len(coached), (len(graded), len(coached))
