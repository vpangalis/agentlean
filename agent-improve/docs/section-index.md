# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 11664 lines

| Lines | Heading |
|---|---|
| 27–49 |  🗺 Where state lives — a MAP, not a definition |
| 50–254 | Agentic Architecture Reference |
| 149–254 |  About this document |
| 155–212 |   Scope — three agents, one architecture |
| 213–227 |   The two-document division |
| 228–242 |   Section numbering and provenance |
| 243–254 |   Reading conventions |
| 255–546 | Part I — Orientation |
| 259–335 |  1. What Agent Improve is |
| 279–305 |   What makes it architecturally distinctive |
| 306–335 |   The runtime stack |
| 336–387 |  2. How to read this document |
| 342–358 |   By what you are trying to do |
| 359–387 |   Canonical ownership |
| 388–486 |  3. Terminology |
| 399–415 |   Structural primitives |
| 416–427 |   Role labels |
| 428–445 |   The recursion is two levels, not infinite |
| 446–460 |   "Harness" — two senses, do not conflate |
| 461–471 |   "Agent" — used carefully |
| 472–486 |   Things that are deliberately not levels |
| 487–546 |  4. Architecture at a glance |
| 530–546 |   The five things that shape everything else |
| 547–1274 | Part II — State and Persistence |
| 554–612 |  5. `SupervisorState` — orchestration only |
| 566–572 |   `gate_passed` is a dict, not a list |
| 573–584 |   `current_phase` and `phase_index` are derived, and kept anyway |
| 585–604 |   Four fields were removed as redundant, and may not return |
| 605–612 |   Artifacts are not here |
| 613–848 |  6. `PhaseState` — per-phase subgraph state |
| 628–659 |   `asks` — §56 AMENDMENT, ratified 2026-09-09 |
| 660–729 |   `field_log` — §56 AMENDMENT, ratified 2026-09-21 |
| 730–735 |   `draft`, `belt_edits` and `final` are `dict`, never `str` |
| 736–758 |   `coaching_plan` is one typed plan, not a queue |
| 759–774 |   `gate_attempts` — the field whose absence recreated a production bug |
| 775–795 |   `validator_feedback` and `belt_edits` are different, and must stay separate |
| 796–813 |   `citations` and `uploads` — the evidence trail |
| 814–831 |   `hop_results` and `synthesis_output` must be state, not node locals |
| 832–840 |   Per-phase variants |
| 841–848 |   Naming discipline |
| 849–925 |  7. Field typing law — every captured field is a string |
| 865–877 |   Why strings |
| 878–897 |   The one exception — three cross-phase reference dicts |
| 898–925 |   Computation results |
| 926–1018 |  8. The checkpointer / store split |
| 950–969 |   Phased backend |
| 970–981 |   Concurrency and atomicity |
| 982–997 |   Why Blob, and not Cosmos / Tables / SQLite |
| 998–1018 |   On-blob checkpoint format |
| 1019–1155 |  9. The Store — cross-phase artifacts and boundary mappers |
| 1060–1083 |   Namespace convention |
| 1084–1113 |   Why cross-phase data cannot travel on parent state |
| 1114–1134 |   Boundary mappers |
| 1135–1147 |   Two prohibitions that follow |
| 1148–1155 |   Ordering constraint |
| 1156–1213 |  10. Azure Blob — two distinct concerns |
| 1175–1200 |   Complete physical layout |
| 1201–1213 |   The case blob is not updated per turn |
| 1214–1274 |  11. `step_log` — the audit trail |
| 1235–1244 |   `artifacts` and `step_log` are separate fields and stay separate |
| 1245–1274 |   Entries carry deterministic keys, never a raw timestamp as identity |
| 1275–1645 | Part III — The Graph |
| 1281–1321 |  12. Topology |
| 1311–1321 |   The subgraph builder takes the phase as a parameter |
| 1322–1461 |  13. The phase subgraph — five nodes |
| 1399–1429 |   The subgraph is a cycle, not a pipeline |
| 1430–1442 |   Two node names are BANNED |
| 1443–1448 |   Leaf tools are NOT subgraph nodes |
| 1449–1461 |   The validation stack and the policy advisory are NOT tools |
| 1462–1497 |  14. Node contract |
| 1485–1497 |   Reflection is a node, not a private function |
| 1498–1562 |  15. Routing — static edges and `Command` |
| 1504–1521 |   The decision test |
| 1522–1527 |   Never mix static edges and `Command` from the same node |
| 1528–1555 |   Level 1 does not route — it advances |
| 1556–1562 |   No subgraph imports another subgraph's nodes |
| 1563–1645 |  16. `thread_id`, `checkpoint_ns`, and where persistence attaches |
| 1569–1584 |   One `thread_id` per project |
| 1585–1598 |   The checkpointer and store go on the parent graph ONLY |
| 1599–1625 |   The wrapper node must invoke the subgraph directly (G-44) |
| 1626–1645 |   `recursion_limit` is a backstop, not the hop cap |
| 1646–2387 | Part IV — The Coaching Agent |
| 1652–1766 |  17. The Planner / Executor contract |
| 1728–1758 |   `CoachingPlan` |
| 1759–1766 |   Extraction is structured output, not a node and not a tool |
| 1767–1814 |  18. Building the executor — `create_agent` |
| 1779–1786 |   Binding tools directly onto a bare model is a violation |
| 1787–1792 |   `create_react_agent` is superseded |
| 1793–1805 |   deepagents is not a dependency |
| 1806–1814 |   The structured response and the coaching text coexist |
| 1815–2136 |  19. The middleware stack — eight, in order |
| 1837–1883 |   Ordering rules that bind |
| 1884–1895 |   Three independent retry caps |
| 1896–1939 |   19.1 `BeforeModelStateInjection` — injection timing |
| 1940–1955 |   19.2 `DMAICSkillsMiddleware` — progressive disclosure |
| 1956–1995 |   19.3 `SummarizationMiddleware` — context compression |
| 1996–2022 |   19.4 `ModelRetryMiddleware` — API-level retry |
| 2023–2035 |   19.5 `ToolRetryMiddleware` — tool-level retry |
| 2036–2058 |   19.6 `ContradictionDetectionMiddleware` — the mid-phase check |
| 2059–2093 |   19.7 `CoherenceMiddleware` — validation Layer 2a |
| 2094–2124 |   19.8 `DMAICGraderMiddleware` — coaching process quality |
| 2125–2136 |   19.9 Middleware deliberately NOT used |
| 2137–2211 |  20. `CoachingResponse` — the per-turn schema |
| 2191–2194 |   The executor node writes the response into state |
| 2195–2201 |   The executor's `response_format` is `CoachingResponse`, never a phase Output |
| 2202–2211 |   What structured output does NOT give you |
| 2212–2323 |  21. LLM roles, temperature, and the factory |
| 2232–2240 |   Factory only |
| 2241–2261 |   Roles |
| 2262–2278 |   Temperature |
| 2279–2323 |   Structured output — scoped by call type |
| 2324–2387 |  22. Prompts |
| 2350–2370 |   The memory hierarchy paragraph is mandatory |
| 2371–2387 |   Anti-hallucination guards are mandatory |
| 2388–3166 | Part V — Knowledge and Retrieval |
| 2392–2747 |  23. The three indexes |
| 2404–2454 |   23.1 `improve_knowledge_index` — methodology |
| 2455–2580 |   23.2 `improve_evidence_index` — Belt-uploaded evidence |
| 2500–2524 |    Supersession deletes; it does not flag |
| 2525–2580 |    Two Azure behaviours govern the migration |
| 2581–2653 |   23.2.1 The `role` vocabulary — ratified, not invented per phase |
| 2620–2653 |    `unclassified (pre-ask-binding)` is a MIGRATION SENTINEL, not a thirteenth role |
| 2654–2702 |   23.3 `improve_case_index` — case records (cross-case memory) |
| 2703–2713 |   The internal phase key is `analyse`, never `analyse_phase` |
| 2714–2738 |   23.4 The write-path trap that made `phase_relevance` unfilterable |
| 2739–2747 |   23.5 Schema change procedure |
| 2748–2876 |  24. The three `rag_lookup_*` tools |
| 2766–2823 |   `rag_lookup_evidence` returns a structured record, not rendered text |
| 2824–2836 |   RAG via tool, never via prepended system message |
| 2837–2861 |   The retrieval mechanism |
| 2862–2869 |   `belt_level` filtering is OFF by default |
| 2870–2876 |   `source_file` and `page_number` are returned, never filtered |
| 2877–2942 |  25. Multi-query and Reciprocal Rank Fusion |
| 2886–2902 |   Why it is mandatory |
| 2903–2909 |   The implementation |
| 2910–2931 |   `MultiQueryRetriever` and `EnsembleRetriever` are BANNED |
| 2932–2942 |   Encapsulation |
| 2943–3076 |  26. Multi-hop retrieval |
| 2958–2994 |   The hop cap is `RemainingSteps` |
| 2995–3013 |   Per-phase policy |
| 3014–3058 |   Planned multi-hop — the Analyse pipeline |
| 3059–3076 |   **UNVERIFIED** — planned multi-hop is Analyse-only |
| 3077–3123 |  27. Retrieval failure semantics |
| 3088–3096 |   Never wrap a retrieval call in a bare `except Exception` returning `[]` |
| 3097–3106 |   Three rules that each have already bitten |
| 3107–3123 |   The coach-facing message must not read as absence |
| 3124–3166 |  28. Memory taxonomy |
| 3142–3166 |   The static/dynamic split is the part that matters |
| 3167–3513 | Part VI — Tools |
| 3171–3328 |  29. The data channel and the universal eight |
| 3177–3212 |   29.1 There is no MCP — the data-channel decision |
| 3213–3255 |   29.2 The universal eight |
| 3221–3255 |    `load_evidence_series` joins the set — RATIFIED 2026-09-09 |
| 3256–3265 |   29.3 `record_field` is RETIRED and may not be reintroduced |
| 3266–3328 |   29.4 Cross-agent tools — a third category, present but NOT BOUND |
| 3329–3403 |  30. Computation tools and per-phase binding |
| 3334–3371 |   Tool sets are per phase, not universal |
| 3372–3377 |   Each of the 20 is a separate named tool |
| 3378–3386 |   All 20 are pure functions |
| 3387–3396 |   `imr_chart_limits` — the choice that is usually wrong by default |
| 3397–3403 |   Tool decisions are the model's, not the graph's |
| 3404–3436 |  31. Tool arg schemas and docstrings |
| 3410–3415 |   Every `@tool` uses `args_schema=` |
| 3416–3436 |   Docstrings are interface, not commentary |
| 3437–3513 |  32. Phase skills — SKILL.md |
| 3460–3464 |   Each skill's `allowed-tools` MUST match that phase's subset in §30 |
| 3465–3474 |   Progressive disclosure — three levels |
| 3475–3480 |   Storage backend: `FilesystemBackend` |
| 3481–3502 |   Each SKILL.md must carry |
| 3503–3513 |   Two distinct kinds of skill exist in this repository |
| 3514–4094 | Part VII — Validation and Gates |
| 3521–3641 |  33. The nine-step HITL gate |
| 3542–3555 |   Two quality checks, two actors, two moments |
| 3556–3567 |   Gates are one-way doors, with exactly one defined exception |
| 3568–3572 |   Implementation: graph-level `interrupt()` |
| 3573–3603 |   33.1 The two-node split |
| 3604–3633 |   33.2 `gate_apply_node` writes the gate document TWICE |
| 3634–3641 |   33.3 The checkpoint commits only after Belt approval |
| 3642–3745 |  34. The four-layer validation stack |
| 3657–3664 |   Layer 2a is middleware; layers 2b–2d are the node |
| 3665–3671 |   Layer 2d is NOT `DMAICGraderMiddleware` |
| 3672–3677 |   Run cheapest first |
| 3678–3687 |   The counter and the feedback |
| 3688–3697 |   Layer 2b is the only deterministic layer, deliberately |
| 3698–3709 |   Per-phase constraint sets |
| 3710–3719 |   34.1 Where each check fires |
| 3720–3745 |   34.2 The self-healing hierarchy and the transparency principle |
| 3746–3881 |  35. Two tiers of field, and the `warning` verdict |
| 3752–3766 |   The problem this solves |
| 3767–3783 |   Three distinct things check these fields, and conflating them is a design error |
| 3784–3832 |   Gate-required fields by phase |
| 3833–3849 |   The grader's verdict has three statuses |
| 3850–3857 |   Why two tiers |
| 3858–3881 |   The grader is belt-level aware |
| 3882–3975 |  36. Two graders — and why they are not redundant |
| 3901–3914 |   Why both exist |
| 3915–3938 |   `COACHING_QUALITY_RUBRIC` |
| 3939–3948 |   Mechanism, both graders |
| 3949–3958 |   Three criteria are verified deterministically, not by judgment |
| 3959–3975 |   The ratified rubric coverage |
| 3976–4072 |  37. Mid-phase contradiction and the re-approval cascade |
| 3982–4003 |   The check runs every turn, not only at gates |
| 4004–4037 |   §37 governs a GATE-COMMITTED value only |
| 4038–4051 |   There is NO tolerance threshold, and none may be added |
| 4052–4059 |   The re-approval cascade |
| 4060–4072 |   The cascade has a hard dependency on compensating actions |
| 4073–4094 |  38. Escalation |
| 4095–5675 | Part VIII — The DMAIC Domain |
| 4102–5296 |  39. The five phases |
| 4120–4134 |   The measurement thread that runs across three phases |
| 4135–4369 |   39.1 Define phase, complete specification |
| 4142–4149 |    39.1.1 Purpose |
| 4150–4212 |    39.1.2 The ordered field list — the `field_index` sequence (closes G-38) |
| 4213–4227 |    39.1.3 The composed-problem-statement rule (binding) |
| 4228–4242 |    39.1.4 The `team` structure |
| 4243–4252 |    39.1.5 SIPOC handling |
| 4253–4264 |    39.1.6 Gate, storage, progress view |
| 4265–4283 |    39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4284–4290 |    39.1.8 The other four phases |
| 4291–4323 |    39.1.9 The metric registry and Define's placeholder |
| 4324–4331 |    39.1.10 Tools bound to Define |
| 4332–4339 |    39.1.11 Conditions — routing and the gate |
| 4340–4347 |    39.1.12 State parameters — Define's use of `PhaseState` |
| 4348–4355 |    39.1.13 Metric literacy — what each metric means |
| 4356–4369 |    39.1.14 Cross-phase reads and writes |
| 4370–4625 |   39.2 Measure phase, complete specification |
| 4380–4388 |    39.2.1 Purpose |
| 4389–4411 |    39.2.2 The ordered field list — the `field_index` sequence |
| 4412–4472 |    39.2.3 The metric registry and Measure's placeholder |
| 4473–4492 |    39.2.4 SIPOC → the detailed process map |
| 4493–4514 |    39.2.5 Tools bound to Measure |
| 4515–4544 |    39.2.6 Conditions — sequence locks, routing, and the gate |
| 4545–4562 |    39.2.7 State parameters — Measure's use of `PhaseState` |
| 4563–4579 |    39.2.8 Metric literacy — what each metric means |
| 4580–4593 |    39.2.9 Gate, storage, progress view |
| 4594–4602 |    39.2.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4603–4619 |    39.2.11 Cross-phase reads and writes |
| 4620–4625 |    39.2.12 The other two phases |
| 4626–4855 |   39.3 Analyse phase, complete specification |
| 4636–4645 |    39.3.1 Purpose |
| 4646–4671 |    39.3.2 The ordered field list — the `field_index` sequence |
| 4672–4708 |    39.3.3 The metric registry and Analyse's placeholder (linkage form — closes F-13) |
| 4709–4728 |    39.3.4 Two movements — generate, then validate |
| 4729–4751 |    39.3.5 Tools bound to Analyse |
| 4752–4780 |    39.3.6 Conditions — methodology guards, routing, and the gate |
| 4781–4794 |    39.3.7 State parameters — Analyse's use of `PhaseState` |
| 4795–4810 |    39.3.8 Metric literacy — what each metric and statistic means |
| 4811–4822 |    39.3.9 Gate, storage, progress view |
| 4823–4831 |    39.3.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4832–4849 |    39.3.11 Cross-phase reads and writes |
| 4850–4855 |    39.3.12 The other phase |
| 4856–5058 |   39.4 Improve phase, complete specification |
| 4866–4874 |    39.4.1 Purpose |
| 4875–4895 |    39.4.2 The ordered field list — the `field_index` sequence |
| 4896–4914 |    39.4.3 The metric registry and Improve's placeholder (linkage form) |
| 4915–4932 |    39.4.4 Two movements — generate-and-select, then pilot-and-prove |
| 4933–4951 |    39.4.5 Tools bound to Improve |
| 4952–4983 |    39.4.6 Conditions — methodology guards, DOE belt-gating, routing, gate |
| 4984–4997 |    39.4.7 State parameters — Improve's use of `PhaseState` |
| 4998–5011 |    39.4.8 Metric literacy — what each metric and statistic means |
| 5012–5023 |    39.4.9 Gate, storage, progress view |
| 5024–5033 |    39.4.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5034–5050 |    39.4.11 Cross-phase reads and writes |
| 5051–5058 |    39.4.12 The last phase |
| 5059–5296 |   39.5 Control phase, complete specification |
| 5069–5077 |    39.5.1 Purpose |
| 5078–5106 |    39.5.2 The ordered field list — the `field_index` sequence |
| 5107–5136 |    39.5.3 The metric registry, the comparison, and single authority (closes F-14) |
| 5137–5153 |    39.5.4 Two movements — confirm it held, then lock it in |
| 5154–5173 |    39.5.5 Tools bound to Control |
| 5174–5206 |    39.5.6 Conditions — guards, routing, gate |
| 5207–5220 |    39.5.7 State parameters — Control's use of `PhaseState` |
| 5221–5235 |    39.5.8 Metric literacy — what each metric and statistic means |
| 5236–5249 |    39.5.9 Gate, storage, progress view |
| 5250–5260 |    39.5.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5261–5276 |    39.5.11 Cross-phase reads and writes — the thread closes here |
| 5277–5296 |    39.5.12 The measurement thread, closed |
| 5297–5392 |  40. The five `{Phase}Output` schemas |
| 5320–5338 |   Field counts |
| 5339–5350 |   The four gate-metadata fields |
| 5351–5364 |   Three fields are on all five schemas |
| 5365–5392 |   40.1 Gate assembly |
| 5393–5476 |  41. Structured dict fields, and FMEA |
| 5415–5426 |   The grader checks every sub-field is populated |
| 5427–5435 |   `control_plan` is `dict`, never `str` |
| 5436–5444 |   `stability_assessment` is checked BEFORE capability |
| 5445–5456 |   `experiment_justification` is Tier 1 and does not require an experiment |
| 5457–5476 |   FMEA has no field in any schema, and none may be added |
| 5477–5508 |  42. Cross-phase reference fields in practice |
| 5509–5675 |  43. The coaching method |
| 5527–5554 |   43.1 The seven-step computation pattern |
| 5555–5592 |   43.2 Show before asking |
| 5593–5615 |   43.3 The A→F session flow |
| 5616–5647 |   43.4 The live gate document preview |
| 5648–5657 |   43.5 No external URLs |
| 5658–5675 |   43.6 What the coach must not do |
| 5676–6032 | Part IX — Reliability |
| 5680–5708 |   43.7 Metric literacy — the metric, and the statistic |
| 5709–5737 |  44. The failure pipeline |
| 5738–5850 |  45. Timeouts and compensating actions |
| 5745–5776 |   Per-node timeouts — required on every phase executor node |
| 5777–5786 |   Composition order — retries run BEFORE the handler |
| 5787–5796 |   Node-level error handlers — required on every node with external writes |
| 5797–5802 |   Hand-written Saga orchestrators are BANNED |
| 5803–5811 |   Two dependencies on this rule, both correctness-critical |
| 5812–5843 |   Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST** |
| 5844–5850 |   `DeltaChannel` is NOT used |
| 5851–5966 |  46. The fallback chain and circuit breakers |
| 5857–5869 |   The v2.1 four-level chain |
| 5870–5876 |   Backoff strategy is chosen per level, not globally |
| 5877–5895 |   Level 3 cache |
| 5896–5911 |   Circuit breakers — three-state, two instances |
| 5912–5918 |   Degraded mode uses actual state, never a generic error |
| 5919–5926 |   HTTP 400 is NOT a fallback case |
| 5927–5966 |   46.1 Geographic redundancy — **DEFERRED** |
| 5967–6007 |  47. Disconnect policy — what a dropped client commits |
| 5984–5990 |   Ratified policy: ABANDON, not COMPLETE |
| 5991–6007 |   Five requirements |
| 6008–6032 |  48. Structured errors |
| 6033–6521 | Part X — Operations |
| 6037–6091 |  49. API surface |
| 6043–6052 |   One runtime |
| 6053–6060 |   Async by default |
| 6061–6085 |   Endpoints |
| 6086–6091 |   Envelopes are Pydantic v2 |
| 6092–6248 |  50. UI and language rules |
| 6099–6137 |   50.1 Coach response structure |
| 6138–6149 |   Plain language always |
| 6150–6157 |   Citations |
| 6158–6171 |   Contextual feedback |
| 6172–6178 |   Connection status before the first interaction |
| 6179–6184 |   The gate review screen |
| 6185–6223 |   The live gate document |
| 6224–6235 |   The all-gate-fields tab is the contradiction backstop |
| 6236–6248 |   The conflict resolution panel |
| 6249–6324 |  51. Tracing and observability |
| 6255–6265 |   LangSmith is mandatory |
| 6266–6298 |   `@traceable` on every custom function |
| 6299–6304 |   What gets traced |
| 6305–6312 |   P50/P99 latency is a coaching quality signal |
| 6313–6324 |   Logs |
| 6325–6379 |  52. Evaluation and regression testing |
| 6331–6338 |   Built alongside the refactor, not before it |
| 6339–6345 |   The dataset is authored jointly, not generated |
| 6346–6359 |   Minimum viable suite |
| 6360–6370 |   Rubrics and the eval dataset are complementary, not duplicative |
| 6371–6379 |   Two open validation questions this suite answers |
| 6380–6521 |  53. Configuration, dependencies and deployment |
| 6386–6402 |   Fail-fast environment validation |
| 6403–6426 |   Dependency floor |
| 6427–6437 |   `/verify-current-version` is a mandatory checkpoint |
| 6438–6445 |   Infrastructure not yet provisioned |
| 6446–6457 |   Deployment layer: FastAPI, not LangGraph Server |
| 6458–6521 |   53.1 Migration sequence |
| 6522–7090 | Part XI — Governance |
| 6526–6568 |  54. Where code is allowed to live |
| 6533–6550 |   Classes are permitted ONLY in these files |
| 6551–6568 |   Target folder structure |
| 6569–6939 |  55. Anti-drift |
| 6583–6597 |   Rule numbers are load-bearing |
| 6598–6608 |   The registry guards code, not documentation |
| 6609–6614 |   Verification discipline |
| 6615–6637 |   Reference sweeps must use raw `grep -rn`, never a gitignore-filtered tool |
| 6638–6688 |   55.1 Spec-layer governance rules |
| 6689–6771 |   55.2 The BUILT markers, and the paths that oblige a re-check |
| 6772–6852 |   55.3 The phase completeness set — what one phase actually traverses |
| 6853–6902 |   55.4 Facts have one owner — the ratified minimum |
| 6903–6939 |   55.5 The commit gates govern. The rule files are advisory context. |
| 6940–7090 |  56. Amendment procedure |
| 6967–7010 |   56.0 What changed about amending, when the rules stopped being one file |
| 7011–7029 |   56.0.1 Rule, reference, and owned fact — three destinations |
| 7030–7072 |   56.1 A phase is one atomic unit — schema, validator, skill |
| 7073–7090 |   What requires an amendment rather than a routine change |
| 7091–11435 | Part XII — Specification |
| 7101–7124 |   56.2 The rule lands here; the reasoning lands in the commit |
| 7125–7158 |   56.3 The tree at HEAD is the only source of truth |
| 7159–7420 |  57. The specification layer — how to read and write a spec entry |
| 7166–7186 |   Why this Part exists |
| 7187–7202 |   The five structural rules |
| 7203–7217 |   Entry identity and traceability |
| 7218–7265 |   The entry template — three layers |
| 7266–7277 |   How gaps are marked |
| 7278–7294 |   57.1 The two calibrated samples |
| 7295–7348 |   57.2 SAMPLE 1 — CLASS TEMPLATE — S-C01 `SupervisorState` |
| 7298–7348 |    SPEC — `SupervisorState` |
| 7349–7399 |   57.3 SAMPLE 2 — FUNCTION/NODE TEMPLATE — S-F04 `phase_executor` (the coach node) |
| 7353–7399 |    SPEC — `phase_executor` (the coach node) |
| 7400–7420 |   57.4 Entry index |
| 7421–8750 |  58. Spec — graph management |
| 7431–7434 |   58.1 S-C01 · `SupervisorState` |
| 7435–7600 |   58.2 S-C02 · `PhaseState` |
| 7601–7619 |   58.3 S-C03 · Per-phase use of `PhaseState` |
| 7620–7695 |   58.4 S-C04 · `CoachingPlan` |
| 7696–7805 |   58.5 S-C05 · `CoachingResponse` |
| 7806–7857 |   58.6 S-C06 · `AzureBlobStore` |
| 7858–7903 |   58.7 S-C07 · `AzureBlobCheckpointSaver` |
| 7904–7950 |   58.8 S-C08 · `ImproveBlobClient` |
| 7951–8013 |   58.9 S-C09 · `storage/models.py` — the record models |
| 8014–8077 |   58.10 S-F01 · The supervisor graph — static edges |
| 8048–8057 |    SIPOC — at a glance |
| 8058–8077 |    Behaviors (EARS) |
| 8078–8123 |   58.11 S-F02 · `build_phase_subgraph(phase, llm)` |
| 8096–8105 |    SIPOC — at a glance |
| 8106–8123 |    Behaviors (EARS) |
| 8124–8164 |   58.12 S-F03 · `phase_planner` node |
| 8135–8144 |    SIPOC — at a glance |
| 8145–8164 |    Behaviors (EARS) |
| 8165–8176 |   58.13 S-F04 · `phase_executor` node |
| 8177–8238 |   58.14 S-F05 · `validation_stack` node |
| 8187–8196 |    SIPOC — at a glance |
| 8197–8208 |    Behaviors (EARS) |
| 8209–8238 |    ⚠ AI-ACT — high-risk surface |
| 8239–8290 |   58.15 S-F06 · `gate_review_node` |
| 8249–8258 |    SIPOC — at a glance |
| 8259–8266 |    Behaviors (EARS) |
| 8267–8290 |    ⚠ AI-ACT — high-risk surface |
| 8291–8358 |   58.16 S-F07 · `gate_apply_node` |
| 8312–8321 |    SIPOC — at a glance |
| 8322–8334 |    Behaviors (EARS) |
| 8335–8358 |    ⚠ AI-ACT — high-risk surface |
| 8359–8394 |   58.17 S-F08 · The escalation subgraph |
| 8367–8376 |    SIPOC — at a glance |
| 8377–8394 |    Behaviors (EARS) |
| 8395–8463 |   58.18 S-F09 · `analyse_executor_node` |
| 8435–8444 |    SIPOC — at a glance |
| 8445–8463 |    Behaviors (EARS) |
| 8464–8557 |   58.19 S-F10 · `define_input_mapper` |
| 8507–8519 |    SIPOC — at a glance |
| 8520–8548 |    Execution site — where a boundary mapper actually runs |
| 8549–8557 |    Behaviors (EARS) |
| 8558–8611 |   58.20 S-F11 · `define_output_mapper` |
| 8587–8596 |    SIPOC — at a glance |
| 8597–8611 |    Behaviors (EARS) |
| 8612–8661 |   58.21 S-F12 · The Measure, Analyse, Improve and Control mapper pairs |
| 8620–8629 |    SIPOC — at a glance |
| 8630–8661 |    Behaviors (EARS) |
| 8662–8750 |   58.22 S-F13 · Level 2 `Command` routing |
| 8679–8696 |    DP1 — the planner owns the field / gate decision |
| 8697–8717 |    DP2 — the validation stack's three exits |
| 8718–8738 |    DP3 — the gate exits |
| 8739–8750 |    What is settled and binds |
| 8751–9133 |  59. Spec — knowledge and retrieval |
| 8764–8793 |   59.1 S-C16 · `Hop` |
| 8794–8840 |   59.2 S-C17 · `Plan` — the hop decomposition plan |
| 8841–8877 |   59.3 S-C18 · `SynthesisOutput` |
| 8878–8894 |   59.4 S-C19 · `QueryVariants` |
| 8895–8941 |   59.5 S-F14 · `rag_lookup_methodology` |
| 8916–8925 |    SIPOC — at a glance |
| 8926–8941 |    Behaviors (EARS) |
| 8942–8989 |   59.6 S-F15 · `rag_lookup_evidence` |
| 8965–8974 |    SIPOC — at a glance |
| 8975–8989 |    Behaviors (EARS) |
| 8990–9036 |   59.7 S-F16 · `rag_lookup_case_history` |
| 9013–9022 |    SIPOC — at a glance |
| 9023–9036 |    Behaviors (EARS) |
| 9037–9087 |   59.8 S-F17 · `reciprocal_rank_fusion` |
| 9064–9073 |    SIPOC — at a glance |
| 9074–9087 |    Behaviors (EARS) |
| 9088–9133 |   59.9 S-F18 · The retriever layer — `search_knowledge`, `search_cases`, `search_evidence` |
| 9116–9133 |    SIPOC — at a glance |
| 9134–9419 |  60. Spec — tools |
| 9152–9185 |   60.1 S-F19 · `propose_template` |
| 9165–9185 |    SIPOC — at a glance |
| 9186–9224 |   60.2 S-F20 · `propose_diagram` |
| 9201–9210 |    SIPOC — at a glance |
| 9211–9224 |    Behaviors (EARS) |
| 9225–9266 |   60.3 S-F21 · `check_gate_status` |
| 9240–9249 |    SIPOC — at a glance |
| 9250–9266 |    Behaviors (EARS) |
| 9267–9302 |   60.4 S-F22 · `request_human_approval` |
| 9281–9302 |    SIPOC — at a glance |
| 9303–9319 |   60.5 S-F23 · `load_skill(name)` |
| 9320–9364 |   60.6 S-F24 · The 20 computation tools |
| 9343–9364 |    Behaviors (EARS) — binding on all twenty |
| 9365–9419 |   60.7 S-F57 · `load_evidence_series(blob_path, column)` |
| 9390–9399 |    SIPOC — at a glance |
| 9400–9419 |    Behaviors (EARS) |
| 9420–9672 |  61. Spec — the coaching agent's middleware |
| 9438–9500 |   61.1 S-C10 · `ContradictionDetectionMiddleware` |
| 9460–9469 |    Behaviors (EARS) |
| 9470–9500 |    ⚠ AI-ACT — high-risk surface |
| 9501–9542 |   61.2 S-C11 · `BeforeModelStateInjection` |
| 9514–9542 |    Behaviors (EARS) |
| 9543–9582 |   61.3 S-C12 · `DMAICSkillsMiddleware` |
| 9563–9582 |    Behaviors (EARS) |
| 9583–9619 |   61.4 S-C13 · `CoherenceMiddleware` |
| 9597–9619 |    Behaviors (EARS) |
| 9620–9655 |   61.5 S-C14 · `DMAICGraderMiddleware` |
| 9630–9655 |    Behaviors (EARS) |
| 9656–9672 |   61.6 S-C15 · `HITLInterrupt` |
| 9673–10080 |  62. Spec — validation and gates |
| 9687–9729 |   62.1 S-C20 · `CriterionVerdict` |
| 9730–9747 |   62.2 S-C21 · `GraderVerdict` |
| 9748–9761 |   62.3 S-C22 · `CoachingGraderVerdict` |
| 9762–9773 |   62.4 S-C23 · `CoherenceResult` |
| 9774–9788 |   62.5 S-C24 · `ConstraintCheckResult` / `ConstraintVerdict` |
| 9789–9801 |   62.6 S-C25 · `PolicyAdvisoryResult` |
| 9802–9838 |   62.7 S-C26 · `DMAICGateValidator` |
| 9839–9873 |   62.8 S-F25 · Layer 2c — the constraint check |
| 9848–9857 |    SIPOC — at a glance |
| 9858–9873 |    Behaviors (EARS) |
| 9874–9921 |   62.9 S-F26 · Layer 2d — the gate grader |
| 9889–9898 |    SIPOC — at a glance |
| 9899–9921 |    Behaviors (EARS) |
| 9922–9963 |   62.10 S-F27 · The policy advisory |
| 9937–9946 |    SIPOC — at a glance |
| 9947–9963 |    Behaviors (EARS) |
| 9964–10080 |   62.11 S-F28 · Gate document assembly |
| 10052–10061 |    SIPOC — at a glance |
| 10062–10080 |    Behaviors (EARS) |
| 10081–10602 |  63. Spec — the DMAIC gate documents |
| 10099–10167 |   63.1 S-C27 · `DefineOutput` |
| 10168–10208 |   63.2 S-C28 · `MeasureOutput` |
| 10209–10266 |   63.3 S-C29 · `AnalyseOutput` |
| 10267–10326 |   63.4 S-C30 · `ImproveOutput` |
| 10327–10398 |   63.5 S-C31 · `ControlOutput` |
| 10399–10465 |   63.6 S-C32 · The three cross-phase reference dicts |
| 10466–10507 |   63.7 S-C33 · The three structured dict fields |
| 10508–10546 |   63.8 S-C38 · `metric_definitions` — the project metric registry |
| 10547–10602 |   63.9 S-C39 · `phase_metrics` — the per-phase placeholder |
| 10603–10891 |  64. Spec — reliability |
| 10614–10654 |   64.1 S-C34 · `AgentImproveError` |
| 10655–10693 |   64.2 S-C35 · `CircuitBreaker` |
| 10694–10780 |   64.3 S-F29 · `phase_error_recovery` |
| 10722–10731 |    SIPOC — at a glance |
| 10732–10780 |    Behaviors (EARS) |
| 10781–10829 |   64.4 S-F30 · `degraded_mode_response` |
| 10802–10811 |    SIPOC — at a glance |
| 10812–10829 |    Behaviors (EARS) |
| 10830–10848 |   64.5 S-F31 · `synthesise_partial` |
| 10849–10873 |   64.6 S-F32 · `delete_or_flag_stale_in_case_index` |
| 10874–10891 |   64.7 S-F33 · `degraded_coaching_response` node |
| 10892–11068 |  65. Spec — API, UI and evidence |
| 10902–10922 |   65.1 S-C36 · `CitationRecord` and `CitationBundle` |
| 10923–10940 |   65.2 S-C37 · The API envelopes |
| 10941–10993 |   65.3 S-F34 · The API surface |
| 10963–10972 |    SIPOC — at a glance |
| 10973–10993 |    Behaviors (EARS) |
| 10994–11033 |   65.4 S-F35 · The upload handler |
| 11019–11033 |    Behaviors (EARS) |
| 11034–11068 |   65.5 S-F36 · The `improve_case_index` write path |
| 11069–11079 |  66. The SPEC-GAP register — MOVED |
| 11080–11173 |  67. EU AI Act compliance posture |
| 11087–11102 |   67.1 The deadlines are now fixed |
| 11103–11128 |   67.2 The classification question — open, and not answered here |
| 11129–11146 |   67.3 The eight core provider obligations |
| 11147–11157 |   67.4 One compliance finding is already recorded in this document |
| 11158–11173 |   67.5 Compliance-source discipline |
| 11174–11254 |  68. The DORA-structured compliance risk register |
| 11181–11198 |   68.1 Why DORA structure |
| 11199–11215 |   68.2 The register |
| 11216–11239 |   68.3 Pending classification — not register rows |
| 11240–11254 |   68.4 The infrastructure risk already on record |
| 11255–11435 |  69. Spec — computation tools |
| 11284–11355 |   69.1 Common conventions — stated once, binding on all twenty |
| 11356–11361 |   69.2 S-F37 · Define — 1 tool |
| 11362–11374 |   69.3 S-F38–S-F45 · Measure — 8 tools |
| 11375–11384 |   69.4 S-F46–S-F50 · Analyse — 5 tools |
| 11385–11390 |   69.5 S-F51 · Improve — 1 tool |
| 11391–11408 |   69.6 S-F52–S-F56 · Control — 5 tools |
| 11409–11435 |   69.7 The Measure control-chart boundary — a tool that is deliberately absent |
| 11436–11664 | Appendices |
| 11440–11455 |  Appendix A — Provenance index |
| 11446–11449 |   A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference |
| 11450–11455 |   A.2 `agent-improve/ARCHITECTURE.md` → this reference |
| 11456–11486 |  Appendix B — Deferred backlog |
| 11487–11552 |  Appendix C — Trusted sources |
| 11493–11512 |   Tier 1 — current, authoritative |
| 11513–11531 |   Tier 1 — compliance |
| 11532–11535 |   Tier 2 — official announcements |
| 11536–11539 |   Tier 3 — informed practitioner, cross-check before citing |
| 11540–11546 |   Downgraded — historical |
| 11547–11552 |   Excluded |
| 11553–11632 |  Appendix D — Retired names, banned patterns, and exclusions |
| 11555–11577 |   D.1 Retired names — never reintroduce |
| 11578–11621 |   D.2 Banned patterns |
| 11622–11632 |   D.3 Architecturally excluded — not deferred |
| 11633–11641 |  Appendix E — Current state |
| 11642–11664 |  Appendix F — The v2.2.16 registers |
| 11648–11653 |   F.1 Decisions Resolved (v2.2) — the former §17 |
| 11654–11664 |   F.2 Change Log — the former §18 |
| 11658–11664 |    F.2.1 Amendment procedure — the former §18.1 |
