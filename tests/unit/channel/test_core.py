"""Comprehensive test suite for channel.core."""

from __future__ import annotations

import dataclasses
import time
from pathlib import Path

import pytest

from audit import SecureAuditLog
from channel.core import (
    _MAX_PAYLOAD_BYTES,
    Envelope,
    SecureAgentChannel,
    _ReplayCache,
    _ReplayCacheFullError,
    _sanitize,
    generate_shared_secret,
)
from contracts import ReasonCode

# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def secret() -> bytes:
    return generate_shared_secret()


@pytest.fixture
def channel(secret: bytes) -> SecureAgentChannel:
    return SecureAgentChannel(
        shared_secret=secret,
        key_id="test-v1",
        allowed_senders=frozenset({"Agent_A", "Agent_B"}),
    )


@pytest.fixture
def open_channel(secret: bytes) -> SecureAgentChannel:
    """Channel without sender whitelist."""
    return SecureAgentChannel(
        shared_secret=secret,
        key_id="open-v1",
    )


# ===========================================================================
# 1. _sanitize — 4 tests
# ===========================================================================


class TestSanitize:
    """Control characters are removed, length is bounded."""

    def test_removes_newline(self) -> None:
        assert "\n" not in _sanitize("a\nb")

    def test_removes_null_byte(self) -> None:
        assert "\x00" not in _sanitize("a\x00b")

    def test_truncates_to_max_len(self) -> None:
        assert len(_sanitize("a" * 200, max_len=10)) == 10

    def test_converts_non_string_to_string(self) -> None:
        assert _sanitize(42) == "42"


# ===========================================================================
# 2. Envelope — 6 tests
# ===========================================================================


class TestEnvelopeConstruction:
    """Immutable envelope with strict invariants."""

    @pytest.fixture
    def valid_envelope(self) -> Envelope:
        return Envelope(
            version="v1",
            key_id="test-v1",
            sender_id="Agent_A",
            timestamp=time.time(),
            nonce="a" * 32,
            payload={"x": 1},
            signature="b" * 64,
        )

    def test_valid_construction(self, valid_envelope: Envelope) -> None:
        assert valid_envelope.sender_id == "Agent_A"
        assert valid_envelope.nonce == "a" * 32

    def test_rejects_wrong_version(self) -> None:
        with pytest.raises(ValueError, match="version"):
            Envelope(
                version="v99",
                key_id="test-v1",
                sender_id="Agent_A",
                timestamp=time.time(),
                nonce="a" * 32,
                payload={"x": 1},
                signature="b" * 64,
            )

    def test_rejects_invalid_sender(self) -> None:
        with pytest.raises(ValueError, match="sender"):
            Envelope(
                version="v1",
                key_id="test-v1",
                sender_id="bad sender!",
                timestamp=time.time(),
                nonce="a" * 32,
                payload={"x": 1},
                signature="b" * 64,
            )

    def test_rejects_invalid_nonce_format(self) -> None:
        with pytest.raises(ValueError, match="nonce"):
            Envelope(
                version="v1",
                key_id="test-v1",
                sender_id="Agent_A",
                timestamp=time.time(),
                nonce="too-short",
                payload={"x": 1},
                signature="b" * 64,
            )

    def test_rejects_invalid_signature_format(self) -> None:
        with pytest.raises(ValueError, match="signature"):
            Envelope(
                version="v1",
                key_id="test-v1",
                sender_id="Agent_A",
                timestamp=time.time(),
                nonce="a" * 32,
                payload={"x": 1},
                signature="too-short",
            )

    def test_is_frozen(self, valid_envelope: Envelope) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            valid_envelope.sender_id = "Hacker"  # type: ignore[misc]


# ===========================================================================
# 3. _ReplayCache — 4 tests
# ===========================================================================


class TestReplayCache:
    """Bounded, thread-safe nonce cache."""

    def test_new_nonce_accepted(self) -> None:
        cache = _ReplayCache()
        assert cache.check_and_add("n1") is True

    def test_replay_rejected(self) -> None:
        cache = _ReplayCache()
        cache.check_and_add("n1")
        assert cache.check_and_add("n1") is False

    def test_capacity_does_not_evict_unexpired_nonces(self) -> None:
        cache = _ReplayCache(max_size=3)
        for i in range(3):
            assert cache.check_and_add(f"n{i}") is True
        assert cache.check_and_add("n0") is False
        with pytest.raises(_ReplayCacheFullError, match="capacity exhausted"):
            cache.check_and_add("n3")

    def test_many_unique_nonces(self) -> None:
        cache = _ReplayCache(max_size=100)
        for i in range(50):
            assert cache.check_and_add(f"n{i}") is True


