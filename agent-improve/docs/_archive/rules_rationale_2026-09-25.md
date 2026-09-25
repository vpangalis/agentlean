# Rules rationale and history — archived 2026-09-25

Moved out of `.claude/rules/` by step 6.66 (founder ruling 2026-09-25), verbatim. Each block below is text removed from a rule file, filed under the rule file and the numbered heading it sat under, in original order. The current binding text stays in `.claude/rules/`; this file records what was true when written and is not governed.

## `.claude/rules/architecture.md`

### architecture.md · §1 — Architecture principles

<!-- original lines 11-14 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

### architecture.md · 1.1 — One State Per Level, One Runtime, One Source of Truth

<!-- original lines 36-37 -->
  (§1.7, §10). Passing only a checkpointer is the most common
  architecture mistake.

### architecture.md · 1.2 — Hierarchical Subgraphs, One Thread, Auto Namespacing

<!-- original lines 43-56 -->
```
supervisor_graph                    thread_id = case_id, e.g. "IMPR-2026-FS1"
├── define_subgraph                 checkpoint_ns auto-managed by LangGraph
├── measure_subgraph
├── analyse_subgraph
├── improve_subgraph
├── control_subgraph
└── escalation_subgraph
```

**Binding rules:**

- **One `thread_id` per project.** Never per phase, never concatenated
  (`{case_id}-define` and similar are BANNED).

<!-- original lines 58-60 -->
  subgraphs compile without either. LangGraph routes their writes
  through the parent's saver, distinguished by an auto-managed
  `checkpoint_ns`.

<!-- original lines 70-72 -->
  state** (§10.2). Subgraph state updates are not guaranteed to
  propagate to the parent immediately — this is documented LangGraph
  behaviour, and the store is the documented fix.

### architecture.md · 1.3 — Tool-Calling Coach, Explicit Planner

<!-- original lines 88-89 -->
Fusing them loses the boundary that makes coaching inspectable and
costs the ability to test either half.

<!-- original lines 96-97 -->
deterministic gate-check on `gate_passed` plus static edges. There
is nothing to reason about, so nothing reasons.

### architecture.md · 1.4 — Async by Default

