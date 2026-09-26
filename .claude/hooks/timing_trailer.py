#!/usr/bin/env python3
"""prepare-commit-msg — append this commit's pre-commit timing as a `Timing:` trailer. Step 6.67.

The founder's board shows "the last commits with their timing lines", read
from git log only; the timing log itself is untracked. So the line has to
travel in the commit. `prepare-commit-msg` runs AFTER pre-commit and before
the message is final: it sums the timing records the pre-commit wrote since
its start marker (`.claude/logs/pre-commit-start`) and appends one line:

    Timing: pre-commit 118 s — full test run 104 s · continuity 2 s · control-board 6 s

Fail-SOFT and silent: a timing line is a measurement, never a reason to stop
a commit. Skipped for merge and squash messages, and when a line is present.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / ".claude" / "logs" / "timing.jsonl"
START = ROOT / ".claude" / "logs" / "pre-commit-start"


def line(start: float, rows: list[dict]) -> str | None:
    lo = dt.datetime.fromtimestamp(start, dt.timezone.utc)
    parts: dict[str, float] = {}
    for r in rows:
        if r.get("kind") != "hook" or not str(r.get("hook", "")).startswith("pre-commit "):
            continue
        if dt.datetime.fromisoformat(r["at"]) < lo:
            continue
        name = r["hook"][len("pre-commit "):]
        parts[name] = parts.get(name, 0.0) + float(r.get("seconds") or 0)
    if not parts:
        return None
    total = round(sum(parts.values()))
    detail = " · ".join(f"{k} {round(v)} s" for k, v in parts.items())
    suite = "" if "full test run" in parts else " (docs only: no suite)"
    return f"Timing: pre-commit {total} s{suite} — {detail}"


def main(argv: list[str]) -> int:
    if len(argv) < 2 or (len(argv) > 2 and argv[2] in ("merge", "squash")):
        return 0
    msg = Path(argv[1])
    text = msg.read_text(encoding="utf-8")
    if "\nTiming:" in text or not START.is_file():
        return 0
    rows = [json.loads(ln) for ln in LOG.read_text(encoding="utf-8").splitlines() if ln.strip()]
    got = line(float(START.read_text().strip()), rows)
    if got:
        msg.write_text(text.rstrip("\n") + "\n" + got + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception:  # noqa: BLE001 — a measurement never stops a commit
        sys.exit(0)
