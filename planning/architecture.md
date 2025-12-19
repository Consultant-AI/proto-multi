# Proto Multi-Agent System - Product Requirements Document

## Goal
Make it run a business while it improves itself in the process


---

# Complete System Architecture

## 6-Layer Enterprise Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    PROTO MULTI-AGENT SYSTEM                          │
│              Enterprise-Grade Autonomous Business Platform            │
└──────────────────────────────────────────────────────────────────────┘

1. PRESENTATION LAYER
   ├── Web UI (FastAPI) - http://localhost:8000
   │   ├── Dark-themed interface
   │   ├── Real-time message streaming
   │   ├── File uploads & management
   │   └── Session persistence
   ├── CLI Interface
   └── REST API Endpoints

2. ORCHESTRATION LAYER
   ├── CEO Agent - Main orchestrator & delegation
   ├── Company Orchestrator - Continuous operation daemon
   │   ├── Event loop for autonomous business
   │   ├── Health monitoring
   │   └── Graceful shutdown handling
   └── Work Queue System
       ├── Priority-based (LOW/MEDIUM/HIGH/CRITICAL)
       ├── Retry mechanism (configurable max retries)
       └── State persistence for recovery

3. AGENT LAYER (20+ Specialist Agents)
   ├── Engineering (Dev, DevOps, QA, Security)
   ├── Product (PM, UX, Strategy)
   ├── Business (Marketing, Sales, CS, Finance, Legal)
   └── Operations (HR, BizOps, Admin, Data, Content)

4. PLANNING & STATE MANAGEMENT
   ├── Project Manager
   │   ├── Folder structure management
   │   ├── Document generation (overview, requirements, specs, roadmap)
   │   └── Integration with TaskManager & KnowledgeStore
   ├── Task Manager
   │   ├── Hierarchical tasks with dependencies
   │   ├── Status tracking (PENDING/IN_PROGRESS/COMPLETED/BLOCKED/CANCELLED)
   │   ├── Priority levels (LOW/MEDIUM/HIGH/CRITICAL)
   │   └── Parent-child relationships
   ├── Knowledge Store
   │   ├── Persistent learning across sessions
   │   ├── Types: technical_decision, learning, pattern, reference, context, best_practice, lesson_learned
   │   ├── Search & relevance scoring
   │   └── Task/entry linking
   └── Complexity Analyzer
       ├── Determines if planning docs needed
       └── Complexity levels: simple/medium/complex/very_complex

5. TOOL LAYER (16 Tools)
   ├── Core: Computer, LocalComputer, Bash, Edit
   ├── Coding: Glob, Grep, Git, Todo, PythonExec
   └── Planning: Planning, ReadPlanning, Delegate, Task, Knowledge, Project, WorkQueue

6. INFRASTRUCTURE
   ├── Logging System
   │   ├── 4 separate streams (sessions, errors, tools, system)
   │   ├── JSONL format for machine readability
   │   └── Unified log viewer for chronological debugging
   ├── Training System
   │   ├── Test suites for agent validation
   │   └── Training data storage
   ├── Verification System
   │   ├── Screenshot analysis
   │   └── Feedback loops for iterative improvement
   └── Persistence
       └── .proto/ folder structure for all state
```

---

## Agent Hierarchy

```
User Input
    ↓
CEO Agent (Entry Point)
    ↓
├── Analyzes request complexity
├── Plans execution strategy
└── Delegates to specialist agents
    ↓
    ├─→ Engineering Manager
    │   ├─→ Senior Developer
    │   │   ├─→ Code Reviewer
    │   │   ├─→ Refactoring Specialist
    │   │   ├─→ Test Writer
    │   │   └─→ Utility Tools
    │   │       ├─→ Calculator
    │   │       ├─→ Text Processor
    │   │       ├─→ Date/Time Helper
    │   │       ├─→ Regex Builder
    │   │       ├─→ Hash Generator
    │   │       └─→ URL Parser
    │   ├─→ Frontend Developer
    │   │   ├─→ Component Generator
    │   │   ├─→ CSS Optimizer
    │   │   └─→ Media Processor
    │   │       ├─→ Image Optimizer
    │   │       ├─→ SVG Generator
    │   │       ├─→ Color Palette
    │   │       └─→ QR Code Generator
    │   ├─→ Backend Developer
    │   │   ├─→ API Generator
    │   │   ├─→ Database Optimizer
    │   │   ├─→ Migration Writer
    │   │   └─→ Data Processor
    │   │       ├─→ JSON Parser
    │   │       ├─→ CSV Processor
    │   │       ├─→ XML Handler
    │   │       └─→ File Converter
    │   ├─→ Mobile Developer
    │   ├─→ DevOps Engineer
    │   │   ├─→ Dockerfile Generator
    │   │   ├─→ CI Pipeline Builder
    │   │   └─→ Terraform Writer
    │   ├─→ QA Engineer
    │   │   ├─→ E2E Test Writer
    │   │   └─→ Bug Analyzer
    │   └─→ Security Engineer
    │       ├─→ Vulnerability Scanner
    │       └─→ Encryption Helper
    │
    ├─→ Product Manager
    │   ├─→ Product Strategist
    │   ├─→ UX Designer
    │   └─→ User Researcher
    │
    ├─→ Marketing Director
    │   ├─→ Content Marketer
    │   ├─→ Social Media Manager
    │   ├─→ Email Marketing Specialist
    │   └─→ SEO Specialist
    │
    ├─→ Sales Director
    │   ├─→ Account Executive
    │   └─→ Sales Development Rep
    │
    ├─→ Customer Success Manager
    │   ├─→ Customer Success Specialist
    │   └─→ Customer Support Agent
    │
    ├─→ Data & Analytics Manager
    │   ├─→ Data Analyst
    │   │   ├─→ Chart Generator
    │   │   ├─→ Graph Maker
    │   │   ├─→ Statistics Calculator
    │   │   └─→ Data Visualizer
    │   └─→ Growth Analyst
    │
    ├─→ Technical Writer
    │   ├─→ Documentation Generator
    │   ├─→ Markdown Formatter
    │   └─→ Diagram Generator
    │       ├─→ Flowchart Maker
    │       ├─→ Sequence Diagram
    │       └─→ ER Diagram
    │
    └─→ COO
        ├─→ Finance Manager
        ├─→ Legal & Compliance
        ├─→ HR Manager
        └─→ Business Operations

