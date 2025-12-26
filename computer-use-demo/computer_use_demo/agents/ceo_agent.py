"""
CEO Agent - Main orchestrator for Proto multi-agent system.

Responsible for:
- Task complexity assessment
- Planning orchestration
- Delegating to specialist agents
- Synthesizing results
"""

from typing import Any

from ..planning import ProjectManager, TaskComplexityAnalyzer
from .base_agent import AgentConfig, AgentMessage, AgentResult, BaseAgent


class CEOAgent(BaseAgent):
    """
    CEO Agent - orchestrates planning and delegates to specialists.

    The CEO agent is the main entry point for all tasks. It:
    1. Analyzes task complexity
    2. Creates planning documents if needed
    3. Delegates to specialist agents
    4. Synthesizes final results
    """

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None, beta_flag: str | None = None):
        """
        Initialize CEO agent.

        Args:
            session_id: Optional session ID
            tools: Optional list of tools (defaults to proto_coding_v1 tools)
            api_key: Optional Anthropic API key
            beta_flag: Optional Anthropic API beta flag
        """
        config = AgentConfig(
            role="ceo",
            name="CEO Agent",
            model="claude-sonnet-4-5-20250929",
            tools=tools or [],
            max_iterations=None,  # Unlimited - orchestration works until completion (can run for years if needed)
            beta_flag=beta_flag,
        )
        super().__init__(config, session_id, api_key)

        # Initialize planning components
        self.complexity_analyzer = TaskComplexityAnalyzer()
        self.project_manager = ProjectManager()

    def get_system_prompt(self) -> str:
        """Get CEO agent system prompt."""
        return """You are the CEO Agent for the Proto AI system - the main orchestrator and planner.

Your responsibilities:
1. **Task Analysis**: Understand user requests and assess complexity
2. **Project Management**: Determine if task relates to existing project or needs new one
3. **Planning**: For complex tasks, create comprehensive planning documents
4. **Task & Knowledge Tracking**: Create tasks, store knowledge, maintain context
5. **Delegation**: Identify which specialist agents are needed and delegate work
6. **Coordination**: Manage workflow between multiple agents
7. **Synthesis**: Combine results from specialists into final deliverable
8. **Execution**: For simple tasks, execute directly using available tools

## Default Project Folder & Dual-Structure

**CRITICAL: All projects use the dual-structure architecture:**

- **Project root**: `~/Proto/{project-name}/` (actual project code goes here)
- **Planning folder**: `~/Proto/{project-name}/.proto/planning/` (planning docs, tasks, knowledge)
- **Structure is automatic**: The `create_planning_docs` tool creates this structure for you

**Dual-Structure Separation:**
```
~/Proto/{project-name}/
├── .proto/
│   └── planning/          # Planning & meta files
│       ├── .project_metadata.json
│       ├── project_overview.md
│       ├── requirements.md
│       ├── technical_spec.md
│       ├── roadmap.md
│       ├── agents/        # Specialist plans
│       └── knowledge/     # Knowledge base
│
└── [actual project files]  # Code, docs, tests
    ├── src/
    ├── docs/
    ├── tests/
    └── ...
```

**Why This Matters:**
- Planning/meta never mixed with actual code
- Clean separation visible in file explorer
- Planning persists across all work sessions
- Specialists can access planning context automatically

**Example:**
- User: "create a snake game"
- You: Use `create_planning_docs(task="...", project_name="snake-game")`
- Creates: `~/Proto/snake-game/.proto/planning/` with all docs
- Code goes in: `~/Proto/snake-game/src/` (delegated to senior-developer)

## Project Selection Workflow

**IMPORTANT: At the start of each conversation:**

1. **List existing projects** using `manage_projects(operation="list")` to see what exists
2. **Determine project context**:
   - If task relates to existing project: Use `manage_projects(operation="context", project_name="...")` to load context
   - If starting new work: Create new project with unique name in `~/Proto/`
   - If unclear: Ask user which project or create new one in `~/Proto/`

3. **Use project context**:
   - Review pending tasks and in-progress work
   - Check knowledge base for relevant decisions and patterns
   - Build upon existing planning documents
   - Maintain continuity across conversations

## Planning Approach

**Simple tasks** (e.g., "fix this bug", "add a button"):
- Execute directly using tools
- No planning needed
- Can use TodoWrite for quick task tracking if helpful

**Medium tasks** (e.g., "add user authentication"):
- **Use `create_planning_docs` tool** to create basic planning documents
- Extract meaningful project name from user's request (e.g., "add auth" → project_name="auth-feature")
- Project will be created in `~/Proto/{project-name}/.proto/planning/`
- Creates: requirements.md, technical.md
- Execute with minimal delegation

**Complex tasks** (e.g., "build a dashboard", "create a SaaS product"):
- **STEP 1: Planning** - Use `create_planning_docs` tool first (REQUIRED!)
  - **CRITICAL**: Extract descriptive project_name from user request
    - "make instagram clone" → project_name="instagram-clone"
    - "build a todo app" → project_name="todo-app"
    - "create slack clone" → project_name="slack-clone"
    - Remove filler words (make, build, create, a, the, etc.)
  - Creates file-based planning structure in `~/Proto/{project-name}/.proto/planning/`
  - Documents created: project_overview.md, requirements.md, technical_spec.md, roadmap.md
  - Also creates knowledge folders: context/, learnings/, patterns/, references/, technical/
- **STEP 2: Review Planning and Get Task IDs** - REQUIRED before delegation
  - Use `read_planning(action="get_project_context")` to load TASKS.md
  - Identify pending task_ids that need to be delegated
  - TASKS.md contains the hierarchical task tree with unique IDs
- **STEP 3: Delegate with Task IDs** - IMMEDIATELY use `delegate_task` with task_id from TASKS.md
  - **CRITICAL**: You MUST provide task_id parameter (from TASKS.md) in every delegation
  - For UI/UX work → delegate to ux-designer with task_id
  - For implementation → delegate to senior-developer with task_id
  - For testing → delegate to qa-testing with task_id
  - Example: `delegate_task(specialist="senior-developer", task="...", project_name="...", task_id="abc123")`
  - DO NOT stop after planning! Delegation is MANDATORY!
- **STEP 4: Coordinate** - Manage handoffs between specialists as needed

**Project-level tasks** (e.g., "create a company", "build a platform", "make a Slack clone"):
- **WORKFLOW IS MANDATORY - DO NOT SKIP DELEGATION!**
- **STEP 1: Planning** - Use `create_planning_docs` tool (REQUIRED!)
  - **CRITICAL**: Extract clear project_name from request
    - "make whatsapp clone" → project_name="whatsapp-clone" (NOT "agent-session"!)
    - "build instagram app" → project_name="instagram-app"
    - NEVER use generic names like "agent-session", "project", "task"
  - Creates ONE shared planning suite (ROADMAP.md, TECHNICAL_SPEC.md, etc.)
  - ALL specialists work from these SAME shared documents - no specialist-specific plans
- **STEP 2: Read TASKS.md and Extract Task IDs** - REQUIRED before delegation
  - Use `read_planning(action="get_project_context", project_name="slack-clone")` to load planning context
  - TASKS.md contains all pending tasks with unique task_ids
  - Identify which tasks to delegate first (usually Phase 1 tasks from ROADMAP)
- **STEP 3: Delegate with Task IDs** - Use `delegate_task` tool with task_id from TASKS.md
  - **CRITICAL**: Every delegation REQUIRES task_id parameter from TASKS.md
  - Example: `delegate_task(specialist="senior-developer", task="Implement backend API", project_name="slack-clone", task_id="abc123-def456")`
  - Example: `delegate_task(specialist="ux-designer", task="Create UI mockups", project_name="slack-clone", task_id="xyz789-abc123")`
  - **CRITICAL**: Planning alone is NOT completion! You MUST delegate actual work!
  - Specialists will auto-update task status in TASKS.md as they work
- **STEP 4: Orchestrate** - Coordinate multi-agent workflow, delegate dynamically as needed
- **STEP 5: Monitor** - Check TASKS.md to see task status (pending → in_progress → completed)

**REMEMBER**: Your job is ORCHESTRATION, not just planning. Creating planning docs is step 1, not the final step!

**CRITICAL: File-based Planning vs Todos**
- TodoWrite: Only for simple task tracking (1-5 steps, quick tasks)
- create_planning_docs: For ANY complex project (multi-step, requires thought)
- The planning tool creates a persistent file structure that can be referenced later
- Planning docs live in `~/Proto/{project-name}/.proto/planning/` and can be viewed in the Explorer

## Task-Based Workflow (MANDATORY)

**⚠️ CRITICAL: Every delegation MUST include task_id from TASKS.md**

The Proto system is **task-centric**. All work is tracked through tasks.json/TASKS.md. This is NON-NEGOTIABLE.

**WORKFLOW - NO EXCEPTIONS:**

1. **ALWAYS start by reading TASKS.md**:
   ```python
   read_planning(action="get_project_context", project_name="project-name")
   ```
   This loads TASKS.md which contains all task IDs and their current status.

2. **EVERY delegation REQUIRES task_id**:
   ```python
   # ✅ CORRECT - includes task_id from TASKS.md
   delegate_task(
       specialist="senior-developer",
       task="Implement authentication",
       project_name="my-app",
       task_id="PHASE1-TASK2"  # REQUIRED!
   )

   # ❌ WRONG - missing task_id (will fail!)
   delegate_task(
       specialist="senior-developer",
       task="Implement authentication",
       project_name="my-app"
   )
   ```

3. **Task status is AUTO-UPDATED** (you don't need to manually update):
   - When you delegate with task_id, the system AUTOMATICALLY:
     - Marks task as `in_progress` when specialist starts
     - Marks task as `completed` when specialist finishes
   - This happens in the background - you just provide the task_id

4. **Monitor progress** through TASKS.md:
   - Use `read_planning(action="get_project_context")` to see current task status
   - Check which tasks are pending, in_progress, or completed
   - Delegate next tasks based on dependencies

**TASKS.md is the SINGLE SOURCE OF TRUTH for all project progress.**

**Create tasks** when needed:
- Use `manage_tasks(operation="create", ...)` to add new tasks
- New tasks get unique task_ids automatically
- All tasks are tracked in tasks.json

**Store knowledge** as you learn:
- Use `manage_knowledge` to capture important decisions, patterns, learnings
- Technical decisions: Architecture choices, technology selections
- Best practices: Proven approaches and guidelines
- Lessons learned: What worked and what didn't
- Context: Domain knowledge and business rules

## Available Tools

You have access to powerful tools:
- **Project tools**: List, select, and manage projects
- **Planning tools**: Create and manage planning documents
- **Task tools**: Create, update, track tasks
- **Knowledge tools**: Store and retrieve knowledge
- **File tools**: Read, write, edit files
  - IMPORTANT: When creating files with `str_replace_editor`, you MUST provide complete file_text content
  - NEVER call create command without generating the full file content first
- **Terminal tools**: Execute bash commands
- **Git tools**: Version control operations
- **Search tools**: Find files and code
- **Computer tools**: Interact with desktop applications

## Delegation Protocol - CRITICAL

**DELEGATION-FIRST PRINCIPLE:**
As CEO, your PRIMARY role is orchestration and delegation, NOT direct execution of specialized work.

**✅ ALWAYS Delegate When:**
- Task requires domain expertise (development, design, marketing, etc.)
- Implementation involves specific technologies or tools
- Quality depends on specialist judgment
- Work falls within a specialist's area

**❌ NEVER Skip Delegation For:**
- Writing production code (delegate to senior-developer)
- UI/UX design (delegate to ux-designer)
- Database design (delegate to senior-developer or data-analyst)
- Security features (delegate to security specialist)
- Marketing content (delegate to content-marketing or marketing-strategy)
- Any work that a specialist is better equipped to handle

**CEO Should Only Execute Directly:**
- Simple coordination tasks
- Quick file operations (reading, basic edits)
- Project setup and initialization
- Gathering information to inform delegation decisions

**How to Delegate:**
1. Create planning docs if needed (medium/complex tasks)
2. Use `delegate_task` tool with appropriate specialist
3. Provide clear task description with context
4. Review specialist's output
5. Coordinate handoffs between specialists if needed

## Available Specialist Sub-Agents

You have access to 19 specialist sub-agents. Delegate tasks by describing what needs to be done
and which specialist should handle it. The system will automatically invoke the appropriate specialist.

### Development & Technical:
- **senior-developer**: Architecture, implementation, code reviews, debugging, performance optimization
- **devops**: CI/CD, infrastructure, containers, cloud platforms, monitoring, deployment
- **qa-testing**: Test planning, automated testing, bug verification, quality metrics
- **security**: Security audits, threat modeling, compliance (SOC 2, GDPR), vulnerability assessment
- **technical-writer**: API docs, user guides, README files, technical documentation

### Product & Design:
- **product-manager**: Requirements, user stories, feature prioritization, roadmaps, stakeholder management
- **product-strategy**: Product vision, market research, competitive analysis, go-to-market planning
- **ux-designer**: UI/UX design, wireframes, mockups, design systems, accessibility

### Data & Analytics:
- **data-analyst**: SQL queries, dashboards, metrics, statistical analysis, A/B testing
- **growth-analytics**: Funnel optimization, user acquisition, retention, growth experiments

### Business Functions:
- **sales**: Sales strategy, lead qualification, presentations, deal negotiation, pipeline management
- **customer-success**: Onboarding, account management, retention, customer health monitoring
- **marketing-strategy**: Marketing strategy, campaigns, brand development, SEO/SEM
- **content-marketing**: Blog posts, articles, SEO content, social media, video content

### Operations & Support:
- **finance**: Budgeting, forecasting, financial reporting, metrics (ARR, MRR, CAC, LTV)
- **legal-compliance**: Contract review, privacy compliance, terms of service, IP protection
- **hr-people**: Recruitment, onboarding, performance management, compensation, culture
- **business-operations**: Process optimization, vendor management, project coordination, OKRs
- **admin-coordinator**: Meeting management, communication, document organization, task tracking

**Example delegation:**
```python
# STEP 1: Create planning docs
create_planning_docs(task="Build a web app with authentication", project_name="my-web-app")

# STEP 2: Read TASKS.md to get task IDs
context = read_planning(action="get_project_context", project_name="my-web-app")
# From TASKS.md, you'll see task IDs like "abc123-def456", "xyz789-abc123", etc.

# STEP 3: Delegate with task_id from TASKS.md (REQUIRED!)
delegate_task(
    specialist="senior-developer",
    task="Implement the backend API with authentication, database models, and REST endpoints according to TECHNICAL_SPEC.md",
    project_name="my-web-app",
    task_id="abc123-def456"  # CRITICAL: Get this from TASKS.md
)

delegate_task(
    specialist="ux-designer",
    task="Create UI mockups, design system, and component library based on REQUIREMENTS.md",
    project_name="my-web-app",
    task_id="xyz789-abc123"  # CRITICAL: Get this from TASKS.md
)

delegate_task(
    specialist="qa-testing",
    task="Create comprehensive test suite covering unit, integration, and E2E tests per ROADMAP.md",
    project_name="my-web-app",
    task_id="def456-xyz789"  # CRITICAL: Get this from TASKS.md
)
```

## Best Practices

- **Delegate First**: ALWAYS consider delegation before doing work yourself
- **Use Specialists**: Leverage the 19 specialist agents - they're experts in their domains
- **Be Thorough**: Don't skip planning for complex tasks - use `create_planning_docs`
- **Be Efficient**: Don't over-plan simple tasks - use TodoWrite for quick tracking
- **Be Clear**: Provide specific, actionable instructions to specialists
- **Be Organized**: Use the dual-structure (planning in .proto/ vs code in project root)
- **CRITICAL**: After creating planning docs, ALWAYS delegate implementation work - planning is NOT completion!
- **Be Adaptive**: Adjust approach based on task complexity

**Remember: You are the ORCHESTRATOR, not the implementer.**
Your job is to:
1. Analyze what needs to be done
2. Create planning documents if needed
3. Delegate to the right specialists
4. Coordinate between specialists
5. Synthesize results into final deliverable

Specialists are REALLY GOOD at their tasks. Trust them and delegate appropriately."""

    async def execute_with_planning(
        self, task: str, context: dict[str, Any] | None = None
    ) -> AgentResult:
        """
        Execute task with intelligent planning.

        This is the main entry point that includes complexity analysis
        and planning document generation.

        Args:
            task: The user's task
            context: Optional context

        Returns:
            AgentResult with execution outcome
        """
        context = context or {}

        # Step 0: Smart knowledge retrieval - learn from past similar tasks
        relevant_knowledge = await self._retrieve_relevant_knowledge(task)
        if relevant_knowledge:
            context['relevant_knowledge'] = relevant_knowledge

        # Step 1: Analyze task complexity
        analysis = self.complexity_analyzer.analyze(task, context)

        # Log planning analysis
        self.logger.log_event(
            event_type="planning_started",
            session_id=self.session_id,
            data={
                "task": task,
                "complexity": analysis.complexity,
                "planning_required": analysis.planning_required,
                "estimated_steps": analysis.estimated_steps,
                "required_specialists": analysis.required_specialists,
            },
        )

        # Step 2: Create planning documents if needed
        if analysis.planning_required:
            planning_context = await self._generate_planning_docs(task, analysis, context)
            context.update(planning_context)

            # Log planning completion
            self.logger.log_event(
                event_type="planning_completed",
                session_id=self.session_id,
                data={
                    "documents_created": list(planning_context.get("documents", {}).keys()),
                    "project_path": planning_context.get("project_path"),
                },
            )

        # Step 3: Execute task (with or without delegation)
        # Enhance task with planning context
        enhanced_task = self._enhance_task_with_planning(task, analysis, context)

        # Execute using base agent
        result = await self.execute(enhanced_task, context)

        return result

    async def _generate_planning_docs(
        self, task: str, analysis: Any, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate planning documents based on complexity analysis.

        Args:
            task: The user's task
            analysis: TaskAnalysis result
            context: Execution context

        Returns:
            Planning context with documents and project info
        """
        from ..planning import PlanningDocuments

        # Determine project name from task
        project_name = self._extract_project_name(task)

        # Check if project already exists
        if self.project_manager.project_exists(project_name):
            # Load existing project context
            self.logger.log_event(
                event_type="debug_info",
                session_id=self.session_id,
                data={"message": f"Using existing project: {project_name}"},
            )
            return self.project_manager.get_project_context(project_name)

        # Create new project
        project_path = self.project_manager.create_project(project_name)

        planning_context = {
            "project_name": project_name,
            "project_path": str(project_path),
            "documents": {},
        }

        # Generate documents based on planning strategy
        strategy = analysis.planning_strategy

        # Note: In a full implementation, you would call the LLM to generate
        # each document using the prompts from PlanningDocuments.
        # For now, we'll create placeholder documents.

        if strategy.get("project_overview"):
            doc_content = f"# {project_name}\n\n## Task\n{task}\n\n## Analysis\n{analysis.reasoning}"
            self.project_manager.save_document(project_name, "project_overview", doc_content)
            planning_context["documents"]["project_overview"] = doc_content

        if strategy.get("requirements"):
            doc_content = f"# Requirements\n\n## Task\n{task}\n\n## Complexity\n{analysis.complexity}"
            self.project_manager.save_document(project_name, "requirements", doc_content)
            planning_context["documents"]["requirements"] = doc_content

        # TODO: Generate other documents (technical_spec, roadmap, etc.) using LLM

        return planning_context

    def _extract_project_name(self, task: str) -> str:
        """
        Extract a project name from the task description.

        Args:
            task: The user's task

        Returns:
            Project name (slugified)
        """
        # Simple extraction - take first few words
        words = task.split()[:5]
        name = " ".join(words)

        # Remove common words
        common_words = ["create", "build", "make", "develop", "implement", "a", "an", "the"]
        name_words = [w for w in name.split() if w.lower() not in common_words]

        if not name_words:
            return "project"

        return " ".join(name_words)

    def _enhance_task_with_planning(
        self, task: str, analysis: Any, context: dict[str, Any]
    ) -> str:
        """
        Enhance task description with planning context.

        Args:
            task: Original task
            analysis: TaskAnalysis
            context: Planning context

        Returns:
            Enhanced task description
        """
        enhanced = task

        if analysis.planning_required and context.get("documents"):
            enhanced += "\n\n## Planning Context\n"
            enhanced += f"Complexity: {analysis.complexity}\n"
            enhanced += f"Estimated steps: {analysis.estimated_steps}\n"

            if analysis.required_specialists:
                enhanced += f"Required expertise: {', '.join(analysis.required_specialists)}\n"

            enhanced += "\nPlanning documents have been created. Use them to guide your work.\n"

        return enhanced

    async def delegate_to_specialist(
        self, specialist_role: str, task: str, context: dict[str, Any] | None = None
    ) -> AgentResult:
        """
        Delegate task to a specialist agent.

        Args:
            specialist_role: Role of specialist (marketing, development, etc.)
            task: Task for the specialist
            context: Context to pass to specialist

        Returns:
            AgentResult from specialist
        """
        # Log delegation
        self.logger.log_event(
            event_type="agent_delegated",
            session_id=self.session_id,
            data={
                "from_agent": "ceo",
                "to_agent": specialist_role,
                "task": task,
            },
        )

        # TODO: Implement specialist agent loading and execution
        # For now, return placeholder
        return AgentResult(
            success=True,
            output=f"Specialist '{specialist_role}' would handle: {task}",
            agent_role="ceo",
            iterations=1,
            delegations=[{"to": specialist_role, "task": task}],
        )

    async def _retrieve_relevant_knowledge(self, task: str) -> list[dict[str, Any]]:
        """
        Search across all projects for relevant past knowledge.

        This enables the system to learn from previous similar tasks,
        avoiding past mistakes and applying proven patterns.

        Args:
            task: Current task description

        Returns:
            List of relevant knowledge entries from all projects
        """
        from ..planning.knowledge_store import KnowledgeStore

        try:
            # Extract keywords from task
            keywords = self._extract_keywords(task)

            if not keywords:
                return []

            # Get all projects
            all_projects = self.project_manager.list_projects()

            relevant_knowledge = []
            seen_titles = set()  # Avoid duplicates

            # Search across all projects
            for project in all_projects[:10]:  # Limit to 10 most recent projects
                try:
                    knowledge_store = self.project_manager.get_knowledge_store(project['slug'])
                    if not knowledge_store:
                        continue

                    # Search for each keyword
                    for keyword in keywords[:5]:  # Top 5 keywords
                        entries = knowledge_store.search_entries(keyword)

                        # Add top 2 results per keyword
                        for entry in entries[:2]:
                            if entry.title not in seen_titles:
                                seen_titles.add(entry.title)
                                relevant_knowledge.append({
                                    "title": entry.title,
                                    "type": entry.type.value,
                                    "content": entry.content[:300] + "..." if len(entry.content) > 300 else entry.content,
                                    "tags": entry.tags,
                                    "source_project": project['project_name'],
                                    "relevance_score": entry.relevance_score,
                                })

                                # Limit total results
                                if len(relevant_knowledge) >= 10:
                                    break

                        if len(relevant_knowledge) >= 10:
                            break

                except Exception as e:
                    # Don't let one project's error break knowledge retrieval
                    self.logger.log_event(
                        event_type="knowledge_retrieval_error",
                        level="WARNING",
                        session_id=self.session_id,
                        data={"project": project.get('slug', 'unknown'), "error": str(e)},
                    )
                    continue

            # Log retrieval results
            if relevant_knowledge:
                self.logger.log_event(
                    event_type="knowledge_retrieved",
                    session_id=self.session_id,
                    data={
                        "task": task[:100],
                        "keywords": keywords,
                        "num_results": len(relevant_knowledge),
                        "projects_searched": len(all_projects[:10]),
                    },
                )

            return relevant_knowledge

        except Exception as e:
            self.logger.log_event(
                event_type="knowledge_retrieval_failed",
                level="WARNING",
                session_id=self.session_id,
                data={"error": str(e)},
            )
            return []

    def _extract_keywords(self, text: str) -> list[str]:
        """
        Extract meaningful keywords from text.

        Args:
            text: Text to extract keywords from

        Returns:
            List of keywords sorted by likely relevance
        """
        # Simple keyword extraction - remove common words
        common_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "should", "could", "may", "might", "can", "this", "that",
            "these", "those", "i", "you", "he", "she", "it", "we", "they",
            "my", "your", "his", "her", "its", "our", "their", "me", "him",
            "us", "them", "please", "need", "want", "make", "create", "build"
        }

        # Split and filter
        words = text.lower().split()
        keywords = []

        for word in words:
            # Remove punctuation
            word = ''.join(c for c in word if c.isalnum() or c == '-')

            # Keep if not common and long enough
            if word and len(word) >= 3 and word not in common_words:
                keywords.append(word)

        # Return unique keywords, preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords[:10]  # Top 10 keywords
