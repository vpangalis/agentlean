#!/usr/bin/env python3
"""The CURRENT BUILD STATUS block in `agent-improve/docs/CONTINUITY.md`.

ONE generator, TWO consumers:

  * `.githooks/pre-commit` — regenerates the block and `git add`s CONTINUITY.md,
    so keeping it current does not depend on anyone remembering.
  * `.claude/hooks/commit-msg-refactor-guard.py` rule 5 — verifies the staged
    CONTINUITY.md carries the block regeneration would produce. Fail-closed
    backstop for a bypassed, disabled or broken pre-commit hook, and for a
    hand-edited block.

WHY THE WORK IS SPLIT ACROSS TWO HOOKS
    Measured, not assumed (throwaway repo, 2026-08-31):

        pre-commit  `git add`  -> the file LANDS in the commit
        commit-msg  `git add`  -> it does NOT. The commit is written from the
                                  tree git already resolved, and the hook's
                                  write is left behind as a DIRTY WORKING TREE

    The second is the dangerous one: it looks like it worked. So regeneration
    can only live in pre-commit. And rule 1 needs the subject, which pre-commit
    cannot see (it runs before the message exists), so verification can only
    live in commit-msg. Neither hook can do both jobs.

WHY THE BLOCK IS DERIVED, NOT WRITTEN
    Every value comes from the thing that is already the authority for it:

        last                  git log       highest `refactor(arch-v2): commit X.Y`
        progress (done)       git log       count of distinct spine steps
        next / titles         Appendix D    REFACTORING_PROCEDURE.md
        progress (total)      Appendix D    the row count
        CLAUDE.md version     CLAUDE.md     line 2
        ARCHITECTURE version  ARCHITECTURE.md  its `Version X.Y · date` line

    Nothing here is a second source of truth.

WHAT CHANGED 2026-09-10, AND WHY IT HAD TO
    This module used to read `BUILD_TRACKER.md`, deciding "is this row done"
    with `"done" in status.lower()` and "is this the cursor" with `"▶" in
    status` — **substring searches over human prose.**

    THAT PARSER FIRED TWICE. Once on 2026-09-08, when a note reading *"was
    marked ▶ next until the audit …"* left on step 7.1 made the block report
    `next 7.1` while Appendix D said 6.9. Once on 2026-09-10, when step 6.16 —
    the step that BUILDS the board generator, so its description necessarily
    says "the ▶ cursor" and "if this step is never done" — was read as both the
    cursor and a completed step, reporting `next 6.16` and skipping two steps.
    The second was latent for two days behind row ordering.

    **A convention that a document must avoid two English words to keep a
    parser correct is a parser problem, not a writing problem.** So the prose
    is no longer parsed at all: completion comes from git history, which cannot
    be phrased ambiguously, and the step list comes from Appendix D's fixed
    row format.

    `BUILD_TRACKER.md` was deleted in the same series (DECISIONS Part AV).

THE ONE-COMMIT LAG, STATED RATHER THAN HIDDEN
    At pre-commit time the commit being made does not exist in git log yet, so
    while committing `refactor(arch-v2): commit 6.14` this reports
    `last 6.13, next 6.14`. **That is correct at the moment it is written** —
    6.14 has not landed — and it is what the old tracker-derived version
    reported too, by a different route. The block catches up on the next
    commit, which is why `pre-commit-continuity.py` now runs on EVERY commit
    rather than only when a document input is staged: git log is an input, and
    git log moves every time.

    CONTINUITY.md's own title line has read `Version 4.7` since v4.9 was
    written into its header comment. That is the drift this exists to end.

READS THE INDEX, NOT THE WORKING TREE
    Both consumers care about what is being COMMITTED. `staged_text()` reads
    `git show :<path>`, so an Appendix D edit that was made but not staged does
    not silently produce a status block describing a commit that is not
    happening.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import datetime as _dt
import re
import subprocess

PROCEDURE = "agent-improve/docs/REFACTORING_PROCEDURE.md"
CONTINUITY = "agent-improve/docs/CONTINUITY.md"
CLAUDE_MD = "agent-improve/CLAUDE.md"
ARCH_MD = "agent-improve/ARCHITECTURE.md"

STEP_INDEX_HEADING = "Appendix D"

BEGIN = "<!-- BEGIN CURRENT BUILD STATUS -->"
END = "<!-- END CURRENT BUILD STATUS -->"

# Appendix D row:  | **Commit 4.2** | thread_id + disconnect policy | BLOCKED |
# The status cell is EMPTY for every schedulable step — completion comes from
# git, so the column carries only what git cannot say. Hence `[A-Za-z]*`, not
# `+`: an empty cell must match and read as available, and the same widening
# is made in `session-start-context.py`.
_STEP_ROW = re.compile(
    r"\|\s*\*\*Commit (?P<step>\d+\.\d+)\*\*\s*\|(?P<what>[^|]*)\|\s*(?:\*\*)?(?P<status>[A-Za-z]*)"
)

# Statuses git cannot supply. A row carrying one is never proposed as `next`.
UNAVAILABLE = {"blocked", "gated", "external"}

_CLAUDE_V = re.compile(r"^#\s*Version\s+(?P<v>\S+)", re.M)
# Three components, not two: the file has read `Version 1.19.2` since
# 2026-09-01 and a `\d+\.\d+` match reported it as v1.19 — a patch level
# dropped silently from the one line that says which document this is.
_ARCH_V = re.compile(r"^Version\s+(?P<v>\d+(?:\.\d+)+)", re.M)
_SPINE = re.compile(r"refactor\(arch-v2\):\s*commit\s+(?P<step>\d+\.\d+)")


def _run(args: list[str], cwd: str) -> str:
    out = subprocess.run(
        args, capture_output=True, encoding="utf-8", errors="replace",
        cwd=cwd, timeout=15,
    )
    return out.stdout if out.returncode == 0 else ""


def staged_text(path: str, cwd: str) -> str:
    """The staged blob for `path`, or the working-tree file when unstaged."""
    text = _run(["git", "show", f":{path}"], cwd)
    if text:
        return text
    try:
        import os
        with open(os.path.join(cwd, path), encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def _key(step: str) -> tuple[int, ...]:
    """Numeric tuple key, so 6.10 > 6.9 and 2.10 > 2.2."""
    return tuple(int(p) for p in step.split("."))


def parse_step_index(text: str) -> list[tuple[str, str, str]]:
    """Appendix D's rows as (step, title, status). Nothing else is read.

    Bounded to the Appendix D section so a `| **Commit X.Y** |` written inside
    a step's prose elsewhere in the document cannot be mistaken for a row.
    """
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines)
                  if ln.startswith("## ") and STEP_INDEX_HEADING in ln), None)
    if start is None:
        return []
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    rows = []
    for m in _STEP_ROW.finditer("\n".join(lines[start:end])):
        rows.append((m.group("step"), m.group("what").strip(),
                     m.group("status").strip().lower()))
    return rows


def spine_steps(cwd: str) -> list[str]:
    """Every step that has landed as a `refactor(arch-v2)` commit.

    **This is the completion record, and it is not editable prose.** A step is
    done when a commit says so; there is no document to disagree with.
    """
    log = _run(["git", "log", "--format=%s", "--grep=^refactor(arch-v2):"], cwd)
    return sorted({m.group("step") for ln in log.splitlines()
                   if (m := _SPINE.search(ln))}, key=_key)


def derive(cwd: str) -> dict:
    """The block's values, from git history and Appendix D."""
    rows = parse_step_index(staged_text(PROCEDURE, cwd))
    title_of = {step: what for step, what, _ in rows}

    landed = spine_steps(cwd)
    last_step = landed[-1] if landed else "—"
    last_key = _key(last_step) if landed else (-1,)

    available = [step for step, _, status in rows
                 if status not in UNAVAILABLE and _key(step) > last_key]
    next_step = min(available, key=_key) if available else "—"

    # **The count is the INTERSECTION, not len(landed).** Git history carries
    # five spine commits from before this table existed — 0.1, 1.1, 1.2, 2.1,
    # 2.2, under ARCHITECTURE.md §15's old numbering — and Appendix D starts at
    # 2.3. Counting all 35 against a total of 55 drawn from the table reports
    # progress over two different populations, which is the drift class this
    # whole module was rewritten to remove. Only rows the table actually lists
    # count towards its total.
    in_table = {step for step, _, _ in rows}
    done = sum(1 for step in landed if step in in_table)

    return {
        "last_step": last_step,
        "last_what": title_of.get(last_step, ""),
        "next_step": next_step,
        "next_what": title_of.get(next_step, ""),
        "done": str(done),
        "total": str(len(rows)) if rows else "?",
    }


