from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from backend.core.state import IncidentGraphState
from backend.core.llm import get_llm
from backend.knowledge.tools import search_knowledge_base
from backend.reasoning.services.knowledge_formatter import build_refs_block

_logger = logging.getLogger("knowledge_node")

_KNOWLEDGE_SYSTEM_PROMPT = (
    "You are a technical knowledge advisor. Answer the user's question using ONLY "
    "the retrieved knowledge documents below.\n\n"
    "Rules:\n"
    "- Quote or paraphrase only what the documents actually say.\n"
    "- If the documents do not address the question, say so plainly and stop.\n"
    "- Cite the source document name when stating a fact, e.g. 'Per NSK Bearing Manual: ...'.\n"
    "- Plain text only. No JSON. No markdown headers.\n"
    "- Be concise — target 200-300 words.\n"
    "- Do not include a [KNOWLEDGE REFERENCES] block — that is appended separately."
)


def knowledge_node(state: IncidentGraphState) -> dict:
    """Answer document/manual/spec questions from the knowledge index."""
    question = (state.get("question") or "").strip()

    knowledge_docs = search_knowledge_base.invoke({"query": question, "top_k": 6})
    _logger.info("[knowledge_node] retrieval → %d docs", len(knowledge_docs))

    if not knowledge_docs:
        summary = (
            "No relevant knowledge documents were found for this question. "
            "Try rephrasing with the document name or a more specific term."
        )
        return {
            "knowledge_result": {"summary": summary, "supporting_knowledge": []},
            "_last_node": "knowledge_node",
        }

    knowledge_block = "\n".join(
        f"Per {(getattr(item, 'source', None) or getattr(item, 'doc_id', ''))}"
        f"{(' [' + getattr(item, 'section_title', '') + ']') if getattr(item, 'section_title', None) else ''}: "
        f"{(getattr(item, 'content_text', '') or '')[:600]}"
        for item in knowledge_docs
    )

    user_prompt = (
        f"USER QUESTION: {question}\n\n"
        "--- RETRIEVED KNOWLEDGE DOCUMENTS ---\n"
        f"{knowledge_block}"
    )

    llm = get_llm("reasoning", 0.2)
    response_text = llm.invoke([
        SystemMessage(content=_KNOWLEDGE_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]).content

    refs = build_refs_block(knowledge_docs)
    summary = response_text + "\n\n[KNOWLEDGE REFERENCES]\n" + refs

    return {
        "knowledge_result": {
            "summary": summary,
            "supporting_knowledge": [_to_dict(k) for k in knowledge_docs],
        },
        "_last_node": "knowledge_node",
    }


def _to_dict(obj) -> dict:
    if isinstance(obj, dict):
        return obj
    try:
        return dict(obj)
    except Exception:
        return vars(obj)
