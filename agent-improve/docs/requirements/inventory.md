# As-is capability inventory (DRAFT — founder, 2026-09-26)

> **DRAFT — a read-only inventory, not a requirement.** No product change, no live model call, no
> build. Every row describes what exists at `8a670e1`. **State** is proven by the test named, or by
> the recorded outcome in `docs/test-results.json` (2026-09-26, 1,311 passed, 67 skipped — the
> skipped are all live or storage runs), or by reading when no test exists (then `unknown` or `by
> reading`). **Covered by** is a requirement id from this folder (R Define, W workspace, M Measure,
> T technical — [platform.md](platform.md)) or `none`. **Reuse** is a proposal only.

Paths: `ui/` and `backend/` are under `agent-improve/`. The whole UI is one file, `ui/index.html`.

## 1. UI

| Id | Area | Capability | Evidence | State | Covered by | Reuse |
|---|---|---|---|---|---|---|
| U01 | UI | Landing screen: New case, Open case | `ui/index.html::#scr-landing`, `showScreen` | works — plain switch | none | keep — the entry point |
| U02 | UI | Recent cases list: phase, leader, days in phase, red/amber/green dot | `ui/index.html::loadRegistry` → `GET /registry` | works — `test_capability_rows.py::test_row_1` | none | keep — needs a requirement (inventory Q64) |
| U03 | UI | Open a recent case, asking the user's name in a browser prompt | `ui/index.html::quickOpenCase` | works — `test_row_1` | R8 (identity, later) | fix — the name prompt goes when R8 lands |
| U04 | UI | Case number badge on the create form | `ui/index.html::initCreate`, `#new-case-id` | broken — the browser invents an id; the server assigns its own (`routes.py::create_case`) | none | fix — show the server's id after create |
| U05 | UI | Create form: title, department, target date | `ui/index.html::submitCreateCase` → `POST /cases` | unknown — no test of this form | none | keep — add a test |
| U06 | UI | Pick belt level (Yellow, Green, Black) | `ui/index.html::selectBelt` | works — sent as `belt_level` | none (Q24) | keep |
| U07 | UI | Add team members (name, role) | `ui/index.html::addTeamMember`, `renderTeamList` | works — matches the case schema | R4, R7 (team element) | keep |
| U08 | UI | Upload documents on the create form | `ui/index.html::handleCreateFiles` | broken — lists names, never sends the files | R10 (draft), W5 | fix — or drop until R10 is ratified |
| U09 | UI | "Create case and begin Define" | `ui/index.html::submitCreateCase` | unknown — no test | none | keep — add a test |
| U10 | UI | Search a case by number, title or leader | `ui/index.html::doSearch` | works — registry route, first match only | none | keep |
| U11 | UI | Join a case with a name | `ui/index.html::joinCase` | works — same open path as `test_row_1` | R8 | keep |
| U12 | UI | Workspace header: case badge, user initials | `ui/index.html::openWorkspace` | works | none | keep |
| U13 | UI | Phase navigation: active, done, locked, viewing | `ui/index.html::renderPhaseNav` | works | W2 | keep |
| U14 | UI | Define progress in the nav ("X/26", six groups) | `ui/index.html::buildNavDefineStatus` | partial — counts the old field keys, not R4's elements | W2, R4 | fix — read the server's report elements |
| U15 | UI | Measure progress in the nav | `ui/index.html::buildNavMeasureStatus` | unknown — keys not checked against the Measure schema | M1 | rebuild — with the Measure requirements |
| U16 | UI | Overall progress bar ("Phase n of 5") | `ui/index.html::#prog-fill` | works — fixed percentages | W2 | keep |
| U17 | UI | Case files panel, grouped by phase | `ui/index.html::buildCaseFilesNav` | works — `GET /cases/{id}` returns `files` | W5 | keep |
| U18 | UI | Upload file from the files panel | `ui/index.html::triggerFileUpload` → `POST /upload` | partial — no UI test; the route is proven live (`test_row_8`) | W5 | keep — add a test |
| U19 | UI | Click a file to preview it | `ui/index.html::previewCaseFile` | broken — a stub toast | none | fix — or drop |
| U20 | UI | Remove a file | `ui/index.html::deleteCaseFile` → `DELETE /files/...` | partial — the stored file and index entry stay behind | none (Q60) | fix — delete the blob and index entry too |
| U21 | UI | Tabs: Phase overview, AI guide, Gate, History | `ui/index.html::selectTab` | works | W1 | keep |
| U22 | UI | Phase overview pages for all five phases | `ui/index.html::renderOverview` | works — fixed text typed in the page | W1 | fix — W1 wants the text from the skills, never typed twice |
| U23 | UI | Pop-open explainers ("What is 5W2H?") | `ui/index.html::toggleExplainer` | works | W1 | keep |
| U24 | UI | "Start the AI guide" button | `ui/index.html::renderOverview` | works | none | keep |
| U25 | UI | Orientation text says History is "under ···" | `ui/index.html::renderOverview` | broken — no such menu; History is a tab | W1 | fix — one sentence |
| U26 | UI | Tool briefing page | `ui/index.html::openToolBriefing` | broken — unreachable (only a dead branch opens it) | none | drop |
| U27 | UI | Right-hand progress card | `ui/index.html::buildProgressNarrative` | broken — never called | none | drop |
| U28 | UI | Define field checklist | `ui/index.html::renderDefineChecklist` | broken — never called | none | drop |
| U29 | UI | Chat history redrawn from saved turns | `ui/index.html::renderHistoryTurns`, `renderTurn` | works — `test_coaching_blocks.py` (node) | W3 | keep |
| U30 | UI | Reply blocks: progress, why it matters, example, your turn, warning | `ui/index.html::renderTurn` | works — `test_coaching_blocks.py::test_the_ui_renders_one_block_per_field` | R2 | keep |
| U31 | UI | "Welcome back" recap with hint cards | `ui/index.html::renderChat` | partial — built from old key groups in the browser | W3 | rebuild — W3 wants confirmed values from state |
| U32 | UI | First-time opener with "Ask this" card | `ui/index.html::sendPresetMessage` | works | R1 | keep |
| U33 | UI | Type and send a message | `ui/index.html::sendMessage` → `POST /ask` | partial — live row 2 was red on its last runs (45 s timeouts) | R1, T24 | keep — the timeout is the backend's |
| U34 | UI | Confirm / Change buttons under a read-back | `ui/index.html::renderTurn` (`#rb-confirm`, `#rb-change`) | unknown — backend proven (`test_moves`, `test_wiring`); buttons untested; gone after a reload | T6 | fix — show after reload; add a test |
| U35 | UI | "AI is thinking..." indicator | `ui/index.html::#typing` | partial — generic text, against the UI rule | none (Q42) | fix |
| U36 | UI | Source links under replies | `ui/index.html::renderTurn` (`.src-pill`) | partial — shows index, not file and page | none (Q36) | fix — file and page |
| U37 | UI | "Gate updated — section complete" pop-up | `ui/index.html::showSectionToast` | unknown — depends on `section_completed` | none | keep — verify |
| U38 | UI | Fields-captured hint under the chat box | `ui/index.html::renderChips` | works | none | keep |
| U39 | UI | Suggestion chips | `ui/index.html::renderChatChips` | broken — stubbed to `return` | W4 | drop — or rebuild for W4 |
| U40 | UI | Welcome-back banner from the server | `ui/index.html::loadSessionGreeting` | broken — stubbed; `POST /context` unused | W3 | drop — W3 rebuilds it |
| U41 | UI | Attach a file in the chat | `ui/index.html::handleChatFile` → `POST /upload` | partial — reads a field `/upload` does not return; file not added to the panel | W5 | fix |
| U42 | UI | Live 5W2H mind map under the chat | `ui/index.html::render5W2HMindmap` | works — `test_coaching_blocks.py` | R2 | keep |
| U43 | UI | Live SIPOC with Table / Flow toggle | `ui/index.html::renderSipocDiagram` | works | R2 | keep |
| U44 | UI | Goal and scope, benefits, charter cards | `ui/index.html::renderGoalScopeCard`, `renderBenefitsCard`, `renderCharterCard` | partial — old field names | R5 | fix — or drop for the R5 report |
| U45 | UI | "All sections complete" banner | `ui/index.html::renderLiveViz` | partial — old keys | R5 | fix |
| U46 | UI | "Submit for gate review" under the chat | `ui/index.html::submitGateReview` → `POST /gate` | works — `test_gate_acceptance.py` | R6 | keep |
| U47 | UI | Gate tab phase switcher | `ui/index.html::renderGate` | works | none | keep |
| U48 | UI | Gate review panel with editable fields | `ui/index.html::renderGateReview` | broken — the panel is removed before it draws; edits never sent | none (Q19) | rebuild — or drop for Define, which uses the report |
| U49 | UI | Define report, seven sections, badges, history | `ui/index.html::renderDefineReport`, `defineReportHtml` | works — `test_define_report.py::test_the_gate_screen_draws_the_seven_sections_and_both_diagrams` | R5 | keep |
| U50 | UI | SIPOC inside the report | `ui/index.html::renderDefineReport` | works — same test | R5 | keep |
| U51 | UI | Submit the Define report for acceptance | `ui/index.html::defineReportActionsHtml` | works — `test_gate_acceptance.py::test_the_screen_offers_approve_and_reject_only_while_paused` | R6 | keep |
| U52 | UI | Approve the report | `ui/index.html::decideDefineReport` → `POST /gate/decision` | works — `test_gate_acceptance.py::test_the_pause_survives_a_restart_and_an_approval_writes_once` | R6, T15 | keep |
| U53 | UI | Reject the report: parts and a reason | `ui/index.html::decideDefineReport` | works — `test_gate_acceptance.py::test_a_rejection_names_an_element_and_a_reason` | R6, T16 | keep |
| U54 | UI | Measure gate document | `ui/index.html::renderGate` (measure) | unknown — old keys, no test | M1 | rebuild — with Measure requirements |
| U55 | UI | Analyse gate document | `ui/index.html::renderGate` (analyse) | unknown | none | rebuild |
| U56 | UI | Improve gate document | `ui/index.html::renderGate` (improve) | unknown | none | rebuild |
| U57 | UI | Control gate document | `ui/index.html::renderGate` (control) | unknown | none | rebuild |
| U58 | UI | Locked future phase on the Gate tab | `ui/index.html::renderGate` | works | none | keep |
| U59 | UI | Leftover gate page for other phases | `ui/index.html::renderGate` (stub branch) | broken — dead branch | none | drop |
| U60 | UI | Gate result screen (checked items, continue) | `ui/index.html::renderGateResult` | partial — old keys; can disagree with the server | R6 | fix |
| U61 | UI | "Reviewing gate..." state | `ui/index.html::submitGateReview` | works | none | keep |
| U62 | UI | History tab: sessions by date | `ui/index.html::renderHistory` | works — built in the browser | none | keep |
| U63 | UI | AI summary of each session | `ui/index.html::generateSessionSummary` → `POST /summarise` | partial — AI turns sent as `assistant`, summarised as "Team member" | none | fix |
| U64 | UI | Step-by-step plan view | `ui/index.html::renderSteps` | broken — unreachable | W4 | drop |
| U65 | UI | Live diagram view | `ui/index.html::renderDiagram` | broken — unreachable; Measure is placeholder art | none | drop |
| U66 | UI | Right panel of captured fields | `ui/index.html::renderRightPanel` | broken — never called; its elements are absent | none | drop |
| U67 | UI | Toast messages | `ui/index.html::toast` | works | none | keep |
| U68 | UI | Shared API error handling | `ui/index.html::apiJSON` | partial — three direct `fetch` calls skip it | T32 | fix |
| U69 | UI | Chat box grows with text | `ui/index.html` (input listener) | works | none | keep |

