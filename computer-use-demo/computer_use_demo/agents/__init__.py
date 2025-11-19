"""
Proto Multi-Agent System.

Provides CEO agent for orchestration and specialist agents
for domain-specific expertise.
"""

from .base_agent import AgentConfig, AgentMessage, AgentResult, AgentRole, BaseAgent
from .ceo_agent import CEOAgent
from .specialists import (
    BaseSpecialist,
    CustomerSuccessAgent,
    DataAnalystAgent,
    DevOpsAgent,
    MarketingStrategyAgent,
    ProductManagerAgent,
    QATestingAgent,
    SalesAgent,
    SeniorDeveloperAgent,
    TechnicalWriterAgent,
    UXDesignerAgent,
)

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
    # Core SaaS Agents
    "ProductManagerAgent",
    "QATestingAgent",
    "DevOpsAgent",
    "TechnicalWriterAgent",
    "DataAnalystAgent",
    "CustomerSuccessAgent",
    "SalesAgent",
    # Original Agents
    "MarketingStrategyAgent",
    "SeniorDeveloperAgent",
    "UXDesignerAgent",
]
