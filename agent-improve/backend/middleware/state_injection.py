"""`BeforeModelStateInjection` — middleware position 1.

WHAT IT DOES
    Prepends this phase's project state to the **top** of the prompt: what is
    captured so far, the prior phases' gate documents from the Store, the
    phase's requirements, and what is still missing.

THE HOOK IS `before_agent`, AND THE NAME SAYS OTHERWISE
    It fires on `before_agent`, **never `before_model`**, which fires before
    every model call inside a turn and re-injects the same facts repeatedly.

    **The class name is `BeforeModelStateInjection` and its hook is
    `before_agent`.** The name is kept; the mismatch is written down here
    rather than silently fixed.

WHY THE WORK IS SPLIT ACROSS TWO HOOKS, AND WHY THAT IS STILL "once per turn"
    In `langchain.agents.middleware`, `before_agent(state, runtime)` returns a
    **state update** — it cannot reach the prompt. The prompt is reached
    through `wrap_model_call(request, handler)`, where `ModelRequest` carries
    `system_message` and `.override()`.

    So: **`before_agent` COMPOSES the block, once per turn** — every read of
    `artifacts`, every Store lookup, every missing-field computation happens
    there and nowhere else. `wrap_model_call` then does a pure
    read-and-prepend of the already-composed string: the expensive half runs
    once per turn, and the cheap half cannot recompute because it has nothing
    to recompute from.

    (The field is `system_message`, not `system_prompt` — `create_agent` takes
    `system_prompt=`, `ModelRequest` carries `system_message`. Two names for
    adjacent things.)

MISSING FIELDS ARE THE GATE'S OWN COMPUTATION
    They are derived at injection time, never from a stored list. **And never
    from a second implementation** — `gate_registry.missing_gate_fields` is
    what `validate_{phase}` itself calls, so the prompt and the gate cannot
    disagree. A stored readiness list would be a second source of truth that
    drifts.

> **G-24:** the constructor arguments, the exact composition of the injected
> block and its token budget are not ratified. What is below is the minimum
> the behaviours require, composed from values that already exist; nothing
> here should be read as settling them.
"""
from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Optional

from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import ModelRequest
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from backend.core.prompts import (
    CAPTURE_RULES,
    FIELD_SHAPES,
    MOVE_INSTRUCTIONS,
    MOVE_OPENING,
    MOVE_PREAMBLE,
    SECTION_CONVERSATION,
    UPLOAD_TURN,
    SECTION_FEEDBACK,
    SECTION_MOVE,
    SECTION_RULES,
    SECTION_STATE,
    cut_at,
)
from backend.core.substate import PhaseState
from backend.middleware.grader import applies
from backend.phases import moves
from backend.phases.define.schema import define_progress
from backend.phases.gate_registry import GATE_SPECS, declared_type, missing_gate_fields
from backend.phases.mappers_common import PHASE_ORDER

logger = logging.getLogger(__name__)


#: G-252: a part of an element that would otherwise share the element's name.
_PART_NAMES: dict[tuple[str, str], str] = {
    ("define", "critical_to_quality"): "CTQs",
    ("define", "problem_5w2h"): "Problem statement (5W2H)",
    ("define", "metric_definitions"): "Primary metric definitions",
}

#: What one entry of a list value is called, for its one-line summary.
_ENTRY_NOUNS: dict[str, tuple[str, str]] = {
    "team": ("person", "people"), "critical_to_quality": ("CTQ", "CTQs"),
    "metric_definitions": ("metric", "metrics"), "process_steps": ("step", "steps"),
}


def display_name(phase: str, field: str) -> str:
    """G-252: the name the Belt sees for a field, never its code name."""
    from backend.core import guard_messages
    return _PART_NAMES.get((phase, field)) or guard_messages.element_name(phase, field)


