# Calibrated Spec-Entry Samples (APPROVED — verbatim standard)

These two entries are the approved reference standard for the specification
layer. Every spec entry is built to match one of these. Transcribe them
VERBATIM into the §57 preamble as the reference examples — do not paraphrase.

- `SupervisorState` = the **class** template.
- `phase_executor` = the **function/node** template (all three layers: SIPOC,
  EARS table, AI-ACT flag, feeding a DORA row).

---

## SAMPLE 1 — CLASS TEMPLATE — `SupervisorState`

## SPEC — `SupervisorState`

**Canonical definition. File: `core/state.py`. Referenced by architecture §5 (rationale), procedure step [tbd].**
*Rebuild test: `core/state.py`'s `SupervisorState` must be reconstructable from this entry alone.*

**Purpose:** The orchestration-level (Level 1) graph state. Carries only what the supervisor needs to route between phases and assemble the final result. It deliberately holds no captured fields, no gate documents, and no phase-internal working data — those live in `PhaseState` (§6) and the Store (§9). It is a `TypedDict`, not a Pydantic model, because it is consumed by `create_agent`-based nodes, which do not support Pydantic state.

**Definition:**
```python
class SupervisorState(TypedDict):
    messages:      Annotated[list[BaseMessage], operator.add]
    history:       Annotated[list[str], operator.add]
    case_id:       str
    phase_index:   int
    current_phase: str
    gate_passed:   dict[str, bool]
    final_output:  Optional[dict]
```
**Exactly seven fields. Adding an eighth requires a §56 amendment.**

**Fields:**

| Field | Type | Meaning | Reducer | Writer | Readers |
|---|---|---|---|---|---|
| `messages` | `Annotated[list[BaseMessage], operator.add]` | The Belt↔system conversation at the orchestration level. Append-only. | `operator.add` (appended, never replaced) | each Belt turn; subgraph return | input mappers (§9), seeding `PhaseState.messages` |
| `history` | `Annotated[list[str], operator.add]` | Human-readable trace breadcrumbs, one appended per node entry. Diagnostic only — no control logic reads it. | `operator.add` | every node, on entry | trace reconstruction / debugging only |
| `case_id` | `str` | Stable project identifier. Also serves as the LangGraph `thread_id` and the first Store namespace segment. Set once, never mutated. | none (last-write-wins, but only written once) | session start | everything; identity across checkpointer + Store |
| `phase_index` | `int` | Zero-based index of the current phase in the fixed DMAIC order `[define, measure, analyse, improve, control]`. Derived from `gate_passed`; stored for readability. | none | **output mapper only** | UI progress display, readability |
| `current_phase` | `str` | Name of the phase currently executing; one of the five DMAIC phase names. Derived from `phase_index`; stored for readability. | none | **output mapper only** | routing, state injection (§9), index writes |
| `gate_passed` | `dict[str, bool]` | Maps each phase name to whether its gate has been approved. Absence of a key means "not yet reached." The authoritative signal the supervisor routes on. | none (whole-dict replace by the single writer) | **output mapper only**; re-approval cascade sets a phase `False` (§37) | supervisor advancement logic |
| `final_output` | `Optional[dict]` | The assembled final deliverable, written only when Control's gate passes. `None` until then. | none | Control's output mapper, at the final gate | API response at project completion |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | a node begins execution | append one human-readable entry to `history` | §14 |
| B2 | the output mapper runs at gate approval | write `phase_index`, `current_phase`, and `gate_passed` together in a single update; no other node SHALL write any of these three | §9 |
| B3 | a reader queries `gate_passed` for a phase name not present as a key | treat the result as "gate not passed" (absent key ≡ `False`), never as an error | §37 |
| B4 | Control's gate is approved | populate `final_output`; UNTIL that point `final_output` SHALL remain `None` | §9 |
| B5 | the re-approval cascade fires for a phase | set that phase's `gate_passed` entry to `False` rather than deleting the key | §37 |

**Invariants:**
- `phase_index` and `current_phase` are derived from `gate_passed` and MUST have exactly one writer (the output mapper). A second writer is prohibited — it converts a derived field into a competing source of truth.
- Captured fields, gate documents, and phase-internal working data MUST NOT appear on this schema (they belong to `PhaseState`/§6 and the Store/§9).
- Any proposed new field MUST name its writing node and its reading node; if either is unclear, the field is rejected (the `project_context` failure — a field with no writer whose only reader ran before it would have been written).

**Failure modes:**
- A `KeyError` on `gate_passed[phase]` is a **contract violation in the reader**, not an expected path — readers MUST use absence-tolerant access (`.get(phase, False)`), per B3.
- Reading `final_output` before Control's gate returns `None`; callers MUST handle `None` as "project not yet complete," not as an error.