Each agent has access to:
    ├─→ All 16 Tools (See complete list below)
    ├─→ Knowledge Store (Project context, persistent learnings)
    ├─→ Task Management (Planning, tracking, dependencies)
    ├─→ Project Management (Structure, documents, metadata)
    └─→ Ability to call ANY other agent (not limited by hierarchy)
```

---

## Agent Delegation Model

### Why Delegation to Specialists is Critical

**CEO Agent Role:**
- Orchestrates work, analyzes complexity, creates planning
- **Should NOT do specialized work directly**
- **Should ALWAYS delegate to specialists** for execution

**Specialist Sub-Agent Excellence:**
Each specialist is highly optimized for their domain:

**Engineering Specialists:**
- **Senior Developer**: Expert at complex implementation, architecture decisions
- **Frontend Developer**: Masters React, TypeScript, UI/UX implementation
- **Backend Developer**: Database design, APIs, authentication, scalability
- **DevOps Engineer**: Docker, CI/CD, deployment, infrastructure
- **QA Engineer**: Testing strategies, E2E tests, bug analysis
- **Security Engineer**: Vulnerability assessment, encryption, security audits

**Product & Design Specialists:**
- **Product Manager**: Requirements, roadmaps, feature prioritization
- **UX Designer**: User experience, interface design, usability
- **User Researcher**: User needs analysis, testing, feedback

**Business Specialists:**
- **Marketing Director**: Strategy, campaigns, content planning
- **Sales Director**: Pipeline management, outreach, conversions
- **Customer Success Manager**: Support, retention, satisfaction

### Delegation Best Practices

**✅ ALWAYS Delegate When:**
1. Task requires specialized domain knowledge
2. Implementation involves specific technologies
3. Quality depends on expert judgment
4. Specialist has dedicated tools/workflows

**❌ NEVER Skip Delegation:**
- CEO writing frontend code directly ❌
- CEO designing database schemas ❌
- CEO implementing security features ❌
- Any agent doing work outside their expertise ❌

### Delegation Flow

```
User: "Build a web app with authentication"
    ↓
CEO Agent:
  1. Analyzes: "Complex project requiring planning"
  2. Creates planning docs in .proto/planning/
  3. Breaks down into specialist tasks:
     ├─ "Design authentication system" → Backend Developer
     ├─ "Create login UI" → Frontend Developer
     ├─ "Set up deployment" → DevOps Engineer
     └─ "Write security tests" → QA Engineer
    ↓
Backend Developer (Specialist):
  ✅ Reads project context from .proto/planning/
  ✅ Understands requirements, technical spec
  ✅ Implements authentication (JWT, sessions, etc.)
  ✅ Uses tools: Edit, Bash, PythonExec, Git
  ✅ Updates knowledge base with decisions
  ✅ Returns result to CEO
    ↓
Frontend Developer (Specialist):
  ✅ Reads Backend Developer's work
  ✅ Implements login forms, state management
  ✅ Integrates with backend API
  ✅ Returns result to CEO
    ↓
CEO Agent:
  ✅ Coordinates handoffs between specialists
  ✅ Ensures consistency across work
  ✅ Updates project status
  ✅ Reports completion to user
```

### Sub-Agent Specialization Advantages

**1. Deep Domain Expertise**
- Specialists have domain-specific prompts and context
- Know best practices for their field
- Make better technical decisions

**2. Better Tool Usage**
- Each specialist knows optimal tool combinations
- Senior Developer: GlobTool → GrepTool → EditTool → GitTool
- DevOps Engineer: BashTool → Docker commands → Git commits
- Frontend Developer: EditTool → PythonExec (npm) → Browser testing

**3. Quality & Efficiency**
- Specialists work faster in their domain
- Fewer iterations needed
- Higher quality output

**4. Knowledge Accumulation**
- Each specialist builds domain-specific knowledge
- Patterns recognized and reused
- Continuous improvement in specialty

**5. Parallel Execution**
- Multiple specialists can work simultaneously
- Frontend + Backend + DevOps in parallel
- Reduces total project time

### When Any Agent Can Delegate

**Not Just CEO:**
Any agent can delegate when they need specialist help:

```
Senior Developer working on API:
  "I need a database schema designed"
  → Delegates to Backend Developer (database specialist)

Frontend Developer needs deployment:
  "This needs to be deployed to production"
  → Delegates to DevOps Engineer

Product Manager needs market research:
  "What do users think about this feature?"
  → Delegates to User Researcher
