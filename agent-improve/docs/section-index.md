# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 11665 lines

| Lines | Heading |
|---|---|
| 27–49 |  🗺 Where state lives — a MAP, not a definition |
| 50–256 | Agentic Architecture Reference |
| 151–256 |  About this document |
| 157–214 |   Scope — three agents, one architecture |
| 215–229 |   The two-document division |
| 230–244 |   Section numbering and provenance |
| 245–256 |   Reading conventions |
| 257–548 | Part I — Orientation |
| 261–337 |  1. What Agent Improve is |
| 281–307 |   What makes it architecturally distinctive |
| 308–337 |   The runtime stack |
| 338–389 |  2. How to read this document |
| 344–360 |   By what you are trying to do |
| 361–389 |   Canonical ownership |
| 390–488 |  3. Terminology |
| 401–417 |   Structural primitives |
| 418–429 |   Role labels |
| 430–447 |   The recursion is two levels, not infinite |
| 448–462 |   "Harness" — two senses, do not conflate |
| 463–473 |   "Agent" — used carefully |
| 474–488 |   Things that are deliberately not levels |
| 489–548 |  4. Architecture at a glance |
| 532–548 |   The five things that shape everything else |
| 549–1276 | Part II — State and Persistence |
| 556–614 |  5. `SupervisorState` — orchestration only |
| 568–574 |   `gate_passed` is a dict, not a list |
| 575–586 |   `current_phase` and `phase_index` are derived, and kept anyway |
| 587–606 |   Four fields were removed as redundant, and may not return |
| 607–614 |   Artifacts are not here |
| 615–850 |  6. `PhaseState` — per-phase subgraph state |
| 630–661 |   `asks` — §56 AMENDMENT, ratified 2026-09-09 |
| 662–731 |   `field_log` — §56 AMENDMENT, ratified 2026-09-21 |
| 732–737 |   `draft`, `belt_edits` and `final` are `dict`, never `str` |
| 738–760 |   `coaching_plan` is one typed plan, not a queue |
| 761–776 |   `gate_attempts` — the field whose absence recreated a production bug |
| 777–797 |   `validator_feedback` and `belt_edits` are different, and must stay separate |
| 798–815 |   `citations` and `uploads` — the evidence trail |
| 816–833 |   `hop_results` and `synthesis_output` must be state, not node locals |
| 834–842 |   Per-phase variants |
| 843–850 |   Naming discipline |
| 851–927 |  7. Field typing law — every captured field is a string |
| 867–879 |   Why strings |
| 880–899 |   The one exception — three cross-phase reference dicts |
| 900–927 |   Computation results |
| 928–1020 |  8. The checkpointer / store split |
| 952–971 |   Phased backend |
| 972–983 |   Concurrency and atomicity |
| 984–999 |   Why Blob, and not Cosmos / Tables / SQLite |
| 1000–1020 |   On-blob checkpoint format |
| 1021–1157 |  9. The Store — cross-phase artifacts and boundary mappers |
| 1062–1085 |   Namespace convention |
| 1086–1115 |   Why cross-phase data cannot travel on parent state |
| 1116–1136 |   Boundary mappers |
| 1137–1149 |   Two prohibitions that follow |
| 1150–1157 |   Ordering constraint |
| 1158–1215 |  10. Azure Blob — two distinct concerns |
| 1177–1202 |   Complete physical layout |
| 1203–1215 |   The case blob is not updated per turn |
| 1216–1276 |  11. `step_log` — the audit trail |
| 1237–1246 |   `artifacts` and `step_log` are separate fields and stay separate |
| 1247–1276 |   Entries carry deterministic keys, never a raw timestamp as identity |
| 1277–1647 | Part III — The Graph |
| 1283–1323 |  12. Topology |
| 1313–1323 |   The subgraph builder takes the phase as a parameter |
| 1324–1463 |  13. The phase subgraph — five nodes |
| 1401–1431 |   The subgraph is a cycle, not a pipeline |
| 1432–1444 |   Two node names are BANNED |
| 1445–1450 |   Leaf tools are NOT subgraph nodes |
| 1451–1463 |   The validation stack and the policy advisory are NOT tools |
| 1464–1499 |  14. Node contract |
| 1487–1499 |   Reflection is a node, not a private function |
| 1500–1564 |  15. Routing — static edges and `Command` |
| 1506–1523 |   The decision test |
| 1524–1529 |   Never mix static edges and `Command` from the same node |
| 1530–1557 |   Level 1 does not route — it advances |
| 1558–1564 |   No subgraph imports another subgraph's nodes |
| 1565–1647 |  16. `thread_id`, `checkpoint_ns`, and where persistence attaches |
| 1571–1586 |   One `thread_id` per project |
| 1587–1600 |   The checkpointer and store go on the parent graph ONLY |
| 1601–1627 |   The wrapper node must invoke the subgraph directly (G-44) |
| 1628–1647 |   `recursion_limit` is a backstop, not the hop cap |
| 1648–2389 | Part IV — The Coaching Agent |
| 1654–1768 |  17. The Planner / Executor contract |
| 1730–1760 |   `CoachingPlan` |
| 1761–1768 |   Extraction is structured output, not a node and not a tool |
| 1769–1816 |  18. Building the executor — `create_agent` |
| 1781–1788 |   Binding tools directly onto a bare model is a violation |
| 1789–1794 |   `create_react_agent` is superseded |
| 1795–1807 |   deepagents is not a dependency |
| 1808–1816 |   The structured response and the coaching text coexist |
| 1817–2138 |  19. The middleware stack — eight, in order |
| 1839–1885 |   Ordering rules that bind |
| 1886–1897 |   Three independent retry caps |
| 1898–1941 |   19.1 `BeforeModelStateInjection` — injection timing |
| 1942–1957 |   19.2 `DMAICSkillsMiddleware` — progressive disclosure |
| 1958–1997 |   19.3 `SummarizationMiddleware` — context compression |
| 1998–2024 |   19.4 `ModelRetryMiddleware` — API-level retry |
| 2025–2037 |   19.5 `ToolRetryMiddleware` — tool-level retry |
| 2038–2060 |   19.6 `ContradictionDetectionMiddleware` — the mid-phase check |
| 2061–2095 |   19.7 `CoherenceMiddleware` — validation Layer 2a |
| 2096–2126 |   19.8 `DMAICGraderMiddleware` — coaching process quality |
| 2127–2138 |   19.9 Middleware deliberately NOT used |
| 2139–2213 |  20. `CoachingResponse` — the per-turn schema |
| 2193–2196 |   The executor node writes the response into state |
| 2197–2203 |   The executor's `response_format` is `CoachingResponse`, never a phase Output |
| 2204–2213 |   What structured output does NOT give you |
| 2214–2325 |  21. LLM roles, temperature, and the factory |
| 2234–2242 |   Factory only |
| 2243–2263 |   Roles |
| 2264–2280 |   Temperature |
| 2281–2325 |   Structured output — scoped by call type |
| 2326–2389 |  22. Prompts |
| 2352–2372 |   The memory hierarchy paragraph is mandatory |
| 2373–2389 |   Anti-hallucination guards are mandatory |
| 2390–3168 | Part V — Knowledge and Retrieval |
| 2394–2749 |  23. The three indexes |
| 2406–2456 |   23.1 `improve_knowledge_index` — methodology |
| 2457–2582 |   23.2 `improve_evidence_index` — Belt-uploaded evidence |
| 2502–2526 |    Supersession deletes; it does not flag |
| 2527–2582 |    Two Azure behaviours govern the migration |
| 2583–2655 |   23.2.1 The `role` vocabulary — ratified, not invented per phase |
| 2622–2655 |    `unclassified (pre-ask-binding)` is a MIGRATION SENTINEL, not a thirteenth role |
| 2656–2704 |   23.3 `improve_case_index` — case records (cross-case memory) |
| 2705–2715 |   The internal phase key is `analyse`, never `analyse_phase` |
| 2716–2740 |   23.4 The write-path trap that made `phase_relevance` unfilterable |
| 2741–2749 |   23.5 Schema change procedure |
| 2750–2878 |  24. The three `rag_lookup_*` tools |
| 2768–2825 |   `rag_lookup_evidence` returns a structured record, not rendered text |
| 2826–2838 |   RAG via tool, never via prepended system message |
| 2839–2863 |   The retrieval mechanism |
| 2864–2871 |   `belt_level` filtering is OFF by default |
| 2872–2878 |   `source_file` and `page_number` are returned, never filtered |
| 2879–2944 |  25. Multi-query and Reciprocal Rank Fusion |
| 2888–2904 |   Why it is mandatory |
| 2905–2911 |   The implementation |
| 2912–2933 |   `MultiQueryRetriever` and `EnsembleRetriever` are BANNED |
| 2934–2944 |   Encapsulation |
| 2945–3078 |  26. Multi-hop retrieval |
| 2960–2996 |   The hop cap is `RemainingSteps` |
| 2997–3015 |   Per-phase policy |
| 3016–3060 |   Planned multi-hop — the Analyse pipeline |
| 3061–3078 |   **UNVERIFIED** — planned multi-hop is Analyse-only |
| 3079–3125 |  27. Retrieval failure semantics |
| 3090–3098 |   Never wrap a retrieval call in a bare `except Exception` returning `[]` |
| 3099–3108 |   Three rules that each have already bitten |
| 3109–3125 |   The coach-facing message must not read as absence |
| 3126–3168 |  28. Memory taxonomy |
| 3144–3168 |   The static/dynamic split is the part that matters |
| 3169–3515 | Part VI — Tools |
| 3173–3330 |  29. The data channel and the universal eight |
| 3179–3214 |   29.1 There is no MCP — the data-channel decision |
| 3215–3257 |   29.2 The universal eight |
| 3223–3257 |    `load_evidence_series` joins the set — RATIFIED 2026-09-09 |
| 3258–3267 |   29.3 `record_field` is RETIRED and may not be reintroduced |
| 3268–3330 |   29.4 Cross-agent tools — a third category, present but NOT BOUND |
| 3331–3405 |  30. Computation tools and per-phase binding |
| 3336–3373 |   Tool sets are per phase, not universal |
| 3374–3379 |   Each of the 20 is a separate named tool |
| 3380–3388 |   All 20 are pure functions |
| 3389–3398 |   `imr_chart_limits` — the choice that is usually wrong by default |
| 3399–3405 |   Tool decisions are the model's, not the graph's |
| 3406–3438 |  31. Tool arg schemas and docstrings |
| 3412–3417 |   Every `@tool` uses `args_schema=` |
| 3418–3438 |   Docstrings are interface, not commentary |
| 3439–3515 |  32. Phase skills — SKILL.md |
| 3462–3466 |   Each skill's `allowed-tools` MUST match that phase's subset in §30 |
| 3467–3476 |   Progressive disclosure — three levels |
| 3477–3482 |   Storage backend: `FilesystemBackend` |
| 3483–3504 |   Each SKILL.md must carry |
| 3505–3515 |   Two distinct kinds of skill exist in this repository |
| 3516–4096 | Part VII — Validation and Gates |
| 3523–3643 |  33. The nine-step HITL gate |
| 3544–3557 |   Two quality checks, two actors, two moments |
| 3558–3569 |   Gates are one-way doors, with exactly one defined exception |
| 3570–3574 |   Implementation: graph-level `interrupt()` |
| 3575–3605 |   33.1 The two-node split |
| 3606–3635 |   33.2 `gate_apply_node` writes the gate document TWICE |
| 3636–3643 |   33.3 The checkpoint commits only after Belt approval |
| 3644–3747 |  34. The four-layer validation stack |
| 3659–3666 |   Layer 2a is middleware; layers 2b–2d are the node |
| 3667–3673 |   Layer 2d is NOT `DMAICGraderMiddleware` |
| 3674–3679 |   Run cheapest first |
| 3680–3689 |   The counter and the feedback |
| 3690–3699 |   Layer 2b is the only deterministic layer, deliberately |
| 3700–3711 |   Per-phase constraint sets |
| 3712–3721 |   34.1 Where each check fires |
| 3722–3747 |   34.2 The self-healing hierarchy and the transparency principle |
| 3748–3883 |  35. Two tiers of field, and the `warning` verdict |
| 3754–3768 |   The problem this solves |
| 3769–3785 |   Three distinct things check these fields, and conflating them is a design error |
| 3786–3834 |   Gate-required fields by phase |
| 3835–3851 |   The grader's verdict has three statuses |
| 3852–3859 |   Why two tiers |
| 3860–3883 |   The grader is belt-level aware |
| 3884–3977 |  36. Two graders — and why they are not redundant |
| 3903–3916 |   Why both exist |
| 3917–3940 |   `COACHING_QUALITY_RUBRIC` |
| 3941–3950 |   Mechanism, both graders |
| 3951–3960 |   Three criteria are verified deterministically, not by judgment |
| 3961–3977 |   The ratified rubric coverage |
| 3978–4074 |  37. Mid-phase contradiction and the re-approval cascade |
| 3984–4005 |   The check runs every turn, not only at gates |
| 4006–4039 |   §37 governs a GATE-COMMITTED value only |
| 4040–4053 |   There is NO tolerance threshold, and none may be added |
| 4054–4061 |   The re-approval cascade |
| 4062–4074 |   The cascade has a hard dependency on compensating actions |
| 4075–4096 |  38. Escalation |
| 4097–5677 | Part VIII — The DMAIC Domain |
| 4104–5298 |  39. The five phases |
| 4122–4136 |   The measurement thread that runs across three phases |
| 4137–4371 |   39.1 Define phase, complete specification |
| 4144–4151 |    39.1.1 Purpose |
| 4152–4214 |    39.1.2 The ordered field list — the `field_index` sequence (closes G-38) |
| 4215–4229 |    39.1.3 The composed-problem-statement rule (binding) |
| 4230–4244 |    39.1.4 The `team` structure |
| 4245–4254 |    39.1.5 SIPOC handling |
| 4255–4266 |    39.1.6 Gate, storage, progress view |
| 4267–4285 |    39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4286–4292 |    39.1.8 The other four phases |
| 4293–4325 |    39.1.9 The metric registry and Define's placeholder |
| 4326–4333 |    39.1.10 Tools bound to Define |
| 4334–4341 |    39.1.11 Conditions — routing and the gate |
| 4342–4349 |    39.1.12 State parameters — Define's use of `PhaseState` |
| 4350–4357 |    39.1.13 Metric literacy — what each metric means |
| 4358–4371 |    39.1.14 Cross-phase reads and writes |
| 4372–4627 |   39.2 Measure phase, complete specification |
| 4382–4390 |    39.2.1 Purpose |
| 4391–4413 |    39.2.2 The ordered field list — the `field_index` sequence |
| 4414–4474 |    39.2.3 The metric registry and Measure's placeholder |
| 4475–4494 |    39.2.4 SIPOC → the detailed process map |
| 4495–4516 |    39.2.5 Tools bound to Measure |
| 4517–4546 |    39.2.6 Conditions — sequence locks, routing, and the gate |
| 4547–4564 |    39.2.7 State parameters — Measure's use of `PhaseState` |
| 4565–4581 |    39.2.8 Metric literacy — what each metric means |
| 4582–4595 |    39.2.9 Gate, storage, progress view |
| 4596–4604 |    39.2.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4605–4621 |    39.2.11 Cross-phase reads and writes |
| 4622–4627 |    39.2.12 The other two phases |
| 4628–4857 |   39.3 Analyse phase, complete specification |
| 4638–4647 |    39.3.1 Purpose |
| 4648–4673 |    39.3.2 The ordered field list — the `field_index` sequence |
| 4674–4710 |    39.3.3 The metric registry and Analyse's placeholder (linkage form — closes F-13) |
| 4711–4730 |    39.3.4 Two movements — generate, then validate |
| 4731–4753 |    39.3.5 Tools bound to Analyse |
| 4754–4782 |    39.3.6 Conditions — methodology guards, routing, and the gate |
| 4783–4796 |    39.3.7 State parameters — Analyse's use of `PhaseState` |
| 4797–4812 |    39.3.8 Metric literacy — what each metric and statistic means |
| 4813–4824 |    39.3.9 Gate, storage, progress view |
| 4825–4833 |    39.3.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 4834–4851 |    39.3.11 Cross-phase reads and writes |
| 4852–4857 |    39.3.12 The other phase |
| 4858–5060 |   39.4 Improve phase, complete specification |
| 4868–4876 |    39.4.1 Purpose |
| 4877–4897 |    39.4.2 The ordered field list — the `field_index` sequence |
| 4898–4916 |    39.4.3 The metric registry and Improve's placeholder (linkage form) |
| 4917–4934 |    39.4.4 Two movements — generate-and-select, then pilot-and-prove |
| 4935–4953 |    39.4.5 Tools bound to Improve |
| 4954–4985 |    39.4.6 Conditions — methodology guards, DOE belt-gating, routing, gate |
| 4986–4999 |    39.4.7 State parameters — Improve's use of `PhaseState` |
| 5000–5013 |    39.4.8 Metric literacy — what each metric and statistic means |
| 5014–5025 |    39.4.9 Gate, storage, progress view |
| 5026–5035 |    39.4.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5036–5052 |    39.4.11 Cross-phase reads and writes |
| 5053–5060 |    39.4.12 The last phase |
| 5061–5298 |   39.5 Control phase, complete specification |
| 5071–5079 |    39.5.1 Purpose |
| 5080–5108 |    39.5.2 The ordered field list — the `field_index` sequence |
| 5109–5138 |    39.5.3 The metric registry, the comparison, and single authority (closes F-14) |
| 5139–5155 |    39.5.4 Two movements — confirm it held, then lock it in |
| 5156–5175 |    39.5.5 Tools bound to Control |
| 5176–5208 |    39.5.6 Conditions — guards, routing, gate |
| 5209–5222 |    39.5.7 State parameters — Control's use of `PhaseState` |
| 5223–5237 |    39.5.8 Metric literacy — what each metric and statistic means |
| 5238–5251 |    39.5.9 Gate, storage, progress view |
| 5252–5262 |    39.5.10 The SKILL.md content (AUTHORITATIVE during the refactor) |
| 5263–5278 |    39.5.11 Cross-phase reads and writes — the thread closes here |
| 5279–5298 |    39.5.12 The measurement thread, closed |
| 5299–5394 |  40. The five `{Phase}Output` schemas |
| 5322–5340 |   Field counts |
| 5341–5352 |   The four gate-metadata fields |
| 5353–5366 |   Three fields are on all five schemas |
| 5367–5394 |   40.1 Gate assembly |
| 5395–5478 |  41. Structured dict fields, and FMEA |
| 5417–5428 |   The grader checks every sub-field is populated |
| 5429–5437 |   `control_plan` is `dict`, never `str` |
| 5438–5446 |   `stability_assessment` is checked BEFORE capability |
| 5447–5458 |   `experiment_justification` is Tier 1 and does not require an experiment |
| 5459–5478 |   FMEA has no field in any schema, and none may be added |
| 5479–5510 |  42. Cross-phase reference fields in practice |
| 5511–5677 |  43. The coaching method |
| 5529–5556 |   43.1 The seven-step computation pattern |
| 5557–5594 |   43.2 Show before asking |
| 5595–5617 |   43.3 The A→F session flow |
| 5618–5649 |   43.4 The live gate document preview |
| 5650–5659 |   43.5 No external URLs |
| 5660–5677 |   43.6 What the coach must not do |
| 5678–6034 | Part IX — Reliability |
| 5682–5710 |   43.7 Metric literacy — the metric, and the statistic |
| 5711–5739 |  44. The failure pipeline |
| 5740–5852 |  45. Timeouts and compensating actions |
| 5747–5778 |   Per-node timeouts — required on every phase executor node |
| 5779–5788 |   Composition order — retries run BEFORE the handler |
| 5789–5798 |   Node-level error handlers — required on every node with external writes |
| 5799–5804 |   Hand-written Saga orchestrators are BANNED |
| 5805–5813 |   Two dependencies on this rule, both correctness-critical |
| 5814–5845 |   Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST** |
| 5846–5852 |   `DeltaChannel` is NOT used |
| 5853–5968 |  46. The fallback chain and circuit breakers |
| 5859–5871 |   The v2.1 four-level chain |
| 5872–5878 |   Backoff strategy is chosen per level, not globally |
| 5879–5897 |   Level 3 cache |
| 5898–5913 |   Circuit breakers — three-state, two instances |
| 5914–5920 |   Degraded mode uses actual state, never a generic error |
| 5921–5928 |   HTTP 400 is NOT a fallback case |
| 5929–5968 |   46.1 Geographic redundancy — **DEFERRED** |
| 5969–6009 |  47. Disconnect policy — what a dropped client commits |
| 5986–5992 |   Ratified policy: ABANDON, not COMPLETE |
| 5993–6009 |   Five requirements |
| 6010–6034 |  48. Structured errors |
| 6035–6522 | Part X — Operations |
| 6039–6092 |  49. API surface |
| 6045–6054 |   One runtime |
| 6055–6062 |   Async by default |
| 6063–6086 |   Endpoints |
| 6087–6092 |   Envelopes are Pydantic v2 |
| 6093–6249 |  50. UI and language rules |
| 6100–6138 |   50.1 Coach response structure |
| 6139–6150 |   Plain language always |
| 6151–6158 |   Citations |
| 6159–6172 |   Contextual feedback |
| 6173–6179 |   Connection status before the first interaction |
| 6180–6185 |   The gate review screen |
| 6186–6224 |   The live gate document |
| 6225–6236 |   The all-gate-fields tab is the contradiction backstop |
| 6237–6249 |   The conflict resolution panel |
| 6250–6325 |  51. Tracing and observability |
| 6256–6266 |   LangSmith is mandatory |
| 6267–6299 |   `@traceable` on every custom function |
| 6300–6305 |   What gets traced |
| 6306–6313 |   P50/P99 latency is a coaching quality signal |
| 6314–6325 |   Logs |
| 6326–6380 |  52. Evaluation and regression testing |
| 6332–6339 |   Built alongside the refactor, not before it |
| 6340–6346 |   The dataset is authored jointly, not generated |
| 6347–6360 |   Minimum viable suite |
| 6361–6371 |   Rubrics and the eval dataset are complementary, not duplicative |
| 6372–6380 |   Two open validation questions this suite answers |
| 6381–6522 |  53. Configuration, dependencies and deployment |
| 6387–6403 |   Fail-fast environment validation |
| 6404–6427 |   Dependency floor |
| 6428–6438 |   `/verify-current-version` is a mandatory checkpoint |
| 6439–6446 |   Infrastructure not yet provisioned |
| 6447–6458 |   Deployment layer: FastAPI, not LangGraph Server |
| 6459–6522 |   53.1 Migration sequence |
| 6523–7091 | Part XI — Governance |
| 6527–6569 |  54. Where code is allowed to live |
| 6534–6551 |   Classes are permitted ONLY in these files |
| 6552–6569 |   Target folder structure |
| 6570–6940 |  55. Anti-drift |
| 6584–6598 |   Rule numbers are load-bearing |
| 6599–6609 |   The registry guards code, not documentation |
| 6610–6615 |   Verification discipline |
| 6616–6638 |   Reference sweeps must use raw `grep -rn`, never a gitignore-filtered tool |
| 6639–6689 |   55.1 Spec-layer governance rules |
| 6690–6772 |   55.2 The BUILT markers, and the paths that oblige a re-check |
| 6773–6853 |   55.3 The phase completeness set — what one phase actually traverses |
| 6854–6903 |   55.4 Facts have one owner — the ratified minimum |
| 6904–6940 |   55.5 The commit gates govern. The rule files are advisory context. |
| 6941–7091 |  56. Amendment procedure |
| 6968–7011 |   56.0 What changed about amending, when the rules stopped being one file |
| 7012–7030 |   56.0.1 Rule, reference, and owned fact — three destinations |
| 7031–7073 |   56.1 A phase is one atomic unit — schema, validator, skill |
| 7074–7091 |   What requires an amendment rather than a routine change |
| 7092–11436 | Part XII — Specification |
| 7102–7125 |   56.2 The rule lands here; the reasoning lands in the commit |
| 7126–7159 |   56.3 The tree at HEAD is the only source of truth |
| 7160–7421 |  57. The specification layer — how to read and write a spec entry |
| 7167–7187 |   Why this Part exists |
| 7188–7203 |   The five structural rules |
| 7204–7218 |   Entry identity and traceability |
| 7219–7266 |   The entry template — three layers |
| 7267–7278 |   How gaps are marked |
| 7279–7295 |   57.1 The two calibrated samples |
| 7296–7349 |   57.2 SAMPLE 1 — CLASS TEMPLATE — S-C01 `SupervisorState` |
| 7299–7349 |    SPEC — `SupervisorState` |
| 7350–7400 |   57.3 SAMPLE 2 — FUNCTION/NODE TEMPLATE — S-F04 `phase_executor` (the coach node) |
| 7354–7400 |    SPEC — `phase_executor` (the coach node) |
| 7401–7421 |   57.4 Entry index |
| 7422–8751 |  58. Spec — graph management |
| 7432–7435 |   58.1 S-C01 · `SupervisorState` |
| 7436–7601 |   58.2 S-C02 · `PhaseState` |
| 7602–7620 |   58.3 S-C03 · Per-phase use of `PhaseState` |
| 7621–7696 |   58.4 S-C04 · `CoachingPlan` |
| 7697–7806 |   58.5 S-C05 · `CoachingResponse` |
| 7807–7858 |   58.6 S-C06 · `AzureBlobStore` |
| 7859–7904 |   58.7 S-C07 · `AzureBlobCheckpointSaver` |
| 7905–7951 |   58.8 S-C08 · `ImproveBlobClient` |
| 7952–8014 |   58.9 S-C09 · `storage/models.py` — the record models |
| 8015–8078 |   58.10 S-F01 · The supervisor graph — static edges |
| 8049–8058 |    SIPOC — at a glance |
| 8059–8078 |    Behaviors (EARS) |
| 8079–8124 |   58.11 S-F02 · `build_phase_subgraph(phase, llm)` |
| 8097–8106 |    SIPOC — at a glance |
| 8107–8124 |    Behaviors (EARS) |
| 8125–8165 |   58.12 S-F03 · `phase_planner` node |
| 8136–8145 |    SIPOC — at a glance |
| 8146–8165 |    Behaviors (EARS) |
| 8166–8177 |   58.13 S-F04 · `phase_executor` node |
| 8178–8239 |   58.14 S-F05 · `validation_stack` node |
| 8188–8197 |    SIPOC — at a glance |
| 8198–8209 |    Behaviors (EARS) |
| 8210–8239 |    ⚠ AI-ACT — high-risk surface |
| 8240–8291 |   58.15 S-F06 · `gate_review_node` |
| 8250–8259 |    SIPOC — at a glance |
| 8260–8267 |    Behaviors (EARS) |
| 8268–8291 |    ⚠ AI-ACT — high-risk surface |
| 8292–8359 |   58.16 S-F07 · `gate_apply_node` |
| 8313–8322 |    SIPOC — at a glance |
| 8323–8335 |    Behaviors (EARS) |
| 8336–8359 |    ⚠ AI-ACT — high-risk surface |
| 8360–8395 |   58.17 S-F08 · The escalation subgraph |
| 8368–8377 |    SIPOC — at a glance |
| 8378–8395 |    Behaviors (EARS) |
| 8396–8464 |   58.18 S-F09 · `analyse_executor_node` |
| 8436–8445 |    SIPOC — at a glance |
| 8446–8464 |    Behaviors (EARS) |
| 8465–8558 |   58.19 S-F10 · `define_input_mapper` |
| 8508–8520 |    SIPOC — at a glance |
| 8521–8549 |    Execution site — where a boundary mapper actually runs |
| 8550–8558 |    Behaviors (EARS) |
| 8559–8612 |   58.20 S-F11 · `define_output_mapper` |
| 8588–8597 |    SIPOC — at a glance |
| 8598–8612 |    Behaviors (EARS) |
| 8613–8662 |   58.21 S-F12 · The Measure, Analyse, Improve and Control mapper pairs |
| 8621–8630 |    SIPOC — at a glance |
| 8631–8662 |    Behaviors (EARS) |
| 8663–8751 |   58.22 S-F13 · Level 2 `Command` routing |
| 8680–8697 |    DP1 — the planner owns the field / gate decision |
| 8698–8718 |    DP2 — the validation stack's three exits |
| 8719–8739 |    DP3 — the gate exits |
| 8740–8751 |    What is settled and binds |
| 8752–9134 |  59. Spec — knowledge and retrieval |
| 8765–8794 |   59.1 S-C16 · `Hop` |
| 8795–8841 |   59.2 S-C17 · `Plan` — the hop decomposition plan |
| 8842–8878 |   59.3 S-C18 · `SynthesisOutput` |
| 8879–8895 |   59.4 S-C19 · `QueryVariants` |
| 8896–8942 |   59.5 S-F14 · `rag_lookup_methodology` |
| 8917–8926 |    SIPOC — at a glance |
| 8927–8942 |    Behaviors (EARS) |
| 8943–8990 |   59.6 S-F15 · `rag_lookup_evidence` |
| 8966–8975 |    SIPOC — at a glance |
| 8976–8990 |    Behaviors (EARS) |
| 8991–9037 |   59.7 S-F16 · `rag_lookup_case_history` |
| 9014–9023 |    SIPOC — at a glance |
| 9024–9037 |    Behaviors (EARS) |
| 9038–9088 |   59.8 S-F17 · `reciprocal_rank_fusion` |
| 9065–9074 |    SIPOC — at a glance |
| 9075–9088 |    Behaviors (EARS) |
| 9089–9134 |   59.9 S-F18 · The retriever layer — `search_knowledge`, `search_cases`, `search_evidence` |
| 9117–9134 |    SIPOC — at a glance |
| 9135–9420 |  60. Spec — tools |
| 9153–9186 |   60.1 S-F19 · `propose_template` |
| 9166–9186 |    SIPOC — at a glance |
| 9187–9225 |   60.2 S-F20 · `propose_diagram` |
| 9202–9211 |    SIPOC — at a glance |
| 9212–9225 |    Behaviors (EARS) |
| 9226–9267 |   60.3 S-F21 · `check_gate_status` |
| 9241–9250 |    SIPOC — at a glance |
| 9251–9267 |    Behaviors (EARS) |
| 9268–9303 |   60.4 S-F22 · `request_human_approval` |
| 9282–9303 |    SIPOC — at a glance |
| 9304–9320 |   60.5 S-F23 · `load_skill(name)` |
| 9321–9365 |   60.6 S-F24 · The 20 computation tools |
| 9344–9365 |    Behaviors (EARS) — binding on all twenty |
| 9366–9420 |   60.7 S-F57 · `load_evidence_series(blob_path, column)` |
| 9391–9400 |    SIPOC — at a glance |
| 9401–9420 |    Behaviors (EARS) |
| 9421–9673 |  61. Spec — the coaching agent's middleware |
| 9439–9501 |   61.1 S-C10 · `ContradictionDetectionMiddleware` |
| 9461–9470 |    Behaviors (EARS) |
| 9471–9501 |    ⚠ AI-ACT — high-risk surface |
| 9502–9543 |   61.2 S-C11 · `BeforeModelStateInjection` |
| 9515–9543 |    Behaviors (EARS) |
| 9544–9583 |   61.3 S-C12 · `DMAICSkillsMiddleware` |
| 9564–9583 |    Behaviors (EARS) |
| 9584–9620 |   61.4 S-C13 · `CoherenceMiddleware` |
| 9598–9620 |    Behaviors (EARS) |
| 9621–9656 |   61.5 S-C14 · `DMAICGraderMiddleware` |
| 9631–9656 |    Behaviors (EARS) |
| 9657–9673 |   61.6 S-C15 · `HITLInterrupt` |
| 9674–10081 |  62. Spec — validation and gates |
| 9688–9730 |   62.1 S-C20 · `CriterionVerdict` |
| 9731–9748 |   62.2 S-C21 · `GraderVerdict` |
| 9749–9762 |   62.3 S-C22 · `CoachingGraderVerdict` |
| 9763–9774 |   62.4 S-C23 · `CoherenceResult` |
| 9775–9789 |   62.5 S-C24 · `ConstraintCheckResult` / `ConstraintVerdict` |
| 9790–9802 |   62.6 S-C25 · `PolicyAdvisoryResult` |
| 9803–9839 |   62.7 S-C26 · `DMAICGateValidator` |
| 9840–9874 |   62.8 S-F25 · Layer 2c — the constraint check |
| 9849–9858 |    SIPOC — at a glance |
| 9859–9874 |    Behaviors (EARS) |
| 9875–9922 |   62.9 S-F26 · Layer 2d — the gate grader |
| 9890–9899 |    SIPOC — at a glance |
| 9900–9922 |    Behaviors (EARS) |
| 9923–9964 |   62.10 S-F27 · The policy advisory |
| 9938–9947 |    SIPOC — at a glance |
| 9948–9964 |    Behaviors (EARS) |
| 9965–10081 |   62.11 S-F28 · Gate document assembly |
| 10053–10062 |    SIPOC — at a glance |
| 10063–10081 |    Behaviors (EARS) |
| 10082–10603 |  63. Spec — the DMAIC gate documents |
| 10100–10168 |   63.1 S-C27 · `DefineOutput` |
| 10169–10209 |   63.2 S-C28 · `MeasureOutput` |
| 10210–10267 |   63.3 S-C29 · `AnalyseOutput` |
| 10268–10327 |   63.4 S-C30 · `ImproveOutput` |
| 10328–10399 |   63.5 S-C31 · `ControlOutput` |
| 10400–10466 |   63.6 S-C32 · The three cross-phase reference dicts |
| 10467–10508 |   63.7 S-C33 · The three structured dict fields |
| 10509–10547 |   63.8 S-C38 · `metric_definitions` — the project metric registry |
| 10548–10603 |   63.9 S-C39 · `phase_metrics` — the per-phase placeholder |
| 10604–10892 |  64. Spec — reliability |
| 10615–10655 |   64.1 S-C34 · `AgentImproveError` |
| 10656–10694 |   64.2 S-C35 · `CircuitBreaker` |
| 10695–10781 |   64.3 S-F29 · `phase_error_recovery` |
| 10723–10732 |    SIPOC — at a glance |
| 10733–10781 |    Behaviors (EARS) |
| 10782–10830 |   64.4 S-F30 · `degraded_mode_response` |
| 10803–10812 |    SIPOC — at a glance |
| 10813–10830 |    Behaviors (EARS) |
| 10831–10849 |   64.5 S-F31 · `synthesise_partial` |
| 10850–10874 |   64.6 S-F32 · `delete_or_flag_stale_in_case_index` |
| 10875–10892 |   64.7 S-F33 · `degraded_coaching_response` node |
| 10893–11069 |  65. Spec — API, UI and evidence |
| 10903–10923 |   65.1 S-C36 · `CitationRecord` and `CitationBundle` |
| 10924–10941 |   65.2 S-C37 · The API envelopes |
| 10942–10994 |   65.3 S-F34 · The API surface |
| 10964–10973 |    SIPOC — at a glance |
| 10974–10994 |    Behaviors (EARS) |
| 10995–11034 |   65.4 S-F35 · The upload handler |
| 11020–11034 |    Behaviors (EARS) |
| 11035–11069 |   65.5 S-F36 · The `improve_case_index` write path |
| 11070–11080 |  66. The SPEC-GAP register — MOVED |
| 11081–11174 |  67. EU AI Act compliance posture |
| 11088–11103 |   67.1 The deadlines are now fixed |
| 11104–11129 |   67.2 The classification question — open, and not answered here |
| 11130–11147 |   67.3 The eight core provider obligations |
| 11148–11158 |   67.4 One compliance finding is already recorded in this document |
| 11159–11174 |   67.5 Compliance-source discipline |
| 11175–11255 |  68. The DORA-structured compliance risk register |
| 11182–11199 |   68.1 Why DORA structure |
| 11200–11216 |   68.2 The register |
| 11217–11240 |   68.3 Pending classification — not register rows |
| 11241–11255 |   68.4 The infrastructure risk already on record |
| 11256–11436 |  69. Spec — computation tools |
| 11285–11356 |   69.1 Common conventions — stated once, binding on all twenty |
| 11357–11362 |   69.2 S-F37 · Define — 1 tool |
| 11363–11375 |   69.3 S-F38–S-F45 · Measure — 8 tools |
| 11376–11385 |   69.4 S-F46–S-F50 · Analyse — 5 tools |
| 11386–11391 |   69.5 S-F51 · Improve — 1 tool |
| 11392–11409 |   69.6 S-F52–S-F56 · Control — 5 tools |
| 11410–11436 |   69.7 The Measure control-chart boundary — a tool that is deliberately absent |
| 11437–11665 | Appendices |
| 11441–11456 |  Appendix A — Provenance index |
| 11447–11450 |   A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference |
| 11451–11456 |   A.2 `agent-improve/ARCHITECTURE.md` → this reference |
| 11457–11487 |  Appendix B — Deferred backlog |
| 11488–11553 |  Appendix C — Trusted sources |
| 11494–11513 |   Tier 1 — current, authoritative |
| 11514–11532 |   Tier 1 — compliance |
| 11533–11536 |   Tier 2 — official announcements |
| 11537–11540 |   Tier 3 — informed practitioner, cross-check before citing |
| 11541–11547 |   Downgraded — historical |
| 11548–11553 |   Excluded |
| 11554–11633 |  Appendix D — Retired names, banned patterns, and exclusions |
| 11556–11578 |   D.1 Retired names — never reintroduce |
| 11579–11622 |   D.2 Banned patterns |
| 11623–11633 |   D.3 Architecturally excluded — not deferred |
| 11634–11642 |  Appendix E — Current state |
| 11643–11665 |  Appendix F — The v2.2.16 registers |
| 11649–11654 |   F.1 Decisions Resolved (v2.2) — the former §17 |
| 11655–11665 |   F.2 Change Log — the former §18 |
| 11659–11665 |    F.2.1 Amendment procedure — the former §18.1 |
