"""Development ADB Bridge driver for iQOO/Android physical devices and emulators."""

import logging
import os
import re
import subprocess
from typing import Optional

logger = logging.getLogger("nexus.android.adb")


class ADBBridge:
    """Fast subprocess-based ADB bridge."""

    def __init__(self, device_id: Optional[str] = None, adb_path: str = "adb"):
        self.device_id = device_id
        self.adb_path = adb_path
        self._auto_detect_device()

    def _auto_detect_device(self) -> None:
        """Auto-detect connected Android/iQOO device if not explicitly set."""
        if self.device_id:
            return
        
        devices = self.list_devices()
        if devices:
            self.device_id = devices[0]
            logger.info(f"Auto-selected ADB device: {self.device_id}")

    def list_devices(self) -> list[str]:
        """Returns list of connected device serials."""
        try:
            res = subprocess.run([self.adb_path, "devices"], capture_output=True, text=True, timeout=5)
            lines = res.stdout.strip().splitlines()
            devices = []
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])
            return devices
        except Exception as e:
            logger.debug(f"ADB device detection failed: {e}")
            return []

    def _base_cmd(self) -> list[str]:
        cmd = [self.adb_path]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        return cmd

    def shell(self, command: str, timeout: float = 10.0) -> str:
        """Runs an ADB shell command."""
        cmd = self._base_cmd() + ["shell", command]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return res.stdout
        except Exception as e:
            logger.error(f"ADB shell command '{command}' failed: {e}")
            return ""

    def dump_hierarchy(self) -> str:
        """Dumps UIAutomator hierarchy XML directly to stdout string."""
        # 1. Try direct dump to memory / file on device
        self.shell("uiautomator dump /data/local/tmp/uidump.xml")
        xml_content = self.shell("cat /data/local/tmp/uidump.xml")
        if xml_content and "<hierarchy" in xml_content:
            return xml_content
        return ""

    def get_foreground_app(self) -> str:
        """Determines the current foreground package name."""
        output = self.shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
        # Matches formats like 'com.whatsapp/com.whatsapp.HomeActivity'
        match = re.search(r"([a-zA-Z0-9_\.]+)/([a-zA-Z0-9_\.]+)", output)
        if match:
            return match.group(1)
        
        # Fallback dumpsys activity
        alt_output = self.shell("dumpsys activity top | grep 'ACTIVITY'")
        match = re.search(r"ACTIVITY ([a-zA-Z0-9_\.]+)/", alt_output)
        if match:
            return match.group(1)
        
        return "unknown"

    def tap(self, x: int, y: int) -> bool:
        """Dispatches touch tap event at (x, y)."""
        res = self.shell(f"input tap {x} {y}")
        return True

    def type_text(self, text: str) -> bool:
        """Types text escaping special shell characters."""
        # Replace spaces with %s for adb input text
        escaped = text.replace(" ", "%s").replace("&", "\&").replace("<", "\<").replace(">", "\>")
        self.shell(f"input text '{escaped}'")
        return True

    def keyevent(self, code: int) -> bool:
        """Dispatches an Android keyevent code (3=HOME, 4=BACK, 66=ENTER, etc.)."""
        self.shell(f"input keyevent {code}")
        return True

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> bool:
        """Dispatches touch swipe event."""
        self.shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")
        return True

    def capture_screenshot(self) -> bytes:
        """Captures a PNG screenshot as raw bytes."""
        cmd = self._base_cmd() + ["exec-out", "screencap", "-p"]
        try:
            res = subprocess.run(cmd, capture_output=True, timeout=10)
            return res.stdout
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return b""
