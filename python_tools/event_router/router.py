"""Small event router for validated GitHub webhook payloads."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


Handler = Callable[[dict[str, Any]], Any]


class EventRouter:
    """Route ``X-GitHub-Event`` payloads to explicit handlers."""

    def __init__(self) -> None:
        self._handlers: dict[tuple[str, str | None], Handler] = {}

    def register(self, event: str, handler: Handler, action: str | None = None) -> None:
        if not event.strip():
            raise ValueError("event must not be empty")
        self._handlers[(event, action)] = handler

    def dispatch(self, event: str, payload: dict[str, Any]) -> Any:
        action = payload.get("action")
        handler = self._handlers.get((event, action)) or self._handlers.get((event, None))
        if handler is None:
            return None
        return handler(payload)
