# Excessive Computer Tool Use - FIXED!

## The Problem

Looking at the logs from the latest run:

```
13:41-13:43: Good start
✅ bash: 3 calls (mkdir, cd, start server)
✅ str_replace_editor: 3 calls (created 3 files)

13:45-13:56: Went wrong
⚠️ computer: 38 calls!
- screenshot, left_click, type, key, wait, triple_click
- Opening text editors, clicking files, typing code character by character
```

**The task was:** "Create a new folder on the desktop for the WhatsApp clone React project, then run it in the browser, use it, and **make improvements afterward**."

**What went wrong:** The agent interpreted "make improvements" as:
1. ✅ Create files with str_replace_editor (correct)
2. ✅ Run in browser with computer tool (correct)
3. ❌ Make improvements by CLICKING on a text editor and TYPING code in the GUI (WRONG!)

Instead of step 3, it should have been:
3. ✅ Make improvements with str_replace_editor (edit the code files directly)

## Why This Happened

The agent thought "make improvements" meant:
- Open VS Code or a text editor (computer tool)
- Click on files (computer tool)
- Select code (triple_click with computer tool)
- Type new code character by character (computer tool)
- Save file (Cmd+S with computer tool)

This resulted in **38+ computer tool calls** when it should have been **2-3 str_replace_editor calls**.

## Root Cause

The system prompt said "DO NOT use computer tool to open text editors", but it wasn't explicit enough about what "make improvements", "edit code", "fix bugs", "add features" means.

The agent needed to understand:
- **Editing code = str_replace_editor tool**
- **Testing in browser = computer tool**

## The Fix

Added explicit clarification to the system prompt about code editing:

### 1. Updated Tool Selection Guide ([orchestrator.py](computer_use_demo/agent_sdk/orchestrator.py:83-93))

**Before:**
```
1. **File Creation/Editing** → Use `str_replace_editor` tool:
   - Create files: str_replace_editor with command="create"
   - Edit files: str_replace_editor with command="str_replace"
```

**After:**
```
1. **File Creation/Editing/Improving** → Use `str_replace_editor` tool:
   - Create files: str_replace_editor with command="create"
   - Edit files: str_replace_editor with command="str_replace"
   - Improve code: str_replace_editor with command="str_replace"
   - Fix bugs: str_replace_editor with command="str_replace"
   - Add features: str_replace_editor with command="str_replace"
   - View files: str_replace_editor with command="view"
   - ❌ DO NOT use computer tool to open text editors (VS Code, vim, nano, etc)
   - ❌ DO NOT use computer tool to click on "New File" or type code
   - ❌ DO NOT use computer tool to select/copy/paste code
   - ⚠️ CRITICAL: "Make improvements" = use str_replace_editor, NOT computer tool!
```

### 2. Added Explicit User Intent Mapping ([orchestrator.py](computer_use_demo/agent_sdk/orchestrator.py:141-153))

```
**Understanding user intent - Complete the FULL request:**
- "Create a game" = bash/edit tools only (just create files)
- "Test the game" = computer tool (open browser, click, screenshot)
- "Create and test a game" = bash/edit + computer (DO NOT stop after files!)
- "Run it in Chrome" = create files WITH bash/edit, THEN use computer tool
- "write X and run it" = create WITH bash/edit, THEN use computer to run/show
- **"Make improvements" = str_replace_editor to edit code files (NOT computer tool!)**
- **"Fix bugs" = str_replace_editor to edit code files (NOT computer tool!)**
- **"Add features" = str_replace_editor to edit code files (NOT computer tool!)**
- **"Edit the code" = str_replace_editor to edit code files (NOT computer tool!)**

⚠️ DO NOT stop halfway! If user asks to test/run/show, you must use computer tool after creating files!
⚠️ DO NOT use computer tool to edit code! Use str_replace_editor for ALL code editing!
```

### 3. Added CORRECT vs WRONG Example ([orchestrator.py](computer_use_demo/agent_sdk/orchestrator.py:205-229))

```
**Example - Editing/Improving Code (CORRECT vs WRONG):**

User says: "make improvements to the code"

✅ CORRECT:
Step 1: str_replace_editor → view the file to understand current code
Step 2: str_replace_editor → str_replace to fix bugs or add features
Step 3: bash → restart server if needed
Step 4: computer → refresh browser to test changes
Total: 2 edit calls + 1 bash + 1 computer = EFFICIENT!

❌ WRONG - DO NOT DO THIS:
Step 1: computer → screenshot to see desktop
Step 2: computer → click on VS Code or text editor icon
Step 3: computer → click File > Open
Step 4: computer → click on the file
Step 5: computer → triple_click to select line
Step 6: computer → type new code character by character
Step 7: computer → press Cmd+S to save
Step 8: computer → click terminal
Step 9: computer → type restart command
... 20+ computer tool calls - VERY SLOW and WASTEFUL!
```

