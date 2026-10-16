# ADR-0073: The coach makes one tool call per response (parallel tool calls off)

Status: PROPOSED (drafted by Claude Code, 2026-09-30, for the founder's ruling; the fix it records was approved in the review of 309f9fc)
Requirements: R1 (every turn a coached reply), T69 (the per-turn model-call budget), DEF-002, DEF-160
Depends on: ADR-0059 (the model-call limit), ADR-0068 / ADR-0069 (the tools offered per turn type)

## Context

G-139. On an answer turn the coach may make one model call (T69: four per turn; the planner's
judgment and the two after-agent checks take the rest). Its structured reply, `CoachingResponse`,
reaches the agent as a tool call: `create_agent` uses `ToolStrategy` because it does not recognise
the Azure deployment name as a model with native structured output.

The live run of 2026-09-30 (define_runthrough_20260930T102427, turn 25, element 10) recorded the
cause: the coach's one call returned **two identical** `CoachingResponse` tool calls in one response
(parallel tool calls). `ToolStrategy` rejects more than one structured response and asks the model
again; that second call is past the answer turn's share, so the call limit ends the loop and code
writes the reply. One run in three showed it.

## Options considered

**A. Native structured output (`ProviderStrategy`).** The reply comes back as JSON content, not a
tool call, so it cannot be duplicated. Checked 2026-09-30:
- the deployments support it at API version 2024-10-21 — `operational-premium` runs
  gpt-4o-2024-11-20, `operational-model` gpt-4o-mini-2024-07-18; a `CoachingResponse` json_schema
  reply was accepted and parsed, alone and beside a strict tool;
- **but not with the coach's tools as they are**: with a JSON-schema response format every bound
  tool must be strict, and Azure rejected the Define executor's real tool set —
  `propose_template`'s schema is not strict-compatible ("'required' is required to be supplied and
  to be an array including every key in properties"). Teaching turns bind those tools, so option A
  needs the tool argument schemas made strict-compatible first.

**B. Parallel tool calls off for the coach (chosen).** Every coach model call is made with
`parallel_tool_calls=False`, so a response holds at most one tool call — one structured reply, or
one lookup. Set in the turn-tools middleware (`backend/middleware/turn_tools.py`), which already
narrows the coach's tools on every call, through `request.override(model_settings=...)`;
`create_agent` passes `model_settings` to `bind_tools`. The structured-output tool is always bound,
so the parameter is always valid.

**Rejected: de-duplicating the two replies in code** (founder, 2026-09-30).

## Decision

Option B. The coach's model calls carry `parallel_tool_calls=False`.

## Consequences

- An answer turn's one call yields exactly one structured reply; the duplicate cannot happen.
- A teaching turn can no longer ask for two lookups in one response; it asks one per call, within its
  two-call share (the last call is offered no tools, G-131). Measured by the run-throughs' model-call
  counts and turn times.
- Option A remains open: making the tool schemas strict-compatible would let the coach use native
  structured output and drop the structured-output tool altogether. That is its own ADR.

## Verification

- `backend/tests/test_g139_one_structured_reply.py`: a scripted coach that returns two identical
  structured replies while parallel calls are allowed; the answer turn ends in the coach's own reply
  within one call, and every bind carries `parallel_tool_calls=False`.
- Two consecutive live run-throughs on main with no code-written reply; DEF-002 and DEF-160 pass;
  M1 46/46.