def last_spine_commit(cwd: str) -> str:
    """The most recent `refactor(arch-v2)` commit, as `hash — step`.

    Informational only — `last_step` comes from the same log by way of
    `spine_steps`, and this adds the hash a reader can go look at.
    """
    log = _run(["git", "log", "-40", "--format=%h %s"], cwd)
    for line in log.splitlines():
        m = _SPINE.search(line)
        if m:
            return f"`{line.split()[0]}` (commit {m.group('step')})"
    return "—"


def build_block(cwd: str, today: str | None = None) -> str:
    t = derive(cwd)
    claude = _CLAUDE_V.search(staged_text(CLAUDE_MD, cwd))
    arch = _ARCH_V.search(staged_text(ARCH_MD, cwd))
    date = today or _dt.date.today().isoformat()

    return "\n".join([
        BEGIN,
        "<!-- Generated by .githooks/pre-commit; verified by the commit-msg",
        "     guard's rule 5. Do not hand-edit — it is rewritten from git log",
        "     and Appendix D on the next commit. -->",
        "",
        "## CURRENT BUILD STATUS",
        "",
        f"| | |",
        f"|---|---|",
        f"| **Last completed** | step **{t['last_step']}** — {t['last_what']} |",
        f"| **Next** | step **{t['next_step']}** — {t['next_what']} |",
        f"| **Spine steps landed** | {t['done']} of {t['total']} |",
        f"| **Last spine commit** | {last_spine_commit(cwd)} |",
        f"| **ARCHITECTURE.md** | v{arch.group('v') if arch else '—'} |",
        f"| **CLAUDE.md** | v{claude.group('v') if claude else '—'} |",
        f"| **Block regenerated** | {date} |",
        "",
        "*`Last completed` and the landed count come from **git log** — the",
        "`refactor(arch-v2): commit X.Y` subjects. `Next` and the total come",
        "from **Appendix D** of `docs/REFACTORING_PROCEDURE.md`. Nothing here",
        "is hand-maintained and no prose is parsed, so this cannot drift from",
        "either. A step that landed under another subject is invisible to the",
        "count by design — give it a BLOCKED / GATED / EXTERNAL status in",
        "Appendix D so the pointer does not stop on it.*",
        END,
    ])


def extract_block(text: str) -> str | None:
    """The existing block, or None when the file carries no markers."""
    start = text.find(BEGIN)
    end = text.find(END)
    if start == -1 or end == -1 or end < start:
        return None
    return text[start: end + len(END)]


def splice(text: str, block: str) -> str:
    """Replace the block, or insert it at the very top of the file."""
    existing = extract_block(text)
    if existing is not None:
        return text.replace(existing, block, 1)
    return block + "\n\n" + text


__all__ = [
    "PROCEDURE", "CONTINUITY", "CLAUDE_MD", "ARCH_MD", "BEGIN", "END",
    "UNAVAILABLE", "staged_text", "parse_step_index", "spine_steps", "derive",
    "build_block", "extract_block", "splice",
]
