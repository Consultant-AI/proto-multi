# Proto Planning & Multi-Agent Architecture

Comprehensive planning system and multi-agent framework for intelligent task execution.

## Overview

Proto now includes an advanced planning and multi-agent system that:
- **Analyzes task complexity** to determine appropriate planning depth
- **Generates structured planning documents** for complex tasks
- **Orchestrates specialist agents** with domain expertise
- **Enables hierarchical delegation** between agents
- **Maintains project context** across sessions

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Task                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │    CEO Agent          │  ◄── Main Orchestrator
           │  (Task Analyzer)      │
           └───────────┬───────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Complexity  │ │   Planning   │ │  Delegation  │
│   Analysis   │ │  Generation  │ │   Logic      │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │Marketing │  │Developer │  │ Designer │
   │Specialist│  │Specialist│  │Specialist│
   └──────────┘  └──────────┘  └──────────┘
```

## Components

### 1. Planning System

Located in `computer_use_demo/planning/`

#### Task Complexity Analyzer ([analyzer.py](computer_use_demo/computer_use_demo/planning/analyzer.py))

Analyzes tasks to determine:
- **Complexity level**: simple, medium, complex, or project
- **Required specialists**: Which domain experts are needed
- **Planning depth**: What planning documents to create
- **Estimated effort**: Number of steps required

**Example:**
```python
from computer_use_demo.planning import TaskComplexityAnalyzer

analyzer = TaskComplexityAnalyzer()
analysis = analyzer.analyze("create a company website with e-commerce")

# Result:
# - complexity: "project"
# - planning_required: True
# - estimated_steps: 30+
# - required_specialists: ["marketing", "development", "design"]
```

#### Planning Documents ([documents.py](computer_use_demo/computer_use_demo/planning/documents.py))

Seven document templates with LLM generation prompts:

1. **Project Overview** (00_PROJECT_OVERVIEW.md)
   - Purpose, scope, success criteria
   - High-level timeline
   - Dependencies and risks

2. **Requirements** (01_REQUIREMENTS.md)
   - User stories
   - Functional and non-functional requirements
   - Acceptance criteria

3. **Technical Specification** (02_TECHNICAL_SPEC.md)
   - System architecture
   - Technology stack
   - Data models and APIs
   - Security and performance considerations

4. **Roadmap** (03_ROADMAP.md)
   - Milestones and phases
   - Task breakdown with estimates
   - Dependencies and critical path

5. **Knowledge Base** (04_KNOWLEDGE_BASE.md)
   - Domain context
   - Best practices
   - Common patterns
   - Resources and examples

6. **Decisions** (05_DECISIONS.md)
   - Decision log template
   - Options considered
   - Rationale and implications

7. **Specialist Plans** (agents/{specialist}_plan.md)
   - Specialist-specific scope
   - Deliverables and tasks
   - Dependencies on other agents

#### Project Manager ([project_manager.py](computer_use_demo/computer_use_demo/planning/project_manager.py))

Manages planning folder structure:

```
.proto/planning/
└── {project-slug}/
    ├── .project_metadata.json
    ├── 00_PROJECT_OVERVIEW.md
    ├── 01_REQUIREMENTS.md
    ├── 02_TECHNICAL_SPEC.md
    ├── 03_ROADMAP.md
    ├── 04_KNOWLEDGE_BASE.md
    ├── 05_DECISIONS.md
    ├── agents/
    │   ├── marketing_plan.md
    │   ├── development_plan.md
    │   └── design_plan.md
    └── knowledge/
        └── {knowledge-items}.json
