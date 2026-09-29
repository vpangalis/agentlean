"""The pre-push check, .claude/hooks/pre_push.py — founder ruling 4.3, 2026-09-29: a push
requires a passing full-suite run on the exact source being pushed."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]


def _mod():
    spec = importlib.util.spec_from_file_location("pre_push", _REPO / ".claude" / "hooks" / "pre_push.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_source_leaves_out_markdown_and_the_hooks_generated_outputs() -> None:
    p = _mod()
    assert p.counts("agent-improve/backend/core/graph.py")
    assert p.counts("agent-improve/skills/dmaic-define-phase/SKILL.md")      # the coach reads it
    assert p.counts("agent-improve/docs/runthrough/define_runthrough_20260929T113121.json")
    assert p.counts("agent-improve/docs/defects.json")
    assert not p.counts("agent-improve/docs/CONTINUITY.md")
    for generated in p.GENERATED:
        assert not p.counts(generated), generated


def test_a_push_needs_a_passing_full_run_on_each_pushed_source(tmp_path) -> None:
    p = _mod()
    ledger = tmp_path / "full-runs.jsonl"
    rows = [{"source": "aaa", "exit": 0}, {"source": "bbb", "exit": 0}, {"source": "bbb", "exit": 1},
            {"source": "ccc", "exit": 1}, {"source": "ccc", "exit": 0}]
    ledger.write_text("\n".join(json.dumps(r) for r in rows) + "\nnot json\n", encoding="utf-8")
    passed = p.passed_sources(ledger)
    assert passed == {"aaa", "ccc"}                        # the latest verdict on a source wins
    src = {"1" * 40: "aaa", "2" * 40: "bbb", "3" * 40: "zzz"}.get
    ok = [("refs/heads/main", "1" * 40, "refs/heads/main", "0" * 40)]
    assert p.refusals(ok, src, passed) == []
    bad = p.refusals([*ok, ("refs/heads/x", "2" * 40, "refs/heads/x", "0" * 40),
                      ("refs/heads/y", "3" * 40, "refs/heads/y", "0" * 40)], src, passed)
    assert len(bad) == 2 and "refs/heads/x" in bad[0] and "refs/heads/y" in bad[1]
    delete = [("(delete)", p.ZERO, "refs/heads/old", "4" * 40)]
    assert p.refusals(delete, src, passed) == []


def test_a_documentation_commit_keeps_its_parents_source(tmp_path) -> None:
    """The pre-commit hook's full run tests the index before it writes CONTINUITY and the board;
    the commit's source must equal the source that run recorded."""
    import subprocess

    def git(*a: str) -> str:
        return subprocess.run(["git", *a], cwd=tmp_path, capture_output=True, encoding="utf-8",
                              check=True).stdout.strip()
    git("init", "-q")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "notes.md").write_text("one\n", encoding="utf-8")
    git("add", "a.py", "notes.md")
    git("commit", "-qm", "one")
    p = _mod()
    first = p.source_id("HEAD", tmp_path)
    (tmp_path / "notes.md").write_text("two\n", encoding="utf-8")
    git("commit", "-qam", "docs")
    assert p.source_id("HEAD", tmp_path) == first
    (tmp_path / "a.py").write_text("x = 2\n", encoding="utf-8")
    git("commit", "-qam", "code")
    assert p.source_id("HEAD", tmp_path) != first
