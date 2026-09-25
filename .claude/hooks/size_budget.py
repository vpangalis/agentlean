#!/usr/bin/env python3
"""The size budget — rule 12 of the commit-msg guard. Step 6.66 (founder ruling 2026-09-25).

CLAUDE.md §22 (h): REPLACE, DON'T APPEND. The governing documents grew every
step because every step added and none replaced; the overnight run moved their
history to `docs/_archive/`, and this keeps them from growing back. Each
budgeted file has a bound in `.claude/config/size-budget.json` — its size after
slimming plus 10%, in characters of the STAGED blob (LF line endings):

    below 90% of the bound   pass
    90% to 100%              pass, with a warning naming the headroom left
    over 100%                REFUSED — replace text, or move history to the archive

Only files STAGED in the commit are measured. Raising a bound is a deliberate
act in the budget file, in its own commit, with the reason in the body.

    python .claude/hooks/size_budget.py            # report every budgeted file (working tree)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUDGET = ROOT / ".claude" / "config" / "size-budget.json"
WARN_AT = 0.90


def load(path: Path = BUDGET) -> dict[str, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: int(v) for k, v in data["bounds"].items()}


def measure(text: str) -> int:
    return len(text.replace("\r\n", "\n"))


def verdicts(sizes: dict[str, int], bounds: dict[str, int]) -> list[tuple[str, str, int, int]]:
    """(level, path, size, bound) for each measured file with a bound; level is ok|warn|over."""
    out = []
    for path, size in sorted(sizes.items()):
        bound = bounds.get(path)
        if bound is None:
            continue
        level = "over" if size > bound else "warn" if size >= WARN_AT * bound else "ok"
        out.append((level, path, size, bound))
    return out


def staged_sizes(root: Path, staged: list[str], bounds: dict[str, int]) -> dict[str, int]:
    sizes = {}
    for path in staged:
        if path not in bounds:
            continue
        blob = subprocess.run(["git", "show", f":{path}"], cwd=root, capture_output=True,
                              encoding="utf-8", errors="replace", timeout=30)
        if blob.returncode == 0:
            sizes[path] = measure(blob.stdout)
    return sizes


def message(level: str, path: str, size: int, bound: int) -> str:
    pct = 100 * size / bound
    if level == "over":
        return (f"{path}: {size:,} chars, bound {bound:,} ({pct:.0f}%) — over by {size - bound:,}. "
                "REPLACE, DON'T APPEND: change statements in place and move history to docs/_archive/.")
    return f"{path}: {size:,} of {bound:,} chars ({pct:.0f}%) — {bound - size:,} left before the budget refuses"


def main() -> int:
    bounds = load()
    sizes = {p: measure((ROOT / p).read_text(encoding="utf-8")) for p in bounds if (ROOT / p).is_file()}
    for level, path, size, bound in verdicts(sizes, bounds):
        print(f"{level:4} {message(level, path, size, bound)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
