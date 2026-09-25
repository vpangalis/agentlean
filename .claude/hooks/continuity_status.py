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
import os
import re
import subprocess

PROCEDURE = "agent-improve/docs/REFACTORING_PROCEDURE.md"
CONTINUITY = "agent-improve/docs/CONTINUITY.md"
CLAUDE_MD = "agent-improve/CLAUDE.md"
ARCH_MD = "agent-improve/ARCHITECTURE.md"

STEP_INDEX_HEADING = "Appendix D"

BEGIN = "<!-- BEGIN CURRENT BUILD STATUS -->"
END = "<!-- END CURRENT BUILD STATUS -->"

# The step board, written into REFACTORING_PROCEDURE.md itself. Same generator,
# same inputs, so the board and the plan cannot disagree by construction —
# which is the whole reason step 6.16's generator reads THIS rather than
# re-deriving from the row list on its own.
BOARD_BEGIN = "<!-- BEGIN STEP BOARD -->"
BOARD_END = "<!-- END STEP BOARD -->"

# Appendix D row:  | **Commit 4.2** | thread_id + disconnect policy | BLOCKED |
# The status cell is EMPTY for every schedulable step — completion comes from
# git, so the column carries only what git cannot say. Hence `[A-Za-z]*`, not
# `+`: an empty cell must match and read as available, and the same widening
# is made in `session-start-context.py`.
# **`Seq` is column 1 and ORDERING READS IT** (2026-09-11). The step number is
# a stable identifier, not a position: Appendix D is no longer in execution
# order, so `next` is the lowest-`Seq` row that has not landed.
_STEP_ROW = re.compile(
    r"\|\s*(?P<seq>\d+)\s*\|\s*\*\*Commit (?P<step>\d+\.\d+)\*\*\s*"
    r"\|(?P<what>[^|]*)\|\s*(?:\*\*)?(?P<status>[A-Za-z]*)"
)

# Statuses git cannot supply. A row carrying one is never proposed as `next`.
UNAVAILABLE = {"blocked", "gated", "external"}

_CLAUDE_V = re.compile(r"^#\s*Version\s+(?P<v>\S+)", re.M)
# Three components, not two: the file has read `Version 1.19.2` since
# 2026-09-01 and a `\d+\.\d+` match reported it as v1.19 — a patch level
# dropped silently from the one line that says which document this is.
_ARCH_V = re.compile(r"^Version\s+(?P<v>\d+(?:\.\d+)+)", re.M)
_SPINE = re.compile(r"refactor\(arch-v2\):\s*commit\s+(?P<step>\d+\.\d+)")



def _features_headline() -> str:
    """Step 6.66 — Define's feature list, status only from test-results.json."""
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                         "agent-improve", "tools", "control_board"))
        import features
        return features.headline()
    except Exception as exc:                        # noqa: BLE001 — never break the block
        return f"— (features unreadable: {exc.__class__.__name__})"

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


