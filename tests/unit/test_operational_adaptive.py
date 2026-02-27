from __future__ import annotations
from typing import Any

from backend.ai.model_policy import ModelPolicy
from backend.ai.model_strategy import ModelStrategy
from backend.ai.escalation_controller import EscalationController
from backend.workflow.models import (
    ReflectionResult,
    OperationalDraftPayload,
    OperationalReflectionOutput,
    OperationalGuidance,
)
from backend.workflow.nodes.operational_escalation_node import OperationalEscalationNode
from backend.workflow.nodes.operational_node import OperationalNode
from backend.workflow.nodes.operational_reflection_node import OperationalReflectionNode


class MockSettings:
    MODEL_INTENT_CLASSIFIER = "intent-model"
    MODEL_OPERATIONAL = "operational-model"
    MODEL_OPERATIONAL_PREMIUM = "operational-premium"
    MODEL_STRATEGY = "operational-model"
    MODEL_STRATEGY_PREMIUM = "operational-premium"
    AZURE_OPENAI_CHAT_DEPLOYMENT = "operational-model"


class MockRetriever:
    def retrieve_similar_cases(
        self, query: str, current_case_id: str, country: str | None
    ) -> list[Any]:
        return []

    def retrieve_evidence_for_case(self, case_id: str) -> list[Any]:
        return []


class MockLLMClient:
    def __init__(self, default_model_name: str):
        self._default_model_name = default_model_name
        self.last_model_used: str | None = None
        self.call_count: int = 0

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type,
        temperature: float = 0.1,
        user_question: str | None = None,
        model_name: str | None = None,
        model_name_override: str | None = None,
    ) -> Any:
        self.last_model_used = (
            model_name or model_name_override or self._default_model_name
        )
        self.call_count += 1
        name = response_model.__name__

        if name == "OperationalReasoningDraft":
            return response_model(
                current_state="D1_2",
                current_state_recommendations="Isolate affected batch immediately.",
                next_state_preview="Move to D3: identify root cause via 5-Why.",
            )

        if name == "OperationalReflectionAssessment":
            return response_model(
                schema_valid=True,
                completeness_score=0.85,
                hallucination_risk="LOW",
                should_regenerate=False,
                issues=[],
            )

        raise ValueError(f"MockLLMClient: unexpected response_model {name}")


class MockLLMClientLowQuality(MockLLMClient):
    def complete_json(self, *args, **kwargs) -> Any:
        response_model = kwargs.get("response_model") or args[2]
        self.call_count += 1
        name = response_model.__name__

        if name == "OperationalReasoningDraft":
            self.last_model_used = kwargs.get("model_name") or self._default_model_name
            return response_model(
                current_state="D1_2",
                current_state_recommendations="Check things.",
                next_state_preview="",
            )

        if name == "OperationalReflectionAssessment":
            return response_model(
                schema_valid=False,
                completeness_score=0.3,
                hallucination_risk="HIGH",
                should_regenerate=True,
                issues=["Incomplete recommendations", "Missing next state"],
            )

        if name == "OperationalReflectionRegeneration":
            return response_model(
                current_state_recommendations="Isolate and contain batch before root cause.",
                next_state_preview="Proceed to D3 after containment confirmed.",
            )

        raise ValueError(f"MockLLMClientLowQuality: unexpected {name}")


def test_operational_node_returns_output() -> None:
    settings = MockSettings()
    llm = MockLLMClient(settings.MODEL_OPERATIONAL)
    node = OperationalNode(MockRetriever(), llm, settings)

    result = node.run(
        question="What should we do now?",
        case_id="CASE-001",
        case_context={"organization_country": "GR"},
        current_d_state="D1_2",
    )

    assert result.operational_draft is not None
    assert result.operational_draft.current_state == "D1_2"
    assert len(result.operational_draft.current_state_recommendations) > 0


def test_operational_node_uses_default_model() -> None:
    settings = MockSettings()
    llm = MockLLMClient(settings.MODEL_OPERATIONAL)
    node = OperationalNode(MockRetriever(), llm, settings)

    node.run(
        question="What should we do now?",
        case_id="CASE-001",
        case_context={"organization_country": "GR"},
        current_d_state="D1_2",
    )

    assert llm.last_model_used == settings.MODEL_OPERATIONAL


def test_operational_node_override_uses_given_model() -> None:
    settings = MockSettings()
    llm = MockLLMClient(settings.MODEL_OPERATIONAL)
    node = OperationalNode(MockRetriever(), llm, settings)

    node.run(
        question="What next?",
        case_id="CASE-001",
        case_context={"organization_country": "GR"},
        current_d_state="D3",
        model_name=settings.MODEL_OPERATIONAL_PREMIUM,
    )

    assert llm.last_model_used == settings.MODEL_OPERATIONAL_PREMIUM


