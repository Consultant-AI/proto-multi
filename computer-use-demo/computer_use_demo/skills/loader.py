"""
Skill loader - discovers and loads SKILL.md files.
"""

import re
from pathlib import Path
from typing import Any

import yaml

from .types import Skill, SkillTrigger


def get_enterprise_skills_path() -> Path:
    """Get path to enterprise-level skills directory."""
    return Path.home() / ".claude" / "skills"


def get_project_skills_path(project_root: Path | None = None) -> Path | None:
    """Get path to project-level skills directory."""
    if project_root:
        return project_root / ".claude" / "skills"

    # Search upward for project root
    current = Path.cwd()
    indicators = [".git", ".claude", "package.json", "pyproject.toml"]

    while current != current.parent:
        for indicator in indicators:
            if (current / indicator).exists():
                return current / ".claude" / "skills"
        current = current.parent

    return None


def load_skills_from_directory(directory: Path) -> list[Skill]:
    """
    Load skills from a directory containing SKILL.md files.

    Skills are organized as:
    skills/
    ├── code-review/
    │   └── SKILL.md
    ├── security-audit/
    │   └── SKILL.md
    └── test-writing/
        └── SKILL.md
    """
    skills = []

    if not directory.exists():
        return skills

    # Look for SKILL.md files in subdirectories
    for skill_dir in directory.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                skill = parse_skill_file(skill_file)
                if skill:
                    skills.append(skill)

    # Also look for any .md files directly in the directory
    # All .md files with valid skill frontmatter are treated as skills
    for md_file in directory.glob("*.md"):
        skill = parse_skill_file(md_file)
        if skill:
            # Check if skill not already loaded (from subdirectory)
            if not any(s.name == skill.name for s in skills):
                skills.append(skill)

    return skills


def parse_skill_file(path: Path) -> Skill | None:
    """
    Parse a SKILL.md file.

    SKILL.md format:
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
    3. Security vulnerabilities
    ...
    """
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return None

    # Parse frontmatter
    frontmatter, body = _parse_frontmatter(content)

    if not frontmatter:
        # No frontmatter - use filename as name
        frontmatter = {"name": path.stem}

    # Build skill
    name = frontmatter.get("name", path.stem)
    description = frontmatter.get("description", "")

    # Parse triggers
    triggers_data = frontmatter.get("triggers", {})
    triggers = SkillTrigger(
        keywords=triggers_data.get("keywords", []),
        file_patterns=triggers_data.get("file_patterns", []),
        tools=triggers_data.get("tools", []),
    )

    # Parse other fields
    allowed_tools = frontmatter.get("allowed_tools", [])
    priority = frontmatter.get("priority", 0)
    tags = frontmatter.get("tags", [])
    enabled = frontmatter.get("enabled", True)

    return Skill(
        name=name,
        description=description,
        content=body.strip(),
        triggers=triggers,
        allowed_tools=allowed_tools,
        enabled=enabled,
        source=path,
        tags=tags,
        priority=priority,
    )


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """
    Parse YAML frontmatter from markdown content.

    Returns (frontmatter_dict, remaining_content).
    """
    # Check for frontmatter delimiters
    if not content.startswith("---"):
        return {}, content

    # Find end of frontmatter
    lines = content.split("\n")
    end_index = None

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = i
            break

    if end_index is None:
        return {}, content

    # Parse YAML
    frontmatter_text = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1:])

    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError:
        frontmatter = {}

    return frontmatter, body


def load_all_skills(
    project_root: Path | None = None,
    include_enterprise: bool = True,
) -> list[Skill]:
    """
    Load all skills from enterprise and project levels.

    Args:
        project_root: Optional project root path
        include_enterprise: Whether to include enterprise skills

    Returns:
        List of all skills
    """
    skills = []

    # Load enterprise skills
    if include_enterprise:
        enterprise_path = get_enterprise_skills_path()
        enterprise_skills = load_skills_from_directory(enterprise_path)
        skills.extend(enterprise_skills)

    # Load project skills
    project_path = get_project_skills_path(project_root)
    if project_path:
        project_skills = load_skills_from_directory(project_path)
        skills.extend(project_skills)

    # Sort by priority (higher first)
    skills.sort(key=lambda s: s.priority, reverse=True)

    return skills
