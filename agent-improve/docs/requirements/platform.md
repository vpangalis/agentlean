# Platform — technical requirements

R8 moved to business.md; R9 is retired into T71 and T72.

## Technical requirements

> **Status:** T1–T68 ACCEPTED 2026-09-27 (except T41, RETIRED); T69–T70 ACCEPTED;
> T71–T84 PROPOSED — awaiting founder. Each is a measurable quality or constraint, with `MoSCoW` (`?` until the founder
> ratifies it) and `Design` (its ADR, or `none`). **Proof**
> names the test in `backend/tests/` that proves it today, or `none`. The decisions behind
> them are in [docs/adr](../adr/README.md). Counts are owned by the code cited, never copied here.

### State model

| Id | Requirement | § | MoSCoW | Design | Proof |
|---|---|---|---|---|---|
| T1 | The supervisor state holds case-level routing only; artifacts and gate documents are never on it (fields owned by `backend/core/state.py`) | §5 | ? | ADR-0015 | `test_state.py::test_supervisor_state_has_exactly_seven_fields`, `::test_artifacts_and_gate_documents_are_not_on_supervisor_state` |
| T2 | The phase state's declared fields equal its owner's (`backend/core/substate.py`); no typed computation fields | §6 | ? | ADR-0015 | `test_state.py::test_phase_state_has_exactly_twenty_four_declared_fields`, `::test_no_typed_computation_fields_on_phase_state` |
| T3 | No phase node writes `case_id` or `current_phase` | §5 | ? | ADR-0015 | `test_phase_subgraphs.py::test_no_node_writes_case_id_or_current_phase` |
| T4 | The input mapper never populates the managed `remaining_steps` | §6, §26 | ? | ADR-0015 | `test_mappers.py::test_input_mapper_does_not_populate_remaining_steps` |
| T5 | Every value in a computation result is a string | §7 | ? | ADR-0016 | `test_computation.py::test_every_result_value_is_a_string` |
| T6 | No value is stored before the Belt confirms it | §20 | ? | ADR-0002 | `test_wiring.py::test_wired_6_61_nothing_is_stored_before_confirmation` |
### Checkpointing and durability

| Id | Requirement | § | MoSCoW | Design | Proof |
|---|---|---|---|---|---|
| T7 | The checkpointer and store attach to the parent graph only; every subgraph compiles with neither | §8 | ? | ADR-0017 | `test_supervisor_graph.py::test_every_subgraph_compiles_with_neither` |
| T8 | Every turn writes a checkpoint under `thread_id` = case id; an invoke without `thread_id` fails | §16 | ? | ADR-0024 | `test_turn_graph.py::test_one_turn_writes_a_checkpoint_under_the_case_id`, `test_checkpointer.py::test_thread_id_required` |
| T9 | A second concurrent write on one case is detected by ETag, retried, then raised — never silently overwritten | §8, §10 | ? | ADR-0018 | `test_checkpointer.py::test_concurrent_turn_raises_after_retry` |
| T10 | The field log survives the turn boundary through the case record | §6 | ? | ADR-0019 | `test_capture_accumulates.py::test_the_log_crosses_the_turn_boundary_through_the_case_record` |
| T11 | Exactly one writer per `thread_id` at a time (a Blob lease) | §10, §64 | ? | ADR-0018 | none |
| T12 | `thread_id` comes from an authenticated session, never from the request body (with R8) | §16 | ? | ADR-0024 | none |
| T13 | The case blob is never written mid-conversation, only at gate approval | §10, §33.3 | ? | ADR-0038 | none |
### Pause and resume

| Id | Requirement | § | MoSCoW | Design | Proof |
|---|---|---|---|---|---|
| T14 | A validated Define report pauses the graph and writes nothing before a decision | §33.3 | ? | ADR-0037 | `test_gate_acceptance.py::test_a_validated_define_report_pauses_and_nothing_is_written` |
| T15 | A pause survives a process restart; one approval writes exactly once; pending writes round-trip | §33 | ? | ADR-0037 | `test_gate_acceptance.py::test_the_pause_survives_a_restart_and_an_approval_writes_once`, `::test_pending_writes_round_trip_and_the_special_channels_overwrite` |
| T16 | A decision with nothing pending answers 409; a rejection must name an element and a reason | §49 | ? | ADR-0009 | `test_gate_acceptance.py::test_there_is_nothing_to_decide_before_a_submission`, `::test_a_rejection_names_an_element_and_a_reason` |
| T17 | The retention sweep never removes a paused thread | §8, §58 | ? | none | none |
### Idempotent writes

