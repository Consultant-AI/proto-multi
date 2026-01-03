"""
Proto Rules Module - Enforced guardrails for all agents.

Rules define constraints that must be followed by all agents.
Unlike memory (preferences), rules are enforced and can block actions.

Rule Hierarchy:
1. Enterprise: ~/.claude/rules/ (organization-wide)
2. Project: .claude/rules/ (project-specific)

Rule File Format (markdown):
    # No Secrets in Commits

    Prevent committing sensitive files.

    ## Config
    - severity: error
    - scope: file
    - patterns: *.env, secrets.json, credentials.*

    ## Conditions
    - Block commits of .env files
    - Block commits of files containing API keys

Usage:
    from computer_use_demo.rules import (
        check_rules,
        get_rule_enforcer,
        Rule,
    )

    # Check if a tool call violates rules
    result = check_rules(
        tool_name="bash",
        tool_input={"command": "git add .env"},
    )

    if not result.allowed:
        for violation in result.violations:
            print(f"Blocked: {violation.message}")
"""

from .enforcer import (
    RuleEnforcer,
    check_rules,
    get_rule_enforcer,
)

from .loader import (
    get_enterprise_rules_path,
    get_project_rules_path,
    load_all_rules,
    load_rules_from_directory,
    parse_rule_file,
)

from .types import (
    Rule,
    RuleCheckResult,
    RuleScope,
    RuleSeverity,
    RuleViolation,
)

__all__ = [
    # Types
    "Rule",
    "RuleCheckResult",
    "RuleScope",
    "RuleSeverity",
    "RuleViolation",
    # Loader
    "get_enterprise_rules_path",
    "get_project_rules_path",
    "load_all_rules",
    "load_rules_from_directory",
    "parse_rule_file",
    # Enforcer
    "RuleEnforcer",
    "get_rule_enforcer",
    "check_rules",
]
