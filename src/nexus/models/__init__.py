"""NEXUS Model Provider Abstraction."""

from nexus.models.base import LocalModelProvider
from nexus.models.snapdragon.provider import SnapdragonNPUProvider
from nexus.models.onnx.provider import ONNXModelProvider
from nexus.models.openjarvis.adapter import OpenJarvisModelProvider
from nexus.models.remote.client import RemoteFallbackProvider

__all__ = [
    "LocalModelProvider",
    "SnapdragonNPUProvider",
    "ONNXModelProvider",
    "OpenJarvisModelProvider",
    "RemoteFallbackProvider",
    "get_model_provider",
]


def get_model_provider(mode: str = "openjarvis", model_name: str = "") -> LocalModelProvider:
    """Factory function returning the configured LocalModelProvider."""
    m = mode.lower()
    if m in ("snapdragon", "snapdragon_npu", "qnn", "npu"):
        return SnapdragonNPUProvider(model_name=model_name or "Snapdragon NPU (Hexagon)")
    elif m in ("onnx", "onnx_runtime"):
        return ONNXModelProvider(model_name=model_name or "ONNX Local")
    elif m in ("remote", "remote_fallback", "cloud", "gemini", "openai"):
        return RemoteFallbackProvider(model_name=model_name or "Cloud API Fallback")
    else:
        return OpenJarvisModelProvider(model_name=model_name or "OpenJarvis Local")
