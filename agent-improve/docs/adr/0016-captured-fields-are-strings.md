# 0016. Every captured field is a string

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §7, §41

## Context

Typed numbers captured from conversation broke when a Belt wrote '≈ 12%' or 'about two weeks'.

## Decision

Captured values are stored as the Belt's words (strings, or dicts and lists of strings where the schema says so). Computation results are strings too; tools parse at use.

## Consequences

No capture fails on a unit or a word. Every consumer must parse, and parsing happens in the tool, never in the schema.
