# 0027. A fixed middleware stack around the coach

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §19

## Context

Cross-cutting concerns (state injection, skills, summarisation, retry, coherence, grading) were scattered through node code.

## Decision

A fixed, ordered middleware stack: state injection, skills, summarisation, model retry, tool retry, contradiction detection, coherence, grader. Each retry cap is separate.

## Consequences

Order is part of the design and is tested. Two middlewares (coherence, grader) are also validation layers.
