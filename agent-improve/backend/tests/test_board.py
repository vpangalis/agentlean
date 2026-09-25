"""The control board REFUSES what is not true — step 6.63, the brief's item 8.

Each test below is one refusal the founder asked to see, run against the REAL
procedure (or the real page) with one thing broken:

    1  an unregistered step in Order
    2  a step in Order with no Estimate
    3  a card precondition naming a step that does not exist
    4  a landing while a precondition step is only built
    5  a symbol that exists but is unreachable from app.py's routes
    6  the board and CONTINUITY.md disagreeing
    7  a status colour typed by hand
    8  a diagram label that disagrees with the code's configuration

Plus the case every refusal is measured against: the page as generated is
true (`test_the_generated_page_is_true`), so each failure below is caused by
the one thing the test broke and by nothing else.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO = Path(__file__).resolve().parents[3]
_TOOLS = _REPO / "agent-improve" / "tools" / "control_board"
_HOOKS = _REPO / ".claude" / "hooks"
_PROCEDURE = _REPO / "agent-improve" / "docs" / "REFACTORING_PROCEDURE.md"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import progress  # noqa: E402


def _text() -> str:
    return _PROCEDURE.read_text(encoding="utf-8")


def _p(text: str, **kw):
    """`progress()` with no git and no recorded run, unless a test gives them."""
    kw.setdefault("commits", [])
    kw.setdefault("results", {"source_hash": "h", "outcomes": {}})
    kw.setdefault("current_hash", "h")
    return progress.progress(text, **kw)


def _card_precondition(text: str, step: str, value: str) -> str:
    head = text.index(f"\n## Step {step} — ")
    m = re.compile(r"^\| \*\*Precondition\*\* \|.*\|\s*$", re.M).search(text, head)
    assert m, f"{step}'s card has no Precondition row"
    return text[:m.start()] + f"| **Precondition** | {value} |" + text[m.end():]


def _guard():
    spec = importlib.util.spec_from_file_location(
        "commit_msg_guard", _HOOKS / "commit-msg-refactor-guard.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── 1 · 2 · 3 — the plan refuses ─────────────────────────────────────────────


def test_1_an_unregistered_step_in_order_is_refused() -> None:
    text = _text()
    last = max(r["n"] for r in progress.order_rows(text))
    row = f"| L8 | {last + 1} | — | **9.9** | A step nobody registered | ☐ | — | — |\n"
    found = re.search(r"^\| L\d+ \|[^|]*\| — \| \*\*6\.61\*\* \|", text, re.M)
    assert found, "6.61's Appendix F row not found"
    at = found.start()
    broken = text[:at] + row + text[at:]
    problems = _p(broken)["problems"]
    assert "9.9 is in Appendix F's Order but not registered in Appendix D" in problems, problems


def test_2_a_step_in_order_with_no_estimate_is_refused() -> None:
    text = re.sub(r"^\| \*\*6\.61\*\* \| 4 \|", "| **6.61** |  |", _text(), count=1, flags=re.M)
    assert "6.61 is in Order and has no Estimate" in _p(text)["problems"]


def test_3_a_precondition_naming_no_step_is_refused() -> None:
    text = _card_precondition(_text(), "6.61", "9.8 has landed")
    assert "6.61's precondition names 9.8, which is not a registered step" in _p(text)["problems"]


# ── 4 — a landing on a built-only precondition ───────────────────────────────


def test_4_a_landing_while_a_precondition_is_only_built_is_refused() -> None:
    """6.41 is ✅ built and has no wiring proof: built, not wired."""
    guard = _guard()
    text = _card_precondition(_text(), "6.61", "6.41 has landed")
    p = _p(text)
    assert p["steps"]["6.41"]["state"] == "built"
    why = guard.landing_refusal(p, "6.61")
    assert "its precondition 6.41 is built, not wired" in why, why


def test_4d_a_precondition_of_none_names_no_step() -> None:
    """ "none — READY (6.61's Part 0 is committed)" depends on nothing — the
    step in the explanation is context, not a precondition. Found when rule 11
    refused 6.63's own landing on it."""
    card = {"precondition": "none — **READY** (6.61's Part 0 is committed)"}
    assert progress.depends_on("6.63", card, []) == []
    assert progress.depends_on("6.63", {"precondition": "6.61 has landed"}, []) == ["6.61"]


