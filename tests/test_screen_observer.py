"""Tests for ScreenObserver and compact screen state representation."""

from unittest.mock import MagicMock
from nexus.android.screen.observer import ScreenObserver
from tests.test_accessibility_parser import SAMPLE_XML_HIERARCHY


def test_compact_screen_state():
    mock_driver = MagicMock()
    mock_driver.dump_hierarchy.return_value = SAMPLE_XML_HIERARCHY
    mock_driver.get_foreground_app.return_value = "com.whatsapp"

    observer = ScreenObserver(driver=mock_driver)
    state = observer.observe()

    assert state.app == "WhatsApp"
    assert state.package == "com.whatsapp"
    assert len(state.elements) > 0
    assert "Chats" in state.visible_text
    assert "Mom" in state.visible_text

    compact_dict = state.to_dict()
    assert "app" in compact_dict
    assert "elements" in compact_dict
    assert "visible_text" in compact_dict
