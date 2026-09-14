#!/usr/bin/env python3
"""commit-msg hook — the refactor-commit guard.

Blocks a `refactor(arch-v2)` commit unless ALL FOUR hold (rules 2b, 6, 7 and 8
bind on EVERY commit, each on its own trigger):

**Rule 2 was DELETED 2026-09-10** and its number is not reused — every other
rule keeps the number it has been referred to by in commit messages, DECISIONS
entries and this file's own prose since 2026-08-31. Renumbering to close the
gap would silently redirect every one of those references. The rules are
therefore 1, 2b, 3, 4, 5, 6, 7 and 8.

  1. SUBJECT — matches the spine format EXACTLY:
         refactor(arch-v2): commit X.Y — <what changed>
     One space after the colon, lowercase "commit", X.Y digits, a real em dash
     (U+2014) with a single space either side, and a non-empty description.
     session-start-context.py parses this subject to report "last completed"
     (`_GITLOG_STEP_RE`); a malformed one silently drops the step out of the
     only automated continuity signal the project has.

  2. ~~TRACKER~~ — **DELETED 2026-09-10.** It required BUILD_TRACKER.md and
     REFACTORING_PROCEDURE.md to be staged together: *one step = one commit =
     one row moved IN BOTH.* BUILD_TRACKER.md no longer exists, and a landing
     step no longer moves a row in Appendix D either — completion is read from
     git log.

     **It was never the check it looked like.** It verified both files were
     TOUCHED, never that they AGREED, and that gap is not theoretical: 6.13
     shipped with the two disagreeing about the next step while this rule
     passed. The real defence was to stop storing the same fact twice.

  2b. STATUS — `agent-improve/ARCHITECTURE.md` is staged whenever
     the commit touches a path that file tabulates (STATUS_WATCHED). **This one
     is NOT scoped to `refactor(arch-v2)`** and runs before the prefix gate:
     a middleware swap lands as a `fix(` as easily as a `refactor(`, and
     scoping it would exempt exactly the commits nobody reviews against the
     spine. Added 2026-09-08 with the file itself.

  3. TYPE-CHECK — mypy over the changed Python, against the PINNED venv, so an
     invented LangGraph/LangChain/LangSmith method or a wrong signature fails
     against the real installed library's types. Ratcheted (see below).

  4. TESTS — pytest green.

  5. CONTINUITY — `agent-improve/docs/CONTINUITY.md` is staged AND its CURRENT
     BUILD STATUS block matches what regeneration from the staged inputs
     produces. CONTINUITY.md is what a new session reads first, and a
     first-read document that lags the build is worse than one that is merely
     terse — it is confidently wrong. Its own title line read `Version 4.7`
     while its header comment said 4.9, which is the drift this ends.

     NORMALLY THIS RULE NEVER FIRES, and that is the design. `.githooks/
     pre-commit` regenerates and stages the block automatically, so by the time
     this runs it is already correct. Rule 5 is the fail-closed backstop for
     the cases where it did not: pre-commit not installed (`core.hooksPath`
     unset in a fresh clone), the script erroring, `git commit --no-verify` on
     an earlier attempt leaving a stale block staged, or a hand-edited block.

  6. 8D — the body of a FIX commit answers **D2 IS, D2 IS-NOT, D4 OCCURRENCE,
     D4 ESCAPE, D5 FIX and D7 PREVENT**. CLAUDE.md §20, founder ruling
     2026-09-11: every defect, modification or adaptation is worked as an 8D
     before a fix is proposed, and *"convention decays; a gate does not"*.

     **NOT scoped to `refactor(arch-v2)`, and not scoped to `fix(` either.**
     Three triggers: the subject's type is a fix; the subject names a registered
     defect (`G-49`, `F-15`, `WATCH 26`); or the body already carries a
     `D<n>` label, which is what stops a half-written 8D from passing. The
     middle trigger — and only that one — can be declined on the record with
     `8D: NOT A FIX — <why>`.

     **D4's two halves are the point.** An occurrence cause with no escape
     cause is the shape that lets the same CLASS of defect return through the
     same blind spot, and §20 names that split as the clause carrying the
     weight. An empty discipline is a finding: `NONE — <reason>` passes, bare
     `NONE` does not.

     It checks that each discipline is ANSWERED, never that the answer is
     right. That limit is written into `check_8d`'s docstring rather than left
     for someone to assume away.

  7. SCRATCH — no path NEW to the tree matches a scratch pattern: a `scratch/`
     or `_drafts/` segment, a `.bak`/`.tmp`/`.old` suffix, a `~$` lock file or
     a OneDrive `conflicted copy`. **CLAUDE.md §0.32, clause 2**: scratch lives
     outside the tree, is never committed, and is never evidence. It reads the
     NAME and never the content, and only paths new to the tree — a ratchet,
     like rule 3, because two `.bak` archives are tracked deliberately.

  8. STEP OR GAP — every path NEW to the tree has a number behind it.
     **CLAUDE.md §0.32, clause 3.** A spine subject declares its own step;
     any other type carries `Step: 6.22` or `Gap: G-57` in the body, and the
     number must RESOLVE — Appendix D for a step, §66's register for a gap,
     both read from the INDEX so a gap registered in the same commit counts.
     It checks that a number is declared and exists, never that the file
     belongs to it: the same limit rule 6 carries, and stated for the same
     reason.

NON-refactor commits are touched by rules 2b, 6, 7 and 8 only. A docs or chore
commit that changes no tabulated path, claims to fix nothing, and adds no file
still passes through untouched.

USAGE
    commit-msg hook:   <guard> <path-to-commit-message-file>
    regenerate rule 3's baseline:   <guard> --update-baseline

WHY commit-msg AND NOT pre-commit
    `pre-commit` runs BEFORE the message exists, so it cannot see the subject
    and rule 1 is unimplementable there. `commit-msg` receives the message as
    argv[1] and still has the staged index, so it can enforce all four. It runs
    after pre-commit and before the commit object is written — a non-zero exit
    aborts the commit.

RULE 3 IS A RATCHET, NOT A WALL
    The v1 tree carries 97 pre-existing mypy errors across 12 files (measured
    2026-08-31). A gate that blocked on all of them would block every commit
    touching core/checkpointer.py or any orchestrate.py from day one — and a
    guard people route around with --no-verify is worse than no guard.
    So: the known errors are recorded in .claude/config/mypy-baseline.txt and
    only errors NOT in that baseline block. Existing debt is visible and
    countable; new debt cannot land. Line numbers are stripped from the
    baseline key so it does not churn when unrelated lines move; the recorded
    COUNT per key still has to not increase, so a second copy of an existing
    error is caught.

THE PINNED VENV IS MANDATORY
    Both checks run against agent-improve/.venv (LangGraph 1.2.11), never
    whatever python is on PATH. WATCH 2: the repo root carries a second, stale
    venv (LangGraph 1.1.10). Type-checking against the wrong one would validate
    against the wrong library and report success. If the pinned venv is
    missing, this guard BLOCKS rather than falling back.

FAIL-CLOSED, DELIBERATELY
    The other two hooks in this directory are fail-soft: a SessionStart or
    PreToolUse hook that breaks must never wedge the developer. This one is the
    opposite. A guard that waves the commit through when its own logic breaks is
    "a check that cannot fail" — the failure mode CONTINUITY §7 names as worse
    than no check, because it is recorded as evidence. So an internal error
    BLOCKS and says so. The escape hatch is `git commit --no-verify`, printed in
    every failure message.

Python 3.11+, standard library only. mypy and pytest are invoked as
subprocesses of the pinned venv; this script imports neither.
"""

