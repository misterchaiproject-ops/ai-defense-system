"""Security regression tests for replay-cache retention and SQLite sharing.

These tests assert that unexpired nonces are not evicted, invalid signatures cannot
poison nonce state, and independent SQLite connections reserve each nonce atomically.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import sqlite3
from pathlib import Path
from threading import Barrier

from channel.core import SecureAgentChannel, _ReplayCache, generate_shared_secret
from contracts import ReasonCode


def test_cache_capacity_does_not_evict_unexpired_nonce() -> None:
    """A full cache must fail closed rather than make an accepted message replayable."""
    channel = SecureAgentChannel(
        shared_secret=generate_shared_secret(),
        key_id="test-v1",
        allowed_senders=frozenset({"Agent_A"}),
    )
    channel._replay._max = 2

    first = channel.create_message("Agent_A", {"action": "first"})
    second = channel.create_message("Agent_A", {"action": "second"})
    third = channel.create_message("Agent_A", {"action": "third"})

    for envelope in (first, second):
        result = channel.verify_message(envelope)
        assert result.approved is True
        assert result.reason is ReasonCode.OK

    full_result = channel.verify_message(third)
    assert full_result.approved is False
    assert full_result.reason is ReasonCode.INTERNAL_ERROR

    # The first active nonce remains recorded even though the cache is full.
    replay_result = channel.verify_message(first)
    assert replay_result.approved is False
    assert replay_result.reason is ReasonCode.REPLAY_DETECTED


def test_invalid_signature_does_not_poison_legitimate_nonce() -> None:
    """Unauthenticated input must not reserve a nonce before signature validation."""
    from dataclasses import replace

    channel = SecureAgentChannel(
        shared_secret=generate_shared_secret(),
        key_id="test-v1",
        allowed_senders=frozenset({"Agent_A"}),
    )
    envelope = channel.create_message("Agent_A", {"action": "legitimate"})
    replacement_char = "0" if envelope.signature[0] != "0" else "1"
    tampered = replace(
        envelope,
        signature=replacement_char + envelope.signature[1:],
    )

    invalid_result = channel.verify_message(tampered)
    assert invalid_result.approved is False
    assert invalid_result.reason is ReasonCode.INVALID_SIGNATURE

    legitimate_result = channel.verify_message(envelope)
    assert legitimate_result.approved is True
    assert legitimate_result.reason is ReasonCode.OK


def test_nonce_retention_uses_maximum_protocol_window_for_shared_database(
    tmp_path: Path,
) -> None:
    """A short-window verifier must not expire nonces for longer-window peers."""
    database = tmp_path / "shared-replay-cache.sqlite3"
    channel = SecureAgentChannel(
        shared_secret=generate_shared_secret(),
        key_id="test-v1",
        allowed_senders=frozenset({"Agent_A"}),
        max_delay_seconds=30,
        db_path=database,
    )
    envelope = channel.create_message("Agent_A", {"action": "shared-window"})
    result = channel.verify_message(envelope)
    assert result.approved is True

    connection = sqlite3.connect(database)
    try:
        row = connection.execute(
            "SELECT expires_at FROM seen_nonces WHERE nonce = ?",
            (envelope.nonce,),
        ).fetchone()
    finally:
        connection.close()

    assert row is not None
    assert row[0] == envelope.timestamp + 300.0


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
