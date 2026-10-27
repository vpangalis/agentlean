"""C9 (founder ruling 2026-10-27, the coaching grader; the founder's blind-sheet ruling the same day): the coach's graded
turns from a run-through and an eval, as two files joined by a row id, the rows shuffled so the grader's fails and
passes are mixed:

- GRADER_LABELS.csv — what the founder labels, blind: the Belt's message, the confirmed values given to the coach,
  the move, the planner's decision, the coach's reply, and empty columns pass / fail / n/a for G1, G3, G4 and G6
  (the criteria the model judges), with a note.
- GRADER_VERDICTS.csv — the grader's verdicts, quotes and reasons per criterion (the code checks G2 and G4's order
  beside them), keyed by the same row id, with where each row came from.

`scripts/judge_replay.py --labels GRADER_LABELS.csv --verdicts GRADER_VERDICTS.csv` joins them.

The confirmed values are the coach's own section 3 block (`<confirmed_values>`): for a run-through turn, read from the
coach's recorded input (`--scratch` of the run); for an eval trial, built by the same function from the case the eval
seeded (`state_injection.confirmed_values`, from the run-through record the eval was seeded from).

    cd agent-improve; python -m scripts.grader_labels --record <define_runthrough_*.json> --inputs <its _inputs.jsonl>
        --evals <evals_*.json> [--out-dir "Claude outputs"]
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
from pathlib import Path
from typing import Any

OUT_DIR = Path(__file__).resolve().parents[1] / "Claude outputs"
LABELS, VERDICTS = "GRADER_LABELS.csv", "GRADER_VERDICTS.csv"
#: The criteria the founder labels — those the model judges (founder ruling 2026-10-27, A3).
LABELLED = ("G1", "G3", "G4", "G6")
#: The code checks, shown with the verdicts (never labelled).
CODE = ("G2", "G4-order")
LABEL_COLUMNS = ("row_id", "belt_message", "confirmed_values", "move", "planner_decision", "coach_reply",
                 *(f"{c}_founder" for c in LABELLED), "founder_note")
VERDICT_COLUMNS = ("row_id", "source", "element", "move",
                   *(f"{c}_{k}" for c in (*LABELLED, *CODE) for k in ("verdict", "quote", "reason")))
#: The order is shuffled, the same way each time.
SEED = 20261027
#: What the founder needs at least of each (founder ruling 2026-10-27, C9).
AT_LEAST = 30
_CONFIRMED = re.compile(r"<confirmed_values>.*?</confirmed_values>", re.S)


def _reply_text(reply: dict[str, Any] | None) -> str:
    """The reply as the Belt was shown it: the message, then its explanation, example and question blocks."""
    reply = reply or {}
    parts = [str(reply.get("answer") or "").strip()]
    for label, key in (("EXPLANATION", "explanation"), ("EXAMPLE", "example"), ("QUESTION", "prompt")):
        text = str(reply.get(key) or "").strip()
        if text:
            parts.append(f"[{label}] {text}")
    return "\n\n".join(p for p in parts if p)


def _verdicts(grade: dict[str, Any]) -> dict[str, str]:
    """The grade's verdict, quote and reason per criterion; a fail with no quote reads "not counted"."""
    failed = {str(f.get("criterion")): f for f in grade.get("failed") or [] if isinstance(f, dict)}
    uncounted = {str(f.get("criterion")): f for f in grade.get("not_counted") or [] if isinstance(f, dict)}
    out: dict[str, str] = {}
    for criterion, status in (grade.get("verdicts") or {}).items():
        f, u = failed.get(str(criterion)) or {}, uncounted.get(str(criterion)) or {}
        out[f"{criterion}_verdict"] = "not counted (fail with no quote)" if status == "pass" and u else str(status)
        out[f"{criterion}_quote"] = str(f.get("evidence") or "")
        out[f"{criterion}_reason"] = str(f.get("reason") or u.get("reason") or "")
    return out


def _turn(source: str, element: str, belt: str, confirmed: str, reply: dict[str, Any] | None,
          grade: dict[str, Any]) -> dict[str, Any]:
    return {"source": source, "element": element, "move": grade.get("move") or "", "belt_message": belt,
            "confirmed_values": confirmed, "planner_decision": grade.get("decision") or "",
            "coach_reply": _reply_text(reply), "verdicts": _verdicts(grade)}


def coach_inputs(path: Path | None) -> dict[int, str]:
    """Per run-through turn, the confirmed values in the coach's first input of that turn (its section 3 block)."""
    out: dict[int, str] = {}
    if path is None or not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        found = _CONFIRMED.search(json.dumps(entry.get("coach_inputs") or [], ensure_ascii=False))
        if found:
            out.setdefault(int(entry.get("n") or 0), json.loads(f'"{found.group(0)}"'))
    return out