from __future__ import annotations

import collections
import fnmatch
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import continuity_status as cs

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

# SCOPE: which commits are checked at all. All four rules apply only to subjects
# beginning with this prefix. Widen by editing this one string — e.g. "" to
# check every commit. Rejected as the default: the tracker records build STEPS,
# and a docs or hotfix commit advances none, so requiring a tracker touch on
# those would train people to bypass the hook.
GUARDED_PREFIX = "refactor(arch-v2)"

# The spine format, fixed by REFACTORING_PROCEDURE.md's completion contract.
# The em dash is written as an escape on purpose: a literal one here is
# invisibly easy to replace with a hyphen by the same editor slip this rule
# exists to catch.
SUBJECT_RE = re.compile(r"^refactor\(arch-v2\): commit \d+\.\d+ — \S.*$")

# `TRACKER_PATH` and `PROCEDURE_PATH` were rule 2's, and went with it.
# Appendix D's location is `continuity_status.PROCEDURE`, which rule 5 reaches
# through `build_block` — this file no longer needs to know it.

# Rule 2b — the architecture panel's repo-side source, and the paths it
# tabulates. Unlike the rest of this guard it is NOT scoped to
# `refactor(arch-v2)` commits: the rule is "whenever a commit changes something
# that file describes", and a middleware swap lands as a `fix(` just as easily
# as a `refactor(`. Scoping it to the prefix would have exempted exactly the
# commits nobody is reviewing against the spine.
# Repointed 2026-09-10: `docs/ARCHITECTURE_STATUS.md` is archived and its
# tables now live as `> **BUILT:**` markers on the items they describe
# (ARCHITECTURE.md §55.2). Same rule, one file.
STATUS_PATH = "agent-improve/ARCHITECTURE.md"

# Deliberately narrow: the twelve paths whose contents are literally tabulated
# in that file. A rule that fired on every backend file gets routed around with
# --no-verify within a week, and a guard people route around is worse than none
# (the same argument that makes rule 3 a ratchet rather than a wall).
STATUS_WATCHED = (
    "agent-improve/backend/core/graph.py",
    "agent-improve/backend/core/state.py",
    "agent-improve/backend/core/substate.py",
    "agent-improve/backend/core/checkpointer.py",
    "agent-improve/backend/core/store.py",
    "agent-improve/backend/middleware/",          # prefix — the whole package
    "agent-improve/backend/phases/subgraph_common.py",
    "agent-improve/backend/phases/nodes_common.py",
    "agent-improve/backend/knowledge/tools.py",
    "agent-improve/backend/knowledge/computation.py",
    "agent-improve/backend/gateway/routes.py",
    "agent-improve/backend/storage/blob.py",
)

# ── `docs/board.html` WAS HERE AND IS REMOVED, 2026-09-14 ─────────────────
#
# **A WATCHED PATH MUST BE A SOURCE OF TRUTH, NEVER THE OUTPUT OF A
# GENERATOR.** That is the rule this list is now held to, and the board broke
# it: `build_board.py` regenerates it from Appendix D, the BUILT markers, §66
# and **git log** during pre-commit.
#
# **Git log moves on every commit, so the board changes on every commit** —
# and because the hook runs BEFORE the commit it is part of exists, the board
# permanently lags one commit and spends every commit catching up with the
# previous one. Rule 2b therefore demanded an `ARCHITECTURE.md` edit on every
# commit, whether or not any architectural fact had changed.
#
# **The entry's own comment argued the opposite and was wrong when written**:
# *"It carries NO wall-clock date precisely so that it changes when, and only
# when, one of those four sources does."* True, and it defeats the point —
# git log IS one of those four sources, and it is the one that moves
# unconditionally. Removing the date removed a clock and left a counter.
#
# **What it cost is on the record**: `ef59aa8`, a `fix(ops)` commit touching
# only `start.ps1`, was blocked and carries an `ARCHITECTURE.md` §56 entry
# written only to satisfy this rule. **A gate that always fires is a gate that
# gets bypassed** — the argument rule 3 is a ratchet for, and rule 2b is
# deliberately narrow for, applied to itself.
#
# **The board is not left unguarded.** `verify_built.py` re-runs the counts
# behind it, which is the check appropriate to a projection: a derived file is
# verified by REGENERATING it and comparing, never by asking whether someone
# remembered to touch a different file in the same commit.

# Everything type-checked and tested lives under this project.
PROJECT = "agent-improve"
VENV_REL = os.path.join(PROJECT, ".venv")
MYPY_INI = os.path.join(PROJECT, "mypy.ini")
TESTS_REL = os.path.join("backend", "tests")
BASELINE_REL = os.path.join(".claude", "config", "mypy-baseline.txt")

# mypy's cache must NOT live under the OneDrive-synced tree: a cold run there
# took 67s versus 4.4s warm, and OneDrive fights the thousands of small cache
# files. Measured 2026-08-31.
CACHE_DIR = os.path.join(tempfile.gettempdir(), "agentlean-mypy-cache")

MYPY_TIMEOUT = 600   # cold run over a large change can exceed a minute
PYTEST_TIMEOUT = 300

BYPASS = "git commit --no-verify"

# Strips "file:LINE: error:" down to a line-number-independent key.
_ERR_RE = re.compile(r"^(?P<file>[^:]+):\d+:(?:\d+:)?\s*error:\s*(?P<msg>.*?)\s*(?P<code>\[[a-z-]+\])?$")


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def _utf8() -> None:
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def note(msg: str) -> None:
    """Progress line — a commit that pauses for 60s must say why."""
    _utf8()
    sys.stderr.write(f"  [guard] {msg}\n")
    sys.stderr.flush()


def fail(title: str, *body: str) -> None:
    _utf8()
    sys.stderr.write(f"\n  COMMIT BLOCKED — {title}\n\n")
    for line in body:
        sys.stderr.write(f"  {line}\n")
    sys.stderr.write(f"\n  Bypass (records the drift rather than fixing it): {BYPASS}\n\n")
    sys.exit(1)


