"""Citation models for Agent Improve.

Single definition site for CitationRecord and CitationBundle.
Used by all nodes that produce or consume citations.
"""
from __future__ import annotations

import logging
from typing import Any, Iterable

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


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


def as_records(citations: Iterable[Any]) -> list[CitationRecord]:
    """G-176: the citations a turn kept, as records — the coach writes `CoachingResponse.citations` as free
    dicts (its sources, anchored in code to an upload's `blob_path`), so each is mapped: a record as is;
    a coach citation by its document (`document_id`, `blob_path`, `source` or `title`) and what it says
    (`relevance_summary`, `quote`, `excerpt`, `text` or `summary`). One with no document is left out and
    logged — a citation never breaks a reload or an approval."""
    out: list[CitationRecord] = []
    for c in citations:
        if isinstance(c, CitationRecord):
            out.append(c)
            continue
        if not isinstance(c, dict):
            continue
        try:
            out.append(CitationRecord(**c))
            continue
        except ValidationError:
            pass
        document = next((str(c[k]) for k in ("document_id", "blob_path", "source", "title") if c.get(k)), "")
        if not document:
            logger.warning("G-176: a citation with no document is left out: %s", str(c)[:200])
            continue
        said = next((str(c[k]) for k in ("relevance_summary", "quote", "excerpt", "text", "summary") if c.get(k)), "")
        score = c.get("relevance_score")
        out.append(CitationRecord(
            agent_origin=str(c.get("agent_origin") or "agent_improve"),
            index_name=str(c.get("index_name") or ("improve_evidence_index" if c.get("blob_path") else "")),
            document_id=document, relevance_summary=said or document,
            relevance_score=float(score) if isinstance(score, (int, float)) else None))
    return out
