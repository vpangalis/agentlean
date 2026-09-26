"""Appendix F's `Order` column is READ — against the real document — step 6.63.

**The plan read as empty for a week and nothing noticed.** Since 6.37
(2026-09-18) Appendix F carries a Zone cell between `Order` and the step, and
the two copies of the `read_order` regex — `build_board.py` and
`continuity_status.py` — expected the step straight after `Order`. Both read
ZERO rows; the step board and CONTINUITY.md rendered an empty vertical as a
legitimate sentence (the 6.63 card's 8D, fifth cause). The escape: no test
ran a reader against the REAL document, only against fixtures written to
match the regex.

So this file reads the real Appendix F, through every reader that renders
the plan, and fails on an empty one.

**Until 6.63 this file also compared `Order` with an order derived from story
rank in `stories.py`.** That comparison is retired, not weakened: the founder
ruled on 2026-09-25 *"Priority = Appendix F Order column"*, so rank is no
longer a second source of the same fact, and a check that two sources agree
has nothing to compare once there is one.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_TOOLS = _REPO / "agent-improve" / "tools" / "control_board"
_HOOKS = _REPO / ".claude" / "hooks"
_PROCEDURE = _REPO / "agent-improve" / "docs" / "REFACTORING_PROCEDURE.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _progress():
    if str(_TOOLS) not in sys.path:
        sys.path.insert(0, str(_TOOLS))
    import progress
    return progress


def _nonempty_plan(steps: list[str], reader: str) -> list[str]:
    """The assertion every reader is held to. The table carries an `Order`
    column, so an empty result is a reader that cannot see it."""
    text = _PROCEDURE.read_text(encoding="utf-8")
    assert "| Layer | Order |" in text, "Appendix F no longer has an Order column"
    assert steps, (f"{reader} reads NO Order rows from the real Appendix F — the plan "
                   "would render as empty. The 6.63 8D: a Zone cell sits between "
                   "Order and the step.")
    return steps


def test_the_one_reader_returns_the_real_plan() -> None:
    progress = _progress()
    order = _nonempty_plan(progress.read_order(_PROCEDURE.read_text(encoding="utf-8")),
                           "progress.read_order")
    assert "7.9" in order, "Define's last step is not in the plan"


def test_the_step_board_reads_the_same_plan() -> None:
    bb = _load("build_board", _HOOKS / "build_board.py")
    progress = _progress()
    board = _nonempty_plan([r["step"] for r in bb.read_order()], "build_board.read_order")
    assert board == progress.read_order(_PROCEDURE.read_text(encoding="utf-8"))


def test_continuity_reads_the_same_plan(monkeypatch) -> None:
    """`continuity_status` reads the STAGED procedure; pointed at the working
    file here so the comparison is one document, not the index and the tree."""
    cs = _load("continuity_status", _HOOKS / "continuity_status.py")
    monkeypatch.setattr(cs, "staged_text", lambda path, cwd: (_REPO / path).read_text(encoding="utf-8"))
    progress = _progress()
    cont = _nonempty_plan([step for _n, step, *_ in cs.read_order(str(_REPO))],
                          "continuity_status.read_order")
    assert cont == progress.read_order(_PROCEDURE.read_text(encoding="utf-8"))


#: The regex both hooks carried until 6.63, verbatim — kept here as the
#: mutation, so the check above is seen to FAIL on the reader it replaced.
_OLD = re.compile(r"^\|\s*L\d+\s*\|(?P<order>[^|]*)\|\s*\*\*(?P<step>\d+\.\d+)"
                  r"\*\*\s*\|(?P<item>[^|]*)\|(?P<state>[^|]*)\|", re.M)


def test_mutation_the_old_regex_is_refused() -> None:
    text = _PROCEDURE.read_text(encoding="utf-8")
    old = [m["step"] for m in _OLD.finditer(text) if m["order"].strip().isdigit()]
    with pytest.raises(AssertionError, match="reads NO Order rows"):
        _nonempty_plan(old, "the pre-6.63 regex")


def test_a_duplicate_order_number_is_refused() -> None:
    progress = _progress()
    text = _PROCEDURE.read_text(encoding="utf-8")
    first = progress.order_rows(text)[0]
    second = progress.order_rows(text)[1]
    # Renumber the second row's Order to the first's.
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if re.match(r"^\|\s*L\d+\s*\|\s*" + str(second["n"]) + r"\s*\|[^|]*\|\s*\*\*"
                    + re.escape(second["step"]) + r"\*\*", ln):
            lines[i] = re.sub(r"^(\|\s*L\d+\s*\|)\s*\d+\s*\|", rf"\1 {first['n']} |", ln)
            break
    with pytest.raises(ValueError, match=f"Order {first['n']} is on both"):
        progress.order_rows("\n".join(lines))
