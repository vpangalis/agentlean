# 0009. One resume route: POST /gate/decision

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §49; review ruling 1 (2026-09-26)

## Context

The pause needed a way back into the graph. Two routes (one per decision) would duplicate the resume logic.

## Decision

Approve and reject both resume the paused graph through `POST /gate/decision`. It answers 409 when nothing is waiting.

## Consequences

One place to secure when R8 lands. The UI sends one request for both decisions.
