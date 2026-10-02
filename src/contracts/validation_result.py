"""
Unified validation result.

Replaces the fragile (bool, str) pattern with a single, immutable,
self-documenting object.

Security invariants enforced at construction:
  - approved must be a real bool (not int/str/truthy value).
  - reason must be a ReasonCode member (not a raw string).
  - metadata must be a Mapping, is copied into an immutable
    MappingProxyType, and its size is bounded to prevent DoS.
  - The invariant approved <-> reason is ReasonCode.OK is
    enforced: mixing them raises ValueError.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Final

from .reason_codes import ReasonCode

MAX_METADATA_ENTRIES: Final[int] = 64


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
        default_factory=lambda: MappingProxyType({}),
        hash=False,
    )

    def __post_init__(self) -> None:
        _validate_approved(self.approved)
        _validate_reason(self.reason)
        _freeze_and_bound_metadata(self)
        _validate_invariant(self.approved, self.reason)

    def __bool__(self) -> bool:
        return self.approved

    @classmethod
    def ok(cls) -> ValidationResult:
        return cls(approved=True, reason=ReasonCode.OK)

    @classmethod
    def reject(cls, reason: ReasonCode, **meta: Any) -> ValidationResult:
        return cls(approved=False, reason=reason, metadata=meta)


def _validate_approved(approved: object) -> None:
    if not isinstance(approved, bool):
        raise TypeError(f"approved must be a bool, got {type(approved).__name__}")


def _validate_reason(reason: object) -> None:
    if not isinstance(reason, ReasonCode):
        raise TypeError(f"reason must be a ReasonCode, got {type(reason).__name__}")


def _freeze_and_bound_metadata(result: ValidationResult) -> None:
    md = result.metadata
    if not isinstance(md, Mapping):
        raise TypeError(f"metadata must be a Mapping, got {type(md).__name__}")
    if len(md) > MAX_METADATA_ENTRIES:
        raise ValueError(f"metadata must not exceed {MAX_METADATA_ENTRIES} entries")
    if not isinstance(md, MappingProxyType):
        object.__setattr__(result, "metadata", MappingProxyType(dict(md)))


def _validate_invariant(approved: bool, reason: ReasonCode) -> None:
    if approved and reason is not ReasonCode.OK:
        raise ValueError("approved=True requires ReasonCode.OK")
    if not approved and reason is ReasonCode.OK:
        raise ValueError("approved=False cannot use ReasonCode.OK")


__all__ = ["ValidationResult", "MAX_METADATA_ENTRIES"]
