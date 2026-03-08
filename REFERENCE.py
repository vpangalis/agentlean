"""
REFERENCE.py — CoSolve Canonical Code Patterns
Version: 2.0 — 2026-03-08

NOT executed. Read before writing any CoSolve code.
Every pattern here must be followed exactly.
"""

# =============================================================================
# 1. STATE — backend/state.py
# =============================================================================
from __future__ import annotations
from typing import TypedDict

class IncidentGraphState(TypedDict, total=False):
    """Single source of truth. All fields optional (total=False).
    Nodes return dict slices — only the keys they produce."""
    case_id: str | None
    question: str
    session_id: str | None
    case_context: dict | None
    case_status: str | None
    current_d_state: str | None
    classification: dict | None
    route: str | None
    question_ready: bool
    clarifying_question: str | None
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


# =============================================================================
# 2. TOOLS — backend/tools.py
# =============================================================================
import os
from langchain_core.tools import tool
from backend.config import Settings
from backend.infra.case_search_client import CaseSearchClient
from backend.infra.evidence_search_client import EvidenceSearchClient
from backend.infra.knowledge_search_client import KnowledgeSearchClient
from backend.infra.embeddings import EmbeddingClient

# Module-level singletons — instantiated once, shared across all nodes
_settings = Settings()
_case_client = CaseSearchClient(_settings)
_evidence_client = EvidenceSearchClient(_settings)
_knowledge_client = KnowledgeSearchClient(_settings)
_embedding_client = EmbeddingClient(_settings)

# Minimum score threshold — kept from HybridRetriever
KNOWLEDGE_MIN_SCORE = 0.5


