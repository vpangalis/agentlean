# 0047. One structured error schema for every external failure

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §48

## Context

Breakers and fallbacks need to know whether to retry.

## Decision

`AgentImproveError` carries severity and a retry recommendation; every external failure uses it.

## Consequences

Retry decisions are data, not string matching.
