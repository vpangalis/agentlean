"""Every reader of the gap register and the BUILT markers reads EITHER document.

WHY THIS FILE EXISTS — STEP 6.36
--------------------------------
The 2026-09-18 founder ruling moves §66's gap register and the 69 `> **BUILT:**`
markers out of `ARCHITECTURE.md` and into `REFACTORING_PROCEDURE.md`. **The
commit that performs the move cannot pass the commit guard unless the guard
already knows both locations**: rule 8 resolves a `Gap: G-nn` trailer against
§66 read from the index, and a migration commit stages an `ARCHITECTURE.md`
with §66 removed. The guard would refuse the edit that teaches it where to look.

So the readers learn both locations in a commit that moves no content, and this
file is what says they did.

**THE FALLBACK IS THE HALF THAT CANNOT BE OBSERVED IN PRODUCTION TODAY.** The
procedure carries no §66 and no markers yet, so every real read resolves
through the fallback and the preferred path is never taken; after step 6.37 the
reverse is true, and neither state exercises both. That is exactly the shape of
coverage that disappears without anyone noticing — G-81, registered 2026-09-15,
is the same failure one level up. Both paths are therefore driven here with
injected documents rather than by waiting for the migration to exercise them.

ONE TEST PER READER, AND THERE ARE THREE READERS
------------------------------------------------
Enumerated from the hooks rather than guessed, per §56's v1.57 precedent:

    commit-msg-refactor-guard.py  `_known_gaps`   — rule 8, §66, from the INDEX
    build_board.py               `read_gaps`      — §66, for the health panel
    build_board.py               `read_markers`   — the `> **BUILT:**` lines

`verify_built.py` and `drift-check.py` are NOT readers of either and are
deliberately absent: `verify_built.py` parses Appendix D and Appendix F, both
already in the procedure, and its `ARCH` constant is unused; `drift-check.py`
reads the governed documents named in `fact_owners.yaml` and parses neither
markers nor §66.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True).stdout.strip()
_HOOKS = Path(_ROOT) / ".claude" / "hooks"


def _hook(name: str, mod: str):
    """Load a hook by path — its filename is not an importable module name."""
    if str(_HOOKS) not in sys.path:
        sys.path.insert(0, str(_HOOKS))
    spec = importlib.util.spec_from_file_location(mod, _HOOKS / name)
    assert spec and spec.loader, f"{name} is not where this file thinks it is"
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def rs():
    return _hook("_register_source.py", "_register_source")


@pytest.fixture(scope="module")
def board():
    return _hook("build_board.py", "build_board")


@pytest.fixture(scope="module")
def guard():
    return _hook("commit-msg-refactor-guard.py", "commit_msg_refactor_guard")


# -- the documents the readers are given, one row and one marker each -------
#
# **Different gap numbers per document on purpose.** A fixture that put the
# same number in both would pass whichever source the reader actually read,
# which is the assertion this file exists to make.
_IN_PROCEDURE = """## 66. The SPEC-GAP register

### 66.6 Closed

| # | Gap | Marked at |
|---|---|---|
| **G-901** | THE PROCEDURE ROW - the preferred location | §1 |

## 3. A section

> **BUILT:** ✅ built · the procedure's own marker · **closes:** `[none]`
"""

_IN_ARCHITECTURE = """## 66. The SPEC-GAP register

### 66.6 Closed

| # | Gap | Marked at |
|---|---|---|
| **G-902** | THE ARCHITECTURE ROW - the fallback location | §2 |

## 4. Another section

