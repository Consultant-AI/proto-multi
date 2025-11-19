"""
Specialist Agents for Proto multi-agent system.

Each specialist has domain-specific expertise and can be
delegated tasks by the CEO agent.
"""

from .base_specialist import BaseSpecialist
# Extended SaaS Agents
from .admin_coordinator_agent import AdminCoordinatorAgent
from .business_operations_agent import BusinessOperationsAgent
from .content_marketing_agent import ContentMarketingAgent
from .finance_agent import FinanceAgent
from .growth_analytics_agent import GrowthAnalyticsAgent
from .hr_people_agent import HRPeopleAgent
from .legal_compliance_agent import LegalComplianceAgent
from .product_strategy_agent import ProductStrategyAgent
from .security_agent import SecurityAgent
# Core SaaS Agents
from .customer_success_agent import CustomerSuccessAgent
from .data_analyst_agent import DataAnalystAgent
from .devops_agent import DevOpsAgent
from .product_manager_agent import ProductManagerAgent
from .qa_testing_agent import QATestingAgent
from .sales_agent import SalesAgent
from .technical_writer_agent import TechnicalWriterAgent
# Original Agents
from .marketing_strategy_agent import MarketingStrategyAgent
from .senior_developer_agent import SeniorDeveloperAgent
from .ux_designer_agent import UXDesignerAgent

__all__ = [
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
]
