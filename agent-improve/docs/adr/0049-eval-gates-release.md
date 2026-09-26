# 0049. The evaluation suite gates a release

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §52

## Context

Prompt and model changes regress silently.

## Decision

A jointly authored suite of 20–30 examples runs on every commit touching prompts, graph or model config; a drop of more than 10% in any metric blocks release.

## Consequences

The suite is not built yet (T-list gaps).
