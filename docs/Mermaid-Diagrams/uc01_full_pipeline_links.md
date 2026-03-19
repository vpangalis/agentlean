# UC01 — Full Pipeline: Code Navigation Links

Companion to [uc01_full_pipeline.mmd](./uc01_full_pipeline.mmd).
The **#** column matches the Mermaid autonumber arrow number shown in the diagram exactly.

---

## Arrows 1–2 — cosolve-ui.js

| # | What | Link |
|---|------|------|
| 1 | User types question in AI textarea | [index.html:943](../../ui/index.html#L943) |
| 2 | fetch POST /entry/reasoning with JSON payload | [cosolve-ui.js:2094](../../ui/cosolve-ui.js#L2094) |

---

## Arrows 3–4 — support_routes.py

| # | What | Link |
|---|------|------|
| 3 | _dispatch_entry_handler(envelope) L82 — wraps in HTTP error handling | [support_routes.py:82](../../backend/gateway/api/support_routes.py#L82) |
| 4 | entry_handler.handle_entry(envelope) L84 | [support_routes.py:84](../../backend/gateway/api/support_routes.py#L84) |

---

## Arrow 5 — entry_handler.py

| # | What | Link |
|---|------|------|
| 5 | handle_ai_reasoning(envelope, graph) L68 — extracts question L49 + case_id L50, builds initial_state L60 | [reasoning_handler.py:43](../../backend/gateway/reasoning_handler.py#L43) |

---

## Arrow 6 — reasoning_handler.py (empty question guard)

| # | What | Link |
|---|------|------|
| 6 | Guard: empty question — returns EntryResponseEnvelope status=accepted immediately L54-58 | [reasoning_handler.py:52](../../backend/gateway/reasoning_handler.py#L52) |

---

## Arrow 7 — reasoning_handler.py → graph.py

| # | What | Link |
|---|------|------|
| 7 | graph.invoke(initial_state) — RUNS ENTIRE PIPELINE (blocking call) | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |

---

## Arrows 8–9 — graph.py → start_node.py

| # | What | Link |
|---|------|------|
| 8 | start_node(state) L6 — entry point of graph | [start_node.py:6](../../backend/reasoning/nodes/start_node.py#L6) |
| 9 | Returns: operational_escalated=False, strategy_escalated=False | [start_node.py:9](../../backend/reasoning/nodes/start_node.py#L9) |

---

## Arrows 10–14 — graph.py → context_node.py → blob_storage.py

| # | What | Link |
|---|------|------|
| 10 | context_node(state) L23 — checks for case_id in state | [context_node.py:23](../../backend/reasoning/nodes/context_node.py#L23) |
| 11 | CaseRepository.load(case_id) L102 — fetch case from Azure Blob | [context_node.py:34](../../backend/reasoning/nodes/context_node.py#L34) |
| 12 | Azure Blob returns raw JSON bytes | [blob_storage.py:20](../../backend/storage/blob_storage.py#L20) |
| 13 | Returns: case_context, case_status, current_d_state (case found) | [context_node.py:42](../../backend/reasoning/nodes/context_node.py#L42) |
| 14 | Returns: case_context=None (no case_id) | [context_node.py:27](../../backend/reasoning/nodes/context_node.py#L27) |

---

## Arrows 15–16 — graph.py → intent_classification_node.py

| # | What | Link |
|---|------|------|
| 15 | intent_classification_node(state) L11 — LLM classifies intent + scope + confidence | [intent_classification_node.py:11](../../backend/reasoning/nodes/intent_classification_node.py#L11) |
| 16 | Returns: classification{intent, scope, confidence} merged into state | [intent_classification_node.py:11](../../backend/reasoning/nodes/intent_classification_node.py#L11) |

---

## Arrows 17–19 — graph.py → question_readiness_node.py

| # | What | Link |
|---|------|------|
| 17 | question_readiness_node(state) L18 — checks if question is clear enough | [question_readiness_node.py:18](../../backend/reasoning/nodes/question_readiness_node.py#L18) |
| 18 | Fast path: case loaded OR KPI/Strategy — question_ready=True (no LLM) | [question_readiness_node.py:25](../../backend/reasoning/nodes/question_readiness_node.py#L25) |
| 19 | LLM path: returns question_ready + clarifying_question | [question_readiness_node.py:38](../../backend/reasoning/nodes/question_readiness_node.py#L38) |

---

## Arrows 20–22 — routing.py (question readiness conditional edge)

| # | What | Link |
|---|------|------|
| 20 | route_question_readiness(state) L15 — reads question_ready flag | [routing.py:15](../../backend/reasoning/routing.py#L15) |
| 21 | NOT_READY — short-circuits to response_formatter_node | [routing.py:20](../../backend/reasoning/routing.py#L20) |
| 22 | READY — proceeds to router_node | [routing.py:21](../../backend/reasoning/routing.py#L21) |

---

## Arrows 23–24 — router_node.py

| # | What | Link |
|---|------|------|
| 23 | router_node(state) L6 — reads classification["intent"], sets route key | [router_node.py:6](../../backend/reasoning/nodes/router_node.py#L6) |
| 24 | Returns: route = OPERATIONAL_CASE / SIMILARITY_SEARCH / STRATEGY_ANALYSIS / KPI_ANALYSIS | [router_node.py:9](../../backend/reasoning/nodes/router_node.py#L9) |

---

## Arrows 25–26 — routing.py (intent conditional edge)

| # | What | Link |
|---|------|------|
| 25 | route_intent(state) L24 — reads route key from state | [routing.py:24](../../backend/reasoning/routing.py#L24) |
| 26 | Dispatches to the appropriate domain node | [routing.py:24](../../backend/reasoning/routing.py#L24) |

---

## Arrows 27–30 — Domain node → response_formatter_node.py

| # | What | Link |
|---|------|------|
| 27 | Domain node runs (operational / similarity / strategy / kpi) | [graph.py:74](../../backend/core/graph.py#L74) |
| 28 | Domain node returns draft + result into state | [graph.py:85](../../backend/core/graph.py#L85) |
| 29 | response_formatter_node(state) L9 — picks result by intent | [response_formatter_node.py:9](../../backend/reasoning/nodes/response_formatter_node.py#L9) |
| 30 | Returns: final_response{answer, sources, chips, timestamp} | [response_formatter_node.py:25](../../backend/reasoning/nodes/response_formatter_node.py#L25) |

---

## Arrow 31 — graph.py → reasoning_handler.py

| # | What | Link |
|---|------|------|
| 31 | graph.invoke() returns full graph_result dict | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |

---

## Arrows 32–36 — reasoning_handler.py (response gates)

| # | What | Link |
|---|------|------|
| 32 | Gate 1: classification_low_confidence==True — build_clarifying_response() L75 | [reasoning_handler.py:71](../../backend/gateway/reasoning_handler.py#L71) |
| 33 | Returns EntryResponseEnvelope status=accepted (low confidence path) | [reasoning_handler.py:90](../../backend/gateway/reasoning_handler.py#L90) |
| 34 | Gate 2: question_ready==False — build_clarifying_question_response() L80 | [reasoning_handler.py:77](../../backend/gateway/reasoning_handler.py#L77) |
| 35 | Returns EntryResponseEnvelope status=ok (not ready path) | [reasoning_handler.py:114](../../backend/gateway/reasoning_handler.py#L114) |
| 36 | Gate 3 success: graph_result.get("final_response") L82 — EntryResponseEnvelope status=accepted | [reasoning_handler.py:83](../../backend/gateway/reasoning_handler.py#L83) |

---

## Arrows 37–38 — support_routes.py → cosolve-ui.js

| # | What | Link |
|---|------|------|
| 37 | FastAPI auto-serializes EntryResponseEnvelope to JSON — returned to browser | [support_routes.py:111](../../backend/gateway/api/support_routes.py#L111) |
| 38 | fetch() resolves — AI panel rendered: answer text + suggestion chips | [cosolve-ui.js:2117](../../ui/cosolve-ui.js#L2117) |
