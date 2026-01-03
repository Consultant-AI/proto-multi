"""
Agent Creator.

Creates new specialist agents from specifications.
"""

import json
from pathlib import Path
from typing import Any

from .types import AgentSpec, Modification, ModificationType, ModificationStatus


class AgentCreator:
    """
    Creates new specialist agents.

    Generates agent code from specifications including:
    - System prompt
    - Tool configuration
    - Skill loading
    - Delegation rules
    """

    def __init__(self, agents_dir: Path | None = None):
        self._agents_dir = agents_dir or Path.cwd() / "computer_use_demo" / "agents"
        self._agents_dir.mkdir(parents=True, exist_ok=True)

        self._templates_dir = self._agents_dir / "templates"

    def create_agent_spec(
        self,
        name: str,
        description: str,
        capabilities: list[str],
        tools: list[str] | None = None,
        skills: list[str] | None = None,
        model: str = "claude-sonnet-4-20250514",
    ) -> AgentSpec:
        """Create an agent specification."""
        # Generate system prompt
        system_prompt = self._generate_system_prompt(name, description, capabilities)

        return AgentSpec(
            name=name,
            display_name=name.replace("-", " ").title(),
            description=description,
            capabilities=capabilities,
            system_prompt=system_prompt,
            tools=tools or ["edit", "read", "glob", "grep", "bash"],
            skills=skills or [],
            model=model,
        )

    def _generate_system_prompt(
        self,
        name: str,
        description: str,
        capabilities: list[str],
    ) -> str:
        """Generate a system prompt for the agent."""
        caps_text = "\n".join(f"- {cap}" for cap in capabilities)

        return f'''You are a specialist agent named "{name}".

{description}

Your capabilities include:
{caps_text}

Guidelines:
- Focus on your area of expertise
- Ask for clarification when requirements are ambiguous
- Delegate tasks outside your expertise to appropriate specialists
- Provide clear, actionable outputs
- Document your reasoning and decisions
'''

    async def generate_agent_code(self, spec: AgentSpec) -> str:
        """Generate Python code for the agent."""
        code = f'''"""
{spec.display_name} Agent.

{spec.description}
"""

from typing import Any
from .base_agent import BaseAgent


class {self._to_class_name(spec.name)}(BaseAgent):
    """
    {spec.description}

    Capabilities:
    {chr(10).join(f"    - {cap}" for cap in spec.capabilities)}
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="{spec.name}",
            model="{spec.model}",
            **kwargs
        )
        self._tools = {spec.tools}
        self._skills = {spec.skills}

    @property
    def system_prompt(self) -> str:
        return """{spec.system_prompt}"""

    @property
    def capabilities(self) -> list[str]:
        return {spec.capabilities}

    async def can_handle(self, task_description: str) -> float:
        """
        Determine if this agent can handle a task.

        Returns confidence score 0-1.
        """
        keywords = {spec.capabilities}
        task_lower = task_description.lower()

        matches = sum(1 for kw in keywords if kw.lower() in task_lower)
        return min(matches / max(len(keywords), 1), 1.0)
'''
        return code

    def _to_class_name(self, name: str) -> str:
        """Convert agent name to class name."""
        return "".join(word.title() for word in name.replace("-", "_").split("_")) + "Agent"

    async def create_agent(
        self,
        spec: AgentSpec,
        dry_run: bool = False,
    ) -> Modification:
        """
        Create a new agent from specification.

        Args:
            spec: Agent specification
            dry_run: If True, don't actually create the file

        Returns:
            Modification record
        """
        code = await self.generate_agent_code(spec)
        filename = f"{spec.name.replace('-', '_')}.py"
        target_path = self._agents_dir / filename

        modification = Modification(
            type=ModificationType.AGENT_CREATE,
            target=str(target_path),
            description=f"Create agent: {spec.display_name}",
            changes={
                "type": "create",
                "content": code,
                "spec": {
                    "name": spec.name,
                    "capabilities": spec.capabilities,
                    "tools": spec.tools,
                },
            },
            reason=f"Create new specialist agent: {spec.description}",
            source="agent_creator",
        )

        if not dry_run:
            target_path.write_text(code)
            modification.status = ModificationStatus.APPLIED

            # Also save spec
            spec_path = self._agents_dir / "specs" / f"{spec.name}.json"
            spec_path.parent.mkdir(exist_ok=True)
            with open(spec_path, "w") as f:
                json.dump({
                    "name": spec.name,
                    "display_name": spec.display_name,
                    "description": spec.description,
                    "capabilities": spec.capabilities,
                    "tools": spec.tools,
                    "skills": spec.skills,
                    "model": spec.model,
                }, f, indent=2)

            print(f"[AgentCreator] Created agent: {spec.name}")

        return modification

    def list_agents(self) -> list[dict[str, Any]]:
        """List existing agent specifications."""
        specs = []
        specs_dir = self._agents_dir / "specs"

        if specs_dir.exists():
            for spec_file in specs_dir.glob("*.json"):
                try:
                    with open(spec_file, "r") as f:
                        specs.append(json.load(f))
                except Exception:
                    pass

        return specs
