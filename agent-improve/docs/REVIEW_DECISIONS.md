<!--
Review document: agent-improve/reviews/REVIEW_DECISIONS.md
Normalised: UTF-8 without BOM, LF line endings
Purpose: tracked review artefact for cross-session architectural reference
Added in: f44e5c7
-->

# EDUCATIONAL.md Review — Decision Log

**Scope:** Full pre-refactor review of EDUCATIONAL.md (v as of upload, 85 sections at start, 10,416 lines).

**This log's three roles (ratified by user this session):**

1. **Corrections applied to EDUCATIONAL.md** — batch commit turns the 85-section file into a corrected version (85 + §86 authored + §87 backlog = 87 sections at end).
2. **Basis for ground-up rewrite of CLAUDE.md and ARCHITECTURE.md** — after EDUCATIONAL.md batch commit lands, both governance docs get rewritten to align. Versioning target: **CLAUDE.md v2.1 → v2.2, ARCHITECTURE.md v2.1.1 → v2.2.** Not incremental patches — full alignment pass so the new v2.2 versions reflect every ratified decision cleanly.
3. **Plan for Agent Improve v2.1 refactoring in Claude Code** — the ratified decisions drive the actual codebase changes: schema updates (index rename, 18 computation tools, three retrieval tools with metadata filters, SupervisorState/PhaseState additions), middleware wiring (SummarizationMiddleware, `before_model` injection, mid-phase conflict detection), and file-level changes captured throughout this log.

**File rename at end:** EDUCATIONAL.md → REFACTORING_AGENT_IMPROVE.md
**New file to follow (separate cowork):** AGENT_DESIGN_GUIDELINES.md (clean grouping + weekly-update skill)

**Sequence to execute:**
1. Finish EDUCATIONAL.md review (current phase, currently around §40)
2. Batch commit EDUCATIONAL.md → REFACTORING_AGENT_IMPROVE.md via Claude Code
3. Ground-up rewrite of CLAUDE.md (v2.1 → v2.2) and ARCHITECTURE.md (v2.1.1 → v2.2) — both must reflect every ratified decision in this log
4. Agent Improve v2.1 codebase refactor executes against the new v2.2 governance docs
5. Follow-up cowork space authors AGENT_DESIGN_GUIDELINES.md with weekly-update skill for LangChain/LangGraph/LangSmith drift monitoring

**Housekeeping the user should update in Project instructions:**

- **MCP removal from stack description.** Instructions currently read *"built Gap Report — SupervisorState / PhaseState vs DMAIC requirements
Sources cross-referenced

#	Source	What I used
1	Governance docs	SupervisorState (8 fields) and PhaseState (11 fields), verified identical in CLAUDE.md §10.1 and ARCHITECTURE.md §4.1 after f429e36
2	MBB eBook	5_BB_EB_MT_v11.1_PDF2_compressed (1).pdf, 700pp. Extracted with the project venv's pypdf. Phase checklists at p84 (Define), p234 (Measure), p421 (Analyse), p558 (Improve), p681 (Control)
3	Code	core/state.py, storage/models.py, five phases/*/schema.py, four *_REQUIRED_FOR_GATE lists in phases/*/validate.py
merged_output.pdf does not exist in the repo — only the 5_BB_EB_MT_v11.1 file and Problem Solving 8D.pdf.

1. SupervisorState — routing sufficiency
Every field present is needed. project_id (thread_id + store namespace), gate_passed (routing), messages/history (conversation), project_context (feeds input mappers), final_output. No field is dead.

1.1 — CRITICAL: gate_attempts is required by rule and declared nowhere
CLAUDE.md §1.7: "gate_attempts MUST be in the checkpointed state, never in route scope — this is what fixes the v1 'attempts always reset to 0' bug." §3.5 repeats it.

It is not in SupervisorState and not in PhaseState. v1's ImproveGraphState has it (gate_attempts: int, line 25). The refactor dropped the field while keeping the rule that mandates it, and §9.2's "iteration cap is 3, SHARED across all four layers" has no counter to live in.

This is the one finding I'd fix before any other. It reintroduces the exact v1 bug the architecture was written to close.

1.2 — escalated has no home either
v1 has escalated: bool. §3.5 routes to the escalation subgraph by conditional edge. If that edge reads gate_attempts >= 3 the flag is genuinely derivable; if it needs to stay escalated across turns, it is not. Undetermined in the docs — worth deciding explicitly.

1.3 — current_phase and phase_index are derivable from gate_passed
Both are PHASE_ORDER[len(gate_passed)] and len(gate_passed). By the exact argument used to remove open_items in f429e36 — "a stored copy can contradict the derived one" — these two are the same redundancy class. A gate_passed of ["define","measure"] with current_phase: "control" is representable and wrong.

I'm not recommending removal; current_phase is read in many places and the ergonomics are real. But the principle you just ratified applies to them, and the docs should say why they're exempt.

1.4 — project_id vs case_id is an unresolved naming split
Docs use project_id throughout. All code uses case_id — ImproveGraphState, CaseDocument, RegistryEntry, and improve_evidence_index's filter field (§7.3). If they're the same identifier, one name should win before core/state.py is written; if not, SupervisorState is missing whichever one it lacks.

2. PhaseState — can it hold what a Belt produces?
artifacts: dict[str, Any] is untyped, so structurally it can hold anything. The gaps are in the fields around it.

2.1 — There is no captured_fields
Your question names PhaseState.captured_fields. That field does not exist — it's artifacts. Three names are in play for one concept: artifacts (schema + store namespace), "captured fields" (CLAUDE.md §8.5, §6.3), phase_inputs (all current code). Worth collapsing to one.

2.2 — Missing fields
Missing	Required by	Evidence
gate_attempts	§1.7, §3.5, §9.2 shared cap of 3	Absent from both schemas; present in v1
Accumulated validator feedback	§9.2 "3 attempts with accumulated feedback"	feedback is documented as "Belt corrections at gate" — a different thing. Per-layer feedback fed back to the executor has no field
citations	§13 (visible citations), core/citations.py, PhaseRecord.citations	v1 has it. PhaseState does not. Citations have nowhere to accumulate during a phase
uploads	§1.9 (uploads are the only external data channel), PhaseRecord.uploads	v1 has uploaded_files. PhaseState does not
analyst_output	PhaseRecord.analyst_output	v1 has it; no home in the new schema
Citations and uploads are the notable ones — both are persisted by PhaseRecord, so something must produce them, and no state field does.

2.3 — Two type problems
final: str — documented as "approved gate document". But §10.1's own rule is that draft and feedback are dict never str because "string-typed handoffs force downstream nodes to parse prose." The gate document is the single most downstream-consumed artifact in the system and it is typed str. This contradicts §4.6 and §10.2.

coaching_plan: list[dict[str, Any]] — CLAUDE.md §1.3 and §3.3 describe the planner producing one structured plan (focus_field, next_action, retrieval_strategy, tools_needed). REFACTORING §10's earlier example has coaching_plan: dict. List-of-dicts vs single dict is unreconciled.

3. Rubric criteria → field mapping (§42)
7 of 21 rubric criteria have no corresponding field.

Phase	Criterion	Field	Status
Define	problem_statement	—	⚠ Composite of 7 5W2H fields; no single field
Define	business_case	business_case_rationale	✅ name mismatch only
Define	project_scope	scope_in + scope_out	✅ composite
Define	team	team_members	✅
Define	goal_statement	goal_statement	✅
Measure	baseline_mean	baseline_mean	⚠ Optional[str], not gate-required
Measure	baseline_sigma	—	❌ No field. baseline_variation and current_sigma_level are neither
Measure	measurement_system_validated	msa_required	⚠ Gate requires the question; msa_result (the evidence) is not gate-required
Measure	data_collection_plan	data_collection_plan	✅
Analyse	root_causes	vital_few_causes, root_cause_statement	✅
Analyse	root_cause_validation	cause_verified	⚠ verification_method/evidence_summary not gate-required
Analyse	causal_hypothesis	—	❌ No field. Rubric says "linked back to captured baseline metric" — nothing links Analyse to Measure's baseline
Analyse	ruled_out_causes	—	❌ No field. No "rejected with rationale" anywhere
Improve	solution_selected	selected_solution	✅
Improve	solution_linked_to_root_cause	—	❌ No field. selection_rationale is generic prose
Improve	pilot_results	pilot_result	✅
Improve	implementation_plan	implementation_plan	⚠ not gate-required
Control	control_plan	control_plan	✅
Control	sustainability_check	sustainability_confirmed	✅
Control	post_improvement_metric	—	❌ No field. Control captures no post-improvement measurement at all
Control	handover_documented	—	⚠ documentation_updated + sponsor_final_sign_off, neither gate-required, neither is handover to process owner
post_improvement_metric is the most serious. The Control schema has no field for the measured value after improvement — so the project cannot demonstrate the baseline actually shifted. eBook p681 opens with "How do the results of the improvement(s) match the requirements of the business case and improvement goals?" and lists "Verify Financial Impact" as a required action item.

The three "linkage" criteria (causal_hypothesis, solution_linked_to_root_cause, post_improvement_metric) fail for one shared reason: nothing in the schema carries a cross-phase reference. Each phase's fields are self-contained, so a grader asked to check "is this linked to the baseline?" has no field to read.

4. eBook coverage gaps
Requirements from the phase checklists with no corresponding field:

Phase	eBook requires (p.)	In schema?
Define (84)	COPQ identified; finance/controller involvement	❌ (current_cost adjacent)
Define (84)	VOC identified, VOC requirements, stakeholder key issues	❌ none
Define (84)	High-level process map + who developed it	❌ (sipoc optional, different artifact)
Measure (234)	As-is process map, decision points, data collection points	❌
Measure (234)	X-Y matrix; FMEA	❌
Measure (234)	Stability / special causes (Voice of the Process)	❌
Measure (234)	Short-term and long-term capability	⚠ single current_sigma_level
Analyse (421)	Completed hypothesis tests; statistical problem statement	❌
Analyse (421)	Response discrete or continuous; mean vs variance	❌
Analyse (421)	Updated FMEA; process owner buy-in	⚠ root_cause_agreed_by, not gate-required
Improve (558)	DOE justification, execution, mathematical model	❌
Improve (558)	Practical and statistical significance	❌
Control (681)	Verify financial impact	❌
Control (681)	Lessons learned; transferability / spreading best practice	❌
Control (681)	Control plan handed off to process owner	❌
Control (681)	Champion + Belt + Finance agree project complete	⚠ sponsor_final_sign_off only
A structural observation: §5.2 binds 18 computation tools, and their outputs have nowhere typed to land. Analyse gets t_test, chi_square_test, anova, pearson_correlation, linear_regression; AnalysePhaseInput has no field for a test result. Improve gets calculate_doe_main_effects; ImprovePhaseInput has no DOE field. Control gets four control-chart tools; ControlPhaseInput has control_chart_type (a label, not results). A Belt can run the tool and the number is lost unless it's prose in evidence_summary — which §4.3 forbids parsing back out.

Transferability is a platform-level gap. rag_lookup_case_history exists for yokoten and improve_case_index carries phase_summary_*, but no field captures the transferable lesson, so cross-case retrieval has thin material to work with.

5. Boundary mapper cross-check
Does the handoff carry what the next planner needs? Partially — with one contradiction and one omission.

5.1 — CONTRADICTION: the typed-float promise cannot be kept
CLAUDE.md §10.2: "Measure reads Define's baseline metric as a typed float, not out of prose."

Every baseline field in code is a string:

DefinePhaseInput.how_much_baseline: str — "1.8mm vs 1.3mm avg"
MeasurePhaseInput.baseline_mean: Optional[str] — "Average value with unit"
There is no typed float anywhere in the system. The rule that justifies the store-mediated handoff describes a data shape that does not exist. Either the fields become numeric (with separate unit fields), or §10.2 is overstating what the mapper delivers.

5.2 — OMISSION: gate documents are never written
§10.2 defines two store namespaces: "artifacts" and "gate_documents". define_output_mapper writes only artifacts. Nothing writes gate_documents, and PhaseState.final — the approved gate document — is never persisted anywhere. A downstream phase reading "Define's gate document" would find an empty namespace.

5.3 — Smaller items
define_input_mapper(parent, store) takes store and never uses it. Correct for Define (no prior phase), but the signature implies a contract it doesn't honour, and no other input mapper is specified anywhere.
ARCHITECTURE §4.3 step 5 asserts measure_input_mapper "reads Define's artifacts from the store and builds Measure's phase_context" — there is no code or spec for which subset. Since artifacts is untyped, the next planner receives an opaque dict.
measure/validate.py currently pre-populates primary_metric_confirmed/secondary_metric_confirmed from Define's phase_inputs. That's a real cross-phase dependency satisfied today by v1 flat state. Under v2 it must come through the store, and no mapper spec covers it.
PhaseRecord.gate_passed is bool per phase; SupervisorState.gate_passed is list[str]. Same name, two shapes, two layers — currently harmless, but a rename on one side would be safer.
6. Ranked summary
#	Finding	Severity
1	gate_attempts mandated by §1.7/§3.5, absent from both schemas — reintroduces the v1 reset bug	Critical
2	gate_documents namespace never written; final never persisted	Critical
3	§10.2's "typed float" baseline contradicts every baseline field being str	High
4	Control has no post_improvement_metric — cannot show the baseline shifted	High
5	7 of 21 rubric criteria have no field; 3 fail for the same cross-phase-reference gap	High
6	No field for accumulated validator feedback (§9.2)	High
7	18 computation tools have no typed destination for results	High
8	citations and uploads persisted by PhaseRecord, absent from PhaseState	Medium
9	final: str violates §10.1's own dict-not-str rule	Medium
10	project_id vs case_id unresolved across docs and code	Medium
11	Rubric criteria not gate-required (baseline_mean, implementation_plan, msa_result) — grader can fail what the gate passed	Medium
12	eBook items absent: VOC, COPQ, FMEA, stability, hypothesis tests, financial verification, lessons learned	Medium
13	current_phase/phase_index derivable from gate_passed — same redundancy class just removed	Low
14	coaching_plan list-vs-dict unreconciled	Low
15	Three names for one concept: artifacts / captured fields / phase_inputs	Low
Findings 1, 2 and 6 are self-inflicted — the rules requiring them already exist and the schemas don't satisfy them. They're cheap to fix and I'd take them first. Findings 4, 5 and 7 are the substantive DMAIC gap: the schemas capture what a Belt says but not what a Belt measures, and the rubrics already ask for the latter.

Want me to draft the schema amendments for the critical set, or work through the rubric/field reconciliation first?on LangChain 1.x, LangGraph 1.2+, Azure OpenAI, and MCP."* Post-§39 ratification (MCP explicitly out of scope for AgentLean), MCP should come out of the stack list. It remains valid as EDUCATIONAL.md pedagogical content, not as a runtime component.
- **Section count.** Instructions say EDUCATIONAL.md has *"86 sections as of July 2026."* Actual file has 85 sections; target end-state is 87 sections (85 original + §86 authored + §87 backlog). Update instructions to reflect target once batch commit lands.
- **LangGraph version precision.** Instructions say *"LangGraph 1.2+"* — current codebase pinned at 1.1.10 per user-provided requirements.txt. Recommend tightening to *"LangGraph 1.2.6+"* once upgrade lands, since our ratified §23 subgraph design depends on the checkpoint_ns fix in that point release. See "Runtime version target" note below.

**Runtime version target for v2.1 refactor (verified this session):**

- `langgraph`: upgrade 1.1.10 → 1.2.7 (latest on PyPI). Required for §23 subgraph checkpoint_ns fix and consistent with §34's `recursion_limit` + `GraphRecursionError` handling.
- `langchain`: 1.2.13 → 1.3.11 optional but recommended; backward compatible per LangChain 1.0 stability commitment.
- `langchain-classic`: keep at 1.0.3. Retains `MultiQueryRetriever`, `EnsembleRetriever` legacy classes (verified deprecated but present — not used in ratified design).
- `langgraph.prebuilt` deprecated in 1.0 → 1.1, functionality moved to `langchain.agents`. Codebase sweep needed during upgrade — any imports from `langgraph.prebuilt` must migrate.
- Adjacent packages (`langchain-core`, `langchain-openai`, `langchain-community`, `langchain-text-splitters`, `langsmith`, `langfuse`) — let pip resolve during upgrade, then repin.

---

## Pre-commit priority actions (do first, before other batch-commit work)

These items were elevated to first-priority status this session. Order matters — later work depends on some of these landing.

**1. Rename `phase_summary_analyse_phase` → `phase_summary_analyse` in `improve_case_index`.**

*User decision this session:* fix the field name at the source rather than maintaining a mapping constant. Cleaner than the workaround I originally proposed in §40.

Scope of change:
- Update `improve_case_index` schema in Azure AI Search
- Reindex existing case content (breaking change — the field name changes, existing indexed documents need to have the field renamed or be reindexed with the new schema)
- Update any code that reads `phase_summary_analyse_phase` to use `phase_summary_analyse` — codebase sweep needed at implementation time
- Update CLAUDE.md §7 and ARCHITECTURE.md §7 schema documentation (see item 2) to reflect corrected name

Priority reason: any code that uses the naive pattern `phase_summary_{phase.lower()}` will fail on Analyse until this is fixed. Fixing the field name up-front means no mapping constants ever exist in the codebase, and future readers won't be surprised by the inconsistency.

Deferred consideration: whether other similar field-name inconsistencies exist across the three indexes. Worth a schema audit during batch commit.

**2. Capture full index schemas in CLAUDE.md §7 and ARCHITECTURE.md §7.**

*User decision this session:* the schemas verified against actual Azure AI Search state must be documented in both governance docs as part of batch commit. Without this, decisions keep discovering schema facts (vector field names, field-name inconsistencies, `case_id` filter capability, `days_in_phase` as Int32) that were not documented.

Schemas to capture (as verified user-provided this session, post-rename in item 1):

*`improve_knowledge_index`:*
```
id                String
content           String
content_vector    SingleCollection (3072d)
metadata          String
source_file       String
phase_relevance   String
page_number       Int32
```

*`improve_evidence_index`:*
```
id                String
content           String
content_vector    SingleCollection (3072d)
metadata          String
case_id           String
```

*`improve_case_index` (post-rename):*
```
id                      String
case_id                 String
title                   String
belt_level              String
leader                  String
department              String
current_phase           String
rag_status              String
status                  String
created_at              String
target_date             String
days_in_phase           Int32
phase_summary_define    String
phase_summary_measure   String
phase_summary_analyse   String   ← RENAMED per item 1
phase_summary_improve   String
phase_summary_control   String
content_text            String
embedding               SingleCollection
```

Placement: both governance docs should have an "Index Schemas" subsection under §7. Recommend a single canonical source (e.g., ARCHITECTURE.md §7 holds the full schemas, CLAUDE.md §7 references ARCHITECTURE.md rather than duplicating). Prevents drift between the two governance docs.

Note on `improve_case_index.embedding`: vector dimension not explicitly stated in the user-provided schema paste. Likely 3072 (consistent with `text-embedding-3-large` used by the other two indexes). Confirm the actual dimension when documenting in the governance doc.

---

## Trusted sources for architectural reasoning (ratified and UPDATED August 2026)

**IMPORTANT: The December 2024 "Building Effective Agents" post was the primary Anthropic reference throughout this review. It is now 19 months old. Anthropic published 14 engineering posts after it, several of which directly evolve or supersede its guidance. The table below reflects the corrected priority as of August 2026.**

### Tier 1 — Primary (current, authoritative, check before any architectural decision)

| Source | Date | Topic | Why it matters |
|---|---|---|---|
| `anthropic.com/engineering/effective-harnesses-for-long-running-agents` | Nov 2025 | Harness concept, context reset, session bridging | Reframes agents as "harness + model." The harness (control plane) is the engineering, not the prompt. Directly relevant — DMAIC coaching is a long-running agent task. |
| `anthropic.com/engineering/harness-design-long-running-apps` | Mar 2026 | Planner/Generator/Evaluator, ablation discipline | Three-agent architecture tested against solo agent. Maps to our Planner/Executor/Grader. **This is the current Anthropic agent architecture guidance.** |
| `anthropic.com/engineering/managed-agents` | Apr 2026 | Brain/hands separation, scaling | Separating planning from execution at infrastructure level. Confirms our Planner-Executor cascade. |
| `anthropic.com/engineering/how-we-contain-claude` | Jul 2026 | Containment, blast radius, security boundaries | Newest post. Containment architecture for Claude products. Relevant for hook security (§45/§86). |
| `anthropic.com/engineering/effective-context-engineering-for-ai-agents` | Sep 2025 | Context window management as first-class discipline | Directly relevant to SummarizationMiddleware and progressive skill disclosure. |
| `anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills` | Oct 2025 | Agent Skills, SKILL.md spec | The spec our §83/§84 skills middleware is built against. |
| `anthropic.com/engineering/demystifying-evals-for-ai-agents` | Jan 2026 | Eval design for agents | Directly relevant to §75 eval dataset. |
| `anthropic.com/engineering/writing-tools-for-agents` | Sep 2025 | Tool design principles | Relevant to our 18 computation tools + 3 retrieval tools. |
| `docs.langchain.com`, `reference.langchain.com`, `python.langchain.com` | Ongoing | LangChain/LangGraph/deepagents official docs | API patterns, middleware, create_agent, structured output |
| `github.com/langchain-ai/*` (repos, issues, releases, changelogs) | Ongoing | Source of truth for code, versions, breaking changes | Version verification, bug fixes, feature status |
| `pypi.org` | Ongoing | Package versions and dependency data | Definitive version/dependency data |

### Tier 2 — Official publications (announcements, strategic context)

| Source | Content type |
|---|---|
| `langchain.com/blog` | LangChain team feature announcements and design rationale |
| `anthropic.com/news/*` | Product announcements, enterprise case studies |
| `resources.anthropic.com` | Whitepapers, trend reports (2026 Agentic Coding Trends Report) |
| `claude.com/blog/*` | Claude-specific product blog |

### Tier 3 — Informed practitioner (cross-checked, cited)

| Source | Content type |
|---|---|
| `marsdevs.com/guides` | Practitioner guides with Tier 1 citations |
| `deepwiki.com/langchain-ai/*` | Community wiki with source references |
| `agentpatterns.ai` | Pattern vocabulary crosswalk across frameworks |

### Downgraded — Historical context (no longer primary)

| Source | Date | Status |
|---|---|---|
| `anthropic.com/engineering/building-effective-agents` | Dec 2024 | **Historical foundation.** Still the most-cited post in the industry. Core advice ("start simple, add complexity only when needed") remains valid. But the harness concept, Planner/Generator/Evaluator pattern, context reset discipline, and ablation approach from the 2025-2026 posts supersede it for architectural guidance. |

### Excluded

Stack Overflow, Reddit, Medium, Dev.to — unverified unless linking directly to Tier 1 content.

### Verification discipline going forward

Before any architectural decision: check `anthropic.com/engineering` post index and `pypi.org/project/langgraph` release history. These two sources move fastest and have the most impact on our design.

The AGENT_DESIGN_GUIDELINES.md weekly-update skill (step 11) automates this. Until then, manual checks at the start of each Claude Code session and each claude.ai review session.

---

## Cross-cutting corrections

- **Section count mismatch — RESOLVED.** Project instructions state 86 sections; actual file has 85. Root cause: §45 (line 4547) forward-references "Section 86 for the full verified hook mechanics" but §86 was never authored. Decision: **Path A — author §86 as promised.** Content: "Section 86 — Verified Claude Code Hook Mechanics." Web-verify current Claude Code hooks API before drafting; do not write from memory. Draft deferred to batch phase.

  Related loose ends to close in the same authoring pass:
  - CLAUDE.md §4.3 (mandates `.with_structured_output()`) vs drift hook (blocks that pattern, references non-existent §4.6) — self-contradiction noted in userMemories.
  - Any other §45/§50 references that assume §86 exists.

