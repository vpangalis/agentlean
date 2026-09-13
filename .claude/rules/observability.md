---
paths:
  - "agent-improve/backend/core/tracing.py"
  - "agent-improve/backend/core/logging_setup.py"
  - "agent-improve/backend/core/metrics.py"
---
# §11 — Tracing and observability

> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

## 11. TRACING AND OBSERVABILITY

### 11.1 — LangSmith required

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=agentlean-improve
```

Production environments without LangSmith fail startup with a clear
error (§11.4).

### 11.2 — `@traceable` on every custom function

LangSmith traces LangChain runnables and LangGraph nodes
automatically. It does **not** trace plain Python functions. Without
`@traceable`, the logic *between* nodes is invisible and a gate failure
surfaces as a 500 with no indication of which layer failed.

`@traceable` is REQUIRED on every function that:
- Extracts fields from LLM responses
- **Validates gate criteria — all four layers of §9.2**
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
metric. High P99 degrades the Belt's experience. The usual outlier is
multi-hop retrieval combined with a grader call on the same turn; the
fixes in order of preference are caching (§4.8 Level 3), a faster
grader model, and reordering the validation stack cheapest-first
(already mandated in §9.2).

### 11.4 — Fail-fast environment validation

Validate all required credentials at startup, before the first request:

```
AZURE_OPENAI_KEY        — coaching LLM
AZURE_SEARCH_API_KEY    — retrieval        (NOT "AZURE_SEARCH_KEY")
LANGCHAIN_API_KEY       — observability
```

Missing credentials exit 1 with a clear message. This integrates with
Docker health checks — a container failing startup receives no traffic.

**`.env` hygiene:** the app loads `agent-improve/.env`. A root `.env`
can silently shadow values depending on `load_dotenv()` search order —
audit and remove it if redundant.

### 11.5 — Logs

Structured logs via `logging`. Every request gets a `request_id`. Every
node logs entry, exit, and the state-slice keys it returned.


## Never

*§14's bans that belong to this file — 2 of 95, each landing in exactly one rule file. Verbatim, with their citations.*

- Never build a tracing, metrics or callback layer for LLM calls — LangSmith
  does it, and `@traceable` covers the plain functions between nodes
  (§0.24, §11.2)
- Never disable LangSmith tracing
