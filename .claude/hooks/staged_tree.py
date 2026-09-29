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
    python .claude/hooks/staged_tree.py --suite-at <rev>  # the full suite on a commit's tree (pre-push)
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


def run_suite(root: Path = ROOT, tree: str | None = None) -> tuple[int, str]:
    """THE commit's one full run, on the staged tree. The recorder writes its
    record inside the staged worktree; it is copied back to the checkout,
    where the board, the ratchet and rule 11 read it and the hook stages it.

    Founder ruling 4.3, 2026-09-29: the verdict also goes to the pre-push ledger
    (`pre_push.record`). `tree` is `--suite-at`'s: a commit's tree, whose record is
    not copied back — the checkout's record belongs to its own index."""
    copy_back = tree is None
    tree = tree or index_tree(root)
    wt = sync(root, tree)
    base = [venv_python(root), "-m", "pytest", "backend/tests", "-q", "--no-header",
            "-p", "no:cacheprovider"]
    # Two passes (founder, 2026-09-27): everything but `serial` in parallel, then
    # the `serial` tests alone — a test timing the event loop cannot share the
    # machine. Both runs are on the same source, so the recorder MERGES them into
    # one record. Exit 5 is "no test selected", not a failure.
    # `wallclock` tests are the run-through stage's (founder ruling 4, 2026-09-28; G-127).
    par = run([*base, "-n", "auto", "-m", "not serial and not wallclock"], wt, root, AGENT_IMPROVE_FULL_RUN="1")
    ser = run([*base, "-n", "0", "-m", "serial and not wallclock"], wt, root, AGENT_IMPROVE_FULL_RUN="1")
    record = wt / PROJECT / "docs" / "test-results.json"
    if copy_back and record.is_file():
        shutil.copyfile(record, root / PROJECT / "docs" / "test-results.json")
    codes = [c for c in (par.returncode, ser.returncode) if c not in (0, 5)]

    def last(r: subprocess.CompletedProcess) -> str:
        return next((ln for ln in reversed(((r.stdout or "") + (r.stderr or "")).splitlines())
                     if ln.strip()), "").strip()
    out = ((par.stdout or "") + (par.stderr or "") + (ser.stdout or "") + (ser.stderr or "")
           + "\n" + f"parallel: {last(par)} | serial: {last(ser)}" + "\n")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import pre_push
    pre_push.record(tree, codes[0] if codes else 0, f"parallel: {last(par)} | serial: {last(ser)}", root)
    return (codes[0] if codes else 0), out


#: Founder item 9, 2026-09-29 — test files a fast run always includes: they read the live
#: run-through record, whose freshness any product change alters, whatever the import graph says.
ALWAYS_FAST = ("backend/tests/test_define_runthrough.py", "backend/tests/test_define_features.py")


def fast_tests(root: Path = ROOT) -> list[str] | None:
    """The test files the STAGED change reaches (the pre-flight's import-graph plan) plus
    ALWAYS_FAST, relative to agent-improve/; None when the change reaches everything."""
    sys.path.insert(0, str(root / ".claude" / "hooks"))
    import preflight
    changed = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=root, capture_output=True,
                             encoding="utf-8").stdout.split()
    p = preflight.plan(changed)
    if p["tests"] == "ALL":
        return None
    rel = {t[len(PROJECT) + 1:] for t in p["tests"]} | set(ALWAYS_FAST)
    return sorted(r for r in rel if (root / PROJECT / r).is_file())


def run_fast(root: Path = ROOT) -> tuple[int, str]:
    """Founder item 9, 2026-09-29: a commit's FAST run, on the staged tree — the tests its change
    reaches. The recorder (AGENT_IMPROVE_FAST_RUN=1) carries every other test's outcome forward
    from the last record instead of discarding it: a test the change does not reach through
    imports has the outcome it had. The full suite still runs once per package, before the
    package's last commit (AGENT_IMPROVE_FULL_SUITE=1), and must pass there."""
    tests = fast_tests(root)
    if tests is None:
        return run_suite(root)
    wt = sync(root)
    base = [venv_python(root), "-m", "pytest", *tests, "-q", "--no-header", "-p", "no:cacheprovider",
            "-m", "not wallclock", "-n", "auto" if len(tests) > 12 else "0"]
    r = run(base, wt, root, AGENT_IMPROVE_FAST_RUN="1")
    record = wt / PROJECT / "docs" / "test-results.json"
    if record.is_file():
        shutil.copyfile(record, root / PROJECT / "docs" / "test-results.json")
    text = (r.stdout or "") + (r.stderr or "")
    last = next((ln for ln in reversed(text.splitlines()) if ln.strip()), "").strip()
    code = 0 if r.returncode in (0, 5) else r.returncode
    return code, text + chr(10) + f"fast ({len(tests)} test files): {last}" + chr(10)


if __name__ == "__main__":
    if "--fast" in sys.argv:
        code, out = run_fast()
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        print(out)
        sys.exit(code)
    if "--suite-at" in sys.argv:
        rev = sys.argv[sys.argv.index("--suite-at") + 1]
        code, out = run_suite(tree=_git(["rev-parse", f"{rev}^{{tree}}"], ROOT, clean_env()))
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        print(out)
        sys.exit(code)
    if "--suite" in sys.argv:
        code, out = run_suite()
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        print(out)
        sys.exit(code)
    print(sync() / PROJECT)
    sys.exit(0)
