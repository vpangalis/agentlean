"""Step 6.66 Part 7 — THE DEFINE RUN-THROUGH: the measured distance to "Define works end to end".

**OUTSIDE PYTEST, ON PURPOSE**, like `move_proof_661.py` (whose model-call
counter and cap it reuses) and `coaching_proof_656.py` (whose tracing switch and
LangSmith send-counter it reuses): real model calls, real storage, the real
`POST /ask` route, a NEW case. Tracing is OFF and every send is counted.

A scripted Belt walks all thirteen Define elements. Each message is chosen from the
MOVE RECORD the last reply carried (founder ruling R5: the move is decided in
code), never from a turn counter:

    teach / challenge / respond / store_and_advance  ->  answer the named field
    read_back                                         ->  click Confirm
Probes, each once: a WEAK first answer at the problem statement (4); a CHANGE
click at the voice of the customer (3); a TYPED correction at the goal (7);
"where do we stand?" before the scope (6); the savings figures at the
benefits analysis (10); an evidence upload before the SIPOC (12). Then the gate:
`GET /gate/review`, and `POST /gate` — as far as the gate exists today.

THE CAP — `--max-calls` (default 150, founder ruling 2026-09-25, diagnosis
included) counted at the chat-model boundary, every role; the call past it
raises and the run stops with what it has. A field challenged three times is
recorded as STUCK and the walk stops there. Either way the gate steps run
(they make no model call), so the record always says how far Define got.

THE RECORD — one lean JSON line per turn, plus a summary line carrying the
source hash it ran on, written to `docs/runthrough/` as one .json array (tracked: the tests in
`backend/tests/test_define_runthrough.py` read it, and fail when it is older
than the source). The coach's full inputs go to `--scratch`, never the tree.

    cd agent-improve; python -m scripts.define_runthrough --scratch <dir>
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from scripts.coaching_proof_656 import ANSWERS, SAVINGS, SENDS, WEAK_4, _tracing_off
from scripts.move_proof_661 import CALLS, COACH_INPUTS, CapReached, _count_model_calls, token_totals

CASE_TITLE = "DEFINE RUN-THROUGH — step 6.66, do not use for other proofs"
USER = "define-runthrough-6.66"
OPENING = "Hi — I'm ready to start Define on our project."
WHERE = "Where do we stand?"
OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "runthrough"
#: The scenarios' own model-call allowance, beside the walk's --max-calls (about 50 used on 2026-10-13).
SCENARIO_CALLS = 80
MAX_ATTEMPTS = 3            # answers to one field before it is recorded STUCK
#: ADR-0070: the elements whose read-back must carry a visual, and where the reply carries it.
VISUAL_FIELDS = {"baseline_estimate": "visualisation", "goal_statement": "visualisation",
                 "target_value": "visualisation", "process_map_sipoc": "sipoc_diagram"}

#: The good answer per element — each meets its acceptance criteria in
#: skills/dmaic-define-phase/SKILL.md (R2, R3; 2026-09-26). Positions 1-8 start
#: from 6.56's scripted Belt, with what the criteria added: where/when/baseline
#: in the business case, training, the CTQs, the 5W2H "how", the KPI link.
GOOD: dict[str, str] = {
    "business_case": ("Across our three hospital sites, 23% of supplier invoices were paid "
                      "after their 30-day terms from January to June 2026. " + ANSWERS[1]),
    "team": ANSWERS[2] + (" Training: Dev and Amira need a half-day on data collection "
                          "before Measure; nobody else needs any."),
    "voc_summary": ANSWERS[3] + (" CTQs: suppliers — paid within 30 days of the invoice "
                                 "date on every invoice; ward managers — no supplier puts "
                                 "us on stop in a quarter."),
    "problem_statement": ANSWERS[4] + (" How it shows: suppliers chase us by phone and "
                                       "email, and some put us on stop. The steps where it shows: "
                                       "resolve mismatches and approve — invoices wait there."),
    "baseline_estimate": ANSWERS[5] + " It feeds our finance KPI, creditor days.",
    "project_scope": ANSWERS[6], "goal_statement": ANSWERS[7], "target_value": ANSWERS[8],
    "target_date": "We plan to finish the project by 31 March 2027 (2027-03-31).",
    "benefits_analysis": ("Cost of the gap: about £68,000 a year in interest and lost "
                          "discounts, from the savings calculation. It is sustainable — "
                          "every year, not one-off. It would start in Q2 2027 at about "
                          "£17,000 a quarter. Our finance contact is Sam Reid, management "
                          "accountant, who will validate it."),
    "secondary_metrics": ("Two things must not get worse: the number of supplier payment "
                          "queries the AP team handles each month, and AP staff overtime "
                          "hours. Both should stay at or below today's levels."),
    "process_map_sipoc": (
        "Suppliers: our medical and general suppliers, and the purchasing team who raise "
        "the purchase orders. Inputs: supplier invoices, purchase orders and goods-received "
        "notes. Process: receive the invoice, match it to the purchase order and the goods "
        "receipt, resolve mismatches, approve, then schedule and release payment. Outputs: "
        "paid invoices and remittance advice. Customers: the suppliers, and our ward "
        "managers who rely on their deliveries. Process metrics: days from invoice receipt "
        "to payment release, and the share of invoices with a match exception. "
        "How each step performs today, roughly: receive the invoice — about 1 day (2 hours to "
        "3 days), about 600 a week, no problems; match — about 1 day (1 hour to 2 days), about "
        "600 a week, no problems; resolve mismatches — about 5 days (1 to 20 days), about 140 a "
        "week, problem: buyers answer queries late (Dev said so); approve — about 4 days (1 to "
        "15 days), about 600 a week, problem: approvers on leave and nobody covers (Lena said "
        "so); schedule and release payment — about 2 days (1 to 4 days), two payment runs a "
        "week, no problems. The whole process: about 12 days from receipt to payment, about "
        "600 invoices a week."),
    "issues_and_barriers": ("Two barriers: the three sites use different approval routes, "
                            "and an ERP change freeze until January limits system changes. "
                            "One risk: AP staff turnover over the winter."),
}
#: A further answer when a good one is challenged — adds detail, never repeats.
MORE = ("To add detail: this is based on the AP ledger for January to June 2026, across "
        "all three hospital sites, and the finance director has agreed it.")
#: The Change probe's revised answer (position 3).
VOC_REVISED = (ANSWERS[3] + " One more thing: suppliers also told us they cannot see "
               "the status of an invoice once it is submitted.")
#: The typed-correction probe (position 7): a qualified reply, never a plain yes.
GOAL_CORRECTION = ("Nearly — reduce the late payment rate from 23% to under 5% by 31 March "
                   "2027, and keep it under 5% for three months after that.")
UPLOAD_CSV = ("month,invoices,paid_late,late_rate_pct\n"
              "2026-01,3480,810,23.3\n2026-02,3390,770,22.7\n2026-03,3620,850,23.5\n"
              "2026-04,3510,790,22.5\n2026-05,3570,840,23.5\n2026-06,3450,780,22.6\n")


def _guard_mode() -> dict[str, Any]:
    """The input guard's mode and the Content Safety set-up this run ran under (never the key)."""
    from backend.core import content_safety
    return {"mode": "development" if content_safety.development_mode() else "strict",
            "content_safety_configured": content_safety.configured()}


