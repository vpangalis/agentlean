"""DEF-142 (T86, ADR-0061): the offline Define eval set — tasks from real failures, graded by code, then the rubric
model, with a human sample; each task runs k = 3 times and pass^3 is reported.

A task (evals/define/define_tasks.jsonl, one JSON object per line): `id`, `status` (candidate until the founder marks
it keep / change / drop — testing rule §12.1: the dataset is authored jointly, not generated), `source` (the defect),
`element`, `messages` [{text, action?}], `expect` (the code grader's checks, below), `why`.

The starting state is a live slice's (scripts/live_slice.py): the elements before `element` seeded as confirmed from
a run-through record. The rubric stage costs no extra call: it reads the coaching grader's verdict the live turn
already logged (define_runthrough.grader_entry).

    cd agent-improve; python -m scripts.define_evals [--status final] [--ids E03,E04] [--k 3] [--max-calls 150]

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
#: The eval set: the tasks kept and the tasks changed as the founder said (marks of 2026-10-23); a dropped one never runs.
FINAL = ("keep", "change")
KNOWN = {"move", "move_not", "move_field", "stored", "moves_equal", "reply_contains", "reply_contains_any",
         "reply_contains_each_any",
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
    for group in e.get("reply_contains_each_any") or []:
        if not any(s.lower() in answer.lower() for s in group):
            failed.append(f"reply has none of {group}")
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
    # G-251: on the app's own event loop (the TestClient's portal). A fresh asyncio.run left the storage client's
    # session on a dead loop each trial ("SSL shutdown timed out") and the run of 2026-10-23 hung at exit.
    client.portal.call(seed)
    replies, rubric, grades = [], [], []
    for m in task["messages"]:
        body = {"case_id": case_id, "phase": "define", "user": "eval", "message": m["text"],
                **({"action": m["action"]} if m.get("action") else {})}
        r = client.post("/ask", json=body)
        replies.append(r.json() if r.status_code == 200 else {"http": r.status_code})
        g = grader_entry(case_id, m["text"])
        if g:
            rubric.append(g.get("status"))
            # C9 (founder ruling 2026-10-27): each graded turn whole, for GRADER_LABELS.csv — the Belt's message,
            # the reply's blocks, the move and the grader's entry (verdicts, quotes, the planner's decision given).
            last = replies[-1] if isinstance(replies[-1], dict) else {}
            grades.append({"belt": m["text"], "grade": g, "move": last.get("move"),
                           "reply": {k: last.get(k) for k in ("answer", "explanation", "example", "prompt")}})
    structured = ((client.get(f"/cases/{case_id}").json().get("phases") or {}).get("define") or {}).get("structured")
    outcome = {"replies": replies, "stored": task["element"] in (structured or {}), "rubric": rubric}
    return {"case_id": case_id, **grade(task, outcome),
            "moves": [r.get("move") for r in replies], "rubric": rubric, "grades": grades,
            # ADR-0061 decision 2: the human sample reads what the Belt was shown.
            "answers": [str(r.get("answer") or r.get("http") or "") for r in replies]}


async def outcome_from_case(case_id: str, task: dict[str, Any]) -> dict[str, Any]:
    """G-251: one trial graded OFFLINE from its case — no model call. Each Belt message's reply body is rebuilt from
    the reply message the /ask route projects (its text, coaching_move, readback_card, coaching_blocks); `stored`
    from the case as the app reloads it; the rubric from the define subgraph's latest checkpoint (the last turn's
    verdict only)."""
    from langchain_core.messages import AIMessage, HumanMessage

    from backend.core import conversation
    from backend.core.graph import get_graph
    from backend.gateway.routes import _with_unfinished_work
    from backend.storage import blob
    from scripts.define_runthrough import grader_entry
    case = await blob.load_case(case_id)
    if case is None:
        raise ValueError(f"{case_id} not found")
    snap = await get_graph().aget_state({"configurable": {"thread_id": case_id}})
    replies: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for m in (snap.values or {}).get("messages") or []:
        if isinstance(m, HumanMessage):
            if current is not None:
                replies.append(current)
            current = {}
        elif isinstance(m, AIMessage) and not m.tool_calls and m.text.strip() and current is not None:
            extra = dict(m.additional_kwargs or {})
            current = {"answer": m.text, "move": (extra.get("coaching_move") or {}).get("move"),
                       "move_field": (extra.get("coaching_move") or {}).get("field"),
                       "readback_card": extra.get(conversation.CARD_KEY),
                       "prompt": str((extra.get("coaching_blocks") or {}).get("prompt") or "")}
    if current is not None:
        replies.append(current)
    seen = await _with_unfinished_work(case)
    stored = task["element"] in dict(seen.phases["define"].structured or {})
    g = grader_entry(case_id, task["messages"][-1]["text"])
    rubric = [g.get("status")] if g else []
    return {"case_id": case_id, **grade(task, {"replies": replies, "stored": stored, "rubric": rubric}),
            "moves": [r.get("move") for r in replies], "rubric": rubric,
            "answers": [r.get("answer") for r in replies]}


def regrade(record_path: Path) -> dict[str, Any]:
    """G-251: an eval record graded again from its cases, offline (the record names each trial's case)."""
    import asyncio
    old = json.loads(record_path.read_text(encoding="utf-8"))
    tasks = {t["id"]: t for t in load()}

    async def all_runs() -> dict[str, list[dict[str, Any]]]:
        return {tid: [await outcome_from_case(r["case_id"], tasks[tid]) for r in runs]
                for tid, runs in old["runs"].items()}
    per_task = asyncio.run(all_runs())
    results = {t: pass_k(runs) for t, runs in per_task.items()}
    return {**{k: v for k, v in old.items() if k not in ("runs", "results", "pass_k", "human_sample")},
            "regraded_from": record_path.name, "pass_k": sum(results.values()), "results": results,
            "trials_passed": {t: sum(bool(r["passed"]) for r in v) for t, v in per_task.items()},
            "human_sample": human_sample(results), "runs": per_task}


def write_record(path: Path, summary: dict[str, Any]) -> None:
    """The record, replaced whole: written to a sibling file, then renamed over it."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(summary, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


def run_all(client: Any, tasks: list[dict[str, Any]], record: list[dict[str, Any]], k: int, out: Path,
            base: dict[str, Any], measures: Any) -> dict[str, Any]:
    """G-251: every task k times; the record is written after EACH trial (`complete` false) and the summary before
    returning — the caller returns inside the client block, so a hang at shutdown loses nothing. `measures()` gives
    the calls and cost at the time of writing."""
    per_task: dict[str, list[dict[str, Any]]] = {}

    def summary(complete: bool) -> dict[str, Any]:
        results = {t: pass_k(runs) for t, runs in per_task.items()}
        return {**base, "complete": complete, "tasks": len(tasks), "trials": sum(len(v) for v in per_task.values()),
                "pass_k": sum(results.values()), "results": results,
                "trials_passed": {t: sum(bool(r.get("passed")) for r in v) for t, v in per_task.items()},
                "human_sample": human_sample(results), "runs": per_task, **measures()}
    for task in tasks:
        for _ in range(k):
            per_task.setdefault(task["id"], []).append(run_task(client, task, record))
            write_record(out, summary(complete=False))
    final = summary(complete=True)
    write_record(out, final)
    return final


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="final", help="which tasks: final (keep and change), or one status")
    ap.add_argument("--ids", default="", help="comma-separated task ids — a diagnosis run of those tasks only")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--max-calls", type=int, default=150)
    ap.add_argument("--record", default="")
    ap.add_argument("--regrade", default="", help="an eval record: grade its trials again from their cases, offline")
    args = ap.parse_args()
    if args.regrade:
        again = regrade(Path(args.regrade))
        write_record(Path(args.regrade), again)
        print(f"pass^{again['k']}: {again['pass_k']} of {len(again['runs'])} (regraded offline) · "
              f"trials passed {again['trials_passed']}")
        return 0
    from scripts.define_runthrough import _cost, _product_hash, _tracing_off
    from scripts.live_slice import _latest_record
    from scripts.move_proof_661 import CALLS, _count_model_calls, token_totals
    _tracing_off()
    _count_model_calls(args.max_calls)
    wanted = FINAL if args.status == "final" else (args.status,)
    ids = {i.strip() for i in args.ids.split(",") if i.strip()}
    tasks = [t for t in load() if t["status"] in wanted and (not ids or t["id"] in ids)]
    record = json.loads((Path(args.record) if args.record else _latest_record()).read_text(encoding="utf-8"))
    from fastapi.testclient import TestClient

    from backend.app import app
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"evals_{stamp}.json"
    base = {"kind": "evals", "started": stamp, "status": args.status, "ids": sorted(ids), "k": args.k,
            "product_hash": _product_hash()}
    with TestClient(app) as client:
        summary = run_all(client, tasks, record, args.k, out, base,
                          lambda: {"model_calls": len(CALLS), "cost": _cost(token_totals(CALLS))})
    print(f"pass^{args.k}: {summary['pass_k']} of {len(tasks)} · model calls {len(CALLS)} · "
          f"USD {summary['cost'].get('usd')} · human sample {summary['human_sample']}")
    print(f"record: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
