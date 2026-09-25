# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md §22 b). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 11655 lines

| Lines | Heading |
|---|---|
| 27–49 |  🗺 Where state lives — a MAP, not a definition |
| 50–251 | Agentic Architecture Reference |
| 146–251 |  About this document |
| 152–209 |   Scope — three agents, one architecture |
| 210–224 |   The two-document division |
| 225–239 |   Section numbering and provenance |
| 240–251 |   Reading conventions |
| 252–543 | Part I — Orientation |
| 256–332 |  1. What Agent Improve is |
| 276–302 |   What makes it architecturally distinctive |
| 303–332 |   The runtime stack |
| 333–384 |  2. How to read this document |
| 339–355 |   By what you are trying to do |
| 356–384 |   Canonical ownership |
| 385–483 |  3. Terminology |
| 396–412 |   Structural primitives |
| 413–424 |   Role labels |
| 425–442 |   The recursion is two levels, not infinite |
| 443–457 |   "Harness" — two senses, do not conflate |
| 458–468 |   "Agent" — used carefully |
| 469–483 |   Things that are deliberately not levels |
| 484–543 |  4. Architecture at a glance |
| 527–543 |   The five things that shape everything else |
| 544–1271 | Part II — State and Persistence |
| 551–609 |  5. `SupervisorState` — orchestration only |
| 563–569 |   `gate_passed` is a dict, not a list |
| 570–581 |   `current_phase` and `phase_index` are derived, and kept anyway |
| 582–601 |   Four fields were removed as redundant, and may not return |
| 602–609 |   Artifacts are not here |
| 610–845 |  6. `PhaseState` — per-phase subgraph state |
| 625–656 |   `asks` — §56 AMENDMENT, ratified 2026-09-09 |
| 657–726 |   `field_log` — §56 AMENDMENT, ratified 2026-09-21 |
| 727–732 |   `draft`, `belt_edits` and `final` are `dict`, never `str` |
| 733–755 |   `coaching_plan` is one typed plan, not a queue |
| 756–771 |   `gate_attempts` — the field whose absence recreated a production bug |
| 772–792 |   `validator_feedback` and `belt_edits` are different, and must stay separate |
| 793–810 |   `citations` and `uploads` — the evidence trail |
| 811–828 |   `hop_results` and `synthesis_output` must be state, not node locals |
| 829–837 |   Per-phase variants |
| 838–845 |   Naming discipline |
| 846–922 |  7. Field typing law — every captured field is a string |
| 862–874 |   Why strings |
| 875–894 |   The one exception — three cross-phase reference dicts |
| 895–922 |   Computation results |
| 923–1015 |  8. The checkpointer / store split |
| 947–966 |   Phased backend |
| 967–978 |   Concurrency and atomicity |
| 979–994 |   Why Blob, and not Cosmos / Tables / SQLite |
| 995–1015 |   On-blob checkpoint format |
| 1016–1152 |  9. The Store — cross-phase artifacts and boundary mappers |
| 1057–1080 |   Namespace convention |
| 1081–1110 |   Why cross-phase data cannot travel on parent state |
| 1111–1131 |   Boundary mappers |
| 1132–1144 |   Two prohibitions that follow |
| 1145–1152 |   Ordering constraint |
| 1153–1210 |  10. Azure Blob — two distinct concerns |
| 1172–1197 |   Complete physical layout |
| 1198–1210 |   The case blob is not updated per turn |
| 1211–1271 |  11. `step_log` — the audit trail |
| 1232–1241 |   `artifacts` and `step_log` are separate fields and stay separate |
| 1242–1271 |   Entries carry deterministic keys, never a raw timestamp as identity |
| 1272–1642 | Part III — The Graph |
| 1278–1318 |  12. Topology |
| 1308–1318 |   The subgraph builder takes the phase as a parameter |
| 1319–1458 |  13. The phase subgraph — five nodes |
| 1396–1426 |   The subgraph is a cycle, not a pipeline |
| 1427–1439 |   Two node names are BANNED |
| 1440–1445 |   Leaf tools are NOT subgraph nodes |
| 1446–1458 |   The validation stack and the policy advisory are NOT tools |
| 1459–1494 |  14. Node contract |
| 1482–1494 |   Reflection is a node, not a private function |
| 1495–1559 |  15. Routing — static edges and `Command` |
| 1501–1518 |   The decision test |
| 1519–1524 |   Never mix static edges and `Command` from the same node |
| 1525–1552 |   Level 1 does not route — it advances |
| 1553–1559 |   No subgraph imports another subgraph's nodes |
| 1560–1642 |  16. `thread_id`, `checkpoint_ns`, and where persistence attaches |
| 1566–1581 |   One `thread_id` per project |
| 1582–1595 |   The checkpointer and store go on the parent graph ONLY |
| 1596–1622 |   The wrapper node must invoke the subgraph directly (G-44) |
| 1623–1642 |   `recursion_limit` is a backstop, not the hop cap |
| 1643–2384 | Part IV — The Coaching Agent |
| 1649–1763 |  17. The Planner / Executor contract |
| 1725–1755 |   `CoachingPlan` |
| 1756–1763 |   Extraction is structured output, not a node and not a tool |
| 1764–1811 |  18. Building the executor — `create_agent` |
| 1776–1783 |   Binding tools directly onto a bare model is a violation |
| 1784–1789 |   `create_react_agent` is superseded |
| 1790–1802 |   deepagents is not a dependency |
| 1803–1811 |   The structured response and the coaching text coexist |
| 1812–2133 |  19. The middleware stack — eight, in order |
| 1834–1880 |   Ordering rules that bind |
| 1881–1892 |   Three independent retry caps |
| 1893–1936 |   19.1 `BeforeModelStateInjection` — injection timing |
| 1937–1952 |   19.2 `DMAICSkillsMiddleware` — progressive disclosure |
| 1953–1992 |   19.3 `SummarizationMiddleware` — context compression |
| 1993–2019 |   19.4 `ModelRetryMiddleware` — API-level retry |
| 2020–2032 |   19.5 `ToolRetryMiddleware` — tool-level retry |
| 2033–2055 |   19.6 `ContradictionDetectionMiddleware` — the mid-phase check |
| 2056–2090 |   19.7 `CoherenceMiddleware` — validation Layer 2a |
| 2091–2121 |   19.8 `DMAICGraderMiddleware` — coaching process quality |
| 2122–2133 |   19.9 Middleware deliberately NOT used |
| 2134–2208 |  20. `CoachingResponse` — the per-turn schema |
| 2188–2191 |   The executor node writes the response into state |
| 2192–2198 |   The executor's `response_format` is `CoachingResponse`, never a phase Output |
| 2199–2208 |   What structured output does NOT give you |
| 2209–2320 |  21. LLM roles, temperature, and the factory |
| 2229–2237 |   Factory only |
| 2238–2258 |   Roles |
| 2259–2275 |   Temperature |
| 2276–2320 |   Structured output — scoped by call type |
| 2321–2384 |  22. Prompts |
| 2347–2367 |   The memory hierarchy paragraph is mandatory |
| 2368–2384 |   Anti-hallucination guards are mandatory |
| 2385–3163 | Part V — Knowledge and Retrieval |
| 2389–2744 |  23. The three indexes |
| 2401–2451 |   23.1 `improve_knowledge_index` — methodology |
| 2452–2577 |   23.2 `improve_evidence_index` — Belt-uploaded evidence |
| 2497–2521 |    Supersession deletes; it does not flag |
| 2522–2577 |    Two Azure behaviours govern the migration |
| 2578–2650 |   23.2.1 The `role` vocabulary — ratified, not invented per phase |
| 2617–2650 |    `unclassified (pre-ask-binding)` is a MIGRATION SENTINEL, not a thirteenth role |
| 2651–2699 |   23.3 `improve_case_index` — case records (cross-case memory) |
| 2700–2710 |   The internal phase key is `analyse`, never `analyse_phase` |
| 2711–2735 |   23.4 The write-path trap that made `phase_relevance` unfilterable |
| 2736–2744 |   23.5 Schema change procedure |
| 2745–2873 |  24. The three `rag_lookup_*` tools |
| 2763–2820 |   `rag_lookup_evidence` returns a structured record, not rendered text |
| 2821–2833 |   RAG via tool, never via prepended system message |
| 2834–2858 |   The retrieval mechanism |
| 2859–2866 |   `belt_level` filtering is OFF by default |
| 2867–2873 |   `source_file` and `page_number` are returned, never filtered |
| 2874–2939 |  25. Multi-query and Reciprocal Rank Fusion |
| 2883–2899 |   Why it is mandatory |
| 2900–2906 |   The implementation |
| 2907–2928 |   `MultiQueryRetriever` and `EnsembleRetriever` are BANNED |
| 2929–2939 |   Encapsulation |
| 2940–3073 |  26. Multi-hop retrieval |
| 2955–2991 |   The hop cap is `RemainingSteps` |
| 2992–3010 |   Per-phase policy |
| 3011–3055 |   Planned multi-hop — the Analyse pipeline |
| 3056–3073 |   **UNVERIFIED** — planned multi-hop is Analyse-only |
| 3074–3120 |  27. Retrieval failure semantics |
| 3085–3093 |   Never wrap a retrieval call in a bare `except Exception` returning `[]` |
| 3094–3103 |   Three rules that each have already bitten |
| 3104–3120 |   The coach-facing message must not read as absence |
| 3121–3163 |  28. Memory taxonomy |
| 3139–3163 |   The static/dynamic split is the part that matters |
| 3164–3510 | Part VI — Tools |
| 3168–3325 |  29. The data channel and the universal eight |
| 3174–3209 |   29.1 There is no MCP — the data-channel decision |
| 3210–3252 |   29.2 The universal eight |
| 3218–3252 |    `load_evidence_series` joins the set — RATIFIED 2026-09-09 |
| 3253–3262 |   29.3 `record_field` is RETIRED and may not be reintroduced |
| 3263–3325 |   29.4 Cross-agent tools — a third category, present but NOT BOUND |
| 3326–3400 |  30. Computation tools and per-phase binding |
| 3331–3368 |   Tool sets are per phase, not universal |
| 3369–3374 |   Each of the 20 is a separate named tool |
| 3375–3383 |   All 20 are pure functions |
| 3384–3393 |   `imr_chart_limits` — the choice that is usually wrong by default |
| 3394–3400 |   Tool decisions are the model's, not the graph's |
| 3401–3433 |  31. Tool arg schemas and docstrings |
| 3407–3412 |   Every `@tool` uses `args_schema=` |
| 3413–3433 |   Docstrings are interface, not commentary |
| 3434–3510 |  32. Phase skills — SKILL.md |
| 3457–3461 |   Each skill's `allowed-tools` MUST match that phase's subset in §30 |
| 3462–3471 |   Progressive disclosure — three levels |
| 3472–3477 |   Storage backend: `FilesystemBackend` |
| 3478–3499 |   Each SKILL.md must carry |
| 3500–3510 |   Two distinct kinds of skill exist in this repository |
| 3511–4091 | Part VII — Validation and Gates |
| 3518–3638 |  33. The nine-step HITL gate |
| 3539–3552 |   Two quality checks, two actors, two moments |
| 3553–3564 |   Gates are one-way doors, with exactly one defined exception |
| 3565–3569 |   Implementation: graph-level `interrupt()` |
| 3570–3600 |   33.1 The two-node split |
| 3601–3630 |   33.2 `gate_apply_node` writes the gate document TWICE |
| 3631–3638 |   33.3 The checkpoint commits only after Belt approval |
| 3639–3742 |  34. The four-layer validation stack |
| 3654–3661 |   Layer 2a is middleware; layers 2b–2d are the node |
| 3662–3668 |   Layer 2d is NOT `DMAICGraderMiddleware` |
| 3669–3674 |   Run cheapest first |
| 3675–3684 |   The counter and the feedback |
| 3685–3694 |   Layer 2b is the only deterministic layer, deliberately |
| 3695–3706 |   Per-phase constraint sets |
| 3707–3716 |   34.1 Where each check fires |
| 3717–3742 |   34.2 The self-healing hierarchy and the transparency principle |
| 3743–3878 |  35. Two tiers of field, and the `warning` verdict |
| 3749–3763 |   The problem this solves |
| 3764–3780 |   Three distinct things check these fields, and conflating them is a design error |
| 3781–3829 |   Gate-required fields by phase |
| 3830–3846 |   The grader's verdict has three statuses |
| 3847–3854 |   Why two tiers |
| 3855–3878 |   The grader is belt-level aware |
| 3879–3972 |  36. Two graders — and why they are not redundant |
| 3898–3911 |   Why both exist |
| 3912–3935 |   `COACHING_QUALITY_RUBRIC` |
| 3936–3945 |   Mechanism, both graders |
| 3946–3955 |   Three criteria are verified deterministically, not by judgment |
| 3956–3972 |   The ratified rubric coverage |
| 3973–4069 |  37. Mid-phase contradiction and the re-approval cascade |
| 3979–4000 |   The check runs every turn, not only at gates |
| 4001–4034 |   §37 governs a GATE-COMMITTED value only |
| 4035–4048 |   There is NO tolerance threshold, and none may be added |
| 4049–4056 |   The re-approval cascade |
| 4057–4069 |   The cascade has a hard dependency on compensating actions |
| 4070–4091 |  38. Escalation |
| 4092–5670 | Part VIII — The DMAIC Domain |
| 4099–5292 |  39. The five phases |
| 4117–4131 |   The measurement thread that runs across three phases |
| 4132–4365 |   39.1 Define phase, complete specification |
| 4139–4146 |    39.1.1 Purpose |
| 4147–4209 |    39.1.2 The ordered field list — the `field_index` sequence (closes G-38) |
| 4210–4224 |    39.1.3 The composed-problem-statement rule (binding) |
| 4225–4239 |    39.1.4 The `team` structure |
| 4240–4249 |    39.1.5 SIPOC handling |
| 4250–4261 |    39.1.6 Gate, storage, progress view |
| 4262–4280 |    39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4281–4287 |    39.1.8 The other four phases |
| 4288–4319 |    39.1.9 The metric registry and Define's placeholder |
| 4320–4327 |    39.1.10 Tools bound to Define |
| 4328–4335 |    39.1.11 Conditions — routing and the gate |
| 4336–4343 |    39.1.12 State parameters — Define's use of `PhaseState` |
| 4344–4351 |    39.1.13 Metric literacy — what each metric means |
| 4352–4365 |    39.1.14 Cross-phase reads and writes |
| 4366–4621 |   39.2 Measure phase, complete specification |
| 4376–4384 |    39.2.1 Purpose |
| 4385–4407 |    39.2.2 The ordered field list — the `field_index` sequence |
| 4408–4468 |    39.2.3 The metric registry and Measure's placeholder |
| 4469–4488 |    39.2.4 SIPOC → the detailed process map |
| 4489–4510 |    39.2.5 Tools bound to Measure |
| 4511–4540 |    39.2.6 Conditions — sequence locks, routing, and the gate |
| 4541–4558 |    39.2.7 State parameters — Measure's use of `PhaseState` |
| 4559–4575 |    39.2.8 Metric literacy — what each metric means |
| 4576–4589 |    39.2.9 Gate, storage, progress view |
| 4590–4598 |    39.2.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4599–4615 |    39.2.11 Cross-phase reads and writes |
| 4616–4621 |    39.2.12 The other two phases |
| 4622–4851 |   39.3 Analyse phase, complete specification |
| 4632–4641 |    39.3.1 Purpose |
| 4642–4667 |    39.3.2 The ordered field list — the `field_index` sequence |
| 4668–4704 |    39.3.3 The metric registry and Analyse's placeholder (linkage form — closes F-13) |
| 4705–4724 |    39.3.4 Two movements — generate, then validate |
| 4725–4747 |    39.3.5 Tools bound to Analyse |
| 4748–4776 |    39.3.6 Conditions — methodology guards, routing, and the gate |
| 4777–4790 |    39.3.7 State parameters — Analyse's use of `PhaseState` |
| 4791–4806 |    39.3.8 Metric literacy — what each metric and statistic means |
| 4807–4818 |    39.3.9 Gate, storage, progress view |
| 4819–4827 |    39.3.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4828–4845 |    39.3.11 Cross-phase reads and writes |
| 4846–4851 |    39.3.12 The other phase |
| 4852–5054 |   39.4 Improve phase, complete specification |
| 4862–4870 |    39.4.1 Purpose |
| 4871–4891 |    39.4.2 The ordered field list — the `field_index` sequence |
| 4892–4910 |    39.4.3 The metric registry and Improve's placeholder (linkage form) |
| 4911–4928 |    39.4.4 Two movements — generate-and-select, then pilot-and-prove |
| 4929–4947 |    39.4.5 Tools bound to Improve |
| 4948–4979 |    39.4.6 Conditions — methodology guards, DOE belt-gating, routing, gate |
| 4980–4993 |    39.4.7 State parameters — Improve's use of `PhaseState` |
| 4994–5007 |    39.4.8 Metric literacy — what each metric and statistic means |
| 5008–5019 |    39.4.9 Gate, storage, progress view |
| 5020–5029 |    39.4.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5030–5046 |    39.4.11 Cross-phase reads and writes |
| 5047–5054 |    39.4.12 The last phase |
| 5055–5292 |   39.5 Control phase, complete specification |
| 5065–5073 |    39.5.1 Purpose |
| 5074–5102 |    39.5.2 The ordered field list — the `field_index` sequence |
| 5103–5132 |    39.5.3 The metric registry, the comparison, and single authority (closes F-14) |
| 5133–5149 |    39.5.4 Two movements — confirm it held, then lock it in |
| 5150–5169 |    39.5.5 Tools bound to Control |
| 5170–5202 |    39.5.6 Conditions — guards, routing, gate |
| 5203–5216 |    39.5.7 State parameters — Control's use of `PhaseState` |
| 5217–5231 |    39.5.8 Metric literacy — what each metric and statistic means |
| 5232–5245 |    39.5.9 Gate, storage, progress view |
| 5246–5256 |    39.5.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5257–5272 |    39.5.11 Cross-phase reads and writes — the thread closes here |
| 5273–5292 |    39.5.12 The measurement thread, closed |
| 5293–5387 |  40. The five `{Phase}Output` schemas |
| 5315–5333 |   Field counts |
| 5334–5345 |   The four gate-metadata fields |
| 5346–5359 |   Three fields are on all five schemas |
| 5360–5387 |   40.1 Gate assembly |
| 5388–5471 |  41. Structured dict fields, and FMEA |
| 5410–5421 |   The grader checks every sub-field is populated |
| 5422–5430 |   `control_plan` is `dict`, never `str` |
| 5431–5439 |   `stability_assessment` is checked BEFORE capability |
| 5440–5451 |   `experiment_justification` is Tier 1 and does not require an experiment |
| 5452–5471 |   FMEA has no field in any schema, and none may be added |
| 5472–5503 |  42. Cross-phase reference fields in practice |
| 5504–5670 |  43. The coaching method |
| 5522–5549 |   43.1 The seven-step computation pattern |
| 5550–5587 |   43.2 Show before asking |
| 5588–5610 |   43.3 The A→F session flow |
| 5611–5642 |   43.4 The live gate document preview |
| 5643–5652 |   43.5 No external URLs |
| 5653–5670 |   43.6 What the coach must not do |
| 5671–6027 | Part IX — Reliability |
| 5675–5703 |   43.7 Metric literacy — the metric, and the statistic |
| 5704–5732 |  44. The failure pipeline |
| 5733–5845 |  45. Timeouts and compensating actions |
| 5740–5771 |   Per-node timeouts — required on every phase executor node |
| 5772–5781 |   Composition order — retries run BEFORE the handler |
| 5782–5791 |   Node-level error handlers — required on every node with external writes |
| 5792–5797 |   Hand-written Saga orchestrators are BANNED |
| 5798–5806 |   Two dependencies on this rule, both correctness-critical |
| 5807–5838 |   Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST** |
| 5839–5845 |   `DeltaChannel` is NOT used |
| 5846–5961 |  46. The fallback chain and circuit breakers |
| 5852–5864 |   The v2.1 four-level chain |
| 5865–5871 |   Backoff strategy is chosen per level, not globally |
| 5872–5890 |   Level 3 cache |
| 5891–5906 |   Circuit breakers — three-state, two instances |
| 5907–5913 |   Degraded mode uses actual state, never a generic error |
| 5914–5921 |   HTTP 400 is NOT a fallback case |
| 5922–5961 |   46.1 Geographic redundancy — **DEFERRED** |
| 5962–6002 |  47. Disconnect policy — what a dropped client commits |
| 5979–5985 |   Ratified policy: ABANDON, not COMPLETE |
| 5986–6002 |   Five requirements |
| 6003–6027 |  48. Structured errors |
| 6028–6516 | Part X — Operations |
| 6032–6086 |  49. API surface |
| 6038–6047 |   One runtime |
| 6048–6055 |   Async by default |
| 6056–6080 |   Endpoints |
| 6081–6086 |   Envelopes are Pydantic v2 |
| 6087–6243 |  50. UI and language rules |
| 6094–6132 |   50.1 Coach response structure |
| 6133–6144 |   Plain language always |
| 6145–6152 |   Citations |
| 6153–6166 |   Contextual feedback |
| 6167–6173 |   Connection status before the first interaction |
| 6174–6179 |   The gate review screen |
| 6180–6218 |   The live gate document |
| 6219–6230 |   The all-gate-fields tab is the contradiction backstop |
| 6231–6243 |   The conflict resolution panel |
| 6244–6319 |  51. Tracing and observability |
| 6250–6260 |   LangSmith is mandatory |
| 6261–6293 |   `@traceable` on every custom function |
| 6294–6299 |   What gets traced |
| 6300–6307 |   P50/P99 latency is a coaching quality signal |
| 6308–6319 |   Logs |
| 6320–6374 |  52. Evaluation and regression testing |
| 6326–6333 |   Built alongside the refactor, not before it |
| 6334–6340 |   The dataset is authored jointly, not generated |
| 6341–6354 |   Minimum viable suite |
| 6355–6365 |   Rubrics and the eval dataset are complementary, not duplicative |
| 6366–6374 |   Two open validation questions this suite answers |
| 6375–6516 |  53. Configuration, dependencies and deployment |
| 6381–6397 |   Fail-fast environment validation |
| 6398–6421 |   Dependency floor |
| 6422–6432 |   `/verify-current-version` is a mandatory checkpoint |
| 6433–6440 |   Infrastructure not yet provisioned |
| 6441–6452 |   Deployment layer: FastAPI, not LangGraph Server |
| 6453–6516 |   53.1 Migration sequence |
| 6517–7085 | Part XI — Governance |
| 6521–6563 |  54. Where code is allowed to live |
| 6528–6545 |   Classes are permitted ONLY in these files |
| 6546–6563 |   Target folder structure |
| 6564–6934 |  55. Anti-drift |
| 6578–6592 |   Rule numbers are load-bearing |
| 6593–6603 |   The registry guards code, not documentation |
| 6604–6609 |   Verification discipline |
| 6610–6632 |   Reference sweeps must use raw `grep -rn`, never a gitignore-filtered tool |
| 6633–6683 |   55.1 Spec-layer governance rules |
| 6684–6766 |   55.2 The BUILT markers, and the paths that oblige a re-check |
| 6767–6847 |   55.3 The phase completeness set — what one phase actually traverses |
| 6848–6897 |   55.4 Facts have one owner — the ratified minimum |
| 6898–6934 |   55.5 The commit gates govern. The rule files are advisory context. |
| 6935–7085 |  56. Amendment procedure |
| 6962–7005 |   56.0 What changed about amending, when the rules stopped being one file |
| 7006–7024 |   56.0.1 Rule, reference, and owned fact — three destinations |
| 7025–7067 |   56.1 A phase is one atomic unit — schema, validator, skill |
| 7068–7085 |   What requires an amendment rather than a routine change |
| 7086–11426 | Part XII — Specification |
| 7096–7119 |   56.2 The rule lands here; the reasoning lands in the commit |
| 7120–7153 |   56.3 The tree at HEAD is the only source of truth |
| 7154–7415 |  57. The specification layer — how to read and write a spec entry |
| 7161–7181 |   Why this Part exists |
| 7182–7197 |   The five structural rules |
| 7198–7212 |   Entry identity and traceability |
| 7213–7260 |   The entry template — three layers |
| 7261–7272 |   How gaps are marked |
| 7273–7289 |   57.1 The two calibrated samples |
| 7290–7343 |   57.2 SAMPLE 1 — CLASS TEMPLATE — S-C01 `SupervisorState` |
| 7293–7343 |    SPEC — `SupervisorState` |
| 7344–7394 |   57.3 SAMPLE 2 — FUNCTION/NODE TEMPLATE — S-F04 `phase_executor` (the coach node) |
| 7348–7394 |    SPEC — `phase_executor` (the coach node) |
| 7395–7415 |   57.4 Entry index |
| 7416–8744 |  58. Spec — graph management |
| 7426–7429 |   58.1 S-C01 · `SupervisorState` |
| 7430–7595 |   58.2 S-C02 · `PhaseState` |
| 7596–7614 |   58.3 S-C03 · Per-phase use of `PhaseState` |
| 7615–7689 |   58.4 S-C04 · `CoachingPlan` |
| 7690–7799 |   58.5 S-C05 · `CoachingResponse` |
| 7800–7851 |   58.6 S-C06 · `AzureBlobStore` |
| 7852–7897 |   58.7 S-C07 · `AzureBlobCheckpointSaver` |
| 7898–7944 |   58.8 S-C08 · `ImproveBlobClient` |
| 7945–8007 |   58.9 S-C09 · `storage/models.py` — the record models |
| 8008–8071 |   58.10 S-F01 · The supervisor graph — static edges |
| 8042–8051 |    SIPOC — at a glance |
| 8052–8071 |    Behaviors (EARS) |
| 8072–8117 |   58.11 S-F02 · `build_phase_subgraph(phase, llm)` |
| 8090–8099 |    SIPOC — at a glance |
| 8100–8117 |    Behaviors (EARS) |
| 8118–8158 |   58.12 S-F03 · `phase_planner` node |
| 8129–8138 |    SIPOC — at a glance |
| 8139–8158 |    Behaviors (EARS) |
| 8159–8170 |   58.13 S-F04 · `phase_executor` node |
| 8171–8232 |   58.14 S-F05 · `validation_stack` node |
| 8181–8190 |    SIPOC — at a glance |
| 8191–8202 |    Behaviors (EARS) |
| 8203–8232 |    ⚠ AI-ACT — high-risk surface |
| 8233–8284 |   58.15 S-F06 · `gate_review_node` |
| 8243–8252 |    SIPOC — at a glance |
| 8253–8260 |    Behaviors (EARS) |
| 8261–8284 |    ⚠ AI-ACT — high-risk surface |
| 8285–8352 |   58.16 S-F07 · `gate_apply_node` |
| 8306–8315 |    SIPOC — at a glance |
| 8316–8328 |    Behaviors (EARS) |
| 8329–8352 |    ⚠ AI-ACT — high-risk surface |
| 8353–8388 |   58.17 S-F08 · The escalation subgraph |
| 8361–8370 |    SIPOC — at a glance |
| 8371–8388 |    Behaviors (EARS) |
| 8389–8457 |   58.18 S-F09 · `analyse_executor_node` |
| 8429–8438 |    SIPOC — at a glance |
| 8439–8457 |    Behaviors (EARS) |
| 8458–8551 |   58.19 S-F10 · `define_input_mapper` |
| 8501–8513 |    SIPOC — at a glance |
| 8514–8542 |    Execution site — where a boundary mapper actually runs |
| 8543–8551 |    Behaviors (EARS) |
| 8552–8605 |   58.20 S-F11 · `define_output_mapper` |
| 8581–8590 |    SIPOC — at a glance |
| 8591–8605 |    Behaviors (EARS) |
| 8606–8655 |   58.21 S-F12 · The Measure, Analyse, Improve and Control mapper pairs |
| 8614–8623 |    SIPOC — at a glance |
| 8624–8655 |    Behaviors (EARS) |
| 8656–8744 |   58.22 S-F13 · Level 2 `Command` routing |
| 8673–8690 |    DP1 — the planner owns the field / gate decision |
| 8691–8711 |    DP2 — the validation stack's three exits |
| 8712–8732 |    DP3 — the gate exits |
| 8733–8744 |    What is settled and binds |
| 8745–9127 |  59. Spec — knowledge and retrieval |
| 8758–8787 |   59.1 S-C16 · `Hop` |
| 8788–8834 |   59.2 S-C17 · `Plan` — the hop decomposition plan |
| 8835–8871 |   59.3 S-C18 · `SynthesisOutput` |
| 8872–8888 |   59.4 S-C19 · `QueryVariants` |
| 8889–8935 |   59.5 S-F14 · `rag_lookup_methodology` |
| 8910–8919 |    SIPOC — at a glance |
| 8920–8935 |    Behaviors (EARS) |
| 8936–8983 |   59.6 S-F15 · `rag_lookup_evidence` |
| 8959–8968 |    SIPOC — at a glance |
| 8969–8983 |    Behaviors (EARS) |
| 8984–9030 |   59.7 S-F16 · `rag_lookup_case_history` |
| 9007–9016 |    SIPOC — at a glance |
| 9017–9030 |    Behaviors (EARS) |
| 9031–9081 |   59.8 S-F17 · `reciprocal_rank_fusion` |
| 9058–9067 |    SIPOC — at a glance |
| 9068–9081 |    Behaviors (EARS) |
| 9082–9127 |   59.9 S-F18 · The retriever layer — `search_knowledge`, `search_cases`, `search_evidence` |
| 9110–9127 |    SIPOC — at a glance |
| 9128–9413 |  60. Spec — tools |
| 9146–9179 |   60.1 S-F19 · `propose_template` |
| 9159–9179 |    SIPOC — at a glance |
| 9180–9218 |   60.2 S-F20 · `propose_diagram` |
| 9195–9204 |    SIPOC — at a glance |
| 9205–9218 |    Behaviors (EARS) |
| 9219–9260 |   60.3 S-F21 · `check_gate_status` |
| 9234–9243 |    SIPOC — at a glance |
| 9244–9260 |    Behaviors (EARS) |
| 9261–9296 |   60.4 S-F22 · `request_human_approval` |
| 9275–9296 |    SIPOC — at a glance |
| 9297–9313 |   60.5 S-F23 · `load_skill(name)` |
| 9314–9358 |   60.6 S-F24 · The 20 computation tools |
| 9337–9358 |    Behaviors (EARS) — binding on all twenty |
| 9359–9413 |   60.7 S-F57 · `load_evidence_series(blob_path, column)` |
| 9384–9393 |    SIPOC — at a glance |
| 9394–9413 |    Behaviors (EARS) |
| 9414–9666 |  61. Spec — the coaching agent's middleware |
| 9432–9494 |   61.1 S-C10 · `ContradictionDetectionMiddleware` |
| 9454–9463 |    Behaviors (EARS) |
| 9464–9494 |    ⚠ AI-ACT — high-risk surface |
| 9495–9536 |   61.2 S-C11 · `BeforeModelStateInjection` |
| 9508–9536 |    Behaviors (EARS) |
| 9537–9576 |   61.3 S-C12 · `DMAICSkillsMiddleware` |
| 9557–9576 |    Behaviors (EARS) |
| 9577–9613 |   61.4 S-C13 · `CoherenceMiddleware` |
| 9591–9613 |    Behaviors (EARS) |
| 9614–9649 |   61.5 S-C14 · `DMAICGraderMiddleware` |
| 9624–9649 |    Behaviors (EARS) |
| 9650–9666 |   61.6 S-C15 · `HITLInterrupt` |
| 9667–10074 |  62. Spec — validation and gates |
| 9681–9723 |   62.1 S-C20 · `CriterionVerdict` |
| 9724–9741 |   62.2 S-C21 · `GraderVerdict` |
| 9742–9755 |   62.3 S-C22 · `CoachingGraderVerdict` |
| 9756–9767 |   62.4 S-C23 · `CoherenceResult` |
| 9768–9782 |   62.5 S-C24 · `ConstraintCheckResult` / `ConstraintVerdict` |
| 9783–9795 |   62.6 S-C25 · `PolicyAdvisoryResult` |
| 9796–9832 |   62.7 S-C26 · `DMAICGateValidator` |
| 9833–9867 |   62.8 S-F25 · Layer 2c — the constraint check |
| 9842–9851 |    SIPOC — at a glance |
| 9852–9867 |    Behaviors (EARS) |
| 9868–9915 |   62.9 S-F26 · Layer 2d — the gate grader |
| 9883–9892 |    SIPOC — at a glance |
| 9893–9915 |    Behaviors (EARS) |
| 9916–9957 |   62.10 S-F27 · The policy advisory |
| 9931–9940 |    SIPOC — at a glance |
| 9941–9957 |    Behaviors (EARS) |
| 9958–10074 |   62.11 S-F28 · Gate document assembly |
| 10046–10055 |    SIPOC — at a glance |
| 10056–10074 |    Behaviors (EARS) |
| 10075–10593 |  63. Spec — the DMAIC gate documents |
| 10093–10158 |   63.1 S-C27 · `DefineOutput` |
| 10159–10199 |   63.2 S-C28 · `MeasureOutput` |
| 10200–10257 |   63.3 S-C29 · `AnalyseOutput` |
| 10258–10317 |   63.4 S-C30 · `ImproveOutput` |
| 10318–10389 |   63.5 S-C31 · `ControlOutput` |
| 10390–10456 |   63.6 S-C32 · The three cross-phase reference dicts |
| 10457–10498 |   63.7 S-C33 · The three structured dict fields |
| 10499–10537 |   63.8 S-C38 · `metric_definitions` — the project metric registry |
| 10538–10593 |   63.9 S-C39 · `phase_metrics` — the per-phase placeholder |
| 10594–10882 |  64. Spec — reliability |
| 10605–10645 |   64.1 S-C34 · `AgentImproveError` |
| 10646–10684 |   64.2 S-C35 · `CircuitBreaker` |
| 10685–10771 |   64.3 S-F29 · `phase_error_recovery` |
| 10713–10722 |    SIPOC — at a glance |
| 10723–10771 |    Behaviors (EARS) |
| 10772–10820 |   64.4 S-F30 · `degraded_mode_response` |
| 10793–10802 |    SIPOC — at a glance |
| 10803–10820 |    Behaviors (EARS) |
| 10821–10839 |   64.5 S-F31 · `synthesise_partial` |
| 10840–10864 |   64.6 S-F32 · `delete_or_flag_stale_in_case_index` |
| 10865–10882 |   64.7 S-F33 · `degraded_coaching_response` node |
| 10883–11059 |  65. Spec — API, UI and evidence |
| 10893–10913 |   65.1 S-C36 · `CitationRecord` and `CitationBundle` |
| 10914–10931 |   65.2 S-C37 · The API envelopes |
| 10932–10984 |   65.3 S-F34 · The API surface |
| 10954–10963 |    SIPOC — at a glance |
| 10964–10984 |    Behaviors (EARS) |
| 10985–11024 |   65.4 S-F35 · The upload handler |
| 11010–11024 |    Behaviors (EARS) |
| 11025–11059 |   65.5 S-F36 · The `improve_case_index` write path |
| 11060–11070 |  66. The SPEC-GAP register — MOVED |
| 11071–11164 |  67. EU AI Act compliance posture |
| 11078–11093 |   67.1 The deadlines are now fixed |
| 11094–11119 |   67.2 The classification question — open, and not answered here |
| 11120–11137 |   67.3 The eight core provider obligations |
| 11138–11148 |   67.4 One compliance finding is already recorded in this document |
| 11149–11164 |   67.5 Compliance-source discipline |
| 11165–11245 |  68. The DORA-structured compliance risk register |
| 11172–11189 |   68.1 Why DORA structure |
| 11190–11206 |   68.2 The register |
| 11207–11230 |   68.3 Pending classification — not register rows |
| 11231–11245 |   68.4 The infrastructure risk already on record |
| 11246–11426 |  69. Spec — computation tools |
| 11275–11346 |   69.1 Common conventions — stated once, binding on all twenty |
| 11347–11352 |   69.2 S-F37 · Define — 1 tool |
| 11353–11365 |   69.3 S-F38–S-F45 · Measure — 8 tools |
| 11366–11375 |   69.4 S-F46–S-F50 · Analyse — 5 tools |
| 11376–11381 |   69.5 S-F51 · Improve — 1 tool |
| 11382–11399 |   69.6 S-F52–S-F56 · Control — 5 tools |
| 11400–11426 |   69.7 The Measure control-chart boundary — a tool that is deliberately absent |
| 11427–11655 | Appendices |
| 11431–11446 |  Appendix A — Provenance index |
| 11437–11440 |   A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference |
| 11441–11446 |   A.2 `agent-improve/ARCHITECTURE.md` → this reference |
| 11447–11477 |  Appendix B — Deferred backlog |
| 11478–11543 |  Appendix C — Trusted sources |
| 11484–11503 |   Tier 1 — current, authoritative |
| 11504–11522 |   Tier 1 — compliance |
| 11523–11526 |   Tier 2 — official announcements |
| 11527–11530 |   Tier 3 — informed practitioner, cross-check before citing |
| 11531–11537 |   Downgraded — historical |
| 11538–11543 |   Excluded |
| 11544–11623 |  Appendix D — Retired names, banned patterns, and exclusions |
| 11546–11568 |   D.1 Retired names — never reintroduce |
| 11569–11612 |   D.2 Banned patterns |
| 11613–11623 |   D.3 Architecturally excluded — not deferred |
| 11624–11632 |  Appendix E — Current state |
| 11633–11655 |  Appendix F — The v2.2.16 registers |
| 11639–11644 |   F.1 Decisions Resolved (v2.2) — the former §17 |
| 11645–11655 |   F.2 Change Log — the former §18 |
| 11649–11655 |    F.2.1 Amendment procedure — the former §18.1 |

