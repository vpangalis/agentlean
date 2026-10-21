# ADR-0104: The upload interpretation binds structured output — pattern 2 gains exactly one path exclusion

Status: ACCEPTED (founder and Desktop, 2026-10-21 evening; drafted by Claude Code from the ruling)
Requirements: T100 (G-48); DEF-238
Depends on: `.claude/rules/llm.md` §4.3 and §4.6; `.claude/config/deprecated_patterns.yaml` pattern-2

## Context

`backend/upload/agent.py` makes two plain model calls per upload — the interpretation and the image read — and parses
JSON out of the model's text (`_json_object`): against §4.3 ("Never parse JSON from raw LLM text"), and an unreadable
reply silently loses the interpretation. §4.6 scopes a plain model call inside a tool, middleware or validator to the
builder-style `with_structured_output`, but pattern 2 blocks it everywhere but its listed paths, and `backend/upload/`
is not listed. The facts were drafted for Desktop on 2026-10-21
(`agent-improve/Claude outputs/ADR_facts_DEF-238_pattern2_upload.md`).

## Decision

1. Add exactly one path exclusion to `pattern-2-with-structured-output`: `agent-improve/backend/upload/agent.py`.
2. Both upload calls bind `with_structured_output`: the interpretation to `UploadInterpretation`, the image read to a
   one-field typed schema.
3. `_json_object` is removed.
4. Assumption checked before building: the vision deployment accepts the builder-style structured-output call
   (ADR-0073 records Azure refusing strict `ProviderStrategy` for the coach). If it does not, the build stops and the
   finding is reported.

## Rejected

- Keep parsing JSON: violates §4.3 and silently loses the interpretation.
- `create_agent` for a non-agent call: §4.6 scopes `response_format=` to agents.
- Moving the code into an excluded package to suit the guard.
