# ADR-0110: The coach's reply schema types its captured values, citations and contradiction flag

Status: ACCEPTED (founder, 2026-10-24; drafted by Claude Code from the ruling)
Requirements: T86 (the eval set); DEF-142; G-252
Refines: ADR-0073 (the coach makes one tool call per response)

## Context

`CoachingResponse` (`backend/core/substate.py`) is the coach's structured reply, bound through `response_format=` on
`create_agent` and parsed by `ToolStrategy`. Until 2026-10-23 three of its fields were untyped: `fields_captured`
`list[dict]`, `citations` `list[dict]`, `contradiction_flag` `Optional[dict]`. Their shape was taught in a
description of 1,200 tokens that carried section, ADR and step codes; the tool schema was 2,338 of the coach's 5,133
prompt tokens on one live E01 turn (`agent-improve/Claude outputs/PROMPT_ANATOMY.md`). The test that pinned the
untyped shape said "a per-phase response schema stays ruled out" (`backend/tests/test_contract_shape.py`), because a
schema that is the only enforcer leaves the value unchecked when the model ignores it.

## Decision

1. `fields_captured`, `citations` and `contradiction_flag` are typed sub-models: `CapturedValue`
   (`field_name`, `value`, `source`, `reason`), `Citation` (extra keys kept) and `ContradictionFlag` (built from
   `CONTRADICTION_FLAG_KEYS`).
2. The phase's field list is an enum: `coaching_response_model(phase)` limits `field_name` to the phase's gate fields
   less those code writes; the executor binds it as `response_format=`.
3. The schema narrows the shape only. Code stays the enforcer: the declared-type check at capture, the worked-example
   refusal and the confirm-only rule run as before.
4. This replaces "a per-phase response schema stays ruled out" (`test_contract_shape.py`). Its reason holds: the
   schema is not the enforcer.
5. `ELEMENT_READS` (`backend/phases/define/schema.py`), the earlier values each element's coaching reads whole, is
   confirmed as written.

## Consequences

- The tool schema the coach receives falls from 2,338 to 863 tokens on the same turn; field shapes travel in the
  read-back's task section (`prompts.FIELD_SHAPES`, `CAPTURE_RULES`).
- A reply naming a field outside the phase's list fails `ToolStrategy`'s parse and is asked again within the
  turn's call share; the coach deployment parsed the typed schema 2 of 2 in the probe (G-252).

## Rejected

- Untyped dicts: the shape lives only in a description the model may ignore, and the description cost 1,200 tokens.
- Strict mode (`ProviderStrategy` or strict tools): Azure refuses the coach's tool set as strict (ADR-0073).