# ===========================================================================
# 4. SecureAgentChannel — Constructor — 5 tests
# ===========================================================================


class TestChannelConstructor:
    """Initialization and validation."""

    def test_valid_construction(self, secret: bytes) -> None:
        ch = SecureAgentChannel(shared_secret=secret, key_id="test-v1")
        assert ch is not None

    def test_rejects_short_secret(self) -> None:
        with pytest.raises(ValueError, match="must be"):
            SecureAgentChannel(shared_secret=b"short", key_id="test-v1")

    def test_rejects_non_bytes_secret(self) -> None:
        with pytest.raises(TypeError, match="bytes"):
            SecureAgentChannel(
                shared_secret="dummy_secret" * 3,  # type: ignore[arg-type]  # noqa: S106
                key_id="test-v1",
            )

    def test_rejects_invalid_key_id(self, secret: bytes) -> None:
        with pytest.raises(ValueError, match="key_id"):
            SecureAgentChannel(shared_secret=secret, key_id="bad key!")

    def test_rejects_invalid_sender_in_whitelist(self, secret: bytes) -> None:
        with pytest.raises(ValueError, match="sender"):
            SecureAgentChannel(
                shared_secret=secret,
                key_id="test-v1",
                allowed_senders=frozenset({"bad sender!"}),
            )


# ===========================================================================
# 5. Round Trip — 4 tests
# ===========================================================================


class TestChannelRoundTrip:
    """Sign then verify with a valid message."""

    def test_sign_and_verify(self, channel: SecureAgentChannel) -> None:
        env = channel.create_message("Agent_A", {"x": 1})
        result = channel.verify_message(env)
        assert result.approved is True
        assert result.reason is ReasonCode.OK

    def test_envelope_has_correct_fields(self, channel: SecureAgentChannel) -> None:
        env = channel.create_message("Agent_A", {"x": 1})
        assert env.version == "v1"
        assert env.key_id == "test-v1"
        assert env.sender_id == "Agent_A"
        assert len(env.nonce) == 32
        assert len(env.signature) == 64

    def test_payload_preserved(self, channel: SecureAgentChannel) -> None:
        payload = {"action": "adjust_metric", "value": 60.0}
        env = channel.create_message("Agent_A", payload)
        assert dict(env.payload) == payload

    def test_no_whitelist_accepts_any_sender(self, open_channel: SecureAgentChannel) -> None:
        env = open_channel.create_message("AnyAgent", {"x": 1})
        result = open_channel.verify_message(env)
        assert result.approved is True


# ===========================================================================
# 6. Replay Protection — 3 tests
# ===========================================================================


class TestReplayProtection:
    """Duplicate nonces are rejected."""

    def test_replay_rejected(self, channel: SecureAgentChannel) -> None:
        env = channel.create_message("Agent_A", {"x": 1})
        assert channel.verify_message(env).approved is True
        result = channel.verify_message(env)
        assert result.approved is False
        assert result.reason is ReasonCode.REPLAY_DETECTED

    def test_different_messages_have_different_nonces(self, channel: SecureAgentChannel) -> None:
        env1 = channel.create_message("Agent_A", {"x": 1})
        env2 = channel.create_message("Agent_A", {"x": 1})
        assert env1.nonce != env2.nonce

    def test_ten_replays_all_rejected(self, channel: SecureAgentChannel) -> None:
        env = channel.create_message("Agent_A", {"x": 1})
        channel.verify_message(env)
        for _ in range(10):
            result = channel.verify_message(env)
            assert result.reason is ReasonCode.REPLAY_DETECTED


# ===========================================================================
# 7. Tampering — 5 tests
# ===========================================================================


