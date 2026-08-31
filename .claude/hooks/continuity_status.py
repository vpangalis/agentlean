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
    Every value comes from a file that is already the authority for it:

        last / next / stage   BUILD_TRACKER.md  (the ✅/▶ rows)
        progress              BUILD_TRACKER.md  (the Progress line)
        last commit           git log           (the refactor spine)
        CLAUDE.md version     CLAUDE.md         line 2
        ARCHITECTURE version  ARCHITECTURE.md   its `Version X.Y · date` line

    Nothing here is a second source of truth. If the tracker and this block
    disagree, the block is wrong by construction and regenerating fixes it —
    which is the property that makes "CONTINUITY cannot go stale" true rather
    than merely intended.

    CONTINUITY.md's own title line has read `Version 4.7` since v4.9 was
    written into its header comment. That is the drift this exists to end.

READS THE INDEX, NOT THE WORKING TREE
    Both consumers care about what is being COMMITTED. `staged_text()` reads
    `git show :<path>`, so a tracker edit that was made but not staged does not
    silently produce a status block describing a commit that is not happening.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import datetime as _dt
import re
import subprocess

TRACKER = "agent-improve/docs/BUILD_TRACKER.md"
CONTINUITY = "agent-improve/docs/CONTINUITY.md"
CLAUDE_MD = "agent-improve/CLAUDE.md"
ARCH_MD = "agent-improve/ARCHITECTURE.md"

BEGIN = "<!-- BEGIN CURRENT BUILD STATUS -->"
END = "<!-- END CURRENT BUILD STATUS -->"

# Tracker row:  | 3.1 | SupervisorState + PhaseState | §5, §6, §7 | ✅ done |
_ROW = re.compile(
    r"^\|\s*(?P<step>\d+\.\d+)\s*\|(?P<what>[^|]*)\|[^|]*\|\s*(?P<status>[^|]*?)\s*\|\s*$"
)
_STAGE = re.compile(r"^##\s+(?P<stage>Stage\s+\d+\s+—\s+.+?)\s*$")
_PROGRESS = re.compile(r"\*\*Progress:\s*(?P<done>\d+)\s+of\s+(?P<total>\d+)")
_CLAUDE_V = re.compile(r"^#\s*Version\s+(?P<v>\S+)", re.M)
_ARCH_V = re.compile(r"^Version\s+(?P<v>\d+\.\d+)", re.M)
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


def parse_tracker(text: str) -> dict:
    """Walk the tracker's stage tables once, in order.

    `last` is the highest ✅ done row; `next` is the ▶ row, falling back to the
    first unstarted row after `last` so a missing marker degrades to a sensible
    answer rather than an empty one.
    """
    stage_of: dict[str, str] = {}
    rows: list[tuple[str, str, str]] = []          # (step, what, status)
    stage = ""
    for line in text.splitlines():
        m_stage = _STAGE.match(line)
        if m_stage:
            stage = m_stage.group("stage").strip()
            continue
        m_row = _ROW.match(line)
        if m_row:
            step = m_row.group("step")
            rows.append((step, m_row.group("what").strip(), m_row.group("status")))
            stage_of[step] = stage

    def _key(s: str) -> tuple[int, int]:
        a, b = s.split(".")
        return int(a), int(b)

    done = [r for r in rows if "✅" in r[2] or "done" in r[2].lower()]
    nxt = [r for r in rows if "▶" in r[2]]

    # `next` first — the ▶ marker is the cursor, and it is unambiguous.
    if nxt:
        next_step, next_what = nxt[0][0], nxt[0][1]
    else:
        # No marker: fall back to the first row after the highest done one.
        highest = max((r[0] for r in done), key=_key, default=None)
        after = [r for r in rows if highest and _key(r[0]) > _key(highest)]
        next_step, next_what = (after[0][0], after[0][1]) if after else ("—", "")

    # `last` is the highest done step BEFORE the cursor — not simply the
    # highest done step anywhere.
    #
    # Step 9.0 is the reason. It landed out-of-band (`871637f`, a `feat(...)`
    # subject the spine's git-log scan cannot see), so the tracker carries a
    # done row at 9.0 while the spine sits at 3.1. A plain max() reports "last
    # completed 9.0" and skips seven stages of work — the same shape as the
    # trap Appendix D documents for the session-start hook, arrived at from a
    # different direction. Bounding by the cursor excludes any out-of-band row
    # ahead of it without special-casing 9.0 by name.
    before = [r[0] for r in done if next_step != "—" and _key(r[0]) < _key(next_step)]
    last_step = max(before, key=_key, default="—")

    m_prog = _PROGRESS.search(text)
    what_by_step = {r[0]: r[1] for r in rows}
    return {
        "last_step": last_step,
        "last_what": what_by_step.get(last_step, ""),
        "next_step": next_step,
        "next_what": next_what,
        "stage": stage_of.get(next_step) or stage_of.get(last_step) or "—",
        "done": m_prog.group("done") if m_prog else "?",
        "total": m_prog.group("total") if m_prog else "?",
    }


def last_spine_commit(cwd: str) -> str:
    """The most recent `refactor(arch-v2)` commit, as `hash — step`.

    Informational only. It is deliberately NOT the source for `last_step`: at
    pre-commit time the commit being made does not exist yet, so git log always
    lags the tracker by exactly the step in flight.
    """
    log = _run(["git", "log", "-40", "--format=%h %s"], cwd)
    for line in log.splitlines():
        m = _SPINE.search(line)
        if m:
            return f"`{line.split()[0]}` (commit {m.group('step')})"
    return "—"


def build_block(cwd: str, today: str | None = None) -> str:
    t = parse_tracker(staged_text(TRACKER, cwd))
    claude = _CLAUDE_V.search(staged_text(CLAUDE_MD, cwd))
    arch = _ARCH_V.search(staged_text(ARCH_MD, cwd))
    date = today or _dt.date.today().isoformat()

    return "\n".join([
        BEGIN,
        "<!-- Generated by .githooks/pre-commit; verified by the commit-msg",
        "     guard's rule 5. Do not hand-edit — edit BUILD_TRACKER.md and the",
        "     version lines it reads, then commit. -->",
        "",
        "## CURRENT BUILD STATUS",
        "",
        f"| | |",
        f"|---|---|",
        f"| **Last completed** | step **{t['last_step']}** — {t['last_what']} |",
        f"| **Next** | step **{t['next_step']}** — {t['next_what']} |",
        f"| **Stage** | {t['stage']} |",
        f"| **Progress** | {t['done']} of {t['total']} build steps |",
        f"| **Last spine commit** | {last_spine_commit(cwd)} |",
        f"| **ARCHITECTURE.md** | v{arch.group('v') if arch else '—'} |",
        f"| **CLAUDE.md** | v{claude.group('v') if claude else '—'} |",
        f"| **Block regenerated** | {date} |",
        "",
        "*Derived from `docs/BUILD_TRACKER.md`, `CLAUDE.md`, `ARCHITECTURE.md`",
        "and the git spine — never hand-maintained, so it cannot drift from",
        "them. The authority for any figure here is the file it came from.*",
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
    "TRACKER", "CONTINUITY", "CLAUDE_MD", "ARCH_MD", "BEGIN", "END",
    "staged_text", "parse_tracker", "build_block", "extract_block", "splice",
]
