"""Step 6.56 — the coaching proof driver. Positions 1-8 of Define, one case.

**OUTSIDE PYTEST, ON PURPOSE.** It drives real turns — a real model, real
storage — against a NEW case titled "COACHING PROOF — step 6.56, do not use
for other proofs", and writes one record per turn: what the Belt said, where
the walk stood, what the coach did, what the judges said, and the trace id.
Capability rows 26-32 are live-turn rows: the founder marks them from this
record. Row 10's check (`computation_results`' five keys) runs on its own once
a calculation turn exists.

TRACING IS OFF UNLESS `--traced`
--------------------------------
`init_tracing()` sets `LANGCHAIN_TRACING_V2=true` at app startup whenever an
API key exists (`core/tracing.py`), so `LANGSMITH_TRACING=false` on a server
process does NOT switch tracing off. This driver runs the app IN-PROCESS and,
unless `--traced`, switches tracing off the way the test suite does
(`conftest._no_tracing`) and counts every run the LangSmith client is asked to
create or send — any count above zero aborts the dry run.

In `--traced` mode it counts the project's root traces before the first turn
and after every turn, and stops if a turn created more than one.

WHAT IT NEVER DOES
------------------
It never submits a gate (`/gate` is not called), never retries a turn on an
error or a 429, and stops on the first non-200. Hard cap: `--max-turns`
(default 15).

THE SCRIPTED BELT
-----------------
A fictional project — late supplier payments at a hospital group — whose
values differ from every worked example in the Define script, so a captured
value that matches an example is visible (§22, row 27). The answer sent each
turn is chosen by the case's COMPUTED position (`define_position`), not by a
turn counter:

- position 4 is answered WEAKLY first (the weak-answer probe, row 31), then
  properly;
- a position that did not advance is answered once with a confirmation, then
  with the answer again, until the cap;
- after position 8 (the target) the Belt gives the two numbers the expected-
  savings calculation needs — the turn where row 26 (taught first) and row 10
  (recorded) become observable. The run ends after that turn.

Usage (from agent-improve/):
    python -m scripts.coaching_proof_656 --out <dir>            # dry, untraced
    python -m scripts.coaching_proof_656 --out <dir> --traced   # THE traced run
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

CASE_TITLE = "COACHING PROOF — step 6.56, do not use for other proofs"
DRY_TITLE = "COACHING PROOF DRY RUN — step 6.56, do not use"
USER = "coaching-proof-6.56"

OPENING = "Hi — I'm ready to start Define on our project."

ANSWERS: dict[int, str] = {
    1: ("Late payments to our suppliers are costing us: we paid about £62,000 in "
        "late-payment interest and lost early-payment discounts last year, and "
        "three key medical suppliers put us on stop twice this year, which held "
        "up ward stock."),
    2: ("I'm leading it — Priya Shah, Green Belt, running it day to day. Sponsor: "
        "Tom Okafor, Finance Director, who signs off and clears blockers. Process "
        "owner: Lena Hart, Accounts Payable Manager. Members: Dev Patel and Amira "
        "Khan, two AP clerks who process the invoices."),
    3: ("Our customers are the suppliers, who need paying on the agreed 30-day "
        "terms, and our own ward managers, who need stock to keep arriving. "
        "Suppliers complain most about payments arriving late and not knowing "
        "when they will be paid; ward managers about deliveries being held."),
    4: ("What: supplier invoices are paid after their 30-day terms. Where: the "
        "accounts payable team across our three hospital sites. When: every month "
        "since January 2026 — I measured January to June. Who: the suppliers, and "
        "the ward managers whose stock gets held. Why it matters: interest, lost "
        "discounts and supplier stops. How much: 23% of invoices were paid late "
        "over January to June 2026 — one measure, the late payment rate."),
    5: ("One metric: late payment rate, in %, meaning the share of supplier "
        "invoices paid more than 30 days after the invoice date. It is about 23% "
        "today, from the AP ledger for January to June 2026."),
    6: ("In scope: invoice receipt to payment release for purchase-order invoices "
        "at our three hospital sites. Out of scope: non-PO invoices, payroll, "
        "procurement tendering, and the ERP system itself."),
    7: "Reduce the late payment rate from 23% to under 5% by 31 March 2027.",
    8: "Late payment rate: under 5% of supplier invoices.",
}

#: Position 4's first answer — the weak-answer probe (row 31).
WEAK_4 = "The problem is basically that paying suppliers is slow and messy."

#: A position that did not advance gets this once.
CONFIRM = "Yes, that's right — please record it exactly as I said it."

#: After position 8: the two numbers expected savings needs (rows 26 and 10).
SAVINGS = ("Roughly, each late invoice costs us about £9 in interest and lost "
           "discount, and we pay around 42,000 supplier invoices a year.")


# ── tracing: off unless --traced ─────────────────────────────────────────

SENDS: list[str] = []
_CLIENT_SENDS = ("create_run", "update_run", "batch_ingest_runs", "multipart_ingest")


def _tracing_off() -> None:
    """`conftest._no_tracing` + `_count_tracing_calls`, outside pytest."""
    for name in ("LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING_V2",
                 "LANGSMITH_TRACING", "LANGCHAIN_TRACING"):
        os.environ[name] = "false"
    import langsmith.utils as ls_utils
    from langsmith import Client
    from langsmith.run_trees import configure
    getattr(ls_utils.get_env_var, "cache_clear")()
    for method in _CLIENT_SENDS:
        if hasattr(Client, method):
            setattr(Client, method,
                    lambda self, *a, _m=method, **k: SENDS.append(_m))
    import backend.app as app_mod
    import backend.core.tracing as tracing_mod
    tracing_mod.init_tracing = lambda: None  # type: ignore[assignment]
    app_mod.init_tracing = lambda: None      # type: ignore[attr-defined]
    configure(enabled=False)


def _langsmith():
    from langsmith import Client
    from backend.core.config import settings
    return Client(api_key=settings.LANGCHAIN_API_KEY), settings.LANGCHAIN_PROJECT


def _root_count(since: dt.datetime) -> int:
    client, project = _langsmith()
    return sum(1 for _ in client.list_runs(project_name=project, is_root=True,
                                           start_time=since, select=["id"]))


def _trace_id(case_id: str, started: dt.datetime) -> str | None:
    """The root trace of the turn that started at `started`, polled while
    LangSmith ingests it."""
    client, project = _langsmith()
    flt = (f'and(eq(metadata_key, "thread_id"), eq(metadata_value, "{case_id}"))')
    for _ in range(12):
        roots = [r for r in client.list_runs(project_name=project, is_root=True,
                                             filter=flt,
                                             start_time=started - dt.timedelta(seconds=5))
                 if r.end_time]
        if roots:
            return str(sorted(roots, key=lambda r: r.start_time)[0].trace_id)
        time.sleep(5)
    return None


# ── reading what the turn wrote ──────────────────────────────────────────


def _latest_final(case_id: str) -> dict:
    """The define subgraph's final state for the latest turn."""
    from urllib.parse import unquote
    from backend.core.checkpointer import get_checkpointer
    cp = get_checkpointer()
    prefix = f"checkpoints/{case_id}/ns/"
    finals = []
    for b in cp._container.list_blobs(name_starts_with=prefix):
        if not b.name.endswith("/latest.json"):
            continue
        ns = unquote(b.name[len(prefix):-len("/latest.json")])
        if "|" in ns or not ns.startswith("define"):
            continue
        t = cp.get_tuple({"configurable": {"thread_id": case_id, "checkpoint_ns": ns}})
        if t is not None:
            finals.append((t.checkpoint["ts"], t.checkpoint.get("channel_values") or {}))
    return sorted(finals, key=lambda f: f[0])[-1][1] if finals else {}


