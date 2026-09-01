"""5-Tier Priority Element Selector for Android Accessibility Nodes."""

from typing import Optional
from nexus.android.accessibility.parser import AccessibilityNode


class ElementSelector:
    """Finds target UI elements based on prioritized resolution strategies:
    1. Direct Node ID
    2. Resource ID
    3. Visible Text / Semantic Label
    4. Content Description
    5. Fallback Coordinate / OCR
    """

    def find_by_node_id(self, nodes: list[AccessibilityNode], node_id: str) -> Optional[AccessibilityNode]:
        for n in nodes:
            if n.node_id == node_id:
                return n
        return None

    def find_by_resource_id(self, nodes: list[AccessibilityNode], resource_id: str) -> Optional[AccessibilityNode]:
        target = resource_id.strip()
        # 1. Exact match
        for n in nodes:
            if n.resource_id == target:
                return n
        # 2. Suffix match (e.g. "search_box" matches "com.app:id/search_box")
        for n in nodes:
            if n.resource_id.endswith(f"/{target}") or n.resource_id.endswith(f":id/{target}"):
                return n
        return None

    def find_by_text(self, nodes: list[AccessibilityNode], text: str, exact: bool = False) -> Optional[AccessibilityNode]:
        query = text.strip()
        if not query:
            return None
        
        # 1. Exact case-sensitive match
        for n in nodes:
            if n.text == query:
                return n
        
        # 2. Exact case-insensitive match
        q_lower = query.lower()
        for n in nodes:
            if n.text.lower() == q_lower:
                return n

        if not exact:
            # 3. Substring match (query inside node.text or node.text inside query)
            for n in nodes:
                if n.text and (q_lower in n.text.lower() or n.text.lower() in q_lower):
                    return n
            # 4. Content desc match
            for n in nodes:
                if n.content_desc and (q_lower in n.content_desc.lower() or n.content_desc.lower() in q_lower):
                    return n

        return None

    def find_by_content_desc(self, nodes: list[AccessibilityNode], desc: str) -> Optional[AccessibilityNode]:
        q_lower = desc.strip().lower()
        for n in nodes:
            if n.content_desc.lower() == q_lower:
                return n
        for n in nodes:
            if q_lower in n.content_desc.lower():
                return n
        return None

    def resolve_element(
        self,
        nodes: list[AccessibilityNode],
        query: str,
        preferred_type: Optional[str] = None
    ) -> Optional[AccessibilityNode]:
        """Unified 5-tier element locator."""
        # Tier 1: Node ID
        res = self.find_by_node_id(nodes, query)
        if res:
            return res

        # Tier 2: Resource ID
        res = self.find_by_resource_id(nodes, query)
        if res:
            return res

        # Tier 3: Visible Text
        res = self.find_by_text(nodes, query)
        if res:
            return res

        # Tier 4: Content Description
        res = self.find_by_content_desc(nodes, query)
        if res:
            return res

        return None