| Id | Requirement | § | MoSCoW | Design | Proof |
|---|---|---|---|---|---|
| T18 | The field log upserts on its key; `step_log` keys carry no clock reading | §11 | ? | ADR-0020 | `test_capture_accumulates.py::test_merge_field_log_upserts_on_the_key`, `test_phase_subgraphs.py::test_step_key_carries_no_clock_reading` |
| T19 | A replayed Store put leaves one value; an unwritten key reads as nothing, never an error | §9 | ? | ADR-0019 | `test_store.py::test_put_is_idempotent_on_replay`, `::test_get_returns_none_for_an_unwritten_key` |
| T20 | Writing a gate twice leaves one document and one stamp | §33.2 | ? | ADR-0011 | `test_gate_write.py::test_writing_twice_leaves_one_document_and_one_stamp` |
| T21 | A replayed step leaves one `step_log` entry (today the channel appends — see the drift list) | §11 | ? | ADR-0020 | none |
| T22 | Re-ingesting a document leaves one copy per chunk (ids passed on add) | §23 | ? | ADR-0030 | none |
| T23 | The gate document is written to both the Store and the phase's final output, or to neither | §33.2 | ? | ADR-0011 | none |
### Latency budget

| Id | Requirement | § | MoSCoW | Design | Proof |
|---|---|---|---|---|---|
| T24 | A turn answers before the 45-second wall; the node budget sits below the engine wall | §45 | ? | ADR-0043 | `test_turn_budget.py::test_a_slow_turn_answers_before_the_wall`, `test_executor_timeout.py::test_the_node_budget_sits_below_the_engine_wall` |
| T25 | No knowledge tool blocks the event loop for more than 100 ms | §24 | ? | none | `test_turn_budget.py::test_no_knowledge_tool_blocks_the_loop` |
| T26 | At the hop cap (`COACH_HOP_BUDGET`, `backend/phases/nodes_common.py`) the executor answers instead of searching, and the cap is reachable inside the node budget | §26 | ? | ADR-0032 | `test_hop_cap.py::test_the_cap_is_three`, `::test_the_cap_can_actually_fire_inside_the_node_budget`, `test_executor.py::test_the_sixth_lookup_answers_instead_of_searching` |
| T27 | `recursion_limit` 50 is only the backstop; hitting it still gives the Belt a partial answer | §26 | ? | ADR-0032 | `test_executor.py::test_recursion_limit_is_the_backstop_not_the_hop_cap`, `::test_hitting_the_backstop_gives_the_belt_a_partial_answer` |
| T28 | Turn latency P50 and P99 are recorded per phase | §51 | ? | none | none |
### Error handling

| Id | Requirement | § | MoSCoW | Design | Proof |
|---|---|---|---|---|---|
| T29 | Every node with an external write has an `error_handler` that undoes it and routes to a degraded answer | §45 | ? | ADR-0043 | none |
| T30 | A search 4xx raises as permanent, a connection failure as transient; only a genuine no-match returns an empty list | §27, §48 | ? | ADR-0033 | `test_retriever.py::test_a_4xx_raises_with_severity_permanent`, `::test_a_connection_failure_is_transient`, `::test_a_genuine_no_match_returns_an_empty_list` |
| T31 | No computation tool raises on unparseable input | §30 | ? | ADR-0035 | `test_computation.py::test_no_tool_raises_on_unparseable_input` |
| T32 | A timed-out turn tells the Belt what happened | §45 | ? | ADR-0047 | `test_executor_timeout.py::test_the_belt_facing_message_says_what_happened` |
| T33 | A client disconnect cancels the run and commits nothing from that turn | §47 | ? | ADR-0046 | `test_abandon.py::test_a_disconnect_cancels_the_run_and_raises_client_gone` |
| T34 | A model failure falls through levels 1–4; degraded mode names the phase and the captured count and says progress is saved | §46 | ? | ADR-0044 | none |
| T35 | Two three-state circuit breakers: 3 failures in 30 s open, 60 s reset, one half-open probe | §46 | ? | ADR-0044 | none |
| T36 | A token-limit 400 is never retried on a smaller model | §46 | ? | ADR-0044 | none |
| T37 | A deployment rollout ends no coaching session: in-flight turns checkpoint and resume | §45 | ? | ADR-0043 | none |
| T38 | Retries are exhausted before a node's error handler runs | §44 | ? | ADR-0043 | none |
### Tracing

