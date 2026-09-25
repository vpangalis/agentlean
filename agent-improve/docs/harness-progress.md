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
| 0 | Register 6.66 + this file | DONE | 5d29baa |
| 1 | Measure first | DONE — baseline below | 5d29baa |
| 2 | Speed: pre-flight, xdist, repeat report | DONE — see Part 2 below | (this commit) |
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

## Part 2 — speed (what was built)

- `.claude/hooks/preflight.py`: drift, built markers, mypy over the changed
  Python AND its direct importers (rule 3's baseline), and the tests of both
  plus every test naming a changed document or a hook/tool that reads it — all
  four in parallel; serial (`-n 0`) at 12 test files or fewer. `--plan` shows
  the selection. Times itself into the timing log (`kind: preflight`).
- `.claude/hooks/preflight-on-commit.py` (PreToolUse, Bash|PowerShell): runs the
  pre-flight before every `git commit`, blocks on failure (exit 2). Fail-soft
  if the hook itself breaks.
- Kept: the one full parallel run per commit in the pre-commit hook.
- Found on its first run: `verify_built` "facts with nothing to anchor to"
  37 → 38 — the 6.66 registration commit had not moved the pin. Fixed.
- Found: `-p no:xdist` breaks the conftest (it defines `pytest_testnodedown`);
  serial is `-n 0`.
- Found: `test_turn_budget` (2 tests) fails under CPU contention and passes
  alone (3 passed, 5.7 s) — a timing-sensitive test.

Area-test repeats in the 6.61 prompts (timing log):

| Prompt | Runs | Full | Area | Back-to-back same-count | xdist on < 200 tests |
|---|---|---|---|---|---|
| 6.65 + 6.61 part A | 12 | 3 (339 s) | 9 (134 s) | 3 | 4 (107 s) |
| 6.61 part B | 30 | 0 | 30 (583 s) | 9 | 5 (160 s) |
| 6.61 review + commit | 7 | 2 (207 s) | 5 (136 s) | 1 | 3 (111 s) |

## Next

Part 3 — CLAUDE.md to rules and pointers (≤ 150 lines); guard rule 6 narrowed.
Parts 4 and 5a are running in sub-agents (worktrees); their output lands here.
