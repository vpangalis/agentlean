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
    assert '"cut_offs": cut_offs(walk)' in src, "the run's summary does not carry the count (the walk's calls)"


def test_g153_a_run_with_more_than_one_cut_off_fails() -> None:
    """Founder ruling 2026-10-12: strict output was probed and refused, so a cut-off reply stays answered
    in code — and a run with more than one cut-off fails (exit 5)."""
    ok = {"cost": {"within_ceiling": True}}
    assert define_runthrough.CUT_OFF_LIMIT == 1
    assert define_runthrough.exit_code({**ok, "cut_offs": {"count": 1, "calls": []}}, []) == 0
    assert define_runthrough.exit_code({**ok, "cut_offs": {"count": 2, "calls": []}}, []) == 5
    assert define_runthrough.exit_code(ok, []) == 0


def test_the_coach_input_ratchet_refuses_above_its_ceiling_and_accepts_at_or_below() -> None:
    """Founder rulings 2026-10-27, item 10 and ADR-0111 D7 (b), offline — the one comparison the record's test
    (test_define_runthrough.py) and the run share: run 4's 6,810 + 5% is a ceiling of 7,150, rounded down; at or
    below it passes, above it is refused naming both numbers. The tracked record is the ruled one, never raised."""
    r = {"coach_input_tokens_per_call": 6810, "allowance": 0.05, "measured_on": "run 4"}
    assert define_runthrough.coach_ratchet_ceiling(r) == 7150
    for ok in (7150, 7150.0, 6821.6, 6810, 1):
        assert define_runthrough.coach_ratchet_refusal(ok, r) is None, ok
    refused = define_runthrough.coach_ratchet_refusal(7150.1, r)
    assert refused and "7,150.1 tokens per call" in refused and "ceiling of 7,150 " in refused and "6,810" in refused
    assert define_runthrough.coach_ratchet_refusal(9000, r)
    assert define_runthrough.coach_input_per_call(
        {"by_role": {"coach": {"calls": 35, "input_tokens": 238757}}}) == 238757 / 35
    assert define_runthrough.coach_input_per_call({"by_role": {"grader": {"calls": 3, "input_tokens": 9}}}) is None
    tracked = define_runthrough.load_coach_ratchet()
    assert tracked["coach_input_tokens_per_call"] <= 6810 and tracked["allowance"] == 0.05, tracked
    assert tracked["_rule"] and tracked["measured_on"], tracked


def test_the_latest_run_keeps_the_coach_input_per_call_within_its_ratchet() -> None:
    """Founder rulings 2026-10-27, item 10 and ADR-0111 D7 (b), on the latest counted live run-through record: the
    coach's input tokens per call (summary.tokens.by_role["coach"]) is at most the ratchet's ceiling. Here, not in
    test_define_runthrough.py, whose module is a feature measurement (xfail) and could not refuse."""
    files = sorted((define_runthrough.Path(define_runthrough.__file__).resolve().parents[1] / "docs" / "runthrough")
                   .glob("define_runthrough_*.json"))
    assert files, "no run-through record in docs/runthrough/"
    summary: dict = next((line for line in json.loads(files[-1].read_text(encoding="utf-8"))
                          if line.get("kind") == "summary"), {})
    tokens = summary.get("tokens") or {}
    per_call = define_runthrough.coach_input_per_call(tokens)
    assert per_call is not None, f"{files[-1].name} records no coach call"
    coach = tokens["by_role"]["coach"]
    refusal = define_runthrough.coach_ratchet_refusal(per_call, define_runthrough.load_coach_ratchet())
    assert refusal is None, (f"{files[-1].name}: {refusal}; of its {coach.get('input_tokens', 0):,} coach input "
                             f"tokens, {coach.get('cached_input_tokens', 0):,} were served from the prompt cache")


