"""Default adapters for the dependency-injection layer."""

from __future__ import annotations

import re
import time
from collections.abc import Mapping

_KEY_ID_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")
_MIN_SECRET_BYTES = 32


class SystemClock:
    """Production wall-clock implementation of the Clock protocol."""

    def now(self) -> float:
        return time.time()


class MappingKeyProvider:
    """Validated key provider backed by an internal copy of a mapping."""

    def __init__(self, key_ring: Mapping[str, bytes], active_key_id: str) -> None:
        if not key_ring:
            raise ValueError("key_ring must not be empty")
        if active_key_id not in key_ring:
            raise ValueError(f"active_key_id {active_key_id!r} not present in key_ring")

        validated: dict[str, bytes] = {}
        for key_id, secret in key_ring.items():
            if not _KEY_ID_RE.match(key_id):
                raise ValueError(f"invalid key_id: {key_id!r}")
            if not isinstance(secret, bytes):
                raise TypeError(f"secret for {key_id!r} must be bytes")
            if len(secret) < _MIN_SECRET_BYTES:
                raise ValueError(
                    f"secret for {key_id!r} must be >= {_MIN_SECRET_BYTES} bytes"
                )
            validated[key_id] = bytes(secret)

        self._key_ring = validated
        self._active_key_id = active_key_id

    def get_key(self, key_id: str) -> bytes | None:
        return self._key_ring.get(key_id)

    def get_active_key_id(self) -> str:
        return self._active_key_id

    def __repr__(self) -> str:
        return (
            f"MappingKeyProvider(active_key_id={self._active_key_id!r}, "
            f"key_count={len(self._key_ring)})"
        )


__all__ = ["MappingKeyProvider", "SystemClock"]
