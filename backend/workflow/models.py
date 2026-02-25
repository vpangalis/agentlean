from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from backend.retrieval.models import CaseSummary, EvidenceSummary, KnowledgeSummary


class IntentClassificationResult(BaseModel):
    intent: Literal[
        "OPERATIONAL_CASE",
        "SIMILARITY_SEARCH",
        "STRATEGY_ANALYSIS",
        "KPI_ANALYSIS",
    ]
    scope: Literal["LOCAL", "COUNTRY", "GLOBAL"]
    confidence: float = Field(ge=0.0, le=1.0)


class OperationalGuidance(BaseModel):
    current_state: str
    current_state_recommendations: str
    next_state_preview: str
    supporting_cases: list[CaseSummary] = Field(default_factory=list)
    referenced_evidence: list[EvidenceSummary] = Field(default_factory=list)
    suggestions: list[dict[str, Any]] = Field(default_factory=list)


class OperationalReasoningDraft(BaseModel):
    current_state: str
    current_state_recommendations: str
    next_state_preview: str


class ScopeContext(BaseModel):
    country: Optional[str] = None

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        return normalized


class KPIMetrics(BaseModel):
    total_closed_cases: int
    min_closure_days: int | None = None
    avg_closure_days: float | None = None
    max_closure_days: int | None = None


class ReflectionVerdict(BaseModel):
    schema_valid: bool
    completeness_score: float = Field(ge=0.0, le=1.0)
    hallucination_risk: Literal["LOW", "MEDIUM", "HIGH"]
    should_regenerate: bool
    issues: list[str] = Field(default_factory=list)


class ReflectionResult(BaseModel):
    quality_score: float = Field(ge=0.0, le=1.0)
    needs_escalation: bool
    reasoning_feedback: str


class ContextNodeOutput(BaseModel):
    case_context: dict[str, Any] | None
    current_d_state: str | None


class IntentNodeOutput(BaseModel):
    classification: IntentClassificationResult


class IntentReflectionOutput(BaseModel):
    classification: IntentClassificationResult
    intent_reflection: ReflectionVerdict


class RouterNodeOutput(BaseModel):
    route: Literal[
        "OPERATIONAL_CASE",
        "SIMILARITY_SEARCH",
        "STRATEGY_ANALYSIS",
        "KPI_ANALYSIS",
    ]


class OperationalDraftPayload(BaseModel):
    current_state: str
    current_state_recommendations: str
    next_state_preview: str
    supporting_cases: list[CaseSummary] = Field(default_factory=list)
    referenced_evidence: list[EvidenceSummary] = Field(default_factory=list)
    suggestions: list[dict[str, Any]] = Field(default_factory=list)


class OperationalNodeOutput(BaseModel):
    operational_draft: OperationalDraftPayload


class OperationalReflectionOutput(BaseModel):
    operational_result: OperationalGuidance
    operational_reflection: ReflectionResult


class SimilarityDraftPayload(BaseModel):
    summary: str
    supporting_cases: list[CaseSummary] = Field(default_factory=list)
    suggestions: list[dict[str, Any]] = Field(default_factory=list)


class SimilarityNodeOutput(BaseModel):
    similarity_draft: SimilarityDraftPayload


class SimilarityResultPayload(BaseModel):
    summary: str
    supporting_cases: list[CaseSummary] = Field(default_factory=list)
    suggestions: list[dict[str, Any]] = Field(default_factory=list)


class SimilarityReflectionAssessment(BaseModel):
    case_specificity: str
    relevance_honesty: str
    pattern_quality: str
    general_advice_flagged: str
    explore_next_quality: str
    needs_regeneration: bool
    regeneration_focus: str | None = None


class SimilarityReflectionOutput(BaseModel):
    similarity_result: SimilarityResultPayload
    similarity_reflection: SimilarityReflectionAssessment


class StrategyDraftPayload(BaseModel):
    summary: str
    supporting_cases: list[CaseSummary] = Field(default_factory=list)
    supporting_knowledge: list[KnowledgeSummary] = Field(default_factory=list)
    suggestions: list[dict[str, Any]] = Field(default_factory=list)


class StrategyNodeOutput(BaseModel):
    strategy_draft: StrategyDraftPayload


class StrategyResultPayload(BaseModel):
    summary: str
    strategic_recommendations: list[str] = Field(default_factory=list)
    supporting_cases: list[CaseSummary] = Field(default_factory=list)
    supporting_knowledge: list[KnowledgeSummary] = Field(default_factory=list)
    suggestions: list[dict[str, Any]] = Field(default_factory=list)


class StrategyReflectionOutput(BaseModel):
    strategy_result: StrategyResultPayload
    strategy_reflection: ReflectionResult
    strategy_fail_section: str = ""
    strategy_fail_reason: str = ""


class KPINodeOutput(BaseModel):
    kpi_metrics: KPIMetrics


class KPIInterpretation(BaseModel):
    summary: str
    insights: list[str] = Field(default_factory=list)
    metrics: KPIMetrics


class KPIReflectionOutput(BaseModel):
    kpi_interpretation: KPIInterpretation
    kpi_reflection: ReflectionVerdict


class FinalResponsePayload(BaseModel):
    timestamp: str
    classification: IntentClassificationResult | None
    result: dict[str, Any]


class ResponseFormatterOutput(BaseModel):
    final_response: FinalResponsePayload


__all__ = [
    "IntentClassificationResult",
    "OperationalGuidance",
    "OperationalReasoningDraft",
    "ScopeContext",
    "KPIMetrics",
    "ReflectionVerdict",
    "ReflectionResult",
    "ContextNodeOutput",
    "IntentNodeOutput",
    "IntentReflectionOutput",
    "RouterNodeOutput",
    "OperationalDraftPayload",
    "OperationalNodeOutput",
    "OperationalReflectionOutput",
    "SimilarityDraftPayload",
    "SimilarityNodeOutput",
    "SimilarityResultPayload",
    "SimilarityReflectionAssessment",
    "SimilarityReflectionOutput",
    "StrategyDraftPayload",
    "StrategyNodeOutput",
    "StrategyResultPayload",
    "StrategyReflectionOutput",
    "KPINodeOutput",
    "KPIInterpretation",
    "KPIReflectionOutput",
    "FinalResponsePayload",
    "ResponseFormatterOutput",
]
