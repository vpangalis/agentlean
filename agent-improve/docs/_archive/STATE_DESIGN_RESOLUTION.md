<!--
Review document: agent-improve/docs/STATE_DESIGN_RESOLUTION.md
Normalised: UTF-8 without BOM, LF line endings
Purpose: tracked review artefact for cross-session architectural reference
Added in: f44e5c7
-->

# State Design Resolution — All 15 Audit Findings

**Purpose:** Complete corrected state design for the refactored Agent Improve.
Claude Code reads this to update ARCHITECTURE.md, CLAUDE.md, and REFACTORING_AGENT_IMPROVE.md in one commit.

**Status key:** ✅ Confirmed by user | ❓ Needs user decision | 🔄 Depends on another finding

---

## SupervisorState — corrected schema

```python
class SupervisorState(TypedDict):
    messages: list[BaseMessage]       # conversation history (parent owns)
    history: list[str]                # node execution history
    case_id: str                      # canonical identifier — matches code + indexes (Finding 10)
    phase_index: int                  # current position in PHASE_ORDER
    current_phase: str                # PHASE_ORDER[phase_index]
    gate_passed: dict[str, bool]      # {"define": True, "measure": False, ...}
    final_output: Optional[dict]      # set when Control gate passes
```

Removed in this review:
- `dmaic_plan` — covered by Define's gate document in store (removed v2.2.7)
- `key_decisions` — covered by artifacts at gate passage (removed v2.2.7)
- `open_items` — blockers are validation failures; forward context is in gate documents (removed v2.2.7)
- `project_context` — no writer, no reader, content covered by case metadata + Define gate doc (removed v2.2.8)
- `project_id` — renamed to `case_id` to match all code and indexes (Finding 10)

---

## PhaseState — corrected schema

```python
class PhaseState(TypedDict):
    coaching_plan: dict[str, Any]     # planner output: focus_field, next_action, retrieval_strategy
    field_index: int                  # which field the planner is working on
    draft: dict[str, Any]             # working extraction — fields being coached
    artifacts: dict[str, Any]         # captured fields approved within this phase
    step_log: list[dict]              # audit trail — every action, validation, tool call
    belt_edits: dict[str, Any]        # Belt's corrections during gate review (renamed from feedback)
    turn_count: int                   # coaching turns in this phase
    final: dict[str, Any]             # approved gate document (changed from str to dict)
    gate_attempts: int                # validation retry counter, cap 3, resets on pass
    validator_feedback: list[dict]    # accumulated per-criterion feedback across retry attempts
    citations: list[dict]             # sources cited by coach during this phase
    uploads: list[dict]               # files Belt uploaded during this phase
```

---

## Finding resolutions

### Finding 1 — gate_attempts missing ✅ CONFIRMED

**Problem:** §1.7 and §3.5 mandate this field. Without it, the validation loop has no counter and reintroduces the v1 "attempts always reset to 0" bug.

**Resolution:** Add `gate_attempts: int` to PhaseState. Default 0. Incremented by validation node on each retry. Reset to 0 when gate passes. When >= 3, escalate to Belt. Per-phase (not supervisor level) because each phase has its own retry count.

### Finding 2 — gate_documents never written to store ✅ CONFIRMED

**Problem:** The store-mediated handoff depends on gate_apply writing the approved gate document, but this write was never specified.

**Resolution:** gate_apply writes TWO things after Belt approval:
1. Store: `store.put(("projects", pid, "artifacts"), phase_name, {all captured fields})`
2. PhaseState: `final = {same dict}` (for checkpoint crash recovery)

Physical blob path: `store/projects/IMPR-2026-E9D/artifacts/define.json`

Next phase planner reads: `store.get(("projects", pid, "artifacts"), "define")`

### Finding 6 — no accumulated validator feedback ✅ CONFIRMED

**Problem:** When coach retries after validation failure, it needs to know what failed previously to avoid repeating the same mistake.

**Resolution:** Add `validator_feedback: list[dict]` to PhaseState. Each failed attempt appends:
```python
{"attempt": 1, "layer": "grader", "criteria_failed": ["root_cause_validation"],
 "feedback": "does not reference statistical evidence", "timestamp": "..."}
```
Coach reads full list on retry. Resets to `[]` when gate passes.

Also rename existing `feedback` field to `belt_edits` — Belt's gate review corrections are a different kind of feedback than validation results.

### Finding 8 — citations and uploads missing ✅ CONFIRMED

**Problem:** Coach cites BB eBook sources and Belt uploads files. Neither is tracked in PhaseState, so the gate document can't show what evidence was used.

**Resolution:** Add both to PhaseState:
- `citations: list[dict]` — `{"source": "improve_knowledge_index", "page": 47, "content_summary": "...", "turn": 5}`
- `uploads: list[dict]` — `{"filename": "defect_data_q2.xlsx", "case_id": "...", "upload_turn": 3, "purpose": "baseline data"}`

Both included in gate document written to store at gate passage.

### Finding 9 — final typed as str, should be dict ✅ CONFIRMED (with Finding 2)

**Problem:** `final: str` contradicts the dict-not-str rule in §10.1. Gate document is structured data.

**Resolution:** Changed to `final: dict[str, Any]` in the schema above.

### Finding 3 — baseline is str everywhere, docs promise typed float ✅ CONFIRMED — Option B

**Problem:** §10.2 says "Measure reads Define's baseline metric as a typed float." Every baseline field is `str`.

**Resolution:** Option B — all captured fields are strings across the entire project. No exceptions. This is a project-wide design rule, not just a baseline decision.

**Design rule:** All captured fields are `str`. Computation tools parse at point of use. Gate documents show the Belt's exact words. §10.2 must be corrected to stop claiming typed floats.

**Rationale:** ~25 numeric fields across DMAIC. Option C (raw + value + unit) triples that to 75 fields — schema explosion. Parsing logic lives inside the 18 computation tools, each knows how to extract a number from a string. If parsing fails, the tool returns a clear error asking the Belt to reformat.

### Finding 4 — Control has no post_improvement_metric ✅ CONFIRMED

**Problem:** A DMAIC project that can't show the baseline shifted hasn't proved anything. eBook p681 requires "verify financial impact."

**Resolution:** Add three fields to Control's required gate fields:
- `post_improvement_metric: str` — measured value after improvement ("3.1% error rate")
- `improvement_delta: str` — change from baseline ("reduced from 12.3% to 3.1%")
- `financial_impact_verified: str` — quantified savings ("saves 35 hours/month rework, ~€4,200/month")

All strings per Finding 3 rule. Control grader rubric updated to check these exist and reference the Define/Measure baseline (cross-phase linkage — connects to Finding 5).

### Finding 5 — 7 of 21 rubric criteria have no field ✅ CONFIRMED — Option A for cross-phase, add simple fields for the rest

**Problem:** 7 rubric criteria have no corresponding field. Three fail because nothing links across phases.

**Resolution for cross-phase linkage (3 criteria):** Option A — explicit cross-reference fields. The coach captures the link as a structured dict. The grader checks mechanically: does the reference field exist in the referenced phase's gate document with that value? Deterministic, no LLM judgment needed for the linkage check itself.

Affected criteria:
- `causal_hypothesis` (Analyse):
  ```python
  causal_hypothesis = {
      "hypothesis": "Inadequate onboarding causes error spike in first 60 days",
      "references_phase": "measure",
      "references_field": "baseline_mean",
      "references_value": "12.3%"
  }
  ```
- `solution_linked_to_root_cause` (Improve):
  ```python
  solution_linked_to_root_cause = {
      "solution": "Structured 5-day onboarding programme",
      "references_phase": "analyse",
      "references_field": "root_cause_statement",
      "references_value": "Training gap — new staff 23% vs 4%"
  }
  ```
- `post_improvement_metric` (Control) — covered by Finding 4, but the grader also checks linkage:
  ```python
  post_improvement_metric = {
      "metric": "3.1% error rate",
      "references_phase": "measure",
      "references_field": "baseline_mean",
      "references_value": "12.3%"
  }
  ```

The grader reads the referenced phase's gate document from the store and verifies the referenced field and value exist. If they don't match, the grader fails the criterion with specific feedback: "references baseline_mean = 12.3% but Measure gate document shows baseline_mean = 15%."

**Rationale for Option A over B:** These are the highest-stakes linkage checks in DMAIC — a broken link means the project built on the wrong foundation. LLM-based reasoning (Option B) can fail when Belt terminology differs between phases ("high rework" vs "12.3% invoice error rate"). Deterministic field matching is more reliable for exactly these three checks.

