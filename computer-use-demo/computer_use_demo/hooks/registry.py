"""
Hook registry for managing and discovering hooks.

Loads hooks from configuration files and provides lookup by event/tool.
"""

import json
import os
import re
from pathlib import Path
from typing import Any

from .types import HookConfig, HookEvent, HookFailBehavior


class HookRegistry:
    """
    Registry for managing hooks.

    Loads hooks from:
    1. ~/.claude/hooks.json (user-level)
    2. .claude/hooks.json (project-level)

    Project-level hooks take precedence over user-level hooks.
    """

    def __init__(self):
        self._hooks: list[HookConfig] = []
        self._loaded = False

    def load(self, project_path: str | None = None) -> None:
        """
        Load hooks from configuration files.

        Args:
            project_path: Path to the project root (for project-level hooks)
        """
        self._hooks = []

        # Load user-level hooks first
        user_hooks_path = Path.home() / ".claude" / "hooks.json"
        if user_hooks_path.exists():
            self._load_from_file(user_hooks_path)

        # Load project-level hooks (override user-level)
        if project_path:
            project_hooks_path = Path(project_path) / ".claude" / "hooks.json"
            if project_hooks_path.exists():
                self._load_from_file(project_hooks_path)

        self._loaded = True

    def _load_from_file(self, path: Path) -> None:
        """Load hooks from a JSON configuration file."""
        try:
            with open(path, "r") as f:
                config = json.load(f)

            hooks_data = config.get("hooks", [])
            for hook_data in hooks_data:
                hook = self._parse_hook(hook_data)
                if hook:
                    self._hooks.append(hook)

        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse hooks config at {path}: {e}")
        except Exception as e:
            print(f"Warning: Failed to load hooks from {path}: {e}")

    def _parse_hook(self, data: dict[str, Any]) -> HookConfig | None:
        """Parse a hook configuration from JSON data."""
        try:
            # Parse event type
            event_str = data.get("event", "")
            try:
                event = HookEvent(event_str)
            except ValueError:
                print(f"Warning: Unknown hook event type: {event_str}")
                return None

            # Parse fail behavior
            fail_behavior_str = data.get("fail_behavior", "warn")
            try:
                fail_behavior = HookFailBehavior(fail_behavior_str)
            except ValueError:
                fail_behavior = HookFailBehavior.WARN

            return HookConfig(
                event=event,
                command=data.get("command", ""),
                tool=data.get("tool"),
                pattern=data.get("pattern"),
                blocking=data.get("blocking", True),
                fail_behavior=fail_behavior,
                timeout=data.get("timeout", 30),
                description=data.get("description", ""),
                enabled=data.get("enabled", True),
            )

        except Exception as e:
            print(f"Warning: Failed to parse hook: {e}")
            return None

    def get_hooks_for_event(
        self, event: HookEvent, tool_name: str | None = None, tool_input: dict[str, Any] | None = None
    ) -> list[HookConfig]:
        """
        Get all hooks that should be triggered for an event.

        Args:
            event: The event type
            tool_name: Name of the tool (for filtering)
            tool_input: Tool input (for pattern matching)

        Returns:
            List of matching hook configurations
        """
        if not self._loaded:
            self.load()

        matching_hooks = []

        for hook in self._hooks:
            if not hook.enabled:
                continue

            # Check event matches
            if hook.event != event:
                # Also check for specific tool events
                if not self._is_tool_specific_event(hook.event, event, tool_name):
                    continue

            # Check tool filter
            if hook.tool and tool_name and hook.tool != tool_name:
                continue

            # Check pattern filter
            if hook.pattern and tool_input:
                if not self._matches_pattern(hook.pattern, tool_input):
                    continue

            matching_hooks.append(hook)

        return matching_hooks

    def _is_tool_specific_event(self, hook_event: HookEvent, actual_event: HookEvent, tool_name: str | None) -> bool:
        """Check if a tool-specific event matches the actual event and tool."""
        if not tool_name:
            return False

        # Map tool names to their specific events
        tool_event_map = {
            ("str_replace_editor", HookEvent.PRE_TOOL_CALL): HookEvent.PRE_EDIT,
            ("str_replace_editor", HookEvent.POST_TOOL_CALL): HookEvent.POST_EDIT,
            ("str_replace_based_edit_tool", HookEvent.PRE_TOOL_CALL): HookEvent.PRE_EDIT,
            ("str_replace_based_edit_tool", HookEvent.POST_TOOL_CALL): HookEvent.POST_EDIT,
            ("bash", HookEvent.PRE_TOOL_CALL): HookEvent.PRE_BASH,
            ("bash", HookEvent.POST_TOOL_CALL): HookEvent.POST_BASH,
            ("computer", HookEvent.PRE_TOOL_CALL): HookEvent.PRE_COMPUTER,
            ("computer", HookEvent.POST_TOOL_CALL): HookEvent.POST_COMPUTER,
        }

        expected_specific_event = tool_event_map.get((tool_name, actual_event))
        return hook_event == expected_specific_event

    def _matches_pattern(self, pattern: str, tool_input: dict[str, Any]) -> bool:
        """Check if tool input matches a regex pattern."""
        try:
            # Convert tool input to string for pattern matching
            input_str = json.dumps(tool_input, default=str)
            return bool(re.search(pattern, input_str))
        except Exception:
            return False

    def add_hook(self, hook: HookConfig) -> None:
        """Add a hook programmatically."""
        self._hooks.append(hook)

    def remove_hook(self, hook: HookConfig) -> None:
        """Remove a hook."""
        if hook in self._hooks:
            self._hooks.remove(hook)

    def clear(self) -> None:
        """Clear all hooks."""
        self._hooks = []
        self._loaded = False

    @property
    def hooks(self) -> list[HookConfig]:
        """Get all registered hooks."""
        if not self._loaded:
            self.load()
        return self._hooks.copy()


# Global registry instance
_global_registry: HookRegistry | None = None


def get_hook_registry() -> HookRegistry:
    """Get the global hook registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = HookRegistry()
    return _global_registry
