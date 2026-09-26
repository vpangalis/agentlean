# 0031. Multi-query retrieval fused by Reciprocal Rank Fusion

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §25

## Context

Single queries missed relevant passages phrased differently.

## Decision

Each lookup runs the original query plus three to five variants and fuses the lists with RRF, constant 60.

## Consequences

Better recall at the cost of more search calls per lookup.
