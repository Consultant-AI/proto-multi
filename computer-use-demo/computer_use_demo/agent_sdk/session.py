"""
Session Management - Persistence and resumption for agent sessions.

Implements Agent SDK's session storage pattern with JSONL transcripts
and CLAUDE.md convention storage.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from anthropic.types.beta import BetaMessageParam


class SessionManager:
    """
    Manages session persistence and resumption.

    Features:
    - JSONL transcript storage (one message per line)
    - CLAUDE.md convention storage and loading
    - Session metadata tracking
    - Automatic session directory management
    """

    def __init__(self, session_id: str | None = None, claude_home: Path | None = None):
        """
        Initialize session manager.

        Args:
            session_id: Unique session ID (generated if None)
            claude_home: Path to .claude directory (defaults to ~/.claude)
        """
        self.session_id = session_id or self._generate_session_id()

        # Determine claude home directory
        if claude_home:
            self.claude_home = Path(claude_home)
        else:
            self.claude_home = Path.home() / ".claude"

        # Session directory
        self.session_dir = self.claude_home / "projects" / f"computer-use-{self.session_id}"
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.transcript_file = self.session_dir / "transcript.jsonl"
        self.conventions_file = self.session_dir / "CLAUDE.md"
        self.metadata_file = self.session_dir / "metadata.json"

        # Project-level CLAUDE.md (in the actual project directory)
        # This is where the tool usage priority guidance lives
        self.project_conventions_file = Path.cwd() / ".claude" / "CLAUDE.md"

        # Initialize metadata
        self._initialize_metadata()

    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return datetime.now().strftime("%Y%m%d-%H%M%S-") + str(uuid.uuid4())[:8]

    def _initialize_metadata(self):
        """Initialize or load session metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "session_id": self.session_id,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "message_count": 0,
                "tool_executions": 0,
            }
            self._save_metadata()

    def _save_metadata(self):
        """Save session metadata"""
        self.metadata["last_updated"] = datetime.now().isoformat()
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def session_exists(self) -> bool:
        """Check if a session transcript exists"""
        return self.transcript_file.exists()

    async def save_session(self, messages: list[BetaMessageParam]):
        """
        Save session messages to JSONL transcript.

        Args:
            messages: List of conversation messages
        """
        # Write all messages to transcript (overwrites previous)
        with open(self.transcript_file, "w") as f:
            for message in messages:
                # Serialize message as JSON line
                json_line = json.dumps(self._serialize_message(message))
                f.write(json_line + "\n")

        # Update metadata
        self.metadata["message_count"] = len(messages)
        self._save_metadata()

    def load_session(self) -> list[BetaMessageParam] | None:
        """
        Load session messages from JSONL transcript.

        Returns:
            List of messages or None if session doesn't exist
        """
        if not self.session_exists():
            return None

        messages: list[BetaMessageParam] = []
        with open(self.transcript_file, "r") as f:
            for line in f:
                if line.strip():
                    message_data = json.loads(line)
                    messages.append(self._deserialize_message(message_data))

        return messages

    def save_conventions(self, conventions: str):
        """
        Save desktop/session conventions to CLAUDE.md.

        Args:
            conventions: Markdown content with conventions and learnings
        """
        with open(self.conventions_file, "w") as f:
            f.write(conventions)

    def load_conventions(self) -> str | None:
        """
        Load conventions from CLAUDE.md.

        Checks two locations in order:
        1. Project-level .claude/CLAUDE.md (tool usage priority guidance)
        2. Session-level CLAUDE.md (session-specific learnings)

        Returns:
            Conventions content or None if file doesn't exist
        """
        # First, try to load project-level conventions (has tool priority guidance)
        if self.project_conventions_file.exists():
            with open(self.project_conventions_file, "r") as f:
                project_conventions = f.read()

            # If session-specific conventions exist, append them
            if self.conventions_file.exists():
                with open(self.conventions_file, "r") as f:
                    session_conventions = f.read()
                return f"{project_conventions}\n\n---\n\n# Session-Specific Learnings\n\n{session_conventions}"

            return project_conventions

        # Fall back to session-only conventions
        if self.conventions_file.exists():
            with open(self.conventions_file, "r") as f:
                return f.read()

        return None

    def append_convention(self, section: str, content: str):
        """
        Append a new convention to CLAUDE.md.

        Args:
            section: Section header (e.g., "Application Launching")
            content: Content to append under the section
        """
        current = self.load_conventions() or "# Desktop Automation Conventions\n\n"

        # Add new section
        new_section = f"\n## {section}\n{content}\n"
        current += new_section

        self.save_conventions(current)

    def record_tool_execution(self, tool_name: str, success: bool):
        """
        Record a tool execution in metadata.

        Args:
            tool_name: Name of the tool executed
            success: Whether execution was successful
        """
        self.metadata["tool_executions"] = self.metadata.get("tool_executions", 0) + 1

        # Track tool-specific stats
        if "tools" not in self.metadata:
            self.metadata["tools"] = {}

        if tool_name not in self.metadata["tools"]:
            self.metadata["tools"][tool_name] = {"executions": 0, "successes": 0, "failures": 0}

        self.metadata["tools"][tool_name]["executions"] += 1
        if success:
            self.metadata["tools"][tool_name]["successes"] += 1
        else:
            self.metadata["tools"][tool_name]["failures"] += 1

        self._save_metadata()

    def get_session_stats(self) -> dict[str, Any]:
        """
        Get session statistics.

        Returns:
            Dictionary with session stats
        """
        return {
            "session_id": self.session_id,
            "created_at": self.metadata.get("created_at"),
            "last_updated": self.metadata.get("last_updated"),
            "message_count": self.metadata.get("message_count", 0),
            "tool_executions": self.metadata.get("tool_executions", 0),
            "tools": self.metadata.get("tools", {}),
        }

    def _serialize_message(self, message: BetaMessageParam) -> dict[str, Any]:
        """
        Serialize a message for JSON storage.

        Args:
            message: Message to serialize

        Returns:
            JSON-serializable dict
        """
        # Handle different message content types
        serialized = {
            "role": message["role"],
            "content": message["content"],
        }

        # Note: BetaMessageParam content can be str or list
        # The JSON encoder will handle this appropriately

        return serialized

    def _deserialize_message(self, data: dict[str, Any]) -> BetaMessageParam:
        """
        Deserialize a message from JSON storage.

        Args:
            data: JSON data to deserialize

        Returns:
            BetaMessageParam message
        """
        # Reconstruct message
        message: BetaMessageParam = {
            "role": data["role"],  # type: ignore
            "content": data["content"],
        }

        return message

    def cleanup_old_sessions(self, max_age_days: int = 30):
        """
        Clean up old session directories.

        Args:
            max_age_days: Maximum age in days to keep sessions
        """
        projects_dir = self.claude_home / "projects"
        if not projects_dir.exists():
            return

        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)

        for session_dir in projects_dir.glob("computer-use-*"):
            if session_dir.is_dir():
                metadata_file = session_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                        created_at = datetime.fromisoformat(metadata.get("created_at", ""))
                        if created_at.timestamp() < cutoff_time:
                            # Delete old session
                            import shutil
                            shutil.rmtree(session_dir)
