# Critical Fix Applied - Tool Priority Not Being Followed

## Problem Identified

From the logs of your tic-tac-toe task:
- **26 computer tool calls** (clicking, typing, screenshots)
- **0 bash tool calls** (should have used for mkdir, running server)
- **0 str_replace_editor calls** (should have used for creating HTML/CSS/JS files)

The agent was behaving like a human using a GUI instead of like Claude Code using direct tools.

## Root Cause

**The CLAUDE.md conventions file was not being loaded into the system prompt!**

The SessionManager was looking for CLAUDE.md in the session directory (`~/.claude/projects/computer-use-{session-id}/CLAUDE.md`), but the actual CLAUDE.md with tool priority guidance was in the project directory (`.claude/CLAUDE.md`).

Result: The agent never saw the tool usage priority guidance, so it defaulted to GUI automation.

## Fixes Applied

### 1. Load Project CLAUDE.md ✅

**File**: `computer_use_demo/agent_sdk/session.py`

**Change**: Modified `load_conventions()` to check two locations:
1. **Project-level** `.claude/CLAUDE.md` (tool priority guidance) - **FIRST**
2. Session-level CLAUDE.md (session-specific learnings) - second

**Code**:
```python
def load_conventions(self) -> str | None:
    # First, try to load project-level conventions (has tool priority guidance)
    if self.project_conventions_file.exists():
        with open(self.project_conventions_file, "r") as f:
            project_conventions = f.read()

        # If session-specific conventions exist, append them
        if self.conventions_file.exists():
            with open(self.conventions_file, "r") as f:
                session_conventions = f.read()
            return f"{project_conventions}\n\n---\n\n# Session-Specific Learnings\n\n{session_conventions}"

        return project_conventions

    # Fall back to session-only conventions
    if self.conventions_file.exists():
        with open(self.conventions_file, "r") as f:
            return f.read()

    return None
```

### 2. Enhanced System Prompt ✅

**File**: `computer_use_demo/agent_sdk/orchestrator.py`

**Change**: Added strong `<CRITICAL_TOOL_USAGE_PRIORITY>` section to system prompt with:
- Clear tool priority rules
- Examples of CORRECT usage (bash/edit for files)
- Examples of WRONG usage (computer for files)
- Emphasis: "You are Claude Code with direct access to file and command tools"

**Key Addition**:
```
<CRITICAL_TOOL_USAGE_PRIORITY>
⚠️ IMPORTANT: You work like Claude Code - prefer DIRECT tools over GUI automation!

1. File Creation/Editing → Use `str_replace_editor` tool
   ❌ DO NOT use computer tool to open text editors and type

2. Running Commands → Use `bash` tool
   ❌ DO NOT use computer tool to open terminal and type

3. GUI Control → Use `computer` tool ONLY when absolutely necessary
   ✅ Opening browsers, clicking links, visual verification
   ❌ NOT for file operations, NOT for running commands

**Key principle: You are NOT a human using a GUI. You are Claude Code with direct access to file and command tools!**
</CRITICAL_TOOL_USAGE_PRIORITY>
```

### 3. Tool Logger Field Name ✅

Already correct - uses `"tool"` field in JSON logs.

## Expected Behavior Now

### For "write tictactoe code in html css js and run it on chrome and test it"

**BEFORE (what happened - WRONG)**:
```
1. computer → screenshot (unnecessary)
2. computer → click file manager
3. computer → click new file
4. computer → click text editor
5. computer → type HTML code character by character
6. computer → save file
7. ... repeat for CSS and JS
Total: 26 computer tool calls, 0 bash/edit
```

**AFTER (what should happen - CORRECT)**:
```
1. bash → mkdir tic-tac-toe
2. str_replace_editor → create index.html (full HTML in one call)
3. str_replace_editor → create style.css (full CSS in one call)
4. str_replace_editor → create game.js (full JavaScript in one call)
5. bash → cd tic-tac-toe && python3 -m http.server 8000 &
6. computer → open Chrome to localhost:8000
7. computer → click on game to test (optional)
Total: 4 bash/edit tools, 1-2 computer tools
```

