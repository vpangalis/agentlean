from __future__ import annotations

from backend.ai.model_strategy import ModelStrategy


class ModelPolicy:
    def __init__(self, model_strategy: ModelStrategy):
        self._strategy = model_strategy

    def resolve_model(self, node_name: str, state: dict) -> str:
        if node_name == "operational":
            if state.get("operational_escalated") is True:
                return self._strategy.operational_premium
            return self._strategy.operational_default

        if node_name == "strategy":
            if state.get("strategy_escalated") is True:
                return self._strategy.strategy_premium
            return self._strategy.strategy_default

        return self._strategy.intent_default


__all__ = ["ModelPolicy"]
