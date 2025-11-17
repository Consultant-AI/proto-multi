# Debugging Guide - Tool Usage Logging

## Overview

The Agent SDK now includes comprehensive tool usage logging to help debug issues where the agent might be using the wrong tools (e.g., using `computer` tool for file operations instead of `str_replace_editor`).

## What's Logged

Every tool execution is logged with:
- Tool name
- Tool input parameters
- Timestamp
- Warning messages when problematic patterns detected

## Log Locations

### Console Output

When running the webui, you'll see real-time logging:

```
INFO - Tool executed: bash (mkdir project)
INFO - Tool executed: str_replace_editor (create_file: app.py)
WARNING - ⚠️  Computer tool used: screenshot (count: 1)
ERROR - ❌ TOO MANY COMPUTER TOOL CALLS! Should use bash/edit tools!
```

### Log Files

All tool executions are saved to:
```
~/.claude/projects/webui-{session-id}/tool_log.jsonl
```

Each line is a JSON object:
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "tool_name": "bash",
  "tool_input": {"command": "mkdir project"},
  "iteration": 1
}
```

### Summary Statistics

At the end of each task, a summary is printed:

```
=== Tool Usage Summary ===
bash: 5 calls
str_replace_editor: 3 calls
computer: 2 calls

Total tool calls: 10
=========================
```

## Warning System

### Computer Tool Overuse

If the agent uses the `computer` tool more than 3 times in a single task, you'll see:

```
ERROR - ❌ TOO MANY COMPUTER TOOL CALLS! Should use bash/edit tools!
ERROR - Check .claude/CLAUDE.md for tool usage priority guidance
```

This indicates the agent is likely:
- Opening text editors via GUI instead of using `str_replace_editor`
- Opening terminals via GUI instead of using `bash`
- Taking unnecessary screenshots

## How to Use Logs for Debugging

### Example 1: Agent Using Too Many Screenshots

**Symptom**: Task takes a long time, lots of screenshots

**Check logs**:
```bash
cd ~/.claude/projects/
ls -lt | head -n 2  # Find latest session
cat webui-*/tool_log.jsonl | grep computer
```

**Expected output showing problem**:
```json
{"tool_name": "computer", "tool_input": {"action": "screenshot"}}
{"tool_name": "computer", "tool_input": {"action": "screenshot"}}
{"tool_name": "computer", "tool_input": {"action": "screenshot"}}
{"tool_name": "computer", "tool_input": {"action": "screenshot"}}
```

**Solution**: Verify `.claude/CLAUDE.md` has tool priority guidance and `.claude/settings.json` has `auto_verification: false`

### Example 2: Agent Using GUI for File Creation

**Symptom**: Agent opens text editor and types code instead of creating file directly

**Check logs**:
```bash
cat ~/.claude/projects/webui-*/tool_log.jsonl | tail -n 20
```

**Expected output showing problem**:
```json
{"tool_name": "computer", "tool_input": {"action": "left_click"}}
{"tool_name": "computer", "tool_input": {"action": "type", "text": "gedit"}}
{"tool_name": "computer", "tool_input": {"action": "key", "text": "Return"}}
{"tool_name": "computer", "tool_input": {"action": "type", "text": "def hello():"}}
```

**Solution**: Agent should have used:
```json
{"tool_name": "str_replace_editor", "tool_input": {"command": "create", "path": "app.py"}}
```

### Example 3: Correct Tool Usage

**Good logs look like this**:
```json
{"tool_name": "bash", "tool_input": {"command": "mkdir my-project"}}
{"tool_name": "str_replace_editor", "tool_input": {"command": "create", "path": "app.py"}}
{"tool_name": "str_replace_editor", "tool_input": {"command": "create", "path": "README.md"}}
{"tool_name": "bash", "tool_input": {"command": "ls -la my-project"}}
{"tool_name": "computer", "tool_input": {"action": "screenshot"}}  // Optional verification
```

## Analyzing Tool Usage

### Count Tool Usage Per Session

```bash
cd ~/.claude/projects/webui-*/
cat tool_log.jsonl | jq -r '.tool_name' | sort | uniq -c | sort -rn
```

Example output:
```
  15 computer
   3 bash
   2 str_replace_editor
