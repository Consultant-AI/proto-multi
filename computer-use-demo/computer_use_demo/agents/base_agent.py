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
        Execute a task.

        Args:
            task: The task to execute
            context: Optional context (planning docs, project info, etc.)

        Returns:
            AgentResult with execution outcome
        """
        context = context or {}
        self.iteration_count = 0
        delegations = []

        # Log task start
        self.logger.log_event(
            event_type="message_sent",
            session_id=self.session_id,
            data={
                "task": task,
                "agent_role": self.config.role,
                "context_keys": list(context.keys()),
            },
        )

        # Add initial user message
        self.messages = [{"role": "user", "content": task}]

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
                    return AgentResult(
                        success=True,
                        output=final_output,
                        agent_role=self.config.role,
                        iterations=self.iteration_count,
                        messages=self.messages,
                        delegations=delegations,
                    )

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
            return AgentResult(
                success=False,
                output="",
                agent_role=self.config.role,
                iterations=self.iteration_count,
                messages=self.messages,
                error=str(e),
            )

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

        # Call API
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=4096,
            temperature=self.config.temperature,
            system=system_prompt,
            messages=self.messages,
            tools=tools if tools else None,
        )

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