def test_the_run_lowers_the_coach_ratchet_when_it_falls_and_never_raises_it(tmp_path) -> None:
    """ADR-0111 D7 (b): after its tree record is written, a complete run below the recorded figure lowers it to its
    own, rounded down; a run above it, or one that stopped early, leaves it as it is; above the ceiling the run
    says the ratchet test will refuse — the exit code does not change for it."""
    path = tmp_path / "coach-input-ratchet.json"
    base = {"_rule": "the ruling", "coach_input_tokens_per_call": 6810, "allowance": 0.05, "measured_on": "run 4"}
    path.write_text(json.dumps(base), encoding="utf-8")

    def summary(input_tokens: int, stopped: str = "done") -> dict:
        return {"stopped": stopped, "tokens": {"by_role": {"coach": {"calls": 10, "input_tokens": input_tokens}}}}

    def after(s: dict, name: str = "define_runthrough_X") -> str | None:
        return define_runthrough.coach_ratchet_after_run(s, name, path)

    def held() -> bool:
        return json.loads(path.read_text(encoding="utf-8")) == base
    line = after(summary(68_216))                                   # 6,821.6: above the record, within the ceiling
    assert line and "within the ceiling of 7,150" in line and held(), line
    line = after(summary(71_510))                                   # 7,151.0: above the ceiling
    assert line and "will refuse" in line and "7,151.0" in line and "7,150" in line and held(), line
    line = after(summary(60_000, stopped="cap: 150 model calls"))   # below, but the run stopped early
    assert line and "not lowered" in line and held(), line
    assert after({"tokens": {}}) is None and held()
    line = after(summary(67_995), "define_runthrough_20261028T090000")   # 6,799.5: below, complete
    assert line and "lowered from 6,810 to 6,799" in line, line
    assert json.loads(path.read_text(encoding="utf-8")) == {
        **base, "coach_input_tokens_per_call": 6799, "measured_on": "define_runthrough_20261028T090000"}
    src = define_runthrough.Path(define_runthrough.__file__).read_text(encoding="utf-8")
    assert src.index("tree.write_text(") < src.index("coach_ratchet_after_run(summary, tree.stem)"), \
        "the run does not check the ratchet after writing its tree record"


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


def test_the_founders_sheet_is_read_and_right_for_the_wrong_reason_is_counted_apart(tmp_path) -> None:
    """Founder 2026-10-13: the labels come from the Excel sheet (reply_good yes/no, judge_right right/wrong,
    an optional note); a rejection labelled right WITH a note is "right outcome, wrong reason", counted
    apart; an empty row is not a label."""
    from openpyxl import Workbook

    from scripts import judge_replay

    wb = Workbook()
    ws = wb.active
    ws.title = "Turns"
    ws.append(["id", "turn type", "Belt message", "coach reply (the one judged)", "coherence verdict",
               "coherence reason", "grader verdict", "grader reason", "rejected_by", "reply_good (yes/no)",
               "judge_right (right/wrong)", "note (optional)"])
    ws.append(["r#1", "", "", "", "rejected", "", "", "", "coherence", "no", "right", "it missed the real gap"])
    ws.append(["r#2", "", "", "", "rejected", "", "", "", "coherence", "yes", "wrong", None])
    ws.append(["r#3", "", "", "", "accepted", "", "pass", "", "none", None, None, None])
    sheet = tmp_path / "s.xlsx"
    wb.save(sheet)
    labels = judge_replay.labels_from_sheet(sheet)
    assert labels == {"r#1": {"reply_good": False, "rejection_right": True, "note": "it missed the real gap"},
                      "r#2": {"reply_good": True, "rejection_right": False, "note": ""}}
    turns = [{"id": i, "move": "challenge", "coherence": {"coherent": False}, "grader": None} for i in ("r#1", "r#2")]
    out = judge_replay.report(turns, [], labels, {}, 1.0)
    assert out["right_outcome_wrong_reason"] == ["r#1"]
    assert out["rejections_labelled_wrong"]["wrong"] == ["r#2"]