class TestTampering:
    """Any field modification is detected."""

    def test_tampered_payload_rejected(self, channel: SecureAgentChannel) -> None:
        env = channel.create_message("Agent_A", {"x": 1})
        tampered = dataclasses.replace(env, payload={"x": 999})
        result = channel.verify_message(tampered)
        assert result.approved is False
        assert result.reason is ReasonCode.INVALID_SIGNATURE

    def test_tampered_signature_rejected(self, channel: SecureAgentChannel) -> None:
        env = channel.create_message("Agent_A", {"x": 1})
        replacement = "0" if env.signature[0] != "0" else "1"
        tampered_signature = replacement + env.signature[1:]
        tampered = dataclasses.replace(env, signature=tampered_signature)
        result = channel.verify_message(tampered)
        assert result.approved is False
        assert result.reason is ReasonCode.INVALID_SIGNATURE

    def test_invalid_signature_does_not_consume_nonce(self, channel: SecureAgentChannel) -> None:
        """An unauthenticated envelope must not poison a legitimate nonce."""
        valid = channel.create_message("Agent_A", {"action": "read"})
        replacement = "0" if valid.signature[0] != "0" else "1"
        bad_signature = replacement + valid.signature[1:]
        invalid = dataclasses.replace(valid, signature=bad_signature)

        rejected = channel.verify_message(invalid)
        assert rejected.approved is False
        assert rejected.reason is ReasonCode.INVALID_SIGNATURE

        # The same envelope with its original, valid signature must still work.
        accepted = channel.verify_message(valid)
        assert accepted.approved is True
        assert accepted.reason is ReasonCode.OK

    def test_tampered_nonce_rejected(self, channel: SecureAgentChannel) -> None:
        env = channel.create_message("Agent_A", {"x": 1})
        tampered = dataclasses.replace(env, nonce="f" * 32)
        result = channel.verify_message(tampered)
        assert result.approved is False

    def test_tampered_timestamp_rejected(self, channel: SecureAgentChannel) -> None:
        env = channel.create_message("Agent_A", {"x": 1})
        tampered = dataclasses.replace(env, timestamp=env.timestamp + 0.001)
        result = channel.verify_message(tampered)
        assert result.approved is False

    def test_unauthorized_sender_rejected(self, channel: SecureAgentChannel) -> None:
        env = channel.create_message("Agent_A", {"x": 1})
        tampered = dataclasses.replace(env, sender_id="Unknown_Agent")
        result = channel.verify_message(tampered)
        assert result.approved is False


# ===========================================================================
# 8. Timing — 2 tests
# ===========================================================================


class TestTiming:
    """Timestamps outside the freshness window are rejected."""

    def test_too_old_rejected(self, channel: SecureAgentChannel) -> None:
        env = channel.create_message("Agent_A", {"x": 1})
        tampered = dataclasses.replace(env, timestamp=time.time() - 100)
        result = channel.verify_message(tampered)
        assert result.approved is False

    def test_far_future_rejected(self, channel: SecureAgentChannel) -> None:
        env = channel.create_message("Agent_A", {"x": 1})
        tampered = dataclasses.replace(env, timestamp=time.time() + 100)
        result = channel.verify_message(tampered)
        assert result.approved is False


# ===========================================================================
# 9. Fail-Closed — 3 tests
# ===========================================================================


class TestFailClosed:
    """Defensive guarantees."""

    def test_non_envelope_rejected(self, channel: SecureAgentChannel) -> None:
        result = channel.verify_message("not an envelope")
        assert result.approved is False

    def test_none_rejected(self, channel: SecureAgentChannel) -> None:
        result = channel.verify_message(None)
        assert result.approved is False

    def test_generate_shared_secret_length(self) -> None:
        s = generate_shared_secret()
        assert isinstance(s, bytes)
        assert len(s) == 32


# ===========================================================================
# 10. Additional Coverage — 10 tests
# ===========================================================================


class TestEnvelopeAdditional:
    """Cover remaining Envelope validation branches."""

    def test_rejects_invalid_key_id(self) -> None:
        with pytest.raises(ValueError, match="key_id"):
            Envelope(
                version="v1",
                key_id="bad key!",
                sender_id="Agent_A",
                timestamp=time.time(),
                nonce="a" * 32,
                payload={"x": 1},
                signature="b" * 64,
            )

    def test_rejects_nan_timestamp(self) -> None:
        with pytest.raises(ValueError, match="finite"):
            Envelope(
                version="v1",
                key_id="test-v1",
                sender_id="Agent_A",
                timestamp=float("nan"),
                nonce="a" * 32,
                payload={"x": 1},
                signature="b" * 64,
            )

    def test_rejects_bool_timestamp(self) -> None:
        with pytest.raises(TypeError, match="numeric"):
            Envelope(
                version="v1",
                key_id="test-v1",
                sender_id="Agent_A",
                timestamp=True,
                nonce="a" * 32,
                payload={"x": 1},
                signature="b" * 64,
            )

    def test_rejects_non_mapping_payload(self) -> None:
        with pytest.raises(TypeError, match="Mapping"):
            Envelope(
                version="v1",
                key_id="test-v1",
                sender_id="Agent_A",
                timestamp=time.time(),
                nonce="a" * 32,
                payload="not a mapping",  # type: ignore[arg-type]
                signature="b" * 64,
            )


