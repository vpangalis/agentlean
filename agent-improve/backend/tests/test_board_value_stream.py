"""The control board — one picture and one list that always agree (board redesign, founder
2026-09-30; the layout is `docs/founder-inputs/board-mockup.html`'s).

Pinned: every shown feature is one tile in its stage × layer cell and the tiles number the
registry's features; colour = state, three states; every number — the milestone buttons, the
"What's left" groups, Next up and the tile total — is read from `count()`, and the list of a
milestone sums to its total minus its done; the pilot cut splits M2 only once the registry
carries it; the retired sections are gone; the commit guard's rule 10 reads the page back as true.
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
import rank as R  # noqa: E402


@pytest.fixture(scope="module")
def board() -> tuple[dict, str]:
    d = bcb.data()
    return d, bcb.render(d)


_TILE = re.compile(r"<button type='button' class='t (\w+)' data-f='(DEF-\d{3})' data-ms='([^']*)' "
                   r"data-tip='([^']*)' aria-label='[^']*'></button>")
_SECTION = re.compile(r"<section data-for='([\w-]+)'(?: hidden)?><h2>What's left · [^<]* · (\d+)</h2>(.*?)</section>", re.S)
_BUTTON = re.compile(r"<button type='button' class='m' data-ms='([\w-]+)'.*?<span class='big'>(\d+)"
                     r"<span class='small mut'> / (\d+) done</span>", re.S)


def _blob(page: str) -> dict:
    m = re.search(r'<script type="application/json" id="board-data">(.*?)</script>', page, re.S)
    assert m
    return json.loads(m.group(1).replace("<\\/", "</"))


def test_the_grid_tile_count_equals_the_registry(board) -> None:
    """One tile per registry feature; only a feature whose requirement is Won't-now is not shown."""
    d, page = board
    feats, reqs = F.load(), F.requirements()
    deferred = {f["id"] for f in feats if (reqs.get(f["requirement"]) or {}).get("moscow") == "Won't-now"}
    tiles = [fid for _, fid, _, _ in _TILE.findall(page)]
    assert sorted(tiles) == sorted(f["id"] for f in feats if f["id"] not in deferred)
    assert len(tiles) == d["count"]["tiles"] == len(feats) - len(deferred)
    assert f'data-tiles="{d["count"]["tiles"]}"' in page
    assert d["count"]["hidden"] == sorted(deferred)


def test_the_sum_of_the_list_is_total_minus_done_for_every_milestone(board) -> None:
    """THE count test (founder 2026-09-30): for every milestone the list holds exactly total − done
    features, its groups' counts add up to that, and its button, its tiles and its heading all
    say the same — every number is read from `count()`."""
    d, page = board
    c = d["count"]
    assert c == bcb.count(d["features"])
    sections = {k: (int(n), body) for k, n, body in _SECTION.findall(page)}
    buttons = {k: (int(done), int(total)) for k, done, total in _BUTTON.findall(page)}
    tiles = _TILE.findall(page)
    assert set(sections) == set(buttons) == {x["key"] for x in c["milestones"]}
    for x in c["milestones"]:
        k = x["key"]
        heading, body = sections[k]
        items = re.findall(r"<li><i class='dot (\w+)'></i><a href='#' data-f='(DEF-\d{3})'>", body)
        groups = [int(n) for n in re.findall(r"<span data-n='(\d+)'>", body)]
        assert len(items) == sum(groups) == heading == x["total"] - x["done"] == len(x["left"]), k
        assert "green" not in {cls for cls, _ in items}, k
        assert buttons[k] == (x["done"], x["total"]), k
        mine = [cls for cls, _, ms, _ in tiles if k in ms.split()]
        assert len(mine) == x["total"] and mine.count("green") == x["done"], k
        assert mine.count("amber") == x["built"] and mine.count("grey") == x["not_started"], k
        assert x["done"] + x["built"] + x["not_started"] == x["total"], k
        for g in x["groups"]:
            if g["built"]:
                assert f"{len(g['left'])} left</span> ({g['built']} built, to prove)" in body, (k, g["layer"])


