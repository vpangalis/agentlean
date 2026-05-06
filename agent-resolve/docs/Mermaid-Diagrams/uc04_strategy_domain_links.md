# UC04 — Strategy Domain: Code Navigation Links

Companion to [uc04_strategy_domain.mmd](./uc04_strategy_domain.mmd).
The **#** column matches the Mermaid `autonumber` arrow number shown in the diagram exactly.

---

## Arrows 1–2 — cosolve-ui.js

| # | What | Link |
|---|------|------|
| 1 | User types portfolio-level pattern question | [index.html:943](../../ui/index.html#L943) |
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

## Arrows 7–8 — graph.py → strategy_node.py

| # | What | Link |
|---|------|------|
| 7 | strategy_node(state) L28 — start→context→intent→readiness(fast-path)→router→STRATEGY_ANALYSIS | [strategy_node.py:28](../../backend/reasoning/nodes/strategy_node.py#L28) |
| 8 | get_llm("reasoning", 0.2) L38 — LLM client instantiated | [strategy_node.py:38](../../backend/reasoning/nodes/strategy_node.py#L38) |

---

## Arrows 9–14 — strategy_node.py → tools.py → case_search_client.py → Azure AI Search (anchor queries loop)

| # | What | Link |
|---|------|------|
| 9 | search_cases_for_pattern_analysis.invoke({query:anchor_query, top_k:20}) L47 | [strategy_node.py:47](../../backend/reasoning/nodes/strategy_node.py#L47) |
| 10 | hybrid_search_cases() L66 — case search client | [case_search_client.py:66](../../backend/knowledge/case_search_client.py#L66) |
| 11 | Azure AI Search — case_index_v3 hybrid search | [case_search_client.py:43](../../backend/knowledge/case_search_client.py#L43) |
| 12 | Azure AI Search returns List[Document] | [tools.py:136](../../backend/knowledge/tools.py#L136) |
| 13 | List[Document] passed back to tools.py | [tools.py:136](../../backend/knowledge/tools.py#L136) |
| 14 | anchor_cases returned to strategy_node | [strategy_node.py:47](../../backend/reasoning/nodes/strategy_node.py#L47) |

---

## Arrows 15–20 — strategy_node.py → tools.py → case_search_client.py → Azure AI Search (question query)

| # | What | Link |
|---|------|------|
| 15 | search_cases_for_pattern_analysis.invoke({query:question, top_k:20}) L56 | [strategy_node.py:56](../../backend/reasoning/nodes/strategy_node.py#L56) |
| 16 | hybrid_search_cases() L66 | [case_search_client.py:66](../../backend/knowledge/case_search_client.py#L66) |
| 17 | Azure AI Search — case_index_v3 | [case_search_client.py:43](../../backend/knowledge/case_search_client.py#L43) |
| 18 | Azure AI Search returns List[Document] | [tools.py:136](../../backend/knowledge/tools.py#L136) |
| 19 | List[Document] passed back to tools.py | [tools.py:136](../../backend/knowledge/tools.py#L136) |
| 20 | question_cases returned to strategy_node | [strategy_node.py:56](../../backend/reasoning/nodes/strategy_node.py#L56) |

---

## Arrows 21–26 — strategy_node.py → tools.py → knowledge_search_client.py → Azure AI Search (knowledge)

| # | What | Link |
|---|------|------|
| 21 | search_knowledge_base.invoke({query, top_k:5}) L62 | [strategy_node.py:62](../../backend/reasoning/nodes/strategy_node.py#L62) |
| 22 | hybrid_search_knowledge() L40 | [knowledge_search_client.py:40](../../backend/knowledge/knowledge_search_client.py#L40) |
| 23 | Azure AI Search — knowledge_index_v2 | [knowledge_search_client.py:28](../../backend/knowledge/knowledge_search_client.py#L28) |
| 24 | Azure AI Search returns List[Document] | [tools.py:271](../../backend/knowledge/tools.py#L271) |
| 25 | List[Document] passed back to tools.py | [tools.py:271](../../backend/knowledge/tools.py#L271) |
| 26 | knowledge_docs returned to strategy_node | [strategy_node.py:62](../../backend/reasoning/nodes/strategy_node.py#L62) |

---

## Arrows 27–33 — strategy_node.py → Azure OpenAI

| # | What | Link |
|---|------|------|
| 27 | merge + deduplicate all_cases | [strategy_node.py:109](../../backend/reasoning/nodes/strategy_node.py#L109) |
| 28 | _to_dict() L146, _resolve_country() L156 | [strategy_node.py:146](../../backend/reasoning/nodes/strategy_node.py#L146) |
| 29 | llm.invoke(STRATEGY_PROMPT) L109 — question + all_cases_block + knowledge_block | [strategy_node.py:109](../../backend/reasoning/nodes/strategy_node.py#L109) |
| 30 | LLM returns response_text | [strategy_node.py:109](../../backend/reasoning/nodes/strategy_node.py#L109) |
| 31 | _extract_suggestions() L178 | [strategy_node.py:178](../../backend/reasoning/nodes/strategy_node.py#L178) |
| 32 | _ensure_general_advice_prefix() L166 | [strategy_node.py:166](../../backend/reasoning/nodes/strategy_node.py#L166) |
| 33 | strategy_draft returned to state | [strategy_node.py:178](../../backend/reasoning/nodes/strategy_node.py#L178) |

---

## Arrows 34–41 — strategy_reflection_node.py → Azure OpenAI → strategy_escalation_node.py

| # | What | Link |
|---|------|------|
| 34 | strategy_reflection_node(state) L16 | [strategy_reflection_node.py:16](../../backend/reasoning/nodes/strategy_reflection_node.py#L16) |
| 35 | llm.with_structured_output(StrategyReflectionAssessment).invoke() L31 | [strategy_reflection_node.py:31](../../backend/reasoning/nodes/strategy_reflection_node.py#L31) |
| 36 | LLM returns StrategyReflectionAssessment | [strategy_reflection_node.py:31](../../backend/reasoning/nodes/strategy_reflection_node.py#L31) |
| 37 | _score(assessment) L86 — 0.0–1.0 quality score | [strategy_reflection_node.py:86](../../backend/reasoning/nodes/strategy_reflection_node.py#L86) |
| 38 | score >= 0.65 — strategy_result=draft CONTINUE path | [strategy_reflection_node.py:86](../../backend/reasoning/nodes/strategy_reflection_node.py#L86) |
| 39 | score < 0.65 — strategy_result=draft, ESCALATE path | [strategy_reflection_node.py:86](../../backend/reasoning/nodes/strategy_reflection_node.py#L86) |
| 40 | strategy_escalation_node(state) L7 — _run_strategy(model=reasoning) | [strategy_escalation_node.py:7](../../backend/reasoning/nodes/strategy_escalation_node.py#L7) |
| 41 | strategy_result=premium returned to state | [strategy_escalation_node.py:9](../../backend/reasoning/nodes/strategy_escalation_node.py#L9) |

---

## Arrows 42–47 — response_formatter_node.py → reasoning_handler.py → cosolve-ui.js

| # | What | Link |
|---|------|------|
| 42 | response_formatter_node(state) L9 — intent==STRATEGY_ANALYSIS picks strategy_result L21 | [response_formatter_node.py:9](../../backend/reasoning/nodes/response_formatter_node.py#L9) |
| 43 | Returns final_response{answer, sources, chips, timestamp} | [response_formatter_node.py:25](../../backend/reasoning/nodes/response_formatter_node.py#L25) |
| 44 | graph.invoke() returns full graph_result dict | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |
| 45 | EntryResponseEnvelope(intent, status=accepted, data=final_response) L83 | [reasoning_handler.py:83](../../backend/gateway/reasoning_handler.py#L83) |
| 46 | FastAPI auto-serializes to JSON — returned to browser | [support_routes.py:111](../../backend/gateway/api/support_routes.py#L111) |
| 47 | fetch() resolves — AI panel rendered: answer + chips | [cosolve-ui.js:2117](../../ui/cosolve-ui.js#L2117) |
