"""Futuristic Terminal HUD interface for NEXUS."""

import sys
import time
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from nexus.ui.state import HUDStateTracker

console = Console()


class NexusHUD:
    """Renders the NEXUS futuristic HUD terminal interface."""

    def __init__(self):
        self.tracker = HUDStateTracker()

    def print_banner(self, model_badge: str = "[LOCAL AI: Snapdragon NPU]") -> None:
        """Displays the main futuristic NEXUS header."""
        header_text = Text()
        header_text.append("⚡ NEXUS — iQOO On-Device AI Agent ⚡\n", style="bold cyan")
        header_text.append("Architecture: ", style="dim")
        header_text.append("HEAR → OBSERVE → PLAN → ACT → VERIFY → RESPOND\n", style="bold green")
        header_text.append("Active Engine: ", style="dim")
        
        if "LOCAL" in model_badge.upper():
            header_text.append(f"{model_badge}\n", style="bold black on green")
        else:
            header_text.append(f"{model_badge}\n", style="bold black on yellow")

        header_text.append("Hardware Target: iQOO / Snapdragon (Qualcomm Hexagon NPU)", style="dim italic")

        panel = Panel(
            header_text,
            box=box.DOUBLE,
            border_style="cyan",
            expand=False,
            padding=(1, 2)
        )
        console.print(panel)

    def print_step(self, stage: str, detail: str, status: str = "INFO") -> None:
        """Prints a styled pipeline step."""
        stage_colors = {
            "HEAR": "bold magenta",
            "OBSERVE": "bold blue",
            "PLAN": "bold cyan",
            "SAFETY": "bold yellow",
            "ACTION": "bold green",
            "VERIFY": "bold dark_orange",
            "RESPOND": "bold spring_green3",
            "DONE": "bold white on green",
            "ERROR": "bold white on red",
        }
        
        color = stage_colors.get(stage.upper(), "bold white")
        tag = f"[{stage.upper()}]"
        
        console.print(f"[{color}]{tag:<10}[/{color}] {detail}")

    def render_turn_summary(self, command: str, action: str, response: str, badge: str) -> None:
        """Renders summary box for completed turn."""
        table = Table(show_header=False, box=box.ROUNDED, border_style="green", expand=False)
        table.add_column("Key", style="bold cyan")
        table.add_column("Value", style="white")

        table.add_row("Command", f'"{command}"')
        table.add_row("Action", action)
        table.add_row("Response", response)
        table.add_row("Inference", badge)

        console.print(table)
