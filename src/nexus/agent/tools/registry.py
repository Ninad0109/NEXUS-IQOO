"""Tool registry defining supported phone-native agent capabilities."""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., Any]


class ToolRegistry:
    """Registry for agent tools."""

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, name: str, description: str, parameters: dict[str, Any], handler: Callable[..., Any]) -> None:
        self._tools[name.upper()] = ToolDefinition(
            name=name.upper(),
            description=description,
            parameters=parameters,
            handler=handler
        )

    def get_tool(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name.upper())

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())
