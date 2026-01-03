"""
Type definitions for the rules system.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class RuleSeverity(str, Enum):
    """Severity levels for rules."""

    ERROR = "error"      # Blocks the action
    WARNING = "warning"  # Warns but allows
    INFO = "info"        # Informational only


class RuleScope(str, Enum):
    """Scope of rule application."""

    ALL = "all"              # Applies to all tools
    TOOL = "tool"            # Applies to specific tools
    FILE = "file"            # Applies to file operations
    COMMAND = "command"      # Applies to bash commands


@dataclass
class Rule:
    """A single rule definition."""

    # Rule identifier
    id: str

    # Human-readable name
    name: str

    # Description of what this rule enforces
    description: str

    # Severity level
    severity: RuleSeverity = RuleSeverity.ERROR

    # Scope of application
    scope: RuleScope = RuleScope.ALL

    # Tools this rule applies to (empty = all)
    tools: list[str] = field(default_factory=list)

    # File patterns this rule applies to (glob patterns)
    file_patterns: list[str] = field(default_factory=list)

    # Check function (returns True if rule passes, False if violated)
    check: Callable[[dict[str, Any]], bool] | None = None

    # Patterns to match (for built-in checks)
    match_patterns: list[str] = field(default_factory=list)

    # Patterns to exclude
    exclude_patterns: list[str] = field(default_factory=list)

    # Source file
    source: Path | None = None

    # Tags
    tags: list[str] = field(default_factory=list)

    # Whether rule is enabled
    enabled: bool = True


@dataclass
class RuleViolation:
    """A rule violation."""

    # The rule that was violated
    rule: Rule

    # Description of the violation
    message: str

    # Context about the violation
    context: dict[str, Any] = field(default_factory=dict)

    # Tool that triggered the violation
    tool_name: str | None = None

    # Tool input that triggered the violation
    tool_input: dict[str, Any] | None = None


@dataclass
class RuleCheckResult:
    """Result of checking rules against an action."""

    # Whether the action is allowed
    allowed: bool = True

    # Violations found
    violations: list[RuleViolation] = field(default_factory=list)

    # Rules that passed
    passed_rules: list[Rule] = field(default_factory=list)

    # Whether any blocking violations exist
    @property
    def has_blocking_violations(self) -> bool:
        return any(v.rule.severity == RuleSeverity.ERROR for v in self.violations)

    # Whether any warnings exist
    @property
    def has_warnings(self) -> bool:
        return any(v.rule.severity == RuleSeverity.WARNING for v in self.violations)
