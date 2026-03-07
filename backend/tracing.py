"""Langfuse tracing integration for CoSolve (v3.14.5)."""
from __future__ import annotations
import logging
import os

_logger = logging.getLogger(__name__)


class LangfuseTracer:
    """Singleton wrapper around the Langfuse client for CoSolve tracing."""

    def __init__(self) -> None:
        self._client = None

    # ── Configuration ──────────────────────────────────────────────

    def is_configured(self) -> bool:
        sk = os.getenv("LANGFUSE_SECRET_KEY", "")
        pk = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        if not sk or not pk:
            return False
        if sk.startswith("sk-lf-...") or pk.startswith("pk-lf-..."):
            return False
        return True

    # ── Client ─────────────────────────────────────────────────────

    def get_langfuse(self):
        """Return the Langfuse singleton, creating it once if needed."""
        if not self.is_configured():
            return None
        if self._client is None:
            try:
                from langfuse import Langfuse
                self._client = Langfuse()
                _logger.info("Langfuse client initialised")
            except Exception as exc:
                _logger.warning("Langfuse init failed: %s", exc)
        return self._client

    # ── Handler ────────────────────────────────────────────────────

    def get_langfuse_handler(
        self,
        session_id: str | None = None,
        user_id: str | None = None,
        trace_name: str = "cosolve-agent",
        metadata: dict | None = None,
    ):
        if not self.is_configured():
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

    # ── Metadata ───────────────────────────────────────────────────

    def apply_trace_metadata(self, handler) -> None:
        if handler is None:
            return
        try:
            trace_id = getattr(handler, "last_trace_id", None)
            if not trace_id:
                return
            import requests
            from datetime import datetime, timezone
            host = os.getenv(
                "LANGFUSE_HOST",
                os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
            ).rstrip("/")
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
                                 "timestamp": datetime.now(timezone.utc).isoformat(),
                                 "body": body}]},
                auth=(pk, sk), timeout=5,
            )
        except Exception as exc:
            _logger.debug("apply_trace_metadata skipped: %s", exc)

    # ── Flush ──────────────────────────────────────────────────────

    def flush(self) -> None:
        lf = self.get_langfuse()
        if lf is None:
            return
        try:
            lf.flush()
            _logger.debug("Langfuse flush complete")
        except Exception as exc:
            _logger.warning("Langfuse flush failed: %s", exc)


# ── Module-level singleton and shims (all existing callers unchanged) ──

_tracer = LangfuseTracer()


def _is_configured() -> bool:
    return _tracer.is_configured()


def get_langfuse():
    return _tracer.get_langfuse()


def get_langfuse_handler(
    session_id=None, user_id=None,
    trace_name="cosolve-agent", metadata=None,
):
    return _tracer.get_langfuse_handler(
        session_id=session_id, user_id=user_id,
        trace_name=trace_name, metadata=metadata,
    )


def apply_trace_metadata(handler) -> None:
    _tracer.apply_trace_metadata(handler)


def flush_langfuse() -> None:
    _tracer.flush()
