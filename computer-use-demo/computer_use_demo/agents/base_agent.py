"""
Base Agent class for Proto multi-agent system.

Provides core agent functionality that all agents (CEO and specialists) inherit from.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal

from anthropic import Anthropic
from anthropic.types import Message, TextBlock

from ..logging import get_logger
from ..tools.collection import ToolCollection

AgentRole = Literal["ceo", "marketing", "development", "design", "analytics", "content", "research"]


@dataclass
class AgentConfig:
    """Configuration for an agent."""

    role: AgentRole
    name: str
    model: str = "claude-sonnet-4-5-20250929"
    system_prompt: str = ""
    tools: list[Any] = field(default_factory=list)
    max_iterations: int = 25
    temperature: float = 1.0
    max_self_correction_attempts: int = 3  # Max retry attempts with self-correction


@dataclass
class AgentMessage:
    """Message for inter-agent communication."""

    from_agent: str  # Agent role that sent this
    to_agent: str  # Agent role that should receive this
    message_type: Literal["task_delegation", "result", "question", "notification"]
    content: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from agent execution."""

    success: bool
    output: str
    agent_role: AgentRole
    iterations: int
    messages: list[dict[str, Any]] = field(default_factory=list)
    delegations: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


class BaseAgent(ABC):
    """
    Base class for all Proto agents.

    Provides:
    - Tool execution capabilities
    - Message handling with Anthropic API
    - Logging integration
    - Session management
    - Inter-agent communication protocol
    """

    def __init__(self, config: AgentConfig, session_id: str | None = None):
        """
        Initialize base agent.

        Args:
            config: Agent configuration
            session_id: Optional session ID for logging
        """
        self.config = config
        self.session_id = session_id or f"{config.role}-agent"
        self.client = Anthropic()
        self.logger = get_logger()
        self.messages: list[dict[str, Any]] = []
        self.iteration_count = 0

        # Log agent creation
        self.logger.log_event(
            event_type="session_created",
            session_id=self.session_id,
            data={
                "agent_role": config.role,
                "agent_name": config.name,
                "model": config.model,
            },
        )

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        Must be implemented by subclasses to define agent behavior.

        Returns:
            System prompt string
        """
        pass

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> AgentResult:
        """
        Execute a task with self-healing retry loop.

        If the task fails, the agent will:
        1. Analyze the failure
        2. Retrieve relevant knowledge from past similar failures
        3. Inject learnings into context
        4. Retry the task
        5. Repeat until success or max_self_correction_attempts reached
        6. If still failing, queue improvement task for later

        Args:
            task: The task to execute
            context: Optional context (planning docs, project info, etc.)

        Returns:
            AgentResult with execution outcome
        """
        context = context or {}

        # Self-healing retry loop
        for retry_attempt in range(self.config.max_self_correction_attempts):
            # Execute task attempt
            result = await self._execute_attempt(task, context)

            # If successful, return immediately
            if result.success:
                # Capture successful recovery pattern if this was a retry
                if retry_attempt > 0:
                    await self._capture_recovery_pattern(task, result, retry_attempt, context)
                return result

            # Task failed - check if we should retry
            if retry_attempt < self.config.max_self_correction_attempts - 1:
                # Not the last attempt - try to fix and retry
                self.logger.log_event(
                    event_type="self_correction_attempt",
                    session_id=self.session_id,
                    data={
                        "task": task[:100],
                        "attempt": retry_attempt + 1,
                        "error": result.error,
                    },
                )

                # Analyze failure and retrieve learnings
                fix_context = await self._analyze_and_learn_from_failure(
                    task, result, context
                )

                # Inject learnings into context for next attempt
                context.update(fix_context)

                # Add retry guidance to the task description
                retry_guidance = fix_context.get("retry_guidance", "")
                if retry_guidance:
                    # Prepend guidance to task for next attempt
                    enhanced_task = f"{retry_guidance}\n\n---\n\n{task}"
                    context["_enhanced_task_for_retry"] = enhanced_task

                # Reset for next attempt
                self.messages = []
                self.iteration_count = 0

            else:
                # Last attempt failed - queue for later if too hard
                self.logger.log_event(
                    event_type="self_correction_exhausted",
                    session_id=self.session_id,
                    data={
                        "task": task[:100],
                        "total_attempts": self.config.max_self_correction_attempts,
                        "final_error": result.error,
                    },
                )

                # Queue improvement task for later (existing behavior)
                await self._queue_improvement_task(task, result, context)

                return result

        # Should never reach here, but return last result as fallback
        return result

    async def _execute_attempt(self, task: str, context: dict[str, Any]) -> AgentResult:
        """
        Execute a single task attempt (original execute logic).

        Args:
            task: The task to execute
            context: Optional context (planning docs, project info, etc.)

        Returns:
            AgentResult with execution outcome
        """
        self.iteration_count = 0
        delegations = []
        task_start_time = None

        # Use enhanced task if this is a retry with guidance
        actual_task = context.get("_enhanced_task_for_retry", task)

        # Log task start
        self.logger.log_event(
            event_type="message_sent",
            session_id=self.session_id,
            data={
                "task": task[:100],  # Log original task
                "agent_role": self.config.role,
                "context_keys": list(context.keys()),
                "is_retry": "_enhanced_task_for_retry" in context,
            },
        )

        # Add initial user message (with retry guidance if applicable)
        self.messages = [{"role": "user", "content": actual_task}]

        # Track task start time for auto-knowledge capture
        from datetime import datetime
        task_start_time = datetime.utcnow()

        try:
            # Execution loop
            while self.iteration_count < self.config.max_iterations:
                self.iteration_count += 1

                # Call Anthropic API
                response = await self._call_api()

                # Process response
                stop_reason = response.stop_reason

                if stop_reason == "end_turn":
                    # Agent finished
                    final_output = self._extract_text(response)
                    result = AgentResult(
                        success=True,
                        output=final_output,
                        agent_role=self.config.role,
                        iterations=self.iteration_count,
                        messages=self.messages,
                        delegations=delegations,
                    )

                    # Auto-capture knowledge from successful execution
                    await self._auto_capture_knowledge(task, result, context, task_start_time)

                    return result

                elif stop_reason == "tool_use":
                    # Process tool use
                    tool_results = await self._process_tools(response)

                    # Add assistant message and tool results to conversation
                    self.messages.append(
                        {"role": "assistant", "content": response.content}
                    )
                    self.messages.append(
                        {"role": "user", "content": tool_results}
                    )

                elif stop_reason == "max_tokens":
                    # Hit token limit, continue
                    self.messages.append(
                        {"role": "assistant", "content": response.content}
                    )
                    self.messages.append(
                        {"role": "user", "content": "Please continue."}
                    )

                else:
                    # Unexpected stop reason
                    return AgentResult(
                        success=False,
                        output=self._extract_text(response),
                        agent_role=self.config.role,
                        iterations=self.iteration_count,
                        messages=self.messages,
                        error=f"Unexpected stop reason: {stop_reason}",
                    )

            # Max iterations reached
            return AgentResult(
                success=False,
                output=self._extract_text(self.messages[-1]["content"]) if self.messages else "",
                agent_role=self.config.role,
                iterations=self.iteration_count,
                messages=self.messages,
                error=f"Max iterations ({self.config.max_iterations}) reached",
            )

        except Exception as e:
            self.logger.log_error(self.session_id, e)
            result = AgentResult(
                success=False,
                output="",
                agent_role=self.config.role,
                iterations=self.iteration_count,
                messages=self.messages,
                error=str(e),
            )

            # Auto-capture knowledge from failures
            await self._auto_capture_knowledge(task, result, context, task_start_time)

            return result

    async def _call_api(self) -> Message:
        """
        Call Anthropic API with current messages.

        Returns:
            API response message
        """
        system_prompt = self.get_system_prompt()

        # Prepare tools if any
        tools = [tool.to_params() for tool in self.config.tools] if self.config.tools else []

        # Log API request
        self.logger.log_event(
            event_type="api_request",
            session_id=self.session_id,
            data={
                "agent_role": self.config.role,
                "iteration": self.iteration_count,
                "message_count": len(self.messages),
                "has_tools": len(tools) > 0,
            },
        )

        # Call API - only include tools if non-empty
        api_params = {
            "model": self.config.model,
            "max_tokens": 4096,
            "temperature": self.config.temperature,
            "system": system_prompt,
            "messages": self.messages,
        }

        if tools:  # Only add tools parameter if there are actual tools
            api_params["tools"] = tools

        response = self.client.messages.create(**api_params)

        # Log API response
        self.logger.log_event(
            event_type="api_response",
            session_id=self.session_id,
            data={
                "agent_role": self.config.role,
                "stop_reason": response.stop_reason,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            },
        )

        return response

    async def _process_tools(self, response: Message) -> list[dict[str, Any]]:
        """
        Process tool use blocks in the response.

        Args:
            response: API response with tool use

        Returns:
            List of tool result blocks
        """
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input
                tool_id = block.id

                # Log tool execution start
                self.logger.log_event(
                    event_type="tool_selected",
                    session_id=self.session_id,
                    data={
                        "agent_role": self.config.role,
                        "tool_name": tool_name,
                        "tool_id": tool_id,
                    },
                )

                # Find and execute tool
                tool_result = await self._execute_tool(tool_name, tool_input, tool_id)
                tool_results.append(tool_result)

        return tool_results

    async def _execute_tool(
        self, tool_name: str, tool_input: dict[str, Any], tool_id: str
    ) -> dict[str, Any]:
        """
        Execute a specific tool.

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters
            tool_id: Unique tool call ID

        Returns:
            Tool result block
        """
        try:
            # Find tool in config
            tool = next((t for t in self.config.tools if t.name == tool_name), None)

            if not tool:
                return {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": f"Error: Tool '{tool_name}' not found",
                    "is_error": True,
                }

            # Execute tool
            result = await tool(**tool_input)

            # Log successful execution
            self.logger.log_event(
                event_type="tool_executed",
                session_id=self.session_id,
                data={
                    "agent_role": self.config.role,
                    "tool_name": tool_name,
                    "tool_id": tool_id,
                    "success": not getattr(result, "error", None),
                },
            )

            # Format result
            if hasattr(result, "error") and result.error:
                return {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": result.error,
                    "is_error": True,
                }

            return {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": result.output if hasattr(result, "output") else str(result),
            }

        except Exception as e:
            # Log tool failure
            self.logger.log_event(
                event_type="tool_failed",
                level="ERROR",
                session_id=self.session_id,
                data={
                    "agent_role": self.config.role,
                    "tool_name": tool_name,
                    "tool_id": tool_id,
                },
                error=e,
            )

            return {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": f"Error executing tool: {str(e)}",
                "is_error": True,
            }

    def _extract_text(self, content: Any) -> str:
        """
        Extract text from message content.

        Args:
            content: Message content (can be string, list of blocks, etc.)

        Returns:
            Extracted text
        """
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, TextBlock):
                    text_parts.append(block.text)
                elif isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            return "\n".join(text_parts)

        return str(content)

    async def _auto_capture_knowledge(
        self,
        task: str,
        result: AgentResult,
        context: dict[str, Any],
        task_start_time: Any,
    ) -> None:
        """
        Automatically capture knowledge from task execution.

        This method runs after every task completion (success or failure) to:
        - Extract learnings from successful approaches
        - Document patterns that worked
        - Capture lessons from failures
        - Record technical decisions made

        Args:
            task: The task that was executed
            result: The execution result
            context: Execution context (may contain project_name)
            task_start_time: When task started (datetime object)
        """
        try:
            # Only capture if we have a project context
            project_name = context.get("project_name") or context.get("metadata", {}).get("project_name")
            if not project_name:
                return  # Skip if no project context

            from datetime import datetime
            from ..planning import ProjectManager
            from ..planning.knowledge_store import KnowledgeType

            # Calculate task duration
            task_end_time = datetime.utcnow()
            duration_seconds = (task_end_time - task_start_time).total_seconds()

            # Initialize project manager and knowledge store
            project_manager = ProjectManager()
            knowledge_store = project_manager.get_knowledge_store(project_name)
            if not knowledge_store:
                return  # Project doesn't exist yet

            # Prepare task summary
            task_summary = task[:100] + "..." if len(task) > 100 else task

            if result.success:
                # CAPTURE SUCCESSFUL PATTERNS
                # Analyze what tools were used and how
                tools_used = self._extract_tools_used(result.messages)

                if tools_used:
                    # Capture successful tool usage pattern
                    knowledge_store.add_entry(
                        title=f"Successful approach: {task_summary}",
                        content=f"""Task: {task}

