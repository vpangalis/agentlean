# G-23 + G-31 — `DMAICGateValidator` and `check_gate_status()` design

> **DRAFT — for founder ruling, not ratified.** Nothing below is a founder ruling. Every
> signature, model and routing choice is a *proposal*; where the design is open it is offered
> as options with a recommendation. Read at HEAD `44d111a`, 2026-09-25. Paths are relative to
> `agent-improve/`. Unblocks (if ruled): procedure step 7.1 (G-23 milestone), inherited by 7.2.

## 1. What the documents say (the ratified frame)

| Source | What it fixes |
|---|---|
| ARCH §34 (L3639–3742) | Four layers, cheapest first; 2a is `CoherenceMiddleware`, 2b–2d are the `validation_stack` node; cap 3 **shared**, counter `PhaseState.gate_attempts`, feedback `PhaseState.validator_feedback`; every attempt → `step_log` |
| ARCH §35 (L3743–3878) | Tier 1 blocks at 2b and may `fail` at 2d; Tier 2 at worst `warning`. **Define has no Tier 2** (Option A) |
| ARCH §62.7 S-C26 (L9796–9832) | Static-method namespace, no state; B1 deterministic presence, B2 Tier 1 only, B3 runs first, **B4 same answer as `check_gate_status()`**. G-23: names, signatures, return shapes undefined |
| ARCH §60.3 S-F21 (L9219–9260) | `check_gate_status() -> dict`, derived at call time (B1), same derivation as 2b (B2), Tier 1 / Tier 2 progress separate (B3). G-31: zero-arg signature must know phase + `artifacts`; needs an `args_schema` |
| ARCH §62.1 S-C20 (L9681–9723) | `CriterionVerdict{criterion, tier, status: Literal["pass","warning","fail"], feedback}` — specified, **not built** |
| ARCH §62.9 S-F26 (L9868–9915) | Layer 2d = one `grader` call @0.1 **plus deterministic lookups** (B2 cross-phase, B3 `computation_results`, B4 every dict sub-field, B7 measurement thread) |
| ARCH §58.14 S-F05 + S-F13 DP2 | Pass → `goto="gate_review"`; fail under cap → `goto="planner"`; at cap → escalation via `Command.PARENT`; **`gate_attempts` +1 once, at entry** |
| ARCH §33 / §33.1 (L3518–3638) | Graph-level `interrupt()` in `gate_review`; `gate_apply` branches approve/reject; `HumanInTheLoopMiddleware` banned |
| `.claude/rules/gates.md` §9.2, §9.7 | Same as §34/§35; `CriterionVerdict` "designated for `validation/schemas.py`; not yet built" |
| CLAUDE.md §0.24 | Prefer framework primitives → `interrupt()` + `Command(resume=)`, `ToolRuntime` (§6 below) |

## 2. What exists today (IS)

| Item | Where | Fact |
|---|---|---|
| `DMAICGateValidator` | `backend/validation/gate_validator.py` | **File absent.** `.claude/config/fact_owners.yaml:83–89` pre-registers it; `drift-check.py:134` reports `PENDING` |
| One missing-field computation | `backend/phases/gate_registry.py:298` | `missing_gate_fields(phase: str, data: dict[str, Any]) -> list[str]` — Tier-1 names + `missing_structured` sub-field entries (`"process_map_sipoc.customers"`, `"team[0].role"`) |
| Its callers | `phases/define/validate.py:97`, `middleware/state_injection.py:226` | 2b and the prompt already share **one** function (step 6.3) — B4 is met today without the class, but nothing asserts it |
| Tier registry | `gate_registry.py:59–94` | `GateSpec(model, tier_1, tier_2, assemble)`; Define `tier_2 = ()` |
| Emptiness rule | `gate_registry.py:201` | `_is_empty`: `None`, blank str, empty container |
| Define gate list | `phases/define/schema.py:71` | `DEFINE_REQUIRED_FOR_GATE_FIELDS` = 12 coached + `metric_definitions` = **13** |
| 2b node path | `phases/nodes_common.py:2050–2136` | `validation_stack` calls v1 `validate_define(ImproveGraphState)` through `to_v1_state`; **always `goto="gate_review"`, pass or fail** (L2113) |
| v1 validator | `phases/define/validate.py:74–132` | Returns `{"gate_attempts", "escalated", "phase_inputs": {"define": {… "_gate_passed", "_missing_fields"}}}`; **resets `gate_attempts` to 0 on pass** (L104) |
| `validator_feedback` entry | `nodes_common.py:2119–2127` | `{key, layer:"2b", impl, passed, missing, attempts, escalated}` |
| `gate_review` / `gate_apply` | `nodes_common.py:2139`, `:2164` | Pass-throughs; **0 `interrupt()` call sites** |
| Existing verdict types | `validation/schemas.py:40,84,108` | `CoherenceResult`, `CriterionResult{criterion, status: Literal["pass","fail"], feedback}`, `CoachingGraderVerdict{criteria, warning}` — the **coaching** grader's; no `tier`, by design (G-12) |
| State fields | `core/substate.py:604,646,648,655,660,670` | `artifacts: dict[str, Any]`, `belt_edits`, `final`, `gate_attempts: int`, `validator_feedback: list[dict]`, `rejection_feedback: list[dict]` |
| `check_gate_status` | — | **Absent**; not bound (G-108); `knowledge/tools.py:657` records it as owed at 7.1 |
| Cap setting | `core/config.py:105` | `settings.GATE_MAX_ATTEMPTS` (default 3) |
| Grader LLM | `core/llm.py:81,191` | `get_llm("grader")`, temperature 0.1 |

