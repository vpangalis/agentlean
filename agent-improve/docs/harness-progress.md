# Harness progress — step 6.66

The long-running-harness progress file (Anthropic, *Effective harnesses for
long-running agents*): a session reads this, `git log`, and
`docs/define_features.json` first, then runs the smoke test, then takes the
next failing feature in its lane. **Replace, don't append** — this file holds
the current state, not a diary; git holds the history.

## Overnight run 2026-09-25 → 26 (founder ruling, step 6.66)

| Part | What | State | Commit |
|---|---|---|---|
| A | Permission warm-up | DONE | — |
| 0 | Register 6.66 + this file | DONE | (this commit) |
| 1 | Measure first | DONE — baseline below | (this commit) |
| 2 | Speed: pre-flight, xdist, repeat report | next | |
| 3 | CLAUDE.md → rules and pointers; guard rule 6 narrowed | | |
| 4 | Slim ARCHITECTURE.md + procedure; size budget; section index | | |
| 5 | define_features.json, status from tests, coverage test, discrepancies | | |
| 6 | Lanes A/B/C + integrator: branches, worktrees | | |
| 7 | Define run-through test, once on main, ≤150 live calls | | |
| 8 | G-23 design draft, G-40 rubric draft | | |
| 9 | Fresh-eyes review | | |

## Baseline (Part 1, measured 2026-09-25 at 669b39c)

| Measure | Value | How |
|---|---|---|
| Always-loaded context | CLAUDE.md 24,413 chars / 6,370 tok + MEMORY.md 200 tok + session-start ≈ 250 tok ≈ **6.8k tok** | `tiktoken` cl100k as a proxy (not Claude's tokenizer) |
| + typical `backend/phases` edit | graph + llm + middleware + module-layout + state rule files ≈ **+20.8k tok** | same |
| ARCHITECTURE.md | 12,928 lines · 912k chars · 237k tok | `wc`, tiktoken |
| REFACTORING_PROCEDURE.md | 8,437 lines · 625k chars · 174k tok | same |
| CONTINUITY.md | 1,552 lines · 107k chars · 30k tok | same |
| Rule files (13) | 3,019 lines · 132k chars · 34.2k tok; largest state.md 8.3k, middleware.md 6.5k, gates.md 4.5k | same |
| Full suite (hook, `-n auto`) | median **114 s** (n=6), 1,327 tests | `.claude/logs/timing.jsonl` |
| Whole commit hook, non-md commit | **138 s** wall (warm-up commit) | `time git commit` |
| Hook parts other than the suite | board 9.5 s + rule 10 board 9.3 s + rule 3 mypy 8.6 s + continuity 3.7 s + rest < 3 s | timing log medians |
| Area test runs | `-n auto` with 34–54 tests: **22–30 s**; serial 1–47 tests: **4–12 s** | timing log |

## Next

Part 2 — pre-flight.
