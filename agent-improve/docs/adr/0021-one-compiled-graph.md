# 0021. One compiled graph is the only runtime path

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §12

## Context

Routes that dispatched nodes by hand behaved differently from the graph.

## Decision

One supervisor graph with one subgraph per phase and an escalation subgraph. `/ask`, `/ask/stream` and `/gate/*` all invoke the same compiled object. Entry uses `add_edge(START, ...)`.

## Consequences

What is tested is what runs. Routes contain no graph logic (see 0011).
