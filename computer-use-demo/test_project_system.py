#!/usr/bin/env python3
"""
Test script for Project Folder System with Knowledge and Task Management.

Tests the integrated project folder system including:
- Project creation and structure
- Task management (create, update, query)
- Knowledge management (add, search, retrieve)
- Project context loading
"""

import shutil
from pathlib import Path

from computer_use_demo.planning import (
    KnowledgeStore,
    KnowledgeType,
    ProjectManager,
    TaskManager,
    TaskPriority,
    TaskStatus,
)


def cleanup_test_project(project_manager: ProjectManager, project_name: str):
    """Clean up test project."""
    project_path = project_manager.get_project_path(project_name)
    if project_path and project_path.exists():
        shutil.rmtree(project_path)
        print(f"✓ Cleaned up test project: {project_path}")


def test_project_creation():
    """Test project folder creation with full structure."""
    print("\n" + "=" * 80)
    print("TEST 1: Project Creation")
    print("=" * 80)

    project_manager = ProjectManager()
    project_name = "Test E-Commerce Platform"

    # Clean up if exists
    cleanup_test_project(project_manager, project_name)

    # Create project
    project_path = project_manager.create_project(project_name)
    print(f"✓ Created project: {project_path}")

    # Verify structure (base directories created by project_manager)
    expected_dirs = [
        "agents",
        "knowledge",
        "data",
        "data/inputs",
        "data/outputs",
        "data/artifacts",
    ]

    for dir_name in expected_dirs:
        dir_path = project_path / dir_name
        assert dir_path.exists(), f"Missing directory: {dir_name}"
        print(f"  ✓ {dir_name}/")

    # Verify metadata
    assert (project_path / ".project_metadata.json").exists()
    print("  ✓ .project_metadata.json")

    print("\n✅ Project creation test PASSED")
    return project_manager, project_name


def test_task_management(project_manager: ProjectManager, project_name: str):
    """Test task management functionality."""
    print("\n" + "=" * 80)
    print("TEST 2: Task Management")
    print("=" * 80)

    project_path = project_manager.get_project_path(project_name)
    task_manager = TaskManager(project_path)

    # Create tasks
    print("\n1. Creating tasks...")
    task1 = task_manager.create_task(
        title="Design database schema",
        description="Design PostgreSQL schema for e-commerce platform",
        priority=TaskPriority.HIGH,
        assigned_agent="senior-developer",
        tags=["database", "backend", "architecture"],
    )
    print(f"  ✓ Created: {task1.title} (ID: {task1.id[:8]})")

    task2 = task_manager.create_task(
        title="Implement user authentication",
        description="JWT-based auth with refresh tokens",
        priority=TaskPriority.CRITICAL,
        assigned_agent="senior-developer",
        tags=["backend", "security"],
    )
    print(f"  ✓ Created: {task2.title} (ID: {task2.id[:8]})")

    task3 = task_manager.create_task(
        title="Create product catalog API",
        description="RESTful API for product CRUD operations",
        priority=TaskPriority.MEDIUM,
        tags=["backend", "api"],
    )
    print(f"  ✓ Created: {task3.title} (ID: {task3.id[:8]})")

    # Add dependency
    print("\n2. Adding dependencies...")
    task_manager.add_dependency(task2.id, task1.id)  # Auth depends on schema
    print(f"  ✓ {task2.title} now depends on {task1.title}")

    # Update task status
    print("\n3. Updating task status...")
    task_manager.mark_task_in_progress(task1.id)
    print(f"  ✓ Marked '{task1.title}' as in progress")

    task_manager.add_task_note(task1.id, "Using UUID for primary keys")
    print(f"  ✓ Added note to '{task1.title}'")

    # Query tasks
    print("\n4. Querying tasks...")
    pending = task_manager.get_pending_tasks()
    print(f"  ✓ Pending tasks: {len(pending)}")
    for task in pending:
        print(f"    - {task.title} [{task.priority.value}]")

    in_progress = task_manager.get_in_progress_tasks()
    print(f"  ✓ In-progress tasks: {len(in_progress)}")
    for task in in_progress:
        print(f"    - {task.title}")

    # Get summary
    print("\n5. Task summary...")
    summary = task_manager.get_task_summary()
    print(f"  ✓ Total: {summary['total']}")
    print(f"  ✓ Pending: {summary['pending']}")
    print(f"  ✓ In Progress: {summary['in_progress']}")
    print(f"  ✓ Completed: {summary['completed']}")

    # Verify persistence
    print("\n6. Testing persistence...")
    task_manager2 = TaskManager(project_path)
    assert len(task_manager2.get_all_tasks()) == 3
    print("  ✓ Tasks persisted and reloaded correctly")

    print("\n✅ Task management test PASSED")
    return task1, task2, task3


