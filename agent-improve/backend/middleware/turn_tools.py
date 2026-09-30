"""The coach's tools per turn type — ADR-0069 (refining ADR-0068), founder rulings 1 and 6, 2026-09-28.

LangChain's documented dynamic tool selection (https://docs.langchain.com/oss/python/langchain/tools):
a `wrap_model_call` middleware narrows `request.tools` with `request.override(tools=…)` before each
model call. Every tool stays registered with `create_agent`; this chooses which the model is offered.
Built with the `@wrap_model_call` decorator on a module function, so no class is added outside the
files that may hold one.

    teaching   lookups, `propose_template`, `load_skill`
    upload     `rag_lookup_evidence`, `load_evidence_series`
    answer     none — the structured reply only (the response format is not a tool in `request.tools`)

The turn type is decided in code by the executor from the move and the phase state, never by a model,
and recorded in `step_log` (`phases/nodes_common.py::turn_type_of`).
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call

TEACHING, UPLOAD, ANSWER = "teaching", "upload", "answer"
TOOLS_BY_TURN: dict[str, frozenset[str]] = {
    TEACHING: frozenset({"rag_lookup_methodology", "rag_lookup_evidence", "rag_lookup_case_history",
                         "propose_template", "load_skill"}),
    UPLOAD: frozenset({"rag_lookup_evidence", "load_evidence_series"}),
    ANSWER: frozenset(),
}


def _name(tool: Any) -> str:
    return str(getattr(tool, "name", None) or (tool.get("name") if isinstance(tool, dict) else "") or "")


def offered(turn_type: str, tools: list[Any]) -> list[Any]:
    """The registered tools a turn of `turn_type` may offer the model."""
    keep = TOOLS_BY_TURN.get(turn_type, frozenset())
    return [t for t in tools if _name(t) in keep]


def turn_tools_middleware(turn_type: str, coach_limit: int | None = None) -> Any:
    """The `wrap_model_call` middleware that offers only this turn type's tools — and none on the
    coach's LAST allowed call (G-131), so that call must be the structured reply, never a tool
    call the call limit then ends with a reply written in code. The count is the call limit's own
    (`ModelCallLimitMiddleware`'s `run_model_call_count` in the agent state)."""
    async def select_tools(request: ModelRequest,
                           handler: Callable[[ModelRequest], Awaitable[ModelResponse]]) -> ModelResponse:
        state: dict[str, Any] = dict(request.state or {})
        made = int(state.get("run_model_call_count") or 0)
        last = coach_limit is not None and made >= coach_limit - 1
        tools = [] if last else offered(turn_type, list(request.tools or []))
        # G-139 (ADR-0073, option B): one tool call per response. The coach's structured reply is a
        # tool call (ToolStrategy); with parallel calls allowed it once came back TWICE in one
        # response, ToolStrategy rejected the pair and asked again, and the answer turn's one-call
        # share ran out. The structured-output tool is always bound, so the setting is always valid.
        settings = {**(request.model_settings or {}), "parallel_tool_calls": False}
        return await handler(request.override(tools=tools, model_settings=settings))

    return wrap_model_call(name=f"TurnTools[{turn_type}]")(select_tools)


__all__ = ["TEACHING", "UPLOAD", "ANSWER", "TOOLS_BY_TURN", "offered", "turn_tools_middleware"]
