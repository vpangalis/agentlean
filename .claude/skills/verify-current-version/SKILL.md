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
disable-model-invocation: false
allowed-tools: WebFetch, WebSearch, Read, Grep
version: "0.2"
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

**These are the ratified trusted-source tiers (August 2026).** The same tiers are recorded
in REFACTORING_AGENT_IMPROVE.md §45 and REVIEW_DECISIONS.md. One list, used by both this
skill and the human monitoring habit, so the two cannot diverge. **If you change this list,
change it in all three places in the same commit.**

Query the sources relevant to the pattern being verified. If a source fails (timeout, 404,
network error), note it in the report and continue with the others — do not block on a
single source.

**Start here for anything version-related.** These two move fastest and have the most
impact on our design:

- **PyPI JSON API** — `https://pypi.org/pypi/<package>/json` — the definitive answer to
  "what is the latest version". Read `info.version`.
- **Anthropic engineering post index** — https://anthropic.com/engineering — the fastest-
  moving source of architectural guidance.

### Tier 1 — Primary (current, authoritative)

**Library, API, and version sources**

1. **PyPI** — https://pypi.org — definitive package version and dependency data. Prefer the
   JSON API (above) over the HTML page.
2. **LangGraph GitHub releases** — https://github.com/langchain-ai/langgraph/releases
3. **LangChain GitHub releases** — https://github.com/langchain-ai/langchain/releases
4. **LangChain docs (consolidated changelog)** — https://docs.langchain.com/oss/python/releases/changelog
5. **LangChain docs (canonical URLs)** — https://docs.langchain.com/ for the specific API being verified
6. **deepagents docs and releases** — https://docs.langchain.com/oss/python/deepagents and https://github.com/langchain-ai/deepagents/releases
7. **LangSmith docs** — https://docs.smith.langchain.com
8. **Anthropic Claude Code docs** — https://code.claude.com/docs and https://docs.anthropic.com — for hooks, skills, Claude Code specifics
9. **Anthropic platform docs** — https://platform.claude.com/docs — for the Agent Skills spec
10. **MCP specification** — https://spec.modelcontextprotocol.io and https://github.com/modelcontextprotocol/specification/releases *(knowledge-only for AgentLean — MCP is architecturally excluded per §39; verify only if the question is about the protocol itself)*

**Architectural guidance sources** — check these when the question is about agent
*architecture* rather than a specific API signature:

| Source | Date | Topic | Bears on |
|---|---|---|---|
| `anthropic.com/engineering/harness-design-long-running-apps` | Mar 2026 | Planner/Generator/Evaluator, ablation discipline | **Current Anthropic agent architecture guidance.** Maps to our Planner/Executor/Grader — §44 |
| `anthropic.com/engineering/effective-harnesses-for-long-running-agents` | Nov 2025 | Harness concept, context reset, session bridging | "Harness + model" framing — Terminology Reference |
| `anthropic.com/engineering/managed-agents` | Apr 2026 | Brain/hands separation, scaling | Planner-Executor cascade — §5, §11 |
| `anthropic.com/engineering/how-we-contain-claude` | Jul 2026 | Containment, blast radius, security boundaries | Hook security — §45, §86 |
| `anthropic.com/engineering/effective-context-engineering-for-ai-agents` | Sep 2025 | Context-window management | `SummarizationMiddleware` §36, skill disclosure §84 |
| `anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills` | Oct 2025 | Agent Skills, SKILL.md spec | §83, §84 |
| `anthropic.com/engineering/demystifying-evals-for-ai-agents` | Jan 2026 | Eval design for agents | §75 evaluation dataset |
| `anthropic.com/engineering/writing-tools-for-agents` | Sep 2025 | Tool design principles | 18 computation + 3 retrieval tools — §39 |

### Tier 2 — Official publications (announcement signal, strategic context)

- **LangChain blog** — https://langchain.com/blog (legacy alias: https://blog.langchain.dev)
- **Anthropic news** — https://anthropic.com/news
- **Anthropic research and whitepapers** — https://resources.anthropic.com
- **Claude product blog** — https://claude.com/blog

### Tier 3 — Informed practitioner (cross-checked, always cited)

- https://marsdevs.com/guides — practitioner guides carrying Tier 1 citations
- https://deepwiki.com/langchain-ai/* — community wiki with source references
- https://agentpatterns.ai — pattern vocabulary crosswalk across frameworks

### Downgraded — historical context, no longer primary

- `anthropic.com/engineering/building-effective-agents` (Dec 2024) — **historical
  foundation.** Its core advice ("find the simplest solution possible") still holds, but
  the harness concept, the Planner/Generator/Evaluator pattern, context-reset discipline,
  and the ablation approach from the 2025–2026 posts supersede it for architectural
  guidance. **Do not cite it as current architecture guidance.**

### Excluded

Stack Overflow, Reddit, Medium, Dev.to — unverified unless linking directly to Tier 1
content.

### Operational extras (outside the tiers, useful for specific questions)

- https://updates.langchain.com — newsletter archive; marketing subdomain, signal not authority
- https://updates.langfuse.com and https://github.com/langfuse/langfuse/releases — only for LangSmith-alternative signalling (§73)

Tier 1 is authoritative for "is this pattern current". Tier 2 surfaces new patterns earlier
— useful context, never a substitute for Tier 1. Tier 3 must always be cross-checked
against Tier 1 before it informs a decision.

### Two practical notes, learned the hard way

- **The consolidated changelog does not carry patch-level entries.**
  `docs.langchain.com/oss/python/releases/changelog` stops at minor versions (e.g. 1.2.0).
  For a question like "what changed between 1.2.7 and 1.2.10", it will return nothing
  useful. Go to the GitHub releases instead.
- **For verbatim release bodies, use the GitHub API, not the HTML page.**
  `https://api.github.com/repos/langchain-ai/langgraph/releases?per_page=10` returns
  `tag_name`, `published_at`, and the full `body` for each release. The rendered HTML page
  summarises and can misreport dates.

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

6. **Cross-check with REFACTORING_AGENT_IMPROVE.md** — read
   `agent-improve/docs/REFACTORING_AGENT_IMPROVE.md`. This is the live rationale document; if a
   section documents this pattern (search for the API name, and use the Document Navigation
   index at the top — sections are ordered by topic, not by number), note the section number
   and whether its guidance aligns with the live source. If they disagree, flag it — the
   section needs a correction.

   Then check whether a **rule** depends on it: `agent-improve/CLAUDE.md` is binding and
   `agent-improve/ARCHITECTURE.md` carries the design. A drift that reaches a rule is more
   serious than one confined to the rationale, and correcting it is a §18 amendment commit.

   **Do not cross-check EDUCATIONAL.md.** It is the frozen historical training register
   (its own header says so) and is deliberately not maintained. It will report stale
   versions by design, and treating agreement with it as a signal is a false positive.

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

  Governance alignment:
    REFACTORING_AGENT_IMPROVE.md: <section number and agreement/disagreement, or "not documented">
    Rule affected: <CLAUDE.md / ARCHITECTURE.md section, or "none — rationale only">

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
