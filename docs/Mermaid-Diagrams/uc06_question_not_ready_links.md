# UC06 — Question Not Ready: Code Navigation Links

Companion to [uc06_question_not_ready.mmd](./uc06_question_not_ready.mmd).
The **#** column matches the Mermaid `autonumber` arrow number shown in the diagram exactly.

---

## Arrows 1–2 — cosolve-ui.js

| # | What | Link |
|---|------|------|
| 1 | User types vague question with no case_id | [index.html:943](../../ui/index.html#L943) |
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
| 5 | handle_ai_reasoning(envelope, graph) L68 — case_id=None L50 | [reasoning_handler.py:43](../../backend/gateway/reasoning_handler.py#L43) |

---

## Arrow 6 — reasoning_handler.py → graph.py

| # | What | Link |
|---|------|------|
| 6 | graph.invoke(initial_state) L66 | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |

---

## Arrows 7–8 — graph.py → start_node.py

| # | What | Link |
|---|------|------|
| 7 | start_node(state) L6 | [start_node.py:6](../../backend/reasoning/nodes/start_node.py#L6) |
| 8 | Returns: escalated flags = False | [start_node.py:9](../../backend/reasoning/nodes/start_node.py#L9) |

---

## Arrows 9–10 — graph.py → context_node.py

| # | What | Link |
|---|------|------|
| 9 | context_node(state) L23 — case_id is None, skip blob | [context_node.py:23](../../backend/reasoning/nodes/context_node.py#L23) |
| 10 | Returns: case_context=None immediately L27 | [context_node.py:27](../../backend/reasoning/nodes/context_node.py#L27) |

---

## Arrows 11–12 — graph.py → intent_classification_node.py

| # | What | Link |
|---|------|------|
| 11 | intent_classification_node(state) L11 — case_loaded=False L18 | [intent_classification_node.py:11](../../backend/reasoning/nodes/intent_classification_node.py#L11) |
| 12 | Returns: intent=OPERATIONAL, confidence=0.4 | [intent_classification_node.py:11](../../backend/reasoning/nodes/intent_classification_node.py#L11) |

---

## Arrows 13–14 — graph.py → question_readiness_node.py

| # | What | Link |
|---|------|------|
| 13 | question_readiness_node(state) L18 — OPERATIONAL not in _ALWAYS_READY_INTENTS, case_loaded=False | [question_readiness_node.py:18](../../backend/reasoning/nodes/question_readiness_node.py#L18) |
| 14 | LLM call — returns question_ready=False, clarifying_question | [question_readiness_node.py:38](../../backend/reasoning/nodes/question_readiness_node.py#L38) |

---

## Arrows 15–16 — routing.py (NOT_READY short-circuit)

| # | What | Link |
|---|------|------|
| 15 | route_question_readiness(state) L15 — not question_ready L16 | [routing.py:15](../../backend/reasoning/routing.py#L15) |
| 16 | NOT_READY — skips router_node + all domain nodes, goes to response_formatter | [routing.py:20](../../backend/reasoning/routing.py#L20) |

---

## Arrows 17–18 — response_formatter_node.py

| # | What | Link |
|---|------|------|
| 17 | response_formatter_node(state) L9 — question_ready=False path | [response_formatter_node.py:9](../../backend/reasoning/nodes/response_formatter_node.py#L9) |
| 18 | Returns final_response{clarifying_question} | [response_formatter_node.py:25](../../backend/reasoning/nodes/response_formatter_node.py#L25) |

---

## Arrow 19 — graph.py → reasoning_handler.py

| # | What | Link |
|---|------|------|
| 19 | graph.invoke() returns graph_result | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |

---

## Arrows 20–21 — reasoning_handler.py (clarifying question path)

| # | What | Link |
|---|------|------|
| 20 | question_ready==False L77 — build_clarifying_question_response(envelope, cq) L80 | [reasoning_handler.py:77](../../backend/gateway/reasoning_handler.py#L77) |
| 21 | EntryResponseEnvelope status=ok L134 — summary=clarifying_question | [reasoning_handler.py:114](../../backend/gateway/reasoning_handler.py#L114) |

---

## Arrows 22–23 — support_routes.py → cosolve-ui.js

| # | What | Link |
|---|------|------|
| 22 | FastAPI auto-serializes to JSON — returned to browser | [support_routes.py:111](../../backend/gateway/api/support_routes.py#L111) |
| 23 | fetch() resolves — UI displays clarifying question + suggestion chips | [cosolve-ui.js:2117](../../ui/cosolve-ui.js#L2117) |
