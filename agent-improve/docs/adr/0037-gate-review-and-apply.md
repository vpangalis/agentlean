# 0037. The gate is two nodes: review pauses, apply writes

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §33.1, §33.2

## Context

A single gate node could not pause for a human and then write safely.

## Decision

`gate_review` presents validated fields and calls `interrupt()`, with no model call. `gate_apply` applies the decision, writes the gate document and routes on.

## Consequences

The pause is resumable; the write happens once, after approval.
