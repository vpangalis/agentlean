---
paths:
  - "agent-improve/backend/validation/**"
  - "agent-improve/backend/phases/gate_assembly.py"
  - "agent-improve/backend/phases/gate_registry.py"
  - "agent-improve/backend/phases/*/validate.py"
  - "agent-improve/backend/phases/*/schema.py"
---
# §9 — Validation and gates

> Never renumber — `deprecated_patterns.yaml` cites these (§0.2). History/rationale: `docs/_archive/rules_rationale_2026-09-25.md`.

## 9. VALIDATION AND GATES

### 9.1 — The nine-step HITL gate pattern

| Step | What happens |
|---|---|
| 1. Executor runs | Coach responds; extraction captures fields |
| 2. **Validation stack** | Four layers, cheapest first (§9.2), accumulated feedback. **Checks the AI's work. The Belt does not see this loop.** |
| 3. Interrupt fires | `gate_review_node` pauses; Belt sees validated output |
| 4. Belt reviews | Checks AI-captured values |
| 5. Belt edits *(optional)* | Corrects wrong fields |
| 6. **Policy advisory** | Checks the **Belt's edits** against required-field policy, cross-phase consistency and approved values (§9.4). **Non-blocking.** |
| 7. Belt approves | Gate document assembled and written to the store **and** `PhaseState.final` (§9.6) |
| 8. Checkpoint saves | State committed **only now** |
| 9. Next phase | The subgraph reaches `END`; the parent's static edge advances. **The supervisor makes no decision** (§3.1) |

### 9.2 — The four-layer validation stack

All four run inside step 2. **Cheapest first; each fires only if the
previous passes.**

| Layer | Checks | Mechanism | Fires |
|---|---|---|---|
| **2a. Coherence** | Real, conclusive, on-topic, not parroting the Belt | `CoherenceMiddleware` (§8.9), `coherence` role, temp 0.1 | **Every coaching turn** |
| **2b. Field presence** | All **Tier 1** fields populated (`DMAICGateValidator`) | **Deterministic**, no LLM | Gate boundary only |
| **2c. Constraint** | Addresses budget / timeline / risk / measurement | `constraint` role, temp 0.1 | Gate + key decisions mid-conversation |
| **2d. Quality rubric** | Gate document vs `PHASE_RUBRIC`, per criterion. **Tier 1 fails, Tier 2 warns** | `grader` role, temp 0.1 | Gate boundary only |

- **2a is middleware; 2b–2d are the `validation_stack` node.** Do not move
  either across.
- **Layer 2d is NOT `DMAICGraderMiddleware`** — two graders (§8.2).
- **The cap is 3, SHARED across all four layers** — not per layer. Counter
  `PhaseState.gate_attempts`, feedback `PhaseState.validator_feedback`
  (§10.1); neither in route scope. Feedback is specific, never *"try again."*
- **2a and 2c stay LLM calls** — settled; never re-optimise into a regex or
  format check.
- **Per-phase constraint sets** are `{PHASE}_CONSTRAINTS` in
  `core/prompts.py`; Measure is covered by its rubric. **Value-dependent
  constraints are required** where a constraint depends on another field
  (e.g. risk mitigation only when `risk_level == "low"`).
- Every attempt at every layer is logged to `step_log` as a dict (§10.3).

### 9.3 — Where each check fires, and what the Belt sees

| Layer | Every turn | Key decision moments | Gate boundary |
|---|---|---|---|
| 2a Coherence | ✅ | ✅ | ✅ |
| 2b Field presence | ❌ | ❌ | ✅ |
| 2c Constraint | ❌ | ✅ | ✅ full check |
| 2d Quality rubric | ❌ | ❌ | ✅ last |
| Mid-phase contradiction (§9.4) — **semantic as of §R1; cadence reviewed and kept, the coach runs every turn** | ✅ | ✅ | ✅ |

**The self-healing hierarchy:**

| Level | Trigger | Belt sees | Retry |
|---|---|---|---|
| 1 — Silent | Coherence failure mid-turn | **Invisible** | Max 2, then degraded mode |
| 2 — Coached | Constraint failure on a Belt proposal — coach teaches | Transparent | **No cap** — dialogue, not a loop |
| 3 — Validated | Full four-layer check at the gate | Pass/fail, Belt corrects and approves | Max 3, accumulated feedback |
| 4 — Escalated | Attempts exhausted — defers with unresolved constraints named | Transparent, Belt is arbiter | None |

