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

## State Management & Persistence

### Persistent Storage Architecture

```
~/.proto/
├── daemon/
│   ├── work_queue.json           # Pending/active work items
│   └── orchestrator_state.json   # Runtime state for recovery
│
└── planning/
    └── {project-slug}/            # e.g., "saas-company", "xclone"
        ├── .project_metadata.json # Project metadata (name, description, tags)
        ├── tasks.json             # TaskManager state
        │
        ├── project_overview.md    # High-level project description
        ├── requirements.md        # Detailed requirements
        ├── technical_spec.md      # Technical specifications
        ├── roadmap.md             # Project roadmap
        ├── knowledge_base.md      # Aggregated knowledge
        ├── decisions.md           # Technical decisions log
        │
        ├── agents/                # Specialist-specific plans
        │   ├── senior-developer_plan.md
        │   ├── product-manager_plan.md
        │   └── marketing-strategy_plan.md
        │
        ├── knowledge/             # KnowledgeStore
        │   ├── index.json         # Knowledge index
        │   ├── technical_decision/
        │   ├── learning/
        │   ├── pattern/
        │   ├── reference/
        │   ├── context/
        │   ├── best_practice/
        │   └── lesson_learned/
        │
        └── data/                  # Project artifacts
            ├── inputs/            # Input files
            ├── outputs/           # Generated outputs
            └── artifacts/         # Build artifacts, exports

logs/                              # Logging system
├── proto_sessions.jsonl           # Session events
├── proto_errors.jsonl             # Error tracking
├── proto_tools.jsonl              # Tool invocations
└── proto_system.jsonl             # System events
```

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

### 1. Flexible Delegation
- Any agent can call any other agent based on task needs
- Not constrained by organizational hierarchy
- CEO orchestrates, but specialists self-organize

### 2. Enterprise-Grade Architecture
- Multi-tier design (Presentation → Orchestration → Agents → Planning → Tools → Infrastructure)
- Production-ready components (logging, monitoring, recovery)
- Scalable and maintainable

### 3. Continuous Operation
- Can run autonomously via CompanyOrchestrator daemon
- WorkQueue system for scheduled/ongoing work
- Health monitoring and graceful degradation

### 4. Persistent Learning
- Knowledge accumulates across sessions
- Decisions, patterns, learnings stored permanently
- Each project makes future projects better

### 5. Tool Access
- All 16 tools available to all agents
- Tools can be chained for complex operations
- Smart tool selection based on task requirements

### 6. Hierarchical UI, Flat Execution
- Tree structure for user navigation/discovery
- Actual execution is flexible peer-to-peer
- Best agent/tool selected regardless of hierarchy

### 7. State Persistence
- All project state in `.proto/planning/{project}/`
- Recovery from crashes/restarts
- Full audit trail via Git commits

### 8. Self-Improvement
- System learns from each interaction
- Knowledge base grows continuously
- Future performance improves automatically

---

## Project Lifecycle Example

### Starting a New Project

**1. User Request**: "Build a SaaS application for project management"

**2. CEO Analysis**:
```python
complexity = analyzer.analyze_task(user_request)  # Result: "very_complex"
# → Triggers comprehensive planning
```

**3. Planning Phase**:
```python
# ProjectTool checks: does "saas-project-management" exist?
if not project_tool.exists("saas-project-management"):
    # PlanningTool creates:
    planning_tool.create(
        project_name="saas-project-management",
        documents=["project_overview", "requirements", "technical_spec", "roadmap"]
    )
```

**4. Task Breakdown**:
```python
# TaskTool creates hierarchical tasks:
task_tool.create(
    title="Build SaaS Backend",
    priority="HIGH",
    dependencies=[],
    subtasks=[
        "Design database schema",
        "Implement authentication",
        "Create API endpoints",
        "Add rate limiting"
    ]
)
```

**5. Execution**:
```python
# CEO delegates to specialists:
delegate_tool.delegate(
    specialist="senior-developer",
    task="Build backend infrastructure",
    context=read_planning_tool.get_project_context("saas-project-management")
)
```

**6. Specialist Work**:
```python
# Senior Developer uses tools:
glob_tool.find("src/**/*.py")  # Find relevant files
grep_tool.search("class.*Model", type="py")  # Find models
edit_tool.create("src/models/user.py", content=...)  # Create new file
python_exec.run("pytest tests/")  # Run tests
git_tool.commit("Add User model with authentication")
```

**7. Knowledge Capture**:
```python
knowledge_tool.add(
    title="FastAPI + SQLAlchemy + Alembic Stack",
    type="best_practice",
    content="This stack provides excellent dev experience for SaaS apps",
    tags=["fastapi", "sqlalchemy", "backend"]
)
```

**8. Progress Tracking**:
```python
task_tool.update(
    task_id="build-backend",
    status="COMPLETED",
    notes="Backend infrastructure complete with auth and core models"
)
```

**9. Continuous Improvement**:
- Knowledge stored for future SaaS projects
- Patterns identified and catalogued
- Next SaaS project starts with this accumulated wisdom

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

## System Status

### ✅ Completed
- Multi-agent architecture (20+ specialists with 4-level nesting)
- Complete tool suite (16 tools across 4 categories)
- Planning & state management (ProjectManager, TaskManager, KnowledgeStore)
- Work queue & orchestration (CompanyOrchestrator, WorkQueue)
- Logging & monitoring (4-stream JSONL system, unified viewer)
- Web UI (FastAPI, dark theme, real-time streaming, agent tree)
- Persistent storage architecture (.proto/ folder structure)
- Git integration for audit trail
- Training & verification systems (7 test suites, FeedbackLoop)
- **✨ AUTOMATIC SELF-IMPROVEMENT SYSTEM:**
  - ✅ Auto-knowledge capture after every task execution
  - ✅ Smart cross-project knowledge retrieval before planning
  - ✅ Background log mining for pattern discovery
  - ✅ Error trend analysis and recommendations
  - ✅ **Auto-improvement task generation** (⭐ NEW - Jan 2025)
    - Automatically queues debugging tasks when tasks fail
    - Queues optimization tasks when tasks are inefficient (10+ iterations)
    - Queues systematic fix tasks when errors repeat 3+ times
    - All improvement tasks linked to originating project
  - ✅ **Project-aware optimization queueing** (⭐ ENHANCED - Jan 2025)
    - Analyzes each project's knowledge store for improvement opportunities
    - Queues root cause analysis when 5+ failures accumulated
    - Queues component creation when 5+ patterns identified
    - Cross-project knowledge consolidation when idle
  - ✅ Continuous learning AND active self-improvement while working

### 🚧 In Progress

**High Priority:**
- ✅ ~~Self-improvement during work (auto-capture + auto-improvement tasks implemented)~~
- ✅ ~~Self-improvement outside work (background daemon + project-aware optimization implemented)~~
- Multi-project orchestration enhancements
- Agent parallelization on single computer
- Add newest models (Claude 3.7, etc.)
- Add alternative models (Gemini, GPT-4, etc.)

**Next Phase:**
- Architecture resilience improvements
- Agent parallelization across multiple computers
- Cloud computer control & provisioning
- Distributed agent execution
- Multi-company management system
- Marketing automation agents
- Content generation agents
- Agency services (marketing, dev, backoffice for clients)
- Advanced metrics & analytics dashboard
- ML-based pattern recognition
- Enhanced verification with visual regression testing
