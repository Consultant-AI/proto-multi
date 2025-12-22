"""
Proto AI Agent Structured Logging System.

Provides comprehensive, AI-readable logging for:
- User actions (messages, session management)
- Agent behavior (tool selection, execution)
- System events (server lifecycle, errors)

All logs are in JSON Lines format for easy parsing and analysis.
"""

from .structured_logger import (
    EventType,
    LogLevel,
    StructuredLogger,
    get_logger,
)

__all__ = [
    "EventType",
    "LogLevel",
    "StructuredLogger",
    "get_logger",
]