- **Checkpointer strategy — REVISED this session (replaces earlier "PostgresSaver for both dev and production" ruling).** Phased approach ratified:
  - **During refactor:** keep `AzureBlobCheckpointSaver` (already committed at steps 2.1–2.2, unit tested, wired into `graph.compile()`). Works for single-developer development. No new infrastructure needed.
  - **Post-refactor, pre-production:** migrate to `PostgresSaver` + `PostgresStore`. Add Azure Database for PostgreSQL (~€12-15/month flexible server). Migration is small — change checkpointer constructor and connection string, run existing unit tests against PostgreSQL.
  - **Rationale for the phased approach:** `AzureBlobCheckpointSaver` is custom code maintained by us, not the LangChain team. It wasn't tested for concurrent access (Azure Blob has no row-level locking). `PostgresSaver` is the officially maintained, primary tested path — handles concurrency correctly, queryable with SQL for debugging, updated by the LangChain team on every LangGraph release. But adding PostgreSQL during the heaviest refactoring period adds unnecessary infrastructure complexity. Use the working Blob checkpointer during refactor, migrate to the production-grade path before real Belts use the system.
  - **`AzureBlobStore` (for cross-phase artifacts):** same phased approach. Build against Azure Blob during refactor, migrate to `PostgresStore` alongside the checkpointer migration.
  
  Affected sections in the log: §17 (SupervisorState references to store), §36 (context management), §52 (Checkpointer + BaseStore split), and the AzureBlobStore new section — all remain architecturally correct. Only the backing implementation changes from Azure Blob to PostgreSQL at migration time. The `BaseCheckpointSaver` and `BaseStore` interfaces are the same regardless of backend.

- **Overlap and duplication across sections.** Multiple sections cover related concepts from different angles (§5/§11/§17/§20 all touch Planner/Executor; §17/§18/§19/§23 all touch state and subgraph mechanics; §26/§44/§45/§50 all touch governance and anti-drift). This is expected given the file is a chronological training register. The batch commit is the point at which overlaps get reconciled — during review we capture the intended reconciliation without editing yet. Final commit produces a coherent set of sections with cross-references, not five sections repeating each other.

- **Topic groups index misalignment.** The Document Navigation index at the top of the file lists incorrect section numbers in at least one place: index says "Section 28 — Multi-Query Retrieval (parallel variants)" but actual §28 is "LCEL Primitives — RunnableParallel, RunnableBranch, Pipe Operator." Multi-Query Retrieval is §32. Sweep the entire index against actual section headings during batch commit; correct all mismatches.

- **Canonical tool names (authoritative reference).** Some earlier entries in this log used the placeholder name `rag_lookup(query, phase)` before Option B naming was ratified. The final canonical retrieval tools for v2.1 are:
  - `rag_lookup_methodology(query, phase, top_k)` — hits `improve_knowledge_index`, filters by `phase_relevance` (per §37 decision), uses `content_vector` field, applies multi-query + RRF
  - `rag_lookup_evidence(query, case_id, top_k)` — hits `improve_evidence_index`, filters by `case_id`, vector field to be confirmed against index schema, applies multi-query + RRF
  - `rag_lookup_case_history(query, top_k, exclude_current_case=True)` — hits `improve_case_index`, uses `embedding` field, applies multi-query + RRF, supports yokoten
  
  Any earlier `rag_lookup` reference in this log should be read as pointing to whichever of the three applies to the surrounding context. Claude Code's batch commit should use the three canonical names throughout the refactored EDUCATIONAL.md, CLAUDE.md §7, and ARCHITECTURE.md §3.2 / §7.

---

## Section-by-section decisions

### §2 — Human-in-the-Loop (Interrupts)

**Change:** Replace the sparse three-row interrupt-point table with the full eight-step gate pattern.

**Rationale:** Current text describes interrupts only as approve/reject binary. The correct pattern includes belt-edit and a policy advisory step between edit and approve, so the LLM's second-opinion analysis reaches the belt *before* the approval decision commits state.

**Replacement text (draft):**

```
## 2. Human-in-the-Loop (Interrupts)

### What It Is
LangGraph pauses graph execution at declared points, persists state, and waits
for explicit human approval before resuming. Requires checkpointing as a
prerequisite.

### How It Works
[existing code block retained]

### Full HITL Gate Pattern (Replaces Approve/Reject Only)

The original description treated interrupts as a binary approve/reject
decision. The correct pattern is an eight-step sequence:

| Step             | What Happens |
|------------------|--------------|
| Executor runs    | Coaching LLM runs + extraction captures phase fields into Task Plan |
| Interrupt fires  | Graph pauses; Belt sees extracted fields in the UI |
| Belt reviews     | Belt checks AI-captured values for accuracy |
| Belt edits       | Belt corrects wrong fields directly in Task Plan (optional) |
| Policy advisory  | Orchestrator reads full phase state, validates against required-field policy and cross-phase consistency rules, surfaces structured feedback to Belt (non-blocking — Belt may act on it or override) |
| Belt approves    | Belt confirms gate is ready — with or without acting on advisory |
| Checkpoint saves | State committed to Azure Blob / PostgreSQL only now — never before Belt approves |
| Next task?       | Supervisor reads gate_passed[], routes to next unfinished phase or next field |

**Why advisory is non-blocking:** The Belt is the domain expert. The policy
check offers a second opinion before the approval decision, not a veto after
it. A blocking post-approval check would place the LLM above the human's
judgment, which is wrong in a coaching context. The advisory fires inside the
existing interrupt window — no additional round-trip.

**Implementation note:** The policy advisory is a validate_phase_gate tool
call from the coaching agent (canonical tool to be defined in Step 3.0 — see
ARCHITECTURE.md §5.1). Not a separate subgraph node.

### Where Interrupts Belong in Agent Improve
[existing table retained]

### Current Gap
[existing text retained]

### Dependency Chain
[existing block retained]
```

**Open questions to confirm before commit:**
- Confirm tool name `validate_phase_gate` matches Step 3.0 intent for `knowledge/tools.py`.
- Confirm scope of policy advisory for v2.1: single-phase field completeness only, or also cross-phase consistency (e.g. Measure's Y matches Define's Y)?

---

### §8 — Implementation Sequencing Decision

**Change:** Section is stale. Its "Correct Sequence" describes Option A (defer refactor until all three agents complete). We selected Option B (see §16). Either rewrite the section to describe the Option B sequence, or mark it superseded with a note pointing to §16.

**Recommendation:** Rewrite. §8 is well-placed in the file; a "superseded" note is jarring. Draft replacement to be produced during batch write.

---

### §16 — Architectural Debt Acknowledgement

**Change:** Record Option B as the selected path.

**Replacement text (draft) for the decision paragraph:**

```
Decision: Option B selected. The v2.1 refactor introduces checkpointer, private
subagent states, and explicit planner/tool-calling nodes before Improve and
Control phases are built. Each new phase will be built on the correct
foundation from the start. See §8 for the updated sequence and CLAUDE.md /
ARCHITECTURE.md v2.1 for the full specification.
```

---

### §17 — InsightForge Mapping — Refactor Specification

**Changes:**

1. **Item 3 checkpointing block** — replace dev/prod split with PostgresSaver-only version (see cross-cutting correction above).

2. **Item 1 SupervisorState schema — align with §18 and slim down.**

   Current schema mixes orchestration state and cross-phase artifacts. With the Checkpointer + BaseStore split (§52 + new section, see below), artifacts move to the store. SupervisorState shrinks to orchestration state only.

   **Renamings for consistency with §18:**
   - `captured_fields` → moved to store, removed from SupervisorState
   - `gate_documents` → moved to store, removed from SupervisorState
   - `step_index` → `phase_index` (disambiguates from field-level index in §18)
   - `step_log` → moved to store (append-only, cross-phase audit trail)

   **Replacement SupervisorState (draft):**

   ```python
   class SupervisorState(TypedDict):
       messages:        Annotated[list[BaseMessage], operator.add]
       history:         Annotated[list[str], operator.add]
       project_id:      str
       project_context: str                          # never changes after Define
       dmaic_plan:      list[dict[str, Any]]
       phase_index:     int                          # 0=Define ... 4=Control
       current_phase:   str
       key_decisions:   Annotated[list[str], operator.add]   # added per §36 decision
       open_items:      list[str]                             # added per §36 decision
       final_output:    str                          # populated on Control gate approval
   ```

   Note: `key_decisions` and `open_items` were added in the §36 decision (context compression) as part of the SummarizationMiddleware plus typed-state design. See §36 log entry.

3. **Item 6 observability block** — the snapshot inspection example references `state.values["captured_fields"]`. That field no longer exists on SupervisorState after the changes above. Update to reference the store instead:
   ```python
   for state in graph.get_state_history(config):
       print(state.values["current_phase"], state.values["phase_index"])
   # Cross-phase artifact inspection uses the store, not checkpoint history:
   store.get(("projects", project_id, "artifacts"), "define")
   ```

---

### §18 — Lab Code — PlannerState Schema

**Changes:**

1. **Rename PlannerState → PhaseState** and align field names with §17 SupervisorState. PlannerState is what runs *inside* a phase subgraph; the name PhaseState is clearer.

2. **Field renamings and type corrections:**
   - `counter` → `turn_count` with explicit comment (coaching turns before gate fires)
   - `step_index` → `field_index` (within-phase field pointer)
   - `plan` type kept as `list[dict[str, Any]]` — already structured, matches design
   - Add `draft: dict[str, Any]` — structured extraction result per turn
   - Add `feedback: dict[str, Any]` — structured Belt corrections at gate
   - Add `phase_context: str` — what this phase is coaching toward
   - Rename `final_output` → `final` for consistency with §19 ChainState

   **Replacement PhaseState (draft):**

   ```python
   class PhaseState(TypedDict):
       messages:      Annotated[list[BaseMessage], operator.add]
       history:       Annotated[list[str], operator.add]
       phase_context: str
       coaching_plan: list[dict[str, Any]]        # phase planner output
       field_index:   int                          # current field within phase
       draft:         dict[str, Any]              # extracted fields this turn
       artifacts:     dict[str, Any]              # accumulated fields for phase
       step_log:      Annotated[list[dict[str, Any]], operator.add]
       feedback:      dict[str, Any]              # Belt corrections at gate
       final:         str                          # approved gate document
       turn_count:    int
   ```

3. **New subsection required — Boundary Mapper Pattern.** Currently implicit. Add explicit input/output mapper functions showing how SupervisorState ↔ PhaseState communicate. Draft to be produced during batch write. See §19 changes for the concrete Define→Measure example.

4. **Mapping table** — the last row referencing InMemorySaver removed per cross-cutting correction. Add row for boundary mappers.

---

### §5 — Planner / Executor Model

**Change:** The two-level cascade in the current section describes Global Planner/Executor and Phase Planner/Executor but does not connect the cascade to the Plan → Execute → Review → Revise cycle from §19. Add explicit framing: **same cycle, nested at two scopes.**

**Addition to draft:**
- New subsection "The Nested Cycle" clarifying that Plan → Execute → Review → Revise happens at both the phase (Level 1) and per-field (Level 2) scope.
- Level 1 Execute contains many Level 2 iterations before Level 1 Review fires.
- Diagram to be produced showing the interleaving.

**Why:** Without this framing, the phase executor collapses back into a monolithic coaching loop with implicit branching inside the prompt — the exact "planning implicit in prompts" problem §5 diagnoses as Gap 10. Making Level 2 explicit is what turns coaching into an inspectable, per-field, structured process.

---

### §19 — Multi-Step Task Chaining

**Changes:**

1. **ChainState field types** — `plan`, `draft`, `final`, `feedback` are all `str` in the course version. This is a teaching simplification. For Agent Improve, replace with structured types matching PhaseState (see §18). Keep the course-original as a "source lab" reference block only, clearly marked.

2. **Multi-Chain Orchestration code block** — replace string-interpolation example with store-mediated boundary mapper for DMAIC. Chain 1 = Define phase; Chain 2 = Measure phase.

   **CORRECTION (from §23 review):** Earlier draft said each phase runs on its own thread_id (`IMPR-2026-FS1-define`, `IMPR-2026-FS1-measure`). That was Pattern B (separate graph invocations). §23 describes Pattern A (subgraphs embedded in parent supervisor graph), and LangGraph docs (verified 2026-07) confirm Pattern A is the native mechanism for multi-phase orchestration. The corrected model:

   - **One thread_id per project**: `IMPR-2026-FS1`
   - **Each phase = one subgraph embedded as a node** in the supervisor parent graph
   - **LangGraph auto-namespaces each subgraph's checkpoints** via `checkpoint_ns` (fixed in LangGraph 1.2.6 — subgraph inherits parent checkpoint_ns correctly)
   - **AzureBlobStore mediates artifacts between subgraphs** — per LangChain docs: *"Use shared state via Store for data that needs to cross graph boundaries"*

   Define's `artifacts` written to store via `AzureBlobStore.put()` at gate approval; Measure's input mapper reads via `store.get()`. Concrete Define→Measure walkthrough already produced in review conversation — to be inserted verbatim into refactored §19.

3. **"AgentLean Mapping" paragraph** — retain and expand to state explicitly: each DMAIC phase is a subgraph embedded in the supervisor parent graph; one thread_id per project; each subgraph has its own auto-managed checkpoint_ns; cross-phase artifacts flow through the store, not through parent state or string concatenation.

4. **New subsection — Nested Plan/Execute/Review/Revise (Level 1 vs Level 2).**

   **Level 1 — Phase chain:**
   - Plan: phase planner decides the coaching strategy for the phase (which fields to elicit, in what order, with which tools)
   - Execute: phase executor iterates through the strategy, running per-field cycles (Level 2)
   - Review: gate interrupt — Belt reviews all captured fields for the phase
   - Revise: Belt edits + policy advisory + Belt approval; final gate document written

   **Level 2 — Per-field cycle (nested inside Level 1 Execute):**
   - Plan: within-turn planner decides the coaching action for the current field (elicit, teach, challenge, re-ask with different framing, offer worked example)
   - Execute: coaching LLM runs; extraction runs; one field captured
   - Review: fast completeness + sanity check on the captured field (no interrupt)
   - Revise: if not clean, loop back to Level 2 Plan with the failure signal; otherwise increment field_index and move to next field

   **Concrete example — Define phase, IMPR-2026-FS1:**
   Six required fields (problem_statement, business_case, project_scope, goal_statement, baseline_metric, target_metric) → Level 2 fires ~6–10 times inside Level 1 Execute (some fields need re-asks) → Level 1 Review interrupt fires only when Level 2 completes for all six.

   **What this replaces in the current codebase:** the monolithic coaching loop where field capture, re-asking, and completeness checking are all fused inside a single prompt — the Gap 10 "planning implicit in prompts" problem §5 diagnoses.

---

### New Section (proposed, position TBD) — AzureBlobStore and Multi-Chain Persistence

**Rationale:** §52 establishes the Checkpointer + BaseStore split as concept. Nothing in the file applies it concretely to Agent Improve. This is a required addition for the refactor.

**Content to draft:**
- `AzureBlobStore` class design (implements `langgraph.store.base.BaseStore`)
- Namespace convention: `("projects", project_id, <kind>)`
- Compile-time wiring: `graph.compile(checkpointer=..., store=...)`
- Runtime pattern for DMAIC phase chains (Define→Measure→Analyse→Improve→Control)
- Ordering constraint: implement AFTER Step 6 (thread_id wired through `graph.ainvoke`), since store is meaningless without functional checkpoint persistence first

**Verified against current LangGraph docs** (2026-07 web check):
- BaseStore interface: `put`, `get`, `search`, `delete` methods with tuple namespaces
- Store injected into nodes via `get_store()` or function argument
- LangChain docs explicitly recommend Store for cross-subgraph data — matches our Define→Measure boundary case exactly

**Position:** Recommend inserting immediately after §52 (or as §52a), so the general finding and its Agent Improve application are adjacent.

---

### §20 — Supervisor / Worker Architecture — Implementation

**Change:** Section 20 as written presents a flat two-level supervisor/worker model that contradicts §5 (Two-Level Cascade), §11 (Phase Planner and Phase Executor), and §17 (Recursive Orchestrator Pattern). Reframe around the recursive **Planner-Executor pair** already established in §5, extending it to explicit three levels.

**Nature of the contradiction:**
- §20 states supervisors have NO tools and workers perform a SINGLE well-defined function.
- §5 and §11 describe a Planner + Executor pair at each supervisory level (Global Planner + Global Executor, then Phase Planner + Phase Executor).
- §17 names the pattern "recursive."
- Flat supervisor/worker cannot express a phase-level agent that plans coaching strategy AND has its own executor dispatching to leaf tools.

**Correct model — Planner-Executor pair recursively applied, three levels for Agent Improve:**

| Level | Planner (reasons) | Executor (dispatches) | Leaf |
|---|---|---|---|
| 1 — Global | Global Planner: which phase, are gates passed, what's missing | Global Executor: routes to phase subagent | — |
| 2 — Phase | Phase Planner: coaching strategy, which field, which action | Phase Executor: routes to leaf tools per plan step | — |
| 3 — Leaf | — | — | extraction, RAG lookup, gate validator, coaching LLM, policy advisory |

**Recursion rule:** at every non-leaf level, the pattern is (Planner reasons, Executor dispatches). The Executor's targets can themselves be Planner-Executor pairs. Only at the leaf level do you find single-function tools.

**Implementation implications:**
- Planners run on `operational-premium` (gpt-4o) — reasoning-heavy structured decisions
- Executors are routing mechanisms — LangGraph nodes or router functions, not necessarily LLMs
- Leaf tools use `operational-model` (gpt-4o-mini) or are pure functions
- The Planner/Executor split matters for cost, observability, and testing — fusing them loses the boundary

**Section 20 rewrite:**

Replace the "Supervisor responsibilities" / "Worker agent design principles" flat lists with:

*The pattern is a Planner-Executor pair applied recursively. At every non-leaf level, a Planner reasons and produces a structured plan; an Executor consumes that plan and dispatches to the next level. At the innermost level, workers are single-function tools. The Planner and Executor are distinct components — never fused. The Executor's targets can themselves be Planner-Executor pairs, which is what makes the pattern recursive.*

**Universal anti-patterns (revised — apply at every level):**
- Executors reasoning (they dispatch, they don't decide)
- Planners dispatching directly to leaves (they produce plans; the Executor at their level consumes them)
- Leaves influencing control flow (leaves return results; the Executor at their level routes)
- Overlapping responsibilities between two Planners at the same level
- Unstructured or ambiguous plan objects between a Planner and its Executor

**Implementation Pattern code blocks:**

The `make_supervisor_node` / `make_worker_node` factory functions from the course lab are useful **as Level 1 primitives** (Global Planner + Global Executor pattern) and **as leaf-level worker wrappers.** They do not describe Level 2 phase subagents, which need the full Planner + Executor decomposition from §5 and §11.

Add a subsection: "Level 2 Phase Structure — see §5, §11, and §19 Nested Cycle."

**State schema:**

The course's minimal `SupervisorState(MessagesState) { next: str }` is a Level 1 pattern. Agent Improve's SupervisorState (per §17 update) is richer — `dmaic_plan`, `phase_index`, `current_phase`. Level 2 PhaseState (per §18 update) contains `coaching_plan`, `field_index`, and its own state. Note both explicitly in §20 so future readers see the level-by-level state distinction.

**Correction record:** an earlier draft of this decision proposed "phase subagent is simultaneously worker and supervisor." That framing was rejected because it collapsed the Planner/Executor split that §5 already establishes correctly. Current framing preserves the split.

---

### §21 — Message Passing Across Agent Nodes

**Changes:**

1. **PipelineState field types.** `draft: str` and `feedback: str` are the same teaching simplification as §19 ChainState. For Agent Improve these are structured `dict[str, Any]`, matching the §18 PhaseState update. The line `# final comes from messages` is worse than a simplification — it makes downstream consumers parse prose from message history, which is the Gap 10 anti-pattern. Replace with a structured `final` field.

   **Replacement PipelineState:**
   ```python
   class PipelineState(MessagesState):
       draft:    dict[str, Any]    # generator's structured output
       feedback: dict[str, Any]    # reviewer's structured critique
       final:    dict[str, Any]    # refiner's structured result
   ```

2. **AgentLean Application paragraph — rewrite for scope correctness.**

   Current text: *"Define writes its gate document to both `captured_fields["define"]` (for Measure to access directly) and to messages (for audit trail). Measure reads from `captured_fields["define"]`, not from message history."*

   This contradicts §17 (captured_fields removed from SupervisorState) and the new AzureBlobStore section (between-phase handoff via store). The dual-storage principle is correct but misscoped: it describes within-chain handoff, not between-chain.

   **Replacement paragraph (draft):**

   *This is the pattern for within-chain handoff — nodes inside a single phase subgraph passing structured results to each other. Inside the Define subgraph, the extraction node writes to both `state["draft"]` (structured, for the next node) and messages (for audit). The gate-review node reads `state["draft"]`, not message history.*

   *Between-chain handoff — Define → Measure, Measure → Analyse, etc. — uses a different mechanism: the store, not a state field. When Define's gate is approved, its artifacts are written via `store.put(("projects", project_id, "artifacts"), "define", {...})`. Measure's input mapper reads them via `store.get(...)`. See §19 (Multi-Step Task Chaining) and the AzureBlobStore section (after §52).*

3. **Section title / opening — clarify handoff channel.**

   The title "Message Passing Across Agent Nodes" is misleading — the primary channel in the dual-storage pattern is a dedicated state field, not messages. Either rename to "State Passing Across Agent Nodes" or open with an explicit clarification:

   *Despite the section name, the primary handoff channel in this pattern is a dedicated state field. Messages provide the audit trail, not the primary channel. Downstream nodes read structured state, never parse prose from message history.*

4. **Dual Storage Pattern code block — keep, with structured types.**

   The principle is correct. Update the code example so `draft_content` is a `dict[str, Any]`, not an implicit string.

   ```python
   # Generator writes to both — structured state field + audit message
   return {
       "draft": {"problem_statement": "...", "baseline_metric": "..."},   # structured for downstream
       "messages": [
           AIMessage(
               content=json.dumps(draft, indent=2),  # or a human-readable summary
               name="generator"
           )
       ]
   }
   
   # Reviewer reads structured field directly — never parses prose
   reviewer_input = state.get("draft", {})
   ```

5. **Safe State Access Pattern — keep as-is.**

   The `.get()` with default pattern is a valid defensive-coding rule regardless of type. No change needed.

---

### §23 — Modular Subgraph Architecture

**Change:** Section is architecturally correct — the LangGraph subgraph mechanism it describes is the right pattern for Agent Improve. Only the AgentLean Application paragraph needs updating to reconcile with §17 (SupervisorState slimdown) and the AzureBlobStore section.

**Verified against LangGraph docs (2026-07):**
- Subgraphs embedded in a parent graph share the parent's thread_id
- Each subgraph gets its own auto-managed checkpoint_ns
- LangGraph 1.2.6 fixed a regression where nested subgraphs weren't inheriting parent checkpoint_ns — confirms the intended pattern
- LangChain docs explicitly recommend the Store for cross-subgraph data: *"Use shared state via Store for data that needs to cross graph boundaries"*

**Sections it correctly aligns with:**
- §5 (Two-Level Cascade) — subgraphs implement the phase-level boundary
- §17 (SupervisorState) — parent state holds orchestration; subgraph state holds phase-internal detail
- §18 (PhaseState) — the subgraph's internal state schema
- §20 (Planner-Executor recursion) — each subgraph internally contains a Planner-Executor pair

**AgentLean Application paragraph — rewrite:**

Current text refers only to subgraph embedding. Expand to state the full pattern:

*Each DMAIC phase subagent IS a subgraph embedded as a node in the supervisor parent graph. The parent graph has one thread_id per project (e.g. `IMPR-2026-FS1`); each subgraph — Define, Measure, Analyse, Improve, Control — has its own auto-managed checkpoint_ns (LangGraph handles this).*

*The subgraph's internal state (`DefineState`, `MeasureState`, ...) is the PhaseState schema from §18. The parent's `SupervisorState` (§17) never sees the subgraph's coaching turns, tool calls, or extraction attempts — only the structured output at exit.*

*Cross-phase artifacts do NOT flow through the parent's state (that's why §17 removed `captured_fields` from SupervisorState). They flow through the AzureBlobStore, because LangGraph subgraph state does not automatically propagate to the parent's visibility. See the AzureBlobStore section (after §52) for the mechanism.*

