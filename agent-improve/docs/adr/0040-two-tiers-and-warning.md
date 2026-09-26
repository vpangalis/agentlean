# 0040. Two tiers of field, and a warning verdict

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §35

## Context

Not every field should block a gate in every phase.

## Decision

Tier 1 fields block; Tier 2 fields can only warn. Define has no Tier 2 (0004).

## Consequences

A Tier 2 criterion can never fail a gate; this is not yet tested.
