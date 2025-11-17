# Agent SDK Integration - Production-Ready Computer Automation

This is a **production-grade integration** of Claude Agent SDK with computer-use-demo, combining the best of both systems:

- ✅ **Proven GUI automation** from computer-use-demo (xdotool, screenshots, Docker)
- ✅ **Advanced orchestration** from Claude Agent SDK (feedback loops, subagents, sessions)

## What This Gives You

### 🎯 Core Capabilities

**From Computer-Use-Demo:**
- Full GUI control (mouse, keyboard, screenshots)
- Desktop automation via xdotool in Docker container
- Visual verification through screenshots
- Bash command execution with persistent sessions
- File editing with str_replace_editor tool

**From Agent SDK:**
- Feedback loops (gather → act → verify → repeat)
- Session persistence and resumption
- Automatic context management
- Subagent coordination for parallel tasks
- Error recovery and retry logic
- CLAUDE.md convention learning

### 🚀 New Features

1. **Session Persistence**: Your work is automatically saved
2. **Automatic Verification**: Actions are verified visually and programmatically
3. **Subagent Parallelization**: Complex tasks split across specialized agents
4. **Context Management**: Long sessions don't exhaust context window
5. **Error Recovery**: Failed actions automatically retry with corrections
6. **Convention Learning**: System learns and remembers patterns via CLAUDE.md

## Quick Start

### Option 1: Drop-in Replacement (Easiest)

```python
# Just change the import!
# Before:
from computer_use_demo.loop import sampling_loop

# After:
from computer_use_demo.agent_loop import sampling_loop

# Everything else stays the same, but you get all Agent SDK features
messages = await sampling_loop(
    model="claude-sonnet-4-5",
    provider="anthropic",
    system_prompt_suffix="",
    messages=messages,
    output_callback=handle_output,
    tool_output_callback=handle_tool_output,
    api_response_callback=handle_api_response,
    api_key=api_key,
    tool_version=ToolVersion.COMPUTER_USE_20250124,
    # NEW: Optional Agent SDK parameters
    session_id="my-project",  # Enable persistence
    enable_verification=True,  # Auto-verify actions
    enable_subagents=True,     # Enable parallelization
)
```

### Option 2: Direct Orchestrator (More Control)

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

# Access detailed statistics
stats = orchestrator.session_manager.get_session_stats()
print(f"Tool executions: {stats['tool_executions']}")
print(f"Session ID: {stats['session_id']}")
```

## Architecture Overview

```
User Request
     ↓
Agent SDK Orchestrator (feedback loops, sessions, context)
     ↓
Subagent Coordinator (parallel execution)
     ↓
     ├─→ Execution Agent (GUI automation)
     ├─→ Verification Agent (screenshot analysis)
     └─→ File Operations Agent (code editing)
          ↓
     Tool Layer
          ├─→ Computer Tool (mouse, keyboard, screenshots)
          ├─→ Bash Tool (commands, scripts)
          └─→ Edit Tool (file operations)
               ↓
     Docker Container (Ubuntu desktop + X11)
```

## Real-World Examples

### Example 1: Development Workflow

```python
messages = [
    {
        "role": "user",
        "content": """
        Create a Python web scraper:
        1. Research BeautifulSoup documentation online
        2. Create scraper.py with proper structure
        3. Write tests in test_scraper.py
        4. Run tests and verify they pass
        """
    }
]

# Agent SDK will:
# - Research in browser (execution subagent)
# - Create files (file operations subagent)
# - Verify syntax and run tests
# - Report results with screenshots
result = await sampling_loop(
    model="claude-sonnet-4-5",
    provider="anthropic",
    messages=messages,
    # ... callbacks ...
    api_key=api_key,
    tool_version=ToolVersion.COMPUTER_USE_20250124,
    session_id="web-scraper-project",
    enable_verification=True,
    enable_subagents=True,
)
```

### Example 2: Multi-Application Testing

```python
messages = [
    {
        "role": "user",
        "content": """
        Test the web application:
        1. Start the dev server in terminal
        2. Open browser and navigate to localhost:3000
        3. Click through all navigation links
        4. Verify each page loads without errors
        5. Take screenshots of each page
        6. Generate a test report
        """
    }
]

result = await sampling_loop(
    # ... parameters ...
    session_id="webapp-testing",
    enable_verification=True,  # Verify each page load
)

# Agent automatically:
# - Launches server and verifies it started
# - Opens browser with visual confirmation
# - Tests each link with screenshot verification
# - Detects any error pages or crashes
# - Generates comprehensive report
```

### Example 3: Resumable Sessions

```python
# First session - start work
messages = [
    {
        "role": "user",
        "content": "Set up a Django project with authentication"
    }
]

