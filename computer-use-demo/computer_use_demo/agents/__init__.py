"""
Proto Multi-Agent System.

Provides CEO agent for orchestration and specialist agents
for domain-specific expertise.
"""

from typing import Optional

from .base_agent import AgentConfig, AgentMessage, AgentResult, AgentRole, BaseAgent
from .ceo_agent import CEOAgent
from .specialists import (
    AdminCoordinatorAgent,
    BaseSpecialist,
    BusinessOperationsAgent,
    ContentMarketingAgent,
    CustomerSuccessAgent,
    DataAnalystAgent,
    DevOpsAgent,
    FinanceAgent,
    GrowthAnalyticsAgent,
    HRPeopleAgent,
    LegalComplianceAgent,
    MarketingStrategyAgent,
    ProductManagerAgent,
    ProductStrategyAgent,
    QATestingAgent,
    SalesAgent,
    SecurityAgent,
    SeniorDeveloperAgent,
    TechnicalWriterAgent,
    UXDesignerAgent,
)

# Agent registry mapping names to classes
AGENT_REGISTRY = {
    "ceo-agent": CEOAgent,
    "product-manager": ProductManagerAgent,
    "qa-testing": QATestingAgent,
    "devops": DevOpsAgent,
    "technical-writer": TechnicalWriterAgent,
    "data-analyst": DataAnalystAgent,
    "customer-success": CustomerSuccessAgent,
    "sales": SalesAgent,
    "finance": FinanceAgent,
    "security": SecurityAgent,
    "content-marketing": ContentMarketingAgent,
    "growth-analytics": GrowthAnalyticsAgent,
    "legal-compliance": LegalComplianceAgent,
    "hr-people": HRPeopleAgent,
    "business-operations": BusinessOperationsAgent,
    "product-strategy": ProductStrategyAgent,
    "admin-coordinator": AdminCoordinatorAgent,
    "marketing-strategy": MarketingStrategyAgent,
    "senior-developer": SeniorDeveloperAgent,
    "ux-designer": UXDesignerAgent,
}


def create_agent_by_name(agent_name: str, **kwargs) -> Optional[BaseAgent]:
    """
    Create an agent instance by name.

    Args:
        agent_name: Name of agent (e.g., "ceo-agent", "senior-developer")
        **kwargs: Additional arguments to pass to agent constructor

    Returns:
        Agent instance or None if not found
    """
    agent_class = AGENT_REGISTRY.get(agent_name)
    if not agent_class:
        return None

    return agent_class(**kwargs)


def list_available_agents() -> list[str]:
    """Get list of all available agent names."""
    return list(AGENT_REGISTRY.keys())


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
    # Extended SaaS Agents
    "FinanceAgent",
    "SecurityAgent",
    "ContentMarketingAgent",
    "GrowthAnalyticsAgent",
    "LegalComplianceAgent",
    "HRPeopleAgent",
    "BusinessOperationsAgent",
    "ProductStrategyAgent",
    "AdminCoordinatorAgent",
    # Original Agents
    "MarketingStrategyAgent",
    "SeniorDeveloperAgent",
    "UXDesignerAgent",
    # Utilities
    "create_agent_by_name",
    "list_available_agents",
]
