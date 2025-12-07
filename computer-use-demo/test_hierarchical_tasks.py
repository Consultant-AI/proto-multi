#!/usr/bin/env python3
"""
Test hierarchical task creation with intelligent parent detection.

This script demonstrates how TodoWrite automatically creates parent-child
relationships based on task context.
"""

import asyncio
import json
from pathlib import Path

from computer_use_demo.tools.coding.todo import TodoWriteTool
from computer_use_demo.planning import ProjectManager


async def test_hierarchical_tasks():
    """Test hierarchical task creation."""
    print("=" * 80)
    print("Testing Hierarchical Task Creation with Intelligent Parent Detection")
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
    print()

    # Test 1: Create a root task
    print("1. Creating root task 'Build WhatsApp Clone'...")
    todos = [
        {
            "content": "Build WhatsApp Clone",
            "status": "in_progress",
            "activeForm": "Building WhatsApp Clone",
        },
    ]

    result = await todo_tool(todos=todos)
    print(result.output)
    print()

    # Test 2: Add child tasks while parent is in_progress
    print("2. Adding child tasks while parent is in_progress...")
    todos = [
        {
            "content": "Build WhatsApp Clone",
            "status": "in_progress",
            "activeForm": "Building WhatsApp Clone",
        },
        {
            "content": "Set up React project",
            "status": "in_progress",
            "activeForm": "Setting up React project",
        },
        {
            "content": "Design database schema",
            "status": "pending",
            "activeForm": "Designing database schema",
        },
    ]

    result = await todo_tool(todos=todos)
    print(result.output)
    print()

    # Test 3: Add grandchild tasks
    print("3. Adding grandchild tasks (nested deeper)...")
    todos = [
        {
            "content": "Build WhatsApp Clone",
            "status": "in_progress",
            "activeForm": "Building WhatsApp Clone",
        },
        {
            "content": "Set up React project",
            "status": "completed",
            "activeForm": "Setting up React project",
        },
        {
            "content": "Install dependencies",
            "status": "completed",
            "activeForm": "Installing dependencies",
        },
        {
            "content": "Configure webpack",
            "status": "in_progress",
            "activeForm": "Configuring webpack",
        },
        {
            "content": "Design database schema",
            "status": "pending",
            "activeForm": "Designing database schema",
        },
    ]

    result = await todo_tool(todos=todos)
    print(result.output)
    print()

    # Test 4: Verify in ProjectManager
    print("4. Verifying hierarchical structure in ProjectManager...")
    pm = ProjectManager()
    project_name = "agent-session"  # or detect active project

    if not pm.project_exists(project_name):
        print(f"✗ Project '{project_name}' not found!")
        return False

    task_manager = pm.get_task_manager(project_name)
    task_tree = task_manager.get_task_tree()

    print(f"✓ Found task tree with {len(task_tree)} root tasks")
    print()

    # Display tree structure
    def print_tree(nodes, indent=0):
        """Recursively print task tree."""
        for node in nodes:
            task = node["task"]
            prefix = "  " * indent + "└─ " if indent > 0 else ""
            status_icon = {
                "completed": "✅",
                "in_progress": "🔄",
                "pending": "⏳",
            }.get(task["status"], "❓")

            print(f"{prefix}{status_icon} {task['title']} ({task['status']})")

            # Print children recursively
            if node["children"]:
                print_tree(node["children"], indent + 1)

    print("Task Tree Structure:")
    print("-" * 80)
    print_tree(task_tree)
    print("-" * 80)
    print()

    # Test 5: Verify parent-child relationships
    print("5. Verifying parent-child relationships...")

    # Get all tasks
    all_tasks = task_manager.get_all_tasks()
    tasks_by_title = {task.title: task for task in all_tasks}

    # Check specific relationships
    checks = [
        ("Set up React project", "Build WhatsApp Clone"),
        ("Install dependencies", "Set up React project"),
        ("Configure webpack", "Set up React project"),
    ]

    all_passed = True
    for child_title, expected_parent_title in checks:
        child_task = tasks_by_title.get(child_title)
        if not child_task:
            print(f"✗ Task '{child_title}' not found")
            all_passed = False
            continue

        if not child_task.parent_id:
            print(f"✗ Task '{child_title}' has no parent (expected '{expected_parent_title}')")
            all_passed = False
            continue

        parent_task = task_manager.get_task(child_task.parent_id)
        if not parent_task:
            print(f"✗ Parent task not found for '{child_title}'")
            all_passed = False
            continue

        if parent_task.title != expected_parent_title:
            print(
                f"✗ Task '{child_title}' parent is '{parent_task.title}', "
                f"expected '{expected_parent_title}'"
            )
            all_passed = False
        else:
            print(f"✓ Task '{child_title}' → parent '{expected_parent_title}'")

    print()

    if all_passed:
        print("=" * 80)
        print("✓ All hierarchical tests passed!")
        print("=" * 80)
        print()
        print("Summary:")
        print("- TodoWrite now automatically detects parent-child relationships")
        print("- Tasks following an in_progress or completed task become its children")
        print("- This creates natural hierarchical task structures")
        print("- Dashboard will display tasks in tree view with expand/collapse")
    else:
        print("=" * 80)
        print("✗ Some tests failed")
        print("=" * 80)

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_hierarchical_tasks())
    exit(0 if success else 1)
