from __future__ import annotations

import asyncio
import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response

from backend.core.config import settings
from backend.core.tracing import init_tracing
from backend.core.logging_setup import configure_logging
from backend.core.request_context import (
    new_request_id,
    set_request_id,
    get_request_id,
)
from backend.gateway.routes import router
from backend.core.llm import warm_turn_llms
from backend.knowledge import retriever
from backend.storage import blob

configure_logging(level=getattr(settings, "LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Assigns a request_id to every incoming request and
    exposes it both as a context var (for logging) and as a
    response header (for client correlation).
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Allow caller-supplied id (for trace correlation across
        # services), otherwise generate one.
        incoming = request.headers.get("x-request-id")
        rid = incoming.strip() if incoming else new_request_id()
        set_request_id(rid)
        try:
            response = await call_next(request)
        finally:
            pass
        response.headers["x-request-id"] = rid
        return response

app = FastAPI(
    title="Agent Improve",
    description="DMAIC improvement agent — by Agentlean",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIdMiddleware)

app.include_router(router)
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="ui", html=True), name="ui")


@app.on_event("startup")
async def startup():
    init_tracing()
    # Step 6.54 (G-93) — every client a Define turn uses is built HERE, before
    # the app accepts a request, rather than inside the first Belt's turn. On
    # a first turn the lazy builds cost ~20 s (trace 01a0d357…) and pushed an
    # open question past its budget. Built in a worker thread: the builds are
    # synchronous and load certificate bundles. A failure is logged and the
    # app still starts — a turn then builds lazily, as it did before 6.54.
    started = time.monotonic()
    try:
        await asyncio.to_thread(warm_turn_llms)
        await asyncio.to_thread(retriever.warm_clients)
        logger.info("Clients built before the first turn in %.1fs (step 6.54)",
                    time.monotonic() - started)
    except Exception as exc:  # noqa: BLE001 — startup must not fail on a warm-up
        logger.warning(
            "Client warm-up FAILED after %.1fs (%s: %s) — the first turn will "
            "build its clients and may miss its budget (G-93)",
            time.monotonic() - started, type(exc).__name__, exc,
        )
    logger.info("Agent Improve starting on port 8020")


@app.on_event("shutdown")
async def shutdown():
    # `storage/blob.py` caches one `azure.storage.blob.aio` client for the
    # process; its aiohttp session needs a deterministic close or it is merely
    # garbage-collected, which logs an unclosed-session warning (step 3.5).
    # This is NOT the graceful drain of step 8.5 — that one waits for in-flight
    # coaching turns via `RunControl.request_drain()` and stays gated. Closing
    # an HTTP session is a separate, ungated concern.
    await blob.aclose()
    # 6.54 — the per-index search clients built at startup, closed the same way.
    retriever.close_clients()
    logger.info("Agent Improve shutting down")


__all__ = ["app"]
