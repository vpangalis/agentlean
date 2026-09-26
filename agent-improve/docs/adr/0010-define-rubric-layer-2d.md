# 0010. The Define rubric is validation layer 2d

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §34; [define.md R7](../requirements/define.md)

## Context

Requirement R7 asks for one pass/fail criterion per element, each with a reason, before the report reaches the Belt.

## Decision

A rubric grader runs as layer 2d of the validation stack. It gives each criterion pass or fail with a reason. Criteria that code can decide are decided in code.

## Consequences

A failing report does not pause; the failing criterion is named. It adds one grader call per gate attempt.
