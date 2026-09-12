"""Middleware positions 1–3 — what procedure step 6.3 established.

Verify for the step is `trace-check`; what is pinned here is everything the
trace cannot show. Three things would be silent if they broke:

  * **the hook** — `before_agent` vs `before_model` is a cost and correctness
    difference the trace shows only as extra tokens, and S-C11 B1 names it;
  * **the order** — the declared list is NESTING order and the position numbers
    are EXECUTION order, opposite for `after_*` (§19). Position 1 being FIRST is
    what puts project facts above skills loading and summarisation, and that
    follows from the `before_*` clause specifically — first-to-last — not from
    any single rule covering all three hook kinds;
  * **the missing-field agreement** — §19.1's whole point. A coach asking for a
    field the gate does not want, or silent about one it does, is a bug nobody
    sees until a gate refuses to open.

The parameter names for `SummarizationMiddleware` are checked against the
INSTALLED class rather than against §19.3's code block, for the reason
CLAUDE.md §0.10 records: `retries=` vs `max_retries=` sat wrong inside the
canonical block for months because nothing checked it.
"""
from __future__ import annotations

import asyncio
import inspect
from typing import Any, cast

import pytest
from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    ModelRetryMiddleware,
    SummarizationMiddleware,
    ToolRetryMiddleware,
)
from langchain_core.language_models.fake_chat_models import (
    GenericFakeChatModel,
)
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.tools import tool

from backend.core.substate import CoachingPlan, PhaseState
from backend.knowledge.computation import COMPUTATION_TOOLS_BY_PHASE
from backend.knowledge.tools import UNIVERSAL_TOOLS
from backend.middleware.skills import (
    LEVEL_1_TOKEN_BUDGET,
    SKILL_DIRS,
    DMAICSkillsMiddleware,
    allowed_tools,
    description,
    instructions,
)
from backend.core.substate import CONTRADICTION_FLAG_KEYS, CoachingResponse
from backend.middleware import coherence as coherence_module
from backend.middleware import contradiction as contradiction_module
from backend.middleware import grader as grader_module
from backend.middleware.coherence import COHERENCE_MAX_RETRIES, SKIP_GRADER_KEY, CoherenceMiddleware
from backend.middleware.contradiction import ContradictionDetectionMiddleware
from backend.middleware.grader import (
    GRADER_MAX_ITERATIONS,
    MAX_ITERATIONS_WARNING,
    DMAICGraderMiddleware,
)
from backend.middleware.state_injection import BeforeModelStateInjection
from backend.validation.schemas import (
    CoachingGraderVerdict,
    CoherenceResult,
    CriterionResult,
)
from backend.phases import nodes_common as _c
from backend.phases.gate_registry import GATE_SPECS, missing_gate_fields
from backend.phases.mappers_common import PHASE_ORDER


def _state(**overrides: Any) -> PhaseState:
    base: PhaseState = {
        "case_id": "IMPR-TEST-63", "current_phase": "define",
        "messages": [], "history": [], "phase_context": "",
        "coaching_plan": None, "field_index": 0, "draft": {}, "artifacts": {},
        "step_log": [], "belt_edits": {}, "turn_count": 0, "final": {},
        "gate_attempts": 0, "validator_feedback": [], "rejection_feedback": [],
        "citations": [], "uploads": [], "asks": [], "hop_results": [],
        "synthesis_output": None,
    }
    base.update(overrides)  # type: ignore[typeddict-item]
    return base


def _texts(message: Any) -> list[str]:
    """The text of each content block.

    `.content_blocks` is a union of TypedDicts and only some carry `text`, so
    the cast is the honest narrowing for a test that constructed text blocks
    itself — not a silencing of a real union the production code has to handle.
    """
    blocks = cast(list[dict[str, Any]], message.content_blocks)
    return [str(b.get("text", "")) for b in blocks]


def _block(phase: str = "define", **kw: Any) -> str:
    mw = BeforeModelStateInjection(phase, _state(**kw.pop("state", {})), **kw)
    mw.before_agent(None, None)
    return mw._block


# ══════════════════════════════════════════════════════════════════════════
# Position 1 — BeforeModelStateInjection
# ══════════════════════════════════════════════════════════════════════════


def test_the_hook_is_before_agent_not_before_model() -> None:
    """**S-C11 B1**, and the one thing the class name argues against.

    `before_model` fires before every model call inside a turn, so the same
    project facts would be re-injected on every tool round-trip. The check is
    that the class overrides `before_agent` and does NOT override
    `before_model` — inheriting the base no-op is what makes that true.
    """
    assert "before_agent" in BeforeModelStateInjection.__dict__
    assert "abefore_agent" in BeforeModelStateInjection.__dict__
    assert "before_model" not in BeforeModelStateInjection.__dict__, (
        "overriding before_model re-injects the same facts on every model "
        "call within a turn — S-C11 B1 forbids exactly this"
    )


def test_composition_happens_once_per_turn_not_per_model_call() -> None:
    """B1's cost argument, made checkable.

    `wrap_model_call` must be a pure read of what `before_agent` composed. If
    it recomputed, the once-per-turn guarantee would be decorative — so the
    test empties the composed block and checks the prompt is left alone.
    """
    mw = BeforeModelStateInjection("define", _state())
    mw.before_agent(None, None)
    assert mw._block

    mw._block = ""
    request = _FakeRequest(SystemMessage(content="coach instructions"))
    assert mw._prepend(cast(Any, request)) is request, (
        "wrap_model_call recomputed instead of reading — B1"
    )


class _FakeRequest:
    """The two `ModelRequest` members `_prepend` touches."""

    def __init__(self, system_message: SystemMessage | None) -> None:
        self.system_message = system_message
        self.messages = ["untouched"]

    def override(self, **kw: Any) -> "_FakeRequest":
        out = _FakeRequest(kw.get("system_message", self.system_message))
        out.messages = self.messages
        return out


def test_facts_go_above_the_coach_instructions_never_into_messages() -> None:
    """**S-C11 B2.** *"Injecting in `messages[]` append order is a violation."*

    Models weight earlier content more heavily, and facts arriving after the
    Belt's message let the response drift toward the Belt's framing.
    """
    mw = BeforeModelStateInjection("define", _state())
    mw.before_agent(None, None)
    request = _FakeRequest(SystemMessage(content="COACH INSTRUCTIONS"))
    out = mw._prepend(cast(Any, request))

    assert out.system_message is not None
    text = str(out.system_message.content)
    assert text.index("PROJECT STATE") < text.index("COACH INSTRUCTIONS"), (
        "project facts must be ABOVE the coach's instructions (B2)"
    )
    assert out.messages == ["untouched"], "B2 — messages[] is not the channel"


