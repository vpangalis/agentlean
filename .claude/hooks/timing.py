#!/usr/bin/env python3
"""The value-stream timing log — step 6.65 (founder ruling 2026-09-25, rule g).

ONE append-only, machine-readable log: `.claude/logs/timing.jsonl` — the
existing hook-log area (gitignored, as `drift.log` is), so appending never
dirties the tree. One JSON object per line.

WHO WRITES WHAT
    the hooks            {"kind": "hook", "hook": ..., "seconds": ...}   self-timed
    the test recorder    {"kind": "tests", "seconds", "workers", "outcomes"}  self-timed
    the audit recorder   {"kind": "live_model", "calls", "seconds"}      self-timed
    the prompt record    {"kind": "prompt", "prompt", "step", "start", "end",
                          "minutes": {category: {"value", "basis"}}}
        one per prompt, written at report time; each category is VERIFIED
        (summed from the self-timed lines inside the prompt's window, or read
        from git) or ASSUMED (estimated), and says which.

    python .claude/hooks/timing.py summarise START END   # sums the self-timed lines

Standard library only: the hooks run it with whatever python is on PATH.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
#: 6.68 — a run inside the staged worktree (staged_tree.py) logs to the
#: checkout's own log directory, named by AGENTLEAN_LOGS.
LOG = Path(os.environ.get("AGENTLEAN_LOGS") or ROOT / ".claude" / "logs") / "timing.jsonl"

#: The categories of a prompt record, in the founder's order (rule g).
CATEGORIES: tuple[str, ...] = (
    "reading_docs", "coding", "tests", "live_model_calls", "hooks",
    "documentation", "waiting_for_founder",
)


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def append(record: dict[str, Any], log: Path | None = None) -> None:
    """Append one record. Never raises — timing must not fail a commit or a
    test run; a record that could not be written is a lost measurement, not
    a broken tool."""
    path = log or Path(os.environ.get("TIMING_LOG") or LOG)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"at": now(), **record}, ensure_ascii=False) + "\n")
    except (OSError, ValueError):
        pass


def read(log: Path | None = None) -> list[dict[str, Any]]:
    path = log or Path(os.environ.get("TIMING_LOG") or LOG)
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def summarise(start: str, end: str, log: Path | None = None) -> dict[str, Any]:
    """The self-timed lines inside [start, end], summed per category —
    everything here is VERIFIED; the rest of a prompt record is estimated."""
    lo, hi = dt.datetime.fromisoformat(start), dt.datetime.fromisoformat(end)
    inside = [r for r in read(log)
              if r.get("kind") in ("hook", "tests", "live_model")
              and lo <= dt.datetime.fromisoformat(r["at"]) <= hi]
    hooks: dict[str, float] = {}
    for r in inside:
        if r["kind"] == "hook":
            hooks[r["hook"]] = hooks.get(r["hook"], 0.0) + float(r.get("seconds") or 0)
    tests = [r for r in inside if r["kind"] == "tests"]
    live = [r for r in inside if r["kind"] == "live_model"]
    return {
        "hooks_seconds": {k: round(v, 1) for k, v in sorted(hooks.items())},
        "tests": {"runs": len(tests), "seconds": round(sum(float(r.get("seconds") or 0) for r in tests), 1)},
        "live_model": {"calls": sum(int(r.get("calls") or 0) for r in live),
                       "seconds": round(sum(float(r.get("seconds") or 0) for r in live), 1)},
    }


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "summarise":
        print(json.dumps(summarise(sys.argv[2], sys.argv[3]), indent=1))
        sys.exit(0)
    print(__doc__)
    sys.exit(2)
