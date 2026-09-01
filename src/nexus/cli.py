"""Main CLI entrypoint for NEXUS agent."""

import asyncio
import sys
import click
from rich.console import Console
from nexus.agent.core import NexusAgent
from nexus.android.actions.adb_dev import ADBBridge
from nexus.android.actions.executor import ActionExecutor
from nexus.android.screen.observer import ScreenObserver
from nexus.config import get_config
from nexus.models import get_model_provider
from nexus.speech.stt import LocalSTTEngine
from nexus.speech.ptt import PushToTalkController
from nexus.ui.hud import NexusHUD

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="nexus")
def main():
    """⚡ NEXUS — iQOO On-Device Phone AI Agent CLI."""
    pass


@main.command()
@click.option("--mode", "-m", default="snapdragon_npu", help="Inference mode: snapdragon_npu, onnx, openjarvis, remote_fallback")
@click.option("--simulation", "-s", is_flag=True, default=False, help="Run in simulation mode without physical device")
@click.option("--voice", "-v", is_flag=True, default=False, help="Enable Push-to-Talk microphone input")
def run(mode: str, simulation: bool, voice: bool):
    """Start interactive NEXUS session."""
    asyncio.run(_run_interactive(mode, simulation, voice))


async def _run_interactive(mode: str, simulation: bool, voice: bool):
    hud = NexusHUD()
    provider = get_model_provider(mode)
    hud.print_banner(model_badge=provider.badge)

    executor = ActionExecutor(simulation=simulation)
    screen_obs = ScreenObserver()
    agent = NexusAgent(model_provider=provider, executor=executor, screen_observer=screen_obs, simulation=simulation)
    stt = LocalSTTEngine()
    ptt = PushToTalkController(simulation=simulation)

    console.print("\n[bold green]NEXUS is ready.[/bold green] Type a command or 'exit' to quit.\n")

    while True:
        try:
            if voice:
                console.print("[bold yellow]Press Enter to start speaking (Push-to-Talk)...[/bold yellow]")
                input()
                hud.print_step("HEAR", "Listening for voice input...")
                audio = ptt.record_phrase(duration_sec=3.0)
                command = stt.transcribe(audio)
                hud.print_step("HEAR", f'User spoke: "{command}"')
            else:
                command = console.input("[bold cyan]nexus>[/bold cyan] ").strip()

            if not command:
                continue
            if command.lower() in ("exit", "quit", "q"):
                console.print("[dim]Exiting NEXUS. Goodbye![/dim]")
                break

            hud.print_step("HEAR", f'Processing command: "{command}"')
            
            # Observe pre-screen
            pre_obs = screen_obs.observe()
            hud.print_step("OBSERVE", f"Current Screen: {pre_obs.app} ({len(pre_obs.elements)} elements)")

            # Plan
            hud.print_step("PLAN", "Planning structured action via local model...")
            plan = await agent.plan(command, pre_obs)
            hud.print_step("PLAN", f"Action: {plan.action} | Thought: {plan.thought}")

            # Act
            hud.print_step("ACTION", f"Executing {plan.action} via Accessibility / Input Layer...")
            res = await agent.run_step(command)

            # Verify
            hud.print_step("VERIFY", f"State verification: {'PASSED' if res.verification_passed else 'FAILED'}")

            # Respond
            hud.print_step("RESPOND", f"{res.response}")
            hud.print_step("DONE", "Turn completed successfully\n", status="SUCCESS")

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Session closed.[/dim]")
            break
        except Exception as e:
            console.print(f"[bold red]Error during turn: {e}[/bold red]")


@main.command()
@click.option("--simulation/--live", default=True, help="Run simulation or live ADB execution")
def demo(simulation: bool):
    """Run automated 6-step NEXUS demo suite."""
    from scripts.run_demo import run_all_demos
    asyncio.run(run_all_demos(simulation=simulation))


@main.command()
def devices():
    """List connected Android/iQOO devices via ADB."""
    bridge = ADBBridge()
    devs = bridge.list_devices()
    if devs:
        console.print(f"[bold green]Connected Devices ({len(devs)}):[/bold green]")
        for d in devs:
            console.print(f"  • [cyan]{d}[/cyan]")
    else:
        console.print("[yellow]No ADB devices detected. Connect phone via USB with USB Debugging enabled.[/yellow]")


@main.command()
def screen():
    """Inspect current phone screen and print compact observation JSON."""
    obs = ScreenObserver()
    state = obs.observe()
    console.print_json(state.to_json())


if __name__ == "__main__":
    main()

@main.command()
@click.option("--port", "-p", default=8088, help="Port to serve web simulator on")
def web(port: int):
    """Launch interactive browser-based simulator for video presentations."""
    from scripts.start_web_demo import start_server
    start_server()
