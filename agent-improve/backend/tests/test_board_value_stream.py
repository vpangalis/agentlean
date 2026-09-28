"""The control board as a value-stream picture — brief Part F7 (founder, 2026-09-27).

Pinned: every feature is one tile in its stage × layer cell; a status is derived as the brief
defines it (green = passes; amber = written and failing, or its lane's top; grey = a stub);
the page carries the blocks of the founder's mockup and no longer the retired tables; and the
commit guard's rule 10 reads the rendered page back as true.
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
import check_board  # noqa: E402
import features as F  # noqa: E402


@pytest.fixture(scope="module")
def board() -> tuple[dict, str]:
    d = bcb.data()
    return d, bcb.render(d)


def test_every_feature_is_one_tile_in_its_cell(board) -> None:
    d, page = board
    tiles = re.findall(r"data-f='(DEF-\d{3})' data-tip", page)
    assert sorted(tiles) == sorted(f["id"] for f in F.load())


def test_a_status_is_derived_green_amber_grey(board) -> None:
    d, _ = board
    st = F.status(F.load(), F.results())
    tops = {x["now"] for x in d["lanes"]}
    for f in d["features"]:
        # founder 2026-09-28: a passing test that is not end to end is amber, not green
        assert (f["status"] == "green") == (st[f["id"]] == "passing" and not f["not_e2e"]), f["id"]
        if f["id"] in tops:
            assert f["status"] == "amber", f["id"]


def test_the_page_has_the_mockups_blocks_and_not_the_retired_tables(board) -> None:
    _, page = board
    for block in ("Define complete", "Belt journey", "Value stream", "Now per lane", "Waiting for you",
                  "Prompt flow", "Burn-up per milestone", "Last commits"):
        assert f">{block}" in page, block
    for retired in ("By clause and by lane", "Next failing feature per lane"):
        assert retired not in page
    assert page.count("class='h'") == 4                      # the health strip's four counters


def test_rule_10_reads_the_rendered_page_back_as_true(board) -> None:
    _, page = board
    assert check_board.check(page, None) == []


def test_a_feature_held_by_its_adr_is_never_a_lanes_top_and_waiting_counts_it(board) -> None:
    """Founder 2026-09-28: held features stay on the board, marked, but no lane takes one."""
    d, page = board
    held = {f["id"]: f["held"] for f in d["features"] if f["held"]}
    tops = {x["now"] for x in d["lanes"]} | {i for x in d["lanes"] for i in x["package"]["features"]}
    assert held and not held.keys() & tops
    for adr in set(held.values()):
        n = sum(1 for a in held.values() if a == adr)
        assert f"{adr} PROPOSED — holds {n} feature(s)" in page


_CELL = re.compile(r"<td><div class='tiles'>(.*?)</div></td>", re.S)
_TILE = re.compile(r"<button class='t ([^']*)' data-f='(DEF-\d{3})' data-tip='[^']*'>([^<]*)</button>")


def test_each_cell_stands_in_the_order_of_work(board) -> None:
    """Tooling, founder 2026-09-28: in a cell the squares are sorted by rank; unranked last."""
    d, page = board
    rank_of = {f["id"]: f["rank"] for f in d["features"]}
    cells = [_TILE.findall(c) for c in _CELL.findall(page)]
    assert sum(len(c) for c in cells) == len(d["features"])
    for cell in cells:
        keys = [(rank_of[i] is None, rank_of[i] or 0) for _, i, _ in cell]
        assert keys == sorted(keys), [i for _, i, _ in cell]


def test_an_m1_square_is_outlined_and_numbered_with_its_rank(board) -> None:
    d, page = board
    f_of = {f["id"]: f for f in d["features"]}
    tiles = [t for c in _CELL.findall(page) for t in _TILE.findall(c)]
    assert any(" m1" in f" {cls}" for cls, _, _ in tiles)
    for cls, fid, text in tiles:
        f = f_of[fid]
        classes = cls.split()
        assert "x" not in classes                          # the small x is retired
        assert ("m1" in classes) == (f["tier"] == 1), fid
        assert text == (str(f["rank"]) if f["tier"] == 1 and f["rank"] else ""), fid


def test_the_legend_is_one_line(board) -> None:
    _, page = board
    assert '<div class="legend" data-key="legend">colour = status · outline = M1 · number = order of work</div>' in page


def test_now_per_lane_highlights_the_square_and_the_panel_names_its_place(board) -> None:
    """A click on a lane row marks the grid square with that id; the panel reads
    Stage · Layer · Tier · position in the order of work."""
    d, page = board
    for x in d["lanes"]:
        if x["now"]:
            assert f"<div class='row' data-f='{x['now']}'>" in page
            assert f"class='t amber" in page and f"data-f='{x['now']}' data-tip" in page
    assert "mark(a.dataset.f)" in page and ".vs .t[data-f=" in page and ".t.hl{" in page
    assert "'Stage · Layer · Tier · Order of work'" in page
    m = re.search(r'<script type="application/json" id="board-data">(.*?)</script>', page, re.S)
    assert m
    blob = json.loads(m.group(1).replace("<\/", "</"))
    assert blob["stages"] == dict(bcb.STAGES) and blob["layers"] == dict(bcb.LAYERS)
    assert blob["ranked"] == sum(1 for f in d["features"] if f["rank"])