**Resolution for missing simple fields (4 criteria):** Add the fields to the phase schemas:
- `baseline_sigma: str` (Measure) — calculated sigma level from baseline data
- `ruled_out_causes: str` (Analyse) — alternatives considered and rejected with rationale
- `handover_documented: str` (Control) — process owner accepting responsibility, named individual
- `problem_statement: str` (Define) — single consolidated field; the 5W2H sub-fields feed into it but the rubric checks the consolidated statement

All strings per Finding 3 rule. All gate-required per Finding 11.

**Note:** The three cross-phase fields are dicts (not strings) — this is the one exception to the "all captured fields are strings" rule from Finding 3. The dict contains string values, but the container is a dict so the grader can read the reference fields mechanically. This exception is justified because these fields serve two purposes: holding the Belt's content AND carrying the cross-phase reference.

### Finding 7 — 18 computation tools have no typed destination ✅ CONFIRMED — Option B

**Problem:** Belt runs `t_test` and gets p=0.001. Result vanishes into conversation prose. Grader can't verify "was a hypothesis test actually run?"

**Resolution:** Option B — store computation results in `artifacts["computation_results"]` as a list. One structured container per phase, all tool outputs in one place.

```python
artifacts["computation_results"] = [
    {"tool": "t_test", 
     "inputs": {"sample1": "new_staff_errors", "sample2": "experienced_staff_errors"},
     "result": {"t_statistic": "4.23", "p_value": "0.001", "significant": "yes"},
     "turn": 7, "phase": "analyse"},
    {"tool": "calculate_cpk", 
     "inputs": {"usl": "5%", "lsl": "0%", "mean": "3.1%", "std_dev": "0.8%"},
     "result": {"cpk": "1.33"},
     "turn": 12, "phase": "measure"}
]
```

All values stored as strings per Finding 3 rule. No new top-level PhaseState fields — results live inside `artifacts` which already exists. Gate document includes them. Grader checks "was a hypothesis test run?" by reading `artifacts["computation_results"]` for entries with `"tool": "t_test"`.

**Rationale for B over A:** Option A adds 3-5 new typed fields per phase — schema growth for the same outcome. Option B gives the grader the same mechanical check ("is there a computation_results entry for t_test?") without per-phase field proliferation. All 18 tools write to the same list structure; only the `tool` name and `phase` field differ.

### Finding 10 — project_id vs case_id naming split ✅ CONFIRMED — case_id everywhere

**Problem:** Docs say `project_id`. All code says `case_id`. Same identifier, two names.

**Resolution:** `case_id` is the canonical name across the entire project. Docs change to match code, not the other way around. SupervisorState field becomes `case_id: str` (not `project_id`). Store namespaces become `("projects", case_id, "artifacts")`. All three governance docs updated in the same commit.

**Rationale:** Code, Azure AI Search indexes (`improve_case_index.case_id`, `improve_evidence_index.case_id`), blob paths, and all existing models already use `case_id`. One find-and-replace in docs vs migration of code + indexes + blob paths.

### Finding 11 — rubric criteria not gate-required ✅ CONFIRMED — two-tier approach

**Problem:** Some fields exist but aren't gate-required. Grader checks them against the rubric, creating a contradiction where the grader can fail what the gate already passed.

**Resolution:** Two-tier field classification per phase. Eliminates the Layer 2 / Layer 4 contradiction while keeping coaching flexible.

**Tier 1 — Gate-required.** Layer 2 (field presence) blocks without them. Gate cannot pass.
- Define: `problem_statement`, `project_scope`, `goal_statement`
- Measure: `baseline_mean`, `data_collection_plan`
- Analyse: `root_cause_statement`, `root_cause_validation`
- Improve: `selected_solution`, `pilot_result`
- Control: `control_plan`, `post_improvement_metric`

**Tier 2 — Rubric-recommended.** Grader flags as missing with explicit warning. Belt sees the gap, chooses to add it now or proceed with acknowledgment. All other rubric criteria fall here (baseline_sigma, ruled_out_causes, handover_documented, financial_impact_verified, implementation_plan, etc.).

When Belt proceeds without a Tier 2 field, the gate document records: `{"acknowledged_gaps": ["baseline_sigma — Belt accepted gap"]}`. Next phase planner sees this and factors it into coaching plan.

**Rationale (from user):** A rigid gate that blocks on every criterion teaches Belts to fill fields mechanically. Tier 1 catches genuinely incomplete phases. Tier 2 coaches toward best practice while respecting the Belt's judgment about their own project. The audit trail shows conscious decisions, not silent omissions.

**Impact on the four-layer validation stack:**
- Layer 2 (field presence) checks Tier 1 fields only — blocks if missing
- Layer 4 (grader) checks both tiers — flags Tier 2 gaps as warnings, not failures
- The grader's structured verdict gains a new status: `"warning"` alongside `"pass"` and `"fail"`
- A gate can pass with warnings but not with failures

### Finding 12 — eBook items not in schema ✅ CONFIRMED — belt-level-aware tiering

**Problem:** MBB eBook lists items (VOC, COPQ, FMEA, stability, hypothesis tests, financial verification, lessons learned) not in the schema.

**Coaching scope:** Both Green Belt and Black Belt. The two-tier system from Finding 11 handles level differences. The grader reads `belt_level` from the case record and adjusts recommendations accordingly.

**New fields to add:**
- `voc_summary: str` (Define) — **Tier 1**. Every DMAIC project needs customer perspective regardless of belt level.
- `lessons_learned: str` (Control) — **Tier 2**. Valuable for cross-project learning via case index.
- `transferability: str` (Control) — **Tier 2**. Feeds yokoten / `rag_lookup_case_history`.

**Already covered by existing fields or rubric strengthening (no new fields):**
- COPQ → strengthen `business_case` rubric to require quantification
- Financial verification → `financial_impact_verified` from Finding 4
- Hypothesis test results → `artifacts["computation_results"]` from Finding 7
- Handover → `handover_documented` from Finding 5
- Process maps → captured via `propose_diagram` tool, results in conversation
- Short/long-term capability → `calculate_cpk` tool, results in `artifacts["computation_results"]`
- Practical + statistical significance → strengthen `pilot_result` rubric

**Belt-level-aware Tier 2 items (grader flags for BB only, suppressed for GB):**
- FMEA — heavy methodology, BB-level tool. User: "definitely very heavy"
- DOE — heavy methodology, BB-level tool. User: "are heavy"
- X-Y matrix — BB prioritisation technique
- Statistical problem statement — BB discipline
- Updated FMEA in Analyse — only if FMEA was done in Measure
- Stability / special causes — important for meaningful baseline, Tier 2 with strong warning for both levels
- Three-party sign-off (Champion + Belt + Finance) — ideal for BB, simplified for GB

**Grader belt-level logic:**
```
if belt_level == "Black Belt":
    flag FMEA, DOE, X-Y matrix, statistical problem statement as Tier 2 recommendations
if belt_level == "Green Belt":
    suppress these — do not recommend heavy methodology GB isn't trained for
```

### Finding 13 — current_phase/phase_index derivable from gate_passed ✅ KEEP (document exemption)

**Problem:** Same redundancy class as the fields we just removed.

**Resolution:** Keep for ergonomics — `state["current_phase"]` is read in dozens of places and deriving it every time adds noise. Document in ARCHITECTURE.md why these are exempt: "derived values kept for readability; the supervisor is responsible for keeping them consistent with gate_passed."

### Finding 14 — coaching_plan list vs dict ✅ CONFIRMED — single dict, transient

**Problem:** Some docs show `coaching_plan: dict`, others show `list[dict]`.

**Resolution:** `coaching_plan: dict[str, Any]` — single plan per planner turn. Overwritten each time the planner runs. No upfront queue.

```python
coaching_plan = {
    "focus_field": "root_cause_statement",
    "next_action": "coach_root_cause_identification",
    "retrieval_strategy": "multi_hop",
    "tools_needed": ["rag_lookup_methodology", "rag_lookup_evidence"]
}
```

**Rationale:** The Belt's responses change what the next plan should be. A plan made at turn 1 can't anticipate turn 4. The planner reads current `artifacts` (captured fields) to know what's done and what's next — no pre-planned list needed.

**Results storage:** The plan itself is transient — overwritten per turn. Results land durably in:
- `artifacts` — captured field values and computation results
- `citations` — sources the coach referenced
- `step_log` — what the planner decided and why (audit trail)
- `messages` — the coaching conversation itself
- LangSmith trace — complete LLM input/output for the planner call

