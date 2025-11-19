"""
Specialist Agents for Proto multi-agent system.

Each specialist has domain-specific expertise and can be
delegated tasks by the CEO agent.
"""

from .base_specialist import BaseSpecialist
from .customer_success_agent import CustomerSuccessAgent
from .data_analyst_agent import DataAnalystAgent
from .devops_agent import DevOpsAgent
from .marketing_strategy_agent import MarketingStrategyAgent
from .product_manager_agent import ProductManagerAgent
from .qa_testing_agent import QATestingAgent
from .sales_agent import SalesAgent
from .senior_developer_agent import SeniorDeveloperAgent
from .technical_writer_agent import TechnicalWriterAgent
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
    # Original Agents
    "MarketingStrategyAgent",
    "SeniorDeveloperAgent",
    "UXDesignerAgent",
]
