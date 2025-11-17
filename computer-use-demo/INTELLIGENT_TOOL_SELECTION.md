# Intelligent Tool Selection - Not Hardcoded!

## The Right Approach

You pointed out correctly: **it should use both when needed**, not follow a rigid hardcoded sequence.

## How It Works Now

The agent intelligently chooses tools based on **what the user asks for**:

### File/Command Operations → Direct Tools
```
User: "Create a Python script that calculates fibonacci"
Agent: Uses str_replace_editor to create the file
Tools used: str_replace_editor only ✅
```

### GUI Operations → Computer Tool
```
User: "Open Chrome and go to google.com"
Agent: Uses computer tool to click Chrome, type URL
Tools used: computer only ✅
```

### Combined Operations → Both Tools
```
User: "Create a tic-tac-toe game and test it in Chrome"
Agent:
  1. Uses bash/edit to create files (file operation)
  2. Uses computer to open browser and test (GUI operation)
Tools used: bash, str_replace_editor, computer ✅
```

## Intelligence, Not Rules

### ❌ Before (Hardcoded - BAD):
```
IF user_mentions("test"):
    ALWAYS do Phase 1 (files)
    ALWAYS do Phase 2 (browser)
    REQUIRED in this order
```

### ✅ Now (Intelligent - GOOD):
```
Analyze user request:
  - What operations are needed?
  - File creation? → Use bash/edit
  - Visual interaction? → Use computer
  - Both? → Use both
  - Choose tools that match the task
```

## Examples of Intelligent Selection

### Example 1: File Creation Only
```
User: "Create a README.md file"

Agent thinking:
- User wants a file created
- No mention of viewing, testing, or GUI
- Task type: File operation
- Tool choice: str_replace_editor

Result: ✅ Creates file with str_replace_editor
        ✅ Does NOT open computer tool unnecessarily
```

### Example 2: Browser Only
```
User: "Click the login button on the current page"

Agent thinking:
- User wants GUI interaction
- No file creation mentioned
- Task type: Visual/GUI operation
- Tool choice: computer

Result: ✅ Uses computer tool to click
        ✅ Does NOT use bash/edit (not needed)
```

### Example 3: Both Tools Needed
```
User: "Write tictactoe code in html css js and run it on chrome and test it"

Agent thinking:
- "Write code" → File creation needed
- "Run it on chrome" → Browser interaction needed
- "Test it" → Visual interaction needed
- Task types: File operation + GUI operation
- Tool choices: bash/edit + computer

Result: ✅ Uses bash/edit for files
        ✅ Uses computer for browser testing
        ✅ Both tools used because both were needed
```

### Example 4: Command Execution Only
```
User: "Run npm install"

Agent thinking:
- User wants command executed
- No file creation, no GUI
- Task type: Command operation
- Tool choice: bash

Result: ✅ Uses bash tool only
        ✅ Efficient, no unnecessary tools
```

## Key Principles

### 1. Match Tool to Task Type
- **File operations** → bash, str_replace_editor
- **GUI operations** → computer
- **Command execution** → bash
- **Visual verification** → computer

### 2. Parse User Intent
Look for keywords:
- "create", "write", "make a file" → bash/edit tools
- "test", "show", "open browser", "click" → computer tool
- "run in chrome", "play the game" → computer tool
- "and" connecting both types → both tools

### 3. Don't Overuse Tools
- If user says "create a file" → don't open browser
- If user says "click button" → don't create files
- Only use what's actually needed for the task

### 4. Complete the Request
- If user asks to "test in browser" → do use computer tool
- If user only asks to "create files" → don't use computer tool
- Match your actions to what was requested

## How the Agent Decides

```
1. Read user request carefully
2. Identify operations needed:
   - File creation? (bash/edit)
   - Command execution? (bash)
   - Browser interaction? (computer)
   - Visual verification? (computer)
3. Select appropriate tool(s)
4. Execute in logical order
5. Don't add unnecessary steps
```

## Configuration Changes

### System Prompt ([orchestrator.py](computer_use_demo/agent_sdk/orchestrator.py:118-143))

**Changed from rigid phases to intelligent selection:**
```
**INTELLIGENT TOOL SELECTION:**

**Understanding user intent:**
- "Create a game" = bash/edit tools only (just create files)
- "Test the game" = computer tool (open browser, click, screenshot)
- "Create and test a game" = bash/edit + computer (both types needed)
- "Run it in Chrome" = computer tool (browser interaction needed)

**Key principle:**
- Match the tool to the task type, not to a fixed sequence
- Listen to what the user asks for - if they want to see it, use computer tool
```

### CLAUDE.md ([.claude/CLAUDE.md](computer_use_demo/.claude/CLAUDE.md:59-83))

**Changed from mandatory phases to intelligent principles:**
```
3. **Don't Hardcode - Be Intelligent:**
   - Not every task needs both tool types
   - Some tasks only need file tools (create files)
   - Some tasks only need computer tool (click a button)
   - Some tasks need both (create files AND test in browser)
   - **Read the user's request carefully and choose appropriately**
```

## Benefits of This Approach

### ✅ Flexibility
- Agent can handle simple file creation tasks
- Agent can handle simple GUI tasks
- Agent can handle complex combined tasks
- No forced sequences

### ✅ Efficiency
- Only uses tools that are actually needed
- No wasted computer tool calls for file-only tasks
- No unnecessary file creation for GUI-only tasks

### ✅ Intelligence
- Agent understands user intent
- Makes decisions based on context
- Not following blind rules

### ✅ Natural Behavior
- Behaves like an intelligent assistant
- Not like a rigid automation script
- Adapts to different request types

## Test Cases

### Test 1: File Only
```
Request: "Create app.py with hello world"
Expected: str_replace_editor only
Why: No GUI interaction requested
```

### Test 2: GUI Only
```
Request: "Take a screenshot of the desktop"
Expected: computer tool only
Why: No file creation requested
```

### Test 3: Both Tools
```
Request: "Create game and show it running in browser"
Expected: bash/edit + computer
Why: File creation + visual display requested
```

### Test 4: Command Only
```
Request: "List all Python files"
Expected: bash tool only
Why: Just a command, no files or GUI
```

## Restart and Test

```bash
python3 -m computer_use_demo.webui
```

The agent will now intelligently choose tools based on your request!

Try different types of requests:
- **File-only**: "Create a Python script"
- **GUI-only**: "Click the Chrome icon"
- **Combined**: "Create a game and test it in browser"

Each will use the appropriate tools! 🎯
