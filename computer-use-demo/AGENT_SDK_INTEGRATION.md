# Agent SDK Integration Guide

This document describes the production-grade Agent SDK integration with computer-use-demo.

## Overview

The Agent SDK integration transforms computer-use-demo from a simple demonstration into a production-ready autonomous agent platform combining:

- **Computer-use-demo's proven GUI automation** (screenshot, mouse, keyboard control via xdotool)
- **Claude Agent SDK's advanced orchestration** (feedback loops, subagents, session persistence)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Agent SDK Orchestration Core                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Main Agent Loop (Feedback Model)                │   │
│  │  • Gather Context → Take Action → Verify Work    │   │
│  │  • Session Persistence & Auto-save               │   │
│  │  • Context Management & Compaction               │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────┴───────────────────────────────┐   │
│  │         Subagent Coordinator                     │   │
│  │  • Parallel execution (max 3 concurrent)         │   │
│  │  • Specialized roles (execution, verification)   │   │
│  │  • Isolated context windows                      │   │
│  └──────┬─────────────┬──────────────┬──────────────┘   │
└─────────┼─────────────┼──────────────┼──────────────────┘
          │             │              │
   ┌──────▼──────┐ ┌───▼─────────┐ ┌──▼────────────┐
   │ Execution   │ │ Verification│ │ File/Code     │
   │ Subagent    │ │ Subagent    │ │ Subagent      │
   └──────┬──────┘ └───┬─────────┘ └──┬────────────┘
          │            │               │
┌─────────▼────────────▼───────────────▼──────────────┐
│           Unified Tool Layer                        │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐ │
│  │ Computer │ │   Bash   │ │  Edit   │ │  Agent  │ │
│  │   Tool   │ │   Tool   │ │  Tool   │ │   SDK   │ │
│  │(GUI)     │ │(Commands)│ │ (Files) │ │  Tools  │ │
│  └────┬─────┘ └────┬─────┘ └────┬────┘ └─────────┘ │
└───────┼────────────┼────────────┼────────────────────┘
        │            │            │
   ┌────▼────────────▼────────────▼────────┐
   │    Docker Container (X11 Desktop)     │
   │  • GUI automation via xdotool         │
   │  • Visual verification via screenshots│
   │  • Desktop environment (Ubuntu 24.04) │
   └───────────────────────────────────────┘
```

## Key Components

### 1. Agent Orchestrator (`agent_sdk/orchestrator.py`)

Production-grade orchestration loop replacing the simple while loop:

**Features:**
- Feedback loop pattern: gather → act → verify → repeat
- Automatic verification after GUI actions
- Session persistence with JSONL transcripts
- Context management and automatic compaction
- Enhanced system prompt with conventions

**Usage:**
```python
from computer_use_demo.agent_sdk import AgentOrchestrator

orchestrator = AgentOrchestrator(
    session_id="my-session",
    enable_subagents=True,
    enable_verification=True,
)

messages = await orchestrator.orchestrate(
    model="claude-sonnet-4-5",
    provider="anthropic",
    # ... other parameters
)
```

### 2. Session Manager (`agent_sdk/session.py`)

Persistent session storage and resumption:

**Features:**
- JSONL transcript storage (one message per line)
- CLAUDE.md convention storage
- Session metadata tracking
- Tool execution statistics
- Automatic cleanup of old sessions

**Storage Structure:**
```
~/.claude/projects/computer-use-{session_id}/
├── transcript.jsonl        # Conversation history
├── CLAUDE.md              # Learned conventions
└── metadata.json          # Session statistics
```

**Usage:**
```python
from computer_use_demo.agent_sdk import SessionManager

session = SessionManager(session_id="my-session")

# Save session
await session.save_session(messages)

# Load session
messages = session.load_session()

