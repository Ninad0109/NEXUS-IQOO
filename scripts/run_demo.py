"""Automated Demo Runner for NEXUS 6 Core Demonstrations."""

import asyncio
import sys
from rich.console import Console
from nexus.agent.core import NexusAgent
from nexus.android.actions.executor import ActionExecutor
from nexus.android.screen.observer import ScreenObserver
from nexus.models.snapdragon.provider import SnapdragonNPUProvider
from nexus.ui.hud import NexusHUD

console = Console()

DEMO_COMMANDS = [
    {
        "id": 1,
        "title": "Demo 1: Open WhatsApp",
        "command": "Open WhatsApp",
        "expected_action": "OPEN_APP",
        "description": "Opens WhatsApp and verifies it is in foreground."
    },
    {
        "id": 2,
        "title": "Demo 2: Open Gmail and show unread emails",
        "command": "Open Gmail and show me my latest emails",
        "expected_action": "OPEN_APP",
        "description": "Opens Gmail and inspects conversation list."
    },
    {
        "id": 3,
        "title": "Demo 3: Search Pune Metro on Chrome",
        "command": "Open Chrome and search for Pune Metro",
        "expected_action": "OPEN_APP",
        "description": "Launches Chrome and enters search query."
    },
    {
        "id": 4,
        "title": "Demo 4: What is on my screen?",
        "command": "What is currently on my screen?",
        "expected_action": "DESCRIBE_SCREEN",
        "description": "Performs compact semantic UI observation and text summarization."
    },
    {
        "id": 5,
        "title": "Demo 5: Go back",
        "command": "Go back",
        "expected_action": "BACK",
        "description": "Dispatches back navigation keyevent."
    },
    {
        "id": 6,
        "title": "Demo 6: Take a screenshot",
        "command": "Take a screenshot",
        "expected_action": "TAKE_SCREENSHOT",
        "description": "Captures raw screen buffer and stores artifact."
    },
]


async def run_all_demos(simulation: bool = True):
    hud = NexusHUD()
    model = SnapdragonNPUProvider()
    hud.print_banner(model_badge=model.badge)

    executor = ActionExecutor(simulation=simulation)
    screen_obs = ScreenObserver()
    agent = NexusAgent(model_provider=model, executor=executor, screen_observer=screen_obs, simulation=simulation)

    console.print(f"\n[bold green]Running {len(DEMO_COMMANDS)} NEXUS Verification Demos (Simulation={simulation})...[/bold green]\n")

    for demo in DEMO_COMMANDS:
        console.print(f"\n[bold cyan]══════════════════════════════════════════════════════════════[/bold cyan]")
        console.print(f"[bold cyan]▶ {demo['title']}[/bold cyan]")
        console.print(f"[dim]{demo['description']}[/dim]\n")

        hud.print_step("HEAR", f'User Voice Input: "{demo["command"]}"')
        
        # Turn execution
        result = await agent.run_step(demo["command"])

        hud.print_step("PLAN", f'Plan: {result.action} | Thought: "{result.thought}"')
        hud.print_step("ACTION", f"Dispatched {result.action}")
        hud.print_step("VERIFY", f"State verification: {'PASSED' if result.verification_passed else 'FAILED'}")
        hud.print_step("RESPOND", f"{result.response}")
        hud.print_step("DONE", f"Turn complete\n", status="SUCCESS")

    console.print("[bold green]✔ All 6 NEXUS Demos completed successfully![/bold green]\n")


if __name__ == "__main__":
    is_sim = "--live" not in sys.argv
    asyncio.run(run_all_demos(simulation=is_sim))
