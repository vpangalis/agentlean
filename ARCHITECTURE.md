# ARCHITECTURE.md — CoSolve Structural Decisions
# Version: 2.0 — Updated after full codebase audit 2026-03-08

---

## Guiding Principle

CoSolve is a LangGraph application. LangGraph IS the architecture.
The graph, state, tools, and runnables replace all custom scaffolding.
Do not fight the framework — use it.

The business logic — prompts, routing rules, retrieval logic, reflection
criteria — is the valuable part. The class scaffolding is overhead.

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
- `backend/config.py`
- `backend/retrieval/models.py` — CaseSummary, EvidenceSummary, KnowledgeSummary
- Azure indexes — no changes in Azure portal
- Graph topology — edges, conditional edges, routing logic, escalation rules
- Prompt CONTENT inside each node — reasoning stays, container changes
- The UI entirely

### CHANGES
- `backend/workflow/nodes/*.py` — 18 classes → 18 module-level functions
- `backend/retrieval/hybrid_retriever.py` — class dissolved, methods become @tool functions
- `backend/workflow/models.py` — Pydantic output models collapsed into IncidentGraphState
- `backend/app.py` — removes all dependency injection wiring
- `backend/api/routes.py` — adds CoSolveRequest/CoSolveResponse envelope translation

### NEW FILES
- `backend/state.py` — single IncidentGraphState TypedDict
- `backend/tools.py` — all @tool functions wrapping retrieval logic
- `backend/prompts.py` — all prompts as module-level string constants
- `backend/graph.py` — graph compilation only
- `backend/api/schemas.py` — CoSolveRequest, CoSolveResponse
- `backend/workflow/routing.py` — all conditional edge functions

---

## Directory Structure

```
backend/
    state.py                    ← ONE file, ONE TypedDict: IncidentGraphState
    prompts.py                  ← ALL prompts as module-level string constants
    tools.py                    ← ALL @tool functions wrapping retrieval logic
    llm.py                      ← unchanged — get_llm() with lru_cache
    graph.py                    ← compiles and wires the graph, nothing else
    tracing.py                  ← LangSmith placeholder (Langfuse removed)
    config.py                   ← unchanged
    app.py                      ← FastAPI startup only, no node wiring
    api/
        schemas.py              ← CoSolveRequest, CoSolveResponse
        routes.py               ← /ask only, envelope translation
    workflow/
        nodes/                  ← 17 files, one function each
            start_node.py
            context_node.py
            intent_classification_node.py
            question_readiness_node.py
            router_node.py
            operational_node.py
            operational_reflection_node.py
            operational_escalation_node.py
            similarity_node.py
            similarity_reflection_node.py
            strategy_node.py
            strategy_reflection_node.py
            strategy_escalation_node.py
            kpi_node.py
            kpi_reflection_node.py
            response_formatter_node.py
            end_node.py
        routing.py              ← all conditional edge functions
        services/               ← unchanged (knowledge_formatter etc)
        node_parsing_utils.py   ← unchanged
    retrieval/
        models.py               ← unchanged
    infra/                      ← unchanged entirely
    ingestion/                  ← unchanged entirely
    utils/                      ← unchanged
```

---

## State

One class. One file. All graph fields here.
Nodes return dict slices — only the keys they update.
No Pydantic output models. No .model_dump(). No cast().

```python
# backend/state.py
from __future__ import annotations
from typing import TypedDict

class IncidentGraphState(TypedDict, total=False):
    # Envelope fields — set from CoSolveRequest
    case_id: str | None
    question: str
    session_id: str | None
    # Context
    case_context: dict | None
    case_status: str | None
    current_d_state: str | None
    # Routing
    classification: dict | None
    route: str | None
    question_ready: bool
    clarifying_question: str | None
    # Node outputs — plain dicts only
    operational_draft: dict | None
    operational_result: dict | None
    operational_reflection: dict | None
    operational_escalated: bool
    similarity_draft: dict | None
    similarity_result: dict | None
    similarity_reflection: dict | None
    similarity_escalated: bool
    strategy_draft: dict | None
    strategy_result: dict | None
    strategy_reflection: dict | None
    strategy_escalated: bool
    kpi_metrics: dict | None
    kpi_interpretation: dict | None
    final_response: dict | None
    _last_node: str
```