def _write(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def _source_hash() -> str:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "control_board"))
    import features
    return features.source_hash()


def _product_hash() -> str:
    """The product source only (no tests) — what the record's tests bind to."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "control_board"))
    import features
    return features.product_hash()


class Walk:
    """The scripted Belt. State: which probes have fired, answers per field."""

    def __init__(self) -> None:
        self.fired: set[str] = set()
        self.attempts: dict[str, int] = {}
        self.confirms: dict[str, int] = {}
        self.last: tuple[str, str | None] = ("", None)

    def once(self, probe: str) -> bool:
        if probe in self.fired:
            return False
        self.fired.add(probe)
        return True

    def next(self, move: str | None, field: str | None) -> tuple[str, str | None, str]:
        """(message, action, why) for the reply that carried `move` on `field`."""
        if move == "read_back":
            key = field or ""
            if self.last == ("confirm", field):
                self.confirms[key] = self.confirms.get(key, 0) + 1
                if self.confirms[key] >= MAX_ATTEMPTS:
                    # A Confirm answered by a read-back again, three times (R14's three
                    # attempts, founder ruling 2, 2026-09-28 — it was twice): the
                    # confirmation cannot complete the position (6.66's run found this
                    # at position 5). Stuck, not a reason to spend.
                    return "", None, "stuck"
            self.last = ("confirm", field)
            if field == "voc_summary" and self.once("change"):
                return "Change", "change", "probe: Change click"
            if field == "goal_statement" and self.once("typed-correction"):
                return GOAL_CORRECTION, None, "probe: typed correction"
            return "Confirm", "confirm", "confirm click"
        self.last = ("answer", field)
        if field is None:
            return "", None, "done"
        if move in ("teach", "store_and_advance"):
            if field == "project_scope" and self.once("where"):
                return WHERE, None, "probe: where do we stand"
            if field == "benefits_analysis" and self.once("savings"):
                return SAVINGS, None, "probe: savings figures"
        n = self.attempts.get(field, 0)
        self.attempts[field] = n + 1
        if n >= MAX_ATTEMPTS:
            return "", None, "stuck"
        if field == "problem_statement" and n == 0:
            return WEAK_4, None, "probe: weak first answer"
        if field == "voc_summary" and "change" in self.fired and n >= 1:
            return VOC_REVISED, None, "revised answer after Change"
        if move == "challenge" and n >= 1 and not (field == "problem_statement" and n == 1):
            return GOOD[field] + " " + MORE, None, "answer again, with more detail"
        return GOOD[field], None, "good answer"


def run(client: Any, rec: Path, scratch: Path, cap: int) -> dict[str, Any]:
    from backend.phases import moves
    created = client.post("/cases", json={
        "title": CASE_TITLE, "belt_level": "green", "leader": "Priya Shah",
        "department": "Finance — Accounts Payable", "target_date": "2027-03-31", "team": []})
    created.raise_for_status()
    case_id = created.json()["case_id"]
    print(f"case {case_id} — {CASE_TITLE}")
    walk, out = Walk(), {"case_id": case_id, "stopped": None, "turns": 0}
    message, action, why = OPENING, None, "opening"
    uploaded = False
    for n in range(1, 80):
        if why in ("done", "stuck"):
            out["stopped"] = why
            break
        if len(CALLS) >= cap:
            # The node's containment can turn the call past the cap into a
            # fallback reply, so the walk stops itself rather than trust it.
            out["stopped"] = f"cap: {cap} model calls"
            break
        if getattr(walk, "_field", None) == "issues_and_barriers" and "early_gate" not in out:
            # DEF-064 / row 17 (founder 2026-10-14, A+): one gate submit while a field is still missing —
            # layer 2b refuses it in code, no model call.
            eg = client.post("/gate", json={"case_id": case_id, "submitted_by": USER, "phase": "define"})
            eb = eg.json() if eg.headers.get("content-type", "").startswith("application/json") else {"text": eg.text[:300]}
            out["early_gate"] = {"http": eg.status_code, "passed": bool(isinstance(eb, dict) and eb.get("passed")),
                                 "missing": (eb.get("missing_fields") if isinstance(eb, dict) else None)}
            _write(rec, {"kind": "early_gate", **out["early_gate"]})
        if walk_field := getattr(walk, "_field", None):
            if walk_field == "process_map_sipoc" and not uploaded:
                uploaded = True
                c0, t0 = len(CALLS), time.time()
                try:
                    up = client.post("/upload", data={"case_id": case_id, "uploaded_by": USER,
                                                      "phase": "define", "kind": "evidence"},
                                     files={"file": ("ap_late_payments_jan_jun_2026.csv",
                                                 UPLOAD_CSV.encode(), "text/csv")})
                    up_body: Any = (up.json() if up.headers.get("content-type", "").startswith("application/json")
                                    else up.text[:300])
                    up_http: Any = up.status_code
                except Exception as exc:  # noqa: BLE001 — recorded, the walk goes on
                    up_body, up_http = f"{exc.__class__.__name__}: {exc}"[:300], None
                _write(rec, {"kind": "upload", "http": up_http,
                             "seconds": round(time.time() - t0, 1),
                             "model_calls": [c["kind"] for c in CALLS[c0:]], "body": up_body})
        c0, i0, t0 = len(CALLS), len(COACH_INPUTS), time.time()
        body: dict[str, Any] = {"case_id": case_id, "phase": "define", "message": message, "user": USER}
        if action:
            body["action"] = action
        try:
            resp = client.post("/ask", json=body)
        except CapReached as exc:
            out["stopped"] = f"cap: {exc}"
            _write(rec, {"kind": "turn", "n": n, "why": why, "belt": message, "action": action,
                         "http": None, "stopped": out["stopped"]})
            break
        seconds = round(time.time() - t0, 1)
        case = client.get(f"/cases/{case_id}").json()
        history = case.get("conversation_history") or []
        ai = [t for t in history if t.get("role") == "ai"]
        mrec = (ai[-1].get(moves.MOVE_RECORD_KEY) if ai else None) or {}
        structured = ((case.get("phases") or {}).get("define") or {}).get("structured") or {}
        rb = resp.json() if resp.status_code == 200 else {}
        judgment = mrec.get("judgment") or {}
        line = {
            "kind": "turn", "n": n, "why": why, "belt": message, "action": action,
            "http": resp.status_code, "seconds": seconds,
            "model_calls": [c["kind"] for c in CALLS[c0:]],
            "tokens": token_totals(CALLS[c0:])["total"],          # item 4 (2026-09-30)
            "move": mrec.get("move"), "field": mrec.get("field"), "status": mrec.get("status"),
            "verdict": judgment.get("verdict") if isinstance(judgment, dict) else None,
            "stored_field": (mrec.get("stored") or {}).get("field") if isinstance(mrec.get("stored"), dict) else mrec.get("stored_field"),
            "stored_keys": sorted(structured),
            "stored_types": {k: type(v).__name__ for k, v in structured.items()},
            "reply": {k: rb.get(k) for k in ("answer", "explanation", "example", "prompt",
                                             "progress", "move", "move_field", "grader_warning",
                                             "sipoc_diagram", "visualisation")},
            "gate_status": rb.get("gate_status"),
            "fallback": bool(mrec.get("fallback")),
            # G-139 (founder ruling 2, 2026-09-30): what the coach returned when the call limit ended it.
            "limit": mrec.get("limit"),
            "resend": bool(mrec.get("resend")),
            "error": None if resp.status_code == 200 else resp.text[:400],
            # Founder ruling 2026-10-14: the log-only grader's verdict on this reply, from step_log.
            "grader": grader_entry(case_id, message),
        }
        # Founder ruling 3, 2026-09-28: the stored state is checked after EVERY Confirm — a Confirm
        # that moved on must have stored its element; one that did not must say so (G-117, G-121).
        # ADR-0070 (founder, 2026-09-28): the read-backs of elements 5, 7, 8 and 12 carry their
        # visual, drawn by the program and marked not yet confirmed; a Confirm carries it confirmed.
        if line["field"] in VISUAL_FIELDS and line["move"] == "read_back":
            vis = rb.get(VISUAL_FIELDS[line["field"]])
            line["visual_check"] = {"field": line["field"], "present": bool(vis),
                                    "not_yet_confirmed": isinstance(vis, dict) and vis.get("confirmed") is False}
            out.setdefault("visuals_missing", [])
            if not line["visual_check"]["not_yet_confirmed"]:
                out["visuals_missing"].append(line["field"])
        if action == "confirm" and getattr(walk, "_field", None) in VISUAL_FIELDS:
            vis = rb.get(VISUAL_FIELDS[getattr(walk, "_field")])
            if vis and vis.get("confirmed"):
                out.setdefault("confirmed_visuals", {})[getattr(walk, "_field")] = vis
        if action == "confirm":
            asked = getattr(walk, "_field", None)
            advanced = line["move"] == "store_and_advance"
            line["confirm_check"] = {"field": asked, "advanced": advanced,
                                     "stored": bool(asked and asked in structured),
                                     "lost": bool(advanced and asked and asked not in structured)}
            out["confirms"] = out.get("confirms", 0) + 1
            out["confirms_lost"] = out.get("confirms_lost", 0) + int(line["confirm_check"]["lost"])
        _write(rec, line)
        _write(scratch, {"n": n, "coach_inputs": COACH_INPUTS[i0:], "move_record": mrec})
        out["turns"] = n
        check = line.get("confirm_check")
        print(f"{n:>2} [{why}] http={resp.status_code} move={line['move']} field={line['field']} "
              f"verdict={line['verdict']} calls={len(CALLS) - c0} total={len(CALLS)} {seconds}s"
              + (f" confirm: {check['field']} stored={check['stored']}{' LOST' if check['lost'] else ''}" if check else ""))
        if resp.status_code != 200:
            out["stopped"] = f"http {resp.status_code}"
            break
        walk._field = line["field"]  # type: ignore[attr-defined]
        message, action, why = walk.next(line["move"], line["field"])
        if why == "stuck":
            out["stuck_at"] = line["field"]

    # ── DEF-064, A+ (founder 2026-10-14): while the case is still in Define — one correction of a confirmed
    # element (row 6), one traced coaching turn (rows 2, 13, 33, 35), then the capability rows on the case ──
    if out.get("stopped") == "done":
        out["capability"] = capability_steps(client, rec, case_id, scratch)

    # ── the gate, as far as it exists: review, then submit (no model call) ──
    rv = client.get(f"/gate/review/{case_id}/define")
    review = rv.json() if rv.status_code == 200 else {"error": rv.text[:400]}
    # ADR-0070: the gate document shows the same visuals the Confirms drew (the last Confirm of each).
    report_vis = ((review.get("report") or {}).get("visuals") or {}) if isinstance(review, dict) else {}
    kinds = {"baseline_estimate": "baseline_target", "goal_statement": "baseline_target",
             "target_value": "baseline_target", "process_map_sipoc": "sipoc"}
    confirmed = out.get("confirmed_visuals") or {}
    last = {kinds[f]: v for f, v in confirmed.items() if f in ("target_value", "process_map_sipoc")}
    # target_date is element 9's, confirmed after element 8: compared without it.
    def _core(v: Any) -> Any:
        return {k: x for k, x in (v or {}).items() if k != "target_date"} if isinstance(v, dict) else v
    out["gate_visuals"] = {"kinds": sorted(report_vis),
                           "same_as_reply": {k: _core(report_vis.get(k)) == _core(v) for k, v in last.items()}}
    _write(rec, {"kind": "gate_review", "http": rv.status_code, "body": review})
    sb = client.post("/gate", json={"case_id": case_id, "submitted_by": USER, "phase": "define"})
    submit = sb.json() if sb.headers.get("content-type", "").startswith("application/json") else {"text": sb.text[:400]}
    _write(rec, {"kind": "gate_submit", "http": sb.status_code, "body": submit})
    # Founder ruling 3, 2026-09-28 — the last two steps (stop condition 7's evidence): approve the
    # Define report, then one turn that enters Measure. Only after a submission that passed.
    if sb.status_code == 200 and isinstance(submit, dict) and (submit.get("awaiting_acceptance") or submit.get("passed")):
        c0, t0 = len(CALLS), time.time()
        dc = client.post("/gate/decision", json={"case_id": case_id, "phase": "define", "decision": "approve",
                                                 "actor": "Priya Shah"})
        decided = dc.json() if dc.headers.get("content-type", "").startswith("application/json") else {"text": dc.text[:400]}
        _write(rec, {"kind": "gate_decision", "http": dc.status_code, "seconds": round(time.time() - t0, 1),
                     "model_calls": [c["kind"] for c in CALLS[c0:]], "body": decided})
        print(f"gate decision {dc.status_code}")
        if dc.status_code == 200:
            # T23, live (founder 2026-10-14): the approval wrote the gate document once — the Store's
            # record and the case's confirmed values agree, and a second approval changes neither.
            out["t23"] = t23_check(client, case_id)
            _write(rec, {"kind": "t23_check", **out["t23"]})
            print(f"T23 live check: {out['t23']}")
            c0, t0 = len(CALLS), time.time()
            ms = client.post("/ask", json={"case_id": case_id, "phase": "measure", "user": USER,
                                           "message": "We're ready for Measure. Where do we start?"})
            mb = ms.json() if ms.status_code == 200 else {"error": ms.text[:400]}
            after = client.get(f"/cases/{case_id}").json()
            _write(rec, {"kind": "measure_turn", "http": ms.status_code, "seconds": round(time.time() - t0, 1),
                         "model_calls": [c["kind"] for c in CALLS[c0:]], "phase": mb.get("phase"),
                         "current_phase": after.get("current_phase"),
                         "reply": {k: mb.get(k) for k in ("answer", "prompt", "progress", "move", "move_field")}})
            print(f"measure turn {ms.status_code} · phase now {after.get('current_phase')}")
    final = client.get(f"/cases/{case_id}").json()
    _write(rec, {"kind": "final_case", "current_phase": final.get("current_phase"),
                 "define_structured": ((final.get("phases") or {}).get("define") or {}).get("structured"),
                 "field_log_keys": sorted(str(e.get("key")) for e in (((final.get("phases") or {})
                                   .get("define") or {}).get("field_log") or []))[:200]})
    print(f"gate review {rv.status_code} · submit {sb.status_code} · phase now {final.get('current_phase')}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-calls", type=int, default=150)
    ap.add_argument("--scratch", required=True, help="where the coach's full inputs go (outside the tree)")
    ap.add_argument("--slices", action="store_true",
                    help="the three live slices from saved cases (founder 2026-10-14); recorded in the tree")
    ap.add_argument("--slice", type=int, choices=(1, 2, 3), help="one live slice only")
    ap.add_argument("--scenarios-only", action="store_true",
                    help="run only the hard-path scenarios (b)-(e); the record goes to --scratch, never the tree")
    args = ap.parse_args()
    # DEF-064: the real send methods, kept for the one traced turn (traced_turn), before tracing goes off.
    from langsmith import Client as _LSClient
    from scripts.coaching_proof_656 import _CLIENT_SENDS
    REAL_SENDS.update({m: getattr(_LSClient, m) for m in _CLIENT_SENDS if hasattr(_LSClient, m)})
    _tracing_off()
    # The walk stops itself at --max-calls (`run` checks it); the hard cap at the model boundary leaves the
    # hard-path scenarios their own allowance — they ran into the walk's cap on 2026-10-13 (run 074320).
    _count_model_calls(args.max_calls + SCENARIO_CALLS)
    if args.scenarios_only:
        return _scenarios_only(Path(args.scratch))
    if args.slices or args.slice:
        return _slices(Path(args.scratch), args.slice)
    # R3's repeated-run record first (10 calls, inside the same cap), so one
    # re-run by the integrator refreshes both records it binds to the source.
    from scripts.validation_repeat import run as validation_repeat
    validation_repeat()
    # Its `asyncio.run` loop is closed now; a model instance cached inside it holds an async
    # client bound to that loop, and the run-through's first judgment would reuse it and fail
    # with "Connection error." (M1 loop, 2026-09-28: two runs stopped at turn 2). Rebuild them.
    from backend.core.llm import _build_llm
    _build_llm.cache_clear()
    stamp =dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Written line by line to scratch while running (a crash keeps every turn);
    # the tree gets one .json array at the end — rule 7 keeps .jsonl out of it.
    rec = Path(args.scratch) / f"define_runthrough_{stamp}.jsonl"
    scratch = Path(args.scratch) / f"define_runthrough_{stamp}_inputs.jsonl"
    scratch.parent.mkdir(parents=True, exist_ok=True)
    _wallclock(stamp, Path(args.scratch))
    source, product = _source_hash(), _product_hash()
    started = time.time()
    from fastapi.testclient import TestClient
    from backend.app import app
    out: dict[str, Any] = {}
    walk: list[dict[str, Any]] = []
    with TestClient(app) as client:
        try:
            out = run(client, rec, scratch, args.max_calls)
        except CapReached as exc:
            out["stopped"] = f"cap: {exc}"
        # Founder rulings 2026-10-13: the hard paths, each its own case, pass check and cost line.
        from scripts.hard_path_scenarios import run_all
        walk = list(CALLS)          # R12's ceiling is the Define walk's; each scenario has its own cost line
        out["scenarios"] = run_all(client, lambda e: _write(rec, e), GOOD)
        out["scenarios_cost"] = _cost(token_totals(CALLS[len(walk):]))
    summary = {"kind": "summary", "source_hash": source, "product_hash": product, "started": stamp,
               "minutes": round((time.time() - started) / 60, 1), "cap": args.max_calls,
               "model_calls": len(walk),
               "by_kind": {k: sum(c["kind"] == k for c in walk) for k in sorted({c["kind"] for c in walk})},
               "langsmith_sends": len(SENDS),
               # Founder 2026-09-30 (Part A3): the run says which guard mode it ran under and whether
               # Content Safety was configured — the report reads it here, never from the command line.
               "guard_mode": _guard_mode(),
               # Founder 2026-09-30 (review of 309f9fc), item 4: tokens per role, per model and in
               # total, so the run's cost can be computed from the deployments' prices.
               "tokens": token_totals(walk),
               # G-153 (founder 2026-10-11): the calls cut off at their token limit, counted per run.
               "cut_offs": cut_offs(walk), **out}
    summary["cost"] = _cost(summary["tokens"])
    summary["grader_findings"] = grader_findings([json.loads(l) for l in rec.read_text(encoding="utf-8").splitlines()
                                                  if l.strip()])
    # Founder ruling 2026-10-12 (turn time): median and 90th percentile per turn type, p90 watched.
    summary["turn_times"] = turn_times([json.loads(l) for l in rec.read_text(encoding="utf-8").splitlines()
                                        if l.strip()])
    _write(rec, summary)
    print(json.dumps(summary, indent=1, default=str))
    print(grader_findings_text(summary["grader_findings"]))
    _time_it(started, len(CALLS))
    tree = OUT_DIR / f"define_runthrough_{stamp}.json"
    tree.write_text(json.dumps([json.loads(l) for l in rec.read_text(encoding="utf-8").splitlines() if l.strip()],
                               indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"record: {tree}")
    return exit_code(summary, SENDS)


def _slices(scratch: Path, only: int | None = None) -> int:
    """The three live slices (founder ruling 2026-10-14), each from a saved case: recorded line by line to
    scratch, then to docs/runthrough/slices_<stamp>.json with the cost and the source they ran on."""
    from fastapi.testclient import TestClient

    from backend.app import app
    from scripts.hard_path_scenarios import run_slices
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    rec = scratch / f"slices_{stamp}.jsonl"
    scratch.mkdir(parents=True, exist_ok=True)
    source, product = _source_hash(), _product_hash()
    with TestClient(app) as client:
        result = run_slices(client, lambda e: _write(rec, e), GOOD, only)
    _write(rec, {"kind": "summary", "source_hash": source, "product_hash": product, "started": stamp,
                 "slices": result, "model_calls": len(CALLS), "langsmith_sends": len(SENDS),
                 "cost": _cost(token_totals(CALLS))})
    tree = OUT_DIR / f"slices_{stamp}.json"
    tree.write_text(json.dumps([json.loads(l) for l in rec.read_text(encoding="utf-8").splitlines() if l.strip()],
                               indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"slices: {result}; record: {tree}; USD {_cost(token_totals(CALLS)).get('usd')}")
    return 0 if all(result.values()) else 6


def _scenarios_only(scratch: Path) -> int:
    """The scenarios alone, recorded to scratch (iteration; a full run records them in the tree)."""
    from fastapi.testclient import TestClient

    from backend.app import app
    from scripts.hard_path_scenarios import run_all
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    rec = scratch / f"scenarios_{stamp}.jsonl"
    scratch.mkdir(parents=True, exist_ok=True)
    with TestClient(app) as client:
        result = run_all(client, lambda e: _write(rec, e), GOOD)
    print(f"scenarios: {result}; record: {rec}; USD {_cost(token_totals(CALLS)).get('usd')}")
    return 0 if all(result.values()) else 6


#: DEF-064 — the correction (row 6): issues and barriers revised once, after every element is confirmed.
REVISED_ISSUES = ("Three barriers now: the three sites use different approval routes, the ERP change freeze until "
                  "January, and the AP team's year-end close in December, when nobody is free for workshops.")
#: DEF-064 — the traced turn (rows 2, 13, 33, 35): a question that reaches the coach, captures nothing.
TRACED_TURN = ("Before we submit, can you remind me what the customers column of our SIPOC is for, and whether "
               "ours names the right people?")
TRACED_USER = "capability-traced-turn"
#: The LangSmith client's real send methods, kept before tracing is switched off (main).
REAL_SENDS: dict[str, Any] = {}


def _parent_inputs(case_id: str) -> int:
    """How many `input` checkpoints the case's parent graph holds — row 2 counts one per POST."""
    from backend.core.checkpointer import get_checkpointer
    cfg = {"configurable": {"thread_id": case_id, "checkpoint_ns": ""}}
    return sum(1 for t in get_checkpointer().list(cfg) if (t.metadata or {}).get("source") == "input")


