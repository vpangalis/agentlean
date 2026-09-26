# 0041. Two graders: coherence and coaching quality

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §36

## Context

One grader could not judge both whether an answer holds together and whether the coaching followed the method.

## Decision

Coherence (layer 2a) checks the content; the process grader checks the coaching. The grader stands down when coherence has degraded.

## Consequences

Two model calls, two different failure messages.