def test_injection_uses_content_blocks_not_string_concatenation() -> None:
    """**§21 / CLAUDE.md §4.5** — the rule step 2.6 applied across 20 sites.

    `SystemMessage.content` is `str | list[dict]`. Concatenating with an
    f-string over a MULTI-PART message renders the literal
    ``"[{'type': 'text', ...}]"`` into the prompt: structure destroyed, no
    error raised, and the coach silently reads a Python repr.

    The fixture is deliberately a list-content message, because a string one
    passes either way — which is why the original defect survived review until
    it was asked about.
    """
    mw = BeforeModelStateInjection("define", _state())
    mw.before_agent(None, None)
    multipart = SystemMessage(content=[
        {"type": "text", "text": "COACH PART ONE"},
        {"type": "text", "text": "COACH PART TWO"},
    ])
    out = mw._prepend(cast(Any, _FakeRequest(multipart)))

    assert out.system_message is not None
    texts = _texts(out.system_message)
    assert texts[1:] == ["COACH PART ONE", "COACH PART TWO"], (
        "the existing blocks were not preserved intact"
    )
    assert "PROJECT STATE" in texts[0], "B2 — facts go first"
    assert len(texts) == 3

    # **The check is per BLOCK, not on `.content`.** A multi-part message's
    # `.content` is a list and reprs as one — correctly. The failure being
    # guarded is a repr flattened INTO a block's text, which is what the old
    # f-string produced.
    assert not any("'type': 'text'" in t for t in texts), (
        "a Python repr was flattened into a text block — the §4.5 failure"
    )


def test_skills_catalogue_also_uses_content_blocks() -> None:
    """Position 2 runs AFTER position 1, so its input is already multi-part.

    That makes this the site where string concatenation would actually have
    bitten in production rather than only in a contrived test.
    """
    mw = DMAICSkillsMiddleware("define")
    mw.before_agent(None, None)
    multipart = SystemMessage(content=[
        {"type": "text", "text": "PROJECT STATE ..."},
        {"type": "text", "text": "COACH INSTRUCTIONS"},
    ])
    out = mw._append_catalogue(cast(Any, _FakeRequest(multipart)))

    texts = _texts(out.system_message)
    assert texts[:2] == ["PROJECT STATE ...", "COACH INSTRUCTIONS"]
    assert "AVAILABLE COACHING SKILLS" in texts[-1]
    assert not any("'type': 'text'" in t for t in texts)


def test_the_two_middlewares_compose_without_flattening() -> None:
    """Both hooks in sequence — the shape the model actually receives.

    Four blocks, in order: project state, the coach's two parts, then skills.
    A flattening bug in EITHER site shows up here as a repr in the text.
    """
    inject = BeforeModelStateInjection("define", _state())
    skills = DMAICSkillsMiddleware("define")
    inject.before_agent(None, None)
    skills.before_agent(None, None)

    request: Any = _FakeRequest(SystemMessage(content=[
        {"type": "text", "text": "COACH PART ONE"},
        {"type": "text", "text": "COACH PART TWO"},
    ]))
    request = inject._prepend(request)
    request = skills._append_catalogue(request)

    texts = _texts(request.system_message)
    assert len(texts) == 4
    assert "PROJECT STATE" in texts[0]
    assert texts[1:3] == ["COACH PART ONE", "COACH PART TWO"]
    assert "AVAILABLE COACHING SKILLS" in texts[3]
    assert not any("'type': 'text'" in t for t in texts)


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_missing_fields_are_the_gates_own_computation(phase: str) -> None:
    """**S-C11 B3, and the drift this step was most likely to introduce.**

    The block must name exactly what `missing_gate_fields` names — the same
    function `validate_{phase}` calls. Not a parallel loop that agrees today.
    """
    artifacts = {GATE_SPECS[phase].tier_1[0]: "supplied"}
    block = _block(phase, state={"artifacts": artifacts,
                                 "current_phase": phase})
    expected = missing_gate_fields(phase, artifacts)

    assert expected, "fixture should leave something missing"
    for field in expected:
        assert field in block, f"{field} missing from the injected block"
    assert GATE_SPECS[phase].tier_1[0] not in block.split("STILL MISSING")[1], (
        "a captured field was reported as missing"
    )


def test_the_validators_and_the_middleware_share_one_implementation() -> None:
    """§19.1 — *"the prompt and `DMAICGateValidator` cannot disagree"*.

    Checked structurally, not by comparing two outputs that happen to match:
    the five validators must call the shared function, and must no longer
    carry a local Tier-1 loop of their own.
    """
    import importlib

    for phase in PHASE_ORDER:
        mod = importlib.import_module(f"backend.phases.{phase}.validate")
        source = inspect.getsource(mod)
        assert "missing_gate_fields" in source, (
            f"{phase}/validate.py does not use the shared computation"
        )
        assert "def _missing_structured" not in source, (
            f"{phase}/validate.py still carries its own structured check — "
            f"that is the second implementation §19.1 forbids"
        )


def test_missing_fields_are_derived_never_read_from_a_stored_list() -> None:
    """**B3** — and §5 removed `open_items` for the same reason.

    Capturing a field must change the block on the very next composition, with
    nothing to invalidate.
    """
    empty = _block(state={"artifacts": {}})
    filled = _block(state={"artifacts": {"business_case": "£120k a year"}})
    assert "business_case" in empty.split("STILL MISSING")[1]
    assert "business_case" not in filled.split("STILL MISSING")[1]


def test_prior_phase_values_are_injected(tmp_path: Any) -> None:
    """**B5** — without them the coach has nothing to compare against and
    §37's contradiction check silently detects nothing."""
    mw = BeforeModelStateInjection(
        "measure", _state(current_phase="measure"),
        config={"configurable": {}},
        prior_documents={"define": {"baseline_estimate": "12.3%"}},
    )
    mw.before_agent(None, None)
    assert "APPROVED IN EARLIER PHASES" in mw._block
    assert "baseline_estimate" in mw._block and "12.3%" in mw._block


def test_only_earlier_phases_are_treated_as_approved() -> None:
    """A later phase's values are not committed and must not be presented so."""
    prior = _c._prior_gate_documents("measure", {"configurable": {
        "v1_phase_inputs": {"define": {"a": "1"}, "measure": {"b": "2"},
                            "control": {"c": "3"}},
    }})
    assert set(prior) == {"define"}


def test_an_unknown_phase_is_refused() -> None:
    with pytest.raises(ValueError, match="Unknown phase"):
        BeforeModelStateInjection("discover", _state())


# ══════════════════════════════════════════════════════════════════════════
# Position 2 — DMAICSkillsMiddleware
# ══════════════════════════════════════════════════════════════════════════


def test_level_1_is_under_the_two_thousand_token_budget() -> None:
    """**S-C12 B1** — all five descriptions, at startup, under 2K combined."""
    from langchain_core.messages.utils import count_tokens_approximately

    total = sum(
        count_tokens_approximately([{"role": "user", "content": description(p)}])
        for p in PHASE_ORDER
    )
    assert 0 < total < LEVEL_1_TOKEN_BUDGET, (
        f"the five descriptions cost ~{total} tokens, over B1's "
        f"{LEVEL_1_TOKEN_BUDGET} budget"
    )


def test_level_2_is_much_larger_than_level_1_which_is_the_point() -> None:
    """Progressive disclosure only earns its complexity if the levels differ."""
    for phase in PHASE_ORDER:
        assert len(instructions(phase)) > 10 * len(description(phase)), phase


def test_level_1_is_actually_DELIVERED_not_just_composed() -> None:
    """**The gap 6.3's trace-check found.**

    The first draft logged that the catalogue was "offered" and put it nowhere,
    leaving the coach holding a `load_skill` tool with no idea what was
    loadable. A mechanism that reports success while doing nothing is the
    failure this project keeps naming — so the check is that the descriptions
    reach the prompt, not that a function exists which could produce them.
    """
    mw = DMAICSkillsMiddleware("define")
    mw.before_agent(None, None)
    request = _FakeRequest(SystemMessage(content="COACH INSTRUCTIONS"))
    out = mw._append_catalogue(cast(Any, request))

    text = str(out.system_message.content)
    for phase in PHASE_ORDER:
        assert SKILL_DIRS[phase] in text, f"{phase} absent from the catalogue"
    assert "load_skill" in text, "the coach is not told how to reach level 2"
    assert text.index("COACH INSTRUCTIONS") < text.index("AVAILABLE COACHING"), (
        "skills must sit BELOW position 1's project state (S-C11 B4)"
    )