def test_4b_the_landing_rule_blocks_the_commit() -> None:
    guard = _guard()
    with pytest.raises(SystemExit):
        guard.check_landing(str(_REPO), "refactor(arch-v2): commit 9.9 — a step nobody registered")


def test_4c_a_wired_step_is_not_refused_for_itself() -> None:
    """The mutation's other side: the same rule lets a wired step through."""
    guard = _guard()
    wired_test = progress.wiring(_text())["10.0"]["test"]
    p = _p(_text(), results={"source_hash": "h",
                             "outcomes": {progress._nodeid(wired_test): "passed"}})
    assert p["steps"]["10.0"]["wired"], p["steps"]["10.0"]["wired_why"]
    assert not [w for w in guard.landing_refusal(p, "10.0") if w.startswith("10.0 is")]


# ── 5 — a symbol that exists and nothing reaches ─────────────────────────────


def test_5_an_unreachable_symbol_is_refused() -> None:
    import reach
    sym = "backend.phases.define.orchestrate::orchestrate_define"
    assert reach.unreachable([sym]) == [f"{sym} exists and is not reachable from app.py's routes"]
    # …and a wiring claim on it is not WIRED, even with its test passing.
    text = _text().replace(
        "| **6.33** | `backend.tests.test_wiring::test_wired_6_33_a_capture_reaches_the_artifacts` "
        "| `backend.phases.nodes_common::executor` |",
        "| **6.33** | `backend.tests.test_wiring::test_wired_6_33_a_capture_reaches_the_artifacts` "
        f"| `{sym}` |")
    test_id = progress.wiring(text)["6.33"]["test"]
    p = _p(text, results={"source_hash": "h", "outcomes": {progress._nodeid(test_id): "passed"}})
    assert not p["steps"]["6.33"]["wired"]
    assert "not reachable" in p["steps"]["6.33"]["wired_why"]


def test_5b_the_referee_counts_unreachable_wired_symbols() -> None:
    spec = importlib.util.spec_from_file_location("verify_built", _HOOKS / "verify_built.py")
    assert spec and spec.loader
    vb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vb)
    assert vb.wired_symbols_unreachable() == "0"


# ── 9 — the tooling route is for tooling only (founder, 2026-09-25) ──────────


def _touches(text: str, step: str, value: str) -> str:
    head = text.index(f"\n## Step {step} — ")
    m = re.compile(r"^\| \*\*Touches\*\* \|.*\|\s*$", re.M).search(text, head)
    assert m, f"{step}'s card has no Touches row"
    return text[:m.start()] + f"| **Touches** | {value} |" + text[m.end():]


def _claim_tooling(text: str, step: str, test_id: str) -> str:
    at = text.index("\n", text.index("| Step | Wired by | Symbols it claims |") + 1) + 1
    row = f"| **{step}** | `{test_id}` *(tooling)* | — |\n"
    return text[:at] + row + text[at:]


_A_TEST = "backend.tests.test_board::test_the_generated_page_is_true"
_PASSED = {"source_hash": "h", "outcomes": {progress._nodeid(_A_TEST): "passed"}}


def test_9_a_product_step_cannot_claim_the_tooling_route() -> None:
    """6.59 touches backend/ — its own passing test cannot make it done."""
    text = _claim_tooling(_touches(_text(), "6.59", "`phases/nodes_common.py` · `docs/`"), "6.59", _A_TEST)
    p = _p(text, results=_PASSED)
    assert not p["steps"]["6.59"]["done"], p["steps"]["6.59"]
    assert p["steps"]["6.59"]["state"] != "tooling"
    assert any(x.startswith("6.59 claims the tooling route") for x in p["problems"]), p["problems"]


