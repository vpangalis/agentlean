# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 11663 lines

| Lines | Heading |
|---|---|
| 27–49 |  🗺 Where state lives — a MAP, not a definition |
| 50–253 | Agentic Architecture Reference |
| 148–253 |  About this document |
| 154–211 |   Scope — three agents, one architecture |
| 212–226 |   The two-document division |
| 227–241 |   Section numbering and provenance |
| 242–253 |   Reading conventions |
| 254–545 | Part I — Orientation |
| 258–334 |  1. What Agent Improve is |
| 278–304 |   What makes it architecturally distinctive |
| 305–334 |   The runtime stack |
| 335–386 |  2. How to read this document |
| 341–357 |   By what you are trying to do |
| 358–386 |   Canonical ownership |
| 387–485 |  3. Terminology |
| 398–414 |   Structural primitives |
| 415–426 |   Role labels |
| 427–444 |   The recursion is two levels, not infinite |
| 445–459 |   "Harness" — two senses, do not conflate |
| 460–470 |   "Agent" — used carefully |
| 471–485 |   Things that are deliberately not levels |
| 486–545 |  4. Architecture at a glance |
| 529–545 |   The five things that shape everything else |
| 546–1273 | Part II — State and Persistence |
| 553–611 |  5. `SupervisorState` — orchestration only |
| 565–571 |   `gate_passed` is a dict, not a list |
| 572–583 |   `current_phase` and `phase_index` are derived, and kept anyway |
| 584–603 |   Four fields were removed as redundant, and may not return |
| 604–611 |   Artifacts are not here |
| 612–847 |  6. `PhaseState` — per-phase subgraph state |
| 627–658 |   `asks` — §56 AMENDMENT, ratified 2026-09-09 |
| 659–728 |   `field_log` — §56 AMENDMENT, ratified 2026-09-21 |
| 729–734 |   `draft`, `belt_edits` and `final` are `dict`, never `str` |
| 735–757 |   `coaching_plan` is one typed plan, not a queue |
| 758–773 |   `gate_attempts` — the field whose absence recreated a production bug |
| 774–794 |   `validator_feedback` and `belt_edits` are different, and must stay separate |
| 795–812 |   `citations` and `uploads` — the evidence trail |
| 813–830 |   `hop_results` and `synthesis_output` must be state, not node locals |
| 831–839 |   Per-phase variants |
| 840–847 |   Naming discipline |
| 848–924 |  7. Field typing law — every captured field is a string |
| 864–876 |   Why strings |
| 877–896 |   The one exception — three cross-phase reference dicts |
| 897–924 |   Computation results |
| 925–1017 |  8. The checkpointer / store split |
| 949–968 |   Phased backend |
| 969–980 |   Concurrency and atomicity |
| 981–996 |   Why Blob, and not Cosmos / Tables / SQLite |
| 997–1017 |   On-blob checkpoint format |
| 1018–1154 |  9. The Store — cross-phase artifacts and boundary mappers |
| 1059–1082 |   Namespace convention |
| 1083–1112 |   Why cross-phase data cannot travel on parent state |
| 1113–1133 |   Boundary mappers |
| 1134–1146 |   Two prohibitions that follow |
| 1147–1154 |   Ordering constraint |
| 1155–1212 |  10. Azure Blob — two distinct concerns |
| 1174–1199 |   Complete physical layout |
| 1200–1212 |   The case blob is not updated per turn |
| 1213–1273 |  11. `step_log` — the audit trail |
| 1234–1243 |   `artifacts` and `step_log` are separate fields and stay separate |
| 1244–1273 |   Entries carry deterministic keys, never a raw timestamp as identity |
| 1274–1644 | Part III — The Graph |
| 1280–1320 |  12. Topology |
| 1310–1320 |   The subgraph builder takes the phase as a parameter |
| 1321–1460 |  13. The phase subgraph — five nodes |
| 1398–1428 |   The subgraph is a cycle, not a pipeline |
| 1429–1441 |   Two node names are BANNED |
| 1442–1447 |   Leaf tools are NOT subgraph nodes |
| 1448–1460 |   The validation stack and the policy advisory are NOT tools |
| 1461–1496 |  14. Node contract |
| 1484–1496 |   Reflection is a node, not a private function |
| 1497–1561 |  15. Routing — static edges and `Command` |
| 1503–1520 |   The decision test |
| 1521–1526 |   Never mix static edges and `Command` from the same node |
| 1527–1554 |   Level 1 does not route — it advances |
| 1555–1561 |   No subgraph imports another subgraph's nodes |
| 1562–1644 |  16. `thread_id`, `checkpoint_ns`, and where persistence attaches |
| 1568–1583 |   One `thread_id` per project |
| 1584–1597 |   The checkpointer and store go on the parent graph ONLY |
| 1598–1624 |   The wrapper node must invoke the subgraph directly (G-44) |
| 1625–1644 |   `recursion_limit` is a backstop, not the hop cap |
| 1645–2386 | Part IV — The Coaching Agent |
| 1651–1765 |  17. The Planner / Executor contract |
| 1727–1757 |   `CoachingPlan` |
| 1758–1765 |   Extraction is structured output, not a node and not a tool |
| 1766–1813 |  18. Building the executor — `create_agent` |
| 1778–1785 |   Binding tools directly onto a bare model is a violation |
| 1786–1791 |   `create_react_agent` is superseded |
| 1792–1804 |   deepagents is not a dependency |
| 1805–1813 |   The structured response and the coaching text coexist |
| 1814–2135 |  19. The middleware stack — eight, in order |
| 1836–1882 |   Ordering rules that bind |
| 1883–1894 |   Three independent retry caps |
| 1895–1938 |   19.1 `BeforeModelStateInjection` — injection timing |
| 1939–1954 |   19.2 `DMAICSkillsMiddleware` — progressive disclosure |
| 1955–1994 |   19.3 `SummarizationMiddleware` — context compression |
| 1995–2021 |   19.4 `ModelRetryMiddleware` — API-level retry |
| 2022–2034 |   19.5 `ToolRetryMiddleware` — tool-level retry |
| 2035–2057 |   19.6 `ContradictionDetectionMiddleware` — the mid-phase check |
| 2058–2092 |   19.7 `CoherenceMiddleware` — validation Layer 2a |
| 2093–2123 |   19.8 `DMAICGraderMiddleware` — coaching process quality |
| 2124–2135 |   19.9 Middleware deliberately NOT used |
| 2136–2210 |  20. `CoachingResponse` — the per-turn schema |
| 2190–2193 |   The executor node writes the response into state |
| 2194–2200 |   The executor's `response_format` is `CoachingResponse`, never a phase Output |
| 2201–2210 |   What structured output does NOT give you |
| 2211–2322 |  21. LLM roles, temperature, and the factory |
| 2231–2239 |   Factory only |
| 2240–2260 |   Roles |
| 2261–2277 |   Temperature |
| 2278–2322 |   Structured output — scoped by call type |
| 2323–2386 |  22. Prompts |
| 2349–2369 |   The memory hierarchy paragraph is mandatory |
| 2370–2386 |   Anti-hallucination guards are mandatory |
| 2387–3165 | Part V — Knowledge and Retrieval |
| 2391–2746 |  23. The three indexes |
| 2403–2453 |   23.1 `improve_knowledge_index` — methodology |
| 2454–2579 |   23.2 `improve_evidence_index` — Belt-uploaded evidence |
| 2499–2523 |    Supersession deletes; it does not flag |
| 2524–2579 |    Two Azure behaviours govern the migration |
| 2580–2652 |   23.2.1 The `role` vocabulary — ratified, not invented per phase |
| 2619–2652 |    `unclassified (pre-ask-binding)` is a MIGRATION SENTINEL, not a thirteenth role |
| 2653–2701 |   23.3 `improve_case_index` — case records (cross-case memory) |
| 2702–2712 |   The internal phase key is `analyse`, never `analyse_phase` |
| 2713–2737 |   23.4 The write-path trap that made `phase_relevance` unfilterable |
| 2738–2746 |   23.5 Schema change procedure |
| 2747–2875 |  24. The three `rag_lookup_*` tools |
| 2765–2822 |   `rag_lookup_evidence` returns a structured record, not rendered text |
| 2823–2835 |   RAG via tool, never via prepended system message |
| 2836–2860 |   The retrieval mechanism |
| 2861–2868 |   `belt_level` filtering is OFF by default |
| 2869–2875 |   `source_file` and `page_number` are returned, never filtered |
| 2876–2941 |  25. Multi-query and Reciprocal Rank Fusion |
| 2885–2901 |   Why it is mandatory |
| 2902–2908 |   The implementation |
| 2909–2930 |   `MultiQueryRetriever` and `EnsembleRetriever` are BANNED |
| 2931–2941 |   Encapsulation |
| 2942–3075 |  26. Multi-hop retrieval |
| 2957–2993 |   The hop cap is `RemainingSteps` |
| 2994–3012 |   Per-phase policy |
| 3013–3057 |   Planned multi-hop — the Analyse pipeline |
| 3058–3075 |   **UNVERIFIED** — planned multi-hop is Analyse-only |
| 3076–3122 |  27. Retrieval failure semantics |
| 3087–3095 |   Never wrap a retrieval call in a bare `except Exception` returning `[]` |
| 3096–3105 |   Three rules that each have already bitten |
| 3106–3122 |   The coach-facing message must not read as absence |
| 3123–3165 |  28. Memory taxonomy |
| 3141–3165 |   The static/dynamic split is the part that matters |
| 3166–3512 | Part VI — Tools |
| 3170–3327 |  29. The data channel and the universal eight |
| 3176–3211 |   29.1 There is no MCP — the data-channel decision |
| 3212–3254 |   29.2 The universal eight |
| 3220–3254 |    `load_evidence_series` joins the set — RATIFIED 2026-09-09 |
| 3255–3264 |   29.3 `record_field` is RETIRED and may not be reintroduced |
| 3265–3327 |   29.4 Cross-agent tools — a third category, present but NOT BOUND |
| 3328–3402 |  30. Computation tools and per-phase binding |
| 3333–3370 |   Tool sets are per phase, not universal |
| 3371–3376 |   Each of the 20 is a separate named tool |
| 3377–3385 |   All 20 are pure functions |
| 3386–3395 |   `imr_chart_limits` — the choice that is usually wrong by default |
| 3396–3402 |   Tool decisions are the model's, not the graph's |
| 3403–3435 |  31. Tool arg schemas and docstrings |
| 3409–3414 |   Every `@tool` uses `args_schema=` |
| 3415–3435 |   Docstrings are interface, not commentary |
| 3436–3512 |  32. Phase skills — SKILL.md |
| 3459–3463 |   Each skill's `allowed-tools` MUST match that phase's subset in §30 |
| 3464–3473 |   Progressive disclosure — three levels |
| 3474–3479 |   Storage backend: `FilesystemBackend` |
| 3480–3501 |   Each SKILL.md must carry |
| 3502–3512 |   Two distinct kinds of skill exist in this repository |
| 3513–4093 | Part VII — Validation and Gates |
| 3520–3640 |  33. The nine-step HITL gate |
| 3541–3554 |   Two quality checks, two actors, two moments |
| 3555–3566 |   Gates are one-way doors, with exactly one defined exception |
| 3567–3571 |   Implementation: graph-level `interrupt()` |
| 3572–3602 |   33.1 The two-node split |
| 3603–3632 |   33.2 `gate_apply_node` writes the gate document TWICE |
| 3633–3640 |   33.3 The checkpoint commits only after Belt approval |
| 3641–3744 |  34. The four-layer validation stack |
| 3656–3663 |   Layer 2a is middleware; layers 2b–2d are the node |
| 3664–3670 |   Layer 2d is NOT `DMAICGraderMiddleware` |
| 3671–3676 |   Run cheapest first |
| 3677–3686 |   The counter and the feedback |
| 3687–3696 |   Layer 2b is the only deterministic layer, deliberately |
| 3697–3708 |   Per-phase constraint sets |
| 3709–3718 |   34.1 Where each check fires |
| 3719–3744 |   34.2 The self-healing hierarchy and the transparency principle |
| 3745–3880 |  35. Two tiers of field, and the `warning` verdict |
| 3751–3765 |   The problem this solves |
| 3766–3782 |   Three distinct things check these fields, and conflating them is a design error |
| 3783–3831 |   Gate-required fields by phase |
| 3832–3848 |   The grader's verdict has three statuses |
| 3849–3856 |   Why two tiers |
| 3857–3880 |   The grader is belt-level aware |
| 3881–3974 |  36. Two graders — and why they are not redundant |
| 3900–3913 |   Why both exist |
| 3914–3937 |   `COACHING_QUALITY_RUBRIC` |
| 3938–3947 |   Mechanism, both graders |
| 3948–3957 |   Three criteria are verified deterministically, not by judgment |
| 3958–3974 |   The ratified rubric coverage |
| 3975–4071 |  37. Mid-phase contradiction and the re-approval cascade |
| 3981–4002 |   The check runs every turn, not only at gates |
| 4003–4036 |   §37 governs a GATE-COMMITTED value only |
| 4037–4050 |   There is NO tolerance threshold, and none may be added |
| 4051–4058 |   The re-approval cascade |
| 4059–4071 |   The cascade has a hard dependency on compensating actions |
| 4072–4093 |  38. Escalation |
| 4094–5674 | Part VIII — The DMAIC Domain |
| 4101–5295 |  39. The five phases |
| 4119–4133 |   The measurement thread that runs across three phases |
| 4134–4368 |   39.1 Define phase, complete specification |
| 4141–4148 |    39.1.1 Purpose |
| 4149–4211 |    39.1.2 The ordered field list — the `field_index` sequence (closes G-38) |
| 4212–4226 |    39.1.3 The composed-problem-statement rule (binding) |
| 4227–4241 |    39.1.4 The `team` structure |
| 4242–4251 |    39.1.5 SIPOC handling |
| 4252–4263 |    39.1.6 Gate, storage, progress view |
| 4264–4282 |    39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4283–4289 |    39.1.8 The other four phases |
| 4290–4322 |    39.1.9 The metric registry and Define's placeholder |
| 4323–4330 |    39.1.10 Tools bound to Define |
| 4331–4338 |    39.1.11 Conditions — routing and the gate |
| 4339–4346 |    39.1.12 State parameters — Define's use of `PhaseState` |
| 4347–4354 |    39.1.13 Metric literacy — what each metric means |
| 4355–4368 |    39.1.14 Cross-phase reads and writes |
| 4369–4624 |   39.2 Measure phase, complete specification |
| 4379–4387 |    39.2.1 Purpose |
| 4388–4410 |    39.2.2 The ordered field list — the `field_index` sequence |
| 4411–4471 |    39.2.3 The metric registry and Measure's placeholder |
| 4472–4491 |    39.2.4 SIPOC → the detailed process map |
| 4492–4513 |    39.2.5 Tools bound to Measure |
| 4514–4543 |    39.2.6 Conditions — sequence locks, routing, and the gate |
| 4544–4561 |    39.2.7 State parameters — Measure's use of `PhaseState` |
| 4562–4578 |    39.2.8 Metric literacy — what each metric means |
| 4579–4592 |    39.2.9 Gate, storage, progress view |
| 4593–4601 |    39.2.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4602–4618 |    39.2.11 Cross-phase reads and writes |
| 4619–4624 |    39.2.12 The other two phases |
| 4625–4854 |   39.3 Analyse phase, complete specification |
| 4635–4644 |    39.3.1 Purpose |
| 4645–4670 |    39.3.2 The ordered field list — the `field_index` sequence |
| 4671–4707 |    39.3.3 The metric registry and Analyse's placeholder (linkage form — closes F-13) |
| 4708–4727 |    39.3.4 Two movements — generate, then validate |
| 4728–4750 |    39.3.5 Tools bound to Analyse |
| 4751–4779 |    39.3.6 Conditions — methodology guards, routing, and the gate |
| 4780–4793 |    39.3.7 State parameters — Analyse's use of `PhaseState` |
| 4794–4809 |    39.3.8 Metric literacy — what each metric and statistic means |
| 4810–4821 |    39.3.9 Gate, storage, progress view |
| 4822–4830 |    39.3.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4831–4848 |    39.3.11 Cross-phase reads and writes |
| 4849–4854 |    39.3.12 The other phase |
| 4855–5057 |   39.4 Improve phase, complete specification |
| 4865–4873 |    39.4.1 Purpose |
| 4874–4894 |    39.4.2 The ordered field list — the `field_index` sequence |
| 4895–4913 |    39.4.3 The metric registry and Improve's placeholder (linkage form) |
| 4914–4931 |    39.4.4 Two movements — generate-and-select, then pilot-and-prove |
| 4932–4950 |    39.4.5 Tools bound to Improve |
| 4951–4982 |    39.4.6 Conditions — methodology guards, DOE belt-gating, routing, gate |
| 4983–4996 |    39.4.7 State parameters — Improve's use of `PhaseState` |
| 4997–5010 |    39.4.8 Metric literacy — what each metric and statistic means |
| 5011–5022 |    39.4.9 Gate, storage, progress view |
| 5023–5032 |    39.4.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5033–5049 |    39.4.11 Cross-phase reads and writes |
| 5050–5057 |    39.4.12 The last phase |
| 5058–5295 |   39.5 Control phase, complete specification |
| 5068–5076 |    39.5.1 Purpose |
| 5077–5105 |    39.5.2 The ordered field list — the `field_index` sequence |
| 5106–5135 |    39.5.3 The metric registry, the comparison, and single authority (closes F-14) |
| 5136–5152 |    39.5.4 Two movements — confirm it held, then lock it in |
| 5153–5172 |    39.5.5 Tools bound to Control |
| 5173–5205 |    39.5.6 Conditions — guards, routing, gate |
| 5206–5219 |    39.5.7 State parameters — Control's use of `PhaseState` |
| 5220–5234 |    39.5.8 Metric literacy — what each metric and statistic means |
| 5235–5248 |    39.5.9 Gate, storage, progress view |
| 5249–5259 |    39.5.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5260–5275 |    39.5.11 Cross-phase reads and writes — the thread closes here |
| 5276–5295 |    39.5.12 The measurement thread, closed |
| 5296–5391 |  40. The five `{Phase}Output` schemas |
| 5319–5337 |   Field counts |
| 5338–5349 |   The four gate-metadata fields |
| 5350–5363 |   Three fields are on all five schemas |
| 5364–5391 |   40.1 Gate assembly |
| 5392–5475 |  41. Structured dict fields, and FMEA |
| 5414–5425 |   The grader checks every sub-field is populated |
| 5426–5434 |   `control_plan` is `dict`, never `str` |
| 5435–5443 |   `stability_assessment` is checked BEFORE capability |
| 5444–5455 |   `experiment_justification` is Tier 1 and does not require an experiment |
| 5456–5475 |   FMEA has no field in any schema, and none may be added |
| 5476–5507 |  42. Cross-phase reference fields in practice |
| 5508–5674 |  43. The coaching method |
| 5526–5553 |   43.1 The seven-step computation pattern |
| 5554–5591 |   43.2 Show before asking |
| 5592–5614 |   43.3 The A→F session flow |
| 5615–5646 |   43.4 The live gate document preview |
| 5647–5656 |   43.5 No external URLs |
| 5657–5674 |   43.6 What the coach must not do |
| 5675–6031 | Part IX — Reliability |
| 5679–5707 |   43.7 Metric literacy — the metric, and the statistic |
| 5708–5736 |  44. The failure pipeline |
| 5737–5849 |  45. Timeouts and compensating actions |
| 5744–5775 |   Per-node timeouts — required on every phase executor node |
| 5776–5785 |   Composition order — retries run BEFORE the handler |
| 5786–5795 |   Node-level error handlers — required on every node with external writes |
| 5796–5801 |   Hand-written Saga orchestrators are BANNED |
| 5802–5810 |   Two dependencies on this rule, both correctness-critical |
| 5811–5842 |   Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST** |
| 5843–5849 |   `DeltaChannel` is NOT used |
| 5850–5965 |  46. The fallback chain and circuit breakers |
| 5856–5868 |   The v2.1 four-level chain |
| 5869–5875 |   Backoff strategy is chosen per level, not globally |
| 5876–5894 |   Level 3 cache |
| 5895–5910 |   Circuit breakers — three-state, two instances |
| 5911–5917 |   Degraded mode uses actual state, never a generic error |
| 5918–5925 |   HTTP 400 is NOT a fallback case |
| 5926–5965 |   46.1 Geographic redundancy — **DEFERRED** |
| 5966–6006 |  47. Disconnect policy — what a dropped client commits |
| 5983–5989 |   Ratified policy: ABANDON, not COMPLETE |
| 5990–6006 |   Five requirements |
| 6007–6031 |  48. Structured errors |
| 6032–6520 | Part X — Operations |
| 6036–6090 |  49. API surface |
| 6042–6051 |   One runtime |
| 6052–6059 |   Async by default |
| 6060–6084 |   Endpoints |
| 6085–6090 |   Envelopes are Pydantic v2 |
| 6091–6247 |  50. UI and language rules |
| 6098–6136 |   50.1 Coach response structure |
| 6137–6148 |   Plain language always |
| 6149–6156 |   Citations |
| 6157–6170 |   Contextual feedback |
| 6171–6177 |   Connection status before the first interaction |
| 6178–6183 |   The gate review screen |
| 6184–6222 |   The live gate document |
| 6223–6234 |   The all-gate-fields tab is the contradiction backstop |
| 6235–6247 |   The conflict resolution panel |
| 6248–6323 |  51. Tracing and observability |
| 6254–6264 |   LangSmith is mandatory |
| 6265–6297 |   `@traceable` on every custom function |
| 6298–6303 |   What gets traced |
| 6304–6311 |   P50/P99 latency is a coaching quality signal |
| 6312–6323 |   Logs |
| 6324–6378 |  52. Evaluation and regression testing |
| 6330–6337 |   Built alongside the refactor, not before it |
| 6338–6344 |   The dataset is authored jointly, not generated |
| 6345–6358 |   Minimum viable suite |
| 6359–6369 |   Rubrics and the eval dataset are complementary, not duplicative |
| 6370–6378 |   Two open validation questions this suite answers |
| 6379–6520 |  53. Configuration, dependencies and deployment |
| 6385–6401 |   Fail-fast environment validation |
| 6402–6425 |   Dependency floor |
| 6426–6436 |   `/verify-current-version` is a mandatory checkpoint |
| 6437–6444 |   Infrastructure not yet provisioned |
| 6445–6456 |   Deployment layer: FastAPI, not LangGraph Server |
| 6457–6520 |   53.1 Migration sequence |
| 6521–7089 | Part XI — Governance |
| 6525–6567 |  54. Where code is allowed to live |
| 6532–6549 |   Classes are permitted ONLY in these files |
| 6550–6567 |   Target folder structure |
| 6568–6938 |  55. Anti-drift |
| 6582–6596 |   Rule numbers are load-bearing |
| 6597–6607 |   The registry guards code, not documentation |
| 6608–6613 |   Verification discipline |
| 6614–6636 |   Reference sweeps must use raw `grep -rn`, never a gitignore-filtered tool |
| 6637–6687 |   55.1 Spec-layer governance rules |
| 6688–6770 |   55.2 The BUILT markers, and the paths that oblige a re-check |
| 6771–6851 |   55.3 The phase completeness set — what one phase actually traverses |
| 6852–6901 |   55.4 Facts have one owner — the ratified minimum |
| 6902–6938 |   55.5 The commit gates govern. The rule files are advisory context. |
| 6939–7089 |  56. Amendment procedure |
| 6966–7009 |   56.0 What changed about amending, when the rules stopped being one file |
| 7010–7028 |   56.0.1 Rule, reference, and owned fact — three destinations |
| 7029–7071 |   56.1 A phase is one atomic unit — schema, validator, skill |
| 7072–7089 |   What requires an amendment rather than a routine change |
| 7090–11434 | Part XII — Specification |
| 7100–7123 |   56.2 The rule lands here; the reasoning lands in the commit |
| 7124–7157 |   56.3 The tree at HEAD is the only source of truth |
| 7158–7419 |  57. The specification layer — how to read and write a spec entry |
| 7165–7185 |   Why this Part exists |
| 7186–7201 |   The five structural rules |
| 7202–7216 |   Entry identity and traceability |
| 7217–7264 |   The entry template — three layers |
| 7265–7276 |   How gaps are marked |
| 7277–7293 |   57.1 The two calibrated samples |
| 7294–7347 |   57.2 SAMPLE 1 — CLASS TEMPLATE — S-C01 `SupervisorState` |
| 7297–7347 |    SPEC — `SupervisorState` |
| 7348–7398 |   57.3 SAMPLE 2 — FUNCTION/NODE TEMPLATE — S-F04 `phase_executor` (the coach node) |
| 7352–7398 |    SPEC — `phase_executor` (the coach node) |
| 7399–7419 |   57.4 Entry index |
| 7420–8749 |  58. Spec — graph management |
| 7430–7433 |   58.1 S-C01 · `SupervisorState` |
| 7434–7599 |   58.2 S-C02 · `PhaseState` |
| 7600–7618 |   58.3 S-C03 · Per-phase use of `PhaseState` |
| 7619–7694 |   58.4 S-C04 · `CoachingPlan` |
| 7695–7804 |   58.5 S-C05 · `CoachingResponse` |
| 7805–7856 |   58.6 S-C06 · `AzureBlobStore` |
| 7857–7902 |   58.7 S-C07 · `AzureBlobCheckpointSaver` |
| 7903–7949 |   58.8 S-C08 · `ImproveBlobClient` |
| 7950–8012 |   58.9 S-C09 · `storage/models.py` — the record models |
| 8013–8076 |   58.10 S-F01 · The supervisor graph — static edges |
| 8047–8056 |    SIPOC — at a glance |
| 8057–8076 |    Behaviors (EARS) |
| 8077–8122 |   58.11 S-F02 · `build_phase_subgraph(phase, llm)` |
| 8095–8104 |    SIPOC — at a glance |
| 8105–8122 |    Behaviors (EARS) |
| 8123–8163 |   58.12 S-F03 · `phase_planner` node |
| 8134–8143 |    SIPOC — at a glance |
| 8144–8163 |    Behaviors (EARS) |
| 8164–8175 |   58.13 S-F04 · `phase_executor` node |
| 8176–8237 |   58.14 S-F05 · `validation_stack` node |
| 8186–8195 |    SIPOC — at a glance |
| 8196–8207 |    Behaviors (EARS) |
| 8208–8237 |    ⚠ AI-ACT — high-risk surface |
| 8238–8289 |   58.15 S-F06 · `gate_review_node` |
| 8248–8257 |    SIPOC — at a glance |
| 8258–8265 |    Behaviors (EARS) |
| 8266–8289 |    ⚠ AI-ACT — high-risk surface |
| 8290–8357 |   58.16 S-F07 · `gate_apply_node` |
| 8311–8320 |    SIPOC — at a glance |
| 8321–8333 |    Behaviors (EARS) |
| 8334–8357 |    ⚠ AI-ACT — high-risk surface |
| 8358–8393 |   58.17 S-F08 · The escalation subgraph |
| 8366–8375 |    SIPOC — at a glance |
| 8376–8393 |    Behaviors (EARS) |
| 8394–8462 |   58.18 S-F09 · `analyse_executor_node` |
| 8434–8443 |    SIPOC — at a glance |
| 8444–8462 |    Behaviors (EARS) |
| 8463–8556 |   58.19 S-F10 · `define_input_mapper` |
| 8506–8518 |    SIPOC — at a glance |
| 8519–8547 |    Execution site — where a boundary mapper actually runs |
| 8548–8556 |    Behaviors (EARS) |
| 8557–8610 |   58.20 S-F11 · `define_output_mapper` |
| 8586–8595 |    SIPOC — at a glance |
| 8596–8610 |    Behaviors (EARS) |
| 8611–8660 |   58.21 S-F12 · The Measure, Analyse, Improve and Control mapper pairs |
| 8619–8628 |    SIPOC — at a glance |
| 8629–8660 |    Behaviors (EARS) |
| 8661–8749 |   58.22 S-F13 · Level 2 `Command` routing |
| 8678–8695 |    DP1 — the planner owns the field / gate decision |
| 8696–8716 |    DP2 — the validation stack's three exits |
| 8717–8737 |    DP3 — the gate exits |
| 8738–8749 |    What is settled and binds |
| 8750–9132 |  59. Spec — knowledge and retrieval |
| 8763–8792 |   59.1 S-C16 · `Hop` |
| 8793–8839 |   59.2 S-C17 · `Plan` — the hop decomposition plan |
| 8840–8876 |   59.3 S-C18 · `SynthesisOutput` |
| 8877–8893 |   59.4 S-C19 · `QueryVariants` |
| 8894–8940 |   59.5 S-F14 · `rag_lookup_methodology` |
| 8915–8924 |    SIPOC — at a glance |
| 8925–8940 |    Behaviors (EARS) |
| 8941–8988 |   59.6 S-F15 · `rag_lookup_evidence` |
| 8964–8973 |    SIPOC — at a glance |
| 8974–8988 |    Behaviors (EARS) |
| 8989–9035 |   59.7 S-F16 · `rag_lookup_case_history` |
| 9012–9021 |    SIPOC — at a glance |
| 9022–9035 |    Behaviors (EARS) |
| 9036–9086 |   59.8 S-F17 · `reciprocal_rank_fusion` |
| 9063–9072 |    SIPOC — at a glance |
| 9073–9086 |    Behaviors (EARS) |
| 9087–9132 |   59.9 S-F18 · The retriever layer — `search_knowledge`, `search_cases`, `search_evidence` |
| 9115–9132 |    SIPOC — at a glance |
| 9133–9418 |  60. Spec — tools |
| 9151–9184 |   60.1 S-F19 · `propose_template` |
| 9164–9184 |    SIPOC — at a glance |
| 9185–9223 |   60.2 S-F20 · `propose_diagram` |
| 9200–9209 |    SIPOC — at a glance |
| 9210–9223 |    Behaviors (EARS) |
| 9224–9265 |   60.3 S-F21 · `check_gate_status` |
| 9239–9248 |    SIPOC — at a glance |
| 9249–9265 |    Behaviors (EARS) |
| 9266–9301 |   60.4 S-F22 · `request_human_approval` |
| 9280–9301 |    SIPOC — at a glance |
| 9302–9318 |   60.5 S-F23 · `load_skill(name)` |
| 9319–9363 |   60.6 S-F24 · The 20 computation tools |
| 9342–9363 |    Behaviors (EARS) — binding on all twenty |
| 9364–9418 |   60.7 S-F57 · `load_evidence_series(blob_path, column)` |
| 9389–9398 |    SIPOC — at a glance |
| 9399–9418 |    Behaviors (EARS) |
| 9419–9671 |  61. Spec — the coaching agent's middleware |
| 9437–9499 |   61.1 S-C10 · `ContradictionDetectionMiddleware` |
| 9459–9468 |    Behaviors (EARS) |
| 9469–9499 |    ⚠ AI-ACT — high-risk surface |
| 9500–9541 |   61.2 S-C11 · `BeforeModelStateInjection` |
| 9513–9541 |    Behaviors (EARS) |
| 9542–9581 |   61.3 S-C12 · `DMAICSkillsMiddleware` |
| 9562–9581 |    Behaviors (EARS) |
| 9582–9618 |   61.4 S-C13 · `CoherenceMiddleware` |
| 9596–9618 |    Behaviors (EARS) |
| 9619–9654 |   61.5 S-C14 · `DMAICGraderMiddleware` |
| 9629–9654 |    Behaviors (EARS) |
| 9655–9671 |   61.6 S-C15 · `HITLInterrupt` |
| 9672–10079 |  62. Spec — validation and gates |
| 9686–9728 |   62.1 S-C20 · `CriterionVerdict` |
| 9729–9746 |   62.2 S-C21 · `GraderVerdict` |
| 9747–9760 |   62.3 S-C22 · `CoachingGraderVerdict` |
| 9761–9772 |   62.4 S-C23 · `CoherenceResult` |
| 9773–9787 |   62.5 S-C24 · `ConstraintCheckResult` / `ConstraintVerdict` |
| 9788–9800 |   62.6 S-C25 · `PolicyAdvisoryResult` |
| 9801–9837 |   62.7 S-C26 · `DMAICGateValidator` |
| 9838–9872 |   62.8 S-F25 · Layer 2c — the constraint check |
| 9847–9856 |    SIPOC — at a glance |
| 9857–9872 |    Behaviors (EARS) |
| 9873–9920 |   62.9 S-F26 · Layer 2d — the gate grader |
| 9888–9897 |    SIPOC — at a glance |
| 9898–9920 |    Behaviors (EARS) |
| 9921–9962 |   62.10 S-F27 · The policy advisory |
| 9936–9945 |    SIPOC — at a glance |
| 9946–9962 |    Behaviors (EARS) |
| 9963–10079 |   62.11 S-F28 · Gate document assembly |
| 10051–10060 |    SIPOC — at a glance |
| 10061–10079 |    Behaviors (EARS) |
| 10080–10601 |  63. Spec — the DMAIC gate documents |
| 10098–10166 |   63.1 S-C27 · `DefineOutput` |
| 10167–10207 |   63.2 S-C28 · `MeasureOutput` |
| 10208–10265 |   63.3 S-C29 · `AnalyseOutput` |
| 10266–10325 |   63.4 S-C30 · `ImproveOutput` |
| 10326–10397 |   63.5 S-C31 · `ControlOutput` |
| 10398–10464 |   63.6 S-C32 · The three cross-phase reference dicts |
| 10465–10506 |   63.7 S-C33 · The three structured dict fields |
| 10507–10545 |   63.8 S-C38 · `metric_definitions` — the project metric registry |
| 10546–10601 |   63.9 S-C39 · `phase_metrics` — the per-phase placeholder |
| 10602–10890 |  64. Spec — reliability |
| 10613–10653 |   64.1 S-C34 · `AgentImproveError` |
| 10654–10692 |   64.2 S-C35 · `CircuitBreaker` |
| 10693–10779 |   64.3 S-F29 · `phase_error_recovery` |
| 10721–10730 |    SIPOC — at a glance |
| 10731–10779 |    Behaviors (EARS) |
| 10780–10828 |   64.4 S-F30 · `degraded_mode_response` |
| 10801–10810 |    SIPOC — at a glance |
| 10811–10828 |    Behaviors (EARS) |
| 10829–10847 |   64.5 S-F31 · `synthesise_partial` |
| 10848–10872 |   64.6 S-F32 · `delete_or_flag_stale_in_case_index` |
| 10873–10890 |   64.7 S-F33 · `degraded_coaching_response` node |
| 10891–11067 |  65. Spec — API, UI and evidence |
| 10901–10921 |   65.1 S-C36 · `CitationRecord` and `CitationBundle` |
| 10922–10939 |   65.2 S-C37 · The API envelopes |
| 10940–10992 |   65.3 S-F34 · The API surface |
| 10962–10971 |    SIPOC — at a glance |
| 10972–10992 |    Behaviors (EARS) |
| 10993–11032 |   65.4 S-F35 · The upload handler |
| 11018–11032 |    Behaviors (EARS) |
| 11033–11067 |   65.5 S-F36 · The `improve_case_index` write path |
| 11068–11078 |  66. The SPEC-GAP register — MOVED |
| 11079–11172 |  67. EU AI Act compliance posture |
| 11086–11101 |   67.1 The deadlines are now fixed |
| 11102–11127 |   67.2 The classification question — open, and not answered here |
| 11128–11145 |   67.3 The eight core provider obligations |
| 11146–11156 |   67.4 One compliance finding is already recorded in this document |
| 11157–11172 |   67.5 Compliance-source discipline |
| 11173–11253 |  68. The DORA-structured compliance risk register |
| 11180–11197 |   68.1 Why DORA structure |
| 11198–11214 |   68.2 The register |
| 11215–11238 |   68.3 Pending classification — not register rows |
| 11239–11253 |   68.4 The infrastructure risk already on record |
| 11254–11434 |  69. Spec — computation tools |
| 11283–11354 |   69.1 Common conventions — stated once, binding on all twenty |
| 11355–11360 |   69.2 S-F37 · Define — 1 tool |
| 11361–11373 |   69.3 S-F38–S-F45 · Measure — 8 tools |
| 11374–11383 |   69.4 S-F46–S-F50 · Analyse — 5 tools |
| 11384–11389 |   69.5 S-F51 · Improve — 1 tool |
| 11390–11407 |   69.6 S-F52–S-F56 · Control — 5 tools |
| 11408–11434 |   69.7 The Measure control-chart boundary — a tool that is deliberately absent |
| 11435–11663 | Appendices |
| 11439–11454 |  Appendix A — Provenance index |
| 11445–11448 |   A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference |
| 11449–11454 |   A.2 `agent-improve/ARCHITECTURE.md` → this reference |
| 11455–11485 |  Appendix B — Deferred backlog |
| 11486–11551 |  Appendix C — Trusted sources |
| 11492–11511 |   Tier 1 — current, authoritative |
| 11512–11530 |   Tier 1 — compliance |
| 11531–11534 |   Tier 2 — official announcements |
| 11535–11538 |   Tier 3 — informed practitioner, cross-check before citing |
| 11539–11545 |   Downgraded — historical |
| 11546–11551 |   Excluded |
| 11552–11631 |  Appendix D — Retired names, banned patterns, and exclusions |
| 11554–11576 |   D.1 Retired names — never reintroduce |
| 11577–11620 |   D.2 Banned patterns |
| 11621–11631 |   D.3 Architecturally excluded — not deferred |
| 11632–11640 |  Appendix E — Current state |
| 11641–11663 |  Appendix F — The v2.2.16 registers |
| 11647–11652 |   F.1 Decisions Resolved (v2.2) — the former §17 |
| 11653–11663 |   F.2 Change Log — the former §18 |
| 11657–11663 |    F.2.1 Amendment procedure — the former §18.1 |