def value_text(value: Any, indent: str = "") -> str:
    """G-252: a value complete, in plain lines — never cut, never Python's dict or list text."""
    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            if v in (None, "", [], {}):
                continue
            inner = value_text(v, indent + "  ")
            lines.append(f"{indent}{k}:" + (f"\n{inner}" if "\n" in inner or isinstance(v, (dict, list))
                                            else f" {inner.strip()}"))
        return "\n".join(lines)
    if isinstance(value, list):
        return "\n".join(f"{indent}- " + value_text(v, indent + "  ").strip().replace("\n", f"\n{indent}  ")
                         for v in value if v not in (None, "", [], {}))
    return f"{indent}{value}"


def value_summary(field: str, value: Any) -> str:
    """G-252: another element's value in one line, written in code."""
    if isinstance(value, list):
        one, many = _ENTRY_NOUNS.get(field, ("entry", "entries"))
        return f"{len(value)} {one if len(value) == 1 else many}"
    if isinstance(value, dict):
        steps = value.get("process_steps")
        if isinstance(steps, list):
            return f"{len(steps)} step{'' if len(steps) == 1 else 's'}"
        return "given: " + ", ".join(k for k, v in value.items() if v not in (None, "", [], {}))
    text = " ".join(str(value).split())
    return text if len(text) <= 120 else f"{len(text.split())} words"


def value_tag(phase: str, field: str, value: Any, whole: bool, status: str = "confirmed") -> str:
    """G-252: one value in its tag, under its display name — complete, or one line."""
    name = display_name(phase, field)
    if not whole:
        return f'<value name="{name}" status="{status}">{value_summary(field, value)}</value>'
    return f'<value name="{name}" status="{status}">\n{value_text(value)}\n</value>'


def tagged(section: str, tag: str) -> str:
    """G-252: a section's body in its tag, the heading line kept first."""
    heading, _, body = section.partition("\n")
    return f"{heading}\n<{tag}>\n{body.strip()}\n</{tag}>"


def reads_whole(phase: str, focus: Optional[str]) -> set[str]:
    """G-252: the fields sent complete this turn — the current element's own, and those it reads. Outside
    Define (no reads map) every value is sent complete."""
    if phase != "define":
        return set()
    from backend.phases.define.schema import ELEMENT_READS
    own = set(dict(moves.positions(phase)).get(focus or "") or ()) | ({focus} if focus else set())
    return own | set(ELEMENT_READS.get(focus or "", ()))


#: What section 3's confirmed values leave out: kept elsewhere in the section, or nowhere.
_NOT_A_VALUE = ("citations", "uploads", "acknowledged_gaps")


def turn_artifacts(state: Any) -> dict[str, Any]:
    """The case's values after this turn's change — what is stored and what this turn's Confirm stores — so sections
    3 and 5 agree, and the coaching grader reads the same values (ADR-0111 D5)."""
    state = state or {}
    plan = state.get("coaching_plan")
    return {**dict(state.get("artifacts") or {}), **dict(getattr(plan, "store", None) or {})}


def confirmed_values(phase: str, artifacts: dict[str, Any], focus: Optional[str]) -> list[str]:
    """Section 3's confirmed values (G-252): the current element's own and those it builds on whole, every other in
    one line written in code, each in its tag under its display name. The coaching grader's "case so far" is this
    list (ADR-0111 D5)."""
    whole = reads_whole(phase, focus)
    return [value_tag(phase, k, v, whole=phase != "define" or k in whole)
            for k, v in artifacts.items() if k not in _NOT_A_VALUE and v not in (None, "", [], {})]


