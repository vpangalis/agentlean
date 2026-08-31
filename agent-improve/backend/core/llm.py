# backend/core/llm.py
"""Single source of truth for all LangChain LLM instances in Agent Improve.

All nodes import from here — never instantiate AzureChatOpenAI inline.
"""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
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
    "coach": settings.LLM_PREMIUM_DEPLOYMENT,
}


class LLMProvider:
    """Factory for cached AzureChatOpenAI instances."""

    @lru_cache(maxsize=16)
    def get_llm(
        self, deployment: str | None = None, temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AzureChatOpenAI:
        """Return a cached AzureChatOpenAI instance per
        (deployment, temperature, max_tokens) tuple."""
        return AzureChatOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_deployment=deployment or settings.LLM_REASONING_DEPLOYMENT,
            api_version=os.environ.get(
                "AZURE_OPENAI_API_VERSION", settings.AZURE_OPENAI_API_VERSION
            ),
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=3,
        )


# ── Module-level singleton ──

llm_provider = LLMProvider()


def get_llm(role: str | None = None, temperature: float = 0.2,
            max_tokens: int | None = None) -> AzureChatOpenAI:
    """Resolve a logical role name to an Azure deployment and return a cached LLM.

    Roles:
      "intent"     — fast, cheap model for classification and routing
      "reasoning"  — operational model for analysis, reflection, formatting
      "premium"    — premium model for escalation and hard reasoning
      "extraction" — operational model used for phase input extraction
      "coach"      — premium model for structured Black Belt coaching turns

    Pass max_tokens to lift the response cap (e.g. 1500 for coaching turns);
    None leaves the Azure default in place.

    Falls back to treating the value as a literal deployment name when no role matches.
    """
    resolved = _ROLE_MAP.get(role, role) if role else None
    return llm_provider.get_llm(
        deployment=resolved, temperature=temperature, max_tokens=max_tokens
    )


def block_text(message: BaseMessage) -> str:
    """Return a model response's text, read from its TYPED content blocks.

    CLAUDE.md §4.5 · reference §21: read `response.content_blocks`.
    String-indexing or substring-parsing the raw `content` field is a
    violation — it breaks the moment a provider returns a multi-part
    response. The returned text is stripped, which is what all callers want.

    **Not `message.text`.** That accessor reads `self.content` directly
    (verified against the pinned langchain-core 1.6.0), so it IS the raw-
    content path §4.5 bans, and it skips the provider translator that
    `content_blocks` runs to normalise Azure output into standard blocks.

    langchain-core ships no blocks-to-text helper of its own (checked
    2026-08-31 against 1.6.0), so this thin adapter over the primitive is
    §0.24's declared framework-gap case, not a reinvention of one. It is
    the single place the extraction is defined — 20 call sites read it.
    """
    return "".join(
        block["text"]
        for block in message.content_blocks
        if block["type"] == "text"
    ).strip()