@pytest.mark.parametrize("path", ["`backend/core/graph.py`", "`ui/index.html`", "`core/graph.py`",
                                  "[`core/graph.py:73`](../backend/core/graph.py#L73)"])
def test_9b_every_spelling_of_a_product_path_is_caught(path) -> None:
    assert progress.touches_product(f"`docs/` · {path}"), path


@pytest.mark.parametrize("touches,product", [
    ("`backend/tests/conftest.py` · `backend/tests/` · `tools/control_board/`", False),
    ("`backend/tests/test_x.py` · `backend/core/graph.py`", True),
    ("`backend/tests/` · `backend/`", True),
    ("`backend/tests/` · `ui/index.html`", True),
])
def test_9d_backend_tests_is_not_product_and_nothing_else_is_exempt(touches, product) -> None:
    """Founder, 2026-09-25: backend/tests/ does not count as product code;
    every other path under backend/ or ui/ still does."""
    assert bool(progress.touches_product(touches)) is product, progress.touches_product(touches)


def test_9c_a_pure_tooling_step_is_tooling_and_not_a_capability() -> None:
    text = _claim_tooling(_touches(_text(), "6.59", "`tools/control_board/` · `docs/`"), "6.59", _A_TEST)
    p = _p(text, results=_PASSED)
    st = p["steps"]["6.59"]
    assert (st["state"], st["done"], st["wired"]) == ("tooling", True, False)
    assert p["proven"] == _p(_text(), results=_PASSED)["proven"], "tooling moved the capability count"


# ── 6 · 7 · 8 — the page against the tree ────────────────────────────────────


@pytest.fixture(scope="module")
def board():
    import build_control_board as bcb
    import check_board
    cs_spec = importlib.util.spec_from_file_location("continuity_status", _HOOKS / "continuity_status.py")
    assert cs_spec and cs_spec.loader
    cs: Any = importlib.util.module_from_spec(cs_spec)
    cs_spec.loader.exec_module(cs)
    cs.staged_text = lambda path, cwd: (_REPO / path).read_text(encoding="utf-8")
    m = bcb.model(staged=False)
    return bcb.render(m), m, cs.build_block(str(_REPO)), check_board


def _refusals(board, page=None, continuity=None) -> list[str]:
    page0, m, cont0, check_board = board
    bad = check_board.check(page if page is not None else page0, m,
                            continuity if continuity is not None else cont0)
    return [b for b in bad if not b.startswith("the plan:")]


def test_the_generated_page_is_true(board) -> None:
    assert _refusals(board) == []


def test_6_the_board_and_continuity_disagreeing_is_refused(board) -> None:
    _page, m, cont, _ = board
    other = cont.replace(m["p"]["headline"], "15 of 35 capabilities proven · working on: 6.43")
    bad = _refusals(board, continuity=other)
    assert any("CONTINUITY.md's headline" in b for b in bad), bad


def test_7_a_status_colour_typed_by_hand_is_refused(board) -> None:
    page = board[0]
    typed = page.replace("<h2>", '<span class="st c-green">done</span><h2>', 1)
    assert any("a colour typed by hand" in b for b in _refusals(board, page=typed))
    # …and a keyed status whose colour was edited disagrees with its reference.
    key = next(k for k, v in board[1]["statuses"].items() if v["colour"] == "red")
    flipped = re.sub(r'class="st c-red" data-key="' + re.escape(key) + '"',
                     f'class="st c-green" data-key="{key}"', page, count=1)
    assert flipped != page
    assert any(f"status {key} is green" in b for b in _refusals(board, page=flipped))


