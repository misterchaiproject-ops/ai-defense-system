"""
Comprehensive test suite for contracts.validation_result.ValidationResult.
"""

from __future__ import annotations

import dataclasses

import pytest

from contracts.reason_codes import ReasonCode
from contracts.validation_result import (
    MAX_METADATA_ENTRIES,
    ValidationResult,
)


class TestValidationResultHappyPaths:
    def test_ok_factory_creates_approved_result(self) -> None:
        result = ValidationResult.ok()
        assert result.approved is True
        assert result.reason is ReasonCode.OK
        assert dict(result.metadata) == {}

    def test_reject_factory_creates_rejected_result(self) -> None:
        result = ValidationResult.reject(ReasonCode.INVALID_TYPE)
        assert result.approved is False
        assert result.reason is ReasonCode.INVALID_TYPE

    def test_reject_with_metadata(self) -> None:
        result = ValidationResult.reject(ReasonCode.VALUE_EXCEEDS_LIMIT, value=100, max=75)
        assert result.approved is False
        assert result.metadata["value"] == 100
        assert result.metadata["max"] == 75

    def test_bool_returns_approved(self) -> None:
        assert bool(ValidationResult.ok()) is True
        assert bool(ValidationResult.reject(ReasonCode.INVALID_TYPE)) is False


class TestValidationResultBoundaryConditions:
    def test_empty_metadata_default(self) -> None:
        result = ValidationResult.ok()
        assert len(result.metadata) == 0

    def test_max_metadata_entries_accepted(self) -> None:
        big_meta = {f"k{i}": i for i in range(MAX_METADATA_ENTRIES)}
        result = ValidationResult(
            approved=False,
            reason=ReasonCode.INVALID_TYPE,
            metadata=big_meta,
        )
        assert len(result.metadata) == MAX_METADATA_ENTRIES

    def test_one_over_max_metadata_rejected(self) -> None:
        huge_meta = {f"k{i}": i for i in range(MAX_METADATA_ENTRIES + 1)}
        with pytest.raises(ValueError, match="must not exceed"):
            ValidationResult(
                approved=False,
                reason=ReasonCode.INVALID_TYPE,
                metadata=huge_meta,
            )


class TestValidationResultInvalidInputs:
    @pytest.mark.parametrize(
        "bad_value",
        [1, 0, "yes", "no", None, [], {}],
    )
    def test_reject_non_bool_approved(self, bad_value: object) -> None:
        with pytest.raises(TypeError, match="must be a bool"):
            ValidationResult(
                approved=bad_value,  # type: ignore[arg-type]
                reason=ReasonCode.INVALID_TYPE,
            )

    @pytest.mark.parametrize(
        "bad_reason",
        ["OK", "INVALID_TYPE", 0, None, [], 42],
    )
    def test_reject_non_reason_code(self, bad_reason: object) -> None:
        with pytest.raises(TypeError, match="must be a ReasonCode"):
            ValidationResult(
                approved=False,
                reason=bad_reason,  # type: ignore[arg-type]
            )

    def test_reject_non_mapping_metadata(self) -> None:
        with pytest.raises(TypeError, match="must be a Mapping"):
            ValidationResult(
                approved=False,
                reason=ReasonCode.INVALID_TYPE,
                metadata=[("k", "v")],  # type: ignore[arg-type]
            )

    def test_reject_approved_true_with_non_ok_reason(self) -> None:
        with pytest.raises(ValueError, match="requires ReasonCode.OK"):
            ValidationResult(approved=True, reason=ReasonCode.INVALID_TYPE)

    def test_reject_approved_false_with_ok_reason(self) -> None:
        with pytest.raises(ValueError, match="cannot use ReasonCode.OK"):
            ValidationResult(approved=False, reason=ReasonCode.OK)


class TestValidationResultSecurityVectors:
    def test_metadata_is_frozen(self) -> None:
        result = ValidationResult.reject(ReasonCode.INVALID_TYPE, k="v")
        with pytest.raises(TypeError):
            result.metadata["new"] = "value"  # type: ignore[index]

    def test_metadata_is_copied_from_source(self) -> None:
        source = {"k": "v"}
        result = ValidationResult(
            approved=False,
            reason=ReasonCode.INVALID_TYPE,
            metadata=source,
        )
        source["k"] = "hacked"
        assert result.metadata["k"] == "v"

    def test_cannot_mutate_any_field(self) -> None:
        result = ValidationResult.ok()
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.approved = False  # type: ignore[misc]
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.reason = ReasonCode.INVALID_TYPE  # type: ignore[misc]
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.metadata = None  # type: ignore[misc,assignment]


class TestValidationResultFailClosed:
    def test_is_hashable(self) -> None:
        r1 = ValidationResult.ok()
        r2 = ValidationResult.ok()
        assert hash(r1) == hash(r2)
        assert {r1, r2} == {r1}

    def test_equal_results_compare_equal(self) -> None:
        r1 = ValidationResult.reject(ReasonCode.INVALID_TYPE, k="v")
        r2 = ValidationResult.reject(ReasonCode.INVALID_TYPE, k="v")
        assert r1 == r2

    def test_different_reason_not_equal(self) -> None:
        r1 = ValidationResult.reject(ReasonCode.INVALID_TYPE)
        r2 = ValidationResult.reject(ReasonCode.MALFORMED_PAYLOAD)
        assert r1 != r2

    def test_ok_and_reject_not_equal(self) -> None:
        r1 = ValidationResult.ok()
        r2 = ValidationResult.reject(ReasonCode.INVALID_TYPE)
        assert r1 != r2
