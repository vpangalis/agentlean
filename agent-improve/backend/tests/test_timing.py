"""Speed without losing quality — step 6.65 (founder ruling 2026-09-25).

The tooling it adds, proven: the timing log appends and sums (rule g), the
test recorder and the tracing guard hold under pytest-xdist (rule a), and the
commit's one full run is the parallel one (rule a).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_HOOKS = _REPO / ".claude" / "hooks"


def _timing():
    spec = importlib.util.spec_from_file_location("timing", _HOOKS / "timing.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_timing_log_appends_and_sums_only_its_window(tmp_path) -> None:
    timing = _timing()
    log = tmp_path / "timing.jsonl"
    rows = [
        {"at": "2026-09-25T10:00:00+00:00", "kind": "hook", "hook": "commit-msg rule 4 tests", "seconds": 113},
        {"at": "2026-09-25T10:01:00+00:00", "kind": "hook", "hook": "commit-msg rule 3 mypy", "seconds": 20},
        {"at": "2026-09-25T10:02:00+00:00", "kind": "tests", "seconds": 5.5},
        {"at": "2026-09-25T10:03:00+00:00", "kind": "live_model", "calls": 12, "seconds": 300},
        {"at": "2026-09-25T12:00:00+00:00", "kind": "tests", "seconds": 999},   # outside
    ]
    log.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    timing.append({"kind": "hook", "hook": "pre-commit continuity", "seconds": 1.0}, log)
    assert len(timing.read(log)) == 6, "append must add one line and keep the rest"
    s = timing.summarise("2026-09-25T09:59:00+00:00", "2026-09-25T10:30:00+00:00", log)
    assert s["hooks_seconds"] == {"commit-msg rule 3 mypy": 20.0, "commit-msg rule 4 tests": 113.0}
    assert s["tests"] == {"runs": 1, "seconds": 5.5}
    assert s["live_model"] == {"calls": 12, "seconds": 300.0}


def test_a_timing_failure_never_raises(tmp_path) -> None:
    """Timing must never fail a commit or a test run."""
    timing = _timing()
    timing.append({"kind": "hook"}, tmp_path / "no" / "\0bad" / "timing.jsonl")


def test_a_workers_tracing_calls_reach_the_controller() -> None:
    """Under xdist the G-95 guard would be blind to calls made in a worker;
    the worker hands its count up and the controller folds it in."""
    from backend.tests import conftest as cf

    class Node:
        workeroutput = {"trace_calls": ["create_run"]}

    before = list(cf.TRACE_CALLS)
    try:
        cf.pytest_testnodedown(Node(), None)
        assert cf.TRACE_CALLS[len(before):] == ["create_run"]
    finally:
        cf.TRACE_CALLS[:] = before


def test_the_commits_one_full_run_is_parallel() -> None:
    """Rule (a): ONE full run per commit, in parallel — the pre-commit hook's,
    first, so the board describes the commit's code; rule 4 reads its record
    and runs the suite itself only when no full run on this source exists."""
    pre = (_REPO / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    assert "AGENT_IMPROVE_FULL_RUN=1" in pre and "-n auto" in pre
    assert pre.index("-m pytest") < pre.index('"$CONTINUITY"'), "the run precedes the headline"
    guard = (_HOOKS / "commit-msg-refactor-guard.py").read_text(encoding="utf-8")
    assert guard.count('"-m", "pytest"') == 1, "the guard's only run is the fallback"
    assert '"-n", "auto"' in guard
    # The verdict is trusted only for the exact index tree it was run for.
    assert "full-run.json" in guard and '["git", "write-tree"]' in guard
    assert "git write-tree" in pre and "full-run.json" in pre
    reqs = (_REPO / "agent-improve" / "requirements.txt").read_text(encoding="utf-8")
    assert "pytest-xdist==" in reqs, "the parallel run's plugin is pinned"


def test_the_record_says_which_source_the_last_full_run_was_on(monkeypatch, tmp_path) -> None:
    import sys
    from backend.tests import conftest as cf
    sys.path.insert(0, str(_REPO / "agent-improve" / "tools" / "control_board"))
    import progress
    path = tmp_path / "test-results.json"
    monkeypatch.setattr(progress, "RESULTS", path)
    monkeypatch.setenv("AGENT_IMPROVE_FULL_RUN", "1")

    cf._record_results({"t::a": "passed"})
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["full_run_hash"] == progress.source_hash()
    monkeypatch.delenv("AGENT_IMPROVE_FULL_RUN")
    cf._record_results({"t::b": "passed"})          # a targeted run, same source
    assert json.loads(path.read_text(encoding="utf-8"))["full_run_hash"] == record["full_run_hash"]
