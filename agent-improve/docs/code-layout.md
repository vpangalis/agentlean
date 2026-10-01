# Code layout

Generated from the code on every commit by `tools/architecture/generate_layout.py` (the pre-commit
hook, `--stage`); never edited by hand. Linked from [ARCHITECTURE.md §3.1](../ARCHITECTURE.md).

<!-- BEGIN GENERATED: code layout — tools/architecture/generate_layout.py -->

### Code layout — `backend/`, generated

Classes are allowed only in files marked **C**; elsewhere module-level functions (ARCHITECTURE.md §3.1).

| Folder | File | Says | Public names |
|---|---|---|---|
| — | `app.py` C | — | `RequestIdMiddleware`, `startup`, `shutdown` |
| `core/` | `checkpointer.py` C | Azure Blob checkpointer for Agent Improve. | `ConcurrentTurnError`, `AzureBlobCheckpointSaver`, `get_checkpointer` |
|  | `citations.py` C | Citation models for Agent Improve. | `CitationRecord`, `CitationBundle` |
|  | `config.py` C | — | `KNOWLEDGE_INDEX_DEFAULT`, `Settings` |
|  | `content_safety.py` | Azure AI Content Safety — Prompt Shields. ADR-0057 (ACCEPTED, fail closed); T71, T72. | `API_VERSION`, `TIMEOUT_S`, `MAX_CHARS`, `configured`, `development_mode`, `required`, `is_content_filter`, `retry_on`, `check_startup`, `shield` |
|  | `conversation.py` | Conversation <-> `messages` marshalling — procedure step 4.2. | `V1_PRESENTATION_KEYS`, `COACHING_BLOCK_KEYS`, `MOVE_RECORD_KEY`, `QUALITY_FEEDBACK_KEY`, `TURN_RECORD_KEYS`, `message_to_turn`, `turn_to_message`, `transport`, `strip_transport` |
|  | `diagrams.py` C | Diagram types and schemas for `propose_diagram` — procedure step 6.2. | `DIAGRAM_TYPES`, `SIPOC_COLUMNS`, `SIPOC_SOURCES`, `DiagramError`, `sipoc_columns`, `build_sipoc`, `build_mindmap_5w2h`, `build_baseline_target`, `BUILDERS` |
|  | `errors.py` C | Structured errors for external service failures — CLAUDE.md §12.3. | `AgentImproveError`, `KnowledgeSearchError`, `StateSchemaVersionError`, `CaseBusyError` |
|  | `graph.py` C | The main graph — ONE compiled graph, entered at the case's current phase. ADR-0063. | `RECURSION_LIMIT`, `ESCALATE_NODE`, `WIRED_PHASES`, `INPUT_MAPPERS`, `OUTPUT_MAPPERS`, `PhaseNotWired`, `phase_node`, `escalate_node`, `route_to_phase`, `graph_builder`, `get_graph` |
|  | `guard.py` | The input guard — a node at the front of the main graph. ADR-0057 (placement, fail closed), | `NODE`, `MAX_CHARS`, `FIXED_RULES`, `fixed_rules`, `blocked`, `without_blocked`, `current_field`, `record`, `input_guard` |
|  | `guard_messages.py` | The guard's message catalogue — ADR-0067 point 2 (ACCEPTED); R20, T71, T72, T92, T93. | `A`, `B`, `D_LENGTH`, `D_RATE`, `D_UPLOAD_NOTICE`, `D_UPLOAD_MAX`, `AZURE`, `UNAVAILABLE`, `UPLOAD_UNAVAILABLE`, `sample`, `element_name`, `reply` |
|  | `llm.py` | Single source of truth for all LangChain LLM instances in Agent Improve. | `PREMIUM_TIER`, `OPERATIONAL_TIER`, `ROLE_DEPLOYMENTS`, `DEFAULT_TEMPERATURE`, `ROLE_TEMPERATURES`, `role_temperature`, `TURN_LLM_CALLS`, `warm_turn_llms`, `get_llm`, `block_text` |
|  | `logging_setup.py` C | Logging configuration for Agent Improve. | `configure_logging` |
|  | `metrics.py` | The metric single-authority invariant. | `PRIMARY_MIRRORED_SCALARS`, `PRIMARY_MIRRORED_DICT`, `NONE_THIS_PHASE`, `primary_entry`, `check_single_authority`, `assert_single_authority` |
|  | `migrations.py` | State schema versions and their migrations — ADR-0065 (ACCEPTED, founder 2026-09-29), T88. | `VERSION_KEY`, `UNVERSIONED`, `migrate_v1_to_v2`, `migrate_v2_to_v3`, `migrate_v3_to_v4`, `migrate_v4_to_v5`, `MIGRATIONS`, `current`, `version_of`, `check_loadable`, `migrate`, `stamp_metadata`, `stamp_record`, `read_record`, `migrate_case` |
|  | `pii.py` | Personal data masked before a model sees it — T87, ADR-0062 (DEF-144). | `PHONE`, `IBAN`, `TYPES`, `STRATEGY`, `detect`, `mask`, `executor_middleware`, `counted` |
|  | `prompts.py` | All prompt constants for Agent Improve. | `ORCHESTRATOR_SYSTEM_BASE`, `ORCHESTRATOR_DEFINE_CONTEXT`, `ORCHESTRATOR_ANALYSE_CONTEXT`, `ORCHESTRATOR_IMPROVE_CONTEXT`, `ORCHESTRATOR_CONTROL_CONTEXT`, `SIPOC_DRAFT_PROMPT`, `SIPOC_TRANSITION_MESSAGE`, `ORCHESTRATOR_MEASURE_CONTEXT`, `EXTRACTION_MEASURE`, `MEASURE_GATE_FIELDS`, `STATE_SUMMARY_TEMPLATE`, `EXTRACTION_DEFINE`, `EXTRACTION_ANALYSE`, `EXTRACTION_IMPROVE`, `EXTRACTION_CONTROL`, `REFLECTION_CHECK`, `ESCALATION_REPORT`, `VISION_EXTRACT_PROMPT`, `UPLOAD_INTERPRET_SYSTEM`, `UPLOAD_ELEMENT_CHECK`, `UPLOAD_INTERPRET_DATA`, `EXTRACTION_MAP`, `ORCHESTRATOR_CONTEXT_MAP`, `VARIANT_PROMPT`, `MEMORY_HIERARCHY`, `ANTI_HALLUCINATION`, `CAPTURE_CONTRACT`, `COACHING_STANCE`, `CONTRADICTION_CHECK`, `DEFINE_COACH_PROMPT`, `MEASURE_COACH_PROMPT`, `ANALYSE_COACH_PROMPT`, `IMPROVE_COACH_PROMPT`, `CONTROL_COACH_PROMPT`, `PHASE_COACH_PROMPT`, `SECTION_RULES`, `SECTION_SCRIPT`, `SECTION_STATE`, `SECTION_MOVE`, `SECTION_FEEDBACK`, `SECTION_CONVERSATION`, `COACH_INPUT_SECTIONS`, `MOVE_PREAMBLE`, `MOVE_INSTRUCTIONS`, `MOVE_OPENING`, `UPLOAD_TURN`, `UPLOAD_READ_NOTE`, `UPLOAD_CHECK_HEAD`, `UPLOAD_CHECK_EARLIER`, `UPLOAD_CHECK_SHOWS`, `UPLOAD_CHECK_CONFLICTS`, `UPLOAD_CHECK_MISSING`, `UPLOAD_CHECK_COMPLETE`, `STORE_NOTE_STORED`, `READ_BACK_CARRIED`, `READ_BACK_METRIC`, `STORE_NOTE_NOT_STORED`, `FALLBACK_RESEND`, `PLANNER_JUDGMENT_PROMPT`, `PLANNER_JUDGMENT_READING_BACK`, `DEFINE_RUBRIC`, `GATE_GRADER_PROMPT`, `COACHING_QUALITY_RUBRIC` |
|  | `request_context.py` | Request-scoped context for Agent Improve. | `new_request_id`, `set_request_id`, `get_request_id`, `set_case_id`, `get_case_id`, `set_phase`, `get_phase`, `current_context` |
|  | `state.py` C | Graph state schemas. | `STATE_SCHEMA_VERSION`, `SupervisorState`, `SUPERVISOR_STATE_FIELDS`, `SUPERVISOR_STATE_DERIVED_FIELDS`, `SUPERVISOR_STATE_REMOVED_FIELDS`, `ImproveGraphState` |
|  | `store.py` C | `AzureBlobStore` — the `BaseStore` implementation carrying cross-phase artifacts. | `STORE_PREFIX`, `blob_path`, `AzureBlobStore`, `get_store` |
|  | `substate.py` C | `PhaseState` — the Level 2 per-phase subgraph state. | `SufficiencyJudgment`, `CoachingPlan`, `FIELDS_CAPTURED_NORMALIZED`, `CoachingResponse`, `CONTRADICTION_FLAG_KEYS`, `PRESENTATIONAL_FIELDS`, `presentational_gaps`, `is_empty_capture`, `split_captures`, `FIELD_LOG_ENTRY_KEYS`, `field_log_key`, `merge_field_log`, `value_history`, `PhaseState`, `PHASE_STATE_IDENTITY_FIELDS`, `PHASE_STATE_PLUMBING_FIELDS`, `PHASE_STATE_CONTENT_FIELDS`, `PHASE_STATE_ENGINE_MANAGED_FIELDS`, `PHASE_STATE_AUTHOR_POPULATED_FIELDS`, `PHASE_STATE_READ_ONLY_FIELDS` |
|  | `tracing.py` | LangSmith tracing initialisation for Agent Improve. | `init_tracing`, `tracing_enabled`, `child_span`, `child_trace` |
| — | `escalate.py` | — | `escalate` |
| `gateway/` | `routes.py` C | — | `UPLOAD_NOTICE_MB`, `UPLOAD_MAX_MB`, `TURNS_PER_MINUTE`, `health`, `summarise_session`, `get_session_context`, `create_case`, `ClientGone`, `CASE_BUSY`, `apply_capture`, `ask`, `gate_review`, `auto_detect_purpose`, `upload_file`, `delete_case_file`, `assemble_gate_document`, `decide_gate`, `submit_gate`, `get_registry`, `get_case` |
|  | `schemas.py` C | — | `CaseCreateRequest`, `AskRequest`, `UploadMetaRequest`, `GateSubmitRequest`, `CitationOut`, `CapturedField`, `GateStatus`, `AskResponse`, `CaseCreateResponse`, `GateSubmitResponse`, `GateDecisionRequest`, `GateDecisionResponse`, `RegistryEntryOut`, `HealthResponse`, `CaseFile`, `SummariseTurn`, `SummariseRequest`, `SummariseResponse`, `ContextRequest`, `ContextResponse`, `GateReviewField`, `GateReviewResponse` |
| `knowledge/` | `computation.py` C | The twenty DMAIC computation tools — procedure steps 5.3 and 5.4. | `SHEWHART`, `IMR_E2`, `IMR_D4`, `SIGMA_SHIFT`, `calculate_expected_savings`, `calculate_sigma_level`, `calculate_cpk`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq`, `calculate_grr`, `calculate_sample_size_proportion`, `calculate_sample_size_mean`, `t_test`, `chi_square_test`, `anova`, `pearson_correlation`, `linear_regression`, `calculate_doe_main_effects`, `xbar_r_chart_limits`, `imr_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk`, `UNIVERSAL_TOOL_COUNT`, `PHASE_TOOL_CEILING`, `COMPUTATION_TOOLS_BY_PHASE`, `COMPUTATION_TOOLS` |
|  | `fusion.py` C | Multi-query fusion — Reciprocal Rank Fusion and the variant schema. | `RRF_K`, `MIN_VARIANTS`, `MAX_VARIANTS`, `TURN_TOOL_MODEL_CALLS`, `CALLING_TOOL`, `T`, `QueryVariants`, `reciprocal_rank_fusion`, `generate_variants`, `run_multi_query` |
|  | `retriever.py` | — | `RETRIEVAL_EXCEPTIONS`, `get_search_client`, `warm_clients`, `close_clients`, `get_embeddings`, `KNOWLEDGE_INDEX_FIELDS`, `get_knowledge_vectorstore`, `EVIDENCE_INDEX_FIELDS`, `EVIDENCE_SELECT`, `EVIDENCE_KIND_DEFAULT`, `get_evidence_vectorstore`, `CROSS_PHASE_RELEVANCE`, `search_knowledge`, `search_cases`, `search_evidence`, `active_work_product_label`, `build_knowledge_context` |
|  | `tool_args.py` C | Pydantic arg schemas for the twenty computation tools — procedure step 5.3. | `ExpectedSavingsArgs`, `SigmaLevelArgs`, `CpkArgs`, `DpmoArgs`, `YieldRtyArgs`, `FtqArgs`, `GrrArgs`, `SampleSizeProportionArgs`, `SampleSizeMeanArgs`, `TTestArgs`, `ChiSquareArgs`, `AnovaArgs`, `PearsonArgs`, `LinearRegressionArgs`, `DoeMainEffectsArgs`, `XbarRArgs`, `ImrArgs`, `PChartArgs`, `CChartArgs`, `PostImprovementCpkArgs`, `LoadEvidenceSeriesArgs`, `ProposeTemplateArgs`, `ProposeDiagramArgs` |
|  | `tools.py` C | The three `rag_lookup_*` tools, plus the four unbound cross-agent tools. | `CROSS_PHASE_RELEVANCE`, `PER_VARIANT_K`, `rag_lookup_methodology`, `rag_lookup_evidence`, `rag_lookup_case_history`, `RAG_LOOKUP_TOOLS`, `search_resolve_cases`, `search_resolve_knowledge`, `search_resolve_evidence`, `search_flow_vsm`, `TEMPLATE_TYPES`, `propose_template`, `propose_diagram`, `load_evidence_series`, `first_numeric_column`, `UNIVERSAL_TOOLS` |
| `middleware/` | `__init__.py` | The coaching agent's middleware stack — procedure steps 6.3 to 6.5. | — |
|  | `coherence.py` C | `CoherenceMiddleware` — position 7 — procedure step 6.5. | `COHERENCE_MAX_RETRIES`, `SKIP_GRADER_KEY`, `CoherenceMiddleware` |
|  | `contradiction.py` C | `ContradictionDetectionMiddleware` — position 6 — procedure step 6.5. | `ContradictionDetectionMiddleware` |
|  | `grader.py` C | `DMAICGraderMiddleware` — position 8 — procedure step 6.5. | `GRADER_MAX_ITERATIONS`, `MAX_ITERATIONS_WARNING`, `MOVE_EXCLUDES`, `applies`, `rubric_for_move`, `DMAICGraderMiddleware` |
|  | `skills.py` C | `DMAICSkillsMiddleware` — position 2 — procedure step 6.3. | `SKILLS_ROOT`, `SKILL_DIRS`, `LEVEL_1_TOKEN_BUDGET`, `SkillNotFound`, `frontmatter`, `description`, `instructions`, `allowed_tools`, `script_record`, `EXAMPLE_MATCH_RATIO`, `EXAMPLE_MIN_CHARS`, `worked_examples`, `example_match`, `script_step`, `script_section`, `acceptance_criteria`, `field_needs`, `teaching_blocks`, `level_1_catalogue`, `DMAICSkillsMiddleware` |
|  | `state_injection.py` C | `BeforeModelStateInjection` — position 1 — procedure step 6.3. | `BeforeModelStateInjection` |
|  | `turn_tools.py` | The coach's tools per turn type — ADR-0069 (refining ADR-0068), founder rulings 1 and 6, 2026-09-28. | `TOOLS_BY_TURN`, `offered`, `turn_tools_middleware` |
| `phases/analyse/` | `analyse.py` | — | — |
|  | `graph.py` | Analyse's phase subgraph. | `PHASE` |
|  | `mappers.py` | Analyse's boundary mappers — procedure step 3.3. | `PHASE`, `PRIOR_PHASE`, `PHASE_CONTEXT_FIELDS`, `analyse_input_mapper`, `analyse_output_mapper` |
|  | `nodes.py` | The five nodes of the Analyse phase subgraph. | `PHASE`, `step_key`, `planner`, `executor`, `validation_stack`, `gate_review`, `gate_apply` |
|  | `orchestrate.py` | — | `VALID_ANALYSE_KEYS`, `ANALYSE_WORK_PRODUCTS`, `orchestrate_analyse` |
|  | `schema.py` C | — | `AnalysePhaseInput`, `ANALYSE_TIER_1_FIELDS`, `ANALYSE_TIER_2_FIELDS`, `AnalyseOutput`, `assemble_analyse_gate_document` |
|  | `validate.py` | Analyse phase gate validator — Layer 2b. | `ANALYSE_REQUIRED_FOR_GATE`, `acknowledged_gaps`, `validate_analyse` |
| `phases/control/` | `analyse.py` | — | — |
|  | `graph.py` | Control's phase subgraph. | `PHASE` |
|  | `mappers.py` | Control's boundary mappers — procedure step 3.3. | `PHASE`, `PRIOR_PHASE`, `PHASE_CONTEXT_FIELDS`, `control_input_mapper`, `control_output_mapper` |
|  | `nodes.py` | The five nodes of the Control phase subgraph. | `PHASE`, `step_key`, `planner`, `executor`, `validation_stack`, `gate_review`, `gate_apply` |
|  | `orchestrate.py` | — | `VALID_CONTROL_KEYS`, `CONTROL_WORK_PRODUCTS`, `orchestrate_control` |
|  | `schema.py` C | — | `ControlPhaseInput`, `CONTROL_TIER_1_FIELDS`, `CONTROL_TIER_2_FIELDS`, `ControlOutput`, `assemble_control_gate_document`, `CONTROL_PLAN_KEYS` |
|  | `validate.py` | Control phase gate validator — Layer 2b. | `CONTROL_REQUIRED_FOR_GATE`, `acknowledged_gaps`, `validate_control` |
| `phases/define/` | `analyse.py` | — | — |
|  | `graph.py` | Define's phase subgraph. | `PHASE` |
|  | `mappers.py` | Define's boundary mappers — procedure step 3.3. | `PHASE`, `define_input_mapper`, `define_output_mapper` |
|  | `nodes.py` | The five nodes of the Define phase subgraph. | `PHASE`, `step_key`, `planner`, `executor`, `validation_stack`, `gate_review`, `gate_apply` |
|  | `orchestrate.py` | — | `orchestrate_define` |
|  | `parse.py` | Define values read in code, before any model — founder ruling 3, 2026-09-28 (M1 loop package 4). | `unit_of`, `parse_limit`, `number_in`, `parse_sipoc`, `missing_columns`, `METRIC_FIELDS`, `normal_unit`, `is_estimate`, `metric_value`, `as_metric`, `metric_text`, `primary_unit` |
|  | `report.py` | The DEFINE REPORT — requirement R5 (`docs/requirements/business.md`, 2026-09-26). | `FIVE_W_TWO_H_QUESTIONS`, `REPORT_SECTIONS`, `element_of`, `define_report` |
|  | `schema.py` C | Define phase gate document. | `DEFINE_REQUIRED_FIELDS`, `DEFINE_FIELD_ORDER`, `DEFINE_REQUIRED_FOR_GATE_FIELDS`, `DEFINE_POSITIONS`, `MetricValue`, `define_position`, `define_progress`, `METRIC_DEFINITION_KEYS`, `PHASE_METRIC_REQUIRED_KEYS`, `SIPOC_KEYS`, `PROJECT_SCOPE_KEYS`, `TEAM_MEMBER_KEYS`, `CTQ_KEYS`, `FIVE_W_TWO_H_KEYS`, `BENEFITS_ANALYSIS_KEYS`, `DefineOutput`, `DEFINE_METRIC_SOURCE`, `NOT_ADDRESSED`, `define_phase_metrics`, `assemble_define_gate_document` |
|  | `validate.py` | Define phase gate validator. | `DEFINE_REQUIRED_FOR_GATE`, `validate_define` |
|  | `visuals.py` | Define's visuals, drawn by the program — ADR-0070 (founder, 2026-09-28; C1, C2, R2). | `VISUAL_OF`, `UI_KEY`, `draw`, `for_field`, `report_visuals` |
| `phases/` | `gate_assembly.py` C | The two invariants that run before a gate document is constructed. | `GATE_METADATA_FIELDS`, `GateAssemblyError`, `check_field_coverage`, `build_gate_document`, `tier_1`, `tier_2` |
|  | `gate_registry.py` C | One place that knows all five gate documents — procedure step 3.4. | `GateSpec`, `GATE_SPECS`, `declared_type`, `split_by_declared_type`, `tier_of`, `review_rows`, `missing_structured`, `missing_gate_fields` |
| `phases/improve/` | `analyse.py` | — | — |
|  | `graph.py` | Improve's phase subgraph. | `PHASE` |
|  | `mappers.py` | Improve's boundary mappers — procedure step 3.3. | `PHASE`, `PRIOR_PHASE`, `PHASE_CONTEXT_FIELDS`, `improve_input_mapper`, `improve_output_mapper` |
|  | `nodes.py` | The five nodes of the Improve phase subgraph. | `PHASE`, `step_key`, `planner`, `executor`, `validation_stack`, `gate_review`, `gate_apply` |
|  | `orchestrate.py` | — | `VALID_IMPROVE_KEYS`, `IMPROVE_WORK_PRODUCTS`, `orchestrate_improve` |
|  | `schema.py` C | — | `ImprovePhaseInput`, `IMPROVE_TIER_1_FIELDS`, `IMPROVE_TIER_2_FIELDS`, `ImproveOutput`, `assemble_improve_gate_document` |
|  | `validate.py` | Improve phase gate validator — Layer 2b. | `IMPROVE_REQUIRED_FOR_GATE`, `acknowledged_gaps`, `validate_improve` |
| `phases/` | `mappers_common.py` C | Shared mechanics for the ten boundary mappers — procedure step 3.3. | `PHASE_ORDER`, `KIND_CASE`, `KIND_ARTIFACTS`, `prior_phase`, `read_case_record`, `CASE_RECORD_FRAMING_FIELDS`, `CASE_RECORD_UPLOADS`, `CASE_RECORD_CAPTURED`, `CASE_RECORD_FIELD_LOG`, `CASE_RECORD_ASKS`, `CASE_RECORD_FIELD_STATUS`, `case_record_from_document`, `captured_from_document`, `field_log_from_document`, `uploads_from_document`, `write_case_record`, `read_gate_document`, `PriorGateDocumentMissing`, `asks_for_phase`, `write_asks`, `uploads_for_phase`, `captured_for_phase`, `field_status_for_phase`, `field_log_for_phase`, `new_phase_state`, `advance`, `write_gate_document`, `compose_phase_context` |
| `phases/measure/` | `analyse.py` | — | — |
|  | `graph.py` | Measure's phase subgraph. | `PHASE` |
|  | `mappers.py` | Measure's boundary mappers — procedure step 3.3. | `PHASE`, `PRIOR_PHASE`, `PHASE_CONTEXT_FIELDS`, `measure_input_mapper`, `measure_output_mapper` |
|  | `nodes.py` | The five nodes of the Measure phase subgraph. | `PHASE`, `step_key`, `planner`, `executor`, `validation_stack`, `gate_review`, `gate_apply` |
|  | `orchestrate.py` | — | `VALID_MEASURE_KEYS`, `MEASURE_WORK_PRODUCTS`, `orchestrate_measure` |
|  | `schema.py` C | — | `DataCollectionEntry`, `MeasurePhaseInput`, `MEASURE_TIER_1_FIELDS`, `MEASURE_TIER_2_FIELDS`, `MeasureOutput`, `assemble_measure_gate_document`, `DETAILED_PROCESS_MAP_KEYS` |
|  | `validate.py` | Measure phase gate validator — Layer 2b. | `MEASURE_REQUIRED_FOR_GATE`, `acknowledged_gaps`, `validate_measure` |
| `phases/` | `moves.py` | The coaching move, decided in code — step 6.61. | `OFFER_PARK`, `MOVES`, `PARK_AFTER`, `PARKED`, `STATUSES`, `REVISE_CLICK`, `REVISE_REASON`, `OFFER_PARK_REASON`, `PARKED_REASON`, `TRY_AGAIN_REASON`, `RETURN_REASON`, `CHANGE_REASON`, `CONFIRM_INCOMPLETE`, `COLUMNS_MISSING`, `REJECTED`, `REJECT_REASON`, `COMPOSED_FIELDS`, `positions`, `focus`, `last_record`, `last_feedback`, `belt_message`, `is_confirmation`, `status_of`, `field_statuses`, `current`, `parked`, `park_events`, `element_rows`, `decide`, `pending_store` |
|  | `nodes_common.py` | The five node bodies, parameterised by phase — procedure step 4.4. | `NODE_NAMES`, `step_key`, `entry_mode`, `planner`, `to_v1_state`, `COACH_RECURSION_BACKSTOP`, `MEASURED_HOP_SECONDS`, `HOP_BUDGET_COMPOSE_RESERVE`, `COACH_HOP_BUDGET`, `TURN_MODEL_CALLS`, `AFTER_AGENT_CALLS`, `REMAINING_STEPS_FLOOR`, `EXECUTOR_RUN_TIMEOUT`, `RETRY_MAX`, `TOOL_RETRY_ON_FAILURE`, `SUMMARIZATION_TRIGGER`, `SUMMARIZATION_KEEP`, `ROUTED_READ_FAILED`, `FIELD_LOG_SOURCES`, `COACHING_BLOCKS`, `TEACHING_MOVES`, `upload_check_text`, `turn_type_of`, `CHANGE_QUESTION`, `executor`, `executor_timeout_handler`, `validation_stack`, `gate_review`, `gate_apply` |
|  | `record.py` | A phase's unfinished work, carried in the checkpoint — ADR-0066 (ACCEPTED), T13. | `KEY`, `empty`, `merge`, `latest`, `latest_by_phase` |
|  | `subgraph_common.py` | `build_phase_subgraph(phase, llm)` — the one parameterised builder. | `PLANNER_RETRY`, `phase_nodes`, `build_phase_subgraph` |
| `storage/` | `blob.py` | Case records on Azure Blob — §10's second concern, as module-level functions. | `REGISTRY_BLOB_PATH`, `storage_configured`, `aclose`, `download_bytes`, `LEASE_SECONDS`, `case_lease`, `case_path`, `load_case`, `save_case`, `create_case`, `write_phase_gate`, `append_turn`, `load_registry`, `save_registry`, `register_case`, `upload_file` |
|  | `layout.py` | Where Agent Improve keeps things — the ONE owner of the storage layout. | `CASE_BLOB`, `REGISTRY_BLOB`, `UPLOAD_BLOB`, `CASE_LOCK_BLOB`, `CHECKPOINT_THREAD`, `CHECKPOINT_NAMESPACED`, `CHECKPOINT_LATEST`, `CHECKPOINT_HISTORY`, `CHECKPOINT_WRITES`, `STORE_PREFIX`, `STORE_BLOB`, `BLOB_PATHS`, `STORE_ROOT`, `KIND_CASE`, `KIND_ARTIFACTS`, `KIND_STEP_LOG`, `CASE_RECORD_KEY`, `STORE_NAMESPACES`, `EVIDENCE_INDEX`, `EVIDENCE_SELECT`, `CASE_INDEX`, `CASE_SELECT`, `search_fields` |
|  | `models.py` C | — | `TeamMemberRecord`, `CriterionCheck`, `ElementCheck`, `UploadInterpretation`, `UploadRecord`, `ChartRecord`, `AnalystOutputRecord`, `PhaseRecord`, `PhaseSummaryRecord`, `CaseDocument`, `RegistryEntry`, `CaseRegistry` |
| `upload/` | `agent.py` | Upload processing — classify, parse deterministically, interpret once. | `INTERPRET_SAMPLE_CHARS`, `process_upload` |
|  | `asks.py` | Asks — the coach's recorded requests for data. Procedure step 6.12. | `OPEN`, `ANSWERED`, `SENTINEL_ROLE`, `SENTINEL_KIND`, `SENTINEL_SHAPE`, `MEASURE_SHAPES`, `SHAPES_BY_PHASE`, `shape_for_field`, `content_digest`, `new_ask`, `open_ask_for_role`, `ensure_ask`, `check_shape`, `mark_answered` |
|  | `classifier.py` | Content-type and kind classification for uploads — procedure step 6.11. | `SUPPORTED_IMAGE_TYPES`, `ARTEFACT_PURPOSES`, `EVIDENCE_PURPOSES`, `EVIDENCE`, `ARTEFACT`, `classify_content_type`, `classify_kind`, `is_image`, `is_supported` |
|  | `parsers.py` | Deterministic extraction for the four formats a Belt actually uploads. | `TYPE_SAMPLE_ROWS`, `MAX_DISTINCT_SAMPLE`, `MAX_TEXT_CHARS`, `NUMERIC_TYPES`, `refusal`, `parse_csv`, `parse_xlsx`, `parse_pdf`, `parse_docx`, `parse_text`, `PARSERS`, `parse_upload`, `hidden_text` |
| `validation/` | `__init__.py` | Validation schemas and, from stage 7, the four-layer stack. | — |
|  | `rubric.py` | Layer 2d for Define — the R7 rubric, graded at the gate. | `DEFINE_CRITERIA`, `CODE_ONLY`, `MODEL_ASKS`, `grade_define` |
|  | `schemas.py` C | Structured outputs for middleware positions 7 and 8 — procedure step 6.5. | `CoherenceResult`, `CriterionResult`, `CoachingGraderVerdict`, `CriterionVerdict`, `GraderVerdict` |

<!-- END GENERATED: code layout -->
