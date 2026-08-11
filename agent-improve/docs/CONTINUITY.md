<!--
Document: agent-improve/docs/CONTINUITY.md
Version: 2.0 — 2026-08-11
Purpose: Comprehensive session-start guide for every new Claude session in
         the AgentLEAN project. Replaces the thin v1 that only tracked code
         migration steps. A new session reading ONLY this file should be
         able to orient fully and continue work without losing a day.

How to use this document:
  - This file lives in the Claude.ai project — it is always available as a
    project doc without being pasted. Read it at the start of any new session.
  - When something changes (decisions ratified, steps completed, stale zones
    resolved), UPDATE this file. Don't let it drift.
  - For architectural decisions, the authoritative records are DECISIONS.md
    and REVIEW_DECISIONS.md. This file points to them; it doesn't duplicate them.
-->

# Agent Improve — Session Continuity Guide
# Version 2.1 — 2026-08-11

---

## 1. What this project is

**AgentLEAN** is a three-agent coaching platform for Lean Six Sigma practitioners:
- **Agent Resolve** — problem-solving agent (production-adjacent, uses Agent Improve learnings)
- **Agent Improve** — DMAIC coaching agent for Black Belts (the agent this document covers)
- **Agent Flow** — flow/process agent (future)

**Agent Improve** coaches a Black Belt (Belt) through five DMAIC phases: Define, Measure,
Analyse, Improve, Control. It is a long-running agentic system built on LangGraph, with a
Planner-Executor pair at two levels, five middleware in a fixed declaration order, four-layer
gate validation, and human-in-the-loop interrupts before each phase gate commits.

**Stack:** LangChain 1.x, LangGraph 1.2.10+, Azure OpenAI, Azure AI Search, AzureBlobCheckpointSaver
(refactor phase) → PostgresSaver/PostgresStore (post-refactor). MCP is architecturally excluded —
never reference it as a runtime component.

---

## 2. The document map — what lives where

Everything is under `agent-improve/`. Two tiers:

### Root (authoritative runtime governance)
- `CLAUDE.md` — **the constitution**. v2.2.14. All rules are here. Rule numbers load-bearing.
- `ARCHITECTURE.md` — **the design reference**. v2.2.15. Implementation patterns, schemas,
  index definitions, middleware ordering.
- `README.md` — minimal repo readme, leave as-is.

### docs/ (reference documents, review records, history)
- `REFACTORING_AGENT_IMPROVE.md` — **the architectural bible**. 87 sections, 11-Part structure.
  Started as EDUCATIONAL.md (Coursera/Edureka coursework). All 85 original sections reviewed,
  corrected, and restructured. This is the primary reference for any architectural decision.
  **Always read relevant sections here before recommending anything.**
- `REVIEW_DECISIONS.md` — **the decision log**. Records every change made during the EDUCATIONAL.md
  review: rationale, web-verification sources, rejected options, open questions. If REFACTORING
  says something is "ratified," this file has the why.
- `DECISIONS.md` — **consolidated decision register**. Synthesizes the major ratified decisions
  into a topically organized reference (state design, middleware, gate fields, coaching, retrieval,
  rejected patterns, pending amendments, code migration status). Written 2026-08-11.
- `EDUCATIONAL.md` — **original chronological learning register**. Preserved as-is. 505KB.
  REFACTORING was derived from it. Do not edit.
- `SKILL_REVIEW_NOTES.md` — **17 coaching review notes** for updating the five DMAIC SKILL.md
  files. Notes 15 (show-first coaching), 16 (A→F session flow), 17 (live gate doc preview) are
  CRITICAL.
- `RESTRUCTURE_PLAN.md` — **historical**. The plan document for reordering EDUCATIONAL.md into
  logical Parts. Has been executed — the 11-Part structure is now in REFACTORING. Keep as record;
  no further action needed.
- `STATE_DESIGN_RESOLUTION.md` — **historical**. Detailed finding-by-finding state design
  analysis (26 findings). Superseded by DECISIONS.md §A. Keep for audit trail.
- `REVIEW_DECISIONS.md` state gap analysis (lines 1–170) is the same material from a prior pass.
- `status-79-84-2026-08-10.md` — **audit record**. Confirms all 6 §79–§84 items landed in
  CLAUDE.md v2.2.14 and ARCHITECTURE.md v2.2.15.
- `*.bak`, `Architecture_drawings_vp.pptx` — backup snapshots and visual diagrams.

---

## 3. The architectural review — what happened and what's pending

### What was done
1. Created EDUCATIONAL.md from Coursera/Edureka courses — chronological learning register.
2. Ran a full 85-section review. Every section assessed against LangChain 1.x, LangGraph 1.2+,
   and Anthropic's current agent engineering posts. Decisions logged in REVIEW_DECISIONS.md.
