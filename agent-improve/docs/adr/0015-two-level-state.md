# 0015. Two levels of state: a routing supervisor and one state per phase

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §4, §5, §6

## Context

One flat state would let every phase read and write every other phase's working data.

## Decision

`SupervisorState` holds case-level routing only. Each phase subgraph runs on its own `PhaseState`. Artifacts and gate documents never sit on the supervisor state. Field sets are owned by `backend/core/state.py` and `backend/core/substate.py`.

## Consequences

Phases are isolated; data crosses a phase boundary only through mappers and the Store (0019). The §4 diagram's field count has drifted from the owner.
