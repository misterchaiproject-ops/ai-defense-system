"""Protocol boundaries for replaceable security infrastructure.

These interfaces intentionally contain no concrete implementation details.
They define the minimum contracts required by future dependency-injection work.
"""

from __future__ import annotations

from typing import Protocol

from audit import AuditEvent


class AuditSink(Protocol):
    """Durable destination for security audit events."""

    def append(self, event: AuditEvent) -> None:
        """Persist one validated audit event."""
        ...


class ReplayStore(Protocol):
    """Store used to enforce nonce uniqueness across message verification."""

    def check_and_add(self, nonce: str) -> bool:
        """Atomically accept a new nonce or reject a previously seen nonce."""
        ...


class Clock(Protocol):
    """Source of wall-clock time used by security decisions."""

    def now(self) -> float:
        """Return the current UTC Unix timestamp in seconds."""
        ...


class KeyProvider(Protocol):
    """Source of cryptographic keys used by authenticated channels."""

    def get_key(self, key_id: str) -> bytes | None:
        """Return the key for ``key_id`` or ``None`` when it is unavailable."""
        ...

    def get_active_key_id(self) -> str:
        """Return the key identifier currently approved for outbound signing."""
        ...
