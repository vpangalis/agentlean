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


# Keys defined by the current MeasurePhaseInput schema. Used to filter
# stale data persisted by previous scaffolds (e.g. y_variables,
# confirmed_factors, data_sources) out of the response.
VALID_MEASURE_KEYS = {
    "primary_metric_confirmed", "secondary_metric_confirmed",
    "data_collection_plan", "msa_required", "msa_result",
    "baseline_period", "baseline_sample_size", "baseline_mean",
    "baseline_variation", "baseline_summary",
    "capability_method", "current_sigma_level", "capability_summary",
}


MEASURE_WORK_PRODUCTS = [
    ("Work product 1 — Metrics confirmation", [
        "primary_metric_confirmed",
        "secondary_metric_confirmed",
    ]),
    ("Work product 2 — Data collection plan", [
        "data_collection_plan",
    ]),
    ("Work product 3 — Measurement reliability", [
        "msa_required",
    ]),
    ("Work product 4 — Baseline data", [
        "baseline_period",
        "baseline_sample_size",
        "baseline_mean",
        "baseline_variation",
        "baseline_summary",
    ]),
    ("Work product 5 — Process capability", [
        "capability_method",
        "current_sigma_level",
        "capability_summary",
    ]),
]


def orchestrate_measure(state: ImproveGraphState) -> dict:
    """Orchestrator node for Measure phase.
    1. Runs extraction to update phase_inputs from chat history
    2. Seeds primary/secondary metric confirmations from Define if unset
    3. Generates next Orchestrator response with state summary
    4. Reflects on response quality before returning
    Returns dict slice only."""

    case_meta = state.get("case_metadata") or {}
    department = case_meta.get("department", "your department")
    title = case_meta.get("title", "this project")
    current_user = state.get("current_user", "the team")
    chat_history = state.get("chat_history") or []
    phase_inputs = state.get("phase_inputs") or {}

    # ── 1. Extract structured fields from conversation ────────────────
    extraction_prompt = EXTRACTION_MAP["measure"]
    conversation_text = _format_conversation(chat_history)
    extracted = _run_extraction(extraction_prompt, conversation_text)

    measure_inputs = phase_inputs.get("measure") or {}
    # Snapshot pre-merge so section completion can tell which section
    # crossed the threshold on THIS turn.
    previous_measure = dict(measure_inputs)
    for key, value in extracted.items():
        if value is not None and value != [] and value != "":
            measure_inputs[key] = value
    # Filter out stale keys from the previous Measure scaffold
    # (y_variables, confirmed_factors, data_sources, etc. persisted
    # in the case blob before the schema was rewritten). Also drops
    # any unexpected keys the extraction LLM might emit.
    measure_inputs = {
        k: v for k, v in measure_inputs.items()
        if k in VALID_MEASURE_KEYS
    }
    phase_inputs["measure"] = measure_inputs
    current_measure = measure_inputs

    # ── 2. Seed metric confirmations from Define if not yet set ───────
    if not current_measure.get("primary_metric_confirmed"):
        define_structured = phase_inputs.get("define") or {}
        pm = define_structured.get("primary_metric")
        pm_unit = define_structured.get("primary_metric_unit", "")
        if pm:
            seed = f"{pm} ({pm_unit})" if pm_unit else pm
            current_measure["primary_metric_confirmed"] = seed
            if "measure" not in phase_inputs:
                phase_inputs["measure"] = {}
            phase_inputs["measure"]["primary_metric_confirmed"] = seed

    if not current_measure.get("secondary_metric_confirmed"):
        define_structured = phase_inputs.get("define") or {}
        sm = define_structured.get("secondary_metric")
        if sm:
            current_measure["secondary_metric_confirmed"] = sm
            if "measure" not in phase_inputs:
                phase_inputs["measure"] = {}
            phase_inputs["measure"]["secondary_metric_confirmed"] = sm

    # ── 3. Generate Orchestrator response with state summary ──────────
    system_prompt = (
        ORCHESTRATOR_SYSTEM_BASE.format(department=department, title=title)
        + "\n\n"
        + ORCHESTRATOR_CONTEXT_MAP["measure"]
    )
    state_summary = _build_state_summary(current_measure)
    logger.info("Measure state summary injected:\n%s", state_summary)
    response_text = _run_orchestrator(
        system_prompt, chat_history, current_user, state_summary
    )

    # ── 4. Reflect on response quality ────────────────────────────────
    response_text = _reflect(response_text)

    # ── 5. Append AI turn to chat history ─────────────────────────────
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

    # ── 6. Detect section completion ──────────────────────────────────
    section_completed = _detect_section_completion(
        current_measure, previous_measure
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
    llm = get_llm("reasoning", temperature=0.3)
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
        phase="measure",
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
    Private — called only from orchestrate_measure."""
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
    measure_inputs: dict,
    previous_inputs: dict,
) -> str | None:
    """Detect which Measure work product just became complete this turn.
    Returns section key string or None.
    """

    def all_present(keys: list[str]) -> bool:
        return all(measure_inputs.get(k) for k in keys)

    def was_incomplete(keys: list[str]) -> bool:
        return not all(previous_inputs.get(k) for k in keys)

    sections = [
        ("metrics_confirmed", [
            "primary_metric_confirmed",
            "secondary_metric_confirmed",
        ]),
        ("data_collection_plan", ["data_collection_plan"]),
        ("msa", ["msa_required"]),
        ("baseline", [
            "baseline_period",
            "baseline_sample_size",
            "baseline_mean",
            "baseline_variation",
            "baseline_summary",
        ]),
        ("capability", [
            "capability_method",
            "current_sigma_level",
            "capability_summary",
        ]),
    ]

    for section_key, required_fields in sections:
        if all_present(required_fields) and was_incomplete(required_fields):
            return section_key

    return None


def _build_state_summary(measure_inputs: dict) -> str:
    """Build a plain-text state summary of captured vs missing fields
    for each work product. Injected into every orchestrator call so the
    LLM always knows exactly where the team stands."""

    def all_captured(keys: list[str]) -> bool:
        return all(measure_inputs.get(k) for k in keys)

    def captured_list(keys: list[str]) -> list[str]:
        return [k for k in keys if measure_inputs.get(k)]

    def missing_list(keys: list[str]) -> list[str]:
        return [k for k in keys if not measure_inputs.get(k)]

    lines = []
    current_work_product = None

    for name, fields in MEASURE_WORK_PRODUCTS:
        done = all_captured(fields)
        missing = missing_list(fields)
        captured = captured_list(fields)

        if done:
            lines.append(
                f"✓ {name} — COMPLETE ({len(fields)}/{len(fields)} fields)"
            )
        else:
            status = "IN PROGRESS" if captured else "NOT STARTED"
            lines.append(f"○ {name} — {status}")
            lines.append(
                f"  Captured ({len(captured)}/{len(fields)}): "
                f"{', '.join(captured) if captured else 'none'}"
            )
            lines.append(f"  Still needed: {', '.join(missing)}")
            if current_work_product is None:
                current_work_product = name

    if current_work_product is None:
        next_action = (
            "All Measure work products are complete. "
            "Summarise the gate document and invite the team to submit."
        )
    else:
        next_action = (
            f"Continue with {current_work_product}. "
            f"Ask for the first missing field only."
        )

    summary_text = "\n".join(lines)
    return STATE_SUMMARY_TEMPLATE.format(
        state_summary=summary_text,
        next_action=next_action,
    )
