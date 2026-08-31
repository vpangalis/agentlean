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


def test_max_retries_stays_until_step_6_4() -> None:
    """The constructor keeps `max_retries=3` until ModelRetryMiddleware lands.

    Removing it before the replacement exists leaves a window with no retry at
    all, so the procedure holds it to step 6.4. This test is the tripwire: when
    6.4 deletes the line, it fails and must be deleted with it.
    """
    source = pathlib.Path(inspect.getfile(llm_module)).read_text(encoding="utf-8")
    tree = ast.parse(source)
    builder = next(n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "_build_llm")
    call = next(n for n in ast.walk(builder)
                if isinstance(n, ast.Call)
                and getattr(n.func, "id", "") == "AzureChatOpenAI")
    retries = {kw.arg: kw.value for kw in call.keywords}["max_retries"]
    assert isinstance(retries, ast.Constant) and retries.value == 3
