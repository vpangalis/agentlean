# Platform — product requirements

> **Founder-owned**, ratified 2026-09-26 (DEFINE REQUIREMENTS v2). Changed only by founder ruling.
> **NOT in the 1 October scope — recorded only.** No Define feature cites these.

R8 Authentication and project-level access: only signed-in Belts; a
   case is visible only to its team; roles Belt, team member, champion.
   Until R8, the Belt approves the gate and is recorded as the actor.

R9 Protection against malicious prompts: Belt input screened before the
   coach, in the R3 validation layer. After the refactor.

## Technical requirements (PROPOSED)

> **PROPOSED — not ratified** (architecture sort, founder 2026-09-26). Drafted from
> [ARCHITECTURE.md](../../ARCHITECTURE.md), which is unchanged. Architecturally significant
> requirements only: each is a measurable quality or constraint. **Proof** names the test in
> `backend/tests/` that proves it today, or `none`. The decisions behind them are in
> [docs/adr](../adr/README.md). Counts are owned by the code cited, never copied here.

### State model

| Id | Requirement | § | Proof |
|---|---|---|---|
| T1 | The supervisor state holds case-level routing only; artifacts and gate documents are never on it (fields owned by `backend/core/state.py`) | §5 | `test_state.py::test_supervisor_state_has_exactly_seven_fields`, `::test_artifacts_and_gate_documents_are_not_on_supervisor_state` |
| T2 | The phase state's declared fields equal its owner's (`backend/core/substate.py`); no typed computation fields | §6 | `test_state.py::test_phase_state_has_exactly_twenty_four_declared_fields`, `::test_no_typed_computation_fields_on_phase_state` |
| T3 | No phase node writes `case_id` or `current_phase` | §5 | `test_phase_subgraphs.py::test_no_node_writes_case_id_or_current_phase` |
| T4 | The input mapper never populates the managed `remaining_steps` | §6, §26 | `test_mappers.py::test_input_mapper_does_not_populate_remaining_steps` |
| T5 | Every value in a computation result is a string | §7 | `test_computation.py::test_every_result_value_is_a_string` |
| T6 | No value is stored before the Belt confirms it | §20 | `test_wiring.py::test_wired_6_61_nothing_is_stored_before_confirmation` |

### Checkpointing and durability

| Id | Requirement | § | Proof |
|---|---|---|---|
| T7 | The checkpointer and store attach to the parent graph only; every subgraph compiles with neither | §8 | `test_supervisor_graph.py::test_every_subgraph_compiles_with_neither` |
| T8 | Every turn writes a checkpoint under `thread_id` = case id; an invoke without `thread_id` fails | §16 | `test_turn_graph.py::test_one_turn_writes_a_checkpoint_under_the_case_id`, `test_checkpointer.py::test_thread_id_required` |
| T9 | A second concurrent write on one case is detected by ETag, retried, then raised — never silently overwritten | §8, §10 | `test_checkpointer.py::test_concurrent_turn_raises_after_retry` |
| T10 | The field log survives the turn boundary through the case record | §6 | `test_capture_accumulates.py::test_the_log_crosses_the_turn_boundary_through_the_case_record` |
| T11 | Exactly one writer per `thread_id` at a time (a Blob lease) | §10, §64 | none |
| T12 | `thread_id` comes from an authenticated session, never from the request body (with R8) | §16 | none |
| T13 | The case blob is never written mid-conversation, only at gate approval | §10, §33.3 | none |

### Pause and resume

| Id | Requirement | § | Proof |
|---|---|---|---|
| T14 | A validated Define report pauses the graph and writes nothing before a decision | §33.3 | `test_gate_acceptance.py::test_a_validated_define_report_pauses_and_nothing_is_written` |
| T15 | A pause survives a process restart; one approval writes exactly once; pending writes round-trip | §33 | `test_gate_acceptance.py::test_the_pause_survives_a_restart_and_an_approval_writes_once`, `::test_pending_writes_round_trip_and_the_special_channels_overwrite` |
| T16 | A decision with nothing pending answers 409; a rejection must name an element and a reason | §49 | `test_gate_acceptance.py::test_there_is_nothing_to_decide_before_a_submission`, `::test_a_rejection_names_an_element_and_a_reason` |
| T17 | The retention sweep never removes a paused thread | §8, §58 | none |

### Idempotent writes

| Id | Requirement | § | Proof |
|---|---|---|---|
| T18 | The field log upserts on its key; `step_log` keys carry no clock reading | §11 | `test_capture_accumulates.py::test_merge_field_log_upserts_on_the_key`, `test_phase_subgraphs.py::test_step_key_carries_no_clock_reading` |
| T19 | A replayed Store put leaves one value; an unwritten key reads as nothing, never an error | §9 | `test_store.py::test_put_is_idempotent_on_replay`, `::test_get_returns_none_for_an_unwritten_key` |
| T20 | Writing a gate twice leaves one document and one stamp | §33.2 | `test_gate_write.py::test_writing_twice_leaves_one_document_and_one_stamp` |
| T21 | A replayed step leaves one `step_log` entry (today the channel appends — see the drift list) | §11 | none |
| T22 | Re-ingesting a document leaves one copy per chunk (ids passed on add) | §23 | none |
| T23 | The gate document is written to both the Store and the phase's final output, or to neither | §33.2 | none |

