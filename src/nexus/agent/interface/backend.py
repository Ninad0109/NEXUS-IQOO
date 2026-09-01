"""AgentBackend abstract interface isolating reasoning from device automation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from nexus.android.screen.observer import CompactScreenState
from nexus.android.actions.executor import ActionResult


@dataclass
class ActionPlan:
    """Structured plan produced by the AgentBackend."""
    action: str
    thought: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    expected_result: str = ""
    target_package: str = ""
    sub_action: Optional[dict[str, Any]] = None


class AgentBackend(ABC):
    """Abstract interface defining the reasoning backend."""

    @abstractmethod
    async def plan(self, command: str, observation: CompactScreenState) -> ActionPlan:
        """Determines the next structured action based on command and screen state."""
        pass

    @abstractmethod
    async def execute(self, tool_name: str, params: dict[str, Any]) -> ActionResult:
        """Executes a tool action through the action layer."""
        pass

    @abstractmethod
    async def remember(self, key: str, value: Any) -> None:
        """Stores contextual state or fact."""
        pass

    @abstractmethod
    async def retrieve(self, query: str) -> list[Any]:
        """Retrieves stored memory matching query."""
        pass
