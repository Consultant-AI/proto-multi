"""
Company-wide organizational structure for all specialist agents.

This defines the complete hierarchy of agents available in the system,
organized by department and function with support for nested sub-agents.
"""

from typing import TypedDict, NotRequired


class AgentNode(TypedDict):
    """Represents a single agent in the organizational tree."""
    id: str  # Agent identifier (matches .md filename)
    name: str  # Display name
    description: str  # Brief description
    icon: str  # Icon/emoji for UI
    sub_agents: NotRequired[list['AgentNode']]  # Optional nested sub-agents


class DepartmentNode(TypedDict):
    """Represents a department with multiple agents."""
    name: str
    icon: str
    agents: list[AgentNode]


# Complete company organizational structure
COMPANY_ORG_STRUCTURE: list[DepartmentNode] = [
    {
        "name": "Company",
        "icon": "🏢",
        "agents": [
            {
                "id": "ceo",
                "name": "CEO",
                "description": "Chief Executive Officer",
                "icon": "👔",
                "sub_agents": [
                    {
                        "id": "engineering-manager",
                        "name": "Engineering Manager",
                        "description": "Head of Engineering",
                        "icon": "⚙️",
                        "sub_agents": [
                            {
                                "id": "senior-developer",
                                "name": "Senior Developer",
                                "description": "Full-stack development & architecture",
                                "icon": "👨‍💻",
                                "sub_agents": [
                                    {
                                        "id": "code-reviewer",
                                        "name": "Code Reviewer",
                                        "description": "Automated code review & best practices",
                                        "icon": "🔍"
                                    },
                                    {
                                        "id": "refactoring-specialist",
                                        "name": "Refactoring Specialist",
                                        "description": "Code refactoring & optimization",
                                        "icon": "♻️"
                                    },
                                    {
                                        "id": "test-writer",
                                        "name": "Test Writer",
                                        "description": "Unit & integration test generation",
                                        "icon": "🧪"
                                    },
                                    {
                                        "id": "utility-tools",
                                        "name": "Utility Tools",
                                        "description": "General purpose utilities & helpers",
                                        "icon": "🛠️",
                                        "sub_agents": [
                                            {
                                                "id": "calculator",
                                                "name": "Calculator",
                                                "description": "Math calculations & expressions",
                                                "icon": "🧮"
                                            },
                                            {
                                                "id": "text-processor",
                                                "name": "Text Processor",
                                                "description": "String manipulation & text analysis",
                                                "icon": "📝"
                                            },
                                            {
                                                "id": "date-time-helper",
                                                "name": "Date/Time Helper",
                                                "description": "Date parsing & time zone utilities",
                                                "icon": "⏰"
                                            },
                                            {
                                                "id": "regex-builder",
                                                "name": "Regex Builder",
                                                "description": "Regular expression generation & testing",
                                                "icon": "🔤"
                                            },
                                            {
                                                "id": "hash-generator",
                                                "name": "Hash Generator",
                                                "description": "MD5, SHA, UUID generation",
                                                "icon": "#️⃣"
                                            },
                                            {
                                                "id": "url-parser",
                                                "name": "URL Parser",
                                                "description": "URL parsing & query string handling",
                                                "icon": "🔗"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "id": "frontend-developer",
                                "name": "Frontend Developer",
                                "description": "React/Vue UI implementation",
                                "icon": "🎨",
                                "sub_agents": [
                                    {
                                        "id": "component-generator",
                                        "name": "Component Generator",
                                        "description": "React component scaffolding",
                                        "icon": "🧩"
                                    },
                                    {
                                        "id": "css-optimizer",
                                        "name": "CSS Optimizer",
                                        "description": "CSS/Tailwind optimization",
                                        "icon": "🎨"
                                    },
                                    {
                                        "id": "media-processor",
                                        "name": "Media Processor",
                                        "description": "Image & media utilities",
                                        "icon": "🖼️",
                                        "sub_agents": [
                                            {
                                                "id": "image-optimizer",
                                                "name": "Image Optimizer",
                                                "description": "Image compression & optimization",
                                                "icon": "🖼️"
                                            },
                                            {
                                                "id": "svg-generator",
                                                "name": "SVG Generator",
                                                "description": "SVG icon & graphic generation",
                                                "icon": "✏️"
                                            },
                                            {
                                                "id": "color-palette",
                                                "name": "Color Palette",
                                                "description": "Color scheme generation & conversion",
                                                "icon": "🎨"
                                            },
                                            {
                                                "id": "qr-code-generator",
                                                "name": "QR Code Generator",
                                                "description": "QR code creation utilities",
                                                "icon": "⬛"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "id": "backend-developer",
                                "name": "Backend Developer",
                                "description": "APIs & server-side logic",
                                "icon": "🔧",
                                "sub_agents": [
                                    {
                                        "id": "api-generator",
                                        "name": "API Generator",
                                        "description": "RESTful/GraphQL API scaffolding",
                                        "icon": "🔌"
                                    },
                                    {
                                        "id": "database-optimizer",
                                        "name": "Database Optimizer",
                                        "description": "Query optimization & schema design",
                                        "icon": "🗄️"
                                    },
                                    {
                                        "id": "migration-writer",
                                        "name": "Migration Writer",
                                        "description": "Database migration generation",
                                        "icon": "🔄"
                                    },
                                    {
                                        "id": "data-processor",
                                        "name": "Data Processor",
                                        "description": "Data transformation & ETL pipelines",
                                        "icon": "⚙️",
                                        "sub_agents": [
                                            {
                                                "id": "json-parser",
                                                "name": "JSON Parser",
                                                "description": "JSON parsing & transformation",
                                                "icon": "📄"
                                            },
                                            {
                                                "id": "csv-processor",
                                                "name": "CSV Processor",
                                                "description": "CSV parsing & manipulation",
                                                "icon": "📊"
                                            },
                                            {
                                                "id": "xml-handler",
                                                "name": "XML Handler",
                                                "description": "XML parsing & generation",
                                                "icon": "📝"
                                            },
                                            {
                                                "id": "file-converter",
                                                "name": "File Converter",
                                                "description": "Format conversion utilities",
                                                "icon": "🔄"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "id": "mobile-developer",
                                "name": "Mobile Developer",
                                "description": "iOS/Android app development",
                                "icon": "📱"
                            },
                            {
                                "id": "devops",
                                "name": "DevOps Engineer",
                                "description": "Infrastructure & deployment",
                                "icon": "🚀",
                                "sub_agents": [
                                    {
                                        "id": "dockerfile-generator",
                                        "name": "Dockerfile Generator",
                                        "description": "Docker & containerization setup",
                                        "icon": "🐳"
                                    },
                                    {
                                        "id": "ci-pipeline-builder",
                                        "name": "CI Pipeline Builder",
                                        "description": "GitHub Actions/Jenkins pipelines",
                                        "icon": "⚙️"
                                    },
                                    {
                                        "id": "terraform-writer",
                                        "name": "Terraform Writer",
                                        "description": "Infrastructure as Code generation",
                                        "icon": "🏗️"
                                    }
                                ]
                            },
                            {
                                "id": "qa-testing",
                                "name": "QA Engineer",
                                "description": "Quality assurance & testing",
                                "icon": "✅",
                                "sub_agents": [
                                    {
                                        "id": "e2e-test-writer",
                                        "name": "E2E Test Writer",
                                        "description": "Playwright/Cypress test generation",
                                        "icon": "🎭"
                                    },
                                    {
                                        "id": "bug-analyzer",
                                        "name": "Bug Analyzer",
                                        "description": "Bug reproduction & root cause analysis",
                                        "icon": "🐛"
                                    }
                                ]
                            },
                            {
                                "id": "security",
                                "name": "Security Engineer",
                                "description": "Application & infrastructure security",
                                "icon": "🔒",
                                "sub_agents": [
                                    {
                                        "id": "vulnerability-scanner",
                                        "name": "Vulnerability Scanner",
                                        "description": "Automated security scanning",
                                        "icon": "🛡️"
                                    },
                                    {
                                        "id": "encryption-helper",
                                        "name": "Encryption Helper",
                                        "description": "Encryption/decryption utilities",
                                        "icon": "🔐"
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        "id": "product-manager",
                        "name": "Product Manager",
                        "description": "Head of Product",
                        "icon": "📋",
                        "sub_agents": [
                            {
                                "id": "product-strategy",
                                "name": "Product Strategist",
                                "description": "Product vision & market strategy",
                                "icon": "🎯"
                            },
                            {
                                "id": "ux-designer",
                                "name": "UX Designer",
                                "description": "UI/UX design & user research",
                                "icon": "🎨"
                            },
                            {
                                "id": "user-research",
                                "name": "User Researcher",
                                "description": "User interviews & feedback analysis",
                                "icon": "🔍"
                            },
                        ]
                    },
                    {
                        "id": "marketing-director",
                        "name": "Marketing Director",
                        "description": "Head of Marketing",
                        "icon": "📣",
                        "sub_agents": [
                            {
                                "id": "content-marketing",
                                "name": "Content Marketer",
                                "description": "Blog posts & content creation",
                                "icon": "✍️"
                            },
                            {
                                "id": "social-media-marketing",
                                "name": "Social Media Manager",
                                "description": "Social media strategy & engagement",
                                "icon": "📱"
                            },
                            {
                                "id": "email-marketing",
                                "name": "Email Marketing Specialist",
                                "description": "Email campaigns & automation",
                                "icon": "✉️"
                            },
                            {
                                "id": "seo-specialist",
                                "name": "SEO Specialist",
                                "description": "Search engine optimization",
                                "icon": "🔍"
                            },
                        ]
                    },
                    {
                        "id": "sales-director",
                        "name": "Sales Director",
                        "description": "Head of Sales",
                        "icon": "💰",
                        "sub_agents": [
                            {
                                "id": "account-executive",
                                "name": "Account Executive",
                                "description": "Deal closing & revenue generation",
                                "icon": "💼"
                            },
                            {
                                "id": "sales-development",
                                "name": "Sales Development Rep",
                                "description": "Lead generation & qualification",
                                "icon": "📞"
                            },
                        ]
                    },
                    {
                        "id": "customer-success-manager",
                        "name": "Customer Success Manager",
                        "description": "Head of Customer Success",
                        "icon": "🤝",
                        "sub_agents": [
                            {
                                "id": "customer-success",
                                "name": "Customer Success Specialist",
                                "description": "Account management & retention",
                                "icon": "👥"
                            },
                            {
                                "id": "customer-support",
                                "name": "Customer Support Agent",
                                "description": "Support tickets & issue resolution",
                                "icon": "💬"
                            },
                        ]
                    },
                    {
                        "id": "data-analytics-manager",
                        "name": "Data & Analytics Manager",
                        "description": "Head of Data & Analytics",
                        "icon": "📊",
                        "sub_agents": [
                            {
                                "id": "data-analyst",
                                "name": "Data Analyst",
                                "description": "Data analysis & insights",
                                "icon": "📈",
                                "sub_agents": [
                                    {
                                        "id": "chart-generator",
                                        "name": "Chart Generator",
                                        "description": "Generate charts with matplotlib/plotly",
                                        "icon": "📊"
                                    },
                                    {
                                        "id": "graph-maker",
                                        "name": "Graph Maker",
                                        "description": "Network graphs & data visualizations",
                                        "icon": "🕸️"
                                    },
                                    {
                                        "id": "statistics-calculator",
                                        "name": "Statistics Calculator",
                                        "description": "Statistical analysis & calculations",
                                        "icon": "📐"
                                    },
                                    {
                                        "id": "data-visualizer",
                                        "name": "Data Visualizer",
                                        "description": "Interactive dashboards & reports",
                                        "icon": "📈"
                                    }
                                ]
                            },
                            {
                                "id": "growth-analytics",
                                "name": "Growth Analyst",
                                "description": "Growth experiments & metrics",
                                "icon": "📉"
                            },
                        ]
                    },
                    {
                        "id": "technical-writer",
                        "name": "Technical Writer",
                        "description": "Documentation & technical content",
                        "icon": "📚",
                        "sub_agents": [
                            {
                                "id": "documentation-generator",
                                "name": "Documentation Generator",
                                "description": "Auto-generate code documentation",
                                "icon": "📄"
                            },
                            {
                                "id": "markdown-formatter",
                                "name": "Markdown Formatter",
                                "description": "Markdown formatting & conversion",
                                "icon": "✍️"
                            },
                            {
                                "id": "diagram-generator",
                                "name": "Diagram Generator",
                                "description": "Mermaid, PlantUML diagram generation",
                                "icon": "📊",
                                "sub_agents": [
                                    {
                                        "id": "flowchart-maker",
                                        "name": "Flowchart Maker",
                                        "description": "Flowchart & process diagrams",
                                        "icon": "🔀"
                                    },
                                    {
                                        "id": "sequence-diagram",
                                        "name": "Sequence Diagram",
                                        "description": "Sequence & interaction diagrams",
                                        "icon": "↔️"
                                    },
                                    {
                                        "id": "er-diagram",
                                        "name": "ER Diagram",
                                        "description": "Entity-relationship diagrams",
                                        "icon": "🗂️"
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": "coo",
                        "name": "Chief Operating Officer",
                        "description": "Head of Operations",
                        "icon": "⚡",
                        "sub_agents": [
                            {
                                "id": "finance",
                                "name": "Finance Manager",
                                "description": "Budgeting & financial planning",
                                "icon": "💵"
                            },
                            {
                                "id": "legal-compliance",
                                "name": "Legal & Compliance",
                                "description": "Contracts & regulatory compliance",
                                "icon": "⚖️"
                            },
                            {
                                "id": "hr-people",
                                "name": "HR Manager",
                                "description": "Recruitment & employee engagement",
                                "icon": "👔"
                            },
                            {
                                "id": "business-operations",
                                "name": "Business Operations",
                                "description": "Process optimization & coordination",
                                "icon": "📊"
                            },
                        ]
                    },
                ]
            },
        ]
    },
]


def get_all_agents() -> list[AgentNode]:
    """Get a flat list of all agents across all departments."""
    agents = []
    for dept in COMPANY_ORG_STRUCTURE:
        agents.extend(dept["agents"])
    return agents


def get_agent_by_id(agent_id: str) -> AgentNode | None:
    """Find an agent by their ID."""
    for dept in COMPANY_ORG_STRUCTURE:
        for agent in dept["agents"]:
            if agent["id"] == agent_id:
                return agent
    return None


def get_department_for_agent(agent_id: str) -> str | None:
    """Get the department name for a given agent."""
    for dept in COMPANY_ORG_STRUCTURE:
        for agent in dept["agents"]:
            if agent["id"] == agent_id:
                return dept["name"]
    return None
