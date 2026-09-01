"""Core NEXUS Agent Orchestrator: HEAR -> OBSERVE -> PLAN -> ACT -> VERIFY -> RESPOND."""

from dataclasses import dataclass
import logging
from typing import Any, Optional
from nexus.agent.interface.backend import AgentBackend, ActionPlan
from nexus.agent.planner.planner import ActionPlanner
from nexus.agent.memory.context_memory import ContextMemory
from nexus.agent.tools.safety import SafetyGate
from nexus.android.actions.executor import ActionExecutor, ActionResult
from nexus.android.screen.observer import ScreenObserver, CompactScreenState
from nexus.android.verification.verifier import VerificationEngine, VerificationResult
from nexus.models.base import LocalModelProvider

logger = logging.getLogger("nexus.agent.core")


@dataclass
class AgentLoopResult:
    """Comprehensive result of an end-to-end agent execution turn."""
    success: bool
    command: str
    action: str
    thought: str
    target_package: str = ""
    verification_passed: bool = True
    response: str = ""
    screen_summary: Optional[dict[str, Any]] = None


class NexusAgent(AgentBackend):
    """Main phone-native AI agent orchestrating the full execution loop."""

    def __init__(
        self,
        model_provider: LocalModelProvider,
        executor: Optional[ActionExecutor] = None,
        screen_observer: Optional[ScreenObserver] = None,
        safety_gate: Optional[SafetyGate] = None,
        simulation: bool = False,
    ):
        self.model_provider = model_provider
        self.simulation = simulation
        self.executor = executor if executor is not None else ActionExecutor(simulation=simulation)
        self.screen_observer = screen_observer if screen_observer is not None else ScreenObserver()
        self.safety_gate = safety_gate if safety_gate is not None else SafetyGate()
        self.verifier = VerificationEngine()
        self.planner = ActionPlanner(model_provider=model_provider)
        self.memory = ContextMemory()

    async def remember(self, key: str, value: Any) -> None:
        self.memory.remember(key, value)

    async def retrieve(self, query: str) -> list[Any]:
        return self.memory.retrieve(query)

    async def plan(self, command: str, observation: CompactScreenState) -> ActionPlan:
        return await self.planner.plan(command, observation)

    async def execute(self, tool_name: str, params: dict[str, Any]) -> ActionResult:
        tool_upper = tool_name.upper()
        if tool_upper == "OPEN_APP":
            pkg = params.get("package", params.get("app_name", ""))
            return self.executor.open_app(pkg)
        elif tool_upper == "BACK":
            return self.executor.back()
        elif tool_upper == "HOME":
            return self.executor.home()
        elif tool_upper == "TAP_TEXT":
            return self.executor.tap_text(params.get("text", ""))
        elif tool_upper == "TAP_NODE":
            return self.executor.tap_node(params.get("node_id", ""))
        elif tool_upper == "TYPE_TEXT":
            return self.executor.type_text(params.get("text", ""))
        elif tool_upper == "SWIPE":
            return self.executor.swipe(params.get("direction", "UP"))
        elif tool_upper == "TAKE_SCREENSHOT":
            return self.executor.take_screenshot()
        elif tool_upper in ("READ_VISIBLE_TEXT", "DESCRIBE_SCREEN"):
            return ActionResult(success=True, action=tool_upper, message="Screen observed")
        
        return ActionResult(success=False, action=tool_upper, message=f"Unknown action {tool_name}")

    async def run_step(self, user_command: str) -> AgentLoopResult:
        """Executes a single end-to-end HEAR -> OBSERVE -> PLAN -> ACT -> VERIFY -> RESPOND turn."""
        logger.info(f"NEXUS Turn: Command='{user_command}'")

        # 1. OBSERVE (Pre-action screen)
        pre_observation = self.screen_observer.observe()
        await self.remember("last_command", user_command)
        await self.remember("pre_observation", pre_observation.to_dict())

        # 2. PLAN
        plan = await self.plan(user_command, pre_observation)
        logger.info(f"NEXUS Plan: Action={plan.action}, Thought='{plan.thought}'")

        # 3. SAFETY GATE
        safety_check = self.safety_gate.check(plan.action, plan.params)
        if not safety_check.allowed:
            return AgentLoopResult(
                success=False,
                command=user_command,
                action=plan.action,
                thought=plan.thought,
                verification_passed=False,
                response=f"Safety Guardrail: {safety_check.reason}",
                screen_summary=pre_observation.to_dict()
            )

        # 4. ACT
        action_result = await self.execute(plan.action, plan.params)

        # Execute sub-action if specified (e.g. typing query after opening browser)
        if plan.sub_action:
            sub_name = plan.sub_action.get("action", "")
            sub_params = {k: v for k, v in plan.sub_action.items() if k != "action"}
            await self.execute(sub_name, sub_params)

        # 5. OBSERVE (Post-action screen)
        if self.simulation and plan.action == "OPEN_APP":
            # In simulation, reflect target package in observation
            post_observation = CompactScreenState(
                app=plan.params.get("app_name", "TargetApp"),
                package=plan.params.get("package", "com.target.app"),
                screen="Main",
                elements=pre_observation.elements,
                visible_text=pre_observation.visible_text
            )
        else:
            post_observation = self.screen_observer.observe()

        # 6. VERIFY
        verification = self.verifier.verify_action(
            action=plan.action,
            params=plan.params,
            pre_state=pre_observation,
            post_state=post_observation
        )

        # 7. RESPOND
        response_text = "Done"
        if plan.action == "OPEN_APP":
            app_name = plan.params.get("app_name", "App")
            response_text = f"Done — Opened {app_name}"
        elif plan.action == "DESCRIBE_SCREEN":
            visible_sample = ", ".join(post_observation.visible_text[:6])
            response_text = f"On screen ({post_observation.app}): {visible_sample}"
        elif plan.action == "READ_VISIBLE_TEXT":
            visible_sample = ", ".join(post_observation.visible_text[:6])
            response_text = f"Visible content: {visible_sample}"
        elif plan.action == "TAKE_SCREENSHOT":
            response_text = "Done — Screenshot captured"
        elif plan.action in ("BACK", "HOME"):
            response_text = f"Done — Navigated {plan.action.lower()}"

        return AgentLoopResult(
            success=action_result.success and verification.success,
            command=user_command,
            action=plan.action,
            thought=plan.thought,
            target_package=plan.target_package or plan.params.get("package", ""),
            verification_passed=verification.success,
            response=response_text,
            screen_summary=post_observation.to_dict()
        )
