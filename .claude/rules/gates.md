---
paths:
  - "agent-improve/backend/validation/**"
  - "agent-improve/backend/phases/gate_assembly.py"
  - "agent-improve/backend/phases/gate_registry.py"
  - "agent-improve/backend/phases/*/validate.py"
  - "agent-improve/backend/phases/*/schema.py"
---
# §9 — Validation and gates

> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

## 9. VALIDATION AND GATES

### 9.1 — The nine-step HITL gate pattern

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

### 9.2 — The four-layer validation stack

All four run inside step 2, before the interrupt.

| Layer | Checks | Mechanism | Model | Fires |
|---|---|---|---|---|
| **2a. Coherence** | Real, meaningful, conclusive? Catches gibberish, vague non-answers, self-contradiction, off-topic replies, parroting the Belt's own words. **Implemented by `CoherenceMiddleware` (§8.9), not by the `validation_stack` node** | Lightweight LLM | `coherence`, temp 0.1 | **Every coaching turn** |
| **2b. Field presence** | All **Tier 1** fields for this phase populated? (`DMAICGateValidator`) | **Deterministic** | No LLM | Gate boundary only |
| **2c. Constraint** | Addresses budget / timeline / risk / measurement? | Lightweight LLM | `constraint`, temp 0.1 | Gate boundary + mid-conversation for key decisions |
| **2d. Quality rubric** | Does the **gate document** meet DMAIC standards per criterion? **Tier 1 fails, Tier 2 warns.** Uses `PHASE_RUBRIC` — *not* `DMAICGraderMiddleware`, which is a different grader (§8.2) | LLM grader | `grader`, temp 0.1 | Gate boundary only |

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

### 9.3 — Where each check fires, and what the Belt sees

| Layer | Every turn | Key decision moments | Gate boundary |
|---|---|---|---|
| 2a Coherence | ✅ | ✅ | ✅ |
| 2b Field presence | ❌ | ❌ | ✅ |
| 2c Constraint | ❌ | ✅ | ✅ full check |
| 2d Quality rubric | ❌ | ❌ | ✅ last |
| Mid-phase contradiction (§9.4) — **semantic as of §R1; cadence reviewed and kept, the coach runs every turn** | ✅ | ✅ | ✅ |

**The self-healing hierarchy — and the transparency principle:**

| Level | Trigger | Behaviour | Belt sees | Retry |
|---|---|---|---|---|
| 1 — Silent | Coherence failure mid-turn | System retries internally | **Invisible** | Max 2, then degraded mode |
| 2 — Coached | Constraint failure on a Belt proposal | Coach teaches toward a better formulation | Transparent, collaborative | **No cap** — this is dialogue, not a loop |
| 3 — Validated | Full four-layer check at the gate | Belt sees pass/fail, corrects, approves | Transparent, Belt approves | Max 3, accumulated feedback |
| 4 — Escalated | Attempts exhausted | System defers with unresolved constraints named | Transparent, Belt is arbiter | None |

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

### 9.4 — Mid-phase conflict detection — auto-flag, no threshold

The policy advisory does **not** only run at gate boundaries. It runs
**before each coach response is returned to the Belt**.

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

### 9.5 — The re-approval cascade

If the Belt confirms a new value, the affected phase **and every
downstream phase that depends on it** return to a provisional state
and require re-review.

This is deliberately heavier than a soft override. A root cause
validated against a baseline of 4.2 is not automatically valid against
3.8. Silent invalidation of downstream analysis is not acceptable.

**The cascade has a hard dependency on §3.6.** When it fires, the
affected phase's `error_handler` compensating logic MUST run to clean
up stale values already written to Azure Blob and `improve_case_index`.
A cascade that marks phases provisional but leaves published values in
place is worse than no cascade — state and index then disagree,
silently.

### 9.6 — `gate_apply_node` writes the gate document TWICE

**This is the write the whole store-mediated handoff depends on.** Every
cross-phase read in §10.2 assumes the previous phase's gate document is
in the store. `gate_apply_node` is what puts it there.

After Belt approval, at step 7, `gate_apply_node` writes to **both**:

```python
# 1. The store — what the next phase's input mapper reads
store.put(("projects", case_id, "artifacts"), phase_name, gate_document)

# 2. PhaseState — so the checkpoint is self-sufficient for crash recovery
return {"final": gate_document, "gate_attempts": 0, "validator_feedback": []}
```

