"""
Orchestrator package.

Public API for the coordination layer.

Exports:
    SecureOrchestrator — coordinates Channel + Guardrail.
"""

from .core import SecureOrchestrator

__all__ = ["SecureOrchestrator"]