def parse_step_index(text: str) -> list[tuple[int, str, str, str]]:
    """Appendix D's rows as (seq, step, title, status). Nothing else is read.

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
        rows.append((int(m.group("seq")), m.group("step"),
                     m.group("what").strip(),
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
    title_of = {step: what for _, step, what, _ in rows}
    seq_of = {step: seq for seq, step, _, _ in rows}

    landed = spine_steps(cwd)
    done_set = set(landed)

    # **`Last completed` is the landed step with the highest `Seq`, not the
    # highest NUMBER** (2026-09-11). Ordering moved to `Seq`; the number is a
    # stable identifier. A landed step absent from the table - history carries
    # 0.1, 1.1, 1.2, 2.1, 2.2 from before it existed - has no Seq and cannot be
    # the answer, which is the same population rule the count below applies.
    in_table_landed = [s_ for s_ in landed if s_ in seq_of]
    last_step = max(in_table_landed, key=lambda s_: seq_of[s_]) \
        if in_table_landed else "—"

    # **No watermark.** `next` is the lowest-Seq row that has not landed and is
    # not blocked/gated/external. A row BELOW the last completed one is
    # therefore still reachable - which is exactly what the old
    # "strictly greater than last" rule made impossible, and what cost a
    # renumber on 2026-09-11.
    available = [(seq, step) for seq, step, _, status in rows
                 if status not in UNAVAILABLE and step not in done_set]
    next_step = min(available)[1] if available else "—"

    # **The count is the INTERSECTION, not len(landed).** Git history carries
    # five spine commits from before this table existed — 0.1, 1.1, 1.2, 2.1,
    # 2.2, under ARCHITECTURE.md §15's old numbering — and Appendix D starts at
    # 2.3. Counting all 35 against a total of 55 drawn from the table reports
    # progress over two different populations, which is the drift class this
    # whole module was rewritten to remove. Only rows the table actually lists
    # count towards its total.
    in_table = {step for _, step, _, _ in rows}
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


def _progress():
    """`tools/control_board/progress.py` — THE ONE FUNCTION behind every
    progress number (step 6.63). Imported by path: the hooks run from the
    repo root with no package on sys.path."""
    import sys
    from pathlib import Path
    ctl = str(Path(__file__).resolve().parents[2] / "agent-improve" / "tools" / "control_board")
    if ctl not in sys.path:
        sys.path.insert(0, ctl)
    import progress
    return progress


def read_order(cwd: str) -> list[tuple]:
    """Appendix F's `Order` column — the vertical (step 6.31).

    **This is what CONTINUITY.md's hand-written *NEXT WORK* list used to be.**
    That list was set on 2026-09-14, sat BELOW the generated region so that
    regeneration could not touch it, and was **wrong at HEAD within a day**.

    **Read by `progress.order_rows`** (step 6.63): the regex this function
    carried until then lost the Zone cell and returned an empty vertical.
    """
    rows = _progress().order_rows(staged_text(PROCEDURE, cwd))
    return [(r["n"], r["step"], r["item"], r["state"]) for r in rows]


def _p(cwd: str, today: str | None = None) -> dict:
    """`progress.progress()` over the STAGED procedure — the text the commit
    will carry, which is what rule 5 compares against."""
    import datetime as dt
    return _progress().progress(staged_text(PROCEDURE, cwd),
                                today=dt.date.fromisoformat(today) if today else None)


def _vertical_lines(cwd: str, p: dict | None = None) -> list[str]:
    """The vertical as table rows, or an explicit statement that it is empty.

    **An empty vertical renders a SENTENCE, never an empty table.** A blank
    table reads as a rendering failure; "nothing is declared" is a fact about
    the plan and has to look like one. Each row's state is `progress()`'s —
    built / wired / proven — not the Appendix F mark.
    """
    p = p or _p(cwd)
    if not p["order"]:
        return ["**No row in Appendix F carries an `Order` number** — nothing "
                "is declared as the current run of work."]
    out = ["| # | Step | State |", "|---|---|---|"]
    out += [f"| **{n}** | **{s}** — {p['steps'][s]['title']} | {p['steps'][s]['state']} |"
            for n, s in enumerate(p["order"], start=1)]
    return out


def build_block(cwd: str, today: str | None = None) -> str:
    """CONTINUITY.md's status block — EVERY number from `progress()` (6.63).

    Until 6.63 this block computed its own: "Spine steps landed 55 of 99" and
    a "Next" from Appendix D's Seq, while the control board said 15 of 35 and
    the plan's Order named another step. Two views, two numbers — the 8D's
    first cause. Now the headline here is the board's headline, character for
    character, and `check_board.py` fails the commit if they differ.
    """
    p = _p(cwd, today)
    claude = _CLAUDE_V.search(staged_text(CLAUDE_MD, cwd))
    arch = _ARCH_V.search(staged_text(ARCH_MD, cwd))
    date = today or _dt.date.today().isoformat()
    wo = p["working_on"]
    plan = p["plan"]
    count = {k: sum(1 for st in p["steps"].values() if st["state"] == k)
             for k in ("proven", "wired", "tooling", "built", "blocked", "unbuilt")}

    return "\n".join([
        BEGIN,
        "<!-- Generated by .githooks/pre-commit; verified by the commit-msg",
        "     guard's rules 5 and 10. Do not hand-edit — it is rewritten from",
        "     tools/control_board/progress.py on the next commit. -->",
        "",
        "## CURRENT BUILD STATUS",
        "",
        "| | |",
        "|---|---|",
        f"| **Headline** | {p['headline']} |",
        f"| **Working on** | step **{wo['step']}** — {wo['title']} |" if wo else
        "| **Working on** | nothing — the Order is empty |",
        f"| **Define finishes (7.9)** | {plan['forecast_define'] or '—'} · conditional on "
        f"{', '.join(plan['conditional_on']) or 'nothing'} · {plan['basis']} |",
        f"| **Steps** | {count['proven']} proven · {count['wired']} wired · "
        f"{count['tooling']} tooling · "
        f"{count['built']} built, not wired · {count['blocked']} waiting · "
        f"{count['unbuilt']} not built |",
        f"| **Define features** | {_features_headline()} |",
        f"| **ARCHITECTURE.md** | v{arch.group('v') if arch else '—'} |",
        f"| **CLAUDE.md** | v{claude.group('v') if claude else '—'} |",
        f"| **Block regenerated** | {date} |",
        "",
        "*Every figure here comes from `tools/control_board/progress.py` — the",
        "one function behind every progress number (step 6.63) — and is the",
        "same as `docs/control-board.html`, the only progress view (founder,",
        "2026-09-25). A step is DONE only when WIRED (a test drives the real",
        "graph through the real route) or PROVEN (its capability row is green).*",
        "",
        "### ⇒ THE VERTICAL — the run of work being done now",
        "",
        *_vertical_lines(cwd, p),
        "",
        "*Projected from the `Order` column of **Appendix F** in",
        "`docs/REFACTORING_PROCEDURE.md` (founder 2026-09-25: *\"Priority =",
        "Appendix F Order column\"*). To change what is next, edit it THERE.*",
        END,
    ])


def build_step_board(cwd: str, today: str | None = None) -> str:
    """The step board written into REFACTORING_PROCEDURE.md — from `progress()`.

    **Until 6.63 it said DONE 56 and BUILDING NOW 6.43**: DONE was "a landing
    commit exists" and BUILDING NOW the lowest Seq not landed — a fifth
    progress view with its own definition of done. Now its states are the
    three proofs (step 6.63) and WORKING ON is the plan's.

    **It deliberately does NOT render `| **Commit X.Y** |` rows**, so it can
    never be mistaken for the step index.
    """
    p = _p(cwd, today)
    date = today or _dt.date.today().isoformat()
    wo = p["working_on"]
    by: dict[str, list[str]] = {}
    for s, st in p["steps"].items():
        by.setdefault(st["state"], []).append(s)

    def names(state: str) -> str:
        return ", ".join(f"**{s}**" for s in by.get(state, [])) or "—"

    out = [
        BOARD_BEGIN,
        "<!-- Generated by .githooks/pre-commit, from tools/control_board/progress.py.",
        "     DO NOT HAND-EDIT — it is rewritten on the next commit. -->",
        "",
        "## Step board",
        "",
        "| State | Count | Steps |",
        "|---|---|---|",
        f"| **WORKING ON** | {1 if wo else 0} | " + (f"**{wo['step']}** — {wo['title']}" if wo else "—") + " |",
        f"| **PROVEN** | {len(by.get('proven', []))} | {names('proven')} |",
        f"| **WIRED** | {len(by.get('wired', []))} | {names('wired')} |",
        f"| **TOOLING** | {len(by.get('tooling', []))} | {names('tooling')} |",
        f"| **BUILT, NOT WIRED** | {len(by.get('built', []))} | {names('built')} |",
        f"| **WAITING** | {len(by.get('blocked', []))} | {names('blocked')} |",
        f"| **NOT BUILT** | {len(by.get('unbuilt', []))} | {names('unbuilt')} |",
        "",
        f"*{len(p['steps'])} steps. PROVEN: every capability row the step owns is green "
        "and its check passed on the current source. WIRED: its Wiring-proofs test "
        "passed on the current source. BUILT: its Appendix F row is ✅. WAITING: "
        "Appendix D says BLOCKED / GATED / EXTERNAL. The same states, with each "
        f"reference, are on `docs/control-board.html`. Regenerated {date}.*",
        BOARD_END,
    ]
    return "\n".join(out)


def extract_block(text: str, begin: str = BEGIN,
                  end_marker: str = END) -> str | None:
    """The existing block, or None when the file carries no markers."""
    start = text.find(begin)
    end = text.find(end_marker)
    BEGIN_, END_ = begin, end_marker
    if start == -1 or end == -1 or end < start:
        return None
    return text[start: end + len(END_)]


def splice(text: str, block: str, begin: str = BEGIN,
           end_marker: str = END) -> str:
    """Replace the block, or insert it at the very top of the file."""
    existing = extract_block(text, begin, end_marker)
    if existing is not None:
        return text.replace(existing, block, 1)
    return block + "\n\n" + text


__all__ = [
    "PROCEDURE", "CONTINUITY", "CLAUDE_MD", "ARCH_MD", "BEGIN", "END",
    "UNAVAILABLE", "BOARD_BEGIN", "BOARD_END",
    "staged_text", "parse_step_index", "spine_steps", "derive",
    "build_block", "build_step_board", "extract_block", "splice",
]
