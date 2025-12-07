#!/usr/bin/env python3
"""
Test the folder-based task system with JSON aggregation.

This script verifies:
1. FolderTaskManager creates proper folder structure
2. Tasks are stored as individual folders with task.json, notes.md, files/
3. Subtasks are nested in parent's tasks/ directory
4. project_data.json is automatically generated for root projects
5. project_data.json contains complete task tree and summary
"""

import json
import shutil
from pathlib import Path

from computer_use_demo.planning import ProjectManager, TaskPriority


def test_folder_task_system():
    """Test the complete folder-based task system."""
    print("=" * 80)
    print("Testing Folder-Based Task System with JSON Aggregation")
    print("=" * 80)
    print()

    # Clean up any existing test data
    test_project = "test-folder-system"
    pm = ProjectManager()

    if pm.project_exists(test_project):
        project_path = pm.get_project_path(test_project)
        if project_path and project_path.exists():
            shutil.rmtree(project_path)
            print(f"✓ Cleaned up existing test project")

    # Create project
    print("1. Creating test project...")
    project_path = pm.create_project(test_project)
    print(f"   ✓ Created project at: {project_path}")
    print()

    # Get task manager (should be FolderTaskManager now)
    print("2. Getting FolderTaskManager...")
    task_manager = pm.get_task_manager(test_project)
    print(f"   ✓ Task manager type: {type(task_manager).__name__}")
    print()

    # Create root task
    print("3. Creating root task 'Build WhatsApp Clone'...")
    root_task = task_manager.create_task(
        title="Build WhatsApp Clone",
        description="Complete WhatsApp clone with real-time messaging",
        priority=TaskPriority.HIGH,
        tags=["main-project"]
    )
    print(f"   ✓ Created root task: {root_task.id}")

    # Verify folder structure
    root_folder = project_path / "tasks" / f"build-whatsapp-clone-{root_task.id[:8]}"
    assert root_folder.exists(), "Root task folder should exist"
    assert (root_folder / "task.json").exists(), "task.json should exist"
    assert (root_folder / "notes.md").exists(), "notes.md should exist"
    assert (root_folder / "files").exists(), "files/ directory should exist"
    assert (root_folder / "project_data.json").exists(), "project_data.json should exist"
    print(f"   ✓ Folder structure created: {root_folder.name}")
    print()

    # Create child tasks
    print("4. Creating child tasks...")
    frontend_task = task_manager.create_task(
        title="Build Frontend",
        description="React-based frontend",
        priority=TaskPriority.HIGH,
        parent_id=root_task.id
    )

    backend_task = task_manager.create_task(
        title="Build Backend",
        description="Node.js backend with WebSockets",
        priority=TaskPriority.HIGH,
        parent_id=root_task.id
    )

    print(f"   ✓ Created 'Build Frontend': {frontend_task.id[:8]}")
    print(f"   ✓ Created 'Build Backend': {backend_task.id[:8]}")

    # Verify child folders are nested
    frontend_folder = root_folder / "tasks" / f"build-frontend-{frontend_task.id[:8]}"
    backend_folder = root_folder / "tasks" / f"build-backend-{backend_task.id[:8]}"
    assert frontend_folder.exists(), "Frontend task folder should exist"
    assert backend_folder.exists(), "Backend task folder should exist"
    print(f"   ✓ Child tasks nested in parent's tasks/ directory")
    print()

    # Create grandchild tasks
    print("5. Creating grandchild tasks...")
    components_task = task_manager.create_task(
        title="Create React Components",
        description="Chat, MessageList, UserProfile components",
        priority=TaskPriority.MEDIUM,
        parent_id=frontend_task.id
    )

    routing_task = task_manager.create_task(
        title="Setup React Router",
        description="Configure routing for app",
        priority=TaskPriority.LOW,
        parent_id=frontend_task.id
    )

    print(f"   ✓ Created 'Create React Components': {components_task.id[:8]}")
    print(f"   ✓ Created 'Setup React Router': {routing_task.id[:8]}")

    # Verify grandchild folders
    components_folder = frontend_folder / "tasks" / f"create-react-components-{components_task.id[:8]}"
    assert components_folder.exists(), "Grandchild task folder should exist"
    print(f"   ✓ Grandchild tasks nested properly (3 levels deep)")
    print()

    # Verify project_data.json
    print("6. Verifying project_data.json...")
    project_json = root_folder / "project_data.json"
    assert project_json.exists(), "project_data.json should exist"

    with open(project_json, "r") as f:
        project_data = json.load(f)

    # Check structure
    assert "version" in project_data, "Should have version"
    assert "project_id" in project_data, "Should have project_id"
    assert "project_title" in project_data, "Should have project_title"
    assert "summary" in project_data, "Should have summary"
    assert "task_tree" in project_data, "Should have task_tree"

    print(f"   ✓ project_data.json structure valid")
    print(f"   ✓ Project title: {project_data['project_title']}")
    print(f"   ✓ Total tasks: {project_data['summary']['total_tasks']}")

    # Verify task tree
    task_tree = project_data["task_tree"]
    assert task_tree["title"] == "Build WhatsApp Clone", "Root should be correct"
    assert len(task_tree["children"]) == 2, "Should have 2 children"

    # Find frontend task in tree
    frontend_in_tree = next(c for c in task_tree["children"] if c["title"] == "Build Frontend")
    assert len(frontend_in_tree["children"]) == 2, "Frontend should have 2 grandchildren"

    print(f"   ✓ Task tree properly nested")
    print()

    # Test updating tasks updates JSON
    print("7. Testing automatic JSON updates...")
    task_manager.update_task(frontend_task.id, status=task_manager.get_task(frontend_task.id).status.__class__.IN_PROGRESS)

    # Reload and check
    with open(project_json, "r") as f:
        updated_data = json.load(f)

    assert updated_data["summary"]["in_progress"] == 1, "Should show 1 in_progress task"
    print(f"   ✓ project_data.json auto-updated on task status change")
    print()

    # Test task notes
    print("8. Testing task notes...")
    task_manager.update_task_notes(
        frontend_task.id,
        "# Build Frontend\n\n## Planning\n\n- Use React 18\n- TailwindCSS for styling\n- Socket.io client"
    )

    notes_file = frontend_folder / "notes.md"
    assert notes_file.exists(), "notes.md should exist"
    notes_content = notes_file.read_text()
    assert "React 18" in notes_content, "Notes should contain custom content"
    print(f"   ✓ Task notes saved successfully")
    print()

    # Display final folder structure
    print("9. Final Folder Structure:")
    print("-" * 80)

    def print_tree(path: Path, prefix: str = "", is_last: bool = True):
        """Recursively print directory tree."""
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{path.name}")

        if path.is_dir():
            contents = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            for i, item in enumerate(contents):
                is_last_item = (i == len(contents) - 1)
                extension = "    " if is_last else "│   "
                print_tree(item, prefix + extension, is_last_item)

    print_tree(root_folder)
    print("-" * 80)
    print()

    # Summary
    print("=" * 80)
    print("✓ All Tests Passed!")
    print("=" * 80)
    print()
    print("Summary:")
    print("- Folder-based task storage: WORKING")
    print("- Hierarchical nesting (infinite depth): WORKING")
    print("- Automatic project_data.json generation: WORKING")
    print("- Automatic JSON updates on changes: WORKING")
    print("- Task notes and files: WORKING")
    print()
    print("The system is ready for dashboard integration!")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_folder_task_system()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