def pending_lines(phase: str, pending: Optional[dict[str, Any]]) -> list[str]:
    """Section 3's answer awaiting the Belt's confirmation, NOT stored: the element, the Belt's words and what the
    Belt's yes stores, each value whole in its tag. The coaching grader reads these lines (ADR-0111 D5)."""
    if not pending:
        return []
    lines = ["<pending>", "An answer awaiting the Belt's confirmation; NOT stored.",
             f"Element: {display_name(phase, str(pending.get('field') or ''))}",
             f"The Belt's words: {pending.get('belt_words')}"]
    if pending.get("store"):
        lines.append("What the Belt's yes stores:")
        lines += [value_tag(phase, k, v, whole=True, status="awaiting confirmation")
                  for k, v in pending["store"].items()]
    return [*lines, "</pending>"]


def element_sources(phase: str, plan: Any) -> str:
    """What the Belt has given for the element, as the coach had it (ADR-0111 D5): section 3's answer awaiting
    Confirm, else the Belt's words section 5 names. Empty with no plan or nothing given."""
    if plan is None:
        return ""
    lines = pending_lines(phase, getattr(plan, "pending", None))
    words = str(getattr(plan, "answer", None) or "").strip()
    return "\n".join(lines or ([f"The Belt's words: {words}"] if words else []))


def _mismatch_what(phase: str, flag: dict[str, Any]) -> str:
    """ADR-0112: what the answer conflicts with, in plain words — a confirmed value by its display name (and the
    phase that approved it, when an earlier one did), or the method's rule."""
    from backend.core.prompts import MISMATCH_APPROVED, MISMATCH_CONFIRMED, MISMATCH_RULE
    field, where = str(flag.get("prior_field") or "").strip(), str(flag.get("approved_phase") or "").strip().lower()
    if not field or where in ("method", "the method") or field.lower() in ("method", "the method"):
        return MISMATCH_RULE
    name = display_name(where if where in PHASE_ORDER else phase, field)
    if where in PHASE_ORDER and where != phase:
        return MISMATCH_APPROVED.format(name=name, phase=where.capitalize())
    return MISMATCH_CONFIRMED.format(name=name)


def mismatch_line(phase: str, flag: Optional[dict[str, Any]], read_back: bool) -> str:
    """ADR-0112 (founder ruling 2026-10-27): a mismatch the coach flagged, told to the Belt in code — what the answer
    conflicts with, named, and the choice to correct it or keep it (on a read-back: Change or Confirm). "" with no
    flag."""
    from backend.core.prompts import MISMATCH_HOW, MISMATCH_HOW_READ_BACK, MISMATCH_LINE
    if not flag:
        return ""
    return MISMATCH_LINE.format(what=_mismatch_what(phase, flag), value=str(flag.get("approved_value") or "").strip(),
                                how=MISMATCH_HOW_READ_BACK if read_back else MISMATCH_HOW)


def mismatch_kept(phase: str, flag: Optional[dict[str, Any]]) -> str:
    """ADR-0112: what the answer's version history says when the Belt keeps an answer with a mismatch. "" with no
    flag."""
    from backend.core.prompts import MISMATCH_KEPT
    if not flag:
        return ""
    return MISMATCH_KEPT.format(what=_mismatch_what(phase, flag), value=str(flag.get("approved_value") or "").strip())


