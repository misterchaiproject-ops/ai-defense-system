"""Tests for orchestrator.core.SecureOrchestrator."""

from __future__ import annotations

import dataclasses

import pytest

from channel import Envelope, SecureAgentChannel
from contracts import (
    Action,
    AgentIdentity,
    Proposal,
    ReasonCode,
    Role,
    ValidationResult,
)
from guardrail import DeterministicGuardrail
from orchestrator import SecureOrchestrator
from orchestrator.core import _reconstruct_proposal

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def secret() -> bytes:
    """32-byte shared secret for channel construction."""
    return b"x" * 32


@pytest.fixture
def channel(secret: bytes) -> SecureAgentChannel:
    """A ready-to-use SecureAgentChannel for tests."""
    return SecureAgentChannel(shared_secret=secret, key_id="test-v1")


@pytest.fixture
def limits() -> dict[str, float]:
    return {"cooling_system": 100.0, "main_valve": 100.0}


@pytest.fixture
def mins() -> dict[str, float]:
    return {"cooling_system": 0.0, "main_valve": 0.0}


@pytest.fixture
def guardrail(limits: dict[str, float], mins: dict[str, float]) -> DeterministicGuardrail:
    return DeterministicGuardrail(limits, min_values=mins)


@pytest.fixture
def admin() -> AgentIdentity:
    return AgentIdentity(agent_id="Admin_01", roles=frozenset({Role.ADMIN}))


@pytest.fixture
def orchestrator(
    channel: SecureAgentChannel, guardrail: DeterministicGuardrail
) -> SecureOrchestrator:
    return SecureOrchestrator(channel=channel, guardrail=guardrail)


# ============================================================
# TestSecureOrchestratorInit
# ============================================================


class TestSecureOrchestratorInit:
    """Test SecureOrchestrator constructor validation."""

    def test_rejects_invalid_channel_type(self, guardrail: DeterministicGuardrail) -> None:
        """Constructor must reject non-SecureAgentChannel channel."""
        with pytest.raises(TypeError, match="channel must be a SecureAgentChannel"):
            SecureOrchestrator(channel="not_a_channel", guardrail=guardrail)  # type: ignore[arg-type]

    def test_rejects_invalid_guardrail_type(self, channel: SecureAgentChannel) -> None:
        """Constructor must reject non-DeterministicGuardrail guardrail."""
        with pytest.raises(TypeError, match="guardrail must be a DeterministicGuardrail"):
            SecureOrchestrator(channel=channel, guardrail="not_a_guardrail")  # type: ignore[arg-type]

    def test_accepts_valid_channel_and_guardrail(
        self, channel: SecureAgentChannel, guardrail: DeterministicGuardrail
    ) -> None:
        """Constructor must accept valid channel and guardrail."""
        orch = SecureOrchestrator(channel=channel, guardrail=guardrail)
        assert orch is not None


# ============================================================
# TestReconstructProposal
# ============================================================


class TestReconstructProposal:
    """Test _reconstruct_proposal helper validation."""

    def test_rejects_non_mapping_payload(self) -> None:
        """Must reject non-Mapping payload."""
        with pytest.raises(TypeError, match="payload must be a Mapping"):
            _reconstruct_proposal("not a mapping")  # type: ignore[arg-type]

    def test_rejects_non_string_action(self) -> None:
        """Must reject payload with non-string action."""
        with pytest.raises(ValueError, match="action must be a string"):
            _reconstruct_proposal({"action": 123, "target": "t", "value": 1.0})

    def test_rejects_non_string_target(self) -> None:
        """Must reject payload with non-string target."""
        with pytest.raises(ValueError, match="target must be a string"):
            _reconstruct_proposal({"action": "adjust_metric", "target": 123, "value": 1.0})

    def test_rejects_unknown_action(self) -> None:
        """Must reject payload with unknown action value."""
        with pytest.raises(ValueError, match="unknown action"):
            _reconstruct_proposal(
                {"action": "not_an_action", "target": "cooling_system", "value": 50.0}
            )

    def test_accepts_valid_payload(self) -> None:
        """Must accept valid payload and return Proposal."""
        result = _reconstruct_proposal(
            {"action": "adjust_metric", "target": "cooling_system", "value": 50.0}
        )
        assert isinstance(result, Proposal)
        assert result.action is Action.ADJUST_METRIC
        assert result.target == "cooling_system"
        assert result.value == 50.0


# ============================================================
# TestProcessOutbound
# ============================================================


