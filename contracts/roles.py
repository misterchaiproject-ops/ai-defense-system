"""
Roles for RBAC (Role-Based Access Control).

Roles determine which actions an agent may propose.
The mapping from roles to actions lives in the Guardrail.
"""

from __future__ import annotations

from enum import Enum, unique


@unique
class Role(str, Enum):
    """
    The set of roles an agent can hold.

    An agent may hold multiple roles simultaneously.
    """
    OBSERVER = "observer"
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"