result = await sampling_loop(
    # ... parameters ...
    session_id="django-auth-project",
)

# Later (after restart, different day, etc.)
# Resume from exactly where you left off
messages = []  # Empty - will load from session

result = await sampling_loop(
    # ... same parameters ...
    session_id="django-auth-project",  # Same ID = resumes
)

# Agent loads previous work and continues
# Session includes: messages, conventions learned, tool stats
```

## Key Components

### 1. Feedback Loop System

Every important action goes through verification:

```
Action Taken (e.g., launch app)
     ↓
Visual Verification (screenshot analysis)
     ↓
Structural Verification (process check, port listening)
     ↓
Success? → Continue : Retry (up to 3 times)
```

### 2. Session Management

```
~/.claude/projects/computer-use-{session-id}/
├── transcript.jsonl       # Full conversation history
├── CLAUDE.md             # Learned conventions
└── metadata.json         # Stats and tool usage
```

Load session conventions:
```python
from computer_use_demo.agent_sdk import SessionManager

session = SessionManager(session_id="my-project")
conventions = session.load_conventions()
stats = session.get_session_stats()
```

### 3. Subagent Specialization

Different agents for different tasks:

- **Execution Agent**: GUI automation specialist
  - Tools: computer, bash
  - Role: Click, type, launch apps, run commands

- **Verification Agent**: Quality gate specialist
  - Tools: computer, bash
  - Role: Verify actions succeeded, detect errors

- **File Operations Agent**: Code and file specialist
  - Tools: edit, bash
  - Role: Create, edit, search files

Agents work in parallel when tasks are independent.

### 4. Verification System

Two-layer verification:

**Visual (Screenshot Analysis):**
```python
from computer_use_demo.verification import ScreenshotAnalyzer

analyzer = ScreenshotAnalyzer()
result = await analyzer.analyze_screenshot(
    screenshot_base64=screen,
    expected_state="VS Code window visible",
    action_taken="launched VS Code",
)
print(f"Success: {result.success}, Confidence: {result.confidence}")
```

**Structural (System Checks):**
```python
from computer_use_demo.verification import StructuralChecker

checker = StructuralChecker()

# Check file exists
await checker.check_file_exists("/tmp/test.py")

# Check process running
await checker.check_process_running("code")

# Check port listening
await checker.check_port_listening(8080)
```

## Configuration

Edit [.claude/settings.json](.claude/settings.json):

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
    "auto_compaction": true
  }
}
```

## Agent Definitions

Specialized agent behaviors defined in `.claude/agents/`:

- [execution_agent.md](.claude/agents/execution_agent.md) - GUI automation
- [verification_agent.md](.claude/agents/verification_agent.md) - Quality checks
- [file_operations_agent.md](.claude/agents/file_operations_agent.md) - File handling

## Learned Conventions

[.claude/CLAUDE.md](.claude/CLAUDE.md) stores discovered patterns:

```markdown
# Desktop Automation Conventions

## Application Launching

**VS Code:**
```bash
(DISPLAY=:1 code --no-sandbox &)
```
Wait 3 seconds, verify with screenshot

## Error Recovery

**Application won't launch:**
1. Check DISPLAY variable
2. Verify process not already running
3. Kill zombie processes: pkill app-name
```

Agents automatically reference and update this file.

## File Structure

```
computer-use-demo/
├── computer_use_demo/
│   ├── agent_sdk/                 # Agent SDK integration
│   │   ├── __init__.py
│   │   ├── orchestrator.py       # Main orchestration loop
│   │   ├── session.py            # Session persistence
│   │   ├── context_manager.py    # Context management
│   │   └── subagents.py          # Subagent coordination
│   ├── verification/             # Verification system
│   │   ├── __init__.py
│   │   ├── screenshot_analyzer.py
│   │   ├── structural_checker.py
│   │   └── feedback_loop.py
│   ├── agent_loop.py            # Drop-in replacement for loop.py
│   ├── loop.py                  # Original simple loop
│   └── tools/                   # Existing tools (preserved)
├── .claude/
│   ├── settings.json            # Configuration
│   ├── CLAUDE.md               # Conventions
│   └── agents/                 # Agent definitions
│       ├── execution_agent.md
│       ├── verification_agent.md
│       └── file_operations_agent.md
├── tests/
│   └── test_agent_sdk_integration.py
├── AGENT_SDK_INTEGRATION.md    # Detailed documentation
└── README_AGENT_SDK.md         # This file
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run integration tests
pytest tests/test_agent_sdk_integration.py -v

# Run specific test
pytest tests/test_agent_sdk_integration.py::TestSessionManager::test_session_creation -v
```

## Migration Guide

### From Simple Loop

