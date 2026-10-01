"""
Actions an agent may propose.

This module defines the closed set of allowed actions in the system.
Using an Enum (not free-form strings) prevents typos and injection.
"""

from __future__ import annotations

from enum import StrEnum, unique


@unique
class Action(StrEnum):
    """
    The complete list of actions an agent may propose.

    Inherits from `str` so it serializes cleanly to JSON.
    """

    READ_STATE = "read_state"
    ADJUST_METRIC = "adjust_metric"
    MODIFY_STATE = "modify_state"
    SHUTDOWN = "shutdown"
