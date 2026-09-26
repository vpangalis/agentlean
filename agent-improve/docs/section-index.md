# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 11666 lines

| Lines | Heading |
|---|---|
| 27–49 |  🗺 Where state lives — a MAP, not a definition |
| 50–257 | Agentic Architecture Reference |
| 152–257 |  About this document |
| 158–215 |   Scope — three agents, one architecture |
| 216–230 |   The two-document division |
| 231–245 |   Section numbering and provenance |
| 246–257 |   Reading conventions |
| 258–549 | Part I — Orientation |
| 262–338 |  1. What Agent Improve is |
| 282–308 |   What makes it architecturally distinctive |
| 309–338 |   The runtime stack |
| 339–390 |  2. How to read this document |
| 345–361 |   By what you are trying to do |
| 362–390 |   Canonical ownership |
| 391–489 |  3. Terminology |
| 402–418 |   Structural primitives |
| 419–430 |   Role labels |
| 431–448 |   The recursion is two levels, not infinite |
| 449–463 |   "Harness" — two senses, do not conflate |
| 464–474 |   "Agent" — used carefully |
| 475–489 |   Things that are deliberately not levels |
| 490–549 |  4. Architecture at a glance |
| 533–549 |   The five things that shape everything else |
| 550–1277 | Part II — State and Persistence |
| 557–615 |  5. `SupervisorState` — orchestration only |
| 569–575 |   `gate_passed` is a dict, not a list |
| 576–587 |   `current_phase` and `phase_index` are derived, and kept anyway |
| 588–607 |   Four fields were removed as redundant, and may not return |
| 608–615 |   Artifacts are not here |
| 616–851 |  6. `PhaseState` — per-phase subgraph state |
| 631–662 |   `asks` — §56 AMENDMENT, ratified 2026-09-09 |
| 663–732 |   `field_log` — §56 AMENDMENT, ratified 2026-09-21 |
| 733–738 |   `draft`, `belt_edits` and `final` are `dict`, never `str` |
| 739–761 |   `coaching_plan` is one typed plan, not a queue |
| 762–777 |   `gate_attempts` — the field whose absence recreated a production bug |
| 778–798 |   `validator_feedback` and `belt_edits` are different, and must stay separate |
| 799–816 |   `citations` and `uploads` — the evidence trail |
| 817–834 |   `hop_results` and `synthesis_output` must be state, not node locals |
| 835–843 |   Per-phase variants |
| 844–851 |   Naming discipline |
| 852–928 |  7. Field typing law — every captured field is a string |
| 868–880 |   Why strings |
| 881–900 |   The one exception — three cross-phase reference dicts |
| 901–928 |   Computation results |
| 929–1021 |  8. The checkpointer / store split |
| 953–972 |   Phased backend |
| 973–984 |   Concurrency and atomicity |
| 985–1000 |   Why Blob, and not Cosmos / Tables / SQLite |
| 1001–1021 |   On-blob checkpoint format |
| 1022–1158 |  9. The Store — cross-phase artifacts and boundary mappers |
| 1063–1086 |   Namespace convention |
| 1087–1116 |   Why cross-phase data cannot travel on parent state |
| 1117–1137 |   Boundary mappers |
| 1138–1150 |   Two prohibitions that follow |
| 1151–1158 |   Ordering constraint |
| 1159–1216 |  10. Azure Blob — two distinct concerns |
| 1178–1203 |   Complete physical layout |
| 1204–1216 |   The case blob is not updated per turn |
| 1217–1277 |  11. `step_log` — the audit trail |
| 1238–1247 |   `artifacts` and `step_log` are separate fields and stay separate |
| 1248–1277 |   Entries carry deterministic keys, never a raw timestamp as identity |
| 1278–1648 | Part III — The Graph |
| 1284–1324 |  12. Topology |
| 1314–1324 |   The subgraph builder takes the phase as a parameter |
| 1325–1464 |  13. The phase subgraph — five nodes |
| 1402–1432 |   The subgraph is a cycle, not a pipeline |
| 1433–1445 |   Two node names are BANNED |
| 1446–1451 |   Leaf tools are NOT subgraph nodes |
| 1452–1464 |   The validation stack and the policy advisory are NOT tools |
| 1465–1500 |  14. Node contract |
| 1488–1500 |   Reflection is a node, not a private function |
| 1501–1565 |  15. Routing — static edges and `Command` |
| 1507–1524 |   The decision test |
| 1525–1530 |   Never mix static edges and `Command` from the same node |
| 1531–1558 |   Level 1 does not route — it advances |
| 1559–1565 |   No subgraph imports another subgraph's nodes |
| 1566–1648 |  16. `thread_id`, `checkpoint_ns`, and where persistence attaches |
| 1572–1587 |   One `thread_id` per project |
| 1588–1601 |   The checkpointer and store go on the parent graph ONLY |
| 1602–1628 |   The wrapper node must invoke the subgraph directly (G-44) |
| 1629–1648 |   `recursion_limit` is a backstop, not the hop cap |
| 1649–2390 | Part IV — The Coaching Agent |
| 1655–1769 |  17. The Planner / Executor contract |
| 1731–1761 |   `CoachingPlan` |
| 1762–1769 |   Extraction is structured output, not a node and not a tool |
| 1770–1817 |  18. Building the executor — `create_agent` |
| 1782–1789 |   Binding tools directly onto a bare model is a violation |
| 1790–1795 |   `create_react_agent` is superseded |
| 1796–1808 |   deepagents is not a dependency |
| 1809–1817 |   The structured response and the coaching text coexist |
| 1818–2139 |  19. The middleware stack — eight, in order |
| 1840–1886 |   Ordering rules that bind |
| 1887–1898 |   Three independent retry caps |
| 1899–1942 |   19.1 `BeforeModelStateInjection` — injection timing |
| 1943–1958 |   19.2 `DMAICSkillsMiddleware` — progressive disclosure |
| 1959–1998 |   19.3 `SummarizationMiddleware` — context compression |
| 1999–2025 |   19.4 `ModelRetryMiddleware` — API-level retry |
| 2026–2038 |   19.5 `ToolRetryMiddleware` — tool-level retry |
| 2039–2061 |   19.6 `ContradictionDetectionMiddleware` — the mid-phase check |
| 2062–2096 |   19.7 `CoherenceMiddleware` — validation Layer 2a |
| 2097–2127 |   19.8 `DMAICGraderMiddleware` — coaching process quality |
| 2128–2139 |   19.9 Middleware deliberately NOT used |
| 2140–2214 |  20. `CoachingResponse` — the per-turn schema |
| 2194–2197 |   The executor node writes the response into state |
| 2198–2204 |   The executor's `response_format` is `CoachingResponse`, never a phase Output |
| 2205–2214 |   What structured output does NOT give you |
| 2215–2326 |  21. LLM roles, temperature, and the factory |
| 2235–2243 |   Factory only |
| 2244–2264 |   Roles |
| 2265–2281 |   Temperature |
| 2282–2326 |   Structured output — scoped by call type |
| 2327–2390 |  22. Prompts |
| 2353–2373 |   The memory hierarchy paragraph is mandatory |
| 2374–2390 |   Anti-hallucination guards are mandatory |
| 2391–3169 | Part V — Knowledge and Retrieval |
| 2395–2750 |  23. The three indexes |
| 2407–2457 |   23.1 `improve_knowledge_index` — methodology |
| 2458–2583 |   23.2 `improve_evidence_index` — Belt-uploaded evidence |
| 2503–2527 |    Supersession deletes; it does not flag |
| 2528–2583 |    Two Azure behaviours govern the migration |
| 2584–2656 |   23.2.1 The `role` vocabulary — ratified, not invented per phase |
| 2623–2656 |    `unclassified (pre-ask-binding)` is a MIGRATION SENTINEL, not a thirteenth role |
| 2657–2705 |   23.3 `improve_case_index` — case records (cross-case memory) |
| 2706–2716 |   The internal phase key is `analyse`, never `analyse_phase` |
| 2717–2741 |   23.4 The write-path trap that made `phase_relevance` unfilterable |
| 2742–2750 |   23.5 Schema change procedure |
| 2751–2879 |  24. The three `rag_lookup_*` tools |
| 2769–2826 |   `rag_lookup_evidence` returns a structured record, not rendered text |
| 2827–2839 |   RAG via tool, never via prepended system message |
| 2840–2864 |   The retrieval mechanism |
| 2865–2872 |   `belt_level` filtering is OFF by default |
| 2873–2879 |   `source_file` and `page_number` are returned, never filtered |
| 2880–2945 |  25. Multi-query and Reciprocal Rank Fusion |
| 2889–2905 |   Why it is mandatory |
| 2906–2912 |   The implementation |
| 2913–2934 |   `MultiQueryRetriever` and `EnsembleRetriever` are BANNED |
| 2935–2945 |   Encapsulation |
| 2946–3079 |  26. Multi-hop retrieval |
| 2961–2997 |   The hop cap is `RemainingSteps` |
| 2998–3016 |   Per-phase policy |
| 3017–3061 |   Planned multi-hop — the Analyse pipeline |
| 3062–3079 |   **UNVERIFIED** — planned multi-hop is Analyse-only |
| 3080–3126 |  27. Retrieval failure semantics |
| 3091–3099 |   Never wrap a retrieval call in a bare `except Exception` returning `[]` |
| 3100–3109 |   Three rules that each have already bitten |
| 3110–3126 |   The coach-facing message must not read as absence |
| 3127–3169 |  28. Memory taxonomy |
| 3145–3169 |   The static/dynamic split is the part that matters |
| 3170–3516 | Part VI — Tools |
| 3174–3331 |  29. The data channel and the universal eight |
| 3180–3215 |   29.1 There is no MCP — the data-channel decision |
| 3216–3258 |   29.2 The universal eight |
| 3224–3258 |    `load_evidence_series` joins the set — RATIFIED 2026-09-09 |
| 3259–3268 |   29.3 `record_field` is RETIRED and may not be reintroduced |
| 3269–3331 |   29.4 Cross-agent tools — a third category, present but NOT BOUND |
| 3332–3406 |  30. Computation tools and per-phase binding |
| 3337–3374 |   Tool sets are per phase, not universal |
| 3375–3380 |   Each of the 20 is a separate named tool |
| 3381–3389 |   All 20 are pure functions |
| 3390–3399 |   `imr_chart_limits` — the choice that is usually wrong by default |
| 3400–3406 |   Tool decisions are the model's, not the graph's |
| 3407–3439 |  31. Tool arg schemas and docstrings |
| 3413–3418 |   Every `@tool` uses `args_schema=` |
| 3419–3439 |   Docstrings are interface, not commentary |
| 3440–3516 |  32. Phase skills — SKILL.md |
| 3463–3467 |   Each skill's `allowed-tools` MUST match that phase's subset in §30 |
| 3468–3477 |   Progressive disclosure — three levels |
| 3478–3483 |   Storage backend: `FilesystemBackend` |
| 3484–3505 |   Each SKILL.md must carry |
| 3506–3516 |   Two distinct kinds of skill exist in this repository |
| 3517–4097 | Part VII — Validation and Gates |
| 3524–3644 |  33. The nine-step HITL gate |
| 3545–3558 |   Two quality checks, two actors, two moments |
| 3559–3570 |   Gates are one-way doors, with exactly one defined exception |
| 3571–3575 |   Implementation: graph-level `interrupt()` |
| 3576–3606 |   33.1 The two-node split |
| 3607–3636 |   33.2 `gate_apply_node` writes the gate document TWICE |
| 3637–3644 |   33.3 The checkpoint commits only after Belt approval |
| 3645–3748 |  34. The four-layer validation stack |
| 3660–3667 |   Layer 2a is middleware; layers 2b–2d are the node |
| 3668–3674 |   Layer 2d is NOT `DMAICGraderMiddleware` |
| 3675–3680 |   Run cheapest first |
| 3681–3690 |   The counter and the feedback |
| 3691–3700 |   Layer 2b is the only deterministic layer, deliberately |
| 3701–3712 |   Per-phase constraint sets |
| 3713–3722 |   34.1 Where each check fires |
| 3723–3748 |   34.2 The self-healing hierarchy and the transparency principle |
| 3749–3884 |  35. Two tiers of field, and the `warning` verdict |
| 3755–3769 |   The problem this solves |
| 3770–3786 |   Three distinct things check these fields, and conflating them is a design error |
| 3787–3835 |   Gate-required fields by phase |
| 3836–3852 |   The grader's verdict has three statuses |
| 3853–3860 |   Why two tiers |
| 3861–3884 |   The grader is belt-level aware |
| 3885–3978 |  36. Two graders — and why they are not redundant |
| 3904–3917 |   Why both exist |
| 3918–3941 |   `COACHING_QUALITY_RUBRIC` |
| 3942–3951 |   Mechanism, both graders |
| 3952–3961 |   Three criteria are verified deterministically, not by judgment |
| 3962–3978 |   The ratified rubric coverage |
| 3979–4075 |  37. Mid-phase contradiction and the re-approval cascade |
| 3985–4006 |   The check runs every turn, not only at gates |
| 4007–4040 |   §37 governs a GATE-COMMITTED value only |
| 4041–4054 |   There is NO tolerance threshold, and none may be added |
| 4055–4062 |   The re-approval cascade |
| 4063–4075 |   The cascade has a hard dependency on compensating actions |
| 4076–4097 |  38. Escalation |
| 4098–5678 | Part VIII — The DMAIC Domain |
| 4105–5299 |  39. The five phases |
| 4123–4137 |   The measurement thread that runs across three phases |
| 4138–4372 |   39.1 Define phase, complete specification |
| 4145–4152 |    39.1.1 Purpose |
| 4153–4215 |    39.1.2 The ordered field list — the `field_index` sequence (closes G-38) |
| 4216–4230 |    39.1.3 The composed-problem-statement rule (binding) |
| 4231–4245 |    39.1.4 The `team` structure |
| 4246–4255 |    39.1.5 SIPOC handling |
| 4256–4267 |    39.1.6 Gate, storage, progress view |
| 4268–4286 |    39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4287–4293 |    39.1.8 The other four phases |
| 4294–4326 |    39.1.9 The metric registry and Define's placeholder |
| 4327–4334 |    39.1.10 Tools bound to Define |
| 4335–4342 |    39.1.11 Conditions — routing and the gate |
| 4343–4350 |    39.1.12 State parameters — Define's use of `PhaseState` |
| 4351–4358 |    39.1.13 Metric literacy — what each metric means |
| 4359–4372 |    39.1.14 Cross-phase reads and writes |
| 4373–4628 |   39.2 Measure phase, complete specification |
| 4383–4391 |    39.2.1 Purpose |
| 4392–4414 |    39.2.2 The ordered field list — the `field_index` sequence |
| 4415–4475 |    39.2.3 The metric registry and Measure's placeholder |
| 4476–4495 |    39.2.4 SIPOC → the detailed process map |
| 4496–4517 |    39.2.5 Tools bound to Measure |
| 4518–4547 |    39.2.6 Conditions — sequence locks, routing, and the gate |
| 4548–4565 |    39.2.7 State parameters — Measure's use of `PhaseState` |
| 4566–4582 |    39.2.8 Metric literacy — what each metric means |
| 4583–4596 |    39.2.9 Gate, storage, progress view |
| 4597–4605 |    39.2.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4606–4622 |    39.2.11 Cross-phase reads and writes |
| 4623–4628 |    39.2.12 The other two phases |
| 4629–4858 |   39.3 Analyse phase, complete specification |
| 4639–4648 |    39.3.1 Purpose |
| 4649–4674 |    39.3.2 The ordered field list — the `field_index` sequence |
| 4675–4711 |    39.3.3 The metric registry and Analyse's placeholder (linkage form — closes F-13) |
| 4712–4731 |    39.3.4 Two movements — generate, then validate |
| 4732–4754 |    39.3.5 Tools bound to Analyse |
| 4755–4783 |    39.3.6 Conditions — methodology guards, routing, and the gate |
| 4784–4797 |    39.3.7 State parameters — Analyse's use of `PhaseState` |
| 4798–4813 |    39.3.8 Metric literacy — what each metric and statistic means |
| 4814–4825 |    39.3.9 Gate, storage, progress view |
| 4826–4834 |    39.3.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4835–4852 |    39.3.11 Cross-phase reads and writes |
| 4853–4858 |    39.3.12 The other phase |
| 4859–5061 |   39.4 Improve phase, complete specification |
| 4869–4877 |    39.4.1 Purpose |
| 4878–4898 |    39.4.2 The ordered field list — the `field_index` sequence |
| 4899–4917 |    39.4.3 The metric registry and Improve's placeholder (linkage form) |
| 4918–4935 |    39.4.4 Two movements — generate-and-select, then pilot-and-prove |
| 4936–4954 |    39.4.5 Tools bound to Improve |
| 4955–4986 |    39.4.6 Conditions — methodology guards, DOE belt-gating, routing, gate |
| 4987–5000 |    39.4.7 State parameters — Improve's use of `PhaseState` |
| 5001–5014 |    39.4.8 Metric literacy — what each metric and statistic means |
| 5015–5026 |    39.4.9 Gate, storage, progress view |
| 5027–5036 |    39.4.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5037–5053 |    39.4.11 Cross-phase reads and writes |
| 5054–5061 |    39.4.12 The last phase |
| 5062–5299 |   39.5 Control phase, complete specification |
| 5072–5080 |    39.5.1 Purpose |
| 5081–5109 |    39.5.2 The ordered field list — the `field_index` sequence |
| 5110–5139 |    39.5.3 The metric registry, the comparison, and single authority (closes F-14) |
| 5140–5156 |    39.5.4 Two movements — confirm it held, then lock it in |
| 5157–5176 |    39.5.5 Tools bound to Control |
| 5177–5209 |    39.5.6 Conditions — guards, routing, gate |
| 5210–5223 |    39.5.7 State parameters — Control's use of `PhaseState` |
| 5224–5238 |    39.5.8 Metric literacy — what each metric and statistic means |
| 5239–5252 |    39.5.9 Gate, storage, progress view |
| 5253–5263 |    39.5.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5264–5279 |    39.5.11 Cross-phase reads and writes — the thread closes here |
| 5280–5299 |    39.5.12 The measurement thread, closed |
| 5300–5395 |  40. The five `{Phase}Output` schemas |
| 5323–5341 |   Field counts |
| 5342–5353 |   The four gate-metadata fields |
| 5354–5367 |   Three fields are on all five schemas |
| 5368–5395 |   40.1 Gate assembly |
| 5396–5479 |  41. Structured dict fields, and FMEA |
| 5418–5429 |   The grader checks every sub-field is populated |
| 5430–5438 |   `control_plan` is `dict`, never `str` |
| 5439–5447 |   `stability_assessment` is checked BEFORE capability |
| 5448–5459 |   `experiment_justification` is Tier 1 and does not require an experiment |
| 5460–5479 |   FMEA has no field in any schema, and none may be added |
| 5480–5511 |  42. Cross-phase reference fields in practice |
| 5512–5678 |  43. The coaching method |
| 5530–5557 |   43.1 The seven-step computation pattern |
| 5558–5595 |   43.2 Show before asking |
| 5596–5618 |   43.3 The A→F session flow |
| 5619–5650 |   43.4 The live gate document preview |
| 5651–5660 |   43.5 No external URLs |
| 5661–5678 |   43.6 What the coach must not do |
| 5679–6035 | Part IX — Reliability |
| 5683–5711 |   43.7 Metric literacy — the metric, and the statistic |
| 5712–5740 |  44. The failure pipeline |
| 5741–5853 |  45. Timeouts and compensating actions |
| 5748–5779 |   Per-node timeouts — required on every phase executor node |
| 5780–5789 |   Composition order — retries run BEFORE the handler |
| 5790–5799 |   Node-level error handlers — required on every node with external writes |
| 5800–5805 |   Hand-written Saga orchestrators are BANNED |
| 5806–5814 |   Two dependencies on this rule, both correctness-critical |
| 5815–5846 |   Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST** |
| 5847–5853 |   `DeltaChannel` is NOT used |
| 5854–5969 |  46. The fallback chain and circuit breakers |
| 5860–5872 |   The v2.1 four-level chain |
| 5873–5879 |   Backoff strategy is chosen per level, not globally |
| 5880–5898 |   Level 3 cache |
| 5899–5914 |   Circuit breakers — three-state, two instances |
| 5915–5921 |   Degraded mode uses actual state, never a generic error |
| 5922–5929 |   HTTP 400 is NOT a fallback case |
| 5930–5969 |   46.1 Geographic redundancy — **DEFERRED** |
| 5970–6010 |  47. Disconnect policy — what a dropped client commits |
| 5987–5993 |   Ratified policy: ABANDON, not COMPLETE |
| 5994–6010 |   Five requirements |
| 6011–6035 |  48. Structured errors |
| 6036–6523 | Part X — Operations |
| 6040–6093 |  49. API surface |
| 6046–6055 |   One runtime |
| 6056–6063 |   Async by default |
| 6064–6087 |   Endpoints |
| 6088–6093 |   Envelopes are Pydantic v2 |
| 6094–6250 |  50. UI and language rules |
| 6101–6139 |   50.1 Coach response structure |
| 6140–6151 |   Plain language always |
| 6152–6159 |   Citations |
| 6160–6173 |   Contextual feedback |
| 6174–6180 |   Connection status before the first interaction |
| 6181–6186 |   The gate review screen |
| 6187–6225 |   The live gate document |
| 6226–6237 |   The all-gate-fields tab is the contradiction backstop |
| 6238–6250 |   The conflict resolution panel |
| 6251–6326 |  51. Tracing and observability |
| 6257–6267 |   LangSmith is mandatory |
| 6268–6300 |   `@traceable` on every custom function |
| 6301–6306 |   What gets traced |
| 6307–6314 |   P50/P99 latency is a coaching quality signal |
| 6315–6326 |   Logs |
| 6327–6381 |  52. Evaluation and regression testing |
| 6333–6340 |   Built alongside the refactor, not before it |
| 6341–6347 |   The dataset is authored jointly, not generated |
| 6348–6361 |   Minimum viable suite |
| 6362–6372 |   Rubrics and the eval dataset are complementary, not duplicative |
| 6373–6381 |   Two open validation questions this suite answers |
| 6382–6523 |  53. Configuration, dependencies and deployment |
| 6388–6404 |   Fail-fast environment validation |
| 6405–6428 |   Dependency floor |
| 6429–6439 |   `/verify-current-version` is a mandatory checkpoint |
| 6440–6447 |   Infrastructure not yet provisioned |
| 6448–6459 |   Deployment layer: FastAPI, not LangGraph Server |
| 6460–6523 |   53.1 Migration sequence |
| 6524–7092 | Part XI — Governance |
| 6528–6570 |  54. Where code is allowed to live |
| 6535–6552 |   Classes are permitted ONLY in these files |
| 6553–6570 |   Target folder structure |
| 6571–6941 |  55. Anti-drift |
| 6585–6599 |   Rule numbers are load-bearing |
| 6600–6610 |   The registry guards code, not documentation |
| 6611–6616 |   Verification discipline |
| 6617–6639 |   Reference sweeps must use raw `grep -rn`, never a gitignore-filtered tool |
| 6640–6690 |   55.1 Spec-layer governance rules |
| 6691–6773 |   55.2 The BUILT markers, and the paths that oblige a re-check |
| 6774–6854 |   55.3 The phase completeness set — what one phase actually traverses |
| 6855–6904 |   55.4 Facts have one owner — the ratified minimum |
| 6905–6941 |   55.5 The commit gates govern. The rule files are advisory context. |
| 6942–7092 |  56. Amendment procedure |
| 6969–7012 |   56.0 What changed about amending, when the rules stopped being one file |
| 7013–7031 |   56.0.1 Rule, reference, and owned fact — three destinations |
| 7032–7074 |   56.1 A phase is one atomic unit — schema, validator, skill |
| 7075–7092 |   What requires an amendment rather than a routine change |
| 7093–11437 | Part XII — Specification |
| 7103–7126 |   56.2 The rule lands here; the reasoning lands in the commit |
| 7127–7160 |   56.3 The tree at HEAD is the only source of truth |
| 7161–7422 |  57. The specification layer — how to read and write a spec entry |
| 7168–7188 |   Why this Part exists |
| 7189–7204 |   The five structural rules |
| 7205–7219 |   Entry identity and traceability |
| 7220–7267 |   The entry template — three layers |
| 7268–7279 |   How gaps are marked |
| 7280–7296 |   57.1 The two calibrated samples |
| 7297–7350 |   57.2 SAMPLE 1 — CLASS TEMPLATE — S-C01 `SupervisorState` |
| 7300–7350 |    SPEC — `SupervisorState` |
| 7351–7401 |   57.3 SAMPLE 2 — FUNCTION/NODE TEMPLATE — S-F04 `phase_executor` (the coach node) |
| 7355–7401 |    SPEC — `phase_executor` (the coach node) |
| 7402–7422 |   57.4 Entry index |
| 7423–8752 |  58. Spec — graph management |
| 7433–7436 |   58.1 S-C01 · `SupervisorState` |
| 7437–7602 |   58.2 S-C02 · `PhaseState` |
| 7603–7621 |   58.3 S-C03 · Per-phase use of `PhaseState` |
| 7622–7697 |   58.4 S-C04 · `CoachingPlan` |
| 7698–7807 |   58.5 S-C05 · `CoachingResponse` |
| 7808–7859 |   58.6 S-C06 · `AzureBlobStore` |
| 7860–7905 |   58.7 S-C07 · `AzureBlobCheckpointSaver` |
| 7906–7952 |   58.8 S-C08 · `ImproveBlobClient` |
| 7953–8015 |   58.9 S-C09 · `storage/models.py` — the record models |
| 8016–8079 |   58.10 S-F01 · The supervisor graph — static edges |
| 8050–8059 |    SIPOC — at a glance |
| 8060–8079 |    Behaviors (EARS) |
| 8080–8125 |   58.11 S-F02 · `build_phase_subgraph(phase, llm)` |
| 8098–8107 |    SIPOC — at a glance |
| 8108–8125 |    Behaviors (EARS) |
| 8126–8166 |   58.12 S-F03 · `phase_planner` node |
| 8137–8146 |    SIPOC — at a glance |
| 8147–8166 |    Behaviors (EARS) |
| 8167–8178 |   58.13 S-F04 · `phase_executor` node |
| 8179–8240 |   58.14 S-F05 · `validation_stack` node |
| 8189–8198 |    SIPOC — at a glance |
| 8199–8210 |    Behaviors (EARS) |
| 8211–8240 |    ⚠ AI-ACT — high-risk surface |
| 8241–8292 |   58.15 S-F06 · `gate_review_node` |
| 8251–8260 |    SIPOC — at a glance |
| 8261–8268 |    Behaviors (EARS) |
| 8269–8292 |    ⚠ AI-ACT — high-risk surface |
| 8293–8360 |   58.16 S-F07 · `gate_apply_node` |
| 8314–8323 |    SIPOC — at a glance |
| 8324–8336 |    Behaviors (EARS) |
| 8337–8360 |    ⚠ AI-ACT — high-risk surface |
| 8361–8396 |   58.17 S-F08 · The escalation subgraph |
| 8369–8378 |    SIPOC — at a glance |
| 8379–8396 |    Behaviors (EARS) |
| 8397–8465 |   58.18 S-F09 · `analyse_executor_node` |
| 8437–8446 |    SIPOC — at a glance |
| 8447–8465 |    Behaviors (EARS) |
| 8466–8559 |   58.19 S-F10 · `define_input_mapper` |
| 8509–8521 |    SIPOC — at a glance |
| 8522–8550 |    Execution site — where a boundary mapper actually runs |
| 8551–8559 |    Behaviors (EARS) |
| 8560–8613 |   58.20 S-F11 · `define_output_mapper` |
| 8589–8598 |    SIPOC — at a glance |
| 8599–8613 |    Behaviors (EARS) |
| 8614–8663 |   58.21 S-F12 · The Measure, Analyse, Improve and Control mapper pairs |
| 8622–8631 |    SIPOC — at a glance |
| 8632–8663 |    Behaviors (EARS) |
| 8664–8752 |   58.22 S-F13 · Level 2 `Command` routing |
| 8681–8698 |    DP1 — the planner owns the field / gate decision |
| 8699–8719 |    DP2 — the validation stack's three exits |
| 8720–8740 |    DP3 — the gate exits |
| 8741–8752 |    What is settled and binds |
| 8753–9135 |  59. Spec — knowledge and retrieval |
| 8766–8795 |   59.1 S-C16 · `Hop` |
| 8796–8842 |   59.2 S-C17 · `Plan` — the hop decomposition plan |
| 8843–8879 |   59.3 S-C18 · `SynthesisOutput` |
| 8880–8896 |   59.4 S-C19 · `QueryVariants` |
| 8897–8943 |   59.5 S-F14 · `rag_lookup_methodology` |
| 8918–8927 |    SIPOC — at a glance |
| 8928–8943 |    Behaviors (EARS) |
| 8944–8991 |   59.6 S-F15 · `rag_lookup_evidence` |
| 8967–8976 |    SIPOC — at a glance |
| 8977–8991 |    Behaviors (EARS) |
| 8992–9038 |   59.7 S-F16 · `rag_lookup_case_history` |
| 9015–9024 |    SIPOC — at a glance |
| 9025–9038 |    Behaviors (EARS) |
| 9039–9089 |   59.8 S-F17 · `reciprocal_rank_fusion` |
| 9066–9075 |    SIPOC — at a glance |
| 9076–9089 |    Behaviors (EARS) |
| 9090–9135 |   59.9 S-F18 · The retriever layer — `search_knowledge`, `search_cases`, `search_evidence` |
| 9118–9135 |    SIPOC — at a glance |
| 9136–9421 |  60. Spec — tools |
| 9154–9187 |   60.1 S-F19 · `propose_template` |
| 9167–9187 |    SIPOC — at a glance |
| 9188–9226 |   60.2 S-F20 · `propose_diagram` |
| 9203–9212 |    SIPOC — at a glance |
| 9213–9226 |    Behaviors (EARS) |
| 9227–9268 |   60.3 S-F21 · `check_gate_status` |
| 9242–9251 |    SIPOC — at a glance |
| 9252–9268 |    Behaviors (EARS) |
| 9269–9304 |   60.4 S-F22 · `request_human_approval` |
| 9283–9304 |    SIPOC — at a glance |
| 9305–9321 |   60.5 S-F23 · `load_skill(name)` |
| 9322–9366 |   60.6 S-F24 · The 20 computation tools |
| 9345–9366 |    Behaviors (EARS) — binding on all twenty |
| 9367–9421 |   60.7 S-F57 · `load_evidence_series(blob_path, column)` |
| 9392–9401 |    SIPOC — at a glance |
| 9402–9421 |    Behaviors (EARS) |
| 9422–9674 |  61. Spec — the coaching agent's middleware |
| 9440–9502 |   61.1 S-C10 · `ContradictionDetectionMiddleware` |
| 9462–9471 |    Behaviors (EARS) |
| 9472–9502 |    ⚠ AI-ACT — high-risk surface |
| 9503–9544 |   61.2 S-C11 · `BeforeModelStateInjection` |
| 9516–9544 |    Behaviors (EARS) |
| 9545–9584 |   61.3 S-C12 · `DMAICSkillsMiddleware` |
| 9565–9584 |    Behaviors (EARS) |
| 9585–9621 |   61.4 S-C13 · `CoherenceMiddleware` |
| 9599–9621 |    Behaviors (EARS) |
| 9622–9657 |   61.5 S-C14 · `DMAICGraderMiddleware` |
| 9632–9657 |    Behaviors (EARS) |
| 9658–9674 |   61.6 S-C15 · `HITLInterrupt` |
| 9675–10082 |  62. Spec — validation and gates |
| 9689–9731 |   62.1 S-C20 · `CriterionVerdict` |
| 9732–9749 |   62.2 S-C21 · `GraderVerdict` |
| 9750–9763 |   62.3 S-C22 · `CoachingGraderVerdict` |
| 9764–9775 |   62.4 S-C23 · `CoherenceResult` |
| 9776–9790 |   62.5 S-C24 · `ConstraintCheckResult` / `ConstraintVerdict` |
| 9791–9803 |   62.6 S-C25 · `PolicyAdvisoryResult` |
| 9804–9840 |   62.7 S-C26 · `DMAICGateValidator` |
| 9841–9875 |   62.8 S-F25 · Layer 2c — the constraint check |
| 9850–9859 |    SIPOC — at a glance |
| 9860–9875 |    Behaviors (EARS) |
| 9876–9923 |   62.9 S-F26 · Layer 2d — the gate grader |
| 9891–9900 |    SIPOC — at a glance |
| 9901–9923 |    Behaviors (EARS) |
| 9924–9965 |   62.10 S-F27 · The policy advisory |
| 9939–9948 |    SIPOC — at a glance |
| 9949–9965 |    Behaviors (EARS) |
| 9966–10082 |   62.11 S-F28 · Gate document assembly |
| 10054–10063 |    SIPOC — at a glance |
| 10064–10082 |    Behaviors (EARS) |
| 10083–10604 |  63. Spec — the DMAIC gate documents |
| 10101–10169 |   63.1 S-C27 · `DefineOutput` |
| 10170–10210 |   63.2 S-C28 · `MeasureOutput` |
| 10211–10268 |   63.3 S-C29 · `AnalyseOutput` |
| 10269–10328 |   63.4 S-C30 · `ImproveOutput` |
| 10329–10400 |   63.5 S-C31 · `ControlOutput` |
| 10401–10467 |   63.6 S-C32 · The three cross-phase reference dicts |
| 10468–10509 |   63.7 S-C33 · The three structured dict fields |
| 10510–10548 |   63.8 S-C38 · `metric_definitions` — the project metric registry |
| 10549–10604 |   63.9 S-C39 · `phase_metrics` — the per-phase placeholder |
| 10605–10893 |  64. Spec — reliability |
| 10616–10656 |   64.1 S-C34 · `AgentImproveError` |
| 10657–10695 |   64.2 S-C35 · `CircuitBreaker` |
| 10696–10782 |   64.3 S-F29 · `phase_error_recovery` |
| 10724–10733 |    SIPOC — at a glance |
| 10734–10782 |    Behaviors (EARS) |
| 10783–10831 |   64.4 S-F30 · `degraded_mode_response` |
| 10804–10813 |    SIPOC — at a glance |
| 10814–10831 |    Behaviors (EARS) |
| 10832–10850 |   64.5 S-F31 · `synthesise_partial` |
| 10851–10875 |   64.6 S-F32 · `delete_or_flag_stale_in_case_index` |
| 10876–10893 |   64.7 S-F33 · `degraded_coaching_response` node |
| 10894–11070 |  65. Spec — API, UI and evidence |
| 10904–10924 |   65.1 S-C36 · `CitationRecord` and `CitationBundle` |
| 10925–10942 |   65.2 S-C37 · The API envelopes |
| 10943–10995 |   65.3 S-F34 · The API surface |
| 10965–10974 |    SIPOC — at a glance |
| 10975–10995 |    Behaviors (EARS) |
| 10996–11035 |   65.4 S-F35 · The upload handler |
| 11021–11035 |    Behaviors (EARS) |
| 11036–11070 |   65.5 S-F36 · The `improve_case_index` write path |
| 11071–11081 |  66. The SPEC-GAP register — MOVED |
| 11082–11175 |  67. EU AI Act compliance posture |
| 11089–11104 |   67.1 The deadlines are now fixed |
| 11105–11130 |   67.2 The classification question — open, and not answered here |
| 11131–11148 |   67.3 The eight core provider obligations |
| 11149–11159 |   67.4 One compliance finding is already recorded in this document |
| 11160–11175 |   67.5 Compliance-source discipline |
| 11176–11256 |  68. The DORA-structured compliance risk register |
| 11183–11200 |   68.1 Why DORA structure |
| 11201–11217 |   68.2 The register |
| 11218–11241 |   68.3 Pending classification — not register rows |
| 11242–11256 |   68.4 The infrastructure risk already on record |
| 11257–11437 |  69. Spec — computation tools |
| 11286–11357 |   69.1 Common conventions — stated once, binding on all twenty |
| 11358–11363 |   69.2 S-F37 · Define — 1 tool |
| 11364–11376 |   69.3 S-F38–S-F45 · Measure — 8 tools |
| 11377–11386 |   69.4 S-F46–S-F50 · Analyse — 5 tools |
| 11387–11392 |   69.5 S-F51 · Improve — 1 tool |
| 11393–11410 |   69.6 S-F52–S-F56 · Control — 5 tools |
| 11411–11437 |   69.7 The Measure control-chart boundary — a tool that is deliberately absent |
| 11438–11666 | Appendices |
| 11442–11457 |  Appendix A — Provenance index |
| 11448–11451 |   A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference |
| 11452–11457 |   A.2 `agent-improve/ARCHITECTURE.md` → this reference |
| 11458–11488 |  Appendix B — Deferred backlog |
| 11489–11554 |  Appendix C — Trusted sources |
| 11495–11514 |   Tier 1 — current, authoritative |
| 11515–11533 |   Tier 1 — compliance |
| 11534–11537 |   Tier 2 — official announcements |
| 11538–11541 |   Tier 3 — informed practitioner, cross-check before citing |
| 11542–11548 |   Downgraded — historical |
| 11549–11554 |   Excluded |
| 11555–11634 |  Appendix D — Retired names, banned patterns, and exclusions |
| 11557–11579 |   D.1 Retired names — never reintroduce |
| 11580–11623 |   D.2 Banned patterns |
| 11624–11634 |   D.3 Architecturally excluded — not deferred |
| 11635–11643 |  Appendix E — Current state |
| 11644–11666 |  Appendix F — The v2.2.16 registers |
| 11650–11655 |   F.1 Decisions Resolved (v2.2) — the former §17 |
| 11656–11666 |   F.2 Change Log — the former §18 |
| 11660–11666 |    F.2.1 Amendment procedure — the former §18.1 |
