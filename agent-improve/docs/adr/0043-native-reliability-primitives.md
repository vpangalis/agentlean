# 0043. Reliability uses LangGraph's primitives, not a hand-written saga

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §44, §45

## Context

Hand-written compensation frameworks drift from the engine they wrap.

## Decision

Every executor node has a `TimeoutPolicy`; every node with external writes has an `error_handler` that undoes the write. Graceful shutdown is required, but its mechanism is unconfirmed and must not be scheduled against an unverified API.

## Consequences

Error handlers and drain are not built yet (T-list gaps).
