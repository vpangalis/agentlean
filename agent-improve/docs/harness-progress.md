# Harness progress — step 6.66

The long-running-harness progress file (Anthropic, *Effective harnesses for
long-running agents*). **Replace, don't append** — this file holds the current
state; git holds the history.

## Session-start routine (every session, every lane)

1. `git log --oneline -5`; read this file.
2. `python agent-improve/tools/control_board/features.py` — Define features
   passing, and the next failing feature per lane. The SessionStart hook prints
   the same. Status comes ONLY from `docs/test-results.json`.
3. Smoke test: `cd agent-improve; pytest backend/tests/test_define_features.py -n 0`.
4. `python agent-improve/tools/control_board/features.py --lane <A|B|C|integrator>`
   — take the first failing feature whose dependencies pass. Make its test pass
   end to end. Never edit a feature to say it passes; there is no status field.

## Overnight run 2026-09-25 → 26 (founder ruling, step 6.66)

| Part | What | State | Commit |
|---|---|---|---|
| A | Permission warm-up | DONE | — |
| 0 | Register 6.66 + this file | DONE | 5d29baa |
| 1 | Measure first | DONE — baseline below | 5d29baa |
| 2 | Speed: pre-flight, xdist, repeat report | DONE | d00c4cf |
| 3 | Guard rule 6 narrowed; rule files slimmed; CLAUDE.md rules-only | DONE (CLAUDE.md in the commit after Part 5) | 189c672, 69e9200 |
| 4 | Slim ARCHITECTURE.md + procedure; size budget; section index | DONE | ddb30fe, 3496e16, 22ddd0d |
| 5 | define_features.json, status from tests, coverage test, discrepancies, routine | DONE | (this commit) |
| 6 | Lanes A/B/C + integrator: branches, worktrees | next | |
| 7 | Define run-through test, once on main, ≤150 live calls | | |
| 8 | G-23 design draft, G-40 rubric draft | | |
| 9 | Fresh-eyes review | | |

## Baseline (Part 1, 669b39c) and after

| Measure | Before | After | How |
|---|---|---|---|
| CLAUDE.md | 418 lines · 6,370 tok | 150 lines · ~2,540 tok | tiktoken cl100k (proxy) |
| Rule files (13) | 3,019 lines · 36.2k tok | 1,687 lines · 19.6k tok | same |
| ARCHITECTURE.md | 12,928 lines · 237k tok | 11,655 lines · 165k tok | same |
| REFACTORING_PROCEDURE.md | 8,468 lines · 175k tok | 5,242 lines · 123k tok | same |
| Full suite (hook, `-n auto`) | median 114 s, 1,327 tests | 96–116 s, 1,339 tests | timing log |
| Area runs | `-n auto` 34–54 tests: 22–30 s | pre-flight serial ≤ 12 files | timing log |

## Night decisions and findings — FOR FOUNDER (one line each)

- **Pre-flight escape**: `# preflight: acknowledged — <why>` passes a pre-flight failure that fails identically at HEAD; the commit hook still gates. Undo: delete `ACK_RE` in `preflight-on-commit.py`.
- **Rule 6's D-label trigger removed** with the subject-code trigger, reading the ruling's two triggers literally; a volunteered half-written 8D on a non-defect commit is no longer refused. Undo: restore `ANY_D_LABEL_RE` in `is_fix_commit`.
- **Size budget warns from day one**: bound = size + 10%, warn at 90% of bound = 99% of today's size. If "90%" meant 90% of the headroom, change `WARN_AT` in `size_budget.py`.
- **Coverage test's gap set** uses two mechanical legs (the register's Step cell; founder milestones blocking a Define step) — 14 gaps — not G-numbers mentioned in card prose (28), because prose moves.
- **ARCHITECTURE.md slimmed only 30%**: what remains is current spec; going further means moving "why" paragraphs out of the spec — needs a ruling on which reasoning is load-bearing.
- **Change log lost text before tonight** (procedure v1.4 tail, v1.3): the pre-commit splice starts at the first BEGIN marker, and v1.4 quoted it (ed9aa1b). v1.3 recovered to the archive; `splice()` stays fragile.
- **Board's short Done-when reader** reads a fixed 900 chars and can run into the next card (6.14).
- **`test_turn_budget`** fails under CPU load (seen twice tonight) and passes alone — a timing-sensitive test.
- **Non-spine commits are never blocked by a red suite** (rule 4 gates `refactor(arch-v2)` only); the pre-flight now catches it earlier.
- **`§19.x`/`§20.x` citations** in CLAUDE.md resolve to no heading (pre-existing).
- **Kept though stale** in the rule files' Never lists: rag.md's "ratified-but-unapplied index fields" (both live), state.md's "seven fields" and the "N of 95" captions.
- **G-53** (premium deployment 429) was mentioned only in archived changelog entries; its register row stands.
- The 24 source discrepancies with their decisions: `docs/define_discrepancies.md` (D1, D2, D3, D7, D8, D9, D15, D21 are FOR FOUNDER).

## Next

Part 6 — lanes. Then Part 7, the run-through (≤ 150 live calls, run once).
