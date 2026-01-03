"""
Hook types and data structures for the Proto hooks system.

Hooks provide deterministic automation triggered by events (pre/post tool calls).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal


class HookEvent(str, Enum):
    """Events that can trigger hooks."""

    # Tool lifecycle events
    PRE_TOOL_CALL = "pre_tool_call"      # Before any tool executes
    POST_TOOL_CALL = "post_tool_call"    # After any tool completes
    ON_TOOL_ERROR = "on_tool_error"      # When a tool fails

    # Session lifecycle events
    ON_SESSION_START = "on_session_start"  # When a session begins
    ON_SESSION_END = "on_session_end"      # When a session ends

    # Specific tool events (pre/post)
    PRE_EDIT = "pre_edit"                # Before Edit tool
    POST_EDIT = "post_edit"              # After Edit tool
    PRE_BASH = "pre_bash"                # Before Bash tool
    POST_BASH = "post_bash"              # After Bash tool
    PRE_COMPUTER = "pre_computer"        # Before Computer tool
    POST_COMPUTER = "post_computer"      # After Computer tool


class HookFailBehavior(str, Enum):
    """What to do when a hook fails."""

    ABORT = "abort"      # Stop tool execution entirely
    WARN = "warn"        # Log warning but continue
    IGNORE = "ignore"    # Silently continue


@dataclass
class HookConfig:
    """Configuration for a single hook."""

    # Which event triggers this hook
    event: HookEvent

    # Shell command to execute
    command: str

    # Optional: only trigger for specific tool (e.g., "str_replace_editor")
    tool: str | None = None

    # Optional: regex pattern to match against tool input/command
    pattern: str | None = None

    # Should this hook block execution until complete?
    blocking: bool = True

    # What to do if hook fails
    fail_behavior: HookFailBehavior = HookFailBehavior.WARN

    # Timeout in seconds (0 = no timeout)
    timeout: int = 30

    # Description for logging/debugging
    description: str = ""

    # Is this hook enabled?
    enabled: bool = True


@dataclass
class HookContext:
    """Context passed to hooks during execution."""

    # Event that triggered the hook
    event: HookEvent

    # Tool being executed (if applicable)
    tool_name: str | None = None

    # Tool input/arguments
    tool_input: dict[str, Any] = field(default_factory=dict)

    # Tool result (for POST events only)
    tool_result: Any = None

    # Error message (for ON_ERROR events only)
    error: str | None = None

    # File path being operated on (if applicable)
    file_path: str | None = None

    # Session ID
    session_id: str | None = None

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HookResult:
    """Result of hook execution."""

    # Was the hook successful?
    success: bool

    # Output from the hook command
    output: str = ""

    # Error message if failed
    error: str | None = None

    # Return code from the shell command
    return_code: int = 0

    # How long the hook took to execute (seconds)
    duration: float = 0.0

    # Should tool execution be aborted?
    should_abort: bool = False
