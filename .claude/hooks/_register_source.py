#!/usr/bin/env python3
"""WHERE the gap register and the BUILT markers live — while they live in two.

**TEMPORARY. THIS FILE IS DELETED AT STEP 6.38.** Every reader below is
expected to read ONE document by then; a permanent dual-read is two sources of
truth, which is the condition the repartition exists to end. The step number
is named here and not left as "later" because a deadline with no step renders
nowhere and is scheduled by nothing — §66's own words about a gap, applied to
a piece of scaffolding.

WHY THIS FILE EXISTS — THE CHICKEN AND THE EGG
----------------------------------------------
The founder's 2026-09-18 ruling moves the gap register, the BUILT markers and
the as-is/to-be view out of `ARCHITECTURE.md` and into
`REFACTORING_PROCEDURE.md`. **The commit that performs that move cannot be
committed while the readers only know the old location.**

`commit-msg-refactor-guard.py` rule 8 resolves a `Gap: G-nn` trailer against
§66's register **read from the git INDEX**. The migration commit stages an
`ARCHITECTURE.md` with §66 removed and a `REFACTORING_PROCEDURE.md` with §66
added. Rule 8, looking only at `ARCHITECTURE.md`, finds an empty register,
every declared gap number fails to resolve, and the guard refuses the commit —
**the guard blocks the edit that would teach it where to look.**

`--no-verify` is the obvious way out and is the wrong one: it is the escape
hatch the whole guard design assumes is never used for convenience, and using
it here would move the register in a commit that no rule inspected.

**So the readers learn both locations FIRST, in a commit that moves no
content**, and the migration then lands under a guard that can still see what
it is checking. This is the same ordering `_fact_owners.py` used when the
ownership registry moved: teach the reader, then move the fact.

THE ORDER IS PREFERENCE, NOT FALLBACK-ON-ERROR
-----------------------------------------------
`REGISTER_SOURCES` is in preference order and the procedure is first.

A reader takes the FIRST definition it finds for a key — a G-number, or the
section a marker sits under — so once a row exists in the procedure that row
wins, and the copy left behind in `ARCHITECTURE.md` cannot contradict it. **A
union that let either document win would make the migration unverifiable**:
a half-moved register would resolve everything from both halves and nothing
would report that the move was incomplete.

**Rule 8 is the one deliberate exception and it takes the UNION.** It answers
*does this gap number exist at all*, and a number that resolves in either
document is scheduled by something. Refusing a commit because a gap is still
registered in the document it has not been moved out of yet is precisely the
deadlock above, one level down.

NOT A READER'S JOB
------------------
This module owns WHERE to look and in WHAT ORDER. It does not parse. The two
§66 parsers in this repository use **deliberately different row regexes** —
the guard's tolerates a struck-through `~~**G-52**~~` because a closed gap is
still a number that resolves, and `build_board.py`'s does not because a closed
gap must not render against a live defect. Centralising the parse would force
one of those two to be wrong.
"""
from __future__ import annotations

from typing import Callable, Iterator

#: Repo-relative, because the two roots in this tree are a real trap:
#: `.claude/` sits ABOVE `agent-improve/`. `verify_built.py`'s anchor
#: evaluator carries the same note and the same five false FAILs behind it.
PROCEDURE_REL = "agent-improve/docs/REFACTORING_PROCEDURE.md"
ARCHITECTURE_REL = "agent-improve/ARCHITECTURE.md"

#: Preference order. The procedure is the destination; ARCHITECTURE.md is
#: where the content still is until step 6.37 moves it.
REGISTER_SOURCES: tuple[str, ...] = (PROCEDURE_REL, ARCHITECTURE_REL)

#: The step that deletes this module and leaves every reader on one document.
REMOVED_BY_STEP = "6.38"


def texts(read: Callable[[str], str]) -> Iterator[tuple[str, str]]:
    """`(rel_path, text)` for each source that has content, in preference order.

    `read` is supplied by the caller because the two callers read from
    different places and must keep doing so: `build_board.py` reads the working
    tree, and the commit guard reads the **git index**, so that a commit which
    registers a gap and adds the file that gap schedules resolves against the
    version being committed rather than the version on disk.

    **A source that cannot be read is skipped, not fatal.** During the
    migration either document may legitimately lack the section a given reader
    wants, and an exception here would turn "the content has moved" into a
    crash in a generator that is required to fail soft.
    """
    for rel in REGISTER_SOURCES:
        try:
            text = read(rel)
        except Exception:                                # noqa: BLE001
            continue
        if text:
            yield rel, text
