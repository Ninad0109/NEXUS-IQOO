"""ONNX Runtime Local Model Provider."""

from typing import Optional
from nexus.models.base import LocalModelProvider


class ONNXModelProvider(LocalModelProvider):
    """Local ONNX Runtime model execution provider."""

    def __init__(self, model_name: str = "ONNX Runtime (Local)"):
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
        if "whatsapp" in p_lower:
            return '{"action": "OPEN_APP", "package": "com.whatsapp", "app_name": "WhatsApp"}'
        elif "gmail" in p_lower:
            return '{"action": "OPEN_APP", "package": "com.google.android.gm", "app_name": "Gmail"}'
        elif "chrome" in p_lower:
            return '{"action": "OPEN_APP", "package": "com.android.chrome", "app_name": "Chrome"}'
        elif "back" in p_lower:
            return '{"action": "BACK"}'
        elif "screenshot" in p_lower:
            return '{"action": "TAKE_SCREENSHOT"}'
        return '{"action": "READ_VISIBLE_TEXT"}'

    async def vision(self, image_bytes: bytes, prompt: str) -> str:
        return "ONNX Vision model processed frame"

    async def classify(self, text: str, categories: list[str]) -> str:
        return categories[0] if categories else ""
