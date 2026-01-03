"""Collection classes for managing multiple tools."""

from typing import Any

from anthropic.types.beta import BetaToolUnionParam

from .base import (
    BaseAnthropicTool,
    ToolError,
    ToolFailure,
    ToolResult,
)

# Import hooks - wrapped in try/except to avoid breaking if hooks module has issues
try:
    from ..hooks import get_hook_executor
    HOOKS_AVAILABLE = True
except ImportError:
    HOOKS_AVAILABLE = False
    get_hook_executor = None

# Import rules - for checking rules before tool execution
try:
    from ..rules import check_rules, RuleSeverity
    RULES_AVAILABLE = True
except ImportError:
    RULES_AVAILABLE = False
    check_rules = None
    RuleSeverity = None


class ToolCollection:
    """A collection of anthropic-defined tools."""

    def __init__(self, *tools: BaseAnthropicTool, hooks_enabled: bool = True, rules_enabled: bool = True):
        self.tools = tools
        self.tool_map = {tool.to_params()["name"]: tool for tool in tools}
        self._hooks_enabled = hooks_enabled and HOOKS_AVAILABLE
        self._rules_enabled = rules_enabled and RULES_AVAILABLE
        self._session_id: str | None = None

    def set_session_id(self, session_id: str) -> None:
        """Set the session ID for hook context."""
        self._session_id = session_id

    def to_params(
        self,
    ) -> list[BetaToolUnionParam]:
        return [tool.to_params() for tool in self.tools]

    async def run(self, *, name: str, tool_input: dict[str, Any]) -> ToolResult:
        tool = self.tool_map.get(name)
        if not tool:
            return ToolFailure(error=f"Tool {name} is invalid")

        # Check rules before execution
        if self._rules_enabled:
            try:
                rule_result = check_rules(name, tool_input)
                if not rule_result.allowed:
                    # Build error message from violations
                    violations_msg = "; ".join(
                        v.message for v in rule_result.violations
                        if v.rule.severity == RuleSeverity.ERROR
                    )
                    return ToolFailure(error=f"Rule violation: {violations_msg}")

                # Log warnings (but don't block)
                for violation in rule_result.violations:
                    if violation.rule.severity == RuleSeverity.WARNING:
                        print(f"[Rules] Warning: {violation.message}")
            except Exception as e:
                # Don't let rule errors break tool execution
                print(f"[Rules] Rule check error: {e}")

        # Run pre-tool hooks
        if self._hooks_enabled:
            try:
                executor = get_hook_executor()
                should_continue, error = await executor.run_pre_tool_hooks(
                    tool_name=name,
                    tool_input=tool_input,
                    session_id=self._session_id,
                )
                if not should_continue:
                    return ToolFailure(error=error or "Hook blocked execution")
            except Exception as e:
                # Don't let hook errors break tool execution
                print(f"[Hooks] Pre-tool hook error: {e}")

        # Execute the tool
        result: ToolResult
        error_message: str | None = None
        try:
            result = await tool(**tool_input)
        except ToolError as e:
            error_message = e.message
            result = ToolFailure(error=e.message)

        # Run post-tool hooks (or error hooks)
        if self._hooks_enabled:
            try:
                executor = get_hook_executor()
                if error_message:
                    await executor.run_error_hooks(
                        tool_name=name,
                        tool_input=tool_input,
                        error=error_message,
                        session_id=self._session_id,
                    )
                else:
                    await executor.run_post_tool_hooks(
                        tool_name=name,
                        tool_input=tool_input,
                        tool_result=result,
                        session_id=self._session_id,
                    )
            except Exception as e:
                # Don't let hook errors affect the result
                print(f"[Hooks] Post-tool hook error: {e}")

        return result
