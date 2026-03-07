"""Langfuse tracing for CoSolve (v3.14.5)."""
from __future__ import annotations
import logging
import os

_logger = logging.getLogger(__name__)
_client = None


def _is_configured() -> bool:
    sk = os.getenv("LANGFUSE_SECRET_KEY", "")
    pk = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    if not sk or not pk:
        return False
    if sk.startswith("sk-lf-...") or pk.startswith("pk-lf-..."):
        return False
    return True


def get_langfuse():
    """Return the module-level Langfuse singleton, creating it if needed."""
    global _client
    if not _is_configured():
        return None
    if _client is None:
        try:
            from langfuse import Langfuse
            _client = Langfuse()
            _logger.info("Langfuse client initialised")
        except Exception as exc:
            _logger.warning("Langfuse init failed: %s", exc)
    return _client


def get_langfuse_handler(
    session_id: str | None = None,
    user_id: str | None = None,
    trace_name: str = "cosolve-agent",
    metadata: dict | None = None,
):
    if not _is_configured():
        return None
    try:
        from langfuse.langchain import CallbackHandler
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        handler = CallbackHandler(public_key=public_key)
        handler._cosolve_session_id = session_id
        handler._cosolve_user_id = user_id
        handler._cosolve_trace_name = trace_name
        handler._cosolve_metadata = metadata or {}
        return handler
    except Exception as exc:
        _logger.warning("Langfuse handler init failed: %s", exc)
        return None


def apply_trace_metadata(handler) -> None:
    if handler is None:
        return
    try:
        trace_id = getattr(handler, "last_trace_id", None)
        if not trace_id:
            return
        import requests
        from datetime import datetime, timezone
        host = os.getenv("LANGFUSE_HOST", os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")).rstrip("/")
        pk = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        sk = os.getenv("LANGFUSE_SECRET_KEY", "")
        if not pk or not sk:
            return
        body: dict = {"id": trace_id}
        name = getattr(handler, "_cosolve_trace_name", None)
        if name:
            body["name"] = name
        session_id = getattr(handler, "_cosolve_session_id", None)
        if session_id:
            body["sessionId"] = session_id
        metadata = getattr(handler, "_cosolve_metadata", None)
        if metadata:
            body["metadata"] = metadata
        requests.post(
            f"{host}/api/public/ingestion",
            json={"batch": [{"id": f"{trace_id}-meta", "type": "trace-create",
                             "timestamp": datetime.now(timezone.utc).isoformat(), "body": body}]},
            auth=(pk, sk), timeout=5,
        )
    except Exception as exc:
        _logger.debug("apply_trace_metadata skipped: %s", exc)


def flush_langfuse() -> None:
    """Flush pending Langfuse events using the persistent singleton."""
    lf = get_langfuse()
    if lf is None:
        return
    try:
        lf.flush()
        _logger.debug("Langfuse flush complete")
    except Exception as exc:
        _logger.warning("Langfuse flush failed: %s", exc)
