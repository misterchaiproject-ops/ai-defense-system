"""Security regression tests for replay-cache retention semantics.

These tests intentionally assert security invariants. On the current implementation,
the eviction test is expected to fail until the replay-retention design is corrected.
No production code is changed by this file.
"""

from __future__ import annotations

from channel.core import SecureAgentChannel, generate_shared_secret
from contracts import ReasonCode


def test_evicted_nonce_cannot_be_accepted_again_before_message_expiry() -> None:
    """A valid message must not become replayable merely because the cache is full."""
    channel = SecureAgentChannel(
        shared_secret=generate_shared_secret(),
        key_id="test-v1",
        allowed_senders=frozenset({"Agent_A"}),
    )
    # Keep the test small and deterministic: one accepted nonce is evicted by the next.
    channel._replay._max = 1

    first = channel.create_message("Agent_A", {"action": "first"})
    second = channel.create_message("Agent_A", {"action": "second"})

    first_result = channel.verify_message(first)
    assert first_result.approved is True
    assert first_result.reason is ReasonCode.OK

    second_result = channel.verify_message(second)
    assert second_result.approved is True
    assert second_result.reason is ReasonCode.OK

    # Both messages are freshly signed and within the 300-second validity window.
    # Security invariant: eviction must not silently make the first nonce reusable.
    replay_result = channel.verify_message(first)
    assert replay_result.approved is False
    assert replay_result.reason is ReasonCode.REPLAY_DETECTED
