"""Abstract base class for NEXUS Local Model Providers."""

from abc import ABC, abstractmethod
from typing import Optional


class LocalModelProvider(ABC):
    """Clean abstraction decoupling on-device NPU/ONNX execution from dev fallbacks."""

    def __init__(self, model_name: str = "nexus-model"):
        self.model_name = model_name

    @property
    @abstractmethod
    def provider_type(self) -> str:
        """Returns 'LOCAL AI' or 'REMOTE FALLBACK'."""
        pass

    @property
    def badge(self) -> str:
        """Formatted UI badge for HUD display."""
        return f"[{self.provider_type}: {self.model_name}]"

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        stop: Optional[list[str]] = None,
        temperature: float = 0.1,
    ) -> str:
        """Generates text / structured plan from prompt."""
        pass

    @abstractmethod
    async def vision(self, image_bytes: bytes, prompt: str) -> str:
        """Screen image understanding fallback."""
        pass

    @abstractmethod
    async def classify(self, text: str, categories: list[str]) -> str:
        """Zero-shot classification for fast intent routing."""
        pass