# --------------------------------------------------------------------------- #
# Environment
# --------------------------------------------------------------------------- #
def repo_root() -> str:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, encoding="utf-8", errors="replace", timeout=10,
    ).stdout.strip()
    if not out:
        fail("could not locate the repository root",
             "`git rev-parse --show-toplevel` returned nothing.")
    return out


def venv_python(root: str) -> str:
    """The PINNED interpreter. Blocks rather than falling back — see WATCH 2."""
    for rel in (os.path.join("Scripts", "python.exe"), os.path.join("bin", "python")):
        candidate = os.path.join(root, VENV_REL, rel)
        if os.path.isfile(candidate):
            return candidate
    fail(
        f"the pinned venv is missing: {VENV_REL}",
        "Rules 3 and 4 must run against the PINNED environment (LangGraph 1.2.11),",
        "never whatever python is on PATH. WATCH 2: the repo root carries a second,",
        "stale venv (LangGraph 1.1.10). Type-checking against that one would validate",
        "against the wrong library and report success.",
        "",
        "Create it, or bypass if you know this commit touches no Python.",
    )
    raise AssertionError("unreachable")


def staged_paths(root: str) -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, encoding="utf-8", errors="replace",
        cwd=root, timeout=10,
    )
    if out.returncode != 0:
        raise RuntimeError(f"git diff --cached failed: {out.stderr.strip()}")
    return [ln.strip().replace("\\", "/") for ln in out.stdout.splitlines() if ln.strip()]


def unstaged_python(root: str) -> list[str]:
    """Python files modified but NOT staged — see the caveat in run_mypy."""
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, encoding="utf-8", errors="replace",
        cwd=root, timeout=10,
    )
    return [ln.strip().replace("\\", "/") for ln in out.stdout.splitlines()
            if ln.strip().endswith(".py")]


# --------------------------------------------------------------------------- #
# Rule 3 — type-check
# --------------------------------------------------------------------------- #
def parse_errors(output: str) -> collections.Counter:
    """mypy stdout -> Counter of line-number-independent keys."""
    keys: collections.Counter = collections.Counter()
    for line in output.splitlines():
        m = _ERR_RE.match(line.strip())
        if not m:
            continue
        f = m.group("file").replace("\\", "/")
        keys[f"{f}\t{m.group('code') or '[?]'}\t{m.group('msg')}"] += 1
    return keys


def load_baseline(root: str) -> collections.Counter:
    path = os.path.join(root, BASELINE_REL)
    counts: collections.Counter = collections.Counter()
    if not os.path.isfile(path):
        return counts
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            n, _, key = line.partition("\t")
            try:
                counts[key] = int(n)
            except ValueError:
                continue
    return counts


def run_mypy(root: str, py: str, files: list[str]) -> collections.Counter:
    """Run mypy over `files` (repo-relative) and return the error Counter."""
    proj = os.path.join(root, PROJECT)
    rel = [os.path.relpath(os.path.join(root, f), proj) for f in files]
    os.makedirs(CACHE_DIR, exist_ok=True)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    out = subprocess.run(
        [py, "-m", "mypy", "--config-file", os.path.join(root, MYPY_INI),
         "--cache-dir", CACHE_DIR, "--no-error-summary", "--no-color-output",
         "--hide-error-context", *rel],
        capture_output=True, encoding="utf-8", errors="replace",
        cwd=proj, timeout=MYPY_TIMEOUT, env=env,
    )
    combined = (out.stdout or "") + (out.stderr or "")
    # mypy exits 1 for "errors found" and 2 for "could not run". Only the
    # second is a guard failure; the first is the thing we are measuring.
    if out.returncode not in (0, 1):
        fail("mypy could not run",
             *combined.strip().splitlines()[:15],
             "",
             "Blocking rather than passing: an unrunnable type-check is not a",
             "passing type-check.")
    # Normalise mypy's paths (relative to agent-improve/) back to repo-relative.
    counter: collections.Counter = collections.Counter()
    for key, n in parse_errors(combined).items():
        f, sep, rest = key.partition("\t")
        counter[f"{PROJECT}/{f}{sep}{rest}"] += n
    return counter


def check_types(root: str, py: str, staged: list[str]) -> None:
    changed = [f for f in staged
               if f.endswith(".py")
               and f.startswith(f"{PROJECT}/")
               and os.path.isfile(os.path.join(root, f))]
    if not changed:
        note("rule 3 type-check: no Python changed — skipped")
        return

    # The checks read the WORKING TREE, not the staged index. If Python is
    # modified-but-unstaged, what is checked is not what is committed. Warning
    # rather than blocking, and definitely not stashing: a hook that moves the
    # developer's uncommitted work is how people lose it.
    dirty = [f for f in unstaged_python(root) if f in changed]
    if dirty:
        note(f"WARNING: {len(dirty)} changed .py file(s) have unstaged edits — "
             "mypy/pytest see the working tree, not the index")

    note(f"rule 3 type-check: mypy over {len(changed)} changed file(s), "
         f"pinned venv (first run after a library change can take ~1 min)…")
    found = run_mypy(root, py, changed)
    base = load_baseline(root)

    new = []
    for key, n in sorted(found.items()):
        allowed = base.get(key, 0)
        if n > allowed:
            f, code, msg = key.split("\t", 2)
            extra = f" (x{n - allowed} more than baseline)" if allowed else ""
            new.append(f"{f}  {code} {msg}{extra}")

    if new:
        fail(
            "type-check found NEW errors in the changed Python",
            "Checked against the pinned venv (agent-improve/.venv, LangGraph 1.2.11),",
            "so these are measured against the real installed library's types.",
            "",
            *[f"  {line}" for line in new[:25]],
            *([f"  … and {len(new) - 25} more"] if len(new) > 25 else []),
            "",
            f"{len(base)} pre-existing error kinds are baselined in {BASELINE_REL}",
            "and do not block. The errors above are NEW.",
            "",
            "If an error is a genuine false positive, fix mypy.ini rather than",
            "widening the baseline — the baseline is for existing debt, not new.",
            f"To re-record the baseline deliberately:  python {BASELINE_REL and '.claude/hooks/commit-msg-refactor-guard.py'} --update-baseline",
        )
    note(f"rule 3 type-check: PASS ({sum(found.values())} baselined error(s) in scope)")