# Access conventions
conventions = session.load_conventions()
```

### 3. Context Manager (`agent_sdk/context_manager.py`)

Automatic context management preventing exhaustion:

**Features:**
- Screenshot truncation with cache optimization
- Image removal in chunks (preserves prompt cache)
- Context statistics tracking
- Token usage estimation

**Usage:**
```python
from computer_use_demo.agent_sdk import ContextManager

context_mgr = ContextManager(max_images=10)

# Compact context
messages = await context_mgr.maybe_compact_context(messages)

# Get stats
stats = context_mgr.get_context_stats(messages)
print(f"Screenshots: {stats['screenshots']}")
```

### 4. Subagent Coordinator (`agent_sdk/subagents.py`)

Parallel execution with specialized agents:

**Subagent Types:**
- **EXECUTION**: GUI automation, command execution
- **VERIFICATION**: Screenshot analysis, validation
- **FILE_OPERATIONS**: File creation, editing, searching
- **RESEARCH**: Web browsing, documentation lookup
- **COORDINATION**: Task decomposition and delegation

**Usage:**
```python
from computer_use_demo.agent_sdk import SubagentCoordinator
from computer_use_demo.agent_sdk.subagents import SubagentTask, SubagentType

coordinator = SubagentCoordinator(max_concurrent=3)

# Create tasks
tasks = [
    SubagentTask(
        task_id="task1",
        subagent_type=SubagentType.EXECUTION,
        prompt="Launch VS Code and open file.py",
    ),
    SubagentTask(
        task_id="task2",
        subagent_type=SubagentType.VERIFICATION,
        prompt="Verify VS Code launched successfully",
    ),
]

# Execute in parallel
results = await coordinator.execute_parallel(tasks, orchestrator_callback)
```

### 5. Verification System (`verification/`)

Comprehensive verification with visual and structural checks:

**Components:**

**Screenshot Analyzer (`screenshot_analyzer.py`):**
- Visual verification using screenshots
- Error dialog detection
- Screenshot comparison
- Verification prompt generation

**Structural Checker (`structural_checker.py`):**
- File existence checks
- Process validation
- Command output verification
- Port listening checks
- Directory contents validation

**Feedback Loop (`feedback_loop.py`):**
- Action execution with verification
- Automatic retry on failure
- Visual + structural verification
- Verification reporting

**Usage:**
```python
from computer_use_demo.verification import (
    ScreenshotAnalyzer,
    StructuralChecker,
    FeedbackLoop,
    Action,
    ActionType,
)

# Create feedback loop
loop = FeedbackLoop(
    enable_visual_verification=True,
    enable_structural_verification=True,
    auto_retry=True,
)

# Define action
action = Action(
    action_type=ActionType.APPLICATION_LAUNCH,
    description="Launch VS Code",
    verification_criteria={
        "expected_visual_state": "VS Code window visible",
        "processes_should_run": ["code"],
    },
    retry_on_failure=True,
    max_retries=3,
)

# Execute with verification
result = await loop.execute_with_verification(
    action=action,
    executor_callback=launch_vscode,
    screenshot_callback=capture_screen,
)

print(f"Success: {result.success}")
print(f"Retries: {result.retries_attempted}")
```

## Configuration

Configuration is stored in `.claude/settings.json`:

```json
{
  "agent_sdk": {
    "enabled": true,
    "session_persistence": true,
    "auto_verification": true,
    "subagents_enabled": true,
    "max_concurrent_subagents": 3
  },
  "verification": {
    "visual_verification": true,
    "structural_verification": true,
    "auto_retry_on_failure": true,
    "max_retries": 3
  },
  "context_management": {
    "max_images": 10,
    "min_removal_threshold": 5,
    "auto_compaction": true
  }
}
```

## Agent Definitions

Specialized agents are defined in `.claude/agents/`:

- **`execution_agent.md`**: GUI automation and command execution specialist
- **`verification_agent.md`**: Visual and structural verification specialist
- **`file_operations_agent.md`**: File creation, editing, and searching specialist

Each agent has:
- Role description and responsibilities
- Available tools
- Operating guidelines
- Best practices
- Example workflows

## Migration from Simple Loop

### Option 1: Drop-in Replacement

Replace the import:

```python
# Before
from computer_use_demo.loop import sampling_loop

