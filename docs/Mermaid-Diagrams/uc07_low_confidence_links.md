# UC07 — Low Confidence Classification: Code Navigation Links

Companion to [uc07_low_confidence.mmd](./uc07_low_confidence.mmd).
The **#** column matches the Mermaid `autonumber` arrow number shown in the diagram exactly.

---

## Arrows 1–2 — cosolve-ui.js

| # | What | Link |
|---|------|------|
| 1 | User types ambiguous question | [index.html:943](../../ui/index.html#L943) |
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
| 6 | graph.invoke(initial_state) L66 — start_node → context_node | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |

---

## Arrows 7–8 — graph.py → context_node.py

| # | What | Link |
|---|------|------|
| 7 | context_node(state) L23 — case_id is None, skip blob | [context_node.py:23](../../backend/reasoning/nodes/context_node.py#L23) |
| 8 | Scan question for TRM-XXXXXXXX-XXXX — not found → case_id_in_question=False L35 | [context_node.py:32](../../backend/reasoning/nodes/context_node.py#L32) |

---

## Arrows 9–12 — graph.py → intent_classification_node.py → Azure OpenAI

| # | What | Link |
|---|------|------|
| 9 | intent_classification_node(state) L11 | [intent_classification_node.py:11](../../backend/reasoning/nodes/intent_classification_node.py#L11) |
| 10 | llm.with_structured_output(_RawClassification).invoke() | [intent_classification_node.py:11](../../backend/reasoning/nodes/intent_classification_node.py#L11) |
| 11 | LLM returns intent, confidence=0.25 | [intent_classification_node.py:11](../../backend/reasoning/nodes/intent_classification_node.py#L11) |
| 12 | coerce_raw() — classification_low_confidence=True set in state | [intent_coercion.py:78](../../backend/reasoning/nodes/intent_coercion.py#L78) |

---

## Arrows 13–14 — graph continues → response_formatter_node.py

| # | What | Link |
|---|------|------|
| 13 | Graph continues: question_readiness → router → domain node → response_formatter | [graph.py:65](../../backend/core/graph.py#L65) |
| 14 | response_formatter_node returns final_response | [response_formatter_node.py:9](../../backend/reasoning/nodes/response_formatter_node.py#L9) |

---

## Arrow 15 — graph.py → reasoning_handler.py

| # | What | Link |
|---|------|------|
| 15 | graph.invoke() returns graph_result | [reasoning_handler.py:66](../../backend/gateway/reasoning_handler.py#L66) |

---

## Arrows 16–17 — reasoning_handler.py (low confidence path)

| # | What | Link |
|---|------|------|
| 16 | classification_low_confidence==True L71 — build_clarifying_response(envelope) L75 | [reasoning_handler.py:71](../../backend/gateway/reasoning_handler.py#L71) |
| 17 | EntryResponseEnvelope status=accepted — summary=_CLARIFYING_TEXT, suggestions=_CLARIFYING_SUGGESTIONS | [reasoning_handler.py:90](../../backend/gateway/reasoning_handler.py#L90) |

---

## Arrows 18–19 — support_routes.py → cosolve-ui.js

| # | What | Link |
|---|------|------|
| 18 | FastAPI auto-serializes to JSON — returned to browser | [support_routes.py:111](../../backend/gateway/api/support_routes.py#L111) |
| 19 | fetch() resolves — UI displays clarifying message + 4 suggestion chips | [cosolve-ui.js:2117](../../ui/cosolve-ui.js#L2117) |
