# ADR-0068 — The coach looks up the method on teaching turns only

Status: ACCEPTED (founder, 2026-09-28)
Requirements: T69 (at most 4 model calls per ordinary coaching turn), R13 (45 s hard limit), R2 (teach before asking), R3 (validation before the coach)
Refines: ARCHITECTURE.md §3.6 (tools), ADR-0059 (framework call limits)

## Context

`ModelCallLimitMiddleware` now caps a turn at 4 model calls (G-119, DEF-094). On a turn where the Belt
answers, the planner's judgment, the coach, coherence and the grader share those 4 calls, which
leaves the coach one call. A methodology lookup needs a second coach call, so the turn ends with a
reply written in code: the Belt gets a canned answer.

What each kind of turn needs:

- **Teaching turn** (the element hasn't been taught yet): an explanation, a worked example and the
  question. This benefits from the method in the manual (R2).
- **Answer turn** (the Belt answered): judged against the element's acceptance criteria by the
  planner and the grader (R3), then read back or challenged. The criteria and the worked example are
  already in the coach's state section and in the phase skill.

## Decision

1. On an answer turn, the coach gets no retrieval tools. It reads back, or challenges by naming the
   failed criterion, from the criteria and the example it already has.
2. On a teaching turn, the coach keeps its methodology lookups, within the same 4-call limit.
3. The turn type is decided in code from `field_status` (the element is untaught or taught), not by
   a model. It is recorded in `step_log`.
4. T69's limit stays at 4.

## Consequences

- Answer turns stop ending in code-written replies because a lookup used up the budget.
- Answer turns get faster, since there is no retrieval round trip.
- A Belt question in the middle of an answer ("what is a CTQ again?") is answered from the skill's
  criteria and example, not the manual. If the evaluation set shows that this loses quality, a later
  ADR can allow one lookup on answer turns in exchange for a smaller grader share.
- ARCHITECTURE.md §3.6 changes in place: tools per turn type.

## Rejected

- **Raise the limit to 5 or 6 calls.** It moves latency back towards the 45 s wall that G-119 just
  fixed, and it changes a founder requirement.
- **Keep it as is.** A canned reply whenever the coach looks something up on an answer turn is a worse
  experience than no lookup at all.

## Verification

- A test with a stub model shows that an answer turn binds no retrieval tool.
- A test shows that a teaching turn keeps its lookups and stays within 4 calls.
- In the live run-through, no answer turn ends in a code-written reply because of the limit.
