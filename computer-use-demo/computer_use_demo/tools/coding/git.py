"""
GitTool: Git operations automation for version control workflows.

Supported commands:
- status: Show working tree status
- diff: Show changes between commits, commit and working tree, etc
- log: Show commit logs
- add: Add file contents to the index
- commit: Record changes to the repository
- branch: List, create, or delete branches
- checkout: Switch branches or restore files
"""

from pathlib import Path
from typing import Any, Literal

from ..base import BaseAnthropicTool, CLIResult, ToolError
from ..run import run


class GitTool(BaseAnthropicTool):
    """
    Git operations tool for automated version control workflows.
    Wraps common git commands with safety checks and better error messages.
    """

    name: Literal["git"] = "git"
    api_type: Literal["custom"] = "custom"

    def to_params(self) -> Any:
        return {
            "name": self.name,
            "description": (
                "Execute git commands for version control. Supports status, diff, log, add, commit, branch, and more. "
                "Use this to check repository state, view changes, and manage commits. "
                "IMPORTANT: Only use safe read-only commands unless explicitly asked to make changes."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "enum": [
                            "status",
                            "diff",
                            "log",
                            "add",
                            "commit",
                            "branch",
                            "checkout",
                            "show",
                            "remote",
                        ],
                        "description": (
                            "Git command to execute. Common commands: "
                            "'status' (see changes), 'diff' (view differences), 'log' (commit history), "
                            "'add' (stage files), 'commit' (save changes), 'branch' (list/create branches)."
                        ),
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Arguments for the git command. Examples: "
                            "For 'diff': ['HEAD', '--stat'] or ['--staged']. "
                            "For 'log': ['-n', '5', '--oneline']. "
                            "For 'add': ['.'] or ['path/to/file']. "
                            "For 'commit': ['-m', 'commit message']."
                        ),
                    },
                    "path": {
                        "type": "string",
                        "description": (
                            "Repository path (absolute). Defaults to current working directory. "
                            "Git commands will be executed in this directory."
                        ),
                    },
                },
                "required": ["command"],
            },
        }

    async def __call__(
        self,
        *,
        command: str,
        args: list[str] | None = None,
        path: str | None = None,
        **kwargs,
    ) -> CLIResult:
        """
        Execute git command.

        Args:
            command: Git command (status, diff, log, add, commit, etc.)
            args: Command arguments
            path: Repository path

        Returns:
            CLIResult with git command output
        """
        try:
            # Validate command
            allowed_commands = [
                "status",
                "diff",
                "log",
                "add",
                "commit",
                "branch",
                "checkout",
                "show",
                "remote",
            ]
            if command not in allowed_commands:
                raise ToolError(
                    f"Command '{command}' not allowed. Allowed commands: {', '.join(allowed_commands)}"
                )

            # Determine repository path
            if path:
                repo_path = Path(path)
                if not repo_path.is_absolute():
                    raise ToolError(
                        f"Path must be absolute. Got: {path}. "
                        f"Maybe you meant: {Path.cwd() / path}"
                    )
                if not repo_path.exists():
                    raise ToolError(f"Path does not exist: {path}")
            else:
                repo_path = Path.cwd()

            # Safety checks for destructive commands
            if command in ["commit", "add", "checkout"]:
                # Warn but allow - user might want these operations
                pass

            # Build git command
            git_cmd = ["git", command]
            if args:
                git_cmd.extend(args)

            # Execute git command in the specified directory
            returncode, stdout, stderr = await run(
                " ".join(f'"{arg}"' if " " in arg else arg for arg in git_cmd),
                cwd=str(repo_path),
            )

            # Format output
            if returncode != 0:
                # Git command failed
                error_msg = stderr.strip() if stderr else "Git command failed"

                # Provide helpful error messages
                if "not a git repository" in error_msg.lower():
                    error_msg += f"\n\nThe directory {repo_path} is not a git repository. "
                    error_msg += "Initialize one with 'git init' or navigate to an existing repository."
                elif "nothing to commit" in error_msg.lower() and command == "commit":
                    error_msg += "\n\nTip: Use 'git add' to stage files before committing."
                elif "no changes added to commit" in error_msg.lower():
                    error_msg += "\n\nTip: Use 'git add <files>' to stage changes, or 'git add .' to stage all changes."

                return CLIResult(error=error_msg)

            # Success - format output
            output = stdout.strip() if stdout else ""

            # Add helpful context for certain commands
            if command == "status" and not output:
                output = "Working tree clean (no changes)"
            elif command == "diff" and not output:
                output = "No differences found"
            elif command == "log" and not output:
                output = "No commits yet"

            # Add command echo for clarity
            cmd_echo = f"git {command}"
            if args:
                cmd_echo += f" {' '.join(args)}"
            full_output = f"$ {cmd_echo}\n{output}"

            return CLIResult(output=full_output)

        except Exception as e:
            if isinstance(e, ToolError):
                raise
            raise ToolError(f"Git command failed: {str(e)}") from e
