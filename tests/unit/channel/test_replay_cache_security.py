"""Security regression tests for replay-cache retention and SQLite sharing.

These tests intentionally assert security invariants. The eviction test is expected
to fail on the current bounded FIFO implementation. The independent-connection test
checks concurrent duplicate reservation against one SQLite file; any exception or
duplicate acceptance is a failure requiring investigation. No production code changes.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

from channel.core import SecureAgentChannel, _ReplayCache, generate_shared_secret
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


def test_independent_sqlite_connections_do_not_accept_same_nonce_twice(
    tmp_path: Path,
) -> None:
    """Two cache objects sharing a database must reserve a nonce only once."""
    database = tmp_path / "replay-cache.sqlite3"
    first_cache = _ReplayCache(max_size=100, db_path=database)
    second_cache = _ReplayCache(max_size=100, db_path=database)

    start = Barrier(2)

    def reserve(cache: _ReplayCache) -> bool:
        start.wait(timeout=5)
        return cache.check_and_add("a" * 32)

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(reserve, (first_cache, second_cache)))
    finally:
        first_cache._conn.close()
        second_cache._conn.close()

    # One caller should reserve the nonce; the other must report it as a replay.
    assert sorted(outcomes) == [False, True]
