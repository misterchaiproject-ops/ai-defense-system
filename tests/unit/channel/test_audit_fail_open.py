"""Security regression tests for audit fail-closed behavior."""

from __future__ import annotations

import dataclasses
import time
from collections.abc import Callable
from unittest.mock import MagicMock, patch

import pytest

from audit import SecureAuditLog
from channel.core import Envelope, SecureAgentChannel
from channel.exceptions import AuditWriteError
from contracts import ReasonCode


def _failing_audit_log() -> MagicMock:
    audit_log = MagicMock(spec=SecureAuditLog)
    audit_log.append.side_effect = OSError("Disk Full (Simulated)")
    return audit_log


def _channel() -> SecureAgentChannel:
    return SecureAgentChannel(shared_secret=b"0" * 32, key_id="test-v1")


def test_write_audit_raises_audit_write_error() -> None:
    channel = _channel()
    channel._audit_log = _failing_audit_log()
    envelope = channel.create_message("Agent_A", {"x": 1})

    with pytest.raises(AuditWriteError):
        channel._write_audit(envelope, ReasonCode.INVALID_SIGNATURE, "<unverified>")


@pytest.mark.parametrize(
    ("reason", "make_envelope"),
    [
        (
            ReasonCode.UNKNOWN_KEY_ID,
            lambda channel: dataclasses.replace(
                channel.create_message("Agent_A", {"x": 1}),
                key_id="unknown-v1",
            ),
        ),
        (
            ReasonCode.ROLE_NOT_PERMITTED,
            lambda channel: channel.create_message("Agent_A", {"x": 1}),
        ),
        (
            ReasonCode.TIMESTAMP_TOO_OLD,
            lambda channel: dataclasses.replace(
                channel.create_message("Agent_A", {"x": 1}),
                timestamp=time.time() - 301,
            ),
        ),
        (
            ReasonCode.TIMESTAMP_FROM_FUTURE,
            lambda channel: dataclasses.replace(
                channel.create_message("Agent_A", {"x": 1}),
                timestamp=time.time() + 2,
            ),
        ),
        (
            ReasonCode.INVALID_SIGNATURE,
            lambda channel: dataclasses.replace(
                channel.create_message("Agent_A", {"x": 1}),
                signature="0" * 64,
            ),
        ),
    ],
)
def test_security_rejection_fails_closed_on_audit_error(
    reason: ReasonCode,
    make_envelope: Callable[[SecureAgentChannel], Envelope],
) -> None:
    channel = _channel()
    if reason is ReasonCode.ROLE_NOT_PERMITTED:
        channel = SecureAgentChannel(
            shared_secret=b"0" * 32,
            key_id="test-v1",
            allowed_senders=frozenset({"Agent_B"}),
        )
    channel._audit_log = _failing_audit_log()

    envelope = make_envelope(channel)
    result = channel.verify_message(envelope)

    assert result.approved is False
    assert result.reason is ReasonCode.AUDIT_FAILURE


def test_replay_rejection_fails_closed_on_audit_error() -> None:
    channel = _channel()
    channel._audit_log = _failing_audit_log()
    envelope = channel.create_message("Agent_A", {"x": 1})

    first_result = channel.verify_message(envelope)
    assert first_result.approved is True
    assert first_result.reason is ReasonCode.OK

    replay_result = channel.verify_message(envelope)
    assert replay_result.approved is False
    assert replay_result.reason is ReasonCode.AUDIT_FAILURE


def test_security_rejection_preserves_original_reason_when_audit_succeeds() -> None:
    channel = _channel()
    audit_log = MagicMock(spec=SecureAuditLog)
    channel._audit_log = audit_log
    envelope = dataclasses.replace(
        channel.create_message("Agent_A", {"x": 1}),
        signature="0" * 64,
    )

    result = channel.verify_message(envelope)

    assert result.approved is False
    assert result.reason is ReasonCode.INVALID_SIGNATURE
    audit_log.append.assert_called_once()


def test_unrelated_exception_remains_internal_error() -> None:
    channel = _channel()
    envelope = channel.create_message("Agent_A", {"x": 1})
    with patch.object(
        channel,
        "_canonicalize",
        MagicMock(side_effect=RuntimeError("unexpected internal error")),
    ):
        result = channel.verify_message(envelope)

    assert result.approved is False
    assert result.reason is ReasonCode.INTERNAL_ERROR


def test_audit_failure_never_returns_ok() -> None:
    channel = _channel()
    channel._audit_log = _failing_audit_log()
    envelope = dataclasses.replace(
        channel.create_message("Agent_A", {"x": 1}),
        signature="0" * 64,
    )

    result = channel.verify_message(envelope)

    assert result.reason is not ReasonCode.OK
    assert result.approved is False