```

**Key Principle:**
**If work requires specialized knowledge, ALWAYS delegate to the specialist.**

---

## Complete Tool Catalog (16 Tools)

### Core Computer Tools (4 tools)

**1. ComputerTool** (VNC/Docker-based GUI automation)
   - Purpose: Original Anthropic computer use tool for containerized environments
   - Versions: ComputerTool20241022, ComputerTool20250124
   - Use when: Running in Docker/VNC environment

**2. LocalComputerTool** (Direct local computer control)
   - Purpose: Full computer control via pyautogui (no Docker/VNC needed)
   - **Screenshot**: Capture screen state with automatic scaling
   - **Mouse Control**:
     - mouse_move: Move cursor to coordinates
     - left_click, right_click, middle_click
     - double_click, triple_click
     - left_click_drag: Drag from current to target position
     - left_mouse_down, left_mouse_up: Low-level mouse control
     - cursor_position: Get current cursor coordinates
   - **Keyboard Control**:
     - type: Type text with realistic interval
     - key: Press key combinations (e.g., "cmd+c", "ctrl+v")
     - hold_key: Hold keys for specified duration
   - **Scrolling**:
     - scroll: Scroll in any direction (up/down/left/right) with amount
     - Support for modifier keys during scroll
   - **Timing**:
     - wait: Pause execution for specified duration

**3. BashTool**
   - Purpose: Execute bash commands in persistent shell
   - Features: Command execution, output capture, session management
   - Safety: 2-minute timeout default, configurable up to 10 minutes

**4. EditTool**
   - Purpose: File editing with find/replace operations
   - Operations: view, create, str_replace, insert, undo
   - Versions: 20241022, 20250429, 20250728
   - Safety: Must read file before editing

### Coding & Development Tools (5 tools)

**5. GlobTool**
   - Purpose: Fast file pattern matching
   - Supports: `**/*.py`, `src/**/*.tsx`, complex glob patterns
   - Output: Sorted by modification time
   - Use when: Finding files by name/pattern

**6. GrepTool**
   - Purpose: Content search with full regex support
   - Features: Context lines (-A/-B/-C), case-insensitive, multiline mode
   - Output modes: content, files_with_matches, count
   - Filtering: By glob pattern or file type
   - Use when: Searching code content

**7. GitTool**
   - Purpose: Git version control operations
   - Operations: status, diff, log, add, commit, push, branch, checkout, merge
   - Safety: Read-only emphasis, warnings for destructive ops
   - Integration: Auto-commits planning changes

**8. PythonExecutionTool**
   - Purpose: Execute Python code in persistent environment
   - Pre-loaded: pandas, numpy, matplotlib, seaborn, plotly
   - Features: Variables persist across executions
   - Use cases: Data analysis, calculations, graph generation

**9. TodoWriteTool**
   - Purpose: Task tracking for complex multi-step workflows
   - Status: pending, in_progress, completed
   - Features: Two-form descriptions (imperative & active)
   - Integration: Auto-syncs with ProjectManager dashboard
   - Use when: Breaking down complex tasks into trackable steps

### Planning & Collaboration Tools (4 tools)

**10. PlanningTool**
   - Purpose: Generate comprehensive planning documents via LLM
   - Creates: project_overview, requirements, technical_spec, roadmap, knowledge_base, decisions, specialist_plans
   - Output: Structured markdown documents in .proto/planning/{project}/
   - Use when: Starting complex projects requiring detailed planning

**11. ReadPlanningTool**
   - Purpose: Read planning documents and project context
   - Operations: list_projects, read_document, get_project_context, check_exists
   - Use when: Continuing existing projects, understanding project state

**12. DelegateTaskTool**
   - Purpose: Delegate tasks to specialist agents
   - Available specialists: marketing-strategy, senior-developer, ux-designer, product-manager (expandable)
   - Features: Passes planning context automatically
   - Use when: CEO needs expert execution from specialists

**13. WorkQueueTool**
   - Purpose: Manage work queue for continuous autonomous operation
   - Operations: add, status, list_pending
   - Priority: LOW, MEDIUM, HIGH, CRITICAL
   - Features: Persistent queue, retry mechanism
   - Use when: Scheduling work for daemon/continuous mode

### Knowledge & Project Management Tools (3 tools)

**14. TaskTool**
   - Purpose: Comprehensive project task management
   - Operations: create, update, complete, block, start, list, get, summary, add_note, add_dependency
   - Features:
     - Status: PENDING, IN_PROGRESS, COMPLETED, BLOCKED, CANCELLED
     - Priority: LOW, MEDIUM, HIGH, CRITICAL
     - Dependencies: Parent-child relationships
     - Metadata: Agent assignment, tags, notes
   - Storage: .proto/planning/{project}/tasks.json
   - Use when: Managing project execution, tracking progress

**15. KnowledgeTool**
   - Purpose: Persistent knowledge base for learning and context
   - Types: technical_decision, learning, pattern, reference, context, best_practice, lesson_learned
   - Operations: add, search, get, update, list, summary, link_to_task
   - Features: Search, tagging, relevance scoring, task linking
   - Storage: .proto/planning/{project}/knowledge/
   - Use when: Storing decisions, patterns, learnings for future reference

**16. ProjectTool**
   - Purpose: Manage and discover projects
   - Operations: list, get, exists, context
   - Features: Helps decide to continue existing or create new project
   - Storage: .proto/planning/ (scans for project directories)
   - Use when: Starting work, checking project existence

### Tool Usage Patterns

- **File Search**: GlobTool (by name) → GrepTool (by content)
- **Code Changes**: GlobTool (find files) → EditTool (make changes) → GitTool (commit)
- **Project Start**: ProjectTool (check exists) → PlanningTool (create docs) → TaskTool (create tasks)
- **Knowledge Capture**: KnowledgeTool (store learning) → link to TaskTool (connect to work)
- **Complex Task**: TodoWriteTool (track progress) → TaskTool (persist in project)
- **Data Analysis**: PythonExecutionTool (calculations) → Chart Generator agent (visualizations)
- **GUI Automation**: LocalComputerTool (screenshot → analyze → click/type)

---

## Data Flow Architecture

```
1. User Request
      ↓
2. Web UI / CLI / API
      ↓
3. CEO Agent
   ├── ComplexityAnalyzer determines: simple/medium/complex/very_complex
   └── If complex → PlanningTool generates docs
      ↓
4. Planning Phase (for complex tasks)
   ├── ProjectTool: Check if project exists
   ├── PlanningTool: Create project_overview, requirements, technical_spec, roadmap
   ├── TaskTool: Break down into tasks with dependencies
   └── KnowledgeTool: Store context & decisions
      ↓