### Finding 15 — three names for one concept ✅ CONFIRMED — artifacts is canonical

**Problem:** `artifacts`, `captured_fields`, `phase_inputs` all refer to the same thing.

**Resolution:** `artifacts` is the single canonical name across the project.
- `artifacts` — PhaseState field name, store namespace, gate document content. Used everywhere.
- `captured_fields` — retired. Replace with `artifacts` in all governance doc prose.
- `phase_inputs` — v1 code name. Replaced during refactor.

Document in ARCHITECTURE.md: "PhaseState.artifacts holds the fields the Belt has produced in this phase. Previous code called these phase_inputs. Previous prose called these captured_fields. Both names are retired."

---

## Store namespace design (complete)

```
Azure Blob Container: agentlean-improve

store/projects/{case_id}/artifacts/define.json
store/projects/{case_id}/artifacts/measure.json
store/projects/{case_id}/artifacts/analyse.json
store/projects/{case_id}/artifacts/improve.json
store/projects/{case_id}/artifacts/control.json

checkpoints/{case_id}/latest.json
checkpoints/{case_id}/history/{checkpoint_id}.json
```

Each artifacts JSON contains the complete approved gate document for that phase:
- All captured fields (strings per Finding 3)
- Cross-phase reference dicts where applicable (Finding 5)
- Computation results list (Finding 7)
- Citations list (Finding 8)
- Uploads list (Finding 8)
- Acknowledged gaps list if Belt proceeded without Tier 2 fields (Finding 11)

Written by gate_apply after Belt approval. Read by next phase's planner via input mapper. `case_id` is the canonical identifier (Finding 10) matching code and Azure AI Search indexes.

---

## All decisions confirmed ✅

| Finding | Decision |
|---|---|
| 3 — baseline typing | Option B — all captured fields are strings, computation tools parse at point of use |
| 4 — post_improvement_metric | Add three fields to Control: post_improvement_metric, improvement_delta, financial_impact_verified |
| 5 — cross-phase references | Option A — explicit cross-reference dicts for 3 fields (causal_hypothesis, solution_linked_to_root_cause, post_improvement_metric). Simple string fields for 4 others. |
| 7 — computation results | Option B — stored in `artifacts["computation_results"]` as list of typed dicts |
| 10 — naming | `case_id` everywhere — docs match code and indexes |
| 11 — gate-required fields | Two-tier system — Tier 1 (gate blocks), Tier 2 (grader warns, Belt acknowledges gap) |
| 12 — eBook items | 3 new fields (voc_summary, lessons_learned, transferability). Rest covered by existing fields or rubric strengthening. Belt-level-aware: FMEA and DOE are Tier 2 BB-only. |
| 14 — coaching_plan | Single `dict[str, Any]` — one plan per planner turn, transient |
| 15 — canonical name | `artifacts` — retired `captured_fields` (prose) and `phase_inputs` (v1 code) |

---

## Post-commit findings (discovered during continued document reading)

### Finding 16 — Phase subgraph node definition doesn't match ratified architecture ✅ CONFIRMED

**Problem:** `build_phase_subgraph` in REFACTORING_AGENT_IMPROVE.md shows five nodes:
```python
planner → executor → policy_advisory → gate_review → revise
```

Ratified architecture has five different nodes:
```python
planner → executor → validation_stack → gate_review → gate_apply
```

Three mismatches:

| Document (wrong) | Ratified (correct) | Problem |
|---|---|---|
| `policy_advisory` as node 3 | `validation_stack` as node 3 | The four-layer validation stack (coherence, field presence, constraints, grader) is missing entirely. Policy advisory is logic inside gate_apply, not its own node. |
| `gate_review` as node 4 | `gate_review` as node 4 | ✅ Matches |
| `revise` as node 5 | `gate_apply` as node 5 | Different name and expanded scope. gate_apply runs policy advisory (step 6), processes Belt approval (step 7), writes gate document to store (step 8). |

**Resolution:** Replace the `build_phase_subgraph` code block in REFACTORING_AGENT_IMPROVE.md with:

```python
def build_phase_subgraph(phase: str, llm, tools_for_phase):
    graph = StateGraph(PhaseState)
    graph.add_node("planner",          make_phase_planner(phase, llm))
    graph.add_node("executor",         make_phase_executor(phase, llm, tools_for_phase))
    graph.add_node("validation_stack", make_validation_stack(phase, llm))
    graph.add_node("gate_review",      make_gate_review(phase))     # interrupt fires here
    graph.add_node("gate_apply",       make_gate_apply(phase))      # policy advisory + store write
    # … conditional edges and cycles
    return graph.compile()        # NO checkpointer — the parent owns it
```

**Also update:** any `add_edge` or conditional edge references in the same section that use the old node names (`policy_advisory`, `revise`). Search all three docs for these node names and correct to `validation_stack` and `gate_apply`.

### Finding 17 — Gate validator and policy advisory incorrectly listed as executor tools ✅ CONFIRMED

**Problem:** REFACTORING_AGENT_IMPROVE.md states: "Extraction, `rag_lookup_*`, the gate validator, the computation tools, and the policy advisory tool are bound to the executor node via `bind_tools()`."

This is wrong on two counts:

1. **The gate validator (four-layer validation stack) is a separate node** (`validation_stack`), not a tool on the executor. It runs after the executor finishes, connected by an edge. It's its own room, not equipment inside the executor room.

2. **The policy advisory is logic inside `gate_apply` node**, not a tool bound to the executor. It fires after the Belt reviews and edits, checking whether edits break cross-phase consistency.

**What IS correctly bound via `bind_tools`:** `record_field`, `rag_lookup_methodology`, `rag_lookup_evidence`, `rag_lookup_case_history`, `propose_template`, `propose_diagram`, `check_gate_status`, `request_human_approval`, and the phase-specific computation tools (18 total).

**Resolution:** Correct the statement to remove gate validator and policy advisory from the tools list. Rewrite to:

"Leaf tools are not subgraph nodes. `record_field`, `rag_lookup_*`, `propose_template`, `propose_diagram`, `check_gate_status`, `request_human_approval`, and the phase-specific computation tools are bound to the executor node via `bind_tools()`. The validation stack and policy advisory are NOT tools — the validation stack is a separate subgraph node; the policy advisory is logic inside the gate_apply node."

### Finding 18 — DMAICGraderMiddleware and validation_stack Layer 4 are NOT redundant ✅ CONFIRMED

**Problem identified during review:** The grader appears to exist in two places — as middleware (DMAICGraderMiddleware inside the executor) and as Layer 4 of the validation_stack node. Initial analysis suggested this was redundant.

**Resolution: They are complementary, not redundant. Two different rubrics, two different purposes, two different timings.**

**DMAICGraderMiddleware (middleware, inside executor, every turn):**
- Fires after every coach response via `after_agent` hook
- Checks **coaching quality** — is the coach doing a good job of coaching?
- Uses COACHING_QUALITY_RUBRIC:
  ```
  - Coach must not accept vague or unmeasurable statements as captured fields
  - Coach must not invent data, metrics, or values the Belt didn't provide
  - Coach must not do the Belt's work (writing their problem statement for them)
  - Coach must stay on the current phase's topic
  - Coach must challenge weak inputs with specific follow-up questions
  - Coach must reference methodology when guiding (not just opinion)
  ```
- Catches problems in real time — the Belt never sees a weak coach response
- If the coach passively accepts "poor morale" as a root cause, the middleware catches it before the Belt sees it and forces the coach to challenge the Belt instead

**Validation stack Layer 4 (separate node, gate boundary only):**
- Fires once when all fields are captured and the planner routes to the gate
- Checks **document quality** — is the complete gate document good enough?
- Uses the phase-specific DMAIC rubric (e.g., ANALYSE_RUBRIC from §42):
  ```
  - root_causes: identified and prioritized against baseline data
  - root_cause_validation: statistical or observational evidence
  - causal_hypothesis: linked back to captured baseline metric
  - ruled_out_causes: alternatives considered and rejected with rationale
  ```
- Catches cross-field and cross-phase consistency issues that per-turn checks can't see
- Example: all four Analyse fields look good individually but root cause mentions "error rate" while baseline metric is "cycle time" — different measures, inconsistent

**Why both are needed:**
- Middleware catches coaching process failures early (every turn) — prevents 8 turns of building on a weak foundation
- Validation node catches document product failures late (gate only) — prevents a consistent-looking but internally contradictory gate document from being approved

