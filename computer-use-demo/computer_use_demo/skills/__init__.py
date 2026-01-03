"""
Proto Skills Module - Auto-activated specialized knowledge.

Skills are context-aware knowledge injections that activate automatically
based on triggers (keywords, file patterns, tools being used).

Skill File Format (SKILL.md with YAML frontmatter):
    ---
    name: code-review
    description: Expert code review guidance
    triggers:
      keywords: [review, code review, check code]
      file_patterns: ["*.py", "*.ts"]
      tools: [str_replace_editor]
    allowed_tools: [str_replace_editor, bash]
    priority: 10
    tags: [review, quality]
    ---

    # Code Review Expertise

    When reviewing code, always check:
    1. Error handling
    2. Edge cases
    ...

Skill Hierarchy:
1. Enterprise: ~/.claude/skills/ (organization-wide)
2. Project: .claude/skills/ (project-specific)

Usage:
    from computer_use_demo.skills import (
        get_skill_injection,
        match_skills,
        SkillContext,
    )

    # Get skills to inject based on context
    injection = get_skill_injection(
        message="Please review this Python code",
        file_path="main.py",
    )

    # Use injection in system prompt
    system_prompt = f"{base_prompt}\\n\\n{injection}"
"""

from .executor import (
    format_skills_for_injection,
    get_active_skill_names,
    get_skill_injection,
    get_skills_for_context,
)

from .loader import (
    get_enterprise_skills_path,
    get_project_skills_path,
    load_all_skills,
    load_skills_from_directory,
    parse_skill_file,
)

from .matcher import (
    SkillMatcher,
    get_skill_matcher,
    match_skills,
)

from .types import (
    Skill,
    SkillContext,
    SkillMatch,
    SkillTrigger,
)

__all__ = [
    # Types
    "Skill",
    "SkillContext",
    "SkillMatch",
    "SkillTrigger",
    # Loader
    "get_enterprise_skills_path",
    "get_project_skills_path",
    "load_all_skills",
    "load_skills_from_directory",
    "parse_skill_file",
    # Matcher
    "SkillMatcher",
    "get_skill_matcher",
    "match_skills",
    # Executor
    "format_skills_for_injection",
    "get_active_skill_names",
    "get_skill_injection",
    "get_skills_for_context",
]
