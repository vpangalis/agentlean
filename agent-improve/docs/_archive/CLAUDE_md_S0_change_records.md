# CLAUDE.md §0 — the change records

> **Moved out of `agent-improve/CLAUDE.md` on 2026-09-13, verbatim.**
> Every subsection below is a dated *What Changed in 2.2.x* entry. Nothing
> here is a rule, and nothing here is cited by a live section for a value —
> that was checked before the move and recorded at ARCHITECTURE.md v1.39.
>
> **FOUR SUBSECTIONS DID NOT MOVE and are still in `CLAUDE.md`:**
> **§0.1** (the three binding documents, and how to resolve a pre-2026-08-22
> `ARCHITECTURE.md §X` citation), **§0.2** (rule numbers are load-bearing),
> **§0.12** (which architecture document a rule cites), **§0.24** (prefer
> framework primitives). The last is cited three times in
> `.claude/config/deprecated_patterns.yaml`; archiving it would have broken
> §0.2's own invariant that those citations resolve.
>
> **Numbers are unchanged and the gaps are deliberate.** §0.2 applies to
> itself: renumbering would silently redirect every citation that names one
> of these.
>
> **The contradictions with CLAUDE.md's live sections are preserved, not
> repaired** — the retired gate field names, Define's counts, and §0.17's
> *"20 + 1 managed, 21 declared"* against §10.1's twenty-two. They were true
> when written; that is what a change record is.

---

### 0.3 — What Changed From v2.1

| Area | v2.1 | v2.2 |
|---|---|---|
| Gate approval | Interrupt → approve | **Nine-step HITL** (§9.1) |
| Gate validation | Field presence | **Four-layer stack** (§9.2) |
| Retrieval tools | 3 (`search_improve_knowledge`, `search_improve_cases`, `search_improve_evidence`) | **3 `rag_lookup_*`** (§7.2) |
| Tool binding | 7 universal tools, same for all phases | **7 universal + 20 per-phase computation** (§5) |
| Coach construction | `bind_tools` on the coach LLM | **`create_agent` + eight middlewares** (§4.4, §8) |
| Structured output | `with_structured_output` mandated everywhere | **Scoped by call type** (§4.6) |
| Cross-phase data | Parent state | **Store** (§10.2) |
| Persistence | Azure Blob only | **Phased Blob → PostgreSQL** (§1.7) |
| MCP | In the stack description | **Architecturally excluded** (§1.9) |
| Index schemas | Partial, in prose | **Canonical in `../AGENTIC_ARCHITECTURE_REFERENCE.md` §23**; rule-bearing facts in §7.3 |

### 0.4 — What Changed in 2.2.9 — the state design closed

All 15 findings from the state design audit landed in one commit. The
rules that bind, and where they live:

| Area | v2.2.8 | v2.2.9 |
|---|---|---|
| Identifier | `project_id` in docs, `case_id` in code | **`case_id` everywhere** (§10.5) |
| Name for captured fields | `artifacts` / `captured_fields` / `phase_inputs` | **`artifacts` only** (§10.5) |
| `SupervisorState` | 7 fields, `gate_passed: list[str]` | 7 fields, **`gate_passed: dict[str, bool]`**, `final_output: Optional[dict]` (§10.1) |
| `PhaseState` | 11 fields, `feedback`, `final: str` | **17 fields (now 19 — §0.15)** — adds `gate_attempts`, `validator_feedback`, `citations`, `uploads`, `hop_results`, `synthesis_output`; `feedback` → **`belt_edits`**; `final: dict` (§10.1) |
| `coaching_plan` | `list[dict]` in some places | **single typed `CoachingPlan`**, transient (§10.1) |
| Gate document write | Unspecified | **`gate_apply_node` writes store + `PhaseState.final`** (§9.6) |
| Captured field typing | Prose promised typed floats | **All `str`**, three cross-phase reference dicts excepted (§10.6) |
| Computation results | Nowhere | **`artifacts["computation_results"]`** (§10.6) |
| Gate-required fields | One flat list, contradicting the rubric | **Two tiers**; grader verdict gains `"warning"` (§9.7) |

### 0.5 — What Changed in 2.2.10 — the executor contract closed

| Area | v2.2.9 | v2.2.10 |
|---|---|---|
| Subgraph nodes | `policy_advisory`, `revise` | **`validation_stack`, `gate_apply`** (§3.3) |
| Validation stack | Listed as an executor tool | **A node**, reached by an edge (§3.3) |
| Policy advisory | Listed as an executor tool | **Logic inside `gate_apply`** (§3.3) |
| Graders | One, conflated | **Two** — `COACHING_QUALITY_RUBRIC` every turn, `PHASE_RUBRIC` at the gate (§8.2) |
| Middleware | Four | **Five** — `ModelRetryMiddleware` added (§8.7) |
| Middleware order | State injection last | **State injection first** (§8.1) |
| Executor `response_format` | `ProviderStrategy(PhaseOutput)` | **`CoachingResponse`** (§4.6, §10.7) |
| Field capture | `record_field` tool | **`CoachingResponse.fields_captured`** (§5.1) |
| Universal tools | 8 | **7** (§5.1) |
| Per-phase totals | 9 / 16 / 13 / 9 / 12 | **9 / 16 / 13 / 9 / 13** (§5.2) — *was `8 / 15 / 12 / 8 / 12`; corrected 2026-09-11, superseded by the amendment of 2026-09-09* † |
| Gate document schemas | Undefined, or two conflicting | **Five canonical `{Phase}Output`** (§10.7) |

> † **`§898` IS STRUCK — IT RESOLVED TO NOTHING.** The row read *"superseded by
> ~~§898's~~ amendment of 2026-09-09"*. There is no §898 in CLAUDE.md,
> ARCHITECTURE.md or the platform reference, and the string occurred exactly
> once in all three: here. **The amendment is real and its citation was not.**
> It is **ARCHITECTURE.md §29.2 — *"`load_evidence_series` joins the set —
> RATIFIED 2026-09-09"*** (tool spec at §60.7 / S-F57), which is what took the
> universal set to its current membership and moved Control's total to 13.
>
> Struck rather than silently repointed, on C-3's precedent: a citation that
> pointed nowhere for three weeks is evidence about how citations are checked
> here, and §55.1 requires every reference to resolve to what it names. **A
> §-number is a literal string and nothing checks them** — which §30's own
> 2026-09-09 note says, about itself, two wrong citations earlier.

### 0.6 — What Changed in 2.2.11 — the eBook gaps closed

Findings 24 and 25, from the BB eBook extraction (57 gaps identified,
25 closed by schema change, the rest by SKILL.md coaching content).

| Area | v2.2.10 | v2.2.11 |
|---|---|---|
| Fields on all five schemas | — | **`issues_and_barriers` (Tier 1)**, **`secondary_metrics` (Tier 2)** (§10.7) |
| Measure Tier 1 | 2 fields | **5** — adds `xy_matrix_summary`, `vital_few_xs`, `issues_and_barriers` (§9.7) |
| Analyse | no practical-significance field | **`practical_significance`, Tier 1** — the eBook's second gate (§9.7) |
| Statistical problem statement | Define, BB-only, no field | **Analyse, all Belts, `statistical_problem_statement`** (§9.7) |
| Process owner buy-in | Control only | **Also Analyse and Improve** — `process_owner_buyin` (§10.7) |
| Improve explanatory power | — | **`explanatory_power`** (§10.7) |
| Three-party sign-off | Rubric item, no field | **`project_signoff` on `ControlOutput`** (§9.7) |
| `control_plan` | `str` | **`dict` of five sub-plans** (§10.8) |
| FMEA | BB-only rubric item | **Not tracked in any schema** (§10.8) |
| Computation tools | Called and returned | **Six-step coaching pattern**, enforced by rubric (§8.2) |

