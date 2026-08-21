<!--
Document: agent-improve/docs/CONTINUITY.md
Version: 2.8 — 2026-08-19
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
# Version 2.8 — 2026-08-19

---

## 1. What this project is

**AgentLEAN** is a three-agent coaching platform for Lean Six Sigma practitioners:
- **Agent Resolve** — problem-solving agent (production-adjacent, uses Agent Improve learnings)
- **Agent Improve** — DMAIC coaching agent for Black Belts (the agent this document covers)
- **Agent Flow** — flow/process agent (future)

**Agent Improve** coaches a Black Belt (Belt) through five DMAIC phases: Define, Measure,
Analyse, Improve, Control. It is a long-running agentic system built on LangGraph, with a
Planner-Executor pair at two levels, eight middleware in a fixed declaration order, four-layer
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
- `DECISIONS.md` — **consolidated decision register** (v1.4 — 2026-08-19). Synthesizes the major
  ratified decisions into a topically organized reference (state design, middleware, gate fields,
  coaching, retrieval, rejected patterns, pending amendments, code migration status, memory
  architecture). Includes Part K: Memory Architecture (§37 taxonomy + §37-D Procedural ratification)
  and Part M: Middleware amendments (Mod A: ContradictionDetectionMiddleware / M2,
  Mod B: CoherenceMiddleware / M3, D69-x closure / M1).
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
6. Compliance audits run for §33, §34, §37, §71 — four finding sets each producing REVIEW_DECISIONS.md
   entries and DECISIONS.md updates. §37 audit (2026-08-11) added four findings, ratified §37-D
   (Procedural Memory taxonomy), and added DECISIONS.md Part K.
7. Mod A (ContradictionDetectionMiddleware) and Mod B (CoherenceMiddleware) ratified (2026-08-12).
   Seven-middleware stack confirmed. DECISIONS.md v1.3 written (Part M). REVIEW_DECISIONS.md
   amended. D69-x decisions confirmed closed.
8. B3.1 amendment (2026-08-12): ToolRetryMiddleware added at position 5 (wrap_tool_call hook).
   Stack is now eight middlewares. M4 registered: §29 naming error (RetryMiddleware →
   ToolRetryMiddleware). REVIEW_DECISIONS.md updated.
9. §22 Debate Agents deferral confirmed (2026-08-19): NOT implemented in v2.1. Decision: test the
   Analyse node in production first; then decide whether adversarial debate is needed. Deferred to
   §87 backlog. REVIEW_DECISIONS.md §22 status updated from "preliminary scoping, full review
   pending" to "Ratified — deferred to §87 backlog, confirmed 2026-08-19."
10. §67 DORA geographic redundancy identified (2026-08-19): v2.1 four-level fallback chain is
    single-region (Frankfurt) — non-compliant with DORA ICT resilience requirements. Ratified
    v2.2 five-level geographically redundant chain (primary Frankfurt + secondary EU region,
    Sweden Central candidate). Deferred to §87 backlog item 14; required before any regulated-
    entity production launch. v2.1 chain unchanged.

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
- **Batch commit to REFACTORING §33/§37** — fix §37-A (`'all'` → `'general'`), §37-B (per-call
  constructor), §37-C (EnsembleRetriever prose) in one commit. See §8 stale zones.
- **Batch commit to REFACTORING §29** — replace `RetryMiddleware` with `ToolRetryMiddleware`
  throughout; update §29 "Where each concern lives" table to note invisible retry is handled by
  `ToolRetryMiddleware` (M4).

### Why RESTRUCTURE_PLAN.md exists
During the review it was noted that EDUCATIONAL.md's chronological order made it hard to use as
a reference. RESTRUCTURE_PLAN.md captured the plan to reorder into 11 logical Parts. The plan
was executed — REFACTORING_AGENT_IMPROVE.md has the 11-Part structure. RESTRUCTURE_PLAN.md is
now a historical record of that decision.

