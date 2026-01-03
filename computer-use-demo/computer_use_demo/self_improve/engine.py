"""
Self-Improvement Engine.

Central coordinator for all self-improvement capabilities.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .types import (
    Modification,
    ModificationStatus,
    AgentSpec,
    ToolSpec,
    SkillSpec,
    ImprovementSuggestion,
)
from .code_modifier import CodeModifier
from .agent_creator import AgentCreator
from .tool_creator import ToolCreator
from .skill_generator import SkillGenerator


class SelfImprovementEngine:
    """
    Central engine for self-improvement capabilities.

    Coordinates:
    - Code modifications
    - Agent creation
    - Tool creation
    - Skill generation
    - Improvement suggestions

    Safety:
    - Rate limiting
    - Approval workflows
    - Rollback capabilities
    - Audit logging
    """

    def __init__(
        self,
        data_dir: Path | None = None,
        max_daily_modifications: int = 10,
    ):
        self._data_dir = data_dir or Path.home() / ".proto" / "self-improvement"
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._max_daily_modifications = max_daily_modifications

        # Components
        self._code_modifier = CodeModifier(
            max_daily_modifications=max_daily_modifications
        )
        self._agent_creator = AgentCreator()
        self._tool_creator = ToolCreator()
        self._skill_generator = SkillGenerator()

        # Tracking
        self._modifications: list[Modification] = []
        self._suggestions: list[ImprovementSuggestion] = []

        # Load history
        self._load_history()

    def _load_history(self) -> None:
        """Load modification history."""
        history_file = self._data_dir / "history.json"
        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    data = json.load(f)
                # Load suggestions
                for sugg in data.get("suggestions", []):
                    self._suggestions.append(ImprovementSuggestion(
                        id=sugg["id"],
                        title=sugg["title"],
                        description=sugg.get("description", ""),
                        priority=sugg.get("priority", "medium"),
                    ))
            except Exception:
                pass

    def _save_history(self) -> None:
        """Save modification history."""
        history_file = self._data_dir / "history.json"
        data = {
            "modifications": [
                {
                    "id": m.id,
                    "type": m.type.value,
                    "target": m.target,
                    "status": m.status.value,
                    "created_at": m.created_at.isoformat(),
                }
                for m in self._modifications
            ],
            "suggestions": [
                {
                    "id": s.id,
                    "title": s.title,
                    "description": s.description,
                    "priority": s.priority,
                }
                for s in self._suggestions
            ],
        }
        with open(history_file, "w") as f:
            json.dump(data, f, indent=2)

    # Agent operations

    async def create_agent(
        self,
        name: str,
        description: str,
        capabilities: list[str],
        tools: list[str] | None = None,
        skills: list[str] | None = None,
        model: str = "claude-sonnet-4-20250514",
        dry_run: bool = False,
    ) -> Modification:
        """
        Create a new specialist agent.

        Args:
            name: Agent name (kebab-case)
            description: What the agent does
            capabilities: List of capabilities
            tools: Tools the agent can use
            skills: Skills to load
            model: Model to use
            dry_run: Preview without creating

        Returns:
            Modification record
        """
        spec = self._agent_creator.create_agent_spec(
            name=name,
            description=description,
            capabilities=capabilities,
            tools=tools,
            skills=skills,
            model=model,
        )

        modification = await self._agent_creator.create_agent(spec, dry_run=dry_run)
        self._modifications.append(modification)
        self._save_history()

        return modification

    # Tool operations

    async def create_tool(
        self,
        name: str,
        description: str,
        steps: list[dict[str, Any]],
        parameters: list[dict[str, Any]] | None = None,
        dry_run: bool = False,
    ) -> Modification:
        """
        Create a new compound tool.

        Args:
            name: Tool name (snake_case)
            description: What the tool does
            steps: Execution steps
            parameters: Input parameters
            dry_run: Preview without creating

        Returns:
            Modification record
        """
        spec = self._tool_creator.create_tool_spec(
            name=name,
            description=description,
            steps=steps,
            parameters=parameters,
        )

        modification = await self._tool_creator.create_tool(spec, dry_run=dry_run)
        self._modifications.append(modification)
        self._save_history()

        return modification

    # Skill operations

    async def generate_skill(
        self,
        name: str,
        description: str = "",
        patterns: list[str] | None = None,
        from_codebase: Path | None = None,
        dry_run: bool = False,
    ) -> Modification | None:
        """
        Generate a new skill.

        Args:
            name: Skill name
            description: Skill description
            patterns: Patterns to include
            from_codebase: Generate from analyzing codebase
            dry_run: Preview without creating

        Returns:
            Modification record
        """
        if from_codebase:
            spec = await self._skill_generator.generate_skill_from_codebase(
                from_codebase,
                name,
            )
            if not spec:
                return None
        else:
            spec = self._skill_generator.create_skill_spec(
                name=name,
                description=description or f"Skill for {name}",
                patterns=patterns or [],
            )

        modification = await self._skill_generator.create_skill(spec, dry_run=dry_run)
        self._modifications.append(modification)
        self._save_history()

        return modification

    # Code modification operations

    async def modify_code(
        self,
        target: str,
        changes: dict[str, Any],
        reason: str = "",
        require_approval: bool = True,
    ) -> Modification:
        """
        Modify code with safety checks.

        Args:
            target: File path to modify
            changes: Changes to make
            reason: Reason for modification
            require_approval: Whether to require approval

        Returns:
            Modification record
        """
        modification = await self._code_modifier.prepare_modification(
            target=target,
            changes=changes,
            reason=reason,
        )

        modification.requires_approval = require_approval

        if not require_approval and modification.is_safe():
            modification.status = ModificationStatus.APPROVED
            await self._code_modifier.apply_modification(modification)

        self._modifications.append(modification)
        self._save_history()

        return modification

    async def approve_modification(
        self,
        modification_id: str,
        approver: str,
        apply: bool = True,
    ) -> bool:
        """
        Approve a pending modification.

        Args:
            modification_id: ID of modification
            approver: Who is approving
            apply: Whether to apply after approval

        Returns:
            True if approved and optionally applied
        """
        for mod in self._modifications:
            if mod.id == modification_id:
                mod.status = ModificationStatus.APPROVED
                mod.approved_by = approver
                mod.approved_at = datetime.utcnow()

                if apply:
                    return await self._code_modifier.apply_modification(mod)
                return True

        return False

    async def rollback_modification(self, modification_id: str) -> bool:
        """
        Roll back a modification.

        Args:
            modification_id: ID of modification

        Returns:
            True if rolled back
        """
        for mod in self._modifications:
            if mod.id == modification_id:
                return await self._code_modifier.rollback_modification(mod)
        return False

    # Suggestions

    def add_suggestion(
        self,
        title: str,
        description: str,
        source: str = "",
        priority: str = "medium",
    ) -> ImprovementSuggestion:
        """Add an improvement suggestion."""
        suggestion = ImprovementSuggestion(
            title=title,
            description=description,
            source=source,
            priority=priority,
        )

        self._suggestions.append(suggestion)
        self._save_history()

        return suggestion

    def list_suggestions(
        self,
        priority: str | None = None,
    ) -> list[ImprovementSuggestion]:
        """List improvement suggestions."""
        suggestions = self._suggestions

        if priority:
            suggestions = [s for s in suggestions if s.priority == priority]

        return sorted(suggestions, key=lambda s: s.created_at, reverse=True)

    # Status and reporting

    def get_status(self) -> dict[str, Any]:
        """Get engine status."""
        can_modify, reason = self._code_modifier.can_modify()

        return {
            "can_modify": can_modify,
            "modification_limit_reason": reason,
            "total_modifications": len(self._modifications),
            "pending_suggestions": len(self._suggestions),
            "modifications_by_status": {
                status.value: len([m for m in self._modifications if m.status == status])
                for status in ModificationStatus
                if any(m.status == status for m in self._modifications)
            },
            "agents_created": len(self._agent_creator.list_agents()),
            "tools_created": len(self._tool_creator.list_tools()),
            "skills_generated": len(self._skill_generator.list_skills()),
        }

    def get_modifications(
        self,
        status: ModificationStatus | None = None,
        limit: int = 100,
    ) -> list[Modification]:
        """Get modification history."""
        mods = self._modifications

        if status:
            mods = [m for m in mods if m.status == status]

        return sorted(mods, key=lambda m: m.created_at, reverse=True)[:limit]


# Global engine instance
_engine: SelfImprovementEngine | None = None


def get_self_improvement_engine() -> SelfImprovementEngine:
    """Get or create the global self-improvement engine."""
    global _engine

    if _engine is None:
        _engine = SelfImprovementEngine()

    return _engine
