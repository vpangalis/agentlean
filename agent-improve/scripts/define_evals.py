"""DEF-142 (T86, ADR-0061): the offline Define eval set — tasks from real failures, graded by code, then the rubric
model, with a human sample; each task runs k = 3 times and pass^3 is reported.

A task (evals/define/define_tasks.jsonl, one JSON object per line): `id`, `status` (candidate until the founder marks
it keep / change / drop — testing rule §12.1: the dataset is authored jointly, not generated), `source` (the defect),
`element`, `messages` [{text, action?}], `expect` (the code grader's checks, below), `why`.

The starting state is a live slice's (scripts/live_slice.py): the elements before `element` seeded as confirmed from
a run-through record. The rubric stage costs no extra call: it reads the coaching grader's verdict the live turn
already logged (define_runthrough.grader_entry).

    cd agent-improve; python -m scripts.define_evals [--status keep] [--k 3] [--max-calls 150]

Runs are deliberate (ADR-0061 decision 4): live calls, within the live-call budget. The record goes to
docs/runthrough/evals_<stamp>.json.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

TASKS = Path(__file__).resolve().parents[1] / "evals" / "define" / "define_tasks.jsonl"
OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "runthrough"
MARKS = ("keep", "change", "drop")
KNOWN = {"move", "move_not", "move_field", "stored", "moves_equal", "reply_contains", "reply_contains_any",
         "reply_not_contains", "card_row", "card_rows_at_most", "card_contains", "card_confirm",
         "question_at_most_once", "rubric_pass"}


def load(path: Path = TASKS) -> list[dict[str, Any]]:
    """The tasks, each checked for its shape; a malformed line raises with its line number."""
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        task = json.loads(line)
        missing = {"id", "status", "source", "element", "messages", "expect", "why"} - set(task)
        unknown = set(task.get("expect") or {}) - KNOWN
        if missing or unknown or not task.get("messages"):
            raise ValueError(f"line {n}: missing {sorted(missing)}, unknown checks {sorted(unknown)}")
        out.append(task)
    return out


def _card_text(card: dict[str, Any] | None) -> str:
    return json.dumps(card or {}, ensure_ascii=False, default=str)


def grade(task: dict[str, Any], outcome: dict[str, Any]) -> dict[str, Any]:
    """The code grader, then the rubric stage: each check of `expect` on the run's outcome — `replies` (each POST
    /ask body), `stored` (is the element in the case record), `rubric` (the grader's status per coached turn).
    Returns {"passed", "failed": [the checks that failed, in words]}."""
    e = task["expect"]
    replies = outcome.get("replies") or [{}]
    last = replies[-1] or {}
    answer = str(last.get("answer") or "")
    card = last.get("readback_card") or {}
    rows = {str(r.get("id")): r for r in (card.get("rows") or []) if isinstance(r, dict)}
    failed: list[str] = []
    if "move" in e and last.get("move") != e["move"]:
        failed.append(f"move {last.get('move')!r}, expected {e['move']!r}")
    if "move_not" in e and last.get("move") == e["move_not"]:
        failed.append(f"move {last.get('move')!r}, never expected")
    if "move_field" in e and last.get("move_field") != e["move_field"]:
        failed.append(f"focus {last.get('move_field')!r}, expected {e['move_field']!r}")
    if "stored" in e and bool(outcome.get("stored")) != e["stored"]:
        failed.append(f"stored {bool(outcome.get('stored'))}, expected {e['stored']}")
    if e.get("moves_equal") and len({r.get("move") for r in replies}) > 1:
        failed.append(f"moves differ: {[r.get('move') for r in replies]}")
    for s in e.get("reply_contains") or []:
        if s.lower() not in answer.lower():
            failed.append(f"reply lacks {s!r}")
    if e.get("reply_contains_any") and not any(s.lower() in answer.lower() for s in e["reply_contains_any"]):
        failed.append(f"reply has none of {e['reply_contains_any']}")
    for s in e.get("reply_not_contains") or []:
        if s.lower() in answer.lower():
            failed.append(f"reply holds {s!r}")
    if "card_row" in e:
        row = rows.get(e["card_row"]["id"]) or {}
        if e["card_row"]["contains"].lower() not in str(row.get("value") or "").lower():
            failed.append(f"card row {e['card_row']['id']!r} lacks {e['card_row']['contains']!r}")
    if "card_rows_at_most" in e:
        value = (rows.get(e["card_rows_at_most"]["id"]) or {}).get("value")
        n = len(value.get("rows") or []) if isinstance(value, dict) else (len(value) if isinstance(value, list) else 0)
        if n > e["card_rows_at_most"]["count"]:
            failed.append(f"card row {e['card_rows_at_most']['id']!r} has {n} rows")
    for s in e.get("card_contains") or []:
        if s.lower() not in _card_text(card).lower():
            failed.append(f"card lacks {s!r}")
    if "card_confirm" in e and bool(card.get("confirm")) != e["card_confirm"]:
        failed.append(f"card Confirm {bool(card.get('confirm'))}, expected {e['card_confirm']}")
    if e.get("question_at_most_once"):
        q = str(last.get("prompt") or "").strip()[:60]
        if q and answer.count(q) > 1:
            failed.append("the question is shown twice")
    if e.get("rubric_pass") and any(s == "failed" for s in outcome.get("rubric") or []):
        failed.append(f"rubric: {outcome.get('rubric')}")
    return {"passed": not failed, "failed": failed}


def pass_k(runs: list[dict[str, Any]]) -> bool:
    """pass^k (ADR-0061 decision 3): a task passes only when every one of its k runs passed."""
    return bool(runs) and all(r["passed"] for r in runs)


def human_sample(results: dict[str, bool], every: int = 5) -> list[str]:
    """The transcripts a human reads (ADR-0061 decision 2): every failure, and every `every`-th pass."""
    passed = [t for t, ok in results.items() if ok]
    return sorted([t for t, ok in results.items() if not ok] + passed[::every])


def run_task(client: Any, task: dict[str, Any], record: list[dict[str, Any]]) -> dict[str, Any]:
    """One live run of a task: a fresh case seeded up to its element, its messages sent, the outcome graded."""
    import asyncio

    from backend.storage import blob
    from scripts.define_runthrough import grader_entry
    from scripts.live_slice import plan_slice
    plan = plan_slice(record, task["element"])
    created = client.post("/cases", json={"title": f"EVAL {task['id']} — {task['source']}", "belt_level": "green",
                                          "leader": "Priya Shah", "department": "Finance — Accounts Payable",
                                          "target_date": "2027-03-31", "team": []})
    created.raise_for_status()
    case_id = created.json()["case_id"]

    async def seed() -> None:
        case = await blob.load_case(case_id)
        assert case is not None
        case.phases["define"].structured = dict(plan["structured"])
        case.phases["define"].field_status = {f: dict(v) for f, v in plan["field_status"].items()}
        await blob.save_case(case)
    asyncio.run(seed())
    replies, rubric = [], []
    for m in task["messages"]:
        body = {"case_id": case_id, "phase": "define", "user": "eval", "message": m["text"],
                **({"action": m["action"]} if m.get("action") else {})}
        r = client.post("/ask", json=body)
        replies.append(r.json() if r.status_code == 200 else {"http": r.status_code})
        g = grader_entry(case_id, m["text"])
        if g:
            rubric.append(g.get("status"))
    structured = ((client.get(f"/cases/{case_id}").json().get("phases") or {}).get("define") or {}).get("structured")
    outcome = {"replies": replies, "stored": task["element"] in (structured or {}), "rubric": rubric}
    return {"case_id": case_id, **grade(task, outcome),
            "moves": [r.get("move") for r in replies], "rubric": rubric}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="keep", help="which tasks: keep (the final set) or candidate")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--max-calls", type=int, default=150)
    ap.add_argument("--record", default="")
    args = ap.parse_args()
    from scripts.define_runthrough import _cost, _product_hash, _tracing_off
    from scripts.live_slice import _latest_record
    from scripts.move_proof_661 import CALLS, _count_model_calls, token_totals
    _tracing_off()
    _count_model_calls(args.max_calls)
    tasks = [t for t in load() if t["status"] == args.status]
    record = json.loads((Path(args.record) if args.record else _latest_record()).read_text(encoding="utf-8"))
    from fastapi.testclient import TestClient

    from backend.app import app
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    per_task: dict[str, list[dict[str, Any]]] = {}
    with TestClient(app) as client:
        for task in tasks:
            per_task[task["id"]] = [run_task(client, task, record) for _ in range(args.k)]
    results = {t: pass_k(runs) for t, runs in per_task.items()}
    summary = {"kind": "evals", "started": stamp, "status": args.status, "k": args.k, "tasks": len(tasks),
               "pass_k": sum(results.values()), "results": results, "human_sample": human_sample(results),
               "runs": per_task, "model_calls": len(CALLS), "cost": _cost(token_totals(CALLS)),
               "product_hash": _product_hash()}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"evals_{stamp}.json"
    out.write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"pass^{args.k}: {summary['pass_k']} of {len(tasks)} · model calls {len(CALLS)} · "
          f"USD {summary['cost'].get('usd')} · human sample {summary['human_sample']}")
    print(f"record: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
