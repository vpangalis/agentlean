# 0032. Multi-hop retrieval is capped by a count in the executor

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §26, §16

## Context

Using `recursion_limit` as the hop budget mixed two units (graph steps and lookups).

## Decision

The executor counts `rag_lookup_*` calls per turn and answers from what it holds at the cap. `recursion_limit` (50) is only a backstop; hitting it still gives the Belt a partial answer.

## Consequences

The code's cap and the documents disagree (drift): tests pin three, §16 and Appendix B say five, a test name says five. A founder ruling must pick one.
