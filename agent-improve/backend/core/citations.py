"""Citation models for Agent Improve.

Single definition site for CitationRecord and CitationBundle.
Used by all nodes that produce or consume citations.
"""
from __future__ import annotations

from pydantic import BaseModel


class CitationRecord(BaseModel):
    """One citation produced by an agent turn."""

    agent_origin: str       # "agent_resolve" | "agent_improve"
    index_name: str         # e.g. "case_index_v3"
    document_id: str        # document identifier from search result
    relevance_summary: str  # plain language explanation of why this was cited
    relevance_score: float | None = None


class CitationBundle(BaseModel):
    """All citations produced in one agent turn."""

    turn: int
    citations: list[CitationRecord] = []
