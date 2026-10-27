"""C9 (founder ruling 2026-10-27, the coaching grader): the grader's verdicts from a run-through and an eval, one row per
graded turn and criterion, for the founder to label pass or fail — before the grader leaves log-only (ADR-0081).

Each row: where it came from, the element and move, the Belt's message, the reply the Belt was shown (its message and
blocks), the planner's judgment the grader was given, the criterion, the grader's verdict, the sentence it quoted and
its reason, and two empty columns, `founder_label` (pass / fail) and `founder_note`. A fail the grader gave without a
quote is shown as "not counted". The founder's labels are read back by `scripts/judge_replay.py --labels`.

    cd agent-improve; python -m scripts.grader_labels [--record <define_runthrough_*.json> ...]
        [--evals <evals_*.json> ...] [--out "Claude outputs/GRADER_LABELS.csv"]
With no --record or --evals, the newest of each.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

RECORDS = Path(__file__).resolve().parents[1] / "docs" / "runthrough"
OUT = Path(__file__).resolve().parents[1] / "Claude outputs" / "GRADER_LABELS.csv"
COLUMNS = ("row", "source", "element", "move", "belt_message", "reply", "planner_decision", "criterion",
           "grader_verdict", "grader_quote", "grader_reason", "founder_label", "founder_note")
#: What the founder needs at least of each (founder ruling 2026-10-27, C9).
AT_LEAST = 30


def _reply_text(reply: dict[str, Any] | None) -> str:
    """The reply as the Belt was shown it: the message, then its explanation, example and question blocks."""
    reply = reply or {}
    parts = [str(reply.get("answer") or "").strip()]
    for label, key in (("EXPLANATION", "explanation"), ("EXAMPLE", "example"), ("QUESTION", "prompt")):
        text = str(reply.get(key) or "").strip()
        if text:
            parts.append(f"[{label}] {text}")
    return "\n\n".join(p for p in parts if p)


def _rows_for(source: str, element: str, belt: str, reply: dict[str, Any] | None, grade: dict[str, Any]
              ) -> list[dict[str, Any]]:
    """One row per criterion of one grade: its verdict, and for a fail the quote and the reason."""
    failed = {str(f.get("criterion")): f for f in grade.get("failed") or [] if isinstance(f, dict)}
    uncounted = {str(f.get("criterion")): f for f in grade.get("not_counted") or [] if isinstance(f, dict)}
    rows = []
    for criterion, status in (grade.get("verdicts") or {}).items():
        f = failed.get(str(criterion)) or {}
        u = uncounted.get(str(criterion)) or {}
        verdict = "not counted (fail with no quote)" if status == "pass" and u else str(status)
        rows.append({"source": source, "element": element, "move": grade.get("move") or "",
                     "belt_message": belt, "reply": _reply_text(reply),
                     "planner_decision": grade.get("decision") or "", "criterion": criterion,
                     "grader_verdict": verdict, "grader_quote": f.get("evidence") or "",
                     "grader_reason": f.get("reason") or u.get("reason") or "", "founder_label": "",
                     "founder_note": ""})
    return rows


def from_runthrough(lines: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for t in (x for x in lines if x.get("kind") == "turn"):
        grade = t.get("grader")
        if isinstance(grade, dict) and grade.get("verdicts"):
            rows += _rows_for(f"{name} turn {t.get('n')}", str(t.get("field") or ""), str(t.get("belt") or ""),
                              t.get("reply") if isinstance(t.get("reply"), dict) else None, grade)
    return rows


def from_evals(record: dict[str, Any], name: str, tasks: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_id, runs in (record.get("runs") or {}).items():
        for trial, run in enumerate(runs or [], 1):
            for n, g in enumerate(run.get("grades") or [], 1):
                grade = g.get("grade") or {}
                if grade.get("verdicts"):
                    rows += _rows_for(f"{name} {task_id} trial {trial} turn {n}",
                                      str((tasks.get(task_id) or {}).get("element") or ""), str(g.get("belt") or ""),
                                      g.get("reply"), grade)
    return rows


def _newest(pattern: str) -> Path | None:
    files = sorted(RECORDS.glob(pattern))
    return files[-1] if files else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="append", default=[])
    ap.add_argument("--evals", action="append", default=[])
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)
    rows: list[dict[str, Any]] = []
    for record in [Path(r) for r in args.record] or [p for p in [_newest("define_runthrough_*.json")] if p]:
        rows += from_runthrough(json.loads(record.read_text(encoding="utf-8")), record.stem)
    from scripts.define_evals import load
    tasks = {t["id"]: t for t in load()}
    for evals in [Path(e) for e in args.evals] or [p for p in [_newest("evals_*.json")] if p]:
        rows += from_evals(json.loads(evals.read_text(encoding="utf-8")), evals.stem, tasks)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for i, r in enumerate(rows, 1):
            w.writerow({"row": i, **r})
    fails = sum(r["grader_verdict"] == "fail" for r in rows)
    passes = sum(r["grader_verdict"] == "pass" for r in rows)
    print(f"{out}: {len(rows)} rows — {fails} fails, {passes} passes, "
          f"{sum(r['grader_verdict'] == 'unknown' for r in rows)} unknown, "
          f"{sum(r['grader_verdict'].startswith('not counted') for r in rows)} not counted"
          + ("" if fails >= AT_LEAST and passes >= AT_LEAST else f" — fewer than {AT_LEAST} of each"))
    return 0 if fails >= AT_LEAST and passes >= AT_LEAST else 1


if __name__ == "__main__":
    sys.exit(main())
