# 0017. The checkpointer and the store attach to the parent graph only

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §8, §16

## Context

A subgraph compiled with its own checkpointer writes a second, conflicting history.

## Decision

The supervisor graph is compiled with the checkpointer and the store. Every phase subgraph is compiled with neither and inherits them.

## Consequences

One checkpoint history per case. Tests that need a checkpointer use an in-memory saver, which §8 says is never used; §8 needs correcting to say 'never in production'.
