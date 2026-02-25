from __future__ import annotations

from datetime import datetime, timezone

from backend.config import Settings
from backend.retrieval.hybrid_retriever import HybridRetriever
from backend.workflow.models import KPIMetrics


class KPIAnalyticsTool:
    def __init__(self, hybrid_retriever: HybridRetriever, settings: Settings) -> None:
        self._hybrid_retriever = hybrid_retriever
        self._settings = settings

    def calculate_metrics(self, country: str | None) -> KPIMetrics:
        cases = self._hybrid_retriever.retrieve_cases_for_kpi(country=country)
        durations: list[int] = []

        for case in cases:
            opening = self._to_datetime(case.opening_date)
            closure = self._to_datetime(case.closure_date)
            if opening is None or closure is None:
                continue
            delta = closure - opening
            if delta.days < 0:
                continue
            durations.append(delta.days)

        if not durations:
            return KPIMetrics(
                total_closed_cases=0,
                min_closure_days=None,
                avg_closure_days=None,
                max_closure_days=None,
            )

        total_days = sum(durations)
        return KPIMetrics(
            total_closed_cases=len(durations),
            min_closure_days=min(durations),
            avg_closure_days=round(total_days / len(durations), 2),
            max_closure_days=max(durations),
        )

    def _to_datetime(self, value: datetime | str | None) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return self._ensure_utc(value)
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return None
            if normalized.endswith("Z"):
                normalized = normalized.replace("Z", "+00:00")
            try:
                parsed = datetime.fromisoformat(normalized)
            except ValueError:
                return None
            return self._ensure_utc(parsed)
        return None

    def _ensure_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


__all__ = ["KPIAnalyticsTool"]
