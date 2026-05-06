# UC05 — KPI Domain: Code Navigation Links

Companion to [uc05_kpi_domain.mmd](./uc05_kpi_domain.mmd).
The **#** column matches the Mermaid `autonumber` arrow number shown in the diagram exactly.

---

## Arrows 1–2 — cosolve-ui.js

| # | What | Link |
|---|------|------|
| 1 | User types KPI or metrics question | [index.html:943](../../ui/index.html#L943) |
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

## Arrows 7–8 — graph.py → kpi_node.py

| # | What | Link |
|---|------|------|
| 7 | kpi_node(state) L10 — start→context→intent→readiness(fast-path)→router→KPI_ANALYSIS | [kpi_node.py:10](../../backend/reasoning/nodes/kpi_node.py#L10) |
| 8 | get_kpis(scope, country, case_id) L24 — _resolve_scope() L44, _resolve_country() L55 | [kpi_node.py:24](../../backend/reasoning/nodes/kpi_node.py#L24) |

---

## Arrows 9–13 — tools.py → case_search_client.py → Azure AI Search (scope=case)

| # | What | Link |
|---|------|------|
| 9 | _case_scope(case_id) L815 | [tools.py:815](../../backend/knowledge/tools.py#L815) |
| 10 | _get_case_search_client() L56 — raw SearchClient (sanctioned SDK exception) | [case_search_client.py:56](../../backend/knowledge/case_search_client.py#L56) |
| 11 | Azure AI Search — case_index_v3 filter=case_id | [case_search_client.py:56](../../backend/knowledge/case_search_client.py#L56) |
| 12 | Azure AI Search returns single case | [tools.py:815](../../backend/knowledge/tools.py#L815) |
| 13 | SearchResult returned to tools.py | [tools.py:815](../../backend/knowledge/tools.py#L815) |

---

## Arrows 14–18 — tools.py → case_search_client.py → Azure AI Search (scope=country)

| # | What | Link |
|---|------|------|
| 14 | _country_scope(country) L765 | [tools.py:765](../../backend/knowledge/tools.py#L765) |
| 15 | _get_case_search_client() L56 | [case_search_client.py:56](../../backend/knowledge/case_search_client.py#L56) |
| 16 | Azure AI Search — case_index_v3 filter=country | [case_search_client.py:56](../../backend/knowledge/case_search_client.py#L56) |
| 17 | Azure AI Search returns List[SearchResult] | [tools.py:765](../../backend/knowledge/tools.py#L765) |
| 18 | List[SearchResult] returned to tools.py | [tools.py:765](../../backend/knowledge/tools.py#L765) |

---

## Arrows 19–23 — tools.py → case_search_client.py → Azure AI Search (scope=global)

| # | What | Link |
|---|------|------|
| 19 | _global_scope() L715 | [tools.py:715](../../backend/knowledge/tools.py#L715) |
| 20 | _get_case_search_client() L56 | [case_search_client.py:56](../../backend/knowledge/case_search_client.py#L56) |
| 21 | Azure AI Search — case_index_v3 top=1000 | [case_search_client.py:56](../../backend/knowledge/case_search_client.py#L56) |
| 22 | Azure AI Search returns all cases | [tools.py:715](../../backend/knowledge/tools.py#L715) |
| 23 | List[SearchResult] returned to tools.py | [tools.py:715](../../backend/knowledge/tools.py#L715) |

---

## Arrows 24–27 — tools.py → kpi_node.py (aggregation)

| # | What | Link |
|---|------|------|
| 24 | aggregate metrics: total_cases, open/closed, avg_resolution_days, d_state_distribution | [tools.py:891](../../backend/knowledge/tools.py#L891) |
| 25 | KPIResult returned to kpi_node | [tools.py:891](../../backend/knowledge/tools.py#L891) |
| 26 | _kpi_result_to_dict() L39 | [kpi_node.py:39](../../backend/reasoning/nodes/kpi_node.py#L39) |
| 27 | kpi_metrics dict returned to state | [kpi_node.py:58](../../backend/reasoning/nodes/kpi_node.py#L58) |

---

## Arrows 28–41 — kpi_reflection_node.py → Azure OpenAI

| # | What | Link |
|---|------|------|
| 28 | kpi_reflection_node(state) L59 — get_llm("reasoning", 0.0) L67 | [kpi_reflection_node.py:59](../../backend/reasoning/nodes/kpi_reflection_node.py#L59) |
| 29 | _generate_interpretation() L71 | [kpi_reflection_node.py:71](../../backend/reasoning/nodes/kpi_reflection_node.py#L71) |
| 30 | llm.with_structured_output(KPIInterpretationDraft).invoke() L132 | [kpi_reflection_node.py:132](../../backend/reasoning/nodes/kpi_reflection_node.py#L132) |
| 31 | LLM returns KPIInterpretationDraft | [kpi_reflection_node.py:132](../../backend/reasoning/nodes/kpi_reflection_node.py#L132) |
| 32 | _semantic_audit() L74 | [kpi_reflection_node.py:74](../../backend/reasoning/nodes/kpi_reflection_node.py#L74) |
| 33 | llm.with_structured_output(KPISemanticAudit).invoke() L151 | [kpi_reflection_node.py:151](../../backend/reasoning/nodes/kpi_reflection_node.py#L151) |
| 34 | LLM returns KPISemanticAudit | [kpi_reflection_node.py:151](../../backend/reasoning/nodes/kpi_reflection_node.py#L151) |
| 35 | _compute_completeness() L166 | [kpi_reflection_node.py:166](../../backend/reasoning/nodes/kpi_reflection_node.py#L166) |
| 36 | _hallucination_risk() L189 | [kpi_reflection_node.py:189](../../backend/reasoning/nodes/kpi_reflection_node.py#L189) |
| 37 | score >= 0.65 — kpi_interpretation returned to state | [kpi_reflection_node.py:166](../../backend/reasoning/nodes/kpi_reflection_node.py#L166) |
| 38 | score < 0.65 — _generate_interpretation(regen_llm) L78 | [kpi_reflection_node.py:78](../../backend/reasoning/nodes/kpi_reflection_node.py#L78) |
| 39 | regen_llm.with_structured_output(KPIInterpretationDraft).invoke() L132 | [kpi_reflection_node.py:132](../../backend/reasoning/nodes/kpi_reflection_node.py#L132) |
| 40 | LLM returns improved draft | [kpi_reflection_node.py:132](../../backend/reasoning/nodes/kpi_reflection_node.py#L132) |
| 41 | kpi_interpretation returned to state | [kpi_reflection_node.py:78](../../backend/reasoning/nodes/kpi_reflection_node.py#L78) |

---

## Arrows 42–47 — response_formatter_node.py → reasoning_handler.py → cosolve-ui.js

| # | What | Link |
|---|------|------|
| 42 | response_formatter_node(state) L9 — intent==KPI_ANALYSIS picks kpi_interpretation L23 | [response_formatter_node.py:9](../../backend/reasoning/nodes/response_formatter_node.py#L9) |
| 43 | Returns final_response{answer, sources, chips, timestamp} | [response_formatter_node.py:25](../../backend/reasoning/nodes/response_formatter_node.py#L25) |
| 44 | graph.invoke() returns full graph_result dict | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |
| 45 | EntryResponseEnvelope(intent, status=accepted, data=final_response) L83 | [reasoning_handler.py:83](../../backend/gateway/reasoning_handler.py#L83) |
| 46 | FastAPI auto-serializes to JSON — returned to browser | [support_routes.py:111](../../backend/gateway/api/support_routes.py#L111) |
| 47 | fetch() resolves — AI panel rendered: answer + chips | [cosolve-ui.js:2117](../../ui/cosolve-ui.js#L2117) |
