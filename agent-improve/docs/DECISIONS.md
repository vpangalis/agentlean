<!--
Document: agent-improve/DECISIONS.md
Version: 1.0 — 2026-08-11
Purpose: Consolidated decision register. Single navigable reference for every
         ratified architectural decision, coaching rule, and deferred/rejected
         item. Synthesized from STATE_DESIGN_RESOLUTION.md (26 findings),
         SKILL_REVIEW_NOTES.md (17 notes), status-79-84-2026-08-10.md, and
         CONTINUITY.md. Replaces the scattered five-file review set as the
         primary cross-session reference.

Source documents (stay in repo, not here):
  agent-improve/reviews/STATE_DESIGN_RESOLUTION.md   — original 26 findings
  agent-improve/reviews/REVIEW_DECISIONS.md           — full EDUCATIONAL.md review log
  agent-improve/SKILL_REVIEW_NOTES.md                 — 17 SKILL.md review notes
  agent-improve/reviews/RESTRUCTURE_PLAN.md           — REFACTORING reorder plan
  agent-improve/reviews/status-79-84-2026-08-10.md   — §79–§84 landing audit

CLAUDE.md version this was written against: v2.2.14
ARCHITECTURE.md version: v2.2.15
-->

# Agent Improve — DECISIONS.md
# Version 1.0 — 2026-08-11

---

## How to read this document

Each decision entry has:
- **Status:** `ADOPTED` | `REJECTED` | `DEFERRED` | `PENDING-AMENDMENT`
- **Landed in:** which governance doc section carries the rule
- **Source:** which review document first captured the finding

Decisions are organized by architectural topic, not chronologically. For the
chronological record, see the source documents listed in the header comment.

---

## Part A — State Design

### A1 — SupervisorState: seven fields, dict-typed gate record

**Status:** ADOPTED — landed in CLAUDE.md §10.1, ARCHITECTURE.md §4.1  
**Source:** STATE_DESIGN_RESOLUTION.md Findings 1–3, 7

The canonical `SupervisorState` has exactly seven fields:

```python
class SupervisorState(TypedDict):
    messages:       Annotated[list[BaseMessage], operator.add]
    history:        Annotated[list[str], operator.add]
    case_id:        str
    phase_index:    int
    current_phase:  str
    gate_passed:    dict[str, bool]       # {"define": True, "measure": False, …}
    final_output:   Optional[dict]        # set at Control gate only
```

`gate_passed` is `dict[str, bool]`, not `list[str]`. Direct lookup
(`gate_passed["measure"]`) and the re-approval cascade (`False` instead
of list remove) both require the dict form.

`final_output` is `Optional[dict]`, never `str`.

An eighth field requires an ARCHITECTURE.md amendment.

**Removed as redundant:** `dmaic_plan`, `key_decisions`, `open_items`,
`project_context` — all four duplicated mechanisms that already exist
(static phase order, `CoachingResponse.fields_captured`, `check_gate_status()`,
input mappers). `project_context` had no writer at all.

`current_phase` and `phase_index` are derived from `gate_passed` and kept
for readability — written in exactly one place (the output mapper at gate
approval). Nothing else may write them.

---

### A2 — PhaseState: fifteen content fields

**Status:** ADOPTED — landed in CLAUDE.md §10.1  
**Source:** STATE_DESIGN_RESOLUTION.md Findings 4–6, 8–12

```python
class PhaseState(TypedDict):
    # conversation plumbing (3)
    messages:           Annotated[list[BaseMessage], operator.add]
    history:            Annotated[list[str], operator.add]
    phase_context:      str

    # content fields (15)
    coaching_plan:      dict[str, Any]     # single dict, overwritten each planner turn
    field_index:        int
    draft:              dict[str, Any]     # this turn's extraction
    artifacts:          dict[str, Any]     # accumulated captured fields for the phase
    step_log:           Annotated[list[dict[str, Any]], operator.add]
    belt_edits:         dict[str, Any]     # Belt corrections at gate review
    turn_count:         int
    final:              dict[str, Any]     # approved gate document (dict, not str)
    gate_attempts:      int                # shared cap counter for 4-layer stack
    validator_feedback: list[dict]         # accumulated per-attempt feedback
    citations:          list[dict]
    uploads:            list[dict]
```

Key naming decisions:
- `feedback` → split into `validator_feedback` (system) and `belt_edits` (Belt). Conflating them would have the coach reading Belt corrections as validation failures.
- `final: str` → `final: dict`. String forces downstream parsing.
- `coaching_plan: list[dict]` → `coaching_plan: dict`. One plan per planner turn; no upfront queue.
- `gate_attempts` MUST be on `PhaseState` in the checkpoint, not in route scope — the v1 "attempts always reset to 0" bug came from route scope.
- `validator_feedback` makes the shared cap of 3 defensible: each entry records attempt, layer, criteria, and feedback; the coach reads the full list on retry.

---

### A3 — Canonical identifier: `case_id` everywhere

**Status:** ADOPTED — landed in CLAUDE.md §10.5  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 13

`project_id` is retired. The identifier is `case_id` everywhere: state
field, store namespace, `thread_id`, blob path, log field, index field,
prose. Both indexes (`improve_evidence_index`, `improve_case_index`) and
the blob path (`cases/case_{id}.json`) always said `case_id` — the rename
resolves the doc/code split.

---

### A4 — Canonical name for captured fields: `artifacts`