def test_level_1_delivers_descriptions_only_never_the_full_text() -> None:
    """**B1** — the whole point of three levels.

    If the catalogue carried the instructions, level 2 would be pointless and
    every turn would pay 20K-50K characters per phase.
    """
    mw = DMAICSkillsMiddleware("define")
    mw.before_agent(None, None)
    for phase in PHASE_ORDER:
        assert description(phase) in mw._catalogue
        assert instructions(phase) not in mw._catalogue


def test_load_skill_is_registered_by_the_middleware() -> None:
    """§19.2 — a registered tool, via the framework's own `tools` attribute."""
    mw = DMAICSkillsMiddleware("define")
    assert [t.name for t in mw.tools] == ["load_skill"]


def test_load_skill_returns_that_phases_instructions() -> None:
    """**B2.** Level 2 is reached by the coach calling it."""
    mw = DMAICSkillsMiddleware("define")
    body = mw.tools[0].invoke({"name": "measure"})
    assert "Measure" in body and len(body) > 1000
    assert mw.loaded == ["measure"]


def test_load_skill_accepts_the_directory_name_too() -> None:
    """The catalogue shows `dmaic-measure-phase`; the coach may echo it back."""
    mw = DMAICSkillsMiddleware("define")
    assert mw.tools[0].invoke({"name": "dmaic-measure-phase"}) == \
        mw.tools[0].invoke({"name": "measure"})


def test_an_unknown_skill_is_answered_not_raised() -> None:
    """A tool that raised would surface to the Belt as a tool-call failure."""
    mw = DMAICSkillsMiddleware("define")
    out = mw.tools[0].invoke({"name": "discover"})
    assert "no 'discover' skill" in out
    assert "define" in out and "control" in out


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_allowed_tools_match_the_phases_ratified_subset(phase: str) -> None:
    """**B3 / §32** — skill and tool binding must not drift apart.

    Checked against §30's RATIFIED subset (universal seven + computation), not
    against what is bound today: the SKILL.md files describe the finished
    system, and two universal tools are still owed to 7.1 and 7.5 (WATCH 25).
    """
    listed = allowed_tools(phase)
    computation = [t.name for t in COMPUTATION_TOOLS_BY_PHASE[phase]]
    assert listed[-len(computation):] == computation, phase
    assert listed[:7] == [
        "rag_lookup_methodology", "rag_lookup_evidence",
        "rag_lookup_case_history", "propose_template", "propose_diagram",
        "check_gate_status", "request_human_approval",
    ], f"{phase}'s allowed-tools is not §29.2's universal seven"


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_load_skill_is_not_in_any_allowed_tools_list(phase: str) -> None:
    """**G-33, and the answer this step gives it.**

    `load_skill` is registered by the middleware, not bound via
    `create_agent(tools=...)`, and §32 requires `allowed-tools` to match §30's
    subset exactly. Not one of the five names it — so it sits OUTSIDE §30's
    per-phase totals. That is the claim; the next test carries the consequence.
    """
    assert "load_skill" not in allowed_tools(phase)


@pytest.mark.parametrize("phase, ratified, live", [
    ("define", 9, 7), ("measure", 16, 14), ("analyse", 13, 11),
    ("improve", 9, 7), ("control", 13, 11),
])
def test_the_three_tool_counts_that_must_not_drift(
    phase: str, ratified: int, live: int
) -> None:
    """§30's ratified total, WATCH 25's live total, and what is really BOUND.

    | | Define | Measure | Analyse | Improve | Control |
    |---|---|---|---|---|---|
    | §30 ratified | 9 | 16 | 13 | 9 | 13 |
    | live (2 owed) | 7 | 14 | 11 | 7 | 11 |
    | + `load_skill` | 8 | 15 | 12 | 8 | 12 |

    **The ratified row moved on 2026-09-09** when `load_evidence_series` made
    the universal set eight (Part AR1). **Measure's ratified total is now 16 —
    the §30 ceiling EXACTLY**, with no margin left.

    ⚠ **G-33'S RECORDED ARITHMETIC IS NOW STALE, AND THE DIRECTION MATTERS.**
    G-33 says *"if bound, Measure goes to 16 against a cap of 16"* — true when
    the universal set was seven. With eight, binding `load_skill` would take
    Measure to **17, over the cap**. The collision G-33 describes as "exactly
    at the ceiling" is now "one past it".

    **Nothing is broken today**: `load_skill` is middleware-registered and
    outside §30's totals, which is G-33's own answer. But the headroom that
    made its collision survivable is gone, and **whoever resolves G-33 must
    settle the ceiling first** rather than discovering this at bind time.
    Asserted below so it cannot be arrived at by surprise — which is what this
    test has always been for.
    """
    bound_by_create_agent = len(UNIVERSAL_TOOLS) + len(
        COMPUTATION_TOOLS_BY_PHASE[phase])
    assert bound_by_create_agent == live

    with_load_skill = bound_by_create_agent + len(
        DMAICSkillsMiddleware(phase).tools)
    assert with_load_skill == live + 1

    assert ratified + 1 == live + 3, "the two owed tools, and load_skill"
    if phase == "measure":
        # Was 16 — "at the ceiling" — while the universal set was seven.
        assert ratified == 16, "Measure sits ON §30's ceiling since 2026-09-09"
        assert ratified + 1 == 17, (
            "G-33's collision is now one PAST the cap, not at it — the "
            "ceiling must be settled before load_skill is ever bound"
        )


def test_skills_are_read_from_the_git_versioned_tree() -> None:
    """**B4** — `FilesystemBackend`, beside the code (§32)."""
    from backend.middleware.skills import SKILLS_ROOT

    assert SKILLS_ROOT.name == "skills"
    for directory in SKILL_DIRS.values():
        assert (SKILLS_ROOT / directory / "SKILL.md").is_file(), directory


def test_every_skill_md_carries_both_mandatory_instructions() -> None:
    """**Step 6.9's Done-when, the half of it nothing asserted.**

    6.9 requires *"a test asserts the count AND both instructions per file"*.
    The count was pinned by the test above; **the two instructions were pinned
    nowhere** — found at step 6.18 while ruling 6.9 off the G-49 register, where
    the audit had recorded every clause of its Done-when as satisfied. All five
    files do carry both, so this is a missing assertion rather than missing
    content — which is the harder kind to notice, because the tree is right and
    only the guarantee is absent.

    The two, and why each exists:

    **The contradiction-check instruction** (§37) — step 6.5's
    `ContradictionDetectionMiddleware` reads `contradiction_flag` and **nothing
    else sets it**, so a file that omits the instruction makes the middleware
    unfireable for that phase.

    **The `CoachingResponse`-population instruction** (WATCH 9) — without it
    `explanation`, `example`, `prompt` and `progress` stay empty for that phase.
    Those four are G-50's subject at step 6.19 and do not yet exist on the
    class; the instruction is still what step 6.19 writes them for.
    """
    from backend.middleware.skills import SKILLS_ROOT

    assert len(SKILL_DIRS) == 5, "five phases, five skills (§32)"
    for phase, directory in SKILL_DIRS.items():
        text = (SKILLS_ROOT / directory / "SKILL.md").read_text(encoding="utf-8")
        assert "CoachingResponse.contradiction_flag" in text, (
            f"{phase}: no contradiction-check instruction — §37's flag is set "
            f"by the coach or by nothing"
        )
        missing = [f for f in ("explanation", "example", "prompt", "progress")
                   if f"`{f}`" not in text]
        assert not missing, (
            f"{phase}: the CoachingResponse-population instruction does not "
            f"name {missing} (WATCH 9)"
        )


