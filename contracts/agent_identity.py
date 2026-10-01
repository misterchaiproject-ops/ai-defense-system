"""
Agent Identity.

Represents an agent in the system: its unique ID and its roles.
Both fields are immutable so the identity cannot be forged after
creation, and can be safely shared across threads.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .roles import Role

# Agent IDs must be simple ASCII identifiers.
_VALID_ID = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")


@dataclass(frozen=True, slots=True)
class AgentIdentity:
    """
    The immutable identity of an agent.

    Attributes:
        agent_id: A short, unique, ASCII identifier.
        roles: A non-empty set of roles the agent holds.
    """
    agent_id: str
    roles: frozenset[Role]

    def __post_init__(self) -> None:
        if not isinstance(self.agent_id, str):
            raise TypeError("agent_id must be a string")
        if not _VALID_ID.match(self.agent_id):
            raise ValueError(
                f"invalid agent_id (must match {_VALID_ID.pattern})"
            )
        if not isinstance(self.roles, frozenset):
            raise TypeError("roles must be a frozenset")
        if not self.roles:
            raise ValueError("roles must be non-empty")
        if not all(isinstance(r, Role) for r in self.roles):
            raise TypeError("all roles must be Role instances")

    def has_role(self, role: Role) -> bool:
        """Check whether this identity has a given role."""
        return role in self.roles
