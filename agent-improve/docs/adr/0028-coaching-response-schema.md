# 0028. `CoachingResponse` is the executor's only output schema

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §20

## Context

Returning a phase output schema from each turn confused a turn with a gate document.

## Decision

The executor returns `CoachingResponse` through structured output. Gate documents are assembled in code from artifacts, with no model call. JSON is never parsed from raw text.

## Consequences

Shape is guaranteed; truth is checked by validation (0039).
