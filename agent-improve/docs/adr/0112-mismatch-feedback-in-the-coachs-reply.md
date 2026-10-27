# ADR-0112: Mismatch feedback in the coach's reply

Status: ACCEPTED (founder ruling 2026-10-27; placed by Claude Code from the ruling's text)
Requirements: founder ruling 2026-10-27 on the coaching grader and mismatch feedback (B, D) and its addition (F7)
Refines: ADR-0042 (its deferral to Measure, through DEF-040's pause node, is superseded)

## Context

The founder's purpose for the judges (2026-10-14): the Belt gets feedback when an entry does not fit the previously
confirmed values or the BB reference book, then moves on. The coach already detects mismatches every turn
(contradiction_flag), but nothing reaches the Belt; DEF-040 planned a pause node before Measure.

## Decision

A mismatch is told to the Belt in the coach's reply, with the conflicting value or rule named, and the choice to
correct or keep. Keeping is recorded, dated. No pause, no interrupt, no new node, no extra model call. The grader
checks that a mismatch was not missed (G6). It applies in every phase. On a counted grader fail in enforce mode the
coach rewrites once, inside the grader middleware, before the Belt sees the reply.

## Consequences

DEF-040's node is dropped; ADR-0042 is not deferred to Measure; four Define eval tasks are added and one Measure task
is recorded.

## Rejected

The ruling records no rejected alternative.
