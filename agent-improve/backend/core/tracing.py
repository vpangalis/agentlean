"""
LangSmith tracing initialisation for Agent Improve.

LangSmith tracing is mandatory (CLAUDE.md).
This module sets up the required environment variables at app
startup. Without valid LangSmith credentials, the app fails
startup in production environments.

Module-level functions only (no classes), per CLAUDE.md.
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

    Reads settings.LANGSMITH_API_KEY, LANGSMITH_PROJECT and LANGSMITH_ENDPOINT — LangSmith's own names, the
    only spelling (founder ruling 2026-10-31). Sets LANGSMITH_TRACING to "true" so all LangChain / LangGraph
    calls are traced: tracing is mandatory, so a key turns it on whatever LANGSMITH_TRACING said.

    In production (settings.ENVIRONMENT == "production"), missing
    credentials raise RuntimeError. In development, missing
    credentials log a warning and tracing is disabled.

    Called once from app.py at FastAPI startup.
    """
    api_key = (settings.LANGSMITH_API_KEY or "").strip()
    project = (settings.LANGSMITH_PROJECT or "agentlean-improve").strip()
    environment = (getattr(settings, "ENVIRONMENT", "development") or "").lower()

    if not api_key:
        message = (
            "LangSmith tracing is not configured. "
            "Set LANGSMITH_API_KEY in the environment. "
            "Per CLAUDE.md §1.8 and §9 this is required."
        )
        if environment == "production":
            raise RuntimeError(message)
        logger.warning("%s Tracing disabled for this run (non-production).", message)
        # Explicitly disable tracing so partial config doesn't leak
        os.environ["LANGSMITH_TRACING"] = "false"
        return

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = api_key
    os.environ["LANGSMITH_PROJECT"] = project

    # Endpoint default is LangSmith Cloud; allow override
    endpoint = getattr(settings, "LANGSMITH_ENDPOINT", "") or ""
    if endpoint:
        os.environ["LANGSMITH_ENDPOINT"] = endpoint

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
    return os.environ.get("LANGSMITH_TRACING", "").lower() == "true"


# ── child-only spans — gap G-95 ──────────────────────────────────────────
#
# A `@traceable` span with no enclosing run STARTS A TRACE OF ITS OWN, and
# every trace counts against LangSmith's monthly unique-traces quota. A span on
# a function that also runs with no turn around it — a unit test, the startup
# warm-up — would start a root trace each time, and once the quota is spent
# every trace, real Belt turns included, is refused with 429.
#
# These wrappers record ONLY inside an already-traced turn. The test is
# `get_current_run_tree()` — "Access the current run (span) within a traced
# function", https://docs.langchain.com/langsmith/access-current-span — which
# the installed SDK (langsmith 0.7.3) reads from a context variable whose
# default is None. It is set inside LangGraph nodes, sync and async, and inside
# `asyncio.to_thread`; it is None outside any run.
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