def traced_turn(client: Any, case_id: str) -> dict[str, Any]:
    """DEF-064 (founder 2026-10-14): ONE coaching turn traced to LangSmith as its own run, labelled by its
    user (`capability-traced-turn`): the real client methods for this request only, flushed, then tracing
    is switched off again. The walk's own send count is untouched — a true 0 (DEF-004)."""
    import datetime as _dt
    import langsmith.utils as ls_utils
    from langchain_core.tracers.langchain import wait_for_all_tracers
    from langsmith import Client
    from langsmith.run_trees import configure
    from backend.core.config import settings
    sends_before = len(SENDS)
    for method, fn in REAL_SENDS.items():
        setattr(Client, method, fn)
    for name in ("LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING_V2", "LANGSMITH_TRACING", "LANGCHAIN_TRACING"):
        os.environ[name] = "true"
    os.environ.setdefault("LANGCHAIN_API_KEY", settings.LANGCHAIN_API_KEY or "")
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT or "agentlean-improve"
    getattr(ls_utils.get_env_var, "cache_clear")()
    configure(enabled=True)
    inputs_before = _parent_inputs(case_id)
    started = _dt.datetime.now(_dt.timezone.utc)
    try:
        resp = client.post("/ask", json={"case_id": case_id, "phase": "define", "user": TRACED_USER,
                                         "message": TRACED_TURN})
        body: Any = resp.json() if resp.content else {}
        status = resp.status_code
    finally:
        wait_for_all_tracers()
        _tracing_off()
    return {"status": status, "body": body, "inputs_before": inputs_before,
            "inputs_after": _parent_inputs(case_id), "started": started.isoformat(),
            "walk_sends_unchanged": len(SENDS) == sends_before}


