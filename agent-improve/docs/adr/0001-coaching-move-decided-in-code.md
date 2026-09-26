# 0001. The coaching move is decided in code, never by a model

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §17 (v1.75), §43 (v1.75), §58 S-C04; `.claude/rules/coaching-move.md`

## Context

Before v1.75 the coach model chose what to do next, and the same turn run twice could teach once and advance the next time. The Belt could not rely on the order of coaching.

## Decision

Code picks the move from the field's status: not yet taught → teach; answered but insufficient → challenge; answered and sufficient → read back; confirmed → store and advance. A model only judges sufficiency and writes the coach's words. Coaching rules and phase scripts contain no move-sequencing. The plan's `move` replaces `next_action`.

## Consequences

The same turn makes the same move every time, so every step touching coaching carries a five-run consistency test. Adding a move is a code change, not a prompt change. Open: a confirmed field has no move that revises it (G-110).
