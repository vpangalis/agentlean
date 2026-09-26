# 0050. Configuration fails fast at start-up

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §53

## Context

A missing credential found at the first Belt turn is a failure in front of a user.

## Decision

Start-up checks every required setting and exits with status 1 when one is missing.

## Consequences

Not built or tested yet (T-list gaps).
