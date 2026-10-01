"""
Comprehensive test suite for contracts.agent_identity.AgentIdentity.

Covers five categories:
  1. Happy paths (valid constructions).
  2. Boundary conditions (length edges, single role, all roles).
  3. Invalid inputs (type confusion, wrong container, empty).
  4. Security vectors (control chars, homographs, String-vs-Enum,
     DoS via oversized frozenset, information disclosure).
  5. Fail-closed behaviors (immutability, hashability, equality,
     has_role safety).

Target: 100% line and branch coverage for agent_identity.py.
"""

from __future__ import annotations

import dataclasses

import pytest

from contracts.agent_identity import MAX_AGENT_ID_LENGTH, AgentIdentity
from contracts.roles import Role

# ===========================================================================
# 1. Happy Paths — 5 tests
# ===========================================================================


class TestAgentIdentityConstruction:
    """Valid constructions produce expected state."""

    def test_create_with_single_role(self) -> None:
        identity = AgentIdentity(
            agent_id="Agent_A",
            roles=frozenset({Role.ADMIN}),
        )
        assert identity.agent_id == "Agent_A"
        assert identity.roles == frozenset({Role.ADMIN})

    def test_create_with_multiple_roles(self) -> None:
        identity = AgentIdentity(
            agent_id="Agent_B",
            roles=frozenset({Role.OPERATOR, Role.SUPERVISOR}),
        )
        assert Role.OPERATOR in identity.roles
        assert Role.SUPERVISOR in identity.roles

    def test_create_with_all_roles(self) -> None:
        identity = AgentIdentity(
            agent_id="Agent_C",
            roles=frozenset({Role.OBSERVER, Role.OPERATOR, Role.SUPERVISOR, Role.ADMIN}),
        )
        assert len(identity.roles) == 4

    def test_create_with_hyphen_in_id(self) -> None:
        identity = AgentIdentity(
            agent_id="Agent-01",
            roles=frozenset({Role.OBSERVER}),
        )
        assert identity.agent_id == "Agent-01"

    def test_create_with_underscore_in_id(self) -> None:
        identity = AgentIdentity(
            agent_id="agent_42",
            roles=frozenset({Role.OBSERVER}),
        )
        assert identity.agent_id == "agent_42"


# ===========================================================================
# 2. Boundary Conditions — 4 tests
# ===========================================================================


class TestAgentIdentityBoundaryConditions:
    """Length and content at the edges of the allowed range."""

    def test_min_length_id(self) -> None:
        identity = AgentIdentity(
            agent_id="a",
            roles=frozenset({Role.OBSERVER}),
        )
        assert identity.agent_id == "a"

    def test_max_length_id(self) -> None:
        long_id = "a" * MAX_AGENT_ID_LENGTH
        identity = AgentIdentity(
            agent_id=long_id,
            roles=frozenset({Role.OBSERVER}),
        )
        assert len(identity.agent_id) == MAX_AGENT_ID_LENGTH

    def test_one_over_max_length_id_rejected(self) -> None:
        too_long = "a" * (MAX_AGENT_ID_LENGTH + 1)
        with pytest.raises(ValueError):
            AgentIdentity(
                agent_id=too_long,
                roles=frozenset({Role.OBSERVER}),
            )

    def test_all_roles_combination(self) -> None:
        all_roles = frozenset({Role.OBSERVER, Role.OPERATOR, Role.SUPERVISOR, Role.ADMIN})
        identity = AgentIdentity(agent_id="super", roles=all_roles)
        assert identity.roles == all_roles


# ===========================================================================
# 3. Invalid Inputs — 9 tests
# ===========================================================================


