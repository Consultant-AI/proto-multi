"""
Type definitions for the skills system.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SkillTrigger:
    """Trigger condition for skill activation."""

    # Keywords that trigger this skill
    keywords: list[str] = field(default_factory=list)

    # File patterns that trigger this skill
    file_patterns: list[str] = field(default_factory=list)

    # Tool names that trigger this skill
    tools: list[str] = field(default_factory=list)

    # Custom trigger function
    custom: Any = None


@dataclass
class Skill:
    """A skill definition."""

    # Skill name
    name: str

    # Description
    description: str = ""

    # The skill content (instructions/knowledge)
    content: str = ""

    # Trigger conditions
    triggers: SkillTrigger = field(default_factory=SkillTrigger)

    # Tools this skill is allowed to use (empty = all)
    allowed_tools: list[str] = field(default_factory=list)

    # Whether skill is enabled
    enabled: bool = True

    # Source file
    source: Path | None = None

    # Tags
    tags: list[str] = field(default_factory=list)

    # Priority (higher = more important when multiple match)
    priority: int = 0


@dataclass
class SkillMatch:
    """Result of matching a skill to a context."""

    # The matched skill
    skill: Skill

    # Why it matched
    match_reason: str

    # Confidence score (0-1)
    confidence: float = 1.0

    # Which triggers fired
    triggered_by: list[str] = field(default_factory=list)


@dataclass
class SkillContext:
    """Context for skill matching and execution."""

    # User's message/task
    message: str = ""

    # Current file being worked on
    file_path: str | None = None

    # Tools being used
    tools_in_use: list[str] = field(default_factory=list)

    # Additional context
    metadata: dict[str, Any] = field(default_factory=dict)
