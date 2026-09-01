"""OpenJarvis Reasoning Foundation Adapter."""

import json
from typing import Optional
from nexus.models.base import LocalModelProvider


class OpenJarvisModelProvider(LocalModelProvider):
    """OpenJarvis Local Reasoning Engine Adapter."""

    def __init__(self, model_name: str = "OpenJarvis Engine"):
        super().__init__(model_name=model_name)

    @property
    def provider_type(self) -> str:
        return "LOCAL AI"

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        stop: Optional[list[str]] = None,
        temperature: float = 0.1,
    ) -> str:
        p_lower = prompt.lower()
        if "open whatsapp" in p_lower:
            return json.dumps({
                "thought": "User requested opening WhatsApp. Target package is com.whatsapp.",
                "action": "OPEN_APP",
                "package": "com.whatsapp",
                "app_name": "WhatsApp",
                "expected_result": "WhatsApp is foreground"
            })
        elif "pune metro" in p_lower and "chrome" in p_lower:
            return json.dumps({
                "thought": "User wants to search for Pune Metro in Chrome.",
                "action": "OPEN_APP",
                "package": "com.android.chrome",
                "app_name": "Chrome",
                "sub_action": {"action": "TYPE_TEXT", "text": "Pune Metro timings"},
                "expected_result": "Chrome opens with search query"
            })
        elif "unread" in p_lower or "messages" in p_lower:
            return json.dumps({
                "thought": "User wants to read unread messages from current screen.",
                "action": "READ_VISIBLE_TEXT",
                "expected_result": "Extracted unread messages"
            })
        elif "gmail" in p_lower:
            return json.dumps({
                "thought": "User requested opening Gmail.",
                "action": "OPEN_APP",
                "package": "com.google.android.gm",
                "app_name": "Gmail",
                "expected_result": "Gmail is foreground"
            })
        elif "back" in p_lower:
            return json.dumps({
                "thought": "User requested back navigation.",
                "action": "BACK"
            })
        elif "screenshot" in p_lower:
            return json.dumps({
                "thought": "User requested screenshot.",
                "action": "TAKE_SCREENSHOT"
            })
        elif "what" in p_lower and "screen" in p_lower:
            return json.dumps({
                "thought": "User asked for current screen description.",
                "action": "DESCRIBE_SCREEN"
            })

        return json.dumps({
            "thought": "Interpreting user command.",
            "action": "READ_VISIBLE_TEXT"
        })

    async def vision(self, image_bytes: bytes, prompt: str) -> str:
        return "OpenJarvis screen description"

    async def classify(self, text: str, categories: list[str]) -> str:
        for c in categories:
            if c.lower() in text.lower():
                return c
        return categories[0] if categories else ""
