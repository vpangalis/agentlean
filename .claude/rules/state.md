---
paths:
  - "agent-improve/backend/core/state.py"
  - "agent-improve/backend/core/substate.py"
  - "agent-improve/backend/core/store.py"
  - "agent-improve/backend/storage/**"
  - "agent-improve/backend/phases/mappers_common.py"
  - "agent-improve/backend/phases/*/mappers.py"
---
# §10 — State and storage

> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

## 10. STATE AND STORAGE

### 10.1 — Two state schemas

**`SupervisorState`** — orchestration only:

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

    # the sixteen content fields
    coaching_plan:      Optional[CoachingPlan]  # ONE typed plan per planner turn
    field_index:        int                # field within the phase
    draft:              dict[str, Any]     # this turn's extraction
    artifacts:          dict[str, Any]     # accumulated for the phase
    step_log:           Annotated[list[dict[str, Any]], operator.add]
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

**Twenty-one author-populated fields — two identity, three plumbing, sixteen
content — plus one engine-managed value, twenty-two declared.**

> **Two of those three figures were already stale before `asks` was added, and
> the block above was right the whole time.** This caption read *"Nineteen …
> fourteen content … twenty declared"* while the field list beneath it carried
> fifteen content fields, because **`rejection_feedback` was added at 2.2.23
> (§0.17) and the caption was never updated with it.** §0.17's own table says
> *"20 + 1 managed, 21 declared"*, so this file disagreed with itself four
> hundred lines apart. Corrected here rather than separately: the count was
> being edited anyway, and §0.18's rule is that a figure sync gets said out loud
> rather than slipped in.

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

### 10.2 — The store — cross-phase artifacts

**Namespace convention:**
```
("projects", case_id, <kind>)
```

| Namespace | Keys | Contents |
|---|---|---|
| `("projects", case_id, "case")` | `"record"` | Case framing — title, department, belt level, leader, target date. Written once at session start from `cases/case_{id}.json`, never mid-conversation |
| `("projects", case_id, "artifacts")` | `"define"`, `"measure"`, … | **Each phase's approved gate document** — written by `gate_apply_node` (§9.6) |
| `("projects", case_id, "step_log")` | timestamped | Append-only cross-phase audit trail |

**Blob prefix:** `store/projects/{case_id}/{kind}/{key}.json`

`case_id` is the same value as the graph's `thread_id` (§10.5).

**The `gate_documents` namespace is retired.** A phase's approved
artifacts and its gate document are the same object; two keys holding
the same content is a question about which is authoritative with no
answer. Reintroducing it is a violation.

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

### 10.3 — `step_log` — dicts, never tuples

Every audit entry is a dict with named keys. Tuples are BANNED — field
names make the log self-documenting and queryable.

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

### 10.4 — Azure Blob — two distinct concerns

**Concern 1: Checkpoints (in-flight graph state)**
- Path: `checkpoints/{case_id}/latest.json` + `history/{id}.json`
- Written by `AzureBlobCheckpointSaver` after every graph node
- Owner: `core/checkpointer.py`

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

### 10.5 — Naming: `case_id` and `artifacts` are the only names

**The project identifier is `case_id`. Everywhere.** State field, store
namespace segment, `thread_id`, blob path, log field, index field,
prose. **`project_id` is retired and may not be reintroduced.**

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

### 10.6 — Every captured field is a string

**All captured fields are `str`.** No phase schema declares a typed
numeric. **Computation tools parse at the point of use** — each of the
20 (§5.2) extracts what it needs from the string it is given and returns
a clear reformatting request to the Belt when it cannot.

```python
baseline_mean = "12.3% invoice error rate, measured over Q2 2026"
```

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

### 10.7 — `CoachingResponse` in, `{Phase}Output` out

**Two schemas, two moments. Never substitute one for the other.**

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

### 10.8 — Structured dict fields; FMEA is not tracked

**Three Tier 1 fields are structured dicts**, distinct from the three
cross-phase reference dicts of §10.6:

