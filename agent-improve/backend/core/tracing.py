"""
LangSmith tracing initialisation for Agent Improve.

Per CLAUDE.md §1.8 and §9, LangSmith tracing is mandatory.
This module sets up the required environment variables at app
startup. Without valid LangSmith credentials, the app fails
startup in production environments.

Module-level functions only (no classes) per CLAUDE.md §2.
"""

from __future__ import annotations

import logging
import os

from backend.core.config import settings

logger = logging.getLogger(__name__)


def init_tracing() -> None:
    """
    Initialise LangSmith tracing at app startup.

    Reads settings.LANGCHAIN_API_KEY and settings.LANGCHAIN_PROJECT.
    Sets the LANGCHAIN_TRACING_V2 environment variable to "true"
    so all LangChain / LangGraph calls are traced.

    In production (settings.ENVIRONMENT == "production"), missing
    credentials raise RuntimeError. In development, missing
    credentials log a warning and tracing is disabled.

    Called once from app.py at FastAPI startup.
    """
    api_key = (settings.LANGCHAIN_API_KEY or "").strip()
    project = (settings.LANGCHAIN_PROJECT or "agentlean-improve").strip()
    environment = (getattr(settings, "ENVIRONMENT", "development") or "").lower()

    if not api_key:
        message = (
            "LangSmith tracing is not configured. "
            "Set LANGCHAIN_API_KEY in the environment. "
            "Per CLAUDE.md §1.8 and §9 this is required."
        )
        if environment == "production":
            raise RuntimeError(message)
        logger.warning("%s Tracing disabled for this run (non-production).", message)
        # Explicitly disable tracing so partial config doesn't leak
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        return

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = api_key
    os.environ["LANGCHAIN_PROJECT"] = project

    # Endpoint default is LangSmith Cloud; allow override
    endpoint = getattr(settings, "LANGCHAIN_ENDPOINT", "") or ""
    if endpoint:
        os.environ["LANGCHAIN_ENDPOINT"] = endpoint

    logger.info(
        "LangSmith tracing enabled. project=%s endpoint=%s",
        project,
        endpoint or "default (smith.langchain.com)",
    )


def tracing_enabled() -> bool:
    """
    Return True if tracing is currently enabled for this process.
    Useful for diagnostics and health checks.
    """
    return os.environ.get("LANGCHAIN_TRACING_V2", "").lower() == "true"
