"""Azure AI Content Safety — Prompt Shields. ADR-0057 (ACCEPTED, fail closed); T71, T72.

One function, `shield`, over the REST operation `text:shieldPrompt`: a user-prompt attack check
(the Belt's message, T71) and a document attack check (upload text, T72). The endpoint and key
come from settings (`CONTENT_SAFETY_ENDPOINT`, `CONTENT_SAFETY_KEY`); in production the endpoint
is a private endpoint inside the intranet (T76).

It never raises. It returns a verdict dict the caller decides on:

    configured        an endpoint and key are set
    reachable         the service answered with a readable body
    user_attack       the user prompt was judged an attack
    document_attacks  one bool per document
    error             why it was not reachable (empty otherwise)

Fail closed is the CALLER's rule (the input guard, the upload pipeline): unreachable blocks the
turn or the upload. Not configured blocks in production; elsewhere the fixed rules stand alone
and the verdict says the service was not configured.

Tests replace `_post` — no live call is ever made by the suite.
"""
from __future__ import annotations

from typing import Any

import httpx

from backend.core.config import settings

API_VERSION = "2024-09-01"
TIMEOUT_S = 5.0
#: Prompt Shields' input limit per text, in characters.
MAX_CHARS = 10_000


async def _post(url: str, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
        r = await client.post(url, headers=headers, json=body)
        r.raise_for_status()
        return r.json()


def configured() -> bool:
    return bool(settings.CONTENT_SAFETY_ENDPOINT and settings.CONTENT_SAFETY_KEY)


def required() -> bool:
    """Production refuses to screen without the service (fail closed); elsewhere it may be absent."""
    return (settings.ENVIRONMENT or "").lower() == "production"


async def shield(user_prompt: str | None = None, documents: list[str] | None = None) -> dict[str, Any]:
    docs = [d[:MAX_CHARS] for d in (documents or [])]
    verdict: dict[str, Any] = {"configured": configured(), "reachable": False, "user_attack": False,
                               "document_attacks": [False] * len(docs), "error": ""}
    if not verdict["configured"]:
        verdict["error"] = "Content Safety is not configured"
        return verdict
    url = f"{str(settings.CONTENT_SAFETY_ENDPOINT).rstrip('/')}/contentsafety/text:shieldPrompt?api-version={API_VERSION}"
    headers = {"Ocp-Apim-Subscription-Key": str(settings.CONTENT_SAFETY_KEY), "Content-Type": "application/json"}
    body: dict[str, Any] = {"documents": docs}
    if user_prompt is not None:
        body["userPrompt"] = user_prompt[:MAX_CHARS]
    try:
        out = await _post(url, headers, body)
        verdict["user_attack"] = bool((out.get("userPromptAnalysis") or {}).get("attackDetected"))
        verdict["document_attacks"] = [bool(d.get("attackDetected")) for d in (out.get("documentsAnalysis") or [])]
        verdict["reachable"] = True
    except Exception as exc:  # noqa: BLE001 — the caller fails closed on any failure
        verdict["error"] = f"{type(exc).__name__}: {exc}"[:200]
    return verdict


__all__ = ["shield", "configured", "required", "API_VERSION", "MAX_CHARS"]