def test_knowledge_management(project_manager: ProjectManager, project_name: str):
    """Test knowledge management functionality."""
    print("\n" + "=" * 80)
    print("TEST 3: Knowledge Management")
    print("=" * 80)

    project_path = project_manager.get_project_path(project_name)
    knowledge_store = KnowledgeStore(project_path)

    # Add knowledge entries
    print("\n1. Adding knowledge entries...")
    entry1 = knowledge_store.add_entry(
        title="PostgreSQL for high-volume transactions",
        content="Chose PostgreSQL over MySQL for better ACID compliance and support for JSONB columns. "
        "Will use connection pooling with pgBouncer for scalability.",
        knowledge_type=KnowledgeType.TECHNICAL_DECISION,
        tags=["database", "postgresql", "architecture"],
        source="senior-developer",
    )
    print(f"  ✓ Added: {entry1.title} [{entry1.type.value}]")

    entry2 = knowledge_store.add_entry(
        title="JWT token expiration best practice",
        content="Access tokens should expire in 15 minutes, refresh tokens in 7 days. "
        "Store refresh tokens in httpOnly cookies for security.",
        knowledge_type=KnowledgeType.BEST_PRACTICE,
        tags=["security", "authentication", "jwt"],
        source="security-specialist",
    )
    print(f"  ✓ Added: {entry2.title} [{entry2.type.value}]")

    entry3 = knowledge_store.add_entry(
        title="Always validate input on server side",
        content="Never trust client-side validation. SQL injection attempts were caught during testing. "
        "Use parameterized queries and input sanitization.",
        knowledge_type=KnowledgeType.LESSON_LEARNED,
        tags=["security", "validation", "backend"],
        source="qa-testing",
    )
    print(f"  ✓ Added: {entry3.title} [{entry3.type.value}]")

    entry4 = knowledge_store.add_entry(
        title="E-commerce domain concepts",
        content="Key entities: User, Product, Order, Cart, Payment. "
        "Business rules: inventory management, pricing tiers, discount codes.",
        knowledge_type=KnowledgeType.CONTEXT,
        tags=["domain", "e-commerce"],
    )
    print(f"  ✓ Added: {entry4.title} [{entry4.type.value}]")

    # Search knowledge
    print("\n2. Searching knowledge...")
    results = knowledge_store.search_entries("security")
    print(f"  ✓ Found {len(results)} entries for 'security':")
    for entry in results:
        print(f"    - {entry.title} [{entry.type.value}]")

    results = knowledge_store.search_entries("postgresql")
    print(f"  ✓ Found {len(results)} entries for 'postgresql':")
    for entry in results:
        print(f"    - {entry.title}")

    # Query by type
    print("\n3. Querying by type...")
    tech_decisions = knowledge_store.get_entries_by_type(KnowledgeType.TECHNICAL_DECISION)
    print(f"  ✓ Technical decisions: {len(tech_decisions)}")
    for entry in tech_decisions:
        print(f"    - {entry.title}")

    best_practices = knowledge_store.get_entries_by_type(KnowledgeType.BEST_PRACTICE)
    print(f"  ✓ Best practices: {len(best_practices)}")

    # Get summary
    print("\n4. Knowledge summary...")
    summary = knowledge_store.get_knowledge_summary()
    print(f"  ✓ Total entries: {summary['total']}")
    print(f"  ✓ By type:")
    for type_name, count in summary['by_type'].items():
        if count > 0:
            print(f"    - {type_name}: {count}")

    # Verify persistence
    print("\n5. Testing persistence...")
    knowledge_store2 = KnowledgeStore(project_path)
    assert len(knowledge_store2.get_all_entries()) == 4
    print("  ✓ Knowledge entries persisted and reloaded correctly")

    print("\n✅ Knowledge management test PASSED")
    return entry1, entry2, entry3


