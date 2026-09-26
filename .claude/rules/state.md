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

> Never renumber — `deprecated_patterns.yaml` cites these (§0.2). History/rationale: `docs/_archive/rules_rationale_2026-09-25.md`.

## 10. STATE AND STORAGE

### 10.1 — Two state schemas

**The schemas are the classes — `SupervisorState` in `core/state.py`,
`PhaseState` in `core/substate.py`. Read them there; never copy fields or
counts here.** Any new field, on either, in any category, requires an
amendment to `../AGENTIC_ARCHITECTURE_REFERENCE.md` (§56), then to this file
(§18).

**`SupervisorState` — orchestration only:**
- **Artifacts and gate documents are NOT on it** — they live in the store (§10.2).
- **`dmaic_plan`, `key_decisions`, `open_items`, `project_context` are NOT on
  it** — each is derived on demand. **Context is composed at the boundary,
  never carried on parent state.**
- `gate_passed` is `dict[str, bool]` (the cascade, §9.5, sets a phase back to
  `False`); `final_output` is `Optional[dict]`, never `str`.
- **`current_phase` and `phase_index` are written in exactly one place: the
  output mapper at gate approval** (§10.2). Rationale:
  `../AGENTIC_ARCHITECTURE_REFERENCE.md` §5.

**`PhaseState` — per-phase subgraph state. Binding rules:**
- **`case_id` and `current_phase` are COPIED DOWN by the input mapper and are
  READ-ONLY inside the subgraph.** Check: grep every node return dict for
  either key — any hit is a violation.
- **`artifacts` MUST be SEEDED at phase entry from the case record, never
  `{}`** — a constant there is a ceiling, not a default.
- **An empty capture is REPORTED by field name, never silently dropped** —
  `None`, `[]`, `{}` or blank does not enter `artifacts`, is not written to
  the case record, and does not overwrite the prior value.
- **`field_status` is STORED** (§56 v1.77): not taught → asked → answered →
  confirmed; the current field is the first not confirmed. **Only code
  changes a status, at turn end** — never derived from the previous reply's record.
- **`field_log` is WHEN each value changed and what it was before**, keyed
  `{phase}:{turn}:{field}` (§10.3). **Its reducer is `merge_field_log`, NOT
  `operator.add`** — it upserts so a replayed turn is idempotent. `step_log`
  has the same key but an appending reducer. A channel with no reducer
  REPLACES history silently. Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §6.
- **`remaining_steps` is engine-managed; the input mapper MUST NOT populate
  it** — undeclared, the five-hop off-ramp never fires (§3.7).
- **`coaching_plan` is one typed `CoachingPlan` via `with_structured_output`**,
  overwritten each planner turn — never a bare dict or a list. Read
  `coaching_plan.retrieval_hops`, never `coaching_plan["retrieval_hops"]`.
- **`draft`, `belt_edits` and `final` are `dict`, never `str`.**
- **`gate_attempts` is on `PhaseState` and in the checkpoint** — per phase,
  +1 per failed attempt, reset to 0 on pass, escalating at 3 (§1.7, §3.5).
