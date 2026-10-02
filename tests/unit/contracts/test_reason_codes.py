"""
Comprehensive test suite for contracts.reason_codes.ReasonCode.

Covers five categories:
  1. Happy paths (all expected members exist with correct values).
  2. Boundary conditions (all 16 codes, iteration completeness).
  3. Invalid inputs (lookup by unknown value).
  4. Security vectors (StrEnum behavior, immutability, hashability).
  5. Fail-closed behaviors (uniqueness, JSON serialization).

Target: 100% coverage for reason_codes.py.
"""

from __future__ import annotations

import json
from enum import StrEnum

import pytest

from contracts.reason_codes import ReasonCode

# ===========================================================================
# 1. Happy Paths — 5 tests
# ===========================================================================


class TestReasonCodeHappyPaths:
    """Expected members exist with correct string values."""

    def test_ok_is_present(self) -> None:
        assert ReasonCode.OK == "OK"
        assert ReasonCode.OK.value == "OK"

    def test_input_validation_codes_present(self) -> None:
        expected = {
            "INVALID_TYPE",
            "MALFORMED_PAYLOAD",
            "VALUE_NOT_FINITE",
            "VALUE_EXCEEDS_LIMIT",
            "VALUE_BELOW_MIN",
            "TARGET_NOT_ALLOWED",
        }
        assert {c.name for c in ReasonCode} >= expected

    def test_rbac_codes_present(self) -> None:
        assert ReasonCode.ROLE_NOT_PERMITTED.value == "ROLE_NOT_PERMITTED"

    def test_message_integrity_codes_present(self) -> None:
        expected = {
            "INVALID_SIGNATURE",
            "REPLAY_DETECTED",
            "UNSUPPORTED_VERSION",
            "INVALID_ENVELOPE",
            "UNKNOWN_KEY_ID",
        }
        assert {c.name for c in ReasonCode} >= expected

    def test_timing_and_fallback_codes_present(self) -> None:
        expected = {
            "TIMESTAMP_TOO_OLD",
            "TIMESTAMP_FROM_FUTURE",
            "INTERNAL_ERROR",
        }
        assert {c.name for c in ReasonCode} >= expected


# ===========================================================================
# 2. Boundary Conditions — 3 tests
# ===========================================================================


class TestReasonCodeBoundaryConditions:
    """Structural properties of the enum."""

    def test_exactly_16_members(self) -> None:
        """The current registry has exactly 16 codes."""
        assert len(list(ReasonCode)) == 16

    def test_all_values_equal_their_names(self) -> None:
        """Every code's value matches its member name."""
        for code in ReasonCode:
            assert code.value == code.name

    def test_is_str_subclass(self) -> None:
        """StrEnum inherits from str — JSON-serializable."""
        assert issubclass(ReasonCode, str)
        assert issubclass(ReasonCode, StrEnum)


# ===========================================================================
# 3. Invalid Inputs — 3 tests
# ===========================================================================


class TestReasonCodeInvalidInputs:
    """Lookup behavior for missing or invalid values."""

    def test_unknown_value_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            ReasonCode("NOT_A_REAL_CODE")

    def test_unknown_name_raises_attribute_error(self) -> None:
        with pytest.raises(AttributeError):
            _ = ReasonCode.NOT_A_REAL_CODE  # type: ignore[attr-defined]

    def test_empty_string_rejected(self) -> None:
        with pytest.raises(ValueError):
            ReasonCode("")


# ===========================================================================
# 4. Security Vectors — 3 tests
# ===========================================================================


class TestReasonCodeSecurityVectors:
    """Adversarial and edge-case behaviors."""

    def test_str_equality_works(self) -> None:
        """StrEnum members compare equal to their raw string values."""
        assert ReasonCode.OK == "OK"
        assert ReasonCode.INVALID_TYPE == "INVALID_TYPE"

    def test_json_serialization_is_clean(self) -> None:
        """Serializes as plain string, no enum metadata leaks."""
        payload = {"reason": ReasonCode.REPLAY_DETECTED}
        encoded = json.dumps(payload)
        assert encoded == '{"reason": "REPLAY_DETECTED"}'

    def test_members_are_hashable(self) -> None:
        """Members can be used in sets and dict keys."""
        s = {ReasonCode.OK, ReasonCode.INVALID_TYPE}
        assert len(s) == 2
        d = {ReasonCode.OK: "ok"}
        assert d[ReasonCode.OK] == "ok"


# ===========================================================================
# 5. Fail-Closed & Structural — 3 tests
# ===========================================================================


class TestReasonCodeFailClosed:
    """Uniqueness and iteration invariants."""

    def test_values_are_unique(self) -> None:
        """No two members share the same value."""
        values = [c.value for c in ReasonCode]
        assert len(values) == len(set(values))

    def test_names_are_unique(self) -> None:
        """No two members share the same name."""
        names = [c.name for c in ReasonCode]
        assert len(names) == len(set(names))

    def test_ok_is_the_only_success_code(self) -> None:
        """OK is the sole success marker — all others are failures."""
        success = [c for c in ReasonCode if c.value == "OK"]
        assert success == [ReasonCode.OK]