Agent: {self.config.name} ({self.config.role})
Duration: {duration_seconds:.1f}s
Iterations: {result.iterations}

Tools used successfully:
{chr(10).join(f'- {tool}' for tool in tools_used)}

Outcome: Task completed successfully
Output summary: {result.output[:200]}...""",
                        knowledge_type=KnowledgeType.PATTERN,
                        tags=[
                            self.config.role,
                            "success",
                            "auto-captured",
                            f"iterations-{result.iterations}",
                        ] + tools_used[:3],  # Add first 3 tools as tags
                        source=f"auto-capture-{self.config.role}",
                    )

                # If task was complex (many iterations), capture as learning
                if result.iterations >= 10:
                    knowledge_store.add_entry(
                        title=f"Complex task solved: {task_summary}",
                        content=f"""This task required {result.iterations} iterations to complete.

Complexity indicators:
- Multiple tool invocations
- Iterative refinement needed
- Agent: {self.config.name}

Key insight: Tasks of this nature benefit from breaking into smaller steps.

Original task: {task}""",
                        knowledge_type=KnowledgeType.LEARNING,
                        tags=[self.config.role, "complex-task", "multi-iteration", "auto-captured"],
                        source=f"auto-capture-{self.config.role}",
                    )

            else:
                # CAPTURE LESSONS FROM FAILURES
                error_msg = result.error or "Unknown error"

                knowledge_store.add_entry(
                    title=f"Lesson learned: {task_summary}",
                    content=f"""Task failed: {task}

