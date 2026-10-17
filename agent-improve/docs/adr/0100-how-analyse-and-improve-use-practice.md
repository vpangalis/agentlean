# ADR-0100: How Analyse and Improve use practice

Status: ACCEPTED (founder, 2026-10-17; drafted by Desktop, 2026-10-17). Scheduled after Define — no build now.
Requirements: R22 (Practice intelligence for Analyse and Improve)
Depends on: ADR-0098 "A fourth index: industry practice", the item-28 ADR "Question turns and prompt architecture"

## Decision

1. **Never in Define** ("no cause, no fix" holds).
2. **Analyse:** after the team's own cause brainstorm, the coach may add candidate causes from `typical_failure` chunks for the case's process area — as hypotheses to test with data.
3. **Improve:** after the team's own solution ideas, the coach may add options from `practice` chunks; each goes through the solution selection matrix like any other idea.
4. **Measure / Control:** `kpi_and_benchmark` chunks may suggest what to measure and typical ranges.
5. **The lookup is run by code** for the move that needs it (filters set from the case), not chosen by the model — consistent with ADR-0069 and the item-28 design. One lookup per turn, inside ADR-0080's 45 s.
6. Every practice line in a reply carries its source and section, labelled "practice option".

## Rejected

Practice suggestions before the team's own ideas (anchoring); the model choosing when to search.
