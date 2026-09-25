# Control board

`docs/control-board.html` is **the only progress view** (founder, 2026-09-25).
Every number, label, diagram element and status colour on it is derived from
the tree, never typed by hand (step 6.63).

## Run

    agent-improve/.venv/Scripts/python.exe agent-improve/tools/control_board/build_control_board.py
    agent-improve/.venv/Scripts/python.exe agent-improve/tools/control_board/check_board.py

The pre-commit hook (`.githooks/pre-commit`) runs the builder with `--staged`
on every commit and stages the page and `docs/test-results.json`. The
commit-msg guard's rule 10 runs the check and refuses the commit if the page
disagrees with the tree.

## Files

| File | What it does |
|---|---|
| `progress.py` | **The one function.** Reads Appendix D, F (Order, Wiring proofs), H, the step cards, the estimate table, `test-results.json` and git log; returns every number, status and reference, the plan and the forecast. CONTINUITY.md, the procedure's step board, the session-start hook and this page all read it |
| `reach.py` | AST call-graph walk from `app.py`'s routes — a symbol claimed as WIRED must be reachable |
| `shape.py` | The architecture diagram, read from the code: the compiled graphs, the `create_agent` middleware list, probes of the skills and state-injection middleware — and each container's "what is there" (routes, graphs, schemas, tools, gate specs, persistence, hooks), step 6.64 |
| `stories.py` | The plan's epics, stories and tasks. No status is typed — the bugs' typed statuses went at 6.64; `resolve()` derives the rest from `progress()` |
| `build_control_board.py` | Renders the page. Every colour carries `data-key` and `data-ref`; every diagram label carries `data-key` |
| `check_board.py` | Recomputes every status and label and compares — rule 10 |

## The three groupings (step 6.64)

The waterfall switches between **Container** (the default — every registered
step under its Appendix F `Layer`, named by that table's `#### L<n> · <name>`
headings), **Work package** and **Epic / story**. The container cards and the
capabilities table use the same containers. A registered step with no
container is a plan problem (`progress.validate`); a container view that omits
one is refused by `check_board.py`.

`docs/test-results.json` records the `commit` its results were run against and
is **not rewritten** by a run whose source and outcomes are both unchanged. The
amber ("older than the code") is still the source hash's to give.

`board.html`, `system_view.py`, `arch_view.py`, `parse_board.py` and
`derived.py` were retired at 6.63: a second progress view, and typed content.
