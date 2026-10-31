from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import dotenv
from pydantic.v1 import BaseSettings, Field

#: ONE .env for the platform, at the repository root (founder ruling 2026-10-31): Agent Improve's settings under
#: their own names, Agent Resolve's legacy block beside them. `backend/core/config.py` → core, backend,
#: agent-improve, the repository.
REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPO_ROOT / ".env"


def load_root_env() -> bool:
    """The one place Agent Improve loads its environment: the repository root's `.env`, overriding the process
    (`override=True`, the project's rule). Called through the `dotenv` module so a test that stubs it stubs this."""
    return dotenv.load_dotenv(ENV_FILE, override=True)

#: The methodology index the coach reads when `AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX`
#: is unset — the CURRENT one: the BB-eBook-only rebuild (1,184 docs). The index it
#: replaced (a contaminated corpus) is named nowhere in code or config, and drift
#: pattern-12 bans its old name, so a missing variable never coaches from it.
KNOWLEDGE_INDEX_DEFAULT = "improve_knowledge_index_v3"

#: R-F (founder ruling 2026-10-27, amending ADR-0080): 45 s is a PROGRESS THRESHOLD, not a cancellation — the
#: page tells the Belt the coach is still working (ui/index.html's TURN_PROGRESS_MS reads the same 45). The turn
#: goes on to the hard limit; a turn whose answer is produced is never cancelled — it always finishes its save.
#: The closing reserve is the time kept, inside the hard limit, for answering after the graph returns.
TURN_LIMIT_S = 45.0
TURN_HARD_LIMIT_S = 120.0
TURN_CLOSE_RESERVE_S = 3.0


