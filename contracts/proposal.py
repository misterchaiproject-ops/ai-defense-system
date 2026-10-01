"""
Immutable Proposal.

A Proposal is the core object that flows through the system:
  - Created by an agent.
  - Validated by the Guardrail.
  - Signed by the Channel.
  - Sent over the network.

Because it is `frozen`, no code can modify it after construction.
This closes the TOCTOU window between validation and signing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .actions import Action


@dataclass(frozen=True, slots=True)
class Proposal:
    """
    An immutable proposal from an agent.

    Attributes:
        action: The requested action (from the Action enum).
        target: The name of the system being acted upon.
        value: Optional numeric value (e.g., a new setpoint).
    """

    action: Action
    target: str
    value: float | None = None

    def __post_init__(self) -> None:
        # Action must be the enum, not a raw string
        if not isinstance(self.action, Action):
            raise TypeError("action must be an Action")

        # Target must be a non-empty string, bounded in size
        if not isinstance(self.target, str) or not self.target.strip():
            raise ValueError("target must be a non-empty string")
        if len(self.target) > 128:
            raise ValueError("target too long (max 128 chars)")

        # Value (if present) must be a finite number, not bool
        if self.value is not None:
            if isinstance(self.value, bool):
                raise TypeError("value must be a number, not bool")
            if not isinstance(self.value, (int, float)):
                raise TypeError("value must be a number or None")
            if not math.isfinite(self.value):
                raise ValueError("value must be finite (no NaN, no Inf)")

    def to_payload(self) -> dict[str, object]:
        """Deterministic dict representation for signing/serialization."""
        return {
            "action": self.action.value,
            "target": self.target,
            "value": self.value,
        }
