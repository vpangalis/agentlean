"""Step 6.66 Part 7 — THE DEFINE RUN-THROUGH: the measured distance to "Define works end to end".

**OUTSIDE PYTEST, ON PURPOSE**, like `move_proof_661.py` (whose model-call
counter and cap it reuses) and `coaching_proof_656.py` (whose tracing switch and
LangSmith send-counter it reuses): real model calls, real storage, the real
`POST /ask` route, a NEW case. Tracing is OFF and every send is counted.

A scripted Belt walks all twelve Define fields. Each message is chosen from the
MOVE RECORD the last reply carried (founder ruling R5: the move is decided in
code), never from a turn counter:

    teach / challenge / respond / store_and_advance  ->  answer the named field
    read_back                                         ->  click Confirm
Probes, each once: a WEAK first answer at the problem statement (4); a CHANGE
click at the voice of the customer (3); a TYPED correction at the goal (7);
"where do we stand?" before the scope (6); the savings figures before the
target date (9); an evidence upload before the SIPOC (11). Then the gate:
`GET /gate/review`, and `POST /gate` — as far as the gate exists today.

THE CAP — `--max-calls` (default 150, founder ruling 2026-09-25, diagnosis
included) counted at the chat-model boundary, every role; the call past it
raises and the run stops with what it has. A field challenged three times is
recorded as STUCK and the walk stops there. Either way the gate steps run
(they make no model call), so the record always says how far Define got.

THE RECORD — one lean JSON line per turn, plus a summary line carrying the
source hash it ran on, written to `docs/runthrough/` (tracked: the tests in
`backend/tests/test_define_runthrough.py` read it, and fail when it is older
than the source). The coach's full inputs go to `--scratch`, never the tree.

    cd agent-improve; python -m scripts.define_runthrough --scratch <dir>
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path
from typing import Any

from scripts.coaching_proof_656 import ANSWERS, SAVINGS, SENDS, WEAK_4, _tracing_off
from scripts.move_proof_661 import CALLS, COACH_INPUTS, CapReached, _count_model_calls

CASE_TITLE = "DEFINE RUN-THROUGH — step 6.66, do not use for other proofs"
USER = "define-runthrough-6.66"
OPENING = "Hi — I'm ready to start Define on our project."
WHERE = "Where do we stand?"
OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "runthrough"
MAX_ATTEMPTS = 3            # answers to one field before it is recorded STUCK

#: The good answer per field. Positions 1-8 are 6.56's scripted Belt; 9-12 are new.
GOOD: dict[str, str] = {
    "business_case": ANSWERS[1], "team": ANSWERS[2], "voc_summary": ANSWERS[3],
    "problem_statement": ANSWERS[4], "baseline_estimate": ANSWERS[5],
    "project_scope": ANSWERS[6], "goal_statement": ANSWERS[7], "target_value": ANSWERS[8],
    "target_date": "We plan to finish the project by 31 March 2027 (2027-03-31).",
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
        "to payment release, and the share of invoices with a match exception."),
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


def _write(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def _source_hash() -> str:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "control_board"))
    import progress
    return progress.source_hash()


class Walk:
    """The scripted Belt. State: which probes have fired, answers per field."""

    def __init__(self) -> None:
        self.fired: set[str] = set()
        self.attempts: dict[str, int] = {}

    def once(self, probe: str) -> bool:
        if probe in self.fired:
            return False
        self.fired.add(probe)
        return True

    def next(self, move: str | None, field: str | None) -> tuple[str, str | None, str]:
        """(message, action, why) for the reply that carried `move` on `field`."""
        if move == "read_back":
            if field == "voc_summary" and self.once("change"):
                return "Change", "change", "probe: Change click"
            if field == "goal_statement" and self.once("typed-correction"):
                return GOAL_CORRECTION, None, "probe: typed correction"
            return "Confirm", "confirm", "confirm click"
        if field is None:
            return "", None, "done"
        if move in ("teach", "store_and_advance"):
            if field == "project_scope" and self.once("where"):
                return WHERE, None, "probe: where do we stand"
            if field == "target_date" and self.once("savings"):
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
            "move": mrec.get("move"), "field": mrec.get("field"), "status": mrec.get("status"),
            "verdict": judgment.get("verdict") if isinstance(judgment, dict) else None,
            "stored_field": (mrec.get("stored") or {}).get("field") if isinstance(mrec.get("stored"), dict) else mrec.get("stored_field"),
            "stored_keys": sorted(structured),
            "stored_types": {k: type(v).__name__ for k, v in structured.items()},
            "reply": {k: rb.get(k) for k in ("answer", "explanation", "example", "prompt",
                                             "progress", "move", "move_field", "grader_warning")},
            "gate_status": rb.get("gate_status"),
            "fallback": bool(mrec.get("fallback")),
            "error": None if resp.status_code == 200 else resp.text[:400],
        }
        _write(rec, line)
        _write(scratch, {"n": n, "coach_inputs": COACH_INPUTS[i0:], "move_record": mrec})
        out["turns"] = n
        print(f"{n:>2} [{why}] http={resp.status_code} move={line['move']} field={line['field']} "
              f"verdict={line['verdict']} calls={len(CALLS) - c0} total={len(CALLS)} {seconds}s")
        if resp.status_code != 200:
            out["stopped"] = f"http {resp.status_code}"
            break
        walk._field = line["field"]  # type: ignore[attr-defined]
        message, action, why = walk.next(line["move"], line["field"])
        if why == "stuck":
            out["stuck_at"] = line["field"]

    # ── the gate, as far as it exists: review, then submit (no model call) ──
    rv = client.get(f"/gate/review/{case_id}/define")
    review = rv.json() if rv.status_code == 200 else {"error": rv.text[:400]}
    _write(rec, {"kind": "gate_review", "http": rv.status_code, "body": review})
    sb = client.post("/gate", json={"case_id": case_id, "submitted_by": USER, "phase": "define"})
    submit = sb.json() if sb.headers.get("content-type", "").startswith("application/json") else {"text": sb.text[:400]}
    _write(rec, {"kind": "gate_submit", "http": sb.status_code, "body": submit})
    final = client.get(f"/cases/{case_id}").json()
    _write(rec, {"kind": "final_case", "current_phase": final.get("current_phase"),
                 "define_structured": ((final.get("phases") or {}).get("define") or {}).get("structured"),
                 "field_log_keys": sorted(((final.get("phases") or {}).get("define") or {}).get("field_log") or {})[:200]})
    print(f"gate review {rv.status_code} · submit {sb.status_code} · phase now {final.get('current_phase')}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-calls", type=int, default=150)
    ap.add_argument("--scratch", required=True, help="where the coach's full inputs go (outside the tree)")
    args = ap.parse_args()
    _tracing_off()
    _count_model_calls(args.max_calls)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rec = OUT_DIR / f"define_runthrough_{stamp}.jsonl"
    scratch = Path(args.scratch) / f"define_runthrough_{stamp}_inputs.jsonl"
    scratch.parent.mkdir(parents=True, exist_ok=True)
    source = _source_hash()
    started = time.time()
    from fastapi.testclient import TestClient
    from backend.app import app
    out: dict[str, Any] = {}
    with TestClient(app) as client:
        try:
            out = run(client, rec, scratch, args.max_calls)
        except CapReached as exc:
            out["stopped"] = f"cap: {exc}"
    summary = {"kind": "summary", "source_hash": source, "started": stamp,
               "minutes": round((time.time() - started) / 60, 1), "cap": args.max_calls,
               "model_calls": len(CALLS),
               "by_kind": {k: sum(c["kind"] == k for c in CALLS) for k in sorted({c["kind"] for c in CALLS})},
               "langsmith_sends": len(SENDS), **out}
    _write(rec, summary)
    print(json.dumps(summary, indent=1, default=str))
    _time_it(started, len(CALLS))
    print(f"record: {rec}")
    return 0 if not SENDS else 3


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