**Both writes are required.** The store write and the checkpoint commit
are separate operations; a crash between them would leave state saying
the gate was not applied while the store says it was. `final` holding
the same dict means the resumed graph can see what was approved without
re-reading the store — which is why `final` is a `dict` and not a `str`.

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

**`gate_attempts` and `validator_feedback` reset here, and only here.**
The retry budget is per gate passage.

### 9.7 — Two tiers of field; the grader gains a `warning` verdict

**Layer 2b and Layer 2d must not be able to contradict each other.**
Before this rule, the gate blocked on a required-field list while the
grader graded against a rubric covering a different set — so a phase
could pass the gate and then be failed by the grader on a criterion the
gate never asked for.

**Every rubric criterion is classified into one of two tiers.**

| Tier | Layer 2b | Layer 2d | Belt |
|---|---|---|---|
| **Tier 1 — gate-required** | **Blocks** | Can `fail` | Must supply it |
| **Tier 2 — rubric-recommended** | Not checked | At worst `warning` | Add it, or proceed with an acknowledged gap |

**Gate-required, by phase:**

| Phase | Gate-required fields | Count |
|---|---|---|
| Define | **All 13 — no tier split (Option A).** `business_case`, `team` (**list[dict]**), `voc_summary`, `problem_statement`, `baseline_estimate`, `project_scope` (**dict**), `goal_statement`, `target_value`, `target_date`, `secondary_metrics`, `process_map_sipoc` (**dict**), `issues_and_barriers`, **`metric_definitions`** (the metric registry, §10.7) | **13** |
| Measure | `baseline_mean`, `data_collection_plan`, `driver_priority_summary`, `vital_few_drivers`, `detailed_process_map` (**dict**), `stability_assessment`, `issues_and_barriers` | 7 |
| Analyse | `root_cause_statement`, `root_cause_validation`, `practical_significance`, `issues_and_barriers` | 4 |
| Improve | `selected_solution`, `pilot_result`, `experiment_justification`, `issues_and_barriers` | 4 |
| Control | `control_plan` (**dict**, 5 sub-plans), `post_improvement_metrics`, `issues_and_barriers` | 3 |

> **Define is the one phase with no Tier 2** (Option A, ratified 2026-08-26 —
> §0.18). **Thirteen gate-required, twelve coached** — `metric_definitions` is
> captured inside position 5's conversation rather than at its own coached
> position, so `field_index` still walks twelve (§0.20). Its row is a **complete
> field set, not a tier**; the other four rows
> are Tier 1 sets and those phases keep both tiers. Everything below about how
> the two tiers interact applies to those four.

**`issues_and_barriers` is gate-required in every phase.** Every real project has
blockers; a Belt reporting none has not looked. If there genuinely are
none, the Belt writes "none identified at this stage" — a conscious
statement, not a silent skip.

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

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §33, §34, §35, §36, §37.*


## Never

*§14's bans that belong to this file — 13 of 95, each landing in exactly one rule file. Verbatim, with their citations.*

- Never let a gate pass with a Tier 1 failure; never let a Tier 2 gap
  block a gate (§9.7)
- Never drop a Tier 2 gap the Belt proceeded past — it goes in
  `acknowledged_gaps` in the gate document (§9.6, §9.7)
- Never recommend DOE to a Green Belt (§9.7). The X-Y matrix and the
  statistical problem statement are no longer belt-gated — both are
  required of all Belts, as fields (§9.7)
- Never let the coach return raw computation output without explaining
  the purpose beforehand and interpreting the result afterwards — it is a
  `COACHING_QUALITY_RUBRIC` criterion, checked every turn (§8.2)
- Never approve a gate without writing the gate document to **both** the
  store and `PhaseState.final` (§9.6)
- Never let the Belt see the grader loop
- Never add a tolerance threshold to mid-phase conflict detection
- Never cap Level 2 coached improvement with a retry limit
- Never make the policy advisory blocking
- Never commit a checkpoint before Belt approval
- Never use `HumanInTheLoopMiddleware` for gates
- Never run retrieval during gate validation
- Never downgrade the coherence or constraint checks to format checks
