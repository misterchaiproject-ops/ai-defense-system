"""
Immutable Agent Identity — the identity contract for RBAC.

An AgentIdentity carries two pieces of information:
  1. ``agent_id``: a short, ASCII-only, bounded identifier.
  2. ``roles``: a non-empty, immutable set of :class:`Role` members.

Security invariants enforced at construction:
  - ``agent_id`` must be a ``str`` matching an ASCII-only pattern
    (no whitespace, no control chars, no Unicode homographs).
  - ``agent_id`` length is bounded (1 to :data:`MAX_AGENT_ID_LENGTH`).
  - ``roles`` must be a ``frozenset`` (not a ``set``) so it cannot be
    mutated after construction.
  - ``roles`` must be non-empty, and its size must not exceed the
    total number of :class:`Role` members (defense against DoS via a
    huge set that forces O(n) iteration before rejection).
  - Every element of ``roles`` must be a :class:`Role` instance. This
    closes a critical RBAC bypass: without this check, an attacker
    could pass ``frozenset({"admin"})`` (a string) and impersonate an
    admin role. This is especially important because :class:`Role`
    subclasses :class:`str`, so ``Role.ADMIN == "admin"`` is ``True``
    in Python — the ``in`` operator would falsely match strings.

The class is ``frozen`` and ``slots``:
  - ``frozen``: prevents reassignment of ``agent_id`` or ``roles``
    after construction (TOCTOU protection).
  - ``slots``: reduces memory footprint and prevents accidental
    attribute creation.

Error message policy:
  - Public error messages are generic (they do NOT reveal internal
    regex patterns or validation logic).
  - Full details are emitted to the module's logger at DEBUG level
    for local diagnostics.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Final

from .roles import Role

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_AGENT_ID_LENGTH: Final[int] = 64

# The maximum number of roles any identity can hold is bounded by the
# number of :class:`Role` enum members.
_MAX_ROLES: Final[int] = len(Role)

# ASCII-only identifier: letters, digits, underscore, hyphen.
# ``fullmatch`` is required (not ``match``) to prevent a trailing
# newline from being accepted.
_VALID_ID: Final[re.Pattern[str]] = re.compile(rf"[A-Za-z0-9_\-]{{1,{MAX_AGENT_ID_LENGTH}}}")


# ---------------------------------------------------------------------------
# AgentIdentity
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AgentIdentity:
    """
    The immutable identity of an agent.

    Attributes:
        agent_id: A short, ASCII-only identifier, 1 to
            :data:`MAX_AGENT_ID_LENGTH` characters.
        roles: A non-empty, immutable set of :class:`Role` members,
            of size at most :data:`_MAX_ROLES`.

    Raises:
        TypeError: If ``agent_id`` is not a ``str``, if ``roles`` is
            not a ``frozenset``, or if ``roles`` contains a
            non-:class:`Role` element.
        ValueError: If ``agent_id`` does not match the allowed pattern
            (empty, too long, contains invalid characters), if
            ``roles`` is empty, or if ``roles`` exceeds
            :data:`_MAX_ROLES`.

    Note on ``has_role`` safety:
        The ``has_role`` method intentionally returns ``False`` (rather
        than raising) when called with a non-:class:`Role` argument.
        This is a deliberate Fail-Safe choice: an accidental call with
        a raw string cannot cause a privilege escalation because
        :class:`Role` subclasses :class:`str`, and ``"admin" in
        frozenset({Role.ADMIN})`` would otherwise be ``True`` in Python.
    """

    agent_id: str
    roles: frozenset[Role]

    def __post_init__(self) -> None:
        _validate_agent_id(self.agent_id)
        _validate_roles(self.roles)

    def has_role(self, role: Role) -> bool:
        """
        Check whether this identity holds the given role.

        Defensive at runtime: if ``role`` is not a :class:`Role`
        instance (e.g., a raw string was passed by untyped caller
        code), returns ``False`` rather than risking an accidental
        match. This is required because :class:`Role` subclasses
        :class:`str`, so ``"admin" in frozenset({Role.ADMIN})`` would
        otherwise return ``True``.

        Args:
            role: The role to check for.

        Returns:
            ``True`` if the identity holds the role, ``False``
            otherwise (including when ``role`` is not a Role).
        """
        if not isinstance(role, Role):
            return False
        return role in self.roles


# ---------------------------------------------------------------------------
# Validation helpers (module-private)
# ---------------------------------------------------------------------------


def _validate_agent_id(agent_id: object) -> None:
    """
    Enforce all ``agent_id`` invariants.

    Args:
        agent_id: The value to validate (typed as ``object`` because
            callers may pass anything at runtime).

    Raises:
        TypeError: If ``agent_id`` is not a string.
        ValueError: If ``agent_id`` is empty, too long, or contains
            characters outside the allowed ASCII set.
    """
    if not isinstance(agent_id, str):
        logger.debug("agent_id type check failed: %s", type(agent_id).__name__)
        raise TypeError(f"agent_id must be a str, got {type(agent_id).__name__}")
    if not _VALID_ID.fullmatch(agent_id):
        logger.debug(
            "agent_id pattern check failed: length=%d, repr=%r",
            len(agent_id),
            agent_id,
        )
        raise ValueError(
            "agent_id must be an ASCII identifier of "
            f"1 to {MAX_AGENT_ID_LENGTH} characters "
            "(letters, digits, underscore, hyphen)"
        )


def _validate_roles(roles: object) -> None:
    """
    Enforce all ``roles`` invariants.

    Order of checks (Fail-Fast, Fail-Closed):
      1. Container type (frozenset).
      2. Non-empty.
      3. Size bound (<= _MAX_ROLES) — prevents O(n) iteration on
         arbitrarily large frozensets.
      4. Element types (all must be Role instances).

    Args:
        roles: The value to validate (typed as ``object`` for
            zero-trust runtime validation).

    Raises:
        TypeError: If ``roles`` is not a frozenset, or if it contains
            a non-:class:`Role` element.
        ValueError: If ``roles`` is empty or exceeds :data:`_MAX_ROLES`.
    """
    if not isinstance(roles, frozenset):
        logger.debug("roles container check failed: %s", type(roles).__name__)
        raise TypeError(f"roles must be a frozenset, got {type(roles).__name__}")
    if not roles:
        logger.debug("roles emptiness check failed")
        raise ValueError("roles must be a non-empty frozenset")
    if len(roles) > _MAX_ROLES:
        logger.debug(
            "roles size check failed: got %d, max %d",
            len(roles),
            _MAX_ROLES,
        )
        raise ValueError(f"roles must not contain more than {_MAX_ROLES} elements")
    if not all(isinstance(r, Role) for r in roles):
        logger.debug("roles element type check failed")
        raise TypeError("roles must contain only Role instances")


__all__ = ["AgentIdentity", "MAX_AGENT_ID_LENGTH"]
