from __future__ import annotations

import os
from typing import Protocol


class Settings(Protocol):
    AZURE_SEARCH_ENDPOINT: str
    AZURE_SEARCH_ADMIN_KEY: str
    AZURE_STORAGE_CONNECTION_STRING: str
    AZURE_STORAGE_CONTAINER: str


class EnvSettings:
    AZURE_SEARCH_ENDPOINT: str = os.environ["AZURE_SEARCH_ENDPOINT"]
    AZURE_SEARCH_ADMIN_KEY: str = os.environ["AZURE_SEARCH_ADMIN_KEY"]
    AZURE_STORAGE_CONNECTION_STRING: str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    AZURE_STORAGE_CONTAINER: str = os.environ["AZURE_STORAGE_CONTAINER"]


settings: Settings = EnvSettings()

__all__ = ["Settings", "settings"]
