# UC02 — Operational Domain: Code Navigation Links

Companion to [uc02_operational_domain.mmd](./uc02_operational_domain.mmd).
The **#** column matches the Mermaid `autonumber` arrow number shown in the diagram exactly.

---

## Arrows 1–2 — cosolve-ui.js

| # | What | Link |
|---|------|------|
| 1 | User types question + case_id | [index.html:943](../../ui/index.html#L943) |
| 2 | fetch POST /entry/reasoning with JSON payload | [cosolve-ui.js:2094](../../ui/cosolve-ui.js#L2094) |

---

## Arrows 3–4 — support_routes.py

| # | What | Link |
|---|------|------|
| 3 | _dispatch_entry_handler(envelope) L82 | [support_routes.py:82](../../backend/gateway/api/support_routes.py#L82) |
| 4 | entry_handler.handle_entry(envelope) L84 | [support_routes.py:84](../../backend/gateway/api/support_routes.py#L84) |

---

## Arrow 5 — entry_handler.py

| # | What | Link |
|---|------|------|
| 5 | handle_ai_reasoning(envelope, graph) L68 | [reasoning_handler.py:43](../../backend/gateway/reasoning_handler.py#L43) |

---

## Arrow 6 — reasoning_handler.py → graph.py

| # | What | Link |
|---|------|------|
| 6 | graph.invoke(initial_state) L66 — RUNS ENTIRE PIPELINE | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |

---

## Arrow 7 — graph.py → operational_node.py

| # | What | Link |
|---|------|------|
| 7 | operational_node(state) L31 — context_node sets case_status from blob L50 | [operational_node.py:31](../../backend/reasoning/nodes/operational_node.py#L31) |

---

## Arrows 8–14 — operational_node.py → tools.py → Azure AI Search (knowledge — ALL branches)

| # | What | Link |
|---|------|------|
| 8 | get_llm("reasoning", 0.2) L44 | [operational_node.py:44](../../backend/reasoning/nodes/operational_node.py#L44) |
| 9 | search_knowledge_base.invoke({query, top_k:4, cosolve_phase}) L47 | [operational_node.py:47](../../backend/reasoning/nodes/operational_node.py#L47) |
| 10 | hybrid_search_knowledge() L40 | [knowledge_search_client.py:40](../../backend/knowledge/knowledge_search_client.py#L40) |
| 11 | Azure AI Search — knowledge_index_v2 | [knowledge_search_client.py:43](../../backend/knowledge/knowledge_search_client.py#L43) |
| 12 | Azure AI Search returns List[Document] | [tools.py:271](../../backend/knowledge/tools.py#L271) |
| 13 | List[KnowledgeSummary] returned to operational_node | [operational_node.py:50](../../backend/reasoning/nodes/operational_node.py#L50) |
| 14 | knowledge_docs returned to operational_node | [operational_node.py:50](../../backend/reasoning/nodes/operational_node.py#L50) |

---

## Arrows 15–18 — Branch A: New problem (no case loaded)

Condition: `is_new_problem_question(question, case_id) == True` — [operational_node.py:61](../../backend/reasoning/nodes/operational_node.py#L61)

| # | What | Link |
|---|------|------|
| 15 | llm.invoke(OPERATIONAL_NEW_PROBLEM_SYSTEM_PROMPT) L66 | [operational_node.py:66](../../backend/reasoning/nodes/operational_node.py#L66) |
| 16 | LLM returns response_text | [operational_node.py:66](../../backend/reasoning/nodes/operational_node.py#L66) |
| 17 | extract_suggestions(response_text) L72 | [operational_node.py:72](../../backend/reasoning/nodes/operational_node.py#L72) |
| 18 | Returns operational_draft{current_state:"No case loaded"} L73 | [operational_node.py:73](../../backend/reasoning/nodes/operational_node.py#L73) |

---

## Arrows 19–35 — Branch B: Closed case

Condition: `case_status == "closed"` — [operational_node.py:86](../../backend/reasoning/nodes/operational_node.py#L86)
Note: `and case_id` removed — redundant, case_status only set when case loaded

| # | What | Link |
|---|------|------|
| 19 | search_similar_cases.invoke({query, current_case_id, country}) L87 | [operational_node.py:87](../../backend/reasoning/nodes/operational_node.py#L87) |
| 20 | hybrid_search_cases() L66 | [case_search_client.py:66](../../backend/knowledge/case_search_client.py#L66) |
| 21 | Azure AI Search — case_index_v3 | [case_search_client.py:43](../../backend/knowledge/case_search_client.py#L43) |
| 22 | Azure AI Search returns List[Document] | [tools.py:76](../../backend/knowledge/tools.py#L76) |
| 23 | List[CaseSummary] returned | [operational_node.py:87](../../backend/reasoning/nodes/operational_node.py#L87) |
| 24 | supporting_cases returned to operational_node | [operational_node.py:87](../../backend/reasoning/nodes/operational_node.py#L87) |
| 25 | search_evidence.invoke({query, case_id}) L90 — filtered by case_id | [operational_node.py:90](../../backend/reasoning/nodes/operational_node.py#L90) |
| 26 | search_evidence() — evidence_index_v1 filter: case_id eq {case_id} | [evidence_search_client.py:36](../../backend/knowledge/evidence_search_client.py#L36) |
| 27 | Azure AI Search — evidence_index_v1 | [evidence_search_client.py:36](../../backend/knowledge/evidence_search_client.py#L36) |
| 28 | Azure AI Search returns List[Document] | [tools.py:324](../../backend/knowledge/tools.py#L324) |
| 29 | List[EvidenceSummary] returned | [operational_node.py:90](../../backend/reasoning/nodes/operational_node.py#L90) |
| 30 | referenced_evidence returned to operational_node | [operational_node.py:90](../../backend/reasoning/nodes/operational_node.py#L90) |
| 31 | format_d_states(case_context) L98 | [operational_node.py:98](../../backend/reasoning/nodes/operational_node.py#L98) |
| 32 | llm.invoke(OPERATIONAL_CLOSED_CASE_SYSTEM_PROMPT) L107 | [operational_node.py:107](../../backend/reasoning/nodes/operational_node.py#L107) |
| 33 | LLM returns response_text | [operational_node.py:107](../../backend/reasoning/nodes/operational_node.py#L107) |
| 34 | extract_suggestions(response_text) L113 | [operational_node.py:113](../../backend/reasoning/nodes/operational_node.py#L113) |
| 35 | Returns operational_draft{current_state:"closed"} L114 | [operational_node.py:114](../../backend/reasoning/nodes/operational_node.py#L114) |

---

## Arrows 36–52 — Branch C: Open / active case

Condition: fallthrough — case loaded and open — [operational_node.py:126](../../backend/reasoning/nodes/operational_node.py#L126)

| # | What | Link |
|---|------|------|
| 36 | search_similar_cases.invoke({query, current_case_id, country}) L129 | [operational_node.py:129](../../backend/reasoning/nodes/operational_node.py#L129) |
| 37 | hybrid_search_cases() L66 | [case_search_client.py:66](../../backend/knowledge/case_search_client.py#L66) |
| 38 | Azure AI Search — case_index_v3 | [case_search_client.py:43](../../backend/knowledge/case_search_client.py#L43) |
| 39 | Azure AI Search returns List[Document] | [tools.py:76](../../backend/knowledge/tools.py#L76) |
| 40 | List[CaseSummary] returned | [operational_node.py:129](../../backend/reasoning/nodes/operational_node.py#L129) |
| 41 | supporting_cases returned to operational_node | [operational_node.py:129](../../backend/reasoning/nodes/operational_node.py#L129) |
| 42 | search_evidence.invoke({query, case_id}) L132 | [operational_node.py:132](../../backend/reasoning/nodes/operational_node.py#L132) |
| 43 | search_evidence() — evidence_index_v1 filter: case_id eq {case_id} | [evidence_search_client.py:36](../../backend/knowledge/evidence_search_client.py#L36) |
| 44 | Azure AI Search — evidence_index_v1 | [evidence_search_client.py:36](../../backend/knowledge/evidence_search_client.py#L36) |
| 45 | Azure AI Search returns List[Document] | [tools.py:324](../../backend/knowledge/tools.py#L324) |
| 46 | List[EvidenceSummary] returned | [operational_node.py:132](../../backend/reasoning/nodes/operational_node.py#L132) |
| 47 | referenced_evidence returned to operational_node | [operational_node.py:132](../../backend/reasoning/nodes/operational_node.py#L132) |
| 48 | format_d_states(case_context) L137 | [operational_node.py:137](../../backend/reasoning/nodes/operational_node.py#L137) |
| 49 | llm.invoke(OPERATIONAL_SYSTEM_PROMPT) L159 | [operational_node.py:159](../../backend/reasoning/nodes/operational_node.py#L159) |
| 50 | LLM returns response_text | [operational_node.py:159](../../backend/reasoning/nodes/operational_node.py#L159) |
| 51 | extract_suggestions(response_text) L166 | [operational_node.py:166](../../backend/reasoning/nodes/operational_node.py#L166) |
| 52 | Returns operational_draft{current_state, supporting_cases} L167 | [operational_node.py:167](../../backend/reasoning/nodes/operational_node.py#L167) |

---

## Arrow 53 — Branch D: No case fallback

Condition: `not case_id` — no case loaded, not a new-problem question

| # | What | Link |
|---|------|------|
| 53 | Returns operational_draft with guidance to load case or ask general question | [operational_node.py:100](../../backend/reasoning/nodes/operational_node.py#L100) |

---

## Arrows 54–63 — operational_reflection_node.py → Azure OpenAI

| # | What | Link |
|---|------|------|
| 54 | operational_reflection_node(state) L27 | [operational_reflection_node.py:27](../../backend/reasoning/nodes/operational_reflection_node.py#L27) |
| 55 | llm.with_structured_output(OperationalReflectionAssessment).invoke() L59 | [operational_reflection_node.py:59](../../backend/reasoning/nodes/operational_reflection_node.py#L59) |
| 56 | LLM returns OperationalReflectionAssessment | [operational_reflection_node.py:59](../../backend/reasoning/nodes/operational_reflection_node.py#L59) |
| 57 | _score(assessment) L119 — 0.0–1.0. Threshold=0.65 | [operational_reflection_node.py:119](../../backend/reasoning/nodes/operational_reflection_node.py#L119) |
| 58 | score >= 0.65 — operational_result=draft | [operational_reflection_node.py:119](../../backend/reasoning/nodes/operational_reflection_node.py#L119) |
| 59 | score < 0.65 — regen_llm.invoke(REGEN_PROMPT) L72 | [operational_reflection_node.py:72](../../backend/reasoning/nodes/operational_reflection_node.py#L72) |
| 60 | LLM returns improved response | [operational_reflection_node.py:72](../../backend/reasoning/nodes/operational_reflection_node.py#L72) |
| 61 | operational_result=regenerated | [operational_reflection_node.py:72](../../backend/reasoning/nodes/operational_reflection_node.py#L72) |
| 62 | operational_escalation_node(state) L7 — _run_operational(model=reasoning) | [operational_escalation_node.py:7](../../backend/reasoning/nodes/operational_escalation_node.py#L7) |
| 63 | operational_result=premium returned | [operational_escalation_node.py:9](../../backend/reasoning/nodes/operational_escalation_node.py#L9) |

---

## Arrows 64–69 — response_formatter_node.py → reasoning_handler.py → cosolve-ui.js

| # | What | Link |
|---|------|------|
| 64 | response_formatter_node(state) L9 — OPERATIONAL_CASE picks operational_result L17 | [response_formatter_node.py:9](../../backend/reasoning/nodes/response_formatter_node.py#L9) |
| 65 | Returns final_response{answer, sources, chips, timestamp} | [response_formatter_node.py:25](../../backend/reasoning/nodes/response_formatter_node.py#L25) |
| 66 | graph.invoke() returns full graph_result dict | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |
| 67 | EntryResponseEnvelope(intent, status=accepted, data=final_response) L83 | [reasoning_handler.py:83](../../backend/gateway/reasoning_handler.py#L83) |
| 68 | FastAPI auto-serializes to JSON — returned to browser | [support_routes.py:111](../../backend/gateway/api/support_routes.py#L111) |
| 69 | fetch() resolves — AI panel rendered: answer + chips | [cosolve-ui.js:2117](../../ui/cosolve-ui.js#L2117) |
