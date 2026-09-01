"""Tests for AgentBackend and NexusAgent execution loop."""

import pytest
from nexus.android.screen.observer import CompactScreenState, CompactScreenElement
from nexus.android.actions.executor import ActionExecutor
from nexus.models.snapdragon.provider import SnapdragonNPUProvider
from nexus.agent.core import NexusAgent


@pytest.mark.asyncio
async def test_agent_open_whatsapp_loop():
    model = SnapdragonNPUProvider()
    executor = ActionExecutor(simulation=True)
    agent = NexusAgent(model_provider=model, executor=executor, simulation=True)

    # Initial state: Home screen
    agent.screen_observer.driver.get_foreground_app = lambda: "com.android.launcher"
    
    result = await agent.run_step("Open WhatsApp")

    assert result.success is True
    assert result.action == "OPEN_APP"
    assert result.target_package == "com.whatsapp"
    assert "Done" in result.response or "Opened WhatsApp" in result.response
