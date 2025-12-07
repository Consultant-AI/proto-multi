# Task System Guide

## Overview

The task management system uses a **folder-based approach** where:
- Each task is a physical folder
- Tasks can have unlimited nested subtasks (infinite depth)
- Chat tasks (TodoWrite) sync with dashboard automatically
- Folder location determines hierarchy, not JSON metadata

## System Architecture

### Two Components Working Together

1. **TodoWrite (Chat Interface)**
   - Flat task list shown in chat
   - All tasks are root-level by default
   - No automatic parent-child relationships
   - Syncs to dashboard via ProjectManager

2. **FolderTaskManager (Backend Storage)**
   - Folder-based storage system
   - Physical folder location = task hierarchy
   - Each root project has `project_data.json` with complete tree
   - Supports infinite nesting for complex project structures

## Folder Structure

### Basic Structure
```
.proto/planning/{project-name}/
├── tasks/
│   ├── {task-folder-1}/          # Root task
│   │   ├── task.json             # Task metadata
│   │   ├── notes.md              # Planning notes
│   │   ├── files/                # Task files
│   │   ├── project_data.json     # Aggregated tree (if root)
│   │   └── tasks/                # Subtasks folder
│   │       └── {subtask-folder}/ # Nested subtask
│   │           ├── task.json
│   │           ├── notes.md
│   │           ├── files/
│   │           └── tasks/        # Can nest infinitely
│   ├── {task-folder-2}/          # Another root task
│   └── {task-folder-3}/          # Another root task
```

### Folder Naming Convention
Format: `{sanitized-title}-{task-id-first-8-chars}`

Example: `build-whatsapp-clone-fb11f039`

## Task Hierarchy Rules

### Rule 1: Physical Location = Hierarchy
**The folder's physical location determines its parent, NOT the task.json file.**

- Tasks in `tasks/` root = Root-level tasks (no parent)
- Tasks in `tasks/{parent}/tasks/` = Children of {parent}
- Can nest infinitely: `tasks/a/tasks/b/tasks/c/tasks/d/...`

### Rule 2: TodoWrite Creates Root Tasks Only
**TodoWrite in chat always creates flat, root-level tasks.**

When you use TodoWrite in chat:
```
1. ✅ [COMPLETED] Create project structure
2. 🔄 [IN_PROGRESS] Build dashboard
3. ⏳ [PENDING] Add authentication
```

All 3 tasks will be:
- At root level (`tasks/` folder)
- No parent relationships
- Synced to dashboard as separate top-level items

### Rule 3: Manual Nesting for Complex Projects
**To create task hierarchies, manually organize folders.**

Example - Creating subtasks:

1. **Create parent task** (via TodoWrite or API)
2. **Move child task folder** into parent's `tasks/` directory:
   ```bash
   mv tasks/child-task-abc123 tasks/parent-task-def456/tasks/
   ```
3. **Restart server** to reload structure

The parent-child relationship is automatically detected from folder location.

## How Chat and Dashboard Stay in Sync

### Synchronization Flow

```
TodoWrite (Chat)
    ↓
Creates/Updates Task
    ↓
ProjectManager._sync_to_project_manager()
    ↓
FolderTaskManager.create_task() / update_task()
    ↓
Saves to folder structure
    ↓
Updates project_data.json
    ↓
Dashboard API reads tasks
    ↓
Dashboard UI displays
```

### Key Points

1. **Single Source of Truth**: Folder structure on disk
2. **Automatic Sync**: TodoWrite → FolderTaskManager → Dashboard
3. **No Conflicts**: TodoWrite only creates root tasks
4. **Manual Hierarchy**: Move folders to create parent-child relationships

## Common Workflows

### Workflow 1: Simple Task List (Chat Only)

```markdown
User: "Build a React app with authentication"

Assistant uses TodoWrite:
1. Setup React project
2. Build login page
3. Add authentication
4. Deploy to production

Result: 4 root-level tasks in dashboard
```

### Workflow 2: Complex Project with Hierarchy

