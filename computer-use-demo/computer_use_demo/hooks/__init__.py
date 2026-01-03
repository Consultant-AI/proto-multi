"""
Proto Hooks System - Deterministic automation for tool execution.

Hooks allow shell commands to be executed automatically before/after tool calls,
providing deterministic automation for tasks like linting, testing, and validation.

Usage:
    from computer_use_demo.hooks import get_hook_executor, get_hook_registry

    # Get the global executor
    executor = get_hook_executor()

    # Run pre-tool hooks
    should_continue, error = await executor.run_pre_tool_hooks(
        tool_name="str_replace_editor",
        tool_input={"path": "/path/to/file.py", "command": "str_replace"},
    )

    if not should_continue:
        # Hook blocked execution
        return ToolFailure(error=error)

    # Run the tool...

    # Run post-tool hooks
    await executor.run_post_tool_hooks(
        tool_name="str_replace_editor",
        tool_input={"path": "/path/to/file.py", "command": "str_replace"},
        tool_result=result,
    )

Configuration (hooks.json):
    {
        "hooks": [
            {
                "event": "pre_tool_call",
                "tool": "str_replace_editor",
                "command": "npm run lint -- {{file_path}}",
                "blocking": true,
                "fail_behavior": "warn"
            }
        ]
    }
"""

from .executor import HookExecutor, get_hook_executor
from .registry import HookRegistry, get_hook_registry
from .template import extract_file_path_from_input, substitute_variables
from .types import (
    HookConfig,
    HookContext,
    HookEvent,
    HookFailBehavior,
    HookResult,
)

__all__ = [
    # Executor
    "HookExecutor",
    "get_hook_executor",
    # Registry
    "HookRegistry",
    "get_hook_registry",
    # Template
    "substitute_variables",
    "extract_file_path_from_input",
    # Types
    "HookConfig",
    "HookContext",
    "HookEvent",
    "HookFailBehavior",
    "HookResult",
]
