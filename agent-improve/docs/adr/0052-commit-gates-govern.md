# 0052. The commit gates govern; rule files are advisory

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §55.5

## Context

Rules written only in prose were ignored under pressure.

## Decision

What must hold is enforced at commit by the guard and hooks. Rule files explain; they do not enforce.

## Consequences

A rule that matters needs a check.
