"""
SecureOrchestrator — coordinates Channel + Guardrail.

Mandatory flow (enforced):
  Outbound:  Guardrail.validate -> Channel.create_message
  Inbound:   Channel.verify_message -> reconstruct Proposal -> Guardrail.validate

Design:
  - Fail-Closed: any failure returns None or a ValidationResult rejection.
  - Guardrail is MANDATORY on inbound (prevents AP-033).
  - TOCTOU-safe: the SAME Proposal object is validated and signed.
  - No generic exceptions; only ValidationResult in inbound flow.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from channel import Envelope, SecureAgentChannel
from contracts import (
    Action,
    AgentIdentity,
    Proposal,
    ReasonCode,
    ValidationResult,
)
from guardrail import DeterministicGuardrail

logger = logging.getLogger(__name__)


class SecureOrchestrator:
    """Coordinates Channel verification and Guardrail validation."""

    def __init__(
        self,
        *,
        channel: SecureAgentChannel,
        guardrail: DeterministicGuardrail,
    ) -> None:
        if not isinstance(channel, SecureAgentChannel):
            raise TypeError("channel must be a SecureAgentChannel")
        if not isinstance(guardrail, DeterministicGuardrail):
            raise TypeError("guardrail must be a DeterministicGuardrail")
        self._channel = channel
        self._guardrail = guardrail

    # ------------------------------------------------------------------
    # Outbound
    # ------------------------------------------------------------------
    def process_outbound(self, proposal: Proposal, identity: AgentIdentity) -> Envelope | None:
        """
        Validate a proposal, then sign it.

        Returns:
            Envelope if accepted, None if rejected.
        """
        # 1) Guardrail validation (outbound)
        v = self._guardrail.validate(proposal, identity)
        if not v.approved:
            logger.info("Outbound rejected: %s", v.reason.value)
            return None

        # 2) Sign the SAME Proposal object (TOCTOU-safe)
        try:
            envelope = self._channel.create_message(
                sender_id=identity.agent_id,
                payload=proposal.to_payload(),
            )
        except Exception:
            logger.exception("Outbound signing failed")
            return None

        return envelope

    # ------------------------------------------------------------------
    # Inbound
    # ------------------------------------------------------------------
    def process_inbound(self, envelope: Envelope, identity: AgentIdentity) -> ValidationResult:
        """
        Verify signature, then validate payload with Guardrail.

        Returns:
            ValidationResult — never raises.
        """
        # 1) Channel verification
        v_channel = self._channel.verify_message(envelope)
        if not v_channel.approved:
            return v_channel

        # 2) Reconstruct Proposal from verified payload
        try:
            proposal = _reconstruct_proposal(envelope.payload)
        except (KeyError, TypeError, ValueError):
            logger.warning("Malformed payload in inbound envelope")
            return ValidationResult.reject(ReasonCode.MALFORMED_PAYLOAD)

        # 3) Guardrail validation (MANDATORY — AP-033 prevention)
        return self._guardrail.validate(proposal, identity)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reconstruct_proposal(payload: Mapping[str, Any]) -> Proposal:
    """Rebuild a Proposal from a verified payload. Raises on malformed input."""
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a Mapping")

    action_str = payload.get("action")
    target = payload.get("target")
    value = payload.get("value")

    if not isinstance(action_str, str):
        raise ValueError("action must be a string")
    if not isinstance(target, str):
        raise ValueError("target must be a string")

    try:
        action = Action(action_str)
    except ValueError as e:
        raise ValueError(f"unknown action: {action_str!r}") from e

    return Proposal(action=action, target=target, value=value)
