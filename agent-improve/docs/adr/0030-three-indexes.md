# 0030. Three search indexes with separate purposes

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §23, §24

## Context

Method knowledge, past cases and the Belt's evidence have different owners, lifetimes and filters.

## Decision

A knowledge index, a case index and an evidence index, each searched by its own `rag_lookup_*` tool. Evidence is filtered by case.

## Consequences

Filters can be strict per index; a case never sees another case's evidence.
