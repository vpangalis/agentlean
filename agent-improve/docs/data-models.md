# Agent Improve — data models

*Generated from the code by `tools/architecture/generate_models.py`, on every commit, by the pre-commit
hook. ARCHITECTURE.md §4.2 links here. Never edited by hand: commit-guard rule 16 refuses a copy that
differs from a fresh generation. Founder ruling 6, 2026-09-29: moved out of ARCHITECTURE.md.*

<!-- BEGIN GENERATED: data models — rewritten from the code on every commit; never edit by hand. -->

### 4.2 Declarations

**State schema version 3** (`core/state.py::STATE_SCHEMA_VERSION`, ADR-0065): written into every checkpoint's metadata, every Store record and every case blob; an older one is migrated on load by `core/migrations.py`, a newer one is refused.

#### `SupervisorState` — `core/state.py`

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

#### `PhaseState` — `core/substate.py`

```python
class PhaseState(TypedDict):
    case_id:            str
    current_phase:      str
    messages:           Annotated[list[BaseMessage], operator.add]
    history:            Annotated[list[str], operator.add]
    phase_context:      str
    coaching_plan:      Optional[CoachingPlan]
    field_index:        int
    draft:              dict[str, Any]
    artifacts:          dict[str, Any]
    step_log:           Annotated[list[dict[str, Any]], operator.add]
    field_log:          Annotated[list[dict[str, Any]], merge_field_log]
    field_status:       dict[str, dict[str, Any]]
    belt_edits:         dict[str, Any]
    turn_count:         int
    final:              dict[str, Any]
    gate_attempts:      int
    validator_feedback: list[dict]
    rejection_feedback: list[dict]
    citations:          list[dict]
    uploads:            list[dict]
    asks:               list[dict]
    hop_results:        list[str]
    synthesis_output:   Optional[dict]
    remaining_steps:    NotRequired[RemainingSteps]
```

#### Planner and coach schemas — `core/substate.py`

```python
class SufficiencyJudgment(BaseModel):
    verdict:          Literal['sufficient', 'insufficient', 'not_an_answer']
    reason:           str
    failed_criterion: Optional[str] = None

class CoachingPlan(BaseModel):
    focus_field:        Optional[str]
    status:             Literal['not taught', 'asked', 'answered', 'confirmed', 'parked']
    move:               Literal['teach', 'challenge', 'read_back', 'store_and_advance', 'respond', 'offer_park']
    judgment:           Optional[SufficiencyJudgment] = None
    answer:             str = ''
    messages:           int = 0
    pending:            Optional[dict] = None
    store:              dict[str, Any] = {}
    stored_field:       Optional[str] = None
    statuses:           dict[str, str] = {}
    field_status:       dict[str, dict[str, Any]] = {}
    reason:             str = ''
    retrieval_strategy: Literal['single_hop', 'multi_hop'] = 'single_hop'
    retrieval_hops:     list[str] = []

class CoachingResponse(BaseModel):
    message:            str
    explanation:        str = ''
    example:            str = ''
    prompt:             str = ''
    progress:           str = ''
    fields_captured:    list[dict] = []
    citations:          list[dict] = []
    contradiction_flag: Optional[dict] = None
```

#### Phase records — `phases/{phase}/schema.py`

```python
class DefineOutput(BaseModel):
    business_case:       str
    team:                list[dict]
    voc_summary:         str
    problem_statement:   str
    baseline_estimate:   MetricValue
    project_scope:       dict
    goal_statement:      str
    target_value:        MetricValue
    target_date:         str
    benefits_analysis:   dict
    secondary_metrics:   str
    process_map_sipoc:   dict
    issues_and_barriers: str
    critical_to_quality: list[dict]
    problem_5w2h:        dict
    metric_definitions:  list[dict]
    phase_metrics:       list[dict] = []
    computation_results: list[dict] = []
    acknowledged_gaps:   list[str] = []
    citations:           list[dict] = []
    uploads:             list[dict] = []

class MeasureOutput(BaseModel):
    baseline_mean:                str
    data_collection_plan:         str
    driver_priority_summary:      str
    vital_few_drivers:            str
    detailed_process_map:         dict
    stability_assessment:         str
    issues_and_barriers:          str
    baseline_sigma:               str = ''
    measurement_system_validated: str = ''
    secondary_metrics:            str = ''
    phase_metrics:                list[dict] = []
    computation_results:          list[dict] = []
    acknowledged_gaps:            list[str] = []
    citations:                    list[dict] = []
    uploads:                      list[dict] = []

class AnalyseOutput(BaseModel):
    root_cause_statement:          str
    root_cause_validation:         str
    practical_significance:        str
    issues_and_barriers:           str
    causal_hypothesis:             dict = {}
    ruled_out_causes:              str = ''
    statistical_problem_statement: str = ''
    process_owner_buyin:           str = ''
    secondary_metrics:             str = ''
    phase_metrics:                 list[dict] = []
    computation_results:           list[dict] = []
    acknowledged_gaps:             list[str] = []
    citations:                     list[dict] = []
    uploads:                       list[dict] = []

class ImproveOutput(BaseModel):
    selected_solution:             str
    pilot_result:                  str
    experiment_justification:      str
    issues_and_barriers:           str
    solution_linked_to_root_cause: dict = {}
    implementation_plan:           str = ''
    explanatory_power:             str = ''
    process_owner_buyin:           str = ''
    secondary_metrics:             str = ''
    phase_metrics:                 list[dict] = []
    computation_results:           list[dict] = []
    acknowledged_gaps:             list[str] = []
    citations:                     list[dict] = []
    uploads:                       list[dict] = []

class ControlOutput(BaseModel):
    control_plan:              dict
    post_improvement_metrics:  dict
    issues_and_barriers:       str
    improvement_delta:         str = ''
    financial_impact_verified: str = ''
    sustainability_check:      str = ''
    handover_documented:       str = ''
    lessons_learned:           str = ''
    transferability:           str = ''
    project_signoff:           str = ''
    secondary_metrics:         str = ''
    actual_close_date:         str = ''
    phase_metrics:             list[dict] = []
    computation_results:       list[dict] = []
    acknowledged_gaps:         list[str] = []
    citations:                 list[dict] = []
    uploads:                   list[dict] = []
```

