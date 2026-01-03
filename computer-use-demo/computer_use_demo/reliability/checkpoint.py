"""
Checkpoint system for state persistence and recovery.

Allows saving and restoring task state for recovery from failures.
"""

import json
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Checkpoint:
    """A saved checkpoint of task state."""

    # Unique checkpoint ID
    checkpoint_id: str

    # Task ID this checkpoint belongs to
    task_id: str

    # Current state data
    state: dict[str, Any]

    # When this checkpoint was created
    created_at: float

    # Decisions made up to this point
    decisions: list[dict[str, Any]] = field(default_factory=list)

    # Files modified (with optional diffs)
    modified_files: list[dict[str, Any]] = field(default_factory=list)

    # External calls made
    external_calls: list[dict[str, Any]] = field(default_factory=list)

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert checkpoint to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Checkpoint":
        """Create checkpoint from dictionary."""
        return cls(
            checkpoint_id=data["checkpoint_id"],
            task_id=data["task_id"],
            state=data.get("state", {}),
            created_at=data.get("created_at", time.time()),
            decisions=data.get("decisions", []),
            modified_files=data.get("modified_files", []),
            external_calls=data.get("external_calls", []),
            metadata=data.get("metadata", {}),
        )


class CheckpointManager:
    """
    Manages checkpoints for task recovery.

    Saves checkpoints to disk and allows restoration after failures.
    """

    def __init__(self, checkpoint_dir: str | Path | None = None):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory for storing checkpoints.
                           Defaults to ~/.proto/checkpoints/
        """
        if checkpoint_dir is None:
            checkpoint_dir = Path.home() / ".proto" / "checkpoints"
        self._checkpoint_dir = Path(checkpoint_dir)
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache of current task checkpoints
        self._current_checkpoints: dict[str, Checkpoint] = {}

    def create_checkpoint(
        self,
        task_id: str,
        state: dict[str, Any],
        decisions: list[dict[str, Any]] | None = None,
        modified_files: list[dict[str, Any]] | None = None,
        external_calls: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Checkpoint:
        """
        Create a new checkpoint for a task.

        Args:
            task_id: ID of the task being checkpointed
            state: Current task state
            decisions: List of decisions made
            modified_files: List of files modified
            external_calls: List of external API calls made
            metadata: Additional metadata

        Returns:
            Created Checkpoint object
        """
        checkpoint = Checkpoint(
            checkpoint_id=str(uuid.uuid4()),
            task_id=task_id,
            state=state,
            created_at=time.time(),
            decisions=decisions or [],
            modified_files=modified_files or [],
            external_calls=external_calls or [],
            metadata=metadata or {},
        )

        # Save to memory
        self._current_checkpoints[task_id] = checkpoint

        # Save to disk
        self._save_checkpoint(checkpoint)

        return checkpoint

    def _save_checkpoint(self, checkpoint: Checkpoint) -> Path:
        """Save checkpoint to disk."""
        # Create task-specific directory
        task_dir = self._checkpoint_dir / checkpoint.task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        # Save checkpoint file
        checkpoint_file = task_dir / f"{checkpoint.checkpoint_id}.json"
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint.to_dict(), f, indent=2, default=str)

        # Also save as "latest" for quick access
        latest_file = task_dir / "latest.json"
        with open(latest_file, "w") as f:
            json.dump(checkpoint.to_dict(), f, indent=2, default=str)

        return checkpoint_file

    def get_latest_checkpoint(self, task_id: str) -> Checkpoint | None:
        """
        Get the most recent checkpoint for a task.

        Args:
            task_id: Task ID to get checkpoint for

        Returns:
            Latest Checkpoint or None if not found
        """
        # Check memory cache first
        if task_id in self._current_checkpoints:
            return self._current_checkpoints[task_id]

        # Load from disk
        task_dir = self._checkpoint_dir / task_id
        latest_file = task_dir / "latest.json"

        if latest_file.exists():
            try:
                with open(latest_file, "r") as f:
                    data = json.load(f)
                checkpoint = Checkpoint.from_dict(data)
                self._current_checkpoints[task_id] = checkpoint
                return checkpoint
            except Exception as e:
                print(f"[Checkpoint] Failed to load checkpoint: {e}")

        return None

    def get_all_checkpoints(self, task_id: str) -> list[Checkpoint]:
        """
        Get all checkpoints for a task, ordered by creation time.

        Args:
            task_id: Task ID to get checkpoints for

        Returns:
            List of Checkpoints, oldest first
        """
        task_dir = self._checkpoint_dir / task_id
        if not task_dir.exists():
            return []

        checkpoints = []
        for checkpoint_file in task_dir.glob("*.json"):
            if checkpoint_file.name == "latest.json":
                continue
            try:
                with open(checkpoint_file, "r") as f:
                    data = json.load(f)
                checkpoints.append(Checkpoint.from_dict(data))
            except Exception:
                continue

        # Sort by creation time
        checkpoints.sort(key=lambda c: c.created_at)
        return checkpoints

    def restore_from_checkpoint(self, checkpoint: Checkpoint) -> dict[str, Any]:
        """
        Restore state from a checkpoint.

        Args:
            checkpoint: Checkpoint to restore from

        Returns:
            The restored state dictionary
        """
        # Update memory cache
        self._current_checkpoints[checkpoint.task_id] = checkpoint

        return checkpoint.state.copy()

    def delete_checkpoint(self, task_id: str, checkpoint_id: str) -> bool:
        """
        Delete a specific checkpoint.

        Args:
            task_id: Task ID
            checkpoint_id: Checkpoint ID to delete

        Returns:
            True if deleted, False if not found
        """
        checkpoint_file = self._checkpoint_dir / task_id / f"{checkpoint_id}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            return True
        return False

    def cleanup_old_checkpoints(
        self,
        task_id: str,
        keep_count: int = 10,
        max_age_hours: float = 24.0,
    ) -> int:
        """
        Clean up old checkpoints for a task.

        Args:
            task_id: Task ID to clean up
            keep_count: Minimum number of checkpoints to keep
            max_age_hours: Maximum age in hours for checkpoints

        Returns:
            Number of checkpoints deleted
        """
        checkpoints = self.get_all_checkpoints(task_id)
        if len(checkpoints) <= keep_count:
            return 0

        now = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted = 0

        # Keep the most recent keep_count checkpoints
        for checkpoint in checkpoints[:-keep_count]:
            age = now - checkpoint.created_at
            if age > max_age_seconds:
                if self.delete_checkpoint(task_id, checkpoint.checkpoint_id):
                    deleted += 1

        return deleted

    def add_decision(
        self,
        task_id: str,
        decision: str,
        rationale: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add a decision to the current checkpoint.

        Args:
            task_id: Task ID
            decision: What was decided
            rationale: Why it was decided
            metadata: Additional information
        """
        checkpoint = self.get_latest_checkpoint(task_id)
        if checkpoint:
            checkpoint.decisions.append({
                "decision": decision,
                "rationale": rationale,
                "timestamp": time.time(),
                "metadata": metadata or {},
            })
            self._save_checkpoint(checkpoint)

    def add_modified_file(
        self,
        task_id: str,
        file_path: str,
        operation: str,
        diff: str | None = None,
    ) -> None:
        """
        Record a file modification.

        Args:
            task_id: Task ID
            file_path: Path to modified file
            operation: What was done (create, edit, delete)
            diff: Optional diff of changes
        """
        checkpoint = self.get_latest_checkpoint(task_id)
        if checkpoint:
            checkpoint.modified_files.append({
                "path": file_path,
                "operation": operation,
                "diff": diff,
                "timestamp": time.time(),
            })
            self._save_checkpoint(checkpoint)

    def add_external_call(
        self,
        task_id: str,
        service: str,
        operation: str,
        idempotency_key: str | None = None,
        success: bool = True,
    ) -> None:
        """
        Record an external API call.

        Args:
            task_id: Task ID
            service: Service that was called
            operation: What operation was performed
            idempotency_key: Key for deduplication
            success: Whether the call succeeded
        """
        checkpoint = self.get_latest_checkpoint(task_id)
        if checkpoint:
            checkpoint.external_calls.append({
                "service": service,
                "operation": operation,
                "idempotency_key": idempotency_key,
                "success": success,
                "timestamp": time.time(),
            })
            self._save_checkpoint(checkpoint)


# Global checkpoint manager instance
_checkpoint_manager: CheckpointManager | None = None


def get_checkpoint_manager() -> CheckpointManager:
    """Get the global checkpoint manager instance."""
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager()
    return _checkpoint_manager
