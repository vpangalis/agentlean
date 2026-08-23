# Conversion plan — spec layer for `AGENTIC_ARCHITECTURE_REFERENCE.md`

**Status: AWAITING APPROVAL. Nothing has been written to either reference file.**

Produced per the audit-first requirement in
`instruction-spec-layer-conversion.md`, against `SPEC_LAYER_GUIDE.md`.
Scope of the work this plan describes: **mechanical restructure + scaffolding +
gap-marking only.** No missing definition, routing design or schema is invented.

---

## 0. What the audit found before planning anything

**The two reference files are byte-identical except for two things.** A full
diff of `AGENTIC_ARCHITECTURE_REFERENCE.md` against `agent-improve/ARCHITECTURE.md`
yields 93 changed lines, all of them accounted for:

| Difference | Direction |
|---|---|
| A 73-line provenance header block | Copy only |
| The v1.3 version note + the "six sections are annotated inline" paragraph + the six `> **Scope:**` annotations (§5, §6, §23, §30, §32, §35) | Root only |

**Parts I–XI are otherwise identical**, which means one insertion applies to
both and "confirm they match on the changed Parts" is mechanically verifiable
after the fact (the diff must still be those same 93 lines and nothing more).

> **Noted, not fixed, out of scope:** the copy's provenance blockquote has
> unrelated continuity-report prose pasted inside it (lines beginning "Rebuilt
> and pushed (6f25c11)…"). Pre-existing; not touched by this conversion.

---

## 1. Where the spec layer goes, and why numbering does not move

**`Part XII — Specification` is inserted after Part XI (Governance) and before
the Appendices.** `Part XIII — Compliance and Risk` follows it.

**§1–§56 do not renumber.** That is a hard constraint, not a convenience:
`CLAUDE.md` carries ~48 `§`-citations into this document, `DECISIONS.md`,
`REVIEW_DECISIONS.md`, `REFACTORING_PROCEDURE.md`, the SKILL.md files and code
comments all cite these numbers, and Appendix A is the resolution index for
older numbering. Renumbering would invalidate all of it for no gain.

This also satisfies the guide's volatility-separation rule: every architecture
Part (why) precedes the spec Part (how).

| New | Contents |
|---|---|
| **§57** | Spec-layer preamble — the three-layer entry template, the two calibrated samples, traceability convention |
| **§58** | Spec — graph management (state, nodes, routing, mappers, persistence) |
| **§59** | Spec — knowledge and retrieval |
| **§60** | Spec — tools |
| **§61** | Spec — validation and gates |
| **§62** | Spec — DMAIC gate documents |
| **§63** | Spec — skills |
| **§64** | Spec — prompts |
| **§65** | Spec — API and UI surface |
| **§66** | **The SPEC-GAP register** — every gap in one table, cross-linked to its inline marker |
| **§67** | Compliance — EU AI Act posture (Part XIII) |
| **§68** | Compliance — the DORA-structured risk register (Part XIII) |

**The five governance rules go to §55.1**, a new subsection of *Anti-drift* —
not a new section. §55 is already the home for "rules need checkable
enforcement," and a new §57 in Part XI would collide with the spec numbering
above.

**Entry IDs are stable and independent of section numbers:** `S-C##` for class
entries, `S-F##` for function/node entries. Tests, reviews and DORA rows cite
these, so a future section move costs nothing.

**Traceability line on every entry:** `Architecture: §N · Procedure: step X.Y ·
Spec: S-x##`, giving the guide's three-way link (architecture ↔ spec ↔
procedure step).

---

## 2. What moves out of each architecture section, and what stays

**Only definitions relocate. Every reasoning paragraph, every rationale table,
every callout stays exactly where it is** and gains one line under its status
line: `**Specification:** §5X — S-x##`.