# --------------------------------------------------------------------------- #
def check_architecture_status(root: str, staged: list[str]) -> None:
    """Rule 2b — ARCHITECTURE_STATUS.md moved with the thing it describes.

    **The one rule here that is not scoped to `refactor(arch-v2)`.**
    ARCHITECTURE.md carries a `> **BUILT:**` marker on every item whose built
    state is claimed — §19's eight positions, §49's route count, §44's Step 0,
    §51's zero `@traceable` (§55.2). A commit that changes a watched path and
    leaves the document alone makes one of those markers quietly false, which
    is the exact failure the coverage audit was run to find: `phase_context`
    was declared, written, read by nothing, and no document said so for six
    steps.

    **Renamed target, unchanged rule (2026-09-10).** This pointed at
    `docs/ARCHITECTURE_STATUS.md`, which held the same claims in a parallel
    table. That file is archived; the markers moved onto the specified items.
    `.claude/hooks/verify_built.py` re-runs the counts behind them, because a
    marker nothing re-runs is a claim.

    Fires on the union of staged paths and STATUS_WATCHED. Prefix entries match
    a whole package.
    """
    hits = sorted({
        w for w in STATUS_WATCHED
        for p in staged
        if (p.lower().startswith(w.lower()) if w.endswith("/")
            else p.lower() == w.lower())
    })
    if not hits:
        return
    if any(p.lower() == STATUS_PATH.lower() for p in staged):
        return
    fail("the architecture status document was not updated in this commit",
         f"Required: {STATUS_PATH}", "",
         "This commit touches path(s) that document tabulates:",
         *[f"  - {h}" for h in hits], "",
         "That file states built/total counts, every middleware and its hook,",
         "and every cap and its value. Changing one of these paths without it",
         "leaves a row silently false — which is how `phase_context` stayed",
         "declared-but-unread for six steps.",
         "",
         "Update it (or confirm nothing it states changed, and touch it so the",
         "check of that is on the record), `git add` it, and commit again.")


# --------------------------------------------------------------------------- #
# Rules 7 and 8 — what may ENTER the tree (CLAUDE.md §0.32)
# --------------------------------------------------------------------------- #
#
# §0.32's FIRST clause — the tree at HEAD is the only source of truth — binds on
# what is CLAIMED, and a commit hook cannot check a claim. Its other two clauses
# bind on what ENTERS the tree, which is precisely what a commit is, so they are
# gated here and the first is left to the rule and to review.
#
# BOTH RANGE OVER `added_paths`, NOT `staged_paths`, AND THAT IS A RATCHET —
# rule 3's argument applied to paths. They see only what is NEW TO THE TREE at
# this commit; a path that is merely modified is invisible to them. Two `.bak`
# files are tracked today under `agent-improve/docs/_archive/`, deliberately, as
# archives of the root file. A rule reading every staged path would block every
# commit that touched one, and a guard people route around with --no-verify is
# worse than no guard. New scratch cannot land; what is already tracked stays
# visible and countable.
#
# NEITHER HAS A SOFT OPT-OUT, unlike rule 6's `8D: NOT A FIX`. Rule 6's opt-out
# exists because its trigger 2 fires on a MENTION and can therefore be wrong
# about what a commit is. These two fire on the INDEX, which cannot be wrong
# about it: either a scratch path is staged or it is not, either a number is
# declared or it is not. The escape is `--no-verify`, which is on the record.

# Rule 7 — path SEGMENTS that mean "working material". Matched whole, lowered,
# against the DIRECTORY part only, so `docs/scratch/note.md` is caught and
# `backend/knowledge/scratchpad_tools.py` is not. The list is not hypothetical:
# `_Artifacts/` and `agent-improve/_Claude_chat_Prompts/` sit untracked in this
# tree today, and `.gitignore` already calls `ARTIFACTS/` "not part of the repo"
# while spelling it in a case the working directory does not use.
SCRATCH_SEGMENTS = frozenset({
    "scratch", "_scratch", "scratchpad", "_scratchpad",
    "tmp", "_tmp", "temp", "_temp",
    "draft", "drafts", "_draft", "_drafts",
    "wip", "_wip", "sandbox", "playground",
    "snapshot", "snapshots", "_snapshot", "_snapshots",
    "artifacts", "_artifacts", "_claude_chat_prompts",
})

# Rule 7 — basename SUFFIXES. `.bak`, `.orig` and `.rej` are an editor's or a
# merge's leavings. `.new`, `.old` and `.save` are a hand-rolled version control
# standing beside the one the repository already has, which is the shape §0.32
# names: a second copy that can disagree with the tracked file, with no history
# to settle which of the two is the file.
SCRATCH_SUFFIXES = (
    ".bak", ".orig", ".rej", ".tmp", ".temp", ".swp", ".swo",
    ".save", ".new", ".old", ".draft", ".log", ".jsonl",
)

# Rule 7 — basename SHAPES, matched case-insensitively with fnmatch. The last
# two are what a SYNCED MIRROR produces, and §0.32's first clause names exactly
# that mirror: OneDrive writes a conflicted copy when two machines edit one
# file, and Office writes a `~$` lock file beside an open document. Both look
# like content and are not.
SCRATCH_GLOBS = (
    "untitled*", "*.copy.*", "* - copy*", "*~",
    "*conflicted copy*", "~$*",
)

# Rule 8 — where a declared number has to RESOLVE. Steps live in Appendix D of
# the procedure (`cs.PROCEDURE` owns that path); gaps live in §66's register in
# ARCHITECTURE.md, which `STATUS_PATH` already names for rule 2b.
_APPENDIX_D_STEP_RE = re.compile(r"\*\*Commit (\d+\.\d+)\*\*")
_GAP_ROW_RE = re.compile(r"\|\s*~{0,2}\*\*(G-\d+)\*\*")

# Rule 8 — where a number may be DECLARED. A spine subject already carries one
# and is not made to repeat it; every other commit type declares a trailer.
_SPINE_STEP_RE = re.compile(r"^refactor\(arch-v2\): commit (\d+\.\d+)\b")
_STEP_TRAILER_RE = re.compile(r"^[\s*_]*Steps?[\s*_]*:[ \t]*(?P<v>.+)$", re.M | re.I)
_GAP_TRAILER_RE = re.compile(r"^[\s*_]*Gaps?[\s*_]*:[ \t]*(?P<v>.+)$", re.M | re.I)
_STEP_TOKEN_RE = re.compile(r"\b\d+\.\d+\b")
_GAP_TOKEN_RE = re.compile(r"\bG-\d+\b", re.I)


def added_paths(root: str) -> list[str]:
    """Paths NEW TO THE TREE AT THIS NAME — added, or renamed into place.

    **`R` is in the filter on purpose.** `git mv REPORT.md REPORT.md.bak` puts a
    scratch name into the tree while adding nothing, and a check reading only
    `A` would watch it happen.
    """
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=AR"],
        capture_output=True, encoding="utf-8", errors="replace",
        cwd=root, timeout=10,
    )
    if out.returncode != 0:
        raise RuntimeError(
            f"git diff --cached --diff-filter=AR failed: {out.stderr.strip()}")
    return [ln.strip().replace("\\", "/") for ln in out.stdout.splitlines() if ln.strip()]