def from_runthrough(lines: list[dict[str, Any]], name: str, confirmed: dict[int, str]) -> list[dict[str, Any]]:
    turns = []
    for t in (x for x in lines if x.get("kind") == "turn"):
        grade = t.get("grader")
        if isinstance(grade, dict) and grade.get("verdicts"):
            turns.append(_turn(f"{name} turn {t.get('n')}", str(t.get("field") or ""), str(t.get("belt") or ""),
                               confirmed.get(int(t.get("n") or 0), ""),
                               t.get("reply") if isinstance(t.get("reply"), dict) else None, grade))
    return turns


def seeded_values(record: list[dict[str, Any]], element: str) -> str:
    """The confirmed values the coach was given on an eval trial's first turn: section 3's block, by the coach's own
    function, from the case the eval seeded from `record` (scripts/live_slice.plan_slice)."""
    from backend.middleware.state_injection import confirmed_values
    from scripts.live_slice import plan_slice
    values = confirmed_values("define", dict(plan_slice(record, element)["structured"]), element)
    return "\n".join(["<confirmed_values>", *values, "</confirmed_values>"])


def from_evals(record: dict[str, Any], name: str, tasks: dict[str, dict[str, Any]],
               seed: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    turns = []
    for task_id, runs in (record.get("runs") or {}).items():
        element = str((tasks.get(task_id) or {}).get("element") or "")
        confirmed = seeded_values(seed, element) if seed and element else ""
        for trial, run in enumerate(runs or [], 1):
            for n, g in enumerate(run.get("grades") or [], 1):
                grade = g.get("grade") or {}
                if grade.get("verdicts"):
                    turns.append(_turn(f"{name} {task_id} trial {trial} turn {n}", element, str(g.get("belt") or ""),
                                       confirmed if n == 1 else "(as the turn before, with its answer)",
                                       g.get("reply"), grade))
    return turns


def write(turns: list[dict[str, Any]], out_dir: Path) -> tuple[Path, Path, dict[str, int]]:
    """The two files, the rows shuffled (fixed seed) and numbered R001…; counts of the labelled criteria's verdicts."""
    order = list(turns)
    random.Random(SEED).shuffle(order)
    out_dir.mkdir(parents=True, exist_ok=True)
    labels, verdicts = out_dir / LABELS, out_dir / VERDICTS
    with labels.open("w", encoding="utf-8-sig", newline="") as lf, verdicts.open("w", encoding="utf-8-sig",
                                                                                 newline="") as vf:
        lw, vw = csv.DictWriter(lf, fieldnames=LABEL_COLUMNS), csv.DictWriter(vf, fieldnames=VERDICT_COLUMNS)
        lw.writeheader()
        vw.writeheader()
        for i, t in enumerate(order, 1):
            rid = f"R{i:03d}"
            lw.writerow({"row_id": rid, **{k: t[k] for k in LABEL_COLUMNS[1:6]},
                         **{f"{c}_founder": "" for c in LABELLED}, "founder_note": ""})
            vw.writerow({"row_id": rid, "source": t["source"], "element": t["element"], "move": t["move"],
                         **{k: t["verdicts"].get(k, "") for k in VERDICT_COLUMNS[4:]}})
    counts = {"turns": len(order)}
    for status in ("fail", "pass", "unknown"):
        counts[status] = sum(t["verdicts"].get(f"{c}_verdict") == status for t in order for c in LABELLED)
    return labels, verdicts, counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="append", default=[], help="a run-through record (its turns are rows)")
    ap.add_argument("--inputs", action="append", default=[], help="that run's --scratch _inputs.jsonl, in order")
    ap.add_argument("--evals", action="append", default=[], help="an eval record (its graded turns are rows)")
    ap.add_argument("--seed-record", default="", help="the run-through record the evals were seeded from")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args(argv)
    turns: list[dict[str, Any]] = []
    for i, rec in enumerate(Path(r) for r in args.record):
        inputs = Path(args.inputs[i]) if i < len(args.inputs) else None
        turns += from_runthrough(json.loads(rec.read_text(encoding="utf-8")), rec.stem, coach_inputs(inputs))
    if args.evals:
        from scripts.define_evals import load
        tasks = {t["id"]: t for t in load()}
        seed_path = args.seed_record or (args.record[0] if args.record else "")
        seed = json.loads(Path(seed_path).read_text(encoding="utf-8")) if seed_path else None
        for ev in (Path(e) for e in args.evals):
            turns += from_evals(json.loads(ev.read_text(encoding="utf-8")), ev.stem, tasks, seed)
    labels, verdicts, counts = write(turns, Path(args.out_dir))
    ok = counts["fail"] >= AT_LEAST and counts["pass"] >= AT_LEAST
    print(f"{labels}\n{verdicts}\n{counts['turns']} turns; G1/G3/G4/G6 verdicts: {counts['fail']} fails, "
          f"{counts['pass']} passes, {counts['unknown']} unknown" + ("" if ok else f" — fewer than {AT_LEAST} of each"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
