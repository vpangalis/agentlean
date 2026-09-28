# ARCHITECTURE v2 — gaps found when v1.88 was retired (for Desktop)

> **Brief Part C4, 2026-09-27. A report, not a decision.** When
> [ARCHITECTURE.md](../ARCHITECTURE.md) v2 replaced v1.88 (archived at
> [docs/_archive/ARCHITECTURE_v1.88_2026-09-27.md](_archive/ARCHITECTURE_v1.88_2026-09-27.md)),
> the brief asked for four checks, reporting gaps and moving nothing. ADRs are never edited,
> so a missing rationale needs a new or superseding ADR. § numbers below are v1.88's.

## 1. Banned patterns (old Appendix D.2) against `.claude/config/deprecated_patterns.yaml`

**Five of the roughly 55 banned items are enforced by the registry.** Some others are held by a
test, and the rest by nothing mechanical.

| Group | Banned in D.2 | Enforced by |
|---|---|---|
| Graph | `set_entry_point` | pattern-6 |
| Graph | hand-written Saga / compensation | pattern-4 |
| LLM and tools | binding tools onto a bare model | pattern-8 (`llm.bind_tools(`) |
| LLM and tools | `create_react_agent`; imports from `langgraph.prebuilt` | pattern-1 (only the `create_react_agent` import; other `langgraph.prebuilt` imports pass) |
| LLM and tools | string-indexing raw content | pattern-3 (`response.content[`) |
| State | artifacts on `SupervisorState`; typed computation destinations; checkpointer or store on a subgraph | tests: `test_state.py`, `test_supervisor_graph.py` (not the registry) |
| LLM and tools | more than 16 tools on a phase executor | test: `test_computation.py::test_no_phase_exceeds_the_sixteen_tool_ceiling` |
| Retrieval | bare `except Exception` returning `[]` | test: `test_retriever.py` (no bare except) |
| Governance | renumbering a rule the registry cites | `verify_rule_citations.py` (rule 13) |
| **State** | numeric captured fields · `gate_attempts` in route scope · merging `validator_feedback`/`belt_edits` · merging `issues_and_barriers`/`acknowledged_gaps` · `str`-typed structured dicts · per-phase `thread_id` · `InMemorySaver` (tests use one) · case blob written mid-conversation · cross-phase data via parent state or interpolation · tuples in `step_log` | **nothing** |
| **Graph** | mixing static edges and `Command` · manual node dispatch in routes · `_reflect()` · fusing planner and executor · a node with external writes and no `error_handler` | **nothing** |
| **LLM and tools** | direct `AzureChatOpenAI` · deepagents · parsing JSON from raw text · parameterised computation-tool grouping · `MultiQueryRetriever` · `EnsembleRetriever` · `OutputFixingParser` · `Conversation*Memory` | **nothing** |
| **Validation and gates** | all thirteen items (Tier 1 pass, Tier 2 blocking, dropped gap, DOE to Green Belts, raw output, gate without both writes, grader loop shown, tolerance threshold, capped Level 2, blocking advisory, checkpoint before approval, `HumanInTheLoopMiddleware`, retrieval in gate validation) | **nothing** |
| **Retrieval** | unconditional pipelines · failure read as absence · filtering on `phase` or `'all'` · index writes without `fields=` · `add_texts` without `ids=` · writing Resolve indexes · any MCP dependency · fetching data not uploaded | **nothing** |
| **Prompts and governance** | inline prompts in node files · missing memory hierarchy or anti-hallucination guards · classes outside the allowed files · duplicating `CitationRecord` · disabling LangSmith · methodology jargon in team-facing strings | **nothing** |

The registry also bans patterns D.2 does not list: pattern-2 (`.with_structured_output(`),
pattern-5 (dict routing), pattern-7 (sync `graph.invoke`), pattern-9 (hand-rolled retry),
pattern-10 (custom tracing), pattern-11 (manual persistence), pattern-12 (the retired index).
**Pattern-2 conflicts with v2 §3.4**, which calls builder-style structured output right for
plain calls. Its exclusions carry that scoping, but the message still says "deprecated".

## 2. Rationale in old Parts II–XI that no ADR states

50 sections were checked, excluding §39 and §43 (method). The check found about 190 rationales:
about 25 are in an ADR's Context or Consequences, and about 165 are not, merged into the rows
below. Most § numbers are cited in some ADR's Source line, but the ADRs' one-sentence Context
leaves the reasons out.