> **BUILT:** ☐ not built · the architecture marker · **closes:** `[9.9]`
"""


def _reader(procedure: str = "", architecture: str = ""):
    """A `read(rel)` over injected documents, keyed by the real paths."""
    def read(rel: str) -> str:
        if rel.endswith("REFACTORING_PROCEDURE.md"):
            return procedure
        if rel.endswith("ARCHITECTURE.md"):
            return architecture
        raise AssertionError(f"a reader asked for an unexpected path: {rel}")
    return read


# -- READER 1 - the commit guard's rule 8 ----------------------------------

def test_the_guard_resolves_a_gap_from_the_procedure(guard):
    """The PREFERRED path - where the register is going."""
    got = guard._known_gaps("", read=_reader(procedure=_IN_PROCEDURE))
    assert "G-901" in got


def test_the_guard_resolves_a_gap_from_architecture_md(guard):
    """The FALLBACK path - where the register still is today."""
    got = guard._known_gaps("", read=_reader(architecture=_IN_ARCHITECTURE))
    assert "G-902" in got


def test_the_guard_takes_the_union_and_not_the_first_hit(guard):
    """**Rule 8 is the one reader that unions**, and the reason is the deadlock.

    A gap being moved is registered in one document or the other depending on
    how far the migration has got. Resolving only the preferred document would
    refuse a commit whose gap has not been moved yet - which is the chicken and
    egg this step exists to break, one level down.
    """
    got = guard._known_gaps("", read=_reader(_IN_PROCEDURE, _IN_ARCHITECTURE))
    assert {"G-901", "G-902"} <= got


def test_the_guard_still_resolves_a_real_gap_number_from_the_real_index(guard):
    """Not only the fixtures - the live register still parses."""
    got = guard._known_gaps(_ROOT)
    assert len(got) > 50, f"§66 resolved to {len(got)} gaps"
    assert {"G-52", "G-57", "G-82", "G-86"} <= got, (
        "G-52 is struck through and must still parse; G-82 and G-86 are the "
        "gaps the 2026-09-18 audit found registered but unscheduled")


# -- READER 2 - build_board's gap register read ----------------------------

def test_read_gaps_takes_the_procedure(board):
    got = board.read_gaps(read=_reader(procedure=_IN_PROCEDURE))
    assert "G-901" in got


def test_read_gaps_falls_back_to_architecture_md(board):
    got = board.read_gaps(read=_reader(architecture=_IN_ARCHITECTURE))
    assert "G-902" in got


def test_read_gaps_prefers_the_procedure_when_both_define_a_number(board):
    """**First definition wins, and the procedure is first.**

    A union would make a half-finished migration unverifiable: every gap would
    resolve from both halves and nothing would report the move incomplete.
    """
    both_define = _IN_ARCHITECTURE.replace("G-902", "G-901").replace(
        "THE ARCHITECTURE ROW", "THE STALE COPY LEFT BEHIND")
    got = board.read_gaps(read=_reader(_IN_PROCEDURE, both_define))
    assert "THE PROCEDURE ROW" in got["G-901"]["desc"], (
        "the copy left behind in ARCHITECTURE.md won - the move would be "
        "unverifiable because a stale row could not be distinguished")


def test_read_gaps_yields_nothing_for_a_document_with_no_section_66(board):
    """A missing §66 is the NORMAL state of one document during the move.

    It must not raise: `build_board.main` fails soft, so an exception here
    stops the board regenerating at exactly the commit that moves the register.
    """
    assert board.read_gaps(read=_reader("no register here", "")) == {}


# -- READER 3 - build_board's BUILT-marker read ----------------------------

def test_read_markers_takes_the_procedure(board):
    got = board.read_markers(read=_reader(procedure=_IN_PROCEDURE))
    assert [m["section"] for m in got] == ["§3"]
    assert got[0]["state"] == "built"


def test_read_markers_falls_back_to_architecture_md(board):
    got = board.read_markers(read=_reader(architecture=_IN_ARCHITECTURE))
    assert [m["section"] for m in got] == ["§4"]
    assert got[0]["state"] == "unbuilt" and got[0]["closes"] == ["9.9"]


def test_read_markers_prefers_the_procedure_for_the_same_section(board):
    """One section, two documents, one row - and the procedure's is the one."""
    stale = _IN_ARCHITECTURE.replace("## 4. Another section", "## 3. A section")
    got = board.read_markers(read=_reader(_IN_PROCEDURE, stale))
    assert [m["section"] for m in got] == ["§3"]
    assert got[0]["state"] == "built", "the stale ARCHITECTURE.md marker won"


# -- the output contract - this phase changes plumbing, not the board ------

def test_the_dual_read_returns_exactly_what_the_single_read_returned(board):
    """**The counts the board was built from, unchanged.**

    Measured at the 2026-09-18 audit on `1469d08`: 69 markers of which 30 were
    open, and 75 gap rows. **All three moved at 6.37 and each moved for a
    stated reason**, which is why they are pinned rather than derived:

        69 -> 70  the prose-form marker at §39.1.11 was normalised. No reader
                  had ever matched it, so the register gained a fact the
                  document always carried.
        30 -> 31  that fact is `☐ not built`.
        75 -> 74  **G-19 is struck through at last.** It read `✅ CLOSED by
                  ruling` in its own cell while the row was never struck, so
                  every closure parse that keys on `~~` counted it OPEN and the
                  board rendered a resolved gap as live.
    """
    markers, gaps = board.read_markers(), board.read_gaps()
    assert len(markers) == 70, f"{len(markers)} markers, not 70"
    assert sum(1 for m in markers if m["state"] != "built") == 31
    assert len(gaps) == 74, f"{len(gaps)} gap rows, not 74"


def test_the_dual_read_is_marked_temporary_and_names_the_step_that_ends_it(rs):
    """**A permanent dual-read is two sources of truth**, which is what we end.

    The removing step is asserted to RESOLVE in Appendix D, on rule 8's own
    argument: a number that resolves nowhere schedules nothing, and a deadline
    carried only in a comment renders on no board.
    """
    assert rs.REMOVED_BY_STEP == "6.38"
    appendix_d = (Path(_ROOT) / "agent-improve" / "docs"
                  / "REFACTORING_PROCEDURE.md").read_text(encoding="utf-8")
    assert f"**Commit {rs.REMOVED_BY_STEP}**" in appendix_d, (
        f"step {rs.REMOVED_BY_STEP} removes the dual-read and is in no "
        "register, so nothing schedules the removal")
    for name in ("_register_source.py", "build_board.py"):
        src = (_HOOKS / name).read_text(encoding="utf-8")
        assert rs.REMOVED_BY_STEP in src, (
            f"{name} carries the dual-read without naming the step that ends "
            "it")


def test_the_preference_order_puts_the_destination_first(rs):
    assert rs.REGISTER_SOURCES == (
        "agent-improve/docs/REFACTORING_PROCEDURE.md",
        "agent-improve/ARCHITECTURE.md")