**Status:** ADOPTED — landed in CLAUDE.md §10.5  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 14

Three names existed for one concept: `artifacts` (code), `captured_fields`
(prose), `phase_inputs` (v1 field). `artifacts` wins everywhere.

`captured_fields` must not appear in prose. `phase_inputs` must not be
added to v2 code.

---

### A5 — All captured fields are `str`; computation results in `artifacts["computation_results"]`

**Status:** ADOPTED — landed in CLAUDE.md §10.6  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 15

Every captured field is typed `str`. No phase schema declares a typed
numeric. Computation tools parse at the point of use and return a clear
reformatting request to the Belt when they cannot.

```python
baseline_mean = "12.3% invoice error rate, measured over Q2 2026"
```

Computation tool output goes in `artifacts["computation_results"]` as a
list of typed dicts, all values strings:

```python
artifacts["computation_results"] = [
    {"tool": "t_test",
     "inputs": {"sample1": "new_staff_errors", "sample2": "experienced_staff_errors"},
     "result": {"t_statistic": "4.23", "p_value": "0.001", "significant": "yes"},
     "turn": 7, "phase": "analyse"}
]
```

The grader scans this list to answer "was a hypothesis test run?" — no
per-phase typed destinations, no new `PhaseState` fields.

Exception: three cross-phase reference dicts are `dict` (see A6).

---

### A6 — Three cross-phase reference dicts

**Status:** ADOPTED — landed in CLAUDE.md §10.6, ARCHITECTURE.md §4.7  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 15

Three fields carry typed dicts (not strings) to enable deterministic grader
linkage checks:

| Field | Phase | Purpose |
|---|---|---|
| `causal_hypothesis` | Analyse | Links root cause to Measure baseline |
| `solution_linked_to_root_cause` | Improve | Links solution to Analyse root cause |
| `post_improvement_metric` | Control | Links result to Measure baseline |

Each carries `references_phase`, `references_field`, `references_value`.
The grader reads the referenced phase's gate document from the store and
checks the named field carries the named value — deterministic, no LLM
judgment in the linkage check.

```python
causal_hypothesis = {
    "hypothesis": "Inadequate onboarding causes error spike in first 60 days",
    "references_phase": "measure",
    "references_field": "baseline_mean",
    "references_value": "12.3%"
}
```

Values inside the dict are still strings.

---

### A7 — Store namespace convention; `gate_documents` namespace retired

**Status:** ADOPTED — landed in CLAUDE.md §10.2  
**Source:** STATE_DESIGN_RESOLUTION.md Findings 5, 9

```
("projects", case_id, "case")      → "record"    (case framing, written once)
("projects", case_id, "artifacts") → "define", "measure", …  (gate documents)
("projects", case_id, "step_log")  → timestamped  (append-only audit trail)
```

Blob prefix: `store/projects/{case_id}/{kind}/{key}.json`

The `gate_documents` namespace is retired — it was a duplicate of
`artifacts` with no way to resolve which was authoritative.

---

### A8 — `gate_apply_node` writes BOTH store and `PhaseState.final`

**Status:** ADOPTED — landed in CLAUDE.md §9.6  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 11

After Belt approval, `gate_apply_node` writes to both:

```python
# 1. Store — what the next phase's input mapper reads
store.put(("projects", case_id, "artifacts"), phase_name, gate_document)

# 2. PhaseState — so the checkpoint is self-sufficient for crash recovery
return {"final": gate_document, "gate_attempts": 0, "validator_feedback": []}
```

Both writes are required. A crash between them would leave state saying the
gate was not applied while the store says it was. `final` holding the same
dict means resumed graphs see what was approved without re-reading the store.

`gate_attempts` and `validator_feedback` reset here and ONLY here.

---

## Part B — Executor Contract & Middleware

### B1 — Five subgraph nodes; `policy_advisory` and `revise` are banned

**Status:** ADOPTED — landed in CLAUDE.md §3.3, ARCHITECTURE.md §3.2  
**Source:** STATE_DESIGN_RESOLUTION.md Findings 16–17

Each phase subgraph contains exactly five nodes:

| Node | Role |
|---|---|
| `planner` | Structured plan: focus_field, next_action, retrieval_strategy, tools_needed |
| `executor` | `create_agent` with the phase's tool subset |
| `validation_stack` | Four layers (§9.2), shared cap of 3 |
| `gate_review` | `interrupt()` — presents validated fields, stops |
| `gate_apply` | Policy advisory, applies corrections, assembles gate doc, routes on |

`policy_advisory` is BANNED as a node name — it is logic inside `gate_apply`.  
`revise` is BANNED as a node name — revision is an **edge** (validation stack routes back to planner with `validator_feedback`).

The validation stack and policy advisory are NOT tools. Adding either to a tool list is a violation.

---

### B2 — Two graders; confusing them is a violation

**Status:** ADOPTED — landed in CLAUDE.md §8.2  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 18

| | `DMAICGraderMiddleware` | Validation stack Layer 2d |
|---|---|---|
| Where | Middleware, inside executor | `validation_stack` node |
| When | **Every coaching turn** (`after_agent`) | **Once**, at gate boundary |
| Rubric | **`COACHING_QUALITY_RUBRIC`** (one, shared) | **`PHASE_RUBRIC`** (five, one per phase) |
| Grades | Coach's **process** | **Gate document** |

