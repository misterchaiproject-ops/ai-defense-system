"""
SecureAgentChannel — signed, replay-resistant messaging.

Signs envelopes with HMAC-SHA256 and verifies them on receipt.
Provides:
  - Canonical JSON (deterministic serialization).
  - Bounded replay cache.
  - Sender allowlist.
  - Timestamp freshness window.
  - Log sanitization.
  - Constant-time signature comparison.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import math
import re
import secrets
import sqlite3
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from contracts import ReasonCode, ValidationResult

logger = logging.getLogger(__name__)

PROTOCOL_VERSION = "v1"
_MIN_SECRET_BYTES = 32
_MAX_PAYLOAD_BYTES = 64 * 1024
_MAX_CLOCK_SKEW_FUTURE = 1.0

_SENDER_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")
_NONCE_RE = re.compile(r"^[0-9a-f]{32}$")
_SIG_RE = re.compile(r"^[0-9a-f]{64}$")
_CONTROL = re.compile(r"[\x00-\x1f\x7f\u200b-\u200f\u2028-\u202f\ufeff]")


def _sanitize(value: Any, max_len: int = 64) -> str:
    """Remove control characters and truncate (anti Log-Injection)."""
    return _CONTROL.sub("", str(value))[:max_len]


# ---------------------------------------------------------------------------
# Envelope
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Envelope:
    """Immutable signed message."""

    version: str
    key_id: str
    sender_id: str
    timestamp: float
    nonce: str
    payload: Mapping[str, Any]
    signature: str

    def __post_init__(self) -> None:
        if self.version != PROTOCOL_VERSION:
            raise ValueError(f"unsupported version: {self.version}")
        if not _SENDER_RE.match(self.key_id):
            raise ValueError("invalid key_id")
        if not _SENDER_RE.match(self.sender_id):
            raise ValueError("invalid sender_id")
        if isinstance(self.timestamp, bool) or not isinstance(self.timestamp, int | float):
            raise TypeError("timestamp must be numeric")
        if not math.isfinite(self.timestamp):
            raise ValueError("timestamp must be finite")
        if not _NONCE_RE.match(self.nonce):
            raise ValueError("invalid nonce format")
        if not _SIG_RE.match(self.signature):
            raise ValueError("invalid signature format")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a Mapping")
        if not isinstance(self.payload, MappingProxyType):
            object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


# ---------------------------------------------------------------------------
# Replay cache
# ---------------------------------------------------------------------------


class _ReplayCache:
    """Bounded, thread-safe nonce cache (FIFO) with SQLite persistence.

    Default (db_path=None) uses an isolated in-memory database.
    Providing db_path enables durable storage across restarts.
    """

    def __init__(
        self,
        max_size: int = 10_000,
        db_path: Path | str | None = None,
    ) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be > 0")
        self._max = max_size
        self._lock = threading.Lock()

        if db_path is None or db_path == ":memory:":
            location = ":memory:"
        else:
            location = str(db_path)
            Path(location).parent.mkdir(parents=True, exist_ok=True)

        self._conn = sqlite3.connect(location, check_same_thread=False)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS seen_nonces ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "nonce TEXT NOT NULL UNIQUE)"
        )
        self._conn.commit()

    def check_and_add(self, nonce: str) -> bool:
        with self._lock:
            row = self._conn.execute(
                "SELECT 1 FROM seen_nonces WHERE nonce = ? LIMIT 1",
                (nonce,),
            ).fetchone()
            if row is not None:
                return False
            self._conn.execute(
                "INSERT INTO seen_nonces (nonce) VALUES (?)",
                (nonce,),
            )
            self._conn.execute(
                "DELETE FROM seen_nonces WHERE id NOT IN ("
                "SELECT id FROM seen_nonces ORDER BY id DESC LIMIT ?)",
                (self._max,),
            )
            self._conn.commit()
            return True


# ---------------------------------------------------------------------------
# Channel
# ---------------------------------------------------------------------------


class SecureAgentChannel:
    """Signs and verifies envelopes."""

    def __init__(
        self,
        shared_secret: bytes | None = None,
        key_id: str | None = None,
        allowed_senders: frozenset[str] | None = None,
        max_delay_seconds: float = 300,
        key_ring: Mapping[str, bytes] | None = None,
        active_key_id: str | None = None,
        db_path: Path | str | None = None,
    ) -> None:
        if key_ring is not None and (shared_secret is not None or key_id is not None):
            raise ValueError("shared_secret/key_id and key_ring are mutually exclusive")

        if key_ring is not None:
            if not key_ring:
                raise ValueError("key_ring must not be empty")
            if active_key_id is None:
                raise ValueError("active_key_id is required with key_ring")
            if active_key_id not in key_ring:
                raise ValueError(f"active_key_id {active_key_id!r} not present in key_ring")
            validated_ring: dict[str, bytes] = {}
            for kid, sec in key_ring.items():
                if not _SENDER_RE.match(kid):
                    raise ValueError(f"invalid key_id: {kid!r}")
                if not isinstance(sec, bytes):
                    raise TypeError(f"secret for {kid!r} must be bytes")
                if len(sec) < _MIN_SECRET_BYTES:
                    raise ValueError(f"secret for {kid!r} must be >= {_MIN_SECRET_BYTES} bytes")
                validated_ring[kid] = bytes(sec)
            self._key_ring = validated_ring
            self._key_id = active_key_id
        else:
            if shared_secret is None or key_id is None:
                raise ValueError(
                    "shared_secret and key_id are required when key_ring is not provided"
                )
            if not isinstance(shared_secret, bytes):
                raise TypeError("shared_secret must be bytes")
            if len(shared_secret) < _MIN_SECRET_BYTES:
                raise ValueError(f"shared_secret must be >= {_MIN_SECRET_BYTES} bytes")
            if not _SENDER_RE.match(key_id):
                raise ValueError("invalid key_id")
            self._key_ring = {key_id: bytes(shared_secret)}
            self._key_id = key_id

        if isinstance(max_delay_seconds, bool) or not isinstance(max_delay_seconds, int | float):
            raise TypeError("max_delay_seconds must be numeric")
        if not math.isfinite(max_delay_seconds) or not (0 < max_delay_seconds <= 300):
            raise ValueError("max_delay_seconds must be in (0, 300]")

        if allowed_senders is not None:
            for s in allowed_senders:
                if not isinstance(s, str) or not _SENDER_RE.match(s):
                    raise ValueError(f"invalid sender: {s!r}")

        self._allowed = allowed_senders
        self._max_delay = float(max_delay_seconds)
        self._replay = _ReplayCache(db_path=db_path)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    def create_message(self, sender_id: str, payload: Mapping[str, Any]) -> Envelope:
        if not _SENDER_RE.match(sender_id):
            raise ValueError("invalid sender_id")

        canonical = self._canonicalize(payload)
        timestamp = time.time()
        nonce = secrets.token_hex(16)

        sig = self._sign(
            key_id=self._key_id,
            sender_id=sender_id,
            timestamp=timestamp,
            nonce=nonce,
            canonical_payload=canonical,
        )

        return Envelope(
            version=PROTOCOL_VERSION,
            key_id=self._key_id,
            sender_id=sender_id,
            timestamp=timestamp,
            nonce=nonce,
            payload=payload,
            signature=sig,
        )

    # ------------------------------------------------------------------
    # Verify
    # ------------------------------------------------------------------
    def verify_message(self, envelope: Any) -> ValidationResult:
        try:
            if not isinstance(envelope, Envelope):
                return ValidationResult.reject(ReasonCode.INVALID_ENVELOPE)

            if envelope.version != PROTOCOL_VERSION:
                return ValidationResult.reject(ReasonCode.UNSUPPORTED_VERSION)

            if envelope.key_id not in self._key_ring:
                return ValidationResult.reject(ReasonCode.UNKNOWN_KEY_ID)

            if self._allowed is not None and envelope.sender_id not in self._allowed:
                logger.warning("Unauthorized sender: %s", _sanitize(envelope.sender_id))
                return ValidationResult.reject(ReasonCode.ROLE_NOT_PERMITTED)

            now = time.time()
            delta = now - envelope.timestamp
            if delta > self._max_delay:
                return ValidationResult.reject(ReasonCode.TIMESTAMP_TOO_OLD)
            if delta < -_MAX_CLOCK_SKEW_FUTURE:
                return ValidationResult.reject(ReasonCode.TIMESTAMP_FROM_FUTURE)

            if not self._replay.check_and_add(envelope.nonce):
                logger.warning(
                    "Replay detected from %s",
                    _sanitize(envelope.sender_id),
                )
                return ValidationResult.reject(ReasonCode.REPLAY_DETECTED)

            canonical = self._canonicalize(dict(envelope.payload))
            expected = self._sign(
                key_id=envelope.key_id,
                sender_id=envelope.sender_id,
                timestamp=envelope.timestamp,
                nonce=envelope.nonce,
                canonical_payload=canonical,
            )
            if not hmac.compare_digest(envelope.signature, expected):
                logger.critical(
                    "Invalid signature from %s",
                    _sanitize(envelope.sender_id),
                )
                return ValidationResult.reject(ReasonCode.INVALID_SIGNATURE)

            return ValidationResult.ok()

        except Exception:
            logger.exception("Channel internal error")
            return ValidationResult.reject(ReasonCode.INTERNAL_ERROR)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    @staticmethod
    def _canonicalize(payload: Mapping[str, Any]) -> bytes:
        try:
            s = json.dumps(
                payload,
                sort_keys=True,
                ensure_ascii=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ValueError(f"payload not serializable: {exc}") from exc
        if len(s) > _MAX_PAYLOAD_BYTES:
            raise ValueError("payload exceeds max size")
        return s

    def _sign(
        self,
        key_id: str,
        *,
        sender_id: str,
        timestamp: float,
        nonce: str,
        canonical_payload: bytes,
    ) -> str:
        mac = hmac.new(self._key_ring[key_id], digestmod=hashlib.sha256)
        mac.update(PROTOCOL_VERSION.encode())
        mac.update(b"\x00")
        mac.update(sender_id.encode())
        mac.update(b"\x00")
        mac.update(f"{timestamp:.6f}".encode("ascii"))
        mac.update(b"\x00")
        mac.update(nonce.encode("ascii"))
        mac.update(b"\x00")
        mac.update(canonical_payload)
        return mac.hexdigest()


def generate_shared_secret() -> bytes:
    """Generate a cryptographically strong 256-bit secret."""
    return secrets.token_bytes(32)