3. Applied corrections and restructuring → produced REFACTORING_AGENT_IMPROVE.md (87 sections,
   11-Part logical structure).
4. Ground-up rewrote CLAUDE.md (v2.1 → v2.2.14) and ARCHITECTURE.md (v2.1.1 → v2.2.15) to
   align with every ratified decision.
5. Started Agent Improve v2.1 codebase refactor against the new governance docs (Steps 2.1–2.2
   committed; Steps 2.5+ pending).

### What is pending
- **Agent Improve codebase refactor** — Steps 2.5+ (see §5 below). This is the current phase.
- **Two pending ARCHITECTURE.md amendments** (see §6 below).
- **Five SKILL.md files** need updating per SKILL_REVIEW_NOTES.md 17 notes. Currently drafts,
  not wired into `DMAICSkillsMiddleware`. Separate Claude Code task.
- **Eval dataset** — 20–30 examples across all five phases. Scheduled after refactor stabilizes
  (see REVIEW_DECISIONS.md §75).
- **AGENT_DESIGN_GUIDELINES.md** — clean architecture reference with weekly-update skill for
  LangChain/LangGraph drift monitoring. Separate cowork space, post-refactor.
- **`_Artifacts/`** untracked, not in `.gitignore` — deferred housekeeping.

### Why RESTRUCTURE_PLAN.md exists
During the review it was noted that EDUCATIONAL.md's chronological order made it hard to use as
a reference. RESTRUCTURE_PLAN.md captured the plan to reorder into 11 logical Parts. The plan
was executed — REFACTORING_AGENT_IMPROVE.md has the 11-Part structure. RESTRUCTURE_PLAN.md is
now a historical record of that decision.

---

## 4. Session protocol — how to work in this project

### Before any architectural recommendation

1. **Check REFACTORING_AGENT_IMPROVE.md** — find the relevant section(s) and read them.
   The "How to read this document" table at the top tells you where to start by topic.
2. **Check REVIEW_DECISIONS.md** — find the decision entry for that section and read the
   rationale and any open questions.
3. **Check Tier 1 sources** (see §4 below) — verify the pattern is still current against
   LangChain/LangGraph docs and Anthropic's engineering posts.
4. If there is a contradiction between REFACTORING and REVIEW_DECISIONS, REVIEW_DECISIONS wins —
   it is the later record.
5. If there is a contradiction between REVIEW_DECISIONS and CLAUDE.md/ARCHITECTURE.md, note it
   explicitly. The governance docs are what Claude Code implements against; REVIEW_DECISIONS
   captures architectural intent.

### Before any code recommendation

1. Check CLAUDE.md for the rule that governs the area.
2. Check ARCHITECTURE.md for the design pattern.
3. Cross-reference DECISIONS.md for the ratified decision if applicable.
4. Verify the LangChain/LangGraph version and whether the pattern is current (see trusted sources).

### Logging decisions

When a decision is made in a session, update DECISIONS.md and CONTINUITY.md. Do NOT leave the
decision only in the conversation — it will be lost when the context is cleared.

---

## 4. Trusted reference sites (ratified August 2026)

These are the sources to check before any architectural decision. Order matters.

### Tier 1 — Check first (current, authoritative)

| Source | Topic |
|---|---|
| `anthropic.com/engineering/effective-harnesses-for-long-running-agents` (Nov 2025) | Harness concept, context reset, session bridging |
| `anthropic.com/engineering/harness-design-long-running-apps` (Mar 2026) | Planner/Generator/Evaluator — **current Anthropic agent architecture guidance** |
| `anthropic.com/engineering/managed-agents` (Apr 2026) | Brain/hands separation, scaling |
| `anthropic.com/engineering/how-we-contain-claude` (Jul 2026) | Containment, blast radius, security |
| `anthropic.com/engineering/effective-context-engineering-for-ai-agents` (Sep 2025) | Context window management — directly relevant to SummarizationMiddleware |
| `anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills` (Oct 2025) | Agent Skills, SKILL.md spec |
| `anthropic.com/engineering/demystifying-evals-for-ai-agents` (Jan 2026) | Eval design |
| `anthropic.com/engineering/writing-tools-for-agents` (Sep 2025) | Tool design principles |
| `docs.langchain.com`, `reference.langchain.com`, `python.langchain.com` | LangChain/LangGraph official docs |
| `github.com/langchain-ai/*` (repos, issues, releases, changelogs) | Version verification, breaking changes |
| `pypi.org` | Package versions |

### Tier 2 — Official announcements (strategic context)

