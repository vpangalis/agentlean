#!/usr/bin/env python3
"""The hooks test what is STAGED — founder ruling 2026-09-26 on the 6.67 report.

Until 6.68 every check ran in the working tree, so a commit that left an edit
unstaged was tested on a tree it did not contain (`796ced5` shipped half-staged
that way). This keeps ONE detached linked worktree per checkout, outside
OneDrive, and sets it to exactly what the commit will contain:

    HEAD      the checkout's HEAD commit      (history reads: `git show HEAD:…`)
    index     the checkout's index tree        (index reads: `git show :…`)
    files     that same tree, and nothing else  (`git clean` removes strays)

plus the two ignored inputs the suite needs: a junction to the pinned venv and
a copy of `agent-improve/.env`. The developer's working tree is never touched —
no stash, no checkout — which is why this is a second worktree and not the
classic stash-and-restore.

The inherited GIT_* variables are stripped before touching the second worktree:
inside a hook, GIT_INDEX_FILE names the index being committed, and a
`read-tree` with it set would write into that index.

    python .claude/hooks/staged_tree.py          # sync, print the synced agent-improve path
    python .claude/hooks/staged_tree.py --suite  # sync, run the full suite there (the hook's run)
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = "agent-improve"
#: Where the logs of a run in the staged tree go — the checkout's own, so the
#: timing log and the slow-test list are not lost with the second worktree.
LOGS_ENV = "AGENTLEAN_LOGS"


def clean_env(**extra: str) -> dict[str, str]:
    """os.environ without the hook-scoped GIT_* variables."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(extra)
    return env


def _git(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, encoding="utf-8",
                       errors="replace", timeout=120, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def location(root: Path = ROOT) -> Path:
    """One staged worktree per checkout (main and each lane get their own)."""
    key = hashlib.sha1(str(root.resolve()).lower().encode()).hexdigest()[:10]
    return Path(tempfile.gettempdir()) / "agentlean-staged" / key


def index_tree(root: Path = ROOT) -> str:
    """The tree the commit will contain — read WITH the inherited env, so a
    hook's GIT_INDEX_FILE (a `--only` or `-a` commit) is the index read."""
    return _git(["write-tree"], root, env=dict(os.environ))


def _link_venv(wt: Path, root: Path) -> None:
    target = root / PROJECT / ".venv"
    link = wt / PROJECT / ".venv"
    if link.exists() or not target.exists():
        return
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                       capture_output=True, timeout=30)
    else:
        link.symlink_to(target, target_is_directory=True)


def venv_python(root: Path = ROOT) -> str:
    for rel in ("Scripts/python.exe", "bin/python"):
        p = root / PROJECT / ".venv" / rel
        if p.is_file():
            return str(p)
    raise RuntimeError("the pinned venv agent-improve/.venv is missing")


def sync(root: Path = ROOT, tree: str | None = None) -> Path:
    """Set the staged worktree to HEAD + `tree` (default: the index tree); return its root."""
    tree = tree or index_tree(root)
    env = clean_env()
    head = _git(["rev-parse", "HEAD"], root, env)
    wt = location(root)
    if not (wt / ".git").exists():
        if wt.exists():
            shutil.rmtree(wt, ignore_errors=True)
        wt.parent.mkdir(parents=True, exist_ok=True)
        _git(["worktree", "prune"], root, env)
        _git(["worktree", "add", "--detach", "--force", str(wt), head], root, env)
    else:
        _git(["update-ref", "--no-deref", "HEAD", head], wt, env)
    _git(["read-tree", "--reset", "-u", tree], wt, env)
    # Strays a previous tree left (never the ignored inputs: .env, the venv junction).
    _git(["clean", "-fdq"], wt, env)
    _link_venv(wt, root)
    src_env = root / PROJECT / ".env"
    if src_env.is_file():
        shutil.copyfile(src_env, wt / PROJECT / ".env")
    return wt


def run(cmd: list[str], wt: Path, root: Path = ROOT, timeout: int = 900,
        **extra: str) -> subprocess.CompletedProcess:
    """Run `cmd` in the staged worktree's agent-improve/, with a clean git env
    and the checkout's log directory."""
    env = clean_env(PYTHONIOENCODING="utf-8", **{LOGS_ENV: str(root / ".claude" / "logs")}, **extra)
    return subprocess.run(cmd, cwd=wt / PROJECT, capture_output=True, encoding="utf-8",
                          errors="replace", timeout=timeout, env=env)


def run_suite(root: Path = ROOT) -> tuple[int, str]:
    """THE commit's one full run, on the staged tree. The recorder writes its
    record inside the staged worktree; it is copied back to the checkout,
    where the board, the ratchet and rule 11 read it and the hook stages it."""
    wt = sync(root)
    r = run([venv_python(root), "-m", "pytest", "backend/tests", "-q", "--no-header",
             "-p", "no:cacheprovider", "-n", "auto"], wt, root, AGENT_IMPROVE_FULL_RUN="1")
    record = wt / PROJECT / "docs" / "test-results.json"
    if record.is_file():
        shutil.copyfile(record, root / PROJECT / "docs" / "test-results.json")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


if __name__ == "__main__":
    if "--suite" in sys.argv:
        code, out = run_suite()
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        print(out)
        sys.exit(code)
    print(sync() / PROJECT)
    sys.exit(0)
