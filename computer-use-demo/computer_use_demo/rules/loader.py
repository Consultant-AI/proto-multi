"""
Rule loader - loads rules from markdown files and configuration.
"""

import re
from pathlib import Path
from typing import Any

from .types import Rule, RuleScope, RuleSeverity


def get_enterprise_rules_path() -> Path:
    """Get path to enterprise-level rules directory."""
    return Path.home() / ".claude" / "rules"


def get_project_rules_path(project_root: Path | None = None) -> Path | None:
    """Get path to project-level rules directory."""
    if project_root:
        return project_root / ".claude" / "rules"

    # Search upward for project root
    current = Path.cwd()
    indicators = [".git", ".claude", "package.json", "pyproject.toml"]

    while current != current.parent:
        for indicator in indicators:
            if (current / indicator).exists():
                return current / ".claude" / "rules"
        current = current.parent

    return None


def load_rules_from_directory(directory: Path) -> list[Rule]:
    """
    Load rules from a directory containing markdown files.

    Each .md file represents one or more rules.
    """
    rules = []

    if not directory.exists():
        return rules

    for md_file in directory.glob("*.md"):
        file_rules = parse_rule_file(md_file)
        rules.extend(file_rules)

    return rules


def parse_rule_file(path: Path) -> list[Rule]:
    """
    Parse a markdown rule file.

    Rule files follow this format:

    # Rule Name

    Description of the rule.

    ## Config
    - severity: error
    - scope: file
    - tools: git, bash
    - patterns: *.env, secrets.json

    ## Conditions
    - Block commits of .env files
    - Warn on hardcoded passwords
    """
    rules = []

    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return rules

    # Parse rules (each H1 is a rule)
    rule_blocks = re.split(r"^# ", content, flags=re.MULTILINE)

    for i, block in enumerate(rule_blocks):
        if not block.strip():
            continue

        rule = _parse_rule_block(block, path, i)
        if rule:
            rules.append(rule)

    return rules


def _parse_rule_block(block: str, source: Path, index: int) -> Rule | None:
    """Parse a single rule block."""
    lines = block.strip().split("\n")

    if not lines:
        return None

    # First line is the rule name
    name = lines[0].strip()
    if not name:
        return None

    # Generate ID from name
    rule_id = f"{source.stem}_{index}_{_slugify(name)}"

    # Extract description (text before first ##)
    description_lines = []
    config_section = ""
    conditions_section = ""

    current_section = "description"
    for line in lines[1:]:
        if line.startswith("## Config"):
            current_section = "config"
        elif line.startswith("## Conditions"):
            current_section = "conditions"
        elif line.startswith("## "):
            current_section = "other"
        elif current_section == "description":
            description_lines.append(line)
        elif current_section == "config":
            config_section += line + "\n"
        elif current_section == "conditions":
            conditions_section += line + "\n"

    description = "\n".join(description_lines).strip()

    # Parse config section
    config = _parse_config(config_section)

    # Parse severity
    severity_str = config.get("severity", "error").lower()
    severity = RuleSeverity.ERROR
    if severity_str == "warning":
        severity = RuleSeverity.WARNING
    elif severity_str == "info":
        severity = RuleSeverity.INFO

    # Parse scope
    scope_str = config.get("scope", "all").lower()
    scope = RuleScope.ALL
    if scope_str == "tool":
        scope = RuleScope.TOOL
    elif scope_str == "file":
        scope = RuleScope.FILE
    elif scope_str == "command":
        scope = RuleScope.COMMAND

    # Parse tools
    tools_str = config.get("tools", "")
    tools = [t.strip() for t in tools_str.split(",") if t.strip()]

    # Parse patterns
    patterns_str = config.get("patterns", "")
    patterns = [p.strip() for p in patterns_str.split(",") if p.strip()]

    # Parse tags
    tags_str = config.get("tags", "")
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]

    # Parse match patterns from conditions
    match_patterns = _parse_conditions(conditions_section)

    return Rule(
        id=rule_id,
        name=name,
        description=description,
        severity=severity,
        scope=scope,
        tools=tools,
        file_patterns=patterns,
        match_patterns=match_patterns,
        tags=tags,
        source=source,
    )


def _parse_config(config_text: str) -> dict[str, str]:
    """Parse key-value pairs from config section."""
    config = {}

    for line in config_text.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            line = line[2:]
        if ":" in line:
            key, value = line.split(":", 1)
            config[key.strip().lower()] = value.strip()

    return config


def _parse_conditions(conditions_text: str) -> list[str]:
    """Parse condition patterns from conditions section."""
    patterns = []

    for line in conditions_text.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            patterns.append(line[2:])

    return patterns


def _slugify(text: str) -> str:
    """Convert text to a slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text.strip("_")


def load_all_rules(
    project_root: Path | None = None,
    include_enterprise: bool = True,
) -> list[Rule]:
    """
    Load all rules from enterprise and project levels.

    Args:
        project_root: Optional project root path
        include_enterprise: Whether to include enterprise rules

    Returns:
        List of all rules (enterprise + project)
    """
    rules = []

    # Load enterprise rules
    if include_enterprise:
        enterprise_path = get_enterprise_rules_path()
        enterprise_rules = load_rules_from_directory(enterprise_path)
        rules.extend(enterprise_rules)

    # Load project rules
    project_path = get_project_rules_path(project_root)
    if project_path:
        project_rules = load_rules_from_directory(project_path)
        rules.extend(project_rules)

    return rules
