"""
GlobTool: Fast file pattern matching for codebase navigation.

Supports glob patterns like:
- *.py (all Python files in current directory)
- **/*.py (all Python files recursively)
- src/**/*.{js,ts} (JavaScript and TypeScript files in src)
"""

from pathlib import Path
from typing import Any, Literal

from ..base import BaseAnthropicTool, CLIResult, ToolError


class GlobTool(BaseAnthropicTool):
    """
    File pattern matching tool for finding files by glob patterns.
    Much faster than using bash commands for file discovery.
    """

    name: Literal["glob"] = "glob"
    api_type: Literal["custom"] = "custom"

    def to_params(self) -> Any:
        return {
            "name": self.name,
            "description": (
                "Search for files matching a glob pattern. Returns list of file paths sorted by modification time. "
                "Supports patterns like '**/*.py' for all Python files, 'src/**/*.ts' for TypeScript in src/, "
                "or '*.{js,json}' for multiple extensions. "
                "Use this tool to quickly find files by name/pattern before reading them."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": (
                            "Glob pattern to match files. Examples: '*.py', '**/*.js', 'src/**/*.{ts,tsx}', "
                            "'tests/**/test_*.py'. Use '**' for recursive search."
                        ),
                    },
                    "path": {
                        "type": "string",
                        "description": (
                            "Base directory to search from (absolute path). Defaults to current working directory if not specified."
                        ),
                    },
                },
                "required": ["pattern"],
            },
        }

    async def __call__(
        self,
        *,
        pattern: str,
        path: str | None = None,
        **kwargs,
    ) -> CLIResult:
        """
        Execute glob pattern search.

        Args:
            pattern: Glob pattern (e.g., "**/*.py", "src/**/*.ts")
            path: Base directory to search from (defaults to cwd)

        Returns:
            CLIResult with list of matching file paths
        """
        try:
            # Determine base path
            if path:
                base_path = Path(path)
                if not base_path.is_absolute():
                    raise ToolError(
                        f"Path must be absolute. Got: {path}. "
                        f"Maybe you meant: {Path.cwd() / path}"
                    )
                if not base_path.exists():
                    raise ToolError(f"Path does not exist: {path}")
                if not base_path.is_dir():
                    raise ToolError(f"Path is not a directory: {path}")
            else:
                base_path = Path.cwd()

            # Execute glob search
            matches = list(base_path.glob(pattern))

            # Filter to files only and sort by modification time (newest first)
            files = [f for f in matches if f.is_file()]
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            # Format output
            if not files:
                output = f"No files found matching pattern '{pattern}' in {base_path}"
            else:
                file_list = "\n".join(str(f) for f in files)
                output = (
                    f"Found {len(files)} file(s) matching '{pattern}' in {base_path}:\n"
                    f"{file_list}"
                )

            return CLIResult(output=output)

        except Exception as e:
            if isinstance(e, ToolError):
                raise
            raise ToolError(f"Glob search failed: {str(e)}") from e
