"""
Channel package.

Public API for the signed-messaging layer.

Exports:
    Envelope              — immutable signed message.
    SecureAgentChannel    — sign/verify envelopes.
    generate_shared_secret — helper to create a 256-bit secret.
"""

from .core import (
    Envelope,
    SecureAgentChannel,
    generate_shared_secret,
)

__all__ = [
    "Envelope",
    "SecureAgentChannel",
    "generate_shared_secret",
]