`langchain.com/blog`, `anthropic.com/news/*`, `resources.anthropic.com`, `claude.com/blog/*`

### Tier 3 — Informed practitioner (cross-checked before citing)

`marsdevs.com/guides`, `deepwiki.com/langchain-ai/*`, `agentpatterns.ai`

### Downgraded — Historical context only

`anthropic.com/engineering/building-effective-agents` (Dec 2024) — the most-cited post in the
industry but 20+ months old. Core advice valid; the Mar 2026 harness-design post supersedes it
for specific architectural guidance.

### Excluded

Stack Overflow, Reddit, Medium, Dev.to — unless linking directly to Tier 1 content.

### Verification discipline

Before any architectural decision: check `anthropic.com/engineering` post index and
`pypi.org/project/langgraph` release history. These move fastest and have the most impact.

---

## 5. Code migration — current state

**Repository:** vpangalis/agentlean — `agent-improve/` subtree.

**HEAD:** `c77584d` — docs: consolidate all architecture documents into docs/.

| Step | Description | Status |
|---|---|---|
| 2.1 | Checkpointer wired into graph.compile() | ✔ committed (`1c3a...`) |
| 2.2 | SupervisorState / PhaseState split (schema only) | ✔ committed (`199e784`) |
| 2.5 | Dependency upgrade: langgraph → 1.2.10, langchain → 1.3.11 | **NEXT** |
| 3.0 | Toolset reconciliation (canonical 7+20, `tool_args.py`) | not started |
| 3.1 | `tool_args.py` Pydantic schemas | **BLOCKED** — canonical toolset must exist in code first |
| 3.3+ | Retrieval tools, middleware stack, gate validation | pending |

**Dependency drift** (current requirements.txt vs target):
- `langgraph` not installed; `langchain` 1.2.13 vs 1.3.11; `langsmith` 0.7.3 vs 0.10.17
- `langgraph.prebuilt` deprecated — any import must migrate to `langchain.agents`
- `InMemorySaver` banned at all stages; `AzureBlobCheckpointSaver` during refactor

**`start.ps1`** runs `git reset --hard origin/main` — always push commits before running it or
they are silently destroyed.

---

## 6. Pending doc amendments

These decisions are ratified but not yet in the governance docs:

| # | Amendment | Target doc | What changes |
|---|---|---|---|
| H1 | Multi-query Option A: per-tool SearchClient instances, RRF | ARCHITECTURE.md §7.4 | Remove "asymmetry is safe" language; document 3-tool pattern |
| H2 | `improve_case_index` vector field: `embedding` → `content_vector` | ARCHITECTURE.md §7.3 | Standardise field name; requires re-index (0 docs, no data loss) |

---

## 7. Open items

- **Step 3.1 blocked** — toolset reconciliation Delta 1c/1d/D3.5: canonical 7 universal tools
  don't exist in code yet. `tool_args.py` cannot be written until the toolset is confirmed
  in `knowledge/tools.py`.
- **`improve_case_index` re-index** — must happen before Step 3.3 (`rag_lookup_case_history`
  references `content_vector`). Delete + recreate the index; re-ingest. 0 documents, no data loss.
- **Five SKILL.md files** — drafts exist in `skills/dmaic-{phase}-phase/SKILL.md`. Not wired
  into `DMAICSkillsMiddleware`. Need updating per SKILL_REVIEW_NOTES.md Notes 1–17 (Notes 15,
  16, 17 are CRITICAL). Separate Claude Code task.
- **Eval dataset** — joint exercise, scheduled after refactor stabilizes.

---

## 8. Stale zones — do NOT ground architectural reasoning in these

- **ARCHITECTURE.md §7.4** — "embedding/content_vector asymmetry is safe by construction."
  Reversed by H2 above. Do not cite this claim.
- **`upload/agent.py:107`** — parses raw `response.content` directly. §4.5 violation (must use
  `response.content_blocks`). No §15 step covers this file. Tracked but not yet scheduled.
- **`core/llm.py`** — class definition violates §2 (classes only in designated files). Role map
  diverges (D3.2). Expected end-of-Step-2 state; schedule correction in Step 3.x planning.
- **REFACTORING §10** — shows `completeness_score: float` on illustrative DefineState/MeasureState
  sketches. Wrong per ratified design (all fields `str`, no stored score). Flagged; correct
  during or after batch commit of any remaining §10 changes.
- **REVIEW_DECISIONS.md lines 444–508 (§17 draft)** — shows a SupervisorState with 9 fields
  including `project_context`, `dmaic_plan`, `key_decisions`, `open_items`. This is a PRE-
  RATIFICATION draft. The ratified 7-field SupervisorState is in DECISIONS.md §A1 and
  CLAUDE.md §10.1. Do not implement the 9-field version.
