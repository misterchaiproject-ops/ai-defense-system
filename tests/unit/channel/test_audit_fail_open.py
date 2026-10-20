from unittest.mock import MagicMock

import pytest

from src.audit.core import SecureAuditLog
from src.channel.core import Envelope, SecureAgentChannel


def test_write_audit_fails_open_on_error(tmp_path):
    # 1. إعداد قناة آمنة
    dummy_secret = b"0" * 32
    dummy_key_id = "test_key_001"
    channel = SecureAgentChannel(shared_secret=dummy_secret, key_id=dummy_key_id)

    # 2. إعداد سجل تدقيق وهمي يفشل عند الكتابة
    failing_audit_log = MagicMock(spec=SecureAuditLog)
    failing_audit_log.append.side_effect = Exception("Disk Full (Simulated)")
    channel._audit_log = failing_audit_log

    # 3. محاولة الكتابة (يجب أن تفشل بصمت حالياً - Fail-Open)
    # نستخدم envelope وهمي
    dummy_envelope = MagicMock(spec=Envelope)

    # هذا هو الاختبار: يجب ألا يرفع استثناء (لأنه Best-effort)
    try:
        channel._write_audit(envelope=dummy_envelope, reason="TEST", agent_id="agent_1")
    except Exception as e:
        pytest.fail(f"Audit write should have failed silently, but raised: {e}")

    # إذا وصلنا هنا، فهذا يثبت الثغرة (Fail-Open)
    print("VULNERABILITY CONFIRMED: Audit write failed silently (Fail-Open)")