*The Define subgraph's internal structure is **not** a straight pipeline (unlike §23's `researcher → summarizer` example — that shows the mechanism but is too simple to represent a DMAIC phase). The Define subgraph has ~5 nodes — planner, executor, gate_review (interrupt), policy_advisory, revise — connected by **conditional edges** and **cycles**. The graph structure is fixed at compile time; routing is dynamic based on state. The planner fires many times per phase, not once: after each executor step, control returns to the planner to decide whether to continue coaching the current field, move to the next field, or trigger the gate.*

*Leaf tools — extraction, RAG lookup, gate validator, policy advisory — are **not** separate subgraph nodes. They are tools bound to the executor node via `bind_tools()`. This is the tool-calling coach agent pattern from ARCHITECTURE.md §B2. From the subgraph's perspective the executor is one node; from inside that node, multiple tools can fire per invocation.*

**No structural changes to the rest of the section** — the Evolution diagram, Composable Subgraph Characteristics, Implementation Pattern, Communication Between Parent and Subgraph, and Naming Convention subsections are all correct.

---

### New Section (proposed, position TBD) — Terminology Reference

**Rationale:** The file uses "agent," "subagent," "node," "subgraph," and "tool" across multiple sections without a single authoritative definition. §5, §11, §17, §18, §20, §23 all use these terms slightly differently. This causes real confusion (surfaced during review — user asked for clarification because the file itself is inconsistent).

**Proposed placement:** Very early in the file, immediately after the "Overview Architecture" block and before §1. Reason: readers need this vocabulary before encountering §1 or later. Alternatively, a Group A prefix section.

**Content to draft:**

*Structural primitives (from LangGraph):*
- **Node** — a Python function in a `StateGraph`. Reads state, does work, returns updates. Atomic unit of execution.
- **Subgraph** — a compiled `StateGraph` embedded as a node in a parent graph. Has its own state schema and internal nodes; the parent sees only its input and output.
- **Tool** — a Python function bound to an LLM via `bind_tools()`. Not a node — invoked from inside a node.

*Role labels applied to those primitives:*
- **Planner** — a node whose responsibility is producing a structured plan (typically an LLM call).
- **Executor** — a node whose responsibility is consuming a plan and dispatching. At Level 1, dispatches to subgraphs via conditional edges. At Level 2, dispatches to tools via the tool-calling loop.
- **Supervisor** — the Level 1 pair (Global Planner + Global Executor) at the top of the hierarchy.
- **Phase subagent** — a subgraph at Level 2 (Define, Measure, Analyse, Improve, Control). Contains its own Planner and Executor nodes.
- **Leaf tools** — the tools bound to a Level 2 executor. Not planner-executor pairs — plain functions.

*The recursion is two-level, not infinite:*

| Level | Planner | Executor | Dispatches to | Mechanism |
|---|---|---|---|---|
| 1 | global_planner (LLM) | global_executor (router) | Phase subgraphs | LangGraph conditional edges |
| 2 | phase_planner (LLM) | phase_executor (LLM+bind_tools) | Leaf tools | tool-calling loop inside node |
| 3 | — | — | — | tools are functions, not P-E pairs |

*"Agent" — used carefully:*
- LangChain classic sense: an LLM with bound tools that decides which tool to call. In our code, this is the Level 2 `phase_executor` node.
- Multi-agent sense: a named role (supervisor, subagent, worker). In our code, "phase subagent" = the Level 2 subgraph as a whole.

*Terms cross-referenced to sections:*
- Node, subgraph, tool → §23 (mechanism), this section (definition)
- Planner-Executor pair, recursion → §5, §11, §20
- Phase subagent, PhaseState → §17, §18, §23
- Tool-calling coach agent → ARCHITECTURE.md §B2 (external reference)

**Sections requiring cross-links back to this reference:**
- §5 opening — cross-link "for terminology, see the reference section"
- §17, §18 — same cross-link
- §20 — same cross-link
- §23 — same cross-link, plus explicit note that "subagent" in the AgentLean Application paragraph means "subgraph"

---

### §27 — LCEL Pipelines — Why We Never Used Them

**Change:** Substantial rewrite. The section correctly identifies LCEL's value but wrongly scopes where it applies. Reframe as node-internal composition tool, not phase-executor replacement.

**Nature of the problem:**

Section's key example (lines showing `measure_chain = prompt | llm | StrOutputParser | extraction | completeness_check`) treats the entire phase executor as one linear LCEL chain. This encodes the pre-subagent monolithic pattern where extraction and completeness checking are fixed pipeline steps. In the current architecture (§17, §18, §23), the phase executor is a **node** inside a 5-node subgraph, with extraction and completeness check as **tools bound to that node** — invoked dynamically by the LLM via `bind_tools`, not chained deterministically via `|`.

Additionally, the `StrOutputParser` pattern is superseded by LangChain 1.0 ProviderStrategy (§82) — native structured output via `llm.with_structured_output(YourSchema)` eliminates the parse-then-validate step.

**What to keep from §27:**

- **The Why Pipelines Matter table** — composability, streaming, batch processing, observability, error handling benefits are real for LCEL used at the right scope.
- **The Two Levels framing** at the bottom — LangGraph = orchestration (which agents when, state, routing), LCEL = internal composition inside nodes (prompt → LLM → parse), LangChain = primitives both are built from. Metaphor "orchestrator is the traffic controller, pipelines are the engine inside each vehicle" is good — keep it.
- The observation that current code chains LLM calls manually — this is still true and still worth improving.

**What to change in §27:**

1. **Remove the "Where Pipelines Belong" measure_chain example** or replace it with a **node-internal example**:

   ```python
   # Inside the planner node — LCEL for prompt construction + structured output
   planner_chain = (
       planner_prompt_template
       | llm.with_structured_output(CoachingPlanSchema)   # §82 ProviderStrategy
   )
   plan = await planner_chain.ainvoke({"state": state})

   # Inside the policy_advisory node — LCEL for validation
   advisory_chain = (
       build_validation_prompt(state)
       | llm.with_structured_output(AdvisorySchema)
   )
   ```

2. **Add explicit scope statement:**

   *LCEL is used **inside individual nodes** for prompt construction, structured output, and deterministic post-processing chains. It does NOT replace the LangGraph node or subgraph structure. The phase executor node, in particular, uses `bind_tools` for dynamic tool invocation — that dispatch cannot be expressed as an LCEL chain because the LLM decides at runtime which tool to call.*

3. **Add cross-references** to §17, §18, §23 (subgraph architecture), §82 (ProviderStrategy supersedes StrOutputParser pattern), Terminology Reference (LCEL is a composition tool, not a level in the hierarchy).

4. **Update the "Current approach — manual chaining" example.** The example is fine as a starting point but should say "the fix is to move each step into the appropriate node in the subgraph, using LCEL inside those nodes for the deterministic parts, and `bind_tools` for the dynamic parts."

5. **Retire the "extraction_runnable" and "completeness_check_runnable" as pipeline steps.** These are tools now, not runnables in an executor chain.

**Why this matters — cascading impact:**

§27 is one of the first sections a reader hits when trying to understand how AgentLean should compose LLM calls. If left as-is, a Claude Code instance or future reader would build the executor as one big LCEL chain, which contradicts §17/§18/§23/§82 and undoes the tool-calling coach agent pattern (ARCHITECTURE.md §B2). This is exactly the drift risk we're seeing repeatedly — the file has correct pieces but earlier sections encode superseded patterns.

---

### §29 — OutputFixingParser

**Change:** Substantive rewrite. Similar treatment to §27 — the section is not wrong for its era but is superseded by LangChain 1.x native structured output.

**Web-verified (2026-07):**
- `OutputFixingParser` moved to `langchain-classic` (compat path, v1.3.4)
- Main `langchain` v1.x exposes native structured output strategies (`ToolStrategy`, `ProviderStrategy`, `NativeStrategy`, `AutoStrategy`) via `llm.with_structured_output(Schema)` or `bind_tools`
- GitHub issue #34098 (Nov 2025) is an open feature request asking for OutputFixingParser to come back to core — confirms it's no longer on the recommended path
- Sources: `python.langchain.com/api_reference/langchain/output_parsers/langchain.output_parsers.fix.OutputFixingParser`; `reference.langchain.com/python/langchain-classic/output_parsers`; GitHub issue #34098

**Fate of the "Three-Layer Defence" model:**

| §29 layer | Status |
|---|---|
| OutputFixingParser | Obsolete — ProviderStrategy (§82) guarantees valid schema output at API level |
| Pydantic validation | Subsumed by ProviderStrategy — schema IS the Pydantic model passed to `with_structured_output` |
| Completeness check | Still relevant — content-level concern, lives as bound tool or conditional edge |

Only the third layer survives, and it lives distributed across the 5-node subgraph, not as a linear pipeline.

**Where each concern lives in the 5-node subgraph:**

- Format validation → inside `extract_field` tool via `llm.with_structured_output(FieldSchema)`. No separate parser needed.
- Schema validation → same location, same mechanism. Native to ProviderStrategy.
- Completeness check → bound tool `check_completeness(captured_fields, phase)` invoked by the executor, OR a conditional edge on the subgraph checking `len(captured_fields) < required_count`.
- Content-level hallucination guard → NOT addressed by §29. Requires: (a) explicit anti-hallucination guards in the executor's prompt (per userMemories requirement), (b) cross-checking against raw conversation, (c) the policy advisory node from §2 reviewing extracted values before Belt approval.
- Retry on failure → LangChain 1.x has `RetryMiddleware` (auto-retry failed tool calls with configurable backoff) for invisible retry; §48 Reflection node pattern for graph-visible retry.

**Rewrite plan:**

1. **Keep the historical framing** — present §29 as "the pre-1.0 pattern for parse-then-validate." Useful for context but not the recommended approach.

2. **Retire the OutputFixingParser recommendation.** Replace with a direct pointer to §82 (ProviderStrategy) for format/schema and to the distributed pattern above for content.

3. **Retire the "Three-Layer Defence" table.** Replace with a "how the concerns are distributed in the subgraph" section listing where each concern lives.

4. **Preserve the Reflection Node vs OutputFixingParser comparison table** — this is a good conceptual framing. Update to say Reflection Node (§48) is the current pattern for visible retry; OutputFixingParser is legacy.

5. **Cross-links to add:**
   - §2 (policy advisory)
   - §48 (Reflection Nodes)
   - §51 (InsightForge Self-Correcting Pipeline — pending own review for possible superseding)
   - §82 (LangChain 1.0 ProviderStrategy)
   - Terminology Reference (tools bound to executor, not layers in a chain)

**Anti-hallucination note (orthogonal):**

Neither OutputFixingParser nor ProviderStrategy addresses content-level hallucination. That requires prompt guards (per userMemories: "LLM must never hallucinate field values from coaching templates — explicit anti-hallucination guards are required in all ORCHESTRATOR prompts") and post-hoc validation via policy advisory. §29's rewrite must state this explicitly so no reader assumes structured output is sufficient defence against hallucinated content.

**Sections to review together with §29:**

Category C (Reasoning, Reflection, and Correction) includes §28, §29, §42, §48, §51, §54, §68, §69, §71. Several of these (§48, §51 specifically) directly overlap with §29's subject matter and need to be reviewed as a group before batch commit. Deferred to next Category C sweep.

---

### §32 — Multi-Query Retrieval — RATIFIED REWRITE

**Status:** Full replacement text ratified this review session. Batch commit will replace the current §32 body with the draft below. Two open points at the bottom — final priority statement and confirmation of `azure_search_retriever` import shape — deferred to batch commit.

**Ratified this session:**
1. Implementation approach — **tool-inside-executor pattern**, not the deprecated `MultiQueryRetriever` class. Explicit and non-negotiable. All references to the class removed from §32; replaced with the `rag_lookup` tool spec above.
2. Gap 15 priority — **promote to v2.1 refactor scope, explicit**. The deferral rationale ("wait for post-completion refactor") is inverted now that active refactor is in progress. §32 rewrite text updated below to state this definitively.

**Web-verified (2026-07):**
- `MultiQueryRetriever` moved to `langchain-classic` in LangChain 1.0 (October 2025). Source: `docs.langchain.com/oss/python/migrate/langchain-v1`
- The class is deprecated even in langchain-classic. Source: `reference.langchain.com/python/langchain-classic/retrievers/multi_query`

**Full replacement text for §32:**

```markdown
## 32. Multi-Query Retrieval

*Source: Edureka Course 2 — Retrieval, Fusion Techniques, and Multi-Hop Reasoning. Updated for LangChain 1.x — see verification note below.*

### What It Is
Enhances document retrieval by generating multiple alternative phrasings of a single query, running them in parallel against the retriever, then merging and deduplicating results. Broader concept coverage than a single query formulation.

### The Problem It Solves
A single query often misses relevant documents because the wording doesn't match how content was indexed:

Single query: "agent error rate"
Misses:       "representative performance", "call handling quality", "AHT metrics"

Multi-query generates alternatives that all hit the same retriever, results merged and deduplicated.

### What Agent Improve Already Has
Azure AI Search with `improve_knowledge_index` implements hybrid retrieval — BM25 (keyword-based lexical search) combined with vector search (semantic similarity). More sophisticated than a pure vector retriever; partially addresses vocabulary mismatch. Remaining gap: sending one query formulation to an already good hybrid retriever, when several formulations would broaden concept coverage.

### Where This Belongs in the Architecture
Multi-query is implemented inside the `rag_lookup` tool — one of the leaf tools bound to each phase executor node (see §23, Terminology Reference). Not a separate node in the subgraph, not a wrapper class around the retriever. From the executor's perspective, `rag_lookup(query, phase)` returns documents; the multi-query behaviour is encapsulated inside the tool.

Applies to all DMAIC phases, not just Analyse. Every phase has vocabulary fan-out in the LSS Black Belt eBook — Define (problem statement / voice of customer / opportunity statement), Measure (baseline metric / current state performance / as-is measurement), Analyse (root cause / fishbone / Ishikawa / 5 Why), Improve (improvement hypothesis / counter-measure / solution design), Control (control plan / sustainability / process governance). The `phase` argument shapes the variant generation prompt so the tool serves all five phases uniformly.

### Reference Implementation (LangChain 1.x)

    from langchain_core.tools import tool
    from langchain_core.documents import Document
    from pydantic import BaseModel

    class QueryVariants(BaseModel):
        queries: list[str]

    @tool
    def rag_lookup(query: str, phase: str) -> list[Document]:
        """Multi-query RAG lookup against improve_knowledge_index.
        Applies to all DMAIC phases (Define, Measure, Analyse, Improve, Control).
        Variant generation is shaped by the `phase` argument."""
        variants = llm.with_structured_output(QueryVariants).invoke(
            f"Generate 3-5 alternative phrasings for retrieving DMAIC {phase} "
            f"content on: {query}. Include synonyms, related terminology, and "
            f"phrasings a Black Belt would use in the LSS Black Belt eBook."
        )
        docs: list[Document] = []
        for q in variants.queries:
            docs.extend(azure_search_retriever.invoke(q))
        return deduplicate_by_id(docs)

Variant generation uses `llm.with_structured_output(QueryVariants)` — LangChain 1.x native structured output (see §82 ProviderStrategy). No manual JSON parsing, no OutputFixingParser (deprecated — see §29).

### What This Section Used to Recommend, and Why That's Wrong Now
The original version recommended `MultiQueryRetriever.from_llm(...)` from `langchain.retrievers.multi_query`. In LangChain 1.x invalid on two counts: the import moved (LangChain 1.0 October 2025 namespace split — `MultiQueryRetriever` and everything else from `langchain.retrievers` moved to `langchain-classic`; old import raises ImportError); and the class is deprecated even in langchain-classic. Rather than depend on a deprecated class, implement the pattern inside the `rag_lookup` tool. Current LangChain 1.x idiom: build patterns from `create_agent`, `bind_tools`, `with_structured_output`, and middleware — not legacy wrapper classes.

Verification: `docs.langchain.com/oss/python/migrate/langchain-v1`; `reference.langchain.com/python/langchain-classic/retrievers/multi_query`. Web-verified July 2026.

### Interaction With Related Retrieval Patterns
- §33 RAG Fusion — reciprocal rank fusion for scoring merged multi-query results. Compatible; can be added inside `rag_lookup` if simple deduplication proves insufficient.
- §34 Multi-Hop Reasoning / §71 Multi-Hop Retrieval (Gap 17 CLOSED) — sequential retrieval where each retrieval informs the next. Different concept, complementary. Multi-query broadens; multi-hop deepens. Both can coexist in `rag_lookup` or as separate tools.
- §35 Query Voting and Weighted Fusion — same cluster; consider together during batch review.

### Gap Register
Gap 15 — single-query formulation only against an already good hybrid retriever. Self-contained tool-level improvement, implemented inside the `rag_lookup` tool (see Reference Implementation). **Included in v2.1 refactor scope.** The previous "deferred to post-completion refactor" rationale is inverted now that active refactor is in progress and the change is a tool-level addition with no architectural risk.
```

**Open questions to resolve before batch commit:**
1. Confirm `azure_search_retriever` module-level exposure in current codebase (or adjust reference implementation).

---

### §33 — RAG Fusion

**Change:** Light rewrite. Section's technical description is fine. Priority statement and Gap Register need updating; the deferral rationale in §33 is superseded by empirical evidence.

**Ratified this session — RRF INCLUDED in v2.1 `rag_lookup` by default (Option 1).**

**Empirical rationale (from user, this session):**

Agent Resolve production experience shows Azure AI Search's ranking is unreliable — the retriever was not capable of ranking properly, and with only one search query it was not even reliably returning the right matches. Since Agent Improve uses the same underlying tech (Azure AI Search hybrid on `improve_knowledge_index`), §33's assumption that "Azure AI Search already does sophisticated hybrid ranking internally" is empirically false for the LSS Black Belt eBook corpus and coaching use case. This overrides §33's theoretical "diminishing returns" assessment.

**Why RRF specifically helps this failure mode:**

RRF operationalises cross-variant consistency. When multiple query variants all return the same document at moderate ranks, that document is more likely genuinely relevant than a document appearing once at the top of one variant. Native Azure AI Search ranking is single-query — it cannot do this consistency check because it doesn't know about the variants. RRF is the layer that combines the variant-level ranking signal into a corpus-level relevance signal.

**Ratified `rag_lookup` reference implementation (supersedes §32 draft):**

```python
from langchain_core.tools import tool
from langchain_core.documents import Document
from pydantic import BaseModel


class QueryVariants(BaseModel):
    queries: list[str]


def reciprocal_rank_fusion(
    ranked_lists: list[list[Document]],
    k: int = 60
) -> list[tuple[Document, float]]:
    """Standard RRF: score each doc as sum of 1/(k+rank) across variant results.
    Documents consistently ranked across variants score higher than one-off hits."""
    scores: dict[str, float] = {}
    docs: dict[str, Document] = {}
    for ranked_list in ranked_lists:
        for rank, doc in enumerate(ranked_list, start=1):
            doc_id = doc.metadata["id"]
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            docs[doc_id] = doc
    return sorted(
        [(docs[doc_id], score) for doc_id, score in scores.items()],
        key=lambda pair: pair[1],
        reverse=True,
    )


@tool
def rag_lookup(query: str, phase: str, top_k: int = 10) -> list[Document]:
    """Multi-query RAG lookup with Reciprocal Rank Fusion, against
    improve_knowledge_index. Applies to all DMAIC phases."""
    variants = llm.with_structured_output(QueryVariants).invoke(
        f"Generate 3-5 alternative phrasings for retrieving DMAIC {phase} "
        f"content on: {query}. Include synonyms, related terminology, and "
        f"phrasings a Black Belt would use in the LSS Black Belt eBook."
    )
    ranked_lists = [
        azure_search_retriever.invoke(q) for q in variants.queries
    ]
    fused = reciprocal_rank_fusion(ranked_lists, k=60)
    return [doc for doc, _score in fused[:top_k]]
```

RRF is ~15 lines; needs no LangChain class or third-party dependency. Same algorithm across framework versions.

**Impact on §32 ratified rewrite:**

The §32 ratified rewrite (recorded above in this log) contained a multi-query-only version of `rag_lookup`. That earlier version is now superseded — the batch commit for both §32 and §33 must use the RRF-included implementation shown here. To avoid two versions of the code drifting, mark this the canonical version and cross-reference from §32.

**§33 section rewrite:**

1. **Keep the 5-step workflow explanation.** Correct and useful.
2. **Keep the RRF explanation and the "cross-result consistency" framing.** Good pedagogy.
3. **Retire the "diminishing returns" priority note.** Replace with an "Empirical override" note stating that Agent Resolve production experience showed native Azure AI Search ranking unreliable for LSS Black Belt content, so RRF is included in v2.1 by default.
4. **Update the Agent Improve Gap Assessment table** to reflect v2.1 target state — all steps implemented.
5. **Update Gap Register.** Currently: "Gap 16 — deferred to post-completion refactor." Replace with:

   *Gap 16 — RRF re-ranking. **Included in v2.1 refactor scope**, integrated with Gap 15 (multi-query) in the `rag_lookup` tool. Empirical evidence from Agent Resolve retrieval quality overrode the earlier "diminishing returns" deferral.*

6. **Cross-references to add:** §32 (parent tool that houses RRF), §35 (query voting and weighted fusion — same cluster), §82 (structured output for variant generation), Terminology Reference (RRF lives inside a tool, not as a subgraph node or wrapper class).

---

## Housekeeping — Project knowledge attachments

**Status: RESOLVED as of this session turn.**

Original discrepancy: project_knowledge_search returned only LSS Black Belt eBook. CLAUDE.md and ARCHITECTURE.md were not indexed in project knowledge despite instructions stating they were.

Resolution: user uploaded both files to `/mnt/user-data/uploads/` on 2026-07-05.
- CLAUDE.md v2.1 (June 2026) — 17KB
- ARCHITECTURE.md v2.1.1 (June 2026) — 20KB

Both are point-in-time snapshots and go stale as commits land in `vpangalis/agentlean`. When citing, note version. If user references a decision not in the attached version, ask them to paste the current relevant section.

**Retroactive check needed:** all references in this log to "ARCHITECTURE.md §B2", "CLAUDE.md §4.3", "CLAUDE.md §4.6" (non-existent), etc. should be verified against the now-attached files during batch commit. If any reference is inaccurate against the actual documents, correct it. Highest-priority sections to check:
- §2 policy advisory referencing ARCHITECTURE.md §5.1 for `validate_phase_gate` tool
- §23 AgentLean Application referencing ARCHITECTURE.md §B2 for tool-calling coach agent
- §27, §29 referencing CLAUDE.md §4.3 for structured output mandate
- Section 86 authoring (Path A) needs CLAUDE.md §4.3 / drift hook / §4.6 reconciliation — now readable

---

### §34 — Multi-Hop Reasoning

**Status:** REOPENED then RATIFIED with hop cap this session. Earlier "ratified" entry was rescinded on user pushback; this replacement is the current locked decision.

**Ratified this session:**

