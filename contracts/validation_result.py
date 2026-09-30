"""
Unified validation result.

Replaces the fragile (bool, str) pattern with a single,
immutable, self-documenting object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .reason_codes import ReasonCode


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """
    The outcome of any validation in the system.

    Invariant:
        approved=True  <=>  reason is ReasonCode.OK
        approved=False <=>  reason is NOT ReasonCode.OK
    """
    approved: bool
    reason: ReasonCode
    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        # Enforce immutable metadata
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(
                self, "metadata", MappingProxyType(dict(self.metadata))
            )
        # Enforce approved <-> reason consistency
        if self.approved and self.reason is not ReasonCode.OK:
            raise ValueError("approved=True requires ReasonCode.OK")
        if not self.approved and self.reason is ReasonCode.OK:
            raise ValueError("approved=False cannot use ReasonCode.OK")

    def __bool__(self) -> bool:
        return self.approved

    @classmethod
    def ok(cls) -> "ValidationResult":
        """Build a success result."""
        return cls(approved=True, reason=ReasonCode.OK)

    @classmethod
    def reject(cls, reason: ReasonCode, **meta: Any) -> "ValidationResult":
        """Build a rejection with optional metadata."""
        return cls(approved=False, reason=reason, metadata=meta)
