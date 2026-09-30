"""Controls review proposal, accepted 2026-09-30: rule 3b reuses the pre-commit hook's whole-tree
mypy count when the index still holds exactly the sources it measured (it ran mypy twice per commit)."""
from __future__ import annotations

import importlib.util
import os
import subprocess
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]


def _mr():
    spec = importlib.util.spec_from_file_location("mypy_ratchet", _REPO / ".claude" / "hooks" / "mypy_ratchet.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(repo: Path, *a: str) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True, env=env)


def test_the_count_is_reused_until_a_python_source_in_the_index_changes(tmp_path, monkeypatch) -> None:
    for k in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(k)
    mr = _mr()
    src = tmp_path / "agent-improve" / "backend"
    src.mkdir(parents=True)
    (src / "a.py").write_text("x = 1\n", encoding="utf-8")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "-A")
    assert mr.known_count(tmp_path) is None
    mr.remember(tmp_path, 67)
    assert mr.known_count(tmp_path) == 67
    (tmp_path / "agent-improve" / "notes.md").write_text("docs\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    assert mr.known_count(tmp_path) == 67, "a non-Python change keeps the count"
    (src / "a.py").write_text("x: int = 'no'\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    assert mr.known_count(tmp_path) is None, "a staged Python change is measured again"