---

## 4. Session protocol — how to work in this project

### Hard rule — read before you speak

**Claude must not answer any architectural, design, or implementation question in this project
before completing all three of the following steps:**

1. Read the relevant section(s) of REFACTORING_AGENT_IMPROVE.md (or confirm via project_search
   that no relevant section exists).
2. Read the corresponding REVIEW_DECISIONS.md entry (or confirm none exists).
3. For patterns involving LangChain, LangGraph, LangSmith, or Anthropic guidance: check at least
   one Tier 1 trusted source (§4 below) to confirm the pattern is current.

This rule is non-negotiable. Answering from training-data recall alone, or from memory of a
prior session without re-reading the documents, is not permitted. If the relevant documents
have not yet been read in this session, the correct response is: "Let me check the documents
before answering." The user must be able to rely on every answer being grounded in the ratified
record, not in what Claude thinks it remembers.

This rule exists because verification failures have caused real rework — for example: incorrectly
stating DMAICGraderMiddleware fires only at gate boundaries (it fires every turn); using the wrong
class name RetryMiddleware instead of ToolRetryMiddleware in §29. The documents exist precisely
to prevent these errors.

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
| `langchain-ai.github.io/langmem` | LangMem — memory taxonomy (Tier 1 for memory architecture questions) |
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

**Dependency drift** — measured in the venv 2026-08-21, not read off requirements.txt:

| Package | Installed | Doc target | Note |
|---|---|---|---|
| `langgraph` | **1.1.10** | 1.2.10 | **Below the ≥1.2.6 floor.** Blocks everything below |
| `langchain` | 1.2.13 | 1.3.11 | |
| `langchain-core` | 1.3.3 | — | let pip resolve |
| `langchain-openai` | 1.1.11 | — | let pip resolve |
| `langchain-community` | 0.4.1 | — | supplies `AzureSearch` |
| `langsmith` | 0.7.3 | — | |
| `langchain-classic` | 1.0.3 | 1.0.3 | ✔ matches the pin |

**`langgraph` 1.1.10 is a hard blocker, not drift.** `TimeoutPolicy`,
`error_handler=` and `RunControl.request_drain()` all require **≥1.2.6**, as does
the subgraph `checkpoint_ns` fix. Nothing in §3.6 (reliability) or §1.2
(hierarchical subgraphs) can be built until `pip install --upgrade` runs. This is
Step 2.5 and it gates more than the table above suggests.

**Do NOT upgrade to the documented 1.2.10 / 1.3.11 pins — they are already stale.**
Current releases are near 1.2.11 / 1.3.15. **Resolve the correct target during
Task 3B** against live PyPI and the LangChain changelog, then pin, then upgrade.
Upgrading to a stale pin means doing the migration twice.

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
| G1 | §67 geographic redundancy amendment | REVIEW_DECISIONS.md | Add §67 amendment section documenting DORA non-compliance of v2.1 single-region chain; ratify v2.2 five-level chain; record §87 backlog item 14 |
| G2 | §22 deferral status update | REVIEW_DECISIONS.md | Change §22 entry from "preliminary scoping, full review pending" to "Ratified — deferred to §87 backlog, confirmed 2026-08-19" |

---

## 7. Open items

- **REVIEW_DECISIONS.md not yet updated for §67/§22** — G1 and G2 amendments (see §6) are ratified but not yet written into the project doc. Content for §67 amendment is in `/home/claude/decisions_v14_additions.md` (N1 entry). Content for §22 update is in the same file (N2 entry). Until REVIEW_DECISIONS.md is updated, the project doc's §22 entry is stale (shows preliminary scoping) and the §67 geographic redundancy section is absent.
- **Step 3.1 blocked** — toolset reconciliation Delta 1c/1d/D3.5: canonical 7 universal tools
  don't exist in code yet. `tool_args.py` cannot be written until the toolset is confirmed
  in `knowledge/tools.py`.
