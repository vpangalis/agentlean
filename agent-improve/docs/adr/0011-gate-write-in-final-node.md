# 0011. The gate write moves into the graph's final node

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §33.2, §45; review ruling 3 (2026-09-26)

## Context

The gate document is written by the route after the graph returns (drift D22), so a crash between the two loses the write and the route holds graph logic.

## Decision

`gate_apply` writes the gate document, as §3.6 and §33.2 already require.

## Consequences

Lane B's next item. The node then needs the error handler that undoes an external write (T-list T29).