def scratch_reason(path: str) -> str:
    """Why `path` is scratch, or an empty string. Names the pattern, not a verdict.

    The message a developer reads has to say WHICH pattern caught the path:
    "this looks like scratch" is an opinion, and "a .bak suffix" is a fact they
    can act on.
    """
    parts = path.lower().split("/")
    name = parts[-1]
    for seg in parts[:-1]:
        if seg in SCRATCH_SEGMENTS:
            return f"a `{seg}/` directory"
    for suffix in SCRATCH_SUFFIXES:
        if name.endswith(suffix):
            return f"a `{suffix}` suffix"
    for glob in SCRATCH_GLOBS:
        if fnmatch.fnmatch(name, glob):
            return f"the `{glob}` shape"
    return ""


def check_scratch(added: list[str]) -> None:
    """Rule 7 — scratch never enters the tree (CLAUDE.md §0.32, clause 2).

    **The clause is "never evidence", and this is the half a gate can hold.**
    A scratch artifact that stays outside the tree cannot be cited as what the
    code says, because a citation resolves to a repo path or it does not
    resolve at all. What this rule stops is the other direction — the draft
    getting committed and thereby becoming citable, at which point two files
    hold the same content and nothing says which one is the file.

    IT CHECKS THE NAME, NEVER THE CONTENT. A scratch file called `notes.md`
    passes. That limit is `check_8d`'s limit restated: the gate makes the
    convention cheap to follow, and does not make it impossible to evade.
    """
    hits = [(p, why) for p in added if (why := scratch_reason(p))]
    if not hits:
        return
    fail("scratch is staged, and scratch never enters the tree",
         "CLAUDE.md §0.32: scratch lives OUTSIDE the tree, is never committed,",
         "and is never evidence.", "",
         "Staged as new, and caught by name:",
         *[f"  - {p}   ({why})" for p, why in hits], "",
         "If the artifact matters it becomes a TRACKED FILE WITH A STEP NUMBER",
         "— a real path, a real name, and rule 8 asking which step or gap it",
         "belongs to. If it does not matter it belongs outside the tree:",
         "",
         "  git restore --staged <path>     # then move it out, or ignore it",
         "",
         "Only paths NEW to the tree are read, so this is about what you are",
         "adding now and never about anything already tracked.")


def _declared_numbers(subject: str, message: str) -> tuple:
    """The step and gap numbers this commit CLAIMS, before any of them resolve."""
    steps = set(_SPINE_STEP_RE.findall(subject))
    for m in _STEP_TRAILER_RE.finditer(message):
        steps.update(_STEP_TOKEN_RE.findall(m.group("v")))
    gaps = set()
    for m in _GAP_TRAILER_RE.finditer(message):
        gaps.update(t.upper() for t in _GAP_TOKEN_RE.findall(m.group("v")))
    return steps, gaps


def _staged_text(root: str, rel: str) -> str:
    """A tracked document AS THIS COMMIT WILL CONTAIN IT — the index, not the disk.

    **This is §0.32's first clause applied to the guard's own reading.** A
    commit that registers G-57 and adds the file that gap schedules, together,
    has to pass — and only the index knows both halves. Reading the working
    tree would read a version this commit is not making, which is the
    cached-copy failure the rule names.
    """
    out = subprocess.run(
        ["git", "show", f":{rel}"],
        capture_output=True, encoding="utf-8", errors="replace",
        cwd=root, timeout=20,
    )
    if out.returncode != 0 or not out.stdout:
        raise RuntimeError(f"cannot read `{rel}` from the index: {out.stderr.strip()}")
    return out.stdout


def check_step_or_gap(root: str, subject: str, message: str, added: list[str]) -> None:
    """Rule 8 — a new file in the tree needs a step number or a gap number (§0.32).

    **A file with no number is a file nothing scheduled**, and §66's register
    already states the consequence in its own words: *"a gap without one does
    not render on the board and so is not scheduled by anything."* A path that
    entered the tree with no step and no gap behind it is that condition one
    level down — present, costing review, owned by no plan.

    THE NUMBER IS DECLARED AND RESOLVED; IT IS NOT VERIFIED TO FIT. A spine
    subject declares its own step; any other type carries `Step: 6.22` or
    `Gap: G-57` in the body. The number must exist — in Appendix D, or in §66's
    register — and that is ALL this checks. Declaring `Step: 2.3` for a file
    with nothing to do with the dependency upgrade passes. Like rule 6, it makes
    the discipline cheap and auditable rather than impossible to evade: the
    trailer is greppable, so a wrong one is findable afterwards, which is more
    than an undeclared file leaves behind.
    """
    if not added:
        return
    steps, gaps = _declared_numbers(subject, message)
    if not steps and not gaps:
        fail("a new file is entering the tree with no step number and no gap number",
             "CLAUDE.md §0.32: a new file in the tree needs a step number or a",
             "gap number.", "",
             "New in this commit:",
             *[f"  - {p}" for p in added], "",
             "Declare the work it belongs to, in the subject or in the body:",
             "",
             "  refactor(arch-v2): commit 6.22 — <what changed>  # the spine says it",
             "  Step: 6.22                                       # any other type",
             "  Gap: G-57                                        # or the register",
             "",
             "The number must RESOLVE — Appendix D of docs/REFACTORING_PROCEDURE.md",
             "for a step, §66's register in ARCHITECTURE.md for a gap. If neither",
             "exists yet then nothing is scheduling this file: register the gap",
             "first, in its own commit, per §56.")

    known_steps = set(_APPENDIX_D_STEP_RE.findall(_staged_text(root, cs.PROCEDURE)))
    known_gaps = {g.upper() for g in _GAP_ROW_RE.findall(_staged_text(root, STATUS_PATH))}
    if (steps & known_steps) or (gaps & known_gaps):
        return
    fail("the step or gap number this commit declares does not resolve",
         "Declared, and found in no register:",
         *[f"  - {d}" for d in sorted(steps) + sorted(gaps)], "",
         f"Steps resolve against Appendix D of {cs.PROCEDURE}.",
         f"Gaps resolve against §66's register in {STATUS_PATH}.",
         "Both are read from the INDEX, so a number registered in THIS commit",
         "counts — stage the register row alongside the file.", "",
         "A number that resolves nowhere schedules nothing, which leaves the",
         "file in the state rule 8 exists to prevent. §66's own words: a gap",
         "without a number does not render on the board, and so is not",
         "scheduled by anything.")


# --------------------------------------------------------------------------- #
# Rule 6 — the 8D body on a FIX commit (CLAUDE.md §20)
# --------------------------------------------------------------------------- #

# A commit "is a fix" on any of three triggers. Deliberately three and not one:
# this project's real fixes land under `refactor(arch-v2)` far more often than
# under `fix(`, so a type-only trigger would exempt exactly the commits the rule
# is for — G-49's fix lands as `commit 6.21`, not as a `fix(`.
FIX_TYPE_RE = re.compile(r"^(?:fix|hotfix)(?:\([^)]*\))?!?:", re.I)

