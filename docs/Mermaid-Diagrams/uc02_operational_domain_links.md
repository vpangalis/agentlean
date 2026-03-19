# UC02 — Operational Domain: Code Navigation Links

Companion to [uc02_operational_domain.mmd](./uc02_operational_domain.mmd).
The **#** column matches the Mermaid `autonumber` step shown in the diagram.

---

## STEP 1–8 — UI → graph.invoke()

| # | What | Link |
|---|------|------|
| 1 | User types question in AI textarea | [index.html:943](../../ui/index.html#L943) |
| 2 | `fetch(${API_BASE}/entry/reasoning, { method:"POST", body: JSON.stringify(payload) })` | [cosolve-ui.js:2094](../../ui/cosolve-ui.js#L2094) |
| 3 | `handle_reasoning_entry(envelope: EntryEnvelope)` — JSON body parsed into Pydantic model | [support_routes.py:108](../../backend/gateway/api/support_routes.py#L108) |
| 4 | `_dispatch_entry_handler(envelope)` — wraps in HTTP error handling | [support_routes.py:82](../../backend/gateway/api/support_routes.py#L82) |
| 5 | `entry_handler.handle_entry(envelope)` | [support_routes.py:84](../../backend/gateway/api/support_routes.py#L84) |
| 6 | `if intent == "AI_REASONING"` — branches to reasoning path | [entry_handler.py:67](../../backend/gateway/entry_handler.py#L67) |
| 7 | `handle_ai_reasoning(envelope, graph)` — extracts question L49 + case_id L50, builds initial_state L60 | [reasoning_handler.py:43](../../backend/gateway/reasoning_handler.py#L43) |
| 8 | **`graph.invoke(initial_state)` — RUNS ENTIRE PIPELINE (blocking call)** | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |

---

## STEP 9 — operational_node entry

| # | What | Link |
|---|------|------|
| 9 | `operational_node(state)` → `_run_operational(state, model_name=None)` → `get_llm("reasoning", 0.2)` | [operational_node.py:31](../../backend/reasoning/nodes/operational_node.py#L31) |

---

## STEP 10–13 — Knowledge search (runs for ALL branches before split)

| # | What | Link |
|---|------|------|
| 10 | `search_knowledge_base.invoke({ query, top_k:4, cosolve_phase })` | [operational_node.py:47](../../backend/reasoning/nodes/operational_node.py#L47) |
| 11 | `hybrid_search_knowledge()` → Azure AI Search `knowledge_index_v2` | [knowledge_search_client.py:40](../../backend/knowledge/knowledge_search_client.py#L40) |
| 12 | Azure AI Search returns `List[Document]` | [tools.py:271](../../backend/knowledge/tools.py#L271) |
| 13 | `List[KnowledgeSummary]` built into `knowledge_block` text | [operational_node.py:50](../../backend/reasoning/nodes/operational_node.py#L50) |

---

## STEP 14–17 — Branch A: New problem (no case loaded)

Condition: `is_new_problem_question(question, case_id) == True` — [operational_node.py:61](../../backend/reasoning/nodes/operational_node.py#L61)
No case/evidence search. Uses `knowledge_block` only.

| # | What | Link |
|---|------|------|
| 14 | `llm.invoke([SystemMessage(OPERATIONAL_NEW_PROBLEM_SYSTEM_PROMPT), HumanMessage(question + knowledge_block)])` | [operational_node.py:66](../../backend/reasoning/nodes/operational_node.py#L66) |
| 15 | LLM returns `response_text` | [operational_node.py:66](../../backend/reasoning/nodes/operational_node.py#L66) |
| 16 | `extract_suggestions(response_text)` — parses `[WHAT TO EXPLORE NEXT]` | [operational_node.py:72](../../backend/reasoning/nodes/operational_node.py#L72) |
| 17 | Returns `{ "operational_draft": { current_state:"No case loaded", recommendations, suggestions } }` | [operational_node.py:73](../../backend/reasoning/nodes/operational_node.py#L73) |

---

## STEP 18–30 — Branch B: Closed case

Condition: `case_status == "closed" and case_id` — [operational_node.py:86](../../backend/reasoning/nodes/operational_node.py#L86)

| # | What | Link |
|---|------|------|
| 18 | `search_similar_cases.invoke({ query, current_case_id, country })` | [operational_node.py:87](../../backend/reasoning/nodes/operational_node.py#L87) |
| 19 | `hybrid_search_cases()` → Azure AI Search `case_index_v3` | [case_search_client.py:66](../../backend/knowledge/case_search_client.py#L66) |
| 20 | Azure AI Search returns `List[Document]` | [tools.py:76](../../backend/knowledge/tools.py#L76) |
| 21 | `List[CaseSummary]` returned to operational_node | [operational_node.py:87](../../backend/reasoning/nodes/operational_node.py#L87) |
| 22 | `search_evidence.invoke({ query, case_id })` — filtered by case_id | [operational_node.py:90](../../backend/reasoning/nodes/operational_node.py#L90) |
| 23 | `search_evidence()` → Azure AI Search `evidence_index_v1` filter: `case_id eq {case_id}` | [evidence_search_client.py:36](../../backend/knowledge/evidence_search_client.py#L36) |
| 24 | Azure AI Search returns `List[Document]` | [tools.py:324](../../backend/knowledge/tools.py#L324) |
| 25 | `List[EvidenceSummary]` returned to operational_node | [operational_node.py:90](../../backend/reasoning/nodes/operational_node.py#L90) |
| 26 | `format_d_states(case_context)` — formats D1–D8 history text for LLM prompt | [operational_node.py:98](../../backend/reasoning/nodes/operational_node.py#L98) |
| 27 | `llm.invoke([SystemMessage(OPERATIONAL_CLOSED_CASE_SYSTEM_PROMPT), HumanMessage(case+history+cases+evidence+knowledge)])` | [operational_node.py:107](../../backend/reasoning/nodes/operational_node.py#L107) |
| 28 | LLM returns `response_text` | [operational_node.py:107](../../backend/reasoning/nodes/operational_node.py#L107) |
| 29 | `extract_suggestions(response_text)` | [operational_node.py:113](../../backend/reasoning/nodes/operational_node.py#L113) |
| 30 | Returns `{ "operational_draft": { current_state:"closed", recommendations, supporting_cases, referenced_evidence, suggestions } }` | [operational_node.py:114](../../backend/reasoning/nodes/operational_node.py#L114) |

---

## STEP 31–43 — Branch C: Open / active case

Condition: fallthrough — no closed match — [operational_node.py:126](../../backend/reasoning/nodes/operational_node.py#L126)

| # | What | Link |
|---|------|------|
| 31 | `search_similar_cases.invoke({ query, current_case_id, country })` | [operational_node.py:129](../../backend/reasoning/nodes/operational_node.py#L129) |
| 32 | `hybrid_search_cases()` → Azure AI Search `case_index_v3` | [case_search_client.py:66](../../backend/knowledge/case_search_client.py#L66) |
| 33 | Azure AI Search returns `List[Document]` | [tools.py:76](../../backend/knowledge/tools.py#L76) |
| 34 | `List[CaseSummary]` returned to operational_node | [operational_node.py:129](../../backend/reasoning/nodes/operational_node.py#L129) |
| 35 | `search_evidence.invoke({ query, case_id })` | [operational_node.py:132](../../backend/reasoning/nodes/operational_node.py#L132) |
| 36 | `search_evidence()` → Azure AI Search `evidence_index_v1` filter: `case_id eq {case_id}` | [evidence_search_client.py:36](../../backend/knowledge/evidence_search_client.py#L36) |
| 37 | Azure AI Search returns `List[Document]` | [tools.py:324](../../backend/knowledge/tools.py#L324) |
| 38 | `List[EvidenceSummary]` returned to operational_node | [operational_node.py:132](../../backend/reasoning/nodes/operational_node.py#L132) |
| 39 | `format_d_states(case_context)` | [operational_node.py:137](../../backend/reasoning/nodes/operational_node.py#L137) |
| 40 | `llm.invoke([SystemMessage(OPERATIONAL_SYSTEM_PROMPT), HumanMessage(active_case+d_state+cases+evidence+knowledge)])` | [operational_node.py:159](../../backend/reasoning/nodes/operational_node.py#L159) |
| 41 | LLM returns `response_text` | [operational_node.py:159](../../backend/reasoning/nodes/operational_node.py#L159) |
| 42 | `extract_suggestions(response_text)` | [operational_node.py:166](../../backend/reasoning/nodes/operational_node.py#L166) |
| 43 | Returns `{ "operational_draft": { current_state, recommendations, supporting_cases, referenced_evidence, suggestions } }` | [operational_node.py:167](../../backend/reasoning/nodes/operational_node.py#L167) |

---

## STEP 44–51 — operational_reflection_node

| # | What | Link |
|---|------|------|
| 44 | `operational_reflection_node(state)` — assesses quality of `operational_draft` | [operational_reflection_node.py:27](../../backend/reasoning/nodes/operational_reflection_node.py#L27) |
| 45 | New-problem bypass: skip LLM — `needs_escalation=False`, returns `operational_result=draft` | [operational_reflection_node.py:37](../../backend/reasoning/nodes/operational_reflection_node.py#L37) |
| 46 | `llm.with_structured_output(OperationalReflectionAssessment).invoke(REFLECTION_PROMPT + draft)` | [operational_reflection_node.py:59](../../backend/reasoning/nodes/operational_reflection_node.py#L59) |
| 47 | LLM returns `OperationalReflectionAssessment` | [operational_reflection_node.py:59](../../backend/reasoning/nodes/operational_reflection_node.py#L59) |
| 48 | `_score(assessment)` — 0.0–1.0 across 5 dimensions. Threshold = 0.65 | [operational_reflection_node.py:64](../../backend/reasoning/nodes/operational_reflection_node.py#L64) |
| 49 | If score < 0.65: `regen_llm.invoke(OPERATIONAL_REGENERATION_SYSTEM_PROMPT)` | [operational_reflection_node.py:72](../../backend/reasoning/nodes/operational_reflection_node.py#L72) |
| 50 | LLM returns improved `response_text` | [operational_reflection_node.py:72](../../backend/reasoning/nodes/operational_reflection_node.py#L72) |
| 51 | Returns `operational_result` + `operational_reflection{ needs_escalation }` | [operational_reflection_node.py:86](../../backend/reasoning/nodes/operational_reflection_node.py#L86) |

---

## STEP 52–57 — Escalation routing

`route_operational_escalation()` reads `needs_escalation` — [routing.py:29](../../backend/reasoning/routing.py#L29)

| # | What | Link |
|---|------|------|
| 52 | **CONTINUE path**: `response_formatter_node(state)` | [response_formatter_node.py:9](../../backend/reasoning/nodes/response_formatter_node.py#L9) |
| 53 | **ESCALATE path**: `operational_escalation_node(state)` | [operational_escalation_node.py:7](../../backend/reasoning/nodes/operational_escalation_node.py#L7) |
| 54 | `_run_operational(state, model_name="reasoning")` → premium model draft | [operational_escalation_node.py:9](../../backend/reasoning/nodes/operational_escalation_node.py#L9) |
| 55 | Hard edge loops back to `operational_reflection_node` (once only) | [graph.py:94](../../backend/core/graph.py#L94) |
| 56 | `operational_reflection_node` returns final `operational_result` | [operational_reflection_node.py:86](../../backend/reasoning/nodes/operational_reflection_node.py#L86) |
| 57 | `response_formatter_node(state)` after escalation path | [response_formatter_node.py:9](../../backend/reasoning/nodes/response_formatter_node.py#L9) |

---

## STEP 58–62 — Format and return

| # | What | Link |
|---|------|------|
| 58 | `intent == "OPERATIONAL_CASE"` → picks `state["operational_result"]` → returns `final_response { timestamp, classification, result }` | [response_formatter_node.py:16](../../backend/reasoning/nodes/response_formatter_node.py#L16) |
| 59 | `graph.invoke()` returns full `graph_result` dict | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |
| 60 | `EntryResponseEnvelope(intent, status:"accepted", data: final_response)` | [reasoning_handler.py:83](../../backend/gateway/reasoning_handler.py#L83) |
| 61 | FastAPI auto-serializes to JSON → returned to browser | [support_routes.py:111](../../backend/gateway/api/support_routes.py#L111) |
| 62 | `fetch()` resolves → `res.json()` → AI panel rendered: answer text + suggestion chips | [cosolve-ui.js:2117](../../ui/cosolve-ui.js#L2117) |
