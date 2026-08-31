#!/usr/bin/env python3
"""commit-msg hook — the refactor-commit guard.

Blocks a `refactor(arch-v2)` commit unless BOTH hold:

  1. The subject matches the spine format EXACTLY:
         refactor(arch-v2): commit X.Y — <what changed>
     One space after the colon, lowercase "commit", X.Y digits, a real em dash
     (U+2014) with a single space either side, and a non-empty description.
     The session-start hook parses this subject to report "last completed"
     (`_GITLOG_STEP_RE`), and REFACTORING_PROCEDURE.md's completion contract
     fixes the format — a malformed subject silently drops the step out of the
     only automated continuity signal the project has.

  2. `agent-improve/docs/BUILD_TRACKER.md` is staged in the same commit.
     One step = one commit = one tracker row moved. The tracker cannot fall out
     of sync with the code if it must move with it.

NON-refactor commits are not touched — docs, fixes and chores pass through
untouched. See "SCOPE" below; widening it is a one-line change.

WHY commit-msg AND NOT pre-commit
    `pre-commit` runs BEFORE the message exists, so it cannot see the subject
    and rule 1 is unimplementable there. `commit-msg` receives the message file
    as argv[1] and still has the staged index, so it can enforce both rules.
    It runs after pre-commit and before the commit object is written — the
    commit is aborted on a non-zero exit.

FAIL-CLOSED, DELIBERATELY
    The other two hooks in this directory are fail-soft: a SessionStart or
    PreToolUse hook that breaks must never wedge the developer. This one is the
    opposite. A guard that waves the commit through when its own logic breaks is
    "a check that cannot fail" — the failure mode CONTINUITY §7 names as worse
    than no check, because it is recorded as evidence. So an internal error
    BLOCKS and says so. The escape hatch is `git commit --no-verify`, printed in
    every failure message.

Python 3.11+, standard library only. No new dependencies. Read-only.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

# --------------------------------------------------------------------------- #
# Configuration — the two things this guard knows
# --------------------------------------------------------------------------- #

# SCOPE: which commits are checked at all. Both rules apply only to subjects
# that begin with this prefix. Widen by editing this one string — e.g. set it to
# "" to check every commit, which would require a BUILD_TRACKER.md touch on
# doc-only commits too (rejected as the default: the tracker records build
# STEPS, and a docs or hotfix commit advances none).
GUARDED_PREFIX = "refactor(arch-v2)"

# The spine format, fixed by REFACTORING_PROCEDURE.md's completion contract.
# — is spelled as an escape on purpose: a literal em dash here is invisibly
# easy to replace with a hyphen by the same editor slip this rule exists to
# catch.
SUBJECT_RE = re.compile(r"^refactor\(arch-v2\): commit \d+\.\d+ — \S.*$")

# The tracker that must move with the code.
TRACKER_PATH = "agent-improve/docs/BUILD_TRACKER.md"

BYPASS = "git commit --no-verify"


def fail(title: str, *body: str) -> None:
    """Print a blocking message and abort the commit."""
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.stderr.write(f"\n  COMMIT BLOCKED — {title}\n\n")
    for line in body:
        sys.stderr.write(f"  {line}\n")
    sys.stderr.write(f"\n  Bypass (records the drift rather than fixing it): {BYPASS}\n\n")
    sys.exit(1)


def read_subject(path: str) -> str:
    """First non-comment, non-blank line of the commit message file."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped
    return ""


def staged_paths(repo_root: str) -> list[str]:
    """Paths staged for this commit, repo-relative, forward slashes."""
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, encoding="utf-8", errors="replace",
        cwd=repo_root, timeout=10,
    )
    if out.returncode != 0:
        raise RuntimeError(f"git diff --cached failed: {out.stderr.strip()}")
    return [ln.strip().replace("\\", "/") for ln in out.stdout.splitlines() if ln.strip()]


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        fail("guard invoked without a message file",
             "This hook expects the commit-message path as argv[1].",
             "It is a commit-msg hook — it will not work as a pre-commit hook.")

    repo_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, encoding="utf-8", errors="replace", timeout=10,
    ).stdout.strip()
    if not repo_root:
        fail("could not locate the repository root", "`git rev-parse --show-toplevel` returned nothing.")

    # Merge commits carry a generated subject and stage nothing of their own.
    if os.path.exists(os.path.join(repo_root, ".git", "MERGE_HEAD")):
        return 0

    subject = read_subject(argv[1])
    if not subject:
        return 0  # empty message — git aborts on its own, with a better error

    # Everything that is not a spine commit passes through untouched.
    if not subject.startswith(GUARDED_PREFIX):
        return 0

    # ── Rule 1 — the subject format ───────────────────────────────────────
    if not SUBJECT_RE.match(subject):
        hint = []
        # Name the specific slip where we can. A generic "malformed" sends the
        # developer hunting through a regex.
        if re.match(r"^refactor\(arch-v2\): commit \d+\.\d+ [-–] ", subject):
            hint = ["The separator is a HYPHEN or EN DASH. It must be an EM DASH (—, U+2014).",
                    "This is the most common slip and the easiest to miss on review."]
        elif not re.match(r"^refactor\(arch-v2\): commit \d+\.\d+\b", subject):
            hint = ["Expected `commit X.Y` (lowercase, digits) right after the colon.",
                    "`step 2.4`, `Commit 2.4` and a bare `2.4` are all rejected here,",
                    "even though the session-start hook tolerates them on read."]
        else:
            hint = ["The description after the em dash is empty."]
        fail(
            "refactor subject does not match the spine format",
            f"Got:      {subject}",
            "Expected: refactor(arch-v2): commit X.Y — <what changed>",
            "",
            *hint,
            "",
            "Why it matters: the session-start hook parses this subject to report",
            "\"last completed\". A malformed one drops the step out of the only",
            "automated continuity signal the project has, silently.",
        )

    # ── Rule 2 — the tracker moved with the code ──────────────────────────
    try:
        staged = staged_paths(repo_root)
    except Exception as exc:  # noqa: BLE001 — fail CLOSED, see the docstring
        fail("the guard itself failed",
             f"{exc}",
             "Blocking rather than passing: a guard that waves a commit through",
             "when its own logic breaks is worse than no guard.")

    # Case-insensitive: this repo lives on a case-insensitive filesystem, so the
    # tracker can be staged as BUILD_TRACKER.md or build_tracker.md depending on
    # how it was first added.
    want = TRACKER_PATH.lower()
    if not any(p.lower() == want for p in staged):
        fail(
            "the build tracker was not updated in this commit",
            f"Required: {TRACKER_PATH}",
            "",
            f"Staged in this commit ({len(staged)} path(s)):",
            *[f"  - {p}" for p in staged[:20]],
            *(["  … and more"] if len(staged) > 20 else []),
            "",
            "One step = one commit = one tracker row moved. Move this step's row",
            "in the tracker, `git add` it, and commit again.",
        )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — fail CLOSED, see the docstring
        fail("the guard itself crashed", f"{exc!r}",
             "Blocking rather than passing, deliberately.")
