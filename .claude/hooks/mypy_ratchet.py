#!/usr/bin/env python3
"""The whole-tree type-error count: it may fall, never rise (founder, 2026-09-27).

Rule 3 type-checks only the files a commit changes, against a per-error
baseline. That let five errors sit unseen in files nobody touched after they
arrived (82b9251 fixed them when a change to config.py made the pre-flight
reach them). This counts EVERY error mypy reports over `backend` and `scripts`
of the STAGED tree, with the project's own `mypy.ini` and pinned venv, and
holds the count in `.claude/config/mypy-ratchet.json`:

  * the pre-commit hook runs `--lower`: when the count has fallen it writes the
    new count and stages the file, so an improvement is kept automatically;
  * the commit-msg guard (rule 3b) refuses a commit whose count is ABOVE the
    staged record, a staged record above HEAD's (the record raised by hand), or
    a count BELOW the record that was not lowered (the ratchet must track).

The count is a measurement, never a pass/fail of the code (CLAUDE.md: a bare
`mypy .` count is a measurement): it can only refuse a rise.

    python .claude/hooks/mypy_ratchet.py --count    # the staged tree's count
    python .claude/hooks/mypy_ratchet.py --lower    # lower the record if it fell

Python 3.11+, stdlib only.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = "agent-improve"
RATCHET = ".claude/config/mypy-ratchet.json"
PATHS = ("backend", "scripts")
CACHE_DIR = os.path.join(tempfile.gettempdir(), "agentlean-mypy-cache")
_ERROR = re.compile(r"^\S.*?:\d+: error: ", re.M)


def venv_python(root: Path = ROOT) -> str:
    for cand in (root / PROJECT / ".venv" / "Scripts" / "python.exe",
                 root / PROJECT / ".venv" / "bin" / "python"):
        if cand.exists():
            return str(cand)
    return sys.executable


def measure(tree_root: Path, py: str) -> int:
    """Every mypy error over PATHS of the project inside `tree_root` (a checkout)."""
    proj = tree_root / PROJECT
    os.makedirs(CACHE_DIR, exist_ok=True)
    out = subprocess.run(
        [py, "-m", "mypy", "--config-file", "mypy.ini", "--cache-dir", CACHE_DIR,
         "--no-error-summary", "--no-color-output", "--hide-error-context", *PATHS],
        cwd=proj, capture_output=True, encoding="utf-8", errors="replace", timeout=600,
        env=dict(os.environ, PYTHONIOENCODING="utf-8"), stdin=subprocess.DEVNULL)
    if out.returncode not in (0, 1):
        raise RuntimeError("mypy could not run: " + (out.stdout + out.stderr).strip()[:500])
    return len(_ERROR.findall(out.stdout + out.stderr))


def recorded(text: str) -> int:
    return int(json.loads(text)["count"])


def _git_show(root: Path, spec: str) -> str | None:
    r = subprocess.run(["git", "show", spec], cwd=root, capture_output=True, encoding="utf-8",
                       errors="replace", stdin=subprocess.DEVNULL)
    return r.stdout if r.returncode == 0 and r.stdout else None


def staged_record(root: Path = ROOT) -> int | None:
    t = _git_show(root, f":{RATCHET}")
    return recorded(t) if t else None


def head_record(root: Path = ROOT) -> int | None:
    t = _git_show(root, f"HEAD:{RATCHET}")
    return recorded(t) if t else None


def staged_count(root: Path = ROOT) -> int:
    sys.path.insert(0, str(root / ".claude" / "hooks"))
    import staged_tree
    return measure(staged_tree.sync(root), venv_python(root))


def write(root: Path, count: int) -> None:
    path = root / RATCHET
    data = json.loads(path.read_text(encoding="utf-8"))
    data["count"] = count
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                    newline="\n")


#: Controls review (founder, 2026-09-30): the pre-commit's count, keyed on the inputs it measured,
#: so rule 3b reuses it instead of running mypy over the whole tree a second time (~5 s a commit).
MARKER = Path(".claude") / "logs" / "mypy-count.json"


def source_key(root: Path = ROOT) -> str:
    """The count's inputs in the INDEX: every .py blob under backend/ and scripts/, and mypy.ini."""
    import hashlib
    out = subprocess.run(["git", "ls-files", "-s", "--", *(f"{PROJECT}/{p}" for p in PATHS), f"{PROJECT}/mypy.ini"],
                         cwd=root, capture_output=True, encoding="utf-8", errors="replace",
                         stdin=subprocess.DEVNULL).stdout
    lines = [ln for ln in out.splitlines() if ln.endswith(".py") or ln.endswith("mypy.ini")]
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()[:16]


def remember(root: Path, count: int) -> None:
    try:
        path = root / MARKER
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"key": source_key(root), "count": count}), encoding="utf-8")
    except OSError:
        pass


def known_count(root: Path = ROOT) -> int | None:
    """The pre-commit's count when the index still holds exactly what it measured; else None."""
    try:
        got = json.loads((root / MARKER).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return int(got["count"]) if got.get("key") == source_key(root) else None


def lower(root: Path = ROOT) -> str:
    """Pre-commit: lower and stage the record when the staged tree's count fell."""
    rec = staged_record(root)
    if rec is None:
        return "no ratchet record staged — nothing to lower"
    n = staged_count(root)
    remember(root, n)
    if n >= rec:
        return f"{n} error(s), record {rec} — unchanged"
    write(root, n)
    subprocess.run(["git", "add", RATCHET], cwd=root, check=True, stdin=subprocess.DEVNULL)
    return f"{n} error(s), record lowered from {rec} to {n} and staged"


def refusal(n: int, staged: int, head: int | None) -> list[str]:
    """Why rule 3b refuses, or [] — pure, so it is testable without mypy."""
    if head is not None and staged > head:
        return [f"the ratchet record was RAISED from {head} to {staged} in {RATCHET}.",
                "It may fall, never rise (founder, 2026-09-27): fix the new errors instead."]
    if n > staged:
        return [f"the whole-tree type-error count ROSE from {staged} to {n}",
                f"(mypy over {', '.join(PATHS)} of the STAGED tree, agent-improve/mypy.ini).",
                "It may fall, never rise: fix the new errors, wherever they are."]
    if n < staged:
        return [f"the count FELL from {staged} to {n} but the record was not lowered.",
                "The pre-commit hook lowers it; if hooks did not run, run",
                "  python .claude/hooks/mypy_ratchet.py --lower",
                "and commit again — the ratchet keeps every improvement."]
    return []


if __name__ == "__main__":
    if sys.argv[1:] == ["--count"]:
        print(staged_count())
    elif sys.argv[1:] == ["--lower"]:
        print(f"  [mypy ratchet] {lower()}", file=sys.stderr)
    else:
        print(__doc__)
        sys.exit(2)