- **`improve_case_index` re-index** — must happen before Step 3.3 (`rag_lookup_case_history`
  references `content_vector`). Delete + recreate the index; re-ingest. 0 documents, no data loss.
- **Five SKILL.md files** — drafts exist in `skills/dmaic-{phase}-phase/SKILL.md`. Not wired
  into `DMAICSkillsMiddleware`. Need updating per SKILL_REVIEW_NOTES.md Notes 1–17 (Notes 15,
  16, 17 are CRITICAL). Separate Claude Code task.
- **Eval dataset** — joint exercise, scheduled after refactor stabilizes.
- **Batch commit to REFACTORING §33/§37** — apply §37-A (`'all'` → `'general'`) and §37-B
  (per-call constructor) fixes, correct §37-C (EnsembleRetriever prose). Same fixes as §33;
  do in one commit. Not yet scheduled — must happen before Step 3.1.
- **Batch commit to REFACTORING §29** — replace `RetryMiddleware` with `ToolRetryMiddleware`
  throughout; update §29 "Where each concern lives" table (M4). Same commit window as §33/§37.
- **Test: planned multi-hop scope** — planned multi-hop (for-loop, hop_results, synthesis LLM call)
  is currently only implemented in `analyse_executor_node`. Other phases use standard ReAct. The
  assumption that reactive tool calling is sufficient for non-Analyse turns is unverified. Validate
  during eval dataset phase (§75): if non-Analyse turns show 3+ sequential tool calls with lower
  coaching quality than Analyse multi-hop turns, extend the planned multi-hop + synthesis mechanism
  to those phases. See DECISIONS.md §F7.

---

## 8. Stale zones — do NOT ground architectural reasoning in these

- **ARCHITECTURE.md §7.4** — "embedding/content_vector asymmetry is safe by construction."
  Reversed by H2 above. Do not cite this claim.
- **`response.content` parsed directly — TWO sites, not one.** Both are §4.5 violations
  (must read `response.content_blocks`):
  - `upload/agent.py:107` — `result.content.strip()`. No §15 step covers this file.
  - `gateway/routes.py:67` — `response.content.strip()`. Found by the Task 2 sweep
    (2026-08-21); previously unrecorded. Covered by §15 Step 9 (Routes), but only
    incidentally — the step is about removing manual dispatch, not this parse.

  Neither is scheduled as its own step. Fixing `routes.py:67` alongside Step 9 is
  cheap; `upload/agent.py` still needs a home.
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
- **REVIEW_DECISIONS.md §22 entry** — shows "preliminary scoping, full review pending." Correct status is "Ratified — deferred to §87 backlog, confirmed 2026-08-19; §22 is NOT implemented in v2.1; test Analyse node in production first; adversarial debate pattern scoped to Analyse phase only." Do not act on the §22 entry as written — it is stale pending the G2 doc amendment.
- **`_Artifacts/audit-2026-07-03.md`** — lives at repo root, untracked, referenced in the old
  CONTINUITY.md. If it exists it is a historical audit. `_Artifacts/` itself is untracked; deferred.
- **REFACTORING §33 canonical implementation** — two bugs not yet fixed in the document. (1) Filter
  uses `phase_relevance eq 'all'`; correct value is `'general'` (218 docs carry `'general'`, zero
  carry `'all'`). (2) Uses `azure_search_retriever.invoke(q, search_kwargs={"filters": ...})`
  which doesn't work — `AzureAISearchRetriever` requires `filters=` in the constructor. The retriever
  cannot be module-level for `rag_lookup_methodology`; it must be instantiated per call with the
  dynamic `phase` filter. Both bugs are recorded in DECISIONS.md §E3 and §E4 and in
  REVIEW_DECISIONS.md §33 compliance audit. Fix before Step 3.1.
