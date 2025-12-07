#!/usr/bin/env python3
"""Debug script to check what tasks the dashboard sees vs what's in folders."""

from computer_use_demo.planning import ProjectManager

# Get ProjectManager
pm = ProjectManager()

# List all projects
print("=" * 80)
print("All Projects:")
print("=" * 80)
projects = pm.list_projects()
for proj in projects:
    print(f"  - {proj['project_name']} ({proj['slug']})")
print()

# Check monday-clone specifically
print("=" * 80)
print("Monday Clone Project Tasks:")
print("=" * 80)

project_name = "monday-clone"
if pm.project_exists(project_name):
    task_manager = pm.get_task_manager(project_name)

    print(f"Task Manager Type: {type(task_manager).__name__}")
    print()

    all_tasks = task_manager.get_all_tasks()
    print(f"Total tasks: {len(all_tasks)}")
    print()

    for task in all_tasks:
        print(f"  [{task.status.value}] {task.title}")
        print(f"    ID: {task.id}")
        print(f"    Parent: {task.parent_id}")
        print()
else:
    print(f"Project '{project_name}' not found!")
