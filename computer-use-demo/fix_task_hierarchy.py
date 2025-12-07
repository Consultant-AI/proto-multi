#!/usr/bin/env python3
"""
Fix task hierarchy - flatten all TodoWrite tasks to be root-level.
"""

from computer_use_demo.planning import ProjectManager

def fix_project_tasks(project_name: str):
    """Remove parent relationships from all TodoWrite tasks in a project."""
    print(f"Fixing tasks in project: {project_name}")
    print("=" * 80)

    pm = ProjectManager()

    if not pm.project_exists(project_name):
        print(f"❌ Project '{project_name}' does not exist")
        return

    task_manager = pm.get_task_manager(project_name)
    all_tasks = task_manager.get_all_tasks()

    # Find all TodoWrite tasks with parents
    todowrite_tasks_with_parents = []
    for task in all_tasks:
        if task.tags and "todowrite" in task.tags and task.parent_id is not None:
            todowrite_tasks_with_parents.append(task)

    if not todowrite_tasks_with_parents:
        print("✅ No TodoWrite tasks with parents found - nothing to fix")
        return

    print(f"Found {len(todowrite_tasks_with_parents)} TodoWrite tasks with parents:")
    for task in todowrite_tasks_with_parents:
        print(f"  - {task.title} (parent: {task.parent_id})")

    print()
    print("Flattening task hierarchy...")

    # Remove parent relationships
    for task in todowrite_tasks_with_parents:
        # Directly modify the task's parent_id
        task.parent_id = None

        # Save the updated task
        folder_path = task_manager.task_folders.get(task.id)
        if folder_path:
            task_json = folder_path / "task.json"
            import json
            with open(task_json, "w") as f:
                json.dump(task.to_dict(), f, indent=2)

        # Update the in-memory task
        task_manager.tasks[task.id] = task

        print(f"  ✅ Removed parent from: {task.title}")

    # Update the project_data.json files
    from computer_use_demo.planning import FolderTaskManager
    if isinstance(task_manager, FolderTaskManager):
        # Get all root tasks and regenerate their project_data.json
        root_tasks = task_manager.get_root_tasks()
        for root_task in root_tasks:
            task_manager._save_project_json(root_task.id)
        print(f"  ✅ Updated project_data.json files")

    print()
    print("=" * 80)
    print("✅ Task hierarchy fixed!")
    print()

    # Verify
    all_tasks = task_manager.get_all_tasks()
    todowrite_tasks = [t for t in all_tasks if t.tags and "todowrite" in t.tags]

    print(f"Summary:")
    print(f"  Total TodoWrite tasks: {len(todowrite_tasks)}")
    print(f"  Root-level tasks: {sum(1 for t in todowrite_tasks if t.parent_id is None)}")
    print(f"  Child tasks: {sum(1 for t in todowrite_tasks if t.parent_id is not None)}")


if __name__ == "__main__":
    # Fix monday-clone project
    fix_project_tasks("monday-clone")