Agent: {self.config.name} ({self.config.role})
Duration: {duration_seconds:.1f}s
Iterations: {result.iterations}

Error: {error_msg}

Context:
- Max iterations: {self.config.max_iterations}
- Tools available: {len(self.config.tools)}

Recommendation: Review task complexity and tool availability. Consider breaking into smaller subtasks or delegating to specialist agent.""",
                    knowledge_type=KnowledgeType.LESSON_LEARNED,
                    tags=[
                        self.config.role,
                        "failure",
                        "auto-captured",
                        "needs-review",
                    ],
                    source=f"auto-capture-{self.config.role}",
                )

            # Log knowledge capture
            self.logger.log_event(
                event_type="knowledge_auto_captured",
                session_id=self.session_id,
                data={
                    "agent_role": self.config.role,
                    "task_success": result.success,
                    "project_name": project_name,
                    "duration_seconds": duration_seconds,
                },
            )

            # Auto-generate improvement tasks based on learnings
            await self._auto_generate_improvement_tasks(
                task, result, context, project_name, duration_seconds
            )

        except Exception as e:
            # Don't let knowledge capture errors break task execution
            self.logger.log_event(
                event_type="knowledge_capture_failed",
                level="WARNING",
                session_id=self.session_id,
                data={"error": str(e)},
            )

    def _extract_tools_used(self, messages: list[dict[str, Any]]) -> list[str]:
        """
        Extract list of tools used during execution.

        Args:
            messages: Conversation messages

        Returns:
            List of unique tool names used
        """
        tools_used = set()

        for message in messages:
            if message.get("role") == "assistant":
                content = message.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_use":
                            tools_used.add(block.get("name", "unknown"))

        return sorted(list(tools_used))

    async def _auto_generate_improvement_tasks(
        self,
        task: str,
        result: AgentResult,
        context: dict[str, Any],
        project_name: str,
        duration_seconds: float,
    ) -> None:
        """
        Automatically generate improvement tasks based on task execution results.

        This creates actionable work items to improve the system when:
        - Tasks fail (create debugging/fix tasks)
        - Tasks are inefficient (create optimization tasks)
        - Patterns emerge that need systematic fixes

        Args:
            task: The task that was executed
            result: The execution result
            context: Execution context
            project_name: Name of the project
            duration_seconds: How long the task took
        """
        try:
            from ..daemon.work_queue import WorkPriority, WorkQueue

            # Initialize work queue
            work_queue = WorkQueue()

            # Prepare task summary for improvement tasks
            task_summary = task[:80] + "..." if len(task) > 80 else task

            # CASE 1: Task failed - create debugging task
            if not result.success:
                error_msg = result.error or "Unknown error"

                # Create improvement task to fix the issue
                work_queue.add_work(
                    description=f"Debug and fix error in '{task_summary}': {error_msg[:100]}",
                    priority=WorkPriority.MEDIUM,
                    project_name=project_name,
                    assigned_agent="senior-developer",
                    context={
                        "improvement_task": True,
                        "improvement_type": "bug_fix",
                        "original_task": task,
                        "error": error_msg,
                        "failed_iterations": result.iterations,
                    },
                )

                self.logger.log_event(
                    event_type="improvement_task_queued",
                    session_id=self.session_id,
                    data={
                        "reason": "task_failure",
                        "project_name": project_name,
                        "original_task": task_summary,
                    },
                )

            # CASE 2: Task took many iterations - create optimization task
            elif result.iterations >= 10:
                tools_used = self._extract_tools_used(result.messages)

                work_queue.add_work(
                    description=f"Optimize inefficient process: '{task_summary}' (took {result.iterations} iterations)",
                    priority=WorkPriority.MEDIUM,
                    project_name=project_name,
                    assigned_agent="senior-developer",
                    context={
                        "improvement_task": True,
                        "improvement_type": "optimization",
                        "original_task": task,
                        "iterations": result.iterations,
                        "duration_seconds": duration_seconds,
                        "tools_used": tools_used,
                    },
                )

                self.logger.log_event(
                    event_type="improvement_task_queued",
                    session_id=self.session_id,
                    data={
                        "reason": "inefficient_execution",
                        "project_name": project_name,
                        "iterations": result.iterations,
                        "original_task": task_summary,
                    },
                )

            # CASE 3: Check for recurring error patterns
            # (only if we have knowledge store access)
            from ..planning import ProjectManager

            project_manager = ProjectManager()
            knowledge_store = project_manager.get_knowledge_store(project_name)

            if knowledge_store and not result.success:
                # Check if this error has occurred multiple times
                error_msg = result.error or ""

                # Extract error category (first part before colon)
                error_category = error_msg.split(":")[0] if ":" in error_msg else error_msg[:50]

                # Search for similar failures
                similar_failures = knowledge_store.search_entries(error_category)
                lesson_learned_count = sum(
                    1 for entry in similar_failures
                    if entry.type.value == "lesson_learned"
                )

                # If we've seen this error 3+ times, create systematic fix task
                if lesson_learned_count >= 3:
                    work_queue.add_work(
                        description=f"Systematic fix for recurring error: {error_category[:80]}",
                        priority=WorkPriority.HIGH,  # Recurring errors are important
                        project_name=project_name,
                        assigned_agent="senior-developer",
                        context={
                            "improvement_task": True,
                            "improvement_type": "systematic_fix",
                            "error_category": error_category,
                            "occurrence_count": lesson_learned_count + 1,
                            "requires_root_cause_analysis": True,
                        },
                    )

                    self.logger.log_event(
                        event_type="improvement_task_queued",
                        session_id=self.session_id,
                        data={
                            "reason": "recurring_error",
                            "project_name": project_name,
                            "error_category": error_category,
                            "occurrence_count": lesson_learned_count + 1,
                        },
                    )

        except Exception as e:
            # Don't let improvement task generation errors break execution
            self.logger.log_event(
                event_type="improvement_task_generation_failed",
                level="WARNING",
                session_id=self.session_id,
                data={"error": str(e)},
            )

    async def _analyze_and_learn_from_failure(
        self,
        task: str,
        result: AgentResult,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze a task failure and retrieve relevant knowledge for retry.

        This method:
        1. Extracts error information
        2. Searches knowledge base for similar past failures
        3. Returns context with learnings to inject into retry attempt

        Args:
            task: The failed task
            result: The failure result
            context: Current task context

        Returns:
            Dict with learnings and suggestions for retry
        """
        try:
            from ..planning import ProjectManager

            # Extract project name from context
            project_name = context.get("project_name", "default")

            # Get knowledge store
            project_manager = ProjectManager()
            knowledge_store = project_manager.get_knowledge_store(project_name)

            if not knowledge_store:
                return {"retry_guidance": "No previous learnings available. Try a different approach."}

            # Extract error information
            error_msg = result.error or "Unknown error"
            error_category = error_msg.split(":")[0] if ":" in error_msg else error_msg[:50]

            # Search for similar failures and their solutions
            similar_failures = knowledge_store.search_entries(error_category)

            # Also search for successful patterns that might help
            task_keywords = self._extract_task_keywords(task)
            helpful_patterns = []
            for keyword in task_keywords[:3]:  # Top 3 keywords
                patterns = knowledge_store.search_entries(keyword)
                helpful_patterns.extend([
                    p for p in patterns
                    if p.type.value in ["pattern", "best_practice"]
                ])

            # Build retry guidance
            retry_context = {
                "retry_guidance": self._build_retry_guidance(
                    error_msg, similar_failures, helpful_patterns
                ),
                "similar_failures_count": len(similar_failures),
                "available_patterns_count": len(helpful_patterns),
            }

            self.logger.log_event(
                event_type="failure_analysis_completed",
                session_id=self.session_id,
                data={
                    "error_category": error_category,
                    "similar_failures": len(similar_failures),
                    "helpful_patterns": len(helpful_patterns),
                },
            )

            return retry_context

        except Exception as e:
            self.logger.log_event(
                event_type="failure_analysis_failed",
                level="WARNING",
                session_id=self.session_id,
                data={"error": str(e)},
            )
            return {"retry_guidance": "Analysis failed. Try a different approach."}

    def _build_retry_guidance(
        self,
        error_msg: str,
        similar_failures: list,
        helpful_patterns: list,
    ) -> str:
        """
        Build guidance message for retry attempt.

        Args:
            error_msg: The error message
            similar_failures: List of similar past failures
            helpful_patterns: List of helpful patterns

        Returns:
            Guidance string to inject into context
        """
        guidance_parts = [
            f"## Self-Correction Retry Guidance\n",
            f"\n**Previous Error**: {error_msg}\n",
        ]

        # Add learnings from similar failures
        if similar_failures:
            guidance_parts.append(f"\n**Past Similar Failures** ({len(similar_failures)} found):\n")
            for failure in similar_failures[:3]:  # Top 3
                guidance_parts.append(f"- {failure.title}: {failure.content[:200]}...\n")

        # Add helpful patterns
        if helpful_patterns:
            guidance_parts.append(f"\n**Helpful Patterns** ({len(helpful_patterns)} found):\n")
            for pattern in helpful_patterns[:3]:  # Top 3
                guidance_parts.append(f"- {pattern.title}: {pattern.content[:200]}...\n")

        guidance_parts.append(
            "\n**Retry Strategy**: Based on the above learnings, adjust your approach to avoid the same error.\n"
        )

        return "".join(guidance_parts)

    def _extract_task_keywords(self, task: str) -> list[str]:
        """
        Extract keywords from task description.

        Args:
            task: Task description

        Returns:
            List of keywords
        """
        # Simple keyword extraction - remove common words
        common_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "should", "could", "may", "might", "can", "this", "that",
            "please", "need", "want"
        }

        words = task.lower().split()
        keywords = [
            word for word in words
            if len(word) >= 3 and word not in common_words
        ]

        return keywords[:10]  # Top 10

    async def _capture_recovery_pattern(
        self,
        task: str,
        result: AgentResult,
        retry_attempt: int,
        context: dict[str, Any],
    ) -> None:
        """
        Capture successful recovery pattern for future use.

        When a task succeeds after failing on previous attempts,
        capture the recovery pattern as a best practice.

        Args:
            task: The task that eventually succeeded
            result: The successful result
            retry_attempt: Which retry attempt succeeded
            context: Task context
        """
        try:
            from ..planning import ProjectManager
            from ..planning.knowledge_store import KnowledgeEntry, KnowledgeType

            project_name = context.get("project_name", "default")
            project_manager = ProjectManager()
            knowledge_store = project_manager.get_knowledge_store(project_name)

            if not knowledge_store:
                return

            # Build recovery pattern content
            task_summary = task[:100] + "..." if len(task) > 100 else task
            recovery_content = f"""
**Task**: {task_summary}

**Initial Failure**: Failed on first attempt

**Recovery**: Succeeded on retry attempt {retry_attempt + 1}

**Key Success Factors**:
- Applied learnings from similar past failures
- Adjusted approach based on error analysis
- Persistence paid off - task was solvable with self-correction

**Lesson**: When encountering similar errors in the future, try the approaches that worked here.
"""

            # Store as best practice
            entry = KnowledgeEntry(
                title=f"Self-healing recovery: {task_summary}",
                content=recovery_content.strip(),
                type=KnowledgeType.BEST_PRACTICE,
                tags=["self-healing", "recovery", f"retry-{retry_attempt}"],
            )

            knowledge_store.add_entry(entry)

            self.logger.log_event(
                event_type="recovery_pattern_captured",
                session_id=self.session_id,
                data={
                    "task": task_summary,
                    "retry_attempt": retry_attempt,
                    "project_name": project_name,
                },
            )

        except Exception as e:
            self.logger.log_event(
                event_type="recovery_pattern_capture_failed",
                level="WARNING",
                session_id=self.session_id,
                data={"error": str(e)},
            )

    async def _queue_improvement_task(
        self,
        task: str,
        result: AgentResult,
        context: dict[str, Any],
    ) -> None:
        """
        Queue improvement task for later when self-correction is exhausted.

        This is called when all retry attempts fail and the task is "too hard for now."

        Args:
            task: The task that failed
            result: The failure result
            context: Task context
        """
        try:
            from ..daemon.work_queue import WorkPriority, WorkQueue

            project_name = context.get("project_name", "default")
            work_queue = WorkQueue()

            task_summary = task[:80] + "..." if len(task) > 80 else task
            error_msg = result.error or "Unknown error"

            # Queue with HIGH priority since it failed multiple retries
            work_queue.add_work(
                description=f"Fix hard failure (exhausted retries): '{task_summary}' - {error_msg[:100]}",
                priority=WorkPriority.HIGH,
                project_name=project_name,
                assigned_agent="senior-developer",
                context={
                    "improvement_task": True,
                    "improvement_type": "hard_failure",
                    "original_task": task,
                    "error": error_msg,
                    "retry_attempts_exhausted": self.config.max_self_correction_attempts,
                    "requires_deep_analysis": True,
                },
            )

            self.logger.log_event(
                event_type="improvement_task_queued",
                session_id=self.session_id,
                data={
                    "reason": "self_correction_exhausted",
                    "project_name": project_name,
                    "original_task": task_summary,
                    "retry_attempts": self.config.max_self_correction_attempts,
                },
            )

        except Exception as e:
            self.logger.log_event(
                event_type="improvement_task_queue_failed",
                level="WARNING",
                session_id=self.session_id,
                data={"error": str(e)},
            )
