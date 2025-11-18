"""
Proto Multi-Agent System.

Provides CEO agent for orchestration and specialist agents
for domain-specific expertise.
"""

from .base_agent import AgentConfig, AgentMessage, AgentResult, AgentRole, BaseAgent
from .ceo_agent import CEOAgent
from .specialists import BaseSpecialist, DesignAgent, DeveloperAgent, MarketingAgent

__all__ = [
    # Base
    "BaseAgent",
    "AgentConfig",
    "AgentMessage",
    "AgentResult",
    "AgentRole",
    # CEO
    "CEOAgent",
    # Specialists
    "BaseSpecialist",
    "MarketingAgent",
    "DeveloperAgent",
    "DesignAgent",
]
