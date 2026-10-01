"""
Immutable Proposal — the core contract that flows through the system.

Security invariants enforced at construction:
- action must be a member of the Action enum.
- target must be non-empty, bounded, no control chars.
- value (if present) must be finite real number (no bool, NaN, Inf).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Final

from .actions import Action

MAX_TARGET_LENGTH: Final[int] = 128

_CONTROL_CHARS: Final[re.Pattern[str]] = re.compile(r"[\x00-\x1f\x7f-\x9f]")


@dataclass(frozen=True, slots=True)
class Proposal:
    """An immutable proposal from an agent."""

    action: Action
    target: str
    value: float | None = None

    def __post_init__(self) -> None:
        _validate_action(self.action)
        _validate_target(self.target)
        _validate_value(self.value)

    def to_payload(self) -> dict[str, str | float | None]:
        """Return a deterministic dict representation for signing."""
        return {
            "action": self.action.value,
            "target": self.target,
            "value": self.value,
        }


def _validate_action(action: object) -> None:
    if not isinstance(action, Action):
        raise TypeError(f"action must be an Action enum member, got {type(action).__name__}")


def _validate_target(target: object) -> None:
    if not isinstance(target, str):
        raise TypeError(f"target must be str, got {type(target).__name__}")
    if not target:
        raise ValueError("target must be a non-empty string")
    if not target.strip():
        raise ValueError("target must not be whitespace-only")
    if len(target) > MAX_TARGET_LENGTH:
        raise ValueError(f"target must be <= {MAX_TARGET_LENGTH} characters, got {len(target)}")
    if _CONTROL_CHARS.search(target):
        raise ValueError("target must not contain control characters")


def _validate_value(value: object) -> None:
    if value is None:
        return
    if isinstance(value, bool):
        raise TypeError("value must be a real number, not bool")
    if not isinstance(value, (int, float)):
        raise TypeError(f"value must be int, float, or None, got {type(value).__name__}")
    if not math.isfinite(value):
        raise ValueError("value must be finite (no NaN, no Inf)")


__all__ = ["Proposal", "MAX_TARGET_LENGTH"]
