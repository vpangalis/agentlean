# 0029. Model roles and tiers are owned by one factory

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §21

## Context

Models created ad hoc had drifting temperatures and costs.

## Decision

`get_llm(role)` is the only way to get a model. Roles, their tier and temperature live in `backend/core/llm.py`. Two tiers: intermediate retrieval on the cheaper model, final synthesis on the premium one. Graders run at 0.1. The client's own retry is off.

## Consequences

Cost is set by role, in one file. A new role is an amendment.