### Latency budget

| Id | Requirement | § | Proof |
|---|---|---|---|
| T24 | A turn answers before the 45-second wall; the node budget sits below the engine wall | §45 | `test_turn_budget.py::test_a_slow_turn_answers_before_the_wall`, `test_executor_timeout.py::test_the_node_budget_sits_below_the_engine_wall` |
| T25 | No knowledge tool blocks the event loop for more than 100 ms | §24 | `test_turn_budget.py::test_no_knowledge_tool_blocks_the_loop` |
| T26 | At the hop cap (`COACH_HOP_BUDGET`, `backend/phases/nodes_common.py`) the executor answers instead of searching, and the cap is reachable inside the node budget | §26 | `test_hop_cap.py::test_the_cap_is_three`, `::test_the_cap_can_actually_fire_inside_the_node_budget`, `test_executor.py::test_the_sixth_lookup_answers_instead_of_searching` |
| T27 | `recursion_limit` 50 is only the backstop; hitting it still gives the Belt a partial answer | §26 | `test_executor.py::test_recursion_limit_is_the_backstop_not_the_hop_cap`, `::test_hitting_the_backstop_gives_the_belt_a_partial_answer` |
| T28 | Turn latency P50 and P99 are recorded per phase | §51 | none |

### Error handling

| Id | Requirement | § | Proof |
|---|---|---|---|
| T29 | Every node with an external write has an `error_handler` that undoes it and routes to a degraded answer | §45 | none |
| T30 | A search 4xx raises as permanent, a connection failure as transient; only a genuine no-match returns an empty list | §27, §48 | `test_retriever.py::test_a_4xx_raises_with_severity_permanent`, `::test_a_connection_failure_is_transient`, `::test_a_genuine_no_match_returns_an_empty_list` |
| T31 | No computation tool raises on unparseable input | §30 | `test_computation.py::test_no_tool_raises_on_unparseable_input` |
| T32 | A timed-out turn tells the Belt what happened | §45 | `test_executor_timeout.py::test_the_belt_facing_message_says_what_happened` |
| T33 | A client disconnect cancels the run and commits nothing from that turn | §47 | `test_abandon.py::test_a_disconnect_cancels_the_run_and_raises_client_gone` |
| T34 | A model failure falls through levels 1–4; degraded mode names the phase and the captured count and says progress is saved | §46 | none |
| T35 | Two three-state circuit breakers: 3 failures in 30 s open, 60 s reset, one half-open probe | §46 | none |
| T36 | A token-limit 400 is never retried on a smaller model | §46 | none |
| T37 | A deployment rollout ends no coaching session: in-flight turns checkpoint and resume | §45 | none |
| T38 | Retries are exhausted before a node's error handler runs | §44 | none |

### Tracing

| Id | Requirement | § | Proof |
|---|---|---|---|
| T39 | With tracing off, no trace is created | §51 | `test_no_tracing.py::test_a_span_outside_a_run_creates_no_trace` |
| T40 | Every Define turn leaves a LangSmith trace (live) | §51 | `test_capability_rows.py::test_row_35_every_define_turn_leaves_a_langsmith_trace` |
| T41 | A production start without LangSmith configured refuses to run | §51, §53 | none |
| T42 | Validation and extraction steps are traced spans | §51 | none |
| T43 | Every log line carries `request_id`, case id and phase | §51 | none |
| T44 | Every grader verdict and every rejection reason reaches `step_log` | §11, §34 | `test_judges_once.py::test_the_graders_verdict_reaches_step_log`, `test_coherence_script_step.py::test_every_rejection_records_its_reason_in_step_log` |

### Model roles and cost

| Id | Requirement | § | Proof |
|---|---|---|---|
| T45 | Roles, tiers and temperatures are those of `backend/core/llm.py`: two tiers; graders and deterministic roles at 0.1; coach in its band; client retry off | §21 | `test_llm.py::test_exactly_eleven_roles`, `::test_two_tiers_only`, `::test_grader_temperature_is_point_one`, `::test_deterministic_roles_are_point_one`, `::test_coach_temperature_in_the_ratified_band`, `::test_the_constructor_pins_retry_off_explicitly` |
| T46 | The model, tool and validation retry caps stay separate | §19.4, §19.5 | `test_middleware.py::test_the_three_retry_caps_stay_separate` |
| T47 | At most one judgment call per substantive Belt answer, none otherwise | §17 | `test_validation_layer.py::test_every_belt_answer_is_judged_and_nothing_else_is` |
| T48 | A coaching turn never runs the validator (no gate attempt consumed) | §34 | `test_turn_graph.py::test_a_coaching_turn_never_runs_the_validator` |
| T49 | Summarisation runs with the ratified trigger and keep settings | §19.3 | `test_middleware.py::test_the_ratified_summarization_settings` |
| T50 | A drop of more than 10% in any eval metric blocks release | §52 | none |