1. **Multi-hop reasoning IS relevant to Agent Improve.** DMAIC coaching questions are inherently multi-hop (§34's sigma/training/6-week example is representative). Web-verified 2026 as core Agentic RAG pattern (MarsDevs 2026 Production Guide, LangChain react-agent template). No separate infrastructure needed — the capability lives in the coach node's ReAct tool-calling loop per ARCHITECTURE.md v2.1.1 §3.2.

2. **Cap: 5 tool calls per Belt turn** (i.e., per coach node invocation). Beyond 5, the LLM is usually lost or looping — cutting it off is correct.

3. **LangGraph implementation:**
   - Mechanism: `recursion_limit` config parameter, not `max_hops`
   - LangGraph counts steps, not hops. Each hop = 2 steps (LLM node → tool node) + 1 final LLM step for synthesis
   - Mapping: `recursion_limit = 2 * max_hops + 1 = 11` for 5 hops
   - Set via: `graph.invoke(state, config={"recursion_limit": 11, "configurable": {"thread_id": project_id}})`
   - Verified: `python.langchain.com/docs/modules/agents/how_to/max_iterations`

4. **Error handling requirement:** Coach node must catch `GraphRecursionError` and return a partial answer to the Belt rather than crash. Verified: `docs.langchain.com/oss/python/langgraph/errors/GRAPH_RECURSION_LIMIT`. Small piece of node-level error handling, but must exist.

5. **Cost mitigations ratified for v2.1** (from earlier turn, retained):
   - Cap the hops (5) — implemented as above
   - Tier the model — intermediate hops on `operational-model` (gpt-4o-mini), final synthesis on `operational-premium` (gpt-4o). Substantial cost lever — gpt-4o-mini is ~15x cheaper.
   - Adaptive routing — simple queries don't need multi-hop
   - Session-scoped caching for repeat retrievals
   - Better single-hop (§32/§33 multi-query + RRF) reduces the need for many hops

**Section 34 rewrite plan:**

1. Keep the pedagogy (what multi-hop is, DMAIC example, TAO connection). Valuable.
2. Retire the "missing infrastructure" framing. Multi-hop lives in the ReAct coach loop already ratified in ARCHITECTURE.md §3.2.
3. Retire the "prerequisite Gap 15" claim. Multi-hop and multi-query are independent.
4. Retire "deferred to post-completion refactor." Included in v2.1 via the ReAct coach.
5. Add: hop cap (5 tool calls per Belt turn), `recursion_limit=11` config, GraphRecursionError handling.
6. Add: cost mitigations (model tiering, adaptive routing, caching).
7. Cross-references: ARCHITECTURE.md §3.2 (coach as ReAct agent), §32/§33 (better single-hop reduces need for many hops), §71 (which the file index claims closes Gap 17 — reconcile during batch commit).

**Section 34 in a sentence:** Multi-hop is what the coach node does when its ReAct loop makes multiple `rag_lookup_methodology` or `rag_lookup_evidence` calls in one Belt turn, capped at 5 hops via `recursion_limit=11`.

**Cost signal for monitoring:** Hitting the 5-hop cap in production is a signal — either the coach's system prompt is encouraging too-broad exploration (prompt tuning), or the question warrants escalation to `operational-premium` for that turn (model tiering).

**Propagation needed to governance docs at batch commit:**
- CLAUDE.md §7 or elsewhere: document the recursion_limit=11 policy for the coach subgraph
- ARCHITECTURE.md §3.2 or §3.3: same, plus the GraphRecursionError handling requirement

---

### `improve_case_index` — Ratified: Option 2 (add third retrieval tool)

**Rationale — from user, this session:**
Lean/DMAIC methodology explicitly values cross-case learning (yokoten — horizontal deployment). An improvement proven in one plant is expected to be shared across sites; benchmarking against parallel cases is standard DMAIC discipline. Agent Improve exists to coach Belts through DMAIC — withholding cross-case retrieval undermines the platform's own methodology alignment.

My earlier Option 3 recommendation ("minimise tool count") was reversed on domain grounds. Correct outcome, better reasoning: adding this tool serves the platform's core value proposition.

**Tool added to coach's bound tools in v2.1:**

```python
@tool
def rag_lookup_case_history(
    query: str,
    top_k: int = 10,
    exclude_current_case: bool = True,
) -> list[Document]:
    """Semantic search across past Agent Improve cases (all phases, all
    completed gates). Useful for yokoten — finding similar problems, root
    causes, or successful counter-measures from prior projects.
    Excludes the current case by default since its content is available
    directly via the AzureBlobStore."""
```

`exclude_current_case=True` as default prevents redundant retrieval — the current case's structured artifacts are already accessible via the AzureBlobStore per §17/§18/§23 decisions. The flag allows semantic search within the current case if the coach needs it.

**Multi-query + RRF applies here too.** Same mechanism as the other two rag_lookup tools. Yokoten questions specifically benefit — different variants of "problems similar to invoice errors" surface different chunks across cases (AP defects, payment processing errors, reconciliation issues, etc.).

**Coach's bound tools — updated list (v2.1, 8 tools):**

1. `record_field`
2. `rag_lookup_methodology` (renamed from `search_methodology`)
3. `rag_lookup_evidence` (renamed from `search_evidence`)
4. **`rag_lookup_case_history` (new)**
5. `propose_template`
6. `propose_diagram`
7. `check_gate_status`
8. `request_human_approval`

**Propagation needed at batch commit:**

- **EDUCATIONAL.md** — no new dedicated section needed. The tool is mentioned in the §32/§33/§34 rewrites and Terminology Reference alongside the other two rag_lookup tools.
- **CLAUDE.md v2.1** — update §7 (RAG section) to document three retrieval tools instead of two. Add `improve_case_index` to §7's index list (currently only knowledge and evidence).
- **ARCHITECTURE.md v2.1.1** — §3.2 bound tools list expands from 7 to 8. §7 Azure AI Search Indexes table moves `improve_case_index` from "Out of scope for refactor" to "Active" with `rag_lookup_case_history` as the tool.

**Multi-tenant scope note (v2.2 consideration):**

ARCHITECTURE.md v2.1.1 does not address multi-tenancy in the case index. If Agent Improve serves multiple organisations, `rag_lookup_case_history` must filter by tenant/organisation to prevent cross-tenant data leakage. Not a v2.1 blocker (single-tenant assumed), but recorded as a v2.2 consideration so it doesn't get missed. The tool's docstring should include a note for future engineers.

---

### §35 — Query Voting and Weighted Fusion

**Change:** Reduce to knowledge-only comparative section. Keep pedagogy for learners understanding *why* RRF was chosen; strip implementation guidance and broken code examples.

**Ratified this session:** §35 is not needed as a design or implementation section — §33 already ratifies RRF inside `rag_lookup_methodology`, `rag_lookup_evidence`, and `rag_lookup_case_history`. §35 becomes purely comparative pedagogy explaining the three fusion approaches in the literature and why RRF won.

**Rewrite plan:**

1. **Reframe the opening.** State explicitly that the implementation decision is settled in §33; this section exists for comparative understanding.

2. **Keep Simple Voting Fusion explanation and example.** Add a note on its weakness: ignores position within each result set. A document ranked 50th in one variant scores the same as a document ranked 1st. For chunked retrieval where position carries information, this loses signal.

3. **Keep Weighted Fusion concept.** Add a note on its weakness for Agent Improve: presumes the original Belt phrasing is more authoritative than LLM-generated variants — often the opposite. Belts phrase problems in plant vernacular; LLM-generated variants translate to methodology terminology, which is what the LSS Black Belt eBook actually uses. Per-query weighting also introduces a hyperparameter that would require tuning against retrieval quality metrics we don't have yet.

4. **RRF subsection becomes brief.** Formula only, plus a pointer to §33 for the ratified implementation.

5. **Keep the DMAIC "why fusion matters" pedagogy** (root cause / cause-and-effect / hypothesis testing surfacing different chunks). This is genuinely valuable teaching.

6. **Delete the `EnsembleRetriever` and `MultiQueryRetriever` code examples.** Both classes moved to langchain-classic in LangChain 1.0 namespace split (web-verified per §32). Non-functional in current codebase, and shouldn't be presented as guidance.

7. **Delete the Gap Register block.** Gap 18 collapses into Gap 16, which §33 closes. Note in-section: "The fusion gap for Agent Improve was closed by the RRF implementation in §33 (formerly Gap 16). No separate Gap 18."

**Cross-references to add:**
- §32 (multi-query, where fusion is applied)
- §33 (canonical RRF implementation inside the three rag_lookup_* tools)
- Terminology Reference (RRF lives inside tools, not as a separate node or wrapper class)

**One future consideration to record (v2.2+):**

Weighted Fusion becomes plausibly useful in one specific scenario: retrieval strategies from *fundamentally different sources* (e.g., BB eBook methodology + case history + external best-practice databases). In that scenario, weighting *per source* rather than *per query variant* could help balance authority levels. Not a v2.1 concern, but recording so it doesn't get lost if additional retrieval sources are added later.

---

### §36 — Short-Term and Long-Term Vector Memory

**Status:** Fully ratified this session. Section packs four distinct concerns — three ratified, one closes as no-op, one becomes operational hygiene.

**Decision 1 — Vector field name asymmetry: closes as no-op.**

§36's concern presumes a shared retriever mapping field names. Under our ratified 3-tool design (§32/§33 + case-history tool), each tool is bound to one specific index and knows its own vector field name locally. No shared code hides the asymmetry, no runtime normalisation needed. The §36 concern evaporates.

For the rewrite: delete the "Critical Technical Note — Vector Field Name Asymmetry" subsection entirely. Add a one-line note under each tool's docstring specifying which vector field it uses (`content_vector`, `embedding`, and whatever `improve_evidence_index` turns out to use — that field name to be confirmed against the actual index schema before batch commit; not documented in §36).

**Decision 2 — Long-term vector memory analysis: keep as confirming.**

§36's diagnosis that `improve_case_index` with `embedding` + five `phase_summary_*` fields IS the long-term memory mechanism aligns with the ratified Option 2 (`rag_lookup_case_history` tool). No new decision; §36 becomes the pedagogical foundation for the tool's existence.

Suggestion added: the `phase_summary_*` fields are pre-computed per-phase summaries. The `rag_lookup_case_history` tool's docstring should note this so the coach knows the tool can retrieve compact per-phase context, not only raw content chunks. Update the tool signature comment:

```python
"""Semantic search across past Agent Improve cases. Retrieves either
raw content chunks (via `embedding` field) or pre-computed per-phase
summaries (via phase_summary_define, phase_summary_measure, ... fields
on improve_case_index)."""
```

**Decision 3 — Short-term memory / messages[] compression: SummarizationMiddleware + two new typed state fields.**

Web-verified LangChain 1.0 native pattern: `SummarizationMiddleware` in the main package, attached via `middleware=[...]` to `create_agent`. Configuration parameters `trigger`, `keep`, and `model`. Available since v1.0 GA (Oct 2025); v1.1 adds context-aware profiles per model.

Source: `docs.langchain.com/oss/python/langchain/middleware/built-in` — *"Automatically summarize conversation history when approaching token limits, preserving recent messages while compressing older context."*

Also verified: `reference.langchain.com/python/langchain/agents/middleware/summarization/SummarizationMiddleware` — class documentation.

Ratified configuration for Agent Improve:

```python
from langchain.agents.middleware import SummarizationMiddleware

SummarizationMiddleware(
    model="azure/operational-model",       # gpt-4o-mini for cost
    trigger=("tokens", 100_000),           # ~78% of gpt-4o's 128k window
    keep=("messages", 20),                 # preserve last 20 turns raw
)
```

Retire §36's custom `conversation_context` structured-JSON implementation. It reinvents what middleware now provides natively.

Preserve §36's underlying insight — some project state should live in typed structured fields, not in messages[] — but apply it correctly: add two new typed state fields to `SupervisorState`, populated at gate boundaries:

- `key_decisions: list[str]` — explicit decisions made during coaching that don't fit as `captured_fields`
- `open_items: list[str]` — outstanding questions or unresolved threads

Both survive messages[] compression because they never live in messages[].

**Impact on earlier §17 SupervisorState decision — update:**

Add two fields to the ratified SupervisorState schema:

```python
class SupervisorState(TypedDict):
    messages:        Annotated[list[BaseMessage], operator.add]
    history:         Annotated[list[str], operator.add]
    project_id:      str
    project_context: str
    dmaic_plan:      list[dict[str, Any]]
    phase_index:     int
    current_phase:   str
    key_decisions:   Annotated[list[str], operator.add]   # NEW — appended at gate
    open_items:      list[str]                             # NEW — replaced at gate
    final_output:    str
```

`key_decisions` uses append-only reducer (decisions accumulate). `open_items` is replaced at each gate boundary (current outstanding items only).

**Decision 4 — .env file cleanup: operational hygiene, not architectural.**

Recorded as operational note, no v2.1 architectural change:
- Root `.env` should be audited during Claude Code work; remove if redundant to prevent silent shadowing
- Correct variable name is `AZURE_SEARCH_API_KEY` not `AZURE_SEARCH_KEY`
- App loads `agent-improve/.env`; ensure no conflicting root `.env`

This is a Claude Code fix, not a governance-doc update.

**Propagation needed at batch commit:**

- **EDUCATIONAL.md §36 rewrite** — restructure per the four decisions above. Retire vector-field-asymmetry concern. Retire custom conversation_context implementation. Reference `SummarizationMiddleware`. Keep long-term memory analysis. Cross-links to §17 (state schema updates), §33 (RRF in the retrieval tools), Terminology Reference (middleware is a LangChain concept).
- **CLAUDE.md v2.1** — add a new subsection (probably §7.4 or §9) documenting the context compression policy: SummarizationMiddleware configuration + rationale.
- **ARCHITECTURE.md v2.1.1** — add subsection under §3 (agent architecture) describing middleware stack on the coach. Note SummarizationMiddleware as ratified. Add `key_decisions` and `open_items` to the SupervisorState schema documentation.
- **§17 log entry** — reference this decision so no drift between §17's schema and §36's new fields.

**Web-verification citations:**
- `docs.langchain.com/oss/python/langchain/middleware/built-in` — SummarizationMiddleware behaviour
- `reference.langchain.com/python/langchain/agents/middleware/summarization/SummarizationMiddleware` — class reference
- `www.langchain.com/blog/langchain-langgraph-1dot0` — v1.0 GA release notes confirming middleware pattern
- `blog.agentailor.com/posts/is-langchain-worth-it-2026` — 2026 practitioner confirmation of middleware as the standard for context compression

---

### §37 — Memory Patterns in Agentic Systems

**Status:** Ratified this session. Rewrite is taxonomic scaffold + one v2.1 addition; five deferred items migrate to new §87 backlog.

**Ratified decisions:**

1. **Rewrite §37 as purely taxonomic.** Each memory pattern (episodic, semantic, working, vector, retrieval control) described with a cross-reference to where it lives in the ratified architecture. No standalone Gap Register — deferred items move to §87.

2. **Ratified mapping (unchanged from §37's own analysis):**
   - Episodic memory → `improve_case_index` phase_summary_* fields, retrieved via `rag_lookup_case_history` (§32/§33 tool ratifications)
   - Semantic memory → `improve_knowledge_index` (LSS Black Belt eBook), retrieved via `rag_lookup_methodology`
   - Working memory → SummarizationMiddleware + typed state fields (§36 ratification)
   - Vector memory in agent-based systems → deferred to §87
   - Retrieval control → one v2.1 update, three deferred to §87

3. **One v2.1 addition — `phase_relevance` filter in `rag_lookup_methodology`.** The `improve_knowledge_index` has a `phase_relevance` field that isn't used in current queries. Adding a filter clause improves retrieval precision immediately. Update the §32 ratified tool signature:

   ```python
   @tool
   def rag_lookup_methodology(query: str, phase: str, top_k: int = 10) -> list[Document]:
       """Multi-query RAG lookup against improve_knowledge_index (LSS Black Belt eBook).
       Filters by phase_relevance to scope results to the current DMAIC phase."""
       variants = llm.with_structured_output(QueryVariants).invoke(
           f"Generate 3-5 alternative phrasings for retrieving DMAIC {phase} "
           f"content on: {query}. Include synonyms, related terminology, and "
           f"phrasings a Black Belt would use in the LSS Black Belt eBook."
       )
       ranked_lists = [
           azure_search_retriever.invoke(
               q,
               search_kwargs={
                   "filters": f"phase_relevance eq '{phase}' or phase_relevance eq 'all'"
               }
           )
           for q in variants.queries
       ]
       fused = reciprocal_rank_fusion(ranked_lists, k=60)
       return [doc for doc, _score in fused[:top_k]]
   ```

   Filter uses OR with `'all'` so cross-phase content in the eBook is included. Confirm against actual index data before batch commit — the exact enumeration of `phase_relevance` values in the index needs verification.

4. **Impact on §32 log entry:** update the `rag_lookup_methodology` reference implementation to include the filter clause. `rag_lookup_evidence` and `rag_lookup_case_history` don't have equivalent phase-relevance filtering (evidence is filtered by case_id already; case history is inherently cross-phase). Filter is methodology-tool-only.

**Items deferred to §87 from §37:**
- Per-turn episodic entries (gate-level granularity is the ratified choice)
- Mid-phase summary persistence to `improve_case_index`
- LangSmith trace-based coaching learning
- Similarity threshold calibration
- Dynamic top-k based on remaining context

---

### New Section (proposed and ratified) — §87 "v2.2 Deferred Backlog"

**Rationale:** Deferred items evaporate without a tracking home. Per-section Gap Registers scatter the picture; v2.2 planning needs one consolidated place to look. New §87 houses every "defer to v2.2+" decision from this review.

**Structure — each entry has:**
- Source section(s) in EDUCATIONAL.md
- Description of the deferred capability
- Why it was deferred from v2.1
- Prerequisite condition or signal that would promote it to v2.2 scope

**Position:** end of EDUCATIONAL.md, after §86 (Verified Claude Code Hook Mechanics). File ends at §87 in the batch-committed version, with §85 (LangSmith 2026 Additions) preceding §86 as the last "content" section.

**Section count reconciliation:** original file has 85; project instructions say 86 (§86 authoring closes the discrepancy); adding §87 brings total to 87. Project instructions should be updated at batch commit to reflect final section count.

**Backlog items collected so far in this review:**

| # | Source | Deferred capability | Why deferred | Promotion trigger |
|---|---|---|---|---|
| 1 | Case-history tool decision | Multi-tenant filtering on `improve_case_index` | ARCHITECTURE.md v2.1.1 does not address multi-tenancy; assumed single-tenant | Agent Improve deployed to multiple organisations |
| 2 | §35 | Per-source weighting in RAG Fusion | Only useful with fundamentally different retrieval sources; current three tools use same underlying corpus type | Fourth retrieval source introduced (e.g., external best-practice database) |
| 3 | §37 | Per-turn episodic entries in `improve_case_index` | Would multiply case-index writes 30-50×; gate-level granularity is sufficient | Coaching evaluation shows gate-level summaries lose actionable detail |
| 4 | §37 | Mid-phase summary persistence to `improve_case_index` | SummarizationMiddleware keeps compressed summary in messages[] for current session; gate-pass covers durability | Belts frequently resume in-flight cases weeks later and coach needs historical mid-phase context |
| 5 | §37 | LangSmith trace-based coaching learning | Substantial feature; own design phase, evaluation criteria, data schema | Dedicated v2.2 workstream — no signal needed, this is a v2.2 priority feature |
| 6 | §37 | Similarity threshold calibration for retrieval | Requires retrieval-quality metrics not yet in place | §75 evaluation dataset populated with representative queries and expected results |
| 7 | §37 | Dynamic top-k based on remaining context | Requires middleware to expose context-remaining state cleanly | Fixed top-k causes context-budget problems in production |

**Growth pattern:**

§87 accumulates entries as the review continues. Every future section decision that produces a "defer to v2.2+" outcome adds a row. When we reach §26, §44, §45, §50 (governance sections) or the sections between §37 and §85 not yet reviewed, more entries likely appear.

**Propagation needed at batch commit:**
- EDUCATIONAL.md — new §87 authored per template above; §37 rewrite retires its Gap Register items and cross-links to §87 for the deferred five
- Project instructions — section count updated (85 → 87)
- CLAUDE.md — no direct change needed; §87 is an EDUCATIONAL.md concern
- ARCHITECTURE.md — no direct change needed; deferred items are not in v2.1 scope

---

### §38 — Hybrid Memory Stack and Context Orchestration Layer

**Status:** Fully ratified this session. Section rewritten as taxonomic scaffold. Compound "Gap 22" retired and decomposed into three small v2.1 additions.

**Decision 1 — No Context Orchestration Layer as a distinct architectural component.**

§38's four sub-components (memory selection, budget management, memory prioritisation, conflict resolution) plus injection timing and self-correcting queries map differently against our ratified stack than §38 assumes:

| §38 concern | Treatment | Status |
|---|---|---|
| Memory selection | Handled by ReAct + tool descriptions (ARCHITECTURE.md v2.1.1 §3.2) | No action |
| Budget management | Handled by SummarizationMiddleware (§36 ratification) | No action |
| Memory prioritization | System prompt engineering — hierarchy paragraph in coach's system prompt | **v2.1** |
| Conflict resolution — gate-time | Policy advisory (§2 ratification) | No action |
| Conflict resolution — mid-phase | Extend policy advisory to detect captured_field contradictions and fire HITL interrupt | **v2.1** |
| Injection timing | Custom `before_model` middleware to prepend structured project state early | **v2.1** |
| Self-correcting queries (reactive) | Multi-query + RRF is the proactive equivalent (§32/§33) | No action; defer explicit reactive form to §87 if ever needed |

Compound Gap 22 retires. Three small v2.1 additions, each with a clear implementation surface. No monolithic new component.

**Decision 2 — Mid-phase captured_field contradiction: auto-flag, no threshold.**

Rationale from user, this session: in production DMAIC, numbers (baseline mean, sigma level, target metric) are taken very seriously. Silent drift across weeks is exactly the failure mode a coaching system must prevent. HITL forces the human to take responsibility for the change. Threshold-based softening would drift in the wrong direction — "the delta was small enough" is not acceptable when downstream analysis depends on the value.

Aligns with §2's HITL pattern principle: policy advisory offers a second opinion before approval; approval is what commits state. Extended: any change to a previously gate-approved value is treated as a mini-gate, not a silent overwrite.

**Mechanics of the mid-phase conflict check:**

- Fires inside the policy advisory node, before each coach response is returned to the Belt
- Compares Belt's most recent statements (extracted in this turn) against captured_fields already committed at prior gates
- If any numeric or categorical field value differs, coach's response is suppressed and a HITL interrupt payload is emitted
- Payload contains: field name, previously approved value + approval timestamp + gate, proposed new value, two Belt-facing options
- Belt options:
  - "Update the approved value" → the affected phase's gate document becomes provisional, downstream phases need re-review
  - "Keep the approved value" → Belt clarifies they misspoke, no state change
- Small structured diff over `captured_fields` — no LLM call, negligible latency

**Re-approval cascade:** if the Belt confirms the new value, the affected phase and all downstream phases (which depend on it) go back to a provisional state and need re-review. This is heavier than a soft override — and that's the point. Silent invalidation of downstream analysis is not acceptable in a production quality system.

**Section rewrite plan for §38:**

1. Retire the "Context Orchestration Layer as a missing architectural component" framing. Replace with:

   *§38 was originally written as a case for a monolithic Context Orchestration Layer (Gap 22). Under LangChain 1.0 middleware + the ratified ReAct coach + policy advisory pattern, the concerns §38 identifies are addressed by three small additions rather than a new component. This section documents the decomposition.*

2. Keep the "Briefing Document Analogy" — good pedagogy. Reframe as: *this briefing is the emergent behaviour of middleware + ReAct + system prompt discipline working together, not a distinct component.*

3. Keep the injection timing pedagogy (early vs late, LLMs weight earlier prompt content more heavily). Point to the `before_model` middleware as the mechanism.

4. Keep the four Design Trade-offs subsection (Context Depth, Retrieval Cost, Injection Timing, System Complexity). Genuinely useful. Explain how each is managed under the decomposed approach.

5. Add explicit "Mid-phase captured_field contradiction handling" subsection documenting the auto-flag + HITL cascade behaviour. Cross-reference §2 (HITL pattern this extends) and §17 (SupervisorState schema).

6. Retire Gap 22 as compound gap. Replace with three individual Gap Register entries:
   - Gap 22a — Memory prioritization in coach system prompt (v2.1)
   - Gap 22b — `before_model` middleware for early structured state injection (v2.1)
   - Gap 22c — Policy advisory extension for mid-phase captured_field contradictions (v2.1)

7. Self-correcting queries subsection: retain as historical context, note it is subsumed by multi-query + RRF (§32/§33). Reactive re-querying could be added to §87 backlog if a signal emerges that proactive multi-query is insufficient.

**Propagation needed at batch commit:**

- **EDUCATIONAL.md §38 rewrite** — per structure above. Cross-links to §2, §17, §32, §33, §36, §37.
- **EDUCATIONAL.md §2 update** — extend the HITL gate pattern section to note that policy advisory also fires mid-phase on captured_field contradictions, not only at gate boundaries. Small addition.
- **EDUCATIONAL.md §87 backlog** — add reactive self-correcting queries as a deferred item (row 8 in the backlog table).
- **CLAUDE.md v2.1** — add a subsection under coach subgraph documenting:
  - Memory hierarchy paragraph for the coach's system prompt (Decision 1 item 1)
  - The `before_model` middleware in the middleware stack
  - The mid-phase conflict-detection policy advisory extension
- **ARCHITECTURE.md v2.1.1** — coach subgraph diagram (§3.2/§3.3) updated to show:
  - `before_model` middleware on the coach's create_agent call
  - Extended policy_advisory node responsibility (both gate-time and mid-phase)

**Adding to §87 backlog (row 8):**

| # | Source | Deferred capability | Why deferred | Promotion trigger |
|---|---|---|---|---|
| 8 | §38 | Reactive self-correcting query restructuring | Multi-query + RRF is the proactive equivalent (§32/§33); reactive form is redundant unless proactive proves insufficient | Retrieval quality evaluation shows multi-query variants systematically miss even after RRF fusion |

---

### §39 — Knowledge Tools in Augmented Reasoning

**Status:** Fully ratified this session. Two substantial architectural decisions locked in.

**Decision 1 — MCP is explicitly out of scope for Agent Improve, Agent Resolve, and Agent Flow. Not deferred. Never.**

Ratified principle from user, this session: *"agent improve as well as agent resolve that we will refactor after will never use MCP to connect to a live system. Users must upload their data they collect and the agents are responsible to guide the user to what kind of data they should collect and how to collect it."*

Extended reasoning ratified in follow-up: *"the tool decorator does the same thing. The only difference is if I would be working for a large enterprise I would use MCP to share the tools to other agents."*

This is architecturally sound. `@tool` decorator handles single-team, single-stack tool composition natively. MCP adds protocol overhead that only pays off when:
- Multiple teams / organisations share tools across independent codebases
- Language-agnostic tool consumers exist (Python tool, Node.js agent)
- Third-party tool ecosystems require standardised interface
- Enterprise tool registries with governance boundaries are needed

None apply to AgentLean. Same team owns all three agents, all Python, all LangChain 1.x. Cross-agent tool sharing (Agent Improve calling into Agent Resolve's search) happens via Python imports from shared modules, not via MCP protocol.

**Implications:**

*EDUCATIONAL.md §57–65 (nine sections on MCP):* Retain as **pedagogical knowledge**, not roadmap or implementation guidance. Same treatment as §35 (Query Voting/Weighted Fusion) — reduce to knowledge-only, retire any "AgentLean MCP roadmap" claims. §63 "AgentLean MCP Server — Scope and Design Decision" needs particular attention — should be restructured to explicitly document "MCP evaluated and rejected for AgentLean, with rationale" rather than any planning language.

*ARCHITECTURE.md §7 cross-agent tools table:* The `search_resolve_cases`, `search_resolve_knowledge`, `search_resolve_evidence` entries remain — but they are `@tool` functions accessing Agent Resolve's Azure AI Search indexes directly, not MCP servers. Confirm the table's language does not imply MCP; if it does, correct.

*userMemories contradiction:* userMemories list MCP in the AgentLean runtime stack. This is stale and should be updated. Correct stack listing for AgentLean: FastAPI, LangGraph 1.2+, LangChain 1.x, Azure OpenAI, Azure AI Search, Azure Blob Storage. No MCP.

*§87 backlog updates:* MCP-based items previously in scope for §87 backlog (real-time SAP data, external verification benchmarks) are removed. These are not "deferred to v2.2" — they are architecturally excluded. The data channel is always uploaded documents via `improve_evidence_index`.

**Data architecture principle to document:**

The `improve_evidence_index` is not merely "case-specific uploaded documents" — it is the *only* channel for external / real-world data in AgentLean. This elevates its architectural importance. Coaching content itself includes guidance on what data to upload and how to structure it. Belt data-collection discipline is what the platform depends on. Worth capturing as an explicit design principle in ARCHITECTURE.md §1 (Overview) or a new principle subsection.

**Decision 2 — Computation tools ratified for v2.1, per-phase bound (Option B).**

Ratified 18 computation tools distributed across DMAIC phases. Each is a `@tool(args_schema=...)` per CLAUDE.md §329 pattern.

**Per-phase distribution:**

| Phase | Universal tools | Phase-specific computation tools | Total |
|---|---|---|---|
| Define | 8 | `calculate_expected_savings` | 9 |
| Measure | 8 | `calculate_sigma_level`, `calculate_cpk`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq`, `calculate_grr`, `calculate_sample_size_proportion`, `calculate_sample_size_mean` | 16 |
| Analyse | 8 | `t_test`, `chi_square_test`, `anova`, `pearson_correlation`, `linear_regression` | 13 |
| Improve | 8 | `calculate_doe_main_effects` | 9 |
| Control | 8 | `xbar_r_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk` | 12 |

Universal 8: `record_field`, `rag_lookup_methodology`, `rag_lookup_evidence`, `rag_lookup_case_history`, `propose_template`, `propose_diagram`, `check_gate_status`, `request_human_approval`.

**Design rationale — per-phase binding (Option B) chosen over universal binding (Option A):**

- Tool selection quality degrades past ~10–15 tools per agent (2026 practitioner guidance)
- Phase-appropriate tool subset keeps each coach in the tractable range
- Under Option B, no phase exceeds 16 tools; most are 9–13
- Under Option A, all coaches would carry 26 tools regardless of relevance — extra reasoning burden per turn

**Design rationale — separate tools rather than parameterised grouping:**

Considered grouping (e.g., one `calculate_sample_size(type, ...)` tool with a mode parameter) and rejected. Parameterisation moves the selection burden into the argument space; LLMs handle distinct named tools more reliably than mode arguments. Each canonical DMAIC calculation gets its own tool with a clear name signalling its purpose.

**Architectural note — phase subgraph builder needs to know its tool subset:**

ARCHITECTURE.md §3.2 currently describes the coach as bound to seven (now eight) universal tools. Under Option B, retrieval + record_field + advisory tools stay universal, but computation tools are phase-specific. The phase subgraph builder function needs an additional parameter indicating which phase it's building — used to select the correct computation tool subset for `bind_tools()`. Small change, worth calling out explicitly.

**Propagation needed at batch commit:**

- **EDUCATIONAL.md §39 rewrite** — restructure as taxonomic scaffold per §37/§38 pattern. Retire MCP-related "missing capabilities" claims. Document computation tools as v2.1 additions. Cross-references to §23, §36, §37, §38, §57–65 (with §57–65 correctly framed as pedagogical knowledge).
- **EDUCATIONAL.md §57–65** — full sweep. Reduce to knowledge-only sections. §63 particularly needs restructuring to document the MCP-out decision explicitly.
- **CLAUDE.md v2.1** — add computation tools section (probably under §5 tools or new §5.x). Document the per-phase binding pattern. Add MCP-out principle to §1 or §7.
- **ARCHITECTURE.md v2.1.1** — §3.2 coach description updated for per-phase tool binding. §3 (agent architecture) or §1 (overview) documents the data-source principle (uploaded documents only, no live integrations).
- **userMemories** — update to remove MCP from stack listing.
- **§87 backlog** — remove MCP-dependent items (real-time SAP data, external verification benchmarks). These are not deferred; they are excluded.

**Retained pedagogy:**

§39's "four capabilities" framing (accesses external knowledge, retrieves documents/databases, enables verification/search/computation, supports grounded reasoning) is worth keeping in the rewrite. The Course 4 (MCP) connection becomes a "knowledge/pedagogy" pointer rather than a roadmap link. The "today vs missing" table gets updated to reflect ratified state — computation tools move from ❌ to ✅, MCP-dependent items are removed as out-of-scope.

---

### §40 — Metadata as a Signal: Freshness, Authority, and Context

**Status:** Ratified this session. Three-way split.

**Schema verification (this session):**

User provided full schemas for all three indexes. All seven metadata fields §40 references verified present:

| Index | Fields (relevant to §40) |
|---|---|
| `improve_knowledge_index` | id, content, `content_vector` (3072d), metadata, `source_file`, `phase_relevance`, `page_number` (Int32) |
| `improve_evidence_index` | id, content, `content_vector` (3072d), metadata, case_id |
| `improve_case_index` | id, case_id, title, `belt_level`, leader, department, current_phase, rag_status, `status`, `created_at`, target_date, `days_in_phase` (Int32), `phase_summary_define`, `phase_summary_measure`, `phase_summary_analyse_phase`, `phase_summary_improve`, `phase_summary_control`, content_text, `embedding` (SingleCollection) |

**Vector field name asymmetry — reconfirmed:** `improve_knowledge_index` and `improve_evidence_index` use `content_vector`. `improve_case_index` uses `embedding`. §36 decision correctly handles this — each tool bound to its own index knows its own field name locally, no shared retriever, no runtime normalisation. Not a blocker.

**Schema issue — RESOLVED via rename (see Pre-commit priority action #1):** `phase_summary_analyse_phase` field renamed to `phase_summary_analyse` for consistency with `phase_summary_define`, `_measure`, `_improve`, `_control`. Original recommendation in this log (mapping constant workaround) is superseded by user's decision this session to fix the field name at the source. Cleaner outcome — no permanent workaround, code can use naive `phase_summary_{phase.lower()}` pattern once rename lands.

**Documentation gap — RESOLVED via schema capture (see Pre-commit priority action #2):** Full schemas for all three indexes will be documented in ARCHITECTURE.md §7 (canonical) and referenced from CLAUDE.md §7 at batch commit.

**Three-way split ratified:**

*Idea 1 — Static metadata filters and ordering. RATIFIED FOR v2.1.*

Small, concrete, no infrastructure change. Adds `filter=` and `order_by=` clauses to retrieval tool implementations.

For `rag_lookup_methodology` (already includes `phase_relevance` filter per §37):
- No additional metadata filters needed. `source_file` and `page_number` are useful as *returned* metadata for citation transparency ("this came from page 47 of the BB eBook"), not as filter criteria.

For `rag_lookup_evidence`:
- Existing `case_id` filter retained (already in ratified signature)
- Add `order_by=["uploaded_at desc"]` — Belt's most recent uploads more likely relevant. Note: `improve_evidence_index` schema does not show an `uploaded_at` field explicitly — verify presence before implementing, or use metadata JSON blob if timestamp lives there.

For `rag_lookup_case_history`:
- Add `filter=f"status eq 'completed'"` — completed cases more authoritative than in-progress ones
- Add `order_by=["created_at desc"]` — freshness for yokoten
- `belt_level` filtering left OFF by default — over-narrowing risk (Green Belt might benefit from Black Belt cases). Optional parameter for scoped searches.

Metadata filters propagate through RRF fusion — each variant query returns metadata-filtered results, RRF combines normally.

*Idea 2 — Authority weighting between sources. NO NEW WORK.*

§38 memory hierarchy paragraph in coach's system prompt (methodology > confirmed captured_fields > case history > recent messages) already handles this. §40's framing as a metadata signal is misleading — the actual mechanism is prompt-level priority, not per-chunk metadata scoring.

*Idea 3 — Feedback adaptation. DEFERRED TO §87 WITH IMPLEMENTATION CAVEATS.*

Concept is valid — coaching system that learns from Belt outcomes is more valuable than static ranking. But §40's sketched implementation has real problems:

1. **Causal attribution weakness.** All chunks retrieved during a phase get equal +0.1 credit for gate passage. A Belt might pass despite unhelpful chunks; the effective chunks might be from turn 3 while turns 1, 5, 8 chunks were irrelevant. Turn-level attribution is missing; over 50 projects, useful chunks and noise chunks both accumulate scores.

2. **Selection bias / cold drift.** Chunks demoted enough to fall below top-k stop being retrieved and can't accumulate positive feedback anymore. Silent disappearance of chunks from the effective corpus.

3. **Infrastructure gap.** Azure AI Search doesn't natively support per-chunk boost adjustments. Would require external score table (Cosmos DB or Blob) combined with vector similarity at query merge time. Real infrastructure work, not the "quick win" §40 implies.

Better v2.2 formulation would use LangSmith trace analysis for retrospective attribution or offline evaluation runs comparing retrieval variants — not real-time in-line score updates. Genuine research workstream.

**Section rewrite plan for §40:**

Restructure into three subsections matching the three ideas. Preserve the "what we have but do not use" table as documentation of actual metadata schema (verified this session). Retire the feedback adaptation code sketch; replace with a note pointing to §87 backlog and the alternative implementation approaches above. Cross-links to §37 (`phase_relevance` filter already ratified), §38 (memory hierarchy already ratified), §87 (feedback adaptation deferred with caveats).

**Adding to §87 backlog (row 9):**

| # | Source | Deferred capability | Why deferred | Promotion trigger |
|---|---|---|---|---|
| 9 | §40 | Feedback-driven chunk score adaptation | Sketched implementation has causal-attribution problems (all chunks equally credited for gate passage regardless of actual contribution) and cold-drift problems (demoted chunks stop being retrieved so can't recover). Requires design work — likely LangSmith trace analysis for retrospective attribution or offline evaluation rather than real-time in-line adjustments. Azure AI Search does not natively support per-chunk boost updates; external score table required. | Retrieval evaluation shows systematic misses that static ranking + metadata filters cannot fix; dedicated v2.2 research workstream established. |

**Propagation needed at batch commit:**

- **EDUCATIONAL.md §40 rewrite** — three-subsection restructure per above
- **ARCHITECTURE.md §7** — add full index schemas (from user-provided data this session) as new subsection. Closes documentation gap.
- **§32/§33 log entries** — update `rag_lookup_evidence` and `rag_lookup_case_history` tool specs to include the new metadata filters and ordering clauses
- **Code path** — implement `PHASE_SUMMARY_FIELD_MAP` mapping constant in whatever module reads `phase_summary_*` fields. Trivial addition, but needs to exist before code hits Analyse phase reads.

---

### §48 — Reflection Nodes vs Consensus Modeling — Resolving the Ambiguity

**Status:** Ratified this session. Two-layer validation design confirmed. Cross-references to §22, §46, §47 scoped.

**Core distinction — preserved exactly as §48 states it:**

- Reflection = ONE perspective checking itself against a STANDARD → our `DMAICGraderMiddleware` (§42)
- Consensus modeling = MULTIPLE genuinely independent perspectives that may legitimately disagree, being RECONCILED → debate subgraph for root cause validation (§22, Analyse phase only)

This distinction is correct and should be preserved verbatim in the rewrite. It's the clearest statement in the file of when each pattern applies.

**Two-layer validation design ratified:**

- **Layer 1 — `DMAICGateValidator` (deterministic, rule-based, no LLM call).** Static methods checking objective properties: does the problem statement contain a number? Does the scope mention exclusions? Does the goal have a time-bound keyword? Cheap, instant, deterministic.
- **Layer 2 — `DMAICGraderMiddleware` (LLM-as-a-judge, subjective quality).** Checks whether the content is *meaningfully* correct, not just structurally present. Is the problem statement a real measurable problem? Is the root cause grounded in evidence?

Layer 1 runs before Layer 2. If deterministic checks fail, no LLM grader call — fix the obvious issues first. Combined iteration cap: 3 (covers both layers together).

**Updated nine-step flow — step 2 becomes two sub-steps:**

| Step | What Happens |
|---|---|
| 1. Executor runs | Coach produces output + extraction |
| 2a. `DMAICGateValidator` | Deterministic rule-based checks (no LLM). If failures → feedback to coach, retry |
| 2b. `DMAICGraderMiddleware` | LLM-as-a-judge quality evaluation against phase rubric. If needs_revision → per-criterion feedback, retry. Combined cap with 2a: 3 iterations |
| 3. Interrupt fires | Belt sees validator+grader approved output |
| 4–9 | (unchanged from §42 ratification) |

**Three-Prompt Separation Pattern — preserved:**

Generation → Validation → Correction is what happens inside the grader loop. §48 makes this explicit in a way §42 didn't. The `ChatPromptTemplate` correction (not `PromptTemplate` for chat models) is correct — preserve it.

**DMAICGateValidator code — preserved with note:**

The `validate_smart_goal`, `validate_problem_statement`, `validate_scope` static methods are useful reference implementations. Note for batch commit: these are illustrative validators for the Define phase; Measure, Analyse, Improve, Control need their own deterministic validators (e.g., `validate_baseline_has_units`, `validate_root_cause_has_evidence_reference`, `validate_control_plan_has_owner`). Draft during governance doc rewrite, not now.

**Simulated LLM Caveat — preserved:**

§48's warning that the course demo uses fake LLMs (attempt 1 hardcoded to fail, attempt 2 to pass) is a good production warning. Real LLMs can fail on attempt 2 as well, or fix one criterion while introducing a new failure. Links to §42's `max_iterations=3` cap.

**Cross-references to §22, §46, §47 — scoping decisions:**

- **§22 (Debate Agents):** Not yet reviewed. Scoped to Analyse phase only (root cause validation). Recommend deferring to §87 backlog as a v2.2 feature — depends on the base coaching loop (v2.1) working first. To be confirmed when we review §22.
- **§46 (Coordination Pattern Taxonomy):** Classification index, not implementation. Needs updating at batch commit to reflect ratified decisions (§38 memory hierarchy now covers "Priority-based resolution" which §46 marks as "not implemented"). No new design.
- **§47 (Opinion Aggregation):** Depends on §22 (debate subgraph as one of its signal sources). If §22 is deferred to v2.2, §47 is also deferred. Gap 28 moves to §87 backlog.

**§48 rewrite plan:**

1. Keep the Reflection vs Consensus distinction verbatim — it's the clearest statement in the file
2. Keep the Three-Prompt Separation Pattern and ChatPromptTemplate correction
3. Keep the DMAICGateValidator code as Layer 1 reference implementation
4. Add explicit cross-reference to §42 DMAICGraderMiddleware as Layer 2
5. Add the two-layer design explanation (Layer 1 deterministic pre-filter → Layer 2 LLM grader)
6. Keep the Simulated LLM Caveat
7. Update the "Connection to RubricMiddleware" paragraph to reference §42's Option B decision (custom middleware, not deepagents)
8. Cross-references: §42 (grader), §22 (debate — scoped to Analyse, likely v2.2), §46 (taxonomy — batch-commit update), §47 (aggregation — depends on §22)

**Propagation:**
- §42 log entry — add note that DMAICGateValidator (Layer 1) runs before the grader (Layer 2) as a pre-filter
- §2 nine-step table — step 2 split into 2a/2b as shown above
- §87 backlog — add §22 (debate subgraph) and §47/Gap 28 (opinion aggregation) as v2.2 candidates, pending §22 review confirmation

**Adding to §87 backlog (rows 10–11, pending §22 review confirmation):**

| # | Source | Deferred capability | Why deferred | Promotion trigger |
|---|---|---|---|---|
| 10 | §22 | Adversarial debate subgraph for root cause validation (Analyse phase) | Analyse-phase-only feature; depends on base coaching loop (v2.1) working first; adds 2-3 LLM calls per root cause evaluation | Base coaching loop stable in production; Analyse phase coach producing root causes that need adversarial stress-testing |
| 11 | §47 | Opinion aggregation framework for combining decision quality signals (Gap 28) | Depends on §22 debate subgraph as one of its signal sources | §22 debate subgraph implemented and producing confidence scores |

---

### §22 — Debate Agents and Consensus Voting (preliminary scoping, full review pending)

**Not yet fully reviewed.** Preliminary scoping from §48 cross-reference analysis:

- Scoped to Analyse phase root cause validation only
- Adversarial debate pattern (advocate + skeptic + judge) is the correct consensus mechanism for this use case
- Hybrid consensus strategy (Confidence + Iteration + Judge) recommended by §22 itself
- Recommend deferring to §87 backlog as v2.2 feature — to be confirmed during full §22 review

---

### §46 — Coordination Pattern Taxonomy (preliminary scoping, full review pending)

**Not yet fully reviewed.** Preliminary scoping:

- Classification index, not implementation
- Several entries are now stale given ratified decisions (e.g., "Priority-based resolution: not implemented" is wrong post-§38)
- Batch-commit update to reflect current ratified state — no new design needed
- Full review deferred to Category B sweep

---

### §47 — Opinion Aggregation Techniques (preliminary scoping, full review pending)

**Not yet fully reviewed.** Preliminary scoping:

- Depends on §22 (debate subgraph as signal source)
- Gap 28 deferred to §87 if §22 is deferred
- Rank Aggregation = RRF (already ratified in §33)
- Weighted Aggregation = memory hierarchy (already ratified in §38)
- Full review deferred to Category B/C sweep

---

### §51 — InsightForge Analytics — Complete Production-Grade Reference Implementation

**Status:** Ratified this session. Reduce to structural reference section — keep the five-layer scaffold and valuable patterns, strip all deprecated code, replace with cross-references to ratified decisions.

**What to preserve:**

1. **Five-layer architecture scaffold** (Workflow → Routing → Transform → Retrieval → Governance) — conceptually sound, maps onto Agent Improve's ratified architecture. Keep as an overview diagram showing how the pieces connect end-to-end.

2. **RunnableSequence, RunnableBranch, RunnableParallel** — keep the three composition patterns as pedagogical reference. These are the LCEL primitives used inside nodes (per §27 ratification). Add a note: "These live inside individual nodes. The subgraph structure (§23) handles the bigger orchestration."

3. **Risk gate pattern** — four trigger conditions (LOW_CONFIDENCE, SENSITIVE_TOPIC, HIGH_RETRY_COUNT, RETRIEVAL_MISS) routing to human review. Directly maps onto our §2 nine-step HITL flow. Useful template for production.

4. **Routing strategy comparison table** — six strategies with limitations. Genuinely new content not covered elsewhere. Hybrid (fixed rules + LLM reasoning) matches our per-phase tool binding rationale.

5. **Practitioner reflection** — domain-varying confidence thresholds ("market vs regulatory" = "Define vs Analyse" in our context). Directly relevant warning against a single global confidence threshold across DMAIC phases.

6. **Governance metrics table** — Pipeline Success Rate, Retry Frequency, Retrieval Relevance, Reasoning Accuracy. Directly applicable to §75 evaluation dataset design.

7. **Scoring/ranking pattern** (Layer 3) — not deprecated, useful as-is. Fallback score of 0 ensuring malformed outputs sink rather than crash is a good defensive pattern.

**What to strip (deprecated, superseded by ratified decisions):**

- Layer 1 `OutputFixingParser` + `parse_with_retry` → replaced by §82 ProviderStrategy (`with_structured_output`). See §29 ratification.
- Layer 2 `create_react_agent` → replaced by `create_agent` from `langchain.agents`. §51 already flags this.
- Layer 4 `ConversationSummaryMemory`, `ConversationEntityMemory`, `VectorStoreRetrieverMemory` → replaced by SummarizationMiddleware (§36) + AzureBlobStore (§52). §51 already flags these.
- Layer 4 `MultiQueryRetriever`, `BM25Retriever` → replaced by multi-query + RRF inside `rag_lookup_*` tools (§32/§33). Deprecated per §32 web-verification.

**Cross-reference map for the rewrite (deprecated layer → ratified replacement):**

| §51 Layer | Deprecated pattern | Ratified replacement |
|---|---|---|
| Layer 1 — Workflow | `OutputFixingParser`, `parse_with_retry` | §82 ProviderStrategy, §42 DMAICGraderMiddleware |
| Layer 2 — Routing | `create_react_agent` | `create_agent`, per-phase tool binding (§39) |
| Layer 3 — Transform | Scoring/ranking (not deprecated) | Keep as-is |
| Layer 4 — Retrieval | `MultiQueryRetriever`, deprecated memory classes | §32/§33 `rag_lookup_*` tools, §36 SummarizationMiddleware, §52 AzureBlobStore |
| Layer 5 — Governance | Risk gate, metrics | §42 grader, §48 gate validator, §75 evaluation metrics |

**Adaptive memory router concept — preserve the pattern, not the classes:**

§51's `adaptive_memory_router` (cheap keyword-based intent classification before expensive retrieval) is a valid pattern even though the classes it uses are deprecated. Worth preserving as a design note: before calling a retrieval tool, a lightweight classifier can decide whether retrieval is even needed for this turn. This could be implemented as a small utility inside the coach's system prompt or as a `before_tool_call` middleware hook. Not ratified as a v2.1 addition but worth noting for v2.2 optimisation.

**No new architectural decisions from §51.** The section becomes a "how the pieces fit together" structural reference, not a source of implementation guidance.

---

### §68 — Decision Validation Against Business Constraints

**Status:** Ratified this session. Completes the gate validation architecture from two layers (§48) to four layers.

**Ratified four-layer gate validation stack:**

| Layer | What it checks | Mechanism | Model | When it fires |
|---|---|---|---|---|
| 1. Coherence | Is this a real, meaningful, conclusive statement? (catches gibberish, vague non-answers, contradictions, off-topic, parroting Belt's words) | **Lightweight LLM check** — `operational-model` (gpt-4o-mini), temperature 0.1 | Cheap LLM | Every coaching turn |
| 2. Field presence | Are all required fields for this phase populated? | Deterministic — field existence on PhaseState | No LLM | Gate boundary only |
| 3. Constraint validation | Does the decision address budget / timeline / risk / measurement? | **Lightweight LLM check** — `operational-model` (gpt-4o-mini), temperature 0.1 | Cheap LLM | Gate boundary + mid-conversation for key decisions |
| 4. Quality rubric | Does it meet DMAIC quality standards per criterion? | Full LLM grader — `DMAICGraderMiddleware`, `operational-model`, temperature 0.1 | Cheap LLM | Gate boundary only |

**Run cheapest first, most expensive last. Each layer only fires if the previous passes.**

**User decision this session (updated):** Layer 1 coherence check upgraded from deterministic (length + question mark) to **lightweight LLM check.** Rationale from user: "I can write garbage in and a length check will not detect it." Deterministic coherence is too poor to serve as a real quality filter. The LLM check catches gibberish, vague non-answers ("there are some issues"), self-contradictions, off-topic responses, and parroting the Belt's own words without adding value — none of which a format check can detect.

**Cost impact of Layer 1 as LLM:** Layer 1 fires every coaching turn (~20-40 times per phase session). At ~250 tokens per check on gpt-4o-mini: ~$0.01-0.02 per phase session. Negligible. The quality improvement over deterministic checking justifies the cost.

**Layer 2 stays deterministic.** Checking whether a field exists in a dictionary genuinely does not need an LLM. This is the only deterministic layer in the stack.

**Layer 3 implementation sketch:**

```python
class ConstraintVerdict(BaseModel):
    constraint: str
    addressed: bool
    evidence: str  # which part of the decision addresses this constraint

class ConstraintCheckResult(BaseModel):
    all_satisfied: bool
    verdicts: list[ConstraintVerdict]

constraint_checker = operational_model.with_structured_output(ConstraintCheckResult)

def validate_constraints(decision: str, constraints: dict, phase: str) -> ConstraintCheckResult:
    return constraint_checker.invoke(
        f"Check whether this {phase} phase decision addresses each constraint.\n\n"
        f"Decision: {decision}\n\n"
        f"Constraints to check:\n"
        + "\n".join(f"- {k}: {v}" for k, v in constraints.items())
    )
```

Model: `operational-model` (gpt-4o-mini). Temperature: 0.1 (consistent verdicts). Structured output via `with_structured_output` (§82 ProviderStrategy).

**Value-dependent constraints — preserved from §68:**

Constraints can be conditional on other field values. Example: the risk mitigation check only fires when `risk_level == "low"` (a low-risk project should explicitly address risk; a high-risk project's decision inherently involves risk). This is more sophisticated than flat constraint lists and should be implemented for any constraint conditional on another field.

**Per-phase constraint sets (from §68, preserved):**

```python
DEFINE_CONSTRAINTS = {
    "baseline": "must reference a measurable current state",
    "target": "must include a specific improvement target",
    "scope": "must define what is included and excluded",
    "timeline": "must reference a project timeline"
}

ANALYSE_CONSTRAINTS = {
    "root_cause": "must identify a specific, actionable root cause",
    "validation": "must reference how root cause was validated",
    # Value-dependent: risk check only if risk_level == "low"
}

IMPROVE_CONSTRAINTS = {
    "budget": "improvement approach must address cost",
    "deadline": "implementation plan must reference timeline",
    "measurement": "must specify how improvement will be measured"
}

CONTROL_CONSTRAINTS = {
    "monitoring": "control plan must specify monitoring frequency",
    "sustainability": "must define process for maintaining gains",
    "handover": "must identify process owner accepting responsibility"
}
```

**Retry-with-accumulated-feedback pattern — preserved:**

When any layer fails, the specific failure reason feeds back to the coach for the next attempt. Not "try again" but "your previous answer did not address timeline or risk mitigation — fix those specifically." Each attempt receives accumulated feedback from all previous failures. Shared iteration cap: 3 across all four layers.

Fallback on max_iterations_reached: escalate to Belt with clear message listing what was tried and what failed. Belt is the final arbiter, not the agent.

**Impact on §48 two-layer design — superseded:**

§48 ratified a two-layer design (2a deterministic, 2b LLM grader). §68 expands this to four layers. The §48 log entry's step 2a/2b becomes 2a/2b/2c/2d:

```
Step 2a: Coherence check (deterministic)
Step 2b: Field presence check (deterministic, §48 DMAICGateValidator)
Step 2c: Constraint validation (lightweight LLM, §68)
Step 2d: Quality rubric (LLM grader, §42 DMAICGraderMiddleware)
```

All four run inside the same pre-Belt window (before the interrupt fires in step 3 of the nine-step HITL pattern).

**Dict-based audit log format — ratified:**

§68's recommendation to use dict-based entries (not tuples) for step_log is correct and aligns with §18's PhaseState `step_log` field. Each validation attempt logged as:

```python
{"layer": "constraint", "attempt": 2, "status": "failed",
 "reason": "does not address timeline", "decision_excerpt": "..."}
```

**§69 (Validation Layer Placement) — explicitly ratified this session:**

§69's content was initially folded into §68's entry. User reviewed §69 in full and ratified the three failure behaviours explicitly:

1. **Silent retry for coherence failures only.** Belt never sees the failed attempt. Justified exception: showing the Belt that the AI produced gibberish adds no value and erodes trust. The Belt only sees the corrected response.

2. **Coached improvement for mid-conversation constraint failures.** When the Belt proposes a weak key decision ("the root cause is poor morale"), the coach uses the constraint failure as a teaching moment rather than silently accepting it. This is core DMAIC pedagogy — the coach teaches the Belt what good looks like. Transparency is key here.

3. **Full HITL escalation at gate boundary.** Belt sees exactly what passed and failed, corrects, approves. Already ratified in §2 and §42.

**Design principle ratified (from user, this session):** *"Coached improvement is key as silent is not transparent."* The default posture of the system is transparency — the Belt sees what's happening and participates in fixing it. Silent retry is the narrowly scoped exception (coherence only), justified only because visibility would harm the Belt's experience without giving them anything actionable. Everything else — constraint failures, field completeness, quality rubric — is visible and collaborative.

**Four-level self-healing hierarchy ratified:**

| Level | Trigger | Behaviour | Belt visibility |
|---|---|---|---|
| 1 — Silent | Coherence failure mid-turn | System retries internally, Belt sees corrected response | Invisible |
| 2 — Coached | Constraint failure on key proposal mid-conversation | Coach helps Belt improve their formulation — educational feedback | Transparent, collaborative |
| 3 — Validated | Full four-layer check at gate boundary | Belt sees results, corrects, approves | Transparent, Belt is approver |
| 4 — Escalated | Max attempts exhausted at gate | System defers to Belt with clear message listing unresolved constraints | Transparent, Belt is final arbiter |

**Retry behaviour per level:**

- Level 1: max 2 silent retries → degraded mode response ("I need a moment to reconnect...")
- Level 2: no retry cap — this is coaching dialogue, not a retry loop. Coach keeps working with the Belt until the proposal improves or the Belt signals gate readiness.
- Level 3: max 3 attempts with accumulated feedback across all four validation layers
- Level 4: no retry — Belt decides manually

**Cross-references:**
- §42 (DMAICGraderMiddleware — Layer 4)
- §48 (DMAICGateValidator — Layer 2, now part of four-layer stack)
- §2 (nine-step HITL pattern — all four layers fire in step 2)
- §18 (step_log audit trail — dict-based format)
- §82 (ProviderStrategy — `with_structured_output` for Layer 3 structured verdicts)

**No new gap number.** §68 completes the gate validation architecture. The four-layer stack is the full implementation target for Gap 23.

---

### §71 — Multi-Hop Retrieval — Gap 17 Formally Closed

**Status:** Ratified this session. Gap 17 confirmed closed. §34/§71 reconciliation ratified.

**§34/§71 reconciliation — two approaches, phase-dependent:**

- **Analyse phase: planned multi-hop (§71's three-stage pipeline).** Planner pre-decomposes the question into typed `Plan` schema with exactly 3 hops before any retrieval fires. More structured, more predictable, fully inspectable in LangSmith (you can see each hop's question and result). Correct for Analyse because root cause validation is inherently layered and inspectability matters in a quality system.

- **All other phases: emergent multi-hop (§34's ReAct loop).** The coach naturally calls `rag_lookup_methodology` multiple times when needed, driven by its own reasoning. No structured hop plan. Correct for phases where multi-hop is occasional (Measure for complex MSA questions, Improve for approach comparison) — overhead of a structured planner isn't justified for rare occurrences.

- **Gate validation: no multi-hop, ever.** §71 explicitly excludes retrieval from the four-layer validation stack (§68). The rubric already encodes the methodology standards. Adding retrieval at gate time is redundant and adds latency at exactly the moment the Belt is waiting.

**Three query types — where multi-hop applies:**

| Type | Source | Multi-hop? | Rationale |
|---|---|---|---|
| 1. Methodology retrieval | `improve_knowledge_index` (BB eBook) | Yes — Analyse always, others occasionally | Knowledge questions are often layered (method → application → threshold) |
| 2. Belt's conversational answers | Belt's own input → field extraction | Never | Not retrieval — extraction and validation (§48, §68, §69) |
| 3. Gate quality evaluation | `captured_fields` in state | Never | Rubric already encodes standards; retrieval is redundant |

**Phase-by-phase multi-hop decision table (from §71, ratified):**

| Phase | Default | Multi-hop trigger |
|---|---|---|
| Define | Single-hop | Never — scoping questions are direct |
| Measure | Single-hop | Complex measurement system validation (GR&R methodology) |
| **Analyse** | **Multi-hop (planned)** | Almost always — root cause validation is inherently layered |
| Improve | Single-hop | When Belt compares competing approaches |
| Control | Single-hop | Never — documentation questions are direct |
| **Gate validation** | **No retrieval** | **Never** |

**Planner integration — retrieval_strategy field:**

The Phase Planner (§5, §11) decides retrieval strategy at plan time, not at retrieval time:

```python
coaching_plan = {
    "next_action": "coach_root_cause_validation",
    "retrieval_strategy": "multi_hop",    # planner decides
    "retrieval_hops": [
        "what tools validate root cause in DMAIC analyse phase",
        "how is {hop1_answer} applied to {root_cause_candidate}",
        "what threshold applies for {hop2_answer} in a call centre context"
    ],
    "focus_field": "root_cause_statement"
}
```

When `retrieval_strategy == "single_hop"`: executor calls `rag_lookup_methodology` once.
When `retrieval_strategy == "multi_hop"`: executor runs the three-hop chain with typed Plan schema.

**Multi-query + multi-hop composition:**

Both can be used together: multi-query (§32/§33) at each hop to improve recall via variant generation + RRF, then chain the best result from each hop to the next. Multi-query broadens coverage within a hop; multi-hop deepens reasoning across hops. Independent, composable.

**Gap 17 — CONFIRMED CLOSED.** The §34 contradiction is resolved:
- §34 originally said Gap 17 open, deferred. Our §34 ratification corrected this — multi-hop is available via the ReAct coach with 5-hop cap (`recursion_limit=11`).
- §71 adds the design layer: scoping (which phases, which query types), phase planner integration, and the planned vs emergent distinction.
- Together they close Gap 17 completely for v2.1.

**Cross-references:**
- §34 (mechanism — ReAct loop, 5-hop cap, `recursion_limit=11`, `GraphRecursionError` handling)
- §32/§33 (multi-query + RRF — composable with multi-hop at each hop)
- §5/§11/§20 (Planner-Executor pattern — planner decides `retrieval_strategy`)
- §68/§69 (gate validation explicitly excluded from multi-hop)

---

## Category C — Review Complete

All Category C sections reviewed and ratified:

| Section | Status |
|---|---|
| §29 — OutputFixingParser | Ratified — superseded by §82 ProviderStrategy |
| §32 — Multi-Query Retrieval | Ratified — `rag_lookup_methodology` with multi-query + RRF |
| §33 — RAG Fusion | Ratified — RRF in all three `rag_lookup_*` tools |
| §34 — Multi-Hop Reasoning | Ratified — ReAct loop, 5-hop cap, `recursion_limit=11` |
| §35 — Query Voting/Weighted Fusion | Ratified — reduced to knowledge-only section |
| §42 — RubricMiddleware | Ratified — Option B custom `DMAICGraderMiddleware` |
| §48 — Reflection vs Consensus | Ratified — two-layer design (expanded to four-layer by §68) |
| §51 — InsightForge Analytics | Ratified — structural reference, deprecated code stripped |
| §54 — RubricMiddleware Correction | Incorporated into §42 |
| §68 — Decision Validation | Ratified — four-layer gate validation stack |
| §69 — Validation Layer Placement | Ratified — three firing contexts, transparency principle |
| §71 — Multi-Hop Retrieval | Ratified — Gap 17 closed, planned (Analyse) vs emergent (others) |

---

## Category D — Reliability, Recovery, and Failure Handling

**All sections reviewed and ratified this session.**

**Scope clarification from user (this session):** *"I don't understand what v2.1 or §87 means. For me, what we have is a deprecated and not production-ready Agent Improve that after my trainings we upgrade to the latest architecture of LangChain and LangGraph. After we complete this document we update it and begin with the full-scale refactoring."*

This reframes the scope: there is the old codebase (broken, monolithic LLM, no subgraphs, no proper retrieval) and the refactored Agent Improve (what we're building after this review). The refactor is a full rebuild to production grade, not an incremental patch. Items needed for a production-grade system belong in the refactor, not on a "later" list.

**§87 backlog survives but is tightened.** It tracks genuinely premature items (beta features, research workstreams requiring their own design phase, capabilities with known unsolved problems). It does NOT track things that are needed for production but were lazily deferred. Saga/compensation and cache infrastructure were incorrectly deferred earlier in this review — both are now in scope per user's decision this session.

### §20 — Fallback Chains (Index mislabel)

**No section to review.** The topic groups index lists "Section 20 — Fallback Chains" in Category D, but actual §20 is "Supervisor / Worker Architecture" (already reviewed and ratified in Category B). Fallback chain content lives in §66 and §67. Added to cross-cutting index corrections — the index entry should point to §66/§67, not §20.

### §49 — Saga-Based Transactions and Compensating Actions

**Status:** Ratified. IN SCOPE for the refactor (not deferred). Updated by §79 — use LangGraph 1.2 native `error_handler=` instead of custom compensating nodes.

**What Saga solves:** when a multi-step process fails partway and leaves partial results in external systems (Azure Blob, `improve_case_index`), compensating actions undo those external writes so the system returns to a consistent state.

**Implementation using LangGraph 1.2 native mechanism:**

```python
def define_error_recovery(error: NodeError, state: DefineState) -> Command:
    """Compensating action for define_executor — undoes external writes."""
    delete_or_flag_stale_in_case_index(state["case_id"], "define")
    return Command(
        update={"extraction_error": str(error), "extraction_incomplete": True},
        goto="degraded_coaching_response"
    )

builder.add_node("define_executor", define_executor_fn,
                 error_handler=define_error_recovery)
```

Every phase executor node that writes to an external system (blob, case index, evidence index) gets an `error_handler=` with the corresponding compensation logic.

**Connection to gate reopening (§38 mid-phase conflict detection):** when a Belt changes a gate-approved value and the re-approval cascade fires, the affected phase's compensating action must run to clean up stale values in external systems. Saga + re-approval cascade are interdependent.

**Connection to time-travel debugging:** resuming from an earlier checkpoint does NOT undo external side effects. The compensating action must run alongside the rollback. This means time-travel for nodes with external writes requires Saga support to be correct.

### §64 — MCP Production Architecture

**Status:** Reduce to knowledge-only per §39 MCP-out decision. Preserve the structured error schema as a standalone pattern — it applies to Azure OpenAI and Azure AI Search errors regardless of MCP.

**Preserved pattern — structured error schema:**

```python
class AgentImproveError(BaseModel):
    error_code: str              # "TIMEOUT", "RATE_LIMIT", "AUTH_FAILURE", etc.
    severity: str                # "transient", "permanent"
    retry_recommendation: str    # "retry_after_backoff", "do_not_retry", "retry_after_delay"
    affected_identifier: str     # which service failed
    message: str                 # human-readable description
    timestamp: datetime
```

This schema is used by the circuit breaker, the fallback chain, and the audit trail (`step_log`). Applicable to all external service calls, not just MCP.

### §66 — Circuit Breaker, Context Recovery, and Safe Reopen

**Status:** Ratified. The six-step failure pipeline is the complete reliability architecture for the refactored Agent Improve.

**Six-step failure pipeline ratified:**

1. **Error classification** — transient vs permanent, structured error schema (§64)
2. **Context recovery** — save partial results before failing, resume from last success
3. **Circuit breaker** — three-state (CLOSED/OPEN/HALF-OPEN) for production. Threshold: 3 failures in 30 seconds trips open. Reset timeout: 60 seconds.
4. **Safe reopen** — one probe request in HALF-OPEN before resuming full traffic
5. **Graceful degradation** — fallback chain (§67)
6. **Smart fallbacks** — alternative models, cache, degraded mode

**Jitter ratified:** jittered backoff for shared resources (multiple subagents may retry simultaneously), exponential backoff for managed services (Azure OpenAI).

### §67 — Self-Healing Fallback Chain — Complete Reference Implementation

**Status:** Ratified. FULL implementation including cache infrastructure (user decision this session — "full scale with cache infrastructure, we need to do this right").

**Four-level fallback chain ratified:**

```
Level 1: Azure OpenAI gpt-4o (operational-premium)
         exponential_backoff — managed service
         ↓ if rate-limited or unavailable

Level 2: Azure OpenAI gpt-4o-mini (operational-model)
         exponential_backoff — same managed tier
         ↓ if also unavailable

Level 3: Response cache (Azure Redis Cache or equivalent)
         jittered_backoff — shared resource
         ↓ if cache miss or unavailable

Level 4: Degraded mode — always succeeds, never crashes
         Belt sees: "I'm having a temporary connection issue.
         Your progress is saved. You have 3 of 5 fields complete
         in the Analyse phase."
```

**Level 3 cache infrastructure — IN SCOPE for the refactor (not deferred).**

User decision: "full scale with cache infrastructure." The original §66/§67 referenced "MCP knowledge cache from Section 65" which doesn't apply under §39 MCP-out. Replace with Azure Redis Cache (or Azure Cache for Redis) as the cache backend. Cache stores: recent retrieval results keyed by query hash + phase, recent coaching responses for similar questions. Session-scoped, not global (different projects have different context).

**Note for Claude Code:** the cache infrastructure requires an Azure Redis Cache instance in the Azure stack. This is a new infrastructure component not in the current `valuesims-*` / `agentlean-*` setup. Add to the infrastructure provisioning plan.

**Degraded mode response uses actual state** — not a generic error:

```python
def degraded_mode_response(state):
    return (
        f"I'm experiencing a temporary connection issue. "
        f"Based on what we've captured so far in the {state['current_phase']} phase "
        f"({len(state['captured_fields'])} fields complete), "
        f"I'd suggest we pause here and continue once the system recovers. "
        f"Your progress is saved and nothing has been lost."
    )
```

**Structured audit log ratified:** every fallback attempt logged as dict (not tuple) to `step_log`:

```python
{"service": "gpt-4o", "attempt": 2, "status": "failed",
 "reason": "timeout after 45s", "timestamp": "..."}
```

### §79 — LangGraph 1.2 Native Reliability Primitives

**Status:** Ratified. Adopt for the refactor. Requires LangGraph 1.2.6+ (already ratified as upgrade target).

**Four primitives adopted:**

1. **Per-node timeouts** — `add_node(timeout=TimeoutPolicy(run_timeout=45))` on every phase executor node. 45 seconds is the wall-clock limit — fallback chain fires before the Belt notices the delay.

2. **Node-level error handlers** — `add_node(error_handler=...)` for Saga compensating actions (§49). Every node with external writes gets a handler.

3. **Graceful shutdown** — `RunControl.request_drain()` for deployment rollouts. Mid-coaching sessions save checkpoint and resume later. Production-grade session preservation.

4. **DeltaChannel** — beta, **deferred to §87 backlog.** Not needed until coaching sessions accumulate >200 turns. Genuinely premature — beta API, no production evidence of need.

**Cross-reference impact:**

| Section | Update needed |
|---|---|
| §49 (Saga) | Rewrite to use native `error_handler=` — done above |
| §66 (Failure pipeline) | Add per-node timeouts as Step 0 |
| §67 (Fallback chain) | Timeout fires before retries — `NodeTimeoutError` triggers the chain |
| §52 (Checkpointer + BaseStore) | Add DeltaChannel note as §87 future optimization |

### §87 backlog — items moved OUT of backlog into refactor scope this session

| # | Item | Previously | Now |
|---|---|---|---|
| - | Saga/compensating actions (§49) | Was "defer to §87" | **IN SCOPE** — user ratified this session |
| - | Cache infrastructure for Level 3 fallback (§67) | Was "defer to §87" | **IN SCOPE** — user: "full scale with cache infrastructure" |

### §87 backlog — item ADDED this session

| # | Source | Deferred capability | Why deferred | Promotion trigger |
|---|---|---|---|---|
| 12 | §79 | DeltaChannel for checkpoint compression | Beta API, not needed until sessions exceed 200 turns | Long-running DMAIC projects accumulate checkpoint size problems in production |
| 13 | §55/cross-cutting | Migrate from `AzureBlobCheckpointSaver` + `AzureBlobStore` to `PostgresSaver` + `PostgresStore` | Azure Blob checkpointer works for single-developer refactoring; adding PostgreSQL during the heaviest refactoring period is unnecessary infrastructure complexity | Post-refactor testing complete; before production launch with real Belts. Provision Azure Database for PostgreSQL (~€12-15/month). Migration is small — change constructor + connection string, run existing tests against PostgreSQL. |

---

## Category E — MCP (Model Context Protocol)

**All sections reviewed and ratified this session as a batch. MCP-out decision (§39) governs all.**

**Overall treatment:** MCP is permanently out of scope for Agent Improve, Agent Resolve, and Agent Flow (§39 ratification). Users upload their own data; `@tool` decorator handles all tool composition. MCP sections become pedagogical knowledge — valuable for understanding the protocol, not implementation guidance for AgentLean.

| Section | Treatment |
|---|---|
| §57 — Course correction (MCP is agent-to-tool, not agent-to-agent) | Keep as-is. Valuable correction to course material. |
| §58 — Course correction (two layers, not four) | Keep as-is. Valuable correction. |
| §59 — FastMCP server implementation | Keep as knowledge. Useful if Agent Flow or future products need MCP. |
| §60 — Internal @tool vs MCP tools | **Preserve as architectural reference** (not just MCP knowledge). The internal-tool boundary, hybrid planner + reactive tool pattern (Option C), and comparison table confirm our ratified architecture. Update tool names to ratified names (`rag_lookup_methodology`, `rag_lookup_evidence`, `rag_lookup_case_history`). |
| §61 — MCP Resources (URI-addressable read-only data) | Reduce to knowledge-only. |
| §62 — MCP Server Ecosystem (third-party servers) | Reduce to knowledge-only. |
| §63 — AgentLean MCP Server scope | **Rewrite** from planning document to "MCP evaluated for AgentLean — rejected, with rationale." Document §39 decision: users upload data, `@tool` handles single-stack composition, MCP overhead unjustified without cross-team tool sharing. |
| §64 — MCP Production Architecture | Structured error schema preserved as standalone (ratified in Category D). MCP-specific content becomes knowledge-only. |
| §65 — MCP Caching | Caching principles (cache key design, TTL, invalidation) preserved as applicable to Azure Redis Cache in the fallback chain (§67 Level 3). MCP-specific framing becomes knowledge-only. |

**§60 tool name updates needed at batch commit:**
- `retrieve_methodology` → `rag_lookup_methodology`
- `retrieve_similar_cases` → `rag_lookup_case_history`
- Add `rag_lookup_evidence` (not present in §60's original text)

**Category E complete.**

---

## Category F — Deployment, Versioning, and Infrastructure

### §55 — LangServe Archived, LangGraph Server Replacement

**Status:** Ratified. Stay on FastAPI.

**Decision:** LangServe is archived (May 2026). LangGraph Server is the official replacement but requires `langgraph-api` under Elastic License 2.0 — even the self-hosted tier requires a commercial license key. Web-verified this session from multiple Tier 1 and Tier 3 sources.

The FastAPI + LangGraph (MIT) + AzureBlobCheckpointSaver pattern is the standard approach for self-hosted deployments without a commercial license. This is what Agent Improve already uses. Fix `routes.py:238` (Step 6), keep the custom plumbing.

LangGraph Studio remains useful for development debugging (`langgraph dev` locally) without adopting LangGraph Server for production.

### §56 — Course Stale Deployment Warning

**Status:** No decision needed. §56 is a course-material reliability flag — treat all deployment code from Edureka Course 4 as stale (LangServe-based), substitute with FastAPI patterns. Already handled by §55 decision.

Editorial update at batch commit: add note "§55 decision ratified: FastAPI is the deployment layer. LangServe substitution complete."

### §72 — LangGraph Server Deployment Option

**Status:** No decision needed. §72 documents the evaluation that §55's decision resolves. Keep as historical record of why FastAPI was chosen over LangGraph Server.

Editorial update at batch commit: add note at top "Decision made in §55: stay on FastAPI. This section documents the evaluation."

### §73 — Langfuse (Open-Source LangSmith Alternative)

**Status:** No decision needed for the refactor. Keep LangSmith (already wired in since commit 1.1). §73 stays as knowledge for future enterprise deployment conversations.

Three triggers to revisit:
1. Enterprise customer asks about data residency for observability data
2. Team grows and per-seat LangSmith pricing becomes significant
3. AgentLean adds components outside the LangChain ecosystem

Langfuse's Code Evaluators capability noted for future reference — programmatic checks against production traces without LLM cost. Connects to §68 Layer 2 (field presence) as a continuous production monitoring option.

### §74 — API Versioning

**Status:** No decision needed for the refactor. No production system exists — the refactor produces the first production-grade version. Versioning practices become relevant after launch when updates must not break live Belts.

Keep §74 as knowledge for post-launch. The breaking-change definition table and "add new fields as optional" discipline are worth preserving for when they matter.

### §75 — Evaluation Dataset Design and Regression Testing

**Status:** Ratified with modified sequencing.

**Decision:** Build eval dataset **alongside** the refactor as a joint exercise in this claude.ai project, not before the refactor starts. User and Claude design the dataset together — Claude proposes examples based on ratified architecture and DMAIC domain, user reviews and corrects with Black Belt expertise. Ratified dataset goes to Claude Code alongside other deliverables.

**Sequencing rationale:** current Agent Improve is not production-ready — establishing a quality baseline against a broken system gives a baseline of "bad." The eval suite becomes critical when coaching agent, retrieval tools, and grader middleware are wired — that's when output quality changes. Infrastructure refactor steps (graph structure, state schemas, checkpointer) don't affect coaching quality.

**Minimum viable eval suite ratified:**

- 20-30 examples across all five DMAIC phases (4-6 per phase)
- Five categories: realistic coaching turns, edge cases, tool-calling scenarios, failure/ambiguous cases, historical production data (once available)
- Five metrics: accuracy (field extraction), relevance (coaching alignment), reasoning quality (explanation depth), tool usage (correct invocation), safety (no invented methodology)
- Evaluators ordered by cost: deterministic field extraction ($0) → LLM-as-judge coaching relevance (~$0.01/example) → LLM-as-judge reasoning quality (~$0.02/example)
- Regression threshold: block release if any metric drops >10% from baseline
- Run frequency: every commit that touches system prompts, graph structure, or model config
- Total cost per run: ~$0.60 for 20 examples

**Eval dataset creation is a separate deliverable from this review** — scheduled as a dedicated session after EDUCATIONAL.md review is complete, when the full architectural picture is available. Output format: JSON or Python file ready for LangSmith's `create_dataset` API.

**Connection to §42 grader rubrics:** the eval dataset and the phase rubrics are complementary but different. Rubrics define what "good" looks like for the grader middleware (runs in production, every gate). The eval dataset tests whether the whole system (coach + retrieval + grader + validation) produces good outcomes (runs in CI/CD, every commit).

---

## Category G — Frontend and User Experience

### §77 — AgentLean Frontend Feedback Requirements

**Status:** No decision needed. Six UI patterns documented as frontend requirements. All data points already produced by the agent architecture (completeness_score, captured_fields, current_phase, gate_passed, LangSmith run ID, node execution events via SSE). The frontend surfaces what the agent already knows.

Minor correction at batch commit: Pattern 3 references "Gap 21's feedback adaptation signal" — likely a mis-reference to §40 feedback adaptation (deferred to §87). Correct the cross-reference.

MCP-related content in §78 (menu item 3 "Start MCP server") stripped per §39 MCP-out decision.

---

## Category H — Governance, Skills, Hooks, and Anti-Drift

### §24 — Governance and Debugging — Production Readiness Framework

**Status:** No decision needed. Correct and well-aligned with ratified architecture. Node risk classification (consequence severity + reversibility) is the principled basis for interrupt placement — preserved. Four-part audit answer (what, why, who approved, when) maps to `step_log`, grader `on_evaluation` callback, and LangSmith traces.

§25 (Gap Register) immediately follows §24. Needs comprehensive update at batch commit to reflect current gap status across the entire review. Many gaps now closed (15, 16, 17, 19, 22, 23, 27, 29), several revised. Housekeeping task, not a section-by-section review item.

### §26 — Orion Intelligence — Graded Assignment Submission

**Status:** No decision needed. Course assignment record. Historical documentation of where architectural thinking started. Four guarantees correctly map to ratified architecture (checkpointing, HITL, auditability, modular subgraphs).

Two superseded points noted for batch commit:
- `InMemorySaver` for dev → superseded by phased checkpointer decision (Azure Blob during refactor, PostgreSQL post-refactor)
- Flat supervisor/worker → superseded by recursive Planner-Executor pair (§5/§20)

### §45 — Anti-Drift Governance Design — Hooks, Skills, and Staying Current

**Status:** No decision needed. All four mechanisms implemented and verified (Gap 27 CLOSED, commits 0.5.0–0.5.5, smoke tested 2026-07-03).

Batch commit tasks:
- Update DEPRECATED_PATTERNS YAML registry with additional deprecated patterns identified during this review: `MultiQueryRetriever`, `EnsembleRetriever`, `OutputFixingParser`, `ConversationSummaryMemory`, `ConversationEntityMemory`, `VectorStoreRetrieverMemory`, `create_react_agent`, `from langgraph.prebuilt import`
- Update §45's forum monitoring source table to reference the trusted sources table ratified in this review rather than maintaining a separate list
- §86 (Path A, forward-referenced from §45) to be authored at batch commit documenting full verified hook mechanics

### §50 — CRITICAL VERSION CORRECTIONS

**Status:** No decision needed. Every correction already addressed through ratified decisions:
- Deprecated memory classes → Checkpointer + BaseStore split (§52)
- `create_react_agent` → `create_agent` (§42/§48 middleware architecture)
- Verify before migrating → `/verify-current-version` skill (§45, Gap 27 CLOSED)

Batch commit: add note "All corrections addressed in ratified architecture. See §36, §42, §52."

### §78 — Menu-Driven Developer Orchestration

**Status:** Ratified. Build alongside eval suite as an early refactor task (~30 minutes). Replaces destructive `start.ps1`.

Updates per ratified decisions:
- Remove MCP server menu option (§39 MCP-out)
- Add "Run evaluation suite" option (§75)
- `check_prerequisites()` env var list matches actual Agent Improve requirements

### §83 — Agent Skills Specification — SKILL.md Standard

**Status:** Ratified this session. Each DMAIC phase becomes a skill following the agentskills.io SKILL.md standard.

Five phase skills under `agent-improve/skills/`:
```
dmaic-define-phase/SKILL.md
dmaic-measure-phase/SKILL.md
dmaic-analyse-phase/SKILL.md
dmaic-improve-phase/SKILL.md
dmaic-control-phase/SKILL.md
```

Each skill's `allowed-tools` lists the phase-specific computation tools plus the universal eight — matching per-phase tool binding (§39).

Storage backend: `FilesystemBackend` — git-versioned alongside code. `ContextHubBackend` (LangSmith) deferred to multi-deployment stage.

Progressive disclosure ratified:
- Level 1 (startup): skill descriptions only, under 2K tokens for all five
- Level 2 (on demand): full phase instructions loaded when coach enters that phase
- Level 3 (on demand): reference files loaded when explicitly needed

Skills authored as part of the refactor — each contains phase coaching instructions, phase rubric (§42), phase-specific computation tools list, coaching strategy guidance. To be drafted in this claude.ai project alongside the eval dataset.

### §84 — SkillsMiddleware in deepagents

**Status:** Ratified this session. Same Option B approach as §42 — custom `DMAICSkillsMiddleware` on `create_agent` hooks, not deepagents adoption.

Implementation: reads SKILL.md frontmatter at startup (Level 1), registers `load_skill(name)` as a tool the coach can call (Level 2 on demand). Same progressive disclosure pattern as §83, implemented as middleware.

When deepagents reaches 1.0, migrate from custom middleware to official `SkillsMiddleware` — same migration path as §42's `DMAICGraderMiddleware` → `RubricMiddleware`.

**Complete coach middleware stack ratified for the refactor (four middlewares):**

| Middleware | Source | Purpose |
|---|---|---|
| `DMAICSkillsMiddleware` | Custom (§83/§84) | Progressive disclosure of phase coaching instructions |
| `DMAICGraderMiddleware` | Custom (§42/§48) | Per-criterion quality evaluation against phase rubrics |
| `SummarizationMiddleware` | LangChain core (§36) | Context compression for long coaching sessions |
| `before_model` state injection | Custom (§38) | Prepend structured project state early in prompt |

All four wired via `create_agent(middleware=[...])`. Three are custom (migrate to deepagents when it reaches 1.0), one is LangChain core (stable).

**Category H complete.**

---

## Category I — Course-Specific Concepts

**No sections to review.** The topic index lists §25 as "Actor-Critic Pattern" with sub-items 25a and 25b, but actual §25 in the file is the Gap Register (covered under §24). Items 25a and 25b are sub-entries inside Gap 25, not standalone sections. The Actor-Critic content referenced in the index was never written as a section.

Added to cross-cutting index corrections: §25 index entry is mislabeled (claims "Actor-Critic Pattern", actual content is "Architectural Gaps — Complete Register"). 25a and 25b are not sections.

**Category I complete — no decisions needed.**

---

## Remaining Category A and B sections — batch assessment

### §1 — LangGraph Persistent Checkpointing

**Status:** Aligned with ratified architecture. Stale parts need batch-commit update.

Updates needed:
- Storage backend table: "Custom Blob Saver — Ruled out, too much custom code" → incorrect, `AzureBlobCheckpointSaver` exists and is working (commits 2.1–2.2). Update table to show Azure Blob as transitional, PostgreSQL as post-refactor target (per phased checkpointer decision).
- "Current Gap" paragraph: "no checkpointer wired into workflow.compile()" → closed by commits 2.1–2.2. Update to reflect current state.
- Fail-fast environment validation subsection: correct, useful, aligns with §78 developer menu. Preserve.
- `@traceable` decorator subsection: valuable, preserve as-is. Add note to apply `@traceable` to all custom validation functions from the four-layer stack (§68).
- LangSmith diagnostic patterns: valuable, preserve. P50/P99 latency guidance directly connects to §75 evaluation.

No decision needed.

### §10 — Subagent State Management

**Status:** Fully aligned. Pattern 2 (private subagent state + shared parent state) is exactly what we ratified in §17 (SupervisorState) and §18 (PhaseState).

Three rules match our ratified design:
- Rule 1 (parent owns conversation) → SupervisorState owns `messages`
- Rule 2 (subagents own phase fields) → PhaseState owns `artifacts`, `draft`, `feedback`
- Rule 3 (typed schemas for communication) → boundary mappers (§19/§23)

`MessagesState` vs explicit `TypedDict` guidance preserved: use `TypedDict` for DMAIC phase states (structured field containers), `MessagesState` only for debate subgraph (§22, if implemented in v2.2).

"Current Gap" paragraph ("Agent Improve uses flat shared state — Pattern 1") → to be updated at batch commit: "refactor targets Pattern 2, ratified in §17/§18."

No decision needed.

### §11 — Recursive Planner/Executor — Every Level Plans

**Status:** Aligned with §5/§20 ratification. Three levels (Supervisor Planner → Phase Planner → Tool Executor) match our ratified Planner-Executor cascade.

Per-phase tool diagram at the bottom is an early version of §39's ratified per-phase binding. Tool names need updating to ratified names at batch commit:
- "RAG tool" → `rag_lookup_methodology` / `rag_lookup_evidence` / `rag_lookup_case_history`
- "sigma calc tool" → `calculate_sigma_level` (and other Measure computation tools)
- "fishbone tool" → not a computation tool; this is a coaching template, not a tool call
- "hypothesis tool" → `t_test`, `chi_square_test`, etc. (Analyse computation tools)
- "control plan tool" → `xbar_r_chart_limits`, `p_chart_limits`, etc. (Control computation tools)

The "Across Multiple Weeks — Continuity" subsection correctly describes the cross-session resume pattern. Update "blob (now) and checkpointer (future)" to reflect current state: "AzureBlobCheckpointSaver (refactor phase), PostgresSaver (post-refactor)."

No decision needed.

### §43 — Common Agent Roles and Responsibilities

**Status:** Partially addressed by ratified decisions. One role deferred to §87.

| Role | §43 Status | Current ratified state |
|---|---|---|
| Coordinator | "exists implicitly" | Ratified as Global Planner + Global Executor (§5/§20) |
| Decision Agent | "MISSING" | **Partially closed** — `DMAICGraderMiddleware` (§42) + four-layer validation (§68) implement the quality-evaluation role. Conflict resolution (§38 mid-phase auto-flag) implements the conflict role. |
| Observer Agent | "MISSING" | **Deferred to §87** — system-wide monitoring agent (completion rates, coaching quality drift, system health) is not a per-project coaching component. Not in refactor scope. |
| Worker | "exists" | Ratified as phase subagents with Planner-Executor pairs (§5/§20/§23) |

Gap 24 update at batch commit: partially closed (Decision Agent role distributed across grader + validation stack + conflict detection). Observer Agent deferred.

**Adding to §87 backlog (row 14):**

| # | Source | Deferred capability | Why deferred | Promotion trigger |
|---|---|---|---|---|
| 14 | §43 | Observer Agent — system-wide monitoring across all Belts and projects (completion rates, coaching quality drift, system health, pattern detection) | Not a per-project coaching component; requires production traffic across multiple projects to produce meaningful patterns | Multiple concurrent DMAIC projects in production generating enough traffic for pattern analysis |

### §44 — Consolidated Architecture Diagnosis — Agent Resolve Benchmark

**Status:** Reviewed and reconciled this session. The foundational refactor blueprint. Mostly aligned with ratified decisions; one significant correction (thread_id model), two adoptions, several stale points.

**Web-verified this session (Tier 1 sources):**

- LangChain support docs (`support.langchain.com`): *"When using subgraphs, only the parent graph should have a checkpointer to avoid duplicate storage and state persistence issues."*
- DeepWiki source analysis (`deepwiki.com/langchain-ai/langgraph`): *"All checkpoints for both the parent and all subgraphs share the same thread_id but differ in checkpoint_ns."* And: *"When [checkpointer is] None, the subgraph checkpoint writes go through the same BaseCheckpointSaver as the parent, distinguished by checkpoint_ns."*
- LangChain persistence docs (`docs.langchain.com/oss/python/langgraph/persistence`): *"When a subgraph updates state, the parent graph may not see the changes immediately. This is because each subgraph manages its own checkpoint namespace. Fix: Use shared state via Store for data that needs to cross graph boundaries."*

**CORRECTION — §44's per-subgraph thread_id architecture (Option A) is WRONG.**

§44 lines 4341–4397 state each subgraph should get its own thread_id (`IMPR-2026-E9D-define`, `IMPR-2026-E9D-measure`). This is incorrect per official documentation verified today:

- One checkpointer on the parent graph ONLY — subgraphs compiled WITHOUT a checkpointer
- One thread_id per project (`IMPR-2026-FS1`)
- LangGraph automatically manages checkpoint_ns — each subgraph gets its own namespace within the shared thread_id
- Interrupts inside subgraphs work correctly via the parent's checkpointer, namespaced by checkpoint_ns
- Per-subgraph thread_ids would cause duplicate storage and state persistence issues

This is the third time in this review the per-subgraph thread_id model was corrected (first in §23, then §19, now §44). The correct model is definitively settled:

```
One project thread_id: "IMPR-2026-FS1"
One checkpointer: on parent graph only
Auto checkpoint_ns: LangGraph manages per-subgraph namespacing
Store: cross-phase artifacts via AzureBlobStore (→ PostgresStore post-refactor)
```

§44's Option A text must be rewritten at batch commit to reflect the correct mechanism.

**Full reconciliation table:**

| §44 claim | Status |
|---|---|
| Static edges for DMAIC phase sequence | **Correct — ADOPT.** Global Planner is deterministic logic reading `gate_passed` flags, not an LLM call. `add_edge("define", "measure")` etc. Command routing reserved for inside phases. |
| Command routing inside phases | **Correct — already ratified** |
| Per-subgraph thread_ids (Option A) | **WRONG — correct to one thread_id + auto checkpoint_ns.** Web-verified against Tier 1. |
| Shared key names (Mechanism 1) for boundary crossing | **Compatible with ratified design.** Use alongside store: shared keys for in-graph communication, store for durability and cross-case retrieval. |
| Explicit transformer functions (Mechanism 2) for boundary crossing | **Compatible.** Our boundary mappers (§19) are the same concept. |
| Two-node HITL pattern (review_node → apply_decision_node) | **Refinement — ADOPT.** More precise than §2's current framing. |
| InMemorySaver for dev / PostgresSaver for production | **Stale.** Superseded by phased checkpointer decision: AzureBlobCheckpointSaver during refactor, PostgresSaver post-refactor. |
| Typed Pydantic boundary outputs (DefineOutput, MeasureOutput) | **Correct — already ratified** in §18 |
| Prompt sequencing vs real nodes decision test | **Correct.** Phases unambiguously need full subgraph nodes (failure modes, quality gates, HITL, different tools). |
| Command(graph=Command.PARENT) for subgraph-to-parent routing | **Correct — preserve** as reference. |
| Send API for dynamic parallel worker creation | **Correct — preserve** as reference for future debate subgraph (§22, v2.2). |
| Static vs dynamic routing decision criterion | **Correct — preserve.** "Could this transition vary at runtime?" = dynamic. "Always exactly once in this order?" = static. |
| Don't mix static edges and Command from the same node | **Critical rule — preserve.** Both paths execute silently if mixed. |
| Root cause analysis (four reasons for architectural debt) | **Correct — preserve.** Still the foundational diagnosis. |
| Three governance layers (constitution → skills → hooks) | **Correct — already implemented** (§45, Gap 27 CLOSED) |
| Division of labor (Claude.ai for architecture, Claude Code for implementation) | **Correct — matches project instructions** |
| MCP references (Context7, GitHub MCP, Playwright) | **Out of scope** per §39. Strip from governance layers, keep as knowledge. |
| Course lab case study (failed subgraph demo) | **Correct — valuable warning.** Preserve as documentation of what NOT to copy from the course. |

**Two adoptions from §44 into the ratified architecture:**

1. **Static edges between phase subgraphs.** The top-level DMAIC orchestrator uses `add_edge("define", "measure")`, `add_edge("measure", "analyse")`, etc. — deterministic, no LLM call. Command-based dynamic routing only inside phase subgraphs where step order is data-dependent. This sharpens §5's Global Planner: it's not an LLM reasoner for phase sequencing — it's a deterministic gate-checker.

2. **Two-node HITL pattern.** Refine §2's nine-step flow: step 3 (interrupt fires) is `gate_review_node` which fires the interrupt and presents fields to the Belt. Steps 5-7 (Belt edits, policy advisory, Belt approves) are processed by `gate_apply_node` which reads the Belt's response, applies corrections, runs the policy advisory, and Commands to the next step or back to the grader. Cleaner separation of collection vs application.

**§44 rewrite plan at batch commit:**

1. Correct Option A (per-subgraph thread_ids) → one project thread_id + auto checkpoint_ns
2. Update checkpointer references (InMemorySaver → phased approach)
3. Strip MCP references from governance section, keep as knowledge
4. Update tool names throughout to ratified canonical names
5. Cross-reference to all ratified decisions that implement §44's concepts
6. Preserve the root cause analysis, governance layers, course lab case study, Command pattern, static-vs-dynamic criterion, and boundary contract sections — all correct and valuable

---

## ═══════════════════════════════════════════════════════════
## EDUCATIONAL.md REVIEW — COMPLETE
## ═══════════════════════════════════════════════════════════

**All 85 sections reviewed.** Every section has been assessed, ratified, corrected, or confirmed aligned. The decision log is the complete record of all changes to be applied.

**Final statistics:**
- Sections with ratified changes: §2, §5, §8, §16, §17, §18, §19, §20, §21, §23, §27, §29, §32, §33, §34, §35, §36, §37, §38, §39, §40, §42, §44, §48, §49, §51, §54, §63, §68, §69, §71, §78, §83, §84
- Sections confirmed aligned (batch-commit housekeeping only): §1, §10, §11, §24, §43, §50, §53, §55, §56, §70, §72, §79, §80, §81, §82
- Sections reduced to knowledge-only: §35, §57, §58, §59, §60, §61, §62, §64, §65, §74, §76, §85
- Sections no changes needed: §25 (Gap Register — comprehensive update at batch commit), §26 (course assignment record), §45 (implemented, Gap 27 CLOSED), §73 (keep LangSmith), §77 (frontend requirements)
- New sections to author: §86 (Verified Claude Code Hook Mechanics), §87 (Deferred Backlog — 14 items), Terminology Reference (position before §1)
- File rename: EDUCATIONAL.md → REFACTORING_AGENT_IMPROVE.md

**Next steps (per the log header):**
1. ✅ EDUCATIONAL.md review — COMPLETE
2. Batch commit EDUCATIONAL.md → REFACTORING_AGENT_IMPROVE.md via Claude Code
3. Ground-up rewrite of CLAUDE.md (v2.1 → v2.2) and ARCHITECTURE.md (v2.1.1 → v2.2)
4. Agent Improve codebase refactor executes against new v2.2 governance docs
5. Follow-up deliverables: eval dataset (joint exercise), DMAIC phase skills (five SKILL.md files), AGENT_DESIGN_GUIDELINES.md (separate cowork with weekly-update skill)

---

## §33 Compliance Audit — REFACTORING_AGENT_IMPROVE.md vs Tier 1 sources

**Date:** 2026-08-11  
**Scope:** §33 canonical `rag_lookup_methodology` implementation reviewed against LangChain 1.x API docs, GitHub issues, and actual `improve_knowledge_index` data. Three findings.

---

### Finding §33-A — Bug: `phase_relevance eq 'all'` (Critical — blocks Step 3.1)

**Status:** Confirmed bug. Fix ratified.

The §33 canonical implementation uses:
```python
f"phase_relevance eq '{phase}' or phase_relevance eq 'all'"
```

`'all'` is wrong. DECISIONS.md §E3 records confirmed index data: 218 documents carry `phase_relevance = 'general'`; no document carries `'all'`. Using `'all'` silently returns zero cross-phase documents — the OR clause is defeated. The section note "Confirm the exact enumeration of `phase_relevance` values in the index before implementing" was an open placeholder. That placeholder is now closed: the confirmed value is `'general'`.

**Ratified fix:** Replace `'all'` with `'general'` throughout all three `rag_lookup_*` tool implementations and all REFACTORING cross-references.

```python
# Wrong (§33 current):
f"phase_relevance eq '{phase}' or phase_relevance eq 'all'"

# Correct:
f"phase_relevance eq '{phase}' or phase_relevance eq 'general'"
```

**Propagation required:**
- REFACTORING_AGENT_IMPROVE.md §33 canonical implementation (line ~3863)
- REFACTORING_AGENT_IMPROVE.md §37 implementation note (line ~3721+)
- REVIEW_DECISIONS.md §37 ratified filter clause (line ~1323) — same `'all'` placeholder
- DECISIONS.md §E3 already records the correct value (no change needed there)

---

### Finding §33-B — API Gap: `search_kwargs` filter at invoke time (High — blocks Step 3.1)

**Status:** Confirmed gap. Fix ratified.

The §33 canonical implementation assumes:
```python
azure_search_retriever.invoke(
    q,
    search_kwargs={"filters": f"phase_relevance eq '{phase}' or phase_relevance eq 'general'"},
)
```

This pattern is incorrect for `AzureAISearchRetriever`. The `search_kwargs=` keyword at invoke time is the `AzureSearchVectorStoreRetriever` interface (vectorstore path). `AzureAISearchRetriever` takes `filters` as a **constructor parameter**. Passing it via `search_kwargs` at invoke time is either silently ignored or causes a kwarg collision.

Verified against:
- GitHub discussion [#29756](https://github.com/langchain-ai/langchain/discussions/29756) — "Azure Search Service Metadata-Based Filtering for Vector Search in Langchain not working"
- GitHub issue [#21492](https://github.com/langchain-ai/langchain/issues/21492) — "`search_kwargs` not being used in vectorstore as_retriever"
- GitHub issue [#14227](https://github.com/langchain-ai/langchain/issues/14227) — "Filters dont work with Azure Search Vector Store retriever"
- GitHub issue [#30482](https://github.com/langchain-ai/langchain/issues/30482) — "AzureSearch: got multiple values for keyword argument 'filter'"

Since `phase` is dynamic (varies per tool call), the filter must be set at construction time, and the retriever **cannot be a module-level static variable** for `rag_lookup_methodology`.

**Ratified fix:** Instantiate `AzureAISearchRetriever` per tool call with `filters=` in the constructor.

```python
from langchain_community.retrievers import AzureAISearchRetriever

@tool
def rag_lookup_methodology(query: str, phase: str, top_k: int = 10) -> list[Document]:
    """Multi-query RAG lookup with Reciprocal Rank Fusion against
    improve_knowledge_index (LSS Black Belt eBook). Filters by phase_relevance
    to scope results to the current DMAIC phase. Uses the content_vector field."""
    variants = llm.with_structured_output(QueryVariants).invoke(
        f"Generate 3-5 alternative phrasings for retrieving DMAIC {phase} "
        f"content on: {query}. Include synonyms, related terminology, and "
        f"phrasings a Black Belt would use in the LSS Black Belt eBook."
    )
    retriever = AzureAISearchRetriever(
        service_name=settings.AZURE_SEARCH_SERVICE_NAME,
        index_name="improve_knowledge_index",
        content_key="content",
        top_k=top_k * 3,  # over-fetch per variant; RRF selects final top_k
        filters=f"phase_relevance eq '{phase}' or phase_relevance eq 'general'",
    )
    ranked_lists = [retriever.invoke(q) for q in variants.queries]
    fused = reciprocal_rank_fusion(ranked_lists, k=60)
    return [doc for doc, _score in fused[:top_k]]
```

The same applies to `rag_lookup_evidence` (filter: `case_id eq '{case_id}'`) and `rag_lookup_case_history` (filter: `status eq 'completed'`). Each creates its retriever per call with the appropriate filter.

Note: `AzureAISearchRetriever` is a thin wrapper — construction cost is negligible vs the network call. No connection pooling concern.

**Propagation required:**
- REFACTORING_AGENT_IMPROVE.md §33 canonical implementation — replace `azure_search_retriever.invoke(q, search_kwargs=...)` pattern with per-call constructor pattern
- REFACTORING_AGENT_IMPROVE.md §32 multi-query sketch (if it also uses the module-level pattern) — same fix
- REFACTORING_AGENT_IMPROVE.md §40 — `rag_lookup_evidence` and `rag_lookup_case_history` filter patterns

---

### Finding §33-C — Open question resolved: `azure_search_retriever` module-level variable (Medium)

**Status:** Open question from §32 review now closed.

REVIEW_DECISIONS.md §32 left open (line ~961): "Confirm `azure_search_retriever` module-level exposure in current codebase (or adjust reference implementation)."

**Resolution: adjust reference implementation.** Finding §33-B makes this definitive — a module-level retriever pre-configured with a static filter cannot support the dynamic `phase` parameter in `rag_lookup_methodology`. The retriever is created per call. This also means the current codebase's `azure_search_retriever` variable (however it is defined) is incompatible with the dynamic-filter design; Step 3.1 should not inherit or reuse it.

---

### §33 — What is confirmed valid

No changes to:
- `reciprocal_rank_fusion()` custom implementation — correct, keep as-is. Verified
  against trusted sites 2026-08-11: `EnsembleRetriever` is NOT deprecated (it lives
  in `langchain.retrievers.ensemble`, active in v0.3), but it solves the **wrong problem**.
  `EnsembleRetriever` combines results from multiple different retriever sources (BM25 + vector).
  Our pattern is same-index multi-query RRF — N phrasings against one index. No standard
  LangChain 1.x class does this. The LangChain rag-fusion template (v0.2) also used a custom
  implementation. The custom 15-line approach is correct, stable, and dependency-free.
  Anthropic "Writing Tools for Agents" (Tier 1) confirms encapsulation principle — complexity
  inside the tool, clean interface to the agent.
- `k=60` — standard RRF choice
- `doc.metadata["id"]` as dedup key — correct for Azure AI Search index schema
- `phase` as a tool parameter — correct design; executor specifies current DMAIC phase per turn
- `llm.with_structured_output(QueryVariants).invoke(...)` — correct §82 ProviderStrategy pattern
- RRF included by default — correct rationale (Agent Resolve empirical override stands)

**Correction to prior framing:** DECISIONS.md §E1 previously stated `EnsembleRetriever` was
"banned — moved to langchain-classic in the 1.0 namespace split." This is factually wrong.
`EnsembleRetriever` is active and not deprecated. Correct reason for not using it: wrong
pattern for same-index multi-query fusion. DECISIONS.md §E1 updated 2026-08-11.

---

### Propagation to REFACTORING_AGENT_IMPROVE.md

**Before Step 3.1 can build `tool_args.py`, apply:**
1. §33-A fix (`'all'` → `'general'`) to §33 canonical implementation
2. §33-B fix (per-call constructor pattern) to §33 canonical implementation
3. Same two fixes to §37 and §40 implementation notes
4. §33-C close note — add a sentence resolving the "Confirm `azure_search_retriever`" open question

These are doc amendments, not ratification decisions — the three-tool architecture and RRF inclusion remain unchanged. The two fixes correct implementation details in the reference code.

*Cross-references: DECISIONS.md §E3 (phase_relevance values confirmed); §32 (multi-query tool parent); §37 (phase_relevance filter ratification); §40 (metadata filters on the other two tools); Step 2.5 (dependency upgrade before Step 3.1); REFACTORING_AGENT_IMPROVE.md §33 lines 3858–3870.*

---

### §53 — MAJOR FINDING — Built-In Middleware Replaces Most of Gaps 2, 19, and Part of 23

**Status:** Confirms our ratified approach. No decision needed.

Key findings from §53 that validate our decisions:
- `SummarizationMiddleware` exists as built-in → we ratified it in §36
- `HumanInTheLoopMiddleware` exists but has confirmed bugs: edit/reject broken in subgraph contexts, only approve reliable → validates our approach of building HITL interrupts directly in the graph (§2) rather than through the middleware
- `RubricMiddleware` requires `create_deep_agent` → validates our §42 Option B decision (custom `DMAICGraderMiddleware` on `create_agent`)

§53's Bug documentation (Gap 32) is important safety information: do NOT rely on `HumanInTheLoopMiddleware` for edit/reject in subgraph contexts. Our nine-step HITL pattern (§2) avoids this bug by using graph-level interrupts + Command(resume=...) rather than middleware-level HITL.

### §70 — Inter-Stage Data Dependency — Outputs Become Inputs

**Status:** Confirms store-mediated handoff. No decision needed.

§70 describes how Define's outputs (problem statement, baseline metric) become Measure's required inputs. This is exactly the AzureBlobStore boundary mapper pattern ratified in §19/§23: Define writes to `store.put(("projects", project_id, "artifacts"), "define", {...})`, Measure reads via `store.get(...)`.

Batch commit: update §70 to reference the ratified store-mediated pattern rather than describing it as a future design.

### §79 — LangGraph 1.2 Native Reliability Primitives

**Status:** Already ratified in Category D. Per-node timeouts, error handlers, graceful shutdown adopted. DeltaChannel deferred to §87 (item 12).

No additional action.

### §80 — LangChain 1.0 AgentMiddleware — The Six Hooks Foundation

**Status:** Foundation reference for our entire middleware stack. No decision needed.

Documents `before_agent`, `after_agent`, `before_model`, `after_model`, `wrap_model_call`, `wrap_tool_call`. Our four ratified middlewares (§42 DMAICGraderMiddleware, §84 DMAICSkillsMiddleware, §36 SummarizationMiddleware, §38 before_model state injection) all depend on these hooks.

Preserve as-is. Cross-reference to the complete middleware stack table in the §84 log entry.

### §81 — LangChain 1.0 Standard Content Blocks — Typed Model Responses

**Status:** Foundation reference. No decision needed.

Documents `AIMessage`, `HumanMessage`, `ToolMessage` with structured content blocks. Foundational for understanding how LangGraph nodes communicate via messages. Preserve as-is.

### §82 — LangChain 1.0 ProviderStrategy — Native Structured Output

**Status:** Already referenced throughout the review. No decision needed.

Documents `with_structured_output(Schema)` — the pattern used in every ratified tool signature (§32/§33 query variant generation, §42 grader verdict, §48 gate validator, §68 constraint checker). This is the canonical structured-output mechanism that replaced `OutputFixingParser` (§29).

Preserve as-is. Confirm at batch commit that the installed `langchain` version supports all four strategies (ToolStrategy, ProviderStrategy, NativeStrategy, AutoStrategy).

---

## REVIEW STATUS — NEAR COMPLETE

**All categories reviewed except one section:**

| Category | Status |
|---|---|
| A — Foundations | **Complete** (§1, §2, §10, §52 reviewed; §44 flagged for dedicated review; §53, §79, §81 confirmed) |
| B — Orchestration | **Complete** (§5, §11, §17–§21, §23, §27, §43 reviewed; §44 flagged; §70, §80, §82 confirmed) |
| C — Reasoning/Reflection | **Complete** |
| D — Reliability/Recovery | **Complete** |
| E — MCP | **Complete** |
| F — Deployment/Infrastructure | **Complete** |
| G — Frontend | **Complete** |
| H — Governance/Anti-Drift | **Complete** |
| I — Course Concepts | **Complete** (index mislabel, no actual sections to review) |

**Single remaining item: §44 — Consolidated Architecture Diagnosis — Agent Resolve Benchmark.**

This is the full refactor blueprint. Requires dedicated review to reconcile against all ratified decisions. Once §44 is reviewed and ratified, the EDUCATIONAL.md review is complete and the batch commit can proceed.

---

## Sections confirmed aligned — no changes beyond batch-commit housekeeping

§1 (update stale parts), §10 (confirm alignment), §11 (update tool names), §53 (validates our approach), §70 (confirms store pattern), §79 (already ratified in Cat D), §80 (foundation reference), §81 (foundation reference), §82 (already used throughout)

---

### §42 — RubricMiddleware — Self-Evaluation and Correction Loop

**Status:** Ratified this session. Option B selected — custom `DMAICGraderMiddleware` on `create_agent` hooks, not deepagents adoption.

**Web-verified (2026-07-30):**

- deepagents is pre-1.0 (stable: 0.6.10, alpha: 0.7.0a7). From GitHub issue #4219 (June 24, 2026): *"APIs may still evolve between minor versions."* Breaking changes shipping weekly in 0.7 alpha line.
- RubricMiddleware requires `create_deep_agent`, not `create_agent`. Confirmed across all Tier 1 documentation pages.
- `create_agent` has the same six middleware hooks (`before_agent`, `after_agent`, `before_model`, `after_model`, `wrap_model_call`, `wrap_tool_call`) that RubricMiddleware uses internally. Custom middleware on `create_agent` is the GA-stable equivalent.
- LangChain ecosystem hierarchy (from deepagents README): *"LangGraph is the graph runtime. LangChain's create_agent is a minimal agent harness on top of it. Deep Agents is a more opinionated harness on top of create_agent."* And: *"Use create_agent when you want a lighter harness without the bundled middleware."*
- Anthropic's own guidance (`anthropic.com/research/building-effective-agents`): *"find the simplest solution possible, and only increase complexity when simpler approaches fall short."*

Sources: `reference.langchain.com/python/deepagents/middleware/rubric/RubricMiddleware`, `docs.langchain.com/oss/python/deepagents/rubric`, `github.com/langchain-ai/deepagents/issues/4219`, `github.com/langchain-ai/deepagents/releases`, `langchain.com/blog/introducing-rubrics-for-deepagents`, `anthropic.com/research/building-effective-agents`

**Decision 1 — Option B: custom DMAICGraderMiddleware on create_agent.**

Rationale:
- deepagents pre-1.0 with breaking changes still shipping — incompatible with end-of-August production target
- Adopting deepagents brings filesystem tools, sub-agent spawning, code interpreter, harness profiles — unused machinery that conflicts with our ratified create_agent architecture
- create_agent's middleware hooks are GA and stable — same hook interface RubricMiddleware uses internally
- Implementation cost difference is ~1 day (3-4 days vs 2-3 days)
- Clean migration path: when deepagents reaches 1.0, migrate from custom middleware to official RubricMiddleware — same hooks, near-drop-in replacement

Risk assessment for end-of-August timeline:
- Option A (deepagents 0.6.10): workable if pinned strictly, but carrying unused machinery and betting no critical fix ships in 0.7/1.0 before August
- Option B (custom middleware): zero dependency risk, full control over API surface
- If timeline were end of Q4, would flip to Option A — deepagents 1.0 would likely be out by then

**Decision 2 — Grader and policy advisory are BOTH kept, at different positions in the flow.**

The grader checks the AI's work before showing it to the Belt. The policy advisory checks the Belt's edits before committing them. Two different actors (AI vs human) producing output at two different moments — each needs its own quality check.

**Updated §2 HITL gate pattern — now nine steps:**

| Step | What Happens | Quality check for |
|---|---|---|
| 1. Executor runs | Coach produces output + extraction captures fields | — |
| 2. **Grader evaluates** | `DMAICGraderMiddleware` evaluates coach output against phase rubric. If `needs_revision` → per-criterion feedback to coach, retry (cap: 3). If `satisfied` → proceed. Belt does NOT see this loop. | **AI's work** |
| 3. Interrupt fires | Graph pauses; Belt sees grader-approved output | — |
| 4. Belt reviews | Belt checks AI-captured values for accuracy | — |
| 5. Belt edits (optional) | Belt corrects wrong fields directly in Task Plan | — |
| 6. **Policy advisory** | Orchestrator validates Belt's edits against required-field policy, cross-phase consistency, and mid-phase captured_field contradictions (§38 auto-flag). Surfaces structured feedback. Non-blocking — Belt may act on it or override. | **Human's edits** |
| 7. Belt approves | Belt confirms gate ready | — |
| 8. Checkpoint saves | State committed only now | — |
| 9. Next task? | Supervisor routes to next phase or field | — |

**Decision 3 — Five DMAIC phase rubrics ratified (draft, subject to refinement against actual BB content):**

```
DEFINE_RUBRIC = """
- problem_statement: measurable problem with baseline and target (numeric where applicable)
- business_case: quantifiable business impact (cost, quality, delivery, or safety terms)
- project_scope: explicit inclusions and exclusions with process boundaries
- team: Belt, sponsor, and 2+ team members with named roles
- goal_statement: SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
"""

MEASURE_RUBRIC = """
- baseline_mean: numeric value with units
- baseline_sigma: calculated correctly from baseline data
- measurement_system_validated: GR&R or equivalent evidence provided
- data_collection_plan: sample size, frequency, and responsible person named
"""

ANALYSE_RUBRIC = """
- root_causes: identified and prioritized against baseline data
- root_cause_validation: statistical or observational evidence provided (not opinion)
- causal_hypothesis: linked back to captured baseline metric
- ruled_out_causes: alternatives considered and rejected with rationale
"""

IMPROVE_RUBRIC = """
- solution_selected: criteria-based selection documented (impact, effort, risk)
- solution_linked_to_root_cause: explicit mapping from solution to prioritized root cause
- pilot_results: measurable improvement demonstrated with data
- implementation_plan: timeline, responsible person, resource requirements
"""

CONTROL_RUBRIC = """
- control_plan: monitoring frequency, thresholds, and responsible person named
- sustainability_check: process defined for maintaining gains
- post_improvement_metric: measured value showing baseline shift
- handover_documented: process owner accepted responsibility with named individual
"""
```

Rubrics stored as constants; grader receives the phase-appropriate rubric based on `current_phase`. Rubrics can evolve based on production experience without changing the grader mechanism.

**Decision 4 — Iteration cap at 3, temperature discipline ratified.**

- Grader iteration cap: 3. On `max_iterations_reached`, output passes through with a warning flag visible to the Belt. Matches §54's example and deepagents documentation defaults.
- Grader temperature: 0.1 (low — consistent, repeatable evaluation). Same gate document must receive same verdict across runs. Required for regression testing (§75).
- Coach temperature: 0.5–0.7 (moderate — natural language variation in coaching improves Belt experience).
- All extraction nodes and field validators: 0.0–0.2 (same rationale as grader).

**Implementation sketch — DMAICGraderMiddleware:**

```python
from langchain.agents.middleware import AgentMiddleware
from pydantic import BaseModel

class CriterionVerdict(BaseModel):
    criterion: str
    passed: bool
    feedback: str  # empty if passed

class GraderVerdict(BaseModel):
    result: Literal["satisfied", "needs_revision", "failed"]
    criteria: list[CriterionVerdict]
    explanation: str

class DMAICGraderMiddleware(AgentMiddleware):
    def __init__(self, model, max_iterations=3, on_evaluation=None):
        self.grader_llm = model.with_structured_output(GraderVerdict)
        self.max_iterations = max_iterations
        self.on_evaluation = on_evaluation
        self._iteration = 0

    def after_agent(self, state, runtime):
        rubric = state.get("rubric")
        if not rubric:
            return None  # no rubric, no grading

        verdict = self.grader_llm.invoke(
            f"Evaluate the agent's output against this rubric:\n{rubric}\n\n"
            f"Transcript:\n{format_messages(state['messages'])}"
        )
        self._iteration += 1

        if self.on_evaluation:
            self.on_evaluation({"iteration": self._iteration, **verdict.dict()})

        if verdict.result == "satisfied" or self._iteration >= self.max_iterations:
            return None  # pass through

        # Inject per-criterion feedback and signal retry
        failed = [c for c in verdict.criteria if not c.passed]
        feedback = "\n".join(f"- {c.criterion}: {c.feedback}" for c in failed)
        # ... inject as HumanMessage, return control to agent loop
```

Note: this is a reference sketch, not production code. The actual `after_agent` hook mechanics for retry signalling need to match `create_agent`'s specific return-value contract. Verify against `reference.langchain.com/python/langchain/agents/middleware` before implementing.

**Audit trail integration:**

The `on_evaluation` callback writes each grading iteration into `step_log` (§18 PhaseState field). This gives the DMAIC audit trail full visibility into what the grader found, how many iterations ran, and what the final verdict was — without leaking grader internals into the coach's messages or the Belt's view.

**§54 corrections incorporated:**

- Temperature discipline (from §54) ratified as Decision 4 above
- `on_evaluation` callback pattern (from §54) adopted for audit trail
- The `deepagents` dependency concern (from §54) resolved via Option B

**Propagation needed at batch commit:**

- **EDUCATIONAL.md §42 rewrite** — restructure around Option B implementation. Retain pedagogy about per-criterion feedback and LLM-as-a-judge pattern. Retire the `create_deep_agent` code examples. Replace with `DMAICGraderMiddleware` on `create_agent`. Include the five phase rubrics. Cross-links to §2 (nine-step HITL pattern), §29 (superseded by grader for quality evaluation), §48 (reflection nodes — related pattern), §54 (corrections incorporated).
- **EDUCATIONAL.md §54** — mark as incorporated into §42 rewrite. Corrections 1 and 2 from §54 are now reflected in the §42 decision. §54 becomes a historical note pointing to §42.
- **EDUCATIONAL.md §2 update** — replace eight-step table with nine-step table above. Grader is step 2 (pre-Belt); policy advisory stays at step 6 (post-Belt-edit).
- **CLAUDE.md v2.2** — new subsection documenting grader middleware configuration, rubric management, temperature policy, audit trail integration.
- **ARCHITECTURE.md v2.2** — coach subgraph diagram updated to show grader middleware in the agent stack (not a subgraph node — a middleware on the create_agent call). Phase rubrics documented as constants.

**Gap Register:** Gap 23 closes at v2.1 via Option B custom middleware. §42's original "deferred to post-completion refactor" no longer applies.

---

## Review methodology notes

**Observed drift risk (from §20 review — first occurrence).** My first pass at §20 collapsed §5's Planner/Executor split into a "worker + supervisor" fusion. User caught it; corrected framing now recorded. In Claude Code, `/verify-current-version` would have prevented this by mandating a fresh read of §5 before touching §20. In this Project the equivalent discipline is manual: before proposing changes to a section, check the topic-group index at the top of EDUCATIONAL.md for related sections and read them first. Applies to remaining review sessions.

**Observed drift risk (from §23 review — second occurrence).** §19 decision recorded per-phase thread_ids (`IMPR-2026-FS1-define`, `IMPR-2026-FS1-measure`) — Pattern B (separate graph invocations). §23 describes Pattern A (subgraphs embedded in parent), and LangGraph 1.2 docs confirm Pattern A is the native mechanism. Should have cross-read §23 before finalising §19. Second occurrence of the same lesson within one review session — treat this as a warning that the cross-read discipline must be structural, not aspirational. Going forward: before recording a decision on any section that involves state, threading, or subgraph mechanics, sweep at minimum §17, §18, §19, §23, §52 for interaction points.

**On the "reasoning discipline" from Project instructions.** When a decision needs verification against current LangChain/LangGraph/LangSmith/MCP behaviour, web_search before asserting. Done for §52/AzureBlobStore (2026-07 BaseStore API confirmed) and §23 (subgraph thread_id/checkpoint_ns confirmed via LangGraph 1.2.6 release notes and LangChain persistence docs). Should be repeated when reviewing §79 (LangGraph 1.2 reliability primitives), §80–82 (LangChain 1.0 middleware/content blocks/ProviderStrategy), and §83–84 (Agent Skills spec and SkillsMiddleware).

---

## Sections still to review

- Group A remaining: §3, §10, §44, §52, §53, §79, §81
- Groups B–I not yet reviewed

