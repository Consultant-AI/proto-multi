"""
Project Structure Manager for Proto Planning System.

Manages planning folder creation, document persistence, and
knowledge base file management.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .documents import DocumentType, PlanningDocuments
from .folder_task_manager import FolderTaskManager
from .knowledge_store import KnowledgeStore
from .task_manager import TaskManager


class ProjectManager:
    """
    Manages project planning folder structure and documents.

    Handles:
    - Creating .proto/planning/{project}/ folders
    - Checking for existing projects
    - Saving/loading planning documents
    - Managing knowledge base files
    """

    PLANNING_ROOT = Path.cwd() / ".proto" / "planning"

    def __init__(self, base_path: Path | None = None):
        """
        Initialize project manager.

        Args:
            base_path: Optional custom base path (default: cwd/.proto/planning)
        """
        self.base_path = base_path or self.PLANNING_ROOT
        self._task_managers: dict[str, TaskManager] = {}
        self._knowledge_stores: dict[str, KnowledgeStore] = {}

    @property
    def planning_root(self) -> Path:
        """Get the planning root path."""
        return self.base_path

    def slugify_project_name(self, project_name: str) -> str:
        """Public method to slugify project names (used by tools)."""
        return self._slugify(project_name)

    def create_project(self, project_name: str) -> Path:
        """
        Create a new project planning folder.

        Args:
            project_name: Name of the project (will be slugified)

        Returns:
            Path to the created project folder
        """
        # Slugify project name
        slug = self._slugify(project_name)

        # Create project directory
        project_path = self.base_path / slug
        project_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (project_path / "agents").mkdir(exist_ok=True)
        (project_path / "knowledge").mkdir(exist_ok=True)
        (project_path / "data").mkdir(exist_ok=True)
        (project_path / "data" / "inputs").mkdir(exist_ok=True)
        (project_path / "data" / "outputs").mkdir(exist_ok=True)
        (project_path / "data" / "artifacts").mkdir(exist_ok=True)

        # Create metadata file
        metadata = {
            "project_name": project_name,
            "slug": slug,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "status": "active",
        }
        self._save_metadata(project_path, metadata)

        return project_path

    def project_exists(self, project_name: str) -> bool:
        """
        Check if a project already exists.

        Args:
            project_name: Name of the project

        Returns:
            True if project exists
        """
        slug = self._slugify(project_name)
        project_path = self.base_path / slug
        return project_path.exists() and (project_path / ".project_metadata.json").exists()

    def get_project_path(self, project_name: str) -> Path | None:
        """
        Get path to existing project.

        Args:
            project_name: Name of the project

        Returns:
            Path to project or None if doesn't exist
        """
        slug = self._slugify(project_name)
        project_path = self.base_path / slug
        if self.project_exists(project_name):
            return project_path
        return None

    def list_projects(self) -> list[dict[str, Any]]:
        """
        List all existing projects.

        Returns:
            List of project metadata dicts
        """
        if not self.base_path.exists():
            return []

        projects = []
        for project_dir in self.base_path.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / ".project_metadata.json"
                if metadata_file.exists():
                    metadata = json.loads(metadata_file.read_text())
                    projects.append(metadata)

        # Sort by updated_at (most recent first)
        projects.sort(key=lambda p: p.get("updated_at", ""), reverse=True)
        return projects

    def save_document(
        self, project_name: str, doc_type: DocumentType, content: str, specialist: str | None = None
    ) -> Path:
        """
        Save a planning document to the project.

        Args:
            project_name: Name of the project
            doc_type: Type of document
            content: Document content (markdown)
            specialist: For specialist plans, the specialist name

        Returns:
            Path to saved document
        """
        # Get or create project
        project_path = self.get_project_path(project_name)
        if not project_path:
            project_path = self.create_project(project_name)

        # Get template to determine filename
        template = PlanningDocuments.get_template(doc_type)
        filename = template.filename

        # Handle specialist plans
        if doc_type == "specialist_plan" and specialist:
            filename = filename.format(specialist=specialist)

        # Write document
        doc_path = project_path / filename
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(content)

        # Update project metadata
        self._update_metadata(project_path)

        return doc_path

    def load_document(
        self, project_name: str, doc_type: DocumentType, specialist: str | None = None
    ) -> str | None:
        """
        Load a planning document from the project.

        Args:
            project_name: Name of the project
            doc_type: Type of document
            specialist: For specialist plans, the specialist name

        Returns:
            Document content or None if doesn't exist
        """
        project_path = self.get_project_path(project_name)
        if not project_path:
            return None

        # Get template to determine filename
        template = PlanningDocuments.get_template(doc_type)
        filename = template.filename

        # Handle specialist plans
        if doc_type == "specialist_plan" and specialist:
            filename = filename.format(specialist=specialist)

        doc_path = project_path / filename
        if doc_path.exists():
            return doc_path.read_text()

        return None

    def get_task_manager(self, project_name: str) -> Optional[TaskManager]:
        """
        Get task manager for a project.

        Args:
            project_name: Name of the project

        Returns:
            TaskManager instance or None if project doesn't exist
        """
        project_path = self.get_project_path(project_name)
        if not project_path:
            return None

        # Cache task managers
        if project_name not in self._task_managers:
            self._task_managers[project_name] = FolderTaskManager(project_path)

        return self._task_managers[project_name]

    def get_knowledge_store(self, project_name: str) -> Optional[KnowledgeStore]:
        """
        Get knowledge store for a project.

        Args:
            project_name: Name of the project

        Returns:
            KnowledgeStore instance or None if project doesn't exist
        """
        project_path = self.get_project_path(project_name)
        if not project_path:
            return None

        # Cache knowledge stores
        if project_name not in self._knowledge_stores:
            self._knowledge_stores[project_name] = KnowledgeStore(project_path)

        return self._knowledge_stores[project_name]

    def get_project_context(self, project_name: str) -> dict[str, Any]:
        """
        Get comprehensive context for a project.

        Loads all planning documents, metadata, tasks, and knowledge.

        Args:
            project_name: Name of the project

        Returns:
            Dict with all project information
        """
        project_path = self.get_project_path(project_name)
        if not project_path:
            return {"exists": False}

        metadata = self._load_metadata(project_path)

        context = {
            "exists": True,
            "metadata": metadata,
            "path": str(project_path),
            "documents": {},
            "tasks": {},
            "knowledge": {},
        }

        # Load all documents
        for doc_type in ["project_overview", "requirements", "technical_spec", "roadmap", "knowledge_base", "decisions"]:
            content = self.load_document(project_name, doc_type)  # type: ignore
            if content:
                context["documents"][doc_type] = content

        # Load specialist plans
        agent_plans_dir = project_path / "agents"
        if agent_plans_dir.exists():
            specialist_plans = {}
            for plan_file in agent_plans_dir.glob("*_plan.md"):
                specialist = plan_file.stem.replace("_plan", "")
                specialist_plans[specialist] = plan_file.read_text()
            if specialist_plans:
                context["documents"]["specialist_plans"] = specialist_plans

        # Load task summary
        task_manager = self.get_task_manager(project_name)
        if task_manager:
            context["tasks"] = task_manager.get_task_summary()
            context["tasks"]["pending_tasks"] = [
                {"id": t.id, "title": t.title, "priority": t.priority.value}
                for t in task_manager.get_pending_tasks()[:5]  # Top 5 pending
            ]
            context["tasks"]["in_progress_tasks"] = [
                {"id": t.id, "title": t.title, "assigned_agent": t.assigned_agent}
                for t in task_manager.get_in_progress_tasks()
            ]

        # Load knowledge summary
        knowledge_store = self.get_knowledge_store(project_name)
        if knowledge_store:
            context["knowledge"] = knowledge_store.get_knowledge_summary()
            # Add recent knowledge entries
            all_entries = knowledge_store.get_all_entries()
            if all_entries:
                # Sort by updated_at, most recent first
                sorted_entries = sorted(
                    all_entries,
                    key=lambda e: e.updated_at,
                    reverse=True
                )
                context["knowledge"]["recent_entries"] = [
                    {"id": e.id, "title": e.title, "type": e.type.value}
                    for e in sorted_entries[:5]  # Top 5 recent
                ]

        return context

    def save_knowledge_base_item(
        self, project_name: str, item_name: str, content: dict[str, Any]
    ) -> None:
        """
        Save a knowledge base item (for reusable knowledge).

        Args:
            project_name: Name of the project
            item_name: Name of the knowledge item
            content: Knowledge content as dict
        """
        project_path = self.get_project_path(project_name)
        if not project_path:
            project_path = self.create_project(project_name)

        kb_dir = project_path / "knowledge"
        kb_dir.mkdir(exist_ok=True)

        kb_file = kb_dir / f"{self._slugify(item_name)}.json"
        kb_file.write_text(json.dumps(content, indent=2))

        self._update_metadata(project_path)

    def load_knowledge_base_items(self, project_name: str) -> dict[str, Any]:
        """
        Load all knowledge base items for a project.

        Args:
            project_name: Name of the project

        Returns:
            Dict mapping item names to content
        """
        project_path = self.get_project_path(project_name)
        if not project_path:
            return {}

        kb_dir = project_path / "knowledge"
        if not kb_dir.exists():
            return {}

        items = {}
        for kb_file in kb_dir.glob("*.json"):
            item_name = kb_file.stem
            items[item_name] = json.loads(kb_file.read_text())

        return items

    def _slugify(self, text: str) -> str:
        """
        Convert text to slug (lowercase, hyphens, alphanumeric).

        Args:
            text: Text to slugify

        Returns:
            Slugified text
        """
        import re

        # Convert to lowercase
        slug = text.lower()

        # Replace spaces and underscores with hyphens
        slug = re.sub(r"[\s_]+", "-", slug)

        # Remove non-alphanumeric characters (except hyphens)
        slug = re.sub(r"[^a-z0-9-]", "", slug)

        # Remove multiple consecutive hyphens
        slug = re.sub(r"-+", "-", slug)

        # Remove leading/trailing hyphens
        slug = slug.strip("-")

        return slug

    def _save_metadata(self, project_path: Path, metadata: dict[str, Any]) -> None:
        """Save project metadata."""
        metadata_file = project_path / ".project_metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))

    def _load_metadata(self, project_path: Path) -> dict[str, Any]:
        """Load project metadata."""
        metadata_file = project_path / ".project_metadata.json"
        if metadata_file.exists():
            return json.loads(metadata_file.read_text())
        return {}

    def _update_metadata(self, project_path: Path) -> None:
        """Update project metadata with current timestamp."""
        metadata = self._load_metadata(project_path)
        metadata["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self._save_metadata(project_path, metadata)