---

## Tools

The HybridRetriever contains sophisticated hybrid search logic
(BM25 + vector + embeddings + score thresholds + field mapping).
This logic is KEPT INTACT — it is NOT replaced with AzureAISearchRetriever.

What changes: HybridRetriever class is dissolved. Its methods become
module-level @tool functions. The search client instances become
module-level singletons in tools.py.

Tool docstrings are mandatory — they are what the LLM reads to reason
about which tool to call. They must be precise and scoped.

```python
# backend/tools.py

# Singletons
_case_client = CaseSearchClient(...)
_evidence_client = EvidenceSearchClient(...)
_knowledge_client = KnowledgeSearchClient(...)
_embedding_client = EmbeddingClient(...)

@tool
def search_similar_cases(query: str, case_id: str | None = None, country: str | None = None) -> list[dict]:
    """Search closed incident cases by hybrid BM25 + vector similarity.
    Use when the question asks about past incidents, precedents, or failure patterns."""
    ...

@tool
def search_knowledge_base(query: str, cosolve_phase: str | None = None) -> list[dict]:
    """Search the strategic knowledge base for best practices and guidance.
    Use when the question asks for strategy, methodology, or general knowledge."""
    ...

@tool
def search_evidence(case_id: str) -> list[dict]:
    """Retrieve evidence documents for a specific case.
    Use when the question asks for reports, photos, or findings from a case."""
    ...

@tool
def search_cases_for_kpi(country: str | None = None) -> list[dict]:
    """Retrieve cases for KPI and trend analysis.
    Use when the question asks about metrics, frequencies, or fleet-wide patterns."""
    ...
```

---

## Nodes

One file. One module-level function. No class. No __init__. No injection.
Prompt imported from prompts.py. LLM from get_llm(). Tools from tools.py.

```python
# backend/workflow/nodes/similarity_node.py
from backend.state import IncidentGraphState
from backend.llm import get_llm
from backend.prompts import SIMILARITY_SYSTEM_PROMPT
from backend.tools import search_similar_cases, search_knowledge_base
import json

def similarity_node(state: IncidentGraphState) -> dict:
    llm = get_llm(deployment="gpt-4o", temperature=0.2)
    # ... build prompt, invoke llm with tools
    return {"similarity_draft": result}   # dict slice only
```

Reflection nodes are identical in structure — just another function.
No base class. No inheritance. No special treatment.

---

## Prompts

All prompts in backend/prompts.py as module-level string constants.
Node files import — never define inline.

```python
# backend/prompts.py
SIMILARITY_SYSTEM_PROMPT = """..."""   # moved from SimilarityNode._SIMILARITY_SYSTEM_PROMPT
SIMILARITY_REFLECTION_PROMPT = """..."""
OPERATIONAL_SYSTEM_PROMPT = """..."""
# one constant per node
```

---

## LLM Selection

| Node type | Deployment | Temperature |
|---|---|---|
| intent_classification, router, question_readiness | gpt-4o-mini | 0.0 |
| similarity, operational, strategy, kpi | gpt-4o | 0.2 |
| All reflection nodes | gpt-4o | 0.0 |
| All escalation nodes | gpt-4o | 0.4 |
| response_formatter | gpt-4o | 0.3 |

---

## API Contract

routes.py only: validate request → translate to state → run graph → translate to response.
IncidentGraphState never leaves the backend.
CoSolveRequest/CoSolveResponse never enter the graph.

---

## Memory Model (2 workers recommended)

Startup per worker:
- compiled_graph — 1 instance
- LLM instances — 1 per (deployment, temperature) via lru_cache
- Tool singletons — 1 per search client, module-level in tools.py

Per request:
- IncidentGraphState — 1 dict, lives for graph invocation, then GC'd
- Zero node objects — functions have no instance cost