---

## SAMPLE 2 — FUNCTION/NODE TEMPLATE — `phase_executor` (the coach node)

## SPEC — `phase_executor` (the coach node)

**Canonical definition. File: `phases/{phase}/nodes.py` (one per phase). References: architecture §14 (node contract), §17 (planner/executor split), §18. Procedure step [tbd].**
*Rebuild test: the phase executor node must be reconstructable from this entry alone.*

**Purpose:** The Level 2 coaching node. Runs one coaching turn: takes the planner's strategy (`CoachingPlan`), coaches the Belt on the chosen field via an LLM with the phase's bound tools, and returns a structured `CoachingResponse` (the Belt-facing message plus captured field values). It decides *nothing* about strategy — that is the planner's job; it executes the plan.

### SIPOC — at a glance

| | |
|---|---|
| **Supplier** (who triggers it) | `phase_planner` (§17) — control returns to the planner after each executor turn, and the planner routes back here via `Command(goto="executor")` when more coaching on the current/next field is needed |
| **Input** (what it reads) | `PhaseState.coaching_plan` (the strategy for this turn), `PhaseState.messages` (conversation), `PhaseState.artifacts` (fields captured so far), `PhaseState.phase_context` (prior-phase committed values, loaded by `before_agent`); the phase's bound tool subset (§30) via `tools=` |
| **Process** (what it does) | Runs `create_agent` with eight middlewares (§19); coaches on `coaching_plan.focus_field`; may call leaf tools in its tool loop; produces a structured `CoachingResponse`; the skill prompt directs it to flag cross-phase contradictions (§37) |
| **Output** (what it produces) | Returns a dict slice: `{"draft": {...}, "artifacts": {...merged...}, "step_log": [{...}], "messages": [...]}` — plus, in `CoachingResponse`, `contradiction_flag` (read by `ContradictionDetectionMiddleware`, §19.6) |
| **Customer** (who consumes it) | `ContradictionDetectionMiddleware` (reads `contradiction_flag`, may raise interrupt); then control returns to `phase_planner`, which decides next field / trigger gate / retry |

### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | invoked | coach only on `coaching_plan.focus_field`; never select a different field (field selection is the planner's responsibility) | §17 |
| B2 | producing its response | return a structured `CoachingResponse` via `response_format`, never free prose parsed downstream | §14 |
| B3 | Belt input materially contradicts a prior-phase gate-approved value present in `phase_context` | populate `contradiction_flag` in the response (read by §19.6) | §37 |
| B4 | capturing one or more field values | return them in `artifacts`; never invent values not supplied by the Belt or a tool | §18 |
| B5 | a tool call in the executor loop fails | surface the failure per §27; never fabricate a substitute result | §27 |
| B6 | the executor runs | append a `step_log` entry keyed deterministically `{phase}:{turn}:{step}` | §47 |

### ⚠ AI-ACT — high-risk surface

**This node produces coaching output that could influence a Belt's assessment or project outcome. If Agent Improve is deployed where its output feeds an employment, certification, or competence decision, this is an Annex III (employment) high-risk function (deadline 2 Dec 2027).**

| Obligation | How this node addresses it |
|---|---|
| Art. 13 (transparency) | Output is clearly AI-generated coaching; the Belt is informed they are interacting with an AI coach (UI contract, §50) |
| Art. 14 (human oversight) | The Belt is always in the loop; coaching is advisory, and no field is committed without the Belt's gate approval (§13, gate_review interrupt) |
| Art. 15 (accuracy/robustness) | Anti-hallucination guard (no invented values); four-layer validation (§35) before any gate commit; contradiction detection (§37) |
| Art. 12 (record-keeping) | Every turn logged to `step_log` and LangSmith (§51); deterministic keys ensure a complete, non-duplicated audit trail |

*Feeds DORA register row **R-EXEC-01**.*

### DORA register row (R-EXEC-01)

| Risk ID | Function | Risk Description | AI Act Art. | Likelihood | Impact | Current Mitigation | Residual Risk | Owner | Customer Negotiation |
|---|---|---|---|---|---|---|---|---|---|
| R-EXEC-01 | `phase_executor` (coach) | AI coaching output could influence a Belt's competence/employment assessment without adequate oversight, or could assert an unverified fact | 13, 14, 15, 12 | Med | High | HITL gate approval (§13); anti-hallucination guard; 4-layer validation (§35); full audit log (§51) | Low–Med — residual depends on whether customer uses gate outputs in formal evaluation | [Provider] | *open — depends on deployment context; customer confirms whether coaching feeds formal assessment* |
