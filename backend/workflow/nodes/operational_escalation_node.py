from __future__ import annotations

from typing import Any

from backend.state import IncidentGraphState
from backend.config import Settings
from backend.ai.model_policy import ModelPolicy
from backend.workflow.nodes.operational_node import _run_operational
from backend.workflow.models import OperationalNodeOutput
from backend.workflow.nodes.operational_node import OperationalNode

_model_policy = ModelPolicy(Settings())


def operational_escalation_node(state: IncidentGraphState) -> dict:
    """Re-run operational reasoning with a premium model after reflection failure."""
    model_name = _model_policy.resolve_model("operational", state)
    result = _run_operational(state, model_name=model_name)
    result["operational_escalated"] = True
    result["_last_node"] = "operational_escalation_node"
    return result


# DEPRECATED: replaced by operational_escalation_node() function above — remove in Phase 8
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
        case_status: str | None = None,
    ) -> OperationalNodeOutput:
        state["operational_escalated"] = True
        model_name = self._model_policy.resolve_model("operational", state)
        return self._operational_node.run(
            question=question,
            case_id=case_id,
            case_context=case_context,
            current_d_state=current_d_state,
            model_name=model_name,
            case_status=case_status,
        )


__all__ = ["OperationalEscalationNode"]
