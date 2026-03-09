# ARCHITECTURE.md — CoSolve Structural Decisions
# Version: 3.0 — 2026-03-09
# Changes from v2.0:
# - LLM roles replace Azure deployment names (decouples nodes from infra)
# - state.py → state/__init__.py (package conflict resolved)
# - tools.py → tools/__init__.py (package conflict resolved)

---

## Guiding Principle

CoSolve is a LangGraph application. LangGraph IS the architecture.
The graph, state, tools, and runnables replace all custom scaffolding.
Do not fight the framework — use it.

---

## What Changes vs What Stays

### STAYS COMPLETELY UNTOUCHED
- `backend/infra/blob_storage.py`
- `backend/infra/embeddings.py`
- `backend/infra/case_search_client.py`
- `backend/infra/evidence_search_client.py`
- `backend/infra/knowledge_search_client.py`
- `backend/ingestion/` — all ingestion pipelines
- `backend/utils/text.py`
- `backend/retrieval/models.py` — CaseSummary, EvidenceSummary, KnowledgeSummary
- Azure indexes — no changes in Azure portal
- Graph topology — edges, conditional edges, routing logic, escalation rules
- Prompt CONTENT inside each node — reasoning stays, container changes
- The UI entirely

---

## Directory Structure

```
backend/
    state/
        __init__.py             ← ONE TypedDict: IncidentGraphState
    tools/
        __init__.py             ← ALL @tool functions + client singletons
    prompts.py                  ← ALL prompts as module-level string constants
    llm.py                      ← get_llm(role, temperature) with lru_cache
    graph.py                    ← compiles and wires the graph, nothing else
    tracing.py                  ← LangSmith placeholder
    config.py                   ← Settings including LLM role → deployment mapping
    app.py                      ← FastAPI startup only, no node wiring
    api/
        schemas.py              ← CoSolveRequest, CoSolveResponse
        routes.py               ← /ask only, envelope translation
    workflow/
        nodes/                  ← 17 files, one function each
        routing.py              ← all conditional edge functions
        services/               ← unchanged
        node_parsing_utils.py   ← unchanged
    retrieval/
        models.py               ← unchanged
    infra/                      ← unchanged entirely
    ingestion/                  ← unchanged entirely
    utils/                      ← unchanged
```

---

## LLM Role Design

Nodes express a LOGICAL ROLE — never an Azure deployment name.
The mapping from role → Azure deployment lives only in config.py.
This means Azure infrastructure can change without touching node code.

### Roles

| Role | Purpose | Azure deployment (config) |
|------|---------|---------------------------|
| `"intent"` | Fast, cheap classification and routing | `LLM_INTENT_DEPLOYMENT = "intent-model"` |
| `"reasoning"` | Powerful analysis, reflection, formatting | `LLM_REASONING_DEPLOYMENT = "operational-premium"` |

### Node role assignments

| Node | Role | Temperature | Reason |
|------|------|-------------|--------|
| intent_classification_node | `"intent"` | 0.0 | Deterministic classification |
| question_readiness_node | `"intent"` | 0.0 | Deterministic classification |
| router_node | `"intent"` | 0.0 | Deterministic routing |
| start_node | `"intent"` | 0.0 | Trivial |
| end_node | `"intent"` | 0.0 | Trivial |
| context_node | `"reasoning"` | 0.3 | Case loading and formatting |
| response_formatter_node | `"reasoning"` | 0.3 | Readable output |
| operational_node | `"reasoning"` | 0.2 | Balanced reasoning |
| similarity_node | `"reasoning"` | 0.2 | Balanced reasoning |
| strategy_node | `"reasoning"` | 0.2 | Balanced reasoning |
| kpi_node | `"reasoning"` | 0.2 | Balanced reasoning |
| operational_reflection_node | `"reasoning"` | 0.0 | Strict, critical |
| similarity_reflection_node | `"reasoning"` | 0.0 | Strict, critical |
| strategy_reflection_node | `"reasoning"` | 0.0 | Strict, critical |
| kpi_reflection_node | `"reasoning"` | 0.0 | Strict, critical |
| operational_escalation_node | `"reasoning"` | 0.4 | Creative alternatives |
| strategy_escalation_node | `"reasoning"` | 0.4 | Creative alternatives |

### get_llm() contract

```python
# backend/llm.py
# get_llm() accepts a role name, resolves it to an Azure deployment via config
def get_llm(role: str, temperature: float) -> AzureChatOpenAI:
    deployment = _resolve_role(role)  # looks up LLM_INTENT_DEPLOYMENT etc.
    return _get_cached_llm(deployment, temperature)

# Nodes call it like this — no Azure names visible:
llm = get_llm("intent", 0.0)
llm = get_llm("reasoning", 0.2)
```

### config.py additions

```python
# Role → Azure deployment name mapping — only place Azure names appear
LLM_INTENT_DEPLOYMENT: str = "intent-model"
LLM_REASONING_DEPLOYMENT: str = "operational-premium"
```

---

## State

One class. One file. `backend/state/__init__.py`.
Nodes return dict slices — only the keys they update.
No Pydantic output models. No `.model_dump()`. No `cast()`.

---

## Tools

`backend/tools/__init__.py` — 7 @tool functions + `_map_case_summary` helper.
Module-level client singletons. No classes.
HybridRetriever logic preserved inside the tool functions.
`KNOWLEDGE_MIN_SCORE = 0.5` preserved.

---

## API Contract

routes.py only: validate → translate to state → run graph → translate to response.
IncidentGraphState never leaves the backend.
CoSolveRequest/CoSolveResponse never enter the graph.

---

## Memory Model (2 workers recommended)

Startup per worker:
- compiled_graph — 1 instance
- LLM instances — 1 per (deployment, temperature) via lru_cache
- Tool singletons — 1 per search client, module-level in tools/__init__.py

Per request:
- IncidentGraphState — 1 dict, lives for graph invocation, then GC'd
- Zero node objects — functions have no instance cost
