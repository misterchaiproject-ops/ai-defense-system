"""Core implementation of encrypted, append-only audit logging."""

from __future__ import annotations

import json
import math
import secrets
import struct
import threading
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AuditError(Exception):
    """Base exception for audit log operations."""


class IntegrityError(AuditError):
    """Raised when log integrity verification or decryption fails."""


class EventValidationError(AuditError):
    """Raised when an AuditEvent fails validation."""


def _validate_string_field(value: Any, name: str) -> str:
    """Validate that a field is a non-empty string without control characters."""
    if not isinstance(value, str) or not value:
        raise EventValidationError(f"Field '{name}' must be a non-empty string.")
    for char in value:
        if unicodedata.category(char) == "Cc" or ord(char) < 32 or (127 <= ord(char) <= 159):
            raise EventValidationError(f"Field '{name}' contains forbidden control characters.")
    return value


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Represents a discrete security or operational audit event."""

    event_type: str
    timestamp: float
    agent_id: str
    details: Mapping[str, Any]

    def __post_init__(self) -> None:
        _validate_string_field(self.event_type, "event_type")
        _validate_string_field(self.agent_id, "agent_id")

        if not isinstance(self.timestamp, int | float) or isinstance(self.timestamp, bool):
            raise EventValidationError("Field 'timestamp' must be a numeric value.")
        if math.isnan(self.timestamp) or math.isinf(self.timestamp) or self.timestamp < 0:
            raise EventValidationError("Field 'timestamp' must be a finite non-negative number.")

        if not isinstance(self.details, Mapping):
            raise EventValidationError("Field 'details' must be a mapping (dictionary).")

        try:
            serialized = json.dumps(self.details, sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError) as e:
            raise EventValidationError(f"Field 'details' must be JSON-serializable: {e}") from e

        if len(serialized.encode("utf-8")) > 16 * 1024:
            raise EventValidationError("Field 'details' exceeds the maximum allowed size of 16 KB.")


class SecureAuditLog:
    """Thread-safe, encrypted, append-only audit log using AES-256-GCM."""

    def __init__(
        self,
        log_path: Path | str,
        key: bytes,
        *,
        create_parents: bool = True,
    ) -> None:
        if not isinstance(key, bytes):
            raise TypeError("Encryption key must be bytes.")
        if len(key) != 32:
            raise ValueError("AES-256 encryption key must be exactly 32 bytes.")

        if not isinstance(log_path, str | Path):
            raise TypeError("log_path must be a string or Path object.")

        path = Path(log_path)
        if create_parents:
            path.parent.mkdir(parents=True, exist_ok=True)
        elif not path.parent.exists():
            raise FileNotFoundError(f"Parent directory does not exist: {path.parent}")

        self._log_path = path
        self._key = key
        self._aesgcm = AESGCM(key)
        self._lock = threading.Lock()

    def append(self, event: AuditEvent) -> None:
        """Encrypt and append an audit event to the log file (Append-Only)."""
        payload_dict = {
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "agent_id": event.agent_id,
            "details": dict(event.details),
        }
        plaintext = json.dumps(payload_dict, sort_keys=True, separators=(",", ":")).encode("utf-8")

        # 12-byte cryptographically secure random nonce for AES-GCM
        nonce = secrets.token_bytes(12)
        ciphertext = self._aesgcm.encrypt(nonce, plaintext, associated_data=b"audit-v1")

        payload = nonce + ciphertext
        length_prefix = struct.pack(">I", len(payload))

        with self._lock, open(self._log_path, "ab") as f:
            f.write(length_prefix + payload)

    def read_all(self) -> list[AuditEvent]:
        """Read, decrypt, and return all audit events from the log."""
        events: list[AuditEvent] = []
        if not self._log_path.exists():
            return events

        with self._lock, open(self._log_path, "rb") as f:
            while True:
                length_bytes = f.read(4)
                if not length_bytes:
                    break
                if len(length_bytes) < 4:
                    raise IntegrityError("Truncated audit log: incomplete length prefix.")

                (length,) = struct.unpack(">I", length_bytes)
                payload = f.read(length)
                if len(payload) < length:
                    raise IntegrityError("Truncated audit log: incomplete payload data.")
                if len(payload) < 12:
                    raise IntegrityError("Invalid audit record: payload too short for nonce.")

                nonce = payload[:12]
                ciphertext = payload[12:]

                try:
                    plaintext = self._aesgcm.decrypt(nonce, ciphertext, associated_data=b"audit-v1")
                except Exception as e:
                    raise IntegrityError(f"Decryption or integrity verification failed: {e}") from e

                try:
                    data = json.loads(plaintext.decode("utf-8"))
                except Exception as e:
                    raise IntegrityError(
                        f"Failed to parse JSON from decrypted audit record: {e}"
                    ) from e

                event = AuditEvent(
                    event_type=data["event_type"],
                    timestamp=data["timestamp"],
                    agent_id=data["agent_id"],
                    details=data["details"],
                )
                events.append(event)

        return events

    def verify_integrity(self) -> bool:
        """Verify that all records in the log are untampered and successfully decrypt."""
        try:
            self.read_all()
            return True
        except IntegrityError:
            return False
