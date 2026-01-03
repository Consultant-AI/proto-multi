"""
Rule enforcer - checks actions against rules.
"""

import fnmatch
import re
import threading
from pathlib import Path
from typing import Any

from .loader import load_all_rules
from .types import Rule, RuleCheckResult, RuleScope, RuleSeverity, RuleViolation


class RuleEnforcer:
    """
    Enforces rules by checking tool calls and actions.

    Usage:
        enforcer = RuleEnforcer()

        # Check a tool call
        result = enforcer.check_tool_call(
            tool_name="bash",
            tool_input={"command": "git commit -m 'update'"},
        )

        if not result.allowed:
            for violation in result.violations:
                print(f"Violation: {violation.message}")
    """

    def __init__(
        self,
        project_root: Path | None = None,
        auto_load: bool = True,
    ):
        self._project_root = project_root
        self._rules: list[Rule] = []
        self._lock = threading.Lock()

        if auto_load:
            self.reload_rules()

    def reload_rules(self) -> None:
        """Reload rules from disk."""
        with self._lock:
            self._rules = load_all_rules(self._project_root)

    @property
    def rules(self) -> list[Rule]:
        """Get loaded rules."""
        return self._rules.copy()

    def add_rule(self, rule: Rule) -> None:
        """Add a rule programmatically."""
        with self._lock:
            self._rules.append(rule)

    def check_tool_call(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
    ) -> RuleCheckResult:
        """
        Check if a tool call violates any rules.

        Args:
            tool_name: Name of the tool being called
            tool_input: Tool input parameters

        Returns:
            RuleCheckResult
        """
        violations = []
        passed = []

        for rule in self._rules:
            if not rule.enabled:
                continue

            # Check if rule applies to this tool
            if not self._rule_applies_to_tool(rule, tool_name):
                continue

            # Check the rule
            violation = self._check_rule(rule, tool_name, tool_input)

            if violation:
                violations.append(violation)
            else:
                passed.append(rule)

        # Determine if action is allowed
        allowed = not any(
            v.rule.severity == RuleSeverity.ERROR for v in violations
        )

        return RuleCheckResult(
            allowed=allowed,
            violations=violations,
            passed_rules=passed,
        )

    def _rule_applies_to_tool(self, rule: Rule, tool_name: str) -> bool:
        """Check if a rule applies to a specific tool."""
        # If rule specifies tools, check if this tool is in the list
        if rule.tools:
            return tool_name in rule.tools

        # Check scope
        if rule.scope == RuleScope.TOOL:
            return True
        elif rule.scope == RuleScope.FILE:
            # File rules apply to edit, write, read tools
            return tool_name in ["str_replace_editor", "edit", "write", "read"]
        elif rule.scope == RuleScope.COMMAND:
            # Command rules apply to bash
            return tool_name == "bash"
        else:
            # ALL scope
            return True

    def _check_rule(
        self,
        rule: Rule,
        tool_name: str,
        tool_input: dict[str, Any],
    ) -> RuleViolation | None:
        """
        Check if a specific rule is violated.

        Returns RuleViolation if violated, None if passed.
        """
        # If rule has a custom check function, use it
        if rule.check:
            context = {
                "tool_name": tool_name,
                "tool_input": tool_input,
            }
            if not rule.check(context):
                return RuleViolation(
                    rule=rule,
                    message=f"Rule '{rule.name}' violated: {rule.description}",
                    context=context,
                    tool_name=tool_name,
                    tool_input=tool_input,
                )
            return None

        # Built-in checks based on rule configuration
        violation = None

        # Check file patterns
        if rule.file_patterns and rule.scope == RuleScope.FILE:
            file_path = self._extract_file_path(tool_input)
            if file_path:
                for pattern in rule.file_patterns:
                    if fnmatch.fnmatch(file_path, pattern):
                        violation = RuleViolation(
                            rule=rule,
                            message=f"Rule '{rule.name}': File '{file_path}' matches blocked pattern '{pattern}'",
                            context={"file_path": file_path, "pattern": pattern},
                            tool_name=tool_name,
                            tool_input=tool_input,
                        )
                        break

        # Check match patterns (general text matching)
        if rule.match_patterns and not violation:
            input_text = str(tool_input)
            for pattern in rule.match_patterns:
                # Check if pattern is a regex or simple text
                if self._matches_pattern(input_text, pattern):
                    violation = RuleViolation(
                        rule=rule,
                        message=f"Rule '{rule.name}': Input matches blocked pattern",
                        context={"pattern": pattern},
                        tool_name=tool_name,
                        tool_input=tool_input,
                    )
                    break

        return violation

    def _extract_file_path(self, tool_input: dict[str, Any]) -> str | None:
        """Extract file path from tool input."""
        # Try common parameter names
        for key in ["path", "file_path", "file", "filename"]:
            if key in tool_input:
                return str(tool_input[key])
        return None

    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches a pattern."""
        # Try as regex first
        try:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        except re.error:
            pass

        # Fall back to simple substring matching
        return pattern.lower() in text.lower()


# Global enforcer instance
_global_enforcer: RuleEnforcer | None = None


def get_rule_enforcer(project_root: Path | None = None) -> RuleEnforcer:
    """Get or create the global rule enforcer."""
    global _global_enforcer

    if _global_enforcer is None:
        _global_enforcer = RuleEnforcer(project_root)

    return _global_enforcer


def check_rules(
    tool_name: str,
    tool_input: dict[str, Any],
) -> RuleCheckResult:
    """
    Convenience function to check rules.

    Args:
        tool_name: Name of the tool
        tool_input: Tool input parameters

    Returns:
        RuleCheckResult
    """
    enforcer = get_rule_enforcer()
    return enforcer.check_tool_call(tool_name, tool_input)