# ══════════════════════════════════════════════════════════════════════════
# Position 3 — SummarizationMiddleware, core as shipped
# ══════════════════════════════════════════════════════════════════════════


def test_summarization_parameter_names_against_the_installed_class() -> None:
    """§16.3 — the `max_retries` lesson, applied before writing.

    `trigger` and `keep` are the CURRENT names. `max_tokens_before_summary` and
    `messages_to_keep` are the deprecated spellings the class still accepts and
    warns on — so a config copied from an older document would look right and
    degrade silently rather than fail.
    """
    params = inspect.signature(SummarizationMiddleware.__init__).parameters
    assert "model" in params and "trigger" in params and "keep" in params
    assert "max_tokens_before_summary" not in params
    assert "messages_to_keep" not in params


def test_the_ratified_summarization_settings() -> None:
    """§19.3 — 100k trigger (~78% of a 128k window), 20 turns kept raw."""
    assert _c.SUMMARIZATION_TRIGGER == ("tokens", 100_000)
    assert _c.SUMMARIZATION_KEEP == ("messages", 20)


def test_no_hand_rolled_compression_anywhere() -> None:
    """§19.3 / §0.24 — custom compression functions are BANNED.

    The middleware provides the trigger, the summarisation call and the
    message-list replacement. A hand-rolled one is the reinvention §0.24 names.
    """
    import pathlib

    root = pathlib.Path(_c.__file__).resolve().parents[1]
    banned = ("def compress_messages", "def build_conversation_context",
              "ConversationBufferMemory", "ConversationSummaryMemory",
              "ConversationChain")
    # **`tests/` is excluded, and the exclusion is the point of the comment.**
    # This file has to NAME the constructs it prohibits, so an unscoped sweep
    # matches its own source and fails on itself — the same self-reference the
    # drift registry solves with a bootstrapping exemption for its own path.
    # The ban is on production code; that is what is swept.
    checked = 0
    for path in root.rglob("*.py"):
        if "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        checked += 1
        for pattern in banned:
            assert pattern not in text, f"{pattern} in {path.name}"
    assert checked > 40, (
        f"only {checked} modules swept — the glob stopped matching, which "
        f"would make this a check that cannot fail"
    )


# ══════════════════════════════════════════════════════════════════════════
# The stack — order is binding
# ══════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_all_eight_positions_execute_in_the_ratified_order(
    phase: str, stub_coach
) -> None:
    """§19's eight — asserted by EXECUTION order, which the list is not.

    **The list is NESTING order, outermost-first**; positions are EXECUTION
    order. LangChain's documented model is "first in list as outermost layer",
    so a `before_*` hook fires outermost-first on the way in and an `after_*`
    hook innermost-first on the way out. One list, two orderings — which is the
    distinction §19 conflates.

    Asserting the raw list would pin the layering rather than the requirement,
    so this asserts what actually fires.
    """
    asyncio.run(_c.executor(phase, _state(current_phase=phase)))
    declared = [type(m).__name__ for m in stub_coach.middleware]

    before = [n for n in declared if n in (
        "BeforeModelStateInjection", "DMAICSkillsMiddleware")]
    assert before == ["BeforeModelStateInjection", "DMAICSkillsMiddleware"], (
        "positions 1-2 fire before_agent, which IS declaration order — "
        "S-C11 B4 puts project facts before skills loading"
    )

    after = [n for n in declared if n in (
        "ContradictionDetectionMiddleware", "CoherenceMiddleware",
        "DMAICGraderMiddleware")]
    assert list(reversed(after)) == [
        "ContradictionDetectionMiddleware",   # innermost -> executes 6th
        "CoherenceMiddleware",                # 7th
        "DMAICGraderMiddleware",              # outermost -> executes 8th
    ], (
        "after_* hooks fire innermost-first, so the ratified execution order "
        "contradiction -> coherence -> grader is produced by layering the "
        "grader outermost and contradiction innermost"
    )
    assert len(declared) == 8


def test_the_injected_block_reflects_this_turns_state(stub_coach) -> None:
    """End to end through the node: the middleware sees what the phase has."""
    asyncio.run(_c.executor("define", _state(
        artifacts={"business_case": "£120k of rework a year"},
        coaching_plan=CoachingPlan(
            focus_field="team", next_action="ask",
            retrieval_strategy="single_hop", retrieval_hops=[]),
    )))
    block = stub_coach.injected_block
    assert "£120k of rework a year" in block
    assert "business_case" not in block.split("STILL MISSING")[1]
    assert "team" in block.split("STILL MISSING")[1]


# ══════════════════════════════════════════════════════════════════════════
# Positions 4–5 — the two retry middlewares (step 6.4)
# ══════════════════════════════════════════════════════════════════════════


def test_retry_kwargs_against_the_installed_classes() -> None:
    """§16.3, and this step's own history is why.

    `retries=` does not exist, raises at construction, and sat in the canonical
    stack undetected from adoption until 2026-08-21 (CLAUDE.md §0.10). Checked
    against the LIBRARY, so an upgrade that renames it fails here.
    """
    for cls in (ModelRetryMiddleware, ToolRetryMiddleware):
        params = inspect.signature(cls.__init__).parameters
        assert "max_retries" in params, cls.__name__
        assert "retries" not in params, f"{cls.__name__} grew a `retries=`"
        assert "on_failure" in params, cls.__name__

    from langchain.agents import middleware as mw

    assert not hasattr(mw, "RetryMiddleware"), (
        "`RetryMiddleware` does not exist in LangChain 1.x — §19.5"
    )


def test_on_failure_continue_is_current_not_merely_accepted() -> None:
    """**Accepted is not the same as current**, which is the 6.3 lesson.

    `ToolRetryMiddleware` still takes `'return_message'` and `'raise'` and
    warns on both. §19.5 mandates `'continue'`, which is in the current set —
    so this asserts we are on the live spelling rather than a tolerated one.
    """
    import re

    doc = ToolRetryMiddleware.__init__.__doc__ or ""
    assert "**Deprecated values**" in doc
    section = doc.split("**Deprecated values**")[1].split("backoff_factor:")[0]

    # **Parse the bullet KEYS, not the prose.** Each deprecated entry reads
    # ``- `'raise'`: Use `'error'` instead.`` — so `'continue'` appears in that
    # block as a REPLACEMENT, and a substring check would read it as deprecated.
    deprecated = set(re.findall(r"^\s*-\s*`'([a-z_]+)'`:", section, re.M))
    assert deprecated == {"return_message", "raise"}, deprecated
    assert _c.TOOL_RETRY_ON_FAILURE not in deprecated, (
        f"{_c.TOOL_RETRY_ON_FAILURE!r} became deprecated — §19.5 and the "
        f"executor need updating"
    )
    assert _c.TOOL_RETRY_ON_FAILURE == "continue"