- **REFACTORING §37 canonical implementation** — three bugs confirmed by §37 compliance audit
  (2026-08-11). (1) §37-A (Critical): same `'all'` → `'general'` filter bug as §33. (2) §37-B
  (High): same per-call constructor requirement as §33. (3) §37-C (Medium): §37's implementation
  note states EnsembleRetriever is "deprecated" — incorrect; it is active in
  `langchain.retrievers.ensemble` (v0.3 confirmed), but wrong pattern for same-index multi-query
  fusion (see DECISIONS.md §E1). Apply all three fixes in the same batch commit as §33.
  The §37 memory taxonomy is now complete — §37-D (Procedural Memory) ratified; see DECISIONS.md §K1.
- **REFACTORING §29** — uses class name `RetryMiddleware` for invisible tool-call retries. This
  class does not exist in LangChain 1.x. The correct class is `ToolRetryMiddleware` (M4, verified
  2026-08-12). Do not cite the §29 class name until the batch commit corrects it.
- **Any five-middleware reference in CLAUDE.md or ARCHITECTURE.md** — the ratified stack is now
  eight middlewares (B3 amended 2026-08-12 to seven; B3.1 amended 2026-08-12 adding
  ToolRetryMiddleware at position 5). Any document showing five or seven entries is stale pending
  the next CLAUDE.md/ARCHITECTURE.md revision.
- **L2a coherence in COACHING_QUALITY_RUBRIC** — L2a coherence check moved to `CoherenceMiddleware`
  (Mod B / M3, ratified 2026-08-12). Any rubric entry for coherence under `DMAICGraderMiddleware`
  is stale. `DMAICGraderMiddleware` evaluates process quality only.

---

## 9. Key architectural decisions (summary — see DECISIONS.md for full detail)

**State:**
- SupervisorState: 7 fields. PhaseState: **17 fields (3 plumbing + 14 content)**. Three fields added / amended 2026-08-11:
  - `hop_results: list[str]` — ordered hop answers for Analyse planned multi-hop; `[]` otherwise (§71-E)
  - `synthesis_output: Optional[dict]` — `SynthesisOutput` from dedicated synthesis LLM call; `None` for single-hop (§71-D Option B)
  - `coaching_plan` type tightened: `dict[str, Any]` → `Optional[CoachingPlan]` Pydantic model (§71-C)
- All captured fields are `str`. Three cross-phase reference dicts are `dict` (causal_hypothesis,
  solution_linked_to_root_cause, post_improvement_metric).
- `gate_apply_node` writes BOTH store and `PhaseState.final` — dual write is required.

**Middleware (declaration order = execution order) — eight middlewares (B3.1):**
1. `BeforeModelStateInjection` (before_agent, MUST be first) ← hook type corrected: before_agent, not before_model
2. `DMAICSkillsMiddleware` (before_agent)
3. `SummarizationMiddleware` (before_model)
4. `ModelRetryMiddleware(retries=2)` (wrap_model_call) — API-level Azure OpenAI retries
5. `ToolRetryMiddleware(max_retries=2, on_failure="continue")` (wrap_tool_call) — tool execution retries (B3.1)
6. `ContradictionDetectionMiddleware` (after_agent) — §38 check: deterministic dict comparison, no LLM, HITLInterrupt on any gate-approved value change (Mod A / M2)
7. `CoherenceMiddleware` (after_agent) — L2a check: LLM call (operational model, temp 0.1), max 2 silent retries, DMAICGraderMiddleware skipped on coherence failure (Mod B / M3)
8. `DMAICGraderMiddleware` (after_agent) — process quality only (seven-step computation pattern, show-first principle, citations)

Adding a new middleware or changing execution order requires an amendment to B3 in DECISIONS.md.

