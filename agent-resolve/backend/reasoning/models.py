"""
reasoning/models.py — Structured output schemas for reflection nodes.

Used exclusively by: reasoning/nodes/*_reflection_node.py
Rule: do NOT import these from gateway or knowledge.
"""
from __future__ import annotations

from pydantic import BaseModel


class OperationalReflectionAssessment(BaseModel):
    case_grounding: str  # GROUNDED | GENERIC | MIXED
    gap_detection: str  # SPECIFIC | VAGUE | MISSING
    next_state_relevance: str  # CONNECTED | DISCONNECTED | MISSING
    general_advice_flagged: str  # PRESENT_FLAGGED | PRESENT_UNFLAGGED | MISSING
    explore_next_quality: str  # SPECIFIC_MULTI_DOMAIN | GENERIC | INCOMPLETE | MISSING
    should_regenerate: bool
    issues: list[str]


class SimilarityReflectionAssessment(BaseModel):
    case_specificity: str
    relevance_honesty: str
    pattern_quality: str
    general_advice_flagged: str
    explore_next_quality: str
    needs_regeneration: bool
    regeneration_focus: str | None = None


class StrategyReflectionAssessment(BaseModel):
    portfolio_breadth: str  # PASS | FAIL
    pattern_specificity: str  # PASS | FAIL
    weakness_strength: str  # PASS | FAIL
    knowledge_grounding: str  # PASS | FAIL
    explore_next_quality: str  # PASS | FAIL
    overall: str  # PASS | FAIL
    fail_section: str  # exact section label or NONE
    fail_reason: str  # one sentence or NONE


__all__ = [
    "OperationalReflectionAssessment",
    "SimilarityReflectionAssessment",
    "StrategyReflectionAssessment",
]
