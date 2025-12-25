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
from .task_manager import Task, TaskManager, TaskPriority, TaskStatus


class ProjectManager:
    """
    Manages project planning folder structure and documents.

    Handles:
    - Creating ~/Proto/{project}/ folders (in user's home directory)
    - Checking for existing projects
    - Saving/loading planning documents
    - Managing knowledge base files
    """

    PLANNING_ROOT = Path.home() / "Proto"

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
        Create a new project with standardized folder structure.

        Creates:
        - ~/Proto/{project}/planning/ for planning documents and task management
          - planning/materials/ for source materials and references
          - planning/reports/ for generated reports and internal documentation
        - ~/Proto/{project}/ (root) for the actual project files (code, assets, etc.)

        Additional folders created on-demand:
        - planning/agents/ when specialist plans are added
        - planning/tasks/ when task tree is generated

        Args:
            project_name: Name of the project (will be slugified)

        Returns:
            Path to the planning folder (planning/)
        """
        # Slugify project name
        slug = self._slugify(project_name)

        # Create project root directory
        project_root = self.base_path / slug
        project_root.mkdir(parents=True, exist_ok=True)

        # Create planning/ folder for planning documents and task management
        planning_path = project_root / "planning"
        planning_path.mkdir(parents=True, exist_ok=True)

        # Create standard planning subfolders
        (planning_path / "materials").mkdir(exist_ok=True)
        (planning_path / "reports").mkdir(exist_ok=True)

        # The rest of the project files go directly in project_root
        # Agents will create their own structure (backend/, frontend/, etc.)

        # Other folders created on-demand:
        # - planning/agents/ when specialist plans are added
        # - planning/tasks/ when task tree is generated

        # Create metadata file in planning folder
        metadata = {
            "project_name": project_name,
            "slug": slug,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "status": "active",
            "structure": "standard",  # Standard planning/ folder, rest in root
            "planning_path": str(planning_path),
            "project_root": str(project_root),
        }
        self._save_metadata(planning_path, metadata)

        return planning_path

    def project_exists(self, project_name: str) -> bool:
        """
        Check if a project already exists (simple planning/ or legacy structures).

        Args:
            project_name: Name of the project

        Returns:
            True if project exists
        """
        slug = self._slugify(project_name)
        project_root = self.base_path / slug

        # Check for simple planning/ structure (current)
        simple_planning_path = project_root / "planning"
        if simple_planning_path.exists() and (simple_planning_path / ".project_metadata.json").exists():
            return True

        # Check for old .proto/planning/ structure (backwards compatibility)
        old_planning_path = project_root / ".proto" / "planning"
        if old_planning_path.exists() and (old_planning_path / ".project_metadata.json").exists():
            return True

        # Check for legacy project structure (backwards compatibility)
        if project_root.exists() and (project_root / ".project_metadata.json").exists():
            return True

        return False

    def get_project_path(self, project_name: str) -> Path | None:
        """
        Get path to existing project planning folder.

        Args:
            project_name: Name of the project

        Returns:
            Path to planning folder (planning/) or None if doesn't exist
        """
        slug = self._slugify(project_name)
        project_root = self.base_path / slug

        # Check for simple planning/ structure (current)
        simple_planning_path = project_root / "planning"
        if simple_planning_path.exists() and (simple_planning_path / ".project_metadata.json").exists():
            return simple_planning_path

        # Check for old .proto/planning/ structure (backwards compatibility)
        old_planning_path = project_root / ".proto" / "planning"
        if old_planning_path.exists() and (old_planning_path / ".project_metadata.json").exists():
            return old_planning_path

        # Check for legacy project structure (backwards compatibility)
        if project_root.exists() and (project_root / ".project_metadata.json").exists():
            return project_root

        return None

    def get_project_root(self, project_name: str) -> Path | None:
        """
        Get path to project root folder where agents create project files.

        The project root is where agents create their own structure
        (backend/, frontend/, etc.) - everything except the planning/ folder.

        Args:
            project_name: Name of the project

        Returns:
            Path to project root or None if doesn't exist
        """
        slug = self._slugify(project_name)
        project_root = self.base_path / slug

        if project_root.exists():
            return project_root

        return None

    def list_projects(self) -> list[dict[str, Any]]:
        """
        List all existing projects (simple planning/, old .proto/planning/, and legacy).

        Returns:
            List of project metadata dicts
        """
        if not self.base_path.exists():
            return []

        projects = []
        for project_dir in self.base_path.iterdir():
            if project_dir.is_dir():
                # Check for simple planning/ structure (current)
                simple_metadata_file = project_dir / "planning" / ".project_metadata.json"
                if simple_metadata_file.exists():
                    metadata = json.loads(simple_metadata_file.read_text())
                    projects.append(metadata)
                    continue

                # Check for old .proto/planning/ structure
                old_metadata_file = project_dir / ".proto" / "planning" / ".project_metadata.json"
                if old_metadata_file.exists():
                    metadata = json.loads(old_metadata_file.read_text())
                    projects.append(metadata)
                    continue

                # Check for legacy project
                legacy_metadata_file = project_dir / ".project_metadata.json"
                if legacy_metadata_file.exists():
                    metadata = json.loads(legacy_metadata_file.read_text())
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

    def create_task_tree_from_roadmap(self, project_name: str) -> Optional[Path]:
        """
        Create a TASKS.md file from the roadmap document.

        This file shows the hierarchical task structure with status tracking.

        Args:
            project_name: Name of the project

        Returns:
            Path to TASKS.md or None if roadmap doesn't exist
        """
        # Load roadmap
        roadmap_content = self.load_document(project_name, "roadmap")
        if not roadmap_content:
            return None

        project_path = self.get_project_path(project_name)
        if not project_path:
            return None

        # Get task manager
        task_manager = self.get_task_manager(project_name)
        if not task_manager:
            return None

        # Parse roadmap and extract tasks
        import re

        # Create root project task if it doesn't exist
        root_tasks = task_manager.get_root_tasks()
        if not root_tasks:
            root_task = task_manager.create_task(
                title=project_name,
                description=f"Root project task for {project_name}",
                priority=TaskPriority.HIGH,
            )
        else:
            root_task = root_tasks[0]
            # Clear existing child tasks to avoid duplicates when regenerating
            child_tasks = task_manager.get_children(root_task.id)
            for child in child_tasks:
                task_manager.delete_task(child.id)

        # Parse roadmap for task structure
        lines = roadmap_content.split('\n')
        current_phase = None
        current_phase_task = None
        phase_tasks = {}  # Track phases by title to avoid duplicates

        for line in lines:
            # Match phase headers like "### **Phase 1: Project Setup & Architecture** (Weeks 1-2)"
            phase_match = re.match(r'^###\s+\*\*Phase\s+\d+:\s+(.+?)\*\*\s*\((.+?)\)', line)
            if phase_match:
                phase_title = phase_match.group(1)
                phase_duration = phase_match.group(2)

                # Check if phase already exists (to avoid duplicates in TOC)
                if phase_title not in phase_tasks:
                    # Create phase task
                    current_phase_task = task_manager.create_task(
                        title=phase_title,
                        description=f"Duration: {phase_duration}",
                        priority=TaskPriority.HIGH,
                        parent_id=root_task.id,
                    )
                    phase_tasks[phase_title] = current_phase_task
                else:
                    # Use existing phase task
                    current_phase_task = phase_tasks[phase_title]
                continue

            # Match task items like "- [ ] **Task Name**" (without task ID)
            task_match = re.match(r'^-\s+\[\s*([x ])\s*\]\s+\*\*([^*]+)\*\*', line)
            if task_match and current_phase_task:
                is_done = task_match.group(1).lower() == 'x'
                task_title = task_match.group(2).strip()

                # Create task
                new_task = task_manager.create_task(
                    title=task_title,
                    description="",
                    priority=TaskPriority.MEDIUM,
                    parent_id=current_phase_task.id,
                )

                # Update status if completed
                if is_done:
                    task_manager.update_task(new_task.id, status=TaskStatus.COMPLETED)
                continue

        # Generate TASKS.md from the task tree
        tasks_md = self._generate_tasks_markdown(task_manager, root_task)

        # Save TASKS.md
        tasks_path = project_path / "TASKS.md"
        tasks_path.write_text(tasks_md)

        return tasks_path

    def _generate_tasks_markdown(self, task_manager: TaskManager, root_task: Task, level: int = 0) -> str:
        """Generate markdown for task tree."""
        indent = "  " * level
        status_emoji = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.BLOCKED: "🚫",
        }

        lines = []

        if level == 0:
            lines.append(f"# {root_task.title} - Task Tree")
            lines.append("")
            lines.append("Status Legend: ⏳ Pending | 🔄 In Progress | ✅ Completed | 🚫 Blocked")
            lines.append("")

        emoji = status_emoji.get(root_task.status, "❓")
        lines.append(f"{indent}- {emoji} **{root_task.title}**")
        if root_task.description:
            lines.append(f"{indent}  - {root_task.description}")
        if root_task.assigned_agent:
            lines.append(f"{indent}  - Assigned: {root_task.assigned_agent}")

        # Get children
        children = task_manager.get_children(root_task.id)
        for child in children:
            child_md = self._generate_tasks_markdown(task_manager, child, level + 1)
            lines.append(child_md)

        return "\n".join(lines) if level > 0 else "\n".join(lines)

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

        # Load all shared documents (used by ALL agents - CEO and specialists)
        for doc_type in ["project_overview", "requirements", "technical_spec", "roadmap", "knowledge_base", "decisions"]:
            content = self.load_document(project_name, doc_type)  # type: ignore
            if content:
                context["documents"][doc_type] = content

        # NOTE: Specialist plans removed - all agents now use the same shared planning documents above
        # No need to load agents/ folder - it won't be created for new projects

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
