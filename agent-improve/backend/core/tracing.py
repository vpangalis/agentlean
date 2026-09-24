"""
LangSmith tracing initialisation for Agent Improve.

Per CLAUDE.md §1.8 and §9, LangSmith tracing is mandatory.
This module sets up the required environment variables at app
startup. Without valid LangSmith credentials, the app fails
startup in production environments.

Module-level functions only (no classes) per CLAUDE.md §2.
"""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import contextmanager
from functools import wraps
from types import SimpleNamespace
from typing import Any, Callable, Iterator, TypeVar

from langsmith import trace, traceable
from langsmith.run_helpers import get_current_run_tree

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


# ── child-only spans — gap G-95 ──────────────────────────────────────────
#
# A `@traceable` span with no enclosing run STARTS A TRACE OF ITS OWN, and
# every trace counts against LangSmith's monthly unique-traces quota. Step
# 8.0's executor slice (a2067db) put spans on functions that also run with no
# turn around them — unit tests, the 6.54 startup warm-up — and on 2026-09-24
# that produced ~4,070 standalone root traces (4,897 with the tests' graph
# runs, against 19 the day before) and the quota ran out: every trace since,
# real Belt turns included, is refused with 429.
#
# These wrappers record ONLY inside an already-traced turn. The test is
# `get_current_run_tree()` — "Access the current run (span) within a traced
# function", https://docs.langchain.com/langsmith/access-current-span — which
# the installed SDK (langsmith 0.7.3) reads from a context variable whose
# default is None. Measured, not assumed: it is set inside LangGraph nodes,
# sync and async, and inside `asyncio.to_thread`; it is None outside any run.
_F = TypeVar("_F", bound=Callable[..., Any])
_NO_SPAN = SimpleNamespace(end=lambda **_: None)


def child_span(**traceable_kwargs: Any) -> Callable[[_F], _F]:
    """`@traceable`, but never a root: outside a traced run it is the bare call."""
    def decorate(fn: _F) -> _F:
        traced = traceable(**traceable_kwargs)(fn)
        if asyncio.iscoroutinefunction(fn):
            @wraps(fn)
            async def async_call(*args: Any, **kwargs: Any) -> Any:
                if get_current_run_tree() is None:
                    return await fn(*args, **kwargs)
                return await traced(*args, **kwargs)
            return async_call  # type: ignore[return-value]

        @wraps(fn)
        def call(*args: Any, **kwargs: Any) -> Any:
            if get_current_run_tree() is None:
                return fn(*args, **kwargs)
            return traced(*args, **kwargs)
        return call  # type: ignore[return-value]
    return decorate


@contextmanager
def child_trace(name: str, **trace_kwargs: Any) -> Iterator[Any]:
    """`langsmith.trace`, but never a root: outside a traced run it yields a
    stand-in whose `.end()` does nothing, so the block runs unchanged."""
    if get_current_run_tree() is None:
        yield _NO_SPAN
        return
    with trace(name, **trace_kwargs) as span:
        yield span

