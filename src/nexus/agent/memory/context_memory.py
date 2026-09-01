"""Context and episodic memory for NEXUS agent."""

from dataclasses import dataclass, field
import time
from typing import Any, Optional


@dataclass
class MemoryEntry:
    key: str
    value: Any
    timestamp: float = field(default_factory=time.time)
    category: str = "context"  # "context", "history", "preference", "state"


class ContextMemory:
    """Manages short-term conversation context and agent memory."""

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self._entries: list[MemoryEntry] = []
        self._kv_store: dict[str, Any] = {}

    def remember(self, key: str, value: Any, category: str = "context") -> None:
        """Stores a key-value fact or context."""
        self._kv_store[key] = value
        self._entries.append(MemoryEntry(key=key, value=value, category=category))
        if len(self._entries) > self.max_history:
            self._entries.pop(0)

    def retrieve(self, query: str) -> list[Any]:
        """Retrieves entries matching query."""
        results = []
        q_lower = query.lower()
        for e in reversed(self._entries):
            if q_lower in e.key.lower() or (isinstance(e.value, str) and q_lower in e.value.lower()):
                results.append(e.value)
        return results

    def get(self, key: str, default: Any = None) -> Any:
        return self._kv_store.get(key, default)

    def clear(self) -> None:
        self._entries.clear()
        self._kv_store.clear()
