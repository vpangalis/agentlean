"""The prompt record, .claude/hooks/prompt_record.py — brief Part F9.1 (founder, 2026-09-27)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]


def _mod():
    spec = importlib.util.spec_from_file_location("prompt_record", _REPO / ".claude" / "hooks" / "prompt_record.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_hook_lines_group_into_commit_attempts() -> None:
    p = _mod()
    lines = [{"at": "2026-09-27T10:00:00+00:00", "hook": "pre-commit full test run", "seconds": 100},
             {"at": "2026-09-27T10:00:05+00:00", "hook": "commit-msg rule 4 tests", "seconds": 1},
             {"at": "2026-09-27T10:05:00+00:00", "hook": "pre-commit continuity", "seconds": 2},
             {"at": "2026-09-27T10:05:01+00:00", "hook": "commit-msg rule 10 board", "seconds": 1}]
    got = p._attempts(lines)
    assert [(a["first"][11:16], a["seconds"]) for a in got] == [("10:00", 101.0), ("10:05", 3.0)]


def test_the_timing_line_summarises_the_record_and_flags_the_time_box() -> None:
    p = _mod()
    rec = {"minutes": {k: {"value": v} for k, v in {"total": 75, "building": 40, "tests": 20, "hooks": 5,
                                                    "waiting_for_founder": 3, "rework": 7}.items()},
           "refused_attempts": 2, "failed_preflights": 1, "commits": [{}, {}], "live_model_calls": 0}
    line = p.line(rec)
    assert line.startswith("Timing: 75 min — over the 60-minute box — building 40 · tests 20")
    assert "rework 7 (2 refused attempt(s), 1 failed pre-flight(s)) · 2 commits · 0 live model calls" in line


def _trailer():
    spec = importlib.util.spec_from_file_location("timing_trailer", _REPO / ".claude" / "hooks" / "timing_trailer.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_two_timing_labels_name_a_fast_run_as_a_test_run(monkeypatch) -> None:
    """Founder ruling 4.4, 2026-09-29. The commit trailer said "(docs only: no suite)" over a fast
    run (234c0a3, 67bc629), and the prompt record counted the fast run's seconds as hooks as well
    as tests."""
    t = _trailer()
    at = "2026-09-29T10:00:00+00:00"
    start = 1_790_000_000.0 - 10**6        # before `at`
    row = lambda h, s: {"kind": "hook", "hook": f"pre-commit {h}", "seconds": s, "at": at}  # noqa: E731
    assert "(fast run: the tests the change reaches)" in t.line(start, [row("fast test run", 47), row("continuity", 9)])
    assert "(docs only" not in t.line(start, [row("fast test run", 47)])
    assert "(docs only: no suite)" in t.line(start, [row("continuity", 9)])
    full = t.line(start, [row("full test run", 232), row("continuity", 9)])
    assert full.startswith("Timing: pre-commit 241 s — ") and "(" not in full.split(" — ")[0]

    p = _mod()
    lines = [{"at": at, "kind": "hook", "hook": "pre-commit fast test run", "seconds": 47},
             {"at": at, "kind": "hook", "hook": "pre-commit continuity", "seconds": 9},
             {"at": at, "kind": "tests", "seconds": 45}]
    monkeypatch.setattr(p.timing, "read", lambda *a, **k: lines)
    m = p.measure("2026-09-29T09:00:00+00:00", "2026-09-29T11:00:00+00:00", [])
    assert m["tests_s"] == 45 and m["hooks_s"] == 9
