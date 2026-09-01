"""HUD state tracker for agent pipeline visualization."""

from dataclasses import dataclass, field
import time
from typing import Optional


@dataclass
class HUDStep:
    stage: str  # "HEAR", "OBSERVE", "PLAN", "SAFETY", "ACTION", "VERIFY", "RESPOND", "DONE"
    detail: str
    timestamp: float = field(default_factory=time.time)
    status: str = "INFO"  # "INFO", "SUCCESS", "WARNING", "ERROR"


class HUDStateTracker:
    """Tracks active pipeline steps for live UI rendering."""

    def __init__(self):
        self.steps: list[HUDStep] = []
        self.active_command: str = ""
        self.active_model_badge: str = "[LOCAL AI]"

    def add_step(self, stage: str, detail: str, status: str = "INFO") -> None:
        self.steps.append(HUDStep(stage=stage, detail=detail, status=status))

    def reset(self, new_command: str = "", badge: str = "[LOCAL AI]") -> None:
        self.steps.clear()
        self.active_command = new_command
        self.active_model_badge = badge
