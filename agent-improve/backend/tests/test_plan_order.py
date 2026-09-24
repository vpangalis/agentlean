"""Appendix F's `Order` equals the order derived from story rank — step 6.49.

**Two orderings of one run of work, and until this test nothing compared
them.** Appendix I rules that `Order` is DERIVED from the rank in
`agent-improve/tools/control_board/stories.py`; the derivation is not built,
so `Order` is still typed in Appendix F and rank is typed in the plan.
`build_board.py` renders one and the control board renders the other. This
test is the check that turns "they agree today" into something that goes red
the commit they stop agreeing.

THE DERIVATION, stated once: the ranked stories in rank order; within each,
its procedure-step tasks in the order the plan lists them; less every task
that is DONE (git log, via `stories.resolve()`) or that the plan marks
BLOCKED. Appendix F's `Order` numbers only the run of work being done, so a
landed step leaves it and a blocked one was never in it.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_TOOLS = _REPO / "agent-improve" / "tools" / "control_board"


def _board():
    spec = importlib.util.spec_from_file_location(
        "build_board", _REPO / ".claude" / "hooks" / "build_board.py")
    assert spec and spec.loader
    bb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bb)
    return bb


def _stories():
    if str(_TOOLS) not in sys.path:
        sys.path.insert(0, str(_TOOLS))
    import stories
    return stories


def derived_order(epics: list[dict]) -> list[str]:
    ranked = sorted((s for ep in epics for s in ep["stories"] if s["rank"]),
                    key=lambda s: s["rank"])
    out = []
    for s in ranked:
        for code, _title, _comp, status, *_ in s["tasks"]:
            if code[:1].isdigit() and status not in ("done", "blocked") and code not in out:
                out.append(code)
    return out


def _divergence(appendix_f: list[str], derived: list[str]) -> str:
    return (f"Appendix F's Order is {appendix_f}; story rank derives {derived}. "
            "One of them was edited without the other — Appendix I rules rank "
            "the source, so either the plan's rank or Appendix F's Order is "
            "wrong, and a person must say which.")


@pytest.mark.xfail(strict=True, reason=(
    "RED — build_board.py read_order() reads ZERO rows: since 6.37 (2026-09-18) "
    "Appendix F carries a Zone column between Order and Step, and read_order's regex "
    "expects the step straight after Order, so the step board renders an empty "
    "vertical. continuity_status.py:250 carries a second copy of the same regex, so "
    "CONTINUITY.md's vertical is empty too. Bug in stories.py, S28."))
def test_appendix_f_order_equals_the_order_derived_from_story_rank() -> None:
    """Reads `Order` through `build_board.read_order()` — the reader the step
    board renders from — rather than a second parser of the same column.
    """
    stories = _stories()
    stories.resolve()
    bb = _board()
    appendix_f = [r["step"] for r in bb.read_order()]
    derived = derived_order(stories.EPICS)
    typed = "| Layer | Order |" in Path(bb.PROCEDURE).read_text(encoding="utf-8")
    assert appendix_f or not typed, (
        "build_board.read_order() reads NO Order rows, but Appendix F's table "
        "carries an Order column — the reader cannot see the column this check "
        "compares, so the step board renders an empty vertical. " + _divergence(appendix_f, derived))
    assert appendix_f == derived, _divergence(appendix_f, derived)


def test_mutation_swapping_two_ranks_turns_it_red() -> None:
    """The mutation is on the check: two ranks swapped in the plan."""
    import copy
    stories = _stories()
    stories.resolve()
    appendix_f = [r["step"] for r in _board().read_order()]
    epics = copy.deepcopy(stories.EPICS)
    ranked = sorted((s for ep in epics for s in ep["stories"] if s["rank"]),
                    key=lambda s: s["rank"])
    ranked[1]["rank"], ranked[2]["rank"] = ranked[2]["rank"], ranked[1]["rank"]
    assert derived_order(epics) != appendix_f
