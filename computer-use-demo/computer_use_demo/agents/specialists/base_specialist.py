"""
Base Specialist Agent - foundation for all specialist agents.

All specialists inherit from this class and add domain-specific:
- System prompts
- Tools (optional)
- Behaviors
"""

from abc import abstractmethod
from typing import Any

from ..base_agent import AgentConfig, BaseAgent


class BaseSpecialist(BaseAgent):
    """
    Base class for specialist agents.

    Specialists inherit from BaseAgent and add:
    - Domain-specific system prompts
    - Specialized knowledge
    - Optional domain-specific tools
    """

    def __init__(
        self,
        role: str,
        name: str,
        session_id: str | None = None,
        tools: list[Any] | None = None,
        model: str = "claude-sonnet-4-5-20250929",
        api_key: str | None = None,
    ):
        """
        Initialize specialist agent.

        Args:
            role: Specialist role (marketing, development, etc.)
            name: Display name for the specialist
            session_id: Optional session ID
            tools: Optional list of tools
            model: Model to use
        """
        config = AgentConfig(
            role=role,  # type: ignore
            name=name,
            model=model,
            tools=tools or [],
            max_iterations=25,
        )
        super().__init__(config, session_id, api_key)

    @abstractmethod
    def get_domain_expertise(self) -> str:
        """
        Get description of this specialist's domain expertise.

        Must be implemented by subclasses.

        Returns:
            Description of expertise
        """
        pass

    def get_system_prompt(self) -> str:
        """
        Get specialist system prompt.

        Combines base specialist prompt with domain expertise.

        Returns:
            Complete system prompt
        """
        base_prompt = f"""You are a {self.config.name} - a specialist agent in the Proto AI multi-agent system.

Your role: {self.config.role}
Your expertise: {self.get_domain_expertise()}

## Your Responsibilities

As a specialist, you:
1. **Focus on your domain**: Apply deep expertise in your specific area
2. **Deliver quality**: Produce high-quality work that meets professional standards
3. **Collaborate**: Work with other specialists when needed
4. **Follow planning**: Use planning documents provided by the CEO agent
5. **Communicate clearly**: Explain your work and decisions

## Working with Other Agents

You may receive tasks from:
- **CEO Agent**: The main orchestrator who delegates high-level tasks
- **Other Specialists**: Colleagues who need your expertise

When receiving a task:
1. Review any planning documents provided
2. Understand the specific deliverables expected
3. Identify dependencies on other specialists
4. Execute your work using available tools
5. Deliver clear, complete results

## Available Tools

You have access to the same powerful tools as other agents:
- File operations (read, write, edit)
- Terminal commands
- Code search and navigation
- Git operations
- Computer control (if needed)

Use these tools to complete your work professionally and efficiently.

## Quality Standards

Your work should be:
- **Professional**: Industry-standard quality
- **Complete**: All requirements met
- **Documented**: Clear explanations and comments
- **Tested**: Verified to work correctly
- **Maintainable**: Easy for others to understand and modify

Remember: You are an expert in {self.config.role}. Apply your deep knowledge to deliver exceptional results."""

        return base_prompt