Never point `DMAICGraderMiddleware` at a phase rubric.  
Never point Layer 2d at `COACHING_QUALITY_RUBRIC`.

---

### B3 — Five middlewares; declaration order is execution order

**Status:** ADOPTED — landed in CLAUDE.md §8.1  
**Source:** STATE_DESIGN_RESOLUTION.md Findings 19–20

```python
middleware=[
    BeforeModelStateInjection(...),    # before_model — MUST be first
    DMAICSkillsMiddleware(...),        # before_agent
    SummarizationMiddleware(...),      # before_model
    ModelRetryMiddleware(retries=2),   # wrap_model_call — ADOPTED in v2.2.10
    DMAICGraderMiddleware(...),        # after_agent
]
```

`BeforeModelStateInjection` MUST be first — project facts must reach the
top of the prompt before skills loading and summarisation shape it. An
earlier revision listed it last, which defeats the priority ordering.

`ModelRetryMiddleware` is the invisible-retry tier: retries the same call
on transient failure, never swaps the model. The fallback chain (§4.8) is
distinct — it swaps the model on service-level failure.

---

### B4 — `CoachingResponse` schema; `response_format=CoachingResponse` on the executor

**Status:** ADOPTED — landed in CLAUDE.md §4.6, §10.7  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 21

```python
class CoachingResponse(BaseModel):
    message: str
    fields_captured: list[dict] = []    # [{field_name: str, value: Any, source: str}]
    citations: list[dict] = []
```

`value` is `Any` (not `str`) — must carry both plain strings and the three
cross-phase reference dicts (see A6). The `Any` is correct here and only here.

The executor node writes the response into state:

```python
result = await executor.ainvoke(state)
resp = result["structured_response"]
for f in resp.fields_captured:
    artifacts[f["field_name"]] = f["value"]
citations.extend(resp.citations)
```

The executor's `response_format` is `CoachingResponse`, never a phase
`{Phase}Output` schema. The gate document is assembled once per phase via
Pydantic construction at `gate_apply` — no LLM call.

---

### B5 — `record_field` tool retired; field capture via structured output

**Status:** ADOPTED — landed in CLAUDE.md §5.1  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 22

`record_field` is retired and may not be reintroduced. Field capture
happens through `CoachingResponse.fields_captured` on the executor — the
coach emits `fields_captured` as structured output on every turn, making
capture part of every response by construction rather than an optional tool
call.

---

### B6 — Universal tool count: seven (not eight)

**Status:** ADOPTED — landed in CLAUDE.md §5.1  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 23

After `record_field` was retired, the universal tool count dropped from 8
to 7. The seven:

```
rag_lookup_methodology(query, phase, top_k=10)
rag_lookup_evidence(query, case_id, top_k=10)
rag_lookup_case_history(query, top_k=10, exclude_current_case=True)
propose_template(template_type, fill_data)
propose_diagram(diagram_type, data)
check_gate_status()
request_human_approval(reason)
```

`search_methodology` and `search_evidence` are superseded — no code may
reference the old names.

---

### B7 — Per-phase tool totals after `record_field` retirement

**Status:** ADOPTED — landed in CLAUDE.md §5.2  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 23

| Phase | Universal | Computation | Total |
|---|---|---|---|
| Define | 7 | 1 (`calculate_expected_savings`) | **8** |
| Measure | 7 | 8 (`sigma_level`, `cpk`, `dpmo`, `yield_rty`, `ftq`, `grr`, `sample_size_proportion`, `sample_size_mean`) | **15** |
| Analyse | 7 | 5 (`t_test`, `chi_square_test`, `anova`, `pearson_correlation`, `linear_regression`) | **12** |
| Improve | 7 | 1 (`calculate_doe_main_effects`) | **8** |
| Control | 7 | 5 (`xbar_r_chart_limits`, `imr_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk`) | **12** |

No phase exceeds 16 tools. Previous totals were 9/16/13/9/12; these are
8/15/12/8/12 reflecting `record_field` removal.

---

## Part C — Gate Fields & Rubric Tiers

### C1 — Two-tier field system; grader gains `warning` verdict

**Status:** ADOPTED — landed in CLAUDE.md §9.7  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 24 (eBook extraction, v2.2.11)

Every rubric criterion is Tier 1 (gate-required, blocks gate, can `fail`)
or Tier 2 (rubric-recommended, at most `warning`, Belt may proceed with
acknowledged gap).

```python
class CriterionVerdict(BaseModel):
    criterion: str
    tier:      int                           # 1 or 2
    status:    Literal["pass", "warning", "fail"]
    feedback:  str
```

A gate MAY pass with warnings. A gate may NEVER pass with failures.

**Tier 1 fields by phase:**

| Phase | Tier 1 Fields | Count |
|---|---|---|
| Define | `problem_statement`, `voc_summary`, `project_scope`, `goal_statement`, `process_map_sipoc` (dict), `issues_and_barriers` | 6 |
| Measure | `baseline_mean`, `data_collection_plan`, `xy_matrix_summary`, `vital_few_xs`, `detailed_process_map` (dict), `stability_assessment`, `issues_and_barriers` | 7 |
| Analyse | `root_cause_statement`, `root_cause_validation`, `practical_significance`, `issues_and_barriers` | 4 |
| Improve | `selected_solution`, `pilot_result`, `experiment_justification`, `issues_and_barriers` | 4 |
| Control | `control_plan` (dict, 5 sub-plans), `post_improvement_metric`, `issues_and_barriers` | 3 |

