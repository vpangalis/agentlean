from __future__ import annotations

from backend.bridge import BackendContainer


def build_backend_container() -> BackendContainer:
	from backend.app.config import settings

	return BackendContainer(settings)


def get_settings():
	from backend.app.config import settings

	return settings


__all__ = ["build_backend_container", "get_settings"]
