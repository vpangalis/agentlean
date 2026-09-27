# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 11670 lines

| Lines | Heading |
|---|---|
| 27–49 |  🗺 Where state lives — a MAP, not a definition |
| 50–260 | Agentic Architecture Reference |
| 155–260 |  About this document |
| 161–218 |   Scope — three agents, one architecture |
| 219–233 |   The two-document division |
| 234–248 |   Section numbering and provenance |
| 249–260 |   Reading conventions |
| 261–552 | Part I — Orientation |
| 265–341 |  1. What Agent Improve is |
| 285–311 |   What makes it architecturally distinctive |
| 312–341 |   The runtime stack |
| 342–393 |  2. How to read this document |
| 348–364 |   By what you are trying to do |
| 365–393 |   Canonical ownership |
| 394–492 |  3. Terminology |
| 405–421 |   Structural primitives |
| 422–433 |   Role labels |
| 434–451 |   The recursion is two levels, not infinite |
| 452–466 |   "Harness" — two senses, do not conflate |
| 467–477 |   "Agent" — used carefully |
| 478–492 |   Things that are deliberately not levels |
| 493–552 |  4. Architecture at a glance |
| 536–552 |   The five things that shape everything else |
| 553–1280 | Part II — State and Persistence |
| 560–618 |  5. `SupervisorState` — orchestration only |
| 572–578 |   `gate_passed` is a dict, not a list |
| 579–590 |   `current_phase` and `phase_index` are derived, and kept anyway |
| 591–610 |   Four fields were removed as redundant, and may not return |
| 611–618 |   Artifacts are not here |
| 619–854 |  6. `PhaseState` — per-phase subgraph state |
| 634–665 |   `asks` — §56 AMENDMENT, ratified 2026-09-09 |
| 666–735 |   `field_log` — §56 AMENDMENT, ratified 2026-09-21 |
| 736–741 |   `draft`, `belt_edits` and `final` are `dict`, never `str` |
| 742–764 |   `coaching_plan` is one typed plan, not a queue |
| 765–780 |   `gate_attempts` — the field whose absence recreated a production bug |
| 781–801 |   `validator_feedback` and `belt_edits` are different, and must stay separate |
| 802–819 |   `citations` and `uploads` — the evidence trail |
| 820–837 |   `hop_results` and `synthesis_output` must be state, not node locals |
| 838–846 |   Per-phase variants |
| 847–854 |   Naming discipline |
| 855–931 |  7. Field typing law — every captured field is a string |
| 871–883 |   Why strings |
| 884–903 |   The one exception — three cross-phase reference dicts |
| 904–931 |   Computation results |
| 932–1024 |  8. The checkpointer / store split |
| 956–975 |   Phased backend |
| 976–987 |   Concurrency and atomicity |
| 988–1003 |   Why Blob, and not Cosmos / Tables / SQLite |
| 1004–1024 |   On-blob checkpoint format |
| 1025–1161 |  9. The Store — cross-phase artifacts and boundary mappers |
| 1066–1089 |   Namespace convention |
| 1090–1119 |   Why cross-phase data cannot travel on parent state |
| 1120–1140 |   Boundary mappers |
| 1141–1153 |   Two prohibitions that follow |
| 1154–1161 |   Ordering constraint |
| 1162–1219 |  10. Azure Blob — two distinct concerns |
| 1181–1206 |   Complete physical layout |
| 1207–1219 |   The case blob is not updated per turn |
| 1220–1280 |  11. `step_log` — the audit trail |
| 1241–1250 |   `artifacts` and `step_log` are separate fields and stay separate |
| 1251–1280 |   Entries carry deterministic keys, never a raw timestamp as identity |
| 1281–1651 | Part III — The Graph |
| 1287–1327 |  12. Topology |
| 1317–1327 |   The subgraph builder takes the phase as a parameter |
| 1328–1467 |  13. The phase subgraph — five nodes |
| 1405–1435 |   The subgraph is a cycle, not a pipeline |
| 1436–1448 |   Two node names are BANNED |
| 1449–1454 |   Leaf tools are NOT subgraph nodes |
| 1455–1467 |   The validation stack and the policy advisory are NOT tools |
| 1468–1503 |  14. Node contract |
| 1491–1503 |   Reflection is a node, not a private function |
| 1504–1568 |  15. Routing — static edges and `Command` |
| 1510–1527 |   The decision test |
| 1528–1533 |   Never mix static edges and `Command` from the same node |
| 1534–1561 |   Level 1 does not route — it advances |
| 1562–1568 |   No subgraph imports another subgraph's nodes |
| 1569–1651 |  16. `thread_id`, `checkpoint_ns`, and where persistence attaches |
| 1575–1590 |   One `thread_id` per project |
| 1591–1604 |   The checkpointer and store go on the parent graph ONLY |
| 1605–1631 |   The wrapper node must invoke the subgraph directly (G-44) |
| 1632–1651 |   `recursion_limit` is a backstop, not the hop cap |
| 1652–2393 | Part IV — The Coaching Agent |
| 1658–1772 |  17. The Planner / Executor contract |
| 1734–1764 |   `CoachingPlan` |
| 1765–1772 |   Extraction is structured output, not a node and not a tool |
| 1773–1820 |  18. Building the executor — `create_agent` |
| 1785–1792 |   Binding tools directly onto a bare model is a violation |
| 1793–1798 |   `create_react_agent` is superseded |
| 1799–1811 |   deepagents is not a dependency |
| 1812–1820 |   The structured response and the coaching text coexist |
| 1821–2142 |  19. The middleware stack — eight, in order |
| 1843–1889 |   Ordering rules that bind |
| 1890–1901 |   Three independent retry caps |
| 1902–1945 |   19.1 `BeforeModelStateInjection` — injection timing |
| 1946–1961 |   19.2 `DMAICSkillsMiddleware` — progressive disclosure |
| 1962–2001 |   19.3 `SummarizationMiddleware` — context compression |
| 2002–2028 |   19.4 `ModelRetryMiddleware` — API-level retry |
| 2029–2041 |   19.5 `ToolRetryMiddleware` — tool-level retry |
| 2042–2064 |   19.6 `ContradictionDetectionMiddleware` — the mid-phase check |
| 2065–2099 |   19.7 `CoherenceMiddleware` — validation Layer 2a |
| 2100–2130 |   19.8 `DMAICGraderMiddleware` — coaching process quality |
| 2131–2142 |   19.9 Middleware deliberately NOT used |
| 2143–2217 |  20. `CoachingResponse` — the per-turn schema |
| 2197–2200 |   The executor node writes the response into state |
| 2201–2207 |   The executor's `response_format` is `CoachingResponse`, never a phase Output |
| 2208–2217 |   What structured output does NOT give you |
| 2218–2329 |  21. LLM roles, temperature, and the factory |
| 2238–2246 |   Factory only |
| 2247–2267 |   Roles |
| 2268–2284 |   Temperature |
| 2285–2329 |   Structured output — scoped by call type |
| 2330–2393 |  22. Prompts |
| 2356–2376 |   The memory hierarchy paragraph is mandatory |
| 2377–2393 |   Anti-hallucination guards are mandatory |
| 2394–3172 | Part V — Knowledge and Retrieval |
| 2398–2753 |  23. The three indexes |
| 2410–2460 |   23.1 `improve_knowledge_index` — methodology |
| 2461–2586 |   23.2 `improve_evidence_index` — Belt-uploaded evidence |
| 2506–2530 |    Supersession deletes; it does not flag |
| 2531–2586 |    Two Azure behaviours govern the migration |
| 2587–2659 |   23.2.1 The `role` vocabulary — ratified, not invented per phase |
| 2626–2659 |    `unclassified (pre-ask-binding)` is a MIGRATION SENTINEL, not a thirteenth role |
| 2660–2708 |   23.3 `improve_case_index` — case records (cross-case memory) |
| 2709–2719 |   The internal phase key is `analyse`, never `analyse_phase` |
| 2720–2744 |   23.4 The write-path trap that made `phase_relevance` unfilterable |
| 2745–2753 |   23.5 Schema change procedure |
| 2754–2882 |  24. The three `rag_lookup_*` tools |
| 2772–2829 |   `rag_lookup_evidence` returns a structured record, not rendered text |
| 2830–2842 |   RAG via tool, never via prepended system message |
| 2843–2867 |   The retrieval mechanism |
| 2868–2875 |   `belt_level` filtering is OFF by default |
| 2876–2882 |   `source_file` and `page_number` are returned, never filtered |
| 2883–2948 |  25. Multi-query and Reciprocal Rank Fusion |
| 2892–2908 |   Why it is mandatory |
| 2909–2915 |   The implementation |
| 2916–2937 |   `MultiQueryRetriever` and `EnsembleRetriever` are BANNED |
| 2938–2948 |   Encapsulation |
| 2949–3082 |  26. Multi-hop retrieval |
| 2964–3000 |   The hop cap is `RemainingSteps` |
| 3001–3019 |   Per-phase policy |
| 3020–3064 |   Planned multi-hop — the Analyse pipeline |
| 3065–3082 |   **UNVERIFIED** — planned multi-hop is Analyse-only |
| 3083–3129 |  27. Retrieval failure semantics |
| 3094–3102 |   Never wrap a retrieval call in a bare `except Exception` returning `[]` |
| 3103–3112 |   Three rules that each have already bitten |
| 3113–3129 |   The coach-facing message must not read as absence |
| 3130–3172 |  28. Memory taxonomy |
| 3148–3172 |   The static/dynamic split is the part that matters |
| 3173–3519 | Part VI — Tools |
| 3177–3334 |  29. The data channel and the universal eight |
| 3183–3218 |   29.1 There is no MCP — the data-channel decision |
| 3219–3261 |   29.2 The universal eight |
| 3227–3261 |    `load_evidence_series` joins the set — RATIFIED 2026-09-09 |
| 3262–3271 |   29.3 `record_field` is RETIRED and may not be reintroduced |
| 3272–3334 |   29.4 Cross-agent tools — a third category, present but NOT BOUND |
| 3335–3409 |  30. Computation tools and per-phase binding |
| 3340–3377 |   Tool sets are per phase, not universal |
| 3378–3383 |   Each of the 20 is a separate named tool |
| 3384–3392 |   All 20 are pure functions |
| 3393–3402 |   `imr_chart_limits` — the choice that is usually wrong by default |
| 3403–3409 |   Tool decisions are the model's, not the graph's |
| 3410–3442 |  31. Tool arg schemas and docstrings |
| 3416–3421 |   Every `@tool` uses `args_schema=` |
| 3422–3442 |   Docstrings are interface, not commentary |
| 3443–3519 |  32. Phase skills — SKILL.md |
| 3466–3470 |   Each skill's `allowed-tools` MUST match that phase's subset in §30 |
| 3471–3480 |   Progressive disclosure — three levels |
| 3481–3486 |   Storage backend: `FilesystemBackend` |
| 3487–3508 |   Each SKILL.md must carry |
| 3509–3519 |   Two distinct kinds of skill exist in this repository |
| 3520–4100 | Part VII — Validation and Gates |
| 3527–3647 |  33. The nine-step HITL gate |
| 3548–3561 |   Two quality checks, two actors, two moments |
| 3562–3573 |   Gates are one-way doors, with exactly one defined exception |
| 3574–3578 |   Implementation: graph-level `interrupt()` |
| 3579–3609 |   33.1 The two-node split |
| 3610–3639 |   33.2 `gate_apply_node` writes the gate document TWICE |
| 3640–3647 |   33.3 The checkpoint commits only after Belt approval |
| 3648–3751 |  34. The four-layer validation stack |
| 3663–3670 |   Layer 2a is middleware; layers 2b–2d are the node |
| 3671–3677 |   Layer 2d is NOT `DMAICGraderMiddleware` |
| 3678–3683 |   Run cheapest first |
| 3684–3693 |   The counter and the feedback |
| 3694–3703 |   Layer 2b is the only deterministic layer, deliberately |
| 3704–3715 |   Per-phase constraint sets |
| 3716–3725 |   34.1 Where each check fires |
| 3726–3751 |   34.2 The self-healing hierarchy and the transparency principle |
| 3752–3887 |  35. Two tiers of field, and the `warning` verdict |
| 3758–3772 |   The problem this solves |
| 3773–3789 |   Three distinct things check these fields, and conflating them is a design error |
| 3790–3838 |   Gate-required fields by phase |
| 3839–3855 |   The grader's verdict has three statuses |
| 3856–3863 |   Why two tiers |
| 3864–3887 |   The grader is belt-level aware |
| 3888–3981 |  36. Two graders — and why they are not redundant |
| 3907–3920 |   Why both exist |
| 3921–3944 |   `COACHING_QUALITY_RUBRIC` |
| 3945–3954 |   Mechanism, both graders |
| 3955–3964 |   Three criteria are verified deterministically, not by judgment |
| 3965–3981 |   The ratified rubric coverage |
| 3982–4078 |  37. Mid-phase contradiction and the re-approval cascade |
| 3988–4009 |   The check runs every turn, not only at gates |
| 4010–4043 |   §37 governs a GATE-COMMITTED value only |
| 4044–4057 |   There is NO tolerance threshold, and none may be added |
| 4058–4065 |   The re-approval cascade |
| 4066–4078 |   The cascade has a hard dependency on compensating actions |
| 4079–4100 |  38. Escalation |
| 4101–5681 | Part VIII — The DMAIC Domain |
| 4108–5302 |  39. The five phases |
| 4126–4140 |   The measurement thread that runs across three phases |
| 4141–4375 |   39.1 Define phase, complete specification |
| 4148–4155 |    39.1.1 Purpose |
| 4156–4218 |    39.1.2 The ordered field list — the `field_index` sequence (closes G-38) |
| 4219–4233 |    39.1.3 The composed-problem-statement rule (binding) |
| 4234–4248 |    39.1.4 The `team` structure |
| 4249–4258 |    39.1.5 SIPOC handling |
| 4259–4270 |    39.1.6 Gate, storage, progress view |
| 4271–4289 |    39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4290–4296 |    39.1.8 The other four phases |
| 4297–4329 |    39.1.9 The metric registry and Define's placeholder |
| 4330–4337 |    39.1.10 Tools bound to Define |
| 4338–4345 |    39.1.11 Conditions — routing and the gate |
| 4346–4353 |    39.1.12 State parameters — Define's use of `PhaseState` |
| 4354–4361 |    39.1.13 Metric literacy — what each metric means |
| 4362–4375 |    39.1.14 Cross-phase reads and writes |
| 4376–4631 |   39.2 Measure phase, complete specification |
| 4386–4394 |    39.2.1 Purpose |
| 4395–4417 |    39.2.2 The ordered field list — the `field_index` sequence |
| 4418–4478 |    39.2.3 The metric registry and Measure's placeholder |
| 4479–4498 |    39.2.4 SIPOC → the detailed process map |
| 4499–4520 |    39.2.5 Tools bound to Measure |
| 4521–4550 |    39.2.6 Conditions — sequence locks, routing, and the gate |
| 4551–4568 |    39.2.7 State parameters — Measure's use of `PhaseState` |
| 4569–4585 |    39.2.8 Metric literacy — what each metric means |
| 4586–4599 |    39.2.9 Gate, storage, progress view |
| 4600–4608 |    39.2.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4609–4625 |    39.2.11 Cross-phase reads and writes |
| 4626–4631 |    39.2.12 The other two phases |
| 4632–4861 |   39.3 Analyse phase, complete specification |
| 4642–4651 |    39.3.1 Purpose |
| 4652–4677 |    39.3.2 The ordered field list — the `field_index` sequence |
| 4678–4714 |    39.3.3 The metric registry and Analyse's placeholder (linkage form — closes F-13) |
| 4715–4734 |    39.3.4 Two movements — generate, then validate |
| 4735–4757 |    39.3.5 Tools bound to Analyse |
| 4758–4786 |    39.3.6 Conditions — methodology guards, routing, and the gate |
| 4787–4800 |    39.3.7 State parameters — Analyse's use of `PhaseState` |
| 4801–4816 |    39.3.8 Metric literacy — what each metric and statistic means |
| 4817–4828 |    39.3.9 Gate, storage, progress view |
| 4829–4837 |    39.3.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4838–4855 |    39.3.11 Cross-phase reads and writes |
| 4856–4861 |    39.3.12 The other phase |
| 4862–5064 |   39.4 Improve phase, complete specification |
| 4872–4880 |    39.4.1 Purpose |
| 4881–4901 |    39.4.2 The ordered field list — the `field_index` sequence |
| 4902–4920 |    39.4.3 The metric registry and Improve's placeholder (linkage form) |
| 4921–4938 |    39.4.4 Two movements — generate-and-select, then pilot-and-prove |
| 4939–4957 |    39.4.5 Tools bound to Improve |
| 4958–4989 |    39.4.6 Conditions — methodology guards, DOE belt-gating, routing, gate |
| 4990–5003 |    39.4.7 State parameters — Improve's use of `PhaseState` |
| 5004–5017 |    39.4.8 Metric literacy — what each metric and statistic means |
| 5018–5029 |    39.4.9 Gate, storage, progress view |
| 5030–5039 |    39.4.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5040–5056 |    39.4.11 Cross-phase reads and writes |
| 5057–5064 |    39.4.12 The last phase |
| 5065–5302 |   39.5 Control phase, complete specification |
| 5075–5083 |    39.5.1 Purpose |
| 5084–5112 |    39.5.2 The ordered field list — the `field_index` sequence |
| 5113–5142 |    39.5.3 The metric registry, the comparison, and single authority (closes F-14) |
| 5143–5159 |    39.5.4 Two movements — confirm it held, then lock it in |
| 5160–5179 |    39.5.5 Tools bound to Control |
| 5180–5212 |    39.5.6 Conditions — guards, routing, gate |
| 5213–5226 |    39.5.7 State parameters — Control's use of `PhaseState` |
| 5227–5241 |    39.5.8 Metric literacy — what each metric and statistic means |
| 5242–5255 |    39.5.9 Gate, storage, progress view |
| 5256–5266 |    39.5.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5267–5282 |    39.5.11 Cross-phase reads and writes — the thread closes here |
| 5283–5302 |    39.5.12 The measurement thread, closed |
| 5303–5398 |  40. The five `{Phase}Output` schemas |
| 5326–5344 |   Field counts |
| 5345–5356 |   The four gate-metadata fields |
| 5357–5370 |   Three fields are on all five schemas |
| 5371–5398 |   40.1 Gate assembly |
| 5399–5482 |  41. Structured dict fields, and FMEA |
| 5421–5432 |   The grader checks every sub-field is populated |
| 5433–5441 |   `control_plan` is `dict`, never `str` |
| 5442–5450 |   `stability_assessment` is checked BEFORE capability |
| 5451–5462 |   `experiment_justification` is Tier 1 and does not require an experiment |
| 5463–5482 |   FMEA has no field in any schema, and none may be added |
| 5483–5514 |  42. Cross-phase reference fields in practice |
| 5515–5681 |  43. The coaching method |
| 5533–5560 |   43.1 The seven-step computation pattern |
| 5561–5598 |   43.2 Show before asking |
| 5599–5621 |   43.3 The A→F session flow |
| 5622–5653 |   43.4 The live gate document preview |
| 5654–5663 |   43.5 No external URLs |
| 5664–5681 |   43.6 What the coach must not do |
| 5682–6038 | Part IX — Reliability |
| 5686–5714 |   43.7 Metric literacy — the metric, and the statistic |
| 5715–5743 |  44. The failure pipeline |
| 5744–5856 |  45. Timeouts and compensating actions |
| 5751–5782 |   Per-node timeouts — required on every phase executor node |
| 5783–5792 |   Composition order — retries run BEFORE the handler |
| 5793–5802 |   Node-level error handlers — required on every node with external writes |
| 5803–5808 |   Hand-written Saga orchestrators are BANNED |
| 5809–5817 |   Two dependencies on this rule, both correctness-critical |
| 5818–5849 |   Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST** |
| 5850–5856 |   `DeltaChannel` is NOT used |
| 5857–5972 |  46. The fallback chain and circuit breakers |
| 5863–5875 |   The v2.1 four-level chain |
| 5876–5882 |   Backoff strategy is chosen per level, not globally |
| 5883–5901 |   Level 3 cache |
| 5902–5917 |   Circuit breakers — three-state, two instances |
| 5918–5924 |   Degraded mode uses actual state, never a generic error |
| 5925–5932 |   HTTP 400 is NOT a fallback case |
| 5933–5972 |   46.1 Geographic redundancy — **DEFERRED** |
| 5973–6013 |  47. Disconnect policy — what a dropped client commits |
| 5990–5996 |   Ratified policy: ABANDON, not COMPLETE |
| 5997–6013 |   Five requirements |
| 6014–6038 |  48. Structured errors |
| 6039–6526 | Part X — Operations |
| 6043–6096 |  49. API surface |
| 6049–6058 |   One runtime |
| 6059–6066 |   Async by default |
| 6067–6090 |   Endpoints |
| 6091–6096 |   Envelopes are Pydantic v2 |
| 6097–6253 |  50. UI and language rules |
| 6104–6142 |   50.1 Coach response structure |
| 6143–6154 |   Plain language always |
| 6155–6162 |   Citations |
| 6163–6176 |   Contextual feedback |
| 6177–6183 |   Connection status before the first interaction |
| 6184–6189 |   The gate review screen |
| 6190–6228 |   The live gate document |
| 6229–6240 |   The all-gate-fields tab is the contradiction backstop |
| 6241–6253 |   The conflict resolution panel |
| 6254–6329 |  51. Tracing and observability |
| 6260–6270 |   LangSmith is mandatory |
| 6271–6303 |   `@traceable` on every custom function |
| 6304–6309 |   What gets traced |
| 6310–6317 |   P50/P99 latency is a coaching quality signal |
| 6318–6329 |   Logs |
| 6330–6384 |  52. Evaluation and regression testing |
| 6336–6343 |   Built alongside the refactor, not before it |
| 6344–6350 |   The dataset is authored jointly, not generated |
| 6351–6364 |   Minimum viable suite |
| 6365–6375 |   Rubrics and the eval dataset are complementary, not duplicative |
| 6376–6384 |   Two open validation questions this suite answers |
| 6385–6526 |  53. Configuration, dependencies and deployment |
| 6391–6407 |   Fail-fast environment validation |
| 6408–6431 |   Dependency floor |
| 6432–6442 |   `/verify-current-version` is a mandatory checkpoint |
| 6443–6450 |   Infrastructure not yet provisioned |
| 6451–6462 |   Deployment layer: FastAPI, not LangGraph Server |
| 6463–6526 |   53.1 Migration sequence |
| 6527–7095 | Part XI — Governance |
| 6531–6573 |  54. Where code is allowed to live |
| 6538–6555 |   Classes are permitted ONLY in these files |
| 6556–6573 |   Target folder structure |
| 6574–6944 |  55. Anti-drift |
| 6588–6602 |   Rule numbers are load-bearing |
| 6603–6613 |   The registry guards code, not documentation |
| 6614–6619 |   Verification discipline |
| 6620–6642 |   Reference sweeps must use raw `grep -rn`, never a gitignore-filtered tool |
| 6643–6693 |   55.1 Spec-layer governance rules |
| 6694–6776 |   55.2 The BUILT markers, and the paths that oblige a re-check |
| 6777–6857 |   55.3 The phase completeness set — what one phase actually traverses |
| 6858–6907 |   55.4 Facts have one owner — the ratified minimum |
| 6908–6944 |   55.5 The commit gates govern. The rule files are advisory context. |
| 6945–7095 |  56. Amendment procedure |
| 6972–7015 |   56.0 What changed about amending, when the rules stopped being one file |
| 7016–7034 |   56.0.1 Rule, reference, and owned fact — three destinations |
| 7035–7077 |   56.1 A phase is one atomic unit — schema, validator, skill |
| 7078–7095 |   What requires an amendment rather than a routine change |
| 7096–11440 | Part XII — Specification |
| 7106–7129 |   56.2 The rule lands here; the reasoning lands in the commit |
| 7130–7163 |   56.3 The tree at HEAD is the only source of truth |
| 7164–7425 |  57. The specification layer — how to read and write a spec entry |
| 7171–7191 |   Why this Part exists |
| 7192–7207 |   The five structural rules |
| 7208–7222 |   Entry identity and traceability |
| 7223–7270 |   The entry template — three layers |
| 7271–7282 |   How gaps are marked |
| 7283–7299 |   57.1 The two calibrated samples |
| 7300–7353 |   57.2 SAMPLE 1 — CLASS TEMPLATE — S-C01 `SupervisorState` |
| 7303–7353 |    SPEC — `SupervisorState` |
| 7354–7404 |   57.3 SAMPLE 2 — FUNCTION/NODE TEMPLATE — S-F04 `phase_executor` (the coach node) |
| 7358–7404 |    SPEC — `phase_executor` (the coach node) |
| 7405–7425 |   57.4 Entry index |
| 7426–8755 |  58. Spec — graph management |
| 7436–7439 |   58.1 S-C01 · `SupervisorState` |
| 7440–7605 |   58.2 S-C02 · `PhaseState` |
| 7606–7624 |   58.3 S-C03 · Per-phase use of `PhaseState` |
| 7625–7700 |   58.4 S-C04 · `CoachingPlan` |
| 7701–7810 |   58.5 S-C05 · `CoachingResponse` |
| 7811–7862 |   58.6 S-C06 · `AzureBlobStore` |
| 7863–7908 |   58.7 S-C07 · `AzureBlobCheckpointSaver` |
| 7909–7955 |   58.8 S-C08 · `ImproveBlobClient` |
| 7956–8018 |   58.9 S-C09 · `storage/models.py` — the record models |
| 8019–8082 |   58.10 S-F01 · The supervisor graph — static edges |
| 8053–8062 |    SIPOC — at a glance |
| 8063–8082 |    Behaviors (EARS) |
| 8083–8128 |   58.11 S-F02 · `build_phase_subgraph(phase, llm)` |
| 8101–8110 |    SIPOC — at a glance |
| 8111–8128 |    Behaviors (EARS) |
| 8129–8169 |   58.12 S-F03 · `phase_planner` node |
| 8140–8149 |    SIPOC — at a glance |
| 8150–8169 |    Behaviors (EARS) |
| 8170–8181 |   58.13 S-F04 · `phase_executor` node |
| 8182–8243 |   58.14 S-F05 · `validation_stack` node |
| 8192–8201 |    SIPOC — at a glance |
| 8202–8213 |    Behaviors (EARS) |
| 8214–8243 |    ⚠ AI-ACT — high-risk surface |
| 8244–8295 |   58.15 S-F06 · `gate_review_node` |
| 8254–8263 |    SIPOC — at a glance |
| 8264–8271 |    Behaviors (EARS) |
| 8272–8295 |    ⚠ AI-ACT — high-risk surface |
| 8296–8363 |   58.16 S-F07 · `gate_apply_node` |
| 8317–8326 |    SIPOC — at a glance |
| 8327–8339 |    Behaviors (EARS) |
| 8340–8363 |    ⚠ AI-ACT — high-risk surface |
| 8364–8399 |   58.17 S-F08 · The escalation subgraph |
| 8372–8381 |    SIPOC — at a glance |
| 8382–8399 |    Behaviors (EARS) |
| 8400–8468 |   58.18 S-F09 · `analyse_executor_node` |
| 8440–8449 |    SIPOC — at a glance |
| 8450–8468 |    Behaviors (EARS) |
| 8469–8562 |   58.19 S-F10 · `define_input_mapper` |
| 8512–8524 |    SIPOC — at a glance |
| 8525–8553 |    Execution site — where a boundary mapper actually runs |
| 8554–8562 |    Behaviors (EARS) |
| 8563–8616 |   58.20 S-F11 · `define_output_mapper` |
| 8592–8601 |    SIPOC — at a glance |
| 8602–8616 |    Behaviors (EARS) |
| 8617–8666 |   58.21 S-F12 · The Measure, Analyse, Improve and Control mapper pairs |
| 8625–8634 |    SIPOC — at a glance |
| 8635–8666 |    Behaviors (EARS) |
| 8667–8755 |   58.22 S-F13 · Level 2 `Command` routing |
| 8684–8701 |    DP1 — the planner owns the field / gate decision |
| 8702–8722 |    DP2 — the validation stack's three exits |
| 8723–8743 |    DP3 — the gate exits |
| 8744–8755 |    What is settled and binds |
| 8756–9138 |  59. Spec — knowledge and retrieval |
| 8769–8798 |   59.1 S-C16 · `Hop` |
| 8799–8845 |   59.2 S-C17 · `Plan` — the hop decomposition plan |
| 8846–8882 |   59.3 S-C18 · `SynthesisOutput` |
| 8883–8899 |   59.4 S-C19 · `QueryVariants` |
| 8900–8946 |   59.5 S-F14 · `rag_lookup_methodology` |
| 8921–8930 |    SIPOC — at a glance |
| 8931–8946 |    Behaviors (EARS) |
| 8947–8994 |   59.6 S-F15 · `rag_lookup_evidence` |
| 8970–8979 |    SIPOC — at a glance |
| 8980–8994 |    Behaviors (EARS) |
| 8995–9041 |   59.7 S-F16 · `rag_lookup_case_history` |
| 9018–9027 |    SIPOC — at a glance |
| 9028–9041 |    Behaviors (EARS) |
| 9042–9092 |   59.8 S-F17 · `reciprocal_rank_fusion` |
| 9069–9078 |    SIPOC — at a glance |
| 9079–9092 |    Behaviors (EARS) |
| 9093–9138 |   59.9 S-F18 · The retriever layer — `search_knowledge`, `search_cases`, `search_evidence` |
| 9121–9138 |    SIPOC — at a glance |
| 9139–9424 |  60. Spec — tools |
| 9157–9190 |   60.1 S-F19 · `propose_template` |
| 9170–9190 |    SIPOC — at a glance |
| 9191–9229 |   60.2 S-F20 · `propose_diagram` |
| 9206–9215 |    SIPOC — at a glance |
| 9216–9229 |    Behaviors (EARS) |
| 9230–9271 |   60.3 S-F21 · `check_gate_status` |
| 9245–9254 |    SIPOC — at a glance |
| 9255–9271 |    Behaviors (EARS) |
| 9272–9307 |   60.4 S-F22 · `request_human_approval` |
| 9286–9307 |    SIPOC — at a glance |
| 9308–9324 |   60.5 S-F23 · `load_skill(name)` |
| 9325–9369 |   60.6 S-F24 · The 20 computation tools |
| 9348–9369 |    Behaviors (EARS) — binding on all twenty |
| 9370–9424 |   60.7 S-F57 · `load_evidence_series(blob_path, column)` |
| 9395–9404 |    SIPOC — at a glance |
| 9405–9424 |    Behaviors (EARS) |
| 9425–9677 |  61. Spec — the coaching agent's middleware |
| 9443–9505 |   61.1 S-C10 · `ContradictionDetectionMiddleware` |
| 9465–9474 |    Behaviors (EARS) |
| 9475–9505 |    ⚠ AI-ACT — high-risk surface |
| 9506–9547 |   61.2 S-C11 · `BeforeModelStateInjection` |
| 9519–9547 |    Behaviors (EARS) |
| 9548–9587 |   61.3 S-C12 · `DMAICSkillsMiddleware` |
| 9568–9587 |    Behaviors (EARS) |
| 9588–9624 |   61.4 S-C13 · `CoherenceMiddleware` |
| 9602–9624 |    Behaviors (EARS) |
| 9625–9660 |   61.5 S-C14 · `DMAICGraderMiddleware` |
| 9635–9660 |    Behaviors (EARS) |
| 9661–9677 |   61.6 S-C15 · `HITLInterrupt` |
| 9678–10085 |  62. Spec — validation and gates |
| 9692–9734 |   62.1 S-C20 · `CriterionVerdict` |
| 9735–9752 |   62.2 S-C21 · `GraderVerdict` |
| 9753–9766 |   62.3 S-C22 · `CoachingGraderVerdict` |
| 9767–9778 |   62.4 S-C23 · `CoherenceResult` |
| 9779–9793 |   62.5 S-C24 · `ConstraintCheckResult` / `ConstraintVerdict` |
| 9794–9806 |   62.6 S-C25 · `PolicyAdvisoryResult` |
| 9807–9843 |   62.7 S-C26 · `DMAICGateValidator` |
| 9844–9878 |   62.8 S-F25 · Layer 2c — the constraint check |
| 9853–9862 |    SIPOC — at a glance |
| 9863–9878 |    Behaviors (EARS) |
| 9879–9926 |   62.9 S-F26 · Layer 2d — the gate grader |
| 9894–9903 |    SIPOC — at a glance |
| 9904–9926 |    Behaviors (EARS) |
| 9927–9968 |   62.10 S-F27 · The policy advisory |
| 9942–9951 |    SIPOC — at a glance |
| 9952–9968 |    Behaviors (EARS) |
| 9969–10085 |   62.11 S-F28 · Gate document assembly |
| 10057–10066 |    SIPOC — at a glance |
| 10067–10085 |    Behaviors (EARS) |
| 10086–10607 |  63. Spec — the DMAIC gate documents |
| 10104–10172 |   63.1 S-C27 · `DefineOutput` |
| 10173–10213 |   63.2 S-C28 · `MeasureOutput` |
| 10214–10271 |   63.3 S-C29 · `AnalyseOutput` |
| 10272–10331 |   63.4 S-C30 · `ImproveOutput` |
| 10332–10403 |   63.5 S-C31 · `ControlOutput` |
| 10404–10470 |   63.6 S-C32 · The three cross-phase reference dicts |
| 10471–10512 |   63.7 S-C33 · The three structured dict fields |
| 10513–10551 |   63.8 S-C38 · `metric_definitions` — the project metric registry |
| 10552–10607 |   63.9 S-C39 · `phase_metrics` — the per-phase placeholder |
| 10608–10896 |  64. Spec — reliability |
| 10619–10659 |   64.1 S-C34 · `AgentImproveError` |
| 10660–10698 |   64.2 S-C35 · `CircuitBreaker` |
| 10699–10785 |   64.3 S-F29 · `phase_error_recovery` |
| 10727–10736 |    SIPOC — at a glance |
| 10737–10785 |    Behaviors (EARS) |
| 10786–10834 |   64.4 S-F30 · `degraded_mode_response` |
| 10807–10816 |    SIPOC — at a glance |
| 10817–10834 |    Behaviors (EARS) |
| 10835–10853 |   64.5 S-F31 · `synthesise_partial` |
| 10854–10878 |   64.6 S-F32 · `delete_or_flag_stale_in_case_index` |
| 10879–10896 |   64.7 S-F33 · `degraded_coaching_response` node |
| 10897–11073 |  65. Spec — API, UI and evidence |
| 10907–10927 |   65.1 S-C36 · `CitationRecord` and `CitationBundle` |
| 10928–10945 |   65.2 S-C37 · The API envelopes |
| 10946–10998 |   65.3 S-F34 · The API surface |
| 10968–10977 |    SIPOC — at a glance |
| 10978–10998 |    Behaviors (EARS) |
| 10999–11038 |   65.4 S-F35 · The upload handler |
| 11024–11038 |    Behaviors (EARS) |
| 11039–11073 |   65.5 S-F36 · The `improve_case_index` write path |
| 11074–11084 |  66. The SPEC-GAP register — MOVED |
| 11085–11178 |  67. EU AI Act compliance posture |
| 11092–11107 |   67.1 The deadlines are now fixed |
| 11108–11133 |   67.2 The classification question — open, and not answered here |
| 11134–11151 |   67.3 The eight core provider obligations |
| 11152–11162 |   67.4 One compliance finding is already recorded in this document |
| 11163–11178 |   67.5 Compliance-source discipline |
| 11179–11259 |  68. The DORA-structured compliance risk register |
| 11186–11203 |   68.1 Why DORA structure |
| 11204–11220 |   68.2 The register |
| 11221–11244 |   68.3 Pending classification — not register rows |
| 11245–11259 |   68.4 The infrastructure risk already on record |
| 11260–11440 |  69. Spec — computation tools |
| 11289–11360 |   69.1 Common conventions — stated once, binding on all twenty |
| 11361–11366 |   69.2 S-F37 · Define — 1 tool |
| 11367–11379 |   69.3 S-F38–S-F45 · Measure — 8 tools |
| 11380–11389 |   69.4 S-F46–S-F50 · Analyse — 5 tools |
| 11390–11395 |   69.5 S-F51 · Improve — 1 tool |
| 11396–11413 |   69.6 S-F52–S-F56 · Control — 5 tools |
| 11414–11440 |   69.7 The Measure control-chart boundary — a tool that is deliberately absent |
| 11441–11670 | Appendices |
| 11445–11460 |  Appendix A — Provenance index |
| 11451–11454 |   A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference |
| 11455–11460 |   A.2 `agent-improve/ARCHITECTURE.md` → this reference |
| 11461–11491 |  Appendix B — Deferred backlog |
| 11492–11557 |  Appendix C — Trusted sources |
| 11498–11517 |   Tier 1 — current, authoritative |
| 11518–11536 |   Tier 1 — compliance |
| 11537–11540 |   Tier 2 — official announcements |
| 11541–11544 |   Tier 3 — informed practitioner, cross-check before citing |
| 11545–11551 |   Downgraded — historical |
| 11552–11557 |   Excluded |
| 11558–11638 |  Appendix D — Retired names, banned patterns, and exclusions |
| 11560–11583 |   D.1 Retired names — never reintroduce |
| 11584–11627 |   D.2 Banned patterns |
| 11628–11638 |   D.3 Architecturally excluded — not deferred |
| 11639–11647 |  Appendix E — Current state |
| 11648–11670 |  Appendix F — The v2.2.16 registers |
| 11654–11659 |   F.1 Decisions Resolved (v2.2) — the former §17 |
| 11660–11670 |   F.2 Change Log — the former §18 |
| 11664–11670 |    F.2.1 Amendment procedure — the former §18.1 |
