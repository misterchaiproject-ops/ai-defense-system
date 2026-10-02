"""
Tests for contracts.proposal.Proposal.

Covers: happy paths, boundary conditions, invalid inputs,
security vectors, payload serialization, and fail-closed behavior.
"""

from __future__ import annotations

import dataclasses
import json
import math
from typing import cast

import pytest
from hypothesis import given
from hypothesis import strategies as st

from contracts.actions import Action
from contracts.proposal import MAX_TARGET_LENGTH, Proposal


class TestProposalConstruction:
    """Valid constructions must succeed and produce expected state."""

    def test_create_read_state_without_value(self) -> None:
        p = Proposal(action=Action.READ_STATE, target="cooling_system")
        assert p.action is Action.READ_STATE
        assert p.target == "cooling_system"
        assert p.value is None

    def test_create_adjust_metric_with_float_value(self) -> None:
        p = Proposal(
            action=Action.ADJUST_METRIC,
            target="cooling_system",
            value=62.5,
        )
        assert p.value == 62.5

    def test_create_adjust_metric_with_int_value(self) -> None:
        p = Proposal(
            action=Action.ADJUST_METRIC,
            target="main_valve",
            value=42,
        )
        assert p.value == 42

    def test_create_with_zero_value(self) -> None:
        p = Proposal(
            action=Action.ADJUST_METRIC,
            target="reactor_core",
            value=0.0,
        )
        assert p.value == 0.0


class TestProposalBoundaryConditions:
    """Edge-of-range values and lengths."""

    def test_target_at_max_length_accepted(self) -> None:
        target = "a" * MAX_TARGET_LENGTH
        p = Proposal(action=Action.READ_STATE, target=target)
        assert len(p.target) == MAX_TARGET_LENGTH

    def test_target_one_over_max_length_rejected(self) -> None:
        target = "a" * (MAX_TARGET_LENGTH + 1)
        with pytest.raises(ValueError, match="must be <="):
            Proposal(action=Action.READ_STATE, target=target)

    def test_target_single_char_accepted(self) -> None:
        p = Proposal(action=Action.READ_STATE, target="x")
        assert p.target == "x"

    def test_value_extremely_large_finite_accepted(self) -> None:
        p = Proposal(
            action=Action.ADJUST_METRIC,
            target="cooling_system",
            value=1e300,
        )
        assert p.value == 1e300

    def test_value_extremely_small_finite_accepted(self) -> None:
        p = Proposal(
            action=Action.ADJUST_METRIC,
            target="cooling_system",
            value=-1e-300,
        )
        assert p.value == -1e-300


