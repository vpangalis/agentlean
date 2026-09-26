# Harness progress — Define on the long-running-harness pattern

**Replace, don't append** — the current state only; git holds the history, and the
overnight run's full record (6.66) is in commit `a3364ae`'s version of this file.

The three layers (step 6.67): how to work — `CLAUDE.md` and `.claude/`; what must
be true — `docs/define_features.json` + `docs/test-results.json` (the board,
`docs/control-board.html`, and CONTINUITY's block are generated from them); why —
`ARCHITECTURE.md`, read only by the cited section via `docs/section-index.md`. The
session-start routine is in CLAUDE.md.

## Requirements (founder-owned, 2026-09-26)

`docs/requirements/define.md` R1–R7 — every Define feature cites one in `requirement`; `platform.md`
R8–R9 are not Define features; `workspace.md`, `measure.md` and define.md's R10 are DRAFTS no feature
cites. Parts 0–8 landed 2026-09-26 (`a006cea` … the part 8 commit): 13 elements with acceptance
criteria, R3's judgment before the coach, the Define report, acceptance through a graph-level pause,
the R7 rubric. New features DEF-065–072 (R2–R7).

## Lanes (branches and worktrees beside this checkout; `.venv` is a junction)

| Lane | Branch · worktree | Starts at |
|---|---|---|
| A — coaching | `lane/a-coaching` · `../AgentLean-lane-a-coaching` | DEF-005 first (strict dependencies), then the Confirm at field 5 (DEF-008, DEF-029) |
| B — gate | `lane/b-gate` · `../AgentLean-lane-b-gate` | DEF-040 — the stop is a node (D1, ruled); row 24 (DEF-062) |
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

## Founder rulings on the 6.67 report (2026-09-26) — applied at 6.68

| Question | Ruling | Where it is now |
|---|---|---|
| Run-through features and the ratchet while the record is stale | Exempt — accepted; the integrator re-runs `scripts/define_runthrough.py` after each merge | `features.ratchet_refusal` |
| Feature tests not written yet | Stubs that fail "not written yet" — accepted | `backend/tests/test_define_*.py` |
| What the hooks test | What is STAGED: a second worktree set to the index (`.claude/hooks/staged_tree.py`) runs the suite, mypy and the pre-flight | `.githooks/pre-commit`, guard rules 3 and 4, `preflight.py` |
| Registering tooling work | None: `chore(tooling):` names no DEF id and passes on the checks alone | guard rule 8 (`TOOLING_RE`) |
| Dependency blocking | Strict, transitively; lane A fixes DEF-005 first | `features.blockers` — the next feature and rule 11 |
| agent-resolve broken links | Ignored until Resolve is refactored | — |
| Pre-flight override | No hand-written "acknowledged"; a failure passes only if HEAD's record has it (`test-results.json` at HEAD; the drift check on HEAD's tree) | `preflight.py`, `preflight-on-commit.py` |
| Size budget | Warn above base + 5%, refuse above base + 10% (the bound) | `size_budget.py`, rule 12 |
| Rule sentences the slimming weakened | An automatic check: rule 14 (`normative_check.py`); against the pre-slimming corpus 71 candidates → 8 rule sentences restored, 63 classified (41 kept in other words, 21 rationale, 1 obsolete) in `.claude/config/normative-retired.json`, open to review | guard rule 14 |
| Discrepancies D1, D2, D3, D7, D8, D9, D15, D21 | D1 the stop is a node · D2/D21 "works end to end" = all features, the five-clause core a second number, row 24 to the gate lane · D3 structural tests now, traced rows marked from one traced run on 30 Sep · D15 row 10 proven by the savings calculation turn · D7–D9 obsolete | the features' descriptions; the file is archived: `docs/_archive/define_discrepancies_2026-09-26.md` |
| Speed | At most ONE code commit per part; docs commits are cheap | — |