# Trigger 2 — the subject names a REGISTERED defect. Subject only, never body:
# half the commits in this log mention a G-number in passing, and a rule that
# fired on a mention would be routed around by the end of the week.
DEFECT_CODE_RE = re.compile(r"\b(?:[GF]-\d+|WATCH\s+\d+)\b")

# The opt-out, and it exempts TRIGGER 2 ONLY. A commit whose subject carries a
# defect code but which changes no behaviour — a register row, a board caption —
# says so on the record instead of reaching for --no-verify. **It cannot exempt
# a `fix(` subject and it cannot exempt a body that already carries D-labels**:
# a commit that calls itself a fix does not get to opt out of being one.
NOT_A_FIX_RE = re.compile(
    r"^[\s*_]*8D[\s*_]*:[ \t]*NOT A FIX\b[^0-9A-Za-z]*(?P<why>.*)$", re.M)

# Trigger 3 — any `D<n>` label already in the body. A half-written 8D is the
# failure mode a presence check invites, so writing one label opts the commit
# into all six.
ANY_D_LABEL_RE = re.compile(r"^[\s*_]*D[0-8]\b", re.M)

TRAILER_RE = re.compile(
    r"^(?:Co-Authored-By|Claude-Session|Signed-off-by|Reviewed-by|Refs):",
    re.I | re.M)

#: The five §20 requires, with D2 split into its two halves because §20 states
#: D2 as *"describe, with IS / IS-NOT"* — and IS-NOT is the half that bounds the
#: defect. Label, then the pattern that finds it.
EIGHTD = (
    ("D2 IS",         r"D2\s+IS(?![\w-])"),
    ("D2 IS-NOT",     r"D2\s+IS-NOT\b"),
    ("D4 OCCURRENCE", r"D4\s+OCCURRENCE\b"),
    ("D4 ESCAPE",     r"D4\s+ESCAPE\b"),
    ("D5 FIX",        r"D5\s+FIX\b"),
    ("D7 PREVENT",    r"D7\s+PREVENT\b"),
)

#: Content below this is empty in all but form. "tbd", "see above" and "unknown"
#: are what a decaying convention produces, and they pass a presence check.
MIN_ANSWER = 20
#: Characters of reason required after the word NONE.
MIN_REASON = 12

# §20's own shape, so the failure message teaches the rule rather than citing it.
EIGHTD_TEMPLATE = (
    "D2 IS: <what happens, where, since when, how you know>",
    "D2 IS-NOT: <the nearest thing this is NOT — what bounds it>",
    "D4 OCCURRENCE: <why the defect happened>",
    "D4 ESCAPE: <why nothing DETECTED it — a separate answer>",
    "D5 FIX: <the permanent change chosen, and why that one>",
    "D7 PREVENT: <what stops a recurrence of the CLASS, not the instance>",
)


def _label_re(pattern):
    return re.compile(r"^[\s*_]*" + pattern + r"[\s*_]*:[ \t]*", re.M)


def read_message(path: str) -> tuple:
    """`(subject, message)` from a commit-message file, comments dropped.

    **A named function because rule 6 reads the BODY, and what counts as the
    body is a decision worth testing.** git's own commit template is comment
    lines, and so is the `# ------------------------ >8 ---` scissors block of a
    verbose commit — which carries the whole staged diff. Dropping `#` lines
    removes the template, the instructions and that diff in one pass, so no
    discipline can be "answered" by text git wrote or by a diff hunk that
    happens to contain the word ESCAPE.
    """
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = [ln.rstrip("\n") for ln in fh
                 if not ln.lstrip().startswith("#")]
    message = "\n".join(lines)
    subject = next((ln.strip() for ln in lines if ln.strip()), "")
    return subject, message


def is_fix_commit(subject: str, body: str) -> str:
    """Why rule 6 applies to this commit, or an empty string if it does not."""
    if FIX_TYPE_RE.match(subject):
        return "the subject's type is a fix"
    if ANY_D_LABEL_RE.search(body):
        return "the body already carries an 8D label"
    if DEFECT_CODE_RE.search(subject):
        optout = NOT_A_FIX_RE.search(body)
        if optout and len((optout.group("why") or "").strip()) >= MIN_REASON:
            return ""
        return "the subject names a registered defect"
    return ""


def eightd_disciplines(message: str) -> dict:
    """Each §20 label to its content — `None` where the label is absent.

    Content runs from the label to the next `D<n>` label or to the first
    trailer, so an answer may be several paragraphs long and the last one does
    not swallow the `Co-Authored-By` block.
    """
    cut = TRAILER_RE.search(message)
    body = message[:cut.start()] if cut else message
    bounds = [m.start() for m in ANY_D_LABEL_RE.finditer(body)]

    found = {}
    for name, pattern in EIGHTD:
        match = _label_re(pattern).search(body)
        if not match:
            found[name] = None
            continue
        nxt = min((b for b in bounds if b > match.start()), default=len(body))
        found[name] = " ".join(body[match.end():nxt].split())
    return found


def eightd_verdict(content) -> str:
    """An empty string if this discipline is answered; otherwise why it is not."""
    if content is None:
        return "MISSING — no such line in the body"
    if not content:
        return "EMPTY — the label is present and says nothing"
    if content.upper().startswith("NONE"):
        reason = content[4:].lstrip(" \t:\u2014\u2013-,.")
        if len(reason) < MIN_REASON:
            return ("NONE WITH NO REASON — §20 allows an empty discipline and "
                    "requires the reason with it (%d+ chars)" % MIN_REASON)
        return ""
    if len(content) < MIN_ANSWER:
        return ("TOO SHORT — %d chars, %d needed. Below that it is empty in "
                "all but form" % (len(content), MIN_ANSWER))
    return ""


