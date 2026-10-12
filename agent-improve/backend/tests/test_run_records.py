"""The live run's record (founder, Desktop review of package 6, 2026-10-11).

- G-153: every run counts the model calls cut off at their token limit (`cut_offs` in the summary).
- A failed run is kept, marked "failed: not counted" (`scripts/mark_failed_run.py`), and no reader
  of the latest record picks it up.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from scripts import define_runthrough, mark_failed_run
from scripts.move_proof_661 import _usage


def test_g153_a_call_cut_off_at_its_token_limit_is_counted_per_run() -> None:
    from langchain_core.messages import AIMessage
    cut = AIMessage(content="", response_metadata={"finish_reason": "length"},
                    usage_metadata={"input_tokens": 5877, "output_tokens": 1500, "total_tokens": 7377})
    done = AIMessage(content="", response_metadata={"finish_reason": "tool_calls"})

    def result(msg):
        return SimpleNamespace(generations=[[SimpleNamespace(message=msg)]], llm_output={})
    calls = [{"kind": "coach", "at": "t1", **_usage(None, result(cut))},
             {"kind": "coach", "at": "t2", **_usage(None, result(done))},
             {"kind": "coherence", "at": "t3"}]
    assert calls[0]["finish_reason"] == "length"
    assert define_runthrough.cut_offs(calls) == {
        "count": 1, "calls": [{"kind": "coach", "at": "t1", "output_tokens": 1500}]}
    src = (define_runthrough.Path(define_runthrough.__file__)).read_text(encoding="utf-8")
    assert '"cut_offs": cut_offs(CALLS)' in src, "the run's summary does not carry the count"


def test_g153_a_run_with_more_than_one_cut_off_fails() -> None:
    """Founder ruling 2026-10-12: strict output was probed and refused, so a cut-off reply stays answered
    in code — and a run with more than one cut-off fails (exit 5)."""
    ok = {"cost": {"within_ceiling": True}}
    assert define_runthrough.CUT_OFF_LIMIT == 1
    assert define_runthrough.exit_code({**ok, "cut_offs": {"count": 1, "calls": []}}, []) == 0
    assert define_runthrough.exit_code({**ok, "cut_offs": {"count": 2, "calls": []}}, []) == 5
    assert define_runthrough.exit_code(ok, []) == 0


def test_a_failed_run_is_kept_marked_and_never_read_as_the_latest(tmp_path) -> None:
    good, bad = "20261011T155414", "20261011T152731"
    for stamp in (good, bad):
        (tmp_path / f"define_runthrough_{stamp}.json").write_text(json.dumps([{"kind": "summary"}]), encoding="utf-8")
        (tmp_path / f"validation_repeat_{stamp}.json").write_text("[]", encoding="utf-8")
        (tmp_path / f"wallclock_{stamp}.json").write_text("{}", encoding="utf-8")
    kept = mark_failed_run.mark(bad, "DEF-005, DEF-006 failed: G-153 turn 5, G-154 turn 26", tmp_path)
    assert sorted(p.name for p in kept) == sorted(f"failed_{k}_{bad}.json" for k in mark_failed_run.KINDS)
    entries = json.loads((tmp_path / f"failed_define_runthrough_{bad}.json").read_text(encoding="utf-8"))
    assert entries[-1]["status"] == "failed: not counted" and "G-153" in entries[-1]["reason"]
    for pattern in ("define_runthrough_*.json", "validation_repeat_*.json", "wallclock_*.json"):
        assert [p.name for p in sorted(tmp_path.glob(pattern))] == [pattern.replace("*", good)], pattern
    with pytest.raises(ValueError):
        mark_failed_run.mark(good, "  ", tmp_path)
    with pytest.raises(FileNotFoundError):
        mark_failed_run.mark("20990101T000000", "no such run", tmp_path)
