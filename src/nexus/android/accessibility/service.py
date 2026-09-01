"""Android Native AccessibilityService interface & protocol."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
from nexus.android.accessibility.parser import AccessibilityNode, UIHierarchyParser


@dataclass
class AccessibilityEvent:
    """Represents a live Android accessibility event."""
    event_type: str  # e.g., TYPE_WINDOW_STATE_CHANGED, TYPE_VIEW_CLICKED
    package_name: str
    class_name: str
    text: list[str]
    timestamp: float


class AccessibilityServiceInterface(ABC):
    """Abstract interface representing the on-device Android Accessibility Service."""

    @abstractmethod
    def get_root_in_active_window(self) -> list[AccessibilityNode]:
        """Returns the current accessibility node hierarchy."""
        pass

    @abstractmethod
    def perform_action(self, node: AccessibilityNode, action_code: int, args: Optional[dict[str, Any]] = None) -> bool:
        """Dispatches an accessibility action (ACTION_CLICK, ACTION_SET_TEXT, etc.) directly on a node."""
        pass

    @abstractmethod
    def perform_global_action(self, global_action_code: int) -> bool:
        """Dispatches a global accessibility action (GLOBAL_ACTION_BACK, GLOBAL_ACTION_HOME, etc.)."""
        pass


class NativeAccessibilityService(AccessibilityServiceInterface):
    """Bridge for the on-device native Android Accessibility Service daemon/socket."""

    def __init__(self, driver: Any = None):
        self.driver = driver
        self.parser = UIHierarchyParser()

    def get_root_in_active_window(self) -> list[AccessibilityNode]:
        if self.driver:
            xml_data = self.driver.dump_hierarchy()
            return self.parser.parse_xml(xml_data)
        return []

    def perform_action(self, node: AccessibilityNode, action_code: int, args: Optional[dict[str, Any]] = None) -> bool:
        if self.driver and node.centroid != (0, 0):
            # If native direct node action is not directly exposed over ADB, tap centroid
            return self.driver.tap(node.centroid[0], node.centroid[1])
        return False

    def perform_global_action(self, global_action_code: int) -> bool:
        if self.driver:
            # Android Global Actions: 1 = BACK, 2 = HOME, 3 = RECENTS, 4 = NOTIFICATIONS
            key_map = {1: 4, 2: 3, 3: 187, 4: 83}
            if global_action_code in key_map:
                return self.driver.keyevent(key_map[global_action_code])
        return False
