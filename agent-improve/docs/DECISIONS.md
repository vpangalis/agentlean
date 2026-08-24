<!--
Document: agent-improve/DECISIONS.md
Version: 1.4 — 2026-08-19
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

v1.1 changes (2026-08-11): §37 compliance audit cross-references added to E3 and E4;
  Part K added (Memory Architecture — §37 taxonomy + §37-D Procedural ratification);
  Amendment Log updated.
v1.2 changes (2026-08-12): Part L added (Validation Architecture — §48/§68 decisions);
  L1 (D68-1) ratified: AzureChatOpenAI invoke requires message list not plain string.
  D09 diagram added to ARCHITECTURE_DIAGRAMS.html covering constraint validation and
  retry-with-accumulated-feedback loop.
v1.3 changes (2026-08-12): B3 amended from five to seven middlewares
  (ContradictionDetectionMiddleware + CoherenceMiddleware added); B2 note added
  (L2a moved to CoherenceMiddleware; DMAICGraderMiddleware now process-quality-only);
  Part M added (M1 D69-x closed, M2 §38 middleware, M3 CoherenceMiddleware);
  Amendment Log updated.
v1.4 changes (2026-08-19): B3 amended from seven to eight middlewares
  (ToolRetryMiddleware added at position 5 — wrap_tool_call hook);
  §22 Debate Agents deferred to §87 backlog (confirmed 2026-08-19);
  Part N added (N1 §67 Geographic Redundancy / DORA compliance — deferred to v2.2);
  Amendment Log updated.
v1.5 changes (2026-08-20): the Task 1 audit rulings applied. A2 field count
  corrected (15 -> 17, 3 plumbing + 14 content); E1 EnsembleRetriever claim
  corrected against the LangChain v1 migration guide; N1 §87 item renumbered
  14 -> 16 (14 and 15 were both already occupied); Part O added — O1
  SupervisorState / store-mediated boundary ruling, O2 improve_evidence_index
  schema (phase + uploaded_at), O3 disconnect policy (ABANDON), O4 minor
  citation corrections; Part P added — P1..P5 recording the audit
  contradictions and how each was resolved. Every ruling in this version is
  now APPLIED to REFACTORING_AGENT_IMPROVE.md, not merely logged.
-->

# Agent Improve — DECISIONS.md
# Version 1.5 — 2026-08-20

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

### A2 — PhaseState: seventeen fields (3 plumbing + 14 content)

**Status:** ADOPTED — landed in CLAUDE.md §10.1; **applied to REFACTORING §18 on 2026-08-20**  
**Source:** STATE_DESIGN_RESOLUTION.md Findings 4–6, 8–12; §71 compliance audit (2026-08-11)

```python
class PhaseState(TypedDict):
    # conversation plumbing (3)
    messages:           Annotated[list[BaseMessage], operator.add]
    history:            Annotated[list[str], operator.add]
    phase_context:      str

    # content fields (14)
    coaching_plan:      Optional[CoachingPlan]  # typed — §71-C; overwritten each planner turn
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
    hop_results:        list[str]           # ordered hop answers, planned multi-hop only; [] otherwise
    synthesis_output:   Optional[dict]      # SynthesisOutput from synthesis call; None for single-hop
```

Key naming decisions:
- `feedback` → split into `validator_feedback` (system) and `belt_edits` (Belt). Conflating them would have the coach reading Belt corrections as validation failures.
- `final: str` → `final: dict`. String forces downstream parsing.
- `coaching_plan: list[dict]` → `coaching_plan: dict`. One plan per planner turn; no upfront queue.
- `coaching_plan: dict` → `coaching_plan: Optional[CoachingPlan]` (Pydantic model — §71-C, 2026-08-11). Plain dict replaced by typed schema enforced via `with_structured_output`. `dict[str, Any]` annotation in the TypedDict is acceptable as interim; prefer typed.
- `gate_attempts` MUST be on `PhaseState` in the checkpoint, not in route scope — the v1 "attempts always reset to 0" bug came from route scope.
- `validator_feedback` makes the shared cap of 3 defensible: each entry records attempt, layer, criteria, and feedback; the coach reads the full list on retry.
- `hop_results` stores intermediate hop answers from the Analyse planned multi-hop pipeline in PhaseState (not in a local Python dict). Required for LangSmith inspectability and checkpoint recovery (§71-E, 2026-08-11). Cleared to `[]` at start of each coaching turn.
- `synthesis_output` stores the `SynthesisOutput` from the dedicated synthesis LLM call (§71-D Option B, 2026-08-11). The coach call reads from this field, not from a local variable. `None` for single-hop turns. Total PhaseState field count: **17 (3 plumbing + 14 content)**.

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

**L2a coherence is now in `CoherenceMiddleware`, not in `COACHING_QUALITY_RUBRIC`.** `DMAICGraderMiddleware` grades coach **process quality only**: seven-step computation pattern, show-first principle, citations, no external URLs. The L2a coherence check (real statement? not parroting? on-topic?) was removed from the rubric in Mod B (M3). Any reference to "coherence" as a `DMAICGraderMiddleware` criterion is stale.

---

### B3 — Eight middlewares; declaration order is execution order

**Status:** ADOPTED — landed in CLAUDE.md §8.1  
**Source:** STATE_DESIGN_RESOLUTION.md Findings 19–20; Mod A (2026-08-12); Mod B (2026-08-12); B3.1 amendment (2026-08-19)

```python
middleware=[
    BeforeModelStateInjection(...),            # before_agent — MUST be first
    DMAICSkillsMiddleware(...),                # before_agent
    SummarizationMiddleware(...),              # before_model
    ModelRetryMiddleware(max_retries=2),       # wrap_model_call — API-level model retries
    ToolRetryMiddleware(                       # wrap_tool_call — tool execution retries (B3.1)
        max_retries=2,
        tools=None,          # None = applies to all bound tools
        on_failure="continue",
        backoff_factor=2.0,
        initial_delay=1.0,
        max_delay=60.0,
        jitter=True,
    ),
    ContradictionDetectionMiddleware(...),     # after_agent — §38 check (Mod A)
    CoherenceMiddleware(...),                  # after_agent — L2a check (Mod B)
    DMAICGraderMiddleware(...),                # after_agent — process quality only
]
```

`BeforeModelStateInjection` MUST be first — project facts must reach the
top of the prompt before skills loading and summarisation shape it.

**Two retry middlewares — distinct and complementary:**

| Middleware | Hook | Failure type | Mechanism |
|---|---|---|---|
| `ModelRetryMiddleware(max_retries=2)` | `wrap_model_call` | Azure OpenAI API errors (rate-limit, timeout, transient 5xx) | Retries the model call before it surfaces to the agent |
| `ToolRetryMiddleware(max_retries=2)` | `wrap_tool_call` | Tool execution errors (Azure Search timeout, extraction error, computation tool failure) | Retries the tool call before it surfaces as a `ToolMessage` error in state |

**Parameter correction, 2026-08-21.** Both entries above previously read
`ModelRetryMiddleware(retries=2)`. **`retries=` does not exist on that class
and raises at construction — the keyword is `max_retries`.** The two retry
middlewares share a parameter vocabulary; `ToolRetryMiddleware` was verified
against the reference when it was added at B3.1 and was always correct, while
`ModelRetryMiddleware` was adopted earlier and never re-checked. Verified
against `reference.langchain.com/python/langchain/agents/middleware/model_retry/ModelRetryMiddleware`;
full record in `BIBLE_VERIFICATION_LOG.md` C-1.

`on_failure="continue"` means: if `max_retries` is exhausted, the tool call returns whatever it has (or a failure message) rather than raising an exception. This keeps the coach loop alive on tool failures — the coach sees the failure result and can decide how to proceed rather than the graph dying.

The fallback chain (§4.8) is distinct from both retry middlewares — it swaps the model on service-level failure, not on individual call failure.

`ContradictionDetectionMiddleware` implements the §38 mid-phase contradiction
check: deterministic dict comparison (no LLM call). Reads
`CoachingResponse.fields_captured` from state after the executor runs,
compares against store-held prior gate values for this phase. Any mismatch
raises `HITLInterrupt`. Ratified as Mod A (2026-08-12). See M2.

`CoherenceMiddleware` fires `after_agent` immediately before
`DMAICGraderMiddleware`. Makes one LLM call (operational model, temp 0.1)
to check whether the gate document is a real, conclusive statement — not
parroting, not off-topic. On failure: Level 1 Silent retry (max 2).
On third failure: degraded mode response. `DMAICGraderMiddleware` is skipped
entirely when coherence fails — this is intentional, not an oversight;
catching incoherence early avoids a wasteful grader call on a response that
is already known to be inadequate. Ratified as Mod B (2026-08-12). See M3.

**Hook execution note:** `ToolRetryMiddleware` fires on `wrap_tool_call` — a different
hook from the `after_agent` middlewares at positions 6–8. Declaration order between
middlewares on different hooks is irrelevant — they do not compete for the same slot.
Position 5 is chosen for logical grouping alongside `ModelRetryMiddleware` (both are
`wrap_*` hooks, both are retry mechanisms).

Adding a new middleware or reordering this stack requires an amendment to B3.

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

`EnsembleRetriever` — **moved to `langchain_classic` in the LangChain 1.0
namespace split; not importable from `langchain` in the current version.**
It also solves the wrong problem: it combines results from **different
retriever sources** (e.g., BM25 + vector), whereas our pattern is
**same-index multi-query RRF** — N phrasings against one index. No standard
LangChain 1.x class exists for this pattern. The LangChain rag-fusion template
(v0.2) also used a custom implementation for the same reason. Custom 15-line
`reciprocal_rank_fusion()` is correct, stable, and dependency-free.