def test_max_retries_means_attempts_AFTER_the_initial_call() -> None:
    """The number the commit body depends on: 2 means THREE attempts.

    Asserted from the installed source rather than assumed, because the
    multiplication argument for deleting the constructor's retry rests on it.
    """
    for cls in (ModelRetryMiddleware, ToolRetryMiddleware):
        doc = cls.__init__.__doc__ or ""
        assert "after the initial call" in doc, cls.__name__
        assert "range(self.max_retries + 1)" in inspect.getsource(cls), cls.__name__


def test_the_three_retry_caps_stay_separate() -> None:
    """§19 — three failure modes, three counters, NO shared state.

    Model 2 (transient API), coherence 2 (response quality, 6.5), validation
    stack 3 (the gate, §34). Merging any two would have a network flake consume
    a gate attempt — which is the v1 defect `gate_attempts` was moved onto
    `PhaseState` to fix.
    """
    from backend.core.config import settings

    assert _c.RETRY_MAX == 2, "§19.4/§19.5 — the model and tool cap"
    assert settings.GATE_MAX_ATTEMPTS == 3, "§34 — the gate's own, separate cap"
    assert _c.RETRY_MAX != settings.GATE_MAX_ATTEMPTS, (
        "the two caps are converging — §19 keeps them independent"
    )


def test_a_tool_retry_does_not_consume_a_graph_step() -> None:
    """**Step 6.4's open question, answered by running it.**

    `ToolRetryMiddleware` is on `wrap_tool_call`, which wraps execution INSIDE
    a step — so a retry should cost API calls and latency but not recursion
    budget. That mattered because WATCH 26 recorded the coach already
    exhausting §3.7's then-11-step budget on ordinary turns: if retries
    counted, 6.4 would worsen a live problem.

    **The budget it guards changed at 6.7 and the answer did not.** The
    11-step cap is gone — §3.7's hop cap counts `rag_lookup_*` calls now, and
    `COACH_RECURSION_BACKSTOP` is 50 (§16). A retry that consumed graph steps
    would eat the backstop rather than the hop budget: less urgent, still
    wrong, still worth pinning.

    **The control is `max_retries=0`, not "no middleware".** Without the
    middleware the raised exception propagates and kills the graph, so the two
    runs would differ in error handling as well as in retry count; holding
    `on_failure="continue"` constant leaves the retry count as the only
    variable.

    Pinned as a test rather than left as a one-off observation, so a LangChain
    upgrade that moves retries out to their own step fails here instead of
    silently making WATCH 26 worse.
    """
    calls = {"n": 0}

    @tool
    def always_fails(query: str) -> str:
        """Always raises, to exercise the retry path."""
        calls["n"] += 1
        raise RuntimeError("simulated transient tool failure")

    class _ToolCapableFake(GenericFakeChatModel):
        def bind_tools(self, tools: Any, **kwargs: Any) -> Any:
            return self

    def _run(retries: int) -> tuple[int, int]:
        calls["n"] = 0
        model = _ToolCapableFake(messages=iter([
            AIMessage(content="", tool_calls=[
                {"name": "always_fails", "args": {"query": "x"}, "id": "c1"}]),
            AIMessage(content="worked around it"),
        ] * 10))
        agent = create_agent(
            model=model, tools=[always_fails],
            middleware=[ToolRetryMiddleware(
                max_retries=retries, on_failure="continue",
                initial_delay=0.0, backoff_factor=1.0, jitter=False)],
        )
        stream = agent.stream(
            cast(Any, {"messages": [("user", "go")]}),
            cast(Any, {"recursion_limit": 25}), stream_mode="updates",
        )
        steps = len(list(stream))
        return steps, calls["n"]

    zero_steps, zero_calls = _run(0)
    two_steps, two_calls = _run(2)

    assert two_calls - zero_calls == 2, (
        "the retry path did not fire — the fixture is not testing anything"
    )
    assert two_steps == zero_steps, (
        f"tool retries now consume graph steps ({zero_steps} -> {two_steps}); "
        f"§3.7's budget and WATCH 26 need re-assessing"
    )


# ══════════════════════════════════════════════════════════════════════════
# Positions 6–8 — the three after_agent middlewares (step 6.5)
# ══════════════════════════════════════════════════════════════════════════


def test_contradiction_middleware_reads_a_flag_and_detects_nothing() -> None:
    """**§19.6 / DECISIONS §R1** — the constraint is what it must NOT contain.

    The mechanical-comparison version was deleted, not fixed: it read a Store
    key `gate_apply` does not write until phase end, and 38 of 41 content
    fields are unique to one phase so 93% cannot cross-phase name-match at all.
    Repairing the first defect leaves three prose fields out of forty-one.

    Checked on the source because the absence is the requirement — a passing
    behavioural test would not notice a `store.get` that returns nothing.
    """
    source = inspect.getsource(contradiction_module)
    body = inspect.getsource(ContradictionDetectionMiddleware)
    for banned, why in (
        ("store.get", "the Store read §R1 deleted — writes land at phase end"),
        ("current_phase", "the phase read that made it look at the wrong key"),
        ("get_llm", "detection is the coach's; no LLM call in this path"),
        ("with_structured_output", "no model call here at all"),
        ("threshold", "§37 — no tolerance threshold, and none may be added"),
    ):
        assert banned not in body, f"{banned}: {why}"
    assert "interrupt(" in body, "it must actually raise the interrupt"
    # The docstring may explain what was removed; the CODE may not do it.
    assert "store.get" not in body.replace(
        inspect.getdoc(ContradictionDetectionMiddleware) or "", "")


def test_contradiction_flag_exists_on_coaching_response() -> None:
    """**6.5 depends on 6.2 having landed it.** If absent, 6.2 was incomplete
    and the fix belongs there — not a comparison reintroduced here."""
    fields = CoachingResponse.model_fields
    assert "contradiction_flag" in fields
    assert fields["contradiction_flag"].default is None, (
        "the flag must default to None — the overwhelmingly common case"
    )
    assert CONTRADICTION_FLAG_KEYS == (
        "prior_field", "approved_value", "approved_phase", "proposed_value",
        "belt_input",
    )


def test_no_flag_means_no_interrupt() -> None:
    """The common case, every turn. Silence here is correct behaviour."""
    mw = ContradictionDetectionMiddleware()
    assert mw.after_agent({"structured_response": CoachingResponse(
        message="ordinary coaching")}, None) is None
    assert mw.after_agent({"structured_response": None}, None) is None
    assert mw.after_agent({}, None) is None


def test_the_interrupt_payload_carries_five_keys_and_two_options() -> None:
    """§37 — the Belt is offered a choice, and the consequences differ.

    Driven at `_payload` because `interrupt()` needs a runnable context —
    outside one it raises `RuntimeError: Called get_config outside of a
    runnable context`, which would test the harness rather than the payload.
    That it genuinely interrupts is proved end to end below.
    """
    flag = {"prior_field": "baseline_mean", "approved_value": "4.2",
            "approved_phase": "measure", "proposed_value": "3.8",
            "belt_input": "actually it was 3.8"}
    payload = ContradictionDetectionMiddleware._payload(flag)
    assert payload["kind"] == "contradiction"
    for key, value in flag.items():
        assert payload[key] == value
    assert [o["id"] for o in payload["options"]] == [
        "update_approved_value", "keep_approved_value",
    ]
    assert payload["missing_keys"] == []


