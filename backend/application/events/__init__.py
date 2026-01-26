"""Application-level event dispatching."""

from .EventDispatcher import DomainEventDispatcher, EventHandler

__all__ = ["DomainEventDispatcher", "EventHandler"]