# Computer Tool Not Being Used - Final Fix

## The Problem

Even after all the changes, logs still show:
```
bash: 3 calls ✅
str_replace_editor: 4 calls ✅
computer: 0 calls ❌  ← STILL NOT BEING USED!
```

The agent says "I'll open it in a browser" but then just creates files and stops.

## Root Cause

The system prompt had conflicting messages:

**Conflicting message 1:**
```
"⚠️ IMPORTANT: You work like Claude Code - prefer DIRECT tools over GUI automation!"
```
This was interpreted as "avoid GUI tools whenever possible"

**Conflicting message 2:**
```
"Use computer tool for visual tasks - USE THIS!"
```
This was being ignored because of the stronger "prefer DIRECT tools" message

**Result:** Agent avoids computer tool entirely!

## The Fix Applied

### 1. Changed Opening Line ([orchestrator.py](computer_use_demo/agent_sdk/orchestrator.py:78-81))

**Before:**
```
⚠️ IMPORTANT: You work like Claude Code - prefer DIRECT tools over GUI automation!
```

**After:**
```
⚠️ IMPORTANT: You have access to BOTH direct tools AND GUI tools - use the right one for each task!
```

**Why:** Removes the bias against GUI tools.

### 2. Made Computer Tool Usage Mandatory ([orchestrator.py](computer_use_demo/agent_sdk/orchestrator.py:97-106))

**Changed:**
```
- ✅ Opening browsers (Chrome, Firefox) - USE THIS!
```

**To:**
```
- ✅ Opening browsers (Chrome, Firefox) - MUST USE computer tool!
- ✅ Clicking links in browsers - MUST USE computer tool!
- ✅ Testing web applications - MUST USE computer tool!

⚠️ CRITICAL: If user says "test in browser", "open chrome", "show it running", "play the game":
   YOU MUST use the computer tool! Don't just create files and stop!
```

**Why:** Makes it explicit that computer tool is REQUIRED for these tasks.

### 3. Added "Complete the FULL request" Warning ([orchestrator.py](computer_use_demo/agent_sdk/orchestrator.py:136-143))

**Added:**
```
**Understanding user intent - Complete the FULL request:**
- "Create and test a game" = bash/edit + computer (DO NOT stop after files!)
- "Run it in Chrome" = create files WITH bash/edit, THEN use computer tool
- "write X and run it" = create WITH bash/edit, THEN use computer to run/show

⚠️ DO NOT stop halfway! If user asks to test/run/show, you must use computer tool after creating files!
```

**Why:** Prevents the agent from stopping after Phase 1.

## Key Changes Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Tone** | "Prefer direct tools" | "Use BOTH tools appropriately" |
| **Computer tool** | "Use when necessary" | "MUST USE for GUI tasks" |
| **Completeness** | (not mentioned) | "DO NOT stop halfway!" |
| **Clarity** | Ambiguous | Explicit keywords trigger computer tool |

## How It Should Work Now

### For "write tictactoe and run it on chrome and test it":

**Agent thinking:**
```
1. "write tictactoe" → Use bash/edit to create files
2. "run it on chrome" → MUST use computer tool to open browser
3. "test it" → MUST use computer tool to interact with game
4. Keywords detected: "run", "chrome", "test" → Computer tool REQUIRED
5. Must complete FULL request → Don't stop after creating files
```

**Expected tool usage:**
```
bash → mkdir
str_replace_editor → create index.html
str_replace_editor → create style.css
str_replace_editor → create game.js
bash → python3 -m http.server
computer → open Chrome    ← MUST happen!
computer → type URL       ← MUST happen!
computer → click game     ← MUST happen!
computer → screenshot     ← MUST happen!
```

## Keyword Triggers

These words REQUIRE computer tool usage:
- "test" (in context of UI/browser)
- "run in chrome/firefox/browser"
- "open in browser"
- "show it"
- "play it"
- "demonstrate"
- "click"
- "interact"

When these appear, agent MUST use computer tool!

## Restart Required

**Important:** You must restart the webui for changes to take effect:

```bash
# Stop current webui (Ctrl+C)
python3 -m computer_use_demo.webui
```

The system prompt is loaded once when the orchestrator initializes, so changes require a restart.

## How to Verify

After restarting, try:
```
write tictactoe code in html css js and run it on chrome and test it
```

Watch the console output:
```
✅ bash called (count: 1)
✅ str_replace_editor called (count: 1)
✅ str_replace_editor called (count: 2)
✅ str_replace_editor called (count: 3)
✅ bash called (count: 2)
⚠️ Computer tool used: left_click (count: 1)   ← Should appear!
⚠️ Computer tool used: type (count: 2)         ← Should appear!
⚠️ Computer tool used: screenshot (count: 3)   ← Should appear!
```

If you still see 0 computer tool calls, the system prompt changes might not be loading correctly.

## Files Modified

1. **`computer_use_demo/agent_sdk/orchestrator.py`**
   - Line 79: Changed "prefer DIRECT tools" to "use BOTH tools appropriately"
   - Lines 97-106: Changed "USE THIS!" to "MUST USE computer tool!"
   - Lines 136-143: Added "Complete the FULL request" warning with "DO NOT stop halfway!"

## Why This Is Critical

**Without computer tool:**
- Files created ✅
- Server running ✅
- **But user sees nothing** ❌
- **No browser opens** ❌
- **No testing happens** ❌
- **Task incomplete** ❌

**With computer tool:**
- Files created ✅
- Server running ✅
- **Browser automatically opens** ✅
- **Game loads visually** ✅
- **Testing happens** ✅
- **User sees it working** ✅
- **Task complete!** ✅

---

## If It STILL Doesn't Work

If after restarting you STILL see 0 computer tool calls:

1. **Check the webui actually restarted:**
   ```bash
   ps aux | grep "computer_use_demo.webui"
   ```

2. **Check if CLAUDE.md is being loaded:**
   ```bash
   # Add debug print to session.py load_conventions()
   # It should print the conventions content
   ```

3. **Check if there's an error in the logs:**
   ```bash
   # Look for Python errors in the terminal where webui is running
   ```

4. **Try a more explicit request:**
   ```
   Create tic-tac-toe files, start server, open Chrome, navigate to localhost:8000, click cells to play, take screenshot
   ```

   This leaves no room for ambiguity.

5. **Check the tool logger output:**
   ```bash
   cat ~/.claude/projects/webui-*/tool_log.jsonl | jq -r '.tool' | sort | uniq -c
   ```

If computer tool still shows 0, there may be a deeper issue with the tool configuration or the agent is hitting a different code path.

---

## Status: ✅ Changes Applied - Restart Required

The system prompt now explicitly requires computer tool usage for browser tasks.

**Restart the webui and test again!** 🚀
