"""Tests for LocalModelProvider abstractions and implementations."""

import pytest
from nexus.models.base import LocalModelProvider
from nexus.models.snapdragon.provider import SnapdragonNPUProvider
from nexus.models.onnx.provider import ONNXModelProvider
from nexus.models.openjarvis.adapter import OpenJarvisModelProvider
from nexus.models.remote.client import RemoteFallbackProvider
from nexus.models import get_model_provider


@pytest.mark.asyncio
async def test_snapdragon_npu_provider():
    provider = SnapdragonNPUProvider()
    assert provider.provider_type == "LOCAL AI"
    assert "LOCAL AI" in provider.badge
    assert "Snapdragon NPU" in provider.badge
    
    response = await provider.generate("Open WhatsApp", system_prompt="Action planner")
    assert response is not None
    assert "OPEN_APP" in response


@pytest.mark.asyncio
async def test_onnx_provider():
    provider = ONNXModelProvider()
    assert provider.provider_type == "LOCAL AI"
    assert "LOCAL AI" in provider.badge
    assert "ONNX" in provider.badge


@pytest.mark.asyncio
async def test_openjarvis_adapter():
    provider = OpenJarvisModelProvider()
    assert provider.provider_type == "LOCAL AI"
    assert "OpenJarvis" in provider.badge


@pytest.mark.asyncio
async def test_remote_fallback_provider():
    provider = RemoteFallbackProvider()
    assert provider.provider_type == "REMOTE FALLBACK"
    assert "REMOTE FALLBACK" in provider.badge


def test_model_factory():
    p1 = get_model_provider("snapdragon_npu")
    assert isinstance(p1, SnapdragonNPUProvider)

    p2 = get_model_provider("remote_fallback")
    assert isinstance(p2, RemoteFallbackProvider)