class TestReplayCacheAdditional:
    """Cover remaining ReplayCache branches."""

    def test_zero_max_size_rejected(self) -> None:
        with pytest.raises(ValueError, match="max_size"):
            _ReplayCache(max_size=0)


class TestChannelAdditional:
    """Cover remaining Channel branches."""

    def test_rejects_non_numeric_max_delay(self, secret: bytes) -> None:
        with pytest.raises(TypeError, match="numeric"):
            SecureAgentChannel(
                shared_secret=secret,
                key_id="test-v1",
                max_delay_seconds="five",  # type: ignore[arg-type]
            )

    def test_rejects_negative_max_delay(self, secret: bytes) -> None:
        with pytest.raises(ValueError, match="max_delay"):
            SecureAgentChannel(
                shared_secret=secret,
                key_id="test-v1",
                max_delay_seconds=-1.0,
            )

    def test_create_message_rejects_invalid_sender(self, channel: SecureAgentChannel) -> None:
        with pytest.raises(ValueError, match="sender_id"):
            channel.create_message("bad sender!", {"x": 1})

    def test_verify_rejects_wrong_key_id(self, channel: SecureAgentChannel) -> None:
        env = channel.create_message("Agent_A", {"x": 1})
        tampered = dataclasses.replace(env, key_id="different-v1")
        result = channel.verify_message(tampered)
        assert result.approved is False
        assert result.reason is ReasonCode.UNKNOWN_KEY_ID

    def test_verify_rejects_unsupported_version(self, channel: SecureAgentChannel) -> None:
        channel.create_message("Agent_A", {"x": 1})
        # Bypass Envelope validation by constructing a fake object
        # (only the Channel's verify_message is being tested here)
        fake = object.__new__(Envelope)
        object.__setattr__(fake, "version", "v99")
        object.__setattr__(fake, "key_id", "test-v1")
        object.__setattr__(fake, "sender_id", "Agent_A")
        object.__setattr__(fake, "timestamp", time.time())
        object.__setattr__(fake, "nonce", "a" * 32)
        object.__setattr__(fake, "payload", {"x": 1})
        object.__setattr__(fake, "signature", "b" * 64)
        result = channel.verify_message(fake)
        assert result.approved is False
        assert result.reason is ReasonCode.UNSUPPORTED_VERSION


class TestCanonicalize:
    """Test _canonicalize JSON serialization and size limits."""

    def test_rejects_non_serializable_payload(self) -> None:
        """Ensure ValueError is raised for non-serializable payloads (e.g., set)."""
        with pytest.raises(ValueError, match="payload not serializable"):
            SecureAgentChannel._canonicalize({"key": {1, 2, 3}})

    def test_rejects_oversized_payload(self) -> None:
        """Ensure ValueError is raised when payload exceeds _MAX_PAYLOAD_BYTES."""
        oversized_data = {"data": "A" * (_MAX_PAYLOAD_BYTES + 1)}
        with pytest.raises(ValueError, match="payload exceeds max size"):
            SecureAgentChannel._canonicalize(oversized_data)


