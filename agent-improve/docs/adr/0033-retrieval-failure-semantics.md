# 0033. Retrieval failures are errors, not empty results

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §27, §48

## Context

An outage that returned an empty list looked like 'nothing found', and the coach answered without grounding.

## Decision

A client error raises a permanent error; a connection failure is transient; only a genuine no-match returns an empty list.

## Consequences

The circuit breaker and fallback can tell outages from misses.