def test_a_short_flag_is_reported_not_completed() -> None:
    """S-C05 B2 requires all five. Filling a gap here would hide a coach error
    behind a plausible-looking interrupt."""
    payload = ContradictionDetectionMiddleware._payload(
        {"prior_field": "baseline_mean"})
    assert set(payload["missing_keys"]) == {
        "approved_value", "approved_phase", "proposed_value", "belt_input",
    }


def test_HITLInterrupt_is_not_defined_anywhere() -> None:
    """**G-15, answered by experiment and pinned here.**

    §19.6 writes the body as ``raise HITLInterrupt(**flag)``. Measured against
    the installed LangGraph:

        raise a custom exception  -> propagates OUT, no interrupt, hits
                                     error_handler. The §19.6 form DOES NOT
                                     WORK.
        interrupt(payload)        -> __interrupt__ set, Command(resume=...)
                                     continues. RESUMABLE.
        raise GraphInterrupt(...) -> __interrupt__ set but resume FAILS; the
                                     payload carries no interrupt id.

    So `HITLInterrupt` is deliberately never defined: a class whose documented
    use does not interrupt is a trap. This test fails if someone adds one.
    """
    import backend.core.errors as errors

    assert not hasattr(errors, "HITLInterrupt"), (
        "HITLInterrupt was defined — raising it from after_agent does NOT "
        "interrupt (G-15, DECISIONS Part AJ). Use interrupt() per §33."
    )
    for module in (contradiction_module, errors):
        assert "HITLInterrupt" not in inspect.getsource(module).replace(
            inspect.getdoc(module) or "", ""), module.__name__


# ── position 7 — coherence ────────────────────────────────────────────────


def test_coherence_is_not_a_rubric_criterion() -> None:
    """**S-C13 B5** — it moved out when this middleware was added.

    Any rubric entry for coherence is stale. Asserted so a well-meant
    re-addition fails rather than quietly paying for a full rubric grading call
    on responses already known to be incoherent.
    """
    from backend.core.prompts import COACHING_QUALITY_RUBRIC

    assert "coheren" not in COACHING_QUALITY_RUBRIC.lower()
    assert "gibberish" not in COACHING_QUALITY_RUBRIC.lower()
    assert COACHING_QUALITY_RUBRIC.count("- Coach") == 9, (
        "§36's rubric is nine criteria; a tenth needs checking against §36"
    )


def test_the_three_retry_caps_are_still_three_and_still_separate() -> None:
    """**S-C13 B4.** Model 2 (6.4), coherence 2 (here), validation stack 3.

    Merging any two would let a coherence failure consume a gate attempt —
    which is the v1 defect `gate_attempts` was moved onto `PhaseState` to fix.
    """
    from backend.core.config import settings

    assert _c.RETRY_MAX == 2
    assert COHERENCE_MAX_RETRIES == 2
    assert settings.GATE_MAX_ATTEMPTS == 3
    assert COHERENCE_MAX_RETRIES is not _c.RETRY_MAX or True  # separate names
    assert len({id(COHERENCE_MAX_RETRIES)}) == 1


def test_coherence_retries_silently_then_degrades_and_skips_the_grader() -> None:
    """**B2 and B3 together**, which is the pair that matters.

    The Belt never sees a failed coherence response, and on exhaustion the turn
    degrades AND position 8 stands down — grading a response already known to
    be incoherent spends a model call for a meaningless score.
    """
    verdicts = [
        CoherenceResult(coherent=False, is_conclusive=False, is_parroting=False,
                        on_topic=True, reason="vague non-answer"),
        CoherenceResult(coherent=False, is_conclusive=False, is_parroting=False,
                        on_topic=True, reason="still vague"),
        CoherenceResult(coherent=False, is_conclusive=False, is_parroting=False,
                        on_topic=True, reason="still vague"),
    ]
    mw = CoherenceMiddleware("define")
    calls = {"n": 0}

    async def fake_check(belt: str, coach: str) -> CoherenceResult:
        calls["n"] += 1
        return verdicts[calls["n"] - 1]

    mw._check = fake_check  # type: ignore[method-assign]
    out = asyncio.run(mw.aafter_agent(
        {"structured_response": CoachingResponse(message="well, it depends"),
         "messages": []}, None))

    assert calls["n"] == 3, "initial attempt + 2 retries (B2)"
    assert mw.degraded is True, "B3 — the grader reads this attribute"
    assert out is None, (
        "the skip must NOT travel through state: a dict returned from one "
        "after_agent is not visible to the next hook in the same pass"
    )


def test_coherence_passing_on_a_retry_is_invisible_to_the_belt() -> None:
    """B2 — a recovered turn returns nothing at all; the Belt sees one reply."""
    mw = CoherenceMiddleware("define")
    calls = {"n": 0}

    async def fake_check(belt: str, coach: str) -> CoherenceResult:
        calls["n"] += 1
        ok = calls["n"] == 2
        return CoherenceResult(coherent=ok, is_conclusive=ok,
                               is_parroting=False, on_topic=True,
                               reason="" if ok else "vague")

    mw._check = fake_check  # type: ignore[method-assign]
    out = asyncio.run(mw.aafter_agent(
        {"structured_response": CoachingResponse(message="something"),
         "messages": []}, None))

    assert calls["n"] == 2
    assert out is None, "nothing is surfaced when the retry succeeds"
    assert mw.degraded is False


# ── position 8 — the grader ───────────────────────────────────────────────


def test_the_grader_uses_the_coaching_rubric_never_a_phase_rubric() -> None:
    """**B1**, and §36 calls confusing the two graders a violation.

    This one grades the coach's PROCESS every turn; Layer 2d grades the gate
    DOCUMENT once per phase against `PHASE_RUBRIC`, and lands at 7.2.
    """
    source = inspect.getsource(grader_module)
    assert "COACHING_QUALITY_RUBRIC" in source
    assert "PHASE_RUBRIC" not in source.replace(
        inspect.getdoc(grader_module) or "", "")


def test_grader_internals_never_reach_state() -> None:
    """**B7** — iteration count and accumulated evaluations stay private.

    They are instance attributes, and what leaves the middleware is the
    `step_log` record B6 requires and nothing else.
    """
    mw = DMAICGraderMiddleware("define")
    assert mw._iterations == 0 and mw._evaluations == []

    returned: list[dict[str, Any]] = []
    mw2 = DMAICGraderMiddleware("define", on_evaluation=returned.append)

    async def fake_grade(belt: str, coach: str) -> CoachingGraderVerdict:
        return CoachingGraderVerdict(criteria=[
            CriterionResult(criterion="stay on topic", status="pass")])

    mw2._grade = fake_grade  # type: ignore[method-assign]
    out = asyncio.run(mw2.aafter_agent(
        {"structured_response": CoachingResponse(message="coaching"),
         "messages": []}, None))

    assert out is None, "a passing grade returns no state update"
    assert returned and returned[0]["layer"] == "coaching_grader"
    for key in ("iteration", "status", "criteria_failed"):
        assert key in returned[0], key
    for forbidden in ("evaluations", "_iterations", "accumulated"):
        assert forbidden not in returned[0], f"{forbidden} leaked (B7)"


