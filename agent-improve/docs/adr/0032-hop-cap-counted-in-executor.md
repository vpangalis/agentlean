# 0032. Multi-hop retrieval is capped by a count in the executor

**Status:** ACCEPTED (founder and Desktop, 2026-10-22)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §26, §16

## Context

Using `recursion_limit` as the hop budget mixed two units (graph steps and lookups).

## Decision

The executor counts `rag_lookup_*` calls per turn and answers from what it holds at the cap. **The cap is three
lookups per Belt turn** (`nodes_common.COACH_HOP_BUDGET`, the value code and tests pin; it fits R13's 45 s turn). `recursion_limit` (50) is only a backstop; hitting it still gives the Belt a partial answer.

## Consequences

The code's cap and the documents disagreed (tests pinned three; §16, Appendix B and a test name said five). Ruled
2026-10-22: three; the documents that said five are corrected. DEF-237 (G-85) builds on it.