## `agent-improve/docs/REFACTORING_PROCEDURE.md` — 5243 lines

| Lines | Heading |
|---|---|
| 1–292 | Agent Improve — Refactoring Procedure |
| 9–19 |  ⚑ STATUS BANNER — 2026-08-27 · the phase specs are now RATIFIED INPUTS |
| 20–163 |  About this document |
| 38–46 |   The three-document division |
| 47–55 |   How to use it |
| 56–73 |   The completion contract |
| 74–100 |   The drift defences on the spine |
| 101–122 |   Verification owed, and by which steps |
| 123–134 |   Numbering |
| 135–143 |   Reading conventions |
| 144–163 |   Verification vocabulary |
| 164–233 |  ⚑ THE WORKING METHOD — ratified 2026-09-23 |
| 169–181 |   1 — The capability register is the unit of progress |
| 182–196 |   2 — Every step declares NEEDS and GIVES |
| 197–201 |   3 — Test first, and the whole set |
| 202–218 |   4 — No build without a specification |
| 219–224 |   5 — Admission: a finding becomes a step only if it blocks a step in flight |
| 225–233 |   6 — A mutation proof neuters the PRODUCER, never the stored value |
| 234–260 |  ⚑ WHAT "DEFINE COMPLETE" MEANS — the definition the vertical is measured against |
| 261–292 |  ⚑ THE DEFINE CRITICAL PATH — sequenced 2026-09-23 |
| 293–343 | Part 0 — Preconditions and gates |
| 297–305 |  0.1 What must be true before step 2.3 |
| 306–325 |  0.2 Standing gates |
| 326–343 |  0.3 What "current codebase" means |
| 344–461 | Part 1 — Stage 2: Foundation hygiene |
| 351–381 |  0.4 Mutation proofs — restore from OUTSIDE the tree, never from HEAD |
| 382–397 |  Step 2.3 — Dependency upgrade |
| 398–413 |  Step 2.4 — `set_entry_point` → `add_edge(START, …)` |
| 414–429 |  Step 2.5 — Async conversion |
| 430–445 |  Step 2.6 — `response.content` → `content_blocks` · 20 sites |
| 446–461 |  Step 2.7 — LLM factory: class → functions, 6 roles → 11 |
| 462–532 | Part 2 — Stage 3: State and persistence |
| 466–481 |  Step 3.1 — `SupervisorState` and `PhaseState` |
| 482–498 |  Step 3.2 — `AzureBlobStore` |
| 499–515 |  Step 3.3 — Boundary mappers |
| 516–532 |  Step 3.4 — `{Phase}PhaseInput` → `{Phase}Output` schemas, with validators and UI |
| 533–636 | Part 3 — Stage 4: The graph |
| 551–568 |  Step 3.5 — `storage/blob.py`: `ImproveBlobClient` class → functions, sync → aio |
| 569–584 |  Step 4.1 — The Define phase subgraph |
| 585–603 |  Step 4.2 — `thread_id` through `graph.ainvoke`, and the disconnect policy |
| 604–620 |  Step 4.3 — The supervisor graph |
| 621–636 |  Step 4.4 — The remaining four phase subgraphs |
| 637–704 | Part 4 — Stage 5: Retrieval and tools |
| 641–656 |  Step 5.1 — Retrieval failure semantics |
| 657–673 |  Step 5.2 — Three `rag_lookup_*` tools with multi-query + RRF |
| 674–689 |  Step 5.3 — The 20 computation tools |
| 690–704 |  Step 5.4 — Per-phase tool binding |
| 705–1755 | Part 5 — Stage 6: The coaching agent |
| 709–723 |  Step 6.1 — Planner / Executor split |
| 724–738 |  Step 6.2 — `create_agent` executor with `CoachingResponse` |
| 739–750 |  Step 6.3 — Middleware positions 1–3 |
| 751–768 |  Step 6.4 — Retry middleware, positions 4–5 · and the factory hardcoded-retry removal |
| 769–780 |  Step 6.5 — Middleware positions 6–8 |
| 781–798 |  Step 6.6 — Prompts |
| 799–816 |  Step 6.7 — The hop cap, as §26 specifies it (WATCH 26) |
| 817–833 |  Step 6.8 — `phase_context` is read (WATCH 19) |
| 834–849 |  Step 6.9 — The four missing SKILL.md files, and §32 conformance |
| 850–897 |  Step 6.10 — `analyse_executor_node` — §26's planned multi-hop |
| 898–921 |  Step 6.11 — The upload path (G-36) |
| 922–940 |  Step 6.12 — Ask-binding: an upload answers a request |
| 941–964 |  Step 6.13 — The evidence index migration |
| 965–1056 |  Step 6.14 — The SKILL.md shape pass: Define, Analyse, Improve, Control |
| 986–998 |   What this step is |
| 999–1013 |   The mechanism, which is NOT in question |
| 1014–1044 |   What the founder owes, and it is the whole content of this step |
| 1045–1056 |   Done when |
| 1057–1159 |  Step 6.17 — The count-check: a written count against the list it describes |
| 1069–1110 |   The defect this closes |
| 1111–1121 |   Not the same check as `verify_built.py`, and the boundary is the point |
| 1122–1149 |   What to assert |
| 1150–1159 |   Done when |
| 1160–1241 |  Step 6.22 — The order-check: the middleware stack's ordering test observes execution (G-52) |
| 1169–1186 |   The defect this closes |
| 1187–1206 |   What to build |
| 1207–1241 |   Done when |
| 1242–1326 |  Step 6.23 — The source-method check: verification against the installed object, not the page (G-54) |
| 1251–1275 |   The defect this closes |
| 1276–1319 |   What to build |
| 1320–1326 |   Done when |
| 1327–1377 |  Step 6.24 — The drift hook learns to read the documents (G-56) |
| 1336–1353 |   The gap this closes |
| 1354–1370 |   What to build |
| 1371–1377 |   Done when |
| 1378–1396 |  Step 6.25 — Scratch leaves the tree |
| 1387–1396 |   Done when |
| 1397–1414 |  Step 6.26 — The guard's tree rules get a test suite (G-57) |
| 1406–1414 |   Done when |
| 1415–1438 |  Step 6.27 — The watched-path contract has one owner (G-58) |
| 1424–1438 |   Done when |
| 1439–1498 |  Step 6.28 — Fact-ownership moves to the commit gate (G-59, G-60) |
| 1448–1465 |   The gap this closes |
| 1466–1491 |   What to build |
| 1492–1498 |   Done when |
| 1499–1540 |  Step 6.29 — Search index schema ownership, ruled (G-60) |
| 1508–1515 |   Why this is a step and not a sentence |
| 1516–1533 |   The ruling to make |
| 1534–1540 |   Done when |
| 1541–1588 |  Step 6.30 — A commit body's code claims carry a resolvable reference (G-62) |
| 1550–1559 |   The ruling |
| 1560–1573 |   The worked case |
| 1574–1581 |   The known limit, recorded with the ruling |
| 1582–1588 |   Done when |
| 1589–1615 |  Step 6.31 — The build matrix: one row per step, anchored to a symbol |
| 1616–1647 |  Step 6.32 — An out-of-band landing gets the lane it earned (G-65) |
| 1648–1689 |  Step 6.16 — The board is generated, not written |
| 1657–1660 |   1 — Appendix D gains two columns |
| 1661–1664 |   2 — `ARCHITECTURE_STATUS.md` gets a parseable closer — **read as: the BUILT markers do** |
| 1665–1668 |   3 — The generator: `.claude/hooks/build_board.py` |
| 1669–1672 |   4 — Lane assignment is DERIVED, never declared |
| 1673–1676 |   5 — Wired into `.githooks/pre-commit`, fail-SOFT |
| 1677–1689 |   6 — `docs/board.html` joins the watched paths |
| 1690–1710 |  Step 6.18 — The executor ignores the tool its own planner names (G-49) |
| 1711–1731 |  Step 6.19 — `CoachingResponse` gains §50.1's four presentational fields (G-50) |
| 1732–1755 |  Step 6.20 — The write paths: `computation_results`, `phase_metrics`, `field_index` |
| 1756–2191 | Part 6 — Stage 7: Validation and gates |
| 1760–1784 |  Step 6.21 — The plan reaches the model (G-49's fix) |
| 1785–1819 |  Step 7.0 — The evaluation suite (§52) |
| 1820–1878 |  Step 7.1 — `DMAICGateValidator` and Layer 2b |
| 1879–1930 |  Step 7.2 — Layers 2c and 2d, and the `validation_stack` node |
| 1931–2100 |  Step 7.3 — The nine-step HITL gate |
| 2101–2113 |  Step 7.4 — Two tiers and the `warning` verdict |
| 2114–2126 |  Step 7.5 — Escalation |
| 2127–2156 |  Step 7.7 — The approve endpoint |
| 2157–2191 |  Step 7.8 — The gate steps that consume validation results |
| 2192–2402 | Part 7 — Stage 8: Reliability |
| 2196–2212 |  Step 7.9 — Define end to end, on one fresh case |
| 2213–2272 |  Step 7.6 — The re-approval cascade (§37) |
| 2273–2309 |  Step 8.0 — Turn telemetry and `@traceable` (§51) |
| 2310–2324 |  Step 8.1 — Structured errors |
| 2325–2346 |  Step 8.2 — Per-node timeouts and compensating actions |
| 2347–2363 |  Step 8.3 — Circuit breakers and the fallback chain |
| 2364–2379 |  Step 8.4 — Level 3 response cache |
| 2380–2402 |  Step 8.5 — Graceful shutdown |
| 2403–2573 | Part 8 — Stage 9: Azure schema changes |
| 2407–2429 |  Step 8.6 — Context recovery (§44 Step 2) |
| 2430–2458 |  Step 8.7 — `delete_blob`, and the upload lifecycle (WATCH 10) |
| 2459–2510 |  Step 9.0 — Knowledge-index rebuild |
| 2511–2573 |  Step 9.1 — The Azure batched reindex, case index only |
| 2574–3766 | Part 9 — Stage 10: API and UI |
| 2578–2618 |  Step 9.2 — The premium deployment's quota, on the coach's own model call (G-53) |
| 2587–2599 |   The condition this clears |
| 2600–2612 |   Why it is registered rather than tolerated |
| 2613–2618 |   Done when |
| 2619–2645 |  Step 6.36 — The register's readers read either document |
| 2629–2645 |   Done when |
| 2646–2672 |  Step 6.37 — The repartition — the operational register moves to the procedure |
| 2656–2672 |   Done when |
| 2673–2693 |  Step 6.38 — The dual-read is removed — one register, one reader |
| 2683–2693 |   Done when |
| 2694–2715 |  Step 6.41 — The symbol-anchor ratchet comes down (G-87) |
| 2704–2715 |   Done when |
| 2716–2736 |  Step 6.39 — The spec-entry population joins the register (assertion 5) |
| 2726–2736 |   Done when |
| 2737–2757 |  Step 6.40 — Every section declares a row or declares itself not-markable (assertion 7) |
| 2747–2757 |   Done when |
| 2758–2778 |  Step 6.35 — The hop cap matches the ceiling that was always in force (G-83) |
| 2779–2801 |  Step 6.34 — A node that runs out of time answers the Belt instead of failing (G-84) |
| 2802–2825 |  Step 6.33 — The capture path accumulates — a field survives the next turn |
| 2826–2848 |  Step 6.42 — The gate document records what Define established |
| 2849–2889 |  Step 6.43 — The coach can read an uploaded document |
| 2890–2953 |  Step 6.44 — The contradiction stop moves from middleware into a node |
| 2954–2988 |  Step 6.45 — The planner decides on field completeness |
| 2989–3009 |  Step 6.46 — The coaching script is guaranteed to reach the model, or its absence is recorded |
| 3010–3036 |  Step 6.47 — Durable writes inside a node, and persistence loss is never silent |
| 3037–3058 |  Step 6.48 — A captured value carries its declared type |
| 3059–3081 |  Step 6.49 — The checks card — twelve capability rows get the check that proves them |
| 3082–3131 |  Step 6.51 — The baseline and the target are values Control can compare |
| 3132–3154 |  Step 6.52 — A turn always answers inside its budget |
| 3155–3176 |  Step 6.54 — The clients are built once, at startup, before any Belt waits for them |
| 3177–3216 |  Step 6.56 — The coaching proof: positions 1–8 of Define, one traced run |
| 3217–3238 |  Step 6.57 — The Belt's step is computed, not counted by the model |
| 3239–3260 |  Step 6.63 — The control board is a true picture of the tree |
| 3261–3289 |  Step 6.66 — The long-running harness: one feature list, status only from tests |
| 3290–3309 |  Step 6.65 — Speed without losing quality |
| 3310–3334 |  Step 6.64 — The board's grouped views are restored, derived |
| 3335–3360 |  Step 6.61 — The coaching move is decided in code |
| 3361–3379 |  Step 6.62 — The other four phase scripts carry no move-sequencing |
| 3380–3404 |  Step 6.58 — A percent convention for the computation tools |
| 3405–3437 |  Step 6.59 — The coherence judge rules on the Belt's words, not the coach's |
| 3438–3477 |  Step 6.53 — A coherence rejection asks the coach again |
| 3478–3497 |  Step 6.60 — The script already delivered is not fetched again |
| 3498–3604 |  Step 6.50 — The conformance pass — the tree against the framework's own documentation |
| 3544–3581 |   The five mechanisms the first run must cover |
| 3582–3604 |   It runs at a cadence, and it reports |
| 3605–3632 |  Step 10.0 — The coaching turn’s output reaches the Belt — four blocks and the grader’s warning |
| 3633–3645 |  Step 10.1 — `/ask/stream` SSE |
| 3646–3689 |  Step 10.2 — The live gate document, conflict panel, and tier bars |
| 3690–3739 |  Step 10.3 — The workspace reads the v2 field names, and progress counts them |
| 3740–3766 |  Step 10.4 — The error contract — a failed turn is readable |
| 3767–3825 | Part 10 — Stage 11: Cleanup and governance |
| 3771–3793 |  Step 11.1 — Delete v1 |
| 3794–3825 |  Step 11.2 — Governance close-out |
| 3826–5009 | Appendices |
| 3832–3847 |  Change log |
| 3848–3862 |  Step board |
| 3863–3955 |  Appendix A — Traceability matrix |
| 3934–3955 |   Coverage check against Reference §53.1 |
| 3956–3977 |  Appendix B — Disposition of the 55 backend files |
| 3978–3993 |  Appendix C — The two parallel workstreams |
| 3994–4219 |  Appendix D — Step index |
| 4073–4219 |   The bands — what the Seq ranges mean |
| 4220–4761 |  Appendix F — The build matrix |
| 4241–4263 |   The columns |
| 4264–4304 |   The anchor grammar — never a line number |
| 4305–4681 |   Layers — nine, not eight |
| 4313–4342 |    L0 · Governance and build tooling |
| 4343–4373 |    L1 · API surface |
| 4374–4405 |    L2 · Supervisor graph |
| 4406–4456 |    L3 · Phase subgraphs |
| 4457–4509 |    L4 · Coaching agent |
| 4510–4531 |    L5 · Middleware |
| 4532–4587 |    L6 · Tools and knowledge |
| 4588–4636 |    L7 · Validation, gates, escalation |
| 4637–4681 |    L8 · Persistence and cross-cutting |
| 4682–4727 |   The Define path — estimate and epic (founder, 2026-09-25) |
| 4728–4761 |   Wiring proofs |
| 4762–5009 |  Appendix G — The SPEC-GAP register |
| 4815–4824 |   66.1 Group A — founder ruling required |
| 4825–4904 |   66.2 Group B — cross-check defects |
| 4905–4920 |   66.3 Group C — schemas named but never defined |
| 4921–4942 |   66.4 Group D — described in prose, no interface |
| 4943–4949 |   66.5 Group E — content the build sequence defers |
| 4950–4968 |   66.6 Closed |
| 4969–4999 |   66.7 Findings — recorded, not gaps |
| 5000–5009 |   66.8 The Supplier/Customer cross-check — first run, 2026-08-23 |
| 5010–5243 | Part XIII — Compliance and Risk |
| 5020–5174 |  Appendix H — The capability register |
| 5027–5088 |   The contract |
| 5089–5101 |   How it differs from Appendix F, which it does not replace |
| 5102–5174 |   ✅ THE SEED HAS LANDED — all 35 of Define's rows are written |
| 5175–5232 |  Appendix I — The plan: epics, stories and rank |
| 5183–5195 |   The rule |
| 5196–5226 |   ✅ THE FILE IS IN THE TREE, AND THE PRE-COMMIT HOOK READS IT — 2026-09-23 |
| 5227–5232 |   The run of work — superseded 2026-09-25 |
| 5233–5243 |  Appendix E — Questions raised by this procedure · BOTH RESOLVED |
