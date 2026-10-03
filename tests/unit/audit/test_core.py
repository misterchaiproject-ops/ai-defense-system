"""Comprehensive tests for audit.core."""

from __future__ import annotations

import concurrent.futures
from pathlib import Path

import pytest

from audit.core import (
    AuditEvent,
    EventValidationError,
    IntegrityError,
    SecureAuditLog,
)


@pytest.fixture
def key() -> bytes:
    """32-byte key for AES-256-GCM."""
    return bytes(range(32))


@pytest.fixture
def log_path(tmp_path: Path) -> Path:
    """Temporary encrypted log file path."""
    return tmp_path / "audit.log.enc"


@pytest.fixture
def audit_log(log_path: Path, key: bytes) -> SecureAuditLog:
    """A ready-to-use SecureAuditLog."""
    return SecureAuditLog(log_path=log_path, key=key)


@pytest.fixture
def sample_event() -> AuditEvent:
    """A valid sample event."""
    return AuditEvent(
        event_type="REPLAY_DETECTED",
        timestamp=1_700_000_000.0,
        agent_id="Agent_A",
        details={"nonce_prefix": "abc123"},
    )


class TestAuditEventValidation:
    """Tests for AuditEvent field validation."""

    def test_accepts_valid_inputs(self) -> None:
        """A well-formed event is constructed without error."""
        event = AuditEvent(
            event_type="TEST",
            timestamp=1.0,
            agent_id="A",
            details={},
        )
        assert event.event_type == "TEST"
        assert event.agent_id == "A"

    def test_rejects_empty_event_type(self) -> None:
        """Empty event_type is rejected."""
        with pytest.raises(EventValidationError, match="event_type"):
            AuditEvent(
                event_type="",
                timestamp=1.0,
                agent_id="A",
                details={},
            )

    def test_rejects_non_str_event_type(self) -> None:
        """Non-str event_type is rejected."""
        with pytest.raises(EventValidationError, match="event_type"):
            AuditEvent(
                event_type=123,  # type: ignore[arg-type]
                timestamp=1.0,
                agent_id="A",
                details={},
            )

    def test_rejects_control_chars_in_event_type(self) -> None:
        """Control characters in event_type are rejected."""
        with pytest.raises(EventValidationError, match="event_type"):
            AuditEvent(
                event_type="BAD\x00TYPE",
                timestamp=1.0,
                agent_id="A",
                details={},
            )

    def test_rejects_negative_timestamp(self) -> None:
        """Negative timestamp is rejected."""
        with pytest.raises(EventValidationError, match="timestamp"):
            AuditEvent(
                event_type="TEST",
                timestamp=-1.0,
                agent_id="A",
                details={},
            )

    def test_rejects_nan_timestamp(self) -> None:
        """NaN timestamp is rejected."""
        with pytest.raises(EventValidationError, match="timestamp"):
            AuditEvent(
                event_type="TEST",
                timestamp=float("nan"),
                agent_id="A",
                details={},
            )

    def test_rejects_non_mapping_details(self) -> None:
        """Non-mapping details is rejected."""
        with pytest.raises(EventValidationError, match="details"):
            AuditEvent(
                event_type="TEST",
                timestamp=1.0,
                agent_id="A",
                details=[1, 2, 3],  # type: ignore[arg-type]
            )

    def test_rejects_non_serializable_details(self) -> None:
        """Details that cannot be JSON-serialized are rejected."""
        with pytest.raises(EventValidationError, match="details"):
            AuditEvent(
                event_type="TEST",
                timestamp=1.0,
                agent_id="A",
                details={"bad": {1, 2, 3}},
            )


class TestSecureAuditLogInit:
    """Tests for SecureAuditLog constructor."""

    def test_rejects_short_key(self, log_path: Path) -> None:
        """A key shorter than 32 bytes is rejected."""
        with pytest.raises(ValueError, match="32"):
            SecureAuditLog(log_path=log_path, key=b"short")

    def test_rejects_non_bytes_key(self, log_path: Path) -> None:
        """A non-bytes key is rejected."""
        with pytest.raises(TypeError, match="bytes"):
            SecureAuditLog(log_path=log_path, key="a" * 32)  # type: ignore[arg-type]

    def test_creates_parents_by_default(self, tmp_path: Path, key: bytes) -> None:
        """Parent directories are created by default."""
        nested = tmp_path / "deeply" / "nested" / "audit.log.enc"
        SecureAuditLog(log_path=nested, key=key)
        assert nested.parent.is_dir()

    def test_rejects_missing_parent_when_disabled(self, tmp_path: Path, key: bytes) -> None:
        """create_parents=False raises if parent is missing."""
        nested = tmp_path / "no" / "parent" / "audit.log.enc"
        with pytest.raises(FileNotFoundError):
            SecureAuditLog(log_path=nested, key=key, create_parents=False)


