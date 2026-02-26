from __future__ import annotations

import logging

from backend.infra.llm_logging_client import LoggedLanguageModelClient
from backend.workflow.models import (
    IntentClassificationResult,
    QuestionReadinessNodeOutput,
    QuestionReadinessResult,
)

_logger = logging.getLogger(__name__)


class QuestionReadinessNode:
    """Decide whether the system has enough context to give a grounded answer.

    Runs immediately after IntentClassificationNode.  Returns ``question_ready``
    (bool) and ``clarifying_question`` (str).  When not ready the graph exits
    early and the entry handler surfaces the clarifying question to the user.

    Architectural rules (non-negotiable):
    - Module level contains ONLY imports, __all__, and this logger instance.
    - Every prompt string, constant, and keyword tuple lives inside the class.
    - Prompt strings are class-level attributes, not instance attributes.
    - ``run()`` is the single public entry point; all helpers are private (_).
    """

    # ── Class-level prompt attributes ────────────────────────────────────

    _SYSTEM_PROMPT = (
        "You decide whether a decision-support system has enough context to give "
        "a meaningful, grounded answer to the user's question. "
        "Return strict JSON only — no explanation, no markdown."
    )

    _READY_DESCRIPTION = (
        "Return {\"ready\": true, \"clarifying_question\": \"\"} when the question "
        "is sufficiently specific and the available context supports a grounded answer. "
        "Return {\"ready\": false, \"clarifying_question\": \"<one short question>\"} "
        "when essential context is missing. "
        "The clarifying_question must be a single, plain conversational sentence "
        "addressed directly to the user — it must never mention intents, nodes, "
        "classification, routing, or any technical term."
    )

    # ── Not-ready trigger keywords (for operational intent, no case loaded) ─

    _OPERATIONAL_NO_CASE_KEYWORDS: tuple[str, ...] = (
        "next step",
        "what should we",
        "what to do",
        "how complete",
        "investigation",
        "root cause",
        "corrective action",
        "gap",
        "status of",
        "focus on",
        "containment",
        "d3",
        "d4",
        "d5",
        "d6",
        "d7",
        "d8",
    )

    def __init__(self, llm_client: LoggedLanguageModelClient) -> None:
        self._llm_client = llm_client

    def run(
        self,
        question: str,
        classification: IntentClassificationResult,
        case_id: str | None,
        case_context: dict | None,
    ) -> QuestionReadinessNodeOutput:
        """Assess whether enough context exists to answer the question.

        Uses a fast LLM call (max_tokens=200).  Falls back to ``ready=True``
        on any error so the graph always continues rather than blocking silently.
        """
        clean_question = (question or "").strip()
        if not clean_question:
            return QuestionReadinessNodeOutput(
                question_ready=False,
                clarifying_question="What would you like to know? Please describe your question.",
            )

        # Fast-path: non-operational intents are always ready.
        if classification.intent != "OPERATIONAL_CASE":
            return QuestionReadinessNodeOutput(question_ready=True, clarifying_question="")

        case_loaded = self._is_case_loaded(case_id, case_context)

        # Fast-path: operational intent with a loaded case is always ready.
        if case_loaded:
            return QuestionReadinessNodeOutput(question_ready=True, clarifying_question="")

        # Operational intent, no case loaded — check the question heuristically
        # first; fall back to LLM only when genuinely ambiguous.
        if self._is_new_problem_question(clean_question):
            # New-problem questions can be answered without a loaded case.
            return QuestionReadinessNodeOutput(question_ready=True, clarifying_question="")

        if self._requires_case_context(clean_question):
            return QuestionReadinessNodeOutput(
                question_ready=False,
                clarifying_question=(
                    "It looks like you're asking about a specific case — "
                    "could you open the relevant case in the Case Board first "
                    "so I can give you grounded guidance?"
                ),
            )

        # Genuinely ambiguous — ask the LLM.
        return self._llm_assess(clean_question, case_loaded=False)

    # ── Private helpers ───────────────────────────────────────────────────

    @staticmethod
    def _is_case_loaded(case_id: str | None, case_context: dict | None) -> bool:
        """Return True when a real case document is available."""
        return bool(case_id and str(case_id).strip()) and isinstance(case_context, dict)

    def _is_new_problem_question(self, question: str) -> bool:
        """Return True for questions about starting a new investigation."""
        q = question.lower()
        new_problem_markers = (
            "new problem",
            "just found",
            "just discovered",
            "just identified",
            "where do we start",
            "how do we start",
            "where to start",
            "how to start",
            "open a case",
            "create a case",
        )
        return any(marker in q for marker in new_problem_markers)

    def _requires_case_context(self, question: str) -> bool:
        """Return True when the question clearly needs a loaded case document."""
        q = question.lower()
        return any(kw in q for kw in QuestionReadinessNode._OPERATIONAL_NO_CASE_KEYWORDS)

    def _llm_assess(self, question: str, *, case_loaded: bool) -> QuestionReadinessNodeOutput:
        """Call the LLM for genuinely ambiguous readiness decisions."""
        user_prompt = (
            f"{QuestionReadinessNode._READY_DESCRIPTION}\n\n"
            "=== CONTEXT ===\n"
            f"case_loaded: {'true' if case_loaded else 'false'}\n"
            f"question: {question}\n\n"
            "=== RESPOND WITH JSON ONLY ===\n"
            '{"ready": true|false, "clarifying_question": "..."}'
        )
        try:
            result: QuestionReadinessResult = self._llm_client.complete_json(
                system_prompt=QuestionReadinessNode._SYSTEM_PROMPT,
                user_prompt=user_prompt,
                response_model=QuestionReadinessResult,
                temperature=0.0,
                user_question=question,
                max_tokens=200,
            )
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "QuestionReadinessNode: LLM call failed; defaulting to ready=True. Error: %s",
                exc,
            )
            return QuestionReadinessNodeOutput(question_ready=True, clarifying_question="")

        return QuestionReadinessNodeOutput(
            question_ready=result.ready,
            clarifying_question=result.clarifying_question if not result.ready else "",
        )


__all__ = ["QuestionReadinessNode"]
