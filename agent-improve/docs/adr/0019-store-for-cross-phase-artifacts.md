# 0019. The Store carries artifacts across phases

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §9, §42

## Context

The next phase needs the previous phase's approved output, but must not read its working state.

## Decision

At gate approval the output mapper writes the phase's artifacts to the Store. The next phase's input mapper reads them from there. A key never written returns nothing, never an error.

## Consequences

Phase boundaries are explicit and replay-safe (writes are idempotent on the key).