def capability_rows(case_id: str, driven_path: Path) -> dict[str, Any]:
    """DEF-064 — every Define capability row's own check, run on this case (pytest, its own process; rows
    read the case from Azure), the traced turn handed to row 2. Each row: passed, failed or skipped (a skip
    is not a pass, Appendix H)."""
    import subprocess
    import xml.etree.ElementTree as ET
    junit = driven_path.with_suffix(".rows.xml")
    env = {**os.environ, "CAPABILITY_CASE_ID": case_id, "CAPABILITY_SCRIPT_CASE_ID": case_id,
           "CAPABILITY_DRIVEN_TURN": str(driven_path)}
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:randomly", "-p", "no:cacheprovider",
                           "backend/tests/test_capability_rows.py", "-k", "test_row_", f"--junitxml={junit}"],
                          cwd=str(Path(__file__).resolve().parents[1]), env=env, capture_output=True, text=True,
                          timeout=900)
    rows: dict[str, str] = {}
    if junit.exists():
        for case in ET.parse(junit).getroot().iter("testcase"):
            name = case.get("name") or ""
            outcome = "failed" if case.find("failure") is not None or case.find("error") is not None else \
                "skipped" if case.find("skipped") is not None else "passed"
            detail = next((str(c.get("message") or "")[:300] for c in case if c.tag in ("failure", "error", "skipped")), "")
            rows[name] = outcome if not detail else f"{outcome}: {detail}"
    return {"rows": rows, "green": bool(rows) and all(v == "passed" for v in rows.values()),
            "exit": proc.returncode}


