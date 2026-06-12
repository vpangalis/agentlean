from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage

from backend.core.state import ImproveGraphState
from backend.core.llm import get_llm
from backend.core.prompts import (
    ORCHESTRATOR_SYSTEM_BASE,
    ORCHESTRATOR_CONTEXT_MAP,
    EXTRACTION_MAP,
    REFLECTION_CHECK,
    STATE_SUMMARY_TEMPLATE,
)
from backend.knowledge.retriever import (
    build_knowledge_context,
    active_work_product_label,
)

logger = logging.getLogger(__name__)


# Keys defined by the current ControlPhaseInput schema. Used to filter
# stale data persisted by previous scaffolds (e.g. control_measures as
# objects, control_chart_configured, monitoring_system, handover_complete)
# out of the response.
VALID_CONTROL_KEYS = {
    "control_plan", "control_measures",
    "monitoring_method", "monitoring_frequency", "control_chart_type",
    "response_plan", "trigger_threshold",
    "documentation_updated", "training_completed",
    "sustainability_confirmed", "sponsor_final_sign_off",
}


CONTROL_WORK_PRODUCTS = [
    {
        "id": "wp1",
        "label": "Control plan",
        "fields": ["control_plan", "control_measures"],
        "hint": (
            "Help the team define what needs to be controlled "
            "to sustain the improvement. The control plan names "
            "the process steps that changed, the new standard, "
            "and who is responsible for maintaining it."
        ),
    },
    {
        "id": "wp2",
        "label": "Monitoring",
        "fields": ["monitoring_method", "monitoring_frequency",
                   "control_chart_type"],
        "hint": (
            "Help the team set up ongoing measurement of the "
            "primary metric. How will they know if the improvement "
            "holds? Define the method, frequency, and who reviews."
        ),
    },
    {
        "id": "wp3",
        "label": "Response plan",
        "fields": ["response_plan", "trigger_threshold"],
        "hint": (
            "Help the team define what happens if the metric "
            "deteriorates. What threshold triggers action? "
            "Who is notified and what do they do?"
        ),
    },
    {
        "id": "wp4",
        "label": "Documentation",
        "fields": ["documentation_updated", "training_completed"],
        "hint": (
            "Help the team confirm that the new way of working is "
            "captured for good. Which SOPs, work instructions, or "
            "systems were updated, and has the team been trained "
            "on the new process and the response plan?"
        ),
    },
    {
        "id": "wp5",
        "label": "Sustainability",
        "fields": ["sustainability_confirmed", "sponsor_final_sign_off"],
        "hint": (
            "Help the team confirm the improvement will hold over "
            "time and close the project. Is sustainability confirmed? "
            "Has the sponsor given final sign-off to hand the process "
            "back to the business?"
        ),
    },
]


def orchestrate_control(state: ImproveGraphState) -> dict:
    """Orchestrator node for Control phase.
    1. Runs extraction to update phase_inputs from chat history
    2. Generates next Orchestrator response with a cross-phase context brief
    3. Reflects on response quality before returning
    Returns dict slice only."""

    case_meta = state.get("case_metadata") or {}
    department = case_meta.get("department", "your department")
    title = case_meta.get("title", "this project")
    current_user = state.get("current_user", "the team")
    chat_history = state.get("chat_history") or []
    phase_inputs = state.get("phase_inputs") or {}

    # ── 1. Extract structured fields from conversation ────────────────
    extraction_prompt = EXTRACTION_MAP["control"]
    conversation_text = _format_conversation(chat_history)
    extracted = _run_extraction(extraction_prompt, conversation_text)

    control_inputs = phase_inputs.get("control") or {}
    # Snapshot pre-merge so section completion can tell which section
    # crossed the threshold on THIS turn.
    previous_control = dict(control_inputs)
    for key, value in extracted.items():
        if value is not None and value != [] and value != "":
            control_inputs[key] = value
    # Filter out stale keys from the previous Control scaffold
    # (control_chart_configured, monitoring_system, handover_complete,
    # financial_impact_verified, etc. persisted in the case blob before
    # the schema was rewritten). Also drops any unexpected keys the
    # extraction LLM might emit.
    control_inputs = {
        k: v for k, v in control_inputs.items()
        if k in VALID_CONTROL_KEYS
    }
    phase_inputs["control"] = control_inputs
    current_control = control_inputs

    # ── 2. Generate Orchestrator response with cross-phase context ────
    system_prompt = (
        ORCHESTRATOR_SYSTEM_BASE.format(department=department, title=title)
        + "\n\n"
        + ORCHESTRATOR_CONTEXT_MAP["control"]
    )
    state_summary = _build_control_context(state)
    logger.info("Control context injected:\n%s", state_summary)
    response_text = _run_orchestrator(
        system_prompt, chat_history, current_user, state_summary
    )

    # ── 3. Reflect on response quality ────────────────────────────────
    # TODO(coaching): reflect disabled — it was tuned for the previous
    # terse output style and compresses the new structured coaching
    # responses, defeating the prompt rewrite. Reintroduce a
    # coaching-aware reflect later.
    # response_text = _reflect(response_text)

    # ── 4. Append AI turn to chat history ─────────────────────────────
    now = datetime.now(timezone.utc).isoformat()
    new_turn = {
        "turn": len(chat_history) + 1,
        "role": "ai",
        "user": None,
        "text": response_text,
        "timestamp": now,
        "citations": [],
    }
    updated_history = chat_history + [new_turn]

    # ── 5. Detect section completion ──────────────────────────────────
    section_completed = _detect_section_completion(
        current_control, previous_control
    )

    return {
        "phase_inputs": phase_inputs,
        "chat_history": updated_history,
        "section_completed": section_completed,
    }


