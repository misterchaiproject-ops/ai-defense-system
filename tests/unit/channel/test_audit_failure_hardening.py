"""Security tests for audit failure handling in SecureAgentChannel."""

from __future__ import annotations

import time

import pytest

from audit import AuditEvent
from channel.core import Envelope, SecureAgentChannel
from contracts import ReasonCode


class FailingAuditLog:
    """Audit sink that deterministically fails writes."""

    def append(self, event: AuditEvent) -> None:
        raise OSError("simulated audit storage failure")


@pytest.fixture
def channel_with_failing_audit() -> SecureAgentChannel:
    """Channel with an enabled audit sink that cannot persist events."""
    return SecureAgentChannel(
        shared_secret=b"s" * 32,
        key_id="test-v1",
        allowed_senders=frozenset({"Agent_A"}),
        audit_log=FailingAuditLog(),
    )


def test_audit_failure_is_not_silent_for_unknown_key(
    channel_with_failing_audit: SecureAgentChannel,
) -> None:
    """A configured audit failure must become an explicit internal security failure."""
    envelope = Envelope(
        version="v1",
        key_id="unknown-v1",
        sender_id="Agent_A",
        timestamp=time.time(),
        nonce="a" * 32,
        payload={"x": 1},
        signature="b" * 64,
    )

    result = channel_with_failing_audit.verify_message(envelope)

    assert result.approved is False
    assert result.reason is ReasonCode.INTERNAL_ERROR


def test_audit_failure_is_not_silent_for_invalid_signature(
    channel_with_failing_audit: SecureAgentChannel,
) -> None:
    """A configured audit failure must not silently return the primary rejection."""
    envelope = Envelope(
        version="v1",
        key_id="test-v1",
        sender_id="Agent_A",
        timestamp=time.time(),
        nonce="b" * 32,
        payload={"x": 1},
        signature="c" * 64,
    )

    result = channel_with_failing_audit.verify_message(envelope)

    assert result.approved is False
    assert result.reason is ReasonCode.INTERNAL_ERROR


def test_disabled_audit_remains_supported() -> None:
    """No configured audit sink is an explicit disabled mode, not a write failure."""
    channel = SecureAgentChannel(
        shared_secret=b"s" * 32,
        key_id="test-v1",
        allowed_senders=frozenset({"Agent_A"}),
        audit_log=None,
    )
    envelope = Envelope(
        version="v1",
        key_id="unknown-v1",
        sender_id="Agent_A",
        timestamp=time.time(),
        nonce="c" * 32,
        payload={"x": 1},
        signature="b" * 64,
    )

    result = channel.verify_message(envelope)

    assert result.approved is False
    assert result.reason is ReasonCode.UNKNOWN_KEY_ID
