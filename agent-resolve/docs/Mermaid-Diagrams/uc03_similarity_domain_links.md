# UC03 — Similarity Domain: Code Navigation Links

Companion to [uc03_similarity_domain.mmd](./uc03_similarity_domain.mmd).
The **#** column matches the Mermaid autonumber arrow number shown in the diagram exactly.

---

## Arrows 1–2 — cosolve-ui.js

| # | What | Link |
|---|------|------|
| 1 | User types similar cases question | [index.html:943](../../ui/index.html#L943) |
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

## Arrow 7 — graph.py → similarity_node.py

| # | What | Link |
|---|------|------|
| 7 | similarity_node(state) L20 — start→context→intent→readiness→router→SIMILARITY_SEARCH | [similarity_node.py:20](../../backend/reasoning/nodes/similarity_node.py#L20) |

---

## Arrows 8–14 — similarity_node.py → tools.py → case_search_client.py → Azure AI Search (cases)

| # | What | Link |
|---|------|------|
| 8 | search_similar_cases.invoke({query, top_k:10}) L29 | [similarity_node.py:29](../../backend/reasoning/nodes/similarity_node.py#L29) |
| 9 | hybrid_search_cases() L66 — case search client | [case_search_client.py:66](../../backend/knowledge/case_search_client.py#L66) |
| 10 | Azure AI Search — case_index_v3 hybrid search | [case_search_client.py:43](../../backend/knowledge/case_search_client.py#L43) |
| 11 | Azure AI Search returns List[Document] | [tools.py:76](../../backend/knowledge/tools.py#L76) |
| 12 | List[Document] passed back to tools.py | [tools.py:76](../../backend/knowledge/tools.py#L76) |
| 13 | _map_case_summary() L48 — per result | [tools.py:48](../../backend/knowledge/tools.py#L48) |
| 14 | List[CaseSummary] returned to similarity_node | [similarity_node.py:29](../../backend/reasoning/nodes/similarity_node.py#L29) |

---

## Arrows 15–20 — similarity_node.py → tools.py → knowledge_search_client.py → Azure AI Search (knowledge)

| # | What | Link |
|---|------|------|
| 15 | search_knowledge_base.invoke({query, top_k:5}) L32 | [similarity_node.py:32](../../backend/reasoning/nodes/similarity_node.py#L32) |
| 16 | hybrid_search_knowledge() L40 — knowledge search client | [knowledge_search_client.py:40](../../backend/knowledge/knowledge_search_client.py#L40) |
| 17 | Azure AI Search — knowledge_index_v2 hybrid search | [knowledge_search_client.py:28](../../backend/knowledge/knowledge_search_client.py#L28) |
| 18 | Azure AI Search returns List[Document] | [tools.py:271](../../backend/knowledge/tools.py#L271) |
| 19 | List[Document] passed back to tools.py | [tools.py:271](../../backend/knowledge/tools.py#L271) |
| 20 | knowledge_docs returned to similarity_node | [similarity_node.py:32](../../backend/reasoning/nodes/similarity_node.py#L32) |

---

## Arrows 21–24 — similarity_node.py → Azure OpenAI

| # | What | Link |
|---|------|------|
| 21 | llm.invoke(SIMILARITY_PROMPT) L73 — question + cases_block + knowledge_block | [similarity_node.py:73](../../backend/reasoning/nodes/similarity_node.py#L73) |
| 22 | LLM returns response_text | [similarity_node.py:73](../../backend/reasoning/nodes/similarity_node.py#L73) |
| 23 | extract_similarity_suggestions(response_text) L108 | [similarity_node.py:108](../../backend/reasoning/nodes/similarity_node.py#L108) |
| 24 | similarity_draft returned to state | [similarity_node.py:108](../../backend/reasoning/nodes/similarity_node.py#L108) |

---

## Arrows 25–32 — similarity_reflection_node.py → Azure OpenAI

| # | What | Link |
|---|------|------|
| 25 | similarity_reflection_node(state) L17 | [similarity_reflection_node.py:17](../../backend/reasoning/nodes/similarity_reflection_node.py#L17) |
| 26 | llm.with_structured_output(SimilarityReflectionAssessment).invoke() L27 | [similarity_reflection_node.py:27](../../backend/reasoning/nodes/similarity_reflection_node.py#L27) |
| 27 | LLM returns SimilarityReflectionAssessment | [similarity_reflection_node.py:27](../../backend/reasoning/nodes/similarity_reflection_node.py#L27) |
| 28 | _score(assessment) L81 — 0.0–1.0 quality score | [similarity_reflection_node.py:81](../../backend/reasoning/nodes/similarity_reflection_node.py#L81) |
| 29 | score >= 0.65 — similarity_result=draft | [similarity_reflection_node.py:81](../../backend/reasoning/nodes/similarity_reflection_node.py#L81) |
| 30 | score < 0.65 — regen_llm.invoke(REGEN_PROMPT) L40 | [similarity_reflection_node.py:40](../../backend/reasoning/nodes/similarity_reflection_node.py#L40) |
| 31 | LLM returns improved response | [similarity_reflection_node.py:40](../../backend/reasoning/nodes/similarity_reflection_node.py#L40) |
| 32 | similarity_result=regenerated returned to state | [similarity_reflection_node.py:40](../../backend/reasoning/nodes/similarity_reflection_node.py#L40) |

---

## Arrows 33–38 — response_formatter_node.py → reasoning_handler.py → cosolve-ui.js

| # | What | Link |
|---|------|------|
| 33 | response_formatter_node(state) L9 — intent==SIMILARITY_SEARCH picks similarity_result L19 | [response_formatter_node.py:9](../../backend/reasoning/nodes/response_formatter_node.py#L9) |
| 34 | Returns final_response{answer, sources, chips, timestamp} | [response_formatter_node.py:25](../../backend/reasoning/nodes/response_formatter_node.py#L25) |
| 35 | graph.invoke() returns full graph_result dict | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |
| 36 | EntryResponseEnvelope(intent, status=accepted, data=final_response) L83 | [reasoning_handler.py:83](../../backend/gateway/reasoning_handler.py#L83) |
| 37 | FastAPI auto-serializes to JSON — returned to browser | [support_routes.py:111](../../backend/gateway/api/support_routes.py#L111) |
| 38 | fetch() resolves — AI panel rendered: answer + chips | [cosolve-ui.js:2117](../../ui/cosolve-ui.js#L2117) |