# ── private helpers ─────────────────────────────────────────────────


def _format_conversation(chat_history: list) -> str:
    """Format chat history as plain text for extraction prompt."""
    lines = []
    for turn in chat_history:
        role = "AI" if turn.get("role") == "ai" else turn.get("user", "Team")
        lines.append(f"{role}: {turn.get('text', '')}")
    return "\n".join(lines)


def _run_extraction(prompt_template: str, conversation: str) -> dict:
    """Run extraction LLM call. Returns partial dict, empty on failure."""
    llm = get_llm("extraction", temperature=0.0)
    prompt = prompt_template.replace("{conversation}", conversation)
    try:
        result = llm.invoke([HumanMessage(content=prompt)])
        text = result.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            text = text[start:end]
        return json.loads(text)
    except Exception as e:
        logger.warning("Extraction failed: %s", e)
        return {}


def _run_orchestrator(
    system_prompt: str,
    chat_history: list,
    current_user: str,
    state_summary: str | None = None,
) -> str:
    """Run orchestrator LLM call. Returns response text."""
    llm = get_llm("coach", temperature=0.4, max_tokens=1500)
    messages = [SystemMessage(content=system_prompt)]
    if state_summary:
        messages.append(SystemMessage(content=state_summary))

    # RAG — ground this turn in retrieved Black Belt methodology
    last_human = next(
        (t.get("text", "") for t in reversed(chat_history)
         if t.get("role") != "ai"),
        "",
    )
    knowledge_block = build_knowledge_context(
        phase="control",
        user_message=last_human,
        work_product_label=active_work_product_label(state_summary),
    )
    if knowledge_block:
        messages.append(SystemMessage(content=knowledge_block))

    for turn in chat_history[-12:]:  # last 12 turns for context window
        role = "ai" if turn.get("role") == "ai" else "human"
        content = turn.get("text", "")
        if role == "ai":
            from langchain_core.messages import AIMessage
            messages.append(AIMessage(content=content))
        else:
            messages.append(
                HumanMessage(content=f"{turn.get('user', 'Team')}: {content}")
            )
    try:
        result = llm.invoke(messages)
        return result.content.strip()
    except Exception as e:
        logger.error("Orchestrator LLM failed: %s", e)
        return "I'm having trouble connecting. Please try again in a moment."


def _reflect(response: str) -> str:
    """Check response quality. Returns revised response if issues found.
    Private — called only from orchestrate_control."""
    llm = get_llm("reasoning", temperature=0.0)
    prompt = REFLECTION_CHECK.format(response=response)
    try:
        result = llm.invoke([HumanMessage(content=prompt)])
        text = result.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)
        if not data.get("passes") and data.get("revised_response"):
            logger.info("Reflection revised response: %s", data.get("issues"))
            return data["revised_response"]
        return response
    except Exception as e:
        logger.warning("Reflection failed, returning original: %s", e)
        return response


def _detect_section_completion(
    control_inputs: dict,
    previous_inputs: dict,
) -> str | None:
    """Detect which Control work product just became complete this turn.
    Returns the work product id string or None.
    """

    def all_present(keys: list[str]) -> bool:
        return all(control_inputs.get(k) for k in keys)

    def was_incomplete(keys: list[str]) -> bool:
        return not all(previous_inputs.get(k) for k in keys)

    for wp in CONTROL_WORK_PRODUCTS:
        fields = wp["fields"]
        if all_present(fields) and was_incomplete(fields):
            return wp["id"]

    return None


