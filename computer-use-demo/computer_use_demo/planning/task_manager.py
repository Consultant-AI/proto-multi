"""
Task Management System for Project Tracking.

This module provides task management capabilities for projects, enabling
agents to create, track, update, and complete tasks throughout project execution.

Tasks are stored in projects/{project}/planning/tasks.json as the single source of truth.
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import shutil


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task:
    """Represents a project task."""

    def __init__(
        self,
        title: str,
        description: str = "",
        status: TaskStatus = TaskStatus.PENDING,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assigned_agent: Optional[str] = None,
        dependencies: Optional[list[str]] = None,
        task_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        tags: Optional[list[str]] = None,
        notes: Optional[list[dict[str, str]]] = None,
        metadata: Optional[dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ):
        """
        Initialize a task.

        Args:
            title: Task title
            description: Detailed task description
            status: Current task status
            priority: Task priority
            assigned_agent: Agent responsible for the task
            dependencies: List of task IDs this task depends on
            task_id: Unique task identifier (auto-generated if not provided)
            created_at: ISO timestamp when task was created
            updated_at: ISO timestamp when task was last updated
            completed_at: ISO timestamp when task was completed
            tags: List of tags for categorization
            notes: List of note entries (timestamp + text)
            metadata: Additional metadata dictionary
            parent_id: ID of parent task/project (None for root-level tasks)
        """
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = TaskStatus(status) if isinstance(status, str) else status
        self.priority = TaskPriority(priority) if isinstance(priority, str) else priority
        self.assigned_agent = assigned_agent
        self.dependencies = dependencies or []
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or self.created_at
        self.completed_at = completed_at
        self.tags = tags or []
        self.notes = notes or []
        self.metadata = metadata or {}
        self.parent_id = parent_id

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "assigned_agent": self.assigned_agent,
            "dependencies": self.dependencies,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "tags": self.tags,
            "notes": self.notes,
            "metadata": self.metadata,
            "parent_id": self.parent_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Create task from dictionary."""
        return cls(
            task_id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", TaskStatus.PENDING),
            priority=data.get("priority", TaskPriority.MEDIUM),
            assigned_agent=data.get("assigned_agent"),
            dependencies=data.get("dependencies", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            completed_at=data.get("completed_at"),
            tags=data.get("tags", []),
            notes=data.get("notes", []),
            metadata=data.get("metadata", {}),
            parent_id=data.get("parent_id"),
        )

    def add_note(self, text: str) -> None:
        """Add a timestamped note to the task."""
        self.notes.append({"timestamp": datetime.utcnow().isoformat(), "text": text})
        self.updated_at = datetime.utcnow().isoformat()

    def update_status(self, status: TaskStatus) -> None:
        """Update task status with timestamp."""
        self.status = status
        self.updated_at = datetime.utcnow().isoformat()
        if status == TaskStatus.COMPLETED:
            self.completed_at = self.updated_at

    # Specification Workflow Methods (Auto-Claude inspired)

    def start_specification(self) -> None:
        """Initialize specification phase for this task."""
        if "implementation_plan" not in self.metadata:
            self.metadata["implementation_plan"] = {}

        self.metadata["implementation_plan"]["spec_status"] = "in_progress"
        self.metadata["implementation_plan"]["spec_started_at"] = datetime.utcnow().isoformat()
        self.metadata["implementation_plan"]["specification"] = {
            "context": "",
            "acceptance_criteria": [],
            "implementation_checklist": [],
            "notes": []
        }
        self.updated_at = datetime.utcnow().isoformat()

    def update_specification(
        self,
        context: Optional[str] = None,
        acceptance_criteria: Optional[list[str]] = None,
        checklist: Optional[list[str]] = None,
        notes: Optional[str] = None
    ) -> None:
        """Update specification details."""
        if "implementation_plan" not in self.metadata:
            self.start_specification()

        spec = self.metadata["implementation_plan"]["specification"]

        if context is not None:
            spec["context"] = context
        if acceptance_criteria is not None:
            spec["acceptance_criteria"] = acceptance_criteria
        if checklist is not None:
            spec["implementation_checklist"] = checklist
        if notes is not None:
            spec["notes"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "text": notes
            })

        self.updated_at = datetime.utcnow().isoformat()

    def complete_specification(self) -> None:
        """Mark specification phase as complete."""
        if "implementation_plan" not in self.metadata:
            self.start_specification()

        self.metadata["implementation_plan"]["spec_status"] = "completed"
        self.metadata["implementation_plan"]["spec_completed_at"] = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

    def start_implementation(self) -> None:
        """Mark task as starting implementation phase."""
        if "implementation_plan" not in self.metadata:
            self.metadata["implementation_plan"] = {}

        self.metadata["implementation_plan"]["started_at"] = datetime.utcnow().isoformat()
        if "commits" not in self.metadata["implementation_plan"]:
            self.metadata["implementation_plan"]["commits"] = []
        if "test_results" not in self.metadata["implementation_plan"]:
            self.metadata["implementation_plan"]["test_results"] = []

        self.updated_at = datetime.utcnow().isoformat()

    def add_commit(self, commit_hash: str, message: str) -> None:
        """Track a git commit for this task."""
        if "implementation_plan" not in self.metadata:
            self.metadata["implementation_plan"] = {}
        if "commits" not in self.metadata["implementation_plan"]:
            self.metadata["implementation_plan"]["commits"] = []

        self.metadata["implementation_plan"]["commits"].append({
            "hash": commit_hash,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow().isoformat()

    def add_test_result(self, test_name: str, passed: bool, details: str = "") -> None:
        """Track test results for this task."""
        if "implementation_plan" not in self.metadata:
            self.metadata["implementation_plan"] = {}
        if "test_results" not in self.metadata["implementation_plan"]:
            self.metadata["implementation_plan"]["test_results"] = []

        self.metadata["implementation_plan"]["test_results"].append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow().isoformat()

    def get_spec_status(self) -> str:
        """Get current specification status."""
        if "implementation_plan" not in self.metadata:
            return "not_started"
        return self.metadata["implementation_plan"].get("spec_status", "not_started")

    def __repr__(self) -> str:
        """String representation of task."""
        return f"Task(id={self.id[:8]}, title={self.title}, status={self.status.value})"


class TaskManager:
    """Manages tasks for a project."""

    def __init__(self, project_path: Path):
        """
        Initialize task manager for a project.

        Args:
            project_path: Path to project PLANNING directory (already points to projects/{project}/planning/)
        """
        self.project_path = Path(project_path)
        self.tasks_file = self.project_path / "tasks.json"
        self.tasks: dict[str, Task] = {}
        self._load_tasks()

    def _load_tasks(self) -> None:
        """Load tasks from disk."""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, "r") as f:
                    data = json.load(f)
                    self.tasks = {
                        task_id: Task.from_dict(task_data)
                        for task_id, task_data in data.get("tasks", {}).items()
                    }
            except Exception as e:
                print(f"Warning: Failed to load tasks: {e}")
                self.tasks = {}
        else:
            self.tasks = {}

    def _save_tasks(self) -> None:
        """Save tasks to disk."""
        # Ensure project path exists (should already exist as it's the planning folder)
        self.project_path.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "updated_at": datetime.utcnow().isoformat(),
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
        }
        with open(self.tasks_file, "w") as f:
            json.dump(data, f, indent=2)

        # Generate the task board HTML file
        self._generate_board_html()

    def _generate_board_html(self) -> None:
        """Generate the task board HTML file with embedded task data."""
        board_file = self.project_path / "board.html"
        template_path = Path(__file__).parent / "task_board_template.html"

        if not template_path.exists():
            return

        # Read template
        template_content = template_path.read_text()

        # Prepare task data for embedding
        tasks_data = {
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()}
        }

        # Embed task data as a script tag before the closing </head>
        data_script = f'<script>window.TASKS_DATA = {json.dumps(tasks_data)};</script>\n</head>'
        html_content = template_content.replace('</head>', data_script)

        # Write the board file
        board_file.write_text(html_content)

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        assigned_agent: Optional[str] = None,
        dependencies: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        parent_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> Task:
        """
        Create a new task.

        Args:
            title: Task title
            description: Task description
            priority: Task priority
            assigned_agent: Agent to assign task to
            dependencies: List of task IDs this task depends on
            tags: Task tags
            metadata: Additional metadata
            parent_id: ID of parent task/project
            task_id: Optional custom task ID (auto-generated UUID if not provided)

        Returns:
            Created task
        """
        task = Task(
            title=title,
            description=description,
            priority=priority,
            assigned_agent=assigned_agent,
            dependencies=dependencies,
            tags=tags,
            metadata=metadata,
            parent_id=parent_id,
            task_id=task_id,
        )
        self.tasks[task.id] = task
        self._save_tasks()
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks."""
        return list(self.tasks.values())

    def get_tasks_by_status(self, status: TaskStatus) -> list[Task]:
        """Get tasks with specific status."""
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_agent(self, agent: str) -> list[Task]:
        """Get tasks assigned to specific agent."""
        return [task for task in self.tasks.values() if task.assigned_agent == agent]

    def get_tasks_by_tag(self, tag: str) -> list[Task]:
        """Get tasks with specific tag."""
        return [task for task in self.tasks.values() if tag in task.tags]

    def get_pending_tasks(self) -> list[Task]:
        """Get all pending tasks."""
        return self.get_tasks_by_status(TaskStatus.PENDING)

    def get_in_progress_tasks(self) -> list[Task]:
        """Get all in-progress tasks."""
        return self.get_tasks_by_status(TaskStatus.IN_PROGRESS)

    def get_completed_tasks(self) -> list[Task]:
        """Get all completed tasks."""
        return self.get_tasks_by_status(TaskStatus.COMPLETED)

    def get_blocked_tasks(self) -> list[Task]:
        """Get all blocked tasks."""
        return self.get_tasks_by_status(TaskStatus.BLOCKED)

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assigned_agent: Optional[str] = None,
        add_tags: Optional[list[str]] = None,
        remove_tags: Optional[list[str]] = None,
    ) -> Optional[Task]:
        """
        Update task fields.

        Args:
            task_id: ID of task to update
            title: New title
            description: New description
            status: New status
            priority: New priority
            assigned_agent: New assigned agent
            add_tags: Tags to add
            remove_tags: Tags to remove

        Returns:
            Updated task or None if not found
        """
        task = self.get_task(task_id)
        if not task:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.update_status(status)
        if priority is not None:
            task.priority = priority
        if assigned_agent is not None:
            task.assigned_agent = assigned_agent
        if add_tags:
            task.tags.extend([tag for tag in add_tags if tag not in task.tags])
        if remove_tags:
            task.tags = [tag for tag in task.tags if tag not in remove_tags]

        task.updated_at = datetime.utcnow().isoformat()
        self._save_tasks()
        return task

    def add_task_note(self, task_id: str, note: str) -> Optional[Task]:
        """Add note to task."""
        task = self.get_task(task_id)
        if task:
            task.add_note(note)
            self._save_tasks()
        return task

    def mark_task_complete(self, task_id: str) -> Optional[Task]:
        """Mark task as completed."""
        return self.update_task(task_id, status=TaskStatus.COMPLETED)

    def mark_task_in_progress(self, task_id: str) -> Optional[Task]:
        """Mark task as in progress."""
        return self.update_task(task_id, status=TaskStatus.IN_PROGRESS)

    def mark_task_blocked(self, task_id: str, reason: Optional[str] = None) -> Optional[Task]:
        """Mark task as blocked."""
        task = self.update_task(task_id, status=TaskStatus.BLOCKED)
        if task and reason:
            task.add_note(f"BLOCKED: {reason}")
            self._save_tasks()
        return task

    def add_dependency(self, task_id: str, depends_on_task_id: str) -> bool:
        """
        Add dependency between tasks.

        Args:
            task_id: Task that depends on another
            depends_on_task_id: Task that must be completed first

        Returns:
            True if dependency added, False otherwise
        """
        task = self.get_task(task_id)
        if not task or depends_on_task_id not in self.tasks:
            return False

        if depends_on_task_id not in task.dependencies:
            task.dependencies.append(depends_on_task_id)
            task.updated_at = datetime.utcnow().isoformat()
            self._save_tasks()
        return True

    def can_start_task(self, task_id: str) -> bool:
        """Check if task can be started (all dependencies completed)."""
        task = self.get_task(task_id)
        if not task:
            return False

        for dep_id in task.dependencies:
            dep_task = self.get_task(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    def get_task_summary(self) -> dict[str, Any]:
        """Get summary statistics of tasks."""
        all_tasks = self.get_all_tasks()
        return {
            "total": len(all_tasks),
            "pending": len(self.get_pending_tasks()),
            "in_progress": len(self.get_in_progress_tasks()),
            "completed": len(self.get_completed_tasks()),
            "blocked": len(self.get_blocked_tasks()),
            "by_priority": {
                "low": len([t for t in all_tasks if t.priority == TaskPriority.LOW]),
                "medium": len([t for t in all_tasks if t.priority == TaskPriority.MEDIUM]),
                "high": len([t for t in all_tasks if t.priority == TaskPriority.HIGH]),
                "critical": len([t for t in all_tasks if t.priority == TaskPriority.CRITICAL]),
            },
        }

    def get_children(self, parent_id: str) -> list[Task]:
        """Get all direct children of a task, sorted by creation time."""
        children = [task for task in self.tasks.values() if task.parent_id == parent_id]
        # Sort by created_at to preserve task creation order
        return sorted(children, key=lambda t: t.created_at)

    def get_root_tasks(self) -> list[Task]:
        """Get all root-level tasks (tasks with no parent), sorted by creation time."""
        root_tasks = [task for task in self.tasks.values() if task.parent_id is None]
        # Sort by created_at to preserve task creation order
        return sorted(root_tasks, key=lambda t: t.created_at)

    def get_task_tree(self) -> list[dict[str, Any]]:
        """
        Get tasks organized in a tree structure.

        Returns:
            List of root tasks with their children nested
        """
        def build_tree(task: Task) -> dict[str, Any]:
            children = self.get_children(task.id)
            return {
                "task": task.to_dict(),
                "children": [build_tree(child) for child in children],
            }

        return [build_tree(task) for task in self.get_root_tasks()]
