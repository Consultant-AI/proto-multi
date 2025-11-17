"""
Subagent Coordinator - Parallel execution with isolated contexts.

Implements Agent SDK's subagent pattern for:
- Parallel task execution
- Specialized agent roles
- Isolated context windows
- Inter-agent communication
"""

import asyncio
from enum import Enum
from typing import Any, Callable
from dataclasses import dataclass

from anthropic.types.beta import BetaMessageParam


class SubagentType(Enum):
    """Types of specialized subagents"""
    EXECUTION = "execution"  # Handles computer control and bash commands
    VERIFICATION = "verification"  # Verifies actions via screenshots and checks
    FILE_OPERATIONS = "file_operations"  # File creation, editing, searching
    RESEARCH = "research"  # Web search and documentation browsing
    COORDINATION = "coordination"  # Coordinates other subagents


@dataclass
class SubagentTask:
    """A task for a subagent to execute"""
    task_id: str
    subagent_type: SubagentType
    prompt: str
    context: dict[str, Any] | None = None
    priority: int = 0


@dataclass
class SubagentResult:
    """Result from a subagent execution"""
    task_id: str
    success: bool
    output: Any
    error: str | None = None
    messages: list[BetaMessageParam] | None = None


class SubagentCoordinator:
    """
    Coordinates parallel subagent execution.

    Features:
    - Task queue management
    - Parallel execution with asyncio
    - Subagent-specific prompts and tools
    - Result aggregation
    - Error handling and recovery
    """

    def __init__(self, max_concurrent: int = 3):
        """
        Initialize subagent coordinator.

        Args:
            max_concurrent: Maximum number of concurrent subagents
        """
        self.max_concurrent = max_concurrent
        self.task_queue: asyncio.Queue[SubagentTask] = asyncio.Queue()
        self.results: dict[str, SubagentResult] = {}
        self.active_subagents: dict[str, asyncio.Task] = {}

        # Subagent configurations
        self.subagent_configs = self._load_subagent_configs()

    def _load_subagent_configs(self) -> dict[SubagentType, dict[str, Any]]:
        """Load configuration for each subagent type"""
        return {
            SubagentType.EXECUTION: {
                "system_prompt_suffix": """
                You are an execution specialist focused on:
                - GUI automation via computer tool
                - Command execution via bash tool
                - Application control and interaction
                - Taking actions requested by the main agent
                """,
                "tools": ["computer", "bash"],
                "max_iterations": 10,
            },
            SubagentType.VERIFICATION: {
                "system_prompt_suffix": """
                You are a verification specialist focused on:
                - Analyzing screenshots for success/failure indicators
                - Running validation commands
                - Checking file contents and system state
                - Providing structured verification results
                """,
                "tools": ["computer", "bash"],
                "max_iterations": 5,
            },
            SubagentType.FILE_OPERATIONS: {
                "system_prompt_suffix": """
                You are a file operations specialist focused on:
                - Creating and editing files with precision
                - Searching codebases for specific patterns
                - Reading and analyzing file contents
                - Managing file system operations
                """,
                "tools": ["str_replace_editor", "bash"],
                "max_iterations": 10,
            },
            SubagentType.RESEARCH: {
                "system_prompt_suffix": """
                You are a research specialist focused on:
                - Web browsing for documentation
                - Searching for solutions and examples
                - Gathering information from multiple sources
                - Synthesizing findings into actionable insights
                """,
                "tools": ["computer", "bash"],
                "max_iterations": 15,
            },
            SubagentType.COORDINATION: {
                "system_prompt_suffix": """
                You are a coordination specialist focused on:
                - Breaking down complex tasks into subtasks
                - Assigning work to appropriate subagents
                - Aggregating results from multiple agents
                - Managing dependencies between tasks
                """,
                "tools": ["bash"],
                "max_iterations": 20,
            },
        }

    async def submit_task(self, task: SubagentTask) -> str:
        """
        Submit a task to the subagent queue.

        Args:
            task: Task to execute

        Returns:
            Task ID for tracking
        """
        await self.task_queue.put(task)
        return task.task_id

    async def execute_task(
        self,
        task: SubagentTask,
        orchestrator_callback: Callable[[SubagentTask], Any],
    ) -> SubagentResult:
        """
        Execute a single task with appropriate subagent.

        Args:
            task: Task to execute
            orchestrator_callback: Callback to main orchestrator

        Returns:
            SubagentResult with execution outcome
        """
        try:
            # Get subagent config
            config = self.subagent_configs.get(task.subagent_type)
            if not config:
                return SubagentResult(
                    task_id=task.task_id,
                    success=False,
                    output=None,
                    error=f"Unknown subagent type: {task.subagent_type}",
                )

            # Build subagent messages
            messages: list[BetaMessageParam] = [
                {
                    "role": "user",
                    "content": task.prompt,
                }
            ]

            # Add context if provided
            if task.context:
                context_str = "\n".join(
                    f"{key}: {value}" for key, value in task.context.items()
                )
                messages[0]["content"] = f"<context>\n{context_str}\n</context>\n\n{task.prompt}"  # type: ignore

            # Execute via orchestrator callback
            # This will call the main orchestrator's loop with subagent-specific config
            result_messages = await orchestrator_callback(task)

            # Extract result from final assistant message
            output = self._extract_output_from_messages(result_messages)

            result = SubagentResult(
                task_id=task.task_id,
                success=True,
                output=output,
                messages=result_messages,
            )

        except Exception as e:
            result = SubagentResult(
                task_id=task.task_id,
                success=False,
                output=None,
                error=str(e),
            )

        # Store result
        self.results[task.task_id] = result
        return result

    async def execute_parallel(
        self,
        tasks: list[SubagentTask],
        orchestrator_callback: Callable[[SubagentTask], Any],
    ) -> dict[str, SubagentResult]:
        """
        Execute multiple tasks in parallel.

        Args:
            tasks: List of tasks to execute
            orchestrator_callback: Callback to main orchestrator

        Returns:
            Dictionary mapping task IDs to results
        """
        # Create coroutines for all tasks
        coros = [
            self.execute_task(task, orchestrator_callback)
            for task in tasks
        ]

        # Execute with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def bounded_task(coro):
            async with semaphore:
                return await coro

        # Run all tasks
        results = await asyncio.gather(
            *[bounded_task(coro) for coro in coros],
            return_exceptions=True,
        )

        # Build results dict
        results_dict = {}
        for task, result in zip(tasks, results):
            if isinstance(result, Exception):
                results_dict[task.task_id] = SubagentResult(
                    task_id=task.task_id,
                    success=False,
                    output=None,
                    error=str(result),
                )
            else:
                results_dict[task.task_id] = result

        return results_dict

    def get_result(self, task_id: str) -> SubagentResult | None:
        """
        Get result for a specific task.

        Args:
            task_id: ID of task to get result for

        Returns:
            SubagentResult if available, None otherwise
        """
        return self.results.get(task_id)

    def _extract_output_from_messages(
        self, messages: list[BetaMessageParam]
    ) -> str:
        """
        Extract final output from message history.

        Args:
            messages: Conversation messages

        Returns:
            Extracted output text
        """
        # Get last assistant message
        for message in reversed(messages):
            if message["role"] == "assistant":
                content = message["content"]
                if isinstance(content, str):
                    return content
                elif isinstance(content, list):
                    # Extract text blocks
                    texts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            texts.append(block.get("text", ""))
                    return "\n".join(texts)

        return ""

    async def coordinate_workflow(
        self,
        workflow_description: str,
        orchestrator_callback: Callable[[SubagentTask], Any],
    ) -> dict[str, SubagentResult]:
        """
        Coordinate a complex multi-agent workflow.

        Args:
            workflow_description: Description of the workflow to execute
            orchestrator_callback: Callback to main orchestrator

        Returns:
            Dictionary of all results
        """
        # First, use coordination agent to break down workflow
        coordination_task = SubagentTask(
            task_id="coordination",
            subagent_type=SubagentType.COORDINATION,
            prompt=f"""
            Break down this workflow into specific tasks for specialized subagents:
            {workflow_description}

            Available subagent types:
            - EXECUTION: GUI automation, running commands
            - VERIFICATION: Checking results, validating state
            - FILE_OPERATIONS: Creating/editing files
            - RESEARCH: Web browsing, documentation lookup

            Respond with a structured task breakdown.
            """,
        )

        # Execute coordination
        coordination_result = await self.execute_task(
            coordination_task, orchestrator_callback
        )

        # TODO: Parse coordination result and create subtasks
        # For now, return just the coordination result
        return {"coordination": coordination_result}

    def get_stats(self) -> dict[str, Any]:
        """
        Get coordinator statistics.

        Returns:
            Dictionary with coordinator stats
        """
        return {
            "max_concurrent": self.max_concurrent,
            "total_tasks": len(self.results),
            "successful_tasks": sum(1 for r in self.results.values() if r.success),
            "failed_tasks": sum(1 for r in self.results.values() if not r.success),
            "active_subagents": len(self.active_subagents),
        }