### 4. Added Key Reminder ([orchestrator.py](computer_use_demo/agent_sdk/orchestrator.py:229-231))

```
⚠️ REMEMBER: Computer tool is for TESTING the application in the browser, NOT for editing code files!

**Key principle: You are NOT a human using a GUI. You are Claude Code with direct access to file and command tools!**
```

## Expected Behavior After Fix

### For "Create WhatsApp clone, run it, make improvements":

**Phase 1: Create (bash/edit tools)**
```
bash → mkdir whatsapp-clone
str_replace_editor → create package.json
str_replace_editor → create index.html
str_replace_editor → create App.jsx
str_replace_editor → create styles.css
```

**Phase 2: Run (bash + computer tool)**
```
bash → npm install && npm run dev &
computer → open Chrome
computer → navigate to localhost:5173
computer → test the interface
computer → screenshot
```

**Phase 3: Make Improvements (str_replace_editor + computer tool)**
```
str_replace_editor → view App.jsx to see current code
str_replace_editor → str_replace to add new feature
str_replace_editor → str_replace to fix styling
bash → restart dev server if needed
computer → refresh browser to see changes
computer → test new features
computer → screenshot showing improvements
```

**Total tool usage:**
- bash: ~5 calls
- str_replace_editor: ~7 calls (3 create + 4 edit)
- computer: ~5 calls (browser testing)
- **Total: ~17 calls (efficient and fast!)**

**NOT 60+ calls with most being computer tool!**

## Key Principles

### 1. You are Claude Code, not a human
- You have DIRECT access to files via str_replace_editor
- You don't need to click on text editors
- You don't need to type code character by character
- You can edit files instantly with str_replace commands

### 2. Computer tool is for visual tasks ONLY
- Opening browsers
- Clicking UI elements in web apps
- Testing interactive features
- Taking screenshots for verification
- **NOT for editing code files!**

### 3. Code editing keywords trigger str_replace_editor
When user says:
- "edit"
- "improve"
- "fix"
- "add feature"
- "modify"
- "update"
- "change"

→ Use **str_replace_editor**, NOT computer tool!

### 4. Browser testing keywords trigger computer tool
When user says:
- "test in browser"
- "run it"
- "show it"
- "open in chrome"
- "click the button"
- "play the game"

→ Use **computer tool** for browser interaction!

## Files Modified

1. **`computer_use_demo/agent_sdk/orchestrator.py`**
   - Lines 83-93: Expanded tool #1 to include Improving/Fixing/Adding features
   - Lines 147-153: Added explicit intent mapping for editing keywords
   - Lines 205-231: Added CORRECT vs WRONG example for code editing
   - Line 231: Added key principle reminder

## Restart Required

**Important:** Restart the webui to load the updated system prompt:

```bash
# Stop current webui (Ctrl+C)
python3 -m computer_use_demo.webui
```

## Testing

Try the same task again:
```
Create a new folder on the desktop for the WhatsApp clone React project, then run it in the browser, use it, and make improvements afterward.
```

**Expected tool usage:**
```
bash: 4-6 calls
str_replace_editor: 6-10 calls (3 create + 3-7 edit for improvements)
computer: 4-6 calls (browser testing only)

Total: ~15-20 calls (NOT 60+!)
```

**What you should NOT see:**
- computer tool clicking on text editors
- computer tool typing code
- computer tool selecting/copying/pasting
- 30+ computer tool calls

## Why This Matters

### Performance Impact:
- **38 computer calls** = slow, expensive, uses lots of context
- **5 computer calls** = fast, efficient, focused on testing

### Cost Impact:
- Each computer tool call includes a screenshot
- Screenshots take up significant context space
- More calls = higher API costs

### User Experience:
- Watching agent click around GUI = slow and frustrating
- Direct file edits = instant and satisfying
- Real-time streaming now shows all this - so efficiency matters!

## Status: ✅ System Prompt Updated

The agent now understands:
1. **Code editing = str_replace_editor tool (direct access)**
2. **Browser testing = computer tool (visual verification)**
3. **"Make improvements" = edit files with str_replace_editor, NOT click around GUI**

**Restart the webui and test it!** 🚀
