# 0022. A phase subgraph is a cycle of five nodes

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §13, §14

## Context

Pipelines of many small nodes made revision loops hard to follow.

## Decision

Planner, executor, validation stack, gate review, gate apply. After each executor step control returns to the planner. Revision is an edge, not a node. A sixth node needs an amendment.

## Consequences

The shape is fixed and testable. Policy advice lives inside `gate_apply`.
