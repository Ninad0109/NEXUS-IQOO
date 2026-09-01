"""Safety confirmation gates for sensitive and high-risk phone operations."""

from dataclasses import dataclass
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger("nexus.agent.safety")


@dataclass
class SafetyCheckResult:
    """Result of a safety gate evaluation."""
    allowed: bool
    requires_confirmation: bool
    action: str
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    reason: str = ""


class SafetyGate:
    """Enforces safety guardrails before executing phone actions."""

    # Actions that ALWAYS require explicit user confirmation
    CONFIRMATION_REQUIRED_ACTIONS = {
        "SEND_MESSAGE": ("CRITICAL", "Sending external message to a contact"),
        "PAYMENT": ("CRITICAL", "Financial payment or transaction"),
        "PURCHASE": ("CRITICAL", "In-app or online purchase"),
        "DELETE": ("HIGH", "Deleting content, email, or chat"),
        "INSTALL_APP": ("HIGH", "Installing third-party application"),
        "CHANGE_SETTINGS": ("MEDIUM", "Modifying critical device settings"),
    }

    def __init__(
        self,
        enabled: bool = True,
        interactive: bool = True,
        confirmation_callback: Optional[Callable[[str, dict[str, Any]], bool]] = None
    ):
        self.enabled = enabled
        self.interactive = interactive
        self.confirmation_callback = confirmation_callback

    def check(self, action: str, params: Optional[dict[str, Any]] = None) -> SafetyCheckResult:
        """Evaluates whether an action is safe to execute automatically or requires confirmation."""
        if not self.enabled:
            return SafetyCheckResult(allowed=True, requires_confirmation=False, action=action, risk_level="LOW")

        action_upper = action.upper()
        params = params or {}

        if action_upper in self.CONFIRMATION_REQUIRED_ACTIONS:
            risk_level, reason = self.CONFIRMATION_REQUIRED_ACTIONS[action_upper]
            
            # If an interactive callback is provided, invoke it
            if self.confirmation_callback:
                confirmed = self.confirmation_callback(action_upper, params)
                return SafetyCheckResult(
                    allowed=confirmed,
                    requires_confirmation=True,
                    action=action_upper,
                    risk_level=risk_level,
                    reason=reason if not confirmed else "Confirmed by user"
                )

            # In non-interactive mode without callback, default to block for safety
            return SafetyCheckResult(
                allowed=False,
                requires_confirmation=True,
                action=action_upper,
                risk_level=risk_level,
                reason=f"Action '{action_upper}' blocked: {reason}. User confirmation required."
            )

        return SafetyCheckResult(
            allowed=True,
            requires_confirmation=False,
            action=action_upper,
            risk_level="LOW",
            reason="Safe autonomous action"
        )
