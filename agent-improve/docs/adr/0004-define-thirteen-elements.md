# 0004. Define coaches thirteen elements, all gate-required

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §39.1, §35; [define.md R4](../requirements/define.md)

## Context

Requirement R4 (2026-09-26) added benefits analysis, critical-to-quality and the 5W2H problem framing to the Define method. The v1.12 list could not hold them.

## Decision

Define coaches thirteen elements in a fixed order. Every gate field is required: there is still no tier split in Define (Option A's principle stands). The field set is owned by `backend/phases/define/schema.py`.

## Consequences

Supersedes the twelve-field list (0006). §35, §39 and §40 still print the old count and must be corrected when ARCHITECTURE.md is edited.