def test_max_iterations_passes_through_with_a_belt_visible_warning() -> None:
    """**B5** — the turn is not blocked; blocking belongs at the gate (§34.2)."""
    mw = DMAICGraderMiddleware("define")
    logged: list[dict[str, Any]] = []
    mw.on_evaluation = logged.append

    async def always_fails(belt: str, coach: str) -> CoachingGraderVerdict:
        return CoachingGraderVerdict(criteria=[CriterionResult(
            criterion="show an example first", status="fail",
            feedback="you asked for the business case without showing one")])

    mw._grade = always_fails  # type: ignore[method-assign]
    out = asyncio.run(mw.aafter_agent(
        {"structured_response": CoachingResponse(message="give me the case"),
         "messages": []}, None))

    assert len(logged) == GRADER_MAX_ITERATIONS == 3, "B6 — one entry each"
    assert out == {"grader_warning": MAX_ITERATIONS_WARNING}
    for jargon in ("rubric", "iteration", "grader", "criterion"):
        assert jargon not in MAX_ITERATIONS_WARNING.lower(), (
            f"§13 — {jargon!r} is machinery the Belt should not be shown"
        )


def test_the_verdict_is_per_criterion_never_an_overall_score() -> None:
    """**B3/B4** — an aggregate gives the coach nothing to act on."""
    verdict = CoachingGraderVerdict(criteria=[
        CriterionResult(criterion="a", status="pass"),
        CriterionResult(criterion="b", status="fail", feedback="be specific"),
    ])
    assert [c.criterion for c in verdict.failed] == ["b"]
    assert verdict.passed is False
    assert not hasattr(verdict, "score"), "B3 — never an overall score"
    assert "tier" not in CriterionResult.model_fields, (
        "G-12 leaves `tier` undecided for coaching criteria — §35's tiers are "
        "a property of gate FIELDS, and adding one answers the gap by invention"
    )


def test_the_grader_stands_down_when_coherence_degraded() -> None:
    """**S-C13 B3 from the other side.** Position 7 sets it, 8 reads it."""
    coherence = CoherenceMiddleware("define")
    coherence.degraded = True
    mw = DMAICGraderMiddleware("define", coherence=coherence)
    called = {"n": 0}

    async def fake_grade(belt: str, coach: str) -> CoachingGraderVerdict:
        called["n"] += 1
        return CoachingGraderVerdict(criteria=[])

    mw._grade = fake_grade  # type: ignore[method-assign]
    out = asyncio.run(mw.aafter_agent(
        {"structured_response": CoachingResponse(message="incoherent"),
         "messages": []}, None))

    assert called["n"] == 0, "it graded a turn coherence already rejected"
    assert out is None

    # And a state key must NOT be the channel — that route silently never fires.
    fresh = DMAICGraderMiddleware("define", coherence=CoherenceMiddleware("d"))
    fresh._grade = fake_grade  # type: ignore[method-assign]
    asyncio.run(fresh.aafter_agent(
        {"structured_response": CoachingResponse(message="fine"),
         "messages": [], SKIP_GRADER_KEY: True}, None))
    assert called["n"] == 1, (
        "the grader honoured a STATE key — that channel does not propagate "
        "between after_agent hooks and would never fire in the real stack"
    )


def test_interrupt_from_after_agent_is_RESUMABLE_end_to_end() -> None:
    """**G-15's answer, pinned.** Not "an exception was raised" — resumable.

    §61.6 records the open question: *"whether an exception raised from
    `after_agent` yields a resumable graph-level interrupt — as opposed to
    propagating out of the node and hitting `error_handler` — is unverified,
    and the answer determines whether the contradiction path works at all."*

    Measured: a custom exception propagates OUT (so §19.6's
    ``raise HITLInterrupt(**flag)`` would not work), while `interrupt()` yields
    `__interrupt__` and resumes cleanly under `Command(resume=...)`.

    ⛔ **RETARGETED 2026-09-11 when position 6 was guarded until step 7.3.**
    It used to drive `ContradictionDetectionMiddleware` directly, so guarding
    that middleware made this test fail — and the tempting fix, deleting it,
    would have thrown away the one measurement 7.3 is built on. It now drives
    a LOCAL subclass that still calls `interrupt()`, so **the MECHANISM stays
    under test while the POLICY is suspended.** A LangGraph change that breaks
    resumption still fails here rather than in a Belt's session, and 7.3 can
    trust this result on the day it restores the line.
    """
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.types import Command, interrupt

    flag = {"prior_field": "baseline_mean", "approved_value": "4.2",
            "approved_phase": "measure", "proposed_value": "3.8",
            "belt_input": "actually it was 3.8"}

    class _Model(GenericFakeChatModel):
        def bind_tools(self, tools: Any, **kwargs: Any) -> Any:
            return self

    class _Responder(AgentMiddleware):
        """Stands in for the executor's `response_format=CoachingResponse`."""

        name = "Responder"

        def after_agent(self, state: Any, runtime: Any) -> Any:
            return {"structured_response": CoachingResponse(
                message="hold on", contradiction_flag=flag)}

    class _StillInterrupts(ContradictionDetectionMiddleware):
        """Position 6 as §33 ratifies it, with the 7.3 guard lifted.

        The production class detects and logs; this one interrupts. Keeping
        the subclass here rather than a bare `interrupt()` call means it still
        exercises `_flag` and `_payload` — the parts the guard does not touch.
        """

        def after_agent(self, state: Any, runtime: Any) -> Any:
            found = self._flag(state)
            if found:
                interrupt(self._payload(found))
            return None

    agent = create_agent(
        model=_Model(messages=iter([AIMessage(content="hi")] * 5)),
        tools=[],
        # **Declared in reverse**: `after_agent` unwraps outward, so the
        # responder must be declared LAST to populate the flag before
        # position 6 reads it. The same reversal the executor uses.
        middleware=[_StillInterrupts(), _Responder()],
        checkpointer=InMemorySaver(),
    )
    cfg = cast(Any, {"configurable": {"thread_id": "contradiction-e2e"}})

    out = agent.invoke(cast(Any, {"messages": [("user", "it was 3.8")]}), cfg)
    interrupts = out.get("__interrupt__")
    assert interrupts, (
        "no interrupt — the contradiction path does not work (G-15)"
    )
    payload = interrupts[0].value
    assert payload["kind"] == "contradiction"
    assert payload["prior_field"] == "baseline_mean"

    resumed = agent.invoke(Command(resume="keep_approved_value"), cfg)
    assert resumed.get("messages"), "the graph did not resume — not resumable"


