# Control board generator

Builds `docs/control-board.html`: one page with the stage strip, the plan (epics,
stories, tasks, bugs, one rank), the whole-system drawing, and the system in
seven columns (what is there, the architecture for that part, open markers,
open steps), each problem tagged with the story that owns it.

Moved into the repo on 23 September 2026, from the Desktop session's workspace,
so that the plan and the board live beside the code they describe and are
rebuilt by the pre-commit hook on every commit.

## Run

    python build_control_board.py docs/board.html docs/control-board.html

`docs/board.html` is the board `build_board.py` already generates from
Appendix D, ARCHITECTURE.md's markers and git log. Run this AFTER it.

## Files, and where each one's truth comes from

| File | What it holds | Provenance today | Target |
|---|---|---|---|
| `parse_board.py` | reads steps, zones, bands, markers, stages from `docs/board.html` | DERIVED | unchanged |
| `stories.py` | THE PLAN: 9 epics, 37 stories, tasks, bugs, rank; maps every map item to a story | the plan is hand-kept (it is a decision); its STATUSES are derived by `resolve()` | the plan's single source; Appendix I points here |
| `derived.py` | reads Appendix H's green rows and git log's committed steps | DERIVED | unchanged |
| `system_view.py` | the seven columns (NEXT no longer declared here): component inventory, open markers per container, stage names, framework rules | inventory RELAYED from the 208e4a7 audit + reports; markers DERIVED | inventory computed from the tree (extend verify_built) |
| `arch_view.py` | architecture text per container: state fields, node conditions and exceptions | RELAYED | read from ARCHITECTURE.md sections |
| `build_control_board.py` | renders the page | code | unchanged |

In the repo, the pre-commit hook (`.githooks/pre-commit`) runs it from the repo
root as `agent-improve/tools/control_board/build_control_board.py
agent-improve/docs/board.html agent-improve/docs/control-board.html`, after
`build_board.py`, and stages the page. Fail-soft but VISIBLE: if it raises, the
previous page stays, the commit proceeds, and the hook prints a warning. The
page's BUILT FROM line names the commit it was built on top of — the parent of
the commit being made — so a page whose sha is older than the newest commit's
parent is a page whose last build failed.

## Derived since 23 September 2026 (`derived.py`, `stories.resolve()`)

| Shown | Source |
|---|---|
| capability rows proven | Appendix H, the count of green rows |
| story DONE | Appendix H: every row the story cites is green |
| task DONE | git log: `refactor(arch-v2): commit X.Y` |
| NEXT | the top-ranked story not done, and its first open step |

`derived.py` fails CLOSED: a register it cannot read raises, so "0 proven" and
"could not look" never render the same.

## What is still typed by hand

1. The status of a story with no rows, a task that is not a procedure step, and
   every bug. No source owns these; the page labels each one HAND. Where a
   source does exist, the typed value only says which kind of not-done
   (todo / blocked) and can never say done.
2. The component inventory (`have` lists), labelled RELAYED from 208e4a7.
   Should be emitted by verify_built.

## Coverage

The page counts every non-green component, open marker and open step, and shows
how many belong to a story. Anything without one is tagged NO STORY. At handover:
117 of 117. On moving into the repo: 119 of 119 — the two steps registered
at 649737c (6.49 and 6.51) are open steps on the map, and both are owned.