class TestSecureAuditLogRoundtrip:
    """Tests for append and read_all."""

    def test_read_empty_log(self, audit_log: SecureAuditLog) -> None:
        """Reading an empty log returns an empty list."""
        assert audit_log.read_all() == []

    def test_append_creates_file(
        self,
        audit_log: SecureAuditLog,
        sample_event: AuditEvent,
        log_path: Path,
    ) -> None:
        """After append, the log file exists."""
        audit_log.append(sample_event)
        assert log_path.exists()

    def test_append_single_event(self, audit_log: SecureAuditLog, sample_event: AuditEvent) -> None:
        """A single appended event is read back intact."""
        audit_log.append(sample_event)
        events = audit_log.read_all()
        assert len(events) == 1
        assert events[0] == sample_event

    def test_read_preserves_order(self, audit_log: SecureAuditLog) -> None:
        """Multiple events are returned in append order."""
        for i in range(5):
            audit_log.append(
                AuditEvent(
                    event_type=f"EVENT_{i}",
                    timestamp=float(i),
                    agent_id="A",
                    details={"i": i},
                )
            )
        events = audit_log.read_all()
        assert [e.event_type for e in events] == [f"EVENT_{i}" for i in range(5)]

    def test_append_multiple_events(self, audit_log: SecureAuditLog) -> None:
        """Many events can be appended and read."""
        for i in range(20):
            audit_log.append(
                AuditEvent(
                    event_type="BULK",
                    timestamp=float(i),
                    agent_id="A",
                    details={"n": i},
                )
            )
        assert len(audit_log.read_all()) == 20


class TestSecureAuditLogIntegrity:
    """Tests for verify_integrity and tamper detection."""

    def test_verify_empty_log(self, audit_log: SecureAuditLog) -> None:
        """An empty log passes integrity verification."""
        assert audit_log.verify_integrity() is True

    def test_verify_valid_log(self, audit_log: SecureAuditLog, sample_event: AuditEvent) -> None:
        """A valid log passes integrity verification."""
        audit_log.append(sample_event)
        assert audit_log.verify_integrity() is True

    def test_detects_tampered_record(
        self,
        audit_log: SecureAuditLog,
        sample_event: AuditEvent,
        log_path: Path,
    ) -> None:
        """Flipping a byte in the file is detected."""
        audit_log.append(sample_event)
        data = bytearray(log_path.read_bytes())
        data[len(data) // 2] ^= 0xFF
        log_path.write_bytes(bytes(data))
        assert audit_log.verify_integrity() is False

    def test_read_rejects_wrong_key(
        self,
        audit_log: SecureAuditLog,
        sample_event: AuditEvent,
        log_path: Path,
        tmp_path: Path,
    ) -> None:
        """Reading with a different key raises IntegrityError."""
        audit_log.append(sample_event)
        wrong_key = bytes([0xFF]) * 32
        wrong_log = SecureAuditLog(log_path=log_path, key=wrong_key)
        with pytest.raises(IntegrityError):
            wrong_log.read_all()

    def test_read_rejects_truncated_record(
        self,
        audit_log: SecureAuditLog,
        sample_event: AuditEvent,
        log_path: Path,
    ) -> None:
        """A truncated log file raises IntegrityError."""
        audit_log.append(sample_event)
        data = log_path.read_bytes()
        log_path.write_bytes(data[:-10])
        with pytest.raises(IntegrityError):
            audit_log.read_all()


class TestSecureAuditLogHardening:
    """Tests for thread safety and nonce uniqueness (G5 hardening)."""

    def test_concurrent_appends_no_corruption(self, audit_log: SecureAuditLog) -> None:
        """Concurrent appends from 5 threads do not corrupt records."""

        def worker(thread_id: int) -> None:
            for i in range(10):
                audit_log.append(
                    AuditEvent(
                        event_type=f"T{thread_id}_E{i}",
                        timestamp=float(thread_id * 100 + i),
                        agent_id="A",
                        details={"t": thread_id, "i": i},
                    )
                )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(worker, tid) for tid in range(5)]
            for fut in futures:
                fut.result()

        events = audit_log.read_all()
        assert len(events) == 50
        event_types = [e.event_type for e in events]
        assert len(set(event_types)) == 50

    def test_nonces_are_unique_across_appends(
        self, audit_log: SecureAuditLog, log_path: Path
    ) -> None:
        """Each appended record uses a distinct 12-byte nonce."""
        for i in range(50):
            audit_log.append(
                AuditEvent(
                    event_type="NONCE_TEST",
                    timestamp=float(i),
                    agent_id="A",
                    details={"i": i},
                )
            )

        data = log_path.read_bytes()
        nonces: list[bytes] = []
        offset = 0
        while offset < len(data):
            length = int.from_bytes(data[offset : offset + 4], "big")
            offset += 4
            payload_start = offset
            nonces.append(data[payload_start : payload_start + 12])
            offset = payload_start + length

        assert len(nonces) == 50
        assert len(set(nonces)) == 50
