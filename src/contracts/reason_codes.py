"""
Reason codes for every validation outcome.

Every rejection or acceptance in the system produces exactly one
ReasonCode. This ensures:

  - Uniformity: no free-form strings.
  - Interoperability: English values work with NIST/MITRE.
  - Analysability: codes are searchable and countable.

The code inherits from `str` so it serializes cleanly to JSON.
"""

from __future__ import annotations

from enum import StrEnum, unique


@unique
class ReasonCode(StrEnum):
    """All possible outcomes of a validation or verification."""

    # ---- Success ---------------------------------------------------------
    OK = "OK"

    # ---- Input validation ------------------------------------------------
    INVALID_TYPE = "INVALID_TYPE"
    MALFORMED_PAYLOAD = "MALFORMED_PAYLOAD"
    VALUE_NOT_FINITE = "VALUE_NOT_FINITE"
    VALUE_EXCEEDS_LIMIT = "VALUE_EXCEEDS_LIMIT"
    VALUE_BELOW_MIN = "VALUE_BELOW_MIN"
    TARGET_NOT_ALLOWED = "TARGET_NOT_ALLOWED"

    # ---- RBAC ------------------------------------------------------------
    ROLE_NOT_PERMITTED = "ROLE_NOT_PERMITTED"

    # ---- Message integrity -----------------------------------------------
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    REPLAY_DETECTED = "REPLAY_DETECTED"
    UNSUPPORTED_VERSION = "UNSUPPORTED_VERSION"
    INVALID_ENVELOPE = "INVALID_ENVELOPE"
    UNKNOWN_KEY_ID = "UNKNOWN_KEY_ID"

    # ---- Timing ----------------------------------------------------------
    TIMESTAMP_TOO_OLD = "TIMESTAMP_TOO_OLD"
    TIMESTAMP_FROM_FUTURE = "TIMESTAMP_FROM_FUTURE"

    # ---- Audit -----------------------------------------------------------
    AUDIT_FAILURE = "AUDIT_FAILURE"

    # ---- Fallback --------------------------------------------------------
    INTERNAL_ERROR = "INTERNAL_ERROR"
