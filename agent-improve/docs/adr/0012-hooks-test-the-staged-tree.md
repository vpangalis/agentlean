# 0012. Commit hooks test what is staged, not the working tree

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §55.5; founder rulings on the 6.67 report (2026-09-26)

## Context

Hooks that ran on the working tree passed commits whose staged content differed from what was tested.

## Decision

The pre-commit hook and the guard check out the staged tree into a temporary directory and run the suite and the type check there. The pre-flight has no acknowledge override; it compares against the failures recorded at the last commit.

## Consequences

A commit is proven as committed. Each commit costs one full suite run.