**Before:**
```python
from computer_use_demo.loop import sampling_loop

messages = await sampling_loop(
    model=model,
    provider=provider,
    # ... parameters
)
```

**After (Option 1 - Easy):**
```python
from computer_use_demo.agent_loop import sampling_loop  # Just change import!

messages = await sampling_loop(
    model=model,
    provider=provider,
    # ... same parameters
    session_id="my-project",  # Optional: add session ID
)
```

**After (Option 2 - Full Control):**
```python
from computer_use_demo.agent_sdk import AgentOrchestrator

orchestrator = AgentOrchestrator(
    session_id="my-project",
    enable_subagents=True,
    enable_verification=True,
)

messages = await orchestrator.orchestrate(
    model=model,
    provider=provider,
    # ... parameters
)

# Access advanced features
stats = orchestrator.session_manager.get_session_stats()
context_info = orchestrator.context_manager.get_context_stats(messages)
```

## Troubleshooting

### Q: Session not persisting?

**A:** Ensure `session_id` parameter is provided and consistent between runs:
```python
session_id = "my-unique-project-id"  # Use same ID each time
```

### Q: Context window exceeded?

**A:** Enable context management:
```python
# In .claude/settings.json
{
  "context_management": {
    "max_images": 10,  # Reduce if needed
    "auto_compaction": true
  }
}
```

### Q: Verification failing incorrectly?

**A:** Adjust verification settings:
```python
enable_verification=False  # Disable if too strict
# Or adjust criteria in action definitions
```

### Q: Subagents not running?

**A:** Check configuration:
```python
enable_subagents=True  # Must be enabled
# And in .claude/settings.json:
{"agent_sdk": {"subagents_enabled": true}}
```

## Performance Tips

1. **Use session IDs** - Enables resumption, avoids re-work
2. **Limit screenshots** - Set `max_images=10` for long sessions
3. **Prefer structural checks** - Faster than screenshots when possible
4. **Enable compaction** - Prevents context exhaustion
5. **Use subagents wisely** - Only for truly independent tasks

## Advanced Usage

### Custom Verification

```python
from computer_use_demo.verification import FeedbackLoop, Action, ActionType

loop = FeedbackLoop(enable_visual_verification=True)

action = Action(
    action_type=ActionType.APPLICATION_LAUNCH,
    description="Launch VS Code",
    verification_criteria={
        "expected_visual_state": "VS Code window visible",
        "processes_should_run": ["code"],
        "ports_should_listen": [9339],  # Extension host
    },
    max_retries=3,
)

result = await loop.execute_with_verification(
    action=action,
    executor_callback=launch_vscode,
    screenshot_callback=capture_screen,
)
```

### Session Analysis

```python
from computer_use_demo.agent_sdk import SessionManager

session = SessionManager(session_id="my-project")

# Get detailed stats
stats = session.get_session_stats()
print(f"Total tools: {stats['tool_executions']}")
print(f"Computer tool: {stats['tools']['computer']}")
print(f"Success rate: {stats['tools']['computer']['successes'] / stats['tools']['computer']['executions']}")

# Load and analyze conventions
conventions = session.load_conventions()
print("Learned conventions:", conventions)
```

## What's Different from Simple Loop?

| Feature | Simple Loop | Agent SDK Loop |
|---------|-------------|----------------|
| **Persistence** | ❌ Lost on restart | ✅ Sessions saved |
| **Verification** | ❌ Manual | ✅ Automatic |
| **Context Management** | Manual image truncation | ✅ Auto-compaction |
| **Subagents** | ❌ Sequential only | ✅ Parallel execution |
| **Error Recovery** | ❌ Fails immediately | ✅ Auto-retry |
| **Convention Learning** | ❌ None | ✅ CLAUDE.md |
| **Statistics** | ❌ None | ✅ Detailed tracking |
| **Compatibility** | ✅ Original | ✅ 100% compatible |

## Summary

This integration provides **production-ready** autonomous agent capabilities while maintaining **100% compatibility** with the original computer-use-demo.

**What you get:**
- ✅ All existing GUI automation features
- ✅ Session persistence and resumption
- ✅ Automatic verification loops
- ✅ Subagent parallelization
- ✅ Error recovery and retry
- ✅ Context management
- ✅ Convention learning
- ✅ Detailed statistics

**What you keep:**
- ✅ Same Docker environment
- ✅ Same tools (computer, bash, edit)
- ✅ Same API interface
- ✅ Same deployment model

**Migration path:**
- ✅ Drop-in replacement (change one import)
- ✅ Gradual adoption (use new features as needed)
- ✅ Full backwards compatibility

For detailed documentation, see [AGENT_SDK_INTEGRATION.md](AGENT_SDK_INTEGRATION.md).

For questions or issues, see the [main computer-use-demo repository](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo).
