---
name: verify-current-version
description: |
  Verify that a proposed architectural pattern, library API, or code approach is current
  against live documentation before finalising any architectural decision. Fetches version
  and changelog information from LangChain, LangGraph, LangSmith, deepagents, Anthropic,
  MCP specification, and Langfuse. Use this skill BEFORE finalising ANY architectural
  decision, BEFORE writing a Claude Code prompt for implementation, and WHENEVER the
  proposed pattern involves LangChain, LangGraph, LangSmith, deepagents, MCP, or Claude
  Code hooks/skills. Reports "confirmed current" or a specific version mismatch with the
  replacement pattern. Fire this skill deliberately — it is a discipline checkpoint, not
  background context.
disable-model-invocation: true
allowed-tools: WebFetch, WebSearch, Read
version: "0.1"
---

# /verify-current-version

## Purpose

You are being invoked to verify that a specific architectural pattern, library API, code
snippet, or design approach is CURRENT against live documentation. The user is about to
make an architectural decision or generate an implementation prompt. Your job is to catch
deprecated patterns before they enter the codebase.

## What to ask the user first

If the user has not already stated what to verify, ask them ONE focused question:

  "What specific pattern, API, or approach should I verify? Paste the exact code
  snippet, function signature, or configuration you plan to use."

Do not proceed until you have concrete text to check. Vague inputs like "check LangGraph"
are not sufficient — you need the actual pattern.

## The source list

Query these sources in this order. If a source fails (timeout, 404, network error),
note it in the report and continue with the others — do not block on a single source.

### Primary (authoritative)

1. **LangGraph GitHub releases** — https://github.com/langchain-ai/langgraph/releases
2. **LangChain GitHub releases** — https://github.com/langchain-ai/langchain/releases
3. **LangChain docs (consolidated)** — https://docs.langchain.com/oss/python/releases/changelog
4. **LangChain docs (canonical URLs)** — https://docs.langchain.com/ for the specific API being verified
5. **deepagents docs and releases** — https://docs.langchain.com/oss/python/deepagents and https://github.com/langchain-ai/deepagents/releases
6. **LangSmith docs** — https://docs.smith.langchain.com
7. **Anthropic Claude Code docs** — https://code.claude.com/docs and https://docs.anthropic.com — for hooks, skills, Claude Code specifics
8. **Anthropic platform docs** — https://platform.claude.com/docs — for Agent Skills spec
9. **MCP specification** — https://spec.modelcontextprotocol.io and https://github.com/modelcontextprotocol/specification/releases

### Secondary (announcement signal)

10. **LangChain blog** — https://blog.langchain.dev
11. **LangChain updates newsletter archive** — https://updates.langchain.com (marketing subdomain; treat as signal, not authority)
12. **Anthropic news** — https://anthropic.com/news
13. **Anthropic engineering blog** — https://anthropic.com/engineering
14. **Langfuse updates** — https://updates.langfuse.com and https://github.com/langfuse/langfuse/releases (relevant only for LangSmith-alternative signalling)

The primary sources are authoritative for "is this pattern current". The secondary sources
surface new patterns and emerging best practices earlier — useful context, not a substitute
for the primary sources.

## The verification procedure

For the pattern the user provided:

1. **Identify the library** — LangGraph, LangChain, LangSmith, deepagents, Anthropic
   (Claude Code), MCP, or Langfuse.

2. **Identify the specific API** — function name, class name, decorator, config field,
   file layout, etc.

3. **Fetch the relevant primary source(s)** — the GitHub releases page and the docs URL
   for that API.

4. **Compare** — is the pattern the current recommended approach, deprecated, superseded,
   or simply obsolete?

5. **If deprecated**, identify the replacement pattern with a link to the source.

6. **Cross-check with EDUCATIONAL.md** — read agent-improve/EDUCATIONAL.md if it exists.
   If a section explicitly documents this pattern (search for the API name), note the
   section number and whether EDUCATIONAL.md's guidance aligns with the live source. If
   they disagree, flag the disagreement — EDUCATIONAL.md may need a correction section.

## The report format

Output a plain-text report with this structure:

  ── VERIFY-CURRENT-VERSION REPORT ──
  Pattern verified: <one-line description>
  Library: <name> | Version currently latest: <version>

  Verdict: [CONFIRMED CURRENT | DEPRECATED | SUPERSEDED | OBSOLETE | UNKNOWN]

  Details:
    <what you found, one paragraph, plain prose>

  Replacement (if applicable):
    <the current pattern, with a link to the authoritative source>

  EDUCATIONAL.md alignment:
    <section number and agreement/disagreement, or "not documented">

  Sources consulted:
    - <URL 1>
    - <URL 2>
    ...
  Sources that failed:
    - <URL X> (reason: <timeout | 404 | network>)

  ── END REPORT ──

If the verdict is anything other than CONFIRMED CURRENT, the user should not proceed with
the pattern as-is. Do not soften this — the whole point of the skill is to catch drift
before it enters the codebase.

## When you cannot verify

If all primary sources for the relevant library fail (network outage, all URLs 404,
etc.), the verdict is UNKNOWN. Do not guess. Do not fall back to your training data.
Explicitly output UNKNOWN and let the user decide whether to proceed at their own risk.