The mechanical rule applied: a line is eligible to move **only** if it is
inside a fenced ` ```python ` block containing a `class`/`def`/signature, or is
one of the two named field-definition tables (§5 "Field by field", §6 "Field by
field"). Nothing else is removed from any section.

| § | Definition that moves | Reasoning that stays (verbatim) |
|---|---|---|
| §5 | `SupervisorState` TypedDict; "Field by field" table | Seven-field ceiling · `gate_passed` dict-not-list · derived-field exemption and its single-writer argument · the four removed fields and the `project_context` no-writer story · artifacts-are-not-here |
| §6 | `PhaseState` TypedDict; "Field by field" table; the duplicate `CoachingPlan` block; the `validator_feedback` / `citations` / `uploads` example dicts | Every subsection: dict-not-str · one-plan-not-a-queue · the `gate_attempts` production-bug account · validator_feedback vs belt_edits · the evidence-trail argument · hop_results-not-locals · per-phase variants · naming discipline |
| §7 | The canonical *shape* of the three cross-phase reference dicts | The typing law itself, why-strings, the rejected alternatives, the computation-results rule. §7 stays the canonical home of the law |
| §9 | `AzureBlobStore` class block; `define_input_mapper` and `define_output_mapper` bodies | Namespace convention · the `BaseStore.search()` re-examination note · why cross-phase data cannot travel on parent state · the three-boundary-mechanisms table · the two prohibitions · ordering constraint |
| §12 | `build_phase_subgraph` block | Topology, one-runtime rule, `add_edge(START, …)` |
| §14 | The `phase_executor` skeleton snippet | The node-contract rule table — it is cross-cutting, not per-function, and every spec entry references it |
| §15 | The six `add_edge` calls | The decision test · never-mix · **Level 1 does not route, it advances** · the `route_after_phase` deletion note · no-cross-imports |
| §16 | The `ainvoke` config block and the `compile()` block | One-thread-per-project · parallel-case isolation · why per-subgraph `thread_id` is wrong · `recursion_limit` is a backstop |
| §17 | `CoachingPlan` (canonical) and the `with_structured_output` lines | Planner/Executor contract table · never-fused · strategy-at-plan-time · extraction-is-structured-output |
| §18 | The `create_agent(...)` block | `system_prompt=` correction · bare-model violation · `create_react_agent` superseded · the deepagents dependency-risk argument · response-and-text-coexist |
| §19 | The `middleware=[...]` list; `SummarizationMiddleware(...)`; `ModelRetryMiddleware(...)`; the `ContradictionDetectionMiddleware` class block | All ordering rules · the three-retry-caps table · every §19.1–§19.9 rationale, including the DECISIONS §R1 blockquote and §19.9's not-used table |
| §20 | `CoachingResponse`; the `contradiction_flag` five-key block; the executor-writes-into-state snippet | Two-schemas-two-moments · why `value` is `Any` · never-a-phase-Output · what structured output does not give you |
| §21 | — nothing | Roles and temperature tables stay: they are configuration, not schemas or signatures, so define-once does not reach them. The structured-output mapping table stays and is mirrored as the spec's schema index |
| §23 | — nothing | **Index schemas stay in §23 by deliberate decision** (see §4 below) |
| §24 | The three-tool signature table; the `AzureSearch` snippet | Retired-names correction · RAG-via-tool · why not `AzureAISearchRetriever` · `belt_level` off by default · source_file/page_number returned not filtered |
| §25 | `reciprocal_rank_fusion` implementation | Why-mandatory (the Agent Resolve evidence) · why the two LangChain classes are banned · encapsulation |
| §26 | The `agent_node` guard snippet; `Hop`; `Plan`; the `analyse_executor_node` body; `SynthesisOutput` | Multi-hop-is-the-ReAct-loop · the `RemainingSteps` argument · per-phase policy table · the three-call table and why synthesis is not folded in · the **UNVERIFIED** Analyse-only note |
| §29.2 | The universal-seven signature block | §29.1 in full · §29.3 `record_field` · §29.4 cross-agent tools and its three binding rules |
| §30 | — nothing | The per-phase binding table is a binding inventory, not a signature set. Stays canonical; spec entries reference it |
| §33 | The §33.2 `store.put` / `return {…}` snippet | The nine-step table · two-checks-two-actors · one-way-doors · §33.1's split rationale and frontend sequence · why both writes · §33.3 |
| §35 | `CriterionVerdict`; the `acknowledged_gaps` example line | The problem-this-solves · the three-mechanisms table · Tier 1 by phase · why-two-tiers · belt-level awareness |
| §36 | — nothing | `COACHING_QUALITY_RUBRIC` text stays (it is prompt content, and §22 names §36 its home) |
| §40 | All five `{Phase}Output` class blocks; the §40.1 assembly snippet | Field counts · the four gate-metadata sources · two-fields-on-all-five · the tier/access-pattern reasoning · assembly-must-reference-every-field |
| §41 | The `control_plan` dict block | Sub-field table · grader-checks-every-sub-field · stability-before-capability · experiment-justification · the FMEA exclusion in full |
| §45 | The `add_node(...)` block; `phase_error_recovery` body | Timeout policy discussion · composition order · Saga ban · the two correctness-critical dependencies · **the entire `request_drain()` UNCONFIRMED warning** · `DeltaChannel` |
| §46 | `degraded_mode_response` body | The chain · backoff-per-level · cache invalidation · breaker asymmetry · HTTP-400 · §46.1 geographic redundancy in full |
| §48 | `AgentImproveError` block | The two-fields-read-by-machinery argument |
| §49 | — nothing | Endpoint table is an inventory; envelopes are a gap (G-18) |

**Two existing define-once violations are resolved by the move**, not created
by it:

1. **`CoachingPlan` is currently defined twice** — §6 (line 602) and §17
   (line 1538), identical text. One canonical entry, both sections reference it.
2. **`PhaseState`'s field semantics are stated in three places** — §6's table,
   §19.3's "lives in" table, and §5's removed-fields table. Only §6's table
   moves; the other two are cross-references and stay.

---

## 3. The complete spec entry list

★ = AI-ACT flag · ◐ = `AI-ACT-REVIEW: uncertain` · **G** = carries a SPEC-GAP

### 3.1 Class entries (37)

| ID | Entry | From | Flag |
|---|---|---|---|
| S-C01 | `SupervisorState` | §5 | — |
| S-C02 | `PhaseState` | §6 | — |
| S-C03 | Per-phase variants `DefineState`…`ControlState` | §6 | **G-19** |
| S-C04 | `CoachingPlan` | §6 + §17 | — |
| S-C05 | `CoachingResponse` | §20 | — |
| S-C06 | `AzureBlobStore` | §9 | — |
| S-C07 | `AzureBlobCheckpointSaver` | §8, §10 | **G-20** |
| S-C08 | `ImproveBlobClient` | §10 | **G-21** |
| S-C09 | `CaseDocument` · `PhaseRecord` · `RegistryEntry` · `PhaseSummaryRecord` | §10 | **G-17** |
| S-C10 | `ContradictionDetectionMiddleware` | §19.6 | ★ |
| S-C11 | `BeforeModelStateInjection` | §19.1 | **G-24** |
| S-C12 | `DMAICSkillsMiddleware` | §19.2 | **G-24** |
| S-C13 | `CoherenceMiddleware` | §19.7 | ◐ **G-24** |
| S-C14 | `DMAICGraderMiddleware` | §19.8 | ◐ **G-24** |
| S-C15 | `HITLInterrupt` | §19.6 | **G-15** |
| S-C16 | `Hop` | §26 | — |
| S-C17 | `Plan` (hop decomposition) | §26 | — |
| S-C18 | `SynthesisOutput` | §26 | — |
| S-C19 | `QueryVariants` | §21, §25 | **G-14** |
| S-C20 | `CriterionVerdict` | §35 | — |
| S-C21 | `GraderVerdict` | §21, §35 | **G-11** |
| S-C22 | `CoachingGraderVerdict` | §21 | **G-12** |
| S-C23 | `CoherenceResult` | §21 | **G-09** |
| S-C24 | `ConstraintCheckResult` / `ConstraintVerdict` | §21 | **G-10** |
| S-C25 | `PolicyAdvisoryResult` | §21 | **G-13** |
| S-C26 | `DMAICGateValidator` | §34, §54 | ◐ **G-23** |
| S-C27 | `DefineOutput` | §40 | — |
| S-C28 | `MeasureOutput` | §40 | — |
| S-C29 | `AnalyseOutput` | §40 | — |
| S-C30 | `ImproveOutput` | §40 | — |
| S-C31 | `ControlOutput` | §40 | — |
| S-C32 | The three cross-phase reference dicts | §7, §42 | — |
| S-C33 | The three structured dict fields | §41 | — |
| S-C34 | `AgentImproveError` | §48 | — |
| S-C35 | `CircuitBreaker` | §46, §54 | **G-22** |
| S-C36 | `CitationRecord` / `CitationBundle` | Appendix D.2 | **G-16** |
| S-C37 | API envelopes (`gateway/schemas.py`) | §49 | **G-18** |

### 3.2 Function / node entries (36)

| ID | Entry | From | Flag |
|---|---|---|---|
| S-F01 | Supervisor graph — static edges | §15, §16 | — |
| S-F02 | `build_phase_subgraph(phase, llm)` | §12 | — |
| S-F03 | `phase_planner` node | §13, §17 | — |
| S-F04 | **`phase_executor` node** — the calibrated function sample | §13, §18, §20 | ★ `R-EXEC-01` |
| S-F05 | `validation_stack` node | §13, §34 | ★ `R-VALSTACK-01` |
| S-F06 | `gate_review_node` | §13, §33.1 | ★ `R-GATEREV-01` |
| S-F07 | `gate_apply_node` | §13, §33.1–2, §40.1 | ★ `R-GATEAPPLY-01` |
| S-F08 | Escalation subgraph | §38 | ◐ **G-34** |
| S-F09 | `analyse_executor_node` | §26 | — |
| S-F10 | `define_input_mapper` | §9 | — |
| S-F11 | `define_output_mapper` | §9 | — |
| S-F12 | Measure / Analyse / Improve / Control mappers | §9 | **G-27** |
| S-F13 | **Level 2 `Command` routing** | §13, §15 | **G-01** |
| S-F14 | `rag_lookup_methodology` | §24, §29.2 | ◐ |
| S-F15 | `rag_lookup_evidence` | §24, §29.2 | ◐ |
| S-F16 | `rag_lookup_case_history` | §24, §29.2 | ◐ |
| S-F17 | `reciprocal_rank_fusion` | §25 | — |
| S-F18 | `search_knowledge` / `search_cases` / `search_evidence` · `_fail()` · `RETRIEVAL_EXCEPTIONS` | §27 | **G-26** |
| S-F19 | `propose_template` | §29.2 | **G-29** |
| S-F20 | `propose_diagram` | §29.2 | **G-30** |
| S-F21 | `check_gate_status` | §29.2 | **G-31** |
| S-F22 | `request_human_approval` | §29.2 | ◐ **G-32** |
| S-F23 | `load_skill(name)` | §19.2, §32 | **G-33** |
| S-F24 | The 20 computation tools (one entry, per-tool table) | §30 | **G-25** |
| S-F25 | Layer 2c — constraint check | §34 | ◐ |
| S-F26 | Layer 2d — gate grader | §34, §36 | ★ (rolls into `R-VALSTACK-01`) |
| S-F27 | Policy advisory (inside `gate_apply`) | §33 step 6 | ◐ |
| S-F28 | Gate assembly | §40.1 | **G-28** |
| S-F29 | `phase_error_recovery` | §45 | **G-03**, **G-06** |
| S-F30 | `degraded_mode_response` | §46 | ◐ |
| S-F31 | `synthesise_partial` | §26 | **G-35** |
| S-F32 | `delete_or_flag_stale_in_case_index` | §45 | **G-35** |
| S-F33 | `degraded_coaching_response` node | §45 | **G-35** |
| S-F34 | API surface — the seven endpoints | §49 | **G-18**, **G-36** |
| S-F35 | Upload handler | §6, §29.1 | **G-36** |
| S-F36 | `improve_case_index` write path | §23.3, §37, §45 | ◐ **G-37** |

**73 entries. 5 AI-ACT flags, 12 `AI-ACT-REVIEW: uncertain`.**

### 3.3 Why those five, and only those five

The guide's rule is that **most entries carry no flag**; a flag on a pure
utility is itself a review finding. Applied:

| Flagged | High-risk surface |
|---|---|
| `phase_executor` | Produces the coaching output the Belt acts on and the extraction that becomes the record |
| `gate_review_node` | The human-oversight surface — Art. 14 lives or dies here |
| `gate_apply_node` | Commits the assessed document; the approval decision |
| `validation_stack` (with Layer 2d) | Produces the pass/fail assessment of the Belt's phase |
| `ContradictionDetectionMiddleware` | Suppresses coaching output and can make an approved assessment provisional |

**Deliberately unflagged:** `phase_planner` (orchestration — chooses what to
coach, asserts nothing), the 20 computation tools (pure deterministic
functions), `check_gate_status` (pure derivation), `propose_template` /
`propose_diagram`, `reciprocal_rank_fusion`, the persistence classes and the
state schemas. The persistence and logging mechanisms appear in the Art. 12
obligation table as **mitigations**, which is a different thing from a flag.

**The 12 uncertains are marked, not guessed**, per the instruction: the
retrieval tools (Art. 10 data governance, and §27's failure-reads-as-absence
risk), the two quality middlewares (Art. 13 — the Belt never sees a silent
retry), `DMAICGateValidator` and the constraint check, the policy advisory,
degraded mode, escalation, `request_human_approval`, and the case-index write
path.

---

## 4. Three deliberate decisions inside the restructure

Each is a judgment call the plan makes explicitly rather than silently.

**(a) Index schemas stay in §23.** They are data-store schemas, not code
classes or function signatures, so the define-once rule does not reach them;
§2 names §23 their canonical home; and §23.5 is a ratified procedure requiring
schema changes to land in §23 first, in the same commit as the Azure change.
Moving them would break that procedure for no benefit. The `rag_lookup_*` spec
entries reference §23 rather than restating it.

**(b) Middleware gets class entries only, not a second function entry per
hook.** Each middleware's hook behaviour is expressed as EARS behaviours on its
class entry. Splitting them would create five duplicate entries whose
Supplier/Customer cells restate the class's.

**(c) The 20 computation tools get one entry, not twenty.** Twenty entries
whose every cell reads `SPEC-GAP` is noise that hides the single real gap.
One entry, a table of all 20 by phase, and one gap covering signatures, return
shapes, and the unspecified "reformatting request" contract (G-25).

---

## 5. THE SPEC-GAP LIST — the review agenda

**41 gaps. None is filled by this task.** Each appears twice: inline at the
point of use as `SPEC-GAP: <what's missing> — to be designed with founder`,
and as a row in the §66 register.

