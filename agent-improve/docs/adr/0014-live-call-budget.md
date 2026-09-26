# 0014. Live model calls are budgeted per prompt

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §52; review ruling 5 (2026-09-26)

## Context

Proof runs against the live model cost money and time, and diagnosis runs were once spent outside a stated cap.

## Decision

At most 150 live model calls per prompt, diagnosis included, unless the prompt says otherwise. Ask before exceeding.

## Consequences

Run scripts count calls and report the total. A full Define run-through fits in one prompt's budget.
