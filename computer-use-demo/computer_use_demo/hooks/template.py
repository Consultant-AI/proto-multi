"""
Template variable substitution for hook commands.

Allows hooks to use variables like {{file_path}}, {{tool_name}}, etc.
"""

import json
import re
from typing import Any

from .types import HookContext


def substitute_variables(command: str, context: HookContext) -> str:
    """
    Substitute template variables in a hook command.

    Supported variables:
    - {{file_path}}: File being operated on
    - {{tool_name}}: Name of the tool being called
    - {{tool_input}}: JSON of tool input/arguments
    - {{event}}: Event type that triggered the hook
    - {{session_id}}: Current session ID
    - {{error}}: Error message (for error hooks)
    - {{result}}: Tool result output (for post hooks)

    Example:
        command = "npm run lint -- {{file_path}}"
        context.file_path = "/path/to/file.ts"
        result = "npm run lint -- /path/to/file.ts"
    """
    # Build substitution map
    substitutions = {
        "file_path": context.file_path or "",
        "tool_name": context.tool_name or "",
        "tool_input": _safe_json(context.tool_input),
        "event": context.event.value if context.event else "",
        "session_id": context.session_id or "",
        "error": context.error or "",
        "result": _get_result_output(context.tool_result),
    }

    # Add any metadata fields
    for key, value in context.metadata.items():
        substitutions[f"metadata.{key}"] = str(value) if value is not None else ""

    # Perform substitution using {{variable}} syntax
    result = command
    for key, value in substitutions.items():
        # Escape special shell characters in values to prevent injection
        safe_value = _shell_escape(str(value))
        result = result.replace(f"{{{{{key}}}}}", safe_value)

    return result


def _safe_json(obj: Any) -> str:
    """Convert object to JSON string safely."""
    try:
        return json.dumps(obj, default=str)
    except Exception:
        return "{}"


def _get_result_output(result: Any) -> str:
    """Extract output string from a tool result."""
    if result is None:
        return ""
    if hasattr(result, "output"):
        return str(result.output) if result.output else ""
    if hasattr(result, "error"):
        return str(result.error) if result.error else ""
    return str(result)


def _shell_escape(s: str) -> str:
    """
    Escape a string for safe use in shell commands.

    This prevents command injection by escaping special characters.
    """
    # For simple cases, just wrap in single quotes and escape existing single quotes
    # This is the safest approach for most shells
    if not s:
        return ""

    # Replace single quotes with escaped version
    escaped = s.replace("'", "'\"'\"'")

    # Only wrap in quotes if the string contains special characters
    if re.search(r'[^\w\-_./]', s):
        return f"'{escaped}'"

    return s


def extract_file_path_from_input(tool_input: dict[str, Any]) -> str | None:
    """
    Extract file path from tool input if present.

    Different tools use different parameter names for file paths.
    """
    # Common file path parameter names
    path_params = ["path", "file_path", "filepath", "filename", "file"]

    for param in path_params:
        if param in tool_input and tool_input[param]:
            return str(tool_input[param])

    return None
