"""
Specialist Agents for Proto multi-agent system.

Each specialist has domain-specific expertise and can be
delegated tasks by the CEO agent or other specialists.
"""

from .base_specialist import BaseSpecialist

# ===== EXISTING AGENTS =====
# Core SaaS Agents
from .customer_success_agent import CustomerSuccessAgent
from .data_analyst_agent import DataAnalystAgent
from .devops_agent import DevOpsAgent
from .product_manager_agent import ProductManagerAgent
from .qa_testing_agent import QATestingAgent
from .sales_agent import SalesAgent
from .technical_writer_agent import TechnicalWriterAgent
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
# Original Agents
from .marketing_strategy_agent import MarketingStrategyAgent
from .senior_developer_agent import SeniorDeveloperAgent
from .ux_designer_agent import UXDesignerAgent

# ===== NEW AGENTS =====
# C-Suite Executives
from .cto_agent import CTOAgent
from .cpo_agent import CPOAgent
from .cmo_agent import CMOAgent
from .cro_agent import CROAgent
from .cco_agent import CCOAgent
from .cdo_agent import CDOAgent
from .cfo_agent import CFOAgent
from .clo_agent import CLOAgent
from .chro_agent import CHROAgent

# Chief of Staff
from .inbox_triage_agent import InboxTriageAgent
from .decision_memo_agent import DecisionMemoAgent
from .meeting_agenda_agent import MeetingAgendaAgent
from .action_tracker_agent import ActionTrackerAgent
from .weekly_brief_agent import WeeklyBriefAgent
from .priority_resolver_agent import PriorityResolverAgent

# Strategy & Planning
from .vision_keeper_agent import VisionKeeperAgent
from .okr_coach_agent import OKRCoachAgent
from .kpi_definition_agent import KPIDefinitionAgent
from .resource_allocation_agent import ResourceAllocationAgent
from .scenario_planning_agent import ScenarioPlanningAgent
from .competitive_strategy_agent import CompetitiveStrategyAgent
from .strategic_initiative_agent import StrategicInitiativeAgent
from .business_model_agent import BusinessModelAgent
from .partnership_strategy_agent import PartnershipStrategyAgent
from .investment_thesis_agent import InvestmentThesisAgent

# Company Operating System
from .okr_tracker_agent import OKRTrackerAgent
from .wbr_agent import WBRAgent
from .metric_pack_agent import MetricPackAgent
from .anomaly_explanation_agent import AnomalyExplanationAgent
from .program_management_agent import ProgramManagementAgent
from .quality_governance_agent import QualityGovernanceAgent
from .policy_enforcement_agent import PolicyEnforcementAgent
from .incident_commander_agent import IncidentCommanderAgent
from .postmortem_agent import PostmortemAgent
from .runbook_agent import RunbookAgent
from .change_management_agent import ChangeManagementAgent
from .communication_agent import CommunicationAgent

# Experimentation & Learning
from .hypothesis_generator_agent import HypothesisGeneratorAgent
from .variant_generator_agent import VariantGeneratorAgent
from .experiment_design_agent import ExperimentDesignAgent
from .traffic_allocation_agent import TrafficAllocationAgent
from .results_interpretation_agent import ResultsInterpretationAgent
from .rollout_controller_agent import RolloutControllerAgent
from .learning_synthesis_agent import LearningSynthesisAgent

# Internal Knowledge
from .wiki_curator_agent import WikiCuratorAgent
from .faq_maintainer_agent import FAQMaintainerAgent
from .search_enhancer_agent import SearchEnhancerAgent
from .glossary_taxonomy_agent import GlossaryTaxonomyAgent

# Additional Product
from .roadmap_priority_agent import RoadmapPriorityAgent
from .feature_spec_agent import FeatureSpecAgent
from .competitor_tracker_agent import CompetitorTrackerAgent
from .user_story_agent import UserStoryAgent
from .release_notes_agent import ReleaseNotesAgent
from .beta_program_agent import BetaProgramAgent
from .product_analytics_agent import ProductAnalyticsAgent
from .feature_flag_agent import FeatureFlagAgent
from .localization_agent import LocalizationAgent
from .platform_api_agent import PlatformAPIAgent

# Core Orchestration
from .coo_execution_agent import COOExecutionAgent
from .pmo_program_agent import PMOProgramAgent
from .scheduler_agent import SchedulerAgent
from .policy_guardrails_agent import PolicyGuardrailsAgent
from .quality_audit_agent import QualityAuditAgent
from .observability_agent import ObservabilityAgent
from .experimentation_agent import ExperimentationAgent

# Product & Design
from .user_research_agent import UserResearchAgent
from .product_discovery_agent import ProductDiscoveryAgent
from .prd_spec_agent import PRDSpecAgent
from .ui_visual_design_agent import UIVisualDesignAgent
from .content_design_agent import ContentDesignAgent
from .accessibility_agent import AccessibilityAgent
from .usability_testing_agent import UsabilityTestingAgent