| Old § | Rationale (paraphrased) | Closest ADR | Suggested |
|---|---|---|---|
| §5 | `gate_passed` is a dict so lookup and the cascade's reset always work | 0015 | superseding 0015 |
| §5 | `current_phase` / `phase_index` are stored only because they have exactly one writer | 0015 | superseding 0015 |
| §5 | derived values (`dmaic_plan`, …) removed; a new field must name its writer and reader | 0015 | superseding 0015 |
| §6 | `asks` is its own field (not `artifacts["asks"]`, not `PhaseRecord.asks`), for stated reasons | none | new ADR |
| §6 | `field_log` is a third record: a quality system shows revision history | none | new ADR (field_log) |
| §6 | its reducer upserts (a replay must not double-log); the key uses the Belt-message count | none | same |
| §6 | it lives in the case blob beside `structured`, never on a different schedule | none | same |
| §6 | one typed plan, not a queue; `Literal` so a typo cannot fall back silently | 0025 | superseding 0025 |
| §6 | `gate_attempts` on PhaseState and per phase | 0039 | superseding 0039 |
| §6 | `validator_feedback` and `belt_edits` stay separate; the cap of 3 needs accumulated feedback | 0039 | superseding 0039 |
| §6 | `hop_results` / `synthesis_output` are state, not locals (trace, resume) | 0032 | superseding 0032 |
| §6 | an empty `uploads` list is visible evidence of typed-only statements | 0034 | superseding 0034 |
| §6 | no per-phase state classes; explicit TypedDict | 0015 | superseding 0015 |
| §7 | the Belt's exact words; typed numeric and raw/value/unit triple rejected | 0016 | superseding 0016 |
| §7, §42 | reference dicts make the grader's link a lookup; why only `post_improvement_metrics` is Tier 1 | 0016, 0019 | new ADR |
| §7 | computation results in one list; typed fields would duplicate | 0035 | superseding 0035 |
| §8 | checkpointer/store asymmetry is deliberate (structural vs product memory) | 0017, 0019 | superseding 0017 |
| §8 | why Blob over Cosmos/Tables/SQLite; the Postgres move is a constructor change | 0018 | superseding 0018 |
| §8 | the Blob saver is acceptable only before production; Postgres is the concurrency fix | 0018 | new ADR (migration trigger) |
| §9 | the case index stays on AI Search (hybrid, multi-query/RRF), not the Store | 0030 | new ADR |
| §9 | cross-phase data cannot ride parent state (propagation, weeks, restarts) | 0019 | superseding 0019 |
| §9 | `gate_documents` retired; the `case` namespace is a copy | 0019 | superseding 0019 |
| §9 | input mappers depend only on BaseStore; no string interpolation of prior output | 0019 | superseding 0019 |
| §10 | the case blob is not written per turn (in-flight vs committed) | 0038 | superseding 0038 |
| §11 | what vs how (`artifacts` vs `step_log`); dict entries so they are queryable | 0020 | superseding 0020 |
| §13 | the subgraph is a cycle, which is why LangGraph and not a DAG engine | 0022 | superseding 0022 |
| §13 | the planner is the only decision point, so the roles do not fuse | 0025 | superseding 0025 |
| §13 | validation is not a tool; policy advisory lives in `gate_apply` | 0022 | superseding 0022 |
| §14 | nodes are async because per-node timeouts need it | 0043 | superseding 0043 |
| §14 | reflection is a node; invisible retry belongs in middleware | 0022 | superseding 0022 |
| §16 | one id doubles as thread, namespace, blob path and filter | 0024 | superseding 0024 |
| §16 | `subgraph.ainvoke` directly with the inherited config; inside a tool, persistence breaks | none | new ADR |
| §16 | `recursion_limit` fails as a hop cap both ways | 0032 | superseding 0032 |
| §17 | retrieval strategy is decided at plan time | 0025 | superseding 0025 |
| §17 | the node loads an unread upload itself (step 6.21) | none | new ADR |
| §17 | confirmation is a rule; Change is answered in code | 0002 | superseding 0002 |
| §17 | containment on timeout gives the script question, logged as a DEFECT | 0044 | superseding 0044 |
| §18 | deepagents excluded as a dependency risk | 0026 | superseding 0026 |
| §19 | built-in middleware preferred; custom only for domain logic | 0027 | superseding 0027 |
| §19 | the order's reasons (injection outermost, contradiction innermost, coherence inside grader) | 0027 | superseding 0027 |
| §19 | three retry caps never merge; `on_failure="continue"` | 0027 | superseding 0027 |
| §19.1 | composition in `before_agent`; missing fields computed at injection | 0003 | superseding 0003 |
| §19.1 | state at the top (lost when 0003 superseded 0005) | 0003, 0005 | superseding 0003 |
| §19.2, §32 | content is delivered and recorded, never fetched; **0036 conflicts with §19.2** (section vs full SKILL.md) | 0036 | superseding 0036 |
| §19.3 | summarisation is safe only because facts never live in `messages[]` | none | new ADR (context compression) |
| §19.6, §37 | the contradiction middleware only reads a flag (no call, no Store read) | 0042 | superseding 0042 |
| §19.9 | `HumanInTheLoopMiddleware` and `LLMToolSelectorMiddleware` rejected, with reasons | none | new ADR (rejected middleware) |
| §20 | the executor never emits a phase Output per turn | 0028 | superseding 0028 |
| §20, §50.1 | response blocks are schema fields, not prompt hopes | none | new ADR |
| §21 | `max_retries=0` explicitly, or retries multiply | 0029 | superseding 0029 |
| §21 | grader temperature 0.1 keeps the 10% regression threshold meaningful | 0029, 0049 | superseding 0029 |
| §21 | two structured-output mechanisms (agent loop vs none) | 0028 | superseding 0028 |
| §22 | memory hierarchy at prompt level; case history is patterns, not prescriptions | none | new ADR |
| §22 | anti-hallucination guards mandatory; three layers | none | new ADR |
| §23 | one tool per index, fields known locally | 0030 | superseding 0030 |
| §23.1 | eBook-only corpus; `phase_relevance` tagged by model, not keywords | none | new ADR (knowledge corpus) |
| §23.2 | evidence metadata server-set; `description` a projection; phase filter off | none | new ADR (evidence identity) |
| §23.2 | supersession deletes chunks; scoped to (case, role) | none | same |
| §23.2.1 | fixed role vocabulary; kind derived from role; the sentinel; adding a role is governance | none | new ADR (role vocabulary) |
| §24 | RAG is a tool, never a prepended message | 0030 | new ADR |
| §24 | evidence lookup returns structured records | none | new ADR |
| §24 | `AzureSearch` over `AzureAISearchRetriever`; belt-level filter off | 0030 | superseding 0030 |
| §25 | RRF mandatory on Resolve evidence; custom fusion code, for reasons | 0031 | superseding 0031 |
| §26 | the cap is three hops because a hop takes about 9.5 s (resolves 0032's open drift) | 0032 | superseding 0032 |
| §26 | synthesis is a separate call | none | new ADR |
| §26 | gate validation never retrieves | 0039 | superseding 0039 |
| §28 | static procedural memory is invariant; dynamic memory adapts delivery only | none | new ADR |
| §29.1 | no MCP is an exclusion; uploads are the only channel (0034 gives another reason) | 0034 | superseding 0034 |
| §29.2–29.4 | `record_field` retired; `load_evidence_series` universal; cross-agent tools unbound | 0034 | superseding 0034 |
| §30–31 | named tools, not modes; `args_schema` load-bearing; the 16 ceiling has no margin | 0035 | superseding 0035 |
| §32 | `allowed-tools` must match the binding | 0036 | superseding 0036 |
| §33 | the grader blocks, the policy advisory never does (the Belt is the expert) | none | new ADR |
| §33 | gates are one-way doors; the cascade is deliberately heavy | 0042 | superseding 0042 |
| §33.2 | the gate document is written twice; attempts reset only at `gate_apply` | 0011, 0037 | superseding 0037 |
| §34 | 2a middleware vs 2b–2d node; cheapest first; LLM checks see content | 0039 | superseding 0039 |
| §34.2 | only coherence retries silently; coached retries uncapped | none | new ADR |
| §38 | escalation names the unresolved constraints | 0039 | superseding 0039 |
| §35 | tiers so 2b and 2d cannot disagree; blocking everything teaches form-filling | 0040 | superseding 0040 |
| §35 | `issues_and_barriers` required everywhere, distinct from `acknowledged_gaps` | 0040 | superseding 0040 |
| §35, §41 | per-phase tier reasons (Control 3, Improve traceability, DOE for Black Belts) | 0040 | new ADR per phase, or the phase requirements |
| §36 | two graders because failures show at different times | 0041 | superseding 0041 |
| §37 | gate-committed values only; no tolerance threshold; no `HITLInterrupt` | 0042 | superseding 0042 |
| §37, §50 | detection best-effort; the all-gate-fields tab is the backstop | 0042 | superseding 0042 |
| §40 | `phase_metrics` on all five schemas; the metric registry is a string-law exception | 0016 | new ADR (metric registry) |
| §40.1 | assembly access encodes the tier (KeyError vs `.get`) | 0040 | superseding 0040 |
| §41 | SIPOC, detailed map and control plan are dicts so sub-fields are checked | 0016 | superseding 0016 |
| §41 | FMEA excluded from every schema | none | new ADR |
| §44, §45 | the timeout is step 0; error handlers needed for time-travel correctness | 0043 | superseding 0043 |
| §46 | backoff per level; session-scoped cache | 0044 | superseding 0044 |
| §46 | breaker asymmetry; three-state; HTTP 400 not retried | 0044 | superseding 0044 |
| §46.1 | the single region is a DORA launch blocker; the second region must be in the EU | 0045 | superseding 0045 |
| §47 | handler shape decides what survives; Blob lease; sweep excludes paused threads | 0046, 0024 | superseding 0046 |
| §50 | UI rules (marked examples, no jargon, connection status, split bars, contextual spinners) | none | new ADR (UI and language) |
| §50 | the gate document is never assembled from presentation fields | 0028 | superseding 0028 |
| §51 | `@traceable` needed on plain functions; `request_id`; child-only spans (quota) | 0048 | superseding 0048 |
| §52 | eval built alongside; jointly authored | 0049 | superseding 0049 |
| §53 | the dependency floor traces to one release note; verify against live PyPI | 0051 | new ADR (dependency policy) |
| §53 | FastAPI over LangGraph Server (licence) | none | new ADR |
| §53.1 | Option B: rebuild the foundation first | none | new ADR, or history |
| §55 | registry citations must resolve; docs exempt so governance can name what it bans | 0052 | new ADR (pattern registry) |
| §55 | a zero-references sweep ends with raw `grep -rn` | none | new ADR |
| §55.1 | every rule states what catches a violation | none | new ADR |
| §55.2–55.3 | BUILT markers, the board, UNMEASURED is not a pass | none | new ADR (or retire with the markers) |
| §55.4 | the registry stores no values; PENDING is not a violation | 0051 | superseding 0051 |
| §55.5 | PreToolUse context arrives after the write; only a deny prevents it | 0052 | superseding 0052 |
| §56.0–56.0.1 | renumbering breaks citations; three destinations for an amendment | 0052, 0051 | new ADR |
| §56.1 | a schema/validator/skill mismatch fails one phase late; middleware never writes captures | 0053 | superseding 0053 |

## 3. Method statements in old §39 and §43 against the skills

139 statements were checked: 124 are present, 10 missing, 3 partial and 1 changed (one partial retired 2026-09-28: `check_gate_status` is not a coach tool). Measure and
Control are complete.

| Old § | Statement | State |
|---|---|---|
| 39.1.4 | The Project Leader is a Black Belt for complex or cross-functional work, a Green Belt for departmental work | **missing** (Define) |
| 39.1.4 | Sponsor/Champion approval is required at the gate | **missing** (Define), and in conflict with R6 ("the Belt, with the team, approves") |
| 39.1.4 | RACI is encouraged, not enforced | **missing** (Define) |
| 39.3.3 | A metric Analyse does not address is written "not addressed this phase" | **missing** (Analyse; borderline) |
| 39.3.7 | Analyse leans on case history more than any other phase | **missing** (Analyse; borderline) |
| 39.4.3 | Pilot effect per metric; "not addressed this phase" | **missing** (Improve; borderline) |
| 39.4.5 | FMEA is supported when a Black Belt raises it, never suggested | **missing** (Improve) |
| 39.4.11 | Improve reads Define's `target_value` and measures the pilot against it | **missing** (Improve) |
| 43.6 | Do not do the Belt's work | **missing** (all), and Control [1] says "do the arithmetic for them" |
| 43.6 | Do not stray off the current phase's topic | **missing** (all) |
| 39.1.5 | SIPOC is built column by column | partial (Define: one Ask, steps first) |
| 43.3 | The A→F session flow | partial: stages redefined in every SKILL.md |
| 43.7 | Metric literacy includes how to read a good or poor value | partial: Define and Measure only |
| 39.1.3 | The 5W2H are prompts, never stored | **changed**: `problem_5w2h` is stored (R4) |
| 43.5 | No external URLs | present in four phases, **absent from Define** |

## 4. Appendix B — the deferred backlog, for Desktop to place

| # | Deferred capability | Promotion trigger |
|---|---|---|
| 1 | Multi-tenant filtering on the case index | Deployed to several organisations |
| 2 | Per-source weighting in RAG fusion | A fourth retrieval source |
| 3 | Per-turn episodic entries in the case index | Gate summaries shown to lose detail |
| 4 | Mid-phase summary persistence | Belts often resume weeks later |
| 5 | Dynamic procedural memory (per-Belt adaptation) | "v2.2 priority workstream" |
| 6 | Similarity-threshold calibration | The eval dataset is populated |
| 7 | Dynamic top-k by remaining context | Fixed top-k causes budget problems |
| 8 | Reactive query restructuring | Multi-query + RRF shown insufficient |
| 9 | Feedback-driven chunk score adaptation | Systematic misses and a research workstream |
| 10 | Adversarial debate subgraph (Analyse) | Stable base loop and root causes needing stress tests |
| 11 | Opinion aggregation | Item 10 producing confidence scores |
| 12 | `DeltaChannel` checkpoint compression | Sessions beyond about 200 turns |
| 13 | **Migrate to `PostgresSaver` + `PostgresStore`** | **Before production launch** |
| 14 | Observer Agent across all Belts | Enough concurrent traffic |
| 15 | Multi-source knowledge index (`tenant_id`) | A customer brings its own methodology |
| 16 | **Secondary EU region** | **Before production launch (DORA)** |
| — | Model tiering per hop | Repeated hop-cap hits on Analyse |

Items 13 and 16 gate a production launch (T68 covers 16).

## 5. Pointers into v1.88 that were not rewritten

| What | Where | Why left |
|---|---|---|
| § citations of v1.88 in code comments and docstrings | about 1,700 in 93 files | Comments, not behaviour; rewriting them is a separate sweep |
| § citations in the ADRs' Source lines | all 56 ADRs | ADRs are never edited; the § numbers are v1.88's, and the archive keeps them readable |
| Links to the deleted `requirements/define.md` | ADRs 0004, 0007, 0008, 0010 | ADRs are never edited |
| `docs/requirements/define.md` cited in `skills/dmaic-define-phase/SKILL.md` | 3 lines | Any edit stales row 3's recorded live run (Part A) |
| T55's proof test | `platform.md` | It proves `BeforeModelStateInjection`, not the contradiction check; the contradiction hook is `after_agent`. platform.md is founder-owned |

## 6. §4.2 — the first regeneration against the transcribed draft (brief Part D)

**Where it landed.** The pre-commit hook regenerates §4.2 on every commit that carries the
markers (Part G). So the first regeneration landed in Part C's own commit, `2bcc1af`, and rule
16 checked it there ("the block equals a fresh generation"). The corrected draft had already
moved the hand-written content to §4.1 and left §4.2 as a placeholder, so against that draft the
diff is placeholder → generated.

**Against the TRANSCRIBED draft** (v2.0 as first delivered, §4 transcribed from the v1.88 spec
entries), field by field: 34 differences in the declarations, none in the index field names (the
first regeneration, recorded in `3f8fb4e`).

| Class | Field | Transcribed | Code (generated) |
|---|---|---|---|
| `PhaseState` | `remaining_steps` | `RemainingSteps` | `NotRequired[RemainingSteps]` |
| `CoachingPlan` | `field_status` | `dict[str, dict]` | `dict[str, dict[str, Any]]` |
| `CoachingPlan` | `reason` | absent | `str = ''` |
| `CoachingResponse` | `explanation`, `example`, `prompt`, `progress` | required | `str = ''` each |
| all five `{Phase}Output` | `phase_metrics` | required | `list[dict] = []` |
| `MeasureOutput` | `baseline_sigma`, `measurement_system_validated`, `secondary_metrics` | required | `str = ''` |
| `AnalyseOutput` | `causal_hypothesis` | required | `dict = {}` |
| `AnalyseOutput` | `ruled_out_causes`, `statistical_problem_statement`, `process_owner_buyin`, `secondary_metrics` | required | `str = ''` |
| `ImproveOutput` | `solution_linked_to_root_cause` | required | `dict = {}` |
| `ImproveOutput` | `implementation_plan`, `explanatory_power`, `process_owner_buyin`, `secondary_metrics` | required | `str = ''` |
| `ControlOutput` | `improvement_delta`, `financial_impact_verified`, `sustainability_check`, `handover_documented`, `lessons_learned`, `transferability`, `project_signoff`, `secondary_metrics`, `actual_close_date` | required | `str = ''` |

The corrected draft's §4.1 already covers the Tier 2 rows ("Fields with a default in §4.2 are the
recommended (Tier 2) fields"), and it removed the three statements the code contradicted. Still
open for Desktop:
- `PhaseState.remaining_steps` is `NotRequired`.
- `CoachingPlan.field_status` is typed more narrowly than the transcription.
- `CoachingPlan.reason` exists in the code and was never transcribed.
- `CoachingResponse`'s four blocks default to `''`, so they are not required.

**The refusal (D3), on the real tree after Part C.** One line inside §4.2 was hand-edited
(`case_id: str  # hand-edited`) and staged, and `.githooks/commit-msg` was run as git runs it.
Rules 10, 12 and 13 passed, then: "COMMIT BLOCKED — ARCHITECTURE.md's generated data-models block
differs from the code (rule 16)" (exit 1). The file was restored; `generate_models.py --check`
reports "current".

## 7. Moved out of ARCHITECTURE.md v2.0 to make room (BRIEF_m1_loop.md Part 1c, 2026-09-28)

ARCHITECTURE.md was at 41,629 of its 42,024-character bound. The sentences below are status or
rationale, not design, and were moved here word for word in substance; the rest of the room came
from tightening duplicates (the "Not here" table, the main-graph and wrapper bullets, the
read-back paragraph, the middleware order table, three glossary rows). A rationale here that no
ADR states is a gap of the kind §2 lists: it needs a new ADR, never an edit.

| From | Kind | Text |
|---|---|---|
| §2.6 | rationale | HumanInTheLoopMiddleware approves tool calls, and neither pause is a tool call. |
| §2.6 | status | Stopping the turn on a contradiction flag is guarded off today. |
| §2.5 | rationale | Pending writes are the partial results of a step that paused; persisting them is what lets a paused run resume in a different process, hours later, and write exactly once. |
| §2.7 | status | Setting the model filter and Prompt Shields block mode on the deployment is a founder action in the Azure portal. |
| §3.1 | status | `core/citations.py::CitationBundle` is declared and unused. |
| §3.3 | rationale | The skills middleware reads the files with a small local reader because LangChain ships no skills backend (the reader itself is in §3.7). |
| §3.3 | rationale | Summarization is safe because facts never live only in `messages`: confirmed values are in `artifacts`, approved records in the Store, routing in `SupervisorState`. |
| §3.3 | rationale | The tool retry is separate from the model retry: a failed search is not a failed model call. |
| §3.3 | rationale | Coherence is not part of the grader's rubric: it asks a different question, and more cheaply. |
| §3.3 | status | Stopping the turn on a contradiction flag is guarded off until the re-approval cascade is built (step 7.3). |
| §3.6 | rationale | check_gate_status and request_human_approval are not coach tools because readiness is in the coach's project-state section and escalation is the graph's. |
| §3.8 | status | Layer 2c: the `constraint` model role exists; no call is made and no `{PHASE}_CONSTRAINTS` exist. |
| §3.10 | status | The page loads one resource from outside the product: the Tabler icon font from `cdn.jsdelivr.net` (`@latest`, `ui/index.html` line 7) — a finding against T78 and C5 (G-114; §2.7 keeps the outbound line). |
| §4.1 | status | The structured-value shapes in §4.1 are not yet declared in code; declaring them (typed dicts or field descriptions) moves them into the generated block and removes that table. |
| §2.6 | rationale | Every change to the report goes through coaching so that it passes the validation layer. |
| §2.3 | status | The third-failure route from validation to escalation (Command.PARENT) is not built (T65). |