Groups A and B are the ones worth reading first — A is the founder's to rule
on, and B is a set of defects the SIPOC cross-check surfaced that nobody has
seen yet.

### A — Founder ruling required (2)

| # | Gap |
|---|---|
| **G-01** | **Level 2 (subgraph-internal) `Command` routing.** §13 draws the branching, §15 states the rule, and no `Command(goto=…)` exists anywhere. The three decision points from guide §9 are listed under the marker: (1) planner → executor vs → validation_stack on field-complete; (2) validation_stack → gate_review / escalation / planner-with-feedback, and its ownership of the `gate_attempts` increment; (3) gate_review → gate_apply. |
| **G-02** | **What a Belt REJECT does.** `POST /gate/reject` is in §49's endpoint table and in §33.1's frontend sequence, and nothing anywhere states its behaviour — re-coach, or apply-with-edits. Guide §9 calls this the coaching-philosophy call needing a founder ruling. |

### B — Cross-check defects the SIPOC pass surfaced (6)

**These are the same defect class as `route_after_phase`** (DECISIONS §R2): a
specified function reading a state field that its state schema does not
declare. They are recorded as gaps, not fixed, because each fix is a design
choice — and adding a field to `PhaseState` is a §56 amendment.

| # | Gap |
|---|---|
| **G-03** | **`PhaseState` carries no `case_id` and no phase identifier**, yet specified code reads both off it: `phase_error_recovery` reads `state["case_id"]` and `state["phase"]` (§45); `analyse_executor_node` reads `state["current_phase"]` (§26); `gate_apply_node`'s Store write needs `case_id` (§33.2). §6's seventeen fields contain none of them. |
| **G-04** | **`remaining_steps` is read off `PhaseState` twice** (§26) and is not a declared field. `RemainingSteps` is a LangGraph managed value that must be declared on the state schema to be populated — undeclared, `state.get("remaining_steps", 10)` returns 10 forever and **the five-hop cap never fires.** A cap that cannot fire. |
| **G-05** | **`extracted_entity`** is read off `PhaseState` by `analyse_executor_node` (§26). Not a declared field, and no writer is named anywhere. |
| **G-06** | **`extraction_error` and `extraction_incomplete`** are written into state by `phase_error_recovery`'s `Command(update=…)` (§45). Neither is a `PhaseState` field. |
| **G-07** | **`state["structured_response"]`** is read by `ContradictionDetectionMiddleware.after_agent` (§19.6). Whether middleware sees `PhaseState` or `create_agent`'s own internal agent state is never stated — and the entry cannot declare its Input cell without it. |
| **G-08** | **`validation_stack.get_acknowledged_gaps()`** is named in §40 as the source of `acknowledged_gaps`. That is attribute access on a node, and §14 requires nodes to be module-level async functions. Where acknowledged gaps are produced, and how they reach gate assembly, is unspecified. |

