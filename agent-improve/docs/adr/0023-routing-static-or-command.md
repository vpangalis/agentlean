# 0023. A node routes by static edges or by `Command`, never both

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §15

## Context

Mixing the two from one node gives two sources of truth for the next step.

## Decision

Each node uses one routing form. Reaching a phase subgraph's end means the gate passed; the supervisor advances on a static edge.

## Consequences

Routing is readable from the builder alone.
