---
paths:
  - "agent-improve/backend/core/tracing.py"
  - "agent-improve/backend/core/logging_setup.py"
  - "agent-improve/backend/core/metrics.py"
  - "agent-improve/backend/core/**"
  - "agent-improve/backend/middleware/**"
  - "agent-improve/backend/phases/nodes_common.py"
  - "agent-improve/scripts/**"
---
# §11 — Tracing and observability

> Never renumber — `deprecated_patterns.yaml` cites these (§0.2). History/rationale: `docs/_archive/rules_rationale_2026-09-25.md`.

## 11. TRACING AND OBSERVABILITY

### 11.1 — LangSmith required

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=agentlean-improve
```

No `LANGCHAIN_*` spelling is read.

Production environments without LangSmith fail startup with a clear
error (§11.4).

### 11.2 — `@traceable` on every custom function

LangSmith does **not** trace plain Python functions.

`@traceable` is REQUIRED on every function that:
- Extracts fields from LLM responses
- **Validates gate criteria — all three layers of §9.2 (2b–2d)**
- Scores completeness
- Makes routing decisions outside LangGraph node routing
- Calls an external Azure service directly, outside a LangChain runnable

### 11.3 — What gets traced

- Every graph invocation (full graph as parent span)
- Every node execution (child span per node)
- Every LLM call (prompt, response, token counts, cost)
- Every tool call (arguments and result)
- Every retrieval (query and top-k results)
- Every validation layer (§11.2)

**P50/P99 latency is a coaching quality signal**, not just an ops
metric. Fixes in order of preference: caching (§4.8 Level 3), a faster
grader model, cheapest-first validation (§9.2).

### 11.4 — Fail-fast environment validation

Validate all required credentials at startup, before the first request:

```
AZURE_OPENAI_API_KEY    — coaching LLM
AZURE_SEARCH_API_KEY    — retrieval        (NOT "AZURE_SEARCH_KEY")
LANGSMITH_API_KEY       — observability
```

Missing credentials exit 1 with a clear message. This integrates with
Docker health checks — a container failing startup receives no traffic.
Deployments: `AZURE_OPENAI_{INTENT,OPERATIONAL,PREMIUM,EMBEDDING}_DEPLOYMENT`.

**`.env` hygiene:** ONE `.env`, at the repo root; Improve loads it only via
`core/config.py::load_root_env()`.

### 11.5 — Logs

Structured logs via `logging`. Every request gets a `request_id`. Every
node logs entry, exit, and the state-slice keys it returned.


## Never

*§14's bans that belong to this file — 2 of 95, each landing in exactly one rule file. Verbatim, with their citations.*

- Never build a tracing, metrics or callback layer for LLM calls — LangSmith
  does it, and `@traceable` covers the plain functions between nodes
  (§0.24, §11.2)
- Never disable LangSmith tracing
