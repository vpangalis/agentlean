#!/usr/bin/env python3
"""The substance counts: broad excepts (ruff BLE001) and over-complex functions (ruff C901) may fall, never rise
(founder ruling 2026-10-24, B4).

Counted over agent-improve/backend, tests excluded, of the STAGED tree, with the pinned venv's ruff and every
`# noqa` ignored — a marker hides a broad except from a reviewer, never from this count. C901 counts functions above
`max_complexity` (B10's target: 15). The record is `.claude/config/ruff-ratchet.json`:

  * the pre-commit hook runs `--lower`: when a count has fallen it writes the new count and stages the file;
  * the commit-msg guard (rule 25) refuses a count ABOVE the staged record, a staged record above HEAD's (raised by
    hand), or a count BELOW the record that was not lowered.

    python .claude/hooks/ruff_ratchet.py --count    # the staged tree's counts
    python .claude/hooks/ruff_ratchet.py --lower    # lower the record where a count fell

Python 3.11+, stdlib only; ruff runs as a subprocess of the pinned venv.
"""
from __future__ import annotations

import collections
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = "agent-improve"
RATCHET = ".claude/config/ruff-ratchet.json"
CODES = ("BLE001", "C901")


def venv_python(root: Path = ROOT) -> str:
    for cand in (root / PROJECT / ".venv" / "Scripts" / "python.exe", root / PROJECT / ".venv" / "bin" / "python"):
        if cand.exists():
            return str(cand)
    return sys.executable


def _record_text(root: Path, spec: str | None) -> str | None:
    if spec is None:
        path = root / RATCHET
        return path.read_text(encoding="utf-8") if path.is_file() else None
    r = subprocess.run(["git", "show", spec], cwd=root, capture_output=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL)
    return r.stdout if r.returncode == 0 and r.stdout else None


def max_complexity(root: Path = ROOT) -> int:
    text = _record_text(root, None)
    return int(json.loads(text)["max_complexity"]) if text else 15


def measure(tree_root: Path, py: str, complexity: int) -> dict[str, int]:
    """BLE001 and C901 over the project's backend inside `tree_root` (a checkout), `# noqa` ignored."""
    proj = tree_root / PROJECT
    out = subprocess.run(
        [py, "-m", "ruff", "check", "backend", "--exclude", "backend/tests", "--select", ",".join(CODES),
         "--config", f"lint.mccabe.max-complexity={complexity}", "--ignore-noqa", "--no-cache",
         "--output-format", "json", "--exit-zero"],
        cwd=proj, capture_output=True, encoding="utf-8", errors="replace", timeout=300,
        env=dict(os.environ, PYTHONIOENCODING="utf-8"), stdin=subprocess.DEVNULL)
    if out.returncode != 0:
        raise RuntimeError("ruff could not run: " + (out.stdout + out.stderr).strip()[:500])
    found = collections.Counter(item["code"] for item in json.loads(out.stdout or "[]"))
    return {code: int(found.get(code, 0)) for code in CODES}


def recorded(text: str) -> dict[str, int]:
    data = json.loads(text)
    return {code: int(data[code]) for code in CODES}


def staged_record(root: Path = ROOT) -> dict[str, int] | None:
    t = _record_text(root, f":{RATCHET}")
    return recorded(t) if t else None


def head_record(root: Path = ROOT) -> dict[str, int] | None:
    t = _record_text(root, f"HEAD:{RATCHET}")
    return recorded(t) if t else None


def staged_count(root: Path = ROOT) -> dict[str, int]:
    sys.path.insert(0, str(root / ".claude" / "hooks"))
    import staged_tree
    return measure(staged_tree.sync(root), venv_python(root), max_complexity(root))


def write(root: Path, counts: dict[str, int]) -> None:
    path = root / RATCHET
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(counts)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def lower(root: Path = ROOT) -> str:
    """Pre-commit: lower and stage the record where a staged count fell."""
    rec = staged_record(root)
    if rec is None:
        return "no ruff ratchet record staged — nothing to lower"
    n = staged_count(root)
    fell = {code: n[code] for code in CODES if n[code] < rec[code]}
    if not fell:
        return f"{n}, record {rec} — unchanged"
    write(root, fell)
    subprocess.run(["git", "add", RATCHET], cwd=root, check=True, stdin=subprocess.DEVNULL)
    return f"{n}, record lowered to {dict(rec, **fell)} and staged"


def refusal(n: dict[str, int], staged: dict[str, int], head: dict[str, int] | None) -> list[str]:
    """Why rule 25 refuses, or [] — pure, so it is testable without ruff."""
    out: list[str] = []
    for code in CODES:
        if head is not None and staged[code] > head[code]:
            out.append(f"{code}: the record was RAISED from {head[code]} to {staged[code]} in {RATCHET} — it may "
                       "fall, never rise; fix the new findings instead.")
        if n[code] > staged[code]:
            out.append(f"{code}: {n[code]} finding(s) in the staged tree, the record is {staged[code]} — a new "
                       f"{'broad except' if code == 'BLE001' else 'over-complex function'} (run: ruff check backend "
                       f"--select {code} --ignore-noqa).")
        elif n[code] < staged[code]:
            out.append(f"{code}: {n[code]} finding(s), the record is {staged[code]} — the record did not follow the "
                       "fall (the pre-commit hook lowers it: python .claude/hooks/ruff_ratchet.py --lower).")
    return out


def main(argv: list[str]) -> int:
    if "--count" in argv:
        print(staged_count(ROOT))
        return 0
    if "--lower" in argv:
        print(lower(ROOT))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
