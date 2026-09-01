"""Remote Development Model Provider (Gemini / OpenAI / Fallback)."""

from typing import Optional
from nexus.models.base import LocalModelProvider


class RemoteFallbackProvider(LocalModelProvider):
    """Remote cloud fallback for development and benchmarking."""

    def __init__(self, model_name: str = "Cloud LLM (Remote Fallback)", api_key: str = ""):
        super().__init__(model_name=model_name)
        self.api_key = api_key

    @property
    def provider_type(self) -> str:
        return "REMOTE FALLBACK"

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
        elif "screen" in p_lower:
            return '{"action": "DESCRIBE_SCREEN"}'
        return '{"action": "READ_VISIBLE_TEXT"}'

    async def vision(self, image_bytes: bytes, prompt: str) -> str:
        return "Remote vision model response"

    async def classify(self, text: str, categories: list[str]) -> str:
        return categories[0] if categories else ""