`issues_and_barriers` is Tier 1 in every phase. A Belt reporting none has
not looked — "none identified at this stage" is valid; silent skip is not.

**Field counts per phase (total/Tier 1/Tier 2/gate metadata):**

| Phase | Total | Tier 1 | Tier 2 | Gate metadata |
|---|---|---|---|---|
| Define | 15 | 6 | 5 | 4 |
| Measure | 14 | 7 | 3 | 4 |
| Analyse | 13 | 4 | 5 | 4 |
| Improve | 13 | 4 | 5 | 4 |
| Control | 15 | 3 | 8 | 4 |

Gate metadata (all five): `computation_results`, `acknowledged_gaps`,
`citations`, `uploads`.

---

### C2 — `issues_and_barriers` is NOT `acknowledged_gaps`

**Status:** ADOPTED — landed in CLAUDE.md §9.7  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 24

`issues_and_barriers` = Belt-stated real-world project blockers (Tier 1).  
`acknowledged_gaps` = system-generated record of skipped Tier 2 fields.

Merging them is a violation.

---

### C3 — eBook additions to schema fields (v2.2.11)

**Status:** ADOPTED — landed in CLAUDE.md §0.6  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 24

Fields added to resolve BB eBook extraction gaps 24–25:

- `issues_and_barriers` — Tier 1, all five phases
- `secondary_metrics` — Tier 2, all five phases
- `xy_matrix_summary` — Tier 1, Measure (produces `vital_few_xs`)
- `vital_few_xs` — Tier 1, Measure
- `practical_significance` — Tier 1, Analyse
- `statistical_problem_statement` — Tier 2, Analyse (all Belts, not Define)
- `process_owner_buyin` — Tier 2, Analyse and Improve (not Control only)
- `explanatory_power` — Tier 2, Improve
- `project_signoff` — Tier 2, Control
- `control_plan` type changed from `str` → `dict` of five sub-plans

---

### C4 — X-Y matrix and statistical problem statement no longer belt-gated

**Status:** ADOPTED — landed in CLAUDE.md §9.7  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 24

| Item | Before | Now |
|---|---|---|
| X-Y matrix | BB-only | `xy_matrix_summary`, Tier 1, all Belts — produces `vital_few_xs` Analyse cannot start without |
| Statistical problem statement | BB-only | Tier 2, all Belts, in Analyse — not Define |
| DOE | BB-only | Still BB-only — the one remaining belt-gated item |
| Stability | Advisory | `stability_assessment`, Tier 1, all Belts — unstable process makes Cpk meaningless |

---

### C5 — Process map fields promoted to Tier 1 schema (v2.2.12)

**Status:** ADOPTED — landed in CLAUDE.md §0.7, §10.8  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 26

Three fields promoted from coaching content to Tier 1 schema fields — a
coaching prompt produces conversation, which cannot be read by the next
phase's planner or checked by the grader:

| Field | Phase | Type | Sub-fields |
|---|---|---|---|
| `process_map_sipoc` | Define | dict | `suppliers`, `inputs`, `process_steps`, `outputs`, `customers`, `process_kpis` |
| `detailed_process_map` | Measure | dict | `steps`, `cycle_times`, `resources`, `value_vs_waste`, `measurement_points`, `baseline_kpis` |
| `stability_assessment` | Measure | str (Tier 1) | — |
| `experiment_justification` | Improve | str (Tier 1) | — |

`experiment_justification` requires a decision (DOE / simplified experiment /
no experiment needed), not necessarily an experiment. All three options are
valid; the failure it catches is drifting past the question.

**Three-phase measurement thread** across the three process map fields:
```
Define   process_map_sipoc["process_kpis"]       — WHAT is measured
Measure  detailed_process_map["baseline_kpis"]   — the BEFORE values
Control  post_improvement_metric                 — the AFTER values
```

The grader verifies the same measurement points carry different values.

---

### C6 — FMEA: deliberately not tracked in any schema

**Status:** ADOPTED — landed in CLAUDE.md §10.8  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 26

FMEA has no field in any schema. It is heavy manufacturing methodology not
appropriate as a universal gate requirement in service/transactional DMAIC.
If a Black Belt performs one, it lives in `uploads`. The schema does not
track it, the grader does not ask for it, and no gate blocks on it.

`fmea_summary`, `updated_fmea`, FMEA sub-keys — all banned.

---

## Part D — Coaching & Skills

### D1 — Seven-step computation tool coaching pattern

**Status:** ADOPTED — landed in CLAUDE.md §8.2 (`COACHING_QUALITY_RUBRIC`)  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 25; SKILL_REVIEW_NOTES.md Notes 1–14

The coach follows a **seven-step** pattern, every computation tool, every
time. Step 1 (educate on the concept) was not in the previous six-step
version:

| # | Step |
|---|---|
| 1 | **Educate on the concept** — what this IS, plain language, real-world analogy, and what the output numbers will mean |
| 2 | **Explain why now** — why the Belt needs it at this point in their project |
| 3 | **Guide data preparation** — what format is needed; check uploads via `rag_lookup_evidence` |
| 4 | **Run the computation** — call the tool |
| 5 | **Interpret their result** — plain language, no jargon |
| 6 | **Visualise** — `propose_diagram` where applicable |
| 7 | **Coach the next move** — what it means for the project |

