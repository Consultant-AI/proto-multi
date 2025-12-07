#!/usr/bin/env python3
"""
Migration script: Convert existing JSON-based tasks to folder structure.

This script migrates projects from the old TaskManager (single tasks.json file)
to the new FolderTaskManager (folder-based storage).

Usage:
    python3 migrate_tasks_to_folders.py [--dry-run] [--backup]

Options:
    --dry-run: Show what would be migrated without making changes
    --backup: Create backup of existing tasks.json files
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

from computer_use_demo.planning import ProjectManager, FolderTaskManager
from computer_use_demo.planning.task_manager import Task


def migrate_project(project_path: Path, dry_run: bool = False, backup: bool = False):
    """
    Migrate a single project from JSON to folder structure.

    Args:
        project_path: Path to project directory
        dry_run: If True, don't make actual changes
        backup: If True, backup existing tasks.json

    Returns:
        Dict with migration statistics
    """
    tasks_json = project_path / "tasks.json"

    if not tasks_json.exists():
        return {"status": "skipped", "reason": "no tasks.json found"}

    # Load existing tasks
    try:
        with open(tasks_json, "r") as f:
            data = json.load(f)
            task_data = data.get("tasks", {})
    except Exception as e:
        return {"status": "error", "reason": f"failed to read tasks.json: {e}"}

    if not task_data:
        return {"status": "skipped", "reason": "no tasks to migrate"}

    print(f"  Found {len(task_data)} tasks to migrate")

    if dry_run:
        print("  [DRY RUN] Would migrate tasks:")
        for task_id, task_dict in task_data.items():
            print(f"    - {task_dict['title']} (ID: {task_id[:8]})")
        return {"status": "dry_run", "count": len(task_data)}

    # Backup if requested
    if backup:
        backup_path = project_path / f"tasks.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(tasks_json, backup_path)
        print(f"  Created backup: {backup_path.name}")

    # Create FolderTaskManager instance
    folder_manager = FolderTaskManager(project_path)

    # Build tasks from dict
    tasks = {task_id: Task.from_dict(task_dict) for task_id, task_dict in task_data.items()}

    # Migrate tasks in order: root tasks first, then their children
    migrated_count = 0
    root_tasks = [t for t in tasks.values() if t.parent_id is None]

    def migrate_task_tree(task: Task):
        """Recursively migrate task and its children."""
        nonlocal migrated_count

        # Save task to folder structure
        folder_manager.tasks[task.id] = task
        folder_manager._save_task_to_folder(task)
        migrated_count += 1
        print(f"    Migrated: {task.title}")

        # Migrate children
        children = [t for t in tasks.values() if t.parent_id == task.id]
        for child in children:
            migrate_task_tree(child)

    # Migrate all root tasks and their subtrees
    for root_task in root_tasks:
        migrate_task_tree(root_task)

    # Generate project_data.json files for all root projects
    folder_manager.save_all_project_jsons()
    print(f"  Generated project_data.json files")

    # Remove old tasks.json
    tasks_json.unlink()
    print(f"  Removed old tasks.json")

    return {"status": "success", "count": migrated_count}


def main():
    """Run migration for all projects."""
    parser = argparse.ArgumentParser(description="Migrate tasks from JSON to folder structure")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without making changes")
    parser.add_argument("--backup", action="store_true", help="Create backup of tasks.json files")
    args = parser.parse_args()

    print("=" * 80)
    print("Task Migration: JSON → Folder Structure")
    print("=" * 80)
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()

    # Get all projects
    pm = ProjectManager()
    projects = pm.list_projects()

    if not projects:
        print("No projects found to migrate.")
        return

    print(f"Found {len(projects)} projects to check:")
    print()

    # Migrate each project
    results = {}
    for project in projects:
        project_name = project["project_name"]
        project_slug = project["slug"]
        project_path = pm.get_project_path(project_name)

        if not project_path:
            print(f"⚠️  {project_name}: Could not find project path")
            continue

        print(f"📁 {project_name} ({project_slug})")

        result = migrate_project(project_path, dry_run=args.dry_run, backup=args.backup)
        results[project_name] = result

        # Print result
        if result["status"] == "success":
            print(f"  ✅ Migrated {result['count']} tasks")
        elif result["status"] == "dry_run":
            print(f"  🔍 Would migrate {result['count']} tasks")
        elif result["status"] == "skipped":
            print(f"  ⏭️  Skipped: {result['reason']}")
        elif result["status"] == "error":
            print(f"  ❌ Error: {result['reason']}")

        print()

    # Summary
    print("=" * 80)
    print("Migration Summary")
    print("=" * 80)

    success_count = sum(1 for r in results.values() if r["status"] == "success")
    error_count = sum(1 for r in results.values() if r["status"] == "error")
    skipped_count = sum(1 for r in results.values() if r["status"] == "skipped")
    total_migrated = sum(r.get("count", 0) for r in results.values() if r["status"] == "success")

    print(f"Projects migrated successfully: {success_count}")
    print(f"Projects skipped: {skipped_count}")
    print(f"Projects with errors: {error_count}")
    print(f"Total tasks migrated: {total_migrated}")
    print()

    if args.dry_run:
        print("This was a DRY RUN. Run without --dry-run to apply changes.")
    else:
        print("✅ Migration complete!")

    print("=" * 80)


if __name__ == "__main__":
    main()