```

**Features:**
- Creates and manages project folders
- Checks for existing projects
- Saves/loads planning documents
- Manages knowledge base items

### 2. Multi-Agent System

Located in `computer_use_demo/agents/`

#### Base Agent ([base_agent.py](computer_use_demo/computer_use_demo/agents/base_agent.py))

Foundation for all agents with:
- **Tool execution**: Runs tools and processes results
- **API integration**: Calls Anthropic API
- **Message handling**: Manages conversation state
- **Logging**: Integrated with structured logging
- **Iteration control**: Max iterations with safeguards

#### CEO Agent ([ceo_agent.py](computer_use_demo/computer_use_demo/agents/ceo_agent.py))

Main orchestrator responsible for:
- **Task analysis**: Assess complexity and requirements
- **Planning**: Generate planning documents for complex tasks
- **Delegation**: Assign work to specialist agents
- **Coordination**: Manage handoffs between specialists
- **Synthesis**: Combine results into final deliverable

**Workflow:**
```python
from computer_use_demo.agents import CEOAgent

# Initialize with tools
ceo = CEOAgent(tools=[...])

# Execute with automatic planning
result = await ceo.execute_with_planning(
    task="Build a landing page for our product",
    context={"existing_project": "product-site"}
)
```

#### Specialist Agents

Three specialist agents included:

**Marketing Agent** ([marketing_agent.py](computer_use_demo/computer_use_demo/agents/specialists/marketing_agent.py))
- Marketing strategy
- Brand development
- Campaign planning
- SEO/SEM
- Content marketing

**Developer Agent** ([developer_agent.py](computer_use_demo/computer_use_demo/agents/specialists/developer_agent.py))
- Software engineering
- System architecture
- Full-stack development
- Testing and optimization
- Technical documentation

**Design Agent** ([design_agent.py](computer_use_demo/computer_use_demo/agents/specialists/design_agent.py))
- UI/UX design
- Visual design
- Interaction design
- Design systems
- Accessibility

**Adding New Specialists:**

```python
from computer_use_demo.agents.specialists import BaseSpecialist

class AnalyticsAgent(BaseSpecialist):
    def __init__(self, session_id=None, tools=None):
        super().__init__(
            role="analytics",
            name="Analytics Specialist",
            session_id=session_id,
            tools=tools
        )

    def get_domain_expertise(self) -> str:
        return """Data analysis, metrics tracking, A/B testing,
        business intelligence, data visualization..."""
```

### 3. Planning Tools

Located in `computer_use_demo/tools/planning/`

The system includes three powerful tools that enable the multi-agent workflow:

#### PlanningTool ([plan_tool.py](computer_use_demo/computer_use_demo/tools/planning/plan_tool.py))

Generates comprehensive planning documents using LLM:
- Analyzes task complexity automatically
- Creates appropriate planning documents based on complexity
- Generates content using Claude with domain-specific prompts
- Saves documents to `.proto/planning/{project}/` structure

**Usage:**
```python
# Agent uses the tool
result = await planning_tool(
    task="Build an e-commerce platform",
    project_name="ecommerce-platform",
    context={"existing_features": ["user auth", "product catalog"]}
)
# Creates: project_overview, requirements, technical_spec, roadmap, etc.
```

#### DelegateTaskTool ([delegate_tool.py](computer_use_demo/computer_use_demo/tools/planning/delegate_tool.py))

Enables CEO agent to delegate work to specialists:
- Instantiates appropriate specialist agent
- Passes planning context and tools to specialist
- Executes specialist's work with full context
- Returns formatted results to CEO

**Usage:**
```python
# CEO delegates to design specialist
result = await delegate_task(
    specialist="design",
    task="Create landing page mockups",
    project_name="ecommerce-platform",
    additional_context={"brand_colors": ["#FF5733", "#3498DB"]}
)
# Design agent receives task + planning docs + context
```

#### ReadPlanningTool ([read_plan_tool.py](computer_use_demo/computer_use_demo/tools/planning/read_plan_tool.py))

Reads planning documents and project context:
- Lists all available projects
- Reads specific planning documents
- Gets comprehensive project context
- Checks if planning exists

**Usage:**
```python
# List all projects
result = await read_planning(action="list_projects")

