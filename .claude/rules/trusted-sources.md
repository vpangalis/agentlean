---
paths:
  - "agent-improve/ARCHITECTURE.md"
  - "agent-improve/docs/adr/**"
  - "agent-improve/docs/requirements/**"
---
# Trusted sources

> Moved from ARCHITECTURE.md v1.88 Appendix C on 2026-09-27 (brief Part C3). The § numbers below refer
> to that archived version (`agent-improve/docs/_archive/ARCHITECTURE_v1.88_2026-09-27.md`).


*Supersedes: REFACTORING §45.*

**Ordered. Check Tier 1 before any architectural decision.**

### Tier 1 — current, authoritative

| Source | Date | Topic |
|---|---|---|
| `anthropic.com/engineering/effective-harnesses-for-long-running-agents` | Nov 2025 | Harness concept, context reset, session bridging |
| `anthropic.com/engineering/harness-design-long-running-apps` | Mar 2026 | Planner/Generator/Evaluator. **A specific research write-up on long-running coding harnesses** — strong evidence from an adjacent domain, not a specification |
| `anthropic.com/engineering/managed-agents` | Apr 2026 | Brain/hands separation, scaling |
| `anthropic.com/engineering/how-we-contain-claude` | Jul 2026 | Containment, blast radius |
| `anthropic.com/engineering/effective-context-engineering-for-ai-agents` | Sep 2025 | Context-window management — §19.3 |
| `anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills` | Oct 2025 | SKILL.md spec — §32 |
| `anthropic.com/engineering/demystifying-evals-for-ai-agents` | Jan 2026 | Eval design — §52 |
| `anthropic.com/engineering/writing-tools-for-agents` | Sep 2025 | Tool design — §29, §30 |
| `anthropic.com/engineering/designing-ai-resistant-technical-evaluations` | Jan 21, 2026 | Eval design that resists gaming — **added 2026-08-21**, bears on §52 |
| `anthropic.com/engineering/quantifying-infrastructure-noise-in-agentic-coding-evals` | Feb 05, 2026 | Separating real regressions from infrastructure noise — **added 2026-08-21**, bears on §52's >10% threshold |
| `anthropic.com/engineering/advanced-tool-use` | Nov 24, 2025 | Advanced tool use on the Claude Developer Platform — **added 2026-08-21**, bears on §29, §30, §31 |
| `docs.langchain.com`, `reference.langchain.com` | Ongoing | LangChain / LangGraph API surface |
| `github.com/langchain-ai/*` | Ongoing | Versions, breaking changes, open issues |
| `langchain-ai.github.io/langmem` | Ongoing | Memory taxonomy — §28 |
| `pypi.org` | Ongoing | Package versions |

### Tier 1 — compliance

*Added 2026-08-23 with Part XIII.*

| Source | Topic |
|---|---|
| `https://artificialintelligenceact.eu/implementation-timeline/` | EU AI Act implementation timeline — the deadlines in §67.1 |
| `https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai` | EU AI Act, European Commission — the regulatory framework |
| `https://ai-act-service-desk.ec.europa.eu` | EU AI Act Service Desk — guidance and classification questions |
| EUR-Lex, Regulation (EU) 2022/2554 | DORA regulation text — the register structure of §68 |
| GitHub Spec Kit; AWS Kiro (`kiro.dev/docs/specs`) | Spec-Driven Development method references — the basis for Part XII's structure |

> **Compliance-source discipline.** The EU AI Act and DORA are in **active
> implementation with shifting guidance**. Any compliance claim must cite a
> current-dated source; **if availability cannot be verified, mark it
> "unverified — requires legal validation" rather than asserting it.** Nothing
> in Part XIII is legal advice, and the classification question of §67.2 needs
> qualified counsel.

### Tier 2 — official announcements

`langchain.com/blog` · `anthropic.com/news/*` · `claude.com/blog/*`

### Tier 3 — informed practitioner, cross-check before citing

`marsdevs.com/guides` · `deepwiki.com/langchain-ai/*` · `agentpatterns.ai`

### Downgraded — historical

`anthropic.com/engineering/building-effective-agents` (Dec 2024). **Still
sound** — its core advice, *"find the simplest solution possible,"* is the
principle behind §18's custom-middleware decision. Ordered lower because newer
specific material exists, **not because it was refuted.**

### Excluded

Stack Overflow, Reddit, Medium, Dev.to — unless linking directly to Tier 1.

### Added 2026-09-27 (brief Part C3)

| Source | Topic |
|---|---|
| Kiro specs — `kiro.dev/docs/specs` | Spec-driven development: requirements, design, tasks (also listed above, under compliance) |
| arc42 — `arc42.org` | Architecture documentation template: the section set of ARCHITECTURE.md |
| C4 model — `c4model.com` | Context, container and component diagrams (ARCHITECTURE.md §2) |
| OWASP GenAI LLM Top 10 — `genai.owasp.org/llm-top-10` | Prompt injection, insecure output handling, excessive agency (T71–T74) |
| Microsoft HAX guidelines — `microsoft.com/en-us/haxtoolkit` | Human-AI interaction guidelines behind W8–W14 |
| Azure AI Content Safety Prompt Shields — `learn.microsoft.com/azure/ai-services/content-safety/concepts/jailbreak-detection` | User-prompt and document attack detection (T71, T72, ADR-0057 input) |
| EU AI Act Articles 12 and 50 — `artificialintelligenceact.eu/article/12/`, `artificialintelligenceact.eu/article/50/` | Record-keeping (the decision trail, R19, T84) and transparency (W8) |