# Engineering
from .frontend_developer_agent import FrontendDeveloperAgent
from .backend_developer_agent import BackendDeveloperAgent
from .mobile_developer_agent import MobileDeveloperAgent
from .database_agent import DatabaseAgent
from .code_review_agent import CodeReviewAgent
from .build_ci_agent import BuildCIAgent
from .release_agent import ReleaseAgent
from .bug_triage_agent import BugTriageAgent

# Infrastructure / DevOps / IT
from .sre_agent import SREAgent
from .monitoring_agent import MonitoringAgent
from .cost_optimization_agent import CostOptimizationAgent
from .it_support_agent import ITSupportAgent
from .asset_license_agent import AssetLicenseAgent

# Data / Analytics / ML
from .data_engineering_agent import DataEngineeringAgent
from .experiment_analysis_agent import ExperimentAnalysisAgent
from .bi_reporting_agent import BIReportingAgent
from .forecasting_agent import ForecastingAgent
from .ml_engineer_agent import MLEngineerAgent
from .data_quality_agent import DataQualityAgent
from .privacy_pii_agent import PrivacyPIIAgent

# Marketing & Growth
from .market_research_agent import MarketResearchAgent
from .brand_agent import BrandAgent
from .seo_agent import SEOAgent
from .paid_acquisition_agent import PaidAcquisitionAgent
from .lifecycle_crm_agent import LifecycleCRMAgent
from .social_media_agent import SocialMediaAgent
from .pr_comms_agent import PRCommsAgent
from .creative_production_agent import CreativeProductionAgent

# Sales
from .lead_enrichment_agent import LeadEnrichmentAgent
from .prospecting_agent import ProspectingAgent
from .sdr_qualification_agent import SDRQualificationAgent
from .sales_ops_agent import SalesOpsAgent
from .deal_desk_agent import DealDeskAgent
from .sales_enablement_agent import SalesEnablementAgent
from .partner_channel_agent import PartnerChannelAgent

# Customer Success & Support
from .onboarding_agent import OnboardingAgent
from .support_triage_agent import SupportTriageAgent
from .support_resolution_agent import SupportResolutionAgent
from .knowledge_base_agent import KnowledgeBaseAgent
from .churn_prevention_agent import ChurnPreventionAgent
from .voice_of_customer_agent import VoiceOfCustomerAgent
from .community_agent import CommunityAgent

# Operations
from .vendor_management_agent import VendorManagementAgent
from .procurement_agent import ProcurementAgent
from .internal_tooling_agent import InternalToolingAgent

# Finance & Accounting
from .bookkeeping_agent import BookkeepingAgent
from .invoicing_ar_agent import InvoicingARAgent
from .accounts_payable_agent import AccountsPayableAgent
from .revenue_ops_agent import RevenueOpsAgent
from .tax_agent import TaxAgent
from .fraud_detection_agent import FraudDetectionAgent

# Legal, Compliance, Risk
from .contract_agent import ContractAgent
from .policy_agent import PolicyAgent
from .intellectual_property_agent import IntellectualPropertyAgent
from .regulatory_agent import RegulatoryAgent
from .risk_agent import RiskAgent

# People (HR) & Talent
from .recruiting_agent import RecruitingAgent
from .interview_loop_agent import InterviewLoopAgent
from .performance_agent import PerformanceAgent
from .learning_development_agent import LearningDevelopmentAgent
from .compensation_benefits_agent import CompensationBenefitsAgent

# Security
from .access_control_agent import AccessControlAgent
from .vulnerability_management_agent import VulnerabilityManagementAgent
from .incident_response_agent import IncidentResponseAgent
from .secure_sdlc_agent import SecureSDLCAgent


