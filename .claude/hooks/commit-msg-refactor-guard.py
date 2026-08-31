#!/usr/bin/env python3
"""commit-msg hook — the refactor-commit guard.

Blocks a `refactor(arch-v2)` commit unless ALL FIVE hold:

  1. SUBJECT — matches the spine format EXACTLY:
         refactor(arch-v2): commit X.Y — <what changed>
     One space after the colon, lowercase "commit", X.Y digits, a real em dash
     (U+2014) with a single space either side, and a non-empty description.
     session-start-context.py parses this subject to report "last completed"
     (`_GITLOG_STEP_RE`); a malformed one silently drops the step out of the
     only automated continuity signal the project has.

  2. TRACKER — `agent-improve/docs/BUILD_TRACKER.md` is staged in the same
     commit. One step = one commit = one tracker row moved.

  3. TYPE-CHECK — mypy over the changed Python, against the PINNED venv, so an
     invented LangGraph/LangChain/LangSmith method or a wrong signature fails
     against the real installed library's types. Ratcheted (see below).

  4. TESTS — pytest green.

  5. CONTINUITY — `agent-improve/docs/CONTINUITY.md` is staged AND its CURRENT
     BUILD STATUS block matches what regeneration from the staged inputs
     produces. Same rule as 2, and for the same reason: one step, one commit,
     and the two orientation documents move with it. BUILD_TRACKER.md is the
     checklist; CONTINUITY.md is what a new session reads first, and a
     first-read document that lags the build is worse than one that is merely
     terse — it is confidently wrong. Its own title line read `Version 4.7`
     while its header comment said 4.9, which is the drift this ends.

     NORMALLY THIS RULE NEVER FIRES, and that is the design. `.githooks/
     pre-commit` regenerates and stages the block automatically, so by the time
     this runs it is already correct. Rule 5 is the fail-closed backstop for
     the cases where it did not: pre-commit not installed (`core.hooksPath`
     unset in a fresh clone), the script erroring, `git commit --no-verify` on
     an earlier attempt leaving a stale block staged, or a hand-edited block.

NON-refactor commits are not touched. Docs, fixes and chores pass through.

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

TRACKER_PATH = "agent-improve/docs/BUILD_TRACKER.md"

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
            "The staged block does not match what the staged BUILD_TRACKER.md,",
            "CLAUDE.md and ARCHITECTURE.md produce. It is derived, so the block",
            "is wrong by construction rather than merely out of date.",
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

    subject = ""
    with open(argv[1], encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if s and not s.startswith("#"):
                subject = s
                break
    if not subject:
        return 0  # git aborts an empty message itself, with a better error

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

    # ── Rule 2 — the tracker moved with the code ──────────────────────────
    try:
        staged = staged_paths(root)
    except Exception as exc:  # noqa: BLE001 — fail CLOSED
        fail("the guard itself failed", f"{exc}",
             "Blocking rather than passing: a guard that waves a commit through",
             "when its own logic breaks is worse than no guard.")

    want = TRACKER_PATH.lower()
    if not any(p.lower() == want for p in staged):
        fail("the build tracker was not updated in this commit",
             f"Required: {TRACKER_PATH}", "",
             f"Staged in this commit ({len(staged)} path(s)):",
             *[f"  - {p}" for p in staged[:20]],
             *(["  … and more"] if len(staged) > 20 else []), "",
             "One step = one commit = one tracker row moved. Move this step's row",
             "in the tracker, `git add` it, and commit again.")

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