Step 1 is mandatory and is the one most often skipped. Never assume the
Belt knows what a Cpk, p-value, or control limit is. Returning raw
computation output without concept + interpretation is a rubric failure,
checked on every coaching turn.

---

### D2 — Show-first coaching principle (Note 15)

**Status:** ADOPTED — landed in CLAUDE.md §8.2 (`COACHING_QUALITY_RUBRIC`)  
**Source:** SKILL_REVIEW_NOTES.md Note 15 (CRITICAL)

For every field, the coach:
1. Shows a **concrete example of a completed answer**
2. Explains **why it works** (what makes it good)
3. Invites the Belt to build theirs **in the same shape**

Never ask "what is your baseline metric?" before showing what a good
baseline metric looks like. Each SKILL.md must carry a worked example per
field.

**SIPOC worked example (Define):**

```
Let me show you a completed SIPOC before you build yours:

Suppliers → Inputs → Process Steps → Outputs → Customers
HR system, Managers → Employee records, Role requirements → 
  1. Receive request, 2. Screen candidates, 3. Interview, 
  4. Select, 5. Contract, 6. Start date set → 
Hired employee, Onboarding pack → Hiring manager, New employee

Key KPIs: Time-to-hire (days), offer acceptance rate (%)

Notice the KPIs are in the SIPOC itself — that's what makes it 
DMAIC-useful rather than just a process map.

Now build yours for [project name].
```

---

### D3 — A→F session flow with visible progress (Note 16)

**Status:** ADOPTED — to be implemented in all five SKILL.md files  
**Source:** SKILL_REVIEW_NOTES.md Note 16 (CRITICAL)

Each SKILL.md must structure coaching as an A→F session flow with a
visible progress count that the Belt can see at any time.

Template: `"We're working through the [Phase] phase — Step 3 of 6."`

The six steps vary per phase but follow the pattern:
- A: Orientation (context setting, phase purpose)
- B: Mandatory Tier 1 fields (one by one, show-first)
- C: Computation tools (seven-step pattern)
- D: Cross-phase references where applicable
- E: Tier 2 fields (advisory, Belt decides)
- F: Gate readiness check (`check_gate_status()`) and submission

Each SKILL.md must include a **Document Layout section** showing the Belt
what the live gate document will look like at the end of the phase, so
they know what they are building toward.

---

### D4 — Live gate document preview (Note 17)

**Status:** ADOPTED — to be implemented in all five SKILL.md files  
**Source:** SKILL_REVIEW_NOTES.md Note 17 (CRITICAL)

The coach must show the Belt a preview of the gate document as it fills in,
using `check_gate_status()` output. The Belt sees what is captured, what is
missing, and what the final document will look like.

Mockup from Note 17 (Define phase):

```
📋 Your Define Gate Document (4 of 6 required fields complete)

✅ Problem Statement: "Invoice error rate at 12.3% causes..."
✅ VOC Summary: "Customer complaints focus on..."
⬜ Project Scope: [not yet captured]
✅ Goal Statement: "Reduce invoice error rate from 12.3% to <3%..."
✅ Process Map (SIPOC): [complete — 6/6 sub-fields]
⬜ Issues & Barriers: [not yet captured]

Tier 2 fields: Business Case ✅  Team ✅  Charter ⬜ (optional)

We're on Step 5 of 6. Let's capture Project Scope next.
```

---

### D5 — No external URLs in coaching; retrieve via `rag_lookup_methodology`

**Status:** ADOPTED — landed in CLAUDE.md §8.2 (`COACHING_QUALITY_RUBRIC`), §0.8  
**Source:** SKILL_REVIEW_NOTES.md (general note across all 17); CLAUDE.md v2.2.14

The coach must not provide external URLs from training data. When
referencing methodology, retrieve via `rag_lookup_methodology` and weave
the content into natural coaching voice.

---

### D6 — SKILL.md allowed-tools must match §5.2 tool subsets

**Status:** ADOPTED — landed in CLAUDE.md §8.3  
**Source:** SKILL_REVIEW_NOTES.md (verified across Notes 1–14)

Each SKILL.md's `allowed-tools` must match exactly the computation tool
subset defined for that phase in CLAUDE.md §5.2. If they drift, the skill
will describe tools the executor does not have access to.

---

## Part E — Retrieval Architecture

### E1 — Multi-query + RRF (Option A: per-tool SearchClient instances)

**Status:** ADOPTED (ratified) — **PENDING DOC AMENDMENT** in ARCHITECTURE.md §7.4  
**Source:** CONTINUITY.md §2 item 7; pre-session decision

Option A: each of the three `rag_lookup_*` tools holds its own
`SearchClient` instance, scoped to its index. No shared retriever.

RRF implementation: 3–5 query variants per tool call, fused with
Reciprocal Rank Fusion k=60. Fifteen lines of code, no LangChain class.

`MultiQueryRetriever` — not used; belongs to the retriever abstraction layer
we are deliberately bypassing with per-call `AzureAISearchRetriever` (see §E4).

`EnsembleRetriever` — not deprecated (active in `langchain.retrievers.ensemble`,
confirmed v0.3), but solves the wrong problem. It combines results from
**different retriever sources** (e.g., BM25 + vector). Our pattern is
**same-index multi-query RRF** — N phrasings against one index. No standard
LangChain 1.x class exists for this pattern. The LangChain rag-fusion template
(v0.2) also used a custom implementation for the same reason. Custom 15-line
`reciprocal_rank_fusion()` is correct, stable, and dependency-free.

