from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RootCause(BaseModel):
    description: str = Field(..., description="Plain language root cause statement")
    evidence: str = Field(..., description="What data or analysis supports this")
    verified: bool = Field(..., description="True if statistically verified")


class HypothesisTest(BaseModel):
    test_name: str = Field(..., description="e.g. chi-square, t-test, correlation")
    result: str = Field(..., description="Plain language result")
    significant: bool = Field(..., description="True if statistically significant")


class AnalysePhaseInput(BaseModel):
    """Gate model for Analyse phase — root cause identification and verification."""

    root_causes: list[RootCause] = Field(
        ...,
        min_length=1,
        description="At least one verified root cause",
    )
    hypothesis_tests: list[HypothesisTest] = Field(
        default_factory=list,
        description="Statistical tests run — empty if graphical analysis only",
    )
    primary_root_cause: str = Field(
        ...,
        description="Single plain language statement of the main root cause",
    )
    process_owner_agrees: bool = Field(
        ..., description="Process owner has confirmed the root cause"
    )
    fmea_updated: bool = Field(..., description="FMEA updated to reflect findings")
    analysis_tools_used: list[str] = Field(
        ...,
        min_length=1,
        description="e.g. fishbone, 5why, pareto, regression",
    )
