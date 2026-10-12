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


def test_every_run_reports_its_turn_times_per_turn_type() -> None:
    """Founder ruling 2026-10-12 (turn time): the run's summary carries, per turn type, the count,
    median, 90th percentile and max, and names the types whose 90th percentile reaches the 30 s watch
    figure (watched, not a stop condition)."""
    teach: list[dict] = [{"kind": "turn", "move": "store_and_advance", "seconds": float(s)} for s in range(20, 30)]
    entries: list[dict] = [{"kind": "turn", "move": "teach", "seconds": 31.0}, *teach,
               {"kind": "turn", "move": "read_back", "seconds": 18.0},
               {"kind": "turn", "move": "challenge", "seconds": 15.0},
               {"kind": "upload", "seconds": 7.8}, {"kind": "turn", "move": "store_and_advance", "seconds": 25.7},
               {"kind": "gate_review", "seconds": None}, {"kind": "gate_decision", "seconds": 4.9},
               {"kind": "summary"}]
    t = define_runthrough.turn_times(entries)
    by = t["by_type"]
    assert set(by) == {"teaching", "read-back", "answer", "upload", "gate"}, by
    assert by["teaching"] == {"n": 11, "median": 25.0, "p90": 29.0, "max": 31.0}, by["teaching"]
    assert by["upload"]["n"] == 1 and by["gate"] == {"n": 1, "median": 4.9, "p90": 4.9, "max": 4.9}
    assert t["p90_watch_s"] == 30.0 and t["p90_over_watch"] == []
    entries[0]["seconds"], entries[10]["seconds"] = 44.0, 40.0
    assert define_runthrough.turn_times(entries)["p90_over_watch"] == ["teaching"]
    src = define_runthrough.Path(define_runthrough.__file__).read_text(encoding="utf-8")
    assert 'summary["turn_times"] = turn_times(' in src, "the run's summary does not carry the turn times"


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


def test_the_judge_evaluation_scores_false_rejects_and_false_accepts_against_the_labels() -> None:
    """Founder ruling 2026-10-12 (quality stop, item 2): the offline evaluation keeps every coherence
    rejection, samples the grader fails and the accepted turns by move, and scores a judge's verdicts
    against the founder's labels — false-reject rate over the replies labelled good, false-accept rate
    over the replies labelled not good; an unlabelled turn is not scored."""
    from scripts import judge_eval_set, judge_replay

    def turn(i: str, move: str, coherent: bool, grade: str | None) -> dict:
        return {"id": i, "move": move, "coherence": {"coherent": coherent},
                "grader": {"status": grade} if grade else None}
    turns = ([turn(f"r{i}", "challenge", False, None) for i in range(3)]
             + [turn(f"f{i}", m, True, "failed") for i, m in enumerate(["read_back"] * 20 + ["challenge"] * 5)]
             + [turn(f"a{i}", "store_and_advance", True, "pass") for i in range(10)])
    picked = judge_eval_set.pick(turns)
    ids = [t["id"] for t in picked]
    assert ids[:3] == ["r0", "r1", "r2"], "every coherence rejection is kept"
    fails = [t for t in picked if t["grader"] and t["grader"]["status"] == "failed"]
    assert len(fails) == judge_eval_set.FAILS_SAMPLED and {t["move"] for t in fails} == {"read_back", "challenge"}
    assert len(picked) == 3 + judge_eval_set.FAILS_SAMPLED + judge_eval_set.ACCEPTED

    labels = {"a": {"reply_good": True}, "b": {"reply_good": True}, "c": {"reply_good": False},
              "d": {"reply_good": False}, "e": {}}
    accepted = {"a": False, "b": True, "c": True, "d": False, "e": False}
    r = judge_replay.rates(accepted, labels)
    assert r["labelled"] == 4 and r["false_rejects"] == ["a"] and r["false_reject_rate"] == 0.5
    assert r["false_accepts"] == ["c"] and r["false_accept_rate"] == 0.5
    assert judge_replay.FALSE_REJECT_STOP == 0.20
