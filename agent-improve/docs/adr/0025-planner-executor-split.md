# 0025. Planner and executor are separate nodes, joined by a structured plan

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §17

## Context

A fused plan-and-act agent could not be tested for what it intended to do.

## Decision

The planner writes a structured plan (focus field, move, retrieval strategy, tools). The executor carries it out. The plan replaces the previous one; it is never queued.

## Consequences

Plans are inspectable in state and testable without a model.
