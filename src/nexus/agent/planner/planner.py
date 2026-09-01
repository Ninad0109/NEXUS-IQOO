"""Action planner for NEXUS agent."""

import json
import logging
import re
from typing import Any, Optional
from nexus.android.screen.observer import CompactScreenState
from nexus.agent.interface.backend import ActionPlan
from nexus.models.base import LocalModelProvider

logger = logging.getLogger("nexus.agent.planner")

PLANNER_SYSTEM_PROMPT = """You are NEXUS, an on-device AI agent running on an iQOO Snapdragon phone.
Your job is to read the user command and the compact structured screen observation, then output a single JSON action object.

Supported actions:
- OPEN_APP: {"action": "OPEN_APP", "package": "<package_name>", "app_name": "<app_name>"}
- BACK: {"action": "BACK"}
- HOME: {"action": "HOME"}
- TAP_TEXT: {"action": "TAP_TEXT", "text": "<visible_text_to_tap>"}
- TAP_NODE: {"action": "TAP_NODE", "node_id": "<node_id_or_resource_id>"}
- TYPE_TEXT: {"action": "TYPE_TEXT", "text": "<text_to_type>"}
- SWIPE: {"action": "SWIPE", "direction": "UP|DOWN|LEFT|RIGHT"}
- READ_VISIBLE_TEXT: {"action": "READ_VISIBLE_TEXT"}
- TAKE_SCREENSHOT: {"action": "TAKE_SCREENSHOT"}
- DESCRIBE_SCREEN: {"action": "DESCRIBE_SCREEN"}
- STOP: {"action": "STOP"}

Output ONLY valid JSON. Example:
{
  "thought": "Opening WhatsApp to check unread messages",
  "action": "OPEN_APP",
  "package": "com.whatsapp",
  "app_name": "WhatsApp"
}
"""


class ActionPlanner:
    """Uses LocalModelProvider to generate structured action plans."""

    def __init__(self, model_provider: LocalModelProvider):
        self.model_provider = model_provider

    async def plan(self, command: str, observation: CompactScreenState) -> ActionPlan:
        """Plans next step from user command and screen observation."""
        screen_context = observation.to_json()
        prompt = f"User Command: \"{command}\"\n\nCurrent Screen Observation:\n{screen_context}\n\nWhat action should be executed?"

        raw_response = await self.model_provider.generate(
            prompt=prompt,
            system_prompt=PLANNER_SYSTEM_PROMPT
        )

        return self._parse_response(raw_response, command)

    def _parse_response(self, raw_response: str, fallback_command: str) -> ActionPlan:
        """Parses LLM text response into structured ActionPlan."""
        try:
            # Extract JSON from code fences or raw string
            json_str = raw_response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            # Find outer curly braces
            match = re.search(r"\{.*\}", json_str, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                action = data.get("action", "READ_VISIBLE_TEXT").upper()
                thought = data.get("thought", "")
                params = {k: v for k, v in data.items() if k not in ("action", "thought", "sub_action", "expected_result")}
                
                return ActionPlan(
                    action=action,
                    thought=thought,
                    params=params,
                    target_package=data.get("package", ""),
                    expected_result=data.get("expected_result", ""),
                    sub_action=data.get("sub_action")
                )
        except Exception as e:
            logger.warning(f"Failed to parse model plan '{raw_response}': {e}")

        # Rule-based fallback parsing
        cmd_lower = fallback_command.lower()
        if "open whatsapp" in cmd_lower:
            return ActionPlan(action="OPEN_APP", params={"package": "com.whatsapp", "app_name": "WhatsApp"}, target_package="com.whatsapp", thought="Opening WhatsApp")
        elif "gmail" in cmd_lower:
            return ActionPlan(action="OPEN_APP", params={"package": "com.google.android.gm", "app_name": "Gmail"}, target_package="com.google.android.gm", thought="Opening Gmail")
        elif "chrome" in cmd_lower:
            return ActionPlan(action="OPEN_APP", params={"package": "com.android.chrome", "app_name": "Chrome"}, target_package="com.android.chrome", thought="Opening Chrome")
        elif "back" in cmd_lower:
            return ActionPlan(action="BACK", thought="Navigating back")
        elif "home" in cmd_lower:
            return ActionPlan(action="HOME", thought="Navigating home")
        elif "screenshot" in cmd_lower:
            return ActionPlan(action="TAKE_SCREENSHOT", thought="Taking screenshot")
        elif "screen" in cmd_lower:
            return ActionPlan(action="DESCRIBE_SCREEN", thought="Describing screen")

        return ActionPlan(action="READ_VISIBLE_TEXT", thought="Reading active screen")
