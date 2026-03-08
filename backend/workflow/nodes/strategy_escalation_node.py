from __future__ import annotations

from typing import Any

from backend.state import IncidentGraphState
from backend.config import Settings
from backend.ai.model_policy import ModelPolicy
from backend.workflow.nodes.strategy_node import _run_strategy
from backend.workflow.models import StrategyNodeOutput
from backend.workflow.nodes.strategy_node import StrategyNode

_model_policy = ModelPolicy(Settings())


def strategy_escalation_node(state: IncidentGraphState) -> dict:
    """Re-run strategy reasoning with a premium model after reflection failure."""
    model_name = _model_policy.resolve_model("strategy", state)
    result = _run_strategy(state, model_name=model_name)
    result["_last_node"] = "strategy_escalation_node"
    return result


# DEPRECATED: replaced by strategy_escalation_node() function above — remove in Phase 8
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
        return self._strategy_node.run(
            question=question,
            country=country,
            model_name=model_name,
            state=state,
        )


__all__ = ["StrategyEscalationNode"]