## 3. Gaps between design and code

| # | Gap | Consequence |
|---|---|---|
| a | **12 vs 13.** ARCH §35 / S-C26 say Define checks 12; code checks 13 (`metric_definitions`, §63.8) | S-C26 text is stale against `schema.py:71`; the validator must read `GATE_SPECS`, never a count |
| b | `validation_stack` never routes to `planner` or escalation (`nodes_common.py:2113`) | S-F05's DP2 exits are unbuilt; a failed 2b still reaches `gate_review` |
| c | `gate_attempts` reset on pass in `validate.py:104` | Contradicts §33.2 "reset **only** in `gate_apply`" |
| d | Increment point: v1 increments on failure; S-F13 DP2 says once, at entry | Needs one rule in code |
| e | v1 validator reads `phase_inputs["define"]` (v1 state), not `PhaseState.artifacts` | WATCH 7 seam; the class should read `artifacts` directly |
| f | `CriterionVerdict`, `GraderVerdict` (G-11), `ConstraintVerdict`/`ConstraintCheckResult` (G-10) unbuilt | 2c/2d have no return shape |
| g | `check_gate_status()` zero-arg vs needs phase + artifacts (G-31) | The executor agent's own state is messages only (`nodes_common.py:1637` invokes with `{"messages": prior}`) |
| h | S-F21 `-> dict` untyped | UI progress bars (§50) have nothing to bind to |

## 4. Proposed method list — `backend/validation/gate_validator.py` (DRAFT)

