"""DEF-253 (T103, founder ruling 2026-10-21; the lesson of 2026-10-20): a LIVE SLICE — one changed element tested live.

The recorded answers of a run-through are replayed up to that element: the elements before it are seeded on a fresh
case as confirmed, from the record's final case (no model call). Only that element's turns run live — the Belt's
messages the record sent while it was in focus, through its Confirm — with their model calls, cost and checks
recorded. The one full run-through per day stays the acceptance run (R12).

    cd agent-improve; python -m scripts.live_slice --element issues_and_barriers [--record <define_runthrough_*.json>]
                                                    [--max-calls 30]

Founder test 2026-10-27 (wave 0): `--seed-case <case id>` seeds the elements before the slice's own from a real case's
confirmed values (the founder's IMPR-2026-PDLWG9) instead of a run-through record, and `--messages <file.json>` sends
the Belt's exact messages — a list of {"message", "action"?, "element"?} — instead of the recorded turns. Every turn
keeps the server's timing line per step (#63) in the record.

The record goes to docs/runthrough/live_slice_<element>_<stamp>.json, with the product hash it ran on.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path
from typing import Any

OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "runthrough"
USER = "live-slice"

#: The helper keys an element's confirmation also stores, by element: seeded only when that element comes before the
#: slice's own, so a slice never starts with its own element half-answered.
HELPERS = {"critical_to_quality": "voc_summary", "problem_5w2h": "problem_statement",
           "metric_definitions": "baseline_estimate", "computation_results": "benefits_analysis"}


def plan_slice(record: list[dict[str, Any]], element: str) -> dict[str, Any]:
    """What the slice seeds and what it runs live, from a run-through record — no model call, no storage.
    `structured` and `field_status`: every element before `element` confirmed, with its own helper keys; `element`
    asked (taught). `turns`: the Belt's messages the record sent while `element` was in focus, through its Confirm."""
    from backend.phases import moves
    positions = list(moves.positions("define"))
    names = [f for f, _ in positions]
    if element not in names:
        raise ValueError(f"{element!r} is not a Define element: {names}")
    before = names[:names.index(element)]
    final = next((x for x in record if x.get("kind") == "final_case"), {}).get("define_structured") or {}
    structured: dict[str, Any] = {}
    for field, fields in positions[:len(before)]:
        for f in fields or (field,):
            if f in final:
                structured[f] = final[f]
    for key, owner in HELPERS.items():
        if key in final and owner in before:
            structured[key] = final[key]
    field_status: dict[str, dict[str, Any]] = {f: {"status": moves.CONFIRMED} for f in before}
    field_status[element] = {"status": moves.ASKED}
    turns_all = [x for x in record if x.get("kind") == "turn"]
    turns = [t for prev, t in zip(turns_all, turns_all[1:]) if prev.get("field") == element]
    return {"element": element, "structured": structured, "field_status": field_status,
            "turns": [{"n": t.get("n"), "belt": t.get("belt") or "", "action": t.get("action"),
                       "recorded_move": t.get("move")} for t in turns],
            "product_hash": next((x for x in record if x.get("kind") == "summary"), {}).get("product_hash")}


def plan_from_case(structured: dict[str, Any], element: str) -> dict[str, Any]:
    """`plan_slice`'s seed, from a real case's confirmed values (`structured`) instead of a run-through record: every
    element before `element` confirmed with its own helper keys, `element` asked. No turns: `--messages` gives them."""
    from backend.phases import moves
    positions = list(moves.positions("define"))
    names = [f for f, _ in positions]
    if element not in names:
        raise ValueError(f"{element!r} is not a Define element: {names}")
    before = names[:names.index(element)]
    seeded: dict[str, Any] = {}
    for field, fields in positions[:len(before)]:
        for f in fields or (field,):
            if f in structured:
                seeded[f] = structured[f]
    for key, owner in HELPERS.items():
        if key in structured and owner in before:
            seeded[key] = structured[key]
    field_status: dict[str, dict[str, Any]] = {f: {"status": moves.CONFIRMED} for f in before}
    field_status[element] = {"status": moves.ASKED}
    return {"element": element, "structured": seeded, "field_status": field_status, "turns": [], "product_hash": None}