## 2. Backend

| Id | Area | Capability | Evidence | State | Covered by | Reuse |
|---|---|---|---|---|---|---|
| B01 | backend | Health check | `backend/gateway/routes.py::health` | unknown — no test; the UI never calls it | none (Q43) | keep — use it for connection status |
| B02 | backend | Summarise a session | `routes.py::summarise_session` | unknown — no test | none | fix — role mapping (U63) |
| B03 | backend | Re-entry greeting listing missing Define sections | `routes.py::get_session_context` | broken — by reading, checks v1 field names | W3 | drop — W3 rebuilds from state |
| B04 | backend | Create a case (blob, registry, Store copy) | `routes.py::create_case` | works — `test_capability_rows.py::test_row_1` (live) | none | keep |
| B05 | backend | Load a case and its files | `routes.py::get_case` | works — `test_row_1` | none | keep |
| B06 | backend | One coaching turn through the compiled graph | `routes.py::ask` | works for Define — `test_turn_graph.py`, `test_wiring.py`; broken from Measure on (B38) | R1, T8 | keep |
| B07 | backend | A client disconnect cancels the run | `routes.py::_run_turn`, `_until_disconnect` | works — `test_abandon.py::test_a_disconnect_cancels_the_run_and_raises_client_gone` | T33 | keep |
| B08 | backend | Merge a turn's captures and change log into the case blob | `routes.py::apply_capture` | works — `test_capture_accumulates.py::test_the_write_merges_rather_than_replacing` | T10, R6 | keep |
| B09 | backend | Copy upload asks to the Store case record | `routes.py::_mirror_asks` | works — used in `test_wiring`, `test_gate_acceptance` fixtures | W5 | keep |
| B10 | backend | Captured-field list and fixed suggestion chips | `routes.py::_build_captured_fields`, `_build_chips` | unknown — no test; chips hard-coded | none | fix — or drop with U39 |
| B11 | backend | Gate review read (rows, missing, document, Define report, awaiting decision) | `routes.py::gate_review` | works for Define — `test_define_report.py`; partial for others | R5, R6 | keep |
| B12 | backend | Submit a gate (Define pauses; others write on pass) | `routes.py::submit_gate` | works for Define — `test_gate_acceptance.py::test_a_validated_define_report_pauses_and_nothing_is_written`; others untested | R6, T14 | keep |
| B13 | backend | Approve or reject by resuming the pause | `routes.py::decide_gate`, `_pending_interrupts` | works for Define — `test_gate_acceptance.py` | R6, T15, T16 | keep — the gate write moves into `gate_apply` (ADR 0011) |
| B14 | backend | Assemble the gate document for writing | `routes.py::assemble_gate_document` | works — `test_gate_document_write.py` | T62 | keep — moves with D22 |
| B15 | backend | Upload: classify, parse, refuse unreadable, interpret once, version by digest | `routes.py::upload_file` | works — `test_row_8` (live), `test_uploads.py` | W5, M1 | keep |
| B16 | backend | Index an evidence upload | `routes.py::_index_upload` | works — `test_evidence_index.py` | T53 | keep |
| B17 | backend | Delete a file record | `routes.py::delete_case_file` | partial — no test; blob and index entry left behind | none (Q60) | fix |
| B18 | backend | Case registry list | `routes.py::get_registry` | works — `test_row_1`, `test_mutation_row_1_a_case_missing_from_the_list_is_red` | none (Q64) | keep |
| B19 | backend | App start-up: CORS, request id, static UI, warm-up, shutdown | `backend/app.py::RequestIdMiddleware`, `startup`, `shutdown` | partial — warm-up and no-trace proven; request id untested | T43 | keep — add the request-id test |
| B20 | backend | No streaming endpoint (`/ask/stream`) | `routes.py::ask` docstring | broken — not built | none (Q83) | rebuild — only if streaming is required |
| B21 | backend | Runtime graph: one phase node, checkpointer and Store | `backend/core/graph.py::get_graph` | works — `test_turn_graph.py::test_parent_carries_both_checkpointer_and_store` | T7 | keep |
| B22 | backend | Phase node: input mapper, subgraph, turn product on the reply | `graph.py::phase_node` | works for Define — `test_turn_graph.py` | T3 | keep — it never calls an output mapper (B39) |
| B23 | backend | Supervisor graph chaining the five phases and escalation | `graph.py::supervisor_builder`, `build_supervisor` | partial — compiled and tested, not the runtime | T7 | fix — decide whether it becomes the runtime |
| B24 | backend | Escalation node (plain message) | `graph.py::escalate_node` | partial — unreachable in production (`test_supervisor_graph.py::test_nothing_reaches_escalation_yet`) | T65 | fix — wire at three attempts |
| B25 | backend | v1 escalation report generator | `backend/escalate.py::escalate` | broken — dead code, imported by nothing | none | drop |
| B26 | backend | Refuse a phase with no subgraph | `graph.py::PhaseNotWired` | works — `test_turn_graph.py::test_a_case_in_a_non_phase_is_refused_rather_than_dispatched` | none | keep |
| B27 | backend | One five-node subgraph builder, 45 s executor timeout | `backend/phases/subgraph_common.py::build_phase_subgraph` | works — `test_phase_subgraphs.py::test_topology_matches_section_13` | T24 | keep |
| B28 | backend | Per-phase node wrappers | `backend/phases/*/nodes.py` | works — structure tested; docstrings stale for Define | none | keep — fix the docstrings |
| B29 | backend | Planner: move in code, sufficiency judgment | `backend/phases/nodes_common.py::planner`, `_judge` | works for Define — `test_validation_layer.py`, `test_wiring.py::test_wired_6_61_the_move_is_decided_in_code` | R3, T47 | keep |
| B30 | backend | Retrieval strategy per phase (Analyse multi-hop) | `nodes_common.py::_retrieval_strategy` | partial — the multi-hop plan is read by nothing | none | fix — or drop multi-hop |
| B31 | backend | Executor: coach agent, captures, change log, blocks, diagrams, computation rows, fallback | `nodes_common.py::executor`, `_build_executor` | works — `test_executor.py`, `test_executor_timeout.py` | R1, R2, T5, T32 | keep |
| B32 | backend | Hop cap and low-steps off-ramp | `nodes_common.py::COACH_HOP_BUDGET`, `_budgeted_rag_tools` | works — `test_hop_cap.py::test_the_cap_is_three` | T26, T27 | keep |
| B33 | backend | Node-issued read of a routed upload | `nodes_common.py::_dispatch_routed_read` | works — `test_executor.py::test_the_node_issued_call_stamps_consumed_at` | W5, T60 | keep |
| B34 | backend | v1 state bridge for validators | `nodes_common.py::to_v1_state` | works — a temporary seam | none | drop — at the v1 removal |
| B35 | backend | Validation stack: presence (2b), Define rubric (2d), shared cap | `nodes_common.py::validation_stack` | partial — `test_row_17` passes; layer 2c unbuilt; escalation computed, not raised | R7, T48, T63, T65 | fix |
| B36 | backend | Gate review pause (`interrupt()`) | `nodes_common.py::gate_review` | works for Define; pass-through for others | R6, T14 | keep |
| B37 | backend | Gate apply: approve ends, reject reopens | `nodes_common.py::gate_apply` | works for Define — `test_gate_acceptance.py::test_a_rejection_reopens_the_named_elements_and_the_coach_guides_back` | R6 | keep — takes the gate write (ADR 0011) |
| B38 | backend | Measure, Analyse, Improve, Control input mappers | `backend/phases/*/mappers.py::*_input_mapper` | broken — by reading: no runtime code writes the prior gate document to the Store, so entering Measure raises | none | fix — wire the output mapper |
| B39 | backend | Output mappers: gate document to the Store, advance phase | `backend/phases/mappers_common.py::write_gate_document`, `advance` | partial — unit tested (`test_mappers.py`), no production caller | T19, T23 | fix — call them from `gate_apply` |
| B40 | backend | Mapper helpers (case record, asks, uploads, change log) | `mappers_common.py::read_case_record` and others | works — `test_mappers.py`, `test_uploads.py` | T10 | keep |
| B41 | backend | Define input mapper | `backend/phases/define/mappers.py::define_input_mapper` | works — `test_mappers.py::test_define_context_comes_from_the_case_record` | T4 | keep |
| B42 | backend | v1 orchestrators for five phases | `backend/phases/*/orchestrate.py` | broken — dead code (`test_executor.py::test_the_v1_orchestrators_are_no_longer_called`) | none | drop |
| B43 | backend | Per-phase `analyse.py` files | `backend/phases/*/analyse.py` | broken — "Implementation pending" stubs | none | drop |
| B44 | backend | Field-presence validators per phase | `backend/phases/*/validate.py` | works for Define — `test_row_17`; others unknown | R7, T62 | keep |
| B45 | backend | Gate registry: tiers, review rows, missing fields | `backend/phases/gate_registry.py::GATE_SPECS` | works — `test_gate_documents.py`, `test_declared_types.py` | T62, T66 | keep |
| B46 | backend | Gate document assembly with coverage check | `backend/phases/gate_assembly.py::build_gate_document` | works — `test_gate_documents.py::test_missing_tier_1_field_raises_keyerror` | T62 | keep |
| B47 | backend | Define report | `backend/phases/define/report.py::define_report` | works — `test_define_report.py` | R5 | keep |
| B48 | backend | Define position ("Step n of 13") and progress | `backend/phases/define/schema.py::define_position` | works — `test_define_position.py` | R4, W2 | keep |
| B49 | backend | Move engine: positions, statuses, read-back, pending store | `backend/phases/moves.py::decide` | works for Define — `test_moves.py`; others walk their gate list | R3, T6 | keep |
| B50 | backend | State injection middleware (facts, move, feedback, upload manifest) | `backend/middleware/state_injection.py::BeforeModelStateInjection` | works — `test_middleware.py::test_composition_happens_once_per_turn_not_per_model_call` | R1 | keep |
| B51 | backend | Skills middleware (catalogue, per-field script, `load_skill`, example refusal) | `backend/middleware/skills.py::DMAICSkillsMiddleware` | works — `test_coaching_script.py`, `test_middleware.py` | R2, T61 | keep |
| B52 | backend | Summarisation middleware | `nodes_common.py::_build_executor` | works — `test_middleware.py::test_the_ratified_summarization_settings` | T49 | keep |
| B53 | backend | Model retry middleware | `_build_executor` (`ModelRetryMiddleware`) | works — `test_middleware.py::test_position_1_wrap_encloses_position_4_retry` | T46 | keep |
| B54 | backend | Tool retry middleware | `_build_executor` (`ToolRetryMiddleware`) | works — `test_middleware.py::test_on_failure_continue_is_current_not_merely_accepted` | T46 | keep |
| B55 | backend | Contradiction detection | `backend/middleware/contradiction.py::ContradictionDetectionMiddleware` | partial — detects, never interrupts ("guarded until 7.3") | T55 | fix — with the re-approval requirement (Q05) |
| B56 | backend | Coherence check (layer 2a) | `backend/middleware/coherence.py::CoherenceMiddleware` | partial — logs rejections; never re-asks (`test_row_12` is a strict expected failure) | T44 | fix |
| B57 | backend | Coaching-quality grader | `backend/middleware/grader.py::DMAICGraderMiddleware` | works — `test_row_13` (live), `test_judges_once.py` | T44, T64 | keep |
| B58 | backend | Middleware execution order | `_build_executor` middleware list | works — `test_middleware_execution_order.py` | T46 | keep |
| B59 | backend | Methodology lookup (multi-query, fusion, phase filter) | `backend/knowledge/tools.py::rag_lookup_methodology` | works — `test_fusion.py`, `test_turn_budget.py` | T25, T51, T58 | keep |
| B60 | backend | Evidence lookup filtered to the case | `tools.py::rag_lookup_evidence` | works — `test_evidence_index.py` | T53 | keep |
| B61 | backend | Past-case lookup | `tools.py::rag_lookup_case_history` | unknown — nothing writes the case index (Z07) | none (Q48) | fix — or unbind until cases are published |
| B62 | backend | Fill a template | `tools.py::propose_template` | unknown — bound; no output test | none | keep — add a test |
| B63 | backend | Propose a diagram (SIPOC, 5W2H) | `tools.py::propose_diagram`, `backend/core/diagrams.py` | works — `test_executor.py::test_a_proposed_diagram_rides_on_the_reply_for_the_ui` | R2 | keep |
| B64 | backend | Load one numeric column from an upload | `tools.py::load_evidence_series` | works — `test_executor.py::test_load_evidence_series_is_bound_on_every_phase` | M1, T60 | keep |
| B65 | backend | Cross-agent searches (Agent Resolve cases, knowledge, evidence) | `tools.py::search_resolve_*` | unknown — present, not bound, no test | none | drop — until cross-agent use is a requirement |
| B66 | backend | Agent Flow value-stream search | `tools.py::search_flow_vsm` | broken — a stub, unbound | none | drop |
| B67 | backend | Expected savings (Define) | `backend/knowledge/computation.py::calculate_expected_savings` | works — `test_computation.py::test_expected_savings_known_answer` | R4 | keep |
| B68 | backend | Sigma level (Measure) | `computation.py::calculate_sigma_level` | works — `test_computation.py::test_sigma_level_known_answers` | none | keep |
| B69 | backend | Cpk (Measure) | `computation.py::calculate_cpk` | works — `test_computation.py::test_cpk_known_answer_centred_process` | T57 | keep — add the stability precondition |
| B70 | backend | DPMO (Measure) | `computation.py::calculate_dpmo` | works — `test_computation.py::test_dpmo_known_answer` | none | keep |
| B71 | backend | Rolled throughput yield (Measure) | `computation.py::calculate_yield_rty` | works — `test_computation.py::test_rty_known_answer_and_the_hidden_factory` | none | keep |
| B72 | backend | First-time quality (Measure) | `computation.py::calculate_ftq` | works — `test_computation.py::test_ftq_known_answer` | none | keep |
| B73 | backend | Gauge R&R, attribute agreement (Measure) | `computation.py::calculate_grr` | works — `test_computation.py::test_grr_perfect_measurement_system_scores_zero` | none | keep |
| B74 | backend | Sample size for a proportion (Measure) | `computation.py::calculate_sample_size_proportion` | works — `test_computation.py::test_sample_size_proportion_known_answer` | none | keep |
| B75 | backend | Sample size for a mean (Measure) | `computation.py::calculate_sample_size_mean` | works — `test_computation.py::test_sample_size_mean_known_answer` | none | keep |
| B76 | backend | t-test (Analyse) | `computation.py::t_test` | works — `test_computation.py::test_t_test_known_answer_welch_by_default` | none | keep |
| B77 | backend | Chi-square (Analyse) | `computation.py::chi_square_test` | works — `test_computation.py::test_chi_square_known_answer` | none | keep |
| B78 | backend | ANOVA (Analyse) | `computation.py::anova` | works — `test_computation.py::test_anova_known_answer` | none | keep |
| B79 | backend | Pearson correlation (Analyse) | `computation.py::pearson_correlation` | works — `test_computation.py::test_pearson_known_answer_perfect_correlation` | none | keep |
| B80 | backend | Linear regression (Analyse) | `computation.py::linear_regression` | works — `test_computation.py::test_linear_regression_known_answer` | none | keep |
| B81 | backend | DOE main effects (Improve) | `computation.py::calculate_doe_main_effects` | works — `test_computation.py::test_doe_main_effects_known_answer` | none | keep |
| B82 | backend | X-bar/R limits (Control) | `computation.py::xbar_r_chart_limits` | works — `test_computation.py::test_xbar_r_known_answer` | none | keep |
| B83 | backend | I-MR limits (Control) | `computation.py::imr_chart_limits` | works — `test_computation.py::test_imr_known_answer` | none | keep |
| B84 | backend | p-chart limits (Control) | `computation.py::p_chart_limits` | works — `test_computation.py::test_p_chart_known_answer_and_varying_limits` | none | keep |
| B85 | backend | c-chart limits (Control) | `computation.py::c_chart_limits` | works — `test_computation.py::test_c_chart_known_answer` | none | keep |
| B86 | backend | Post-improvement Cpk and delta (Control) | `computation.py::post_improvement_cpk` | works — `test_computation.py::test_post_improvement_cpk_known_answer_and_delta` | none | keep |
| B87 | backend | Tool binding per phase under the ceiling | `computation.py::COMPUTATION_TOOLS_BY_PHASE`; `tools.py::UNIVERSAL_TOOLS` | works — `test_computation.py::test_the_live_per_phase_totals_while_two_tools_are_owed` | T52 | keep — two universal tools still owed |
| B88 | backend | Unparseable input gets a reformatting ask | `computation.py::_NeedsReformatting` | works — `test_computation.py::test_no_tool_raises_on_unparseable_input` | T31 | keep |
| B89 | backend | Tool argument schemas | `backend/knowledge/tool_args.py` | works — `test_computation.py::test_every_tool_has_its_own_args_schema` | none | keep |
| B90 | backend | Phase skill files and allowed-tool lists | `skills/dmaic-*-phase/SKILL.md`; `skills.py::allowed_tools` | works for Define — `test_define_skill.py`; partial for others (list two unbuilt tools) | R2, R7, T61 | keep |
| B91 | backend | Supervisor state | `backend/core/state.py::SupervisorState` | works — `test_state.py::test_supervisor_state_has_exactly_seven_fields` | T1 | keep |
| B92 | backend | v1 graph state | `state.py::ImproveGraphState` | partial — legacy, kept for the bridge | none | drop — at the v1 removal |
| B93 | backend | Phase state with the change-log upsert | `backend/core/substate.py::PhaseState`, `merge_field_log` | works — `test_state.py::test_the_field_log_reducer_is_the_upsert_and_not_operator_add` | T2, T18 | keep |
| B94 | backend | Planner judgment and coaching plan schemas | `substate.py::SufficiencyJudgment`, `CoachingPlan` | works — `test_validation_layer.py::test_only_insufficient_carries_a_criterion` | R3 | keep |
| B95 | backend | Coach output schema (blocks, captures, flag, citations) | `substate.py::CoachingResponse` | works — `test_contract_shape.py` | R2 | keep |
| B96 | backend | Capture helpers and value history | `substate.py::is_empty_capture`, `value_history` | works — `test_capture_accumulates.py::test_r6_the_first_and_the_current_confirmed_value_each_with_its_date` | R6 | keep |
| B97 | backend | Define gate document | `backend/phases/define/schema.py::DefineOutput` | works — `test_define_phase_metrics.py::test_a_complete_define_case_assembles` | R4, R5 | keep |
| B98 | backend | Measure to Control gate documents | `backend/phases/{measure,analyse,improve,control}/schema.py::*Output` | works in unit tests only — `test_gate_documents.py` (parametrised) | none | keep — review against their requirements |
| B99 | backend | v1 phase input schemas | `measure/schema.py::MeasurePhaseInput` and others | unknown — used only by dead code | none | drop |
| B100 | backend | API request and response models | `backend/gateway/schemas.py` | works — through the route tests | T16 | keep |
| B101 | backend | Models of the untested routes (health, summarise, context, upload meta) | `gateway/schemas.py::HealthResponse`, `SummariseRequest`, `ContextRequest`, `UploadMetaRequest` | unknown | none | keep or drop with their routes |
| B102 | backend | Validation verdicts (coherence, grader, rubric) | `backend/validation/schemas.py` | works — `test_coherence_script_step.py`, `test_define_rubric.py` | R7, T44 | keep |
| B103 | backend | Citation records | `backend/core/citations.py::CitationRecord`, `CitationBundle` | partial — `CitationBundle` unused | none (Q36) | fix — drop the unused bundle |
| B104 | backend | Query variants schema | `backend/knowledge/fusion.py::QueryVariants` | works — `test_fusion.py` | T51 | keep |
| B105 | backend | Case storage models | `backend/storage/models.py::CaseDocument`, `PhaseRecord`, `UploadRecord`, `RegistryEntry` | works — `test_uploads.py`, `test_gate_write.py` | none | keep |
| B106 | backend | Unused storage models | `models.py::ChartRecord`, `TeamMemberRecord`, `AnalystOutputRecord` | unknown — no user | none | drop |
| B107 | backend | Checkpoints with ETag concurrency | `backend/core/checkpointer.py::AzureBlobCheckpointSaver` | works — `test_checkpointer.py`, `test_row_33` (live) | T8, T9 | keep |
| B108 | backend | Pending writes for pause and resume | `checkpointer.py::put_writes` | works — `test_gate_acceptance.py::test_pending_writes_round_trip_and_the_special_channels_overwrite` | T15 | keep |
| B109 | backend | Checkpoint listing | `checkpointer.py::list`, `alist` | unknown — no test | T17 | keep — add a test |
| B110 | backend | Store case record | `backend/core/store.py::AzureBlobStore`; `mappers_common.py::write_case_record` | works — `test_store.py` | T19 | keep |
| B111 | backend | Store gate document | `mappers_common.py::write_gate_document` | broken — never written at runtime (B39) | T23 | fix |
| B112 | backend | Store semantic search refused by design | `store.py::_reject_semantic_query` | works — `test_store.py::test_semantic_query_is_rejected_and_names_the_other_mechanism` | none | keep |
| B113 | backend | Case blob (the system of record) | `backend/storage/blob.py::create_case`, `save_case`, `load_case` | works — `test_row_1`, `test_row_5` (live) | T13 | keep |
| B114 | backend | Gate write into the phase record, stamped once | `blob.py::write_phase_gate` | works — `test_gate_write.py` | T20 | keep |
| B115 | backend | Registry blob | `blob.py::register_case`, `_update_registry_entry` | works — `test_gate_write.py::test_the_registry_is_updated_in_place_not_appended` | none | keep |
| B116 | backend | Upload bytes to Blob | `blob.py::upload_file`, `download_bytes` | works — `test_row_8` (live); never deleted | none (Q60) | keep — deletion to add |
| B117 | backend | Append a turn to the case | `blob.py::append_turn` | broken — dead code | none | drop |
| B118 | backend | Dated change log with prior values | `substate.py::merge_field_log`; `routes.py::apply_capture` | works — `test_row_6` (live) | R6, T18 | keep |
| B119 | backend | Conversation history with blocks and visuals | `backend/core/conversation.py` | works — `test_coaching_blocks.py::test_a_history_turn_round_trips_the_blocks` | W3 | keep |
| B120 | backend | `step_log` audit entries | `nodes_common.py::_step` | works — `test_coaching_script.py::test_step_log_records_that_the_script_was_delivered` | T44 | keep |
| B121 | backend | Evidence index documents with versioning | `routes.py::_index_upload`; `scripts/backfill_evidence_index.py::mark_superseded` | works — `test_evidence_index.py` (the sweep is a script) | T22, T59 | keep |
| B122 | backend | Knowledge and case index population scripts | `scripts/ingest_knowledge.py`, `scripts/create_indexes.py` | unknown — no test | T22 | fix — ids on add (T22) |
| B123 | backend | Upload asks and versions (digest, role, shape) | `backend/upload/asks.py` | works — `test_uploads.py::test_the_digest_is_version_identity`; two helpers untested | M1, W5 | keep |
| B124 | backend | Structured logs with request, case and phase | `backend/core/logging_setup.py`, `backend/core/request_context.py` | unknown — no test | T43 | keep — add the test |
| B125 | backend | LangSmith traces per Define turn | `backend/core/tracing.py::init_tracing`, `child_span` | works — `test_row_35` (live), `test_no_tracing.py` | T39, T40 | keep |
| B126 | backend | Knowledge search with typed errors | `backend/knowledge/retriever.py::search_knowledge` | works — `test_retriever.py` | T30 | keep |
| B127 | backend | Case-history search | `retriever.py::search_cases` | works in unit tests | none | keep |
| B128 | backend | Evidence search with case filter | `retriever.py::search_evidence` | works — `test_evidence_index.py::test_the_case_filter_survives_an_odata_quote_in_either_argument` | T53 | keep |
| B129 | backend | Knowledge context block builder | `retriever.py::build_knowledge_context` | partial — tested, no production caller | none | drop |
| B130 | backend | Evidence vector store | `retriever.py::get_evidence_vectorstore` | unknown — called by nothing but warm-up | none | drop |
| B131 | backend | Client caching, single-flight, warm-up, embeddings | `retriever.py::get_search_client`, `warm_clients`, `get_embeddings` | works — `test_client_warmup.py` | T25 | keep |
| B132 | backend | Retrieval error classification | `backend/core/errors.py::AgentImproveError` | works — `test_retriever.py::test_status_codes_classify_as_ratified` | T30 | keep |
| B133 | backend | Error to `step_log` entry | `errors.py::AgentImproveError.to_step_log_entry` | unknown — no test | T44 | keep — add a test |
| B134 | backend | Reciprocal rank fusion and query variants | `fusion.py::reciprocal_rank_fusion`, `generate_variants`, `run_multi_query` | works — `test_fusion.py` | T51 | keep |
| B135 | backend | Define gate rubric (layer 2d) | `backend/validation/rubric.py::grade_define` | works — `test_define_rubric.py` | R7, T63 | keep |
| B136 | backend | Single-authority metric check | `backend/core/metrics.py::check_single_authority` | works — `test_metric_single_authority.py` | T54 | keep |
| B137 | backend | Model factory: roles, tiers, temperatures, retry off, warm-up | `backend/core/llm.py::get_llm` | works — `test_llm.py`, `test_client_warmup.py` | T45 | keep |
| B138 | backend | Settings | `backend/core/config.py::Settings` | unknown — no direct test; Langfuse and intent settings unread | T67 | fix — drop dead settings; fail fast |
| B139 | backend | Prompts: coach, labelled sections, moves, judgment, rubrics, variants, upload | `backend/core/prompts.py` | works — `test_wiring.py::test_wired_6_61_the_coach_input_is_six_labelled_sections` | R1, R3, R7 | keep |
| B140 | backend | v1 prompts | `prompts.py::ORCHESTRATOR_*`, `EXTRACTION_*`, `ESCALATION_REPORT` | broken — dead code | none | drop |
| B141 | backend | Upload parsing (csv, xlsx, pdf, docx, text, refusal) | `backend/upload/parsers.py::parse_upload` | works — `test_uploads.py::test_an_unreadable_file_is_refused_with_a_belt_readable_reason` | M1, W5 | keep |
| B142 | backend | Upload classification (evidence or artefact) | `backend/upload/classifier.py` | works — `test_uploads.py` | W5 | keep |
| B143 | backend | Upload interpretation (one model call, labelled fallback) | `backend/upload/agent.py::process_upload` | works — `test_uploads.py::test_the_fallback_announces_itself_rather_than_reading_as_a_summary` | W5, M1 | keep |
| B144 | backend | Image upload reading (vision) | `upload/agent.py::_extract_from_image` | unknown — no test | R10 (draft) | keep — add a test |
| B145 | backend | Escalation after three failed gate attempts | `config.py::Settings.GATE_MAX_ATTEMPTS`; `validation_stack` | broken — a flag only (`test_supervisor_graph.py::test_nothing_reaches_escalation_yet`) | T65 | fix |
| B146 | backend | Measure to Control end to end | the phase nodes, mappers, validators and schemas | partial — generic walk only; no report, pause or rubric; entry fails (B38) | M1 | rebuild — per phase, after its requirements |