def check_8d(subject: str, message: str) -> None:
    """Rule 6 — D2, D4-occurrence, D4-escape, D5 and D7 in a fix's body.

    **CLAUDE.md §20, founder ruling 2026-09-11.** Every defect, modification or
    adaptation is worked as an 8D before a fix is proposed, and *"convention
    decays; a gate does not"*. This is the gate.

    **WHY THESE FIVE AND NOT ALL EIGHT.** D0, D1, D6 and D8 are checkable
    elsewhere or are not prose: D6 is the step's `Verify` and rules 3 and 4
    already run it, D8 is its Done-when, D1 is one person on this project, and
    D0 is preparation. **The five left are the ones nothing else can see**, and
    D4's two halves are why the rule exists: an occurrence cause with no escape
    cause is the shape that lets the same class of defect return through the
    same blind spot. §20 names that split as the clause carrying the weight.

    **AN EMPTY DISCIPLINE IS A FINDING AND SAYS SO.** `NONE` plus a reason
    passes — G-49's own D3 and D7 are empty, and §20 calls that the most useful
    thing the structure produced. `NONE` alone does not pass: the reason IS the
    finding, and without it the word is only a way through the gate.

    **WHAT THIS RULE CANNOT CHECK, stated so nobody mistakes green for good.**
    It checks that each discipline is ANSWERED, never that the answer is right.
    A plausible D4 ESCAPE naming the wrong blind spot passes here and is caught
    only on review. The gate raises the floor; it does not do the thinking.

    **And one parsing limit, measured rather than assumed.** A discipline's
    content runs to the next `D<n>` label or to the trailer, so the LAST label
    in a body absorbs everything after it — `D7 PREVENT` is usually satisfied by
    the rest of the message. Bounding it at a blank line was rejected: a real
    answer is often several paragraphs, and the check is a MINIMUM length, so
    over-capturing makes a commit easier to pass and under-capturing would
    reject a complete answer. Both are the wrong error for a floor.
    """
    why = is_fix_commit(subject, message)
    if not why:
        return

    found = eightd_disciplines(message)
    names = [n for n, _ in EIGHTD]
    problems = [(n, eightd_verdict(found[n])) for n in names
                if eightd_verdict(found[n])]
    if not problems:
        note("rule 6 8D: PASS — six disciplines answered (%s)" % why)
        return

    answered = ["  %-15s %s" % (n, (found[n] or "")[:60])
                for n in names if not eightd_verdict(found[n])]
    fail("the 8D body is incomplete — CLAUDE.md §20",
         "Rule 6 applies because %s." % why, "",
         "NOT ANSWERED",
         *["  %-15s %s" % (n, v) for n, v in problems], "",
         "ANSWERED",
         *(answered or ["  (none)"]), "",
         "§20 requires these five, and D2 in both halves:", "",
         *["  " + line for line in EIGHTD_TEMPLATE], "",
         "An EMPTY discipline is a finding, not an omission — write",
         "`NONE — <why it is empty>` and it passes. D4 ESCAPE is the one most",
         "often missing and usually the expensive one: \"why did nothing detect",
         "this\" is a different question from \"why did it happen\".", "",
         "If this commit changes no behaviour and only its subject names a",
         "defect, say so on the record instead of bypassing:",
         "  8D: NOT A FIX — <why>",
         "That line cannot exempt a `fix(` subject, or a body that already",
         "carries D-labels.")


# Rule 5 — CONTINUITY.md moved with the step
# --------------------------------------------------------------------------- #
def check_continuity(root: str, staged: list[str]) -> None:
    """CONTINUITY.md staged, with a CURRENT BUILD STATUS block that is current.

    The comparison ignores the `Block regenerated` date line: a commit made
    just after midnight, or a rebase replayed on another day, would otherwise
    be blocked over a value that carries no build meaning.
    """
    want = cs.CONTINUITY.lower()
    if not any(p.lower() == want for p in staged):
        fail("CONTINUITY.md was not updated in this commit",
             f"Required: {cs.CONTINUITY}", "",
             f"Staged in this commit ({len(staged)} path(s)):",
             *[f"  - {p}" for p in staged[:20]],
             *(["  … and more"] if len(staged) > 20 else []), "",
             "One step = one commit = both orientation documents moved.",
             "",
             "This is normally automatic: .githooks/pre-commit regenerates the",
             "CURRENT BUILD STATUS block and stages the file for you. Seeing",
             "this message means that hook did not run. Most likely:",
             "  git config core.hooksPath .githooks      <- not set in this clone",
             "Set it and commit again, or stage the file yourself.")

    staged_text = cs.staged_text(cs.CONTINUITY, root)
    found = cs.extract_block(staged_text)
    if found is None:
        fail("CONTINUITY.md carries no CURRENT BUILD STATUS block",
             f"Expected a block delimited by:",
             f"  {cs.BEGIN}", f"  {cs.END}", "",
             "It is generated, not written. Run a commit with .githooks active",
             "and pre-commit will insert it, or regenerate manually:",
             "  python .claude/hooks/pre-commit-continuity.py")

    expected = cs.build_block(root)

    def _strip_date(block: str) -> str:
        return "\n".join(ln for ln in block.splitlines()
                         if "Block regenerated" not in ln)

    if _strip_date(found) != _strip_date(expected):
        fail(
            "CONTINUITY.md's CURRENT BUILD STATUS block is STALE",
            "The staged block does not match what git log, Appendix D of",
            "REFACTORING_PROCEDURE.md, CLAUDE.md and ARCHITECTURE.md produce.",
            "It is derived, so the block is wrong by construction rather than",
            "merely out of date.",
            "",
            "Staged:",
            *[f"  {ln}" for ln in _strip_date(found).splitlines()
              if ln.startswith("| **")],
            "",
            "Expected:",
            *[f"  {ln}" for ln in _strip_date(expected).splitlines()
              if ln.startswith("| **")],
            "",
            "Fix by regenerating rather than by editing the block:",
            "  python .claude/hooks/pre-commit-continuity.py && git add "
            f"{cs.CONTINUITY}",
        )
    note("rule 5 continuity: PASS — status block current")


# --------------------------------------------------------------------------- #
# Rule 4 — tests
# --------------------------------------------------------------------------- #
def check_tests(root: str, py: str) -> None:
    note("rule 4 tests: pytest, pinned venv…")
    proj = os.path.join(root, PROJECT)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    out = subprocess.run(
        [py, "-m", "pytest", TESTS_REL, "-q", "--no-header", "-p", "no:cacheprovider"],
        capture_output=True, encoding="utf-8", errors="replace",
        cwd=proj, timeout=PYTEST_TIMEOUT, env=env,
    )
    if out.returncode != 0:
        body = ((out.stdout or "") + (out.stderr or "")).strip().splitlines()
        fail("tests failed",
             *[f"  {ln}" for ln in body[-25:]],
             "",
             "Run it yourself:",
             f"  cd {PROJECT} && .venv/Scripts/python.exe -m pytest {TESTS_REL} -q")
    summary = next((ln for ln in reversed((out.stdout or "").splitlines()) if ln.strip()), "")
    note(f"rule 4 tests: PASS — {summary.strip()}")