Anthropic "Writing Tools for Agents" (Sep 2025, Tier 1) confirms the
encapsulation principle: complexity belongs inside the tool, not exposed to
the agent. The custom RRF matches this — clean tool interface, fusion hidden.

`rag_lookup_evidence` takes no `order_by` argument — `improve_evidence_index`
has no `uploaded_at` field (upload timestamp buried in non-sortable
`metadata` JSON blob). This is a schema change (ARCHITECTURE.md §7.7), not
a tool change.

---

### E2 — `improve_case_index` vector field: `embedding` → `content_vector`

**Status:** ADOPTED (ratified) — **PENDING RE-INDEX + DOC AMENDMENT** in ARCHITECTURE.md §7.3  
**Source:** CONTINUITY.md §2 item 8

The vector field on `improve_case_index` is standardised to `content_vector`
to match the other two indexes. The old name `embedding` is retired.

Implementation: delete + recreate the index (it held 0 documents as of the
decision), re-ingest, update ARCHITECTURE.md §7.3 and `rag_lookup_case_history`
in `knowledge/tools.py`.

---

### E3 — `phase_relevance` filter field; cross-phase value is `general` not `all`

**Status:** ADOPTED — landed in CLAUDE.md §7.2  
**Source:** ARCHITECTURE.md §7.1.2 (live finding)

Filter `improve_knowledge_index` on `phase_relevance`. Cross-phase value is
`'general'` — not `'phase'` (doesn't exist on the index, Azure rejects the
whole query) and not `'all'` (no document carries it, silently narrows corpus).

218 documents carry `phase_relevance = 'general'`.

---

### E4 — `AzureAISearchRetriever` filter must be set at construction time, not invoke time

**Status:** ADOPTED — 2026-08-11 (§33 compliance audit)  
**Source:** REVIEW_DECISIONS.md §33-B finding; GitHub #29756, #21492, #14227, #30482

`AzureAISearchRetriever.invoke(q, search_kwargs={"filters": ...})` does not work —
`search_kwargs=` at invoke time is the `AzureSearchVectorStoreRetriever` interface,
not `AzureAISearchRetriever`. The filter must be passed as `filters=` in the constructor.

Since the `phase` parameter is dynamic (varies per tool call), the retriever for
`rag_lookup_methodology` **cannot be module-level**. It is created per call:

```python
retriever = AzureAISearchRetriever(
    service_name=..., index_name="improve_knowledge_index",
    content_key="content", top_k=top_k * 3,
    filters=f"phase_relevance eq '{phase}' or phase_relevance eq 'general'",
)
ranked_lists = [retriever.invoke(q) for q in variants.queries]
```

Same pattern applies to `rag_lookup_evidence` (filter: `case_id eq '...'`) and
`rag_lookup_case_history` (filter: `status eq 'completed'`).

Closes §32 open question: "Confirm `azure_search_retriever` module-level exposure
or adjust reference implementation." Answer: adjust — per-call constructor.

---

### E5 — Retrieval failure must raise, not return `[]`

**Status:** ADOPTED — landed in CLAUDE.md §7.2  
**Source:** ARCHITECTURE.md §7.1.1

`KnowledgeSearchError` must be raised on failure. `[]` means "search ran,
matched nothing." Wrapping a retrieval call in bare `except Exception: return []`
hides broken indexes as silent empty corpus — this is how the `phase` filter
bug was hidden in production.

Rules:
- `RETRIEVAL_EXCEPTIONS` spans Azure AI Search and Azure OpenAI embedding (both inside the same `try`)
- A 4xx is `permanent` / `do_not_retry` — malformed query, retrying fails identically
- Materialise results inside the `try` — `SearchClient.search()` is lazy and the HTTP call fires on iteration

---

## Part F — LangChain/LangGraph Patterns: Adopted

### F1 — §79: LangGraph 1.2 native reliability primitives

**Status:** LANDED — CLAUDE.md §3.6, ARCHITECTURE.md §9.2  
**Source:** status-79-84-2026-08-10.md; REFACTORING §79

`TimeoutPolicy(run_timeout=45)` required on every phase executor node.
`error_handler=` required on every node with external writes.
`RunControl.request_drain()` for graceful shutdown.

Custom Saga orchestrators and hand-written compensating-action frameworks
are BANNED.

---

### F2 — §80: AgentMiddleware six hooks foundation

**Status:** LANDED — CLAUDE.md §8.1–§8.7, ARCHITECTURE.md §3.4  
**Source:** status-79-84-2026-08-10.md; REFACTORING §80

The five-middleware stack is built on the six `AgentMiddleware` hooks:
`before_agent`, `after_agent`, `before_model`, `after_model`,
`wrap_model_call`, `wrap_tool_call`. "Prefer built-in middleware wherever
it exists."

---

### F3 — §81: `content_blocks`, not string parsing

**Status:** LANDED — CLAUDE.md §4.5  
**Source:** status-79-84-2026-08-10.md; REFACTORING §81

Read `response.content_blocks`. String-indexing or substring-parsing the
raw content field is a violation.

**Live code gap:** `upload/agent.py:107` still parses `response.content`
directly (§4.5 violation). No §15 step covers it. Code drift, not a
constitution gap. Tracked in CONTINUITY.md §4.

---

### F4 — §82: `ProviderStrategy` / `response_format=` scoped by call type