**Two graders, not one** (updated 2026-08-12):
- `CoherenceMiddleware` → L2a coherence check → every coaching turn → after_agent → runs before DMAICGraderMiddleware
- `DMAICGraderMiddleware` → `COACHING_QUALITY_RUBRIC` (process quality only: seven-step computation pattern, show-first principle, citations) → every coaching turn → middleware
- Validation stack Layer 2d → `PHASE_RUBRIC` → gate boundary only → `validation_stack` node
- L2a coherence is NOT in `COACHING_QUALITY_RUBRIC` — moved to `CoherenceMiddleware` in Mod B (M3). Any reference to coherence as a `DMAICGraderMiddleware` criterion is stale.

**All after_agent middlewares fire every coaching turn** — not just at gate boundaries. The gate
boundary triggers the `validation_stack` NODE (inside the five-node subgraph), which is a
separate mechanism using PHASE_RUBRIC. Do not conflate these two.

**Tools:**
- 7 universal tools (record_field RETIRED — field capture via CoachingResponse structured output)
- Phase-specific computation tools: 1 (Define), 8 (Measure), 5 (Analyse), 1 (Improve), 5 (Control)
- `create_react_agent`, `langgraph.prebuilt` — BANNED
- `HumanInTheLoopMiddleware` — REJECTED (confirmed bugs: edit/reject broken in subgraph contexts)
- MCP — ARCHITECTURALLY EXCLUDED (permanent)

**Retrieval:**
- Three tools: `rag_lookup_methodology`, `rag_lookup_evidence`, `rag_lookup_case_history`
- Multi-query + RRF (k=60) inside each tool, per-tool `AzureAISearchRetriever` instantiated
  per call with `filters=` in constructor (not module-level; not `search_kwargs` at invoke time)
- `EnsembleRetriever` — wrong pattern (multi-source fusion, not same-index multi-query); not used
- Custom `reciprocal_rank_fusion()` — 15 lines, no LangChain class dependency

**Multi-hop:**
- Mechanism: ReAct tool-calling loop inside the executor (not a separate subsystem)
- Hop cap: `RemainingSteps` managed value inside the agent node — graceful synthesis when low
- `recursion_limit`: high backstop on supervisor invocation (e.g., 50) — catches bugs only,
  NOT the hop budget. `recursion_limit=11` at supervisor level does not reliably give the
  executor 5 hops due to subgraph step-sharing and non-propagation issues (DECISIONS.md §F6)
- §34-D model tiering (gpt-4o-mini intermediate / gpt-4o final) — deferred to §87 backlog;
  trigger is LangSmith evidence of repeated 5-hop cap hits on Analyse-phase turns

**Checkpointer:**
- `AzureBlobCheckpointSaver` during refactor
- `PostgresSaver` + `PostgresStore` post-refactor, pre-production
- `InMemorySaver` — BANNED at all stages, including development

**thread_id:**
- One `thread_id` per project (`case_id` value)
- Checkpointer on parent graph ONLY; subgraphs compiled without checkpointer
- LangGraph auto-manages `checkpoint_ns` per subgraph

**Memory architecture (§37-D ratified 2026-08-11 — see DECISIONS.md §K1):**
- Five memory types: Episodic, Semantic, Working, Retrieval control, Procedural
- Procedural has two levels:
  - Static (v2.1): invariant DMAIC methodology — system prompt + SKILL.md via DMAICSkillsMiddleware
    + phase rubrics via DMAICGraderMiddleware + anti-hallucination guards. Correct that this is
    static — methodology consistency is the guarantee.
  - Dynamic (v2.2+): Belt-adaptive coaching delivery — per-Belt procedure store updated via
    LangSmith trace analysis after gate outcomes. The mechanism is §87 backlog item 5 (reframed
    from "LangSmith trace-based coaching learning"). Does not change DMAIC methodology, only
    adapts delivery.

---

## 10. Version log