def test_integrated_project_context(project_manager: ProjectManager, project_name: str):
    """Test integrated project context loading."""
    print("\n" + "=" * 80)
    print("TEST 4: Integrated Project Context")
    print("=" * 80)

    # Get full project context
    print("\n1. Loading full project context...")
    context = project_manager.get_project_context(project_name)

    assert context["exists"]
    print(f"  ✓ Project exists: {context['metadata']['project_name']}")
    print(f"  ✓ Project path: {context['path']}")

    # Check tasks
    print("\n2. Task context...")
    print(f"  ✓ Total tasks: {context['tasks']['total']}")
    print(f"  ✓ Pending tasks: {len(context['tasks']['pending_tasks'])}")
    for task in context['tasks']['pending_tasks']:
        print(f"    - {task['title']} [{task['priority']}]")
    print(f"  ✓ In-progress tasks: {len(context['tasks']['in_progress_tasks'])}")
    for task in context['tasks']['in_progress_tasks']:
        print(f"    - {task['title']}")

    # Check knowledge
    print("\n3. Knowledge context...")
    print(f"  ✓ Total knowledge entries: {context['knowledge']['total']}")
    print(f"  ✓ Recent entries: {len(context['knowledge']['recent_entries'])}")
    for entry in context['knowledge']['recent_entries']:
        print(f"    - {entry['title']} [{entry['type']}]")

    print("\n✅ Integrated project context test PASSED")


def test_task_knowledge_linking(project_manager: ProjectManager, project_name: str, task1, entry1):
    """Test linking tasks and knowledge."""
    print("\n" + "=" * 80)
    print("TEST 5: Task-Knowledge Linking")
    print("=" * 80)

    knowledge_store = project_manager.get_knowledge_store(project_name)

    # Link knowledge to task
    print("\n1. Linking knowledge to task...")
    knowledge_store.link_to_task(entry1.id, task1.id)
    print(f"  ✓ Linked '{entry1.title}' to task '{task1.title}'")

    # Retrieve linked knowledge
    print("\n2. Retrieving knowledge for task...")
    task_knowledge = knowledge_store.get_entries_for_task(task1.id)
    print(f"  ✓ Found {len(task_knowledge)} knowledge entries for task:")
    for entry in task_knowledge:
        print(f"    - {entry.title}")

    print("\n✅ Task-knowledge linking test PASSED")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("PROJECT FOLDER SYSTEM TEST SUITE")
    print("=" * 80)

    try:
        # Test 1: Project creation
        project_manager, project_name = test_project_creation()

        # Test 2: Task management
        task1, task2, task3 = test_task_management(project_manager, project_name)

        # Test 3: Knowledge management
        entry1, entry2, entry3 = test_knowledge_management(project_manager, project_name)

        # Test 4: Integrated context
        test_integrated_project_context(project_manager, project_name)

        # Test 5: Task-knowledge linking
        test_task_knowledge_linking(project_manager, project_name, task1, entry1)

        # Final summary
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✅")
        print("=" * 80)

        # Display project structure
        print("\nFinal Project Structure:")
        project_path = project_manager.get_project_path(project_name)
        print(f"\n{project_path}/")
        for item in sorted(project_path.rglob("*")):
            if item.is_file():
                rel_path = item.relative_to(project_path)
                indent = "  " * (len(rel_path.parts) - 1)
                print(f"{indent}├── {rel_path.name}")

        # Clean up
        print("\n" + "=" * 80)
        cleanup_choice = input("Clean up test project? (y/n): ")
        if cleanup_choice.lower() == "y":
            cleanup_test_project(project_manager, project_name)
        else:
            print(f"Test project preserved at: {project_path}")

        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(run_all_tests())
