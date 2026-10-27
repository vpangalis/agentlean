# 0042. A contradiction of an approved value triggers re-approval

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §37

## Context

A Belt may later contradict a number approved at an earlier gate.

## Decision

Contradiction detection raises a flag; the approved gate is re-opened through a cascade rather than silently overwritten.

## Consequences

Depends on error handlers that undo external writes (T-list T29).

## Notes

Note (founder, 2026-10-27): its deferral to Measure — DEF-040's pause node — is superseded by ADR-0112: a mismatch is
told in the coach's reply, the Belt corrects or keeps it, and the conversation moves on; no pause, no new node.