def test_8_a_diagram_label_that_disagrees_with_the_code_is_refused(board) -> None:
    """The old typed diagram said the skills were "optional"; the code
    delivers the SKILL.md on every model call. Type the old label back in."""
    page, m = board[0], board[1]
    real = m["labels"]["skills:label"]
    assert "on every model call" in real, real
    typed = page.replace(f'data-key="skills:label">{real}<', 'data-key="skills:label">2 skills — optional<', 1)
    assert typed != page
    bad = _refusals(board, page=typed)
    assert any(b.startswith("label skills:label reads '2 skills — optional'") for b in bad), bad


# ── 6.64 — the grouped views, derived (founder, 2026-09-25) ──────────────────


def test_10_a_step_with_no_container_is_refused() -> None:
    """A registered step with no Appendix F row has no Layer, so no container."""
    text = _text()
    found = re.search(r"^\| L\d+ \|[^|]*\| — \| \*\*6\.62\*\* \|.*\n", text, re.M)
    assert found, "6.62's Appendix F row not found"
    gone = text[:found.start()] + text[found.end():]
    assert "6.62 has no container — it has no Appendix F row, so no Layer" in _p(gone)["problems"]


def test_10b_a_layer_with_no_heading_is_no_container() -> None:
    """A Layer the table does not name is not a container either."""
    text = re.sub(r"^\| L3 (\|[^|]*\| — \| \*\*6\.62\*\* \|)", r"| L9 \1", _text(), count=1, flags=re.M)
    problems = _p(text)["problems"]
    assert any(x.startswith("6.62 has no container — its Appendix F Layer L9") for x in problems), problems


def test_10c_every_registered_step_has_a_container_on_the_real_procedure() -> None:
    p = _p(_text())
    assert not [x for x in p["problems"] if "no container" in x], p["problems"]
    placed = [s for c in p["containers"] for s in c["steps"]]
    assert sorted(placed) == sorted(s for s, st in p["steps"].items() if st["registered"])
    assert len(placed) == len(set(placed)), "a step sits in two containers"
    # The names are the table's headings, never a list typed in the generator.
    assert {c["id"]: c["name"] for c in p["containers"]} == {
        f"L{n}": name for n, name in progress.layers(_text()).items()}


def test_11_a_container_view_that_omits_a_registered_step_is_refused(board) -> None:
    page = board[0]
    assert page.count('data-cv="6.62"') == 1
    dropped = page.replace('data-cv="6.62"', 'data-dropped="6.62"')
    assert "the container view omits registered step 6.62" in _refusals(board, page=dropped)


def test_11b_a_step_under_the_wrong_container_is_refused(board) -> None:
    page, m = board[0], board[1]
    home = m["p"]["steps"]["6.62"]["container"]
    other = next(c["id"] for c in m["p"]["containers"] if c["id"] != home)
    # Move 6.62's row out of its own container's group, to the end of another's.
    row = re.search(r'<div class="wrow" data-cv="6\.62">.*?</div></div></div>', page)
    assert row
    moved = page.replace(row[0], "", 1)
    anchor = f'data-ctr="{other}"'
    at = moved.index("</summary>", moved.index(anchor)) + len("</summary>")
    moved = moved[:at] + row[0] + moved[at:]
    assert f"the container view puts 6.62 under {other}; the tree gives {home}" in _refusals(board, page=moved)


def test_the_three_groupings_are_on_the_page(board) -> None:
    """6.64's own proof (the tooling route): the switch, three views, the
    container view the default; a card per container; every story in the epic
    view; the capabilities grouped by container."""
    import stories
    page, m = board[0], board[1]
    assert re.search(r'<input type="radio" name="wf" id="wf-ctr" class="vsw" checked>', page)
    for view in ("ctr", "wp", "epic"):
        assert f'data-view="{view}"' in page, view
    for c in m["p"]["containers"]:
        assert f'data-ctr="{c["id"]}"' in page
        assert f'data-key="ctr:{c["id"]}"' in page
        assert f'<b>{c["id"]} · {c["name"]}</b>' in page
    view_epic = page[page.index('data-view="epic"'):]
    for ep in stories.EPICS:
        for sto in ep["stories"]:
            assert f'<b>{sto["id"]}</b>' in view_epic, sto["id"]
    for c in m["p"]["containers"]:
        if any(c["id"] in cap["containers"] for cap in m["p"]["capabilities"]):
            assert f'<tr class="grp"><td colspan="4">{c["id"]} · ' in page, c["id"]


