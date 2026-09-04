"""Tests for the LLM factory — procedure step 2.7's Verify.

Reference §21 (roles, temperature, factory) · §54 (where classes live) ·
CLAUDE.md §4.1, §4.2, §4.7, §2.

These assert the CONTRACT, not the wiring: that every one of the eleven roles
resolves to a deployment, that the two tiers are assigned as §21's table says,
that the grader's 0.1 holds, and that `core/llm.py` still contains no class.
Nothing here calls Azure.
"""
from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from backend.core import llm as llm_module
from backend.core.llm import (
    DEFAULT_TEMPERATURE,
    OPERATIONAL_TIER,
    PREMIUM_TIER,
    ROLE_DEPLOYMENTS,
    ROLE_TEMPERATURES,
    role_temperature,
)

# §21's role table, transcribed. Kept as a literal rather than derived from
# ROLE_DEPLOYMENTS — a test that reads its expectation out of the code under
# test asserts nothing.
PREMIUM_ROLES = {"coach", "planner", "synthesis", "vision"}
OPERATIONAL_ROLES = {
    "reasoning", "extraction", "coherence", "constraint",
    "grader", "summarizer", "intent",
}
ALL_ROLES = PREMIUM_ROLES | OPERATIONAL_ROLES


def test_exactly_eleven_roles() -> None:
    """§21 specifies eleven roles — no more, no fewer."""
    assert len(ALL_ROLES) == 11
    assert set(ROLE_DEPLOYMENTS) == ALL_ROLES


@pytest.mark.parametrize("role", sorted(ALL_ROLES))
def test_every_role_resolves_to_a_deployment(role: str) -> None:
    """The step's 'Done when': all 11 roles resolve to a deployment."""
    deployment = ROLE_DEPLOYMENTS[role]
    assert isinstance(deployment, str) and deployment.strip()


@pytest.mark.parametrize("role", sorted(PREMIUM_ROLES))
def test_premium_roles_use_the_premium_tier(role: str) -> None:
    assert ROLE_DEPLOYMENTS[role] == PREMIUM_TIER


@pytest.mark.parametrize("role", sorted(OPERATIONAL_ROLES))
def test_operational_roles_use_the_operational_tier(role: str) -> None:
    assert ROLE_DEPLOYMENTS[role] == OPERATIONAL_TIER


def test_two_tiers_only() -> None:
    """§21: 'Two deployment tiers, addressed by role.' Not the v1 three."""
    assert len(set(ROLE_DEPLOYMENTS.values())) == 2


def test_grader_temperature_is_point_one() -> None:
    """The step's 'Done when', and a hard §21 requirement.

    A grader returning different verdicts across runs makes §52's regression
    thresholds meaningless.
    """
    assert ROLE_TEMPERATURES["grader"] == 0.1
    assert role_temperature("grader") == 0.1


@pytest.mark.parametrize("role", ["grader", "coherence", "constraint", "planner"])
def test_deterministic_roles_are_point_one(role: str) -> None:
    """§21's temperature table: consistent verdicts, deterministic planning."""
    assert role_temperature(role) == 0.1


def test_coach_temperature_in_the_ratified_band() -> None:
    """§21: coach responses 0.5-0.7."""
    assert 0.5 <= role_temperature("coach") <= 0.7


def test_extraction_and_synthesis_bands() -> None:
    """§21: extraction 0.0-0.2, synthesis 0.1-0.2."""
    assert 0.0 <= role_temperature("extraction") <= 0.2
    assert 0.1 <= role_temperature("synthesis") <= 0.2


def test_unratified_roles_fall_back_rather_than_inventing_a_figure() -> None:
    """§21 ratifies a temperature for seven roles; four have none.

    Those four must take DEFAULT_TEMPERATURE. A number in ROLE_TEMPERATURES
    for one of them would read as ratified when it is not — adding one is a
    §56 amendment.
    """
    unratified = ALL_ROLES - set(ROLE_TEMPERATURES)
    assert unratified == {"reasoning", "summarizer", "intent", "vision"}
    for role in unratified:
        assert role_temperature(role) == DEFAULT_TEMPERATURE