| Field | Phase | Sub-fields |
|---|---|---|
| `process_map_sipoc` | Define | `suppliers`, `inputs`, `process_steps`, `outputs`, `customers`, `process_metrics` |
| `detailed_process_map` | Measure | `steps`, `cycle_times`, `resources`, `value_vs_waste`, `measurement_points`, `baseline_metrics` |
| `control_plan` | Control | `documentation`, `monitoring`, `response`, `training`, `aligning_systems` |

**The grader checks every sub-field is populated.** A `process_map_sipoc`
with four of six keys filled is the partial-map failure the field exists
to catch — a Belt who maps steps 3–5 of a seven-step process produces a
project that cannot show improvement, because the baseline never covered
the whole thing.

**Three fields carry one measurement thread across three phases**, and
the grader verifies the same measurement points carry different values:

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

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §5, §6, §7, §9, §10, §11, §40.*


## Never

*§14's bans that belong to this file — 29 of 95, each landing in exactly one rule file. Verbatim, with their citations.*

- Never add artifacts or gate documents to `SupervisorState` — seven
  fields, and an eighth needs an amendment (§10.1)
- Never add `dmaic_plan`, `key_decisions`, `open_items` or
  `project_context` to `SupervisorState` — all four were removed as
  redundant (§10.1)
- Never write `project_id` — the identifier is `case_id` everywhere
  (§10.5)
- Never write `captured_fields` in prose or `phase_inputs` in v2 code —
  the name is `artifacts` (§10.5)
- Never reintroduce the `gate_documents` store namespace — the gate
  document lives under `artifacts` (§10.2)
- Never type a captured field as a numeric — all captured fields are
  `str`, and the computation tools parse at the point of use (§10.6)
- Never add typed per-phase destinations for computation results — they
  go in `artifacts["computation_results"]` (§10.6)
- Never hold `gate_attempts` in route scope — it is on `PhaseState` and
  in the checkpoint, or the v1 reset bug returns (§10.1, §1.7)
- Never write `case_id` or `current_phase` from inside a phase subgraph — both
  are copied down by the input mapper at entry and are read-only there; a node
  returning either key is a violation (§10.1)
- Never merge `validator_feedback` and `belt_edits` — system validation
  and Belt corrections are different actors at different moments (§10.1)
- Never merge `issues_and_barriers` and `acknowledged_gaps` — Belt-stated
  blockers and system-recorded skipped fields are different things (§9.7)
- Never type `control_plan`, `process_map_sipoc` or
  `detailed_process_map` as `str` — all three are structured dicts
  (§10.8)
- Never accept a partial process map — the grader checks all six
  sub-fields of `process_map_sipoc` and `detailed_process_map` (§10.8)
- Never assess capability before stability — `stability_assessment` is
  Tier 1 and comes first (§10.8)
- Never add an FMEA field to any schema — it is deliberately not tracked
  (§10.8)
- Never add a field to one phase's Output schema without checking whether
  it belongs on all five (§10.7)
- Never write `current_phase` or `phase_index` outside the output mapper
  — they are derived values kept for readability, and one write site is
  what keeps them honest (§10.1)
- Never store a derived list of missing fields or blockers — derive them
  from `check_gate_status()` and the validation stack at the moment they
  are needed (§9.2, §10.1)
- Never carry phase context on parent state — every input mapper
  composes `phase_context` from the store (§10.2)
- Never hand-roll checkpointing or state persistence — the LangGraph
  checkpointer and store own it (§0.24, §1.7, §10.2). Supplying a BACKEND to
  `BaseCheckpointSaver`, as `AzureBlobCheckpointSaver` does, is using the
  primitive; writing your own alongside it is not
- Never create a per-phase or concatenated `thread_id`
- Never compile a checkpointer or store onto a phase subgraph
- Never use `InMemorySaver`
- Never write to the case blob mid-conversation
- Never write checkpoints to the case blob path
- Never pass cross-phase data through parent state or string interpolation
- Never log to `step_log` as tuples
- Never reintroduce `analyse_phase` as a phase key — the key is
  `analyse`, matching the index field and the other four phases (§7.3)
- Never leave `hop_results` or `synthesis_output` in a node-local variable
  — LangSmith cannot see interpreter locals and a checkpoint restore loses
  them (§10.1)
