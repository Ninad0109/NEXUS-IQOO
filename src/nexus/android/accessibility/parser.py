"""Android Accessibility & UI Hierarchy XML/JSON parser."""

from dataclasses import dataclass, field
import re
import xml.etree.ElementTree as ET
from typing import Any


@dataclass
class AccessibilityNode:
    """Represents a semantic UI element in the Android accessibility tree."""

    node_id: str
    text: str = ""
    resource_id: str = ""
    content_desc: str = ""
    class_name: str = ""
    package: str = ""
    bounds: tuple[int, int, int, int] = (0, 0, 0, 0)  # (x1, y1, x2, y2)
    centroid: tuple[int, int] = (0, 0)  # (center_x, center_y)
    clickable: bool = False
    scrollable: bool = False
    editable: bool = False
    focused: bool = False
    enabled: bool = True
    children: list["AccessibilityNode"] = field(default_factory=list)

    @property
    def element_type(self) -> str:
        """Infer high-level semantic element type from class name and properties."""
        cls = self.class_name.lower()
        if "button" in cls or "imagebutton" in cls:
            return "button"
        if "edittext" in cls:
            return "input"
        if "textview" in cls:
            return "text"
        if "image" in cls:
            return "icon"
        if "tab" in cls or "tabhost" in cls:
            return "tab"
        if "listview" in cls or "recyclerview" in cls:
            return "list"
        if "checkbox" in cls:
            return "checkbox"
        if "switch" in cls:
            return "switch"
        return "element"


class UIHierarchyParser:
    """Parses UIAutomator / Accessibility XML dumps into hierarchical & flat AccessibilityNodes."""

    BOUNDS_PATTERN = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]|(\d+),(\d+),(\d+),(\d+)")

    def parse_bounds(self, bounds_str: str) -> tuple[int, int, int, int]:
        """Extract (x1, y1, x2, y2) bounds from strings like '[0,0][1080,2400]'."""
        if not bounds_str:
            return (0, 0, 0, 0)
        
        match = self.BOUNDS_PATTERN.search(bounds_str)
        if match:
            groups = [g for g in match.groups() if g is not None]
            if len(groups) == 4:
                return (int(groups[0]), int(groups[1]), int(groups[2]), int(groups[3]))
        
        # Fallback numeric extraction
        nums = re.findall(r"\d+", bounds_str)
        if len(nums) >= 4:
            return (int(nums[0]), int(nums[1]), int(nums[2]), int(nums[3]))
        return (0, 0, 0, 0)

    def _parse_xml_node(self, elem: ET.Element, depth: int, index: int, prefix: str = "") -> AccessibilityNode:
        node_id = f"{prefix}node_{depth}_{index}"
        attrib = elem.attrib

        bounds = self.parse_bounds(attrib.get("bounds", ""))
        cx = (bounds[0] + bounds[2]) // 2
        cy = (bounds[1] + bounds[3]) // 2

        node = AccessibilityNode(
            node_id=node_id,
            text=attrib.get("text", "").strip(),
            resource_id=attrib.get("resource-id", "").strip(),
            content_desc=attrib.get("content-desc", "").strip(),
            class_name=attrib.get("class", "").strip(),
            package=attrib.get("package", "").strip(),
            bounds=bounds,
            centroid=(cx, cy),
            clickable=attrib.get("clickable", "false").lower() == "true",
            scrollable=attrib.get("scrollable", "false").lower() == "true",
            editable="edittext" in attrib.get("class", "").lower() or attrib.get("editable", "false").lower() == "true",
            focused=attrib.get("focused", "false").lower() == "true",
            enabled=attrib.get("enabled", "true").lower() == "true",
        )

        for child_idx, child_elem in enumerate(elem):
            child_node = self._parse_xml_node(child_elem, depth + 1, child_idx, prefix=f"{node_id}_")
            node.children.append(child_node)

        return node

    def parse_xml(self, xml_content: str) -> list[AccessibilityNode]:
        """Parses an XML string from UIAutomator dump into a list of root AccessibilityNodes."""
        if not xml_content or not xml_content.strip():
            return []
        
        try:
            root = ET.fromstring(xml_content.strip())
        except ET.ParseError:
            return []

        # If the root is <hierarchy>, its direct children are the root windows/nodes
        if root.tag == "hierarchy":
            roots = []
            for idx, child in enumerate(root):
                roots.append(self._parse_xml_node(child, depth=0, index=idx))
            return roots
        
        return [self._parse_xml_node(root, depth=0, index=0)]

    def flatten_nodes(self, root_nodes: list[AccessibilityNode]) -> list[AccessibilityNode]:
        """Returns a flat list of all accessibility nodes."""
        flat: list[AccessibilityNode] = []

        def traverse(n: AccessibilityNode):
            flat.append(n)
            for c in n.children:
                traverse(c)

        for root in root_nodes:
            traverse(root)
        return flat

    def extract_visible_text(self, root_nodes: list[AccessibilityNode]) -> list[str]:
        """Extracts all non-empty unique text strings and content descriptions from the tree."""
        texts: list[str] = []
        seen = set()

        for node in self.flatten_nodes(root_nodes):
            if node.text and node.text not in seen:
                texts.append(node.text)
                seen.add(node.text)
            elif node.content_desc and node.content_desc not in seen:
                texts.append(node.content_desc)
                seen.add(node.content_desc)

        return texts
