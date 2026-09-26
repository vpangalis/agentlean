"""The hooks test what is STAGED — founder ruling 2026-09-26 on the 6.67 report (step 6.68).

`.claude/hooks/staged_tree.py` keeps a second worktree set to HEAD + the index
tree. Proven on a throwaway repository: the staged content is what the second
worktree holds, never the unstaged edit; HEAD is the checkout's HEAD; a later
sync drops a file the index no longer carries; the checkout is not touched.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_HOOKS = _REPO / ".claude" / "hooks"


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, _HOOKS / file)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


st = _load("staged_tree_under_test", "staged_tree.py")


def _git(repo: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                          encoding="utf-8", env=env).stdout.strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A checkout with a committed, a staged and an unstaged version of one file."""
    for k in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(k)
    r = tmp_path / "checkout"
    (r / "agent-improve").mkdir(parents=True)
    _git(r, "init", "-q")
    _git(r, "config", "user.email", "t@example.com")
    _git(r, "config", "user.name", "t")
    f = r / "agent-improve" / "a.txt"
    f.write_text("committed", encoding="utf-8")
    (r / "agent-improve" / "gone.txt").write_text("x", encoding="utf-8")
    _git(r, "add", ".")
    _git(r, "commit", "-qm", "c1")
    f.write_text("staged", encoding="utf-8")
    _git(r, "add", "agent-improve/a.txt")
    f.write_text("unstaged", encoding="utf-8")
    yield r
    wt = st.location(r)
    subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=r, capture_output=True)
    shutil.rmtree(wt, ignore_errors=True)


def test_the_second_worktree_holds_the_STAGED_content_and_HEAD(repo) -> None:
    wt = st.sync(repo)
    assert (wt / "agent-improve" / "a.txt").read_text(encoding="utf-8") == "staged"
    assert _git(wt, "rev-parse", "HEAD") == _git(repo, "rev-parse", "HEAD")
    assert _git(wt, "diff", "--name-only") == ""             # its files == its index
    assert _git(wt, "diff", "--cached", "--name-only") == "agent-improve/a.txt"   # index != HEAD
    assert (repo / "agent-improve" / "a.txt").read_text(encoding="utf-8") == "unstaged"


def test_a_later_sync_follows_the_index_and_drops_what_it_no_longer_carries(repo) -> None:
    st.sync(repo)
    _git(repo, "rm", "-q", "--cached", "agent-improve/gone.txt")
    wt = st.sync(repo)
    assert not (wt / "agent-improve" / "gone.txt").exists()
    assert (repo / "agent-improve" / "gone.txt").exists()    # the checkout is untouched


def test_the_hook_scoped_git_variables_are_stripped(monkeypatch) -> None:
    monkeypatch.setenv("GIT_INDEX_FILE", "/elsewhere/index")
    assert "GIT_INDEX_FILE" not in st.clean_env()
