<!--
Document: agent-improve/DECISIONS.md
Version: 1.4 — 2026-08-19
Purpose: Consolidated decision register. Single navigable reference for every
         ratified architectural decision, coaching rule, and deferred/rejected
         item. Synthesized from STATE_DESIGN_RESOLUTION.md (26 findings),
         SKILL_REVIEW_NOTES.md (17 notes), status-79-84-2026-08-10.md, and
         CONTINUITY.md. Replaces the scattered five-file review set as the
         primary cross-session reference. (archived to docs/_archive/; canonical: DECISIONS.md)

Source documents (stay in repo, not here):
  agent-improve/docs/_archive/STATE_DESIGN_RESOLUTION.md   — original 26 findings
  agent-improve/reviews/REVIEW_DECISIONS.md           — full EDUCATIONAL.md review log
  agent-improve/SKILL_REVIEW_NOTES.md                 — 17 SKILL.md review notes
  agent-improve/docs/_archive/RESTRUCTURE_PLAN.md           — REFACTORING reorder plan
  agent-improve/docs/_archive/status-79-84-2026-08-10.md   — §79–§84 landing audit (archived to docs/_archive/; canonical: DECISIONS.md)

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
--> (archived to docs/_archive/; canonical: no in-doc equivalent; the file is the artefact)

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
**Source:** STATE_DESIGN_RESOLUTION.md Findings 1–3, 7 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Findings 4–6, 8–12; §71 compliance audit (2026-08-11) (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Finding 13 (archived to docs/_archive/; canonical: DECISIONS.md)

`project_id` is retired. The identifier is `case_id` everywhere: state
field, store namespace, `thread_id`, blob path, log field, index field,
prose. Both indexes (`improve_evidence_index`, `improve_case_index`) and
the blob path (`cases/case_{id}.json`) always said `case_id` — the rename
resolves the doc/code split.

---

### A4 — Canonical name for captured fields: `artifacts`

**Status:** ADOPTED — landed in CLAUDE.md §10.5  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 14 (archived to docs/_archive/; canonical: DECISIONS.md)

Three names existed for one concept: `artifacts` (code), `captured_fields`
(prose), `phase_inputs` (v1 field). `artifacts` wins everywhere.

`captured_fields` must not appear in prose. `phase_inputs` must not be
added to v2 code.

---

### A5 — All captured fields are `str`; computation results in `artifacts["computation_results"]`

**Status:** ADOPTED — landed in CLAUDE.md §10.6  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 15 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Finding 15 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Findings 5, 9 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Finding 11 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Findings 16–17 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Finding 18 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Findings 19–20; Mod A (2026-08-12); Mod B (2026-08-12); B3.1 amendment (2026-08-19) (archived to docs/_archive/; canonical: DECISIONS.md)

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
full record in `BIBLE_VERIFICATION_LOG.md` C-1. (archived to docs/_archive/; canonical: CLAUDE.md §0.10)

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
**Source:** STATE_DESIGN_RESOLUTION.md Finding 21 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Finding 22 (archived to docs/_archive/; canonical: DECISIONS.md)

`record_field` is retired and may not be reintroduced. Field capture
happens through `CoachingResponse.fields_captured` on the executor — the
coach emits `fields_captured` as structured output on every turn, making
capture part of every response by construction rather than an optional tool
call.

---

### B6 — Universal tool count: seven (not eight)

**Status:** ADOPTED — landed in CLAUDE.md §5.1  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 23 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Finding 23 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Finding 24 (eBook extraction, v2.2.11) (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Finding 24 (archived to docs/_archive/; canonical: DECISIONS.md)

`issues_and_barriers` = Belt-stated real-world project blockers (Tier 1).  
`acknowledged_gaps` = system-generated record of skipped Tier 2 fields.

Merging them is a violation.

---

### C3 — eBook additions to schema fields (v2.2.11)

**Status:** ADOPTED — landed in CLAUDE.md §0.6  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 24 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Finding 24 (archived to docs/_archive/; canonical: DECISIONS.md)

| Item | Before | Now |
|---|---|---|
| X-Y matrix | BB-only | `xy_matrix_summary`, Tier 1, all Belts — produces `vital_few_xs` Analyse cannot start without |
| Statistical problem statement | BB-only | Tier 2, all Belts, in Analyse — not Define |
| DOE | BB-only | Still BB-only — the one remaining belt-gated item |
| Stability | Advisory | `stability_assessment`, Tier 1, all Belts — unstable process makes Cpk meaningless |

---

### C5 — Process map fields promoted to Tier 1 schema (v2.2.12)

**Status:** ADOPTED — landed in CLAUDE.md §0.7, §10.8  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 26 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** STATE_DESIGN_RESOLUTION.md Finding 26 (archived to docs/_archive/; canonical: DECISIONS.md)

FMEA has no field in any schema. It is heavy manufacturing methodology not
appropriate as a universal gate requirement in service/transactional DMAIC.
If a Black Belt performs one, it lives in `uploads`. The schema does not
track it, the grader does not ask for it, and no gate blocks on it.

`fmea_summary`, `updated_fmea`, FMEA sub-keys — all banned.

---

## Part D — Coaching & Skills

### D1 — Seven-step computation tool coaching pattern

**Status:** ADOPTED — landed in CLAUDE.md §8.2 (`COACHING_QUALITY_RUBRIC`)  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 25; SKILL_REVIEW_NOTES.md Notes 1–14 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** SKILL_REVIEW_NOTES.md Note 15 (CRITICAL) (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** SKILL_REVIEW_NOTES.md Note 16 (CRITICAL) (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** SKILL_REVIEW_NOTES.md Note 17 (CRITICAL) (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** SKILL_REVIEW_NOTES.md (general note across all 17); CLAUDE.md v2.2.14 (archived to docs/_archive/; canonical: DECISIONS.md)

The coach must not provide external URLs from training data. When
referencing methodology, retrieve via `rag_lookup_methodology` and weave
the content into natural coaching voice.

---

### D6 — SKILL.md allowed-tools must match §5.2 tool subsets

**Status:** ADOPTED — landed in CLAUDE.md §8.3  
**Source:** SKILL_REVIEW_NOTES.md (verified across Notes 1–14) (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** status-79-84-2026-08-10.md; REFACTORING §79 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** status-79-84-2026-08-10.md; REFACTORING §80 (archived to docs/_archive/; canonical: DECISIONS.md)

The eight-middleware stack is built on the six `AgentMiddleware` hooks:
`before_agent`, `after_agent`, `before_model`, `after_model`,
`wrap_model_call`, `wrap_tool_call`. "Prefer built-in middleware wherever
it exists."

---

### F3 — §81: `content_blocks`, not string parsing

**Status:** LANDED — CLAUDE.md §4.5  
**Source:** status-79-84-2026-08-10.md; REFACTORING §81 (archived to docs/_archive/; canonical: DECISIONS.md)

Read `response.content_blocks`. String-indexing or substring-parsing the
raw content field is a violation.

**Live code gap:** `upload/agent.py:107` still parses `response.content`
directly (§4.5 violation). No §15 step covers it. Code drift, not a
constitution gap. Tracked in CONTINUITY.md §4.

---

### F4 — §82: `ProviderStrategy` / `response_format=` scoped by call type

**Status:** LANDED — CLAUDE.md §4.3, §4.6  
**Source:** status-79-84-2026-08-10.md; REFACTORING §82 (archived to docs/_archive/; canonical: DECISIONS.md)

The contradiction in v2.1 (§4.3 mandated `with_structured_output`
everywhere while the hook cited a §4.6 that didn't exist) is resolved.
Now: `response_format=` for agents built with `create_agent`;
`with_structured_output` for plain model calls inside tools/middleware/validators.
See CLAUDE.md §4.6 for the full mapping.

---

### F5 — §83: SKILL.md spec

**Status:** LANDED — ARCHITECTURE.md §8.4, CLAUDE.md §8.3  
**Source:** status-79-84-2026-08-10.md; REFACTORING §83 (archived to docs/_archive/; canonical: DECISIONS.md)

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
**Source:** status-79-84-2026-08-10.md; REFACTORING §79 (archived to docs/_archive/; canonical: DECISIONS.md)

`DeltaChannel` is not adopted — beta API. Deferred until sessions exceed
~200 turns. Not a violation of §79; the decision to not adopt a beta API
is the §79-compliant choice.

---

### G2 — deepagents: REJECTED (pre-1.0)

**Status:** REJECTED while pre-1.0 — landed in CLAUDE.md §4.4, §8.6  
**Source:** status-79-84-2026-08-10.md; REFACTORING §84 (archived to docs/_archive/; canonical: DECISIONS.md)

`create_deep_agent`, `RubricMiddleware`, `SkillsMiddleware` from deepagents
are BANNED while the package remains pre-1.0. Our equivalents:
`DMAICGraderMiddleware` (custom, replaces `RubricMiddleware`),
`DMAICSkillsMiddleware` (custom, replaces `SkillsMiddleware`).

Revisit at deepagents 1.0. If migrating: migrate all three custom
middlewares together or not at all.

---

### G3 — `HumanInTheLoopMiddleware`: REJECTED (two confirmed bugs)

**Status:** REJECTED — landed in CLAUDE.md §8.6  
**Source:** STATE_DESIGN_RESOLUTION.md Finding 16; REFACTORING §53 (archived to docs/_archive/; canonical: DECISIONS.md)

Two confirmed bugs in our exact use case:
1. Edited tool-call args can be silently re-overwritten by the agent re-attempting the original call
2. Edit/reject are broken in subgraph contexts — only approve is reliable

Both would silently discard a Belt's correction. Use graph-level
`interrupt()` + `Command(resume=...)` instead.

---

### G4 — `LLMToolSelectorMiddleware`: REJECTED

**Status:** REJECTED — landed in CLAUDE.md §8.6  
**Source:** STATE_DESIGN_RESOLUTION.md (archived to docs/_archive/; canonical: DECISIONS.md)

Per-phase binding (§5.2) keeps every coach at 8–15 tools. Adding a
selector LLM spends a model call solving a problem already solved
structurally.

---

### G5 — `create_react_agent` / `langgraph.prebuilt`: BANNED

**Status:** REJECTED — landed in CLAUDE.md §4.4  
**Source:** STATE_DESIGN_RESOLUTION.md (archived to docs/_archive/; canonical: DECISIONS.md)

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

**Status:** PENDING — plan in `docs/_archive/RESTRUCTURE_PLAN.md`  
**Source:** docs/_archive/RESTRUCTURE_PLAN.md (archived to docs/_archive/; canonical: DECISIONS.md §G11)

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
| D09 diagram added: constraint validation + retry-with-accumulated-feedback | **`docs/_archive/ARCHITECTURE_DIAGRAMS.html`** — archived 2026-09-01; the diagram exists only there, and `agent-improve/diagrams/` predates it and does not contain D09 | docs | v1.2 — 2026-08-12 (archived to docs/_archive/; canonical: no in-doc equivalent; the file is the artefact) |
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
2" ruling stands; only the parameter name changed.* (archived to docs/_archive/; canonical: CLAUDE.md §0.10)

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
`agent-improve/docs/_archive/SPEC_LAYER_GUIDE.md`. **New decision — not a
previously-logged item.**
**Lands in:** reference **Part XII (§57–§66)** — new; **§55.1** — new; **§56**
amendment list; **§2** canonical-ownership table; **Appendix C** Tier 1
compliance block; and definitions relocated out of §5, §6, §7, §9, §12, §14,
§15, §16, §17, §18, §19, §20, §24, §25, §26, §29, §33, §35, §40, §41, §45, §46
and §48. Applied identically to `agent-improve/ARCHITECTURE.md`. This entry is
both the decision record and the change-log entry required by §56. (archived to docs/_archive/; canonical: ARCHITECTURE.md §57)

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
was closed by the founder supplying `agent-improve/docs/_archive/SPEC_SAMPLES.md`;
**41 remain open** and are the review agenda. §66 is the register. (archived to docs/_archive/; canonical: ARCHITECTURE.md §57.1)

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
entry required by §56. (archived to docs/_archive/; canonical: ARCHITECTURE.md §57)

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
case, is not covered by finding 2, and is tracked as G-44** — resolved
2026-08-24 (see `ARCHITECTURE.md` §16); the trusted-source check it required was
completed that day.

**One thing this session did get right, and it is the reason the cost was
low:** G-43 was registered **marked INFERENCE, needs confirmation**, not as
established fact, and it was deferred rather than acted on. **The cost of a
false alarm raised that way is one tracing session; the cost of one raised as
fact would have been an unnecessary architecture change** — a subgraph
`checkpointer=True` that the design does not need and that §16 correctly
forbids.

---

## Part V — Knowledge-index corpus rebuild (2026-08-25)

### V1 — `improve_knowledge_index` narrowed to one methodology voice

**Status:** RATIFIED 2026-08-24, code landed 2026-08-25. **Corpus and
extraction change; NO schema change, so not routed through §56** — §56's index
trigger is a *schema* change (§23.5). The seven fields, their types, the 3072
dimensions, the HNSW profile and the `general` sentinel are all untouched.
**Source:** founder ruling.
**Lands in:** `scripts/ingest_knowledge.py` (rewritten),
`scripts/create_indexes.py` (knowledge-index definition corrected),
`scripts/diff_knowledge_index.py` (new), `docs/_archive/EXCEL_TOOL_INVENTORY.md` (new).
**Reference §23.1's stated figures go stale on swap** and are re-synced then,
not now — the swap has not run. (archived to docs/_archive/; canonical: ARCHITECTURE.md §30)

#### The decision

**The index carries the BB eBook and nothing else.** Two sources removed:

| Removed | Live docs | Why |
|---|---|---|
| `problem_solving_8D` | 169 | **Cross-framework contamination.** 8D is Agent Resolve's methodology, not DMAIC. Its D1/D2 content was retrievable during DMAIC *Define* coaching, teaching a different method under a similar-sounding name |
| `LSS_tools_suite` | 75 | Thin descriptions plus example data, redundant against the eBook's richer coverage of the same tools; the example-number rows were retrieval attractors |

**The reasoning is about tiers, and it is worth stating precisely.** Source
conflict is governed by the MEMORY HIERARCHY in every coach prompt (CLAUDE.md
§6.3), which arbitrates *between* tiers — methodology outranks captured fields
outranks case history outranks conversation. **It cannot arbitrate between two
competing tier-1 methodology voices, because they occupy the same tier.** One
source removes the conflict rather than ranking it.

**`EXCEL_SHEET_TOOL_MAP` was preserved, not deleted** — moved to
`docs/_archive/EXCEL_TOOL_INVENTORY.md` as the build-inventory for the §30 computation
layer. The tool-to-phase mapping is a spec, not a corpus. That file also
records two observations from comparing it against §30's twenty tools:
`Normality Test` has no computation-tool counterpart, and the workbook files
DPO/Z under Control where §30 correctly files it under Measure. **Neither was
actioned**; both are noted so the §30 build meets them deliberately. (archived to docs/_archive/; canonical: ARCHITECTURE.md §30)

#### Extraction: the ratified rationale was wrong, the ratified choice was right

The ratification called for replacing `pypdf` with `pdfplumber` or PyMuPDF
because *"`.extract_text()` produces character garble — bullets to `%` and the
replacement character, degrading embeddings"*. **Measured across all 700 pages
under both libraries, that rationale does not survive:**

| Artifact | pypdf | pdfplumber |
|---|---|---|
| `(cid:N)` tokens | 0 | **1,477 on 51% of pages** |
| N-struck words (`BBllaacckk`) | 1 | **523 tokens on ~27 pages** |
| `%`-as-space | 181 on 5 pages | 129 on 3 pages |
| U+FFFD replacement char | **0** | **0** |
| running footer | 1,396 on 698 pages | 1,396 on 698 pages |

**Three corrections to the premise:**

1. **The replacement-character garble does not exist.** Zero occurrences under
   either library. It was never an extractor artifact.
2. **`%`-as-space is in the PDF, not the extractor.** The book's fonts
   substitute a visible glyph for the space character on a few pages — `%`,
   `$`, `&`, `)` and `"` were all observed. Both libraries reproduce it
   faithfully. **A library swap cannot fix it.**
3. **pdfplumber is strictly *worse* on garble.** It is the library that
   introduces the `(cid:N)` tokens and the character striking.

**pdfplumber is still correct, for a reason the census cannot measure:
reading order.** The book is a slide deck; on two-column pages pypdf
interleaves the columns into semantic nonsense while pdfplumber keeps them
apart. **A scrambled chunk cannot be repaired downstream. Every artifact
pdfplumber adds can be**, and `normalise_page` does it:

| Artifact | raw | normalised |
|---|---|---|
| `(cid:N)` | 1,477 | **0** |
| space-glyph | 405 | **0** |
| footer | 698 | **0** |
| N-struck tokens | 523 | **6** |

**So the ratified decision stands and its stated reason is replaced.** The
pipeline is pdfplumber for layout plus a normaliser for glyphs, and neither
half is optional. `--audit` re-runs the census on demand, so the repair rules
can be re-derived from evidence if the PDF is ever re-issued rather than
inherited on faith.

**The striking is 2x, 3x AND 4x** — 428 tokens doubled, 29 tripled, 66
quadrupled. A rule written for doubling alone leaves the other two mangled and,
worse, halves a 4x token into a 2x one that then *looks* repaired. The repair
derives the factor from run lengths instead, per token, and only on pages
already showing three or more struck tokens. **A single-run token returns
factor 1**, which is what keeps `XXXX` and rows of underscores untouched;
verified zero dictionary-word collisions across the 517 tokens it alters.

#### The finding that changes how the swap must be done

**Not one of the live index's 1,369 document ids is reproduced by
`make_doc_id()`.** The pipeline that populated it is not in the repository and
used a different key formula.

**Azure Search upserts on key.** So ingesting the rebuilt corpus into the live
index would not replace it — it would **add 1,184 documents beside the existing
1,369, and every document from the two removed sources would survive**. The
contamination this decision exists to remove would still be there, now
outnumbered rather than gone.

**This is what makes ingest-fresh / diff / swap mandatory rather than merely
careful.** `ingest_knowledge.py` states the measured fact at its live-write
prompt, and `diff_knowledge_index.py` reports it as a WRITE SAFETY verdict
rather than leaving it to be inferred from an id count.

#### A blocker found in `create_indexes.py`

**`create_improve_knowledge_index()` declared a schema that matched nothing.**
`doc_id`, `title`, `section_title`, `content_text`, `source`, `phase`,
`tool_name`, `belt_level`, `chunk_type`, `page_start`, `page_end`,
`created_at`, and a vector field named `embedding` — **not one of those fields
exists on the live index**, and `phase` is specifically the name §23.1 records
as the filter bug that makes Azure reject the whole query.

**The ratified procedure could not have been executed with it.** A "fresh"
index built from that definition would have rejected every write the ingest
script makes. Corrected against the live schema and verified field by field:
all seven fields match on every attribute, HNSW cosine m=4 efC=400 efS=500,
profile `default`, no semantic configuration.

> **The failure mode is the one this register keeps naming** (§R1, §R2, §0.14,
> §0.16): **a correct-looking artefact that nothing could see was wrong.**
> `create_indexes.py` skips an index that already exists, so it had run
> harmlessly for as long as the index existed, and its definition was never
> exercised against reality. **A creator that only ever no-ops is not
> verified — it is unobserved.** It became load-bearing the moment a *fresh*
> index was required, which is the first time anything would have executed it.

#### What the rebuild produces, and what is not yet decided

**1,184 documents, all `BB_LSS_ebook`** — against 1,125 eBook documents live,
so the eBook's own coverage grows slightly while the corpus overall drops from
1,369 to 1,184. The `general` sentinel lands on 230 documents (live: 218), so
cross-phase methodology stays reachable from every phase.

**Classification moved on 32% of the 700 shared source pages**, consistent with
the ~58% reproduction figure the ratification anticipated. Compared **by source
page rather than by document id**, deliberately: chunk boundaries move whenever
extraction changes, so a chunk id is not a stable identity across a rebuild —
a page is.

> **That figure first read 37-38%, and the difference was the measuring
> instrument, not the corpus.** A page's dominant tag was taken with
> `Counter.most_common(1)`, which preserves *insertion order* among equal
> counts — so the same corpus read from a local JSONL and read back from Azure
> disagreed on the handful of tied pages and produced two different headline
> percentages **on identical data**. Ties now break alphabetically and both
> paths report 32%. **A statistic that moves when nothing moved cannot be used
> to judge a swap**, which is the whole purpose this one serves.

#### What retrieval actually returns — the evidence the swap turns on

The diff reports counts. **This is what a coach receives**, six representative
methodology queries, top-3, live against rebuilt.

**The contamination is not theoretical, and it ranks first.** For *"how do I
validate a root cause with a hypothesis test"* — a DMAIC Analyse question — the
live index returns **`problem_solving_8D` p71, "D5: Identify & Validate the
Root Cause", as the top hit**. A Belt asking an Analyse question gets 8D's D5
step ahead of the eBook's hypothesis-testing chapter. The rebuilt index returns
the eBook's *Purpose of Hypothesis Testing* instead. **This is the exact
failure the corpus decision was ratified to fix, observed live rather than
argued.**

**The normalisation is visible in what the coach would quote:**

| Query | Live returns | Rebuilt returns |
|---|---|---|
| project charter | `• The%Problem • Project%Scope • Project%Metrics` | `• The Problem • Project Scope • Project Metrics` |
| hypothesis testing | `(cid:4)Introduction to Hypothesis Testing(cid:5)` | `Introduction to Hypothesis Testing.` |
| Cpk | chunk ends on the running footer | footer gone, chunk carries content instead |

**The phase-tag changes are genuinely mixed, and that is worth saying rather
than glossing.** Page 634's control-chart-selection table moves `measure` →
`control`, which is better. Page 681's Control-phase wrap-up moves `control` →
`improve` and page 286's hypothesis-testing intro moves `analyse` → `measure`,
both of which are worse. **The rebuild does not improve classification and was
not intended to** — Ruling 2 defers that work precisely because no consumer
reads the field yet. Recorded so nobody later reads the rebuild as having
fixed it.

#### The three rulings

Both items the ratification left open were ruled 2026-08-25, together with a
third question that the rebuild surfaced.

**Ruling 1 — the knowledge rebuild sequences INDEPENDENTLY of the §23.2/§23.3
reindex.** The ratification framed this as "fold into one reindex, or sequence
after?" **The question dissolves rather than trading off:** step 9.1 touches
`improve_evidence_index` and `improve_case_index` **only**, and
`improve_knowledge_index` needs **no schema change at all** — its seven fields,
3072 dimensions and `default` profile were verified live and already match
§23.1 exactly. **There is no shared Azure operation to fold into.** The two are
independent by construction, and the knowledge rebuild is additionally
unblocked where step 9.1 is EXTERNAL and gated on 5.2.

**Ruling 2 — the phase classifier is DEFERRED, because nothing reads what it
writes.** No live code path filters on `phase_relevance`:
`build_knowledge_context()` — the grounding path all five orchestrators call —
invokes `search_knowledge()` with no phase argument and documents the omission
as deliberate; `search_improve_knowledge`'s `phase` parameter defaults to `""`.
Sharpening the tag now would be an unobservable improvement, and would change
two variables at once in a rebuild whose diff is worth being able to attribute.
**Revisit when `rag_lookup_methodology` lands** (§24) — that tool binds the
filter, and the classifier becomes measurable against a real consumer then
rather than against none.

**Ruling 3 — `page_number` stays the PDF index; the citation string carries the
caveat.** Not in the ratification; found during the rebuild. The stored value
and the eBook's printed page number disagree, and **the offset is piecewise,
not constant**:

| PDF pages | Printed number |
|---|---|
| 1–3 | cover, legal notice, contents — unnumbered |
| 4–693 | pdf index − 3 (690 pages) |
| 694–700 | an appendix, numbering restarts at 1 |

So a chunk stored as `page_number: 47` sits on printed page 44, and §23.1's
citation example — *"this came from page 47 of the BB eBook"* — points a Belt
three pages past the content quoted. **A single offset constant would be wrong
at both ends**, pushing front matter to zero and negative and landing 693 out
across the appendix. That shape, not the size of the error, is why the stored
value is unchanged: the PDF index is the one number unambiguous for all 700
pages, and it is what the live index already holds. **The fix belongs in the
citation string — "PDF page N", not "page N"** — and is owed wherever citations
are rendered (CLAUDE.md §13).

#### Execution status

The corpus was built and diffed locally first, then ingested into
`improve_knowledge_index_v2` under Ruling 1. **`improve_knowledge_index` is
untouched** and still holds all 1,369 documents. The swap is deliberately not
part of this record — it is a separate, reported step.

> **Superseded in part by §V2 the same day.** Ruling 2 deferred classification;
> the founder reversed it and folded classification into the rebuild.
> `improve_knowledge_index_v2` was consequently never swapped in — it is the
> keyword-classified build, and `_v3` supersedes it.

---

### V2 — LLM phase classification, and the swap (2026-08-25)

**Status:** RATIFIED and LANDED 2026-08-25. **Supersedes Ruling 2 of §V1** —
classification is IN this rebuild, not deferred to `rag_lookup_methodology`.
**Still not a schema change**, so still not routed through §56.
**Lands in:** `scripts/ingest_knowledge.py` (classifier replaced), `.env` and
`.env.example` (the swap), reference §23.1 and `ARCHITECTURE.md` §23.1
(figures), reference head note v1.7.2.

#### Keyword counting classified on vocabulary; the replacement classifies on subject

`detect_phase` scored each chunk against per-phase word lists and took the
highest count. **That mechanism cannot distinguish what a passage is about
from which words it contains**, and the eBook breaks it in both directions:

| Page | Keyword said | Why it was wrong | LLM says |
|---|---|---|---|
| 681 — Control-phase wrap-up | `improve`, `general` | The page lists "Improvement Selected / Develop Training Plan / Implement Training Plan", so *improve* outscores *control* on a page whose whole subject is closing out Control | **`control`** |
| 286 — introduction to hypothesis testing | `measure` | Dense with measurement vocabulary while teaching an Analyse technique | **`analyse`** |
| 634 — control-chart selection table | `control` | Already correct | `control` |

Each chunk now gets **one call to the cheap tier** — the `operational` role,
resolving to `operational-model` (gpt-4o-mini) — at temperature 0.0, returning
exactly one of six labels. The prompt states what each phase covers and
instructs the model to **judge the passage on what it teaches, not on which
words appear in it**, which is precisely the distinction the scorer could not
make.

**The two classifiers agree on 52% of chunks.** The largest single migration is
`measure → analyse` (71 chunks) — the p286 failure mode, at scale.

| Label | Keyword | LLM | Δ |
|---|---|---|---|
| define | 125 | 62 | −63 |
| measure | 319 | 219 | −100 |
| analyse | 233 | 310 | **+77** |
| improve | 138 | 192 | +54 |
| control | 138 | 142 | +4 |
| general | 230 | 259 | +29 |

#### The output contract avoids a blocked pattern rather than amending it

**The builder-style structured-output call is blocked by
`deprecated_patterns.yaml`'s `pattern-2`, and CLAUDE.md §18.1 already records
that entry as stale** — §4.6 now sanctions it for plain model invocations and
the registry has not caught up.

**Neither available shortcut was taken.** Amending the registry to unblock a
data rebuild is the in-passing rule change §0 and §56 forbid; routing around a
live hook silently is worse. So the classifier does not need the pattern at
all: **one bare label from a closed set of six, matched against that set.**
§4.3 is untouched because no JSON is parsed. **The registry update remains
owed**, and this work neither performs nor depends on it.

> **The hook also fired on this document while it was being drafted**, on the
> sentence naming the blocked call. That is the §0.14 pattern a third time — a
> check that cannot distinguish using a construct from documenting one. It is
> also exactly why §18.1 path-excludes `agent-improve/**/*.md`, and the
> exclusion did its job.

#### Two failure modes, opposite handling — and a bug in the first attempt

**The first full run aborted, and the abort was correct.** At 8 concurrent
workers Azure returned HTTP 429 for **603 of 1,184 chunks**. Those fall back to
`general`, which would have produced a corpus of 750 `general` tags with
roughly 600 of them fabricated. `--max-classify-failures 0` stopped it and
**nothing was written**.

**It exposed a defect in the classification cache.** The fallback was cached
alongside real verdicts, so every rate-limited chunk would have been recorded
as a decided `general`. **The cache exists to make a re-run cheap and
reproducible; caching the guess would have made the re-run skip precisely the
chunks that needed retrying** — turning a transient 429 into a permanent
mislabel, invisibly, inside the mechanism meant to protect against it. **A
missing key is retried; a cached guess is forever.** Only real verdicts are
cached now.

**The two failure modes need opposite handling, and the architecture already
said so:**

| Mode | Handling | Evidence |
|---|---|---|
| **429, transient** | Retry with jittered exponential backoff; 4 workers, not 8 | 603 failures → **1** |
| **400 `content_filter`, permanent** | **Do not retry** | reference §27 / CLAUDE.md §7.2 — "a 4xx is permanent, and retrying fails identically" |

**Jitter matters as much as the backoff**: every worker hits the quota wall at
the same instant, so a fixed sleep marches them back into it together.

**One chunk ships unclassified, by explicit decision.** PDF page 302 — a
passage on statistical power and sample size for a 1-Sample t test — is refused
by Azure's content management policy. A false positive, and permanent. It ships
as `general`: genuinely Analyse content, so precision is lost, but `general` is
ORed into every phase filter so the passage stays retrievable from all five
rather than dropped or given a tag nobody stands behind. **The run proceeds
past it only under an explicit `--max-classify-failures 1`**, and
`classify_corpus` now names unclassified chunks by page and id rather than
merely counting them.

#### Verification, then the swap

Both gates ran against `improve_knowledge_index_v3` **before** the env var
moved.

**Gate 1 — the Analyse contamination probe**, *"validate a root cause with a
hypothesis test"*. The live index returned `problem_solving_8D` p71 — 8D's
"D5: Identify & Validate the Root Cause" — **at rank 1**. The rebuilt index
returned **zero non-eBook results** in the top 5. The normalisation shows in
the same output: live returns `Mood(cid:1)s Median Test`, rebuilt returns
`Moods Median Test`.

**Gate 2 — the three pages the keyword classifier got wrong.** p286 `analyse`,
p634 `control`, p681 `control` — every chunk on every page correct.

**The swap is one line and reversible.** `AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX`
now reads `improve_knowledge_index_v3` in `.env` and `.env.example`.
**`improve_knowledge_index` is retained intact at 1,369 documents** as the
rollback target — point the variable back and the previous corpus is live
again, with no re-ingest.

Confirmed post-swap through the application's own path: `search_knowledge()`
returns no 8D, `build_knowledge_context()` produces a 4,319-character grounding
block containing none, and `_phase_filter()` now selects meaningfully different
content per phase — which it could not usefully do while the tags were keyword
artefacts.

**This reverses §V1's closing note.** That entry recorded that the rebuild "does
not improve classification and was not intended to". With §V2 it does, and the
p681 / p286 / p634 cases are the demonstration.

#### One residual, deliberately not fixed here

**`CLAUDE.md` §7.2 still reads "(218 carry `general`)".** It is a binding rule
file, and correcting it requires a numbered `§0.x` entry under §18. **That is a
rule amendment, not a figure sync**, and making it inside a data-rebuild commit
is what §56's "never amend a rule in passing" forbids. Recorded as owed.

The same figure appears in `docs/DECISIONS.md` §E3,
`docs/REFACTORING_AGENT_IMPROVE.md` and `docs/REVIEW_DECISIONS.md`. **Those are
the historical record and are correct as history** — they state what was
confirmed when it was confirmed. Rewriting them would falsify the trail.

---

## Part W — The Define phase, fully specified (2026-08-26)

### W1 — §39.1, G-38 closed, and the Define atomic unit rebuilt

**Status:** RATIFIED 2026-08-25 (`docs/_archive/DEFINE_AMENDMENT_2026-08-25.md`), applied
2026-08-26. **§56 amendment** — it adds a governance rule (§56.1), changes a
shared schema (`CoachingResponse`), and closes a register gap.
**Lands in:** `ARCHITECTURE.md` §39.1, §50.1, §56.1, §20/S-C05, §35, §40,
§63.1, §66; `phases/define/{schema,validate}.py`;
`skills/dmaic-define-phase/SKILL.md`. (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.1)

#### Three collisions between the amendment and the live document

The amendment was ratified against an out-of-date reading of `ARCHITECTURE.md`.
**None of the three was resolved by guessing**; each went to a founder ruling
before any file was touched.

**1. "New §41" was already occupied.** §41 is "Structured dict fields, and
FMEA" — RATIFIED, cited **23 times** inside `ARCHITECTURE.md`, three times in
`CLAUDE.md` §10.8, and mapped in Appendix A (`§4.10.5–§4.10.7 → §41`). It is
also where the partial-map rule lives, which the amendment's own §41.5 cited as
"(§41)" — circularly. Sections run 1–68 with **no gaps**, so Part VIII had no
free two-level number.

> **Ruling: Define is §39.1.** §39 is "The five phases", and §39.1 expands the
> very table row that describes Define. **Zero citations break**, and §39.2–
> §39.5 are reserved for the other four (§39.1.8). The cost is three-level
> sub-numbering (§39.1.2, §39.1.7), which this document did not previously use.
> **Renumbering §41 was rejected**: it would have rewritten 23 internal
> citations plus three in a binding rule file, pulling a §18 amendment into a
> feature commit — the thing §56 exists to prevent.

**2. `secondary_metrics` vanished.** §41.2's ten-row table omits it, but §40
requires it on **all five schemas** as the Tier-2 counterpart to
`issues_and_barriers`, and Part E did not retract that rule.

> **Ruling: keep it.** §39.1.2 is explicitly *"the `field_index` sequence the
> planner walks"* — the **coached** list. Gate-metadata fields are already
> excluded from it on the same logic, so reading ten rows as the whole schema
> was the misreading. `DefineOutput` is **15 fields: 8 Tier 1, 3 Tier 2, 4 gate
> metadata**. §40's cross-schema invariant stands, unretracted.

**3. `message` versus the four presentational fields.** Part C says the visible
message is carried "as discrete presentational fields, not one free-text blob";
Part D says existing S-C05 fields are "unchanged", which leaves `message` in
place. Two sources of truth for what the UI renders is exactly the
inconsistency §50.1 exists to remove.

> **Resolved without a ruling, because §20 already gives `message` a second
> job:** it is appended to `messages` and is what summarisation later
> compresses (§19.3). So `message` is the **transcript** and the four are the
> **render contract**. Documented at S-C05 rather than left to be rediscovered.

#### What changed

| Site | Change |
|---|---|
| **§39.1** (new) | Define fully specified — purpose, the ordered field list, the composed-problem-statement rule, `team` structure, SIPOC handling, gate/storage, the SKILL content, and the shape the other four phases inherit |
| **§39.1.2** | The ten-field coached order — **this list closed G-38** |
| **§50.1** (new) | Coach response structure: Explanation / Example / Your turn / Progress, schema-backed rather than prompt-hoped |
| **§56.1** (new) | The atomic-unit principle, plus the five-step capture path and the rule that middleware never captures |
| **§20 / S-C05** | `CoachingResponse` gains `explanation`, `example`, `prompt`, `progress` |
| **§35** | Define Tier 1: 6 → **8** (`team` and `baseline` join) |
| **§40 / §63.1** | Define counts 15/**8**/**3**/4; `DefineOutput` rebuilt; `project_scope` becomes a dict; a note that a coached list is not a schema |
| **§66** | G-38 → **Closed**; F-11 recorded; **7 inline G-38 markers reconciled** |

**G-38's closure is per-phase, and the document now says so in all eight
places.** Closing it in the register while seven spec entries still read
"blocked on G-38 (open)" would have been the §55 failure mode — a register that
disagrees with the entries it governs. Each marker now states that Define has
its list and the other four remain blocked on G-27 and G-28.

**Register: 44 identified, 9 closed or resolved, 35 open** — counted
mechanically from §66.1–§66.6, not carried forward from the previous note.

#### The consequence that is not in the amendment

**Conforming `validate.py` to §39.1.2 breaks the v1 Define gate, and this was
verified rather than assumed.** `DefinePhaseInput` was consumed by
`validate.py` alone; the actual **writer** on the v1 path is
`phases/define/orchestrate.py`, which still emits the granular 5W2H names. With
the validator on v2 names and the writer on v1 names, **every Tier 1 field
reads as missing and the gate cannot open.**

**A v1-to-v2 shim was rejected.** It would be *adding* v1-style code, which
CLAUDE.md §17 forbids, and it would hide the divergence at precisely the seam
where the two vocabularies meet — which is how a rename half-lands and stays
half-landed. The divergence is instead **stated at the top of `validate.py`**
and tracked.

**The three downstream cross-phase briefs were deliberately NOT updated.**
`analyse`, `improve` and `control` orchestrators read Define's v1 names, and
they are consistent with the v1 writer as it stands. **Switching the readers
ahead of the writer would break the briefs rather than fix them.** They migrate
together at procedure step 3.4. The one stale comment naming the now-deleted
`DefinePhaseInput` was corrected in place.

#### Verification

33 automated checks, all passing: §39.1.2's table parsed and compared against
`schema.py`'s constants; the three files' field vocabularies proved identical;
SKILL.md's body proved **verbatim** against §39.1.7 by substring match (it is
generated from that section, not retyped); §35/§40/§63.1 counts reconciled; the
capture path round-tripped `fields_captured` → `artifacts` →
`DefineOutput(**artifacts)`; and the gate proved to block on a missing Tier 1
field, a four-of-six SIPOC and a one-sided `project_scope`, while **not**
blocking on absent Tier 2. Drift-check clean on all five changed files. Pytest
6/6. Pydantic field typing and the `response_format=` contract verified against
live documentation (report in-session).

> **One check failed first, and it was the check that was wrong.** The §39.1.2
> table parser skipped row 8, whose type cell reads `` `str` (ISO) `` — text
> outside the backticks that the pattern did not allow — and reported a false
> order mismatch against a correct document. Fixed, and a row-count assertion
> added so a silently-skipped row fails loudly instead of producing a confident
> wrong answer.

#### Owed

- **`CLAUDE.md` §9.7 and §10.7 carry Define's old counts** (6 Tier 1, 15/6/5/4).
  Founder ruling: **not touched here.** §18 requires a numbered `§0.x` entry,
  which makes it a rule amendment rather than a figure sync, and §56 forbids
  making one in passing. Joins the still-owed §7.2 "218 carry `general`" fix.
- **`phases/define/orchestrate.py` migration** — step 3.4, and with it the three
  cross-phase briefs.
- **The `CoachingResponse` UI rendering** — §50.1 defines the contract; no
  production UI exists yet.

---

## Part X — WATCH 7: the v1 Define writer is carried, not migrated (2026-08-28)

### X1 — Route A. `orchestrate.py` is deleted at 11.1, never migrated; WATCH 7 clears at 6.2

**Status:** RATIFIED 2026-08-28 (founder ruling). **Not a §56 amendment** — it
changes no design, no schema and no rule. It rules on **build sequencing**: which
of three routes closes a watch, and therefore what work is *not* done.
**Lands in:** `CONTINUITY.md` §5, §6, §9 (v4.9); `REFACTORING_PROCEDURE.md`
§0.2's gate row, the status banner, steps 6.2 and 11.1.
**Source:** `docs/_archive/WATCH7_AUDIT_2026-08-27.md` — the evidence and the three
costed routes. (archived to docs/_archive/; canonical: DECISIONS.md Part X)

#### The ruling

**`phases/define/orchestrate.py` and `EXTRACTION_DEFINE`'s Define block are NOT
migrated to the v2 §39.1.2 field names.** They keep writing the v1 names,
unchanged, until the executor's own capture path exists at **step 6.2**
(`create_agent(…, response_format=CoachingResponse)`), and are then **deleted at
step 11.1** — which is what `REFACTORING_PROCEDURE.md` Appendix B specified from
the beginning.

**The Define gate is accepted as inert until 6.2.** Nothing is blocked by that:
no case runs the Define gate today, and steps 2.4 → 3.3 are all clear.

**WATCH 7 clears at step 6.2, not step 4.1.** §0.2's gate table says 4.1, and
that is wrong on its own terms — **step 4.1's own prompt has the executor still
delegating to `orchestrate_define`**, so 4.1 cannot stop the v1 writer writing.
The row is **annotated rather than rewritten**, per the annotate-don't-rewrite
rule.

#### What was ruled against

**Route B — full v1→v2 cutover now: REJECTED.** It is not step 4.1; it is step
3.4's Define portion *plus* the `ui/index.html` coupling that is outstanding for
all five phases — 78 UI sites, Measure's metric seeding, `gateway/routes.py`,
`upload/agent.py`, and design rulings owed on 5W2H retention, `process_metrics`
capture and the registry's `meaning` key. Its verify method is **`manual-UI`**.
Running it now would put the project's largest untested file in front of the
foundation steps everything else depends on.

**Route C — bring the executor forward: REJECTED.** 6.2 depends on middleware,
tool binding and `PhaseState`; reordering it earlier pulls most of Stages 3–5
with it, and the reorder is itself a §56-class amendment.

#### Why Route A, in one line

**It spends nothing on a file the procedure already marks for deletion.**
Appendix B lists all five `orchestrate.py` under **Delete**, step 11.1 deletes
them, and `phases/define/validate.py`'s own docstring says the v2 writer is the
executor node. Migrating a file scheduled for deletion, purely to keep a v1 path
alive, is the investment CLAUDE.md §17 exists to prevent.

#### The consequence that must survive this ruling

**Every v1 Define field name now in the tree is the RULED-CORRECT state, not
drift.** A future session — or a drift sweep — will find `define.what`,
`define.how_goal`, `define.primary_metric`, `define.sipoc`, `scope_in`,
`estimated_completion_date` and the rest in:

- `phases/define/orchestrate.py` and `core/prompts.py`'s `EXTRACTION_DEFINE`
- the three cross-phase Define briefs in `analyse` / `improve` / `control`
- `phases/measure/orchestrate.py` and `phases/measure/validate.py` (metric seeding)
- `gateway/routes.py:433` and `upload/agent.py:89`
- 78 sites in `ui/index.html`

**Leave them.** They are removed together, at 10.2 (the UI half) and 11.1 (the
backend half) — not one at a time, and not as a tidy-up. **Two vocabularies
coexisting is the ruled state of this codebase until then**: `schema.py`,
`validate.py` and the five SKILL.md files speak v2; everything that executes
speaks v1. Only `goal_statement` and `target_date` exist in both.

#### The measurement that made the ruling checkable

Set-comparison of what the v1 path writes against `DefineOutput.model_fields`,
run before any change so it was a check that could fail:

| | |
|---|---|
| Written / declared / gate-read | **26 / 18 / 13** |
| Names already agreeing | **2** — `goal_statement`, `target_date` |
| Required fields v1 can never supply | **11 of 13** |

The intersection of 2 matches `validate.py`'s docstring exactly. **WATCH 7's
diagnosis was right; its estimated size was wrong** — that is the whole finding.

#### Owed

- **`ARCHITECTURE.md` §39.1.2 says "16 fields in total: 12 required, 4 gate
  metadata"** where §40 and §63.1 in the same document both say **18**. Stale
  since the metric registry landed at v1.15. **Not touched here** — it is a §56
  route, and §56 forbids making one in passing. The code-side copy of the same
  figure (`phases/define/schema.py`'s class docstring) **was** corrected, since
  that is a docstring rather than a governance figure.
- **Step 10.2 (the UI rebuild) must land before 11.1's backend deletions**, or
  the workspace renders blank panels with no error — the failure step 3.4 names.
  Recorded at step 11.1.

---

## Part Y — G-21 resolved: the `storage/blob.py` function surface (2026-09-01)

### Y1 — There is no class interface, and that is the resolution

**Status:** RATIFIED 2026-09-01 (founder ruling, at the step 3.5 review).
**Not a §56 amendment** — it changes no design, no schema and no rule. It
**records a ratification already made** and closes a register entry that had
been carried as open while the decision behind it was taken.
**Lands in:** `ARCHITECTURE.md` §58.8 (S-C08) and §66's Group D row and header
count; `CONTINUITY.md` §6.
**Source:** procedure step 3.5, commit `025bde7`.

#### The gap, and why it could not be answered as written

**G-21 asked for "the class interface — method names, signatures, return types,
and how registry updates are sequenced against case writes."** The first three
quarters of that question had no valid answer: **§54 and `CLAUDE.md` §2 both
name `storage/blob.py` among the files that hold module-level functions ONLY**,
with no exception. `ImproveBlobClient` was a class where none is permitted — the
same violation step 2.7 cleared in `core/llm.py`.

**So the gap was answered by removing its subject.** Step 3.5 deleted the class.
The `grep -rn "class ImproveBlobClient" agent-improve/backend/` in the step's
own *Done when* returns zero.

> **S-C08's own title is still `ImproveBlobClient`.** That is now a stale label
> on a spec entry whose subject is a module, not a class. Left as-is
> deliberately: renaming a spec-entry title is a §56 amendment and does not
> belong in a record-keeping commit.

#### The ratified surface — thirteen module-level names

| Kind | Names |
|---|---|
| **sync** | `case_path(case_id) -> str` · `storage_configured() -> bool` |
| **async** | `load_case` · `save_case` · `create_case` · `write_phase_gate` · `append_turn` · `load_registry` · `save_registry` · `register_case` · `upload_file` · `aclose` |
| **const** | `REGISTRY_BLOB_PATH` |

`case_path` stays synchronous because it is pure string construction; making it
`async` would be noise. Everything that performs I/O is `async`, per §1.4 and
§49.

**`storage_configured()` replaces the import-time singleton.** The old module
built a client at import under a bare `except` and left `blob_client = None` on
failure — so an unrelated construction error read to every caller as "storage
not configured", and a 503 was returned for a bug. The function reads settings
at call time and answers only the question it is named for.

#### B2's sequencing — the case blob first, then the registry

**`write_phase_gate` awaits `save_case` before `_update_registry_entry`.** The
order is not arbitrary: `cases/case_{id}.json` is the system of record and
`registry.json` is a projection of it, so **the registry must never point at a
phase the case document does not yet show.** The reverse order would leave a
window where the dashboard advertises a gate the case has not recorded.

They remain **two separate writes**, exactly as S-C08 B2 states, both covered by
the node's `error_handler` (§45). This ruling settles their *order*, not their
atomicity — Blob gives no cross-blob transaction and none is claimed.

#### The aio lifecycle — ruled on a measurement, not a preference

**One cached `azure.storage.blob.aio` client, keyed on its event loop, closed by
`aclose()` on `app.py`'s existing shutdown hook.**

Measured against the real container (`agent-improve-cases`, case
`IMPR-2026-E9D`, 74,693 bytes, n=25, 2026-09-01):

| shape | load (median) | save (median) |
|---|---|---|
| per-operation client (`core/store.py`'s pattern) | 289.2 ms | 360.3 ms |
| **cached client** | **96.6 ms** | **82.5 ms** |

**~470 ms per `/ask` request, 3–4×.** The figure that decided it: constructing a
client and tearing down its session with **no blob I/O at all costs 0.5 ms**.
The 470 ms is TLS and connection setup a fresh pool cannot reuse — so the
per-operation shape was never paying for object construction, which is precisely
why the procedure demanded a number rather than an opinion.

**`core/store.py` keeps the per-operation shape and is right to.** Store writes
happen a handful of times per phase; the trade that is wrong on `/ask` is
correct there. Two Blob owners, two lifecycles, one measurement each.

**This does not depend on the gated step 8.5.** `app.py` already had an
`@app.on_event("shutdown")` hook; 8.5 is the graceful *drain* of in-flight
coaching turns via `RunControl.request_drain()`, a different concern from
closing an HTTP session. (That hook's own deprecation is **WATCH 12**.)

#### What G-21 does NOT resolve

**Deletion.** S-C08's *Paths owned* includes `uploads/{case_id}/{file}`, and no
behaviour anywhere governs removing one. `DELETE /files/{case_id}/{file_id}`
drops the upload record from the case document and leaves the blob in place
forever. **This is a new gap, not a residue of G-21** — G-21 asked about the
interface and the write sequencing, and both are now answered. Carried as
**WATCH 10** with a SPEC-GAP owed.

#### Register effect

**§66: 46 identified, 13 → 14 closed or resolved, 33 → 32 open.**

> **The 12/34 figure quoted when this closure was scoped was already stale.**
> §66's own header had moved to 13/33 when **G-27** closed at procedure step 3.3
> on 2026-08-31, and `CONTINUITY.md` §6 was never updated to match — the same
> propagation failure its own bracketed note records against the earlier
> 44/9/35. Both are corrected here, so the live figure is **46/14/32** and the
> two documents agree.

---

## Part Z — Step 4.2: the checkpointer becomes real (2026-09-02)

**Procedure step 4.2**, `thread_id` through `graph.ainvoke` and the disconnect
policy. Reference §16, §47, §49; CLAUDE.md §1.1, §1.2, §1.7. This part records
the seven decisions the step had to make, because none of them were settled by
the paper spec and each would otherwise have to be re-derived by the next
session.

**What the step delivered:** `gateway/routes.py` no longer dispatches a node.
Both hand-built tables (`node_map` in `/ask`, `validate_map` in `/gate`) and all
ten function-level `orchestrate_*` / `validate_*` imports are gone; both routes
call `await graph.ainvoke(state, config={"configurable": {"thread_id": case_id},
"recursion_limit": 50})` on the same compiled object. **These are the first
checkpoints this system has ever written** (§53.1, Appendix E).

---

### Z1 — A one-node parent, not the supervisor

**Ruled: build the smallest parent §16 permits — `START → define_phase → END`
over `SupervisorState`, compiled with checkpointer AND store — and let 4.3 grow
it.**

The step needs *a* parent for exactly one reason: §16 puts the checkpointer and
the store on the parent and forbids them on a subgraph, so making checkpoints
real requires a parent to attach them to. It does not need the *supervisor*,
which is 4.3's subject (five phase nodes, static DMAIC edges, escalation, and a
test asserting that topology) and which cannot be built anyway while four of the
five subgraphs land at 4.4.

**The v1 chained graph was deleted rather than kept alongside.** It wired ten
`orchestrate_*` / `validate_*` nodes over `ImproveGraphState` with conditional
edges running Define through Control, so one `ainvoke` would have executed the
whole DMAIC sequence — which is precisely why the route dispatched a single node
by hand. It has no turn boundary and cannot be invoked. `escalate` goes with it
and returns as the parent's conditional branch at 4.3.

**Consequence, ruled and recorded rather than hidden: only Define runs through
the graph until 4.4** (WATCH 17). The other four raise `PhaseNotWired` → HTTP
501. Reinstating a v1 fallback table for them was rejected: that table is the
thing §49 exists to remove, and no case can reach Measure today anyway — the
Define gate is inert (WATCH 7), `current_phase` advances only on a gate pass,
and the UI locks later phases.

---

### Z2 — `define_output_mapper` is designated and deliberately not called

**Ruled: the parent node runs the input mapper and the subgraph, and does NOT
run the output mapper. `gate_apply` writes nothing.**

§15 says a phase subgraph reaches `END` only through `gate_apply`, so arriving
there means the gate passed. **That is a statement about the finished subgraph
and becomes true when stage 7 lands the `interrupt()` at `gate_review`.** At 4.2
there is no interrupt, so the subgraph runs to `END` on every invoke and `END`
means only "the graph ran".

Calling the output mapper here would therefore write a gate document to the
Store and advance `current_phase` **on every coaching turn** — a gate approval
the Belt never saw, which is the exact failure §47's ABANDON policy and §33's
nine-step gate exist to prevent. The two omissions (`gate_apply`'s writes and
the output mapper call) are one decision and must be reversed together at
stage 7.

**What this buys is `current_phase`'s single writer, made real** (§5 B2, S-F11
B1). The v1 routes rebuilt an eleven-field `ImproveGraphState` literal per
request with `current_phase` in it. 4.2's routes write the seven `SupervisorState`
fields **once**, on the turn where the thread has no checkpoint, and send only
the new message afterwards — so the output mapper is the only thing that could
write it, and nothing else does.

---

### Z3 — `checkpoint_ns` was missing from the blob layout. That was a defect.

**Found at 4.2, the step that first invoked the graph. Fixed in
`core/checkpointer.py`, which was NOT in the step's `Touches` list.**

§1.7's layout — `checkpoints/{thread_id}/latest.json` plus
`history/{checkpoint_id}.json` — was written before phase subgraphs existed in
the code, and `AzureBlobCheckpointSaver` keyed every path on `thread_id` alone.
§16 puts the checkpointer on the parent and routes the subgraph's writes through
it **distinguished by an auto-managed `checkpoint_ns`**; this class read
`thread_id` from `config["configurable"]` and discarded `checkpoint_ns`
entirely. So parent and subgraph wrote to **one** `latest.json` and read each
other's state back.

**The symptom raised no error.** The Define subgraph loaded the parent's
`messages` on top of its own and the conversation doubled every turn, while
every individual turn still looked correct. Reproduced directly: LangGraph
assigns `""` to the parent and `"define_phase:{task_id}"` to the subgraph.

**Fix:** `""` keeps `checkpoints/{thread_id}/…` **exactly** — so step 4.2's own
`azure-query` verification reads the path it names and no existing blob moves —
and a non-empty namespace goes under
`checkpoints/{thread_id}/ns/{percent-encoded ns}/…`. `checkpoint_ns` now flows
through `put`, `get_tuple`, `list` and the returned configs.

**Editing a file outside `Touches` was the lesser evil**, and it is recorded
here rather than left in a commit body: without it 4.2 does not work, and the
alternative — a step that ships a corrupted conversation — is not a step. The
class docstring and the module header both state the added segment.

> **This is the fourth instance of the pattern this project keeps naming**: a
> rule that was correct (§16 has always said `checkpoint_ns`) paired with an
> implementation that could not be seen to disagree with it, because nothing
> exercised it. Zero checkpoints had ever been written.

---

### Z4 — Per-run framing rides on `config`, not on state

**Ruled: `entry`, `current_user`, `case_metadata` and `v1_artifacts` travel in
`config["configurable"]`.**

`PhaseState` is twenty-one declared fields and a twenty-second requires a §56
amendment; `SupervisorState` is seven and an eighth likewise. The v1
orchestrator needs the case framing and the route needs to say whether this turn
coaches or validates, and **none of it wants to be state**: it is immutable
per-run configuration, which is what `configurable` is for, and
`core/checkpointer.py` already reads `thread_id` from exactly there. No
mechanism is invented; the one already in service is used.

**One API fact, verified against the installed LangGraph 1.2.11 rather than
remembered.** LangGraph injects `config` into a node only when the parameter's
annotation is exactly `RunnableConfig`, `"RunnableConfig"`,
`Optional[RunnableConfig]` or `"Optional[RunnableConfig]"`
(`langgraph/_internal/_runnable.py`, `KWARGS_CONFIG_KEYS`). Under
`from __future__ import annotations` — which every file here uses —
`config: RunnableConfig | None = None` stringifies to `"RunnableConfig | None"`,
which is **not** in that tuple: LangGraph emits a `UserWarning` and **silently
does not inject config**. Every node would have run with `config=None` and the
coach would have lost its framing with no error. All signatures use
`Optional[RunnableConfig]`, and `test_config_reaches_the_v1_seam` pins it.

---

### Z5 — The turn's product travels on the message

**Ruled: the coach's answer, the captured fields, the presentational payloads
and the gate verdict all ride in the reply `AIMessage`'s `additional_kwargs`.**

`SupervisorState` carries orchestration only (§5) and `graph.ainvoke` returns
`SupervisorState`, so `messages` is the only channel from the graph to the
route. That is not a workaround — it is the channel `CoachingResponse`
formalises at 6.2 (§10.7), reached early by the seam.

Two shared helpers make it one implementation rather than two: `messages` ↔ v1
turn dicts live in the new `core/conversation.py`, because `gateway/routes.py`
and `phases/define/nodes.py` both need the conversion and neither may import the
other (routes importing a phase's nodes is what §1.1 forbids; `phases/`
importing `gateway/` inverts the layering). **Not in Appendix B's `New` file
list** — flagged, like `phases/mappers_common.py`, rather than assumed.

---

### Z6 — The 4.1 subgraph could not actually run; 4.2 had to fix three things

Step 4.1 built the topology and **routed no traffic**, so three defects were
latent. All three are fixed in `phases/define/nodes.py`:

| # | Defect | Consequence had traffic been routed |
|---|---|---|
| 1 | **The planner/executor cycle did not terminate.** The predicate was `"executor" if not artifacts else "validation_stack"`, and the executor writes `draft`, never `artifacts` (deliberately — WATCH 7) | `artifacts` stays `{}` forever, the planner routes to the executor forever, `GraphRecursionError` at the §16 backstop of 50. Invisible at 4.1 because the only caller was a test that seeded `artifacts` by hand |
| 2 | **The bridge dropped everything the route returns** — the coach's answer, the SIPOC payload, the visualisation, the section-completion marker | `/ask` returns an empty answer to the Belt |
| 3 | **`_to_v1_state` could not run.** It passed `PhaseState.history` (`list[str]` breadcrumbs) as v1's `chat_history` (turn dicts), and omitted `case_metadata` and `current_user` | `AttributeError` on `str.get("role")` on the first turn |

**The new predicate is `turn_count`-based and is a PLACEHOLDER, not DP1.**
`entry == "gate"` → validate; `turn_count == 0` → coach one turn;
`turn_count > 0` → leave the cycle. The executor increments it and the input
mapper resets it, so **one `ainvoke` is one Belt turn** — the boundary the
procedure's own ordering note says 4.2 exists to establish. S-F13's real DP1
reads §39.1.2's field ordering and lands at 6.1. Pinned by
`test_planner_does_not_route_on_artifacts`, so the retired predicate cannot
return by accident.

**`draft` is the v1 accumulator for the duration of the WATCH 7 seam**, and
`artifacts` stays empty. `draft` is `PhaseState`'s "this turn's extraction" and
the v1 running extraction is exactly that; putting v1 names into `artifacts`
would put them on the v2 gate path, which Route A exists to prevent.

---

### Z7 — `validation_stack` runs the validator only on a gate submission

**Ruled: `validation_stack` delegates to the v1 `validate_{phase}` when the
planner's `next_action == "gate"`, and passes through otherwise.**

Symmetric with the executor's `orchestrate_define` delegation and governed by
the same WATCH 7 ruling: `validate.py` is carried unchanged and deleted at 11.1,
and the verdict is the one `/gate` returned before, on the same inputs, computed
in a different place. The Define gate stays inert.

**Running it on every coaching turn was rejected, and the reason is §34's cap.**
`validate_define` increments `gate_attempts` on failure, so validating each
coaching turn would burn the shared cap of 3 in three turns and escalate a Belt
who is simply still typing — the cap firing on the wrong event. Pinned by
`test_a_coaching_turn_never_runs_the_validator`.

**`gate_attempts` moved out of route scope but does not yet accumulate** — see
WATCH 18. The counter's home is now correct (`PhaseState`, §1.7); its lifetime
is not, and that half needs the interrupt at stage 7.

---

### The §47 disposition, stated once

**Three in scope, two deferred. Not five of five.**

| # | Requirement | Disposition at 4.2 |
|---|---|---|
| 1 | Deliberate handler shape | **IN — but not as first shipped.** The inline `await` this step originally carried does NOT abandon on disconnect, and the `azure-query` verification disproved it (Z8). It is now a disconnect race: the run is a task, an ASGI `receive()` watcher runs beside it, and the task is cancelled and awaited the moment `http.disconnect` arrives. `/ask/stream` is still 10.1's and must choose again rather than inherit |
| 2 | Deterministic `step_log` keys | **IN.** `f"{phase}:{turn_count}:{step_name}"` at **every** write site, via one `step_key()` helper so it is checkable rather than habitual. The parent's `history` reuses the same keys rather than minting a second identity |
| 3 | Per-thread concurrency guard | **IN, as the optimistic ETag guard rather than the specified lease.** The guarantee is *two tabs waste a turn, they do not corrupt one*. The pessimistic lease and the unguarded history-blob orphan are WATCH 15, resolving at PostgreSQL |
| 4 | Reconciliation sweep excluding paused threads | **OUT** — needs `interrupt()`, stage 7. WATCH 13 |
| 5 | `thread_id` from the authenticated session | **OUT** — no auth layer; §17 places it post-refactor. `case_id` stays client-supplied. **WATCH 14, and it is a tenancy gap, not a tidiness one** |

---

### Z8 — The ABANDON policy did not work as first shipped. The live verification is what found it.

**This is the most important thing step 4.2 learned, and it was learned by
running the check rather than by reviewing the code.**

Step 4.2 shipped `/ask` and `/gate` with a plain `await graph.ainvoke(...)`,
commented as the deliberate §47 shape on the reasoning that *the run is the
handler's own task, so when the client goes the task is cancelled with it*.
**That reasoning is false on this stack**, and the step's own `azure-query`
verification is what established it: a client killed 3 seconds into a 30-second
turn left the turn running. It completed 5 seconds later, wrote **12 checkpoint
blobs** across the parent and a fresh subgraph namespace, and appended **two
turns to the case blob**. §47's opening finding, reproduced word for word —
*the Belt sees nothing; the checkpoint says the turn happened.*

**Starlette does not cancel an endpoint coroutine on client disconnect.**
Verified against the installed starlette 0.50.0 / uvicorn 0.29.0. The server
records the disconnect on the receive channel; a handler that never awaits
`receive()` is never told, and runs to completion. Only a streaming response
(whose generator is closed) or an explicit read of the receive channel observes
it.

**The second attempt also failed, and its failure is the more instructive one.**
Racing the run against a `Request.is_disconnected()` poll looks exactly right
and does not fire. Uvicorn's `receive()` does two things in order —
`flow.resume_reading()`, then `await message_event.wait()` — and Starlette's
`is_disconnected()` wraps that call in an **immediately-cancelled
`CancelScope`**. So each poll re-arms the socket read and tears down its own
wait in the same tick; nothing ever waits for the protocol to deliver the EOF.
Live result: the turn completed again, 19 seconds after the client left.

**What works is awaiting the raw ASGI `receive()`** in a watcher task beside
the run, cancelling and then *awaiting* the run when `http.disconnect` arrives.
Re-verified live: the handler logged the abandonment **in the same second as
the abort**, **no node ran at all**, no subgraph namespace was created, and the
case blob was untouched.

**Three rulings fall out of this and bind on later steps:**

1. **`t.cancel()` is not enough on its own — the cancelled task must be
   awaited.** Cancellation is a request; a handler that returns without
   awaiting leaves the run finishing on the loop, still checkpointing. That is
   the original defect with extra steps.
2. **The guarantee is scoped, and the scope is what to state.** LangGraph
   writes an entry checkpoint when `ainvoke` begins, before any node runs, so a
   turn abandoned after that point leaves those blobs behind. What ABANDON
   guarantees is that **no node runs and no checkpoint is written AFTER the
   client is gone** — not that the turn leaves no trace. A partially-executed
   turn is what resuming from `latest.json` is for. **Procedure step 4.2's
   *Done when* said "leaves no new checkpoint", which was written before anyone
   knew about the entry checkpoint; it is corrected to the scoped form.**
3. **`/ask/stream` (step 10.1) must make this choice explicitly in its own
   `gen()`'s `finally`.** Inheriting this one silently is precisely the
   accident §47 names.

> **The standing lesson, paid for again.** *A check that cannot fail is worse
> than no check, because it is recorded as evidence.* Here the check COULD
> fail, was run, and failed — which is the only reason the system does not now
> ship a documented ABANDON policy that quietly does the opposite. Both wrong
> implementations passed a green unit suite. `backend/tests/test_abandon.py`
> now pins the mechanism, not just the outcome, so neither can return.

---

### Confirmed before coding, as the step required

**The 4.2 node path's only external write is the case-blob save.** Traced with
an unfiltered `grep -rn`: `improve_case_index` is **read** only
(`knowledge/retriever.py`), the single `upload_documents` call in the codebase
writes `improve_evidence_index` from the file-upload route — outside the `/ask`
path — and nothing in `phases/`, `escalate.py`, `knowledge/` or `upload/agent.py`
writes an index. The Store write (`write_gate_document`) sits in the output
mapper, which Z2 rules is not called.

**The case blob is still written per turn**, which §10 says it should not be.
That is unchanged v1 behaviour and is not 4.2's to fix: the conversation moves
into the checkpoint only once the checkpoint is where the UI reads it from,
which is the UI rebuild at 10.2. What 4.2 changes is that the checkpoint now
exists alongside it.

---

## Part AA — Step 4.3: the escalation topology, and why Level 1 still does not route (2026-09-02)

**Procedure step 4.3**, the supervisor graph. Reference §12, §15, §16, §38 and
**§58.10 — S-F01**; CLAUDE.md §1.2, §3.5. One ruling, recorded because the
step's own prompt asked for the shape that has already been deleted once.

---

### AA1 — Escalation is a NODE at Level 1 and an EDGE one level down

**Ruled: the supervisor gets an `escalate` node with a single static edge to
`END`, and NO conditional edge anywhere at Level 1.** The conditional edge that
reaches it lives inside the phase subgraph, and the hop is
`Command(graph=Command.PARENT, goto="escalate")`.

**The step's prompt says "route to escalation on the conditional edge §3.5
describes", and read literally that rebuilds `route_after_phase`.** §3.5 names
the *trigger* — the validation stack exhausting its shared cap of 3 — and does
not say where the edge lives. Two ratified sections do, and they agree:

  * **§15:** *"Escalation at >= 3 | A conditional edge **from inside the phase**
    to the escalation subgraph (§38), which defers to the Belt and **never
    returns to the supervisor**."* And, immediately above it: *"The six
    `add_edge` calls above are the complete Level 1 wiring; there is no
    conditional edge, no router function, and nothing for the supervisor to
    branch on."*
  * **§38:** the subgraph is reachable two ways — the validation stack's cap,
    and the `request_human_approval` tool — **both of which fire inside a
    phase.**
  * **S-F01's invariants:** *"`route_after_phase` was deleted on 2026-08-22 and
    MUST NOT be reinstated."*

**Why the literal reading is not a smaller mistake than it looks.** The deleted
router branched on `state["gate_attempts"]`, and `SupervisorState` has seven
fields and not that one — so it raised `KeyError` **on the gate-failure path
specifically**, the one path a supervisor-level branch would exist to serve.
Any Level 1 escalation branch needs the same counter and reaches for it in the
same place. §15 is explicit that `gate_attempts` *"is read only inside the
phase… and must not be added to `SupervisorState`"*, which is what makes the
Level 1 branch unbuildable rather than merely unwanted. This reaffirms §R2 and
CLAUDE.md §0.14 rather than reopening them.

**Pinned in `test_supervisor_graph.py`**, four ways, because the step's prompt
shows this is the thing most likely to come back: the builder has no branches;
neither `route_after_phase` nor `_gate_router` exists in the module; the module
reads `gate_attempts` off no state (checked by AST, not text — the module's own
docstring quotes the banned expression in order to forbid it, and a substring
check failed on that prose); and `escalate_node` reaches for none of
`gate_attempts` / `_missing_fields` / `phase_inputs`.

---

### AA2 — `Command.PARENT` survives S-F10's execution site. Verified, not assumed.

**This was a real open question and the answer decides whether AA1 is
buildable at all.**

§0.17 makes the escalation hop **the only use of `Command.PARENT` in this
architecture**, and `Command.PARENT` is documented against a subgraph added to
the parent **as a node**. But S-F10 requires the opposite shape: each phase
subgraph is invoked **inside** the parent's uniquely-named node function, so the
input mapper can run at the boundary. If the hop did not cross that boundary,
§38's escalation and §9's mapper placement would be in direct conflict and one
of them would have to give.

**Tested against the pinned langgraph 1.2.11, both shapes, before the topology
was written.** It works. A `Command(graph=Command.PARENT, goto="escalate")`
raised inside a subgraph invoked via `await subgraph.ainvoke(...)` propagates as
a `ParentCommand` exception out of the call, through the parent's node function,
and is caught by the parent's task runner (`pregel/_retry.py`), which rewrites
its namespace and dispatches to `escalate`. **No spec gap; the two sections are
compatible.**

**One consequence is load-bearing and must survive stage 7:** because the hop is
an exception, **the phase node function's code after the subgraph invoke does
not run.** The output mapper is therefore skipped on an escalation — which is
correct, since an escalated phase did not pass its gate and must not write a
gate document, and it is correct *by accident of mechanism* rather than by an
explicit branch. `test_command_parent_reaches_the_escalation_node` asserts the
skip, so a LangGraph version bump that changed it would fail loudly rather than
start writing gate documents for escalated phases.

---

### AA3 — The supervisor is the target; it is not yet the runtime

**Ruled: `build_supervisor()` is built, tested and NOT wired to the routes.
`get_graph()` continues to return the one-turn parent step 4.2 shipped.**

§15's justification for static edges rests on a precondition it states plainly:
**a phase subgraph reaches `END` only through `gate_apply`, which runs only
after Belt approval, so reaching `END` MEANS the gate passed.**

**That precondition is false today.** `gate_review` does not raise `interrupt()`
until stage 7, so the Define subgraph runs straight through to `END` on every
invoke and `END` means only "the graph ran" (Z2). Wire the DMAIC chain to live
traffic now and **one `/ask` turn would run Define, then Measure, then
Analyse** — the entire sequence in a single Belt turn, which is precisely the
defect the procedure's Part 3 ordering note records against the v1 graph and
which step 4.2 existed to remove.

So 4.3 follows **4.1's precedent**: build the structure, test it, route no
traffic to it. The alternative shapes were both rejected —

| Rejected | Why |
|---|---|
| Swap the runtime now and accept the chained run | Breaks `/ask` for every case, to no benefit; the topology is verifiable without it |
| Bring `interrupt()` forward to make the chain safe | That is stage 7, and an `interrupt()` with no `/gate/approve` and `/gate/reject` resume routes (§49) halts every turn with nothing able to resume it |

**The swap trigger is stated in code, not left to memory:** when `gate_review`
raises `interrupt()`, `get_graph` returns `build_supervisor()` and the node is
renamed `define_phase` → `define`. Both functions live in `core/graph.py` so
the swap cannot be made in one and missed in the other, and
`test_get_graph_is_still_the_one_turn_parent` **fails if it happens early**.

**The node keeps the name `define_phase` deliberately.** Renaming it to the
supervisor's `define` now would change every subgraph's `checkpoint_ns` from
`define_phase:{task}` to `define:{task}`, orphaning the checkpoints written
since 4.2. It costs nothing today — the input mapper rebuilds child state on
every invoke — but it is a rename to make once, with the swap, rather than
twice.

---

### AA4 — Two smaller findings, recorded so they are not rediscovered

**`escalate -> END` is absent from `get_graph()`'s drawing and present in the
wiring.** `CompiledStateGraph.get_graph()` omits edges out of nodes not
reachable from `START`, and nothing reaches `escalate` until stage 7 raises the
`Command`. Verified as a general LangGraph behaviour, not a quirk of this graph.
The topology tests therefore read `supervisor_builder()` — the uncompiled
builder — and one test asserts the edge is *absent from the drawing*, so that
when something does reach escalation it fails and forces a behavioural test in
its place.

**The `_subgraph(phase)` rename dropped a guard, and it was caught by the 4.2
tests rather than by review.** Step 4.2's node read `state["current_phase"]` and
raised `PhaseNotWired` for the four unbuilt phases; generalising the node into a
`phase_node(phase)` factory closed over the phase instead, so a case sitting in
Measure would have been coached as Define. Restored as an explicit check against
`WIRED_PHASES` before the mapper runs, so the four still surface as **501** and
not as a 500 from inside `new_phase_state`'s identity assertion.

---

## Part AB — Step 4.4: one builder, five phases, and the brief that was about to go empty (2026-09-02)

**Procedure step 4.4**, the remaining four phase subgraphs. Reference §12, §13,
§14, §15, §34; **§58.11 — S-F02**. Three decisions and one defect caught before
it shipped. **WATCH 17 closes here**: all five phases are wired and the four
501s are gone.

---

### AB1 — One parameterised builder, extracted; not five copies, and not four importing Define's

**Ruled: `build_phase_subgraph` moves out of `phases/define/graph.py` into
`phases/subgraph_common.py`, and the five node bodies into
`phases/nodes_common.py`. Each `phases/{phase}/graph.py` re-exports the builder;
each `phases/{phase}/nodes.py` keeps five real module-level `async def`s that
delegate.**

§12 is singular about this — *"the subgraph builder takes the phase as a
parameter"* — and step 4.4's own words are *"same five-node structure, **built
from the parameterised builder**"*. Step 4.1 had put that builder inside
Define's module, where it refused every other phase; 4.4 is the step that makes
the parameter mean something.

**Three shapes were available and two were rejected:**

| Shape | Why not |
|---|---|
| **Copy the builder and the five node bodies into each phase** | Five topologies that must agree by hand. §12's *"identical node-name sets"* becomes a convention rather than a fact, and the live rules inside the bodies — §47's `step_log` key format, §34's do-not-validate-a-coaching-turn, the WATCH 7 seam — end up enforced in five places to be kept in step manually. **A rule enforced in four of five places is not enforced** |
| **The four import Define's builder** | Worse than duplication. It makes Define structurally special and puts four phases' topology behind one phase's module — the coupling §12's *"no subgraph imports another subgraph's nodes"* is guarding against, even though a builder is not literally a node |
| **Extract to shared modules** ✅ | Every phase is a peer of every other; one copy of each rule |

**The per-phase `nodes.py` files keep five real `async def`s, and that is
deliberate rather than lazy.** §14 requires module-level async functions and the
test suite asserts `fn.__module__` is that phase's module. Generating them in a
factory would put `__module__` on the shared file, and satisfying the assertion
would then mean rewriting `__module__` to something it is not — a test passed by
making an attribute lie. The wrappers are two lines each.

**How the builder finds a phase's nodes:** `importlib.import_module(
f"backend.phases.{phase}.nodes")`, by name rather than through a registry dict.
A registry would make every phase's nodes a load-time dependency of every other,
which is the coupling §12 exists to prevent even though it is not the letter of
the rule. `test_no_subgraph_imports_another_subgraphs_nodes` greps all ten
per-phase modules for sibling imports.

**Both modules are outside Appendix B's file plan** — flagged, as
`phases/mappers_common.py` was at 3.3 and `core/conversation.py` at 4.2, and
Appendix B is updated in this commit so the list matches reality. All four share
one shape: **the plan enumerates `phases/{phase}/…` five times over, and the
five copies it implies are the thing that drifts.**

---

### AB2 — `get_graph(phase)`: five trivial graphs, not one graph with a branch from `START`

**Ruled: the runtime is one one-node graph per phase, node named
`{phase}_phase`.**

Until 4.4 only Define had a subgraph, so a single-node turn graph hardwired to
Define was the whole runtime. With all five built, that same graph would run
**Define's** subgraph for a Measure case — caught by the input mapper's identity
assertion (S-C02 B8), but as a 500 and only after the wrong phase was entered.

**The obvious alternative was one graph with five phase nodes and a conditional
edge from `START` on `current_phase`. Rejected, and for the same reason 4.3
rejected a Level 1 escalation branch** (Part AA1): that is a conditional edge at
Level 1, the shape §15 and S-F01's invariants forbid, and `route_after_phase`
was deleted for being exactly it. **Building one in scaffolding is how it comes
back** — scaffolding is where a banned pattern is easiest to justify and hardest
to notice later. Five trivial graphs cost nothing and forbid nothing.

**The node name carries the phase because S-F10 makes it load-bearing:**
checkpoint namespaces for subgraphs invoked inside node functions derive from
the node name, so a shared name would put every phase's subgraph state in one
namespace. **The `thread_id` is still one per project** (§16) — the five graphs
share a thread and therefore a parent checkpoint, which is correct: parent state
is the project's, not the phase's, and `messages` accumulating across phases is
what §16's one-thread rule means.

**The `_phase` suffix is kept** rather than renamed to the supervisor's bare
`define` / `measure`, for the reason AA3 gives: the rename moves every
subgraph's `checkpoint_ns`, so it is made once, with the Stage-7 swap.

---

### AB3 — The cross-phase brief was about to go empty, silently

**This is the defect 4.4 caught, and it would not have failed a test or raised
an error.**

**Define is the only phase whose orchestrator reads its own `phase_inputs`
alone.** It has no prior phase. Every other one reads upstream:

| Phase | Reads |
|---|---|
| Measure | Define — seeds `primary_metric_confirmed` / `secondary_metric_confirmed` from Define's `primary_metric` / `secondary_metric` |
| Analyse | Define + Measure — a cross-phase brief injected as a `SystemMessage` on **every** orchestrator call |
| Improve | Define + Measure + Analyse — same |
| Control | every prior phase — same |

The 4.2 seam passed `phase_inputs = {phase: draft}`, which is all a Define-only
runtime needed. Extended unchanged to five phases, **every brief would have
resolved to `{}` and every upstream fact would have vanished from the prompt** —
Measure coaching without Define's metric, Analyse without Measure's baseline —
with no exception anywhere, because each reader is a `.get(...) or {}` with a
labelled fallback. The coach would simply have been less informed, in a way
visible only by reading a transcript.

**Fixed:** `config["configurable"]["v1_phase_inputs"]` now carries **every**
phase's `structured` from the case document, and `to_v1_state` overlays the
current phase with `draft` — the live accumulator, which is newer than the case
document's copy. `gateway/routes.py` is outside the step's `Touches` and was
edited anyway; flagged here, as `core/checkpointer.py` was at 4.2.

**A rename went with it.** Inbound and outbound had both become `v1_artifacts`
meaning different things — inbound "every phase's stored inputs", outbound "this
turn's draft for this phase". The outbound key is now **`v1_draft`**
(`core/graph.py`, `core/conversation.py`'s `_TRANSPORT_KEYS`,
`gateway/routes.py`). Two names for two things, which is the rule §10.5 states
for `case_id` and `artifacts` and which applies with more force to a transport
key nobody is looking at.

---

### AB4 — What the parameterisation must NOT flatten

**§28's per-phase retrieval strategy is a real difference and is carried, not
averaged.** Analyse plans **multi-hop** — root-cause validation is layered — and
the other four are single-hop. It rides on the stub `coaching_plan` and **is
read by nothing yet**; it is there because `CoachingPlan.retrieval_strategy`
selects the executor's entire retrieval path at stage 6, and because a shared
builder is exactly the place a genuine per-phase fact gets quietly lost.
`test_analyse_is_the_one_phase_planning_multi_hop` pins all five values.

**The four gates beyond Define are inert for the same reason Define's is**
(WATCH 7): each `validate_{phase}` requires its §39.x v2 names and its
orchestrator emits the v1 ones. 4.4 wires them; it does not open them.

**`test_define_graph.py` became `test_phase_subgraphs.py`**, parameterised over
all five — 133 tests where there were 34. Every assertion in it was already
generic; only the parameterisation is new. The Done-when's own test asserts the
five node-name sets are identical **to each other**, which five separate checks
against a constant would not quite establish.

---

## Part AC — Step 5.2: the three `rag_lookup_*` tools, G-14 closed, and a citation that was never buildable (2026-09-03)

**Procedure step 5.2.** Reference §24 (the three tools), §25 (multi-query +
RRF), §23 (index schemas), §27 (failure semantics); **S-F14, S-F15, S-F16,
S-F17, S-C19**. Verify method `live-run`, and the live run is what makes AC3
part of this record rather than a later bug report.

---

### AC1 — G-14 CLOSED: the `QueryVariants` schema

**Group C — a schema named but never defined — not a Group A founder ruling**,
so it is resolvable under CONTINUITY's Standing Reasoning Protocol. §21's
mapping table and §25 both name `QueryVariants`; neither defines it. G-14 lists
exactly three undecided points and all three are ruled.

**1. One field, `variants: list[str]`.** A `rationale` or `strategy` field was
considered and rejected: generated on every retrieval, read by nothing, paid for
in tokens on the hot path.

**2. The original query is NOT in the schema, and is always searched anyway.**
This is the substantive ruling. The Belt's own phrasing is the highest-signal
formulation in the set and **must not be at the mercy of a generation call** — a
model that paraphrases badly, or whose variants all drift the same way, would
lose it entirely. `run_multi_query` therefore runs it as **ranked list zero,
unconditionally**, and the model's job is purely to add alternatives. Including
it in the schema would also let the model spend one of its three-to-five slots
restating what it was handed.

> **Consequence worth naming: the fan-out is `1 + len(variants)`, so 4–6 lists
> reach RRF, not 3–5.** The original's list is one vote among them and is
> **deliberately not weighted higher** — RRF's whole premise is that agreement
> across phrasings is the signal, and privileging one phrasing would undo it.

**3. Count model-chosen, bounded 3–5, enforced by the schema.** §25 says "3–5",
which is a range and not a number. Some queries have three natural rephrasings
and some have five; forcing exactly five produces padding, and padding produces
near-duplicate lists that inflate one document's fused score **without adding
evidence**. `min_length` / `max_length` on the field make a violation a parse
failure at the boundary rather than a silent narrowing deeper in.

**File: `knowledge/fusion.py`** — S-C19 sanctions either that or
`tool_args.py`, and fusion.py keeps variant generation and fusion together,
which is the one concern §25's encapsulation rule describes.

---

### AC2 — What was built, and the two classes that stay banned

**`knowledge/fusion.py`** holds `reciprocal_rank_fusion` (S-F17, k=60),
`QueryVariants`, `generate_variants` and `run_multi_query`. **`knowledge/
tools.py`** is rewritten as the three `rag_lookup_*` tools; the three
`search_improve_*` names are retired and `grep-absence` returns **zero** for
all three literal strings.

| Decision | Why |
|---|---|
| **Custom RRF, not `EnsembleRetriever`** | Two independent reasons (§25): both it and `MultiQueryRetriever` moved to `langchain_classic` and are not importable; and `EnsembleRetriever` fuses **different retriever sources**, where ours is **same-index multi-query** — N phrasings against one index. No LangChain 1.x class covers that, which is why LangChain's own rag-fusion template is custom |
| **`AzureSearch` with the filter at call time, not `AzureAISearchRetriever`** | §24's ratified rejection: the latter takes `filters` at *construction*, which forces per-call instantiation once the filter carries a dynamic `phase` and throws away the cached singleton. Re-examined 2026-08-21; no advantage found |
| **`response_format="content_and_artifact"`** | S-F14/15/16 all specify `list[Document]` as the output, but a `@tool` must hand the *model* readable text. Content carries the passages plus `source_file` / `page_number`; the artifact is the `list[Document]` the specs name, available for `CoachingResponse.citations` at 6.2 without the model re-transcribing it. One return, both readings |
| **`PER_VARIANT_K = 10`, sliced after fusion** | Fetching only `top_k` per variant would starve RRF of the lower-ranked agreements that are the entire signal it reads |

**Written against the LIVE index schema, not the target one** (§23, blocked on
step 9.1): `rag_lookup_evidence` takes **no `order_by` and no `phase` filter` —
`improve_evidence_index` has neither field as a top-level yet, both being inside
the non-sortable `metadata` blob; and `rag_lookup_case_history` uses
**`embedding`**, the live vector-field name on the one index that is not
`content_vector`. Per-tool local knowledge of that name is what keeps the
asymmetry safe (§23) — no shared code hides it, so nothing fails silently on it.

---

### AC3 — The citation §50 requires was never buildable, and only the live run could find it

**`search_knowledge` projected four metadata fields that do not exist on the
index.** It read `source`, `tool_name`, `phase` and `section_title`. The live
keys on `improve_knowledge_index_v3` are:

    char_count · id · page_number · phase_relevance · source_file

So **every one of those four came back as `""`, on every call, forever** — and
`.get(key, "")`'s default is exactly what made it silent. No exception, no log,
a well-formed result dict with four empty strings in it.

**The cost is not cosmetic.** §50 requires retrieval citations to surface
`source_file` and `page_number` — *"this came from page 47 of the BB eBook"* —
and **`page_number` was not projected at all**, so a checkable citation was
unbuildable from this return shape. The v1 tool's `[{tool_name or
section_title}]` label had also been rendering empty since it was written.

**`phase_relevance` is the filter field, never `phase`** (§7.2, §24) — the same
confusion that produced the original filter bug §27 exists to prevent. The
filter itself was correct; only the projection back out was wrong, which is why
retrieval "worked" and nobody noticed.

Corrected to project `id`, `content`, `source_file`, `page_number`,
`phase_relevance`. Citations now render:

    [Methodology · BB_LSS_ebook, PDF page 54] …

**"PDF page", per WATCH 5** — `page_number` is the PDF index and the printed
number is piecewise-offset, so "page 54" alone would send the Belt to the wrong
place.

> **This is the second consecutive step where the verify method earned its
> keep.** 5.1's mutations proved its tests could fail; 5.2's `live-run` found a
> defect that a green unit suite, a passing type check and a working retrieval
> path had all been consistent with. `retriever.py` and `core/prompts.py` are
> outside 5.2's `Touches` and were edited anyway — flagged, as at 4.2 and 4.4.

---

### AC4 — Live-run evidence

```
rag_lookup_methodology(phase='define')  -> 6 docs
  define  · BB_LSS_ebook · PDF page 54      general · BB_LSS_ebook · PDF page 233
  define  · pages 53, 51, 83, 46
  distinct phase_relevance: ['define', 'general']   <- the OR clause binds

rag_lookup_methodology(phase='control') -> phase_relevance: ['control']
                                           <- the filter binds PER PHASE
rag_lookup_evidence(case_id='IMPR-2026-E9D') -> 1 doc, test_sipoc.png
```

**The two zero-result calls were checked rather than assumed**, which is the
§27 distinction 5.1 spent itself on: `improve_case_index` holds **0
documents** — consistent with §23's note that it is empty pending the
`embedding` → `content_vector` reindex — and the single evidence document
belongs to `E9D`, so querying `0CB` correctly matched nothing. Both are genuine
empties, not masked failures.

---

### AC5 — One test was arithmetically false, and failed

`test_a_large_k_is_what_makes_that_possible` originally claimed that at `k=1`
one first-place beats three second-places. **It does not:** 3 × ½ = 1.5 > 1/1.
Rebuilt on a case that genuinely flips — first-once versus third-twice, `a` at
k=1 and `b` at k=60 — with a note in the test that this arithmetic is not
eyeballable. Recorded because the failure mode is the one this project keeps
naming: an assertion that reads as obviously true, written without checking,
would have passed for the wrong reason had the numbers happened to line up.

---

## Part AD — Step 5.3: the twenty computation tools, and why their scalar inputs are strings (2026-09-03)

**Procedure step 5.3.** Reference §30 (per-phase binding), §31 (arg schemas),
§7 (the typing law); **§69 — S-F37–S-F56** for the twenty interfaces and
**§60.6 — S-F24** for the EARS behaviours binding on all of them.

**No SPEC-GAP moves here.** G-25 — *"the 20 computation tools: no signature, no
`args_schema`, no return shape for any of them"* — was **RESOLVED at spec level
on 2026-08-26 by §69** and already sits in §66.6. This step builds the code that
section specified; the register is unchanged, and that is the correct outcome
rather than an omission.

    Define 1 · Measure 8 · Analyse 5 · Improve 1 · Control 5  =  20

---

### AD1 — Scalar inputs are `str` + `_num()`, not `float`. This is the design call.

**Ruled: every scalar a Belt might have written as prose is typed `str` in
`tool_args.py` and parsed by `_num()` in `computation.py`. Structured
collections stay typed lists.**

Two ratified behaviours force it, and `float` satisfies neither:

  * **B2** — *"parse what it needs out of the string at the point of use, since
    every captured field is a `str`"*. §7's typing law makes every captured
    field a string. What actually arrives where §69 writes `mean` is
    `"12.3% invoice error rate, measured over Q2 2026"`.
  * **B3** — *"unable to parse its input, return a clear reformatting request to
    the Belt rather than **raising** or guessing"*.

**Declaring `mean: float` would coerce `"12.3"` happily and then RAISE a
`ValidationError` on the prose** — the exact behaviour B3 forbids, at a layer
inside Pydantic that the tool cannot intercept to phrase a question. The Belt
would get a tool-call failure; what B3 requires is *"I could not find a number
in the process mean — you wrote 'about ten-ish'. Could you give me just the
figure?"*

**The split is "prose the Belt typed" versus "a table the coach assembled".**
`subgroups`, `contingency_table`, `x_values` and the rest stay `list[...]`: they
are built by the coach from data it has read, not lifted from a captured-field
sentence, and a malformed one is a genuine call error that Pydantic *should*
reject. What those collections need instead is **methodology** checking — at
least two RTY steps, expected cell counts ≥ 5, equal and constant subgroup
sizes — and §69.1 is explicit that *"preconditions are business and methodology
preconditions… they are NOT argument validation"*. So those live in the tools
and return requests too.

> **One internal exception type, never crossing a boundary.** `_num()` raises
> `_NeedsReformatting`, which every tool converts to a `{"reformatting_request":
> …}` result. `test_no_tool_raises_on_unparseable_input` sweeps all twenty to
> confirm it never escapes — B3 says the Belt gets a question, not a stack
> trace.

---

### AD2 — Three per-tool rulings worth naming

**`post_improvement_cpk` is its own `@tool`, not `calculate_cpk(mode="post")`.**
S-F24 **B4** bans parameterised grouping and §30 binds tools per phase, so the
mode argument is not available even though the formula is identical. §69.6
permits the shared private helper explicitly — *"The two MAY share a helper;
they are two `@tool`s"* — and they share `_cpk_values`. **The difference is the
contract, not the arithmetic**: `post_improvement_cpk` additionally takes
`baseline_cpk` and returns `improvement_delta`, which is the number Control's
`post_improvement_metrics` is graded against, not the new Cpk alone. A test
asserts the two agree on identical data, so the shared helper cannot drift while
they stay two tools.

**A single measurement per period gets sent to I-MR, by name.** **B7**: *"a Belt
SHALL NOT be coached into inventing subgroups to fit a batch chart."*
`xbar_r_chart_limits` given subgroups of size 1 returns a request naming I-MR
rather than computing limits that would look authoritative and mean nothing.
The rule is enforced at the tool, not left to the coaching prompt, because the
prompt is the layer that fails silently.

**`pearson_correlation` below n=10 warns and still answers.** S-F49: *"the tool
returns a warning, not a suppressed result — the Belt decides."* Suppressing it
would have the tool overrule the Belt on a methodology floor that is a guideline,
not arithmetic. The result carries `sample_size_warning` naming the floor.

---

### AD3 — The expected answers are anchored independently, and mutation-proven

**All 67 tests passed on the first run**, which is precisely when this project's
standing lesson applies: *a check that cannot fail is worse than no check,
because it is recorded as evidence.*

**No expectation is a value read back from the code.** Each is one of:

  * a figure a Black Belt recognises on sight — DPMO 3.4 is six sigma, 66,807 is
    three, and p=0.5 at ±5% needs **385**;
  * arithmetic checkable by hand in the test docstring — a process centred at 10
    with σ=1 between limits of 7 and 13 has Cpk of exactly 1.0, and RTY for five
    steps at 95% is 0.95⁵ = 0.7738, not 0.95;
  * a value computed from `scipy` *in the test*, where the tool's job is to route
    to the right standard test rather than to reimplement it.

**Then the suite was proved able to fail — eight mutations of the code under
test, eight caught:**

| Mutation | Caught by |
|---|---|
| `SIGMA_SHIFT` 1.5 → 0.0 | the 3.4-DPMO-is-six-sigma case |
| Cpk takes the best side, not the worst | the off-centre process case |
| RTY sums step yields instead of multiplying | the hidden-factory case |
| Shewhart A2 for n=5 mistyped 0.577 → 0.677 | the X̄-R known answer |
| `_num` **raises** instead of asking | the B3 sweep |
| chi-square skips the expected-count ≥ 5 check | the small-sample case |
| p-chart returns one flat limit | the varying-limits case |
| `post_improvement_cpk` drops the delta | the delta case |

**The trusted-source rule differs for this file, and §69.1 says so.** These are
AIAG MSA-4 for GR&R, Shewhart's constant tables, the standard hypothesis tests
and the 1.5σ long-term-shift convention — **decades-old standards that do not
drift the way a package API does**. The check is *"matches the standard method
as taught in the ingested BB eBook"*, not `/verify-current-version`; applying a
package-version check to a Shewhart constant table would be a category error.
`scipy` and `numpy` are pinned, declared dependencies and are used for the
reference distributions rather than hand-rolled approximations of them.

---

### AD4 — What this step deliberately did not build

**`COMPUTATION_TOOLS_BY_PHASE` is absent.** The per-phase binding is **step
5.4's** — its own `Touches` row names that constant and its *Done when* asserts
the totals 8 / 15 / 12 / 8 / 12 against the universal seven, with no phase over
16. `computation.py` exposes a flat `COMPUTATION_TOOLS` list of the twenty in
§60.6's inventory order; 5.4 partitions it.

**Measure has no chart-limit tool, and that is a specified absence** (§69.7),
not an oversight in the inventory: `stability_assessment` is coached as a
visual read, and the chart-limit tools belong to Control.

---

## Part AE — Step 5.4: the per-phase binding, and the flat list that now derives from it (2026-09-03)

**Procedure step 5.4.** Reference **§30** (tool sets are per phase, not
universal; the 16-tool ceiling), **§29.2** (the universal seven), **§60.6 —
S-F24** (the inventory, by phase). **Stage 5 closes here.**

**No SPEC-GAP moves.** §30's binding table has been ratified since the reference
was signed off; this step is the code for it, and G-25 stays resolved where §69
left it (Part AD).

| Phase | Universal | Computation | Total |
|---|---|---|---|
| Define | 7 | 1 | **8** |
| Measure | 7 | 8 | **15** |
| Analyse | 7 | 5 | **12** |
| Improve | 7 | 1 | **8** |
| Control | 7 | 5 | **12** |

---

### AE1 — `COMPUTATION_TOOLS_BY_PHASE` is §30's table, expressed as the partition itself

**Ruled: the binding is a `dict[str, list[BaseTool]]` keyed by `PHASE_ORDER`'s
five names, holding §60.6's inventory order within each phase.** The executor
composes a phase's tools as `UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]`
(§18) — the form §30, `CLAUDE.md` and `ARCHITECTURE.md` all already write.

**The keys are spelled literally rather than imported.** `knowledge/` does not
depend on `phases/`, and adding that edge to reach a five-element tuple of
strings would be the wrong trade. `test_the_binding_keys_are_the_five_dmaic_phases`
asserts the two agree, so the coupling is a test's rather than an import's.

---

### AE2 — `COMPUTATION_TOOLS` now DERIVES from the partition. This kills a drift point.

**Ruled: the flat list of twenty is a comprehension over
`COMPUTATION_TOOLS_BY_PHASE.values()`, not a second literal list beside it.**

This is the one place step 5.4 edited step 5.3's work, and the reason is
specific. **5.3's flat list already carried the phase split — as comments**
(`# Measure (8)`, `# Control (5)`). Two literals, one of them a comment, both
claiming which tool belongs to which phase: the classic drift point, where an
edit to one is not an edit to the other and nothing fails. Making the grouping
structural rather than commentary leaves **one** statement of the partition.
Order and contents are unchanged, so 5.3's `test_exactly_twenty_tools` still
holds unmodified — which is the evidence that this was a re-expression and not a
change.

---

### AE3 — `UNIVERSAL_TOOL_COUNT = 7` and `PHASE_TOOL_CEILING = 16` are named, not written into assertions

**Ruled: both are module constants in `computation.py`, and both are additions
beyond the constant step 5.4's `Touches` row names.**

The step's *Done when* is *"the per-phase totals 8 / 15 / 12 / 8 / 12, and no
phase exceeds 16"* — **neither number is expressible from the partition alone.**
A total is universal + computation, and the ceiling applies to that total, so a
test written against the subsets alone would assert something §30 does not say.
The alternative was a bare `7` and a bare `16` inside test assertions, which is
the same fact with nowhere to hang its reference.

> **The 7 is owed a check it cannot yet have.** Only three of the universal
> seven exist — `knowledge/tools.py`'s `RAG_LOOKUP_TOOLS`, from step 5.2.
> `propose_template`, `propose_diagram`, `check_gate_status` and
> `request_human_approval` land with the executor at **stage 6**. So
> `UNIVERSAL_TOOL_COUNT`'s docstring records the obligation — **when stage 6
> assembles `UNIVERSAL_TOOLS`, that list must assert its own length against this
> constant** — and `test_the_universal_seven_is_seven` records the arithmetic
> (7 total, 3 built, 4 owed) so the stage-6 commit that adds them has to come
> back here rather than quietly making the totals above wrong.

**The ceiling test asserts the headroom too**, not just `≤ 16`: the maximum is
Measure's 15. A binding sitting exactly on 16 would pass a ceiling check while
leaving no room for §30's amendment process to be the thing that adds the
seventeenth tool.

---

### AE4 — The tests were mutation-checked, not merely run

Seven new tests, green on the first run — which by itself is evidence of
nothing. Three mutations of the binding, each caught by four or five of them:

| Mutation | Caught by |
|---|---|
| `calculate_cpk` moved Measure → Define | totals · ceiling · partition · names |
| `imr_chart_limits` bound to Measure *as well as* Control | those four **and** the chart-limit test |
| Define padded past the ceiling | totals · ceiling · partition · names |

**`test_measure_binds_no_chart_limit_tool` exists for the second row.** §69.7 and
Part AD4 record Measure's absent chart-limit tool as a *specified absence* —
`stability_assessment` is coached as a visual read. An editor moving a chart tool
into Measure "to help with stability" is a plausible, well-meant edit that no
count-based test would catch, because Measure would still hold 8 if one were
swapped in. The test names the absence so it cannot be undone silently.

**`EXPECTED_TOTALS` is written out rather than computed from the subsets.** A
total derived from the thing it is checking agrees with any partition at all.

---

## Part AF — Step 6.1: the planner becomes real, and a stale block had to move first (2026-09-03)

**Procedure step 6.1.** Reference **§17** (the planner/executor contract),
**§58.4 — S-C04** (`CoachingPlan`), **§20**; CLAUDE.md **§4.6** (structured
output scoped by call type), **§4.7** (temperature).

**No SPEC-GAP closes here, and one deliberately stays open** — see AF4.

---

### AF1 — The block came first, and it was ours

**Step 6.1's first substantive line was refused by the drift guard.**
`pattern-2-with-structured-output` blocked the builder-style call in
`phases/nodes_common.py` — the mechanism §4.6's mapping table names for this
exact site in row 1: *"Phase planner | Plain LLM call | `CoachingPlan` |
`with_structured_output`"*.

**The step stopped rather than routing around it.** Three ways round were
available and all three were wrong: `git commit --no-verify` (records the drift
instead of fixing it), relocating the call to an already-excluded directory
(`knowledge/**` — evasion by path, and S-C04 puts the planner in `phases/`), or
`response_format=` (does not apply — §17/S-C04: *"a plain model invocation, not
an agent"*, and §17 forbids the planner dispatching to tools at all, so there is
no loop to attach it to).

**Resolved by governance commit `9fce8fc`, ahead of the code.** CLAUDE.md §18:
*"Never amend a rule in passing while making a feature change."* The exclusion
is **single-file, not `phases/`-wide** — a directory exclusion would also
un-block `phases/**/nodes.py`, which the registry names as *"the case this
pattern exists for"*, one step before 6.2 builds the executor there with
`create_agent`. `pattern-8-bind-tools-in-phase-executor` still covers that
construction inside the same file, which is what makes the single-file scope
safe. **WATCH 24 closed in the same commit** — `validation/**` needed the
identical §4.6 reasoning, forward-declared and inert until stage 7.

> **This is the fourth site where the same over-block has surfaced** (after
> `orchestrate.py`, `validate.py`, then `knowledge/**` and `middleware/**` at
> 5.2). The registry's own comment named the cause in advance: *"the exclusion
> list simply predated the files."* Each time it has cost a stop-and-authorise
> cycle. The remaining un-excluded §4.6 site is `gate_apply`'s policy advisory,
> which lands in `phases/nodes_common.py` — now excluded, so it will not recur
> there.

---

### AF2 — The plan is produced only on the executor-bound path

**Ruled: `_plan_turn` is called when the planner routes to `executor`, and not
otherwise.**

A plan is consumed by the executor and by nothing else. Producing one on the way
to `validation_stack` would spend a `planner`-role premium call on a plan no
node reads, and put a `focus_field` in the LangSmith trace that never coached
anything — a trace that reads as richer while describing less.

**S-C04 B3 is not violated by this.** B3 governs what a NEW plan does to the
previous one — *"overwrite the previous one entirely; plans SHALL NOT
accumulate"* — not that a plan must be produced on every planner visit. On the
gate and close paths the previous plan simply stands.

**Consequence for cost, which is the reason it is worth ruling:** the planner
node runs twice per Belt turn (the cycle returns through it), and this makes
exactly one premium call per turn rather than two.

---

### AF3 — What the executor "consumes" at 6.1, stated rather than implied

**The executor reads `coaching_plan` and records it in `step_log`. It does not
steer the coach by `focus_field`, and it cannot yet.**

The body still delegates to the v1 `orchestrate_{phase}`, which takes no
focus-field parameter, and **Route A forbids touching those five files** — they
carry the v1 names to step 11.1 and are deleted there, not migrated (Part X).
Full consumption is **6.2's**, where `create_agent(...)` replaces the body and
the plan enters the system prompt.

**What §17 requires is nonetheless true here:** the executor decides no strategy
of its own. It never picks a field, never chooses a retrieval mode and never
routes. Recording the plan it ran under is what makes the audit trail link a
turn to the plan that produced it, which is the half that was buildable now.

> **The field ledger reads as entirely missing until 6.2, by the same ruling.**
> The planner reads `artifacts` (§17), and WATCH 7 Route A keeps `artifacts`
> empty for every phase while the v1 orchestrator writes v1 names into `draft`.
> So the planner will keep choosing the first uncoached field. **That is the
> seam, not a planner defect** — and handing it `draft` instead would put v1
> names in front of a planner whose `focus_field` must be a §39.x name.

---

### AF4 — G-01 stays open. DP1 was not invented.

**Ruled: the routing predicate is unchanged. 6.1 is the split plus the real
planner, and nothing else.**

The temptation was specific and would have looked like progress: the planner now
returns a model-authored `next_action`, so routing could have read a `goto` out
of it. **That would close a founder-owned gap by implementation, and would do it
by misreading a field.** S-C04 defines `next_action` as the coaching move —
*"ask, challenge, show an example, run a computation"* — not a routing verb.
S-F13 marks the predicate *"to be designed with founder"*.

`test_planner_does_not_read_a_goto_out_of_next_action` pins it: a plan whose
`next_action` is literally `"gate"` must still route by the placeholder
predicate. **The test exists because the mistake is attractive**, not because
anyone made it.

---

### AF5 — A live bug the typed plan exposed in `validation_stack`

**`validation_stack` was routing on the plan's `next_action`**, testing it
against `"gate"`.

That worked only because 4.4's stub dict put the ROUTING verb in that key. The
moment `next_action` became S-C04's coaching move, the node was reading a field
that no longer means what it was testing — and because the plan is now a
Pydantic model, `.get()` on it raised `AttributeError` rather than quietly
routing wrong. **Eleven tests caught it; a dict-typed plan would have let it
pass while sending gate submissions down the coaching path.**

**Fixed by reading `entry_mode(config)`** — the same per-run intent the planner
routes from, so the two nodes cannot disagree about what kind of turn this is.

> **This is the argument for S-C04 being a Pydantic model rather than a dict,
> demonstrated rather than asserted.** S-C04 gives the reason as
> `retrieval_strategy`'s `Literal`; the failure that actually surfaced was a
> reader of a *renamed* field. A dict would have made it silent.

---

### AF6 — `conftest.py`, and stubbing `get_llm` rather than `_plan_turn`

**Ruled: the planner's model is stubbed at the factory, in a shared
`tests/conftest.py`.**

Patching `_plan_turn` would skip the code under test — the prompt build, the
structured-output wiring and the role choice would all go unexercised while the
tests stayed green. Patching `get_llm` leaves all three live and replaces only
the network call, **and it lets the fixture assert the role and the schema**,
which is how §17's *"planner role, temp 0.1"* and B1's *"never by parsing JSON
from raw model text"* become checkable at all. **B1 cannot be asserted from the
returned plan**: a plan parsed out of raw text would look identical to one that
came through structured output. What distinguishes them is that the schema was
handed to the model, so the fixture records it.

Two modules need the stub — `test_phase_subgraphs.py` calls the node directly,
`test_turn_graph.py` drives it through the compiled graph — and it hangs off the
`wired` fixture there rather than being requested by eleven tests individually.

---

### AF7 — The trace-check, and what it was run against

**Verify method `trace-check`, run live** against Azure OpenAI with
`LANGCHAIN_TRACING_V2=true`. The trace shows, in order:

```
step-6.1-trace-check-2bef29da        chain
  planner                            chain   <- the plan is this span's output
    RunnableSequence                 chain   <- the structured-output chain
      AzureChatOpenAI                llm
      RunnableLambda                 chain   <- the parse into CoachingPlan
  executor                           chain
    AzureChatOpenAI  x2              llm
  planner / validation_stack / gate_review / gate_apply
```

The `planner` span's output carries `Command(goto="executor",
update={"coaching_plan": {"focus_field": "business_case", "next_action": "ask
for it", "retrieval_strategy": "single_hop", "retrieval_hops": []}})` — **the
plan visible as the planner's output, which is the Done-when verbatim.**

**Run against the phase subgraph, not the parent graph.** Both spans the
Done-when names live inside the subgraph, and the subgraph compiles without a
checkpointer or store (§16) — so the check made no Azure Blob write against any
real case. The one premium call per turn ruled in AF2 is visible as the single
`AzureChatOpenAI` span under `planner`.

---

## Part AG — Step 6.2: the `create_agent` executor, and WATCH 7 closed (2026-09-03)

**Procedure step 6.2.** Reference **§18** (building the executor), **§20** /
**§58.5 — S-C05** (`CoachingResponse`), **§57.3 — S-F04** (the coach node),
**§29.2** (the universal seven), **§30**; CLAUDE.md **§4.4**, **§4.6**, **§6.3**,
**§6.4**, **§3.7**.

**WATCH 7 CLOSES HERE**, at exactly the step Route A named (Part X).

---

### AG1 — §16.3 was run BEFORE the code, and it is why the parameter is right

**Both names verified against the installed `langchain.agents.create_agent`,
not against this project's documents:** the signature carries `system_prompt`
and has **no** `prompt` parameter, so `prompt=` would raise `TypeError` at
construction. `tools`, `response_format` and `middleware` are all present.

`test_create_agent_signature_still_has_system_prompt_and_no_prompt` asserts
against the **library**, not against our call. That distinction is the point:
a test that only checked our own kwargs would keep passing if LangChain renamed
the parameter back, which is precisely the shape of the failure CLAUDE.md §0.10
records — `retries=` vs `max_retries=` sat inside the canonical block, the one
an implementer copies verbatim, from adoption until it was verified months
later.

**Tools go to `create_agent(tools=...)`, never onto the model.** §18: binding
onto a bare model bypasses all eight middlewares, silently.
`pattern-8-bind-tools-in-phase-executor` guards the source; a test guards the
behaviour; and a raw `grep -rn "bind_tools" backend/` returns zero.

---

### AG2 — WATCH 7 is closed by demonstration, not by assertion

**The v2 field writer now exists.** `fields_captured` on the `CoachingResponse`
is written into `artifacts` under the §39.1.2 names — which is what
`validate_{phase}` has been reading since the rename, and whose absence made
every phase's gate inert by ruling.

**The live-run is the evidence**, on one real coaching turn:

```
artifacts written by the v2 writer:
  baseline_estimate = 12% of invoices get sent back for correction, Q2 2026
  target_value      = under 5%
  target_date       = end of March 2027
  team              = Me, Ana from AP, and Bo from IT

empty case     : passed=False  missing=13/13
after one turn : passed=False  missing=9/13
all 13 coached : passed=True   missing=0/13
```

Those are the **v2** names, extracted from the Belt's prose by the coach and
read by the **real** `validate_define`. The two halves that had been written
against different vocabularies since the rename now meet.

**`draft` changed meaning, and the change is easy to miss.** It was the v1
accumulator; it is now S-F04's *"this turn's extraction"*, with `artifacts` as
the accumulation. Both are written by the executor, and neither field carries a
reducer — so the merge happens in the node or not at all.

**The five `orchestrate.py` are now dead code and were not touched.** The
delegation is gone from the executor and from the five `nodes.py` imports;
Route A deletes the modules at 11.1.

---

### AG3 — The live-run found a cap that could never fire

**CLAUDE.md §3.7 requires `GraphRecursionError` to be caught in the coach node
and turned into a partial answer** — *"a Belt mid-session never sees a stack
trace because the coach explored too broadly."* It was not, and worse:

**the agent inherited the route's `recursion_limit=50`**, which §16 calls the
backstop against a genuine infinite loop. An agent invoked inside a node takes
the parent invoke's config unless given its own, so §3.7's per-turn cap of
`2 × 5 + 1 = 11` **was not merely wrong — it was unreachable.**

That is the failure mode this register keeps naming, in its third form: after
§0.16's `remaining_steps` returning 10 forever and §0.14's `route_after_phase`,
here a cap that cannot fire is not a loose cap but a check recorded as evidence
while proving nothing.

**Both halves fixed:** `COACH_RECURSION_LIMIT = 11` is passed explicitly, and
the exception becomes a plain-language partial answer (§13 — the message names
no exception, no tool and no limit), with the turn still closing so
`turn_count` advances and the planner's predicate still terminates. The event
is logged as the monitoring signal §3.7 calls it.

**Found by running the thing, not by reading it.** No unit test would have
produced it: the stub never loops, and the subgraph path passes 50 and
completes. It surfaced only when a real turn explored too far.

---

### AG4 — Five universal tools, not seven, and the two absences are the spec's own

**Ruled with founder authorisation: bind five.**

`propose_template` and `propose_diagram` were **owed by step 5.2** — S-F19 and
S-F20 both say *"Procedure: step 5.2"*, and 5.2's prose covered only the three
`rag_lookup_*` tools. They were built here because the executor binds
`UNIVERSAL_TOOLS`, and because without `propose_diagram` the Define SIPOC the
UI already renders would have vanished the moment `create_agent` replaced the
v1 executor that emits it.

**The last two cannot exist yet by the spec's own assignments** —
`check_gate_status` is step 7.1 and needs `DMAICGateValidator` (7.1's
deliverable); `request_human_approval` is step 7.5 and needs the escalation
path. So the live per-phase totals are **6 / 13 / 10 / 6 / 10** against §30's
**8 / 15 / 12 / 8 / 12**. **§30 is not redefined**; the interim is asserted
separately and alongside it, so 7.1 and 7.5 must return to both. **WATCH 25.**

---

### AG5 — The founder ruling on what those two tools ARE

Recorded verbatim, because it is the scoping **G-29 and G-30** were waiting on:

> *"Agent Improve does not export documents. The assembled `{Phase}Output`
> shown on the UI is the record. `propose_diagram` returns structured JSON
> rendered by the UI (`renderSipocDiagram`, `render5W2HMindmap`).
> `propose_template` returns a `str` (S-F19 signature) that the coach presents
> inside its coaching message for the Belt to complete — no UI renderer, by
> design. Neither emits a file; both are coaching aids, not document
> generators."*

**This is why the narrow build is correct rather than provisional.** Neither
tool was designed here: `propose_template` uses the four types §29.2 names, and
`core/diagrams.py` **transcribes the two shapes `ui/index.html` already
renders**, read off the render functions. Inventing a type catalogue would have
closed a founder-owned gap by implementation — the mistake 6.1 declined to make
with G-01 and DP1.

**G-29 and G-30 stay OPEN in §66.** The ruling scopes what the tools are for;
formally closing a spec gap is a §56 amendment, not a build step's to make.
The ruling is carried in `knowledge/tools.py`'s section header, in
`propose_template`'s own docstring (§31 — the docstring is what someone editing
the tool reads, and what the model reads at call time), and in
`core/diagrams.py`'s header.

**The one wrinkle, checked rather than assumed:** the ruling's first phrasing
described both tools as returning JSON the UI renders. `grep` for a template
renderer in `ui/index.html` found none — no `renderTemplate`, no
`template_type` — and S-F19's ratified signature is `-> str`. The founder
confirmed: the coach presents the template inside its message, and the absence
of a renderer is by design. **No code changed on the looser reading.**

---

### AG6 — The coach prompts arrived early, and had to be compliant to arrive at all

**Step 6.6 owns `core/prompts.py`'s rewrite** (§22). `{PHASE}_COACH_PROMPT`
landed at 6.2 because `create_agent` cannot be constructed without a system
prompt — and because CLAUDE.md **§6.3** and **§6.4** make the memory-hierarchy
paragraph and the anti-hallucination guards **mandatory on every coach
prompt**. A thin placeholder would not have deferred a rule; it would have
violated one. Both blocks are present in all five and are asserted.

**6.6's own work is untouched:** deleting the v1 `ORCHESTRATOR_{PHASE}` /
`EXTRACTION_{PHASE}` / `KNOWLEDGE_INJECTION_TEMPLATE` families, and landing the
contradiction-check instruction in the five SKILL.md files.

**The per-turn half is composed in the node, not injected into `messages`.**
§19.1's `BeforeModelStateInjection` is the ratified home and lands at 6.3; until
then the executor composes the field ledger, the captured state, the case
framing and the plan's focus field into the system prompt — because §8.5 puts
project facts at the **top**, and appending them into `messages` after the
Belt's turn is the violation that rule exists to name. The agent is therefore
constructed per turn; 6.3 makes the prompt static and lets it be cached.

**Case framing was nearly dropped.** The v1 bridge carried `case_metadata` and
`current_user` on `config`; the first draft of the v2 prompt carried neither.
`belt_level` is load-bearing — §35's grader suppresses Black-Belt-only
methodology for a Green Belt — so a coach that does not know which Belt it is
talking to cannot honour a rule the grader will hold it to.
