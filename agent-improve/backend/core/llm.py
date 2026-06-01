# backend/core/llm.py
"""Single source of truth for all LangChain LLM instances in Agent Improve.

All nodes import from here — never instantiate AzureChatOpenAI inline.
"""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

from backend.core.config import settings

load_dotenv(override=True)  # MUST use override=True — project requirement

# Role → Azure deployment name mapping
_ROLE_MAP: dict[str, str] = {
    "intent": settings.LLM_INTENT_DEPLOYMENT,
    "reasoning": settings.LLM_REASONING_DEPLOYMENT,
    "operational": settings.LLM_REASONING_DEPLOYMENT,
    "premium": settings.LLM_PREMIUM_DEPLOYMENT,
    "extraction": settings.LLM_REASONING_DEPLOYMENT,
}


class LLMProvider:
    """Factory for cached AzureChatOpenAI instances."""

    @lru_cache(maxsize=16)
    def get_llm(
        self, deployment: str | None = None, temperature: float = 0.2
    ) -> AzureChatOpenAI:
        """Return a cached AzureChatOpenAI instance per (deployment, temperature) pair."""
        return AzureChatOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_deployment=deployment or settings.LLM_REASONING_DEPLOYMENT,
            api_version=os.environ.get(
                "AZURE_OPENAI_API_VERSION", settings.AZURE_OPENAI_API_VERSION
            ),
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            temperature=temperature,
            max_retries=3,
        )


# ── Module-level singleton ──

llm_provider = LLMProvider()


def get_llm(role: str | None = None, temperature: float = 0.2) -> AzureChatOpenAI:
    """Resolve a logical role name to an Azure deployment and return a cached LLM.

    Roles:
      "intent"     — fast, cheap model for classification and routing
      "reasoning"  — operational model for analysis, reflection, formatting
      "premium"    — premium model for escalation and hard reasoning
      "extraction" — operational model used for phase input extraction

    Falls back to treating the value as a literal deployment name when no role matches.
    """
    resolved = _ROLE_MAP.get(role, role) if role else None
    return llm_provider.get_llm(deployment=resolved, temperature=temperature)