5. Execution Phase
   ├── DelegateTaskTool → Specialist Agents
   ├── Specialists use tools:
   │   ├── Coding tools (Glob, Grep, Git, PythonExec)
   │   ├── Computer tools (LocalComputer for GUI)
   │   ├── Planning tools (Task, Knowledge)
   │   └── Other specialist agents as needed
   └── TodoWriteTool tracks progress
      ↓
6. Results Collection
   ├── Task updates (TaskTool)
   ├── Knowledge capture (KnowledgeTool)
   └── Git commits (GitTool)
      ↓
7. Learning & Persistence
   ├── Knowledge stored in .proto/planning/{project}/knowledge/
   ├── Tasks persisted in .proto/planning/{project}/tasks.json
   └── Logs written to logs/ directory
      ↓
8. Response to User
   └── Web UI / CLI / API
```

---

## Operational Modes

### 1. Interactive Mode (Web UI)
- **Access**: http://localhost:8000
- **Features**:
  - Real-time chat interface
  - Agent selection tree (20+ specialists)
  - File explorer & viewer
  - Message streaming
  - Session persistence
- **Use when**: Active user interaction, development, testing

### 2. Continuous Mode (Company Orchestrator)
- **Process**: Daemon runs in background
- **Features**:
  - Monitors WorkQueue for pending items
  - Assigns work by priority (CRITICAL → HIGH → MEDIUM → LOW)
  - Health checks every loop iteration
  - Graceful shutdown on SIGTERM/SIGINT
  - State persistence for recovery
- **Storage**: ~/.proto/daemon/
- **Use when**: Autonomous business operation, scheduled tasks

### 3. CLI/API Mode
- **Features**:
  - Direct agent invocation
  - REST API endpoints
  - Scriptable interactions
- **Use when**: Automation, integration with other systems

---

## Project Management System

### Dual-Structure Architecture

Each project maintains **two separate folders** for clean organization:

**1. Planning & Meta (~/Proto/{project}/.proto/)**
- Planning documents, decisions, knowledge
- Never mixed with actual code

**2. Actual Project Files (~/Proto/{project}/)**
- Source code, documentation, assets
- Standard project structure

### Complete Directory Structure

```
~/Proto/
└── {project-name}/                # Example: "saas-company"
    │
    ├── .proto/                    # Planning & Meta (System Management)
    │   └── planning/
    │       ├── .project_metadata.json  # Project info (name, description, tags, status)
    │       ├── tasks.json              # TaskManager state & dependencies
    │       │
    │       ├── project_overview.md     # High-level project description
    │       ├── requirements.md         # Detailed requirements
    │       ├── technical_spec.md       # Technical specifications
    │       ├── roadmap.md              # Project roadmap & milestones
    │       ├── knowledge_base.md       # Aggregated knowledge
    │       ├── decisions.md            # Technical decisions log
    │       │
    │       ├── agents/                 # Specialist-specific plans
    │       │   ├── senior-developer_plan.md
    │       │   ├── frontend-developer_plan.md
    │       │   ├── devops-engineer_plan.md
    │       │   ├── product-manager_plan.md
    │       │   ├── ux-designer_plan.md
    │       │   └── marketing-strategy_plan.md
    │       │
    │       └── knowledge/              # KnowledgeStore
    │           ├── index.json          # Knowledge index
    │           ├── technical_decision/
    │           ├── learning/
    │           ├── pattern/
    │           ├── reference/
    │           ├── context/
    │           ├── best_practice/
    │           └── lesson_learned/
    │
    └── [Actual Project Files]     # Standard project structure
        ├── src/                   # Source code
        ├── docs/                  # User documentation
        ├── tests/                 # Test files
        ├── public/                # Public assets
        ├── package.json           # Dependencies
        ├── README.md              # Project readme
        └── ...                    # Other project files

~/.proto/daemon/                   # Global system state
├── work_queue.json                # Pending/active work items
└── orchestrator_state.json        # Runtime state for recovery

logs/                              # System logging
├── proto_sessions.jsonl           # Session events
├── proto_errors.jsonl             # Error tracking
├── proto_tools.jsonl              # Tool invocations
└── proto_system.jsonl             # System events
```

### Why This Structure Works

**Clean Separation:**
- ✅ Planning docs never clutter actual codebase
- ✅ Easy to version control (`.proto/` can be in .gitignore or separate repo)
- ✅ Clear distinction between "what we're doing" vs "what we've built"

**Persistent Context:**
- ✅ All meta information survives across sessions
- ✅ Any agent can read planning context to understand project
- ✅ Knowledge accumulates and informs future decisions

**Scalable:**
- ✅ Each project self-contained
- ✅ Easy to archive, clone, or share
- ✅ Specialist plans kept organized by agent type

### Recovery Mechanisms

**1. Session Recovery**
- All sessions logged to `logs/proto_sessions.jsonl`
- Can replay conversations from logs
- Chat state persists in memory during runtime

**2. Work Queue Recovery**
- WorkQueue persisted to `~/.proto/daemon/work_queue.json`
- On crash/restart: daemon loads queue, retries pending items
- Retry mechanism with configurable max attempts

**3. Project State Recovery**
- All project data in `.proto/planning/{project}/`
- Can reconstruct project state from:
  - tasks.json (TaskManager state)
  - knowledge/index.json (KnowledgeStore state)
  - Planning documents (context)

**4. Git-based Recovery**
- Planning changes auto-committed via GitTool
- Can rollback to previous planning states
- Full audit trail of project evolution

---

## Logging & Monitoring

### 4-Stream Logging Architecture

**1. Sessions Log** (`logs/proto_sessions.jsonl`)
- Events: session_start, session_end, user_message, agent_response
- Contains: timestamps, session_id, agent_id, message content
- Use for: Session replay, conversation analysis

**2. Errors Log** (`logs/proto_errors.jsonl`)
- Events: tool_error, agent_error, system_error
- Contains: stack traces, context, recovery actions
- Use for: Debugging, error pattern analysis

**3. Tools Log** (`logs/proto_tools.jsonl`)
- Events: tool_call, tool_result
- Contains: tool name, parameters, results, duration
- Use for: Tool usage patterns, performance analysis

**4. System Log** (`logs/proto_system.jsonl`)
- Events: daemon_start, daemon_stop, health_check, state_persist
- Contains: system state, metrics, lifecycle events
- Use for: System monitoring, health tracking

### Unified Log Viewer

**Command**: `python -m computer_use_demo.logging.unified`
- Merges all 4 streams chronologically
- Color-coded by event type
- AI-friendly timeline format
- Filters by session, agent, time range

---

## Knowledge Accumulation & Self-Improvement

### How the System Learns

The system implements **active, automatic learning** through three mechanisms:

#### 1. Automatic Knowledge Capture (During Work)

**Location**: [agents/base_agent.py](computer-use-demo/computer_use_demo/agents/base_agent.py#L417-L581)

Every agent automatically captures knowledge after task execution:

```python
# ✅ IMPLEMENTED - Auto-capture on task completion
async def _auto_capture_knowledge(task, result, context, start_time):
    """Runs after EVERY task (success or failure)"""

    if result.success:
        # Capture successful patterns
        knowledge_store.add_entry(
            title=f"Successful approach: {task_summary}",
            type=KnowledgeType.PATTERN,
            content=f"""
                Tools used: {tools_used}
                Duration: {duration}s
                Iterations: {result.iterations}
                Outcome: {result.output}
            """,
            tags=[agent_role, "success", "auto-captured"]
        )

        # Capture complex task learnings
        if result.iterations >= 10:
            knowledge_store.add_entry(
                title=f"Complex task solved: {task}",
                type=KnowledgeType.LEARNING,
                content="Tasks of this nature benefit from breaking into smaller steps"
            )

    else:
        # Capture lessons from failures
        knowledge_store.add_entry(
            title=f"Lesson learned: {task}",
            type=KnowledgeType.LESSON_LEARNED,
            content=f"Error: {error_msg}\nRecommendation: Review task complexity...",
            tags=[agent_role, "failure", "needs-review"]
        )
