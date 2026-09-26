# 0013. Types, tests and feature landing bind every code commit

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §55.5; review ruling 2 (2026-09-26)

## Context

A `feat(` commit carried two type errors to main because the guard only gated `refactor(arch-v2)` subjects.

## Decision

Any commit that changes code or config, whatever its prefix, passes the type check (rule 3), the tests (rule 4) and feature landing (rule 11). A documentation-only commit is not gated by them.

## Consequences

Proven by a refused `feat(` commit carrying a type error. Prefixes no longer change what is checked.
