# 0008. The Define gate is a readable report, approved or rejected at a pause

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §33, §33.3; [define.md R5, R6](../requirements/define.md)

## Context

A field checklist does not let a champion judge a Define phase. Requirements R5 and R6 ask for a report and for an explicit approve-or-reject decision.

## Decision

The gate shows a seven-section report assembled in code from confirmed values, with the 5W2H and SIPOC diagrams. The graph pauses at `gate_review` with `interrupt()`. Nothing is written before approval. A rejection names an element and a reason.

## Consequences

The gate can sit paused across restarts, so the checkpointer must persist pending writes. Until R8 (authentication), the Belt is recorded as the approver.
