"""The ONE .env at the repository root (founder ruling 2026-10-31) — T1: no model call, no network, no value printed.

Agent Improve loads its environment from one function (`config.load_root_env`), reads tracing under LangSmith's own
names only, names each deployment once, and never sees LangChain's AZURESEARCH_FIELDS_* (Agent Resolve's field names,
which would re-point Improve's own indexes). Every name Improve's settings read is listed in the root .env.example."""
from __future__ import annotations

import os

import dotenv

from backend.core import config


def _setting_names() -> set[str]:
    """The environment variables Improve's settings read — each field's `env`, else its name."""
    return {f.field_info.extra.get("env") or name for name, f in config.Settings.__fields__.items()}


def test_settings_load_from_the_repository_root_env(monkeypatch) -> None:
    assert config.ENV_FILE == config.REPO_ROOT / ".env" and (config.REPO_ROOT / "agent-improve").is_dir()
    calls: list = []

    def recorded(path=None, **kw) -> bool:
        calls.append((path, kw))
        return True
    monkeypatch.setattr(dotenv, "load_dotenv", recorded)
    assert config.load_root_env() and calls == [(config.ENV_FILE, {"override": True})]
    if config.ENV_FILE.is_file():                    # the developer's and the staged worktree's copy
        values = dotenv.dotenv_values(config.ENV_FILE)
        for name in ("AZURE_OPENAI_API_VERSION", "AZURE_SEARCH_IMPROVE_CASE_INDEX", "AZURE_SEARCH_ENDPOINT"):
            if values.get(name):
                assert str(getattr(config.settings, name)) == values[name], f"{name} not from the root .env"


def test_no_azuresearch_field_names_reach_the_environment() -> None:
    assert not [k for k in os.environ if k.startswith("AZURESEARCH_FIELDS_")]
    if config.ENV_FILE.is_file():
        assert not [k for k in dotenv.dotenv_values(config.ENV_FILE) if k.startswith("AZURESEARCH_FIELDS_")]


def test_every_name_improve_reads_is_in_the_root_example_and_each_is_spelled_once() -> None:
    example = (config.REPO_ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
    listed = {ln.split("=", 1)[0] for ln in example if "=" in ln and not ln.lstrip().startswith("#")}
    assert all(ln.split("=", 1)[1] == "" for ln in example if "=" in ln and not ln.lstrip().startswith("#")), \
        "the example carries a value"
    names = _setting_names()
    assert names - listed == set(), sorted(names - listed)
    # One spelling: tracing under LANGSMITH_* only, one name per deployment, no alias left in the settings.
    assert not [n for n in names if n.startswith("LANGCHAIN_")], sorted(names)
    assert {"LANGSMITH_TRACING", "LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGSMITH_ENDPOINT"} <= names
    for old in ("LLM_INTENT_DEPLOYMENT", "LLM_REASONING_DEPLOYMENT", "LLM_PREMIUM_DEPLOYMENT"):
        assert old not in names and not hasattr(config.settings, old), old
    assert {"AZURE_OPENAI_INTENT_DEPLOYMENT", "AZURE_OPENAI_OPERATIONAL_DEPLOYMENT", "AZURE_OPENAI_PREMIUM_DEPLOYMENT",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"} <= names
