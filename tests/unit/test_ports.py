"""Tests for the stable extensibility boundaries introduced in Phase 1."""

from __future__ import annotations

from pathlib import Path

from audit import AuditEvent, SecureAuditLog
from channel.core import _ReplayCache
from ports import AuditSink, Clock, KeyProvider, ReplayStore


class _FakeClock:
    def now(self) -> float:
        return 1_700_000_000.0


class _FakeKeyProvider:
    def get_key(self, key_id: str) -> bytes | None:
        return b"x" * 32 if key_id == "active" else None

    def get_active_key_id(self) -> str:
        return "active"


def test_secure_audit_log_implements_audit_sink(tmp_path: Path) -> None:
    audit_log = SecureAuditLog(tmp_path / "audit.log", b"k" * 32)

    assert isinstance(audit_log, AuditSink)


def test_replay_cache_implements_replay_store() -> None:
    replay_store = _ReplayCache(max_size=8)

    assert isinstance(replay_store, ReplayStore)


def test_fake_clock_implements_clock() -> None:
    assert isinstance(_FakeClock(), Clock)


def test_fake_key_provider_implements_key_provider() -> None:
    provider = _FakeKeyProvider()

    assert isinstance(provider, KeyProvider)
    assert provider.get_key("active") == b"x" * 32
    assert provider.get_key("missing") is None
    assert provider.get_active_key_id() == "active"


def test_audit_sink_contract_accepts_audit_event(tmp_path: Path) -> None:
    audit_log = SecureAuditLog(tmp_path / "audit.log", b"k" * 32)
    sink: AuditSink = audit_log

    sink.append(
        AuditEvent(
            event_type="test",
            timestamp=1.0,
            agent_id="agent-1",
            details={"phase": 1},
        )
    )

    assert audit_log.read_all()[0].event_type == "test"