> **Correction, 2026-08-20 (audit ruling C3).** This entry previously read
> "not deprecated (active in `langchain.retrievers.ensemble`, confirmed v0.3)."
> That is wrong and it contradicted CLAUDE.md §7.4 and REFACTORING §35, both
> of which say the class moved to `langchain_classic` at the 1.0 migration.
> Verified against the official LangChain v1 migration guide: **CLAUDE.md §7.4
> and REFACTORING §35 are correct; this entry was not.** The "confirmed v0.3"
> observation predates the 1.0 namespace split.
>
> **The conclusion never depended on the wrong fact.** Custom RRF was already
> correct on architectural grounds alone — wrong-problem, not just
> wrong-package. There are now two independent reasons and they agree, which
> is why no downstream decision moves.

Anthropic "Writing Tools for Agents" (Sep 2025, Tier 1) confirms the
encapsulation principle: complexity belongs inside the tool, not exposed to
the agent. The custom RRF matches this — clean tool interface, fusion hidden.

`rag_lookup_evidence` takes no `order_by` argument — `improve_evidence_index`
has no `uploaded_at` field (upload timestamp buried in non-sortable
`metadata` JSON blob). This is a schema change (ARCHITECTURE.md §7.7), not
a tool change.

**§37-C is VOID (closed 2026-08-20).** The §37 compliance audit recorded a
Medium finding that "§37's implementation note describes `EnsembleRetriever` as
deprecated" and asked for a prose update. Two things were wrong with it. First,
the prose is in **§35**, not §37 — §37 does not mention `EnsembleRetriever` at
all. Second, and decisively, that prose is **correct**: the C3 ruling above
confirms the class did move to `langchain_classic`. §37-C asked for correct text
to be changed to match an incorrect log entry. **No action. Do not apply it.**

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

**§37 cross-reference (2026-08-11):** §37 compliance audit confirmed this same bug as
§37-A (Critical) in §37's implementation note for `rag_lookup_methodology`. The fix
is identical: `f"phase_relevance eq '{phase}' or phase_relevance eq 'general'"`.
No new decision — same fix, second confirmation. Tracked for batch commit to REFACTORING §37.

---

### E4 — Retrieval filters are per-call arguments on `AzureSearch`; `AzureAISearchRetriever` is not adopted

**Status:** SUPERSEDED and REWRITTEN 2026-08-21 (Task 2 codebase cross-check)  
**Supersedes:** the 2026-08-11 version of E4, which mandated a per-call `AzureAISearchRetriever(filters=...)` constructor  
**Source:** `backend/knowledge/retriever.py`; GitHub #29756, #21492, #14227, #30482

**The original finding was correct about a class Agent Improve does not
use.** `AzureAISearchRetriever` genuinely does take `filters` at
construction and not via `search_kwargs` at invoke time — issue #30482's
*"got multiple values for keyword argument 'filter'"* is real. And because
`phase` is dynamic, that class would indeed force per-call instantiation.

**But the codebase uses `AzureSearch`** — the
`langchain_community.vectorstores.azuresearch` vectorstore — whose
`similarity_search(query, k=..., filters=...)` takes the filter **at call
time**:

```python
vs = get_knowledge_vectorstore()          # module-level, @lru_cache(maxsize=1)
filters = f"phase_relevance eq '{phase}' or phase_relevance eq 'general'"
docs = vs.similarity_search(query, k=k, filters=filters)
```

The dynamic filter never touches construction, so the cached module-level
singleton is correct and there is no per-call instantiation cost.
`improve_case_index` additionally uses a **raw `SearchClient`**, because
`AzureSearch` resolves its content and vector field names from
process-global settings that default to `content` / `content_vector`, and
that index uses `content_text` / `embedding`.

**Ruling: do not adopt `AzureAISearchRetriever`** (2026-08-21). The current
mechanism works, is in place, and already carries the correct
`phase_relevance` filter. Adopting a different retrieval class is a
migration, not a bug fix, and nothing in the audit produced a reason for one.

**Open for Task 3B:** confirm against current LangChain docs whether
`AzureAISearchRetriever` offers anything `AzureSearch` does not — semantic
ranker access, better hybrid scoring control, a supported upgrade path.
**Revisit only if it does.** Absent a concrete gain, this stays closed.

**What genuinely IS construction-time, and binds:** `fields=`. LangChain
promotes a metadata key to a filterable top-level field only when the key
matches a name in `self.fields`, which defaults to
`[id, content, content_vector, metadata]` and never introspects the live
index. `get_knowledge_vectorstore()` passes `fields=KNOWLEDGE_INDEX_FIELDS`
for exactly this reason. **Omitting it silently buries `phase_relevance` in
the `metadata` JSON blob where `$filter` cannot reach it, with no error** —
which is the original cause of the filter never working. This is the real
constructor-time constraint, and it is not the one E4 originally recorded.

**§37 cross-reference:** §37-B recorded the same superseded finding and is
rewritten with it. No separate action.

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

**Graceful shutdown — the requirement is ratified, the mechanism is not.**
`RunControl.request_drain()` is **UNCONFIRMED — MAY NOT EXIST** as of
2026-08-21: not found in LangGraph releases 1.2.5–1.2.11 or in the reference.
**No work may be scheduled against it until it is confirmed against a real
release or the source**; if it does not exist, a real fallback drain must be
designed. See `../../AGENTIC_ARCHITECTURE_REFERENCE.md` §45.

Custom Saga orchestrators and hand-written compensating-action frameworks
are BANNED.

---

### F2 — §80: AgentMiddleware six hooks foundation

**Status:** LANDED — CLAUDE.md §8.1–§8.7, ARCHITECTURE.md §3.4  
**Source:** status-79-84-2026-08-10.md; REFACTORING §80

The eight-middleware stack is built on the six `AgentMiddleware` hooks:
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

### F6 — §34: Hop cap via `RemainingSteps`, not `recursion_limit`

**Status:** RATIFIED 2026-08-11  
**Source:** REVIEW_DECISIONS.md §34 compliance audit; LangGraph Discussion #1260; deepagents Issue #1698

Two separate mechanisms serve two separate purposes:

**`RemainingSteps` — hop cap (business logic)**  
LangGraph managed value readable inside the agent node at runtime. Initialise
at the start of each executor turn; decrement each tool call. When `remaining_steps <= 2`,
the agent node synthesises from what it has and returns a partial answer. The Belt
always receives a composed response — never a hard crash.

```python
from langgraph.managed import RemainingSteps

def agent_node(state: PhaseState) -> dict:
    if state.get("remaining_steps", 10) <= 2:
        return {"messages": [synthesise_partial(state)]}
    return run_agent_step(state)
```

Survives subgraph boundary — it is in-graph state, not config propagation.

**`recursion_limit` — infinite loop backstop (infrastructure safety)**  
Set high on the supervisor invocation (e.g., 50). Catches genuine bugs
and runaway loops. Does NOT control the per-turn hop budget.

```python
await supervisor.ainvoke(
    state,
    config={"recursion_limit": 50, "configurable": {"thread_id": case_id}},
)
```