def test_every_tile_is_in_all_of_define_and_in_at_most_one_other_milestone(board) -> None:
    d, page = board
    for _, fid, ms, _ in _TILE.findall(page):
        keys = ms.split()
        assert keys[0] == "all" and len(keys) <= 2, fid
    tier_of = {f["id"]: f["tier"] for f in d["features"]}
    ones = {x["key"]: x for x in d["count"]["milestones"]}
    assert set(ones["M1"]["ids"]) == {i for i, t in tier_of.items() if t == 1}
    assert set(ones["M3"]["ids"]) == {i for i, t in tier_of.items() if t == 3}


def test_colour_is_state_three_states(board) -> None:
    """Green = passes end to end on the current code; amber = built, not yet proven — including
    proven only on earlier code; grey = not started (a stub). No fourth state, no outline, no number."""
    d, page = board
    st = F.status(F.load(), F.results())
    for f in d["features"]:
        assert f["status"] in ("green", "amber", "grey"), f["id"]
        assert (f["status"] == "green") == (st[f["id"]] == "passing" and not f["not_e2e"]), f["id"]
        if f["awaiting"] or f["not_e2e"]:
            assert f["status"] == "amber", f["id"]
        if f["status"] == "grey":
            assert f["stub"], f["id"]
    for cls, fid, _, tip in _TILE.findall(page):
        assert cls in ("green", "amber", "grey"), fid
        assert tip.startswith(f"{fid} — "), fid                                # id + one line
    assert " m1" not in page and "awaiting'" not in page and "◷" not in page


def test_the_page_has_the_new_layout_and_not_the_retired_sections(board) -> None:
    """Every section that counted the same features apart is gone (founder 2026-09-30). The
    embedded progress-data keeps rule 10's headline; what the page SHOWS is checked."""
    _, page = board
    shown = re.sub(r"<script.*?</script>", "", page, flags=re.S)
    for block in ('data-key="built-on"', "every number from one count", "class=\"tabs\"", "class=\"ms\"",
                  ">Belt journey</h2>", 'data-key="guide"', ">Next up</h2>", ">Selected tile</h2>", "What's left · "):
        assert block in page, block
    for retired in ("Define complete", "Now per lane", "Waiting for you", "Prompt flow", "Burn-up per milestone",
                    "Last commits", "Value stream</h2>", "<tfoot>", "data-list=", "order of work (#1 = next)",
                    "outline = M1", "M1 — must work for one Belt", "the other must-haves", "should- and could-haves",
                    "awaiting fresh run", "next package", "health"):
        assert retired not in shown, retired


def test_rule_10_reads_the_rendered_page_back_as_true(board) -> None:
    _, page = board
    assert check_board.check(page, None) == []


def test_the_rows_carry_the_founders_plain_names(board) -> None:
    _, page = board
    for name, gloss in (("Screens", "What the Belt sees"), ("Access &amp; files", "Sign-in, roles, uploads"),
                        ("Coaching", "How the coach teaches and checks"), ("Gate", "Report checks and approval"),
                        ("Data &amp; audit", "History, revisions, what is kept"), ("Platform", "Security, errors, logging")):
        assert f"<div class='lay'>{name}<small>{gloss}</small></div>" in page, name
    blob = _blob(page)
    assert blob["stages"] == dict(bcb.STAGES) and blob["layers"] == {k: n for k, n, _ in bcb.LAYERS}


def test_no_code_names_in_the_labels(board) -> None:
    """Plain language (founder 2026-09-30): no tier or lane in what the page shows; milestone codes
    only in the buttons' small text. The features' own descriptions are content, not labels."""
    d, _ = board
    page = bcb.render({**d, "features": [{**f, "description": "x"} for f in d["features"]]})
    shown = re.sub(r"<script.*?</script>|<style>.*?</style>", "", page, flags=re.S)
    assert not re.search(r"(?i)\btier\b|\blane\b", shown)
    assert re.search(r"(?i)\btier\b|\blane\b", bcb.JS) is None