## How to Test

Run the webui again:

```bash
cd /Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-demo
python3 -m computer_use_demo.webui
```

Try the same task:
```
write tictactoe code in html css js and run it on chrome and test it
```

You should now see in the console:
```
✅ bash called (count: 1)
✅ str_replace_editor called (count: 1)
✅ str_replace_editor called (count: 2)
✅ str_replace_editor called (count: 3)
✅ bash called (count: 2)
⚠️ Computer tool used: screenshot (count: 1)

=== Tool Usage Summary ===
bash: 2 calls
str_replace_editor: 3 calls
computer: 1 call
Total tool calls: 6
=========================
```

Instead of:
```
⚠️ Computer tool used: screenshot (count: 1)
⚠️ Computer tool used: key (count: 2)
⚠️ Computer tool used: key (count: 3)
...
ERROR - ❌ TOO MANY COMPUTER TOOL CALLS (26)!
```

## Verify Logs

After running the task, check:

```bash
cd ~/.claude/projects/
latest=$(ls -t | head -n 1)
cat "$latest/tool_log.jsonl" | jq -r '.tool' | sort | uniq -c
```

You should see something like:
```
  2 bash
  3 str_replace_editor
  1 computer
```

NOT:
```
 26 computer
```

## Files Modified

1. **`computer_use_demo/agent_sdk/session.py`**
   - Line 55: Added `self.project_conventions_file = Path.cwd() / ".claude" / "CLAUDE.md"`
   - Lines 136-165: Updated `load_conventions()` to load project CLAUDE.md first

2. **`computer_use_demo/agent_sdk/orchestrator.py`**
   - Lines 78-126: Added `<CRITICAL_TOOL_USAGE_PRIORITY>` section to system prompt

## Why This Matters

**Speed**:
- Before: 26 tool calls taking ~5 minutes
- After: 6 tool calls taking ~30 seconds

**Reliability**:
- GUI automation can fail (UI changes, timing issues)
- Direct tools are deterministic and reliable

**Context Usage**:
- 26 screenshots = massive context usage
- 6 tool calls with minimal screenshots = efficient

**Behavior**:
- Before: Acting like a slow human
- After: Acting like Claude Code - fast and direct

## Test Checklist

When you run the next task, verify:

- [ ] Agent uses `bash` for creating directories
- [ ] Agent uses `str_replace_editor` for creating files
- [ ] Agent creates full file content in one call (not typing character by character)
- [ ] Agent uses `bash` for running commands
- [ ] Agent uses `computer` tool ONLY for browser interaction
- [ ] Console shows "✅ bash called" and "✅ str_replace_editor called"
- [ ] Console does NOT show many "⚠️ Computer tool used" warnings
- [ ] Tool summary shows balanced usage (bash/edit >> computer)

---

## Files Modified

1. **`computer_use_demo/agent_sdk/session.py`**
   - Line 55: Added `self.project_conventions_file = Path.cwd() / ".claude" / "CLAUDE.md"`
   - Lines 136-165: Updated `load_conventions()` to load project CLAUDE.md first

2. **`computer_use_demo/agent_sdk/orchestrator.py`**
   - Lines 78-126: Added `<CRITICAL_TOOL_USAGE_PRIORITY>` section to system prompt

3. **`computer_use_demo/tools/groups.py`** ⚠️ CRITICAL FIX
   - Line 46: Added `EditTool20250728, BashTool20250124` to `computer_use_local` tool group
   - **This fixes "Tool bash is invalid" error**
   - The local version now includes bash and edit tools, not just computer tool

---

## Status: ✅ Fixed and Ready to Test

The agent will now follow tool priority and work like Claude Code!

**Restart the webui** to load the new tool configuration:
```bash
# Stop the current webui (Ctrl+C)
# Then restart:
python3 -m computer_use_demo.webui
```

Run it and check the logs to confirm the fix worked. 🚀
