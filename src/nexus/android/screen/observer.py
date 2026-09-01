"""ScreenObserver generating compact structured representations for agent reasoning."""

from dataclasses import dataclass, field
import json
import logging
from typing import Any, Optional
from nexus.android.accessibility.parser import UIHierarchyParser, AccessibilityNode
from nexus.android.actions.launcher import AppLauncher
from nexus.android.actions.adb_dev import ADBBridge

logger = logging.getLogger("nexus.android.screen")


@dataclass
class CompactScreenElement:
    """Compact structured element description."""
    node_id: str
    text: str
    element_type: str = "element"
    clickable: bool = False
    resource_id: str = ""
    bounds: tuple[int, int, int, int] = (0, 0, 0, 0)

    def to_dict(self) -> dict[str, Any]:
        d = {
            "text": self.text,
            "type": self.element_type,
            "clickable": self.clickable,
        }
        if self.resource_id:
            d["resource_id"] = self.resource_id
        if self.bounds != (0, 0, 0, 0):
            d["bounds"] = list(self.bounds)
        return d


@dataclass
class CompactScreenState:
    """Compact summary of current screen for LLM reasoning without sending raw image frames."""
    app: str
    package: str
    screen: str = "Main"
    elements: list[CompactScreenElement] = field(default_factory=list)
    visible_text: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "app": self.app,
            "screen": self.screen,
            "elements": [e.to_dict() for e in self.elements[:30]],
            "visible_text": self.visible_text[:30],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class ScreenObserver:
    """Observes the Android UI tree and constructs a compact structured screen representation."""

    def __init__(self, driver: Optional[Any] = None, max_elements: int = 30):
        self.driver = driver if driver is not None else ADBBridge()
        self.parser = UIHierarchyParser()
        self.launcher = AppLauncher()
        self.max_elements = max_elements

    def observe(self, xml_override: Optional[str] = None) -> CompactScreenState:
        """Captures active UI hierarchy and extracts semantic compact state."""
        if xml_override is not None:
            xml_dump = xml_override
            pkg = "com.whatsapp"
        else:
            xml_dump = self.driver.dump_hierarchy() if hasattr(self.driver, "dump_hierarchy") else ""
            pkg = self.driver.get_foreground_app() if hasattr(self.driver, "get_foreground_app") else "unknown"

        app_name = self.launcher.get_app_name(pkg)
        
        if not xml_dump:
            return CompactScreenState(
                app=app_name,
                package=pkg,
                screen="Unknown",
                elements=[],
                visible_text=[]
            )

        root_nodes = self.parser.parse_xml(xml_dump)
        flat_nodes = self.parser.flatten_nodes(root_nodes)
        visible_texts = self.parser.extract_visible_text(root_nodes)

        compact_elements: list[CompactScreenElement] = []
        for n in flat_nodes:
            if n.text or n.content_desc or n.clickable:
                label = n.text or n.content_desc
                if label:
                    compact_elements.append(CompactScreenElement(
                        node_id=n.node_id,
                        text=label,
                        element_type=n.element_type,
                        clickable=n.clickable,
                        resource_id=n.resource_id,
                        bounds=n.bounds,
                    ))

        # Infer screen title if any
        screen_title = "Main"
        for n in flat_nodes[:5]:
            if "title" in n.resource_id.lower() or "header" in n.resource_id.lower():
                if n.text:
                    screen_title = n.text
                    break

        return CompactScreenState(
            app=app_name,
            package=pkg,
            screen=screen_title,
            elements=compact_elements[:self.max_elements],
            visible_text=visible_texts[:self.max_elements],
        )