def test_the_page_is_self_contained() -> None:
    """C5: no external font, script or style."""
    page = bcb.render(bcb.data())
    assert "<link" not in page and "@import" not in page and "url(" not in page
    assert not re.search(r"<script[^>]+src=", page)
    assert "IBM Plex" not in page


# ── the pilot cut, the default milestone, Next up — independent of today's records ────────────


def _row(fid: str, tier: int | None, status: str, rank: int | None = None, **kw) -> dict:
    return {"id": fid, "tier": tier, "status": status, "rank": rank, "layer": kw.get("layer", "screen"),
            "held": kw.get("held"), "hidden": kw.get("hidden", False), "pilot": kw.get("pilot")}


def test_until_the_pilot_cut_is_ruled_m2_is_one_button(board) -> None:
    d, page = board
    rows = [_row("A", 1, "green"), _row("B", 2, "grey", 1, pilot=True), _row("C", 2, "amber", 2)]
    c = bcb.count(rows)
    assert [x["key"] for x in c["milestones"]] == ["all", "M1", "M2", "M3"] and not c["pilot_ruled"]
    assert c["milestones"][2]["name"] == "Must-haves"
    if not d["count"]["pilot_ruled"]:
        assert "data-ms='M2'" in page and f"{bcb.PILOT_NOT_RULED}." in page
        assert "Ready for pilot</b>" not in page and "Before customers</b>" not in page


def test_once_ruled_m2_splits_into_ready_for_pilot_and_before_customers() -> None:
    rows = [_row("A", 1, "green"), _row("B", 2, "grey", 2, pilot=True), _row("C", 2, "amber", 1, pilot=False),
            _row("D", 2, "green", pilot=True), _row("E", 3, "grey", 3)]
    c = bcb.count(rows)
    ms = {x["key"]: x for x in c["milestones"]}
    assert c["pilot_ruled"] and list(ms) == ["all", "M1", "M2-pilot", "M2-later", "M3"]
    assert (ms["M2-pilot"]["name"], ms["M2-later"]["name"]) == ("Ready for pilot", "Before customers")
    assert (ms["M2-pilot"]["total"], ms["M2-pilot"]["done"], ms["M2-later"]["total"]) == (2, 1, 1)
    rows[2]["pilot"] = None                                  # one M2 feature without it: not ruled
    assert [x["key"] for x in bcb.count(rows)["milestones"]] == ["all", "M1", "M2", "M3"]


def test_a_pilot_field_is_true_or_false() -> None:
    f = {**F.load()[0], "pilot": "yes"}
    assert any("pilot 'yes' is not true or false" in p for p in R.problems([f]))
    assert not any("pilot" in p for p in R.problems([{**F.load()[0], "pilot": False}]))


def test_the_default_is_the_first_milestone_not_complete() -> None:
    done_m1 = [_row("A", 1, "green"), _row("B", 2, "grey", 1), _row("C", 3, "grey", 2)]
    assert bcb.count(done_m1)["default"] == "M2"
    assert bcb.count([_row("A", 1, "amber", 1), _row("B", 2, "grey", 2)])["default"] == "M1"
    assert bcb.count([_row("A", 1, "green"), _row("B", 2, "green")])["default"] == "all"


def test_next_up_is_the_first_five_open_in_the_order_of_work_never_a_held_one() -> None:
    rows = [_row(f"F{i}", 2, "grey", rank=10 - i) for i in range(8)] + [_row("H", 2, "grey", 0, held="ADR-0071")]
    m2 = next(x for x in bcb.count(rows)["milestones"] if x["key"] == "M2")
    assert m2["next"] == ["F7", "F6", "F5", "F4", "F3"]
    assert m2["left"][0] == "H"


def test_a_milestone_selects_its_tiles_and_its_list() -> None:
    js = bcb.JS
    assert "t.classList.toggle('fade',!t.dataset.ms.split(' ').includes(k))" in js
    assert "s.hidden=s.dataset.for!==k" in js and "location.hash" in js
    assert "document.getElementById('detail').innerHTML=feature(id)" in js