| Id | Requirement | § | MoSCoW | Design | Proof |
|---|---|---|---|---|---|
| T39 | With tracing off, no trace is created | §51 | ? | ADR-0048 | `test_no_tracing.py::test_a_span_outside_a_run_creates_no_trace` |
| T40 | Every Define turn leaves a LangSmith trace **in development and test** (live) | §51 | ? | ADR-0048 | `test_capability_rows.py::test_row_35_every_define_turn_leaves_a_langsmith_trace` |
| T41 | ~~A production start without LangSmith configured refuses to run~~ **RETIRED 2026-09-27, replaced by T77** — production sends no traces outside the intranet | §51, §53 | ? | none | none |
| T42 | Validation and extraction steps are traced spans | §51 | ? | ADR-0048 | none |
| T43 | Every log line carries `request_id`, case id and phase | §51 | ? | none | none |
| T44 | Every grader verdict and every rejection reason reaches `step_log` | §11, §34 | ? | ADR-0020 | `test_judges_once.py::test_the_graders_verdict_reaches_step_log`, `test_coherence_script_step.py::test_every_rejection_records_its_reason_in_step_log` |
### Model roles and cost

| Id | Requirement | § | MoSCoW | Design | Proof |
|---|---|---|---|---|---|
| T45 | Roles, tiers and temperatures are those of `backend/core/llm.py`: two tiers; graders and deterministic roles at 0.1; coach in its band; client retry off | §21 | ? | ADR-0029 | `test_llm.py::test_exactly_eleven_roles`, `::test_two_tiers_only`, `::test_grader_temperature_is_point_one`, `::test_deterministic_roles_are_point_one`, `::test_coach_temperature_in_the_ratified_band`, `::test_the_constructor_pins_retry_off_explicitly` |
| T46 | The model, tool and validation retry caps stay separate | §19.4, §19.5 | ? | ADR-0027 | `test_middleware.py::test_the_three_retry_caps_stay_separate` |
| T47 | At most one judgment call per substantive Belt answer, none otherwise | §17 | ? | ADR-0007 | `test_validation_layer.py::test_every_belt_answer_is_judged_and_nothing_else_is` |
| T48 | A coaching turn never runs the validator (no gate attempt consumed) | §34 | ? | ADR-0039 | `test_turn_graph.py::test_a_coaching_turn_never_runs_the_validator` |
| T49 | Summarisation runs with the ratified trigger and keep settings | §19.3 | ? | ADR-0027 | `test_middleware.py::test_the_ratified_summarization_settings` |
| T50 | A drop of more than 10% in any eval metric blocks release | §52 | ? | ADR-0049 | none |
### Retrieval and tools