class TestProcessOutbound:
    """Test process_outbound behavior (fail-closed on guardrail rejection)."""

    def test_returns_none_when_guardrail_rejects(
        self, orchestrator: SecureOrchestrator, admin: AgentIdentity
    ) -> None:
        """Guardrail rejection must return None."""
        proposal = Proposal(
            action=Action.ADJUST_METRIC,
            target="cooling_system",
            value=150.0,
        )
        result = orchestrator.process_outbound(proposal, admin)
        assert result is None

    def test_returns_envelope_when_guardrail_approves(
        self, orchestrator: SecureOrchestrator, admin: AgentIdentity
    ) -> None:
        """Approved proposal must return an Envelope."""
        proposal = Proposal(
            action=Action.ADJUST_METRIC,
            target="cooling_system",
            value=50.0,
        )
        envelope = orchestrator.process_outbound(proposal, admin)
        assert isinstance(envelope, Envelope)
        assert envelope.sender_id == admin.agent_id

    def test_returns_none_when_signing_fails(
        self,
        orchestrator: SecureOrchestrator,
        admin: AgentIdentity,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Signing failure must return None (fail-closed)."""
        proposal = Proposal(
            action=Action.ADJUST_METRIC,
            target="cooling_system",
            value=50.0,
        )

        def broken_create_message(*args: object, **kwargs: object) -> None:
            raise RuntimeError("Simulated signing failure")

        monkeypatch.setattr(orchestrator._channel, "create_message", broken_create_message)
        result = orchestrator.process_outbound(proposal, admin)
        assert result is None

    def test_payload_matches_proposal(
        self, orchestrator: SecureOrchestrator, admin: AgentIdentity
    ) -> None:
        """Envelope payload must match the original proposal (TOCTOU-safe)."""
        proposal = Proposal(
            action=Action.ADJUST_METRIC,
            target="cooling_system",
            value=75.0,
        )
        envelope = orchestrator.process_outbound(proposal, admin)
        assert isinstance(envelope, Envelope)
        assert dict(envelope.payload) == proposal.to_payload()


# ============================================================
# TestProcessInbound
# ============================================================


class TestProcessInbound:
    """Test process_inbound: channel verify -> reconstruct -> guardrail."""

    def test_returns_rejection_when_channel_rejects(
        self, orchestrator: SecureOrchestrator, admin: AgentIdentity
    ) -> None:
        """A rejected envelope must return the channel's rejection result."""
        payload = {"action": "adjust_metric", "target": "cooling_system", "value": 50.0}
        valid = orchestrator._channel.create_message(admin.agent_id, payload)
        # Tamper with the signature to force channel rejection
        tampered = dataclasses.replace(valid, signature="0" * 64)
        result = orchestrator.process_inbound(tampered, admin)
        assert isinstance(result, ValidationResult)
        assert result.approved is False

    def test_returns_malformed_payload_on_bad_data(
        self,
        orchestrator: SecureOrchestrator,
        admin: AgentIdentity,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Malformed payload must return MALFORMED_PAYLOAD."""
        envelope = orchestrator._channel.create_message(admin.agent_id, {"x": 1})

        def broken_reconstruct(payload: object) -> None:
            raise ValueError("Simulated malformed")

        monkeypatch.setattr("orchestrator.core._reconstruct_proposal", broken_reconstruct)
        result = orchestrator.process_inbound(envelope, admin)
        assert isinstance(result, ValidationResult)
        assert result.reason is ReasonCode.MALFORMED_PAYLOAD

    def test_returns_guardrail_rejection_on_policy_violation(
        self, orchestrator: SecureOrchestrator, admin: AgentIdentity
    ) -> None:
        """Guardrail rejection must be returned as ValidationResult."""
        payload = {
            "action": "adjust_metric",
            "target": "cooling_system",
            "value": 999.0,
        }
        envelope = orchestrator._channel.create_message(admin.agent_id, payload)
        result = orchestrator.process_inbound(envelope, admin)
        assert isinstance(result, ValidationResult)
        assert result.approved is False

    def test_returns_guardrail_approval_on_valid_proposal(
        self, orchestrator: SecureOrchestrator, admin: AgentIdentity
    ) -> None:
        """Valid proposal must pass all layers and return approval."""
        payload = {
            "action": "adjust_metric",
            "target": "cooling_system",
            "value": 50.0,
        }
        envelope = orchestrator._channel.create_message(admin.agent_id, payload)
        result = orchestrator.process_inbound(envelope, admin)
        assert isinstance(result, ValidationResult)
        assert result.approved is True
