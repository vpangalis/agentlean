from __future__ import annotations

from typing import Any

from backend.ai.model_policy import ModelPolicy
from backend.workflow.models import OperationalNodeOutput
from backend.workflow.nodes.operational_node import OperationalNode


class OperationalEscalationNode:
    def __init__(
        self,
        operational_node: OperationalNode,
        model_policy: ModelPolicy,
    ) -> None:
        self._operational_node = operational_node
        self._model_policy = model_policy

    def run(
        self,
        question: str,
        case_id: str,
        case_context: dict[str, Any],
        current_d_state: str | None,
        state: dict[str, Any],
    ) -> OperationalNodeOutput:
        state["operational_escalated"] = True
        model_name = self._model_policy.resolve_model("operational", state)
        return self._operational_node.run(
            question=question,
            case_id=case_id,
            case_context=case_context,
            current_d_state=current_d_state,
            model_name=model_name,
        )


__all__ = ["OperationalEscalationNode"]
