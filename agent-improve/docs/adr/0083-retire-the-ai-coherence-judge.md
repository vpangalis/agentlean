# ADR-0083: The AI coherence judge (layer 2a) is retired

Status: ACCEPTED (founder, 2026-10-13; drafted by Claude Code from the ruling)
Requirements: R1 (guide the Belt through the method); T64 (retired with it); DEF-013, DEF-014 (retired with it)
Supersedes: ADR-0079 (the coherence re-ask); ADR-0081 decision 2's coherence half (its log-only mode)
Depends on: ADR-0081 (the judges are independent: the grader is unaffected), ADR-0059 (T69's call budget)

## Context

Layer 2a (`CoherenceMiddleware`) asked one model, every turn, whether the coach's reply was a real
statement: not parroting, on the phase, asking something. Against the founder's labels on the 40-turn
evaluation set (2026-10-13) it rejected 44% of the good replies (40% on replay), passed 27% of the bad
ones, and gave the wrong reason on 9 of the 13 rejections that were right. It ran log-only from G-161 and
re-asked nothing. What the labels found wrong in the replies is now caught in code (G-170 to G-175, G-168):
the sample, duplicated blocks, the status answer, numbers without a source, a placeholder read back, a
re-confirm after a store, the planner's baseline reading. The code checks proposed as its replacement
(option B: real, asks, not parroting, on the phase) rejected none of the 15 bad replies.

## Decision

1. `CoherenceMiddleware` leaves the coach's middleware; no other check replaces it.
2. Its log-only record (`step_log`, layer `coherence`) stays until the removal is committed, and is gone
   with it; earlier records keep theirs.
3. The after-agent calls in T69's budget go from two (coherence, grader) to one (the grader): the coach's
   share of a turn's four model calls rises by one.
4. Retired with it: T64 (the grader stood down on a coherence verdict — already overtaken by ADR-0081),
   DEF-013 (the judge rules on the Belt's words) and DEF-014 (the re-ask), and the run test that a
   restating move is not taken for parroting.

## Consequences

- One fewer model call per turn (about 5% of a walk's cost on gpt-4o-mini) and no layer-2a latency.
- The validation stack's layer 2a (§9.2) is gone; layers 2b to 2d are unchanged.
- The grader stays log-only until it passes ≥ 90% repeatability and the 20% thresholds (founder, B2).

## Rejected

- **Option B's code checks as the replacement**: on the labelled set they rejected nothing (0% false
  rejects, 100% false accepts) — a check that never fires is cost without signal.
- **Keeping the judge log-only**: a signal wrong on four good replies in ten is noise in every record.

## Notes

Note (founder, 2026-10-14): The purpose of 2a, keeping unusable Belt input out, is served before the coach by the input guard (T71, T93), the planner's judgment of each substantive answer (T47, ADR-0007) and the code copy check (G-159); a separate pre-LLM coherence call would duplicate T47's single judgment.
