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

WHEN IT FIRES
    Only when one of the block's INPUTS is staged — BUILD_TRACKER.md,
    CLAUDE.md or ARCHITECTURE.md. Those are exactly the files the block is
    derived from, so:

      * every `refactor(arch-v2)` commit qualifies (rule 2 already requires
        the tracker), and
      * an unrelated commit is never silently given an extra file.

    pre-commit cannot read the commit subject — it runs before the message
    exists — so scoping by subject is not available here. Scoping by input is
    better anyway: it fires exactly when the derived values can have changed,
    including on a CLAUDE.md version bump that touches no tracker row.

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

TRIGGERS = {cs.TRACKER, cs.CLAUDE_MD, cs.ARCH_MD}


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
    if not (staged & TRIGGERS):
        return 0                     # nothing that feeds the block moved

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

    if after == before:
        # Still stage it if the commit needs it present (rule 5 wants it in
        # the index, not merely correct on disk).
        if cs.CONTINUITY not in staged:
            _git(["git", "add", "--", cs.CONTINUITY], root)
            note("status block already current — staged CONTINUITY.md")
        return 0

    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(after)
    _git(["git", "add", "--", cs.CONTINUITY], root)

    t = cs.parse_tracker(cs.staged_text(cs.TRACKER, root))
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
