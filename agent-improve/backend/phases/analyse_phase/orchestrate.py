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


# Keys defined by the current AnalysePhaseInput schema. Used to filter
# stale data persisted by previous scaffolds (e.g. root_causes,
# hypothesis_tests, primary_root_cause) out of the response.
VALID_ANALYSE_KEYS = {
    "possible_causes", "cause_categories",
    "five_whys_analysis",
    "pareto_top_causes", "vital_few_causes",
    "cause_verified", "verification_method", "evidence_summary",
    "root_cause_statement", "root_cause_agreed_by",
}


ANALYSE_WORK_PRODUCTS = [
    {
        "id": "wp1",
        "label": "Cause brainstorming",
        "fields": ["possible_causes", "cause_categories"],
        "hint": (
            "Help the team brainstorm all possible causes. "
            "Use categories: People, Process, Technology, "
            "Policy/Procedure, Environment. Encourage quantity "
            "at this stage — every idea is valid."
        ),
    },
    {
        "id": "wp2",
        "label": "Root cause drilling",
        "fields": ["five_whys_analysis"],
        "hint": (
            "For the most likely causes, drill deeper with "
            "5 Whys. Ask 'why does that happen?' until the "
            "root level is reached — the point where fixing "
            "it prevents recurrence."
        ),
    },
    {
        "id": "wp3",
        "label": "Prioritisation",
        "fields": ["pareto_top_causes", "vital_few_causes"],
        "hint": (
            "Identify the vital few causes: which 1–3 causes "
            "likely account for the majority of the problem? "
            "Use frequency data from Measure if available."
        ),
    },
    {
        "id": "wp4",
        "label": "Verification",
        "fields": ["cause_verified", "verification_method", "evidence_summary"],
        "hint": (
            "Confirm whether the vital few causes are proven "
            "by data. When this cause is present, is the "
            "problem worse? When absent, does it improve?"
        ),
    },
    {
        "id": "wp5",
        "label": "Root cause statement",
        "fields": ["root_cause_statement", "root_cause_agreed_by"],
        "hint": (
            "Write the root cause statement: name the specific "
            "cause, link it to the metric, keep it "
            "solution-agnostic. Template: 'The primary driver "
            "of [metric] is [cause] because [evidence].'"
        ),
    },
]


def orchestrate_analyse_phase(state: ImproveGraphState) -> dict:
    """Orchestrator node for Analyse phase.
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
    extraction_prompt = EXTRACTION_MAP["analyse_phase"]
    conversation_text = _format_conversation(chat_history)
    extracted = _run_extraction(extraction_prompt, conversation_text)

    analyse_inputs = phase_inputs.get("analyse_phase") or {}
    # Snapshot pre-merge so section completion can tell which section
    # crossed the threshold on THIS turn.
    previous_analyse = dict(analyse_inputs)
    for key, value in extracted.items():
        if value is not None and value != [] and value != "":
            analyse_inputs[key] = value
    # Filter out stale keys from the previous Analyse scaffold
    # (root_causes, hypothesis_tests, primary_root_cause, etc. persisted
    # in the case blob before the schema was rewritten). Also drops any
    # unexpected keys the extraction LLM might emit.
    analyse_inputs = {
        k: v for k, v in analyse_inputs.items()
        if k in VALID_ANALYSE_KEYS
    }
    phase_inputs["analyse_phase"] = analyse_inputs
    current_analyse = analyse_inputs

    # ── 2. Generate Orchestrator response with cross-phase context ────
    system_prompt = (
        ORCHESTRATOR_SYSTEM_BASE.format(department=department, title=title)
        + "\n\n"
        + ORCHESTRATOR_CONTEXT_MAP["analyse_phase"]
    )
    state_summary = _build_analyse_context(state)
    logger.info("Analyse context injected:\n%s", state_summary)
    response_text = _run_orchestrator(
        system_prompt, chat_history, current_user, state_summary
    )

    # ── 3. Reflect on response quality ────────────────────────────────
    response_text = _reflect(response_text)

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
        current_analyse, previous_analyse
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
        phase="analyse_phase",
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
    Private — called only from orchestrate_analyse_phase."""
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
    analyse_inputs: dict,
    previous_inputs: dict,
) -> str | None:
    """Detect which Analyse work product just became complete this turn.
    Returns the work product id string or None.
    """

    def all_present(keys: list[str]) -> bool:
        return all(analyse_inputs.get(k) for k in keys)

    def was_incomplete(keys: list[str]) -> bool:
        return not all(previous_inputs.get(k) for k in keys)

    for wp in ANALYSE_WORK_PRODUCTS:
        fields = wp["fields"]
        if all_present(fields) and was_incomplete(fields):
            return wp["id"]

    return None


