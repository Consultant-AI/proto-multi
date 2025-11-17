"""
Agent SDK integration for computer-use-demo.

This module provides production-grade agent orchestration combining:
- Computer-use-demo's proven GUI automation
- Claude Agent SDK's advanced feedback loops and state management
"""

from .orchestrator import AgentOrchestrator
from .session import SessionManager
from .context_manager import ContextManager
from .subagents import SubagentCoordinator

__all__ = [
    "AgentOrchestrator",
    "SessionManager",
    "ContextManager",
    "SubagentCoordinator",
]
