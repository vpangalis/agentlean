# 0044. A four-level fallback chain and three-state circuit breakers

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §46

## Context

A model or search outage must never become a hard failure for the Belt.

## Decision

Timeout, premium model, smaller model, cache, then degraded mode that names the phase and the saved progress. Two three-state breakers (model, search). A token-limit error is not retried on a smaller model.

## Consequences

None of this is built or tested yet (T-list gaps).