```

**What Gets Auto-Captured:**
- ✅ Successful tool usage patterns
- ✅ Complex task completion strategies
- ✅ Failure lessons with error context
- ✅ Task duration and iteration metrics
- ✅ Agent-specific approaches

#### 2. Smart Knowledge Retrieval (Before Work)

**Location**: [agents/ceo_agent.py](computer-use-demo/computer_use_demo/agents/ceo_agent.py#L398-L532)

CEO agent searches ALL past projects for relevant knowledge before planning:

```python
# ✅ IMPLEMENTED - Cross-project knowledge search
async def _retrieve_relevant_knowledge(task):
    """Searches across all projects for similar past work"""

    # Extract keywords from current task
    keywords = extract_keywords(task)  # ["authentication", "api", "jwt"]

    # Search across 10 most recent projects
    for project in all_projects[:10]:
        knowledge_store = get_knowledge_store(project)

        # Search for each keyword
        for keyword in keywords[:5]:
            entries = knowledge_store.search_entries(keyword)

            # Return top 10 relevant entries
            relevant_knowledge.append({
                "title": entry.title,
                "content": entry.content[:300],
                "source_project": project.name,
                "type": entry.type
            })

    return relevant_knowledge  # Used in planning context
```

**Benefits:**
- ✅ Avoids repeating past mistakes
- ✅ Applies proven patterns from previous projects
- ✅ Learns from failures across all projects
- ✅ Suggests technical decisions that worked before

#### 3. Background Self-Improvement (Outside Work)

**Location**: [daemon/orchestrator.py](computer-use-demo/computer_use_demo/daemon/orchestrator.py#L477-L695)

Company Orchestrator daemon runs continuous improvement every ~100 seconds:

```python
# ✅ IMPLEMENTED - Background learning loop
async def _background_self_improvement():
    """Runs every 10 event loops (~100 seconds)"""

    # Task 1: Mine knowledge from session logs
    await _mine_knowledge_from_logs()
    # - Analyzes last 100 session events
    # - Detects tool sequences used 3+ times
    # - Recommends creating compound tools
    # - Example: "GlobTool → GrepTool → EditTool" appears 5x
    #   → Suggests "FindAndReplaceTool"

    # Task 2: Analyze error patterns
    await _analyze_error_patterns()
    # - Scans last 50 errors from error log
    # - Identifies top 5 recurring errors
    # - Logs recommendations for fixes
    # - Example: "ToolNotFound" error 12x
    #   → Suggests validating tool availability

    # Task 3: Queue optimization tasks (when idle)
    if idle and completed_tasks >= 10:
        work_queue.add_work(
            "Review knowledge base and consolidate duplicate patterns",
            priority=LOW,
            agent="data-analyst"
        )

        work_queue.add_work(
            "Analyze tool usage logs and identify inefficiencies",
            priority=LOW,
            agent="senior-developer"
        )
```

**Improvement Actions:**
- ✅ Pattern discovery from tool sequences
- ✅ Error trend analysis
- ✅ Knowledge consolidation tasks
- ✅ Tool optimization recommendations
- ✅ Automatic queueing of improvement work

### Self-Improvement Mechanism (Complete Loop)

```
┌──────────────────────────────────────────────────────────────┐
│                   DURING WORK (Real-time)                     │
└──────────────────────────────────────────────────────────────┘
User Task → CEO Agent
    ↓
[SMART RETRIEVAL] Search all projects for relevant knowledge
    ↓
Planning with Past Learnings Applied
    ↓
Task Execution by Specialist
    ↓
[SELF-HEALING RETRY LOOP] 🔥 NEW!
    ├─ Task succeeds? → Continue ✓
    ├─ Task fails? → Analyze failure
    │   ├─ Search knowledge base for similar past failures
    │   ├─ Inject learnings into retry context
    │   ├─ Retry with improved approach (max 3 attempts)
    │   ├─ Success after retry? → Capture recovery pattern as best practice
    │   └─ Still failing? → Queue as "hard failure" for later (HIGH priority)
    ↓
