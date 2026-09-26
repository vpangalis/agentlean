"""The documents stop growing — step 6.66 (founder ruling 2026-09-25).

Rule 12 of the commit-msg guard (CLAUDE.md §22 h, REPLACE, DON'T APPEND) and
the generated section index (§22 b). The budget is proven both ways: a staged
document over its bound is REFUSED, one inside it passes, one above base + 5%
passes with a warning, an unbudgeted file is never measured.
"""
from __future__ import annotations

import importlib.util
import json
import os
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


sb = _load("size_budget", "size_budget.py")


def test_over_base_plus_10_is_refused_above_base_plus_5_it_warns() -> None:
    """Founder ruling 2026-09-26: the bound is base + 10% (refused above it);
    the warning starts above base + 5%. Base 1000 -> bound 1100."""
    bounds = {"a.md": 1100, "b.md": 1100, "c.md": 1100, "d.md": 1100}
    got = {p: lvl for lvl, p, _, _ in sb.verdicts(
        {"a.md": 1101, "b.md": 1040, "c.md": 1060, "d.md": 1100}, bounds)}
    assert got == {"a.md": "over", "b.md": "ok", "c.md": "warn", "d.md": "warn"}


def test_an_unbudgeted_file_is_never_measured() -> None:
    assert sb.verdicts({"notes.md": 10**9}, {"a.md": 1}) == []


def test_line_endings_do_not_count() -> None:
    assert sb.measure("a\r\nb\r\n") == sb.measure("a\nb\n") == 4


def test_every_governing_document_has_a_bound() -> None:
    bounds = sb.load()
    must = {"agent-improve/CLAUDE.md", "agent-improve/ARCHITECTURE.md"}   # the procedure is archived (6.67)
    must |= {p.relative_to(_REPO).as_posix() for p in (_REPO / ".claude" / "rules").glob("*.md")}
    assert must <= set(bounds), sorted(must - set(bounds))


@pytest.fixture
def no_git_env(monkeypatch):
    """Inside a commit hook git exports GIT_INDEX_FILE (and, under --only, a
    temporary index). A throwaway repo's `git add` would write into THE
    COMMIT'S index — found on this file's first run inside the hook."""
    for k in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(k)


def _git(repo: Path, *args: str) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)


def _repo_with(tmp_path: Path, size: int, bound: int) -> Path:
    repo = tmp_path / "r"
    (repo / ".claude" / "config").mkdir(parents=True)
    (repo / ".claude" / "config" / "size-budget.json").write_text(
        json.dumps({"bounds": {"doc.md": bound}}), encoding="utf-8")
    (repo / "doc.md").write_text("x" * size, encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "add", "doc.md")
    return repo


def test_the_guard_refuses_a_staged_document_over_its_bound(tmp_path, no_git_env) -> None:
    guard = _load("guard_rule12", "commit-msg-refactor-guard.py")
    repo = _repo_with(tmp_path, size=1200, bound=1000)
    (repo / ".claude" / "hooks").mkdir()
    (repo / ".claude" / "hooks" / "size_budget.py").write_text(
        (_HOOKS / "size_budget.py").read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(SystemExit):
        guard.check_size(str(repo), ["doc.md"])


def test_the_guard_passes_a_staged_document_inside_its_bound(tmp_path, no_git_env) -> None:
    guard = _load("guard_rule12b", "commit-msg-refactor-guard.py")
    repo = _repo_with(tmp_path, size=500, bound=1000)
    (repo / ".claude" / "hooks").mkdir()
    (repo / ".claude" / "hooks" / "size_budget.py").write_text(
        (_HOOKS / "size_budget.py").read_text(encoding="utf-8"), encoding="utf-8")
    guard.check_size(str(repo), ["doc.md"])      # no SystemExit


def test_the_section_index_gives_each_heading_its_range_and_skips_code() -> None:
    si = _load("section_index", "section_index.py")
    text = "# A\nx\n## A.1\ny\n```\n# not a heading\n```\n## A.2\nz\n# B\n"
    got = [(lvl, a, b, t) for lvl, a, b, t in si.sections(text)]
    assert got == [(1, 1, 9, "A"), (2, 3, 7, "A.1"), (2, 8, 9, "A.2"), (1, 10, 10, "B")]


# ── rule 13 — the docs checks a docs-only commit runs instead of the suite (6.67) ──


def _docs_root(tmp_path, link: str) -> Path:
    root = tmp_path / "d"
    (root / ".claude" / "hooks").mkdir(parents=True)
    (root / ".claude" / "hooks" / "check_links.py").write_text(
        (_HOOKS / "check_links.py").read_text(encoding="utf-8"), encoding="utf-8")
    (root / "docs").mkdir()
    (root / "docs" / "there.md").write_text("x", encoding="utf-8")
    (root / "docs" / "note.md").write_text(f"see [it]({link})\n", encoding="utf-8")
    return root


def test_rule_13_refuses_a_staged_document_with_a_broken_link(tmp_path) -> None:
    guard = _load("guard_rule13", "commit-msg-refactor-guard.py")
    with pytest.raises(SystemExit):
        guard.check_docs(str(_docs_root(tmp_path, "gone.md")), ["docs/note.md"])


def test_rule_13_passes_a_staged_document_whose_links_resolve(tmp_path) -> None:
    guard = _load("guard_rule13b", "commit-msg-refactor-guard.py")
    guard.check_docs(str(_docs_root(tmp_path, "there.md#a-section")), ["docs/note.md"])
