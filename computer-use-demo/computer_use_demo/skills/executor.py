"""
Skill executor - injects skills into agent context.
"""

from typing import Any

from .matcher import get_skill_matcher, match_skills
from .types import Skill, SkillContext, SkillMatch


def get_skills_for_context(context: SkillContext) -> list[SkillMatch]:
    """
    Get skills that should be activated for a context.

    Args:
        context: The current context

    Returns:
        List of matched skills
    """
    return match_skills(context)


def format_skills_for_injection(matches: list[SkillMatch]) -> str:
    """
    Format matched skills for injection into agent context.

    Returns formatted content suitable for hidden system prompt injection.

    Args:
        matches: List of skill matches

    Returns:
        Formatted string for injection
    """
    if not matches:
        return ""

    parts = ["<SKILLS>", "The following skills have been auto-activated based on context:", ""]

    for match in matches:
        skill = match.skill
        parts.append(f"### {skill.name}")
        if skill.description:
            parts.append(f"*{skill.description}*")
        parts.append("")
        parts.append(skill.content)
        parts.append("")

    parts.append("</SKILLS>")

    return "\n".join(parts)


def get_skill_injection(
    message: str,
    file_path: str | None = None,
    tools_in_use: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """
    Get skill content to inject based on context.

    Convenience function that creates context and returns injection string.

    Args:
        message: User's message or task
        file_path: Current file being worked on
        tools_in_use: Tools being used
        metadata: Additional context

    Returns:
        Formatted string for injection (empty if no skills match)
    """
    context = SkillContext(
        message=message,
        file_path=file_path,
        tools_in_use=tools_in_use or [],
        metadata=metadata or {},
    )

    matches = get_skills_for_context(context)
    return format_skills_for_injection(matches)


def get_active_skill_names(context: SkillContext) -> list[str]:
    """
    Get names of skills that would be activated.

    Useful for logging/debugging.

    Args:
        context: The context to check

    Returns:
        List of skill names
    """
    matches = match_skills(context)
    return [m.skill.name for m in matches]
