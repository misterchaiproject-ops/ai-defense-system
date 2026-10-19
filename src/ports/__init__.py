"""Stable interfaces for replaceable security infrastructure components.

The ports package contains dependency boundaries only. Concrete implementations
remain in their existing layers and are introduced incrementally in later phases.
"""

from .protocols import AuditSink, Clock, KeyProvider, ReplayStore

__all__ = ["AuditSink", "Clock", "KeyProvider", "ReplayStore"]