[AUTO-CAPTURE] Extract patterns, tools used, duration, outcome
    ↓
Knowledge Stored in .proto/planning/{project}/knowledge/
    ↓
[AUTO-IMPROVEMENT TASK GENERATION] ⭐
    ├─ Task failed? → Queue "Debug and fix" task (MEDIUM priority)
    ├─ Task took 10+ iterations? → Queue "Optimize process" task (MEDIUM priority)
    └─ Error seen 3+ times? → Queue "Systematic fix" task (HIGH priority)
    ↓
Improvement Tasks Added to Work Queue
    ↓
System Executes Improvement Tasks → Gets Better at Running the Business
    ↓
Indexed & Searchable for Future Tasks

┌──────────────────────────────────────────────────────────────┐
│              OUTSIDE WORK (Background/Idle Time)              │
└──────────────────────────────────────────────────────────────┘
CompanyOrchestrator Event Loop (every ~100 seconds)
    ↓
[LOG MINING] Analyze session logs for tool patterns
    ↓
[ERROR ANALYSIS] Identify recurring failures
    ↓
[KNOWLEDGE-BASED OPTIMIZATION] ⭐ ENHANCED!
    ├─ Analyze each project's knowledge store
    ├─ 5+ failures? → Queue root cause analysis (MEDIUM priority)
    ├─ 5+ patterns? → Queue component creation (LOW priority)
    └─ Multiple projects? → Queue cross-project consolidation (LOW priority)
    ↓
Project-Aware Improvement Tasks Queued
    ↓
Self-Optimization Tasks Execute → System Improves
    ↓
LOOP (continuous autonomous improvement)
```

### What Makes This Different

**Before (Manual):**
- ❌ Agents had to explicitly call `manage_knowledge`
- ❌ Knowledge retrieval required manual search
- ❌ No background learning
- ❌ Each task started "cold"
- ❌ Learnings just stored, never acted upon

**Now (Automatic):**
- ✅ **Auto-capture** after every task (success or failure)
- ✅ **Auto-retrieval** before planning (searches all projects)
- ✅ **Auto-mining** from logs every ~100 seconds
- ✅ **Auto-optimization** tasks queue during idle time
- ✅ **Auto-improvement task generation** (⭐) - turns learnings into actionable work
- ✅ **Project-aware optimization** (⭐) - analyzes knowledge stores to queue improvements
- ✅ **Self-healing retry loop** (🔥 NEW!) - immediate retry with learnings until success or max attempts
- ✅ **Recovery pattern capture** (🔥 NEW!) - successful retries become best practices
- ✅ System learns continuously AND actively improves itself while working

### Metrics & Observability

All self-improvement activities are logged:

```jsonl
// Session log - knowledge auto-captured
{"event_type": "knowledge_auto_captured", "agent_role": "ceo", "task_success": true, "project_name": "saas-app", "duration_seconds": 45.2}

// Session log - knowledge retrieved
{"event_type": "knowledge_retrieved", "keywords": ["authentication", "api"], "num_results": 7, "projects_searched": 10}

// 🔥 NEW - Session log - self-healing retry attempt
{"event_type": "self_correction_attempt", "task": "Deploy backend API", "attempt": 1, "error": "ConnectionError: Connection refused"}
{"event_type": "failure_analysis_completed", "error_category": "ConnectionError", "similar_failures": 3, "helpful_patterns": 2}

// 🔥 NEW - Session log - recovery pattern captured
{"event_type": "recovery_pattern_captured", "task": "Deploy backend API", "retry_attempt": 2, "project_name": "saas-app"}

// 🔥 NEW - Session log - self-correction exhausted (too hard for now)
{"event_type": "self_correction_exhausted", "task": "Deploy backend API", "total_attempts": 3, "final_error": "Persistent connection failure"}

// ⭐ Session log - improvement task automatically queued
{"event_type": "improvement_task_queued", "reason": "task_failure", "project_name": "saas-app", "original_task": "Deploy backend API"}
{"event_type": "improvement_task_queued", "reason": "inefficient_execution", "iterations": 15, "project_name": "saas-app"}
{"event_type": "improvement_task_queued", "reason": "recurring_error", "error_category": "TimeoutError", "occurrence_count": 4}
{"event_type": "improvement_task_queued", "reason": "self_correction_exhausted", "retry_attempts": 3, "original_task": "Deploy backend API"}

// System log - pattern discovered
{"event_type": "pattern_discovered", "tool_sequence": ["glob", "grep", "edit"], "occurrence_count": 5, "recommendation": "Consider compound tool"}

