"""
Contracts package.

Public API for the entire system. Every other layer imports from
this package — never from individual modules.

Exports:
    Action            — allowed actions
    AgentIdentity     — agent identity (ID + roles)
    Proposal          — immutable proposal
    ReasonCode        — validation outcome codes
    Role              — agent roles
    ValidationResult  — outcome of any validation
"""

from .actions import Action
from .agent_identity import AgentIdentity
from .proposal import Proposal
from .reason_codes import ReasonCode
from .roles import Role
from .validation_result import ValidationResult

__all__ = [
    "Action",
    "AgentIdentity",
    "Proposal",
    "ReasonCode",
    "Role",
    "ValidationResult",
]
