"""Tests for ActionExecutor and AppLauncher."""

from unittest.mock import MagicMock
from nexus.android.actions.executor import ActionExecutor, ActionResult
from nexus.android.actions.launcher import AppLauncher


def test_app_launcher_resolution():
    launcher = AppLauncher()
    
    assert launcher.resolve_package("WhatsApp") == "com.whatsapp"
    assert launcher.resolve_package("whatsapp") == "com.whatsapp"
    assert launcher.resolve_package("Gmail") == "com.google.android.gm"
    assert launcher.resolve_package("Chrome") == "com.android.chrome"
    assert launcher.resolve_package("Google Chrome") == "com.android.chrome"
    assert launcher.resolve_package("Settings") == "com.android.settings"
    assert launcher.resolve_package("com.custom.app") == "com.custom.app"


def test_action_executor_mock():
    mock_bridge = MagicMock()
    mock_bridge.shell.return_value = "Success"
    
    executor = ActionExecutor(driver=mock_bridge)
    
    # Test OPEN_APP
    res = executor.open_app("WhatsApp")
    assert res.success is True
    assert res.action == "OPEN_APP"
    assert res.target == "com.whatsapp"
    
    # Test BACK
    res = executor.back()
    assert res.success is True
    assert res.action == "BACK"
    mock_bridge.keyevent.assert_called_with(4)
    
    # Test HOME
    res = executor.home()
    assert res.success is True
    assert res.action == "HOME"
    mock_bridge.keyevent.assert_called_with(3)
