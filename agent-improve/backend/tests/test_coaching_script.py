"""The coaching script reaches the model every turn, or its absence is recorded
— procedure step 6.46, Part B (founder ruling 2026-09-24: option A).

WHAT PART A MEASURED
--------------------
`load_skill` was called ZERO times in the last 30 traced turns on
IMPR-2026-0E5 (2026-09-15 .. 09-24). The tool was bound and offered, the
catalogue told the coach to load Define first — and the system prompt told it
*"`load_skill` IS A WHOLE TURN"*. A mechanism that relies on the model choosing
to call a tool cannot guarantee anything; 0 in 30 is the proof.

OPTION A, TESTED HERE
---------------------
`DMAICSkillsMiddleware` puts the current phase's full SKILL.md into the system
message on EVERY model call (`wrap_model_call`, beside the catalogue) — never a
tool result, so nothing is added to the conversation. Each delivery is
recorded, and the executor writes one `coaching_script` entry per turn to
`step_log`: script, version, content hash, delivered true/false.

THE §22 GUARD, WHICH THIS STEP MAKES LOAD-BEARING
-------------------------------------------------
Once the script arrives, so do its worked examples — each a plausible value for
the field it illustrates. A captured value that matches a worked example is
REFUSED and recorded. The matching rule is `skills.example_match`.
"""
from __future__ import annotations

import asyncio
import hashlib
from typing import Any, cast

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from backend.tests.conftest import store_plan
from backend.core.prompts import PHASE_COACH_PROMPT
from backend.core.substate import CoachingResponse, PhaseState
from backend.middleware.skills import script_section, DMAICSkillsMiddleware, instructions
from backend.phases import nodes_common as _nc

SCRIPT = instructions("define")
SCRIPT_HASH = hashlib.sha256(SCRIPT.encode("utf-8")).hexdigest()[:16]
#: SKILL.md's own worked example for `business_case`, verbatim.
EXAMPLE = ("Invoice errors cost ~€35k/month in rework and delayed payments, and "
           "billing complaints rose 40% this year. Fixing this protects revenue "
           "and frees two staff currently spending half their week on corrections.")
BELT_OWN = ("Pricing mistakes on our supplier invoices take the AP team about "
            "ninety hours a month to fix, and two key clients have escalated.")


class _FakeRequest:
    def __init__(self, system_message: SystemMessage | None) -> None:
        self.system_message = system_message
        self.messages = ["untouched"]

    def override(self, **kw: Any) -> "_FakeRequest":
        out = _FakeRequest(kw.get("system_message", self.system_message))
        out.messages = self.messages
        return out


def _texts(message: SystemMessage) -> list[str]:
    """Text of each block — the narrowing `test_middleware._texts` uses: the
    test built text blocks itself, so the cast is honest."""
    blocks = cast(list[dict[str, Any]], message.content_blocks)
    return [str(b.get("text", "")) for b in blocks if b.get("type") == "text"]


def test_the_system_message_carries_the_current_fields_script_on_every_call() -> None:
    """6.46's guarantee, narrowed by 6.61 (item 4, founder): every model call
    carries the script — since 6.61 the opening (first turn only) and the
    CURRENT field's block, not all 31k characters. The delivery record still
    names the whole SKILL.md by version and hash (row 3 reads it)."""
    delivered: list[dict[str, Any]] = []
    mw = DMAICSkillsMiddleware("define", on_delivery=delivered.append,
                               focus_field="business_case", opening=True)
    mw.before_agent(None, None)
    seen: list[Any] = []

    async def handler(request: Any) -> Any:
        seen.append(request)
        return "reply"

    request = _FakeRequest(SystemMessage(content="COACH INSTRUCTIONS"))
    for _ in range(2):                                  # two model calls, one turn
        asyncio.run(mw.awrap_model_call(cast(Any, request), handler))

    part = script_section("define", "business_case", True)
    for req in seen:
        texts = _texts(req.system_message)
        assert part in texts, "the model call went out without its script section"
        assert "[OPENING" in part and "[1 · business_case" in part
        assert "[2 · team" not in part, "another field's block was delivered"
    assert req.messages == ["untouched"], "the script must never enter the conversation"
    assert len(delivered) == 2
    assert {k: delivered[0][k] for k in ("script", "version", "sha256", "chars")} == {
        "script": "dmaic-define-phase", "version": "1.3",
        "sha256": SCRIPT_HASH, "chars": len(SCRIPT)}
    assert delivered[0]["delivered_part"] == "opening + business_case"
    assert delivered[0]["sections"] == ["## 2 · PHASE SCRIPT — what to teach"]