- **Three feedback channels, never merged:** `validator_feedback` (system
  validation, step 2 — attempt, layer, criteria failed, feedback; reset to
  `[]` on pass), `belt_edits` (Belt corrections, step 5), `rejection_feedback`
  (Belt's reasons for rejecting at the gate, read by the planner).
- **`hop_results` and `synthesis_output` MUST be state, not node locals**
  (`[]` / `None` on single-hop turns).
- **`citations` and `uploads` are the evidence trail** — both go into the
  gate document (§9.6).
- `phase_index` (which phase) and `field_index` (which field) are distinct.
  Never reuse `step_index`.
- **Explicit `TypedDict`, not `MessagesState` inheritance.**

### 10.2 — The store — cross-phase artifacts

**Namespace:** `("projects", case_id, <kind>)`; blob prefix
`store/projects/{case_id}/{kind}/{key}.json`. `case_id` equals the graph's
`thread_id` (§10.5).

| Kind | Keys | Contents |
|---|---|---|
| `"case"` | `"record"` | Case framing, written once at session start from `cases/case_{id}.json` — not a second system of record |
| `"artifacts"` | `"define"`, `"measure"`, … | **Each phase's approved gate document**, written by `gate_apply_node` (§9.6) |
| `"step_log"` | timestamped | Append-only cross-phase audit trail |

**The `gate_documents` namespace is retired.**

**Boundary mappers in `phases/{phase}/mappers.py`:** the output mapper writes
artifacts to the store at gate approval and returns **only
orchestration-relevant values**; **every input mapper composes
`phase_context` from the store** and depends only on `BaseStore` — never on
parent state, never on a blob client.

**String-interpolating a previous phase's output into the next phase's
prompt is BANNED** — read a named field from the structured gate document.

**The store is not the case index** — cross-*case* retrieval is
`rag_lookup_case_history` (§7.2).

### 10.3 — `step_log` — dicts, never tuples

Every audit entry is a dict with named keys, e.g.
`{"layer": "constraint", "attempt": 2, "status": "failed", "reason": "..."}`.
Tuples are BANNED. The validation layers (§9.2), each grader iteration
(`on_evaluation`, §8.2) and every fallback attempt (§4.8) write here.

**`artifacts` (WHAT was captured) and `step_log` (HOW) stay separate.**

### 10.4 — Azure Blob — two distinct concerns

| Concern | Path | Written | Owner |
|---|---|---|---|
| Checkpoints | `checkpoints/{case_id}/latest.json` + `history/{id}.json` | After every graph node, by `AzureBlobCheckpointSaver` | `core/checkpointer.py` |
| Case records (system of record) | `cases/case_{id}.json`, `registry.json`, `uploads/{case_id}/{file}` | Case create, gate pass, file upload — **never mid-conversation** | `storage/blob.py` (`ImproveBlobClient`) |

The gate-pass case write and registry update are two writes, both covered by
the node's `error_handler` (§3.6).

### 10.5 — Naming: `case_id` and `artifacts` are the only names

**The project identifier is `case_id`. Everywhere** — state, store,
`thread_id`, blob path, logs, indexes, prose. **`project_id` is retired.**

**A phase's captured fields are `artifacts`. Everywhere** — never
`captured_fields` in prose, never `phase_inputs` in v2 code.

### 10.6 — Every captured field is a string

**All captured fields are `str`**; computation tools parse at the point of
use and ask the Belt to reformat when they cannot. **The gate document shows
the Belt's exact words.**

**The one exception — three cross-phase reference dicts:**
`causal_hypothesis` (Analyse), `solution_linked_to_root_cause` (Improve),
`post_improvement_metrics` (Control), each carrying `references_phase`,
`references_field` and `references_value` so the grader checks the link
deterministically against the store. Values inside are still strings
(`../AGENTIC_ARCHITECTURE_REFERENCE.md` §42).

**Computation tool output goes in `artifacts["computation_results"]`** — a
list of dicts, all values strings; no new `PhaseState` field, no per-phase
typed destinations (`../AGENTIC_ARCHITECTURE_REFERENCE.md` §7).

### 10.7 — `CoachingResponse` in, `{Phase}Output` out

**Two schemas, two moments — never substitute one for the other.**
`CoachingResponse` (`core/substate.py`) is produced **every turn** by the
executor via `response_format=`; `{Phase}Output` (`phases/{phase}/schema.py`,
registered in `phases/gate_registry.py`) is built **once**, at `gate_apply`,
by Pydantic construction with no LLM. Design:
`../AGENTIC_ARCHITECTURE_REFERENCE.md` §40.

- **Adding any field to `CoachingResponse` requires an amendment** (§18).
  `contradiction_flag` rides the same call — no extra LLM call (§9.4, §8.8).
- `fields_captured[].value` is `Any` **deliberately** — it carries the
  cross-phase dicts (§10.6).
- **Every Output field is `str`** except the cross-phase dicts; every schema
  carries the four gate-metadata fields (`computation_results`,
  `acknowledged_gaps`, `citations`, `uploads`).
- **Tier 1 assembly uses `artifacts["field"]`** (a `KeyError` is correct);
  **Tier 2 uses `artifacts.get("field", "")`** (`{}` for dicts). Define has no
  Tier 2 (§0.18).
- **Gate assembly must reference every field in the schema.**
- **Field counts per phase are owned by the schema modules
  (`phases/*/schema.py`)** — never tabulate them here.
- **`issues_and_barriers`, `secondary_metrics` and `phase_metrics` are on all
  five schemas** (§0.20); `phase_metrics` carries `"none this phase"`, not an
  empty list.

### 10.8 — Structured dict fields; FMEA is not tracked

**Three Tier 1 structured dicts:** `process_map_sipoc` (Define),
`detailed_process_map` (Measure), `control_plan` (Control, five sub-plans).
Sub-field keys are owned by `phases/*/schema.py` (e.g. `SIPOC_KEYS`,
`CONTROL_PLAN_KEYS`). **The grader checks every sub-field is populated.**

**One measurement thread across three phases** — Define
`process_map_sipoc["process_metrics"]` (what is measured) → Measure
`detailed_process_map["baseline_metrics"]` (before) → Control
`post_improvement_metrics` (after).

**`stability_assessment` is Tier 1 and comes BEFORE capability**:
stability → special causes if unstable → capability.

**`experiment_justification` is Tier 1 and requires a decision, not an
experiment**: DOE conducted, simplified one-factor experiment, or none needed
because the solution follows from root cause analysis.

**FMEA has no field in any schema, and none may be added.** If a Black Belt
performs one, it lives in `uploads`; no gate blocks on it
(`../AGENTIC_ARCHITECTURE_REFERENCE.md` §41).

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
- Never initialise `artifacts` to `{}` in an input mapper — it is SEEDED from
  the case record, and a constant there is a ceiling, not a default (§10.1)
- Never give `field_log` `operator.add` — the reducer upserts on the
  deterministic key, which is what makes a replayed turn idempotent (§10.1,
  §10.3)
- Never let an empty capture overwrite a stored value, and never drop one
  without naming the field (§10.1)
- Never reintroduce `analyse_phase` as a phase key — the key is
  `analyse`, matching the index field and the other four phases (§7.3)
- Never leave `hop_results` or `synthesis_output` in a node-local variable
  — LangSmith cannot see interpreter locals and a checkpoint restore loses
  them (§10.1)