def capability_steps(client: Any, rec: Path, case_id: str, scratch: Path) -> dict[str, Any]:
    """DEF-064, A+ — while the case is in Define: the correction (row 6), the traced turn, the rows."""
    out: dict[str, Any] = {}
    # Row 6 — one confirmed element changed: Revise, the new answer, its read-back, Confirm.
    steps: list[tuple[str, dict[str, Any]]] = [
        ("revise", {"message": "Change: issues and barriers", "action": "revise", "element": "issues_and_barriers"}),
        ("new answer", {"message": REVISED_ISSUES}), ("confirm", {"message": "Confirm", "action": "confirm"})]
    for why, extra in steps:
        t0 = time.time()
        r = client.post("/ask", json={"case_id": case_id, "phase": "define", "user": USER, **extra})
        b = r.json() if r.status_code == 200 else {}
        _write(rec, {"kind": "check_turn", "why": f"row 6: {why}", "http": r.status_code,
                     "seconds": round(time.time() - t0, 1), "move": b.get("move"), "field": b.get("move_field")})
    out["correction_stored"] = (((client.get(f"/cases/{case_id}").json().get("phases") or {}).get("define") or {})
                                .get("structured") or {}).get("issues_and_barriers") == REVISED_ISSUES
    # Rows 2, 13, 33, 35 — the one traced turn.
    driven = traced_turn(client, case_id)
    _write(rec, {"kind": "traced_turn", **{k: v for k, v in driven.items() if k != "body"},
                 "answer": str((driven.get("body") or {}).get("answer") or "")[:300],
                 "move": (driven.get("body") or {}).get("move")})
    path = scratch.parent / f"driven_turn_{case_id}.json"
    path.write_text(json.dumps(driven, default=str), encoding="utf-8")
    out["traced_turn"] = {"status": driven["status"], "walk_sends_unchanged": driven["walk_sends_unchanged"]}
    out["rows"] = capability_rows(case_id, path)
    _write(rec, {"kind": "capability_rows", **out["rows"]})
    print(f"capability rows: {'GREEN' if out['rows']['green'] else 'NOT GREEN'} "
          f"{ {k: v for k, v in out['rows']['rows'].items() if v != 'passed'} }")
    return out