def _structured(client: Any, case_id: str) -> dict:
    """The case record, through the app's own route on the SAME client — a
    fresh `asyncio.run` per read left storage sessions on dead event loops
    ("SSL shutdown timed out") and hung the process at exit (dry run 1)."""
    resp = client.get(f"/cases/{case_id}")
    resp.raise_for_status()
    return dict(((resp.json().get("phases") or {}).get("define") or {}).get("structured") or {})


def _record(client: Any, n: int, belt: str, kind: str, before: int, resp: Any,
            seconds: float, case_id: str, trace: str | None) -> dict:
    from langchain_core.messages import HumanMessage, ToolMessage
    from backend.middleware.skills import example_match
    from backend.phases.define.schema import define_position
    final = _latest_final(case_id)
    log = [e for e in (final.get("step_log") or []) if isinstance(e, dict)]
    by = {str(e.get("node")): e for e in log}
    ex = by.get("executor", {})
    coh = by.get("coherence", {})
    grade = by.get("coaching_grader", {})
    pos = by.get("define_position", {})
    structured = _structured(client, case_id)
    msgs = list(final.get("messages") or [])
    starts = [i for i, m in enumerate(msgs) if isinstance(m, HumanMessage)]
    turn_msgs = msgs[(starts[-1] + 1) if starts else 0:]
    tools = sorted({m.name for m in turn_msgs if isinstance(m, ToolMessage) and m.name}
                   - {"CoachingResponse"})
    reply = next((str(m.content) for m in reversed(turn_msgs)
                  if isinstance(m, ToolMessage) and str(m.content).startswith(
                      "Returning structured response:")), "")
    captured = list(ex.get("fields_captured") or [])
    return {
        "turn": n, "kind": kind, "first_turn_in_process": n == 1,
        "position_before": before, "position_after": define_position(structured),
        "belt": belt, "status": resp.status_code, "seconds": round(seconds, 1),
        "trace_id": trace,
        "executor_status": ex.get("status"), "fields_captured": captured,
        "fields_example_refused": ex.get("fields_example_refused"),
        "captured_matches_an_example": {
            f: bool(example_match(structured.get(f), "define")) for f in captured},
        "tools_called": tools,
        "computation_rows": len(((final.get("artifacts") or {}).get("computation_results") or [])),
        "coherence": {k: coh.get(k) for k in ("coherent", "is_parroting", "reason", "script_step")},
        "grader": {k: grade.get(k) for k in ("status", "criteria_failed")},
        "progress": {k: pos.get(k) for k in ("label", "reply_progress", "reply_matches")},
        "answer": (resp.json().get("answer") if resp.status_code == 200 else resp.text)[:2000],
        "reply_blocks": reply[:3000],
    }


