"""
Type definitions for the Global CEO Orchestrator.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
import uuid


class TaskPriority(str, Enum):
    """Priority levels for global tasks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Status of a global task."""

    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    WAITING = "waiting"  # Waiting for dependencies
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class TaskDependency:
    """Dependency between tasks."""

    # ID of the task this depends on
    task_id: str

    # Type of dependency
    dependency_type: str = "completion"  # completion, success, data

    # Data key to pass (for data dependencies)
    data_key: str | None = None


@dataclass
class TaskResult:
    """Result of a task execution."""

    # Whether task succeeded
    success: bool

    # Result data
    data: Any = None

    # Error message if failed
    error: str | None = None

    # Execution duration in seconds
    duration: float = 0.0

    # Computer that executed the task
    executed_by: str | None = None

    # Timestamp
    completed_at: datetime = field(default_factory=datetime.utcnow)

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SubTask:
    """A sub-task within a larger global task."""

    # Unique ID
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Parent task ID
    parent_id: str | None = None

    # Sub-task name
    name: str = ""

    # Description
    description: str = ""

    # Status
    status: TaskStatus = TaskStatus.PENDING

    # Assigned computer
    assigned_to: str | None = None

    # Required capabilities (from parent if not set)
    required_capabilities: list[str] = field(default_factory=list)

    # Dependencies on other sub-tasks
    dependencies: list[str] = field(default_factory=list)

    # Result
    result: TaskResult | None = None

    # Order in sequence (for sequential tasks)
    order: int = 0

    # Timeout in seconds
    timeout: float | None = None

    # Created timestamp
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_ready(self, completed_ids: set[str]) -> bool:
        """Check if all dependencies are satisfied."""
        return all(dep in completed_ids for dep in self.dependencies)


@dataclass
class GlobalTask:
    """A task to be executed across the computer network."""

    # Unique task ID
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Task name
    name: str = ""

    # Detailed description
    description: str = ""

    # Priority level
    priority: TaskPriority = TaskPriority.MEDIUM

    # Current status
    status: TaskStatus = TaskStatus.PENDING

    # Required capabilities
    required_capabilities: list[str] = field(default_factory=list)

    # Preferred tags for computer selection
    preferred_tags: list[str] = field(default_factory=list)

    # Task dependencies
    dependencies: list[TaskDependency] = field(default_factory=list)

    # Sub-tasks (after decomposition)
    subtasks: list[SubTask] = field(default_factory=list)

    # Input data for the task
    input_data: dict[str, Any] = field(default_factory=dict)

    # Task result
    result: TaskResult | None = None

    # Assigned computer (if not decomposed)
    assigned_to: str | None = None

    # Who created this task
    created_by: str | None = None

    # Timeout in seconds
    timeout: float = 3600.0  # 1 hour default

    # Maximum retries
    max_retries: int = 3

    # Current retry count
    retry_count: int = 0

    # Created timestamp
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Started timestamp
    started_at: datetime | None = None

    # Completed timestamp
    completed_at: datetime | None = None

    # Custom metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # Callback URL for completion notification
    callback_url: str | None = None

    def is_decomposed(self) -> bool:
        """Check if task has been decomposed into sub-tasks."""
        return len(self.subtasks) > 0

    def get_pending_subtasks(self) -> list[SubTask]:
        """Get sub-tasks that are pending."""
        return [st for st in self.subtasks if st.status == TaskStatus.PENDING]

    def get_ready_subtasks(self) -> list[SubTask]:
        """Get sub-tasks that are ready to run."""
        completed = {
            st.id for st in self.subtasks
            if st.status == TaskStatus.COMPLETED
        }
        return [
            st for st in self.subtasks
            if st.status == TaskStatus.PENDING and st.is_ready(completed)
        ]

    def is_complete(self) -> bool:
        """Check if all sub-tasks are complete."""
        if not self.subtasks:
            return self.status == TaskStatus.COMPLETED

        return all(
            st.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
            for st in self.subtasks
        )

    def has_failed_subtasks(self) -> bool:
        """Check if any sub-tasks have failed."""
        return any(
            st.status == TaskStatus.FAILED
            for st in self.subtasks
        )

    def get_progress(self) -> float:
        """Get task completion progress (0-1)."""
        if not self.subtasks:
            if self.status == TaskStatus.COMPLETED:
                return 1.0
            elif self.status == TaskStatus.RUNNING:
                return 0.5
            return 0.0

        completed = sum(
            1 for st in self.subtasks
            if st.status == TaskStatus.COMPLETED
        )
        return completed / len(self.subtasks)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "required_capabilities": self.required_capabilities,
            "preferred_tags": self.preferred_tags,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress": self.get_progress(),
            "subtask_count": len(self.subtasks),
            "metadata": self.metadata,
        }