def test_the_phase_tabs_follow_the_registry(board) -> None:
    d, page = board
    assert d["phases"] == [p for p in bcb.PHASES if any(f.get("phase") == p for f in F.load())]
    for p in bcb.PHASES:
        if p not in d["phases"]:
            assert f"<span class='tab off'>{p.capitalize()} · not started</span>" in page, p


def test_waiting_on_you_reads_its_file_and_an_empty_file_hides_the_box(tmp_path, board) -> None:
    d, page = board
    f = tmp_path / "w.md"
    f.write_text("# Waiting on you\n\nprose\n\n- Rule `x`\n- \n", encoding="utf-8")
    assert bcb.waiting_on_you(f) == ["Rule `x`"]
    f.write_text("# Waiting on you\n", encoding="utf-8")
    assert bcb.waiting_on_you(f) == [] and bcb.waiting_on_you(tmp_path / "none.md") == []
    assert ("<h2>Waiting on you</h2>" in page) == bool(d["waiting"])
    empty = bcb.render({**d, "waiting": []})
    assert "Waiting on you" not in empty


# ── founder ruling 1, 2026-09-29 — proven on earlier code, awaiting a fresh run ─────────────


def test_an_awaiting_tile_is_a_run_through_feature_the_latest_record_proved(board) -> None:
    """Awaiting is never a failing test elsewhere, never a passing one; on the board it is built."""
    d, _ = board
    st = F.status(F.load(), F.results())
    for f in d["features"]:
        if not f["awaiting"]:
            continue
        t = F.node_id(f["test"])
        assert st[f["id"]] != "passing", f["id"]
        assert t.startswith(F.RUNTHROUGH_TESTS) or t in F.WALLCLOCK_TESTS, f["id"]
        assert f["status"] == "amber" and f["blocker"].startswith("a fresh run-through"), f["id"]


def test_awaiting_is_display_only_the_landing_rule_stays_strict(monkeypatch) -> None:
    """The rule for landing (guard rule 11) and stop condition 7 read `status` — never awaiting."""
    rt = F.RUNTHROUGH_TESTS + "test_run_x"
    feats = [{"id": "R-1", "test": rt, "depends_on": []}, {"id": "R-2", "test": "backend/tests/t.py::t", "depends_on": []},
             {"id": "R-3", "test": F.RUNTHROUGH_TESTS + "test_run_y", "depends_on": []}]
    res = {"outcomes": {rt: "skipped", "backend/tests/t.py::t": "failed"}}
    monkeypatch.setattr(F, "runthrough_fresh", lambda: False)
    monkeypatch.setattr(F, "earlier_proof", lambda: {rt: "passed", F.RUNTHROUGH_TESTS + "test_run_y": "failed"})
    st = F.status(feats, res)
    assert F.awaiting(feats, st) == {"R-1"}
    assert F.landing_refusal("R-1", feats, res)                       # still refused
    assert F.milestone_split(["R-1", "R-2", "R-3"], st, {"R-1"}) == {"total": 3, "proven": 0, "awaiting": 1, "open": 2}
    monkeypatch.setattr(F, "runthrough_fresh", lambda: True)           # a fresh record: its own verdict
    assert F.awaiting(feats, st) == set()


def test_a_feature_held_by_its_adr_is_never_a_lanes_top() -> None:
    """Founder 2026-09-28: held features stay on the board, but no lane takes one. Independent of
    today's records: with ADR-0071 read as PROPOSED, R7's features are held and no lane takes one."""
    import adrs
    records = {n: dict(r) for n, r in adrs.load().items()}
    records["0071"]["status"] = "PROPOSED"
    feats, reqs = F.load(), F.requirements()
    hold = R.held(feats, reqs, records)
    assert hold and set(hold.values()) == {"ADR-0071"}
    ranked = [{**r, "held": hold.get(r["id"])} for r in R.rank(feats, F.results(), reqs)]
    nxt = R.next_per_lane(ranked)
    assert not hold.keys() & {i for i in nxt.values() if i}