# --------------------------------------------------------------------------- #
# --update-baseline
# --------------------------------------------------------------------------- #
def update_baseline() -> int:
    root = repo_root()
    py = venv_python(root)
    proj = os.path.join(root, PROJECT)
    note("regenerating the mypy baseline over the whole backend…")
    os.makedirs(CACHE_DIR, exist_ok=True)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    out = subprocess.run(
        [py, "-m", "mypy", "--config-file", os.path.join(root, MYPY_INI),
         "--cache-dir", CACHE_DIR, "--no-error-summary", "--no-color-output",
         "--hide-error-context", "backend"],
        capture_output=True, encoding="utf-8", errors="replace",
        cwd=proj, timeout=MYPY_TIMEOUT, env=env,
    )
    if out.returncode not in (0, 1):
        sys.stderr.write((out.stdout or "") + (out.stderr or ""))
        return 2
    counts = parse_errors((out.stdout or "") + (out.stderr or ""))
    path = os.path.join(root, BASELINE_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(
            "# mypy baseline — pre-existing type errors that do NOT block a commit.\n"
            "#\n"
            "# Generated by:  python .claude/hooks/commit-msg-refactor-guard.py --update-baseline\n"
            "# Consumed by:   the same script, rule 3, at commit-msg time.\n"
            "#\n"
            "# Format:  <count>\\t<repo-relative file>\\t<error code>\\t<message>\n"
            "# Line numbers are stripped so the baseline does not churn when unrelated\n"
            "# lines move; the COUNT still has to not increase, so a second copy of an\n"
            "# existing error is caught.\n"
            "#\n"
            "# THIS FILE IS DEBT, NOT A CONFIG. It should only ever shrink. Never widen\n"
            "# it to make a new error go away — fix the error, or fix mypy.ini if the\n"
            "# error is a genuine false positive.\n"
            "#\n"
            f"# {sum(counts.values())} errors across {len({k.split(chr(9))[0] for k in counts})} files.\n"
            "\n"
        )
        for key in sorted(counts):
            fh.write(f"{counts[key]}\t{PROJECT}/{key}\n")
    note(f"wrote {BASELINE_REL}: {sum(counts.values())} errors, "
         f"{len(counts)} distinct kinds")
    return 0


# --------------------------------------------------------------------------- #
def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "--update-baseline":
        return update_baseline()

    if len(argv) < 2:
        fail("guard invoked without a message file",
             "Usage: <guard> <commit-msg-file>   |   <guard> --update-baseline",
             "It is a commit-msg hook — it will not work as a pre-commit hook.")

    root = repo_root()

    # Merge commits carry a generated subject and stage nothing of their own.
    if os.path.exists(os.path.join(root, ".git", "MERGE_HEAD")):
        return 0

    subject, message = read_message(argv[1])
    if not subject:
        return 0  # git aborts an empty message itself, with a better error

    # ── Rule 2b — applies to EVERY commit, not only spine commits ─────────
    # Deliberately ahead of the prefix gate: the rule is "changed something it
    # describes", and that is as true of a `fix(` as of a `refactor(`.
    try:
        all_staged = staged_paths(root)
    except Exception as exc:  # noqa: BLE001 — fail CLOSED
        fail("the guard itself failed", f"{exc}",
             "Blocking rather than passing: a guard that waves a commit through",
             "when its own logic breaks is worse than no guard.")
    # ── Rules 7 and 8 — what may ENTER the tree (CLAUDE.md §0.32) ─────────
    # FIRST of all the rules, and ahead of the prefix gate with 2b and 6.
    # A scratch path in the index is a more basic failure than a stale status
    # table, and both of these are lexical: they read the index and the message
    # and spend no subprocess on mypy or pytest to reject a commit that was
    # never going to land. Both bind on EVERY commit — a draft lands under a
    # `docs(` subject as easily as under a `refactor(`, which is the same
    # argument that put 2b ahead of the gate.
    try:
        added = added_paths(root)
    except Exception as exc:  # noqa: BLE001 — fail CLOSED
        fail("the guard itself failed", f"{exc}",
             "Blocking rather than passing: a guard that waves a commit through",
             "when its own logic breaks is worse than no guard.")
    check_scratch(added)
    check_step_or_gap(root, subject, message, added)

    check_architecture_status(root, all_staged)

    # ── Rule 6 — also ahead of the prefix gate, and for the same reason ────
    # A fix lands under any type. It is a pure message check, so it costs
    # nothing and runs before mypy and pytest can spend a minute on a commit
    # that was going to be rejected on its body anyway.
    check_8d(subject, message)

    if not subject.startswith(GUARDED_PREFIX):
        return 0

    # ── Rule 1 — subject format ───────────────────────────────────────────
    if not SUBJECT_RE.match(subject):
        if re.match(r"^refactor\(arch-v2\): commit \d+\.\d+ [-–] ", subject):
            hint = ["The separator is a HYPHEN or EN DASH. It must be an EM DASH (—, U+2014).",
                    "This is the most common slip and the easiest to miss on review."]
        elif not re.match(r"^refactor\(arch-v2\): commit \d+\.\d+\b", subject):
            hint = ["Expected `commit X.Y` (lowercase, digits) right after the colon.",
                    "`step 2.4`, `Commit 2.4` and a bare `2.4` are all rejected here,",
                    "even though the session-start hook tolerates them on read."]
        else:
            hint = ["The description after the em dash is empty."]
        fail("refactor subject does not match the spine format",
             f"Got:      {subject}",
             "Expected: refactor(arch-v2): commit X.Y — <what changed>",
             "", *hint, "",
             "Why it matters: the session-start hook parses this subject to report",
             "\"last completed\". A malformed one drops the step out of the only",
             "automated continuity signal the project has, silently.")

    # ── Rule 2 — DELETED 2026-09-10 ───────────────────────────────────────
    #
    # It required BUILD_TRACKER.md and REFACTORING_PROCEDURE.md to be staged
    # together on every spine commit — "one step = one commit = one row moved
    # IN BOTH". **Both halves of that are now false.** BUILD_TRACKER.md is
    # deleted, and Appendix D no longer carries a per-step status a landing
    # commit has to move: completion is read from git log, so a step that
    # lands changes no document at all.
    #
    # What the rule was really defending was that two documents holding the
    # same fact must not disagree. **The fix was to stop holding it twice**,
    # which is a stronger answer than checking they moved together — the rule
    # only ever verified both files were TOUCHED, never that they AGREED, and
    # 6.13 shipped with them disagreeing while the rule passed.
    #
    # Rule 2b keeps its own number and is untouched; it ran above, ahead of
    # the prefix gate, because it binds on every commit rather than only on
    # spine commits.
    staged = all_staged

    # ── Rule 5 — the other orientation document moved too ─────────────────
    # Before the venv rules, because it is instant and needs no subprocess:
    # a missing CONTINUITY update should not cost a 60s mypy run first.
    check_continuity(root, staged)

    # ── Rules 3 and 4 — against the pinned venv ───────────────────────────
    py = venv_python(root)
    check_types(root, py, staged)
    check_tests(root, py)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except SystemExit:
        raise
    except subprocess.TimeoutExpired as exc:
        fail("a guard check timed out", f"{exc}",
             "Blocking rather than passing.")
    except Exception as exc:  # noqa: BLE001 — fail CLOSED
        fail("the guard itself crashed", f"{exc!r}",
             "Blocking rather than passing, deliberately.")
