"""
DeterministicGuardrail — the deterministic validation layer.

This is the security heart of the system. It performs stateless,
O(1) checks on every Proposal:

  1. Target allowlist (only known systems).
  2. RBAC (role permits the action).
  3. Operational limits (value within [min, max]).
  4. Required value (some actions must carry a value).

Design:
  - Stateless: safe to share across threads.
  - Fail-Closed: any exception -> REJECT.
  - O(1) per check: no loops over lists.
  - No string comparisons where Enums suffice.
"""

from __future__ import annotations

import logging
import math
from types import MappingProxyType
from typing import FrozenSet, Mapping, Optional

from contracts import (
    Action,
    AgentIdentity,
    Proposal,
    ReasonCode,
    Role,
    ValidationResult,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# RBAC matrix: action -> roles allowed to perform it
# ---------------------------------------------------------------------------

_ACTION_ROLES: Mapping[Action, FrozenSet[Role]] = MappingProxyType({
    Action.READ_STATE: frozenset({
        Role.OBSERVER, Role.OPERATOR, Role.SUPERVISOR, Role.ADMIN,
    }),
    Action.ADJUST_METRIC: frozenset({
        Role.OPERATOR, Role.SUPERVISOR, Role.ADMIN,
    }),
    Action.MODIFY_STATE: frozenset({
        Role.SUPERVISOR, Role.ADMIN,
    }),
    Action.SHUTDOWN: frozenset({
        Role.SUPERVISOR, Role.ADMIN,
    }),
})


# Actions that REQUIRE a numeric value
_REQUIRES_VALUE: FrozenSet[Action] = frozenset({
    Action.ADJUST_METRIC,
    Action.MODIFY_STATE,
})


class DeterministicGuardrail:
    """
    Stateless, thread-safe guardrail.

    Validates a Proposal against:
      - Target allowlist
      - RBAC rules
      - Operational limits
      - Required-value rules
    """

    def __init__(
        self,
        operational_limits: Mapping[str, float],
        *,
        min_values: Optional[Mapping[str, float]] = None,
    ) -> None:
        # ---- Validate limits ----
        if not isinstance(operational_limits, Mapping) or not operational_limits:
            raise ValueError("operational_limits must be a non-empty Mapping")

        clean_limits: dict[str, float] = {}
        for target, limit in operational_limits.items():
            if not isinstance(target, str) or not target.strip():
                raise ValueError(f"invalid target key: {target!r}")
            if isinstance(limit, bool) or not isinstance(limit, (int, float)):
                raise TypeError(f"limit for {target!r} must be numeric")
            if not math.isfinite(limit) or limit < 0:
                raise ValueError(
                    f"limit for {target!r} must be finite and >= 0"
                )
            clean_limits[target] = float(limit)

        # ---- Validate min_values ----
        clean_mins: dict[str, float] = {}
        if min_values is not None:
            for target, min_val in min_values.items():
                if target not in clean_limits:
                    raise ValueError(f"min for unknown target: {target!r}")
                if isinstance(min_val, bool) or not isinstance(min_val, (int, float)):
                    raise TypeError(f"min for {target!r} must be numeric")
                if not math.isfinite(min_val):
                    raise ValueError(f"min for {target!r} must be finite")
                if min_val > clean_limits[target]:
                    raise ValueError(f"min > max for {target!r}")
                clean_mins[target] = float(min_val)

        # ---- Immutable internal state ----
        self._limits: Mapping[str, float] = MappingProxyType(clean_limits)
        self._mins: Mapping[str, float] = MappingProxyType(clean_mins)
        self._targets: FrozenSet[str] = frozenset(clean_limits.keys())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def validate(
        self, proposal: Proposal, identity: AgentIdentity
    ) -> ValidationResult:
        """
        Validate a proposal from a given identity.

        Returns ValidationResult — never raises.
        """
        try:
            # 1) Type checks (should never fire if callers use the contracts)
            if not isinstance(proposal, Proposal):
                return ValidationResult.reject(ReasonCode.INVALID_TYPE)
            if not isinstance(identity, AgentIdentity):
                return ValidationResult.reject(ReasonCode.INVALID_TYPE)

            # 2) Target allowlist
            if proposal.target not in self._targets:
                return ValidationResult.reject(
                    ReasonCode.TARGET_NOT_ALLOWED,
                    target=proposal.target,
                )

            # 3) RBAC
            allowed_roles = _ACTION_ROLES.get(proposal.action, frozenset())
            if not (identity.roles & allowed_roles):
                return ValidationResult.reject(
                    ReasonCode.ROLE_NOT_PERMITTED,
                    action=proposal.action.value,
                )

            # 4) Value checks (only if value is present)
            if proposal.value is not None:
                if not math.isfinite(proposal.value):
                    return ValidationResult.reject(
                        ReasonCode.VALUE_NOT_FINITE
                    )
                max_allowed = self._limits[proposal.target]
                if proposal.value > max_allowed:
                    return ValidationResult.reject(
                        ReasonCode.VALUE_EXCEEDS_LIMIT,
                        value=proposal.value,
                        max=max_allowed,
                    )
                min_allowed = self._mins.get(proposal.target)
                if min_allowed is not None and proposal.value < min_allowed:
                    return ValidationResult.reject(
                        ReasonCode.VALUE_BELOW_MIN,
                        value=proposal.value,
                        min=min_allowed,
                    )

            # 5) Required value
            if proposal.action in _REQUIRES_VALUE and proposal.value is None:
                return ValidationResult.reject(
                    ReasonCode.MALFORMED_PAYLOAD,
                    detail="action requires a value",
                )

            # 6) All checks passed
            return ValidationResult.ok()

        except Exception:
            # Fail-Closed: any unexpected error -> reject
            logger.exception("Guardrail internal error")
            return ValidationResult.reject(ReasonCode.INTERNAL_ERROR)