### C — Schemas named but never defined (11)

| # | Gap |
|---|---|
| **G-09** | `CoherenceResult` — named in §21's mapping table, defined nowhere |
| **G-10** | `ConstraintCheckResult` — named in §21, defined nowhere. **Plus a naming split:** `CLAUDE.md` §2 lists both `ConstraintVerdict` and `ConstraintCheckResult` in `validation/schemas.py`; the reference names only the second. Two names, unclear whether two things |
| **G-11** | `GraderVerdict` — only "carries a `list[CriterionVerdict]`" (§35) is stated; no definition |
| **G-12** | `CoachingGraderVerdict` — named in §21, defined nowhere |
| **G-13** | `PolicyAdvisoryResult` — named in §21, defined nowhere |
| **G-14** | `QueryVariants` — named in §21 and §25, defined nowhere |
| **G-15** | `HITLInterrupt` — raised by §19.6 with `**flag`; not defined, and not confirmed to be a LangGraph symbol |
| **G-16** | `CitationRecord` / `CitationBundle` — appear only in Appendix D.2's ban on *duplicating* `CitationRecord` and in `CLAUDE.md` §2's file list. Never defined |
| **G-17** | `CaseDocument` · `PhaseRecord` · `RegistryEntry` · `PhaseSummaryRecord` — `storage/models.py`, named in `CLAUDE.md` §2 and §23.3, defined nowhere |
| **G-18** | **`gateway/schemas.py` envelopes** — §49 says "envelopes are Pydantic v2" and defines none, for any of the seven endpoints |
| **G-19** | **Per-phase `PhaseState` variants** — §6 says `DefineState`, `MeasureState`… "extend `PhaseState` with phase-specific transient fields." The fields are never enumerated, and their existence interacts with §6's fourteen-content-field ceiling |