#### Search indexes — Azure AI Search

**`improve_knowledge_index_v3`** — the default of `settings.AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX`; fields owned by `knowledge/retriever.py::KNOWLEDGE_INDEX_FIELDS`

| Field | Type | Attributes |
|---|---|---|
| `id` | `Edm.String` | key, filterable |
| `content` | `Edm.String` | searchable |
| `content_vector` | `Collection(Edm.Single)` | vector, 3072 dimensions, profile `default` |
| `metadata` | `Edm.String` | searchable |
| `source_file` | `Edm.String` | filterable |
| `phase_relevance` | `Edm.String` | filterable |
| `page_number` | `Edm.Int32` | filterable |

**`improve_evidence_index`** — the default of `settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX`; fields owned by `storage/layout.py::EVIDENCE_INDEX`

| Field | Type | Attributes |
|---|---|---|
| `id` | `Edm.String` | key, filterable |
| `content` | `Edm.String` | searchable |
| `content_vector` | `Collection(Edm.Single)` | vector, 3072 dimensions, profile `default` |
| `metadata` | `Edm.String` | searchable |
| `case_id` | `Edm.String` | filterable |
| `phase` | `Edm.String` | filterable |
| `uploaded_at` | `Edm.String` | filterable, sortable |
| `role` | `Edm.String` | searchable, filterable |
| `kind` | `Edm.String` | filterable |
| `description` | `Edm.String` | searchable |
| `content_digest` | `Edm.String` | filterable |
| `shape_match` | `Edm.String` | filterable |

**`improve_case_index`** — the default of `settings.AZURE_SEARCH_IMPROVE_CASE_INDEX`; fields owned by `storage/layout.py::CASE_INDEX`

| Field | Type | Attributes |
|---|---|---|
| `id` | `Edm.String` | key, filterable |
| `case_id` | `Edm.String` | filterable, sortable |
| `title` | `Edm.String` | searchable |
| `belt_level` | `Edm.String` | filterable, facetable |
| `leader` | `Edm.String` | filterable |
| `department` | `Edm.String` | searchable, filterable |
| `current_phase` | `Edm.String` | filterable, facetable |
| `rag_status` | `Edm.String` | filterable, facetable |
| `status` | `Edm.String` | filterable, facetable |
| `created_at` | `Edm.String` | filterable, sortable |
| `target_date` | `Edm.String` | filterable, sortable |
| `days_in_phase` | `Edm.Int32` | filterable, sortable |
| `phase_summary_define` | `Edm.String` | searchable |
| `phase_summary_measure` | `Edm.String` | searchable |
| `phase_summary_analyse` | `Edm.String` | searchable |
| `phase_summary_improve` | `Edm.String` | searchable |
| `phase_summary_control` | `Edm.String` | searchable |
| `content_text` | `Edm.String` | searchable |
| `embedding` | `Collection(Edm.Single)` | vector, 3072 dimensions, profile `improve-vector-profile` |

#### Store namespaces — `storage/layout.py::STORE_NAMESPACES`

| Namespace | Key | Holds |
|---|---|---|
| `(projects, {case_id}, case)` | `record` | The case framing and session copy of the case |
| `(projects, {case_id}, artifacts)` | `define … control` | Each phase's approved gate document |
| `(projects, {case_id}, step_log)` | `timestamped` | Append-only cross-phase audit trail |

#### Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS`

| Path | Owner | Holds |
|---|---|---|
| `cases/case_{case_id}.json` | `storage/blob.py` | The case record — the system of record |
| `registry.json` | `storage/blob.py` | The case registry |
| `uploads/{case_id}/{filename}` | `storage/blob.py` | An uploaded file's bytes |
| `checkpoints/{thread_id}/latest.json` | `core/checkpointer.py` | The parent graph's newest checkpoint |
| `checkpoints/{thread_id}/history/{checkpoint_id}.json` | `core/checkpointer.py` | Every parent checkpoint |
| `checkpoints/{thread_id}/writes/{checkpoint_id}/{task_id}.json` | `core/checkpointer.py` | A checkpoint's pending writes, one blob per task |
| `checkpoints/{thread_id}/ns/{checkpoint_ns}/…` | `core/checkpointer.py` | The same three for a subgraph namespace (percent-encoded) |
| `store/{namespace}/{key}.json` | `core/store.py` | One Store item |

<!-- END GENERATED: data models -->