Field counts: Define 14 · Measure 12 · Analyse 13 · Improve 12 ·
Control 15.

### 0.7 — What Changed in 2.2.12 — process maps become schema

Finding 26. Three gaps previously assigned to SKILL.md coaching content
were promoted to **Tier 1 schema fields** — a coaching prompt produces a
conversation, and a conversation cannot be read by the next phase's
planner or checked by the grader.

| Area | v2.2.11 | v2.2.12 |
|---|---|---|
| Define process map | Coaching content, no field | **`process_map_sipoc`, Tier 1, dict, 6 sub-fields** (§10.8) |
| Measure process map | Coaching content, no field | **`detailed_process_map`, Tier 1, dict, 6 sub-fields** (§10.8) |
| Stability | Tier 2 rubric criterion, no field | **`stability_assessment`, Tier 1** (§10.8) |
| Experiment justification | Coaching content, no field | **`experiment_justification`, Tier 1** (§10.8) |
| Structured dicts | 1 (`control_plan`) | **3** (§10.8) |
| Before/after KPI chain | Implicit | **Explicit across Define → Measure → Control** (§10.8) |

Field counts: Define 15 · Measure 14 · Analyse 13 · Improve 13 ·
Control 15. Tier 1: 6 · 7 · 4 · 4 · 3.

### 0.8 — What Changed in 2.2.14 — how the coach teaches

The first SKILL.md review. Three changes to coaching behaviour, all
enforced by `COACHING_QUALITY_RUBRIC` every turn (§8.2).

| Area | Before | Now |
|---|---|---|
| Computation tools | **Six**-step pattern, opening with "explain why" | **Seven** steps, opening with **educate on the concept** — what it *is*, plain language, analogy, and what the numbers will mean (§8.2) |
| Asking for a field | Coach asks, then corrects | **Coach shows a completed example first**, explains why it works, then invites the Belt to build theirs |
| Methodology references | Unconstrained | **No external URLs.** Retrieve via `rag_lookup_methodology`, weave into the coach's own voice |

All five SKILL.md files rewritten to match: show-first per field, an
A→F session flow with a visible progress count, a Document Layout
section per phase for the live gate document, upload handling, and
`CoachingResponse` capture instructions.

### 0.9 — What Changed in 2.2.15 — the constitution catches up

Four facts had been ratified and written into
`REFACTORING_AGENT_IMPROVE.md` but never propagated here. **A constitution
that lags the document it governs is worse than one that is merely
incomplete** — it actively misleads, because implementers quote it.

| Area | v2.2.14 | v2.2.15 |
|---|---|---|
| `PhaseState` | 15 fields | **17** — adds `hop_results`, `synthesis_output`; `coaching_plan` typed `CoachingPlan` (§10.1) |
| Middleware stack | Five | **Eight** — adds `ToolRetryMiddleware`, `ContradictionDetectionMiddleware`, `CoherenceMiddleware` (§8.1, §8.7–§8.9) |
| State injection hook | `before_model` | **`before_agent`** (§8.1, §8.5) |
| Layer 2a coherence | Unattributed | **`CoherenceMiddleware`**, not the `validation_stack` node (§8.9, §9.2) |
| `improve_evidence_index` | 5 fields | **7** — `phase`, `uploaded_at` ratified, pending reindex (§7.3) |
| `improve_case_index` vector | `embedding` | **`content_vector`** ratified, pending reindex (§7.3) |

**Two internal contradictions in this file were also corrected**, both
found while propagating:

- **§4.4's `create_agent` example showed
  `response_format=ProviderStrategy(PhaseOutput)`** — contradicting §4.6
  and §10.7, which both mandate `CoachingResponse` on the executor and
  explicitly forbid a `{Phase}Output` there. It is the example an
  implementer copies, so it mattered more than an ordinary stale line.
- **§9.2 did not say which mechanism implements each validation layer.**
  Layer 2a fires every turn and so cannot live in the gate-boundary node;
  2b–2d fire once and cannot live in middleware. The stack is one concept
  across two mechanisms, and the table now says which is which.

**Both Azure schema changes are ratified but NOT applied.** Write code
against the live schema until the reindex runs (§7.3).

### 0.10 — What Changed in 2.2.16 — two wrong keywords, and one document fewer

**Three of these are API facts this file got wrong.** They were found by the
Task 3B verification pass against live documentation and are recorded in
`docs/_archive/BIBLE_VERIFICATION_LOG.md`. (archived to docs/_archive/; canonical: CLAUDE.md §0.10)

| Area | v2.2.15 | v2.2.16 |
|---|---|---|
| `ModelRetryMiddleware` | `retries=2` | **`max_retries=2`** — `retries=` does not exist and **raises at construction** (§8.1, §8.7) |
| `create_agent` prompt | `prompt=` | **`system_prompt=`** — `create_react_agent` took `prompt`; `create_agent` renamed it (§4.4) |
| `AgentMiddleware` hooks | "the six hooks", stated as closed | **The six *we use*.** `dynamic_prompt()`, `hook_config()` and `configure_trace_policy()` also exist (§8.1) |
| Graceful shutdown | `RunControl.request_drain()`, cited as fact | **UNCONFIRMED — MAY NOT EXIST.** No work may be scheduled against it (§3.6) |
| Version targets | 1.2.10 / 1.3.11, already stale | **Verified 2026-08-21**, plus the `langchain-core` ≥1.6.0 jump (§16.1) |
| Binding documents | Three | **Two** — `ARCHITECTURE.md` absorbed into `../AGENTIC_ARCHITECTURE_REFERENCE.md` (§0.1) |

**The `max_retries` error is the one to learn from.** It sat inside the
canonical middleware stack — the block an implementer copies verbatim — from
adoption until 2026-08-21. `ToolRetryMiddleware` was verified against the
reference when it was added and was always correct; `ModelRetryMiddleware` was
adopted earlier and never re-checked. **The two share a parameter vocabulary,
which is exactly the situation where remembering one and inferring the other
goes wrong.** §16.3 is not a formality.

**Every `§`-citation in this file now points at `../AGENTIC_ARCHITECTURE_REFERENCE.md`.**
The former **v2.2.16** `ARCHITECTURE.md §X` and `REFACTORING_AGENT_IMPROVE.md §X`
references were resolved through the reference's Appendix A. Nine items of
**v2.2.16** `ARCHITECTURE.md` content that had no home in the reference were written into it
in the same pass, so the absorption is now real rather than declared.

### 0.11 — What Changed in 2.2.17 — a rule that banned what another rule required

**§5.1 named `search_methodology` and `search_evidence` as the retired
retrieval-tool names. Both were wrong, and the second was actively harmful.**

| | |
|---|---|
| `search_methodology` | **Exists nowhere in the codebase.** Never has |
| `search_evidence` | **Exists and must keep existing** — a live function in `knowledge/retriever.py` that §7.2 names as one of three that must raise `KnowledgeSearchError` rather than return `[]` |

