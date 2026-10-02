"""Comprehensive test suite for contracts.roles.Role."""

from __future__ import annotations

import json
from enum import StrEnum

import pytest

from contracts.roles import Role


class TestRoleHappyPaths:
    def test_observer_present(self) -> None:
        assert Role.OBSERVER.value == "observer"

    def test_operator_present(self) -> None:
        assert Role.OPERATOR.value == "operator"

    def test_supervisor_present(self) -> None:
        assert Role.SUPERVISOR.value == "supervisor"

    def test_admin_present(self) -> None:
        assert Role.ADMIN.value == "admin"


class TestRoleBoundaryConditions:
    def test_exactly_four_members(self) -> None:
        assert len(list(Role)) == 4

    def test_all_values_are_lowercase_identifiers(self) -> None:
        for role in Role:
            assert role.value == role.value.lower()
            assert role.value.isidentifier()

    def test_is_str_subclass(self) -> None:
        assert issubclass(Role, str)
        assert issubclass(Role, StrEnum)


class TestRoleInvalidInputs:
    def test_unknown_value_raises(self) -> None:
        with pytest.raises(ValueError):
            Role("nonexistent")

    def test_unknown_name_raises(self) -> None:
        with pytest.raises(AttributeError):
            _ = Role.NOT_A_ROLE  # type: ignore[attr-defined]


class TestRoleSecurityVectors:
    def test_string_equality_works(self) -> None:
        """StrEnum members compare equal to their raw string values."""
        assert Role.ADMIN == "admin"  # type: ignore[comparison-overlap]

    def test_json_serialization_is_clean(self) -> None:
        payload = {"role": Role.OPERATOR}
        assert json.dumps(payload) == '{"role": "operator"}'

    def test_members_are_hashable(self) -> None:
        s = {Role.OBSERVER, Role.ADMIN}
        assert len(s) == 2


class TestRoleFailClosed:
    def test_values_are_unique(self) -> None:
        values = [r.value for r in Role]
        assert len(values) == len(set(values))

    def test_names_are_unique(self) -> None:
        names = [r.name for r in Role]
        assert len(names) == len(set(names))