### D — Described in prose, no interface (18)

| # | Gap |
|---|---|
| **G-20** | `AzureBlobCheckpointSaver` — the on-blob format is specified (§8); the `BaseCheckpointSaver` method set it implements is not |
| **G-21** | `ImproveBlobClient` — named as the owner of case records (§10); no interface |
| **G-22** | `CircuitBreaker` — three-state behaviour and thresholds stated (§46); no class interface |
| **G-23** | `DMAICGateValidator` — named as a namespace of `@staticmethod` checks (§54); no method names, no signatures |
| **G-24** | **Constructor arguments for all four remaining custom middlewares.** §19 writes `BeforeModelStateInjection(...)`, `DMAICSkillsMiddleware(...)`, `CoherenceMiddleware(...)`, `DMAICGraderMiddleware(...)` — the `(...)` is literal in every case |
| **G-25** | **The 20 computation tools** — names and phase binding only. No signatures, no return shapes, and no defined shape for the "clear reformatting request to the Belt" that §7 requires when a tool cannot parse its input |
| **G-26** | `search_knowledge` / `search_cases` / `search_evidence` signatures; the membership of `RETRIEVAL_EXCEPTIONS`; the `_fail()` contract. §27 specifies their *semantics* precisely and their *interface* not at all |
| **G-27** | **Boundary mappers for Measure, Analyse, Improve and Control.** §9 writes Define's pair in full; the other four are asserted to exist. Each must compose `phase_context` from the prior phase's gate document, and no shape is given |
| **G-28** | **Gate assembly for Measure, Analyse, Improve and Control.** §40.1 shows `DefineOutput` only, and §40 requires that assembly reference every field in the schema |
| **G-29** | `propose_template` — types given as "problem_statement, sipoc, data_collection_plan, fishbone, etc." No closed list, and no `fill_data` schema per type |
| **G-30** | `propose_diagram` — "types and schemas in `core/diagrams.py`". **That file does not exist** (Appendix E) and no schema is stated anywhere |
| **G-31** | `check_gate_status()` — return shape unspecified. It also **takes no arguments** yet must know the current phase and `artifacts`, and §19.1 requires the middleware to derive missing fields "the same way the gate does" |
| **G-32** | `request_human_approval` — its relationship to graph-level `interrupt()` and to the escalation subgraph (§38 names it as one of two entry points) is unspecified |
| **G-33** | **`load_skill(name)`** — a registered tool in §19.2 and §32 that appears in **neither the universal seven (§29.2) nor any phase's tool count (§30)**. Either an eighth universal tool — which moves every count against the 16 cap — or something else |
| **G-34** | **The escalation subgraph** — §38 gives two entry points and a posture. No node list, no state schema, no exit contract. §15 says it "never returns to the supervisor," which leaves how the run terminates unstated |
| **G-35** | Three named-but-undefined helpers: **`synthesise_partial(state)`** (§26, two call sites), **`delete_or_flag_stale_in_case_index()`** (§45), and the **`degraded_coaching_response`** node (§45's `goto=` target — not among §13's five nodes, and §13 forbids adding a sixth without an amendment) |
| **G-36** | **No upload endpoint exists.** §6 names an "Upload handler" as the writer of `PhaseState.uploads`; §10 defines the `uploads/{case_id}/{file}` blob path; §29.1 makes uploads **the only channel through which external data enters the platform** — and §49's endpoint table has no upload endpoint |
| **G-37** | **The `improve_case_index` write path.** §23.3 defines the schema, §37 and §45 require compensating cleanup of it — and nothing states who writes it, when, or with what |