**Middleware stack unchanged:**
```python
middleware=[
    BeforeModelStateInjection(),        # before: inject project state
    DMAICSkillsMiddleware(...),         # before: load phase instructions
    SummarizationMiddleware(...),       # before: compress if needed
    DMAICGraderMiddleware(              # after: check coaching quality
        rubric=COACHING_QUALITY_RUBRIC, # coaching process rubric
        model=grader_llm,
        max_iterations=3,
    ),
]
```

**Validation stack unchanged:**
```
Layer 1: coherence check (LLM)
Layer 2: field presence — Tier 1 required, Tier 2 flagged (deterministic)
Layer 3: constraint validation (LLM)
Layer 4: full-document grader using PHASE_RUBRIC (LLM) — different rubric from middleware
```

### Finding 21 — Adopt ModelRetryMiddleware for invisible retry tier ✅ CONFIRMED

**Problem:** The fallback chain (§67) needs retry-with-backoff for transient LLM failures. The document says `ModelRetryMiddleware` is "worth evaluating" but no decision was made. Without it, we'd write custom retry code (try/except, sleep with backoff, counter increment) — mechanical plumbing the built-in middleware already provides.

**Resolution:** Adopt `ModelRetryMiddleware` from LangChain built-in middleware. It uses the `wrap_model_call` hook — wraps each LLM call with automatic retry and configurable exponential backoff. Invisible to Belt and coach. Handles transient timeouts and rate limits silently.

The middleware stack becomes five (was four):

```python
middleware=[
    BeforeModelStateInjection(),        # before_model: inject project state
    DMAICSkillsMiddleware(...),         # before_agent: load phase instructions
    SummarizationMiddleware(...),       # before_model: compress if needed
    ModelRetryMiddleware(retries=2),    # wrap_model_call: invisible retry on transient failures
    DMAICGraderMiddleware(...),         # after_agent: check coaching quality
]
```

**Distinction preserved:** `ModelRetryMiddleware` handles mechanical retry (network flaked, try again). The fallback chain (§67) handles model-swap (gpt-4o → gpt-4o-mini → cache → degraded). Different tiers, different mechanisms.

**Update needed:** REFACTORING_AGENT_IMPROVE.md §80 line 1737 changes from "worth evaluating" to "adopted." §84 middleware stack table gains a fifth entry. ARCHITECTURE.md middleware stack documentation updated. All `create_agent` code examples in the document should show five middleware, not four.

**Problem:** REFACTORING_AGENT_IMPROVE.md §2 line 673 says:
```
| 2d | Quality rubric | DMAICGraderMiddleware (§42) | LLM grader |
```

This is wrong. Step 2d runs inside the validation_stack node at the gate boundary. `DMAICGraderMiddleware` is the middleware that runs inside the executor during every coaching turn (Finding 18). Two different graders, two different purposes, two different timings.

**Resolution:** Change Step 2d to reference the gate document grader, not the middleware:
```
| 2d | Quality rubric | Gate document grader using PHASE_RUBRIC (e.g., ANALYSE_RUBRIC from §42) | LLM grader — operational-model, temp 0.1 |
```

Also add a clarifying note in §2 that two graders exist:
- `DMAICGraderMiddleware` — fires every coaching turn via `after_agent` hook, checks coaching quality using COACHING_QUALITY_RUBRIC
- Gate document grader — fires once at gate boundary inside validation_stack node Layer 4, checks document quality using the phase-specific DMAIC rubric (DEFINE_RUBRIC, MEASURE_RUBRIC, etc.)

The middleware grader has already done its job during the coaching conversation. The validation node grader checks the complete gate document for cross-field consistency and cross-phase linkage — things the per-turn middleware grader can't see because it evaluates one response at a time.

**Problem 1:** Line 1553 declares `baseline_metric: float` in the `DefineOutput` BaseModel. Finding 3 ratified: all captured fields are strings. This example predates the state design resolution.

**Resolution:** Change to `baseline_metric: str` in the DefineOutput example. Apply the same check to every BaseModel example in the document — any captured field typed as float, int, or bool should be str.

**Problem 2:** The `define_agent` example at line 1591 lists `BeforeModelStateInjection()` last in the middleware list. For `before_model` hooks, declaration order is execution order. State injection should fire first (before skills loading and summarisation prepare content), not last.

**Resolution:** Reorder middleware in the example:
```python
middleware=[
    BeforeModelStateInjection(),                            # 1st: inject project state
    DMAICSkillsMiddleware(skills_dir="agent-improve/skills"), # 2nd: load phase instructions
    SummarizationMiddleware(model="azure/operational-model",  # 3rd: compress if needed
                            trigger=("tokens", 100_000),
                            keep=("messages", 20)),
    DMAICGraderMiddleware(model=grader_llm, max_iterations=3, # after_agent: check coaching quality
                          on_evaluation=write_to_step_log),
]
```

**Scope:** Search entire document for all `create_agent` and BaseModel examples. Verify field types match Finding 3 (all str) and middleware order matches the ratified stack.

---

### Finding 24 — eBook extraction schema gaps — six cross-cutting decisions ✅ ALL CONFIRMED

**Source:** BB eBook extraction (five files under agent-improve/skills/extraction/). 57 gaps identified. Six cross-cutting decisions resolve 25+ of them.

**Decision A — Secondary Metrics. All five phases. Tier 2.**

Add `secondary_metrics: str` to DefineOutput, MeasureOutput, AnalyseOutput, ImproveOutput, ControlOutput. Tier 2 — grader flags if missing: "You haven't identified what could get worse if this improvement succeeds."

Resolves: D-1, M-7, A-10, I-10, C-12 (5 gaps).

**Decision B — Vital Few X's + X-Y Matrix. Measure. Both Tier 1.**

Add two fields to MeasureOutput:
- `xy_matrix_summary: str` — **Tier 1**. Evidence that prioritisation was done. Gate question: "Is there a completed X-Y Matrix?"
- `vital_few_xs: str` — **Tier 1**. The ranked result carried to Analyse. Gate question: "Which X's are you taking into Analyse and why?"

User rationale for Tier 1: "this is critical to any improvement project." Without knowing which X's are the vital few, Analyse guesses at root causes instead of investigating data-driven priorities.

Analyse planner reads both from the store and uses them to focus root cause coaching.