**Why `recursion_limit=11` alone does not work:**  
In our hierarchy (supervisor → phase subgraph → executor), `recursion_limit`
is either shared (supervisor and routing steps consume the budget before the
executor starts — Discussion #1260) or not propagated at all (subgraph reverts
to default 25 — deepagents Issue #1698). Neither reliably gives the executor
exactly 5 hops.

**§34-D model tiering deferred to §87 backlog (2026-08-11):** gpt-4o-mini intermediate /
gpt-4o final synthesis requires RemainingSteps-gated model swap in a custom agent node.
Deferred until LangSmith confirms repeated 5-hop cap hits on Analyse-phase turns.

---

### F7 — §71: Planned multi-hop architecture — three ratified decisions

**Status:** RATIFIED 2026-08-11  
**Source:** REVIEW_DECISIONS.md §71 compliance audit

Three decisions ratified that are specific to the Analyse-phase planned multi-hop pipeline (§71):

**F7a — `RemainingSteps` guard at planned multi-hop node entry**  
The for-loop inside `analyse_executor_node` runs entirely within one LangGraph node invocation; `RemainingSteps` does not decrement per hop. The hop count is bounded at exactly 3 by the `Plan` schema (no runaway risk). A guard at node entry prevents the 3-hop sequence from starting when fewer than 2 steps remain:

```python
async def analyse_executor_node(state: PhaseState) -> dict:
    if state.get("remaining_steps", 10) <= 2:
        return {"messages": [synthesise_partial(state)]}
    # ... planner → for-loop → synthesis
```

**F7b — `CoachingPlan` typed Pydantic schema (§71-C)**  
`coaching_plan` on `PhaseState` must be produced via `with_structured_output(CoachingPlan)`, not a plain dict. Consistent with §82 ProviderStrategy typed-boundary discipline.

```python
class CoachingPlan(BaseModel):
    next_action: str
    retrieval_strategy: Literal["single_hop", "multi_hop"]
    retrieval_hops: list[str]    # template strings; empty for single_hop
    focus_field: str

phase_planner = llm.with_structured_output(CoachingPlan)
```

**F7c — Synthesis is a dedicated step; three LLM calls per Analyse multi-hop turn (§71-D, Option B)**  
Rationale: synthesis is a critical quality gate — assembling multi-hop evidence correctly before the coach translates it into coaching language. "A lean copilot the Belt can trust" requires careful synthesis, not brevity at the cost of quality.

Three calls per Analyse multi-hop turn:
1. Planner (0.1 temp) → `Plan` with hops + `synthesis_instruction`
2. Synthesis (0.1–0.2 temp) → `SynthesisOutput` (evidence chain, key finding, confidence, caveats) — NOT Belt-facing
3. Coach (0.5–0.7 temp) → coaching response delivered to Belt, reading from `synthesis_output` in PhaseState

Each call has one job. Temperature tuning is independent per call. Each stage is unit-testable independently. `synthesis_output: Optional[dict]` added to PhaseState (see A2). If LangSmith shows high latency on multi-hop Analyse turns, this is the trigger for §34-D model tiering (§87 backlog).

**`hop_results: list[str]` and `synthesis_output: Optional[dict]` in PhaseState (see A2):** Both stored in PhaseState for LangSmith inspectability and checkpoint recovery. Schema changes tracked in A2.

**Open assumption — planned multi-hop scope (2026-08-11):** The planned multi-hop pipeline (for-loop, `hop_results`, synthesis LLM call) is implemented only in `analyse_executor_node`. Other phase executor nodes are standard ReAct. The assumption is that reactive tool calling is sufficient for non-Analyse turns. This is unverified — a Define Belt asking whether their problem statement is well-scoped against similar projects, or a Control Belt asking why Cpk remains borderline, could equally benefit from structured multi-hop + synthesis. `CoachingPlan.retrieval_strategy` is not restricted to Analyse; the planner can set `multi_hop` in any phase. Whether the planned pipeline should be extended to other phases is a question for LangSmith data: if non-Analyse turns show 3+ sequential tool calls with lower coaching quality than Analyse multi-hop turns, extend the mechanism. **To be validated during eval dataset phase (§75).**

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
`langchain.agents`. Nothing may import it, nothing may reference
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
| **O1 `SupervisorState` ruling — `DMAICState` retired, cross-phase data store-mediated only; §44 gains Mechanism 3** | New Part O (O1); REFACTORING §44 + 14 sites | DECISIONS.md | **v1.5 — 2026-08-20** |
| **O2 `improve_evidence_index` + `phase` + `uploaded_at`; `PhaseState.uploads` shape specified** | New Part O (O2); REFACTORING §36, §40 | DECISIONS.md | **v1.5 — 2026-08-20** |
| **O3 Disconnect policy ABANDON — five requirements added to §17 item 3 (not a new step)** | New Part O (O3); REFACTORING §17.3a, §18 | DECISIONS.md | **v1.5 — 2026-08-20** |
| **O4 `BaseStore.search()` supports `filter=`; Anthropic harness-post scope softened** | New Part O (O4); REFACTORING §52, §44, §45 | DECISIONS.md | **v1.5 — 2026-08-20** |
| **P1–P5 audit contradictions resolved; E1 EnsembleRetriever corrected; §37-C VOID** | New Part P; E1; A2 | DECISIONS.md | **v1.5 — 2026-08-20** |
| **N1 §87 backlog number corrected 14 → 16 (14 and 15 both occupied)** | N1; REFACTORING §87 | DECISIONS.md | **v1.5 — 2026-08-20** |
| **Category A applied to REFACTORING — 16 change sets, previously logged but never written back** | REFACTORING §10, §17, §18, §29, §33, §34, §35, §36, §37, §40, §44, §52, §67, §71, §80, §82, §84, §87 | REFACTORING_AGENT_IMPROVE.md | **v1.5 — 2026-08-20** |
| B3 amended: seven → eight middlewares (ToolRetryMiddleware added at position 5) | B3, F2 | DECISIONS.md | v1.4 — 2026-08-19 |
| §22 Debate Agents deferred confirmed (no implementation in v2.1) | New Part N (N2) | DECISIONS.md | v1.4 — 2026-08-19 |
| N1 §67 Geographic Redundancy / DORA compliance deferred to v2.2 | New Part N (N1) | DECISIONS.md | v1.4 — 2026-08-19 |
| B3 amended: five → seven middlewares (ContradictionDetectionMiddleware + CoherenceMiddleware) | B3 | DECISIONS.md | v1.3 — 2026-08-12 |
| M1 D69-x decisions confirmed closed | New Part M (M1) | DECISIONS.md | v1.3 — 2026-08-12 |
| M2 §38 check → ContradictionDetectionMiddleware (Mod A ratified) | New Part M (M2) | DECISIONS.md | v1.3 — 2026-08-12 |
| M3 CoherenceMiddleware replaces L2a in COACHING_QUALITY_RUBRIC (Mod B ratified) | New Part M (M3) | DECISIONS.md | v1.3 — 2026-08-12 |
| D68-1 ratified: AzureChatOpenAI invoke requires message list not plain string | New Part L (L1) | DECISIONS.md | v1.2 — 2026-08-12 |
| D09 diagram added: constraint validation + retry-with-accumulated-feedback | ARCHITECTURE_DIAGRAMS.html | docs | v1.2 — 2026-08-12 |
| §37-D Procedural Memory taxonomy ratified (static v2.1 / dynamic v2.2+) | New Part K | DECISIONS.md | v1.1 — 2026-08-11 |
| §37-A/§37-B cross-references added to E3/E4 | E3, E4, E1 notes | DECISIONS.md | v1.1 — 2026-08-11 |
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

---

## Part K — Memory Architecture

### K1 — §37 memory taxonomy: four types confirmed, procedural type ratified (§37-D)

**Status:** RATIFIED 2026-08-11 (§37-D)  
**Source:** REVIEW_DECISIONS.md §37-D; LangMem Tier 1 (langchain-ai.github.io/langmem)

§37 of REFACTORING_AGENT_IMPROVE.md documents four memory types for Agent Improve:
Episodic, Semantic, Working, and Retrieval control. The §37 compliance audit (2026-08-11)
added a fifth — Procedural — as a distinct LangMem Tier 1 category, with a two-level
static/dynamic split ratified for Agent Improve:

| Memory type | What it stores | Agent Improve implementation | Status |
|---|---|---|---|
| Episodic | Per-case history: coaching turns, decisions made, gate outcomes | `step_log`, `improve_case_index`, `SummarizationMiddleware` | v2.1 |
| Semantic | Domain knowledge: DMAIC methodology, tools, templates | `improve_knowledge_index`, `rag_lookup_methodology` | v2.1 |
| Working | In-flight turn state: `artifacts`, `hop_results`, `synthesis_output` | `PhaseState` fields | v2.1 |
| Retrieval control | Which memory to query, when, how: planner decides strategy | `CoachingPlan.retrieval_strategy`, `rag_lookup_*` routing | v2.1 |
| Procedural (static) | How to execute DMAIC coaching — invariant rules, methodology steps, gate criteria | System prompt (CLAUDE.md), SKILL.md files via `DMAICSkillsMiddleware`, phase rubrics via `DMAICGraderMiddleware`, anti-hallucination guards | **v2.1** |
| Procedural (dynamic) | How to adapt coaching delivery — Belt-specific approaches, project-type emphasis, outcome-learned procedures | Per-Belt procedure store, updated via LangSmith trace analysis after gate outcomes | **v2.2+** |

**Static vs dynamic — the distinction that matters:**

Static procedural memory is the invariant DMAIC methodology — the same coaching
rules for every Belt, every project, every domain. This is correct and intentional.
The rules encoded in CLAUDE.md §8.2, the SKILL.md files loaded by
`DMAICSkillsMiddleware`, and the rubric criteria in `DMAICGraderMiddleware` should
NOT vary per Belt — that is the guarantee of methodology consistency.

Dynamic procedural memory is Belt-adaptive coaching delivery. It tracks how this
specific Belt learns best: how much scaffolding they need, whether worked examples
or challenge questions land better, which project-type emphasis helps them most.
It does not change the DMAIC methodology — it adapts how the methodology is delivered.

**Mechanism (v2.2+):** Dynamic procedural memory is the implementation of §87
backlog item 5, reframed from "LangSmith trace-based coaching learning":
- LangSmith traces record gate outcomes and per-turn coaching patterns per Belt
- After each gate: gate passed? How many turns? Which fields required retries?
- A background process (outside the coaching loop) updates a per-Belt procedure
  store with learned delivery adaptations
- The next session for this Belt loads these learned procedures alongside the
  static SKILL.md rules — extending, never overriding, the methodology

**What this is NOT:** Dynamic procedural memory does not change DMAIC content
requirements. A Black Belt still needs `vital_few_xs`. The coach might deliver
the Analyse phase differently for a BB who has completed 10 projects, but the
gate criteria are unchanged.

**§37-C note (Medium finding, not a new decision):** The §37 compliance audit
found that §37's implementation note still describes `EnsembleRetriever` as
deprecated. The correct position is in E1 above — EnsembleRetriever is active
but solves the wrong problem for our same-index multi-query pattern.
A prose update to §37 is tracked for the next batch commit to REFACTORING.

---

## Part L — Validation Architecture (§48 / §68)

### L1 — D68-1: AzureChatOpenAI invoke requires message list, not plain string

**Status:** RATIFIED 2026-08-12  
**Source:** §68 code review; confirmed against AzureChatOpenAI API (August 2026)

`AzureChatOpenAI.invoke()` — including the `.with_structured_output()` variant —
requires a messages list as its argument. Passing a plain string raises a
validation error at runtime. This applies to every standalone LLM call: the
L2c constraint checker, L2a coherence check, and all grader calls.

**The bug in §68's `validate_constraints`:**
```python
# WRONG — plain string, raises ValidationError at runtime
constraint_checker.invoke(
    f"Check whether this {phase} phase decision addresses each constraint.\n\n..."
)
```

**The fix — message tuple list:**
```python
# CORRECT — message tuple list
@traceable
def validate_constraints(decision: str, constraints: dict, phase: str) -> ConstraintCheckResult:
    constraints_text = "\n".join(f"- {k}: {v}" for k, v in constraints.items())
    return constraint_checker.invoke([
        ("system", "You are a constraint validator for DMAIC decisions. "
                   "Return a structured assessment of whether each constraint is addressed."),
        ("human",
         f"Phase: {phase}\n\n"
         f"Decision to evaluate:\n{decision}\n\n"
         f"Constraints to check:\n{constraints_text}\n\n"
         "For each constraint, state whether it is addressed and cite evidence from the decision text.")
    ])
```

**Three valid invocation forms** (all equivalent, all correct):
1. List of message tuples: `[("system", "..."), ("human", "...")]` — preferred for inline calls
2. List of message objects: `[SystemMessage(content="..."), HumanMessage(content="...")]`
3. `ChatPromptTemplate` + chain: `chain.invoke({...})` — prefer when the same template is reused across multiple call sites

For `validate_constraints` specifically, option 1 (message tuple list) is correct.
`ChatPromptTemplate` adds indirection with no benefit for a single-site validation
function. The three-prompt separation principle (generate / validate / correct as
separate `.invoke()` calls) is satisfied by any of the three forms — the form
choice does not affect the separation.

**Applies to all standalone LLM calls in the validation stack:**
- L2a coherence check — must use message list (now in `CoherenceMiddleware`, see M3)
- L2c constraint check (`validate_constraints`) — must use message list
- L2d grader (DMAICGraderMiddleware) — already implemented via middleware, not direct `.invoke()`; not affected

**`@traceable` still required** on `validate_constraints` and other non-LangChain
functions for LangSmith visibility. Confirmed current as of August 2026
(docs.smith.langchain.com).

---

## Part M — Middleware Amendments (2026-08-12)

### M1 — D69-x open decisions: all confirmed closed

**Status:** CONFIRMED CLOSED 2026-08-12  
**Source:** §69 ratification; B1/B2/B3/B6 existing decisions; this session

Three decision points that were presented as open during §69 review are confirmed
resolved by pre-existing ratifications:

| Decision | Subject | Resolved by | Resolution |
|---|---|---|---|
| D69-1 | L2a coherence hook placement | B2 (two graders rule); now superseded by M3 | `CoherenceMiddleware` `after_agent` hook — not inside executor node, not in `DMAICGraderMiddleware` |
| D69-2 | `validate_constraints` as mid-conversation universal tool | B6 (seven universal tools, `validate_constraints` not on list); §69 ratification (Level 2 = coaching dialogue) | Stays as `validation_stack` layer. Not a universal tool. |
| D69-3 | §38 contradiction check placement | §38 ratification; now superseded by M2 | `ContradictionDetectionMiddleware` `after_agent` hook — not inside executor node |

No new decisions required. These were implementation clarity gaps, not open
architectural choices.

---

### M2 — §38 contradiction check: moved to `ContradictionDetectionMiddleware` (Mod A)

**Status:** RATIFIED 2026-08-12  
**Source:** §38 ratification (existing); Mod A placement decision (this session)

The §38 mid-phase contradiction check is implemented as a dedicated
`ContradictionDetectionMiddleware` (`after_agent` hook), not embedded inside
the executor node.

**What it does:** After the executor runs each turn, reads
`CoachingResponse.fields_captured` from state and compares each captured field
against store-held prior gate values for the current phase. Any value change
on an already-approved field raises `HITLInterrupt`.

**Why middleware, not executor node:** The check is architecturally separate
from coaching — it reads the executor's output and polices it against approved
state. Putting it in the middleware stack gives it a named, LangSmith-visible
step and keeps the executor node responsible only for coaching.

**Implementation shape:**

```python
class ContradictionDetectionMiddleware(AgentMiddleware):
    def after_agent(self, state, runtime):
        fields_captured = state.get("structured_response", {}).fields_captured
        for field in fields_captured:
            prior = store.get(
                ("projects", state["case_id"], "artifacts"),
                state["current_phase"]
            )
            if prior and field["field_name"] in prior:
                if prior[field["field_name"]] != field["value"]:
                    raise HITLInterrupt(
                        field=field["field_name"],
                        approved_value=prior[field["field_name"]],
                        proposed_value=field["value"]
                    )
```

**No LLM call.** Deterministic dict comparison only. The §38 "no tolerance
threshold" rule (G7) applies — any mismatch interrupts regardless of magnitude.

Position in stack: sixth (after `ToolRetryMiddleware`, before `CoherenceMiddleware`).

---

### M3 — L2a coherence check: moved to `CoherenceMiddleware` (Mod B)

**Status:** RATIFIED 2026-08-12  
**Source:** §69/§38 review; Mod B decision (this session)

The L2a coherence criterion is removed from `COACHING_QUALITY_RUBRIC` and
implemented as a dedicated `CoherenceMiddleware` (`after_agent` hook) that fires
immediately before `DMAICGraderMiddleware`.

**What it checks (LLM call, operational model, temp 0.1):** Is the gate document
a real, conclusive statement? Is it parroting the Belt's own words back? Is it
on-topic for the current phase?

**Retry behaviour:**
- FAIL → Level 1 Silent retry. Belt never sees the failed response.
- Max 2 retries.
- Third failure → degraded mode: `"I'm experiencing a temporary connection issue. {n} fields captured so far — let's continue once I reconnect."`

**`DMAICGraderMiddleware` skip on coherence failure:** If `CoherenceMiddleware`
fails and triggers degraded mode, `DMAICGraderMiddleware` does not run. This is
intentional — grading an incoherent response would waste a model call and produce
meaningless scores. Catching the quality failure at the coherence gate is faster
and cheaper.

**`COACHING_QUALITY_RUBRIC` change:** L2a coherence criterion is removed. The rubric
now covers process quality only: seven-step computation pattern, show-first
principle, no external URLs, citations present. Any reference to "coherence" as
a `DMAICGraderMiddleware` criterion is stale (see also B2).

**Retry cap independence:** `CoherenceMiddleware` has its own 2-retry cap on
response quality. `ModelRetryMiddleware` has a separate 2-retry cap on API-level
transient failure. They are independent and do not share a counter.

Position in stack: seventh (after `ContradictionDetectionMiddleware`, before
`DMAICGraderMiddleware`).

---

## Part N — Deferred Features (2026-08-19)

### N1 — §67 Geographic Redundancy: DORA / EU AI Act compliance (deferred to v2.2)

**Status:** DEFERRED to **§87 backlog item 16** — v2.2 pre-production  
**Date:** 2026-08-19; backlog number corrected 2026-08-20  

> **Numbering correction (audit ruling C6).** This entry originally claimed
> §87 item 14. Item 14 was already the **Observer Agent** (§43), and item 15
> was already the **multi-source knowledge index** (§37/§60, Finding 27).
> The ruling was to renumber the newer addition rather than an established
> one; applied against the real table, that makes geographic redundancy
> **item 16**. Both existing entries keep their numbers.
**Source:** User decision this session; DORA ICT resilience requirements; EU AI Act data governance

**Finding:** The ratified §67 four-level fallback chain has a single-region dependency. Levels 1–3 (gpt-4o, gpt-4o-mini, Redis Cache) are all provisioned in Azure West Europe (Frankfurt). A Frankfurt regional outage collapses all three active levels simultaneously, leaving only Level 4 degraded mode. This is non-compliant with DORA's ICT resilience obligation to maintain continuity of critical functions via geographic redundancy.

**The v2.1 fallback chain is unchanged.** The four-level chain remains the v2.1 implementation target:

```
Level 1: gpt-4o (Frankfurt) → Level 2: gpt-4o-mini (Frankfurt) → Level 3: Redis Cache → Level 4: Degraded mode
```

**Ratified v2.2 replacement — five-level geographically redundant chain:**

```
Level 1: Azure OpenAI gpt-4o        — West Europe (Frankfurt) — primary
Level 2: Azure OpenAI gpt-4o        — secondary EU region (TBD — Sweden Central candidate)
Level 3: Azure OpenAI gpt-4o-mini   — secondary EU region
Level 4: Azure Redis Cache           — session-scoped response cache
Level 5: Degraded mode               — always succeeds, never crashes
```

**Open decision for v2.2:** secondary region. Sweden Central is the candidate (EU data residency, low latency from Frankfurt, Azure OpenAI available). Requires Azure OpenAI quota provisioned in that region under the same subscription — connection string swap only, no model change.

**Note on TPM vs regional outage:** TPM (Tokens Per Minute) rate-limit exhaustion is handled correctly in v2.1 — a 429 at Level 1 is classified transient, exponential backoff fires, chain activates. The geographic redundancy amendment handles the separate case where Frankfurt is unreachable (regional outage) or the TPM backoff exhaustion propagates to Level 2 before recovering.

**§87 backlog item 16** — landed in REFACTORING §87 on 2026-08-20:

| # | Source | Deferred capability | Why deferred | Promotion trigger |
|---|---|---|---|---|
| 16 | §67 / DORA | Geographic redundancy — secondary Azure OpenAI deployment in second EU region | Infrastructure provisioning decision deferred until base refactor stable; not a v2.1 blocker | Before production launch with real Belts — DORA compliance requires this before any regulated-entity deployment |

---

### N2 — §22 Debate Agents and Consensus Voting: deferred to post-v2.1

**Status:** DEFERRED — no implementation in v2.1  
**Date:** 2026-08-19 (confirmed)  
**Source:** User decision this session; §22 preliminary scoping only

**Decision:** §22 (adversarial debate pattern — advocate + skeptic + judge, Analyse phase only) will not be implemented in v2.1. The refactoring must stabilise the base coaching loop and the Analyse node must be tested in production before deciding whether to add this feature.

**Promotion trigger:** base coaching loop stable + Analyse phase tested in production → evaluate whether debate agents add measurable value.

**§47 Opinion Aggregation is blocked behind §22.** Also deferred; cannot be ratified until §22 is implemented and validated.

**Status at deferral:** §22 had preliminary scoping only in REVIEW_DECISIONS.md — no full review had been completed prior to this deferral decision.

---

## Part O — v2 Rewrite Decisions (2026-08-20)

*Four decisions ratified during the Task 1 audit sign-off. O1 resolves a
contradiction between the review log and CLAUDE.md; O2 and O3 are genuinely
new scope that had never been logged; O4 is two citation corrections.
**All four are applied in REFACTORING_AGENT_IMPROVE.md**, not merely recorded.*

### O1 — `SupervisorState` is the parent state; cross-phase data is store-mediated only

**Status:** RATIFIED 2026-08-20 — applied to REFACTORING §44 and 14 other sites  
**Source:** Task 1 audit finding B1; CLAUDE.md §1.2, §10.1, §10.2

REFACTORING §44's "Correct Implementation for Agent Improve" block declared a
parent state class named `DMAICState` carrying `define_output` and
`measure_output`, and explained that those fields "cross the boundary
automatically" because the key names are shared with the child state.

**Every part of that is wrong under the ratified design**, and it mattered more
than an ordinary stale passage because it was the block a reader would copy as
*the* reference implementation:

| Claim | Contradicts |
|---|---|
| Parent class is `DMAICState` | CLAUDE.md §10.1 / §17 — the class is `SupervisorState` |
| Parent carries `define_output`, `measure_output` | CLAUDE.md §10.1 — seven fields, orchestration only; artifacts are a violation |
| Shared key names carry data across the phase boundary | CLAUDE.md §10.2 and §1.2 — cross-phase data flows through the Store; subgraph state is not guaranteed to propagate to the parent |

**Ruling: CLAUDE.md wins.** REVIEW_DECISIONS.md's §44 reconciliation table
(the line reading *"Shared key names (Mechanism 1) for boundary crossing —
Compatible with ratified design"*) is the stale artifact. A review-log line
does not override the constitution.

**Applied:**
- `DMAICState` → `SupervisorState` at all 15 occurrences
- Per-phase output fields removed from every parent-state occurrence
- §44's reference block rewritten to the store-mediated form with explicit
  `define_output_mapper` / `measure_input_mapper` functions
- **§44 gained "Mechanism 3 — the Store."** §44 previously documented only two
  boundary mechanisms, both in-graph. That omission is the root cause of the
  drift: with only shared-keys and transformers on the page, shared keys looked
  like the answer to "how does Define's output reach Measure." Adding the third
  mechanism, and marking the first two explicitly as in-graph-only, closes the
  gap that produced the error rather than only fixing its output.

### O2 — `improve_evidence_index` gains `phase` and `uploaded_at`

**Status:** RATIFIED 2026-08-20 — new scope, not previously logged  
**Source:** Task 1 audit finding B2

```
improve_evidence_index (7 fields, was 5)
  id, content, content_vector, metadata, case_id        [existing]
  phase         Edm.String  — NEW, auto-set from state["current_phase"] at upload
  uploaded_at   Edm.String  — NEW, ISO 8601, server-side, never Belt-entered
```

`uploaded_at` closes a gap **E1 itself had flagged and worked around**: the
recency ordering `rag_lookup_evidence` wanted was unavailable because the
timestamp lived only inside the non-sortable `metadata` JSON blob. As a
top-level field it sorts correctly and the ordering clause becomes available.

`phase` closes a problem that had never been articulated: two similar documents
uploaded at different phases were **indistinguishable at retrieval time**. Since
this index is the only channel for external data (§39), that ambiguity lands
directly on the coaching answer.

`rag_lookup_evidence` gains an **optional `phase` filter, default unfiltered** —
cross-phase evidence retrieval is the normal case, not the exception (a Control
Belt comparing against the Measure baseline), so filtering by default would
break the comparison the field exists to enable.

Both fields are server-set. **Requires a reindex — batch with E2's
`content_vector` standardisation** so the corpus is rebuilt once.

**Consequential:** `PhaseState.uploads` gains a specified internal shape, which
it previously lacked:
```python
uploads: list[dict]
# {"evidence_index_id": str, "filename": str, "phase": str,
#  "uploaded_at": str, "summary": str}
```

### O3 — Disconnect policy: ABANDON, not COMPLETE

**Status:** RATIFIED 2026-08-20 — new scope, not previously logged  
**Source:** Task 1 audit finding B3; Ranjan Kumar, *"FastAPI + LangGraph: What a Client Disconnect Commits"* (measured 2026-08-04)

**Step mapping:** this is **not a new "Step 6."** It is additional scope on the
existing work of wiring `thread_id` through `graph.ainvoke` — REFACTORING §17
item 3, "Checkpointing", where the disconnect policy now lives as §17 item 3a.
No parallel numbering scheme was created.

**The finding:** once checkpoints actually write, the **FastAPI handler's
control-flow shape — not the checkpointer — decides what survives a client
disconnect.** A handler that hands the run to a bare `asyncio.create_task`
keeps executing after the Belt is gone and checkpoints every node it completes.

**Policy: ABANDON.** A silently-completed gate approval the Belt never saw is
unacceptable in a system whose premise is that the Belt approves what gets
committed (§2 step 7). COMPLETE is defensible for idempotent background work;
it is not defensible for a nine-step HITL gate.

Five requirements, all in scope for that step:

| # | Requirement |
|---|---|
| 1 | Deliberate handler shape — inline `await` streaming, or explicit ABANDON with `t.cancel()` in `gen()`'s `finally`. Never a bare `asyncio.create_task` with no disconnect handling |
| 2 | Deterministic `step_log` keys — `f"{phase}:{turn_count}:{step_name}"`, never a raw timestamp as identity |
| 3 | Azure Blob lease as the per-thread concurrency guard (Postgres advisory locks unavailable pre-migration) |
| 4 | Reconciliation sweep for abandoned threads that **excludes `interrupt()`-paused threads** |
| 5 | `thread_id` / `case_id` derived from the authenticated session, never client-supplied |

**`gate_apply_node` needs no change** — its store write is already idempotent by
key. The exposure is in `step_log` (requirement 2) and concurrent writers
(requirement 3).

### O4 — Two citation corrections

**Status:** RATIFIED 2026-08-20  
**Source:** Task 1 audit finding B4

**`BaseStore.search()` does support metadata filtering** via `filter=`. §52
listed metadata filters among the things the store lacks, which overstated the
case for keeping `improve_case_index` on Azure AI Search. The two capabilities
the store genuinely lacks are **hybrid BM25 + vector scoring** and
**multi-query + RRF** — which are the two the yokoten use case depends on, so
Option A resolves the same way. Right conclusion, one wrong reason, now removed.

**The Anthropic March 2026 harness-design post is scoped more narrowly than
§44/§45 claimed.** It is a specific research write-up on long-running *coding*
harnesses, not general Anthropic architecture guidance superseding "Building
Effective Agents." The Planner/Generator/Evaluator comparison is kept — the
convergence is real and worth recording — but framed as strong evidence from an
adjacent domain rather than as a specification. The Dec 2024 post's downgraded
status is likewise softened: it is ordered lower because newer specific material
exists, not because it was refuted.

---

## Part P — Audit Contradictions Resolved (2026-08-20)

*Five contradictions the Task 1 audit found **inside the decision logs
themselves**, each recorded here with its resolution so the losing side cannot
be cited later as if it were live.*

| # | Contradiction | Resolution |
|---|---|---|
| **P1** | §71-D: the finding body ratifies Option B = **three** LLM calls; the §71 Actions Summary table says *"synthesis = coaching response, 2 LLM calls total"* | **Body wins — three calls** (planner, synthesis, coach). The table was a drafting error from the pre-ratification version. Fixed in REVIEW_DECISIONS.md and applied to REFACTORING §71 |
| **P2** | PhaseState count stated four ways: A2 heading "fifteen content fields", code comment `(15)`, an actual list of 14, closing line "17 (3+14)"; REVIEW_DECISIONS §71-E said "field 13" and "13 fields" | **17 total = 3 plumbing + 14 content.** Standardised in DECISIONS A2, REVIEW_DECISIONS §71-E, and REFACTORING §18 |
| **P3** | `EnsembleRetriever`: DECISIONS E1 said "not deprecated, active in `langchain.retrievers.ensemble`"; CLAUDE.md §7.4 and REFACTORING §35 said "moved to `langchain_classic`" | **CLAUDE.md and §35 correct; E1 wrong.** Verified against the LangChain v1 migration guide. E1 corrected. See E1 and §37-C VOID |
| **P4** | §34-D model tiering: "DEFERRED" in the finding body, "OPEN" in the same audit's Category-C table-update text | **DEFERRED** — consistent with the body and with the §87 backlog entry. Table text fixed |
| **P5** | `completeness_score`: REFACTORING §10 annotated it *"computed, not captured — float is correct"*; §17/§77 say no such stored field exists | **No stored field.** §17/§77 correct. The §10 annotation defended the *type* and missed the question. Removed from all §10 sketches with an explanatory note |

**One further inconsistency, resolved by the same principle:**
`ModelRetryMiddleware(retries=3)` appeared in one §80 illustration against
`retries=2` everywhere else. **Standardised on `retries=2`**, and that
illustration is now explicitly labelled as a generic LangChain example rather
than Agent Improve's stack — it also contained `HumanInTheLoopMiddleware`,
which is BANNED for our gates (§53).

*Superseded 2026-08-21: the keyword itself was wrong. It is `max_retries`, not
`retries` — see B3 and `BIBLE_VERIFICATION_LOG.md` C-1. The "standardise on
2" ruling stands; only the parameter name changed.*

---

## Part Q — Cross-agent tools (2026-08-21)

### Q1 — Cross-agent tools are a distinct category, present but unbound

**Status:** RATIFIED 2026-08-21
**Source:** Task 4 (Refactoring Procedure) Appendix E question 1
**Lands in:** `../../AGENTIC_ARCHITECTURE_REFERENCE.md` §29.4 (new); this entry is both the
decision record and the change-log entry required by §56

**The question.** `backend/knowledge/tools.py` defines four `@tool` functions
that reach outside Agent Improve — `search_resolve_cases`,
`search_resolve_knowledge`, `search_resolve_evidence` and `search_flow_vsm`.
**No section of the architecture reference stated their disposition**, and two sections were in tension:

| Section | Says |
|---|---|
| §29.1 | Cross-agent tool sharing happens via Python imports, read-only, and those **remain `@tool` functions** — i.e. they legitimately exist |
| §29.2 | The universal seven is what every phase executor receives — and these four are not among them |

Read together, the four tools were simultaneously sanctioned and unaccounted
for. Neither section was wrong; the category was missing.

**The ruling.** They are a **third category** — read-only cross-agent tools —
distinct from both the universal seven (§29.2) and the per-phase computation
tools (§30).

**Current disposition: present, not bound.** Verified 2026-08-21 —
`grep -rn "from backend.knowledge.tools import\|bind_tools" backend/` returns
**nothing outside `tools.py` itself**. No coach receives any of them today.
They are reserved for cross-agent scenarios that do not exist until Agent
Resolve integration is real and Agent Flow is built.

**Two facts that shaped the ruling:**

- **`search_flow_vsm` is an explicit stub.** It returns *"Agent Flow VSM index
  not yet available."* unconditionally. Agent Flow has no indexes.
- **The three `search_resolve_*` tools reach real, populated Agent Resolve
  indexes** — `case_index_v3`, `knowledge_index_v2`, `evidence_index_v1`, via
  `similarity_search` only. Read-only is already true in the code, not merely
  intended.

**Why "present but unbound" rather than deletion.** Deleting them would discard
working read-paths into a production system for no gain — the code is not
costing anything while unbound, and rebuilding it later would repeat work
already done and verified. **Why not bind them now:** §30's selection-quality
ceiling is the binding constraint. Analyse is at 12 tools and Measure at 15
against a hard cap of 16; adding three would push Measure to 18. There is no
evidence yet that cross-agent retrieval improves DMAIC coaching, and no eval
dataset (§52) to produce that evidence.

**Three rules bind if they are ever bound to a coach**, recorded now so the
question is decided before the pressure to bind them arises:

1. **Binding any of them is an amendment (§56), not a routine change**, because
   it changes a phase's tool count against §30's cap.
2. **They must first comply with §27.** All four currently `except Exception`
   and return a prose string. That is the exact pattern CLAUDE.md §14 bans —
   retrieval failure must be distinguishable from no matches. It is tolerable
   only while they are unreachable.
3. **They must return citations the way the universal seven do** (§50). They
   currently return `str` with an inline `[Agent Resolve · index · case_id]`
   prefix rather than structured citation metadata, so nothing downstream can
   surface `source_file` / `page_number`.

**Never write to Agent Resolve indexes** (§23.5). Read-only is not a default
that can be relaxed.

---

## Part R — Contradiction detection redesigned (2026-08-22)

### R1 — `ContradictionDetectionMiddleware`: mechanical comparison removed, detection moved to the coach

**Status:** RATIFIED 2026-08-22
**Source:** Architectural review, 2026-08-22. **New decision — not a
previously-logged item.**
**Lands in:** reference §19.6, §20, §32, §37, §50 (and the same five in
`agent-improve/ARCHITECTURE.md`); `CLAUDE.md` §8.8, §9.4, §10.7;
`REFACTORING_PROCEDURE.md` steps 6.5 and 6.6. This entry is both the decision
record and the change-log entry required by §56.

**The question.** `ContradictionDetectionMiddleware` was specified as
deterministic dict comparison with no LLM call, implementing the mid-phase
contradiction check of §37. Analysis showed **the mechanism cannot do its
job** — and not in a way a bug fix reaches.

#### Three defects, each verified against the live documents

**(a) It reads the wrong drawer.** The middleware calls
`store.get(("projects", case_id, "artifacts"), state["current_phase"])`.
`gate_apply_node` is the **only** writer to that namespace and writes at step 7
of the nine-step gate (§33.2) — phase end. **Mid-phase the key does not exist**,
so the check reads nothing, every turn, by construction.

**(b) Field-name matching finds almost nothing.** Even repaired to read prior
phases, it matches on field *name*, and the five `{Phase}Output` schemas
deliberately use different names per phase. Measured across §40:

| | Count |
|---|---|
| Distinct content fields, all five phases (gate metadata excluded) | **41** |
| **Unique to exactly one phase** | **38** |
| Shared across more than one phase | **3** |

`baseline_metric` (Define) and `baseline_mean` (Measure) are the canonical
case: the same quantity, deliberately different names. **93% of fields cannot
cross-phase name-match at all.**

**(c) The three shared names are all prose.** `issues_and_barriers` (all five
phases), `secondary_metrics` (all five), `process_owner_buyin` (Analyse and
Improve). All free text, where `!=` fires on **any rewording** — false
positives, not detections.

**Why this is a redesign and not a fix.** With (a) repaired the reachable
surface is 3 prose fields out of 41, and on those the mechanism produces noise.
**Real contradictions arrive as natural-language prose referencing prior
committed values under different field names.** That requires semantic
understanding. Dict comparison cannot be repaired into it.

#### The ruling — detection moves to the coach, no new LLM call

| Component | Change |
|---|---|
| **SKILL.md** (all five, §32) | Each phase's coach prompt gains a contradiction-check instruction: compare the Belt's input against prior committed values **already in context** (injected by `BeforeModelStateInjection` at `before_agent`), and populate `contradiction_flag` on a material contradiction |
| **`CoachingResponse`** (§20) | Gains `contradiction_flag: Optional[dict] = None`, carrying `prior_field`, `approved_value`, `approved_phase`, `proposed_value`, `belt_input` |
| **`ContradictionDetectionMiddleware`** (§19.6) | **Mechanical comparison deleted entirely** — the `store.get`, the name matching, the `current_phase` read. Becomes: `after_agent` reads the flag; if set, raise `HITLInterrupt` with its contents |
| **§37** | Mechanics updated to semantic detection. **The cascade is unchanged** |

**No new LLM call anywhere.** The flag is produced by the coach's existing
`response_format=CoachingResponse` call — the same call that already returns
`message`, `fields_captured` and `citations`.

**The architecture is unchanged.** The middleware stays a component, stays at
position 6, stays on `after_agent`, stays ahead of `CoherenceMiddleware` and
`DMAICGraderMiddleware`. Only its internals change.

**False positives are controlled by instruction, not by threshold.** SKILL.md
directs the coach to flag only **material numeric or categorical
contradictions of committed values** — never prose rephrasing, and never
refinement of not-yet-committed current-phase values. **The no-tolerance rule
of §37 is untouched**: it governs what happens once a contradiction is
confirmed, not what counts as one.

**Structured output guarantees the flag's shape and presence, not the
correctness of the coach's judgment** — consistent with §20's existing point
that structured output gives shape, never truth.

#### What this honestly costs

**Detection is now best-effort semantic rather than illusory-deterministic.**
The old mechanism's danger was that it *looked* deterministic while detecting
nothing; the new one depends on coach judgment and can miss. **The
always-referenceable all-gate-fields tab — every field, open and closed — is
the documented human backstop for what the coach's judgment misses.** That is
an intentional second layer, not a gap.

#### Provenance — the first confirmed course-pattern fit-bug

**This middleware was adopted as a named pattern from the Edureka course
without verifying its mechanism fit our state model.** DMAIC state is
phase-partitioned, deliberately differently-named per phase, and written only
at gates. The pattern assumed a single flat namespace with stable field names
and continuous writes. **The name was right and the mechanism was never checked
against the thing it would run on.**

> **Flag this class of issue for review of other course-derived components.**
> A pattern adopted by name carries its source's assumptions about state shape,
> write timing and naming. **Those assumptions are invisible in the pattern's
> name and were not re-derived when it was adopted here.** This is the same
> failure family as the `ModelRetryMiddleware(retries=)` keyword and the
> retired-name `grep-absence` — something plausible, adopted once, never
> re-checked against reality.

#### Consequential

**`CoachingResponse` is added to §56's amendment-required list** in this same
change. Its omission was an oversight: it is the same class of load-bearing
schema as `SupervisorState` and `PhaseState`, both of which already gate field
additions. `contradiction_flag` itself lands inside this amendment; **future
additions hit the gate.**

---

### R2 — `route_after_phase` deleted: the supervisor does not route, it advances

**Status:** RATIFIED 2026-08-22
**Source:** Architectural review, 2026-08-22. **New decision.**
**Lands in:** reference §15 and the same section in
`agent-improve/ARCHITECTURE.md`; `CLAUDE.md` §9.1. This entry is both the
decision record and the change-log entry required by §56.

**The contradiction.** §15 showed **both** static phase edges
(`add_edge("define", "measure")` …) **and** a conditional routing function
`route_after_phase` returning `"next"` / `"escalate"` / `"retry"`. **A phase
transition is either static or conditional. It cannot be both.**

#### The evidence, all verified against the live documents

| Finding | Verified |
|---|---|
| §13's topology diagram annotates the exit `END (parent's static edge advances the phase)` | Verbatim |
| `add_conditional_edges` appears **nowhere** in the reference or the copy | Zero occurrences |
| `"next"` / `"escalate"` / `"retry"` appear **only** inside the function's own `return` statements | Nothing consumes them |
| `route_after_phase` reads `state["gate_attempts"]` — **not a `SupervisorState` field** (§5's seven are `messages`, `history`, `case_id`, `phase_index`, `current_phase`, `gate_passed`, `final_output`) | Would `KeyError` at runtime |
| Retry and escalation resolve **inside** the phase subgraph — §13's fail branch loops to the planner, §35 owns the counter, §38's escalation defers to the Belt and never returns upward | Confirmed in all three |

**The `KeyError` would fire only on the gate-failure path**, because the
`gate_passed` check short-circuits and returns `"next"` first. **The bug is
invisible until the first failed gate** — the worst possible discovery moment.

**`route_after_phase` was a fossil** of an abandoned design in which the
supervisor owned retry and escalation. That responsibility moved into the phase
subgraph; the function was never removed.

#### Why static is *safe*, which is the part worth keeping

**A subgraph reaches `END` only through `gate_apply`, and `gate_apply` runs
only after Belt approval** (§33). **Reaching `END` therefore *means* the gate
passed** — so there is no branch for the supervisor to make. The static edge is
not a simplification that ignores gate failure; it is correct *because* gate
failure never reaches the supervisor.

#### The ruling

**`route_after_phase` is DELETED**, not rewritten. The static edge chain
`START → define → measure → analyse → improve → control → END` is the complete
and correct supervisor wiring. §15's heading becomes **"Level 1 does not route
— it advances."** `gate_attempts` **stays on `PhaseState`** and is not added to
`SupervisorState`.

**Scope boundary:** this concerns **Level 1 (supervisor, phase-to-phase) only.**
All Level 2 routing — §13's field→field, →gate and retry→planner branching, and
the `Command`-inside-subgraphs rule — is correct and untouched.

---

#### The finding that matters more than the fossil: a rule with no enforcement hole-check

> **`route_after_phase` was already prohibited when it was written, by two
> rules this project already had.**
>
> - **Appendix D.2** bans *"`gate_attempts` in route scope"*
> - **`CLAUDE.md` §14** carries the identical no-go
>
> **`route_after_phase` is route scope reading `gate_attempts`.** The reference
> contained a code block its own banned-pattern list forbids, and shipped that
> way through a full verification pass.
>
> **The rule was correct. Nothing enforced it against the document's own
> prose.** The drift registry checks *code* — and `agent-improve/**/*.md` is
> explicitly path-excluded from patterns 2–8 (§55), for the good reason that
> governance documents must be able to name a construct in order to prohibit
> it. **That exclusion is right, and it leaves a hole: a banned pattern
> presented as a design example inside a governance document is unreachable by
> every automated check we have.**

**This is the same class as the grep blind spot** (§55) and the retired-name
`grep-absence`: **a correct rule paired with a check that structurally cannot
see the thing it governs.** Three instances now, each found by hand:

| Instance | The rule | The hole |
|---|---|---|
| Retired tool names | "never reference the retired names" | The named strings never existed, so the check matched a fiction |
| Rename sweep | "zero stale references" | The tool filters by `.gitignore` and could not see part of the tree |
| **`route_after_phase`** | "`gate_attempts` never in route scope" | The registry excludes `.md`, so a banned pattern in a *design example* is unchecked |

**Recorded as a pattern, not three anecdotes.** When a rule is written, ask
what would catch a violation of it **in prose**, not only in code — and if the
answer is "nothing", say so in the rule rather than assuming coverage. No
automated fix is proposed here: extending the registry to governance prose
would re-create the problem §55 documents. **The mitigation is that this class
is now named and searched for deliberately during review.**

> ### A fourth candidate was checked and cleared — 2026-08-24
>
> **The list stays at three.** G-43 was raised on 2026-08-24 as an apparent
> fourth instance: `REFACTORING_AGENT_IMPROVE.md` §1432 quotes a LangGraph rule
> — *"only the parent graph should have a checkpointer"* — without its companion
> clause, *pass `checkpointer=True` to the subgraph you'd like to persist*. It
> had the exact shape of §R1 and §R2: guidance adopted as a fragment.
>
> **On inspection the omission was correct.** That clause governs
> **independently-persisted** subgraphs, which this architecture deliberately
> does not use. Dropping it was the right call, not a lost assumption. Full
> record: §U1.
>
> **Recorded because a true negative is evidence too.** The pattern-check fired
> on the right signal and cleared on the right reasoning; **had it been logged
> as a fourth instance without the second half, the pattern list would now
> overstate itself** — and a register of failure modes that inflates is exactly
> as untrustworthy as one that misses. **Firing is not the same as finding.**

---

## Part S — The specification layer (2026-08-23)

### S1 — `AGENTIC_ARCHITECTURE_REFERENCE.md` gains a specification Part

**Status:** RATIFIED 2026-08-23
**Source:** Spec-layer decision, 2026-08-23, governed by
`agent-improve/docs/SPEC_LAYER_GUIDE.md`. **New decision — not a
previously-logged item.**
**Lands in:** reference **Part XII (§57–§66)** — new; **§55.1** — new; **§56**
amendment list; **§2** canonical-ownership table; **Appendix C** Tier 1
compliance block; and definitions relocated out of §5, §6, §7, §9, §12, §14,
§15, §16, §17, §18, §19, §20, §24, §25, §26, §29, §33, §35, §40, §41, §45, §46
and §48. Applied identically to `agent-improve/ARCHITECTURE.md`. This entry is
both the decision record and the change-log entry required by §56.

**The question.** The reference is an *architecture* — it explains shape and
reasoning. It is not a *specification*: it does not define classes and
functions to the level where code could be rebuilt from it without inventing
the missing pieces. Two seams traced during the 2026-08-22 wiring review — the
contradiction middleware (§R1) and `route_after_phase` (§R2) — proved the gap
is real and produces exactly the endless-debugging failure this project exists
to avoid.

**The ruling.** Adopt the missing middle layer of Spec-Driven Development, as a
new Part of the same document. Separate spec files re-create the drift the SSOT
non-overlapping rule eliminated.

| Decision | Ruling |
|---|---|
| Where | **Part XII, after Part XI, before the Appendices.** Architecture (why) precedes spec (how), per volatility separation |
| Numbering | **§1–§56 do not renumber.** ~48 `CLAUDE.md` citations plus DECISIONS, the procedure, the SKILL.md files and code comments depend on them |
| Entry identity | Stable `S-C##` / `S-F##` IDs, independent of section numbers |
| Entry template | SIPOC + EARS behaviors + selective AI-ACT flag, calibrated against two approved samples transcribed verbatim at §57.2 and §57.3 |
| Index schemas | **Stay in §23.** They are data-store schemas, not code signatures; §23.5 is a ratified procedure requiring changes to land there first |
| Middleware | **Class entries only**, hook behaviour expressed as EARS. A second entry per hook would duplicate the SIPOC cells |
| The 20 computation tools | **One entry**, not twenty. Twenty entries whose every cell reads `SPEC-GAP` hide the single real gap |
| Governance | **§55.1**, a subsection of Anti-drift — five rules, each stated with what would catch a violation |

**73 entries: 37 classes, 36 functions and nodes.** Five carry an AI-ACT flag;
twelve carry `AI-ACT-REVIEW: uncertain`.

**42 gaps marked, none filled.** That was the pass's binding constraint. G-41
was closed by the founder supplying `agent-improve/docs/SPEC_SAMPLES.md`;
**41 remain open** and are the review agenda. §66 is the register.

**§66.7 records ten findings that are inconsistencies rather than
absences**, and §66.8 records the cross-check run that produced several of them — including that the drift registry's path exclusions still name
`agent-improve/**`, so **the reference has been unguarded-as-documentation and
guarded-as-code since it moved to the monorepo root in v1.2** (F-01), and that
§33 step 9 still carries the "supervisor reads `gate_passed`" wording that
`CLAUDE.md` v2.2.20 deliberately tightened (F-02). **None was fixed in this
pass**; each needs its own §56-routed decision.

**No `CLAUDE.md` amendment and no `deprecated_patterns.yaml` change.** No rule
there was touched and no reference section renumbered, so neither trigger in
§56 step 5 fires.

#### The finding worth carrying forward

**The Supplier/Customer cross-check works, and its first run proves both
halves of that.** It independently re-detected the Level 2 routing gap (G-01)
and the new mapper-execution-site gap (G-42) from the wiring alone, without
being told where to look — which is the verification surface the layer was
adopted for.

**It also produced 32 structural non-closures that mean nothing.** Nested
sub-components, return paths and build-time relations all trip a rule written
as though the call graph were flat and one-directional. **A check that reports
36 failures of which 4 matter will be ignored by its third run** — which is
the §55 failure mode, arriving from the opposite direction to the three
already recorded. §55.1 rule 3 must be narrowed before it is automated. Full
run and classification: reference §66.8.

### S2 — Compliance and Risk becomes a Part of the reference

**Status:** RATIFIED as scaffold 2026-08-23. **The classification question is
UNRESOLVED and requires qualified legal advice.**
**Lands in:** reference **Part XIII (§67–§68)** — new; Appendix C Tier 1
compliance block. Applied identically to `agent-improve/ARCHITECTURE.md`.

**The question.** The Digital Omnibus is enacted law — Regulation (EU)
2026/1744, in force 27 July 2026 — and the high-risk deadlines are now fixed
and unconditional: **2 December 2027** for standalone Annex III systems,
which includes **employment**.

**Agent Improve may be Annex III high-risk via the employment category**, and
whether it crosses the line depends on **deployment, not on the code**: gate
outputs feeding a formal evaluation is likely high-risk; a private learning
aid with no institutional consequence is likely not.

**The ruling.** **Do not answer the classification question here** — it is a
legal determination. **Scaffold the compliance layer now anyway**, so that if
the answer is high-risk no retrofit is needed. The eight core provider
obligations (Art. 9–15, 43) map to mechanisms that already exist; §67.3 names
each one.

**The register is DORA-structured** — Regulation (EU) 2022/2554 — because DORA
applies directly to financial customers who must track a third-party AI vendor
as ICT risk, **and because the DORA register shape is the universal
risk-register shape every industry uses.** One table is therefore
cross-industry by construction: legible to a bank as DORA, to a factory as a
risk register. It is the artifact handed to a prospect, which is why the
`Customer Negotiation` column is deliberately open.

**Five rows, one per flagged function.** The flag is canonical and the register
is derived; when they disagree the flag wins and the row is regenerated
(§55.1 rule 2). The twelve `AI-ACT-REVIEW: uncertain` entries are held in a
separate table (§68.3) rather than given rows, because putting unresolved
classifications in the register would break the bidirectional check in both
directions.

**One compliance risk was already in the document and is carried in, not newly
asserted:** §46.1's single-region fallback chain, which DORA's ICT resilience
obligations make **non-compliant for any regulated-entity deployment**. It is
`R-INFRA-01`, it has no AI-ACT flag behind it, and it is marked as such so the
flag-is-canonical rule is not read as broken by its presence.

**Compliance-source discipline binds on every claim in this Part:** cite a
current-dated source, or mark it "unverified — requires legal validation."
Nothing in Part XIII is legal advice.

---

## Part T — `PhaseState` identity fields (2026-08-24)

### T1 — G-03 and G-42 resolved: case and phase identity are copied down at the boundary

**Status:** RATIFIED 2026-08-24. **§56 amendment** — `PhaseState` field-ceiling
breach.
**Source:** SPEC-GAP resolution session, 2026-08-24, run under the Standing
Reasoning Protocol (`SPEC_LAYER_GUIDE.md` §6.1). **New decision.**
**Lands in:** reference §6, §56, and spec entries S-C02, S-F02, S-F07, S-F09,
S-F10, S-F11, S-F12, S-F29, S-F32, plus §66; `agent-improve/ARCHITECTURE.md`
identically; `CLAUDE.md` §0.4, §0.15, §10.1, §14; `REFACTORING_PROCEDURE.md`
steps 3.1 and 3.3. This entry is both the decision record and the change-log
entry required by §56.

**The question.** `PhaseState` declared no case identity and no phase
identifier, and three specified functions read one or both off it:
`phase_error_recovery` read `state["case_id"]` and `state["phase"]` (§45);
`analyse_executor_node` read `state["current_phase"]` (§26); and
`gate_apply_node`'s Store write needed `case_id` (§33.2). **The same defect
class as `route_after_phase`** (§R2) — specified code reading state a schema
does not declare.

#### The ruling — A2

**Phase-internal functions read case identity and phase from their own
`PhaseState`, injected by the input mapper at the boundary.** A single source of
truth for inside-subgraph code.

| Field | Type | Writer |
|---|---|---|
| `case_id` | `str` | **Input mapper only**, copied from `SupervisorState.case_id` at phase entry |
| `current_phase` | `str` | **Input mapper only**, copied from `SupervisorState.current_phase` at phase entry |

**`PhaseState` goes 17 → 19: two identity, three plumbing, fourteen content.**

**Chosen over reading `case_id` from config and phase from a build-time
constant, and the reason is the defect itself: mixing sources is what made G-03
latent.** Three functions read three different notional sources, none declared,
and nothing could see that they disagreed.

**The copy-down invariant.** Both fields are **copied down** at phase entry,
are **read-only within the subgraph**, and are **never written back up**.
`SupervisorState.current_phase` remains authoritative and keeps its single
writer, the output mapper. **A boundary-time copy is not a second writer** — the
parent field and the child field are two fields on two schemas, and the child's
is derived from the parent's exactly once, at entry.

**Its check, per §55.1 rule 5:** grep every node's return dict for `case_id` or
`current_phase` as a key. **Any hit is a violation.** Node returns are dict
literals (§14), so the write sites are greppable.

#### G-42 is resolved by the same fix

**The boundary mappers had no stated execution site.** §9 made them plain
functions; §13 permits exactly five nodes and none is a mapper; §12 embeds each
subgraph as a parent node.

**They run inside the parent's uniquely-named node function for that phase** —
which calls the input mapper, invokes the compiled subgraph, and calls the
output mapper on the way back. **This adds no sixth node**: §13's rule governs
the subgraph, and the mapper runs one level up.

**Verified against current documentation, 2026-08-24** (Standing Reasoning
Protocol step 3): where a parent graph and a subgraph have different state
schemas — which `SupervisorState` and `PhaseState` do, sharing no keys — the
documented LangGraph pattern is to invoke the subgraph **inside a node
function** that transforms parent state to subgraph state before invoking and
transforms the result back.

> **The stability condition binds, and is now written into the spec.**
> Namespaces for subgraphs invoked inside node functions are assigned **by call
> order**, and reordering calls can mix up which subgraph loads which state. The
> documented remedy is a uniquely-named parent node per subgraph — satisfied by
> the five phase nodes, which must now stay uniquely named for a stated reason
> rather than by habit. **The escalation edge is the one place order is not
> fixed** (§12, §38), and that is one more thing G-34 must settle.

#### The trigger correction — the part that outlives the two fields

**§56's `PhaseState` trigger read "a fifteenth `PhaseState` content field."**
That is an enforcement hole: a field can be added, declared non-content, and
**skip the amendment gate on a category label the adder chooses.**

**The two fields added here would themselves have slipped through it** — they
are identity fields, not content fields, so on the old wording this amendment
was not required at all.

**Corrected in the same commit.** §56 now fires on **any new `PhaseState`
field, whatever category it is placed in.** A gate whose scope is set by a label
the adder picks is not a gate.

#### Also in this amendment

- **`state["phase"]` → `state["current_phase"]`** at §45's handler, and
  `delete_or_flag_stale_in_case_index`'s parameter renamed to match the field it
  is passed (S-F32). The old name matched nothing.
- **No lag window.** `CLAUDE.md` §10.1 carries the schema quoted into every
  implementation prompt; it moves in this commit, not after it (§0.9).

#### The finding worth carrying forward

**This is the first gap resolved under the Standing Reasoning Protocol, and
step 3 is what earned its place.** The trusted-source check confirmed the mapper
pattern — and while confirming it, surfaced **G-43**, a defect larger than the
one being fixed: §16 compiles phase subgraphs with no checkpointer argument,
which is LangGraph's per-invocation mode, in which *each call starts fresh*.

**Its provenance is a third partial quotation.**
`REFACTORING_AGENT_IMPROVE.md` §1432 quotes the source rule — *"When using
subgraphs, only the parent graph should have a checkpointer, to avoid duplicate
storage and state persistence issues"* — and the companion clause, *pass
`checkpointer=True` to the subgraph you'd like to persist*, **was never carried
across.** §R1 was a pattern adopted by name; §R2 was a rule with no check that
could see it; **this is guidance adopted as a fragment, its assumptions
invisible in what was kept.**

**G-43 is registered at §66.1 as highest severity and marked INFERENCE —
the API behaviour is confirmed, that AgentLean is affected is not.** It is not
resolved here, it gets its own session, and it likely precedes G-04: if
`PhaseState` is re-seeded every turn, G-04's accumulation question is moot until
G-43 is settled.


---

## Part U — G-43 resolved as a false alarm (2026-08-24)

### U1 — Subgraph persistence: design confirmed correct, no new defect

**Status:** RESOLVED 2026-08-24. **Gap-register resolution routed through §56;
no architecture change.**
**Source:** G-43, raised 2026-08-24 during the G-03/G-42 resolution session
(§T1) by the Standing Reasoning Protocol's trusted-source check. Closed the
same day by tracing every invoke site in the reference.
**Lands in:** reference §66 register and the head version note; S-F02's inline
marker removed; `agent-improve/ARCHITECTURE.md` identically. **No `CLAUDE.md`
change and no procedure change** — the remaining work is an existing step.

**The alarm.** §16 compiles phase subgraphs with no checkpointer argument. In
LangGraph that is the **per-invocation** mode, in which *each call starts
fresh*; `checkpointer=True` is the **per-thread** mode, in which state
accumulates on the same thread. The inference was that `PhaseState` might be
re-seeded empty every Belt turn, so `artifacts`, `gate_attempts`, `turn_count`
and `validator_feedback` could not accumulate within a phase. It was registered
at highest severity **and explicitly marked INFERENCE, needing confirmation.**

#### The four findings that closed it

**1. No standalone subgraph invocation exists anywhere in this document.**
Every `.invoke` / `.ainvoke` is one of two things: the **single parent-graph
entry point** — `graph.ainvoke` with `thread_id` in config (§16) — or an **LLM
call**: `phase_planner.invoke`, `executor.ainvoke`, `planner.invoke`,
`synthesis_llm.invoke`. All four are models, not graphs. **The concern requires
a phase subgraph invoked standalone, outside the parent. That does not occur.**

**2. Checkpointer placement is correct, and verified.** The parent compiles
with `checkpointer=checkpointer`; subgraphs compile with no arguments and
inherit persistence through an auto-managed `checkpoint_ns` (§16). **This is
the prescribed LangGraph pattern**, not a deviation from it.

**3. The dropped companion clause should have been dropped.** The clause whose
absence raised the alarm — *pass `checkpointer=True` to the subgraph you'd like
to persist* — governs **independently-persisted subgraphs**, which Agent
Improve deliberately does not use. **Omitting it is correct, not a defect**, and
the provenance concern therefore does not apply: nothing was lost, because the
omitted clause should be omitted.

**4. What remains is already known and already scheduled.** The checkpointer is
**⚠ WIRED but INERT** — `thread_id` is not yet passed at `ainvoke` in the
current *code* (§53.1, Appendix E). That is the existing
`thread_id`-through-`ainvoke` step (§16, §47). **G-43 folds entirely into it and
adds no new work.**

#### The resolution

**G-43 is downgraded from HIGHEST SEVERITY to RESOLVED. The design is correct.**
The memory architecture works as designed — the checkpointer stores full state
in Blob and reloads it on return via `thread_id` — **once the already-planned
`thread_id`-through-`ainvoke` wiring lands.** No architectural change follows,
which is why this is a register resolution rather than an amendment to any
section.

#### The finding worth carrying forward

**The pattern-check fired correctly and cleared correctly, and both halves
matter.** G-43 had the exact shape of §R1 and §R2 — guidance adopted as a
fragment — and looking for that shape is now deliberate review practice. It
found a real candidate. **It then cleared on inspection, because the omitted
clause governed a case this architecture does not have.**

**Recorded as a true negative so the §R-series list is not inflated with a
false fourth instance.** A register of failure modes that overstates itself is
as untrustworthy as one that misses: if three instances become four on a
candidate that did not hold, the next reader weights the pattern wrongly and the
list stops being evidence. **Firing is not finding.** The §R2 note now carries
this explicitly.

**What G-43 verified, and what it did not.** It verified two cases: that no
subgraph is invoked standalone outside the parent, and that the bare-node
compile pattern's persistence is correct. **The wrapper-internal
`subgraph.ainvoke` prescribed by G-42's resolution at S-F10 is a distinct third
case, is not covered by finding 2, and is tracked as G-44** — open, at HIGH
severity, and requiring its own trusted-source check before design.

**One thing this session did get right, and it is the reason the cost was
low:** G-43 was registered **marked INFERENCE, needs confirmation**, not as
established fact, and it was deferred rather than acted on. **The cost of a
false alarm raised that way is one tracing session; the cost of one raised as
fact would have been an unnecessary architecture change** — a subgraph
`checkpointer=True` that the design does not need and that §16 correctly
forbids.