## 3. Azure and other services

| Id | Area | Capability | Evidence | State | Covered by | Reuse |
|---|---|---|---|---|---|---|
| Z01 | Azure | Azure OpenAI premium chat deployment (coach, planner, synthesis, vision) | `backend/core/llm.py::ROLE_DEPLOYMENTS`; env `AZURE_OPENAI_PREMIUM_DEPLOYMENT`, endpoint and key from env | works — `test_llm.py`; live rows 3, 13, 35 passed | T45 | keep |
| Z02 | Azure | Azure OpenAI operational deployment (reasoning, extraction, graders, summariser, intent) | `llm.py`; env `AZURE_OPENAI_OPERATIONAL_DEPLOYMENT` | works — same evidence | T45 | keep |
| Z03 | Azure | Azure OpenAI intent deployment setting | `backend/core/config.py`; env `AZURE_OPENAI_INTENT_DEPLOYMENT` | broken — nothing reads it | none | drop |
| Z04 | Azure | Azure OpenAI embeddings | `backend/knowledge/retriever.py::get_embeddings`; env `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | works — `test_retriever.py`; live row 8 | T53 | keep |
| Z05 | Azure | AI Search: methodology knowledge index | `retriever.py::get_knowledge_vectorstore`; `scripts/create_indexes.py`; env `AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX` | partial — works through `.env`; the default name in `config.py` is the old, contaminated index | T58 | fix — make the default the current index, or fail when unset |
| Z06 | Azure | AI Search: evidence index | `routes.py::_index_upload`; `retriever.py`; env `AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX` (missing from `.env.example`) | works — `test_evidence_index.py`; live row 8 | T53, T59 | keep — add the variable to `.env.example` |
| Z07 | Azure | AI Search: case index (cross-case memory) | `retriever.py`; `create_indexes.py`; env `AZURE_SEARCH_IMPROVE_CASE_INDEX` | partial — read path only; nothing writes it (§23.3: 0 documents) | none (Q48, Q50) | fix — publish closed cases, or drop the lookup |
| Z08 | Azure | AI Search: Agent Resolve indexes (read only) | `backend/knowledge/tools.py::search_resolve_*`; env `AZURE_SEARCH_RESOLVE_*` | unknown — unbound, no test | none | drop — until cross-agent use is required |
| Z09 | Azure | Blob container: checkpoints | `backend/core/checkpointer.py::get_checkpointer`; env `AZURE_BLOB_CONNECTION_STRING`, `AZURE_BLOB_CONTAINER_IMPROVE` | works — `test_checkpointer.py`; live row 33 | T7–T9 | keep |
| Z10 | Azure | Blob container: Store | `backend/core/store.py::get_store`; same env | works — `test_store.py`; live rows 5, 6 | T19 | keep |
| Z11 | Azure | Blob container: case records, registry, uploads | `backend/storage/blob.py`; same env | works — `test_blob.py`, `test_gate_write.py`; live rows 1, 8 | T13 | keep |
| Z12 | Azure | Hosting | `start.ps1` (local uvicorn on port 8020); `backend/app.py` serves `ui/` | broken — no cloud hosting for Improve; local only | none | rebuild — a hosting decision is needed |
| Z13 | Azure | Secrets | `.env` files (git-ignored), `.env.example` placeholders | partial — plain env vars; no Key Vault; no committed secret found; some keys declared twice in the local `.env` | T67 | fix — Key Vault at hosting |
| Z14 | Azure | Identity | `azure-identity` pinned in `requirements.txt`, unused | broken — keys and connection strings only; no managed identity | R8, T12 | rebuild — with hosting and R8 |
| Z15 | other | LangSmith tracing | `backend/core/tracing.py::init_tracing`; env `LANGCHAIN_API_KEY` (or `LANGSMITH_API_KEY`), `LANGCHAIN_PROJECT`, `ENVIRONMENT` | works — live row 35; `test_no_tracing.py` | T39–T41 | keep |
| Z16 | other | Langfuse settings | `config.py::Settings.LANGFUSE_*`; `langfuse` pinned | broken — nothing imports it | none | drop |
| Z17 | other | jsDelivr CDN: icon font for the UI | `ui/index.html` (`@tabler/icons-webfont@latest`) | unknown — works in use, unpinned, no test | none | fix — pin the version |

**Named in ARCHITECTURE.md but absent (not inventoried as capabilities):** Azure Cache for Redis
(fallback level 3), Azure Database for PostgreSQL (the production saver and store), a second EU
region, the `check_gate_status` and `request_human_approval` tools, validation layer 2c, gate
rubrics for Measure to Control, and the `/ask/stream` route.

## 4. Requirement-like statements not yet in docs/requirements/

From [ARCHITECTURE.md](../../ARCHITECTURE.md) and the archived procedure and decisions
(`docs/_archive/REFACTORING_PROCEDURE.md`, `DECISIONS.md`, `REVIEW_DECISIONS.md`; "App H" = the
procedure's capability rows). Paraphrased. **Owner** is a proposal: R new, T new, W new, M new, an
amendment, or drop.

| Id | Statement | Source | Closest id | Owner |
|---|---|---|---|---|
| Q01 | Five phases in fixed order, no skipping or reordering | §39, §15 | none | R new |
| Q02 | Every phase ends at a gate the Belt approves, not only Define | §1, §33, §39.2.6–§39.5.6 | R6 (Define) | R new |
| Q03 | Each later phase opens on the previous phase's approved record | §39.x.11; App H row 24 | none | R new |
| Q04 | Gates are one-way: the only way back is the re-approval cascade | §33 | none | R new |
| Q05 | Contradicting an approved value stops coaching and shows both values, the approving phase and date, and two choices | §37, §50 | T55 (mechanism) | R new |
| Q06 | No tolerance threshold: any material change to an approved value is a mini-gate | §37; DECISIONS G7 | none | fold into Q05 |
| Q07 | "Update" makes that phase and every later phase provisional, each needing re-review | §37; procedure 7.6 | none | R new |
| Q08 | The conflict panel shows which phases become provisional before the Belt confirms | §50; procedure 10.2 | none | W new |
| Q09 | The cascade removes stale published values | §37; procedure 7.6 | T29 (partial) | T new |
| Q10 | A superseding upload triggers the same cascade | procedure 7.6; DECISIONS AP3 | none | fold into Q07 |
| Q11 | Changing a not-yet-approved value is ordinary coaching, kept as history | §37 | R6 | R6 (clarify) |
| Q12 | The Belt's reason for a change is recorded with it | §6; App H row 7; procedure 6.44 | R6 | R6 (amend) |
| Q13 | An "all gate fields" view of every phase, the backstop for missed contradictions | §50; §68 | W2 (partial) | W new |
| Q14 | After three failed gate attempts the system escalates, naming the unresolved criteria | §38, §34.2, §58.17 | T65 | R new |
| Q15 | The coach can hand a decision beyond its remit to a human | §38, §60.4 | none | R new |
| Q16 | Gate feedback is per criterion and accumulates across the attempts | §34, §36 | T63, R3 | T new |
| Q17 | In Measure to Control a gate may pass with a recorded, acknowledged Tier 2 gap | §35 | T66 | R new |
| Q18 | Issues and barriers are required in every phase; "none" must be a conscious answer | §35, §39.x.2 | R5 item 7 | R new |
| Q19 | Every captured field is editable on the gate review screen before approval | §33, §50, §58.15, §68 | R6 | R6 (amend) |
| Q20 | A non-blocking second opinion checks the Belt's gate edits | §33, §62.10 | none | R new |
| Q21 | A reply the grader cannot fix in three tries goes through with a visible warning | §36; procedure 10.0 | none | R new |
| Q22 | Only coherence retries are silent; every other correction is visible | §34.2 | none | R new |
| Q23 | Weak proposals are coached without a retry cap; weak answers are never accepted because retries ran out | §34.2 | R3 (Define) | R new |
| Q24 | Coaching adapts to belt level (for example DOE for Black Belts) | §35, §39.4.6; DECISIONS AG6 | none | R new |
| Q25 | Coaching rules in every phase: no vague answers accepted, no invented data, never do the Belt's work | §36, §43.6 | R1, R3 | R new (all phases) |
| Q26 | The seven-step calculation pattern, never raw statistics | §43.1; App H row 26 | none | R new |
| Q27 | Metric literacy: what a metric is, why now, how to read it | §43.7, §39.x.8; App H row 32 | R2 (partial) | R new |
| Q28 | The coach never gives external URLs | §43.5; App H row 30 | none | R new |
| Q29 | Every turn shows "Step n of N", computed by the system | §43.3; procedure 6.57; App H row 28 | W2 | W new |
| Q30 | The phase report fills in live while coaching | §43.4, §50; App H row 29 | W2, R5 | W new |
| Q31 | Separate bars for required and recommended items | §50, §39.x.9 | none | W new |
| Q32 | Each phase report shows calculations inline with interpretation and charts | §50, §39.x.9 | none | R new |
| Q33 | The report is built only from committed values and calculations | §50 | R5 (partial) | T new |
| Q34 | Every approved phase document carries its citations, uploads, calculations and gaps | §33.2, §6, §65.4 | none | R new |
| Q35 | The audit trail is a product requirement: how a conclusion was reached | §1 | none | R new |
| Q36 | Citations show the source file and page | §50, §65.1 | none | R new |
| Q37 | Cross-agent suggestions carry a visible citation | §50, §29.4 | none | drop (cross-agent unbound) |
| Q38 | Coach replies are structured blocks, never a wall of prose | §50.1; procedure 10.0; App H row 15 | R2 (partial) | W new |
| Q39 | The worked example is marked as illustration and never captured | §50.1, §22, §43.2; procedure 6.46 | T6 (partial) | T new |
| Q40 | No methodology jargon in team-facing text | §50 | none | R new |
| Q41 | Every data request includes a concrete example with column names, in every phase | §50, §29.1 | M1 | R new (all phases) |
| Q42 | Loading messages say what is happening | §50 | none | W new |
| Q43 | The Belt sees system and connection health before the first message | §50 | none | W new |
| Q44 | The trace id is shown so a Belt can report a bad turn | §50, §67.3 | none | W new |
| Q45 | On mobile: shorter sections, larger tap targets | §50.1 | none | W new |
| Q46 | Source order: method, then approved facts, then past cases, then recent chat | §22 | none | R new |
| Q47 | The knowledge base is the BB eBook only; no other framework in DMAIC coaching | DECISIONS V1 | none | R new |
| Q48 | Past cases are searchable as precedent | §23.3, §24 | none | R new |
| Q49 | Shared case data is filtered by tenant before any multi-organisation use | App B item 1, §65.5, §68.3; REVIEW_DECISIONS | R8 | R8 (amend) |
| Q50 | Control's lessons learned feed the cross-case memory | §39.5.2, §65.5 | none | R new |
| Q51 | Uploads are the only external data channel; no number the Belt did not provide | §29.1, App D.3 | none | R new (constraint) |
| Q52 | Every phase coaches what data to upload and its shape | §29.1; procedure 6.14 | M1 | R new (per phase) |
| Q53 | An upload is tied to its request; a shape mismatch becomes a coaching question | DECISIONS AP2, AS6; procedure 6.12 | M1 (partial) | M new |
| Q54 | A re-upload is a new version; superseded versions leave retrieval but history is kept | DECISIONS AP2; §23.2 | none | T new |
| Q55 | As-is evidence and to-be designs are kept apart | DECISIONS AP2; §23.2.1; procedure 6.13 | none | T new |
| Q56 | An unreadable file is refused with a readable reason | DECISIONS AP2; procedure 6.11 | none | R new |
| Q57 | xlsx, csv, pdf and docx are parsed deterministically | procedure 6.11 | M1, R10 (open) | M1 / R10 (answers the open question) |
| Q58 | A figure computed from an upload cites the file | DECISIONS AP2 | M1 | M1 (all phases) |
| Q59 | The coach knows which files were uploaded and can read them | DECISIONS AS3; procedure 6.43; App H row 9 | W5 | W5 (covered) |
| Q60 | Deleting an upload removes the stored file too | procedure 8.7; DECISIONS Part Y | none | R new |
| Q61 | A failed turn reaches the Belt as a readable condition that stays on screen | procedure 10.4; App H row 16 | T32 | T new |
| Q62 | The Belt can leave mid-phase and return weeks later with nothing lost | §1 | T15, W3 | R new |
| Q63 | A case can be created and opened from a case list | App H row 1; §49 | none | W new |
| Q64 | A registry lists cases with phase, status, leader, department, days in phase, target date | §23.3, §49, §65.5 | W2 (partial) | W new |
| Q65 | The dashboard never shows a phase the case record does not | DECISIONS Part Y | none | T new |
| Q66 | Approving Control closes the project with its final record | §39.5.6, §39.5.9 | none | R new |
| Q67 | Each metric is traceable from Define to Control with baseline, target, actual and delta | §39, §39.5.3, §39.5.12 | none | R new |
| Q68 | Baseline and target are stored as a number with a unit; unparseable is asked again | procedure 6.51; App H row 25 | R7 | R7 (amend) / T new |
| Q69 | Structured answers are stored in their structure, never as prose | procedure 6.48; App H row 18 | none | T new |
| Q70 | Planned target date and actual close date are both recorded and compared | §39.1.2, §39.5.2 | none | R new (Control) |
| Q71 | Control verifies realised savings against Define's estimate | §39.5.2, §39.5.11 | R4 | R new (Control) |
| Q72 | Close sign-off by Champion, Belt and Finance | §39.5.2 | R8 | R new |
| Q73 | Champion approval at the Define gate — conflicts with R8's "the Belt approves until R8" | §39.1.4 | R6, R8 | R8 (a ruling) |
| Q74 | Measure: measurement system before baseline; stability before capability | §39.2.6, §41 | T57 | M new |
| Q75 | Measure deliverables: detailed map, data plan, MSA, stability, baseline, vital few | §39.2.1–§39.2.4 | M1 | M new |
| Q76 | Analyse: causes validated with data; correlation is not causation; practical significance | §39.3 | none | R new (Analyse) |
| Q77 | Improve: the solution traces to the root cause; pilot before rollout; state the experiment choice | §39.4, §41 | none | R new (Improve) |
| Q78 | Control: five control sub-plans, an owner who accepted, stability rechecked | §39.5, §41 | none | R new (Control) |
| Q79 | FMEA is never required or tracked | §41, App D.3 | none | R new (exclusion) |
| Q80 | The same situation always gives the same coaching move | §43; procedure 6.61 | none (ADR 0001) | T new |
| Q81 | Whether a turn was coached with its script is recorded | procedure 6.46; App H row 3 | none | T new |
| Q82 | Storage misconfiguration fails loudly | procedure 6.47 | T67 | T new |
| Q83 | Replies stream token by token | §49; procedure 10.1 | T24 | T new (or drop) |
| Q84 | The Belt is told they are working with an AI coach (EU AI Act) | §67.3, §67.1 | none (ADR 0055) | R new |
| Q85 | A legal determination on high-risk status before December 2027 | §67.2, §68.2 | none | R new (operator) |
| Q86 | A DORA-structured risk register, every claim sourced and dated | §68, §67.5 | none (ADR 0056) | R new or drop |
| Q87 | Production launch requires the Postgres saver and store | App B item 13 | T68 | T new |
| Q88 | No export: the phase report on screen is the record (a founder ruling) | DECISIONS AG5 | none | R new (rule again first) |
| Q89 | Per-Belt adaptive coaching delivery, never changing gate criteria (deferred) | §28, App B item 5 | none | R new (deferred) |
| Q90 | A customer's own methodology beside the eBook (deferred) | App B item 15 | none | R new (deferred) |
| Q91 | An adversarial debate to stress-test root causes (deferred) | App B items 10–11; DECISIONS N2 | none | drop, or keep deferred |
| Q92 | UI language choice | not stated anywhere | W1 (open) | W (open question) |
| Q93 | Notifications for pending approvals and escalations | not stated anywhere | none | founder to decide |
| Q94 | Case deletion and retention policy | not stated (only T17, procedure 8.7) | T17 | founder to decide |
