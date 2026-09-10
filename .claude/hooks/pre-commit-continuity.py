#!/usr/bin/env python3
"""pre-commit hook — regenerate CONTINUITY.md's CURRENT BUILD STATUS block.

Rewrites the block from the STAGED inputs and `git add`s CONTINUITY.md, so the
status block is current on every commit that could have moved it, without
anyone having to remember. The commit-msg guard's rule 5 then verifies the
result on `refactor(arch-v2)` subjects.

WHY HERE AND NOT IN THE GUARD
    Measured in a throwaway repo (2026-08-31): a `git add` from **pre-commit**
    lands in the commit; the same `git add` from **commit-msg** does NOT — the
    commit is written from the tree git already resolved, and the hook's write
    is left behind as a dirty working tree. The second failure mode is the
    dangerous one, because it looks like it worked.

WHEN IT FIRES — EVERY COMMIT, since 2026-09-10
    It used to fire only when a document input was staged (BUILD_TRACKER.md,
    CLAUDE.md, ARCHITECTURE.md), which was sound while every value came from a
    document. **`last completed` and the landed count now come from git log**,
    and git log moves on every commit — including commits that stage none of
    those files. Scoping by staged document would leave the block reporting a
    step behind, with nothing to notice it.

    Two things make firing always cheap: an unchanged block writes nothing,
    and `git add` on an unchanged file adds no entry to the commit. So the
    common case costs one git-log read and produces no diff.

    Rule 2 used to guarantee that a spine commit staged the tracker, which is
    how this hook was guaranteed to run on one. **Rule 2 is gone** — it forced
    two documents to move for a step that no longer needs either — so that
    guarantee had to be replaced rather than quietly inherited.

FAIL-SOFT, DELIBERATELY, AND THE OPPOSITE OF THE GUARD
    This hook WRITES. A writing hook that breaks must not wedge a commit, so
    any internal error exits 0 with a warning and the commit proceeds. That is
    safe precisely because it is not the enforcement point: if this hook fails
    to run, is bypassed, or is not installed, the commit-msg guard's rule 5
    still blocks a refactor commit whose block is stale. Fail-soft writer,
    fail-closed checker.

    It also never touches a file the author did not already have clean: if
    CONTINUITY.md has unstaged edits, the hook leaves it alone and says so,
    rather than folding someone's in-progress prose into this commit.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import continuity_status as cs  # noqa: E402

# Files whose STAGED content feeds the block. Since 2026-09-10 they are no
# longer the whole input: `last completed` and the landed count come from git
# log, which moves on EVERY commit. So this hook no longer early-returns on
# them — see `main`. The set survives for one narrower job: deciding whether to
# stage an UNCHANGED CONTINUITY.md so rule 5 finds it in the index.
TRIGGERS = {cs.PROCEDURE, cs.CLAUDE_MD, cs.ARCH_MD}


def note(msg: str) -> None:
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.stderr.write(f"  [continuity] {msg}\n")
    sys.stderr.flush()


def _git(args: list[str], root: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, capture_output=True, encoding="utf-8", errors="replace",
        cwd=root, timeout=20,
    )


def _write_board(root: str) -> None:
    """Regenerate the step board in REFACTORING_PROCEDURE.md, if it has one.

    Fail-soft like the rest of this hook, and additionally SKIPPED when the
    procedure has unstaged edits — folding someone's in-progress prose into
    this commit is exactly what the CONTINUITY.md guard above refuses to do.
    """
    path = os.path.join(root, cs.PROCEDURE)
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8", newline="") as fh:
        before = fh.read()
    if cs.BOARD_BEGIN not in before:
        return                      # no markers: this file does not carry one

    unstaged = {
        ln.strip().replace("\\", "/")
        for ln in _git(["git", "diff", "--name-only"], root).stdout.splitlines()
        if ln.strip()
    }
    staged = {
        ln.strip().replace("\\", "/")
        for ln in _git(["git", "diff", "--cached", "--name-only"], root).stdout.splitlines()
        if ln.strip()
    }
    if cs.PROCEDURE in unstaged and cs.PROCEDURE not in staged:
        note(f"{cs.PROCEDURE} has unstaged edits — step board NOT regenerated")
        return

    after = cs.splice(before, cs.build_step_board(root),
                      cs.BOARD_BEGIN, cs.BOARD_END)
    if after == before:
        return
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(after)
    _git(["git", "add", "--", cs.PROCEDURE], root)
    note("step board regenerated and staged")


def main() -> int:
    root = _git(["git", "rev-parse", "--show-toplevel"], ".").stdout.strip()
    if not root:
        note("could not locate the repo root — skipped")
        return 0

    staged = {
        ln.strip().replace("\\", "/")
        for ln in _git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"], root
        ).stdout.splitlines()
        if ln.strip()
    }
    # NO EARLY RETURN ON THE TRIGGER SET ANY MORE. `last completed` and the
    # landed count are derived from git log, so every commit can move them —
    # scoping by staged document would leave the block stale after any commit
    # that touched neither Appendix D nor a version line. Regenerating is
    # cheap, and an unchanged block writes nothing.
    path = os.path.join(root, cs.CONTINUITY)
    if not os.path.isfile(path):
        note(f"{cs.CONTINUITY} not found — skipped")
        return 0

    # Never fold someone's unstaged CONTINUITY.md edits into this commit.
    unstaged = {
        ln.strip().replace("\\", "/")
        for ln in _git(["git", "diff", "--name-only"], root).stdout.splitlines()
        if ln.strip()
    }
    if cs.CONTINUITY in unstaged and cs.CONTINUITY not in staged:
        note(f"{cs.CONTINUITY} has unstaged edits — NOT regenerating. "
             "Stage or stash them, then commit again.")
        return 0

    with open(path, encoding="utf-8", newline="") as fh:
        before = fh.read()

    block = cs.build_block(root)
    after = cs.splice(before, block)

    # The STEP BOARD, written into REFACTORING_PROCEDURE.md by this same hook.
    # Same generator, same inputs — so the board and the plan cannot disagree
    # by construction, which is what step 6.16's generator relies on.
    _write_board(root)

    if after == before:
        # Rule 5 wants CONTINUITY.md in the INDEX, not merely correct on disk.
        # Staging an unchanged file adds no entry to the commit, so this is
        # free on the many commits that move nothing.
        if cs.CONTINUITY not in staged and (staged & TRIGGERS):
            _git(["git", "add", "--", cs.CONTINUITY], root)
            note("status block already current — staged CONTINUITY.md")
        return 0

    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(after)
    _git(["git", "add", "--", cs.CONTINUITY], root)

    t = cs.derive(root)
    note(f"status block regenerated and staged — "
         f"last {t['last_step']}, next {t['next_step']}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — fail SOFT; rule 5 is the gate
        note(f"regeneration failed ({exc!r}) — commit proceeding. "
             "The commit-msg guard's rule 5 will block a stale block on a "
             "refactor subject.")
        sys.exit(0)
