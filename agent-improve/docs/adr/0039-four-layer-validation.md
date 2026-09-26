# 0039. A four-layer validation stack with one shared cap of three

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §34, §38

## Context

Single-check validation missed incoherent or off-method answers.

## Decision

Layers: schema, coherence, grader, rubric (2d for Define). One attempt counter shared by all layers; the third failure escalates. A coaching turn never runs the validator.

## Consequences

Escalation at three attempts is still a stub (T-list gaps).
