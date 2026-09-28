# ADR-0059 — Call budget and model fallback use LangChain's built-in middleware; the hop budget stays custom

Status: ACCEPTED (founder, 2026-09-28) · Requirements: T69, T34 · CLAUDE.md rule 0.24

## Context
T69 caps model calls per ordinary turn; T34 asks for a model fallback when the primary fails. Both
were designed as hand-built mechanisms. LangChain 1.x ships `ModelCallLimitMiddleware`
(`run_limit`, `exit_behavior`) and `ModelFallbackMiddleware` (`first_model`, further models) in
`langchain.agents.middleware`. The hop budget (`COACH_HOP_BUDGET`) caps `rag_lookup_*` calls as one
shared budget across three tools; `ToolCallLimitMiddleware` limits one `tool_name` per instance.
Verified on the installed langchain 1.3.16 (2026-09-27): `ToolCallLimitMiddleware(*, tool_name: str | None = None,
thread_limit, run_limit, exit_behavior)` — `tool_name=None` counts every tool call, a name counts one tool;
neither counts the three `rag_lookup_*` tools together while leaving the other tools free.

## Decision
1. T69 is enforced by `ModelCallLimitMiddleware(run_limit=…, exit_behavior="end")` on the executor.
   Calls outside the agent (the planner's judgment, the grader, coherence) are counted in
   `step_log` against the same budget.
2. T34 uses `ModelFallbackMiddleware` from the premium to the operational deployment; the degraded
   answer after the last model stays in code.
3. The hop budget stays custom: a shared cap over three tools cannot be expressed with
   `ToolCallLimitMiddleware`. Revisit if LangChain adds a multi-tool limit.

## Wiring
Both middleware join the executor's list in `phases/nodes_common.py::_build_executor`; their
declared position is set so the call limit encloses the retry and the fallback (retries do not
count as new turns' calls beyond the limit). ARCHITECTURE.md §3.3 changes in the building commit.

## Rejected
Hand-written counters and fallback levels (rule 0.24); three per-tool limits (would not cap the
total).