def test_the_system_prompt_no_longer_calls_load_skill_a_whole_turn() -> None:
    assert "IS A WHOLE TURN" not in PHASE_COACH_PROMPT["define"]


# ── the record, through the real executor ────────────────────────────────


def _state() -> PhaseState:
    base: PhaseState = {
        "case_id": "IMPR-TEST-646", "current_phase": "define",
        "messages": [HumanMessage(content="why is my project worth doing?")],
        "history": [], "phase_context": "", "coaching_plan": None,
        "field_index": 0, "draft": {}, "artifacts": {}, "step_log": [],
        "field_log": [], "field_status": {}, "belt_edits": {}, "turn_count": 0, "final": {},
        "gate_attempts": 0, "validator_feedback": [], "rejection_feedback": [],
        "citations": [], "uploads": [], "asks": [], "hop_results": [],
        "synthesis_output": None,
    }
    return base


class _Agent:
    """The coach reduced to one model call through the REAL skills middleware
    the executor mounted (or none, when `call_model` is False)."""

    def __init__(self, middleware: list[Any], reply: CoachingResponse,
                 call_model: bool) -> None:
        self.skills = next(m for m in middleware if isinstance(m, DMAICSkillsMiddleware))
        self.reply, self.call_model = reply, call_model

    async def ainvoke(self, payload: dict, *_: Any, **__: Any) -> dict:
        if self.call_model:
            self.skills.before_agent(None, None)

            async def handler(request: Any) -> Any:
                return "reply"
            await self.skills.awrap_model_call(
                cast(Any, _FakeRequest(SystemMessage(content="COACH"))), handler)
        return {"messages": [*payload["messages"], AIMessage(content=self.reply.message)],
                "structured_response": self.reply}


def _run(monkeypatch, reply: CoachingResponse, call_model: bool = True) -> dict:
    monkeypatch.setattr(_nc, "create_agent",
                        lambda **kw: _Agent(kw["middleware"], reply, call_model))
    return asyncio.run(_nc.executor("define", {**_state(), "coaching_plan": store_plan(reply)}))


def _reply(value: Any, field: str = "business_case") -> CoachingResponse:
    return CoachingResponse(explanation="", example="", prompt="", progress="",
                            message="Noted.", fields_captured=[
                                {"field_name": field, "value": value, "source": "belt"}])


def test_step_log_records_that_the_script_was_delivered(monkeypatch, stub_planner) -> None:
    out = _run(monkeypatch, _reply(BELT_OWN))
    entries = [e for e in out["step_log"] if e.get("node") == "coaching_script"]
    assert entries, f"no coaching_script entry: {[e.get('node') for e in out['step_log']]}"
    e = entries[0]
    assert (e["delivered"], e["script"], e["version"], e["sha256"]) == (
        True, "dmaic-define-phase", "1.3", SCRIPT_HASH)


def test_a_turn_without_the_script_is_distinguishable(monkeypatch, stub_planner) -> None:
    """**The Done-when.** No model call → nothing delivered → the record says so."""
    out = _run(monkeypatch, _reply(BELT_OWN), call_model=False)
    e = [e for e in out["step_log"] if e.get("node") == "coaching_script"][0]
    assert e["delivered"] is False


def test_a_worked_example_is_refused_as_the_belts_data(monkeypatch, stub_planner) -> None:
    """**§22.** The script's own example, captured as the Belt's business case."""
    out = _run(monkeypatch, _reply(EXAMPLE))
    assert "business_case" not in out["artifacts"], "a worked example was captured as data"
    ex = out["step_log"][0]
    assert "business_case" in ex["fields_example_refused"]


def test_the_belts_own_answer_is_kept(monkeypatch, stub_planner) -> None:
    out = _run(monkeypatch, _reply(BELT_OWN))
    assert out["artifacts"]["business_case"] == BELT_OWN
    assert not out["step_log"][0].get("fields_example_refused")


def test_a_lightly_edited_example_is_still_refused(monkeypatch, stub_planner) -> None:
    """The rule is not exact-match: the example with its numbers kept and a
    word changed is still the example."""
    edited = EXAMPLE.replace("~€35k/month", "about €35k a month").replace("Fixing", "Solving")
    out = _run(monkeypatch, _reply(edited))
    assert "business_case" not in out["artifacts"]
