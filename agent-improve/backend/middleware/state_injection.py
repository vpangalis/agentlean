"""`BeforeModelStateInjection` — position 1 — procedure step 6.3.

Canonical: **§61.2 — S-C11**. Architecture **§19.1**, §19 (the stack order),
§37 (why the injected prior values are load-bearing).

WHAT IT DOES
    Prepends this phase's project state to the **top** of the prompt: what is
    captured so far, the prior phases' gate documents from the Store, the
    phase's requirements, and what is still missing.

THE HOOK IS `before_agent`, AND THE NAME SAYS OTHERWISE
    B1: fire on `before_agent`, **never `before_model`**, which fires before
    every model call inside a turn and re-injects the same facts repeatedly.

    **The class name is `BeforeModelStateInjection` and its hook is
    `before_agent`.** §61.2 records this as a naming finding — the name says
    the exact thing the architecture corrects in four places — and says
    explicitly that *"renaming is not in this pass's scope"*. So the name is
    kept and the contradiction is written down here rather than silently fixed.

WHY THE WORK IS SPLIT ACROSS TWO HOOKS, AND WHY THAT IS STILL "once per turn"
    Verified against the installed `langchain.agents.middleware`:
    `before_agent(state, runtime)` returns a **state update** — it cannot reach
    the prompt. The prompt is reached through `wrap_model_call(request,
    handler)`, where `ModelRequest` carries `system_message` and `.override()`.

    So: **`before_agent` COMPOSES the block, once per turn** — every read of
    `artifacts`, every Store lookup, every missing-field computation happens
    there and nowhere else. `wrap_model_call` then does a pure
    read-and-prepend of the already-composed string. B1's cost argument is
    satisfied exactly: the expensive half runs once per turn, and the cheap
    half cannot recompute because it has nothing to recompute from.

    (The field is `system_message`, not `system_prompt` — `create_agent` takes
    `system_prompt=`, `ModelRequest` carries `system_message`. Two names for
    adjacent things, checked rather than assumed. §16.3.)

MISSING FIELDS ARE THE GATE'S OWN COMPUTATION
    B3: derive them at injection time, never from a stored list. **And never
    from a second implementation** — `gate_registry.missing_gate_fields` is
    what `validate_{phase}` itself calls (moved there at this step), so the
    prompt and the gate cannot disagree. §5 removed `open_items` from
    `SupervisorState` for the same reason: a stored readiness list is a second
    source of truth that drifts.

    §19.1 names `check_gate_status()` as the reporter. **That tool does not
    exist** — S-F21 assigns it to step 7.1, where `DMAICGateValidator` lands
    (WATCH 25). Deriving directly from the shared function now is not a
    stand-in for it: it is the same computation the tool will report, so 7.1
    swaps the caller and not the answer.

> **SPEC-GAP (G-24) is OPEN and this file does not close it.** §61.2:
> *"constructor arguments, the exact composition of the injected block, and its
> token budget are unstated — to be designed with founder."* What is below is
> the minimum the ratified behaviours require, composed from values that
> already exist. **The block's composition and its token budget remain a
> founder decision**; nothing here should be read as settling them.
"""
from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Optional

from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import ModelRequest
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from backend.core.prompts import (
    MOVE_INSTRUCTIONS,
    MOVE_OPENING,
    MOVE_PREAMBLE,
    SECTION_CONVERSATION,
    SECTION_FEEDBACK,
    SECTION_MOVE,
    SECTION_RULES,
    SECTION_STATE,
)
from backend.core.substate import PhaseState
from backend.middleware.grader import applies
from backend.phases import moves
from backend.phases.define.schema import define_progress
from backend.phases.gate_registry import GATE_SPECS, declared_type, missing_gate_fields
from backend.phases.mappers_common import PHASE_ORDER

logger = logging.getLogger(__name__)


def _render_value(value: Any, limit: int = 300) -> str:
    """One captured value, flattened for the prompt.

    Structured fields (§10.8's three dicts, the reference dicts, the registry)
    are shown as their sub-keys rather than as repr, because what the coach
    needs from them is which parts are filled.
    """
    if isinstance(value, dict):
        return "{" + ", ".join(
            f"{k}: {str(v)[:60]}" for k, v in value.items() if v
        ) + "}"
    if isinstance(value, list):
        return "; ".join(str(v)[:80] for v in value)[:limit]
    return str(value)[:limit]