def test_12_what_is_there_is_read_from_the_code(board) -> None:
    """A container card's components are labels the check recomputes from the
    code — type one by hand and it is refused, like any diagram label."""
    page, m = board[0], board[1]
    real = m["labels"]["cmp:L5:0"]
    assert real.startswith("1 BeforeModelStateInjection"), real
    typed = page.replace(f'data-key="cmp:L5:0">{real}<', 'data-key="cmp:L5:0">state injection — optional<', 1)
    assert typed != page
    assert any(b.startswith("label cmp:L5:0 reads") for b in _refusals(board, page=typed))


def test_13_no_typed_status_is_left_in_stories() -> None:
    """The bugs' "done" / "todo" / "backlog" were typed; 6.64 deleted them."""
    import stories
    for ep in stories.EPICS:
        for sto in ep["stories"]:
            for bug in sto["bugs"]:
                assert not {"done", "todo", "backlog"} & set(bug), bug


# ── 6.64 — test-results.json: unchanged outcomes leave it untouched ──────────


class _Recorder:
    """The recorder, driven with this test's own outcomes — never by patching
    the session's `_OUTCOMES`, which swallowed this test's report (6.65)."""

    def __init__(self, cf, outcomes: dict[str, str]) -> None:
        self.cf, self.outcomes = cf, dict(outcomes)

    def _record_results(self) -> None:
        self.cf._record_results(self.outcomes)


def _recorder(monkeypatch, tmp_path, outcomes: dict[str, str]):
    from backend.tests import conftest as cf
    path = tmp_path / "test-results.json"
    monkeypatch.setattr(progress, "RESULTS", path)
    return _Recorder(cf, outcomes), path


def test_14_a_run_with_unchanged_outcomes_does_not_rewrite_the_record(monkeypatch, tmp_path) -> None:
    cf, path = _recorder(monkeypatch, tmp_path, {"t::a": "passed"})
    cf._record_results()
    first = path.read_text(encoding="utf-8")
    rec = __import__("json").loads(first)
    assert rec["commit"] and rec["source_hash"] == progress.source_hash()
    path.touch()
    before = path.stat().st_mtime_ns
    cf._record_results()                      # same source, same outcome
    assert path.read_text(encoding="utf-8") == first
    assert path.stat().st_mtime_ns == before, "the file was rewritten for nothing"
    cf.outcomes = {"t::a": "failed"}
    cf._record_results()                      # an outcome changed — written
    assert __import__("json").loads(path.read_text(encoding="utf-8"))["outcomes"]["t::a"] == "failed"


def test_14b_a_record_from_before_6_64_is_written_once_to_carry_its_commit(monkeypatch, tmp_path) -> None:
    import json
    cf, path = _recorder(monkeypatch, tmp_path, {"t::a": "passed"})
    path.write_text(json.dumps({"source_hash": progress.source_hash(),
                                "outcomes": {"t::a": "passed"}, "older": {}}), encoding="utf-8")
    cf._record_results()
    assert "commit" in json.loads(path.read_text(encoding="utf-8"))


def test_14c_a_record_on_older_source_reads_amber() -> None:
    """The amber the commit field must not lose: a pass recorded on another
    source is 'older than the code'."""
    v = progress.verdict("backend.tests.test_board::test_x",
                         {"source_hash": "old", "commit": "abc1234",
                          "outcomes": {"backend/tests/test_board.py::test_x": "passed"}}, "new")
    assert v["colour"] == "amber" and "passed on source old" in v["why"]
