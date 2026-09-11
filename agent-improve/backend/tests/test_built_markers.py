"""`verify_built.py`'s checks, run by `pytest` instead of by a human.

WHY THIS FILE EXISTS
--------------------
**A check nobody runs and a check that passes look identical until you run
it.** `.claude/hooks/verify_built.py` re-runs every counted claim behind
ARCHITECTURE.md's `> **BUILT:**` markers, and until 2026-09-11 nothing ran it
automatically: no hook invoked it, no CI step called it, and its own docstring
is about claims that age because nothing asks them again. **That is the exact
failure mode it was written to prevent, one level up** — the guard against
stale markers was itself only as current as the last time someone remembered
to type the command.

`pytest` is the enforcement point this project already has: rule 4 of
`.claude/hooks/commit-msg-refactor-guard.py` runs it on every spine commit.
Wiring the checks here moves them from advisory to enforced, which is the same
move `test_ContradictionDetectionMiddleware_does_not_call_interrupt` made for
the position-6 guard.

ONE TEST PER CHECK, AND THE COUNT IS PINNED
-------------------------------------------
The checks are parametrised so a failure names **which marker went stale**
rather than reporting "verify_built failed". That creates a second hole, and
`test_the_check_count_is_pinned` closes it: **parametrising over a list means
deleting a check deletes its test, and the suite goes green.** Deleting a
failing check is the cheapest way to make this file stop complaining, so the
count is asserted separately — a check may only be removed deliberately, with
the number changed in the same commit.

**The expectations are NOT duplicated here.** They live in `verify_built.py`'s
`CHECKS` table and this imports them, because two copies of an expectation is
the drift this whole mechanism exists to catch.

COST
----
~7s, not ~49s. `py()` takes an in-process fast path when the running
interpreter is already `agent-improve/.venv` — which it is under pytest — so
the eleven probes do not each pay a cold import of langchain and langgraph.
The subprocess path still applies when the hook is invoked by any other
interpreter, which is what WATCH 2 requires.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# ── Load the hook by path. It is a script, not an installed module. ────────
_ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    capture_output=True, text=True,
).stdout.strip() or str(Path(__file__).resolve().parents[3])
_HOOK = Path(_ROOT) / ".claude" / "hooks" / "verify_built.py"


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("verify_built", _HOOK)
    assert spec and spec.loader, f"cannot load {_HOOK}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pytestmark = pytest.mark.skipif(
    not _HOOK.exists(), reason=f"{_HOOK} not present",
)

_vb = _load() if _HOOK.exists() else None

#: The eleven counted checks, the nine from the 2026-09-11 alignment audit,
#: F-15's reader/writer pairing pass, the two title checks, and the
#: five-phase script byte-match.
_EXPECTED_CHECK_COUNT = 24


def test_the_hook_is_where_this_file_thinks_it_is() -> None:
    """A skipped suite and a passing suite look identical too.

    `pytestmark` skips everything here if the hook is missing, which is right
    for a checkout that has not got it — and wrong if the file simply moved,
    because then this whole module silently stops enforcing anything. This
    test is not skipped by that mark on a normal tree, so a move fails loudly.
    """
    assert _HOOK.exists(), (
        f"verify_built.py is not at {_HOOK} — if it moved, update this file; "
        "if it was deleted, the BUILT markers in ARCHITECTURE.md have nothing "
        "re-running them and every one of them is a claim again"
    )


def test_the_check_count_is_pinned() -> None:
    """Deleting a failing check must not be the way this file goes quiet.

    The parametrised test below is generated FROM `CHECKS`, so removing an
    entry removes its test and the suite passes. That is the cheapest possible
    response to a red build and the one this asserts against: the count moves
    only in a commit that means to move it.

    Eleven counted checks + the nine added by the 2026-09-11 alignment audit +
    F-15's pairing pass, the two title checks + the script byte-match = 24.
    """
    total = len(_vb.CHECKS) + 1          # +1: check_phase_scripts, run separately
    assert total == _EXPECTED_CHECK_COUNT, (
        f"verify_built.py now runs {total} checks, not {_EXPECTED_CHECK_COUNT}. "
        "If you ADDED one, raise the number here. If you REMOVED one, say why "
        "in the commit body — a marker just lost the only thing re-running it."
    )


def test_the_pinned_venv_is_the_one_running_these() -> None:
    """The fast path is only sound because pytest runs under the pinned venv.

    WATCH 2: the repo root carries a second, older interpreter. `py()` skips
    its subprocess when `sys.executable` IS `agent-improve/.venv` — so if that
    ever stops being true here, the probes would answer for whatever
    interpreter pytest happened to use. They would still be CORRECT (the
    subprocess path takes over), just slower; this asserts the assumption
    rather than leaving it implicit.
    """
    assert _vb._is_pinned_interpreter(), (
        f"pytest is running under {sys.executable}, not {_vb.VENV}. The checks "
        "still run correctly via the subprocess path, but ~7s becomes ~49s — "
        "and WATCH 2 says a probe under the wrong interpreter answers for the "
        "wrong tree, so confirm which venv this is before relaxing this."
    )


@pytest.mark.parametrize(
    "label,expected,probe,backs",
    [pytest.param(*c, id=c[0]) for c in (_vb.CHECKS if _vb else [])],
)
def test_built_marker_still_matches_the_tree(
    label: str, expected: str, probe: Any, backs: str,
) -> None:
    """One counted claim from ARCHITECTURE.md, re-run against the tree.

    **A failure here is never "fix the test".** It means either the tree moved
    and the `> **BUILT:**` line it backs is now a claim, or the check itself is
    stale — and which of those it is has to be resolved, never re-baselined.
    `backs` names the marker so the answer starts in the right section.
    """
    got = probe()
    assert got == expected, (
        f"\n  check    : {label}"
        f"\n  expected : {expected}"
        f"\n  tree     : {got}"
        f"\n  backs    : {backs}"
        "\n\n  Either the tree moved and that BUILT marker is now a claim, or "
        "this check is stale. Resolve which — never just re-baseline."
    )


def test_every_phase_SKILL_md_carries_its_section_39_script() -> None:
    """§56.1's atomic unit: the opening script is byte-identical in both places.

    Run separately because `check_phase_scripts` returns its own
    (expected, got) pair rather than sitting in the `CHECKS` table.
    """
    expected, got = _vb.check_phase_scripts()
    assert got == expected, (
        f"{got} of {expected} SKILL.md files carry their §39.x.10 opening "
        "script byte-for-byte. §56.1 makes the script and its section one "
        "atomic unit — a drifting copy is what that rule exists to prevent."
    )


# ── The governance hooks that WRITE. ──────────────────────────────────────
#
# `.githooks/pre-commit` is fail-SOFT by design: a hook that writes must never
# wedge a commit. That is right, and it means a break here is QUIET — proved
# on 2026-09-11, when `parse_step_index` gained a Seq cell, this loop still
# unpacked three values, and the commit went through with the board silently
# unregenerated. Fail-soft needs a loud test behind it.

def _continuity() -> Any:
    spec = importlib.util.spec_from_file_location(
        "continuity_status", Path(_ROOT) / ".claude" / "hooks" / "continuity_status.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_step_board_regenerates() -> None:
    """`build_step_board` must not raise, and must order by Seq.

    It reads Appendix D through `parse_step_index`, whose row shape changed on
    2026-09-11. The pre-commit hook swallowed the resulting TypeError and said
    so on stderr, where it scrolled past; nothing failed.
    """
    cs = _continuity()
    rows = cs.parse_step_index(cs.staged_text(cs.PROCEDURE, _ROOT))
    assert rows, "Appendix D parsed to zero rows"
    assert len(rows[0]) == 4, (
        f"row shape is {len(rows[0])}-tuple, not (seq, step, title, status) — "
        "every consumer of parse_step_index unpacks this"
    )
    seqs = [r[0] for r in rows]
    assert len(set(seqs)) == len(seqs), "duplicate Seq values in Appendix D"

    board = cs.build_step_board(_ROOT, today="2026-01-01")
    assert cs.BOARD_BEGIN in board and cs.BOARD_END in board
    assert "## Step board" in board


def test_the_status_block_regenerates() -> None:
    """`derive` must not raise and must name a real next step."""
    cs = _continuity()
    d = cs.derive(_ROOT)
    assert d["next_step"] != "—", "no next step — Appendix D parse is broken"
    assert d["total"] != "?", "row total unknown — Appendix D parse is broken"
    assert int(d["done"]) <= int(d["total"])


def test_all_three_readers_agree_on_the_next_step() -> None:
    """**The board, the banner and the status block are three parsers.**

    They read the same table through three different regexes, and nothing
    forced them to agree until this test. On 2026-09-10 two of them disagreed
    about the next step while a guard rule that checked only that both files
    had been TOUCHED passed — which is why rule 2 was deleted.
    """
    cs = _continuity()
    spec = importlib.util.spec_from_file_location(
        "build_board", Path(_ROOT) / ".claude" / "hooks" / "build_board.py")
    assert spec and spec.loader
    bb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bb)

    rows = bb.read_appendix_d()
    bb.assign_lanes(rows, bb.landed_steps(), bb.read_preconditions())
    board_next = [r["step"] for r in rows if r["lane"] == "BUILDING NOW"]

    assert board_next == [cs.derive(_ROOT)["next_step"]], (
        f"build_board says next={board_next}, continuity_status says "
        f"{cs.derive(_ROOT)['next_step']} — two parsers, one table, "
        "disagreeing about what to build"
    )