def t23_check(client: Any, case_id: str) -> dict[str, Any]:
    """T23 on the live run (founder 2026-10-14): after the approval the Store holds the Define gate
    document, every value in it equals the case's confirmed value, and a second approval request changes
    neither the Store record nor the case (written once)."""
    from backend.core.store import get_store
    from backend.phases.mappers_common import read_gate_document

    def snapshot() -> tuple[dict[str, Any], dict[str, Any]]:
        doc = read_gate_document(get_store(), case_id, "define") or {}
        structured = ((client.get(f"/cases/{case_id}").json().get("phases") or {}).get("define") or {}).get(
            "structured") or {}
        return dict(doc), dict(structured)
    doc, structured = snapshot()
    differ = sorted(k for k in doc if k in structured and doc[k] != structured[k])
    again = client.post("/gate/decision", json={"case_id": case_id, "phase": "define", "decision": "approve",
                                               "actor": "Priya Shah"})
    doc2, structured2 = snapshot()
    return {"store_written": bool(doc), "fields_in_store": len(doc), "differ_from_case": differ,
            "second_approval_http": again.status_code, "unchanged_after_second": doc2 == doc and structured2 == structured,
            "passed": bool(doc) and not differ and doc2 == doc and structured2 == structured}


def grader_entry(case_id: str, belt: str) -> dict[str, Any] | None:
    """Founder ruling 2026-10-14 — the grader's step_log entry for the turn just sent (the log-only
    after_agent middleware, unchanged): status, move, and each failed criterion with the grader's reason.
    Read from the define subgraph's latest checkpoint, and only when that checkpoint is this turn's (its
    last Belt message is the one sent); None when the turn ran no coach (a reply written in code)."""
    from scripts.coaching_proof_656 import _latest_final
    try:
        final = _latest_final(case_id)
    except Exception as exc:  # noqa: BLE001 — a report line, never a stopped run
        return {"status": "unread", "error": f"{type(exc).__name__}: {exc}"[:200]}
    human = [m for m in final.get("messages") or [] if getattr(m, "type", "") == "human"]
    if not human or str(human[-1].content).strip() != str(belt or "").strip():
        return None
    g = next((e for e in final.get("step_log") or [] if isinstance(e, dict) and e.get("node") == "coaching_grader"),
             None)
    if g is None:
        return None
    return {"status": g.get("status"), "move": g.get("move"), "verdicts": g.get("verdicts"),
            # Founder 2026-10-14: G1–G5 with the sentence of the reply each fail quotes; a fail with no
            # quote is not counted and is shown apart.
            "failed": [{"criterion": f.get("criterion"), "reason": f.get("feedback") or "",
                        "evidence": f.get("evidence") or ""}
                       for f in g.get("failed") or [] if isinstance(f, dict)],
            "not_counted": [{"criterion": f.get("criterion"), "reason": f.get("feedback") or ""}
                            for f in g.get("not_counted") or [] if isinstance(f, dict)]}


