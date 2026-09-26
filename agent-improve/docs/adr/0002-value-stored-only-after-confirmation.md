# 0002. A value is stored only after the Belt confirms it

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §20 (v1.75), §58 S-C04 B7

## Context

The executor used to store whatever the model extracted, so a coach paraphrase could become the case record without the Belt ever agreeing to it.

## Decision

What a turn extracts is held as pending. It is stored only when the Belt confirms the read-back, in the Belt's own words or in a tidied version the Belt confirmed.

## Consequences

The case record contains nothing the Belt did not agree to. Every stored value costs one extra confirmation turn. The Define report reads confirmed values only.
