"""The control board's Belt journey strip — tooling, founder 2026-09-28.

Pinned: the strip carries its subtitle; each of the 13 element squares names its element on
hover and opens a panel with what the Belt provides, why it matters and the acceptance criteria
(all read from the Define skill), what happened to it in the run (read from the run record) and
the features behind it; each stage square opens the same panel with what happens at the stage
(read from the skill or business.md), what happened in the run, and the stage's features.
Nothing in those panels is typed into the generator.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

_PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT / "tools" / "control_board"))

import build_control_board as bcb  # noqa: E402

_STATES = {"stored", "not stored", "stuck", "not reached"}


@pytest.fixture(scope="module")
def board() -> tuple[dict, str]:
    d = bcb.data()
    return d, bcb.render(d)


def _blob(page: str) -> dict:
    m = re.search(r'<script type="application/json" id="board-data">(.*?)</script>', page, re.S)
    assert m
    return json.loads(m.group(1).replace("<\\/", "</"))


def test_the_strip_carries_its_subtitle(board) -> None:
    _, page = board
    assert ">One real Belt run through the product · white = not reached in this run</p>" in page


def test_each_element_square_names_its_element_on_hover_and_opens_its_panel(board) -> None:
    d, page = board
    names = [n for n, _ in bcb._elements()]
    assert len(names) == 13
    squares = re.findall(r"<i class='el (\w+)' data-el='(\d+)' data-tip='([^']*)'></i>", page)
    assert [int(i) for _, i, _ in squares] == list(range(13))
    for (cls, i, tip), name in zip(squares, names):
        assert tip.startswith(f"{int(i) + 1} · {bcb.E(name)} — "), tip
        assert cls in ("done", "wip", "miss", "open")
    assert "closest('[data-el]')" in page and "open(element(+el.dataset.el))" in page


def test_the_element_panel_reads_the_skill_not_the_generator(board) -> None:
    d, _ = board
    skill = bcb._plain(bcb.SKILL.read_text(encoding="utf-8"))
    for e in d["journey"]["element_detail"]:
        assert e["what"] and e["what"] in skill, e["n"]
        assert e["why"] and e["why"] in skill, e["n"]
        assert e["criteria"], e["n"]
        block = re.search(rf"\[{e['n']} · .*?(?=\n\*\*\[|\Z)", bcb.SKILL.read_text(encoding="utf-8"), re.S)
        assert block
        for key, text in e["criteria"]:
            assert f"`{key}`" in block.group(0) and text in skill, (e["n"], key)


def test_what_happened_to_each_element_is_read_from_the_run_record(board) -> None:
    d, _ = board
    j = d["journey"]
    if not j["file"]:
        pytest.skip("no run-through recorded")
    recs = json.loads((bcb.features.RUNTHROUGH / j["file"]).read_text(encoding="utf-8"))
    final = next(r for r in recs if r.get("kind") == "final_case")
    summ = next(r for r in recs if r.get("kind") == "summary")
    stored = set(final.get("define_structured") or {})
    for e, cls in zip(j["element_detail"], j["elements"]):
        assert e["state"] in _STATES and e["happened"], e["n"]
        assert (e["state"] == "stored") == all(f in stored for f in e["fields"]), e["n"]
        assert cls == {"stored": "done", "stuck": "wip", "not stored": "miss", "not reached": "open"}[e["state"]]
        if e["state"] == "stuck":
            assert summ["stuck_at"] in e["fields"]
            assert any(summ["stopped"] in h for h in e["happened"]), e["n"]


def test_the_features_behind_an_element_name_it_and_stand_in_the_order_of_work(board) -> None:
    d, _ = board
    f_of = {f["id"]: f for f in d["features"]}
    for e in d["journey"]["element_detail"]:
        field_feature = [f for f in d["features"] if f"[{e['n']}-" in f["test"]]
        assert all(f["id"] in e["features"] for f in field_feature), e["n"]
        keys = [(f_of[i]["rank"] is None, f_of[i]["rank"] or 0) for i in e["features"]]
        assert keys == sorted(keys), e["n"]
        assert all(f_of[i]["stage"] == "coached" for i in e["features"]), e["n"]


def test_each_stage_square_opens_what_happens_there_from_its_source(board) -> None:
    d, page = board
    for k, label in bcb.STAGES:
        assert f"<div class='stage {d['journey']['stages'][k]}' data-stage='{k}'" in page, k
        s = d["journey"]["stage_detail"][k]
        path, _ = bcb.STAGE_SOURCES[k]
        assert s["label"] == label
        assert s["what"] and s["what"] in re.sub(r"\s+", " ", bcb._plain(path.read_text(encoding="utf-8"))), k
        assert s["source"].startswith(path.name), k
        assert s["features"] == [f["id"] for f in sorted(
            (f for f in d["features"] if f["stage"] == k),
            key=lambda f: (f["rank"] is None, f["rank"] or 0, f["id"]))], k
    assert "open(stage(sg.dataset.stage))" in page
    blob = _blob(page)
    assert set(blob["journey"]["stages"]) == {k for k, _ in bcb.STAGES}
    assert len(blob["journey"]["elements"]) == 13


def test_a_stage_the_run_did_not_reach_names_the_element_it_stopped_at(board) -> None:
    d, _ = board
    j = d["journey"]
    stuck = [e for e in j["element_detail"] if e["state"] == "stuck"]
    if not stuck:
        pytest.skip("the latest run is not stuck")
    e = stuck[0]
    for k in ("report", "approve", "record_written", "next_phase"):
        if j["stages"][k] == "open":
            assert j["stage_detail"][k]["happened"][0] == \
                f"not reached: the run stopped at element {e['n']} ({e['name']})", k


def test_a_synthetic_run_record_drives_the_states(tmp_path, monkeypatch) -> None:
    """Independent of the live record: element 1 stored, stuck at element 2, the rest white."""
    recs = [
        {"kind": "turn", "n": 1, "field": "business_case", "move": "read_back", "verdict": "sufficient"},
        {"kind": "turn", "n": 2, "field": "team", "move": "store_and_advance", "stored_field": "business_case"},
        {"kind": "turn", "n": 3, "field": "team", "move": "challenge", "verdict": "insufficient"},
        {"kind": "final_case", "current_phase": "define", "define_structured": {"business_case": "x"}},
        {"kind": "summary", "case_id": "C-1", "stuck_at": "team", "stopped": "stopped by hand at team"},
    ]
    (tmp_path / "define_runthrough_20260101T000000.json").write_text(json.dumps(recs), encoding="utf-8")
    monkeypatch.setattr(bcb.features, "RUNTHROUGH", tmp_path)
    j = bcb.journey()
    states = [e["state"] for e in j["element_detail"]]
    assert states == ["stored", "stuck", *["not reached"] * 11]
    assert j["elements"][:3] == ["done", "wip", "open"]
    assert "business_case: stored at turn 2" in j["element_detail"][0]["happened"]
    team = j["element_detail"][1]["happened"]
    assert "answer judged insufficient at turn(s) 3" in team
    assert "the run record: stopped by hand at team" in team
    assert j["stage_detail"]["open_case"]["happened"] == ["case C-1 opened; 3 turns recorded"]
    assert j["stage_detail"]["approve"]["happened"] == ["not reached: the run stopped at element 2 (Team)"]