### Retrieval and tools

| Id | Requirement | § | Proof |
|---|---|---|---|
| T51 | RRF fuses with constant 60 over 3–5 query variants plus the original | §25 | `test_fusion.py::test_the_constant_is_60`, `::test_the_variant_count_is_bounded_at_three_to_five` |
| T52 | No phase binds more than 16 tools | §30 | `test_computation.py::test_no_phase_exceeds_the_sixteen_tool_ceiling` |
| T53 | Evidence search is filtered by case, safe against a quote in either argument | §23 | `test_evidence_index.py::test_the_case_filter_survives_an_odata_quote_in_either_argument` |
| T54 | Each metric has one computing authority; a mismatched scalar is a defect | §69 | `test_metric_single_authority.py::test_mismatched_scalar_is_a_defect` |
| T55 | The contradiction check runs before the agent and interrupts only on a flag | §19.6 | `test_middleware.py::test_the_hook_is_before_agent_not_before_model`, `::test_no_flag_means_no_interrupt` |
| T56 | Gate validation makes no retrieval calls | §34 | none |
| T57 | A capability tool refuses until a stability check has passed | §69 | none |
| T58 | Knowledge lookups always include the `general` methodology | §24 | none |
| T59 | An upload's `phase` and `uploaded_at` are set by the server | §65 | none |
| T60 | Evidence series are re-parsed at use and never stored in state | §60 | none |
| T61 | Each skill description stays under 2,000 tokens | §32 | none |

### Gates and validation

| Id | Requirement | § | Proof |
|---|---|---|---|
| T62 | Gate assembly raises on a missing Tier 1 field and references every field of the phase schema | §33, §63 | `test_gate_documents.py::test_missing_tier_1_field_raises_keyerror`, `::test_assembly_references_every_schema_field`, `::test_field_count_matches_spec` |
| T63 | A report failing a rubric criterion is not paused, and the criterion is named | §34 | `test_define_rubric.py::test_a_report_failing_a_criterion_is_not_paused_and_the_criterion_is_named` |
| T64 | The grader stands down once coherence has degraded | §36 | `test_middleware.py::test_the_grader_stands_down_when_coherence_degraded` |
| T65 | The third failed gate attempt escalates | §38 | none |
| T66 | A Tier 2 criterion can never fail a gate | §35 | none |

### Configuration and deployment

| Id | Requirement | § | Proof |
|---|---|---|---|
| T67 | Start-up exits with status 1 when a required credential is missing | §53 | none |
| T68 | A second-region fallback exists before launch (deferred) | §46.1, §68 | none |

### Proposed features for the requirements with no proof

> PROPOSED only — **not** added to `define_features.json`.

| T | Proposed feature — what its test would show |
|---|---|
| T11 | Two writers on one case: the second cannot take the lease and gets a clear retry, never a merged checkpoint |
| T12 | With R8 on, a request naming a case outside the session's team is refused before the graph runs |
| T13 | A whole Define conversation up to the gate leaves the case blob untouched; approval writes it once |
| T17 | The sweep over a paused thread older than the retention window keeps it and its pending writes |
| T21 | A step replayed after a crash leaves one `step_log` entry per key (needs a keyed reducer — a ruling) |
| T22 | Ingesting the same file twice leaves the index document count unchanged |
| T23 | A failure between the two gate writes leaves neither (the error handler undoes the first) |
| T28 | A turn's timing record carries phase and duration; P50 and P99 are computed from them |
| T29 | Each node with an external write is registered with an `error_handler`; a forced write failure is undone |
| T34 | A model outage stubbed at each level: the Belt always gets an answer; the degraded text names phase and count |
| T35 | The breaker opens after 3 failures in 30 s, half-opens at 60 s with one probe, closes on success |
| T36 | A stubbed token-limit 400 is not retried on the smaller model |
| T37 | A drain during a turn: the turn checkpoints and resumes in the next process |
| T38 | A failing write is retried to its cap before the error handler is called |
| T41 | Production settings without LangSmith: start-up refuses |
| T42 | The validation and extraction functions each appear as a span in a recorded trace |
| T43 | Every log line of a turn carries `request_id`, case id and phase |
| T50 | The eval runner fails when a metric falls more than 10% below its baseline |
| T56 | A gate submission with the retriever stubbed to fail passes untouched (no retrieval call) |
| T57 | A capability tool called on an unstable series returns the precondition message, not a Cpk |
| T58 | A knowledge lookup's filter always includes `general` |
| T59 | An upload naming its own `phase` or `uploaded_at` is stored with the server's values |
| T60 | After a computation over evidence, no series is present in the checkpoint |
| T61 | Every SKILL.md description is under 2,000 tokens |
| T65 | Three failed gate attempts route to the escalation subgraph (DEF-046, a stub today) |
| T66 | A Tier 2 criterion stubbed to fail yields a warning, never a failed gate |
| T67 | Start-up with a missing credential exits 1 naming the setting |
| T68 | Deferred until before launch; no feature proposed |
