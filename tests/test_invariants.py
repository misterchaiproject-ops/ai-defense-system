"""
Invariant & Contract Tests for Trust Plane (v0.4)
=================================================
These tests validate the data-contract boundary only.
They do not prove runtime security, cryptographic correctness, or engine behavior.
"""

from dataclasses import MISSING, FrozenInstanceError, fields

import pytest

from src.trust.contracts import (
    AttestationFailureReason,
    AttestationMeasurements,
    AttestationRequest,
    AttestationResult,
    CryptoAlgorithm,
    EvidenceRef,
    TrustAssessment,
    VerificationMetadata,
    VerifiedMessage,
)


@pytest.fixture
def valid_evidence() -> EvidenceRef:
    return EvidenceRef(
        event_id="evt-123",
        correlation_id="cor-456",
        evidence_hash="a" * 64,
    )


@pytest.fixture
def valid_measurements() -> AttestationMeasurements:
    return AttestationMeasurements(
        software_measurement="hash1",
        configuration_hash="hash2",
        model_measurement=None,
        policy_version="v1.0",
        runtime_measurement="hash3",
    )


@pytest.fixture
def valid_verification_metadata() -> VerificationMetadata:
    return VerificationMetadata(
        channel_id="ch-01",
        verified_at=1700000000,
        crypto_algorithm=CryptoAlgorithm.HMAC_SHA256,
        replay_checked=True,
    )


@pytest.fixture
def valid_verified_message(
    valid_verification_metadata: VerificationMetadata,
) -> VerifiedMessage:
    return VerifiedMessage(
        agent_identity="agent-001",
        nonce="nonce-123",
        timestamp=1700000000,
        protocol_version="1.0",
        message_id="msg-001",
        canonical_payload=b'{"a":1}',
        verification_metadata=valid_verification_metadata,
    )


def test_no_enforcement_state_in_trust_contracts() -> None:
    import src.trust.contracts as contracts

    assert not hasattr(contracts, "EnforcementState")


def test_attestation_result_requires_evidence(valid_evidence: EvidenceRef) -> None:
    result = AttestationResult(
        trust_assessment=TrustAssessment.TRUSTED,
        reason=None,
        evidence=valid_evidence,
    )
    assert isinstance(result.evidence, EvidenceRef)
    assert AttestationResult.__annotations__["evidence"] is EvidenceRef


def test_verified_message_requires_canonical_payload(
    valid_verification_metadata: VerificationMetadata,
) -> None:
    with pytest.raises(TypeError):
        VerifiedMessage(
            agent_identity="agent-001",
            nonce="nonce-123",
            timestamp=1700000000,
            protocol_version="1.0",
            message_id="msg-001",
            verification_metadata=valid_verification_metadata,
        )


def test_failure_model_allows_untrusted(valid_evidence: EvidenceRef) -> None:
    result = AttestationResult(
        trust_assessment=TrustAssessment.UNTRUSTED,
        reason=AttestationFailureReason.INTEGRITY_MISMATCH,
        evidence=valid_evidence,
    )
    assert result.trust_assessment is TrustAssessment.UNTRUSTED


def test_no_policy_context_in_trust_contracts() -> None:
    import src.trust.contracts as contracts

    assert not hasattr(contracts, "PolicyContext")


def test_verification_metadata_has_no_defaults() -> None:
    verification_fields = {field.name: field for field in fields(VerificationMetadata)}

    assert verification_fields["replay_checked"].default is MISSING

    with pytest.raises(TypeError):
        VerificationMetadata(
            channel_id="ch-01",
            verified_at=1700000000,
            crypto_algorithm=CryptoAlgorithm.HMAC_SHA256,
        )


def test_crypto_algorithm_is_closed_enum() -> None:
    algorithm_field = next(
        field for field in fields(VerificationMetadata) if field.name == "crypto_algorithm"
    )
    assert algorithm_field.type is CryptoAlgorithm
    assert list(CryptoAlgorithm) == [
        CryptoAlgorithm.HMAC_SHA256,
        CryptoAlgorithm.ED25519,
    ]
    with pytest.raises(ValueError):
        CryptoAlgorithm("none")


def test_contract_immutability(
    valid_evidence: EvidenceRef,
    valid_measurements: AttestationMeasurements,
    valid_verified_message: VerifiedMessage,
) -> None:
    with pytest.raises(FrozenInstanceError):
        valid_evidence.event_id = "new_id"  # type: ignore[misc]

    result = AttestationResult(
        trust_assessment=TrustAssessment.TRUSTED,
        reason=None,
        evidence=valid_evidence,
    )
    with pytest.raises(FrozenInstanceError):
        result.trust_assessment = TrustAssessment.UNTRUSTED  # type: ignore[misc]

    request = AttestationRequest(
        message=valid_verified_message,
        measurements=valid_measurements,
        requested_capabilities=("cap1", "cap2"),
    )
    assert isinstance(request.requested_capabilities, tuple)
    with pytest.raises(FrozenInstanceError):
        request.message = valid_verified_message  # type: ignore[misc]
