# 0020. `step_log` is the audit trail, with deterministic keys

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §11

## Context

Every model call, fallback and verdict must be explainable after the fact.

## Decision

Each node appends dict entries to `step_log`. Keys carry no clock reading, so a replayed step produces the same key.

## Consequences

Audit is complete. §11 claims replay leaves one entry, but the channel appends; either the reducer or the claim must change (drift).