class Settings(BaseSettings):
    AZURE_OPENAI_ENDPOINT: str = Field(
        "",
        env="AZURE_OPENAI_ENDPOINT",
        description="Azure OpenAI endpoint URL.",
    )
    AZURE_OPENAI_API_KEY: str = Field(
        "",
        env="AZURE_OPENAI_API_KEY",
        description="Azure OpenAI API key.",
    )
    AZURE_OPENAI_API_VERSION: str = Field(
        "2024-02-15-preview",
        env="AZURE_OPENAI_API_VERSION",
        description="Azure OpenAI API version.",
    )

    # One name per deployment (founder ruling 2026-10-31): each setting is the variable it reads.
    AZURE_OPENAI_INTENT_DEPLOYMENT: str = Field(
        "intent-model",
        env="AZURE_OPENAI_INTENT_DEPLOYMENT",
        description="Azure deployment for fast/cheap intent classification and routing.",
    )
    AZURE_OPENAI_OPERATIONAL_DEPLOYMENT: str = Field(
        "operational-model",
        env="AZURE_OPENAI_OPERATIONAL_DEPLOYMENT",
        description="Azure deployment for operational reasoning and phase extraction.",
    )
    AZURE_OPENAI_PREMIUM_DEPLOYMENT: str = Field(
        "operational-premium",
        env="AZURE_OPENAI_PREMIUM_DEPLOYMENT",
        description="Azure deployment for premium reasoning and reflection.",
    )
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = Field(
        "text-embedding-3-large",
        env="AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
        description="Azure deployment for text embeddings.",
    )

    AZURE_SEARCH_ENDPOINT: str = Field(
        "",
        env="AZURE_SEARCH_ENDPOINT",
        description="Azure AI Search endpoint URL.",
    )
    AZURE_SEARCH_API_KEY: str = Field(
        "",
        env="AZURE_SEARCH_API_KEY",
        description="Azure AI Search admin API key.",
    )

    AZURE_SEARCH_IMPROVE_CASE_INDEX: str = Field(
        "improve_case_index",
        env="AZURE_SEARCH_IMPROVE_CASE_INDEX",
        description="Azure AI Search index for Agent Improve cases.",
    )
    AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX: str = Field(
        KNOWLEDGE_INDEX_DEFAULT,
        env="AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX",
        description="Azure AI Search index for Agent Improve knowledge.",
    )
    AZURE_SEARCH_KNOWLEDGE_SEMANTIC_CONFIG: str = Field(
        "",
        env="AZURE_SEARCH_KNOWLEDGE_SEMANTIC_CONFIG",
        description=("ADR-0060 decision 2 (B9): the knowledge index's semantic configuration. Set, every methodology "
                     "search is ranked by Azure AI Search's semantic ranker (semantic_hybrid); empty, hybrid only."),
    )
    AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX: str = Field(
        default="improve_evidence_index",
        env="AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX",
        description="Azure AI Search index for Agent Improve uploaded evidence.",
    )
    AZURE_SEARCH_RESOLVE_CASE_INDEX: str = Field(
        "case_index_v3",
        env="AZURE_SEARCH_RESOLVE_CASE_INDEX",
        description="Azure AI Search index for Agent Resolve cases (read-only cross-agent).",
    )
    AZURE_SEARCH_RESOLVE_KNOWLEDGE_INDEX: str = Field(
        "knowledge_index_v2",
        env="AZURE_SEARCH_RESOLVE_KNOWLEDGE_INDEX",
        description="Azure AI Search index for Agent Resolve knowledge (read-only cross-agent).",
    )
    AZURE_SEARCH_RESOLVE_EVIDENCE_INDEX: str = Field(
        "evidence_index_v1",
        env="AZURE_SEARCH_RESOLVE_EVIDENCE_INDEX",
        description="Azure AI Search index for Agent Resolve evidence (read-only cross-agent).",
    )

    AZURE_BLOB_CONNECTION_STRING: str = Field(
        "",
        env="AZURE_BLOB_CONNECTION_STRING",
        description="Azure Blob Storage connection string.",
    )
    AZURE_BLOB_CONTAINER_IMPROVE: str = Field(
        "agent-improve-cases",
        env="AZURE_BLOB_CONTAINER_IMPROVE",
        description="Azure Blob Storage container for Agent Improve cases.",
    )

    AGENT_IMPROVE_PORT: int = Field(
        8020,
        env="AGENT_IMPROVE_PORT",
        description="Port for the Agent Improve backend server.",
    )
    GATE_MAX_ATTEMPTS: int = Field(
        3,
        env="GATE_MAX_ATTEMPTS",
        description="Maximum gate validation attempts before escalation.",
    )
    SESSION_SECRET: str = Field(
        "",
        env="SESSION_SECRET",
        description=("ADR-0091: the key that signs each case's session cookie. Empty: a key for the running "
                     "process only, so every session ends when the server restarts."),
    )
    LOG_LEVEL: str = Field(
        "INFO",
        env="LOG_LEVEL",
        description="Logging level for the Agent Improve backend.",
    )

    # Tracing under LangSmith's own names only (founder ruling 2026-10-31) — no LANGCHAIN_* spelling is read.
    LANGSMITH_TRACING: str = Field(
        "true",
        env="LANGSMITH_TRACING",
        description="LangSmith tracing switch; tracing is mandatory, so init_tracing turns it on whenever a key is set.",
    )
    LANGSMITH_API_KEY: Optional[str] = Field(
        None,
        env="LANGSMITH_API_KEY",
        description="LangSmith API key for tracing.",
    )
    LANGSMITH_PROJECT: str = Field(
        "agentlean-improve",
        env="LANGSMITH_PROJECT",
        description="LangSmith project name for tracing.",
    )
    LANGSMITH_ENDPOINT: Optional[str] = Field(
        None,
        env="LANGSMITH_ENDPOINT",
        description="LangSmith endpoint override; default is LangSmith Cloud.",
    )
    ENVIRONMENT: str = Field(
        "development",
        env="ENVIRONMENT",
        description="Deployment environment; 'production' makes tracing mandatory.",
    )
    GUARD_MODE: str = Field(
        "strict",
        env="GUARD_MODE",
        description="The input guard's mode (ADR-0067, T94): 'strict' unless 'development' is set explicitly.",
    )
    CONTENT_SAFETY_ENDPOINT: Optional[str] = Field(
        None,
        env="CONTENT_SAFETY_ENDPOINT",
        description="Azure AI Content Safety endpoint (private endpoint) for Prompt Shields — ADR-0057.",
    )
    CONTENT_SAFETY_KEY: Optional[str] = Field(
        None,
        env="CONTENT_SAFETY_KEY",
        description="Azure AI Content Safety key — ADR-0057.",
    )

    class Config(BaseSettings.Config):
        env_file = str(ENV_FILE)


load_root_env()

