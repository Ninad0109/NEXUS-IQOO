"""Android Action Executor supporting semantic priority dispatch."""

from dataclasses import dataclass
import logging
from typing import Any, Optional
from nexus.android.accessibility.parser import UIHierarchyParser, AccessibilityNode
from nexus.android.accessibility.selector import ElementSelector
from nexus.android.actions.launcher import AppLauncher
from nexus.android.actions.adb_dev import ADBBridge

logger = logging.getLogger("nexus.android.actions")


@dataclass
class ActionResult:
    """Outcome of an Android action execution."""
    success: bool
    action: str
    target: str = ""
    message: str = ""
    data: Optional[dict[str, Any]] = None


class ActionExecutor:
    """Executes structured phone actions via Accessibility Service / ADB Driver."""

    def __init__(self, driver: Optional[Any] = None, simulation: bool = False):
        self.simulation = simulation
        self.driver = driver if driver is not None else ADBBridge()
        self.launcher = AppLauncher()
        self.parser = UIHierarchyParser()
        self.selector = ElementSelector()

    def open_app(self, app_name_or_package: str) -> ActionResult:
        """Launches target application by package or friendly name."""
        pkg = self.launcher.resolve_package(app_name_or_package)
        app_title = self.launcher.get_app_name(pkg)
        
        logger.info(f"Launching app: {app_title} ({pkg})")
        if not self.simulation:
            # Launch via monkey or am start
            self.driver.shell(f"monkey -p {pkg} -c android.intent.category.LAUNCHER 1")

        return ActionResult(
            success=True,
            action="OPEN_APP",
            target=pkg,
            message=f"Opened {app_title}",
            data={"package": pkg, "app_name": app_title}
        )

    def back(self) -> ActionResult:
        """Navigates back."""
        if not self.simulation:
            self.driver.keyevent(4)
        return ActionResult(success=True, action="BACK", message="Navigated back")

    def home(self) -> ActionResult:
        """Navigates home."""
        if not self.simulation:
            self.driver.keyevent(3)
        return ActionResult(success=True, action="HOME", message="Navigated to home screen")

    def tap_text(self, text: str, exact: bool = False) -> ActionResult:
        """Finds element matching text and taps its center."""
        xml_dump = self.driver.dump_hierarchy() if not self.simulation else ""
        nodes = self.parser.flatten_nodes(self.parser.parse_xml(xml_dump))
        target_node = self.selector.find_by_text(nodes, text, exact=exact)

        if not target_node:
            # Fallback search by content description or resource ID
            target_node = self.selector.resolve_element(nodes, text)

        if target_node:
            cx, cy = target_node.centroid
            if not self.simulation:
                self.driver.tap(cx, cy)
            return ActionResult(
                success=True,
                action="TAP_TEXT",
                target=text,
                message=f"Tapped '{text}' at ({cx}, {cy})",
                data={"node_id": target_node.node_id, "bounds": target_node.bounds, "coordinates": (cx, cy)}
            )
        
        return ActionResult(
            success=False,
            action="TAP_TEXT",
            target=text,
            message=f"Element with text '{text}' not found on active screen"
        )

    def tap_node(self, node_id_or_resource_id: str) -> ActionResult:
        """Taps element by node_id or resource_id."""
        xml_dump = self.driver.dump_hierarchy() if not self.simulation else ""
        nodes = self.parser.flatten_nodes(self.parser.parse_xml(xml_dump))
        target_node = self.selector.find_by_resource_id(nodes, node_id_or_resource_id)
        if not target_node:
            target_node = self.selector.find_by_node_id(nodes, node_id_or_resource_id)

        if target_node:
            cx, cy = target_node.centroid
            if not self.simulation:
                self.driver.tap(cx, cy)
            return ActionResult(
                success=True,
                action="TAP_NODE",
                target=node_id_or_resource_id,
                message=f"Tapped node '{node_id_or_resource_id}' at ({cx}, {cy})",
                data={"coordinates": (cx, cy)}
            )

        return ActionResult(
            success=False,
            action="TAP_NODE",
            target=node_id_or_resource_id,
            message=f"Node '{node_id_or_resource_id}' not found"
        )

    def type_text(self, text: str) -> ActionResult:
        """Types text into current focused element."""
        if not self.simulation:
            self.driver.type_text(text)
        return ActionResult(
            success=True,
            action="TYPE_TEXT",
            target=text,
            message=f"Typed text: '{text}'"
        )

    def swipe(self, direction: str = "UP", distance_px: int = 600) -> ActionResult:
        """Swipes in cardinal direction (UP, DOWN, LEFT, RIGHT)."""
        # Default middle coordinates for standard 1080x2400 screen
        mid_x, mid_y = 540, 1200
        direction = direction.upper()
        
        if direction == "UP":
            x1, y1, x2, y2 = mid_x, mid_y + (distance_px // 2), mid_x, mid_y - (distance_px // 2)
        elif direction == "DOWN":
            x1, y1, x2, y2 = mid_x, mid_y - (distance_px // 2), mid_x, mid_y + (distance_px // 2)
        elif direction == "LEFT":
            x1, y1, x2, y2 = mid_x + (distance_px // 2), mid_y, mid_x - (distance_px // 2), mid_y
        elif direction == "RIGHT":
            x1, y1, x2, y2 = mid_x - (distance_px // 2), mid_y, mid_x + (distance_px // 2), mid_y
        else:
            x1, y1, x2, y2 = mid_x, mid_y + 300, mid_x, mid_y - 300

        if not self.simulation:
            self.driver.swipe(x1, y1, x2, y2)
            
        return ActionResult(
            success=True,
            action="SWIPE",
            target=direction,
            message=f"Swiped {direction}"
        )

    def take_screenshot(self) -> ActionResult:
        """Captures screen."""
        screenshot_bytes = b"" if self.simulation else self.driver.capture_screenshot()
        return ActionResult(
            success=True,
            action="TAKE_SCREENSHOT",
            message=f"Captured screenshot ({len(screenshot_bytes)} bytes)",
            data={"bytes": screenshot_bytes}
        )
