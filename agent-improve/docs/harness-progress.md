# Harness progress — Define on the long-running-harness pattern

**Replace, don't append** — the current state only; git holds the history, and the
overnight run's full record (6.66) is in commit `a3364ae`'s version of this file.

The three layers (step 6.67): how to work — `CLAUDE.md` and `.claude/`; what must
be true — `docs/define_features.json` + `docs/test-results.json` (the board,
`docs/control-board.html`, and CONTINUITY's block are generated from them); why —
`ARCHITECTURE.md`, read only by the cited section via `docs/section-index.md`. The
session-start routine is in CLAUDE.md.

## Lanes (branches and worktrees beside this checkout; `.venv` is a junction)

| Lane | Branch · worktree | Starts at |
|---|---|---|
| A — coaching | `lane/a-coaching` · `../AgentLean-lane-a-coaching` | the Confirm at field 5 (DEF-008, DEF-029) |
| B — gate | `lane/b-gate` · `../AgentLean-lane-b-gate` | DEF-040 — needs founder D1; `docs/founder-inputs/` drafts |
| C — screen and inputs | `lane/c-screen-inputs` · `../AgentLean-lane-c-screen-inputs` | DEF-052 |
| Integrator | `lane/integrator` · `../AgentLean-lane-integrator` | merges A/B/C; re-runs `scripts/define_runthrough.py` |

A feature lands as `refactor(arch-v2): DEF-xxx — …` only when its test and its
dependencies' tests pass (rule 11); once passed it is required on every commit
(rule 11b, `docs/features-ratchet.json`). 40 feature tests are stubs that fail
"not written yet" — a lane replaces the stub with the real test.

## The measured distance (the 6.66 run-through, product unchanged since)

Record `docs/runthrough/define_runthrough_20260925T192526.json`: 18 turns, 79 calls,
0 traces. A Belt is stuck at field 5 of 12 (the Confirm cannot complete
`baseline_estimate` + `metric_definitions`); the executor's backstop fired twice at
field 4. 9 of 64 features pass.

## Proven at 6.67 (Part E)

| Check | Result |
|---|---|
| A fresh session's always-loaded context | 3,279 → **1,565 tokens** (CLAUDE.md 2,631 → 1,070 · MEMORY 200 · session start 448 → 295; tiktoken proxy) |
| Full suite in the hook | green on every 6.67 commit (1,213 passed; feature tests xfail/xpass by design) |
| Board and CONTINUITY | regenerate from the features on every commit; rule 10 passes |
| A DEF commit whose test fails | **refused** — `DEF-001 cannot land yet (rule 11)` |
| A DEF commit whose test and dependencies pass | **landed** — `256ffd4` on branch `proof/6.67-landing` |
| The four lanes | rebased onto `1ee1540` and pushed |

The proof found two defects in Part A before any lane did — the session start
printed nothing (`0ae5302`) and rule 5 refused an unchanged, current CONTINUITY
block (`1ee1540`) — both fixed with a test each.

## Speed (6.67 addendum) — before → after, measured

| Measure | Before | After | Source |
|---|---|---|---|
| Hook, a code commit | 138 s wall (669b39c) · 125–128 s pre-commit today | 109–119 s (the suite is the check: 97–114 s of it) | `Timing:` trailers |
| Hook, a docs-only commit | 21.7 s (5d29baa, board 9.5 s + rule 10 9.3 s) | **4.4 s** (312e892), no suite | `time git commit` |
| Pre-flight, a rule file | 12 s | **3.9 s** | timing log |
| Pre-flight, ARCHITECTURE.md | — | 15.5 s | timing log |
| Pre-flight, a leaf module | — | 20.0 s | timing log |
| Pre-flight, a core module (`moves.py`) | 93 s → 53 s | **25.7 s** (27 slow tests left to the hook) | timing log |
| Pre-flight, a change reaching everything | 107 s (a second full suite) | **0 s of tests** — left to the hook | timing log |

The board is one page from the features, the test record and git log (Part A): N of 64 by
clause and lane, the next failing feature per lane, a burn-up to 1 October, the last
commits with their `Timing:` lines. Its projection appears once two days of runs differ.

## Open decisions — FOR FOUNDER (one line each)

- Run-through features are exempt from the ratchet while the record is stale — any product change stales all of them and only a live run refreshes them.
- The 40 missing feature tests exist as failing stubs (so every node id exists), rather than failing the coverage test until written.
- The hooks test the WORKING TREE, not the index: the pre-flight now warns on unstaged edits (6.67's own Part A shipped half-staged once — `796ced5`); running the suite on the index is the deeper fix.
- Old step and gap numbers resolve only in the frozen, archived procedure; new work is named by DEF ids. A new tooling step has no register now.
- From 6.66, still open: the pre-flight escape (`# preflight: acknowledged`); feature tests xfail so a regression shows on the board (and now in rule 11b), not as a red suite; size-budget warn at 90% of size + 10%; the rule-file slimming's sentence-level review; the 24 discrepancies in `docs/define_discrepancies.md` (D1, D2, D3, D7, D8, D9, D15, D21 need you).
