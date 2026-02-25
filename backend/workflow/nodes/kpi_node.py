from __future__ import annotations

from backend.config import Settings
from backend.tools.kpi_tool import KPIAnalyticsTool
from backend.workflow.models import KPINodeOutput


class KPINode:
    def __init__(self, kpi_tool: KPIAnalyticsTool, settings: Settings) -> None:
        self._kpi_tool = kpi_tool
        self._settings = settings

    def run(self, country: str | None) -> KPINodeOutput:
        return KPINodeOutput(
            kpi_metrics=self._kpi_tool.calculate_metrics(country=country)
        )


__all__ = ["KPINode"]
