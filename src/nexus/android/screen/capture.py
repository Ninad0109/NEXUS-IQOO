"""Screen capture manager for Android runtime."""

from typing import Any, Optional
from nexus.android.actions.adb_dev import ADBBridge


class ScreenCaptureManager:
    """Manages fast on-device frame and buffer capture."""

    def __init__(self, driver: Optional[Any] = None):
        self.driver = driver if driver is not None else ADBBridge()

    def capture_frame(self) -> bytes:
        """Captures raw image bytes of active screen."""
        if hasattr(self.driver, "capture_screenshot"):
            return self.driver.capture_screenshot()
        return b""
