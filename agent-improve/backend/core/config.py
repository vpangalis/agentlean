from __future__ import annotations

import os
from typing import Optional

from pydantic.v1 import BaseSettings, Field


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

    LLM_INTENT_DEPLOYMENT: str = Field(
        "intent-model",
        env="AZURE_OPENAI_INTENT_DEPLOYMENT",
        description="Azure deployment for fast/cheap intent classification and routing.",
    )
    LLM_REASONING_DEPLOYMENT: str = Field(
        "operational-model",
        env="AZURE_OPENAI_OPERATIONAL_DEPLOYMENT",
        description="Azure deployment for operational reasoning and phase extraction.",
    )
    LLM_PREMIUM_DEPLOYMENT: str = Field(
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
        "improve_knowledge_index",
        env="AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX",
        description="Azure AI Search index for Agent Improve knowledge.",
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
    LOG_LEVEL: str = Field(
        "INFO",
        env="LOG_LEVEL",
        description="Logging level for the Agent Improve backend.",
    )

    LANGSMITH_API_KEY: Optional[str] = Field(
        None,
        env="LANGSMITH_API_KEY",
        description="LangSmith API key for tracing.",
    )
    LANGSMITH_PROJECT: Optional[str] = Field(
        None,
        env="LANGSMITH_PROJECT",
        description="LangSmith project name for tracing.",
    )
    LANGCHAIN_API_KEY: Optional[str] = Field(
        None,
        env="LANGCHAIN_API_KEY",
        description="LangChain/LangSmith API key for tracing (CLAUDE.md §1.8).",
    )
    LANGCHAIN_PROJECT: str = Field(
        "agentlean-improve",
        env="LANGCHAIN_PROJECT",
        description="LangSmith project name for tracing (CLAUDE.md §9).",
    )
    LANGCHAIN_ENDPOINT: Optional[str] = Field(
        None,
        env="LANGCHAIN_ENDPOINT",
        description="LangSmith endpoint override; default is LangSmith Cloud.",
    )
    ENVIRONMENT: str = Field(
        "development",
        env="ENVIRONMENT",
        description="Deployment environment; 'production' makes tracing mandatory.",
    )
    LANGFUSE_PUBLIC_KEY: Optional[str] = Field(
        None,
        env="LANGFUSE_PUBLIC_KEY",
        description="Langfuse public key for tracing.",
    )
    LANGFUSE_SECRET_KEY: Optional[str] = Field(
        None,
        env="LANGFUSE_SECRET_KEY",
        description="Langfuse secret key for tracing.",
    )
    LANGFUSE_HOST: Optional[str] = Field(
        None,
        env="LANGFUSE_HOST",
        description="Langfuse host URL.",
    )

    class Config(BaseSettings.Config):
        env_file = ".env"


from dotenv import load_dotenv

load_dotenv(override=True)

settings = Settings(
    AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    AZURE_OPENAI_API_KEY=os.getenv("AZURE_OPENAI_API_KEY", ""),
    AZURE_OPENAI_API_VERSION=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    LLM_INTENT_DEPLOYMENT=os.getenv("AZURE_OPENAI_INTENT_DEPLOYMENT", "intent-model"),
    LLM_REASONING_DEPLOYMENT=os.getenv("AZURE_OPENAI_OPERATIONAL_DEPLOYMENT", "operational-model"),
    LLM_PREMIUM_DEPLOYMENT=os.getenv("AZURE_OPENAI_PREMIUM_DEPLOYMENT", "operational-premium"),
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
    AZURE_SEARCH_ENDPOINT=os.getenv("AZURE_SEARCH_ENDPOINT", ""),
    AZURE_SEARCH_API_KEY=os.getenv("AZURE_SEARCH_API_KEY", ""),
    AZURE_SEARCH_IMPROVE_CASE_INDEX=os.getenv("AZURE_SEARCH_IMPROVE_CASE_INDEX", "improve_case_index"),
    AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX=os.getenv("AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX", "improve_knowledge_index"),
    AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX=os.getenv("AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX", "improve_evidence_index"),
    AZURE_SEARCH_RESOLVE_CASE_INDEX=os.getenv("AZURE_SEARCH_RESOLVE_CASE_INDEX", "case_index_v3"),
    AZURE_SEARCH_RESOLVE_KNOWLEDGE_INDEX=os.getenv("AZURE_SEARCH_RESOLVE_KNOWLEDGE_INDEX", "knowledge_index_v2"),
    AZURE_SEARCH_RESOLVE_EVIDENCE_INDEX=os.getenv("AZURE_SEARCH_RESOLVE_EVIDENCE_INDEX", "evidence_index_v1"),
    AZURE_BLOB_CONNECTION_STRING=os.getenv("AZURE_BLOB_CONNECTION_STRING", ""),
    AZURE_BLOB_CONTAINER_IMPROVE=os.getenv("AZURE_BLOB_CONTAINER_IMPROVE", "agent-improve-cases"),
    AGENT_IMPROVE_PORT=int(os.getenv("AGENT_IMPROVE_PORT", "8020")),
    GATE_MAX_ATTEMPTS=int(os.getenv("GATE_MAX_ATTEMPTS", "3")),
    LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
    LANGSMITH_API_KEY=os.getenv("LANGSMITH_API_KEY"),
    LANGSMITH_PROJECT=os.getenv("LANGSMITH_PROJECT"),
    LANGCHAIN_API_KEY=os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY"),
    LANGCHAIN_PROJECT=os.getenv("LANGCHAIN_PROJECT") or os.getenv("LANGSMITH_PROJECT") or "agentlean-improve",
    LANGCHAIN_ENDPOINT=os.getenv("LANGCHAIN_ENDPOINT"),
    ENVIRONMENT=os.getenv("ENVIRONMENT", "development"),
    LANGFUSE_PUBLIC_KEY=os.getenv("LANGFUSE_PUBLIC_KEY"),
    LANGFUSE_SECRET_KEY=os.getenv("LANGFUSE_SECRET_KEY"),
    LANGFUSE_HOST=os.getenv("LANGFUSE_HOST"),
)

__all__ = ["Settings", "settings"]
