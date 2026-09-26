# 0054. The tree at HEAD is the only source of truth

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §56.3

## Context

Plans, logs and memory disagreed with the code.

## Decision

What the committed tree says wins; documents are corrected to match it.

## Consequences

Every claim in a document can be checked against code.
