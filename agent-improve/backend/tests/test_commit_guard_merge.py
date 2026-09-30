"""Founder ruling 4, 2026-09-30 — the commit guard checks a merge commit into main: rule 11's
landing for every feature it names, the 11b ratchet and rule 10's board. Until then every merge
returned unchecked (25b91f7 landed DEF-079 that way, checked by hand after the push)."""
from __future__ import annotations

from pathlib import Path

import pytest

from backend.tests.test_define_features import _git, _guard, _repo, no_git_env  # noqa: F401 — the fixture

_REPO = Path(__file__).resolve().parents[3]


def _on(repo: Path, branch: str) -> None:
    _git(repo, "branch", "-M", branch)


def _quiet(guard, monkeypatch) -> list[str]:
    ran: list[str] = []
    monkeypatch.setattr(guard, "check_ratchet", lambda root: ran.append("11b"))
    monkeypatch.setattr(guard, "check_board", lambda root, py: ran.append("10"))
    monkeypatch.setattr(guard, "venv_python", lambda root: "python")
    return ran


def test_a_merge_into_main_lands_only_the_features_that_pass(tmp_path, no_git_env, monkeypatch) -> None:
    repo = _repo(tmp_path, "skipped")
    _on(repo, "main")
    guard = _guard()
    _quiet(guard, monkeypatch)
    with pytest.raises(SystemExit):
        guard.check_merge(str(repo), "Merge branch 'x'", "Merge branch 'x'\n\nFeature: DEF-900\n")


def test_a_merge_into_main_runs_the_landing_the_ratchet_and_the_board(tmp_path, no_git_env, monkeypatch) -> None:
    repo = _repo(tmp_path, "passed")
    _on(repo, "main")
    guard = _guard()
    ran = _quiet(guard, monkeypatch)
    subject = "refactor(arch-v2): DEF-900 — the thing works (merge of x)"
    assert guard.check_merge(str(repo), subject, subject + "\n") == 0
    assert ran == ["11b", "10"]


def test_a_merge_into_another_branch_is_left_for_main(tmp_path, no_git_env, monkeypatch) -> None:
    repo = _repo(tmp_path, "skipped")
    _on(repo, "m1/work")
    guard = _guard()
    ran = _quiet(guard, monkeypatch)
    assert guard.check_merge(str(repo), "Merge branch 'y'", "Merge branch 'y'\n\nFeature: DEF-900\n") == 0
    assert ran == []


def test_main_routes_a_merge_to_the_merge_checks_and_git_runs_pre_commit_for_it() -> None:
    src = (_REPO / ".claude" / "hooks" / "commit-msg-refactor-guard.py").read_text(encoding="utf-8")
    at = src.index('"MERGE_HEAD"')
    assert "return check_merge(root, subject, message)" in src[at:at + 200]
    hook = (_REPO / ".githooks" / "pre-merge-commit").read_text(encoding="utf-8")
    assert "exec sh .githooks/pre-commit" in hook
