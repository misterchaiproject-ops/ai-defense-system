import pytest
from unittest.mock import MagicMock
from src.channel.core import SecureAgentChannel, Envelope
from src.channel.exceptions import AuditWriteError
from src.audit.core import SecureAuditLog
from src.contracts.reason_codes import ReasonCode

def test_audit_failure_returns_audit_failure_reason(tmp_path):
    """Invariant 2 & 3: Audit failure -> reject with AUDIT_FAILURE."""
    dummy_secret = b"0" * 32
    channel = SecureAgentChannel(shared_secret=dummy_secret, key_id="test_key")
    
    failing_audit_log = MagicMock(spec=SecureAuditLog)
    failing_audit_log.append.side_effect = Exception("Disk Full")
    channel._audit_log = failing_audit_log

    envelope = MagicMock(spec=Envelope)
    
    result = channel.verify_message(envelope)
    
    assert result.approved is False
    assert result.reason == ReasonCode.AUDIT_FAILURE

def test_write_audit_raises_audit_write_error(tmp_path):
    """T9: _write_audit itself raises AuditWriteError on failure."""
    dummy_secret = b"0" * 32
    channel = SecureAgentChannel(shared_secret=dummy_secret, key_id="test_key")
    
    failing_audit_log = MagicMock(spec=SecureAuditLog)
    failing_audit_log.append.side_effect = Exception("Disk Full")
    channel._audit_log = failing_audit_log

    envelope = MagicMock(spec=Envelope)
    envelope.key_id = "key"
    envelope.sender_id = "sender"
    envelope.nonce = "nonce"
    envelope.timestamp = 123.0
    envelope.version = "1.0"

    with pytest.raises(AuditWriteError, match="Security audit write failed"):
        channel._write_audit(envelope, ReasonCode.REPLAY_DETECTED, "sender")

def test_audit_event_type_uses_reason_value(tmp_path):
    """T10: event_type == reason.value."""
    dummy_secret = b"0" * 32
    channel = SecureAgentChannel(shared_secret=dummy_secret, key_id="test_key")
    
    mock_audit_log = MagicMock(spec=SecureAuditLog)
    channel._audit_log = mock_audit_log

    envelope = MagicMock(spec=Envelope)
    envelope.key_id = "key"
    envelope.sender_id = "sender"
    envelope.nonce = "nonce"
    envelope.timestamp = 123.0
    envelope.version = "1.0"

    channel._write_audit(envelope, ReasonCode.REPLAY_DETECTED, "sender")
    
    args, kwargs = mock_audit_log.append.call_args
    event = args[0]
    assert event.event_type == "REPLAY_DETECTED"