// ⭐ System log - project-aware optimization tasks queued
{"event_type": "optimization_tasks_queued", "tasks_added": 3, "reason": "knowledge_based_optimization", "projects_analyzed": 3}
```

---

## Training & Verification Systems

### Training System

**Location**: `computer_use_demo/training/`

**Test Suites**:
- QA Testing
- DevOps
- Senior Developer
- Sales
- Customer Success
- Technical Writer
- Data Analyst

**Features**:
- Test case definitions
- Validation harness
- Training data storage: `.proto/training/`
- Agent performance evaluation

### Verification System

**Location**: `computer_use_demo/verification/`

**Components**:
1. **ScreenshotAnalyzer**: Analyze GUI state from screenshots
2. **StructuralChecker**: Verify code structure & correctness
3. **FeedbackLoop**: Iterative improvement cycles

**Usage**:
- Verify task completion
- Validate generated code
- Ensure GUI automation succeeded
- Provide feedback for refinement

---

## Key Principles

### 1. Intelligent Delegation (Most Important)
**Core Philosophy: Right Agent for Right Task**
- ✅ CEO orchestrates, specialists execute
- ✅ Any agent can delegate to any specialist when needed
- ✅ Not constrained by organizational hierarchy
- ✅ Specialists are domain experts - always prefer them
- ❌ Never do specialized work outside your expertise
- ❌ Never skip delegation when specialist exists

**Why This Matters:**
- Better quality (specialists know best practices)
- Faster execution (specialists work in their domain)
- Scalable (multiple specialists work in parallel)
- Continuous improvement (specialists accumulate domain knowledge)

### 2. Dual-Structure Project Organization
**Planning Separate from Code**
- ✅ Planning/meta in `{project}/.proto/planning/`
- ✅ Actual code in `{project}/` (src/, docs/, tests/)
- ✅ Clear separation: "what we're doing" vs "what we've built"
- ✅ Planning survives code changes, provides persistent context

**Benefits:**
- Never clutter codebase with planning docs
- Easy to version control separately
- Context available to all agents across sessions
- Specialist plans organized by agent type

### 3. Enterprise-Grade Architecture
- Multi-tier design (Presentation → Orchestration → Agents → Planning → Tools → Infrastructure)
- Production-ready components (logging, monitoring, recovery)
- Scalable and maintainable

### 4. Continuous Operation
- Can run autonomously via CompanyOrchestrator daemon
- WorkQueue system for scheduled/ongoing work
- Health monitoring and graceful degradation

### 5. Persistent Learning & Self-Improvement
- Knowledge accumulates across sessions
- Decisions, patterns, learnings stored permanently
- Each project makes future projects better
- System learns from both successes and failures
- Auto-queues optimization tasks during idle time

### 6. Universal Tool Access
- All 16 tools available to all agents
- Tools can be chained for complex operations
- Smart tool selection based on task requirements
- Specialists know optimal tool combinations for their domain

### 7. Flat Peer-to-Peer Execution
- Tree structure for user navigation/discovery
- Actual execution is flexible peer-to-peer
- Best agent/tool selected regardless of hierarchy
- Any agent can call any other agent when needed

### 8. State Persistence & Recovery
- All project state in `.proto/planning/{project}/`
- Recovery from crashes/restarts
- Full audit trail via Git commits
- Work queue persists for daemon recovery

---

## Project Lifecycle Example

### Complete Example: Building a SaaS Application

**1. User Request**
```
"Build a SaaS application for project management with authentication,
team collaboration, and real-time updates"
```

**2. CEO Agent Analysis & Planning**
```python
# Step 1: Analyze complexity
complexity = analyzer.analyze_task(user_request)
# Result: "very_complex" → Triggers comprehensive planning

# Step 2: Create project structure
project_manager.create_project("saas-project-mgmt")
# Creates:
# ~/Proto/saas-project-mgmt/
# ~/Proto/saas-project-mgmt/.proto/planning/

# Step 3: Generate planning documents
planning_tool.create(
    project_name="saas-project-mgmt",
    documents=[
        "project_overview",     # High-level vision
        "requirements",         # Detailed requirements
        "technical_spec",       # Architecture & tech stack
        "roadmap"              # Implementation phases
    ]
)
# All saved in ~/Proto/saas-project-mgmt/.proto/planning/

# Step 4: Break down into specialist tasks
tasks = [
    ("Product Manager", "Define features & prioritize roadmap"),
    ("UX Designer", "Design user interface & workflows"),
    ("Backend Developer", "Build API & authentication"),
    ("Frontend Developer", "Create React UI"),
    ("DevOps Engineer", "Set up deployment pipeline"),
]
```

**3. CEO Delegates to Product Manager**
```python
delegate_tool.delegate(
    specialist="product-manager",
    task="Define product requirements and feature prioritization",
    context=read_planning_tool.get_project_context("saas-project-mgmt")
)
```

**4. Product Manager Creates Detailed Requirements**
```python
# Product Manager reads planning context from .proto/planning/
# Writes detailed requirements
edit_tool.create(
    file="~/Proto/saas-project-mgmt/.proto/planning/requirements.md",
    content="""
    ## Core Features
    1. User Authentication (Google, GitHub SSO)
    2. Team Workspace Management
    3. Real-time Task Board
    4. Comments & Notifications
    ...
    """
)

# Updates knowledge base
knowledge_tool.add(
    title="Feature Priority: Real-time collaboration critical",
    type="technical_decision",
    content="Users expect instant updates - WebSocket required"
)
```

**5. CEO Delegates to UX Designer**
```python
delegate_tool.delegate(
    specialist="ux-designer",
    task="Design user interface for task management and collaboration"
)
```

**6. UX Designer Creates Mockups**
```python
# UX Designer creates designs in actual project folder
# Note: .proto/ is for planning, actual files go in project root
bash_tool.run("cd ~/Proto/saas-project-mgmt && mkdir -p designs/")
# Creates Figma files, wireframes, etc. in ~/Proto/saas-project-mgmt/designs/

# Documents decisions in planning
edit_tool.create(
    file="~/Proto/saas-project-mgmt/.proto/planning/agents/ux-designer_plan.md",
    content="UI approach: Kanban-style board with drag-drop..."
)
```

**7. CEO Delegates to Backend Developer**
```python
delegate_tool.delegate(
    specialist="backend-developer",
    task="Implement authentication API and database schema",
    context=read_planning_tool.get_project_context("saas-project-mgmt")
)
```

**8. Backend Developer Implements API**
```python
# Backend Dev reads all planning context
planning_context = read_planning_tool.get_project_context("saas-project-mgmt")

# Creates actual code in project folder (NOT in .proto/)
bash_tool.run("cd ~/Proto/saas-project-mgmt && mkdir -p src/api")

# Implements authentication
edit_tool.create(
    file="~/Proto/saas-project-mgmt/src/api/auth.py",
    content="""
    from fastapi import FastAPI, Depends
    from sqlalchemy.orm import Session
    # ... implementation
    """
)

# Runs tests
python_exec.run("cd ~/Proto/saas-project-mgmt && pytest tests/")

# Commits code
git_tool.commit("Add authentication API with JWT tokens")

