# 0046. A dropped client abandons the turn

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §47

## Context

Finishing a turn nobody receives wastes calls and may commit an unseen change.

## Decision

On disconnect the run is cancelled and nothing from that turn is committed.

## Consequences

The Belt repeats the message; no half-turn state.
