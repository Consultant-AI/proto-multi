"""
Folder-based Task Management System.

This module provides a file-system based approach to task management where:
- Each task/project is a folder
- Subtasks are nested folders within parent task folders
- Each folder contains task.json, notes.md, and optional files/
- Dashboard displays as folder/file tree browser
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .task_manager import Task, TaskManager, TaskPriority, TaskStatus


def sanitize_folder_name(name: str) -> str:
    """
    Sanitize task title for use as folder name.

    Args:
        name: Task title

    Returns:
        Sanitized folder name
    """
    # Replace spaces with hyphens, remove special chars
    sanitized = name.lower().replace(" ", "-")
    # Keep only alphanumeric, hyphens, and underscores
    sanitized = "".join(c for c in sanitized if c.isalnum() or c in "-_")
    return sanitized[:100]  # Limit length


class FolderTaskManager(TaskManager):
    """
    Task manager that uses folder structure for storage.

    Each task is stored as:
    - Folder named after task (sanitized)
    - task.json inside folder with metadata
    - notes.md for planning notes
    - files/ for additional files
    - tasks/ for subtasks
    """

    def __init__(self, project_path: Path):
        """
        Initialize folder-based task manager.

        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.tasks_root = self.project_path / "tasks"
        self.tasks: dict[str, Task] = {}
        self.task_folders: dict[str, Path] = {}  # Maps task_id to folder path
        self._load_tasks()

    def _get_task_folder_path(self, task_id: str) -> Optional[Path]:
        """Get folder path for a task by ID."""
        return self.task_folders.get(task_id)

    def _load_task_from_folder(self, folder_path: Path, parent_id: Optional[str] = None) -> Optional[Task]:
        """
        Load task from folder.

        Args:
            folder_path: Path to task folder
            parent_id: ID of parent task

        Returns:
            Task instance or None if invalid
        """
        task_json = folder_path / "task.json"
        if not task_json.exists():
            return None

        try:
            with open(task_json, "r") as f:
                data = json.load(f)

            # Override parent_id from folder structure
            data["parent_id"] = parent_id

            task = Task.from_dict(data)
            self.tasks[task.id] = task
            self.task_folders[task.id] = folder_path

            # Recursively load subtasks
            subtasks_dir = folder_path / "tasks"
            if subtasks_dir.exists() and subtasks_dir.is_dir():
                for subtask_folder in sorted(subtasks_dir.iterdir()):
                    if subtask_folder.is_dir():
                        self._load_task_from_folder(subtask_folder, parent_id=task.id)

            return task
        except Exception as e:
            print(f"Warning: Failed to load task from {folder_path}: {e}")
            return None

    def _load_tasks(self) -> None:
        """Load all tasks from folder structure."""
        self.tasks = {}
        self.task_folders = {}

        if not self.tasks_root.exists():
            return

        # Load root-level tasks
        for task_folder in sorted(self.tasks_root.iterdir()):
            if task_folder.is_dir():
                self._load_task_from_folder(task_folder, parent_id=None)

    def _save_task_to_folder(self, task: Task) -> Path:
        """
        Save task to folder.

        Args:
            task: Task to save

        Returns:
            Path to task folder
        """
        # Determine folder path
        if task.id in self.task_folders:
            folder_path = self.task_folders[task.id]
        else:
            # Create new folder
            folder_name = f"{sanitize_folder_name(task.title)}-{task.id[:8]}"

            if task.parent_id:
                # Subtask - put in parent's tasks/ directory
                parent_folder = self.task_folders.get(task.parent_id)
                if not parent_folder:
                    raise ValueError(f"Parent task {task.parent_id} not found")
                folder_path = parent_folder / "tasks" / folder_name
            else:
                # Root task
                folder_path = self.tasks_root / folder_name

            self.task_folders[task.id] = folder_path

        # Create folder
        folder_path.mkdir(parents=True, exist_ok=True)

        # Save task.json
        task_json = folder_path / "task.json"
        with open(task_json, "w") as f:
            json.dump(task.to_dict(), f, indent=2)

        # Create notes.md if it doesn't exist
        notes_file = folder_path / "notes.md"
        if not notes_file.exists():
            notes_file.write_text(f"# {task.title}\n\n## Notes\n\n")

        # Create files/ directory if it doesn't exist
        files_dir = folder_path / "files"
        files_dir.mkdir(exist_ok=True)

        return folder_path

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
    ) -> Task:
        """
        Create a new task with folder structure.

        Args:
            title: Task title
            description: Task description
            priority: Task priority
            assigned_agent: Agent to assign task to
            dependencies: List of task IDs this task depends on
            tags: Task tags
            metadata: Additional metadata
            parent_id: ID of parent task/project

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
        )

        self.tasks[task.id] = task
        self._save_task_to_folder(task)

        # Update project JSON for the root project
        root_id = self._get_root_task_id(task.id)
        self._save_project_json(root_id)

        return task

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
        Update task fields and save to folder.

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

        # Handle title change - need to rename folder
        old_folder = None
        if title is not None and title != task.title:
            old_folder = self.task_folders.get(task_id)
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

        # Save to folder
        new_folder = self._save_task_to_folder(task)

        # If title changed, move folder
        if old_folder and old_folder != new_folder and old_folder.exists():
            shutil.move(str(old_folder), str(new_folder))
            self.task_folders[task_id] = new_folder

        # Update project JSON for the root project
        root_id = self._get_root_task_id(task_id)
        self._save_project_json(root_id)

        return task

    def delete_task(self, task_id: str) -> bool:
        """
        Delete task and its folder.

        Args:
            task_id: ID of task to delete

        Returns:
            True if deleted, False if not found
        """
        task = self.get_task(task_id)
        if not task:
            return False

        # Get root task ID before deleting (for updating project JSON)
        root_id = self._get_root_task_id(task_id)
        is_root = (root_id == task_id)

        # Delete all children first
        children = self.get_children(task_id)
        for child in children:
            self.delete_task(child.id)

        # Delete folder
        folder_path = self.task_folders.get(task_id)
        if folder_path and folder_path.exists():
            shutil.rmtree(folder_path)

        # Remove from memory
        del self.tasks[task_id]
        if task_id in self.task_folders:
            del self.task_folders[task_id]

        # Update project JSON (unless we deleted the root itself)
        if not is_root:
            self._save_project_json(root_id)

        return True

    def get_task_files(self, task_id: str) -> list[Path]:
        """
        Get all files in task's files/ directory.

        Args:
            task_id: ID of task

        Returns:
            List of file paths
        """
        folder_path = self.task_folders.get(task_id)
        if not folder_path:
            return []

        files_dir = folder_path / "files"
        if not files_dir.exists():
            return []

        return list(files_dir.iterdir())

    def add_task_file(self, task_id: str, filename: str, content: bytes) -> Optional[Path]:
        """
        Add file to task's files/ directory.

        Args:
            task_id: ID of task
            filename: Name of file
            content: File content

        Returns:
            Path to created file or None if task not found
        """
        folder_path = self.task_folders.get(task_id)
        if not folder_path:
            return None

        files_dir = folder_path / "files"
        files_dir.mkdir(exist_ok=True)

        file_path = files_dir / filename
        file_path.write_bytes(content)

        return file_path

    def get_task_notes(self, task_id: str) -> Optional[str]:
        """
        Get task notes content.

        Args:
            task_id: ID of task

        Returns:
            Notes content or None if not found
        """
        folder_path = self.task_folders.get(task_id)
        if not folder_path:
            return None

        notes_file = folder_path / "notes.md"
        if not notes_file.exists():
            return ""

        return notes_file.read_text()

    def update_task_notes(self, task_id: str, content: str) -> bool:
        """
        Update task notes.

        Args:
            task_id: ID of task
            content: New notes content

        Returns:
            True if updated, False if task not found
        """
        folder_path = self.task_folders.get(task_id)
        if not folder_path:
            return False

        notes_file = folder_path / "notes.md"
        notes_file.write_text(content)

        return True

    def _build_task_tree_dict(self, task: Task) -> dict[str, Any]:
        """
        Build task tree dictionary recursively.

        Args:
            task: Task to build tree for

        Returns:
            Dict with task data and all children nested
        """
        task_dict = task.to_dict()

        # Get children
        children = self.get_children(task.id)
        if children:
            task_dict["children"] = [self._build_task_tree_dict(child) for child in children]
        else:
            task_dict["children"] = []

        return task_dict

    def _save_project_json(self, root_task_id: str) -> None:
        """
        Save aggregated JSON file for a root project.

        Creates project_data.json in the root project folder containing
        all task data for that project and its subtasks.

        Args:
            root_task_id: ID of root task/project
        """
        task = self.get_task(root_task_id)
        if not task or task.parent_id is not None:
            # Not a root task
            return

        folder_path = self.task_folders.get(root_task_id)
        if not folder_path:
            return

        # Build complete tree
        tree_data = self._build_task_tree_dict(task)

        # Create project summary
        all_descendants = self._get_all_descendants(root_task_id)

        project_data = {
            "version": "1.0",
            "project_id": root_task_id,
            "project_title": task.title,
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "summary": {
                "total_tasks": len(all_descendants) + 1,  # +1 for root
                "completed": sum(1 for t in all_descendants if t.status == TaskStatus.COMPLETED) + (1 if task.status == TaskStatus.COMPLETED else 0),
                "in_progress": sum(1 for t in all_descendants if t.status == TaskStatus.IN_PROGRESS) + (1 if task.status == TaskStatus.IN_PROGRESS else 0),
                "pending": sum(1 for t in all_descendants if t.status == TaskStatus.PENDING) + (1 if task.status == TaskStatus.PENDING else 0),
                "blocked": sum(1 for t in all_descendants if t.status == TaskStatus.BLOCKED) + (1 if task.status == TaskStatus.BLOCKED else 0),
            },
            "task_tree": tree_data,
        }

        # Save to project_data.json in root folder
        project_json = folder_path / "project_data.json"
        with open(project_json, "w") as f:
            json.dump(project_data, f, indent=2)

    def _get_all_descendants(self, task_id: str) -> list[Task]:
        """
        Get all descendant tasks recursively.

        Args:
            task_id: ID of parent task

        Returns:
            List of all descendant tasks
        """
        descendants = []
        children = self.get_children(task_id)

        for child in children:
            descendants.append(child)
            descendants.extend(self._get_all_descendants(child.id))

        return descendants

    def _get_root_task_id(self, task_id: str) -> str:
        """
        Get the root task ID for a given task.

        Walks up the parent chain to find the root.

        Args:
            task_id: ID of task

        Returns:
            ID of root task
        """
        task = self.get_task(task_id)
        if not task:
            return task_id

        # Walk up the parent chain
        while task.parent_id is not None:
            parent = self.get_task(task.parent_id)
            if not parent:
                break
            task = parent

        return task.id

    def save_all_project_jsons(self) -> None:
        """
        Save project_data.json for all root projects.

        Call this after any task modification to keep JSON files in sync.
        """
        root_tasks = self.get_root_tasks()
        for task in root_tasks:
            self._save_project_json(task.id)
