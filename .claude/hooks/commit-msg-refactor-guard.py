#!/usr/bin/env python3
"""commit-msg hook — the refactor-commit guard.

Blocks a `refactor(arch-v2)` commit unless ALL FOUR hold (rules 2b and 6 bind on
EVERY commit, each on its own trigger):

**Rule 2 was DELETED 2026-09-10** and its number is not reused — every other
rule keeps the number it has been referred to by in commit messages, DECISIONS
entries and this file's own prose since 2026-08-31. Renumbering to close the
gap would silently redirect every one of those references. The rules are
therefore 1, 2b, 3, 4, 5.

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

NON-refactor commits are touched by rules 2b and 6 only. A docs or chore commit
that neither changes a tabulated path nor claims to fix anything still passes
through untouched.

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
    # Added 2026-09-11 with step 6.16. The board is a PROJECTION of Appendix D,
    # the BUILT markers, §66 and git log; the guard is what notices when the
    # projection did not move with them - a stale board visible the way a stale
    # marker is. It carries NO wall-clock date precisely so that it changes
    # when, and only when, one of those four sources does.
    "agent-improve/docs/board.html",
)

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