class BeforeModelStateInjection(AgentMiddleware):
    """Position 1. Project facts at the top of the prompt, once per turn.

    Constructed per turn with the phase's own state, because the executor
    builds the agent per turn. **G-24 leaves the constructor unstated**; the
    arguments are what the behaviours need and no more — the phase, the state
    they are read from, the config that carries the case framing, the prior
    phases' gate documents and this turn's upload.
    """

    name = "BeforeModelStateInjection"

    def __init__(
        self,
        phase: str,
        state: PhaseState,
        config: Optional[RunnableConfig] = None,
        prior_documents: Optional[dict[str, dict]] = None,
        upload: Optional[dict] = None,
    ) -> None:
        super().__init__()
        if phase not in PHASE_ORDER:
            raise ValueError(
                f"Unknown phase {phase!r}. The five (§12) are: "
                f"{', '.join(PHASE_ORDER)}."
            )
        self.phase = phase
        self._state = state
        self._config = config or {}
        #: Prior phases' gate documents, read from the Store by the caller.
        #: Without these the coach has nothing to compare against and the
        #: semantic contradiction check silently detects nothing.
        self._prior = prior_documents or {}
        #: DEF-108 (W5) — the file this upload turn reads, routed by the executor; None otherwise.
        self._upload = upload
        self._block: str = ""
        self._move: str = ""
        self._feedback: str = ""

    # ── the hook that does the work ──────────────────────────────────────

    def before_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        """Compose sections 3, 4 and 5. Once per turn — never `before_model`."""
        self._block = self._compose()
        self._move = tagged(self._compose_move(), "this_turns_move")
        self._feedback = tagged(self._compose_feedback(), "quality_feedback")
        logger.info(
            "%s.state_injection: composed state %d chars, move %d, feedback %d, "
            "%d prior phase(s)",
            self.phase, len(self._block), len(self._move), len(self._feedback),
            len(self._prior),
        )
        return None

    async def abefore_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        """Async twin — the agent loop is async, so this is the one that
        actually fires. It does no I/O; composition is pure."""
        return self.before_agent(state, runtime)

    # ── where the block reaches the prompt ───────────────────────────────

    def wrap_model_call(self, request: ModelRequest, handler: Callable) -> Any:
        return handler(self._prepend(request))

    async def awrap_model_call(
        self, request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[Any]],
    ) -> Any:
        return await handler(self._prepend(request))

    def _prepend(self, request: ModelRequest) -> ModelRequest:
        """Project facts ABOVE the coach's instructions and the conversation.

        Models weight earlier content more heavily, and facts arriving after
        the Belt's message let the response drift toward the Belt's framing
        rather than the project's established state. Injecting in `messages[]`
        append order is not allowed, so this never touches `request.messages`.

        A pure read of what `before_agent` composed: no recomputation here, or
        the once-per-turn guarantee would be decorative.

        **Content BLOCKS, never string concatenation onto `.content`.**
        `SystemMessage.content` is `str | list[dict]`, so an f-string over a
        multi-part message renders the literal ``"[{'type': 'text', ...}]"``
        into the prompt — structure destroyed, no error raised. The rule binds
        on messages this code WRITES, not only on ones it reads.

        `.content_blocks` normalises both shapes to typed blocks, and
        `content_blocks=` is accepted at construction, so prepending is a list
        operation.
        """
        if not self._block:
            return request
        existing = request.system_message
        blocks = list(existing.content_blocks) if existing is not None else []
        # THE SIX SECTIONS, in the ruled order (ADR-0111 D2): static first, the
        # task last. The rules are the agent's own system prompt, labelled here as
        # section 1 by a heading block of their own (their blocks are never
        # concatenated). Section 2, the phase script, is placed after section 1
        # by position 2 (`DMAICSkillsMiddleware`), which runs inside this wrap.
        # Then the per-turn state and feedback, and the move last.
        return request.override(
            system_message=SystemMessage(content_blocks=[
                {"type": "text", "text": SECTION_RULES}, {"type": "text", "text": "<coaching_rules>"}, *blocks,
                {"type": "text", "text": "</coaching_rules>"},
                {"type": "text", "text": self._block},
                {"type": "text", "text": self._feedback},
                {"type": "text", "text": self._move},
                {"type": "text", "text": SECTION_CONVERSATION},
            ])
        )

    # ── composition (G-24: shape is not ratified) ────────────────────────

    def _compose(self) -> str:
        # THE STATE AFTER THIS TURN'S CHANGE, so sections 3 and 4 agree: on a confirming turn the value is shown stored, the step
        # advanced and the next field current — which is what section 5 tells
        # the coach to say.
        plan = self._state.get("coaching_plan")
        artifacts = turn_artifacts(self._state)
        spec = GATE_SPECS[self.phase]
        missing = missing_gate_fields(self.phase, artifacts)

        focus = getattr(plan, "focus_field", None)

        parts = [SECTION_STATE, "<project_state>",
                 f"PROJECT STATE — {self.phase.upper()} PHASE",
                 "(established facts; these outrank anything said in "
                 "conversation that contradicts them)"]

        # The Belt's step, COMPUTED and delivered every turn, so the coach never
        # counts it — and never from the gate list below. First, so it is the
        # number read first.
        if self.phase == "define":
            step = define_progress(artifacts)
            parts += ["<where_the_belt_is>",
                      "Computed, not yours to count:",
                      f"{step['label']} — {step['field']}",
                      "Write this exact text in `progress`. Never count steps "
                      "yourself, and never from the gate list below.",
                      "</where_the_belt_is>"]

        meta = (self._config.get("configurable") or {}).get("case_metadata") or {}
        if meta:
            parts.append("<this_project>")
            parts += [f"{label}: {meta[key]}"
                      for key, label in (("title", "Project"),
                                         ("belt_level", "Belt level"),
                                         ("leader", "Belt"),
                                         ("department", "Department"))
                      if meta.get(key)]
            parts.append("</this_project>")

        # ── phase_context ────────────────────────────────────────────
        # The phase's own composed framing: for Define the case record, and for the other four the prior phase's
        # APPROVED gate values — the only route by which a Measure coach learns what Define committed to.
        context = str(self._state.get("phase_context") or "").strip()
        parts.append("<how_this_phase_was_entered>")
        if context:
            parts.append(context)
        else:
            # An empty framing must not be silent: say it in the block the
            # trace shows, not only in the log.
            logger.warning(
                "%s.state_injection: phase_context is EMPTY — the coach is "
                "being framed without the case record or the prior gate "
                "document. The input mapper composes it at phase entry, so an "
                "empty value here means it did not reach state.", self.phase,
            )
            parts.append("[!] No phase framing was composed for this turn.")
        parts.append("</how_this_phase_was_entered>")

        if self._prior:
            parts.append("<approved_earlier>")
            parts.append("Gate-committed in earlier phases; do not contradict without flagging.")
            for name in PHASE_ORDER:
                doc = self._prior.get(name)
                if not doc:
                    continue
                parts.append(f'<phase name="{name}">')
                parts += [value_tag(name, k, v, whole=True, status="approved")
                          for k, v in doc.items() if v and not k.startswith("_")]
                parts.append("</phase>")
            parts.append("</approved_earlier>")

        parts.append("<confirmed_values>")
        parts.append("Confirmed by the Belt and stored this phase. The current element's values and those it builds "
                     "on are given whole; every other value in one line.")
        # G-252: outside Define every value is complete; in Define, the element's own and its reads.
        parts += confirmed_values(self.phase, artifacts, focus) or ["(nothing stored yet)"]
        parts.append("</confirmed_values>")

        # R5 — every position's stored status, after this turn's change,
        # the current field, and the value awaiting confirmation.
        statuses = dict(getattr(plan, "statuses", None) or {})
        if statuses:
            parts.append("<field_status>")
            parts.append("Stored, after this turn (not taught / asked / answered / confirmed):")
            parts += [f"{i}. {display_name(self.phase, f)} — {s}" for i, (f, s) in enumerate(statuses.items(), 1)]
            parts.append("Current element: "
                         + (display_name(self.phase, focus) if focus else "(every element is confirmed)"))
            parts.append("</field_status>")
        parts += pending_lines(self.phase, getattr(plan, "pending", None) if plan is not None else None)

        # R4 — the calculation FEEDS the benefits analysis: while that element is
        # current, its cost of the gap is a fact the coach proposes as `cost_of_gap`.
        # G-226: the expected saving is the other figure, never the cost of the gap.
        # Proposed, never stored — the Belt confirms it.
        if self.phase == "define" and focus == "benefits_analysis":
            from backend.phases.calculations import how_it_was_calculated
            savings = [r for r in (artifacts.get("computation_results") or [])
                       if isinstance(r, dict) and r.get("tool") == "calculate_expected_savings"]
            parts.append("<savings_calculation>")
            parts.append("Calculated this phase; propose the cost of the gap (today, at the baseline) as "
                         "benefits_analysis.cost_of_gap, with its assumptions. The expected saving (reaching the "
                         "target) is a separate figure: never call it the cost of the gap.")
            parts += [f"{how_it_was_calculated(r) or value_text(r.get('result'))}\nInputs:\n"
                      f"{value_text(r.get('inputs'), '  ')}" for r in savings[-1:]] \
                or ["(not calculated yet — the calculation needs the baseline, the target, "
                    "the cost of one defect and the yearly volume)"]
            parts.append("</savings_calculation>")

        parts += self._upload_manifest()

        # Labelled as the GATE's list, so its "n of N" is not read as the
        # Belt's step: a phase gates on more fields than it walks steps.
        parts.append("<gate_list>")
        parts.append(f"Still missing for the {self.phase} gate: {len(missing)} of {len(spec.tier_1)} gate fields "
                     f"(not the step count).")
        parts += [display_name(self.phase, f) for f in missing] or ["(none — the gate can open)"]
        if spec.tier_2:
            parts.append("Recommended, not gate-blocking: "
                         + ", ".join(display_name(self.phase, f) for f in spec.tier_2))
        parts.append("</gate_list>")
        parts.append("</project_state>")

        return "\n".join(parts)

    def _compose_move(self) -> str:
        """Section 5 — THIS TURN'S MOVE, from the plan code built: the task, last (ADR-0111 D2).

        Authoritative, and says so (`MOVE_PREAMBLE`). The instruction per move
        is `prompts.MOVE_INSTRUCTIONS`; which one applies, and what it names,
        is decided here from the plan — the coach is never asked to choose.
        """
        plan = self._state.get("coaching_plan")
        if plan is None:
            return f"{SECTION_MOVE}\n(no plan was produced for this turn)"
        field = plan.focus_field
        judgment = getattr(plan, "judgment", None)
        reason = plan.reason or (judgment.reason if judgment is not None else "")
        pending = plan.pending or {}
        words = str(pending.get("belt_words") or plan.answer or "").strip() or "(none yet)"
        structured = False
        if plan.move == moves.READ_BACK:
            # G-137 — the structured fields first, so a read-back of a position never leaves out
            # `metric_definitions` and its Confirm can store the position.
            # The baseline and the target count as words: the coach gives the Belt's words and
            # code reads the MetricValue from them (ADR-0071).
            from backend.phases.define.parse import METRIC_FIELDS as _WORDS
            fields = sorted(pending.get("fields") or [field],
                            key=lambda f: declared_type(self.phase, f) in (None, str)
                            or (self.phase == "define" and f in _WORDS))
            structured = any(declared_type(self.phase, f) not in (None, str) for f in fields)
            composed = (structured or len(fields) > 1 or field in moves.COMPOSED_FIELDS
                        or int(pending.get("messages") or 1) > 1)
            key = "read_back_composed" if composed else "read_back_verbatim"
        elif plan.move == moves.STORE_AND_ADVANCE:
            key = "store_and_advance" if field else "store_and_finish"
            fields = []
        elif plan.move == moves.RESPOND:
            key = "complete" if field is None else ("respond_pending" if pending else "respond")
            fields = []
        else:
            key = plan.move
            fields = []
        shape = (" — in the shape the phase script's 'Capture as' gives for it"
                 if plan.move == moves.READ_BACK and structured else "")
        # DEF-029 — every field of the position named, with its declared type, so a read-back
        # carries the whole position and the Belt's Confirm can store it.
        from backend.phases.define.parse import METRIC_FIELDS
        from backend.phases.define.schema import METRIC_DEFINITION_KEYS
        registry = ("{" + ", ".join(METRIC_DEFINITION_KEYS) + "}")

        def entry(f: str) -> str:
            if self.phase == "define" and f == "metric_definitions":
                # G-137 — the keys named here, and why the entry cannot be left out.
                return (f"list[dict] — a LIST, the primary metric FIRST, each {registry} from the Belt's "
                        f"words; the baseline's number is read by this `unit`, so without this entry "
                        f"nothing of the position can be stored")
            if self.phase == "define" and f in METRIC_FIELDS:
                return ("the Belt's words — the number, its unit and its direction are read from them "
                        "in code (ADR-0071), by the unit `metric_definitions` gives; read them back as "
                        "the Belt wrote them")
            if declared_type(self.phase, f) in (None, str):
                return "a string, in the Belt's words"
            if f in FIELD_SHAPES:   # G-252: the shape rules, for the fields read back
                return f"{FIELD_SHAPES[f]} — real structure, never prose"
            return (f"{declared_type(self.phase, f)} — real structure, the keys the phase script's "
                    f"'Capture as' line gives, never prose")
        entries = "\n".join(f"  - `{f}`: {entry(f)}" for f in fields)
        body = MOVE_INSTRUCTIONS[key].format(
            field=field, stored=plan.stored_field, reason=reason, words=words,
            fields=" and ".join(f"`{f}`" for f in fields), shape=shape, entries=entries)
        if plan.move == moves.READ_BACK and plan.reason.startswith(moves.CONFIRM_INCOMPLETE[:40]):
            body = f"{plan.reason}\n\n{body}"
        if plan.move == moves.READ_BACK:
            body = f"{body}\n\n{CAPTURE_RULES}"
        lines = [SECTION_MOVE, MOVE_PREAMBLE, "",
                 # The status AFTER this turn, as section 3 shows it:
                 # on a store-and-advance the field is the NEXT one, and the
                 # before-status is the confirmed field's, not its.
                 f"Field: {field or '(every field is confirmed)'} — status after this turn: "
                 f"{(plan.statuses or {}).get(field or '', plan.status)}"]
        if judgment is not None:
            lines.append(f"The planner's judgment: {judgment.verdict} — {judgment.reason}")
        if self.phase != "define" and not any(isinstance(m, AIMessage) for m in (self._state.get("messages") or [])):
            # Define's welcome is the server's (DEF-200) and flows into element 1's card (R-A): the coach never repeats it.
            lines.append(MOVE_OPENING)
        from backend.phases import calculations
        if plan.move in (moves.TEACH, moves.STORE_AND_ADVANCE) and calculations.calculation_for(self.phase, field):
            # ADR-0077 point 5 (DEF-016): the calculation is taught before any figure exists.
            from backend.core.prompts import CALCULATION_TEACH
            body = f"{body}\n\n{CALCULATION_TEACH}"
        if plan.move in (moves.TEACH, moves.STORE_AND_ADVANCE, moves.CHALLENGE) and field:
            # C3 (DEF-083): every request shows a sample — the script's worked example,
            # inserted by code (G-170); never built from the case's values.
            from backend.core.prompts import SAMPLE_FROM_SCRIPT
            body = f"{body}\n\n{SAMPLE_FROM_SCRIPT}"
        if self._upload:
            # DEF-108 (W5) — ahead of the move, and named as the one exception to its "nothing
            # else": placed after it, a read-back would obey the preamble and leave the file out.
            u = self._upload
            lines += ["", UPLOAD_TURN.format(
                filename=u.get("filename") or "(unnamed file)",
                summary=cut_at(" ".join(str(u.get("summary") or "(no description)").split()), 600),
                blob_path=u.get("blob_path") or "(unknown)",
                element=f"`{field}`" if field else "the report")]
        return "\n".join([*lines, "", body])

    def _compose_feedback(self) -> str:
        """Section 4 — last turn's quality feedback, for the coach.

        The grader's verdict on the PREVIOUS reply, read off that reply (there
        is no coherence judge, ADR-0083). **Never presented as a message from the Belt** — it is a
        system section, and it says whose it is.
        """
        fb = moves.last_feedback(list(self._state.get("messages") or []))
        lines = [SECTION_FEEDBACK]
        if not fb:
            lines.append("  (none — no quality check ran on your previous reply, or "
                         "there is no previous reply)")
            return "\n".join(lines)
        g = fb.get("grader")
        # Only what applies to THIS turn's move: section 4
        # never contradicts section 5. A criterion the move does not answer
        # (a read-back is not a challenge) is left out, and says so.
        plan = self._state.get("coaching_plan")
        move = getattr(plan, "move", None)
        if g:
            failed = list(g.get("failed") or [{"criterion": c_, "feedback": ""}
                                              for c_ in g.get("criteria_failed") or []])
            # ...and only what applied to the move the reply was GRADED as:
            # a verdict recorded before a criterion was excluded for that
            # move cannot leak through.
            kept = [f for f in failed if applies(str(f.get("criterion")), move, self.phase)
                    and applies(str(f.get("criterion")), g.get("move"), self.phase)]
            if g.get("status") == "pass" or not failed:
                lines.append("  Coaching quality: passed every criterion.")
            elif kept:
                lines.append("  Coaching quality: FAILED on your previous reply — apply "
                             "only within this turn's move:")
                lines += [f"    - {f.get('criterion')}: {f.get('feedback')}".rstrip(": ")
                          for f in kept]
            else:
                lines.append("  Coaching quality: nothing that applies to this turn's move.")
        return "\n".join(lines)

    def _upload_manifest(self) -> list[str]:
        """The uploads INVENTORY — one line per entry, never the content.

        `uploads` has two readers: gate document assembly, and this evidence
        context.

        **This is the guarantee that an upload reaches the coach at all.**
        Retrieval is a tool call the model decides to make — there is no
        unconditional retrieval pipeline — so **no uploaded document is
        guaranteed to be read via `rag_lookup_evidence`**. A coach that never
        calls the tool never sees the file. The manifest is deterministic and
        costs one line per upload: the coach cannot fail to know a file exists,
        though it may still choose not to open it.

        **Inventory, not content.** The values stay in the blob and are loaded
        by `load_evidence_series`, which is what keeps this block from
        growing with the data.
        """
        uploads = list(self._state.get("uploads") or [])
        asks = [a for a in (self._state.get("asks") or [])
                if a.get("status") == "open"]
        if not uploads and not asks:
            return []

        parts = ["", "FILES THE BELT HAS UPLOADED THIS PHASE"]
        if not uploads:
            parts.append("  (none yet)")
        for u in uploads:
            consumed = "consumed" if u.get("consumed_at") else "NOT YET READ"
            summary = " ".join(str(u.get("summary") or "").split())
            parts.append(
                f"  - {u.get('filename') or '(unnamed file)'}: {u.get('role') or 'other evidence'} "
                f"[{u.get('shape_match') or 'unsolicited'}, {consumed}] "
                f"- {cut_at(summary, 160)}"
            )
            parts.append(f"    blob_path: {u.get('blob_path') or '(unknown)'}")
        parts.append("  To use any of these numbers, call load_evidence_series "
                     "with the blob_path above. Never retype a figure.")

        if asks:
            parts += ["", "DATA YOU HAVE ASKED FOR AND NOT YET RECEIVED"]
            for a in asks:
                shape = a.get("expected_shape") or {}
                cols = ", ".join(shape.get("columns") or []) or "unspecified"
                parts.append(f"  - {a.get('role')} - columns: {cols}")
        return parts


__all__ = ["BeforeModelStateInjection"]