<!-- original lines 110-110 -->
(prompt building, state transformations, validation logic, all 20

### architecture.md · 1.5 — Streaming Responses

<!-- original lines 119-121 -->
`/ask/stream`. The frontend renders tokens as they arrive. The
non-streaming `/ask` endpoint remains for clients that cannot use
SSE but is not used by the standard UI.

### architecture.md · 1.6 — Interrupt-Based Gates — Nine Steps, Two Nodes

<!-- original lines 125-127 -->
Gate approval is a nine-step sequence with two distinct quality
checks in it, implemented across two nodes. The full sequence is
§9.1; the binding structural rules are:

### architecture.md · 1.7 — Phased Persistence — Blob Now, PostgreSQL Before Production

<!-- original lines 148-157 -->
`AzureBlobCheckpointSaver` lives at `core/checkpointer.py` and
implements `BaseCheckpointSaver`. `AzureBlobStore` lives at
`core/store.py` and implements `BaseStore`.

**Blob layout for checkpoints:**
```
checkpoints/{case_id}/
  latest.json                    — most recent checkpoint (fast resume)
  history/{checkpoint_id}.json   — historical checkpoints for time-travel
```

<!-- original lines 162-165 -->
- `gate_attempts` MUST be in the checkpointed state, never in route
  scope — this is what fixes the v1 "attempts always reset to 0" bug.
  It lives on `PhaseState` (§10.1), per phase, because each phase runs
  its own validation loop with its own cap

<!-- original lines 167-171 -->
**Migration is a constructor and connection-string change.** Both
sides of the split are defined by LangGraph interfaces, so nothing
above the persistence layer changes. Provision Azure Database for
PostgreSQL (flexible server) when the trigger fires; run the existing
unit tests against PostgreSQL before switching.

<!-- original lines 173-176 -->
**Known limitation of the Blob implementation:** it was not tested
for concurrent access, and Azure Blob has no row-level locking. This
is acceptable for single-developer refactoring and is not acceptable
for production. Do not defend it past the migration trigger.

### architecture.md · 1.9 — No MCP. Uploaded Data Is the Only External Channel

<!-- original lines 194-195 -->
connect to a live system.** This is an architectural exclusion, not a
deferral. There is no promotion trigger.

<!-- original lines 197-207 -->
**The runtime stack is:** FastAPI, LangGraph ≥1.2.6, LangChain 1.x,
Azure OpenAI, Azure AI Search, Azure Blob Storage, Azure Cache for
Redis. No MCP.

**The data architecture principle this establishes:**

> `improve_evidence_index` is not merely "case-specific uploaded
> documents." It is the **only** channel through which external,
> real-world data enters AgentLean.

Three consequences that bind on implementation:

<!-- original lines 210-214 -->
   how to structure it**. Data-collection coaching is a first-class
   part of the methodology, not a workaround.
2. Belt data-collection discipline is what the platform's grounding
   depends on.
3. **There is no fallback path where the system fetches a number the

## `.claude/rules/gates.md`

### gates.md · §9 — Validation and gates

<!-- original lines 11-14 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

### gates.md · 9.1 — The nine-step HITL gate pattern

<!-- original lines 20-36 -->
| Step | What happens | Quality check for |
|---|---|---|
| 1. Executor runs | Coach produces its response; extraction captures fields | — |
| 2. **Validation stack** | Four layers, cheapest first (§9.2). Failures feed back with accumulated per-layer feedback. **The Belt does not see this loop.** | **AI's work** |
| 3. Interrupt fires | `gate_review_node` pauses; Belt sees validated output | — |
| 4. Belt reviews | Belt checks AI-captured values for accuracy | — |
| 5. Belt edits *(optional)* | Belt corrects wrong fields | — |
| 6. **Policy advisory** | Validates the Belt's edits against required-field policy, cross-phase consistency, and previously approved values (§9.4). **Non-blocking.** | **Human's edits** |
| 7. Belt approves | Belt confirms the gate is ready; the gate document is assembled and written to the store **and** `PhaseState.final` (§9.6) | — |
| 8. Checkpoint saves | State committed **only now** | — |
| 9. Next phase | **The subgraph reaches `END`; the parent's static edge advances to the next phase.** The supervisor makes no decision — reaching `END` already means the gate passed (§3.1) | — |

**Two quality checks, two actors, two moments.** The grader blocks
(step 2) because it checks the AI's own output and there is no reason
to show the Belt work already known to be below standard. The advisory
does **not** block (step 6) because the Belt is the domain expert — it
offers a second opinion before the decision, not a veto after it.

### gates.md · 9.2 — The four-layer validation stack

<!-- original lines 40-40 -->
All four run inside step 2, before the interrupt.

<!-- original lines 42-47 -->
| Layer | Checks | Mechanism | Model | Fires |
|---|---|---|---|---|
| **2a. Coherence** | Real, meaningful, conclusive? Catches gibberish, vague non-answers, self-contradiction, off-topic replies, parroting the Belt's own words. **Implemented by `CoherenceMiddleware` (§8.9), not by the `validation_stack` node** | Lightweight LLM | `coherence`, temp 0.1 | **Every coaching turn** |
| **2b. Field presence** | All **Tier 1** fields for this phase populated? (`DMAICGateValidator`) | **Deterministic** | No LLM | Gate boundary only |
| **2c. Constraint** | Addresses budget / timeline / risk / measurement? | Lightweight LLM | `constraint`, temp 0.1 | Gate boundary + mid-conversation for key decisions |
| **2d. Quality rubric** | Does the **gate document** meet DMAIC standards per criterion? **Tier 1 fails, Tier 2 warns.** Uses `PHASE_RUBRIC` — *not* `DMAICGraderMiddleware`, which is a different grader (§8.2) | LLM grader | `grader`, temp 0.1 | Gate boundary only |

<!-- original lines 49-90 -->
**Run cheapest first. Each layer fires only if the previous passes.**

**Layer 2a is middleware; layers 2b–2d are the node.** Layer 2a fires
every coaching turn, which a gate-boundary node cannot do — it is
`CoherenceMiddleware` on `after_agent` (§8.9). Layers 2b–2d fire once, at
the gate, inside `validation_stack`. One conceptual stack, two mechanisms;
do not try to move 2a into the node or 2b–2d into middleware.

**Layer 2d is NOT `DMAICGraderMiddleware`.** It runs in the
`validation_stack` node against `PHASE_RUBRIC` and grades the gate
document. `DMAICGraderMiddleware` is middleware position 8, runs against
`COACHING_QUALITY_RUBRIC` every turn, and grades the coach's process
(§8.2). Two graders — confusing them is a violation.

**The counter is `PhaseState.gate_attempts` and the accumulated feedback
is `PhaseState.validator_feedback`** (§10.1). Neither may live in route
scope, and neither may be per layer.

**Layer 2b is the only deterministic layer.** Coherence and constraint
checks are LLM calls because format checks cannot detect content
failures — a length check does not detect fluent nonsense, and a
keyword check rejects a decision that addresses cost without using the
word "budget." Layer 2a costs roughly $0.01–0.02 per phase session at
20–40 turns; this is settled and is not to be re-optimised into a
regex.

**The iteration cap is 3, SHARED across all four layers**, with
accumulated feedback. Not three per layer. Feedback is specific:
*"your previous answer did not address timeline or risk mitigation"*,
never *"try again."*

**Per-phase constraint sets** are constants in `core/prompts.py`:
`DEFINE_CONSTRAINTS`, `ANALYSE_CONSTRAINTS`, `IMPROVE_CONSTRAINTS`,
`CONTROL_CONSTRAINTS`. Measure is covered by its rubric.

**Value-dependent constraints are supported and required** where a
constraint is conditional on another field — e.g. the risk-mitigation
check fires only when `risk_level == "low"`, because a low-risk
project should say how it stays low-risk, whereas a high-risk
project's decision inherently involves risk.

Every attempt at every layer is logged to `step_log` as a dict (§10.3).

### gates.md · 9.3 — Where each check fires, and what the Belt sees

<!-- original lines 102-102 -->
**The self-healing hierarchy — and the transparency principle:**

<!-- original lines 104-109 -->
| Level | Trigger | Behaviour | Belt sees | Retry |
|---|---|---|---|---|
| 1 — Silent | Coherence failure mid-turn | System retries internally | **Invisible** | Max 2, then degraded mode |
| 2 — Coached | Constraint failure on a Belt proposal | Coach teaches toward a better formulation | Transparent, collaborative | **No cap** — this is dialogue, not a loop |
| 3 — Validated | Full four-layer check at the gate | Belt sees pass/fail, corrects, approves | Transparent, Belt approves | Max 3, accumulated feedback |
| 4 — Escalated | Attempts exhausted | System defers with unresolved constraints named | Transparent, Belt is arbiter | None |

<!-- original lines 111-122 -->
> **Design principle: coached improvement is key, because silent is
> not transparent.**
>
> The default posture is transparency. **Silent retry is the narrowly
> scoped exception — coherence only** — justified because showing a
> Belt that the AI produced gibberish adds no value and erodes trust.
> Everything else is visible and collaborative.
>
> Level 2 having no retry cap is deliberate. Capping it would mean the
> coach eventually accepts a weak root cause, which is exactly the
> outcome DMAIC discipline exists to prevent. A constraint failure on
> a Belt's proposal is **a teaching moment, not an error**.

### gates.md · 9.4 — Mid-phase conflict detection — auto-flag, no threshold

<!-- original lines 126-127 -->
The policy advisory does **not** only run at gate boundaries. It runs
**before each coach response is returned to the Belt**.

<!-- original lines 129-142 -->
**Mechanics — semantic detection by the coach** (`docs/_archive/DECISIONS.md` §R1):
- **The coach compares** the Belt's input against the prior committed values
  already in its context, and sets `CoachingResponse.contradiction_flag`
  (§10.7) on a **material** contradiction. The instruction governing this
  lives in each SKILL.md (§8.3)
- `ContradictionDetectionMiddleware` (§8.8) reads the flag and **raises
  `HITLInterrupt`**; the coach's response is suppressed
- Payload: contradicted field, approved value and approving phase, proposed
  value, the Belt's own words, two Belt-facing options
- **No additional LLM call** — the flag rides the response call that already
  runs every turn
- **Flag only material numeric or categorical contradictions of committed
  values** — never prose rephrasing, never refinement of a not-yet-committed
  current-phase value

<!-- original lines 144-161 -->
**Detection is best-effort semantic, not deterministic.** The all-gate-fields
tab (§13) is the acknowledged human backstop.

**Belt's two options:**

| Option | Consequence |
|---|---|
| Update the approved value | The affected phase's gate document becomes provisional; downstream phases need re-review |
| Keep the approved value | The Belt clarifies they misspoke; no state change |

**There is NO tolerance threshold, and none may be added.** In
production DMAIC, baseline means, sigma levels, and target metrics are
taken seriously; silent drift across weeks is exactly the failure mode
a coaching system exists to prevent. *"The delta was small enough"* is
not acceptable when downstream analysis depends on the value.

**Any change to a previously gate-approved value is a mini-gate, never
a silent overwrite.**

### gates.md · 9.5 — The re-approval cascade

<!-- original lines 165-167 -->
If the Belt confirms a new value, the affected phase **and every
downstream phase that depends on it** return to a provisional state
and require re-review.

<!-- original lines 169-178 -->
This is deliberately heavier than a soft override. A root cause
validated against a baseline of 4.2 is not automatically valid against
3.8. Silent invalidation of downstream analysis is not acceptable.

**The cascade has a hard dependency on §3.6.** When it fires, the
affected phase's `error_handler` compensating logic MUST run to clean
up stale values already written to Azure Blob and `improve_case_index`.
A cascade that marks phases provisional but leaves published values in
place is worse than no cascade — state and index then disagree,
silently.

### gates.md · 9.6 — `gate_apply_node` writes the gate document TWICE

<!-- original lines 182-186 -->
**This is the write the whole store-mediated handoff depends on.** Every
cross-phase read in §10.2 assumes the previous phase's gate document is
in the store. `gate_apply_node` is what puts it there.

After Belt approval, at step 7, `gate_apply_node` writes to **both**:

### gates.md · 1. The store — what the next phase's input mapper reads

<!-- original lines 189-189 -->
# 1. The store — what the next phase's input mapper reads

<!-- original lines 191-192 -->

# 2. PhaseState — so the checkpoint is self-sufficient for crash recovery

### gates.md · 2. PhaseState — so the checkpoint is self-sufficient for crash recovery

<!-- original lines 196-200 -->
**Both writes are required.** The store write and the checkpoint commit
are separate operations; a crash between them would leave state saying
the gate was not applied while the store says it was. `final` holding
the same dict means the resumed graph can see what was approved without
re-reading the store — which is why `final` is a `dict` and not a `str`.

<!-- original lines 202-213 -->
**Store path:** `store/projects/{case_id}/artifacts/{phase}.json`

**The gate document contains, and nothing may be omitted from it:**

| Part | Source |
|---|---|
| All captured fields (strings — §10.6) | `artifacts` |
| The three cross-phase reference dicts, where they apply | `artifacts` |
| `computation_results` | `artifacts["computation_results"]` |
| `citations` | `PhaseState.citations` |
| `uploads` | `PhaseState.uploads` |
| `acknowledged_gaps` | Tier 2 fields the Belt chose to proceed without (§9.7) |

<!-- original lines 216-216 -->
The retry budget is per gate passage.

### gates.md · 9.7 — Two tiers of field; the grader gains a `warning` verdict

<!-- original lines 220-226 -->
**Layer 2b and Layer 2d must not be able to contradict each other.**
Before this rule, the gate blocked on a required-field list while the
grader graded against a rubric covering a different set — so a phase
could pass the gate and then be failed by the grader on a criterion the
gate never asked for.

**Every rubric criterion is classified into one of two tiers.**

<!-- original lines 233-233 -->
**Gate-required, by phase:**

<!-- original lines 235-241 -->
| Phase | Gate-required fields | Count |
|---|---|---|
| Define | **All 13 — no tier split (Option A).** `business_case`, `team` (**list[dict]**), `voc_summary`, `problem_statement`, `baseline_estimate`, `project_scope` (**dict**), `goal_statement`, `target_value`, `target_date`, `secondary_metrics`, `process_map_sipoc` (**dict**), `issues_and_barriers`, **`metric_definitions`** (the metric registry, §10.7) | **13** |
| Measure | `baseline_mean`, `data_collection_plan`, `driver_priority_summary`, `vital_few_drivers`, `detailed_process_map` (**dict**), `stability_assessment`, `issues_and_barriers` | 7 |
| Analyse | `root_cause_statement`, `root_cause_validation`, `practical_significance`, `issues_and_barriers` | 4 |
| Improve | `selected_solution`, `pilot_result`, `experiment_justification`, `issues_and_barriers` | 4 |
| Control | `control_plan` (**dict**, 5 sub-plans), `post_improvement_metrics`, `issues_and_barriers` | 3 |

<!-- original lines 243-249 -->
> **Define is the one phase with no Tier 2** (Option A, ratified 2026-08-26 —
> §0.18). **Thirteen gate-required, twelve coached** — `metric_definitions` is
> captured inside position 5's conversation rather than at its own coached
> position, so `field_index` still walks twelve (§0.20). Its row is a **complete
> field set, not a tier**; the other four rows
> are Tier 1 sets and those phases keep both tiers. Everything below about how
> the two tiers interact applies to those four.

<!-- original lines 251-254 -->
**`issues_and_barriers` is gate-required in every phase.** Every real project has
blockers; a Belt reporting none has not looked. If there genuinely are
none, the Belt writes "none identified at this stage" — a conscious
statement, not a silent skip.

<!-- original lines 256-321 -->
**It is NOT the same field as `acknowledged_gaps`.** `issues_and_barriers`
is Belt-stated real-world blockers; `acknowledged_gaps` is
system-generated and records skipped Tier 2 *fields*. Merging them is a
violation.

**Everything else in the rubric is Tier 2** — `baseline_sigma`,
`ruled_out_causes`, `handover_documented`, `financial_impact_verified`,
`implementation_plan`, `lessons_learned`, `transferability`,
`secondary_metrics`, `statistical_problem_statement`,
`process_owner_buyin`, `explanatory_power`, `project_signoff`, and the
rest. **In Define, `secondary_metrics` is gate-required** like every other
Define field, and is coached at position 10 — the Tier 2 listing here is
correct for the other four phases only (§0.18).

**The grader's verdict has three statuses, not two:**

```python
class CriterionVerdict(BaseModel):
    criterion: str
    tier:      int                                     # 1 or 2
    status:    Literal["pass", "warning", "fail"]
    feedback:  str                                     # specific, per criterion
```

**A gate MAY pass with warnings. A gate may NEVER pass with failures.**
Only Tier 1 criteria may produce `fail`.

**A Tier 2 gap the Belt proceeds past MUST be recorded**, never silently
dropped:

```python
"acknowledged_gaps": ["baseline_sigma — Belt accepted gap"]
```

The next phase's planner reads it from the store and factors it into the
coaching plan.

**Why two tiers.** A gate that blocks on every criterion teaches Belts
to fill fields mechanically — complete gate documents, worse projects.
Tier 1 catches genuinely incomplete phases; Tier 2 coaches toward best
practice while leaving the judgment with the Belt, who knows the
project. The audit trail then records conscious decisions rather than
silent omissions.

**The grader is belt-level aware.** It reads `belt_level` from the case
record:

```
if belt_level == "Black Belt":
    flag DOE as a Tier 2 recommendation
if belt_level == "Green Belt":
    suppress it — do not recommend heavy methodology GB isn't trained for
```

**DOE is the only belt-gated item left.** Three others left this list:

| Item | Now |
|---|---|
| X-Y matrix | **`driver_priority_summary`, Tier 1, all Belts** — it produces the vital few X's Analyse cannot start without |
| Statistical problem statement | **`statistical_problem_statement`, Tier 2, all Belts, in Analyse** — not Define |
| FMEA | **Not tracked in any schema.** See §10.8 |

**Stability is no longer belt-gated or advisory.** It is
`stability_assessment`, a **Tier 1 field required of both belt levels**
(§10.8) — a baseline computed across an unstable process is not a
baseline, so it blocks the gate rather than warning about it.

## `.claude/rules/graph.md`

### graph.md · §3 — Graph and node rules

<!-- original lines 8-11 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

### graph.md · 3.1 — Graph structure

<!-- original lines 26-34 -->
The phase subgraph builder takes the phase as a parameter, because it
must select that phase's computation-tool subset (§5.2):

```python
def build_phase_subgraph(phase: str, llm):
    tools = UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]
    ...
    return builder.compile()          # NO checkpointer, NO store
```

### graph.md · 3.3 — Per-phase subgraph nodes (the canonical structure)

<!-- original lines 68-68 -->
names.** Both appeared in earlier revisions:

<!-- original lines 70-73 -->
| Retired | Ratified | Why |
|---|---|---|
| `policy_advisory` | `validation_stack` | The four-layer stack was missing from the node list entirely. The policy advisory is logic inside `gate_apply`, not a node |
| `revise` | `gate_apply` | Revision is an **edge** — the validation stack routes back to the planner with `validator_feedback`. `gate_apply` does advisory + approval + store write |

<!-- original lines 75-83 -->
**The subgraph is a cycle, not a pipeline.** The planner fires many
times per phase, not once: after each executor step, control returns
to the planner to decide whether to continue on the current field,
advance to the next, or trigger the gate.

**Leaf tools are NOT subgraph nodes.** The universal eight (§5.1) and
the phase's computation tools are passed to the executor via `tools=`
on `create_agent`. From the subgraph's perspective the executor is one
node.

<!-- original lines 87-91 -->

| Component | What it is |
|---|---|
| Validation stack | A **node**, reached by an edge after the executor finishes. As a tool, the coach would decide whether to be validated — backwards |
| Policy advisory | **Logic inside `gate_apply`**. It runs after the Belt edits, when the coach is no longer in the loop |

### graph.md · 3.4 — Reflection is a node, not a private function

<!-- original lines 100-107 -->
Reflection is a graph node reached via a conditional edge. The edge
decides whether reflection is needed based on response length, risk
keywords (numbers, commitments, dates), and phase-specific rules.

For **invisible** retry — mechanical, not a coaching event — use the
retry middleware rather than a reflection node: `ModelRetryMiddleware`
for model-call failures, `ToolRetryMiddleware` for tool-call failures
(§8.7). Neither is named `RetryMiddleware`; that class does not exist.

### graph.md · 3.5 — Escalation lives and runs

<!-- original lines 115-116 -->
`gate_attempts` is persisted in the checkpointed state, never in route
scope.

### graph.md · 3.6 — Reliability primitives are native, not hand-written

<!-- original lines 121-121 -->
frameworks are BANNED.** LangGraph 1.2 provides the mechanism.

<!-- original lines 124-135 -->

```python
builder.add_node(
    "phase_executor",
    phase_executor_fn,
    timeout=TimeoutPolicy(run_timeout=45),
    error_handler=phase_error_recovery,
)
```

`run_timeout=45` is the wall-clock limit. `NodeTimeoutError` triggers
the fallback chain (§4.8) before the Belt notices the delay.

<!-- original lines 140-140 -->
external write and routes to a degraded response:

<!-- original lines 142-169 -->
```python
def phase_error_recovery(error: NodeError, state: PhaseState) -> Command:
    delete_or_flag_stale_in_case_index(state["case_id"], state["phase"])
    return Command(
        update={"extraction_error": str(error), "extraction_incomplete": True},
        goto="degraded_coaching_response",
    )
```

**Two dependencies on this rule, both correctness-critical:**
- **Gate reopening** (§9.5) — when the re-approval cascade fires, the
  affected phase's handler must run, or state and index disagree
  silently.
- **Time-travel debugging** — resuming from an earlier checkpoint
  rolls back state, **not** external writes. Time travel is only
  correct for nodes that have a handler.

**Graceful shutdown is REQUIRED; its named mechanism is UNCONFIRMED.** A
deployment rollout must not kill mid-coaching sessions — they save their
checkpoint and resume. **But `RunControl.request_drain()` may not exist:**
it was not found in LangGraph releases 1.2.5–1.2.11 or in the reference
during the 2026-08-21 verification pass.

**No work may be scheduled against `request_drain()` until it is confirmed
against a real release or the LangGraph source.** If it does not exist, a
real fallback drain must be designed rather than a replacement API name
cited. Full statement and what counts as confirmation:
`../AGENTIC_ARCHITECTURE_REFERENCE.md` §45.

### graph.md · 3.7 — Multi-hop is capped at five tool calls per Belt turn

<!-- original lines 179-181 -->
`recursion_limit` is NOT the cap. It is a backstop against a genuine
infinite loop, set high (50) on the parent invoke and inherited by
everything below it:

<!-- original lines 183-208 -->
```python
await graph.ainvoke(
    state,
    config={"recursion_limit": RECURSION_LIMIT,        # 50 — backstop
            "configurable": {"thread_id": case_id}},
)
```

**`remaining_steps` is the graceful off-ramp, not the hop budget.**
It is a `RemainingSteps` managed value declared on `PhaseState`
(§10.1) and read at the top of the executor. When it runs low the
executor stops calling tools and composes an answer from what it
already holds — the Belt gets a coached turn, not a cap message:

```python
if (state.get("remaining_steps") or 0) <= REMAINING_STEPS_FLOOR:
    ...                     # compose from what is in hand; bind no tools
```

**Hops and steps are different units and neither substitutes for the
other.** `remaining_steps` counts graph-node transitions out of
`recursion_limit`; the whole coach loop runs inside ONE node, so it
moves by 1 per executor turn no matter how many hops that turn made.
A hop count is therefore kept separately, in the executor. Both
guards are required: the hop count enforces five, `remaining_steps`
catches the case where the graph itself is running out of room.

<!-- original lines 211-213 -->
turned into a partial answer for the Belt. It is now **belt-and-braces
against a bug, not the primary guard** — a Belt mid-session never sees
a stack trace because the coach explored too broadly.

<!-- original lines 215-227 -->
Hitting the cap is a **monitoring signal**, not just a limit — it
means either the system prompt encourages too-broad exploration, or
the question warrants `operational-premium` for that turn.

**This rule is why the build was wrong from step 6.2 to 6.6.** It
previously carried `recursion_limit = 2 * max_hops + 1 = 11` as the
hop cap — which `../AGENTIC_ARCHITECTURE_REFERENCE.md` §16 explicitly
rejects, and which is also arithmetically short: measured on both
LangGraph 1.1.10 and 1.2.11, a coach making its five permitted hops at
`recursion_limit=11` raises `GraphRecursionError` **before** it can
compose the answer, so a well-behaved five-hop turn could only ever
end in the cap message. That is WATCH 26's see-saw. Whatever this
rule says is what gets built, so it says the mechanism now.

## `.claude/rules/llm.md`

### llm.md · §4 — LLM rules

<!-- original lines 9-12 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

### llm.md · 4.2 — Roles

<!-- original lines 27-41 -->
Defined in `core/llm.py`. Two deployment tiers, addressed by role:

| Role | Deployment | Purpose |
|---|---|---|
| `coach` | `operational-premium` (gpt-4o) | Coaching content, max_tokens=1500 |
| `planner` | `operational-premium` (gpt-4o) | Phase planner structured decisions |
| `synthesis` | `operational-premium` (gpt-4o) | Final multi-hop synthesis |
| `reasoning` | `operational-model` (gpt-4o-mini) | Default reasoning, intermediate hops |
| `extraction` | `operational-model` (gpt-4o-mini) | Field extraction |
| `coherence` | `operational-model` (gpt-4o-mini) | Layer 1 coherence check (§9.2) |
| `constraint` | `operational-model` (gpt-4o-mini) | Layer 3 constraint check (§9.2) |
| `grader` | `operational-model` (gpt-4o-mini) | Layer 4 rubric grading (§8.2) |
| `summarizer` | `operational-model` (gpt-4o-mini) | Context compression (§8.4) |
| `intent` | `operational-model` (gpt-4o-mini) | Short classification |
| `vision` | `operational-premium` (gpt-4o) | Multimodal upload analysis |

<!-- original lines 45-45 -->
runs on `operational-premium`. gpt-4o-mini is roughly 15× cheaper.

### llm.md · 4.4 — Agent construction — `create_agent`, with middleware

<!-- original lines 56-83 -->
**Phase executors are built with `create_agent`.** Binding tools
directly onto a bare LLM inside a phase executor is a violation: it
bypasses the middleware stack (§8), which carries grading, skills,
compression, and state injection.

```python
executor = create_agent(
    model=get_llm("coach"),
    tools=UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase],
    response_format=CoachingResponse,       # §4.6, §10.7 — never a {Phase}Output
    middleware=[...],                       # §8.1 — all eight, in order
    system_prompt=PHASE_COACH_PROMPT[phase],
)
```

**The parameter is `system_prompt=`, not `prompt=`.** `create_react_agent`
took `prompt`; `create_agent` renamed it, and the LangGraph v1 migration
guide calls this out explicitly as a difference to watch when porting. The
verified signature also carries `state_schema`, `context_schema`,
`checkpointer`, `store`, `interrupt_before`, `interrupt_after`, `cache` and
`transformers` — none of which this project sets on the executor, since the
checkpointer and store attach to the parent graph only (§1.2).

*This example previously showed `response_format=ProviderStrategy(PhaseOutput)`
and "all four" middlewares. Both contradicted rules elsewhere in this file —
§4.6 and §10.7 mandate `CoachingResponse` on the executor, and §8.1 declares
eight middlewares. Corrected 2026-08-21. `prompt=` → `system_prompt=`
corrected in the same pass (`docs/_archive/BIBLE_VERIFICATION_LOG.md` C-2).* (archived to docs/_archive/; canonical: CLAUDE.md §0.10)

<!-- original lines 91-92 -->
BANNED while it remains pre-1.0. Our equivalents are custom middleware
on `create_agent` (§8.2, §8.3). Revisit at deepagents 1.0; migrate all

### llm.md · 4.5 — Content blocks, both directions

<!-- original lines 99-102 -->
Model responses carry typed content blocks. Read
`response.content_blocks`. String-indexing or substring-parsing the
raw content field is a violation — it breaks the moment a provider
returns a multi-part response.

<!-- original lines 104-105 -->
**Content blocks apply in both directions. §21 governs messages we
write as well as responses we read. Never build message content by

<!-- original lines 111-116 -->

`SystemMessage.content` is `str | list[dict]`. Over a multi-part
message an f-string renders the literal
`[{'type': 'text', 'text': …}]` into the prompt — structure
destroyed, **no error raised**, and the model silently reads a Python
repr.

<!-- original lines 126-134 -->
**The write side reached a commit at step 6.3** — both custom
middlewares concatenated onto `.content`, and it survived writing,
review, 716 green tests and a live trace. The rule had been filed
under *reading*, because step 2.6's twenty sites were all
`response.content`. **The list-content fixture is the load-bearing
half of this rule:** a string-content message passes the correct and
the broken implementation identically, so a test built on one proves
nothing. Full record: `docs/_archive/DECISIONS.md` Part AH2.


### llm.md · 4.6 — Structured output — scoped by call type

<!-- original lines 139-141 -->
**This rule replaces v2.1 §4.3, which mandated one mechanism
everywhere. There are two mechanisms, and the choice is determined by
what is being called — not by preference.**

<!-- original lines 143-147 -->
| The call is… | Use | Example |
|---|---|---|
| An agent built with `create_agent` | `response_format=Schema` (ProviderStrategy auto-selected) | Phase executor → `CoachingResponse` |
| A plain model invocation inside a tool, middleware, or validator | The builder-style structured-output call on the model | Query variants, grader verdict, constraint verdict |
| Assembling a gate document from already-captured fields | **No LLM call** — Pydantic construction | `DefineOutput(**artifacts)` at `gate_apply` |

<!-- original lines 149-188 -->
**Why the first two exist separately:** `response_format=` attaches to
an agent's model-tools loop. A tool generating query variants, a
middleware grading a transcript, and a validator returning
per-constraint verdicts are not agents — there is no loop to attach to.

Prefer `ProviderStrategy` over `ToolStrategy` where the provider
supports native JSON mode. LangChain 1.2 can infer the choice from the
model profile.

**Complete mapping — every structured output in the system:**

| Component | Built with | Schema | Mechanism |
|---|---|---|---|
| Phase planner | Plain LLM call | `CoachingPlan` | `with_structured_output` |
| **Phase executor (coach)** | **`create_agent` + tools** | **`CoachingResponse`** | **`response_format=`** |
| Validation Layer 2a (coherence) | Plain LLM call | `CoherenceResult` | `with_structured_output` |
| Validation Layer 2c (constraints) | Plain LLM call | `ConstraintCheckResult` | `with_structured_output` |
| Validation Layer 2d (gate grader) | Plain LLM call | `GraderVerdict` | `with_structured_output` |
| `gate_review` | **No LLM** | Interrupt payload | `interrupt()` |
| `gate_apply` — policy advisory | Plain LLM call | `PolicyAdvisoryResult` | `with_structured_output` |
| `DMAICGraderMiddleware` | Plain LLM call in middleware | `CoachingGraderVerdict` | `with_structured_output` |
| Inside `rag_lookup_*` | Plain LLM call | `QueryVariants` | `with_structured_output` |
| Gate document assembly | **No LLM** | `DefineOutput` … `ControlOutput` | `Schema(**artifacts)` |

**The executor's `response_format` is `CoachingResponse`, never a phase
Output schema.** The executor runs once per coaching turn; the gate
document is assembled once per phase. Asking the coach to emit a
complete `DefineOutput` every turn requests fields it has not yet
coached. See §10.7.

**The structured response and the coaching text coexist.** The agent
still calls tools normally through the ReAct loop and still writes
coaching prose into `messages`; only the terminal response is
additionally structured, and it arrives in `result["structured_response"]`.
Reading one does not cost you the other.

**What structured output does NOT give you:** truth. It guarantees
shape. A schema-valid `baseline_estimate: 4.2` invented by the model is
exactly as well-formed as a correct one. Content-level defence is
§6.4, §9.2 Layer 1, and §9.4 — not this rule.

### llm.md · 4.7 — Temperature discipline

<!-- original lines 194-200 -->
| Component | Temperature | Why |
|---|---|---|
| Coach responses | 0.5–0.7 | Natural variation improves the Belt's experience |
| Grader (§8.2) | 0.1 | Same gate document must get the same verdict across runs |
| Coherence check (Layer 1) | 0.1 | Consistent verdicts |
| Constraint check (Layer 3) | 0.1 | Consistent verdicts |
| Extraction, field validators | 0.0–0.2 | Same rationale |

<!-- original lines 203-204 -->
A grader that returns different verdicts across runs makes the
regression thresholds in §12 meaningless.

### llm.md · 4.8 — Fallback chain and circuit breakers

<!-- original lines 218-220 -->
**Backoff rule:** exponential for managed services (Azure OpenAI, which
rate-limits predictably); jittered for shared resources (the cache,
which several subagents may hit simultaneously).

<!-- original lines 222-222 -->
**Circuit breakers — three-state, two instances:**

<!-- original lines 224-227 -->
| Breaker | Wraps | On OPEN |
|---|---|---|
| LLM | Azure OpenAI calls | Coaching turn cannot happen — fall to Level 2, then degraded |
| Search | Azure AI Search calls | Coaching **continues** without RAG grounding — quality degradation, not availability failure |

<!-- original lines 229-249 -->
Threshold 3 failures in 30s trips open; 60s reset timeout; one probe
request in HALF-OPEN before resuming. **Two-state (CLOSED/OPEN)
breakers are not permitted** — this is a long-running service and must
recover without a restart.

**Degraded mode uses actual state, never a generic error:**

```python
def degraded_mode_response(state: PhaseState) -> str:
    return (
        f"I'm experiencing a temporary connection issue. "
        f"Based on what we've captured so far in the {phase} phase "
        f"({n_captured} of {n_total} fields complete), "
        f"I'd suggest we pause here and continue once the system recovers. "
        f"Your progress is saved and nothing has been lost."
    )
```

**HTTP 400 (token limit exceeded) is NOT a fallback case.** It is a
context-management failure — do not retry the same request against a
smaller model. Fix the context (§8.4).

## `.claude/rules/middleware.md`

### middleware.md · §8 — Middleware stack

<!-- original lines 8-11 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

### middleware.md · 8.1 — Eight middlewares, all on `create_agent`

<!-- original lines 17-20 -->
**Canonical: ARCHITECTURE.md §19.** §19 owns the stack and its ordering rules;
this section reproduces them. The block below is generated from
`_build_executor()` in `backend/phases/nodes_common.py` by AST parse, not
transcribed — a reorder in the code shows up here as a diff.

<!-- original lines 22-23 -->
**The list is NESTING order. The position numbers are EXECUTION order. For
`after_*` hooks the two are opposite.**

<!-- original lines 25-137 -->
```python
middleware=[
    BeforeModelStateInjection(...),                             # 1
    DMAICSkillsMiddleware(...),                                 # 2
    SummarizationMiddleware(
        trigger=("tokens", 100_000), keep=("messages", 20)),    # 3
    ModelRetryMiddleware(max_retries=2),                        # 4
    ToolRetryMiddleware(max_retries=2, on_failure="continue"),  # 5
    DMAICGraderMiddleware(...),                                 # 6
    CoherenceMiddleware(...),                                   # 7
    ContradictionDetectionMiddleware(...),                      # 8
]
```

| # | Middleware | | Hook(s) it implements |
|---|---|---|---|
| 1 | `BeforeModelStateInjection` §8.5 | custom | `before_agent`, `wrap_model_call` |
| 2 | `DMAICSkillsMiddleware` §8.3 | custom | `before_agent`, `wrap_model_call` |
| 3 | `SummarizationMiddleware` §8.4 | core | `before_model` |
| 4 | `ModelRetryMiddleware` §8.7 | core | `wrap_model_call` |
| 5 | `ToolRetryMiddleware` §8.7 | core | `wrap_tool_call` |
| 6 | `DMAICGraderMiddleware` §8.2 | custom | `after_agent` |
| 7 | `CoherenceMiddleware` §8.9 | custom | `after_agent` |
| 8 | `ContradictionDetectionMiddleware` §8.8 | custom | `after_agent` |

Applying the three clauses to that list:

- **`before_*` fire 1 → 2 → 3** — `BeforeModelStateInjection`,
  `DMAICSkillsMiddleware`, `SummarizationMiddleware`.
- **`after_*` fire 8 → 7 → 6** — `ContradictionDetectionMiddleware`,
  `CoherenceMiddleware`, `DMAICGraderMiddleware`.
- **`wrap_*` nest 1 ⊃ 2 ⊃ 4 ⊃ 5** — `BeforeModelStateInjection`,
  `DMAICSkillsMiddleware`, `ModelRetryMiddleware`, `ToolRetryMiddleware`;
  position 1 is the outermost layer.

Five are custom, three are core.

**Three ordering clauses, not one.** LangChain states them separately. An
earlier revision of this section collapsed them into *"declaration order is
execution order for hooks of the same kind, so this order is binding"* — a
sentence that is true of `before_*`, **false of `after_*`**, and not even the
right shape for `wrap_*`.

| Hook kind | Ordering, relative to the declared list |
|---|---|
| `before_*` | first to last — **same** as declaration order |
| `after_*` | **last to first** — the **reverse** of declaration order |
| `wrap_*` | nested; the first declared wraps all the others |

Read off the installed `langchain`'s own graph construction — the version is
`requirements.txt`'s — not the
documentation alone — the reading is quoted in the commit that made this
correction. **Not reproduced here: `langchain/agents/factory.py` is the
framework's code and the framework owns it**, so a copy in this file would be
one more transcription to go stale. Re-derive it rather than trusting this
paragraph if it ever matters.

**`BeforeModelStateInjection` MUST be first, and the `before_*` clause is why.**
Project facts have to reach the top of the prompt before skills loading and
summarisation shape it; `before_*` fires first-to-last, so first in the list is
first to run. Listing it last, as an earlier revision did, defeats the ordering
rule §8.5 exists to enforce.

**`BeforeModelStateInjection`'s hook is `before_agent`, not
`before_model`.** State injection belongs at agent-loop start, once per
turn — `before_model` fires before every individual model call within a
turn, which re-injects the same project facts repeatedly and wastes
context. An earlier revision typed it `before_model`; that is corrected.

**Positions 6, 7 and 8 all fire `after_agent`**, so they execute in the reverse
of how they are declared: **declared** grader, coherence, contradiction and
therefore **executing** contradiction, coherence, grader.
`test_the_declared_middleware_list_is_the_ratified_layering` asserts what executes
rather than what is listed — cite it; do not restate the order. **If
`CoherenceMiddleware` exhausts its retries, `DMAICGraderMiddleware` is skipped
for that turn** — deliberately: grading a response already known to be
incoherent spends a model call for a meaningless score. The skip travels
outward on the way out, which works only because coherence sits **inside** the
grader.

**Positions 4 and 5 do compete for a slot.** An earlier revision said they
"compete for no slot with the others; they are adjacent for readability, not
ordering" — false, and it is the same conflation. `wrap_*` hooks nest, so a
`wrap_*` middleware wraps everything declared after it. Since 6.3 positions 1
and 2 also implement `wrap_model_call`, so position 1 **encloses** position 4's
retry: the project-state block is composed and prepended once, and a retry
re-sends the built request rather than rebuilding it per attempt
(`test_position_1_wrap_encloses_position_4_retry`). Position 5 wraps tool calls
rather than model calls, so it is independent of the other three — independent
of *them*, not of position.

**The six named lifecycle hooks ARE the complete set** — `before_agent`,
`before_model`, `after_model`, `after_agent`, `wrap_model_call` and
`wrap_tool_call`, each with an `a`-prefixed async twin. An earlier revision
wrote that `AgentMiddleware` "also exposes `dynamic_prompt()`, `hook_config()`
and `configure_trace_policy()`" and that the set was therefore open. **It does
not.** Those three are module-level names in `langchain.agents.middleware` —
two decorators and a process-wide trace-policy setter — not members of
`AgentMiddleware` and not lifecycle hooks — `vars(AgentMiddleware)` on the
installed 1.3.16 returns the six, their six async twins, and `name`,
`state_schema`, `trace_policy`, `transformers`, and none of those three.
ARCHITECTURE.md §19 owns this and carries the check;
`docs/_archive/BIBLE_VERIFICATION_LOG.md` C-3, which asserted the opposite, is
withdrawn in place.

**Three independent retry caps, and they must not be merged:**
`ModelRetryMiddleware` 2 retries on transient API failure,
`CoherenceMiddleware` 2 retries on response quality, and the four-layer
validation stack's shared cap of 3 at the gate (§9.2). Three different
failure modes, three counters, no shared state.

**Prefer built-in middleware wherever it exists.** Custom middleware is
reserved for genuinely domain-specific logic.

### middleware.md · 8.2 — `DMAICGraderMiddleware` — coaching-quality grading

<!-- original lines 143-144 -->
**THERE ARE TWO GRADERS IN THIS ARCHITECTURE. They are not redundant,
and confusing them is a violation.**

<!-- original lines 148-150 -->
| Where | Middleware, inside the executor | The `validation_stack` node |
| When | **Every coaching turn** (`after_agent`) | **Once**, at the gate boundary |
| Rubric | **`COACHING_QUALITY_RUBRIC`** — one, shared | **`PHASE_RUBRIC`** — five, one per phase |

<!-- original lines 152-152 -->
| Sees | One response | The complete field set |

<!-- original lines 155-155 -->
point Layer 2d at `COACHING_QUALITY_RUBRIC`.**

<!-- original lines 157-158 -->
**`COACHING_QUALITY_RUBRIC`** — a single constant in `core/prompts.py`,
identical for all five phases:

<!-- original lines 160-176 -->
```
- Coach must not accept vague or unmeasurable statements as captured fields
- Coach must not invent data, metrics, or values the Belt didn't provide
- Coach must not do the Belt's work (writing their problem statement for them)
- Coach must stay on the current phase's topic
- Coach must challenge weak inputs with specific follow-up questions
- Coach must reference methodology when guiding (not just opinion)
- Coach must show a concrete example of a completed answer before asking
  the Belt to produce theirs
- Coach must not provide external URLs from training data. When
  referencing methodology, retrieve via rag_lookup_methodology and weave
  the content into natural coaching voice
- Coach must not dump raw statistical output without explanation. When
  calling a computation tool, the coach must educate the Belt on the
  concept first, explain why it matters for their project, then run the
  tool
```

<!-- original lines 178-179 -->
**Two criteria bind on every computation tool call**, and the coach
follows a **seven-step** pattern, every tool, every time:

<!-- original lines 181-189 -->
| # | Step |
|---|---|
| 1 | **Educate on the concept** — what this *is*, plain language, real-world analogy, and what the output numbers will mean |
| 2 | **Explain why now** — why the Belt needs it at this point in their project |
| 3 | **Guide data preparation** — what format is needed; check uploads via `rag_lookup_evidence` |
| 4 | **Run the computation** — call the tool |
| 5 | **Interpret their result** — plain language, no jargon (§13) |
| 6 | **Visualise** — `propose_diagram` where applicable |
| 7 | **Coach the next move** — what it means for the project |

<!-- original lines 191-267 -->
**Step 1 is mandatory and is the one most often skipped.** Never assume
the Belt knows what a Cpk, a p-value or a control limit *is*. Teach the
concept and say what the numbers will mean **before** producing any.

**Returning a p-value with no concept and no interpretation is a rubric
failure**, not a style preference. A Belt handed `t_statistic: 4.23,
p_value: 0.001` has a number they cannot act on and cannot defend at a
gate. Because this grader fires **every turn**, the dump is caught before
the Belt sees it.

**Every SKILL.md must carry the seven-step sequence for each computation
tool in its phase's `allowed-tools`** (§8.3). Design detail and worked
per-tool openings: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §43.1.

**Show before asking is also a rubric criterion.** For every field, the
coach shows a concrete example of a completed answer, explains why it
works, then invites the Belt to build theirs in the same shape. Each
SKILL.md carries the example per field.

**Why both exist.** The middleware catches coaching-process failures in
real time — a coach that accepts "poor morale" as a root cause is
corrected before the Belt sees the response, preventing eight further
turns on a weak foundation. The validation node catches document-product
failures a per-turn check cannot see: four Analyse fields can each look
sound while the root cause discusses "error rate" and the baseline it
references is "cycle time." Cross-field and cross-phase consistency is
only visible once the document is complete.

**Mechanism, both graders:**

- Hook: `after_agent` (middleware) / node logic (Layer 2d)
- Model: `grader` role, temperature 0.1 (§4.7)
- `max_iterations=3`. On `max_iterations_reached`, output passes
  through **with a warning flag visible to the Belt**.
- Verdict is per criterion, not overall: `GraderVerdict` carries a
  `list[CriterionVerdict]`, each with `criterion`, `tier`, `status`
  (`"pass" | "warning" | "fail"`) and `feedback` (§9.7).
- Feedback injected back to the coach is **per criterion and specific**
  — never "try again."
- **Layer 2d is belt-level aware** — reads `belt_level` from the case
  record and suppresses Black-Belt-only recommendations for a Green Belt
  (§9.7).

**Rubric management.** Five `PHASE_RUBRIC` constants in
`core/prompts.py`, one per phase, plus the single
`COACHING_QUALITY_RUBRIC`. Layer 2d receives the phase-appropriate
rubric based on `current_phase`. Rubrics evolve from production
experience **without changing the grader mechanism** — that separation
is the point.

The ratified rubrics cover: Define (problem_statement, voc_summary,
business_case, project_scope, team, goal_statement), Measure
(baseline_mean, baseline_sigma, measurement_system_validated,
data_collection_plan, stability), Analyse (root_cause_statement,
root_cause_validation, causal_hypothesis, ruled_out_causes), Improve
(selected_solution, solution_linked_to_root_cause, pilot_result,
implementation_plan), Control (control_plan, sustainability_check,
post_improvement_metrics, improvement_delta, financial_impact_verified,
handover_documented, lessons_learned, transferability). Each criterion
carries its tier (§9.7). Full coverage in `../AGENTIC_ARCHITECTURE_REFERENCE.md` §36;
the tier table is `../AGENTIC_ARCHITECTURE_REFERENCE.md` §35.

**Three criteria are verified deterministically, not by judgment.**
`causal_hypothesis`, `solution_linked_to_root_cause` and
`post_improvement_metrics` are cross-phase reference dicts (§10.6); the
grader reads the referenced phase's gate document from the store and
checks the named field carries the named value. Criteria that depend on
a computation are checked the same way, by scanning
`artifacts["computation_results"]` for the relevant `tool` entry.

**Audit trail integration.** The `on_evaluation` callback writes each
grading iteration to `step_log` (§10.3). Grader internals — iteration
count, accumulated evaluations, attempt tracking — stay **private to
the middleware** and never reach `PhaseState` or `SupervisorState`.

**The Belt does not see the grader loop.** It runs at step 2 of the
nine-step gate, before the interrupt (§9.1).

### middleware.md · 8.3 — `DMAICSkillsMiddleware` — progressive disclosure

<!-- original lines 273-274 -->
Five phase skills under `agent-improve/skills/`, following the
agentskills.io SKILL.md standard:

<!-- original lines 276-282 -->
```
dmaic-define-phase/SKILL.md
dmaic-measure-phase/SKILL.md
dmaic-analyse-phase/SKILL.md
dmaic-improve-phase/SKILL.md
dmaic-control-phase/SKILL.md
```

<!-- original lines 284-307 -->
**Each skill's `allowed-tools` MUST match that phase's tool subset in
§5.2.** Skill and tool binding must not drift apart.

**Progressive disclosure — three levels:**

| Level | When | What loads |
|---|---|---|
| 1 | Startup | Skill descriptions only — **under 2K tokens for all five combined** |
| 2 | On demand | Full phase instructions, when the coach enters that phase |
| 3 | On demand | Reference files, when explicitly needed |

Level 2 is reached by the coach calling a registered `load_skill(name)`
tool.

**Storage backend: `FilesystemBackend`** — git-versioned alongside the
code, so a skill change is reviewable in the same PR as the code that
depends on it. `ContextHubBackend` is deferred.

**Two distinct kinds of skill exist in this repository** and must not
be confused:
- **Development-workflow skills** under `.claude/skills/` — consumed by
  Claude Code (e.g. `/verify-current-version`)
- **Runtime coaching skills** under `agent-improve/skills/` — consumed
  by the coach

### middleware.md · 8.4 — `SummarizationMiddleware` — context compression policy

<!-- original lines 311-311 -->
**LangChain core, used as shipped.**

<!-- original lines 313-345 -->
```python
SummarizationMiddleware(
    model="azure/operational-model",       # gpt-4o-mini for cost
    trigger=("tokens", 100_000),           # ~78% of gpt-4o's 128k window
    keep=("messages", 20),                 # preserve the last 20 turns raw
)
```

**Custom compression functions are BANNED.** Do not hand-write
`compress_messages()` or a `conversation_context` builder — this
middleware provides the trigger, the summarisation call, and the
message-list replacement.

**The policy that makes prose summarisation safe:** facts do not live
in `messages[]`. Anything that must survive compression lives in typed
state:

| Lives in | Field |
|---|---|
| `SupervisorState` | `current_phase`, `phase_index`, `gate_passed` — orchestration only |
| `PhaseState` | `artifacts`, `draft`, `belt_edits`, `step_log`, `citations`, `uploads`, `validator_feedback`, `final` |
| Store | Cross-phase gate documents (§10.2) |

Summarising *conversation* into prose is correct — that is what
conversation is. Summarising *facts* into prose is the failure this
policy prevents.

**Decisions survive compression as captured fields, not as a decision
list.** When the Belt commits a decision it arrives via
`CoachingResponse.fields_captured` and is approved at a gate, which puts
it in `artifacts` and then the store
— all three outside `messages[]`. That is why no `key_decisions` field
is needed here (§10.1).

<!-- original lines 350-352 -->
`ConversationChain`. All are scheduled for removal in LangChain 2.0.
The replacement is checkpointer (thread-scoped) + store (cross-thread)
+ this middleware.

### middleware.md · 8.5 — state injection — injection timing

<!-- original lines 359-362 -->
structured project state at the **top** of the prompt, ahead of the
conversation: captured fields (this phase's `artifacts` plus prior
phases' gate documents from the store), current phase requirements, and
the missing fields reported by `check_gate_status()`.

<!-- original lines 364-382 -->
**Two hooks, and the division of labour is the design.** `before_agent`
composes the block once per turn; `wrap_model_call` prepends the composed
block to each request and recomputes nothing — a pure read, or the
once-per-turn guarantee would be decorative. Both are defined on the
class rather than inherited, so both are its hooks:
`'wrap_model_call' in vars(BeforeModelStateInjection)` is `True`. This
heading read *"`before_model` state injection"* until 2026-09-12, naming
a hook the class does not implement and hiding the one it does.

**Missing fields are computed at injection time, never read from a
stored list.** The middleware derives them the same way the gate does,
so the prompt and `DMAICGateValidator` cannot disagree (§10.1).

Models weight earlier prompt content more heavily. Injecting project
facts *after* the Belt's message lets the response drift toward the
Belt's framing rather than the project's established state.

**Injecting in `messages[]` append order is a violation.** There is no
"just add it to the history" option.

### middleware.md · 8.6 — Middleware that is deliberately NOT used

<!-- original lines 386-390 -->
| Middleware | Why not |
|---|---|
| `HumanInTheLoopMiddleware` | **Two confirmed bugs hit our exact use case.** Edited tool-call args can be silently re-overwritten by the agent re-attempting the original call; and edit/reject are broken in subgraph contexts, where only approve is reliable. Both would silently discard a Belt's correction. Use graph-level `interrupt()` (§1.6, §9.1). |
| `LLMToolSelectorMiddleware` | Per-phase binding (§5.2) already keeps every coach at 8–15 tools. Adding a selector LLM spends a model call solving a problem solved structurally. |
| deepagents `RubricMiddleware` / `SkillsMiddleware` | Pre-1.0 dependency (§4.4). |

### middleware.md · 8.7 — `ModelRetryMiddleware` — the invisible-retry tier

<!-- original lines 394-396 -->
**LangChain core, used as shipped, ADOPTED.** `max_retries=2` with
exponential backoff, on the `wrap_model_call` hook. It wraps each model
call and silently retries transient timeouts and rate limits.

<!-- original lines 398-400 -->
**The keyword is `max_retries`, not `retries`.** `retries=` does not
exist on this class and raises at construction. The full verified
signature is:

<!-- original lines 402-449 -->
```python
ModelRetryMiddleware(*, max_retries=2, retry_on=default_retry_on,
                     on_failure='continue', backoff_factor=2.0,
                     initial_delay=1.0, max_delay=60.0, jitter=True)
```

`ModelRetryMiddleware` and `ToolRetryMiddleware` share a parameter
vocabulary, which is exactly the situation where remembering one and
inferring the other goes wrong — and it did: `retries=` sat in this
stack, uncaught, from adoption until 2026-08-21
(`docs/_archive/BIBLE_VERIFICATION_LOG.md` C-1). (archived to docs/_archive/; canonical: CLAUDE.md §0.10)

**Hand-writing retry plumbing is BANNED.** Do not write
try / except / sleep / counter loops around an LLM call — this
middleware provides the wrap, the backoff, and the attempt counter.

**Its tier is distinct from the fallback chain (§4.8), and the two must
not be conflated:**

| | `ModelRetryMiddleware` | Fallback chain (§4.8) |
|---|---|---|
| Handles | Mechanical failure — the network flaked | Service-level failure |
| Action | Retry **the same call** | **Swap the model**: gpt-4o → gpt-4o-mini → cache → degraded |
| Visible | Never | Degraded mode is visible to the Belt |

This is the invisible-retry tier named in §9.3's self-healing
hierarchy: mechanical, never a coaching event.

**`ToolRetryMiddleware` is the second half of that tier, and is a
different middleware — not a synonym.** LangChain core, used as shipped,
`max_retries=2`, `on_failure="continue"`, on the `wrap_tool_call` hook.

| | `ModelRetryMiddleware` | `ToolRetryMiddleware` |
|---|---|---|
| Hook | `wrap_model_call` | `wrap_tool_call` |
| Catches | Azure OpenAI rate limits, timeouts, transient 5xx | Tool execution failures — Azure Search timeouts, computation tool errors |
| Wraps | Each model call | Each individual tool invocation |

A failed retrieval call is not a failed model call; `ModelRetryMiddleware`
never sees it. Both are needed and neither substitutes for the other.

**`on_failure="continue"` is what keeps the coaching loop alive.** When
retries are exhausted the tool returns a failure result the coach can
read and work around, rather than raising and killing the graph
mid-session.

**The class is `ToolRetryMiddleware`.** `RetryMiddleware` does not exist
in LangChain 1.x — never write it.

### middleware.md · 8.8 — `ContradictionDetectionMiddleware` — the §9.4 check

<!-- original lines 453-454 -->
**Custom, `after_agent`, position 6.** Implements the mid-phase conflict
detection of §9.4. **It reads a flag; it does not detect anything itself.**

<!-- original lines 463-478 -->
**No store read. No LLM call. No field-name matching.** Detection is done by
the coach in the response call that already runs every turn, and arrives as
`CoachingResponse.contradiction_flag` (§10.7). **No tolerance threshold**, per
§9.4.

**The mechanical dict comparison this replaced could not work** — it read
`store.get(..., current_phase)`, which `gate_apply` does not write until phase
end, and it matched on field names where 38 of 41 fields are unique to one
phase. Full analysis: `docs/_archive/DECISIONS.md` §R1. **Never reintroduce the
comparison.**

**Why middleware rather than logic inside the executor node:** the check
polices the executor's own output, so it does not belong to the thing it
polices. As middleware it is a named, LangSmith-visible step
(`ContradictionDetectionMiddleware.after_agent`) and the executor node
stays responsible only for coaching.

### middleware.md · 8.9 — `CoherenceMiddleware` — validation Layer 2a

<!-- original lines 482-485 -->
**Custom, `after_agent`, position 7 — immediately before the grader.**
Implements Layer 2a of the validation stack (§9.2). One LLM call,
`coherence` role, temperature 0.1: is this a real, conclusive statement?
Is it parroting the Belt's own words? Is it on-topic for this phase?

<!-- original lines 487-490 -->
**Layer 2a fires every coaching turn**, which is why it is middleware and
not part of the `validation_stack` node — that node runs once, at the
gate. Layers 2b–2d live there; 2a lives here. One conceptual stack, two
mechanisms (§9.2).

<!-- original lines 492-500 -->
**On failure: Level 1 silent retry, max 2** (§9.3). The Belt never sees a
failed coherence response. On the third failure the turn degrades and
`DMAICGraderMiddleware` is skipped.

**Coherence is NOT a `COACHING_QUALITY_RUBRIC` criterion.** It moved out
of the rubric when this middleware was added. `DMAICGraderMiddleware`
grades coaching *process* only — seven-step computation pattern,
show-first, citations, no external URLs. Any rubric entry for coherence
is stale (§8.2).

## `.claude/rules/module-layout.md`

### module-layout.md · §2 — Where classes are allowed

<!-- original lines 30-33 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

## `.claude/rules/observability.md`

### observability.md · §11 — Tracing and observability

<!-- original lines 9-12 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

### observability.md · 11.2 — `@traceable` on every custom function

<!-- original lines 29-32 -->
LangSmith traces LangChain runnables and LangGraph nodes
automatically. It does **not** trace plain Python functions. Without
`@traceable`, the logic *between* nodes is invisible and a gate failure
surfaces as a 500 with no indication of which layer failed.

### observability.md · 11.3 — What gets traced

<!-- original lines 51-55 -->
metric. High P99 degrades the Belt's experience. The usual outlier is
multi-hop retrieval combined with a grader call on the same turn; the
fixes in order of preference are caching (§4.8 Level 3), a faster
grader model, and reordering the validation stack cheapest-first
(already mandated in §9.2).

## `.claude/rules/prompts.md`

### prompts.md · §6 and §15 — Prompts, and prompt size

<!-- original lines 8-11 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

## `.claude/rules/rag.md`

### rag.md · §7 — RAG and indexes

<!-- original lines 8-11 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

### rag.md · 7.1 — RAG via tool, never via prepended system message

<!-- original lines 17-22 -->
The v1 pattern (`build_knowledge_context()` injected as a
SystemMessage) is DELETED. Retrieval is a tool call the model decides
to make.

This makes RAG accountable in the trace, lets the model control when
to retrieve, and removes the always-on retrieval cost.

### rag.md · 7.2 — Three retrieval tools, one index each

<!-- original lines 35-43 -->
† `improve_case_index`'s vector field **is still named `embedding`** — that
rename is ratified and not yet applied, and it is now the only one left
(§7.3). **Write code against the live schema, not the target schema.**

> **The evidence index's half of this footnote is DISCHARGED.** It read
> *"`improve_evidence_index` has no `phase` or `uploaded_at`"*. It has both,
> and has had since step 6.13 landed §23.2's seven fields (`1396627`,
> 2026-09-10). Live definition read from Azure on 2026-09-12: **12 fields**,
> `phase` filterable, `uploaded_at` filterable **and sortable**.

<!-- original lines 46-48 -->
vector field name locally.** There is no shared retriever. This is why
the `content_vector` / `embedding` asymmetry is safe: no shared code
can hide it, so nothing can fail silently on it.

<!-- original lines 50-52 -->
**`belt_level` filtering is OFF by default** on case history —
over-narrowing risk, since a Green Belt often benefits from Black Belt
cases. Available as an optional parameter.

<!-- original lines 58-61 -->
value is `general` — never `phase`, never `all`.** Both were wrong in
earlier revisions; `phase` does not exist on the index (Azure rejects the
whole query) and no document carries `all` (259 carry `general`). One
fails loudly, the other silently returns a narrowed corpus.

<!-- original lines 64-73 -->
AND the vectorstore declares it.** LangChain's `AzureSearch` promotes a
metadata key to a top-level field only when the key matches a name in
`self.fields` — and `self.fields` defaults to
`[id, content, content_vector, metadata]`, never the live schema. So
writing methodology requires both the correct key name *and*
`fields=KNOWLEDGE_INDEX_FIELDS` on the vectorstore. Either alone leaves
the value buried in the `metadata` JSON blob, unreachable by `$filter`,
with no error raised. This is how `phase_relevance` went unpopulated.
`ingest_knowledge.py` owns this contract; full detail in
`../AGENTIC_ARCHITECTURE_REFERENCE.md` §23.4.

<!-- original lines 75-84 -->
**Retrieval failure is never an empty result.** All three retrieval
functions — `search_knowledge`, `search_cases`, `search_evidence` — return
`[]` only when the search ran and matched nothing; when they fail they
raise `KnowledgeSearchError`. **Never wrap a retrieval call in a bare
`except Exception` that returns `[]`** — that is what hid the `phase`
filter bug, by reporting a broken index as a silent corpus. Catch
`retriever.RETRIEVAL_EXCEPTIONS` and classify via `_fail()`.

Three rules that fall out of it, each of which has already bitten:
- **`RETRIEVAL_EXCEPTIONS` spans two services.** Azure AI Search *and* the

<!-- original lines 86-87 -->
- **A 4xx is `permanent` / `do_not_retry`**, not transient — it is our
  malformed query, and retrying fails identically.

<!-- original lines 91-91 -->
Full rationale: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §27.

<!-- original lines 93-117 -->
**`rag_lookup_evidence` takes no `order_by` argument — and that is now a
DESIGN CHOICE, not a schema constraint.** The distinction is the whole of this
paragraph, because the rule reads the same either way and means something
different.

This prohibition was justified by *"a tool cannot sort on a field the index does
not have"*. **That justification expired on 2026-09-10** and the rule outlived
it by two days: `uploaded_at` is live, filterable and sortable. Ruled at
ARCHITECTURE.md v1.20 (D) — *"`uploaded_at` exists now, and the tool still takes
no `order_by` as a design choice rather than a schema constraint"* — which is
the owner of this fact; S-F15 B3 is discharged there.

**What keeps it out of the signature is §7.4.** Retrieval here is multi-query +
RRF, and a fused rank is what the tool returns; an `$orderby` applied to that
discards the fusion and returns recency, which is a different tool. Wanting
recency is a real requirement and the answer to it is a filter on `uploaded_at`,
not a sort of the fused set.

**A rule whose reason has expired is not the same rule.** It survived here on
its restated form after its basis was gone, which is exactly what a citation
would have prevented.

Never re-sort the returned `top_k` client-side and present it as recency
ordering: that reorders only what was already retrieved, which is a different
result — and it stays wrong after the reindex too.

### rag.md · 7.3 — Index schemas — field names that bind on code

<!-- original lines 121-151 -->
**The canonical full schemas live in `../AGENTIC_ARCHITECTURE_REFERENCE.md` §23**, with types,
vector dimensions, filter and ordering clauses, and the schema-change
procedure. This subsection carries only the facts a *rule* depends on.
It does not duplicate the schema, and it is not the place to record a
schema change — that lands in `../AGENTIC_ARCHITECTURE_REFERENCE.md` §23 first, in the same
commit as the Azure AI Search change (§23.5).

> **THIS SUBSECTION SAID THAT AND THEN TABLED ALL THREE SCHEMAS ANYWAY,
> AND THE COPY WENT STALE.** It carried `phase ← RATIFIED, pending reindex`
> and `uploaded_at ← RATIFIED, pending reindex` and asserted *"`phase` and
> `uploaded_at` are ratified additions, not live fields"*. **Both have been
> live since step 6.13 landed §23.2's seven fields** (`1396627`, 2026-09-10).
> The tables are removed rather than corrected: a schema transcribed into a
> second document is a schema that will disagree with the index again, and
> the rule this subsection states about itself is the one it broke.
>
> **Read the live definition, do not read this file for it.** Three indexes,
> introspected 2026-09-12 against the pinned venv:
>
> ```python
> from azure.search.documents.indexes import SearchIndexClient
> [f.name for f in client.get_index(name).fields]
> ```
>
> | Index | Live fields | Notes |
> |---|---|---|
> | `improve_knowledge_index` | 7 | as §23 specifies |
> | `improve_evidence_index` | **12** | §23.2's seven APPLIED; `uploaded_at` filterable **and sortable** |
> | `improve_case_index` | 19 | vector field still `embedding` — see below |

**The facts a rule depends on**, and nothing else:

<!-- original lines 154-160 -->
It is the only index where this is true, the difference is historical rather
than deliberate, and **`rag_lookup_case_history` must use the live name**. The
rename to `content_vector` is ratified and still pending — delete + recreate,
0 documents, no data loss. **This is the last unapplied schema change of the
three this subsection used to track.** The per-tool local knowledge of vector
field names (§7.2) is what makes the asymmetry safe in the meantime — that was
the reason not to rush it, never a reason to keep it.

<!-- original lines 162-165 -->
**`phase` and `uploaded_at` are SERVER-SET.** `phase` from
`state["current_phase"]` at upload, `uploaded_at` from the server clock. A
Belt-entered value for either makes it unreliable as a filter or a sort key,
which is the whole reason they were promoted out of `metadata`.

<!-- original lines 167-170 -->
**`phase`'s filter defaults OFF.** It exists because two similar documents
uploaded at different phases were otherwise indistinguishable at retrieval
time — but a Control-phase Belt comparing against the Measure baseline is the
normal case, and filtering by default would break it.

<!-- original lines 172-189 -->
**Breaking schema change — LANDED Aug 2026.**
`phase_summary_analyse_phase` was renamed to `phase_summary_analyse` in
Azure AI Search by delete + recreate (the index held 0 documents, so
nothing was lost and no reindex was needed). The pattern
`phase_summary_{phase.lower()}` is now correct for all five phases. A
mapping constant was considered and rejected: fix the name at the
source so no permanent workaround exists.

**The internal phase key is `analyse`, never `analyse_phase`.** The
key was renamed across the codebase in the same change, so
`f"phase_summary_{phase}"` is correct for all five phases with no
mapping constant anywhere. This binds on: `PHASE_ORDER` and every
`phase_order` list, v1 `phase_inputs` keys, `EXTRACTION_MAP`,
`ORCHESTRATOR_CONTEXT_MAP`, `GATE_CHECKS`, `PhaseSummaryRecord`,
`CaseDocument.phases`, the graph node names, and the module path
`backend.phases.analyse`. `AnalysePhaseInput` keeps its name —
`{Phase}PhaseInput` is the convention all five phases follow. Full
scope: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §23.3.

### rag.md · 7.4 — Multi-query + RRF is mandatory, not optional

<!-- original lines 198-206 -->
This is not a nice-to-have. Agent Resolve production experience showed
Azure AI Search ranking unreliable for this corpus — with a single
query it was not reliably returning the right matches. RRF
operationalises cross-variant consistency, which single-query native
ranking cannot do because it does not know the variants exist.

RRF is about fifteen lines and needs no LangChain class. `MultiQueryRetriever`
and `EnsembleRetriever` are BANNED — both moved to `langchain-classic`
in the 1.0 namespace split, and the former is deprecated even there.

### rag.md · 7.5 — Multi-hop policy per phase

<!-- original lines 226-228 -->
**Gate validation never retrieves.** The rubric already encodes the
methodology standards; retrieval there is redundant and adds latency
at exactly the moment the Belt is waiting.

<!-- original lines 230-231 -->
Multi-query and multi-hop compose: multi-query broadens within a hop,
multi-hop deepens across hops.

## `.claude/rules/state.md`

### state.md · §10 — State and storage

<!-- original lines 12-15 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

### state.md · 10.1 — Two state schemas

<!-- original lines 21-21 -->
**`SupervisorState`** — orchestration only:

<!-- original lines 23-32 -->
```python
class SupervisorState(TypedDict):
    messages:        Annotated[list[BaseMessage], operator.add]
    history:         Annotated[list[str], operator.add]
    case_id:         str                                  # canonical id — §10.5
    phase_index:     int                                  # 0=Define … 4=Control
    current_phase:   str
    gate_passed:     dict[str, bool]                      # {"define": True, …}
    final_output:    Optional[dict]                       # set at the Control gate
```

<!-- original lines 34-241 -->
**Seven fields. That is the entire schema.** An eighth requires an
amendment to `../AGENTIC_ARCHITECTURE_REFERENCE.md` (§56), then to this file (§18).

**`gate_passed` is a `dict[str, bool]`, not a `list[str]`.**
`gate_passed["measure"]` is a direct lookup, and the re-approval cascade
(§9.5) sets a phase back to `False` rather than removing it from a list.

**`final_output` is `Optional[dict]`, never `str`** — same rule as
`PhaseState.final` (§10.1, §10.6).

**Artifacts and gate documents are NOT on `SupervisorState`.** They live
in the store (§10.2). Adding them back is a violation.

**`dmaic_plan`, `key_decisions`, `open_items` and `project_context` are
NOT on `SupervisorState` either.** All four were removed as redundant —
each duplicated something an existing mechanism already carries:

| Removed field | What covers it instead |
|---|---|
| `dmaic_plan` | DMAIC order is fixed and static (§1.2), so there is no plan to store. The project's actual plan is Define's gate document in the store plus `improve_case_index` metadata |
| `key_decisions` | Decisions the Belt commits are captured fields, arriving via `CoachingResponse.fields_captured` and approved at a gate. A decision that is not worth a field is not worth replaying into every prompt |
| `open_items` | Outstanding work is derived, not stored: `check_gate_status()` reports which required fields are unpopulated, and the four-layer validation stack (§9.2) is what surfaces blockers |
| `project_context` | Composed at the boundary by each input mapper (§10.2). Define reads the case record from the store; every later phase reads the prior phase's artifacts. The substance is Define's gate document; the framing is the case record and the `improve_case_index` row (§7.3). `before_agent` injection (§8.5) already puts both in front of every coach |

Deriving these on demand is what keeps them correct. A stored
`open_items` list is a second source of truth for gate readiness that
can disagree with `DMAICGateValidator`; a derived one cannot. Adding
any of the four back is a violation.

**`project_context` had no writer at all.** Its comment said "set once
after Define," yet nothing set it, and its only reader —
`define_input_mapper` — runs before Define. Every later phase already
built `phase_context` from the store. **Context is composed at the
boundary, never carried on parent state.**

**`current_phase` and `phase_index` are derived from `gate_passed` and
kept anyway** — a documented exemption for readability, not an
oversight. They are read in dozens of places, and they are written in
exactly one: the output mapper at gate approval (§10.2). **Nothing else
may write them**, and the supervisor is responsible for keeping them
consistent with `gate_passed`. Full rationale: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §5.

**`PhaseState`** — per-phase subgraph state:

```python
from langgraph.managed import RemainingSteps

class PhaseState(TypedDict):
    # identity — copied down by the input mapper, read-only here
    case_id:            str                # from SupervisorState — §10.2
    current_phase:      str                # from SupervisorState — §10.2

    # conversation plumbing
    messages:           Annotated[list[BaseMessage], operator.add]
    history:            Annotated[list[str], operator.add]
    phase_context:      str                # composed at the boundary — §10.2

    # the eighteen content fields
    coaching_plan:      Optional[CoachingPlan]  # ONE typed plan per planner turn
    field_index:        int                # field within the phase
    draft:              dict[str, Any]     # this turn's extraction
    artifacts:          dict[str, Any]     # accumulated for the phase — SEEDED
    step_log:           Annotated[list[dict[str, Any]], operator.add]
    field_log:          Annotated[list[dict[str, Any]], merge_field_log]
    field_status:       dict[str, dict[str, Any]]  # where each field stands — §56 v1.77
    belt_edits:         dict[str, Any]     # Belt corrections at the gate
    turn_count:         int
    final:              dict[str, Any]     # approved gate document — §9.6
    gate_attempts:      int                # retry counter, cap 3
    validator_feedback: list[dict]         # accumulated per-attempt feedback
    rejection_feedback: list[dict]         # Belt reject reasons — §9.1 step 7
    citations:          list[dict]         # sources cited this phase
    uploads:            list[dict]         # files the Belt uploaded this phase
    asks:               list[dict]         # the coach's data requests — §10.9
    hop_results:        list[str]          # ordered hop answers; [] otherwise
    synthesis_output:   Optional[dict]     # SynthesisOutput; None for single-hop

    # engine-managed — declared, never populated by the mapper
    remaining_steps:    RemainingSteps     # recursion_limit − steps taken
```

**Twenty-three author-populated fields — two identity, three plumbing, eighteen
content — plus one engine-managed value, twenty-four declared.**

**`field_status` is where each field stands, STORED** — §56 amendment v1.77,
ruling R5 (2026-09-25), built at step 6.61. Four statuses per field, every one
starting `not taught`: not taught → asked → answered (the Belt's words held
pending; awaiting confirmation = answered and read back) → confirmed (stored).
The current field is the first not confirmed. **Only code changes a status, at
turn end** — never derived from the previous reply's record.

> **Two of those three figures were already stale before `asks` was added, and
> the block above was right the whole time.** This caption read *"Nineteen …
> fourteen content … twenty declared"* while the field list beneath it carried
> fifteen content fields, because **`rejection_feedback` was added at 2.2.23
> (§0.17) and the caption was never updated with it.** §0.17's own table says
> *"20 + 1 managed, 21 declared"*, so this file disagreed with itself four
> hundred lines apart. Corrected here rather than separately: the count was
> being edited anyway, and §0.18's rule is that a figure sync gets said out loud
> rather than slipped in.

**`field_log` is WHEN each captured value changed and what it was before** —
§56 amendment, ratified 2026-09-21, built at step 6.33. One entry per change,
keyed `{phase}:{turn}:{field}` (§10.3's rule), the first capture of a field
included with no prior value. **A third thing, and neither of the other two can
answer for it**: `artifacts` is WHAT is captured and holds only the current
value, `step_log` is HOW a turn went and never held a value at all. Design:
`../AGENTIC_ARCHITECTURE_REFERENCE.md` §6.

**Its reducer is `merge_field_log`, NOT `operator.add`, and the difference is
enforcement.** A deterministic key exists so a replayed turn overwrites its own
entry instead of duplicating it; `operator.add` appends and cannot honour that.
**`step_log` carries the same key and the appending reducer**, so the two
channels must not be assumed to behave alike. **Declaring the reducer is what
makes the log append-only**: a node that returns only this turn's entries into
a channel with no reducer REPLACES the history, silently.

**`artifacts` MUST be SEEDED at phase entry from the case record, never
initialised to `{}`.** The input mapper is the only thing that builds
`PhaseState`, so a constant there is not a default but a ceiling — nothing
captured survives into a second turn. This is the defect step 6.11 fixed one
field over, on `uploads`, and 6.33 fixed here.

**An empty capture is REPORTED by field name and never silently dropped.** A
`None`, `[]`, `{}` or blank string does not enter `artifacts`, is not written
to the case record, and does not overwrite the prior value. The turn's log used
to count captured KEYS while the write filtered on VALUES, so *"captured 1
field(s)"* and *"nothing reached the gate document"* were both true of the same
turn.

**`remaining_steps` is engine-managed and the input mapper MUST NOT populate
it.** Declaring it is what makes LangGraph supply it (`recursion_limit` − steps
taken); undeclared, `state.get("remaining_steps", 10)` returns 10 forever and
the five-hop cap never fires (§3.7).

**Any new field requires an amendment** to `../AGENTIC_ARCHITECTURE_REFERENCE.md` (§56)
**whatever category it is placed in**, same as `SupervisorState`'s eighth.

**`rejection_feedback` carries the Belt's stated reasons for rejecting at the
gate** and is read by the planner on the re-coaching turn. **It is separate from
`validator_feedback` and must stay separate** — the system rejecting the AI's
output and the Belt rejecting the document are two actors at two moments, the
same rule that keeps `validator_feedback` and `belt_edits` apart.

**`case_id` and `current_phase` are COPIED DOWN by the input mapper at phase
entry and are READ-ONLY inside the subgraph.** They are never written back up;
`SupervisorState.current_phase` keeps its single writer, the output mapper
(§10.2). A boundary-time copy is not a second writer. **Check: grep every node
return dict for `case_id` or `current_phase` as a key — any hit is a
violation.**

**`hop_results` and `synthesis_output` MUST be state, not node locals.**
LangSmith traces node inputs and outputs, not interpreter locals, so hop
results held in a local dict are invisible in the trace and lost on
checkpoint restore — which makes the "planned multi-hop is fully
inspectable" claim false. Both are `[]` / `None` on single-hop turns, and
both are declared on `PhaseState` rather than an Analyse-only variant
because `CoachingPlan.retrieval_strategy` may select `multi_hop` in any
phase.

**`coaching_plan` is a typed `CoachingPlan`, produced via
`with_structured_output`** — not a bare dict. `retrieval_strategy` selects
the executor's entire retrieval path, and its `Literal` constraint is what
stops a typo falling through silently to single-hop. `dict[str, Any]` is
acceptable as an interim annotation; typed is preferred. Read
`coaching_plan.retrieval_hops`, never `coaching_plan["retrieval_hops"]`.

**`draft`, `belt_edits` and `final` are `dict`, never `str`.**
String-typed handoffs force downstream nodes to parse prose, which is
the anti-pattern this architecture exists to remove.

**`coaching_plan` is a single typed plan, never `list[dict]`.** One plan per
planner turn, overwritten each time the planner fires. There is no
upfront queue — the planner reads `artifacts` to know what is captured
and what is next, and a plan made at turn 1 cannot anticipate turn 4.

**`gate_attempts` MUST be on `PhaseState` and in the checkpoint.** It is
the shared counter for the four-layer stack (§9.2): incremented per
failed attempt, reset to 0 when the gate passes, escalating at 3.
Holding it in route scope is what produced the v1 "attempts always reset
to 0" bug — it is per phase, because each phase runs its own loop with
its own cap (§1.7, §3.5).

**`validator_feedback` and `belt_edits` are different things and must
stay separate.** `validator_feedback` is what the system's validation
layers said about the AI's output at step 2; `belt_edits` is what the
Belt corrected at step 5. Two actors, two moments (§9.1). The single
`feedback` field they replace conflated them, which would have had the
coach reading the Belt's corrections as validation failures.

**`validator_feedback` is what makes the shared cap of 3 defensible.**
Each entry records attempt, layer, criteria failed, and specific
feedback; the coach reads the full list on retry. Reset to `[]` when the
gate passes. A cap on retries that carry no memory of the previous
failure is just a cap on repetition.

**`citations` and `uploads` are the evidence trail.** Both are written
into the gate document (§9.6) — the coach cites BB eBook sources and the
Belt uploads files, and without these the gate document cannot show what
the phase was grounded in.

**Naming discipline:** `phase_index` (which phase) and `field_index`
(which field within a phase) are distinct. Never reuse `step_index`.

**Use explicit `TypedDict`, not `MessagesState` inheritance**, for
phase states — their dominant content is structured fields, not
conversation. `MessagesState` inheritance is appropriate only for the
debate subgraph, which is not in scope.

### state.md · 10.2 — The store — cross-phase artifacts

<!-- original lines 245-248 -->
**Namespace convention:**
```
("projects", case_id, <kind>)
```

<!-- original lines 250-250 -->
| Namespace | Keys | Contents |

<!-- original lines 252-254 -->
| `("projects", case_id, "case")` | `"record"` | Case framing — title, department, belt level, leader, target date. Written once at session start from `cases/case_{id}.json`, never mid-conversation |
| `("projects", case_id, "artifacts")` | `"define"`, `"measure"`, … | **Each phase's approved gate document** — written by `gate_apply_node` (§9.6) |
| `("projects", case_id, "step_log")` | timestamped | Append-only cross-phase audit trail |

<!-- original lines 256-256 -->
**Blob prefix:** `store/projects/{case_id}/{kind}/{key}.json`

<!-- original lines 258-258 -->
`case_id` is the same value as the graph's `thread_id` (§10.5).

<!-- original lines 260-263 -->
**The `gate_documents` namespace is retired.** A phase's approved
artifacts and its gate document are the same object; two keys holding
the same content is a question about which is authoritative with no
answer. Reintroducing it is a violation.

<!-- original lines 265-293 -->
**Cross-phase handoff uses boundary mappers**, in
`phases/{phase}/mappers.py`:
- The output mapper writes artifacts to the store at gate approval and
  returns **only orchestration-relevant values** to the parent
- The input mapper reads the prior phase's artifacts from the store

**Every input mapper composes `phase_context` from the store** — Define
from the case record, later phases from the prior phase's artifacts. An
input mapper's only dependency is `BaseStore`. Reading context off
parent state, or handing a mapper a blob client, is a violation: the
first creates a parent field to keep in sync, the second puts untracked
I/O in a translation function.

**The `case` namespace is not a second system of record.**
`cases/case_{id}.json` (§10.4) stays authoritative.

**String-interpolating a previous phase's output into the next
phase's prompt is BANNED.** Measure reads Define's baseline metric as a
named field out of a structured gate document, not out of prose. The
field's *value* is a string (§10.6) — the prohibition is on parsing a
value out of an interpolated prompt, not on the value's type.

**The store is not the case index.** Cross-*case* retrieval for yokoten
is `rag_lookup_case_history` (§7.2). The store carries cross-*phase*
data within one project. Two mechanisms, two purposes.

**Ordering constraint:** implement the store **after** `thread_id` is
wired through `graph.ainvoke`. A store is meaningless without working
checkpoint persistence.

### state.md · 10.3 — `step_log` — dicts, never tuples

<!-- original lines 297-298 -->
Every audit entry is a dict with named keys. Tuples are BANNED — field
names make the log self-documenting and queryable.

<!-- original lines 300-315 -->
```python
{"layer": "constraint", "attempt": 2, "status": "failed",
 "reason": "does not address timeline", "decision_excerpt": "..."}

{"service": "gpt-4o", "attempt": 2, "status": "failed",
 "reason": "timeout after 45s", "timestamp": "..."}
```

Everything requiring an audit trail writes here: the four validation
layers (§9.2), each grader iteration via `on_evaluation` (§8.2), and
every fallback attempt (§4.8).

**`artifacts` and `step_log` are separate fields and must stay
separate.** `artifacts` is WHAT was captured; `step_log` is HOW. For a
DMAIC quality system the Belt must be able to show not just what the
root cause was, but how it was determined.

### state.md · 10.4 — Azure Blob — two distinct concerns

<!-- original lines 319-322 -->
**Concern 1: Checkpoints (in-flight graph state)**
- Path: `checkpoints/{case_id}/latest.json` + `history/{id}.json`
- Written by `AzureBlobCheckpointSaver` after every graph node
- Owner: `core/checkpointer.py`

<!-- original lines 324-338 -->
**Concern 2: Case records (system of record)**
- Path: `cases/case_{id}.json`, `registry.json`, `uploads/{case_id}/{file}`
- Written on case create, on gate pass, on file upload — **never
  mid-conversation**
- Owner: `storage/blob.py` via `ImproveBlobClient`

Same Azure Storage account, separate concerns, separate code paths.

**The case blob is NOT updated per turn.** The v1 pattern of
overwriting `case_{id}.json` on every `/ask` is REMOVED. Conversation
history lives in the checkpoint until gate pass.

**Case-vs-registry atomicity:** gate-pass case blob write and registry
update remain two separate writes. Both are covered by the node's
`error_handler` (§3.6).

### state.md · 10.5 — Naming: `case_id` and `artifacts` are the only names

<!-- original lines 342-344 -->
**The project identifier is `case_id`. Everywhere.** State field, store
namespace segment, `thread_id`, blob path, log field, index field,
prose. **`project_id` is retired and may not be reintroduced.**

<!-- original lines 346-360 -->
This was never a design question — it was documents disagreeing with
code. `improve_case_index.case_id`, `improve_evidence_index.case_id`
(§7.3), `cases/case_{id}.json`, `uploads/{case_id}/{file}` and every
storage model already said `case_id`.

**A phase's captured fields are `artifacts`. Everywhere.**

| Retired name | Was | Rule |
|---|---|---|
| `captured_fields` | Prose name in these documents | Never use in prose — say `artifacts` |
| `phase_inputs` | v1 code field name | Never add to v2 code; replaced during the refactor |

`PhaseState.artifacts` holds the fields the Belt has produced in this
phase. Three names for one concept is how a reader ends up believing
there are three things.

### state.md · 10.6 — Every captured field is a string

<!-- original lines 364-367 -->
**All captured fields are `str`.** No phase schema declares a typed
numeric. **Computation tools parse at the point of use** — each of the
20 (§5.2) extracts what it needs from the string it is given and returns
a clear reformatting request to the Belt when it cannot.

<!-- original lines 369-371 -->
```python
baseline_mean = "12.3% invoice error rate, measured over Q2 2026"
```

<!-- original lines 373-396 -->
**The gate document shows the Belt's exact words.** That is a
requirement of a quality system: the Belt must be able to show what they
stated, not what the system parsed out of it.

> **This corrects the previous §10.2, which claimed "Measure reads
> Define's baseline metric as a typed float."** No baseline field has
> ever been typed as a float in any schema in this project. The prose
> promised a guarantee the schemas did not provide.

**The one exception — three cross-phase reference fields are `dict`:**
`causal_hypothesis` (Analyse), `solution_linked_to_root_cause`
(Improve), `post_improvement_metrics` (Control). Each carries the Belt's
content plus `references_phase`, `references_field` and
`references_value`, so the grader verifies the link by reading the
referenced phase's gate document from the store — deterministic, no LLM
judgment in the linkage check. The values inside the dict are still
strings. Design detail: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §42.

**Computation tool output goes in `artifacts["computation_results"]`**
as a list of typed dicts, all values strings. No new top-level
`PhaseState` field, and no per-phase typed destinations — the grader
answers "was a hypothesis test run?" by scanning that list for
`"tool": "t_test"`. Adding typed per-phase computation fields is a
violation (`../AGENTIC_ARCHITECTURE_REFERENCE.md` §7).

### state.md · 10.7 — `CoachingResponse` in, `{Phase}Output` out

<!-- original lines 400-400 -->
**Two schemas, two moments. Never substitute one for the other.**

<!-- original lines 402-488 -->
| | `CoachingResponse` | `{Phase}Output` |
|---|---|---|
| Fires | **Every coaching turn** | **Once**, at `gate_apply` |
| Produced by | The executor, via `response_format=` | Pydantic construction — no LLM |
| Holds | This turn's extraction | The complete gate document |

**`CoachingResponse` — the per-turn schema:**

```python
class CoachingResponse(BaseModel):
    """Structured extraction from each coaching turn."""
    message: str                        # coaching text the Belt sees
    fields_captured: list[dict] = []    # [{field_name: str, value: Any, source: str}]
    citations: list[dict] = []          # sources referenced this turn
    contradiction_flag: Optional[dict] = None   # §9.4 — material contradiction only
```

**`contradiction_flag` carries `prior_field`, `approved_value`,
`approved_phase`, `proposed_value`, `belt_input` when set**, and is produced by
this same `response_format` call — no additional LLM call (§9.4, §8.8).
**Adding any field to `CoachingResponse` requires an amendment** (§18) — it is
load-bearing in the same way `SupervisorState` and `PhaseState` are.

**`value` is `Any`, not `str`, and that is deliberate** — it must carry
both plain string fields and the three cross-phase reference dicts
(§10.6). Typing it `str` would make `causal_hypothesis`,
`solution_linked_to_root_cause` and `post_improvement_metrics`
uncapturable. This is the one place `Any` is correct; the *values inside*
those dicts are still strings.

**The executor node writes the response into state:**

```python
result = await executor.ainvoke(state)
resp = result["structured_response"]              # CoachingResponse

for f in resp.fields_captured:
    artifacts[f["field_name"]] = f["value"]       # str or dict
citations.extend(resp.citations)
```

**`{Phase}Output` schemas are canonical** — `DefineOutput`,
`MeasureOutput`, `AnalyseOutput`, `ImproveOutput`, `ControlOutput`, in
`phases/{phase}/schema.py`. Full definitions and per-phase gate assembly
are in `../AGENTIC_ARCHITECTURE_REFERENCE.md` §40. The binding rules:

- **Every field is `str`** except the three cross-phase reference dicts
  (§10.6)
- **Every schema carries the same four gate-metadata fields** —
  `computation_results`, `acknowledged_gaps`, `citations`, `uploads`
- **Tier 1 fields are assembled with `artifacts["field"]`** — a
  `KeyError` here is correct, because Layer 2b should have blocked the
  gate
- **Tier 2 fields use `artifacts.get("field", "")`**, cross-phase dicts
  `artifacts.get("field", {})` — an empty value records that the Belt
  proceeded without it (§9.7). **Define never uses this pattern on a
  content field** — all 12 are gate-required, so its assembly is direct
  `artifacts["field"]` access throughout (§0.18)
- **Gate assembly must reference every field in the schema.** A field in
  the schema that assembly never sets is a field that silently never
  reaches the store

**Field counts, all five phases:**

| Phase | Total | Gate-required | Tier 2 | `phase_metrics` | Gate metadata |
|---|---|---|---|---|---|
| Define | **18** | **13 — all of them, incl. `metric_definitions`** | **— (no Tier 2)** | 1 | 4 |
| Measure | **15** | 7 | 3 | 1 | 4 |
| Analyse | **14** | 4 | 5 | 1 | 4 |
| Improve | **14** | 4 | 5 | 1 | 4 |
| Control | **17** | 3 | 9 | 1 | 4 |

**Every total rose by one for `phase_metrics`; Define rose by two**, because it
alone carries `metric_definitions`, the registry (§0.20).

**Define's row reads differently on purpose.** Under Option A every Define
field is gate-required, so its count is the whole content set rather than a
tier within it (§0.18). The other four rows are Tier 1 counts.

**Three fields are on all five schemas:** `issues_and_barriers`,
`secondary_metrics` and **`phase_metrics`** (§0.20). `issues_and_barriers`
is gate-required everywhere; `secondary_metrics` is Tier 2 in the four
tiered phases and **gate-required in Define**; `phase_metrics` is present
on all five and carries `"none this phase"` rather than an empty list
where the phase engaged no metric. Adding a field to one phase without
considering the other four is how the cross-phase gaps in the eBook
extraction arose in the first place.

### state.md · 10.8 — Structured dict fields; FMEA is not tracked

<!-- original lines 492-493 -->
**Three Tier 1 fields are structured dicts**, distinct from the three
cross-phase reference dicts of §10.6:

<!-- original lines 495-499 -->
| Field | Phase | Sub-fields |
|---|---|---|
| `process_map_sipoc` | Define | `suppliers`, `inputs`, `process_steps`, `outputs`, `customers`, `process_metrics` |
| `detailed_process_map` | Measure | `steps`, `cycle_times`, `resources`, `value_vs_waste`, `measurement_points`, `baseline_metrics` |
| `control_plan` | Control | `documentation`, `monitoring`, `response`, `training`, `aligning_systems` |

<!-- original lines 501-505 -->
**The grader checks every sub-field is populated.** A `process_map_sipoc`
with four of six keys filled is the partial-map failure the field exists
to catch — a Belt who maps steps 3–5 of a seven-step process produces a
project that cannot show improvement, because the baseline never covered
the whole thing.

<!-- original lines 507-508 -->
**Three fields carry one measurement thread across three phases**, and
the grader verifies the same measurement points carry different values:

<!-- original lines 510-560 -->
```
Define   process_map_sipoc["process_metrics"]        — WHAT is measured
Measure  detailed_process_map["baseline_metrics"]    — the BEFORE values
Control  post_improvement_metrics                  — the AFTER values
```

**`stability_assessment` is Tier 1 and is checked BEFORE capability.** An
unstable process has special causes, so a baseline Cpk computed across
them is an average of two different processes, not a capability figure.
Coaching order: stability → special causes if unstable → capability.

**`experiment_justification` is Tier 1 and does not require an
experiment.** It requires a decision, stated as one of three: DOE
conducted, simplified one-factor experiment, or no experiment needed
because the solution follows from root cause analysis. All three are
valid; the failure it catches is drifting past the question, not
skipping DOE. Design detail: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §41.

**`control_plan` is `dict`, never `str`.** Five sub-plans, all required:

```python
control_plan: dict = {
    "documentation":    str,   # updated process maps, SOPs, training manuals
    "monitoring":       str,   # what charts, what frequency, what limits, who checks
    "response":         str,   # what happens when monitoring signals a problem
    "training":         str,   # who needs training, in what format, verified how
    "aligning_systems": str,   # HR, IT, budget changes needed to sustain
}
```

**Tier 1 — the gate requires the dict, and the grader checks all five
sub-plans are populated.** A single string cannot show that four were
done and one was skipped, and a Training Plan written but never delivered
is the most common real Control failure. Design detail: `../AGENTIC_ARCHITECTURE_REFERENCE.md`
§41.

**FMEA has no field in any schema, and none may be added.** Not
`fmea_summary`, not `updated_fmea`, not an FMEA sub-key anywhere.

FMEA is heavy manufacturing methodology built around severity ×
occurrence × detection scoring of physical failure modes. Agent Improve's
typical case is service or transactional DMAIC, where `driver_priority_summary`
and `vital_few_drivers` already do the prioritisation job without the RPN
overhead. Requiring an FMEA would push every Belt through a heavy
artefact to satisfy a field — the mechanical field-filling §9.7 exists to
prevent.

**If a Black Belt performs one, it lives in `uploads`** as an attached
document, and the BB SKILL.md may present it as an available technique.
The schema does not track it, the grader does not ask for it, and no gate
blocks on it. Full rationale: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §41.

## `.claude/rules/testing.md`

### testing.md · §12 — Evaluation and regression testing

<!-- original lines 7-10 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

### testing.md · 12.1 — The eval suite is built alongside the refactor

<!-- original lines 16-20 -->
Not before it. Establishing a baseline against the current system
would produce a baseline of "bad." The suite becomes load-bearing when
the coach, retrieval tools, and grader are wired — that is when output
quality changes. Infrastructure steps (graph structure, state schemas,
checkpointer) do not affect coaching quality.

<!-- original lines 22-24 -->
**The dataset is authored jointly, not generated.** Coaching quality
judgments are domain judgments; a generated dataset measures agreement
with a model rather than correctness.

### testing.md · 12.2 — Minimum viable suite

<!-- original lines 37-40 -->
**Rubrics and the eval dataset are complementary, not duplicative.**
Rubrics (§8.2) define what good looks like *for the grader*, in
production, at every gate. The eval dataset tests whether the whole
system produces good outcomes, in CI, at every commit.

### testing.md · 12.3 — Structured errors

<!-- original lines 44-54 -->
All external service failures use one schema, in `core/errors.py`:

```python
class AgentImproveError(BaseModel):
    error_code: str              # "TIMEOUT", "RATE_LIMIT", "AUTH_FAILURE", …
    severity: str                # "transient" | "permanent"
    retry_recommendation: str    # "retry_after_backoff" | "do_not_retry" | …
    affected_identifier: str
    message: str
    timestamp: datetime
```

## `.claude/rules/tools.md`

### tools.md · §5 — Tools

<!-- original lines 9-12 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

### tools.md · 5.1 — The universal eight

<!-- original lines 22-63 -->
Passed to every phase executor via `tools=`:

```
rag_lookup_methodology(query: str, phase: str, top_k: int = 10) -> list[Document]
  improve_knowledge_index. Multi-query + RRF. Filters phase_relevance.

rag_lookup_evidence(query: str, case_id: str, top_k: int = 10) -> list[Document]
  improve_evidence_index. Multi-query + RRF. Filters case_id.

rag_lookup_case_history(query: str, top_k: int = 10,
                        exclude_current_case: bool = True) -> list[Document]
  improve_case_index. Multi-query + RRF. Yokoten — cross-case learning.

propose_template(template_type: str, fill_data: dict) -> str
  Fill-in template for the team. Types: problem_statement, sipoc,
  data_collection_plan, fishbone, etc.

propose_diagram(diagram_type: str, data: dict) -> dict
  Structured diagram JSON (NOT SVG). Types and schemas in
  core/diagrams.py. Frontend renders via SVG template library.

check_gate_status() -> dict
  Current phase gate readiness — which required fields are populated,
  which are missing.

request_human_approval(reason: str) -> str
  Triggers an interrupt awaiting human decision, beyond standard gate
  submission.

load_evidence_series(blob_path: str, column: str) -> dict
  A column's typed values plus n, mean, sigma, min, max — RE-PARSED from the
  case blob with step 6.11's parser. Retrieval finds WHICH file; this loads
  THE VALUES. Ratified 2026-09-09; built at step 6.12.
```

**`load_evidence_series` is universal rather than a computation tool, and that
is a classification rather than an exception.** §5.2's twenty are pure functions
with no I/O; this reads a blob. **The universal set is already where the
I/O-performing tools live** — all three `rag_lookup_*` call Azure AI Search,
this one calls Azure Blob. It stores no parsed values and re-parses instead,
because a second copy of the table is the drift the single-authority rule exists
to prevent.

<!-- original lines 66-75 -->
`search_improve_cases` and `search_improve_evidence`** — the three `@tool`
functions in `knowledge/tools.py` today. No v2 code may reference them.

> **Corrected 2026-08-21.** This rule previously named `search_methodology`
> and `search_evidence`. **`search_methodology` exists nowhere in the
> codebase**, and **`search_evidence` is a live retriever function that §7.2
> requires to keep existing** — so this rule and §7.2 contradicted each other,
> and a grep for the retired names would have passed while every real one
> survived. **Verification depends on the literal strings**, which is why a
> wrong name here is not cosmetic.

<!-- original lines 83-87 -->
**Four further tools in `knowledge/tools.py` are neither retired nor bound** —
`search_resolve_cases`, `search_resolve_knowledge`, `search_resolve_evidence`,
`search_flow_vsm`. Read-only cross-agent tools, a distinct third category,
deliberately bound to no coach. Do not delete them and do not bind them:
`../AGENTIC_ARCHITECTURE_REFERENCE.md` §29.4 states the three rules that bind first.

<!-- original lines 91-94 -->
(§4.6) — the coach emits `fields_captured` as structured output on every
turn, and the executor node writes each entry to `artifacts`. A tool
would make capture a decision the coach might skip; structured output
makes it part of every response by construction.

### tools.md · 5.2 — Per-phase tool binding

<!-- original lines 98-100 -->
**Tool sets are per phase, not universal.** Tool selection quality
degrades past roughly 10–15 tools per agent; per-phase binding keeps
every coach inside the tractable range.

<!-- original lines 102-108 -->
| Phase | Universal | Computation tools | Total |
|---|---|---|---|
| Define | 8 | `calculate_expected_savings` | **9** |
| Measure | 8 | `calculate_sigma_level`, `calculate_cpk`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq`, `calculate_grr`, `calculate_sample_size_proportion`, `calculate_sample_size_mean` | **16** |
| Analyse | 8 | `t_test`, `chi_square_test`, `anova`, `pearson_correlation`, `linear_regression` | **13** |
| Improve | 8 | `calculate_doe_main_effects` | **9** |
| Control | 8 | `xbar_r_chart_limits`, `imr_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk` | **13** |

<!-- original lines 110-112 -->
**No phase exceeds 16 tools**, and **as of 2026-09-09 the maximum is 16
(Measure) — the ceiling exactly.** If a new tool would push a phase past
16, that is an amendment to `../AGENTIC_ARCHITECTURE_REFERENCE.md` (§56), not a routine addition.

<!-- original lines 114-120 -->
> **⚠ REVISIT THE CEILING BEFORE A NINTH UNIVERSAL TOOL, NOT AFTER.**
> `load_evidence_series` took Measure from 15 to 16. **There is no margin left**,
> and the two universal tools still unbuilt — `check_gate_status` and
> `request_human_approval` — are already inside the eight and inside this count.
> A per-phase total that is legal only because nothing else has been added is a
> constraint with no margin, and **the margin is what usually gets discovered by
> exceeding it.**

<!-- original lines 122-135 -->
**`imr_chart_limits` is the individuals / moving-range chart** and is
the right choice whenever the Belt has **one measurement per period**
rather than batches — the common case in service and transactional work.
Never coach a Belt into inventing subgroups to fit a batch chart;
subgroups that were not collected as subgroups produce meaningless
limits.

**Each of the 20 computation tools is a separate named tool.**
Parameterised grouping (one `calculate_sample_size(type, ...)` with a
mode argument) is BANNED — it moves the selection burden into the
argument space, and models handle distinct named tools more reliably
than mode arguments.

**All 20 are pure functions.** No LLM call, deterministic, unit-tested.

## `.claude/rules/ui.md`

### ui.md · §13 — UI and language rules

<!-- original lines 8-11 -->
> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