def grader_findings(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Founder ruling 2026-10-14 — the report's "Grader findings": per flagged turn, the turn, move, element,
    failed criterion and the grader's reason; counts per criterion; and coverage — every coached reply has
    a logged verdict (DEF-015). Read from the record's turns, which carry the step_log entry."""
    turns = [e for e in entries if e.get("kind") == "turn"]
    coached = [t for t in turns if "coach" in (t.get("model_calls") or [])]
    flagged = [{"n": t["n"], "move": (t.get("grader") or {}).get("move") or t.get("move"), "element": t.get("field"),
                "criterion": f["criterion"], "reason": f["reason"], "evidence": f.get("evidence") or ""}
               for t in turns if (t.get("grader") or {}).get("status") == "failed"
               for f in (t.get("grader") or {}).get("failed") or []]
    per: dict[str, int] = {}
    for f in flagged:
        per[str(f["criterion"])] = per.get(str(f["criterion"]), 0) + 1
    statuses: dict[str, int] = {}
    for t in coached:
        s = str((t.get("grader") or {}).get("status") or "no verdict")
        statuses[s] = statuses.get(s, 0) + 1
    uncounted = sum(len((t.get("grader") or {}).get("not_counted") or []) for t in turns)
    return {"coached_replies": len(coached), "verdicts": statuses, "not_counted": uncounted,
            "without_verdict": [t["n"] for t in coached if not (t.get("grader") or {}).get("status")],
            "flagged_turns": sorted({f["n"] for f in flagged}), "per_criterion": dict(sorted(per.items())),
            "findings": flagged}


def grader_findings_text(g: dict[str, Any]) -> str:
    """The section as printed at the end of a run."""
    lines = ["", "## Grader findings (log-only)",
             f"coached replies {g['coached_replies']} · verdicts {g['verdicts']} · without a verdict "
             f"{g['without_verdict'] or 'none'}",
             "per criterion: " + (", ".join(f"{c} {k}" for c, k in g["per_criterion"].items()) or "none failed"),
             f"fails given without a quoted sentence (not counted): {g.get('not_counted', 0)}",
             "", "| turn | move | element | criterion | the sentence quoted | grader's reason |",
             "|---|---|---|---|---|---|"]
    lines += [f"| {f['n']} | {f['move']} | {f['element']} | {f['criterion']} | "
              f"{str(f.get('evidence') or '').replace('|', '/').replace(chr(10), ' ')} | "
              f"{str(f['reason']).replace('|', '/').replace(chr(10), ' ')} |" for f in g["findings"]]
    return "\n".join(lines)


def _cost(tokens: dict[str, Any]) -> dict[str, Any]:
    """R12 (founder ruling 2026-09-30): the run's model cost from its tokens per model and the
    dated price file; an unpriced model is recorded as a failure, never counted as free."""
    from scripts.run_cost import UnpricedModel, load_prices, run_cost
    try:
        return run_cost(tokens.get("by_model") or {}, load_prices())
    except UnpricedModel as exc:
        return {"usd": None, "within_ceiling": False, "error": str(exc)}


def cut_offs(calls: list[dict[str, Any]]) -> dict[str, Any]:
    """G-153: how many model calls stopped at their token limit (finish reason "length"), and which."""
    cut = [{"kind": c.get("kind"), "at": c.get("at"), "output_tokens": c.get("output_tokens")}
           for c in calls if c.get("finish_reason") == "length"]
    return {"count": len(cut), "calls": cut}


#: Founder ruling 2026-10-12 (turn time): each type's 90th percentile is WATCHED against this; it is
#: not a stop condition (45 s per turn stays the ceiling, DEF-093).
P90_WATCH_S = 30.0


def turn_times(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Founder ruling 2026-10-12: the run's turn times per turn type — count, median, 90th
    percentile, max — and the types whose 90th percentile reaches P90_WATCH_S. The types are
    ADR-0069's, from the record: the turn after an upload is the upload turn; teach and store-and-
    advance are teaching; every other turn the Belt answered is an answer turn, its read-backs
    split out; the gate's timed steps, and the first Measure turn, are their own rows."""
    import statistics
    groups: dict[str, list[float]] = {}
    upload = False
    for e in entries:
        kind = e.get("kind")
        if kind == "upload":
            upload = True
            continue
        if kind == "turn":
            move = e.get("move")
            name = ("upload" if upload else "teaching" if move in ("teach", "store_and_advance")
                    else "read-back" if move == "read_back" else "answer")
            upload = False
        elif kind in ("gate_review", "gate_submit", "gate_decision"):
            name = "gate"
        elif kind == "measure_turn":
            name = "first Measure turn"
        else:
            continue
        if e.get("seconds") is not None:
            groups.setdefault(name, []).append(float(e["seconds"]))
    out: dict[str, Any] = {}
    for name, secs in sorted(groups.items()):
        s = sorted(secs)
        out[name] = {"n": len(s), "median": round(statistics.median(s), 1),
                     "p90": s[min(len(s) - 1, max(0, -(-9 * len(s) // 10) - 1))], "max": s[-1]}
    return {"by_type": out, "p90_watch_s": P90_WATCH_S,
            "p90_over_watch": [n for n, v in out.items() if v["p90"] >= P90_WATCH_S]}


#: G-153 (founder ruling 2026-10-12): a cut-off coach reply is answered in code, permanently; a run
#: with more than this many cut-offs fails.
CUT_OFF_LIMIT = 1


def exit_code(summary: dict[str, Any], sends: list[Any]) -> int:
    """0 when the run passed; 3 when anything reached LangSmith; 4 when the run cost more than
    R12's ceiling (or could not be priced); 5 when more than CUT_OFF_LIMIT model calls were cut
    off at their token limit (G-153) — the acceptance test fails."""
    if sends:
        return 3
    cost = summary.get("cost") or {}
    if not cost.get("within_ceiling"):
        why = cost.get("error") or "USD {} over the ceiling of USD {}".format(cost.get("usd"), cost.get("ceiling_usd"))
        print(f"R12 COST CEILING: {why} — the run fails")
        return 4
    cut = int((summary.get("cut_offs") or {}).get("count") or 0)
    if cut > CUT_OFF_LIMIT:
        print(f"G-153 CUT-OFFS: {cut} model calls stopped at their token limit (limit {CUT_OFF_LIMIT}) — the run fails")
        return 5
    return 0


def _wallclock(stamp: str, scratch: Path) -> dict[str, Any]:
    """Founder ruling 4, 2026-09-28 (G-127): the tests that assert on wall-clock time run HERE,
    alone, not in the commit hook. Their outcomes go to docs/runthrough/wallclock_<stamp>.json,
    bound to the product source, which `features.status` reads. The run's own pytest session
    would rewrite docs/test-results.json (the recorder), so the file is restored after it."""
    import subprocess
    import xml.etree.ElementTree as ET
    project = Path(__file__).resolve().parents[1]
    results = project / "docs" / "test-results.json"
    saved = results.read_bytes() if results.is_file() else None
    junit = scratch / f"wallclock_{stamp}.xml"
    try:
        proc = subprocess.run([sys.executable, "-m", "pytest", "backend/tests", "-m", "wallclock", "-n", "0",
                               "-q", "-p", "no:cacheprovider", f"--junitxml={junit}"],
                              cwd=project, capture_output=True, encoding="utf-8", errors="replace", timeout=900)
    finally:
        if saved is not None:
            results.write_bytes(saved)
    outcomes: dict[str, str] = {}
    if junit.is_file():
        for case in ET.parse(junit).getroot().iter("testcase"):
            node = case.get("classname", "").replace(".", "/") + ".py::" + case.get("name", "")
            state = ("failed" if case.find("failure") is not None or case.find("error") is not None
                     else "skipped" if case.find("skipped") is not None else "passed")
            outcomes[node] = state
    rec = {"kind": "wallclock", "product_hash": _product_hash(), "recorded_at": stamp,
           "exit": proc.returncode, "outcomes": dict(sorted(outcomes.items()))}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"wallclock_{stamp}.json").write_text(json.dumps(rec, indent=1) + chr(10), encoding="utf-8")
    print(f"wall-clock tests: {rec['outcomes']}")
    return rec


def _time_it(started: float, calls: int) -> None:
    """Rule (g) — the live-model minutes, measured by the run itself."""
    import importlib.util
    path = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "timing.py"
    spec = importlib.util.spec_from_file_location("timing", path)
    if spec is None or spec.loader is None:
        return
    timing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(timing)
    timing.append({"kind": "live_model", "what": "6.66 define run-through",
                   "seconds": round(time.time() - started, 1), "calls": calls})


if __name__ == "__main__":
    sys.exit(main())
