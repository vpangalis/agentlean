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
    """6.61 touches backend/ — its own passing test cannot make it done."""
    text = _claim_tooling(_touches(_text(), "6.61", "`phases/nodes_common.py` · `docs/`"), "6.61", _A_TEST)
    p = _p(text, results=_PASSED)
    assert not p["steps"]["6.61"]["done"], p["steps"]["6.61"]
    assert p["steps"]["6.61"]["state"] != "tooling"
    assert any(x.startswith("6.61 claims the tooling route") for x in p["problems"]), p["problems"]


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
    text = _claim_tooling(_touches(_text(), "6.61", "`tools/control_board/` · `docs/`"), "6.61", _A_TEST)
    p = _p(text, results=_PASSED)
    st = p["steps"]["6.61"]
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
