# ADR-0081: Two independent judges on every reply, each log-only until proven

Status: ACCEPTED (founder, 2026-10-13; drafted by Claude Code from the ruling)
Requirements: R1 (guide the Belt through the method); DEF-015; G-161, G-162
Supersedes: ADR-0041 (two graders; "the grader stands down when coherence has degraded" — S-C13 B3)
Depends on: ADR-0079 (the coherence re-ask), ADR-0059 (call limits)

## Context

Layer 2a (`CoherenceMiddleware`) asks whether a reply is a real statement; the coaching grader
(`DMAICGraderMiddleware`) grades the coach's process against `COACHING_QUALITY_RUBRIC`. Under S-C13 B3 a
coherence rejection switched the grader off for the turn. The offline evaluation set (2026-10-12) showed
the coherence judge's rejections mostly false (G-161) and the grader failing about half the replies it
graded, with verdicts that do not repeat on replay; a false coherence alarm therefore deleted the very
quality measurement that should have been taken (G-162: fewer than 90% of turns graded).

## Decision

1. **The judges are independent.** Both run on every reply that has text and record their verdicts in
   `step_log` independently; a coherence rejection never switches the grader off. Coherence is a sanity
   check, the grader a quality check; a sanity check's false alarms must not delete quality measurements.
   Empty replies and replies written in code stay ungraded, as before.
2. **Each judge runs `log_only` until it is proven against the founder's labels** (`scripts/judge_replay.py`):
   - coherence (`COHERENCE_MODE`): until its false-reject rate is under 20% (G-161);
   - the grader (`GRADER_MODE`): until verdict agreement on replay is at least 90% and false fails are under 20%.
3. **Log-only changes nothing else:** the verdict is recorded; there is no re-ask (ADR-0079), no
   Belt-visible warning (`GRADER_WARNING`), and the verdict does not reach the coach's next-turn quality
   feedback. In `enforce` mode each judge does what ADR-0079 and §8.2 describe.
4. DEF-015's coverage counts every reply sent.

## Consequences

- One grader call on every reply with text, coherence-rejected ones included — already counted in T69's four.
- `step_log`'s coherence record keeps `degraded` and drops `grader_skipped`; each judge's record carries its mode.
- Removing a containment is a one-line mode change, made only when the replay meets its thresholds.

## Rejected

- **Keeping the skip (S-C13 B3).** It made the quality measure depend on the least reliable judge.
- **Grading only re-asked replies.** Leaves rejected replies unmeasured — the weakest replies (DEF-015 option B).

## Verification

- `backend/tests/test_middleware.py::test_the_grader_grades_every_reply_whatever_coherence_decided` — the
  grader takes no coherence reference, grades a reply, records a FAIL and returns no warning in log-only.
- `backend/tests/test_coherence_script_step.py::test_every_rejection_records_its_reason_in_step_log` — a
  rejection degrades the turn and records no grader skip.
- The tests of the Belt-visible warning run in `enforce` mode (`grader_enforced`).
- The next live run reports the graded share of coaching turns (DEF-015).
