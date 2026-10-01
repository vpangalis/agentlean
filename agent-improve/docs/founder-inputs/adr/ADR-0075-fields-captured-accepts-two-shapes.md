# ADR-0075: `fields_captured` accepts `{}` as `[]` and a single entry as a one-item list

Status: ACCEPTED (founder, 2026-10-01; drafted by Claude Code from the ruling)
Requirements: R1 (every turn a coached reply), T69 (the per-turn model-call budget), DEF-002, DEF-160
Depends on: ADR-0073 (one tool call per response), ADR-0059 (the model-call limit), ADR-0068 / ADR-0069
(no tools on an answer turn)
Defect: G-139 (reopened 2026-10-01)

## Context

On an answer turn the coach has one model call (T69: four per turn; the planner's judgment and the
two after-agent checks take the rest — G-119). Its structured reply, `CoachingResponse`, reaches the
agent as a tool call (`ToolStrategy`). When the reply fails validation, `ToolStrategy` asks the model
again; the call limit refuses the second call and the turn ends in a reply written in code.

ADR-0073 removed one cause (two structured replies in one response). Live runs on 2026-10-01 showed
the other: `fields_captured`, a list, came back in two other shapes:

| Run | Turn | Move | Shape |
|---|---|---|---|
| 083638 | 10 | challenge | `{}` — an empty object |
| 104934 | 8 | challenge | `{}` |
| 104934 | 33 | read-back | one entry object `{field_name, value, source}`, not a list of one |

On 104934 DEF-002 (M1) and DEF-160 failed on those two turns.

## Decision

1. `CoachingResponse.fields_captured` reads an empty object `{}` as `[]`, and a single entry object
   (a dict carrying `field_name`) as a one-item list. A `field_validator(mode="before")` in
   `core/substate.py` does it; the JSON schema the model is shown is unchanged (an array).
2. Any other shape still fails validation as before.
3. Every normalization is recorded in the turn's `step_log` entry as
   `fields_captured_normalized: [{turn, element, shape}]`, `shape` being `empty_object` or
   `single_entry` — so how often the model sends each shape stays measurable.

## Consequences

- No extra model call: T69 and G-119 are unchanged; the answer turn keeps its one call.
- The read-back's single entry is stored like any other once the Belt confirms (nothing about what is
  stored changes; only the parse).
- The rate of each shape can be read from `step_log` across runs; if another shape appears, it fails
  as today and is a new finding.

## Rejected

- **Admit one structured-output retry on an answer turn.** Five calls in the turn against G-119's four,
  and 5–10 s more on those turns.
- **Both (accept the shapes and admit a retry).** The retry would serve shapes not seen yet; not needed
  for the two observed.
- **Hold and land package 2a on route tests only.** Leaves M1 failing on the live record.

## Verification

- Unit: `test_g139_one_structured_reply.py::test_g139_an_invalid_structured_reply_still_ends_in_a_coached_reply`
  — both shapes end in the coach's own reply within one call, and step_log carries
  `{turn, element, shape}`.
- Live: package 2a's re-run — DEF-002 and DEF-160 pass, M1 46/46, under USD 1.50.