| Id | Requirement | § | MoSCoW | Design | Proof |
|---|---|---|---|---|---|
| T51 | RRF fuses with constant 60 over 3–5 query variants plus the original | §25 | ? | ADR-0031 | `test_fusion.py::test_the_constant_is_60`, `::test_the_variant_count_is_bounded_at_three_to_five` |
| T52 | No phase binds more than 16 tools | §30 | ? | ADR-0035 | `test_computation.py::test_no_phase_exceeds_the_sixteen_tool_ceiling` |
| T53 | Evidence search is filtered by case, safe against a quote in either argument | §23 | ? | ADR-0030 | `test_evidence_index.py::test_the_case_filter_survives_an_odata_quote_in_either_argument` |
| T54 | Each metric has one computing authority; a mismatched scalar is a defect | §69 | ? | ADR-0035 | `test_metric_single_authority.py::test_mismatched_scalar_is_a_defect` |
| T55 | The contradiction check runs after the agent (on the reply's flag) and stops the turn only on a flag | §19.6 | ? | ADR-0042 | `test_middleware_execution_order.py::test_after_agent_executes_contradiction_then_coherence_then_grader`, `test_middleware.py::test_no_flag_means_no_interrupt` |
| T56 | Gate validation makes no retrieval calls | §34 | ? | ADR-0039 | none |
| T57 | A capability tool refuses until a stability check has passed | §69 | ? | ADR-0035 | none |
| T58 | Knowledge lookups always include the `general` methodology | §24 | ? | ADR-0030 | none |
| T59 | An upload's `phase` and `uploaded_at` are set by the server | §65 | ? | none | none |
| T60 | Evidence series are re-parsed at use and never stored in state | §60 | ? | none | none |
| T61 | Each skill description stays under 2,000 tokens | §32 | ? | ADR-0036 | none |
### Gates and validation

| Id | Requirement | § | MoSCoW | Design | Proof |
|---|---|---|---|---|---|
| T62 | Gate assembly raises on a missing Tier 1 field and references every field of the phase schema | §33, §63 | ? | ADR-0040 | `test_gate_documents.py::test_missing_tier_1_field_raises_keyerror`, `::test_assembly_references_every_schema_field`, `::test_field_count_matches_spec` |
| T63 | A report failing a rubric criterion is not paused, and the criterion is named | §34 | ? | ADR-0010 | `test_define_rubric.py::test_a_report_failing_a_criterion_is_not_paused_and_the_criterion_is_named` |
| T64 | The grader stands down once coherence has degraded | §36 | ? | ADR-0041 | `test_middleware.py::test_the_grader_stands_down_when_coherence_degraded` |
| T65 | The third failed gate attempt escalates | §38 | ? | ADR-0039 | none |
| T66 | A Tier 2 criterion can never fail a gate | §35 | ? | ADR-0040 | none |
### Configuration and deployment

| Id | Requirement | § | MoSCoW | Design | Proof |
|---|---|---|---|---|---|
| T67 | Start-up exits with status 1 when a required credential is missing | §53 | ? | ADR-0050 | none |
| T68 | A second-region fallback exists before launch (deferred) | §46.1, §68 | ? | ADR-0045 | none |
### Added 2026-09-27

| Id | Requirement | MoSCoW | Design | Proof |
|---|---|---|---|---|
| T69 | An ordinary coaching turn makes at most 4 model calls, retries included; the count is recorded per turn in `step_log` | ? | none | none |
| T70 | Node time limits, retries and compensation use LangGraph's per-node `timeout=`, `retry_policy=` and `error_handler=`; no hand-written budget or retry loop | ? | ADR-0043 | none |
| T71 | The Belt's message is screened before any model reads it — fixed rules, then Azure Prompt Shields — in a node at the front of the parent graph; a blocked turn answers with guidance, stores nothing, and records the verdict in `step_log` | ? | ADR-0057 | none |
| T72 | Upload text is screened for hidden instructions before any model reads it, and is always passed to a model as labelled data, never as instruction | ? | ADR-0057 | none |
| T73 | A coach reply never contains the system prompt, another case's data or an external link | ? | none | none |
| T74 | Every tool is classified read-only, internal write or external effect; an external-effect tool needs human approval; credentials stay in code | ? | ADR-0057 | none |
| T75 | The evaluation set contains prompt-attack cases; a regression blocks release | ? | ADR-0049 | none |
| T76 | In production nothing connects to the public internet; every service is reached over a private endpoint; start-up verifies it | ? | none | none |
| T77 | In production, traces and feedback stay inside the intranet (the decision trail, T84, replaces LangSmith there) | ? | ADR-0048 | none |
| T78 | The UI loads no font, script or style from outside the product | ? | none | none |
| T79 | Every request is authorised against the case team before the graph runs | ? | none | none |
| T80 | Each field-log entry carries value, time, person, reason and source, and the log is append-only | ? | ADR-0020 | none |
| T81 | The as-is process and its performance are stored structured in Define's record and read by later phases through the Store | ? | ADR-0019 | none |
| T82 | Turn progress is streamed with LangGraph's `custom` stream mode | ? | none | none |
| T83 | Reply feedback is stored against the turn's trace (T84 record in production) | ? | none | none |
| T84 | `step_log` and the field log form the decision trail: append-only, kept for the life of the case, served read-only by a route, never leaving the intranet | ? | ADR-0020 | none |