# After
from computer_use_demo.agent_loop import sampling_loop
```

The Agent SDK loop maintains the same interface with optional new parameters.

### Option 2: Direct Orchestrator Use

For more control:

```python
from computer_use_demo.agent_sdk import AgentOrchestrator

orchestrator = AgentOrchestrator(
    session_id=session_id,
    enable_subagents=True,
    enable_verification=True,
)

messages = await orchestrator.orchestrate(
    model=model,
    provider=provider,
    # ... parameters
)

# Access session stats
stats = orchestrator.session_manager.get_session_stats()
```

## Usage Examples

### Example 1: Basic Usage with Persistence

```python
from computer_use_demo.agent_loop import sampling_loop

messages = []

# First session
result = await sampling_loop(
    model="claude-sonnet-4-5",
    provider="anthropic",
    system_prompt_suffix="You are a helpful assistant.",
    messages=messages,
    output_callback=handle_output,
    tool_output_callback=handle_tool_output,
    api_response_callback=handle_api_response,
    api_key=api_key,
    tool_version=ToolVersion.COMPUTER_USE_20250124,
    session_id="my-project",  # Enable persistence
)

# Later - resume session
result = await sampling_loop(
    # ... same parameters ...
    session_id="my-project",  # Resumes from saved state
)
```

### Example 2: Complex Workflow with Verification

```python
from computer_use_demo.agent_loop import sampling_loop

messages = [
    {
        "role": "user",
        "content": """
        Please do the following:
        1. Open VS Code
        2. Create a new Python file called hello.py
        3. Write a hello world function
        4. Verify the file was created correctly
        """
    }
]

result = await sampling_loop(
    model="claude-sonnet-4-5",
    provider="anthropic",
    system_prompt_suffix="",
    messages=messages,
    output_callback=handle_output,
    tool_output_callback=handle_tool_output,
    api_response_callback=handle_api_response,
    api_key=api_key,
    tool_version=ToolVersion.COMPUTER_USE_20250124,
    enable_verification=True,  # Automatic verification
    session_id="vscode-setup",
)

# Agent will automatically:
# 1. Launch VS Code
# 2. Verify it opened (screenshot)
# 3. Create the file
# 4. Verify file exists (structural check)
# 5. Verify content is correct
```

### Example 3: Subagent Parallelization

```python
# For complex multi-task workflows, subagents can work in parallel
messages = [
    {
        "role": "user",
        "content": """
        Multi-task project:
        1. Research Python best practices online
        2. Set up a new project directory structure
        3. Create a README with findings

        These tasks can be done in parallel where appropriate.
        """
    }
]

result = await sampling_loop(
    # ... parameters ...
    enable_subagents=True,  # Enable parallel execution
    session_id="multi-task-project",
)

# Agent SDK will:
# - Create research subagent (web browsing)
# - Create file operations subagent (directory setup)
# - Coordinate and aggregate results
# - Create final README with findings
```

## Best Practices

### 1. Use Session IDs for Projects

```python
# Give each project a meaningful session ID
session_id = f"project-{project_name}-{datetime.now().strftime('%Y%m%d')}"
```

### 2. Enable Verification for Critical Tasks

```python
# For production workflows, enable verification
enable_verification=True
```

### 3. Review Session Statistics

```python
# After execution, review stats
stats = orchestrator.session_manager.get_session_stats()
print(f"Tool executions: {stats['tool_executions']}")
print(f"Success rate: {stats['tools']['computer']['successes'] / stats['tools']['computer']['executions']}")
```

### 4. Use CLAUDE.md for Conventions

Update `.claude/CLAUDE.md` with project-specific patterns:

```markdown
## Project-Specific Conventions

