"""
Proto Multi-Agent System.

Provides CEO agent for orchestration and specialist agents
for domain-specific expertise.
"""

from typing import Optional

from .base_agent import AgentConfig, AgentMessage, AgentResult, AgentRole, BaseAgent
from .ceo_agent import CEOAgent
from .specialists import (
    # Base
    BaseSpecialist,
    # ===== EXISTING AGENTS =====
    # Core SaaS Agents
    AdminCoordinatorAgent,
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
    # ===== NEW AGENTS =====
    # C-Suite Executives
    CTOAgent,
    CPOAgent,
    CMOAgent,
    CROAgent,
    CCOAgent,
    CDOAgent,
    CFOAgent,
    CLOAgent,
    CHROAgent,
    # Chief of Staff
    InboxTriageAgent,
    DecisionMemoAgent,
    MeetingAgendaAgent,
    ActionTrackerAgent,
    WeeklyBriefAgent,
    PriorityResolverAgent,
    # Strategy & Planning
    VisionKeeperAgent,
    OKRCoachAgent,
    KPIDefinitionAgent,
    ResourceAllocationAgent,
    ScenarioPlanningAgent,
    CompetitiveStrategyAgent,
    StrategicInitiativeAgent,
    BusinessModelAgent,
    PartnershipStrategyAgent,
    InvestmentThesisAgent,
    # Company Operating System
    OKRTrackerAgent,
    WBRAgent,
    MetricPackAgent,
    AnomalyExplanationAgent,
    ProgramManagementAgent,
    QualityGovernanceAgent,
    PolicyEnforcementAgent,
    IncidentCommanderAgent,
    PostmortemAgent,
    RunbookAgent,
    ChangeManagementAgent,
    CommunicationAgent,
    # Experimentation & Learning
    HypothesisGeneratorAgent,
    VariantGeneratorAgent,
    ExperimentDesignAgent,
    TrafficAllocationAgent,
    ResultsInterpretationAgent,
    RolloutControllerAgent,
    LearningSynthesisAgent,
    # Internal Knowledge
    WikiCuratorAgent,
    FAQMaintainerAgent,
    SearchEnhancerAgent,
    GlossaryTaxonomyAgent,
    # Additional Product
    RoadmapPriorityAgent,
    FeatureSpecAgent,
    CompetitorTrackerAgent,
    UserStoryAgent,
    ReleaseNotesAgent,
    BetaProgramAgent,
    ProductAnalyticsAgent,
    FeatureFlagAgent,
    LocalizationAgent,
    PlatformAPIAgent,
    # Core Orchestration
    COOExecutionAgent,
    PMOProgramAgent,
    SchedulerAgent,
    PolicyGuardrailsAgent,
    QualityAuditAgent,
    ObservabilityAgent,
    ExperimentationAgent,
    # Product & Design
    UserResearchAgent,
    ProductDiscoveryAgent,
    PRDSpecAgent,
    UIVisualDesignAgent,
    ContentDesignAgent,
    AccessibilityAgent,
    UsabilityTestingAgent,
    # Engineering
    FrontendDeveloperAgent,
    BackendDeveloperAgent,
    MobileDeveloperAgent,
    DatabaseAgent,
    CodeReviewAgent,
    BuildCIAgent,
    ReleaseAgent,
    BugTriageAgent,
    # Infrastructure / DevOps / IT
    SREAgent,
    MonitoringAgent,
    CostOptimizationAgent,
    ITSupportAgent,
    AssetLicenseAgent,
    # Data / Analytics / ML
    DataEngineeringAgent,
    ExperimentAnalysisAgent,
    BIReportingAgent,
    ForecastingAgent,
    MLEngineerAgent,
    DataQualityAgent,
    PrivacyPIIAgent,
    # Marketing & Growth
    MarketResearchAgent,
    BrandAgent,
    SEOAgent,
    PaidAcquisitionAgent,
    LifecycleCRMAgent,
    SocialMediaAgent,
    PRCommsAgent,
    CreativeProductionAgent,
    # Sales
    LeadEnrichmentAgent,
    ProspectingAgent,
    SDRQualificationAgent,
    SalesOpsAgent,
    DealDeskAgent,
    SalesEnablementAgent,
    PartnerChannelAgent,
    # Customer Success & Support
    OnboardingAgent,
    SupportTriageAgent,
    SupportResolutionAgent,
    KnowledgeBaseAgent,
    ChurnPreventionAgent,
    VoiceOfCustomerAgent,
    CommunityAgent,
    # Operations
    VendorManagementAgent,
    ProcurementAgent,
    InternalToolingAgent,
    # Finance & Accounting
    BookkeepingAgent,
    InvoicingARAgent,
    AccountsPayableAgent,
    RevenueOpsAgent,
    TaxAgent,
    FraudDetectionAgent,
    # Legal, Compliance, Risk
    ContractAgent,
    PolicyAgent,
    IntellectualPropertyAgent,
    RegulatoryAgent,
    RiskAgent,
    # People (HR) & Talent
    RecruitingAgent,
    InterviewLoopAgent,
    PerformanceAgent,
    LearningDevelopmentAgent,
    CompensationBenefitsAgent,
    # Security
    AccessControlAgent,
    VulnerabilityManagementAgent,
    IncidentResponseAgent,
    SecureSDLCAgent,
)

