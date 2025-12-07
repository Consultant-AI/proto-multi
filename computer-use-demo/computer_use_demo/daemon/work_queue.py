"""
Work Queue System for Continuous Multi-Agent Operation.

Provides priority-based work queue with persistence for autonomous task processing.
"""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from ..logging import get_logger


class WorkStatus(str, Enum):
    """Status of a work item."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkPriority(str, Enum):
    """Priority level for work items."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def value_score(self) -> int:
        """Return numeric score for sorting."""
        return {"low": 1, "medium": 2, "high": 3, "critical": 4}[self.value]


class WorkItem:
    """
    Work item for agent execution.

    Represents a unit of work that can be assigned to and executed by an agent.
    """

    def __init__(
        self,
        description: str,
        priority: WorkPriority = WorkPriority.MEDIUM,
        project_name: Optional[str] = None,
        assigned_agent: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        work_id: Optional[str] = None,
        status: WorkStatus = WorkStatus.PENDING,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        result: Optional[str] = None,
        error: Optional[str] = None,
        retry_count: int = 0,
        max_retries: int = 3,
    ):
        """
        Initialize work item.

        Args:
            description: Human-readable description of work
            priority: Priority level
            project_name: Associated project (if any)
            assigned_agent: Agent assigned to this work
            context: Additional context data
            work_id: Unique identifier
            status: Current status
            created_at: Creation timestamp
            updated_at: Last update timestamp
            started_at: Start timestamp
            completed_at: Completion timestamp
            result: Result of work execution
            error: Error message if failed
            retry_count: Number of retry attempts
            max_retries: Maximum retry attempts
        """
        self.id = work_id or str(uuid4())
        self.description = description
        self.priority = priority
        self.project_name = project_name
        self.assigned_agent = assigned_agent
        self.context = context or {}
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at
        self.started_at = started_at
        self.completed_at = completed_at
        self.result = result
        self.error = error
        self.retry_count = retry_count
        self.max_retries = max_retries

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority.value,
            "project_name": self.project_name,
            "assigned_agent": self.assigned_agent,
            "context": self.context,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkItem":
        """Create from dictionary."""
        return cls(
            description=data["description"],
            priority=WorkPriority(data["priority"]),
            project_name=data.get("project_name"),
            assigned_agent=data.get("assigned_agent"),
            context=data.get("context", {}),
            work_id=data["id"],
            status=WorkStatus(data["status"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            result=data.get("result"),
            error=data.get("error"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
        )

    def can_retry(self) -> bool:
        """Check if work item can be retried."""
        return self.retry_count < self.max_retries


class WorkQueue:
    """
    Priority-based work queue with persistence.

    Manages work items for autonomous agent execution with priority ordering
    and persistent storage.
    """

    def __init__(self, queue_path: Optional[Path] = None):
        """
        Initialize work queue.

        Args:
            queue_path: Path to queue storage file (defaults to .proto/daemon/work_queue.json)
        """
        self.logger = get_logger()

        if queue_path is None:
            base_path = Path.home() / ".proto" / "daemon"
            base_path.mkdir(parents=True, exist_ok=True)
            queue_path = base_path / "work_queue.json"

        self.queue_path = Path(queue_path)
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)

        self.items: dict[str, WorkItem] = {}
        self._load_queue()

    def _load_queue(self):
        """Load queue from disk."""
        if not self.queue_path.exists():
            return

        try:
            with open(self.queue_path, "r") as f:
                data = json.load(f)
                for item_data in data.get("items", []):
                    item = WorkItem.from_dict(item_data)
                    self.items[item.id] = item

            self.logger.log_event(
                event_type="work_queue_loaded",
                session_id="work-queue",
                data={"count": len(self.items)},
            )
        except Exception as e:
            self.logger.log_event(
                event_type="work_queue_load_error",
                session_id="work-queue",
                data={"error": str(e)},
            )

    def _save_queue(self):
        """Save queue to disk."""
        try:
            data = {
                "items": [item.to_dict() for item in self.items.values()],
                "updated_at": datetime.now().isoformat(),
            }

            with open(self.queue_path, "w") as f:
                json.dump(data, f, indent=2)

            self.logger.log_event(
                event_type="work_queue_saved",
                session_id="work-queue",
                data={"count": len(self.items)},
            )
        except Exception as e:
            self.logger.log_event(
                event_type="work_queue_save_error",
                session_id="work-queue",
                data={"error": str(e)},
            )

    def add_work(
        self,
        description: str,
        priority: WorkPriority = WorkPriority.MEDIUM,
        project_name: Optional[str] = None,
        assigned_agent: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> WorkItem:
        """
        Add work item to queue.

        Args:
            description: Description of work
            priority: Priority level
            project_name: Associated project
            assigned_agent: Specific agent to assign to
            context: Additional context

        Returns:
            Created work item
        """
        item = WorkItem(
            description=description,
            priority=priority,
            project_name=project_name,
            assigned_agent=assigned_agent,
            context=context,
        )

        self.items[item.id] = item
        self._save_queue()

        self.logger.log_event(
            event_type="work_added",
            session_id="work-queue",
            data={
                "work_id": item.id,
                "priority": priority.value,
                "project": project_name,
            },
        )

        return item

    def get_next_work(
        self,
        agent_name: Optional[str] = None,
        project_name: Optional[str] = None,
    ) -> Optional[WorkItem]:
        """
        Get next work item from queue.

        Args:
            agent_name: Filter by assigned agent
            project_name: Filter by project

        Returns:
            Highest priority pending work item, or None
        """
        # Filter pending items
        pending = [
            item for item in self.items.values()
            if item.status == WorkStatus.PENDING
        ]

        # Apply filters
        if agent_name:
            pending = [item for item in pending if item.assigned_agent == agent_name]
        if project_name:
            pending = [item for item in pending if item.project_name == project_name]

        if not pending:
            return None

        # Sort by priority (highest first), then by creation time (oldest first)
        pending.sort(
            key=lambda x: (-x.priority.value_score(), x.created_at)
        )

        return pending[0]

    def mark_assigned(self, work_id: str, agent_name: str):
        """Mark work item as assigned to agent."""
        if work_id not in self.items:
            return

        item = self.items[work_id]
        item.status = WorkStatus.ASSIGNED
        item.assigned_agent = agent_name
        item.updated_at = datetime.now().isoformat()

        self._save_queue()

        self.logger.log_event(
            event_type="work_assigned",
            session_id="work-queue",
            data={"work_id": work_id, "agent": agent_name},
        )

    def mark_in_progress(self, work_id: str):
        """Mark work item as in progress."""
        if work_id not in self.items:
            return

        item = self.items[work_id]
        item.status = WorkStatus.IN_PROGRESS
        item.started_at = datetime.now().isoformat()
        item.updated_at = item.started_at

        self._save_queue()

        self.logger.log_event(
            event_type="work_started",
            session_id="work-queue",
            data={"work_id": work_id},
        )

    def mark_completed(self, work_id: str, result: Optional[str] = None):
        """Mark work item as completed."""
        if work_id not in self.items:
            return

        item = self.items[work_id]
        item.status = WorkStatus.COMPLETED
        item.completed_at = datetime.now().isoformat()
        item.updated_at = item.completed_at
        item.result = result

        self._save_queue()

        self.logger.log_event(
            event_type="work_completed",
            session_id="work-queue",
            data={"work_id": work_id},
        )

    def mark_failed(self, work_id: str, error: str, retry: bool = True):
        """
        Mark work item as failed.

        Args:
            work_id: Work item ID
            error: Error message
            retry: Whether to retry if possible
        """
        if work_id not in self.items:
            return

        item = self.items[work_id]
        item.error = error
        item.retry_count += 1
        item.updated_at = datetime.now().isoformat()

        # Retry if allowed
        if retry and item.can_retry():
            item.status = WorkStatus.PENDING
            item.assigned_agent = None  # Allow reassignment

            self.logger.log_event(
                event_type="work_retry",
                session_id="work-queue",
                data={
                    "work_id": work_id,
                    "retry_count": item.retry_count,
                    "error": error,
                },
            )
        else:
            item.status = WorkStatus.FAILED

            self.logger.log_event(
                event_type="work_failed",
                session_id="work-queue",
                data={"work_id": work_id, "error": error},
            )

        self._save_queue()

    def get_work_by_id(self, work_id: str) -> Optional[WorkItem]:
        """Get work item by ID."""
        return self.items.get(work_id)

    def get_work_by_status(self, status: WorkStatus) -> list[WorkItem]:
        """Get all work items with given status."""
        return [item for item in self.items.values() if item.status == status]

    def get_work_by_project(self, project_name: str) -> list[WorkItem]:
        """Get all work items for project."""
        return [
            item for item in self.items.values()
            if item.project_name == project_name
        ]

    def get_pending_work(self) -> list[WorkItem]:
        """Get all pending work items."""
        return self.get_work_by_status(WorkStatus.PENDING)

    def get_queue_summary(self) -> dict[str, Any]:
        """Get summary of queue state."""
        summary = {
            "total": len(self.items),
            "by_status": {},
            "by_priority": {},
        }

        # Count by status
        for status in WorkStatus:
            count = len([i for i in self.items.values() if i.status == status])
            summary["by_status"][status.value] = count

        # Count by priority (pending only)
        for priority in WorkPriority:
            count = len([
                i for i in self.items.values()
                if i.status == WorkStatus.PENDING and i.priority == priority
            ])
            summary["by_priority"][priority.value] = count

        return summary

    def clear_completed(self, older_than_hours: int = 24):
        """
        Clear completed work items older than specified hours.

        Args:
            older_than_hours: Only clear items completed this many hours ago
        """
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        cutoff_iso = cutoff.isoformat()

        to_remove = []
        for work_id, item in self.items.items():
            if (
                item.status == WorkStatus.COMPLETED
                and item.completed_at
                and item.completed_at < cutoff_iso
            ):
                to_remove.append(work_id)

        for work_id in to_remove:
            del self.items[work_id]

        if to_remove:
            self._save_queue()

            self.logger.log_event(
                event_type="work_queue_cleared",
                session_id="work-queue",
                data={"cleared_count": len(to_remove)},
            )