**Transparency is the default; silent retry is the narrow exception —
coherence only.**

### 9.4 — Mid-phase conflict detection — auto-flag, no threshold

The advisory also runs **before each coach response reaches the Belt**,
by semantic detection (`docs/_archive/DECISIONS.md` §R1):
- **The coach** compares the Belt's input against prior committed values and
  sets `CoachingResponse.contradiction_flag` (§10.7) on a **material**
  contradiction — instruction in each SKILL.md (§8.3). **No additional LLM
  call.**
- `ContradictionDetectionMiddleware` (§8.8) **raises `HITLInterrupt`**; the
  coach's response is suppressed. Payload: field, approved value and phase,
  proposed value, the Belt's words, two options.
- **Flag only material numeric or categorical contradictions of committed
  values** — never rephrasing, never refinement of a not-yet-committed value.
- Detection is best-effort; the all-gate-fields tab (§13) is the human
  backstop.

**The Belt's two options:** update the approved value (that phase's gate
document becomes provisional; downstream phases need re-review), or keep it
(no state change).

**There is NO tolerance threshold, and none may be added. Any change to a
gate-approved value is a mini-gate, never a silent overwrite.**

### 9.5 — The re-approval cascade

A confirmed new value returns the affected phase **and every downstream
phase that depends on it** to provisional, requiring re-review.

**Hard dependency on §3.6:** the affected phase's `error_handler` MUST run to
clean up stale values in Azure Blob and `improve_case_index`.

### 9.6 — `gate_apply_node` writes the gate document TWICE

At step 7, `gate_apply_node` writes to **both** — neither alone is enough:

```python
store.put(("projects", case_id, "artifacts"), phase_name, gate_document)
return {"final": gate_document, "gate_attempts": 0, "validator_feedback": []}
```

Store path: `store/projects/{case_id}/artifacts/{phase}.json`.

**The gate document contains, and nothing may be omitted:** all captured
fields (strings, §10.6) and the cross-phase dicts from `artifacts`;
`computation_results`; `citations`; `uploads`; `acknowledged_gaps` (§9.7).

**`gate_attempts` and `validator_feedback` reset here, and only here.**

### 9.7 — Two tiers of field; the grader gains a `warning` verdict

**Layer 2b and Layer 2d must not be able to contradict each other** — every
rubric criterion is in one tier:

| Tier | Layer 2b | Layer 2d | Belt |
|---|---|---|---|
| **Tier 1 — gate-required** | **Blocks** | Can `fail` | Must supply it |
| **Tier 2 — rubric-recommended** | Not checked | At worst `warning` | Add it, or proceed with an acknowledged gap |

**The per-phase sets are owned by `phases/*/schema.py`**
(`DEFINE_REQUIRED_FOR_GATE_FIELDS`, `{PHASE}_TIER_1_FIELDS`,
`{PHASE}_TIER_2_FIELDS`), registered in `phases/gate_registry.py` — never
tabulate them here. **Define has no Tier 2** (Option A, §0.18); every Define
field is gate-required.

**`issues_and_barriers` is gate-required in every phase** ("none identified
at this stage" is a valid answer). **It is NOT `acknowledged_gaps`** —
Belt-stated blockers vs system-recorded skipped Tier 2 fields.

**`CriterionVerdict` (designated for `validation/schemas.py`, §2; not yet
built) carries `criterion`, `tier` (1 or 2), `status`
(`Literal["pass", "warning", "fail"]`) and specific per-criterion
`feedback`.** A gate MAY pass with warnings; **NEVER with
failures.** Only Tier 1 criteria may `fail`.

**A Tier 2 gap the Belt proceeds past MUST be recorded** —
`"acknowledged_gaps": ["baseline_sigma — Belt accepted gap"]` — and the next
phase's planner reads it.

**The grader is belt-level aware** (`belt_level` on the case record). **DOE is
the only belt-gated item** — a Tier 2 recommendation for Black Belts only. The
X-Y matrix (`driver_priority_summary`, Tier 1), `statistical_problem_statement`
(Tier 2, Analyse) and `stability_assessment` (Tier 1) apply to all Belts;
FMEA is not tracked (§10.8).

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
