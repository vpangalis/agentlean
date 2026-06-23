from __future__ import annotations

import logging
from functools import lru_cache

from langgraph.graph import StateGraph, END

from backend.core.state import ImproveGraphState
from backend.core.config import settings
from backend.core.checkpointer import get_checkpointer

# Phase orchestrate nodes
from backend.phases.define.orchestrate import orchestrate_define
from backend.phases.define.validate import validate_define
from backend.phases.measure.orchestrate import orchestrate_measure
from backend.phases.measure.validate import validate_measure
from backend.phases.analyse_phase.orchestrate import orchestrate_analyse_phase
from backend.phases.analyse_phase.validate import validate_analyse_phase
from backend.phases.improve.orchestrate import orchestrate_improve
from backend.phases.improve.validate import validate_improve
from backend.phases.control.orchestrate import orchestrate_control
from backend.phases.control.validate import validate_control

from backend.escalate import escalate

logger = logging.getLogger(__name__)

PHASE_ORDER = [
    "define",
    "measure",
    "analyse_phase",
    "improve",
    "control",
]


def _gate_router(phase: str):
    """Returns a routing function for the validate node of a given phase."""

    def router(state: ImproveGraphState) -> str:
        phase_data = (state.get("phase_inputs") or {}).get(phase, {})
        if state.get("escalated"):
            return "escalate"
        if phase_data.get("_gate_passed"):
            return "pass"
        return "fail"

    router.__name__ = f"route_{phase}"
    return router


@lru_cache(maxsize=1)
def get_graph():
    """Build and compile the Agent Improve LangGraph graph.
    Cached — compiled once per process."""

    builder = StateGraph(ImproveGraphState)

    # ── add all nodes ──────────────────────────────────────────────
    builder.add_node("orchestrate_define",        orchestrate_define)
    builder.add_node("validate_define",           validate_define)
    builder.add_node("orchestrate_measure",       orchestrate_measure)
    builder.add_node("validate_measure",          validate_measure)
    builder.add_node("orchestrate_analyse_phase", orchestrate_analyse_phase)
    builder.add_node("validate_analyse_phase",    validate_analyse_phase)
    builder.add_node("orchestrate_improve",       orchestrate_improve)
    builder.add_node("validate_improve",          validate_improve)
    builder.add_node("orchestrate_control",       orchestrate_control)
    builder.add_node("validate_control",          validate_control)
    builder.add_node("escalate",                  escalate)

    # ── entry point ────────────────────────────────────────────────
    builder.set_entry_point("orchestrate_define")

    # ── define phase ───────────────────────────────────────────────
    builder.add_edge("orchestrate_define", "validate_define")
    builder.add_conditional_edges(
        "validate_define",
        _gate_router("define"),
        {
            "pass":     "orchestrate_measure",
            "fail":     "orchestrate_define",
            "escalate": "escalate",
        },
    )

    # ── measure phase ──────────────────────────────────────────────
    builder.add_edge("orchestrate_measure", "validate_measure")
    builder.add_conditional_edges(
        "validate_measure",
        _gate_router("measure"),
        {
            "pass":     "orchestrate_analyse_phase",
            "fail":     "orchestrate_measure",
            "escalate": "escalate",
        },
    )

    # ── analyse phase ──────────────────────────────────────────────
    builder.add_edge("orchestrate_analyse_phase", "validate_analyse_phase")
    builder.add_conditional_edges(
        "validate_analyse_phase",
        _gate_router("analyse_phase"),
        {
            "pass":     "orchestrate_improve",
            "fail":     "orchestrate_analyse_phase",
            "escalate": "escalate",
        },
    )

    # ── improve phase ──────────────────────────────────────────────
    builder.add_edge("orchestrate_improve", "validate_improve")
    builder.add_conditional_edges(
        "validate_improve",
        _gate_router("improve"),
        {
            "pass":     "orchestrate_control",
            "fail":     "orchestrate_improve",
            "escalate": "escalate",
        },
    )

    # ── control phase ──────────────────────────────────────────────
    builder.add_edge("orchestrate_control", "validate_control")
    builder.add_conditional_edges(
        "validate_control",
        _gate_router("control"),
        {
            "pass":     END,
            "fail":     "orchestrate_control",
            "escalate": "escalate",
        },
    )

    # ── escalation always ends ─────────────────────────────────────
    builder.add_edge("escalate", END)

    try:
        checkpointer = get_checkpointer()
    except RuntimeError as e:
        logger.critical(
            "Checkpointer unavailable — graph will not persist state. "
            "This is acceptable for offline dev only. Error: %s", e
        )
        checkpointer = None

    graph = builder.compile(checkpointer=checkpointer)
    logger.info("Agent Improve graph compiled — %d nodes", len(PHASE_ORDER) * 2 + 1)
    return graph