class TestAgentIdentityInvalidInputs:
    """Every rejection path raises the appropriate exception type."""

    def test_reject_non_string_id(self) -> None:
        with pytest.raises(TypeError, match="must be a str"):
            AgentIdentity(
                agent_id=123,  # type: ignore[arg-type]
                roles=frozenset({Role.OBSERVER}),
            )

    def test_reject_empty_id(self) -> None:
        with pytest.raises(ValueError):
            AgentIdentity(
                agent_id="",
                roles=frozenset({Role.OBSERVER}),
            )

    def test_reject_id_with_space(self) -> None:
        with pytest.raises(ValueError):
            AgentIdentity(
                agent_id="Agent A",
                roles=frozenset({Role.OBSERVER}),
            )

    def test_reject_id_with_dot(self) -> None:
        with pytest.raises(ValueError):
            AgentIdentity(
                agent_id="Agent.A",
                roles=frozenset({Role.OBSERVER}),
            )

    def test_reject_non_frozenset_roles(self) -> None:
        with pytest.raises(TypeError, match="must be a frozenset"):
            AgentIdentity(
                agent_id="Agent_A",
                roles={Role.ADMIN},  # type: ignore[arg-type]
            )

    def test_reject_set_roles(self) -> None:
        with pytest.raises(TypeError, match="must be a frozenset"):
            AgentIdentity(
                agent_id="Agent_A",
                roles=set({Role.ADMIN}),  # type: ignore[arg-type]
            )

    def test_reject_empty_roles(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            AgentIdentity(agent_id="Agent_A", roles=frozenset())

    def test_reject_list_roles(self) -> None:
        with pytest.raises(TypeError, match="must be a frozenset"):
            AgentIdentity(
                agent_id="Agent_A",
                roles=[Role.ADMIN],  # type: ignore[arg-type]
            )

    def test_reject_none_roles(self) -> None:
        with pytest.raises(TypeError, match="must be a frozenset"):
            AgentIdentity(
                agent_id="Agent_A",
                roles=None,  # type: ignore[arg-type]
            )


# ===========================================================================
# 4. Security Vectors — 11 tests
# ===========================================================================


class TestAgentIdentitySecurityVectors:
    """Adversarial inputs a real attacker might attempt."""

    def test_reject_newline_in_id(self) -> None:
        with pytest.raises(ValueError):
            AgentIdentity(
                agent_id="Agent\nAdmin",
                roles=frozenset({Role.OBSERVER}),
            )

    def test_reject_null_byte_in_id(self) -> None:
        with pytest.raises(ValueError):
            AgentIdentity(
                agent_id="Agent\x00",
                roles=frozenset({Role.OBSERVER}),
            )

    def test_reject_trailing_newline_in_id(self) -> None:
        """A trailing newline is rejected (``$`` vs ``\\Z`` trap)."""
        with pytest.raises(ValueError):
            AgentIdentity(
                agent_id="Agent_A\n",
                roles=frozenset({Role.OBSERVER}),
            )

    def test_reject_ansi_escape_in_id(self) -> None:
        with pytest.raises(ValueError):
            AgentIdentity(
                agent_id="\x1b[31mAgent",
                roles=frozenset({Role.OBSERVER}),
            )

    def test_reject_unicode_homograph_in_id(self) -> None:
        """Cyrillic 'О' (U+041E) is not the Latin 'O' (U+004F)."""
        with pytest.raises(ValueError):
            AgentIdentity(
                agent_id="Agent_О",  # noqa: RUF001
                roles=frozenset({Role.OBSERVER}),
            )

    def test_reject_string_role_impersonating_admin(self) -> None:
        """
        CRITICAL: a raw string 'admin' must NOT be accepted as a role.
        Without the isinstance check, RBAC could be bypassed.
        """
        with pytest.raises(TypeError, match="only Role instances"):
            AgentIdentity(
                agent_id="Attacker",
                roles=frozenset({"admin"}),  # type: ignore[arg-type]
            )

    def test_reject_mixed_string_and_role(self) -> None:
        """Even one non-Role element invalidates the whole set."""
        with pytest.raises(TypeError, match="only Role instances"):
            AgentIdentity(
                agent_id="Attacker",
                roles=frozenset({Role.OBSERVER, "admin"}),  # type: ignore[arg-type]
            )

    def test_reject_oversized_frozenset(self) -> None:
        """
        DoS defense: a frozenset larger than the number of Role members
        must be rejected BEFORE iterating over its elements.
        """
        huge = frozenset(f"fake_role_{i}" for i in range(100))
        with pytest.raises(ValueError, match="must not contain more than"):
            AgentIdentity(agent_id="Attacker", roles=huge)  # type: ignore[arg-type]

    def test_frozen_cannot_mutate_any_field(self) -> None:
        identity = AgentIdentity(
            agent_id="Agent_A",
            roles=frozenset({Role.ADMIN}),
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            identity.agent_id = "Hacked"  # type: ignore[misc]
        with pytest.raises(dataclasses.FrozenInstanceError):
            identity.roles = frozenset({Role.OBSERVER})  # type: ignore[misc]

    def test_error_message_does_not_reveal_regex_pattern(self) -> None:
        """
        Information disclosure prevention: the ValueError message must
        not contain the internal regex pattern.
        """
        with pytest.raises(ValueError) as exc_info:
            AgentIdentity(
                agent_id="invalid id!",
                roles=frozenset({Role.OBSERVER}),
            )
        message = str(exc_info.value)
        assert "A-Za-z0-9" not in message
        assert "{1,64}" not in message

    def test_error_message_does_not_include_raw_input(self) -> None:
        """
        Information disclosure prevention: the ValueError message must
        not echo the raw (potentially malicious) input.
        """
        payload = "Agent\nAdmin\x00"
        with pytest.raises(ValueError) as exc_info:
            AgentIdentity(
                agent_id=payload,
                roles=frozenset({Role.OBSERVER}),
            )
        assert payload not in str(exc_info.value)


# ===========================================================================
# 5. Fail-Closed & Structural — 4 tests
# ===========================================================================


class TestAgentIdentityFailClosed:
    """Defensive guarantees and structural correctness."""

    def test_identity_is_hashable(self) -> None:
        i1 = AgentIdentity(agent_id="Agent_A", roles=frozenset({Role.ADMIN}))
        i2 = AgentIdentity(agent_id="Agent_A", roles=frozenset({Role.ADMIN}))
        assert hash(i1) == hash(i2)
        assert {i1, i2} == {i1}

    def test_equal_identities_compare_equal(self) -> None:
        i1 = AgentIdentity(agent_id="Agent_A", roles=frozenset({Role.ADMIN}))
        i2 = AgentIdentity(agent_id="Agent_A", roles=frozenset({Role.ADMIN}))
        assert i1 == i2

    def test_different_ids_not_equal(self) -> None:
        i1 = AgentIdentity(agent_id="Agent_A", roles=frozenset({Role.ADMIN}))
        i2 = AgentIdentity(agent_id="Agent_B", roles=frozenset({Role.ADMIN}))
        assert i1 != i2

    def test_same_id_different_roles_not_equal(self) -> None:
        i1 = AgentIdentity(agent_id="Agent_A", roles=frozenset({Role.ADMIN}))
        i2 = AgentIdentity(agent_id="Agent_A", roles=frozenset({Role.OBSERVER}))
        assert i1 != i2


# ===========================================================================
# 6. has_role() method — 4 tests
# ===========================================================================


class TestAgentIdentityHasRole:
    """Behavior of the has_role() method."""

    def test_has_role_returns_true_for_held_role(self) -> None:
        identity = AgentIdentity(
            agent_id="Agent_A",
            roles=frozenset({Role.OPERATOR, Role.SUPERVISOR}),
        )
        assert identity.has_role(Role.OPERATOR) is True
        assert identity.has_role(Role.SUPERVISOR) is True

    def test_has_role_returns_false_for_missing_role(self) -> None:
        identity = AgentIdentity(
            agent_id="Agent_A",
            roles=frozenset({Role.OBSERVER}),
        )
        assert identity.has_role(Role.ADMIN) is False
        assert identity.has_role(Role.OPERATOR) is False

    def test_has_role_returns_false_for_string_admin(self) -> None:
        """
        CRITICAL: `has_role("admin")` must NOT return True even though
        `"admin" == Role.ADMIN` in Python (StrEnum trap).
        """
        identity = AgentIdentity(
            agent_id="Agent_A",
            roles=frozenset({Role.ADMIN}),
        )
        assert identity.has_role("admin") is False  # type: ignore[arg-type]
        assert identity.has_role("ADMIN") is False  # type: ignore[arg-type]

    def test_has_role_returns_false_for_none(self) -> None:
        """None must not match any role."""
        identity = AgentIdentity(
            agent_id="Agent_A",
            roles=frozenset({Role.ADMIN}),
        )
        assert identity.has_role(None) is False  # type: ignore[arg-type]
