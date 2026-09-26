# 0038. Nothing is committed to the case before approval

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §33.3, §10

## Context

A partial gate write left the case blob claiming a gate that the Belt never approved.

## Decision

The case blob and the registry are written only after approval, never mid-conversation.

## Consequences

A crash before approval loses nothing the Belt agreed to.