| Date | Change |
|---|---|
| 2026-08-19 | v2.8 — §22 deferral confirmed (not implemented in v2.1; test Analyse node first; deferred to §87 backlog). §67 DORA non-compliance identified; v2.2 five-level geographically redundant fallback chain ratified (Sweden Central candidate); deferred to §87 backlog item 14. DECISIONS.md updated to v1.4. §1 "seven middleware" corrected to "eight middleware." §6 pending amendments: G1 (REVIEW_DECISIONS.md §67 amendment) and G2 (REVIEW_DECISIONS.md §22 status update) added. §7 open items: REVIEW_DECISIONS.md not yet updated flagged. §8 stale zones: §22 REVIEW_DECISIONS.md entry added. |
| 2026-08-19 | v2.7 — Hard rule added to §4: Claude must read project documents and check Tier 1 sources before answering any architectural question. Non-negotiable. Rationale: verification failures (DMAICGraderMiddleware firing schedule, RetryMiddleware class name) caused rework. §3 "What was done" updated with B3.1 (ToolRetryMiddleware) and M4 (§29 naming). §7 open items updated with §29 batch commit. §8 stale zones: §29 RetryMiddleware stale zone added; five/seven-middleware stale zone updated to eight. §9 middleware summary updated to eight entries; explicit note that after_agent fires every turn (not gate-boundary). |
| 2026-08-12 | v2.6 — Mod A and Mod B ratified; B3 amended to seven-middleware stack; BeforeModelStateInjection hook type corrected (before_model → before_agent); ContradictionDetectionMiddleware (§38 check, after_agent, deterministic dict comparison, HITLInterrupt on value change, Mod A/M2) and CoherenceMiddleware (L2a check, after_agent, LLM call, max 2 silent retries, DMAICGraderMiddleware skipped on failure, Mod B/M3) added; L2a moved from COACHING_QUALITY_RUBRIC to CoherenceMiddleware; D69-x confirmed closed (M1). DECISIONS.md v1.3 written. REVIEW_DECISIONS.md amended. §8 stale zones for five-middleware references and L2a in COACHING_QUALITY_RUBRIC added. |
| 2026-08-11 | v2.5 — §37 compliance audit (4 findings): §37-A/§37-B confirmed (same retrieval bugs as §33); §37-C (EnsembleRetriever prose incorrect); §37-D ratified (Procedural Memory taxonomy, static v2.1 / dynamic v2.2+). DECISIONS.md v1.1: Part K added, E1/E3/E4 cross-referenced. §8 stale zone for §37 added. §9 memory architecture summary added. LangMem added to Tier 1 sources. |
| 2026-08-11 | v2.4 — §71-D revised: Option B ratified (3 LLM calls/turn). synthesis_output added to PhaseState. PhaseState count revised to 17. DECISIONS.md §F7c, A2 updated. |
| 2026-08-11 | v2.3 — §71 compliance audit: 5 findings; 4 blocking Step 3.1. CoachingPlan Pydantic schema ratified (§71-C). hop_results added to PhaseState (§71-E). RemainingSteps guard at node entry (§71-B). DECISIONS.md §F7, A2 updated. |
| 2026-08-11 | v2.2 — §34 compliance audit: RemainingSteps ratified for hop cap; recursion_limit demoted to backstop. DECISIONS.md §F6 added. §9 retrieval + multi-hop summary updated. |
| 2026-08-11 | v2.1 — §33 compliance audit: two bugs found (phase_relevance `'all'` → `'general'`; search_kwargs → constructor filter). DECISIONS.md §E4 added. Stale zone §8 extended. |
| 2026-08-11 | v2.0 — comprehensive rewrite; added document map, review history, trusted sources, session protocol, full stale zones, architectural summary |
| 2026-08-10 | v1.x — §3 updated: §79–§84 RESOLVED (all 6 items landed in CLAUDE.md v2.2.14) |
| 2026-08-10 | v1.x — updated CONTINUITY.md §3 for multi-query Option A and content_vector ratifications |
| 2026-08-05 | v1.x — seven-step coaching, show-first principle, process map Tier 1 promotions landed (CLAUDE.md v2.2.12–14) |
| 2026-08-03/05 | v1.x — 26 state design findings locked (CLAUDE.md v2.2.9–12) |

