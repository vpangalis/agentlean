"""What the coach's model fallback must never see — ADR-0082 (founder ruling 2026-10-13, T34 option A).

`ModelFallbackMiddleware` (ADR-0059 decision 2) sends every failed call to the next model. Two failures
are not the model's to recover from: a `content_filter` refusal (T92) and a token-limit HTTP 400 (§4.8,
T36 — fix the context, never a smaller model). This `wrap_model_call` middleware, declared inside the
retry and so inside the fallback, turns either one into a reply marked with the reason; neither layer
above it sees a failure. The executor reads the mark (`kept_from_fallback`) and writes the reply in code.

Built with the `@wrap_model_call` decorator on a module function, so no class is added outside the files
that may hold one.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain_core.messages import AIMessage, BaseMessage

from backend.core import content_safety
from backend.core.llm import is_token_limit

#: The key on the marked reply's `additional_kwargs`; its value is one of the two reasons.
MARK = "kept_from_fallback"
CONTENT_FILTER, TOKEN_LIMIT = "content_filter", "token_limit"


def reason(exc: BaseException) -> Optional[str]:
    """Which of the two kept-out failures `exc` is, or None for one the retry and fallback handle."""
    if content_safety.is_content_filter(exc):
        return CONTENT_FILTER
    if is_token_limit(exc):
        return TOKEN_LIMIT
    return None


def kept_from_fallback(messages: list[BaseMessage]) -> Optional[str]:
    """The reason on the agent's last marked reply, if the turn ended on one."""
    for m in reversed(messages):
        if isinstance(m, AIMessage):
            return (m.additional_kwargs or {}).get(MARK)
    return None


def _model(request: ModelRequest) -> str:
    m = request.model
    return str(getattr(m, "deployment_name", None) or getattr(m, "model_name", None) or type(m).__name__)


def kept_from_fallback_middleware(attempts: Optional[list[dict[str, Any]]] = None) -> Any:
    """The `wrap_model_call` middleware that marks a refusal or a token-limit error instead of raising it.
    Innermost of the three, it sees every attempt the retry and the fallback make: each one, with its
    model and outcome, goes to `attempts` for `step_log` (§4.8: every attempt is logged)."""
    async def keep_out(request: ModelRequest,
                       handler: Callable[[ModelRequest], Awaitable[ModelResponse]]) -> ModelResponse:
        try:
            response = await handler(request)
        except Exception as exc:
            why = reason(exc)
            if attempts is not None:
                attempts.append({"model": _model(request), "outcome": why or type(exc).__name__})
            if why is None:
                raise
            return ModelResponse(result=[AIMessage(content="", additional_kwargs={MARK: why})])
        if attempts is not None:
            attempts.append({"model": _model(request), "outcome": "ok"})
        return response

    return wrap_model_call(name="KeptFromFallback")(keep_out)


__all__ = ["MARK", "CONTENT_FILTER", "TOKEN_LIMIT", "reason", "kept_from_fallback",
           "kept_from_fallback_middleware"]
