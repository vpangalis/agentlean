# 0035. Computation tools are pure, bound per phase, under a ceiling

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §30, §31, §69

## Context

Too many tools degrade tool choice; statistics done by the model are unreliable.

## Decision

Statistics are pure functions that never raise and return strings. Each phase binds its own subset; no phase exceeds sixteen tools. One tool is the single authority for each metric.

## Consequences

The model chooses among few tools. A tool precondition (e.g. stability before capability) is still untested (T-list gaps).
