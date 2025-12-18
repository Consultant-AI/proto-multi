# Project Creation Guide

## Overview

All projects in Proto are stored in the `.proto/planning/` directory. Each project has a structured folder hierarchy for organization.

## Project Directory Structure

```
.proto/planning/{project-name}/
├── README.md                   # Project description and overview
├── tasks/                      # All project tasks (folder-based task system)
│   └── {task-folders}/        # Each task is a folder with metadata
├── docs/                       # Planning documents, PRDs, designs
└── files/                      # Project files, code, media, etc.
```

## Creating a New Project

### Using the API Endpoint

**Endpoint**: `POST /api/dashboard/projects`

**Request Body**:
```json
{
  "project_name": "Snake Game",
  "description": "A classic snake game built with HTML, CSS, and JavaScript"
}
```

**Response**:
```json
{
  "name": "snake-game",
  "path": "/path/to/.proto/planning/snake-game",
  "created": true
}
```

### Project Name Rules

- Names are automatically sanitized to lowercase
- Spaces are converted to hyphens
- Only alphanumeric characters and hyphens are allowed
- Example: "Snake Game" → "snake-game"

## Working with Project Files

### Where to Put Files

1. **Code Files**: Put in `{project-name}/files/` directory
   - Example: `snake-game/files/index.html`
   - Example: `snake-game/files/game.js`

2. **Planning Documents**: Put in `{project-name}/docs/` directory
   - Example: `snake-game/docs/requirements.md`
   - Example: `snake-game/docs/design.md`

3. **Task-Specific Files**: Put in task folder's `files/` subdirectory
   - Example: `snake-game/tasks/implement-game-logic/files/algorithm.py`

### Creating Files via API

**For project files** (code, media, etc.):
```bash
# Use the browse/file endpoint with absolute path
PUT /api/browse/file?path=/path/to/.proto/planning/snake-game/files/index.html
```

**For task files**:
```bash
# Use the task-specific endpoint
POST /api/dashboard/tasks/{task_id}/files
```

## Important Rules for Agents

### ❌ DO NOT Create Files in /tmp/

Files created in `/tmp/` will NOT appear in the Explorer and will be lost on restart.

### ✅ DO Create Files in Project Directories

Always create files within the project's directory structure:
- `.proto/planning/{project-name}/files/` for project files
- `.proto/planning/{project-name}/docs/` for planning documents
- `.proto/planning/{project-name}/tasks/{task-id}/files/` for task-specific files

### Workflow Example

When a user asks to "create a snake game":

1. **Create the project**:
   ```
   POST /api/dashboard/projects
   Body: {"project_name": "Snake Game", "description": "Classic snake game"}
   ```

2. **Get the project path** from the response

3. **Create game files** in the project's `files/` directory:
   - `files/index.html` - Main HTML file
   - `files/game.js` - Game logic
   - `files/style.css` - Styling

4. **Refresh Explorer** - The project will now appear in the UI

## Viewing Projects in the UI

All projects in `.proto/planning/` automatically appear in the Explorer panel in the UI. After creating a project:

1. The project folder appears immediately
2. Click the folder to expand and see `tasks/`, `docs/`, and `files/`
3. Click any file to view its contents

## Example: Complete Project Creation

```bash
# 1. Create project
curl -X POST http://localhost:8000/api/dashboard/projects \
  -H "Content-Type: application/json" \
  -d '{"project_name": "Todo App", "description": "A simple todo list application"}'

# Response: {"name": "todo-app", "path": "...", "created": true}

# 2. Create HTML file
# PUT to /api/browse/file?path=.proto/planning/todo-app/files/index.html

# 3. Create JavaScript file
# PUT to /api/browse/file?path=.proto/planning/todo-app/files/app.js

# 4. View in UI - appears automatically in Explorer
```

## Sub-Projects

Projects can contain sub-projects for complex applications:

```
.proto/planning/e-commerce-platform/
├── README.md
├── files/
├── docs/
├── tasks/
└── sub-projects/              # Optional sub-projects directory
    ├── frontend/
    │   ├── README.md
    │   ├── files/
    │   └── docs/
    └── backend/
        ├── README.md
        ├── files/
        └── docs/
```

Create sub-projects by simply creating directories within the main project's directory.

## Summary

- **Always use `.proto/planning/{project-name}/` for new projects**
- **Never use `/tmp/` for project files**
- **Use the POST /api/dashboard/projects endpoint to create projects**
- **Put code/files in `files/` directory**
- **Put planning docs in `docs/` directory**
- **Projects automatically appear in the UI Explorer**