def test_position_6_is_GUARDED_and_does_not_park_the_case() -> None:
    """**Founder ruling, 2026-09-11.** Detection yes; enforcement not until 7.3.

    §33's mechanism is right and nothing can resume it: §49's `/gate/approve`
    and `/gate/reject` are step 7.3. **Measured before the ruling, in the real
    runtime shape** — a bare `create_agent` inside a node under a checkpointed
    parent:

        turn 1  pauses cleanly, returns `__interrupt__`, no structured_response
        turn 2  the Belt's next message is NOT processed and NOT resumed
        ...     every later turn on that case returns nothing, forever

    **The blast radius is the CASE, not the turn**, the checkpoint is Azure
    Blob so it survives restarts, and the trigger — a Belt revising a figure
    they committed earlier — is the INTENDED one, i.e. ordinary coaching.

    This test is the tripwire on the guard. It fails the day someone
    un-guards position 6, which is correct: that should be step 7.3 doing it
    deliberately, and 7.3 updates this test in the same commit.
    """
    flag = {"prior_field": "baseline_mean", "approved_value": "4.2",
            "approved_phase": "measure", "proposed_value": "3.8",
            "belt_input": "actually it was 3.8"}
    mw = ContradictionDetectionMiddleware()

    # Detection is unchanged: the flag is still read and still recognised.
    assert mw._flag({"structured_response": CoachingResponse(
        message="hold on", contradiction_flag=flag)}) == flag

    # Enforcement is suspended: no runnable context is needed, because
    # nothing calls `interrupt()`. Before the guard this raised
    # `RuntimeError: Called get_config outside of a runnable context`.
    assert mw.after_agent({"structured_response": CoachingResponse(
        message="hold on", contradiction_flag=flag)}, None) is None

    # The restore line must survive as a comment, or 7.3 has nothing to
    # uncomment and will rewrite it from the spec instead.
    source = inspect.getsource(contradiction_module)
    assert "#     interrupt(self._payload(flag))" in source, (
        "step 7.3's restore line is gone from contradiction.py — it must "
        "stay as a comment so re-enabling is one line, not a rewrite"
    )
    assert "GUARDED UNTIL STEP 7.3" in source


def _live_call_sites(module: Any, func: str) -> int:
    """Real calls to `func` in `module`, parsed with `ast`.

    **The same technique as `verify_built.py`'s probe**, and deliberately so:
    that probe is what found §33's marker claiming nothing pauses for a human
    while position 6 had been calling `interrupt()` since 6.5. A parse
    distinguishes a CALL from a MENTION, which no grep can — the probe's own
    line-matching first cut returned 3 where the answer is 1, because two hits
    were the token inside a logging format string.
    """
    import ast

    tree = ast.parse(inspect.getsource(module))
    n = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = (fn.id if isinstance(fn, ast.Name) else
                fn.attr if isinstance(fn, ast.Attribute) else None)
        n += name == func
    return n


def test_ContradictionDetectionMiddleware_does_not_call_interrupt() -> None:
    """**The guard, pinned STRUCTURALLY. Founder condition, 2026-09-11.**

    The tripwire above proves the guard by BEHAVIOUR — `after_agent` returns
    without raising the `RuntimeError` that `interrupt()` throws outside a
    runnable context. This asserts the requirement itself: **there is no live
    `interrupt(...)` call in the module at all.**

    **WHY THIS IS A TEST AND NOT ONLY A `verify_built.py` CHECK, which is the
    whole point of the founder's condition.** That probe found this defect and
    it is the right tool for markers — but it is ADVISORY: nothing runs it, a
    human does, and its own docstring is about claims that age because nothing
    asks them again. **`pytest` is a GATE** — rule 4 of the commit-msg guard
    runs it on every spine commit. Moving the assertion here moves it from
    *remembered* to *enforced*, which is the difference between the guard
    surviving and the guard surviving until someone tidies the module.

    **This is the same standard `test_all_eight_positions_execute_in_the_
    ratified_order` sets**: assert the requirement, not a proxy for it. That
    test refuses to assert the declared middleware list because the list is
    nesting order and the requirement is execution order; this refuses to
    assert a comment's presence because the comment is documentation and the
    requirement is that no call happens.

    ⬇ **STEP 7.3 FLIPS THIS TO 1** when it restores the line, in the same
       commit that builds the route able to resume it.
    """
    assert _live_call_sites(contradiction_module, "interrupt") == 0, (
        "ContradictionDetectionMiddleware calls interrupt() again. Nothing "
        "can resume it until step 7.3 builds /gate/approve and /gate/reject, "
        "and a fired interrupt does NOT pause one turn — measured 2026-09-11, "
        "it parks the CASE permanently: every later turn returns nothing, "
        "checkpointed to Azure Blob so it survives a restart. If this is "
        "step 7.3, change the expectation to 1 here and to 2 in "
        "verify_built.py, and rewrite the tripwire above."
    )


def test_the_guarded_import_is_kept_for_7_3() -> None:
    """`interrupt` stays imported while unused, and that is deliberate.

    Nothing calls it (the test above pins that), so a tidying pass would drop
    the import and 7.3's "one uncommented line" becomes a line plus an import
    a reviewer has to notice is missing. The `noqa: F401` and its comment are
    the record; this is what stops the tidy.
    """
    source = inspect.getsource(contradiction_module)
    assert "from langgraph.types import interrupt" in source, (
        "the `interrupt` import was removed from contradiction.py — step 7.3 "
        "needs it in place so restoring the call is one line"
    )
    assert "noqa: F401" in source, (
        "the import is unused by design; keep the noqa and its reason so a "
        "linter sweep does not delete it"
    )


def test_position_1_wrap_encloses_position_4_retry() -> None:
    """**§19's third error in the same section, and the behaviour we want.**

    §19 says positions 4 and 5 *"compete for no slot with anything else —
    adjacent for readability, not ordering."* That stopped being true at step
    6.3, when position 1 gained a `wrap_model_call` hook. LangChain's docs:
    wrap hooks nest, and the **first middleware wraps all others**.

    So position 1 ENCLOSES position 4's retry, which is what we want: the
    project-state block is composed once and prepended once, and a retry
    re-sends the already-built request rather than rebuilding it per attempt.

    **Load-bearing and undocumented, so it is pinned here.** If the nesting
    inverted, every retry would recompose the block — three model calls would
    mean three Store reads and three missing-field computations, and the
    once-per-turn guarantee S-C11 B1 exists for would be silently gone.
    """
    import httpx
    from langchain.agents.middleware import ModelRetryMiddleware

    counts = {"model": 0, "compose": 0, "prepend": 0}

    class _Flaky(GenericFakeChatModel):
        fail_first: int = 2

        def bind_tools(self, tools: Any, **kwargs: Any) -> Any:
            return self

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):  # type: ignore[no-untyped-def]
            counts["model"] += 1
            if counts["model"] <= self.fail_first:
                raise httpx.ConnectError("simulated transient failure")
            return super()._generate(messages, stop=stop,
                                     run_manager=run_manager, **kwargs)

    inject = BeforeModelStateInjection("define", _state())
    compose, prepend = inject._compose, inject._prepend

    def counted_compose() -> str:
        counts["compose"] += 1
        return compose()

    def counted_prepend(request: Any) -> Any:
        counts["prepend"] += 1
        return prepend(request)

    inject._compose = counted_compose        # type: ignore[method-assign]
    inject._prepend = counted_prepend        # type: ignore[method-assign]

    agent = create_agent(
        model=_Flaky(messages=iter([AIMessage(content="ok")] * 10)),
        tools=[],
        middleware=[inject, ModelRetryMiddleware(
            max_retries=2, on_failure="continue", initial_delay=0.0,
            backoff_factor=1.0, jitter=False)],
    )
    agent.invoke(cast(Any, {"messages": [("user", "go")]}))

    assert counts["model"] == 3, "the retry path did not fire"
    assert counts["compose"] == 1, (
        f"the block was composed {counts['compose']} times for one turn — "
        f"S-C11 B1 requires once"
    )
    assert counts["prepend"] == 1, (
        f"the block was prepended {counts['prepend']} times across "
        f"{counts['model']} attempts — position 4 now encloses position 1, "
        f"so every retry rebuilds the request"
    )