- **Any reference to `gate_documents` store namespace** — retired; use `artifacts`.
- **Any reference to `project_id`** — retired; use `case_id`.
- **`_Artifacts/audit-2026-07-03.md`** — lives at repo root, untracked, referenced in the old
  CONTINUITY.md. If it exists it is a historical audit. `_Artifacts/` itself is untracked; deferred.
- **REFACTORING §33 canonical implementation** — two bugs not yet fixed in the document. (1) Filter
  uses `phase_relevance eq 'all'`; correct value is `'general'` (218 docs carry `'general'`, zero
  carry `'all'`). (2) Uses `azure_search_retriever.invoke(q, search_kwargs={"filters": ...})`
  which doesn't work — `AzureAISearchRetriever` requires `filters=` in the constructor. The retriever
  cannot be module-level for `rag_lookup_methodology`; it must be instantiated per call with the
  dynamic `phase` filter. Both bugs are recorded in DECISIONS.md §E3 and §E4 and in
  REVIEW_DECISIONS.md §33 compliance audit. Fix before Step 3.1.
- **REVIEW_DECISIONS.md §32/§37 filter clauses** — same `'all'` placeholder appears in the §37
  discussion (line ~1323). Carry the same fix when amending REFACTORING §33.

---

## 9. Key architectural decisions (summary — see DECISIONS.md for full detail)

**State:**
- SupervisorState: 7 fields. PhaseState: 15 content fields + 3 plumbing.
- All captured fields are `str`. Three cross-phase reference dicts are `dict` (causal_hypothesis,
  solution_linked_to_root_cause, post_improvement_metric).
- `gate_apply_node` writes BOTH store and `PhaseState.final` — dual write is required.

**Middleware (declaration order = execution order):**
1. `BeforeModelStateInjection` (before_model, MUST be first)
2. `DMAICSkillsMiddleware` (before_agent)
3. `SummarizationMiddleware` (before_model)
4. `ModelRetryMiddleware(retries=2)` (wrap_model_call)
5. `DMAICGraderMiddleware` (after_agent)

**Two graders, not one:**
- `DMAICGraderMiddleware` → `COACHING_QUALITY_RUBRIC` → every coaching turn → middleware
- Validation stack Layer 2d → `PHASE_RUBRIC` → gate boundary only → `validation_stack` node

**Tools:**
- 7 universal tools (record_field RETIRED — field capture via CoachingResponse structured output)
- Phase-specific computation tools: 1 (Define), 8 (Measure), 5 (Analyse), 1 (Improve), 5 (Control)
- `create_react_agent`, `langgraph.prebuilt` — BANNED
- `HumanInTheLoopMiddleware` — REJECTED (confirmed bugs: edit/reject broken in subgraph contexts)
- MCP — ARCHITECTURALLY EXCLUDED (permanent)

**Retrieval:**
- Three tools: `rag_lookup_methodology`, `rag_lookup_evidence`, `rag_lookup_case_history`
- Multi-query + RRF (k=60) inside each tool, per-tool SearchClient instances (Option A)
- `MultiQueryRetriever`, `EnsembleRetriever` — BANNED (moved to langchain-classic)

**Checkpointer:**
- `AzureBlobCheckpointSaver` during refactor
- `PostgresSaver` + `PostgresStore` post-refactor, pre-production
- `InMemorySaver` — BANNED at all stages, including development

**thread_id:**
- One `thread_id` per project (`case_id` value)
- Checkpointer on parent graph ONLY; subgraphs compiled without checkpointer
- LangGraph auto-manages `checkpoint_ns` per subgraph

---

## 10. Version log

| Date | Change |
|---|---|
| 2026-08-11 | v2.1 — §33 compliance audit: two bugs found (phase_relevance `'all'` → `'general'`; search_kwargs → constructor filter). DECISIONS.md §E4 added. Stale zone §8 extended. |
| 2026-08-11 | v2.0 — comprehensive rewrite; added document map, review history, trusted sources, session protocol, full stale zones, architectural summary |
| 2026-08-10 | v1.x — §3 updated: §79–§84 RESOLVED (all 6 items landed in CLAUDE.md v2.2.14) |
| 2026-08-10 | v1.x — updated CONTINUITY.md §3 for multi-query Option A and content_vector ratifications |
| 2026-08-05 | v1.x — seven-step coaching, show-first principle, process map Tier 1 promotions landed (CLAUDE.md v2.2.12–14) |
| 2026-08-03/05 | v1.x — 26 state design findings locked (CLAUDE.md v2.2.9–12) |