# ── the run ──────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, help="directory for the per-turn record")
    ap.add_argument("--traced", action="store_true", help="THE traced run (founder-approved)")
    ap.add_argument("--max-turns", type=int, default=15)
    ap.add_argument("--max-position", type=int, default=8)
    args = ap.parse_args()

    if not args.traced:
        _tracing_off()
    from fastapi.testclient import TestClient
    from backend.app import app
    from backend.phases.define.schema import define_position

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc)
    jsonl = out / f"coaching_proof_656_{'traced' if args.traced else 'dry'}_{stamp:%Y%m%dT%H%M%S}.jsonl"
    baseline = _root_count(stamp - dt.timedelta(seconds=1)) if args.traced else None

    records: list[dict] = []
    with TestClient(app) as client:
        created = client.post("/cases", json={
            "title": CASE_TITLE if args.traced else DRY_TITLE,
            "belt_level": "green", "leader": "Priya Shah",
            "department": "Finance — Accounts Payable",
            "target_date": "2027-03-31", "team": [],
        })
        if created.status_code != 200:
            print(f"STOP: case creation answered {created.status_code}: {created.text[:300]}")
            return 2
        case_id = created.json()["case_id"]
        print(f"case {case_id} ({'TRACED' if args.traced else 'dry, untraced'})")

        sent: dict[int, int] = {}     # position -> Belt messages sent at it
        savings_sent = False
        for n in range(1, args.max_turns + 1):
            position = define_position(_structured(client, case_id))
            if n == 1:
                belt, kind = OPENING, "opening"
            elif position > args.max_position:
                belt, kind, savings_sent = SAVINGS, "savings (rows 26, 10)", True
            else:
                # Per position: [the weak probe, at 4 only], the answer, one
                # confirmation — then the answer again until the cap.
                seq = ([(WEAK_4, "weak-answer probe (row 31)")] if position == 4 else []) + [
                    (ANSWERS[position], f"answer position {position}"),
                    (CONFIRM, f"confirm position {position}")]
                k = sent.get(position, 0)
                belt, kind = seq[k] if k < len(seq) else seq[-2]
                sent[position] = k + 1

            started = dt.datetime.now(dt.timezone.utc)
            t0 = time.time()
            resp = client.post("/ask", json={"case_id": case_id, "phase": "define",
                                             "message": belt, "user": USER})
            seconds = time.time() - t0
            trace = _trace_id(case_id, started) if args.traced else None
            rec = _record(client, n, belt, kind, position, resp, seconds, case_id, trace)
            records.append(rec)
            with jsonl.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            print(f"turn {n:2} [{kind}] pos {position}->{rec['position_after']} "
                  f"{resp.status_code} {rec['seconds']}s captured={rec['fields_captured']} "
                  f"coherent={rec['coherence']['coherent']} grade={rec['grader']['status']} "
                  f"calc_rows={rec['computation_rows']} trace={trace}")

            if resp.status_code != 200:
                print("STOP: first error — no retry.")
                break
            if not args.traced and SENDS:
                print(f"STOP: the dry run asked LangSmith to send {len(SENDS)} run(s).")
                return 3
            if args.traced:
                made = _root_count(stamp - dt.timedelta(seconds=1)) - (baseline or 0)
                if made > n:
                    print(f"STOP: {made} traces after {n} turn(s) — over one per turn.")
                    break
            if savings_sent:
                break

    print(f"{len(records)} turn(s) recorded -> {jsonl}")
    if not args.traced:
        print(f"LangSmith sends in this dry run: {len(SENDS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
