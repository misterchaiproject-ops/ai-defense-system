"""Comprehensive test suite for guardrail.core.DeterministicGuardrail."""

from __future__ import annotations

from types import MappingProxyType

import pytest

from contracts import (
    Action,
    AgentIdentity,
    Proposal,
    ReasonCode,
    Role,
)
from guardrail.core import DeterministicGuardrail

# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def limits() -> dict[str, float]:
    return {"cooling_system": 75.0, "main_valve": 100.0}


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
def observer() -> AgentIdentity:
    return AgentIdentity(agent_id="Obs_01", roles=frozenset({Role.OBSERVER}))


@pytest.fixture
def operator() -> AgentIdentity:
    return AgentIdentity(agent_id="Op_01", roles=frozenset({Role.OPERATOR}))


@pytest.fixture
def supervisor() -> AgentIdentity:
    return AgentIdentity(agent_id="Sup_01", roles=frozenset({Role.SUPERVISOR}))


# ===========================================================================
# 1. Constructor — 6 tests
# ===========================================================================


class TestGuardrailConstructor:
    """Initialization and validation of limits."""

    def test_valid_construction(self, limits: dict[str, float]) -> None:
        g = DeterministicGuardrail(limits)
        assert "cooling_system" in g._limits

    def test_rejects_empty_limits(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            DeterministicGuardrail({})

    def test_rejects_non_mapping_limits(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            DeterministicGuardrail([])  # type: ignore[arg-type]

    def test_rejects_negative_limit(self) -> None:
        with pytest.raises(ValueError, match="finite and >= 0"):
            DeterministicGuardrail({"x": -1.0})

    def test_rejects_nan_limit(self) -> None:
        with pytest.raises(ValueError, match="finite"):
            DeterministicGuardrail({"x": float("nan")})

    def test_rejects_bool_limit(self) -> None:
        with pytest.raises(TypeError, match="numeric"):
            DeterministicGuardrail({"x": True})


# ===========================================================================
# 2. Happy Paths — 6 tests
# ===========================================================================


class TestGuardrailHappyPaths:
    """Valid proposals are accepted."""

    def test_admin_can_adjust(
        self, guardrail: DeterministicGuardrail, admin: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "cooling_system", 60.0)
        result = guardrail.validate(p, admin)
        assert result.approved is True
        assert result.reason is ReasonCode.OK

    def test_observer_can_read(
        self, guardrail: DeterministicGuardrail, observer: AgentIdentity
    ) -> None:
        p = Proposal(Action.READ_STATE, "cooling_system")
        result = guardrail.validate(p, observer)
        assert result.approved is True

    def test_operator_can_adjust(
        self, guardrail: DeterministicGuardrail, operator: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "cooling_system", 60.0)
        result = guardrail.validate(p, operator)
        assert result.approved is True

    def test_supervisor_can_modify(
        self, guardrail: DeterministicGuardrail, supervisor: AgentIdentity
    ) -> None:
        p = Proposal(Action.MODIFY_STATE, "main_valve", 80.0)
        result = guardrail.validate(p, supervisor)
        assert result.approved is True

    def test_value_at_max_boundary(
        self, guardrail: DeterministicGuardrail, admin: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "cooling_system", 75.0)
        result = guardrail.validate(p, admin)
        assert result.approved is True

    def test_value_at_min_boundary(
        self, guardrail: DeterministicGuardrail, admin: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "cooling_system", 0.0)
        result = guardrail.validate(p, admin)
        assert result.approved is True


# ===========================================================================
# 3. RBAC Enforcement — 6 tests
# ===========================================================================


class TestGuardrailRBAC:
    """Role-based access control is enforced."""

    def test_observer_cannot_adjust(
        self, guardrail: DeterministicGuardrail, observer: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "cooling_system", 60.0)
        result = guardrail.validate(p, observer)
        assert result.approved is False
        assert result.reason is ReasonCode.ROLE_NOT_PERMITTED

    def test_operator_cannot_modify(
        self, guardrail: DeterministicGuardrail, operator: AgentIdentity
    ) -> None:
        p = Proposal(Action.MODIFY_STATE, "main_valve", 80.0)
        result = guardrail.validate(p, operator)
        assert result.approved is False
        assert result.reason is ReasonCode.ROLE_NOT_PERMITTED

    def test_operator_cannot_shutdown(
        self, guardrail: DeterministicGuardrail, operator: AgentIdentity
    ) -> None:
        p = Proposal(Action.SHUTDOWN, "cooling_system", 0.0)
        result = guardrail.validate(p, operator)
        assert result.approved is False

    def test_supervisor_can_shutdown(
        self, guardrail: DeterministicGuardrail, supervisor: AgentIdentity
    ) -> None:
        p = Proposal(Action.SHUTDOWN, "cooling_system", 0.0)
        result = guardrail.validate(p, supervisor)
        assert result.approved is True

    def test_multiple_roles_union(self, guardrail: DeterministicGuardrail) -> None:
        identity = AgentIdentity(
            agent_id="multi",
            roles=frozenset({Role.OBSERVER, Role.OPERATOR}),
        )
        p = Proposal(Action.ADJUST_METRIC, "cooling_system", 60.0)
        result = guardrail.validate(p, identity)
        assert result.approved is True

    def test_role_not_permitted_includes_action(
        self, guardrail: DeterministicGuardrail, observer: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "cooling_system", 60.0)
        result = guardrail.validate(p, observer)
        assert result.metadata.get("action") == "adjust_metric"


# ===========================================================================
# 4. Target Allowlist — 3 tests
# ===========================================================================


class TestGuardrailTargets:
    """Targets not in the limits map are rejected."""

    def test_unknown_target_rejected(
        self, guardrail: DeterministicGuardrail, admin: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "plasma_cannon", 50.0)
        result = guardrail.validate(p, admin)
        assert result.approved is False
        assert result.reason is ReasonCode.TARGET_NOT_ALLOWED

    def test_case_sensitive_target(
        self, guardrail: DeterministicGuardrail, admin: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "Cooling_System", 50.0)
        result = guardrail.validate(p, admin)
        assert result.approved is False

    def test_target_included_in_metadata(
        self, guardrail: DeterministicGuardrail, admin: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "unknown", 50.0)
        result = guardrail.validate(p, admin)
        assert result.metadata.get("target") == "unknown"


# ===========================================================================
# 5. Value Checks — 5 tests
# ===========================================================================


class TestGuardrailValues:
    """Numeric limits and finiteness are enforced."""

    def test_value_above_max_rejected(
        self, guardrail: DeterministicGuardrail, admin: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "cooling_system", 100.0)
        result = guardrail.validate(p, admin)
        assert result.approved is False
        assert result.reason is ReasonCode.VALUE_EXCEEDS_LIMIT

    def test_value_below_min_rejected(
        self, guardrail: DeterministicGuardrail, admin: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "cooling_system", -1.0)
        result = guardrail.validate(p, admin)
        assert result.approved is False
        assert result.reason is ReasonCode.VALUE_BELOW_MIN

    def test_max_included_in_metadata(
        self, guardrail: DeterministicGuardrail, admin: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "cooling_system", 100.0)
        result = guardrail.validate(p, admin)
        assert result.metadata.get("max") == 75.0

    def test_min_included_in_metadata(
        self, guardrail: DeterministicGuardrail, admin: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "cooling_system", -1.0)
        result = guardrail.validate(p, admin)
        assert result.metadata.get("min") == 0.0

    def test_value_none_when_required_rejected(
        self, guardrail: DeterministicGuardrail, admin: AgentIdentity
    ) -> None:
        p = Proposal(Action.ADJUST_METRIC, "cooling_system")
        result = guardrail.validate(p, admin)
        assert result.approved is False
        assert result.reason is ReasonCode.MALFORMED_PAYLOAD


# ===========================================================================
# 6. Fail-Closed & Structural — 3 tests
# ===========================================================================


class TestGuardrailFailClosed:
    """Defensive guarantees."""

    def test_invalid_proposal_type_rejected(
        self, guardrail: DeterministicGuardrail, admin: AgentIdentity
    ) -> None:
        result = guardrail.validate("not a proposal", admin)  # type: ignore[arg-type]
        assert result.approved is False
        assert result.reason is ReasonCode.INVALID_TYPE

    def test_invalid_identity_type_rejected(self, guardrail: DeterministicGuardrail) -> None:
        p = Proposal(Action.READ_STATE, "cooling_system")
        result = guardrail.validate(p, "not an identity")  # type: ignore[arg-type]
        assert result.approved is False
        assert result.reason is ReasonCode.INVALID_TYPE

    def test_limits_are_immutable(self, guardrail: DeterministicGuardrail) -> None:
        assert isinstance(guardrail._limits, MappingProxyType)
        with pytest.raises(TypeError):
            guardrail._limits["new"] = 100.0  # type: ignore[index]
