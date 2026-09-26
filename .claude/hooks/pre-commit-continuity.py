#!/usr/bin/env python3
"""pre-commit writer — CONTINUITY.md's status block, and the feature ratchet. Step 6.67.

Fail-SOFT: a writing hook that breaks must never wedge a commit; the
commit-msg guard's rules 5 and 11 are the fail-closed checks. Two writes:

  1. CONTINUITY.md's CURRENT BUILD STATUS block, from `continuity_status.build_block`
     (the features and the recorded run), staged.
  2. `docs/features-ratchet.json` — every feature passing in the record just
     written by the commit's full run is added (never removed), staged. Rule 11
     reads the COMMITTED ratchet (HEAD's) as the set that must keep passing.

The pre-6.67 writer also spliced a step board into the procedure; the
procedure is archived (`docs/_archive/retired-tooling/hooks/pre-commit-continuity.py`).
"""
from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import continuity_status as cs  # noqa: E402

RATCHET = "agent-improve/docs/features-ratchet.json"


def note(msg: str) -> None:
    print(f"  [continuity] {msg}", file=sys.stderr)


def _git(args: list[str], root: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, encoding="utf-8", errors="replace",
                          cwd=root, timeout=30)


def main() -> int:
    root = _git(["git", "rev-parse", "--show-toplevel"], ".").stdout.strip()
    if not root:
        note("could not locate the repo root — skipped")
        return 0
    unstaged = {ln.strip() for ln in _git(["git", "diff", "--name-only"], root).stdout.splitlines()}
    path = os.path.join(root, cs.CONTINUITY)
    if cs.CONTINUITY in unstaged:
        note(f"{cs.CONTINUITY} has unstaged edits — NOT regenerating")
    elif os.path.isfile(path):
        with open(path, encoding="utf-8", newline="") as fh:
            before = fh.read()
        after = cs.splice(before, cs.build_block(root))
        if after != before:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(after)
            note("status block regenerated — from the features")
        _git(["git", "add", "--", cs.CONTINUITY], root)
    try:
        f = cs._features(root)
        new = f.update_ratchet()
        _git(["git", "add", "--", RATCHET], root)
        if new:
            note(f"ratchet: {', '.join(new)} now required on every commit")
    except Exception as exc:  # noqa: BLE001
        note(f"ratchet not updated ({exc!r})")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — fail SOFT; rule 5 is the gate
        note(f"regeneration failed ({exc!r}) — commit proceeding; rule 5 guards")
        sys.exit(0)
