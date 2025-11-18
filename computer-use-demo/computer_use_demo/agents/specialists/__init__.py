"""
Specialist Agents for Proto multi-agent system.

Each specialist has domain-specific expertise and can be
delegated tasks by the CEO agent.
"""

from .base_specialist import BaseSpecialist
from .design_agent import DesignAgent
from .developer_agent import DeveloperAgent
from .marketing_agent import MarketingAgent

__all__ = [
    "BaseSpecialist",
    "MarketingAgent",
    "DeveloperAgent",
    "DesignAgent",
]
