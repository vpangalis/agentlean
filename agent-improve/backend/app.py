from __future__ import annotations

import logging

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
    logger.info("Agent Improve starting on port 8020")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Agent Improve shutting down")


__all__ = ["app"]
