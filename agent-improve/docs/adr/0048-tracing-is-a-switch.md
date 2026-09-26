# 0048. Tracing is a switch, required in production

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §51

## Context

Tests and local runs must not send traces; production must never run blind.

## Decision

With tracing off, no trace is created. In production, start-up refuses to run without LangSmith.

## Consequences

The production refusal is not built yet (T-list gaps).
