# 0051. Facts have one owner; documents cite, never copy

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §55.4

## Context

Counts copied into documents went stale (field counts, versions).

## Decision

Dependency versions are owned by `requirements.txt`; field names and counts by the schema modules. A document that states such a number must cite the owner on the same line; a hook refuses it otherwise.

## Consequences

Documents shrink to reasons; numbers are read from code.