class TestChannelErrorHandling:
    """Test graceful handling of internal errors in verify_message."""

    def test_verify_message_handles_internal_error(
        self, channel: SecureAgentChannel, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Ensure internal errors return INTERNAL_ERROR (fail-closed)."""
        # Create a valid message first
        payload = {"action": "adjust_metric", "value": 60.0}
        env = channel.create_message("Agent_A", payload)

        # Simulate an internal error by breaking _canonicalize
        def broken_canonicalize(payload: object) -> bytes:
            raise RuntimeError("Simulated internal error")

        monkeypatch.setattr(SecureAgentChannel, "_canonicalize", staticmethod(broken_canonicalize))

        # verify_message must handle the error gracefully
        result = channel.verify_message(env)
        assert result.approved is False
        assert result.reason is ReasonCode.INTERNAL_ERROR


# =============================================================================
# TestReplayCachePersistence - SQLite durability across instances
# =============================================================================


class TestReplayCachePersistence:
    """Tests for SQLite-backed nonce persistence across instances."""

    def test_nonce_persists_across_instances(self, tmp_path: Path) -> None:
        """A nonce added by one instance is detected by a new instance."""
        db_file = tmp_path / "replay.db"

        cache1 = _ReplayCache(db_path=db_file)
        assert cache1.check_and_add("persistent-nonce") is True

        cache2 = _ReplayCache(db_path=db_file)
        assert cache2.check_and_add("persistent-nonce") is False

    def test_capacity_policy_persists_across_instances(self, tmp_path: Path) -> None:
        """Unexpired nonce records survive restart and are not FIFO-evicted."""
        db_file = tmp_path / "replay.db"
        max_size = 3

        cache1 = _ReplayCache(max_size=max_size, db_path=db_file)
        for i in range(max_size):
            assert cache1.check_and_add(f"n{i}") is True
        with pytest.raises(_ReplayCacheFullError, match="capacity exhausted"):
            cache1.check_and_add("n3")

        cache2 = _ReplayCache(max_size=max_size, db_path=db_file)
        assert cache2.check_and_add("n0") is False
        with pytest.raises(_ReplayCacheFullError, match="capacity exhausted"):
            cache2.check_and_add("n3")

    def test_migrates_legacy_database_without_expiry_column(
        self,
        tmp_path: Path,
    ) -> None:
        """Legacy nonce rows remain reserved after adding expiry metadata."""
        import sqlite3

        db_file = tmp_path / "legacy-replay.db"
        connection = sqlite3.connect(db_file)
        connection.execute(
            "CREATE TABLE seen_nonces ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "nonce TEXT NOT NULL UNIQUE)"
        )
        connection.execute(
            "INSERT INTO seen_nonces (nonce) VALUES (?)",
            ("legacy-nonce",),
        )
        connection.commit()
        connection.close()

        cache = _ReplayCache(db_path=db_file)
        assert cache.check_and_add("legacy-nonce") is False

    def test_memory_mode_isolated(self) -> None:
        """Two default instances do not share state."""
        cache1 = _ReplayCache()
        cache2 = _ReplayCache()

        assert cache1.check_and_add("isolated") is True
        assert cache2.check_and_add("isolated") is True

    def test_db_file_created_after_first_write(self, tmp_path: Path) -> None:
        """The SQLite file exists after the first write."""
        db_file = tmp_path / "replay.db"
        cache = _ReplayCache(db_path=db_file)
        cache.check_and_add("first")
        assert db_file.exists()


# =============================================================================
# TestKeyRotation - Key ring support with legacy backward compatibility
# =============================================================================


class TestKeyRotation:
    """Tests for key rotation (key_ring + active_key_id)."""

    def test_legacy_single_key_still_works(self, secret: bytes) -> None:
        """Legacy single-key construction remains functional."""
        ch = SecureAgentChannel(
            shared_secret=secret,
            key_id="legacy-v1",
        )
        env = ch.create_message(
            "Agent_A",
            {"action": "adjust_metric", "value": 10.0},
        )
        assert env.key_id == "legacy-v1"
        assert ch.verify_message(env).approved is True

    def test_active_key_used_for_signing(self, secret: bytes) -> None:
        """Messages are signed with the active key from the ring."""
        key_ring = {
            "key-v1": secret,
            "key-v2": generate_shared_secret(),
        }
        ch = SecureAgentChannel(
            key_ring=key_ring,
            active_key_id="key-v2",
        )
        env = ch.create_message(
            "Agent_A",
            {"action": "adjust_metric", "value": 10.0},
        )
        assert env.key_id == "key-v2"

    def test_old_key_envelope_still_verified(self, secret: bytes) -> None:
        """Envelopes signed with an older ring key are still verified."""
        key_ring = {
            "key-v1": secret,
            "key-v2": generate_shared_secret(),
        }
        old_ch = SecureAgentChannel(
            key_ring=key_ring,
            active_key_id="key-v1",
        )
        env = old_ch.create_message(
            "Agent_A",
            {"action": "adjust_metric", "value": 10.0},
        )
        new_ch = SecureAgentChannel(
            key_ring=key_ring,
            active_key_id="key-v2",
        )
        result = new_ch.verify_message(env)
        assert result.approved is True

    def test_unknown_key_rejected(self, secret: bytes) -> None:
        """Envelopes with an unknown key_id are rejected."""
        ch = SecureAgentChannel(
            key_ring={"key-v1": secret},
            active_key_id="key-v1",
        )
        env = ch.create_message(
            "Agent_A",
            {"action": "adjust_metric", "value": 10.0},
        )
        tampered = dataclasses.replace(env, key_id="unknown-key")
        result = ch.verify_message(tampered)
        assert result.approved is False
        assert result.reason is ReasonCode.UNKNOWN_KEY_ID

    def test_ambiguous_args_rejected(self, secret: bytes) -> None:
        """Passing both shared_secret and key_ring raises ValueError."""
        with pytest.raises(ValueError, match="key_ring"):
            SecureAgentChannel(
                shared_secret=secret,
                key_id="legacy-v1",
                key_ring={"key-v1": secret},
                active_key_id="key-v1",
            )


# =============================================================================
# TestChannelG1Wiring - SQLite persistence wired through SecureAgentChannel
# =============================================================================


class TestChannelG1Wiring:
    """Tests for db_path wiring from SecureAgentChannel to _ReplayCache."""

    def test_channel_db_path_creates_file(self, secret: bytes, tmp_path: Path) -> None:
        """A channel configured with db_path creates the SQLite file."""
        db_file = tmp_path / "channel_replay.db"
        ch = SecureAgentChannel(
            shared_secret=secret,
            key_id="wire-v1",
            db_path=db_file,
        )
        env = ch.create_message(
            "Agent_A",
            {"action": "adjust_metric", "value": 10.0},
        )
        assert ch.verify_message(env).approved is True
        assert db_file.exists()

    def test_channel_persistence_across_instances(self, secret: bytes, tmp_path: Path) -> None:
        """Replay detection persists across instances sharing db_path."""
        db_file = tmp_path / "channel_persist.db"

        sender = SecureAgentChannel(
            shared_secret=secret,
            key_id="wire-v1",
            db_path=db_file,
        )
        env = sender.create_message(
            "Agent_A",
            {"action": "adjust_metric", "value": 10.0},
        )

        verifier1 = SecureAgentChannel(
            shared_secret=secret,
            key_id="wire-v1",
            db_path=db_file,
        )
        assert verifier1.verify_message(env).approved is True

        verifier2 = SecureAgentChannel(
            shared_secret=secret,
            key_id="wire-v1",
            db_path=db_file,
        )
        result = verifier2.verify_message(env)
        assert result.approved is False
        assert result.reason is ReasonCode.REPLAY_DETECTED

    def test_channel_default_db_path_isolated(self, secret: bytes) -> None:
        """Two default channels do not share replay state."""
        sender = SecureAgentChannel(shared_secret=secret, key_id="wire-v1")
        env = sender.create_message(
            "Agent_A",
            {"action": "adjust_metric", "value": 10.0},
        )

        ch1 = SecureAgentChannel(shared_secret=secret, key_id="wire-v1")
        ch2 = SecureAgentChannel(shared_secret=secret, key_id="wire-v1")

        assert ch1.verify_message(env).approved is True
        assert ch2.verify_message(env).approved is True


# ============================================================
# 10. Audit Logging — G5.2
# ============================================================


class TestAuditLogging:
    """Audit log integration with verify_message."""

    @pytest.fixture
    def audit_logger(self, tmp_path: Path) -> SecureAuditLog:
        return SecureAuditLog(
            log_path=tmp_path / "audit.enc",
            key=b"a" * 32,
        )

    @pytest.fixture
    def wired_channel(
        self,
        secret: bytes,
        audit_logger: SecureAuditLog,
    ) -> SecureAgentChannel:
        return SecureAgentChannel(
            shared_secret=secret,
            key_id="test-v1",
            allowed_senders=frozenset({"Agent_A", "Agent_B"}),
            audit_log=audit_logger,
        )

    def test_unknown_key_id_writes_audit(
        self,
        wired_channel: SecureAgentChannel,
        audit_logger: SecureAuditLog,
    ) -> None:
        envelope = Envelope(
            version="v1",
            key_id="unknown-v1",
            sender_id="Agent_A",
            timestamp=time.time(),
            nonce="a" * 32,
            payload={"x": 1},
            signature="b" * 64,
        )

        result = wired_channel.verify_message(envelope)

        assert result.approved is False
        events = audit_logger.read_all()
        assert len(events) == 1
        assert events[0].event_type == "verify_rejected"
        assert events[0].agent_id == "<unknown>"
        assert events[0].details["reason"] == "UNKNOWN_KEY_ID"
        assert events[0].details["key_id"] == "unknown-v1"

    def test_role_not_permitted_writes_audit(
        self,
        wired_channel: SecureAgentChannel,
        audit_logger: SecureAuditLog,
    ) -> None:
        envelope = Envelope(
            version="v1",
            key_id="test-v1",
            sender_id="Agent_X",
            timestamp=time.time(),
            nonce="a" * 32,
            payload={"x": 1},
            signature="b" * 64,
        )

        result = wired_channel.verify_message(envelope)

        assert result.approved is False
        events = audit_logger.read_all()
        assert len(events) == 1
        assert events[0].event_type == "verify_rejected"
        assert events[0].agent_id == "Agent_X"
        assert events[0].details["reason"] == "ROLE_NOT_PERMITTED"

    def test_timestamp_too_old_writes_audit(
        self,
        wired_channel: SecureAgentChannel,
        audit_logger: SecureAuditLog,
    ) -> None:
        envelope = Envelope(
            version="v1",
            key_id="test-v1",
            sender_id="Agent_A",
            timestamp=time.time() - 10_000.0,
            nonce="a" * 32,
            payload={"x": 1},
            signature="b" * 64,
        )

        result = wired_channel.verify_message(envelope)

        assert result.approved is False
        events = audit_logger.read_all()
        assert len(events) == 1
        assert events[0].agent_id == "Agent_A"
        assert events[0].details["reason"] == "TIMESTAMP_TOO_OLD"

    def test_timestamp_from_future_writes_audit(
        self,
        wired_channel: SecureAgentChannel,
        audit_logger: SecureAuditLog,
    ) -> None:
        envelope = Envelope(
            version="v1",
            key_id="test-v1",
            sender_id="Agent_A",
            timestamp=time.time() + 10_000.0,
            nonce="a" * 32,
            payload={"x": 1},
            signature="b" * 64,
        )

        result = wired_channel.verify_message(envelope)

        assert result.approved is False
        events = audit_logger.read_all()
        assert len(events) == 1
        assert events[0].agent_id == "Agent_A"
        assert events[0].details["reason"] == "TIMESTAMP_FROM_FUTURE"

    def test_replay_detected_writes_audit(
        self,
        wired_channel: SecureAgentChannel,
        audit_logger: SecureAuditLog,
    ) -> None:
        envelope = wired_channel.create_message("Agent_A", {"x": 1})
        first_result = wired_channel.verify_message(envelope)
        assert first_result.approved is True

        result = wired_channel.verify_message(envelope)
        assert result.approved is False

        events = audit_logger.read_all()
        assert len(events) == 1
        assert events[0].event_type == "verify_rejected"
        assert events[0].agent_id == "Agent_A"
        assert events[0].details["reason"] == "REPLAY_DETECTED"

    def test_invalid_signature_writes_audit(
        self,
        wired_channel: SecureAgentChannel,
        audit_logger: SecureAuditLog,
    ) -> None:
        envelope = Envelope(
            version="v1",
            key_id="test-v1",
            sender_id="Agent_A",
            timestamp=time.time(),
            nonce="d" * 32,
            payload={"x": 1},
            signature="c" * 64,
        )

        result = wired_channel.verify_message(envelope)

        assert result.approved is False
        events = audit_logger.read_all()
        assert len(events) == 1
        assert events[0].event_type == "verify_rejected"
        assert events[0].agent_id == "<unverified>"
        assert events[0].details["reason"] == "INVALID_SIGNATURE"

    def test_no_audit_log_silently_drops_rejection(
        self,
        secret: bytes,
    ) -> None:
        channel = SecureAgentChannel(
            shared_secret=secret,
            key_id="test-v1",
            allowed_senders=frozenset({"Agent_A"}),
            audit_log=None,
        )
        envelope = Envelope(
            version="v1",
            key_id="bad-v1",
            sender_id="Agent_A",
            timestamp=time.time(),
            nonce="e" * 32,
            payload={"x": 1},
            signature="b" * 64,
        )

        result = channel.verify_message(envelope)

        assert result.approved is False
