# ADR-0069 — Answer turns bind no tools; upload turns count as teaching turns

Status: ACCEPTED (founder, 2026-09-28)
Requirements: T69 (at most 4 model calls per turn), R13 (45 s), R3 (validation before the coach), W5 (uploads strengthen answers), C1 and C2 (reports and visuals from confirmed values)
Refines: ADR-0068 (the coach looks up the method on teaching turns only). ADR-0068 stays in force; this ADR widens its rule from retrieval tools to all tools and adds the upload case.

## Context

ADR-0068 removed only the retrieval tools from answer turns. In the live run after it, 7 of 34 turns
still ended in a reply written in code, 3 of them answer turns (G-128). The coach's single allowed call
went on a tool that stayed bound: templates, diagrams, evidence series, computation or `load_skill`.

What an answer turn has to do: judge the answer against the element's criteria, which the planner and
the grader do, then read back or challenge. None of that needs a tool:

- Diagrams and report templates are drawn in code from stored, confirmed values (C1, C2).
- Deterministic calculations belong to their single computing authority in code (T54), and run on
  the confirmed values.
- The method content of the element is already in the coach's context.

The one real case that needs a tool is a Belt referring to an uploaded file. That is an upload turn,
not an answer turn.

## Decision

1. **Turn types, decided in code** from `field_status` and the request (no model), recorded in `step_log`:

   | Turn type | When | Coach tools |
   |---|---|---|
   | teaching | the current element is untaught | lookups, templates, `load_skill`, within the 4-call limit |
   | upload | the turn carries a new upload, or the Belt refers to one not yet read | evidence and upload tools, within the 4-call limit |
   | answer | anything else | **none**: a structured reply only |

2. Diagrams and templates shown after a Confirm are produced in code from the stored values, not
   through a coach tool call.
3. T69 stays at 4.

## Consequences

- Answer turns can no longer end in a code-written reply because the coach spent its call on a tool.
- Answer turns get faster.
- If the Belt asks for a calculation in an answer, the coach reads the numbers back. The calculation
  runs in code once they're confirmed, or the coach offers it on the next teaching turn.
- ARCHITECTURE.md §3.6 changes in place: a tools-per-turn-type table.

## Rejected

- **Let a structured reply follow one tool call.** That means two coach calls, so five in total. It
  breaks T69 and moves latency back towards the 45 s wall.
- **Keep ADR-0068 as is.** G-128 shows it still produces canned replies.

## Verification

- A stub-model test shows that answer turns bind no tools.
- A test shows that an upload turn binds the evidence tools.
- In the live run-through, no turn ends in a code-written reply because of the limit (ADR-0068's check,
  now passing).