# Read specific document
result = await read_planning(
    action="read_document",
    project_name="ecommerce-platform",
    document_type="requirements"
)

# Get full project context
result = await read_planning(
    action="get_project_context",
    project_name="ecommerce-platform"
)
```

**Integration:**
All three tools are included in the `proto_coding_v1` tool group in [groups.py](computer_use_demo/computer_use_demo/tools/groups.py), making them available to agents alongside coding tools (Bash, Edit, Glob, Grep, Git, TodoWrite).

### 4. Logging Integration

Enhanced [structured_logger.py](computer_use_demo/computer_use_demo/logging/structured_logger.py) with new event types:

**Planning Events:**
- `planning_started`: Task complexity analysis begins
- `planning_completed`: Planning documents generated
- `complexity_analyzed`: Complexity assessment result
- `document_generated`: Planning document created
- `project_created`: New project folder created

**Multi-Agent Events:**
- `agent_delegated`: CEO delegates to specialist
- `agent_response`: Specialist returns results
- `agent_collaboration`: Specialists collaborate

**Example Log:**
```json
{
  "timestamp": "2025-11-18T14:30:00.000Z",
  "level": "INFO",
  "event_type": "planning_started",
  "session_id": "ceo-agent",
  "data": {
    "task": "Create landing page",
    "complexity": "complex",
    "planning_required": true,
    "required_specialists": ["design", "development"]
  }
}
```

## Usage Examples

### Example 1: Simple Task (No Planning)

```python
from computer_use_demo.agents import CEOAgent

ceo = CEOAgent(tools=[bash_tool, edit_tool])
result = await ceo.execute_with_planning("Fix the typo in README.md")

# Analysis: complexity="simple", no planning docs created
# Execution: Direct tool use to fix typo
```

### Example 2: Complex Task (With Planning)

```python
ceo = CEOAgent(tools=[...])
result = await ceo.execute_with_planning(
    "Build a user authentication system with email verification"
)

# Analysis: complexity="complex"
# Planning: Creates requirements, technical spec, roadmap
# Execution: Uses planning docs to guide implementation
```

### Example 3: Project-Level (Multi-Agent)

```python
ceo = CEOAgent(tools=[...])
result = await ceo.execute_with_planning(
    "Create a SaaS product with landing page, user dashboard, and payment integration"
)

# Analysis: complexity="project"
# Planning: Full planning suite generated
# Delegation:
#   - Design agent: Landing page and dashboard UI
#   - Developer agent: Backend and payment integration
#   - Marketing agent: Landing page copy and SEO
# Coordination: CEO manages handoffs
# Synthesis: CEO combines all deliverables
```

### Example 4: Existing Project Context

```python
from computer_use_demo.planning import ProjectManager

pm = ProjectManager()

# Check for existing project
if pm.project_exists("ecommerce-platform"):
    context = pm.get_project_context("ecommerce-platform")

    # Use existing planning docs
    result = await ceo.execute_with_planning(
        "Add product reviews feature",
        context=context
    )
```

## Implementation Status

### ✅ Completed

- [x] Task Complexity Analyzer
- [x] Planning Document Templates
- [x] Project Manager
- [x] Base Agent Class
- [x] CEO Agent
- [x] Base Specialist Agent
- [x] Marketing, Developer, Design Specialists
- [x] Logging Integration
- [x] **Planning Tool**: Tool for agents to generate planning docs
- [x] **Delegate Tool**: Tool for CEO to delegate to specialists
- [x] **Read Planning Tool**: Tool for reading planning documents
- [x] **LLM-based Planning**: LLM generates actual document content
- [x] **Tool Group Integration**: Planning tools added to proto_coding_v1

### 🚧 Future Enhancements

- [ ] **Agent Communication Protocol**: Enhanced message passing between agents
- [ ] **WebUI Integration**: UI for viewing agent hierarchy and delegation
- [ ] **Additional Specialists**: Analytics, Content, Research agents
- [ ] **Specialist Tool Customization**: Domain-specific tools per specialist
- [ ] **Planning Document Viewer**: UI for browsing planning docs
- [ ] **Agent Performance Metrics**: Track effectiveness of delegation
- [ ] **Workflow Testing**: Comprehensive end-to-end testing

## Configuration

### Environment Variables

```bash
# Planning system
PROTO_PLANNING_ROOT=/path/to/planning/folder  # Default: cwd/.proto/planning