class BeforeModelStateInjection(AgentMiddleware):
    """Position 1. Project facts at the top of the prompt, once per turn.

    Constructed per turn with the phase's own state, because the executor
    builds the agent per turn (step 6.2). **G-24 leaves the constructor
    unstated**; these three arguments are what the ratified behaviours need and
    no more — the phase, the state they are read from, and the config that
    carries the case framing.
    """

    name = "BeforeModelStateInjection"

    def __init__(
        self,
        phase: str,
        state: PhaseState,
        config: Optional[RunnableConfig] = None,
        prior_documents: Optional[dict[str, dict]] = None,
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
        #: **B5** — without these the coach has nothing to compare against and
        #: the semantic contradiction check (§37) silently detects nothing.
        self._prior = prior_documents or {}
        self._block: str = ""
        self._move: str = ""
        self._feedback: str = ""

    # ── the hook that does the work (B1) ─────────────────────────────────

    def before_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        """Compose sections 3, 4 and 5. Once per turn — never `before_model` (B1)."""
        self._block = self._compose()
        self._move = self._compose_move()
        self._feedback = self._compose_feedback()
        logger.info(
            "%s.state_injection: composed state %d chars, move %d, feedback %d, "
            "%d prior phase(s)",
            self.phase, len(self._block), len(self._move), len(self._feedback),
            len(self._prior),
        )
        return None

    async def abefore_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        """Async twin — §1.4 makes the agent loop async, so this is the one
        that actually fires. It does no I/O; composition is pure."""
        return self.before_agent(state, runtime)

    # ── where the block reaches the prompt (B2) ──────────────────────────

    def wrap_model_call(self, request: ModelRequest, handler: Callable) -> Any:
        return handler(self._prepend(request))

    async def awrap_model_call(
        self, request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[Any]],
    ) -> Any:
        return await handler(self._prepend(request))

    def _prepend(self, request: ModelRequest) -> ModelRequest:
        """Project facts ABOVE the coach's instructions and the conversation.

        **B2** — models weight earlier content more heavily, and facts arriving
        after the Belt's message let the response drift toward the Belt's
        framing rather than the project's established state. *"Injecting in
        `messages[]` append order is a violation — there is no 'just add it to
        the history' option."* This never touches `request.messages`.

        A pure read of what `before_agent` composed: no recomputation here, or
        the once-per-turn guarantee would be decorative.

        **Content BLOCKS, never string concatenation onto `.content`** (§21,
        CLAUDE.md §4.5). `SystemMessage.content` is `str | list[dict]`, so an
        f-string over a multi-part message renders the literal
        ``"[{'type': 'text', ...}]"`` into the prompt — structure destroyed,
        no error raised. This is the same rule step 2.6 applied across twenty
        `response.content` sites, and it binds on messages this code WRITES,
        not only on ones it reads.

        `.content_blocks` normalises both shapes to typed blocks, and
        `content_blocks=` is accepted at construction (verified against the
        installed langchain-core 1.6.0), so prepending is a list operation.
        """
        if not self._block:
            return request
        existing = request.system_message
        blocks = list(existing.content_blocks) if existing is not None else []
        # 6.61 — THE SIX SECTIONS (§19.1 v1.75), in the ruled order. The rules
        # are the agent's own system prompt, labelled here as section 1 by a
        # heading block of their own (their blocks are never concatenated —
        # §21). Section 2, the phase script, is placed after section 1 by
        # position 2 (`DMAICSkillsMiddleware`), which runs inside this wrap.
        return request.override(
            system_message=SystemMessage(content_blocks=[
                {"type": "text", "text": SECTION_RULES}, *blocks,
                {"type": "text", "text": self._block},
                {"type": "text", "text": self._move},
                {"type": "text", "text": self._feedback},
                {"type": "text", "text": SECTION_CONVERSATION},
            ])
        )

    # ── composition (G-24: shape is not ratified) ────────────────────────

    def _compose(self) -> str:
        # 6.61 (item 2) — THE STATE AFTER THIS TURN'S CHANGE, so sections 3
        # and 4 agree: on a confirming turn the value is shown stored, the step
        # advanced and the next field current — which is what section 4 tells
        # the coach to say.
        plan = self._state.get("coaching_plan")
        artifacts = {**dict(self._state.get("artifacts") or {}),
                     **dict(getattr(plan, "store", None) or {})}
        spec = GATE_SPECS[self.phase]
        missing = missing_gate_fields(self.phase, artifacts)

        parts = [SECTION_STATE,
                 f"PROJECT STATE — {self.phase.upper()} PHASE",
                 "(established facts; these outrank anything said in "
                 "conversation that contradicts them)"]

        # 6.57 — the Belt's step, COMPUTED and delivered every turn, as v1.71
        # delivers the script. The coach used to count it and counted the
        # gate list below ("13 of 13"). First, so it is the number read first.
        if self.phase == "define":
            step = define_progress(artifacts)
            parts += ["\nWHERE THE BELT IS — computed, not yours to count",
                      f"  {step['label']} — {step['field']}",
                      "  Write this exact text in `progress`. Never count steps "
                      "yourself, and never from the gate list below."]

        meta = (self._config.get("configurable") or {}).get("case_metadata") or {}
        if meta:
            parts.append("\nTHIS PROJECT")
            parts += [f"  {label}: {meta[key]}"
                      for key, label in (("title", "Project"),
                                         ("belt_level", "Belt level"),
                                         ("leader", "Belt"),
                                         ("department", "Department"))
                      if meta.get(key)]

        # ── phase_context — §9's SECOND named consumer (step 6.8) ────
        #
        # §9 names two readers of `phase_context`, "the planner; state
        # injection (§19.1)", and until 6.8 NEITHER existed. The field was
        # composed at every phase entry by all five input mappers and thrown
        # away, which is why nothing broke and nothing was noticed for six
        # steps (WATCH 19, `DECISIONS.md` Part AM).
        #
        # **This is not a duplicate of THIS PROJECT above.** That block is the
        # case metadata riding on `config` — the v1 seam, deleted at 11.1.
        # This is the phase's own composed framing: for Define the case record,
        # and for the other four **the prior phase's APPROVED gate values**,
        # which is the only route by which a Measure coach learns what Define
        # committed to. The two overlap for Define and do not for the rest.
        context = str(self._state.get("phase_context") or "").strip()
        parts.append("\nHOW THIS PHASE WAS ENTERED")
        if context:
            parts.append(f"  {context}")
        else:
            # Silence is what hid this for six steps. Say it in the block the
            # trace shows, not only in the log.
            logger.warning(
                "%s.state_injection: phase_context is EMPTY — the coach is "
                "being framed without the case record or the prior gate "
                "document. The input mapper composes it at phase entry, so an "
                "empty value here means it did not reach state.", self.phase,
            )
            parts.append("  [!] No phase framing was composed for this turn.")

        if self._prior:
            parts.append("\nAPPROVED IN EARLIER PHASES — gate-committed, "
                         "do not contradict without flagging (§37)")
            for name in PHASE_ORDER:
                doc = self._prior.get(name)
                if not doc:
                    continue
                parts.append(f"  [{name}]")
                parts += [f"    {k}: {_render_value(v)}"
                          for k, v in doc.items()
                          if v and not k.startswith("_")]

        parts.append("\nCONFIRMED BY THE BELT AND STORED THIS PHASE")
        if artifacts:
            parts += [f"  {k}: {_render_value(v)}" for k, v in artifacts.items()]
        else:
            parts.append("  (nothing stored yet)")

        # 6.61 (R5) — every position's stored status, after this turn's change,
        # the current field, and the value awaiting confirmation.
        statuses = dict(getattr(plan, "statuses", None) or {})
        if statuses:
            parts.append("\nFIELD STATUS — stored, after this turn "
                         "(not taught / asked / answered / confirmed)")
            parts += [f"  {i}. {f} — {s}" for i, (f, s) in enumerate(statuses.items(), 1)]
            parts.append("  CURRENT FIELD: "
                         + (getattr(plan, "focus_field", None) or "(every field is confirmed)"))
        pending = getattr(plan, "pending", None) if plan is not None else None
        if pending:
            parts.append("\nPENDING — an answer awaiting the Belt's confirmation; NOT stored")
            parts.append(f"  field: {pending.get('field')}")
            parts.append(f"  the Belt's words: {pending.get('belt_words')}")
            if pending.get("store"):
                parts.append("  what the Belt's yes stores: "
                             + "; ".join(f"{k} = {_render_value(v, 600)}"
                                         for k, v in pending["store"].items()))

        parts += self._upload_manifest()

        # 6.57 — labelled as the GATE's list, so its "n of 13" is not read as
        # the Belt's step: Define gates on 13 fields and walks 12 steps.
        parts.append(f"\nTHE GATE LIST — STILL MISSING FOR THE {self.phase.upper()} "
                     f"GATE ({len(missing)} of {len(spec.tier_1)} gate fields; "
                     f"not the step count)")
        parts += [f"  {f}" for f in missing] or ["  (none — the gate can open)"]
        if spec.tier_2:
            parts.append("  Recommended, not gate-blocking: "
                         + ", ".join(spec.tier_2))

        return "\n".join(parts)

    def _compose_move(self) -> str:
        """Section 4 — THIS TURN'S MOVE, from the plan code built (6.61).

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
            fields = list(pending.get("fields") or [field])
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
        body = MOVE_INSTRUCTIONS[key].format(
            field=field, stored=plan.stored_field, reason=reason, words=words,
            fields=" and ".join(f"`{f}`" for f in fields), shape=shape)
        lines = [SECTION_MOVE, MOVE_PREAMBLE, "",
                 # Fix 2 — the status AFTER this turn, as section 3 shows it:
                 # on a store-and-advance the field is the NEXT one, and the
                 # before-status is the confirmed field's, not its.
                 f"Field: {field or '(every field is confirmed)'} — status after this turn: "
                 f"{(plan.statuses or {}).get(field or '', plan.status)}"]
        if judgment is not None:
            lines.append(f"The planner's judgment: {judgment.verdict} — {judgment.reason}")
        if not any(isinstance(m, AIMessage) for m in (self._state.get("messages") or [])):
            lines.append(MOVE_OPENING)
        return "\n".join([*lines, "", body])

    def _compose_feedback(self) -> str:
        """Section 5 — last turn's quality feedback, for the coach (6.61).

        The grader's and coherence's verdicts on the PREVIOUS reply, read off
        that reply. **Never presented as a message from the Belt** — it is a
        system section, and it says whose it is.
        """
        fb = moves.last_feedback(list(self._state.get("messages") or []))
        lines = [SECTION_FEEDBACK]
        if not fb:
            lines.append("  (none — no quality check ran on your previous reply, or "
                         "there is no previous reply)")
            return "\n".join(lines)
        g, c = fb.get("grader"), fb.get("coherence")
        # 6.61 (item 3) — only what applies to THIS turn's move: section 5
        # never contradicts section 4. A criterion the move does not answer
        # (a read-back is not a challenge) is left out, and says so.
        plan = self._state.get("coaching_plan")
        move = getattr(plan, "move", None)
        if g:
            failed = list(g.get("failed") or [{"criterion": c_, "feedback": ""}
                                              for c_ in g.get("criteria_failed") or []])
            # ...and only what applied to the move the reply was GRADED as:
            # a verdict recorded before a criterion was excluded for that
            # move cannot leak through.
            kept = [f for f in failed if applies(str(f.get("criterion")), move)
                    and applies(str(f.get("criterion")), g.get("move"))]
            if g.get("status") == "pass" or not failed:
                lines.append("  Coaching quality: passed every criterion.")
            elif kept:
                lines.append("  Coaching quality: FAILED on your previous reply — apply "
                             "only within this turn's move:")
                lines += [f"    - {f.get('criterion')}: {f.get('feedback')}".rstrip(": ")
                          for f in kept]
            else:
                lines.append("  Coaching quality: nothing that applies to this turn's move.")
        if c:
            lines.append("  Coherence: " + ("coherent" if c.get("coherent") else
                                            f"NOT coherent — {c.get('reason') or ''}"))
        return "\n".join(lines)

    def _upload_manifest(self) -> list[str]:
        """The uploads INVENTORY — one line per entry, never the content.

        **§6 names two readers of `uploads`: "gate document assembly; evidence
        context". Gate assembly was wired; THIS ONE NEVER WAS** — verified
        against the tree at step 6.12 and recorded as a defect found rather
        than a gap filled (`DECISIONS.md` Part AS). Third instance of the
        WATCH-19 shape: a field declared, written, and read by nothing.

        **This is the guarantee that an upload reaches the coach at all.**
        §24 makes retrieval a tool call the model decides to make — *"there is
        no unconditional retrieval pipeline"* — so **no uploaded document is
        guaranteed to be read via `rag_lookup_evidence`**. A coach that never
        calls the tool never sees the file. The manifest is deterministic and
        costs one line per upload: the coach cannot fail to know a file exists,
        though it may still choose not to open it.

        **Inventory, not content.** The values stay in the blob and are loaded
        by `load_evidence_series` (S-F57), which is what keeps this block from
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
                f"  - {u.get('role') or 'other evidence'} "
                f"[{u.get('shape_match') or 'unsolicited'}, {consumed}] "
                f"- {summary[:160]}"
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