**So §5.1 banned a name §7.2 mandated.** Two rules in this file, in direct
contradiction, on a string.

**Why it mattered more than a typo:** the Refactoring Procedure verifies
retirement by `grep-absence`, which checks these strings **literally**. A check
written from the old list would have passed — matching a name that never
existed — while all three real retired names survived untouched. **A
verification that cannot fail is worse than no verification**, because it is
recorded as evidence.

| Area | v2.2.16 | v2.2.17 |
|---|---|---|
| Retired retrieval-tool names | `search_methodology`, `search_evidence` | **`search_improve_knowledge`, `search_improve_cases`, `search_improve_evidence`** (§5.1) |
| Retriever-layer names | Implicitly retired by §5.1 | **Explicitly NOT retired** — the tool layer is replaced, the retriever layer keeps its names (§5.1, §7.2) |
| Cross-agent tools | Unaccounted for | **A distinct third category, present and deliberately unbound** — `../AGENTIC_ARCHITECTURE_REFERENCE.md` §29.4 (§5.1, §14) |

**The cross-agent addition went through the reference's §56 amendment procedure**,
not directly into a rule here: decision recorded at `docs/_archive/DECISIONS.md` §Q1,
section added as reference §29.4, its version incremented to 1.1. This file
carries only the pointer, because the disposition is a design fact and §29.4 is
its canonical home.

### 0.13 — What Changed in 2.2.19 — contradiction detection redesigned

**`ContradictionDetectionMiddleware`'s mechanical dict comparison is deleted.**
It could not do its job, in three independent ways verified against the
schemas: it read `store.get(..., current_phase)`, which `gate_apply` does not
write until phase end; it matched on field names where **38 of 41 content
fields are unique to exactly one phase**; and the 3 shared names are all prose,
where `!=` fires on any rewording. Repairing the first leaves 3 prose fields
out of 41.

| Area | v2.2.18 | v2.2.19 |
|---|---|---|
| Detection | Deterministic dict comparison in middleware | **Semantic, by the coach**, via SKILL.md instruction (§8.3) |
| `CoachingResponse` | 3 fields | **4** — adds `contradiction_flag` (§10.7) |
| The middleware | Compares, then raises | **Reads the flag, then raises** (§8.8) |
| LLM calls added | — | **None.** The flag rides the existing response call |
| Position, hook, order | 6, `after_agent` | **Unchanged** |
| Cascade (§9.5) | — | **Unchanged.** Only detection changed |
| `CoachingResponse` field additions | Ungated | **Require an amendment** (§18) |

**Detection is now best-effort semantic rather than illusory-deterministic.**
The old mechanism's danger was looking deterministic while detecting nothing.
The all-gate-fields tab (§13) is the acknowledged human backstop.

**Provenance: the first confirmed course-pattern fit-bug.** The middleware was
adopted as a named pattern from the Edureka course without checking its
mechanism against DMAIC's phase-partitioned, differently-named, gate-written
state. **A pattern adopted by name carries its source's assumptions about state
shape, write timing and naming, and those assumptions are invisible in the
name.** Other course-derived components are flagged for the same review. Full
record: `docs/_archive/DECISIONS.md` §R1.

### 0.14 — What Changed in 2.2.20 — the supervisor does not route

