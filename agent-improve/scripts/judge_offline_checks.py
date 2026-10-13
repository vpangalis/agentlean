"""Founder ruling 2026-10-13, item 3 — offline checks of the coaching grader on the evaluation set (the
coherence judge is retired, ADR-0083). Replay only: nothing in the product changes.

  c  repeatability — the grader replayed REPEATS times per turn; the share of turns whose verdict flips;
     per criterion, the flip rate and which criteria cause flips (B2's line: >= 90% repeat)
  d  grader fail drivers — per criterion, how often it fails, and on which moves
  g  truncation — replies over the grader's 4,000-character cut, and whether the [QUESTION TO THE BELT]
     block is cut off

    cd agent-improve; python -m scripts.judge_offline_checks
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
ABLATION = 3
CONCURRENCY = 1          # 8 in parallel hit the deployment's rate limit (429) on 397 of 520 calls
CUT = 4000


async def _grade(turn: dict[str, Any]) -> dict[str, Any]:
    from backend.middleware.grader import DMAICGraderMiddleware
    g = await DMAICGraderMiddleware("define", move=turn["move"])._grade(turn["belt"], turn["reply_judged"])
    return {"passed": g.passed, "criteria": {c.criterion: c.status for c in g.criteria},
            "failed": [c.criterion for c in g.failed]}


async def run(turns: list[dict[str, Any]]) -> dict[str, Any]:
    sem = asyncio.Semaphore(CONCURRENCY)

    async def limited(coro: Any) -> Any:
        async with sem:
            return await coro
    jobs: list[tuple[str, str, Any]] = []
    for t in turns:
        jobs += [(t["id"], "grader", _grade(t)) for _ in range(REPEATS)]
    results = await asyncio.gather(*(limited(c) for _, _, c in jobs), return_exceptions=True)
    out: dict[str, dict[str, list[Any]]] = collections.defaultdict(lambda: collections.defaultdict(list))
    for (tid, kind, _), r in zip(jobs, results):
        out[tid][kind].append(r if not isinstance(r, BaseException) else {"error": repr(r)[:200]})
    return out


def _ok(xs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [x for x in xs if "error" not in x]


def analyse(turns: list[dict[str, Any]], out: dict[str, Any]) -> dict[str, Any]:
    by_id = {t["id"]: t for t in turns}
    # c — repeatability
    grd_flip = [i for i in out if len({x["passed"] for x in _ok(out[i]["grader"])}) > 1]
    crit_runs: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])    # [turns seen, turns flipped]
    for i in out:
        statuses: dict[str, set[str]] = collections.defaultdict(set)
        for x in _ok(out[i]["grader"]):
            for c, s in x["criteria"].items():
                statuses[c].add(s)
        for c, s in statuses.items():
            crit_runs[c][0] += 1
            crit_runs[c][1] += len(s) > 1
    flips_by_criterion = {c: {"turns": n, "flipped": f, "rate": round(f / n, 2)} for c, (n, f) in
                          sorted(crit_runs.items(), key=lambda kv: -kv[1][1])}
    # d — grader fail drivers
    fails: dict[str, dict[str, int]] = collections.defaultdict(lambda: collections.defaultdict(int))
    graded: dict[str, int] = collections.defaultdict(int)
    for i in out:
        move = by_id[i]["move"]
        for x in _ok(out[i]["grader"]):
            graded[move] += 1
            for c in x["failed"]:
                fails[c][move] += 1
    drivers = {c: {"fails": sum(m.values()), "by_move": dict(m)} for c, m in
               sorted(fails.items(), key=lambda kv: -sum(kv[1].values()))}
    # g — truncation
    long = [{"id": t["id"], "chars": len(t["reply_judged"]),
             "question_cut": "[QUESTION TO THE BELT]" in t["reply_judged"]
             and t["reply_judged"].index("[QUESTION TO THE BELT]") >= CUT}
            for t in turns if len(t["reply_judged"]) > CUT]
    errors = sum("error" in x for i in out for k in out[i] for x in out[i][k])
    n = len(out) or 1
    return {
        "c_repeatability": {"turns": len(out), "grader_flipped": len(grd_flip),
                            "grader_flip_share": round(len(grd_flip) / n, 2),
                            "grader_repeat_share": round(1 - len(grd_flip) / n, 2),
                            "grader_flips_by_criterion": flips_by_criterion, "grader_flipped_ids": grd_flip},
        "d_grader_fail_drivers": {"graded_by_move": dict(graded), "by_criterion": drivers},
        "g_truncation": {"over_4000": len(long), "question_block_cut": sum(x["question_cut"] for x in long),
                         "turns": long},
        "errors": errors,
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    from scripts.coaching_proof_656 import _tracing_off
    from scripts.define_runthrough import _cost
    from scripts.move_proof_661 import CALLS, _count_model_calls, token_totals
    _tracing_off()
    _count_model_calls(2000)
    turns = json.loads((EVALS / "judge_turns.json").read_text(encoding="utf-8"))["turns"]
    t0 = time.time()
    out = asyncio.run(run(turns))
    result: dict[str, Any] = {"analysis": analyse(turns, out), "seconds": round(time.time() - t0, 1),
              "calls": len(CALLS), "cost": _cost(token_totals(CALLS)), "raw": out}
    path = EVALS / f"judge_offline_checks_{time.strftime('%Y%m%dT%H%M%S', time.gmtime())}.json"
    path.write_text(json.dumps(result, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(f"seconds {result['seconds']}, calls {result['calls']}, cost {result['cost'].get('usd')}; record {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
