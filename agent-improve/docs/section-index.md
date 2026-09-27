# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 11669 lines

| Lines | Heading |
|---|---|
| 27–49 |  🗺 Where state lives — a MAP, not a definition |
| 50–259 | Agentic Architecture Reference |
| 154–259 |  About this document |
| 160–217 |   Scope — three agents, one architecture |
| 218–232 |   The two-document division |
| 233–247 |   Section numbering and provenance |
| 248–259 |   Reading conventions |
| 260–551 | Part I — Orientation |
| 264–340 |  1. What Agent Improve is |
| 284–310 |   What makes it architecturally distinctive |
| 311–340 |   The runtime stack |
| 341–392 |  2. How to read this document |
| 347–363 |   By what you are trying to do |
| 364–392 |   Canonical ownership |
| 393–491 |  3. Terminology |
| 404–420 |   Structural primitives |
| 421–432 |   Role labels |
| 433–450 |   The recursion is two levels, not infinite |
| 451–465 |   "Harness" — two senses, do not conflate |
| 466–476 |   "Agent" — used carefully |
| 477–491 |   Things that are deliberately not levels |
| 492–551 |  4. Architecture at a glance |
| 535–551 |   The five things that shape everything else |
| 552–1279 | Part II — State and Persistence |
| 559–617 |  5. `SupervisorState` — orchestration only |
| 571–577 |   `gate_passed` is a dict, not a list |
| 578–589 |   `current_phase` and `phase_index` are derived, and kept anyway |
| 590–609 |   Four fields were removed as redundant, and may not return |
| 610–617 |   Artifacts are not here |
| 618–853 |  6. `PhaseState` — per-phase subgraph state |
| 633–664 |   `asks` — §56 AMENDMENT, ratified 2026-09-09 |
| 665–734 |   `field_log` — §56 AMENDMENT, ratified 2026-09-21 |
| 735–740 |   `draft`, `belt_edits` and `final` are `dict`, never `str` |
| 741–763 |   `coaching_plan` is one typed plan, not a queue |
| 764–779 |   `gate_attempts` — the field whose absence recreated a production bug |
| 780–800 |   `validator_feedback` and `belt_edits` are different, and must stay separate |
| 801–818 |   `citations` and `uploads` — the evidence trail |
| 819–836 |   `hop_results` and `synthesis_output` must be state, not node locals |
| 837–845 |   Per-phase variants |
| 846–853 |   Naming discipline |
| 854–930 |  7. Field typing law — every captured field is a string |
| 870–882 |   Why strings |
| 883–902 |   The one exception — three cross-phase reference dicts |
| 903–930 |   Computation results |
| 931–1023 |  8. The checkpointer / store split |
| 955–974 |   Phased backend |
| 975–986 |   Concurrency and atomicity |
| 987–1002 |   Why Blob, and not Cosmos / Tables / SQLite |
| 1003–1023 |   On-blob checkpoint format |
| 1024–1160 |  9. The Store — cross-phase artifacts and boundary mappers |
| 1065–1088 |   Namespace convention |
| 1089–1118 |   Why cross-phase data cannot travel on parent state |
| 1119–1139 |   Boundary mappers |
| 1140–1152 |   Two prohibitions that follow |
| 1153–1160 |   Ordering constraint |
| 1161–1218 |  10. Azure Blob — two distinct concerns |
| 1180–1205 |   Complete physical layout |
| 1206–1218 |   The case blob is not updated per turn |
| 1219–1279 |  11. `step_log` — the audit trail |
| 1240–1249 |   `artifacts` and `step_log` are separate fields and stay separate |
| 1250–1279 |   Entries carry deterministic keys, never a raw timestamp as identity |
| 1280–1650 | Part III — The Graph |
| 1286–1326 |  12. Topology |
| 1316–1326 |   The subgraph builder takes the phase as a parameter |
| 1327–1466 |  13. The phase subgraph — five nodes |
| 1404–1434 |   The subgraph is a cycle, not a pipeline |
| 1435–1447 |   Two node names are BANNED |
| 1448–1453 |   Leaf tools are NOT subgraph nodes |
| 1454–1466 |   The validation stack and the policy advisory are NOT tools |
| 1467–1502 |  14. Node contract |
| 1490–1502 |   Reflection is a node, not a private function |
| 1503–1567 |  15. Routing — static edges and `Command` |
| 1509–1526 |   The decision test |
| 1527–1532 |   Never mix static edges and `Command` from the same node |
| 1533–1560 |   Level 1 does not route — it advances |
| 1561–1567 |   No subgraph imports another subgraph's nodes |
| 1568–1650 |  16. `thread_id`, `checkpoint_ns`, and where persistence attaches |
| 1574–1589 |   One `thread_id` per project |
| 1590–1603 |   The checkpointer and store go on the parent graph ONLY |
| 1604–1630 |   The wrapper node must invoke the subgraph directly (G-44) |
| 1631–1650 |   `recursion_limit` is a backstop, not the hop cap |
| 1651–2392 | Part IV — The Coaching Agent |
| 1657–1771 |  17. The Planner / Executor contract |
| 1733–1763 |   `CoachingPlan` |
| 1764–1771 |   Extraction is structured output, not a node and not a tool |
| 1772–1819 |  18. Building the executor — `create_agent` |
| 1784–1791 |   Binding tools directly onto a bare model is a violation |
| 1792–1797 |   `create_react_agent` is superseded |
| 1798–1810 |   deepagents is not a dependency |
| 1811–1819 |   The structured response and the coaching text coexist |
| 1820–2141 |  19. The middleware stack — eight, in order |
| 1842–1888 |   Ordering rules that bind |
| 1889–1900 |   Three independent retry caps |
| 1901–1944 |   19.1 `BeforeModelStateInjection` — injection timing |
| 1945–1960 |   19.2 `DMAICSkillsMiddleware` — progressive disclosure |
| 1961–2000 |   19.3 `SummarizationMiddleware` — context compression |
| 2001–2027 |   19.4 `ModelRetryMiddleware` — API-level retry |
| 2028–2040 |   19.5 `ToolRetryMiddleware` — tool-level retry |
| 2041–2063 |   19.6 `ContradictionDetectionMiddleware` — the mid-phase check |
| 2064–2098 |   19.7 `CoherenceMiddleware` — validation Layer 2a |
| 2099–2129 |   19.8 `DMAICGraderMiddleware` — coaching process quality |
| 2130–2141 |   19.9 Middleware deliberately NOT used |
| 2142–2216 |  20. `CoachingResponse` — the per-turn schema |
| 2196–2199 |   The executor node writes the response into state |
| 2200–2206 |   The executor's `response_format` is `CoachingResponse`, never a phase Output |
| 2207–2216 |   What structured output does NOT give you |
| 2217–2328 |  21. LLM roles, temperature, and the factory |
| 2237–2245 |   Factory only |
| 2246–2266 |   Roles |
| 2267–2283 |   Temperature |
| 2284–2328 |   Structured output — scoped by call type |
| 2329–2392 |  22. Prompts |
| 2355–2375 |   The memory hierarchy paragraph is mandatory |
| 2376–2392 |   Anti-hallucination guards are mandatory |
| 2393–3171 | Part V — Knowledge and Retrieval |
| 2397–2752 |  23. The three indexes |
| 2409–2459 |   23.1 `improve_knowledge_index` — methodology |
| 2460–2585 |   23.2 `improve_evidence_index` — Belt-uploaded evidence |
| 2505–2529 |    Supersession deletes; it does not flag |
| 2530–2585 |    Two Azure behaviours govern the migration |
| 2586–2658 |   23.2.1 The `role` vocabulary — ratified, not invented per phase |
| 2625–2658 |    `unclassified (pre-ask-binding)` is a MIGRATION SENTINEL, not a thirteenth role |
| 2659–2707 |   23.3 `improve_case_index` — case records (cross-case memory) |
| 2708–2718 |   The internal phase key is `analyse`, never `analyse_phase` |
| 2719–2743 |   23.4 The write-path trap that made `phase_relevance` unfilterable |
| 2744–2752 |   23.5 Schema change procedure |
| 2753–2881 |  24. The three `rag_lookup_*` tools |
| 2771–2828 |   `rag_lookup_evidence` returns a structured record, not rendered text |
| 2829–2841 |   RAG via tool, never via prepended system message |
| 2842–2866 |   The retrieval mechanism |
| 2867–2874 |   `belt_level` filtering is OFF by default |
| 2875–2881 |   `source_file` and `page_number` are returned, never filtered |
| 2882–2947 |  25. Multi-query and Reciprocal Rank Fusion |
| 2891–2907 |   Why it is mandatory |
| 2908–2914 |   The implementation |
| 2915–2936 |   `MultiQueryRetriever` and `EnsembleRetriever` are BANNED |
| 2937–2947 |   Encapsulation |
| 2948–3081 |  26. Multi-hop retrieval |
| 2963–2999 |   The hop cap is `RemainingSteps` |
| 3000–3018 |   Per-phase policy |
| 3019–3063 |   Planned multi-hop — the Analyse pipeline |
| 3064–3081 |   **UNVERIFIED** — planned multi-hop is Analyse-only |
| 3082–3128 |  27. Retrieval failure semantics |
| 3093–3101 |   Never wrap a retrieval call in a bare `except Exception` returning `[]` |
| 3102–3111 |   Three rules that each have already bitten |
| 3112–3128 |   The coach-facing message must not read as absence |
| 3129–3171 |  28. Memory taxonomy |
| 3147–3171 |   The static/dynamic split is the part that matters |
| 3172–3518 | Part VI — Tools |
| 3176–3333 |  29. The data channel and the universal eight |
| 3182–3217 |   29.1 There is no MCP — the data-channel decision |
| 3218–3260 |   29.2 The universal eight |
| 3226–3260 |    `load_evidence_series` joins the set — RATIFIED 2026-09-09 |
| 3261–3270 |   29.3 `record_field` is RETIRED and may not be reintroduced |
| 3271–3333 |   29.4 Cross-agent tools — a third category, present but NOT BOUND |
| 3334–3408 |  30. Computation tools and per-phase binding |
| 3339–3376 |   Tool sets are per phase, not universal |
| 3377–3382 |   Each of the 20 is a separate named tool |
| 3383–3391 |   All 20 are pure functions |
| 3392–3401 |   `imr_chart_limits` — the choice that is usually wrong by default |
| 3402–3408 |   Tool decisions are the model's, not the graph's |
| 3409–3441 |  31. Tool arg schemas and docstrings |
| 3415–3420 |   Every `@tool` uses `args_schema=` |
| 3421–3441 |   Docstrings are interface, not commentary |
| 3442–3518 |  32. Phase skills — SKILL.md |
| 3465–3469 |   Each skill's `allowed-tools` MUST match that phase's subset in §30 |
| 3470–3479 |   Progressive disclosure — three levels |
| 3480–3485 |   Storage backend: `FilesystemBackend` |
| 3486–3507 |   Each SKILL.md must carry |
| 3508–3518 |   Two distinct kinds of skill exist in this repository |
| 3519–4099 | Part VII — Validation and Gates |
| 3526–3646 |  33. The nine-step HITL gate |
| 3547–3560 |   Two quality checks, two actors, two moments |
| 3561–3572 |   Gates are one-way doors, with exactly one defined exception |
| 3573–3577 |   Implementation: graph-level `interrupt()` |
| 3578–3608 |   33.1 The two-node split |
| 3609–3638 |   33.2 `gate_apply_node` writes the gate document TWICE |
| 3639–3646 |   33.3 The checkpoint commits only after Belt approval |
| 3647–3750 |  34. The four-layer validation stack |
| 3662–3669 |   Layer 2a is middleware; layers 2b–2d are the node |
| 3670–3676 |   Layer 2d is NOT `DMAICGraderMiddleware` |
| 3677–3682 |   Run cheapest first |
| 3683–3692 |   The counter and the feedback |
| 3693–3702 |   Layer 2b is the only deterministic layer, deliberately |
| 3703–3714 |   Per-phase constraint sets |
| 3715–3724 |   34.1 Where each check fires |
| 3725–3750 |   34.2 The self-healing hierarchy and the transparency principle |
| 3751–3886 |  35. Two tiers of field, and the `warning` verdict |
| 3757–3771 |   The problem this solves |
| 3772–3788 |   Three distinct things check these fields, and conflating them is a design error |
| 3789–3837 |   Gate-required fields by phase |
| 3838–3854 |   The grader's verdict has three statuses |
| 3855–3862 |   Why two tiers |
| 3863–3886 |   The grader is belt-level aware |
| 3887–3980 |  36. Two graders — and why they are not redundant |
| 3906–3919 |   Why both exist |
| 3920–3943 |   `COACHING_QUALITY_RUBRIC` |
| 3944–3953 |   Mechanism, both graders |
| 3954–3963 |   Three criteria are verified deterministically, not by judgment |
| 3964–3980 |   The ratified rubric coverage |
| 3981–4077 |  37. Mid-phase contradiction and the re-approval cascade |
| 3987–4008 |   The check runs every turn, not only at gates |
| 4009–4042 |   §37 governs a GATE-COMMITTED value only |
| 4043–4056 |   There is NO tolerance threshold, and none may be added |
| 4057–4064 |   The re-approval cascade |
| 4065–4077 |   The cascade has a hard dependency on compensating actions |
| 4078–4099 |  38. Escalation |
| 4100–5680 | Part VIII — The DMAIC Domain |
| 4107–5301 |  39. The five phases |
| 4125–4139 |   The measurement thread that runs across three phases |
| 4140–4374 |   39.1 Define phase, complete specification |
| 4147–4154 |    39.1.1 Purpose |
| 4155–4217 |    39.1.2 The ordered field list — the `field_index` sequence (closes G-38) |
| 4218–4232 |    39.1.3 The composed-problem-statement rule (binding) |
| 4233–4247 |    39.1.4 The `team` structure |
| 4248–4257 |    39.1.5 SIPOC handling |
| 4258–4269 |    39.1.6 Gate, storage, progress view |
| 4270–4288 |    39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4289–4295 |    39.1.8 The other four phases |
| 4296–4328 |    39.1.9 The metric registry and Define's placeholder |
| 4329–4336 |    39.1.10 Tools bound to Define |
| 4337–4344 |    39.1.11 Conditions — routing and the gate |
| 4345–4352 |    39.1.12 State parameters — Define's use of `PhaseState` |
| 4353–4360 |    39.1.13 Metric literacy — what each metric means |
| 4361–4374 |    39.1.14 Cross-phase reads and writes |
| 4375–4630 |   39.2 Measure phase, complete specification |
| 4385–4393 |    39.2.1 Purpose |
| 4394–4416 |    39.2.2 The ordered field list — the `field_index` sequence |
| 4417–4477 |    39.2.3 The metric registry and Measure's placeholder |
| 4478–4497 |    39.2.4 SIPOC → the detailed process map |
| 4498–4519 |    39.2.5 Tools bound to Measure |
| 4520–4549 |    39.2.6 Conditions — sequence locks, routing, and the gate |
| 4550–4567 |    39.2.7 State parameters — Measure's use of `PhaseState` |
| 4568–4584 |    39.2.8 Metric literacy — what each metric means |
| 4585–4598 |    39.2.9 Gate, storage, progress view |
| 4599–4607 |    39.2.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4608–4624 |    39.2.11 Cross-phase reads and writes |
| 4625–4630 |    39.2.12 The other two phases |
| 4631–4860 |   39.3 Analyse phase, complete specification |
| 4641–4650 |    39.3.1 Purpose |
| 4651–4676 |    39.3.2 The ordered field list — the `field_index` sequence |
| 4677–4713 |    39.3.3 The metric registry and Analyse's placeholder (linkage form — closes F-13) |
| 4714–4733 |    39.3.4 Two movements — generate, then validate |
| 4734–4756 |    39.3.5 Tools bound to Analyse |
| 4757–4785 |    39.3.6 Conditions — methodology guards, routing, and the gate |
| 4786–4799 |    39.3.7 State parameters — Analyse's use of `PhaseState` |
| 4800–4815 |    39.3.8 Metric literacy — what each metric and statistic means |
| 4816–4827 |    39.3.9 Gate, storage, progress view |
| 4828–4836 |    39.3.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4837–4854 |    39.3.11 Cross-phase reads and writes |
| 4855–4860 |    39.3.12 The other phase |
| 4861–5063 |   39.4 Improve phase, complete specification |
| 4871–4879 |    39.4.1 Purpose |
| 4880–4900 |    39.4.2 The ordered field list — the `field_index` sequence |
| 4901–4919 |    39.4.3 The metric registry and Improve's placeholder (linkage form) |
| 4920–4937 |    39.4.4 Two movements — generate-and-select, then pilot-and-prove |
| 4938–4956 |    39.4.5 Tools bound to Improve |
| 4957–4988 |    39.4.6 Conditions — methodology guards, DOE belt-gating, routing, gate |
| 4989–5002 |    39.4.7 State parameters — Improve's use of `PhaseState` |
| 5003–5016 |    39.4.8 Metric literacy — what each metric and statistic means |
| 5017–5028 |    39.4.9 Gate, storage, progress view |
| 5029–5038 |    39.4.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5039–5055 |    39.4.11 Cross-phase reads and writes |
| 5056–5063 |    39.4.12 The last phase |
| 5064–5301 |   39.5 Control phase, complete specification |
| 5074–5082 |    39.5.1 Purpose |
| 5083–5111 |    39.5.2 The ordered field list — the `field_index` sequence |
| 5112–5141 |    39.5.3 The metric registry, the comparison, and single authority (closes F-14) |
| 5142–5158 |    39.5.4 Two movements — confirm it held, then lock it in |
| 5159–5178 |    39.5.5 Tools bound to Control |
| 5179–5211 |    39.5.6 Conditions — guards, routing, gate |
| 5212–5225 |    39.5.7 State parameters — Control's use of `PhaseState` |
| 5226–5240 |    39.5.8 Metric literacy — what each metric and statistic means |
| 5241–5254 |    39.5.9 Gate, storage, progress view |
| 5255–5265 |    39.5.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5266–5281 |    39.5.11 Cross-phase reads and writes — the thread closes here |
| 5282–5301 |    39.5.12 The measurement thread, closed |
| 5302–5397 |  40. The five `{Phase}Output` schemas |
| 5325–5343 |   Field counts |
| 5344–5355 |   The four gate-metadata fields |
| 5356–5369 |   Three fields are on all five schemas |
| 5370–5397 |   40.1 Gate assembly |
| 5398–5481 |  41. Structured dict fields, and FMEA |
| 5420–5431 |   The grader checks every sub-field is populated |
| 5432–5440 |   `control_plan` is `dict`, never `str` |
| 5441–5449 |   `stability_assessment` is checked BEFORE capability |
| 5450–5461 |   `experiment_justification` is Tier 1 and does not require an experiment |
| 5462–5481 |   FMEA has no field in any schema, and none may be added |
| 5482–5513 |  42. Cross-phase reference fields in practice |
| 5514–5680 |  43. The coaching method |
| 5532–5559 |   43.1 The seven-step computation pattern |
| 5560–5597 |   43.2 Show before asking |
| 5598–5620 |   43.3 The A→F session flow |
| 5621–5652 |   43.4 The live gate document preview |
| 5653–5662 |   43.5 No external URLs |
| 5663–5680 |   43.6 What the coach must not do |
| 5681–6037 | Part IX — Reliability |
| 5685–5713 |   43.7 Metric literacy — the metric, and the statistic |
| 5714–5742 |  44. The failure pipeline |
| 5743–5855 |  45. Timeouts and compensating actions |
| 5750–5781 |   Per-node timeouts — required on every phase executor node |
| 5782–5791 |   Composition order — retries run BEFORE the handler |
| 5792–5801 |   Node-level error handlers — required on every node with external writes |
| 5802–5807 |   Hand-written Saga orchestrators are BANNED |
| 5808–5816 |   Two dependencies on this rule, both correctness-critical |
| 5817–5848 |   Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST** |
| 5849–5855 |   `DeltaChannel` is NOT used |
| 5856–5971 |  46. The fallback chain and circuit breakers |
| 5862–5874 |   The v2.1 four-level chain |
| 5875–5881 |   Backoff strategy is chosen per level, not globally |
| 5882–5900 |   Level 3 cache |
| 5901–5916 |   Circuit breakers — three-state, two instances |
| 5917–5923 |   Degraded mode uses actual state, never a generic error |
| 5924–5931 |   HTTP 400 is NOT a fallback case |
| 5932–5971 |   46.1 Geographic redundancy — **DEFERRED** |
| 5972–6012 |  47. Disconnect policy — what a dropped client commits |
| 5989–5995 |   Ratified policy: ABANDON, not COMPLETE |
| 5996–6012 |   Five requirements |
| 6013–6037 |  48. Structured errors |
| 6038–6525 | Part X — Operations |
| 6042–6095 |  49. API surface |
| 6048–6057 |   One runtime |
| 6058–6065 |   Async by default |
| 6066–6089 |   Endpoints |
| 6090–6095 |   Envelopes are Pydantic v2 |
| 6096–6252 |  50. UI and language rules |
| 6103–6141 |   50.1 Coach response structure |
| 6142–6153 |   Plain language always |
| 6154–6161 |   Citations |
| 6162–6175 |   Contextual feedback |
| 6176–6182 |   Connection status before the first interaction |
| 6183–6188 |   The gate review screen |
| 6189–6227 |   The live gate document |
| 6228–6239 |   The all-gate-fields tab is the contradiction backstop |
| 6240–6252 |   The conflict resolution panel |
| 6253–6328 |  51. Tracing and observability |
| 6259–6269 |   LangSmith is mandatory |
| 6270–6302 |   `@traceable` on every custom function |
| 6303–6308 |   What gets traced |
| 6309–6316 |   P50/P99 latency is a coaching quality signal |
| 6317–6328 |   Logs |
| 6329–6383 |  52. Evaluation and regression testing |
| 6335–6342 |   Built alongside the refactor, not before it |
| 6343–6349 |   The dataset is authored jointly, not generated |
| 6350–6363 |   Minimum viable suite |
| 6364–6374 |   Rubrics and the eval dataset are complementary, not duplicative |
| 6375–6383 |   Two open validation questions this suite answers |
| 6384–6525 |  53. Configuration, dependencies and deployment |
| 6390–6406 |   Fail-fast environment validation |
| 6407–6430 |   Dependency floor |
| 6431–6441 |   `/verify-current-version` is a mandatory checkpoint |
| 6442–6449 |   Infrastructure not yet provisioned |
| 6450–6461 |   Deployment layer: FastAPI, not LangGraph Server |
| 6462–6525 |   53.1 Migration sequence |
| 6526–7094 | Part XI — Governance |
| 6530–6572 |  54. Where code is allowed to live |
| 6537–6554 |   Classes are permitted ONLY in these files |
| 6555–6572 |   Target folder structure |
| 6573–6943 |  55. Anti-drift |
| 6587–6601 |   Rule numbers are load-bearing |
| 6602–6612 |   The registry guards code, not documentation |
| 6613–6618 |   Verification discipline |
| 6619–6641 |   Reference sweeps must use raw `grep -rn`, never a gitignore-filtered tool |
| 6642–6692 |   55.1 Spec-layer governance rules |
| 6693–6775 |   55.2 The BUILT markers, and the paths that oblige a re-check |
| 6776–6856 |   55.3 The phase completeness set — what one phase actually traverses |
| 6857–6906 |   55.4 Facts have one owner — the ratified minimum |
| 6907–6943 |   55.5 The commit gates govern. The rule files are advisory context. |
| 6944–7094 |  56. Amendment procedure |
| 6971–7014 |   56.0 What changed about amending, when the rules stopped being one file |
| 7015–7033 |   56.0.1 Rule, reference, and owned fact — three destinations |
| 7034–7076 |   56.1 A phase is one atomic unit — schema, validator, skill |
| 7077–7094 |   What requires an amendment rather than a routine change |
| 7095–11439 | Part XII — Specification |
| 7105–7128 |   56.2 The rule lands here; the reasoning lands in the commit |
| 7129–7162 |   56.3 The tree at HEAD is the only source of truth |
| 7163–7424 |  57. The specification layer — how to read and write a spec entry |
| 7170–7190 |   Why this Part exists |
| 7191–7206 |   The five structural rules |
| 7207–7221 |   Entry identity and traceability |
| 7222–7269 |   The entry template — three layers |
| 7270–7281 |   How gaps are marked |
| 7282–7298 |   57.1 The two calibrated samples |
| 7299–7352 |   57.2 SAMPLE 1 — CLASS TEMPLATE — S-C01 `SupervisorState` |
| 7302–7352 |    SPEC — `SupervisorState` |
| 7353–7403 |   57.3 SAMPLE 2 — FUNCTION/NODE TEMPLATE — S-F04 `phase_executor` (the coach node) |
| 7357–7403 |    SPEC — `phase_executor` (the coach node) |
| 7404–7424 |   57.4 Entry index |
| 7425–8754 |  58. Spec — graph management |
| 7435–7438 |   58.1 S-C01 · `SupervisorState` |
| 7439–7604 |   58.2 S-C02 · `PhaseState` |
| 7605–7623 |   58.3 S-C03 · Per-phase use of `PhaseState` |
| 7624–7699 |   58.4 S-C04 · `CoachingPlan` |
| 7700–7809 |   58.5 S-C05 · `CoachingResponse` |
| 7810–7861 |   58.6 S-C06 · `AzureBlobStore` |
| 7862–7907 |   58.7 S-C07 · `AzureBlobCheckpointSaver` |
| 7908–7954 |   58.8 S-C08 · `ImproveBlobClient` |
| 7955–8017 |   58.9 S-C09 · `storage/models.py` — the record models |
| 8018–8081 |   58.10 S-F01 · The supervisor graph — static edges |
| 8052–8061 |    SIPOC — at a glance |
| 8062–8081 |    Behaviors (EARS) |
| 8082–8127 |   58.11 S-F02 · `build_phase_subgraph(phase, llm)` |
| 8100–8109 |    SIPOC — at a glance |
| 8110–8127 |    Behaviors (EARS) |
| 8128–8168 |   58.12 S-F03 · `phase_planner` node |
| 8139–8148 |    SIPOC — at a glance |
| 8149–8168 |    Behaviors (EARS) |
| 8169–8180 |   58.13 S-F04 · `phase_executor` node |
| 8181–8242 |   58.14 S-F05 · `validation_stack` node |
| 8191–8200 |    SIPOC — at a glance |
| 8201–8212 |    Behaviors (EARS) |
| 8213–8242 |    ⚠ AI-ACT — high-risk surface |
| 8243–8294 |   58.15 S-F06 · `gate_review_node` |
| 8253–8262 |    SIPOC — at a glance |
| 8263–8270 |    Behaviors (EARS) |
| 8271–8294 |    ⚠ AI-ACT — high-risk surface |
| 8295–8362 |   58.16 S-F07 · `gate_apply_node` |
| 8316–8325 |    SIPOC — at a glance |
| 8326–8338 |    Behaviors (EARS) |
| 8339–8362 |    ⚠ AI-ACT — high-risk surface |
| 8363–8398 |   58.17 S-F08 · The escalation subgraph |
| 8371–8380 |    SIPOC — at a glance |
| 8381–8398 |    Behaviors (EARS) |
| 8399–8467 |   58.18 S-F09 · `analyse_executor_node` |
| 8439–8448 |    SIPOC — at a glance |
| 8449–8467 |    Behaviors (EARS) |
| 8468–8561 |   58.19 S-F10 · `define_input_mapper` |
| 8511–8523 |    SIPOC — at a glance |
| 8524–8552 |    Execution site — where a boundary mapper actually runs |
| 8553–8561 |    Behaviors (EARS) |
| 8562–8615 |   58.20 S-F11 · `define_output_mapper` |
| 8591–8600 |    SIPOC — at a glance |
| 8601–8615 |    Behaviors (EARS) |
| 8616–8665 |   58.21 S-F12 · The Measure, Analyse, Improve and Control mapper pairs |
| 8624–8633 |    SIPOC — at a glance |
| 8634–8665 |    Behaviors (EARS) |
| 8666–8754 |   58.22 S-F13 · Level 2 `Command` routing |
| 8683–8700 |    DP1 — the planner owns the field / gate decision |
| 8701–8721 |    DP2 — the validation stack's three exits |
| 8722–8742 |    DP3 — the gate exits |
| 8743–8754 |    What is settled and binds |
| 8755–9137 |  59. Spec — knowledge and retrieval |
| 8768–8797 |   59.1 S-C16 · `Hop` |
| 8798–8844 |   59.2 S-C17 · `Plan` — the hop decomposition plan |
| 8845–8881 |   59.3 S-C18 · `SynthesisOutput` |
| 8882–8898 |   59.4 S-C19 · `QueryVariants` |
| 8899–8945 |   59.5 S-F14 · `rag_lookup_methodology` |
| 8920–8929 |    SIPOC — at a glance |
| 8930–8945 |    Behaviors (EARS) |
| 8946–8993 |   59.6 S-F15 · `rag_lookup_evidence` |
| 8969–8978 |    SIPOC — at a glance |
| 8979–8993 |    Behaviors (EARS) |
| 8994–9040 |   59.7 S-F16 · `rag_lookup_case_history` |
| 9017–9026 |    SIPOC — at a glance |
| 9027–9040 |    Behaviors (EARS) |
| 9041–9091 |   59.8 S-F17 · `reciprocal_rank_fusion` |
| 9068–9077 |    SIPOC — at a glance |
| 9078–9091 |    Behaviors (EARS) |
| 9092–9137 |   59.9 S-F18 · The retriever layer — `search_knowledge`, `search_cases`, `search_evidence` |
| 9120–9137 |    SIPOC — at a glance |
| 9138–9423 |  60. Spec — tools |
| 9156–9189 |   60.1 S-F19 · `propose_template` |
| 9169–9189 |    SIPOC — at a glance |
| 9190–9228 |   60.2 S-F20 · `propose_diagram` |
| 9205–9214 |    SIPOC — at a glance |
| 9215–9228 |    Behaviors (EARS) |
| 9229–9270 |   60.3 S-F21 · `check_gate_status` |
| 9244–9253 |    SIPOC — at a glance |
| 9254–9270 |    Behaviors (EARS) |
| 9271–9306 |   60.4 S-F22 · `request_human_approval` |
| 9285–9306 |    SIPOC — at a glance |
| 9307–9323 |   60.5 S-F23 · `load_skill(name)` |
| 9324–9368 |   60.6 S-F24 · The 20 computation tools |
| 9347–9368 |    Behaviors (EARS) — binding on all twenty |
| 9369–9423 |   60.7 S-F57 · `load_evidence_series(blob_path, column)` |
| 9394–9403 |    SIPOC — at a glance |
| 9404–9423 |    Behaviors (EARS) |
| 9424–9676 |  61. Spec — the coaching agent's middleware |
| 9442–9504 |   61.1 S-C10 · `ContradictionDetectionMiddleware` |
| 9464–9473 |    Behaviors (EARS) |
| 9474–9504 |    ⚠ AI-ACT — high-risk surface |
| 9505–9546 |   61.2 S-C11 · `BeforeModelStateInjection` |
| 9518–9546 |    Behaviors (EARS) |
| 9547–9586 |   61.3 S-C12 · `DMAICSkillsMiddleware` |
| 9567–9586 |    Behaviors (EARS) |
| 9587–9623 |   61.4 S-C13 · `CoherenceMiddleware` |
| 9601–9623 |    Behaviors (EARS) |
| 9624–9659 |   61.5 S-C14 · `DMAICGraderMiddleware` |
| 9634–9659 |    Behaviors (EARS) |
| 9660–9676 |   61.6 S-C15 · `HITLInterrupt` |
| 9677–10084 |  62. Spec — validation and gates |
| 9691–9733 |   62.1 S-C20 · `CriterionVerdict` |
| 9734–9751 |   62.2 S-C21 · `GraderVerdict` |
| 9752–9765 |   62.3 S-C22 · `CoachingGraderVerdict` |
| 9766–9777 |   62.4 S-C23 · `CoherenceResult` |
| 9778–9792 |   62.5 S-C24 · `ConstraintCheckResult` / `ConstraintVerdict` |
| 9793–9805 |   62.6 S-C25 · `PolicyAdvisoryResult` |
| 9806–9842 |   62.7 S-C26 · `DMAICGateValidator` |
| 9843–9877 |   62.8 S-F25 · Layer 2c — the constraint check |
| 9852–9861 |    SIPOC — at a glance |
| 9862–9877 |    Behaviors (EARS) |
| 9878–9925 |   62.9 S-F26 · Layer 2d — the gate grader |
| 9893–9902 |    SIPOC — at a glance |
| 9903–9925 |    Behaviors (EARS) |
| 9926–9967 |   62.10 S-F27 · The policy advisory |
| 9941–9950 |    SIPOC — at a glance |
| 9951–9967 |    Behaviors (EARS) |
| 9968–10084 |   62.11 S-F28 · Gate document assembly |
| 10056–10065 |    SIPOC — at a glance |
| 10066–10084 |    Behaviors (EARS) |
| 10085–10606 |  63. Spec — the DMAIC gate documents |
| 10103–10171 |   63.1 S-C27 · `DefineOutput` |
| 10172–10212 |   63.2 S-C28 · `MeasureOutput` |
| 10213–10270 |   63.3 S-C29 · `AnalyseOutput` |
| 10271–10330 |   63.4 S-C30 · `ImproveOutput` |
| 10331–10402 |   63.5 S-C31 · `ControlOutput` |
| 10403–10469 |   63.6 S-C32 · The three cross-phase reference dicts |
| 10470–10511 |   63.7 S-C33 · The three structured dict fields |
| 10512–10550 |   63.8 S-C38 · `metric_definitions` — the project metric registry |
| 10551–10606 |   63.9 S-C39 · `phase_metrics` — the per-phase placeholder |
| 10607–10895 |  64. Spec — reliability |
| 10618–10658 |   64.1 S-C34 · `AgentImproveError` |
| 10659–10697 |   64.2 S-C35 · `CircuitBreaker` |
| 10698–10784 |   64.3 S-F29 · `phase_error_recovery` |
| 10726–10735 |    SIPOC — at a glance |
| 10736–10784 |    Behaviors (EARS) |
| 10785–10833 |   64.4 S-F30 · `degraded_mode_response` |
| 10806–10815 |    SIPOC — at a glance |
| 10816–10833 |    Behaviors (EARS) |
| 10834–10852 |   64.5 S-F31 · `synthesise_partial` |
| 10853–10877 |   64.6 S-F32 · `delete_or_flag_stale_in_case_index` |
| 10878–10895 |   64.7 S-F33 · `degraded_coaching_response` node |
| 10896–11072 |  65. Spec — API, UI and evidence |
| 10906–10926 |   65.1 S-C36 · `CitationRecord` and `CitationBundle` |
| 10927–10944 |   65.2 S-C37 · The API envelopes |
| 10945–10997 |   65.3 S-F34 · The API surface |
| 10967–10976 |    SIPOC — at a glance |
| 10977–10997 |    Behaviors (EARS) |
| 10998–11037 |   65.4 S-F35 · The upload handler |
| 11023–11037 |    Behaviors (EARS) |
| 11038–11072 |   65.5 S-F36 · The `improve_case_index` write path |
| 11073–11083 |  66. The SPEC-GAP register — MOVED |
| 11084–11177 |  67. EU AI Act compliance posture |
| 11091–11106 |   67.1 The deadlines are now fixed |
| 11107–11132 |   67.2 The classification question — open, and not answered here |
| 11133–11150 |   67.3 The eight core provider obligations |
| 11151–11161 |   67.4 One compliance finding is already recorded in this document |
| 11162–11177 |   67.5 Compliance-source discipline |
| 11178–11258 |  68. The DORA-structured compliance risk register |
| 11185–11202 |   68.1 Why DORA structure |
| 11203–11219 |   68.2 The register |
| 11220–11243 |   68.3 Pending classification — not register rows |
| 11244–11258 |   68.4 The infrastructure risk already on record |
| 11259–11439 |  69. Spec — computation tools |
| 11288–11359 |   69.1 Common conventions — stated once, binding on all twenty |
| 11360–11365 |   69.2 S-F37 · Define — 1 tool |
| 11366–11378 |   69.3 S-F38–S-F45 · Measure — 8 tools |
| 11379–11388 |   69.4 S-F46–S-F50 · Analyse — 5 tools |
| 11389–11394 |   69.5 S-F51 · Improve — 1 tool |
| 11395–11412 |   69.6 S-F52–S-F56 · Control — 5 tools |
| 11413–11439 |   69.7 The Measure control-chart boundary — a tool that is deliberately absent |
| 11440–11669 | Appendices |
| 11444–11459 |  Appendix A — Provenance index |
| 11450–11453 |   A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference |
| 11454–11459 |   A.2 `agent-improve/ARCHITECTURE.md` → this reference |
| 11460–11490 |  Appendix B — Deferred backlog |
| 11491–11556 |  Appendix C — Trusted sources |
| 11497–11516 |   Tier 1 — current, authoritative |
| 11517–11535 |   Tier 1 — compliance |
| 11536–11539 |   Tier 2 — official announcements |
| 11540–11543 |   Tier 3 — informed practitioner, cross-check before citing |
| 11544–11550 |   Downgraded — historical |
| 11551–11556 |   Excluded |
| 11557–11637 |  Appendix D — Retired names, banned patterns, and exclusions |
| 11559–11582 |   D.1 Retired names — never reintroduce |
| 11583–11626 |   D.2 Banned patterns |
| 11627–11637 |   D.3 Architecturally excluded — not deferred |
| 11638–11646 |  Appendix E — Current state |
| 11647–11669 |  Appendix F — The v2.2.16 registers |
| 11653–11658 |   F.1 Decisions Resolved (v2.2) — the former §17 |
| 11659–11669 |   F.2 Change Log — the former §18 |
| 11663–11669 |    F.2.1 Amendment procedure — the former §18.1 |
