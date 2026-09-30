"""
Smoke tests: verify imports and basic flow.

If these pass, the foundation is solid. If they fail, we know exactly
where to look — before writing deeper tests.
"""

from __future__ import annotations

import pytest

from channel import Envelope, SecureAgentChannel, generate_shared_secret
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


# ---------------------------------------------------------------------------
# Test: imports work
# ---------------------------------------------------------------------------

def test_imports_ok() -> None:
    """All public APIs must be importable."""
    assert Action is not None
    assert Role is not None
    assert Proposal is not None
    assert AgentIdentity is not None
    assert ReasonCode is not None
    assert ValidationResult is not None
    assert DeterministicGuardrail is not None
    assert SecureAgentChannel is not None
    assert Envelope is not None
    assert SecureOrchestrator is not None
    assert generate_shared_secret is not None


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def guardrail() -> DeterministicGuardrail:
    return DeterministicGuardrail(
        operational_limits={
            "cooling_system": 75.0,
            "main_valve": 100.0,
        },
        min_values={
            "cooling_system": 0.0,
            "main_valve": 0.0,
        },
    )


@pytest.fixture
def channel() -> SecureAgentChannel:
    return SecureAgentChannel(
        shared_secret=generate_shared_secret(),
        key_id="test-v1",
        allowed_senders=frozenset({"Agent_A"}),
    )


@pytest.fixture
def orchestrator(
    guardrail: DeterministicGuardrail, channel: SecureAgentChannel
) -> SecureOrchestrator:
    return SecureOrchestrator(channel=channel, guardrail=guardrail)


@pytest.fixture
def admin() -> AgentIdentity:
    return AgentIdentity(
        agent_id="Agent_A",
        roles=frozenset({Role.ADMIN}),
    )


@pytest.fixture
def observer() -> AgentIdentity:
    return AgentIdentity(
        agent_id="Agent_A",
        roles=frozenset({Role.OBSERVER}),
    )


# ---------------------------------------------------------------------------
# Test: Proposal + AgentIdentity
# ---------------------------------------------------------------------------

def test_proposal_creation() -> None:
    p = Proposal(action=Action.ADJUST_METRIC, target="cooling_system", value=60.0)
    assert p.action is Action.ADJUST_METRIC
    assert p.target == "cooling_system"
    assert p.value == 60.0
    assert p.to_payload() == {
        "action": "adjust_metric",
        "target": "cooling_system",
        "value": 60.0,
    }


def test_proposal_rejects_nan() -> None:
    with pytest.raises(ValueError):
        Proposal(
            action=Action.ADJUST_METRIC,
            target="cooling_system",
            value=float("nan"),
        )


def test_agent_identity_basic() -> None:
    ident = AgentIdentity(agent_id="Agent_X", roles=frozenset({Role.ADMIN}))
    assert ident.has_role(Role.ADMIN)
    assert not ident.has_role(Role.OBSERVER)


# ---------------------------------------------------------------------------
# Test: Guardrail
# ---------------------------------------------------------------------------

def test_guardrail_accepts_valid(
    guardrail: DeterministicGuardrail, admin: AgentIdentity
) -> None:
    p = Proposal(action=Action.ADJUST_METRIC, target="cooling_system", value=60.0)
    result = guardrail.validate(p, admin)
    assert result.approved is True
    assert result.reason is ReasonCode.OK


def test_guardrail_rejects_unknown_target(
    guardrail: DeterministicGuardrail, admin: AgentIdentity
) -> None:
    p = Proposal(action=Action.ADJUST_METRIC, target="unknown", value=50.0)
    result = guardrail.validate(p, admin)
    assert result.approved is False
    assert result.reason is ReasonCode.TARGET_NOT_ALLOWED


def test_guardrail_rejects_rbac(
    guardrail: DeterministicGuardrail, observer: AgentIdentity
) -> None:
    p = Proposal(action=Action.ADJUST_METRIC, target="cooling_system", value=60.0)
    result = guardrail.validate(p, observer)
    assert result.approved is False
    assert result.reason is ReasonCode.ROLE_NOT_PERMITTED


def test_guardrail_rejects_above_limit(
    guardrail: DeterministicGuardrail, admin: AgentIdentity
) -> None:
    p = Proposal(action=Action.ADJUST_METRIC, target="cooling_system", value=999.0)
    result = guardrail.validate(p, admin)
    assert result.approved is False
    assert result.reason is ReasonCode.VALUE_EXCEEDS_LIMIT


# ---------------------------------------------------------------------------
# Test: Channel
# ---------------------------------------------------------------------------

def test_channel_round_trip(channel: SecureAgentChannel) -> None:
    env = channel.create_message("Agent_A", {"x": 1})
    result = channel.verify_message(env)
    assert result.approved is True


def test_channel_rejects_replay(channel: SecureAgentChannel) -> None:
    env = channel.create_message("Agent_A", {"x": 1})
    assert channel.verify_message(env).approved is True
    # Second delivery: rejected
    result = channel.verify_message(env)
    assert result.approved is False
    assert result.reason is ReasonCode.REPLAY_DETECTED


# ---------------------------------------------------------------------------
# Test: Orchestrator — end-to-end
# ---------------------------------------------------------------------------

def test_orchestrator_full_round_trip(
    orchestrator: SecureOrchestrator, admin: AgentIdentity
) -> None:
    p = Proposal(
        action=Action.ADJUST_METRIC, target="cooling_system", value=60.0
    )
    envelope = orchestrator.process_outbound(p, admin)
    assert envelope is not None

    result = orchestrator.process_inbound(envelope, admin)
    assert result.approved is True
    assert result.reason is ReasonCode.OK


def test_orchestrator_rejects_at_outbound(
    orchestrator: SecureOrchestrator, observer: AgentIdentity
) -> None:
    p = Proposal(
        action=Action.ADJUST_METRIC, target="cooling_system", value=60.0
    )
    envelope = orchestrator.process_outbound(p, observer)
    assert envelope is None


def test_orchestrator_enforces_guardrail_inbound(
    orchestrator: SecureOrchestrator,
    admin: AgentIdentity,
    observer: AgentIdentity,
) -> None:
    """
    AP-033 test: a valid signature does not bypass Guardrail.

    Send a SHUTDOWN proposal signed by admin, then verify with an
    observer identity — inbound Guardrail must reject.
    """
    p = Proposal(
        action=Action.SHUTDOWN, target="cooling_system", value=0.0
    )
    envelope = orchestrator.process_outbound(p, admin)
    assert envelope is not None

    result = orchestrator.process_inbound(envelope, observer)
    assert result.approved is False
    assert result.reason is ReasonCode.ROLE_NOT_PERMITTED
