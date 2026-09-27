# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 11671 lines

| Lines | Heading |
|---|---|
| 27–49 |  🗺 Where state lives — a MAP, not a definition |
| 50–261 | Agentic Architecture Reference |
| 156–261 |  About this document |
| 162–219 |   Scope — three agents, one architecture |
| 220–234 |   The two-document division |
| 235–249 |   Section numbering and provenance |
| 250–261 |   Reading conventions |
| 262–553 | Part I — Orientation |
| 266–342 |  1. What Agent Improve is |
| 286–312 |   What makes it architecturally distinctive |
| 313–342 |   The runtime stack |
| 343–394 |  2. How to read this document |
| 349–365 |   By what you are trying to do |
| 366–394 |   Canonical ownership |
| 395–493 |  3. Terminology |
| 406–422 |   Structural primitives |
| 423–434 |   Role labels |
| 435–452 |   The recursion is two levels, not infinite |
| 453–467 |   "Harness" — two senses, do not conflate |
| 468–478 |   "Agent" — used carefully |
| 479–493 |   Things that are deliberately not levels |
| 494–553 |  4. Architecture at a glance |
| 537–553 |   The five things that shape everything else |
| 554–1281 | Part II — State and Persistence |
| 561–619 |  5. `SupervisorState` — orchestration only |
| 573–579 |   `gate_passed` is a dict, not a list |
| 580–591 |   `current_phase` and `phase_index` are derived, and kept anyway |
| 592–611 |   Four fields were removed as redundant, and may not return |
| 612–619 |   Artifacts are not here |
| 620–855 |  6. `PhaseState` — per-phase subgraph state |
| 635–666 |   `asks` — §56 AMENDMENT, ratified 2026-09-09 |
| 667–736 |   `field_log` — §56 AMENDMENT, ratified 2026-09-21 |
| 737–742 |   `draft`, `belt_edits` and `final` are `dict`, never `str` |
| 743–765 |   `coaching_plan` is one typed plan, not a queue |
| 766–781 |   `gate_attempts` — the field whose absence recreated a production bug |
| 782–802 |   `validator_feedback` and `belt_edits` are different, and must stay separate |
| 803–820 |   `citations` and `uploads` — the evidence trail |
| 821–838 |   `hop_results` and `synthesis_output` must be state, not node locals |
| 839–847 |   Per-phase variants |
| 848–855 |   Naming discipline |
| 856–932 |  7. Field typing law — every captured field is a string |
| 872–884 |   Why strings |
| 885–904 |   The one exception — three cross-phase reference dicts |
| 905–932 |   Computation results |
| 933–1025 |  8. The checkpointer / store split |
| 957–976 |   Phased backend |
| 977–988 |   Concurrency and atomicity |
| 989–1004 |   Why Blob, and not Cosmos / Tables / SQLite |
| 1005–1025 |   On-blob checkpoint format |
| 1026–1162 |  9. The Store — cross-phase artifacts and boundary mappers |
| 1067–1090 |   Namespace convention |
| 1091–1120 |   Why cross-phase data cannot travel on parent state |
| 1121–1141 |   Boundary mappers |
| 1142–1154 |   Two prohibitions that follow |
| 1155–1162 |   Ordering constraint |
| 1163–1220 |  10. Azure Blob — two distinct concerns |
| 1182–1207 |   Complete physical layout |
| 1208–1220 |   The case blob is not updated per turn |
| 1221–1281 |  11. `step_log` — the audit trail |
| 1242–1251 |   `artifacts` and `step_log` are separate fields and stay separate |
| 1252–1281 |   Entries carry deterministic keys, never a raw timestamp as identity |
| 1282–1652 | Part III — The Graph |
| 1288–1328 |  12. Topology |
| 1318–1328 |   The subgraph builder takes the phase as a parameter |
| 1329–1468 |  13. The phase subgraph — five nodes |
| 1406–1436 |   The subgraph is a cycle, not a pipeline |
| 1437–1449 |   Two node names are BANNED |
| 1450–1455 |   Leaf tools are NOT subgraph nodes |
| 1456–1468 |   The validation stack and the policy advisory are NOT tools |
| 1469–1504 |  14. Node contract |
| 1492–1504 |   Reflection is a node, not a private function |
| 1505–1569 |  15. Routing — static edges and `Command` |
| 1511–1528 |   The decision test |
| 1529–1534 |   Never mix static edges and `Command` from the same node |
| 1535–1562 |   Level 1 does not route — it advances |
| 1563–1569 |   No subgraph imports another subgraph's nodes |
| 1570–1652 |  16. `thread_id`, `checkpoint_ns`, and where persistence attaches |
| 1576–1591 |   One `thread_id` per project |
| 1592–1605 |   The checkpointer and store go on the parent graph ONLY |
| 1606–1632 |   The wrapper node must invoke the subgraph directly (G-44) |
| 1633–1652 |   `recursion_limit` is a backstop, not the hop cap |
| 1653–2394 | Part IV — The Coaching Agent |
| 1659–1773 |  17. The Planner / Executor contract |
| 1735–1765 |   `CoachingPlan` |
| 1766–1773 |   Extraction is structured output, not a node and not a tool |
| 1774–1821 |  18. Building the executor — `create_agent` |
| 1786–1793 |   Binding tools directly onto a bare model is a violation |
| 1794–1799 |   `create_react_agent` is superseded |
| 1800–1812 |   deepagents is not a dependency |
| 1813–1821 |   The structured response and the coaching text coexist |
| 1822–2143 |  19. The middleware stack — eight, in order |
| 1844–1890 |   Ordering rules that bind |
| 1891–1902 |   Three independent retry caps |
| 1903–1946 |   19.1 `BeforeModelStateInjection` — injection timing |
| 1947–1962 |   19.2 `DMAICSkillsMiddleware` — progressive disclosure |
| 1963–2002 |   19.3 `SummarizationMiddleware` — context compression |
| 2003–2029 |   19.4 `ModelRetryMiddleware` — API-level retry |
| 2030–2042 |   19.5 `ToolRetryMiddleware` — tool-level retry |
| 2043–2065 |   19.6 `ContradictionDetectionMiddleware` — the mid-phase check |
| 2066–2100 |   19.7 `CoherenceMiddleware` — validation Layer 2a |
| 2101–2131 |   19.8 `DMAICGraderMiddleware` — coaching process quality |
| 2132–2143 |   19.9 Middleware deliberately NOT used |
| 2144–2218 |  20. `CoachingResponse` — the per-turn schema |
| 2198–2201 |   The executor node writes the response into state |
| 2202–2208 |   The executor's `response_format` is `CoachingResponse`, never a phase Output |
| 2209–2218 |   What structured output does NOT give you |
| 2219–2330 |  21. LLM roles, temperature, and the factory |
| 2239–2247 |   Factory only |
| 2248–2268 |   Roles |
| 2269–2285 |   Temperature |
| 2286–2330 |   Structured output — scoped by call type |
| 2331–2394 |  22. Prompts |
| 2357–2377 |   The memory hierarchy paragraph is mandatory |
| 2378–2394 |   Anti-hallucination guards are mandatory |
| 2395–3173 | Part V — Knowledge and Retrieval |
| 2399–2754 |  23. The three indexes |
| 2411–2461 |   23.1 `improve_knowledge_index` — methodology |
| 2462–2587 |   23.2 `improve_evidence_index` — Belt-uploaded evidence |
| 2507–2531 |    Supersession deletes; it does not flag |
| 2532–2587 |    Two Azure behaviours govern the migration |
| 2588–2660 |   23.2.1 The `role` vocabulary — ratified, not invented per phase |
| 2627–2660 |    `unclassified (pre-ask-binding)` is a MIGRATION SENTINEL, not a thirteenth role |
| 2661–2709 |   23.3 `improve_case_index` — case records (cross-case memory) |
| 2710–2720 |   The internal phase key is `analyse`, never `analyse_phase` |
| 2721–2745 |   23.4 The write-path trap that made `phase_relevance` unfilterable |
| 2746–2754 |   23.5 Schema change procedure |
| 2755–2883 |  24. The three `rag_lookup_*` tools |
| 2773–2830 |   `rag_lookup_evidence` returns a structured record, not rendered text |
| 2831–2843 |   RAG via tool, never via prepended system message |
| 2844–2868 |   The retrieval mechanism |
| 2869–2876 |   `belt_level` filtering is OFF by default |
| 2877–2883 |   `source_file` and `page_number` are returned, never filtered |
| 2884–2949 |  25. Multi-query and Reciprocal Rank Fusion |
| 2893–2909 |   Why it is mandatory |
| 2910–2916 |   The implementation |
| 2917–2938 |   `MultiQueryRetriever` and `EnsembleRetriever` are BANNED |
| 2939–2949 |   Encapsulation |
| 2950–3083 |  26. Multi-hop retrieval |
| 2965–3001 |   The hop cap is `RemainingSteps` |
| 3002–3020 |   Per-phase policy |
| 3021–3065 |   Planned multi-hop — the Analyse pipeline |
| 3066–3083 |   **UNVERIFIED** — planned multi-hop is Analyse-only |
| 3084–3130 |  27. Retrieval failure semantics |
| 3095–3103 |   Never wrap a retrieval call in a bare `except Exception` returning `[]` |
| 3104–3113 |   Three rules that each have already bitten |
| 3114–3130 |   The coach-facing message must not read as absence |
| 3131–3173 |  28. Memory taxonomy |
| 3149–3173 |   The static/dynamic split is the part that matters |
| 3174–3520 | Part VI — Tools |
| 3178–3335 |  29. The data channel and the universal eight |
| 3184–3219 |   29.1 There is no MCP — the data-channel decision |
| 3220–3262 |   29.2 The universal eight |
| 3228–3262 |    `load_evidence_series` joins the set — RATIFIED 2026-09-09 |
| 3263–3272 |   29.3 `record_field` is RETIRED and may not be reintroduced |
| 3273–3335 |   29.4 Cross-agent tools — a third category, present but NOT BOUND |
| 3336–3410 |  30. Computation tools and per-phase binding |
| 3341–3378 |   Tool sets are per phase, not universal |
| 3379–3384 |   Each of the 20 is a separate named tool |
| 3385–3393 |   All 20 are pure functions |
| 3394–3403 |   `imr_chart_limits` — the choice that is usually wrong by default |
| 3404–3410 |   Tool decisions are the model's, not the graph's |
| 3411–3443 |  31. Tool arg schemas and docstrings |
| 3417–3422 |   Every `@tool` uses `args_schema=` |
| 3423–3443 |   Docstrings are interface, not commentary |
| 3444–3520 |  32. Phase skills — SKILL.md |
| 3467–3471 |   Each skill's `allowed-tools` MUST match that phase's subset in §30 |
| 3472–3481 |   Progressive disclosure — three levels |
| 3482–3487 |   Storage backend: `FilesystemBackend` |
| 3488–3509 |   Each SKILL.md must carry |
| 3510–3520 |   Two distinct kinds of skill exist in this repository |
| 3521–4101 | Part VII — Validation and Gates |
| 3528–3648 |  33. The nine-step HITL gate |
| 3549–3562 |   Two quality checks, two actors, two moments |
| 3563–3574 |   Gates are one-way doors, with exactly one defined exception |
| 3575–3579 |   Implementation: graph-level `interrupt()` |
| 3580–3610 |   33.1 The two-node split |
| 3611–3640 |   33.2 `gate_apply_node` writes the gate document TWICE |
| 3641–3648 |   33.3 The checkpoint commits only after Belt approval |
| 3649–3752 |  34. The four-layer validation stack |
| 3664–3671 |   Layer 2a is middleware; layers 2b–2d are the node |
| 3672–3678 |   Layer 2d is NOT `DMAICGraderMiddleware` |
| 3679–3684 |   Run cheapest first |
| 3685–3694 |   The counter and the feedback |
| 3695–3704 |   Layer 2b is the only deterministic layer, deliberately |
| 3705–3716 |   Per-phase constraint sets |
| 3717–3726 |   34.1 Where each check fires |
| 3727–3752 |   34.2 The self-healing hierarchy and the transparency principle |
| 3753–3888 |  35. Two tiers of field, and the `warning` verdict |
| 3759–3773 |   The problem this solves |
| 3774–3790 |   Three distinct things check these fields, and conflating them is a design error |
| 3791–3839 |   Gate-required fields by phase |
| 3840–3856 |   The grader's verdict has three statuses |
| 3857–3864 |   Why two tiers |
| 3865–3888 |   The grader is belt-level aware |
| 3889–3982 |  36. Two graders — and why they are not redundant |
| 3908–3921 |   Why both exist |
| 3922–3945 |   `COACHING_QUALITY_RUBRIC` |
| 3946–3955 |   Mechanism, both graders |
| 3956–3965 |   Three criteria are verified deterministically, not by judgment |
| 3966–3982 |   The ratified rubric coverage |
| 3983–4079 |  37. Mid-phase contradiction and the re-approval cascade |
| 3989–4010 |   The check runs every turn, not only at gates |
| 4011–4044 |   §37 governs a GATE-COMMITTED value only |
| 4045–4058 |   There is NO tolerance threshold, and none may be added |
| 4059–4066 |   The re-approval cascade |
| 4067–4079 |   The cascade has a hard dependency on compensating actions |
| 4080–4101 |  38. Escalation |
| 4102–5682 | Part VIII — The DMAIC Domain |
| 4109–5303 |  39. The five phases |
| 4127–4141 |   The measurement thread that runs across three phases |
| 4142–4376 |   39.1 Define phase, complete specification |
| 4149–4156 |    39.1.1 Purpose |
| 4157–4219 |    39.1.2 The ordered field list — the `field_index` sequence (closes G-38) |
| 4220–4234 |    39.1.3 The composed-problem-statement rule (binding) |
| 4235–4249 |    39.1.4 The `team` structure |
| 4250–4259 |    39.1.5 SIPOC handling |
| 4260–4271 |    39.1.6 Gate, storage, progress view |
| 4272–4290 |    39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4291–4297 |    39.1.8 The other four phases |
| 4298–4330 |    39.1.9 The metric registry and Define's placeholder |
| 4331–4338 |    39.1.10 Tools bound to Define |
| 4339–4346 |    39.1.11 Conditions — routing and the gate |
| 4347–4354 |    39.1.12 State parameters — Define's use of `PhaseState` |
| 4355–4362 |    39.1.13 Metric literacy — what each metric means |
| 4363–4376 |    39.1.14 Cross-phase reads and writes |
| 4377–4632 |   39.2 Measure phase, complete specification |
| 4387–4395 |    39.2.1 Purpose |
| 4396–4418 |    39.2.2 The ordered field list — the `field_index` sequence |
| 4419–4479 |    39.2.3 The metric registry and Measure's placeholder |
| 4480–4499 |    39.2.4 SIPOC → the detailed process map |
| 4500–4521 |    39.2.5 Tools bound to Measure |
| 4522–4551 |    39.2.6 Conditions — sequence locks, routing, and the gate |
| 4552–4569 |    39.2.7 State parameters — Measure's use of `PhaseState` |
| 4570–4586 |    39.2.8 Metric literacy — what each metric means |
| 4587–4600 |    39.2.9 Gate, storage, progress view |
| 4601–4609 |    39.2.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4610–4626 |    39.2.11 Cross-phase reads and writes |
| 4627–4632 |    39.2.12 The other two phases |
| 4633–4862 |   39.3 Analyse phase, complete specification |
| 4643–4652 |    39.3.1 Purpose |
| 4653–4678 |    39.3.2 The ordered field list — the `field_index` sequence |
| 4679–4715 |    39.3.3 The metric registry and Analyse's placeholder (linkage form — closes F-13) |
| 4716–4735 |    39.3.4 Two movements — generate, then validate |
| 4736–4758 |    39.3.5 Tools bound to Analyse |
| 4759–4787 |    39.3.6 Conditions — methodology guards, routing, and the gate |
| 4788–4801 |    39.3.7 State parameters — Analyse's use of `PhaseState` |
| 4802–4817 |    39.3.8 Metric literacy — what each metric and statistic means |
| 4818–4829 |    39.3.9 Gate, storage, progress view |
| 4830–4838 |    39.3.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4839–4856 |    39.3.11 Cross-phase reads and writes |
| 4857–4862 |    39.3.12 The other phase |
| 4863–5065 |   39.4 Improve phase, complete specification |
| 4873–4881 |    39.4.1 Purpose |
| 4882–4902 |    39.4.2 The ordered field list — the `field_index` sequence |
| 4903–4921 |    39.4.3 The metric registry and Improve's placeholder (linkage form) |
| 4922–4939 |    39.4.4 Two movements — generate-and-select, then pilot-and-prove |
| 4940–4958 |    39.4.5 Tools bound to Improve |
| 4959–4990 |    39.4.6 Conditions — methodology guards, DOE belt-gating, routing, gate |
| 4991–5004 |    39.4.7 State parameters — Improve's use of `PhaseState` |
| 5005–5018 |    39.4.8 Metric literacy — what each metric and statistic means |
| 5019–5030 |    39.4.9 Gate, storage, progress view |
| 5031–5040 |    39.4.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5041–5057 |    39.4.11 Cross-phase reads and writes |
| 5058–5065 |    39.4.12 The last phase |
| 5066–5303 |   39.5 Control phase, complete specification |
| 5076–5084 |    39.5.1 Purpose |
| 5085–5113 |    39.5.2 The ordered field list — the `field_index` sequence |
| 5114–5143 |    39.5.3 The metric registry, the comparison, and single authority (closes F-14) |
| 5144–5160 |    39.5.4 Two movements — confirm it held, then lock it in |
| 5161–5180 |    39.5.5 Tools bound to Control |
| 5181–5213 |    39.5.6 Conditions — guards, routing, gate |
| 5214–5227 |    39.5.7 State parameters — Control's use of `PhaseState` |
| 5228–5242 |    39.5.8 Metric literacy — what each metric and statistic means |
| 5243–5256 |    39.5.9 Gate, storage, progress view |
| 5257–5267 |    39.5.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5268–5283 |    39.5.11 Cross-phase reads and writes — the thread closes here |
| 5284–5303 |    39.5.12 The measurement thread, closed |
| 5304–5399 |  40. The five `{Phase}Output` schemas |
| 5327–5345 |   Field counts |
| 5346–5357 |   The four gate-metadata fields |
| 5358–5371 |   Three fields are on all five schemas |
| 5372–5399 |   40.1 Gate assembly |
| 5400–5483 |  41. Structured dict fields, and FMEA |
| 5422–5433 |   The grader checks every sub-field is populated |
| 5434–5442 |   `control_plan` is `dict`, never `str` |
| 5443–5451 |   `stability_assessment` is checked BEFORE capability |
| 5452–5463 |   `experiment_justification` is Tier 1 and does not require an experiment |
| 5464–5483 |   FMEA has no field in any schema, and none may be added |
| 5484–5515 |  42. Cross-phase reference fields in practice |
| 5516–5682 |  43. The coaching method |
| 5534–5561 |   43.1 The seven-step computation pattern |
| 5562–5599 |   43.2 Show before asking |
| 5600–5622 |   43.3 The A→F session flow |
| 5623–5654 |   43.4 The live gate document preview |
| 5655–5664 |   43.5 No external URLs |
| 5665–5682 |   43.6 What the coach must not do |
| 5683–6039 | Part IX — Reliability |
| 5687–5715 |   43.7 Metric literacy — the metric, and the statistic |
| 5716–5744 |  44. The failure pipeline |
| 5745–5857 |  45. Timeouts and compensating actions |
| 5752–5783 |   Per-node timeouts — required on every phase executor node |
| 5784–5793 |   Composition order — retries run BEFORE the handler |
| 5794–5803 |   Node-level error handlers — required on every node with external writes |
| 5804–5809 |   Hand-written Saga orchestrators are BANNED |
| 5810–5818 |   Two dependencies on this rule, both correctness-critical |
| 5819–5850 |   Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST** |
| 5851–5857 |   `DeltaChannel` is NOT used |
| 5858–5973 |  46. The fallback chain and circuit breakers |
| 5864–5876 |   The v2.1 four-level chain |
| 5877–5883 |   Backoff strategy is chosen per level, not globally |
| 5884–5902 |   Level 3 cache |
| 5903–5918 |   Circuit breakers — three-state, two instances |
| 5919–5925 |   Degraded mode uses actual state, never a generic error |
| 5926–5933 |   HTTP 400 is NOT a fallback case |
| 5934–5973 |   46.1 Geographic redundancy — **DEFERRED** |
| 5974–6014 |  47. Disconnect policy — what a dropped client commits |
| 5991–5997 |   Ratified policy: ABANDON, not COMPLETE |
| 5998–6014 |   Five requirements |
| 6015–6039 |  48. Structured errors |
| 6040–6527 | Part X — Operations |
| 6044–6097 |  49. API surface |
| 6050–6059 |   One runtime |
| 6060–6067 |   Async by default |
| 6068–6091 |   Endpoints |
| 6092–6097 |   Envelopes are Pydantic v2 |
| 6098–6254 |  50. UI and language rules |
| 6105–6143 |   50.1 Coach response structure |
| 6144–6155 |   Plain language always |
| 6156–6163 |   Citations |
| 6164–6177 |   Contextual feedback |
| 6178–6184 |   Connection status before the first interaction |
| 6185–6190 |   The gate review screen |
| 6191–6229 |   The live gate document |
| 6230–6241 |   The all-gate-fields tab is the contradiction backstop |
| 6242–6254 |   The conflict resolution panel |
| 6255–6330 |  51. Tracing and observability |
| 6261–6271 |   LangSmith is mandatory |
| 6272–6304 |   `@traceable` on every custom function |
| 6305–6310 |   What gets traced |
| 6311–6318 |   P50/P99 latency is a coaching quality signal |
| 6319–6330 |   Logs |
| 6331–6385 |  52. Evaluation and regression testing |
| 6337–6344 |   Built alongside the refactor, not before it |
| 6345–6351 |   The dataset is authored jointly, not generated |
| 6352–6365 |   Minimum viable suite |
| 6366–6376 |   Rubrics and the eval dataset are complementary, not duplicative |
| 6377–6385 |   Two open validation questions this suite answers |
| 6386–6527 |  53. Configuration, dependencies and deployment |
| 6392–6408 |   Fail-fast environment validation |
| 6409–6432 |   Dependency floor |
| 6433–6443 |   `/verify-current-version` is a mandatory checkpoint |
| 6444–6451 |   Infrastructure not yet provisioned |
| 6452–6463 |   Deployment layer: FastAPI, not LangGraph Server |
| 6464–6527 |   53.1 Migration sequence |
| 6528–7096 | Part XI — Governance |
| 6532–6574 |  54. Where code is allowed to live |
| 6539–6556 |   Classes are permitted ONLY in these files |
| 6557–6574 |   Target folder structure |
| 6575–6945 |  55. Anti-drift |
| 6589–6603 |   Rule numbers are load-bearing |
| 6604–6614 |   The registry guards code, not documentation |
| 6615–6620 |   Verification discipline |
| 6621–6643 |   Reference sweeps must use raw `grep -rn`, never a gitignore-filtered tool |
| 6644–6694 |   55.1 Spec-layer governance rules |
| 6695–6777 |   55.2 The BUILT markers, and the paths that oblige a re-check |
| 6778–6858 |   55.3 The phase completeness set — what one phase actually traverses |
| 6859–6908 |   55.4 Facts have one owner — the ratified minimum |
| 6909–6945 |   55.5 The commit gates govern. The rule files are advisory context. |
| 6946–7096 |  56. Amendment procedure |
| 6973–7016 |   56.0 What changed about amending, when the rules stopped being one file |
| 7017–7035 |   56.0.1 Rule, reference, and owned fact — three destinations |
| 7036–7078 |   56.1 A phase is one atomic unit — schema, validator, skill |
| 7079–7096 |   What requires an amendment rather than a routine change |
| 7097–11441 | Part XII — Specification |
| 7107–7130 |   56.2 The rule lands here; the reasoning lands in the commit |
| 7131–7164 |   56.3 The tree at HEAD is the only source of truth |
| 7165–7426 |  57. The specification layer — how to read and write a spec entry |
| 7172–7192 |   Why this Part exists |
| 7193–7208 |   The five structural rules |
| 7209–7223 |   Entry identity and traceability |
| 7224–7271 |   The entry template — three layers |
| 7272–7283 |   How gaps are marked |
| 7284–7300 |   57.1 The two calibrated samples |
| 7301–7354 |   57.2 SAMPLE 1 — CLASS TEMPLATE — S-C01 `SupervisorState` |
| 7304–7354 |    SPEC — `SupervisorState` |
| 7355–7405 |   57.3 SAMPLE 2 — FUNCTION/NODE TEMPLATE — S-F04 `phase_executor` (the coach node) |
| 7359–7405 |    SPEC — `phase_executor` (the coach node) |
| 7406–7426 |   57.4 Entry index |
| 7427–8756 |  58. Spec — graph management |
| 7437–7440 |   58.1 S-C01 · `SupervisorState` |
| 7441–7606 |   58.2 S-C02 · `PhaseState` |
| 7607–7625 |   58.3 S-C03 · Per-phase use of `PhaseState` |
| 7626–7701 |   58.4 S-C04 · `CoachingPlan` |
| 7702–7811 |   58.5 S-C05 · `CoachingResponse` |
| 7812–7863 |   58.6 S-C06 · `AzureBlobStore` |
| 7864–7909 |   58.7 S-C07 · `AzureBlobCheckpointSaver` |
| 7910–7956 |   58.8 S-C08 · `ImproveBlobClient` |
| 7957–8019 |   58.9 S-C09 · `storage/models.py` — the record models |
| 8020–8083 |   58.10 S-F01 · The supervisor graph — static edges |
| 8054–8063 |    SIPOC — at a glance |
| 8064–8083 |    Behaviors (EARS) |
| 8084–8129 |   58.11 S-F02 · `build_phase_subgraph(phase, llm)` |
| 8102–8111 |    SIPOC — at a glance |
| 8112–8129 |    Behaviors (EARS) |
| 8130–8170 |   58.12 S-F03 · `phase_planner` node |
| 8141–8150 |    SIPOC — at a glance |
| 8151–8170 |    Behaviors (EARS) |
| 8171–8182 |   58.13 S-F04 · `phase_executor` node |
| 8183–8244 |   58.14 S-F05 · `validation_stack` node |
| 8193–8202 |    SIPOC — at a glance |
| 8203–8214 |    Behaviors (EARS) |
| 8215–8244 |    ⚠ AI-ACT — high-risk surface |
| 8245–8296 |   58.15 S-F06 · `gate_review_node` |
| 8255–8264 |    SIPOC — at a glance |
| 8265–8272 |    Behaviors (EARS) |
| 8273–8296 |    ⚠ AI-ACT — high-risk surface |
| 8297–8364 |   58.16 S-F07 · `gate_apply_node` |
| 8318–8327 |    SIPOC — at a glance |
| 8328–8340 |    Behaviors (EARS) |
| 8341–8364 |    ⚠ AI-ACT — high-risk surface |
| 8365–8400 |   58.17 S-F08 · The escalation subgraph |
| 8373–8382 |    SIPOC — at a glance |
| 8383–8400 |    Behaviors (EARS) |
| 8401–8469 |   58.18 S-F09 · `analyse_executor_node` |
| 8441–8450 |    SIPOC — at a glance |
| 8451–8469 |    Behaviors (EARS) |
| 8470–8563 |   58.19 S-F10 · `define_input_mapper` |
| 8513–8525 |    SIPOC — at a glance |
| 8526–8554 |    Execution site — where a boundary mapper actually runs |
| 8555–8563 |    Behaviors (EARS) |
| 8564–8617 |   58.20 S-F11 · `define_output_mapper` |
| 8593–8602 |    SIPOC — at a glance |
| 8603–8617 |    Behaviors (EARS) |
| 8618–8667 |   58.21 S-F12 · The Measure, Analyse, Improve and Control mapper pairs |
| 8626–8635 |    SIPOC — at a glance |
| 8636–8667 |    Behaviors (EARS) |
| 8668–8756 |   58.22 S-F13 · Level 2 `Command` routing |
| 8685–8702 |    DP1 — the planner owns the field / gate decision |
| 8703–8723 |    DP2 — the validation stack's three exits |
| 8724–8744 |    DP3 — the gate exits |
| 8745–8756 |    What is settled and binds |
| 8757–9139 |  59. Spec — knowledge and retrieval |
| 8770–8799 |   59.1 S-C16 · `Hop` |
| 8800–8846 |   59.2 S-C17 · `Plan` — the hop decomposition plan |
| 8847–8883 |   59.3 S-C18 · `SynthesisOutput` |
| 8884–8900 |   59.4 S-C19 · `QueryVariants` |
| 8901–8947 |   59.5 S-F14 · `rag_lookup_methodology` |
| 8922–8931 |    SIPOC — at a glance |
| 8932–8947 |    Behaviors (EARS) |
| 8948–8995 |   59.6 S-F15 · `rag_lookup_evidence` |
| 8971–8980 |    SIPOC — at a glance |
| 8981–8995 |    Behaviors (EARS) |
| 8996–9042 |   59.7 S-F16 · `rag_lookup_case_history` |
| 9019–9028 |    SIPOC — at a glance |
| 9029–9042 |    Behaviors (EARS) |
| 9043–9093 |   59.8 S-F17 · `reciprocal_rank_fusion` |
| 9070–9079 |    SIPOC — at a glance |
| 9080–9093 |    Behaviors (EARS) |
| 9094–9139 |   59.9 S-F18 · The retriever layer — `search_knowledge`, `search_cases`, `search_evidence` |
| 9122–9139 |    SIPOC — at a glance |
| 9140–9425 |  60. Spec — tools |
| 9158–9191 |   60.1 S-F19 · `propose_template` |
| 9171–9191 |    SIPOC — at a glance |
| 9192–9230 |   60.2 S-F20 · `propose_diagram` |
| 9207–9216 |    SIPOC — at a glance |
| 9217–9230 |    Behaviors (EARS) |
| 9231–9272 |   60.3 S-F21 · `check_gate_status` |
| 9246–9255 |    SIPOC — at a glance |
| 9256–9272 |    Behaviors (EARS) |
| 9273–9308 |   60.4 S-F22 · `request_human_approval` |
| 9287–9308 |    SIPOC — at a glance |
| 9309–9325 |   60.5 S-F23 · `load_skill(name)` |
| 9326–9370 |   60.6 S-F24 · The 20 computation tools |
| 9349–9370 |    Behaviors (EARS) — binding on all twenty |
| 9371–9425 |   60.7 S-F57 · `load_evidence_series(blob_path, column)` |
| 9396–9405 |    SIPOC — at a glance |
| 9406–9425 |    Behaviors (EARS) |
| 9426–9678 |  61. Spec — the coaching agent's middleware |
| 9444–9506 |   61.1 S-C10 · `ContradictionDetectionMiddleware` |
| 9466–9475 |    Behaviors (EARS) |
| 9476–9506 |    ⚠ AI-ACT — high-risk surface |
| 9507–9548 |   61.2 S-C11 · `BeforeModelStateInjection` |
| 9520–9548 |    Behaviors (EARS) |
| 9549–9588 |   61.3 S-C12 · `DMAICSkillsMiddleware` |
| 9569–9588 |    Behaviors (EARS) |
| 9589–9625 |   61.4 S-C13 · `CoherenceMiddleware` |
| 9603–9625 |    Behaviors (EARS) |
| 9626–9661 |   61.5 S-C14 · `DMAICGraderMiddleware` |
| 9636–9661 |    Behaviors (EARS) |
| 9662–9678 |   61.6 S-C15 · `HITLInterrupt` |
| 9679–10086 |  62. Spec — validation and gates |
| 9693–9735 |   62.1 S-C20 · `CriterionVerdict` |
| 9736–9753 |   62.2 S-C21 · `GraderVerdict` |
| 9754–9767 |   62.3 S-C22 · `CoachingGraderVerdict` |
| 9768–9779 |   62.4 S-C23 · `CoherenceResult` |
| 9780–9794 |   62.5 S-C24 · `ConstraintCheckResult` / `ConstraintVerdict` |
| 9795–9807 |   62.6 S-C25 · `PolicyAdvisoryResult` |
| 9808–9844 |   62.7 S-C26 · `DMAICGateValidator` |
| 9845–9879 |   62.8 S-F25 · Layer 2c — the constraint check |
| 9854–9863 |    SIPOC — at a glance |
| 9864–9879 |    Behaviors (EARS) |
| 9880–9927 |   62.9 S-F26 · Layer 2d — the gate grader |
| 9895–9904 |    SIPOC — at a glance |
| 9905–9927 |    Behaviors (EARS) |
| 9928–9969 |   62.10 S-F27 · The policy advisory |
| 9943–9952 |    SIPOC — at a glance |
| 9953–9969 |    Behaviors (EARS) |
| 9970–10086 |   62.11 S-F28 · Gate document assembly |
| 10058–10067 |    SIPOC — at a glance |
| 10068–10086 |    Behaviors (EARS) |
| 10087–10608 |  63. Spec — the DMAIC gate documents |
| 10105–10173 |   63.1 S-C27 · `DefineOutput` |
| 10174–10214 |   63.2 S-C28 · `MeasureOutput` |
| 10215–10272 |   63.3 S-C29 · `AnalyseOutput` |
| 10273–10332 |   63.4 S-C30 · `ImproveOutput` |
| 10333–10404 |   63.5 S-C31 · `ControlOutput` |
| 10405–10471 |   63.6 S-C32 · The three cross-phase reference dicts |
| 10472–10513 |   63.7 S-C33 · The three structured dict fields |
| 10514–10552 |   63.8 S-C38 · `metric_definitions` — the project metric registry |
| 10553–10608 |   63.9 S-C39 · `phase_metrics` — the per-phase placeholder |
| 10609–10897 |  64. Spec — reliability |
| 10620–10660 |   64.1 S-C34 · `AgentImproveError` |
| 10661–10699 |   64.2 S-C35 · `CircuitBreaker` |
| 10700–10786 |   64.3 S-F29 · `phase_error_recovery` |
| 10728–10737 |    SIPOC — at a glance |
| 10738–10786 |    Behaviors (EARS) |
| 10787–10835 |   64.4 S-F30 · `degraded_mode_response` |
| 10808–10817 |    SIPOC — at a glance |
| 10818–10835 |    Behaviors (EARS) |
| 10836–10854 |   64.5 S-F31 · `synthesise_partial` |
| 10855–10879 |   64.6 S-F32 · `delete_or_flag_stale_in_case_index` |
| 10880–10897 |   64.7 S-F33 · `degraded_coaching_response` node |
| 10898–11074 |  65. Spec — API, UI and evidence |
| 10908–10928 |   65.1 S-C36 · `CitationRecord` and `CitationBundle` |
| 10929–10946 |   65.2 S-C37 · The API envelopes |
| 10947–10999 |   65.3 S-F34 · The API surface |
| 10969–10978 |    SIPOC — at a glance |
| 10979–10999 |    Behaviors (EARS) |
| 11000–11039 |   65.4 S-F35 · The upload handler |
| 11025–11039 |    Behaviors (EARS) |
| 11040–11074 |   65.5 S-F36 · The `improve_case_index` write path |
| 11075–11085 |  66. The SPEC-GAP register — MOVED |
| 11086–11179 |  67. EU AI Act compliance posture |
| 11093–11108 |   67.1 The deadlines are now fixed |
| 11109–11134 |   67.2 The classification question — open, and not answered here |
| 11135–11152 |   67.3 The eight core provider obligations |
| 11153–11163 |   67.4 One compliance finding is already recorded in this document |
| 11164–11179 |   67.5 Compliance-source discipline |
| 11180–11260 |  68. The DORA-structured compliance risk register |
| 11187–11204 |   68.1 Why DORA structure |
| 11205–11221 |   68.2 The register |
| 11222–11245 |   68.3 Pending classification — not register rows |
| 11246–11260 |   68.4 The infrastructure risk already on record |
| 11261–11441 |  69. Spec — computation tools |
| 11290–11361 |   69.1 Common conventions — stated once, binding on all twenty |
| 11362–11367 |   69.2 S-F37 · Define — 1 tool |
| 11368–11380 |   69.3 S-F38–S-F45 · Measure — 8 tools |
| 11381–11390 |   69.4 S-F46–S-F50 · Analyse — 5 tools |
| 11391–11396 |   69.5 S-F51 · Improve — 1 tool |
| 11397–11414 |   69.6 S-F52–S-F56 · Control — 5 tools |
| 11415–11441 |   69.7 The Measure control-chart boundary — a tool that is deliberately absent |
| 11442–11671 | Appendices |
| 11446–11461 |  Appendix A — Provenance index |
| 11452–11455 |   A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference |
| 11456–11461 |   A.2 `agent-improve/ARCHITECTURE.md` → this reference |
| 11462–11492 |  Appendix B — Deferred backlog |
| 11493–11558 |  Appendix C — Trusted sources |
| 11499–11518 |   Tier 1 — current, authoritative |
| 11519–11537 |   Tier 1 — compliance |
| 11538–11541 |   Tier 2 — official announcements |
| 11542–11545 |   Tier 3 — informed practitioner, cross-check before citing |
| 11546–11552 |   Downgraded — historical |
| 11553–11558 |   Excluded |
| 11559–11639 |  Appendix D — Retired names, banned patterns, and exclusions |
| 11561–11584 |   D.1 Retired names — never reintroduce |
| 11585–11628 |   D.2 Banned patterns |
| 11629–11639 |   D.3 Architecturally excluded — not deferred |
| 11640–11648 |  Appendix E — Current state |
| 11649–11671 |  Appendix F — The v2.2.16 registers |
| 11655–11660 |   F.1 Decisions Resolved (v2.2) — the former §17 |
| 11661–11671 |   F.2 Change Log — the former §18 |
| 11665–11671 |    F.2.1 Amendment procedure — the former §18.1 |
