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
