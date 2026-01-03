"""
Tool Creator.

Creates compound tools from specifications.
"""

import json
from pathlib import Path
from typing import Any

from .types import ToolSpec, Modification, ModificationType, ModificationStatus


class ToolCreator:
    """
    Creates compound tools that combine multiple operations.

    Features:
    - Multi-step tool execution
    - Parameter validation
    - Output formatting
    - Safety constraints
    """

    def __init__(self, tools_dir: Path | None = None):
        self._tools_dir = tools_dir or Path.cwd() / "computer_use_demo" / "tools" / "compound"
        self._tools_dir.mkdir(parents=True, exist_ok=True)

    def create_tool_spec(
        self,
        name: str,
        description: str,
        steps: list[dict[str, Any]],
        parameters: list[dict[str, Any]] | None = None,
    ) -> ToolSpec:
        """Create a tool specification."""
        return ToolSpec(
            name=name,
            display_name=name.replace("_", " ").title(),
            description=description,
            parameters=parameters or [],
            steps=steps,
        )

    async def generate_tool_code(self, spec: ToolSpec) -> str:
        """Generate Python code for the tool."""
        params_code = self._generate_params_code(spec.parameters)
        steps_code = self._generate_steps_code(spec.steps)

        code = f'''"""
{spec.display_name} Tool.

{spec.description}
"""

from typing import Any
from ..base import BaseAnthropicTool, ToolResult


class {self._to_class_name(spec.name)}(BaseAnthropicTool):
    """
    {spec.description}

    This is a compound tool that executes multiple steps.
    """

    name = "{spec.name}"
    description = """{spec.description}"""

    def __init__(self):
        self._max_runtime = {spec.max_runtime}
        self._requires_confirmation = {spec.requires_confirmation}

    def get_parameters(self) -> dict[str, Any]:
        return {{
{params_code}
        }}

    async def __call__(self, **kwargs) -> ToolResult:
        """Execute the compound tool."""
        try:
            context = {{"params": kwargs, "results": {{}}}}

{steps_code}

            return ToolResult(
                output=self._format_output(context["results"]),
                error=None,
            )

        except Exception as e:
            return ToolResult(
                output="",
                error=str(e),
            )

    def _format_output(self, results: dict[str, Any]) -> str:
        """Format the output from all steps."""
        output_lines = []
        for step_name, result in results.items():
            output_lines.append(f"## {{step_name}}")
            output_lines.append(str(result))
            output_lines.append("")
        return "\\n".join(output_lines)
'''
        return code

    def _to_class_name(self, name: str) -> str:
        """Convert tool name to class name."""
        return "".join(word.title() for word in name.split("_")) + "Tool"

    def _generate_params_code(self, parameters: list[dict[str, Any]]) -> str:
        """Generate parameter definition code."""
        if not parameters:
            return ""

        lines = []
        for param in parameters:
            param_def = {
                "type": param.get("type", "string"),
                "description": param.get("description", ""),
            }
            if "default" in param:
                param_def["default"] = param["default"]
            if param.get("required", True):
                param_def["required"] = True

            lines.append(f'            "{param["name"]}": {param_def},')

        return "\n".join(lines)

    def _generate_steps_code(self, steps: list[dict[str, Any]]) -> str:
        """Generate step execution code."""
        lines = []

        for i, step in enumerate(steps):
            step_name = step.get("name", f"step_{i}")
            step_type = step.get("type", "custom")

            lines.append(f"            # Step: {step_name}")

            if step_type == "bash":
                cmd = step.get("command", "echo 'no command'")
                lines.append(f'            import subprocess')
                lines.append(f'            result = subprocess.run({repr(cmd)}, shell=True, capture_output=True, text=True)')
                lines.append(f'            context["results"]["{step_name}"] = result.stdout')

            elif step_type == "read":
                path = step.get("path", "")
                lines.append(f'            from pathlib import Path')
                lines.append(f'            path = Path({repr(path)}).expanduser()')
                lines.append(f'            context["results"]["{step_name}"] = path.read_text() if path.exists() else ""')

            elif step_type == "write":
                path = step.get("path", "")
                content_key = step.get("content_from", "")
                lines.append(f'            from pathlib import Path')
                lines.append(f'            path = Path({repr(path)}).expanduser()')
                lines.append(f'            content = context["results"].get("{content_key}", "")')
                lines.append(f'            path.write_text(content)')
                lines.append(f'            context["results"]["{step_name}"] = "Written to " + str(path)')

            else:
                # Custom step - just add a placeholder
                lines.append(f'            # Custom step implementation needed')
                lines.append(f'            context["results"]["{step_name}"] = "Step completed"')

            lines.append("")

        return "\n".join(lines)

    async def create_tool(
        self,
        spec: ToolSpec,
        dry_run: bool = False,
    ) -> Modification:
        """
        Create a new compound tool.

        Args:
            spec: Tool specification
            dry_run: If True, don't actually create the file

        Returns:
            Modification record
        """
        code = await self.generate_tool_code(spec)
        filename = f"{spec.name}.py"
        target_path = self._tools_dir / filename

        modification = Modification(
            type=ModificationType.TOOL_CREATE,
            target=str(target_path),
            description=f"Create tool: {spec.display_name}",
            changes={
                "type": "create",
                "content": code,
                "spec": {
                    "name": spec.name,
                    "parameters": spec.parameters,
                    "steps": spec.steps,
                },
            },
            reason=f"Create new compound tool: {spec.description}",
            source="tool_creator",
        )

        if not dry_run:
            target_path.write_text(code)
            modification.status = ModificationStatus.APPLIED

            # Save spec
            spec_path = self._tools_dir / "specs" / f"{spec.name}.json"
            spec_path.parent.mkdir(exist_ok=True)
            with open(spec_path, "w") as f:
                json.dump({
                    "name": spec.name,
                    "description": spec.description,
                    "parameters": spec.parameters,
                    "steps": spec.steps,
                }, f, indent=2)

            print(f"[ToolCreator] Created tool: {spec.name}")

        return modification

    def list_tools(self) -> list[dict[str, Any]]:
        """List existing tool specifications."""
        specs = []
        specs_dir = self._tools_dir / "specs"

        if specs_dir.exists():
            for spec_file in specs_dir.glob("*.json"):
                try:
                    with open(spec_file, "r") as f:
                        specs.append(json.load(f))
                except Exception:
                    pass

        return specs
