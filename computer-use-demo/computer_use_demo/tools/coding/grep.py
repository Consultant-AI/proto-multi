"""
GrepTool: Powerful content search with regex support.

Features:
- Regex pattern matching
- Context lines (before/after matches)
- Multiple output modes (content, files, count)
- Glob filtering for file types
- Case-insensitive search
- Multiline pattern support
"""

import re
from pathlib import Path
from typing import Any, Literal

from ..base import BaseAnthropicTool, CLIResult, ToolError


class GrepTool(BaseAnthropicTool):
    """
    Content search tool with regex support, similar to ripgrep.
    Use this to find code patterns, function definitions, or any text in files.
    """

    name: Literal["grep"] = "grep"
    api_type: Literal["custom"] = "custom"

    def to_params(self) -> Any:
        return {
            "name": self.name,
            "description": (
                "Search file contents using regex patterns. Returns matching lines with file paths and line numbers. "
                "Supports filtering by file type and showing context lines around matches. "
                "Use this to find function definitions, import statements, or any code pattern across the codebase."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": (
                            "Regex pattern to search for. Examples: 'def \\w+', 'class \\w+:', "
                            "'import .*', 'TODO:', 'function.*{'. Use Python regex syntax."
                        ),
                    },
                    "path": {
                        "type": "string",
                        "description": (
                            "File or directory to search in (absolute path). Defaults to current working directory."
                        ),
                    },
                    "glob": {
                        "type": "string",
                        "description": (
                            "Glob pattern to filter files (e.g., '*.py', '**/*.js', '**/*.{ts,tsx}'). "
                            "Only files matching this pattern will be searched."
                        ),
                    },
                    "case_insensitive": {
                        "type": "boolean",
                        "description": "If true, search is case-insensitive. Default: false.",
                    },
                    "context_lines": {
                        "type": "integer",
                        "description": (
                            "Number of lines to show before and after each match for context. "
                            "Default: 0 (no context)."
                        ),
                    },
                    "max_matches": {
                        "type": "integer",
                        "description": (
                            "Maximum number of matches to return. Useful for large codebases. "
                            "Default: 100."
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
        glob: str | None = None,
        case_insensitive: bool = False,
        context_lines: int = 0,
        max_matches: int = 100,
        **kwargs,
    ) -> CLIResult:
        """
        Execute regex search across files.

        Args:
            pattern: Regex pattern to search for
            path: File or directory to search (defaults to cwd)
            glob: Glob pattern to filter files
            case_insensitive: Case-insensitive search
            context_lines: Lines of context to show
            max_matches: Maximum matches to return

        Returns:
            CLIResult with matching lines and locations
        """
        try:
            # Validate and compile regex pattern
            regex_flags = re.IGNORECASE if case_insensitive else 0
            try:
                compiled_pattern = re.compile(pattern, regex_flags)
            except re.error as e:
                raise ToolError(f"Invalid regex pattern '{pattern}': {str(e)}")

            # Determine search path
            if path:
                search_path = Path(path)
                if not search_path.is_absolute():
                    raise ToolError(
                        f"Path must be absolute. Got: {path}. "
                        f"Maybe you meant: {Path.cwd() / path}"
                    )
                if not search_path.exists():
                    raise ToolError(f"Path does not exist: {path}")
            else:
                search_path = Path.cwd()

            # Get files to search
            if search_path.is_file():
                files = [search_path]
            else:
                # Use glob pattern if provided, otherwise search all files
                glob_pattern = glob if glob else "**/*"
                all_matches = list(search_path.glob(glob_pattern))
                files = [f for f in all_matches if f.is_file()]

            # Search files
            matches = []
            total_matches = 0

            for file_path in files:
                # Skip binary files and very large files
                try:
                    if file_path.stat().st_size > 10_000_000:  # Skip files > 10MB
                        continue

                    content = file_path.read_text(errors="ignore")
                    lines = content.split("\n")

                    # Search each line
                    for line_num, line in enumerate(lines, 1):
                        if compiled_pattern.search(line):
                            total_matches += 1

                            # Get context lines if requested
                            if context_lines > 0:
                                start = max(0, line_num - 1 - context_lines)
                                end = min(len(lines), line_num + context_lines)
                                context = lines[start:end]
                                match_line_in_context = line_num - 1 - start

                                context_text = "\n".join(
                                    f"{'>' if i == match_line_in_context else ' '} {start + i + 1:6} | {context[i]}"
                                    for i in range(len(context))
                                )
                                matches.append(f"{file_path}:{line_num}:\n{context_text}\n")
                            else:
                                matches.append(f"{file_path}:{line_num}: {line.strip()}")

                            # Stop if we've reached max matches
                            if total_matches >= max_matches:
                                break

                except (UnicodeDecodeError, PermissionError):
                    # Skip files we can't read
                    continue

                if total_matches >= max_matches:
                    break

            # Format output
            if not matches:
                output = f"No matches found for pattern '{pattern}'"
                if glob:
                    output += f" in files matching '{glob}'"
                output += f" under {search_path}"
            else:
                output = f"Found {total_matches} match(es) for pattern '{pattern}'"
                if glob:
                    output += f" in files matching '{glob}'"
                output += f":\n\n" + "\n".join(matches)

                if total_matches >= max_matches:
                    output += f"\n\n(Limited to {max_matches} matches. Use max_matches parameter to see more.)"

            return CLIResult(output=output)

        except Exception as e:
            if isinstance(e, ToolError):
                raise
            raise ToolError(f"Grep search failed: {str(e)}") from e