**A dead routing function was deleted from the architecture reference's §15.**
`route_after_phase` returned `"next"` / `"escalate"` / `"retry"` — labels wired
to nothing — and read `state["gate_attempts"]` off `SupervisorState`, where
**that field does not exist** (§10.1's seven fields). It would have raised
`KeyError` **on the gate-failure path specifically**, which is the last place a
latent bug should sit.

**It contradicted the static edges printed directly above it.** A phase
transition is either static or conditional; it cannot be both. Static is
correct, and **safe for a reason worth stating**: a subgraph reaches `END` only
through `gate_apply`, which runs only after Belt approval — so **reaching `END`
means the gate passed**, and there is no branch for the supervisor to make.
Retry and escalation resolve inside the phase (§3.3, §9.2, §3.5).

| Area | v2.2.19 | v2.2.20 |
|---|---|---|
| Supervisor routing | Static edges **and** a conditional router | **Static edges only** — the router is deleted |
| §9.1 step 9 | "Supervisor reads `gate_passed`, routes onward" | **"The parent's static edge advances"** — the supervisor makes no decision |
| `gate_attempts` | On `PhaseState` | **Unchanged.** Not added to `SupervisorState`, and route scope remains banned (§14) |
| Level 2 routing | — | **Untouched.** `Command` inside subgraphs stays correct |

**Step 9's wording was tightened deliberately.** "Routes onward" was not wrong,
but it was the last phrasing from which the wrong mental model could be
re-derived — **loose-but-plausible language is how a deleted design regrows.**

> **The finding worth carrying forward:** `route_after_phase` was **already
> prohibited** when it was written. §14 bans holding `gate_attempts` in route
> scope, and that function was route scope reading `gate_attempts`. **The rule
> was correct; nothing enforced it against a design example inside a governance
> document** — the drift registry checks code, and `agent-improve/**/*.md` is
> path-excluded for the good reason that a governance file must be able to name
> a construct to forbid it. **Third instance of one pattern: a correct rule
> paired with a check that structurally cannot see what it governs.** Full
> record: `docs/_archive/DECISIONS.md` §R2.

### 0.15 — What Changed in 2.2.21 — `PhaseState` learns who and where it is

**Three specified functions read case identity and phase off `PhaseState`,
which declared neither.** `phase_error_recovery` read `state["case_id"]` and
`state["phase"]`; `analyse_executor_node` read `state["current_phase"]`;
`gate_apply_node`'s Store write needed `case_id`. **The same defect class as
`route_after_phase`** (§0.14): specified code reading state a schema does not
declare, with nothing able to see the disagreement.

| Area | v2.2.20 | v2.2.21 |
|---|---|---|
| `PhaseState` | 17 fields — 3 plumbing, 14 content | **19 fields — 2 identity, 3 plumbing, 14 content** (§10.1) |
| Case identity inside a subgraph | Undeclared; read from three notional sources | **`PhaseState.case_id`**, copied down by the input mapper (§10.1) |
| Phase identity inside a subgraph | Undeclared | **`PhaseState.current_phase`**, copied down by the input mapper (§10.1) |
| Writer | — | **Input mapper only.** Read-only inside the subgraph, never written back up |
| The amendment trigger | "a fifteenth `PhaseState` **content** field" | **Any new `PhaseState` field, whatever category** — the old wording was an enforcement hole |
| Boundary mapper execution site | Unstated | **Inside the parent's uniquely-named node function** for that phase |

**Ruling A2 was chosen over reading `case_id` from config and phase from a
build-time constant, and the reason is the defect itself:** mixing sources is
what made this latent. Phase-internal code now takes both from its own state
and from nothing else.

**The copy-down is not a second writer.** The parent field and the child field
are two fields on two schemas; the child's is derived from the parent's exactly
once, at entry. `SupervisorState.current_phase` keeps its single writer
(§10.1). **Check: grep every node return dict for `case_id` or `current_phase`
as a key — any hit is a violation.**

> **The trigger correction matters more than the two fields.** §56's
> `PhaseState` trigger fired only on a *fifteenth content field*, so a field
> could be added, declared non-content, and skip the amendment gate on a
> category label. **The two fields added here would themselves have slipped
> through it.** A gate whose scope is set by a label the adder chooses is not a
> gate. Corrected in the same commit — the reference's §56 now fires on any new
> `PhaseState` field. Full record: `docs/_archive/DECISIONS.md` §T1.

### 0.16 — What Changed in 2.2.22 — the hop cap starts firing

**`remaining_steps` was read off `PhaseState` and never declared.** §26 of the
architecture guards the Analyse multi-hop chain with
`state.get("remaining_steps", 10) <= 2` — and with the field undeclared, that
`.get` returned **10 on every call, forever.** The guard could not fire, and
the five-hop cap §3.7 mandates has never been enforceable.

| Area | v2.2.21 | v2.2.22 |
|---|---|---|
| `PhaseState` | 19 fields | **19 author-populated + 1 engine-managed = 20 declared** (§10.1) |
| `remaining_steps` | Read, never declared | **Declared `remaining_steps: RemainingSteps`**, from `langgraph.managed` (§10.1) |
| Who populates it | Nobody — hence the bug | **LangGraph's execution loop.** The input mapper MUST NOT |
| The `10` default | Masked the defect | **A bug artifact. Gone** |
| The 5-hop rule | Unenforceable | **Unchanged, and now actually fires** |

**Declaring a managed value is what activates it.** `RemainingSteps` resolves to
`Annotated[int, RemainingStepsManager]`, and the manager returns
`scratchpad.stop - scratchpad.step`. Verified against the installed LangGraph
**1.2.11** — import path, type and source all read directly, not inferred.

> **The failure mode is the one this file keeps naming.** A cap that cannot fire
> is not a loose cap; it is **a check recorded as evidence while proving
> nothing.** `.get(key, default)` on an undeclared key never raises, so nothing
> anywhere reported that the budget was fictional. Full record:
> `ARCHITECTURE.md` §66 (G-04, closed) and its S-C02 entry.

### 0.17 — What Changed in 2.2.23 — the subgraph learns to route

**Level 2 routing existed as a rule with no design.** §15 said `Command` inside
subgraphs; §13 drew a branch; **no `Command(goto=…)` was specified anywhere**,
and what a Belt REJECT did was stated nowhere at all.

| Area | v2.2.22 | v2.2.23 |
|---|---|---|
| Field / gate decision | Drawn after the executor | **The planner owns it** — the executor returns plainly and emits no routing `Command` (§1.3, §17) |
| `gate_attempts` | Increment site unstated | **Once, at `validation_stack` entry.** A partial stack still costs an attempt |
| Escalation hop | Unstated | `Command.PARENT` — **the only use of it in this architecture** |
| Belt REJECT | Undefined | **Loops to the planner with a mandatory reason** (§9.1) |
| `PhaseState` | 19 author-populated + 1 managed | **20 + 1 managed, 21 declared** — adds `rejection_feedback` (§10.1) |

**`rejection_feedback` is a third actor at a third moment.** `validator_feedback`
is what the validation layers said about the AI's output at step 2; `belt_edits`
is what the Belt corrected at step 5; **`rejection_feedback` is why the Belt
refused at step 7.** Merging any two of the three would have the coach read one
actor's intent as another's — the conflation the original single `feedback`
field was split to end.

> **The reason is mandatory, and that is the ruling rather than a nicety.** A
> rejection with no reason gives the coach nothing to change, so the next turn
> reproduces the one just refused — the Belt rejects again, and the loop is a
> loop rather than a conversation.

**Two dependencies are recorded, not assumed.** DP1's "field complete" predicate
needs the per-phase field ordering (**G-38**, open), and the escalation exit
needs a node name (**G-34**, open). The *structure* is settled; those two are
not, and `ARCHITECTURE.md` S-F13 says so at the point of use rather than in a
footnote.

### 0.18 — What Changed in 2.2.24 — two stale figures, corrected on the record

**This entry exists because §0 forbids the silent fix.** Both corrections below
are figure syncs, not rule changes — but a binding file whose numbers drift is a
binding file that gets quoted wrongly into implementation prompts, and §0 routes
every change to this file through a numbered entry regardless of how small the
change looks. **Tracked as WATCH 8** in `docs/CONTINUITY.md`, deferred twice
precisely so both halves could land together here rather than half-landing in a
feature commit.

| Area | v2.2.23 | v2.2.24 |
|---|---|---|
| Methodology corpus (§7.2) | "218 carry `general`" | **259** — the corpus was rebuilt and reclassified (commit `871637f`) |
| Define gate-required fields (§9.7) | 6, with 5 Tier 2 | **12 — all of them, no Tier 1 / Tier 2 split** (§39.1 / Option A) |
| Define field counts (§10.7) | 15 total · 6 · 5 · 4 | **16 total · 12 required · — · 4** |

**The `general` count moved because the index was rebuilt, not because the rule
changed.** `phase_relevance`'s cross-phase value is still `general`, still never
`phase` and never `all` — that rule is unchanged and remains the point of §7.2.
What changed underneath it is the corpus: `improve_knowledge_index_v3` classifies
by LLM rather than by keyword counting, and 259 of its 1,184 documents land on
`general`. **The old figure described an index that is no longer bound.**

**Define is now the one phase with no Tier 2, and that is a ruling rather than a
drift.** Option A, ratified 2026-08-26: every Define field blocks the gate, so
`DEFINE_REQUIRED_FOR_GATE` is the whole coached list and **there is no
`acknowledged_gaps` path out of Define** — nothing is skippable, so nothing can
be recorded as consciously skipped. `target_metric` joins the schema;
`business_case`, `target_date` and `secondary_metrics` move from Tier 2 into the
required set. **The other four phases keep both tiers**, each settled at its own
phase review, so §9.7's two-tier machinery below is unchanged for them.

> **Why `baseline_metric`, `target_metric` and `target_date` stay discrete fields.**
> They read as redundant against `goal_statement` and are not. That field is the
> human-readable SMART sentence; these three are the **machine-readable values
> Control extracts** to compute target-vs-actual. Folded into prose, Control has
> nothing to compare. Anyone "simplifying" them away breaks the measurement
> thread one phase before the breakage is visible (§10.7, §39.1.2).

**Rule numbers are untouched.** No section renumbered, so
`.claude/config/deprecated_patterns.yaml`'s citations (§4.6, §4.5, §3.6, §4.4)
still resolve and §0.2 is satisfied. Neither hook parses this file —
`session-start-context.py` reads `docs/REFACTORING_PROCEDURE.md`, and the drift
check reads the registry YAML — so this edit changes no hook behaviour.

**Sections 0.6 and 0.7 keep their original figures.** They are dated "What
Changed" records of 2.2.11 and 2.2.12 and say what was true then; correcting
them would destroy the record this log exists to keep. **This entry supersedes
them**, and the live figures are the tables in §9.7 and §10.7.

### 0.19 — What Changed in 2.2.25 — Define's baseline field is `baseline_metric`

**Founder ruling, 2026-08-26. This reverses a rename made earlier the same day**
(commit `885defc`, which renamed `baseline_metric` → `baseline` on the authority
of `docs/_archive/DEFINE_FINALIZATION_2026-08-26.md`). **`docs/CONTINUITY.md` v4.1 §5 is
authoritative**: the field is `baseline_metric`. (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.1.2)

| Area | v2.2.24 | v2.2.25 |
|---|---|---|
| Define field #5 (§9.7) | `baseline` | **`baseline_metric`** |

**The reason is a name collision, and it is a real one.** Measure carries
`baseline_mean` and `baseline_sigma`; `detailed_process_map` carries
`baseline_kpis`. **A bare `baseline` sitting among those three reads as a generic
prefix** rather than as Define's discrete current-state value — and that is
precisely the ambiguity the measurement thread cannot afford, since Control has
to find this field by name to compute target-vs-actual. **`baseline_metric` pairs
with `target_metric`** and makes the Define-sets / Control-compares relationship
legible without reading the surrounding prose.

**The three sibling fields are untouched** — they are the collision, not
casualties of it. So is every English use of the word: *a rough baseline*, *a
baseline Cpk*, *the Measure baseline*. **The rename is of one identifier, not of
a vocabulary.**

> **§0.18's note was corrected in place rather than superseded.** It states a
> live rule — why the three measurement-thread fields stay discrete — rather than
> a historical count, so leaving the old field name there would have left a rule
> naming a field that no longer exists. **§0.6 and §0.7's dated figures are still
> untouched**, for the reason §0.18 gives: they record what was true then.

### 0.20 — What Changed in 2.2.26 — the metric registry, and Measure specified

**A founder-ratified change set in six steps**, recorded here as one amendment
because it is one decision: **a project tracks N metrics, and the architecture
must trace each of them across five phases by name.** Full detail:
`ARCHITECTURE.md` v1.15 and §39.2. Prompt of record:
`docs/_archive/CLAUDE_CODE_PROMPT_measure_naming_registry.md`. (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.2)

| Area | v2.2.25 | v2.2.26 |
|---|---|---|
| Define field #5 | `baseline_metric` | **`baseline_estimate`** |
| Define field #8 | `target_metric` | **`target_value`** |
| SIPOC key | `process_kpis` | **`process_metrics`** |
| Detailed-map key | `baseline_kpis` | **`baseline_metrics`** |
| Measure → Analyse | `vital_few_xs` | **`vital_few_drivers`** |
| Measure prioritisation | `xy_matrix_summary` | **`driver_priority_summary`** |
| Control result | `post_improvement_metric` | **`post_improvement_metrics`** |
| Same field on all five (§10.7) | **two** | **three** — adds `phase_metrics` |
| Define gate-required (§9.7) | 12 | **13** — adds `metric_definitions` |
| Field counts (§10.7) | 16/14/13/13/15 | **18/15/14/14/16** |

**`baseline_mean`, `baseline_sigma` and `post_improvement_cpk` are untouched**,
and that is the point of the two-tier rule rather than an exception to it:
**spell out what is cryptic or local; keep what is industry-standard.** Those
three, and all 20 computation-tool names, are terms a Belt meets in every
textbook and every audit. What changed for the tools is only the first line of
each docstring, which now leads with the plain concept before the standard term.

**The registry is two new structured fields, and a fourth exception to §10.6.**
`metric_definitions` (Define's registry of `{name, unit, meaning}`) and
`phase_metrics` (a per-phase placeholder on all five schemas) are `list[dict]`
for **the same reason and in the same class** as the three cross-phase reference
dicts: **the grader traces a metric by key equality on `name`.** Prose cannot
carry that — *"Error rate: 12.3%"* and *"error rate (%)"* are one metric to a
reader and two to a matcher. **Scalar values inside both stay strings**; the
exception is the container, never the typing law.

> **`phase_metrics` is authoritative; the scalars mirror it.** `baseline_mean`,
> `baseline_sigma`, `baseline_estimate`, `target_value` and
> `post_improvement_metrics` are **the primary metric's mirror**, kept because a
> gate document reads better with a named scalar than with a list index, and
> because Control's comparison was specified against them first. **They MUST
> equal that metric's `phase_metrics` entry; additional metrics live only in
> `phase_metrics`.** Enforced as a `gate_apply` assembly invariant that
> **raises** (`core/metrics.py`, `ARCHITECTURE.md` S-F28 B1–B5), because two
> stores holding one value drift invisibly: both reads succeed, and the
> disagreement only surfaces a phase later when Control reads whichever it got.

**Define's 12-position coached walk is unchanged.** `metric_definitions` is
gate-required but captured **inside position 5**, where the Belt names what they
are measuring — asking "what are we measuring" and "what is it today" as two
coached positions would make the Belt say it twice. **Twelve coached, thirteen
gate-required**, and `field_index` still walks twelve.

**Metric literacy is a new coaching requirement** (§43.7, §32): the coach
teaches **the metric** — what it is, why it matters in this phase, how to read a
good or bad value — as distinct from the seven-step education on **the
statistic**. Applied in full to Measure's SKILL.md; the other four inherit at
their reviews.

> **§0.6, §0.7, §0.18 and §0.19 keep their original field names**, for the
> reason §0.18 gives: they are dated records of what was true then. A rename
> that edits the amendment log destroys the trail the log exists to keep. **The
> live names are §9.7's and §10.7's tables.**

> **The root reference temporarily diverges, and this is expected.**
> `../AGENTIC_ARCHITECTURE_REFERENCE.md` was **deliberately not renamed** — it is
> the platform document for all three agents, and §0.12 states the two are
> expected to diverge rather than be kept identical. **Until the back-port,
> §-citations from this file into root sections may name the old field names**
> (`baseline_metric`, `vital_few_xs`, `process_kpis` and the rest) while Improve
> uses the new ones. **The rules those sections state are unaffected**; only the
> field spellings differ. Owed at back-port once Improve settles (§8).

### 0.21 — What Changed in 2.2.27 — Analyse specified; the reference dicts name their metric

**Analyse is the third ratified per-phase specification** (`ARCHITECTURE.md`
§39.3, v1.16). Nothing in this file's rules changes shape; **two facts it states
do.**

| Area | v2.2.26 | v2.2.27 |
|---|---|---|
| Cross-phase reference dicts (§10.6) | three reference keys | **four** — adds `references_metric_name` |
| Grader link verification (§8.2) | reads the named field's value | **resolves the `phase_metrics` entry by metric name**, then reads the value from it |
| Analyse tiers (§9.7) | 4 Tier 1 / 5 Tier 2 | **unchanged — confirmed at review** |
| `AnalyseOutput` count (§10.7) | 14 | **unchanged** |

**`references_metric_name` closes F-13.** With one metric, "references Measure's
`baseline_mean`" is unambiguous. **With two it is not:** `baseline_mean` is only
the *primary* metric's mirror, and the others live solely in `phase_metrics`, so
a hypothesis referencing the bare scalar resolves against whichever metric
happens to be primary — **comparing two different things while looking
verified.** The key turns a positional guess into a lookup. It is on **all three**
reference dicts so the shape is settled once; Analyse populates it now, Improve
and Control at their own reviews.

> **This is a key INSIDE the dict value, not a new schema field.** No
> `{Phase}Output` count moves — Analyse stays 14 — and §10.7's three-fields rule
> is untouched. The dicts were already the exception to the string law (§10.6);
> this adds a fourth key to that exception, not a fifth exception.

**Two methodology guards are now Tier 1 rubric criteria** for Analyse:
**correlation is not causation** — an association result requires a stated
mechanism before it counts as a root cause — and **statistical is not practical
significance** — a validated cause explaining a trivial share is coached back,
not passed. **Both produce gate documents that read as complete**, which is
exactly why they are checked explicitly rather than left to the grader's overall
impression.

### 0.22 — What Changed in 2.2.28 — Improve specified; Define's tool block added

**Improve is the fourth ratified per-phase specification** (`ARCHITECTURE.md`
§39.4, v1.18). **No rule in this file changes shape**; one §32 compliance gap
closes.

| Area | v2.2.27 | v2.2.28 |
|---|---|---|
| Improve tiers (§9.7) | 4 Tier 1 / 5 Tier 2 | **unchanged — confirmed at review** |
| `ImproveOutput` count (§10.7) | 14 | **unchanged** |
| Define's bound tool (§5.2, §8.3) | no seven-step block | **`calculate_expected_savings` block added** |

**The §32 gap is the substantive part for this file.** §8.3 requires every
SKILL.md to carry the seven-step sequence for **every computation tool in its
phase's `allowed-tools`**, and §5.2 binds `calculate_expected_savings` to
Define. **Define's SKILL.md carried no block for it** — so the rule was stated
and unmet in the one phase whose coaching content is otherwise the ratified
exemplar. The block is now in `ARCHITECTURE.md` §39.1.7 and in the Define
SKILL.md at the matching position, after the `target_value` field: the tool
needs both `baseline_estimate` and `target_value` before it can compute
anything, so placing it earlier would coach a calculation the Belt cannot yet
supply inputs for.

> **This was a real gap, not a formatting nit.** A Belt reaching Define's one
> computation tool with no seven-step block gets exactly the raw-output dump
> §8.2's rubric fires on every turn to prevent — the coach would run the tool
> and hand back a number with no concept taught and no interpretation.

**Improve's two Tier-1 rubric guards** are worth knowing when quoting §9.7 into
an implementation prompt: **the solution must trace to the validated root
cause** (resolved by lookup against Analyse's gate document, not by judgment),
and **pilot before rollout** — practical *and* statistical significance, the
same two-gate test Analyse uses. **DOE belt-gating is a rubric criterion, not a
preference**: all three answers to `experiment_justification` are valid, DOE is
recommended for Black Belts and suppressed for Green Belts, and **the question
is asked of both**.

### 0.23 — What Changed in 2.2.29 — Control specified; the five-phase spec is complete

**Control is the fifth and final ratified per-phase specification**
(`ARCHITECTURE.md` §39.5, v1.19). **There is no §39.6.**

| Area | v2.2.28 | v2.2.29 |
|---|---|---|
| `ControlOutput` (§10.7) | 16 | **17** — adds `actual_close_date` |
| Control tiers (§9.7) | 3 Tier 1 / 8 Tier 2 | **3 Tier 1 / 9 Tier 2** |
| Per-metric comparison | undefined | **`phase_metrics` is authoritative for all N** |

**`actual_close_date` closes F-12** — the achieved completion date, paired with
Define's planned `target_date`. **Tier 2, and that is the ruling:** a slipped
date does not invalidate the improvement, exactly as Define's target is a
planning parameter rather than a result (§39.1.2).

**F-14 closes with a division of labour, not a new field.** `phase_metrics`
holds every metric's `baseline` / `target` / `actual` / `delta` / `met`;
`post_improvement_metrics` stays the **primary** metric's Tier-1 deterministic
link back to Measure's `baseline_mean`. **The grader grades every entry** — a
project that met its primary metric and silently missed a secondary one has not
fully succeeded.

> **Control's single-authority shape is the odd one, and it is written down
> rather than inferred.** `post_improvement_metrics` is a reference dict whose
> value sits under `metric`; the `phase_metrics` entry calls the same number
> `actual`. **Two names for one number is precisely the drift the invariant
> exists to catch**, so `core/metrics.py` carries an explicit mapping for
> Control and the test suite pins it in both directions.

**Three Tier-1 guards in `CONTROL_RUBRIC`**, worth knowing when quoting §9.7
into an implementation prompt: **link back to the baseline** — the only Tier-1
cross-phase reference in the system; **the control plan complete AND
delivered** — all five sub-plans populated *and* a named owner who accepted, so
a plan authored but never run fails; and **stability before capability again**,
before `post_improvement_cpk`.

**All five DMAIC phases are now specified.** What remains is build, not
specification: **WATCH 7** (`orchestrate.py` still writes v1 field names),
**G-27** (boundary mappers) and **G-28** (gate assembly for the four phases
beyond Define), and the root-reference back-port.


### 0.25 — What Changed in 2.2.31 — §4.5 covers the write side

**§4.5 said "read `response.content_blocks`" and nothing about the messages we
construct.** Step 6.3 shipped two middlewares that built a `SystemMessage` by
f-string over an existing `.content`, and the rule as written did not forbid it.

| Area | v2.2.30 | v2.2.31 |
|---|---|---|
| §4.5 scope | **Reading** model responses | **Both directions** — messages we write as well as responses we read |
| Building message content | Unstated | **Never interpolate or concatenate an existing message's `.content`** — construct with `content_blocks=` |
| Plain-string construction | Unstated | **Fine.** `AIMessage(content="text")` needs no blocks |
| Testing it | Unstated | **A list-content fixture is required**; a string-content one passes both implementations |
| §14 no-go list | One entry, read side | **Two** — the write side is named separately |

**Why the gap was invisible.** Step 2.6 converted twenty sites, and all twenty
were `response.content` — so the rule got filed under *reading*, and writing
never came up. `pattern-3-response-content-parsing` matches
`response\.content\s*\[`, which is the read side too. **Nothing in the registry
or this file addressed construction**, and the defect passed writing, review,
716 green tests and a live trace before it was caught by a question.

**The list-content fixture is the load-bearing half.** `SystemMessage.content`
is `str | list[dict]`, and a string-content message behaves identically under
the correct and the broken implementation. **Only a multi-part fixture
distinguishes them** — which is why the rule names the test requirement rather
than leaving it to judgment.

**No rule was renumbered**, so `deprecated_patterns.yaml`'s four citations still
resolve and §0.2 is satisfied. **No registry pattern was added**: the prose rule
in this file is the mechanism for now, and a write-side pattern stays available
as its own governance commit.

**The reference back-port is owed, not done.** §21 is the platform section that
owns this and binds on all three agents; adding it there is a §56 amendment and
is queued with the other two at step 11.2 (`docs/CONTINUITY.md` WATCH 27).
Full record of the defect: `docs/_archive/DECISIONS.md` Part AH2.

---

### 0.26 — What Changed in 2.2.32 — §3.7 stops specifying the wrong cap

**§3.7 carried `recursion_limit = 2 * max_hops + 1 = 11` as the hop cap, and
`../AGENTIC_ARCHITECTURE_REFERENCE.md` §16 explicitly rejects it.** §26 ratified
`RemainingSteps` instead, in August 2026. This file never caught up, and since
step 6.2 the build has followed this file — which is the correct precedence, and
exactly why a stale rule here is expensive.

| Area | v2.2.31 | v2.2.32 |
|---|---|---|
| The hop cap | `recursion_limit = 11` | **A count of `rag_lookup_*` calls**, kept in the executor |
| `recursion_limit` | The cap | **A backstop only**, 50, against a genuine infinite loop (§16) |
| `remaining_steps` | Not mentioned in §3.7 | **The graceful off-ramp** — read at the executor's top; low means compose from what is in hand (§26, S-F09 B1) |
| `GraphRecursionError` | The primary guard | **Belt-and-braces against a bug.** Still MUST be caught |
| Units | Conflated | **Hops ≠ steps, and both guards are needed** — see below |

**`recursion_limit=11` was also arithmetically short**, which is what made the
symptom a see-saw rather than a clean failure. Measured on **both** LangGraph
1.1.10 and 1.2.11, identically: a coach making its five permitted hops at
`recursion_limit=11` consumes all eleven steps on the hops themselves and raises
`GraphRecursionError` **before** the model can compose an answer. Four hops fit;
five never did. A well-behaved five-hop turn could only ever end in the cap
message, so prompt wording moved the failure between phases without removing it
— WATCH 26 (`docs/_archive/DECISIONS.md` Part AK3).

**Hops and steps are different units, and this was the substantive design
question.** `remaining_steps` is `recursion_limit` minus graph-node transitions.
The coach's whole tool-calling loop runs inside ONE node — the executor invokes
its agent with `ainvoke` and returns — so the phase subgraph's counter moves by
**1 per executor turn regardless of hop count**, measured. It can therefore
never enforce a five-hop rule, and a five-hop counter can never notice the graph
running out of room. **Both guards exist because they answer different
questions.**

**`remaining_steps` does cross the subgraph boundary**, which is the property
§26 chose it for, and it was measured rather than assumed — both ways a
subgraph can be entered, and on both library versions.

**Both measurements were taken twice, and that is a finding of its own.**
`agent-improve/.venv` runs LangGraph 1.2.11 / LangChain 1.3.16; the repo-root
`.venv` — which the session-start hook reads, and which §16.1's *Installed*
column still reports — is at 1.1.10 / 1.2.13. **The results are identical on
both**, so nothing here rests on it. §16.1 and the hook are stale against the
venv that actually runs the code — its own governance commit, not this one. Declaring it is what
activates it — that was §0.16's fix and it still holds.

**`remaining_steps` has nothing to do with `step_log`**, the coaching record
declared beside it on the same state object. Same word, opposite meanings: one
is a LangGraph execution counter, the other is this project's audit trail. The
schema now says so at the declaration.

**This is a governance commit and lands alone**, per §0's amendment rule — the
code that follows it is step 6.7.

### 0.27 — What Changed in 2.2.33 — the universal eight, and `PhaseState` gains `asks`

**Two founder rulings, 2026-09-09, both prerequisites for step 6.12.** Full
record: `docs/_archive/DECISIONS.md` Part AR.

| Area | v2.2.32 | v2.2.33 |
|---|---|---|
| The universal set | **seven** | **eight** — adds `load_evidence_series` (§5.1) |
| Per-phase totals (§5.2) | 8 / 15 / 12 / 8 / 12 | **9 / 16 / 13 / 9 / 13** |
| Measure against the 16 cap | 15, one under | **16, the ceiling exactly** |
| `PhaseState` | 20 author-populated + 1 managed | **21 + 1 managed, 22 declared** — adds `asks` (§10.1) |
| §10.1's caption | said nineteen / fourteen content / twenty | **corrected** — it had been stale since §0.17 |

**`load_evidence_series` is universal because of what it does, not because
nothing else fits.** §5.2's twenty computation tools are pure functions with no
I/O — that is what makes them unit-testable without a network — and this reads
a blob. **The universal set is already where the I/O-performing tools live**:
all three `rag_lookup_*` tools call Azure AI Search, and this one calls Azure
Blob. Classification, not exception.

**It exists because similarity search is the wrong mechanism for loading data.**
You do not fetch five hundred rows by vector similarity. **Retrieval finds WHICH
file; a deterministic fetch loads THE VALUES**, and the split is what lets a
computation tool receive a Belt's numbers without the coach transcribing them —
the §6.4 anti-pattern performed on the platform's own evidence.

> **⚠ THE 16 CEILING NOW HAS NO MARGIN, AND THAT IS THE PART TO CARRY FORWARD.**
> Measure sits at exactly 16. **A ninth universal tool breaks §5.2 for Measure on
> the day it is added**, and the two universal tools still unbuilt —
> `check_gate_status` (7.1) and `request_human_approval` (7.5) — are already
> counted inside the eight. **Revisit the ceiling before adding a ninth, not
> after.** A per-phase total that is legal only because nothing further has been
> added is a constraint with no margin, and the margin is what usually gets
> discovered by exceeding it.

**`asks` is a §56 amendment and could not have been anything else.** §10.1's rule
is that **any** new `PhaseState` field requires one, whatever category it is
placed in — the wording §0.15 tightened precisely so a field could not skip the
gate on a category label.

**`artifacts["asks"]` was considered and rejected on three grounds**, and the
first is the one that decides it:

| | |
|---|---|
| **Whose record it is** | `artifacts` holds **the Belt's captured values**. An ask is a **system** record — the coach's own request. §10.6's precedent turns on that distinction, not on convenience |
| **What reads `artifacts`** | Gate assembly and `check_gate_status()` both walk it; an `asks` key would land in every gate document and need excluding by name from the completeness computation |
| **§10.6's string law** | Every value in `artifacts` is a string with four ratified exceptions. A structured `asks` list needs a **fifth** — so the "no amendment" route costs an amendment to the typing law instead, and a worse one |

**The case blob was rejected on §10.4.** The case record is written *"on case
create, on gate pass, on file upload — never mid-conversation"*. **An ask is
born in a coaching turn**, and there is no sanctioned write moment between that
turn and the upload answering it moments later. Putting asks there would
reinstate the per-turn write §10.4 removed.

**No rule was renumbered**, so `deprecated_patterns.yaml`'s citations still
resolve and §0.2 is satisfied. **No code changed** — both rulings are
specification, and step 6.12 builds them.

---

### 0.28 — What Changed in 2.2.34 — the document set collapses to two

**FOUNDER RULING 2026-09-10.** Five documents were hand-maintained per build
step and three carried the same facts in different shapes. **Two are
hand-written from here:**

| Document | Holds |
|---|---|
| `ARCHITECTURE.md` | the design, the gap register, and what is built |
| `REFACTORING_PROCEDURE.md` | the plan — step specs plus Appendix D's step list |

Everything else is **generated from git, or frozen.**

#### THE SPLIT — where a decision goes now

| | Goes to | Why there |
|---|---|---|
| **The RULE** | `ARCHITECTURE.md`, as a §56 amendment **with a version bump** | Permanent, indexed, and what a build step is checked against |
| **The REASONING** | **the commit message body** | Already required, already permanent, already tied to the diff it explains |

**`DECISIONS.md` is CLOSED** — frozen at Part AU, historical, no new entries.
Nothing was deleted. It closed because its own *How to read this document*
requires `Status / Landed in / Source` on every entry, and that field appears
**40 times in Parts A–Q and zero times in Parts R–AU**. Closing it stated what
had already happened.

**The reasoning half is the load-bearing claim.** What was decided, what was
rejected, what an audit found, what you chose not to fix — all of it belongs
with the change it justifies. **A commit body is never re-read except when
investigating that commit, and that is the correct cost**: the moment you want
the reasoning is the moment you are already looking at the diff.

#### What this ends

Three documents held one fact in three shapes and a fourth summarised all of
them. Guard **rule 2** existed to keep two of them in step and checked only that
both had been *touched*, never that they *agreed* — and step 6.13 shipped with
them disagreeing about the next step while that rule passed. **Rule 2 is
deleted; its number is not reused.** The rules are 1, 2b, 3, 4, 5.

**`BUILD_TRACKER.md` is deleted** and `REVIEW_DECISIONS.md` archived. Build
completion is now **git log** — the highest `refactor(arch-v2): commit X.Y` —
and Appendix D's status column carries only what git cannot say: `BLOCKED`,
`GATED`, `EXTERNAL`. **No hook parses prose for done-ness any more**, which is
what fired twice: once on step 7.1 (2026-09-08) and once on step 6.16
(2026-09-10), the second because that step's description necessarily contains
the words "cursor" and "never done".

`ARCHITECTURE_STATUS.md` is **kept and stripped** — its *Re-running the counts*
block is the only thing in the repo that verifies a claim against the tree.
Converting it to generated output belongs to step **6.16**, which already
builds a generator and already reads it.

---

### 0.29 — What Changed in 2.2.35 — a finding is delivered as a visual

**FOUNDER RULING 2026-09-11.** Nothing about the architecture changed. What
changed is **how a finding reaches the person who has to act on it**, and it is
a rule — **§19 — how findings reach the founder** — because the failure it
closes has cost this refactor more than any code defect in it.

| | Before | From 2026-09-11 |
|---|---|---|
| **An output asking for a DECISION** | prose, the options described one after another | **a table** — one row per option, the full detail in the cells (§19.1 — a decision or an explanation is delivered as a visual) |
| **An output that EXPLAINS** — an audit finding, a mechanism, a breakage | prose threaded with section numbers | **a diagram or a table**, carrying the full detail (§19.1 — a decision or an explanation is delivered as a visual) |
| **A number or a code in human-facing text** | `6.20`, `§39.1.7`, `G-49` | **6.20 — the write paths**, **§39.1.7 — Define's state contract**, **G-49 — the executor ignores the tool its planner names** (§19.2 — never a bare number, never a bare code) |
| **Where it binds** | the board alone, from step 6.16 — the board is generated, not written | **the board, plus every report, brief, finding and reply** (§19.4 — where the rule bites, and the open item) |

**The reason is recorded so the rule is not read as a style note.** The largest
cost of this refactor has not been code. It has been **findings the founder
could not read, and therefore could not act on.** A correct finding that does
not reach a decision has not been delivered.

**What this amendment does NOT do.** No rule is renumbered, no schema changes,
and `.claude/config/deprecated_patterns.yaml` is untouched — §19 is a new
number after the last one and nothing moved, so §0.2 — rule numbers are
load-bearing is satisfied with no registry edit. The 1,128 parenthetical
`(§x)` cross-references already standing in this file and in `ARCHITECTURE.md`
are converted **as each rule is next amended, not in one sweep**, which is the
one scoping call in this amendment and is flagged for the founder at
§19.4 — where the rule bites, and the open item.

### 0.30 — What Changed in 2.2.36 — 8D is the structure for every fix

**FOUNDER RULING 2026-09-11.** Every **defect, modification or adaptation** is
worked as an 8D **before any fix is proposed** — not features, defects and
changes — and it is **enforced at the commit** rather than trusted.
**§20 — every fix is an 8D** holds the rule; **rule 6** of the commit-msg guard
holds the gate.

| | Before | From 2026-09-11 |
|---|---|---|
| **A defect's structure** | whatever the author reached for, per defect | **the nine disciplines**, D0 to D8, worked before a fix is proposed (§20.1 — the nine disciplines) |
| **A root cause** | one answer — why it happened | **two answers** — occurrence AND escape. *"Why did nothing detect this"* is separate, and usually the expensive one (§20.2 — three clauses carry the weight) |
| **An interim containment** | put in place, and lives on | **records its own removal condition**, or it becomes permanent (§20.2 — three clauses carry the weight) |
| **An empty discipline** | omitted, and reads as forgotten | **`NONE — <reason>`, never omitted.** An empty discipline is a finding (§20.2 — three clauses carry the weight) |
| **The commit body of a fix** | prose, in whatever shape | **five labels the guard checks** — D2 IS, D2 IS-NOT, D4 OCCURRENCE, D4 ESCAPE, D5 FIX, D7 PREVENT (§20.4 — enforced at the commit, as rule 6) |
| **A defect report to the founder** | §19's visual, in any shape | **the 8D table**, with the empty disciplines shown empty (§20.5 — every defect report is delivered in this structure) |

**THE WORKED EXAMPLE IS G-49, AND ITS TWO EMPTY DISCIPLINES ARE THE POINT.**
§20.3 — the worked example carries the whole of it, and D3 and D7 both read
`NONE` with a reason: nothing protects the Belt today, and nothing yet stops a
second instance of the class. **Those two lines say more about the product's
state than the four answered disciplines do**, and neither would have appeared
in a report written without the structure.

**WHY A GATE AND NOT A CONVENTION.** The founder's words, recorded because they
are the whole argument: *convention decays; a gate does not.* Rule 6 is
deliberately **not** scoped to `fix(` subjects — this project's real fixes land
as spine commits, and G-49's own fix will land as `commit 6.21`, so a type-only
trigger would have exempted the most important fix commit in the backlog. What
the gate cannot check is written into its own docstring and into §20.4: it
checks that a discipline is ANSWERED, never that the answer is right.

**No rule was renumbered**, so `deprecated_patterns.yaml`'s citations still
resolve (§0.2 — rule numbers are load-bearing). **The guard's rule numbers are
now 1, 2b, 3, 4, 5, 6** — rule 2's number stays retired.

### 0.31 — What Changed in 2.2.37 — a claim about code carries the code

**FOUNDER RULING 2026-09-11.** **Any claim about what the code does carries the
lines it rests on, quoted, with file and line number** — not a description of
them (§20.5.1 — a claim about code carries the code). An absence claim carries
the command and its output, since there are no lines to quote.

| | Before | From 2026-09-11 |
|---|---|---|
| **A code claim in a report** | the claim, with a `file:line` pointer | **the claim, plus the three-to-six lines it rests on, quoted** (§20.5.1 — a claim about code carries the code) |
| **An absence claim** | *"nothing reads this"* | **the search that shows it, with its output** — and absence claims are usually the load-bearing half of a diagnosis (§20.5.1 — a claim about code carries the code) |
| **What a reviewer can do with it** | take it on trust, or open the file by hand | **check it where it is read** (§20.5.2 — why, and what it cost to learn) |

**THE REASON IS A TOOL LIMIT, NOT A PREFERENCE.** Claude Desktop can locate any
source file in this repository and **read none of them** — the file reader
refuses `.py` as `application/octet-stream`. A code claim in a report is
therefore **unverifiable at review** unless the report carries its own evidence,
and "take it on trust" is what actually happens. Quoting four lines costs
nothing.

**IT CAUGHT TWO WRONG CITATIONS IN THE REPORT THAT PROMPTED IT.** Step 6.18's
G-49 report cited `nodes_common.py:1035` for the agent invocation — **it is
1028**, with 1035 being the `recursion_limit` argument four lines below — and
`:995` for the `coaching_plan` read, which is **990**. **The diagnosis was
correct and the pointers were not**, and both pointed at plausible neighbouring
code inside the right function. A line number is the one part of a code claim
that carries no evidence of its own truth; quoting the lines would have failed
at writing time, because the quote and the claim would not have matched.

**No rule was renumbered** (§0.2 — rule numbers are load-bearing), and rule 6
of the commit-msg guard is unchanged: this rule governs reports, which no gate
reads.

---

