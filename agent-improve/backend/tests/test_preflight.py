"""The pre-flight — step 6.66 (founder ruling 2026-09-25).

A commit is never refused for a knock-on effect: the pre-flight checks what a
change REACHES (its importers, the tests of both, the tests that name a changed
document) and the PreToolUse hook runs it before every `git commit`. Proven
both ways: it selects the knock-on and blocks on a failure; it lets a clean
commit and every other command through.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_HOOKS = _REPO / ".claude" / "hooks"


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, _HOOKS / file)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _pf():
    return _load("preflight", "preflight.py")


def _hook():
    return _load("preflight_on_commit", "preflight-on-commit.py")


def test_a_changed_module_type_checks_its_importers_and_runs_its_own_tests() -> None:
    """6.67 (addendum, speed item 2): changed files and their importers ONLY —
    the importers are type-checked; the tests run are the changed module's own.
    The commit hook's full run covers everything else."""
    pf = _pf()
    graph = {
        "backend.a": set(),
        "backend.b": {"backend.a"},                  # imports a — type-checked
        "backend.c": set(),
        "backend.tests.test_a": {"backend.a"},       # tests a directly — RUN
        "backend.tests.test_moves": {"backend.b"},   # tests b, the importer — left to the hook
        "backend.tests.test_state": {"backend.c"},   # unrelated — NOT run
    }
    p = pf.plan(["agent-improve/backend/a.py"], graph)
    assert p["importers"] == ["backend.b", "backend.tests.test_a"]   # both type-checked
    assert "agent-improve/backend/tests/test_moves.py" not in p["tests"]
    assert "agent-improve/backend/tests/test_state.py" not in p["tests"]


def test_a_slow_test_is_left_to_the_hook(monkeypatch) -> None:
    pf = _pf()
    monkeypatch.setattr(pf, "slow_tests", lambda: ["backend/tests/test_x.py::test_slow"])
    seen = {}

    def fake_run(cmd, cwd):
        seen["cmd"] = cmd
        return 0, "1 passed"
    monkeypatch.setattr(pf, "_run", fake_run)
    ok, msg = pf.check_tests("py", {"tests": ["agent-improve/backend/tests/test_x.py"]})
    assert ok and "--deselect" in seen["cmd"] and "backend/tests/test_x.py::test_slow" in seen["cmd"]
    assert "1 slow test(s) left to the hook" in msg


def test_a_changed_document_reaches_the_tests_that_read_it() -> None:
    """6.61's first commit was refused for a stale count in a document."""
    p = _pf().plan(["agent-improve/ARCHITECTURE.md"], graph={})
    assert "agent-improve/backend/tests/test_state.py" in p["tests"]  # it reads ARCHITECTURE.md by name


def test_the_conftest_reaches_everything() -> None:
    assert _pf().plan(["agent-improve/backend/tests/conftest.py"], graph={})["tests"] == "ALL"


def test_relative_imports_resolve(tmp_path) -> None:
    pkg = tmp_path / "phases"
    pkg.mkdir()
    f = pkg / "nodes.py"
    f.write_text("from . import moves\nfrom ..core.state import PhaseState\n", encoding="utf-8")
    got = _pf()._imports(f, "backend.phases.nodes")
    assert "backend.phases.moves" in got and "backend.core.state" in got


def test_the_hook_blocks_a_commit_when_the_preflight_fails() -> None:
    def failing(echo):
        echo("  !! tests  stale count")
        return 1
    code, msg = _hook().decide({"tool_name": "Bash", "tool_input": {"command": "git commit -F m.txt"}}, failing)
    assert code == 2 and "PRE-FLIGHT FAILED" in msg and "stale count" in msg


def test_the_hook_lets_a_clean_commit_through() -> None:
    code, _ = _hook().decide({"tool_name": "Bash", "tool_input": {"command": "git add x && git commit -F m.txt"}},
                             lambda echo: 0)
    assert code == 0


def test_the_hook_ignores_every_other_command() -> None:
    def never(echo):
        raise AssertionError("the pre-flight must not run for a non-commit command")
    h = _hook()
    for cmd in ("git status", "git log --oneline", "pytest -q", "git commit --dry-run", "echo git committee"):
        assert h.decide({"tool_name": "Bash", "tool_input": {"command": cmd}}, never)[0] == 0, cmd
    assert h.decide({"tool_name": "Edit", "tool_input": {}}, never)[0] == 0


def test_an_acknowledged_failure_passes_on_the_record() -> None:
    cmd = "git commit -F m.txt   # preflight: acknowledged — fails identically at HEAD 669b39c"
    code, msg = _hook().decide({"tool_name": "PowerShell", "tool_input": {"command": cmd}}, lambda echo: 1)
    assert code == 0 and "ACKNOWLEDGED" in msg


def test_a_short_acknowledgement_does_not_pass() -> None:
    cmd = "git commit -F m.txt   # preflight: acknowledged — ok"
    assert _hook().decide({"tool_name": "Bash", "tool_input": {"command": cmd}}, lambda echo: 1)[0] == 2


def test_the_whole_suite_is_left_to_the_hook(monkeypatch) -> None:
    """6.67: when a change reaches everything (conftest), the hook's one full
    run is that check — the pre-flight runs nothing rather than a second suite."""
    pf = _pf()
    monkeypatch.setattr(pf, "_run", lambda cmd, cwd: (_ for _ in ()).throw(AssertionError("ran")))
    ok, msg = pf.check_tests("py", {"tests": "ALL"})
    assert ok and "left to the commit hook" in msg