def test_c9_the_blind_labels_sheet_and_the_verdicts_are_two_files_joined_by_row_id(tmp_path) -> None:
    """C9 (founder ruling 2026-10-27; the blind sheet): GRADER_LABELS.csv carries the Belt's message, the confirmed values
    given to the coach, the move, the planner's decision, the coach's reply and empty founder columns for G1, G3, G4
    and G6 — no verdict; GRADER_VERDICTS.csv carries the grader's verdicts and quotes by the same row id; the rows are
    shuffled; judge_replay.py joins them and scores agreement per criterion (C10, ADR-0081's thresholds)."""
    import csv

    from scripts import grader_labels
    from scripts.judge_replay import join_labels, label_agreement
    grade = {"status": "failed", "move": "challenge",
             "verdicts": {"G1": "pass", "G4": "fail", "G3": "pass", "G2": "pass"},
             "failed": [{"criterion": "G4", "reason": "explain what fits", "evidence": "Tell me more."}],
             "not_counted": [{"criterion": "G3", "reason": "invented"}], "decision": "insufficient — no step named"}
    run = [{"kind": "turn", "n": n, "field": "problem_statement", "belt": f"Answer {n}.",
            "reply": {"answer": "Tell me more.", "prompt": "Where does it show?"}, "grader": grade} for n in range(1, 7)]
    block = '<confirmed_values>\n<value name="Team">{n} people</value>\n</confirmed_values>'
    inputs = tmp_path / "in.jsonl"
    inputs.write_text("\n".join(json.dumps({"n": n, "coach_inputs": [[{"type": "system", "blocks": [
        block.format(n=n)]}]]}) for n in range(1, 7)), encoding="utf-8")
    (tmp_path / "rt.json").write_text(json.dumps(run), encoding="utf-8")
    grader_labels.main(["--record", str(tmp_path / "rt.json"), "--inputs", str(inputs), "--out-dir", str(tmp_path)])
    labels = list(csv.DictReader((tmp_path / grader_labels.LABELS).open(encoding="utf-8-sig")))
    verdicts = list(csv.DictReader((tmp_path / grader_labels.VERDICTS).open(encoding="utf-8-sig")))
    assert [r["row_id"] for r in labels] == [f"R{i:03d}" for i in range(1, 7)] == [r["row_id"] for r in verdicts]
    assert not any("verdict" in k or "quote" in k for k in labels[0]), "the labels sheet shows no verdict"
    assert set(labels[0]) >= {"belt_message", "confirmed_values", "move", "planner_decision", "coach_reply",
                              "G1_founder", "G3_founder", "G4_founder", "G6_founder"}
    assert [r["belt_message"] for r in labels] != [f"Answer {n}." for n in range(1, 7)], "the rows are not shuffled"
    first = labels[0]
    n = int(first["belt_message"].split()[1].rstrip("."))
    assert f"{n} people" in first["confirmed_values"] and first["planner_decision"] == "insufficient — no step named"
    v = next(x for x in verdicts if x["row_id"] == first["row_id"])
    assert v["G4_verdict"] == "fail" and v["G4_quote"] == "Tell me more." and v["G2_verdict"] == "pass"
    assert v["G3_verdict"].startswith("not counted") and v["source"] == f"rt turn {n}"
    for r in labels:
        r.update(G1_founder="pass", G4_founder="fail", G3_founder="n/a", G6_founder="")
    out = label_agreement(join_labels(labels, verdicts))
    assert out["per_criterion"]["G4"]["agreement"] == 1.0 and out["per_criterion"]["G1"]["agree"] == 6
    assert "G3" not in out["per_criterion"] and out["met"] is True
    worse = [{**r, "G4_founder": "pass"} for r in labels]
    assert label_agreement(join_labels(worse, verdicts))["per_criterion"]["G4"]["false_fail_rate"] == 1.0