# Agent registry mapping names to classes
AGENT_REGISTRY = {
    # CEO
    "ceo-agent": CEOAgent,
    # ===== EXISTING AGENTS =====
    # Core SaaS Agents
    "product-manager": ProductManagerAgent,
    "qa-testing": QATestingAgent,
    "devops": DevOpsAgent,
    "technical-writer": TechnicalWriterAgent,
    "data-analyst": DataAnalystAgent,
    "customer-success": CustomerSuccessAgent,
    "sales": SalesAgent,
    # Extended SaaS Agents
    "finance": FinanceAgent,
    "security": SecurityAgent,
    "content-marketing": ContentMarketingAgent,
    "growth-analytics": GrowthAnalyticsAgent,
    "legal-compliance": LegalComplianceAgent,
    "hr-people": HRPeopleAgent,
    "business-operations": BusinessOperationsAgent,
    "product-strategy": ProductStrategyAgent,
    "admin-coordinator": AdminCoordinatorAgent,
    # Original Agents
    "marketing-strategy": MarketingStrategyAgent,
    "senior-developer": SeniorDeveloperAgent,
    "ux-designer": UXDesignerAgent,
    # ===== NEW AGENTS =====
    # C-Suite Executives
    "cto": CTOAgent,
    "cpo": CPOAgent,
    "cmo": CMOAgent,
    "cro": CROAgent,
    "cco": CCOAgent,
    "cdo": CDOAgent,
    "cfo": CFOAgent,
    "clo": CLOAgent,
    "chro": CHROAgent,
    # Chief of Staff
    "inbox-triage": InboxTriageAgent,
    "decision-memo": DecisionMemoAgent,
    "meeting-agenda": MeetingAgendaAgent,
    "action-tracker": ActionTrackerAgent,
    "weekly-brief": WeeklyBriefAgent,
    "priority-resolver": PriorityResolverAgent,
    # Strategy & Planning
    "vision-keeper": VisionKeeperAgent,
    "okr-coach": OKRCoachAgent,
    "kpi-definition": KPIDefinitionAgent,
    "resource-allocation": ResourceAllocationAgent,
    "scenario-planning": ScenarioPlanningAgent,
    "competitive-strategy": CompetitiveStrategyAgent,
    "strategic-initiative": StrategicInitiativeAgent,
    "business-model": BusinessModelAgent,
    "partnership-strategy": PartnershipStrategyAgent,
    "investment-thesis": InvestmentThesisAgent,
    # Company Operating System
    "okr-tracker": OKRTrackerAgent,
    "wbr": WBRAgent,
    "metric-pack": MetricPackAgent,
    "anomaly-explanation": AnomalyExplanationAgent,
    "program-management": ProgramManagementAgent,
    "quality-governance": QualityGovernanceAgent,
    "policy-enforcement": PolicyEnforcementAgent,
    "incident-commander": IncidentCommanderAgent,
    "postmortem": PostmortemAgent,
    "runbook": RunbookAgent,
    "change-management": ChangeManagementAgent,
    "communication": CommunicationAgent,
    # Experimentation & Learning
    "hypothesis-generator": HypothesisGeneratorAgent,
    "variant-generator": VariantGeneratorAgent,
    "experiment-design": ExperimentDesignAgent,
    "traffic-allocation": TrafficAllocationAgent,
    "results-interpretation": ResultsInterpretationAgent,
    "rollout-controller": RolloutControllerAgent,
    "learning-synthesis": LearningSynthesisAgent,
    # Internal Knowledge
    "wiki-curator": WikiCuratorAgent,
    "faq-maintainer": FAQMaintainerAgent,
    "search-enhancer": SearchEnhancerAgent,
    "glossary-taxonomy": GlossaryTaxonomyAgent,
    # Additional Product
    "roadmap-priority": RoadmapPriorityAgent,
    "feature-spec": FeatureSpecAgent,
    "competitor-tracker": CompetitorTrackerAgent,
    "user-story": UserStoryAgent,
    "release-notes": ReleaseNotesAgent,
    "beta-program": BetaProgramAgent,
    "product-analytics": ProductAnalyticsAgent,
    "feature-flag": FeatureFlagAgent,
    "localization": LocalizationAgent,
    "platform-api": PlatformAPIAgent,
    # Core Orchestration
    "coo-execution": COOExecutionAgent,
    "pmo-program": PMOProgramAgent,
    "scheduler": SchedulerAgent,
    "policy-guardrails": PolicyGuardrailsAgent,
    "quality-audit": QualityAuditAgent,
    "observability": ObservabilityAgent,
    "experimentation": ExperimentationAgent,
    # Product & Design
    "user-research": UserResearchAgent,
    "product-discovery": ProductDiscoveryAgent,
    "prd-spec": PRDSpecAgent,
    "ui-visual-design": UIVisualDesignAgent,
    "content-design": ContentDesignAgent,
    "accessibility": AccessibilityAgent,
    "usability-testing": UsabilityTestingAgent,
    # Engineering
    "frontend-developer": FrontendDeveloperAgent,
    "backend-developer": BackendDeveloperAgent,
    "mobile-developer": MobileDeveloperAgent,
    "database": DatabaseAgent,
    "code-review": CodeReviewAgent,
    "build-ci": BuildCIAgent,
    "release": ReleaseAgent,
    "bug-triage": BugTriageAgent,
    # Infrastructure / DevOps / IT
    "sre": SREAgent,
    "monitoring": MonitoringAgent,
    "cost-optimization": CostOptimizationAgent,
    "it-support": ITSupportAgent,
    "asset-license": AssetLicenseAgent,
    # Data / Analytics / ML
    "data-engineering": DataEngineeringAgent,
    "experiment-analysis": ExperimentAnalysisAgent,
    "bi-reporting": BIReportingAgent,
    "forecasting": ForecastingAgent,
    "ml-engineer": MLEngineerAgent,
    "data-quality": DataQualityAgent,
    "privacy-pii": PrivacyPIIAgent,
    # Marketing & Growth
    "market-research": MarketResearchAgent,
    "brand": BrandAgent,
    "seo": SEOAgent,
    "paid-acquisition": PaidAcquisitionAgent,
    "lifecycle-crm": LifecycleCRMAgent,
    "social-media": SocialMediaAgent,
    "pr-comms": PRCommsAgent,
    "creative-production": CreativeProductionAgent,
    # Sales
    "lead-enrichment": LeadEnrichmentAgent,
    "prospecting": ProspectingAgent,
    "sdr-qualification": SDRQualificationAgent,
    "sales-ops": SalesOpsAgent,
    "deal-desk": DealDeskAgent,
    "sales-enablement": SalesEnablementAgent,
    "partner-channel": PartnerChannelAgent,
    # Customer Success & Support
    "onboarding": OnboardingAgent,
    "support-triage": SupportTriageAgent,
    "support-resolution": SupportResolutionAgent,
    "knowledge-base": KnowledgeBaseAgent,
    "churn-prevention": ChurnPreventionAgent,
    "voice-of-customer": VoiceOfCustomerAgent,
    "community": CommunityAgent,
    # Operations
    "vendor-management": VendorManagementAgent,
    "procurement": ProcurementAgent,
    "internal-tooling": InternalToolingAgent,
    # Finance & Accounting
    "bookkeeping": BookkeepingAgent,
    "invoicing-ar": InvoicingARAgent,
    "accounts-payable": AccountsPayableAgent,
    "revenue-ops": RevenueOpsAgent,
    "tax": TaxAgent,
    "fraud-detection": FraudDetectionAgent,
    # Legal, Compliance, Risk
    "contract": ContractAgent,
    "policy": PolicyAgent,
    "intellectual-property": IntellectualPropertyAgent,
    "regulatory": RegulatoryAgent,
    "risk": RiskAgent,
    # People (HR) & Talent
    "recruiting": RecruitingAgent,
    "interview-loop": InterviewLoopAgent,
    "performance": PerformanceAgent,
    "learning-development": LearningDevelopmentAgent,
    "compensation-benefits": CompensationBenefitsAgent,
    # Security
    "access-control": AccessControlAgent,
    "vulnerability-management": VulnerabilityManagementAgent,
    "incident-response": IncidentResponseAgent,
    "secure-sdlc": SecureSDLCAgent,
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
    # Specialists Base
    "BaseSpecialist",
    # ===== EXISTING AGENTS =====
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
    # Utilities
    "create_agent_by_name",
    "list_available_agents",
]
