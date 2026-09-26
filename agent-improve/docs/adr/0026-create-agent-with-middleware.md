# 0026. The executor is `create_agent` with middleware

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §18, §19.9

## Context

Tools bound onto a bare model bypass retry, injection and grading.

## Decision

Phase executors are built with `create_agent`, `response_format=CoachingResponse`, `system_prompt=` and the full middleware stack. `create_react_agent`, `langgraph.prebuilt` and the deepagents package are not used.

## Consequences

Revisit deepagents at its 1.0; migrate the custom middlewares together or not at all.