### E — Content the build sequence defers (3)

Marked so they are visible, not because they are overdue — guide §8 sequences
prompts as subsystem 5.

| # | Gap |
|---|---|
| **G-38** | **`field_index` has no ordering source.** §6 defines it as "which field within the phase"; the ordered per-phase field list it indexes into is stated nowhere, and §13's "advance to the next field" depends on it |
| **G-39** | **`turn_count`'s increment contract** — when, by whom, by how much — is unstated, and it is load-bearing in §11's deterministic `step_log` key |
| **G-40** | **Prompt constants.** `{PHASE}_COACH_PROMPT`, `{PHASE}_PLANNER_PROMPT`, the five `PHASE_RUBRIC`s and the four `{PHASE}_CONSTRAINTS` sets are named (§22) with coverage lists (§36) and no text. Only `COACHING_QUALITY_RUBRIC` is written out |

### F — The spec layer's own gap (1)

| # | Gap |
|---|---|
| **G-41** | **The two calibrated samples' verbatim text is not in the repository.** Guide §7 gives their skeletons and says "see the conversation of 2026-08-23 for the full text"; no transcript of that conversation exists in any file. **This one blocks step 2 of the instruction** and needs a decision before execution — see §6 below |

---

## 6. The one question that blocks execution

**Instruction step 2 requires the two calibrated samples transcribed VERBATIM,
"do not paraphrase them." Their verbatim text does not exist in any file I can
read.** `SPEC_LAYER_GUIDE.md` §7 carries their skeletons — for `SupervisorState`,
seven required template features; for `phase_executor`, the SIPOC cells, B1–B6
one-liners, and the AI-ACT / `R-EXEC-01` targets — and defers the full text to
the conversation.

