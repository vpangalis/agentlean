from __future__ import annotations

import os
from typing import Any

import requests


class EmbeddingClient:
    """Infrastructure client for generating embeddings."""

    def __init__(self, openai_client: Any | None = None, settings_module: Any | None = None) -> None:
        self._openai_client = openai_client
        self._settings = settings_module

    def generate_embedding(self, text: str) -> list[float]:
        if self._openai_client is not None:
            if self._settings is None:
                raise ValueError("Settings module is required for OpenAI embeddings.")
            embedding = (
                self._openai_client.embeddings.create(
                    model=self._settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                    input=text,
                )
                .data[0]
                .embedding
            )
            return embedding

        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

        if not endpoint or not api_key or not deployment:
            raise ValueError("Azure OpenAI embedding configuration is missing.")

        url = (
            f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/embeddings?"
            f"api-version={api_version}"
        )
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key,
        }
        payload = {
            "input": text,
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"Embedding request failed: {response.text}")
        body = response.json()
        return body["data"][0]["embedding"]
