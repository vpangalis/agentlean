# 0034. No MCP: tools are in-process, with a small universal set

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §29.1–§29.4

## Context

An MCP server added a process boundary and a protocol for tools only this app calls.

## Decision

Tools are in-process Python. A small set of universal tools is bound in every phase; `record_field` is retired and may not return. Cross-agent tools exist but are not bound.

## Consequences

§29.2 says eight universal tools, §4 and the tests say seven: the section needs a ruling and a correction.