Reconstructing them from the skeleton would be paraphrase, which the
instruction forbids, and these two entries define the format every other entry
is built to. Three ways forward:

| | Option | Consequence |
|---|---|---|
| **A** | **Paste the two samples in before execution** (recommended) | The calibrated standard is exactly what was approved; everything else is built to it |
| **B** | Build both from the guide §7 skeleton, marked `SPEC-SAMPLE: reconstructed from SPEC_LAYER_GUIDE §7 — not the approved verbatim text` | Unblocks now, but the calibration standard is my reconstruction, and 71 entries get built against it |
| **C** | Leave the preamble's sample slots as `SPEC-GAP: calibrated samples — paste from the 2026-08-23 conversation` | Honest, but the preamble ships without the examples that define the format |

---

## 7. Compliance and Risk Part (Part XIII)

**§67 — EU AI Act posture.** Verified deadlines as stated in guide §4.1
(Regulation (EU) 2026/1744 in force 27 July 2026; 2 Dec 2027 for standalone
Annex III including employment; 2 Aug 2028 for Annex I). The
classification-depends-on-deployment note carried across **unresolved and
labelled as a legal determination**, not answered. The eight-obligation table
(Art. 9, 10, 11, 12, 13, 14, 15, 43) mapped to existing mechanisms exactly as
guide §4.1 states them.

