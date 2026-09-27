#!/usr/bin/env python3
"""The prompt record — brief Part F9 (founder, 2026-09-27). One line per prompt, written at its end,
in `.claude/logs/prompts.jsonl` (gitignored, beside `timing.jsonl`). The report's timing line is a
summary of this record.

    python .claude/hooks/prompt_record.py record --start ISO --subject "…" [--features DEF-1,DEF-2]
        [--end ISO] [--waiting-min N] [--questions N] [--live-calls N]
    python .claude/hooks/prompt_record.py line            # the timing line of the last record

Each record: start, end, subject (the part or features), commits (from git log in the window),
and minutes by category, each VERIFIED (summed from the self-timed lines of `timing.jsonl`, or
read from git) or ASSUMED (given by the caller):

    tests       the pre-commit hook's full runs, pre-flight test runs, recorded test runs
    hooks       every other hook and pre-flight second
    waiting     time waiting for the founder (questions asked)                  ASSUMED
    rework      commit attempts that did not land, and failed pre-flights
    building    the rest of the wall clock
    live_model_calls   from the audit recorder's lines, else the caller's count

Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import timing  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
LOG = Path(os.environ.get("AGENTLEAN_LOGS") or ROOT / ".claude" / "logs") / "prompts.jsonl"
#: The time box of a prompt (brief Part F9.3, effective 2026-09-28).
TIME_BOX_MIN = 60


def _t(s: str) -> dt.datetime:
    d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def _commits(start: str, end: str) -> list[dict[str, str]]:
    out = subprocess.run(["git", "log", f"--since={start}", f"--until={end}", "--format=%h%x1f%cI%x1f%s"],
                         cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace").stdout
    rows = [line.split("\x1f") for line in out.splitlines() if line.strip()]
    return [{"sha": r[0], "at": r[1], "subject": r[2]} for r in reversed(rows) if len(r) == 3]


def _attempts(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group the hook lines into commit attempts: an attempt starts at a pre-commit line that
    follows a commit-msg line (or the first line) and holds everything until the next one."""
    out: list[dict[str, Any]] = []
    prev = ""
    for r in lines:
        name = str(r.get("hook") or "")
        if name.startswith("pre-commit") and (not out or prev.startswith("commit-msg")):
            out.append({"first": r["at"], "last": r["at"], "seconds": 0.0})
        if out:
            out[-1]["last"] = r["at"]
            out[-1]["seconds"] += float(r.get("seconds") or 0)
        prev = name
    return out


def measure(start: str, end: str, commits: list[dict[str, str]]) -> dict[str, Any]:
    lo, hi = _t(start), _t(end)
    inside = [r for r in timing.read() if lo <= _t(r["at"]) <= hi]
    hooks = [r for r in inside if r.get("kind") == "hook"]
    tests_s = sum(float(r.get("seconds") or 0) for r in hooks if r["hook"] == "pre-commit full test run")
    tests_s += sum(float(r.get("seconds") or 0) for r in inside if r.get("kind") == "tests")
    pre = [r for r in inside if r.get("kind") == "preflight"]
    tests_s += sum(float((r.get("checks") or {}).get("tests") or 0) for r in pre)
    hooks_s = sum(float(r.get("seconds") or 0) for r in hooks if r["hook"] != "pre-commit full test run")
    hooks_s += sum(float(r.get("seconds") or 0) - float((r.get("checks") or {}).get("tests") or 0) for r in pre)
    landed = [_t(c["at"]) for c in commits]
    rework_s = 0.0
    refused = 0
    for a in _attempts(hooks):
        f, last = _t(a["first"]), _t(a["last"])
        # git stamps a commit when `git commit` STARTS, before the hooks run; a hook line is
        # written when that hook ends — so a landed commit is dated before its attempt's lines.
        if not any(f - dt.timedelta(seconds=240) <= c <= last + dt.timedelta(seconds=30) for c in landed):
            rework_s += a["seconds"]
            refused += 1
    failed_pre = [r for r in pre if not r.get("ok")]
    rework_s += sum(float(r.get("seconds") or 0) for r in failed_pre)
    live = sum(int(r.get("calls") or 0) for r in inside if r.get("kind") == "live_model")
    return {"tests_s": tests_s, "hooks_s": hooks_s, "rework_s": rework_s, "refused_attempts": refused,
            "failed_preflights": len(failed_pre), "live_calls": live}


def record(start: str, end: str, subject: str, features: list[str], waiting_min: float,
           questions: int, live_calls: int | None) -> dict[str, Any]:
    commits = _commits(start, end)
    m = measure(start, end, commits)
    wall = (_t(end) - _t(start)).total_seconds() / 60
    tests, hooks, rework = m["tests_s"] / 60, m["hooks_s"] / 60, m["rework_s"] / 60
    building = max(wall - tests - hooks - waiting_min - rework, 0.0)
    calls = m["live_calls"] if live_calls is None else live_calls

    def cat(v: float, basis: str) -> dict[str, Any]:
        return {"value": round(v, 1), "basis": basis}

    rec = {"kind": "prompt", "start": start, "end": end, "subject": subject, "features": features,
           "commits": commits, "questions": questions,
           "refused_attempts": m["refused_attempts"], "failed_preflights": m["failed_preflights"],
           "minutes": {"total": cat(wall, "VERIFIED — the window"),
                       "building": cat(building, "VERIFIED — the rest of the window"),
                       "tests": cat(tests, "VERIFIED — timing.jsonl"),
                       "hooks": cat(hooks, "VERIFIED — timing.jsonl"),
                       "waiting_for_founder": cat(waiting_min, "ASSUMED — given"),
                       "rework": cat(rework, "VERIFIED — attempts that did not land, failed pre-flights")},
           "live_model_calls": calls}
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def read(log: Path | None = None) -> list[dict[str, Any]]:
    path = log or LOG
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def line(rec: dict[str, Any]) -> str:
    """The report's timing line — a summary of the record."""
    m = {k: v["value"] for k, v in rec["minutes"].items()}
    over = " — over the 60-minute box" if m["total"] > TIME_BOX_MIN else ""
    return (f"Timing: {m['total']:.0f} min{over} — building {m['building']:.0f} · tests {m['tests']:.0f} · "
            f"hooks {m['hooks']:.0f} · waiting for the founder {m['waiting_for_founder']:.0f} · "
            f"rework {m['rework']:.0f} ({rec['refused_attempts']} refused attempt(s), "
            f"{rec['failed_preflights']} failed pre-flight(s)) · {len(rec['commits'])} commits · "
            f"{rec['live_model_calls']} live model calls")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("--start", required=True)
    r.add_argument("--end", default=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
    r.add_argument("--subject", required=True)
    r.add_argument("--features", default="")
    r.add_argument("--waiting-min", type=float, default=0.0)
    r.add_argument("--questions", type=int, default=0)
    r.add_argument("--live-calls", type=int, default=None)
    sub.add_parser("line")
    a = ap.parse_args(argv)
    if a.cmd == "record":
        rec = record(a.start, a.end, a.subject, [x for x in a.features.split(",") if x],
                     a.waiting_min, a.questions, a.live_calls)
        print(line(rec))
        return 0
    recs = read()
    print(line(recs[-1]) if recs else "no prompt recorded yet")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