class TestProposalInvalidInputs:
    """Rejection paths for invalid inputs."""

    @pytest.mark.parametrize(
        "bad_value",
        [float("nan"), float("inf"), float("-inf")],
        ids=["NaN", "+Inf", "-Inf"],
    )
    def test_reject_non_finite_values(self, bad_value: float) -> None:
        with pytest.raises(ValueError, match="finite"):
            Proposal(
                action=Action.ADJUST_METRIC,
                target="cooling_system",
                value=bad_value,
            )

    def test_reject_bool_true(self) -> None:
        with pytest.raises(TypeError, match="not bool"):
            Proposal(
                action=Action.ADJUST_METRIC,
                target="cooling_system",
                value=True,
            )

    def test_reject_bool_false(self) -> None:
        with pytest.raises(TypeError, match="not bool"):
            Proposal(
                action=Action.ADJUST_METRIC,
                target="cooling_system",
                value=False,
            )

    def test_reject_string_value(self) -> None:
        with pytest.raises(TypeError, match="must be int, float, or None"):
            Proposal(
                action=Action.ADJUST_METRIC,
                target="cooling_system",
                value="62.5",  # type: ignore[arg-type]
            )

    def test_reject_empty_target(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            Proposal(action=Action.READ_STATE, target="")

    @pytest.mark.parametrize("bad", [" ", "\t", "\n", "   \t  "])
    def test_reject_whitespace_only_target(self, bad: str) -> None:
        with pytest.raises(ValueError, match="non-empty|whitespace"):
            Proposal(action=Action.READ_STATE, target=bad)

    def test_reject_non_action_enum(self) -> None:
        with pytest.raises(TypeError, match="Action enum"):
            Proposal(
                action="read_state",  # type: ignore[arg-type]
                target="cooling_system",
            )

    def test_reject_non_string_target(self) -> None:
        with pytest.raises(TypeError, match="must be str"):
            Proposal(
                action=Action.READ_STATE,
                target=123,  # type: ignore[arg-type]
            )


class TestProposalSecurityVectors:
    """Adversarial inputs a real attacker might attempt."""

    def test_reject_null_byte_in_target(self) -> None:
        with pytest.raises(ValueError, match="control characters"):
            Proposal(action=Action.READ_STATE, target="cooling\x00system")

    def test_reject_newline_in_target(self) -> None:
        with pytest.raises(ValueError, match="control characters"):
            Proposal(action=Action.READ_STATE, target="cooling\nsystem")

    def test_reject_ansi_escape_in_target(self) -> None:
        with pytest.raises(ValueError, match="control characters"):
            Proposal(
                action=Action.READ_STATE,
                target="cooling\x1b[31mRED\x1b[0m",
            )

    def test_frozen_cannot_mutate_any_field(self) -> None:
        p = Proposal(
            action=Action.ADJUST_METRIC,
            target="cooling_system",
            value=60.0,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.value = 999.0  # type: ignore[misc]
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.target = "hacked"  # type: ignore[misc]
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.action = Action.SHUTDOWN  # type: ignore[misc]


class TestProposalPayload:
    """to_payload() output is what gets signed — must be stable."""

    def test_to_payload_deterministic(self) -> None:
        p = Proposal(
            action=Action.ADJUST_METRIC,
            target="cooling_system",
            value=60.0,
        )
        assert p.to_payload() == p.to_payload()

    def test_to_payload_json_serializable(self) -> None:
        p = Proposal(
            action=Action.ADJUST_METRIC,
            target="cooling_system",
            value=60.0,
        )
        encoded = json.dumps(
            p.to_payload(),
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        decoded = json.loads(encoded)
        assert decoded == {
            "action": "adjust_metric",
            "target": "cooling_system",
            "value": 60.0,
        }

    def test_to_payload_keys_are_fixed(self) -> None:
        p = Proposal(action=Action.READ_STATE, target="x")
        payload = p.to_payload()
        assert list(payload.keys()) == ["action", "target", "value"]
        assert payload["value"] is None


class TestProposalFailClosed:
    """Defensive guarantees."""

    def test_value_nan_rejected_before_guardrail(self) -> None:
        with pytest.raises(ValueError):
            Proposal(
                action=Action.ADJUST_METRIC,
                target="cooling_system",
                value=math.nan,
            )

    def test_proposal_is_hashable(self) -> None:
        p1 = Proposal(action=Action.READ_STATE, target="x")
        p2 = Proposal(action=Action.READ_STATE, target="x")
        assert p1 == p2
        assert hash(p1) == hash(p2)
        assert {p1, p2} == {p1}


# ============================================================
# TestPropertyBased - Hypothesis
# ============================================================


class TestPropertyBased:
    """Property-based tests using Hypothesis to explore edge cases."""

    @given(
        action=st.sampled_from(list(Action)),
        target=st.text(
            min_size=1,
            max_size=MAX_TARGET_LENGTH,
            alphabet=st.characters(blacklist_categories=("Cc", "Cf", "Cs", "Co")),
        ).filter(lambda s: s.strip() != ""),
        value=st.one_of(
            st.none(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.integers(),
        ),
    )
    def test_roundtrip_preserves_proposal(
        self, action: Action, target: str, value: float | int | None
    ) -> None:
        """Any valid Proposal must survive to_payload() -> rebuild."""
        original = Proposal(action=action, target=target, value=value)
        payload = original.to_payload()
        rebuilt = Proposal(
            action=Action(cast(str, payload["action"])),
            target=cast(str, payload["target"]),
            value=cast("float | None", payload["value"]),
        )
        assert rebuilt == original

    @given(infinite=st.sampled_from([float("inf"), float("-inf")]))
    def test_rejects_infinite_value(self, infinite: float) -> None:
        """Infinite values must always be rejected (fail-closed)."""
        with pytest.raises(ValueError, match="finite"):
            Proposal(
                action=Action.ADJUST_METRIC,
                target="cooling_system",
                value=infinite,
            )

    @given(bool_value=st.booleans())
    def test_rejects_bool_value(self, bool_value: bool) -> None:
        """Booleans must always be rejected (bool is subclass of int)."""
        with pytest.raises(TypeError, match="bool"):
            Proposal(
                action=Action.ADJUST_METRIC,
                target="cooling_system",
                value=bool_value,
            )

    @given(
        target=st.text(
            min_size=MAX_TARGET_LENGTH + 1,
            max_size=MAX_TARGET_LENGTH * 2,
            alphabet=st.characters(blacklist_categories=("Cc", "Cf", "Cs", "Co")),
        )
    )
    def test_rejects_overlong_target(self, target: str) -> None:
        """Targets longer than MAX_TARGET_LENGTH must be rejected."""
        with pytest.raises(ValueError, match="characters"):
            Proposal(
                action=Action.ADJUST_METRIC,
                target=target,
                value=0.0,
            )

    @given(control_char=st.sampled_from(["\x00", "\x01", "\x1f", "\x7f"]))
    def test_rejects_control_chars_in_target(self, control_char: str) -> None:
        """Control characters in target must be rejected (injection protection)."""
        target = "a" + control_char + "b"
        with pytest.raises(ValueError, match="control characters|whitespace-only"):
            Proposal(
                action=Action.ADJUST_METRIC,
                target=target,
                value=0.0,
            )
