"""Comprehensive test suite for contracts.actions.Action."""

from __future__ import annotations

import json
from enum import StrEnum

import pytest

from contracts.actions import Action


class TestActionHappyPaths:
    def test_read_state_present(self) -> None:
        assert Action.READ_STATE.value == "read_state"

    def test_adjust_metric_present(self) -> None:
        assert Action.ADJUST_METRIC.value == "adjust_metric"

    def test_modify_state_present(self) -> None:
        assert Action.MODIFY_STATE.value == "modify_state"

    def test_shutdown_present(self) -> None:
        assert Action.SHUTDOWN.value == "shutdown"


class TestActionBoundaryConditions:
    def test_exactly_four_members(self) -> None:
        assert len(list(Action)) == 4

    def test_all_values_are_lowercase_identifiers(self) -> None:
        for action in Action:
            assert action.value == action.value.lower()
            assert action.value.isidentifier()

    def test_is_str_subclass(self) -> None:
        assert issubclass(Action, str)
        assert issubclass(Action, StrEnum)


class TestActionInvalidInputs:
    def test_unknown_value_raises(self) -> None:
        with pytest.raises(ValueError):
            Action("delete_everything")

    def test_unknown_name_raises(self) -> None:
        with pytest.raises(AttributeError):
            _ = Action.DELETE_ALL  # type: ignore[attr-defined]


class TestActionSecurityVectors:
    def test_string_equality_works(self) -> None:
        """StrEnum members compare equal to their raw string values."""
        assert Action.SHUTDOWN == "shutdown"  # type: ignore[comparison-overlap]

    def test_json_serialization_is_clean(self) -> None:
        payload = {"action": Action.ADJUST_METRIC}
        assert json.dumps(payload) == '{"action": "adjust_metric"}'

    def test_members_are_hashable(self) -> None:
        s = {Action.READ_STATE, Action.SHUTDOWN}
        assert len(s) == 2


class TestActionFailClosed:
    def test_values_are_unique(self) -> None:
        values = [a.value for a in Action]
        assert len(values) == len(set(values))

    def test_names_are_unique(self) -> None:
        names = [a.name for a in Action]
        assert len(names) == len(set(names))
