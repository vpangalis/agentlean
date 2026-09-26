# 0007. The answer check is the planner's judgment, naming the failed criterion

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §17 B5 (v1.77); [define.md R3](../requirements/define.md)

## Context

Requirement R3 asks that every Belt answer be checked against the element's acceptance criteria, and that a challenge say what is missing.

## Decision

When the focus field is answered and the reply is not a plain yes, the planner-role model returns one sufficiency judgment that names the failed criterion. In every other case no model is called. The challenge quotes that criterion.

## Consequences

One model call per substantive answer, none on a confirmation. The criteria live in each SKILL.md, so they have one owner.
