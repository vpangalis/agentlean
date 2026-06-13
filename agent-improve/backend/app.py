from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.tracing import init_tracing
from backend.gateway.routes import router

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

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