`class DMAICGateValidator:` — `@staticmethod` only, no attributes (S-C26 B5, §54). It **wraps**
`gate_registry`, it does not re-implement it (keeps step 6.3's one computation).

| # | Method | Exact signature (proposed) | Returns | Layer / caller |
|---|---|---|---|---|
| 1 | `tier_1_fields` | `(phase: str) -> tuple[str, ...]` | `GATE_SPECS[phase].tier_1` | helper; tests |
| 2 | `check_presence` | `(phase: str, artifacts: Mapping[str, Any]) -> FieldPresenceResult` | new model | **Layer 2b** — `validation_stack` |
| 3 | `gate_status` | `(phase: str, artifacts: Mapping[str, Any]) -> GateStatus` | new model, **contains** #2's result | **G-31** tool, `BeforeModelStateInjection`, UI |
| 4 | `deterministic_verdicts` | `(phase: str, artifacts: Mapping[str, Any], prior_documents: Mapping[str, Mapping[str, Any]]) -> list[CriterionVerdict]` | S-C20 list | **Layer 2d, code half** (S-F26 B2/B3/B4/B7) — see Q1 |

`Mapping[str, Any]` matches `split_by_declared_type`'s input (`gate_registry.py:127–129`);
`artifacts` is `dict[str, Any]` on `PhaseState` (`substate.py:604`). `prior_documents` has the shape
`_prior_gate_documents` already produces for the middleware (`nodes_common.py:1049`).

Layers 2c and 2d-LLM call a model, so they are **not** static "deterministic checks"; they are module
functions in their S-F files:

| # | Function | File | Exact signature (proposed) | Returns |
|---|---|---|---|---|
| 5 | `check_constraints` | `validation/constraints.py` (S-F25) | `async def check_constraints(phase: str, artifacts: Mapping[str, Any], constraints: str) -> ConstraintCheckResult` | new (G-10) |
| 6 | `grade_gate_document` | `validation/gate_grader.py` (new; **not** `middleware/grader.py`, §36) | `async def grade_gate_document(phase: str, document: Mapping[str, Any], rubric: str, belt_level: Literal["Green Belt", "Black Belt"] \| None, deterministic: list[CriterionVerdict]) -> GraderVerdict` | S-C21 (G-11) |

`grade_gate_document` makes the builder-style structured-output call S-C21 specifies (the same
form `middleware/coherence.py:218` uses, permitted for plain LLM calls by `deprecated_patterns.yaml`'s
note) at `get_llm("grader")`, and merges `deterministic` verdicts so the model is never asked a lookup
question (S-F26 B2/B3). No retrieval (B6).

## 5. Return shapes (DRAFT) — all in `backend/validation/schemas.py`

| Model | Status | Fields (Pydantic v2) |
|---|---|---|
| `FieldPresenceResult` | **new** (G-23) | `phase: str` · `required: tuple[str, ...]` · `missing: list[str]` (**exactly** `missing_gate_fields(phase, artifacts)`, order kept) · `@property passed -> bool` (= `not missing`; derived, never stored — mirrors `CoachingGraderVerdict.passed`, `schemas.py:137`) |
| `GateStatus` | **new** (G-31) | `phase: str` · `presence: FieldPresenceResult` (the 2b object itself → B4 by construction) · `tier_1_total: int` · `tier_1_present: int` · `tier_2_total: int` · `tier_2_missing: list[str]` (reported, never blocking; Define always `0` / `[]`) · `position: dict[str, Any] \| None` (Define: `define_progress()`, `schema.py:113`) |
| `CriterionVerdict` | specified S-C20, **unbuilt** | `criterion: str` · `tier: int` (1 \| 2) · `status: Literal["pass","warning","fail"]` · `feedback: str` + a `model_validator` refusing `tier == 2 and status == "fail"` (S-C20 B1) |
| `GraderVerdict` | named S-C21, **undefined (G-11)** | proposed: `phase: str` · `verdicts: list[CriterionVerdict]` · `max_iterations_reached: bool = False` (§36) · derived properties `failed`, `warnings`, `passed`. **No** `acknowledged_gaps` (Q3) |
| `ConstraintVerdict` | named, **undefined (G-10)** | proposed: `constraint: str` · `status: Literal["pass","fail"]` · `feedback: str` |
| `ConstraintCheckResult` | named, **undefined (G-10)** | proposed: `verdicts: list[ConstraintVerdict]` · property `passed`. Two types — envelope + item, mirroring `GraderVerdict` / `CriterionVerdict` |
| `ValidatorFeedbackEntry` | **new** `TypedDict` (state stays `list[dict]`) | `key: str` · `layer: Literal["2b","2c","2d"]` · `attempt: int` · `passed: bool` · `missing: list[str]` · `verdicts: list[dict]` (`model_dump()` of the layer's items) · `escalated: bool`. A superset of today's entry (`nodes_common.py:2119`); `impl` kept while the v1 seam lives |

## 6. How it is called from the graph

```
planner ──(entry == "gate")──▶ validation_stack ──pass──▶ gate_review ──interrupt()──▶ [Belt]
   ▲                               │ fail, attempt < 3                     │ Command(resume={...})
   └──────── validator_feedback ◀──┘                                       ▼
                    attempt ≥ 3 ──▶ escalation (Command.PARENT, G-34)     gate_apply ─approve─▶ END
                                                                          └─reject(reason)─▶ planner
```

| Order | Node | Call | vs. interrupt |
|---|---|---|---|
| 0 | `validation_stack` | `attempt = state["gate_attempts"] + 1` (DP2: once, at entry) | before |
| 1 | `validation_stack` | `DMAICGateValidator.check_presence(phase, state["artifacts"])` → stop if `not passed` | before |
| 2 | `validation_stack` | `await check_constraints(phase, artifacts, DEFINE_CONSTRAINTS)` | before |
| 3 | `validation_stack` | `det = DMAICGateValidator.deterministic_verdicts(...)`; `await grade_gate_document(..., deterministic=det)` | before |
| 4 | `validation_stack` | `Command(goto="gate_review" \| "planner" \| PARENT, update={"gate_attempts": attempt, "validator_feedback": [entry], "step_log": [...]})` | before |
| 5 | `gate_review` | `decision = interrupt(payload)`; payload = `review_rows(phase, artifacts)` (`gate_registry.py:178`) + the `GraderVerdict` (envelope is G-18's) | **the interrupt** |
| 6 | `gate_apply` | reads the resume value; policy advisory on `belt_edits` (non-blocking); `build_gate_document`; resets `gate_attempts=0`, `validator_feedback=[]` **here only** | after |
| — | executor turn | `check_gate_status` tool → `DMAICGateValidator.gate_status(phase, artifacts)` | not on the gate path |

**§0.24 — framework primitives, verified offline in `agent-improve/.venv` (langgraph 1.2.11, langchain 1.3.16, langchain-core 1.6.0; no model or network calls):**

| Primitive | Evidence |
|---|---|
| `langgraph.types.interrupt(value) -> Any`; `Command` fields `graph, update, resume, goto, PARENT` | imported; a 2-node graph with `InMemorySaver` paused with `Interrupt(value=…)`, resumed by `Command(resume={"action":"approve"})`, routed to `END` by `Command(goto=…)` |
| **The node re-runs from its start on resume** (docs: *"any code before the `interrupt` runs again"*) | measured: the reviewing node ran **2×**. `gate_review` must do nothing non-idempotent before `interrupt()` — it writes nothing today; keep it so (D6) |
| `langchain.tools.ToolRuntime` + `create_agent(context_schema=…)` + `ainvoke(..., context=…)` | a fake-model agent: a tool whose only parameter is `runtime: ToolRuntime[Ctx]` has an **empty** model-facing schema and read `runtime.context.phase` / `.artifacts` correctly |

Docs: https://docs.langchain.com/oss/python/langgraph/interrupts (fetched 2026-09-25): checkpointer +
`thread_id` required; the resume value is what `interrupt` returns; side effects before it must be
idempotent; approve/reject routes by `Command(goto=…)`.

## 7. What G-31 adds / changes

| G-31 question | Proposal (DRAFT) |
|---|---|
| Return shape | `GateStatus` (§5), returned as `model_dump()` — typed, not a bare `dict`. S-F21's signature line changes from `-> dict` |
| How a zero-arg tool knows phase + `artifacts` | `@tool async def check_gate_status(runtime: ToolRuntime[CoachContext]) -> dict[str, Any]` — **the model sees zero args** (verified). `CoachContext{phase: str, artifacts: Mapping[str, Any]}` passed as `context=` at `agent.ainvoke` (`nodes_common.py:1637`), `context_schema=CoachContext` on `create_agent` (`:957`) |
| `args_schema` (§31) | Met: `ToolRuntime` is excluded, the schema is an empty object; nothing hand-built |
| Same derivation as 2b (S-F21 B2 / S-C26 B4) | Structural: `GateStatus.presence` **is** `check_presence`'s result. Test: for fixture `artifacts`, `gate_status(p,a).presence == check_presence(p,a)` and `.missing == missing_gate_fields(p,a)`; a mutation of one path goes red. **Discharges** the 7.1 forward-note rather than withdrawing it |
| `BeforeModelStateInjection` | Switch `state_injection.py:226` to `DMAICGateValidator.gate_status(...)` — "7.1 swaps the caller and not the answer" (`state_injection.py:46–52`) |
| Freshness | `artifacts` in context is the turn's opening snapshot; a field captured this turn is not in it until the node returns. Rejected alternative: a per-turn closure (`model_copy`, as `_budgeted_rag_tools` does) — same staleness, more code |
| Binding | +1 tool in every phase (G-108): Define 7 → 8, within §30's cap |

## 8. Open questions for the founder (DRAFT recommendations)

| # | Question | Options | Recommendation |
|---|---|---|---|
| **Q1** | Does `DMAICGateValidator` own only 2b (+ status), or also 2d's deterministic half? | A: 2b + `gate_status` only; lookups in `gate_grader.py`. B: add `deterministic_verdicts` (#4) to the class | **B** — S-C26 calls it "a namespace of `@staticmethod` deterministic checks"; S-F26's lookups are deterministic and stateless — what §54's one class exception is for. `gate_grader.py` stays the one model call |
| **Q2** | Is `check_gate_status()` the validator, a caller of it, or a second answer? (the 7.1 blocker text) | A: the tool **calls** `gate_status`, which **contains** the 2b result. B: tool and 2b each call `missing_gate_fields` (today). C: tool reads a stored status | **A** — one computation, typed, agreement testable by equality. C is forbidden by S-F21 B1 |
| **Q3** | Where do `acknowledged_gaps` and the overall decision live? (couples G-08 / G-11) | A: `GraderVerdict` carries `acknowledged_gaps`. B: `gate_apply` derives them from `GraderVerdict.warnings` + the Belt's resume choice | **B** — proceeding past a gap is a Belt decision made after the interrupt; the grader cannot know it. Define: always `[]` (DEF-045) |
| Q4 *(minor)* | `gate_attempts` increment / reset | DP2 (at entry) + §33.2 (reset only in `gate_apply`); drop `validate.py:104`'s reset | Adopt both; v1 `validate_{phase}` becomes a thin wrapper over `check_presence` until 11.1 |

## 9. Not decided here

G-18 interrupt/resume envelopes · G-34 escalation target · G-13 `PolicyAdvisoryResult` · G-40 rubric
and `DEFINE_CONSTRAINTS` **text** (see `G40_define_rubric_DRAFT.md`) · D1/D6 contradiction stop.