@tool
def search_similar_cases(
    query: str,
    case_id: str | None = None,
    country: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    """Search closed incident cases by hybrid BM25 + vector similarity.
    Use when the question asks about past incidents, precedents, or failure patterns.
    Excludes the currently active case. Filters by country when provided.
    Returns case_id, problem_description, five_whys_text, permanent_actions_text."""
    embedding = _embedding_client.generate_embedding(query)
    filters = ["status eq 'closed'"]
    if case_id:
        filters.append(f"case_id ne '{case_id.replace(chr(39), chr(39)*2)}'")
    if country:
        filters.append(f"organization_country eq '{country.replace(chr(39), chr(39)*2)}'")
    results = _case_client.hybrid_search(
        search_text=query,
        embedding=embedding,
        filter_expression=" and ".join(filters),
        top_k=top_k,
    )
    return [r for r in results if r.get("case_id")]


@tool
def search_knowledge_base(
    query: str,
    cosolve_phase: str | None = None,
    top_k: int = 4,
) -> list[dict]:
    """Search the strategic knowledge base for best practices and guidance.
    Use when the question asks for methodology, strategy, or engineering knowledge.
    Filter by cosolve_phase (root_cause, corrective_action, etc.) when relevant.
    Returns doc_id, title, source, content_text, score."""
    embedding = _embedding_client.generate_embedding(query)
    results = _knowledge_client.hybrid_search(
        search_text=query,
        embedding=embedding,
        top_k=top_k,
        cosolve_phase=cosolve_phase,
    )
    return [r for r in results if (r.get("@search.score") or 0) >= KNOWLEDGE_MIN_SCORE]


@tool
def search_evidence(case_id: str, top_k: int = 5) -> list[dict]:
    """Retrieve evidence documents attached to a specific incident case.
    Use when the question asks for technical reports, photos, or findings.
    Returns filename, content_type, created_at."""
    return _evidence_client.search_by_case_id(case_id=case_id, top_k=top_k)


@tool
def search_cases_for_kpi(country: str | None = None, top_k: int = 200) -> list[dict]:
    """Retrieve closed cases for KPI and trend analysis.
    Use when the question asks about metrics, recurrence rates, or fleet patterns.
    Returns status, current_stage, opening_date, closure_date, department."""
    filters = ["status eq 'closed'"]
    if country:
        filters.append(f"organization_country eq '{country.replace(chr(39), chr(39)*2)}'")
    return _case_client.filtered_search(
        filter_expression=" and ".join(filters),
        top_k=top_k,
    )


# =============================================================================
# 3. PROMPTS — backend/prompts.py
# =============================================================================
# All prompts are module-level string constants.
# Node files import the prompt they need — never define inline.
# Prompt CONTENT is not changed during refactor — only moved here.

SIMILARITY_SYSTEM_PROMPT = """..."""   # exact content from SimilarityNode._SIMILARITY_SYSTEM_PROMPT
SIMILARITY_REFLECTION_PROMPT = """..."""
OPERATIONAL_SYSTEM_PROMPT = """..."""
OPERATIONAL_REFLECTION_PROMPT = """..."""
STRATEGY_SYSTEM_PROMPT = """..."""
STRATEGY_REFLECTION_PROMPT = """..."""
KPI_SYSTEM_PROMPT = """..."""
KPI_REFLECTION_PROMPT = """..."""
INTENT_CLASSIFICATION_PROMPT = """..."""
QUESTION_READINESS_PROMPT = """..."""
CONTEXT_PROMPT = """..."""
RESPONSE_FORMATTER_PROMPT = """..."""


# =============================================================================
# 4. NODE — backend/workflow/nodes/similarity_node.py
# =============================================================================
# One file. One function. No class. No __init__. No injection.

from backend.state import IncidentGraphState
from backend.llm import get_llm
from backend.prompts import SIMILARITY_SYSTEM_PROMPT
from backend.tools import search_similar_cases, search_knowledge_base
from backend.workflow.node_parsing_utils import extract_similarity_suggestions
from backend.workflow.services.knowledge_formatter import knowledge_formatter
from langchain_core.messages import HumanMessage, SystemMessage
import json

def similarity_node(state: IncidentGraphState) -> dict:
    """Find similar historical cases and extract patterns."""
    llm = get_llm(deployment="gpt-4o", temperature=0.2)

    # Retrieve using tools directly
    cases = search_similar_cases.invoke({
        "query": state.get("question", ""),
        "case_id": state.get("case_id"),
        "country": _resolve_country(state),
    })
    knowledge = search_knowledge_base.invoke({
        "query": state.get("question", ""),
        "cosolve_phase": "root_cause",
    })

    # Build prompt
    user_prompt = (
        f"USER QUESTION: {state.get('question', '')}\n"
        f"ACTIVE CASE STATUS: {(state.get('case_status') or 'open').lower()}\n\n"
        "--- ACTIVE CASE CONTEXT ---\n"
        f"{json.dumps(state.get('case_context') or {}, default=str)}\n\n"
        "--- RETRIEVED CLOSED CASES ---\n"
        f"{json.dumps(cases, default=str)}\n\n"
        "--- KNOWLEDGE BASE REFERENCES ---\n"
        f"{json.dumps(knowledge, default=str)}"
    )

    response = llm.invoke([
        SystemMessage(content=SIMILARITY_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ])

    response_text = response.content
    suggestions = extract_similarity_suggestions(response_text)

    # Return ONLY the keys this node produces
    return {
        "similarity_draft": {
            "summary": response_text,
            "supporting_cases": cases,
            "suggestions": suggestions,
        },
        "_last_node": "similarity_node",
    }

def _resolve_country(state: IncidentGraphState) -> str | None:
    """Extract country from question if present."""
    classification = state.get("classification") or {}
    if isinstance(classification, dict) and classification.get("scope") == "GLOBAL":
        return None
    question = state.get("question", "")
    marker = "country:"
    idx = question.lower().find(marker)
    if idx < 0:
        return None
    return question[idx + len(marker):].strip().split()[0].strip(",.;") or None


# =============================================================================
# 5. REFLECTION NODE — backend/workflow/nodes/similarity_reflection_node.py
# =============================================================================
# Reflection is just another function — same pattern, different prompt.

from backend.state import IncidentGraphState
from backend.llm import get_llm
from backend.prompts import SIMILARITY_REFLECTION_PROMPT
from langchain_core.messages import HumanMessage, SystemMessage
import json

def similarity_reflection_node(state: IncidentGraphState) -> dict:
    """Critically assess quality of the similarity result."""
    llm = get_llm(deployment="gpt-4o", temperature=0.0)  # strict

    draft = state.get("similarity_draft") or {}
    response = llm.invoke([
        SystemMessage(content=SIMILARITY_REFLECTION_PROMPT),
        HumanMessage(content=json.dumps(draft, default=str)),
    ])

    try:
        reflection = json.loads(response.content)
    except Exception:
        reflection = {"raw": response.content}

    return {
        "similarity_reflection": reflection,
        "_last_node": "similarity_reflection_node",
    }


# =============================================================================
# 6. ROUTING — backend/workflow/routing.py
# =============================================================================
# All conditional edge functions here. Plain functions. No class.

from backend.state import IncidentGraphState

def route_intent(state: IncidentGraphState) -> str:
    route = state.get("route")
    valid = {"OPERATIONAL_CASE", "SIMILARITY_SEARCH", "STRATEGY_ANALYSIS", "KPI_ANALYSIS"}
    return str(route) if route in valid else "SIMILARITY_SEARCH"

def route_question_readiness(state: IncidentGraphState) -> str:
    return "NOT_READY" if not state.get("question_ready", True) else "READY"

def route_operational_escalation(state: IncidentGraphState) -> str:
    case_context = state.get("case_context")
    if _extract_case_status(case_context) == "closed":
        return "CONTINUE"
    reflection = state.get("operational_reflection") or {}
    if isinstance(reflection, dict):
        score = reflection.get("quality_score", 1.0)
        if float(score) < 0.7 and not state.get("operational_escalated"):
            return "ESCALATE"
    return "CONTINUE"

def route_strategy_escalation(state: IncidentGraphState) -> str:
    reflection = state.get("strategy_reflection") or {}
    if isinstance(reflection, dict):
        score = reflection.get("quality_score", 1.0)
        if float(score) < 0.7 and not state.get("strategy_escalated"):
            return "ESCALATE"
    return "CONTINUE"

def _extract_case_status(case_context: dict | None) -> str | None:
    if not isinstance(case_context, dict):
        return None
    nested = case_context.get("case")
    if isinstance(nested, dict) and isinstance(nested.get("status"), str):
        return nested["status"].strip().lower()
    flat = case_context.get("status")
    if isinstance(flat, str):
        return flat.strip().lower()
    return None


# =============================================================================
# 7. GRAPH — backend/graph.py
# =============================================================================
# Wires everything. No business logic. No LLM calls.

from langgraph.graph import StateGraph
from backend.state import IncidentGraphState
from backend.workflow.nodes.start_node import start_node
from backend.workflow.nodes.context_node import context_node
from backend.workflow.nodes.intent_classification_node import intent_classification_node
from backend.workflow.nodes.question_readiness_node import question_readiness_node
from backend.workflow.nodes.router_node import router_node
from backend.workflow.nodes.operational_node import operational_node
from backend.workflow.nodes.operational_reflection_node import operational_reflection_node
from backend.workflow.nodes.operational_escalation_node import operational_escalation_node
from backend.workflow.nodes.similarity_node import similarity_node
from backend.workflow.nodes.similarity_reflection_node import similarity_reflection_node
from backend.workflow.nodes.strategy_node import strategy_node
from backend.workflow.nodes.strategy_reflection_node import strategy_reflection_node
from backend.workflow.nodes.strategy_escalation_node import strategy_escalation_node
from backend.workflow.nodes.kpi_node import kpi_node
from backend.workflow.nodes.kpi_reflection_node import kpi_reflection_node
from backend.workflow.nodes.response_formatter_node import response_formatter_node
from backend.workflow.nodes.end_node import end_node
from backend.workflow.routing import (
    route_intent,
    route_question_readiness,
    route_operational_escalation,
    route_strategy_escalation,
)

def build_graph():
    graph = StateGraph(IncidentGraphState)

    # Nodes
    graph.add_node("start_node", start_node)
    graph.add_node("context_node", context_node)
    graph.add_node("intent_classification_node", intent_classification_node)
    graph.add_node("question_readiness_node", question_readiness_node)
    graph.add_node("router_node", router_node)
    graph.add_node("operational_node", operational_node)
    graph.add_node("operational_reflection_node", operational_reflection_node)
    graph.add_node("operational_escalation_node", operational_escalation_node)
    graph.add_node("similarity_node", similarity_node)
    graph.add_node("similarity_reflection_node", similarity_reflection_node)
    graph.add_node("strategy_node", strategy_node)
    graph.add_node("strategy_reflection_node", strategy_reflection_node)
    graph.add_node("strategy_escalation_node", strategy_escalation_node)
    graph.add_node("kpi_node", kpi_node)
    graph.add_node("kpi_reflection_node", kpi_reflection_node)
    graph.add_node("response_formatter_node", response_formatter_node)
    graph.add_node("end_node", end_node)

    # Entry and finish
    graph.set_entry_point("start_node")
    graph.set_finish_point("end_node")

    # Edges — topology unchanged from UnifiedIncidentGraph
    graph.add_edge("start_node", "context_node")
    graph.add_edge("context_node", "intent_classification_node")
    graph.add_edge("intent_classification_node", "question_readiness_node")
    graph.add_conditional_edges("question_readiness_node", route_question_readiness,
        {"READY": "router_node", "NOT_READY": "response_formatter_node"})
    graph.add_conditional_edges("router_node", route_intent, {
        "OPERATIONAL_CASE": "operational_node",
        "SIMILARITY_SEARCH": "similarity_node",
        "STRATEGY_ANALYSIS": "strategy_node",
        "KPI_ANALYSIS": "kpi_node",
    })
    graph.add_edge("operational_node", "operational_reflection_node")
    graph.add_conditional_edges("operational_reflection_node", route_operational_escalation,
        {"ESCALATE": "operational_escalation_node", "CONTINUE": "response_formatter_node"})
    graph.add_edge("operational_escalation_node", "operational_reflection_node")
    graph.add_edge("similarity_node", "similarity_reflection_node")
    graph.add_edge("similarity_reflection_node", "response_formatter_node")
    graph.add_edge("strategy_node", "strategy_reflection_node")
    graph.add_conditional_edges("strategy_reflection_node", route_strategy_escalation,
        {"ESCALATE": "strategy_escalation_node", "CONTINUE": "response_formatter_node"})
    graph.add_edge("strategy_escalation_node", "strategy_reflection_node")
    graph.add_edge("kpi_node", "kpi_reflection_node")
    graph.add_edge("kpi_reflection_node", "response_formatter_node")
    graph.add_edge("response_formatter_node", "end_node")

    return graph.compile()

compiled_graph = build_graph()


# =============================================================================
# 8. API SCHEMAS — backend/api/schemas.py
# =============================================================================
from pydantic import BaseModel

class CoSolveRequest(BaseModel):
    """What the UI sends. Nothing else crosses inbound."""
    question: str
    case_id: str | None = None
    session_id: str | None = None

class Source(BaseModel):
    case_id: str
    title: str
    relevance: float | None = None

class SuggestedQuestions(BaseModel):
    ask_your_team: list[str] = []
    ask_cosolve: list[str] = []

class CoSolveResponse(BaseModel):
    """What the backend returns. Nothing else crosses outbound."""
    answer: str
    intent: str
    sources: list[Source] = []
    suggested_questions: SuggestedQuestions | None = None
    warning: str | None = None


# =============================================================================
# 9. ROUTE — backend/api/routes.py
# =============================================================================
from fastapi import APIRouter
from backend.api.schemas import CoSolveRequest, CoSolveResponse, Source, SuggestedQuestions
from backend.state import IncidentGraphState
from backend.graph import compiled_graph

router = APIRouter()

@router.post("/ask", response_model=CoSolveResponse)
async def ask(request: CoSolveRequest) -> CoSolveResponse:
    # 1 — envelope → state
    state: IncidentGraphState = {
        "question": request.question,
        "case_id": request.case_id,
        "session_id": request.session_id,
    }
    # 2 — run graph
    result = compiled_graph.invoke(state)
    # 3 — state → envelope
    return _build_response(result)

def _build_response(state: IncidentGraphState) -> CoSolveResponse:
    final = state.get("final_response") or {}
    return CoSolveResponse(
        answer=final.get("answer", ""),
        intent=str(state.get("route") or ""),
        sources=[Source(**s) for s in final.get("sources", [])],
        suggested_questions=SuggestedQuestions(**final.get("suggested_questions", {}))
            if final.get("suggested_questions") else None,
        warning=final.get("warning"),
    )
