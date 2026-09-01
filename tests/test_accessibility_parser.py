"""Tests for UIHierarchyParser and AccessibilityNode."""

from nexus.android.accessibility.parser import AccessibilityNode, UIHierarchyParser
from nexus.android.accessibility.selector import ElementSelector

SAMPLE_XML_HIERARCHY = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout" package="com.whatsapp" content-desc="" checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[0,0][1080,2400]">
    <node index="0" text="" resource-id="com.whatsapp:id/toolbar" class="android.view.ViewGroup" package="com.whatsapp" content-desc="" bounds="[0,72][1080,240]">
      <node index="0" text="WhatsApp" resource-id="com.whatsapp:id/title" class="android.widget.TextView" package="com.whatsapp" bounds="48,110,320,180]" clickable="false" />
      <node index="1" text="" resource-id="com.whatsapp:id/menuitem_search" class="android.widget.ImageView" package="com.whatsapp" content-desc="Search" bounds="[840,96][960,216]" clickable="true" />
    </node>
    <node index="1" text="" resource-id="com.whatsapp:id/tabs" class="android.widget.LinearLayout" package="com.whatsapp" bounds="[0,240][1080,360]">
      <node index="0" text="Chats" resource-id="" class="android.widget.TextView" package="com.whatsapp" bounds="[30,260][250,340]" clickable="true" />
      <node index="1" text="Updates" resource-id="" class="android.widget.TextView" package="com.whatsapp" bounds="[290,260][510,340]" clickable="true" />
      <node index="2" text="Calls" resource-id="" class="android.widget.TextView" package="com.whatsapp" bounds="[550,260][770,340]" clickable="true" />
    </node>
    <node index="2" text="" resource-id="android:id/list" class="android.widget.ListView" package="com.whatsapp" bounds="[0,360][1080,2200]" scrollable="true">
      <node index="0" text="" resource-id="com.whatsapp:id/conversations_row" class="android.widget.RelativeLayout" package="com.whatsapp" bounds="[0,360][1080,560]" clickable="true">
        <node index="0" text="Mom" resource-id="com.whatsapp:id/conversations_row_contact_name" class="android.widget.TextView" package="com.whatsapp" bounds="[180,390][500,450]" />
        <node index="1" text="Call me when you are free!" resource-id="com.whatsapp:id/conversations_row_message_snippet" class="android.widget.TextView" package="com.whatsapp" bounds="[180,460][800,520]" />
      </node>
      <node index="1" text="" resource-id="com.whatsapp:id/conversations_row" class="android.widget.RelativeLayout" package="com.whatsapp" bounds="[0,560][1080,760]" clickable="true">
        <node index="0" text="John" resource-id="com.whatsapp:id/conversations_row_contact_name" class="android.widget.TextView" package="com.whatsapp" bounds="[180,590][400,650]" />
        <node index="1" text="Pune Metro timings check" resource-id="com.whatsapp:id/conversations_row_message_snippet" class="android.widget.TextView" package="com.whatsapp" bounds="[180,660][800,720]" />
      </node>
    </node>
  </node>
</hierarchy>
"""


def test_parse_xml_hierarchy():
    parser = UIHierarchyParser()
    root_nodes = parser.parse_xml(SAMPLE_XML_HIERARCHY)
    assert len(root_nodes) == 1
    
    all_nodes = parser.flatten_nodes(root_nodes)
    assert len(all_nodes) > 5

    # Check bounds parsing and centroid
    search_node = next((n for n in all_nodes if n.content_desc == "Search"), None)
    assert search_node is not None
    assert search_node.bounds == (840, 96, 960, 216)
    assert search_node.centroid == (900, 156)


def test_extract_visible_texts():
    parser = UIHierarchyParser()
    root_nodes = parser.parse_xml(SAMPLE_XML_HIERARCHY)
    visible_texts = parser.extract_visible_text(root_nodes)
    
    assert "WhatsApp" in visible_texts
    assert "Chats" in visible_texts
    assert "Mom" in visible_texts
    assert "Call me when you are free!" in visible_texts
    assert "John" in visible_texts


def test_element_selector_priority():
    parser = UIHierarchyParser()
    nodes = parser.flatten_nodes(parser.parse_xml(SAMPLE_XML_HIERARCHY))
    selector = ElementSelector()

    # Priority 2: Resource ID
    match_resid = selector.find_by_resource_id(nodes, "com.whatsapp:id/menuitem_search")
    assert match_resid is not None
    assert match_resid.content_desc == "Search"

    # Priority 3: Visible text exact & substring
    match_text = selector.find_by_text(nodes, "Mom")
    assert match_text is not None
    assert match_text.text == "Mom"

    match_snippet = selector.find_by_text(nodes, "Pune Metro")
    assert match_snippet is not None
    assert match_snippet.text == "Pune Metro timings check"

    # Content-desc search
    match_desc = selector.find_by_content_desc(nodes, "search")
    assert match_desc is not None
    assert match_desc.bounds == (840, 96, 960, 216)
