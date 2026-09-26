# 0036. Phase knowledge lives in SKILL.md files, disclosed progressively

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §32, §19.2

## Context

Method content in prompts made prompts long and mixed what to teach with how to behave.

## Decision

Each phase has SKILL.md files: what to teach, examples, acceptance criteria. Skills middleware loads only the current element's section.

## Consequences

Domain content leaves ARCHITECTURE.md for the skills. Descriptions must stay small.