**§68 — the DORA-structured register.** Ten columns as specified. **Five rows,
one per flagged function** — `R-EXEC-01`, `R-GATEREV-01`, `R-GATEAPPLY-01`,
`R-VALSTACK-01`, `R-CONTRA-01` — each citing the function plus the behaviour
IDs it aggregates, so row ↔ flag correspondence is checkable by Risk ID.

**The 12 uncertains get a separate holding table, not register rows.** The
register's integrity rule is that every row traces to a flag and every flag
appears in the register; putting unresolved classifications in it would break
that in both directions.

**One compliance finding is already in the document and will be cited, not
invented:** §46.1 states that the single-region fallback chain is
"non-compliant for any regulated-entity deployment" under DORA's ICT resilience
obligations. That becomes a register entry against the existing Appendix B
item 16.

---

## 8. Governance, sources, and the §56 route

**§55.1 — five rules, each with its stated check**, per guide §6 and the R2
discipline (a rule whose enforcement is "nothing" says so):

| Rule | What catches a violation |
|---|---|
| Spec-before-code | A code change whose spec entry's last-modified predates it |
| Flag-is-canonical, register-is-derived | Every register Risk ID traces to a flagged function; every flagged function appears in the register |
| SIPOC Supplier/Customer cross-check | grep by function name — A's Customer must list A as Supplier |
| Define-once | A schema or signature appearing in both the spec Part and an architecture section |
| Selective flagging | A flag on a pure utility, or a missing flag on a coaching / gate / assessment function |

**§56 gains one line** to its "what requires an amendment" list: a change to a
spec entry's schema or signature.

**Appendix C gains a Tier 1 — compliance block**: the three EU AI Act sources,
DORA (EUR-Lex 2022/2554), and the SDD method references (GitHub Spec Kit, AWS
Kiro), **with the compliance-source discipline note** — any compliance claim
cites a current-dated source or is marked "unverified — requires legal
validation."

**The §56 route for this change:**

1. `DECISIONS.md` gains **Part S — The specification layer (2026-08-23)**,
   entries S1 (spec layer: structure, template, entry inventory, the gap
   register) and S2 (the compliance/risk layer). Per §56 step 4 this entry is
   both the decision record and the change log.
2. One commit updating both reference files.
3. Version **1.5 → 1.6** in both, plus the one-line version note at each head.
4. **No `deprecated_patterns.yaml` change** — it cites `CLAUDE.md` rule
   numbers, and no `CLAUDE.md` rule and no reference section §1–§56 renumbers.
   Verified, not assumed.
5. **No `CLAUDE.md` amendment.** This touches no rule there. Flagging it as
   your call whether §0.x should gain a pointer to the spec layer — I will not
   add one unasked.

**Post-execution verification, run and reported:**

- `diff` the two reference files → must still be exactly the 93 lines of §0,
  proving the changed Parts match.
- Every removed line is inside a `python` code fence or one of §5/§6's two
  field tables → proves no reasoning was lost.
- Every `SPEC-GAP` inline marker has a §66 register row, and vice versa.
- Every AI-ACT flag has a §68 register row, and vice versa.
- Supplier/Customer cross-check across all 73 entries; mismatches reported as
  findings, **not silently corrected**.

---

## 9. Scale, stated plainly

Roughly **3,000–3,500 added lines per file**, taking each from ~5,335 to
~8,500. No architecture section loses prose; the growth is the spec Part, the
compliance Part and the gap register.

**Nothing in this plan touches code.**