# Agent configuration
PROTO_DEFAULT_MODEL=claude-sonnet-4-5-20250929
PROTO_MAX_ITERATIONS=25

# Logging (includes planning events)
PROTO_LOG_DIR=/path/to/logs  # Default: project_root/logs
PROTO_LOG_LEVEL=INFO
```

### Complexity Analysis Tuning

Customize keywords in [analyzer.py](computer_use_demo/computer_use_demo/planning/analyzer.py):

```python
# Add project-level indicators
PROJECT_KEYWORDS = [
    "create company",
    "build startup",
    # Add your keywords...
]

# Add specialist indicators
SPECIALIST_INDICATORS = {
    "your_domain": ["keyword1", "keyword2", ...],
}
```

## Best Practices

### For Simple Tasks
- Let the CEO agent execute directly
- Don't force planning on trivial tasks
- Use existing tools efficiently

### For Complex Tasks
- Trust the planning system
- Review generated planning docs
- Use docs to guide implementation
- Update docs as decisions are made

### For Projects
- Create comprehensive planning upfront
- Leverage specialist agents
- Document decisions in decision log
- Maintain knowledge base

### For Existing Projects
- Always check for existing planning
- Reuse planning context
- Update documents as project evolves
- Track changes in decision log

## Troubleshooting

### "Planning docs not being created"
- Check task complexity analysis
- Verify keywords trigger complex/project classification
- Check PROJECT_KEYWORDS in analyzer

### "Specialist not found"
- Ensure specialist is imported in specialists/__init__.py
- Check role name matches SpecialistDomain type
- Verify agent initialization

### "Planning folder permission denied"
- Check PROTO_PLANNING_ROOT permissions
- Ensure write access to .proto/planning/
- Try different location

## Next Steps

1. **Integrate with WebUI**: Add agent selection and planning doc viewer
2. **Implement Tools**: Create PlanningTool, DelegateTaskTool
3. **LLM Planning**: Generate actual planning docs with LLM
4. **Test Multi-Agent**: Build complete workflow example
5. **Add More Specialists**: Analytics, Content, Research agents

## Architecture Diagrams

### Planning Flow

```
User Task
    │
    ├─► Complexity Analyzer
    │       │
    │       ├─► Simple? ──► Execute Directly
    │       ├─► Medium? ──► Basic Planning ──► Execute
    │       ├─► Complex? ──► Full Planning ──► Execute
    │       └─► Project? ──► Full Planning + Delegation
    │
    └─► CEO Agent
            │
            ├─► Create Planning Docs (if needed)
            │
            ├─► Execute or Delegate
            │       │
            │       ├─► Marketing Specialist
            │       ├─► Developer Specialist
            │       └─► Design Specialist
            │
            └─► Synthesize Results
```

### Agent Hierarchy

```
                CEO Agent
                 (Orchestrator)
                      │
        ┌─────────────┼─────────────┐
        │             │             │
    Marketing     Developer      Designer
   Specialist     Specialist    Specialist
        │             │             │
        └─────────────┼─────────────┘
                      │
                 (Can delegate to
                  each other if
                    needed)
```

## Contributing

To add new specialists or planning document types:

1. Create specialist in `agents/specialists/`
2. Extend `SpecialistDomain` type
3. Add to `SPECIALIST_INDICATORS` in analyzer
4. Update `__init__.py` exports
5. Add tests and documentation

---

**Built with Claude Sonnet 4.5** for the Proto AI Agent System
