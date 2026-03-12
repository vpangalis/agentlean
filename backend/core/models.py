"""
core/models.py — Shared cross-domain Pydantic models.

Used by: gateway (API schemas), core (graph state), reasoning (nodes),
         knowledge (tools output).
Rule: import only from here for cross-domain model needs.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class IntentClassificationResult(BaseModel):
    intent: Literal[
        "OPERATIONAL_CASE",
        "SIMILARITY_SEARCH",
        "STRATEGY_ANALYSIS",
        "KPI_ANALYSIS",
    ]
    scope: Literal["LOCAL", "COUNTRY", "GLOBAL"]
    confidence: float = Field(ge=0.0, le=1.0)


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


class KPIResult(BaseModel):
    """Computed KPI metrics produced by KPITool.get_kpis().

    Contains the raw metric values plus rendering hints and follow-up
    suggestions for the frontend chips.
    """

    scope: Literal["global", "country", "case"] = "global"
    scope_label: str = "Global"
    render_hint: Literal["table", "bar_chart", "gauge", "summary_text"] = "table"
    suggestions: list[str] = Field(default_factory=list)

    # ── Common metrics (global + country) ──────────────────────────────────
    total_cases_opened_ytd: Optional[int] = None
    total_cases_closed_ytd: Optional[int] = None
    avg_closure_days_ytd: Optional[float] = None
    avg_closure_days_rolling_12m: Optional[float] = None
    recurrence_rate: Optional[float] = None
    first_closure_rate: Optional[float] = None
    overdue_count: Optional[int] = None
    overdue_pct: Optional[float] = None
    d_stage_distribution: Optional[dict[str, int]] = None
    avg_days_per_stage: Optional[dict[str, float]] = None
    monthly_opened_closed: Optional[list[dict[str, Any]]] = None

    # ── Country-scope additions ────────────────────────────────────────────
    country_ranking: Optional[list[dict[str, Any]]] = None
    active_case_load: Optional[list[dict[str, Any]]] = None
    ytd_closed_count: Optional[int] = None
    global_avg_closure_days: Optional[float] = None

    # ── Global + country scope: status counts ─────────────────────────────
    open_count: Optional[int] = None
    in_progress_count: Optional[int] = None

    # ── Case-scope additions ───────────────────────────────────────────────
    stage_timeline: Optional[list[dict]] = None
    days_elapsed: Optional[int] = None
    gauge_label: Optional[str] = None
    category_benchmark_days: Optional[float] = None
    current_stage: Optional[str] = None
    responsible_leader: Optional[str] = None
    department: Optional[str] = None
    days_stuck_at_current_stage: Optional[int] = None
    similar_cases_avg_resolution_days: Optional[float] = None

    # ── Backward-compat fields (kept so old code that reads these still works) ─
    total_closed_cases: Optional[int] = None
    min_closure_days: Optional[int] = None
    avg_closure_days: Optional[float] = None
    max_closure_days: Optional[int] = None


class QuestionReadinessResult(BaseModel):
    ready: bool
    clarifying_question: str = ""


__all__ = [
    "IntentClassificationResult",
    "ScopeContext",
    "KPIResult",
    "QuestionReadinessResult",
]
