"""
Specialist Agents for Proto multi-agent system.

Each specialist has domain-specific expertise and can be
delegated tasks by the CEO agent.
"""

from .base_specialist import BaseSpecialist
from .marketing_strategy_agent import MarketingStrategyAgent
from .senior_developer_agent import SeniorDeveloperAgent
from .ux_designer_agent import UXDesignerAgent

__all__ = [
    "BaseSpecialist",
    "MarketingStrategyAgent",
    "SeniorDeveloperAgent",
    "UXDesignerAgent",
]