```markdown
1. Create main tasks via TodoWrite:
   - Backend Development
   - Frontend Development
   - Testing & Deployment

2. Manually create subtask structure:
   .proto/planning/my-project/tasks/
   ├── backend-development-abc123/
   │   ├── task.json
   │   ├── project_data.json
   │   └── tasks/
   │       ├── setup-database-def456/
   │       ├── create-api-endpoints-ghi789/
   │       └── add-authentication-jkl012/
   ├── frontend-development-mno345/
   │   └── tasks/
   │       ├── create-components-pqr678/
   │       └── setup-routing-stu901/
   └── testing-deployment-vwx234/

3. Restart server to load hierarchy

Result: Dashboard shows nested tree structure
```

### Workflow 3: Moving Tasks Between Levels

**Promote child to root:**
```bash
mv tasks/parent-abc/tasks/child-def tasks/
```

**Demote root to child:**
```bash
mv tasks/task-ghi tasks/parent-jkl/tasks/
```

**Move between parents:**
```bash
mv tasks/parent-a-xyz/tasks/child-123 tasks/parent-b-uvw/tasks/
```

Always restart server after moving folders.

## API Endpoints

### Get Project Data
```http
GET /api/dashboard/projects/{project_name}/data
```
Returns `project_data.json` with complete task tree and summary.

### Get Project Tasks
```http
GET /api/dashboard/projects/{project_name}
```
Returns full task tree with hierarchical structure.

### Task Files
```http
GET /api/dashboard/tasks/{task_id}/files
POST /api/dashboard/tasks/{task_id}/files
GET /api/dashboard/tasks/{task_id}/files/{filename}
```

### Task Notes
```http
GET /api/dashboard/tasks/{task_id}/notes
POST /api/dashboard/tasks/{task_id}/notes
```

## project_data.json Format

Each root task folder contains `project_data.json`:

```json
{
  "version": "1.0",
  "project_id": "task-uuid",
  "project_title": "Build WhatsApp Clone",
  "updated_at": "2025-11-20T17:05:56.969237Z",
  "summary": {
    "total_tasks": 5,
    "completed": 0,
    "in_progress": 1,
    "pending": 4,
    "blocked": 0
  },
  "task_tree": {
    "id": "task-uuid",
    "title": "Build WhatsApp Clone",
    "status": "pending",
    "children": [
      {
        "id": "child-uuid",
        "title": "Build Frontend",
        "children": [...]
      }
    ]
  }
}
```

## Troubleshooting

### Issue: Tasks show different in chat vs dashboard

**Cause**: Folder location doesn't match expected hierarchy

**Solution**:
1. Check folder structure: `ls -R .proto/planning/{project}/tasks/`
2. Move folders to correct location
3. Restart server

### Issue: Child task appears at root level

**Cause**: Task folder is in wrong location

**Solution**:
```bash
# Move to correct parent's tasks/ folder
mv tasks/child-task-abc tasks/parent-task-def/tasks/
# Restart server
```

### Issue: TodoWrite creates nested tasks

**Cause**: Should not happen anymore (fixed in this update)

**Verification**: Check `todo.py` line 288 - should return `None`

### Issue: project_data.json not updating

**Cause**: Auto-update may have failed

**Solution**:
```python
from computer_use_demo.planning import ProjectManager

pm = ProjectManager()
tm = pm.get_task_manager('project-name')
root_tasks = tm.get_root_tasks()
for task in root_tasks:
    tm._save_project_json(task.id)
```

## Best Practices

1. **Use TodoWrite for simple task lists** - Quick flat lists for chat tracking
2. **Use folder structure for complex projects** - Multi-level hierarchies
3. **Keep TodoWrite tasks at root** - Don't manually nest TodoWrite tasks
4. **Separate TodoWrite from manual hierarchies** - Use different projects
5. **Restart after folder moves** - Always reload to see changes
6. **Use project_data.json for overview** - Quick stats without walking tree

## Migration from Old System

If you have projects using the old `tasks.json` file:

```bash
python3 migrate_tasks_to_folders.py
```

This will:
1. Convert tasks.json to folder structure
2. Preserve all task metadata
3. Generate project_data.json files
4. Maintain parent-child relationships based on parent_id

## Summary

**Key Takeaway**:
- TodoWrite = Flat lists for chat
- Folder structure = Hierarchies for dashboard
- Physical location = Source of truth
- Both systems work together seamlessly

The system gives you flexibility:
- Simple flat lists when you need them
- Complex nested hierarchies when you want them
- Automatic sync between chat and dashboard
- Complete control over task organization
