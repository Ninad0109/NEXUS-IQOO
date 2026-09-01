"""Integration test for NEXUS Milestone 1: Working Vertical Slice.
Voice/Text -> STT -> AgentBackend -> OPEN_APP -> AccessibilityService -> Verify Foreground -> "Done"
"""

import pytest
from unittest.mock import MagicMock
from nexus.agent.core import NexusAgent
from nexus.android.actions.executor import ActionExecutor
from nexus.android.screen.observer import ScreenObserver
from nexus.models.openjarvis.adapter import OpenJarvisModelProvider
from nexus.speech.stt import LocalSTTEngine


@pytest.mark.asyncio
async def test_vertical_slice_open_whatsapp():
    # 1. Voice / STT Input
    stt = LocalSTTEngine(engine_type="mock")
    user_voice = stt.transcribe("Open WhatsApp")
    assert user_voice == "Open WhatsApp"

    # 2. Setup mock driver for Android Accessibility / ADB
    mock_driver = MagicMock()
    mock_driver.dump_hierarchy.return_value = """<?xml version='1.0' encoding='UTF-8' ?>
    <hierarchy rotation="0">
      <node index="0" text="" class="android.widget.FrameLayout" package="com.whatsapp" bounds="[0,0][1080,2400]">
        <node index="0" text="WhatsApp" class="android.widget.TextView" package="com.whatsapp" bounds="[48,110][320,180]" />
        <node index="1" text="Chats" class="android.widget.TextView" package="com.whatsapp" bounds="[30,260][250,340]" />
      </node>
    </hierarchy>"""
    mock_driver.get_foreground_app.return_value = "com.whatsapp"

    # 3. Agent Execution with OpenJarvis Model Provider
    model = OpenJarvisModelProvider()
    executor = ActionExecutor(driver=mock_driver, simulation=False)
    screen_obs = ScreenObserver(driver=mock_driver)
    agent = NexusAgent(model_provider=model, executor=executor, screen_observer=screen_obs)

    # 4. Run Step
    result = await agent.run_step(user_voice)

    # 5. Verify assertions
    assert result.success is True
    assert result.action == "OPEN_APP"
    assert result.target_package == "com.whatsapp"
    assert result.verification_passed is True
    assert "Done — Opened WhatsApp" in result.response
