from __future__ import annotations

from typing import Iterable, Protocol, TypeVar


TEvent = TypeVar("TEvent")


class EventHandler(Protocol[TEvent]):
    def handle(self, event: TEvent) -> None: ...


class DomainEventDispatcher:
    """Dispatches domain events to registered handlers synchronously."""

    def __init__(self, handlers: Iterable[EventHandler[TEvent]] | None = None) -> None:
        self._handlers: list[EventHandler[TEvent]] = list(handlers or [])

    def register(self, handler: EventHandler[TEvent]) -> None:
        self._handlers.append(handler)

    def dispatch(self, event: TEvent) -> None:
        for handler in self._handlers:
            handler.handle(event)


__all__ = ["DomainEventDispatcher", "EventHandler"]