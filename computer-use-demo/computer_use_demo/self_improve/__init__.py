"""
Proto Self-Improvement Engine.

Safe self-modification capabilities for the agent system.

Components:
- CodeModifier: Safe code modifications with testing
- AgentCreator: Create new specialist agents
- ToolCreator: Create compound tools
- SkillGenerator: Generate skills from patterns

Safety:
- All changes require tests to pass
- Maximum 10 modifications per day
- Rollback capability for all changes
- Human approval for critical changes

Usage:
    from computer_use_demo.self_improve import (
        SelfImprovementEngine,
        get_self_improvement_engine,
    )

    engine = get_self_improvement_engine()

    # Create a new agent
    await engine.create_agent(
        name="security-expert",
        description="Security analysis specialist",
        capabilities=["code-review", "vulnerability-scan"],
    )

    # Generate a skill from patterns
    await engine.generate_skill(
        name="api-design",
        patterns=["REST", "GraphQL", "OpenAPI"],
    )
"""

from .types import (
    Modification,
    ModificationType,
    ModificationStatus,
    AgentSpec,
    ToolSpec,
    SkillSpec,
    SafetyCheck,
)

from .code_modifier import (
    CodeModifier,
)

from .agent_creator import (
    AgentCreator,
)

from .tool_creator import (
    ToolCreator,
)

from .skill_generator import (
    SkillGenerator,
)

from .engine import (
    SelfImprovementEngine,
    get_self_improvement_engine,
)

__all__ = [
    # Types
    "Modification",
    "ModificationType",
    "ModificationStatus",
    "AgentSpec",
    "ToolSpec",
    "SkillSpec",
    "SafetyCheck",
    # Components
    "CodeModifier",
    "AgentCreator",
    "ToolCreator",
    "SkillGenerator",
    # Engine
    "SelfImprovementEngine",
    "get_self_improvement_engine",
]