def scripted_turns(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """`--messages`: the Belt's exact messages as the slice's turns."""
    return [{"n": i, "belt": str(m["message"]), "action": m.get("action"), "element": m.get("element"),
             "recorded_move": None} for i, m in enumerate(messages, 1)]


def _timing(queue: Any) -> list[str]:
    """#63: the server's timing lines for the turn just answered ("before the graph   1.29 s", …), drained."""
    lines: list[str] = []
    while queue is not None and not queue.empty():
        message = queue.get_nowait().getMessage()
        if message.startswith("turn timing · "):
            lines.append(" ".join(message[len("turn timing · "):].split()))
    return lines


def replay(client: Any, case_id: str, plan: dict[str, Any], timing: Any = None) -> dict[str, Any]:
    """The live half: each of the element's recorded messages sent, in order, through POST /ask. Passed when a turn
    stored the element and moved on: a store_and_advance, or a Confirm whose reply is on another element (the goal's
    Confirm reads the target back from it, A8 — 2026-10-22)."""
    out: list[dict[str, Any]] = []

    def moved_on(x: dict[str, Any]) -> bool:
        return x["move"] == "store_and_advance" or (
            x.get("action") == "confirm" and x["http"] == 200 and x.get("move_field") not in (None, plan["element"]))
    for t in plan["turns"]:
        body = {"case_id": case_id, "phase": "define", "user": USER, "message": t["belt"],
                **({"action": t["action"]} if t.get("action") else {}),
                **({"element": t["element"]} if t.get("element") else {})}
        sent = time.time()
        r = client.post("/ask", json=body)
        got = r.json() if r.status_code == 200 else {}
        answer = str(got.get("answer") or getattr(r, "text", "") or "")
        out.append({"n": t["n"], "belt": t["belt"][:200], "action": t.get("action"), "http": r.status_code,
                    "move": got.get("move"), "move_field": got.get("move_field"),
                    "recorded_move": t.get("recorded_move"), "seconds": round(time.time() - sent, 1),
                    "failed": got.get("failed"), "answer": answer[:400],
                    "asks_to_send_again": "send" in answer.lower() and "again" in answer.lower(),
                    "steps": _timing(timing)})
        if moved_on(out[-1]):
            break
    return {"turns": out, "passed": any(moved_on(x) for x in out)}


def _latest_record() -> Path:
    files = sorted(OUT_DIR.glob("define_runthrough_*.json"))
    if not files:
        raise SystemExit("no run-through record in docs/runthrough/")
    return files[-1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--element", required=True)
    ap.add_argument("--record", default="")
    ap.add_argument("--max-calls", type=int, default=30)
    ap.add_argument("--seed-case", default="", help="seed from this case's confirmed values (founder test 2026-10-27)")
    ap.add_argument("--messages", default="", help="a JSON list of the Belt's messages to send instead of the record's")
    args = ap.parse_args()
    import asyncio

    from scripts.define_runthrough import _cost, _product_hash, _tracing_off
    from scripts.move_proof_661 import CALLS, STORAGE, _count_model_calls, _time_storage, storage_since, token_totals
    _tracing_off()
    _count_model_calls(args.max_calls)
    _time_storage()
    import logging
    import queue
    from logging.handlers import QueueHandler

    from fastapi.testclient import TestClient

    from backend.app import app
    from backend.storage import blob
    framing = {"title": f"LIVE SLICE — {args.element}", "leader": "Priya Shah",
               "department": "Finance — Accounts Payable"}
    if args.seed_case:
        from backend.gateway.routes import _with_unfinished_work

        async def read_case() -> Any:
            case = await blob.load_case(args.seed_case)
            assert case is not None, f"case {args.seed_case} not found"
            return await _with_unfinished_work(case)
        seed_case = asyncio.run(read_case())
        plan = plan_from_case(dict(seed_case.phases["define"].structured or {}), args.element)
        framing = {"title": f"LIVE SLICE — {args.element} — seeded from {args.seed_case}: {seed_case.title}",
                   "leader": seed_case.leader, "department": seed_case.department}
        source = Path(args.seed_case)
    else:
        source = Path(args.record) if args.record else _latest_record()
        plan = plan_slice(json.loads(source.read_text(encoding="utf-8")), args.element)
    if args.messages:
        plan["turns"] = scripted_turns(json.loads(Path(args.messages).read_text(encoding="utf-8")))
    timing: Any = queue.Queue()
    logging.getLogger("backend.gateway.routes").addHandler(QueueHandler(timing))
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    with TestClient(app) as client:
        created = client.post("/cases", json={"title": framing["title"], "belt_level": "green",
                                              "leader": framing["leader"], "department": framing["department"],
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
        s0 = len(STORAGE)
        result = replay(client, case_id, plan, timing)
        final = client.get(f"/cases/{case_id}").json()
    stored = args.element in (((final.get("phases") or {}).get("define") or {}).get("structured") or {})
    checks = {"the element's recorded turns were found": bool(plan["turns"]),
              "a turn stored the element and moved on": result["passed"],
              "the element is in the case record": stored}
    if args.messages:
        # The founder's scripted messages (wave 0, R-F): the slice is judged on the turns, not on a store.
        checks = {"every message was sent": len(result["turns"]) == len(plan["turns"]),
                  "no turn was discarded (HTTP 200, not failed)": all(
                      x["http"] == 200 and not x["failed"] for x in result["turns"]),
                  "no reply asks the Belt to send again": not any(x["asks_to_send_again"] for x in result["turns"]),
                  "every turn logged its steps": all(x["steps"] for x in result["turns"])}
    entry = {"kind": "live_slice", "element": args.element, "case_id": case_id, "from_record": source.name,
             "messages": args.messages and Path(args.messages).name,
             "recorded_product_hash": plan["product_hash"], "product_hash": _product_hash(),
             "seeded": sorted(plan["structured"]), "turns": result["turns"], "checks": checks,
             "passed": all(checks.values()), "model_calls": len(CALLS), "cost": _cost(token_totals(CALLS)),
             "storage": storage_since(s0), "started": stamp}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"live_slice_{args.element}_{stamp}.json"
    out.write_text(json.dumps(entry, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"live slice {args.element}: {'PASS' if entry['passed'] else 'FAIL'} · case {case_id} · "
          f"{len(result['turns'])} live turn(s) · model calls {len(CALLS)} · USD {entry['cost'].get('usd')}")
    for name, ok in checks.items():
        print(f"  {'ok ' if ok else 'NO '} {name}")
    print(f"record: {out}")
    return 0 if entry["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