def test_operational_node_extracts_country_from_d_states() -> None:
    settings = MockSettings()
    llm = MockLLMClient(settings.MODEL_OPERATIONAL)
    node = OperationalNode(MockRetriever(), llm, settings)

    result = node.run(
        question="What should we do?",
        case_id="CASE-002",
        case_context={"d_states": {"D1_2": {"data": {"country": "FR"}}}},
        current_d_state="D1_2",
    )

    assert result.operational_draft is not None


def test_reflection_node_returns_high_quality_result() -> None:
    llm = MockLLMClient("operational-model")
    node = OperationalReflectionNode(llm, llm)

    draft = OperationalDraftPayload(
        current_state="D1_2",
        current_state_recommendations="Isolate affected batch immediately.",
        next_state_preview="Move to D3.",
        supporting_cases=[],
        referenced_evidence=[],
    )

    output = node.run(question="What should we do?", draft=draft)

    assert output.operational_reflection.quality_score >= 0.65
    assert output.operational_reflection.needs_escalation is False
    assert output.operational_result.current_state == "D1_2"


def test_reflection_node_sets_needs_escalation_on_low_quality() -> None:
    llm = MockLLMClientLowQuality("operational-model")
    node = OperationalReflectionNode(llm, llm)

    draft = OperationalDraftPayload(
        current_state="D1_2",
        current_state_recommendations="Check things.",
        next_state_preview="",
        supporting_cases=[],
        referenced_evidence=[],
    )

    output = node.run(question="What should we do?", draft=draft)

    assert output.operational_reflection.needs_escalation is True
    assert output.operational_reflection.quality_score < 0.65


def test_reflection_node_regenerates_when_should_regenerate() -> None:
    llm = MockLLMClientLowQuality("operational-model")
    node = OperationalReflectionNode(llm, llm)

    draft = OperationalDraftPayload(
        current_state="D1_2",
        current_state_recommendations="Check things.",
        next_state_preview="",
        supporting_cases=[],
        referenced_evidence=[],
    )

    output = node.run(question="What should we do?", draft=draft)

    assert "contain" in output.operational_result.current_state_recommendations.lower()


def test_escalation_node_sets_escalated_flag() -> None:
    settings = MockSettings()
    llm = MockLLMClient(settings.MODEL_OPERATIONAL)
    node = OperationalNode(MockRetriever(), llm, settings)
    policy = ModelPolicy(ModelStrategy(settings))
    escalation_node = OperationalEscalationNode(node, policy)

    state: dict[str, Any] = {
        "operational_reflection": {"needs_escalation": True},
        "operational_escalated": False,
    }

    escalation_node.run(
        question="What should we do?",
        case_id="CASE-001",
        case_context={"organization_country": "GR"},
        current_d_state="D1_2",
        state=state,
    )

    assert state["operational_escalated"] is True


def test_escalation_node_uses_premium_model() -> None:
    settings = MockSettings()
    llm = MockLLMClient(settings.MODEL_OPERATIONAL)
    node = OperationalNode(MockRetriever(), llm, settings)
    policy = ModelPolicy(ModelStrategy(settings))
    escalation_node = OperationalEscalationNode(node, policy)

    state: dict[str, Any] = {
        "operational_reflection": {"needs_escalation": True},
        "operational_escalated": False,
    }

    escalation_node.run(
        question="What should we do?",
        case_id="CASE-001",
        case_context={"organization_country": "GR"},
        current_d_state="D1_2",
        state=state,
    )

    assert llm.last_model_used == settings.MODEL_OPERATIONAL_PREMIUM


def test_full_escalation_flow() -> None:
    settings = MockSettings()
    llm = MockLLMClientLowQuality(settings.MODEL_OPERATIONAL)
    node = OperationalNode(MockRetriever(), llm, settings)
    policy = ModelPolicy(ModelStrategy(settings))
    escalation_node = OperationalEscalationNode(node, policy)
    reflection_node = OperationalReflectionNode(llm, llm)
    controller = EscalationController()

    draft_output = node.run(
        question="Surface defect on batch A-112",
        case_id="CASE-TEST",
        case_context={"organization_country": "GR"},
        current_d_state="D3",
    )

    reflection_output = reflection_node.run(
        question="Surface defect on batch A-112",
        draft=draft_output.operational_draft,
    )

    state: dict[str, Any] = {
        "operational_reflection": reflection_output.operational_reflection,
        "operational_escalated": False,
    }
    assert controller.should_escalate_operational(state) is True

    escalation_output = escalation_node.run(
        question="Surface defect on batch A-112",
        case_id="CASE-TEST",
        case_context={"organization_country": "GR"},
        current_d_state="D3",
        state=state,
    )

    assert state["operational_escalated"] is True
    assert llm.last_model_used == settings.MODEL_OPERATIONAL_PREMIUM
