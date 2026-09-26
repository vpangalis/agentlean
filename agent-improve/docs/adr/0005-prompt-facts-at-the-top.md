# 0005. The coach's prompt puts facts at the top

**Status:** SUPERSEDED by 0003 (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §17 note on S-C11 B2

## Context

Step S-C11 ordered the coach's prompt with facts first so that the model saw state before instructions.

## Decision

Facts at the top, then the phase guidance; feedback travels on its own channel, never in `messages[]`.

## Consequences

Superseded by the six labelled sections (0003). The channel rule (feedback never in `messages[]`) survives inside 0003.
