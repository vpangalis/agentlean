"""Package P0 — the commit hook and the tooling (founder ruling 2026-10-20: P0 runs before P1; requirement T97).

One test per P0 feature, each the proof of a tooling defect: G-177/G-230 (DEF-232), G-229 (DEF-233), G-231
(DEF-234), G-233 (DEF-235).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "agent-improve"
HOOKS = ROOT / ".claude" / "hooks"

#: A feature test's outcome is the measurement (as in test_define_e2e.py): failing, it reads xfail.
pytestmark = pytest.mark.xfail(strict=False, reason="a Define feature test — its outcome is the measurement")


def test_the_commit_hook_regenerates_the_generated_documents_before_it_runs_the_tests() -> None:
    """DEF-232 — G-177 / G-230: the pre-commit hook runs every generator the tests check (the data models, the code
    layout, the routes, the value keys, the middleware order) and stages their output BEFORE it runs the tests on
    the staged tree, so a commit that changes a generated source never fails its own first run."""
    hook = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    tests_at = hook.index('staged_tree.py $RUNFLAG')
    for generator in ("generate_models.py", "generate_layout generate_routes generate_value_keys "
                                            "generate_middleware_order"):
        assert generator in hook, generator
        assert hook.index(generator) < tests_at, f"{generator} runs after the tests"


def test_a_hook_whose_dependency_is_missing_refuses_with_the_reason(tmp_path) -> None:
    """DEF-233 — G-229: a Claude Code guard whose dependency (pyyaml) cannot be imported refuses the tool call —
    exit 2, the reason on stderr — instead of exiting 0 and letting every write through unchecked. Both guards.
    (One test, not parametrized: the feature names this node id, and rule 11 reads its outcome.)"""
    fake = tmp_path / "yaml"
    fake.mkdir()
    (fake / "__init__.py").write_text("raise ImportError('pyyaml is not installed (simulated)')\n", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(tmp_path), "PYTHONIOENCODING": "utf-8"}
    for hook in ("pre-tool-use-drift-check.py", "fact-ownership-guard.py"):
        r = subprocess.run([sys.executable, str(HOOKS / hook)], input='{"tool_name": "Write", "tool_input": {}}',
                           capture_output=True, text=True, encoding="utf-8", env=env, cwd=ROOT, timeout=60)
        assert r.returncode == 2, (hook, r.returncode, r.stderr)
        assert "pyyaml" in r.stderr.lower(), (hook, r.stderr)


def test_the_test_summary_is_pytests_result_line_not_the_last_line() -> None:
    """DEF-234 — G-231: the summary the hook prints is pytest's result line, even when the interpreter's exit
    prints a logging error after it (aiohttp's unclosed connector ends in "Arguments: ()")."""
    sys.path.insert(0, str(HOOKS))
    import staged_tree
    out = ("....\n12 passed, 3 xfailed, 1 warning in 4.20s\n--- Logging error ---\nTraceback (most recent call "
           "last):\nValueError: I/O operation on closed file.\nCall stack:\nMessage: 'Unclosed connector'\nArguments: ()\n")
    assert staged_tree.result_line(out) == "12 passed, 3 xfailed, 1 warning in 4.20s"
    assert staged_tree.result_line("no result here\n") == "no result here"


def test_t67s_child_process_writes_utf8_whatever_the_shell() -> None:
    """DEF-235 — G-233: T67's test starts the app in a child process and reads its stderr as UTF-8; the child must
    write UTF-8 whatever the shell's encoding, so the test passes with PYTHONIOENCODING and PYTHONUTF8 unset."""
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
    t67 = "backend/tests/test_define_e2e.py::test_t67_start_up_exits_with_status_1_when_a_required_credential_is_missing"
    r = subprocess.run([sys.executable, "-m", "pytest", t67, "-q", "--no-header", "-p", "no:cacheprovider", "-n", "0",
                        "--runxfail"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env={**env, "AGENT_IMPROVE_NO_RECORD": "1"}, cwd=PROJECT, timeout=300)
    assert r.returncode == 0, r.stdout[-1500:]
