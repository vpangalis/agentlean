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
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from backend.core.substate import PhaseState
from backend.phases.gate_registry import GATE_SPECS, missing_gate_fields
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

    # ── the hook that does the work (B1) ─────────────────────────────────

    def before_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        """Compose the block. Once per turn — never `before_model` (B1)."""
        self._block = self._compose()
        logger.info(
            "%s.state_injection: composed %d chars, %d prior phase(s)",
            self.phase, len(self._block), len(self._prior),
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
        return request.override(
            system_message=SystemMessage(
                content_blocks=[{"type": "text", "text": self._block}, *blocks],
            )
        )

    # ── composition (G-24: shape is not ratified) ────────────────────────

    def _compose(self) -> str:
        artifacts = dict(self._state.get("artifacts") or {})
        spec = GATE_SPECS[self.phase]
        missing = missing_gate_fields(self.phase, artifacts)

        parts = [f"PROJECT STATE — {self.phase.upper()} PHASE",
                 "(established facts; these outrank anything said in "
                 "conversation that contradicts them)"]

        meta = (self._config.get("configurable") or {}).get("case_metadata") or {}
        if meta:
            parts.append("\nTHIS PROJECT")
            parts += [f"  {label}: {meta[key]}"
                      for key, label in (("title", "Project"),
                                         ("belt_level", "Belt level"),
                                         ("leader", "Belt"),
                                         ("department", "Department"))
                      if meta.get(key)]

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

        parts.append("\nCAPTURED THIS PHASE")
        if artifacts:
            parts += [f"  {k}: {_render_value(v)}" for k, v in artifacts.items()]
        else:
            parts.append("  (nothing captured yet)")

        parts.append(f"\nSTILL MISSING FOR THE {self.phase.upper()} GATE "
                     f"({len(missing)} of {len(spec.tier_1)})")
        parts += [f"  {f}" for f in missing] or ["  (none — the gate can open)"]
        if spec.tier_2:
            parts.append("  Recommended, not gate-blocking: "
                         + ", ".join(spec.tier_2))

        return "\n".join(parts)


__all__ = ["BeforeModelStateInjection"]