settings = Settings(
    AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    AZURE_OPENAI_API_KEY=os.getenv("AZURE_OPENAI_API_KEY", ""),
    AZURE_OPENAI_API_VERSION=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    AZURE_OPENAI_INTENT_DEPLOYMENT=os.getenv("AZURE_OPENAI_INTENT_DEPLOYMENT", "intent-model"),
    AZURE_OPENAI_OPERATIONAL_DEPLOYMENT=os.getenv("AZURE_OPENAI_OPERATIONAL_DEPLOYMENT", "operational-model"),
    AZURE_OPENAI_PREMIUM_DEPLOYMENT=os.getenv("AZURE_OPENAI_PREMIUM_DEPLOYMENT", "operational-premium"),
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
    AZURE_SEARCH_ENDPOINT=os.getenv("AZURE_SEARCH_ENDPOINT", ""),
    AZURE_SEARCH_API_KEY=os.getenv("AZURE_SEARCH_API_KEY", ""),
    AZURE_SEARCH_IMPROVE_CASE_INDEX=os.getenv("AZURE_SEARCH_IMPROVE_CASE_INDEX", "improve_case_index"),
    AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX=os.getenv("AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX", KNOWLEDGE_INDEX_DEFAULT),
    AZURE_SEARCH_KNOWLEDGE_SEMANTIC_CONFIG=os.getenv("AZURE_SEARCH_KNOWLEDGE_SEMANTIC_CONFIG", ""),
    AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX=os.getenv("AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX", "improve_evidence_index"),
    AZURE_SEARCH_RESOLVE_CASE_INDEX=os.getenv("AZURE_SEARCH_RESOLVE_CASE_INDEX", "case_index_v3"),
    AZURE_SEARCH_RESOLVE_KNOWLEDGE_INDEX=os.getenv("AZURE_SEARCH_RESOLVE_KNOWLEDGE_INDEX", "knowledge_index_v2"),
    AZURE_SEARCH_RESOLVE_EVIDENCE_INDEX=os.getenv("AZURE_SEARCH_RESOLVE_EVIDENCE_INDEX", "evidence_index_v1"),
    AZURE_BLOB_CONNECTION_STRING=os.getenv("AZURE_BLOB_CONNECTION_STRING", ""),
    AZURE_BLOB_CONTAINER_IMPROVE=os.getenv("AZURE_BLOB_CONTAINER_IMPROVE", "agent-improve-cases"),
    AGENT_IMPROVE_PORT=int(os.getenv("AGENT_IMPROVE_PORT", "8020")),
    GATE_MAX_ATTEMPTS=int(os.getenv("GATE_MAX_ATTEMPTS", "3")),
    SESSION_SECRET=os.getenv("SESSION_SECRET", ""),
    LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
    LANGSMITH_TRACING=os.getenv("LANGSMITH_TRACING", "true"),
    LANGSMITH_API_KEY=os.getenv("LANGSMITH_API_KEY"),
    LANGSMITH_PROJECT=os.getenv("LANGSMITH_PROJECT") or "agentlean-improve",
    LANGSMITH_ENDPOINT=os.getenv("LANGSMITH_ENDPOINT"),
    ENVIRONMENT=os.getenv("ENVIRONMENT", "development"),
    GUARD_MODE=os.getenv("GUARD_MODE", "strict"),
    CONTENT_SAFETY_ENDPOINT=os.getenv("CONTENT_SAFETY_ENDPOINT"),
    CONTENT_SAFETY_KEY=os.getenv("CONTENT_SAFETY_KEY"),
)

#: T67 (DEF-139): the credentials Agent Improve cannot run a turn without — the coaching
#: models, retrieval and the case store. Missing at start-up, the app exits with status 1.
REQUIRED_CREDENTIALS: tuple[str, ...] = (
    "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY",
    "AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_API_KEY",
    "AZURE_BLOB_CONNECTION_STRING",
)


def missing_credentials(s: "Settings | None" = None) -> list[str]:
    """The required credentials that are not set (blank counts as not set)."""
    s = s or settings
    missing = [name for name in REQUIRED_CREDENTIALS if not str(getattr(s, name, "") or "").strip()]
    # ADR-0105 decision 8: outside GUARD_MODE=development the sessions and one-time codes are signed with
    # SESSION_SECRET — without it a restart would void every code and session, so the app does not start.
    if str(getattr(s, "GUARD_MODE", "strict") or "").strip().lower() != "development" \
            and not str(getattr(s, "SESSION_SECRET", "") or "").strip():
        missing.append("SESSION_SECRET")
    return missing


def check_credentials() -> None:
    """T67: name every missing credential on stderr and exit with status 1 — before the app
    accepts a request, so a container without them never receives traffic."""
    missing = missing_credentials()
    if missing:
        print("Agent Improve cannot start — required credential(s) missing: " + ", ".join(missing)
              + ". Set them in the repository root's .env or the environment.", file=sys.stderr)
        raise SystemExit(1)


__all__ = ["Settings", "settings", "REQUIRED_CREDENTIALS", "missing_credentials", "check_credentials", "REPO_ROOT",
           "ENV_FILE", "load_root_env"]