```

This shows the agent is heavily favoring `computer` tool (bad!).

### Find All Computer Tool Actions

```bash
cat tool_log.jsonl | jq 'select(.tool_name == "computer") | .tool_input.action' | sort | uniq -c
```

Example output:
```
  10 screenshot
   3 left_click
   2 type
```

### Timeline of Tool Usage

```bash
cat tool_log.jsonl | jq -r '[.timestamp, .tool_name, .tool_input.action // .tool_input.command // "N/A"] | @tsv'
```

This shows chronological order of tool usage.

## Common Issues and Solutions

### Issue: Many computer tool calls at start of task

**Problem**: Agent takes screenshots before doing anything

**Solution**:
- Disable `auto_verification` in `.claude/settings.json`
- Update system prompt to discourage initial screenshots

### Issue: Agent opens text editor to create files

**Problem**: Agent uses `computer` tool to click, open gedit, type code

**Solution**:
- Verify `.claude/CLAUDE.md` has "TOOL USAGE PRIORITY" section at top
- Check system prompt emphasizes direct file tools

### Issue: Agent opens terminal to run commands

**Problem**: Agent uses `computer` tool to open terminal instead of `bash` tool

**Solution**:
- System prompt should emphasize bash tool for all commands
- Add to CLAUDE.md: "Use bash tool, NOT computer tool with terminal"

## Integration with WebUI

The logging is automatically enabled when running:

```bash
python3 -m computer_use_demo.webui
```

You'll see logs in the terminal where you started the webui.

## Viewing Logs in Real-Time

While the webui is running, in another terminal:

```bash
# Follow the latest log file
cd ~/.claude/projects/
latest_session=$(ls -t | head -n 1)
tail -f "$latest_session/tool_log.jsonl" | jq -r '[.timestamp, .tool_name] | @tsv'
```

## Performance Impact

The logging has minimal performance impact:
- JSON serialization is fast
- Logs written asynchronously (doesn't block agent)
- Log files are append-only (no rewrites)

## Configuration

### Disable Logging

Edit `computer_use_demo/agent_sdk/orchestrator.py`:

```python
# In __init__ method:
self.tool_logger = ToolLogger(session_id or "unknown", enabled=False)
```

### Change Log Level

Edit `computer_use_demo/agent_sdk/tool_logger.py`:

```python
# Change WARNING threshold for computer tool
if self.tool_counts['computer'] > 5:  # Changed from 3 to 5
    logger.error("❌ TOO MANY COMPUTER TOOL CALLS!")
```

## Next Steps

When you see problematic tool usage:

1. **Check the logs** to understand what tools are being used
2. **Review CLAUDE.md** to ensure tool priority guidance is clear
3. **Verify settings.json** has optimized configuration
4. **Update system prompt** if needed to emphasize correct tool usage
5. **Test again** with a simple task to verify improvement

## Example Debugging Session

```bash
# 1. Run a task
python3 -m computer_use_demo.webui
# (In UI: "Create a Python file app.py with hello world")

# 2. Check what happened
cd ~/.claude/projects/
latest=$(ls -t | head -n 1)
cd "$latest"

# 3. View tool usage summary
cat tool_log.jsonl | jq -r '.tool_name' | sort | uniq -c

# 4. If you see many 'computer' calls, investigate:
cat tool_log.jsonl | jq 'select(.tool_name == "computer")'

# 5. Look for patterns - is it typing code? clicking around?
cat tool_log.jsonl | jq -r 'select(.tool_name == "computer") | .tool_input.action' | sort | uniq -c

# 6. Compare with what SHOULD have happened:
#    Expected: 1x bash (optional), 1x str_replace_editor
#    Actual: 15x computer (screenshot, click, type)
```

---

**The logging system helps you understand exactly what the agent is doing so you can optimize its behavior to work like Claude Code - fast, direct, and efficient!**
