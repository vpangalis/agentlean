# Architecture sort — PROPOSAL (founder, 2026-09-26)

> **PROPOSED — nothing here is ratified, and [ARCHITECTURE.md](../ARCHITECTURE.md) is unchanged.**
> Its output: the technical requirements T1–T68 in
> [platform.md](requirements/platform.md#technical-requirements-proposed), the decision records in
> [docs/adr](adr/README.md), and this file (the map, the drift, and the completeness check).
> DESIGN stays in ARCHITECTURE.md (founder, 2026-09-26).

Classes: **T** a measurable technical requirement → platform.md · **ADR** a decision → docs/adr ·
**DESIGN** stays in ARCHITECTURE.md · **DOMAIN** method content → skills · **STATUS** build
state → tests and features · **OBSOLETE** superseded or a pointer to an archived document.

## 1. The map

| Section | Class | Why |
|---|---|---|
| Where state lives (map) | DESIGN | Orientation diagram of where each piece of state lives |
| About this document | OBSOLETE | Rules for the single-document model; the three layers in CLAUDE.md replace them |
| §1 What Agent Improve is | DESIGN | Product overview |
| §2 How to read this document | OBSOLETE | Reading guide; `docs/section-index.md` replaces it |
| §3 Terminology | DESIGN | Glossary |
| §4 Architecture at a glance | DESIGN | Overview diagram (its field count has drifted — see §2 below) |
| §5 `SupervisorState` | ADR + T | [0015](adr/0015-two-level-state.md); T1, T3 |
| §6 `PhaseState` | ADR + T | 0015; T2, T4, T10 |
| §7 Field typing law | ADR | [0016](adr/0016-captured-fields-are-strings.md); T5 |
| §8 Checkpointer / store split | ADR + T | [0017](adr/0017-checkpointer-on-the-parent-only.md); T7, T17 |
| §9 The Store | ADR + T | [0019](adr/0019-store-for-cross-phase-artifacts.md); T19 |
| §10 Azure Blob | ADR + T | [0018](adr/0018-azure-blob-checkpointer.md); T9, T11, T13 |
| §11 `step_log` | T | T18, T21, T44; [0020](adr/0020-step-log-audit-trail.md) |
| §12 Topology | DESIGN | Graph shape; [0021](adr/0021-one-compiled-graph.md) |
| §13 The phase subgraph | DESIGN | The five nodes; [0022](adr/0022-five-node-phase-cycle.md) |
| §14 Node contract | T | Return and async contract of every node |
| §15 Routing | ADR | [0023](adr/0023-routing-static-or-command.md) |
| §16 `thread_id`, `checkpoint_ns` | ADR + T | [0024](adr/0024-thread-id-is-the-case.md); T8, T12 |
| §17 Planner / Executor | ADR + STATUS | [0001](adr/0001-coaching-move-decided-in-code.md), [0025](adr/0025-planner-executor-split.md); T47; long build-status notes |
| §18 `create_agent` | ADR | [0026](adr/0026-create-agent-with-middleware.md) |
| §19 Middleware stack | ADR + T | [0027](adr/0027-middleware-stack.md); T46, T49, T55 |
| §20 `CoachingResponse` | ADR | [0028](adr/0028-coaching-response-schema.md), [0002](adr/0002-value-stored-only-after-confirmation.md); T6 |
| §21 LLM roles | T | T45; [0029](adr/0029-model-roles-and-tiers.md) |
| §22 Prompts | ADR | [0003](adr/0003-coach-input-in-labelled-sections.md) |
| §23 The three indexes | ADR + T | [0030](adr/0030-three-indexes.md); T22, T53 |
| §24 `rag_lookup_*` tools | T | T25, T58 |
| §25 Multi-query and RRF | ADR + T | [0031](adr/0031-multi-query-rrf.md); T51 |
| §26 Multi-hop | ADR + T | [0032](adr/0032-hop-cap-counted-in-executor.md); T26, T27 |
| §27 Retrieval failure | ADR + T | [0033](adr/0033-retrieval-failure-semantics.md); T30 |
| §28 Memory taxonomy | DESIGN | Conceptual map of memory kinds |
| §29 Data channel, universal tools | ADR | [0034](adr/0034-no-mcp-data-channel.md) |
| §30 Computation tools | ADR + T | [0035](adr/0035-computation-tools-per-phase.md); T31, T52 |
| §31 Tool arg schemas | T | Argument and docstring rules |
| §32 SKILL.md | ADR + T | [0036](adr/0036-phase-skills.md); T61 |
| §33 The HITL gate | ADR + T | [0008](adr/0008-define-gate-is-a-report.md), [0037](adr/0037-gate-review-and-apply.md), [0038](adr/0038-checkpoint-commits-after-approval.md); T14–T16, T20, T23 |
| §34 Four-layer validation | ADR + T | [0039](adr/0039-four-layer-validation.md), [0010](adr/0010-define-rubric-layer-2d.md); T48, T56, T63 |
| §35 Two tiers and `warning` | ADR + T | [0040](adr/0040-two-tiers-and-warning.md); T66 |
| §36 Two graders | ADR + T | [0041](adr/0041-two-graders.md); T64 |
| §37 Contradiction cascade | ADR | [0042](adr/0042-contradiction-and-reapproval.md) |
| §38 Escalation | ADR + T | 0039; T65 |
| §39 The five phases | DOMAIN | Method content → skills. OBSOLETE: 39.1.7, 39.2.10, 39.3.10, 39.4.10, 39.5.10 (defer to the files). T/ADR: 39.x.3, 39.1.9, 39.2.3. STATUS: 39.4.12, 39.5.12 |
| §40 Output schemas | T | Schemas are owned by code; the prose count is stale |
| §41 Structured dict fields, FMEA | DOMAIN + T | Dict shapes are T; the FMEA method goes to skills |
| §42 Cross-phase references | ADR | 0019 |
| §43 The coaching method | ADR + DOMAIN | The intro is 0001; the subsections are method → skills |
| §44 Failure pipeline | ADR + T | [0043](adr/0043-native-reliability-primitives.md); T38 |
| §45 Timeouts, compensation | ADR + T | 0043, [0011](adr/0011-gate-write-in-final-node.md); T24, T29, T32, T37 |
| §46 Fallback, breakers | ADR + T | [0044](adr/0044-fallback-chain-and-breakers.md), [0045](adr/0045-geo-redundancy-deferred.md); T34–T36, T68 |
| §47 Disconnect policy | ADR + T | [0046](adr/0046-disconnect-abandons.md); T33 |
| §48 Structured errors | ADR | [0047](adr/0047-one-error-schema.md); T30 |
| §49 API surface | T | T16; the route list is stale |
| §50 UI and language | DESIGN + ADR | Screen and wording rules |
| §51 Tracing | T | T28, T39–T43; [0048](adr/0048-tracing-is-a-switch.md) |
| §52 Evaluation | T | T50; [0049](adr/0049-eval-gates-release.md), [0014](adr/0014-live-call-budget.md) |
| §53 Configuration, deployment | T | T67; [0050](adr/0050-config-fails-fast.md). 53.1 is STATUS/OBSOLETE (a migration sequence) |
| §54 Where code lives | DESIGN | Module layout |
| §55 Anti-drift | OBSOLETE + ADR | Points to archived procedures. 55.2 and 55.3 are STATUS; 55.4 and 55.5 are [0051](adr/0051-facts-have-one-owner.md) and [0052](adr/0052-commit-gates-govern.md) |
| §56 Amendment procedure | OBSOLETE + ADR | 56 and 56.0 are OBSOLETE; 56.0.1, 56.1, 56.2 and 56.3 are ADRs ([0053](adr/0053-phase-is-atomic.md), [0054](adr/0054-head-is-truth.md)) |
| §57 How to write a spec entry | OBSOLETE | Features plus requirements replace the spec format |
| §58 Spec — graph management | T + STATUS | Behaviour clauses → T and features; BUILT markers → tests |
| §59 Spec — retrieval | T + STATUS | Same |
| §60 Spec — tools | T + STATUS | Same; T60 |
| §61 Spec — middleware | T + STATUS | Same |
| §62 Spec — validation and gates | T + STATUS | Same |
| §63 Spec — gate documents | T + DOMAIN | T62; per-phase content → skills |
| §64 Spec — reliability | T + STATUS | T11 |
| §65 Spec — API, UI, evidence | T + STATUS | T59 |
| §66 SPEC-GAP register | OBSOLETE | A pointer only |
| §67 EU AI Act posture | ADR | [0055](adr/0055-eu-ai-act-posture.md) |
| §68 DORA risk register | ADR + STATUS | [0056](adr/0056-dora-risk-register.md) |
| §69 Spec — computation tools | T + DOMAIN | T54, T57 |
| Appendix A — Provenance | OBSOLETE | Points to archived documents |
| Appendix B — Deferred backlog | STATUS | Belongs with features |
| Appendix C — Trusted sources | DESIGN | Reference list |
| Appendix D — Retired names, bans | ADR + T | Enforced by `deprecated_patterns.yaml` |
| Appendix E — Current state | OBSOLETE | Build state belongs with tests |
| Appendix F — v2.2.16 registers | OBSOLETE | Historical registers |

## 2. Drift found (ARCHITECTURE.md against the code, reported, not edited)

| Where | The document says | The code / tests say |
|---|---|---|
| §16, §26, Appendix B | a hop cap of five | `COACH_HOP_BUDGET` in `backend/phases/nodes_common.py` is three (`test_hop_cap.py::test_the_cap_is_three`); the name `test_executor.py::test_the_sixth_lookup_answers_instead_of_searching` still says five |
| §26 | the cap is `RemainingSteps` | the executor counts `rag_lookup_*` calls |
| §4 diagram | the phase state's field count | differs from the owner, `backend/core/substate.py` |
| §4, §29.2 | seven universal tools in one, eight in the other | the tests pin the set in `backend/knowledge/tools.py` |
| §8 | an in-memory saver is never used | `test_define_report`, `test_wiring` and `test_middleware` use one (true only of production) |
| §35, §39.1.2, §40 | Define's twelve fields | thirteen elements (R4); schema owned by `backend/phases/define/schema.py` |
| S-F10, S-F12 | two different Define field counts, and `artifacts={}` | the schema owner above |
| G-07, G-15 | open | tests exist that close them |
| S-F03 | the old SIPOC shape | changed at v1.77 |
| §30, §69 | computation tools return a string | they return a dict whose values are strings (`test_computation.py::test_every_result_value_is_a_string`) |
| Supersession sweep | keyed on `(case_id, role)` | keyed on `blob_path` |
| §11 | a replayed step leaves one `step_log` entry | `step_log` uses `operator.add`, so a replay appends (T21) |
| §19 | positions 4 and 5 are independent | since 6.3 position 1 wraps the model call and encloses the retry (`nodes_common.py`, comment in the executor's middleware list) |
| §33.2 | `gate_apply` writes the gate document | the route writes it after the graph returns (D22, [0011](adr/0011-gate-write-in-final-node.md)) |
| §49 | lists `/ask/stream` and `GET /cases` | neither exists; `/health`, `/summarise`, `/context`, `GET /gate/review/{case_id}/{phase}` and `DELETE /files/{case_id}/{file_id}` exist and are missing |
| §53.1, §55, §55.1, §55.2, §56, §57, §66, Appendix A | point to REFACTORING_PROCEDURE and DECISIONS as current | both are archived |
| Part IX / Part XII | §43.7 sits under the Part IX heading; §56.2 and §56.3 sit after Part XII | misplaced headings |

## 3. Completeness check — is each design area described AS BUILT? (founder, 2026-09-26)

**Across every area:** ARCHITECTURE.md carries **no** `path::symbol` reference (zero found), and no
link to an ADR or a T-requirement (both are new today). Paths appear only as file names
(`core/state.py`), and only in some sections. Every area below therefore needs its code
references and its ADR and T links added when ARCHITECTURE.md is next edited.

| Area | § | As built? | Code references today | ADR · T | What is missing or outdated |
|---|---|---|---|---|---|
| Main state and phase sub-states | §5, §6 | Yes, with drift | `core/state.py`, `core/substate.py` (files only) | 0015, 0016 · T1–T6, T10 | §4's field count; no `backend/core/state.py::SupervisorState`, `backend/core/substate.py::PhaseState` |
| Graph topology, node types | §12–§14 | Shape yes; location missing | `core/graph.py`, `escalate.py` | 0021–0023, 0025, 0037 · T3, T7 | The five nodes live in `backend/phases/nodes_common.py` (planner, executor, `validation_stack`, `gate_review`, `gate_apply`) — never named. The gate write is described in `gate_apply` but is in the route (D22) |
| Checkpointing, persistence | §8, §10, §16 | Partly | `core/checkpointer.py`, `storage/blob.py` (§10 only) | 0017–0020, 0024 · T7–T13, T18–T23 | §8 and §16 cite no code. Pending writes (`AzureBlobCheckpointSaver.put_writes`, built at part 6) mentioned once. The in-memory-saver sentence contradicts the tests |
| Interrupts (pause and resume) | §33 | Partly | none | 0008, 0009, 0037, 0038 · T14–T16 | `gate_review`'s `interrupt()`, `POST /gate/decision` and `_pending_interrupts` in `backend/gateway/routes.py` appear only in changelog notes (v1.83), not as the design. No code references |
| Middleware stack, in order | §19 | Order yes; reasoning outdated | none | 0026, 0027 · T46, T49, T55, T64 | The mount point `backend/phases/nodes_common.py` (the executor's `middleware=[...]`) is never cited; the independence of positions 4 and 5 no longer holds |
| Tools and retrieval | §23–§31 | Yes, with drift | `knowledge/tools.py`, `knowledge/retriever.py`, `knowledge/fusion.py`, `knowledge/computation.py` | 0030–0036 · T22, T25–T27, T30, T31, T51–T61 | Hop cap three against five; the universal tool count; the cap mechanism |
| API | §49 | Outdated | `gateway/routes.py`, `gateway/schemas.py` | 0009 · T16 | Route list wrong both ways (see drift) |
| UI | §50 | Missing | none | — · none | `ui/index.html` never cited; the Define report screen (`renderDefineReport`, `decideDefineReport`, part 5–6) absent |
| Tracing | §51 | Partly | `core/tracing.py`, `retriever.py`, `validate.py` | 0048 · T39–T44, T28 | Which functions are traced is not listed; production refusal described but not built |
| Error handling | §44–§48 | Described as target, not as built | `core/errors.py` | 0043–0047 · T29–T38 | No `error_handler=` and no circuit breaker exist in the code; the sections read as built. Must be marked NOT BUILT |
| Model roles and cost | §21 | Yes | `core/llm.py` | 0029, 0014 · T45–T50 | No `backend/core/llm.py::ROLE_DEPLOYMENTS` / `ROLE_TEMPERATURES` references; cost per role not stated |

**Described only as history:** §17 and §19.1 carry the design inside dated founder-ruling quotes
(v1.75, v1.77) rather than as the current description; §33's pause and §8's pending writes exist
only in changelog lines; §55–§57 describe a retired procedure.
