"""Middleware positions 1–3 — what procedure step 6.3 established.

Verify for the step is `trace-check`; what is pinned here is everything the
trace cannot show. Three things would be silent if they broke:

  * **the hook** — `before_agent` vs `before_model` is a cost and correctness
    difference the trace shows only as extra tokens, and S-C11 B1 names it;
  * **the order** — declaration order is execution order for hooks of the same
    kind (§19), and position 1 being first is what puts project facts above
    skills loading and summarisation;
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
from backend.middleware.state_injection import BeforeModelStateInjection
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
        "citations": [], "uploads": [], "hop_results": [],
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
    ("define", 8, 6), ("measure", 15, 13), ("analyse", 12, 10),
    ("improve", 8, 6), ("control", 12, 10),
])
def test_the_three_tool_counts_that_must_not_drift(
    phase: str, ratified: int, live: int
) -> None:
    """§30's ratified total, WATCH 25's live total, and what is really BOUND.

    | | Define | Measure | Analyse | Improve | Control |
    |---|---|---|---|---|---|
    | §30 ratified | 8 | 15 | 12 | 8 | 12 |
    | live (2 owed) | 6 | 13 | 10 | 6 | 10 |
    | + `load_skill` | 7 | 14 | 11 | 7 | 11 |

    **G-33's collision is real but not yet live.** Once 7.1 and 7.5 land, the
    bound count is ratified + 1 — and Measure reaches **16, exactly the §30
    ceiling**, which is what G-33 says: *"if bound, Measure goes to 16 against
    a cap of 16."* Asserted here so that step cannot arrive at it by surprise.
    """
    bound_by_create_agent = len(UNIVERSAL_TOOLS) + len(
        COMPUTATION_TOOLS_BY_PHASE[phase])
    assert bound_by_create_agent == live

    with_load_skill = bound_by_create_agent + len(
        DMAICSkillsMiddleware(phase).tools)
    assert with_load_skill == live + 1

    assert ratified + 1 == live + 3, "the two owed tools, and load_skill"
    if phase == "measure":
        assert ratified + 1 == 16, "G-33's collision, at the ceiling"


def test_skills_are_read_from_the_git_versioned_tree() -> None:
    """**B4** — `FilesystemBackend`, beside the code (§32)."""
    from backend.middleware.skills import SKILLS_ROOT

    assert SKILLS_ROOT.name == "skills"
    for directory in SKILL_DIRS.values():
        assert (SKILLS_ROOT / directory / "SKILL.md").is_file(), directory


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
def test_positions_one_to_three_mount_in_declaration_order(
    phase: str, stub_coach
) -> None:
    """§19 — declaration order IS execution order for hooks of the same kind.

    Positions 1 and 2 both fire `before_agent`, so their relative order is what
    puts project facts in front of skills loading. S-C11 B4: position 1 must be
    first, *"so project facts reach the prompt before skills loading and
    summarisation shape it"*.
    """
    asyncio.run(_c.executor(phase, _state(current_phase=phase)))
    assert [type(m).__name__ for m in stub_coach.middleware] == [
        "BeforeModelStateInjection",   # 1 — before_agent, FIRST (S-C11 B4)
        "DMAICSkillsMiddleware",       # 2 — before_agent + load_skill
        "SummarizationMiddleware",     # 3 — before_model
        "ModelRetryMiddleware",        # 4 — wrap_model_call  (step 6.4)
        "ToolRetryMiddleware",         # 5 — wrap_tool_call   (step 6.4)
    ], "6-8 land at 6.5"


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
    budget. That mattered because WATCH 26 records the coach already
    exhausting §3.7's 11-step budget on ordinary turns: if retries counted,
    6.4 would worsen a live problem before 6.6 relieves it.

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
