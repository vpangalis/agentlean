"""The control board as a value-stream picture — brief Part F7 (founder, 2026-09-27).

Pinned: every feature is one tile in its stage × layer cell; a status is derived as the brief
defines it (green = passes; amber = written and failing, or its lane's top; grey = a stub);
the page carries the blocks of the founder's mockup and no longer the retired tables; and the
commit guard's rule 10 reads the rendered page back as true.
"""
from __future__ import annotations

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