Resolves: M-3, M-6, A-9, C-6 (4 gaps — the vital few X's chain across Measure → Analyse → Control).

**Decision C — FMEA. Dropped entirely from schema.**

No `fmea_summary` field in any phase. User: "FMEA is not typically something you would do in an improvement project." FMEA is heavy manufacturing methodology. For service/transactional DMAIC projects (the typical Agent Improve use case), the X-Y Matrix already prioritises causes without the severity × occurrence × detection overhead.

If a Black Belt does an FMEA, it lives in `uploads` as an attached document. The SKILL.md for BB projects can mention FMEA as a technique. The schema doesn't track it.

Resolves: M-4, A-4, C-4 (3 gaps — the FMEA chain is closed by not tracking it).

**Decision D — Control Plan restructured. Tier 1.**

Replace `control_plan: str` with `control_plan: dict` containing five sub-plans:
```python
control_plan: dict  # {
    #   "documentation": str,    — updated process maps, SOPs, training manuals
    #   "monitoring": str,       — what charts, frequency, limits, who checks
    #   "response": str,         — what happens when monitoring signals a problem
    #   "training": str,         — who needs training, format, verification
    #   "aligning_systems": str  — HR, IT, budget changes to sustain
    # }
```

Tier 1 — gate requires the dict, grader checks all five sub-plans populated. Belt works through them one at a time during coaching. Control SKILL.md must explain each sub-plan and guide the Belt through it.

Resolves: C-1 (five elements), C-2 (develop vs implement), C-5 (monitoring method), C-15 (mistake-proofing as part of response/monitoring). 4 gaps.

**Decision E — Issues and Barriers. All five phases. Tier 1.**

Add `issues_and_barriers: str` to DefineOutput, MeasureOutput, AnalyseOutput, ImproveOutput, ControlOutput. **Tier 1** — gate-required. Every project has blockers. A Belt who says "no issues" hasn't thought about it.

User rationale for Tier 1: "issues and barriers are standard in any improvement project."

Different from `acknowledged_gaps` (system-generated — records skipped Tier 2 fields). Issues and barriers are Belt-stated real-world project blockers — sponsor availability, data access, team disagreement, resource constraints.

If genuinely no barriers: Belt writes "none identified at this stage" — conscious statement, not silent skip.

Next phase planner reads from store and factors in: "Belt reported IT won't give database access — data collection will be challenging."

Resolves: D-5, M-11, A-12, I-12, C-14 (5 gaps).

**Decision F — Practical Significance in Analyse. Tier 1.**

Add `practical_significance: str` to AnalyseOutput. **Tier 1** — gate-required.

The eBook has two separate gates: statistical significance (is the effect real?) AND practical significance (is the effect big enough to matter?). A root cause that's statistically significant at p=0.001 but explains 0.1% of the problem isn't worth building an Improve solution for.

Improve's rubric already requires both for `pilot_result`. Making Analyse symmetric means the Belt checks practical significance BEFORE designing a solution.

Coach asks: "Your hypothesis test shows this is statistically significant. But how much of the problem does it explain? If you fixed this completely, how much would the error rate drop?"

Resolves: A-1 (1 gap).

---

**Impact on Output schemas (cumulative with Findings 1-23):**

| Phase | Fields before F24 | New fields | Fields after F24 |
|---|---|---|---|
| Define | 12 | +secondary_metrics, +issues_and_barriers | 14 |
| Measure | 10 | +xy_matrix_summary, +vital_few_xs, +secondary_metrics, +issues_and_barriers | 14 |
| Analyse | 10 | +practical_significance, +secondary_metrics, +issues_and_barriers | 13 |
| Improve | 10 | +secondary_metrics, +issues_and_barriers | 12 |
| Control | 14 | +secondary_metrics, +issues_and_barriers (control_plan restructured from str to dict) | 16 |

**Tier 1 updates (fields that block the gate):**

| Phase | Tier 1 before | Tier 1 after |
|---|---|---|
| Define | 4 | 5 (+issues_and_barriers) |
| Measure | 2 | 6 (+xy_matrix_summary, +vital_few_xs, +issues_and_barriers) |
| Analyse | 2 | 4 (+practical_significance, +issues_and_barriers) |
| Improve | 2 | 3 (+issues_and_barriers) |
| Control | 2 | 3 (+issues_and_barriers, control_plan already Tier 1 but now dict) |

---

### Finding 26 — Process maps, stability assessment, and experiment justification — three critical gaps resolved ✅ CONFIRMED

**Source:** User review of the nine "no field" gaps. Three upgraded from coaching content to schema fields based on domain expertise.

**D-2/M-5 — Process map. Two structured dict fields across Define and Measure. Both Tier 1.**

User rationale: "A process map is vital — if not visualised it will lead to more issues later. The Belt must measure each process step in timing and resources. Far too often Belts capture only segments of the process which in an improvement project are vital as otherwise there is no way to measure the improvement."

**DefineOutput gains:** `process_map_sipoc: dict` — **Tier 1**
```python
process_map_sipoc: dict  # {
    #   "suppliers": str,        — who provides inputs
    #   "inputs": str,           — what enters the process
    #   "process_steps": str,    — 5-7 high-level steps
    #   "outputs": str,          — what the process produces
    #   "customers": str,        — who receives outputs
    #   "process_kpis": str      — what is measured at each step
    # }
```

Coach responsibilities:
- Guide Belt through each SIPOC element
- Validate completeness: end-to-end, no missing steps, inputs match suppliers, outputs reach customers
- Challenge fragments: "you've described steps 3-5 but what happens before and after?"
- Verify consistency with `project_scope`
- If Belt uploads an existing process diagram, decompose it into structured SIPOC format and validate

**MeasureOutput gains:** `detailed_process_map: dict` — **Tier 1**
```python
detailed_process_map: dict  # {
    #   "steps": str,            — detailed process steps (expanded from SIPOC)
    #   "cycle_times": str,      — timing per step
    #   "resources": str,        — who/what involved per step
    #   "value_vs_waste": str,   — which steps add value, which are waste (VSM element)
    #   "measurement_points": str — where data is collected per step
    #   "baseline_kpis": str     — current KPIs per step before improvement
    # }
```

Coach responsibilities:
- Check Measure map against Define SIPOC — does it expand correctly?
- Verify measurement points align with `data_collection_plan`
- Value-vs-waste analysis identifies improvement candidates
- Baseline KPIs establish the "before" that Control's "after" compares against

**Before/after KPI connection across phases:**
- Define: `process_map_sipoc.process_kpis` — what is measured
- Measure: `detailed_process_map.baseline_kpis` — the "before" values
- Control: `post_improvement_metric` — the "after" values
- Grader verifies same measurement points, different values

**M-2 — Stability assessment. Tier 1.**

Add `stability_assessment: str` to MeasureOutput — **Tier 1**, gate-required.

The eBook is explicit: check stability BEFORE capability. An unstable process has special causes — baseline Cpk is meaningless if the process isn't in statistical control. The SKILL.md coaching sequence: run stability check first → if unstable, identify special causes → only after stability confirmed, proceed to capability calculation.

**I-1 — Experiment justification. Tier 1.**

Add `experiment_justification: str` to ImproveOutput — **Tier 1**, gate-required.

The Belt must state one of three options:
1. "DOE conducted — here's why and what we found" (full experiment)
2. "Simplified experiment — tested one factor at a time, before/after comparison" (simplified for business Belts)
3. "No experiment needed — solution follows directly from root cause analysis, here's why" (most common in service projects)

All three are valid. The point: the Belt consciously reasoned about whether an experiment was needed. The SKILL.md includes a simplified DOE explanation for Belts without statistical training — three options presented in plain language.

**Updated field counts (cumulative — Findings 1-26):**

| Phase | Total before | New fields | Total after | Tier 1 |
|---|---|---|---|---|
| Define | 14 | +process_map_sipoc (dict, T1) | 15 | 6 |
| Measure | 12 | +detailed_process_map (dict, T1), +stability_assessment (str, T1) | 14 | 7 |
| Analyse | 13 | (no change) | 13 | 4 |
| Improve | 12 | +experiment_justification (str, T1) | 13 | 4 |
| Control | 15 | (no change) | 15 | 3 |

**Remaining six no-field gaps (unchanged — confirmed as coaching content):**
- D-3: Stakeholder analysis — coaching content in Define SKILL.md
- D-4/M-10/A-11/I-11: Project plan — coaching content, timeline/resource concerns captured in `issues_and_barriers`
- M-1: Short/long-term capability — coaching guides both, numbers in `computation_results`

**Impact on gate assembly logic:** Add `process_map_sipoc` to DefineOutput assembly (bracket access — Tier 1). Add `detailed_process_map` and `stability_assessment` to MeasureOutput assembly (bracket access — Tier 1). Add `experiment_justification` to ImproveOutput assembly (bracket access — Tier 1).

**Impact on SKILL.md authoring:** Define SKILL.md needs SIPOC coaching guidance per element. Measure SKILL.md needs detailed process map coaching + stability-before-capability sequencing. Improve SKILL.md needs the simplified three-option experiment justification dialogue. These are the most content-heavy coaching sequences after the computation tool patterns (Finding 25).

**Tier/placement corrections (2):**
- A-2: Statistical problem statement — eBook places in Analyse for all Belts, we placed in Define BB-only. Correct to Analyse, all Belts.
- C-3: Three-party sign-off — eBook asks as General gate question, we have it as Tier 2 with no field. Add `project_signoff: str` to ControlOutput, Tier 2.

**Covered by SKILL.md coaching content, no schema change (10+):**
- D-2, M-5: Process map persistence — coach uses `propose_diagram`, result lives in conversation. SKILL.md guides the Belt through creating process maps.
- D-3: Stakeholder analysis — coaching content in Define SKILL.md, distinct from `team` field.
- D-4, M-10, A-11, I-11: Project plan — cross-phase coaching content, not a captured field per phase.
- M-1: Short-term AND long-term capability — coaching guidance to address both when using `calculate_cpk`, results in `computation_results`.
- M-2: Stability assessment — coaching guides Belt to check stability before capability. Tier 2 rubric with strong warning.
- I-1, I-2: Experiment justification — coaching content in Improve SKILL.md. The valuable answer is often "no DOE needed."

**Need your judgment (5):**
- D-6: Lean opportunities / waste analysis — ✅ SKILL.md coaching content, no field
- D-7: Benefits analysis with deferral date — ✅ coaching content in business_case, no field
- D-8: Finance sign-off at Define — ✅ coaching content, no field
- I-3: Explanatory power (R², variance explained) — ✅ Add `explanatory_power: str` Tier 2 on ImproveOutput
- A-5, I-6: Process owner buy-in at Analyse and Improve — ✅ Add `process_owner_buyin: str` Tier 2 on AnalyseOutput and ImproveOutput

**Page correction:** §13.5 and REFACTORING §42 cite "eBook p681" for verified financial impact. Correct page is book pp677-679.

**Tier/placement corrections (from extraction):**
- A-2: Statistical problem statement — correct from Define BB-only to Analyse all Belts per eBook. Add `statistical_problem_statement: str` Tier 2 on AnalyseOutput.
- C-3: Three-party sign-off — add `project_signoff: str` Tier 2 on ControlOutput. Gate question: "Do the Champion, the Belt and Finance all agree this project is complete?"

---

**FINAL Output schema field counts (cumulative — Findings 1-25):**

```
DefineOutput (16 fields):
  Tier 1: problem_statement, project_scope, goal_statement, voc_summary, issues_and_barriers
  Tier 2: business_case, team, baseline_metric, target_metric, secondary_metrics
  Gate metadata: computation_results, acknowledged_gaps, citations, uploads

MeasureOutput (16 fields):
  Tier 1: baseline_mean, data_collection_plan, xy_matrix_summary, vital_few_xs, issues_and_barriers
  Tier 2: baseline_sigma, measurement_system_validated, secondary_metrics
  Gate metadata: computation_results, acknowledged_gaps, citations, uploads

AnalyseOutput (16 fields):
  Tier 1: root_cause_statement, root_cause_validation, practical_significance, issues_and_barriers
  Tier 2: causal_hypothesis (dict), ruled_out_causes, secondary_metrics, statistical_problem_statement, process_owner_buyin
  Gate metadata: computation_results, acknowledged_gaps, citations, uploads

ImproveOutput (15 fields):
  Tier 1: selected_solution, pilot_result, issues_and_barriers
  Tier 2: solution_linked_to_root_cause (dict), implementation_plan, secondary_metrics, explanatory_power, process_owner_buyin
  Gate metadata: computation_results, acknowledged_gaps, citations, uploads

ControlOutput (19 fields):
  Tier 1: control_plan (dict — 5 sub-plans), post_improvement_metric (dict), issues_and_barriers
  Tier 2: improvement_delta, financial_impact_verified, sustainability_check, handover_documented, lessons_learned, transferability, secondary_metrics, project_signoff
  Gate metadata: computation_results, acknowledged_gaps, citations, uploads
```

---

### Finding 25 — Computation tool coaching pattern — the coach teaches, not just computes ✅ CONFIRMED

**Problem identified by user:** "We need to ensure the phase_executor node not only guides the Belt but explains them how to prepare for linear_regression and how to collect the data and we need to ensure the phase_executor node has the tool to calculate the linear regression or pearson correlation and interpret it and give it back to the Belt with visual and text explanation. This is a critical part of the coach who does not only ask questions but assists the Belt in every aspect."

**Resolution:** Every computation tool interaction follows a six-step coaching pattern. This is a core requirement for every SKILL.md:

1. **Explain why** — what this analysis proves and why the Belt needs it now
2. **Guide data preparation** — what data format is needed, check Belt's uploaded data via `rag_lookup_evidence`
3. **Run the computation** — coach calls the tool, Belt sees the call happening
4. **Interpret the result** — translate statistical output into plain language the Belt understands
5. **Visualise** — call `propose_diagram` to show the result graphically where applicable
6. **Coach the next move** — what does this result mean for the project? What's the next step?

This pattern applies to ALL 18 computation tools, not just linear regression:

| Phase | Tool | Coaching example |
|---|---|---|
| Define | `calculate_expected_savings` | "Let's estimate the financial impact. If each rework costs €X and you have Y per month..." |
| Measure | `calculate_sigma_level` | "Your sigma level tells us how capable the process is. Let me calculate it from your defect data..." |
| Measure | `calculate_cpk` | "Cpk shows whether your process fits within the spec limits. You'll need USL, LSL, mean, and std dev..." |
| Measure | `calculate_grr` | "Before we trust the data, we need to verify the measurement system. GR&R checks whether different people measuring the same thing get the same result..." |
| Analyse | `t_test` | "To prove the training gap is real, we'll compare error rates between the two groups statistically..." |
| Analyse | `linear_regression` | "Let's see how strongly training hours predict error rate. You'll need two columns of data..." |
| Control | `xbar_r_chart_limits` | "Control charts will monitor whether the improvement holds. I'll calculate the control limits from your post-improvement data..." |

Each SKILL.md must include the coaching sequence for every computation tool in that phase's `allowed-tools`. The coach doesn't just call the tool — it wraps the tool call in a teaching moment.

**Impact on SKILL.md authoring:** This is the most content-heavy part of each skill. The six-step pattern for each tool produces 20-40 lines of coaching guidance per tool. For Measure (8 computation tools), that's 160-320 lines of computation coaching alone. The BB eBook extraction provides the methodology content; we shape it into the six-step coaching conversation format.

**Impact on the DMAICGraderMiddleware (COACHING_QUALITY_RUBRIC):** Add a criterion: "When calling a computation tool, the coach must explain the purpose before calling, interpret the result after, and suggest a visualisation where applicable. The coach must not dump raw statistical output without explanation."

**Problem:** REFACTORING_AGENT_IMPROVE.md has two different `DefineOutput` definitions:
- Line 1551: `problem_statement: str, baseline_metric: float, scope: str` (wrong type, incomplete)
- Line 8187: `ctqs: list[str], confidence_score: float, gaps_identified: list[str]` (wrong fields entirely)

Neither matches the ratified Define phase fields. Both use `float` (contradicts Finding 3). `MeasureOutput`, `AnalyseOutput`, `ImproveOutput`, `ControlOutput` are referenced but never defined.

**Cross-check issues found:**
1. Three cross-phase fields are `dict` but original schemas missed `citations` and `uploads` in gate metadata
2. `computation_results` and `acknowledged_gaps` are gate metadata assembled at gate time, not captured by CoachingResponse
3. `citations` (Finding 8) was in PhaseState but missing from Output schemas
4. `uploads` (Finding 8) was in PhaseState but missing from Output schemas

**Resolution:** Replace both with one canonical definition per phase. All field values are `str` (Finding 3). Cross-phase reference fields are `dict` (Finding 5). Gate metadata includes computation_results, acknowledged_gaps, citations, and uploads. Tier classification from Finding 11 noted per field.

```python
class DefineOutput(BaseModel):
    """Gate document for the Define phase."""
    # Tier 1 — gate-required
    problem_statement: str          # measurable problem with baseline and target
    project_scope: str              # explicit inclusions and exclusions
    goal_statement: str             # SMART criteria
    voc_summary: str                # voice of customer (Finding 12)
    # Tier 2 — rubric-recommended
    business_case: str              # quantifiable business impact
    team: str                       # Belt, sponsor, 2+ members with roles
    baseline_metric: str            # current measured state
    target_metric: str              # target value
    # Gate metadata — assembled at gate time, not captured per-turn
    computation_results: list[dict] = []  # accumulated from tool calls during phase (Finding 7)
    acknowledged_gaps: list[str] = []     # Tier 2 fields Belt proceeded without (Finding 11)
    citations: list[dict] = []            # sources referenced during phase (Finding 8)
    uploads: list[dict] = []              # files Belt uploaded during phase (Finding 8)

class MeasureOutput(BaseModel):
    """Gate document for the Measure phase."""
    # Tier 1 — gate-required
    baseline_mean: str              # numeric value with units (as string)
    data_collection_plan: str       # sample size, frequency, responsible person
    # Tier 2 — rubric-recommended
    baseline_sigma: str             # calculated sigma level (Finding 5)
    measurement_system_validated: str  # GR&R or equivalent evidence
    # Gate metadata
    computation_results: list[dict] = []
    acknowledged_gaps: list[str] = []
    citations: list[dict] = []
    uploads: list[dict] = []

class AnalyseOutput(BaseModel):
    """Gate document for the Analyse phase."""
    # Tier 1 — gate-required
    root_cause_statement: str       # identified and prioritized
    root_cause_validation: str      # statistical or observational evidence
    # Tier 2 — rubric-recommended
    causal_hypothesis: dict         # cross-phase ref to Measure baseline (Finding 5)
    ruled_out_causes: str           # alternatives rejected with rationale (Finding 5)
    # Gate metadata
    computation_results: list[dict] = []
    acknowledged_gaps: list[str] = []
    citations: list[dict] = []
    uploads: list[dict] = []

class ImproveOutput(BaseModel):
    """Gate document for the Improve phase."""
    # Tier 1 — gate-required
    selected_solution: str          # criteria-based selection documented
    pilot_result: str               # measurable improvement demonstrated
    # Tier 2 — rubric-recommended
    solution_linked_to_root_cause: dict  # cross-phase ref to Analyse root cause (Finding 5)
    implementation_plan: str        # timeline, responsible person, resources
    # Gate metadata
    computation_results: list[dict] = []
    acknowledged_gaps: list[str] = []
    citations: list[dict] = []
    uploads: list[dict] = []

class ControlOutput(BaseModel):
    """Gate document for the Control phase."""
    # Tier 1 — gate-required
    control_plan: str               # monitoring frequency, thresholds, responsible person
    post_improvement_metric: dict   # cross-phase ref to Measure baseline (Finding 5)
    # Tier 2 — rubric-recommended
    improvement_delta: str          # change from baseline (Finding 4)
    financial_impact_verified: str  # quantified savings (Finding 4)
    sustainability_check: str       # process for maintaining gains
    handover_documented: str        # process owner accepting responsibility (Finding 5)
    lessons_learned: str            # what went well, what didn't (Finding 12)
    transferability: str            # can this be applied elsewhere (Finding 12)
    # Gate metadata
    computation_results: list[dict] = []
    acknowledged_gaps: list[str] = []
    citations: list[dict] = []
    uploads: list[dict] = []
```

**Gate assembly logic (all five phases):**

```python
# DEFINE — gate assembly
gate_document = DefineOutput(
    problem_statement=artifacts["problem_statement"],
    project_scope=artifacts["project_scope"],
    goal_statement=artifacts["goal_statement"],
    voc_summary=artifacts.get("voc_summary", ""),
    business_case=artifacts.get("business_case", ""),
    team=artifacts.get("team", ""),
    baseline_metric=artifacts.get("baseline_metric", ""),
    target_metric=artifacts.get("target_metric", ""),
    computation_results=artifacts.get("computation_results", []),
    acknowledged_gaps=validation_stack.get_acknowledged_gaps(),
    citations=state["citations"],
    uploads=state["uploads"],
)

# MEASURE — gate assembly
gate_document = MeasureOutput(
    baseline_mean=artifacts["baseline_mean"],
    data_collection_plan=artifacts["data_collection_plan"],
    baseline_sigma=artifacts.get("baseline_sigma", ""),
    measurement_system_validated=artifacts.get("measurement_system_validated", ""),
    computation_results=artifacts.get("computation_results", []),
    acknowledged_gaps=validation_stack.get_acknowledged_gaps(),
    citations=state["citations"],
    uploads=state["uploads"],
)

# ANALYSE — gate assembly (note: causal_hypothesis is dict, not str)
gate_document = AnalyseOutput(
    root_cause_statement=artifacts["root_cause_statement"],
    root_cause_validation=artifacts["root_cause_validation"],
    causal_hypothesis=artifacts.get("causal_hypothesis", {}),      # dict — cross-phase ref
    ruled_out_causes=artifacts.get("ruled_out_causes", ""),
    computation_results=artifacts.get("computation_results", []),
    acknowledged_gaps=validation_stack.get_acknowledged_gaps(),
    citations=state["citations"],
    uploads=state["uploads"],
)

# IMPROVE — gate assembly (note: solution_linked_to_root_cause is dict)
gate_document = ImproveOutput(
    selected_solution=artifacts["selected_solution"],
    pilot_result=artifacts["pilot_result"],
    solution_linked_to_root_cause=artifacts.get("solution_linked_to_root_cause", {}),  # dict
    implementation_plan=artifacts.get("implementation_plan", ""),
    computation_results=artifacts.get("computation_results", []),
    acknowledged_gaps=validation_stack.get_acknowledged_gaps(),
    citations=state["citations"],
    uploads=state["uploads"],
)

# CONTROL — gate assembly (note: post_improvement_metric is dict)
gate_document = ControlOutput(
    control_plan=artifacts["control_plan"],
    post_improvement_metric=artifacts.get("post_improvement_metric", {}),  # dict
    improvement_delta=artifacts.get("improvement_delta", ""),
    financial_impact_verified=artifacts.get("financial_impact_verified", ""),
    sustainability_check=artifacts.get("sustainability_check", ""),
    handover_documented=artifacts.get("handover_documented", ""),
    lessons_learned=artifacts.get("lessons_learned", ""),
    transferability=artifacts.get("transferability", ""),
    computation_results=artifacts.get("computation_results", []),
    acknowledged_gaps=validation_stack.get_acknowledged_gaps(),
    citations=state["citations"],
    uploads=state["uploads"],
)
```

**Pattern across all five:**
- Tier 1 fields use `artifacts["field"]` — KeyError if missing (gate should not have passed Layer 2 without them)
- Tier 2 fields use `artifacts.get("field", "")` — empty string if Belt proceeded without them
- Cross-phase dict fields use `artifacts.get("field", {})` — empty dict if not captured
- Gate metadata always comes from the same four sources: `artifacts["computation_results"]`, `validation_stack.get_acknowledged_gaps()`, `state["citations"]`, `state["uploads"]`

---

### Finding 23 — ProviderStrategy IS used on phase executor via CoachingResponse ✅ CONFIRMED (REVISED)

**Problem (original):** §82 code examples show `response_format=ProviderStrategy(DefineOutput)` — wrong schema for per-turn coaching.

**Problem (revised after source verification):** The `response_format` feature on `create_agent` is correct and valuable. The official LangChain docs (verified August 4, 2026) confirm: structured response is returned in `result["structured_response"]` key of the agent's final state. The agent still calls tools normally during the ReAct loop. Only the terminal response is structured. Coaching text appears in `messages` as normal. Both exist simultaneously.

**The real error in the document:** Using `DefineOutput` (the complete gate document) as the response_format. The correct schema is a per-turn coaching response that captures one turn's output.

**Resolution:** ProviderStrategy IS used on the phase executor. The schema is `CoachingResponse`, not `DefineOutput`.

**CoachingResponse schema (per-turn, used on every executor invoke):**

```python
class CoachingResponse(BaseModel):
    """Structured extraction from each coaching turn."""
    message: str                        # coaching text the Belt sees
    fields_captured: list[dict] = []    # [{field_name: str, value: Any, source: str}]
    citations: list[dict] = []          # sources referenced this turn
```

`value` is `Any` (not `str`) to handle both plain string fields and cross-phase reference dicts (Finding 5 — `causal_hypothesis`, `solution_linked_to_root_cause`, `post_improvement_metric` are dicts).

**How it works per turn:**

```python
result = agent.invoke(state)

# Belt sees coaching text:
result["messages"][-1]  →  "Good, I've captured your baseline at 12.3%..."

# System reads structured extraction:
result["structured_response"]  →  CoachingResponse(
    message="Good, I've captured your baseline at 12.3%...",
    fields_captured=[{"field_name": "baseline_metric", "value": "12.3%", "source": "belt_stated"}],
    citations=[]
)
```

The executor node reads `structured_response` and writes to PhaseState:
- `fields_captured` → each entry written to `artifacts[field_name] = value`
- `citations` → appended to `state["citations"]`

**Impact on tools:** `record_field` tool is REMOVED from universal tools (was 8, now 7). Field capture happens via `structured_response`, not tool calls. The universal 7: `rag_lookup_methodology`, `rag_lookup_evidence`, `rag_lookup_case_history`, `propose_template`, `propose_diagram`, `check_gate_status`, `request_human_approval`.

**Impact on tool counts per phase:**

| Phase | Universal | Phase-specific | Total |
|---|---|---|---|
| Define | 7 | 1 (calculate_expected_savings) | 8 |
| Measure | 7 | 8 computation tools | 15 |
| Analyse | 7 | 5 computation tools | 12 |
| Improve | 7 | 1 (calculate_doe_main_effects) | 8 |
| Control | 7 | 4 computation tools | 11 |

**create_agent call (corrected):**

```python
define_agent = create_agent(
    model="operational-premium",
    tools=UNIVERSAL_TOOLS + [calculate_expected_savings],   # 8 tools (record_field removed)
    response_format=CoachingResponse,                       # auto-selects ProviderStrategy for gpt-4o
    middleware=[
        BeforeModelStateInjection(),
        DMAICSkillsMiddleware(skills_dir="agent-improve/skills"),
        SummarizationMiddleware(model="azure/operational-model",
                                trigger=("tokens", 100_000),
                                keep=("messages", 20)),
        ModelRetryMiddleware(retries=2),
        DMAICGraderMiddleware(model=grader_llm, max_iterations=3,
                              on_evaluation=write_to_step_log),
    ],
)
```

**Complete structured output mapping (revised):**

| Node / Component | Built with | Output schema | Mechanism |
|---|---|---|---|
| Phase planner | Plain LLM call | `CoachingPlan` | `model.with_structured_output(CoachingPlan)` |
| Phase executor (coach) | `create_agent` + tools | `CoachingResponse` | `response_format=CoachingResponse` (ProviderStrategy auto-selected) |
| Validation Layer 1 (coherence) | Plain LLM call | `CoherenceResult` | `model.with_structured_output(CoherenceResult)` |
| Validation Layer 3 (constraints) | Plain LLM call | `ConstraintCheckResult` | `model.with_structured_output(ConstraintCheckResult)` |
| Validation Layer 4 (gate grader) | Plain LLM call | `GraderVerdict` | `model.with_structured_output(GraderVerdict)` |
| Gate review | No LLM | Interrupt payload | `interrupt()` — no structured output |
| Gate apply — policy advisory | Plain LLM call | `PolicyAdvisoryResult` | `model.with_structured_output(PolicyAdvisoryResult)` |
| DMAICGraderMiddleware | Plain LLM call inside middleware | `CoachingGraderVerdict` | `model.with_structured_output(CoachingGraderVerdict)` |
| Inside `rag_lookup_*` tools | Plain LLM call | `QueryVariants` | `model.with_structured_output(QueryVariants)` |
| Gate document assembly | No LLM call | `DefineOutput` etc. | `DefineOutput(**artifacts)` — Pydantic validation only |

**Key distinction:** `response_format=CoachingResponse` on `create_agent` = structured extraction on every turn alongside normal coaching text. `model.with_structured_output(Schema)` = wraps a plain LLM call for one-shot structured responses inside tools, middleware, and non-agent nodes. `DefineOutput(**artifacts)` = Pydantic validation at gate time, no LLM call.

**Update needed in all three docs:** Replace `DefineOutput` with `CoachingResponse` in all `create_agent` examples. Add `CoachingResponse` schema definition. Update tool counts (universal 8 → 7, remove `record_field`). Add all five Output schemas with corrected gate metadata (citations, uploads). Add gate assembly logic.

---

## Final integrity check (to run AFTER all corrections are applied)

---

### Finding 27 — Multi-source knowledge index (BACKLOG — not in refactor scope) ✅ CONFIRMED for backlog

**Problem:** Companies may have their own improvement methodology documents (internal BB guides, company-specific process standards) alongside the standard BB eBook. Currently `improve_knowledge_index` has no source separation — all chunks look the same. If a company uploads their own guide, the coach can't distinguish between standard BB methodology and company-specific guidance. Conflicting advice from two sources has no attribution.

**Three issues for future implementation:**
1. No source separation — chunks from different documents mix with no attribution
2. Phase classifier tuned to BB eBook — different documents may get misclassified
3. No tenant isolation — Company A's methodology visible to Company B's Belts

**Resolution (post-refactor, add to §87 backlog):**

Add two fields to `improve_knowledge_index` schema:
```
source_document: str    — "bb_ebook_v11.1" or "acme_corp_guide_v2"
tenant_id: str          — which company (multi-tenant isolation)
```

Retrieval filter update in `rag_lookup_methodology`:
```python
# Default: BB eBook only
filter = f"phase_relevance eq '{phase}' and source_document eq 'bb_ebook_v11.1'"

# Company with custom guide: their guide first, BB eBook as fallback
filter = f"phase_relevance eq '{phase}' and (source_document eq 'acme_corp_guide_v2' or source_document eq 'bb_ebook_v11.1')"
```

Ingestion update in `ingest_knowledge.py`:
- Accept a `source_document` parameter
- Accept a `tenant_id` parameter
- Re-evaluate phase classifier for non-BB-eBook documents (different terminology/structure)

**Coaching impact:** The coach weaves source content into natural coaching voice (no citation blocks shown to Belt). When company content is available, the coach can say "your company's improvement guide recommends..." and fall back to BB eBook for topics the company guide doesn't cover.

**Why deferred:** The refactor builds against the BB eBook as the single knowledge source. The architecture supports multiple sources — the index schema needs two fields and the retrieval filter needs one additional clause. This is incremental, not architectural. Adding it now would complicate ingestion, retrieval, and testing without a second document to test against.

**§87 backlog item:** Add as item 15 — "Multi-source knowledge index: source_document field, tenant_id field, retrieval filter priority, phase classifier re-evaluation for non-BB documents."

Before Claude Code commits the corrections batch, run a comprehensive integrity check across all three documents:

1. **Every BaseModel/TypedDict schema** — field types match ratified decisions (all captured fields str, final is dict, gate_passed is dict[str, bool], cross-phase refs are dicts)
2. **Every code example** — node names match Finding 16 (validation_stack, gate_apply — not policy_advisory, revise), middleware order correct, tool lists match §39 per-phase binding
3. **Every cross-reference** — §N references resolve, field names match canonical names (artifacts not captured_fields, case_id not project_id, belt_edits not feedback)
4. **Rubric consistency** — COACHING_QUALITY_RUBRIC (middleware) and PHASE_RUBRIC (validation node) documented as separate rubrics per Finding 18
5. **Store namespace** — all store.put/store.get calls use case_id and "artifacts" namespace consistently
6. **Two-tier field classification** — every field in every phase classified as Tier 1 or Tier 2, consistent across ARCHITECTURE.md, CLAUDE.md, and REFACTORING_AGENT_IMPROVE.md
7. **Grader verdict schema** — includes "warning" status alongside "pass" and "fail" per Finding 11
8. **Schema compatibility chain** — verify the complete field flow from capture to store:
   - Every `field_name` the coach can produce in `CoachingResponse.fields_captured` must match a field in the corresponding phase's Output schema (DefineOutput, MeasureOutput, etc.)
   - Every Tier 1 field in each Output schema must be reachable by the coach via CoachingResponse (the coach must be able to capture it)
   - Every Tier 2 field in each Output schema must either be capturable by the coach OR producible by a computation tool (via `artifacts["computation_results"]`)
   - Cross-phase dict fields (`causal_hypothesis`, `solution_linked_to_root_cause`, `post_improvement_metric`) must accept `value: Any` from CoachingResponse (not just `str`)
   - Gate assembly logic for each phase must reference every field in that phase's Output schema — no field left unassembled
   - `PhaseState.artifacts` must be able to hold every field from every phase (it's `dict[str, Any]` — confirm no type conflict with dict-typed cross-phase fields)
   - Store write path: `gate_apply` writes `OutputSchema.dict()` → store accepts dict → next phase planner reads dict → input mapper deserialises correctly
   - Pydantic validation at gate assembly: Tier 1 fields raise on missing (KeyError from `artifacts["field"]`), Tier 2 fields default to empty (`.get("field", "")`)
9. **Tool count consistency** — universal tools = 7 (record_field removed per Finding 23), per-phase totals: Define 8, Measure 15, Analyse 12, Improve 8, Control 11. Verify across all three docs.
10. **CoachingResponse ↔ Output schema field name match** — produce a table per phase:

```
DEFINE PHASE:
  CoachingResponse field_name    DefineOutput field     Type match?
  "problem_statement"        →   problem_statement      str ✓
  "project_scope"            →   project_scope          str ✓
  "goal_statement"           →   goal_statement         str ✓
  "voc_summary"              →   voc_summary            str ✓
  "business_case"            →   business_case          str ✓
  "team"                     →   team                   str ✓
  "baseline_metric"          →   baseline_metric        str ✓
  "target_metric"            →   target_metric          str ✓

ANALYSE PHASE (cross-phase dict example):
  CoachingResponse field_name    AnalyseOutput field    Type match?
  "root_cause_statement"     →   root_cause_statement   str ✓
  "root_cause_validation"    →   root_cause_validation  str ✓
  "causal_hypothesis"        →   causal_hypothesis      dict ✓ (value: Any handles dict)
  "ruled_out_causes"         →   ruled_out_causes       str ✓
  
  ... same for Measure, Improve, Control
```

Claude Code produces this table for all five phases and flags any field name mismatch, type mismatch, or unreachable Tier 1 field.
