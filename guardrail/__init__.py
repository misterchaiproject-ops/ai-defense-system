"""
Guardrail package.

Public API for the deterministic validation layer.

Exports:
    DeterministicGuardrail — stateless proposal validator.
"""

from .core import DeterministicGuardrail

__all__ = ["DeterministicGuardrail"]
