#!/usr/bin/env python3
"""
Test TodoWrite integration with ProjectManager.

This script tests that TodoWrite automatically creates tasks in ProjectManager.
"""

import asyncio
import json
from pathlib import Path

from computer_use_demo.tools.coding.todo import TodoWriteTool
from computer_use_demo.planning import ProjectManager


async def test_todo_integration():
    """Test TodoWrite integration with ProjectManager."""
    print("=" * 80)
    print("Testing TodoWrite Integration with ProjectManager")
    print("=" * 80)
    print()

    # Clean up any existing test data
    todo_file = Path.cwd() / ".proto_todos.json"
    if todo_file.exists():
        todo_file.unlink()
        print("Cleaned up existing .proto_todos.json")

    # Initialize TodoWrite tool
    todo_tool = TodoWriteTool()
    print("✓ Initialized TodoWrite tool")

    # Test 1: Create initial todos
    print("\n1. Creating initial todos...")
    todos = [
        {
            "content": "Review codebase structure",
            "status": "completed",
            "activeForm": "Reviewing codebase structure",
        },
        {
            "content": "Implement feature X",
            "status": "in_progress",
            "activeForm": "Implementing feature X",
        },
        {
            "content": "Write tests",
            "status": "pending",
            "activeForm": "Writing tests",
        },
    ]

    result = await todo_tool(todos=todos)
    print(result.output)
    print()

    # Test 2: Verify tasks in ProjectManager
    print("2. Verifying tasks in ProjectManager...")
    pm = ProjectManager()

    if not pm.project_exists("agent-session"):
        print("✗ Project 'agent-session' not found!")
        return False

    print("✓ Project 'agent-session' exists")

    task_manager = pm.get_task_manager("agent-session")
    all_tasks = task_manager.get_all_tasks()

    print(f"✓ Found {len(all_tasks)} tasks in ProjectManager")
    print()

    # Display tasks
    for task in all_tasks:
        print(f"  - {task.title}")
        print(f"    Status: {task.status.value}")
        print(f"    Tags: {', '.join(task.tags)}")
        print()

    # Verify task count
    if len(all_tasks) != 3:
        print(f"✗ Expected 3 tasks, got {len(all_tasks)}")
        return False

    # Verify statuses
    task_by_title = {task.title: task for task in all_tasks}

    expected_statuses = {
        "Review codebase structure": "completed",
        "Implement feature X": "in_progress",
        "Write tests": "pending",
    }

    for title, expected_status in expected_statuses.items():
        if title not in task_by_title:
            print(f"✗ Task '{title}' not found in ProjectManager")
            return False

        actual_status = task_by_title[title].status.value
        if actual_status != expected_status:
            print(f"✗ Task '{title}' has status '{actual_status}', expected '{expected_status}'")
            return False

    print("✓ All task statuses match")

    # Test 3: Update todos
    print("\n3. Updating todos (marking 'Implement feature X' as completed)...")
    updated_todos = [
        {
            "content": "Review codebase structure",
            "status": "completed",
            "activeForm": "Reviewing codebase structure",
        },
        {
            "content": "Implement feature X",
            "status": "completed",
            "activeForm": "Implementing feature X",
        },
        {
            "content": "Write tests",
            "status": "in_progress",
            "activeForm": "Writing tests",
        },
    ]

    result = await todo_tool(todos=updated_todos)
    print(result.output)
    print()

    # Test 4: Verify updated status in ProjectManager
    print("4. Verifying updated status in ProjectManager...")
    # Create fresh ProjectManager and TaskManager to reload data
    pm_fresh = ProjectManager()
    task_manager = pm_fresh.get_task_manager("agent-session")
    all_tasks = task_manager.get_all_tasks()
    task_by_title = {task.title: task for task in all_tasks}

    feature_x_task = task_by_title.get("Implement feature X")
    if not feature_x_task:
        print("✗ Could not find 'Implement feature X' task")
        return False

    if feature_x_task.status.value != "completed":
        print(f"✗ 'Implement feature X' status is '{feature_x_task.status.value}', expected 'completed'")
        return False

    print("✓ Task status updated correctly")

    # Test 5: Remove a task from todos
    print("\n5. Removing 'Review codebase structure' from todos...")
    final_todos = [
        {
            "content": "Implement feature X",
            "status": "completed",
            "activeForm": "Implementing feature X",
        },
        {
            "content": "Write tests",
            "status": "in_progress",
            "activeForm": "Writing tests",
        },
    ]

    result = await todo_tool(todos=final_todos)
    print(result.output)
    print()

    # Test 6: Verify removed task is marked as completed
    print("6. Verifying removed task is marked as completed in ProjectManager...")
    # Create fresh ProjectManager and TaskManager to reload data
    pm_fresh2 = ProjectManager()
    task_manager = pm_fresh2.get_task_manager("agent-session")
    all_tasks = task_manager.get_all_tasks()
    task_by_title = {task.title: task for task in all_tasks}

    review_task = task_by_title.get("Review codebase structure")
    if not review_task:
        print("✗ Could not find 'Review codebase structure' task")
        return False

    if review_task.status.value != "completed":
        print(f"✗ Removed task status is '{review_task.status.value}', expected 'completed'")
        return False

    print("✓ Removed task marked as completed")

    print()
    print("=" * 80)
    print("✓ All tests passed!")
    print("=" * 80)
    print()
    print("TodoWrite is now fully integrated with ProjectManager.")
    print("Tasks created via TodoWrite will automatically appear in the dashboard.")

    return True


if __name__ == "__main__":
    success = asyncio.run(test_todo_integration())
    exit(0 if success else 1)