__all__ = [
    "BaseSpecialist",
    # ===== EXISTING AGENTS =====
    # Core SaaS
    "ProductManagerAgent",
    "QATestingAgent",
    "DevOpsAgent",
    "TechnicalWriterAgent",
    "DataAnalystAgent",
    "CustomerSuccessAgent",
    "SalesAgent",
    # Extended SaaS
    "FinanceAgent",
    "SecurityAgent",
    "ContentMarketingAgent",
    "GrowthAnalyticsAgent",
    "LegalComplianceAgent",
    "HRPeopleAgent",
    "BusinessOperationsAgent",
    "ProductStrategyAgent",
    "AdminCoordinatorAgent",
    # Original
    "MarketingStrategyAgent",
    "SeniorDeveloperAgent",
    "UXDesignerAgent",
    # ===== NEW AGENTS =====
    # C-Suite Executives
    "CTOAgent",
    "CPOAgent",
    "CMOAgent",
    "CROAgent",
    "CCOAgent",
    "CDOAgent",
    "CFOAgent",
    "CLOAgent",
    "CHROAgent",
    # Chief of Staff
    "InboxTriageAgent",
    "DecisionMemoAgent",
    "MeetingAgendaAgent",
    "ActionTrackerAgent",
    "WeeklyBriefAgent",
    "PriorityResolverAgent",
    # Strategy & Planning
    "VisionKeeperAgent",
    "OKRCoachAgent",
    "KPIDefinitionAgent",
    "ResourceAllocationAgent",
    "ScenarioPlanningAgent",
    "CompetitiveStrategyAgent",
    "StrategicInitiativeAgent",
    "BusinessModelAgent",
    "PartnershipStrategyAgent",
    "InvestmentThesisAgent",
    # Company Operating System
    "OKRTrackerAgent",
    "WBRAgent",
    "MetricPackAgent",
    "AnomalyExplanationAgent",
    "ProgramManagementAgent",
    "QualityGovernanceAgent",
    "PolicyEnforcementAgent",
    "IncidentCommanderAgent",
    "PostmortemAgent",
    "RunbookAgent",
    "ChangeManagementAgent",
    "CommunicationAgent",
    # Experimentation & Learning
    "HypothesisGeneratorAgent",
    "VariantGeneratorAgent",
    "ExperimentDesignAgent",
    "TrafficAllocationAgent",
    "ResultsInterpretationAgent",
    "RolloutControllerAgent",
    "LearningSynthesisAgent",
    # Internal Knowledge
    "WikiCuratorAgent",
    "FAQMaintainerAgent",
    "SearchEnhancerAgent",
    "GlossaryTaxonomyAgent",
    # Additional Product
    "RoadmapPriorityAgent",
    "FeatureSpecAgent",
    "CompetitorTrackerAgent",
    "UserStoryAgent",
    "ReleaseNotesAgent",
    "BetaProgramAgent",
    "ProductAnalyticsAgent",
    "FeatureFlagAgent",
    "LocalizationAgent",
    "PlatformAPIAgent",
    # Core Orchestration
    "COOExecutionAgent",
    "PMOProgramAgent",
    "SchedulerAgent",
    "PolicyGuardrailsAgent",
    "QualityAuditAgent",
    "ObservabilityAgent",
    "ExperimentationAgent",
    # Product & Design
    "UserResearchAgent",
    "ProductDiscoveryAgent",
    "PRDSpecAgent",
    "UIVisualDesignAgent",
    "ContentDesignAgent",
    "AccessibilityAgent",
    "UsabilityTestingAgent",
    # Engineering
    "FrontendDeveloperAgent",
    "BackendDeveloperAgent",
    "MobileDeveloperAgent",
    "DatabaseAgent",
    "CodeReviewAgent",
    "BuildCIAgent",
    "ReleaseAgent",
    "BugTriageAgent",
    # Infrastructure / DevOps / IT
    "SREAgent",
    "MonitoringAgent",
    "CostOptimizationAgent",
    "ITSupportAgent",
    "AssetLicenseAgent",
    # Data / Analytics / ML
    "DataEngineeringAgent",
    "ExperimentAnalysisAgent",
    "BIReportingAgent",
    "ForecastingAgent",
    "MLEngineerAgent",
    "DataQualityAgent",
    "PrivacyPIIAgent",
    # Marketing & Growth
    "MarketResearchAgent",
    "BrandAgent",
    "SEOAgent",
    "PaidAcquisitionAgent",
    "LifecycleCRMAgent",
    "SocialMediaAgent",
    "PRCommsAgent",
    "CreativeProductionAgent",
    # Sales
    "LeadEnrichmentAgent",
    "ProspectingAgent",
    "SDRQualificationAgent",
    "SalesOpsAgent",
    "DealDeskAgent",
    "SalesEnablementAgent",
    "PartnerChannelAgent",
    # Customer Success & Support
    "OnboardingAgent",
    "SupportTriageAgent",
    "SupportResolutionAgent",
    "KnowledgeBaseAgent",
    "ChurnPreventionAgent",
    "VoiceOfCustomerAgent",
    "CommunityAgent",
    # Operations
    "VendorManagementAgent",
    "ProcurementAgent",
    "InternalToolingAgent",
    # Finance & Accounting
    "BookkeepingAgent",
    "InvoicingARAgent",
    "AccountsPayableAgent",
    "RevenueOpsAgent",
    "TaxAgent",
    "FraudDetectionAgent",
    # Legal, Compliance, Risk
    "ContractAgent",
    "PolicyAgent",
    "IntellectualPropertyAgent",
    "RegulatoryAgent",
    "RiskAgent",
    # People (HR) & Talent
    "RecruitingAgent",
    "InterviewLoopAgent",
    "PerformanceAgent",
    "LearningDevelopmentAgent",
    "CompensationBenefitsAgent",
    # Security
    "AccessControlAgent",
    "VulnerabilityManagementAgent",
    "IncidentResponseAgent",
    "SecureSDLCAgent",
]