def _build_control_context(state: ImproveGraphState) -> str:
    """Build a plain-text context brief for the Control orchestrator.

    Mirrors Improve's _build_improve_context() pattern — shows what is
    captured vs still needed — but additionally carries forward the
    cross-phase context the team needs in Control: the Define problem
    framing, the Measure baseline, and (critically) the Improve solution
    and confirmed result the control plan must protect. Injected as a
    SystemMessage on every orchestrator call."""

    phase_inputs = state.get("phase_inputs") or {}
    define = phase_inputs.get("define") or {}
    measure = phase_inputs.get("measure") or {}
    analyse = phase_inputs.get("analyse_phase") or {}
    improve = phase_inputs.get("improve") or {}
    control = phase_inputs.get("control") or {}

    # ── Cross-phase brief: Define ─────────────────────────────────────
    define_lines = [
        "FROM DEFINE:",
        f"  Problem statement: {define.get('what') or '—'}",
        f"  Primary metric: {define.get('primary_metric') or '—'}",
        f"  Target value: {define.get('how_goal') or '—'}",
    ]

    # ── Cross-phase brief: Measure ────────────────────────────────────
    measure_lines = [
        "FROM MEASURE:",
        f"  Baseline mean: {measure.get('baseline_mean') or '—'}",
        f"  Capability (sigma): {measure.get('current_sigma_level') or '—'}",
    ]

    # ── Cross-phase brief: Improve (the gains to protect) ─────────────
    improve_lines = [
        "FROM IMPROVE (protect these gains):",
        f"  Root cause controlled: {analyse.get('root_cause_statement') or '—'}",
        f"  Selected solution: {improve.get('selected_solution') or '—'}",
        f"  Pilot result: {improve.get('pilot_result') or '—'}",
        f"  Improvement confirmed: {improve.get('improvement_confirmed') or '—'}",
    ]

    # ── Control progress: captured vs missing per work product ────────
    def all_captured(keys: list[str]) -> bool:
        return all(control.get(k) for k in keys)

    def captured_list(keys: list[str]) -> list[str]:
        return [k for k in keys if control.get(k)]

    def missing_list(keys: list[str]) -> list[str]:
        return [k for k in keys if not control.get(k)]

    progress_lines = ["CONTROL PROGRESS:"]
    current_work_product = None
    for wp in CONTROL_WORK_PRODUCTS:
        name = f"{wp['id']} — {wp['label']}"
        fields = wp["fields"]
        captured = captured_list(fields)
        missing = missing_list(fields)
        if all_captured(fields):
            progress_lines.append(
                f"  ✓ {name} — COMPLETE ({len(fields)}/{len(fields)} fields)"
            )
        else:
            status = "IN PROGRESS" if captured else "NOT STARTED"
            progress_lines.append(f"  ○ {name} — {status}")
            progress_lines.append(
                f"    Captured ({len(captured)}/{len(fields)}): "
                f"{', '.join(captured) if captured else 'none'}"
            )
            progress_lines.append(f"    Still needed: {', '.join(missing)}")
            if current_work_product is None:
                current_work_product = wp

    # ── Snapshot of any closure detail already captured ───────────────
    snapshot_lines = [
        "SUSTAIN SNAPSHOT:",
        f"  Monitoring method: {control.get('monitoring_method') or '—'}",
        f"  Sustainability confirmed: {control.get('sustainability_confirmed') or '—'}",
        f"  Sponsor final sign-off: {control.get('sponsor_final_sign_off') or '—'}",
    ]

    if current_work_product is None:
        next_action = (
            "All Control work products are complete. Summarise the control "
            "plan and confirm sustainability for the gate document, then "
            "invite the team to submit and close the project."
        )
    else:
        next_action = (
            f"Continue with {current_work_product['id']} — "
            f"{current_work_product['label']}. {current_work_product['hint']}"
        )

    summary_text = "\n".join(
        define_lines
        + [""]
        + measure_lines
        + [""]
        + improve_lines
        + [""]
        + snapshot_lines
        + [""]
        + progress_lines
    )
    return STATE_SUMMARY_TEMPLATE.format(
        state_summary=summary_text,
        next_action=next_action,
    )
