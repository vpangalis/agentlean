# 0024. The thread id is the case id

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §16

## Context

Checkpoints must be found again for a case after a restart.

## Decision

Every invoke carries `thread_id` = `case_id`; a call without it fails. Subgraphs use their own `checkpoint_ns` under that thread.

## Consequences

Resume after restart is by case. Once R8 lands, the id must come from an authenticated session (T-list T12).
