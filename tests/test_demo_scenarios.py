"""Integration tests for all 6 target NEXUS demo scenarios."""

import pytest
from unittest.mock import MagicMock
from nexus.agent.core import NexusAgent
from nexus.android.actions.executor import ActionExecutor
from nexus.android.screen.observer import ScreenObserver
from nexus.models.snapdragon.provider import SnapdragonNPUProvider
from tests.test_accessibility_parser import SAMPLE_XML_HIERARCHY


@pytest.fixture
def agent():
    mock_driver = MagicMock()
    mock_driver.dump_hierarchy.return_value = SAMPLE_XML_HIERARCHY
    mock_driver.get_foreground_app.return_value = "com.whatsapp"
    mock_driver.capture_screenshot.return_value = b"FAKE_PNG"

    model = SnapdragonNPUProvider()
    executor = ActionExecutor(driver=mock_driver, simulation=False)
    screen_obs = ScreenObserver(driver=mock_driver)
    return NexusAgent(model_provider=model, executor=executor, screen_observer=screen_obs)


@pytest.mark.asyncio
async def test_demo_1_open_whatsapp(agent):
    res = await agent.run_step("Open WhatsApp")
    assert res.success is True
    assert res.action == "OPEN_APP"
    assert res.target_package == "com.whatsapp"


@pytest.mark.asyncio
async def test_demo_2_open_gmail(agent):
    res = await agent.run_step("Open Gmail and show me my latest emails")
    assert res.success is True
    assert res.action == "OPEN_APP"
    assert res.target_package == "com.google.android.gm"


@pytest.mark.asyncio
async def test_demo_3_open_chrome(agent):
    res = await agent.run_step("Open Chrome and search for Pune Metro")
    assert res.success is True
    assert res.action == "OPEN_APP"
    assert res.target_package == "com.android.chrome"


@pytest.mark.asyncio
async def test_demo_4_what_is_on_my_screen(agent):
    res = await agent.run_step("What is currently on my screen?")
    assert res.success is True
    assert res.action in ("READ_VISIBLE_TEXT", "DESCRIBE_SCREEN")
    assert "Mom" in str(res.screen_summary.get("visible_text", []))


@pytest.mark.asyncio
async def test_demo_5_go_back(agent):
    res = await agent.run_step("Go back")
    assert res.success is True
    assert res.action == "BACK"


@pytest.mark.asyncio
async def test_demo_6_take_screenshot(agent):
    res = await agent.run_step("Take a screenshot")
    assert res.success is True
    assert res.action == "TAKE_SCREENSHOT"