def test_unknown_role_raises_rather_than_passing_through() -> None:
    """§21: 'New roles require an amendment.'

    The v1 factory fell back to treating an unknown name as a literal
    deployment name, which is how `get_llm("operational-premium", ...)` lived
    in upload/agent.py unnoticed. That fallback is gone.
    """
    with pytest.raises(ValueError, match="Unknown LLM role"):
        llm_module.get_llm("operational")           # retired v1 role
    with pytest.raises(ValueError, match="Unknown LLM role"):
        llm_module.get_llm("operational-premium")   # a deployment name
    with pytest.raises(ValueError, match="Unknown LLM role"):
        llm_module.get_llm("premium")               # retired v1 role


def test_llm_module_declares_no_class() -> None:
    """§54 / CLAUDE.md §2: the LLM factory is module-level functions ONLY.

    Parsed rather than grepped, so a class inside a docstring or a comment
    does not fail the test and a real one cannot hide from it.
    """
    source = pathlib.Path(inspect.getfile(llm_module)).read_text(encoding="utf-8")
    classes = [n.name for n in ast.walk(ast.parse(source))
               if isinstance(n, ast.ClassDef)]
    assert classes == [], f"core/llm.py must contain no class, found: {classes}"


def test_public_factory_is_a_module_level_function() -> None:
    """The v1 API was a method on an LLMProvider instance."""
    assert inspect.isfunction(llm_module.get_llm)
    assert not hasattr(llm_module, "LLMProvider")
    assert not hasattr(llm_module, "llm_provider")


def test_the_constructor_pins_retry_off_explicitly() -> None:
    """**Step 6.4: `max_retries=0`, and the zero must be EXPLICIT.**

    This is 2.7's tripwire, inverted — and then tightened by the 6.4 ruling.

    The old test asserted the constructor kept a retry of 3 until
    `ModelRetryMiddleware` landed — removing it earlier would have left a
    window with no retry at all, which is why the procedure held it to 6.4.
    Now the middleware exists and is the ONLY retry layer.

    **Absence is not the same as zero, which is the whole point of this
    assertion.** Deleting the keyword inherits `DEFAULT_MAX_RETRIES = 2` and
    silently restores the stacking: two layers multiply rather than add, so the
    middleware's 3 attempts become 9 requests, and the SDK's `Retry-After`
    waits (up to 60s each) happen inside one middleware attempt where the
    visible layer cannot see, report or fall back from them.

    Checked on the AST rather than by grep so a commented-out or reformatted
    keyword cannot pass: what matters is what the CALL actually carries.
    """
    source = pathlib.Path(inspect.getfile(llm_module)).read_text(encoding="utf-8")
    tree = ast.parse(source)
    builder = next(n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "_build_llm")
    call = next(n for n in ast.walk(builder)
                if isinstance(n, ast.Call)
                and getattr(n.func, "id", "") == "AzureChatOpenAI")
    kwargs = {kw.arg: kw.value for kw in call.keywords}
    retries = kwargs.get("max_retries")
    assert retries is not None, (
        "the constructor no longer sets `max_retries` at all — which does NOT "
        "disable SDK retry, it inherits DEFAULT_MAX_RETRIES = 2 and silently "
        "restores the stacking this step removed (DECISIONS Part AI)"
    )
    assert isinstance(retries, ast.Constant) and retries.value == 0, (
        f"the constructor must pin retry OFF explicitly; found {retries!r}. "
        f"§19.4 puts retry on ModelRetryMiddleware, and two layers multiply "
        f"rather than add"
    )


def test_retry_is_owned_by_the_middleware_now() -> None:
    """The replacement exists, which is what made the deletion safe."""
    from backend.phases.nodes_common import RETRY_MAX

    assert RETRY_MAX == 2
    # "Attempts after the initial call" — so 2 is three attempts. Asserted
    # against the installed class rather than a comment, because the number in
    # the commit body depends on it.
    import inspect as _i
    from langchain.agents.middleware import ModelRetryMiddleware

    doc = ModelRetryMiddleware.__init__.__doc__ or ""
    assert "after the initial call" in doc, (
        "the semantics of max_retries changed — the three-attempts claim in "
        "DECISIONS Part AI and in this file's comments needs re-checking"
    )
    assert "range(self.max_retries + 1)" in _i.getsource(ModelRetryMiddleware)
