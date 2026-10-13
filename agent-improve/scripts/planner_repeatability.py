"""Founder ruling 2026-10-13, A7 (G-168, option A then B if unstable): the planner's judgment, replayed.

  cases  G-168's two judgment cases (evals/define/judgment_cases.json), REPEATS times each, with the live
         phase context they were judged with: how often the verdict is the expected one, and how often
         the `baseline` criterion fails.
  turns  every turn of the evaluation set the planner judged (a challenge, a read-back or a respond move),
         REPEATS times each, as a first answer with no earlier answer and no case context: the share of
         turns whose verdict flips, per recorded move, and the `baseline` criterion's flips.

The ruling's line: if the baseline judgment still flips more than 1 in 5, it is decided in code (option B).
Replay only: nothing in the product changes.

    cd agent-improve; python -m scripts.planner_repeatability
"""
from __future__ import annotations

import asyncio
import collections
import json
import sys
import time
from pathlib import Path
from typing import Any

EVALS = Path(__file__).resolve().parents[1] / "evals" / "define"
REPEATS = 5
JUDGED_MOVES = ("challenge", "read_back", "respond")


async def _judge(case: dict[str, Any]) -> dict[str, Any]:
    from scripts.judge_replay import replay_judgment
    try:
        return await replay_judgment(case)
    except Exception as exc:  # noqa: BLE001 — a failed call is counted, never a crash
        return {"id": case["id"], "error": repr(exc)[:200]}


async def run() -> dict[str, Any]:
    cases = json.loads((EVALS / "judgment_cases.json").read_text(encoding="utf-8"))["cases"]
    turns = [t for t in json.loads((EVALS / "judge_turns.json").read_text(encoding="utf-8"))["turns"]
             if t["move"] in JUDGED_MOVES and (t.get("script_step") or {}).get("field")]
    as_cases = [{"id": t["id"], "field": t["script_step"]["field"], "belt": t["belt"], "expected": None,
                 "phase_context": "", "move": t["move"]} for t in turns]
    out: dict[str, Any] = {"cases": collections.defaultdict(list), "turns": collections.defaultdict(list)}
    for kind, items in (("cases", cases), ("turns", as_cases)):
        for item in items:
            for _ in range(REPEATS):
                out[kind][item["id"]].append(await _judge(item))   # serial: the tier's rate limit (429)
    out["moves"] = {t["id"]: t["move"] for t in as_cases}
    return out


def analyse(out: dict[str, Any]) -> dict[str, Any]:
    ok = lambda xs: [x for x in xs if "error" not in x]          # noqa: E731
    cases = {i: {"agree": sum(x["agrees"] for x in ok(xs)), "of": len(ok(xs)),
                 "baseline_fails": sum(x.get("failed_criterion") == "baseline" for x in ok(xs)),
                 "verdicts": [x["verdict"] for x in ok(xs)]} for i, xs in out["cases"].items()}
    per_move: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])     # [turns, flipped]
    flipped, baseline_flips = [], []
    for i, xs in out["turns"].items():
        verdicts = {x["verdict"] for x in ok(xs)}
        move = out["moves"][i]
        per_move[move][0] += 1
        if len(verdicts) > 1:
            per_move[move][1] += 1
            flipped.append(i)
        crit = [x.get("failed_criterion") == "baseline" for x in ok(xs)]
        if any(crit) and not all(crit):
            baseline_flips.append(i)
    n = len(out["turns"]) or 1
    return {"cases": cases,
            "turns": {"judged": len(out["turns"]), "flipped": len(flipped), "flip_share": round(len(flipped) / n, 2),
                      "flipped_ids": flipped,
                      "per_move": {m: {"turns": a, "flipped": f, "share": round(f / a, 2) if a else None}
                                   for m, (a, f) in per_move.items()},
                      "baseline_criterion_flips": baseline_flips},
            "errors": sum("error" in x for k in ("cases", "turns") for xs in out[k].values() for x in xs)}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    from scripts.coaching_proof_656 import _tracing_off
    from scripts.define_runthrough import _cost
    from scripts.move_proof_661 import CALLS, _count_model_calls, token_totals
    _tracing_off()
    _count_model_calls(1000)
    t0 = time.time()
    out = asyncio.run(run())
    result: dict[str, Any] = {"analysis": analyse(out), "seconds": round(time.time() - t0, 1), "calls": len(CALLS),
              "cost": _cost(token_totals(CALLS)), "raw": {k: dict(v) if isinstance(v, dict) else v for k, v in out.items()}}
    path = EVALS / f"planner_repeatability_{time.strftime('%Y%m%dT%H%M%S', time.gmtime())}.json"
    path.write_text(json.dumps(result, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps(result["analysis"], indent=1, ensure_ascii=False))
    print(f"seconds {result['seconds']}, calls {result['calls']}, cost {result['cost'].get('usd')}; record {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
