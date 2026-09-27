# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 11667 lines

| Lines | Heading |
|---|---|
| 27–49 |  🗺 Where state lives — a MAP, not a definition |
| 50–258 | Agentic Architecture Reference |
| 153–258 |  About this document |
| 159–216 |   Scope — three agents, one architecture |
| 217–231 |   The two-document division |
| 232–246 |   Section numbering and provenance |
| 247–258 |   Reading conventions |
| 259–550 | Part I — Orientation |
| 263–339 |  1. What Agent Improve is |
| 283–309 |   What makes it architecturally distinctive |
| 310–339 |   The runtime stack |
| 340–391 |  2. How to read this document |
| 346–362 |   By what you are trying to do |
| 363–391 |   Canonical ownership |
| 392–490 |  3. Terminology |
| 403–419 |   Structural primitives |
| 420–431 |   Role labels |
| 432–449 |   The recursion is two levels, not infinite |
| 450–464 |   "Harness" — two senses, do not conflate |
| 465–475 |   "Agent" — used carefully |
| 476–490 |   Things that are deliberately not levels |
| 491–550 |  4. Architecture at a glance |
| 534–550 |   The five things that shape everything else |
| 551–1278 | Part II — State and Persistence |
| 558–616 |  5. `SupervisorState` — orchestration only |
| 570–576 |   `gate_passed` is a dict, not a list |
| 577–588 |   `current_phase` and `phase_index` are derived, and kept anyway |
| 589–608 |   Four fields were removed as redundant, and may not return |
| 609–616 |   Artifacts are not here |
| 617–852 |  6. `PhaseState` — per-phase subgraph state |
| 632–663 |   `asks` — §56 AMENDMENT, ratified 2026-09-09 |
| 664–733 |   `field_log` — §56 AMENDMENT, ratified 2026-09-21 |
| 734–739 |   `draft`, `belt_edits` and `final` are `dict`, never `str` |
| 740–762 |   `coaching_plan` is one typed plan, not a queue |
| 763–778 |   `gate_attempts` — the field whose absence recreated a production bug |
| 779–799 |   `validator_feedback` and `belt_edits` are different, and must stay separate |
| 800–817 |   `citations` and `uploads` — the evidence trail |
| 818–835 |   `hop_results` and `synthesis_output` must be state, not node locals |
| 836–844 |   Per-phase variants |
| 845–852 |   Naming discipline |
| 853–929 |  7. Field typing law — every captured field is a string |
| 869–881 |   Why strings |
| 882–901 |   The one exception — three cross-phase reference dicts |
| 902–929 |   Computation results |
| 930–1022 |  8. The checkpointer / store split |
| 954–973 |   Phased backend |
| 974–985 |   Concurrency and atomicity |
| 986–1001 |   Why Blob, and not Cosmos / Tables / SQLite |
| 1002–1022 |   On-blob checkpoint format |
| 1023–1159 |  9. The Store — cross-phase artifacts and boundary mappers |
| 1064–1087 |   Namespace convention |
| 1088–1117 |   Why cross-phase data cannot travel on parent state |
| 1118–1138 |   Boundary mappers |
| 1139–1151 |   Two prohibitions that follow |
| 1152–1159 |   Ordering constraint |
| 1160–1217 |  10. Azure Blob — two distinct concerns |
| 1179–1204 |   Complete physical layout |
| 1205–1217 |   The case blob is not updated per turn |
| 1218–1278 |  11. `step_log` — the audit trail |
| 1239–1248 |   `artifacts` and `step_log` are separate fields and stay separate |
| 1249–1278 |   Entries carry deterministic keys, never a raw timestamp as identity |
| 1279–1649 | Part III — The Graph |
| 1285–1325 |  12. Topology |
| 1315–1325 |   The subgraph builder takes the phase as a parameter |
| 1326–1465 |  13. The phase subgraph — five nodes |
| 1403–1433 |   The subgraph is a cycle, not a pipeline |
| 1434–1446 |   Two node names are BANNED |
| 1447–1452 |   Leaf tools are NOT subgraph nodes |
| 1453–1465 |   The validation stack and the policy advisory are NOT tools |
| 1466–1501 |  14. Node contract |
| 1489–1501 |   Reflection is a node, not a private function |
| 1502–1566 |  15. Routing — static edges and `Command` |
| 1508–1525 |   The decision test |
| 1526–1531 |   Never mix static edges and `Command` from the same node |
| 1532–1559 |   Level 1 does not route — it advances |
| 1560–1566 |   No subgraph imports another subgraph's nodes |
| 1567–1649 |  16. `thread_id`, `checkpoint_ns`, and where persistence attaches |
| 1573–1588 |   One `thread_id` per project |
| 1589–1602 |   The checkpointer and store go on the parent graph ONLY |
| 1603–1629 |   The wrapper node must invoke the subgraph directly (G-44) |
| 1630–1649 |   `recursion_limit` is a backstop, not the hop cap |
| 1650–2391 | Part IV — The Coaching Agent |
| 1656–1770 |  17. The Planner / Executor contract |
| 1732–1762 |   `CoachingPlan` |
| 1763–1770 |   Extraction is structured output, not a node and not a tool |
| 1771–1818 |  18. Building the executor — `create_agent` |
| 1783–1790 |   Binding tools directly onto a bare model is a violation |
| 1791–1796 |   `create_react_agent` is superseded |
| 1797–1809 |   deepagents is not a dependency |
| 1810–1818 |   The structured response and the coaching text coexist |
| 1819–2140 |  19. The middleware stack — eight, in order |
| 1841–1887 |   Ordering rules that bind |
| 1888–1899 |   Three independent retry caps |
| 1900–1943 |   19.1 `BeforeModelStateInjection` — injection timing |
| 1944–1959 |   19.2 `DMAICSkillsMiddleware` — progressive disclosure |
| 1960–1999 |   19.3 `SummarizationMiddleware` — context compression |
| 2000–2026 |   19.4 `ModelRetryMiddleware` — API-level retry |
| 2027–2039 |   19.5 `ToolRetryMiddleware` — tool-level retry |
| 2040–2062 |   19.6 `ContradictionDetectionMiddleware` — the mid-phase check |
| 2063–2097 |   19.7 `CoherenceMiddleware` — validation Layer 2a |
| 2098–2128 |   19.8 `DMAICGraderMiddleware` — coaching process quality |
| 2129–2140 |   19.9 Middleware deliberately NOT used |
| 2141–2215 |  20. `CoachingResponse` — the per-turn schema |
| 2195–2198 |   The executor node writes the response into state |
| 2199–2205 |   The executor's `response_format` is `CoachingResponse`, never a phase Output |
| 2206–2215 |   What structured output does NOT give you |
| 2216–2327 |  21. LLM roles, temperature, and the factory |
| 2236–2244 |   Factory only |
| 2245–2265 |   Roles |
| 2266–2282 |   Temperature |
| 2283–2327 |   Structured output — scoped by call type |
| 2328–2391 |  22. Prompts |
| 2354–2374 |   The memory hierarchy paragraph is mandatory |
| 2375–2391 |   Anti-hallucination guards are mandatory |
| 2392–3170 | Part V — Knowledge and Retrieval |
| 2396–2751 |  23. The three indexes |
| 2408–2458 |   23.1 `improve_knowledge_index` — methodology |
| 2459–2584 |   23.2 `improve_evidence_index` — Belt-uploaded evidence |
| 2504–2528 |    Supersession deletes; it does not flag |
| 2529–2584 |    Two Azure behaviours govern the migration |
| 2585–2657 |   23.2.1 The `role` vocabulary — ratified, not invented per phase |
| 2624–2657 |    `unclassified (pre-ask-binding)` is a MIGRATION SENTINEL, not a thirteenth role |
| 2658–2706 |   23.3 `improve_case_index` — case records (cross-case memory) |
| 2707–2717 |   The internal phase key is `analyse`, never `analyse_phase` |
| 2718–2742 |   23.4 The write-path trap that made `phase_relevance` unfilterable |
| 2743–2751 |   23.5 Schema change procedure |
| 2752–2880 |  24. The three `rag_lookup_*` tools |
| 2770–2827 |   `rag_lookup_evidence` returns a structured record, not rendered text |
| 2828–2840 |   RAG via tool, never via prepended system message |
| 2841–2865 |   The retrieval mechanism |
| 2866–2873 |   `belt_level` filtering is OFF by default |
| 2874–2880 |   `source_file` and `page_number` are returned, never filtered |
| 2881–2946 |  25. Multi-query and Reciprocal Rank Fusion |
| 2890–2906 |   Why it is mandatory |
| 2907–2913 |   The implementation |
| 2914–2935 |   `MultiQueryRetriever` and `EnsembleRetriever` are BANNED |
| 2936–2946 |   Encapsulation |
| 2947–3080 |  26. Multi-hop retrieval |
| 2962–2998 |   The hop cap is `RemainingSteps` |
| 2999–3017 |   Per-phase policy |
| 3018–3062 |   Planned multi-hop — the Analyse pipeline |
| 3063–3080 |   **UNVERIFIED** — planned multi-hop is Analyse-only |
| 3081–3127 |  27. Retrieval failure semantics |
| 3092–3100 |   Never wrap a retrieval call in a bare `except Exception` returning `[]` |
| 3101–3110 |   Three rules that each have already bitten |
| 3111–3127 |   The coach-facing message must not read as absence |
| 3128–3170 |  28. Memory taxonomy |
| 3146–3170 |   The static/dynamic split is the part that matters |
| 3171–3517 | Part VI — Tools |
| 3175–3332 |  29. The data channel and the universal eight |
| 3181–3216 |   29.1 There is no MCP — the data-channel decision |
| 3217–3259 |   29.2 The universal eight |
| 3225–3259 |    `load_evidence_series` joins the set — RATIFIED 2026-09-09 |
| 3260–3269 |   29.3 `record_field` is RETIRED and may not be reintroduced |
| 3270–3332 |   29.4 Cross-agent tools — a third category, present but NOT BOUND |
| 3333–3407 |  30. Computation tools and per-phase binding |
| 3338–3375 |   Tool sets are per phase, not universal |
| 3376–3381 |   Each of the 20 is a separate named tool |
| 3382–3390 |   All 20 are pure functions |
| 3391–3400 |   `imr_chart_limits` — the choice that is usually wrong by default |
| 3401–3407 |   Tool decisions are the model's, not the graph's |
| 3408–3440 |  31. Tool arg schemas and docstrings |
| 3414–3419 |   Every `@tool` uses `args_schema=` |
| 3420–3440 |   Docstrings are interface, not commentary |
| 3441–3517 |  32. Phase skills — SKILL.md |
| 3464–3468 |   Each skill's `allowed-tools` MUST match that phase's subset in §30 |
| 3469–3478 |   Progressive disclosure — three levels |
| 3479–3484 |   Storage backend: `FilesystemBackend` |
| 3485–3506 |   Each SKILL.md must carry |
| 3507–3517 |   Two distinct kinds of skill exist in this repository |
| 3518–4098 | Part VII — Validation and Gates |
| 3525–3645 |  33. The nine-step HITL gate |
| 3546–3559 |   Two quality checks, two actors, two moments |
| 3560–3571 |   Gates are one-way doors, with exactly one defined exception |
| 3572–3576 |   Implementation: graph-level `interrupt()` |
| 3577–3607 |   33.1 The two-node split |
| 3608–3637 |   33.2 `gate_apply_node` writes the gate document TWICE |
| 3638–3645 |   33.3 The checkpoint commits only after Belt approval |
| 3646–3749 |  34. The four-layer validation stack |
| 3661–3668 |   Layer 2a is middleware; layers 2b–2d are the node |
| 3669–3675 |   Layer 2d is NOT `DMAICGraderMiddleware` |
| 3676–3681 |   Run cheapest first |
| 3682–3691 |   The counter and the feedback |
| 3692–3701 |   Layer 2b is the only deterministic layer, deliberately |
| 3702–3713 |   Per-phase constraint sets |
| 3714–3723 |   34.1 Where each check fires |
| 3724–3749 |   34.2 The self-healing hierarchy and the transparency principle |
| 3750–3885 |  35. Two tiers of field, and the `warning` verdict |
| 3756–3770 |   The problem this solves |
| 3771–3787 |   Three distinct things check these fields, and conflating them is a design error |
| 3788–3836 |   Gate-required fields by phase |
| 3837–3853 |   The grader's verdict has three statuses |
| 3854–3861 |   Why two tiers |
| 3862–3885 |   The grader is belt-level aware |
| 3886–3979 |  36. Two graders — and why they are not redundant |
| 3905–3918 |   Why both exist |
| 3919–3942 |   `COACHING_QUALITY_RUBRIC` |
| 3943–3952 |   Mechanism, both graders |
| 3953–3962 |   Three criteria are verified deterministically, not by judgment |
| 3963–3979 |   The ratified rubric coverage |
| 3980–4076 |  37. Mid-phase contradiction and the re-approval cascade |
| 3986–4007 |   The check runs every turn, not only at gates |
| 4008–4041 |   §37 governs a GATE-COMMITTED value only |
| 4042–4055 |   There is NO tolerance threshold, and none may be added |
| 4056–4063 |   The re-approval cascade |
| 4064–4076 |   The cascade has a hard dependency on compensating actions |
| 4077–4098 |  38. Escalation |
| 4099–5679 | Part VIII — The DMAIC Domain |
| 4106–5300 |  39. The five phases |
| 4124–4138 |   The measurement thread that runs across three phases |
| 4139–4373 |   39.1 Define phase, complete specification |
| 4146–4153 |    39.1.1 Purpose |
| 4154–4216 |    39.1.2 The ordered field list — the `field_index` sequence (closes G-38) |
| 4217–4231 |    39.1.3 The composed-problem-statement rule (binding) |
| 4232–4246 |    39.1.4 The `team` structure |
| 4247–4256 |    39.1.5 SIPOC handling |
| 4257–4268 |    39.1.6 Gate, storage, progress view |
| 4269–4287 |    39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4288–4294 |    39.1.8 The other four phases |
| 4295–4327 |    39.1.9 The metric registry and Define's placeholder |
| 4328–4335 |    39.1.10 Tools bound to Define |
| 4336–4343 |    39.1.11 Conditions — routing and the gate |
| 4344–4351 |    39.1.12 State parameters — Define's use of `PhaseState` |
| 4352–4359 |    39.1.13 Metric literacy — what each metric means |
| 4360–4373 |    39.1.14 Cross-phase reads and writes |
| 4374–4629 |   39.2 Measure phase, complete specification |
| 4384–4392 |    39.2.1 Purpose |
| 4393–4415 |    39.2.2 The ordered field list — the `field_index` sequence |
| 4416–4476 |    39.2.3 The metric registry and Measure's placeholder |
| 4477–4496 |    39.2.4 SIPOC → the detailed process map |
| 4497–4518 |    39.2.5 Tools bound to Measure |
| 4519–4548 |    39.2.6 Conditions — sequence locks, routing, and the gate |
| 4549–4566 |    39.2.7 State parameters — Measure's use of `PhaseState` |
| 4567–4583 |    39.2.8 Metric literacy — what each metric means |
| 4584–4597 |    39.2.9 Gate, storage, progress view |
| 4598–4606 |    39.2.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4607–4623 |    39.2.11 Cross-phase reads and writes |
| 4624–4629 |    39.2.12 The other two phases |
| 4630–4859 |   39.3 Analyse phase, complete specification |
| 4640–4649 |    39.3.1 Purpose |
| 4650–4675 |    39.3.2 The ordered field list — the `field_index` sequence |
| 4676–4712 |    39.3.3 The metric registry and Analyse's placeholder (linkage form — closes F-13) |
| 4713–4732 |    39.3.4 Two movements — generate, then validate |
| 4733–4755 |    39.3.5 Tools bound to Analyse |
| 4756–4784 |    39.3.6 Conditions — methodology guards, routing, and the gate |
| 4785–4798 |    39.3.7 State parameters — Analyse's use of `PhaseState` |
| 4799–4814 |    39.3.8 Metric literacy — what each metric and statistic means |
| 4815–4826 |    39.3.9 Gate, storage, progress view |
| 4827–4835 |    39.3.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4836–4853 |    39.3.11 Cross-phase reads and writes |
| 4854–4859 |    39.3.12 The other phase |
| 4860–5062 |   39.4 Improve phase, complete specification |
| 4870–4878 |    39.4.1 Purpose |
| 4879–4899 |    39.4.2 The ordered field list — the `field_index` sequence |
| 4900–4918 |    39.4.3 The metric registry and Improve's placeholder (linkage form) |
| 4919–4936 |    39.4.4 Two movements — generate-and-select, then pilot-and-prove |
| 4937–4955 |    39.4.5 Tools bound to Improve |
| 4956–4987 |    39.4.6 Conditions — methodology guards, DOE belt-gating, routing, gate |
| 4988–5001 |    39.4.7 State parameters — Improve's use of `PhaseState` |
| 5002–5015 |    39.4.8 Metric literacy — what each metric and statistic means |
| 5016–5027 |    39.4.9 Gate, storage, progress view |
| 5028–5037 |    39.4.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5038–5054 |    39.4.11 Cross-phase reads and writes |
| 5055–5062 |    39.4.12 The last phase |
| 5063–5300 |   39.5 Control phase, complete specification |
| 5073–5081 |    39.5.1 Purpose |
| 5082–5110 |    39.5.2 The ordered field list — the `field_index` sequence |
| 5111–5140 |    39.5.3 The metric registry, the comparison, and single authority (closes F-14) |
| 5141–5157 |    39.5.4 Two movements — confirm it held, then lock it in |
| 5158–5177 |    39.5.5 Tools bound to Control |
| 5178–5210 |    39.5.6 Conditions — guards, routing, gate |
| 5211–5224 |    39.5.7 State parameters — Control's use of `PhaseState` |
| 5225–5239 |    39.5.8 Metric literacy — what each metric and statistic means |
| 5240–5253 |    39.5.9 Gate, storage, progress view |
| 5254–5264 |    39.5.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5265–5280 |    39.5.11 Cross-phase reads and writes — the thread closes here |
| 5281–5300 |    39.5.12 The measurement thread, closed |
| 5301–5396 |  40. The five `{Phase}Output` schemas |
| 5324–5342 |   Field counts |
| 5343–5354 |   The four gate-metadata fields |
| 5355–5368 |   Three fields are on all five schemas |
| 5369–5396 |   40.1 Gate assembly |
| 5397–5480 |  41. Structured dict fields, and FMEA |
| 5419–5430 |   The grader checks every sub-field is populated |
| 5431–5439 |   `control_plan` is `dict`, never `str` |
| 5440–5448 |   `stability_assessment` is checked BEFORE capability |
| 5449–5460 |   `experiment_justification` is Tier 1 and does not require an experiment |
| 5461–5480 |   FMEA has no field in any schema, and none may be added |
| 5481–5512 |  42. Cross-phase reference fields in practice |
| 5513–5679 |  43. The coaching method |
| 5531–5558 |   43.1 The seven-step computation pattern |
| 5559–5596 |   43.2 Show before asking |
| 5597–5619 |   43.3 The A→F session flow |
| 5620–5651 |   43.4 The live gate document preview |
| 5652–5661 |   43.5 No external URLs |
| 5662–5679 |   43.6 What the coach must not do |
| 5680–6036 | Part IX — Reliability |
| 5684–5712 |   43.7 Metric literacy — the metric, and the statistic |
| 5713–5741 |  44. The failure pipeline |
| 5742–5854 |  45. Timeouts and compensating actions |
| 5749–5780 |   Per-node timeouts — required on every phase executor node |
| 5781–5790 |   Composition order — retries run BEFORE the handler |
| 5791–5800 |   Node-level error handlers — required on every node with external writes |
| 5801–5806 |   Hand-written Saga orchestrators are BANNED |
| 5807–5815 |   Two dependencies on this rule, both correctness-critical |
| 5816–5847 |   Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST** |
| 5848–5854 |   `DeltaChannel` is NOT used |
| 5855–5970 |  46. The fallback chain and circuit breakers |
| 5861–5873 |   The v2.1 four-level chain |
| 5874–5880 |   Backoff strategy is chosen per level, not globally |
| 5881–5899 |   Level 3 cache |
| 5900–5915 |   Circuit breakers — three-state, two instances |
| 5916–5922 |   Degraded mode uses actual state, never a generic error |
| 5923–5930 |   HTTP 400 is NOT a fallback case |
| 5931–5970 |   46.1 Geographic redundancy — **DEFERRED** |
| 5971–6011 |  47. Disconnect policy — what a dropped client commits |
| 5988–5994 |   Ratified policy: ABANDON, not COMPLETE |
| 5995–6011 |   Five requirements |
| 6012–6036 |  48. Structured errors |
| 6037–6524 | Part X — Operations |
| 6041–6094 |  49. API surface |
| 6047–6056 |   One runtime |
| 6057–6064 |   Async by default |
| 6065–6088 |   Endpoints |
| 6089–6094 |   Envelopes are Pydantic v2 |
| 6095–6251 |  50. UI and language rules |
| 6102–6140 |   50.1 Coach response structure |
| 6141–6152 |   Plain language always |
| 6153–6160 |   Citations |
| 6161–6174 |   Contextual feedback |
| 6175–6181 |   Connection status before the first interaction |
| 6182–6187 |   The gate review screen |
| 6188–6226 |   The live gate document |
| 6227–6238 |   The all-gate-fields tab is the contradiction backstop |
| 6239–6251 |   The conflict resolution panel |
| 6252–6327 |  51. Tracing and observability |
| 6258–6268 |   LangSmith is mandatory |
| 6269–6301 |   `@traceable` on every custom function |
| 6302–6307 |   What gets traced |
| 6308–6315 |   P50/P99 latency is a coaching quality signal |
| 6316–6327 |   Logs |
| 6328–6382 |  52. Evaluation and regression testing |
| 6334–6341 |   Built alongside the refactor, not before it |
| 6342–6348 |   The dataset is authored jointly, not generated |
| 6349–6362 |   Minimum viable suite |
| 6363–6373 |   Rubrics and the eval dataset are complementary, not duplicative |
| 6374–6382 |   Two open validation questions this suite answers |
| 6383–6524 |  53. Configuration, dependencies and deployment |
| 6389–6405 |   Fail-fast environment validation |
| 6406–6429 |   Dependency floor |
| 6430–6440 |   `/verify-current-version` is a mandatory checkpoint |
| 6441–6448 |   Infrastructure not yet provisioned |
| 6449–6460 |   Deployment layer: FastAPI, not LangGraph Server |
| 6461–6524 |   53.1 Migration sequence |
| 6525–7093 | Part XI — Governance |
| 6529–6571 |  54. Where code is allowed to live |
| 6536–6553 |   Classes are permitted ONLY in these files |
| 6554–6571 |   Target folder structure |
| 6572–6942 |  55. Anti-drift |
| 6586–6600 |   Rule numbers are load-bearing |
| 6601–6611 |   The registry guards code, not documentation |
| 6612–6617 |   Verification discipline |
| 6618–6640 |   Reference sweeps must use raw `grep -rn`, never a gitignore-filtered tool |
| 6641–6691 |   55.1 Spec-layer governance rules |
| 6692–6774 |   55.2 The BUILT markers, and the paths that oblige a re-check |
| 6775–6855 |   55.3 The phase completeness set — what one phase actually traverses |
| 6856–6905 |   55.4 Facts have one owner — the ratified minimum |
| 6906–6942 |   55.5 The commit gates govern. The rule files are advisory context. |
| 6943–7093 |  56. Amendment procedure |
| 6970–7013 |   56.0 What changed about amending, when the rules stopped being one file |
| 7014–7032 |   56.0.1 Rule, reference, and owned fact — three destinations |
| 7033–7075 |   56.1 A phase is one atomic unit — schema, validator, skill |
| 7076–7093 |   What requires an amendment rather than a routine change |
| 7094–11438 | Part XII — Specification |
| 7104–7127 |   56.2 The rule lands here; the reasoning lands in the commit |
| 7128–7161 |   56.3 The tree at HEAD is the only source of truth |
| 7162–7423 |  57. The specification layer — how to read and write a spec entry |
| 7169–7189 |   Why this Part exists |
| 7190–7205 |   The five structural rules |
| 7206–7220 |   Entry identity and traceability |
| 7221–7268 |   The entry template — three layers |
| 7269–7280 |   How gaps are marked |
| 7281–7297 |   57.1 The two calibrated samples |
| 7298–7351 |   57.2 SAMPLE 1 — CLASS TEMPLATE — S-C01 `SupervisorState` |
| 7301–7351 |    SPEC — `SupervisorState` |
| 7352–7402 |   57.3 SAMPLE 2 — FUNCTION/NODE TEMPLATE — S-F04 `phase_executor` (the coach node) |
| 7356–7402 |    SPEC — `phase_executor` (the coach node) |
| 7403–7423 |   57.4 Entry index |
| 7424–8753 |  58. Spec — graph management |
| 7434–7437 |   58.1 S-C01 · `SupervisorState` |
| 7438–7603 |   58.2 S-C02 · `PhaseState` |
| 7604–7622 |   58.3 S-C03 · Per-phase use of `PhaseState` |
| 7623–7698 |   58.4 S-C04 · `CoachingPlan` |
| 7699–7808 |   58.5 S-C05 · `CoachingResponse` |
| 7809–7860 |   58.6 S-C06 · `AzureBlobStore` |
| 7861–7906 |   58.7 S-C07 · `AzureBlobCheckpointSaver` |
| 7907–7953 |   58.8 S-C08 · `ImproveBlobClient` |
| 7954–8016 |   58.9 S-C09 · `storage/models.py` — the record models |
| 8017–8080 |   58.10 S-F01 · The supervisor graph — static edges |
| 8051–8060 |    SIPOC — at a glance |
| 8061–8080 |    Behaviors (EARS) |
| 8081–8126 |   58.11 S-F02 · `build_phase_subgraph(phase, llm)` |
| 8099–8108 |    SIPOC — at a glance |
| 8109–8126 |    Behaviors (EARS) |
| 8127–8167 |   58.12 S-F03 · `phase_planner` node |
| 8138–8147 |    SIPOC — at a glance |
| 8148–8167 |    Behaviors (EARS) |
| 8168–8179 |   58.13 S-F04 · `phase_executor` node |
| 8180–8241 |   58.14 S-F05 · `validation_stack` node |
| 8190–8199 |    SIPOC — at a glance |
| 8200–8211 |    Behaviors (EARS) |
| 8212–8241 |    ⚠ AI-ACT — high-risk surface |
| 8242–8293 |   58.15 S-F06 · `gate_review_node` |
| 8252–8261 |    SIPOC — at a glance |
| 8262–8269 |    Behaviors (EARS) |
| 8270–8293 |    ⚠ AI-ACT — high-risk surface |
| 8294–8361 |   58.16 S-F07 · `gate_apply_node` |
| 8315–8324 |    SIPOC — at a glance |
| 8325–8337 |    Behaviors (EARS) |
| 8338–8361 |    ⚠ AI-ACT — high-risk surface |
| 8362–8397 |   58.17 S-F08 · The escalation subgraph |
| 8370–8379 |    SIPOC — at a glance |
| 8380–8397 |    Behaviors (EARS) |
| 8398–8466 |   58.18 S-F09 · `analyse_executor_node` |
| 8438–8447 |    SIPOC — at a glance |
| 8448–8466 |    Behaviors (EARS) |
| 8467–8560 |   58.19 S-F10 · `define_input_mapper` |
| 8510–8522 |    SIPOC — at a glance |
| 8523–8551 |    Execution site — where a boundary mapper actually runs |
| 8552–8560 |    Behaviors (EARS) |
| 8561–8614 |   58.20 S-F11 · `define_output_mapper` |
| 8590–8599 |    SIPOC — at a glance |
| 8600–8614 |    Behaviors (EARS) |
| 8615–8664 |   58.21 S-F12 · The Measure, Analyse, Improve and Control mapper pairs |
| 8623–8632 |    SIPOC — at a glance |
| 8633–8664 |    Behaviors (EARS) |
| 8665–8753 |   58.22 S-F13 · Level 2 `Command` routing |
| 8682–8699 |    DP1 — the planner owns the field / gate decision |
| 8700–8720 |    DP2 — the validation stack's three exits |
| 8721–8741 |    DP3 — the gate exits |
| 8742–8753 |    What is settled and binds |
| 8754–9136 |  59. Spec — knowledge and retrieval |
| 8767–8796 |   59.1 S-C16 · `Hop` |
| 8797–8843 |   59.2 S-C17 · `Plan` — the hop decomposition plan |
| 8844–8880 |   59.3 S-C18 · `SynthesisOutput` |
| 8881–8897 |   59.4 S-C19 · `QueryVariants` |
| 8898–8944 |   59.5 S-F14 · `rag_lookup_methodology` |
| 8919–8928 |    SIPOC — at a glance |
| 8929–8944 |    Behaviors (EARS) |
| 8945–8992 |   59.6 S-F15 · `rag_lookup_evidence` |
| 8968–8977 |    SIPOC — at a glance |
| 8978–8992 |    Behaviors (EARS) |
| 8993–9039 |   59.7 S-F16 · `rag_lookup_case_history` |
| 9016–9025 |    SIPOC — at a glance |
| 9026–9039 |    Behaviors (EARS) |
| 9040–9090 |   59.8 S-F17 · `reciprocal_rank_fusion` |
| 9067–9076 |    SIPOC — at a glance |
| 9077–9090 |    Behaviors (EARS) |
| 9091–9136 |   59.9 S-F18 · The retriever layer — `search_knowledge`, `search_cases`, `search_evidence` |
| 9119–9136 |    SIPOC — at a glance |
| 9137–9422 |  60. Spec — tools |
| 9155–9188 |   60.1 S-F19 · `propose_template` |
| 9168–9188 |    SIPOC — at a glance |
| 9189–9227 |   60.2 S-F20 · `propose_diagram` |
| 9204–9213 |    SIPOC — at a glance |
| 9214–9227 |    Behaviors (EARS) |
| 9228–9269 |   60.3 S-F21 · `check_gate_status` |
| 9243–9252 |    SIPOC — at a glance |
| 9253–9269 |    Behaviors (EARS) |
| 9270–9305 |   60.4 S-F22 · `request_human_approval` |
| 9284–9305 |    SIPOC — at a glance |
| 9306–9322 |   60.5 S-F23 · `load_skill(name)` |
| 9323–9367 |   60.6 S-F24 · The 20 computation tools |
| 9346–9367 |    Behaviors (EARS) — binding on all twenty |
| 9368–9422 |   60.7 S-F57 · `load_evidence_series(blob_path, column)` |
| 9393–9402 |    SIPOC — at a glance |
| 9403–9422 |    Behaviors (EARS) |
| 9423–9675 |  61. Spec — the coaching agent's middleware |
| 9441–9503 |   61.1 S-C10 · `ContradictionDetectionMiddleware` |
| 9463–9472 |    Behaviors (EARS) |
| 9473–9503 |    ⚠ AI-ACT — high-risk surface |
| 9504–9545 |   61.2 S-C11 · `BeforeModelStateInjection` |
| 9517–9545 |    Behaviors (EARS) |
| 9546–9585 |   61.3 S-C12 · `DMAICSkillsMiddleware` |
| 9566–9585 |    Behaviors (EARS) |
| 9586–9622 |   61.4 S-C13 · `CoherenceMiddleware` |
| 9600–9622 |    Behaviors (EARS) |
| 9623–9658 |   61.5 S-C14 · `DMAICGraderMiddleware` |
| 9633–9658 |    Behaviors (EARS) |
| 9659–9675 |   61.6 S-C15 · `HITLInterrupt` |
| 9676–10083 |  62. Spec — validation and gates |
| 9690–9732 |   62.1 S-C20 · `CriterionVerdict` |
| 9733–9750 |   62.2 S-C21 · `GraderVerdict` |
| 9751–9764 |   62.3 S-C22 · `CoachingGraderVerdict` |
| 9765–9776 |   62.4 S-C23 · `CoherenceResult` |
| 9777–9791 |   62.5 S-C24 · `ConstraintCheckResult` / `ConstraintVerdict` |
| 9792–9804 |   62.6 S-C25 · `PolicyAdvisoryResult` |
| 9805–9841 |   62.7 S-C26 · `DMAICGateValidator` |
| 9842–9876 |   62.8 S-F25 · Layer 2c — the constraint check |
| 9851–9860 |    SIPOC — at a glance |
| 9861–9876 |    Behaviors (EARS) |
| 9877–9924 |   62.9 S-F26 · Layer 2d — the gate grader |
| 9892–9901 |    SIPOC — at a glance |
| 9902–9924 |    Behaviors (EARS) |
| 9925–9966 |   62.10 S-F27 · The policy advisory |
| 9940–9949 |    SIPOC — at a glance |
| 9950–9966 |    Behaviors (EARS) |
| 9967–10083 |   62.11 S-F28 · Gate document assembly |
| 10055–10064 |    SIPOC — at a glance |
| 10065–10083 |    Behaviors (EARS) |
| 10084–10605 |  63. Spec — the DMAIC gate documents |
| 10102–10170 |   63.1 S-C27 · `DefineOutput` |
| 10171–10211 |   63.2 S-C28 · `MeasureOutput` |
| 10212–10269 |   63.3 S-C29 · `AnalyseOutput` |
| 10270–10329 |   63.4 S-C30 · `ImproveOutput` |
| 10330–10401 |   63.5 S-C31 · `ControlOutput` |
| 10402–10468 |   63.6 S-C32 · The three cross-phase reference dicts |
| 10469–10510 |   63.7 S-C33 · The three structured dict fields |
| 10511–10549 |   63.8 S-C38 · `metric_definitions` — the project metric registry |
| 10550–10605 |   63.9 S-C39 · `phase_metrics` — the per-phase placeholder |
| 10606–10894 |  64. Spec — reliability |
| 10617–10657 |   64.1 S-C34 · `AgentImproveError` |
| 10658–10696 |   64.2 S-C35 · `CircuitBreaker` |
| 10697–10783 |   64.3 S-F29 · `phase_error_recovery` |
| 10725–10734 |    SIPOC — at a glance |
| 10735–10783 |    Behaviors (EARS) |
| 10784–10832 |   64.4 S-F30 · `degraded_mode_response` |
| 10805–10814 |    SIPOC — at a glance |
| 10815–10832 |    Behaviors (EARS) |
| 10833–10851 |   64.5 S-F31 · `synthesise_partial` |
| 10852–10876 |   64.6 S-F32 · `delete_or_flag_stale_in_case_index` |
| 10877–10894 |   64.7 S-F33 · `degraded_coaching_response` node |
| 10895–11071 |  65. Spec — API, UI and evidence |
| 10905–10925 |   65.1 S-C36 · `CitationRecord` and `CitationBundle` |
| 10926–10943 |   65.2 S-C37 · The API envelopes |
| 10944–10996 |   65.3 S-F34 · The API surface |
| 10966–10975 |    SIPOC — at a glance |
| 10976–10996 |    Behaviors (EARS) |
| 10997–11036 |   65.4 S-F35 · The upload handler |
| 11022–11036 |    Behaviors (EARS) |
| 11037–11071 |   65.5 S-F36 · The `improve_case_index` write path |
| 11072–11082 |  66. The SPEC-GAP register — MOVED |
| 11083–11176 |  67. EU AI Act compliance posture |
| 11090–11105 |   67.1 The deadlines are now fixed |
| 11106–11131 |   67.2 The classification question — open, and not answered here |
| 11132–11149 |   67.3 The eight core provider obligations |
| 11150–11160 |   67.4 One compliance finding is already recorded in this document |
| 11161–11176 |   67.5 Compliance-source discipline |
| 11177–11257 |  68. The DORA-structured compliance risk register |
| 11184–11201 |   68.1 Why DORA structure |
| 11202–11218 |   68.2 The register |
| 11219–11242 |   68.3 Pending classification — not register rows |
| 11243–11257 |   68.4 The infrastructure risk already on record |
| 11258–11438 |  69. Spec — computation tools |
| 11287–11358 |   69.1 Common conventions — stated once, binding on all twenty |
| 11359–11364 |   69.2 S-F37 · Define — 1 tool |
| 11365–11377 |   69.3 S-F38–S-F45 · Measure — 8 tools |
| 11378–11387 |   69.4 S-F46–S-F50 · Analyse — 5 tools |
| 11388–11393 |   69.5 S-F51 · Improve — 1 tool |
| 11394–11411 |   69.6 S-F52–S-F56 · Control — 5 tools |
| 11412–11438 |   69.7 The Measure control-chart boundary — a tool that is deliberately absent |
| 11439–11667 | Appendices |
| 11443–11458 |  Appendix A — Provenance index |
| 11449–11452 |   A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference |
| 11453–11458 |   A.2 `agent-improve/ARCHITECTURE.md` → this reference |
| 11459–11489 |  Appendix B — Deferred backlog |
| 11490–11555 |  Appendix C — Trusted sources |
| 11496–11515 |   Tier 1 — current, authoritative |
| 11516–11534 |   Tier 1 — compliance |
| 11535–11538 |   Tier 2 — official announcements |
| 11539–11542 |   Tier 3 — informed practitioner, cross-check before citing |
| 11543–11549 |   Downgraded — historical |
| 11550–11555 |   Excluded |
| 11556–11635 |  Appendix D — Retired names, banned patterns, and exclusions |
| 11558–11580 |   D.1 Retired names — never reintroduce |
| 11581–11624 |   D.2 Banned patterns |
| 11625–11635 |   D.3 Architecturally excluded — not deferred |
| 11636–11644 |  Appendix E — Current state |
| 11645–11667 |  Appendix F — The v2.2.16 registers |
| 11651–11656 |   F.1 Decisions Resolved (v2.2) — the former §17 |
| 11657–11667 |   F.2 Change Log — the former §18 |
| 11661–11667 |    F.2.1 Amendment procedure — the former §18.1 |