# Documents decision in planning/knowledge
knowledge_tool.add(
    project="saas-project-mgmt",
    title="Auth Stack: FastAPI + JWT + SQLAlchemy",
    type="best_practice",
    content="FastAPI provides excellent async support for real-time features",
    tags=["backend", "authentication", "fastapi"]
)
```

**9. CEO Delegates to Frontend Developer**
```python
delegate_tool.delegate(
    specialist="frontend-developer",
    task="Build React UI connecting to backend API",
    context=read_planning_tool.get_project_context("saas-project-mgmt")
)
```

**10. Frontend Developer Builds UI**
```python
# Frontend Dev creates React app in actual project folder
bash_tool.run("cd ~/Proto/saas-project-mgmt && npx create-react-app frontend")

# Implements components
edit_tool.create(
    file="~/Proto/saas-project-mgmt/frontend/src/components/TaskBoard.tsx",
    content="// Task board implementation with drag-drop..."
)

# Integrates with backend
edit_tool.create(
    file="~/Proto/saas-project-mgmt/frontend/src/api/client.ts",
    content="// API client connecting to FastAPI backend..."
)

# Updates planning with frontend decisions
knowledge_tool.add(
    project="saas-project-mgmt",
    title="Frontend Stack: React + TypeScript + TailwindCSS",
    type="technical_decision",
    tags=["frontend", "react", "typescript"]
)
```

**11. CEO Delegates to DevOps Engineer**
```python
delegate_tool.delegate(
    specialist="devops-engineer",
    task="Set up deployment pipeline and hosting"
)
```

**12. DevOps Sets Up Deployment**
```python
# DevOps creates deployment configs in project folder
edit_tool.create(
    file="~/Proto/saas-project-mgmt/Dockerfile",
    content="FROM python:3.11..."
)

edit_tool.create(
    file="~/Proto/saas-project-mgmt/docker-compose.yml",
    content="services:\n  backend:\n    ..."
)

# Documents deployment strategy
knowledge_tool.add(
    project="saas-project-mgmt",
    title="Deployment: Docker + Railway",
    type="technical_decision",
    content="Railway provides easy deployment with auto-scaling"
)
```

**13. Final Project Structure**
```
~/Proto/saas-project-mgmt/
├── .proto/                          # Planning & Meta
│   └── planning/
│       ├── project_overview.md      # CEO created
│       ├── requirements.md          # Product Manager updated
│       ├── technical_spec.md        # Backend Dev contributed
│       ├── roadmap.md
│       ├── knowledge/               # All specialists contributed
│       │   └── technical_decision/
│       │       ├── auth-stack.json
│       │       ├── frontend-stack.json
│       │       └── deployment.json
│       └── agents/                  # Specialist plans
│           ├── product-manager_plan.md
│           ├── ux-designer_plan.md
│           ├── backend-developer_plan.md
│           ├── frontend-developer_plan.md
│           └── devops-engineer_plan.md
│
└── [Actual Project Files]           # All specialists built this
    ├── src/                         # Backend code
    │   ├── api/
    │   ├── models/
    │   └── services/
    ├── frontend/                    # Frontend code
    │   ├── src/
    │   ├── public/
    │   └── package.json
    ├── designs/                     # UX designs
    ├── tests/                       # QA tests
    ├── Dockerfile                   # DevOps config
    ├── docker-compose.yml
    └── README.md
```

**14. Continuous Improvement**
```python
# All knowledge captured during execution
# Future "build SaaS" projects will:
# - Retrieve this knowledge automatically
# - Apply proven patterns
# - Avoid same mistakes
# - Start from accumulated wisdom
```

### Key Takeaways from Example

✅ **CEO orchestrated, never coded directly**
✅ **Each specialist worked in their domain**
✅ **Planning (.proto/) separate from code**
✅ **All decisions documented in knowledge base**
✅ **Specialists collaborated through CEO coordination**
✅ **Project structure clean and organized**
✅ **Knowledge persists for future projects**

---

## Extension Points

### Adding New Tools

1. Create tool class inheriting from `BaseAnthropicTool`
2. Implement `__call__` method
3. Register in `tools/groups.py`
4. Add to appropriate TOOL_GROUPS

### Adding New Specialist Agents

1. Create agent definition in `.claude/agents/specialists/{name}.md`
2. Add to `agent_org_structure.py`
3. Optional: Create test suite in `training/`
4. Optional: Add specialized sub-agents

### Customizing Planning Templates

1. Edit templates in `planning/documents.py`
2. Modify `PlanningDocuments.templates` dict
3. Adjust prompts for LLM generation
4. Test with `PlanningTool`

---


---

## Hetzner Cloud Deployment

### Quick Setup
```bash
export HETZNER_API_TOKEN=your-token
export ANTHROPIC_API_KEY=your-key
cd computer-use-demo/hetzner-deploy
pip3 install -r requirements.txt
./deploy.sh
```

### Deployment Options
- **Server**: Hetzner CX22 (2 vCPU, 4GB RAM)
- **Cost**: €0.007/hr (~€5/month if 24/7)
- **Build Time**: 10-15 min (fresh) or 1-2 min (from snapshot)
- **Location**: Ashburn, VA (USA) or Nuremberg, Germany (nbg1)

### Features
- Auto-start on boot
- Pause/resume (€0/hr when paused)
- Snapshots for quick cloning
- HTTP Basic Auth (admin/anthropic2024)

### Control Dashboard
```bash
python3 control_panel.py
# Access: http://localhost:5500
```

**Dashboard Actions:**
- Create/delete instances
- Pause/resume for cost savings
- Create snapshots (~€0.20/month storage)
- Clone from snapshots (1-2 min deploy)

### Cost Savings
- Running 24/7: ~€7/month
- Snapshot + Delete: ~€0.20/month
- **Savings: ~€6.80/month (97%)**

---

*Last updated: 2025-12-19*
