from __future__ import annotations

from dataclasses import dataclass

import pytest

from channel.core import SecureAgentChannel
from ports import AuditSink, Clock, KeyProvider, ReplayStore


class FakeClock:
    def __init__(self, value: float) -> None:
        self.value = value

    def now(self) -> float:
        return self.value


class FakeReplayStore:
    def __init__(self) -> None:
        self.seen: set[str] = set()

    def check_and_add(self, nonce: str) -> bool:
        if nonce in self.seen:
            return False
        self.seen.add(nonce)
        return True


class FakeKeyProvider:
    def __init__(self, key_id: str, secret: bytes) -> None:
        self.key_id = key_id
        self.secret = secret

    def get_key(self, key_id: str) -> bytes | None:
        return self.secret if key_id == self.key_id else None

    def get_active_key_id(self) -> str:
        return self.key_id


class ShortKeyProvider(FakeKeyProvider):
    pass


class NonBytesKeyProvider:
    def get_key(self, key_id: str) -> bytes | None:
        return "not-a-key"  # type: ignore[return-value]

    def get_active_key_id(self) -> str:
        return "managed"


@dataclass
class FakeAuditSink:
    events: list[object]

    def append(self, event: object) -> None:
        self.events.append(event)


def test_injected_clock_and_replay_store_control_runtime() -> None:
    clock = FakeClock(1_000.0)
    replay = FakeReplayStore()
    channel = SecureAgentChannel(
        key_ring={"k1": b"s" * 32},
        active_key_id="k1",
        clock=clock,
        replay_store=replay,
    )

    envelope = channel.create_message("agent-1", {"action": "read"})

    assert envelope.timestamp == 1_000.0
    assert channel.verify_message(envelope).approved is True
    assert channel.verify_message(envelope).approved is False


def test_injected_key_provider_is_used_for_signing_and_verification() -> None:
    provider = FakeKeyProvider("managed", b"k" * 32)
    channel = SecureAgentChannel(key_provider=provider)

    envelope = channel.create_message("agent-1", {"action": "read"})

    assert envelope.key_id == "managed"
    assert channel.verify_message(envelope).approved is True


def test_short_injected_key_is_rejected_at_crypto_boundary() -> None:
    provider = ShortKeyProvider("managed", b"k" * 31)
    channel = SecureAgentChannel(key_provider=provider)

    with pytest.raises(ValueError, match="shorter than 32 bytes"):
        channel.create_message("agent-1", {"action": "read"})


def test_non_bytes_injected_key_is_rejected_at_crypto_boundary() -> None:
    channel = SecureAgentChannel(key_provider=NonBytesKeyProvider())

    with pytest.raises(TypeError, match="non-bytes key"):
        channel.create_message("agent-1", {"action": "read"})


def test_injected_audit_sink_receives_security_event() -> None:
    sink = FakeAuditSink([])
    channel = SecureAgentChannel(
        key_ring={"k1": b"s" * 32},
        active_key_id="k1",
        audit_log=sink,
    )

    envelope = channel.create_message("agent-1", {"action": "read"})
    envelope = type(envelope)(
        version=envelope.version,
        key_id=envelope.key_id,
        sender_id=envelope.sender_id,
        timestamp=envelope.timestamp,
        nonce=envelope.nonce,
        payload=envelope.payload,
        signature="0" * 64,
    )

    result = channel.verify_message(envelope)

    assert result.approved is False
    assert len(sink.events) == 1


def test_legacy_constructor_remains_compatible() -> None:
    channel = SecureAgentChannel(shared_secret=b"k" * 32, key_id="legacy")
    envelope = channel.create_message("agent-1", {"action": "read"})

    assert channel.verify_message(envelope).approved is True


def test_dependency_ports_are_runtime_contracts() -> None:
    assert isinstance(FakeClock(0.0), Clock)
    assert isinstance(FakeReplayStore(), ReplayStore)
    assert isinstance(FakeKeyProvider("k1", b"k" * 32), KeyProvider)
    assert isinstance(FakeAuditSink([]), AuditSink)
