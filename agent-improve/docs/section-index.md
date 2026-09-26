# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 11661 lines

| Lines | Heading |
|---|---|
| 27–49 |  🗺 Where state lives — a MAP, not a definition |
| 50–252 | Agentic Architecture Reference |
| 147–252 |  About this document |
| 153–210 |   Scope — three agents, one architecture |
| 211–225 |   The two-document division |
| 226–240 |   Section numbering and provenance |
| 241–252 |   Reading conventions |
| 253–544 | Part I — Orientation |
| 257–333 |  1. What Agent Improve is |
| 277–303 |   What makes it architecturally distinctive |
| 304–333 |   The runtime stack |
| 334–385 |  2. How to read this document |
| 340–356 |   By what you are trying to do |
| 357–385 |   Canonical ownership |
| 386–484 |  3. Terminology |
| 397–413 |   Structural primitives |
| 414–425 |   Role labels |
| 426–443 |   The recursion is two levels, not infinite |
| 444–458 |   "Harness" — two senses, do not conflate |
| 459–469 |   "Agent" — used carefully |
| 470–484 |   Things that are deliberately not levels |
| 485–544 |  4. Architecture at a glance |
| 528–544 |   The five things that shape everything else |
| 545–1272 | Part II — State and Persistence |
| 552–610 |  5. `SupervisorState` — orchestration only |
| 564–570 |   `gate_passed` is a dict, not a list |
| 571–582 |   `current_phase` and `phase_index` are derived, and kept anyway |
| 583–602 |   Four fields were removed as redundant, and may not return |
| 603–610 |   Artifacts are not here |
| 611–846 |  6. `PhaseState` — per-phase subgraph state |
| 626–657 |   `asks` — §56 AMENDMENT, ratified 2026-09-09 |
| 658–727 |   `field_log` — §56 AMENDMENT, ratified 2026-09-21 |
| 728–733 |   `draft`, `belt_edits` and `final` are `dict`, never `str` |
| 734–756 |   `coaching_plan` is one typed plan, not a queue |
| 757–772 |   `gate_attempts` — the field whose absence recreated a production bug |
| 773–793 |   `validator_feedback` and `belt_edits` are different, and must stay separate |
| 794–811 |   `citations` and `uploads` — the evidence trail |
| 812–829 |   `hop_results` and `synthesis_output` must be state, not node locals |
| 830–838 |   Per-phase variants |
| 839–846 |   Naming discipline |
| 847–923 |  7. Field typing law — every captured field is a string |
| 863–875 |   Why strings |
| 876–895 |   The one exception — three cross-phase reference dicts |
| 896–923 |   Computation results |
| 924–1016 |  8. The checkpointer / store split |
| 948–967 |   Phased backend |
| 968–979 |   Concurrency and atomicity |
| 980–995 |   Why Blob, and not Cosmos / Tables / SQLite |
| 996–1016 |   On-blob checkpoint format |
| 1017–1153 |  9. The Store — cross-phase artifacts and boundary mappers |
| 1058–1081 |   Namespace convention |
| 1082–1111 |   Why cross-phase data cannot travel on parent state |
| 1112–1132 |   Boundary mappers |
| 1133–1145 |   Two prohibitions that follow |
| 1146–1153 |   Ordering constraint |
| 1154–1211 |  10. Azure Blob — two distinct concerns |
| 1173–1198 |   Complete physical layout |
| 1199–1211 |   The case blob is not updated per turn |
| 1212–1272 |  11. `step_log` — the audit trail |
| 1233–1242 |   `artifacts` and `step_log` are separate fields and stay separate |
| 1243–1272 |   Entries carry deterministic keys, never a raw timestamp as identity |
| 1273–1643 | Part III — The Graph |
| 1279–1319 |  12. Topology |
| 1309–1319 |   The subgraph builder takes the phase as a parameter |
| 1320–1459 |  13. The phase subgraph — five nodes |
| 1397–1427 |   The subgraph is a cycle, not a pipeline |
| 1428–1440 |   Two node names are BANNED |
| 1441–1446 |   Leaf tools are NOT subgraph nodes |
| 1447–1459 |   The validation stack and the policy advisory are NOT tools |
| 1460–1495 |  14. Node contract |
| 1483–1495 |   Reflection is a node, not a private function |
| 1496–1560 |  15. Routing — static edges and `Command` |
| 1502–1519 |   The decision test |
| 1520–1525 |   Never mix static edges and `Command` from the same node |
| 1526–1553 |   Level 1 does not route — it advances |
| 1554–1560 |   No subgraph imports another subgraph's nodes |
| 1561–1643 |  16. `thread_id`, `checkpoint_ns`, and where persistence attaches |
| 1567–1582 |   One `thread_id` per project |
| 1583–1596 |   The checkpointer and store go on the parent graph ONLY |
| 1597–1623 |   The wrapper node must invoke the subgraph directly (G-44) |
| 1624–1643 |   `recursion_limit` is a backstop, not the hop cap |
| 1644–2385 | Part IV — The Coaching Agent |
| 1650–1764 |  17. The Planner / Executor contract |
| 1726–1756 |   `CoachingPlan` |
| 1757–1764 |   Extraction is structured output, not a node and not a tool |
| 1765–1812 |  18. Building the executor — `create_agent` |
| 1777–1784 |   Binding tools directly onto a bare model is a violation |
| 1785–1790 |   `create_react_agent` is superseded |
| 1791–1803 |   deepagents is not a dependency |
| 1804–1812 |   The structured response and the coaching text coexist |
| 1813–2134 |  19. The middleware stack — eight, in order |
| 1835–1881 |   Ordering rules that bind |
| 1882–1893 |   Three independent retry caps |
| 1894–1937 |   19.1 `BeforeModelStateInjection` — injection timing |
| 1938–1953 |   19.2 `DMAICSkillsMiddleware` — progressive disclosure |
| 1954–1993 |   19.3 `SummarizationMiddleware` — context compression |
| 1994–2020 |   19.4 `ModelRetryMiddleware` — API-level retry |
| 2021–2033 |   19.5 `ToolRetryMiddleware` — tool-level retry |
| 2034–2056 |   19.6 `ContradictionDetectionMiddleware` — the mid-phase check |
| 2057–2091 |   19.7 `CoherenceMiddleware` — validation Layer 2a |
| 2092–2122 |   19.8 `DMAICGraderMiddleware` — coaching process quality |
| 2123–2134 |   19.9 Middleware deliberately NOT used |
| 2135–2209 |  20. `CoachingResponse` — the per-turn schema |
| 2189–2192 |   The executor node writes the response into state |
| 2193–2199 |   The executor's `response_format` is `CoachingResponse`, never a phase Output |
| 2200–2209 |   What structured output does NOT give you |
| 2210–2321 |  21. LLM roles, temperature, and the factory |
| 2230–2238 |   Factory only |
| 2239–2259 |   Roles |
| 2260–2276 |   Temperature |
| 2277–2321 |   Structured output — scoped by call type |
| 2322–2385 |  22. Prompts |
| 2348–2368 |   The memory hierarchy paragraph is mandatory |
| 2369–2385 |   Anti-hallucination guards are mandatory |
| 2386–3164 | Part V — Knowledge and Retrieval |
| 2390–2745 |  23. The three indexes |
| 2402–2452 |   23.1 `improve_knowledge_index` — methodology |
| 2453–2578 |   23.2 `improve_evidence_index` — Belt-uploaded evidence |
| 2498–2522 |    Supersession deletes; it does not flag |
| 2523–2578 |    Two Azure behaviours govern the migration |
| 2579–2651 |   23.2.1 The `role` vocabulary — ratified, not invented per phase |
| 2618–2651 |    `unclassified (pre-ask-binding)` is a MIGRATION SENTINEL, not a thirteenth role |
| 2652–2700 |   23.3 `improve_case_index` — case records (cross-case memory) |
| 2701–2711 |   The internal phase key is `analyse`, never `analyse_phase` |
| 2712–2736 |   23.4 The write-path trap that made `phase_relevance` unfilterable |
| 2737–2745 |   23.5 Schema change procedure |
| 2746–2874 |  24. The three `rag_lookup_*` tools |
| 2764–2821 |   `rag_lookup_evidence` returns a structured record, not rendered text |
| 2822–2834 |   RAG via tool, never via prepended system message |
| 2835–2859 |   The retrieval mechanism |
| 2860–2867 |   `belt_level` filtering is OFF by default |
| 2868–2874 |   `source_file` and `page_number` are returned, never filtered |
| 2875–2940 |  25. Multi-query and Reciprocal Rank Fusion |
| 2884–2900 |   Why it is mandatory |
| 2901–2907 |   The implementation |
| 2908–2929 |   `MultiQueryRetriever` and `EnsembleRetriever` are BANNED |
| 2930–2940 |   Encapsulation |
| 2941–3074 |  26. Multi-hop retrieval |
| 2956–2992 |   The hop cap is `RemainingSteps` |
| 2993–3011 |   Per-phase policy |
| 3012–3056 |   Planned multi-hop — the Analyse pipeline |
| 3057–3074 |   **UNVERIFIED** — planned multi-hop is Analyse-only |
| 3075–3121 |  27. Retrieval failure semantics |
| 3086–3094 |   Never wrap a retrieval call in a bare `except Exception` returning `[]` |
| 3095–3104 |   Three rules that each have already bitten |
| 3105–3121 |   The coach-facing message must not read as absence |
| 3122–3164 |  28. Memory taxonomy |
| 3140–3164 |   The static/dynamic split is the part that matters |
| 3165–3511 | Part VI — Tools |
| 3169–3326 |  29. The data channel and the universal eight |
| 3175–3210 |   29.1 There is no MCP — the data-channel decision |
| 3211–3253 |   29.2 The universal eight |
| 3219–3253 |    `load_evidence_series` joins the set — RATIFIED 2026-09-09 |
| 3254–3263 |   29.3 `record_field` is RETIRED and may not be reintroduced |
| 3264–3326 |   29.4 Cross-agent tools — a third category, present but NOT BOUND |
| 3327–3401 |  30. Computation tools and per-phase binding |
| 3332–3369 |   Tool sets are per phase, not universal |
| 3370–3375 |   Each of the 20 is a separate named tool |
| 3376–3384 |   All 20 are pure functions |
| 3385–3394 |   `imr_chart_limits` — the choice that is usually wrong by default |
| 3395–3401 |   Tool decisions are the model's, not the graph's |
| 3402–3434 |  31. Tool arg schemas and docstrings |
| 3408–3413 |   Every `@tool` uses `args_schema=` |
| 3414–3434 |   Docstrings are interface, not commentary |
| 3435–3511 |  32. Phase skills — SKILL.md |
| 3458–3462 |   Each skill's `allowed-tools` MUST match that phase's subset in §30 |
| 3463–3472 |   Progressive disclosure — three levels |
| 3473–3478 |   Storage backend: `FilesystemBackend` |
| 3479–3500 |   Each SKILL.md must carry |
| 3501–3511 |   Two distinct kinds of skill exist in this repository |
| 3512–4092 | Part VII — Validation and Gates |
| 3519–3639 |  33. The nine-step HITL gate |
| 3540–3553 |   Two quality checks, two actors, two moments |
| 3554–3565 |   Gates are one-way doors, with exactly one defined exception |
| 3566–3570 |   Implementation: graph-level `interrupt()` |
| 3571–3601 |   33.1 The two-node split |
| 3602–3631 |   33.2 `gate_apply_node` writes the gate document TWICE |
| 3632–3639 |   33.3 The checkpoint commits only after Belt approval |
| 3640–3743 |  34. The four-layer validation stack |
| 3655–3662 |   Layer 2a is middleware; layers 2b–2d are the node |
| 3663–3669 |   Layer 2d is NOT `DMAICGraderMiddleware` |
| 3670–3675 |   Run cheapest first |
| 3676–3685 |   The counter and the feedback |
| 3686–3695 |   Layer 2b is the only deterministic layer, deliberately |
| 3696–3707 |   Per-phase constraint sets |
| 3708–3717 |   34.1 Where each check fires |
| 3718–3743 |   34.2 The self-healing hierarchy and the transparency principle |
| 3744–3879 |  35. Two tiers of field, and the `warning` verdict |
| 3750–3764 |   The problem this solves |
| 3765–3781 |   Three distinct things check these fields, and conflating them is a design error |
| 3782–3830 |   Gate-required fields by phase |
| 3831–3847 |   The grader's verdict has three statuses |
| 3848–3855 |   Why two tiers |
| 3856–3879 |   The grader is belt-level aware |
| 3880–3973 |  36. Two graders — and why they are not redundant |
| 3899–3912 |   Why both exist |
| 3913–3936 |   `COACHING_QUALITY_RUBRIC` |
| 3937–3946 |   Mechanism, both graders |
| 3947–3956 |   Three criteria are verified deterministically, not by judgment |
| 3957–3973 |   The ratified rubric coverage |
| 3974–4070 |  37. Mid-phase contradiction and the re-approval cascade |
| 3980–4001 |   The check runs every turn, not only at gates |
| 4002–4035 |   §37 governs a GATE-COMMITTED value only |
| 4036–4049 |   There is NO tolerance threshold, and none may be added |
| 4050–4057 |   The re-approval cascade |
| 4058–4070 |   The cascade has a hard dependency on compensating actions |
| 4071–4092 |  38. Escalation |
| 4093–5673 | Part VIII — The DMAIC Domain |
| 4100–5294 |  39. The five phases |
| 4118–4132 |   The measurement thread that runs across three phases |
| 4133–4367 |   39.1 Define phase, complete specification |
| 4140–4147 |    39.1.1 Purpose |
| 4148–4210 |    39.1.2 The ordered field list — the `field_index` sequence (closes G-38) |
| 4211–4225 |    39.1.3 The composed-problem-statement rule (binding) |
| 4226–4240 |    39.1.4 The `team` structure |
| 4241–4250 |    39.1.5 SIPOC handling |
| 4251–4262 |    39.1.6 Gate, storage, progress view |
| 4263–4281 |    39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4282–4288 |    39.1.8 The other four phases |
| 4289–4321 |    39.1.9 The metric registry and Define's placeholder |
| 4322–4329 |    39.1.10 Tools bound to Define |
| 4330–4337 |    39.1.11 Conditions — routing and the gate |
| 4338–4345 |    39.1.12 State parameters — Define's use of `PhaseState` |
| 4346–4353 |    39.1.13 Metric literacy — what each metric means |
| 4354–4367 |    39.1.14 Cross-phase reads and writes |
| 4368–4623 |   39.2 Measure phase, complete specification |
| 4378–4386 |    39.2.1 Purpose |
| 4387–4409 |    39.2.2 The ordered field list — the `field_index` sequence |
| 4410–4470 |    39.2.3 The metric registry and Measure's placeholder |
| 4471–4490 |    39.2.4 SIPOC → the detailed process map |
| 4491–4512 |    39.2.5 Tools bound to Measure |
| 4513–4542 |    39.2.6 Conditions — sequence locks, routing, and the gate |
| 4543–4560 |    39.2.7 State parameters — Measure's use of `PhaseState` |
| 4561–4577 |    39.2.8 Metric literacy — what each metric means |
| 4578–4591 |    39.2.9 Gate, storage, progress view |
| 4592–4600 |    39.2.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4601–4617 |    39.2.11 Cross-phase reads and writes |
| 4618–4623 |    39.2.12 The other two phases |
| 4624–4853 |   39.3 Analyse phase, complete specification |
| 4634–4643 |    39.3.1 Purpose |
| 4644–4669 |    39.3.2 The ordered field list — the `field_index` sequence |
| 4670–4706 |    39.3.3 The metric registry and Analyse's placeholder (linkage form — closes F-13) |
| 4707–4726 |    39.3.4 Two movements — generate, then validate |
| 4727–4749 |    39.3.5 Tools bound to Analyse |
| 4750–4778 |    39.3.6 Conditions — methodology guards, routing, and the gate |
| 4779–4792 |    39.3.7 State parameters — Analyse's use of `PhaseState` |
| 4793–4808 |    39.3.8 Metric literacy — what each metric and statistic means |
| 4809–4820 |    39.3.9 Gate, storage, progress view |
| 4821–4829 |    39.3.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4830–4847 |    39.3.11 Cross-phase reads and writes |
| 4848–4853 |    39.3.12 The other phase |
| 4854–5056 |   39.4 Improve phase, complete specification |
| 4864–4872 |    39.4.1 Purpose |
| 4873–4893 |    39.4.2 The ordered field list — the `field_index` sequence |
| 4894–4912 |    39.4.3 The metric registry and Improve's placeholder (linkage form) |
| 4913–4930 |    39.4.4 Two movements — generate-and-select, then pilot-and-prove |
| 4931–4949 |    39.4.5 Tools bound to Improve |
| 4950–4981 |    39.4.6 Conditions — methodology guards, DOE belt-gating, routing, gate |
| 4982–4995 |    39.4.7 State parameters — Improve's use of `PhaseState` |
| 4996–5009 |    39.4.8 Metric literacy — what each metric and statistic means |
| 5010–5021 |    39.4.9 Gate, storage, progress view |
| 5022–5031 |    39.4.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5032–5048 |    39.4.11 Cross-phase reads and writes |
| 5049–5056 |    39.4.12 The last phase |
| 5057–5294 |   39.5 Control phase, complete specification |
| 5067–5075 |    39.5.1 Purpose |
| 5076–5104 |    39.5.2 The ordered field list — the `field_index` sequence |
| 5105–5134 |    39.5.3 The metric registry, the comparison, and single authority (closes F-14) |
| 5135–5151 |    39.5.4 Two movements — confirm it held, then lock it in |
| 5152–5171 |    39.5.5 Tools bound to Control |
| 5172–5204 |    39.5.6 Conditions — guards, routing, gate |
| 5205–5218 |    39.5.7 State parameters — Control's use of `PhaseState` |
| 5219–5233 |    39.5.8 Metric literacy — what each metric and statistic means |
| 5234–5247 |    39.5.9 Gate, storage, progress view |
| 5248–5258 |    39.5.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5259–5274 |    39.5.11 Cross-phase reads and writes — the thread closes here |
| 5275–5294 |    39.5.12 The measurement thread, closed |
| 5295–5390 |  40. The five `{Phase}Output` schemas |
| 5318–5336 |   Field counts |
| 5337–5348 |   The four gate-metadata fields |
| 5349–5362 |   Three fields are on all five schemas |
| 5363–5390 |   40.1 Gate assembly |
| 5391–5474 |  41. Structured dict fields, and FMEA |
| 5413–5424 |   The grader checks every sub-field is populated |
| 5425–5433 |   `control_plan` is `dict`, never `str` |
| 5434–5442 |   `stability_assessment` is checked BEFORE capability |
| 5443–5454 |   `experiment_justification` is Tier 1 and does not require an experiment |
| 5455–5474 |   FMEA has no field in any schema, and none may be added |
| 5475–5506 |  42. Cross-phase reference fields in practice |
| 5507–5673 |  43. The coaching method |
| 5525–5552 |   43.1 The seven-step computation pattern |
| 5553–5590 |   43.2 Show before asking |
| 5591–5613 |   43.3 The A→F session flow |
| 5614–5645 |   43.4 The live gate document preview |
| 5646–5655 |   43.5 No external URLs |
| 5656–5673 |   43.6 What the coach must not do |
| 5674–6030 | Part IX — Reliability |
| 5678–5706 |   43.7 Metric literacy — the metric, and the statistic |
| 5707–5735 |  44. The failure pipeline |
| 5736–5848 |  45. Timeouts and compensating actions |
| 5743–5774 |   Per-node timeouts — required on every phase executor node |
| 5775–5784 |   Composition order — retries run BEFORE the handler |
| 5785–5794 |   Node-level error handlers — required on every node with external writes |
| 5795–5800 |   Hand-written Saga orchestrators are BANNED |
| 5801–5809 |   Two dependencies on this rule, both correctness-critical |
| 5810–5841 |   Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST** |
| 5842–5848 |   `DeltaChannel` is NOT used |
| 5849–5964 |  46. The fallback chain and circuit breakers |
| 5855–5867 |   The v2.1 four-level chain |
| 5868–5874 |   Backoff strategy is chosen per level, not globally |
| 5875–5893 |   Level 3 cache |
| 5894–5909 |   Circuit breakers — three-state, two instances |
| 5910–5916 |   Degraded mode uses actual state, never a generic error |
| 5917–5924 |   HTTP 400 is NOT a fallback case |
| 5925–5964 |   46.1 Geographic redundancy — **DEFERRED** |
| 5965–6005 |  47. Disconnect policy — what a dropped client commits |
| 5982–5988 |   Ratified policy: ABANDON, not COMPLETE |
| 5989–6005 |   Five requirements |
| 6006–6030 |  48. Structured errors |
| 6031–6519 | Part X — Operations |
| 6035–6089 |  49. API surface |
| 6041–6050 |   One runtime |
| 6051–6058 |   Async by default |
| 6059–6083 |   Endpoints |
| 6084–6089 |   Envelopes are Pydantic v2 |
| 6090–6246 |  50. UI and language rules |
| 6097–6135 |   50.1 Coach response structure |
| 6136–6147 |   Plain language always |
| 6148–6155 |   Citations |
| 6156–6169 |   Contextual feedback |
| 6170–6176 |   Connection status before the first interaction |
| 6177–6182 |   The gate review screen |
| 6183–6221 |   The live gate document |
| 6222–6233 |   The all-gate-fields tab is the contradiction backstop |
| 6234–6246 |   The conflict resolution panel |
| 6247–6322 |  51. Tracing and observability |
| 6253–6263 |   LangSmith is mandatory |
| 6264–6296 |   `@traceable` on every custom function |
| 6297–6302 |   What gets traced |
| 6303–6310 |   P50/P99 latency is a coaching quality signal |
| 6311–6322 |   Logs |
| 6323–6377 |  52. Evaluation and regression testing |
| 6329–6336 |   Built alongside the refactor, not before it |
| 6337–6343 |   The dataset is authored jointly, not generated |
| 6344–6357 |   Minimum viable suite |
| 6358–6368 |   Rubrics and the eval dataset are complementary, not duplicative |
| 6369–6377 |   Two open validation questions this suite answers |
| 6378–6519 |  53. Configuration, dependencies and deployment |
| 6384–6400 |   Fail-fast environment validation |
| 6401–6424 |   Dependency floor |
| 6425–6435 |   `/verify-current-version` is a mandatory checkpoint |
| 6436–6443 |   Infrastructure not yet provisioned |
| 6444–6455 |   Deployment layer: FastAPI, not LangGraph Server |
| 6456–6519 |   53.1 Migration sequence |
| 6520–7088 | Part XI — Governance |
| 6524–6566 |  54. Where code is allowed to live |
| 6531–6548 |   Classes are permitted ONLY in these files |
| 6549–6566 |   Target folder structure |
| 6567–6937 |  55. Anti-drift |
| 6581–6595 |   Rule numbers are load-bearing |
| 6596–6606 |   The registry guards code, not documentation |
| 6607–6612 |   Verification discipline |
| 6613–6635 |   Reference sweeps must use raw `grep -rn`, never a gitignore-filtered tool |
| 6636–6686 |   55.1 Spec-layer governance rules |
| 6687–6769 |   55.2 The BUILT markers, and the paths that oblige a re-check |
| 6770–6850 |   55.3 The phase completeness set — what one phase actually traverses |
| 6851–6900 |   55.4 Facts have one owner — the ratified minimum |
| 6901–6937 |   55.5 The commit gates govern. The rule files are advisory context. |
| 6938–7088 |  56. Amendment procedure |
| 6965–7008 |   56.0 What changed about amending, when the rules stopped being one file |
| 7009–7027 |   56.0.1 Rule, reference, and owned fact — three destinations |
| 7028–7070 |   56.1 A phase is one atomic unit — schema, validator, skill |
| 7071–7088 |   What requires an amendment rather than a routine change |
| 7089–11432 | Part XII — Specification |
| 7099–7122 |   56.2 The rule lands here; the reasoning lands in the commit |
| 7123–7156 |   56.3 The tree at HEAD is the only source of truth |
| 7157–7418 |  57. The specification layer — how to read and write a spec entry |
| 7164–7184 |   Why this Part exists |
| 7185–7200 |   The five structural rules |
| 7201–7215 |   Entry identity and traceability |
| 7216–7263 |   The entry template — three layers |
| 7264–7275 |   How gaps are marked |
| 7276–7292 |   57.1 The two calibrated samples |
| 7293–7346 |   57.2 SAMPLE 1 — CLASS TEMPLATE — S-C01 `SupervisorState` |
| 7296–7346 |    SPEC — `SupervisorState` |
| 7347–7397 |   57.3 SAMPLE 2 — FUNCTION/NODE TEMPLATE — S-F04 `phase_executor` (the coach node) |
| 7351–7397 |    SPEC — `phase_executor` (the coach node) |
| 7398–7418 |   57.4 Entry index |
| 7419–8747 |  58. Spec — graph management |
| 7429–7432 |   58.1 S-C01 · `SupervisorState` |
| 7433–7598 |   58.2 S-C02 · `PhaseState` |
| 7599–7617 |   58.3 S-C03 · Per-phase use of `PhaseState` |
| 7618–7692 |   58.4 S-C04 · `CoachingPlan` |
| 7693–7802 |   58.5 S-C05 · `CoachingResponse` |
| 7803–7854 |   58.6 S-C06 · `AzureBlobStore` |
| 7855–7900 |   58.7 S-C07 · `AzureBlobCheckpointSaver` |
| 7901–7947 |   58.8 S-C08 · `ImproveBlobClient` |
| 7948–8010 |   58.9 S-C09 · `storage/models.py` — the record models |
| 8011–8074 |   58.10 S-F01 · The supervisor graph — static edges |
| 8045–8054 |    SIPOC — at a glance |
| 8055–8074 |    Behaviors (EARS) |
| 8075–8120 |   58.11 S-F02 · `build_phase_subgraph(phase, llm)` |
| 8093–8102 |    SIPOC — at a glance |
| 8103–8120 |    Behaviors (EARS) |
| 8121–8161 |   58.12 S-F03 · `phase_planner` node |
| 8132–8141 |    SIPOC — at a glance |
| 8142–8161 |    Behaviors (EARS) |
| 8162–8173 |   58.13 S-F04 · `phase_executor` node |
| 8174–8235 |   58.14 S-F05 · `validation_stack` node |
| 8184–8193 |    SIPOC — at a glance |
| 8194–8205 |    Behaviors (EARS) |
| 8206–8235 |    ⚠ AI-ACT — high-risk surface |
| 8236–8287 |   58.15 S-F06 · `gate_review_node` |
| 8246–8255 |    SIPOC — at a glance |
| 8256–8263 |    Behaviors (EARS) |
| 8264–8287 |    ⚠ AI-ACT — high-risk surface |
| 8288–8355 |   58.16 S-F07 · `gate_apply_node` |
| 8309–8318 |    SIPOC — at a glance |
| 8319–8331 |    Behaviors (EARS) |
| 8332–8355 |    ⚠ AI-ACT — high-risk surface |
| 8356–8391 |   58.17 S-F08 · The escalation subgraph |
| 8364–8373 |    SIPOC — at a glance |
| 8374–8391 |    Behaviors (EARS) |
| 8392–8460 |   58.18 S-F09 · `analyse_executor_node` |
| 8432–8441 |    SIPOC — at a glance |
| 8442–8460 |    Behaviors (EARS) |
| 8461–8554 |   58.19 S-F10 · `define_input_mapper` |
| 8504–8516 |    SIPOC — at a glance |
| 8517–8545 |    Execution site — where a boundary mapper actually runs |
| 8546–8554 |    Behaviors (EARS) |
| 8555–8608 |   58.20 S-F11 · `define_output_mapper` |
| 8584–8593 |    SIPOC — at a glance |
| 8594–8608 |    Behaviors (EARS) |
| 8609–8658 |   58.21 S-F12 · The Measure, Analyse, Improve and Control mapper pairs |
| 8617–8626 |    SIPOC — at a glance |
| 8627–8658 |    Behaviors (EARS) |
| 8659–8747 |   58.22 S-F13 · Level 2 `Command` routing |
| 8676–8693 |    DP1 — the planner owns the field / gate decision |
| 8694–8714 |    DP2 — the validation stack's three exits |
| 8715–8735 |    DP3 — the gate exits |
| 8736–8747 |    What is settled and binds |
| 8748–9130 |  59. Spec — knowledge and retrieval |
| 8761–8790 |   59.1 S-C16 · `Hop` |
| 8791–8837 |   59.2 S-C17 · `Plan` — the hop decomposition plan |
| 8838–8874 |   59.3 S-C18 · `SynthesisOutput` |
| 8875–8891 |   59.4 S-C19 · `QueryVariants` |
| 8892–8938 |   59.5 S-F14 · `rag_lookup_methodology` |
| 8913–8922 |    SIPOC — at a glance |
| 8923–8938 |    Behaviors (EARS) |
| 8939–8986 |   59.6 S-F15 · `rag_lookup_evidence` |
| 8962–8971 |    SIPOC — at a glance |
| 8972–8986 |    Behaviors (EARS) |
| 8987–9033 |   59.7 S-F16 · `rag_lookup_case_history` |
| 9010–9019 |    SIPOC — at a glance |
| 9020–9033 |    Behaviors (EARS) |
| 9034–9084 |   59.8 S-F17 · `reciprocal_rank_fusion` |
| 9061–9070 |    SIPOC — at a glance |
| 9071–9084 |    Behaviors (EARS) |
| 9085–9130 |   59.9 S-F18 · The retriever layer — `search_knowledge`, `search_cases`, `search_evidence` |
| 9113–9130 |    SIPOC — at a glance |
| 9131–9416 |  60. Spec — tools |
| 9149–9182 |   60.1 S-F19 · `propose_template` |
| 9162–9182 |    SIPOC — at a glance |
| 9183–9221 |   60.2 S-F20 · `propose_diagram` |
| 9198–9207 |    SIPOC — at a glance |
| 9208–9221 |    Behaviors (EARS) |
| 9222–9263 |   60.3 S-F21 · `check_gate_status` |
| 9237–9246 |    SIPOC — at a glance |
| 9247–9263 |    Behaviors (EARS) |
| 9264–9299 |   60.4 S-F22 · `request_human_approval` |
| 9278–9299 |    SIPOC — at a glance |
| 9300–9316 |   60.5 S-F23 · `load_skill(name)` |
| 9317–9361 |   60.6 S-F24 · The 20 computation tools |
| 9340–9361 |    Behaviors (EARS) — binding on all twenty |
| 9362–9416 |   60.7 S-F57 · `load_evidence_series(blob_path, column)` |
| 9387–9396 |    SIPOC — at a glance |
| 9397–9416 |    Behaviors (EARS) |
| 9417–9669 |  61. Spec — the coaching agent's middleware |
| 9435–9497 |   61.1 S-C10 · `ContradictionDetectionMiddleware` |
| 9457–9466 |    Behaviors (EARS) |
| 9467–9497 |    ⚠ AI-ACT — high-risk surface |
| 9498–9539 |   61.2 S-C11 · `BeforeModelStateInjection` |
| 9511–9539 |    Behaviors (EARS) |
| 9540–9579 |   61.3 S-C12 · `DMAICSkillsMiddleware` |
| 9560–9579 |    Behaviors (EARS) |
| 9580–9616 |   61.4 S-C13 · `CoherenceMiddleware` |
| 9594–9616 |    Behaviors (EARS) |
| 9617–9652 |   61.5 S-C14 · `DMAICGraderMiddleware` |
| 9627–9652 |    Behaviors (EARS) |
| 9653–9669 |   61.6 S-C15 · `HITLInterrupt` |
| 9670–10077 |  62. Spec — validation and gates |
| 9684–9726 |   62.1 S-C20 · `CriterionVerdict` |
| 9727–9744 |   62.2 S-C21 · `GraderVerdict` |
| 9745–9758 |   62.3 S-C22 · `CoachingGraderVerdict` |
| 9759–9770 |   62.4 S-C23 · `CoherenceResult` |
| 9771–9785 |   62.5 S-C24 · `ConstraintCheckResult` / `ConstraintVerdict` |
| 9786–9798 |   62.6 S-C25 · `PolicyAdvisoryResult` |
| 9799–9835 |   62.7 S-C26 · `DMAICGateValidator` |
| 9836–9870 |   62.8 S-F25 · Layer 2c — the constraint check |
| 9845–9854 |    SIPOC — at a glance |
| 9855–9870 |    Behaviors (EARS) |
| 9871–9918 |   62.9 S-F26 · Layer 2d — the gate grader |
| 9886–9895 |    SIPOC — at a glance |
| 9896–9918 |    Behaviors (EARS) |
| 9919–9960 |   62.10 S-F27 · The policy advisory |
| 9934–9943 |    SIPOC — at a glance |
| 9944–9960 |    Behaviors (EARS) |
| 9961–10077 |   62.11 S-F28 · Gate document assembly |
| 10049–10058 |    SIPOC — at a glance |
| 10059–10077 |    Behaviors (EARS) |
| 10078–10599 |  63. Spec — the DMAIC gate documents |
| 10096–10164 |   63.1 S-C27 · `DefineOutput` |
| 10165–10205 |   63.2 S-C28 · `MeasureOutput` |
| 10206–10263 |   63.3 S-C29 · `AnalyseOutput` |
| 10264–10323 |   63.4 S-C30 · `ImproveOutput` |
| 10324–10395 |   63.5 S-C31 · `ControlOutput` |
| 10396–10462 |   63.6 S-C32 · The three cross-phase reference dicts |
| 10463–10504 |   63.7 S-C33 · The three structured dict fields |
| 10505–10543 |   63.8 S-C38 · `metric_definitions` — the project metric registry |
| 10544–10599 |   63.9 S-C39 · `phase_metrics` — the per-phase placeholder |
| 10600–10888 |  64. Spec — reliability |
| 10611–10651 |   64.1 S-C34 · `AgentImproveError` |
| 10652–10690 |   64.2 S-C35 · `CircuitBreaker` |
| 10691–10777 |   64.3 S-F29 · `phase_error_recovery` |
| 10719–10728 |    SIPOC — at a glance |
| 10729–10777 |    Behaviors (EARS) |
| 10778–10826 |   64.4 S-F30 · `degraded_mode_response` |
| 10799–10808 |    SIPOC — at a glance |
| 10809–10826 |    Behaviors (EARS) |
| 10827–10845 |   64.5 S-F31 · `synthesise_partial` |
| 10846–10870 |   64.6 S-F32 · `delete_or_flag_stale_in_case_index` |
| 10871–10888 |   64.7 S-F33 · `degraded_coaching_response` node |
| 10889–11065 |  65. Spec — API, UI and evidence |
| 10899–10919 |   65.1 S-C36 · `CitationRecord` and `CitationBundle` |
| 10920–10937 |   65.2 S-C37 · The API envelopes |
| 10938–10990 |   65.3 S-F34 · The API surface |
| 10960–10969 |    SIPOC — at a glance |
| 10970–10990 |    Behaviors (EARS) |
| 10991–11030 |   65.4 S-F35 · The upload handler |
| 11016–11030 |    Behaviors (EARS) |
| 11031–11065 |   65.5 S-F36 · The `improve_case_index` write path |
| 11066–11076 |  66. The SPEC-GAP register — MOVED |
| 11077–11170 |  67. EU AI Act compliance posture |
| 11084–11099 |   67.1 The deadlines are now fixed |
| 11100–11125 |   67.2 The classification question — open, and not answered here |
| 11126–11143 |   67.3 The eight core provider obligations |
| 11144–11154 |   67.4 One compliance finding is already recorded in this document |
| 11155–11170 |   67.5 Compliance-source discipline |
| 11171–11251 |  68. The DORA-structured compliance risk register |
| 11178–11195 |   68.1 Why DORA structure |
| 11196–11212 |   68.2 The register |
| 11213–11236 |   68.3 Pending classification — not register rows |
| 11237–11251 |   68.4 The infrastructure risk already on record |
| 11252–11432 |  69. Spec — computation tools |
| 11281–11352 |   69.1 Common conventions — stated once, binding on all twenty |
| 11353–11358 |   69.2 S-F37 · Define — 1 tool |
| 11359–11371 |   69.3 S-F38–S-F45 · Measure — 8 tools |
| 11372–11381 |   69.4 S-F46–S-F50 · Analyse — 5 tools |
| 11382–11387 |   69.5 S-F51 · Improve — 1 tool |
| 11388–11405 |   69.6 S-F52–S-F56 · Control — 5 tools |
| 11406–11432 |   69.7 The Measure control-chart boundary — a tool that is deliberately absent |
| 11433–11661 | Appendices |
| 11437–11452 |  Appendix A — Provenance index |
| 11443–11446 |   A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference |
| 11447–11452 |   A.2 `agent-improve/ARCHITECTURE.md` → this reference |
| 11453–11483 |  Appendix B — Deferred backlog |
| 11484–11549 |  Appendix C — Trusted sources |
| 11490–11509 |   Tier 1 — current, authoritative |
| 11510–11528 |   Tier 1 — compliance |
| 11529–11532 |   Tier 2 — official announcements |
| 11533–11536 |   Tier 3 — informed practitioner, cross-check before citing |
| 11537–11543 |   Downgraded — historical |
| 11544–11549 |   Excluded |
| 11550–11629 |  Appendix D — Retired names, banned patterns, and exclusions |
| 11552–11574 |   D.1 Retired names — never reintroduce |
| 11575–11618 |   D.2 Banned patterns |
| 11619–11629 |   D.3 Architecturally excluded — not deferred |
| 11630–11638 |  Appendix E — Current state |
| 11639–11661 |  Appendix F — The v2.2.16 registers |
| 11645–11650 |   F.1 Decisions Resolved (v2.2) — the former §17 |
| 11651–11661 |   F.2 Change Log — the former §18 |
| 11655–11661 |    F.2.1 Amendment procedure — the former §18.1 |