**Status:** LANDED — CLAUDE.md §4.3, §4.6  
**Source:** status-79-84-2026-08-10.md; REFACTORING §82

The contradiction in v2.1 (§4.3 mandated `with_structured_output`
everywhere while the hook cited a §4.6 that didn't exist) is resolved.
Now: `response_format=` for agents built with `create_agent`;
`with_structured_output` for plain model calls inside tools/middleware/validators.
See CLAUDE.md §4.6 for the full mapping.

---

### F5 — §83: SKILL.md spec

**Status:** LANDED — ARCHITECTURE.md §8.4, CLAUDE.md §8.3  
**Source:** status-79-84-2026-08-10.md; REFACTORING §83

Five SKILL.md files under `agent-improve/skills/`, following the
agentskills.io standard. On disk as `skills/dmaic-{phase}-phase/SKILL.md`.
Filename restored in commit `fe21816`.

---

## Part G — Rejected / Deferred Items

### G1 — DeltaChannel: DEFERRED

**Status:** DEFERRED to §87 item 12  
**Source:** status-79-84-2026-08-10.md; REFACTORING §79

`DeltaChannel` is not adopted — beta API. Deferred until sessions exceed
~200 turns. Not a violation of §79; the decision to not adopt a beta API
is the §79-compliant choice.

---

### G2 — deepagents: REJECTED (pre-1.0)

**Status:** REJECTED while pre-1.0 — landed in CLAUDE.md §4.4, §8.6  
**Source:** status-79-84-2026-08-10.md; REFACTORING §84

`create_deep_agent`, `RubricMiddleware`, `SkillsMiddleware` from deepagents
are BANNED while the package remains pre-1.0. Our equivalents:
`DMAICGraderMiddleware` (custom, replaces `RubricMiddleware`),
`DMAICSkillsMiddleware` (custom, replaces `SkillsMiddleware`).

Revisit at deepagents 1.0. If migrating: migrate all three custom
middlewares together or not at all.

---

### G3 — `HumanInTheLoopMiddleware`: REJECTED (two confirmed bugs)

**Status:** REJECTED — landed in CLAUDE.md §8.6  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 16; REFACTORING §53

Two confirmed bugs in our exact use case:
1. Edited tool-call args can be silently re-overwritten by the agent re-attempting the original call
2. Edit/reject are broken in subgraph contexts — only approve is reliable

Both would silently discard a Belt's correction. Use graph-level
`interrupt()` + `Command(resume=...)` instead.

---

### G4 — `LLMToolSelectorMiddleware`: REJECTED

**Status:** REJECTED — landed in CLAUDE.md §8.6  
**Source:** STATE_DESIGN_RESOLUTION.md

Per-phase binding (§5.2) keeps every coach at 8–15 tools. Adding a
selector LLM spends a model call solving a problem already solved
structurally.

---

### G5 — `create_react_agent` / `langgraph.prebuilt`: BANNED

**Status:** REJECTED — landed in CLAUDE.md §4.4  
**Source:** STATE_DESIGN_RESOLUTION.md

`create_react_agent` is superseded by `create_agent` from
`langchain.agents`. Nothing may import it, nothing may import from
`langgraph.prebuilt`.

---

### G6 — Parameterised computation tool groups: BANNED

**Status:** REJECTED — landed in CLAUDE.md §5.2  
**Source:** CLAUDE.md §5.2

One `calculate_sample_size(type, ...)` with a mode argument instead of two
named tools is banned — it moves selection burden into argument space, and
models handle distinct named tools more reliably than mode arguments.

---

### G7 — Tolerance threshold on mid-phase conflict detection: BANNED

**Status:** REJECTED — landed in CLAUDE.md §9.4  
**Source:** CLAUDE.md §9.4

"The delta was small enough" is not acceptable. Every change to a
gate-approved value triggers a mini-gate. No threshold, and none may be
added.

---

### G8 — MCP: ARCHITECTURALLY EXCLUDED

**Status:** REJECTED (permanent exclusion, not deferral) — landed in CLAUDE.md §1.9  
**Source:** REFACTORING §63; CLAUDE.md §1.9

Agent Improve, Agent Resolve, and Agent Flow will never use MCP. The
`improve_evidence_index` is the only channel through which external
real-world data enters AgentLean. No promotion trigger exists.

---

### G9 — `InMemorySaver`: BANNED at all stages

**Status:** REJECTED — landed in CLAUDE.md §1.7  
**Source:** CLAUDE.md §1.7

Not used at any stage, including development. `AzureBlobCheckpointSaver`
during the refactor; `PostgresSaver` pre-production.

---

### G10 — `ConversationBufferMemory` and related legacy classes: BANNED

**Status:** REJECTED — landed in CLAUDE.md §8.4  
**Source:** CLAUDE.md §8.4

`ConversationBufferMemory`, `ConversationBufferWindowMemory`,
`ConversationSummaryMemory`, `ConversationEntityMemory`,
`VectorStoreRetrieverMemory`, `ConversationChain` — all scheduled for
removal in LangChain 2.0. Replacement: checkpointer + store +
`SummarizationMiddleware`.

---

### G11 — REFACTORING_AGENT_IMPROVE.md restructuring: PENDING (separate task)

**Status:** PENDING — plan in `reviews/RESTRUCTURE_PLAN.md`  
**Source:** reviews/RESTRUCTURE_PLAN.md

Reorder REFACTORING_AGENT_IMPROVE.md from chronological to logical
reference structure (11 Parts + Appendix). Rules: no content changes,
only reorder; §N numbers stay the same; rebuild navigation index; verify
`wc -l` within ±5 lines of original.

This is a standalone Claude Code task — not part of the current code
migration steps.

**Known stale content in REFACTORING_AGENT_IMPROVE.md §10:** still shows
`completeness_score: float` which is wrong per the ratified all-`str`
field rule (A5 above). Must be corrected during or after restructuring.

---

## Part H — Pending Doc Amendments

### H1 — ARCHITECTURE.md §7.4: multi-query Option A description

**Status:** PENDING  
**Content:** Update to describe Option A (per-tool `SearchClient` instances),
remove the "asymmetry" language that implied `improve_case_index` used a
different retriever mechanism, and confirm RRF implementation detail.

---

### H2 — ARCHITECTURE.md §7.3: `improve_case_index` vector field rename

**Status:** PENDING  
**Content:** Update `embedding` → `content_vector` in the index schema.
Requires re-index (delete + recreate, 0 documents, no data loss). Also
update `rag_lookup_case_history` in `knowledge/tools.py` to reference the
new field name.

---

## Part I — Code Migration Status

### I1 — Current HEAD and step sequence

As of 2026-08-11: HEAD `8dfe1a8`

| Step | Description | Status |
|---|---|---|
| 2.1 | Checkpointer wired into graph.compile() | ✔ committed |
| 2.2 | SupervisorState / PhaseState split (schema only) | ✔ committed |
| 2.5 | AzureBlobStore, boundary mappers, `gate_apply_node` dual write | **NEXT** |
| 3.0 | Toolset reconciliation (canonical 7+20, `tool_args.py`) | unblocked by §79–§84 audit |
| 3.1 | `tool_args.py` Pydantic schemas | **BLOCKED** — canonical toolset must be confirmed in code before args schemas can be written (Delta 1c/1d, D3.5) |

---

### I2 — Live code gaps (not constitution gaps)

| Gap | File | Rule | Priority |
|---|---|---|---|
| `response.content` string-indexed | `upload/agent.py:107` | §4.5 (D3.4) | No §15 step covering it — code drift, add to step 3.x planning |
| `core/llm.py` class violation | `core/llm.py` | §2 (classes only in designated files) | Track in §4 stale zones |

---

### I3 — §79–§84 items: all confirmed LANDED

**Audit date:** 2026-08-10  
**Governance docs audited:** CLAUDE.md v2.2.14, ARCHITECTURE.md v2.2.15,
`.claude/config/deprecated_patterns.yaml`

| Item | Status | Landed in |
|---|---|---|
| §79 LangGraph 1.2 reliability primitives | LANDED | CLAUDE.md §3.6 · ARCHITECTURE.md §9.2 |
| §80 AgentMiddleware six hooks | LANDED | CLAUDE.md §8.1–§8.7 · ARCHITECTURE.md §3.4 |
| §81 `content_blocks` | LANDED | CLAUDE.md §4.5 |
| §82 `ProviderStrategy` / `response_format=` | LANDED | CLAUDE.md §4.3 + §4.6 |
| §83 SKILL.md spec | LANDED | ARCHITECTURE.md §8.4 · CLAUDE.md §8.3 |
| §84 SkillsMiddleware | LANDED | ARCHITECTURE.md §3.3, §3.4 |

Two deliberate divergences: DeltaChannel deferred (G1); deepagents banned
(G2). Both are §79/§84-compliant choices, not gaps.

Anchor note: July 2026 audit expected the middleware stack at §3.2. The
v2.2 rewrite moved it — §3.2 is the subgraph, §3.3 the executor, §3.4
middleware. Any cross-reference to "§3.2 middleware stack" is stale.

Step 3.0 is NOT blocked by §79–§84. Step 3.1 remains blocked by the
toolset gap (I1 above).

---

## Part J — Amendment Log

| Amendment | Changed | Governance doc | Version |
|---|---|---|---|
| Seven-step computation pattern (was six) | §8.2 `COACHING_QUALITY_RUBRIC` | CLAUDE.md | v2.2.14 |
| Show-first coaching principle | §8.2 `COACHING_QUALITY_RUBRIC` | CLAUDE.md | v2.2.14 |
| No external URLs rule | §8.2 `COACHING_QUALITY_RUBRIC` | CLAUDE.md | v2.2.14 |
| `process_map_sipoc`, `detailed_process_map` as Tier 1 dicts | §10.8, §9.7 | CLAUDE.md | v2.2.12 |
| `stability_assessment` Tier 1 | §9.7 | CLAUDE.md | v2.2.12 |
| `experiment_justification` Tier 1 | §10.8 | CLAUDE.md | v2.2.12 |
| eBook fields (`issues_and_barriers`, `secondary_metrics`, etc.) | §0.6, §9.7, §10.7 | CLAUDE.md | v2.2.11 |
| Executor contract (5 nodes, 2 graders, 5 middlewares) | §3.3, §8.1, §8.2 | CLAUDE.md | v2.2.10 |
| State design (all 15 findings) | §10.1–§10.6 | CLAUDE.md | v2.2.9 |
| Multi-query Option A | ARCHITECTURE.md §7.4 | — | **PENDING** |
| `improve_case_index` `content_vector` rename | ARCHITECTURE.md §7.3 | — | **PENDING** |
