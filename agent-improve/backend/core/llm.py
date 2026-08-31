# backend/core/llm.py
"""Single source of truth for all LangChain LLM instances in Agent Improve.

All nodes import from here — never instantiate `AzureChatOpenAI` inline
(CLAUDE.md §4.1 · reference §21).

**Module-level functions only.** Reference §54 and CLAUDE.md §2 name the LLM
factory explicitly among the files where no class may live, which is why the
v1 `LLMProvider` class is gone. It also carried a real bug: `@lru_cache` on a
*method* keys on `self` and keeps the instance alive for the process. The
cache is now on a module-level function, where it belongs.
"""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langchain_openai import AzureChatOpenAI

from backend.core.config import settings

load_dotenv(override=True)  # MUST use override=True — project requirement


# ── The two deployment tiers (§21) ────────────────────────────────────────
#
# §21: "Two deployment tiers, addressed by role." Two, not three. The v1 map
# addressed a third setting, LLM_INTENT_DEPLOYMENT ('intent-model'), for the
# `intent` role; §21 puts `intent` on the operational tier with the other
# cheap roles. The setting still exists in config.py and is simply no longer
# read here — removing it is config surface, not this step's business.
#
# Model tiering is a COST rule, not a style preference: gpt-4o-mini is roughly
# 15x cheaper, so only genuinely premium work is addressed to the premium tier.
PREMIUM_TIER = settings.LLM_PREMIUM_DEPLOYMENT       # operational-premium, gpt-4o
OPERATIONAL_TIER = settings.LLM_REASONING_DEPLOYMENT  # operational-model, gpt-4o-mini


# ── The eleven roles (§21 · CLAUDE.md §4.2) ───────────────────────────────
#
# This map IS the role vocabulary. A name not in it is not a role, and
# **new roles require a §56 amendment** — which is why an unknown name now
# raises instead of being passed through as a literal deployment name. That
# v1 fallback is how `get_llm("operational-premium", ...)` came to exist in
# upload/agent.py: a deployment name masquerading as a role, invisible to
# every check.
ROLE_DEPLOYMENTS: dict[str, str] = {
    # premium tier — gpt-4o
    "coach":       PREMIUM_TIER,   # Coaching content, max_tokens=1500
    "planner":     PREMIUM_TIER,   # Phase planner structured decisions
    "synthesis":   PREMIUM_TIER,   # Multi-hop synthesis (§26)
    "vision":      PREMIUM_TIER,   # Multimodal upload analysis
    # operational tier — gpt-4o-mini
    "reasoning":   OPERATIONAL_TIER,  # Default reasoning, intermediate hops
    "extraction":  OPERATIONAL_TIER,  # Field extraction
    "coherence":   OPERATIONAL_TIER,  # Layer 2a (§19.7)
    "constraint":  OPERATIONAL_TIER,  # Layer 2c (§34)
    "grader":      OPERATIONAL_TIER,  # Rubric grading (§36)
    "summarizer":  OPERATIONAL_TIER,  # Context compression (§19.3)
    "intent":      OPERATIONAL_TIER,  # Short classification
}


# ── Per-role temperature defaults (§21 temperature table) ─────────────────
#
# §21 ratifies a temperature for SEVEN of the eleven roles. Where it gives a
# band, the entry below takes the reproducible end of it. The remaining four
# — reasoning, summarizer, intent, vision — have no ratified figure, so they
# fall through to DEFAULT_TEMPERATURE rather than carry a number invented here
# that would read as ratified. Pinning one is a §56 amendment, not an edit.
DEFAULT_TEMPERATURE = 0.2

ROLE_TEMPERATURES: dict[str, float] = {
    "coach":      0.5,  # §21 band 0.5-0.7 — natural variation for the Belt
    "synthesis":  0.1,  # §21 band 0.1-0.2 — reproducible evidence assembly
    "grader":     0.1,  # HARD requirement — see below
    "coherence":  0.1,  # consistent verdicts
    "constraint": 0.1,  # consistent verdicts
    "planner":    0.1,  # deterministic decomposition
    "extraction": 0.0,  # §21 band 0.0-0.2 — field extraction and validators
}

# The grader's 0.1 is a hard requirement, not a tuning knob (§21): a grader
# that returns different verdicts across runs makes §52's regression
# thresholds meaningless — you cannot detect a 10% quality drop against a
# baseline that moves on its own. `test_llm.py` asserts it.


def role_temperature(role: str) -> float:
    """The ratified default temperature for `role`, or DEFAULT_TEMPERATURE."""
    return ROLE_TEMPERATURES.get(role, DEFAULT_TEMPERATURE)


@lru_cache(maxsize=32)
def _build_llm(
    deployment: str,
    temperature: float,
    max_tokens: int | None,
) -> AzureChatOpenAI:
    """Construct one `AzureChatOpenAI`, cached per (deployment, temperature,
    max_tokens).

    The cache is `functools.lru_cache` deliberately. LangChain ships a
    *response* cache (`langchain_core.caches.BaseCache`) and no model-INSTANCE
    cache, so there is no framework primitive being reinvented here (§0.24,
    checked against the pinned langchain-core 1.6.0). `AzureChatOpenAI` is
    itself the framework's model construction; nothing about the model is
    hand-managed.
    """
    return AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=deployment,
        api_version=os.environ.get(
            "AZURE_OPENAI_API_VERSION", settings.AZURE_OPENAI_API_VERSION
        ),
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        temperature=temperature,
        max_tokens=max_tokens,
        # KEEP UNTIL STEP 6.4. This is hand-rolled retry that
        # ModelRetryMiddleware replaces (§19.4, CLAUDE.md §8.7), but removing
        # it before the middleware exists leaves a window with no retry at
        # all. 6.4 lands the replacement and deletes this line.
        max_retries=3,
    )


def get_llm(
    role: str,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> AzureChatOpenAI:
    """Resolve one of the eleven §21 roles to a cached model.

        llm = get_llm("coach", max_tokens=1500)

    `temperature` defaults to the role's ratified value (§21); pass one only
    to override deliberately. `max_tokens` of None leaves the Azure default
    in place — pass 1500 for coaching turns.

    Raises `ValueError` for a name that is not one of the eleven roles. §21
    requires an amendment to add a role, so an unrecognised name is a bug at
    the call site, not a deployment name to pass through.
    """
    try:
        deployment = ROLE_DEPLOYMENTS[role]
    except KeyError:
        raise ValueError(
            f"Unknown LLM role {role!r}. The eleven roles (§21) are: "
            f"{', '.join(sorted(ROLE_DEPLOYMENTS))}. A new role requires a "
            f"§56 amendment, not a new string here."
        ) from None

    if temperature is None:
        temperature = role_temperature(role)

    return _build_llm(deployment, temperature, max_tokens)


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
