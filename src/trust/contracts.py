"""
Trust Plane Data Contracts (v0.4)
=================================
This module contains data contracts only.
It must not contain execution, hashing, or policy logic.
It must not import Policy, Channel, Audit, or Engine modules.
"""

from dataclasses import dataclass
from enum import Enum


class TrustAssessment(Enum):
    """Trust assessment derived from verified evidence."""

    TRUSTED = "trusted"
    DEGRADED = "degraded"
    SUSPICIOUS = "suspicious"
    UNTRUSTED = "untrusted"


class AttestationFailureReason(Enum):
    """Reasons that can explain a non-successful trust assessment."""

    UNKNOWN_IDENTITY = "unknown_identity"
    INTEGRITY_MISMATCH = "integrity_mismatch"
    CONFIGURATION_MISMATCH = "configuration_mismatch"
    VERSION_REVOKED = "version_revoked"
    CAPABILITY_ESCALATION = "capability_escalation"
    POLICY_MISMATCH = "policy_mismatch"
    INTERNAL_FAILURE = "internal_failure"
    AUDIT_FAILURE = "audit_failure"
    TRUST_STATE_REJECTED = "trust_state_rejected"


class CryptoAlgorithm(Enum):
    """
    Cryptographic algorithms attested by SecureAgentChannel.

    Trust Plane does not select the algorithm; the Channel establishes it
    and supplies the closed enum value as verification metadata.
    """

    HMAC_SHA256 = "hmac_sha256"
    ED25519 = "ed25519"


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    """Reference to an audit/evidence record created outside this contract layer."""

    event_id: str
    correlation_id: str
    evidence_hash: str


@dataclass(frozen=True, slots=True)
class AttestationMeasurements:
    """Measurements required for trust evaluation."""

    software_measurement: str
    configuration_hash: str
    model_measurement: str | None
    policy_version: str
    runtime_measurement: str


@dataclass(frozen=True, slots=True)
class VerificationMetadata:
    """Verification metadata produced by SecureAgentChannel."""

    channel_id: str
    verified_at: int
    crypto_algorithm: CryptoAlgorithm
    replay_checked: bool


@dataclass(frozen=True, slots=True)
class VerifiedMessage:
    """
    Cryptographically verified message passed from Channel to Trust Plane.

    ``canonical_payload`` is expected to follow RFC 8785/JCS. Validation of
    canonicalization belongs to the Channel/messaging layer, not this contract.
    """

    agent_identity: str
    nonce: str
    timestamp: int
    protocol_version: str
    message_id: str
    canonical_payload: bytes
    verification_metadata: VerificationMetadata


@dataclass(frozen=True, slots=True)
class AttestationRequest:
    """Input contract for the attestation evaluation boundary."""

    message: VerifiedMessage
    measurements: AttestationMeasurements
    requested_capabilities: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AttestationResult:
    """Trust evaluation result; it intentionally contains no enforcement state."""

    trust_assessment: TrustAssessment
    reason: AttestationFailureReason | None
    evidence: EvidenceRef