def _build_analyse_context(state: ImproveGraphState) -> str:
    """Build a plain-text context brief for the Analyse orchestrator.

    Mirrors Measure's _build_state_summary() pattern — shows what is
    captured vs still needed — but additionally carries forward the
    cross-phase context the team needs in Analyse: the Define problem
    framing and the Measure baseline findings. Injected as a SystemMessage
    on every orchestrator call so the LLM always knows where the team
    stands and what upstream phases already established."""

    phase_inputs = state.get("phase_inputs") or {}
    define = phase_inputs.get("define") or {}
    measure = phase_inputs.get("measure") or {}
    analyse = phase_inputs.get("analyse_phase") or {}

    # ── Cross-phase brief: Define ─────────────────────────────────────
    # NB: DefinePhaseInput has no dedicated process-name field, so the
    # process line falls back to "—". The problem is held in `what` and
    # the target state in `how_goal` (there are no problem_statement /
    # target_value fields).
    process_name = (
        define.get("process_name")
        or define.get("process_description")
        or "—"
    )
    define_lines = [
        "FROM DEFINE:",
        f"  Problem statement: {define.get('what') or '—'}",
        f"  Primary metric: {define.get('primary_metric') or '—'}",
        f"  Target value: {define.get('how_goal') or '—'}",
        f"  Process: {process_name}",
    ]

    # ── Cross-phase brief: Measure ────────────────────────────────────
    # NB: MeasurePhaseInput has no trend_direction field; baseline_period
    # is the available period descriptor.
    measure_lines = [
        "FROM MEASURE:",
        f"  Baseline mean: {measure.get('baseline_mean') or '—'}",
        f"  Capability (sigma): {measure.get('current_sigma_level') or '—'}",
        f"  Baseline period: {measure.get('baseline_period') or '—'}",
    ]

    # ── Analyse progress: captured vs missing per work product ────────
    def all_captured(keys: list[str]) -> bool:
        return all(analyse.get(k) for k in keys)

    def captured_list(keys: list[str]) -> list[str]:
        return [k for k in keys if analyse.get(k)]

    def missing_list(keys: list[str]) -> list[str]:
        return [k for k in keys if not analyse.get(k)]

    progress_lines = ["ANALYSE PROGRESS:"]
    current_work_product = None
    for wp in ANALYSE_WORK_PRODUCTS:
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

    # ── Snapshot of any root cause already captured ───────────────────
    cause_count = len(analyse.get("possible_causes") or [])
    snapshot_lines = [
        "ROOT CAUSE SNAPSHOT:",
        f"  Possible causes identified: {cause_count}",
        f"  Vital few causes: {analyse.get('vital_few_causes') or '—'}",
        f"  Root cause statement: {analyse.get('root_cause_statement') or '—'}",
    ]

    if current_work_product is None:
        next_action = (
            "All Analyse work products are complete. Summarise the root "
            "cause for the gate document and invite the team to submit."
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
        + snapshot_lines
        + [""]
        + progress_lines
    )
    return STATE_SUMMARY_TEMPLATE.format(
        state_summary=summary_text,
        next_action=next_action,
    )