### Database Access
- Database runs on port 5432
- Connection string in .env file
- Use psql for verification

### Testing
- Run tests with: pytest tests/
- All tests must pass before deployment
```

### 5. Leverage Subagents for Complex Workflows

For multi-step workflows, let the orchestrator delegate:

```python
messages = [
    {
        "role": "user",
        "content": "Build and deploy the application (research, code, test, deploy)"
    }
]

# Agent SDK will automatically:
# - Break down into subtasks
# - Assign to specialized subagents
# - Execute in parallel where possible
# - Verify each phase
```

## Troubleshooting

### Session Not Persisting

**Issue:** Changes aren't saved between runs

**Solution:**
- Ensure `session_id` is provided and consistent
- Check `~/.claude/projects/` directory exists and is writable
- Verify `session_persistence: true` in settings.json

### Verification Failing

**Issue:** Actions marked as failed even when they succeed

**Solution:**
- Review verification criteria in action definition
- Check screenshot is being captured correctly
- Adjust confidence thresholds
- Disable auto-retry if false positives occur: `auto_retry=False`

### Context Window Exhaustion

**Issue:** "Context window exceeded" errors

**Solution:**
- Enable context management: `auto_compaction: true`
- Reduce `max_images` in settings.json
- Use `only_n_most_recent_images` parameter
- Clear old screenshots: `context_mgr.maybe_compact_context(messages)`

### Subagents Not Executing

**Issue:** Subagents don't run in parallel

**Solution:**
- Verify `enable_subagents=True`
- Check `max_concurrent_subagents` in settings.json
- Ensure tasks are independent (can run in parallel)
- Review subagent coordinator stats: `coordinator.get_stats()`

## Performance Considerations

### Context Management

- **Images are expensive**: Each screenshot ~1500 tokens
- **Use compaction**: Set `max_images=10` for long sessions
- **Prefer structural checks**: Use bash checks over screenshots when possible

### Subagent Overhead

- **Parallel execution adds latency**: Only use for truly independent tasks
- **Context isolation**: Each subagent has independent context window
- **Coordination cost**: Main agent must aggregate subagent results

### Session Storage

- **JSONL appends**: Sessions grow over time
- **Cleanup old sessions**: Run `cleanup_old_sessions(max_age_days=30)`
- **Large transcripts**: Consider archiving very long sessions

## Advanced Features

### Custom Verification Criteria

Define complex verification:

```python
action = Action(
    action_type=ActionType.COMMAND_EXECUTION,
    description="Start web server",
    verification_criteria={
        "processes_should_run": ["python", "server.py"],
        "ports_should_listen": [{"port": 8080, "host": "localhost"}],
        "command_checks": [
            {
                "command": "curl -s localhost:8080/health",
                "expected_output": "OK",
                "expected_exit_code": 0,
            }
        ],
    },
)
```

### Hook System (Future)

`.claude/hooks/error_detection.json`:

```json
{
  "after_tool_execution": {
    "computer": "check_for_error_dialogs"
  }
}
```

### MCP Integration (Future)

Expose computer tool as MCP server for other agents:

```json
{
  "mcpServers": {
    "computer_use": {
      "type": "subprocess",
      "command": "python",
      "args": ["-m", "computer_use_demo.mcp_server"]
    }
  }
}
```

## Summary

The Agent SDK integration provides production-ready capabilities:

✅ **Session Persistence** - Resume work across restarts
✅ **Feedback Loops** - Automatic verification of actions
✅ **Context Management** - Prevent context exhaustion
✅ **Subagent Coordination** - Parallel execution
✅ **Error Recovery** - Automatic retry on failures
✅ **Verification System** - Visual + structural validation
✅ **Statistics & Monitoring** - Track success rates
✅ **Convention Learning** - CLAUDE.md memory system

All while maintaining **100% compatibility** with existing computer-use-demo tools and Docker environment.

For questions or issues, see the [GitHub repository](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo).
