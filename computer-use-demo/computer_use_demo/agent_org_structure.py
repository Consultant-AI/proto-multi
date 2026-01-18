"""
Company-wide organizational structure for all specialist agents.

This defines the complete hierarchy of agents available in the system,
structured as a company org chart with CEO at the top.

NOTE: This hierarchy is for UI navigation purposes only. The actual agent
system is peer-to-peer where any agent can delegate to any other agent.
"""

from typing import TypedDict, NotRequired


class AgentNode(TypedDict):
    """Represents a single agent in the organizational tree."""
    id: str  # Agent identifier (matches role slug)
    name: str  # Display name
    description: str  # Brief description
    icon: str  # Icon/emoji for UI
    sub_agents: NotRequired[list['AgentNode']]  # Optional nested sub-agents


# Complete company org chart - single tree structure under CEO
COMPANY_ORG_TREE: AgentNode = {
    "id": "ceo-agent",
    "name": "CEO",
    "description": "Chief Executive Officer - Strategic oversight & orchestration",
    "icon": "👔",
    "sub_agents": [
        # Chief of Staff
        {
            "id": "inbox-triage",
            "name": "Chief of Staff",
            "description": "Executive support & coordination",
            "icon": "📬",
            "sub_agents": [
                {"id": "decision-memo", "name": "Decision Memo Writer", "description": "Decision documentation & analysis", "icon": "📝"},
                {"id": "meeting-agenda", "name": "Meeting Agenda", "description": "Meeting preparation & pre-reads", "icon": "📋"},
                {"id": "action-tracker", "name": "Action Tracker", "description": "Follow-up tracking & accountability", "icon": "✅"},
                {"id": "weekly-brief", "name": "Weekly Brief", "description": "What changed this week summaries", "icon": "📰"},
                {"id": "priority-resolver", "name": "Priority Resolver", "description": "Priority conflict resolution", "icon": "⚖️"},
            ]
        },
        # Strategy & Planning
        {
            "id": "vision-keeper",
            "name": "Strategy Lead",
            "description": "Vision & strategic planning",
            "icon": "🎯",
            "sub_agents": [
                {"id": "okr-coach", "name": "OKR Coach", "description": "OKR framework & goal setting", "icon": "🎯"},
                {"id": "kpi-definition", "name": "KPI Definition", "description": "Metric design & KPI frameworks", "icon": "📊"},
                {"id": "resource-allocation", "name": "Resource Allocation", "description": "Resource planning & distribution", "icon": "💰"},
                {"id": "scenario-planning", "name": "Scenario Planning", "description": "Future scenarios & contingencies", "icon": "🔮"},
                {"id": "competitive-strategy", "name": "Competitive Strategy", "description": "Competitive positioning & analysis", "icon": "⚔️"},
                {"id": "strategic-initiative", "name": "Strategic Initiative", "description": "Strategic program execution", "icon": "🚀"},
                {"id": "business-model", "name": "Business Model", "description": "Business model design & innovation", "icon": "💡"},
                {"id": "partnership-strategy", "name": "Partnership Strategy", "description": "Strategic alliances & partnerships", "icon": "🤝"},
                {"id": "investment-thesis", "name": "Investment Thesis", "description": "Investment strategy & capital allocation", "icon": "📈"},
            ]
        },
        # COO - Operations
        {
            "id": "coo-execution",
            "name": "COO",
            "description": "Chief Operating Officer - Execution & operations",
            "icon": "⚡",
            "sub_agents": [
                {
                    "id": "pmo-program",
                    "name": "PMO Director",
                    "description": "Program Management Office - Cross-functional coordination",
                    "icon": "📋",
                    "sub_agents": [
                        {"id": "scheduler", "name": "Scheduler", "description": "Task scheduling & resource allocation", "icon": "📅"},
                        {"id": "admin-coordinator", "name": "Admin Coordinator", "description": "Administrative support & coordination", "icon": "📋"},
                        {"id": "program-management", "name": "Program Management", "description": "Multi-project coordination", "icon": "🗂️"},
                    ]
                },
                {
                    "id": "business-operations",
                    "name": "Business Operations",
                    "description": "Process optimization & coordination",
                    "icon": "📊",
                    "sub_agents": [
                        {"id": "vendor-management", "name": "Vendor Management", "description": "Vendor relationships & contracts", "icon": "🏢"},
                        {"id": "procurement", "name": "Procurement", "description": "Purchasing & vendor selection", "icon": "🛒"},
                        {"id": "internal-tooling", "name": "Internal Tooling", "description": "Internal tools & automation", "icon": "🛠️"},
                        {"id": "change-management", "name": "Change Management", "description": "Organizational change planning", "icon": "🔄"},
                        {"id": "communication", "name": "Internal Communications", "description": "Company announcements & messaging", "icon": "📢"},
                    ]
                },
                {
                    "id": "quality-audit",
                    "name": "Quality & Audit",
                    "description": "Quality assurance & internal audits",
                    "icon": "✅",
                    "sub_agents": [
                        {"id": "policy-guardrails", "name": "Policy & Guardrails", "description": "Policy enforcement & safety guardrails", "icon": "🛡️"},
                        {"id": "observability", "name": "Observability", "description": "System observability & telemetry", "icon": "👁️"},
                        {"id": "quality-governance", "name": "Quality Governance", "description": "Quality standards & governance", "icon": "✅"},
                        {"id": "policy-enforcement", "name": "Policy Enforcement", "description": "Policy compliance verification", "icon": "📜"},
                    ]
                },
                {
                    "id": "okr-tracker",
                    "name": "Company OS",
                    "description": "Company operating system & metrics",
                    "icon": "⚙️",
                    "sub_agents": [
                        {"id": "wbr", "name": "Weekly Business Review", "description": "WBR preparation & analysis", "icon": "📊"},
                        {"id": "metric-pack", "name": "Metric Pack Builder", "description": "Metric packages & dashboards", "icon": "📈"},
                        {"id": "anomaly-explanation", "name": "Anomaly Explanation", "description": "Metric anomaly investigation", "icon": "🔍"},
                        {"id": "incident-commander", "name": "Incident Commander", "description": "Incident response leadership", "icon": "🚨"},
                        {"id": "postmortem", "name": "Postmortem", "description": "Incident analysis & lessons learned", "icon": "📝"},
                        {"id": "runbook", "name": "Runbook", "description": "Operational procedures & playbooks", "icon": "📖"},
                    ]
                },
                {
                    "id": "wiki-curator",
                    "name": "Knowledge Management",
                    "description": "Internal knowledge & documentation",
                    "icon": "📚",
                    "sub_agents": [
                        {"id": "faq-maintainer", "name": "FAQ Maintainer", "description": "FAQ management & curation", "icon": "❓"},
                        {"id": "search-enhancer", "name": "Search Enhancer", "description": "Internal search optimization", "icon": "🔍"},
                        {"id": "glossary-taxonomy", "name": "Glossary & Taxonomy", "description": "Terminology & classification", "icon": "📖"},
                    ]
                },
            ]
        },
        # CTO - Technology
        {
            "id": "cto",
            "name": "CTO",
            "description": "Chief Technology Officer - Technology strategy & engineering",
            "icon": "💻",
            "sub_agents": [
                {
                    "id": "senior-developer",
                    "name": "Tech Lead",
                    "description": "Architecture & technical leadership",
                    "icon": "👨‍💻",
                    "sub_agents": [
                        {"id": "frontend-developer", "name": "Frontend Developer", "description": "React/Vue UI implementation & performance", "icon": "🖥️"},
                        {"id": "backend-developer", "name": "Backend Developer", "description": "APIs, services & server-side logic", "icon": "🔧"},
                        {"id": "mobile-developer", "name": "Mobile Developer", "description": "iOS/Android app development", "icon": "📱"},
                        {"id": "database", "name": "Database Specialist", "description": "Schema design, queries & optimization", "icon": "🗄️"},
                    ]
                },
                {
                    "id": "qa-testing",
                    "name": "QA Manager",
                    "description": "Testing strategy & automation",
                    "icon": "✅",
                    "sub_agents": [
                        {"id": "bug-triage", "name": "Bug Triage", "description": "Bug prioritization & assignment", "icon": "🐛"},
                        {"id": "code-review", "name": "Code Reviewer", "description": "Code quality & best practices", "icon": "🔍"},
                    ]
                },
                {
                    "id": "devops",
                    "name": "DevOps Manager",
                    "description": "Infrastructure & deployment automation",
                    "icon": "🚀",
                    "sub_agents": [
                        {"id": "sre", "name": "SRE", "description": "Site reliability & system stability", "icon": "🔧"},
                        {"id": "monitoring", "name": "Monitoring Engineer", "description": "Alerting, dashboards & observability", "icon": "📊"},
                        {"id": "build-ci", "name": "Build/CI Engineer", "description": "CI/CD pipelines & build automation", "icon": "🔨"},
                        {"id": "release", "name": "Release Manager", "description": "Release coordination & deployment", "icon": "🚀"},
                        {"id": "cost-optimization", "name": "Cost Optimizer", "description": "Cloud cost management & optimization", "icon": "💰"},
                    ]
                },
                {
                    "id": "security",
                    "name": "Security Lead",
                    "description": "Application & infrastructure security",
                    "icon": "🔐",
                    "sub_agents": [
                        {"id": "access-control", "name": "Access Control", "description": "IAM, permissions & access reviews", "icon": "🔑"},
                        {"id": "vulnerability-management", "name": "Vulnerability Management", "description": "Scanning, patching & remediation", "icon": "🛡️"},
                        {"id": "incident-response", "name": "Incident Response", "description": "Security incidents & response", "icon": "🚨"},
                        {"id": "secure-sdlc", "name": "Secure SDLC", "description": "Security in development lifecycle", "icon": "🔒"},
                    ]
                },
                {"id": "it-support", "name": "IT Support", "description": "Internal IT helpdesk & support", "icon": "🖥️"},
                {"id": "asset-license", "name": "Asset/License Manager", "description": "Software licenses & asset tracking", "icon": "📋"},
            ]
        },
        # CPO - Product
        {
            "id": "cpo",
            "name": "CPO",
            "description": "Chief Product Officer - Product vision & strategy",
            "icon": "🎯",
            "sub_agents": [
                {
                    "id": "product-manager",
                    "name": "Product Manager",
                    "description": "Product roadmap & feature prioritization",
                    "icon": "📋",
                    "sub_agents": [
                        {"id": "product-strategy", "name": "Product Strategist", "description": "Product vision & market strategy", "icon": "🎯"},
                        {"id": "product-discovery", "name": "Product Discovery", "description": "Opportunity identification & validation", "icon": "🔍"},
                        {"id": "prd-spec", "name": "PRD/Spec Writer", "description": "Product requirements & specifications", "icon": "📝"},
                        {"id": "roadmap-priority", "name": "Roadmap Priority", "description": "Feature prioritization & sequencing", "icon": "🗺️"},
                        {"id": "feature-spec", "name": "Feature Spec Writer", "description": "Detailed feature specifications", "icon": "📄"},
                        {"id": "user-story", "name": "User Story Mapper", "description": "User stories & journey mapping", "icon": "👤"},
                        {"id": "competitor-tracker", "name": "Competitor Tracker", "description": "Competitive feature monitoring", "icon": "👁️"},
                    ]
                },
                {
                    "id": "ux-designer",
                    "name": "Design Lead",
                    "description": "User experience design & research",
                    "icon": "🎨",
                    "sub_agents": [
                        {"id": "user-research", "name": "User Researcher", "description": "User interviews & behavioral research", "icon": "🔬"},
                        {"id": "ui-visual-design", "name": "UI/Visual Designer", "description": "Visual design & design systems", "icon": "🖌️"},
                        {"id": "content-design", "name": "Content Designer", "description": "UX writing & content strategy", "icon": "✍️"},
                        {"id": "accessibility", "name": "Accessibility Specialist", "description": "WCAG compliance & inclusive design", "icon": "♿"},
                        {"id": "usability-testing", "name": "Usability Tester", "description": "Usability studies & user testing", "icon": "🧪"},
                    ]
                },
                {
                    "id": "experimentation",
                    "name": "Experimentation Lead",
                    "description": "A/B testing & experiment orchestration",
                    "icon": "🧪",
                    "sub_agents": [
                        {"id": "hypothesis-generator", "name": "Hypothesis Generator", "description": "Hypothesis formulation & testable predictions", "icon": "💡"},
                        {"id": "variant-generator", "name": "Variant Generator", "description": "A/B test variant creation", "icon": "🔀"},
                        {"id": "experiment-design", "name": "Experiment Design", "description": "Statistical experiment methodology", "icon": "📐"},
                        {"id": "traffic-allocation", "name": "Traffic Allocation", "description": "Experiment traffic management", "icon": "🚦"},
                        {"id": "results-interpretation", "name": "Results Interpretation", "description": "Experiment result analysis", "icon": "📊"},
                        {"id": "rollout-controller", "name": "Rollout Controller", "description": "Feature rollout management", "icon": "🎚️"},
                        {"id": "learning-synthesis", "name": "Learning Synthesis", "description": "Cross-experiment learnings", "icon": "🎓"},
                    ]
                },
                {
                    "id": "release-notes",
                    "name": "Product Operations",
                    "description": "Product operations & releases",
                    "icon": "📦",
                    "sub_agents": [
                        {"id": "beta-program", "name": "Beta Program Manager", "description": "Beta & early access programs", "icon": "🔬"},
                        {"id": "product-analytics", "name": "Product Analytics", "description": "Product metrics & usage analysis", "icon": "📈"},
                        {"id": "feature-flag", "name": "Feature Flag Manager", "description": "Feature flag lifecycle", "icon": "🏁"},
                        {"id": "localization", "name": "Localization Manager", "description": "Product localization & i18n", "icon": "🌍"},
                        {"id": "platform-api", "name": "Platform/API Product", "description": "API product & developer experience", "icon": "🔌"},
                    ]
                },
                {"id": "technical-writer", "name": "Technical Writer", "description": "Documentation & technical content", "icon": "📚"},
            ]
        },
        # CMO - Marketing
        {
            "id": "cmo",
            "name": "CMO",
            "description": "Chief Marketing Officer - Marketing & brand strategy",
            "icon": "📣",
            "sub_agents": [
                {
                    "id": "marketing-strategy",
                    "name": "Marketing Director",
                    "description": "Marketing strategy & campaigns",
                    "icon": "🎯",
                    "sub_agents": [
                        {"id": "market-research", "name": "Market Researcher", "description": "Competitive analysis & market insights", "icon": "🔍"},
                        {"id": "brand", "name": "Brand Manager", "description": "Brand identity & guidelines", "icon": "🏷️"},
                    ]
                },
                {
                    "id": "content-marketing",
                    "name": "Content Lead",
                    "description": "Blog posts & content creation",
                    "icon": "✍️",
                    "sub_agents": [
                        {"id": "seo", "name": "SEO Specialist", "description": "Search engine optimization", "icon": "🔍"},
                        {"id": "social-media", "name": "Social Media Manager", "description": "Social media strategy & engagement", "icon": "📱"},
                        {"id": "creative-production", "name": "Creative Producer", "description": "Creative assets & production", "icon": "🎬"},
                    ]
                },
                {
                    "id": "growth-analytics",
                    "name": "Growth Lead",
                    "description": "Growth metrics & funnel optimization",
                    "icon": "📈",
                    "sub_agents": [
                        {"id": "paid-acquisition", "name": "Paid Acquisition", "description": "PPC, ads & paid campaigns", "icon": "💵"},
                        {"id": "lifecycle-crm", "name": "Lifecycle/CRM", "description": "Email marketing & lifecycle campaigns", "icon": "📧"},
                    ]
                },
                {"id": "pr-comms", "name": "PR/Communications", "description": "Public relations & press", "icon": "📰"},
            ]
        },
        # CRO - Revenue/Sales
        {
            "id": "cro",
            "name": "CRO",
            "description": "Chief Revenue Officer - Sales & revenue growth",
            "icon": "💰",
            "sub_agents": [
                {
                    "id": "sales",
                    "name": "Sales Director",
                    "description": "Deal closing & revenue generation",
                    "icon": "💼",
                    "sub_agents": [
                        {"id": "prospecting", "name": "Prospecting", "description": "Outbound prospecting & outreach", "icon": "🎯"},
                        {"id": "sdr-qualification", "name": "SDR/Qualification", "description": "Lead qualification & discovery", "icon": "📞"},
                        {"id": "deal-desk", "name": "Deal Desk", "description": "Pricing, quotes & approvals", "icon": "📋"},
                    ]
                },
                {
                    "id": "sales-ops",
                    "name": "Sales Operations",
                    "description": "CRM, processes & sales tools",
                    "icon": "⚙️",
                    "sub_agents": [
                        {"id": "lead-enrichment", "name": "Lead Enrichment", "description": "Lead data enrichment & scoring", "icon": "📊"},
                        {"id": "sales-enablement", "name": "Sales Enablement", "description": "Training & sales collateral", "icon": "📚"},
                    ]
                },
                {"id": "partner-channel", "name": "Partner/Channel", "description": "Partner relationships & channel sales", "icon": "🤝"},
            ]
        },
        # CCO - Customer
        {
            "id": "cco",
            "name": "CCO",
            "description": "Chief Customer Officer - Customer success & satisfaction",
            "icon": "🤝",
            "sub_agents": [
                {
                    "id": "customer-success",
                    "name": "CS Director",
                    "description": "Account management & retention",
                    "icon": "👥",
                    "sub_agents": [
                        {"id": "onboarding", "name": "Onboarding Specialist", "description": "Customer onboarding & implementation", "icon": "🚀"},
                        {"id": "churn-prevention", "name": "Churn Prevention", "description": "At-risk identification & retention", "icon": "🛡️"},
                        {"id": "voice-of-customer", "name": "Voice of Customer", "description": "Customer feedback & NPS", "icon": "🎤"},
                    ]
                },
                {
                    "id": "support-triage",
                    "name": "Support Manager",
                    "description": "Ticket routing & prioritization",
                    "icon": "📥",
                    "sub_agents": [
                        {"id": "support-resolution", "name": "Support Resolution", "description": "Issue resolution & troubleshooting", "icon": "🔧"},
                        {"id": "knowledge-base", "name": "Knowledge Base", "description": "Help articles & documentation", "icon": "📖"},
                    ]
                },
                {"id": "community", "name": "Community Manager", "description": "Community engagement & forums", "icon": "💬"},
            ]
        },
        # CDO - Data
        {
            "id": "cdo",
            "name": "CDO",
            "description": "Chief Data Officer - Data strategy & analytics",
            "icon": "📊",
            "sub_agents": [
                {
                    "id": "data-analyst",
                    "name": "Analytics Manager",
                    "description": "Data analysis & insights",
                    "icon": "📈",
                    "sub_agents": [
                        {"id": "bi-reporting", "name": "BI/Reporting", "description": "Business intelligence & dashboards", "icon": "📊"},
                        {"id": "experiment-analysis", "name": "Experiment Analyst", "description": "A/B test analysis & statistics", "icon": "🧮"},
                        {"id": "forecasting", "name": "Forecasting Analyst", "description": "Predictive analytics & forecasting", "icon": "🔮"},
                    ]
                },
                {
                    "id": "data-engineering",
                    "name": "Data Engineering Lead",
                    "description": "Data pipelines & ETL",
                    "icon": "🔀",
                    "sub_agents": [
                        {"id": "data-quality", "name": "Data Quality", "description": "Data validation & quality assurance", "icon": "✅"},
                        {"id": "privacy-pii", "name": "Privacy/PII Specialist", "description": "Data privacy & PII handling", "icon": "🔒"},
                    ]
                },
                {"id": "ml-engineer", "name": "ML Engineer", "description": "Machine learning & model development", "icon": "🤖"},
            ]
        },
        # CFO - Finance
        {
            "id": "cfo",
            "name": "CFO",
            "description": "Chief Financial Officer - Finance & accounting",
            "icon": "💵",
            "sub_agents": [
                {
                    "id": "finance",
                    "name": "Finance Director",
                    "description": "FP&A, budgeting & financial planning",
                    "icon": "💰",
                    "sub_agents": [
                        {"id": "bookkeeping", "name": "Bookkeeper", "description": "Transaction recording & reconciliation", "icon": "📒"},
                        {"id": "invoicing-ar", "name": "Invoicing/AR", "description": "Invoices & accounts receivable", "icon": "📄"},
                        {"id": "accounts-payable", "name": "Accounts Payable", "description": "Bill payments & AP management", "icon": "💳"},
                        {"id": "revenue-ops", "name": "Revenue Operations", "description": "Revenue recognition & metrics", "icon": "📈"},
                    ]
                },
                {"id": "tax", "name": "Tax Specialist", "description": "Tax compliance & planning", "icon": "🧾"},
                {"id": "fraud-detection", "name": "Fraud Detection", "description": "Fraud prevention & anomaly detection", "icon": "🚨"},
            ]
        },
        # CLO - Legal
        {
            "id": "clo",
            "name": "CLO",
            "description": "Chief Legal Officer - Legal & compliance",
            "icon": "⚖️",
            "sub_agents": [
                {
                    "id": "legal-compliance",
                    "name": "General Counsel",
                    "description": "Contracts & regulatory compliance",
                    "icon": "⚖️",
                    "sub_agents": [
                        {"id": "contract", "name": "Contract Specialist", "description": "Contract drafting & review", "icon": "📝"},
                        {"id": "policy", "name": "Policy Manager", "description": "Internal policies & procedures", "icon": "📋"},
                        {"id": "intellectual-property", "name": "IP Specialist", "description": "Patents, trademarks & IP protection", "icon": "💡"},
                    ]
                },
                {"id": "regulatory", "name": "Regulatory Affairs", "description": "Regulatory compliance & filings", "icon": "📜"},
                {"id": "risk", "name": "Risk Manager", "description": "Risk assessment & mitigation", "icon": "⚠️"},
            ]
        },
        # CHRO - People
        {
            "id": "chro",
            "name": "CHRO",
            "description": "Chief Human Resources Officer - People & culture",
            "icon": "👥",
            "sub_agents": [
                {
                    "id": "hr-people",
                    "name": "HR Director",
                    "description": "HR operations & employee engagement",
                    "icon": "👔",
                    "sub_agents": [
                        {"id": "recruiting", "name": "Recruiter", "description": "Talent sourcing & recruitment", "icon": "🔍"},
                        {"id": "interview-loop", "name": "Interview Coordinator", "description": "Interview scheduling & coordination", "icon": "📅"},
                        {"id": "performance", "name": "Performance Manager", "description": "Performance reviews & development", "icon": "📊"},
                    ]
                },
                {"id": "learning-development", "name": "L&D Specialist", "description": "Training & professional development", "icon": "📚"},
                {"id": "compensation-benefits", "name": "Comp & Benefits", "description": "Compensation, benefits & payroll", "icon": "💰"},
            ]
        },
    ]
}

# For backward compatibility - wrap in a single department
COMPANY_ORG_STRUCTURE = [
    {
        "name": "Company",
        "icon": "🏢",
        "agents": [COMPANY_ORG_TREE]
    }
]


def get_all_agents() -> list[AgentNode]:
    """Get a flat list of all agents across the org tree."""
    agents = []

    def collect_agents(agent: AgentNode):
        agents.append(agent)
        if "sub_agents" in agent and agent["sub_agents"]:
            for sub in agent["sub_agents"]:
                collect_agents(sub)

    collect_agents(COMPANY_ORG_TREE)
    return agents


def get_agent_by_id(agent_id: str) -> AgentNode | None:
    """Find an agent by their ID (searches nested structure)."""
    def search_agent(agent: AgentNode) -> AgentNode | None:
        if agent["id"] == agent_id:
            return agent
        if "sub_agents" in agent and agent["sub_agents"]:
            for sub in agent["sub_agents"]:
                found = search_agent(sub)
                if found:
                    return found
        return None

    return search_agent(COMPANY_ORG_TREE)


def get_department_for_agent(agent_id: str) -> str | None:
    """Get the department name for a given agent (always 'Company' in tree structure)."""
    if get_agent_by_id(agent_id):
        return "Company"
    return None
