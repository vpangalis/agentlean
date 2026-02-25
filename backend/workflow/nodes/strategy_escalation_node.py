from __future__ import annotations

from typing import Any

from backend.ai.model_policy import ModelPolicy
from backend.workflow.models import StrategyNodeOutput
from backend.workflow.nodes.strategy_node import StrategyNode


class StrategyEscalationNode:
    def __init__(
        self,
        strategy_node: StrategyNode,
        model_policy: ModelPolicy,
    ) -> None:
        self._strategy_node = strategy_node
        self._model_policy = model_policy

    def run(
        self,
        question: str,
        country: str | None,
        state: dict[str, Any],
    ) -> StrategyNodeOutput:
        model_name = self._model_policy.resolve_model("strategy", state)
        return self._strategy_node.run_with_model_override(
            question=question,
            country=country,
            model_name=model_name,
            state=state,
        )


__all__ = ["StrategyEscalationNode"]
